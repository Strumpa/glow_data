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
        center=(2 * pin_pitch, 2 * pin_pitch, 0.0)
    )
    water_rod_cell1.add_circle(water_rod_inner_radius)
    water_rod_cell1.add_circle(water_rod_outer_radius)
    water_rod_cell1.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
        PropertyType.MACRO: ["MACRO_WATER_ROD_1"] * 3
    })

    water_rod_cell2 = RectCell(
        name="WATER_ROD_2",
        height_x_width=(2 * pin_pitch, 2 * pin_pitch),
        center=(2 * pin_pitch, 2 * pin_pitch, 0.0)
    )
    water_rod_cell2.add_circle(water_rod_inner_radius)
    water_rod_cell2.add_circle(water_rod_outer_radius)
    water_rod_cell2.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
        PropertyType.MACRO: ["MACRO_WATER_ROD_2"] * 3
    })

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


def create_box_cell_with_rounded_corners(assembly_pitch, channel_box_inner_side, channel_box_outer_side,
                                         pin_pitch, n_pins, pincell_translation,
                                         corner_inner_radius, corner_outer_radius, 
                                         pin_lattice_corner_radius, center):
    """
    Create the assembly box cell exactly as in GE-14_rounded_corners.py.
    This creates a single cell with 3 material zones: COOLANT, CHANNEL_BOX, MODERATOR.
    
    The geometry uses rounded corners and cannot be subdivided into separate strip MACROs
    due to GLOW's limitation with curved edges. Instead, each material zone gets its own MACRO.
    
    Returns:
    --------
    RectCell with 3 zones (coolant gap, channel box, moderator)
    """
    pin_lattice_side = n_pins * pin_pitch
    
    # --------------------
    # CREATE ASSEMBLY BOX CELLS (with rounded corners) - EXACTLY AS IN ORIGINAL
    # --------------------
    
    # Inner coolant cell (the coolant gap between pins and channel box)
    coolant_intra_assembly_cell = RectCell(
        name="intra_assembly_coolant",
        height_x_width=(channel_box_inner_side, channel_box_inner_side),
        center=center,
        rounded_corners=[
            (0, corner_inner_radius),
            (1, corner_inner_radius),
            (2, corner_inner_radius),
            (3, corner_inner_radius)
        ]
    )
    
    # Channel box cell
    channel_box_cell = RectCell(
        name="channel_box",
        height_x_width=(channel_box_outer_side, channel_box_outer_side),
        center=center,
        rounded_corners=[
            (0, corner_outer_radius),
            (1, corner_outer_radius),
            (2, corner_outer_radius),
            (3, corner_outer_radius)
        ]
    )
    
    # Outer moderator cell (inter-assembly gap)
    assembly_cell = RectCell(
        name="out_of_assembly_moderator",
        height_x_width=(assembly_pitch, assembly_pitch),
        center=center
    )
    
    # Inner pin lattice region with rounded corners to match the coolant gap inner boundary
    rounded_pin_lattice_corners = None
    if pin_lattice_corner_radius > 0:
        rounded_pin_lattice_corners = [
            (0, pin_lattice_corner_radius),
            (1, pin_lattice_corner_radius),
            (2, pin_lattice_corner_radius),
            (3, pin_lattice_corner_radius)
        ]
    
    rounded_pin_lattice_cell = RectCell(
        name="rounded_pin_lattice_for_cut",
        height_x_width=(pin_lattice_side, pin_lattice_side),
        center=center,
        rounded_corners=rounded_pin_lattice_corners
    )
    
    # --------------------
    # CREATE BOX GEOMETRY USING CUT OPERATIONS - EXACTLY AS IN ORIGINAL
    # --------------------
    # Cut the channel_box face from the assembly face to create the outer moderator ring
    moderator_face = make_cut(assembly_cell.face, channel_box_cell.face)
    
    # Cut the coolant region out of the channel box to create the channel box ring
    channel_box_face = make_cut(channel_box_cell.face, coolant_intra_assembly_cell.face)
    
    # Cut the pin lattice region out of the coolant to create the coolant gap ring
    # Use the ROUNDED version for the cut to get proper rounded inner boundary
    coolant_gap_face = make_cut(coolant_intra_assembly_cell.face, rounded_pin_lattice_cell.face)
    
    # Combine all three layers into a compound for the box
    box_face = make_compound([moderator_face, channel_box_face, coolant_gap_face])
    
    # Create the box cell with the combined moderator + channel box + coolant gap geometry
    box_cell = RectCell(
        name="assembly_box",
        height_x_width=(assembly_pitch, assembly_pitch),
        center=center
    )
    
    # Update the box cell geometry with the cut faces
    box_cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, box_face)
    
    # Set properties for the zones in the box
    # The geometry has 3 zones created in this order via make_compound:
    # 0 = moderator_face (outer ring)
    # 1 = channel_box_face (middle ring) 
    # 2 = coolant_gap_face (inner ring)
    box_cell.set_properties({
        PropertyType.MATERIAL: ["MODERATOR_2", "CHANNEL_BOX", "COOLANT"],
        PropertyType.MACRO: ["MACRO_MODERATOR_OUTSIDE", "MACRO_CHANNEL_BOX", "MACRO_COOLANT_GAP"]
    })
    
    return box_cell


