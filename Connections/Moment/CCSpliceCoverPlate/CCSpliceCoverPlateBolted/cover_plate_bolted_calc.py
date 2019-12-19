'''
Created on 30-Oct-2017
Revised on 5-March-2018
Revised on 13-April-2018
Revised on 15-June-2018 (experts suggestions)
Revised on 18-June-2018 (experts suggestions)
Revised on 25-June-2018 (After launch)
@author: Swathi M.
'''

# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from Connections.Moment.CCSpliceCoverPlate.CCSpliceCoverPlateBolted.model import *
from Connections.connection_calculations import ConnectionCalculations
import math
import logging
import sys
flag = 1
logger = None

def module_setup():
    global logger
    logger = logging.getLogger("osdag.cover_plate_bolted_calc")
    module_setup()

########################################################################################################################
# Reference:
########################################################################################################################
### 1. Example 10.14 - M.L. Gambhir (page 10.83)
### 2. Example 5.27 - N. Subramanian (page 427)
### 3. IS 800 : 2007
### 4. 30 good rules for connection design, AISC
### 5. Steel Designer's Manual - 6th Edition (2003)
### 6. Bolted field splices for steel bridge flexural members AISC - overview and design example: Design example 3.1
### 7. INSDAG design example
### 8. Structural steel work connections - Graham Owens (Design Examples)


'''
ASCII diagram - Column-Column Bolted Splice Connection with Cover Plates
                                                           +-----+ Flange splice plate
                                                           |
                      ++         ++        ++          ++  |      ++        ++
                 +----||---------||--------||----++----||--v------||--------||----+
    +------------+----||---------||--------||----++----||---------||--------||----+------------+
    +-----------------||---------||--------||----++----||---------||--------||-----------------+
    |                 ++         ++        ++    ||    ++         ++        ++                 |
    |                                            ||                                            |
    |   BEAM                            +------------------+                                   |
    |                                   |        ||        |                                   |
    |                                   |   x    ||    x   |                                   |
    |                                   |        ||        |                                   |
    |                                   |        ||        <------+ Web splice plate           |
    |                                   |   x    ||    x   |                                   |
    |                                   |        ||        |                                   |
    |                                   |        ||        |                                   |
    |                                   |   x    ||    x   |                                   |
    |                                   |        ||        |                                   |
    |                                   +------------------+                                   |
    |                                            ||                                            |
    |                 ++         ++        ++    ||    ++         ++         ++                |
    +-----------------||---------||--------||----++----||---------||---------||----------------+
    +-----------------||---------||--------||----++----||---------||---------||----------------+
                 +----||---------||--------||----++----||---------||---------||---+
                      ++         ++        ++          ++         ++         ++
'''
########################################################################################################################
########################################################################################################################
# def fetchColumnPara(self):
#     column_section = self.ui.combo_columnSec.currentText()
#     dictcolumndata = get_columndata(column_section)
#     return dictcolumndata
#
# ########################################################################################################################
#
#
    # Read input values from Column  database

    # dictcolumndata = get_columndata(column_section)
    #
    # column_t_w = float(dictcolumndata["tw"])
    # column_f_t = float(dictcolumndata["T"])
    # column_d = float(dictcolumndata["D"])
    #
    # column_r1 = float(dictcolumndata["R1"])
    # column_b = float(dictcolumndata["B"])
    # column_area = float(dictcolumndata["Area"])

########################################################################################################################


########################################################################################################################
# Force in flange (kN)  [Reference: M.L. Gambhir (page 10.83), N. Subramanian (page 427)]
# Revised on 15-June-2018
def flange_force(column_d, column_f_t,column_b, column_area, axial_force, moment_load):

    """
    Args:
       Column_d: Overall depth of the column section in mm (float)
       Column_b: width of the column section in mm (float)
       Column_f_t: Thickness of flange in mm (float)
       axial_force: Factored axial force in kN (float)
       moment_load: Factored bending moment in kN-m (float)
    Returns:
        Force in flange in kN (float)
    """
    tm = moment_load
    area_f = column_b * column_f_t
    axial_force_f = float(area_f * axial_force / column_area)
    return round((tm*1000)/(column_d - column_f_t), 2) + (axial_force_f)        # kN

# Force in flange (kN)  [Reference:  N. Subramanian (page 428)]
def web_force(column_d,column_f_t, column_t_w, axial_force,column_area):
    """
    Args:
       column_d: Overall depth of the column section in mm (float)
       column_f_t: Thickness of flange in mm (float)
       column_t_w: Thickness of flange in mm (float)
       axial_force: Factored axial force in kN (float)

    Returns:
        Force in flange in kN (float)
    """
    axial_force_w = ((column_d - 2(column_f_t)) * column_t_w * axial_force) / column_area
    return round(axial_force_w)
########################################################################################################################
########################################################################################################################
# Thickness of flange splice plate [Reference: N. Subramanian (Page 428), M.L. Gambhir (Page 10.84)]
def thk_flange_plate(column_d, column_f_t, bolt_diameter, column_area,  axial_force, moment_load,column_b,column_fy, dia_hole):
    """
    Args:
        column_d: Overall depth of the column section in mm (float)
        column_f_t: Thickness of flange in mm (float)
        axial_force: Factored axial force in kN (float)
        moment_load: Factored bending moment in kN-m (float)
        column_b: Width of flange in mm (float)
        column_fy: Characteristic yield stress in N/mm^2 (float)
        pitch = gauge
    Returns:
    """

    edge_dist = 1.5 * dia_hole
    gauge = 2.5 * bolt_diameter
    gauge_req = (column_b - (2 * edge_dist)) / gauge  # number of gauge dist required along flange width
    n = gauge_req + 1  # number of bolts along flange width
    gamma_m0 = 1.10 # Partial safety factor against yield stress and buckling = 1.10 (float)
    ff = flange_force(column_d, column_f_t,column_b, column_area, axial_force, moment_load)
    flangeplatethickness = ff / ((column_b - n * dia_hole) * (column_fy / (gamma_m0 * 1000)))

    return round(flangeplatethickness, 2) # mm

def flange_plate_w(edge_dist, number_of_column_flange, flange_gauge):
    flangeplatewidth = float((edge_dist + (number_of_column_flange -1)* flange_gauge)*2)
    return round(flangeplatewidth, 2)

## Minimum thickness of flange splice plate
def flange_plate_min_t( column_t_w, flangeplatemaxt):
    """
    Args:
        column_t_w: thickness of web in mm(float)
    Returns: Maximum thickness of flange splice plate in mm (float)
    """
    flangeplatemint = min(column_t_w/2, 10)
    return float(flangeplatemint)

## Maximum Height of flange splice plate
def flange_plate_l_max(end_dist,number_of_row_flange, pitch_distance):
    flangeplateheightmax = float((end_dist + (number_of_row_flange -1)* pitch_distance)*2)
    return round((flangeplateheightmax) ,2)

## Minimum thickness of flange splice plate
def flange_plate_l_min(flangeplatewidth):
    flangeplateheightmin =  (2 * flangeplatewidth)
    return round((flangeplateheightmin) ,2)

## Maximum width of flange splice plate
def flange_plate_w_max(column_b):
    flangeplatewidthmax = column_b
    return round(flangeplatewidthmax, 2)

## Minimum width of flange splice plate

def flange_plate_w_min(edge_dist, flange_gauge):
    flangeplatewidthmin = float((edge_dist + flange_gauge)*2)
    return round(flangeplatewidthmin, 2)

########################################################################################################################
########################################################################################################################
## Height of Web splice plate
def web_plate_l(end_dist,number_of_row_flange, pitch_distance):
    flangeplateheight = float((end_dist + (number_of_row_flange -1)* pitch_distance)*2)
    return round((flangeplateheight) ,2)

## Minimum thickness of web splice plate
def web_plate_l_min(flangeplatewidth):
    flangeplateheightmin =  (2 * flangeplatewidth)
    return round((flangeplateheightmin) ,2)

# Maximum width of flange splice plate
def web_max_w(column_d, column_f_t, column_r1):
    """
    Args:
        column_d: Overall depth of supported beam (float) in mm
        column_f_t: Thickness of flange in mm (float)
        column_r1: Root radius of the beam section in mm (float)
    Returns: Maximum width of web splice plate in mm (float)
    """
    maxwebwidth = float(round((column_d - 2 * column_f_t - 2 * column_r1 - 2 * 5), 2))
    return maxwebwidth


## Width of web splice plate
# Minimum width of web splice plate [Reference: Steel Designer`s Manual - SCI - 6th edition, page 754]
def web_min_w(column_d):
    """
    Args:
    column_d: Overall depth of supported column (float) in mm
    Returns: Minimum width of web splice plate (float)
    """
    web_min_w= round((0.5 * column_d), 2)
    return web_min_w

## Maximum thickness of web splice plate [Reference: Handbook on structural steel detailing, INSDAG - Chapter 5, section 5.2.3 page 5.7]
def web_max_t(bolt_diameter):
    """
    Args:
        bolt_diameter: Nominal bolt diameter in mm (int)
    Returns: Maximum thickness of web splice plate in mm (float)
    """
    max_web_t = round((0.5 * bolt_diameter), 2)
    return max_web_t

## Minimum thickness of web splice plate [Reference: N. subramanian, page 373]
def web_min_t( shear_load, column_d, gamma_m0, column_fy):
    """
    Args:
        column_t_w: thickness of web in mm(float)
    Returns: Maximum thickness of web splice plate in mm (float)
    """

    web_min_t = math.sqrt(3) * (gamma_m0 * shear_load) / (0.6 * column_d * column_fy)
    return web_min_t
########################################################################################################################
########################################################################################################################
# Maximun Width of inner flange splice plate
def func_max_inner_flange_plate_w(column_b,column_t_w, column_r1):
    max_inner_flange_plate_w = (column_b - column_t_w - column_r1)/2
    return (max_inner_flange_plate_w)


# Minimun Width of inner flange splice plate
def func_min_inner_flange_plate_w(edge_dist, number_of_column_flange, gauge_flange, column_t_w, column_r1 ):

    min_inner_flange_plate_w = 2 * (2* edge_dist + (number_of_column_flange - 1)* gauge_flange) - column_t_w- (2 * column_r1)
    return (min_inner_flange_plate_w)


# Maximun Height of inner flange splice plate
def func_max_inner_flange_l(end_dist,number_of_row_flange, flange_pitch):
    flangeinnerplatemaxl = float((end_dist + (number_of_row_flange -1)* flange_pitch)*2)
    return round((flangeinnerplatemaxl) ,2)


# Minimun Height of inner flange splice plate

# Maximun Thickness of inner flange splice plate

