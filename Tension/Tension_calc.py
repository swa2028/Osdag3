


from Tension.model import *
from utilities.is800_2007 import IS800_2007
from utilities.other_standards import IS1363_part_1_2002, IS1363_part_3_2002, IS1367_Part3_2002
from utilities.common_calculation import *
from Connections import connection_calculations
import math
import logging
flag = 1
logger = None
beam_d = 0
beam_B = 0


def module_setup():
    global logger
    logger = logging.getLogger("osdag.Tension_calc")


module_setup()

# Start of Main Program

def bolt_capacity(member_fu, bolt_fu,bolt_type,bolt_hole_type, bolt_slip,thickness,diameter, end_distance, pitch, A_nb,A_sb):
    if bolt_type == "Bearing Bolt":
        Vsb = IS800_2007.cl_10_3_3_bolt_shear_capacity(bolt_fu, A_nb, A_sb, n_n=1, n_s=0, safety_factor_parameter='field')
        Vdpb = IS800_2007.cl_10_3_4_bolt_bearing_capacity(member_fu, bolt_fu, thickness ,diameter, end_distance, pitch,bolt_hole_type,safety_factor_parameter='field')
        Vs = IS800_2007.cl_10_3_2_bolt_design_strength(Vsb, Vdpb)
    elif bolt_type == "Friction Grip Bolt":
        muf = bolt_slip
        n_e = 2  # number of effective surfaces offering frictional resistance
        Vdsf = round(IS800_2007.bolt_shear_friction_grip_bolt(diameter, bolt_fu, muf, n_e, bolt_hole_type), 2)*1000
        Vsb = IS800_2007.cl_10_3_3_bolt_shear_capacity(bolt_fu, A_nb, A_sb, n_n=1, n_s=0, safety_factor_parameter='field')
        Vs = IS800_2007.cl_10_3_2_bolt_design_strength(Vsb, Vdsf)
    else:
        pass
    return Vs

def member_dimensions(member_size,member_type):
    if member_type == "Angle" or member_type == "Back to Back Angles" or member_type == "Star Angles":
        member_type = "Angles"
    elif member_type == "Channels" or member_type == "Back to Back Channels":
        member_type = "Channels"
    else:
        pass
    memberdata = get_memberdata(member_size,member_type)
    return memberdata

