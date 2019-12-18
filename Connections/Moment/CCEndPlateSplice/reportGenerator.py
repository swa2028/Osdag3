"""
Created on April, 2019
@author: Yash Lokhande
"""

# from __builtin__ import str
import time
import math
import os
import pickle
from Connections.connection_calculations import ConnectionCalculations
from Connections.Moment.CCEndPlateSplice.ccEndPlateSpliceCalc import ccEndPlate
# from Connections.Moment.CCEndPlateSplice.column_end_plate_main import DesignPreference
#####################  Start of report  #################################################
class A:
    def __init__(self,outObj, uiObj, dictcolumndata, filename, reportsummary, folder):
        '''
        This function writes the html file and that html is converted into pdf in main file
        '''
        self.filename = filename
        self.myfile = open(filename, "w")
        self.myfile.write(self.t('! DOCTYPE html')) # Start of html
        self.myfile.write(self.t('html'))
        self.myfile.write(self.t('head'))
        self.myfile.write(self.t('link type="text/css" rel="stylesheet" '))

        self.myfile.write(self.t('style'))
        self.myfile.write('table{width= 100%; border-collapse:collapse; border:1px solid black collapse}')
    #      Avoids the splitting of the table on next page
        self.myfile.write('table{ page-break-inside:auto }')
        self.myfile.write('tr{ page-break-inside:avoid; page-break-after:auto }')
    #      Provides 3px padding for th, tr and td
        self.myfile.write('th,td,tr {padding:3px}')
    #     Provides light green background color(#D5DF93), font-weight bold, font-size 20 and font-family
        self.myfile.write('td.detail{background-color:#D5DF93; font-size:20; font-family:Helvetica, Arial, Sans Serif; font-weight:bold}')
    #     Provides font-weight bold, font-size 20 and font-family
        self.myfile.write('td.detail1{font-size:20; font-family:Helvetica, Arial, Sans Serif; font-weight:bold}')
    #     Provides font-size 20 and font-family
        self.myfile.write('td.detail2{font-size:20; font-family:Helvetica, Arial, Sans Serif}')
    #     Provides dark green background color(#8FAC3A), font-weight bold, font-size 20 and font-family
        self.myfile.write('td.header0{background-color:#8fac3a; font-size:20; font-family:Helvetica, Arial, Sans Serif; font-weight:bold}')
    #     Provides grey background color(#E6E6E6), font-weight bold, font-size 20 and font-family
        self.myfile.write('td.header1{background-color:#E6E6E6; font-size:20; font-family:Helvetica, Arial, Sans Serif; font-weight:bold}')
    #     Provides only font-size 20 and width of the images box
        self.myfile.write('td.header2{font-size:20; width:100%}')
        self.myfile.write(self.t('/style'))

        self.myfile.write(self.t('/head'))
        self.myfile.write(self.t('body{font-size:25; font-family:Helvetica, Arial, Sans Serif;}'))

        s = ccEndPlate()
        ccEndPlate.ccEndPlateSplice(s,uiObj)
        # s.end_plate_thickness


    #####################   Additional comments input  #################################################
        self.addtionalcomments = str(reportsummary['AdditionalComments'])

    #########################  Calling the values from input, output and ui dict   #############################################
    # Extended End Plate Data

        # Section properties from beam data dict
        # self.beam_tw = float(dictbeamdata["tw"])
        # self.beam_tf = float(dictbeamdata["T"])
        # self.beam_d = float(dictbeamdata["D"])
        # self.beam_B = float(dictbeamdata["B"])
        # self.beam_R1 = float(dictbeamdata["R1"])
        #
        # # Data from Input dock
        # self.connectivity = str(uiObj['Member']['Connectivity'])
        # self.beam_sec = uiObj['Member']['BeamSection']
        # self.beam_fu = str(float(uiObj['Member']['fu (MPa)']))
        # # beam_fy = str(float(uiObj['Member']['fy (MPa)']))
        # # weld_fu_govern = str(outObj['Weld']['WeldFuGovern'])
        # self.column_sec = uiObj['Member']['ColumnSection']
        # self.column_fu = str(float(uiObj['Member']['fu (MPa)']))
        # self.factored_moment = str(float(uiObj['Load']['Moment (kNm)']))
        # self.factored_shear_load = str(float(uiObj['Load']['ShearForce (kN)']))
        # self.factored_axial_load = str(float(uiObj['Load']['AxialForce (kN)']))
        # self.bolt_dia = str(int(uiObj['Bolt']['Diameter (mm)']))
        # self.bolt_type = uiObj["Bolt"]["Type"]
        # self.bolt_grade = str(float(uiObj['Bolt']['Grade']))
        # self.endplate_type = str(uiObj['Member']['EndPlate_type'])
        # self.weld_method =  str((uiObj['Weld']['Method']))
        #
        # self.bolt_fu = str((int(float(self.bolt_grade)) * 100))
        # self.net_area_thread = {12: str(84.3), 16: str(157), 20: str(245), 22: str(303), 24: str(353), 27: str(459), 30: str(561), 36: str(817)}[int(self.bolt_dia)]
        #
        # # Design Preferences
        #
        # self.bolt_hole_clrnce = str(float(uiObj["bolt"]["bolt_hole_clrnce"]))
        # self.bolt_hole_type = str(uiObj["bolt"]["bolt_hole_type"])
        # self.bolt_grade_fu = str(float(uiObj["bolt"]["bolt_fu"]))
        # self.slip_factor = str(float(uiObj["bolt"]["slip_factor"]))
        # self. bolt_Type = str(uiObj['bolt']['bolt_type'])  # for pre-tensioned/ non- pretensioned bolts
        #
        # self.typeof_weld = str(uiObj["weld"]["typeof_weld"])
        # fu_overwrite = str(float(uiObj["weld"]["fu_overwrite"]))
        #
        # self.typeof_edge = str(uiObj["detailing"]["typeof_edge"])
        # self.min_edgend_dist = str(float(uiObj["detailing"]["min_edgend_dist"]))  # factor: 1.7 or 1.5 depending on type of edge, IS 800- Cl 10.2.4.2
        # # gap = float(uiObj["detailing"]["gap"])
        # self.corrosive = str(uiObj["detailing"]["is_env_corrosive"])
        # design_method = str(uiObj["design"]["design_method"])
        #
        # # Data from output dict
        # # Bolt
        # self.number_of_bolts = str(int(outObj['Bolt']['NumberOfBolts']))
        # if float(self.number_of_bolts) <= 20:
        #     #no_rows = str(int(outObj['Bolt']['NumberOfRows']))
        #     #bolts_per_column = str(outObj['Bolt']['BoltsPerColumn'])
        #     self.cross_centre_gauge = str(outObj['Bolt']['CrossCentreGauge'])
        # else:
        #     #no_rows = str(0)
        #     #bolts_per_column = str(0)
        #     self.cross_centre_gauge = str(outObj['Bolt']['CrossCentreGauge'])
        #
        # self.end_distance = str(int(float(outObj['Bolt']['End'])))
        # self.edge_distance = str(int(float(outObj['Bolt']['Edge'])))
        # # gauge_distance = str(int(float(outObj['Bolt']['Gauge'])))
        # self.l_v = str(int(float(outObj['Bolt']['Lv'])))
        # self.pitch_dist = str(int(float(outObj['Bolt']['Pitch'])))
        # self.pitch_dist_min = str(int(float(outObj['Bolt']['PitchMini'])))
        # self.pitch_dist_max = str(int(float(outObj['Bolt']['PitchMax'])))
        #
        # self.slip_capacity = str(float(outObj["Bolt"]["SlipCapacity"]))
        # self.shear_capacity = str(float(outObj["Bolt"]["ShearCapacity"]))
        # self.bearing_capacity = str(float(outObj["Bolt"]["BearingCapacity"]))
        # self.bolt_capacity = str(float(outObj["Bolt"]["BoltCapacity"]))
        # self.bolt_tension_capacity = str(float(outObj["Bolt"]["TensionCapacity"]))
        # self.tension_in_bolt = str(float(outObj["Bolt"]["TensionBolt"]))
        # self.combined_capacity = str(float(outObj["Bolt"]["CombinedCapacity"]))
        # self.moment_tension = str(float(outObj["Bolt"]["TensionMoment"]))
        # self.axial_tension = str(float(outObj["Bolt"]["TensionAxial"]))
        # self.prying_force = str(float(outObj["Bolt"]["TensionPrying"]))
        # self.plate_thk = str(outObj['Plate']['Thickness'])  # Sum of plate thickness experiencing bearing in same direction
        #
        # if float(self.number_of_bolts) <= 20:
        #     if self.bolt_type == "Friction Grip Bolt":
        #         self.Vsf = str(float(outObj['Bolt']['ShearBolt']))
        #         self.Vdf = str(float(outObj['Bolt']['BoltCapacity']))
        #         self.Tf = str(float(outObj['Bolt']['TensionBolt']))
        #         self.Tdf = str(float(outObj['Bolt']['TensionCapacity']))
        #     else:
        #         self.Vsb = str(float(outObj['Bolt']['ShearBolt']))
        #         self.Vdb = str(float(outObj['Bolt']['BoltCapacity']))
        #         self.Tb = str(float(outObj['Bolt']['TensionBolt']))
        #         self.Tdb = str(float(outObj['Bolt']['TensionCapacity']))
        #
        #     combinedcapacity = str(float(outObj['Bolt']['CombinedCapacity']))
        # else:
        #     if self.bolt_type == "Friction Grip Bolt":
        #         self.Vsf = str(float(outObj['Bolt']['ShearBolt']))
        #         self.Vdf = str(float(outObj['Bolt']['BoltCapacity']))
        #         self.Tf = str(float(outObj['Bolt']['TensionBolt']))
        #         self.Tdf = str(float(outObj['Bolt']['TensionCapacity']))
        #     else:
        #         self.Vsb = str(float(outObj['Bolt']['ShearBolt']))
        #         self.Vdb = str(float(outObj['Bolt']['BoltCapacity']))
        #         self.Tb = str(float(outObj['Bolt']['TensionBolt']))
        #         self.Tdb = str(float(outObj['Bolt']['TensionCapacity']))
        #
        #     combinedcapacity = str(0)
        #
        # self.pitch_mini = str(int(float(outObj['Bolt']['PitchMini'])))
        # self.pitch_max = str(outObj['Bolt']['PitchMax'])
        # self.end_mini = str(outObj['Bolt']['EndMini'])
        # self.end_max = str(outObj['Bolt']['EndMax'])
        # self.edge_mini = str(self.end_mini)
        # self.edge_max = str(self.end_max)
        # self.dia_hole = str(int(outObj['Bolt']['DiaHole']))
        #
        # # Stiffener and Continuity plate
        # self.cont_plate_tens_length = str(float(outObj['ContPlateTens']['Length']))
        # self.cont_plate_tens_width = str(float(outObj['ContPlateTens']['Width']))
        # self.cont_plate_tens_thk = str(float(outObj['ContPlateTens']['Thickness']))
        # cont_plate_tens_thk_min = str(float(outObj['ContPlateTens']['ThicknessMin']))
        # self.cont_plate_tens_weld = str(float(outObj['ContPlateTens']['Weld']))
        #
        # self.cont_plate_comp_length = str(float(outObj['ContPlateComp']['Length']))
        # self.cont_plate_comp_width = str(float(outObj['ContPlateComp']['Width']))
        # self.cont_plate_comp_thk = str(float(outObj['ContPlateComp']['Thickness']))
        # self.cont_plate_comp_thk_min = str(float(outObj['ContPlateComp']['ThicknessMin']))
        # self.cont_plate_comp_weld = str(float(outObj['ContPlateComp']['Weld']))
        #
        # self.st_length = str(float(outObj['Stiffener']['Length']))
        # self.st_height = str(float(outObj['Stiffener']['Height']))
        # self.st_thk = str(float(outObj['Stiffener']['Thickness']))
        # self.st_notch_bottom = str(float(outObj['Stiffener']['NotchBottom']))
        # self.st_notch_top = str(float(outObj['Stiffener']['NotchTop']))
        # self.st_weld = str(float(outObj['Stiffener']['Weld']))
        #
        # # Plate
        # self.plate_tk_min = str(float(outObj['Plate']['ThickRequired']))
        # self.end_plate_thickness = str(float(outObj['Plate']['Thickness']))
        # # M_p = str(float(outObj['Plate']['Mp']))
        # self.plate_height = str(float(outObj['Plate']['Height']))
        # self.plate_width = str(float(outObj['Plate']['Width']))
        # toe_of_weld_moment = str(float(outObj['Plate']['Moment']))
        # self.beam_B = str(float(outObj['Plate']['be']))
        # self.end_plate_fy = str(float(outObj['Plate']['fy']))
        # self.bf = str(float(outObj['Plate']['WidthMin']))
        # # plate_moment_demand = str(float(outObj['Plate']['MomentDemand']))
        # # plate_moment_capacity = str(float(outObj['Plate']['MomentCapacity']))
        #
        # # Weld
        # if self.weld_method == "Fillet Weld":
        #     if float(self.number_of_bolts) <= 20:
        #         self.flange_weld_size_min = str(float(outObj["Weld"]["FlangeSizeMin"]))
        #         self.flange_weld_size_max = str(float(outObj["Weld"]["FlangeSizeMax"]))
        #         flange_weld_throat_size = str(float(outObj["Weld"]["FlangeThroat"]))
        #         self.flange_weld_size_provd = str(float(uiObj["Weld"]["Flange (mm)"]))
        #         self.flange_weld_stress = str(float(outObj["Weld"]["FlangeStress"]))
        #         self.flange_weld_strength = str(float(outObj["Weld"]["FlangeStrength"]))
        #         self.flange_weld_effective_length_top = str(float(outObj["Weld"]["FlangeLengthTop"]))
        #         self.flange_weld_effective_length_bottom = str(float(outObj["Weld"]["FlangeLengthBottom"]))
        #         self.web_weld_stress = str(float(outObj["Weld"]["WebStress"]))
        #         self.web_weld_strength = str(float(outObj["Weld"]["WebStrength"]))
        #         self.web_weld_size_min = str(float(outObj["Weld"]["WebSizeMin"]))
        #         self.web_weld_size_max = str(float(outObj["Weld"]["WebSizeMax"]))
        #         web_weld_throat_size = str(float(outObj["Weld"]["WebThroat"]))
        #         self.web_weld_size_provd = str(float(uiObj["Weld"]["Web (mm)"]))
        #         self.web_weld_effective_length = str(float(outObj["Weld"]["WebLength"]))
        # else:
        #     self.weld_size = str(float(outObj["Weld"]["Size"]))
        #     self.groove_weld_size_flange = str(float(outObj["Weld"]["FlangeSize"]))
        #     self.groove_weld_size_web = str(float(outObj["Weld"]["WebSize"]))
        #
        # # Calling pitch distance values from Output dict of calc file
        # if self.endplate_type == 'Flush end plate':
        #     if float(self.number_of_bolts) == float(4):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #
        #     elif float(self.number_of_bolts) == float(8):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #
        #     elif float(self.number_of_bolts) == float(12):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #         self.pitch45 = str(float(outObj['Bolt']['Pitch45']))
        #         self.pitch56 = str(float(outObj['Bolt']['Pitch56']))
        #
        # elif self.endplate_type == 'Extended one way':
        #
        #     if float(self.number_of_bolts) == float(6):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #
        #     elif float(self.number_of_bolts) == float(8):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #
        #     elif float(self.number_of_bolts) == float(10):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #         self.pitch45 = str(float(outObj['Bolt']['Pitch45']))
        #
        #     elif float(self.number_of_bolts) == float(12):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #         self.pitch45 = str(float(outObj['Bolt']['Pitch45']))
        #         self.pitch56 = str(float(outObj['Bolt']['Pitch56']))
        #
        # else:  # endplate_type == 'both_way':
        #     if float(self.number_of_bolts) == float(8):
        #         self.pitch = str(float(outObj['Bolt']['Pitch']))
        #     elif float(self.number_of_bolts) == float(12):
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #         self.pitch45 = str(float(outObj['Bolt']['Pitch45']))
        #     elif float(self.number_of_bolts) == float(16):
        #         self.pitch23 = str(float(outObj['Bolt']['Pitch23']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #         self.pitch45 = str(float(outObj['Bolt']['Pitch45']))
        #         self.pitch56 = str(float(outObj['Bolt']['Pitch56']))
        #         self.pitch67 = str(float(outObj['Bolt']['Pitch67']))
        #     elif float(self.number_of_bolts) == float(20):
        #         self.pitch12 = str(float(outObj['Bolt']['Pitch12']))
        #         self.pitch34 = str(float(outObj['Bolt']['Pitch34']))
        #         self.pitch45 = str(float(outObj['Bolt']['Pitch45']))
        #         self.pitch56 = str(float(outObj['Bolt']['Pitch56']))
        #         self.pitch67 = str(float(outObj['Bolt']['Pitch67']))
        #         self.pitch78 = str(float(outObj['Bolt']['Pitch78']))
        #         self.pitch910 = str(float(outObj['Bolt']['Pitch910']))
        #
        # # End Plate
        self.plateDimension = str(s.end_plate_height) + " X " + str(s.end_plate_width) + " X " + str(s.end_plate_thickness)
        # self.status = str(outObj['Bolt']['status'])
        #
        # # Calls from connection calculations file
        # self.k_h = str(float(ConnectionCalculations.calculate_k_h(self.bolt_hole_type)))
        # self.F_0 = str(float(ConnectionCalculations.proof_load_F_0(self.bolt_dia, self.bolt_fu)))

        #######################  Header of the pdf fetched from dialogbox   ########################################

        c = (self.design_summary(reportsummary))
        rstr = (c)
        print(rstr)

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # Page 1 & 2 of report
        # Design Conclusion
        rstr += self.t('table border-collapse= "collapse" border="1px solid black" width= 100% ')

        row = [0, 'Design Conclusion', "IS800:2007/Limit state design"]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="header0"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        if s.design_status == 'True':
            row = [1, "Column to Column End Plate Connection", "<p align=left style=color:green><b>Pass</b></p>"]
        else:
            row = [1, "Column to Column End Plate Connection", "<p align=left style=color:red><b>Fail</b></p>"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail1 "') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail1"') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        # row = [0, "Extended End Plate", " "]
        # rstr += self.t('tr')
        # rstr += self.t('td colspan="2" class="header0"') + self.space(row[0]) + row[1] + self.t('/td')
        # rstr += self.t('/tr')

        row = [0, "Connection Properties", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [0, "Connection ", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Connection Type", "Moment Connection"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        # TODO: should we add Single Extended End Plate
        # row = [1, "Connection Title", " Single Fin Plate"]
        row = [1, "Connection Title", "Extended End Plate"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        if s.endplate_type == "Extended both ways":
            row = [1, "End plate type", "Extended both ways"]
        else:
            row = [1,"End plate type", "Flush End Type"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [0, "Connection Category ", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Connectivity", "Column to Column"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Column to end plate Connection", "Welded"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "End Plate to End Plate Connection", "Bolted"]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [0, "Loading Details ", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Bending Moment (kNm)", str(s.factored_moment)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Shear Force (kN)", str(s.factored_shear_load)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Axial Force (kN)", str(s.factored_axial_load)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [0, "Components ", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Column Section", str(s.column_sec)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Grade of Steel", "Fe " + str(s.column_fu)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        # TODO: Check with sir weather to add below lines (Danish)
        # row = [2, "Hole", bolt_hole_type]
        # rstr += self.t('tr')
        # rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        # rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        # rstr += self.t('/tr')

        row = [1, "Plate Section", self.plateDimension]
        rstr += self.t('tr')
        rstr += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Thickness (t) (mm)", str(s.end_plate_thickness)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Width (mm)", str(s.end_plate_width)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Depth (mm)", str(s.end_plate_height)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Clearance holes for fasteners", str(s.bolt_hole_type)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [1, "Weld ", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Type", uiObj["Weld"]["Type"]]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        if s.weld_type == "Flush":
            row = [2, "Weld at Flange (mm)", uiObj['Weld']['Flange (mm)']]
            rstr += self.t('tr')
            rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
            rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
            rstr += self.t('/tr')

            row = [2, "Weld at Web (mm)", uiObj['Weld']['Web (mm)']]
            rstr += self.t('tr')
            rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
            rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
            rstr += self.t('/tr')
        else:
            pass

        row = [1, "Bolts ", " "]
        rstr += self.t('tr')
        rstr += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Type", str(s.bolt_type)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Property Class", str(s.bolt_grade)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Diameter (d) (mm)", str(s.bolt_dia)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        # bolt_hole_dia = float(s.bolt_dia) + float(s.bolt_hole_clrnce)
        # bolt_hole_dia_str = str(float(bolt_hole_dia))
        row = [2, "Hole diameter (<i>d</i><sub>o</sub>) (mm)", str(s.dia_hole)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2"') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Number of Bolts (n)", str(s.no_of_bolts)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Number of Bolts along web", str(s.no_bolts_web)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Number of Bolts along flange", str(s.no_bolts_flange)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "End Distance (e)(mm)", str(s.end_dist_provided)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2"') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Edge Distance (<i>e</i><sup>'</sup>) (mm)", str(s.end_dist_provided)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        row = [2, "Pitch Distance (p) (mm)", str(s.min_pitch)]
        rstr += self.t('tr')
        rstr += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td class="detail2 "') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        # page break (Below three lines are for page break)
        rstr += self.t('/table')
        rstr += self.t('h1 style="page-break-before:always"')
        rstr += self.t('/h1')

    #&&&&&&&&&&&&&&&&&&&&&&&  Start of page 3 (Design Preferences)  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

        d = (self.design_summary(reportsummary))
        print(d)

        d += self.t('table width = 100% border-collapse= "collapse" border="1px solid black"')
        row = [0, "Design Preferences", " "]
        d += self.t('tr')
        d += self.t('td colspan="4" class="detail"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('/tr')

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& Bolt &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        row = [0, "Bolt ", " "]
        d += self.t('tr')
        d += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Hole Type", str(s.bolt_hole_type)]
        d += self.t('tr')
        d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Hole Clearance (mm)", str(s.bolt_hole_clrnce)]
        d += self.t('tr')
        d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Ultimate Strength (<i>f</i><sub>u</sub>) (MPa)", str(s.bolt_fu)]
        d += self.t('tr')
        d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        if s.bolt_type == "Friction Grip Bolt":
            row = [1, "Slip factor", str(s.slip_factor)]
        else:
            row = [1, "Slip factor", "N/A"]
        d += self.t('tr')
        d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        if s.bolt_type_tension == "Pre-tensioned":
            row = [1, "Beta (&#946;)(pre-tensioned bolt)", str(1)]
        else:
            row = [1, "Beta (&#946;)(non pre-tensioned)", str(2)]
        d += self.t('tr')
        d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& Weld &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        row = [0, "Weld ", " "]
        d += self.t('tr')
        d += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Type of Weld", str(s.weld_method)]
        d += self.t('tr')
        d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        # row = [1, "Material Grade (MPa) (overwrite)", fu_overwrite]
        # d += self.t('tr')
        # d += self.t('td class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        # d += self.t('td class="detail2"') + row[2] + self.t('/td')
        # d += self.t('/tr')

        # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& Detailing &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
        row = [0, "Detailing ", " "]
        d += self.t('tr')
        d += self.t('td colspan="2" class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('/tr')

        if uiObj["detailing"]["typeof_edge"] == "Sheared or hand flame cut":
            row = [1, "Type of Edges", "Sheared or hand flame cut"]
        else:
            row = [1, "Type of Edges", "Rolled, machine-flame cut, sawn and planed"]

        d += self.t('tr')
        d += self.t('td clospan="2" class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Minimum Edge-End Distance", str(s.end_dist_min) ]
        d += self.t('tr')
        d += self.t('td clospan="2" class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Edge-End Distance Provided", str(s.end_dist_provided)]
        d += self.t('tr')
        d += self.t('td clospan="2" class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

        row = [1, "Are members exposed to corrosive influences?", str(s.corrosive_influences)]
        d += self.t('tr')
        d += self.t('td clospan="2" class="detail2"') + self.space(row[0]) + row[1] + self.t('/td')
        d += self.t('td class="detail2"') + row[2] + self.t('/td')
        d += self.t('/tr')

       # Page break
        d += self.t('/table')
        d += self.t('h1 style="page-break-before:always"')
        d += self.t('/h1')

        # &&&&&&&&&&&&&&&&&&&&&&&  Start of page 4 (Checks)  &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
    #     e = (self.design_summary(reportsummary))
    #     print(e)
    #
    #     e += self.t('table border-collapse= "collapse" border="1px solid black" width=100%')
    #     row = [0, "Design Check", " "]
    #     e += self.t('tr')
    #     e += self.t('td colspan="4" scope="colgroup" class="detail"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Check", "Required", "Provided", "Remark"]
    #     e += self.t('td colspan="1" class="header1" scope="col" column-width: 120px') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td colspan="1" class="header1" scope="col" column-width: 120px') + row[2] + self.t('/td')
    #     e += self.t('td colspan="1" class="header1" scope="col" column-width: 120px') + row[3] + self.t('/td')
    #     e += self.t('td colspan="1" class="header1" scope="col" column-width: 120px') + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # # Check for tension in critical bolt
    #     # if float(number_of_bolts) <= float(20):
    #     #     row = [0, "Tension in critical bolt (kN)", " Tension in bolt due to external factored moment + Prying force = " + tension_critical + "+" + prying_force + " = " + str(float(tension_critical) + float(prying_force)) + " <br> [cl. 10.4.7] ", " ", ""]
    #     # else:
    #     #     row = [0, "Tension in critical bolt (kN)",
    #     #            " Tension in bolt due to external factored moment + Prying force = Cannot compute" " <br> [cl. 10.4.7] ", " ", ""]
    #     #
    #     # e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     # e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     # e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     # e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     # e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Bolt Checks", " "]
    #     e += self.t('td colspan="4" class="detail" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    # # Check for shear capacity
    #     e += self.t('tr')
    #     self.required_shear_force = str(float(self.factored_shear_load) / float(self.number_of_bolts))
    #     self.const = str(round(math.pi / 4 * 0.78, 4))
    #     self.n_e = str(1)
    #     self.n_n = str(1)
    #
    #     if self.bolt_type == "Bearing Bolt":
    #         if float(self.required_shear_force) > float(self.shear_capacity):
    #             row = [0, "Bolt shear capacity (kN)",
    #                    "Factored shear force / Number of bolts = " + self.factored_shear_load + " / " + self.number_of_bolts + " = "
    #                    + str(round(float(self.required_shear_force), 3)),
    #                    "<i>V</i><sub>dsb</sub> = (" + self.bolt_fu + "*" + self.n_n + "*" + self.const + "*" + self.bolt_dia + "*" + self.bolt_dia +
    #                    ")/(&#8730;3*1.25) = " + self.shear_capacity + "<br> [cl. 10.3.3]",
    #                    " <p align=left style=color:red><b>Fail</b></p> "]
    #         else:
    #             row = [0, "Bolt shear capacity (kN)", "Factored shear force / Number of bolts = " + self.factored_shear_load + " / " + self.number_of_bolts + " = "
    #                    + str(round(float(self.required_shear_force), 3)), "<i>V</i><sub>dsb</sub> = (" + self.bolt_fu + "*" + self.n_n + "*" + self.const + "*" + self.bolt_dia + "*" + self.bolt_dia +
    #             ")/(&#8730;3*1.25) = " + self.shear_capacity + "<br> [cl. 10.3.3]", " <p align=left style=color:green><b>Pass</b></p> "]
    #     else:
    #         if float(self.required_shear_force) > float(self.slip_capacity):
    #             row = [0, "Bolt slip resistance (kN)", "Factored shear force / Number of bolts = " + self.factored_shear_load + " / " + self.number_of_bolts + " = "
    #                    + str(round(float(self.required_shear_force), 3)), "<i>V</i><sub>dsf</sub> = (" + self.slip_factor + "*" + self.n_e + "*" + self.k_h + "*" + self.F_0 +
    #                 ") / 1.25 = " + self.slip_capacity + "<br> [cl. 10.4.3]", " <p align=left style=color:red><b>Fail</b></p> "]
    #         else:
    #             row = [0, "Bolt slip resistance (kN)",
    #                    "Factored shear force / Number of bolts = " + self.factored_shear_load + " / " + self.number_of_bolts + " = "
    #                    + str(round(float(self.required_shear_force), 3)),
    #                    "<i>V</i><sub>dsf</sub> = (" + self.slip_factor + "*" + self.n_e + "*" + self.k_h + "*" + self.F_0 +
    #                    ") / 1.25 = " + self.slip_capacity + "<br> [cl. 10.4.3]",
    #                    " <p align=left style=color:green><b>Pass</b></p> "]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Check for bearing capacity
    #     e += self.t('tr')
    #     if self.bolt_type == "Friction Grip Bolt" :
    #         row = [0, "Bolt bearing capacity (kN)", "N/A", "N/A", ""]
    #     else:
    #         row = [0, "Bolt bearing capacity (kN)", "", " <i>V</i><sub>dpb</sub> = (2.5 * <i>k</i><sub>b</sub> * d * t * <i>f</i><sub>u</sub>  = " + self.bearing_capacity + "<br> [cl. 10.3.4]", ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Check for bolt capacity
    #     e += self.t('tr')
    #     if self.bolt_type == "Bearing Bolt":
    #         row = [0, "Bolt capacity (kN)","min(Shear Capacity, Bearing Capacity) =" + " min (" + self.shear_capacity + ", " + self.bearing_capacity + ") ", self.bolt_capacity, ""]
    #     else:
    #         row = [0, "Bolt capacity (kN)","", "Bolt slip resistance ="+ self.bolt_capacity, ""]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Check for Tension capacity of bolt
    #     # TODO: Check for bearing bolt type (Danish)
    #     e += self.t('tr')
    #
    #     if float(self.number_of_bolts) <= float(20):
    #         if float(self.tension_in_bolt) > float(self.bolt_tension_capacity):
    #             row = [0, "Tension capacity of bolt (kN)", "&#8805; Tension in bolt due to external moment + external axial load + prying force ="+ str(float(self.moment_tension))+"+" + str(float(self.axial_tension))+"+" + str(float(self.prying_force)) + "=" +  str(float(self.tension_in_bolt)),
    #                    " Tension capacity = "  "(0.9" "*" + self.bolt_fu + "*" + self.net_area_thread + ") / (1.25*1000) = "
    #                    + bolt_tension_capacity + " <br> [cl. 10.4.5]", " <p align=left style=color:red><b>Fail</b></p> "]
    #         else:
    #
    #             row = [0, "Tension capacity of bolt (kN)", "&#8805; Tension in bolt due to external moment + external axial load + prying force ="+ str(float(self.moment_tension))+"+" + str(float(self.axial_tension))+"+" + str(float(self.prying_force)) + "=" + str(float(self.tension_in_bolt)),
    #                    " Tension capacity = "  "(0.9" "*" + self.bolt_fu + "*" + self.net_area_thread + ") / " "(1.25*1000) = "
    #                    + self.bolt_tension_capacity + " <br> [cl. 10.4.5]", " <p align=left style=color:green><b>Pass</b></p> "]
    #     else:
    #         row = [0, "Tension capacity of critical bolt (kN)", "Cannot compute",
    #                " Tension capacity = "  "(0.9" "*" + self.bolt_fu + "*" + self.net_area_thread + ") / (1.25*1000) = "
    #                + self.bolt_tension_capacity + " <br> [cl. 10.4.5]", " <p align=left style=color:red><b>Fail</b></p> "]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Check for Combined capacity
    #     e += self.t('tr')
    #     if float(self.number_of_bolts) <= float(20):
    #         if self.bolt_type == "Friction Grip Bolt":
    #             if float(self.combined_capacity) > float(1):
    #                 row = [0, "Combined shear and tension capacity of bolt", "&#8804; 1.0", "(<i>V</i><sub>sf</sub>/<i>V</i><sub>df</sub>)^2 + (<i>T</i><sub>f</sub>/<i>T</i><sub>df</sub>)^2 = (" + self.Vsf + "/" + self.Vdf + ")^2 + ("
    #                     + self.Tf + "/" + self.Tdf + ")^2 = " + self.combined_capacity + " <br> [cl. 10.4.6]", " <p align=left style=color:red><b>Fail</b></p> "]
    #             else:
    #
    #                 row = [0, "Combined shear and tension capacity of bolt", "&#8804; 1.0",
    #                        "(<i>V</i><sub>sf</sub>/<i>V</i><sub>df</sub>)^2 + (<i>T</i><sub>f</sub>/<i>T</i><sub>df</sub>)^2 = (" + self.Vsf + "/" + self.Vdf + ")^2 + ("
    #                        + self.Tf + "/" + self.Tdf + ")^2 = " + self.combined_capacity + " <br> [cl. 10.4.6]", " <p align=left style=color:green><b>Pass</b></p> "]
    #         else:
    #             if float(self.combined_capacity) > float(1):
    #                 row = [0, "Combined shear and tension capacity of bolt", "&#8804; 1.0", "(<i>V</i><sub>sb</sub>/<i>V</i><sub>db</sub>)^2 + (<i>T</i><sub>b</sub>/<i>T</i><sub>db</sub>)^2 = (" + self.Vsb + "/" + self.Vdb + ")^2 + ("
    #                        + self.Tb + "/" + self.Tdb + ")^2 = " + self.combined_capacity + " <br> [cl. 10.3.6]", " <p align=left style=color:red><b>Fail</b></p> "]
    #                 # print(type(row))
    #
    #             else:
    #                 row = [0, "Combined shear and tension capacity of bolt", "&#8804; 1.0", "(<i>V</i><sub>sb</sub>/<i>V</i><sub>db</sub>)^2 + (<i>T</i><sub>b</sub>/<i>T</i><sub>db</sub>)^2 = (" + self.Vsb + "/" + self.Vdb + ")^2 + ("
    #                        + self.Tb + "/" + self.Tdb + ")^2 = " + self.combined_capacity + " <br> [cl. 10.3.6]", " <p align=left style=color:green><b>Pass</b></p> "]
    #     else:
    #         row = [0, "Combined shear and tension capacity of bolt", "&#8804; 1.0",
    #                "(<i>V</i><sub>sb</sub>/<i>V</i><sub>db</sub>)^2 + (<i>T</i><sub>b</sub>/<i>T</i><sub>db</sub>)^2 = Cannot compute" " <br> [cl. 10.3.6]", " <p align=left style=color:red><b>Fail</b></p> "]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Number of bolts required
    #     e += self.t('tr')
    #     row = [0, "No. of bolts", "&#8805; 4 , &#8804; 12", str(float(self.number_of_bolts)), ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # TODO: Add pitch checks (Danish)
    #     # Bolt pitch
    #     if self.number_of_bolts == 8:
    #         if float(self.pitch) < float(self.pitch_mini) or float(self.pitch) > float(self.pitch_max):
    #             row = [0, "Bolt pitch (mm)"," &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                    + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]",self.pitch, "  <p align=left style=color:red><b>Fail</b></p>"]
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #             e += self.t('/tr')
    #         else:
    #             row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                    + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch, "  <p align=left style=color:green><b>Pass</b></p>"]
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #             e += self.t('/tr')
    #     elif self.number_of_bolts == 12:
    #         if float(self.pitch23) == float(self.pitch45) < float(self.pitch_mini) or float(self.pitch34) < float(self.pitch_mini):
    #             if float(self.pitch23) == float(self.pitch45) > float(self.pitch_mini) or float(self.pitch34) > float(self.pitch_max):
    #                 row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                        + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch23 and self.pitch34, "  <p align=left style=color:red><b>Fail</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #             else:
    #                 row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                        + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch23 and self.pitch34, "  <p align=left style=color:green><b>Pass</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #     elif self.number_of_bolts == 16:
    #         if float(self.pitch23) == float(self.pitch34) == float(self.pitch56) == float(self.pitch67) < float(self.pitch_mini) or float(self.pitch45) < float(self.pitch_mini):
    #             if float(self.pitch23) == float(self.pitch34) == float(self.pitch56) == float(self.pitch67) > float(self.pitch_mini) or float(self.pitch45) > float(self.pitch_mini):
    #                 row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                        + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch23 and self.pitch45, "  <p align=left style=color:red><b>Fail</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #             else:
    #                 row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                        + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch23 and self.pitch45,
    #                        "  <p align=left style=color:green><b>Pass</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #     elif self.number_of_bolts == 20:
    #         if float(self.pitch12) == float(self.pitch34) == float(self.pitch45) == float(self.pitch67) == float(self.pitch78) == float(self.pitch910) < float(self.pitch_mini) or float(self.pitch56) < float(self.pitch_mini):
    #             if float(self.pitch12) == float(self.pitch34) == float(self.pitch45) == float(self.pitch67) == float(self.pitch78) == float(self.pitch910) > float(self.pitch_mini) or float(self.pitch56) > float(self.pitch_mini):
    #                 row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                        + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch12 and self.pitch56, "  <p align=left style=color:red><b>Fail</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #             else:
    #                 row = [0, "Bolt pitch (mm)", " &#8805; 2.5* " + self.bolt_dia + " = " + self.pitch_mini + ",  &#8804; Min(32*" + self.end_plate_thickness + ", 300) = "
    #                        + self.pitch_max + "<br> [cl. 10.2.2 & cl. 10.2.3]", self.pitch12 and self.pitch56,
    #                        "  <p align=left style=color:green><b>Pass</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #
    #     # Pitch Distance
    #     e += self.t('tr')
    #
    #     if float(self.pitch_dist) < float(self.pitch_dist_min) or float(self.pitch_dist) > float(self.pitch_dist_max):
    #         row = [0, "Pitch distance (mm)"," &#8805; 2.5 * d  = " + self.pitch_dist_min + ", &#8804; min(32 * t, 300) = " + self.pitch_dist_max + " <br> [cl. 10.2.2 & cl. 10.2.3]",
    #                self.pitch_dist, " <p align=left style=color:red><b>Fail</b></p> "]
    #     else:
    #         row = [0, "Pitch distance (mm)"," &#8805; 2.5 * d  = " + self.pitch_dist_min + ", &#8804; min(32 * t, 300) = " + self.pitch_dist_max + " <br> [cl. 10.2.2 & cl. 10.2.3]",
    #                self.pitch_dist, " <p align=left style=color:green><b>Pass</b></p> "]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # if float(gauge_distance) > float(gauge_max):
    #     #     row = [0, "Bolt gauge (mm)"," &#8805; 2.5*" + bolt_dia + " = " + gauge_mini + ", &#8804; min(32*" + end_plate_thickness + ", 300) = " + gauge_max + " <br> [cl. 10.2.2 & cl. 10.2.3]",
    #     #        gauge_distance, " <p align=left style=color:red><b>Fail</b></p> "]
    #     # else:
    #     #     row = [0, "Bolt gauge (mm)"," &#8805; 2.5*" + bolt_dia + " = " + gauge_mini + ", &#8804; min(32*" + end_plate_thickness + ", 300) = " + gauge_max + " <br> [cl. 10.2.2 & cl. 10.2.3]",
    #     #            gauge_distance, " <p align=left style=color:green><b>Pass</b></p> "]
    #     #
    #     # e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     # e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     # e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     # e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     # e += self.t('/tr')
    #
    #     # End Distance
    #     e += self.t('tr')
    #
    #     self.end_mini_actual = str(float(self.min_edgend_dist) * float(self.dia_hole))
    #
    #     if self.typeof_edge == "a - Sheared or hand flame cut":
    #
    #         if float(self.end_distance) < float(self.end_mini) or float(self.end_distance) > float(self.end_max):
    #             row = [0, "End distance (mm)"," &#8805; 1.7 <i>d</i><sub>o</sub>" + " = " + self.end_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.end_max + " <br> [cl. 10.2.4]",
    #                    self.end_distance,"  <p align=left style=color:red><b>Fail</b></p>"]
    #         else:
    #             row = [0, "End distance (mm)"," &#8805; 1.7 <i>d</i><sub>o</sub>" + " = " + self.end_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.end_max + " <br> [cl. 10.2.4]",
    #                    self.end_distance,"  <p align=left style=color:green><b>Pass</b></p>"]
    #
    #     else:
    #         if float(self.end_distance) < float(self.end_mini) or float(self.end_distance) > float(self.end_max):
    #             row = [0, "End distance (mm)",
    #                    " &#8805; 1.5 <i>d</i><sub>o</sub>" + " = " + self.end_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.end_max + " <br> [cl. 10.2.4]",
    #                    self.end_distance, "  <p align=left style=color:red><b>Fail</b></p>"]
    #         else:
    #
    #             row = [0, "End distance (mm)",
    #                    " &#8805; 1.5 <i>d</i><sub>o</sub>" + " = " + self.end_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.end_max + " <br> [cl. 10.2.4]",
    #                    self.end_distance, "  <p align=left style=color:green><b>Pass</b></p>"]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #     e += self.t('tr')
    #
    #     # if float(end_distance) > float(end_max):
    #     #     row = [0, "End distance (mm)",
    #     #            " &#8805; " + min_edgend_dist + "*" + dia_hole + " = " + end_mini_actual + ", &#8804; 12*" + end_plate_thickness + " = " + end_max + " <br> [cl. 10.2.4]", end_distance,
    #     #             "  <p align=left style=color:red><b>Fail</b></p>"]
    #     # else:
    #     #     row = [0, "End distance (mm)",
    #     #            " &#8805; " + min_edgend_dist + "*" + dia_hole + " = " + end_mini_actual + ", &#8804; 12*" + end_plate_thickness + " = " + end_max + " <br> [cl. 10.2.4]",
    #     #            end_distance, "  <p align=left style=color:green><b>Pass</b></p>"]
    #     #
    #     # e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     # e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     # e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     # e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     # e += self.t('/tr')
    #     # e += self.t('tr')
    #
    #     # Edge Distance
    #     e += self.t('tr')
    #
    #     self.edge_mini_actual = self.end_mini_actual
    #     if self.typeof_edge == "a - Sheared or hand flame cut":
    #         if float(self.edge_distance) < float(self.edge_mini) or float(self.edge_distance) > float(self.edge_max):
    #             row = [0, "Edge distance (mm)"," &#8805; 1.7 <i>d</i><sub>o</sub>" + " = " + self.edge_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.edge_max + " <br> [cl. 10.2.4]",
    #                    self.end_distance, "  <p align=left style=color:red><b>Fail</b></p>"]
    #         else:
    #             row = [0, "Edge distance (mm)"," &#8805; 1.7 <i>d</i><sub>o</sub>" + " = " + self.edge_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.edge_max + " <br> [cl. 10.2.4]",
    #                    self.end_distance, "  <p align=left style=color:green><b>Pass</b></p>"]
    #     else:
    #         if float(self.edge_distance) < float(self.edge_mini) or float(self.edge_distance) > float(self.edge_max):
    #             row = [0, "Edge distance (mm)"," &#8805; 1.5 <i>d</i><sub>o</sub>" + " = " + self.edge_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.edge_max + " <br> [cl. 10.2.4]",self.end_distance, "<p align=left style=color:red><b>Fail</b></p>"]
    #         else:
    #             row = [0, "Edge distance (mm)"," &#8805; 1.5 <i>d</i><sub>o</sub>" + " = " + self.edge_mini_actual + ", &#8804; 12*t*&#949;" + " = " + self.edge_max + " <br> [cl. 10.2.4]",self.end_distance, "  <p align=left style=color:green><b>Pass</b></p>"]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #     e += self.t('tr')
    #
    #     e += self.t('tr')
    #     if float(self.number_of_bolts) <= float(20):
    #
    #         if self.endplate_type == "Flush end plate":
    #             if float(self.l_v) < float(33) or float(self.l_v) > float(47):
    #                 row = [0, "Distance to the centre line of bolt from face of beam flange (mm)", "33mm &#8804; <i>l</i><sub>v</sub> &#8804; 47mm",self.l_v, "<p align=left style=color:red><b>Fail</b></p>"]
    #             else:
    #                 row = [0, "Distance to the centre line of bolt from face of beam flange (mm)", "33mm &#8804; <i>l</i><sub>v</sub> &#8804; 47mm",self.l_v, "<p align=left style=color:green><b>Pass</b></p>"]
    #
    #         elif self.endplate_type == "Extended one way":
    #             if float(self.l_v) < float(25) or float(self.l_v) > float(63.5):
    #                 row = [0, "Distance to the centre line of bolt from face of beam flange (mm)", "25mm &#8804; <i>l</i><sub>v</sub> &#8804; 63.5mm",self.l_v, "<p align=left style=color:red><b>Fail</b></p>"]
    #             else:
    #                 row = [0, "Distance to the centre line of bolt from face of beam flange (mm)", "25mm &#8804; <i>l</i><sub>v</sub> &#8804; 63.5mm",self.l_v, "<p align=left style=color:green><b>Pass</b></p>"]
    #         else:
    #             if float(self.l_v) < float(50) or float(self.l_v) > float(62.5):
    #                 row = [0, "Distance to the centre line of bolt from face of beam flange (mm)", "50mm &#8804; <i>l</i><sub>v</sub> &#8804; 62.5mm",self.l_v, "<p align=left style=color:red><b>Fail</b></p>"]
    #             else:
    #                 row = [0, "Distance to the centre line of bolt from face of beam flange (mm)", "50mm &#8804; <i>l</i><sub>v</sub> &#8804; 62.5mm",self.l_v, "<p align=left style=color:green><b>Pass</b></p>"]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #     e += self.t('tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Plate Checks", " "]
    #     e += self.t('td colspan="4" class="detail" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Plate thickness
    #
    #     e += self.t('tr')
    #     if float(self.number_of_bolts) <= (20):
    #         if float(self.plate_tk_min) > float(self.end_plate_thickness):
    #             row = [0, "Plate thickness (mm)", ("&#8805; &#8730; (M *" + "(1.1/fy) *" + "(4/<i>b</i><sub>e</sub>)) = &#8805; &#8730; ("+self.moment_tension+"*"+"(1.1/"+self.end_plate_fy+") * (4/"+self.beam_B+")) ="+self.plate_tk_min), self.end_plate_thickness, "  <p align=left style=color:red><b>Fail</b></p>"]
    #         else:
    #             row = [0, "Plate thickness (mm)", ("&#8805; &#8730; (M *" + "(1.1/fy) *" + "(4/<i>b</i><sub>e</sub>)) = &#8805; &#8730; ("+self.moment_tension+"*"+"(1.1/"+self.end_plate_fy+") * (4/"+self.beam_B+")) ="+self.plate_tk_min), self.end_plate_thickness, "  <p align=left style=color:green><b>Pass</b></p>"]
    #     else:
    #         row = [0, "Plate thickness (mm)", " Cannot compute ", self.end_plate_thickness, "  <p align=left style=color:red><b>Fail</b></p>"]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # "( (4" "*" "1.10" "*" + M_p + "*1000)/(" + end_plate_fy + "*" + b_e + ") ) ^ 0.5 = " + str(round(float(plate_tk_min), 3)) +
    #     #                    "<br> [Design of Steel Structures - N. Subramanian, 2014]"
    #
    #     # Plate Height
    #
    #     # if number_of_bolts == 20:
    #     #     plate_height_mini = str(float(beam_d) + float(50) + float(2 * float(pitch_mini)) + float(2 * float(end_mini)))  # for 20 number of bolts
    #     #     plate_height_max = str(float(beam_d) + float(50) + float(2 * float(pitch_mini)) + float(2 * float(end_max)))  # for 20 number of bolts
    #     # else:
    #     #     plate_height_mini = str(float(beam_d) + float(50) + float(2 * float(end_mini)))  # for bolts less than 20
    #     #     plate_height_max = str(float(beam_d) + float(50) + float(2 * float(end_max)))  # for bolts less than 20
    #
    #     e += self.t('tr')
    #
    #     if float(self.number_of_bolts) <= float(20):
    #         row = [0, "Plate height (mm)", "", self.plate_height, ""]
    #
    #     else:
    #         row = [0, "Plate height (mm)", " Cannot compute ", " Cannot compute", " <p align=left style=color:red><b>Fail</b></p>", "300",""]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Plate Width
    #     e += self.t('tr')
    #     if float(self.number_of_bolts) <= 20:
    #         #g_1 = float(90)  # cross centre gauge distance
    #         # plate_width_mini = beam_B        # max(float((g_1 + (2 * float(edge_mini)))), beam_B)
    #         # plate_width_max = beam_B+25    # max(float((beam_B + 25)), float(plate_width_mini))
    #
    #         if float(self.plate_width) < float(self.bf):
    #             row = [0, "Plate width (mm)","&#8805; width of beam flange" + " , "+"&#8805;" + str(float(self.bf)), self.plate_width, " <p align=left style=color:red><b>Fail</b></p>", "300", ""]
    #         else:
    #             row = [0, "Plate width (mm)","&#8805; width of beam flange" + " , "+"&#8805;" + str(float(self.bf)), self.plate_width, " <p align=left style=color:green><b>Pass</b></p>", "300", ""]
    #     else:
    #         row = [0, "Plate width (mm)", " Cannot compute ", " Cannot compute ", " <p align=left style=color:red><b>Fail</b></p>", "300", ""]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    # # weld checks
    #     e += self.t('tr')
    #     row = [0, "Weld Checks", " "]
    #     e += self.t('td colspan="4" class="detail" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     if self.weld_method == "Groove Weld (CJP)":
    #         row = [0, "Gap between beam and plate","Refernce: IS 9595:1996, Annex B",self.weld_size,""]
    #         e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #         e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #         e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #         e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #         e += self.t('/tr')
    #     else:
    #         e += self.t('/tr')
    #         # row = [0,"","","",""]
    #
    #   # flange weld checks
    #     e += self.t('tr')
    #     row = [0, "Flange", " "]
    #     e += self.t('td colspan="4" class="detail1" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Weld thickness at flange
    #     e += self.t('tr')
    #     if self.weld_method == "Fillet Weld":
    #         if float(self.number_of_bolts) <= 20:
    #             row = [0, "Effective weld length on top flange (mm)", "", self.flange_weld_effective_length_top, ""]
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #             e += self.t('/tr')
    #
    #             row = [0, "Effective weld length on bottom flange (mm)", "", self.flange_weld_effective_length_bottom, ""]
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #             e += self.t('/tr')
    #
    #             if float(self.flange_weld_size_provd) < float(self.flange_weld_size_min) or float(self.flange_weld_size_provd) > (self.flange_weld_size_max):
    #                 row = [0, "Weld throat thickness at flange (mm)", "&#60; " + str(self.flange_weld_size_max) + ",""&#62; " + str(self.flange_weld_size_min) , str(float(self.flange_weld_size_provd)), " <p align=left style=color:red><b>Fail</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #
    #             else:
    #                 row = [0, "Weld throat thickness at flange (mm)", "&#60; " + str(self.flange_weld_size_max) + ",""&#62; " + str(self.flange_weld_size_min) , str(float(self.flange_weld_size_provd)), " <p align=left style=color:green><b>Pass</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #
    #             if float(self.flange_weld_stress) > float(self.flange_weld_strength):
    #                 row = [0, "Critical stress in weld at flange (N/mm^2)","&#8805; ((M/<i>Z</i><sub>weld,flange</sub>) + (P/<i>A</i><sub>weld</sub>)) ="+ self.flange_weld_stress,"(<i>f</i><sub>u</sub> / &#8730;3 * <i>&#120574;</i><sub>mb</sub>) = "+ self.flange_weld_strength, " <p align=left style=color:red><b>Fail</b></p>"]
    #
    #
    #             else:
    #                 row = [0, "Critical stress in weld at flange (N/mm^2)","&#8805; ((M/<i>Z</i><sub>weld,flange</sub>) + (P/<i>A</i><sub>weld</sub>)) ="+ self.flange_weld_stress,"(<i>f</i><sub>u</sub> / &#8730;3 * <i>&#120574;</i><sub>mb</sub>) = "+ self.flange_weld_strength, " <p align=left style=color:green><b>Pass</b></p>"]
    #
    #     else:
    #         row = [0,"Weld Size at Flange (mm)","min(beam flange thickness, end plate thickness) = min(" +str(float(self.beam_tf)) + " , "+str(float(self.plate_thk))+")" ,self.groove_weld_size_flange,""]
    #
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # web weld checks
    #     e += self.t('tr')
    #     row = [0, "Web", " "]
    #     e += self.t('td colspan="4" class="detail1" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Weld thickness at web
    #     e += self.t('tr')
    #     if self.weld_method == "Fillet Weld":
    #         if float(self.number_of_bolts) <= 20:
    #             row = [0, "Effective weld length at web (each side) (mm)", "", self.web_weld_effective_length, ""]
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #             e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #             e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #             e += self.t('/tr')
    #
    #             if float(self.web_weld_size_provd) < float(self.web_weld_size_min) or float(self.web_weld_size_provd) > (self.web_weld_size_max):
    #                 row = [0, "Weld throat thickness at web (mm)", "&#60; " + str(self.web_weld_size_max)+ ",""&#62; " + str(self.web_weld_size_min) , self.web_weld_size_provd, " <p align=left style=color:red><b>Fail</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #
    #             else:
    #                 row = [0, "Weld throat thickness at web (mm)", "&#60; " + str(self.web_weld_size_max)+ ",""&#62; " + str(self.web_weld_size_min) , self.web_weld_size_provd, " <p align=left style=color:green><b>Pass</b></p>"]
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #                 e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #                 e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #                 e += self.t('/tr')
    #
    #             if float(self.web_weld_stress) > float(self.web_weld_strength):
    #                 row = [0, "Critical stress in weld at web (N/mm^2)",
    #                        "&#8805; &#8730; ((M/<i>Z</i><sub>weld,web</sub> + P/<i>A</i><sub>weld</sub>)<i></i><sup>2</sup>)) + (V/<i>A</i><sub>weld,web</sub>)<i></i><sup>2</sup> =" + self.web_weld_stress,
    #                        "(<i>f</i><sub>u</sub> / &#8730;3 * <i>&#120574;</i><sub>mb</sub>) = " + self.web_weld_strength,
    #                        " <p align=left style=color:red><b>Fail</b></p>"]
    #
    #             else:
    #                 row = [0, "Critical stress in weld at web (N/mm^2)",
    #                        "&#8805; &#8730; ((M/<i>Z</i><sub>weld,web</sub> + P/<i>A</i><sub>weld</sub>)<i></i><sup>2</sup>)) + (V/<i>A</i><sub>weld,web</sub>)<i></i><sup>2</sup> =" + self.web_weld_stress,
    #                        "(<i>f</i><sub>u</sub> / &#8730;3 * <i>&#120574;</i><sub>mb</sub>) = " + self.web_weld_strength,
    #                        " <p align=left style=color:green><b>Pass</b></p>"]
    #
    #     else:
    #         row = [0, "Weld Size at Web (mm)","min(beam web thickness, plate thickness) = min("+ str(float(self.beam_tw)) +" , "+ str(float(self.plate_thk)) + ")", self.groove_weld_size_web, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # # Stiffener Checks
    #     e += self.t('tr')
    #     row = [0, "Stiffener Checks", " "]
    #     e += self.t('td colspan="4" class="detail" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Horizontal continuity plate in tension
    #     e += self.t('tr')
    #     row = [0, "Horizontal Continuity Plate in Tension", " "]
    #     e += self.t('td colspan="4" class="detail1" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Length (mm)", "", self.cont_plate_tens_length, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Width (mm)", "", self.cont_plate_tens_width, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Thickness (mm)", "&#8805;"+ str(round(float(self.cont_plate_comp_thk_min),3)), self.cont_plate_tens_thk, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Weld (mm)", "", self.cont_plate_tens_weld, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # Horizontal continuity plate in comp
    #     e += self.t('tr')
    #     row = [0, "Horizontal Continuity Plate in Compression", " "]
    #     e += self.t('td colspan="4" class="detail1" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Length (mm)", "", self.cont_plate_comp_length, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Width (mm)", "", self.cont_plate_comp_width, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Thickness (mm)", "&#8805;"+ str(round(float(self.cont_plate_comp_thk_min),3)), self.cont_plate_comp_thk, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Weld (mm)", "", self.cont_plate_comp_weld, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     # End Plate Stifferners
    #     e += self.t('tr')
    #     row = [0, "End Plate Stiffeners", " "]
    #     e += self.t('td colspan="4" class="detail1" align="center"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Length (mm)", "", self.st_length, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Height (mm)", "", self.st_height, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Thickness (mm)", "", self.st_thk, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Noch at top side of plate (mm)", "", self.st_notch_top, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Noch at bottom side of plate (mm)", "", self.st_notch_bottom, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #     row = [0, "Fillet weld size (mm)", "", self.st_weld, ""]
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[2] + self.t('/td')
    #     e += self.t('td class="detail2"') + self.space(row[0]) + row[3] + self.t('/td')
    #     e += self.t('td class="detail1"') + self.space(row[0]) + row[4] + self.t('/td')
    #     e += self.t('/tr')
    #
    #     e += self.t('tr')
    #
    #     e += self.t('/table')
    #     e += self.t('h1 style="page-break-before:always"')  # page break
    #     e += self.t('/h1')
    #
    #     # ######################################### End of checks #########################################
    #
    #     # ################################### Page 6: Views  ###################################################
    #
    #     f = (self.design_summary(reportsummary))
    #     print(f)
    #
    #     f += self.t('table width = 100% border-collapse= "collapse" border="1px solid black"')
    #
    #     if self.status == "True":
    #
    #         row = [0, "Fabrication Drawings", " "]
    #         f += self.t('tr')
    #         f += self.t('td colspan="2" class=" detail" align=center '
    #                   '') + self.space(row[0]) + row[1] + self.t('/td')
    #         f += self.t('/tr')
    #         png = folder + "/images_html/3D_Model.png"
    #         datapng = '<object type="image/PNG" data= %s height = "550px" width = "auto" ></object>' % png
    #
    #         top = folder + "/images_html/extendTop.png"
    #         datatop = '<object type="image/PNG" data= %s height = "630px" width = "820px" ></object>' % top
    #
    #         if self.status == 'True':
    #             row = [0, datapng]
    #             f += self.t('tr')
    #             f += self.t('td  align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #             row = [1, datatop]
    #             f += self.t('tr')
    #             f += self.t('td align="center" class=" header2 "') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #         else:
    #             pass
    #
    #         f += self.t('/table')
    #         f += self.t('h1 style="page-break-before:always"')  # page break
    #         f += self.t('/h1')
    #
    #         f += self.t('table width = 100% border-collapse= "collapse" border="1px solid black"')
    #         row = [0, "Fabrication Drawings", " "]
    #         f += self.t('tr')
    #         f += self.t('td colspan="2" class=" detail" align=center '
    #                   '') + self.space(row[0]) + row[1] + self.t('/td')
    #         f += self.t('/tr')
    #         side = folder + "/images_html/extendSide.png"
    #         dataside = '<object type="image/PNG" data= %s height = "600px" width = "800px" ></object>' % side
    #
    #         front = folder + "/images_html/extendFront.png"
    #         datafront = '<object type="image/PNG" data= %s height = "680px" width = "1000px" </object>' % front
    #
    #         if self.status == 'True':
    #             row = [1, dataside]
    #             f += self.t('tr')
    #             f += self.t('td align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #             row = [1, datafront]
    #             f += self.t('tr')
    #             f += self.t('td align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #         else:
    #             pass
    #
    #         f += self.t('/table')
    #         f += self.t('h1 style="page-break-before:always"')  # page break
    #         f += self.t('/h1')
    #
    #     else:
    #         f += self.t('table width = 100% border-collapse= "collapse" border="1px solid black"')
    #
    #         row = [0, "Fabrication Drawings", " "]
    #         f += self.t('tr')
    #         f += self.t('td colspan="2" class=" detail"') + self.space(row[0]) + row[1] + self.t('/td')
    #         f += self.t('/tr')
    #
    #         row = [0, "The fabrication drawings are not been generated due to the failure of the connection.", " "]
    #         f += self.t('tr')
    #         f += self.t('td colspan="2" class=" detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #         f += self.t('/tr')
    #
    #         f += self.t('/table')
    #         f += self.t('h1 style="page-break-before:always"')  # page break
    #         f += self.t('/h1')
    #
    #     f += self.t('table width = 100% border-collapse= "collapse" border="1px solid black"')
    #
    #     if self.weld_method == "Groove Weld (CJP)":
    #
    #         row = [0, "Weld Detailing", " "]
    #         f += self.t('tr')
    #         f += self.t('td colspan="2" class=" detail"') + self.space(row[0]) + row[1] + self.t('/td')
    #         f += self.t('/tr')
    #
    #         if float(self.beam_tf) <= float(12):
    #             row = [0, '<object type= "image/PNG" data= "Butt_weld_single_flange.png"  ></object>']
    #             f += self.t('tr')
    #             f += self.t('td  align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #             row = [0, "Note :- As flange thickness, <i>t</i><sub>f</sub> (" + str(float(self.beam_tf)) + "mm) <= 12mm, single bevel groove welding is provided [Reference: IS 9595: 1996] (All dimensions are in mm )", " "]
    #             f += self.t('tr')
    #             f += self.t('td colspan="1" class=" detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #         else:
    #             row = [0, '<object type= "image/PNG" data= "Butt_weld_double_flange.png"  ></object>']
    #             f += self.t('tr')
    #             f += self.t('td  align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #             row = [0,
    #                    "Note :- As flange thickness, <i>t</i><sub>f</sub> (" + str(float(self.beam_tf)) + "mm) >= 12mm, double bevel groove welding is provided [Reference: IS 9595: 1996] (All dimensions are in mm )",
    #                    " "]
    #             f += self.t('tr')
    #             f += self.t('td colspan="2" class=" detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #         if float(self.beam_tw) <= float(12):
    #             row = [0, '<object type= "image/PNG" data= "Butt_weld_single_web.png"  ></object>']
    #             f += self.t('tr')
    #             f += self.t('td  align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #             row = [0,
    #                    "Note :- As web thickness, <i>t</i><sub>w</sub> (" + str(float(self.beam_tw)) + "mm) <= 12mm, single bevel groove welding is provided [Reference: IS 9595: 1996] (All dimensions are in mm )",
    #                    " "]
    #             f += self.t('tr')
    #             f += self.t('td colspan="2" class=" detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #         else:
    #             row = [0, '<object type= "image/PNG" data= "Butt_weld_double_web.png"  ></object>']
    #             f += self.t('tr')
    #             f += self.t('td  align="center" class=" header2"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #             row = [0,
    #                    "Note :- As web thickness, <i>t</i><sub>w</sub> (" + str(float(self.beam_tw)) + "mm) >= 12mm, double bevel groove welding is provided [Reference: IS 9595: 1996] (All dimensions are in mm )",
    #                    " "]
    #             f += self.t('tr')
    #             f += self.t('td colspan="2" class=" detail1"') + self.space(row[0]) + row[1] + self.t('/td')
    #             f += self.t('/tr')
    #
    #         f += self.t('/table')
    #         f += self.t('h1 style="page-break-before:always"')  # page break
    #         f += self.t('/h1')
    #
    #     else:
    #         f += self.t('/tr')

        # ############################## Page 7 (Additional comments)  #############################################################

        g = (self.design_summary(reportsummary))
        print(g)

        g += self.t('table width = 100% border-collapse= "collapse" border="1px solid black"')
        g += self.t('''col width=30%''')
        g += self.t('''col width=70%''')

        g += self.t('tr')
        row = [0, "Additional Comments", self.addtionalcomments]
        g += self.t('td class= "detail1"') + self.space(row[0]) + row[1] + self.t('/td')
        g += self.t('td class= "detail2" align="justified"') + row[2] + self.t('/td')
        g += self.t('/tr')
        g += self.t('/table')

    ###### Writing all the pages  #####
        self.myfile.write(rstr)
        self.myfile.write(d)
        # myfile.write(e)
        # myfile.write(f)
        self.myfile.write(g)
        self.myfile.write(self.t('/body'))
        self.myfile.write(self.t('/html'))
        self.myfile.close()


    def space(self,n):
        rstr = "&nbsp;" * 4 * n
        return rstr

    def t(self,n):
        abc = '<' + n + '/>'
        return abc

    def w(n):
        return '{' + n + '}'

    def quote(m):
        return '"' + m + '"'

    def design_summary(self,reportsummary):

        self.companyname = str(reportsummary["ProfileSummary"]['CompanyName'])
        companylogo = str(reportsummary["ProfileSummary"]['CompanyLogo'])
        self.groupteamname = str(reportsummary["ProfileSummary"]['Group/TeamName'])
        self.designer = str(reportsummary["ProfileSummary"]['Designer'])
        self.projecttitle = str(reportsummary['ProjectTitle'])
        self.subtitle = str(reportsummary['Subtitle'])
        self.jobnumber = str(reportsummary['JobNumber'])
        self.client = str(reportsummary['Client'])
        addtionalcomments = str(reportsummary['AdditionalComments'])

        rstr = self.t('table border-collapse= "collapse" border="1px solid black" width=100%')

        rstr += self.t('tr')
        row = [0, '<object type= "image/PNG" data= "cmpylogoExtendEndplate.png" height=60 ></object>',
               '<font face="Helvetica, Arial, Sans Serif" size="3">Created with</font>' "&nbsp" "&nbsp" "&nbsp" "&nbsp" "&nbsp" '<object type= "image/PNG" data= "Osdag_header.png" height=60 ''&nbsp" "&nbsp" "&nbsp" "&nbsp"></object>']
        rstr += self.t('td colspan="2" align= "center"') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('td colspan="2" align= "center"') + row[2] + self.t('/td')
        rstr += self.t('/tr')

        rstr += self.t('tr')
        row = [0, 'Company Name']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.companyname]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')

        row = [0, 'Project Title']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.projecttitle]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        rstr += self.t('tr')
        row = [0, 'Group/Team Name']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.groupteamname]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, 'Subtitle']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.subtitle]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        rstr += self.t('tr')
        row = [0, 'Designer']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.designer]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, 'Job Number']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.jobnumber]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')

        rstr += self.t('tr')
        row = [0, 'Date']
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, time.strftime("%d /%m /%Y")]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, "Client"]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        row = [0, self.client]
        rstr += self.t('td class="detail" ') + self.space(row[0]) + row[1] + self.t('/td')
        rstr += self.t('/tr')
        rstr += self.t('/table')

        rstr += self.t('hr')
        rstr += self.t('/hr')

        return rstr