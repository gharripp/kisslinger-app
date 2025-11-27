import trimesh
import numpy as np
from scipy.interpolate import interp1d


def get_rz_slice_debug(mesh, phi_degrees, num_points=200):
    """
    Slices mesh, closes the loop, and interpolates R, Z points.
    """
    phi_rad = np.radians(phi_degrees)
    normal = np.array([np.sin(phi_rad), -np.cos(phi_rad), 0])
    origin = np.array([0, 0, 0])

    # 1. Slice
    slice_3d = mesh.section(plane_origin=origin, plane_normal=normal)
    if slice_3d is None:
        print("slice_3d is None")
        return None, None

    try:
        vertices_3d = np.concatenate(slice_3d.discrete)
    except ValueError:
        print("ValueError in concatenate")
        return None, None

    # 2. Filter (Keep only the "front" of the infinite plane)
    direction_vector = np.array([np.cos(phi_rad), np.sin(phi_rad), 0])
    dot_products = np.dot(vertices_3d, direction_vector)
    vertices_3d = vertices_3d[dot_products > 0]  # Masking

    if len(vertices_3d) < 2:
        print(f"Not enough vertices after filtering: {len(vertices_3d)}")
        return None, None

    # 3. Convert to R, Z
    R_raw = np.sqrt(vertices_3d[:, 0] ** 2 + vertices_3d[:, 1] ** 2)
    Z_raw = vertices_3d[:, 2]
    points = np.column_stack((R_raw, Z_raw))

    # 4. Sort points to form a path
    # points_sorted = _sort_points_by_proximity(points) # Skipping sort for debug check

    print("Success so far")
    return points, points


from slice_chamber_final import rotate_mesh_to_q1

filename = "chamber_surface.stl"
mesh = trimesh.load(filename, process=False)
mesh = rotate_mesh_to_q1(mesh)

print("Testing angle 0.0...")
get_rz_slice_debug(mesh, 0.0, num_points=500)
