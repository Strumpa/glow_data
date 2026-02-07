from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *

class CAR2D():
    def __init__(self, name, nx, ny, meshx, meshy, materials):
        """
        Definition of a 2D cartesian geometry in the x-y plane according to the DRAGON5 definition
        :param name: name of the geometry, used as MACRO PropertyType
        :param lx: number of cells in x direction
        :param ly: number of cells in y direction
        :param meshx: mesh in x direction : array of nx+1 values, bounds to the cells
        :param meshy: mesh in y direction : array of ny+1 values, bounds to the cells
        :param materials: list of material names (str) of length nx*ny, ordered in x-increasing/y-increasing DRAGON5 convention

        """
        self.type = "CAR2D"
        self.nameMACRO = name
        self.nx = nx
        self.ny = ny
        self.meshx = meshx
        self.meshy = meshy

        self.xmin = self.meshx[0]
        self.xmax = self.meshx[-1]
        self.ymin = self.meshy[0]
        self.ymax = self.meshy[-1]

        self.origin = [self.xmin, self.ymin] # Origin of the geometry, lower left corner, assumung z invariance

        self.number_of_regions = self.nx * self.ny

        self.materials = materials

    def create_GLOW_MACRO(self):
        """
        Create a list of RectCell objects corresponding to the regions defined in the CAR2D object
        Iterate over mesh points and materials to create the correpsonding cells, 
        Use CAR2D name to define the MACRO PropertyType
        """

        regions = []
        for i in range(self.nx):
            for j in range(self.ny):
                cell_name = f"{self.nameMACRO}_cell_{i}_{j}"
                x_width = self.meshx[i+1] - self.meshx[i]
                y_width = self.meshy[j+1] - self.meshy[j]
                center_x = self.meshx[i] + x_width/2
                center_y = self.meshy[j] + y_width/2
                cell = RectCell(name=cell_name, height_x_width=(y_width, x_width), center=(center_x, center_y, 0.0))
                cell.set_properties(
                    {PropertyType.MATERIAL: [self.materials[j*self.nx + i]],
                     PropertyType.MACRO: [self.nameMACRO]}
                )
                regions.append(cell)
        return regions
    
    def split_into_GLOW_MACROS(self, splitx, splity):
        """
        Split the CAR2D into sub-geometries, representing individual MACROS, 
        splitx : array representing the number of subdivisions in each element along the x direction
        splity : array representing the number of subdivisions in each element along the y direction
        splitx/y arrays of length nx-1/ny-1 respectively
        """
        # recompute mesh for split macros before creating RectCells with individual MACROS. 

        regions = []
        split_xmesh = self.get_split_mesh(self.meshx, splitx)
        split_ymesh = self.get_split_mesh(self.meshy, splity)
        print("Original xmesh:", self.meshx)
        print("Original ymesh:", self.meshy)
        print("Number of x subdivisions:", splitx)
        print("Number of y subdivisions:", splity)
        print("Split xmesh:", split_xmesh)
        print("Split ymesh:", split_ymesh)

        for i in range(len(split_xmesh)-1):
            for j in range(len(split_ymesh)-1):
                # Find which original cell this (i,j) belongs to
                # original cell index in x direction
                orig_i = None
                for ix in range(self.nx):
                    if split_xmesh[i] >= self.meshx[ix] and split_xmesh[i+1] <= self.meshx[ix+1]:
                        orig_i = ix
                        break
                # original cell index in y direction
                orig_j = None
                for jy in range(self.ny):
                    if split_ymesh[j] >= self.meshy[jy] and split_ymesh[j+1] <= self.meshy[jy+1]:
                        orig_j = jy
                        break
                if orig_i is None or orig_j is None:
                    raise ValueError("Split mesh points do not align with original mesh.")
                
                cell_name = f"{self.nameMACRO}_cell_{i}_{j}"
                if len(split_xmesh) == len(self.meshx): # 1 x-subdivision
                    # initial CAR2D is being split in y-direction
                    # create a new macro name for every new subdivision along the y-direction
                    macro_name = f"{self.nameMACRO}y{j}"
                    print(f"adding cell name = {cell_name} to MACRO with name {macro_name}")
                elif len(split_ymesh) == len(self.meshy): # one y-subdivision,
                    # create new macro name for every new subdivision along the x-direction
                    macro_name = f"{self.nameMACRO}x{i}"
                    print(f"adding cell name = {cell_name} to MACRO with name {macro_name}")
                else: 
                    macro_name = f"{self.nameMACRO}{i}{j}"
                    print(f"adding cell name = {cell_name} to MACRO with name {macro_name}")
                    print(f"In splitx and splity > 1 case, assigning unique MACRO name per cell: {macro_name}")
                    return regions
                x_width = split_xmesh[i+1] - split_xmesh[i]
                y_width = split_ymesh[j+1] - split_ymesh[j]
                center_x = split_xmesh[i] + x_width/2
                center_y = split_ymesh[j] + y_width/2
                cell = RectCell(name=cell_name, height_x_width=(y_width, x_width), center=(center_x, center_y, 0.0))
                cell.set_properties(
                    {PropertyType.MATERIAL: [self.materials[orig_j*self.nx + orig_i]],
                     PropertyType.MACRO: [macro_name]}
                )
                regions.append(cell)
        return regions
        

    def get_split_mesh(self, mesh_to_split, n_split_array):
        """
        Create a split mesh by subdividing each element of the input mesh according to the number of subdivisions specified in n_split_array
        """
        split_mesh = [mesh_to_split[0]]
        for i in range(len(n_split_array)):
            x_start = mesh_to_split[i]
            x_end = mesh_to_split[i+1]
            n_splits = n_split_array[i]
            delta_x = (x_end - x_start) / n_splits
            for j in range(1, n_splits + 1):
                split_mesh.append(x_start + j * delta_x)
        return split_mesh