def tension_design(uiObj):
    global logger
    global design_status
    design_status = False

    # if uiObj['Member']['Location'] == "Web":
    #     conn_type = "Web"
    # elif uiObj['Member']['Location'] == "Flange":
    #     conn_type = "Flange"
    # else:
    #     conn_type = "Leg"
    # print ("A")
    member_type = uiObj['Member']['SectionType']
    conn_type = uiObj['Member']['ConnType']
    conn = uiObj['Member']['Location']
    # Member_type = "Angles"
    member_size = uiObj['Member']['SectionSize']
    # Member_size = "40 40 x 4"
    member_fu = float(uiObj['Member']['fu (MPa)'])
    member_fy = float(uiObj['Member']['fy (MPa)'])
    member_length = float(uiObj["Member"]["Member_length"])
    tension_load = float(uiObj["Load"]["AxialForce (kN)"])

    diameter = float(uiObj["Bolt"]["Diameter (mm)"])
    bolt_type = (uiObj["Bolt"]["Type"])
    bolt_grade = float(uiObj["Bolt"]["Grade"])
    bolt_fu = float(uiObj["bolt"]["bolt_fu"])
    bolt_slip = float(uiObj["bolt"]["slip_factor"])
    plate_thickness = float(uiObj["Plate"]["Thickness (mm)"])

    weld_type = (uiObj["Weld"]["Type"])
    # weld_thickness = float(uiObj["Weld"]["Thickness (mm)"])
    weld_fu =  float(uiObj["weld"]["fu_overwrite"])
    weld_fabrication = str(uiObj["weld"]["typeof_weld"])

    dia_hole = diameter + int(uiObj["bolt"]["bolt_hole_clrnce"])
    bolt_hole_type = uiObj["bolt"]["bolt_hole_type"]
    edge_type = uiObj["detailing"]["typeof_edge"]

    old_beam_section = get_oldbeamcombolist()
    old_column_section = get_oldcolumncombolist()

    if member_size in old_beam_section or member_size in old_column_section:
        logger.warning(": You are using a section (in red colour) that is not available in the latest version of IS 808")

    if member_fu < 410 or member_fy < 230:
        logger.warning(" : You are using a section of grade that is not available in the latest version of IS 2062")

    dictmemberdata = member_dimensions(member_size, member_type)
    print(dictmemberdata)
    if member_type == "Channels" or member_type == "Back to Back Channels":
        member_tw = float(dictmemberdata["tw"])
        member_tf = float(dictmemberdata["T"])
        member_d = float(dictmemberdata["D"])
        member_B = float(dictmemberdata["B"])
        member_R1= float(dictmemberdata["R1"])
        member_Ag = float(dictmemberdata["Area"]) * 100
        radius_gyration = min((float(dictmemberdata["rz"])),(float(dictmemberdata["ry"])))*10

    else:
        member_leg = dictmemberdata["AXB"]
        leg = member_leg.split("x")
        leg1 = leg[0]
        leg2 = leg[1]
        t = float(dictmemberdata["t"])
        member_Ag = float(dictmemberdata["Area"]) * 100
        radius_gyration = min((float(dictmemberdata["ru(max)"])), (float(dictmemberdata["rv(min)"]))) * 10

    if member_type == "Back to Back Channels":
        member_Ag = float(dictmemberdata["Area"]) * 100 * 2
        member_Izz = float(dictmemberdata["Iz"])
        member_Iyy = float(dictmemberdata["Iy"])
        member_Cy = float(dictmemberdata["Cy"])/10
        Iyy = (member_Iyy + (member_Ag/100* (member_Cy+(plate_thickness/20))*(member_Cy+(plate_thickness/20))))*2
        Izz = 2 * member_Izz
        I = min(Iyy,Izz)
        radius_gyration = (math.sqrt(I / (member_Ag/100))) * 10
    else:
        pass

    if member_type == "Back to Back Angles" and conn == "LongerLeg":
        member_Izz = float(dictmemberdata["Iz"])
        member_Iyy = float(dictmemberdata["Iy"])
        member_Cy = float(dictmemberdata["Cy"])/10
        Iyy = (member_Iyy + (member_Ag/100 * (member_Cy+(plate_thickness/20)) *(member_Cy+(plate_thickness/20)))) * 2
        Izz = 2 * member_Izz
        I = min(Iyy, Izz)
        radius_gyration = (math.sqrt(I / (member_Ag/100* 2))) * 10

    elif member_type == "Back to Back Angles" and conn == "ShorterLeg":
        member_Izz = float(dictmemberdata["Iz"])
        member_Iyy = float(dictmemberdata["Iy"])
        member_Cz = float(dictmemberdata["Cz"])/10
        Izz = (member_Izz + (member_Ag/100 * (member_Cz +(plate_thickness/20))*(member_Cz +(plate_thickness/20)))) * 2
        Iyy = 2 * member_Iyy
        I = min(Iyy, Izz)
        radius_gyration = (math.sqrt(I/(member_Ag/100* 2))) * 10

    elif member_type == "Star Angles" and conn == "LongerLeg":
        member_Izz = float(dictmemberdata["Iz"])
        member_Iyy = float(dictmemberdata["Iy"])
        member_Cy = float(dictmemberdata["Cy"])/10
        member_Cz = float(dictmemberdata["Cz"]) / 10
        Iyy = (member_Iyy + (member_Ag/100 * (member_Cy+(plate_thickness/20)) * (member_Cy+(plate_thickness/20)))) * 2
        Izz = (member_Izz + (member_Ag/100 * member_Cz * member_Cz)) * 2
        I = min(Iyy, Izz)
        radius_gyration = (math.sqrt(I / (member_Ag/100* 2))) * 10

    elif member_type == "Star Angles" and conn == "ShorterLeg":
        member_Izz = float(dictmemberdata["Iz"])
        member_Iyy = float(dictmemberdata["Iy"])
        member_Cy = float(dictmemberdata["Cy"])/10
        member_Cz = float(dictmemberdata["Cz"]) / 10
        Izz = (member_Izz + (member_Ag/100 * (member_Cz+(plate_thickness/20)) * (member_Cz+(plate_thickness/20)))) * 2
        Iyy = (member_Iyy + (member_Ag/100 * member_Cz * member_Cz)) * 2
        I = min(Iyy, Izz)
        radius_gyration = (math.sqrt(I/(member_Ag/100*2))) * 10

    else:
        pass

    bolt_arrange = False
    weld_arrange = False
    if conn_type == "Bolted" and conn == "Web":

        [A_sb, A_nb] = IS1367_Part3_2002.bolt_area(diameter)
        edge_distance = IS800_2007.cl_10_2_4_2_min_edge_end_dist(diameter, bolt_hole_type, edge_type)
        end_distance = IS800_2007.cl_10_2_4_2_min_edge_end_dist(diameter, bolt_hole_type, edge_type)
        pitch = IS800_2007.cl_10_2_2_min_spacing(diameter)
        no_of_bolts_sec = int(((member_d- 2*member_tf) - (edge_distance * 2))/pitch)
        if no_of_bolts_sec == 0:
            logger.error(": Select Smaller Diameter Bolt")
        else:


        # pitch = float(math.floor(((member_d- 2*member_tf) - (edge_distance * 2))/no_of_bolts_sec))

            # kbChk1 = end_distance / float(3 * dia_hole)
            # kbChk2 = pitch / float(3 * dia_hole) - 0.25
            # kbChk3 = bolt_fu / float(member_fu)
            # kbChk4 = 1
            # kb = min(kbChk1, kbChk2, kbChk3, kbChk4)
            # kb = round(kb, 3)

            Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, member_tw, diameter,
                               end_distance, pitch, A_nb, A_sb)
            no_of_bolts = float(math.ceil(tension_load / (Vs/1000)))

            restart = True

            while restart:
                if no_of_bolts < no_of_bolts_sec:
                    no_of_rows_bolt = no_of_bolts
                    no_of_columns_bolt = 1
                    bolt_qty = float(no_of_rows_bolt * no_of_columns_bolt)
                    if no_of_rows_bolt == 1:
                        row_pitch = 0
                    else:
                        row_pitch = round((int(((member_d- 2*member_tf)-(edge_distance * 2)) / (no_of_rows_bolt-1))),2)
                    column_pitch = IS800_2007.cl_10_2_2_min_spacing(diameter)
                    edge_distance = float((((member_d- 2*member_tf) - (row_pitch * (no_of_rows_bolt-1))))/2)
                    # kbChk1 = end_distance / float(3 * dia_hole)
                    # kbChk2 = pitch / float(3 * dia_hole) - 0.25
                    # kbChk3 = bolt_fu / float(member_fu)
                    # kbChk4 = 1
                    # kb = min(kbChk1, kbChk2, kbChk3, kbChk4)
                    # kb = round(kb, 3)
                    #
                    # Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, member_tw, diameter,
                    #                    end_distance, column_pitch, kb, A_nb, A_sb)
                    Bij = 1.075 - ((column_pitch * (no_of_columns_bolt - 1))/(200 * diameter))
                    if (column_pitch * (no_of_columns_bolt - 1)) == (15 * diameter):
                        if 0.75 < Bij:
                            Vs = 0.75 * Vs
                        elif Bij > 1:
                            Vs = 1 * Vs
                        else:
                            Vs = Vs
                        rev_bolt_qty = float(math.ceil(tension_load / (Vs / 1000)))
                        if bolt_qty >= rev_bolt_qty:
                            bolt_arrange = True
                            break
                    else:
                        break



                    #
                    # if bolt_arrange == True:
                    #     break
                    # else:
                    #     logger.error(": Bolot Diameter is not sufficient")

                elif no_of_bolts == no_of_bolts_sec:
                    no_of_rows_bolt = no_of_bolts
                    no_of_columns_bolt = 1
                    bolt_qty = float(no_of_bolts)
                    if no_of_rows_bolt == 1:
                        row_pitch = 0
                    else:
                        row_pitch = round((int(((member_d - 2 * member_tf) - (edge_distance * 2)) / (no_of_rows_bolt - 1))), 2)
                    column_pitch = IS800_2007.cl_10_2_2_min_spacing(diameter)
                    edge_distance = float((((member_d - 2 * member_tf) - (row_pitch * (no_of_rows_bolt-1)))) / 2)
                    # kbChk1 = end_distance / float(3 * dia_hole)
                    # kbChk2 = pitch / float(3 * dia_hole) - 0.25
                    # kbChk3 = bolt_fu / float(member_fu)
                    # kbChk4 = 1
                    # kb = min(kbChk1, kbChk2, kbChk3, kbChk4)
                    # kb = round(kb, 3)
                    # Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip,member_tw, diameter,
                    #                    end_distance, column_pitch, kb, A_nb, A_sb)
                    Bij = 1.075 - ((column_pitch * (no_of_columns_bolt - 1)) / (200 * diameter))
                    if (column_pitch * (no_of_columns_bolt - 1)) == (15 * diameter):
                        if 0.75 < Bij:
                            Vs = 0.75 * Vs
                        elif Bij > 1:
                            Vs = 1 * Vs
                        else:
                            Vs = Vs
                        rev_bolt_qty = float(math.ceil(tension_load / (Vs / 1000)))
                        if bolt_qty >= rev_bolt_qty:
                            bolt_arrange = True
                            break
                    else:
                        break


                    # if bolt_arrange == True:
                    #     break
                    # else:
                    #     logger.error(": Bolot Diameter is not sufficient")

                elif no_of_bolts > no_of_bolts_sec:
                    ratio = round_up((no_of_bolts/no_of_bolts_sec))
                    no_of_columns_bolt = ratio
                    print(no_of_columns_bolt)
                    # total_bolt_1 = no_of_bolts_sec * no_of_columns_bolt
                    # total_bolt_2 = (no_of_bolts_sec-1) * no_of_columns_bolt
                    # if total_bolt_1 > total_bolt_2 and total_bolt_2>=no_of_bolts:
                    #     no_of_rows_bolt = no_of_bolts_sec-1
                    # elif total_bolt_2 > total_bolt_1 and total_bolt_1 >= no_of_bolts:
                    #     no_of_rows_bolt = no_of_bolts_sec
                    # else:
                    #     pass
                    for i in range(int(no_of_bolts_sec+1)):
                        if bolt_arrange == True:
                            break
                        else:
                            pass
                        no_of_columns_bolt = ratio
                        for j in range(3):
                            bolt_qty = (no_of_bolts_sec - i) * (no_of_columns_bolt+j)
                            no_of_columns_bolt= no_of_columns_bolt+j
                            if (bolt_qty - no_of_bolts) == 0:
                                no_of_rows_bolt = float(math.ceil(bolt_qty/no_of_columns_bolt))
                                bolt_arrange = True
                                break
                            elif bolt_qty > no_of_bolts and (bolt_qty - no_of_bolts) == 1:
                                no_of_rows_bolt = float(math.ceil(bolt_qty/no_of_columns_bolt))
                                bolt_arrange = True
                                break
                            elif bolt_qty > no_of_bolts and (bolt_qty - no_of_bolts) == 2:
                                no_of_rows_bolt = float(math.ceil(bolt_qty/no_of_columns_bolt))
                                bolt_arrange = True
                                break
                            else:
                                pass
                    if bolt_arrange == True:
                        bolt_qty = float(no_of_columns_bolt * no_of_rows_bolt)
                        if no_of_rows_bolt == 1:
                            row_pitch = 0
                        else:
                            row_pitch = round((int(((member_d - 2 * member_tf) - (edge_distance * 2)) / (no_of_rows_bolt - 1))),2)
                        column_pitch = IS800_2007.cl_10_2_2_min_spacing(diameter)
                        edge_distance = float((((member_d - 2 * member_tf) - (row_pitch * (no_of_rows_bolt-1)))) / 2)
                        # kbChk1 = end_distance / float(3 * dia_hole)
                        # kbChk2 = pitch / float(3 * dia_hole) - 0.25
                        # kbChk3 = bolt_fu / float(member_fu)
                        # kbChk4 = 1
                        # kb = min(kbChk1, kbChk2, kbChk3, kbChk4)
                        # kb = round(kb, 3)
                        # Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, member_tw, diameter,
                        #                    end_distance, column_pitch, kb, A_nb, A_sb)
                        Bij = 1.075 - ((column_pitch * (no_of_columns_bolt - 1)) / (200 * diameter))
                        if (column_pitch * (no_of_columns_bolt - 1)) == (15 * diameter):
                            if Bij < 0.75:
                                Vs = 0.75 * Vs
                            elif Bij > 1:
                                Vs = 1 * Vs
                            else:
                                Vs = Vs
                            rev_bolt_qty = float(math.ceil(tension_load / (Vs / 1000)))
                            if bolt_qty >= rev_bolt_qty:
                                bolt_arrange = True
                                break
                            else:
                                no_of_bolts = rev_bolt_qty
                        else:
                            break

                    else:
                        logger.error(": Bolt Diameter is not sufficient")
                else:
                    bolt_arrange = False



    # if no_of_bolts < no_of_bolts_sec:
    #     no_of_rows_bolt = no_of_bolts
    #     no_of_columns_bolt = 1
    #     bolt_qty = no_of_bolts
    #     pitch = round((float((member_d - (end_distance * 2)) / bolt_qty)),2)
    #     end_distance = member_d - pitch * (bolt_qty-1)
    #     Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, plate_thickness, diameter,
    #                        end_distance, pitch, kb, A_nb, A_sb)
    #
    # elif no_of_bolts == no_of_bolts_sec:
    #     no_of_rows_bolt = no_of_bolts
    #     no_of_columns_bolt = 1
    #     bolt_qty = no_of_bolts
    #     pitch = round((float((member_d - (end_distance * 2)) / bolt_qty)), 2)
    #     end_distance = member_d - pitch * (bolt_qty - 1)
    #     Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, plate_thickness, diameter,
    #                        end_distance, pitch, kb, A_nb, A_sb)
    #
    # elif no_of_bolts > no_of_bolts_sec:
    #     ratio = round_up((no_of_bolts/no_of_bolts_sec),0)
    #     no_of_columns_bolt = ratio
    #     total_bolt_1 = no_of_bolts_sec * no_of_columns_bolt
    #     total_bolt_2 = (no_of_bolts_sec-1) * no_of_columns_bolt
    #     if total_bolt_1 > total_bolt_2 and total_bolt_2>=no_of_bolts:
    #         no_of_rows_bolt = no_of_bolts_sec-1
    #     elif total_bolt_2 > total_bolt_1 and total_bolt_1 >= no_of_bolts:
    #         no_of_rows_bolt = no_of_bolts_sec
    #     else:
    #         pass
    #     bolt_qty = no_of_columns_bolt * no_of_rows_bolt
    #     Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, plate_thickness, diameter,
    #                        end_distance, pitch, kb, A_nb, A_sb)





