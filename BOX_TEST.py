from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


def build_subdivisions_GEO(bounding_box_length, inner_side_length, outer_side_length, number_subdivisions, translation=(0.0,0.0,0.0)):
    box_elements = []
    pitch = bounding_box_length / number_subdivisions
    ## Compute sub-meshing points
    x1 = (bounding_box_length - outer_side_length)/2
    box_thickness = (outer_side_length - inner_side_length)/2
    print("Moderator box thickness:", box_thickness)
    x2 = x1 + box_thickness
    x3 = x2 + (inner_side_length)
    x4 = x3 + box_thickness
    test_lattice = Lattice(name="test_lattice", center=(0.0+translation[0], 0.0+translation[1], 0.0+translation[2]))
    
    ### Do MODERATOR regions first
    # Central region : 
    central_region = RectCell(name="central_region", height_x_width=(pitch, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    central_region.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(central_region)
    test_lattice.add_cell(central_region, ())
    
    # Moderator in lower left corner
    moderator_ll = RectCell(name="moderator_ll", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_ll.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_ll)
    test_lattice.add_cell(moderator_ll, ())
    
    # Moderator region in bottom right corner
    moderator_br = RectCell(name="moderator_br", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_br)
    test_lattice.add_cell(moderator_br, ())
    
    # Moderator box covering BOX region
    moderator_tl = RectCell(name="moderator_tl", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_tl)
    test_lattice.add_cell(moderator_tl, ())
    
    # Moderator in bottom middle edge
    moderator_bm = RectCell(name="moderator_bm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_bm)
    test_lattice.add_cell(moderator_bm, ())
    
    # Moderator in top right corner
    moderator_tr = RectCell(name="moderator_tr", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_tr)
    test_lattice.add_cell(moderator_tr, ())
    
    # Moderator in top middle edge
    moderator_tm = RectCell(name="moderator_tm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_tm)
    test_lattice.add_cell(moderator_tm, ())
    
    # Moderator left middle edge
    moderator_lm = RectCell(name="moderator_lm", height_x_width=(pitch, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    moderator_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_lm)
    test_lattice.add_cell(moderator_lm, ())
    
    # Moderator right middle edge
    moderator_rm = RectCell(name="moderator_rm", height_x_width=(pitch, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    moderator_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(moderator_rm)
    test_lattice.add_cell(moderator_rm, ())
    
    ## Corners
    # BOX LL corner
    box_corner_ll = RectCell(name="box_corner_ll", height_x_width=(box_thickness, box_thickness), center=(x1+(box_thickness)/2+translation[0], x1+(box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner_ll.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_ll)
    test_lattice.add_cell(box_corner_ll, ())
    
    # rectangular box to the right of box corner
    box_right = RectCell(name="box_right", height_x_width=(box_thickness,pitch-x2), center=(x2 + (pitch - x2)/2+translation[0], x1+box_thickness/2+translation[1], 0.0+translation[2]))
    box_right.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_right)
    test_lattice.add_cell(box_right, ())
    
    # rectangular box above coolant corner
    box_top = RectCell(name="box_top", height_x_width=(pitch - x2, box_thickness), center=(x1 + box_thickness/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_top.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_top)
    test_lattice.add_cell(box_top, ())
    # box corner on bottom right
    box_corner_br = RectCell(name="box_corner_br", height_x_width=(box_thickness, box_thickness), center=(bounding_box_length - x1 - (box_thickness)/2+translation[0], x1+(box_thickness)/2+translation[1], 0.0+translation[2]))
    #  
    box_corner_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_br)
    test_lattice.add_cell(box_corner_br, ())
    # rectangular box left of box corner
    box_left_br = RectCell(name="box_left_br", height_x_width=(box_thickness,pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], x1 + box_thickness/2+translation[1], 0.0+translation[2]))
    box_left_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_left_br)
    test_lattice.add_cell(box_left_br, ())
    # rectangular box above box corner
    box_top_br = RectCell(name="box_top_br", height_x_width=(pitch - x2, box_thickness), center=(bounding_box_length - box_thickness/2-x1+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_top_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_top_br)
    test_lattice.add_cell(box_top_br, ())
    # box covering coolant corner
    box_corner_tl = RectCell(name="box_corner_tl", height_x_width=(box_thickness, box_thickness), center=(x1+(box_thickness)/2+translation[0], bounding_box_length - x1 - (box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_tl)
    test_lattice.add_cell(box_corner_tl, ())
    # rectangular box to the right of box corner
    box_right_tl = RectCell(name="box_right_tl", height_x_width=(box_thickness,pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length - x1 - box_thickness/2+translation[1], 0.0+translation[2]))
    box_right_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_right_tl)
    test_lattice.add_cell(box_right_tl, ())
    # rectangular box below box corner
    box_bottom_tl = RectCell(name="box_bottom_tl", height_x_width=(pitch - x2, box_thickness), center=(x1 + box_thickness/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_bottom_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_bottom_tl)
    test_lattice.add_cell(box_bottom_tl, ())
    
    # box covering coolant corner
    box_corner_tr = RectCell(name="box_corner_tr", height_x_width=(box_thickness, box_thickness), center=(bounding_box_length - x1 - (box_thickness)/2+translation[0], bounding_box_length - x1 - (box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_tr)
    test_lattice.add_cell(box_corner_tr, ())
    # rectangular box left of box corner
    box_left_tr = RectCell(name="box_left_tr", height_x_width=(box_thickness,pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length - x1 - box_thickness/2+translation[1], 0.0+translation[2]))
    box_left_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_left_tr)
    test_lattice.add_cell(box_left_tr, ())
    # rectangular box below box corner
    box_bottom_tr = RectCell(name="box_bottom_tr", height_x_width=(pitch - x2, box_thickness), center=(bounding_box_length - box_thickness/2 - x1+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_bottom_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_bottom_tr)
    test_lattice.add_cell(box_bottom_tr, ())
    
    # box edge center bottom
    box_edge_cb = RectCell(name="box_edge_cb", height_x_width=(box_thickness, pitch), center=(bounding_box_length/2+translation[0], x1 + box_thickness/2+translation[1], 0.0+translation[2]))
    box_edge_cb.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_cb)
    test_lattice.add_cell(box_edge_cb, ())
    # box edge center top
    box_edge_ct = RectCell(name="box_edge_ct", height_x_width=(box_thickness, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x1 - box_thickness/2+translation[1], 0.0+translation[2]))
    box_edge_ct.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_ct)
    test_lattice.add_cell(box_edge_ct, ())
    # box edge center left
    box_edge_cl = RectCell(name="box_edge_cl", height_x_width=(pitch, box_thickness), center=(x1 + box_thickness/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_edge_cl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_cl)
    test_lattice.add_cell(box_edge_cl, ())
    # box edge center right
    box_edge_cr = RectCell(name="box_edge_cr", height_x_width=(pitch, box_thickness), center=(bounding_box_length - x1 - box_thickness/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_edge_cr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_cr)
    test_lattice.add_cell(box_edge_cr, ())
    
    ## Coolant around moderator box regions
    # Corners
    top_left_corner = RectCell(name="top_left_corner", height_x_width=(x1, x1), center=(x1/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    top_left_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(top_left_corner)
    test_lattice.add_cell(top_left_corner, ())

    top_right_corner = RectCell(name="top_right_corner", height_x_width=(x1, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    top_right_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(top_right_corner)
    test_lattice.add_cell(top_right_corner, ())

    bottom_left_corner = RectCell(name="bottom_left_corner", height_x_width=(x1, x1), center=(x1/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    bottom_left_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(bottom_left_corner)
    test_lattice.add_cell(bottom_left_corner, ())

    bottom_right_corner = RectCell(name="bottom_right_corner", height_x_width=(x1, x1), center=(bounding_box_length - x1/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    bottom_right_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(bottom_right_corner)
    test_lattice.add_cell(bottom_right_corner, ())

    # Top center rectangle :
    top_center_rectangle = RectCell(name="top_center_rectangle", height_x_width=(x1, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    top_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(top_center_rectangle)
    test_lattice.add_cell(top_center_rectangle, ())
    # Bottom center rectangle :
    bottom_center_rectangle = RectCell(name="bottom_center_rectangle", height_x_width=(x1, pitch), center=(bounding_box_length/2+translation[0], x1/2+translation[1], 0.0+translation[2])) 
    bottom_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(bottom_center_rectangle)
    test_lattice.add_cell(bottom_center_rectangle, ())
    # Left center rectangle :
    left_center_rectangle = RectCell(name="left_center_rectangle", height_x_width=(pitch, x1), center=(x1/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    left_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(left_center_rectangle)
    test_lattice.add_cell(left_center_rectangle, ())
    # Right center rectangle :
    right_center_rectangle = RectCell(name="right_center_rectangle", height_x_width=(pitch, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    right_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(right_center_rectangle)
    test_lattice.add_cell(right_center_rectangle, ())
    
    ## Filling small rectangles with coolant : 
    # horizontal rect from bottom left corner to bottom center rectangle
    coolant_bl_to_bc = RectCell(name="coolant_bl_to_bc", height_x_width=(x1, pitch - x1), center=(x1 + (pitch - x1)/2+translation[1], x1/2+translation[0],  0.0+translation[2]))
    coolant_bl_to_bc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_bl_to_bc)
    test_lattice.add_cell(coolant_bl_to_bc, ())
    # horizontal rect from bottom right corner to bottom center rectangle
    coolant_br_to_bc = RectCell(name="coolant_br_to_bc", height_x_width=(x1, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2+translation[1], x1/2+translation[0],  0.0+translation[2]))
    coolant_br_to_bc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_br_to_bc)
    test_lattice.add_cell(coolant_br_to_bc, ())
    # horizontal rect from top left corner to top center rectangle
    coolant_tl_to_tc = RectCell(name="coolant_tl_to_tc", height_x_width=(x1, pitch - x1), center=(x1 + (pitch - x1)/2+translation[1], bounding_box_length - x1/2+translation[0],  0.0+translation[2]))
    coolant_tl_to_tc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_tl_to_tc)
    test_lattice.add_cell(coolant_tl_to_tc, ())
    # horizontal rect from top right corner to top center rectangle
    coolant_tr_to_tc = RectCell(name="coolant_tr_to_tc", height_x_width=(x1, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2+translation[1], bounding_box_length - x1/2+translation[0],  0.0+translation[2]))
    coolant_tr_to_tc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_tr_to_tc)
    test_lattice.add_cell(coolant_tr_to_tc, ())
    # vertical rect from bottom left corner to left center rectangle
    coolant_bl_to_cl = RectCell(name="coolant_bl_to_cl", height_x_width=(pitch - x1, x1), center=(x1/2+translation[0], x1 + (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_bl_to_cl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_bl_to_cl)
    test_lattice.add_cell(coolant_bl_to_cl, ())
    # vertical rect from bottom right corner to right center rectangle
    coolant_br_to_cr = RectCell(name="coolant_br_to_cr", height_x_width=(pitch - x1, x1), center=(bounding_box_length - x1/2+translation[0], x1 + (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_br_to_cr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_br_to_cr)
    test_lattice.add_cell(coolant_br_to_cr, ())
    # vertical rect from top left corner to left center rectangle
    coolant_tl_to_cl = RectCell(name="coolant_tl_to_cl", height_x_width=(pitch - x1, x1), center=(x1/2+translation[0], bounding_box_length - x1 - (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_tl_to_cl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_tl_to_cl)
    test_lattice.add_cell(coolant_tl_to_cl, ())
    # vertical rect from top right corner to right center rectangle
    coolant_tr_to_cr = RectCell(name="coolant_tr_to_cr", height_x_width=(pitch - x1, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x1 - (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_tr_to_cr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_tr_to_cr)
    test_lattice.add_cell(coolant_tr_to_cr, ())
    
    
    test_lattice.show(PropertyType.MATERIAL)

    return test_lattice

if __name__ == "__main__":
    pitch = 1.295
    assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
    channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
    moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
    intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness
    number_subdivisions = 3

    lattice = build_subdivisions_GEO(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, number_subdivisions, translation=(0.0, 0.0, 0.0))


    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/tdt_data/AT10_BOX_TISO_test", TdtSetup(
                                                        geom_type=GeometryType.TECHNOLOGICAL, 
                                                        property_type=PropertyType.MATERIAL,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        ))