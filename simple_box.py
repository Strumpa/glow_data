from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


def make_simple_box(pitch: float):
    #lattice = build_subdivisions_GEO(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, number_subdivisions, translation=(0.0, 0.0, 0.0))

    lattice = Lattice(name="test_simple_box", center=(0.0, 0.0, 0.0))
    
    # Central region : 
    central_region = RectCell(name="central_region", height_x_width=(pitch, pitch), center=(3*pitch/2, 3*pitch/2, 0.0))
    central_region.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    
    # Center top : 
    center_top = RectCell(name="center_top", height_x_width=(pitch, pitch), center=(3*pitch/2, 5*pitch/2, 0.0))
    center_top.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    # Center bottom :
    center_bottom = RectCell(name="center_bottom", height_x_width=(pitch, pitch), center=(3*pitch/2, pitch/2, 0.0))
    center_bottom.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    # Center left :
    center_left = RectCell(name="center_left", height_x_width=(pitch, pitch), center=(pitch/2, 3*pitch/2, 0.0))
    center_left.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    # Center right :
    center_right = RectCell(name="center_right", height_x_width=(pitch, pitch), center=(5*pitch/2, 3*pitch/2, 0.0))
    center_right.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )

    # Top left corner : 
    top_corner = RectCell(name="top_corner", height_x_width=(pitch, pitch), center=(pitch/2, 5*pitch/2, 0.0))
    top_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    
    # Top right corner : 
    right_corner = RectCell(name="right_corner", height_x_width=(pitch, pitch), center=(5*pitch/2, 5*pitch/2, 0.0))
    right_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    
    # Bottom left corner : 
    left_corner = RectCell(name="left_corner", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
    left_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    # Bottom right corner : 
    bottom_right_corner = RectCell(name="bottom_right_corner", height_x_width=(pitch, pitch), center=(5*pitch/2, pitch/2, 0.0))
    bottom_right_corner.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    
    lattice.add_cell(central_region, ())
    lattice.add_cell(top_corner, ())
    lattice.add_cell(right_corner, ())
    lattice.add_cell(left_corner, ())
    lattice.add_cell(bottom_right_corner, ())
    lattice.add_cell(center_top, ())
    lattice.add_cell(center_bottom, ())
    lattice.add_cell(center_left, ())
    lattice.add_cell(center_right, ())
    
    
    lattice.show(PropertyType.MATERIAL)

    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/tdt_data/simple_box_fixed", TdtSetup(
                                                    geom_type=GeometryType.TECHNOLOGICAL, 
                                                    property_type=PropertyType.MATERIAL,
                                                    type_geo=LatticeGeometryType.ISOTROPIC,
                                                    ))
    return

def make_box_coolant_moder(pitch:float, moder_box_outer_side: float):
    """
    create a CAR2D with coolant surroounding moderator, no box width.
    IC tracking doesnt work with x1 = (side-moder_box_outer_side)/2
    """
    side = 3*pitch
    lattice = Lattice(name="test_simple_box2", center=(0.0, 0.0, 0.0))
    #background = RectCell(name="background", height_x_width=(3*pitch, 3*pitch), center=(3*pitch/2, 3*pitch/2, 0.0))
    #background.set_properties(
    #    {PropertyType.MATERIAL: ["COOLANT"]}
    #)
    #lattice.add_cell(background, ())    
    
    x1 = (side-moder_box_outer_side)/2
    #x1 = pitch
    print("x1 =", x1)
    print("moder_box_outer_side =", moder_box_outer_side)
    
    # Moderator center box :
    moderator = RectCell(name="moderator", height_x_width=(side-2*x1, side-2*x1), center=(3*pitch/2, 3*pitch/2, 0.0))
    moderator.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"]}
    )
    
    
    # Top center rectangle :
    top_center_rectangle = RectCell(name="top_center_rectangle", height_x_width=(x1, side-2*x1), center=(side/2, side - x1/2, 0.0))
    top_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    
    # Bottom center rectangle :
    bottom_center_rectangle = RectCell(name="bottom_center_rectangle", height_x_width=(x1, side-2*x1), center=(side/2, x1/2, 0.0)) 
    bottom_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    # Left center rectangle :
    left_center_rectangle = RectCell(name="left_center_rectangle", height_x_width=(side-2*x1, x1), center=(x1/2, side/2, 0.0))
    left_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    # Right center rectangle :
    right_center_rectangle = RectCell(name="right_center_rectangle", height_x_width=(side-2*x1, x1), center=(side - x1/2, side/2, 0.0))
    right_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )

    # square coolant x1 by x1
    # top left corner:
    coolant_TL = RectCell(name="coolant_TL", height_x_width=(x1, x1), center=(x1/2, side - x1/2, 0.0))
    coolant_TL.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    # top right :
    coolant_TR = RectCell(name="coolant_TR", height_x_width=(x1, x1), center=(side - x1/2, side - x1/2, 0.0))
    coolant_TR.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    # bottom left :
    coolant_BL = RectCell(name="coolant_BL", height_x_width=(x1, x1), center=(x1/2, x1/2, 0.0))
    coolant_BL.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    
    # bottom right :
    coolant_BR = RectCell(name="coolant_BR", height_x_width=(x1, x1), center=(side - x1/2, x1/2, 0.0))
    coolant_BR.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"]}
    )
    
    lattice.add_cell(moderator, ())
    
    lattice.add_cell(coolant_TL, ())
    lattice.add_cell(coolant_TR, ())
    lattice.add_cell(coolant_BL, ())
    lattice.add_cell(coolant_BR, ())
    
    lattice.add_cell(bottom_center_rectangle, ())
    lattice.add_cell(top_center_rectangle, ())
    lattice.add_cell(left_center_rectangle, ())
    lattice.add_cell(right_center_rectangle, ())
    
    

    
    lattice.show(PropertyType.MATERIAL)

    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/tdt_data/simple_box_coolant_moder", TdtSetup(
                                                    geom_type=GeometryType.TECHNOLOGICAL, 
                                                    property_type=PropertyType.MATERIAL,
                                                    type_geo=LatticeGeometryType.ISOTROPIC,
                                                    ))
    


if __name__ == "__main__":
    pitch = 1.295
    assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
    channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
    moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
    intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness
    number_subdivisions = 3
    
    make_simple_box(pitch)
    make_box_coolant_moder(pitch, moder_box_outer_side)
    
    

    
    
    