# Thickness of flange splice plate [Reference: N. Subramanian (Page 428), M.L. Gambhir (Page 10.84)]
def func_flangeinnerplatet(column_d, column_f_t, column_area, bolt_diameter , axial_force, moment_load,column_b,column_fy, dia_hole):
    """
    Args:
        column_d: Overall depth of the column section in mm (float)
        column_f_t: Thickness of flange in mm (float)
        axial_force: Factored axial force in kN (float)
        moment_load: Factored bending moment in kN-m (float)
        column_b: Width of flange in mm (float)
        column_fy: Characteristic yield stress in N/mm^2 (float)
        pitch = gauge
    Returns:
    """

    edge_dist = 1.5 * dia_hole
    gauge = 2.5 * bolt_diameter
    gauge_req = (column_b - (2 * edge_dist)) / gauge  # number of gauge dist required along flange width
    n = gauge_req + 1  # number of bolts along flange width
    gamma_m0 = 1.10 # Partial safety factor against yield stress and buckling = 1.10 (float)
    ff = flange_force(column_d, column_f_t,column_b, column_area, axial_force, moment_load)
    flangeinnerplatethickness = ff / ((column_b - n * dia_hole) * (column_fy / (gamma_m0 * 1000)))

    return round(flangeinnerplatethickness, 2) # mm


# Minimun Thickness of inner flange splice plate
def func_min_inner_flange__t( column_t_w):
    """
    Args:
        column_t_w: thickness of web in mm(float)
    Returns: Maximum thickness of flange splice plate in mm (float)
    """
    flangeinnerplatemint = min(column_t_w/2,10)
    return float(flangeinnerplatemint)



########################################################################################################################
# Capacity of flange [Reference: N. Subramanian (Page 428), M.L. Gambhir (Page 10.84)]
def flange_capacity(column_f_t,column_b,n,dia_hole,column_fy):
    """
    Args:
        tf: Thickness of flange in mm (float)
        bf: Width of flange in mm (float)
        bolt_hole_diameter: Diameter of bolt hole in mm
        fy: Characteristic yield stress in kN/m2 (float)
    Returns: Calculates flange capacity (kN) (float)(
    """
    gamma_m0 = 1.10 # Partial safety factor against yield stress and buckling = 1.10 (float)
    eff_area =(column_b - n * dia_hole) * column_f_t # eff area = (bf-n*d0)tf ## where n = number of bolts in a row (here it is 2)
    flangecapacity = (eff_area * column_fy)/(gamma_m0*1000)
    return round(flangecapacity, 2)  # kN

########################################################################################################################


########################################################################################################################
# Calculation of block shear capacity of web splice plate in axial [Reference: Bolted field splices for steel bridge flexural\
#  members AISC - overview and design example: Design example 3.1] [link: https://www.aisc.org/globalassets/nsba/design-resources/bolted-field-splices-for-steel-bridge-flexural-members_march2017.pdf]
def web_block_shear_axial( end_dist, number_of_row_web, column_t_w, dia_hole, column_d, column_f_t, number_of_column_web, column_fy, column_fu):
    """
    Args:
        edge_dist: Edge/end distance in mm (Assumption: edge distance = end distance) (float)
        column_t_wp: Thickness of web splice plate in mm (float)
        column_t_w: Thickness of web in mm (float)
        number_of_column_web: number of bolt columns(int)
        number_of_row_web: number of bolt rows(int)
        column_f_t: Thickness of flange in mm (float)
        dia_hole: Diameter of bolt hole in mm (int)
        fy: Characteristic yield stress in N/mm^2 (float)
        fu: Ultimate tensile stress of the material in N/mm^2 (float)
        gauge_dist = 2.5 * dia_hole
    Returns: Block shear capacity of web splice plate in kN
    """

    gamma_m0 = 1.10
    gamma_m1 = 1.25
    pitch = 2.5 * dia_hole
    gauge_dist = 2.5 * dia_hole
    Avg = 2 * (end_dist + (number_of_row_web - 1) * pitch) * column_t_w
    Avn = 2*(end_dist + (number_of_row_web - 1) * pitch - (number_of_column_web - 0.5) * dia_hole) * column_t_w
    Atg = (column_d - column_f_t - ((number_of_column_web - 1) * gauge_dist)) * column_t_w
    Atn = (column_d - column_f_t - ((number_of_column_web - 1) * gauge_dist) - (number_of_column_web - 0.5) * dia_hole) * column_t_w

    Tdb1 = ((Avg * column_fy) / (math.sqrt(3) * gamma_m0)) + ((0.9 * Atn * column_fu) / (gamma_m1))
    Tdb2 = ((0.9 * Avn * column_fu) / (math.sqrt(3))) + ((Atg * column_fy) / gamma_m0)
    Tdbw1 = min(Tdb1, Tdb2)

    return round((Tdbw1 / 1000), 2)

# Calculation of block shear capacity of web splice plate in shear [Reference: Bolted field splices for steel bridge flexural\
#  members AISC - overview and design example: Design example 3.1] [link: https://www.aisc.org/globalassets/nsba/design-resources/bolted-field-splices-for-steel-bridge-flexural-members_march2017.pdf]
def web_block_shear(edge_dist, end_dist, column_t_wp, dia_hole, number_of_row_web, number_of_column_web, fy, fu):
    """
    Args:
        gauge_dist = 2.5 * dia_hole
    Returns: Block shear capacity of web splice plate in kN
    """
    gamma_m0 = 1.10
    gamma_m1 = 1.25
    pitch = 2.5 * dia_hole
    gauge_dist = 2.5 * dia_hole
    Avg = (edge_dist + (number_of_column_web - 1) * gauge_dist) * column_t_wp
    Avn = (edge_dist + (number_of_column_web - 1) * gauge_dist - (number_of_column_web -0.5) * dia_hole)*column_t_wp
    Atg = ((number_of_row_web-1)* pitch + end_dist) * column_t_wp
    Atn = ((number_of_row_web-1)*pitch + (number_of_row_web-1)*dia_hole + end_dist) * column_t_wp

    Tdb1 = ((Avg * fy)/(math.sqrt(3) * gamma_m0)) + ((0.9 * Atn * fu) / (gamma_m1))
    Tdb2 = ((0.9 * Avn * fu) / (math.sqrt(3))) + ((Atg * fy) / gamma_m0)
    Tdbw2 = min(Tdb1, Tdb2)

    return round((Tdbw2 / 1000), 2)

########################################################################################################################
# Calculation of block shear capacity flange [Reference: Bolted field splices for steel bridge flexural\
#  members AISC - overview and design example: Design example 3.1] [link: https://www.aisc.org/globalassets/nsba/design-resources/bolted-field-splices-for-steel-bridge-flexural-members_march2017.pdf]
def flange_block_shear(end_dist, column_b, column_f_t, gauge_dist,number_of_column_flange,  pitch, dia_hole, number_of_row_flange,fy, fu):
    """
    Args:
        edge_dist: Edge/end distance in mm (Assumption: edge distance = end distance) (float)
        column_f_t: Thickness of flange in mm (float)
        column_f_tp: Thickness of flange splice plate in mm (float)
        dia_hole: Diameter of bolt hole in mm
        column_b: Width of flange in mm (float)
        gauge_dist: Gauge distance between bolts in flange in mm (float)
        fy: Characteristic yield stress in N/mm^2 (float)
        fu: Ultimate tensile stress of the material in N/mm^2 (float)
    Returns: Block shear capacity of flange splice plate in mm
    """

    gamma_m0 = 1.10
    gamma_m1 = 1.25
    Avg = 2 * (end_dist + (number_of_row_flange - 1) * pitch) * column_f_t
    Avn = 2 * (end_dist + (number_of_row_flange - 1) * pitch - (number_of_row_flange - 0.5) * dia_hole) * column_f_t
    Atg = (column_b - (number_of_column_flange - 1) * gauge_dist) * column_f_t
    Atn = (column_b - ((number_of_column_flange - 1) * gauge_dist) - (number_of_column_flange - 1) * dia_hole) * column_f_t

    Tdb1 = 2 * (((Avg * fy) / (math.sqrt(3) * gamma_m0)) + ((0.9 * Atn * fu) / (gamma_m1)))
    Tdb2 = 2 * (((0.9 * Avn * fu) / (math.sqrt(3))) + ((Atg * fy) / gamma_m0))
    Tdb_f = min(Tdb1, Tdb2)

    return round((Tdb_f / 1000), 2)



# Calculation of block shear capacity of outer flange splice plate [Reference: Bolted field splices for steel bridge flexural\
#  members AISC - overview and design example: Design example 3.1] [link: https://www.aisc.org/globalassets/nsba/design-resources/bolted-field-splices-for-steel-bridge-flexural-members_march2017.pdf]
def outerflange_plate_block_shear(end_dist, column_f_tp, gauge_dist, number_of_column_flange,  pitch, dia_hole, number_of_row_flange,fy, fu):

    gamma_m0 = 1.10
    gamma_m1 = 1.25
    Avg = 2 * (end_dist + (number_of_row_flange - 1) * pitch) * column_f_tp
    Avn = 2 * (end_dist + (number_of_row_flange - 1) * pitch - (number_of_row_flange - 0.5) * dia_hole) * column_f_tp
    Atg = ((number_of_column_flange - 1) * gauge_dist) * column_f_tp
    Atn = (((number_of_column_flange - 1) * gauge_dist) - (number_of_column_flange - 1) * dia_hole) * column_f_tp

    Tdb1 = 2 * (((Avg * fy) / (math.sqrt(3) * gamma_m0)) + ((0.9 * Atn * fu) / (gamma_m1)))
    Tdb2 = 2 * (((0.9 * Avn * fu) / (math.sqrt(3))) + ((Atg * fy) / gamma_m0))
    Tdb_fp = min(Tdb1, Tdb2)

    return round((Tdb_fp / 1000), 2)

def innerflange_plate_block_shear(edge_dist, end_dist, column_f_itp, pitch, number_of_row_flange, number_of_column_flange, gauge_dist, dia_hole, flange_width, fy, fu):
#Flange splice plate block shear for inner flange splice plate
#pattern 1
    gamma_m0 = 1.10
    gamma_m1 = 1.25
    Avg = (end_dist + (number_of_row_flange - 1) * pitch)  * column_f_itp
    Avn = (end_dist + (number_of_row_flange - 1)*pitch - (number_of_row_flange- 0.5)*dia_hole) * column_f_itp
    Atg = (edge_dist + (number_of_column_flange - 1)*gauge_dist) * column_f_itp
    Atn = (edge_dist + (number_of_column_flange - 1)*gauge_dist - (number_of_column_flange - 0.5) * dia_hole) * column_f_itp

    Tdb1 = 2 * (((Avg * fy) / (math.sqrt(3) * gamma_m0)) + ((0.9 * Atn * fu) / (gamma_m1)))
    Tdb2 = 2 * (((0.9 * Avn * fu) / (math.sqrt(3))) + ((Atg * fy) / gamma_m0))
    Tdb_ifp = min(Tdb1, Tdb2)
    return round((Tdb_ifp / 1000), 2)

