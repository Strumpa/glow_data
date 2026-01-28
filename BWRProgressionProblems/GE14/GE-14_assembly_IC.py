from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


# --------------------
# HELPER FUNCTIONS
# --------------------
def computeSantamarinaradii(fuel_radius, gap_radius, clad_radius, gadolinium=False):
    """
    Helper to define fuel region radii for fuel pins
    A. Santamarina recommendations:
    - UOX pins: 50%, 80%, 95% and 100% volume fractions
    - Gd2O3 pins: 20%, 40%, 60%, 80%, 95% and 100% volume fractions
    """
    if not gadolinium:
        pin_radii = [
            (0.5**0.5) * fuel_radius,
            (0.8**0.5) * fuel_radius,
            (0.95**0.5) * fuel_radius,
            fuel_radius,
            gap_radius,
            clad_radius
        ]
    else:
        pin_radii = [
            (0.2**0.5) * fuel_radius,
            (0.4**0.5) * fuel_radius,
            (0.6**0.5) * fuel_radius,
            (0.8**0.5) * fuel_radius,
            (0.95**0.5) * fuel_radius,
            fuel_radius,
            gap_radius,
            clad_radius
        ]
    return pin_radii


def generate_cells(lattice_desc, pitch, C_to_mat, fuel_rad, gap_rad, clad_rad, corner_radius=0):
    """
    Generate RectCell objects for each individual subgeometry in the lattice
    
    Parameters:
    -----------
    corner_radius : float, optional
        Radius of curvature for the outer corner of corner fuel cells.
        Only the 4 corner cells (positions (0,0), (0,n-1), (n-1,0), (n-1,n-1)) 
        will have a single rounded corner to match the channel box inner boundary.
    """
    Gd_cells = ["ROD5G", "ROD6H", "ROD6K", "ROD7G", "ROD7H"]
    lattice_components = []
    n_rows = len(lattice_desc)
    n_cols = len(lattice_desc[0]) if lattice_desc else 0
    
    for row_idx in range(n_rows):
        row = lattice_desc[row_idx]
        row_of_cells = []
        for cell_idx in range(len(row)):
            cell_id = row[cell_idx]
            
            # Check if this is a corner cell that needs a rounded corner
            # to match the channel box inner boundary
            rounded_corners = None
            if corner_radius > 0:
                # Corner 0 = bottom-left of cell (row=0, col=0 -> assembly corner)
                # Corner 1 = bottom-right of cell (row=0, col=n_cols-1 -> assembly corner)
                # Corner 2 = top-right of cell (row=n_rows-1, col=n_cols-1 -> assembly corner)
                # Corner 3 = top-left of cell (row=n_rows-1, col=0 -> assembly corner)
                if row_idx == 0 and cell_idx == 0:
                    rounded_corners = [(0, corner_radius)]
                elif row_idx == 0 and cell_idx == n_cols - 1:
                    rounded_corners = [(1, corner_radius)]
                elif row_idx == n_rows - 1 and cell_idx == n_cols - 1:
                    rounded_corners = [(2, corner_radius)]
                elif row_idx == n_rows - 1 and cell_idx == 0:
                    rounded_corners = [(3, corner_radius)]
            
            tmp_cell = RectCell(
                name=cell_id,
                height_x_width=(pitch, pitch),
                center=(pitch / 2, pitch / 2, 0.0),
                rounded_corners=rounded_corners
            )
            mat_name = C_to_mat[cell_id]
            
            if cell_id in Gd_cells:
                radii = computeSantamarinaradii(fuel_rad, gap_rad, clad_rad, gadolinium=True)
            elif "ROD" in cell_id and "W" not in cell_id:
                radii = computeSantamarinaradii(fuel_rad, gap_rad, clad_rad, gadolinium=False)
            else:  # Water rod placeholder
                radii = []
                mat_name = "MODERATOR"
            
            for radius in radii:
                tmp_cell.add_circle(radius)

            if mat_name == "MODERATOR":
                tmp_cell.set_properties({
                    PropertyType.MATERIAL: ["MODERATOR"],
                    PropertyType.MACRO: [f"MACRO{row_idx}{cell_idx}"]
                })
            else:
                if cell_id in Gd_cells:
                    list_of_cell_mats = [mat_name] * 6
                else:
                    list_of_cell_mats = [mat_name] * 4
                list_of_cell_mats.extend(["GAP", "CLAD", "COOLANT"])
                tmp_cell.set_properties({
                    PropertyType.MATERIAL: list_of_cell_mats,
                    PropertyType.MACRO: [f"MACRO{row_idx}{cell_idx}"] * len(list_of_cell_mats)
                })
            row_of_cells.append(tmp_cell)
        lattice_components.append(row_of_cells)
    return lattice_components


