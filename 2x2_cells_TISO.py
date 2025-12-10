from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *

pitch = 1.295
# Build the cell1's geometry layout by adding three circular regions
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
for radius in radii:
    cell1.add_circle(radius)
    cell2.add_circle(radius)
    cell4.add_circle(radius)
# Assign the materials to each zone in the cell1
cell1.set_properties(
      {PropertyType.MATERIAL: [1, 1, 1, 1, 4, 5, 6]}
)
cell2.set_properties(
      {PropertyType.MATERIAL: [2, 2, 2, 2, 4, 5, 6]}
)
cell4.set_properties(
      {PropertyType.MATERIAL: [3, 3, 3, 3, 4, 5, 6]}
)
# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice([cell1], 'Cartesian Lattice', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 3)
lattice.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell4, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell2, ((1/2)*pitch, (3/2)*pitch, 0.0))

lattice.show(PropertyType.MATERIAL)

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one
lattice.show(PropertyType.MATERIAL)

#bounding_box = Rectangle((pitch, pitch, 0.0), 2*pitch, 2*pitch)

#lattice.lattice_box=bounding_box

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MATERIAL)


# Perform the geometry analysis and export the TDT file of the surface
# geometry

analyse_and_generate_tdt(
    [lattice], "data/bwr_cartesian_2x2_cells_TISO", TdtSetup(
                                                        geom_type=GeometryType.TECHNOLOGICAL, 
                                                        property_type=PropertyType.MATERIAL,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
#                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY)
                                                         )
                       )