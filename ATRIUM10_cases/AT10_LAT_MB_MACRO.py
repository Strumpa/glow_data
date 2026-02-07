from glow.geometry_layouts.cells import RectCell
from glow.geometry_layouts.geometries import Rectangle
from glow.support.types import GeometryType, PropertyType, SymmetryType
from glow.geometry_layouts.lattices import Lattice
from glow.main import TdtSetup, analyse_and_generate_tdt
from glow.interface.geom_interface import *
from glow.support.types import *


def generate_moderator_box_cells_GEO(bounding_box_length, inner_side_length, outer_side_length, number_subdivisions, translation=(0.0,0.0,0.0)):
    box_elements = []
    pitch = bounding_box_length / number_subdivisions
    ## Compute sub-meshing points
    x1 = (bounding_box_length - outer_side_length)/2
    box_thickness = (outer_side_length - inner_side_length)/2
    print("Moderator box thickness:", box_thickness)
    x2 = x1 + box_thickness
    x3 = x2 + (inner_side_length)
    x4 = x3 + box_thickness
    
    ### MACROS order : 
    ## x-increasing/y-increasing DRAGON5 convention
    # ie start from bottom left corner
    # MACROW1 MACROW2 MACROW3 
    # MACROW4 MACROW5 MACROW6 
    # MACROW7 MACROW8 MACROW9

    ### Do MODERATOR regions first
    # Central region : 
    central_region = RectCell(name="central_region", height_x_width=(pitch, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    central_region.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW5"]}
    )
    box_elements.append(central_region)
    
    # Moderator in lower left corner
    moderator_ll = RectCell(name="moderator_ll", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_ll.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(moderator_ll)
    
    # Moderator region in bottom right corner
    moderator_br = RectCell(name="moderator_br", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(moderator_br)
    
    # Moderator in top left corner
    moderator_tl = RectCell(name="moderator_tl", height_x_width=(pitch - x2, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(moderator_tl)
    
    # Moderator in bottom middle edge
    moderator_bm = RectCell(name="moderator_bm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_bm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW2"]}
    )
    box_elements.append(moderator_bm)
    
    # Moderator in top right corner
    moderator_tr = RectCell(name="moderator_tr", height_x_width=(pitch - x2, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(moderator_tr)
    
    # Moderator in top middle edge
    moderator_tm = RectCell(name="moderator_tm", height_x_width=(pitch - x2, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    moderator_tm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW8"]}
    )
    box_elements.append(moderator_tm)
    
    # Moderator left middle edge
    moderator_lm = RectCell(name="moderator_lm", height_x_width=(pitch, pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    moderator_lm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW4"]}
    )
    box_elements.append(moderator_lm)
    
    # Moderator right middle edge
    moderator_rm = RectCell(name="moderator_rm", height_x_width=(pitch, pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    moderator_rm.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR"],
         PropertyType.MACRO: ["MACROW6"]}
    )
    box_elements.append(moderator_rm)
    
    ## Corners
    # BOX ELEMENTS OF MACROW1 : lower left corner 
    # BOX LL corner
    box_corner_ll = RectCell(name="box_corner_ll", height_x_width=(box_thickness, box_thickness), center=(x1+(box_thickness)/2+translation[0], x1+(box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner_ll.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(box_corner_ll)
    
    # rectangular box to the right of box corner
    box_right = RectCell(name="box_right", height_x_width=(box_thickness,pitch-x2), center=(x2 + (pitch - x2)/2+translation[0], x1+box_thickness/2+translation[1], 0.0+translation[2]))
    box_right.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(box_right)
    
    # rectangular box above coolant corner
    box_top = RectCell(name="box_top", height_x_width=(pitch - x2, box_thickness), center=(x1 + box_thickness/2+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_top.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(box_top)

    # box corner on bottom right
    box_corner_br = RectCell(name="box_corner_br", height_x_width=(box_thickness, box_thickness), center=(bounding_box_length - x1 - (box_thickness)/2+translation[0], x1+(box_thickness)/2+translation[1], 0.0+translation[2]))
    #  
    box_corner_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(box_corner_br)

    # rectangular box left of box corner
    box_left_br = RectCell(name="box_left_br", height_x_width=(box_thickness,pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], x1 + box_thickness/2+translation[1], 0.0+translation[2]))
    box_left_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(box_left_br)
    # rectangular box above box corner
    box_top_br = RectCell(name="box_top_br", height_x_width=(pitch - x2, box_thickness), center=(bounding_box_length - box_thickness/2-x1+translation[0], x2 + (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_top_br.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(box_top_br)

    # BOX elements of MACROW7 : TOP LEFT
    # box covering coolant corner
    box_corner_tl = RectCell(name="box_corner_tl", height_x_width=(box_thickness, box_thickness), center=(x1+(box_thickness)/2+translation[0], bounding_box_length - x1 - (box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(box_corner_tl)
    # rectangular box to the right of box corner
    box_right_tl = RectCell(name="box_right_tl", height_x_width=(box_thickness,pitch - x2), center=(x2 + (pitch - x2)/2+translation[0], bounding_box_length - x1 - box_thickness/2+translation[1], 0.0+translation[2]))
    box_right_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(box_right_tl)
    
    # rectangular box below box corner
    box_bottom_tl = RectCell(name="box_bottom_tl", height_x_width=(pitch - x2, box_thickness), center=(x1 + box_thickness/2+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_bottom_tl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(box_bottom_tl)
    
    ## BOX ELEMENTS OF MACROW9 : TOP RIGHT CORNER
    # box covering coolant corner
    box_corner_tr = RectCell(name="box_corner_tr", height_x_width=(box_thickness, box_thickness), center=(bounding_box_length - x1 - (box_thickness)/2+translation[0], bounding_box_length - x1 - (box_thickness)/2+translation[1], 0.0+translation[2]))
    box_corner_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(box_corner_tr)
    # rectangular box left of box corner
    box_left_tr = RectCell(name="box_left_tr", height_x_width=(box_thickness,pitch - x2), center=(bounding_box_length - x2 - (pitch - x2)/2+translation[0], bounding_box_length - x1 - box_thickness/2+translation[1], 0.0+translation[2]))
    box_left_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(box_left_tr)
    # rectangular box below box corner
    box_bottom_tr = RectCell(name="box_bottom_tr", height_x_width=(pitch - x2, box_thickness), center=(bounding_box_length - box_thickness/2 - x1+translation[0], bounding_box_length - x2 - (pitch - x2)/2+translation[1], 0.0+translation[2]))
    box_bottom_tr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(box_bottom_tr)
    
    ## central-side MACROS: 2, 4, 6, 8
    # box edge center bottom
    box_edge_cb = RectCell(name="box_edge_cb", height_x_width=(box_thickness, pitch), center=(bounding_box_length/2+translation[0], x1 + box_thickness/2+translation[1], 0.0+translation[2]))
    box_edge_cb.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW2"]}
    )
    box_elements.append(box_edge_cb)
    # box edge center top
    box_edge_ct = RectCell(name="box_edge_ct", height_x_width=(box_thickness, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x1 - box_thickness/2+translation[1], 0.0+translation[2]))
    box_edge_ct.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW8"]}
    )
    box_elements.append(box_edge_ct)
    # box edge center left
    box_edge_cl = RectCell(name="box_edge_cl", height_x_width=(pitch, box_thickness), center=(x1 + box_thickness/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_edge_cl.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW4"]}
    )
    box_elements.append(box_edge_cl)
    # box edge center right
    box_edge_cr = RectCell(name="box_edge_cr", height_x_width=(pitch, box_thickness), center=(bounding_box_length - x1 - box_thickness/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    box_edge_cr.set_properties(
        {PropertyType.MATERIAL: ["MODERATOR_BOX"],
         PropertyType.MACRO: ["MACROW6"]}
    )
    box_elements.append(box_edge_cr)
    
    ## Coolant around moderator box regions
    # Top left coolant corner : MACROW7
    top_left_corner = RectCell(name="top_left_corner", height_x_width=(x1, x1), center=(x1/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    top_left_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(top_left_corner)

    top_right_corner = RectCell(name="top_right_corner", height_x_width=(x1, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    top_right_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(top_right_corner)

    bottom_left_corner = RectCell(name="bottom_left_corner", height_x_width=(x1, x1), center=(x1/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    bottom_left_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(bottom_left_corner)

    bottom_right_corner = RectCell(name="bottom_right_corner", height_x_width=(x1, x1), center=(bounding_box_length - x1/2+translation[0], x1/2+translation[1], 0.0+translation[2]))
    bottom_right_corner.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(bottom_right_corner)

    # Top center rectangle : MACROW8
    top_center_rectangle = RectCell(name="top_center_rectangle", height_x_width=(x1, pitch), center=(bounding_box_length/2+translation[0], bounding_box_length - x1/2+translation[1], 0.0+translation[2]))
    top_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW8"]}
    )
    box_elements.append(top_center_rectangle)

    # Bottom center rectangle : MACROW2
    bottom_center_rectangle = RectCell(name="bottom_center_rectangle", height_x_width=(x1, pitch), center=(bounding_box_length/2+translation[0], x1/2+translation[1], 0.0+translation[2])) 
    bottom_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW2"]}
    )
    box_elements.append(bottom_center_rectangle)

    # Left center rectangle :
    left_center_rectangle = RectCell(name="left_center_rectangle", height_x_width=(pitch, x1), center=(x1/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    left_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW4"]}
    )
    box_elements.append(left_center_rectangle)

    # Right center rectangle :
    right_center_rectangle = RectCell(name="right_center_rectangle", height_x_width=(pitch, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length/2+translation[1], 0.0+translation[2]))
    right_center_rectangle.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW6"]}
    )
    box_elements.append(right_center_rectangle)
    
    ## Filling small rectangles with coolant : 
    # horizontal rect from bottom left corner to bottom center rectangle
    coolant_bl_to_bc = RectCell(name="coolant_bl_to_bc", height_x_width=(x1, pitch - x1), center=(x1 + (pitch - x1)/2+translation[1], x1/2+translation[0],  0.0+translation[2]))
    coolant_bl_to_bc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(coolant_bl_to_bc)

    # horizontal rect from bottom right corner to bottom center rectangle
    coolant_br_to_bc = RectCell(name="coolant_br_to_bc", height_x_width=(x1, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2+translation[1], x1/2+translation[0],  0.0+translation[2]))
    coolant_br_to_bc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(coolant_br_to_bc)

    # horizontal rect from top left corner to top center rectangle
    coolant_tl_to_tc = RectCell(name="coolant_tl_to_tc", height_x_width=(x1, pitch - x1), center=(x1 + (pitch - x1)/2+translation[1], bounding_box_length - x1/2+translation[0],  0.0+translation[2]))
    coolant_tl_to_tc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(coolant_tl_to_tc)
    # horizontal rect from top right corner to top center rectangle
    coolant_tr_to_tc = RectCell(name="coolant_tr_to_tc", height_x_width=(x1, pitch - x1), center=(bounding_box_length - x1 - (pitch - x1)/2+translation[1], bounding_box_length - x1/2+translation[0],  0.0+translation[2]))
    coolant_tr_to_tc.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(coolant_tr_to_tc)
    # vertical rect from bottom left corner to left center rectangle
    coolant_bl_to_cl = RectCell(name="coolant_bl_to_cl", height_x_width=(pitch - x1, x1), center=(x1/2+translation[0], x1 + (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_bl_to_cl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW1"]}
    )
    box_elements.append(coolant_bl_to_cl)
    # vertical rect from bottom right corner to right center rectangle
    coolant_br_to_cr = RectCell(name="coolant_br_to_cr", height_x_width=(pitch - x1, x1), center=(bounding_box_length - x1/2+translation[0], x1 + (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_br_to_cr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW3"]}
    )
    box_elements.append(coolant_br_to_cr)
    # vertical rect from top left corner to left center rectangle
    coolant_tl_to_cl = RectCell(name="coolant_tl_to_cl", height_x_width=(pitch - x1, x1), center=(x1/2+translation[0], bounding_box_length - x1 - (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_tl_to_cl.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW7"]}
    )
    box_elements.append(coolant_tl_to_cl)
    # vertical rect from top right corner to right center rectangle
    coolant_tr_to_cr = RectCell(name="coolant_tr_to_cr", height_x_width=(pitch - x1, x1), center=(bounding_box_length - x1/2+translation[0], bounding_box_length - x1 - (pitch - x1)/2+translation[1],  0.0+translation[2]))
    coolant_tr_to_cr.set_properties(
        {PropertyType.MATERIAL: ["COOLANT"],
         PropertyType.MACRO: ["MACROW9"]}
    )
    box_elements.append(coolant_tr_to_cr)

    return box_elements


def add_cells_to_regular_lattice(lattice, ordered_cells, moderator_box_elements, cell_pitch, translation):
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
            print(f"Adding cell {cell} at position ({row_idx}, {cell_idx})")
            print(f"x coord : {(cell_idx + 1/2)*cell_pitch} cm")
            print(f"y coord : {(row_idx + 1/2)*cell_pitch} cm")
            if cell.name[0] == "W":
                continue
            else:
                lattice.add_cell(cell, ((cell_idx + 1/2)*cell_pitch+translation, (row_idx + 1/2)*cell_pitch+translation,  0.0))
    for element in moderator_box_elements:
        lattice.add_cell(element, ())

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

            
tracking_type = "TISO" # "TSPC"

pitch = 1.295
assembly_pitch, water_gap_width = 15.24, 0.75 # Assembly pitch and water gap thickness
channel_box_outer_side, channel_box_inner_side, channel_box_thickness = 13.74, 13.4, 0.17 # Channel box outer, inner sides and thickness
moder_box_outer_side, moder_box_inner_side, moder_box_thickness = 3.5, 3.34, 0.08 # Moderating box outer, inner sides and thickness
intra_assembly_water_gap_width = (channel_box_inner_side - 10*pitch)/2 # Intra-assembly water gap thickness
number_subdivisions = 3

pincell_translation = water_gap_width+channel_box_thickness+intra_assembly_water_gap_width
water_box_bottom_corner = (4*pitch+pincell_translation, 4*pitch+pincell_translation, 0.0)
print("Water box bottom corner:", water_box_bottom_corner)


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
ordered_fuel_cells = generate_cells(lattice_desc=lattice_description, pitch=pitch, C_to_mat=C_to_MAT)
box_elements = generate_moderator_box_cells_GEO(number_subdivisions*pitch, moder_box_inner_side, moder_box_outer_side, number_subdivisions, water_box_bottom_corner)
# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = Lattice(name='ATRIUM-10 Lattice - with moderator box', center=(assembly_pitch/2, assembly_pitch/2, 0.0))


lattice = add_cells_to_regular_lattice(lattice=lattice, 
                                       ordered_cells=ordered_fuel_cells, 
                                       moderator_box_elements=box_elements,
                                       cell_pitch=pitch, translation=pincell_translation)

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one

# Apply the eighth symmetry type to the cartesian lattice
lattice.apply_symmetry(SymmetryType.FULL)
# Show the resulting layout with the 'MATERIAL' colorset
lattice.show(PropertyType.MATERIAL)
lattice.show(PropertyType.MACRO)


# Perform the geometry analysis and export the TDT file of the surface
# geometry
if tracking_type == "TISO":
    lattice.type_geo = LatticeGeometryType.ISOTROPIC
    analyse_and_generate_tdt(
    [lattice], "data/glow_data/tdt_data/AT10_LAT_MB_TISO_MACRO", TdtSetup(GeometryType.SECTORIZED, 
                                                        property_types=[PropertyType.MATERIAL,PropertyType.MACRO],
                                                        type_geo=LatticeGeometryType.ISOTROPIC,
                                                        symmetry_type=BoundaryType.AXIAL_SYMMETRY))