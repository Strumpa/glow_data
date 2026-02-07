from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *



tracking_type = "TISO" # "TSPC"
pitch = 1.295
# numbered in increasing x / increasing y order
cell1 = RectCell(name="C1", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell2 = RectCell(name="C2", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell3 = RectCell(name="C3", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell4 = RectCell(name="C4", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell5 = RectCell(name="C5", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell6 = RectCell(name="C6", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell7 = RectCell(name="C7", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell8 = RectCell(name="C8", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
cell9 = RectCell(name="C9", height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))

radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
radiiGd = [0.19834, 0.28049, 0.34353, 0.39668, 0.43227, 0.4435, 0.4520, 0.5140]
#radii = [0.4435, 0.4520, 0.5140]
### Set up 3x3_Gd_C test : All fuels 24UOX, except 24UOX center
#    24UOX | 24UOX | 24UOX
#    24UOX | 24UOX  | 24UOX
#    24UOX | 24UOX | 24UOX
### Set up 3x3_Gd_TR test 

# Cells 1, 2, 3, 4, 6, 7, 8, 9 : UOX fuels
# Cell 5 : Gd fuel

for radius in radii:
    cell1.add_circle(radius)
    cell2.add_circle(radius)
    cell3.add_circle(radius)
    cell4.add_circle(radius)
    cell6.add_circle(radius)
    cell7.add_circle(radius)
    cell8.add_circle(radius)
    cell9.add_circle(radius)
for radius in radiiGd:
      cell5.add_circle(radius)
# Assign the materials to each zone in the cell1
cell1.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO1"]*7
       }
)
cell2.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO2"]*7
      }
)
cell3.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO3"]*7
       }
)
cell4.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO4"]*7
      }
)
cell5.set_properties(
      {PropertyType.MATERIAL: ["45Gd_1", "45Gd_2", "45Gd_3", "45Gd_4", "45Gd_5", "45Gd_6", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO5"]*9
       }
)
cell6.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO6"]*7
      }
)
cell7.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO7"]*7
      }
)
cell8.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO8"]*7
}
)
cell9.set_properties(
      {PropertyType.MATERIAL: ["24UOX_1", "24UOX_2", "24UOX_3", "24UOX_4", "GAP", "CLAD", "MODERATOR"],
       PropertyType.MACRO: ["MACRO9"]*7
}
)


# ------------------------------------------------
# Test 3x3_Gd_C_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
lattice = Lattice([cell1], '3x3 with Gd center', center=(0.0, 0.0, 0.0))
lattice.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))

# Second row
lattice.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell5, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice.add_cell(cell6, ((5/2)*pitch, (3/2)*pitch, 0.0))

# Third row
lattice.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell8, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice.add_cell(cell9, ((5/2)*pitch, (5/2)*pitch, 0.0))

# Apply the full symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MACRO)
lattice.show(PropertyType.MATERIAL)

# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice], "data/glow_data/tdt_data/3x3_Gd_C_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
      

### Set up 3x3_Gd_TR test
# Cells 1 to 8 : UOX fuels
# Cell 9 : Gd fuel, so switch cell5 and cell9

