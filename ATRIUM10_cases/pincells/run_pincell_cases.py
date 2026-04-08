# Example of a simple DRAGON 1 level flux calulation scheme with starterDD
# Generate a glow geometry with a single AT10 pincell,
# Run dragon with a RSE+IC self shielding step + direct 295g MOC flux calculation.

# Date : 30/03/2026
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
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
except NameError:
    # Running inside glow/SALOME — CWD is /home/user/data/
    PROJECT_ROOT = Path("/home/user/data/glow_data")

pincell_id = "AT10_45Gd" # or "AT10_45Gd" for the Gd case
nuclear_data_library = "endfb8r1"  # Options: "endfb8r1", "jeff311"

AT10_PINCELL_INPUTS = PROJECT_ROOT / "ATRIUM10_cases" / "pincells" / "input_configs" / pincell_id
DRAGON_EXEC = os.environ.get('dragon_exec', 'path/to/dragon_executable')
DRAGLIBS_PATH = Path(os.environ.get('DRAGLIB_DIR', "/path/to/draglibs"))

# glow_data sits next to the starterDD project root
GLOW_DATA = PROJECT_ROOT
AT10_OUTPUT = GLOW_DATA / "starterDD_outputs" / "AT10" / pincell_id / "1L_scheme"
AT10_SERP_OUTPUT = GLOW_DATA / "ATRIUM10_cases" / "pincells" / "Serpent2_export" / pincell_id

export_serpent2 = False # Set to False to skip Serpent2 export step
run_dragon = True # Set to False for a dry run (no Dragon execution)
run_glow = False  # Set to False to skip glow geometry generation and case setup

if nuclear_data_library == "endfb8r1":
    draglib_name = "draglibendfb8r1SHEM295_v5p1"
    draglib_alias = "endfb8r1295"
elif nuclear_data_library == "jeff311":
    draglib_name = "draglibJeff3p1p1SHEM295_v5p1"
    draglib_alias = "J311_295"
else:
    raise ValueError(f"Unsupported nuclear data library: {nuclear_data_library}")

ssh_method = "PT"  # Options: "PT", "RSE"
ssh_solution_doors = ["CP"] # "CP" or "IC"
possible_track_generation_method = {"CP": ["TSPC", "TISO"], 
                                    "IC": ["TISO"],
                                    "MOC": ["TSPC","TISO"]} # Options: "TSPC", "TISO" for CP and MOC, only TISO for IC
flux_solution_doors = ["MOC"]  # Options: "MOC", "TSPC"
anisortopy_treatment_options = ["ANIS1", "ANIS2", "ANIS2_CTRA", "ANIS4"] # Options: "ANIS1", "ANIS2", "ANIS4"
calculations_schemes = [f"{ssh_method}_{solution_door}_{track_method_ssh}_1L_{flux_solution_door}_{track_method_flux}_{anisotropy}" 
                        for solution_door in ssh_solution_doors 
                        for track_method_ssh in possible_track_generation_method.get(solution_door, []) 
                        for flux_solution_door in flux_solution_doors 
                        for track_method_flux in possible_track_generation_method.get(flux_solution_door, [])
                        for anisotropy in anisortopy_treatment_options]  # List of calculation schemes to generate (must match names in AT10_INPUTS/)

# Serpent2 reference keff at 900K for TFuel and 600K for non-fuel materials
keff_S2_reference = {"endfb8r1": {"AT10_24UOX": 1.23734E+00,
                                  "AT10_45Gd": 4.31421E-01,
                                  "AT10_50UOX": 1.36421E+00}, 
                     
                     "jeff311": None}  # Reference keff values for Serpent2 models with the specified nuclear data libraries
results_summary = {}
#calculations_schemes = ["CALC_SCHEME"]
for calculation_scheme in calculations_schemes:
    AT10_pincell = DragonCase(
            case_name=pincell_id,
            call_glow=run_glow,
            draglibs_names_to_alias={
                draglib_name: draglib_alias
            },
            config_yamls={
                "MATS": str(AT10_PINCELL_INPUTS / "material_compositions.yaml"),
                "GEOM": str(AT10_PINCELL_INPUTS / "GEOM.yaml"),
                "CALC_SCHEME": str(AT10_PINCELL_INPUTS / f"{calculation_scheme}.yaml"),
            },
            output_path=str(AT10_OUTPUT),
            tdt_path=str(AT10_OUTPUT),
        )
    fuel_id = pincell_id.split("_")[1]  # Extract "24UOX", "45Gd", or "50UOX" from the pincell_id
    # Step 1 : Assign temperatures : 
    AT10_pincell.set_fuel_material_temperatures({
        fuel_id: 900.0
    })
    AT10_pincell.set_non_fuel_temperatures(structural_temperature=600.0, coolant_temperature=600.0, moderator_temperature=600.0, gap_temperature=600.0)


    # Step 2: Generate CLE2000 procedures (x2m + c2m files)
    result = AT10_pincell.generate_cle2000_procedures()

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
        dry_result = AT10_pincell.run(
            draglib_paths={
                draglib_name: (DRAGLIBS_PATH / draglib_name),
            }, # if None, read from the $DRAGLIBS env var, and selected name + alias in the case config.
            results_root="./results",
            dry_run=True,
        )
        print(f"Dry run directory: {dry_result.run_directory}")

    # --- Option B: full execution --------------------------------------
    # Requires $dragon_exec and draglib files to be available.
    #
    if run_dragon:
        print("Running Dragon... This may take a few moments.")
        print(f"Using Dragon executable: {DRAGON_EXEC}")
        run_result = AT10_pincell.run(
            dragon_executable=DRAGON_EXEC,  # or None to use $dragon_exec
            draglib_paths={
                draglib_name: (DRAGLIBS_PATH / draglib_name),
            },
            results_root="./results",
            num_threads=1,
        )
        print(f"Draglibs path used: {DRAGLIBS_PATH / draglib_name}")
        print("Dragon run completed.")
        print(f"Success: {run_result.success}")
        print(f"keff:    {run_result.keff}")
        print(f"Time:    {run_result.wall_time_seconds:.1f}s")
        print(f"Results: {run_result.run_directory}")
        if nuclear_data_library in keff_S2_reference and keff_S2_reference[nuclear_data_library][pincell_id] is not None:
            print(f"Serpent2 reference keff for {nuclear_data_library}: {keff_S2_reference[nuclear_data_library][pincell_id]}")
            delta_keff = (run_result.keff - keff_S2_reference[nuclear_data_library][pincell_id])*1e5
            print(f"Delta keff (pcm): {delta_keff:.2f} pcm")
            results_summary[calculation_scheme] = (run_result.keff, delta_keff)