#pattern 2
    gamma_m0 = 1.10
    gamma_m1 = 1.25
    Avg = 2 * (end_dist + (number_of_row_flange - 1) * pitch) * column_f_tp
    Avn = 2 * (end_dist + (number_of_row_flange - 1) * pitch - (number_of_row_flange - 0.5) * dia_hole) * column_f_tp
    Atg = ((number_of_column_flange - 1) * gauge_dist) * column_f_tp
    Atn = (((number_of_column_flange - 1) * gauge_dist) - (number_of_column_flange - 1) * dia_hole) * column_f_tp
    Tdb1 = 2 * (((Avg * fy) / (math.sqrt(3) * gamma_m0)) + ((0.9 * Atn * fu) / (gamma_m1)))
    Tdb2 = 2 * (((0.9 * Avn * fu) / (math.sqrt(3))) + ((Atg * fy) / gamma_m0))
    Tdb_ifp = min(Tdb1, Tdb2)

    return round((Tdb_ifp / 1000), 2)


########################################################################################################################
# Check for shear yielding of web splice plate (Clause 8.4.1, IS 800 : 2007)
def shear_yielding(A_v, column_fy):
    """
    Args:
        A_v: Total cross sectional area in shear in mm^2 (float)
        column_fy: Characteristic yield stress in N/mm^2 (float)
    Returns: Strength of web splice plate under shear yielding (kN) ----> (float)
    """
    gamma_m0 = 1.10
    V_d = (A_v * column_fy) / (math.sqrt(3) * gamma_m0 * 1000) # kN
    return round(V_d, 2)

########################################################################################################################
# Check for shear rupture of web splice plate (Clause 8.4.1, IS 800 : 2007)
def shear_rupture(column_fu,web_plate_w,n_bolts,dia_hole,web_plate_t):
    """
    Args:
        A_vn: net effective area of web cover plate attacted to web in mm^2 (float)
        column_fy: Characteristic yield stress in N/mm^2 (float)
    Returns: Strength of web splice plate under shear yielding (kN) ----> (float)
    """
    gamma_m1 = 1.25
    A_vn = (web_plate_w - n_bolts * 2 * dia_hole) * web_plate_t
    R_n = (0.9 * A_vn * column_fu) / (math.sqrt(3) * gamma_m1 * 1000) # kN
    return round(R_n, 2)
########################################################################################################################
########################################################################################################################
# Calculation of cross center gauge of flange
# '''
#            <--  gauge  --->
#            |     (g)      |
#           +-+            +-+
#     +----------------------------+
#     +----------------------------+
#     +     +-+     ||     +-+
#                   ||      ^
#                   || webmaxh     +----Bolt+
#                   ||
#                   ||
#                   ||
#                   ||
#                   ||
#                   ||
#                   ||
#           +-+     ||     +-+
#     +----------------------------+
#     +----------------------------+
#           +-+            +-+
#
# '''

########################################################################################################################
def fetchColumnPara(self):
    column_section = self.ui.combo_columnSec.currentText()
    dictcolumndata = get_columndata(column_section)
    return dictcolumndata

########################################################################################################################
# Start of main program


def coverplateboltedconnection(uiObj):
    global logger
    logger = logging.getLogger("osdag.cover_plate_bolted_calc")
    global design_status
    design_status = True

    print(uiObj)
    connectivity = uiObj["Member"]["Connectivity"]
    column_section = uiObj["Member"]["ColumnSection"]
    column_fu = float(uiObj["Member"]["fu (MPa)"])
    column_fy = float(uiObj["Member"]["fy (MPa)"])

    axial_force = float(uiObj["Load"]["AxialForce"])
    moment_load = float(uiObj["Load"]["Moment (kNm)"])
    shear_load = float(uiObj["Load"]["ShearForce (kN)"])
    # if shear_load == '':
    #     shear_load = 0
    # else:
    #     shear_load = float(uiObj["Load"]["ShearForce"])

    bolt_diameter = int(uiObj["Bolt"]["Diameter (mm)"])
    bolt_grade = float(uiObj["Bolt"]["Grade"])
    bolt_type = (uiObj["Bolt"]["Type"])
    flange_plate_preference = uiObj['FlangePlate']['Preferences']
    gap = float(uiObj["detailing"]["gap(mm)"]) # gap between web  plate and column flange

    mu_f = float(uiObj["bolt"]["slip_factor"])
    dp_bolt_hole_type = str(uiObj["bolt"]["bolt_hole_type"])
    dia_hole = int(uiObj["bolt"]["bolt_hole_clrnce"]) + bolt_diameter
    bolt_fu = float(uiObj["bolt"]["bolt_fu"])
    type_edge = str(uiObj["detailing"]["typeof_edge"])
    web_plate_t = float(uiObj['WebPlate']['Thickness (mm)'])
    web_plate_w = str(uiObj['WebPlate']['Width (mm)'])
    flange_plate_t = float(uiObj["FlangePlate"]["Thickness (mm)"])
    flange_plate_w = float(uiObj["FlangePlate"]["Width (mm)"])
    # if flange_plate_w == '':
    #     flange_plate_w = 0
    # else:
    #     flange_plate_w = float(flange_plate_w)

    flange_plate_l = str(uiObj["FlangePlate"]["Height (mm)"])
    flange_plate_l = float(flange_plate_l)

    # if flange_plate_l == '':
    #     flange_plate_l = 0
    # else:
    #     flange_plate_l = float(flange_plate_l)

    # flange_plate_fu = float(uiObj["Member"]["fu (Mpa)"])
    # flange_plate_fy = float(uiObj["Member"]["fy (MPa)"])
    flange_plate_fu = column_fu
    flange_plate_fy = column_fy


    # if web_plate_w == '':s
    #     web_plate_w = 0
    # else:
    #web_plate_w = float(web_plate_w)

    web_plate_w = str(uiObj["WebPlate"]["Width (mm)"])
    web_plate_w = float(web_plate_w)
    # if web_plate_w == '':
    #     web_plate_w = 0
    # else:
    #web_plate_w = round((web_plate_w), 2)

    web_plate_l = str(uiObj["FlangePlate"]["Height (mm)"])
    web_plate_l = float(web_plate_l)

    # if web_plate_l == '':
    #     web_plate_l = 0
    # else:


    web_plate_fu = float(column_fu)
    web_plate_fy = float(column_fy)

    old_column_section = get_oldcolumncombolist()

    if column_section in old_column_section:
        logger.warning(" : You are using a section (in red color) that is not available in latest version of IS 808")
    if column_fu < 410 or column_fy < 230:
        logger.warning(" : You are using a section of grade that is not available in latest version of IS 2062")

    ########################################################################################################################
    # Read input values from Column  database

    dictcolumndata = get_columndata(column_section)

    column_t_w = float(dictcolumndata["tw"])
    column_f_t = float(dictcolumndata["T"])
    column_d = float(dictcolumndata["D"])

    column_r1 = float(dictcolumndata["R1"])
    column_b = float(dictcolumndata["B"])
    column_area = float(dictcolumndata["Area"])


    ########################################################################################################################

    # Input for plate dimensions (for optional inputs) and validation

    # Check for web plate thickness
    gamma_m0 = 1.1
    #webmint = float(web_min_t( shear_load, column_d, gamma_m0, column_fy))
    #if web_plate_t < web_min_t( shear_load, column_d, gamma_m0, column_fy)
    gamma_m0  = 1.1
    # a = web_max_t(bolt_diameter)
    if web_plate_t < float(column_t_w / 2):  ## Web plate thickness = web plate 1 thickness = (thickness of web / 2)
        min_web_t = float(math.sqrt(3) * (gamma_m0 * shear_load) / (0.6 * column_d * column_fy))
        web_opt_thk = max(min_web_t, (column_t_w / 2))
        # print (web_opt_thk)
        # print(logger)
        # # web_opt_thk = web_plate_t
        # web_plate_t = web_opt_thk
        # web_plate_t = web_opt_thk
        design_status = False
        logger.error(": Chosen web splice plate thickness is not sufficient")
        logger.warning(": Minimum required thickness of web splice plate is %2.2f mm" % (web_opt_thk))
        logger.info(": Increase the thickness of web splice plate")

    elif web_plate_t > web_max_t(bolt_diameter):
        # print (a)
        # print (web_plate_t)
        # print(logger)
        design_status = False
        logger.error(": Thickness of web splice plate is greater than the maximum thickness")
        # logger.warning(": Maximum allowed thickness of web splice plate is %2.2f mm" % (a))
        # logger.info(": Decrease the thickness of web splice plate")

    else:
        pass

    # Web splice plate width input and check for maximum and minimum values #todo
    if flange_plate_preference == "Outside":
        webmaxw = web_max_w( column_d, column_f_t, column_r1)
    elif flange_plate_preference == "Outside + Inside":
        webmaxw = web_max_w(column_d, column_f_t, column_r1) - flange_plate_t
    #
    else:
        pass

    minwebw = float(web_min_w(column_d))
    # if web_plate_w != 0:

    if web_plate_w > webmaxw:
        design_status = False
        logger.error(": Width  of web splice plate is greater than the clear depth of column")
        logger.warning(": Maximum web splice plate width allowed is %2.2f mm" % (webmaxw))
        logger.info(": Reduce the width of web splice plate")

        # else:
        #     pass

    elif minwebw > webmaxw: #TODO is this conditiom is imp??
        design_status = False
        logger.error(": Minimum Width  of web splice plate is more than the clear depth of the column")
        logger.warning(": Width  of web splice plate should be greater than %2.2f mm" % (minwebw))
        logger.warning(": Allowed Width  of web splice plate is %2.2f mm" % (webmaxw))
        logger.info(": Increase the Width  of web splice plate")

    elif web_plate_l < minwebw:
        design_status = False
        logger.error(": Width of web splice plate is less than the required minimum height as specified in Steel Designer's Manual")
        logger.warning(": Width of web splice plate should be greater than %2.2f mm" % (minwebw))
        logger.info(": Increase the Width of web splice plate")

    else:
        pass

    # Width of flange splice plate (maximum and minimum values)
    if flange_plate_preference == "Outside":
        # if flange_plate_w != 0:
            if flange_plate_w < (column_b - 2 * 10): # AISC Essential detailing requirements for a splice --> B - Half inch on both sides
                # Note: half inch (0.5 inch) = 12.7 mm
                flangeplatewidth = round(column_b - (2 * 10) , 2)
                design_status = False
                logger.error(": Width of flange splice plate is not sufficient")
                logger.warning(": Minimum width of flange splice plate is restricted to %2.2f mm" % (flangeplatewidth))
                logger.info(": Increase the width of flange splice plate")

            elif flange_plate_w > column_b:
                flangeplatewidth = round(column_b, 2)
                design_status = False
                logger.error(": Width of flange splice plate is greater than the maximum width as mentioned in AISC")
                logger.warning(": Maximum width of flange splice plate is restricted to %2.2f mm" % (flangeplatewidth))
                logger.info(": Decrease the width of flange splice plate")

            else:
                pass

    elif flange_plate_preference == "Outside + Inside":
        # if flange_plate_w != 0:
            if flange_plate_w < float(column_b - 2 * 10):  # AISC Essential detailing requirements for a splice --> B - Half inch on both sides
                # Note: half inch (0.5 inch) = 12.7 mm
                flangeplatewidth = round(column_b - (2 * 10), 2)
                design_status = False
                logger.error(": Width of outer flange splice plate is not sufficient")
                logger.warning(": Minimum width of outer flange splice plate is restricted to %2.2f mm" % (flangeplatewidth))
                logger.info(": Increase the width of outer flange splice plate")

            elif flange_plate_w > column_b:
                flangeplatewidth = round(column_b, 2)
                design_status = False
                logger.error(": Width of outer flange splice plate is greater than the maximum width as mentioned in AISC")
                logger.warning(": Maximum width of outer flange splice plate is restricted to %2.2f mm" % (flangeplatewidth))
                logger.info(": Decrease the width of outer flange splice plate")

            else:
                pass

    else:
        pass

