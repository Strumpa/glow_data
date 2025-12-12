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
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell6 = RectCell(name="C6", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell7 = RectCell(name="C7", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))

radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
radiiGd = [0.19834, 0.28049, 0.34353, 0.39668, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
for radius in radii:
    cell1.add_circle(radius)
    cell2.add_circle(radius)
    cell3.add_circle(radius)
    cell4.add_circle(radius)
    cell6.add_circle(radius)
for radius in radiiGd:
      cell7.add_circle(radius)
# Assign the materials to each zone in the cell1
cell1.set_properties(
      {PropertyType.MATERIAL: ["24UOX", "24UOX", "24UOX", "24UOX", "GAP", "CLAD", "MODERATOR"]}
)
cell2.set_properties(
      {PropertyType.MATERIAL: ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD", "MODERATOR"]}
)
cell3.set_properties(
      {PropertyType.MATERIAL: ["42UOX", "42UOX", "42UOX", "42UOX", "GAP", "CLAD", "MODERATOR"]}
)
cell4.set_properties(
      {PropertyType.MATERIAL: ["45UOX", "45UOX", "45UOX", "45UOX", "GAP", "CLAD", "MODERATOR"]}
)
cell6.set_properties(
      {PropertyType.MATERIAL: ["50UOX", "50UOX", "50UOX", "50UOX", "GAP", "CLAD", "MODERATOR"]}
)
cell7.set_properties(
      {PropertyType.MATERIAL: ["45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "45Gd", "GAP", "CLAD", "MODERATOR"]}
)
# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice([cell1], 'ATRIUM-10 3x3', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 1)
#    C1 C2 C3
#    C2 C4 C7
#    C3 C7 C6
lattice.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell2, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell4, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell7, ((5/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell3, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell7, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch, (5/2)*pitch, 0.0))

lattice.show(PropertyType.MATERIAL)

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one
lattice.show(PropertyType.MATERIAL)

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MATERIAL)


# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
      lattice.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice], "data/tdt_data/AT10_3x3_cells_TISO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_type=PropertyType.MATERIAL,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
elif tracking_type == "TSPC":
      lattice.type_geo = LatticeGeometryType.RECTANGLE_SYM
      analyse_and_generate_tdt(
      [lattice], "data/tdt_data/AT10_3x3_cells_TSPC", TdtSetup(GeometryType.SECTORIZED, 
                                                            property_type=PropertyType.MATERIAL,
                                                            type_geo=LatticeGeometryType.RECTANGLE_SYM,
                                                            symmetry_type=BoundaryType.AXIAL_SYMMETRY))