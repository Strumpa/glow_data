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


def generate_cells(lattice_desc, pitch, C_to_mat, fuel_rad, gap_rad, clad_rad, corner_radius=0, windmill=False):
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
                    if windmill:
                        tmp_cell.sectorize([1]*8 + [8], [0]*8 + [22.5], windmill=True)
                else:
                    list_of_cell_mats = [mat_name] * 4
                    if windmill:
                        tmp_cell.sectorize([1]*6 + [8], [0]*6 + [22.5], windmill=True)
                list_of_cell_mats.extend(["GAP", "CLAD", "COOLANT"])
                tmp_cell.set_properties({
                    PropertyType.MATERIAL: list_of_cell_mats,
                    PropertyType.MACRO: [f"MACRO{row_idx}{cell_idx}"] * len(list_of_cell_mats)
                })
            row_of_cells.append(tmp_cell)
        lattice_components.append(row_of_cells)
    return lattice_components


def create_water_rods(pin_pitch, water_rod_inner_radius, water_rod_outer_radius, windmill=False):
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
        PropertyType.MACRO: ["MACRO_WATER_ROD_1"] * 3
    })
    
    # Do the same for water rod cell 2
    water_rod_cell2 = RectCell(
        name="WATER_ROD_2",
        height_x_width=(2 * pin_pitch, 2 * pin_pitch),
        center=(0.0, 0.0, 0.0)
    )
    water_rod_cell2.add_circle(water_rod_inner_radius)
    water_rod_cell2.add_circle(water_rod_outer_radius)
    water_rod_cell2.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
        PropertyType.MACRO: ["MACRO_WATER_ROD_2"] * 3
    })
    
    if windmill:
        water_rod_cell1.sectorize([1, 1, 8], [0, 0, 0], windmill=True)
        water_rod_cell2.sectorize([1, 1, 8], [0, 0, 0], windmill=True)
        
    return water_rod_cell1, water_rod_cell2




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