# ------------------------------------------------
# Test 3x3_Gd_TR_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
lattice2 = Lattice([cell1], '3x3 with Gd top right', center=(0.0, 0.0, 0.0))
lattice2.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice2.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
# Second row
lattice2.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice2.add_cell(cell9, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice2.add_cell(cell6, ((5/2)*pitch, (3/2)*pitch, 0.0))
# Third row
lattice2.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice2.add_cell(cell8, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice2.add_cell(cell5, ((5/2)*pitch, (5/2)*pitch, 0.0))

# Apply the full symmetry type to the cartesian lattice
lattice2.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice2.show(PropertyType.MACRO)
lattice2.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice2.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice2], "data/glow_data/tdt_data/3x3_Gd_TR_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
      
# ------------------------------------------------
# Test 3x3_Gd_TC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 2, 3, 4, 5, 6, 7, 9 : UOX fuels
# Cell 8 : Gd fuel, so switch cell5 and cell8
lattice3 = Lattice([cell1], '3x3 with Gd top center', center=(0.0, 0.0, 0.0))
lattice3.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice3.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
# Second row
lattice3.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice3.add_cell(cell8, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice3.add_cell(cell6, ((5/2)*pitch, (3/2)*pitch, 0.0))
# Third row
lattice3.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice3.add_cell(cell5, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice3.add_cell(cell9, ((5/2)*pitch, (5/2)*pitch, 0.0))

# Apply the full symmetry type to the cartesian lattice
lattice3.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice3.show(PropertyType.MACRO)
lattice3.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice3.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice3], "data/glow_data/tdt_data/3x3_Gd_TC_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
      

### For sanity check : create tests for bottom center and bottom left Gd positions too
# These should be equivalent to the top center and top right tests respectively

# ------------------------------------------------
# Test 3x3_Gd_BC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 3, 4, 5, 6, 7, 8, 9 : UOX fuels
# Cell 2 : Gd fuel, so switch cell2 and cell5
lattice4 = Lattice([cell1], '3x3 with Gd bottom center', center=(0.0, 0.0, 0.0))
lattice4.add_cell(cell5, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice4.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
# Second row
lattice4.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice4.add_cell(cell2, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice4.add_cell(cell6, ((5/2)*pitch, (3/2)*pitch, 0.0))
# Third row
lattice4.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice4.add_cell(cell8, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice4.add_cell(cell9, ((5/2)*pitch, (5/2)*pitch, 0.0))
# Apply the full symmetry type to the cartesian lattice
lattice4.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice4.show(PropertyType.MACRO)
lattice4.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice4.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice4], "data/glow_data/tdt_data/3x3_Gd_BC_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
# ------------------------------------------------
# Test 3x3_Gd_BL_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 2, 3, 4, 5, 6, 7, 8, 9 : UOX fuels
# Cell 1 : Gd fuel, so switch cell1 and cell5
lattice5 = Lattice([cell5], '3x3 with Gd bottom left', center=(0.0, 0.0, 0.0))
lattice5.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice5.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
#     Second row
lattice5.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice5.add_cell(cell6, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice5.add_cell(cell7, ((5/2)*pitch, (3/2)*pitch, 0.0))
#     Third row  
lattice5.add_cell(cell8, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice5.add_cell(cell9, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice5.add_cell(cell1, ((5/2)*pitch, (5/2)*pitch, 0.0))
# Apply the full symmetry type to the cartesian lattice
lattice5.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice5.show(PropertyType.MACRO)
lattice5.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice5.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice5], "data/glow_data/tdt_data/3x3_Gd_BL_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))


# ------------------------------------------------
# Test 3x3_Gd_RC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 2, 3, 4, 5, 7, 8, 9 : UOX fuels
# Cell 6 : Gd fuel, so switch cell6 and cell5
lattice5 = Lattice([cell1], '3x3 with Gd right center', center=(0.0, 0.0, 0.0))
lattice5.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice5.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
#     Second row
lattice5.add_cell(cell4, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice5.add_cell(cell6, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice5.add_cell(cell5, ((5/2)*pitch, (3/2)*pitch, 0.0))
#     Third row  
lattice5.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice5.add_cell(cell8, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice5.add_cell(cell9, ((5/2)*pitch, (5/2)*pitch, 0.0))
# Apply the full symmetry type to the cartesian lattice
lattice5.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice5.show(PropertyType.MACRO)
lattice5.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice5.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice5], "data/glow_data/tdt_data/3x3_Gd_RC_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
      
# ------------------------------------------------
# Test 3x3_Gd_LC_TISO_MACRO LATTICE CONSTRUCTION
# ------------------------------------------------
# Cells 1, 2, 3, 5, 6, 7, 8, 9 : UOX fuels
# Cell 4 : Gd fuel, so switch cell6 and cell5
lattice5 = Lattice([cell1], '3x3 with Gd left center', center=(0.0, 0.0, 0.0))
lattice5.add_cell(cell2, ((3/2)*pitch, (1/2)*pitch, 0.0))
lattice5.add_cell(cell3, ((5/2)*pitch, (1/2)*pitch, 0.0))
#     Second row
lattice5.add_cell(cell5, ((1/2)*pitch, (3/2)*pitch, 0.0))
lattice5.add_cell(cell4, ((3/2)*pitch, (3/2)*pitch, 0.0))
lattice5.add_cell(cell6, ((5/2)*pitch, (3/2)*pitch, 0.0))
#     Third row  
lattice5.add_cell(cell7, ((1/2)*pitch, (5/2)*pitch, 0.0))
lattice5.add_cell(cell8, ((3/2)*pitch, (5/2)*pitch, 0.0))
lattice5.add_cell(cell9, ((5/2)*pitch, (5/2)*pitch, 0.0))
# Apply the full symmetry type to the cartesian lattice
lattice5.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice5.show(PropertyType.MACRO)
lattice5.show(PropertyType.MATERIAL)
# Perform the geometry analysis and export the TDT file of the surface geometry
if tracking_type == "TISO":
      lattice5.type_geo = LatticeGeometryType.ISOTROPIC
      analyse_and_generate_tdt(
      [lattice5], "data/glow_data/tdt_data/3x3_Gd_LC_TISO_MACRO_fuel_rings", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))

      

      