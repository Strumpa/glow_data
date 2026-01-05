from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


def add_cells_to_regular_lattice(lattice, ordered_cells, cell_pitch):
    """
    add cells to the lattice geometry
    
    Parameters : 
    --------------
        - lattice : glow lattice object, to represent regular cartesian lattice
        - ordered_cells : list of cells to add to regular lattice
        - cell_pitch : regular x/y-offset seperating cells (square cell side length)

    Return : 
    ---------

        - lattice : glow lattice with update geometry
    """

    for row_idx in range(len(ordered_cells)):
        row_of_cells = ordered_cells[row_idx]
        for cell_idx in range(len(row_of_cells)):
            cell = row_of_cells[cell_idx]
            if row_idx == 0 and cell_idx == 0: # Skip first cell for now, see for better implementation with initial empty lattice
                continue
            else:
                print(f"Adding cell {cell} at position ({row_idx}, {cell_idx})")
                print(f"x coord : {(cell_idx + 1/2)*cell_pitch} cm")
                print(f"y coord : {(row_idx + 1/2)*cell_pitch} cm")
                lattice.add_cell(cell, ((cell_idx + 1/2)*cell_pitch, (row_idx + 1/2)*cell_pitch,  0.0))

    return lattice



def generate_cells(lattice_desc, pitch, C_to_mat):
    """
    generate RectCell objects for each individual subgeometry in the lattice
    
    Parameters : 
    -------------
    lattice_desc : list of list of strings : cell names for lattice description, ordered in x-increasing, y-increasing 
        (DRAGON convention)
    
    pitch : float : cell pitch (cm) (assuming all cells are squares of pitch x pitch dimension)

    C_to_mat : dictionary : keys are "C" identifiers, values are corresponding fuel material names.


    Returns : 
    -----------
    list of list of RectCell to be used to assemble the lattice with : 
        - ordered in x-increasing, y-increasing order 
        - geometrical definition of sub-regions defined
        - materials set 
        - MACROS associated       
    """
    Gd_cells = ["C7", "C8"]
    lattice_components = []
    for row_idx in range(len(lattice_desc)):
        row = lattice_desc[row_idx]
        row_of_cells = []
        for cell_idx in range(len(row)):
            cell_id = row[cell_idx]
            print(f"at row={row_idx+1}, col={cell_idx+1}, cell_id = {cell_id}")
            tmp_cell = RectCell(name=cell_id, height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
            if cell_id in Gd_cells:
                mat_name = C_to_mat[cell_id]
                radii = [0.19834, 0.28049, 0.34353, 0.39668, 0.43227, 0.4435, 0.4520, 0.5140]
                print(f"Adding Gd bearing pin with mat_name = {mat_name}")
            elif cell_id[0] == "C":
                mat_name = C_to_mat[cell_id]
                radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
                print(f"Adding UOX pin with mat_name = {mat_name}")
            else: ## This is simplified for water hole, need to improve that later
                radii = []
                mat_name = "MODERATOR"
            for radius in radii:
                tmp_cell.add_circle(radius)

            if mat_name == "MODERATOR":
                tmp_cell.set_properties(
                    {PropertyType.MATERIAL: ["MODERATOR"],
                     PropertyType.MACRO: [f"MACRO{row_idx}{cell_idx}"]}
                )
            else:
                if cell_id in Gd_cells:
                    print("Construct list of fuel materials for Gd cell")
                    list_of_cell_mats = [mat_name]*6
                    print(list_of_cell_mats)
                else:
                    print("Construct list of fuel materials for UOX cell")
                    list_of_cell_mats = [mat_name]*4
                    print(list_of_cell_mats)
                list_of_cell_mats.extend(["GAP", "CLAD", "COOLANT"])
                # Assign the materials to each zone in the cell
                print(list_of_cell_mats)
                tmp_cell.set_properties(
                    {PropertyType.MATERIAL: list_of_cell_mats,
                    PropertyType.MACRO: [f"MACRO{row_idx}{cell_idx}"]*len(list_of_cell_mats)}
                )
            row_of_cells.append(tmp_cell)
        lattice_components.append(row_of_cells)
    return lattice_components

            


C_to_MAT = {
    "C1":"24UOX",
    "C2":"32UOX",
    "C3":"42UOX",
    "C4":"45UOX",
    "C5":"48UOX",
    "C6":"50UOX",
    "C7":"45Gd",
    "C8":"42Gd",
}

tracking_type = "TISO" # "TSPC"
pitch = 1.295
asembly_pitch = 15.24

lattice_description = [
    ["C1", "C2", "C3", "C5", "C6", "C5", "C4", "C3", "C2", "C1"],
    ["C2", "C4", "C7", "C6", "C7", "C6", "C6", "C7", "C4", "C2"],
    ["C3", "C7", "C6", "C6", "C6", "C7", "C6", "C6", "C7", "C3"],
    ["C5", "C6", "C6", "C6", "C6", "C6", "C7", "C6", "C5", "C4"],
    ["C6", "C7", "C6", "C6", "W1", "WB", "W2", "C4", "C6", "C4"],
    ["C5", "C6", "C7", "C6", "WL", "W0", "WR", "C3", "C7", "C4"],
    ["C4", "C6", "C6", "C7", "W3", "WT", "W4", "C4", "C4", "C4"],
    ["C3", "C7", "C6", "C6", "C4", "C3", "C4", "C4", "C8", "C3"],
    ["C2", "C4", "C7", "C5", "C6", "C7", "C4", "C8", "C4", "C2"],
    ["C1", "C2", "C3", "C4", "C4", "C4", "C4", "C3", "C2", "C1"]
    ]

# Generate material cells 

ordered_cells = generate_cells(lattice_desc=lattice_description, pitch=pitch, C_to_mat=C_to_MAT)

# Apply the cell1's sectorization
#cell1.sectorize([1, 1, 1, 1, 1, 1, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice([ordered_cells[0][0]], 'ATRIUM-10 Lattice', center=(0.0, 0.0, 0.0))
#lattice.add_rings_of_cells(cell1, 1)

# First row
lattice = add_cells_to_regular_lattice(lattice=lattice, ordered_cells=ordered_cells, cell_pitch=pitch)

lattice.show(PropertyType.MATERIAL)

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one
lattice.show(PropertyType.MATERIAL)

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MACRO)


# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/glow_data/tdt_data/AT10_LAT_TISO_MACRO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL, PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))