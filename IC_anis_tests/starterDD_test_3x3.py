from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *

from starterDD.starterDD.GeometryBuilder.glow_builder import generate_IC_cells, add_cells_to_regular_lattice, export_glow_geom



tracking_type = "TISO" # "TSPC"
pitch = 1.295
lattice_center = (0.0, 0.0, 0.0)
# numbered in increasing x / increasing y order
## Geometric data
lattice_desc_3x3_GdC = [
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_45Gd",  "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX"]
            ]

fuel_rod_radius, gap_radius, clad_radius = 0.4435, 0.4520, 0.5140

# ------------------------------------------------
# Test 3x3_Gd_C_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
cells_3x3_GdC = generate_IC_cells(lattice_desc_3x3_GdC, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)

lattice_3x3_GdC = Lattice(name='3x3 with Gd center', center=lattice_center)
lattice_3x3_GdC = add_cells_to_regular_lattice(lattice_3x3_GdC, cells_3x3_GdC, pitch, translation=0.0)

# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdC.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdC.show(PropertyType.MACRO)
lattice_3x3_GdC.show(PropertyType.MATERIAL)

# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_C_1fuel_index", lattice_3x3_GdC, tracking_type, export_macro=True)

### Set up 3x3_Gd_TR test
# Cells 1 to 8 : UOX fuels
# Cell 9 : Gd fuel, so switch cell5 and cell9

lattice_desc_3x3_GdTR = [
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_45Gd"]
            ]

cells_3x3_GdTR = generate_IC_cells(lattice_desc_3x3_GdTR, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)

# ------------------------------------------------
# Test 3x3_Gd_TR_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
lattice_3x3_GdTR = Lattice(name ='3x3 with Gd top right', center=lattice_center)

lattice_3x3_GdTR = add_cells_to_regular_lattice(lattice_3x3_GdTR, cells_3x3_GdTR, pitch)
# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdTR.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdTR.show(PropertyType.MACRO)
lattice_3x3_GdTR.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_TR_1fuel_index", lattice_3x3_GdTR , tracking_type, export_macro=True)
      
# ------------------------------------------------
# Test 3x3_Gd_TC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 2, 3, 4, 5, 6, 7, 9 : UOX fuels
# Cell 8 : Gd fuel, so switch cell5 and cell8
lattice_desc_3x3_GdTC = [
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_45Gd",  "ROD_24UOX"]
            ]
cells_3x3_GdTC = generate_IC_cells(lattice_desc_3x3_GdTC, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)
lattice_3x3_GdTC = Lattice(name='3x3 with Gd top center', center=lattice_center)
lattice_3x3_GdTC = add_cells_to_regular_lattice(lattice_3x3_GdTC, cells_3x3_GdTC, pitch)
# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdTC.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdTC.show(PropertyType.MACRO)
lattice_3x3_GdTC.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_TC_1fuel_index", lattice_3x3_GdTC , tracking_type, export_macro=True)
      

### For sanity check : create tests for bottom center and bottom left Gd positions too
# These should be equivalent to the top center and top right tests respectively

# ------------------------------------------------
# Test 3x3_Gd_BC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 3, 4, 5, 6, 7, 8, 9 : UOX fuels
# Cell 2 : Gd fuel, so switch cell2 and cell5
lattice_desc_3x3_GdBC = [
            ["ROD_24UOX", "ROD_45Gd",  "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX"]
            ]
cells_3x3_GdBC = generate_IC_cells(lattice_desc_3x3_GdBC, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)
lattice_3x3_GdBC = Lattice(name='3x3 with Gd bottom center', center=lattice_center)
lattice_3x3_GdBC = add_cells_to_regular_lattice(lattice_3x3_GdBC, cells_3x3_GdBC, pitch)
# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdBC.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdBC.show(PropertyType.MACRO)
lattice_3x3_GdBC.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_BC_1fuel_index", lattice_3x3_GdBC , tracking_type, export_macro=True)

# ------------------------------------------------
# Test 3x3_Gd_BL_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 2, 3, 4, 5, 6, 7, 8, 9 : UOX fuels
# Cell 1 : Gd fuel, so switch cell1 and cell5
lattice_desc_3x3_GdBL = [
            ["ROD_45Gd",  "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX"]
            ]
cells_3x3_GdBL = generate_IC_cells(lattice_desc_3x3_GdBL, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)
lattice_3x3_GdBL = Lattice(name='3x3 with Gd bottom left', center=lattice_center)
lattice_3x3_GdBL = add_cells_to_regular_lattice(lattice_3x3_GdBL, cells_3x3_GdBL, pitch)
# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdBL.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdBL.show(PropertyType.MACRO)
lattice_3x3_GdBL.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_BL_1fuel_index", lattice_3x3_GdBL , tracking_type, export_macro=True)


# ------------------------------------------------
# Test 3x3_Gd_RC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 2, 3, 4, 5, 7, 8, 9 : UOX fuels
# Cell 6 : Gd fuel, so switch cell6 and cell5
lattice_3x3_GdRC_desc = [
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_45Gd",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX"]
            ]
cells_3x3_GdRC = generate_IC_cells(lattice_3x3_GdRC_desc, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)
lattice_3x3_GdRC = Lattice(name='3x3 with Gd right center', center=lattice_center)
lattice_3x3_GdRC = add_cells_to_regular_lattice(lattice_3x3_GdRC, cells_3x3_GdRC, pitch)
# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdRC.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdRC.show(PropertyType.MACRO)
lattice_3x3_GdRC.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_RC_1fuel_index", lattice_3x3_GdRC , tracking_type, export_macro=True)

# ------------------------------------------------
# Test 3x3_Gd_LC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 2, 3, 5, 6, 7, 8, 9 : UOX fuels
# Cell 4 : Gd fuel, so switch cell6 and cell5
lattice_3x3_GdLC_desc = [
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX",],
            ["ROD_45Gd",  "ROD_24UOX", "ROD_24UOX",],
            ["ROD_24UOX", "ROD_24UOX", "ROD_24UOX"]
            ]
cells_3x3_GdLC = generate_IC_cells(lattice_3x3_GdLC_desc, 
                                 Gd_cells=["ROD_45Gd"],
                                 pitch=pitch, 
                                 C_to_mat={"ROD_24UOX": "24UOX", "ROD_45Gd": "45Gd"}, 
                                 fuel_rad=fuel_rod_radius, 
                                 gap_rad=gap_radius, 
                                 clad_rad=clad_radius,
                                 corner_radius=0,
                                 windmill=False)
lattice_3x3_GdLC = Lattice(name='3x3 with Gd left center', center=lattice_center)
lattice_3x3_GdLC = add_cells_to_regular_lattice(lattice_3x3_GdLC, cells_3x3_GdLC, pitch)
# Show the resulting layout with the 'MATERIAL' colorset
lattice_3x3_GdLC.apply_symmetry(SymmetryType.FULL)
lattice_3x3_GdLC.show(PropertyType.MACRO)
lattice_3x3_GdLC.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
export_glow_geom("data/glow_data/tdt_data", "3x3_Gd_LC_1fuel_index", lattice_3x3_GdLC , tracking_type, export_macro=True)

      

      