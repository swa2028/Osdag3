"""
Started in Nov 2019

@author: Yash LOkhande


Module (Moment connection): 1. Column to Column extended both ways end plate splice connection
                            2. Column to Column flushed end plate splice connection

Reference:
            1) IS 800: 2007 General construction in steel - Code of practice (Third revision)
            2) Design of Steel structures by Dr. N Subramanian (chapter 5 and 6)
            3) Fundamentals of Structural steel design by M.L Gambhir
            4) AISC Design guide 16 and 4


"""

from .model import *
from utilities.is800_2007 import IS800_2007
from utilities.other_standards import IS1363_part_1_2002, IS1363_part_3_2002, IS1367_Part3_2002
from utilities.common_calculation import *
import math
import logging
import numpy as np
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

    bolt_dia = float(uiObj['Bolt']['Diameter (mm)'])
    bolt_type = (uiObj["Bolt"]["Type"])
    bolt_grade = float(uiObj['Bolt']['Grade'])
    bolt_fu = float(uiObj["bolt"]["bolt_fu"])
    bolt_fy = float((bolt_grade - int(bolt_grade)) * bolt_fu)

    mu_f = float(uiObj["bolt"]["slip_factor"])
    gamma_mw = float(uiObj["weld"]["safety_factor"])
    dp_bolt_hole_type = uiObj["bolt"]["bolt_hole_type"]
    if dp_bolt_hole_type == "Over-sized":
        bolt_hole_type = 'over_size'
    else:   # "Standard"
        bolt_hole_type = 'standard'

    dia_hole = bolt_dia + int(uiObj["bolt"]["bolt_hole_clrnce"])
    end_plate_thickness = [float(0),float(uiObj['Plate']['Thickness (mm)'])]

    # TODO implement after excomm review for different grades of plate
    end_plate_fu = float(uiObj['Member']['fu (MPa)'])
    end_plate_fy = float(uiObj['Member']['fy (MPa)'])

    weld_type = str(uiObj["Weld"]["Type"])  # This is - Fillet weld or Groove weld

    if weld_type == "Fillet":
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
        # logger.warning(": The input factored moment (%2.2f kN-m) is less that the minimum design action on the connection (Cl. 10.7-6, IS 800:2007)" % factored_moment)
        logger.info(": The connection is designed for %2.2f kN-m" % float(moment_minimum))

    factored_moment = round(moment_minimum, 3)

    #######################################################################
    # Calculation of Bolt strength in MPa
    bolt_fu = float(uiObj["bolt"]["bolt_fu"])
    bolt_fy = float((bolt_grade - int(bolt_grade)) * bolt_fu)

    #######################################################################
    # Calculation of Spacing

    # Minimum and maximum end distances (mm) [Cl. 10.2.4.2 & Cl. 10.2.4.3, IS 800:2007]
    end_dist_min = float(IS800_2007.cl_10_2_4_2_min_edge_end_dist(
        d=bolt_dia, bolt_hole_type=bolt_hole_type, edge_type=edge_type))

    end_dist_max = IS800_2007.cl_10_2_4_3_max_edge_dist(plate_thicknesses=end_plate_thickness, f_y=end_plate_fy,
                                                        corrosive_influences=corrosive_influences)

    # Minimum and maximum edge distances (mm) [Cl. 10.2.4.2 & Cl. 10.2.4.3, IS 800:2007]
    edge_dist_mini = end_dist_min
    edge_dist_max = end_dist_max

    # min_pitch & max_pitch = Minimum and Maximum pitch distance (mm) [Cl. 10.2.2, IS 800:2007]
    min_pitch = float(3.0 * bolt_dia)
    max_pitch = IS800_2007.cl_10_2_3_1_max_spacing(end_plate_thickness)

    # min_gauge & max_gauge = Minimum and Maximum gauge distance (mm) [Cl. 10.2.3.1, IS 800:2007]
    gauge_dist_min = min_pitch
    gauge_dist_max = max_pitch
    #######################################################################

    #######################################################################
    # Calculation for number of bolts
    #######################################################################

    no_bolts_web = ((column_d - (2 * column_tf) - (2 * end_dist_min)) / min_pitch) + 1
    no_bolts_web = int(math.floor(no_bolts_web))

    if no_bolts_web == 1 or no_bolts_web < 1:
        design_status = False
        logger.warning(": The bolt diameter selected is larger for the given section.")
        logger.info(": Decrease the bolt diameter or increase the size of section.")

    no_bolts_flange = (((column_B/2) - (column_tw / 2) - (2 * end_dist_min)) / min_pitch) + 1
    no_bolts_flange = math.floor(no_bolts_flange)

    no_of_bolts = int(no_bolts_web + (no_bolts_flange - 1))

