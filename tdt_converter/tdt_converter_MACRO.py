"""
TDT Converter with MACRO definitions.

This script converts a GLOW-format tdt file into a GEO-format tdt file with MACRO definitions.
In GLOW format, all geometrical elements are listed individually.
In GEO MACRO format, elements are grouped into sub-geometries (MACROs), typically corresponding
to pin cells in a cartesian lattice.

The MACRO grouping is determined by analyzing the element centers to identify which elements
belong to the same pin cell based on spatial proximity.
"""

from pathlib import Path
import re
import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class Element:
    """Represents a geometric element (line segment or circle)."""
    elem_id: int
    elem_type: int  # 1 = line segment, 2 = circle
    node_minus: int
    node_plus: int
    cx: float
    cy: float
    ex_or_r: float
    ey_or_theta1: float
    theta2: float = 0.0
    comment: str = ""
    
    def get_center(self, pitch: float) -> Tuple[float, float]:
        """Get the center point of this element for MACRO grouping."""
        if self.elem_type == 2:  # Circle
            return (self.cx, self.cy)
        else:  # Line segment - use midpoint
            return (self.cx + self.ex_or_r / 2, self.cy + self.ey_or_theta1 / 2)


@dataclass
class GlowTDTData:
    """Parsed data from a GLOW-format TDT file."""
    typgeo: int = 0
    nbfold: int = 0
    nbnode: int = 0
    nbelem: int = 0
    nbmacro: int = 1
    nreg: int = 0
    z: int = 0
    mac2: int = 1
    index: int = 0
    kindex: int = 0
    prec: int = 1
    eps: float = 1.0e-5
    eps0: float = 1.0e-5
    flux_regions: List[int] = field(default_factory=list)
    macro_name: str = "mac"
    macro_order: str = ""
    elements: List[Element] = field(default_factory=list)
    defaul: int = 0
    nbbcda: int = 0
    allsur: int = 0
    albedo: float = 1.0
    medium_per_region: List[int] = field(default_factory=list)
    material_comments: List[str] = field(default_factory=list)


def parse_glow_tdt_file(filepath: Path) -> GlowTDTData:
    """Parse a GLOW-format TDT file."""
    data = GlowTDTData()
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Parse header section
        if line.startswith('* typge'):
            i += 1
            values = lines[i].replace(',', ' ').split()
            data.typgeo = int(values[0])
            data.nbfold = int(values[1])
            data.nbnode = int(values[2])
            data.nbelem = int(values[3])
            data.nbmacro = int(values[4])
            data.nreg = int(values[5])
            data.z = int(values[6])
            data.mac2 = int(values[7])
        
        elif line.startswith('* index'):
            i += 1
            values = lines[i].split()
            data.index = int(values[0])
            data.kindex = int(values[1])
            data.prec = int(values[2])
        
        elif line.startswith('*') and 'eps' in line.lower() and 'eps0' in line.lower():
            i += 1
            values = lines[i].split()
            data.eps = float(values[0])
            data.eps0 = float(values[1])
        
        elif line.startswith('*') and 'flux region number per geometry' in line.lower():
            # Parse only the specific "flux region number per geometry region" section
            i += 1
            flux_str = ""
            while i < len(lines):
                current_line = lines[i].strip()
                if current_line.startswith('*') and 'names' in current_line.lower():
                    break
                if current_line.startswith('mac') and not ',' in current_line:
                    break
                if current_line == '':
                    i += 1
                    continue
                flux_str += current_line + " "
                i += 1
            flux_str = flux_str.replace(',', ' ')
            data.flux_regions = [int(x) for x in flux_str.split() if x.isdigit()]
            continue
        
        elif line.startswith('*') and 'names of macro' in line.lower():
            i += 1
            data.macro_name = lines[i].strip()
        
        elif line.startswith('*') and 'macro order' in line.lower():
            i += 1
            # Skip this - it contains shorthand like "28*1"
            data.macro_order = lines[i].strip()
        
        elif line.startswith('* ELEM'):
            # Parse element
            parts = line.split()
            elem_id = int(parts[2])
            comment = " ".join(parts[3:]) if len(parts) > 3 else ""
            
            i += 1
            type_node_line = lines[i].strip()
            type_node_values = type_node_line.replace(',', ' ').split()
            elem_type = int(type_node_values[0])
            node_minus = int(type_node_values[1])
            node_plus = int(type_node_values[2])
            
            i += 1  # Skip comment line (*)
            i += 1
            coords_line = lines[i].strip()
            # Parse coordinates more robustly
            coords_str = coords_line.replace(',', ' ')
            coords = []
            for part in coords_str.split():
                try:
                    coords.append(float(part))
                except ValueError:
                    continue
            
            elem = Element(
                elem_id=elem_id,
                elem_type=elem_type,
                node_minus=node_minus,
                node_plus=node_plus,
                cx=coords[0] if len(coords) > 0 else 0.0,
                cy=coords[1] if len(coords) > 1 else 0.0,
                ex_or_r=coords[2] if len(coords) > 2 else 0.0,
                ey_or_theta1=coords[3] if len(coords) > 3 else 0.0,
                theta2=coords[4] if len(coords) > 4 else 0.0,
                comment=comment
            )
            data.elements.append(elem)
        
        elif line.startswith('* boundaries') or line.startswith('* boundary'):
            i += 1
            bc_values = lines[i].replace(',', ' ').split()
            data.defaul = int(bc_values[0])
            data.nbbcda = int(bc_values[1])
            data.allsur = int(bc_values[2])
        
        elif line.startswith('* albedo'):
            i += 1
            data.albedo = float(lines[i].strip())
        
        elif line.startswith('#'):
            data.material_comments.append(line)
        
        elif line.startswith('* medium'):
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('-'):
                val = lines[i].strip()
                if val.isdigit():
                    data.medium_per_region.append(int(val))
                i += 1
            continue
        
        i += 1
    
    return data


def identify_pin_cells(data: GlowTDTData, num_macros: int) -> Dict[int, List[int]]:
    """
    Identify pin cells by grouping elements based on their circle centers.
    Returns a dictionary mapping macro_id -> list of flux_region indices.
    
    Args:
        data: Parsed GLOW TDT data
        num_macros: Number of MACROs to create
    """
    # Find all circles and their centers
    circle_centers = {}
    for elem in data.elements:
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            if center not in circle_centers:
                circle_centers[center] = []
            circle_centers[center].append(elem.elem_id)
    
    # Sort centers to get consistent ordering (bottom-left to top-right)
    sorted_centers = sorted(circle_centers.keys(), key=lambda c: (c[1], c[0]))
    
    # The number of unique pin cell positions
    detected_macros = len(sorted_centers)
    
    # Use detected or specified number of macros
    actual_macros = num_macros if num_macros > 0 else detected_macros
    if actual_macros == 0:
        actual_macros = 1
    
    # Map each flux region to a macro based on which pin cell it belongs to
    regions_per_pin = data.nreg // actual_macros
    
    macro_assignments = {}
    for macro_id in range(1, actual_macros + 1):
        start_region = (macro_id - 1) * regions_per_pin + 1
        end_region = macro_id * regions_per_pin
        macro_assignments[macro_id] = list(range(start_region, end_region + 1))
    
    return macro_assignments