def build_moderation_box(bounding_box_length, inner_side_length, outer_side_length, pitch, translation=(0.0,0.0,0.0)):
    box_elements = []
    ## Compute sub-meshing points
    x1 = (bounding_box_length - outer_side_length)/2
    box_thickness = (outer_side_length - inner_side_length)/2
    x2 = x1 + box_thickness
    x3 = x2 + (inner_side_length)
    x4 = x3 + box_thickness
    ## Generate a total of 9 CAR2D to represent the moderation box MACROS

    # Bottom left corner CAR2D
    bl_xmesh = [0.0+translation[0], x1+translation[0], x2+translation[0], pitch+translation[0]]
    bl_ymesh = [0.0+translation[1], x1+translation[1], x2+translation[1], pitch+translation[1]]
    bl_materials = ["COOLANT", "COOLANT", "COOLANT",
                    "COOLANT", "MODERATOR_BOX", "MODERATOR_BOX",
                    "COOLANT", "MODERATOR_BOX", "MODERATOR"]
    bl_car2d = CAR2D(name="MBL_CORNER", nx=3, ny=3, meshx=bl_xmesh, meshy=bl_ymesh,
                     materials=bl_materials)
    bl_elements = bl_car2d.create_GLOW_MACRO()
    box_elements.extend(bl_elements)
    # Bottom edge CAR2D
    bottom_xmesh = [pitch+translation[0], 2*pitch+translation[0]]
    bottom_ymesh = [0.0+translation[1], x1+translation[1], x2+translation[1], pitch+translation[1]]
    bottom_materials = ["COOLANT", "MODERATOR_BOX", "MODERATOR"]
    bottom_car2d = CAR2D(name="MBOTTOM_EDGE", nx=1, ny=3, meshx=bottom_xmesh, meshy=bottom_ymesh,
                         materials=bottom_materials)
    bottom_elements = bottom_car2d.create_GLOW_MACRO()
    box_elements.extend(bottom_elements)
    # Bottom right corner CAR2D
    br_xmesh = [2*pitch + translation[0], x3+translation[0], x4 + translation[0], 3*pitch +translation[0]]
    br_ymesh = [0.0 + translation[1], x1+translation[1], x2+translation[1], pitch+translation[1]]
    br_materials = ["COOLANT", "COOLANT", "COOLANT",
                    "MODERATOR_BOX", "MODERATOR_BOX", "COOLANT",
                    "MODERATOR", "MODERATOR_BOX", "COOLANT"]
    br_car2d = CAR2D(name="MBR_CORNER", nx=3, ny=3, meshx=br_xmesh, meshy=br_ymesh,
                     materials=br_materials)
    br_elements = br_car2d.create_GLOW_MACRO()
    box_elements.extend(br_elements)

    # Left edge CAR2D
    left_xmesh = [0.0 + translation[0], x1+translation[0], x2+translation[0], pitch+translation[0]]
    left_ymesh = [pitch+translation[1], 2*pitch+translation[1]]
    left_materials = ["COOLANT", "MODERATOR_BOX", "MODERATOR"]
    left_car2d = CAR2D(name="MLEFT_EDGE", nx=3, ny=1, meshx=left_xmesh, meshy=left_ymesh,
                       materials=left_materials)
    left_elements = left_car2d.create_GLOW_MACRO()
    box_elements.extend(left_elements)
    # Right edge CAR2D
    right_xmesh = [2*pitch + translation[0], x3+translation[0], x4 + translation[0], 3*pitch +translation[0]]
    right_ymesh = [pitch+translation[1], 2*pitch+translation[1]]
    right_materials = ["MODERATOR", "MODERATOR_BOX", "COOLANT"]
    right_car2d = CAR2D(name="MRIGHT_EDGE", nx=3, ny=1, meshx=right_xmesh, meshy=right_ymesh,
                        materials=right_materials)
    right_elements = right_car2d.create_GLOW_MACRO()
    box_elements.extend(right_elements)
    # Top left corner CAR2D
    tl_xmesh = [0.0+translation[0], x1+translation[0], x2+translation[0], pitch+translation[0]]
    tl_ymesh = [2*pitch+translation[1], x3+translation[1], x4+translation[1], 3*pitch+translation[1]]
    tl_materials = ["COOLANT", "MODERATOR_BOX", "MODERATOR",
                    "COOLANT", "MODERATOR_BOX", "MODERATOR_BOX",
                    "COOLANT", "COOLANT", "COOLANT"]
    tl_car2d = CAR2D(name="MTL_CORNER", nx=3, ny=3, meshx=tl_xmesh, meshy=tl_ymesh,
                     materials=tl_materials)
    tl_elements = tl_car2d.create_GLOW_MACRO()
    box_elements.extend(tl_elements)
    # Top edge CAR2D
    top_xmesh = [pitch+translation[0], 2*pitch+translation[0]]
    top_ymesh = [2*pitch+translation[1], x3+translation[1], x4+translation[1], 3*pitch+translation[1]]
    top_materials = ["MODERATOR", "MODERATOR_BOX", "COOLANT"]
    top_car2d = CAR2D(name="MTOP_EDGE", nx=1, ny=3, meshx=top_xmesh, meshy=top_ymesh,
                        materials=top_materials)
    top_elements = top_car2d.create_GLOW_MACRO()
    box_elements.extend(top_elements)
    # Top right corner CAR2D
    tr_xmesh = [2*pitch + translation[0], x3+translation[0], x4 + translation[0], 3*pitch +translation[0]]
    tr_ymesh = [2*pitch+translation[1], x3+translation[1], x4+translation[1], 3*pitch+translation[1]]
    tr_materials = ["MODERATOR", "MODERATOR_BOX", "COOLANT",
                    "MODERATOR_BOX", "MODERATOR_BOX", "COOLANT",
                    "COOLANT", "COOLANT", "COOLANT"]
    tr_car2d = CAR2D(name="MTR_CORNER", nx=3, ny=3, meshx=tr_xmesh, meshy=tr_ymesh,
                     materials=tr_materials)
    tr_elements = tr_car2d.create_GLOW_MACRO()
    box_elements.extend(tr_elements)

    # Central CAR2D
    center_xmesh = [pitch+translation[0], 2*pitch+translation[0]]
    center_ymesh = [pitch+translation[1], 2*pitch+translation[1]]
    center_materials = ["MODERATOR"]
    center_car2d = CAR2D(name="MCENTER", nx=1, ny=1, meshx=center_xmesh, meshy=center_ymesh,
                         materials=center_materials)
    center_elements = center_car2d.create_GLOW_MACRO()
    box_elements.extend(center_elements)    
                
    #test_lattice.show(PropertyType.MATERIAL)

    return box_elements