# member_d = 250
# [A_sb, A_nb] = IS1367_Part3_2002.bolt_area(12)
# end_distance = IS800_2007.cl_10_2_4_2_min_edge_end_dist(12,"standard", 'hand_flame_cut')
# print(round(end_distance,0))
# pitch = IS800_2007.cl_10_2_2_min_spacing(12)
# print(round(pitch,0))
# no_of_bolts_sec = float(math.floor((member_d - (end_distance * 2)) / pitch))
# print(no_of_bolts_sec)
# pitch = round(float((member_d - (end_distance * 2)) / no_of_bolts_sec),0)
# print(pitch)
# kbChk1 = end_distance / float(3 * 14)
# kbChk2 = pitch / float(3 * 14) - 0.25
# kbChk3 = 410 / float(410)
# kbChk4 = 1
# kb = min(kbChk1, kbChk2, kbChk3, kbChk4)
# kb = round(kb, 3)
# print(kb)
#
# Vs = bolt_capacity(410,410,"Bearing Bolt","standard",0.3,12,12,end_distance,pitch,kb,A_nb,A_sb)
# print(Vs/1000)
# tension_load = 750
# no_of_bolts = float(round_up(tension_load/(Vs/1000)))
# print(no_of_bolts)
# print(no_of_bolts_sec)
# shear_force_bolt = tension_load/bolt_qty
# bolt_efficiency = shear_force_bolt/Vs
# print(bolt_qty)
# print(no_of_rows_bolt)
# print(no_of_columns_bolt)
# print(Vs)


    # if no_of_bolts < no_of_bolts_sec:
    #     no_of_rows_bolt = no_of_bolts
    #     no_of_columns_bolt = 1
    #     bolt_qty = no_of_bolts
    #     pitch = round((float((member_d - (end_distance * 2)) / bolt_qty)),2)
    #     end_distance = member_d - pitch * (bolt_qty-1)
    #     Vs = bolt_capacity(410,410,"Bearing Bolt","standard",0.3,12,12,end_distance,pitch,kb,A_nb,A_sb)
    #
    # elif no_of_bolts == no_of_bolts_sec:
    #     no_of_rows_bolt = no_of_bolts
    #     no_of_columns_bolt = 1
    #     bolt_qty = no_of_bolts
    #     pitch = round((float((member_d - (end_distance * 2)) / bolt_qty)), 2)
    #     end_distance = member_d - pitch * (bolt_qty - 1)
    #     Vs = bolt_capacity(410,410,"Bearing Bolt","standard",0.3,12,12,end_distance,pitch,kb,A_nb,A_sb)
    #
    # elif no_of_bolts > no_of_bolts_sec:
    #     ratio = round_up((no_of_bolts/no_of_bolts_sec))
    #     no_of_columns_bolt = ratio
    #     # total_bolt_1 = no_of_bolts_sec * no_of_columns_bolt
    #     # total_bolt_2 = (no_of_bolts_sec-1) * no_of_columns_bolt
    #     # if total_bolt_1 > total_bolt_2 and total_bolt_2>=no_of_bolts:
    #     #     no_of_rows_bolt = no_of_bolts_sec-1
    #     # elif total_bolt_2 > total_bolt_1 and total_bolt_1 >= no_of_bolts:
    #     #     no_of_rows_bolt = no_of_bolts_sec
    #     # else:
    #     #     pass
    #     for i in range(int(no_of_bolts_sec)):
    #         for j in range(int(no_of_columns_bolt+2)):
    #             bolt_qty = (no_of_bolts_sec - i) * (no_of_columns_bolt+j)
    #             if (bolt_qty - no_of_bolts) == 0:
    #                 no_of_rows_bolt = float(math.ceil(bolt_qty/no_of_columns_bolt))
    #             elif bolt_qty > no_of_bolts and (bolt_qty - no_of_bolts) == 1:
    #                 no_of_rows_bolt = float(math.ceil(bolt_qty/no_of_columns_bolt))
    #             elif bolt_qty > no_of_bolts and (bolt_qty - no_of_bolts) == 2:
    #                 no_of_rows_bolt = float(math.ceil(bolt_qty/no_of_columns_bolt))
    #             else:
    #                 pass
    #
    #     bolt_qty = no_of_columns_bolt * no_of_rows_bolt
    #     Vs = bolt_capacity(410, 410, "Bearing Bolt", "standard", 0.3, 12, 12, end_distance, pitch, kb, A_nb, A_sb)
        # bolt_qty = no_of_bolts
        # pitch = round((float((member_d - (end_distance * 2)) / bolt_qty)), 2)
        # end_distance = member_d - pitch * (bolt_qty - 1)
        # Vs = bolt_capacity(member_fu, bolt_fu, bolt_type, bolt_hole_type, bolt_slip, plate_thickness, diameter,
        #                    end_distance, pitch, kb, A_nb, A_sb)

