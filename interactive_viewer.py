#!/usr/bin/env python3
"""
Interactive viewer for cross-sections with a slider to scroll through angles.
Use the slider or arrow keys to navigate between toroidal angles.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np

# Read the fixed CSV file
print("Loading data...")
df = pd.read_csv("chamber_coordinates_fixed.csv")

# Get all unique angles, sorted
angles = sorted(df["Phi_Deg"].unique())
print(f"Found {len(angles)} toroidal angles from {angles[0]}° to {angles[-1]}°")
print("Use the slider or arrow keys (Left/Right) to navigate")
print("Press 'q' to quit")

# Get global R and Z ranges for consistent axis limits
R_min, R_max = df["R_mm"].min(), df["R_mm"].max()
Z_min, Z_max = df["Z_mm"].min(), df["Z_mm"].max()
margin = 20

# Create figure
fig, ax = plt.subplots(figsize=(12, 10))
plt.subplots_adjust(bottom=0.15)

# Current angle index
current_idx = [0]


def update_plot(angle_idx):
    """Update the plot for a given angle index."""
    ax.clear()

    phi = angles[int(angle_idx)]
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
        s=100,
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
        s=100,
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
        s=100,
        label="Last 10",
        zorder=5,
        edgecolors="black",
        linewidths=0.5,
    )

    # Add point 0 annotation
    ax.annotate(
        f"Point 0\n({R[0]:.0f}, {Z[0]:.0f})",
        xy=(R[0], Z[0]),
        xytext=(R[0] + 60, Z[0] + 60),
        fontsize=10,
        ha="left",
        arrowprops=dict(arrowstyle="->", color="orange", lw=2),
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9),
    )

    ax.set_xlim(R_min - margin, R_max + margin)
    ax.set_ylim(Z_min - margin, Z_max + margin)
    ax.set_xlabel("R (mm)", fontsize=12)
    ax.set_ylabel("Z (mm)", fontsize=12)
    ax.set_title(
        f"Toroidal Cross-Section at φ = {phi:.1f}°  (index {int(angle_idx)}/{len(angles) - 1})",
        fontsize=14,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")
    ax.legend(fontsize=10, loc="lower right")

    fig.canvas.draw_idle()


# Create slider
ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
slider = Slider(ax_slider, "Angle Index", 0, len(angles) - 1, valinit=0, valstep=1)
slider.on_changed(lambda val: update_plot(val))


# Keyboard navigation
def on_key(event):
    if event.key == "right":
        new_val = min(slider.val + 1, len(angles) - 1)
        slider.set_val(new_val)
    elif event.key == "left":
        new_val = max(slider.val - 1, 0)
        slider.set_val(new_val)
    elif event.key == "up":
        new_val = min(slider.val + 10, len(angles) - 1)
        slider.set_val(new_val)
    elif event.key == "down":
        new_val = max(slider.val - 10, 0)
        slider.set_val(new_val)
    elif event.key == "q":
        plt.close()


fig.canvas.mpl_connect("key_press_event", on_key)

# Initial plot
update_plot(0)

plt.show()