# Calculation of Width of outer flange splice plate
#     if flange_plate_preference == "Outside":
#         if flange_plate_w != 0:
#             flange_plate_w = flange_plate_w
#
#         elif flange_plate_w == 0:
#             flange_plate_w = column_b
#
#     elif flange_plate_preference == "Outside + Inside":
#         if flange_plate_w != 0:
#             flange_plate_w = flange_plate_w
#
#         elif flange_plate_w == 0:
#             flange_plate_w = column_b
#     else:
#         pass




    def boltdesignweb (web_plate_l, flange_plate_w, flange_plate_l, flange_plate_t,web_t_thinner):
        # Bolt fu and fy calculation
        # bolt_fu = int(bolt_grade) * 100
        bolt_fy = (bolt_grade - int(bolt_grade)) * bolt_fu
        print(bolt_fu)
        # Minimum pitch and gauge
        min_pitch = int(2.5 * bolt_diameter)
        min_gauge = int(2.5 * bolt_diameter)


        # Minimum and maximum end and edge distance
        if uiObj["detailing"]["typeof_edge"] == str("a - Sheared or hand flame cut"):
            min_end_dist = int(float(1.7 * dia_hole))
        else:
            min_end_dist = int(float(1.5 * dia_hole))
        min_edge_dist = min_end_dist

        # Calculation of kb
        kbChk1 = min_end_dist / float(3 * dia_hole)
        kbChk2 = min_pitch / float(3 * dia_hole) - 0.25
        kbChk3 = bolt_fu / float(column_fu)
        kbChk4 = 1
        kb = float(min(kbChk1, kbChk2, kbChk3, kbChk4))
        kb = round(kb, 3)

        # Bolt capacity calculation for web splice

        web_t_thinner = min(column_t_w, web_plate_t)
        web_bolt_planes = 1
        number_of_bolts = 1
        if bolt_type == "Bearing Bolt":
            web_bolt_shear_capacity = round(ConnectionCalculations.bolt_shear(bolt_diameter, web_bolt_planes, bolt_fu), 2)
            web_bolt_bearing_capacity = round(ConnectionCalculations.bolt_bearing(bolt_diameter, number_of_bolts, web_t_thinner,\
                                                                            kb, web_plate_fu), 2)
            web_bolt_capacity = min(web_bolt_shear_capacity,web_bolt_bearing_capacity)

        elif bolt_type == "Friction Grip Bolt":
            muf = mu_f
            bolt_hole_type = dp_bolt_hole_type  # 1 for standard, 0 for oversize hole
            n_e = 2  # number of effective surfaces offering frictional resistance
            web_bolt_shear_capacity = round(ConnectionCalculations.bolt_shear_friction_grip_bolt(bolt_diameter, bolt_fu, muf, n_e, bolt_hole_type), 2)
            web_bolt_bearing_capacity = 'N/A'
            web_bolt_capacity = web_bolt_shear_capacity

            print(web_bolt_bearing_capacity, web_bolt_shear_capacity, web_bolt_capacity)
        else:
            pass


        # Bolt capacity calculation for flange splice
        if flange_plate_preference == "Outside":
            flange_t_thinner = min(column_f_t, flange_plate_t)
        else:
            flange_t_thinner = min(column_f_t, (2 * flange_plate_t))

        number_of_bolts = 1
        if bolt_type == "Bearing Bolt":
            flange_bolt_shear_capacity = round(ConnectionCalculations.bolt_shear(bolt_diameter, number_of_bolts, bolt_fu), 2)
            flange_bolt_bearing_capacity = round(ConnectionCalculations.bolt_bearing(bolt_diameter, number_of_bolts, flange_t_thinner, \
                                                                                kb, int(flange_plate_fu)), 2)

            flange_bolt_capacity = min(flange_bolt_shear_capacity, flange_bolt_bearing_capacity)

        elif bolt_type == "Friction Grip Bolt":
            muf = mu_f
            bolt_hole_type = dp_bolt_hole_type  # 1 for standard, 0 for oversize hole
            n_e = 1  # number of effective surfaces offering frictional resistance
            flange_bolt_shear_capacity = round(ConnectionCalculations.bolt_shear_friction_grip_bolt(bolt_diameter, bolt_fu, muf, n_e,
                                                                                 bolt_hole_type), 2)

            flange_bolt_bearing_capacity = 'N/A'
            flange_bolt_capacity = flange_bolt_shear_capacity

            print(flange_bolt_bearing_capacity, flange_bolt_shear_capacity, flange_bolt_capacity)

         # else:
         #     pass

        # Maximum pitch and gauge distance for web splice plate
        max_pitch = int(min((32 * web_t_thinner), 300))
        max_gauge = int(min((32 * web_t_thinner), 300))

        # Maximim pitch and gauge distance for flange splice plate
        max_pitch_flange = int(min((32.0 * flange_t_thinner), 300))
        max_gauge_flange = int(min((32 * flange_t_thinner), 300))

    # Calculation of number of bolts required for web splice plate
        if shear_load != 0:
            web_bolts_required = float(math.ceil(shear_load/ web_bolt_capacity))
        else:
            web_bolts_required = 2

 # Calculation of axial capacity
        if axial_force == 0:
            axial_capacity = float((0.3* column_area * column_fy)/ gamma_m0)
        else:
            pass

# Calculation of number of bolts required for flange splice plate
    #### 1. No. of bolts along column length; connecting each column = 1.05 * Force in flange [Reference: Annex F, Clause 10.6.1, F-2.2, Page 130]
        ff = flange_force(column_d, column_f_t,column_b,column_area, axial_force, moment_load)
        if ff != 0:
            flange_bolts_required = int(math.ceil((ff/ flange_bolt_capacity)))
        else:
            flange_bolts_required = 2

# From practical considerations, minimum number of bolts required for web splice plate is  [Reference: ML Gambhir page 10.84]
        if web_bolts_required > 0 and web_bolts_required <= 1:
            web_bolts_required = 2

    # number_of_rows_web = web_bolts_required

# Number of bolts in even number (for design of flange splice plate)
        if flange_bolts_required % 2 == 0:
            flange_bolts_required = flange_bolts_required
        else:
            flange_bolts_required = flange_bolts_required + 1


        #flange_bolts_required
# # Number of rows of bolts in flange splice

#
#
#     '''
#     ASCII Diagram to represent flange splice plate
#                     row 1                 row 4   Gap between beams
#                   +---->                  +-->   ++-----+

#                   |                       |      ||
#     +--------+----|-----------------------|------||-----------------------------------+---------+
#     |        |    +                       |      vv                                   |         |
#     |        |                            |      ||                                   |         |
#     |        |    +       +       +       +      ||    +       +       +       +      |         |
#     |        |                                   ||                                   |         |
#     |        |                                   ||                                   |         |
#     |        |                                   ||                   ++-+            |         |
#     |        |    +       +       +       +      ||    +       +      |+ |     +      |         |
#     |        |                                   ||                   +--v            |         |
#     |   ^    |            ^                      ||                      |            |         |
#     +---|----+------------|--------------- ------++----------------------|------------+---------+
#         |                 |                                              | Bolt
#         | Beam            |Flange splice plate                           +------+
#         +-----+           +--------+
#                            In the above diagram total number of bolts along one side of beam is 8
#                              number of rows = 8/2 = 4
#     '''

        # boltparameters = boltdesignweb(web_plate_l, flange_plate_w, flange_plate_l, flange_plate_t, web_t_thinner)
        edge_distance =50
        number_of_rows_flange = flange_bolts_required / 2
        total_web_plate_bolts = web_bolts_required * 2
        total_flange_plate_bolts = flange_bolts_required * 4
        number_of_column_flange = column_b - 2 * column_f_t - 2 * column_r1 - 2 * edge_distance




    # Calculation of bolt group capacity for web splice plate
        web_bolt_group_capcity = web_bolts_required * web_bolt_capacity

    # Calculation of bolt group capacity for flange splice plate
        flange_bolt_group_capacity = flange_bolts_required * flange_bolt_capacity


        max_pitch = int(min((32 * web_t_thinner), 300))
        max_gauge = int(min((32 * web_t_thinner), 300))

    # Roundup pitch and end distances as a whole number in the multiples of 10
        if min_pitch % 10 != 0 or min_gauge % 10 != 0:
            min_pitch = int(min_pitch / 10) * 10 + 10
            min_gauge = int(min_pitch / 10) * 10 + 10
        else:
            min_pitch = min_pitch + 10
            min_gauge = min_gauge + 10

    # Roundup end and edge distances as a whole number in the multiples of 10
        if min_end_dist % 10 != 0:
            min_end_dist = int(min_end_dist / 10) * 10 + 10
            min_edge_dist = int(min_edge_dist / 10) * 10 + 10
        else:
            min_end_dist = min_end_dist
            min_edge_dist = min_end_dist



##########################################################################################################################################################
   #flange cover plate details (height,width,thickness)



    # def validation_input(max_value,min_value, user_input, parameter):
    #     if  user_input < max_value and user_input > min_value:
    #         design_status = False
    #         #logger.error(": Chosen range of flange splice plate is not sufficient")
    #         logger.warning("Please enter in the range { } to { }".format(parameter,max_value, min_value))
    #         #logger.info(": Increase the height of flange splice plate")
    #     else:
    #         pass
    #     return design_status
    #
    # flange_plate_l = validation_input(max_h, max)



    # Pitch calculation for a user given height of web splice plate
        if web_plate_l != 0:
            length_avail = (web_plate_l - 2 * min_edge_dist )
            web_pitch = round(length_avail / (web_bolts_required - 1), 3)

    # Case : When there is no user input for height of web splice plate

            #minwebw = web_min_w(column_d)
        elif web_plate_l == 0:
    # Consider web splice plate equal to minimum required height of web splice plate & calc pitch

            web_plate_l_opt = web_min_w(column_d)
            web_pitch = int(round((((web_plate_l_opt - (2 * min_end_dist)) / (web_bolts_required - 1)) / 5)) * 5 + 5)
            web_plate_l = round(int(web_pitch * (web_bolts_required - 1) + (2 * min_end_dist)), 2)

        else:
            pass

    ## In the above case if "pitch < requ_web_t
    ## In the above case if "pitch < required min pitch" then recalculate height of web splice plate
        #minwebw = web_min_w(column_d)
        if web_pitch <= min_pitch:
            web_plate_l_opt = (web_bolts_required - 1) * min_pitch + 2 * min_end_dist
            web_pitch = min_pitch


        elif web_pitch >= max_pitch:
            web_plate_l_opt = (web_bolts_required - 1) * max_pitch + 2 * min_end_dist
            web_pitch = max_pitch
            web_plate_l = web_plate_l_opt
        # web_plate_l = web_plate_l_opt

        else:
             pass


