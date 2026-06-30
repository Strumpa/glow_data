## 3x3 test case for diagonal symmetry applied to IC solver

## Glow imports
from glow import *
from glow.geometry_layouts.layouts import associate_colors_to_regions, build_compound_regions
from glow.support.types import *
from glow.geometry_layouts.cells import CartesianCell
from glow.geometry_layouts.layouts import Region
from glow.geometry_layouts.lattices import CartesianLattice
from glow.geometry_layouts.geometries import Rectangle, Circle
from glow.main import TdtSetup, export_layout_to_tdt
from glow.interface.geom_interface import *
from glow.support.types import GeometryType, LayoutGeometryType, PropertyType, \
    SymmetryType
from glow.interface.geom_entities import wrap_shape
import numpy as np
import os

SYM_TO_LAYOUT_AND_BOUNDARY = {
    SymmetryType.FULL: {"TISO": {"layout": LayoutGeometryType.ISOTROPIC, "boundary": None},
                        "TSPC": {"layout": LayoutGeometryType.RECTANGLE_SYM, "boundary": BoundaryType.AXIAL_SYMMETRY}},
    SymmetryType.DIAG: {"TISO": {"layout": LayoutGeometryType.SYMMETRIES_TWO, "boundary": BoundaryType.AXIAL_SYMMETRY},
                        "TSPC": {"layout": LayoutGeometryType.RECTANGLE_EIGHT, "boundary": BoundaryType.AXIAL_SYMMETRY}},
}


tdt_output_path = "3x3_test_data" # modify according to where you wish to save output tdt files
# check of output path exists and create if not
cwd = os.getcwd()
if not os.path.isabs(tdt_output_path):
    tdt_output_path = os.path.join(cwd, tdt_output_path)
if not os.path.exists(tdt_output_path):
    os.makedirs(tdt_output_path)
diag_options = [True, False]
spatial_methods = ["MOC", "IC"]
sectorize_coolant_opt = [True, False]

fuel_radius = 0.4435
gap_radius = 0.4520
clad_radius = 0.5140
pin_pitch = 1.295

lattice_description = [
    ["ROD1", "ROD1", "ROD1"],
    ["ROD1", "ROD5", "ROD1"],
    ["ROD1", "ROD1", "ROD7"]
]

assembly_pitch = 3.885
Gd_rod_ids = ["ROD7"]


def computeVolumeBasedRadii(fuel_radius, gap_radius, clad_radius, fuel_volume_fractions):
    """
    Helper to define fuel region radii for fuel pins
    fuel_radius:
        radius of the fuel pellet, in cm
    gap_radius:
        radius of the expansion gap, in cm
    clad_radius:
        radius of the cladding, in cm
    fuel_volume_fractions:
        volume fractions for the fuel subdivisions, ordered radially
    """
    pin_radii = []
    if gap_radius is not None and gap_radius < fuel_radius:
        # in case expansion gap is inner most region, add it as the first radius and then compute the fuel radii based on the remaining fuel volume after subtracting the gap volume
        pin_radii.append(gap_radius)
    for volume_fract in fuel_volume_fractions:
        pin_radii.append(
            (volume_fract**0.5) * fuel_radius,
        )
    if gap_radius is not None and gap_radius > fuel_radius:
        # if gap radius is inner most region, add the clad radius as the last radius after the fuel radii
        pin_radii.append(gap_radius)    
    if clad_radius is not None:
        pin_radii.append(clad_radius)
    if gap_radius is not None and gap_radius > fuel_radius and clad_radius is None:
        ## print warning as this would be (fuel zones + gap zone) without clad. 
        print("Warning : gap radius is larger than fuel radius but no clad radius provided, this would lead to a pin with fuel zones and outer gap zone but no clad. Please check the input radii.")
    return pin_radii

center=(assembly_pitch / 2.0, assembly_pitch / 2.0, 0.0)

