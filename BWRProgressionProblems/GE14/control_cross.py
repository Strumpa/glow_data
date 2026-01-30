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


lattice.add_cell(assembly_box_cell, ())

#lattice.lattice_box = assembly_box_cell
# Show the lattice
lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MATERIAL)

# --------------------  
# GENERATE TDT FILE
# --------------------
lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice],
    f"data/glow_data/tdt_data/GE14_control_cross",
    TdtSetup(
        GeometryType.SECTORIZED,
        property_types=[PropertyType.MATERIAL],
        type_geo=LatticeGeometryType.ISOTROPIC,
        symmetry_type=BoundaryType.AXIAL_SYMMETRY
    )
)