def compute_pitch(data: GlowTDTData) -> float:
    """Compute the pin cell pitch from the geometry."""
    # Find max coordinates from line segments
    max_x = 0.0
    for elem in data.elements:
        if elem.elem_type == 1:  # Line segment
            max_x = max(max_x, elem.cx + abs(elem.ex_or_r))
    
    # Find number of unique circle centers in x-direction
    x_centers = set()
    for elem in data.elements:
        if elem.elem_type == 2:
            x_centers.add(round(elem.cx, 4))
    
    num_pins_x = len(x_centers)
    if num_pins_x > 0:
        return max_x / num_pins_x
    return max_x


def detect_grid_dimensions(elements: List[Element]) -> Tuple[int, int, Dict[Tuple[float, float], int]]:
    """
    Detect grid dimensions (nx, ny) and number of circles per pin cell.
    
    Returns:
        (nx, ny, circles_per_pin): Grid dimensions and dict mapping center to circle count
                                   Rectangle-only cells have 0 circles.
    """
    # Find unique circle centers and count circles per center
    circle_centers = {}
    for elem in elements:
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            if center not in circle_centers:
                circle_centers[center] = 0
            circle_centers[center] += 1
    
    if not circle_centers:
        return 1, 1, {}
    
    # Get unique x and y coordinates from circles
    x_coords = sorted(set(c[0] for c in circle_centers.keys()))
    y_coords = sorted(set(c[1] for c in circle_centers.keys()))
    
    # Compute pitch from circle centers
    if len(x_coords) >= 2:
        pitch = x_coords[1] - x_coords[0]
    else:
        pitch = x_coords[0] * 2  # Assume center is at half-pitch
    
    # Compute grid dimensions from circle center range
    # Range = (n-1) * pitch, so n = range/pitch + 1
    x_range = x_coords[-1] - x_coords[0]
    y_range = y_coords[-1] - y_coords[0]
    nx = int(round(x_range / pitch)) + 1
    ny = int(round(y_range / pitch)) + 1
    
    # Build complete grid including rectangle-only cells
    all_centers = {}
    for row in range(ny):
        for col in range(nx):
            cx = round(x_coords[0] + col * pitch, 4)
            cy = round(y_coords[0] + row * pitch, 4)
            # Use circle count if exists, otherwise 0 for rectangle-only
            all_centers[(cx, cy)] = circle_centers.get((cx, cy), 0)
    
    return nx, ny, all_centers


def generate_merge_array_variable(data: GlowTDTData, nx: int, ny: int, 
                                   circles_per_pin: Dict[Tuple[float, float], int]) -> List[int]:
    """
    Generate the merge array for GEO format with variable circles per pin.
    
    The merge array interleaves regions from macros in the same row.
    Each pin has (circles + 1) regions (circles + 1 for the background region outside circles).
    
    Args:
        data: Parsed GLOW data
        nx: Number of pins in x direction
        ny: Number of pins in y direction
        circles_per_pin: Dict mapping pin center to circle count
    """
    # Sort centers by grid position (row, col)
    sorted_centers = sorted(circles_per_pin.keys(), key=lambda c: (c[1], c[0]))
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    
    # Map center to grid position and regions per pin
    center_to_grid = {}
    regions_per_pin = {}
    for center in sorted_centers:
        col = x_coords.index(center[0])
        row = y_coords.index(center[1])
        center_to_grid[center] = (col, row)
        # Each pin has n_circles + 1 regions (circles plus background)
        regions_per_pin[(col, row)] = circles_per_pin[center] + 1
    
    # Calculate starting region for each macro
    macro_start_region = {}
    current_region = 1
    for row in range(ny):
        for col in range(nx):
            macro_start_region[(col, row)] = current_region
            current_region += regions_per_pin[(col, row)]
    
    merge = []
    
    # Find the max regions per pin in any macro for interleaving
    max_regions = max(regions_per_pin.values())
    
    # Process each row
    for row in range(ny):
        # For each region index (up to max)
        for region_idx in range(max_regions):
            # Interleave from all macros in this row
            for col in range(nx):
                n_regions = regions_per_pin[(col, row)]
                if region_idx < n_regions:
                    region_num = macro_start_region[(col, row)] + region_idx
                    merge.append(region_num)
    
    return merge


def generate_macro_indices_variable(nx: int, ny: int, 
                                     circles_per_pin: Dict[Tuple[float, float], int]) -> List[int]:
    """Generate macro indices for each flux region with variable circles per pin."""
    sorted_centers = sorted(circles_per_pin.keys(), key=lambda c: (c[1], c[0]))
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    
    indices = []
    macro_id = 1
    for row in range(ny):
        for col in range(nx):
            center = (x_coords[col], y_coords[row])
            n_circles = circles_per_pin.get(center, 6)
            regions = n_circles + 1  # circles + background
            indices.extend([macro_id] * regions)
            macro_id += 1
    return indices


def compute_macro_indices_from_elements(elements: List[Element], nx: int, ny: int,
                                         circles_per_pin: Dict[Tuple[float, float], int]) -> List[int]:
    """
    Compute macro indices for each region based on element positions.
    
    Each element belongs to a specific pin cell based on its center position (for circles)
    or the pin cell it bounds (for lines). Regions are numbered per element in order.
    
    Args:
        elements: List of elements in original order
        nx: Number of pins in x direction
        ny: Number of pins in y direction
        circles_per_pin: Dict mapping pin center to circle count
    """
    # Build grid mapping from circle centers
    sorted_centers = sorted(circles_per_pin.keys(), key=lambda c: (c[1], c[0]))
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    
    # Compute pitch
    if len(x_coords) >= 2:
        pitch = x_coords[1] - x_coords[0]
    else:
        pitch = x_coords[0] * 2  # Assume center is at half-pitch
    
    def get_macro_id(col: int, row: int) -> int:
        """Get 1-based macro ID for grid position (col, row)."""
        return row * nx + col + 1
    
    def find_pin_for_element(elem: Element) -> Tuple[int, int]:
        """Find which pin cell (col, row) an element belongs to."""
        if elem.elem_type == 2:  # Circle
            # Circle center determines pin
            center = (round(elem.cx, 4), round(elem.cy, 4))
            if center in circles_per_pin:
                col = x_coords.index(center[0])
                row = y_coords.index(center[1])
                return (col, row)
        
        # For lines or unmatched circles, find nearest pin center
        elem_center_x = elem.cx + elem.ex_or_r / 2 if elem.elem_type == 1 else elem.cx
        elem_center_y = elem.cy + elem.ey_or_theta1 / 2 if elem.elem_type == 1 else elem.cy
        
        # Find closest pin center
        min_dist = float('inf')
        best_col, best_row = 0, 0
        for center in sorted_centers:
            dist = (elem_center_x - center[0])**2 + (elem_center_y - center[1])**2
            if dist < min_dist:
                min_dist = dist
                best_col = x_coords.index(center[0])
                best_row = y_coords.index(center[1])
        
        return (best_col, best_row)
    
    # Track current pin and regions count
    macro_indices = []
    current_pin = None
    
    for elem in elements:
        pin = find_pin_for_element(elem)
        if current_pin is None:
            current_pin = pin
        
        # Each element contributes 1 region (simplified - actual TDT may differ)
        # The element defines a region bounded by its surfaces
        macro_id = get_macro_id(pin[0], pin[1])
        macro_indices.append(macro_id)
    
    return macro_indices