# [A_sb, A_nb] = IS1367_Part3_2002.bolt_area(12)
# print (A_sb,A_nb)
# end_distance = IS800_2007.cl_10_2_4_2_min_edge_end_dist(12, "standard",'hand_flame_cut')
# print(end_distance)
# pitch = IS800_2007.cl_10_2_2_min_spacing(12)
# print(pitch)
# Vsb = IS800_2007.cl_10_3_3_bolt_shear_capacity(410, A_nb, A_sb, n_n=1, n_s=0, safety_factor_parameter='field')
# print(Vsb)
# Vdpb = IS800_2007.cl_10_3_4_bolt_bearing_capacity(410, 410, 12, 12, end_distance, pitch,"standard",safety_factor_parameter='field')
# print(Vdpb)
# Vsb = IS800_2007.cl_10_3_3_bolt_shear_capacity(410, A_nb, A_sb, n_n=1, n_s=0, safety_factor_parameter='field')
# print(Vsb)
        if bolt_arrange == True:
            shear_force_bolt = tension_load / bolt_qty
            bolt_efficiency = shear_force_bolt / (Vs/1000)
            if member_type == "Channels" and conn == "Web":
                member_Ag = float(dictmemberdata["Area"]) * 100
                member_An = member_Ag - (no_of_rows_bolt * dia_hole * member_tw)
                if no_of_rows_bolt >=2 :
                    A_vg = ((column_pitch*(no_of_columns_bolt-1) + end_distance)*member_tw)*2
                    A_vn = ((column_pitch*(no_of_columns_bolt-1) + end_distance - ((no_of_columns_bolt -0.5)*dia_hole)) * member_tw)*2
                    A_tg = row_pitch * (no_of_rows_bolt - 1) * member_tw
                    A_tn = (row_pitch*(no_of_rows_bolt - 1) - ((1)*dia_hole)) * member_tw
                else:
                    A_vg = (column_pitch + end_distance) * member_tw
                    A_vn = ((column_pitch * (no_of_columns_bolt - 1) + end_distance - ((no_of_columns_bolt - 0.5) * dia_hole)) * member_tw)
                    A_tg = (end_distance)* member_tw
                    A_tn = (end_distance - 0.5* dia_hole) * member_tw
            elif member_type == "Back to Back Channels" and conn == "Web":
                member_Ag = float (dictmemberdata["Area"]) * 100 * 2
                member_An = member_Ag - (no_of_rows_bolt * dia_hole * 2 * member_tw)
                if no_of_rows_bolt >=2:
                    A_vg = ((column_pitch*(no_of_columns_bolt-1) + end_distance) * member_tw) * 2 * 2
                    A_vn = ((column_pitch*(no_of_columns_bolt-1) + end_distance - ((no_of_columns_bolt - 0.5)*dia_hole)) * member_tw)*2*2
                    A_tg = row_pitch* (no_of_rows_bolt - 1)* member_tw*2
                    A_tn = (row_pitch*(no_of_rows_bolt-1) - ((1)*dia_hole)) * member_tw * 2
                else:
                    A_vg = (column_pitch + end_distance) * member_tw * 2
                    A_vn = ((column_pitch * (no_of_columns_bolt - 1) + end_distance - ((no_of_columns_bolt - 0.5) * dia_hole)) * member_tw)*2
                    A_tg = end_distance * member_tw * 2
                    A_tn = (end_distance - 0.5* dia_hole) * member_tw * 2

            plate_detailing = False
            plate_length = (column_pitch * (no_of_columns_bolt - 1)) + 2 * end_distance
            total_plate_length = round_up((plate_length + member_d/4),5,30)
            plate_width = member_d + 50
            plate_A_vg = ((column_pitch*(no_of_columns_bolt-1) + end_distance) * plate_thickness) * 2
            plate_A_vn = ((column_pitch * (no_of_columns_bolt - 1) + end_distance - (
                        (no_of_columns_bolt - 0.5) * dia_hole)) * plate_thickness) * 2
            plate_A_tg = row_pitch * (no_of_rows_bolt - 1) * plate_thickness
            plate_A_tn = (row_pitch * (no_of_rows_bolt - 1) - ((1) * dia_hole)) * plate_thickness

            plate_capacity = IS800_2007.cl_6_4_1_block_shear_strength(plate_A_vg, plate_A_vn, plate_A_tg, plate_A_tn, member_fu, member_fy)/1000
            if plate_capacity > tension_load:
                plate_detailing = True
            else:
                plate_detailing = False
                logger.error(": Chosen Plate Thickness is not sufficient")
            tension_yielding = IS800_2007.tension_member_design_due_to_yielding_of_gross_section(member_Ag,
                                                                                                     member_fy) / 1000
            k = 1
            radius_gyration_min = k * (member_length) / 400
            tension_slenderness = IS800_2007.design_check_for_slenderness(k, member_length, radius_gyration)

            tension_blockshear = IS800_2007.cl_6_4_1_block_shear_strength(A_vg, A_vn, A_tg, A_tn, member_fu,
                                                                          member_fy) / 1000
            #     # Calculation for Design Strength Due to Yielding of Gross Section
            #     if (Member_type == "Angles")and bolt_row > 1 :
            #      tension_rupture =IS800_2007.tension_angle_member_design_due_to_rupture_of_critical_section(member_An,member_Ag, member_fu , member_fy, L_c, w, shear_lag, t)/1000
            #     else:
            tension_rupture = IS800_2007.tension_member_design_due_to_rupture_of_critical_section(member_An,
                                                                                                  member_fu) / 1000

            tension_design = min(tension_blockshear, tension_rupture, tension_yielding)
        else:
            logger.error(": Quantity of Bolts required are uneconomical")




