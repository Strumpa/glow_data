# DRAGON 2-levels flux calculation scheme with starterDD
# Generate glow geometries for each calculation step for the GE14  assembly,
# Run dragon with a PT+IC self shielding step + first level IC on 295g + second level 26g MOC flux calculation.
# At self shielding step and 1st level flux calculation, each pin is divided in Santamarina radial zones, 
# Material Mixes are numbered by material ie enrichment / fuel type. 
# Cross sections are condensed from 295g to 26g after the first level flux calculation, 
# Mixes are duplicated to the "by pin" numbering scheme and assigned to the respective pins,
# The second level flux calculation is performed on the 26g cross sections with the "by pin" mixes.

# Date : 08/04/2026
# R.Guasch

from pathlib import Path
import os

try:
    from glow.support.types import GeometryType, PropertyType
    from starterDD.starterDD.InterfaceToDD.case_generator import DragonCase
    GLOW_AVAILABLE = True
    from starterDD.starterDD.DDModel.helpers import associate_material_to_rod_ID
    from starterDD.starterDD.MaterialProperties.material_mixture import parse_all_compositions_from_yaml
    from starterDD.starterDD.DDModel import CartesianAssemblyModel
    from starterDD.starterDD.InterfaceToDD.Serpent2_exports import (
        Serpent2Model,
        S2_Settings,
        S2_EnergyGrid,
    )
except ImportError:
    GLOW_AVAILABLE = False
    from starterDD.InterfaceToDD.case_generator import DragonCase
    from starterDD.DDModel.helpers import associate_material_to_rod_ID
    from starterDD.MaterialProperties.material_mixture import parse_all_compositions_from_yaml
    from starterDD.DDModel import CartesianAssemblyModel
    from starterDD.InterfaceToDD.Serpent2_exports import (
        Serpent2Model,
        S2_Settings,
        S2_EnergyGrid,
    )

# =====================================================================
# Configuration paths — anchored to the project root so the script
# works regardless of the working directory it is launched from.
#
# Inside glow/SALOME, __file__ is not defined (the script is exec'd
# in an embedded interpreter), so we fall back to the well-known
# Docker mount point.
# =====================================================================
try:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    PWD = Path(__file__).resolve().parent
except NameError:
    # Running inside glow/SALOME — CWD is /home/user/data/
    PROJECT_ROOT = Path("/home/user/data/glow_data")
    PWD = PROJECT_ROOT / "BWRProgressionProblems" / "GE14" / "DOM_slice"

assembly_id = "GE14_DOM" # Identifier for the assembly configuration (e.g., "GE14_DOM")
macro_grouping_type = "3x3"
nuclear_data_library = "endfb8r1"  # Options: "endfb8r1", "jeff311"

GE14_DOM_INPUTS = PROJECT_ROOT / "BWRProgressionProblems" / "GE14" / "input_configs" / assembly_id
GE14_GENERAL_INPUTS = PROJECT_ROOT / "BWRProgressionProblems" / "GE14" / "input_configs" 
DRAGON_EXEC = os.environ.get('dragon_exec', 'path/to/dragon_executable')
DRAGLIBS_PATH = Path(os.environ.get('DRAGLIB_DIR', "/path/to/draglibs"))

GLOW_DATA = PROJECT_ROOT

case_name_suffix = f"macro_groupings"
GE14_OUTPUT = GLOW_DATA / "starterDD_outputs" / "GE14" / assembly_id / "2L_scheme" / macro_grouping_type

GE14_SERP_OUTPUT = GLOW_DATA / "BWRProgressionProblems" / "GE14" / "Serpent2_export" / assembly_id

export_serpent2 = False # Set to False to skip Serpent2 export step
run_dragon = False # Set to False for a dry run (no Dragon execution)
run_glow = True  # Set to False to skip glow geometry generation and case setup

if nuclear_data_library == "endfb8r1":
    draglib_name = "draglibendfb8r1SHEM295_v5p1"
    draglib_alias = "endfb8r1295"
elif nuclear_data_library == "jeff311":
    draglib_name = "draglibJeff3p1p1SHEM295_v5p1"
    draglib_alias = "J311_295"
else:
    raise ValueError(f"Unsupported nuclear data library: {nuclear_data_library}")



GE14_assembly = DragonCase(
        case_name=f"{assembly_id}_{case_name_suffix}",
        call_glow=run_glow,
        draglib_name_to_alias={
            draglib_name: draglib_alias
        },
        config_yamls={
            "MATS": str(GE14_GENERAL_INPUTS / "material_compositions.yaml"),
            "GEOM": str(GE14_DOM_INPUTS / "GEOM_DIAG.yaml"),
            "CALC_SCHEME": str(GE14_DOM_INPUTS / f"CALC_SCHEME_2L_{macro_grouping_type}_{case_name_suffix}.yaml"),
        },
        output_path=str(GE14_OUTPUT),
        tdt_path=str(GE14_OUTPUT),
    )
# Step 1 : Assign temperatures : 

GE14_assembly.set_fuel_material_temperatures({
    "UOX16": 900.0,
    "UOX28": 900.0,
    "UOX32": 900.0,
    "UOX36": 900.0,
    "UOX40": 900.0,
    "UOX40Gd8": 900.0,
    "UOX44": 900.0,
    "UOX44Gd6": 900.0,
    "UOX44Gd3": 900.0,
    "UOX49": 900.0,
    "UOX49Gd8": 900.0,
    "UOX49Gd6": 900.0,

})
GE14_assembly.set_non_fuel_temperatures(structural_temperature=600.0, coolant_temperature=600.0, moderator_temperature=600.0, gap_temperature=600.0)


