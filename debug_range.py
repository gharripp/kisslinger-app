import trimesh
import numpy as np
from slice_chamber_final import rotate_mesh_to_q1

filename = "chamber_surface.stl"
mesh = trimesh.load(filename, process=False)
mesh = rotate_mesh_to_q1(mesh)

vertices = mesh.vertices
angles = np.degrees(np.arctan2(vertices[:, 1], vertices[:, 0]))
print(f"Min angle: {angles.min()}")
print(f"Max angle: {angles.max()}")
