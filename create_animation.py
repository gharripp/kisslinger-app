#!/usr/bin/env python3
"""
Create MP4 animation from cross-section data for WhatsApp sharing.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Read the fixed CSV file
print("Loading data...")
df = pd.read_csv("chamber_coordinates_fixed.csv")

# Get all unique angles, sorted
angles = sorted(df["Phi_Deg"].unique())
print(f"Found {len(angles)} toroidal angles from {angles[0]}° to {angles[-1]}°")

# Set up the figure with fixed axis limits
fig, ax = plt.subplots(figsize=(10, 8))

# Get global R and Z ranges for consistent axis limits
R_min, R_max = df["R_mm"].min(), df["R_mm"].max()
Z_min, Z_max = df["Z_mm"].min(), df["Z_mm"].max()
margin = 20  # mm


def animate(frame_idx):
    """Update function for animation."""
    ax.clear()

    phi = angles[frame_idx]
    data = df[df["Phi_Deg"] == phi]

    R = data["R_mm"].values
    Z = data["Z_mm"].values
    n_points = len(R)

    # Plot the full cross-section
    ax.plot(R, Z, "b-", linewidth=1.5, alpha=0.6, zorder=1)
    ax.scatter(R, Z, c="blue", s=5, alpha=0.3, zorder=2)

    # Highlight first 10 points (orange)
    ax.scatter(
        R[:10],
        Z[:10],
        c="orange",
        s=80,
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
        s=80,
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
        s=80,
        label="Last 10",
        zorder=5,
        edgecolors="black",
        linewidths=0.5,
    )

    # Add point 0 marker with annotation
    ax.annotate(
        f"Point 0\n({R[0]:.0f}, {Z[0]:.0f})",
        xy=(R[0], Z[0]),
        xytext=(R[0] + 50, Z[0] + 50),
        fontsize=9,
        ha="left",
        arrowprops=dict(arrowstyle="->", color="orange", lw=1.5),
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    ax.set_xlim(R_min - margin, R_max + margin)
    ax.set_ylim(Z_min - margin, Z_max + margin)
    ax.set_xlabel("R (mm)", fontsize=12)
    ax.set_ylabel("Z (mm)", fontsize=12)
    ax.set_title(
        f"Toroidal Cross-Section at φ = {phi:.2f}°", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")
    ax.legend(fontsize=10, loc="lower right")

    return []


print("Creating animation...")
# Use every angle for smooth animation
ani = animation.FuncAnimation(fig, animate, frames=len(angles), interval=50, blit=False)

# Save as MP4 using pillow writer first to create frames, then convert
# Actually, matplotlib can save directly to MP4 if we have the right writer
try:
    # Try with ffmpeg first
    print("Saving animation as MP4...")
    ani.save("debug/cross_section_animation.mp4", writer="ffmpeg", fps=20, dpi=100)
    print("Done! Animation saved to debug/cross_section_animation.mp4")
except Exception as e:
    print(f"ffmpeg not available: {e}")
    print("Saving as GIF instead (you can convert to MP4 online)...")
    ani.save(
        "debug/cross_section_animation_hires.gif", writer="pillow", fps=20, dpi=100
    )
    print("Done! Animation saved to debug/cross_section_animation_hires.gif")

plt.close()