#
# Results directory structure:
#   results/
#   └── AT10_<pincell_id>/
#       └── RSE_IC_1L_CP/
#           ├── 2026-03-12T14-32-07/
#           │   ├── run_manifest.yaml
#           │   ├── inputs/           (frozen config yamls)
#           │   ├── procedures/       (generated CLE2000 files)
#           │   ├── AT10_<pincell_id>.result   (Dragon listing)
#           │   └── _CPO_AT10_<pincell_id>     (COMPO output)
#           └── latest -> 2026-03-12T14-32-07/

if run_dragon and results_summary:
    print("\n" + "=" * 60)
    print("  DRAGON RESULTS SUMMARY (delta keff in pcm relative to Serpent2 reference)")
    print("=" * 60)
    for scheme, (keff, delta_keff) in results_summary.items():
        print(f"  {scheme}: keff = {keff:.6f}, delta = {delta_keff:.2f} pcm")
    print("=" * 60)

     # save a pandas data frame with the results summary (optional)
    # introduce columns for calculation scheme options : self-shielding method, SSH solution door, flux solution door, track generation method for SSH and flux, anisotropy treatment
    try:
        import pandas as pd
        df = pd.DataFrame.from_dict(results_summary, orient='index', columns=['keff', 'delta_keff_pcm'])
        df.index.name = 'calculation_scheme'
        df.reset_index(inplace=True)

        # Parse scheme name into explicit option columns.
        # The anisotropy token may include underscores (e.g., ANIS2_CTRA),
        # so capture it as the trailing remainder.
        scheme_pattern = (
            r'^(?P<ssh_method>[^_]+)_(?P<ssh_solution_door>[^_]+)_(?P<ssh_tracking_method>[^_]+)_'
            r'(?P<flux_levels>[^_]+)_(?P<flux_solution_door>[^_]+)_(?P<flux_tracking_method>[^_]+)_'
            r'(?P<anisotropy_expansion>.+)$'
        )
        extracted = df['calculation_scheme'].str.extract(scheme_pattern)
        if extracted.notna().all(axis=1).all():
            df = pd.concat([df, extracted], axis=1)
        else:
            print(
                "\nWarning: some calculation_scheme values could not be parsed; "
                "scheme option columns were not expanded for those rows."
            )

        summary_csv_path = Path("results") / f"results_summary_{pincell_id}_{nuclear_data_library}.csv"
        summary_csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(summary_csv_path, index=False)
        print(f"\nResults summary saved to: {summary_csv_path}")
    except ImportError:
        print("\nPandas not available, skipping results summary CSV export.")

# export to Serpent2
if export_serpent2:
    
    outout_dir = AT10_SERP_OUTPUT
    outout_dir.mkdir(parents=True, exist_ok=True)
    output_filepath = f"{AT10_SERP_OUTPUT}/{pincell_id}_00_{nuclear_data_library}.serp"
    # =====================================================================
    # 1. Load material compositions and rod-ID → material mapping
    # =====================================================================
    path_to_yaml_compositions = AT10_PINCELL_INPUTS / "material_compositions.yaml"
    path_to_yaml_geometry = AT10_PINCELL_INPUTS / "GEOM.yaml"

    compositions = parse_all_compositions_from_yaml(path_to_yaml_compositions)
    ROD_to_material = associate_material_to_rod_ID(
        path_to_yaml_compositions, path_to_yaml_geometry
    )

    # =====================================================================
    # 2. Build the CartesianAssemblyModel
    # =====================================================================
    AT10_assembly = CartesianAssemblyModel(
        name=f"{pincell_id}_serpent2",
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
    settings.title = f"AT-10 BWR fuel cell ({pincell_id}) - Serpent2 export from starterDD, void 0%"
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
    model = Serpent2Model(assembly_model=AT10_assembly, settings=settings)

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

