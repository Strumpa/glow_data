## Goal of this script is to define SPLITX and SPLITY for lartesian geometries using GLOW functionnalities.
from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *

# Instead of creating a RectCell per sub-rectangle, build faces from vertices/edges
# using the low-level geometry interface (make_vertex, make_edge, make_face).
# This creates geometric faces for each subdivision and tags them with material.
def make_grid_faces(parent: RectCell, nx: int, ny: int, material: str):
    # parent width/height and lower-left corner
    dx = parent.width / nx
    dy = parent.height / ny
    cx_parent, cy_parent = parent.center[0], parent.center[1]
    x0 = cx_parent - parent.width / 2.0
    y0 = cy_parent - parent.height / 2.0

    # create a (nx+1) x (ny+1) grid of vertices
    verts = []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = x0 + i * dx
            y = y0 + j * dy
            v = make_vertex((x, y, 0.0))
            verts.append(v)

    # helper to index vertex at grid (i,j)
    def v_at(i, j):
        return verts[j * (nx + 1) + i]

    faces = []
    for j in range(ny):
        for i in range(nx):
            # rectangle corners (lower-left, lower-right, upper-right, upper-left)
            v00 = v_at(i, j)
            v10 = v_at(i + 1, j)
            v11 = v_at(i + 1, j + 1)
            v01 = v_at(i, j + 1)

            # create four edges for the rectangle (order matters for consistent orientation)
            e_bottom = make_edge(v00, v10)
            e_right = make_edge(v10, v11)
            e_top = make_edge(v11, v01)
            e_left = make_edge(v01, v00)

            # assemble a face from the four edges
            face = make_face([e_bottom, e_right, e_top, e_left])

            # tag material on the face (face objects typically support set_properties)
            try:
                face.set_properties({PropertyType.MATERIAL: [material]})
            except Exception:
                # some glow versions might attach properties differently; ignore if not supported
                pass

            faces.append(face)

    return faces

# Example usage
width = 5.0
height = 20.0
nx = 20 # number of subdivisions in x
ny = 10  # number of subdivisions in y
cell_center = (10.0, 40.0, 0.0)
radii = [0.5]
cell = RectCell(name="Parent Cell", height_x_width=(height, width), center=cell_center)
for radius in radii:
    cell.add_circle(radius)
# replace previous single-cell material assignment with creation of faces for the grid
cell.set_properties({PropertyType.MATERIAL: ["MAT_1", "MAT_2"]})  # keep a property on the parent if desired
cell.center = cell_center
faces = make_grid_faces(cell, nx, ny, "MAT_1")

# Optionally convert these faces into a partitioned geometry that replaces the cell face
# (uncomment/use if your glow version provides make_partition and cell.update_geometry_from_face)
partitioned = make_partition([cell.face], [f for f in faces], ShapeType.COMPOUND)
cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, partitioned)
lattice = Lattice([cell], 'Dummy Lattice')
lattice.show(PropertyType.MATERIAL)


lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
[lattice], "data/glow_data/tdt_data/dummy_cells", TdtSetup(
                                                    GeometryType.SECTORIZED, 
                                                    property_type=PropertyType.MATERIAL,
                                                    type_geo=LatticeGeometryType.ISOTROPIC,
#                                                            symmetry_type=BoundaryType.AXIAL_SYMMETRY
                                                    ))