# Recalculate pitch if height of web splice plate is greater than maximum height of web splice plate

        if web_plate_l > webmaxw:
            web_plate_l_opt = web_max_w(column_d, column_f_t, column_r1)
            web_pitch = (web_plate_l_opt - 2 * min_end_dist) / (web_bolts_required - 1)

        else:
             pass



# # Calculation of height of flange splice plate (When user doesn't specify the value)
#
#     '''
#     ASCII Diagram to represent length and height of flange splice plate
#              <----------------length = (2 * Ltp) + Gap------------------>
#              +----------------------------++----------------------------+  ^
#              |                            ||                            |  |
#              |   +        +       +       ||    +         +       +     |
#              |                            ||                            | width
#              |   +        +       +       ||    +         +       +     |
#              |                            ||                            |  |
#              +----------------------------++----------------------------+  v
#                                           ||
#              <---------+  Ltp  +--------->||<---------+  Ltp  +--------->
#                                          Gap
#                                           vv
#     '''


    # Calculation of length of outer flange splice plate (optional input)
        Ltp = (2 * min_end_dist) + (min_pitch * (number_of_rows_flange - 1))
        if Ltp < max(column_b, 225): # Note: Ltp > 225 mm and Ltp > width of column
            Ltp = max(column_b, 225)
        else:
            pass



        flange_plate_l_opt = (2 * Ltp)
    # Calculation of length of inner flange splice plate (optional input)
        Ltpi = (2 * min_end_dist) + (min_pitch * (number_of_rows_flange - 1))
        if Ltp < max(column_b, 225):  # Note: Ltp > 225 mm and Ltp > width of column
            Ltp = max(column_b, 225)
        else:
            pass
        flange_plate_l_opt = (2 * Ltp)


    #### 1. Check if Ltp > width of column (column_b) and 225 mm ; Note: refer above ASCII diagram
        ## Reference: Steel Designer's Manual - SCI - 6th edition, page 754
        if flange_plate_l != 0:
            Ltp_input = (flange_plate_l) / 2
            if Ltp_input < Ltp:
                design_status = False
                logger.error(": Chosen height of flange splice plate is not sufficient")
                logger.warning(": Minimum required height of flange splice plate is %2.2f" % (flange_plate_l_opt))
                logger.info(": Increase the height of flange splice plate")
            else:
                pass

            if number_of_rows_flange > 1:
                flange_plate_l = flange_plate_l
                flange_pitch = round((Ltp_input - (2 * min_end_dist)) /(number_of_rows_flange - 1), 2)

            else:
                design_status = False
                logger.error(": Chosen height of flange splice plate is not sufficient")
                logger.warning(": Minimum required height of flange splice plate is %2.2f" % (flange_plate_l_opt))
                logger.info(": Increase the height of flange splice plate")

        flange_gauge = flange_pitch
        if flange_plate_l == 0:
            flange_plate_l = flange_plate_l_opt
            if number_of_rows_flange > 1:
                flange_pitch = int(Ltp - (2 * min_end_dist)) / int(number_of_rows_flange - 1)
                if flange_pitch % 10 != 0:
                    flange_pitch = int(flange_pitch / 10) * 10 + 10
                else:
                    flange_pitch = flange_pitch + 10

                Ltp11 = (2 * min_end_dist) + (flange_pitch * (number_of_rows_flange - 1))
                flange_plate_l = (2 * Ltp11)
            else:
                flange_pitch = 0

        else:
            pass
        flange_gauge = flange_pitch
    #flange_pitch = flange_gauge

    # Calculation of minimum web plate thickness and maximum end/edge distance

        if web_plate_l != 0:
            web_min_t = math.sqrt(3) * (gamma_m0 * shear_load) / (0.6 * column_d * column_fy)
            max_end_distance = int((12 * web_min_t * math.sqrt(250 / column_fy)).real)
            web_opt_thk = max(web_min_t, (column_t_w / 2 ))
            max_edge_distance = max_end_distance
            # if web_plate_t < web_min_t:
            #     design_status = False
            #     logger.error(": Chosen web splice plate thickness is not sufficient")
            #     logger.warning(": Minimum required thickness of web splice plate is %2.2f mm" % (web_opt_thk))
            #     logger.info(": Increase the thickness of web splice plate")

        elif web_plate_l == 0:
            web_min_t = (math.sqrt(3) * (gamma_m0 * shear_load)) / (column_fy * web_plate_l_opt)
            web_opt_thk = max(web_min_t, (column_t_w/2))
            max_end_distance = int((12 * web_min_t * math.sqrt(250 / column_fy)).real)
            max_edge_distance = max_end_distance

        ################################################################################################################

    # Calculation of resultant force on bolts in web

        def res_shear_bolt(mu_w, shear_load, ecc, extreme_bolt_dist,n_c,number_of_rows_web, number_of_column_web, end_dist, ltp, pitch_web, r_i, x, y, i):

            ecc = (ltp - 2 * end_dist)/2
            sigma_x = (number_of_rows_web - (2 * i - 1) * gauge_web) / 2
            sigma_y = (number_of_column_web - (2 * i -1) * pitch_web) / 2
            r_i = sigma_x.sq + sigma_y.sq
            hor_shear_force_bolts = ((mu_w + shear_load * ecc)*  extreme_bolt_dist) / r_i       #horizontal shear force acting on each bolt due to moment developed by eccentricity.
            # extreme bolt distance in X direction
            ver_shear_force_bolts = ((mu_w + shear_load * ecc)*  extreme_bolt_dist) / r_i       #vertical shear force acting on each bolt due to moment developed by eccentricity
            # extreme bolt distance in Y direction
            hor_force = shear_load/number_of_bolts
            area_web = (column_d -2* column_f_t) * column_t_w
            axial_force_web = (axial_force * area_web) / column_area                            #horizontal force acting on each bolt (assuming uniform shear distribution)
            ver_force = axial_force_web /number_of_bolts                                        #vertical force acting on each bolt (assuming uniform axial distribution)
            shearresbolt = math.sqrt((hor_shear_force_bolts + hor_force).sq + ( ver_shear_force_bolts + ver_force).sq)

            if shearresbolt > web_bolt_capacity:
                design_status = False
                logger.error(": Number of bolts is not sufficient")
                logger.warning(": shear_res_bolt should be less than web_bolt_capacity of web")
                logger.info(": Increase number of bolts and spacing between bolts")
            else:
                pass

            return res_shear_bolt

        ################################################################################################################


        # Fetch bolt design output parameters dictionary

        # if web_plate_l == 0 and flange_plate_l == 0 and flange_plate_w == 0:
        boltParam = {}
        #outputObj['Bolt']['status'] = design_status
        boltParam["ShearCapacity"] = web_bolt_shear_capacity
        boltParam["BearingCapacity"] = web_bolt_bearing_capacity
        boltParam["CapacityBolt"] = web_bolt_capacity
        boltParam["BoltsRequired"] = web_bolts_required
        boltParam["TotalBoltsRequired"] = total_web_plate_bolts
        boltParam["Pitch"] = web_pitch
        boltParam["End"] = min_end_dist
        boltParam["Edge"] = min_edge_dist
        boltParam["WebPlateHeight"] = web_plate_l
        boltParam["WebGauge"] = min_gauge
        boltParam["WebGaugeMax"] = max_gauge
        boltParam["webPlateDemand"] = shear_load

        boltParam["ShearCapacityF"] = flange_bolt_shear_capacity
        boltParam["BearingCapacityF"] = flange_bolt_bearing_capacity
        boltParam["CapacityBoltF"] = flange_bolt_capacity
        boltParam["BoltsRequiredF"] = flange_bolts_required # Note: This outputs number of bolts required in one side of splice
        boltParam["TotalBoltsRequiredF"] = total_flange_plate_bolts
        boltParam["NumberBoltColFlange"] = number_of_rows_flange
        boltParam["PitchF"] = flange_pitch
        boltParam["EndF"] = min_end_dist
        boltParam["EdgeF"] = min_edge_dist
        boltParam["FlangePlateHeight"] = flange_plate_l
        boltParam["FlangePlateWidth"] = flange_plate_w
        boltParam["FlangePlateDemand"] = flange_force(column_d, column_f_t,column_b,column_area, axial_force, moment_load)
        boltParam['MaxPitchF'] = max_pitch_flange
        boltParam["FlangeTThinner"] = flange_t_thinner
        boltParam["WebTThinner"] = web_t_thinner
        boltParam["WebPlateWidth"] = web_plate_w

        boltParam["Resultantforce"] = res_shear_bolt

        # bolt parameters required for calculation
        boltParam["bolt_fu"] = bolt_fu
        boltParam["bolt_fy"] = bolt_fy
        boltParam["dia_hole"] = dia_hole
        boltParam["kb"] = kb
        return boltParam
            # else:
            #     boltParam = {}
            # 	# outputObj['Bolt']['status'] = design_status
            #     boltParam["ShearCapacity"] = web_bolt_shear_capacity
            #     boltParam["BearingCapacity"] = web_bolt_bearing_capacity
            #     boltParam["CapacityBolt"] = web_bolt_capacity
            #     boltParam["BoltsRequired"] = web_bolts_required
            #     boltParam["TotalBoltsRequired"] = total_web_plate_bolts
            #     boltParam["Pitch"] = web_pitch
            #     boltParam["End"] = min_end_dist
            #     boltParam["Edge"] = min_edge_dist
            #     boltParam["WebPlateHeight"] = web_plate_l
            #     boltParam["WebGauge"] = min_gauge
            #     boltParam["FlangeGauge"] = min_gauge
            #     boltParam["WebGaugeMax"] = max_gauge
            #     boltParam["webPlateDemand"] = shear_load
            #
            #     boltParam["ShearCapacityF"] = flange_bolt_shear_capacity
            #     boltParam["BearingCapacityF"] = flange_bolt_bearing_capacity
            #     boltParam["CapacityBoltF"] = flange_bolt_capacity
            #     boltParam["BoltsRequiredF"] = flange_bolts_required  # Note: This outputs number of bolts required in one side of splice
            #     boltParam["TotalBoltsRequiredF"] = total_flange_plate_bolts
            #     boltParam["NumberBoltColFlange"] = number_of_rows_flange
            #     boltParam["PitchF"] = flange_pitch
            #     boltParam["EndF"] = min_end_dist
            #     boltParam["EdgeF"] = min_edge_dist
            #     boltParam["FlangePlateHeight"] = flange_plate_l
            #     boltParam["FlangePlateWidth"] = flange_plate_w
            #     boltParam["FlangePlateDemand"] = flange_force(column_d, column_f_t, axial_force, moment_load)
            #     boltParam['MaxPitchF'] = max_pitch_flange
            #     boltParam["FlangeTThinner"] = flange_t_thinner
            #     boltParam["Resultantforce"] = res_shear_bolt
            #
            #
            #     # bolt parameters required for calculation
            #     boltParam["bolt_fu"] = bolt_fu
            #     boltParam["bolt_fy"] = bolt_fy
            #     boltParam["dia_hole"] = dia_hole
            #     boltParam["kb"] = kb
            #     return boltParam
            # boltParam = {}
            # #outputObj['Bolt']['status'] = design_status
            # boltParam["ShearCapacity"] = web_bolt_shear_capacity
            # boltParam["BearingCapacity"] = web_bolt_bearing_capacity
            # boltParam["CapacityBolt"] = web_bolt_capacity
            # boltParam["BoltsRequired"] = web_bolts_required
            # boltParam["TotalBoltsRequired"] = total_web_plate_bolts
            # boltParam["Pitch"] = web_pitch
            # boltParam["End"] = min_end_dist
            # boltParam["Edge"] = min_edge_dist
            # boltParam["WebPlateHeight"] = web_plate_l
            # boltParam["WebGauge"] = min_gauge
            # boltParam["FlangeGauge"] = min_gauge
            # boltParam["WebGaugeMax"] = max_gauge
            # boltParam["webPlateDemand"] = shear_load
            #
            # boltParam["ShearCapacityF"] = flange_bolt_shear_capacity
            # boltParam["BearingCapacityF"] = flange_bolt_bearing_capacity
            # boltParam["CapacityBoltF"] = flange_bolt_capacity
            # boltParam["BoltsRequiredF"] = flange_bolts_required  # Note: This outputs number of bolts required in one side of splice
            # boltParam["TotalBoltsRequiredF"] = total_flange_plate_bolts
            # boltParam["NumberBoltColFlange"] = number_of_rows_flange
            # boltParam["PitchF"] = flange_pitch
            # boltParam["EndF"] = min_end_dist
            # boltParam["EdgeF"] = min_edge_dist
            # boltParam["FlangePlateHeight"] = flange_plate_l
            # boltParam["FlangePlateWidth"] = flange_plate_w
            # boltParam["FlangePlateDemand"] = flange_force(column_d, column_f_t, axial_force, moment_load)
            # boltParam['MaxPitchF'] = max_pitch_flange
            # boltParam["FlangeTThinner"] = flange_t_thinner
            # boltParam["WebTThinner"] = web_t_thinner
            # boltParam["Resultantforce"] = res_shear_bolt
            #
            #
            # # bolt parameters required for calculation
            # boltParam["bolt_fu"] = bolt_fu
            # boltParam["bolt_fy"] = bolt_fy
            # boltParam["dia_hole"] = dia_hole
            # boltParam["kb"] = kb
            # return boltParam
            # Call function for bolt design output

    web_t_thinner = min(column_t_w, web_plate_t)
    boltparameters = boltdesignweb(web_plate_l,flange_plate_w, flange_plate_l, flange_plate_t, web_t_thinner)
    print("boltparmameters", boltparameters)

    # check for long joint provisions for web splice plate [Reference: Clause 10.3.3.1, page 75, IS 800 : 2007]
    length_joint_web = (boltparameters["BoltsRequired"] - 1) * boltparameters["Pitch"]
    if length_joint_web > 15 * bolt_diameter:
        beta_lj = (1.075 - length_joint_web) / (200 * bolt_diameter)
        web_bolt_shear_capacity = beta_lj * boltparameters["ShearCapacity"]
        new_bolt_param = boltdesignweb(web_plate_l, flange_plate_w, flange_plate_l, flange_plate_t)
    else:
        new_bolt_param = boltparameters

    # check for long joint provisions for flange splice plate
    length_joint_flange = ((boltparameters["BoltsRequiredF"] / 2) - 1) * boltparameters["PitchF"]
    if length_joint_flange > 15 * bolt_diameter:
        beta_lj = (1.075 - length_joint_flange) / (200 * bolt_diameter)
        flange_bolt_shear_capacity = beta_lj * boltparameters["ShearCapacityF"]
        new_bolt_param = boltdesignweb(web_plate_l, flange_plate_w, flange_plate_l, flange_plate_t,web_t_thinner)
    else:
        new_bolt_param = boltparameters
    #####################################################################################################################

