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
    water_rod_cell2 = RectCell(
        name="WATER_ROD_2",
        height_x_width=(2 * pin_pitch, 2 * pin_pitch),
        center=(0.0, 0.0, 0.0)
    )
    water_rod_cell2.add_circle(water_rod_inner_radius)
    water_rod_cell2.add_circle(water_rod_outer_radius)
    water_rod_cell2.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
    })

    water_rod_cell2_face = make_partition(
        [water_rod_cell2.face],
        [face1.face, face2.face, face3.face, face4.face],
        shape_type=ShapeType.COMPOUND
    )
    water_rod_cell2.update_geometry_from_face(GeometryType.TECHNOLOGICAL, water_rod_cell2_face)
    water_rod_cell2.set_properties({
        PropertyType.MATERIAL: ["MODERATOR", "MODERATOR", "MODERATOR", "MODERATOR",
                                 "CLAD", "CLAD", "CLAD", "CLAD",
                                 "COOLANT", "COOLANT", "COOLANT", "COOLANT"],
        #
        PropertyType.MACRO: ["WATER_ROD_2_MACRO_1", "WATER_ROD_2_MACRO_2", "WATER_ROD_2_MACRO_3", "WATER_ROD_2_MACRO_4", 
                             "WATER_ROD_2_MACRO_1", "WATER_ROD_2_MACRO_2", "WATER_ROD_2_MACRO_3", "WATER_ROD_2_MACRO_4", 
                             "WATER_ROD_2_MACRO_4", "WATER_ROD_2_MACRO_2", "WATER_ROD_2_MACRO_3", "WATER_ROD_2_MACRO_1"]
    })

    return water_rod_1_macros, water_rod_cell2


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
# GENERATE WATER RODS
# --------------------

water_rod_1_macros, water_rod_2_macros = create_water_rods(
    pin_pitch,
    water_rod_inner_radius,
    water_rod_outer_radius
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
    PropertyType.MACRO: ["MACRO_INTRA_ASSEMBLY_COOLANT", "MACRO_CHANNEL_BOX", "MACRO_ASSEMBLY_MODERATOR"]
})

# --------------------
# LATTICE CONSTRUCTION
# --------------------
lattice = Lattice(name='GE14_full_assembly', center=center)


# Add water rod cells at their specific locations
lattice.add_cell(water_rod_1_macros,
                (4 * pin_pitch + pincell_translation, 4 * pin_pitch + pincell_translation, 0.0)
                )
lattice.add_cell(water_rod_2_macros,
                (6 * pin_pitch + pincell_translation, 6 * pin_pitch + pincell_translation, 0.0)
                )

lattice.lattice_box = assembly_box_cell
# Show the lattice
lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MACRO)

# --------------------  
# GENERATE TDT FILE
# --------------------
lattice.type_geo = LatticeGeometryType.ISOTROPIC
analyse_and_generate_tdt(
    [lattice],
    f"data/glow_data/tdt_data/GE14_full_assembly_rounded_corners",
    TdtSetup(
        GeometryType.SECTORIZED,
        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
        type_geo=LatticeGeometryType.ISOTROPIC,
        symmetry_type=BoundaryType.AXIAL_SYMMETRY
    )
)