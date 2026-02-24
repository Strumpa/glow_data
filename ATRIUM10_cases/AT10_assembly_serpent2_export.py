# AT10 assembly geometry export to Serpent2.
#
# Generates a Serpent2 input file equivalent to the Dragon model
# with detectors for MT=18 (fission) and MT=27 (absorption) for each pin.
#
# Uses dt -4 to sum reaction rates over all material zones of each pin,
# matching the _by_pin numbering convention from Dragon.
#
# R.Guasch — 24/02/2026
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
path_to_yaml_compositions = "input_configs/material_compositions.yaml"
path_to_yaml_geometry     = "input_configs/GEOM_ATRIUM10.yaml"

path_to_output = "serpent2_outputs"  # Directory to save the Serpent2 input file
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
# 2. Build the CartesianAssemblyModel
# =====================================================================
AT10_assembly = CartesianAssemblyModel(
    name="AT10_assembly_serpent2",
    tdt_file="dummy.tdt",  # Not used for Serpent2 export
    geometry_description_yaml=path_to_yaml_geometry,
)
AT10_assembly.set_rod_ID_to_material_mapping(ROD_to_material)
AT10_assembly.set_uniform_temperatures(
    fuel_temperature=900.0,
    gap_temperature=600.0,
    coolant_temperature=600.0,
    moderator_temperature=600.0,
    structural_temperature=600.0,
)
# Build pins with self-shielding radii from YAML (Santamarina prescription)
AT10_assembly.analyze_lattice_description(build_pins=True, apply_self_shielding="from_yaml")
AT10_assembly.set_material_compositions(compositions)

# Number fuel material mixtures by pin (creates unique names like UOX24_zone1_pin3)
AT10_assembly.number_fuel_material_mixtures_by_pin()
AT10_assembly.identify_generating_and_daughter_mixes()

# =====================================================================
# 3. Configure Serpent2 settings
# =====================================================================
settings = S2_Settings()
settings.title = "ATRIUM-10 BWR assembly - Serpent2 export from starterDD"
settings.bc = 2  # Reflective boundary conditions
settings.neutrons_per_cycle = 50000
settings.active_cycles = 500
settings.inactive_cycles = 100
settings.ures = True  # Unresolved resonance probability tables

# Optional: set up library paths (uncomment and adjust as needed)
# settings.set_endfb8r1_libraries("/path/to/nuclear_data")
# settings.set_jeff311_libraries("/path/to/nuclear_data")

# Add geometry plot
settings.add_plot(plot_type=3, x_pixels=2000, y_pixels=2000, position=0.5)

# =====================================================================
# 4. Build the Serpent2Model
# =====================================================================
print("Building Serpent2 model...")
model = Serpent2Model(assembly_model=AT10_assembly, settings=settings)

# Build geometry: pins, lattice, channel box
model.build(
    gap_material_name="gap",
    clad_material_name="clad",
    coolant_material_name="cool",
    outer_water_material_name="cool_outer",
    channel_box_material_name="zr4",
    lattice_name="10",
    empty_universe_name="empty",
)

# Add structural (non-fuel) materials from the assembly composition lookup
model.build_structural_materials_from_assembly(
    name_map={
        "COOLANT": "cool",
        "CLAD": "clad",
        "GAP": "gap",
        "MODERATOR": "moderator",
        "CHANNEL_BOX": "zr4",
    },
    temperature_map={
        "COOLANT": 600.0,
        "CLAD": 600.0,
        "GAP": 600.0,
        "MODERATOR": 600.0,
        "CHANNEL_BOX": 600.0,
    },
)

# =====================================================================
# 5. Add detectors for fission and absorption reactions
# =====================================================================
print("Adding detectors for reaction rates...")

# Define reaction-to-isotope mapping:
# - Fission (MT=18): Only actinides with fission data
# - Absorption (MT=27): All isotopes of interest (actinides + Gd poisons)
#
# This ensures each isotope is only scored for reactions where it has data.
reaction_isotope_map = {
    'Fission': ['U234', 'U235', 'U236', 'U238'],  # Actinides with fission XS
    'absorption': ['U234', 'U235', 'U236', 'U238', 'Gd155', 'Gd157'],  # All tracked
}

# Add detector configuration:
# - Creates energy grid (2g energy grid with cutoff at 0.625 eV)
# - Creates single-isotope response materials for each unique isotope
# - Creates one detector per unique fuel pin
# - Uses dm cards for FUEL MATERIALS ONLY (excludes gap, clad, coolant)
# - Uses dt -4 to sum scores over all fuel material zones within each pin
#   This matches the Dragon _by_pin numbering convention where all radial
#   zones of a pin are grouped together for reaction rate tallying.
model.add_detector_config(
    reaction_isotope_map=reaction_isotope_map,
    energy_bounds=[0.625],  # Default: full energy range (single bin)
    energy_grid_name="2g",  # Use 2g energy grid for condensed reaction rates
    fuel_temperature=900.0,
    detector_type=-4,  # dt -4: sum over dm materials (all fuel zones of a pin)
)

# Optionally add a global flux detector
model.add_flux_detector(energy_grid_name="2g", name="flux_2g")

# =====================================================================
# 6. Print summary and write output
# =====================================================================
print(model.summary())

output_filepath = f"{path_to_output}/AT10_assembly_serpent2.serp"
model.write(output_filepath)

print(f"\nSerpent2 model exported to: {output_filepath}")
print(f"  - Total materials: {len(model.materials)}")
print(f"  - Pin universes: {len(model.pin_universes)}")
print(f"  - Detectors: {len(model.detectors)}")
print(f"  - Isotope response materials: {len(model.isotope_response_materials)}")

# =====================================================================
# 7. Summary of detector configuration
# =====================================================================
print("\n" + "=" * 60)
print("  DETECTOR SUMMARY")
print("=" * 60)
print("  Reaction-isotope mapping:")
for reaction, isotopes in reaction_isotope_map.items():
    print(f"    - {reaction}: {', '.join(isotopes)}")
print(f"  Domain: dm cards for FUEL MATERIALS ONLY per pin")
print(f"  Detector type: dt -4 (sum over fuel zones per pin)")
print(f"  Energy grid: full range (integrated over all energies)")
print(f"  Total detectors: {len(model.detectors)}")
print("=" * 60)