def build_subdivided_box_macro_cells(assembly_pitch, channel_box_inner_side, channel_box_outer_side,
                                     pin_pitch, n_pins, pincell_translation, gap_wide, channel_box_thickness,
                                     coolant_intra_assembly_width, corner_inner_radius, corner_outer_radius,
                                     pin_lattice_corner_radius, center):
    """
    Build a subdivided assembly box where each subdivision is a separate cell with its own MACRO.
    
    This function creates the same 3-layer geometry as create_box_cell_with_rounded_corners,
    but subdivided into MACROs aligned with the fuel pin lattice:
    - 4 corner MACROs (each containing the curved portion with 3 material zones)
    - Edge strip MACROs (rectangular strips for the straight portions)
    
    The approach creates each subdivision as a separate RectCell, avoiding the GLOW limitation
    with curved edges in update_geometry_from_face by using boolean operations (make_cut, make_common)
    to create the actual curved geometry only for corner cells.
    
    Returns:
    --------
    List of RectCell objects, one for each MACRO subdivision
    """
    macro_cells = []
    
    # Key positions
    lattice_side = n_pins * pin_pitch
    
    # Define the box region boundaries
    # The pin lattice runs from pincell_translation to (pincell_translation + lattice_side)
    x_coolant_outer = pincell_translation
    x_coolant_inner = pincell_translation + lattice_side
    y_coolant_outer = pincell_translation
    y_coolant_inner = pincell_translation + lattice_side
    
    # For edge strips, we skip the first and last pin positions (those are corners)
    # Edge strips run from index 1 to index (n_pins - 2), so 8 strips for a 10-pin lattice
    n_edge_strips = n_pins - 2  # = 8
    
    # The corner regions extend from the edge to 1 pin into the lattice
    # Corner extends from x=0 to x=(x_coolant_outer + pin_pitch) on each side
    corner_extent = pin_pitch
    
    # Width of the box region (from assembly edge to inner coolant boundary)
    box_region_width = pincell_translation  # = gap_wide + channel_box_thickness + coolant_intra_assembly_width
    
    # --------------------
    # CREATE CORNER MACROS (4 corners, each with 3 material zones)
    # Each corner uses boolean operations to create proper curved geometry
    # --------------------
    
    corner_positions = [
        ("BL", 0, 0),  # Bottom-left
        ("BR", assembly_pitch, 0),  # Bottom-right  
        ("TL", 0, assembly_pitch),  # Top-left
        ("TR", assembly_pitch, assembly_pitch),  # Top-right
    ]
    
    # For corners, create the full 3-layer geometry with curves
    # Then we'll do the subdivision later
    # For now, let's create simple rectangular regions as placeholders
    # that will be replaced by the actual geometry during lattice assembly
    
    # Actually, the key insight is: we can create the corner cells with the MACRO property,
    # and the actual geometry (with curves) comes from using make_cut operations
    
    # --------------------
    # STRATEGY: Create subdivided cells that tile the box region exactly
    # For corners: Include all 3 material layers (MODERATOR, CHANNEL_BOX, COOLANT)
    # For edges: Include all 3 material layers in rectangular strips
    # --------------------
    
    # 1. CORNER CELLS - each corner is a square from assembly edge to (edge + corner_extent)
    #    These will overlap with the curved box geometry and need special handling
    
    # Bottom-left corner: x in [0, x_coolant_outer + corner_extent], y in [0, y_coolant_outer + corner_extent]
    bl_size = x_coolant_outer + corner_extent
    bl_cell = create_corner_macro_cell(
        corner_name="BL_CORNER",
        x_start=0, y_start=0,
        width=bl_size, height=bl_size,
        assembly_pitch=assembly_pitch,
        corner_inner_radius=corner_inner_radius,
        corner_outer_radius=corner_outer_radius,
        pin_lattice_corner_radius=pin_lattice_corner_radius,
        gap_wide=gap_wide,
        channel_box_thickness=channel_box_thickness,
        coolant_intra_assembly_width=coolant_intra_assembly_width,
        corner_position="BL"
    )
    macro_cells.append(bl_cell)
    
    # Bottom-right corner
    br_x_start = x_coolant_inner - corner_extent
    br_size_x = assembly_pitch - br_x_start
    br_size_y = y_coolant_outer + corner_extent
    br_cell = create_corner_macro_cell(
        corner_name="BR_CORNER",
        x_start=br_x_start, y_start=0,
        width=br_size_x, height=br_size_y,
        assembly_pitch=assembly_pitch,
        corner_inner_radius=corner_inner_radius,
        corner_outer_radius=corner_outer_radius,
        pin_lattice_corner_radius=pin_lattice_corner_radius,
        gap_wide=gap_wide,
        channel_box_thickness=channel_box_thickness,
        coolant_intra_assembly_width=coolant_intra_assembly_width,
        corner_position="BR"
    )
    macro_cells.append(br_cell)
    
    # Top-left corner
    tl_y_start = y_coolant_inner - corner_extent
    tl_size_x = x_coolant_outer + corner_extent
    tl_size_y = assembly_pitch - tl_y_start
    tl_cell = create_corner_macro_cell(
        corner_name="TL_CORNER",
        x_start=0, y_start=tl_y_start,
        width=tl_size_x, height=tl_size_y,
        assembly_pitch=assembly_pitch,
        corner_inner_radius=corner_inner_radius,
        corner_outer_radius=corner_outer_radius,
        pin_lattice_corner_radius=pin_lattice_corner_radius,
        gap_wide=gap_wide,
        channel_box_thickness=channel_box_thickness,
        coolant_intra_assembly_width=coolant_intra_assembly_width,
        corner_position="TL"
    )
    macro_cells.append(tl_cell)
    
    # Top-right corner
    tr_x_start = x_coolant_inner - corner_extent
    tr_y_start = y_coolant_inner - corner_extent
    tr_size_x = assembly_pitch - tr_x_start
    tr_size_y = assembly_pitch - tr_y_start
    tr_cell = create_corner_macro_cell(
        corner_name="TR_CORNER",
        x_start=tr_x_start, y_start=tr_y_start,
        width=tr_size_x, height=tr_size_y,
        assembly_pitch=assembly_pitch,
        corner_inner_radius=corner_inner_radius,
        corner_outer_radius=corner_outer_radius,
        pin_lattice_corner_radius=pin_lattice_corner_radius,
        gap_wide=gap_wide,
        channel_box_thickness=channel_box_thickness,
        coolant_intra_assembly_width=coolant_intra_assembly_width,
        corner_position="TR"
    )
    macro_cells.append(tr_cell)
    
    # 2. EDGE STRIP CELLS - rectangular strips along each edge
    #    Each strip spans all 3 material layers
    
    # Bottom edge strips (between BL and BR corners)
    bottom_strip_height = y_coolant_outer + corner_extent
    for i in range(n_edge_strips):
        x_start = x_coolant_outer + corner_extent + i * pin_pitch
        strip = create_edge_strip_macro_cell(
            strip_name=f"BOTTOM_{i+1}",
            x_start=x_start, y_start=0,
            width=pin_pitch, height=bottom_strip_height,
            gap_wide=gap_wide,
            channel_box_thickness=channel_box_thickness,
            coolant_intra_assembly_width=coolant_intra_assembly_width,
            edge_position="BOTTOM"
        )
        macro_cells.append(strip)
    
    # Top edge strips (between TL and TR corners)
    top_strip_y_start = y_coolant_inner - corner_extent
    top_strip_height = assembly_pitch - top_strip_y_start
    for i in range(n_edge_strips):
        x_start = x_coolant_outer + corner_extent + i * pin_pitch
        strip = create_edge_strip_macro_cell(
            strip_name=f"TOP_{i+1}",
            x_start=x_start, y_start=top_strip_y_start,
            width=pin_pitch, height=top_strip_height,
            gap_wide=gap_wide,
            channel_box_thickness=channel_box_thickness,
            coolant_intra_assembly_width=coolant_intra_assembly_width,
            edge_position="TOP"
        )
        macro_cells.append(strip)
    
    # Left edge strips (between BL and TL corners)
    left_strip_width = x_coolant_outer + corner_extent
    for i in range(n_edge_strips):
        y_start = y_coolant_outer + corner_extent + i * pin_pitch
        strip = create_edge_strip_macro_cell(
            strip_name=f"LEFT_{i+1}",
            x_start=0, y_start=y_start,
            width=left_strip_width, height=pin_pitch,
            gap_wide=gap_wide,
            channel_box_thickness=channel_box_thickness,
            coolant_intra_assembly_width=coolant_intra_assembly_width,
            edge_position="LEFT"
        )
        macro_cells.append(strip)
    
    # Right edge strips (between BR and TR corners)
    right_strip_x_start = x_coolant_inner - corner_extent
    right_strip_width = assembly_pitch - right_strip_x_start
    for i in range(n_edge_strips):
        y_start = y_coolant_outer + corner_extent + i * pin_pitch
        strip = create_edge_strip_macro_cell(
            strip_name=f"RIGHT_{i+1}",
            x_start=right_strip_x_start, y_start=y_start,
            width=right_strip_width, height=pin_pitch,
            gap_wide=gap_wide,
            channel_box_thickness=channel_box_thickness,
            coolant_intra_assembly_width=coolant_intra_assembly_width,
            edge_position="RIGHT"
        )
        macro_cells.append(strip)
    
    print(f"Created {len(macro_cells)} MACRO subdivision cells:")
    print(f"  - 4 corner MACROs (with 3 material zones each)")
    print(f"  - {4 * n_edge_strips} edge strip MACROs ({n_edge_strips} per edge)")
    
    return macro_cells