for apply_diagonal_symmetry in diag_options:
    for sectorize_coolant in sectorize_coolant_opt:
        for spatial_method in spatial_methods:
            # Create an empty lattice
            lattice = CartesianLattice(
                name=f"PB2_Type6-C_lattice",
                centre=center,
                cells=[],
            )

            # Iterate over lattice description to create all fuel cells, water rod cells and add to a Lattice
            water_rod_counter = 0
            row_idx = -1
            for row in lattice_description:
                row_idx += 1
                cell_idx = -1
                for cell in row:
                    cell_idx += 1
                    if cell in Gd_rod_ids:
                        fuel_material_names = [f"Gd_{cell}_1", f"Gd_{cell}_2", f"Gd_{cell}_3",
                                            f"Gd_{cell}_4", f"Gd_{cell}_5", f"Gd_{cell}_6",
                                            f"Gd_{cell}_7", f"Gd_{cell}_8", f"Gd_{cell}_9",
                                            f"Gd_{cell}_10", f"Gd_{cell}_11"]
                        fuel_volume_fractions = [0.1, 0.2, 0.3, 
                                                0.4, 0.5, 0.6, 
                                                0.7, 0.8, 0.9, 
                                                0.95, 1.0]
                        sectors = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8]
                        angles =  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 22.5]
                    else:
                        fuel_material_names = [f"UOX_{cell}_{row_idx}{cell_idx}_1", f"UOX_{cell}_{row_idx}{cell_idx}_2", 
                                            f"UOX_{cell}_{row_idx}{cell_idx}_3", f"UOX_{cell}_{row_idx}{cell_idx}_4"]
                        fuel_volume_fractions = [0.5, 0.8, 0.95, 1.0]
                        sectors = [1, 1, 1, 1, 1, 1, 8]
                        angles = [0, 0, 0, 0, 0, 0, 22.5]
                    radii = computeVolumeBasedRadii(fuel_radius, gap_radius, clad_radius, fuel_volume_fractions)
                    list_of_material_names = [fuel_material_name for fuel_material_name in fuel_material_names] + ["GAP", "CLAD"]
                    tmp_cell = CartesianCell(
                            name=fuel_material_names[0],
                            width_height=(pin_pitch, pin_pitch),
                            center=(0.0, 0.0, 0.0),
                            base_props={PropertyType.MATERIAL:"COOLANT",
                                        PropertyType.MACRO: f"MACRO{row_idx}{cell_idx}"}
                        )
                    for radius, mat in zip(radii[::-1],list_of_material_names[::-1]):
                        tmp_cell.add(
                            Region(Circle(radius=radius), properties={PropertyType.MATERIAL:mat, 
                                                                        PropertyType.MACRO:f"MACRO{row_idx}{cell_idx}"})
                    )
                    if sectorize_coolant:
                        tmp_cell.sectorize(sectors, angles, windmill=True)
                    lattice.add(
                            tmp_cell, position=((cell_idx + 0.5) * pin_pitch,
                                            (row_idx + 0.5) * pin_pitch,
                                            0.0)
                            )
                    

            ## Create a base CartesianCell to hold the assembly model :
            assembly = CartesianCell(
                name="3x3_Gd_test",
                width_height=(assembly_pitch, assembly_pitch),
                center=center,
                base_props={PropertyType.MATERIAL: "COOLANT",
                            PropertyType.MACRO:"BASE_CELL"},
            )

            assembly.add(lattice)

            if apply_diagonal_symmetry:
                assembly.apply_symmetry(SymmetryType.DIAG)
                symmetry_id = "DIAG"
                symetry_type = SymmetryType.DIAG

            else:
                assembly.apply_symmetry(SymmetryType.FULL)
                symmetry_id = "FULL"
                symetry_type = SymmetryType.FULL

            if sectorize_coolant:
                assembly.show(GeometryType.SECTORIZED, PropertyType.MATERIAL)
                geometry_to_export = GeometryType.SECTORIZED
                sect_id = "sect"
            else:
                assembly.show(GeometryType.TECHNOLOGICAL, PropertyType.MATERIAL)
                geometry_to_export = GeometryType.TECHNOLOGICAL
                sect_id = "nosect"
            ## Export the lower diagonal applying TISO conditions and exporting both MATERIAL and MACRO properties
            if spatial_method == "IC":
                tdt_file_name = f"3x3_Gd_{symmetry_id}_IC_TISO_MACRO_{sect_id}_test"
                reflection_type = "TISO"
                properties_to_export = [PropertyType.MACRO, PropertyType.MATERIAL]
            elif spatial_method == "MOC":
                tdt_file_name = f"3x3_Gd_{symmetry_id}_MOC_TSPC_{sect_id}_test"
                reflection_type = "TSPC"
                properties_to_export = [PropertyType.MATERIAL]
            export_layout_to_tdt(
                assembly, f"{tdt_output_path}/{tdt_file_name}", 
                        TdtSetup(geometry_to_export,
                                property_types=properties_to_export,
                                type_geo=SYM_TO_LAYOUT_AND_BOUNDARY[symetry_type][reflection_type]["layout"],
                                symmetry_type=symetry_type))   