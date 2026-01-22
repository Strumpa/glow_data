from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *




def create_assembly_box(assembly_pitch, channel_box_outer_side,channel_box_inner_side, corner_inner_radius_of_curvature):
    """
    Create the assembly box cell for GE-14 assembly
    Parameters :
    --------------
        - assembly_pitch : float, assembly pitch (cm)
        - channel_box_inner_side : float, inner side of channel box (cm)
    """
    assembly_cell = RectCell(name="out_of_assembly_moderator", height_x_width=(assembly_pitch, assembly_pitch), center=(assembly_pitch/2, assembly_pitch/2, 0.0),
                                           rounded_corners=[(0, corner_inner_radius_of_curvature), (1, corner_inner_radius_of_curvature),
                                                            (2, corner_inner_radius_of_curvature), (3, corner_inner_radius_of_curvature)])
    assembly_cell.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACRO_ASSEMBLY_OUT_MODERATOR"]*1}
    )

    coolant_intra_assembly_cell = RectCell(name="intra_assembly_coolant", height_x_width=(channel_box_inner_side, channel_box_inner_side), center=(assembly_pitch/2, assembly_pitch/2, 0.0),
                                           rounded_corners=[(0, corner_inner_radius_of_curvature), (1, corner_inner_radius_of_curvature),
                                                            (2, corner_inner_radius_of_curvature), (3, corner_inner_radius_of_curvature)])
    coolant_intra_assembly_cell.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACRO_INTRA_ASSEMBLY_COOLANT"]*1}
    )
    

    return assembly_cell, coolant_intra_assembly_cell




# --------------------
# GEOMETRY PARAMETERS
# --------------------
# Main geometrical dimensions
assembly_pitch = 15.24 # cm
pin_pitch = 1.3
gap_wide = 0.7549
gap_narrow = 0.7549
channel_box_thickness = 0.1651
channel_box_corner_radius = 0.9652

channel_box_inner_side = 15.24 - 2* channel_box_thickness - 2* gap_wide 
channel_box_outer_side = 15.24 - 2* gap_wide
coolant_intra_assembly = (channel_box_inner_side - 10*pin_pitch) / 2
corner_inner_radius_of_curvature = 0.9652


assembly_box_cell, coolant_intra_assembly_cell = create_assembly_box(assembly_pitch=assembly_pitch, 
                                                                                channel_box_outer_side=channel_box_outer_side,
                                                                                channel_box_inner_side=channel_box_inner_side,
                                                                                corner_inner_radius_of_curvature=corner_inner_radius_of_curvature)
# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='big_square_rounded', center=(assembly_pitch/2, assembly_pitch/2, 0.0))
lattice2 = Lattice(name='smaller_square_rounded', center=(assembly_pitch/2, assembly_pitch/2, 0.0))
lattice3 = Lattice(name='big_and_smaller_square_rounded', center=(assembly_pitch/2, assembly_pitch/2, 0.0))

# Add assembly box cells
lattice.add_cell(assembly_box_cell, ())
lattice2.add_cell(coolant_intra_assembly_cell, ())


lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)
lattice2.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)

# Perform the geometry analysis and export the TDT file of the surface
# geometry

lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice], f"data/glow_data/tdt_data/assembly_box_rounded_corners", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))

lattice2.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice2], f"data/glow_data/tdt_data/coolant_intra_assembly_rounded_corners", TdtSetup(GeometryType.SECTORIZED,
                                                        property_types=[PropertyType.MATERIAL],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))


lattice3.add_cell(assembly_box_cell, ())
lattice3.add_cell(coolant_intra_assembly_cell, ())
## This is where the problem occurs when both cells are in the same lattice : 
# calling show() on lattice3 leads to segfault in SALOME
#lattice3.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface
# geometry

# Calling analyse_and_generate_tdt on lattice3 : RuntimeError: Shapes not compatible
lattice3.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice3], f"data/glow_data/tdt_data/assembly_and_coolant_rounded_corners", TdtSetup(GeometryType.SECTORIZED,
                                                        property_types=[PropertyType.MATERIAL],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
    