"""
Created on 16th October, 2017 (Updated from 26th April 2019 for Extended One Way and Flush End Plate connection).

@author: Danish Ansari


Module (Moment connection): 1. Beam to beam extended end plate splice connection
                            2. Beam to beam extended one way end plate splice connection
                            3. Beam to beam flushed end plate splice connection

Reference:
            1) IS 800: 2007 General construction in steel - Code of practice (Third revision)
            2) Design of Steel structures by Dr. N Subramanian (chapter 5 and 6)
            3) Fundamentals of Structural steel design by M.L Gambhir
            4) AISC Design guide 16 and 4


"""

from model import *
from utilities.is800_2007 import IS800_2007
from utilities.other_standards import IS1363_part_1_2002, IS1363_part_3_2002, IS1367_Part3_2002
from utilities.common_calculation import *
import math
import logging
import numpy
flag = 1
logger = None


def module_setup():
    global logger
    logger = logging.getLogger("osdag.ccEndPlateSpliceCalc")


module_setup()

#######################################################################
# Function for fetching column parameters_sqr from the database

def fetchColumnPara(self):
    column_sec = self.ui.combo_columnSec.currentText()
    dictcolumndata = get_columndata(column_sec)
    return dictcolumndata

#######################################################################
#######################################################################
# Start of Main Program

