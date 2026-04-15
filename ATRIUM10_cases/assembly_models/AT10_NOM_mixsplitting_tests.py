# DRAGON 2-levels flux calculation scheme with starterDD
# Generate glow geometries for each calculation step for the AT10 NOM assembly,
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
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    PWD = Path(__file__).resolve().parent
except NameError:
    # Running inside glow/SALOME — CWD is /home/user/data/
    PROJECT_ROOT = Path("/home/user/data/glow_data")
    PWD = PROJECT_ROOT / "ATRIUM10_cases" / "assembly_models"

assembly_id = "AT10_NOM" # Identifier for the assembly configuration (e.g., "GE14_DOM")
nuclear_data_library = "endfb8r1"  # Options: "endfb8r1", "jeff311"
mix_splitting = False  # Set to True to enable mix splitting in the second level flux calculation

if mix_splitting:
    case_name_suffix = "split"
    calculation_scheme = "CALC_SCHEME_2L_mix_splitting"
else:    
    case_name_suffix = "by_pin"
    calculation_scheme = "CALC_SCHEME_2L_by_pin"

AT10_NOM_INPUTS = PROJECT_ROOT / "ATRIUM10_cases" / "assembly_models" / "input_configs" / assembly_id
DRAGON_EXEC = os.environ.get('dragon_exec', 'path/to/dragon_executable')
DRAGLIBS_PATH = Path(os.environ.get('DRAGLIB_DIR', "/path/to/draglibs"))

# glow_data sits next to the starterDD project root
GLOW_DATA = PROJECT_ROOT
if mix_splitting:
    AT10_OUTPUT = GLOW_DATA / "starterDD_outputs" / "AT10" / assembly_id / "2L_scheme" / "mix_splitting"
else:
    AT10_OUTPUT = GLOW_DATA / "starterDD_outputs" / "AT10" / assembly_id / "2L_scheme" / "by_pin"

AT10_SERP_OUTPUT = GLOW_DATA / "ATRIUM10_cases" / "assembly_models" / "Serpent2_export" / assembly_id

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

AT10_assembly = DragonCase(
        case_name=f"{assembly_id}_{case_name_suffix}",
        call_glow=run_glow,
        draglib_name_to_alias={
            draglib_name: draglib_alias
        },
        config_yamls={
            "MATS": str(AT10_NOM_INPUTS / "material_compositions.yaml"),
            "GEOM": str(AT10_NOM_INPUTS / "GEOM.yaml"),
            "CALC_SCHEME": str(AT10_NOM_INPUTS / f"{calculation_scheme}.yaml"),
        },
        output_path=str(AT10_OUTPUT),
        tdt_path=str(AT10_OUTPUT),
    )
# Step 1 : Assign temperatures : 

AT10_assembly.set_fuel_material_temperatures({
    "24UOX": 900.0,
    "32UOX": 900.0,
    "42UOX": 900.0,
    "45UOX": 900.0,
    "48UOX": 900.0,
    "50UOX": 900.0,
    "45Gd": 900.0,
    "48Gd": 900.0,
})
AT10_assembly.set_non_fuel_temperatures(structural_temperature=600.0, coolant_temperature=600.0, moderator_temperature=600.0, gap_temperature=600.0)


# Step 2: Generate CLE2000 procedures (x2m + c2m files)
result = AT10_assembly.generate_cle2000_procedures()

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
    dry_result = AT10_assembly.run(
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
    run_result = AT10_assembly.run(
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
    reference_keff_from_S2 = 1.03493E+00
    print(f"Reference keff from Serpent2: {reference_keff_from_S2}")
    keff_diff = (run_result.keff - reference_keff_from_S2)*1e5
    print(f"Difference in pcm: {keff_diff:.2f} pcm")