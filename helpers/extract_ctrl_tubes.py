"""
Extract CTRL Tube geometrical information from GE14-00-C.serp file
This script extracts the 42 control blade tubes, each made of 2 concentric cylinders
"""

# CTRL Tube surface definitions from ge14-00-C.serp
# Each tube has 2 cylinders: inner (smaller radius) and outer (larger radius)
# Cylinder format: cyl x_center y_center radius

ctrl_tubes = []

# West side tubes (x = -1.770, varying y from negative to more negative)
# Surfaces 335-376 (21 tubes on west side)
west_tubes_data = [
    (335, 336, -1.770000000E+0, -4.591826190E-1, 1.752600000E-1, 2.387600000E-1),
    (337, 338, -1.770000000E+0, -9.475278571E-1, 1.752600000E-1, 2.387600000E-1),
    (339, 340, -1.770000000E+0, -1.435873095E+0, 1.752600000E-1, 2.387600000E-1),
    (341, 342, -1.770000000E+0, -1.924218333E+0, 1.752600000E-1, 2.387600000E-1),
    (343, 344, -1.770000000E+0, -2.412563571E+0, 1.752600000E-1, 2.387600000E-1),
    (345, 346, -1.770000000E+0, -2.900908810E+0, 1.752600000E-1, 2.387600000E-1),
    (347, 348, -1.770000000E+0, -3.389254048E+0, 1.752600000E-1, 2.387600000E-1),
    (349, 350, -1.770000000E+0, -3.877599286E+0, 1.752600000E-1, 2.387600000E-1),
    (351, 352, -1.770000000E+0, -4.365944524E+0, 1.752600000E-1, 2.387600000E-1),
    (353, 354, -1.770000000E+0, -4.854289762E+0, 1.752600000E-1, 2.387600000E-1),
    (355, 356, -1.770000000E+0, -5.342635000E+0, 1.752600000E-1, 2.387600000E-1),
    (357, 358, -1.770000000E+0, -5.830980238E+0, 1.752600000E-1, 2.387600000E-1),
    (359, 360, -1.770000000E+0, -6.319325476E+0, 1.752600000E-1, 2.387600000E-1),
    (361, 362, -1.770000000E+0, -6.807670714E+0, 1.752600000E-1, 2.387600000E-1),
    (363, 364, -1.770000000E+0, -7.296015952E+0, 1.752600000E-1, 2.387600000E-1),
    (365, 366, -1.770000000E+0, -7.784361190E+0, 1.752600000E-1, 2.387600000E-1),
    (367, 368, -1.770000000E+0, -8.272706429E+0, 1.752600000E-1, 2.387600000E-1),
    (369, 370, -1.770000000E+0, -8.761051667E+0, 1.752600000E-1, 2.387600000E-1),
    (371, 372, -1.770000000E+0, -9.249396905E+0, 1.752600000E-1, 2.387600000E-1),
    (373, 374, -1.770000000E+0, -9.737742143E+0, 1.752600000E-1, 2.387600000E-1),
    (375, 376, -1.770000000E+0, -1.022608738E+1, 1.752600000E-1, 2.387600000E-1),
]

