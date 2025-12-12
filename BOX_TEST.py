from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


def build_subdivisions(bounding_box_length, inner_side_length, outer_side_length, number_subdivisions):
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
    central_region = RectCell(name="central_region", height_x_width=(pitch, pitch), center=(bounding_box_length/2, bounding_box_length/2, 0.0))
    central_region.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(central_region)
    test_lattice.add_cell(central_region, ())

    # Corners : add overlapping cells to build bounding box.
    ### Bottom left corner
    coolant_corner = RectCell(name="coolant_corner", height_x_width=(pitch,pitch), center=(pitch/2, pitch/2, 0.0))
    coolant_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner)
    test_lattice.add_cell(coolant_corner, ())
    # box covering coolant corner
    box_corner = RectCell(name="box_corner", height_x_width=(pitch-x1, pitch-x1), center=(x1+(pitch-x1)/2, x1+(pitch-x1)/2, 0.0))
    box_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner)
    test_lattice.add_cell(box_corner, ())
    # Moderator box covering BOX region
    box_moderator = RectCell(name="box_moderator", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2, x2 + (pitch - x2)/2, 0.0))
    box_moderator.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator)
    test_lattice.add_cell(box_moderator, ())


    # Bottom right corner
    cooalant_corner_br = RectCell(name="coolant_corner_br", height_x_width=(pitch,pitch), center=(bounding_box_length - pitch/2, pitch/2, 0.0))
    cooalant_corner_br.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(cooalant_corner_br)
    test_lattice.add_cell(cooalant_corner_br, ())
    # box covering coolant corner
    box_corner_br = RectCell(name="box_corner_br", height_x_width=(pitch-x1, pitch-x1), center=(bounding_box_length - x1 - (pitch - x1)/2, x1+(pitch-x1)/2, 0.0))
    #  
    box_corner_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_br)
    test_lattice.add_cell(box_corner_br, ())
    # Moderator box covering BOX region
    box_moderator_br = RectCell(name="box_moderator_br", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2, x2 + (pitch - x2)/2, 0.0))
    box_moderator_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_br)
    test_lattice.add_cell(box_moderator_br, ())

    ### Top left corner
    coolant_corner_tl = RectCell(name="coolant_corner_tl", height_x_width=(pitch,pitch), center=(pitch/2, bounding_box_length - pitch/2, 0.0))
    coolant_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_corner_tl)
    test_lattice.add_cell(coolant_corner_tl, ())
    # box covering coolant corner
    box_corner_tl = RectCell(name="box_corner_tl", height_x_width=(pitch-x1, pitch-x1), center=(x1+(pitch-x1)/2, bounding_box_length - x1 - (pitch - x1)/2, 0.0)) 
    box_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_tl)
    test_lattice.add_cell(box_corner_tl, ())
    # Moderator box covering BOX region
    box_moderator_tl = RectCell(name="box_moderator_tl", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2, bounding_box_length - x2 - (pitch - x2)/2, 0.0))
    box_moderator_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tl)
    test_lattice.add_cell(box_moderator_tl, ())

    ### Top right corner
    cooalant_corner_tr = RectCell(name="coolant_corner_tr", height_x_width=(pitch,pitch), center=(bounding_box_length - pitch/2, bounding_box_length - pitch/2, 0.0))
    cooalant_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(cooalant_corner_tr)
    test_lattice.add_cell(cooalant_corner_tr, ())
    # box covering coolant corner
    box_corner_tr = RectCell(name="box_corner_tr", height_x_width=(pitch-x1, pitch-x1), center=(bounding_box_length - x1 - (pitch - x1)/2, bounding_box_length - x1 - (pitch - x1)/2, 0.0))
    #  
    box_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_corner_tr)
    test_lattice.add_cell(box_corner_tr, ())
    # Moderator box covering BOX region
    box_moderator_tr = RectCell(name="box_moderator_tr", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2, bounding_box_length - x2 - (pitch - x2)/2, 0.0))
    box_moderator_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tr)
    test_lattice.add_cell(box_moderator_tr, ())

    ### Bottom middle edge
    coolant_edge_bm = RectCell(name="coolant_edge_bm", height_x_width=(pitch, pitch), center=(bounding_box_length/2, pitch/2, 0.0))
    coolant_edge_bm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_bm)
    test_lattice.add_cell(coolant_edge_bm, ())
    # box covering coolant edge
    box_edge_bm = RectCell(name="box_edge_bm", height_x_width=(pitch - x1, pitch), center=(bounding_box_length/2, x1 + (pitch - x1)/2, 0.0))
    box_edge_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_bm)
    test_lattice.add_cell(box_edge_bm, ())
    # Moderator box covering BOX region
    box_moderator_bm = RectCell(name="box_moderator_bm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2, x2 + (pitch - x2)/2, 0.0))
    box_moderator_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_bm)
    test_lattice.add_cell(box_moderator_bm, ())

    ### Top middle edge
    coolant_edge_tm = RectCell(name="coolant_edge_tm", height_x_width=(pitch, pitch), center=(bounding_box_length/2, bounding_box_length - pitch/2, 0.0))
    coolant_edge_tm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_tm)
    test_lattice.add_cell(coolant_edge_tm, ())
    # box covering coolant edge
    box_edge_tm = RectCell(name="box_edge_tm", height_x_width=(pitch - x1, pitch), center=(bounding_box_length/2, bounding_box_length - x1 - (pitch - x1)/2, 0.0))
    box_edge_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_tm)
    test_lattice.add_cell(box_edge_tm, ())
    # Moderator box covering BOX region
    box_moderator_tm = RectCell(name="box_moderator_tm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2, bounding_box_length - x2 - (pitch - x2)/2, 0.0))
    box_moderator_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_tm)
    test_lattice.add_cell(box_moderator_tm, ())
    
    ### Left middle edge
    coolant_edge_lm = RectCell(name="coolant_edge_lm", height_x_width=(pitch, pitch), center=(pitch/2, bounding_box_length/2, 0.0))
    coolant_edge_lm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_lm)
    test_lattice.add_cell(coolant_edge_lm, ())
    # box covering coolant edge
    box_edge_lm = RectCell(name="box_edge_lm", height_x_width=(pitch, pitch - x1), center=(x1 + (pitch - x1)/2, bounding_box_length/2, 0.0))
    box_edge_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_lm)
    test_lattice.add_cell(box_edge_lm, ())
    # Moderator box covering BOX region
    box_moderator_lm = RectCell(name="box_moderator_lm", height_x_width=(pitch, pitch - x2), center=(x2 + (pitch - x2)/2, bounding_box_length/2, 0.0))
    box_moderator_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_lm)
    test_lattice.add_cell(box_moderator_lm, ())


    ### Right middle edge
    coolant_edge_rm = RectCell(name="coolant_edge_rm", height_x_width=(pitch, pitch), center=(bounding_box_length - pitch/2, bounding_box_length/2, 0.0))
    coolant_edge_rm.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    box_elements.append(coolant_edge_rm)
    test_lattice.add_cell(coolant_edge_rm, ())
    # box covering coolant edge
    box_edge_rm = RectCell(name="box_edge_rm", height_x_width=(pitch, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2, bounding_box_length/2, 0.0))
    #  
    box_edge_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
    )
    box_elements.append(box_edge_rm)
    test_lattice.add_cell(box_edge_rm, ())
    # Moderator box covering BOX region
    box_moderator_rm = RectCell(name="box_moderator_rm", height_x_width=(pitch, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2, bounding_box_length/2, 0.0))
    box_moderator_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    box_elements.append(box_moderator_rm)
    test_lattice.add_cell(box_moderator_rm, ())


    #test_lattice.show(PropertyType.MATERIAL)
    return box_elements





pitch = 1.295
assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness
number_subdivisions = 3

build_subdivisions(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, number_subdivisions)


    