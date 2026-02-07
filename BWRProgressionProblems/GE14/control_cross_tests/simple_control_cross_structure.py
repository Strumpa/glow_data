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
        Rectangle(height=(lattice_pitch), width=(lattice_pitch), center=(assembly_pitch/2, assembly_pitch/2, 0.0)),  # Middle-middle
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
        (2,2),  # Middle-middle : covering the pin lattice region
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
    list_of_materials = ["COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT","COOLANT",] \
        + ["CHANNEL_BOX", "CHANNEL_BOX", "CHANNEL_BOX", "CHANNEL_BOX"]*2 \
        + ["MODERATOR"]*8 + [sheath_material]*2 + ["MODERATOR"]*4 + ["CHANNEL_BOX"]*4 + [sheath_material]*2 + ["CHANNEL_BOX"]*4 + ["MODERATOR"]*4 \
        + [sheath_material]
        #+ ["MACRO90", "MACRO00", "MACRO99", "MACRO09",] \ instead of base cell
    list_of_macros = ["BCELL1", "BCELL2","BCELL3","BCELL4",] + ["LSIDE0", "LSIDE1", "BSIDE0", "BSIDE1", "TSIDE0",  "TSIDE1", "RSIDE0","RSIDE1"]  \
        + ["LSIDE1", "LSIDE0","TSIDE0","BSIDE0","TSIDE1","BSIDE1","RSIDE1","RSIDE0"] \
        + ["TSIDE0","RSIDE0", "RSIDE1", "TSIDE1","LSIDE0","LSIDE1","BSIDE0","BSIDE1",] \
        + ["WCROSS", "NCROSS","WCROSS", "NCROSS", "UWEST", "RNORTH"] + ["BCELL2", "BCELL1","BCELL4","BCELL3",]  \
        + ["WCROSS", "NCROSS","NEAST","NWEST","SWEST","SEAST","NWEST","SEAST","SWEST","NEAST",] \
        + ["NWCORNER"]    
    print(len(list_of_macros))
    print(len(list_of_materials))
    print(f"Material at postition len(list_of_materials)-1: {list_of_materials[-1]}")

    # set properties for the new MACRO regions
    assembly_box_cell.set_properties({
        PropertyType.MATERIAL: list_of_materials,# + ["mat0"] + ["mat"] * (45 - len(list_of_materials)),
        PropertyType.MACRO: list_of_macros #+  ["macro0"] + ["macro1"] * (45 - len(list_of_macros))
    })
    
    # return the updated assembly box cell
    return assembly_box_cell
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
    #rounded_corners=[(1, tip_radius)]
    )
ctrl_cross_sheath_cells.append(control_cross_right_wing_cell)

# control cross bottom wing
control_cross_bottom_wing_cell = Rectangle(
    name="CONTROL_CROSS_BOTTOM_WING_HALF",
    height=blade_half_span - central_structure_half_span,
    width=blade_thickness,
    center=(0.0,
            assembly_pitch - (blade_half_span - central_structure_half_span)/2 - central_structure_half_span, 
            0.0),
    #rounded_corners=[(1, tip_radius)]
    )
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
    #rounded_corners=[(1, tip_radius-sheath_thickness)]
    )
ctrl_cross_sheath_cells.append(inner_right_wing_cell)

inner_bottom_wing_cell = Rectangle(
    name="CONTROL_CROSS_BOTTOM_WING_INNER",
    height=blade_half_span - central_structure_half_span - sheath_thickness,
    width=inner_sheath_width,
    center=(0.0,
            assembly_pitch - (blade_half_span - central_structure_half_span - sheath_thickness)/2 - central_structure_half_span, 
            0.0),
    #rounded_corners=[(1, tip_radius-sheath_thickness)]
    )
ctrl_cross_sheath_cells.append(inner_bottom_wing_cell)

### Build geometry for control cross structure without absorber tubes and no rounded corners first : check tracking possibility for TISO option.
assembly_box_cell_face = make_partition(
    [assembly_box_cell.face],
    [channel_box_cell.face, coolant_intra_assembly_cell.face] + [structure.face for structure in ctrl_cross_sheath_cells],
    shape_type=ShapeType.COMPOUND
)

assembly_box_cell.update_geometry_from_face(GeometryType.TECHNOLOGICAL, assembly_box_cell_face)

list_of_materials =  ["MAT1"]*10     
print(list_of_materials)
assembly_box_cell.set_properties({
    PropertyType.MATERIAL: list_of_materials
})

# --------------------
# LATTICE CONSTRUCTION
# --------------------
lattice = Lattice(name='GE14_simple_ctrl_structure', center=center)

# Add the box cell FIRST - this establishes the base/background for the lattice
# Using () as position means it's the base cell

assembly_box_cell = split_box_in_MACROs_for_IC(
    assembly_box_cell,
    pincell_pitch=pin_pitch,
    assembly_pitch=assembly_pitch,
    control_cross_thickness=blade_thickness,
    control_cross_half_span=blade_half_span
)

lattice.add_cell(assembly_box_cell, ())

#lattice.lattice_box = assembly_box_cell
# Show the lattice
#lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)
lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MACRO)
# --------------------  
# GENERATE TDT FILE
# --------------------
lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice],
    f"data/glow_data/tdt_data/GE14_simple_control_cross_struct",
    TdtSetup(
        GeometryType.SECTORIZED,
        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
        type_geo=LatticeGeometryType.ISOTROPIC,
        symmetry_type=BoundaryType.AXIAL_SYMMETRY
    )
)