def create_water_rods(pin_pitch, water_rod_inner_radius, water_rod_outer_radius):
    """
    Create water rod cells for GE-14 assembly (2x2 pin pitch size)
    Cell center is at (2*pin_pitch, 2*pin_pitch) because the cell spans 2x2 pins
    """
    water_rod_cell1 = RectCell(
        name="WATER_ROD_1",
        height_x_width=(2 * pin_pitch, 2 * pin_pitch),
        center=(0.0, 0.0 , 0.0)
    )
    water_rod_cell1.add_circle(water_rod_inner_radius)
    water_rod_cell1.add_circle(water_rod_outer_radius)
    water_rod_cell1.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
        #PropertyType.MACRO: ["MACRO_WATER_ROD_1"] * 3
    })
    # Split the water rod into 4 different MACROS for IC method compatibility
    # 4 Rectangle faces
    face1 = Rectangle(
        name="WATER_ROD_1_Q1_FACE",
        height=pin_pitch,
        width=pin_pitch,
        center=(-pin_pitch / 2, -pin_pitch / 2, 0.0)
    )
    face2 = Rectangle(
        name="WATER_ROD_1_Q2_FACE",
        height=pin_pitch,
        width=pin_pitch,
        center=(pin_pitch / 2, -pin_pitch / 2, 0.0)
    )
    face3 = Rectangle(
        name="WATER_ROD_1_Q3_FACE",
        height=pin_pitch,
        width=pin_pitch,
        center=(-pin_pitch / 2, pin_pitch / 2, 0.0)
    )
    face4 = Rectangle(
        name="WATER_ROD_1_Q4_FACE",
        height=pin_pitch,
        width=pin_pitch,
        center=(pin_pitch / 2, pin_pitch / 2, 0.0)
    )
    water_rod_cell1_face = make_partition(
        [water_rod_cell1.face],
        [face1.face, face2.face, face3.face, face4.face],
        shape_type=ShapeType.COMPOUND
    )
    # Create macro for quadrant 1 (bottom-left)
    water_rod_1_macros = RectCell(
        name="WATER_ROD_1_MACROS",
        height_x_width=(pin_pitch*2, pin_pitch*2),
        center=(0.0, 0.0, 0.0)
    )
    water_rod_1_macros.update_geometry_from_face(GeometryType.TECHNOLOGICAL, water_rod_cell1_face)
    water_rod_1_macros.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "MODERATOR", "MODERATOR", "MODERATOR",
                                 "CLAD", "CLAD", "CLAD", "CLAD",
                                 "COOLANT", "COOLANT", "COOLANT", "COOLANT"],
        # 
        PropertyType.MACRO: ["WATER_ROD_1_MACRO_1", "WATER_ROD_1_MACRO_2", "WATER_ROD_1_MACRO_3", "WATER_ROD_1_MACRO_4", 
                             "WATER_ROD_1_MACRO_1", "WATER_ROD_1_MACRO_2", "WATER_ROD_1_MACRO_3", "WATER_ROD_1_MACRO_4", 
                             "WATER_ROD_1_MACRO_4", "WATER_ROD_1_MACRO_2", "WATER_ROD_1_MACRO_3", "WATER_ROD_1_MACRO_1"]
    })

    # Do the same for water rod cell 2
    water_rod_2_macros = RectCell(
        name="WATER_ROD_2",
        height_x_width=(2 * pin_pitch, 2 * pin_pitch),
        center=(0.0, 0.0, 0.0)
    )
    water_rod_2_macros.add_circle(water_rod_inner_radius)
    water_rod_2_macros.add_circle(water_rod_outer_radius)
    water_rod_2_macros.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
    })

    water_rod_2_macros_face = make_partition(
        [water_rod_2_macros.face],
        [face1.face, face2.face, face3.face, face4.face],
        shape_type=ShapeType.COMPOUND
    )
    water_rod_2_macros.update_geometry_from_face(GeometryType.TECHNOLOGICAL, water_rod_2_macros_face)
    water_rod_2_macros.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "MODERATOR", "MODERATOR", "MODERATOR",
                                 "CLAD", "CLAD", "CLAD", "CLAD",
                                 "COOLANT", "COOLANT", "COOLANT", "COOLANT"],
        #
        PropertyType.MACRO: ["WATER_ROD_2_MACRO_1", "WATER_ROD_2_MACRO_2", "WATER_ROD_2_MACRO_3", "WATER_ROD_2_MACRO_4", 
                             "WATER_ROD_2_MACRO_1", "WATER_ROD_2_MACRO_2", "WATER_ROD_2_MACRO_3", "WATER_ROD_2_MACRO_4", 
                             "WATER_ROD_2_MACRO_4", "WATER_ROD_2_MACRO_2", "WATER_ROD_2_MACRO_3", "WATER_ROD_2_MACRO_1"]
    })

    return water_rod_1_macros, water_rod_2_macros




