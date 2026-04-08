# AT10 controlled assembly geometry export to Serpent2.
#
# Generates a Serpent2 input file for the ATRIUM-10 assembly WITH
# control cross (cruciform control blade).  This extends the
# uncontrolled export (AT10_assembly_serpent2_export.py) by adding
# control-cross geometry (surfaces, lattices, cells) and materials
# (B4C absorber rods + SS304 sheath structure).
#
# R.Guasch
# ---------------------------------------------------------------------------
import os
from starterDD.DDModel.helpers import associate_material_to_rod_ID
from starterDD.MaterialProperties.material_mixture import parse_all_compositions_from_yaml
from starterDD.DDModel import CartesianAssemblyModel
from starterDD.InterfaceToDD.serpent2_cards import (
    Serpent2Model,
    S2_Settings,
    S2_EnergyGrid,
)

# =====================================================================
# Configuration paths
# =====================================================================
assembly_id = "AT10_NOM-C"
path_to_yaml_compositions = f"input_configs/{assembly_id}/material_compositions.yaml"
path_to_yaml_geometry     = f"input_configs/{assembly_id}/GEOM.yaml"
nuclear_data_library = "endfb8r1"

path_to_output = f"serpent2_outputs/{assembly_id}"
if os.path.exists(path_to_output):
    print(f"Output directory already exists: {path_to_output}")
else:
    os.makedirs(path_to_output)
    print(f"Created output directory: {path_to_output}")

# =====================================================================
# 1. Load material compositions and rod-ID → material mapping
# =====================================================================
compositions = parse_all_compositions_from_yaml(path_to_yaml_compositions)
ROD_to_material = associate_material_to_rod_ID(
    path_to_yaml_compositions, path_to_yaml_geometry
)

# =====================================================================
# 2. Build the CartesianAssemblyModel (with control cross from YAML)
# =====================================================================
AT10_assembly = CartesianAssemblyModel(
    name="AT10_assembly_CTRL_serpent2",
    tdt_file="dummy.tdt",
    geometry_description_yaml=path_to_yaml_geometry,
)
AT10_assembly.set_rod_ID_to_material_mapping(ROD_to_material)
AT10_assembly.set_uniform_temperatures(
    fuel_temperature=750.0,
    gap_temperature=750.0,
    coolant_temperature=559.0,
    moderator_temperature=559.0,
    structural_temperature=559.0,
)
AT10_assembly.analyze_lattice_description(build_pins=True, apply_self_shielding="from_yaml")
AT10_assembly.set_material_compositions(compositions)
AT10_assembly.number_fuel_material_mixtures_by_pin()
AT10_assembly.identify_generating_and_daughter_mixes()

# Verify control cross was loaded
assert AT10_assembly.has_control_cross, (
    "GEOM_ATRIUM10_CTRL.yaml must contain CONTROL_CROSS_GEOMETRY section."
)
print(f"Control cross loaded: {AT10_assembly.control_cross}")

# =====================================================================
# 3. Configure Serpent2 settings
# =====================================================================
settings = S2_Settings()
settings.title = "ATRIUM-10 BWR assembly CTRL - Serpent2 export from starterDD"
settings.bc = 2  # Reflective boundary conditions
settings.neutrons_per_cycle = 2000000
settings.active_cycles = 5000
settings.inactive_cycles = 100
settings.ures = True

settings.set_nuclear_data_evaluation(nuclear_data_library)
settings.add_plot(plot_type=3, x_pixels=1500, y_pixels=1500)

# =====================================================================
# 4. Build the Serpent2Model (WITH control cross)
# =====================================================================
print("Building Serpent2 model with control cross...")
model = Serpent2Model(assembly_model=AT10_assembly, settings=settings)

# Build geometry: pins, lattice, channel box + control cross.
# The build() method auto-detects has_control_cross and creates
# the S2_ControlCrossGeometry, integrating it into the channel
# geometry (complement operators in the moderator gap cell).
model.build(
    gap_material_name="gap",
    clad_material_name="clad",
    coolant_material_name="coolant",
    outer_water_material_name="moderator",
    channel_box_material_name="zr4",
    lattice_name="10",
    empty_universe_name="empty",
    # Control cross material names matching YAML composition names
    ctrl_absorber_material_name="ctrl_rod",
    ctrl_sheath_material_name="ctrl_cross",
)

