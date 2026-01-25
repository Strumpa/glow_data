from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *




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
fuel_lattice_side_length = 10 * pin_pitch




#Create the assembly box cell for GE-14 assembly
assembly_cell = RectCell(name="out_of_assembly_moderator", 
                         height_x_width=(assembly_pitch, assembly_pitch), 
                         center=(assembly_pitch/2, assembly_pitch/2, 0.0))
assembly_cell.set_properties(
    {PropertyType.MATERIAL: ["MODERATOR"],
    PropertyType.MACRO: ["MACRO_ASSEMBLY_OUT_MODERATOR"]*1}
)

channel_box_cell = RectCell(name="assembly_channel_box", 
                            height_x_width=(channel_box_outer_side, channel_box_outer_side), 
                            center=(assembly_pitch/2, assembly_pitch/2, 0.0),                                        
                            rounded_corners=[(0, corner_inner_radius_of_curvature+channel_box_thickness), 
                                            (1, corner_inner_radius_of_curvature+channel_box_thickness),
                                            (2, corner_inner_radius_of_curvature+channel_box_thickness), 
                                            (3, corner_inner_radius_of_curvature+channel_box_thickness)])
channel_box_cell.set_properties(
    {PropertyType.MATERIAL: ["CHANNEL_BOX_MATERIAL"],
    PropertyType.MACRO: ["MACRO_ASSEMBLY_CHANNEL_BOX"]*1}
)

coolant_intra_assembly_cell = RectCell(name="intra_assembly_coolant", height_x_width=(channel_box_inner_side, channel_box_inner_side), center=(assembly_pitch/2, assembly_pitch/2, 0.0),
                                        rounded_corners=[(0, corner_inner_radius_of_curvature), (1, corner_inner_radius_of_curvature),
                                                        (2, corner_inner_radius_of_curvature), (3, corner_inner_radius_of_curvature)])
coolant_intra_assembly_cell.set_properties(
    {PropertyType.MATERIAL: ["COOLANT"],
    PropertyType.MACRO: ["MACRO_INTRA_ASSEMBLY_COOLANT"]*1}
)
    
# --------------------
# CREATE COMPOUND GEOMETRY FOR THE ASSEMBLY BOX TO TREAT ROUNDED CORNERS
moderator_face = make_cut(assembly_cell.face, channel_box_cell.face)
box_face = make_cut(channel_box_cell.face, coolant_intra_assembly_cell.face)
cut_geometry = make_compound([moderator_face, box_face, coolant_intra_assembly_cell.face])

moderator_cell = RectCell(name="test_cell", height_x_width=(assembly_pitch, assembly_pitch), center=(assembly_pitch/2, assembly_pitch/2, 0.0))

moderator_cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, cut_geometry)
moderator_cell.set_properties(
    {PropertyType.MATERIAL: ["MODERATOR", "CHANNEL_BOX_MATERIAL", "COOLANT"],
    PropertyType.MACRO: ["MACRO_ASSEMBLY_OUT_MODERATOR", "MACRO_ASSEMBLY_CHANNEL_BOX", "MACRO_INTRA_ASSEMBLY_COOLANT"]}
)
# --------------------

# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='test_lattice', center=(assembly_pitch/2, assembly_pitch/2, 0.0))

# Add assembly box cells
lattice.add_cell(moderator_cell, ())


lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)

# Perform the geometry analysis and export the TDT file of the surface
# geometry

lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice], f"data/glow_data/tdt_data/assembly_box_rounded_corners", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
