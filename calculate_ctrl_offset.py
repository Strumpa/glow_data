"""
Calculate the x-distance (offset) between the center of the control cross 
and the first tube on the North side
"""

# From the Serpent file analysis:
# The control cross central structure is bounded by surfaces:
# - surf 321: px = -1.770000000E+0  (West boundary)
# - surf 328: px =  2.150100000E-1  (East boundary)
# - surf 319: py =  1.770000000E+0  (North boundary)
# - surf 327: py = -2.150100000E-1  (South boundary)

# Central structure boundaries
x_west_boundary = -1.770000000E+0  # surf 321
x_east_boundary = 2.150100000E-1   # surf 328
y_north_boundary = 1.770000000E+0  # surf 319
y_south_boundary = -2.150100000E-1 # surf 327

# Calculate the center of the control cross
# The center is at the geometric center of the cross structure
x_center_cross = (x_west_boundary + x_east_boundary) / 2
y_center_cross = (y_south_boundary + y_north_boundary) / 2

print("=" * 80)
print("CONTROL CROSS CENTER CALCULATION")
print("=" * 80)
print(f"\nCentral Structure Boundaries:")
print(f"  West boundary (surf 321):  x = {x_west_boundary:12.6f} cm")
print(f"  East boundary (surf 328):  x = {x_east_boundary:12.6f} cm")
print(f"  North boundary (surf 319): y = {y_north_boundary:12.6f} cm")
print(f"  South boundary (surf 327): y = {y_south_boundary:12.6f} cm")

print(f"\nControl Cross Center:")
print(f"  x_center = {x_center_cross:12.6f} cm")
print(f"  y_center = {y_center_cross:12.6f} cm")

# First tube on the North side (from previous analysis)
# This is tube #22, surface 377
x_first_north_tube = 4.591826190E-1
y_first_north_tube = 1.770000000E+0

print(f"\nFirst North Side Tube (Tube #22):")
print(f"  x_tube = {x_first_north_tube:12.6f} cm")
print(f"  y_tube = {y_first_north_tube:12.6f} cm")

# Calculate the x-offset
x_offset = x_first_north_tube - x_center_cross

print("\n" + "=" * 80)
print("RESULT")
print("=" * 80)
print(f"\nX-offset from control cross center to first North tube:")
print(f"  Δx = {x_offset:12.6f} cm")
print(f"  Δx = {x_offset * 10:12.6f} mm")

# Additional information
print("\n" + "=" * 80)
print("ADDITIONAL GEOMETRY INFORMATION")
print("=" * 80)
print(f"\nControl cross width (x-direction):  {x_east_boundary - x_west_boundary:12.6f} cm")
print(f"Control cross height (y-direction): {y_north_boundary - y_south_boundary:12.6f} cm")

# Distance from cross center to the y-axis where north tubes are located
y_offset = y_first_north_tube - y_center_cross
print(f"\nY-offset from cross center to North tube axis:")
print(f"  Δy = {y_offset:12.6f} cm")

# Distance from east boundary of cross to first north tube
distance_from_east_boundary = x_first_north_tube - x_east_boundary
print(f"\nDistance from east boundary of cross to first North tube:")
print(f"  Distance = {distance_from_east_boundary:12.6f} cm")
print(f"  Distance = {distance_from_east_boundary * 10:12.6f} mm")

print("\n" + "=" * 80)
