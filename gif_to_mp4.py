#!/usr/bin/env python3
"""
Convert GIF to MP4 using imageio.
"""

import imageio.v3 as iio
import numpy as np

print("Converting GIF to MP4...")

# Read the GIF
gif_path = "debug/cross_section_animation_hires.gif"
mp4_path = "debug/cross_section_animation.mp4"

# Read all frames
frames = iio.imread(gif_path)
print(f"Read {len(frames)} frames from GIF")

# Write as MP4
iio.imwrite(mp4_path, frames, fps=20, codec="libx264")
print(f"Saved MP4 to {mp4_path}")