#     elif conn=="Flange" and Member_type != "Angles":
#             Member_An = Member_Ag - (member_d * member_tw/2) - (bolt_column * dia_hole * member_tf)
#             A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * member_tf) * 2 * 2
#             A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * member_tf) * 2 * 2
#             A_tg = (bolt_column_pitch*(bolt_column/2 -1) + bolt_edgedistance) * member_tf * 2 * 2
#             A_tn = ((bolt_column_pitch*(bolt_column/2 -1) + bolt_edgedistance) - (bolt_column/2 -0.5) * dia_hole) * member_tf * 2 * 2
#         # elif Member_type == "Channels":
#         #     Member_An = Member_Ag -(member_d * member_tw/2) - (bolt_column * dia_hole * member_tf)
#         #     A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * member_tf) * 2
#         #     A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * member_tf) * 2
#         #     A_tg = (bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) * member_tf * 2
#         #     A_tn = ((bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) - (bolt_column / 2 - 0.5) * dia_hole) * member_tf * 2
#         # elif Member_type == "Columns":
#         #     Member_An = Member_Ag - (member_d * member_tw / 2) - (bolt_column * dia_hole * member_tf)
#         #     A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * member_tf) * 2
#         #     A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * member_tf) * 2
#         #     A_tg = (bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) * member_tf * 2
#         #     A_tn = ((bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) - (bolt_column / 2 - 0.5) * dia_hole) * member_tf * 2
#
#     elif conn == "Back to Back Angles" and conn == "Star Angles":
#         Member_Ag = float(dictmemberdata["Area"]) * 100*2
#         Member_An = Member_Ag - (bolt_column * dia_hole * 2* t)
#         A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * t)*2
#         A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * t)*2
#         A_tg = ((bolt_column_pitch * (bolt_column - 1)) + bolt_edgedistance)* t*2
#         A_tn = ((((bolt_column_pitch * (bolt_column - 1)) + bolt_edgedistance)) - (((bolt_column -0.5) * dia_hole))) * t*2
#     else:
#         Member_An = Member_Ag - (bolt_column * dia_hole * t)
#         A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * t)
#         A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * t)
#         A_tg = ((bolt_column_pitch * (bolt_column - 1)) + bolt_edgedistance)* t
#         A_tn = ((((bolt_column_pitch * (bolt_column - 1)) + bolt_edgedistance)) - (((bolt_column -0.5) * dia_hole))) * t
#
#     if Member_type == "Angles":
#         w = max(float(leg1), float(leg2))
#         shear_lag = ((min(float(leg1), float(leg2)))-bolt_edgedistance) + w - t
#         L_c = (bolt_row_pitch * (bolt_row - 1))
#     else:
#         pass
#
#         # Calculation for Design Strength Due to Yielding of Gross Section
#
#     no_of_bolts = bolt_row
#

        # cl 6.2 Design Strength Due to Block Shear


    elif conn_type == "Welded" and conn == "Web":
        member_Ag = float(dictmemberdata["Area"]) * 100 * 2
        member_An = member_Ag
        A_vg = 0
        A_vn = 0
        A_tg = 0
        A_tn = 0



        # plate_detailing = False
        # plate_length = (column_pitch * (no_of_columns_bolt - 1)) + 2 * end_distance
        # plate_width = member_d + 50
        # plate_A_vg = ((column_pitch * (no_of_columns_bolt - 1) + end_distance) * plate_thickness) * 2
        # plate_A_vn = ((column_pitch * (no_of_columns_bolt - 1) + end_distance - (
        #         (no_of_columns_bolt - 0.5) * dia_hole)) * plate_thickness) * 2
        # plate_A_tg = row_pitch * (no_of_rows_bolt - 1) * plate_thickness * 2
        # plate_A_tn = (row_pitch * (no_of_rows_bolt - 1) - ((1) * dia_hole)) * plate_thickness * 2
        #
        # plate_capacity = IS800_2007.cl_6_4_1_block_shear_strength(plate_A_vg, plate_A_vn, plate_A_tg, plate_A_tn,
        #                                                           member_fu, member_fy) / 1000
        # if plate_capacity > tension_load:
        #     plate_detailing = True
        # else:
        #     plate_detailing = False
        #     logger.error(": Chosen Plate Thickness is not sufficient")

        f_weld = IS800_2007.cl_10_5_7_1_1_fillet_weld_design_stress(
            ultimate_stresses=[member_fu,weld_fu], fabrication=weld_fabrication)
        max_weld_thickness = float (min(plate_thickness, member_tf,member_tw))
        print(max_weld_thickness)
        weld_thickness = round_up((0.75 * max_weld_thickness),1,3)
        # if weld_thickness >  max_weld_thickness:
        #     logger.error(": Chosen Weld Size is higher than Member Thickness or Plate Thickness")

        throat = IS800_2007.cl_10_5_3_2_fillet_weld_effective_throat_thickness(weld_thickness, fusion_face_angle=90)
        L_eff = tension_load*1000/(throat * f_weld)

        Btw = IS800_2007.cl_10_5_7_3_weld_long_joint(L_eff, throat)
        if L_eff > 150 * throat:
            f_weld = Btw * f_weld
        else:
            pass
        if member_type == "Channels":
            web_weld = member_d
            L_eff = tension_load * 1000 / (throat * f_weld)
            print(L_eff)
            # diff = ((L_eff - member_d)/2)%10
            # print(diff)
            flange_weld = round_up(((L_eff - member_d)/2),10,50)

        else:
            web_weld = member_d
            L_eff = tension_load * 1000 / (throat * f_weld)
            print(L_eff)
            # diff = ((L_eff - member_d)/2)%10
            # print(diff)
            flange_weld = round_up(((L_eff - 2*member_d) / 4), 10, 50)

        plate_length = flange_weld
        total_plate_length = round_up((plate_length + member_d / 4), 5, 30)
        plate_width = member_d + 50


        plate_A_vg = plate_length * plate_thickness
        plate_A_vn = plate_A_vg
        plate_A_tg = plate_width * plate_thickness
        plate_A_tn = plate_A_tg
        plate_capacity = IS800_2007.cl_6_4_1_block_shear_strength(plate_A_vg, plate_A_vn, plate_A_tg, plate_A_tn, member_fu, member_fy) / 1000
        if plate_capacity > tension_load:
            plate_detailing = True
        else:
            plate_detailing = False
            logger.error(": Chosen Plate Thickness is not sufficient")

        k = 1
        radius_gyration_min = k * (member_length) / 400
        # cl 6.2 Design Strength Due to Block Shear
        tension_blockshear = IS800_2007.cl_6_4_1_block_shear_strength(A_vg, A_vn, A_tg, A_tn, member_fu,
                                                                      member_fy) / 1000
        #     # Calculation for Design Strength Due to Yielding of Gross Section
        #     if (Member_type == "Angles")and bolt_row > 1 :
        #      tension_rupture =IS800_2007.tension_angle_member_design_due_to_rupture_of_critical_section(member_An,member_Ag, member_fu , member_fy, L_c, w, shear_lag, t)/1000
        #     else:
        tension_rupture = IS800_2007.tension_member_design_due_to_rupture_of_critical_section(member_An, member_fu) / 1000
        tension_yielding = IS800_2007.tension_member_design_due_to_yielding_of_gross_section(member_Ag, member_fy) / 1000
        tension_slenderness = IS800_2007.design_check_for_slenderness(k, member_length, radius_gyration)
        if conn_type == "Welded" and conn == "Web":
            tension_design = min(tension_rupture, tension_yielding)
        else:
            tension_design = min(tension_rupture, tension_yielding, tension_blockshear)

        weld_arrange = True
    else:
        pass


    if bolt_arrange == True or weld_arrange == True:
 # End of Calculation, SAMPLE Output dictionary
        outputobj = dict()

        # FOR OUTPUT DOCK
        outputobj['Tension_Force'] = {}
        outputobj['Plate'] = {}
        outputobj['Bolt'] = {}
        outputobj['Weld'] = {}

        outputobj['Tension_Force']['Yielding'] = float(round(tension_yielding,3))
        outputobj['Tension_Force']['Rupture'] = float(round(tension_rupture,3))
        outputobj['Tension_Force']['Block_Shear'] = float(round(tension_blockshear,3))
        outputobj['Tension_Force']['Efficiency'] = float(round((tension_load/tension_design),3))
        outputobj['Tension_Force']['Slenderness'] = float(round((tension_slenderness),3))
        if conn_type == "Bolted" and conn == "Web":
            outputobj['Tension_Force']['End_Distance'] = float(round((end_distance), 3))
            outputobj['Tension_Force']['Edge_Distance'] = float(round((edge_distance), 3))
            outputobj['Bolt']['No_of_Rows_Bolts'] = float(round(no_of_rows_bolt, 3))
            outputobj['Bolt']['No_of_Columns_Bolts'] = float(round(no_of_columns_bolt, 3))
            outputobj['Bolt']['Row_Pitch'] = float(round(row_pitch, 3))
            outputobj['Bolt']['Column_Pitch'] = float(round(column_pitch, 3))
            outputobj['Bolt']['Bolt_Qty'] = float(round(bolt_qty, 3))
            outputobj['Bolt']['Req_Qty'] = float(round(no_of_bolts, 3))
        elif conn_type == "Welded" and conn == "Web":
            outputobj['Weld']['Length1'] = float(round(flange_weld, 3))
            outputobj['Weld']['Length2'] = float(round(web_weld, 3))
            outputobj['Weld']['Size'] = float(round(weld_thickness, 3))


        outputobj['Plate']['Length'] = float(round(plate_length, 3))
        outputobj['Plate']['Total Length'] = float(round(total_plate_length,3))
        outputobj['Plate']['Width'] = float(round(plate_width, 3))
        outputobj['Plate']['Thickness'] = float(round(plate_thickness, 3))
        outputobj['Tension_Force']['Design_Status'] = design_status

    else:
        outputobj = dict()
        outputobj['Tension_Force'] = {}
        outputobj['Plate'] = {}
        outputobj['Bolt'] = {}

        outputobj['Tension_Force']['Yielding'] = 0
        outputobj['Tension_Force']['Rupture'] = 0
        outputobj['Tension_Force']['Block_Shear'] = 0
        outputobj['Tension_Force']['Efficiency'] = 0
        outputobj['Tension_Force']['Slenderness'] = 0
        if conn_type == "Bolted" and conn == "Web":
            outputobj['Tension_Force']['End_Distance'] = 0
            outputobj['Tension_Force']['Edge_Distance'] = 0
            outputobj['Bolt']['No_of_Rows_Bolts'] = 0
            outputobj['Bolt']['No_of_Columns_Bolts'] = 0
            outputobj['Bolt']['Row_Pitch'] = 0
            outputobj['Bolt']['Column_Pitch'] = 0
            outputobj['Bolt']['Bolt_Qty'] = 0
            outputobj['Bolt']['Req_Qty'] = 0
        else:
            pass
        outputobj['Plate']['Length'] = 0
        outputobj['Plate']['Total Length'] = 0
        outputobj['Plate']['Width'] = 0
        outputobj['Plate']['Thickness'] = 0
        outputobj['Tension_Force']['Design_Status'] = design_status
        design_status = False







        # for i,j in uiObj.items():
        #     if j == " ":
        #         logger.error(": Please enter all the inputs")
        #     else:
        #         pass

    if outputobj['Tension_Force']['Efficiency'] < 1 and outputobj['Tension_Force']['Slenderness'] < 400:
        design_status = True
    elif outputobj['Tension_Force']['Efficiency'] > 1 and outputobj['Tension_Force']['Slenderness'] < 400:
        design_status = False
        logger.error(": Chosen Member Section Size is not sufficient")
        logger.info(": Increase the size of Member ")
    elif outputobj['Tension_Force']['Efficiency'] < 1 and outputobj['Tension_Force']['Slenderness']> 400:
        design_status = False
        logger.error(": Chosen Member Section Size is not sufficient")
        logger.warning(": Minimum Radius of Gyration of Member shall be {} mm ".format(radius_gyration_min))
        logger.info(": Increase the size of Member ")

    if design_status is True:
        logger.info(":Member is safe for the applied tension load \n")
        logger.info(":In case of reversal load, Slenderness value shall be less than 180 \n")
        logger.debug(" :=========End Of design===========")
    else:
        logger.error(":Member fails for the applied tension load \n ")
        logger.info(": Increase the size of Member ")
        logger.debug(" :=========End Of design===========")

    outputobj['Tension_Force']['Design_Status'] = design_status

    return outputobj
    #