# Step 2: Generate CLE2000 procedures (x2m + c2m files)
result = GE14_assembly.generate_cle2000_procedures()

# =====================================================================
# Step 3: Execute the case with the Dragon runner
#
# The runner replaces the manual rdragon + .access + .save workflow.
# It handles: executable resolution, input staging (TDT files,
# draglibs), execution in a temp directory, output collection,
# and traceability (manifest + config archival).
#
# Requirements:
#   - Dragon executable: set $dragon_exec or pass explicitly
#   - Draglib files: set $DRAGLIBS directory or pass draglib_paths
#
# Use dry_run=True to stage everything without executing Dragon.
# =====================================================================

# --- Option A: dry run (no Dragon execution) -----------------------
# Useful for verifying the setup before running.
#
if not run_dragon:
    dry_result = GE14_assembly.run(
        draglib_paths={
            draglib_name: (DRAGLIBS_PATH / draglib_name),
        }, # if None, read from the $DRAGLIBS env var, and selected name + alias in the case config.
        results_root=f"{str(PWD)}/results/{assembly_id}_{case_name_suffix}",
        dry_run=True,
    )
    print(f"Dry run directory: {dry_result.run_directory}")

# --- Option B: full execution --------------------------------------
# Requires $dragon_exec and draglib files to be available.
#
if run_dragon:
    print("Running Dragon... This may take a few moments.")
    print(f"Using Dragon executable: {DRAGON_EXEC}")
    run_result = GE14_assembly.run(
        dragon_executable=DRAGON_EXEC,  # or None to use $dragon_exec
        draglib_paths={
            draglib_name: (DRAGLIBS_PATH / draglib_name),
        },
        results_root=f"{str(PWD)}/results/{assembly_id}_{case_name_suffix}",
        num_threads=20,
    )
    print(f"Draglibs path used: {DRAGLIBS_PATH / draglib_name}")
    print("Dragon run completed.")
    print(f"Success: {run_result.success}")
    print(f"keff:    {run_result.keff}")
    print(f"Time:    {run_result.wall_time_seconds:.1f}s")
    print(f"Results: {run_result.run_directory}")
    reference_keff_from_S2 = 9.90259E-01
    print(f"Reference keff from Serpent2: {reference_keff_from_S2}")
    keff_diff = (run_result.keff - reference_keff_from_S2)*1e5
    print(f"Difference in pcm: {keff_diff:.2f} pcm")



# export to Serpent2
if export_serpent2:
    
    outout_dir = GE14_SERP_OUTPUT
    outout_dir.mkdir(parents=True, exist_ok=True)
    output_filepath = f"{GE14_SERP_OUTPUT}/{assembly_id}_00_{nuclear_data_library}.serp"
    # =====================================================================
    # 1. Load material compositions and rod-ID → material mapping
    # =====================================================================
    path_to_yaml_compositions = GE14_GENERAL_INPUTS / "material_compositions.yaml"
    path_to_yaml_geometry = GE14_DOM_INPUTS / "GEOM.yaml"

    compositions = parse_all_compositions_from_yaml(path_to_yaml_compositions)
    ROD_to_material = associate_material_to_rod_ID(
        path_to_yaml_compositions, path_to_yaml_geometry
    )

    # =====================================================================
    # 2. Build the CartesianAssemblyModel
    # =====================================================================
    GE14_assembly = CartesianAssemblyModel(
        name=f"{assembly_id}_serpent2",
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
    settings.title = f"GE-14 BWR fuel cell ({assembly_id}) - Serpent2 export from starterDD, void 0%"
    settings.bc = 2  # Reflective boundary conditions
    settings.neutrons_per_cycle = 20000
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
            'n,alpha': ['U235', 'U238'],  # MT=107
            'n,2n': ['U235', 'U238'],  # MT=16
            'n,3n': ['U235', 'U238'],  # MT=17
        }
    elif nuclear_data_library == "jeff311":
            reaction_isotope_map = {
            'disappearance': ['U235', 'U238', 'Gd155', 'Gd157'],  # All tracked, MT=101
            'fission': ['U235', 'U238'],  # Actinides with fission XS MT=18
            'n,gamma': ['U235', 'U238', 'Gd155', 'Gd157'],  # MT=102
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

    model.add_detector_config(
        reaction_isotope_map=reaction_isotope_map,
        energy_grid_name="full",  # Use fully energy condensed grid for 1g reaction rates
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
            'n,alpha': ['U238'],  # MT=107
            'n,2n': ['U238'],  # MT=16
            'n,3n': ['U238'],  # MT=17
        }
    elif nuclear_data_library == "jeff311":
        reaction_isotope_map_295g_U238 = {
            'disappearance': ['U238'],  # All tracked, MT=101
            'fission': ['U238'],  # Actinides with fission XS MT=18
            'n,gamma': ['U238'],  # MT=102
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

    model.add_assembly_integrated_detector_config(
        reaction_isotope_map=reaction_isotope_map_295g_U238,
        energy_grid_name="26g",  # Fine energy mesh for U238 rates
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