# Add structural (non-fuel) materials from the assembly composition lookup.
# This auto-discovers COOLANT, CLAD, GAP, MODERATOR, CHANNEL_BOX, and also
# CTRL_ROD and CTRL_CROSS from the control YAML file.
model.build_structural_materials_from_assembly(
    name_map={
        "COOLANT": "coolant",
        "CLAD": "clad",
        "GAP": "gap",
        "MODERATOR": "moderator",
        "CHANNEL_BOX": "zr4",
        "CTRL_ROD": "ctrl_rod",
        "CTRL_CROSS": "ctrl_cross",
    },
    temperature_map={
        "COOLANT": 559.0,
        "CLAD": 559.0,
        "GAP": 750.0,
        "MODERATOR": 559.0,
        "CHANNEL_BOX": 559.0,
        "CTRL_ROD": 559.0,
        "CTRL_CROSS": 559.0,
    },
)

# =====================================================================
# 5. Add detectors for fission and absorption reactions
# =====================================================================
print("Adding detectors for reaction rates...")

if nuclear_data_library == "endfb8r1":
    reaction_isotope_map = {
        'disappearance': ['U235', 'U238', 'Gd155', 'Gd157'],
        'fission': ['U235', 'U238'],
        'n,gamma': ['U235', 'U238', 'Gd155', 'Gd157'],
        'n,proton': ['U238'],
        'n,alpha': ['U235', 'U238'],
        'n,2n': ['U235', 'U238'],
        'n,3n': ['U235', 'U238'],
    }
elif nuclear_data_library == "jeff311":
    reaction_isotope_map = {
        'disappearance': ['U235', 'U238', 'Gd155', 'Gd157'],
        'fission': ['U235', 'U238'],
        'n,gamma': ['U235', 'U238', 'Gd155', 'Gd157'],
        'n,2n': ['U235', 'U238'],
        'n,3n': ['U235', 'U238'],
        'n,4n': ['U235', 'U238'],
    }

model.add_detector_config(
    reaction_isotope_map=reaction_isotope_map,
    energy_grid_name="2g",
    fuel_temperature=750.0,
    detector_type=-4,
)

# Assembly-integrated 295g detector for U238
if nuclear_data_library == "endfb8r1":
    reaction_isotope_map_295g_U238 = {
        'disappearance': ['U238'],
        'fission': ['U238'],
        'n,gamma': ['U238'],
        'n,alpha': ['U238'],
        'n,2n': ['U238'],
        'n,3n': ['U238'],
    }
elif nuclear_data_library == "jeff311":
    reaction_isotope_map_295g_U238 = {
        'disappearance': ['U238'],
        'fission': ['U238'],
        'n,gamma': ['U238'],
        'n,2n': ['U238'],
        'n,3n': ['U238'],
        'n,4n': ['U238'],
    }

model.add_assembly_integrated_detector_config(
    reaction_isotope_map=reaction_isotope_map_295g_U238,
    energy_grid_name="295g",
    fuel_temperature=750.0,
    detector_type=-4,
)
model.add_assembly_integrated_detector_config(
    reaction_isotope_map=reaction_isotope_map_295g_U238,
    energy_grid_name="26g",  # Fine energy mesh for U238 rates
    fuel_temperature=900.0,
    detector_type=-4,  # dt -4: sum over dm materials (all fuel zones, all pins)
)

# Global flux detectors
model.add_flux_detector(energy_grid_name="295g", name="flux_295g")
model.add_flux_detector(energy_grid_name="26g", name="flux_26g")
model.add_flux_detector(energy_grid_name="2g", name="flux_2g")

# =====================================================================
# 6. Print summary and write output
# =====================================================================
print(model.summary())

output_filepath = f"{path_to_output}/{assembly_id}_assembly_{nuclear_data_library}.serp"
model.write(output_filepath)

print(f"\nSerpent2 model exported to: {output_filepath}")
print(f"  - Total materials: {len(model.materials)}")
print(f"  - Pin universes: {len(model.pin_universes)}")
print(f"  - Detectors: {len(model.detectors)}")
print(f"  - Isotope response materials: {len(model.isotope_response_materials)}")
print(f"  - Control cross: {AT10_assembly.control_cross}")

# =====================================================================
# 7. Summary
# =====================================================================
print("\n" + "=" * 60)
print("  CONTROLLED ASSEMBLY EXPORT SUMMARY")
print("=" * 60)
print(f"  Control cross center : {AT10_assembly.control_cross.center}")
print(f"  Tubes per wing       : {AT10_assembly.control_cross.number_tubes_per_wing}")
print(f"  Blade half-span      : {AT10_assembly.control_cross.blade_half_span}")
print(f"  Blade thickness      : {AT10_assembly.control_cross.blade_thickness}")
print(f"  Absorber material    : {AT10_assembly.control_cross.absorber_material}")
print(f"  Sheath material      : {AT10_assembly.control_cross.sheath_material}")
print("=" * 60)