def add_cells_to_regular_lattice(lattice, ordered_cells, cell_pitch, translation):
    """
    Add fuel cells to the lattice, skipping water rod placeholders
    """
    for row_idx in range(len(ordered_cells)):
        row_of_cells = ordered_cells[row_idx]
        for cell_idx in range(len(row_of_cells)):
            cell = row_of_cells[cell_idx]
            if "W" in cell.name:  # Skip water rod placeholders
                continue
            else:
                lattice.add_cell(
                    cell,
                    (
                        (cell_idx + 0.5) * cell_pitch + translation,
                        (row_idx + 0.5) * cell_pitch + translation,
                        0.0
                    )
                )
    return lattice

def make_grid_faces(parent: Rectangle, nx: int, ny: int):
    # parent width/height and lower-left corner
    lx = float(parent.lx) 
    ly = float(parent.ly)  
    dx = lx / nx
    dy = ly / ny
    cx_parent, cy_parent = float(parent.o.GetParameters().split(":")[0]), float(parent.o.GetParameters().split(":")[1])
    x0 = cx_parent - lx / 2.0
    y0 = cy_parent - ly / 2.0

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

            faces.append(face)

    return faces

def split_box_in_MACROs_for_IC(assembly_box_cell, pincell_pitch, assembly_pitch):
    """
    Make a partition of the box cell to define new MACROs properties to allow for IC method.
    
    Parameters :
    ------------ 
    assembly_box_cell : RectCell
        The assembly box cell to be split into MACROs.
    pincell_pitch : float
        The pitch of individual pin cells in the lattice.
    assembly_pitch : float
        The overall pitch of the assembly box.
    Returns:
    --------
    RectCell
        The updated assembly box cell with MACRO definitions for IC.
    """
    
    lattice_pitch = 10 * pincell_pitch
    x0 = (assembly_pitch - lattice_pitch) / 2
    y0 = (assembly_pitch - lattice_pitch) / 2
    x1 = x0 + lattice_pitch
    y1 = y0 + lattice_pitch
    
    # Create vertices for the partition
    points = [  (0.0, 0.0, 0.0), 
                (x0, 0.0, 0.0),
                (x1, 0.0, 0.0), 
                (assembly_pitch, 0.0, 0.0),
                (0.0, y0, 0.0),
                (x0, y0, 0.0),
                (x1, y0, 0.0),
                (assembly_pitch, y0, 0.0),
                (0.0, y1, 0.0),
                (x0, y1, 0.0),
                (x1, y1, 0.0),
                (assembly_pitch, y1, 0.0),
                (0.0, assembly_pitch, 0.0),
                (x0, assembly_pitch, 0.0),
                (x1, assembly_pitch, 0.0),
                (assembly_pitch, assembly_pitch, 0.0)
              ]
    # Create rectangles for the partition
    rectangles_to_split = [
        Rectangle(height=y0, width=x0, center=(x0/2, y0/2, 0.0)),  # Bottom-left
        Rectangle(height=y0, width=(x1 - x0), center=((x0 + x1)/2, y0/2, 0.0)), # Bottom-middle
        Rectangle(height=y0, width=(assembly_pitch - x1), center=((x1 + assembly_pitch)/2, y0/2, 0.0)), # Bottom-right
        Rectangle(height=(y1 - y0), width=x0, center=(x0/2, (y0 + y1)/2, 0.0)), # Middle-left
        #Rectangle(height=(y1 - y0), width=(x1 - x0), center=((x0 + x1)/2, (y0 + y1)/2, 0.0))  # Middle-middle
        Rectangle(height=(y1 - y0), width=(assembly_pitch - x1), center=((x1 + assembly_pitch)/2, (y0 + y1)/2, 0.0)),  # Middle-right
        Rectangle(height=(assembly_pitch - y1), width=x0, center=(x0/2, (y1 + assembly_pitch)/2, 0.0)),  # Top-left
        Rectangle(height=(assembly_pitch - y1), width=(x1 - x0), center=((x0 + x1)/2, (y1 + assembly_pitch)/2, 0.0)), # Top-middle        
        Rectangle(height=(assembly_pitch - y1), width=(assembly_pitch - x1), center=((x1 + assembly_pitch)/2, (y1 + assembly_pitch)/2, 0.0))  # Top-right
    ]
    
    nx_ny_splits = [
        (1,1),  # Bottom-left
        (10, 1),  # Bottom-middle
        (1, 1),   # Bottom-right
        (1, 10),  # Middle-left
        (1, 10),  # Middle-right
        (1, 1),   # Top-left
        (10, 1),  # Top-middle
        (1, 1)    # Top-right
    ]
    splitting_faces = []
    # Split rectangles and collect faces
    for react, (nx, ny) in zip(rectangles_to_split, nx_ny_splits):
        splitting_faces.extend(make_grid_faces(react, nx, ny))
    # Assemble all the geometric shapes together
    assembly_box_cell_face = make_partition(
        [assembly_box_cell.face],
        splitting_faces,
        shape_type=ShapeType.COMPOUND
    )
    # Update the box cell's technological geometry with the assembled one
    assembly_box_cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, assembly_box_cell_face)
    
    # Define MACRO names for each region
    list_of_macros = ["BASE_CELL", 
                    # COOLANT REGIONS IN DIFFERENT MACROS
                      "LEFTSIDE_5", "LEFTSIDE_6", 
                      "BOTSIDE_5", "BOTSIDE_6", 
                      "TOPSIDE_5", "RIGHTSIDE_5", 
                      "TOPSIDE_6", "RIGHTSIDE_6", 
                      "LEFTSIDE_4", "BOTSIDE_4", 
                      "LEFTSIDE_7", "BOTSIDE_7", 
                      "TOPSIDE_4", "RIGHTSIDE_4", 
                      "TOPSIDE_7", "RIGHTSIDE_7",
                    # CHANNEL BOX REGIONS IN DIFFERENT MACROS
                      "LEFTSIDE_6", "LEFTSIDE_5",
                      "TOPSIDE_5", "TOPSIDE_6",
                      "BOTSIDE_5", "BOTSIDE_6",
                      "RIGHTSIDE_6", "RIGHTSIDE_5",
                      "LEFTSIDE_4", "TOPSIDE_4",
                      "BOTSIDE_4", "RIGHTSIDE_4",
                      "LEFTSIDE_7", "TOPSIDE_7",
                      "BOTSIDE_7", "RIGHTSIDE_7",
                    # MODERATOR REGIONS IN DIFFERENT MACROS
                      "RIGHTSIDE_5", "TOPSIDE_5",
                      "RIGHTSIDE_6", "TOPSIDE_6",
                      "BOTSIDE_5", "LEFTSIDE_5",
                      "BOTSIDE_6", "LEFTSIDE_6", 
                      "RIGHTSIDE_4", "TOPSIDE_4",
                      "BOTSIDE_4", "LEFTSIDE_4",
                      "RIGHTSIDE_7", "TOPSIDE_7",
                      "BOTSIDE_7", "LEFTSIDE_7",
                    # COOLANT REGIONS IN DIFFERENT MACROS
                      "LEFTSIDE_3", "BOTSIDE_3",
                      "LEFTSIDE_8", "BOTSIDE_8",
                      "TOPSIDE_3", "RIGHTSIDE_3",
                      "TOPSIDE_8", "RIGHTSIDE_8",
                    # CHANNEL BOX REGIONS IN DIFFERENT MACROS
                      "TOPSIDE_3", "LEFTSIDE_3",
                      "BOTSIDE_3", "RIGHTSIDE_3",
                      "LEFTSIDE_8", "TOPSIDE_8",
                      "RIGHTSIDE_8", "BOTSIDE_8",
                    # MODERATOR REGION IN DIFFERENT MACROS
                      "RIGHTSIDE_3", "TOPSIDE_3",
                      "RIGHTSIDE_8", "BOTSIDE_3",
                      "LEFTSIDE_3", "BOTSIDE_8",
                      "TOPSIDE_8", "LEFTSIDE_8",
                    # COOLANT REGIONS IN DIFFERENT MACROS
                      "LEFTSIDE_2", "BOTSIDE_2",
                      "LEFTSIDE_9", "BOTSIDE_9",
                      "TOPSIDE_2", "RIGHTSIDE_2",
                      "TOPSIDE_9", "RIGHTSIDE_9",
                    # CHANNEL BOX REGIONS IN DIFFERENT MACROS
                      "TOPSIDE_2", "LEFTSIDE_2",
                      "BOTSIDE_2", "RIGHTSIDE_2",
                      "LEFTSIDE_9", "TOPSIDE_9",
                      "RIGHTSIDE_9", "BOTSIDE_9",
                    # MODERATOR REGION IN DIFFERENT MACROS
                      "RIGHTSIDE_2", "TOPSIDE_2",
                      "RIGHTSIDE_9", "BOTSIDE_2",
                      "LEFTSIDE_2", "BOTSIDE_9",
                      "TOPSIDE_9", "LEFTSIDE_9",
                    # COOLANT REGIONS IN DIFFERENT MACROS
                        "LEFTSIDE_1", "BOTSIDE_1",
                        "TOPSIDE_1", "RIGHTSIDE_1",
                        "LEFTSIDE_10", "BOTSIDE_10",
                        "TOPSIDE_10", "RIGHTSIDE_10",
                    # CHANNEL BOX REGIONS IN DIFFERENT MACROS
                        "TOPSIDE_1", "LEFTSIDE_1",
                        "BOTSIDE_1", "RIGHTSIDE_1",
                        "LEFTSIDE_10", "TOPSIDE_10",
                        "RIGHTSIDE_10", "BOTSIDE_10",
                    # MODERATOR REGION IN DIFFERENT MACROS
                        "BOTSIDE_1", "LEFTSIDE_1",
                        "RIGHTSIDE_1", "TOPSIDE_1",
                        "RIGHTSIDE_10", "BOTSIDE_10",
                        "LEFTSIDE_10", "TOPSIDE_10",
                    # ELEMENTS OF THE ROUNDED CORNER REGIONS : TO BE REGROUPED WITH CORNERING FUEL CELL MACROS
                        "MACRO90", "MACRO00", "MACRO99", "MACRO09",
                    # ELEMENTS OF THE ROUNDED CORNER REGIONS : TO BE REGROUPED WITH CORNERS OF LATTICE
                        "CORNER_TOP_RIGHT",
                        "CORNER_TOP_LEFT",
                        "CORNER_BOTTOM_LEFT",
                        "CORNER_BOTTOM_RIGHT",
                    # MODERATOR CORNERS
                        "CORNER_BOTTOM_RIGHT",
                        "CORNER_TOP_LEFT",
                        "CORNER_TOP_RIGHT",
                        "CORNER_BOTTOM_LEFT"
                      ]
    list_of_materials = ["COOLANT"] + ["COOLANT"] * 16 + ["CHANNEL_BOX"] * 16 + ["MODERATOR"] * 16 \
    + ["COOLANT"] * 8 + ["CHANNEL_BOX"] * 8 + ["MODERATOR"] * 8 \
    + ["COOLANT"] * 8 + ["CHANNEL_BOX"] * 8 + ["MODERATOR"] * 8 \
    + ["COOLANT"] * 8 + ["CHANNEL_BOX"] * 8 + ["MODERATOR"] * 8 \
    + ["CHANNEL_BOX"] * 8 + ["MODERATOR"] * 4



    # set properties for the new MACRO regions
    assembly_box_cell.set_properties({
        PropertyType.MATERIAL: list_of_materials,
        PropertyType.MACRO: list_of_macros
    })
    
    # return the updated assembly box cell
    return assembly_box_cell