## Note: As per discussion with Prof. Siddhartha Ghosh below flange_gauge calculation is implemented on 27-July-2018
    # Minimum and maximum end and edge distance
    if uiObj["detailing"]["typeof_edge"] == str("a - Sheared or hand flame cut"):
        min_end_dist1 = int(float(1.7 * dia_hole))
    else:
        min_end_dist1 = int(float(1.5 * dia_hole))

    edge_dist = min_end_dist1
    #

    if flange_plate_preference == "Outside":
        # if flange_plate_w == 0:
        #     flange_plate_w = column_b
        #     flange_g = flange_plate_w - 2 * edge_dist
        #
        #     if flange_g < (2 * edge_dist + column_t_w):
        #         design_status = False
        #         logger.error(": Flange width available is not sufficient")
        #         # logger.warning(": Decrease the diameter of bolt")
        #         logger.info(": Try wider flange beam section or decrease bolt diameter")
        #     else:
        #         pass

        # if flange_plate_w != 0:
        #     flange_plate_w = flange_plate_w
        #     flange_g = flange_plate_w - 2 * edge_dist
        number_of_column_flange = 2
        flange_gauge = int(flange_plate_w - 2 * edge_dist - column_t_w) / (number_of_column_flange -1)
        flangeminw = flange_plate_w_min(edge_dist,flange_gauge)

        if flange_plate_w < flangeminw and flange_plate_w > column_b:
            design_status = False
            logger.error(": Flange width available is not sufficient")
            logger.warning(": width of flange should be between flangeminw and column_b")
            logger.info(": Try wider flange column section")
        else:
            pass


            # if flange_g < (2 * edge_dist + column_t_w):
            #     design_status = False
            #     logger.error(": Flange width available is not sufficient")
            #     # logger.warning(": Decrease the diameter of bolt")
            #     logger.info(": Try wider flange beam section or decrease bolt diameter")
            # else:
            #     pass

    elif flange_plate_preference == "Outside + Inside":
        # if flange_plate_w == 0:
        #     flange_plate_w = beam_b
        #     inner_flange_plate_w = (float(flange_plate_w) - 2 * (float(beam_r1)) - float(beam_w_t)) / 2
        #     flange_g = flange_plate_w - (2 * edge_dist)
        #     remaining_x = (inner_flange_plate_w - edge_dist)
        #
        #     if remaining_x < edge_dist:
        #         design_status = False
        #         logger.error(": Flange width available is not sufficient")
        #         # logger.warning(": Decrease the diameter of bolt")
        #         logger.info(": Try wider flange beam section or decrease bolt diameter")


        number_of_column_flange = column_b - 2 * column_f_t - 2 * column_r1 - 2 * edge_dist
        flange_gauge = int(flange_plate_w - 2 * edge_dist - column_t_w) / (number_of_column_flange -1)
        flange_pitch = flange_gauge
        flangeminw = flange_plate_w_min(edge_dist, flange_gauge)
        if flange_plate_w < flangeminw and flange_plate_w > column_b:
            design_status = False
            logger.error(": Flange width available is not sufficient")
            logger.warning(": width of flange should be between flangeminw and column_b")
            logger.info(": Try wider flange column section")
        else:
            pass

        inner_flange_plate_w = (float(flange_plate_w) - 2 * (float(column_r1)) - float(column_t_w)) / 2
        flange_g = flange_plate_w - (2 * edge_dist)
        number_of_column_flange = column_b - 2 * column_f_t - 2 * column_r1 - 2 * edge_dist
        min_inner_flange_plate_w = func_min_inner_flange_plate_w(edge_dist, number_of_column_flange, flange_gauge, column_t_w, column_r1)
        max_inner_flange_plate_w = func_max_inner_flange_plate_w(column_b, column_t_w, column_r1)
        if inner_flange_plate_w < min_inner_flange_plate_w and inner_flange_plate_w > max_inner_flange_plate_w:
            design_status = False
            logger.error(": Inner Flange width available is not sufficient")
            logger.warning(": Inner width of flange should be between min_inner_flange_plate_w and max_inner_flange_plate_w"% (inner_flange_plate_w))
            logger.info(": Try wider flange column section")

        else:
            pass

        # else:
        # pass

        # if flange_plate_w != 0:
        #     flange_plate_w = flange_plate_w
        #     inner_flange_plate_w = (float(flange_plate_w) - 2 * (float(beam_r1)) - float(beam_w_t)) / 2
        #     flange_g = flange_plate_w - (2 * edge_dist)
        #     remaining_x = (inner_flange_plate_w - edge_dist)
        #
        #     if remaining_x < edge_dist:
        #         design_status = False
        #         logger.error(": Flange width available is not sufficient")
        #         # logger.warning(": Decrease the diameter of bolt")
        #         logger.info(": Try wider flange beam section or decrease bolt diameter")
        #     else:
        #         pass

    inner_flange_plate_w = (float(flange_plate_w) - 2 * (float(column_r1)) - float(column_t_w)) / 2
    flange_g = flange_plate_w - (2 * edge_dist)
    #
    # Revised on 18-June-2018, Implementing new check
    ## Splice plate area > 1.05 * (Area of the flange)
    ## That is (Breath of flange plate * thickness of flange splice plate ) > 1.05 (breath of flange * thickness of flange)
    ## Implies;;;;; Thickness of flange > (1.05 (breath of flange * thickness of flange)) /  Breath of flange plate
    if flange_plate_w >= 0:
        flange_plate_w = new_bolt_param["FlangePlateWidth"]
        thkflangeplate2 = (1.05 * (column_b * column_f_t)) / new_bolt_param["FlangePlateWidth"]

    thkflangeplate = thk_flange_plate(column_d, column_f_t, bolt_diameter, column_area,  axial_force, moment_load,column_b,column_fy, dia_hole)

    flangeplatethick111 = max(thkflangeplate2, (column_f_t / 2), 10, thkflangeplate)
    flangeplatethick = round(flangeplatethick111)


    # thkflangeplate1 = max(thkflangeplate, thkflangeplate)
    if flange_plate_preference == "Outside":
        if flange_plate_t < flangeplatethick:
            # flange_plate_t = flangeplatethick
            design_status = False
            logger.error(": Chosen flange splice plate thickness is not sufficient")
            logger.warning(": Minimum required thickness of flange splice plate is %2.2f mm" % (flangeplatethick))
            logger.info(": Increase the thickness of flange splice plate")

    elif flange_plate_preference == "Outside + Inside":
        flangepthk = (flangeplatethick / 2)
        if flange_plate_t < flangepthk:
            # flange_plate_t = flangepthk
            design_status = False
            logger.error(": Chosen flange splice plate thickness is not sufficient")
            logger.warning(": Minimum required thickness of flange splice plate is %2.2f mm" % (flangepthk))
            logger.info(": Increase the thickness of flange splice plate")

    else:
        pass

    # Check for dimensions of web splice
    webmaxw = web_max_w(column_d, column_f_t, column_r1)

    if web_plate_l == 0:
        web_plate_l = new_bolt_param["WebPlateWidth"]
        if web_plate_l > webmaxw:
            design_status = False
            logger.error(": Required width of web splice plate is greater than the clear depth of column")
            logger.warning(": Maximum web splice plate width allowed is %2.2f mm" % (webmaxw))
            logger.info(": Please select deeper column  section")

        elif web_plate_l < (0.5 * column_d):
            design_status = False
            logger.error(": Required height of web splice plate is less than the minimum height as specified in Steel Designer's Manual")
            logger.warning(": Height of web splice plate should be greater than %2.2f mm" % (0.5 * column_d))
            logger.info(": Increase the diameter of bolt")

        else:
            pass


    # Revised on 15-June-2018
    # Check for the capacity of fasteners (as per experts review) [Strength of fasteners >  50% (Effective Area of flange * Fy)] [Reference: Annex F, Clause 10.6.1, F-2.2, Page 130]
    Area_flange = (column_b - (2 * dia_hole)) * column_f_t

    flange_capacity1 = (Area_flange * column_fy) / (1000 * 1.10) # kN
    bolt_strength = new_bolt_param["BoltsRequiredF"] * new_bolt_param["CapacityBoltF"]

    if bolt_strength < (0.5 * (flange_capacity1)):
        capacity_bolts = int(math.ceil((0.5 * (flange_capacity1)) / new_bolt_param["BoltsRequiredF"]))
        design_status = False
        logger.error(": Strength of fasteners is less than 50% the capacity of flange as per clause 10.6.1, Annex F, IS 800")
        logger.warning(": Bolt capacity required is %d kN" % (capacity_bolts))
        logger.info(": Reduce the size of beam section")

        # design_status = False
        # logger.error(": Strength of fasteners is less than 50% the capacity of flange as per clause 10.6.1, Annex F, IS 800")
        # logger.warning(": Bolt capacity required is %d kN" % (capacity_bolts))
        # logger.info(": Increase diameter and slip factor of the bolt")


    ## Web plate width input (optional) and validation
    if web_plate_w != 0:
        edge_distance = boltparameters["Edge"]
        min_gauge = boltparameters["WebGauge"]
        gauge_web = web_plate_w - 2 * edge_distance
        max_gauge = boltparameters["WebGaugeMax"]
        # calculation of total width of web splice plate
        ## Case 1: width is sufficient
        web_plate_w_req = gauge_web + 2 * boltparameters["Edge"]
        ## Case 2: when gauge is less than the minimum gauge

        min_web_w_gauge = min_gauge + 2 * boltparameters["Edge"] + gap
        ## Case 3: when gauge distance is less than 2 times the end distance
        ### Note: gauge_web > (End distance of one beam + end distance of other beam)
        web_plate_w_3 = 2 * edge_distance + 2 * edge_distance + gap
        ## Case 6: when gauge distance is greater than maximum gauge [min(32t, 300)]
        web_plate_w_6 = max_gauge + 2 * edge_distance + gap

        ## Case 2
        if gauge_web < min_gauge:
            # web_plate_w_req = web_plate_w
            design_status = False
            logger.error(": Chosen width for web splice plate is not sufficient")
            logger.warning(": Minimum width of web splice plate required is %2.2f mm" % (min_web_w_gauge))
            logger.info(": Increase the width of web splice plate")
        ## Case 3
        elif gauge_web < ((2 * edge_distance) + gap):
            # web_plate_w_req = web_plate_w
            design_status = False
            logger.error(": Chosen width of web splice plate is not sufficient")
            logger.warning(": Minimum width of web splice plate required is %2.2f mm" % (web_plate_w_3))
            logger.info(": Increase the width of web splice plate")
        ## Case 6
        elif gauge_web > (max_gauge + gap):
            # web_plate_w_req = web_plate_w
            design_status = False
            logger.error(": Width is greater than the maximum allowed width of web splice plate")
            logger.warning(": Maximum width of web splice plate allowed is %2.2f mm" % (web_plate_w_6))
            logger.info(": Decrease the width of web splice plate")

    elif web_plate_w == 0:
        edge_distance = boltparameters["Edge"]
        min_gauge = boltparameters["WebGauge"]
        max_gauge = boltparameters["WebGaugeMax"]
        web_plate_w_req =  4 * edge_distance + gap
        gauge_web = int(web_plate_w_req - 2 * edge_distance)
        if (2 * edge_distance) < min_gauge:
            web_plate_w_req = min_gauge + (2 * edge_distance) + gap
        # elif (2 * edge_distance) < 90:
        #     web_plate_w_req = 100 + (2 * edge_distance) + gap
        # elif (2 * edge_distance) > 140:
        #     web_plate_w_req = 140 + (2 * edge_distance) + gap
        elif (2 * edge_distance) > max_gauge:
            web_plate_w_req = max_gauge + (2 * edge_distance) + gap
        else:
            pass

    #####################################################################################################################
    # Check for shear yielding of web splice plate
    web_plate_w = boltparameters["WebPlateWidth"]
    A_v = web_plate_w * web_plate_t
    V_d = shear_yielding(A_v, column_fy)
    if V_d < shear_load:
        design_status = False
        logger.error(": Web splice plate fails in shear yielding [cl. 8.4.1] / AISC design manual")
        logger.warning(": Minimum shear yielding capacity required is  %2.2f kN" % (shear_load))
        logger.info(": Increase the thickness of web splice plate")
    else:
        pass

        #####################################################################################################################
        # Check for shear rupture of web splice plate
    web_plate_w = boltparameters["WebPlateWidth"]
    n_bolts = boltparameters["BoltsRequired"]
    A_vn = (web_plate_w - n_bolts * 2 * dia_hole) * web_plate_t
    R_n = shear_rupture(column_fu,web_plate_w,n_bolts,dia_hole,web_plate_t)
    if R_n < shear_load:
        design_status = False
        logger.error(": Web splice plate fails due to shear rupture")
        logger.warning(": Minimum shear yielding capacity required is  %2.2f kN" % (shear_load))
        logger.info(": Increase the thickness of web splice plate")
    else:
        pass

        #####################################################################################################################
        # Check for block shear capacity of web splice plate in axial
    web_t_thinner = min(web_plate_t, column_t_w)

    Tdb = web_block_shear_axial(boltparameters["WebPlateHeight"], boltparameters["Edge"], web_t_thinner,
                          boltparameters["BoltsRequired"],
                          boltparameters["dia_hole"], column_fy, column_fu)

    if Tdb < axial_force:
        design_status = False
        logger.error(": Block shear capacity of web splice plate is less than applied axial force")
        logger.warning(": Minimum block shear capacity required is %2.2f kN" % (axial_force))
        logger.info(": Increase the thickness of web splice plate")
    else:
        pass

        #####################################################################################################################
        # Check for block shear capacity of web splice plate in shear
    web_t_thinner= min(web_plate_t, column_t_w)
    Tdb = web_block_shear(boltparameters["WebPlateHeight"], boltparameters["Edge"], web_t_thinner,
                            boltparameters["BoltsRequired"], \
                            boltparameters["dia_hole"], column_fy, column_fu)

    if Tdb < shear_load:
        design_status = False
        logger.error(": Block shear capacity of web splice plate is less than applied shear force [cl. 6.4.1]")
        logger.warning(": Minimum block shear capacity required is %2.2f kN" % (shear_load))
        logger.info(": Increase the thickness of web splice plate")
    else:
        pass

    #####################################################################################################################
    # Capacity of web splice plate
    web_splice_capacity = min(Tdb, V_d, R_n)


    #####################################################################################################################
    # Check for capacity of flange splice plate
    flangecapacity = flange_capacity(column_f_t, column_b, dia_hole, column_fy)
    ff = flange_force(column_d, column_f_t,column_b,column_area, axial_force, moment_load)
    if flangecapacity < ff:
        design_status = False
        logger.error(": Flange capacity is less than force in flange")
        logger.warning(": Minimum flange capacity required is %2.2f kN" %(ff))
        logger.info(": Increase the size of beam section")
    else:
        pass

    #####################################################################################################################
    # Strength against yielding of gross section (flange splice plate)
    flangeplatewidth = boltparameters["FlangePlateWidth"]
    flangeplatethickness = flange_plate_t
    gamma_m0 = 1.10
    Tdg_flange_plate = round(((flangeplatewidth * flangeplatethickness * column_fy) / (gamma_m0 * 1000)), 2)
    if Tdg_flange_plate < ff:
        design_status = False
        logger.error(": Flange splice plate fails due to yielding of gross section")
        logger.warning(": Minimum flange splice plate capacity required is %2.2f kN" % (ff))
        logger.info(": Increase the thickness of flange splice plate")

    #####################################################################################################################
    # Strength against rupture (flange splice plate)
    net_area = (flangeplatewidth - 2 * dia_hole) * flangeplatethickness
    gamma_m1 = 1.25
    Tdn_flange_plate = round(((0.9 * net_area * flange_plate_fu) / (gamma_m1 * 1000)), 2)
    if Tdn_flange_plate < ff:
        design_status = False
        logger.error(": Flange splice plate fails due to rupture")
        logger.warning(": Minimum flange splice plate capacity required is %2.2f kN" % (ff))
        logger.info(": Increase the thickness of flange splice plate")

    #####################################################################################################################
    # Check for block shear capacity of flange splice plate
    min_thk = min(flange_plate_t, column_f_t)
    n_bolts = boltparameters["BoltsRequiredF"] / 2
    Ltp = (boltparameters["FlangePlateHeight"] - gap) / 2

    min_edge_dist = boltparameters["EdgeF"]

    Tdb_flange = outerflange_plate_block_shear( boltparameters["EndF"], min_thk, boltparameters["FlangeGauge"] , boltparameters["BoltsRequiredF"], boltparameters["PitchF"],  dia_hole,  flange_plate_fy, flange_plate_fu)

    if Tdb_flange < ff:
        design_status = False
        logger.error(": Block shear capacity of flange splice plate is less than force in flange [cl. 6.4.1]")
        logger.warning(": Minimum block shear capacity required is %2.2f kN" % (ff))
        logger.info(": Increase the thickness of flange splice plate")
    else:
        pass

    # Capacity of flange splice plate
    flange_splice_capacity = min(Tdg_flange_plate, Tdn_flange_plate, Tdb_flange)

    #####################################################################################################################
    # Check for block shear capacity of flange ##
    n_bolts = boltparameters["BoltsRequiredF"] / 2
    Ltp = (boltparameters["FlangePlateHeight"] - gap) / 2


    Tdb_columnflange = flange_block_shear(Ltp, boltparameters["EdgeF"],boltparameters["EndF"],boltparameters["FlangeGauge"], column_f_t, n_bolts, dia_hole,
                                    boltparameters["FlangePlateWidth"], column_fy, column_fu)

    if Tdb_columnflange < ff:
        design_status = False
        logger.error(": Block shear capacity of flange is less than force in flange [cl. 6.4.1]")
        logger.warning(": Minimum block shear capacity required is %2.2f kN" % (ff))
        logger.info(": Choose the higher column section")
    else:
        pass
    #####################################################################################################################

    #####################################################################################################################
    # End of calculation for design of web splice plate
    # Output
    ## When height and width of web splice plate are zero
    # if web_plate_l == 0 and web_plate_w == 0 and flange_plate_l == 0 and flange_plate_w == 0:
        outputObj = {}
        outputObj["Bolt"] = {}
        outputObj["Bolt"]["status"] = design_status

        outputObj["WebBolt"] = {}
        outputObj["WebBolt"]["ShearCapacity"] = new_bolt_param["ShearCapacity"]
        outputObj["WebBolt"]["BearingCapacity"] = new_bolt_param["BearingCapacity"]
        outputObj["WebBolt"]["CapacityBolt"] = new_bolt_param["CapacityBolt"]
        outputObj["WebBolt"]["BoltsRequired"] = new_bolt_param["BoltsRequired"]
        outputObj["WebBolt"]["TotalBoltsRequired"] = new_bolt_param["TotalBoltsRequired"]
        outputObj["WebBolt"]["Pitch"] = new_bolt_param["Pitch"]
        outputObj["WebBolt"]["End"] = new_bolt_param["End"]
        outputObj["WebBolt"]["Edge"] = new_bolt_param["Edge"]
        outputObj["WebBolt"]["WebPlateHeight"] = new_bolt_param["WebPlateHeight"]
        outputObj["WebBolt"]["WebGauge"] = gauge_web
        outputObj["WebBolt"]["WebGaugeMax"] = new_bolt_param["WebGaugeMax"]
        outputObj["WebBolt"]["webPlateDemand"] = new_bolt_param["webPlateDemand"]
        outputObj["WebBolt"]["WebPlateWidth"] = web_plate_w_req
        outputObj["WebBolt"]["WebPlateCapacity"] = web_splice_capacity

        outputObj["FlangeBolt"] = {}
        outputObj["FlangeBolt"]["ShearCapacityF"] = new_bolt_param["ShearCapacityF"]
        outputObj["FlangeBolt"]["BearingCapacityF"] = new_bolt_param["BearingCapacityF"]
        outputObj["FlangeBolt"]["CapacityBoltF"] = new_bolt_param["CapacityBoltF"]
        outputObj["FlangeBolt"]["BoltsRequiredF"] = new_bolt_param["BoltsRequiredF"] # Note: This outputs number of bolts required in one side of splice
        outputObj["FlangeBolt"]["TotalBoltsRequiredF"] = new_bolt_param["TotalBoltsRequiredF"]
        outputObj["FlangeBolt"]["NumberBoltColFlange"] = new_bolt_param["NumberBoltColFlange"]
        outputObj["FlangeBolt"]["PitchF"] = new_bolt_param["PitchF"]
        outputObj["FlangeBolt"]["EndF"] = new_bolt_param["EndF"]
        outputObj["FlangeBolt"]["EdgeF"] = edge_dist
        outputObj["FlangeBolt"]["FlangePlateHeight"] = new_bolt_param["FlangePlateHeight"]
        outputObj["FlangeBolt"]["FlangePlateWidth"] = new_bolt_param["FlangePlateWidth"]
        outputObj["FlangeBolt"]["ThicknessFlangePlate"] = flangeplatethickness
        outputObj["FlangeBolt"]["FlangeGauge"] = int(flange_g)
        outputObj["FlangeBolt"]["FlangePlateDemand"] = new_bolt_param["FlangePlateDemand"]
        outputObj["FlangeBolt"]["FlangeCapacity"] = flange_splice_capacity
        outputObj["FlangeBolt"]["edge_dist_gauge"] = edge_dist # For 3D model

        ####### For reference and validation
        outputObj["WebBolt"]["WebBlockShear"] = Tdb
        outputObj["WebBolt"]["ShearYielding"] = V_d
        outputObj["WebBolt"]["ShearRupture"] = R_n
        outputObj["FlangeBolt"]["FlangeCapacity"] = flangecapacity
        outputObj["FlangeBolt"]["Yielding"] = Tdg_flange_plate
        outputObj["FlangeBolt"]["Rupture"] = Tdn_flange_plate
        outputObj["FlangeBolt"]["FlangeBlockShear"] = Tdb_flange
        outputObj['FlangeBolt']['columnrootradius'] = column_r1
        outputObj['FlangeBolt']['columnflangethk'] = column_f_t
        outputObj['FlangeBolt']['column_fu'] = column_fu
        outputObj["FlangeBolt"]["kb"] = new_bolt_param["kb"]
        outputObj['FlangeBolt']['DiaHole'] = int(dia_hole)
        outputObj['FlangeBolt']['FlangeForce'] = ff
        outputObj['FlangeBolt']['MaxPitchF'] = new_bolt_param["MaxPitchF"]
        outputObj["FlangeBolt"]["FlangeTThinner"] = new_bolt_param["FlangeTThinner"]

        # Dimension of inner flange plate
        outputObj["FlangeBolt"]["InnerFlangePlateHeight"] = new_bolt_param["FlangePlateHeight"]
        outputObj["FlangeBolt"]["InnerFlangePlateWidth"] = inner_flange_plate_w # There will be 4 inner plates, this width is width of each plate
        outputObj["FlangeBolt"]["InnerFlangePlateThickness"] = flange_plate_t
        outputObj["FlangeBolt"]["flangeplatethick"] = flangeplatethick

    # else:
        outputObj = {}
        outputObj["Bolt"] = {}
        outputObj["Bolt"]["status"] = design_status

        outputObj["WebBolt"] = {}
        outputObj["WebBolt"]["ShearCapacity"] = new_bolt_param["ShearCapacity"]
        outputObj["WebBolt"]["BearingCapacity"] = new_bolt_param["BearingCapacity"]
        outputObj["WebBolt"]["CapacityBolt"] = new_bolt_param["CapacityBolt"]
        outputObj["WebBolt"]["BoltsRequired"] = new_bolt_param["BoltsRequired"]
        outputObj["WebBolt"]["TotalBoltsRequired"] = new_bolt_param["TotalBoltsRequired"]
        outputObj["WebBolt"]["Pitch"] = new_bolt_param["Pitch"]
        outputObj["WebBolt"]["End"] = new_bolt_param["End"]
        outputObj["WebBolt"]["Edge"] = new_bolt_param["Edge"]
        outputObj["WebBolt"]["WebPlateHeight"] = new_bolt_param["WebPlateHeight"]
        outputObj["WebBolt"]["WebGauge"] = gauge_web
        outputObj["WebBolt"]["WebGaugeMax"] = new_bolt_param["WebGaugeMax"]
        outputObj["WebBolt"]["webPlateDemand"] = new_bolt_param["webPlateDemand"]
        outputObj["WebBolt"]["WebPlateWidth"] = web_plate_w_req
        outputObj["WebBolt"]["WebPlateCapacity"] = web_splice_capacity

        outputObj["FlangeBolt"] = {}
        outputObj["FlangeBolt"]["ShearCapacityF"] = new_bolt_param["ShearCapacityF"]
        outputObj["FlangeBolt"]["BearingCapacityF"] = new_bolt_param["BearingCapacityF"]
        outputObj["FlangeBolt"]["CapacityBoltF"] = new_bolt_param["CapacityBoltF"]
        outputObj["FlangeBolt"]["BoltsRequiredF"] = new_bolt_param["BoltsRequiredF"]  # Note: This outputs number of bolts required in one side of splice
        outputObj["FlangeBolt"]["TotalBoltsRequiredF"] = new_bolt_param["TotalBoltsRequiredF"]
        outputObj["FlangeBolt"]["NumberBoltColFlange"] = new_bolt_param["NumberBoltColFlange"]
        outputObj["FlangeBolt"]["PitchF"] = new_bolt_param["PitchF"]
        outputObj["FlangeBolt"]["EndF"] = new_bolt_param["EndF"]
        outputObj["FlangeBolt"]["EdgeF"] = edge_dist
        outputObj["FlangeBolt"]["ThicknessFlangePlate"] = flangeplatethickness
        outputObj["FlangeBolt"]["FlangePlateHeight"] = new_bolt_param["FlangePlateHeight"]
        outputObj["FlangeBolt"]["FlangePlateWidth"] = new_bolt_param["FlangePlateWidth"]
        outputObj["FlangeBolt"]["FlangeGauge"] = int(flange_g)
        outputObj["FlangeBolt"]["FlangePlateDemand"] = new_bolt_param["FlangePlateDemand"]
        outputObj["FlangeBolt"]["FlangeCapacity"] = flange_splice_capacity
        outputObj['FlangeBolt']['MaxPitchF'] = new_bolt_param["MaxPitchF"]
        outputObj["FlangeBolt"]["FlangeTThinner"] = new_bolt_param["FlangeTThinner"]
        outputObj["FlangeBolt"]["edge_dist_gauge"] = edge_dist  # For 3D model

        # Dimension of inner flange plate
        outputObj["FlangeBolt"]["InnerFlangePlateHeight"] = new_bolt_param["FlangePlateHeight"]
        outputObj["FlangeBolt"]["InnerFlangePlateWidth"] = inner_flange_plate_w # There will be 4 inner plates, this width is width of each plate
        outputObj["FlangeBolt"]["InnerFlangePlateThickness"] = flange_plate_t
        outputObj["FlangeBolt"]["flangeplatethick"] = flangeplatethick

        ####### For reference and validation
        outputObj["WebBolt"]["WebBlockShear"] = Tdb
        outputObj["WebBolt"]["ShearYielding"] = V_d
        outputObj["WebBolt"]["ShearRupture"] = R_n
        outputObj["FlangeBolt"]["FlangeCapacity"] = flangecapacity
        outputObj["FlangeBolt"]["Yielding"] = Tdg_flange_plate
        outputObj["FlangeBolt"]["Rupture"] = Tdn_flange_plate
        outputObj["FlangeBolt"]["FlangeBlockShear"] = Tdb_flange
        outputObj['FlangeBolt']['columndepth'] = column_d
        outputObj['FlangeBolt']['columnrootradius'] =column_r1
        outputObj['FlangeBolt']['columnflangethk'] = column_f_t
        outputObj["FlangeBolt"]["kb"] = new_bolt_param["kb"]
        outputObj['FlangeBolt']['DiaHole'] = int(dia_hole)
        outputObj['FlangeBolt']['FlangeForce'] = ff


    if design_status == True:

        logger.info(": Overall bolted cover plate splice connection design is safe \n")
        logger.debug(" :=========End Of design===========")
    else:
        logger.error(": Design is not safe \n ")
        logger.debug(" :=========End Of design===========")

    return outputObj


########################################### End of Design ################################################
