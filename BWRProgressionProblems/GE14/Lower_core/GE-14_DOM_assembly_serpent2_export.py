# GE14 assembly geometry export to Serpent2.
#
# Generates a Serpent2 input file equivalent to the Dragon model
# with detectors for MT=18 (fission) and MT=27 (absorption) for each pin.
#
# Uses dt -4 to sum reaction rates over all material zones of each pin,
# matching the _by_pin numbering convention from Dragon.
#
# R.Guasch — 25/02/2026
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
assembly_id = "GE14_DOM"
path_to_yaml_compositions = "../input_configs/material_compositions.yaml"
path_to_yaml_geometry     = f"../input_configs/{assembly_id}/GEOM.yaml"
path_to_yaml_calc_scheme  = f"../input_configs/{assembly_id}/CALC_SCHEME.yaml"
nuclear_data_library = "endfb8r1"  # Specify the nuclear data library to use (e.g., "endfb8r1", "jeff311", etc.)

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
GE14_assembly = CartesianAssemblyModel(
    name="GE14_DOM_assembly_serpent2",
    tdt_file="dummy.tdt",  # Not used for Serpent2 export
    geometry_description_yaml=path_to_yaml_geometry,
)
GE14_assembly.set_rod_ID_to_material_mapping(ROD_to_material)
GE14_assembly.set_uniform_temperatures(
    fuel_temperature=900.0,
    gap_temperature=600.0,
    coolant_temperature=600.0,
    moderator_temperature=600.0,
    structural_temperature=600.0,
)
# Build pins with self-shielding radii from YAML (Santamarina prescription)
GE14_assembly.analyze_lattice_description(build_pins=True, apply_self_shielding="from_yaml")
GE14_assembly.set_material_compositions(compositions)

# Number fuel material mixtures by pin (creates unique names like UOX24_zone1_pin3)
GE14_assembly.number_fuel_material_mixtures_by_pin()
GE14_assembly.identify_generating_and_daughter_mixes()

# =====================================================================
# 3. Configure Serpent2 settings
# =====================================================================
settings = S2_Settings()
settings.title = "GE-14 BWR assembly - Serpent2 export from starterDD, void 0%, uncontrolled geometry"
settings.bc = 2  # Reflective boundary conditions
settings.neutrons_per_cycle = 2000000
settings.active_cycles = 5000
settings.inactive_cycles = 100
settings.ures = True  # Unresolved resonance probability tables
settings.set_nuclear_data_evaluation(nuclear_data_library)
# Optional: set up library paths (uncomment and adjust as needed)
# settings.set_endfb8r1_libraries("/path/to/nuclear_data")
# settings.set_jeff311_libraries("/path/to/nuclear_data")

# Add geometry plot
settings.add_plot(plot_type=3, x_pixels=1500, y_pixels=1500)

# =====================================================================
# 4. Build the Serpent2Model
# =====================================================================
print("Building Serpent2 model...")
model = Serpent2Model(assembly_model=GE14_assembly, settings=settings)

# Build geometry: pins, lattice, channel box
model.build(
    gap_material_name="gap",
    clad_material_name="zr2",
    coolant_material_name="coolant",
    outer_water_material_name="moderator",
    channel_box_material_name="zr4",
    lattice_name="10",
    empty_universe_name="empty",
)

