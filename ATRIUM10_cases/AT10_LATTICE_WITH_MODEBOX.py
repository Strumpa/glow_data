from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *

def build_subdivisions(bounding_box_length, inner_side_length, outer_side_length, number_subdivisions, water_box_bottom_corner):
    box_elements = []
    pitch = bounding_box_length / number_subdivisions
    ## Compute sub-meshing points
    x1 = (bounding_box_length - outer_side_length)/2
    box_thickness = (outer_side_length - inner_side_length)/2
    print("Moderator box thickness:", box_thickness)
    x2 = x1 + box_thickness
    x3 = x2 + (inner_side_length)
    x4 = x3 + box_thickness
    test_lattice = Lattice(name="test_lattice", center=(15.24/2, 15.24/2, 0.0))

    # Central region : 
    central_region = RectCell(name="central_region", height_x_width=(pitch, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    central_region.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(central_region)
    test_lattice.add_cell(central_region, ())

    # Corners : add overlapping cells to build bounding box.
    
    ### Bottom left corner
    coolant_corner = RectCell(name="coolant_corner", height_x_width=(pitch,pitch), center=(pitch/2 + water_box_bottom_corner[0], pitch/2 + water_box_bottom_corner[1], 0.0))
    coolant_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner)
    test_lattice.add_cell(coolant_corner, ())
    # box covering coolant corner
    box_corner = RectCell(name="box_corner", height_x_width=(pitch-x1, pitch-x1), center=(x1+(pitch-x1)/2 + water_box_bottom_corner[0], x1+(pitch-x1)/2 + water_box_bottom_corner[1], 0.0))
    box_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner)
    test_lattice.add_cell(box_corner, ())
    # Moderator box covering BOX region
    box_moderator = RectCell(name="box_moderator", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2 + water_box_bottom_corner[0], x2 + (pitch - x2)/2 + water_box_bottom_corner[1], 0.0))
    box_moderator.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator)
    test_lattice.add_cell(box_moderator, ())


    # Bottom right corner
    coolant_corner_br = RectCell(name="coolant_corner_br", height_x_width=(pitch,pitch), center=(bounding_box_length - pitch/2 + water_box_bottom_corner[0], pitch/2 + water_box_bottom_corner[1], 0.0))
    coolant_corner_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner_br)
    test_lattice.add_cell(coolant_corner_br, ())
    # box covering coolant corner
    box_corner_br = RectCell(name="box_corner_br", height_x_width=(pitch-x1, pitch-x1), center=(bounding_box_length - x1 - (pitch - x1)/2 + water_box_bottom_corner[0], x1+(pitch-x1)/2 + water_box_bottom_corner[1], 0.0))
    #  
    box_corner_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_br)
    test_lattice.add_cell(box_corner_br, ())
    # Moderator box covering BOX region
    box_moderator_br = RectCell(name="box_moderator_br", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2 + water_box_bottom_corner[0], x2 + (pitch - x2)/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_br)
    test_lattice.add_cell(box_moderator_br, ())

    ### Top left corner
    coolant_corner_tl = RectCell(name="coolant_corner_tl", height_x_width=(pitch,pitch), center=(pitch/2 + water_box_bottom_corner[0], bounding_box_length - pitch/2 + water_box_bottom_corner[1], 0.0))
    coolant_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner_tl)
    test_lattice.add_cell(coolant_corner_tl, ())
    # box covering coolant corner
    box_corner_tl = RectCell(name="box_corner_tl", height_x_width=(pitch-x1, pitch-x1), center=(x1+(pitch-x1)/2 + water_box_bottom_corner[0], bounding_box_length - x1 - (pitch - x1)/2 + water_box_bottom_corner[1], 0.0)) 
    box_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_tl)
    test_lattice.add_cell(box_corner_tl, ())
    # Moderator box covering BOX region
    box_moderator_tl = RectCell(name="box_moderator_tl", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2 + water_box_bottom_corner[0], bounding_box_length - x2 - (pitch - x2)/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tl)
    test_lattice.add_cell(box_moderator_tl, ())

    ### Top right corner
    cooalant_corner_tr = RectCell(name="coolant_corner_tr", height_x_width=(pitch,pitch), center=(bounding_box_length - pitch/2 + water_box_bottom_corner[0], bounding_box_length - pitch/2 + water_box_bottom_corner[1], 0.0))
    cooalant_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(cooalant_corner_tr)
    test_lattice.add_cell(cooalant_corner_tr, ())
    # box covering coolant corner
    box_corner_tr = RectCell(name="box_corner_tr", height_x_width=(pitch-x1, pitch-x1), center=(bounding_box_length - x1 - (pitch - x1)/2 + water_box_bottom_corner[0], bounding_box_length - x1 - (pitch - x1)/2 + water_box_bottom_corner[1], 0.0))
    #  
    box_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_tr)
    test_lattice.add_cell(box_corner_tr, ())
    # Moderator box covering BOX region
    box_moderator_tr = RectCell(name="box_moderator_tr", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2 + water_box_bottom_corner[0], bounding_box_length - x2 - (pitch - x2)/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tr)
    test_lattice.add_cell(box_moderator_tr, ())

    ### Bottom middle edge
    coolant_edge_bm = RectCell(name="coolant_edge_bm", height_x_width=(pitch, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], pitch/2 + water_box_bottom_corner[1], 0.0))
    coolant_edge_bm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_bm)
    test_lattice.add_cell(coolant_edge_bm, ())
    # box covering coolant edge
    box_edge_bm = RectCell(name="box_edge_bm", height_x_width=(pitch - x1, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], x1 + (pitch - x1)/2 + water_box_bottom_corner[1], 0.0))
    box_edge_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_bm)
    test_lattice.add_cell(box_edge_bm, ())
    # Moderator box covering BOX region
    box_moderator_bm = RectCell(name="box_moderator_bm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], x2 + (pitch - x2)/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_bm)
    test_lattice.add_cell(box_moderator_bm, ())

    ### Top middle edge
    coolant_edge_tm = RectCell(name="coolant_edge_tm", height_x_width=(pitch, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], bounding_box_length - pitch/2 + water_box_bottom_corner[1], 0.0))
    coolant_edge_tm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_tm)
    test_lattice.add_cell(coolant_edge_tm, ())
    # box covering coolant edge
    box_edge_tm = RectCell(name="box_edge_tm", height_x_width=(pitch - x1, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], bounding_box_length - x1 - (pitch - x1)/2 + water_box_bottom_corner[1], 0.0))
    box_edge_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_tm)
    test_lattice.add_cell(box_edge_tm, ())
    # Moderator box covering BOX region
    box_moderator_tm = RectCell(name="box_moderator_tm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2 + water_box_bottom_corner[0], bounding_box_length - x2 - (pitch - x2)/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tm)
    test_lattice.add_cell(box_moderator_tm, ())
    
    ### Left middle edge
    coolant_edge_lm = RectCell(name="coolant_edge_lm", height_x_width=(pitch, pitch), center=(pitch/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    coolant_edge_lm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_lm)
    test_lattice.add_cell(coolant_edge_lm, ())
    # box covering coolant edge
    box_edge_lm = RectCell(name="box_edge_lm", height_x_width=(pitch, pitch - x1), center=(x1 + (pitch - x1)/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    box_edge_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_lm)
    test_lattice.add_cell(box_edge_lm, ())
    # Moderator box covering BOX region
    box_moderator_lm = RectCell(name="box_moderator_lm", height_x_width=(pitch, pitch - x2), center=(x2 + (pitch - x2)/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_lm)
    test_lattice.add_cell(box_moderator_lm, ())


    ### Right middle edge
    coolant_edge_rm = RectCell(name="coolant_edge_rm", height_x_width=(pitch, pitch), center=(bounding_box_length - pitch/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    coolant_edge_rm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_rm)
    test_lattice.add_cell(coolant_edge_rm, ())
    # box covering coolant edge
    box_edge_rm = RectCell(name="box_edge_rm", height_x_width=(pitch, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    box_edge_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_rm)
    test_lattice.add_cell(box_edge_rm, ())
    # Moderator box covering BOX region
    box_moderator_rm = RectCell(name="box_moderator_rm", height_x_width=(pitch, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2 + water_box_bottom_corner[0], bounding_box_length/2 + water_box_bottom_corner[1], 0.0))
    box_moderator_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_rm)
    test_lattice.add_cell(box_moderator_rm, ())


    #test_lattice.show(PropertyType.MATERIAL)
    return box_elements


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

    # Corners : add overlapping cells to build bounding box.
    ### Bottom left corner
    coolant_corner = RectCell(name="coolant_corner", height_x_width=(x1,x1), center=(x1/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    coolant_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner)
    test_lattice.add_cell(coolant_corner, ())
    
    
    # Coolant vertical rectangle right of bottom left corner
    coolant_vert_right = RectCell(name="coolant_vert_right", height_x_width=(x1, box_thickness), center=(x1+(box_thickness)/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    coolant_vert_right.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_vert_right)
    test_lattice.add_cell(coolant_vert_right, ())
    # Coolant horizontal rectangle above bottom left corner
    coolant_horiz_above = RectCell(name="coolant_horiz_above", height_x_width=(box_thickness, x1), center=(x1/2+translation[0], x1+(box_thickness)/2+translation[1], 0.0+translation[2]))
    coolant_horiz_above.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_horiz_above)
    test_lattice.add_cell(coolant_horiz_above, ())
    
    # long coolant rectangle to the right of bottom left corner
    coolant_long_right = RectCell(name="coolant_long_right", height_x_width=(x1, pitch-x2), center=(x2 + (pitch - x2)/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    coolant_long_right.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_right)
    test_lattice.add_cell(coolant_long_right, ())
    # long coolant rectangle above bottom left corner
    coolant_long_above = RectCell(name="coolant_long_above", height_x_width=(pitch-x2, x1), center=(x1/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    coolant_long_above.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_above)
    test_lattice.add_cell(coolant_long_above, ())
    
    
    
    # box covering coolant corner
    box_corner = RectCell(name="box_corner", height_x_width=(box_thickness, box_thickness), center=(x1+(box_thickness)/2+translation[0], x1+(box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner)
    test_lattice.add_cell(box_corner, ())
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

    # Moderator in lower left corner
    box_moderator = RectCell(name="box_moderator", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_moderator.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator)
    test_lattice.add_cell(box_moderator, ())


    # Bottom right corner
    coolant_corner_br = RectCell(name="coolant_corner_br", height_x_width=(x1,x1), center=(bounding_box_length - (x1)/2+translation[0], (x1)/2+translation[1], 0.0+translation[2]))
    coolant_corner_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner_br)
    test_lattice.add_cell(coolant_corner_br, ())
    # little rectangle left of bottom right corner
    coolant_vert_left_br = RectCell(name="coolant_vert_left_br", height_x_width=(x1, box_thickness), center=(bounding_box_length - x1 - (box_thickness)/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    coolant_vert_left_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_vert_left_br)
    test_lattice.add_cell(coolant_vert_left_br, ())
    # little rectangle above bottom right corner
    coolant_horiz_above_br = RectCell(name="coolant_horiz_above_br", height_x_width=(box_thickness,x1), center=(bounding_box_length - x1/2+translation[0], x1 + (box_thickness)/2+translation[1], 0.0+translation[2]))
    coolant_horiz_above_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_horiz_above_br)
    test_lattice.add_cell(coolant_horiz_above_br, ())
    # long rectangle to the left of bottom right corner
    coolant_long_left_br = RectCell(name="coolant_long_left_br", height_x_width=(x1, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    coolant_long_left_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_left_br)
    test_lattice.add_cell(coolant_long_left_br, ())
    # long rectangle above bottom right corner
    coolant_long_above_br = RectCell(name="coolant_long_above_br", height_x_width=(pitch - x2, x1), center=(bounding_box_length - x1/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    coolant_long_above_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_above_br)
    test_lattice.add_cell(coolant_long_above_br, ())

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
    
    # Moderator region in bottom right corner
    box_moderator_br = RectCell(name="box_moderator_br", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_moderator_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_br)
    test_lattice.add_cell(box_moderator_br, ())
    

    ### Top left corner
    coolant_corner_tl = RectCell(name="coolant_corner_tl", height_x_width=(x1,x1), center=(x1/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    coolant_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner_tl)
    test_lattice.add_cell(coolant_corner_tl, ())
    # little rectangle right of top left corner
    coolant_vert_right_tl = RectCell(name="coolant_vert_right_tl", height_x_width=(x1, box_thickness), center=(x1 + (box_thickness)/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    coolant_vert_right_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_vert_right_tl)
    test_lattice.add_cell(coolant_vert_right_tl, ())
    # little rectangle below top left corner
    coolant_horiz_below_tl = RectCell(name="coolant_horiz_below_tl", height_x_width=(box_thickness,x1), center=(x1/2+translation[0], bounding_box_length - x1 - (box_thickness)/2+translation[1], 0.0+translation[2]))
    coolant_horiz_below_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_horiz_below_tl)
    test_lattice.add_cell(coolant_horiz_below_tl, ())
    # long rectangle to the right of top left corner
    coolant_long_right_tl = RectCell(name="coolant_long_right_tl", height_x_width=(x1, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    coolant_long_right_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_right_tl)
    test_lattice.add_cell(coolant_long_right_tl, ())
    # long rectangle below top left corner
    coolant_long_below_tl = RectCell(name="coolant_long_below_tl", height_x_width=(pitch - x2, x1), center=(x1/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    coolant_long_below_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_below_tl)
    test_lattice.add_cell(coolant_long_below_tl, ())
    
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
    
    # Moderator box covering BOX region
    box_moderator_tl = RectCell(name="box_moderator_tl", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_moderator_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tl)
    test_lattice.add_cell(box_moderator_tl, ())

    ### Top right corner
    coolant_corner_tr = RectCell(name="coolant_corner_tr", height_x_width=(x1,x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    coolant_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner_tr)
    test_lattice.add_cell(coolant_corner_tr, ())
    # little rectangle left of top right corner
    coolant_vert_left_tr = RectCell(name="coolant_vert_left_tr", height_x_width=(x1, box_thickness), center=(bounding_box_length - x1 - (box_thickness)/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    coolant_vert_left_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_vert_left_tr)
    test_lattice.add_cell(coolant_vert_left_tr, ())
    # little rectangle below top right corner
    coolant_horiz_below_tr = RectCell(name="coolant_horiz_below_tr", height_x_width=(box_thickness,x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x1 - (box_thickness)/2+translation[1], 0.0+translation[2]))
    coolant_horiz_below_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_horiz_below_tr)
    test_lattice.add_cell(coolant_horiz_below_tr, ())
    # long rectangle to the left of top right corner
    coolant_long_left_tr = RectCell(name="coolant_long_left_tr", height_x_width=(x1, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    coolant_long_left_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_left_tr)
    test_lattice.add_cell(coolant_long_left_tr, ())
    # long rectangle below top right corner
    coolant_long_below_tr = RectCell(name="coolant_long_below_tr", height_x_width=(pitch - x2, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    coolant_long_below_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_long_below_tr)
    test_lattice.add_cell(coolant_long_below_tr, ())
    
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
    
    # Moderator in top right corner
    box_moderator_tr = RectCell(name="box_moderator_tr", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_moderator_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tr)
    test_lattice.add_cell(box_moderator_tr, ())



    ### Bottom middle edge
    coolant_edge_bm = RectCell(name="coolant_edge_bm", height_x_width=(pitch, pitch), center=(bounding_box_length/2+translation[0], pitch/2+translation[1], 0.0+translation[2]))
    coolant_edge_bm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_bm)
    test_lattice.add_cell(coolant_edge_bm, ())
    # box covering coolant edge
    box_edge_bm = RectCell(name="box_edge_bm", height_x_width=(pitch - x1, pitch), center=(bounding_box_length/2+translation[0], x1 + (pitch - x1)/2+translation[1], 0.0+translation[2]))
    box_edge_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_bm)
    test_lattice.add_cell(box_edge_bm, ())
    # Moderator box covering BOX region
    box_moderator_bm = RectCell(name="box_moderator_bm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_moderator_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_bm)
    test_lattice.add_cell(box_moderator_bm, ())

    ### Top middle edge
    coolant_edge_tm = RectCell(name="coolant_edge_tm", height_x_width=(pitch, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - pitch/2+translation[1], 0.0+translation[2]))
    coolant_edge_tm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_tm)
    test_lattice.add_cell(coolant_edge_tm, ())
    # box covering coolant edge
    box_edge_tm = RectCell(name="box_edge_tm", height_x_width=(pitch - x1, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x1 - (pitch - x1)/2+translation[1], 0.0+translation[2]))
    box_edge_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_tm)
    test_lattice.add_cell(box_edge_tm, ())
    # Moderator box covering BOX region
    box_moderator_tm = RectCell(name="box_moderator_tm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_moderator_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tm)
    test_lattice.add_cell(box_moderator_tm, ())
    
    ### Left middle edge
    coolant_edge_lm = RectCell(name="coolant_edge_lm", height_x_width=(pitch, pitch), center=(pitch/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    coolant_edge_lm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_lm)
    test_lattice.add_cell(coolant_edge_lm, ())
    # box covering coolant edge
    box_edge_lm = RectCell(name="box_edge_lm", height_x_width=(pitch, pitch - x1), center=(x1 + (pitch - x1)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_edge_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_lm)
    test_lattice.add_cell(box_edge_lm, ())
    # Moderator box covering BOX region
    box_moderator_lm = RectCell(name="box_moderator_lm", height_x_width=(pitch, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_moderator_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_lm)
    test_lattice.add_cell(box_moderator_lm, ())


    ### Right middle edge
    coolant_edge_rm = RectCell(name="coolant_edge_rm", height_x_width=(pitch, pitch), center=(bounding_box_length - pitch/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    coolant_edge_rm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_rm)
    test_lattice.add_cell(coolant_edge_rm, ())
    # box covering coolant edge
    box_edge_rm = RectCell(name="box_edge_rm", height_x_width=(pitch, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    #  
    box_edge_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_rm)
    test_lattice.add_cell(box_edge_rm, ())
    # Moderator box covering BOX region
    box_moderator_rm = RectCell(name="box_moderator_rm", height_x_width=(pitch, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_moderator_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_rm)
    test_lattice.add_cell(box_moderator_rm, ())

    # Central region : 
    central_region = RectCell(name="central_region", height_x_width=(pitch, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    central_region.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(central_region)
    test_lattice.add_cell(central_region, ())

    #test_lattice.show(PropertyType.MATERIAL)
    
    return box_elements


def build_subdivisions_GEO_fixed(bounding_box_length, inner_side_length, outer_side_length, number_subdivisions, translation=(0.0,0.0,0.0)):
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
    
    
    #test_lattice.show(PropertyType.MATERIAL)

    return box_elements

tracking_type = "TISO" # "TSPC"

pitch = 1.295
assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness
number_subdivisions = 3

pincell_translation = water_gap_width+channel_box_thickness+intra_assembly_water_gap_width
water_box_bottom_corner = (4*pitch+pincell_translation, 4*pitch+pincell_translation, 0.0)
print("Water box bottom corner:", water_box_bottom_corner)

# Build the cell1's geometry layout by adding three circular regions
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell5 = RectCell(name="C5", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell6 = RectCell(name="C6", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell7 = RectCell(name="C7", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell8 = RectCell(name="C8", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))


radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
radiiGd = [0.19834, 0.28049, 0.34353, 0.39668, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
for radius in radii:
    cell1.add_circle(radius)
    cell2.add_circle(radius)
    cell3.add_circle(radius)
    cell4.add_circle(radius)
    cell5.add_circle(radius)
    cell6.add_circle(radius)
for radius in radiiGd:
    cell7.add_circle(radius)
    cell8.add_circle(radius)
# Assign the materials to each zone in the cell1
cell1.set_properties(
    {PropertyType.MATERIAL: ["24UOX", "24UOX", "24UOX", "24UOX", "GAP", "CLAD", "COOLANT"]}
)
cell2.set_properties(
    {PropertyType.MATERIAL: ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD", "COOLANT"]}
)
cell3.set_properties(
     {PropertyType.MATERIAL: ["42UOX", "42UOX", "42UOX", "42UOX", "GAP", "CLAD", "COOLANT"]}
)
cell4.set_properties(
    {PropertyType.MATERIAL: ["45UOX", "45UOX", "45UOX", "45UOX", "GAP", "CLAD", "COOLANT"]}
)
cell5.set_properties(
    {PropertyType.MATERIAL: ["48UOX", "48UOX", "48UOX", "48UOX", "GAP", "CLAD", "COOLANT"]}
)
cell6.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"]}
)
cell7.set_properties(
    {PropertyType.MATERIAL: ["45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "GAP", "CLAD", "COOLANT"]}
)
cell8.set_properties(
    {PropertyType.MATERIAL: ["42Gd", "42Gd", "42Gd", "42Gd", "42Gd", "42Gd", "GAP", "CLAD", "COOLANT"]}
)

# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='ATRIUM-10 Lattice with moderator box', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 1)
"""
    C1 C2 C3 C5 C6 C5 C4 C3 C2 C1
    C2 C4 C7 C6 C7 C6 C6 C7 C4 C2
    C3 C7 C6 C6 C6 C7 C6 C6 C7 C3
    C5 C6 C6 C6 C6 C6 C7 C6 C5 C4
    C6 C7 C6 C6 W1 WB W2 C4 C6 C4
    C5 C6 C7 C6 WL W0 WR C3 C7 C4
    C4 C6 C6 C7 W3 WT W4 C4 C4 C4
    C3 C7 C6 C6 C4 C3 C4 C4 C8 C3
    C2 C4 C7 C5 C6 C7 C4 C8 C4 C2
    C1 C2 C3 C4 C4 C4 C4 C3 C2 C1
"""
lattice.add_cell(cell1, ((1/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((3/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell5, ((7/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((9/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell5, ((11/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((13/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((15/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((17/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell1, ((19/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
# Second row
lattice.add_cell(cell2, ((1/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((3/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((5/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((7/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((9/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((11/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((13/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((15/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((17/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((19/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
# Third row
lattice.add_cell(cell3, ((1/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((3/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((7/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((9/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((11/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((13/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((15/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((17/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((19/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
# Fourth row
lattice.add_cell(cell5, ((1/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((3/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((7/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((9/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((11/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((13/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((15/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell5, ((17/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((19/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
# Fifth row
lattice.add_cell(cell6, ((1/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((3/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((7/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((15/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((17/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((19/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
# Sixth row
lattice.add_cell(cell5, ((1/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((3/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((5/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((7/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((15/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((17/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((19/2)*pitch+pincell_translation, (11/2)*pitch+pincell_translation, 0.0))
# Seventh row
lattice.add_cell(cell4, ((1/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((3/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((7/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((15/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((17/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((19/2)*pitch+pincell_translation, (13/2)*pitch+pincell_translation, 0.0))

# Eighth row
lattice.add_cell(cell3, ((1/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((3/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((7/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((9/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((11/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((13/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((15/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell8, ((17/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((19/2)*pitch+pincell_translation, (15/2)*pitch+pincell_translation, 0.0))
# Ninth row
lattice.add_cell(cell2, ((1/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((3/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((5/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell5, ((7/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell6, ((9/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell7, ((11/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((13/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell8, ((15/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((17/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((19/2)*pitch+pincell_translation, (17/2)*pitch+pincell_translation, 0.0))

# Tenth row
lattice.add_cell(cell1, ((1/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((3/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((7/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((9/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((11/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((13/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((15/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((17/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell1, ((19/2)*pitch+pincell_translation, (19/2)*pitch+pincell_translation, 0.0))

box_elements = build_subdivisions_GEO_fixed(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, number_subdivisions, water_box_bottom_corner)
for element in box_elements:
    lattice.add_cell(element, ())

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MATERIAL)


# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/glow_data/tdt_data/AT10_lattice_MODEBOX_TISO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
elif tracking_type == "TSPC":
    lattice.type_geo = LatticeGeometryType.RECTANGLE_SYM
    analyse_and_generate_tdt(
    [lattice], 
    "data/glow_data/tdt_data/AT10_lattice_MODEBOX_TSPC", 
    TdtSetup(GeometryType.SECTORIZED, 
            property_type=PropertyType.MATERIAL,
            type_geo=LatticeGeometryType.RECTANGLE_SYM,
            symmetry_type=BoundaryType.AXIAL_SYMMETRY),
    #compound_to_export=make_partition([r.face for r in lattice.regions], [], ShapeType.COMPOUND)
)