def ccEndPlateSplice(uiObj):
    global logger
    global design_status
    design_status = True

    column_sec = uiObj['Member']['ColumnSection']
    column_fu = float(uiObj['Member']['fu (MPa)'])
    column_fy = float(uiObj['Member']['fy (MPa)'])
    weld_fu = float(uiObj['weld']['fu_overwrite'])
    weld_fu_govern = min(column_fu, weld_fu)  # Mpa  (weld_fu_govern is the governing value of weld strength)

    factored_moment = float(uiObj['Load']['Moment (kNm)'])
    factored_shear_load = float(uiObj['Load']['ShearForce (kN)'])
    factored_axial_load = uiObj['Load']['AxialForce (kN)']
    if factored_axial_load == '':
        factored_axial_load = 0
    else:
        factored_axial_load = float(factored_axial_load)

    bolt_dia = int(uiObj['Bolt']['Diameter (mm)'])
    bolt_type = uiObj["Bolt"]["Type"]
    bolt_grade = float(uiObj['Bolt']['Grade'])
    bolt_fu = uiObj["bolt"]["bolt_fu"]
    bolt_fy = (bolt_grade - int(bolt_grade)) * bolt_fu

    mu_f = float(uiObj["bolt"]["slip_factor"])
    gamma_mw = float(uiObj["weld"]["safety_factor"])
    dp_bolt_hole_type = uiObj["bolt"]["bolt_hole_type"]
    if dp_bolt_hole_type == "Over-sized":
        bolt_hole_type = 'over_size'
    else:   # "Standard"
        bolt_hole_type = 'standard'

    dia_hole = bolt_dia + int(uiObj["bolt"]["bolt_hole_clrnce"])
    end_plate_thickness = float(uiObj['Plate']['Thickness (mm)'])

    # TODO implement after excomm review for different grades of plate
    end_plate_fu = float(uiObj['Member']['fu (MPa)'])
    end_plate_fy = float(uiObj['Member']['fy (MPa)'])

    weld_type = str(uiObj["Weld"]["Type"])  # This is - Fillet weld or Groove weld

    if uiObj["Weld"]["Type"] == "Fillet Weld":
        weld_thickness_flange = float(uiObj['Weld']['Flange (mm)'])
        weld_thickness_web = float(uiObj['Weld']['Web (mm)'])
    else:
        weld_thickness_flange = 0
        weld_thickness_web = 0

    if uiObj["detailing"]["typeof_edge"] == "a - Sheared or hand flame cut":
        edge_type = 'hand_flame_cut'
    else:   # "b - Rolled, machine-flame cut, sawn and planed"
        edge_type = 'machine_flame_cut'

    corrosive_influences = False
    if uiObj['detailing']['is_env_corrosive'] == "Yes":
        corrosive_influences = True

    [bolt_shank_area, bolt_net_area] = IS1367_Part3_2002.bolt_area(bolt_dia)


    old_column_section = get_oldcolumncombolist()

    if column_sec in old_column_section:
        logger.warning(": You are using a section (in red colour) that is not available in the latest vey_sqrion of IS 808")

    if column_fu < 410 or column_fy < 230:
        logger.warning(" : You are using a section of grade that is not available in latest vey_sqrion of IS 2062")

    #######################################################################
    # Read input values from Column database

    dictcolumndata = get_columndata(column_sec)
    global column_tw
    column_tw = float(dictcolumndata["tw"])
    global column_tf
    column_tf = float(dictcolumndata["T"])
    column_d = float(dictcolumndata["D"])
    column_B = float(dictcolumndata["B"])
    column_R1 = float(dictcolumndata["R1"])
    column_Zz = float(dictcolumndata["Zz"])

    #######################################################################
    # Validation of minimum input moment (Cl. 10.7- 6 and Cl. 8.2.1, IS 800:2007)

    M_d = (1.2 * column_Zz * 1000 * column_fy) / 1.10
    moment_minimum = 0.5 * (M_d / 1000000)

    if float(factored_moment) < float(moment_minimum):
        design_status = False
        logger.warning(": The input factored moment (%2.2f kN-m) is less that the minimum design action on the connection (Cl. 10.7-6, IS 800:2007)" % factored_moment)
        logger.info(": The connection is designed for %2.2f kN-m" % float(moment_minimum))

    factored_moment = round(moment_minimum, 3)

    #######################################################################
    # Calculation of Bolt strength in MPa
    bolt_fu = uiObj["bolt"]["bolt_fu"]
    bolt_fy = (bolt_grade - int(bolt_grade)) * bolt_fu

    #######################################################################
    # Calculation of Spacing

    # min_pitch & max_pitch = Minimum and Maximum pitch distance (mm) [Cl. 10.2.2, IS 800:2007]
    min_pitch = math.floor(column_d - (2 * column_tf) - (2 * min_end_distance)) / (no_bolts_web-1)  # has been changed for detailing purpose
    max_pitch = IS800_2007.cl_10_2_3_1_max_spacing(end_plate_thickness)

    # min_gauge & max_gauge = Minimum and Maximum gauge distance (mm) [Cl. 10.2.3.1, IS 800:2007]
    gauge_dist_min = min_pitch
    gauge_dist_max = max_pitch

    # Minimum and maximum end distances (mm) [Cl. 10.2.4.2 & Cl. 10.2.4.3, IS 800:2007]
    end_dist_min = (column_d - (2 * column_tf) - (2 * min_pitch)) / 2
    end_dist_max = IS800_2007.cl_10_2_4_3_max_edge_dist(plate_thicknesses=end_plate_thickness, f_y=end_plate_fy, corrosive_influences=corrosive_influences)
    
    # Minimum and maximum edge distances (mm) [Cl. 10.2.4.2 & Cl. 10.2.4.3, IS 800:2007]
    edge_dist_mini = end_dist_mini
    edge_dist_max = end_dist_max

    #######################################################################
    # End plate detailing

    # end plate height
    if uiObj["Member"]["Connectivity"] == "Extended both ways":
        end_plate_height = column_d + 30
    elif uiObj["Member"]["Connectivity"] == "Flush":
        end_plate_height = column_d + 4 * end_dist_mini  # TODO 10 mm is the cover provided beyond flange on either sides

    # end plate width
    end_plate_width = column_B + 25

    # end plate thickness
    if float(min_pitch) >= float(2 * end_dist_min):
        b_eff = (2 * end_dist_min)
    else:
        b_eff = min_pitch

    t_b1 = (factored_axial_load / no_of_bolts) + (factored_moment * y_1 / y_sqr)
    t_b2,t_b3 = (factored_axial_load / no_of_bolts) + (factored_moment * y_2 / y_sqr)
    y_1 = column_tf/2 + end_dist_min
    y_2 = y_1 + min_pitch

    if uiObj["Member"]["Connectivity"] == "Flush":
        m_ep = max(0.5 * t_b1 * end_dist_min, t_b2 * end_dist_min)
    elif uiObj["Member"]["Connectivity"] == "Extended both ways":
        m_ep = max(0.5 * t_b1 * end_dist_min, t_b3 * end_dist_min)
    
    gamma_m0 = 1.10
    m_dp = b_eff * end_plate_thickness**2 * column_fy / (4 * gamma_m0)
    
    if m_ep > m_dp:
        design_status = False
        logger.warning(": The moment acting on plate is more than the moment design capacity of the plate.)
        logger.info(": Increase the plate thickness.)

    ####################################################################################
    # Calculate bolt capabilities

    if bolt_type == "Friction Grip Bolt":
        bolt_slip_capacity = IS800_2007.cl_10_4_3_bolt_slip_resistance(
            f_ub=bolt_fu, A_nb=bolt_net_area, n_e=1, mu_f=mu_f, bolt_hole_type=bolt_hole_type)
        bolt_tension_capacity = IS800_2007.cl_10_4_5_friction_bolt_tension_resistance(
            f_ub=bolt_fu, f_yb=bolt_fy, A_sb=bolt_shank_area, A_n=bolt_net_area)
        bearing_capacity = 0.0
        bolt_shear_capacity = 0.0
        bolt_capacity = bolt_slip_capacity

    else:
        bolt_shear_capacity = IS800_2007.cl_10_3_3_bolt_shear_capacity(
            f_u=bolt_fu, A_nb=bolt_net_area, A_sb=bolt_shank_area, n_n=1, n_s=0)
        bearing_capacity = IS800_2007.cl_10_3_4_bolt_bearing_capacity(
            f_u=min(column_fu, end_plate_fu), f_ub=bolt_fu, t=(2 * end_plate_thickness), d=bolt_dia, e=end_dist_mini,
            p=min_pitch, bolt_hole_type=bolt_hole_type)
        bolt_slip_capacity = 0.0
        bolt_capacity = min(bolt_shear_capacity, bearing_capacity)
        bolt_tension_capacity = IS800_2007.cl_10_3_5_bearing_bolt_tension_resistance(
            f_ub=bolt_fu, f_yb=bolt_fy, A_sb=bolt_shank_area, A_n=bolt_net_area)
    
    #######################################################################
    # Calculation for number of bolts
    #######################################################################

    no_bolts_web = ((column_d - (2 * column_tf) - (2 * min_edge_distance))/min_pitch) +1
    no_bolts_web = math.floor(no_bolts_web)

    no_bolts_flange = ((column_B - (column_tw/2) - (2 * min_edge_distance)) / min_pitch) + 1
    no_bolts_flange = math.floor(no_bolts_flange)

    no_of_bolts = no_bolts_web + no_bolts_flange

    if ['Member']['Connectivity'] == "Flush":
        y_max = column_d - column_tf - (column_tf/2) - end_dist
    elif ["Member"]["Connectivity"] == "Extended both ways":
        y_max = column_d - (column_tf/2) + end_dist

    if ['Member']['Connectivity'] == "Flush":
        y_sqr = 0
        for i in no_bolts_web:
            y_sqr = y_sqr + (end_dist + (column_tf / 2) + ((i-1) * pitch)) ** 2
            return y_sqr
    elif ["Member"]["Connectivity"] == "Extended both ways":
        y_sqr = 0
        for i in no_bolts_web:
            y_sqr = y_sqr + (end_dist + (column_tf / 2) + ((i-1) * pitch)) ** 2
            y_sqr = y_sqr + 2 * end_dist + column_tf
            return y_sqr

    ###########################################################################
        # Bolt Checks
    ###########################################################################
    t_b = (factored_axial_load / no_of_bolts) + (factored_moment * y_max / y_sqr)

    if t_b > bolt_tension_capacity:
        design_status = False
        logger.error(": The tension capacity of the connection is less than the bolt tension capacity.")
        logger.warning(": Tension capacity of connection should be more than or equal to bolt tension capacity i.e %s KN." % bolt_tension_capacity)
        logger.info(": Increase diameter of bolt or class of the bolt.")

    v_sb = factored_shear_load / n_w
    if uiObj["Member"]["Connectivity"] == "Flush":
        n_w = no_bolts_web
    if uiObj["Member"]["Connectivity"] == "Extended both ways":
        n_w = no_bolts_web

    if v_sb > bolt_capacity:combined_capcitycombined_capcity
        design_status = False
        logger.error(": The Shear capacity of the connection is less than the bolt shear capacity.")
        logger.warning(": Shear capacity of connection should be more than or equal to bolt capacity i.e %s KN." % bolt_capacity)
        logger.info(": Increase diameter of bolt or class of the bolt.")

    combined_capacity = (v_sb/bolt_capacity)**2 + (t_b/bolt_tension_capacity)**2
    if float(combined_capacity) > float(1)
    design_status = False
        logger.error(": Load due to combined shear and tension on selected bolt exceeds the limiting value")
        logger.warning(": Higher section is required for the safe design.")
        logger.info(": Re-design the connection using section of higher dimensions.")

    #########################################################################
     # Stiffener
    #########################################################################
    shear_on_stiff = t_b1
    moment_on_stiff = t_b1 * end_dist_min

    
    # #######################################################################
    # Calculating pitch, gauge, end and edge distances for different cases

    # Case 1: When the height and the width of end plate is not specified by user
    if end_plate_height == 0 and end_plate_width == 0:

        if uiObj["Member"]["Connectivity"] == "Flush":

            if number_of_bolts == 4:
                pitch_distance = beam_d - ((2 * beam_tf) + (2 * p_fi))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 6:
                pitch_distance_1_2 = pitch_dist_min  # Distance between the 1st and 2nd row of bolt from top
                pitch_distance_2_3 = beam_d - ((2 * beam_tf) + (2 * p_fi) + pitch_distance_1_2)  # Distance between 2nd and 3rd row of bolt from top

                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_2_3 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_2_3 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        elif uiObj["Member"]["Connectivity"] == "Extended one way":

            if number_of_bolts == 6:
                pitch_distance = beam_d - ((2 * beam_tf) + (2 * p_fi))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 8:
                pitch_distance_2_3 = pitch_dist_min  # Distance between 2nd and 3rd row of bolt from top
                pitch_distance_3_4 = beam_d - ((2 * beam_tf) + (2 * p_fi) + pitch_distance_2_3)  # Distance between the 3rd and 4th row of bolt from top

                if (pitch_distance_2_3 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_2_3 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 10:
                pitch_distance_1_2 = pitch_distance_3_4 = pitch_dist_min  # Distance between 1st, 2nd and 3rd, 4th row of bolt from top
                pitch_distance_4_5 = beam_d - ((2 * beam_tf) + (2 * p_fi) + pitch_distance_3_4)  # Distance between the 4th and 5th row of bolt from top
                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min) or (pitch_distance_4_5 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max) or (pitch_distance_4_5 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")
        else:
            if number_of_bolts == 8:
                pitch_distance = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 12:
                pitch_distance_2_3 = pitch_distance_4_5 = pitch_dist_min  # Distance between 2nd, 3rd and 4th, 5th row of bolt from top
                pitch_distance_3_4 = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v) + pitch_distance_2_3 + pitch_distance_4_5)

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 16:
                pitch_distance_2_3 = pitch_distance_3_4 = pitch_distance_5_6 = pitch_distance_6_7 = pitch_dist_min
                pitch_distance_4_5 = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v) + pitch_distance_2_3 + pitch_distance_3_4 + pitch_distance_5_6 + pitch_distance_6_7)

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 20:
                pitch_distance_1_2 = pitch_distance_9_10 = pitch_dist_min
                pitch_distance_3_4 = pitch_distance_4_5 = pitch_distance_6_7 = pitch_distance_7_8 = pitch_dist_min
                pitch_distance_5_6 = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v) + (4 * pitch_dist_min))

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        if uiObj["Member"]["Connectivity"] == "Flush":
            end_plate_height_provided = beam_d + (2 * weld_thickness_flange) + (2 * 10)

        elif uiObj["Member"]["Connectivity"] == "Extended one way":
            if number_of_bolts == 6 or number_of_bolts == 8:
                end_plate_height_provided = beam_d + p_fo + end_dist_mini + weld_thickness_flange + 10
            elif number_of_bolts == 10:
                end_plate_height_provided = beam_d + p_fo + pitch_distance_1_2 + end_dist_mini + weld_thickness_flange + 10

        else:
            if number_of_bolts == 8 or number_of_bolts == 12 or number_of_bolts == 16:
                end_plate_height_provided = beam_d + ((2 * weld_thickness_flange) + (2 * l_v) + (2 * end_dist_mini))
            else:
                end_plate_height_provided = beam_d + ((2 * weld_thickness_flange) + (2 * l_v) + (2 * pitch_dist_min) + (2 * end_dist_mini))

        end_plate_width_provided = max(beam_B + 25, g_1 + (2 * edge_dist_mini))
        edge_dist_mini = (end_plate_width_provided - g_1)/2

        if uiObj["detailing"]["typeof_edge"] == "a - Sheared or hand flame cut":
            end_dist_mini = int(math.ceil(1.7 * dia_hole))
        else:
            end_dist_mini = min_edge_distance = int(math.ceil(1.5 * dia_hole))

        # cross_centre_gauge = end_plate_width_provided - (2 * edge_dist_mini)
        cross_centre_gauge = max(float(90), g_1)

    # Case 2: When the height of end plate is specified but the width is not specified by the user

    elif end_plate_height != 0 and end_plate_width == 0:
        height_available = end_plate_height  # available height of end plate

        if uiObj["Member"]["Connectivity"] == "Flush":
            if number_of_bolts == 4:
                pitch_distance = height_available - ((2 * 10) + (2 * weld_thickness_flange) + (2 * beam_tf) + (2 * p_fi))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 6:
                pitch_distance_1_2 = pitch_dist_min  # Distance between the 1st and 2nd row of bolt from top
                pitch_distance_2_3 = height_available - ((2 * 10) + (2 * weld_thickness_flange) + (2 * beam_tf) + (2 * p_fi) + pitch_distance_1_2)  # Distance between 2nd and 3rd row of bolt from top

                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_2_3 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_2_3 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        elif uiObj["Member"]["Connectivity"] == "Extended one way":

            if number_of_bolts == 6:
                pitch_distance = height_available - (min_end_distance + p_fo + (2 * beam_tf) + (2 * p_fi) + 10)

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 8:
                pitch_distance_2_3 = pitch_dist_min  # Distance between 2nd and 3rd row of bolt from top
                pitch_distance_3_4 = height_available - (min_end_distance + p_fo + weld_thickness_flange + (2 * beam_tf) + (2 * p_fi) + 10 + pitch_distance_2_3)  # Distance between the 3rd and 4th row of bolt from top

                if (pitch_distance_2_3 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_2_3 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 10:
                pitch_distance_1_2 = pitch_distance_3_4 = pitch_dist_min  # Distance between 1st, 2nd and 3rd, 4th row of bolt from top
                pitch_distance_4_5 = height_available - (min_end_distance + pitch_distance_1_2 + p_fo + weld_thickness_flange + (2 * beam_tf) + 10 + (2 * p_fi) + pitch_distance_3_4)  # Distance between the 4th and 5th row of bolt from top

                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min) or (pitch_distance_4_5 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max) or (pitch_distance_4_5 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")
        else:
            if number_of_bolts == 8:
                pitch_distance = height_available - ((2 * end_dist_mini) + (2 * l_v) + (4 * weld_thickness_flange) + (2 * beam_tf) + (2 * l_v))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 12:
                pitch_distance_2_3 = pitch_distance_4_5 = pitch_dist_min
                pitch_distance_3_4 = height_available - ((2 * end_dist_mini) + (2 * l_v) + (4 * weld_thickness_flange) + (2 * beam_tf) + (2 * l_v) + pitch_distance_2_3 + pitch_distance_4_5)

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 16:
                pitch_distance_2_3 = pitch_distance_3_4 = pitch_distance_5_6 = pitch_distance_6_7 = pitch_dist_min
                pitch_distance_4_5 = height_available - ((2 * end_dist_mini) + (4 * l_v) + (4 * weld_thickness_flange) + (2 * beam_tf) + (4 * pitch_dist_min))

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 20:
                pitch_distance_1_2 = pitch_distance_9_10 = pitch_dist_min
                pitch_distance_3_4 = pitch_distance_4_5 = pitch_distance_6_7 = pitch_distance_7_8 = pitch_dist_min
                pitch_distance_5_6 = height_available - ((2 * end_dist_mini) + (4 * l_v) + (2 * beam_tf) + (4 * weld_thickness_flange) + (6 * pitch_dist_min))

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        end_plate_height_provided = height_available
        end_plate_width_provided = max(beam_B + 25, g_1 + (2 * edge_dist_mini))
        edge_dist_mini = (end_plate_width_provided - g_1) / 2
        if uiObj["detailing"]["typeof_edge"] == "a - Sheared or hand flame cut":
            end_dist_mini = int(math.ceil(1.7 * dia_hole))
        else:
            end_dist_mini = min_edge_distance = int(float(1.5 * dia_hole))
        # cross_centre_gauge = end_plate_width_provided - (2 * edge_dist_mini)

        # cross_centre_gauge = max(float(90), float(((2 * min_edge_distance) + beam_tw)))?
        cross_centre_gauge = max(float(90), g_1)

    # Case 3: When the height of end plate is not specified but the width is specified by the user
    elif end_plate_height == 0 and end_plate_width != 0:

        if uiObj["Member"]["Connectivity"] == "Flush":
            if number_of_bolts == 4:
                pitch_distance = beam_d - ((2 * beam_tf) + (2 * p_fi))
                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 6:
                pitch_distance_1_2 = pitch_dist_min  # Distance between the 1st and 2nd row of bolt from top
                pitch_distance_2_3 = beam_d - ((2 * beam_tf) + (2 * p_fi) + pitch_distance_1_2)  # Distance between 2nd and 3rd row of bolt from top
                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_2_3 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_2_3 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        elif uiObj["Member"]["Connectivity"] == "Extended one way":
            if number_of_bolts == 6:
                pitch_distance = beam_d - ((2 * beam_tf) + (2 * p_fi))
                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 8:
                pitch_distance_2_3 = pitch_dist_min  # Distance between 2nd and 3rd row of bolt from top
                pitch_distance_3_4 = beam_d - ((2 * beam_tf) + (2 * p_fi) + pitch_distance_2_3)  # Distance between the 3rd and 4th row of bolt from top
                if (pitch_distance_2_3 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_2_3 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 10:
                pitch_distance_1_2 = pitch_distance_3_4 = pitch_dist_min  # Distance between 1st, 2nd and 3rd, 4th row of bolt from top
                pitch_distance_4_5 = beam_d - ((2 * beam_tf) + (2 * p_fi) + pitch_distance_3_4)  # Distance between the 4th and 5th row of bolt from top
                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min) or (pitch_distance_4_5 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max) or (pitch_distance_4_5 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")
        else:
            if number_of_bolts == 8:
                pitch_distance = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 12:
                pitch_distance_2_3 = pitch_distance_4_5 = pitch_dist_min  # Distance between 2nd, 3rd and 4th, 5th row of bolt from top
                pitch_distance_3_4 = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v) + pitch_distance_2_3 + pitch_distance_4_5)

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 16:
                pitch_distance_2_3 = pitch_distance_3_4 = pitch_distance_5_6 = pitch_distance_6_7 = pitch_dist_min
                pitch_distance_4_5 = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v) + pitch_distance_2_3 + pitch_distance_3_4 + pitch_distance_5_6 + pitch_distance_6_7)

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 20:
                pitch_distance_1_2 = pitch_distance_9_10 = pitch_dist_min
                pitch_distance_3_4 = pitch_distance_4_5 = pitch_distance_6_7 = pitch_distance_7_8 = pitch_dist_min
                pitch_distance_5_6 = beam_d - ((2 * beam_tf) + (2 * weld_thickness_flange) + (2 * l_v) + (4 * pitch_dist_min))

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        if uiObj["Member"]["Connectivity"] == "Flush":
            end_plate_height_provided = beam_d + (2 * weld_thickness_flange) + (2 * 10)

        elif uiObj["Member"]["Connectivity"] == "Extended one way":
            if number_of_bolts == 6 or number_of_bolts == 8:
                end_plate_height_provided = beam_d + p_fo + end_dist_mini + weld_thickness_flange + 10
            elif number_of_bolts == 10:
                end_plate_height_provided = beam_d + p_fo + pitch_distance_1_2 + end_dist_mini + weld_thickness_flange + 10
        else:
            if number_of_bolts == 8 or number_of_bolts == 12 or number_of_bolts == 16:
                end_plate_height_provided = beam_d + ((2 * weld_thickness_flange) + (2 * l_v) + (2 * end_dist_mini))
            else:
                end_plate_height_provided = beam_d + ((2 * weld_thickness_flange) + (2 * l_v) + (2 * pitch_dist_min) + (2 * end_dist_mini))

        end_plate_width_provided = end_plate_width
        # end_plate_width_provided = max(beam_B + 25, g_1 + (2 * edge_dist_mini))
        edge_dist_mini = (end_plate_width_provided - g_1) / 2
        if uiObj["detailing"]["typeof_edge"] == "a - Sheared or hand flame cut":
            end_dist_mini = int(math.ceil(1.7 * dia_hole))
        else:
            end_dist_mini = min_edge_distance = int(float(1.5 * dia_hole))

        # cross_centre_gauge = end_plate_width_provided - (2 * edge_dist_mini)
        # cross_centre_gauge = max(float(90), float(((2 * min_edge_distance) + beam_tw)))
        cross_centre_gauge = max(float(90), g_1)

    # Case 4: When the height and the width of End Plate is specified by the user
    elif end_plate_height != 0 and end_plate_width != 0:

        height_available = end_plate_height

        if uiObj["Member"]["Connectivity"] == "Flush":
            if number_of_bolts == 4:
                pitch_distance = height_available - ((2 * 10) + (2 * weld_thickness_flange) + (2 * beam_tf) + (2 * p_fi))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 6:
                pitch_distance_1_2 = pitch_dist_min  # Distance between the 1st and 2nd row of bolt from top
                pitch_distance_2_3 = height_available - (
                            (2 * 10) + (2 * weld_thickness_flange) + (2 * beam_tf) + (2 * p_fi) + pitch_distance_1_2)  # Distance between 2nd and 3rd row of bolt from top

                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_2_3 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_2_3 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        elif uiObj["Member"]["Connectivity"] == "Extended one way":

            if number_of_bolts == 6:
                pitch_distance = height_available - (min_end_distance + p_fo + (2 * beam_tf) + (2 * p_fi) + 10)

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 8:
                pitch_distance_2_3 = pitch_dist_min  # Distance between 2nd and 3rd row of bolt from top
                pitch_distance_3_4 = height_available - (min_end_distance + p_fo + weld_thickness_flange + (2 * beam_tf) + (
                            2 * p_fi) + 10 + pitch_distance_2_3)  # Distance between the 3rd and 4th row of bolt from top

                if (pitch_distance_2_3 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_2_3 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 10:
                pitch_distance_1_2 = pitch_distance_3_4 = pitch_dist_min  # Distance between 1st, 2nd and 3rd, 4th row of bolt from top
                pitch_distance_4_5 = height_available - (min_end_distance + pitch_distance_1_2 + p_fo + weld_thickness_flange + (2 * beam_tf) + 10 + (
                            2 * p_fi) + pitch_distance_3_4)  # Distance between the 4th and 5th row of bolt from top

                if (pitch_distance_1_2 < pitch_dist_min) or (pitch_distance_3_4 < pitch_dist_min) or (pitch_distance_4_5 < pitch_dist_min):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if (pitch_distance_1_2 > pitch_dist_max) or (pitch_distance_3_4 > pitch_dist_max) or (pitch_distance_4_5 > pitch_dist_max):
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")
        else:
            if number_of_bolts == 8:
                pitch_distance = height_available - ((2 * end_dist_mini) + (2 * l_v) + (4 * weld_thickness_flange) + (2 * beam_tf) + (2 * l_v))

                if pitch_distance < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")
                if pitch_distance > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 12:
                pitch_distance_2_3 = pitch_distance_4_5 = pitch_dist_min
                pitch_distance_3_4 = height_available - (
                            (2 * end_dist_mini) + (2 * l_v) + (4 * weld_thickness_flange) + (2 * beam_tf) + (2 * l_v) + pitch_distance_2_3 + pitch_distance_4_5)

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_4_5 and pitch_distance_3_4) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 16:
                pitch_distance_2_3 = pitch_distance_3_4 = pitch_distance_5_6 = pitch_distance_6_7 = pitch_dist_min
                pitch_distance_4_5 = height_available - ((2 * end_dist_mini) + (4 * l_v) + (4 * weld_thickness_flange) + (2 * beam_tf) + (4 * pitch_dist_min))

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_2_3 and pitch_distance_3_4 and pitch_distance_5_6 and pitch_distance_6_7 and pitch_distance_4_5) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

            elif number_of_bolts == 20:
                pitch_distance_1_2 = pitch_distance_9_10 = pitch_dist_min
                pitch_distance_3_4 = pitch_distance_4_5 = pitch_distance_6_7 = pitch_distance_7_8 = pitch_dist_min
                pitch_distance_5_6 = height_available - ((2 * end_dist_mini) + (4 * l_v) + (2 * beam_tf) + (4 * weld_thickness_flange) + (6 * pitch_dist_min))

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) < pitch_dist_min:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is smaller than the minimum required value ")
                    logger.warning(": Minimum required Pitch distance (Clause 10.2.2, IS 800:2007) is % 2.2f mm" % pitch_dist_min)
                    logger.info(": Re-design the connection using bolt of smaller diameter")

                if (pitch_distance_1_2 and pitch_distance_3_4 and pitch_distance_4_5 and pitch_distance_6_7 and pitch_distance_7_8 and pitch_distance_9_10 and pitch_distance_5_6) > pitch_dist_max:
                    design_status = False
                    logger.error(": Detailing Error - Pitch distance is greater than the maximum allowed value ")
                    logger.warning(": Maximum allowed Pitch distance (Clause 10.2.3, IS 800:2007) is % 2.2f mm" % pitch_dist_max)
                    logger.info(": Re-design the connection using bolt of higher diameter")

        end_plate_height_provided = height_available
        end_plate_width_provided = end_plate_width
        cross_centre_gauge = end_plate_width_provided - (2 * edge_dist_mini)

        # end_plate_width_provided = max(beam_B + 25, g_1 + (2 * edge_dist_mini))
        edge_dist_mini = (end_plate_width_provided - g_1) / 2
        if uiObj["detailing"]["typeof_edge"] == "a - Sheared or hand flame cut":
            end_dist_mini = int(math.ceil(1.7 * dia_hole))
        else:
            end_dist_mini = min_edge_distance = int(float(1.5 * dia_hole))
        # cross_centre_gauge = end_plate_width_provided - (2 * edge_dist_mini)
        # cross_centre_gauge = max(float(90), float(((2 * min_edge_distance) + beam_tw)))
        cross_centre_gauge = max(float(90), g_1)

    #######################################################################
    # Validation of calculated Height and Width of End Plate

    if uiObj["Member"]["Connectivity"] == "Flush":
        if number_of_bolts == 4 or number_of_bolts == 6:
            if end_plate_height_provided < end_plate_height_mini:
                design_status = False
                logger.error(": Height of End Plate is less than the minimum required height")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % end_plate_height_mini)
                logger.info(": Increase the Height of End Plate")
            if end_plate_height_provided > end_plate_height_max:
                design_status = False
                logger.error(": Height of End Plate exceeds the maximum allowed height")
                logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % end_plate_height_max)
                logger.info(": Decrease the Height of End Plate")

    elif uiObj["Member"]["Connectivity"] == "Extended one way":
        if number_of_bolts == 6 or number_of_bolts == 8:
            if end_plate_height_provided < end_plate_height_mini:
                design_status = False
                logger.error(": Height of End Plate is less than the minimum required height")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % end_plate_height_mini)
                logger.info(": Increase the Height of End Plate")
            if end_plate_height_provided > end_plate_height_max:
                design_status = False
                logger.error(": Height of End Plate exceeds the maximum allowed height")
                logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % end_plate_height_max)
                logger.info(": Decrease the Height of End Plate")
        else:
            if end_plate_height_provided < (end_plate_height_mini + pitch_distance_1_2):
                design_status = False
                logger.error(": Height of End Plate is less than the minimum required height")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % (end_plate_height_mini + pitch_distance_1_2))
                logger.info(": Increase the Height of End Plate")
            if end_plate_height_provided > (end_plate_height_max + pitch_distance_1_2):
                design_status = False
                logger.error(": Height of End Plate exceeds the maximum allowed height")
                logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % (end_plate_height_max + pitch_distance_1_2))
                logger.info(": Decrease the Height of End Plate")

    else:
        if number_of_bolts == 8 or number_of_bolts == 12 or number_of_bolts == 16:
            if end_plate_height_provided < end_plate_height_mini:
                design_status = False
                logger.error(": Height of End Plate is less than the minimum required height")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % end_plate_height_mini)
                logger.info(": Increase the Height of End Plate")
            if end_plate_height_provided > end_plate_height_max:
                design_status = False
                logger.error(": Height of End Plate exceeds the maximum allowed height")
                logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % end_plate_height_max)
                logger.info(": Decrease the Height of End Plate")

        elif number_of_bolts == 20:
            if end_plate_height_provided < (end_plate_height_mini + (2 * pitch_dist_min)):
                design_status = False
                logger.error(": Height of End Plate is less than the minimum required height")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % end_plate_height_mini)
                logger.info(": Increase the Height of End Plate")
            if end_plate_height_provided > (end_plate_height_max + (2 * pitch_dist_min)):
                design_status = False
                logger.error(": Height of End Plate exceeds the maximum allowed height")
                logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % end_plate_height_max)
                logger.info(": Decrease the Height of End Plate")

    if end_plate_width_provided < end_plate_width_mini:
        design_status = False
        logger.error(": Width of the End Plate is less than the minimum required value ")
        logger.warning(": Minimum End Plate width required is %2.2f mm" % end_plate_width_mini)
        logger.info(": Increase the width of End Plate")

    if end_plate_width_provided > end_plate_width_max:
        design_status = False
        logger.error(": Width of the End Plate exceeds the maximum allowed width ")
        logger.warning(": Maximum allowed width of End Plate is %2.2f mm" % end_plate_width_max)
        logger.info(": Decrease the width of End Plate")

    # TODO: Check the range and add reference for the below g_1 values
    #######################################################################
    # Validation of calculated cross-centre gauge distance
    if cross_centre_gauge < 90:
        design_status = False
        logger.error(": The cross-centre gauge is less than the minimum required value (Steel designey_sqr manual, page 733, 6th edition - 2003) ")
        logger.warning(": The minimum required value of cross centre gauge is %2.2f mm" % g_1)
        logger.info(": Increase the width of the End Plate or decrease the diameter of the bolt")
    if cross_centre_gauge > 160:
        design_status = False
        logger.error(": The cross-centre gauge is greater than the maximum allowed value (Steel designey_sqr manual, page 733, 6th edition - 2003) ")
        logger.warning(": The maximum allowed value of cross centre gauge is 140 mm")
        logger.info(": Decrease the width of the End Plate or increase the diameter of the bolt")

    #######################################################################
    # Calculation of Tension in bolts
    # Assuming the Neutral axis to pass through the centre of the bottom flange
    # T1, T2, ..., Tn are the Tension in the bolts starting from top of the end plate and y1, y2, ..., yn are its corresponding distances from N.A

    if number_of_bolts == 4:  # flush ep
        y1 = beam_d - (beam_tf / 2) - beam_tf - p_fi
        y2 = (beam_tf / 2) + p_fi
        y = (y1 ** 2 + y2 ** 2)

        T1 = (M_u * 10 ** 3 * y1) / (2 * y)  # Here, T1 is the tension in the topmost bolt (i.e. critical bolt) starting from the tension flange

        T_f = (T1 * (beam_d - beam_tf)) / y1
        v_st = 2 * T1
        tension_critical_bolt = T1

    elif number_of_bolts == 6:

        if uiObj["Member"]["Connectivity"] == "Extended one way":
            y1 = (beam_d - beam_tf / 2) + p_fo
            y2 = y1 - (p_fo + beam_tf + p_fi)
            y3 = (beam_tf / 2) + p_fi
            y = (y1 ** 2 + y2 ** 2 + y3 ** 2)

            T1 = (M_u * 10 ** 3 * y1) / (2 * y)  # Here, T1 is the tension in the topmost bolt (i.e. critical bolt) starting from the tension flange

            T_f = (T1 * (beam_d - beam_tf)) / y1
            v_st = 2 * T1
            tension_critical_bolt = T1

        elif uiObj["Member"]["Connectivity"] == "Flush":
            y1 = beam_d - (beam_tf / 2) - beam_tf - p_fi
            y2 = y1 - pitch_distance_1_2
            y3 = (beam_tf / 2) + p_fi
            y = (y1 ** 2 + y2 ** 2 + y3 ** 2)

            T1 = (M_u * 10 ** 3 * y1) / (2 * y)  # Here, T1 is the tension in the topmost bolt (i.e. critical bolt) starting from the tension flange
            T2 = (M_u * 10 ** 3 * y2) / (2 * y)

            T_f = (T1 * (beam_d - beam_tf)) / y1
            v_st = 2 * (T1 + T2)
            tension_critical_bolt = T1

    elif number_of_bolts == 8:

        if uiObj["Member"]["Connectivity"] == "Extended one way":
            y1 = (beam_d - beam_tf / 2) + p_fo
            y2 = y1 - (p_fo + beam_tf + p_fi)
            y3 = y2 - pitch_distance_2_3
            y4 = (beam_tf / 2) + p_fi
            y = (y1 ** 2 + y2 ** 2 + y3 ** 2 + y4 ** 2)

            T1 = (M_u * 10 ** 3 * y1) / (2 * y)  # Here, T1 is the tension in the topmost bolt (i.e. critical bolt) starting from the tension flange

            T_f = (T1 * (beam_d - beam_tf)) / y1
            v_st = 2 * T1
            tension_critical_bolt = T1

        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            y1 = (beam_d - beam_tf / 2) + weld_thickness_flange + l_v
            y2 = y1 - ((2 * l_v) + (2 * weld_thickness_flange) + beam_tf)
            y3 = weld_thickness_flange + l_v + (beam_tf / 2)
            y = (y1 ** 2 + y2 ** 2 + y3 ** 2)

            # Tension in bolt is divided by 2 because there is two columns of bolt
            T1 = (M_u * 10 ** 3 * y1) / (2 * y)  # Here, T1 is the tension in the topmost bolt (i.e. critical bolt) starting from the tension flange
            T2 = (M_u * 10 ** 3 * y2) / (2 * y)
            T3 = (M_u * 10 ** 3 * y3) / (2 * y)

            T_f = (T1 * (beam_d - beam_tf)) / y1
            v_st = 2 * T1
            tension_critical_bolt = T1
        else:
            pass

    elif number_of_bolts == 10:  # extended one way
        y1 = (beam_d - beam_tf / 2) + p_fo + pitch_distance_1_2
        y2 = y1 - pitch_distance_1_2
        y3 = y2 - p_fo - beam_tf - p_fi
        y4 = y3 - pitch_distance_3_4
        y5 = (beam_tf / 2) + p_fi
        y = (y1 ** 2 + y2 ** 2 + y3 ** 2 + y4 ** 2 + y5 ** 2)

        T1 = (M_u * 10 ** 3 * y1) / (2 * y)  # Here, T1 is the tension in the topmost bolt (i.e. critical bolt) starting from the tension flange
        T2 = (M_u * 10 ** 3 * y2) / (2 * y)

        T_f = (T1 * (beam_d - beam_tf)) / y1
        v_st = 2 * (T1 + T2)
        tension_critical_bolt = T1

    elif number_of_bolts == 12:  # extended both ways
        y1 = (beam_d - beam_tf / 2) + weld_thickness_flange + l_v
        y2 = y1 - ((2 * l_v) + (2 * weld_thickness_flange) + beam_tf)
        y3 = y2 - pitch_distance_2_3
        y4 = (beam_tf / 2) + weld_thickness_flange + l_v + pitch_dist_min
        y5 = y4 - pitch_distance_4_5
        y = (y1 ** 2 + y2 ** 2 + y3 ** 2 + y4 ** 2 + y5 ** 2)

        T1 = (M_u * 10 ** 3 * y1) / (2 * y)
        T2 = (M_u * 10 ** 3 * y2) / (2 * y)
        T3 = (M_u * 10 ** 3 * y3) / (2 * y)
        T4 = (M_u * 10 ** 3 * y4) / (2 * y)
        T5 = (M_u * 10 ** 3 * y5) / (2 * y)

        T_f = (T1 * (beam_d - beam_tf)) / y1
        v_st = 2 * T1
        tension_critical_bolt = T1

    elif number_of_bolts == 16:  # extended both ways
        y1 = (beam_d - beam_tf / 2) + weld_thickness_flange + l_v
        y2 = y1 - ((2 * l_v) + (2 * weld_thickness_flange) + beam_tf)
        y3 = y2 - pitch_distance_2_3
        y4 = y3 - pitch_distance_3_4
        y5 = (beam_tf / 2) + weld_thickness_flange + l_v + (2 * pitch_dist_min)
        y6 = y5 - pitch_distance_5_6
        y7 = y6 - pitch_distance_6_7
        y = (y1 ** 2 + y2 ** 2 + y3 ** 2 + y4 ** 2 + y5 ** 2 + y6 ** 2 + y7 ** 2)

        T1 = (M_u * 10 ** 3 * y1) / (2 * y)
        T2 = (M_u * 10 ** 3 * y2) / (2 * y)
        T3 = (M_u * 10 ** 3 * y3) / (2 * y)
        T4 = (M_u * 10 ** 3 * y4) / (2 * y)
        T5 = (M_u * 10 ** 3 * y5) / (2 * y)
        T6 = (M_u * 10 ** 3 * y6) / (2 * y)
        T7 = (M_u * 10 ** 3 * y7) / (2 * y)

        T_f = (T1 * (beam_d - beam_tf)) / y1
        v_st = 2 * T1
        tension_critical_bolt = T1

    elif number_of_bolts == 20:  # extended both ways
        y1 = (beam_d - beam_tf / 2) + weld_thickness_flange + l_v + pitch_distance_1_2
        y2 = y1 - pitch_distance_1_2
        y3 = y2 - (beam_tf + (2 * l_v) + (2 * weld_thickness_flange))
        y4 = y3 - pitch_distance_3_4
        y5 = y4 - pitch_distance_4_5
        y6 = y5 - pitch_distance_5_6
        y7 = y6 - pitch_distance_6_7
        y8 = y7 - pitch_distance_7_8
        y = (y1 ** 2 + y2 ** 2 + y3 ** 2 + y4 ** 2 + y5 ** 2 + y6 ** 2 + y7 ** 2 + y8 ** 2)

        T1 = (M_u * 10 ** 3 * y1) / (2 * y)
        T2 = (M_u * 10 ** 3 * y2) / (2 * y)
        T3 = (M_u * 10 ** 3 * y3) / (2 * y)
        T4 = (M_u * 10 ** 3 * y4) / (2 * y)
        T5 = (M_u * 10 ** 3 * y5) / (2 * y)
        T6 = (M_u * 10 ** 3 * y6) / (2 * y)
        T7 = (M_u * 10 ** 3 * y7) / (2 * y)
        T8 = (M_u * 10 ** 3 * y8) / (2 * y)

        T_f = (T1 * (beam_d - beam_tf)) / y1
        v_st = 2 * (T1 + T2)
        tension_critical_bolt = T1

    else:
        design_status = False

    #######################################################################
    # Calculating actual required thickness of End Plate (tp_required) as per bending criteria
    #######################################################################

    # Calculating Prying force in the bolt
    # NOte: We have used thick plate approach for the ep design. In this approach it is assumed that there will not be any prying force acting on the bolt since the ep is sufficiently thick
    # However, we are incorporating the prying force in the bolt check to be more conservative and was also recommended by the Expert committee (Excomm)

    b_e = end_plate_width_provided / 2
    if uiObj['bolt']['bolt_type'] == "pre-tensioned":
        beta = float(1)
    else:
        beta = float(2)
    eta = 1.5
    f_0 = 0.7 * (bolt_fu / 1000)  # kN/mm**2
    l_e = min(float(end_dist_mini), float(1.1 * end_plate_thickness * math.sqrt((beta * f_0 * 10 ** 3) / bolt_fy)))

    # Calculating T_e for all the configurations and connectivity types

    if number_of_bolts == 4:
        T_e = max(T_flange / 2, 0)
    elif number_of_bolts == 6:
        T_e = max(T_flange / 4, 0)
    elif number_of_bolts == 8:
        if uiObj["Member"]["Connectivity"] == "Extended one way":
            T_e = max(T_flange / 6, 0)
        else:
            T_e = max(T_flange / 4, 0)
    elif number_of_bolts == 10:
        T_e = max(T_flange / 8, 0)
    elif number_of_bolts == 12 or 16 or 20:
        T_e = max((T_flange / (number_of_bolts / 2)), 0)
    else:
        pass

    Q = round(prying_force(T_e, p_fo or l_v, l_e, beta, eta, f_0, b_e, end_plate_thickness), 3)

    # Check for tension in the critical bolt
    if tension_critical_bolt >= bolt_tension_capacity:
        design_status = False
        logger.error(": Tension in the critical bolt exceeds its tension carrying capacity")
        if bolt_type == "Friction Grip Bolt":
            logger.warning(": Maximum allowed tension in the critical bolt of selected diameter is %2.2f mm (Clause 10.4.5, IS 800:2007)" % bolt_tension_capacity)
        else:
            logger.warning(": Maximum allowed tension in the critical bolt of selected diameter is %2.2f mm (Clause 10.3.5, IS 800:2007)" % bolt_tension_capacity)
        logger.info(": Increase bolt diameter/grade")
        Q_allowable = float(0)
    else:
        Q_allowable = round(bolt_tension_capacity - tension_critical_bolt, 3)  # check for allowable prying force in each of the critical bolt of the configuration

    # Check for prying force in each bolt
    if Q > Q_allowable:
        design_status = False
        logger.error(": Prying force in the critical bolt exceeds its allowable limit")
        logger.warning(": Maximum allowed prying force in the critical bolt is %2.2f kN" % Q_allowable)
        logger.info(": Increase end plate thickness or bolt diameter")
    else:
        pass

    # Finding the end plate thickness (taking moment about toe of weld and equating with the plastic moment capacity of the end plate)
    M_p = round(((T_e * p_fo) - (Q * l_e)), 3)  # kN-mm
    tp_required = math.sqrt((M_p * 10 ** 3 * 1.10 * 4) / (end_plate_fy * b_e))
    tp_provided = math.ceil(tp_required / 2.) * 2

    if end_plate_thickness < tp_provided:
        design_status = False
        logger.error(": Chosen end plate thickness in not sufficient")
        logger.warning(": Minimum required thickness of end plate is %2.2f mm" % math.ceil(tp_required))
        logger.info(": Increase end plate thickness")
    else:
        pass

    # Check for tension in the critical bolt

    # Tension in critical bolt due to external factored moment + prying action
    T_b = tension_critical_bolt + Q

    if bolt_type == "Friction Grip Bolt":
        if T_b >= Tdf:
            design_status = False
            logger.error(": Tension acting on the critical bolt exceeds its tension carrying capacity ")
            logger.warning(": Maximum allowed tension on Friction Grip Bolt bolt (Clause 10.4.5, IS 800:2007) of selected diameter is %2.2f kN" % Tdf)
            logger.info(": Re-design the connection using bolt of higher diameter or grade")
    else:
        if T_b >= Tdb:
            design_status = False
            logger.error(": Tension acting on the critical bolt exceeds its tension carrying capacity ")
            logger.warning(": Maximum allowed tension on Bearing bolt (Clause 10.3.5, IS 800:2007) of selected diameter is %2.2f kN" % Tdb)
            logger.info(": Re-design the connection using bolt of higher diameter or grade")

    #######################################################################
    # Moment demand of End Plate
    M_d = ((tp_required ** 2 * end_plate_fy * b_e) / 4.4 * 1000) * 10 ** -6  # kN-m

    # Moment Capacity of End Plate
    M_c = ((tp_provided ** 2 * end_plate_fy * b_e) / 4.4 * 1000) * 10 ** -6  # kN-m

    if M_d > M_c:
        design_status = False
        logger.error(": The moment demand on end plate exceeds its moment carrying capacity")
        logger.warning(": The moment carrying capacity of end plate is %2.2f kNm" % M_c)
        logger.info(": Increase end plate thickness")

    #######################################################################
    # Check for Combined shear and tension capacity of bolt

    # 1. Friction Grip Bolt bolt (Cl. 10.4.6, IS 800:2007)
    # Here, Vsf = Factored shear load acting on single bolt, Vdf = shear capacity of single Friction Grip Bolt bolt
    # Tf = External factored tension acting on a single Friction Grip Bolt bolt, Tdf = Tension capacity of single Friction Grip Bolt bolt

    # 2. Bearing bolt (Cl. 10.3.6, IS 800:2007)
    # Here, Vsb = Factored shear load acting on single bolt, Vdb = shear capacity of single bearing bolt
    # Tb = External factored tension acting on single bearing bolt, Tdb = Tension capacity of single bearing bolt

    if bolt_type == "Friction Grip Bolt":
        Vsf = factored_shear_load / float(number_of_bolts)
        Vdf = V_dsf
        Tf = T_b
    else:
        Vsb = factored_shear_load / float(number_of_bolts)
        Vdb = V_db
        Tb = T_b

    if bolt_type == "Friction Grip Bolt":
        combined_capacity = (Vsf / Vdf) ** 2 + (Tf / Tdf) ** 2

        if combined_capacity > 1.0:
            design_status = False
            logger.error(": Load due to combined shear and tension on selected Friction Grip Bolt bolt exceeds the limiting value")
            logger.warning(": The maximum allowable value is 1.0 (Clause 10.4.6, IS 800:2007)")
            logger.info(": Re-design the connection using bolt of higher diameter or grade")
    else:
        combined_capacity = (Vsb / Vdb) ** 2 + (Tb / Tdb) ** 2

        if combined_capacity > 1.0:
            design_status = False
            logger.error(": Load due to combined shear and tension on selected Bearing Bolt exceeds the limiting value")
            logger.warning(": The maximum allowable value is 1.0 (Clause 10.3.6, IS 800:2007)")
            logger.info(": Re-design the connection using bolt of higher diameter or grade")

    #######################################################################
    # Check for Shear yielding and shear rupture of end plate

    # 1. Shear yielding of end plate (Clause 8.4.1, IS 800:2007)
    # if end_plate_width != 0:
    #     A_v = end_plate_width_provided * tp_provided  # gross shear area of end plate
    # else:

    A_v = end_plate_width_provided * tp_provided  # gross shear area of end plate
    V_d = shear_yielding(A_v, end_plate_fy)

    if V_d < factored_shear_load:
        design_status = False
        logger.error(": The End Plate might yield due to Shear")
        logger.warning(": The minimum required shear yielding capacity is %2.2f kN" % factored_shear_load)
        logger.info(": Increase the thickness of End Plate")

    # 2. Shear rupture of end plate (Clause 8.4.1, IS 800:2007)
    A_vn = A_v - (number_of_bolts * dia_hole)
    R_n = shear_rupture(A_vn, end_plate_fu)

    if R_n < factored_shear_load:
        design_status = False
        logger.error(": The End Plate might rupture due to Shear")
        logger.warning(": The minimum shear rupture capacity required is %2.2f kN" % factored_shear_load)
        logger.info(": Increase the thickness of End Plate")

    # TODO add block shear check

    #######################################################################
    # Member Checks
    # Strength of flange under Compression (Reference: Example 5.23 & 5.27, Design of Steel structures by Dr. N. Subramanian)

    A_f = beam_B * beam_tf  # area of beam flange
    capacity_beam_flange = ((beam_fy / 1.10) * A_f) / 1000  # kN
    force_flange = T_flange  # T_flange will act as compressive force at the compression flange
    # force_flange = (M_u * 10 ** 3 / (beam_d - beam_tf)) + (factored_axial_load / 2)

    if capacity_beam_flange < force_flange:
        design_status = False
        logger.error(": Force acting on the compression flange is greater than its load carrying capacity")
        logger.warning(": The maximum allowable force on the beam flange for the selected section is %2.2f kN" % capacity_beam_flange)
        logger.info(": Use a deeper beam section with wider and/or thicker flange")

    #######################################################################
    # Design of Weld
    #######################################################################

    if uiObj["Weld"]["Type"] == "Fillet Weld":

        # Assumption: The size of weld at flange will be greater than the size of weld at the web
        # Weld at flange resists bending moment whereas the weld at web resists shear + axial load

        # Ultimate and yield strength of welding material is assumed as Fe410 (E41 electrode)
        # (Reference: Design of Steel structures by Dr. N. Subramanian)

        # Minimum weld size (mm)
        # Minimum weld size at flange (for drop-down list)
        # Minimum weld size (tw_minimum) depends on the thickness of the thicker part (Table 21, IS 800:2007)

        t_thicker = max(beam_tf, beam_tw, tp_provided)
        t_thinner_weld = min(beam_tf, beam_tw, tp_provided)

        if t_thicker <= 10.0:
            tw_minimum = 3
        elif t_thicker > 10.0 and t_thicker <= 20.0:
            tw_minimum = 5
        elif t_thicker > 20.0 and t_thicker <= 32.0:
            tw_minimum = 6
        elif t_thicker > 32.0 and t_thicker <= 50.0:
            tw_minimum = 8

        if weld_thickness_flange < tw_minimum:
            design_status = False
            logger.error(": Selected weld size at flange is less than the minimum required value")
            logger.warning(": Minimum weld size required at flange (as per Table 21, IS 800:2007) is %2.2f mm " % tw_minimum)
            logger.info(": Increase the weld size at flange")

        if weld_thickness_web < tw_minimum:
            design_status = False
            logger.error(": Selected weld size at web is less than the minimum required value")
            logger.warning(": Minimum weld size required at web (as per Table 21, IS 800:2007) is %2.2f mm " % tw_minimum)
            logger.info(": Increase the weld size at web")


        # Design of weld at flange
        # Capacity of unit weld (Clause 10.5.7, IS 800:2007)
        k = 0.7  # constant (Table 22, IS 800:2007)
        t_te = max(3, (0.7 * t_thinner_weld))  # effective throat thickness (Cl. 10.5.3.1, IS 800:2007)

        # capacity_unit_flange is the capacity of weld of unit throat thickness
        capacity_unit_flange = (k * weld_fu_govern) / (math.sqrt(3) * gamma_mw)  # N/mm**2 or MPa

        # Calculating the effective length of weld at the flange
        L_effective_flange = ((2 * beam_B) + (2 * (beam_B - beam_tw - beam_R1))) - (6 * weld_thickness_flange)  # mm

        # Calculating the area of weld at flange (a_weld_flange)
        a_weld_flange = L_effective_flange * t_te  # mm**2

        # Calculating stresses on weld
        # Assumption: The weld at flanges are designed to carry Factored external moment and moment due to axial load,
        # whereas, the weld at beam web are designed to resist factored shear force and axial loads

        # 1. Direct stress (DS)

        # Since there is no direct stress (DS_flange) acting on weld at flange, the value of direct stress will be zero
        DS_flange = 0

        # 2. Bending Stress (BS)
        # Finding section modulus i.e. Z = Izz / y (Reference: Table 6.7, Design of Steel structures by Dr. N. Subramanian)
        # Z = (beam_B * beam_d) + (beam_d ** 2 / 3)  # mm **3
        Z = (beam_B + (beam_B - beam_tw - (2 * beam_R1) - (6 * weld_thickness_flange))) * beam_d  # mm **3
        BS_flange = (M_u * 10 ** 3) / Z

        # Resultant (R)
        R = math.sqrt(DS_flange ** 2 + BS_flange ** 2)

        # Actual required size of weld
        t_weld_flange_actual = math.ceil((R * 10 ** 3) / capacity_unit_flange)  # mm

        if t_weld_flange_actual % 2 == 0:
            t_weld_flange = t_weld_flange_actual
        else:
            t_weld_flange = t_weld_flange_actual + 1

        if weld_thickness_flange < t_weld_flange:
            design_status = False
            logger.error(": Weld size at the flange is not sufficient")
            logger.warning(": Minimum weld size required is %2.2f mm " % t_weld_flange_actual)
            logger.info(": Increase the weld size at flange")
        if weld_thickness_flange > min(beam_tf, tp_provided):
            design_status = False
            logger.error(": Weld size at the flange exceeds the maximum allowed value")
            logger.warning(": Maximum allowed weld size at the flange is %2.2f mm" % min(beam_tf, tp_provided))
            logger.info(": Decrease the weld size at flange")

        # Design of weld at web

        t_weld_web = int(min(beam_tw, tp_required))

        if t_weld_web % 2 == 0:
            t_weld_web = t_weld_web
        else:
            t_weld_web -= 1

        if t_weld_web > t_weld_flange:
            t_weld_web = t_weld_flange
        else:
            t_weld_web = t_weld_web

        if weld_thickness_web < t_weld_web:
            design_status = False
            logger.error(": Weld size at the web is not sufficient")
            logger.warning(": Minimum weld size required is %2.2f mm" % t_weld_web)
            logger.info(": Increase the weld size at web")
        if weld_thickness_web > int(min(beam_tw, tp_required)):
            design_status = False
            logger.error(": Weld size at the web exceeds the maximum allowed value")
            logger.warning(": Maximum allowed weld size at the web is %2.2f mm" % int(min(beam_tw, tp_required)))
            logger.info(": Decrease the weld size at web")

        if (weld_thickness_flange or weld_thickness_web) > (2 * tw_minimum):
            logger.warning(": The required weld size is higher, It is recommended to provide full penetration butt weld")

        #######################################################################
        # Weld Checks
        # Check for stresses in weld due to individual force (Clause 10.5.9, IS 800:2007)

        # Weld at flange
        # 1. Check for normal stress

        f_a_flange = (force_flange * 10 ** 3) / (t_te * L_effective_flange)  # Here, 3 mm is the effective minimum throat thickness

        # Design strength of fillet weld (Clause 10.5.7.1.1, IS 800:2007)
        f_wd = weld_fu_govern / (math.sqrt(3) * gamma_mw)

        if f_a_flange > f_wd:
            design_status = False
            logger.error(": The stress in weld at flange exceeds the limiting value")
            logger.warning(": Maximum stress weld can carry is %2.2f N/mm^2 (Clause 10.5.7.1.1, IS 800:2007)" % f_wd)
            logger.info(": Increase the Ultimate strength of weld and/or length of weld")

        # Weld at web
        L_effective_web = 2 * ((beam_d - (2 * beam_tf) - (2 * beam_R1)) - (2 * weld_thickness_web))

        # 1. Check for normal stress (Clause 10.5.9, IS 800:2007)
        f_a_web = factored_axial_load * 10 ** 3 / (t_te * L_effective_web)

        # 2. Check for shear stress
        q_web = factored_shear_load * 10 ** 3 / (t_te * L_effective_web)

        # 3. Combination of stress (Clause 10.5.10.1.1, IS 800:2007)

        f_e = math.sqrt(f_a_web ** 2 + (3 * q_web ** 2))

        if f_e > f_wd:
            design_status = False
            logger.error(": The stress in weld due to combination of shear and axial force at web exceeds the limiting value")
            logger.warning(": Maximum stress due to combination of forces the weld can carry is %2.2f N/mm^2 (Clause 10.5.10.1.1, IS 800:2007)" % f_wd)
            logger.info(": Increase the Ultimate strength of weld and/or length of weld")

    else:
        k = 1
        weld_size_butt = end_plate_thickness


    #######################################################################
    # Design of Stiffener

    # TODO: add material strengths for below condition (design preference?)
    stiffener_fy = beam_fy
    stiffener_fu = beam_fu

    # Thickness of stiffener
    ts1 = beam_tw
    ts2 = (beam_fy / stiffener_fy) * beam_tw
    thickness_stiffener = math.ceil(max(ts1, ts2))

    thickness_stiffener_provided = math.ceil(thickness_stiffener / 2.) * 2  # round off to the nearest higher multiple of two

    # size of notch (n_s) in the stiffener
    if uiObj["Weld"]["Type"] == "Fillet Weld":
        n_s = weld_thickness_flange + 5
    else:
        n_s = 5

    # calculating effective length of the stiffener and the weld
    l_st_effective = ((v_st * 10 ** 3 * math.sqrt(3) * 1.10) / (thickness_stiffener_provided * stiffener_fy)) + n_s  # calculating effective length of the stiffener as per shear criteria

    if uiObj["Weld"]["Type"] == "Fillet Weld":
        l_weld_effective = ((v_st * 10 ** 3 * math.sqrt(3) * gamma_mw) / (2 * k * weld_thickness_flange * weld_fu_govern)) - (2 * weld_thickness_flange)  # effective required length of weld (either sides) as per weld criteria
    else:
        l_weld_effective = ((v_st * 10 ** 3 * math.sqrt(3) * gamma_mw) / (2 * k * weld_size_butt * weld_fu_govern))

    # Height of stiffener (h_st) (mm)
    # TODO: Do calculation for actual height of end plate above

    if uiObj["Member"]["Connectivity"] == "Extended one way":
        h_st = end_plate_height_provided - beam_d - weld_thickness_flange - 10
    elif uiObj["Member"]["Connectivity"] == "Extended both ways":
        h_st = (end_plate_height_provided - beam_d) / 2
    else:
        w_st = (end_plate_width_provided - beam_tw) / 2  # width in case of flush end plate

    if uiObj["Member"]["Connectivity"] == "Flush":
        l_st = max(l_st_effective, (l_weld_effective / 2))  # taking the maximum length out of the two possibilities
    else:
        # Length of stiffener (l_st) (as per AISC, DG 16 recommendations)
        cf = math.pi / 180  # convey_sqrion factor to convert degree into radian
        l_stiffener = math.ceil(((h_st - 25) / math.tan(30 * cf)) + 25)

        l_st = max(l_st_effective, (l_weld_effective / 2), l_stiffener)  # taking the maximum length out of the three possibilities

    # Length and size of weld for the stiffener (on each side)
    l_weld_st = l_st  # length of weld provided along the length of the stiffener

    if uiObj["Member"]["Connectivity"] == "Flush":
        w_weld_st = w_st  # length of weld to be provided along the width of the stiffener

        if uiObj["Weld"]["Type"] == "Fillet Weld":
            z_weld_st = min(weld_thickness_web, thickness_stiffener_provided)  # size of weld for stiffener at web
        else:
            z_weld_st = thickness_stiffener_provided
    else:
        h_weld_st = h_st  # length of weld provided along the height of the stiffener

        if uiObj["Weld"]["Type"] == "Fillet Weld":
            z_weld_st = min(weld_thickness_flange, thickness_stiffener_provided)  # size of weld for stiffener at flange
        else:
            z_weld_st = thickness_stiffener_provided

    # Check for Moment in stiffener

    # Calculating the eccentricity (e) of the bolt group

    if uiObj["Member"]["Connectivity"] == "Extended one way" or uiObj["Member"]["Connectivity"] == "Extended both ways":
        if number_of_bolts == 6 or 8 or 12 or 16:
            e = h_st - end_dist_mini
        elif number_of_bolts == 10 or 20:
            e = h_st - end_dist_mini - (pitch_distance_1_2 / 2)
    else:
        if number_of_bolts == 4:
            e = pitch_dist_min
            s = beam_tf + p_fi + pitch_dist_min  # s is the distance of the stiffener from the outer edge of the beam flange to the outer edge of the stiffener plate
        elif number_of_bolts == 6:
            e = pitch_dist_min + (pitch_distance_1_2 / 2)
            s = beam_tf + p_fi + pitch_distance_1_2 + pitch_dist_min

    # Moment in stiffener (M_st)
    M_st = v_st * e

    # Moment capacity of stiffener
    M_capacity_st = ((l_st ** 2 * thickness_stiffener_provided * stiffener_fy) / (4 * 1.10)) * 10 ** -3

    if M_st > M_capacity_st:
        design_status = False
        logger.error(": The moment in stiffener exceeds its moment carrying capacity")
        logger.warning(": The moment carrying capacity of the stiffener is % 2.2f mm" % M_capacity_st)
        logger.info(": Increase the length and/or thickness of the stiffener")

    # Check in weld for the combined forces

    f_a = M_st / (2 * ((k * z_weld_st * l_weld_st ** 2) / 4))
    q = v_st / (2 * l_weld_st * 0.7 * z_weld_st)
    f_e = (math.sqrt(f_a ** 2 + (3 * q ** 2))) * 10 ** 3

    if f_e > (weld_fu / (math.sqrt(3) * gamma_mw)):

        # updating weld size

        if uiObj["Member"]["Connectivity"] == "Flush":
            z_weld_st = max(weld_thickness_web, thickness_stiffener_provided)  # updated size of weld for stiffener at web
        else:
            z_weld_st = max(weld_thickness_flange, thickness_stiffener_provided)  # updated size of weld for stiffener at flange

        f_a = M_st / (2 * ((k * z_weld_st * l_weld_st ** 2) / 4))
        q = v_st / (2 * l_weld_st * 0.7 * z_weld_st)
        f_e = (math.sqrt(f_a ** 2 + (3 * q ** 2))) * 10 ** 3

        if f_e > (weld_fu / (math.sqrt(3) * gamma_mw)):
            design_status = False
            logger.error(": The stress in the weld at stiffener subjected to a combination of normal and shear stress exceeds the maximum allowed value")
            logger.warning(": Maximum allowed stress in the weld under combined loading is % 2.2f N/mm^2 (Cl. 10.5.10, IS 800:2007)" % f_e)
            logger.info(": Increase the size of weld at the stiffener")
    else:
        pass

    # TODO: Is the below check required?
    # Check of stiffener against local buckling
    # E = 2 * 10 ** 5  # MPa
    # ts_required = 1.79 * h_st * stiffener_fy / E  # mm

    # if thickness_stiffener_provided < ts_required:
    #     design_status = False
    #     logger.error(": The thickness of stiffener is not sufficient")
    #     logger.error(": The stiffener might buckle locally (AISC Design guide 16)")
    #     logger.warning(": Minimum required thickness of stiffener to prevent local bucklimg is % 2.2f mm" % ts_required)
    #     logger.info(": Increase the thickness of stiffener")

    else:
        design_status = False
        logger.error(": The number of bolts exceeds 20")
        logger.warning(": Maximum number of bolts that can be accommodated in Extended End plate configuration is 20")
        logger.info(": Re-design the connection")

