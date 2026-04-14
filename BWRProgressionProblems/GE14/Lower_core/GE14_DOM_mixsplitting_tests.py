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
    
except ImportError:
    
    GLOW_AVAILABLE = False
    from starterDD.InterfaceToDD.case_generator import DragonCase

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
    PWD = PROJECT_ROOT / "BWRProgressionProblems" / "GE14" / "Lower_core"

assembly_id = "GE14_DOM" # Identifier for the assembly configuration (e.g., "GE14_DOM")
nuclear_data_library = "endfb8r1"  # Options: "endfb8r1", "jeff311"
mix_splitting = True  # Set to True to enable mix splitting in the second level flux calculation

if mix_splitting:
    case_name_suffix = "split"
    calculation_scheme = "CALC_SCHEME_2L_mix_splitting"
else:    
    case_name_suffix = "by_pin"
    calculation_scheme = "CALC_SCHEME_2L_by_pin"

GE14_DOM_INPUTS = PROJECT_ROOT / "BWRProgressionProblems" / "GE14" / "input_configs" / assembly_id
GE14_GENERAL_INPUTS = PROJECT_ROOT / "BWRProgressionProblems" / "GE14" / "input_configs" 
DRAGON_EXEC = os.environ.get('dragon_exec', 'path/to/dragon_executable')
DRAGLIBS_PATH = Path(os.environ.get('DRAGLIB_DIR', "/path/to/draglibs"))

# glow_data sits next to the starterDD project root
GLOW_DATA = PROJECT_ROOT
if mix_splitting:
    GE14_OUTPUT = GLOW_DATA / "starterDD_outputs" / "GE14" / assembly_id / "2L_scheme" / "mix_splitting"
else:
    GE14_OUTPUT = GLOW_DATA / "starterDD_outputs" / "GE14" / assembly_id / "2L_scheme" / "by_pin"

GE14_SERP_OUTPUT = GLOW_DATA / "BWRProgressionProblems" / "GE14" / "Serpent2_export" / assembly_id

export_serpent2 = False # Set to False to skip Serpent2 export step
run_dragon = False # Set to False for a dry run (no Dragon execution)
run_glow = False  # Set to False to skip glow geometry generation and case setup

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
        draglibs_names_to_alias={
            draglib_name: draglib_alias
        },
        config_yamls={
            "MATS": str(GE14_GENERAL_INPUTS / "material_compositions.yaml"),
            "GEOM": str(GE14_DOM_INPUTS / "GEOM.yaml"),
            "CALC_SCHEME": str(GE14_DOM_INPUTS / f"{calculation_scheme}.yaml"),
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