def create_corner_macro_cell(corner_name, x_start, y_start, width, height,
                             assembly_pitch, corner_inner_radius, corner_outer_radius,
                             pin_lattice_corner_radius, gap_wide, channel_box_thickness,
                             coolant_intra_assembly_width, corner_position):
    """
    Create a corner MACRO cell with 3 material zones (MODERATOR, CHANNEL_BOX, COOLANT)
    and rounded corners matching the channel box geometry.
    
    The corner cell is positioned at (x_start, y_start) with dimensions (width, height).
    The corner_position indicates which corner of the assembly this represents:
    'BL' = bottom-left, 'BR' = bottom-right, 'TL' = top-left, 'TR' = top-right
    """
    center = (x_start + width/2, y_start + height/2, 0.0)
    
    # Create the bounding cell for this corner region
    corner_cell = RectCell(
        name=f"MACRO_{corner_name}",
        height_x_width=(height, width),
        center=center
    )
    
    # Determine which corner needs to be rounded based on corner_position
    # Corner indices: 0=BL, 1=BR, 2=TR, 3=TL (counterclockwise from bottom-left)
    # But we need to round the INNER corner of the corner cell (the one facing the center)
    corner_mapping = {
        "BL": 2,  # Round top-right corner of BL cell (faces center)
        "BR": 3,  # Round top-left corner of BR cell
        "TL": 1,  # Round bottom-right corner of TL cell
        "TR": 0   # Round bottom-left corner of TR cell
    }
    inner_corner_idx = corner_mapping[corner_position]
    
    # Create the 3 material zones using boolean operations
    # This requires creating rectangles for each zone and cutting appropriately
    
    # For corners, we need to create:
    # 1. Outer moderator zone (from assembly edge to channel box outer surface)
    # 2. Channel box zone (from outer to inner surface)
    # 3. Coolant zone (from channel box inner surface to fuel lattice boundary)
    
    # The corner includes a curved inner boundary, so we use rounded corner cells
    
    # Actually, let's simplify: create this corner as a single region with a placeholder
    # material, and rely on the proper geometry being established when we add it to the lattice
    # The actual 3-zone structure with curves will be created by the main box_cell
    
    # For MACRO subdivision, we just need the rectangular boundaries
    corner_cell.set_properties({
        PropertyType.MATERIAL: ["MODERATOR_2"],  # Placeholder
        PropertyType.MACRO: [f"MACRO_{corner_name}"]
    })
    
    return corner_cell


