# carrying_idler_cost_fixed.py
import math

# ---------------------------
# CONFIGURABLE CONSTANTS
# ---------------------------
BELT_WIDTH = 1000             # mm (fixed by spec)
STEEL_COST_PER_KG = 70.0      # ₹ per kg (change to your company rate)
BEARING_COST_PAIR = 100.0     # ₹
SEAL_COST = 30.0              # ₹
WELDING_COST = 80.0           # ₹
MARKUP = 1.25                 # multiplier

STEEL_DENSITY = 7850.0        # kg/m^3 (steel density)

# ---------------------------
# UTILITY - units: mm -> m
# ---------------------------
def mm_to_m(x_mm):
    return x_mm / 1000.0

# ---------------------------
# INPUT (you enter X values)
# ---------------------------
print("=== CARRYING IDLER WITHOUT FRAME - COST CALCULATOR ===")
pipe_diameter_mm = float(input("Enter Pipe Diameter (mm): ").strip())
face_width_mm = float(input("Enter Face Width (mm): ").strip())
shaft_diameter_mm = float(input("Enter Shaft Diameter (mm): ").strip())
shaft_length_mm = float(input("Enter Shaft Length (mm): ").strip())
pipe_thickness_mm = float(input("Enter Pipe Thickness (mm): ").strip())
qty = int(input("Enter Quantity: ").strip())

# ---------------------------
# RULE: make shaft even by adding 3 if odd (as given)
# Use robust integer logic
# ---------------------------
shaft_dia_int = int(round(shaft_diameter_mm))
if shaft_dia_int % 2 != 0:
    shaft_dia_int += 3  # add 3 to make it even as per rule
shaft_diameter_mm = float(shaft_dia_int)

# ---------------------------
# WEIGHT CALCULATIONS (accurate geometry)
# - Pipe: approximate as hollow cylinder (outer dia D, thickness t, length = face_width)
#   Volume = pi * ( (D/2)^2 - (D/2 - t)^2 ) * L
# - Shaft: solid cylinder: Volume = pi * (d/2)^2 * L
# Units: convert mm -> m for volume (m^3), multiply by density to get kg
# ---------------------------
# Convert to meters
D_m = mm_to_m(pipe_diameter_mm)
t_m = mm_to_m(pipe_thickness_mm)
L_m = mm_to_m(face_width_mm)       # pipe length = face width (as per your formula)
d_shaft_m = mm_to_m(shaft_diameter_mm)
L_shaft_m = mm_to_m(shaft_length_mm)

# Pipe (hollow cylinder) volume and mass
outer_area = math.pi * (D_m / 2.0) ** 2
inner_radius = (D_m / 2.0) - t_m
if inner_radius < 0:
    inner_area = 0.0
else:
    inner_area = math.pi * (inner_radius) ** 2
pipe_volume_m3 = max(0.0, (outer_area - inner_area) * L_m)
pipe_weight_kg = pipe_volume_m3 * STEEL_DENSITY

# Shaft (solid cylinder) volume and mass
shaft_volume_m3 = math.pi * (d_shaft_m / 2.0) ** 2 * L_shaft_m
shaft_weight_kg = shaft_volume_m3 * STEEL_DENSITY

total_weight_kg = pipe_weight_kg + shaft_weight_kg

# ---------------------------
# COST ELEMENTS
# ---------------------------
housing_cost = pipe_diameter_mm / 2.0           # as per your rule (₹)
material_cost = total_weight_kg * STEEL_COST_PER_KG
bearing_cost = BEARING_COST_PAIR
seal_cost = SEAL_COST
welding_cost = WELDING_COST

total_cost_per_roller = material_cost + housing_cost + bearing_cost + seal_cost + welding_cost
cost_price_for_qty = total_cost_per_roller * qty
unit_selling_price = total_cost_per_roller * MARKUP
total_selling_price = unit_selling_price * qty

# ---------------------------
# OUTPUT (detailed breakdown)
# ---------------------------
print("\n===== DETAILED BREAKDOWN =====")
print(f"Input summary:")
print(f"  Pipe Dia (mm):       {pipe_diameter_mm}")
print(f"  Face Width (mm):     {face_width_mm}")
print(f"  Pipe Thickness (mm): {pipe_thickness_mm}")
print(f"  Shaft Dia (mm) used: {shaft_diameter_mm}  (rounded rule applied)")
print(f"  Shaft Length (mm):   {shaft_length_mm}")
print(f"  Quantity:            {qty}")

print("\nWeight calculations:")
print(f"  Pipe volume (m^3):   {pipe_volume_m3:.8f}")
print(f"  Pipe weight (kg):    {pipe_weight_kg:.4f}")
print(f"  Shaft volume (m^3):  {shaft_volume_m3:.8f}")
print(f"  Shaft weight (kg):   {shaft_weight_kg:.4f}")
print(f"  Total weight (kg):   {total_weight_kg:.4f}")

print("\nCost elements (change constants at top if needed):")
print(f"  Steel cost (@{STEEL_COST_PER_KG} ₹/kg):  {material_cost:.2f} ₹")
print(f"  Housing cost:        {housing_cost:.2f} ₹")
print(f"  Bearing cost (pair): {bearing_cost:.2f} ₹")
print(f"  Seal cost:           {seal_cost:.2f} ₹")
print(f"  Welding cost:        {welding_cost:.2f} ₹")

print("\nTotals:")
print(f"  Total cost per roller (₹)  : {total_cost_per_roller:.2f}")
print(f"  Cost price for {qty} pcs   : {cost_price_for_qty:.2f}")
print(f"  Unit selling price (₹)     : {unit_selling_price:.2f}  (markup {MARKUP*100-100:.0f}%)")
print(f"  Total selling price (₹)    : {total_selling_price:.2f}")

print("\n===== END =====")