### GLOW OUTPUT PARAMETERS 
tracking_type = "TISO"  # Options: "TISO" or "TSPC"


# --------------------
# GEOMETRY PARAMETERS
# --------------------
# Main geometrical dimensions
assembly_pitch = 15.24  # cm
pin_pitch = 1.3
gap_wide = 0.7549
channel_box_thickness = 0.1651
fuel_pellet_radius = 0.438
fuel_clad_inner_radius = 0.447
fuel_clad_outer_radius = 0.515
water_rod_inner_radius = 1.170
water_rod_outer_radius = 1.245

# Derived dimensions
channel_box_inner_side = assembly_pitch - 2 * channel_box_thickness - 2 * gap_wide
channel_box_outer_side = assembly_pitch - 2 * gap_wide
coolant_intra_assembly_width = (channel_box_inner_side - 10 * pin_pitch) / 2
corner_inner_radius_of_curvature = 0.9652
corner_outer_radius_of_curvature = corner_inner_radius_of_curvature + channel_box_thickness

# Inner corner radius for the pin lattice region (where fuel pins sit)
# This accounts for the rounded corners cutting into the coolant gap
#pin_lattice_corner_radius = corner_inner_radius_of_curvature - pin_pitch / 2
pin_lattice_corner_radius = corner_inner_radius_of_curvature - (coolant_intra_assembly_width + pin_pitch / 2)
if pin_lattice_corner_radius < 0:
    pin_lattice_corner_radius = 0  # No rounding needed if coolant gap is large enough

