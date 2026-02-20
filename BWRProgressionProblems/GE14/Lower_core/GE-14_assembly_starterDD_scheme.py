# GE-14 assembly geometry generation using DragonCalculationScheme.
#
# This script replaces the manual box subdivision and MACRO assignment
# of GE-14_assembly_starterDD.py with the automated pipeline provided
# by ``build_full_assembly_geometry`` and ``DragonCalculationScheme``.
#
# R.Guasch — 19/02/2026
# ---------------------------------------------------------------------------

from starterDD.starterDD.DDModel.helpers import associate_material_to_rod_ID
from starterDD.starterDD.MaterialProperties.material_mixture import parse_all_compositions_from_yaml
from starterDD.starterDD.DDModel import (
    CartesianAssemblyModel,
    DragonCalculationScheme,
)
from starterDD.starterDD.GeometryBuilder.glow_builder import build_full_assembly_geometry
from starterDD.starterDD.GeometryAnalysis.tdt_parser import read_material_mixture_indices_from_tdt_file
from starterDD.starterDD.InterfaceToDD.dragon_module_calls import LIB

# =====================================================================
# Configuration paths
# =====================================================================
path_to_yaml_compositions = "glow_data/BWRProgressionProblems/GE14/input_configs/material_compositions.yaml"
path_to_yaml_geometry     = "glow_data/BWRProgressionProblems/GE14/input_configs/GEOM_GE14_DOM.yaml"
path_to_yaml_calc_scheme  = "glow_data/BWRProgressionProblems/GE14/input_configs/CALC_SCHEME_GE14.yaml"

path_to_tdt  = "data/glow_data/tdt_data"
path_to_procs = "glow_data/BWRProgressionProblems/GE14/cle2000_procs"

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
    name="GE14_assembly",
    tdt_file=f"{path_to_tdt}/GE14_DOM.tdt",
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
GE14_assembly.analyze_lattice_description(build_pins=True)
GE14_assembly.set_material_compositions(compositions)

# =====================================================================
# 3. Load the Dragon Calculation Scheme from YAML
# =====================================================================
scheme = DragonCalculationScheme.from_yaml(path_to_yaml_calc_scheme)
print(scheme.summary())

# =====================================================================
# 4. For each calculation step, build geometry and generate outputs
# =====================================================================
for step in scheme.steps:
    print(f"\n{'='*60}")
    print(f"Processing step: {step.name}  ({step.step_type})")
    print(f"  Method:   {step.self_shielding_method} + {step.spatial_method}")
    print(f"  Tracking: {step.tracking}")
    print(f"  Macros:   {step.export_macros}")
    print(f"{'='*60}")

    # Derive output file name from the step
    file_to_save_name = f"GE14_DOM_{step.name}_{step.spatial_method}"

    # Number fuel material mixtures (needs radii applied first via step)
    step.apply_radii(GE14_assembly)
    GE14_assembly.number_fuel_material_mixtures_by_pin()

    # ---- Build full geometry (fuel cells + box + MACROs) and export TDT ----
    lattice, assembly_box_cell = build_full_assembly_geometry(
        assembly_model=GE14_assembly,
        calculation_step=step,
        output_path=path_to_tdt,
        output_file_name=file_to_save_name,
    )

    # Show the lattice in the SALOME viewer
    from glow.support.types import GeometryType, PropertyType
    lattice.show(
        geometry_type_to_show=GeometryType.SECTORIZED,
        property_type_to_show=PropertyType.MATERIAL,
    )
    if step.export_macros:
        lattice.show(
            geometry_type_to_show=GeometryType.SECTORIZED,
            property_type_to_show=PropertyType.MACRO,
        )

    if step.name == "SSH":
        print("Skipping TDT material mixture indices recovery for SSH step.")

        # ---- Recover TDT material mixture indices ----
        tdt_indices = read_material_mixture_indices_from_tdt_file(
            tdt_file_path=f"/home/user/{path_to_tdt}",
            tdt_file_name=file_to_save_name,
            tracking_option=step.tracking,
            include_macros=step.export_macros,
            material_names=None,  # get ALL entries (fuel + non-fuel)
        )
        GE14_assembly.enforce_material_mixture_indices_from_tdt(tdt_indices)

        # ---- Identify generating / daughter mixes ----
        GE14_assembly.identify_generating_and_daughter_mixes()

        # ---- Build LIB .c2m ----
        mix_definition_proc_name = f"MIX_GE14_{step.name}"
        lib = LIB(GE14_assembly)
        lib.set_isotope_alias("MODERATOR", "H1", "H1_H2O")
        lib.set_isotope_alias("COOLANT", "H1", "H1_H2O")
        lib.write_to_c2m(path_to_procs, mix_definition_proc_name)

        print(f"Step '{step.name}' completed — TDT exported, LIB written to "
            f"{path_to_procs}/{mix_definition_proc_name}.c2m")