####################################################################################
    # New values of pitch and end distance from detailing
####################################################################################

    end_dist = (column_d - (2 * column_tf) - ((no_bolts_web - 1) * min_pitch)) / 2
    pitch = math.floor(column_d - (2 * column_tf) - (2 * end_dist_min)) / (no_bolts_web - 1)  # has been changed for detailing purpose

######################################################################################
    # End plate detailing
###########################################################################################
    # end plate height
    if uiObj["Member"]["Connectivity"] == "Extended both ways":
        end_plate_height = column_d + 30
    elif uiObj["Member"]["Connectivity"] == "Flush":
        end_plate_height = column_d + 4 * end_dist_min  # TODO 10 mm is the cover provided beyond flange on either sides

    # end plate width
    end_plate_width = column_B + 25

    # end plate thickness
    if float(min_pitch) >= float(2 * end_dist_min):
        b_eff = (2 * end_dist_min)
    else:
        b_eff = min_pitch

########################################################################################
    # Defining y_max and y_sqr
#########################################################################################

    if uiObj['Member']['Connectivity'] == "Flush":
        y_max = column_d - column_tf - (column_tf / 2) - end_dist
    elif uiObj["Member"]["Connectivity"] == "Extended both ways":
        y_max = column_d - (column_tf / 2) + end_dist

    if uiObj['Member']['Connectivity'] == "Flush":
        y_sqre = 0
        for i in range(no_bolts_web):
            y_sqr = (end_dist + (column_tf / 2) + ((int(i) - 1) * pitch)) ** 2
            y_sqre = y_sqre + y_sqr
            # return y_sqr
    elif uiObj["Member"]["Connectivity"] == "Extended both ways":
        y_sqre = 0
        for i in range(no_bolts_web):
            y_sqr = (end_dist + (column_tf / 2) + ((int(i) - 1) * pitch)) ** 2
            y_sqr = y_sqr + 2 * end_dist + column_tf
            y_sqre = y_sqre + y_sqr

            # return y_sqr

    t_b1 = (factored_axial_load / no_of_bolts) + (factored_moment * y_max / y_sqr)
    t_b2 = t_b3 = (factored_axial_load / no_of_bolts) + (factored_moment * y_max / y_sqr)
    y_1 = column_tf/2 + end_dist_min
    y_2 = y_1 + min_pitch

    if uiObj["Member"]["Connectivity"] == "Flush":
        m_ep = max(0.5 * t_b1 * end_dist_min, t_b2 * end_dist_min)
    elif uiObj["Member"]["Connectivity"] == "Extended both ways":
        m_ep = max(0.5 * t_b1 * end_dist_min, t_b3 * end_dist_min)
    
    gamma_m0 = 1.10


    m_dp = b_eff * end_plate_thickness[1]**2 * column_fy / (4 * gamma_m0)
    
    if m_ep > m_dp:
        design_status = False
        logger.warning(": The moment acting on plate is more than the moment design capacity of the plate.")
        logger.info(": Increase the plate thickness.")
    else:
        pass

    ####################################################################################
    # Calculate bolt capabilities

    if bolt_type == "Friction Grip Bolt":
        bolt_slip_capacity = IS800_2007.cl_10_4_3_bolt_slip_resistance(f_ub=bolt_fu, A_nb=bolt_net_area, n_e=1, mu_f=mu_f,
                                                                       bolt_hole_type=bolt_hole_type)
        bolt_tension_capacity = IS800_2007.cl_10_4_5_friction_bolt_tension_resistance(
            f_ub=bolt_fu, f_yb=bolt_fy, A_sb=bolt_shank_area, A_n=bolt_net_area)
        bolt_bearing_capacity = 0.0
        bolt_shear_capacity = 0.0
        bolt_capacity = bolt_slip_capacity

    else:
        bolt_shear_capacity = IS800_2007.cl_10_3_3_bolt_shear_capacity(
            f_u=bolt_fu, A_nb=bolt_net_area, A_sb=bolt_shank_area, n_n=1, n_s=0)
        bolt_bearing_capacity = IS800_2007.cl_10_3_4_bolt_bearing_capacity(
            f_u=min(column_fu, end_plate_fu), f_ub=bolt_fu, t=sum(end_plate_thickness), d=bolt_dia, e=end_dist_min,
            p=min_pitch, bolt_hole_type=bolt_hole_type)
        bolt_slip_capacity = 0.0
        bolt_capacity = min(bolt_shear_capacity, bolt_bearing_capacity)
        bolt_tension_capacity = IS800_2007.cl_10_3_5_bearing_bolt_tension_resistance(
            f_ub=bolt_fu, f_yb=bolt_fy, A_sb=bolt_shank_area, A_n=bolt_net_area)
    


    ###########################################################################
        # Bolt Checks
    ###########################################################################
    t_b = (factored_axial_load / no_of_bolts) + (factored_moment * y_max / y_sqr)

    if t_b > bolt_tension_capacity:
        design_status = False
        logger.error(": The tension capacity of the connection is less than the bolt tension capacity.")
        logger.warning(": Tension capacity of connection should be more than or equal to bolt tension capacity i.e %s KN." % bolt_tension_capacity)
        logger.info(": Increase diameter of bolt or class of the bolt.")

    if uiObj["Member"]["Connectivity"] == "Flush":
        n_w = no_bolts_web
    elif uiObj["Member"]["Connectivity"] == "Extended both ways":
        n_w = no_bolts_web
    else:
        pass

    v_sb = factored_shear_load / n_w


    if v_sb > bolt_capacity:
        design_status = False
        logger.error(": The Shear capacity of the connection is less than the bolt shear capacity.")
        logger.warning(": Shear capacity of connection should be more than or equal to bolt capacity i.e %s KN." % bolt_capacity)
        logger.info(": Increase diameter of bolt or class of the bolt.")
    else:
        pass

    combined_capacity = (v_sb/bolt_capacity)**2 + (t_b/bolt_tension_capacity)**2
    if float(combined_capacity) > float(1):
        design_status = False
        logger.error(": Load due to combined shear and tension on selected bolt exceeds the limiting value")
        logger.warning(": Higher section is required for the safe design.")
        logger.info(": Re-design the connection using section of higher dimensions.")
    else:
        pass
    
    #########################################################################
     # Stiffener
    ########################################################################
    shear_on_stiff = t_b1
    moment_on_stiff = t_b1 * end_dist_min
    if uiObj['Weld']['Type'] == "Fillet":
        if weld_thickness_flange <= 10:
            n = 15
        elif weld_thickness_flange >10 and weld_thickness_flange<= 14:
            n = 20
        elif weld_thickness_flange > 14:
            n = 25
    a = 196
    b = -28 * n
    c = n ** 2
    d = t_b1 * end_dist_min * 4 * 1.1 / 250

    coeff = [a, b, c, d]

    ans = np.roots(coeff)
    for i in range(len(ans)):
        # if np.isreal(ans[i]):
        t_s = (np.real(ans[i]))

    h_s = 14 * t_s
    if h_s < 100:
        design_status = False
        logger.warning(": Stiffener height is not sufficient for the practical purpose")
        logger.info(": Re-design the connection by increasing the thickness of the stiffener")

    extension = column_d - end_plate_height
    if extension < 50:
        stiffener_width = 50
    else:
        stiffener_width = extension

    stiff_moment = t_b1 * end_dist_min
    stiff_moment_capacity = ((t_s * (14 * t_s - n)**2) / 4) * (column_fy/gamma_m0)

    if stiff_moment > stiff_moment_capacity:
        design_status = False
        logger.error(": Moment due to stiffener is greater than the stiffener moment capacity ")
        logger.info(": Re-design the connection by reducing diameter of bolt or using the higher section")

    stiff_shear = t_b1
    stiff_shear_capacity = t_s * (h_s - n) * (column_fy / gamma_m0)

    if stiff_shear > stiff_shear_capacity:
        design_status = False
        logger.error(": The shear force due to stiffener is greater than the stiffener's shear capacity ")
        logger.info(": Re-design the connection by reducing diameter of bolt or using the higher section")

    if t_s < 6:
        design_status = False
        logger.error(": The minimum thickness of stiffener required is 6mm")
        logger.info(": Re-design the connection by increasing the thickness of stiffener")

    ###########################################################################
    # End of calculation, sample output dictionary
    ###########################################################################

    outputobj = dict()

    outputobj['Bolt'] = {}
    outputobj["Weld"] = {}
    outputobj['Plate'] = {}
    outputobj['Stiffener'] = {}

    ##########   Bolts   #############
    outputobj['Bolt']['status'] = design_status
    outputobj['Bolt']['NumberOfBolts'] = int(no_of_bolts)
    outputobj["Bolt"]["NumberOfRows"] = int(no_bolts_flange)
    outputobj["Bolt"]["ShearBolt"] = float(round(v_sb,3))
    outputobj["Bolt"]["TensionBolt"] = float(round(t_b1,3))

    outputobj["Bolt"]["ShearCapacity"] = float(round(bolt_shear_capacity,3))
    outputobj["Bolt"]["BearingCapacity"] = float(round(bolt_bearing_capacity,3))
    outputobj["Bolt"]["BoltCapacity"] = float(round(bolt_capacity,3))
    outputobj["Bolt"]["SlipCapacity"] = float(round(bolt_slip_capacity,3))
    outputobj["Bolt"]["TensionCapacity"] = float(round(bolt_tension_capacity,3))
    outputobj["Bolt"]["CombinedCapacity"] = float(round(combined_capacity,3))

    outputobj['Bolt']['End'] = float(round(end_dist_min, 3))
    outputobj['Bolt']['Edge'] = float(round(edge_dist_mini, 3))
    outputobj['Bolt']['Pitch'] = float(round(min_pitch, 3))
    outputobj["Bolt"]["Gauge"] = float(round(min_pitch, 3))
    outputobj['Bolt']['EndMax'] = float(round(end_dist_max, 3))
    outputobj['Bolt']['PitchMax'] = float(round(max_pitch, 3))

    ############   Plate    #########################
    outputobj['Plate']['Height'] = float(round(end_plate_height,3))
    outputobj['Plate']['Width'] = float(round(end_plate_width,3))
    outputobj['Plate']['Thickness'] = float(round(end_plate_thickness[1],3))
    outputobj['Plate']['Moment'] = float(round(m_ep,3))
    outputobj['Plate']['MomentCapacity'] = float(round(m_dp,3))

    # #############   Stiffener    ##################
    outputobj['Stiffener']['ShearForce'] = float(round(stiff_shear,3))
    outputobj['Stiffener']['Moment'] = float(round(stiff_moment,3))
    outputobj['Stiffener']['ShearForceCapity'] = float(round(stiff_shear_capacity,3))
    outputobj['Stiffener']['MomentCapacity'] = float(round(stiff_moment_capacity,3))
    outputobj['Stiffener']['Height'] = float(round(h_s,3))
    outputobj['Stiffener']['Width'] = float(round(stiffener_width,3))
    outputobj['Stiffener']['Thickness'] = float(round(t_s,3))
    outputobj['Stiffener']['NotchSize'] = float(round(n,3))

    ################ Weld  ########################
    outputobj["Weld"]["Web"] = 0
    outputobj["Weld"]["Flange"] = 0