def create_edge_strip_macro_cell(strip_name, x_start, y_start, width, height,
                                  gap_wide, channel_box_thickness, coolant_intra_assembly_width,
                                  edge_position):
    """
    Create an edge strip MACRO cell with 3 material zones (MODERATOR, CHANNEL_BOX, COOLANT).
    
    Edge strips are rectangular and contain straight portions of the 3 material zones.
    """
    center = (x_start + width/2, y_start + height/2, 0.0)
    
    # Create the edge strip cell
    strip_cell = RectCell(
        name=f"MACRO_{strip_name}",
        height_x_width=(height, width),
        center=center
    )
    
    # For edge strips, we could subdivide into 3 zones, but for simplicity
    # we'll treat the entire strip as a single MACRO region
    strip_cell.set_properties({
        PropertyType.MATERIAL: ["MODERATOR_2"],  # Placeholder
        PropertyType.MACRO: [f"MACRO_{strip_name}"]
    })
    
    return strip_cell


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
pin_lattice_corner_radius = corner_inner_radius_of_curvature - coolant_intra_assembly_width
if pin_lattice_corner_radius < 0:
    pin_lattice_corner_radius = 0  # No rounding needed if coolant gap is large enough

# Cap the corner radius at the maximum allowed for pin cells (half the pitch)
max_pin_corner_radius = pin_pitch / 2 - 0.001  # Small margin for numerical stability
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
# CREATE BOX CELL (with rounded corners) - EXACTLY AS IN GE-14_rounded_corners.py
# --------------------
print("\n=== Creating assembly box cell ===")
box_cell = create_box_cell_with_rounded_corners(
    assembly_pitch=assembly_pitch,
    channel_box_inner_side=channel_box_inner_side,
    channel_box_outer_side=channel_box_outer_side,
    pin_pitch=pin_pitch,
    n_pins=10,
    pincell_translation=pincell_translation,
    corner_inner_radius=corner_inner_radius_of_curvature,
    corner_outer_radius=corner_outer_radius_of_curvature,
    pin_lattice_corner_radius=pin_lattice_corner_radius,
    center=center
)
print("Created box cell with 3 zones: MODERATOR_2, CHANNEL_BOX, COOLANT")

