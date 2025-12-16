## Goal of this script is to define SPLITX and SPLITY for lartesian geometries using GLOW functionnalities.
from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *
from typing import List

def split_rectangle_old(
    parent: RectCell,
    nx: int,
    ny: int,
    material: str
) -> List[RectCell]:
    """
    Split a rectangular region into nx by ny smaller rectangles.

    Parameters
    ----------
    parent : RectCell
        The parent rectangle (width, height, center).
    nx : int
        Number of subdivisions in x-direction.
    ny : int
        Number of subdivisions in y-direction.

    Returns
    -------
    List[RectCell]
        List of nx * ny RectCell objects.
    """

    if nx <= 0 or ny <= 0:
        raise ValueError("nx and ny must be positive integers")

    dx = parent.width / nx
    dy = parent.height / ny

    cx_parent, cy_parent = parent.center[0], parent.center[1]

    # Bottom-left corner of parent in global coordinates
    x0 = cx_parent - parent.width / 2.0
    y0 = cy_parent - parent.height / 2.0

    subcells = []

    for j in range(ny):        # y-direction (bottom → top)
        for i in range(nx):    # x-direction (left → right)

            # Local center in parent frame
            cx_local = (i + 0.5) * dx
            cy_local = (j + 0.5) * dy

            # Global center coordinates
            cx = x0 + cx_local
            cy = y0 + cy_local
            cell =  RectCell(
                    height_x_width=(dy, dx),
                    center=(cx, cy, 0.0)
                )
            cell.set_properties(
                  {PropertyType.MATERIAL: [material]}
            )
            subcells.append(cell)
            

    return subcells
    


# Create dummy rectangular cell for SPLIXY definition
HEIGHT = 20.0 
WIDTH = 5.0


nx = 20  # Number of divisions in X direction
ny = 10  # Number of divisions in Y direction
dummy_cell_center = (10.0, 40.0, 0.0)
cell = RectCell(name="Dummy cell", height_x_width=(HEIGHT, WIDTH), center=dummy_cell_center)
cell.center = dummy_cell_center

subcells = split_rectangle_old(cell, nx, ny, material="MAT_1")

#partitioned_cell = make_partition(
#    [cell.face],
#    [cell2.face],
#    ShapeType.COMPOUND
#)

#cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, partitioned_cell)
lattice = Lattice(name = 'SPLIXY Lattice', center=(0.0, 0.0, 0.0))
for cell in subcells:
    lattice.add_cell(cell, (0.0, 0.0, 0.0))
lattice.show(PropertyType.MATERIAL)


lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
[lattice], "data/tdt_data/dummy_cells", TdtSetup(
                                                    GeometryType.SECTORIZED, 
                                                    property_type=PropertyType.MATERIAL,
                                                    type_geo=LatticeGeometryType.ISOTROPIC,
#                                                            symmetry_type=BoundaryType.AXIAL_SYMMETRY
                                                    ))
