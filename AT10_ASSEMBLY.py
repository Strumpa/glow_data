from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


# --------------------
# TRACKING TYPE
# --------------------

tracking_type = "TSPC" # "TSPC"

# --------------------
# GEOMETRY PARAMETERS
# --------------------
    

pitch = 1.295

assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness

lattice_side_length = 10*pitch


pincell_translation = water_gap_width+channel_box_thickness+intra_assembly_water_gap_width

# Build the cell1's geometry layout by adding three circular regions
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell5 = RectCell(name="C5", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell6 = RectCell(name="C6", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell7 = RectCell(name="C7", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell8 = RectCell(name="C8", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
#water_square = RectCell(name="W0", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
water_surrounding_assembly = RectCell(name="water_blade", height_x_width=(assembly_pitch, assembly_pitch), center=(assembly_pitch/2, assembly_pitch/2, 0.0))
outer_assembly_box = RectCell(name="outer_assembly_box", height_x_width=(channel_box_outer_side, channel_box_outer_side), center=(assembly_pitch/2, assembly_pitch/2, 0.0))
inner_assembly_box = RectCell(name="inner_assembly_box", height_x_width=(channel_box_inner_side, channel_box_inner_side), center=(assembly_pitch/2, assembly_pitch/2, 0.0))
outer_moderation_box = RectCell(name="outer_moderation_box", height_x_width=(moder_box_outer_side, moder_box_outer_side), center=(assembly_pitch/2+pitch/2, assembly_pitch/2+pitch/2, 0.0))
inner_moderation_box = RectCell(name="inner_moderation_box", height_x_width=(moder_box_inner_side, moder_box_inner_side), center=(assembly_pitch/2+pitch/2, assembly_pitch/2+pitch/2, 0.0)) 


# Define radii for the fuel regions, gap and cladding
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
outer_moderation_box.set_properties(
    {PropertyType.MATERIAL: ["MODERATOR_BOX"]}
)
inner_moderation_box.set_properties(
    {PropertyType.MATERIAL: ["MODERATOR"]}
)
water_surrounding_assembly.set_properties(
    {PropertyType.MATERIAL: ["MODERATOR"]}
)
outer_assembly_box.set_properties(
    {PropertyType.MATERIAL: ["CHANNEL_BOX"]}
)
inner_assembly_box.set_properties(
    {PropertyType.MATERIAL: ["COOLANT"]}
)
# Apply the cell1's sectorization
cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)
#outer_moderation_box.sectorize([16], [0])


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='AT10 Assembly Lattice', center=(assembly_pitch/2, assembly_pitch/2, 0.0))
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
lattice.add_cell(water_surrounding_assembly, ())
lattice.add_cell(outer_assembly_box, ())
lattice.add_cell(inner_assembly_box, ())
lattice.add_cell(outer_moderation_box, ())
lattice.add_cell(inner_moderation_box, ())
lattice.show(PropertyType.MATERIAL)
# First row
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

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(geometry_type_to_show=GeometryType.SECTORIZED, property_type_to_show=PropertyType.MATERIAL)

# Build the cell representing the lattice's box so that it sligthly cuts
# the outmost ring of cells; the box is subdivided by means of squares at
# its corners. The dimensions of the lattice are extracted to get the box
# dimensions.

# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/tdt_data/AT10_assembly_TISO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_type=PropertyType.MATERIAL,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
elif tracking_type == "TSPC":
    lattice.type_geo = LatticeGeometryType.RECTANGLE_SYM
    analyse_and_generate_tdt(
    [lattice], "data/tdt_data/AT10_assembly_TSPC", TdtSetup(GeometryType.SECTORIZED, 
                                                            property_type=PropertyType.MATERIAL,
                                                            type_geo=LatticeGeometryType.RECTANGLE_SYM,
                                                            symmetry_type=BoundaryType.AXIAL_SYMMETRY))