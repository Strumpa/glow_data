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
from starterDD.starterDD.GeometryAnalysis.tdt_parser import read_material_mixture_indices_from_tdt_file
from starterDD.starterDD.InterfaceToDD.dragon_module_calls import LIB

# set up 3x3 test cases for IC method testing in 
lattice_center = (0.0, 0.0, 0.0)
### GLOW OUTPUT PARAMETERS 
tracking_type = "TISO"  # Options: "TISO" or "TSPC"
export_macro = True  # Whether to export MACRO definitions in the TDT file
path_to_tdt = "data/glow_data/tdt_data"
case_names_to_latdesc = {"3x3_Gd_C_MAC":None, 
                        "3x3_Gd_TR_MAC":[["ROD1", "ROD1", "ROD1",],
                                        ["ROD1", "ROD1", "ROD1",],
                                        ["ROD1", "ROD1", "ROD7"]], 
                        
                        "3x3_Gd_TC_MAC":[["ROD1", "ROD1", "ROD1",],
                                        ["ROD1", "ROD1", "ROD1",],
                                        ["ROD1", "ROD7",  "ROD1"]],
                        
                        "3x3_Gd_BC_MAC":[["ROD1", "ROD7",  "ROD1",],
                                        ["ROD1", "ROD1", "ROD1",],
                                        ["ROD1", "ROD1", "ROD1"]],
                        
                        "3x3_Gd_BL_MAC":[["ROD7", "ROD1",  "ROD1",],
                                        ["ROD1", "ROD1", "ROD1",],
                                        ["ROD1", "ROD1", "ROD1"]],
                        
                        "3x3_Gd_RC_MAC":[["ROD1", "ROD1",  "ROD1",],
                                        ["ROD1", "ROD1", "ROD7",],
                                        ["ROD1", "ROD1", "ROD1"]],
                        
                        "3x3_Gd_LC_MAC":[["ROD1", "ROD1",  "ROD1",],
                                        ["ROD7", "ROD1", "ROD1",],
                                        ["ROD1", "ROD1", "ROD1"]],
                        }
## import model : 
path_to_yaml_compositions = "glow_data/ATRIUM10_cases/input_configs/material_compositions.yaml"
path_to_yaml_geometry = "glow_data/IC_anis_tests/input_configs/geometry_definitions_MACRO_tests.yaml"
compositions = parse_all_compositions_from_yaml(path_to_yaml_compositions)
ROD_to_material = associate_material_to_rod_ID(path_to_yaml_compositions,
                                               path_to_yaml_geometry)
for case_name, lattice_desc in case_names_to_latdesc.items():
    file_to_save_name = case_name

    if lattice_desc is not None:
        # update the lattice description attribute in the assembly model
        Gd_3x3_test_case.update_lattice_description(lattice_desc)
    else:
        # Create the assembly model with the given tdt file and lattice description.
        Gd_3x3_test_case = CartesianAssemblyModel(name="3x3_test_case",
                                            tdt_file=path_to_tdt + "/" + file_to_save_name + ".tdt",
                                            geometry_description_yaml=path_to_yaml_geometry)
        # Set the rod ID to material mapping in the assembly model
        Gd_3x3_test_case.set_rod_ID_to_material_mapping(ROD_to_material)
        # Set uniform temperatures for all materials in the assembly model
        Gd_3x3_test_case.set_uniform_temperatures(fuel_temperature=750.0, gap_temperature=750.0, coolant_temperature=559.0, moderator_temperature=559.0, structural_temperature=559.0)
    
    # Analyze the lattice description to build the lattice structure in the assembly model
    Gd_3x3_test_case.analyze_lattice_description(build_pins=True)
    # Set the material compositions in the assembly model
    Gd_3x3_test_case.set_material_compositions(compositions)
    # Number fuel material mixtures based on material names
    Gd_3x3_test_case.number_fuel_material_mixtures_by_material()

    # ------------------------------------------------
    # Test 3x3_Gd_C_TISO_MACRO LATTICE CONSTRUCTION
    # ------------------------------------------------
    ordered_fuel_cells = generate_fuel_cells(
        assemblyModel=Gd_3x3_test_case,
    )

    lattice_3x3 = Lattice(name=case_name, center=lattice_center)
    lattice_3x3 = add_cells_to_regular_lattice(lattice_3x3, ordered_fuel_cells, 
                                                Gd_3x3_test_case.pin_geometry_dict["pin_pitch"], 
                                                translation=0.0)

    # Show the resulting layout with the 'MATERIAL' colorset
    lattice_3x3.apply_symmetry(SymmetryType.FULL)
    lattice_3x3.show(PropertyType.MACRO)
    lattice_3x3.show(PropertyType.MATERIAL)

    # Perform the geometry analysis and export the TDT file of the surface geometry
    export_glow_geom(path_to_tdt, file_to_save_name, lattice_3x3, tracking_type, export_macro=True)
    