# Add structural (non-fuel) materials from the assembly composition lookup
model.build_structural_materials_from_assembly(
    name_map={
        "COOLANT": "coolant",
        "CLAD": "zr2",
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
# To reconstruct DRAGON neutronic absorption the following are needed :
# MT 102 (n,gamma), 103 (n,proton), 104 (n,deutron), 105 (n,ttriton), 107 (n,alpha), 108 (n,2alpha) 28 (n,np), 16 (n,2n), 17 (n,3n), 37 (n,4n)
# This ensures each isotope is only scored for reactions where it has data.
if nuclear_data_library == "endfb8r1":
    print("Using ENDF/B-VIII.1 nuclear data library for detector configuration.")
    reaction_isotope_map = {
        'disappearance': ['U235', 'U238', 'Gd155', 'Gd157'],  # All tracked, MT=101
        'fission': ['U235', 'U238'],  # Actinides with fission XS MT=18
        'n,gamma': ['U235', 'U238', 'Gd155', 'Gd157'],  # MT=102
        'n,proton': ['U238'],  # MT=103, not available for U235 in ENDF/B-VIII.1
        #'n,deutron': ['U235', 'U238'],  # MT=104, not available for U235 and U238 in ENDF/B-VIII.1
        #'n,triton': ['U235', 'U238'],  # MT=105, not available for U235 and U238 in ENDF/B-VIII.1
        'n,alpha': ['U235', 'U238'],  # MT=107
        #'n,2alpha': ['U235', 'U238'],  # MT=108, not available for U235 and U238 in ENDF/B-VIII.1
        #'n,np': ['U235', 'U238'],  # MT=28, not available for U235 and U238 in ENDF/B-VIII.1
        'n,2n': ['U235', 'U238'],  # MT=16
        'n,3n': ['U235', 'U238'],  # MT=17
        #'n,4n': ['U235', 'U238'],  # MT=37, not available for U235 and U238 in ENDF/B-VIII.1
    }
elif nuclear_data_library == "jeff311":
        reaction_isotope_map = {
        'disappearance': ['U235', 'U238', 'Gd155', 'Gd157'],  # All tracked, MT=101
        'fission': ['U235', 'U238'],  # Actinides with fission XS MT=18
        'n,gamma': ['U235', 'U238', 'Gd155', 'Gd157'],  # MT=102
        #'n,proton': ['U235', 'U238'],  # MT=103, not available for U235 in JEFF-3.1.1
        #'n,deutron': ['U235', 'U238'],  # MT=104, not available for U235, U238 in JEFF-3.1.1
        #'n,triton': ['U235', 'U238'],  # MT=105, not available for U235, U238 in JEFF-3.1.1
        #'n,alpha': ['U238'],  # MT=107, not available for U235, U238 in JEFF-3.1.1
        #'n,2alpha': ['U235', 'U238'],  # MT=108, not available for U235, U238 in JEFF-3.1.1
        #'n,np': ['U235', 'U238'],  # MT=28
        'n,2n': ['U235', 'U238'],  # MT=16
        'n,3n': ['U235', 'U238'],  # MT=17
        'n,4n': ['U235', 'U238'],  # MT=37
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
    energy_grid_name="2g",  # Use 2g energy grid for condensed reaction rates
    fuel_temperature=900.0,
    detector_type=-4,  # dt -4: sum over dm materials (all fuel zones of a pin)
)

# For precise 295g U238 rates tallies, spatially integrated over all fuel :
if nuclear_data_library == "endfb8r1":
    print("Adding separate 295g detector for U238 using ENDF/B-VIII.1 available reaction data.")
    reaction_isotope_map_295g_U238 = {
        'disappearance': ['U238'],  # MT=101
        'fission': ['U238'],  # MT=18
        'n,gamma': ['U238'],  # MT=102
        'n,proton': ['U238'],  # MT=103
        #'n,deutron': ['U238'],  # MT=104, not available for U238 in ENDF/B-VIII.1
        #'n,triton': ['U238'],  # MT=105, not available for U238 in ENDF/B-VIII.1
        'n,alpha': ['U238'],  # MT=107
        #'n,2alpha': ['U238'],  # MT=108, not available for U238 in ENDF/B-VIII.1
        #'n,np': ['U238'],  # MT=28, not available for U238 in ENDF/B-VIII.1
        'n,2n': ['U238'],  # MT=16
        'n,3n': ['U238'],  # MT=17
        #'n,4n': ['U238'],  # MT=37, not available for U238 in ENDF/B-VIII.1
    }
elif nuclear_data_library == "jeff311":
     reaction_isotope_map_295g_U238 = {
        'disappearance': ['U238'],  # All tracked, MT=101
        'fission': ['U238'],  # Actinides with fission XS MT=18
        'n,gamma': ['U238'],  # MT=102
        #'n,proton': ['U238'],  # MT=103, not available for U235 in JEFF-3.1.1
        #'n,deutron': ['U235', 'U238'],  # MT=104, not available for U235, U238 in JEFF-3.1.1
        #'n,triton': ['U235', 'U238'],  # MT=105, not available for U235, U238 in JEFF-3.1.1
        #'n,alpha': ['U238'],  # MT=107, not available for U235, U238 in JEFF-3.1.1
        #'n,2alpha': ['U235', 'U238'],  # MT=108, not available for U235, U238 in JEFF-3.1.1
        #'n,np': ['U235', 'U238'],  # MT=28
        'n,2n': ['U238'],  # MT=16
        'n,3n': ['U238'],  # MT=17
        'n,4n': ['U238'],  # MT=37
    }

model.add_assembly_integrated_detector_config(
    reaction_isotope_map=reaction_isotope_map_295g_U238,
    energy_grid_name="295g",  # Fine energy mesh for U238 rates
    fuel_temperature=900.0,
    detector_type=-4,  # dt -4: sum over dm materials (all fuel zones, all pins)
)


# Optionally add a global flux detector
model.add_flux_detector(energy_grid_name="295g", name="flux_295g")
model.add_flux_detector(energy_grid_name="26g", name="flux_26g")
model.add_flux_detector(energy_grid_name="2g", name="flux_2g")

# =====================================================================
# 6. Print summary and write output
# =====================================================================
print(model.summary())

output_filepath = f"{path_to_output}/GE14_DOM_00_assembly_{nuclear_data_library}.serp"
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
print("  Reaction-isotope mapping (per-pin 2g detectors):")
for reaction, isotopes in reaction_isotope_map.items():
    print(f"    - {reaction}: {', '.join(isotopes)}")
print(f"  Reaction-isotope mapping (assembly-integrated 295g detector):")
for reaction, isotopes in reaction_isotope_map_295g_U238.items():
    print(f"    - {reaction}: {', '.join(isotopes)}")
print(f"  Domain: dm cards for FUEL MATERIALS ONLY per pin")
print(f"  Detector type: dt -4 (sum over fuel zones per pin)")
print(f"  Energy grid: full range (integrated over all energies)")
print(f"  Total detectors: {len(model.detectors)}")
print("=" * 60)