#######
    # outputobj = dict()
    #
    # outputobj['Bolt'] = {}
    # outputobj["Weld"] = {}
    # outputobj['Plate'] = {}
    # outputobj['Stiffener'] = {}
    #
    # ##########   Bolts   #############
    # outputobj['Bolt']['status'] = design_status
    # outputobj['Bolt']['NumberOfBolts'] = 0
    # outputobj["Bolt"]["NumberOfRows"] = 0
    # outputobj["Bolt"]["ShearBolt"] = 0
    # outputobj["Bolt"]["TensionBolt"] = 0
    #
    # outputobj["Bolt"]["ShearCapacity"] = 0
    # outputobj["Bolt"]["BearingCapacity"] = 0
    # outputobj["Bolt"]["BoltCapacity"] = 0
    # outputobj["Bolt"]["SlipCapacity"] = 0
    # outputobj["Bolt"]["TensionCapacity"] = 0
    # outputobj["Bolt"]["CombinedCapacity"] = 0
    #
    # outputobj['Bolt']['End'] = 0
    # outputobj['Bolt']['Edge'] = 0
    # outputobj['Bolt']['Pitch'] = 0
    # outputobj["Bolt"]["Gauge"] = 0
    # outputobj['Bolt']['EndMax'] = 0
    # outputobj['Bolt']['PitchMax'] = 0
    #
    # ############   Plate    #########################
    # outputobj['Plate']['Height'] = 0
    # outputobj['Plate']['Width'] = 0
    # outputobj['Plate']['Thickness'] = 0
    # outputobj['Plate']['Moment'] = 0
    # outputobj['Plate']['MomentCapacity'] = 0
    #
    # # #############   Stiffener    ##################
    # outputobj['Stiffener']['ShearForce'] = 0
    # outputobj['Stiffener']['Moment'] = 0
    # outputobj['Stiffener']['ShearForceCapity'] = 0
    # outputobj['Stiffener']['MomentCapacity'] = 0
    # outputobj['Stiffener']['Height'] = 0
    # outputobj['Stiffener']['Width'] = 0
    # outputobj['Stiffener']['Thickness'] = 0
    # outputobj['Stiffener']['NotchSize'] = 0
    #
    # # ################ Weld  ###############
    # outputobj["Weld"]["Web"] = 0
    # outputobj["Weld"]["Flange"] = 0

    ###########################################################################
    # End of Output dictionary
    
    if design_status == True:
        logger.info(": Overall column end plate splice connection design is safe \n")
        logger.debug(" :=========End Of design===========")
    else:
        logger.error(": Design is not safe \n ")
        logger.debug(" :=========End Of design===========")

    return outputobj