def compute_macro_indices_for_glow(elements: List[Element], nx: int, ny: int,
                                    circles_per_pin: Dict[Tuple[float, float], int]) -> List[int]:
    """
    Compute macro indices for each flux region based on GLOW's pin ordering.
    
    GLOW orders pins from top-right to bottom-left, and each pin contributes
    (n_circles + 1) regions where n_circles varies per pin.
    Rectangle-only cells (0 circles) contribute 1 region each.
    
    Args:
        elements: List of elements in GLOW order
        nx: Number of pins in x direction
        ny: Number of pins in y direction  
        circles_per_pin: Dict mapping pin center to circle count (0 for rect-only)
    """
    # Build grid mapping from all cell centers
    sorted_centers = sorted(circles_per_pin.keys(), key=lambda c: (c[1], c[0]))
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    
    def get_macro_id(col: int, row: int) -> int:
        """Get 1-based macro ID for grid position (col, row).
        Macro IDs are numbered row-major from bottom-left:
        7 8 9
        4 5 6
        1 2 3
        """
        return row * nx + col + 1
    
    def get_grid_pos(center: Tuple[float, float]) -> Tuple[int, int]:
        """Get (col, row) grid position for a center coordinate."""
        col = x_coords.index(center[0])
        row = y_coords.index(center[1])
        return (col, row)
    
    # Separate cells with circles from rectangle-only cells
    cells_with_circles = {c: n for c, n in circles_per_pin.items() if n > 0}
    rect_only_cells = {c for c, n in circles_per_pin.items() if n == 0}
    
    # Build ordering of pin cells from element traversal
    pin_order = []  # List of centers in the order they appear
    seen_centers = set()
    
    for elem in elements:
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            if center in cells_with_circles and center not in seen_centers:
                seen_centers.add(center)
                pin_order.append(center)
    
    # Build macro_indices by following pin_order, inserting rect-only cells at correct positions
    # GLOW orders pins from top-right to bottom-left (decreasing row, decreasing col within row)
    macro_indices = []
    processed_macros = set()
    
    for center in pin_order:
        col, row = get_grid_pos(center)
        macro_id = get_macro_id(col, row)
        
        # Before processing this pin, check if any rect-only cells should come first
        # (they would have higher macro_id if we're going in decreasing order)
        for rect_center in sorted(rect_only_cells, key=lambda c: get_macro_id(*get_grid_pos(c)), reverse=True):
            rect_col, rect_row = get_grid_pos(rect_center)
            rect_macro_id = get_macro_id(rect_col, rect_row)
            if rect_macro_id not in processed_macros and rect_macro_id > macro_id:
                # This rect-only cell should come before current pin
                macro_indices.append(rect_macro_id)  # 1 region for rect-only
                processed_macros.add(rect_macro_id)
        
        # Now add regions for this pin cell
        n_circles = cells_with_circles[center]
        n_regions = n_circles + 1  # circles + background
        macro_indices.extend([macro_id] * n_regions)
        processed_macros.add(macro_id)
    
    # Add any remaining rect-only cells (those with lower macro_id than all processed pins)
    for rect_center in sorted(rect_only_cells, key=lambda c: get_macro_id(*get_grid_pos(c)), reverse=True):
        rect_col, rect_row = get_grid_pos(rect_center)
        rect_macro_id = get_macro_id(rect_col, rect_row)
        if rect_macro_id not in processed_macros:
            macro_indices.append(rect_macro_id)  # 1 region for rect-only
            processed_macros.add(rect_macro_id)
    
    return macro_indices


def compute_boundary_conditions(data: GlowTDTData) -> List[Tuple[List[int], float]]:
    """
    Compute boundary conditions based on the geometry.
    Returns list of (element_ids, albedo) tuples for each boundary.
    """
    # Identify elements on each boundary (left, bottom, right, top)
    max_x = 0.0
    max_y = 0.0
    
    for elem in data.elements:
        if elem.elem_type == 1:  # Line segment
            max_x = max(max_x, elem.cx + abs(elem.ex_or_r))
            max_y = max(max_y, elem.cy + abs(elem.ey_or_theta1))
    
    eps = 1e-4
    left_boundary = []
    bottom_boundary = []
    right_boundary = []
    top_boundary = []
    
    for i, elem in enumerate(data.elements):
        if elem.elem_type == 1:  # Line segment
            # Check if on left boundary (x = 0)
            if abs(elem.cx) < eps and abs(elem.ex_or_r) < eps:
                left_boundary.append(i + 1)
            # Check if on bottom boundary (y = 0)
            if abs(elem.cy) < eps and abs(elem.ey_or_theta1) < eps:
                bottom_boundary.append(i + 1)
            # Check if on right boundary (x = max_x)
            if abs(elem.cx - max_x) < eps or abs(elem.cx + elem.ex_or_r - max_x) < eps:
                if abs(elem.ex_or_r) < eps:  # Vertical line at right edge
                    right_boundary.append(i + 1)
            # Check if on top boundary (y = max_y)
            if abs(elem.cy - max_y) < eps or abs(elem.cy + elem.ey_or_theta1 - max_y) < eps:
                if abs(elem.ey_or_theta1) < eps:  # Horizontal line at top edge
                    top_boundary.append(i + 1)
    
    boundaries = []
    if bottom_boundary:
        boundaries.append((bottom_boundary, 1.0))
    if left_boundary:
        boundaries.append((left_boundary, 1.0))
    if right_boundary:
        boundaries.append((right_boundary, 1.0))
    if top_boundary:
        boundaries.append((top_boundary, 1.0))
    
    return boundaries


def format_number_scientific(value: float) -> str:
    """Format a number in scientific notation like Fortran."""
    if value == 0.0:
        return "     0.0000000E+00"
    return f"{value:18.7E}"


def format_int(value: int, width: int = 6) -> str:
    """Format an integer with specified width."""
    return f"{value:>{width}}"


