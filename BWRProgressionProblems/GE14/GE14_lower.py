from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


def computeSantamarinaradii(fuel_radius, gap_radius, clad_radius, gadolinium=False):
    # Helper to defined fuel region radii for fuel pins --> important for evolution calculations
    # UOX : Finer discretization close to the outer radii is important for rim effects : Pu formation
    # Gd2O3 : rim effect + Gd evolution = challenge for deterministic methods, need 6 sub regions.
    """
    r_out = float, fuel radius
    isGd = bool, adapting discretization to Gd pin --> 6 radial sub regions instead.
    A. Santamarina recommandations :
    volumes for UOX pins : 50%, 80%, 95% and 100%
    volumes for Gd2O3 pins : 20%, 40%, 60%, 80%, 95% and 100%
    """
    if gadolinium==False:
        pin_radii=[(0.5**0.5)*fuel_radius, (0.8**0.5)*fuel_radius, (0.95**0.5)*fuel_radius, fuel_radius, gap_radius, clad_radius]
        
    else :
        pin_radii=[(0.2**0.5)*fuel_radius, (0.4**0.5)*fuel_radius, (0.6**0.5)*fuel_radius, 
                    (0.8**0.5)*fuel_radius, (0.95**0.5)*fuel_radius, fuel_radius, gap_radius, clad_radius]
    return pin_radii


def generate_cells(lattice_desc, pitch, C_to_mat, fuel_rad, gap_rad, clad_rad):
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
    Gd_cells = ["ROD5G", "ROD6H", "ROD6K",  "ROD7G", "ROD7H"]
    lattice_components = []
    for row_idx in range(len(lattice_desc)):
        row = lattice_desc[row_idx]
        row_of_cells = []
        for cell_idx in range(len(row)):
            cell_id = row[cell_idx]
            tmp_cell = RectCell(name=cell_id, height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
            mat_name = C_to_mat[cell_id]
            if cell_id in Gd_cells:
                radii = computeSantamarinaradii(fuel_rad, gap_rad, clad_rad, gadolinium=True)
            elif "ROD" in cell_id and "W" not in cell_id:
                mat_name = C_to_mat[cell_id]
                radii = computeSantamarinaradii(fuel_rad, gap_rad, clad_rad, gadolinium=False)
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
                    list_of_cell_mats = [mat_name]*6
                else:
                    list_of_cell_mats = [mat_name]*4
                list_of_cell_mats.extend(["GAP", "CLAD", "COOLANT"])
                # Assign the materials to each zone in the cell
                tmp_cell.set_properties(
                    {PropertyType.MATERIAL: list_of_cell_mats,
                    PropertyType.MACRO: [f"MACRO{row_idx}{cell_idx}"]*len(list_of_cell_mats)}
                )
            row_of_cells.append(tmp_cell)
        lattice_components.append(row_of_cells)
    return lattice_components


def create_water_rods(pin_pitch, water_rod_inner_radius, water_rod_outer_radius):
    """
    Create water rods cells for GE-14 assembly
    Parameters :
    --------------
        - pin_pitch : float, pin pitch (cm)
        - water_rod_inner_radius : float, inner radius of water rod (cm)
        - water_rod_outer_radius : float, outer radius of water rod (cm)
    """
    water_rod_cell1 = RectCell(name="WATER_ROD_1", height_x_width=(2*pin_pitch, 2*pin_pitch), center=(2*pin_pitch, 2*pin_pitch, 0.0))
    water_rod_cell1.add_circle(water_rod_inner_radius)
    water_rod_cell1.add_circle(water_rod_outer_radius)
    water_rod_cell1.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
         PropertyType.MACRO: ["MACRO_WATER_ROD_1"]*3}
    )

    water_rod_cell2 = RectCell(name="WATER_ROD_2", height_x_width=(2*pin_pitch, 2*pin_pitch), center=(2*pin_pitch, 2*pin_pitch, 0.0))
    water_rod_cell2.add_circle(water_rod_inner_radius)
    water_rod_cell2.add_circle(water_rod_outer_radius)
    water_rod_cell2.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR", "CLAD", "COOLANT"],
         PropertyType.MACRO: ["MACRO_WATER_ROD_2"]*3}
    )

    return water_rod_cell1, water_rod_cell2


