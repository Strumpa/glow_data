from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *

pitch = 1.295
# Build the cell's geometry layout by adding three circular regions
cell = RectCell(name="Cartesian cell", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
for radius in radii:
    cell.add_circle(radius)
# Assign the materials to each zone in the cell
cell.set_properties(
      {PropertyType.MATERIAL: [1, 1, 1, 1, 2, 3, 4]}
)
# Apply the cell's sectorization
#cell.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell
lattice = Lattice([cell], 'Cartesian Lattice', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell, 0)
lattice.show(PropertyType.MATERIAL)

# Assemble all the geometric shapes together
# Update the box cell's technological geometry with the assembled one

# Apply the eighth symmetry type to the cartesian lattice
#lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MATERIAL)
#lattice.type_geo = 1 # 0, 1, 2 for TISO tracking, >2 for TSPC tracking
# Perform the geometry analysis and export the TDT file of the surface
# geometry
analyse_and_generate_tdt(
    [lattice], "data/bwr_cartesian_simple_cell", TdtSetup(GeometryType.SECTORIZED))