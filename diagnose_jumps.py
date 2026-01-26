#!/usr/bin/env python3
"""
Diagnose the specific jump locations to understand what's happening.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("chamber_coordinates_fixed.csv")

# Problem transitions identified by user
problem_transitions = [(3.0, 3.5), (57.0, 57.5), (61.5, 62.0)]

print("=" * 70)
print("DIAGNOSING JUMP LOCATIONS")
print("=" * 70)

fig, axes = plt.subplots(
    len(problem_transitions), 2, figsize=(16, 6 * len(problem_transitions))
)

for row, (phi1, phi2) in enumerate(problem_transitions):
    print(f"\n{'=' * 70}")
    print(f"TRANSITION: {phi1}° -> {phi2}°")
    print("=" * 70)

    # Get data for both angles
    data1 = df[df["Phi_Deg"] == phi1]
    data2 = df[df["Phi_Deg"] == phi2]

    R1, Z1 = data1["R_mm"].values, data1["Z_mm"].values
    R2, Z2 = data2["R_mm"].values, data2["Z_mm"].values

    # Analyze first 20 points
    print(f"\nFirst 20 points at {phi1}°:")
    print(f"  R range: {R1[:20].min():.1f} to {R1[:20].max():.1f}")
    print(f"  Z range: {Z1[:20].min():.1f} to {Z1[:20].max():.1f}")
    print(f"  Point 0: R={R1[0]:.2f}, Z={Z1[0]:.2f}")

    print(f"\nFirst 20 points at {phi2}°:")
    print(f"  R range: {R2[:20].min():.1f} to {R2[:20].max():.1f}")
    print(f"  Z range: {Z2[:20].min():.1f} to {Z2[:20].max():.1f}")
    print(f"  Point 0: R={R2[0]:.2f}, Z={Z2[0]:.2f}")

    # Calculate jump
    jump_R = R2[0] - R1[0]
    jump_Z = Z2[0] - R1[0]
    jump_dist = np.sqrt((R2[0] - R1[0]) ** 2 + (Z2[0] - Z1[0]) ** 2)
    print(
        f"\nJump: dR={R2[0] - R1[0]:.2f}, dZ={Z2[0] - Z1[0]:.2f}, distance={jump_dist:.2f} mm"
    )

    # Find where point 0 of phi1 would be in phi2's ordering
    # (i.e., find the closest point in phi2 to phi1's point 0)
    dists_to_p0 = np.sqrt((R2 - R1[0]) ** 2 + (Z2 - Z1[0]) ** 2)
    closest_idx = np.argmin(dists_to_p0)
    print(f"\nClosest point in {phi2}° to {phi1}°'s point 0: index {closest_idx}")
    print(f"  That point: R={R2[closest_idx]:.2f}, Z={Z2[closest_idx]:.2f}")

    # Plot both
    ax1, ax2 = axes[row]

    ax1.plot(R1, Z1, "b-", alpha=0.5)
    ax1.scatter(R1[:20], Z1[:20], c="orange", s=80, zorder=5, edgecolors="black")
    ax1.scatter(R1[0], Z1[0], c="red", s=200, marker="*", zorder=10, label=f"Point 0")
    ax1.set_title(
        f"φ = {phi1}° - Point 0 at ({R1[0]:.0f}, {Z1[0]:.0f})", fontweight="bold"
    )
    ax1.set_xlabel("R (mm)")
    ax1.set_ylabel("Z (mm)")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_aspect("equal")

    ax2.plot(R2, Z2, "b-", alpha=0.5)
    ax2.scatter(R2[:20], Z2[:20], c="orange", s=80, zorder=5, edgecolors="black")
    ax2.scatter(R2[0], Z2[0], c="red", s=200, marker="*", zorder=10, label=f"Point 0")
    # Also mark where phi1's point 0 would be
    ax2.scatter(
        R1[0], Z1[0], c="green", s=200, marker="X", zorder=10, label=f"Previous point 0"
    )
    ax2.set_title(
        f"φ = {phi2}° - Point 0 at ({R2[0]:.0f}, {Z2[0]:.0f})", fontweight="bold"
    )
    ax2.set_xlabel("R (mm)")
    ax2.set_ylabel("Z (mm)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_aspect("equal")

plt.tight_layout()
plt.savefig("debug/diagnose_jumps.png", dpi=150, bbox_inches="tight")
print(f"\nSaved debug/diagnose_jumps.png")
plt.close()