########################################################################################################################
    # End of Calculation
    # Output dictionary for different cases
    if number_of_bolts <= 20:

        outputobj = {}
        outputobj['Bolt'] = {}
        outputobj['Bolt']['status'] = design_status
        outputobj['Bolt']['CriticalTension'] = round(T_b, 3)
        outputobj['Bolt']['TensionCapacity'] = round(bolt_tension_capacity, 3)
        outputobj['Bolt']['ShearCapacity'] = round(bolt_shear_capacity, 3)
        outputobj['Bolt']['BearingCapacity'] = bearing_capacity
        outputobj['Bolt']['BoltCapacity'] = round(bolt_capacity, 3)
        outputobj['Bolt']['CombinedCapacity'] = round(combined_capacity, 3)
        outputobj['Bolt']['NumberOfBolts'] = int(number_of_bolts)
        outputobj['Bolt']['NumberOfRows'] = int(round(number_rows, 3))
        outputobj['Bolt']['BoltsPerColumn'] = int(n_c)
        outputobj['Bolt']['kb'] = float(round(k_b, 3))
        outputobj['Bolt']['SumPlateThick'] = float(round(sum_plate_thickness, 3))
        outputobj['Bolt']['BoltFy'] = bolt_fy

        if bolt_type == "Friction Grip Bolt":
            outputobj['Bolt']['Vsf'] = float(round(Vsf, 3))
            outputobj['Bolt']['Vdf'] = float(round(Vdf, 3))
            outputobj['Bolt']['Tf'] = float(round(Tf, 3))
            outputobj['Bolt']['Tdf'] = float(round(Tdf, 3))
        else:
            outputobj['Bolt']['Vsb'] = float(round(Vsb, 3))
            outputobj['Bolt']['Vdb'] = float(round(Vdb, 3))
            outputobj['Bolt']['Tb'] = float(round(Tb, 3))
            outputobj['Bolt']['Tdb'] = float(round(Tdb, 3))

        outputobj['Bolt']['PitchMini'] = pitch_dist_min
        outputobj['Bolt']['PitchMax'] = pitch_dist_max
        outputobj['Bolt']['EndMax'] = end_dist_max
        outputobj['Bolt']['EndMini'] = end_dist_mini
        outputobj['Bolt']['DiaHole'] = int(dia_hole)

        if uiObj["Member"]["Connectivity"] == "Flush":
            if number_of_bolts == 4:
                outputobj['Bolt']['Pitch'] = float(pitch_distance)
            elif number_of_bolts == 6:
                outputobj['Bolt']['Pitch12'] = float(pitch_distance_1_2)
                outputobj['Bolt']['Pitch23'] = float(pitch_distance_2_3)

            outputobj['Bolt']['TensionCritical'] = round(tension_critical_bolt, 3)  # Tension in critical bolt required for report generator
            outputobj['Bolt']['PryingForce'] = Q

        elif uiObj["Member"]["Connectivity"] == "Extended one way":
            if number_of_bolts == 6:
                outputobj['Bolt']['Pitch23'] = float(pitch_distance)
            elif number_of_bolts == 8:
                outputobj['Bolt']['Pitch23'] = float(pitch_distance_2_3)
                outputobj['Bolt']['Pitch34'] = float(pitch_distance_3_4)
            elif number_of_bolts == 10:
                outputobj['Bolt']['Pitch12'] = float(pitch_distance_1_2)
                outputobj['Bolt']['Pitch34'] = float(pitch_distance_3_4)
                outputobj['Bolt']['Pitch45'] = float(pitch_distance_4_5)

            outputobj['Bolt']['TensionCritical'] = round(tension_critical_bolt, 3)  # Tension in critical bolt required for report generator
            outputobj['Bolt']['PryingForce'] = Q

        else:
            if number_of_bolts == 8:
                outputobj['Bolt']['Pitch'] = float(pitch_distance)
                outputobj['Bolt']['TensionCritical'] = round(T1, 3)  # Tension in critical bolt required for report generator
                outputobj['Bolt']['PryingForce'] = Q
            elif number_of_bolts == 12:
                outputobj['Bolt']['Pitch23'] = float(pitch_distance_2_3)
                outputobj['Bolt']['Pitch34'] = float(pitch_distance_3_4)
                outputobj['Bolt']['Pitch45'] = float(pitch_distance_4_5)
                outputobj['Bolt']['TensionCritical'] = round(T1, 3)  # Tension in critical bolt required for report generator
                outputobj['Bolt']['PryingForce'] = Q
            elif number_of_bolts == 16:
                outputobj['Bolt']['Pitch23'] = float(pitch_distance_2_3)
                outputobj['Bolt']['Pitch34'] = float(pitch_distance_3_4)
                outputobj['Bolt']['Pitch45'] = float(pitch_distance_4_5)
                outputobj['Bolt']['Pitch56'] = float(pitch_distance_5_6)
                outputobj['Bolt']['Pitch67'] = float(pitch_distance_6_7)
                outputobj['Bolt']['TensionCritical'] = round(T1, 3)  # Tension in critical bolt required for report generator
                outputobj['Bolt']['PryingForce'] = Q
            elif number_of_bolts == 20:
                outputobj['Bolt']['Pitch12'] = float(pitch_distance_1_2)
                outputobj['Bolt']['Pitch34'] = float(pitch_distance_3_4)
                outputobj['Bolt']['Pitch45'] = float(pitch_distance_4_5)
                outputobj['Bolt']['Pitch56'] = float(pitch_distance_5_6)
                outputobj['Bolt']['Pitch67'] = float(pitch_distance_6_7)
                outputobj['Bolt']['Pitch78'] = float(pitch_distance_7_8)
                outputobj['Bolt']['Pitch910'] = float(pitch_distance_9_10)
                outputobj['Bolt']['TensionCritical'] = round(T1, 3)  # Tension in critical bolt required for report generator
                outputobj['Bolt']['PryingForce'] = Q

        outputobj['Bolt']['Gauge'] = float(gauge_dist_min)
        outputobj['Bolt']['CrossCentreGauge'] = float(cross_centre_gauge)
        outputobj['Bolt']['End'] = float(end_dist_mini)
        outputobj['Bolt']['Edge'] = float(edge_dist_mini)
        # ===================  CAD ===================
        if uiObj["Member"]["Connectivity"] == "Extended both ways":  # TODO: Here we are assigning p_fi to l_v for Extended one way and Flush EP for CAD
            outputobj['Bolt']['Lv'] = float(l_v)
        else:
            l_v = p_fi
            outputobj['Bolt']['Lv'] = float(l_v)
        # ===================  CAD ===================

        outputobj['Plate'] = {}
        outputobj['Plate']['Height'] = float(round(end_plate_height_provided, 3))
        outputobj['Plate']['Width'] = float(round(end_plate_width_provided, 3))
        # ===================  CAD ===================
        outputobj['Plate']['Thickness'] = float(round(end_plate_thickness, 3))
        # ===================  CAD ===================
        outputobj['Plate']['MomentDemand'] = round(M_d, 3)
        outputobj['Plate']['MomentCapacity'] = round(M_c, 3)

        outputobj['Plate']['ThickRequired'] = float(round(tp_required, 3))
        outputobj['Plate']['Mp'] = float(round(M_p, 3))

        if uiObj["Weld"]["Type"] == "Fillet Weld":
            outputobj['Weld'] = {}
            outputobj['Weld']['CriticalStressflange'] = round(f_a_flange, 3)
            outputobj['Weld']['CriticalStressWeb'] = round(f_e, 3)
            outputobj['Weld']['WeldStrength'] = round(f_wd, 3)
            outputobj['Weld']['ForceFlange'] = float(round(force_flange, 3))
            outputobj['Weld']['LeffectiveFlange'] = float(L_effective_flange)
            outputobj['Weld']['LeffectiveWeb'] = float(L_effective_web)

            outputobj['Weld']['FaWeb'] = float(round(f_a_web, 3))
            outputobj['Weld']['Qweb'] = float(round(q_web, 3))
            outputobj['Weld']['Resultant'] = float(round(R, 3))
            outputobj['Weld']['UnitCapacity'] = float(round(capacity_unit_flange, 3))
            outputobj['Weld']['WeldFuGovern'] = float(weld_fu_govern)

        else:
            outputobj['Weld'] = {}
            outputobj['Weld']['WeldSize'] = int(weld_size_butt)

        outputobj['Weld']['WeldFuGovern'] = float(weld_fu_govern)

        outputobj['Stiffener'] = {}
        if uiObj["Member"]["Connectivity"] == "Flush":
            outputobj['Stiffener']['Height'] = round(w_st, 3)
            outputobj['Stiffener']['Location'] = int(s)
        else:
            outputobj['Stiffener']['Height'] = round(h_st, 3)

        outputobj['Stiffener']['Length'] = round(l_st, 3)
        outputobj['Stiffener']['Thickness'] = float(round(thickness_stiffener_provided, 3))
        outputobj['Stiffener']['NotchSize'] = round(n_s, 3)
        outputobj['Stiffener']['WeldSize'] = int(z_weld_st)
        outputobj['Stiffener']['Moment'] = round((M_st * 10 ** -3), 3)
        outputobj['Stiffener']['MomentCapacity'] = round((M_capacity_st * 10 ** -3), 3)
        outputobj['Stiffener']['Notch'] = float(n_s)

        # ===================  CAD ===================
        # if uiObj["Member"]["Connectivity"] == "Extended one way":
        if uiObj["Member"]["Connectivity"] == "Extended one way" or "Flush":  # TOdo added by day_sqrhan
            outputobj['Plate']['Projection'] = weld_thickness_flange + 10
        else:
            pass
        # ===================  CAD ===================

    else:
        outputobj = {}
        outputobj['Bolt'] = {}
        outputobj['Bolt']['status'] = design_status
        outputobj['Bolt']['CriticalTension'] = 0
        outputobj['Bolt']['TensionCapacity'] = round(bolt_tension_capacity, 3)
        outputobj['Bolt']['ShearCapacity'] = round(bolt_shear_capacity, 3)
        outputobj['Bolt']['BearingCapacity'] = bearing_capacity
        outputobj['Bolt']['BoltCapacity'] = round(bolt_capacity, 3)
        outputobj['Bolt']['CombinedCapacity'] = 0
        outputobj['Bolt']['NumberOfBolts'] = int(number_of_bolts)
        outputobj['Bolt']['NumberOfRows'] = 0
        outputobj['Bolt']['BoltsPerColumn'] = 0
        outputobj['Bolt']['kb'] = float(round(k_b, 3))
        outputobj['Bolt']['SumPlateThick'] = float(round(sum_plate_thickness, 3))
        outputobj['Bolt']['BoltFy'] = bolt_fy

        if bolt_type == "Friction Grip Bolt":
            outputobj['Bolt']['Vsf'] = 0
            outputobj['Bolt']['Vdf'] = 0
            outputobj['Bolt']['Tf'] = 0
            outputobj['Bolt']['Tdf'] = 0
        else:
            outputobj['Bolt']['Vsb'] = 0
            outputobj['Bolt']['Vdb'] = 0
            outputobj['Bolt']['Tb'] = 0
            outputobj['Bolt']['Tdb'] = 0

        outputobj['Bolt']['PitchMini'] = pitch_dist_min
        outputobj['Bolt']['PitchMax'] = pitch_dist_max
        outputobj['Bolt']['EndMax'] = end_dist_max
        outputobj['Bolt']['EndMini'] = end_dist_mini
        outputobj['Bolt']['DiaHole'] = int(dia_hole)

        outputobj['Bolt']['Pitch'] = pitch_dist_min
        outputobj['Bolt']['TensionCritical'] = 0  # Tension in critical bolt required for report generator
        outputobj['Bolt']['PryingForce'] = 0

        outputobj['Bolt']['Gauge'] = float(gauge_dist_min)
        outputobj['Bolt']['CrossCentreGauge'] = 0
        outputobj['Bolt']['End'] = float(end_dist_mini)
        outputobj['Bolt']['Edge'] = float(edge_dist_mini)
        # ===================  CAD ===================
        if uiObj["Member"]["Connectivity"] == "Extended both ways":  # TODO: Here we are assigning p_fi to l_v for Extended one way and Flush EP for CAD
            outputobj['Bolt']['Lv'] = float(l_v)
        else:
            l_v = p_fi
            outputobj['Bolt']['Lv'] = float(l_v)
        # ===================  CAD ===================

        outputobj['Plate'] = {}
        outputobj['Plate']['Height'] = 0
        outputobj['Plate']['Width'] = 0
        # ===================  CAD ===================
        outputobj['Plate']['Thickness'] = float(round(end_plate_thickness, 3))
        # ===================  CAD ===================

        outputobj['Plate']['MomentDemand'] = 0
        outputobj['Plate']['MomentCapacity'] = 0
        outputobj['Plate']['ThickRequired'] = 0
        outputobj['Plate']['Mp'] = 0

        if uiObj["Weld"]["Type"] == "Fillet Weld":
            outputobj['Weld'] = {}
            outputobj['Weld']['CriticalStressflange'] = 0
            outputobj['Weld']['CriticalStressWeb'] = 0
            outputobj['Weld']['WeldStrength'] = 0
            outputobj['Weld']['ForceFlange'] = 0
            outputobj['Weld']['LeffectiveFlange'] = 0
            outputobj['Weld']['LeffectiveWeb'] = 0
            outputobj['Weld']['FaWeb'] = 0
            outputobj['Weld']['Qweb'] = 0
            outputobj['Weld']['Resultant'] = 0
            outputobj['Weld']['UnitCapacity'] = 0
            outputobj['Weld']['WeldFuGovern'] = float(weld_fu_govern)

        else:
            outputobj['Weld'] = {}
            outputobj['Weld']['WeldSize'] = 0

        outputobj['Weld']['WeldFuGovern'] = float(weld_fu_govern)


        outputobj['Stiffener'] = {}
        if uiObj["Member"]["Connectivity"] == "Flush":
            outputobj['Stiffener']['Height'] = 0
            outputobj['Stiffener']['Location'] = 0
        else:
            outputobj['Stiffener']['Height'] = 0

        outputobj['Stiffener']['Length'] = 0
        outputobj['Stiffener']['Thickness'] = 0
        outputobj['Stiffener']['NotchSize'] = 0
        outputobj['Stiffener']['WeldSize'] = 0
        outputobj['Stiffener']['Moment'] = 0
        outputobj['Stiffener']['MomentCapacity'] = 0
        outputobj['Stiffener']['Notch'] = 0

        # ===================  CAD ===================
        # if uiObj["Member"]["Connectivity"] == "Extended one way":
        if uiObj["Member"]["Connectivity"] == "Extended one way" or "Flush":  # TOdo added by day_sqrhan
            outputobj['Plate']['Projection'] = 0
        else:
            pass
        # ===================  CAD ===================

    ###########################################################################
    # End of Output dictionary
    
    if design_status == True:
        logger.info(": Overall extended end plate connection design is safe \n")
        logger.debug(" :=========End Of design===========")
    else:
        logger.error(": Design is not safe \n ")
        logger.debug(" :=========End Of design===========")

    return outputobj



