# Cap the corner radius at the maximum allowed for pin cells (half the pitch)
max_pin_corner_radius = pin_pitch / 2 - 0.0001  # Small margin for numerical stability
if pin_lattice_corner_radius > max_pin_corner_radius:
    print(f"WARNING: Pin lattice corner radius ({pin_lattice_corner_radius:.4f}) exceeds max allowed ({max_pin_corner_radius:.4f})")
    print(f"         Capping at maximum value. Corner fuel cells won't perfectly match channel box corners.")
    pin_lattice_corner_radius = max_pin_corner_radius

print(f"=== Geometry dimensions ===")
print(f"Channel box inner side: {channel_box_inner_side:.4f} cm")
print(f"Channel box outer side: {channel_box_outer_side:.4f} cm")
print(f"Coolant gap width: {coolant_intra_assembly_width:.4f} cm")
print(f"Corner inner radius (channel box): {corner_inner_radius_of_curvature:.4f} cm")
print(f"Corner outer radius (channel box): {corner_outer_radius_of_curvature:.4f} cm")
print(f"Pin lattice corner radius: {pin_lattice_corner_radius:.4f} cm")
print(f"Pin lattice side: {10 * pin_pitch:.4f} cm")

# Translation offset for pin cells (from assembly origin to first pin center)
pincell_translation = gap_wide + channel_box_thickness + coolant_intra_assembly_width

