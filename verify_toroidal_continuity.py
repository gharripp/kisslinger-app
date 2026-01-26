#!/usr/bin/env python3
"""
Verify toroidal continuity of the fixed kisslinger file.
Plots cross-sections at multiple angles, highlighting:
- First 10 points (orange)
- Middle 10 points (green)
- Last 10 points (red)

If the fix worked, these colored segments should be at consistent
physical locations across all toroidal angles.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the fixed CSV file
df = pd.read_csv("chamber_coordinates_fixed.csv")

# Angles to verify - same as debug images plus a few more
verify_angles = [58.0, 60.0, 62.0, 70.0, 72.0, 0.0, 30.0, 45.0, 90.0]

print("Verifying toroidal continuity after fix...")
print(f"Checking angles: {verify_angles}")

# Create subplot grid
n_cols = 3
n_rows = int(np.ceil(len(verify_angles) / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
axes = axes.flatten()

for idx, phi in enumerate(verify_angles):
    ax = axes[idx]

    # Get data for this angle
    data = df[df["Phi_Deg"] == phi]

    if len(data) == 0:
        ax.text(0.5, 0.5, f"No data at {phi}°", ha="center", va="center")
        ax.set_title(
            f"φ = {phi:.1f}° - NO DATA", fontsize=11, fontweight="bold", color="red"
        )
        continue

    R = data["R_mm"].values
    Z = data["Z_mm"].values
    n_points = len(R)

    # Plot the full cross-section
    ax.plot(R, Z, "b-", linewidth=1, alpha=0.5, zorder=1)
    ax.scatter(R, Z, c="blue", s=3, alpha=0.3, zorder=2)

    # Highlight first 10 points (orange)
    ax.scatter(
        R[:10],
        Z[:10],
        c="orange",
        s=50,
        label="First 10",
        zorder=5,
        edgecolors="black",
        linewidths=0.5,
    )

    # Highlight middle 10 points (green)
    mid_start = n_points // 2 - 5
    mid_end = mid_start + 10
    ax.scatter(
        R[mid_start:mid_end],
        Z[mid_start:mid_end],
        c="green",
        s=50,
        label="Middle 10",
        zorder=5,
        edgecolors="black",
        linewidths=0.5,
    )

    # Highlight last 10 points (red)
    ax.scatter(
        R[-10:],
        Z[-10:],
        c="red",
        s=50,
        label="Last 10",
        zorder=5,
        edgecolors="black",
        linewidths=0.5,
    )

    ax.set_xlabel("R (mm)", fontsize=10)
    ax.set_ylabel("Z (mm)", fontsize=10)
    ax.set_title(f"φ = {phi:.1f}° ({n_points} points)", fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")
    ax.legend(fontsize=8, loc="lower right")

    # Print diagnostic info
    print(f"\nAngle {phi}°:")
    print(f"  First point (idx 0):    R={R[0]:.2f}, Z={Z[0]:.2f}")
    print(
        f"  Middle point (idx {n_points // 2}): R={R[n_points // 2]:.2f}, Z={Z[n_points // 2]:.2f}"
    )
    print(f"  Last point (idx {n_points - 1}):  R={R[-1]:.2f}, Z={Z[-1]:.2f}")

# Hide unused subplots
for idx in range(len(verify_angles), len(axes)):
    axes[idx].axis("off")

plt.tight_layout()
plt.savefig("debug/verify_toroidal_continuity.png", dpi=150, bbox_inches="tight")
print(f"\nSaved debug/verify_toroidal_continuity.png")

# Also create a quantitative summary
print("\n" + "=" * 60)
print("QUANTITATIVE CHECK: Starting point locations")
print("=" * 60)
print(f"{'Angle':>8} {'R[0]':>10} {'Z[0]':>10} {'Max R':>10}")
print("-" * 40)

for phi in sorted(verify_angles):
    data = df[df["Phi_Deg"] == phi]
    if len(data) > 0:
        R = data["R_mm"].values
        Z = data["Z_mm"].values
        print(f"{phi:>8.1f} {R[0]:>10.2f} {Z[0]:>10.2f} {R.max():>10.2f}")

print("\nExpected: R[0] should be close to Max R, Z[0] should be close to 0")
