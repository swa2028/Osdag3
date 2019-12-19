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

class ccEndPlate:
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

    def ccEndPlateSplice(self,uiObj):
        global logger
        global design_status
        # module_setup()
        self.design_status = True

        self.connectivity = uiObj["Member"]["Connectivity"]
        self.column_sec = uiObj['Member']['ColumnSection']
        self.column_fu = float(uiObj['Member']['fu (MPa)'])
        self.column_fy = float(uiObj['Member']['fy (MPa)'])
        self.weld_fu = float(uiObj['weld']['fu_overwrite'])
        self.weld_fu_govern = min(self.column_fu, self.weld_fu)  # Mpa  (weld_fu_govern is the governing value of weld strength)

        self.factored_moment = float(uiObj['Load']['Moment (kNm)'])
        self.factored_shear_load = float(uiObj['Load']['ShearForce (kN)'])
        self.factored_axial_load = uiObj['Load']['AxialForce (kN)']
        if self.factored_axial_load == '':
            self.factored_axial_load = 0
        else:
            self.factored_axial_load = float(self.factored_axial_load)

        self.bolt_dia = float(uiObj['Bolt']['Diameter (mm)'])
        self.bolt_type = (uiObj["Bolt"]["Type"])
        self.bolt_type_tension = (uiObj["bolt"]["bolt_type"])
        self.bolt_grade = float(uiObj['Bolt']['Grade'])
        self.bolt_fu = float(uiObj["bolt"]["bolt_fu"])
        self.bolt_fy = float((self.bolt_grade - int(self.bolt_grade)) * self.bolt_fu)
        self.slip_factor = float(uiObj["bolt"]["slip_factor"])
        self.bolt_hole_type = (uiObj["bolt"]["bolt_hole_type"])
        self.bolt_hole_clrnce = float(uiObj["bolt"]["bolt_hole_clrnce"])

        self.mu_f = float(uiObj["bolt"]["slip_factor"])
        self.gamma_mw = float(uiObj["weld"]["safety_factor"])
        self.dp_bolt_hole_type = uiObj["bolt"]["bolt_hole_type"]
        if self.dp_bolt_hole_type == "Over-sized":
            self.bolt_hole_type = 'over_size'
        else:   # "Standard"
            self.bolt_hole_type = 'standard'

        self.dia_hole = self.bolt_dia + int(uiObj["bolt"]["bolt_hole_clrnce"])

        if self.connectivity == "Extended both ways":
            self.endplate_type = "Extended both ways"
        else:
            self.endplate_type = "Flush"

        self.end_plate_thickness = [float(uiObj['Plate']['Thickness (mm)']),float(uiObj['Plate']['Thickness (mm)'])]

        self.end_plate_height = uiObj["Plate"]["Height (mm)"]
        if self.end_plate_height == '':
            self.end_plate_height = 0
        else:
            self.end_plate_height = float(self.end_plate_height)

        self.end_plate_width = uiObj["Plate"]["Width (mm)"]
        if self.end_plate_width == '':
            self.end_plate_width = 0
        else:
            self.end_plate_width = float(self.end_plate_width)

        # TODO implement after excomm review for different grades of plate
        self.end_plate_fu = float(uiObj['Member']['fu (MPa)'])
        self.end_plate_fy = float(uiObj['Member']['fy (MPa)'])

        self.weld_type = str(uiObj["Weld"]["Type"])  # This is - Fillet weld or Groove weld
        self.weld_method = (uiObj["weld"]["typeof_weld"])
        if self.weld_type == "Fillet":
            self.weld_thickness_flange = float(uiObj['Weld']['Flange (mm)'])
            self.weld_thickness_web = float(uiObj['Weld']['Web (mm)'])
        else:
            self.weld_thickness_flange = 0
            self.weld_thickness_web = 0

        if uiObj["detailing"]["typeof_edge"] == "Sheared or hand flame cut":
            self.edge_type = 'hand_flame_cut'
        else:   # "b - Rolled, machine-flame cut, sawn and planed"
            self.edge_type = 'machine_flame_cut'

        self.corrosive_influences = False
        if uiObj['detailing']['is_env_corrosive'] == "Yes":
            self.corrosive_influences = True

        [self.bolt_shank_area, self.bolt_net_area] = IS1367_Part3_2002.bolt_area(self.bolt_dia)


        old_column_section = get_oldcolumncombolist()

        if self.column_sec in old_column_section:
            logger.warning(": You are using a section (in red colour) that is not available in the latest version of IS 808")

        if self.column_fu < 410 or self.column_fy < 230:
            logger.warning(" : You are using a section of grade that is not available in latest version of IS 2062")

        #######################################################################
        # Read input values from Column database

        dictcolumndata = get_columndata(self.column_sec)
        global column_tw
        self.column_tw = float(dictcolumndata["tw"])
        global column_tf
        self.column_tf = float(dictcolumndata["T"])
        self.column_d = float(dictcolumndata["D"])
        self.column_B = float(dictcolumndata["B"])
        self.column_R1 = float(dictcolumndata["R1"])
        self.column_Zz = float(dictcolumndata["Zz"])

        #######################################################################
        # Validation of minimum input moment (Cl. 10.7- 6 and Cl. 8.2.1, IS 800:2007)

        self.M_d = (1.2 * self.column_Zz * 1000 * self.column_fy) / 1.10
        self.moment_minimum = 0.5 * (self.M_d / 1000000)

        if float(self.factored_moment) < float(self.moment_minimum):
            design_status = False
            logger.warning(": The input factored moment (%2.2f kN-m) is less that the minimum design action on the connection (Cl. 10.7-6, IS 800:2007)" % self.factored_moment)
            logger.info(": The connection is designed for %2.2f kN-m (Cl. 10.7, IS 800:2007)" % float(self.moment_minimum))
            self.factored_moment = round(self.moment_minimum, 3)

        #######################################################################
        # Calculation of Bolt strength in MPa
        self.bolt_fu = float(uiObj["bolt"]["bolt_fu"])
        self.bolt_fy = float((self.bolt_grade - int(self.bolt_grade)) * self.bolt_fu)

        #######################################################################
        # Calculation of Spacing

        # Minimum and maximum end distances (mm) [Cl. 10.2.4.2 & Cl. 10.2.4.3, IS 800:2007]
        self.end_dist_min = float(IS800_2007.cl_10_2_4_2_min_edge_end_dist(
            d=self.bolt_dia, bolt_hole_type=self.bolt_hole_type, edge_type=self.edge_type))

        self.end_dist_max = IS800_2007.cl_10_2_4_3_max_edge_dist(plate_thicknesses=self.end_plate_thickness, f_y=self.end_plate_fy,
                                                            corrosive_influences=self.corrosive_influences)

        # Minimum and maximum edge distances (mm) [Cl. 10.2.4.2 & Cl. 10.2.4.3, IS 800:2007]
        self.edge_dist_mini = self.end_dist_min
        self.edge_dist_max = self.end_dist_max

        # min_pitch & max_pitch = Minimum and Maximum pitch distance (mm) [Cl. 10.2.2, IS 800:2007]
        self.min_pitch = float(3.0 * self.bolt_dia)
        self.max_pitch = IS800_2007.cl_10_2_3_1_max_spacing(self.end_plate_thickness)

        # min_gauge & max_gauge = Minimum and Maximum gauge distance (mm) [Cl. 10.2.3.1, IS 800:2007]
        self.gauge_dist_min = self.min_pitch
        self.gauge_dist_max = self.max_pitch
        #######################################################################

        #######################################################################
        # Calculation for number of bolts
        #######################################################################

        self.no_bolts_web = ((self.column_d - (2 * self.column_tf) - (2 * self.end_dist_min)) / self.min_pitch) + 1
        self.no_bolts_web = int(math.floor(self.no_bolts_web ))
        self.end_dist_provided = (self.column_d - (2 * self.column_tf) - ((self.no_bolts_web - 1) * self.min_pitch)) / 2

        if self.no_bolts_web == 1 or self.no_bolts_web < 1:
            design_status = False
            logger.warning(": The bolt diameter selected is larger for the given section.")
            logger.info(": Decrease the bolt diameter or increase the size of section.")

        self.no_bolts_flange = (((self.column_B / 2) - (self.column_tw / 2) - (self.end_dist_provided * 2)) / self.min_pitch)  # excluding the bolt which is common
        self.no_bolts_flange = int(math.floor(self.no_bolts_flange))

        if uiObj["Member"]["Connectivity"] == "Flush":
            self.no_bolts_flange = self.no_bolts_flange
        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.no_bolts_flange = self.no_bolts_flange * 2

        if uiObj["Member"]["Connectivity"] == "Flush":
            self.no_of_bolts = int(2 * self.no_bolts_web + 4 * (self.no_bolts_flange))
        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.no_of_bolts = int(2 * self.no_bolts_web + 4 * (self.no_bolts_flange + 4))

    ######################################################################################
        # End plate detailing
    ###########################################################################################
        # end plate height
        if uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.end_plate_height_min = self.column_d + 2 * self.weld_thickness_flange + 10
        elif uiObj["Member"]["Connectivity"] == "Flush":
            self.end_plate_height_min = self.column_d + 4 * self.end_dist_provided + 2 * self.weld_thickness_flange
            self.end_plate_height_max = self.column_d + 4 * self.end_dist_max + 2 * self.weld_thickness_flange

        if self.end_plate_height != 0:
            if float(self.end_plate_height) <= float(self.column_d):
                design_status = False
                logger.error(": Height of End Plate is less than/or equal to the depth of the Beam ")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % self.end_plate_height_min)
                logger.info(": Increase the Height of End Plate")

            elif float(self.end_plate_height) <= float(self.end_plate_height_min):
                design_status = False
                logger.error(": Height of End Plate is less than the minimum required height")
                logger.warning(": Minimum End Plate height required is %2.2f mm" % self.end_plate_height_min)
                logger.info(": Increase the Height of End Plate")

            if uiObj["Member"]["Connectivity"] == "Extended both ways":
                if self.end_plate_height > self.end_plate_height_max:
                    design_status = False
                    logger.error(": Height of End Plate exceeds the maximum allowed height")
                    logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % self.end_plate_height_max)
                    logger.info(": Decrease the Height of End Plate")

            if uiObj["Member"]["Connectivity"] == "Flush":
                if self.end_plate_height > self.end_plate_height_min:
                    design_status = False
                    logger.warning(": Maximum allowed height of End Plate is %2.2f mm" % self.end_plate_height_min)
                    logger.info(": Decrease the Height of End Plate")

        # end plate width
        self.end_plate_width_min = (self.column_B)
        self.end_plate_width_max = (self.column_B + 25)

        if self.end_plate_width != 0:
            if self.end_plate_width < self.end_plate_width_min:
                design_status = False
                logger.error(": Width of the End Plate is less than the minimum required value ")
                logger.warning(": Minimum End Plate width required is %2.2f mm" % self.end_plate_width_min)
                logger.info(": Increase the width of End Plate")
            if self.end_plate_width > self.end_plate_width_max:
                design_status = False
                logger.error(": Width of the End Plate exceeds the maximum allowed width ")
                logger.warning(": Maximum allowed width of End Plate is %2.2f mm" % self.end_plate_width_max)
                logger.info(": Decrease the width of End Plate")

        # end plate thickness
        if float(self.min_pitch) >= float(2 * self.end_dist_provided):
            self.b_eff = (2 * self.end_dist_provided)
        else:
            self.b_eff = self.min_pitch

    ########################################################################################
        # Defining y_max and y_sqr
    #########################################################################################

        if uiObj['Member']['Connectivity'] == "Flush":
            self.y_max = self.column_d - self.column_tf - (self.column_tf / 2) - self.end_dist_provided
        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.y_max = self.column_d - (self.column_tf / 2) + self.end_dist_provided

        self.y_2 = self.column_d - self.column_tf - (self.column_tf / 2) - self.end_dist_provided - self.min_pitch

        if uiObj['Member']['Connectivity'] == "Flush":
            self.y_sqre = 0
            for i in range(1,(self.no_bolts_web + 1)):
                self.y_sqr = (self.end_dist_provided + (self.column_tf / 2) + ((int(i) - 1) * self.min_pitch)) ** 2
                self.y_sqre = self.y_sqre + self.y_sqr
        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.y_sqre = 0
            for i in range(1,(self.no_bolts_web + 2)):
                if i == self.no_bolts_web + 1:
                    self.y_end = ((self.column_tf / 2) + ((int(i) - 2) * self.min_pitch) + 3 * self.end_dist_provided + self.column_tf) ** 2
                    self.y_sqre = self.y_end + self.y_sqre
                else:
                    self.y_sqr = (self.end_dist_provided + (self.column_tf / 2) + ((int(i) - 1) * self.min_pitch)) ** 2
                    self.y_sqre = self.y_sqre + self.y_sqr

        self.t_b1 = (self.factored_axial_load / self.no_of_bolts) + (self.factored_moment * self.y_max / self.y_sqr)
        self.t_b2 = self.t_b3 = (self.factored_axial_load / self.no_of_bolts) + (self.factored_moment * self.y_2 / self.y_sqr)

        if uiObj["Member"]["Connectivity"] == "Flush":
            self.m_ep = max(0.5 * self.t_b1 * self.end_dist_provided, self.t_b2 * self.end_dist_provided)
        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.m_ep = max(0.5 * self.t_b1 * self.end_dist_provided, self.t_b3 * self.end_dist_provided)

        self.gamma_m0 = 1.10

        self.t_p = math.ceil(math.sqrt((self.m_ep * 4 * self.gamma_m0) / (self.b_eff * self.end_plate_fy)))
        if self.t_p % 2 == 1:
            self.t_p = self.t_p + 1

        if float(self.end_plate_thickness[0]) < float(self.t_p):
            self.end_plate_thickness = self.t_p
            design_status = False
            logger.error(": Chosen end plate thickness is not sufficient")
            logger.warning(": Minimum required thickness of end plate as per the detailing criteria is %2.2f mm " % self.end_plate_thickness)
            logger.info(": Increase the thickness of end plate ")

        self.m_dp = self.b_eff * (self.end_plate_thickness[0])**2 * self.column_fy / (4 * self.gamma_m0)
        if self.m_ep > self.m_dp:
            design_status = False
            logger.warning(": The moment acting on plate is more than the moment design capacity of the plate.")
            logger.info(": Increase the plate thickness.")
        else:
            pass

        ####################################################################################
        # Calculate bolt capabilities

        if self.bolt_type == "Friction Grip Bolt":
            self.bolt_slip_capacity = IS800_2007.cl_10_4_3_bolt_slip_resistance(f_ub=self.bolt_fu, A_nb=self.bolt_net_area, n_e=1, mu_f=self.mu_f,
                                                                           bolt_hole_type=self.bolt_hole_type)
            self.bolt_tension_capacity = IS800_2007.cl_10_4_5_friction_bolt_tension_resistance(
                f_ub=self.bolt_fu, f_yb=self.bolt_fy, A_sb=self.bolt_shank_area, A_n=self.bolt_net_area)
            self.bolt_bearing_capacity = 0.0
            self.bolt_shear_capacity = 0.0
            self.bolt_capacity = self.bolt_slip_capacity

        else:
            self.bolt_shear_capacity = IS800_2007.cl_10_3_3_bolt_shear_capacity(
                f_u=self.bolt_fu, A_nb=self.bolt_net_area, A_sb=self.bolt_shank_area, n_n=1, n_s=0)
            self.bolt_bearing_capacity = IS800_2007.cl_10_3_4_bolt_bearing_capacity(
                f_u=min(self.column_fu, self.end_plate_fu), f_ub=self.bolt_fu, t=sum(self.end_plate_thickness), d=self.bolt_dia, e=self.end_dist_min,
                p=self.min_pitch, bolt_hole_type=self.bolt_hole_type)
            self.bolt_slip_capacity = 0.0
            self.bolt_capacity = min(self.bolt_shear_capacity, self.bolt_bearing_capacity)
            self.bolt_tension_capacity = IS800_2007.cl_10_3_5_bearing_bolt_tension_resistance(
                f_ub=self.bolt_fu, f_yb=self.bolt_fy, A_sb=self.bolt_shank_area, A_n=self.bolt_net_area)

        ###########################################################################
            # Bolt Checks
        ###########################################################################
        self.t_b = (self.factored_axial_load / self.no_of_bolts) + (self.factored_moment * self.y_max / self.y_sqr)

        if self.t_b > self.bolt_tension_capacity:
            design_status = False
            logger.error(": The tension capacity of the connection is less than the bolt tension capacity.")
            logger.warning(": Tension capacity of connection should be more than or equal to bolt tension capacity i.e %s KN." % self.bolt_tension_capacity)
            logger.info(": Increase diameter of bolt or class of the bolt.")

        if uiObj["Member"]["Connectivity"] == "Flush":
            self.n_w = self.no_bolts_web
        elif uiObj["Member"]["Connectivity"] == "Extended both ways":
            self.n_w = self.no_bolts_web
        else:
            pass

        self.v_sb = self.factored_shear_load / self.n_w

        if self.v_sb > self.bolt_capacity:
            design_status = False
            logger.error(": The Shear capacity of the connection is less than the bolt shear capacity.")
            logger.warning(": Shear capacity of connection should be more than or equal to bolt capacity i.e %s KN." % self.bolt_capacity)
            logger.info(": Increase diameter of bolt or class of the bolt.")
        else:
            pass

        # Check for combined tension and shear
        if self.bolt_type == "Friction Grip Bolt":
            self.combined_capacity = IS800_2007.cl_10_4_6_friction_bolt_combined_shear_and_tension(V_sf=self.v_sb, V_df=self.bolt_capacity, T_f=self.t_b, T_df=self.bolt_tension_capacity)
        else:
            self.combined_capacity = IS800_2007.cl_10_3_6_bearing_bolt_combined_shear_and_tension(V_sb=self.v_sb, V_db=self.bolt_capacity, T_b=self.t_b, T_db=self.bolt_tension_capacity)

        # combined_capacity = (v_sb/bolt_capacity)**2 + (t_b/bolt_tension_capacity)**2
        if float(self.combined_capacity) > float(1):
            design_status = False
            logger.error(": Load due to combined shear and tension on selected bolt exceeds the limiting value")
            logger.warning(": Higher section is required for the safe design.")
            logger.info(": Re-design the connection using section of higher dimensions.")
        else:
            pass

        #########################################################################
         # Stiffener
        ########################################################################
        self.shear_on_stiff = self.t_b1
        self.moment_on_stiff = self.t_b1 * self.end_dist_provided
        if uiObj['Weld']['Type'] == "Fillet":
            if self.weld_thickness_flange <= 10:
                self.n = 15
            elif self.weld_thickness_flange >10 and self.weld_thickness_flange <= 14:
                self.n = 20
            elif self.weld_thickness_flange > 14:
                self.n = 25
        a = 196
        b = -28 * self.n
        c = self.n ** 2
        d = -(self.t_b1 * self.end_dist_provided * 4 * self.gamma_m0 / self.column_fy)

        coeff = [a, b, c, d]

        self.t_s = np.roots(coeff)
        # for i in range(len(ans)):
        #     if np.isreal(ans[i]):
        #         t_s = (np.real(ans[i]))
        self.t_s = np.amax(self.t_s)

        self.h_s = 14 * self.t_s
        if self.h_s < 100:
            design_status = False
            logger.warning(": Stiffener height is not sufficient for the practical purpose")
            logger.info(": Re-design the connection by increasing the thickness of the stiffener")

        self.extension = self.column_d - self.end_plate_height
        if self.extension < 50:
            self.stiffener_width = 50
        else:
            self.stiffener_width = self.extension

        self.stiff_moment = self.t_b1 * self.end_dist_min
        self.stiff_moment_capacity = ((self.t_s * (14 * self.t_s - self.n)**2) / 4) * (self.column_fy/self.gamma_m0)

        if self.stiff_moment > self.stiff_moment_capacity:
            design_status = False
            logger.error(": Moment due to stiffener is greater than the stiffener moment capacity ")
            logger.info(": Re-design the connection by reducing diameter of bolt or using the higher section")

        self.stiff_shear = self.t_b1
        self.stiff_shear_capacity = self.t_s * (self.h_s - self.n) * (self.column_fy / self.gamma_m0)

        if self.stiff_shear > self.stiff_shear_capacity:
            design_status = False
            logger.error(": The shear force due to stiffener is greater than the stiffener's shear capacity ")
            logger.info(": Re-design the connection by reducing diameter of bolt or using the higher section")

        if self.t_s < 6:
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
        outputobj['Bolt']['NumberOfBolts'] = int(self.no_of_bolts)
        outputobj["Bolt"]["NumberOfRows"] = int(self.no_bolts_flange)
        outputobj["Bolt"]["ShearBolt"] = float(round(self.v_sb,3))
        outputobj["Bolt"]["TensionBolt"] = float(round(self.t_b1,3))

        outputobj["Bolt"]["ShearCapacity"] = float(round(self.bolt_shear_capacity,3))
        outputobj["Bolt"]["BearingCapacity"] = float(round(self.bolt_bearing_capacity,3))
        outputobj["Bolt"]["BoltCapacity"] = float(round(self.bolt_capacity,3))
        outputobj["Bolt"]["SlipCapacity"] = float(round(self.bolt_slip_capacity,3))
        outputobj["Bolt"]["TensionCapacity"] = float(round(self.bolt_tension_capacity,3))
        outputobj["Bolt"]["CombinedCapacity"] = float(round(self.combined_capacity,3))

        outputobj['Bolt']['End'] = float(round(self.end_dist_provided, 3))
        outputobj['Bolt']['Edge'] = float(round(self.end_dist_provided, 3))
        outputobj['Bolt']['Pitch'] = float(round(self.min_pitch, 3))
        outputobj["Bolt"]["Gauge"] = float(round(self.min_pitch, 3))
        outputobj['Bolt']['EndMax'] = float(round(self.end_dist_max, 3))
        outputobj['Bolt']['PitchMax'] = float(round(self.max_pitch, 3))

        ############   Plate    #########################
        outputobj['Plate']['Height'] = float(round(self.end_plate_height,3))
        outputobj['Plate']['Width'] = float(round(self.end_plate_width,3))
        outputobj['Plate']['Thickness'] = float(round(self.end_plate_thickness[1],3))
        outputobj['Plate']['Moment'] = float(round(self.m_ep,3))
        outputobj['Plate']['MomentCapacity'] = float(round(self.m_dp,3))

        # #############   Stiffener    ##################
        outputobj['Stiffener']['ShearForce'] = float(round(self.stiff_shear,3))
        outputobj['Stiffener']['Moment'] = float(round(self.stiff_moment,3))
        outputobj['Stiffener']['ShearForceCapity'] = float(round(self.stiff_shear_capacity,3))
        outputobj['Stiffener']['MomentCapacity'] = float(round(self.stiff_moment_capacity,3))
        outputobj['Stiffener']['Height'] = float(round(self.h_s,3))
        outputobj['Stiffener']['Width'] = float(round(self.stiffener_width,3))
        outputobj['Stiffener']['Thickness'] = float(round(self.t_s,3))
        outputobj['Stiffener']['NotchSize'] = float(round(self.n,3))

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

        if self.design_status == True:
            logger.info(": Overall column end plate splice connection design is safe \n")
            logger.debug(" :=========End Of design===========")
        else:
            logger.error(": Design is not safe \n ")
            logger.debug(" :=========End Of design===========")

        return outputobj
