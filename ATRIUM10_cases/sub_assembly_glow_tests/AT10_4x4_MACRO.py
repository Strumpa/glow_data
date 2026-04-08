from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *



tracking_type = "TISO" # "TSPC"
pitch = 1.295
# Build the cell1's geometry layout by adding three circular regions
"""
    1:C1   2:C2  3:C3  4:C5
    5:C2   6:C4  7:C7  8:C6
    9:C3  10:C7 11:C6 12:C6
    13:C5 14:C6 15:C6 16:C6 
"""
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell5 = RectCell(name="C5", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell6 = RectCell(name="C6", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell7 = RectCell(name="C7", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell8 = RectCell(name="C8", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell9 = RectCell(name="C9", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell10 = RectCell(name="C10", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell11 = RectCell(name="C11", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell12 = RectCell(name="C12", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell13 = RectCell(name="C13", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell14 = RectCell(name="C14", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell15 = RectCell(name="C15", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell16 = RectCell(name="C16", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
water_square = RectCell(name="W0", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))

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
    cell8.add_circle(radius)
    cell9.add_circle(radius)
    cell11.add_circle(radius)
    cell12.add_circle(radius)
    cell13.add_circle(radius)
    cell14.add_circle(radius)
    cell15.add_circle(radius)
    cell16.add_circle(radius)
for radius in radiiGd:
    cell7.add_circle(radius)
    cell10.add_circle(radius)
# Assign the materials to each zone in the cell1

"""
    1:C1   2:C2  3:C3  4:C5
    5:C2   6:C4  7:C7  8:C6
    9:C3  10:C7 11:C6 12:C6
    13:C5 14:C6 15:C6 16:C6 
"""

dict_C_to_MAT = {
    "C1":"24UOX",
    "C2":"32UOX",
    "C3":"42UOX",
    "C4":"45UOX",
    "C5":"48UOX",
    "C6":"50UOX",
    "C7":"45Gd",
}
## MACRO1
# C1 : 24UOX 
cell1.set_properties(
    {PropertyType.MATERIAL: ["24UOX", "24UOX", "24UOX", "24UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO1"]*7}
)
## MACRO2
# C2 : 32UOX
cell2.set_properties(
    {PropertyType.MATERIAL: ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO2"]*7}
)
## MACRO3
# C3 : 42UOX
cell3.set_properties(
     {PropertyType.MATERIAL: ["42UOX", "42UOX", "42UOX", "42UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO3"]*7}
)
## MACRO4
# C5 : 48UOX
cell4.set_properties(
    {PropertyType.MATERIAL: ["48UOX", "48UOX", "48UOX", "48UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO4"]*7}
)
### MACRO5
# C2 : 32UOX
cell5.set_properties(
    {PropertyType.MATERIAL: ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO5"]*7}
)
### MACRO6
# C4: 45UOX
cell6.set_properties(
    {PropertyType.MATERIAL: ["45UOX", "45UOX", "45UOX", "45UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO6"]*7}
)
### MACRO7
# C7 : 45Gd
cell7.set_properties(
    {PropertyType.MATERIAL: ["45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO7"]*9}
)
### MACRO8
# C6 : 50UOX
cell8.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO8"]*7}
)
### MACRO9 
# C3 : 42UOX
cell9.set_properties(
    {PropertyType.MATERIAL: ["42UOX", "42UOX", "42UOX", "42UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO9"]*7}
)

### MACRO10 
# C7 : 45Gd
cell10.set_properties(
    {PropertyType.MATERIAL: ["45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO10"]*9}
)
### MACRO11
# C6 : 50UOX
cell11.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO11"]*7}
)
### MACRO12
# C6 : 50UOX
cell12.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO12"]*7}
)
### MACRO13
# C5 : 48UOX
cell13.set_properties(
    {PropertyType.MATERIAL: ["48UOX", "48UOX", "48UOX", "48UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO13"]*7}
)
### MACRO14
# C6 : 50UOX
cell14.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO14"]*7}
)
### MACRO15
# C6 : 50UOX
cell15.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO15"]*7}
)
### MACRO16
# C6 : 50UOX
cell16.set_properties(
    {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "COOLANT"],
     PropertyType.MACRO: ["MACRO16"]*7}
)

# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice([cell1], 'ATRIUM-10 4x4 - MACROS', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 1)
"""
    C1 C2 C3 C5
    C2 C4 C7 C6
    C3 C7 C6 C6
    C5 C6 C6 C6 

"""
# First row
#lattice.add_cell(cell1, ((1/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell4, ((7/2)*pitch, (1/2)*pitch, 0.0))

# Second row
lattice.add_cell(cell5, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell6, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell7, ((5/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell8, ((7/2)*pitch, (3/2)*pitch, 0.0))

# Third row
lattice.add_cell(cell9, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell10, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell11, ((5/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell12, ((7/2)*pitch, (5/2)*pitch, 0.0))

# Fourth row
lattice.add_cell(cell13, ((1/2)*pitch, (7/2)*pitch, 0.0))
lattice.add_cell(cell14, ((3/2)*pitch, (7/2)*pitch, 0.0))
lattice.add_cell(cell15, ((5/2)*pitch, (7/2)*pitch, 0.0))
lattice.add_cell(cell16, ((7/2)*pitch, (7/2)*pitch, 0.0))


# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MATERIAL)
lattice.show(PropertyType.MACRO)

# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/glow_data/tdt_data/AT10_4x4_TISO_MACRO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL,PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))