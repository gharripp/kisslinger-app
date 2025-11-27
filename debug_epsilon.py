import trimesh
import numpy as np
from slice_chamber_final import get_rz_slice, rotate_mesh_to_q1

filename = "chamber_surface.stl"
mesh = trimesh.load(filename, process=False)
mesh = rotate_mesh_to_q1(mesh)

epsilon = 1e-5
print(f"Testing angle {epsilon}...")
r, z = get_rz_slice(mesh, epsilon, num_points=500)
if r is None:
    print(f"Angle {epsilon} failed.")
else:
    print(f"Angle {epsilon} succeeded with {len(r)} points.")