center = (assembly_pitch / 2, assembly_pitch / 2, 0.0)

# --------------------
# LATTICE DESCRIPTION (10x10 GE-14)
# --------------------
lattice_description = [
    ["ROD2", "ROD5", "ROD7", "ROD7", "ROD7", "ROD7", "ROD7", "ROD7", "ROD7", "ROD3"],
    ["ROD5", "ROD5", "ROD6H", "ROD7", "ROD7", "ROD7G", "ROD7", "ROD7G", "ROD7", "ROD7"],
    ["ROD5", "ROD6H", "ROD6", "ROD7", "ROD7", "ROD7", "ROD7G", "ROD7", "ROD7G", "ROD7"],
    ["ROD5", "ROD5", "ROD6H", "WROD", "WROD", "ROD7", "ROD7", "ROD7G", "ROD7", "ROD7"],
    ["ROD5", "ROD5G", "ROD6", "WROD", "WROD", "ROD7", "ROD7", "ROD7", "ROD7G", "ROD7"],
    ["ROD5", "ROD4", "ROD7H", "ROD5", "ROD7", "WROD", "WROD", "ROD7", "ROD7", "ROD7"],
    ["ROD5", "ROD5", "ROD6", "ROD7G", "ROD5", "WROD", "WROD", "ROD7", "ROD7", "ROD7"],
    ["ROD3", "ROD3", "ROD6K", "ROD6", "ROD7H", "ROD6", "ROD6H", "ROD6", "ROD6H", "ROD7"],
    ["ROD2", "ROD2", "ROD3", "ROD5", "ROD4", "ROD5G", "ROD5", "ROD6H", "ROD5", "ROD5"],
    ["ROD1", "ROD2", "ROD3", "ROD5", "ROD5", "ROD5", "ROD5", "ROD5", "ROD5", "ROD2"],
]

