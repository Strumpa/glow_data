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
    #  
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

tracking_type = "TISO" # "TSPC"

pitch = 1.295
assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness
number_subdivisions = 3

pincell_translation = 1.0
water_box_bottom_corner = (1*pitch+pincell_translation, 1*pitch+pincell_translation, 0.0)
print("Water box bottom corner:", water_box_bottom_corner)

# Build the cell1's geometry layout by adding three circular regions
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell5 = RectCell(name="C5", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))


radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
for radius in radii:
    cell1.add_circle(radius)
    cell2.add_circle(radius)
    cell3.add_circle(radius)
    cell4.add_circle(radius)
    cell5.add_circle(radius)
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

# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='ATRIUM-10 Lattice with moderator box', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 1)
"""
 C1 C2 C3 C4 C5 
 C2 W1 WB W2 C4 
 C3 WL W0 WR C3 
 C4 W3 WT W4 C2
 C5 C4 C3 C2 C1 
"""
print("Adding cells to lattice...")
# First row
print(f"Position of first cell center: {(1/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0}")
lattice.add_cell(cell1, ((1/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((3/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((7/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell5, ((9/2)*pitch+pincell_translation, (1/2)*pitch+pincell_translation, 0.0))
# Second row
lattice.add_cell(cell2, ((1/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((9/2)*pitch+pincell_translation, (3/2)*pitch+pincell_translation, 0.0))
# Third row
lattice.add_cell(cell3, ((1/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((9/2)*pitch+pincell_translation, (5/2)*pitch+pincell_translation, 0.0))
# Fourth row
lattice.add_cell(cell4, ((1/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((9/2)*pitch+pincell_translation, (7/2)*pitch+pincell_translation, 0.0))
# Fifth row
lattice.add_cell(cell5, ((1/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell4, ((3/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell2, ((7/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.add_cell(cell1, ((9/2)*pitch+pincell_translation, (9/2)*pitch+pincell_translation, 0.0))
lattice.show(PropertyType.MATERIAL)

box_elements = build_subdivisions_GEO(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, number_subdivisions, water_box_bottom_corner)
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
    [lattice], "data/tdt_data/AT10_test_MODEBOX_TISO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_type=PropertyType.MATERIAL,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))