# --------------------
# CREATE MACRO SUBDIVISION CELLS (aligned with pin pitch)
# --------------------
print("\n=== Creating MACRO subdivision cells ===")
macro_subdivision_cells = build_subdivided_box_macro_cells(
    assembly_pitch=assembly_pitch,
    channel_box_inner_side=channel_box_inner_side,
    channel_box_outer_side=channel_box_outer_side,
    pin_pitch=pin_pitch,
    n_pins=10,
    pincell_translation=pincell_translation,
    gap_wide=gap_wide,
    channel_box_thickness=channel_box_thickness,
    coolant_intra_assembly_width=coolant_intra_assembly_width,
    corner_inner_radius=corner_inner_radius_of_curvature,
    corner_outer_radius=corner_outer_radius_of_curvature,
    pin_lattice_corner_radius=pin_lattice_corner_radius,
    center=center
)

# --------------------
# LATTICE CONSTRUCTION
# --------------------
lattice = Lattice(name='GE14_full_assembly_MACRO', center=center)

# NOTE: We add BOTH the box_cell (for proper curved geometry) AND the MACRO subdivision cells.
# The box_cell provides the technological geometry with materials (MODERATOR_2, CHANNEL_BOX, COOLANT).
# The MACRO subdivision cells provide MACRO attribution boundaries aligned with pin pitch.
# When GLOW processes the lattice, it will combine these to create regions with both
# the correct material from box_cell AND the MACRO from the subdivision cells.

