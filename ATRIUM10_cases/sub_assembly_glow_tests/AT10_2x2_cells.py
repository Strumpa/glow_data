from glow.geometry_layouts.cells import CartesianCell
from glow.geometry_layouts.geometries import Circle, Rectangle
from glow.geometry_layouts.lattices import Lattice, CartesianLattice
from glow.geometry_layouts.layouts import Region
from glow.interface.geom_entities import wrap_shape
from glow.interface.geom_interface import *
from glow.main import TdtSetup, export_layout_to_tdt
from glow.support.types import GeometryType, LayoutGeometryType, PropertyType, \
    SymmetryType


tracking_type = "TISO" # "TSPC"
pitch = 1.295
# Build the cell1's geometry layout by adding three circular regions
# Build the geometry layout of the cell by adding three circular regions, from
# external to internal
radii = [0.313602, 0.396678, 0.43227, 0.4435, 0.4520, 0.5140]
materials_c1 = ["24UOX", "24UOX", "24UOX", "24UOX", "GAP", "CLAD"]
cell1 = CartesianCell(
    name="Cartesian cell", base_props={PropertyType.MATERIAL: "COOLANT"},
    width_height=(pitch, pitch)
)
for r, mat in zip(radii[::-1], materials_c1[::-1]):
    print(f"Adding region with radius {r} and material {mat}")
    cell1.add(
        Region(Circle(radius=r), properties={PropertyType.MATERIAL: mat})
    )
# Apply the cell's sectorisation
cell1.sectorize([1, 1, 1, 1, 1, 4, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)

materials_c2 = ["32UOX", "32UOX", "32UOX", "32UOX", "GAP", "CLAD"]
cell2 = CartesianCell(
    name="Cartesian cell", base_props={PropertyType.MATERIAL: "COOLANT"},
    width_height=(pitch, pitch)
)
for r, mat in zip(radii[::-1], materials_c2[::-1]):
    print(f"Adding region with radius {r} and material {mat}")
    cell2.add(
        Region(Circle(radius=r), properties={PropertyType.MATERIAL: mat})
    )
# Apply the cell's sectorisation
cell2.sectorize([1, 1, 1, 1, 1, 4, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)


materials_c4 = ["45UOX", "45UOX", "45UOX", "45UOX", "GAP", "CLAD"]
cell4 = CartesianCell(
    name="Cartesian cell", base_props={PropertyType.MATERIAL: "COOLANT"},
    width_height=(pitch, pitch)
)
for r, mat in zip(radii[::-1], materials_c4[::-1]):
    print(f"Adding region with radius {r} and material {mat}")
    cell4.add(
        Region(Circle(radius=r), properties={PropertyType.MATERIAL: mat})
    )
# Apply the cell's sectorisation
cell4.sectorize([1, 1, 1, 1, 1, 4, 8], [0, 0, 0, 0, 0, 0, 22.5], windmill=True)



# --------------------
# LATTICE CONSTRUCTION
# --------------------
# Build the lattice with several rings of the same cartesian cell1
lattice = CartesianLattice([], name='ATRIUM-10 2x2', centre=(pitch, pitch, 0.0))
#lattice.add_rings_of_cells(cell1, 3)
lattice.add(cell1, position=((1/2)*pitch, (1/2)*pitch, 0.0))
lattice.add(cell2, position=((3/2)*pitch, (1/2)*pitch, 0.0))
lattice.add(cell4, position=((3/2)*pitch, (3/2)*pitch, 0.0))
lattice.add(cell2, position=((1/2)*pitch, (3/2)*pitch, 0.0))

# Assemble all the geometric shapes together
# Update the box cell1's technological geometry with the assembled one

box_w, box_h = (lattice.dimensions[0], lattice.dimensions[1])
channel_thickness = 0.1
gap_thinkness = 0.02
moderator_thickness = 0.1

assembly = CartesianCell(
    width_height=(box_w + 2*channel_thickness+ 2*gap_thinkness + 2*moderator_thickness, box_h + 2*channel_thickness+ 2*gap_thinkness + 2*moderator_thickness),
    center=(box_w/2, box_h/2, 0.0),
    base_props={PropertyType.MATERIAL: "MODERATOR"}
)
# 
lattice_area = Rectangle(
    height=(box_h),
    width=(box_w),
    center=(box_w/2, box_h/2, 0.0)
)
# coolant inside channel box
coolant_area = Rectangle(
    height=(box_h + 2*gap_thinkness),
    width=(box_w + 2*gap_thinkness),
    center=(box_w/2, box_h/2, 0.0),
    rounded_corners=[(0, 0.02),
                    (1, 0.02),
                    (2, 0.02),
                    (3, 0.02),]
)
# Coolant region between channel box and lattice, inscribed betwee lattice area and coolant area (inner channel box boundary)
coolant_channel_area = Region(
    coolant_area - lattice_area,
    properties={PropertyType.MATERIAL: "COOLANT"}
)

# channel box area 
channel_area = Rectangle(
    height=(box_h + 2*gap_thinkness + 2*channel_thickness),
    width=(box_w + 2*gap_thinkness + 2*channel_thickness),
    center=(box_w/2, box_h/2, 0.0),
    rounded_corners=[(0, 0.02),
                    (1, 0.02),
                    (2, 0.02),
                    (3, 0.02),]
)
# Channel box region, inscribed between channel area and coolant area
channel_box_area = Region(
    channel_area - coolant_area,
    properties={PropertyType.MATERIAL: "CHANNEL_BOX"}
)

# Build the box contour as a 'Region' obtained by cutting the entire assembly
# with the inner region and assigning a material
box_contour = Region(
    assembly - channel_area,
    properties={PropertyType.MATERIAL: "MODERATOR"}
)


# Add the lattice to the assembly cell, then apply the assembly layer region
assembly.add(lattice)
assembly.add(coolant_channel_area)
assembly.add(channel_box_area)
assembly.add(box_contour)

# Update the hierarchical tree of the layout and collapse all the layers into
# one, while cutting the refined geometry due to the box layer overlapping
# the outer cells
assembly.update_hierarchical_structure(True)

# Apply the FULL symmetry type to the cartesian lattice
assembly.apply_symmetry(SymmetryType.FULL)

#assembly.geometry_maps[GeometryType.SECTORIZED] = \
#    assembly.get_geometry_map(GeometryType.SECTORIZED)
# Show the resulting layout with the 'MATERIAL' colorset
assembly.show(PropertyType.MATERIAL, GeometryType.SECTORIZED)

# Perform the geometry analysis and export the TDT file of the surface
# geometry

if tracking_type == "TISO":
      export_layout_to_tdt(
      assembly, "data/glow_data/tdt_data/AT10_2x2_cells_TISO", TdtSetup(
                                                            geom_type=GeometryType.SECTORIZED, 
                                                            type_geo=LayoutGeometryType.ISOTROPIC,
                                                            property_types=[PropertyType.MATERIAL],
                                                            symmetry_type=SymmetryType.FULL
                                                            ))
elif tracking_type == "TSPC":
      export_layout_to_tdt(
      assembly, "data/glow_data/tdt_data/AT10_2x2_cells_TSPC", TdtSetup(
                                                            geom_type=GeometryType.SECTORIZED, 
                                                            type_geo=LayoutGeometryType.RECTANGLE_SYM,
                                                            property_types=[PropertyType.MATERIAL],
                                                            symmetry_type=SymmetryType.FULL
                                                            ))