# North side tubes (y = 1.770, varying x from positive to more positive)
# Surfaces 377-418 (21 tubes on north side)
north_tubes_data = [
    (377, 378, 4.591826190E-1, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (379, 380, 9.475278571E-1, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (381, 382, 1.435873095E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (383, 384, 1.924218333E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (385, 386, 2.412563571E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (387, 388, 2.900908810E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (389, 390, 3.389254048E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (391, 392, 3.877599286E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (393, 394, 4.365944524E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (395, 396, 4.854289762E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (397, 398, 5.342635000E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (399, 400, 5.830980238E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (401, 402, 6.319325476E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (403, 404, 6.807670714E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (405, 406, 7.296015952E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (407, 408, 7.784361190E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (409, 410, 8.272706429E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (411, 412, 8.761051667E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (413, 414, 9.249396905E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (415, 416, 9.737742143E+0, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
    (417, 418, 1.022608738E+1, 1.770000000E+0, 1.752600000E-1, 2.387600000E-1),
]

# Combine all tubes
for idx, (surf_inner, surf_outer, x, y, r_inner, r_outer) in enumerate(west_tubes_data):
    tube = {
        'tube_id': idx + 1,
        'location': 'West',
        'center_x': x,
        'center_y': y,
        'inner_radius': r_inner,
        'outer_radius': r_outer,
        'surface_inner': surf_inner,
        'surface_outer': surf_outer,
    }
    ctrl_tubes.append(tube)

for idx, (surf_inner, surf_outer, x, y, r_inner, r_outer) in enumerate(north_tubes_data):
    tube = {
        'tube_id': idx + 22,  # Continue numbering from 22
        'location': 'North',
        'center_x': x,
        'center_y': y,
        'inner_radius': r_inner,
        'outer_radius': r_outer,
        'surface_inner': surf_inner,
        'surface_outer': surf_outer,
    }
    ctrl_tubes.append(tube)

# Print summary
print("=" * 80)
print(f"CTRL TUBE GEOMETRICAL INFORMATION - GE14-00-C")
print("=" * 80)
print(f"\nTotal number of CTRL tubes: {len(ctrl_tubes)}")
print(f"West side tubes: {len(west_tubes_data)}")
print(f"North side tubes: {len(north_tubes_data)}")

print("\n" + "=" * 80)
print("TUBE DETAILS")
print("=" * 80)

print("\n{:4s} {:8s} {:12s} {:12s} {:12s} {:12s} {:10s} {:10s}".format(
    "ID", "Location", "Center X", "Center Y", "Inner R", "Outer R", "Surf In", "Surf Out"))
print("-" * 104)

for tube in ctrl_tubes:
    print("{:4d} {:8s} {:12.6e} {:12.6e} {:12.6e} {:12.6e} {:10d} {:10d}".format(
        tube['tube_id'],
        tube['location'],
        tube['center_x'],
        tube['center_y'],
        tube['inner_radius'],
        tube['outer_radius'],
        tube['surface_inner'],
        tube['surface_outer']
    ))

# Save to CSV file
import csv

csv_filename = '/home/loutre/glow_env/glow/glow_data/ctrl_tubes_geometry.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    fieldnames = ['tube_id', 'location', 'center_x', 'center_y', 'inner_radius', 'outer_radius', 
                  'surface_inner', 'surface_outer']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for tube in ctrl_tubes:
        writer.writerow(tube)

print("\n" + "=" * 80)
print(f"Data saved to: {csv_filename}")
print("=" * 80)

# Print center coordinates only
print("\n" + "=" * 80)
print("CENTER COORDINATES SUMMARY")
print("=" * 80)

print("\nWest Side Tubes (x = -1.77 cm):")
print("{:4s} {:12s} {:12s}".format("ID", "X (cm)", "Y (cm)"))
print("-" * 30)
for tube in ctrl_tubes[:21]:
    print("{:4d} {:12.6f} {:12.6f}".format(tube['tube_id'], tube['center_x'], tube['center_y']))

print("\nNorth Side Tubes (y = 1.77 cm):")
print("{:4s} {:12s} {:12s}".format("ID", "X (cm)", "Y (cm)"))
print("-" * 30)
for tube in ctrl_tubes[21:]:
    print("{:4d} {:12.6f} {:12.6f}".format(tube['tube_id'], tube['center_x'], tube['center_y']))

print("\n" + "=" * 80)
print("NOTES:")
print("=" * 80)
print("- Each CTRL tube consists of 2 concentric cylinders")
print("- Inner cylinder radius: 0.17526 cm (material 27 - B4C absorber)")
print("- Outer cylinder radius: 0.23876 cm (material 26 - SS304 cladding)")
print("- West side: 21 tubes aligned along x = -1.77 cm")
print("- North side: 21 tubes aligned along y = 1.77 cm")
print("- Total: 42 tubes forming the control blade wings")
print("=" * 80)