# def tension_welded_design(uiObj):
#     global logger
#     global design_status
#     design_status = True
#
#     # if uiObj['Member']['Location'] == "Web":
#     #     conn_type = "Web"
#     # elif uiObj['Member']['Location'] == "Flange":
#     #     conn_type = "Flange"
#     # else:
#     #     conn_type = "Leg"
#     conn = uiObj['Member']['Location']
#     Member_type = uiObj['Member']['SectionType']
#     # Member_type = "Angles"
#     Member_size = uiObj['Member']['SectionSize']
#     # Member_size = "40 40 x 4"
#     Member_fu = float(uiObj['Member']['fu (MPa)'])
#     Member_fy = float(uiObj['Member']['fy (MPa)'])
#     Member_length = float(uiObj["Member"]["Member_length"])
#     Tension_load = float(uiObj["Load"]["AxialForce (kN)"])
#
#     # bolt_dia = int(uiObj['Bolt']['Diameter (mm)'])
#     # bolt_row = int(uiObj["Bolt"]["RowsofBolts"])
#     # bolt_column = int(uiObj["Bolt"]["ColumnsofBolts"])
#     # bolt_row_pitch = float(uiObj["Bolt"]["Rowpitch"])
#     # bolt_column_pitch = float(uiObj["Bolt"]["Columnpitch"])
#     # bolt_enddistance = float(uiObj["Bolt"]["Enddistance"])
#     # bolt_edgedistance = float(uiObj["Bolt"]["Edgedistance"])
#     if conn == "Back to Back Web" or conn == "Star Angles" or conn == "Back to Back Angles":
#         Plate_thickness = float(uiObj["Weld"]["Platethickness"])
#     Inline_Weld = float(uiObj["Weld"]["inline_tension"])
#     Oppline_Weld = float(uiObj["Weld"]["oppline_tension"])
#
#
#     # dia_hole = bolt_dia + int(uiObj["bolt"]["bolt_hole_clrnce"])
#     end1_cond1 = uiObj["Support_Condition"]["end1_cond1"]
#     end1_cond2 = uiObj["Support_Condition"]["end1_cond2"]
#     end2_cond1 = uiObj["Support_Condition"]["end2_cond1"]
#     end2_cond2 = uiObj["Support_Condition"]["end2_cond2"]
#
#     # mu_f = float(uiObj["bolt"]["slip_factor"])
#     # gamma_mw = float(uiObj["weld"]["safety_factor"])
#     #
#     # gamma_mw = float(uiObj["weld"]["safety_factor"])
#     # if gamma_mw == 1.50:
#     #     weld_fabrication = 'field'
#     # else:
#     #     weld_fabrication = 'shop'
#     #
#     # dp_bolt_hole_type = uiObj["bolt"]["bolt_hole_type"]
#     # if dp_bolt_hole_type == "Over-sized":
#     #     bolt_hole_type = 'over_size'
#     # else:  # "Standard"
#     #     bolt_hole_type = 'standard'
#     #
#     # dia_hole = bolt_dia + int(uiObj["bolt"]["bolt_hole_clrnce"])
#     #
#     # if uiObj["detailing"]["typeof_edge"] == "a - Sheared or hand flame cut":
#     #     edge_type = 'hand_flame_cut'
#     # else:   # "b - Rolled, machine-flame cut, sawn and planed"
#     #     edge_type = 'machine_flame_cut'
#     #
#     # corrosive_influences = False
#     # if uiObj['detailing']['is_env_corrosive'] == "Yes":
#     #     corrosive_influences = True
#     #
#     # [bolt_shank_area, bolt_net_area] = IS1367_Part3_2002.bolt_area(bolt_dia)
#
#     old_beam_section = get_oldbeamcombolist()
#     old_column_section = get_oldcolumncombolist()
#
#     if Member_size in old_beam_section or Member_size in old_column_section:
#         logger.warning(": You are using a section (in red colour) that is not available in the latest version of IS 808")
#
#     if Member_fu < 410 or Member_fy < 230:
#         logger.warning(" : You are using a section of grade that is not available in the latest version of IS 2062")
#
#     dictmemberdata = get_memberdata(Member_size,Member_type)
#     print(dictmemberdata)
#     if Member_type != "Angles":
#         member_tw = float(dictmemberdata["tw"])
#         member_tf = float(dictmemberdata["T"])
#         member_d = float(dictmemberdata["D"])
#         member_B = float(dictmemberdata["B"])
#         member_R1= float(dictmemberdata["R1"])
#         Member_Ag = float (dictmemberdata["Area"]) * 100
#         radius_gyration = min((float(dictmemberdata["rz"])),(float(dictmemberdata["ry"])))*10
#
#     else:
#         member_leg = dictmemberdata["AXB"]
#         leg = member_leg.split("x")
#         leg1 = leg[0]
#         leg2 = leg[1]
#         t = float(dictmemberdata["t"])
#
#         Member_Ag = float(dictmemberdata["Area"]) * 100
#         radius_gyration = min((float(dictmemberdata["ru(max)"])), (float(dictmemberdata["rv(min)"]))) * 10
#
#     if conn == "Back to Back Web" and Member_type == "Channels":
#         Member_Izz = float(dictmemberdata["Iz"])
#         Member_Iyy = float(dictmemberdata["Iy"])
#         Member_Cy = float(dictmemberdata["Cy"])/10
#         Iyy = (Member_Iyy + (Member_Ag/100* (Member_Cy+(Plate_thickness/20))* (Member_Cy+(Plate_thickness/20))))*2
#         Izz = 2 * Member_Izz
#         I = min(Iyy,Izz)
#         radius_gyration = (math.sqrt(I / (Member_Ag/100* 2))) * 10
#
#     if conn == "Back to Back Angles" and Member_type == "Angles":
#         Member_Izz = float(dictmemberdata["Iz"])
#         Member_Iyy = float(dictmemberdata["Iy"])
#         Member_Cy = float(dictmemberdata["Cy"])/10
#         Iyy = (Member_Iyy + (Member_Ag/100 * (Member_Cy+(Plate_thickness/20)) *(Member_Cy+(Plate_thickness/20)))) * 2
#         Izz = 2 * Member_Izz
#         I = min(Iyy, Izz)
#         radius_gyration = (math.sqrt(I / (Member_Ag/100* 2))) * 10
#
#
#     if conn == "Star Angles" and Member_type == "Angles":
#         Member_Izz = float(dictmemberdata["Iz"])
#         Member_Iyy = float(dictmemberdata["Iy"])
#         Member_Cy = float(dictmemberdata["Cy"])/10
#         Member_Cz = float(dictmemberdata["Cz"]) / 10
#         Iyy = (Member_Iyy + (Member_Ag/100 * (Member_Cy+(Plate_thickness/20)) * (Member_Cy+(Plate_thickness/20)))) * 2
#         Izz = (Member_Izz + (Member_Ag/100 * Member_Cz * Member_Cz)) * 2
#         I = min(Iyy, Izz)
#         radius_gyration = (math.sqrt(I / (Member_Ag/100* 2))) * 10
#
#
#
#     # if conn == "Back to Back Leg" and Member_type == "Angles":
#     #     Member_Izz = float(dictmemberdata["Iz"])
#     #     Member_Iyy = float(dictmemberdata["Iy"])
#     #     Member_Cy = float(dictmemberdata["Cy"])/10
#     #     Iyy = (Member_Iyy + (Member_Ag/100 * Member_Cy * Member_Cy)) * 2
#     #     Izz = 2 * Member_Izz
#     #     I = min(Iyy, Izz)
#     #     radius_gyration = (math.sqrt(I / (Member_Ag/100* 2))) * 10
#     #
#
#     # Calculation for Design Strength Due to Yielding of Gross Section
#
#     if conn == "Web" and Member_type != "Angles":
#         Member_An = Member_Ag
#         A_vg = Inline_Weld * member_tw
#         A_vn = A_vg
#         A_tg = Oppline_Weld * member_tw
#         A_tn = A_tg
#
#     elif conn == "Leg" and Member_type == "Angles":
#         Member_An = Member_Ag
#         A_vg = 0
#         A_vn = 0
#         A_tg = 0
#         A_tn = 0
#
#     elif conn == "Back to Back Web":
#         Member_Ag = float (dictmemberdata["Area"]) * 100 *2
#         Member_An = Member_Ag
#         A_vg = 0
#         A_vn = 0
#         A_tg = 0
#         A_tn = 0
#
#     elif conn=="Flange":
#         Member_An = Member_Ag - (member_d * member_tw/2)
#         A_vg = Inline_Weld * member_tf
#         A_vn = A_vg
#         A_tg = Oppline_Weld * member_tf
#         A_tn = A_tg
#         # elif Member_type == "Channels":
#         #     Member_An = Member_Ag -(member_d * member_tw/2) - (bolt_column * dia_hole * member_tf)
#         #     A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * member_tf) * 2
#         #     A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * member_tf) * 2
#         #     A_tg = (bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) * member_tf * 2
#         #     A_tn = ((bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) - (bolt_column / 2 - 0.5) * dia_hole) * member_tf * 2
#         # elif Member_type == "Columns":
#         #     Member_An = Member_Ag - (member_d * member_tw / 2) - (bolt_column * dia_hole * member_tf)
#         #     A_vg = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance) * member_tf) * 2
#         #     A_vn = ((bolt_row_pitch * (bolt_row - 1) + bolt_enddistance - ((bolt_row - 0.5) * dia_hole)) * member_tf) * 2
#         #     A_tg = (bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) * member_tf * 2
#         #     A_tn = ((bolt_column_pitch * (bolt_column / 2 - 1) + bolt_edgedistance) - (bolt_column / 2 - 0.5) * dia_hole) * member_tf * 2
#
#     elif conn=="Back to Back Angles" or conn == "Star Angles":
#         Member_Ag = float(dictmemberdata["Area"]) * 100 * 2
#         Member_An = Member_Ag
#         A_vg = 0
#         A_vn = 0
#         A_tg = 0
#         A_tn = 0
#
#     else:
#         pass
#
#
#     if Member_type == "Angles":
#         w = max(float(leg1), float(leg2))
#         shear_lag = w
#         L_c = Inline_Weld/2
#     else:
#         pass
#     # Calculation for Design Strength Due to Yielding of Gross Section
#     tension_yielding = IS800_2007.tension_member_design_due_to_yielding_of_gross_section(Member_Ag, Member_fy) / 1000
#     # no_of_bolts = bolt_row
#
#     k = IS800_2007.effective_length_coefficeint(end1_cond1, end1_cond2, end2_cond1, end2_cond2)
#     tension_slenderness = IS800_2007.design_check_for_slenderness(k, Member_length, radius_gyration)
#     radius_gyration_min = k * (Member_length) / 400
#
#     # cl 6.2 Design Strength Due to Block Shear
#     if Member_type !="Angles" or conn == "Back to Back Web":
#         tension_blockshear = IS800_2007.cl_6_4_1_block_shear_strength(A_vg, A_vn, A_tg, A_tn, Member_fu, Member_fy)/1000
#     else:
#         tension_blockshear = 0
#
#     if Member_type !="Channels" and  conn == "Web":
#         tension_blockshear = IS800_2007.cl_6_4_1_block_shear_strength(A_vg, A_vn, A_tg, A_tn, Member_fu, Member_fy)/1000
#     else:
#         tension_blockshear = 0
#
#
#
#     if Member_type == "Angles":
#         tension_rupture =IS800_2007.tension_angle_member_design_due_to_rupture_of_critical_section(Member_An,Member_Ag, Member_fu , Member_fy, L_c, w, shear_lag, t)/1000
#     else:
#         tension_rupture =IS800_2007.tension_member_design_due_to_rupture_of_critical_section(Member_An, Member_fu)/1000
#
#
#     tension_design = min(tension_blockshear,tension_rupture,tension_yielding)
#
#     if tension_design == 0:
#         tension_design = min(tension_rupture,tension_yielding)
#     else:
#         pass
#
#  # End of Calculation, SAMPLE Output dictionary
#     outputobj = dict()
#
#     # FOR OUTPUT DOCK
#     outputobj['Tension_Force'] = {}
#
#     outputobj['Tension_Force']['Yielding'] = float(round(tension_yielding,3))
#     outputobj['Tension_Force']['Rupture'] = float(round(tension_rupture,3))
#     outputobj['Tension_Force']['Block_Shear'] = float(round(tension_blockshear,3))
#     outputobj['Tension_Force']['Efficiency'] = float(round((Tension_load/tension_design),3))
#     outputobj['Tension_Force']['Slenderness'] = float(round((tension_slenderness),3))
#
#     # for i,j in uiObj.items():
#     #     if j == " ":
#     #         logger.error(": Please enter all the inputs")
#     #     else:
#     #         pass
#
#     if outputobj['Tension_Force']['Efficiency'] < 1 and outputobj['Tension_Force']['Slenderness'] < 400:
#         design_status = True
#     elif outputobj['Tension_Force']['Efficiency'] > 1 and outputobj['Tension_Force']['Slenderness'] < 400:
#         design_status = False
#         logger.error(": Chosen Member Section Size is not sufficient")
#         logger.info(": Increase the size of Member ")
#     elif outputobj['Tension_Force']['Efficiency'] < 1 and outputobj['Tension_Force']['Slenderness']> 400:
#         design_status = False
#         logger.error(": Chosen Member Section Size is not sufficient")
#         logger.warning(": Minimum Radius of Gyration of Member shall be {} mm ".format(radius_gyration_min))
#         logger.info(": Increase the size of Member ")
#
#     if design_status is True:
#         logger.info(":Member is safe for the applied tension load \n")
#         logger.info(":In case of reversal load, Slenderness value shall be less than 180 \n")
#         logger.debug(" :=========End Of design===========")
#     else:
#         logger.error(":Member fails for the applied tension load \n ")
#         logger.debug(" :=========End Of design===========")
#
#     outputobj['Tension_Force']['Design_Status'] = design_status
#
#     return outputobj
#
# # tg = tension_member_design_due_to_yielding_of_gross_section(586, 210)
# # print(tg)
# #
# # tr = preliminary_tension_member_design_due_to_rupture_of_critical_section(586, 410, "welded", "none")
# # print(tr)
# #
# # trc = tension_member_design_due_to_rupture_of_critical_section(300, 300, 410, 210, 50, 50, 50, 6)
# # print(trc)
# #
# # tdb = IS800_2007.cl_6_4_1_block_shear_strength(300, 300, 0, 0, 410, 210)
# # print(tdb)
# #
# # tc = tension_member_design_check_for_slenderness(1,2000,21.1,"Only_tension")
# # print(tc)