def build_assembly_box(assembly_pitch, channel_box_outer_side, channel_box_inner_side, cell_pitch, number_subdivision):
    """
    Create geometrical elements describing the assembly channel box surrounding pincell lattice,
    
    :param assembly_pitch (cm) : assmebly pitch : outer channel box + water on both sides. 
    :param channel_box_outer_side (cm): outer side length of channel box
    :param channel_box_inner_side (cm): inner side length of channel box
    :param cell_pitch (cm): pincell pitch for lattice definition
    :param number_subdivisions (cm): (minimal) number of subdivisions / pincells per side lattice
    """

    channel_box_thickness = (channel_box_outer_side - channel_box_inner_side) / 2
    LLat = number_subdivision * cell_pitch
    inner_assembly_coolant_thickness = (channel_box_inner_side - LLat) / 2
    water_blade_thickness = (assembly_pitch - channel_box_outer_side) / 2

    all_elements = []

    ### Bottom left corner CAR2D : 
    bottom_left_corner_xmesh = [0.0, water_blade_thickness, water_blade_thickness + channel_box_thickness, water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness]
    bottom_left_corner_ymesh = [0.0, water_blade_thickness, water_blade_thickness + channel_box_thickness, water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness]
    bottom_left_corner_materials = ["MODERATOR", "MODERATOR", "MODERATOR", 
                                    "MODERATOR", "CHANNEL_BOX", "CHANNEL_BOX", 
                                    "MODERATOR", "CHANNEL_BOX", "COOLANT"]
    bottom_left_corner_car2d = CAR2D(name="BLCORNER", nx=3, ny=3, meshx=bottom_left_corner_xmesh, meshy=bottom_left_corner_ymesh,
                                     materials=bottom_left_corner_materials)
    blcorner_elements = bottom_left_corner_car2d.create_GLOW_MACRO()
    all_elements.extend(blcorner_elements)
    ### Bottom right corner CAR2D :
    bottom_right_corner_xmesh = [assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness, assembly_pitch - water_blade_thickness, assembly_pitch]
    bottom_right_corner_ymesh = [0.0, water_blade_thickness, water_blade_thickness + channel_box_thickness, water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness]
    bottom_right_corner_materials = ["MODERATOR", "MODERATOR", "MODERATOR",
                                     "CHANNEL_BOX", "CHANNEL_BOX", "MODERATOR",
                                     "COOLANT", "CHANNEL_BOX", "MODERATOR"]
    bottom_right_corner_car2d = CAR2D(name="BRCORNER", nx=3, ny=3, meshx=bottom_right_corner_xmesh, meshy=bottom_right_corner_ymesh,
                                        materials=bottom_right_corner_materials)
    brcorner_elements = bottom_right_corner_car2d.create_GLOW_MACRO()
    all_elements.extend(brcorner_elements)  

    ### Top left corner CAR2D :
    top_left_corner_xmesh = [0.0, water_blade_thickness, water_blade_thickness + channel_box_thickness, water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness]
    top_left_corner_ymesh = [assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness, assembly_pitch - water_blade_thickness, assembly_pitch]
    top_left_corner_materials = ["MODERATOR", "CHANNEL_BOX", "COOLANT",
                                 "MODERATOR", "CHANNEL_BOX", "CHANNEL_BOX",
                                    "MODERATOR", "MODERATOR", "MODERATOR"]
    top_left_corner_car2d = CAR2D(name="TLCORNER", nx=3, ny=3, meshx=top_left_corner_xmesh, meshy=top_left_corner_ymesh,
                                        materials=top_left_corner_materials)
    tlcorner_elements = top_left_corner_car2d.create_GLOW_MACRO()
    all_elements.extend(tlcorner_elements)

    ### Top right corner CAR2D :
    top_right_corner_xmesh = [assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness, assembly_pitch - water_blade_thickness, assembly_pitch]
    top_right_corner_ymesh = [assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness, assembly_pitch - water_blade_thickness, assembly_pitch]
    top_right_corner_materials = ["COOLANT", "CHANNEL_BOX", "MODERATOR",
                                  "CHANNEL_BOX", "CHANNEL_BOX", "MODERATOR",
                                    "MODERATOR", "MODERATOR", "MODERATOR"]
    top_right_corner_car2d = CAR2D(name="TRCORNER", nx=3, ny=3, meshx=top_right_corner_xmesh, meshy=top_right_corner_ymesh,
                                        materials=top_right_corner_materials)
    trcorner_elements = top_right_corner_car2d.create_GLOW_MACRO()
    all_elements.extend(trcorner_elements)

    # bottom moderator+box+coolant CAR2D
    bottom_xmesh = [water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness]
    bottom_ymesh = [0.0, water_blade_thickness, water_blade_thickness + channel_box_thickness, water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness]
    bottom_materials = ["MODERATOR", "CHANNEL_BOX", "COOLANT"]
    bottom_car2d = CAR2D(name="BOTTOM_EDGE", nx=1, ny=3, meshx=bottom_xmesh, meshy=bottom_ymesh,
                                        materials=bottom_materials)
    bottom_elements = bottom_car2d.split_into_GLOW_MACROS(splitx=[10], splity=[1,1,1])
    all_elements.extend(bottom_elements)

    # top moderator+box+coolant CAR2D
    top_xmesh = [water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness]
    top_ymesh = [assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness, assembly_pitch - water_blade_thickness , assembly_pitch]
    top_materials = ["COOLANT", "CHANNEL_BOX", "MODERATOR"]
    top_car2d = CAR2D(name="TOP_EDGE", nx=1, ny=3, meshx=top_xmesh, meshy=top_ymesh,
                                        materials=top_materials)
    top_elements = top_car2d.split_into_GLOW_MACROS(splitx=[10], splity=[1,1,1])
    all_elements.extend(top_elements)

    # left moderator+box+coolant CAR2D
    left_xmesh = [0.0, water_blade_thickness, water_blade_thickness + channel_box_thickness, water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness]
    left_ymesh = [water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness]
    left_materials = ["MODERATOR", "CHANNEL_BOX", "COOLANT"]
    left_car2d = CAR2D(name="LEFT_EDGE", nx=3, ny=1, meshx=left_xmesh, meshy=left_ymesh,
                                        materials=left_materials)
    left_elements = left_car2d.split_into_GLOW_MACROS(splitx=[1,1,1], splity=[10])
    all_elements.extend(left_elements)
    # right moderator+box+coolant CAR2D
    right_xmesh = [assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness, assembly_pitch - water_blade_thickness, assembly_pitch]
    right_ymesh = [water_blade_thickness + channel_box_thickness + inner_assembly_coolant_thickness, assembly_pitch - water_blade_thickness - channel_box_thickness - inner_assembly_coolant_thickness]
    right_materials = ["COOLANT", "CHANNEL_BOX", "MODERATOR"]
    right_car2d = CAR2D(name="RIGHT_EDGE", nx=3, ny=1, meshx=right_xmesh, meshy=right_ymesh,
                                        materials=right_materials)
    right_elements = right_car2d.split_into_GLOW_MACROS(splitx=[1,1,1], splity=[10])
    all_elements.extend(right_elements)

    
    
    ## - describe the remaining corner elements
    ## - use split to submesh moderator and coolant elements to generate : 
    #       - geometry for IC method.
    #       - finely meshed geometry for MOC. 

    return all_elements


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
            if cell.name[0] == "W":
                continue
            else:
                lattice.add_cell(cell, ((cell_idx + 1/2)*cell_pitch+translation, (row_idx + 1/2)*cell_pitch+translation,  0.0))

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
            tmp_cell = RectCell(name=cell_id, height_x_width=(pitch, pitch), center=(pitch/2, pitch/2, 0.0))
            if cell_id in Gd_cells:
                mat_name = C_to_mat[cell_id]
                radii = [0.19834, 0.28049, 0.34353, 0.39668, 0.43227, 0.4435, 0.4520, 0.5140]
            elif cell_id[0] == "C":
                mat_name = C_to_mat[cell_id]
                radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
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


