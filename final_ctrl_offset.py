"""
Final correct calculation of the offset between control cross center and first North tube
"""

# Key surface definitions
surf_321_px = -1.770000000E+0  # West edge of control blade
surf_328_px =  2.150100000E-1  # East boundary of central north arm
surf_319_py =  1.770000000E+0  # North edge of control blade
surf_327_py = -2.150100000E-1  # South boundary of central structures

# Looking at the control blade cross structure:
# The central junction/cross is where the North and West arms meet
# This appears to be a "+" shape positioned in the upper-left

# The actual CENTER of the control cross (the junction point) should be considered
# as the point where both arms intersect, which is likely around (-1.77, 1.77)
# or we should use the geometric center of the cross structure

# However, looking at typical BWR control blade geometry, the cross center
# is usually at the geometric center of the junction where all arms meet.

# From the cell definitions, the overlap/junction region would be:
# The area that could belong to both arms (if they existed) is around:
# x ~ -1.77 to -1.374, y ~ -0.215 to 1.374

# But for a more physical interpretation: if the control blade has a cruciform shape,
# the center is typically at the origin or at the geometric center of symmetry.

# Actually, let me think about this from the blade geometry:
# The blade extends from -1.77 to +10.216 in x
# and from -10.216 to +1.77 in y

# This suggests the blade is NOT centered at (0,0) but rather the cruciform
# center might be at around where the central structure is thickest

# For a BWR control blade with absorber tubes along wings:
# The center should be at the junction of the four wings (cruciform center)

# Looking at the symmetry: if south wing goes to -10.216 and north structure ends at 1.77,
# and east wing goes to 10.216 and west structure ends at -1.77,
# then the cross center should be at approximately:

x_center_cruciform = 0.0  # Typical cruciform center
y_center_cruciform = 0.0

# But this doesn't match the geometry shown... Let me reconsider.

# Actually, looking at the surfaces again:
# - North central structure goes from x=-1.77 to x=+0.215
# - West central structure goes from x=-1.374 to x=-1.77
# 
# The CENTER of this "+" shaped structure would be at:
# For North arm: x_center = (-1.77 + 0.215)/2 = -0.7775
# For West arm: x_center = (-1.374 + (-1.77))/2 = -1.572

# Wait, these are perpendicular arms. The junction center should be where they meet.
# Let's find the overlapping region or junction point.

# The most logical center point for the control cross is at the corner: (-1.77, 1.77)
# OR at the geometric center of where both arms could overlap

# Let me calculate it differently - find the center of the thick part of the cross:
# The "thick" part (central junction) would be approximately:
# x: somewhere between -1.77 and 0.215 for North arm
# y: somewhere between -0.215 and 1.77 for the vertical extent

# For a standard BWR cruciform blade, the center is at the intersection point.
# Given the asymmetric positioning, let's assume the center is at the point
# where the blade would be inserted, which is typically at a corner or center junction.

# Most reasonable interpretation: The control cross center is at (-1.77, 1.77) - the corner
# OR at the geometric center of the North arm junction around x ≈ -0.778, y ≈ 1.572

# Let's calculate both scenarios:

# Tube data
x_first_north_tube = 4.591826190E-1
y_first_north_tube = 1.770000000E+0
tube_spacing = 0.488345238  # cm (calculated from consecutive tubes)

print("=" * 80)
print("CORRECTED OFFSET CALCULATION")
print("=" * 80)

# Scenario 1: Center at the corner/junction (-1.77, 1.77)
x_center_corner = surf_321_px  # -1.77
y_center_corner = surf_319_py  # 1.77
offset_from_corner = x_first_north_tube - x_center_corner

print(f"\nScenario 1: Center at corner junction ({x_center_corner:.3f}, {y_center_corner:.3f})")
print(f"  First North tube at: ({x_first_north_tube:.6f}, {y_first_north_tube:.6f})")
print(f"  X-offset: {offset_from_corner:.6f} cm = {offset_from_corner*10:.3f} mm")
print(f"  Ratio to tube spacing: {offset_from_corner / tube_spacing:.3f}")

# Scenario 2: Center at geometric center of North arm central structure
x_center_north_arm = (surf_321_px + surf_328_px) / 2  # Center of North arm
y_center_north_arm = (surf_319_py + 1.373760000E+0) / 2  # Center of North arm height
offset_from_north_center = x_first_north_tube - x_center_north_arm

print(f"\nScenario 2: Center at North arm center ({x_center_north_arm:.6f}, {y_center_north_arm:.6f})")
print(f"  X-offset: {offset_from_north_center:.6f} cm = {offset_from_north_center*10:.3f} mm")
print(f"  Ratio to tube spacing: {offset_from_north_center / tube_spacing:.3f}")

# Scenario 3: Looking at where the central structure ends (east boundary)
offset_from_east_edge = x_first_north_tube - surf_328_px

print(f"\nScenario 3: From east edge of central structure ({surf_328_px:.6f})")
print(f"  X-offset: {offset_from_east_edge:.6f} cm = {offset_from_east_edge*10:.3f} mm")
print(f"  Ratio to tube spacing: {offset_from_east_edge / tube_spacing:.3f}")

print("\n" + "=" * 80)
print("TUBE SPACING REFERENCE")
print("=" * 80)
print(f"Spacing between consecutive tubes: {tube_spacing:.6f} cm = {tube_spacing*10:.3f} mm")

print("\n" + "=" * 80)
print("MOST LIKELY ANSWER")
print("=" * 80)
print(f"\nIf 'center of control cross' refers to the corner junction at (-1.77, 1.77):")
print(f"  X-offset = {offset_from_corner:.6f} cm = {offset_from_corner*10:.3f} mm")
print(f"  This is approximately {offset_from_corner / tube_spacing:.1f} times the tube spacing")
print(f"\nThis makes physical sense as the first tube is positioned several")
print(f"tube-spacings away from the central structure.")