def add_cells_to_regular_lattice(lattice, ordered_cells, cell_pitch, translation):
    """
    add cells from the list of list of ordered_cells to the lattice geometry
    Non-fuel cells from ordered_cells are skipped, 
    all cells containted in moderator_box_elements are added last.
    
    Parameters : 
    --------------
        - lattice : glow lattice object, to represent regular cartesian lattice
        - ordered_cells : list of cells to add to regular lattice
        - cell_pitch : regular x/y-offset seperating cells (square cell side length)
        - translation : constant translation offset (cm) to specify cells positions

    Return : 
    ---------

        - lattice : glow lattice with update geometry
    """

    for row_idx in range(len(ordered_cells)):
        row_of_cells = ordered_cells[row_idx]
        for cell_idx in range(len(row_of_cells)):
            cell = row_of_cells[cell_idx]
            if "W" in cell.name:
                continue
            else:
                lattice.add_cell(cell, ((cell_idx + 1/2)*cell_pitch+translation, (row_idx + 1/2)*cell_pitch+translation,  0.0))

    return lattice


def create_assembly_box(assembly_pitch, channel_box_outer_side,channel_box_inner_side, corner_inner_radius_of_curvature):
    """
    Create the assembly box cell for GE-14 assembly
    Parameters :
    --------------
        - assembly_pitch : float, assembly pitch (cm)
        - channel_box_inner_side : float, inner side of channel box (cm)
    """
    assembly_cell = RectCell(name="out_of_assembly_moderator", height_x_width=(assembly_pitch, assembly_pitch), center=(assembly_pitch/2, assembly_pitch/2, 0.0))
    assembly_cell.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACRO_ASSEMBLY_OUT_MODERATOR"]*1}
    )
    channel_box_thickness = (channel_box_outer_side - channel_box_inner_side) / 2
    corner_outer_radius_of_curvature = corner_inner_radius_of_curvature# + channel_box_thickness

    box_cell = RectCell(name="channel_box", height_x_width=(channel_box_outer_side, channel_box_outer_side), center=(assembly_pitch/2, assembly_pitch/2, 0.0),
                        rounded_corners=[(0, corner_outer_radius_of_curvature), (1, corner_outer_radius_of_curvature),
                                         (2, corner_outer_radius_of_curvature), (3, corner_outer_radius_of_curvature)])
    box_cell.set_properties(
        {PropertyType.MATERIAL: ["CHANNEL_BOX"],
         PropertyType.MACRO: ["MACRO_CHANNEL_BOX"]*1}
    )

    coolant_intra_assembly_cell = RectCell(name="intra_assembly_coolant", height_x_width=(channel_box_inner_side, channel_box_inner_side), center=(assembly_pitch/2, assembly_pitch/2, 0.0),
                                           rounded_corners=[(0, corner_inner_radius_of_curvature), (1, corner_inner_radius_of_curvature),
                                                            (2, corner_inner_radius_of_curvature), (3, corner_inner_radius_of_curvature)])
    coolant_intra_assembly_cell.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACRO_INTRA_ASSEMBLY_COOLANT"]*1}
    )
    

    return assembly_cell, box_cell, coolant_intra_assembly_cell

