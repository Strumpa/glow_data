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
# numbered in increasing x / increasing y order
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell5 = RectCell(name="C5", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell6 = RectCell(name="C6", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell7 = RectCell(name="C7", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell8 = RectCell(name="C8", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell9 = RectCell(name="C9", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))

radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
radiiGd = [0.19834, 0.28049, 0.34353, 0.39668, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
#    1:C1 2:C2 3:C3
#    4:C2 5:C4 6:C7
#    7:C3 8:C7 9:C6
# 2 and 4 are the same
# 3 and 7 are the same
# 6 and 8 are the same
### Test with diagonal symmetry ?

for radius in radii:
    cell1.add_circle(radius)
    cell2.add_circle(radius)
    cell3.add_circle(radius)
    cell4.add_circle(radius)
    cell5.add_circle(radius)
    cell7.add_circle(radius)
    cell9.add_circle(radius)
for radius in radiiGd:
      cell6.add_circle(radius)
      cell8.add_circle(radius)
# Assign the materials to each zone in the cell1
cell1.set_properties(
      {PropertyType.MATERIAL: ["24UOX", "24UOX", "24UOX", "24UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO1", "MACRO1", "MACRO1", "MACRO1", "MACRO1", "MACRO1", "MACRO1"]
       }
)
cell2.set_properties(
      {PropertyType.MATERIAL: ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO2", "MACRO2", "MACRO2", "MACRO2", "MACRO2", "MACRO2", "MACRO2"]}
)
cell3.set_properties(
      {PropertyType.MATERIAL: ["42UOX", "42UOX", "42UOX", "42UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO3", "MACRO3", "MACRO3", "MACRO3", "MACRO3", "MACRO3", "MACRO3"]}
)
cell4.set_properties(
      {PropertyType.MATERIAL: ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO4", "MACRO4", "MACRO4", "MACRO4", "MACRO4", "MACRO4", "MACRO4"]}
)
cell5.set_properties(
      {PropertyType.MATERIAL: ["45UOX", "45UOX", "45UOX", "45UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO5", "MACRO5", "MACRO5", "MACRO5", "MACRO5", "MACRO5", "MACRO5"]}
)
cell6.set_properties(
      {PropertyType.MATERIAL: ["45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO6", "MACRO6", "MACRO6", "MACRO6", "MACRO6", "MACRO6", "MACRO6", "MACRO6", "MACRO6"]}
)
cell7.set_properties(
      {PropertyType.MATERIAL: ["42UOX", "42UOX", "42UOX", "42UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO7", "MACRO7", "MACRO7", "MACRO7", "MACRO7", "MACRO7", "MACRO7"]}
)
cell8.set_properties(
      {PropertyType.MATERIAL: ["45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO8", "MACRO8", "MACRO8", "MACRO8", "MACRO8", "MACRO8", "MACRO8", "MACRO8", "MACRO8"]}
)
cell9.set_properties(
      {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO9", "MACRO9", "MACRO9", "MACRO9", "MACRO9", "MACRO9", "MACRO9"]}
)

# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice([cell1], 'ATRIUM-10 3x3 - MACROS', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 1)
#    1:C1 2:C2 3:C3
#    4:C2 5:C4 6:C7
#    7:C3 8:C7 9:C6
lattice.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))

# Second row
lattice.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell5, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch, (3/2)*pitch, 0.0))

# Third row
lattice.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell8, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell9, ((5/2)*pitch, (5/2)*pitch, 0.0))

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MACRO)
lattice.show(PropertyType.MATERIAL)


# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
      lattice.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice], "data/glow_data/tdt_data/AT10_3x3_TISO_MACRO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
      