ROD_to_material = {
    "ROD1": "UOX160",
    "ROD2": "UOX280",
    "ROD3": "UOX320",
    "ROD4": "UOX360",
    "ROD5": "UOX395",
    "ROD5G": "UOX395_Gd8",
    "ROD6": "UOX440",
    "ROD6H": "UOX440_Gd6",
    "ROD6K": "UOX440_Gd3",
    "ROD7": "UOX490",
    "ROD7G": "UOX490_Gd8",
    "ROD7H": "UOX490_Gd6",
    "RODN": "UOXNAT",
    "WROD": "MODERATOR"
}

# --------------------
# GENERATE FUEL CELLS
# --------------------
ordered_fuel_cells = generate_cells(
    lattice_desc=lattice_description,
    pitch=pin_pitch,
    C_to_mat=ROD_to_material,
    fuel_rad=fuel_pellet_radius,
    gap_rad=fuel_clad_inner_radius,
    clad_rad=fuel_clad_outer_radius,
    corner_radius=pin_lattice_corner_radius  # Rounded corners for corner fuel cells
)

# Create water rod cells
water_rod_cell1, water_rod_cell2 = create_water_rods(
    pin_pitch, water_rod_inner_radius, water_rod_outer_radius
)

# --------------------
# CREATE ASSEMBLY BOX CELLS (with rounded corners)
# --------------------
# Inner coolant cell (the moderator gap between pins and channel box)
coolant_intra_assembly_cell = Rectangle(
    name="intra_assembly_coolant",
    height=channel_box_inner_side,
    width=channel_box_inner_side,
    center=center,
    rounded_corners=[
        (0, corner_inner_radius_of_curvature),
        (1, corner_inner_radius_of_curvature),
        (2, corner_inner_radius_of_curvature),
        (3, corner_inner_radius_of_curvature)
    ]
)

