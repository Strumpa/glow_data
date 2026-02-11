from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *
from starterDD.starterDD.DDModel.helpers import associate_material_to_rod_ID
from starterDD.starterDD.MaterialProperties.material_mixture import parse_all_compositions_from_yaml
from starterDD.starterDD.GeometryBuilder.glow_builder import generate_fuel_cells, add_cells_to_regular_lattice, export_glow_geom, make_grid_faces
from starterDD.starterDD.DDModel import CartesianAssemblyModel

# --------------------
# HELPER FUNCTIONS
# --------------------


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
export_macro = True  # Whether to export MACRO definitions in the TDT file
path_to_tdt = "data/glow_data/tdt_data"
file_to_save_name = f"GE14_simplified_satamarina"

## import model : 
path_to_yaml_compositions = "glow_data/BWRProgressionProblems/GE14/input_configs/material_compositions.yaml"
path_to_yaml_geometry = "glow_data/BWRProgressionProblems/GE14/input_configs/simplified_geometry_santamarina.yaml"
compositions = parse_all_compositions_from_yaml(path_to_yaml_compositions)
ROD_to_material = associate_material_to_rod_ID(path_to_yaml_compositions,
                                               path_to_yaml_geometry)
# Create the assembly model with the given tdt file and lattice description.
GE14_simple_assembly = CartesianAssemblyModel(name="GE14_simple_assembly",
                                    tdt_file=path_to_tdt + "/" + file_to_save_name + ".tdt",
                                    geometry_description_yaml=path_to_yaml_geometry)
# Set the rod ID to material mapping in the assembly model
GE14_simple_assembly.set_rod_ID_to_material_mapping(ROD_to_material)
# Set uniform temperatures for all materials in the assembly model
GE14_simple_assembly.set_uniform_temperatures(fuel_temperature=900.0, gap_temperature=600.0, coolant_temperature=600.0, moderator_temperature=600.0, structural_temperature=600.0)
# Analyze the lattice description to build the lattice structure in the assembly model
GE14_simple_assembly.analyze_lattice_description(build_pins=True)
# Set the material compositions in the assembly model
GE14_simple_assembly.set_material_compositions(compositions)
# Number fuel material mixtures based on material names
GE14_simple_assembly.number_fuel_material_mixtures_by_material()
# --------------------
# GEOMETRY PARAMETERS
# --------------------

# Recover Main geometrical dimensions
assembly_pitch = GE14_simple_assembly.assembly_pitch  # cm
pin_pitch = GE14_simple_assembly.pin_geometry_dict["pin_pitch"]  # cm
gap_wide = GE14_simple_assembly.gap_wide  # cm
channel_box_thickness = GE14_simple_assembly.channel_box_thickness  # cm
fuel_pellet_radius = GE14_simple_assembly.pin_geometry_dict["fuel_radius"]  # cm
fuel_clad_inner_radius = GE14_simple_assembly.pin_geometry_dict["gap_radius"]  # cm
fuel_clad_outer_radius = GE14_simple_assembly.pin_geometry_dict["clad_radius"]  # cm
water_rod_inner_radius = 1.170  # cm
water_rod_outer_radius = 1.245  # cm


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
# LATTICE DESCRIPTION (simplified 10x10 GE-14)
# --------------------
#lattice_description = GE14_simple_assembly.lattice_description


# --------------------
# GENERATE FUEL CELLS
# --------------------
ordered_fuel_cells = generate_fuel_cells(
    assemblyModel=GE14_simple_assembly,
)


# Create water rod cells
water_rod_cell1, water_rod_cell2 = create_water_rods(
    pin_pitch, water_rod_inner_radius, water_rod_outer_radius, windmill=False
)
#water_rod_cell1, water_rod_cell2 = create_water_rods_i(
#    pin_pitch, water_rod_inner_radius, water_rod_outer_radius, windmill=False
#)

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

## split the box into MACROs for IC method compatibility
assembly_box_cell = split_box_in_MACROs_for_IC(assembly_box_cell, pin_pitch, assembly_pitch)

lattice.lattice_box = assembly_box_cell

# Show the lattice
lattice.show(geometry_type_to_show=GeometryType.SECTORIZED, property_type_to_show=PropertyType.MACRO)

# --------------------  
# GENERATE TDT FILE
# --------------------
export_glow_geom(path_to_tdt, file_to_save_name, lattice, tracking_type, export_macro=export_macro)