def write_geo_macro_file(data: GlowTDTData, output_path: Path, num_macros: int = 0):
    """
    Write a GEO-format TDT file with MACRO definitions.
    
    Args:
        data: Parsed GLOW TDT data
        output_path: Path to output file
        num_macros: Number of macros (0 = auto-detect from geometry)
    """
    # Detect grid dimensions and circles per pin
    nx, ny, circles_per_pin = detect_grid_dimensions(data.elements)
    detected_macros = nx * ny
    
    if num_macros == 0:
        num_macros = detected_macros
    
    print(f"  Grid dimensions: {nx}x{ny} = {num_macros} macros")
    
    # Print circles per pin summary
    circle_counts = list(circles_per_pin.values())
    min_circles = min(circle_counts)
    max_circles = max(circle_counts)
    if min_circles == max_circles:
        print(f"  Circles per pin: {min_circles}")
    else:
        print(f"  Circles per pin: {min_circles}-{max_circles} (variable)")
    
    # Use original merge array from input file (preserves GLOW format)
    if data.flux_regions and len(data.flux_regions) == data.nreg:
        merge = data.flux_regions
    else:
        # Fallback to identity merge
        merge = list(range(1, data.nreg + 1))
    
    # Generate macro_indices based on which pin cell each region belongs to
    # GLOW orders pins from top-right to bottom-left
    macro_indices = compute_macro_indices_for_glow(data.elements, nx, ny, circles_per_pin)
    
    # Keep original elements with their original node connectivity
    # MACRO definition only requires grouping via merge/macro_indices, not element reordering or node renumbering
    ordered_elements = data.elements  # Keep original order and node numbers
    
    # Use original nbnode from input file
    actual_nbnode = data.nbnode
    
    with open(output_path, 'w') as f:
        # Header
        f.write("BEGIN\n\n")
        f.write("          DEFINE DOMAINE\n")
        f.write("          ==============\n\n")
        
        # Section 1: Main dimensions
        f.write("          1.main dimensions:\n\n")
        f.write("*typgeo  nbfold  nbnode  nbelem  nbmacro  nbflux\n")
        f.write(f"     {data.typgeo}     {data.nbfold}    {actual_nbnode}    {data.nbelem}     {num_macros}    {data.nreg}\n\n")
        
        # Section 2: Impression and precision
        f.write("          2.impression and precision:\n\n")
        f.write("*index   kndex   prec\n")
        f.write(f"     {data.index}     {data.kindex}     {data.prec}\n\n")
        
        # Section 3: Precision of geometry data
        f.write("          3.precision of geometry data:\n\n")
        f.write("*eps\n")
        f.write(f"     {data.eps:.7E}\n\n")
        
        # Section 4: Flux region mapping (merge array)
        f.write("          4.flux region number per geometry region (mesh):\n\n")
        f.write("*merge\n")
        # Write merge array 10 values per line with proper width for large numbers
        for i in range(0, len(merge), 10):
            line_values = merge[i:i+10]
            line = "    " + "    ".join(f"{v:3d}" for v in line_values)
            f.write(line + "\n")
        f.write("\n")
        
        # Section 5: Macro names (4 names per line to avoid very long lines)
        f.write("          5.name of geometry:\n\n")
        f.write("*macro_names\n")
        names_per_line = 4
        for i in range(0, num_macros, names_per_line):
            macro_names_chunk = [f"MACR{j:06d}" for j in range(i+1, min(i+names_per_line+1, num_macros+1))]
            f.write("   " + "     ".join(macro_names_chunk) + "\n")
        f.write("\n")
        
        # Section 6: Macro indices per flux region
        f.write("          6.macro order number per flux region:\n\n")
        f.write("*macro_indices\n")
        for i in range(0, len(macro_indices), 10):
            line_values = macro_indices[i:i+10]
            line = "    " + "    ".join(f"{v:3d}" for v in line_values)
            f.write(line + "\n")
        f.write("\n")
        
        # Section 7: Element data
        f.write("          7.read integer and real data for each elements:\n")
        
        # Elements already reordered and renumbered above (before calculating actual_nbnode)
        for i, elem in enumerate(ordered_elements):
            f.write(f"\n elem =          {i+1}\n")
            f.write("*type    node-   node+\n")
            f.write(f"     {elem.elem_type}    {elem.node_minus}    {elem.node_plus}\n")
            f.write("*cx            cy            ex or R       ey or theta1  theta2\n")
            f.write(f"{format_number_scientific(elem.cx)}{format_number_scientific(elem.cy)}")
            f.write(f"{format_number_scientific(elem.ex_or_r)}{format_number_scientific(elem.ey_or_theta1)}")
            f.write(f"{format_number_scientific(elem.theta2)}\n")
        
        # Section 8: Boundary conditions
        f.write("\n          8.read integer and real data for boundary conditions:\n\n")
        f.write("*defaul  nbbcda  allsur  divsur  ndivsur\n")
        # Use nbbcda=0 like original GLOW file - let SALT auto-detect perimeter from node=0 elements
        f.write(f"     {data.defaul}     0     {data.allsur}     0     0\n\n")
        
        f.write("          DEFAULT = REFLECTIVE\n")
        f.write("          ===================\n\n")
        f.write("*albedo  deltasur\n")
        f.write("     1.0000000E+00     0.0000000E+00\n")
        
        # No explicit boundary conditions needed - SALT determines perimeter automatically
        
        # Section 9: Medium per node
        f.write("\n          9.medium per node:\n\n")
        
        # Include material index comments from GLOW file
        if data.material_comments:
            f.write("          Material index mapping (from GLOW):\n")
            for comment in data.material_comments:
                f.write(f"          {comment}\n")
            f.write("\n")
        
        f.write("*mil(nbreg)\n")
        # Reorder medium based on merge array
        reordered_medium = reorder_medium_for_geo(data.medium_per_region, merge)
        for i in range(0, len(reordered_medium), 10):
            line_values = reordered_medium[i:i+10]
            line = "    " + "    ".join(f"{v:2d}" for v in line_values)
            f.write(line + "\n")
        
        f.write("\nEND\n")


