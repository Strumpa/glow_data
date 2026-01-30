"""
Recalculate the control cross geometry more carefully
Analyzing the cell definitions to understand the true structure
"""

# Surface definitions from ge14-00-C.serp
# px surfaces (perpendicular to x-axis, at specific x values)
surf_321_px = -1.770000000E+0  # px
surf_324_px = -1.373760000E+0  # px
surf_326_px = -1.516000000E+0  # px
surf_328_px =  2.150100000E-1  # px
surf_334_px =  1.021626000E+1  # px

# py surfaces (perpendicular to y-axis, at specific y values)
surf_319_py =  1.770000000E+0  # py
surf_323_py =  1.373760000E+0  # py
surf_325_py =  1.516000000E+0  # py
surf_327_py = -2.150100000E-1  # py
surf_333_py = -1.021626000E+1  # py

print("=" * 80)
print("CONTROL CROSS STRUCTURE ANALYSIS")
print("=" * 80)

# Let's analyze each cell definition:
print("\nCell 401: $CTRL Blade Central Structure North")
print("  Surfaces: 321, -319, -328, 323")
print("  Translation: 321 (x > -1.77), -319 (y < 1.77), -328 (x < 0.215), 323 (y > 1.374)")
print("  This is the NORTH arm of the cross")
print(f"    x range: {surf_321_px:.6f} to {surf_328_px:.6f} cm")
print(f"    y range: {surf_323_py:.6f} to {surf_319_py:.6f} cm")

print("\nCell 402: $CTRL Blade Central Structure West")
print("  Surfaces: 321, -323, 327, -324")
print("  Translation: 321 (x > -1.77), -323 (y < 1.374), 327 (y > -0.215), -324 (x < -1.374)")
print("  This is the WEST arm of the cross")
print(f"    x range: {surf_324_px:.6f} to {surf_321_px:.6f} cm")
print(f"    y range: {surf_327_py:.6f} to {surf_323_py:.6f} cm")

# The TRUE CENTER of the cross should be at the junction point
# Looking at the geometry, the cross structure appears to be in the UPPER LEFT quadrant
# The junction point where both arms meet is likely at or near x=-1.77, y=1.77

# But wait, let me think about this differently. The control cross has a central junction.
# Looking at the surfaces more carefully:
# - The North arm goes from y=1.374 to y=1.77
# - The West arm goes from x=-1.77 to x=-1.374
# 
# The typical BWR control blade has a cruciform shape centered at the origin
# But in this case, it seems shifted to the upper-left quadrant

# Let's check if there's a central cell that defines the junction
print("\n" + "=" * 80)
print("INTERPRETING THE GEOMETRY")
print("=" * 80)

print("\nThe control cross appears to be positioned in the upper-left region.")
print("The central junction of the cross is where both arms meet.")
print("\nBased on the cell definitions:")
print("  - North arm: rectangular region")
print(f"      x: [{surf_321_px:.6f}, {surf_328_px:.6f}] cm")
print(f"      y: [{surf_323_py:.6f}, {surf_319_py:.6f}] cm")
print("  - West arm: rectangular region")
print(f"      x: [{surf_324_px:.6f}, {surf_321_px:.6f}] cm")
print(f"      y: [{surf_327_py:.6f}, {surf_323_py:.6f}] cm")

# The center of the ENTIRE cross structure (including both arms)
# would be somewhere in the overlapping region or geometric center

# Actually, looking at the surfaces:
# surf 321: px = -1.770 and surf 319: py = 1.770
# These seem to be the outer edges of the blade in the corner

# The actual center of the control blade cross should be at (0, 0) typically
# Or we should look at where the control blade is positioned

print("\n" + "=" * 80)
print("CHECKING FOR SYMMETRY")
print("=" * 80)

# Let's check the wing surfaces to understand the full geometry
print("\nWing and tip surfaces:")
print(f"  surf 333: py = {surf_333_py:.6f} cm (far south)")
print(f"  surf 334: px = {surf_334_px:.6f} cm (far east)")
print(f"  surf 319: py = {surf_319_py:.6f} cm (north edge)")
print(f"  surf 321: px = {surf_321_px:.6f} cm (west edge)")

# The full blade extends from:
# x: -1.77 to +10.216 cm
# y: -10.216 to +1.77 cm

# This suggests the blade is centered around a different point
# Let's calculate the center based on the FULL blade extent
x_min_blade = surf_321_px  # -1.77
x_max_blade = surf_334_px  # +10.216
y_min_blade = surf_333_py  # -10.216
y_max_blade = surf_319_py  # +1.77

x_center_full = (x_min_blade + x_max_blade) / 2
y_center_full = (y_min_blade + y_max_blade) / 2

print(f"\nFull blade extent:")
print(f"  x: [{x_min_blade:.6f}, {x_max_blade:.6f}] cm")
print(f"  y: [{y_min_blade:.6f}, {y_max_blade:.6f}] cm")
print(f"\nGeometric center of full blade:")
print(f"  x_center = {x_center_full:.6f} cm")
print(f"  y_center = {y_center_full:.6f} cm")

# First tube on North side
x_first_north_tube = 4.591826190E-1
y_first_north_tube = 1.770000000E+0

# Distance between consecutive tubes (calculated from data)
tube_spacing = 9.475278571E-1 - 4.591826190E-1

print("\n" + "=" * 80)
print("TUBE SPACING AND OFFSET CALCULATIONS")
print("=" * 80)
print(f"\nTube spacing: {tube_spacing:.6f} cm = {tube_spacing*10:.6f} mm")

print(f"\nFirst North tube position:")
print(f"  x = {x_first_north_tube:.6f} cm")
print(f"  y = {y_first_north_tube:.6f} cm")

# Now calculate offset from different potential centers
offset_from_full_center = x_first_north_tube - x_center_full
offset_from_corner = x_first_north_tube - surf_321_px
offset_from_east_boundary = x_first_north_tube - surf_328_px

print(f"\nX-offset from geometric center of full blade: {offset_from_full_center:.6f} cm")
print(f"X-offset from west edge (surf 321): {offset_from_corner:.6f} cm")
print(f"X-offset from east boundary of central structure (surf 328): {offset_from_east_boundary:.6f} cm")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print(f"\nThe most meaningful offset is likely from the west corner (-1.77, 1.77)")
print(f"to the first North tube (0.459, 1.77):")
print(f"  Δx = {offset_from_corner:.6f} cm = {offset_from_corner*10:.6f} mm")
print(f"\nThis is consistent with: tube spacing = {tube_spacing:.6f} cm = {tube_spacing*10:.6f} mm")
print(f"Ratio: {offset_from_corner / tube_spacing:.3f}")