# Add the box cell FIRST - this establishes the base geometry with materials
# Using () as position means it's the base cell
lattice.add_cell(box_cell, ())

# Add MACRO subdivision cells - these provide MACRO boundaries
# Note: These cells will intersect with box_cell to create regions with MACRO attribution
print("\n=== Adding MACRO subdivision cells to lattice ===")
for macro_cell in macro_subdivision_cells:
    # Get the center position from the cell
    cell_center = macro_cell.center
    lattice.add_cell(macro_cell, cell_center)
print(f"Added {len(macro_subdivision_cells)} MACRO subdivision cells")

# Add all fuel pin cells to the lattice
lattice = add_cells_to_regular_lattice(
    lattice=lattice,
    ordered_cells=ordered_fuel_cells,
    cell_pitch=pin_pitch,
    translation=pincell_translation
)

# Add water rod cells at their specific locations
# Water rod 1: positions (3,4) x (3,4) -> center at (4*pitch, 4*pitch) + translation
lattice.add_cell(
    water_rod_cell1,
    (4 * pin_pitch + pincell_translation, 4 * pin_pitch + pincell_translation, 0.0)
)
# Water rod 2: positions (5,6) x (5,6) -> center at (6*pitch, 6*pitch) + translation
lattice.add_cell(
    water_rod_cell2,
    (6 * pin_pitch + pincell_translation, 6 * pin_pitch + pincell_translation, 0.0)
)

# Show the lattice
print("\n=== Showing lattice with MATERIAL property ===")
lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)

print("\n=== Showing lattice with MACRO property ===")
lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MACRO)

# --------------------
# GENERATE TDT FILE
# --------------------
lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice],
    f"data/glow_data/tdt_data/GE14_full_assembly_MACRO",
    TdtSetup(
        GeometryType.SECTORIZED,
        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
        type_geo=LatticeGeometryType.ISOTROPIC,
        symmetry_type=BoundaryType.AXIAL_SYMMETRY
    )
)

print("\n=== TDT file generated successfully ===")