# Channel box cell
channel_box_cell = Rectangle(
    name="channel_box",
    height=channel_box_outer_side,
    width=channel_box_outer_side,
    center=center,
    rounded_corners=[
        (0, corner_outer_radius_of_curvature),
        (1, corner_outer_radius_of_curvature),
        (2, corner_outer_radius_of_curvature),
        (3, corner_outer_radius_of_curvature)
    ]
)

# Outer moderator cell (inter-assembly gap)
assembly_box_cell = RectCell(
    name="out_of_assembly_moderator",
    height_x_width=(assembly_pitch, assembly_pitch),
    center=center
)

assembly_box_cell_face = make_partition(
    [assembly_box_cell.face],
    [channel_box_cell.face, coolant_intra_assembly_cell.face],
    shape_type=ShapeType.COMPOUND
)

assembly_box_cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, assembly_box_cell_face)

assembly_box_cell.set_properties({
    PropertyType.MATERIAL: ["COOLANT", "CHANNEL_BOX", "MODERATOR"],
})

# --------------------
# LATTICE CONSTRUCTION
# --------------------
lattice = Lattice(name='GE14_full_assembly - MACROs', center=center)

# Add the box cell FIRST - this establishes the base/background for the lattice
# Using () as position means it's the base cell

# Add all fuel pin cells to the lattice
lattice = add_cells_to_regular_lattice(
    lattice=lattice,
    ordered_cells=ordered_fuel_cells,
    cell_pitch=pin_pitch,
    translation=pincell_translation
)

# Add water rod cells at their specific locations
# -> center at (4*pitch, 4*pitch) + translation

lattice.add_cell(
        water_rod_cell1,
        (4 * pin_pitch + pincell_translation, 4 * pin_pitch + pincell_translation, 0.0)
    )
# center at (6*pitch, 6*pitch) + translation
lattice.add_cell(
    water_rod_cell2,
    (6 * pin_pitch + pincell_translation, 6 * pin_pitch + pincell_translation, 0.0)
)

## Discretize box for MOC
assembly_box_cell = split_box_in_MACROs_for_IC(assembly_box_cell, pin_pitch, assembly_pitch)

lattice.lattice_box = assembly_box_cell

# Show the lattice
lattice.show(geometry_type_to_show=GeometryType.SECTORIZED, property_type_to_show=PropertyType.MACRO)

# --------------------  
# GENERATE TDT FILE
# --------------------
if tracking_type == "TISO":
    output_file_name = "GE-14_assembly_IC_MACRO_TISO"
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
        [lattice], 
        f"data/glow_data/tdt_data/{output_file_name}", 
        TdtSetup(GeometryType.SECTORIZED, 
                property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                type_geo=LatticeGeometryType.ISOTROPIC,
                symmetry_type=BoundaryType.AXIAL_SYMMETRY))
elif tracking_type == "TSPC":
    raise NotImplementedError("TSPC tracking type is not supported for IC MACRO geometry.")