# --------------------
# TRACKING TYPE
# --------------------

tracking_type = "TISO" # "TSPC"
include_MACRO_definitions = False

# --------------------
# GEOMETRY PARAMETERS
# --------------------
    
pitch = 1.295

assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness

lattice_side_length = 10*pitch


pincell_translation = water_gap_width+channel_box_thickness+intra_assembly_water_gap_width
water_box_bottom_corner = (4*pitch+pincell_translation, 4*pitch+pincell_translation, 0.0)

# Create elements of moderation box : 
number_subdivisions = 3
mode_box_elements = build_moderation_box(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, pitch, water_box_bottom_corner)

# Create Assembly box elements
assembly_box_elements = build_assembly_box(assembly_pitch, channel_box_outer_side, channel_box_inner_side, pitch, 10)

# --------------------
# LATTICE CELLS GENERATION
# --------------------
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
ordered_fuel_cells = generate_cells(lattice_desc=lattice_description, pitch=pitch, C_to_mat=C_to_MAT)
# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='ATRIUM-10 ASSEMBLY', center=(assembly_pitch/2, assembly_pitch/2, 0.0))


lattice = add_cells_to_regular_lattice(lattice=lattice, 
                                       ordered_cells=ordered_fuel_cells,
                                       cell_pitch=pitch, translation=pincell_translation)


for element in mode_box_elements:
    lattice.add_cell(element, ())
for element in assembly_box_elements:
    lattice.add_cell(element, ())

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
        output_file_name = "AT10_assembly_TISO_MACRO"
    else:
        props = [PropertyType.MATERIAL]
        output_file_name = "AT10_assembly_TISO"
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], f"data/glow_data/tdt_data/{output_file_name}", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=props,
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))
elif tracking_type == "TSPC":
    lattice.type_geo = LatticeGeometryType.RECTANGLE_SYM
    analyse_and_generate_tdt(
    [lattice], "data/glow_data/tdt_data/AT10_assembly_TSPC", TdtSetup(GeometryType.SECTORIZED, 
                                                            property_types=[PropertyType.MATERIAL],
                                                            type_geo=LatticeGeometryType.RECTANGLE_SYM,
                                                            symmetry_type=BoundaryType.AXIAL_SYMMETRY))