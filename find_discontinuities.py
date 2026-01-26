#!/usr/bin/env python3
"""
Find toroidal discontinuities - angles where the starting point jumps.
This detects where point 0 location changes significantly from one angle to the next.
"""

import pandas as pd
import numpy as np

# Read the fixed CSV file
df = pd.read_csv("chamber_coordinates_fixed.csv")

# Get all unique angles, sorted
angles = sorted(df["Phi_Deg"].unique())
print(f"Analyzing {len(angles)} toroidal angles from {angles[0]}° to {angles[-1]}°\n")

# Extract starting point (point 0) for each angle
starting_points = []
for phi in angles:
    data = df[(df["Phi_Deg"] == phi) & (df["Point_Index"] == 0)]
    if len(data) > 0:
        starting_points.append(
            {"phi": phi, "R": data["R_mm"].values[0], "Z": data["Z_mm"].values[0]}
        )

# Calculate jumps between consecutive angles
print("Checking for discontinuities in starting point location...")
print("=" * 70)

jumps = []
for i in range(1, len(starting_points)):
    prev = starting_points[i - 1]
    curr = starting_points[i]

    dR = curr["R"] - prev["R"]
    dZ = curr["Z"] - prev["Z"]
    dist = np.sqrt(dR**2 + dZ**2)

    jumps.append(
        {
            "phi": curr["phi"],
            "prev_phi": prev["phi"],
            "dR": dR,
            "dZ": dZ,
            "dist": dist,
            "R": curr["R"],
            "Z": curr["Z"],
            "prev_R": prev["R"],
            "prev_Z": prev["Z"],
        }
    )

# Calculate statistics
dists = np.array([j["dist"] for j in jumps])
mean_dist = np.mean(dists)
std_dist = np.std(dists)
threshold = mean_dist + 3 * std_dist

print(f"Mean distance between consecutive starting points: {mean_dist:.2f} mm")
print(f"Std deviation: {std_dist:.2f} mm")
print(f"Threshold for 'jump' (mean + 3*std): {threshold:.2f} mm")
print()

# Find large jumps
large_jumps = [j for j in jumps if j["dist"] > threshold]

if large_jumps:
    print(f"FOUND {len(large_jumps)} DISCONTINUITIES:")
    print("-" * 70)
    for j in large_jumps:
        print(f"\nAngle {j['phi']:.1f}° (from {j['prev_phi']:.1f}°):")
        print(f"  Jump distance: {j['dist']:.2f} mm")
        print(f"  Previous: R={j['prev_R']:.2f}, Z={j['prev_Z']:.2f}")
        print(f"  Current:  R={j['R']:.2f}, Z={j['Z']:.2f}")
        print(f"  Delta:    dR={j['dR']:.2f}, dZ={j['dZ']:.2f}")
else:
    print("No significant discontinuities found!")

# Also check for sign flips or large Z changes which might indicate issues
print("\n" + "=" * 70)
print("Additional check: Large Z changes in starting point")
print("=" * 70)

z_changes = [(j["phi"], j["dZ"]) for j in jumps if abs(j["dZ"]) > 50]
if z_changes:
    print(f"Found {len(z_changes)} angles with large Z changes (> 50mm):")
    for phi, dZ in z_changes:
        print(f"  φ = {phi:.1f}°: dZ = {dZ:.2f} mm")
else:
    print("No large Z changes detected.")

# Print top 10 largest jumps for inspection
print("\n" + "=" * 70)
print("TOP 10 LARGEST JUMPS (for inspection):")
print("=" * 70)
sorted_jumps = sorted(jumps, key=lambda x: x["dist"], reverse=True)[:10]
for j in sorted_jumps:
    print(
        f"  φ={j['phi']:5.1f}°: dist={j['dist']:7.2f} mm  |  R={j['R']:.1f}, Z={j['Z']:.1f}"
    )