if __name__ == "__main__":

    # --------------------
    # TRACKING TYPE
    # --------------------

    tracking_type = "TISO" # "TSPC"
    include_MACRO_definitions = False

    # --------------------
    # GEOMETRY PARAMETERS
    # --------------------
    # Main geometrical dimensions
    assembly_pitch = 15.24 # cm
    pin_pitch = 1.3
    gap_wide = 0.7549
    gap_narrow = 0.7549
    channel_box_thickness = 0.1651
    channel_box_corner_radius = 0.9652
    fuel_pellet_radius = 0.438
    fuel_clad_inner_radius = 0.447
    fuel_clad_outer_radius = 0.515
    water_rod_inner_radius = 1.170
    water_rod_outer_radius = 1.245

    channel_box_inner_side = 15.24 - 2* channel_box_thickness - 2* gap_wide 
    channel_box_outer_side = 15.24 - 2* gap_wide
    coolant_intra_assembly_cell = (channel_box_inner_side - 10*pin_pitch) / 2
    corner_inner_radius_of_curvature = 0.9652

    pincell_translation = gap_wide+channel_box_thickness+coolant_intra_assembly_cell
    # Define geometry
    lattice_description = [ ["ROD2",  "ROD5",  "ROD7",  "ROD7",  "ROD7",  "ROD7",  "ROD7",  "ROD7",  "ROD7", "ROD3"],
                            ["ROD5",  "ROD5", "ROD6H",  "ROD7",  "ROD7", "ROD7G",  "ROD7", "ROD7G",  "ROD7", "ROD7"],
                            ["ROD5", "ROD6H",  "ROD6",  "ROD7",  "ROD7",  "ROD7", "ROD7G",  "ROD7", "ROD7G", "ROD7"],
                            ["ROD5",  "ROD5", "ROD6H",  "WROD",  "WROD",  "ROD7",  "ROD7", "ROD7G",  "ROD7", "ROD7"],
                            ["ROD5", "ROD5G",  "ROD6",  "WROD",  "WROD",  "ROD7",  "ROD7",  "ROD7", "ROD7G", "ROD7"],
                            ["ROD5",  "ROD4", "ROD7H",  "ROD5",  "ROD7",  "WROD",  "WROD",  "ROD7",  "ROD7", "ROD7"],
                            ["ROD5",  "ROD5",  "ROD6", "ROD7G",  "ROD5",  "WROD",  "WROD",  "ROD7",  "ROD7", "ROD7"],
                            ["ROD3",  "ROD3", "ROD6K",  "ROD6", "ROD7H",  "ROD6",  "ROD6H", "ROD6", "ROD6H", "ROD7"],
                            ["ROD2",  "ROD2",  "ROD3",  "ROD5",  "ROD4", "ROD5G",  "ROD5", "ROD6H",  "ROD5", "ROD5"],
                            ["ROD1",  "ROD2",  "ROD3",  "ROD5",  "ROD5",  "ROD5",  "ROD5",  "ROD5",  "ROD5", "ROD2"],                            
                            ]    
    
    ROD_to_material = {
        "ROD1" : "UOX160",
        "ROD2" : "UOX280",
        "ROD3" : "UOX320",
        "ROD4" : "UOX360",
        "ROD5" : "UOX395",
        "ROD5G" : "UOX395_Gd8",
        "ROD6" : "UOX440",
        "ROD6H" : "UOX440_Gd6",
        "ROD6K" : "UOX440_Gd3",
        "ROD7" : "UOX490",
        "ROD7G" : "UOX490_Gd8",
        "ROD7H" : "UOX490_Gd6",
        "RODN" : "UOXNAT",
        "WROD" : "MODERATOR"
    }

    # Generate material cells 
    ordered_fuel_cells = generate_cells(lattice_desc=lattice_description, pitch=pin_pitch, C_to_mat=ROD_to_material, 
                                        fuel_rad=fuel_pellet_radius, gap_rad=fuel_clad_inner_radius, clad_rad=fuel_clad_outer_radius)
    
    # Create water rods cells
    water_rod_cell1, water_rod_cell2 = create_water_rods(pin_pitch, water_rod_inner_radius, water_rod_outer_radius)

    # Create assembly box cells

    assembly_box_cell, channel_box_cell, coolant_intra_assembly_cell = create_assembly_box(assembly_pitch=assembly_pitch, 
                                                                                    channel_box_outer_side=channel_box_outer_side,
                                                                                    channel_box_inner_side=channel_box_inner_side,
                                                                                    corner_inner_radius_of_curvature=corner_inner_radius_of_curvature)
    # --------------------
    # LATTICE CONSTRUCTION
    # --------------------
    # Build the lattice with several rings of the same cartesian cell1
    lattice = Lattice(name='GE-14 LATTICE', center=(assembly_pitch/2, assembly_pitch/2, 0.0))

    # Add assembly box cells
    lattice.add_cell(assembly_box_cell, ())
    #lattice.add_cell(channel_box_cell, ())
    lattice.add_cell(coolant_intra_assembly_cell, ())

    #lattice = add_cells_to_regular_lattice(lattice=lattice, 
    #                                    ordered_cells=ordered_fuel_cells,
    #                                    cell_pitch=pin_pitch, translation=pincell_translation)
    # Add water rods cells
    #lattice.add_cell(water_rod_cell1,(4*pin_pitch + pincell_translation, 4*pin_pitch + pincell_translation, 0.0))
    #lattice.add_cell(water_rod_cell2,(6*pin_pitch + pincell_translation, 6*pin_pitch + pincell_translation, 0.0))

    # Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
if include_MACRO_definitions:
    lattice.show(geometry_type_to_show=GeometryType.TECHNOLOGICAL, property_type_to_show=PropertyType.MACRO)
else:
    lattice.show(geometry_type_to_show=GeometryType.SECTORIZED, property_type_to_show=PropertyType.MATERIAL)

# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
    if include_MACRO_definitions:
        props = [PropertyType.MATERIAL,PropertyType.MACRO]
        output_file_name = "GE-14_lattice_TISO_MACRO"
    else:
        props = [PropertyType.MATERIAL]
        output_file_name = "GE-14_lattice_TISO"
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], f"data/glow_data/tdt_data/{output_file_name}", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=props,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
elif tracking_type == "TSPC":
    lattice.type_geo = LatticeGeometryType.RECTANGLE_SYM
    analyse_and_generate_tdt(
    [lattice], "data/glow_data/tdt_data/GE-14_lattice_TSPC", TdtSetup(GeometryType.SECTORIZED, 
                                                            property_types=[PropertyType.MATERIAL],
                                                            type_geo=LatticeGeometryType.RECTANGLE_SYM,
                                                            symmetry_type=BoundaryType.AXIAL_SYMMETRY))