def reorder_elements_for_geo(elements: List[Element]) -> List[Element]:
    """
    Reorder elements for GEO MACRO format.
    The GEO format groups elements by pin cell position.
    For a 2x2 case, elements are ordered: 
    - Pin cell 1 (bottom-left): boundary lines + circles
    - Pin cell 2 (bottom-right): boundary lines + circles  
    - Pin cell 3 (top-left): boundary lines + circles
    - Pin cell 4 (top-right): boundary lines + circles
    
    Line segment assignment rules:
    - Lines are assigned to the pin cell that "owns" them
    - For shared internal boundaries, lines go to the lower/left cell
    - The first macro (bottom-left) gets all 4 boundaries
    - Subsequent macros only get their non-shared boundaries
    """
    if not elements:
        return []
    
    # Find unique circle centers (pin cell positions)
    circle_centers = {}
    for elem in elements:
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            if center not in circle_centers:
                circle_centers[center] = []
            circle_centers[center].append(elem)
    
    if not circle_centers:
        # No circles found, return elements as-is
        return elements
    
    # Sort centers: bottom-left to top-right (row by row)
    sorted_centers = sorted(circle_centers.keys(), key=lambda c: (c[1], c[0]))
    
    # Determine grid dimensions
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    nx = len(x_coords)
    ny = len(y_coords)
    
    # Compute pitch from circle centers
    if len(x_coords) >= 2:
        pitch = x_coords[1] - x_coords[0]
    else:
        pitch = sorted_centers[0][0] * 2
    
    # Create pin cell boundaries for each center
    # Each pin cell is defined by (x_min, x_max, y_min, y_max)
    cell_bounds = {}
    for center in sorted_centers:
        cx, cy = center
        half_pitch = pitch / 2
        cell_bounds[center] = (
            cx - half_pitch,  # x_min
            cx + half_pitch,  # x_max
            cy - half_pitch,  # y_min
            cy + half_pitch   # y_max
        )
    
    # Group line segments
    line_segments = [e for e in elements if e.elem_type == 1]
    
    # Normalize line segments to have positive direction vectors
    # and create a mapping of normalized lines
    normalized_lines = []
    for line in line_segments:
        cx, cy = line.cx, line.cy
        dx, dy = line.ex_or_r, line.ey_or_theta1
        
        # Normalize: ensure positive direction (dx >= 0, dy >= 0)
        if dx < 0 or (dx == 0 and dy < 0):
            # Flip the line: new start = old end
            new_cx = cx + dx
            new_cy = cy + dy
            new_dx = -dx
            new_dy = -dy
            normalized_lines.append({
                'orig': line,
                'cx': new_cx, 'cy': new_cy,
                'dx': new_dx, 'dy': new_dy,
                'end_x': new_cx + new_dx,
                'end_y': new_cy + new_dy
            })
        else:
            normalized_lines.append({
                'orig': line,
                'cx': cx, 'cy': cy,
                'dx': dx, 'dy': dy,
                'end_x': cx + dx,
                'end_y': cy + dy
            })
    
    # Assign lines to pin cells based on geometric position
    # Rules: A line belongs to the cell whose boundary it lies on,
    # For shared boundaries:
    # - Horizontal lines go to the LOWER cell (where the line is the top boundary/y_max)
    # - Vertical lines go to the LEFT cell (where the line is the right boundary/x_max)
    def assign_line_to_cell(norm_line, sorted_centers, cell_bounds, tol=1e-4):
        """Assign a normalized line segment to a pin cell."""
        cx, cy = norm_line['cx'], norm_line['cy']
        end_x, end_y = norm_line['end_x'], norm_line['end_y']
        dx, dy = norm_line['dx'], norm_line['dy']
        
        # Determine if line is horizontal or vertical
        is_horizontal = abs(dy) < tol
        is_vertical = abs(dx) < tol
        
        best_center = None
        
        if is_horizontal:
            # Horizontal line at y = cy
            # Find cell where this line is on the TOP boundary (y_max)
            # This assigns shared boundaries to the LOWER cell
            for center in sorted_centers:
                bounds = cell_bounds[center]
                x_min, x_max, y_min, y_max = bounds
                # Check if line is on top boundary of this cell
                if abs(cy - y_max) < tol:
                    line_x_min = min(cx, end_x)
                    line_x_max = max(cx, end_x)
                    if line_x_min >= x_min - tol and line_x_max <= x_max + tol:
                        best_center = center
                        break
            # If not found (external boundary at bottom), check bottom boundaries
            if best_center is None:
                for center in sorted_centers:
                    bounds = cell_bounds[center]
                    x_min, x_max, y_min, y_max = bounds
                    if abs(cy - y_min) < tol:
                        line_x_min = min(cx, end_x)
                        line_x_max = max(cx, end_x)
                        if line_x_min >= x_min - tol and line_x_max <= x_max + tol:
                            best_center = center
                            break
        
        elif is_vertical:
            # Vertical line at x = cx
            # Find cell where this line is on the RIGHT boundary (x_max)
            # This assigns shared boundaries to the LEFT cell
            for center in sorted_centers:
                bounds = cell_bounds[center]
                x_min, x_max, y_min, y_max = bounds
                # Check if line is on right boundary of this cell
                if abs(cx - x_max) < tol:
                    line_y_min = min(cy, end_y)
                    line_y_max = max(cy, end_y)
                    if line_y_min >= y_min - tol and line_y_max <= y_max + tol:
                        best_center = center
                        break
            # If not found (external boundary at left), check left boundaries
            if best_center is None:
                for center in sorted_centers:
                    bounds = cell_bounds[center]
                    x_min, x_max, y_min, y_max = bounds
                    if abs(cx - x_min) < tol:
                        line_y_min = min(cy, end_y)
                        line_y_max = max(cy, end_y)
                        if line_y_min >= y_min - tol and line_y_max <= y_max + tol:
                            best_center = center
                            break
        
        # Fallback: assign to nearest center
        if best_center is None:
            mid_x = (cx + end_x) / 2
            mid_y = (cy + end_y) / 2
            min_dist = float('inf')
            for center in sorted_centers:
                dist = math.sqrt((mid_x - center[0])**2 + (mid_y - center[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    best_center = center
        
        return best_center
    
    # Create mapping from center to line segments
    # For GEO MACRO format, we MUST use normalized coordinates (positive direction vectors)
    # This is required for SALT multicell surfacic tracking to work correctly
    center_to_lines = {center: [] for center in sorted_centers}
    for norm_line in normalized_lines:
        assigned_center = assign_line_to_cell(norm_line, sorted_centers, cell_bounds)
        # Create a new Element with normalized coordinates for GEO format
        # The GEO format requires lines to start from lower/left and go to upper/right
        orig = norm_line['orig']
        new_line = Element(
            elem_id=orig.elem_id,
            elem_type=1,
            node_minus=orig.node_minus,
            node_plus=orig.node_plus,
            cx=norm_line['cx'],
            cy=norm_line['cy'],
            ex_or_r=norm_line['dx'],
            ey_or_theta1=norm_line['dy'],
            theta2=orig.theta2,
            comment=orig.comment
        )
        center_to_lines[assigned_center].append(new_line)
    
    # Sort lines within each cell: horizontal (y-sorted) first, then vertical (x-sorted)
    # This matches the GEO MACRO ordering: bottom, top, left, right
    def line_sort_key(line):
        """Sort key for lines: horizontal lines first (by y), then vertical (by x)"""
        is_horizontal = abs(line.ey_or_theta1) < 1e-4
        is_vertical = abs(line.ex_or_r) < 1e-4
        if is_horizontal:
            return (0, line.cy)  # Horizontal: sort by y (bottom first)
        elif is_vertical:
            return (1, line.cx)  # Vertical: sort by x (left first)
        else:
            return (2, line.cx, line.cy)  # Other
    
    for center in sorted_centers:
        center_to_lines[center].sort(key=line_sort_key)
    
    # Create ordered list of elements
    ordered = []
    for center in sorted_centers:
        # Add boundary lines for this pin cell first
        lines = center_to_lines[center]
        ordered.extend(lines)
        
        # Add circles for this pin cell (from smallest to largest radius)
        circles = sorted(circle_centers[center], key=lambda e: e.ex_or_r)
        ordered.extend(circles)
    
    return ordered


def renumber_nodes_for_geo_variable(elements: List[Element], nx: int, ny: int, 
                                      circles_per_pin: Dict[Tuple[float, float], int]) -> List[Element]:
    """
    Renumber nodes for GEO MACRO format with variable circles per pin.
    
    With variable circles per pin, the node numbering scheme becomes more complex.
    Each row of pins shares a contiguous block of nodes.
    
    For a row, nodes are numbered:
    - Each pin in the row has (n_circles_i + 1) nodes: 1 central + n_circles for the circle chain
    - Within a row, pins are numbered left to right
    - The node numbering for each pin depends on the cumulative nodes of previous pins in the row
    
    Args:
        elements: Already-ordered list of elements from reorder_elements_for_geo
        nx: Number of pins in x direction  
        ny: Number of pins in y direction
        circles_per_pin: Dict mapping pin center to circle count
    """
    if not elements:
        return []
    
    # Build grid mapping
    sorted_centers = sorted(circles_per_pin.keys(), key=lambda c: (c[1], c[0]))
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    
    center_to_grid = {}
    for center in sorted_centers:
        col = x_coords.index(center[0])
        row = y_coords.index(center[1])
        center_to_grid[center] = (col, row)
    
    # Get circles per grid position
    def get_circles(col, row):
        center = (x_coords[col], y_coords[row])
        return circles_per_pin.get(center, 6)
    
    # Calculate the starting node for each macro and nodes per row
    # GEO MACRO format uses ROW-INTERLEAVED node numbering:
    # Within a row, pin nodes are interleaved: 
    #   Pin 0: 1, 3, 5, 7, 9, 11, 13  (odd)
    #   Pin 1: 2, 4, 6, 8, 10, 12, 14 (even)
    # Each row takes up: nx * (max_circles_in_row + 1) nodes
    
    def get_max_circles_in_row(row):
        """Get maximum circles for any pin in a row."""
        return max(get_circles(col, row) for col in range(nx))
    
    def get_nodes_in_row(row):
        """Get total nodes used by pins in a row (interleaved pattern)."""
        max_circ = get_max_circles_in_row(row)
        return nx * (max_circ + 1)
    
    def get_row_start_node(row):
        """Get the starting node number for a row."""
        start = 1
        for r in range(row):
            start += get_nodes_in_row(r)
        return start
    
    def get_central_node(col, row):
        """Get the central node for a pin at (col, row).
        
        In interleaved numbering:
        - Pin (0,0) has central node 1
        - Pin (1,0) has central node 2
        - Pin (col, row) has central node = row_start + col
        """
        row_start = get_row_start_node(row)
        return row_start + col
    
    def get_circle_node_sequence(col, row):
        """Get the circle node sequence for a pin at (col, row).
        
        In interleaved numbering, circle nodes use stride of nx:
        - Pin (0,0): 13, 11, 9, 7, 5, 3, 1  (stride 2 = nx * 1 for nx=2... wait)
        
        Actually looking at GEO reference:
        - Pin (0,0): nodes 13, 11, 9, 7, 5, 3, 1  - stride 2
        - Pin (1,0): nodes 14, 12, 10, 8, 6, 4, 2 - stride 2
        
        So each pin's circles use stride 2 (= nx), not within pin but across pins.
        For pin (col, row):
        - Central = row_start + col
        - Last circle node = central + n_circles * nx 
        - Nodes: last, last-nx, last-2*nx, ..., central
        
        Wait, that gives stride=nx=2:
        - Pin (0,0): central=1, nodes at 1+6*2=13, 11, 9, 7, 5, 3, 1 ✓
        - Pin (1,0): central=2, nodes at 2+6*2=14, 12, 10, 8, 6, 4, 2 ✓
        """
        central = get_central_node(col, row)
        n_circles = get_circles(col, row)
        # Last circle node is at central + n_circles * nx
        start_node = central + n_circles * nx
        # Stride is nx (interleaved with other pins in row)
        sequence = list(range(start_node, central - 1, -nx))
        return sequence
    
    # Compute pitch for boundary detection
    if len(x_coords) >= 2:
        pitch = x_coords[1] - x_coords[0]
    else:
        pitch = x_coords[0] * 2
    
    # Create cell bounds for line assignment
    cell_bounds = {}
    for center in sorted_centers:
        cx, cy = center
        half_pitch = pitch / 2
        cell_bounds[center] = (cx - half_pitch, cx + half_pitch, cy - half_pitch, cy + half_pitch)
    
    # Determine which macro each element belongs to
    def find_macro_for_element(elem):
        """Find which macro (col, row) an element belongs to."""
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            return center_to_grid.get(center, (0, 0))
        else:  # Line
            for center in sorted_centers:
                x_min, x_max, y_min, y_max = cell_bounds[center]
                
                is_horizontal = abs(elem.ey_or_theta1) < 1e-4
                is_vertical = abs(elem.ex_or_r) < 1e-4
                eps = 1e-4
                
                if is_horizontal:
                    if abs(elem.cy - y_max) < eps or abs(elem.cy - y_min) < eps:
                        line_mid_x = elem.cx + elem.ex_or_r / 2
                        if x_min - eps <= line_mid_x <= x_max + eps:
                            return center_to_grid[center]
                elif is_vertical:
                    if abs(elem.cx - x_max) < eps or abs(elem.cx - x_min) < eps:
                        line_mid_y = elem.cy + elem.ey_or_theta1 / 2
                        if y_min - eps <= line_mid_y <= y_max + eps:
                            return center_to_grid[center]
            return (0, 0)
    
    # Track circle count per macro
    macro_circle_count = {}
    
    new_elements = []
    for elem in elements:
        col, row = find_macro_for_element(elem)
        central = get_central_node(col, row)
        
        if elem.elem_type == 1:  # Line segment
            is_horizontal = abs(elem.ey_or_theta1) < 1e-4
            is_vertical = abs(elem.ex_or_r) < 1e-4
            eps = 1e-4
            
            # Get neighboring central nodes
            upper_central = get_central_node(col, row + 1) if row < ny - 1 else 0
            right_central = get_central_node(col + 1, row) if col < nx - 1 else 0
            
            # Calculate cell boundaries
            cell_x_min = col * pitch
            cell_x_max = (col + 1) * pitch
            cell_y_min = row * pitch
            cell_y_max = (row + 1) * pitch
            
            if is_horizontal:
                if abs(elem.cy - cell_y_min) < eps and row == 0:
                    node_minus, node_plus = 0, central
                elif abs(elem.cy - cell_y_max) < eps:
                    if row < ny - 1:
                        node_minus, node_plus = central, upper_central
                    else:
                        node_minus, node_plus = central, 0
                else:
                    node_minus, node_plus = 0, central
                    
            elif is_vertical:
                if abs(elem.cx - cell_x_min) < eps and col == 0:
                    node_minus, node_plus = central, 0
                elif abs(elem.cx - cell_x_max) < eps:
                    if col < nx - 1:
                        node_minus, node_plus = right_central, central
                    else:
                        node_minus, node_plus = 0, central
                else:
                    node_minus, node_plus = 0, central
            else:
                node_minus, node_plus = 0, central
            
            new_elem = Element(
                elem_id=len(new_elements) + 1,
                elem_type=1,
                node_minus=node_minus,
                node_plus=node_plus,
                cx=elem.cx,
                cy=elem.cy,
                ex_or_r=elem.ex_or_r,
                ey_or_theta1=elem.ey_or_theta1,
                theta2=elem.theta2,
                comment=elem.comment
            )
            new_elements.append(new_elem)
            
        else:  # Circle (elem_type == 2)
            macro_key = (col, row)
            if macro_key not in macro_circle_count:
                macro_circle_count[macro_key] = 0
            circle_idx = macro_circle_count[macro_key]
            macro_circle_count[macro_key] += 1
            
            node_seq = get_circle_node_sequence(col, row)
            
            if circle_idx < len(node_seq) - 1:
                node_minus = node_seq[circle_idx]
                node_plus = node_seq[circle_idx + 1]
            else:
                node_minus = node_seq[-2] if len(node_seq) >= 2 else central + 2
                node_plus = node_seq[-1] if node_seq else central
            
            new_elem = Element(
                elem_id=len(new_elements) + 1,
                elem_type=2,
                node_minus=node_minus,
                node_plus=node_plus,
                cx=elem.cx,
                cy=elem.cy,
                ex_or_r=elem.ex_or_r,
                ey_or_theta1=elem.ey_or_theta1,
                theta2=elem.theta2,
                comment=elem.comment
            )
            new_elements.append(new_elem)
    
    return new_elements


def renumber_nodes_for_geo_general(elements: List[Element], nx: int, ny: int, 
                                     n_circles: int) -> List[Element]:
    """
    Renumber nodes for GEO MACRO format (generalized for NxN grids).
    
    Elements are expected to be already ordered by reorder_elements_for_geo():
    - Macro 0: lines then circles, Macro 1: lines then circles, etc.
    
    The function traverses elements in order and assigns node numbers based
    on the geometric position of each element.
    
    Args:
        elements: Already-ordered list of elements from reorder_elements_for_geo
        nx: Number of pins in x direction
        ny: Number of pins in y direction
        n_circles: Number of circles per pin cell
    """
    if not elements:
        return []
    
    # Compute nodes per row: each row has nx pins, each with (n_circles + 1) nodes
    nodes_per_row = nx * (n_circles + 1)
    
    def get_central_node(col: int, row: int) -> int:
        """Get the central node number for a macro at (col, row)."""
        return row * nodes_per_row + col + 1
    
    def get_circle_node_sequence(col: int, row: int) -> List[int]:
        """
        Get the circle node sequence for a macro at (col, row).
        Returns nodes from outermost circle down to central node (n_circles+1 values).
        """
        central = get_central_node(col, row)
        # Circle nodes start at central + 2*n_circles and go down by 2
        start_node = central + 2 * n_circles
        sequence = list(range(start_node, central - 1, -2))
        return sequence
    
    # Build mapping from circle center to grid position
    circle_centers = {}
    for elem in elements:
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            if center not in circle_centers:
                circle_centers[center] = []
            circle_centers[center].append(elem)
    
    sorted_centers = sorted(circle_centers.keys(), key=lambda c: (c[1], c[0]))
    x_coords = sorted(set(c[0] for c in sorted_centers))
    y_coords = sorted(set(c[1] for c in sorted_centers))
    
    center_to_grid = {}
    for center in sorted_centers:
        col = x_coords.index(center[0])
        row = y_coords.index(center[1])
        center_to_grid[center] = (col, row)
    
    # Compute pitch for boundary detection
    if len(x_coords) >= 2:
        pitch = x_coords[1] - x_coords[0]
    else:
        pitch = x_coords[0] * 2
    
    # Create cell bounds for line assignment
    cell_bounds = {}
    for center in sorted_centers:
        cx, cy = center
        half_pitch = pitch / 2
        cell_bounds[center] = (cx - half_pitch, cx + half_pitch, cy - half_pitch, cy + half_pitch)
    
    # Determine which macro each element belongs to based on its geometric position
    def find_macro_for_element(elem):
        """Find which macro (col, row) an element belongs to."""
        if elem.elem_type == 2:  # Circle
            center = (round(elem.cx, 4), round(elem.cy, 4))
            return center_to_grid.get(center, (0, 0))
        else:  # Line
            # Find which cell this line is assigned to based on cell bounds
            for center in sorted_centers:
                x_min, x_max, y_min, y_max = cell_bounds[center]
                
                is_horizontal = abs(elem.ey_or_theta1) < 1e-4
                is_vertical = abs(elem.ex_or_r) < 1e-4
                eps = 1e-4
                
                if is_horizontal:
                    # Check if line is on top or bottom of this cell
                    if abs(elem.cy - y_max) < eps or abs(elem.cy - y_min) < eps:
                        line_mid_x = elem.cx + elem.ex_or_r / 2
                        if x_min - eps <= line_mid_x <= x_max + eps:
                            return center_to_grid[center]
                elif is_vertical:
                    # Check if line is on left or right of this cell
                    if abs(elem.cx - x_max) < eps or abs(elem.cx - x_min) < eps:
                        line_mid_y = elem.cy + elem.ey_or_theta1 / 2
                        if y_min - eps <= line_mid_y <= y_max + eps:
                            return center_to_grid[center]
            # Fallback: nearest center
            return (0, 0)
    
    # Track which circle we're on for each macro
    macro_circle_count = {}
    
    new_elements = []
    for elem in elements:
        col, row = find_macro_for_element(elem)
        central = get_central_node(col, row)
        
        if elem.elem_type == 1:  # Line segment
            # Determine line orientation and position
            is_horizontal = abs(elem.ey_or_theta1) < 1e-4
            is_vertical = abs(elem.ex_or_r) < 1e-4
            eps = 1e-4
            
            # Get neighboring central nodes
            upper_central = get_central_node(col, row + 1) if row < ny - 1 else 0
            right_central = get_central_node(col + 1, row) if col < nx - 1 else 0
            
            # Calculate cell boundaries for this macro
            cell_x_min = col * pitch
            cell_x_max = (col + 1) * pitch
            cell_y_min = row * pitch
            cell_y_max = (row + 1) * pitch
            
            if is_horizontal:
                # Horizontal line
                if abs(elem.cy - cell_y_min) < eps and row == 0:
                    # Bottom external boundary (y = 0)
                    node_minus, node_plus = 0, central
                elif abs(elem.cy - cell_y_max) < eps:
                    # Top boundary of this cell
                    if row < ny - 1:
                        # Internal boundary
                        node_minus, node_plus = central, upper_central
                    else:
                        # External top boundary
                        node_minus, node_plus = central, 0
                else:
                    # Fallback
                    node_minus, node_plus = 0, central
                    
            elif is_vertical:
                # Vertical line
                if abs(elem.cx - cell_x_min) < eps and col == 0:
                    # Left external boundary (x = 0)
                    node_minus, node_plus = central, 0
                elif abs(elem.cx - cell_x_max) < eps:
                    # Right boundary of this cell
                    if col < nx - 1:
                        # Internal boundary
                        node_minus, node_plus = right_central, central
                    else:
                        # External right boundary
                        node_minus, node_plus = 0, central
                else:
                    # Fallback
                    node_minus, node_plus = 0, central
            else:
                node_minus, node_plus = 0, central
            
            new_elem = Element(
                elem_id=len(new_elements) + 1,
                elem_type=1,
                node_minus=node_minus,
                node_plus=node_plus,
                cx=elem.cx,
                cy=elem.cy,
                ex_or_r=elem.ex_or_r,
                ey_or_theta1=elem.ey_or_theta1,
                theta2=elem.theta2,
                comment=elem.comment
            )
            new_elements.append(new_elem)
            
        else:  # Circle (elem_type == 2)
            # Get the circle count for this macro
            macro_key = (col, row)
            if macro_key not in macro_circle_count:
                macro_circle_count[macro_key] = 0
            circle_idx = macro_circle_count[macro_key]
            macro_circle_count[macro_key] += 1
            
            # Get node sequence for this macro
            node_seq = get_circle_node_sequence(col, row)
            
            # Assign nodes for this circle
            if circle_idx < len(node_seq) - 1:
                node_minus = node_seq[circle_idx]
                node_plus = node_seq[circle_idx + 1]
            else:
                # Last circle (fallback)
                node_minus = node_seq[-2] if len(node_seq) >= 2 else central + 2
                node_plus = node_seq[-1] if node_seq else central
            
            new_elem = Element(
                elem_id=len(new_elements) + 1,
                elem_type=2,
                node_minus=node_minus,
                node_plus=node_plus,
                cx=elem.cx,
                cy=elem.cy,
                ex_or_r=elem.ex_or_r,
                ey_or_theta1=elem.ey_or_theta1,
                theta2=elem.theta2,
                comment=elem.comment
            )
            new_elements.append(new_elem)
    
    return new_elements


# Keep old function for backward compatibility (deprecated)
def renumber_nodes_for_geo(elements: List[Element], num_macros: int = 4) -> List[Element]:
    """Deprecated: Use renumber_nodes_for_geo_general instead."""
    # Detect grid dimensions
    circle_count = sum(1 for e in elements if e.elem_type == 2)
    n_circles = 6  # Default assumption
    nx = ny = int(num_macros ** 0.5)
    if nx * ny != num_macros:
        nx, ny = num_macros, 1  # Fall back to 1D
    return renumber_nodes_for_geo_general(elements, nx, ny, n_circles)


def compute_boundary_conditions_reordered(elements: List[Element]) -> List[Tuple[List[int], float]]:
    """Compute boundary conditions for reordered elements."""
    max_x = 0.0
    max_y = 0.0
    
    for elem in elements:
        if elem.elem_type == 1:
            # Calculate end points of line segment
            end_x = elem.cx + elem.ex_or_r
            end_y = elem.cy + elem.ey_or_theta1
            max_x = max(max_x, elem.cx, end_x)
            max_y = max(max_y, elem.cy, end_y)
    
    eps = 1e-4
    boundaries = [[], [], [], []]  # bottom, left, right, top
    
    for i, elem in enumerate(elements):
        if elem.elem_type == 1:
            # Calculate end points
            x1, y1 = elem.cx, elem.cy
            x2, y2 = elem.cx + elem.ex_or_r, elem.cy + elem.ey_or_theta1
            
            # Determine if this is a horizontal or vertical line
            is_horizontal = abs(y2 - y1) < eps
            is_vertical = abs(x2 - x1) < eps
            
            # Check which boundary the line is on
            # Bottom boundary: both y coords near 0
            if is_horizontal and abs(y1) < eps and abs(y2) < eps:
                boundaries[0].append(i + 1)
            # Left boundary: both x coords near 0
            elif is_vertical and abs(x1) < eps and abs(x2) < eps:
                boundaries[1].append(i + 1)
            # Right boundary: both x coords near max_x
            elif is_vertical and abs(x1 - max_x) < eps and abs(x2 - max_x) < eps:
                boundaries[2].append(i + 1)
            # Top boundary: both y coords near max_y
            elif is_horizontal and abs(y1 - max_y) < eps and abs(y2 - max_y) < eps:
                boundaries[3].append(i + 1)
    
    result = []
    for boundary in boundaries:
        if boundary:
            result.append((sorted(boundary), 1.0))
    
    return result


def reorder_medium_for_geo(medium: List[int], merge: List[int]) -> List[int]:
    """Reorder medium array according to merge mapping."""
    if not medium:
        return []
    
    # Create inverse mapping: flux_region -> medium
    region_to_medium = {i+1: m for i, m in enumerate(medium)}
    
    # Reorder according to merge array
    reordered = []
    for flux_region in merge:
        if flux_region in region_to_medium:
            reordered.append(region_to_medium[flux_region])
    
    return reordered


def convert_glow_to_geo_macro(input_path: Path, output_path: Path, num_macros: int = 4):
    """
    Main conversion function.
    
    Args:
        input_path: Path to GLOW-format TDT file
        output_path: Path for output GEO MACRO format file
        num_macros: Number of MACROs (0 = auto-detect from geometry)
    """
    print(f"Reading GLOW TDT file: {input_path}")
    data = parse_glow_tdt_file(input_path)
    
    print(f"Found {data.nbelem} elements, {data.nreg} regions")
    
    # Auto-detect grid dimensions
    nx, ny, circles_per_pin = detect_grid_dimensions(data.elements)
    detected_macros = nx * ny
    
    if num_macros == 0:
        num_macros = detected_macros
    
    # Summarize circles per pin
    circle_counts = list(circles_per_pin.values())
    min_c, max_c = min(circle_counts), max(circle_counts)
    if min_c == max_c:
        circles_summary = f"{min_c}"
    else:
        circles_summary = f"{min_c}-{max_c} (variable)"
    
    print(f"Creating {num_macros} MACROs ({nx}x{ny} grid, {circles_summary} circles/pin)...")
    
    write_geo_macro_file(data, output_path, num_macros)
    print(f"Wrote GEO MACRO file: {output_path}")


# Main execution
if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) >= 3:
        input_file = Path(sys.argv[1])
        output_file = Path(sys.argv[2])
        num_macros = int(sys.argv[3]) if len(sys.argv) > 3 else 0  # 0 = auto-detect
    else:
        # Configure test case
        case_name = "AT10_lattice_MODEBOX_TISO"
        path_to_glow_tdt_data = Path("../../tdt_data/")
        input_file = path_to_glow_tdt_data / f"{case_name}.dat"
        output_file = Path("converted_tdt_data") / f"{case_name}_MACRO_converted.dat"
        num_macros = 0  # Auto-detect
    
    # Create output directory if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Run conversion
    convert_glow_to_geo_macro(input_file, output_file, num_macros=num_macros)