def split_box_in_MACROs_for_IC(assembly_box_cell, pincell_pitch, assembly_pitch, control_cross_thickness, control_cross_half_span):
    """
    Make a partition of the box cell to allow for sub-meshing for MOC calculations.
    
    Parameters :
    ------------ 
    assembly_box_cell : RectCell
        The assembly box cell to be discretized for MOC. 
    pincell_pitch : float
        The pitch of individual pin cells in the lattice.
    assembly_pitch : float
        The overall pitch of the assembly box.
    control_cross_thickness : float
        The thickness of the control cross arms.
    control_cross_half_span : float
        The half-span of the control cross arms.
    Returns:
    --------
    RectCell
        The updated assembly box cell with discretized geometry for MOC.
    """
    
    lattice_pitch = 10 * pincell_pitch
    x0 = control_cross_thickness / 2
    y_blade = assembly_pitch - control_cross_half_span
    x1 = (assembly_pitch - lattice_pitch) / 2
    y1 = (assembly_pitch - lattice_pitch) / 2
    x2 = assembly_pitch - x1
    xend = x0 + lattice_pitch
    yend = y1 + lattice_pitch
    # Create vertices for the partition

    # Create rectangles for the partition in x-increasing / y-increasing order
    rectangles_to_split = [
        Rectangle(height=y1, width=x1 , center=(x1/2, y1/2, 0.0)), # Bottom-left corner : moderator + box
        Rectangle(height=y_blade-y1, width=x0, center=(x0/2, (y_blade-y1)/2+y1, 0.0)),  # Bottom-left : moderator under west arm of control cross
        Rectangle(height=y1, width=(x2 - x1), center=((x1 + x2)/2, y1/2, 0.0)), # center bottom : moderator + box + coolant gap
        
        Rectangle(height=y1, width=(assembly_pitch - x2), center=((x2 + assembly_pitch)/2, y1/2, 0.0)), # Bottom-right
        # Rectangle overlapping with the control cross arm
        Rectangle(height=(assembly_pitch - y_blade), width=x0, center=(x0/2, (assembly_pitch - y_blade)/2 + y_blade, 0.0)),  # left : overlapping with control cross arm
        Rectangle(height=lattice_pitch, width=(x1 - x0), center=((x0 + x1)/2, lattice_pitch/2 + y1 , 0.0)),  # middle
        #Rectangle(height=(lattice_pitch), width=(lattice_pitch), center=(assembly_pitch/2, assembly_pitch/2, 0.0))  # Middle-middle
        Rectangle(height=(lattice_pitch), width=(assembly_pitch - x2), center=((x2 + assembly_pitch)/2, (assembly_pitch)/2, 0.0)),  # Middle-right
        
        Rectangle(height=(x1 - x0), width=(x1 - x0), center=((x0 + x1)/2, (assembly_pitch-control_cross_thickness/2 - (x1 - x0)/2), 0.0)),  # Top-left moderator corner
        Rectangle(height=(x1 - x0), width=(lattice_pitch), center=((x1 + x2)/2, (assembly_pitch-control_cross_thickness/2 - (x1 - x0)/2), 0.0)), # Top-middle : moderator + box + coolant gap

        # Rectangle overlapping with the control cross north arm
        Rectangle(height=(control_cross_thickness/2), width=control_cross_half_span, center=(control_cross_half_span/2, (assembly_pitch - control_cross_thickness/4), 0.0)),  # top : overlapping with control cross north arm
        
        Rectangle(height=(control_cross_thickness/2), width=assembly_pitch-control_cross_half_span-x1, 
                  center=(((assembly_pitch-control_cross_half_span-x1)/2 + control_cross_half_span, 
                           (assembly_pitch - control_cross_thickness/4), 
                           0.0))),  # top-right moderator region right of north arm
        Rectangle(height=x1, width=y1, center=((x2 + assembly_pitch)/2, (assembly_pitch - x1/2), 0.0)),  # Top-right : moderator + box
    ]
    
    
    nx_ny_splits = [
        (1,1),  # Bottom-left corner: moderator + box
        (1,1),  # Bottom-left : under the cross arm
        (2,1),   # Bottom-center : center bottom
        (1,1),   # Bottom-right corner
        (1,1),   # Rectangle overlapping with the control cross arm
        (1,2),    # Middle-left : moderator + box + coolant gap
        #(1,1),  # Middle-middle : covering the pin lattice region
        (1,2),  # Middle-right
        (1,1),   # Top-left moderator corner under cross
        (2,1),  # Top-middle : moderator + box + coolant gap
        (1,1),    # Rectangle overlapping with the control cross north arm
        (1,1),    # top-right moderator region right of north arm
        (1,1),   # Top-right corner : moderator + box
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
    """
    list_of_macros = ["BASE_CELL"] + ["MACRO_LEFT_SIDE", "MACRO_BOT_SIDE", "MACRO_TOP_SIDE", "MACRO_RIGHT_SIDE"]  \
        + ["MACRO_LEFT_SIDE", "MACRO_TOP_SIDE", "MACRO_BOT_SIDE", "MACRO_RIGHT_SIDE"] \
        + ["MACRO_TOP_SIDE", "MACRO_RIGHT_SIDE", "MACRO_LEFT_SIDE", "MACRO_BOT_SIDE"] \
        + ["MACRO_NORTH_CROSS"] + ["MACRO_WEST_CROSS"]*2 + ["MACRO_NORTH_CROSS"]*2 + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS"] + ["MACRO_WEST_CROSS"]*2 \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS"] \
        + ["MACRO_NORTH_CROSS"] + ["MACRO_WEST_CROSS"]*2 + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS", "MACRO_NORTH_CROSS"] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS","MACRO_WEST_CROSS"] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS"] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS",] \
        + ["MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS",] \
        + ["UNDER_WEST_CROSS", "RIGHT_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["MACRO90", "MACRO00", "MACRO99", "MACRO09",] \
        + ["MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS", "MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["NORTH_EAST_CORNER", "NORTH_WEST_CORNER", "SOUTH_WEST_CORNER",  "SOUTH_EAST_CORNER", "NORTH_WEST_CORNER", "SOUTH_EAST_CORNER", "NORTH_EAST_CORNER",] \
        + ["SOUTH_WEST_CORNER", "MACRO_WEST_CROSS"]
            
    """
    list_of_materials = ["COOLANT", "COOLANT", "COOLANT", "COOLANT", "COOLANT", "COOLANT", "COOLANT", "COOLANT", "COOLANT",] \
        + ["CHANNEL_BOX", "CHANNEL_BOX", "CHANNEL_BOX", "CHANNEL_BOX"]*2 \
        + ["MODERATOR"]*8 + [sheath_material]*2 + ["MODERATOR"]*6 + [sheath_material]*6 + ["MODERATOR"]*4 + [sheath_material]*2 + [absorber_material]*2 + [sheath_material]*2 \
        + [absorber_material]*4 + ["MODERATOR"]*4 + [absorber_material]*4 + [sheath_material]*4 + ["MODERATOR"]*4 + [absorber_material]*4 + [sheath_material]*4 + ["MODERATOR"]*2 \
        + [absorber_material]*2 + ["MODERATOR"]*2 + [absorber_material]*2 + [sheath_material]*4 + [absorber_material]*4 + ["MODERATOR"]*4 + [sheath_material]*4 + [absorber_material]*4 \
        + ["MODERATOR"]*4 + [sheath_material]*4 + [absorber_material]*4 + ["MODERATOR"]*4 + [sheath_material]*4 + [absorber_material]*4 + ["MODERATOR"]*6 + [sheath_material]*6 + [absorber_material]*4 \
        + ["MODERATOR"]*4 + [sheath_material]*2 + [absorber_material]*2 + ["MODERATOR"]*2 + ["CHANNEL_BOX"]*4 + [sheath_material]*2 + [absorber_material]*2 + [sheath_material]*2 + ["CHANNEL_BOX"]*4 \
        + ["MODERATOR"]*4 + [sheath_material]   
    
    list_of_macros = ["BASE_CELL"] + ["MACRO_LEFT_SIDE0", "MACRO_LEFT_SIDE1", "MACRO_BOT_SIDE0", "MACRO_BOT_SIDE1", "MACRO_TOP_SIDE0", "MACRO_RIGHT_SIDE0", "MACRO_TOP_SIDE1", "MACRO_RIGHT_SIDE1"]  \
        + ["MACRO_LEFT_SIDE1", "MACRO_LEFT_SIDE0","MACRO_TOP_SIDE0","MACRO_BOT_SIDE0","MACRO_TOP_SIDE1","MACRO_BOT_SIDE1","MACRO_RIGHT_SIDE1","MACRO_RIGHT_SIDE0"] \
        + ["MACRO_TOP_SIDE0","MACRO_RIGHT_SIDE0","MACRO_RIGHT_SIDE1","MACRO_TOP_SIDE1","MACRO_LEFT_SIDE0","MACRO_LEFT_SIDE1","MACRO_BOT_SIDE0","MACRO_BOT_SIDE1"] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS", "MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS", "MACRO_WEST_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS",]  \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS",] \
        + ["MACRO_NORTH_CROSS","MACRO_WEST_CROSS","UNDER_WEST_CROSS","RIGHT_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO_NORTH_CROSS","MACRO_WEST_CROSS","MACRO_WEST_CROSS","MACRO_NORTH_CROSS",] \
        + ["MACRO_WEST_CROSS","MACRO_NORTH_CROSS","MACRO90", "MACRO00", "MACRO99", "MACRO09","MACRO_WEST_CROSS", "MACRO_NORTH_CROSS","MACRO_WEST_CROSS", "MACRO_NORTH_CROSS","MACRO_WEST_CROSS", "MACRO_NORTH_CROSS",] \
        + ["NORTH_EAST_CORNER", "NORTH_WEST_CORNER", "SOUTH_WEST_CORNER",  "SOUTH_EAST_CORNER", "NORTH_WEST_CORNER", "SOUTH_EAST_CORNER", "NORTH_EAST_CORNER",] \
        + ["SOUTH_WEST_CORNER", "MACRO_WEST_CROSS"]                


    # set properties for the new MACRO regions
    assembly_box_cell.set_properties({
        PropertyType.MATERIAL: list_of_materials + ["mat"] * (174 - len(list_of_materials)),
        PropertyType.MACRO: list_of_macros + ["macro1"] * (174 - len(list_of_macros))
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

# control cross dimensions
blade_half_span = 12.3825
blade_thickness = 0.79248
number_tubes_per_wing = 21
tip_radius = 0.39624
central_structure_half_span = 1.98501
sheath_thickness = 0.14224

# absorber tube dimensions
absorber_tube_outer_radius = 0.23876
absorber_tube_inner_radius = 0.17526

absorber_material = "B4C"
sheath_material = "SS304"


## --------------------------
# COMPUTE DERIVED DIMENSIONS
# ---------------------------

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
    corner_radius=pin_lattice_corner_radius,  # Rounded corners for corner fuel cells
    windmill=False
)

# Create water rod cells
water_rod_cell1, water_rod_cell2 = create_water_rods(
    pin_pitch, water_rod_inner_radius, water_rod_outer_radius, windmill=False
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


ctrl_cross_sheath_cells = []
# control cross center at top left corner of assembly
# due to symmetry, we only model 1/4 of the control cross
# Center 
control_cross_center_cell = Rectangle(
    name="CONTROL_CROSS_CENTER_QUARTER",
    height=blade_thickness/2,
    width=blade_thickness/2,
    center=(blade_thickness/4,
            assembly_pitch - blade_thickness/4, 
            0.0),
)
ctrl_cross_sheath_cells.append(control_cross_center_cell)

# control cross right central structure 
control_cross_right_central_structure_cell = Rectangle(
    name="CONTROL_CROSS_RIGHT_CENTRAL_STRUCTURE_HALF",
    height=blade_thickness/2,
    width=central_structure_half_span-blade_thickness/2,
    center=((central_structure_half_span-blade_thickness/2)/2 + blade_thickness/2,
            assembly_pitch - blade_thickness/4, 
            0.0),
)
ctrl_cross_sheath_cells.append(control_cross_right_central_structure_cell)
# bottom central structure
control_cross_bottom_central_structure_cell = Rectangle(
    name="CONTROL_CROSS_BOTTOM_CENTRAL_STRUCTURE_HALF",
    height=central_structure_half_span - blade_thickness/2,
    width=blade_thickness/2,
    center=(blade_thickness/4,
            assembly_pitch - (central_structure_half_span - blade_thickness/2)/2 - blade_thickness/2, 
            0.0),
)
ctrl_cross_sheath_cells.append(control_cross_bottom_central_structure_cell)

# control cross right wing
control_cross_right_wing_cell = Rectangle(
    name="CONTROL_CROSS_RIGHT_WING_HALF",
    height=blade_thickness,
    width=blade_half_span - central_structure_half_span,
    center=((blade_half_span - central_structure_half_span)/2 + central_structure_half_span,
            assembly_pitch, 
            0.0),
    rounded_corners=[(1, tip_radius)])
ctrl_cross_sheath_cells.append(control_cross_right_wing_cell)

# control cross bottom wing
control_cross_bottom_wing_cell = Rectangle(
    name="CONTROL_CROSS_BOTTOM_WING_HALF",
    height=blade_half_span - central_structure_half_span,
    width=blade_thickness,
    center=(0.0,
            assembly_pitch - (blade_half_span - central_structure_half_span)/2 - central_structure_half_span, 
            0.0),
    rounded_corners=[(1, tip_radius)])
ctrl_cross_sheath_cells.append(control_cross_bottom_wing_cell)

# subdivide control cross sheath cells to add absorber tubes : first create another rectangle to partition each "WING" sheath cell
inner_sheath_width = blade_thickness - 2 * sheath_thickness
inner_right_wing_cell = Rectangle(
    name="CONTROL_CROSS_RIGHT_WING_INNER",
    height=inner_sheath_width,
    width=blade_half_span - central_structure_half_span - sheath_thickness,
    center=((blade_half_span - central_structure_half_span - sheath_thickness)/2 + central_structure_half_span,
            assembly_pitch, 
            0.0),
    rounded_corners=[(1, tip_radius-sheath_thickness)])
ctrl_cross_sheath_cells.append(inner_right_wing_cell)

inner_bottom_wing_cell = Rectangle(
    name="CONTROL_CROSS_BOTTOM_WING_INNER",
    height=blade_half_span - central_structure_half_span - sheath_thickness,
    width=inner_sheath_width,
    center=(0.0,
            assembly_pitch - (blade_half_span - central_structure_half_span - sheath_thickness)/2 - central_structure_half_span, 
            0.0),
    rounded_corners=[(1, tip_radius-sheath_thickness)])
ctrl_cross_sheath_cells.append(inner_bottom_wing_cell)


# first control cylinder tube offset from center
moderator_width = blade_thickness - 2 * sheath_thickness
delta_tube = 0.4883456  # spacing between tubes centers
print("=== Absorber Tubes Placement ===")

#delta_tube += missing / number_tubes_per_wing  # adjust to fit exactly
b4c_tubes = []
for i in range(number_tubes_per_wing):
    offset_x = 2.229183 + i * delta_tube
    tube_x_tmp = RectCell(
        name="CONTROL_CROSS_TUBE_X",
        height_x_width=(moderator_width, delta_tube),
        center=(offset_x, assembly_pitch - 0.0, 0.0)
    )
    tube_x_tmp.add_circle(absorber_tube_inner_radius)
    tube_x_tmp.add_circle(absorber_tube_outer_radius)
    
    offset_y = offset_x
    tube_y_tmp = RectCell(
        name="CONTROL_CROSS_TUBE_Y",
        height_x_width=(delta_tube, moderator_width),
        center=(0.0, assembly_pitch - offset_y, 0.0)
    )
    tube_y_tmp.add_circle(absorber_tube_inner_radius)
    tube_y_tmp.add_circle(absorber_tube_outer_radius)

    b4c_tubes.append(tube_x_tmp)
    b4c_tubes.append(tube_y_tmp)

assembly_box_cell_face = make_partition(
    [assembly_box_cell.face],
    [channel_box_cell.face, coolant_intra_assembly_cell.face] + [tube.face for tube in b4c_tubes] + [structure.face for structure in ctrl_cross_sheath_cells],
    shape_type=ShapeType.COMPOUND
)

assembly_box_cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, assembly_box_cell_face)

list_of_materials =  ["COOLANT", "CHANNEL_BOX", "MODERATOR"] + [sheath_material]*2 + ["MODERATOR"]*6 + [sheath_material]*6 \
    + ["MODERATOR"]*4 + [sheath_material]*2 + [absorber_material]*2 + [sheath_material]* 2 + [absorber_material]*4 \
    + ["MODERATOR"]*4 + [absorber_material]*4 + [sheath_material]*4 + ["MODERATOR"]*4 + [absorber_material]*4 + [sheath_material]*4 \
    + ["MODERATOR"]*2 + [absorber_material]*2 + ["MODERATOR"]*2 + [absorber_material]*2 + [sheath_material]*4 + [absorber_material]*4 \
    + ["MODERATOR"]*4 + [sheath_material]*4 + [absorber_material]*4 + ["MODERATOR"]*4 + [sheath_material]*4 + [absorber_material]*4 \
    + ["MODERATOR"]*4 + [sheath_material]*4 + [absorber_material]*4 + ["MODERATOR"]*4 + [sheath_material]*6 + [absorber_material]*4 \
    + ["MODERATOR"]*2 + [sheath_material]*2 + [absorber_material]*2 + ["MODERATOR"]*2 + [sheath_material]*2 + [absorber_material]*2 \
    + [sheath_material]*3       
print(list_of_materials)
assembly_box_cell.set_properties({
    PropertyType.MATERIAL: list_of_materials
})

# --------------------
# LATTICE CONSTRUCTION
# --------------------
lattice = Lattice(name='GE14_ctrl_assembly', center=center)

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

## split the box into MACROs for IC
assembly_box_cell = split_box_in_MACROs_for_IC(assembly_box_cell, pin_pitch, assembly_pitch, blade_thickness, blade_half_span)

lattice.lattice_box = assembly_box_cell
# Show the lattice
lattice.show(geometry_type_to_show=GeometryType.SECTORIZED, property_type_to_show=PropertyType.MACRO)
#lattice.show(geometry_type_to_show=GeometryType.SECTORIZED, property_type_to_show=PropertyType.MATERIAL)

# --------------------  
# GENERATE TDT FILE
# --------------------
if tracking_type == "TISO":
    output_file_name = "GE-14_assembly_ctrl_IC_MACRO_TISO"
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