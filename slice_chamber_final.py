import trimesh
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import csv


def rotate_mesh_to_q1(mesh):
    """
    Detects the mesh's position and rotates it to the 0-90 degree First Quadrant.
    """
    center = mesh.centroid
    mean_angle = np.degrees(np.arctan2(center[1], center[0]))
    print(f"Original Mesh Position: Centered around {mean_angle:.1f}°")

    best_rotation = 0
    min_dist_to_45 = 1000

    # Check which 90-degree rotation brings us closest to 45 degrees
    for i in range(-4, 5):
        rot = i * 90
        test_angle = mean_angle + rot
        test_angle = (test_angle + 180) % 360 - 180  # Normalize

        dist = abs(test_angle - 45)
        if dist < min_dist_to_45:
            min_dist_to_45 = dist
            best_rotation = rot

    if best_rotation != 0:
        print(f"-> Rotating mesh by {best_rotation}° to align with 0-90°...")
        matrix = trimesh.transformations.rotation_matrix(
            np.radians(best_rotation), [0, 0, 1]
        )
        mesh.apply_transform(matrix)
    else:
        print("-> Mesh is already in the correct quadrant.")

    return mesh


def get_rz_slice(mesh, phi_degrees, num_points=200):
    """
    Slices mesh, closes the loop, and interpolates R, Z points.
    FIXED: Uses angular sorting instead of greedy nearest-neighbor.
    """
    phi_rad = np.radians(phi_degrees)
    normal = np.array([np.sin(phi_rad), -np.cos(phi_rad), 0])
    origin = np.array([0, 0, 0])

    # 1. Slice
    slice_3d = mesh.section(plane_origin=origin, plane_normal=normal)

    # Retry with small epsilon if exact slice fails (common at 0 degrees)
    if slice_3d is None:
        phi_rad += 1e-5
        normal = np.array([np.sin(phi_rad), -np.cos(phi_rad), 0])
        slice_3d = mesh.section(plane_origin=origin, plane_normal=normal)

    if slice_3d is None:
        return None, None

    try:
        vertices_3d = np.concatenate(slice_3d.discrete)
    except ValueError:
        return None, None

    # 2. Filter (Keep only the "front" of the infinite plane)
    direction_vector = np.array([np.cos(phi_rad), np.sin(phi_rad), 0])
    dot_products = np.dot(vertices_3d, direction_vector)
    vertices_3d = vertices_3d[dot_products > 0]  # Masking

    if len(vertices_3d) < 2:
        return None, None

    # 3. Convert to R, Z
    R_raw = np.sqrt(vertices_3d[:, 0] ** 2 + vertices_3d[:, 1] ** 2)
    Z_raw = vertices_3d[:, 2]
    points = np.column_stack((R_raw, Z_raw))

    # 4. Sort points to form a path - FIXED VERSION
    points_sorted = _sort_points_by_angle(points)

    # 4.5 Normalize starting point for toroidal continuity
    points_sorted = _normalize_starting_point(points_sorted)

    # Remove duplicates
    _, idx = np.unique(points_sorted, axis=0, return_index=True)
    points_sorted = points_sorted[np.sort(idx)]

    # --- FIX: FORCE CLOSE THE LOOP ---
    # Append the first point to the end to bridge the gap at the bottom
    points_sorted = np.vstack([points_sorted, points_sorted[0]])

    # 5. Interpolate
    diffs = np.diff(points_sorted, axis=0)
    dists = np.sqrt((diffs**2).sum(axis=1))
    cumulative_dist = np.insert(np.cumsum(dists), 0, 0)
    total_dist = cumulative_dist[-1]

    if total_dist == 0:
        return None, None

    # Linear interpolation along the path
    interp_func_R = interp1d(cumulative_dist, points_sorted[:, 0], kind="linear")
    interp_func_Z = interp1d(cumulative_dist, points_sorted[:, 1], kind="linear")

    # Generate exactly 'num_points'
    # Note: We use 0 to total_dist inclusive to complete the circle
    target_dists = np.linspace(0, total_dist, num_points)

    return interp_func_R(target_dists), interp_func_Z(target_dists)


def _sort_points_by_angle(points):
    """
    Sort points by their angular position around the centroid.
    This prevents self-intersecting paths.
    """
    if len(points) == 0:
        return np.array([])

    # Calculate centroid
    centroid = np.mean(points, axis=0)

    # Calculate angle of each point relative to centroid
    # Using atan2(Z - Z_center, R - R_center)
    angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])

    # Sort by angle
    sorted_indices = np.argsort(angles)

    return points[sorted_indices]


def _normalize_starting_point(points):
    """
    Roll the points array so that index 0 is at the outboard side (maximum R).
    This ensures toroidal continuity across slices.

    We find points near the maximum R value, then pick the one with minimum Z
    as a tie-breaker. This handles cases where the cross-section is symmetric
    and has two points with nearly the same max R (one at +Z, one at -Z).
    """
    if len(points) == 0:
        return points

    # Find max R and get points within a small tolerance of it
    max_R = points[:, 0].max()
    R_tolerance = 0.01 * max_R  # 1% tolerance
    near_max_R = points[:, 0] >= (max_R - R_tolerance)

    if np.sum(near_max_R) > 1:
        # Multiple points near max R - use minimum Z as tie-breaker
        candidates = np.where(near_max_R)[0]
        z_values = points[candidates, 1]
        best_candidate = candidates[np.argmin(z_values)]
        start_idx = best_candidate
    else:
        # Single max R point
        start_idx = np.argmax(points[:, 0])

    # Roll array so start_idx becomes index 0
    return np.roll(points, -start_idx, axis=0)


def _sort_points_by_proximity(points):
    """Greedy nearest-neighbor sort - OLD VERSION (has bugs)."""
    points_list = points.tolist()
    if not points_list:
        return np.array([])

    # Heuristic: Start with the lowest Z (bottom)
    points_list.sort(key=lambda p: p[1])
    path = [points_list.pop(0)]

    while points_list:
        last_point = path[-1]
        dists = np.sum((np.array(points_list) - last_point) ** 2, axis=1)
        nearest_idx = np.argmin(dists)
        path.append(points_list.pop(nearest_idx))

    return np.array(path)


def save_to_csv(results, filename="chamber_coordinates.csv"):
    """Saves the dictionary of results to a CSV file."""
    print(f"Saving data to {filename}...")
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Header
        writer.writerow(["Phi_Deg", "Point_Index", "R_mm", "Z_mm"])

        # Sort by angle to keep file ordered
        sorted_angles = sorted(results.keys())
        for phi in sorted_angles:
            r_vals, z_vals = results[phi]
            for i, (r, z) in enumerate(zip(r_vals, z_vals)):
                writer.writerow([phi, i, f"{r:.4f}", f"{z:.4f}"])
    print("Save complete.")


def generate_slices(mesh, start_angle=0, end_angle=90, step=0.5, num_points=500):
    """
    Generates R, Z slices for the given mesh over a range of angles.
    """
    print(f"Scanning {start_angle}° to {end_angle}°...")
    results = {}
    # Use np.arange but include the end_angle by adding a small buffer to the stop value
    for phi in np.arange(start_angle, end_angle + step / 2, step):
        r_vals, z_vals = get_rz_slice(mesh, phi, num_points=num_points)
        if r_vals is not None:
            results[phi] = (r_vals, z_vals)

    print(f"Generated slices for {len(results)} angles.")
    return results


def smooth_toroidal_continuity(results):
    """
    Post-process the results to ensure smooth toroidal continuity.
    Uses propagation: for each slice, find the point closest to the previous
    slice's point 0 and roll the array to make that the new starting point.
    """
    print("Smoothing toroidal continuity...")

    sorted_angles = sorted(results.keys())
    if len(sorted_angles) < 2:
        return results

    smoothed = {}

    # First angle: keep as-is (already normalized to max R)
    first_phi = sorted_angles[0]
    smoothed[first_phi] = results[first_phi]
    prev_R0, prev_Z0 = results[first_phi][0][0], results[first_phi][1][0]

    # Process subsequent angles
    for phi in sorted_angles[1:]:
        r_vals, z_vals = results[phi]
        n_points = len(r_vals)

        # Find the point closest to previous slice's point 0
        dists = np.sqrt((r_vals - prev_R0) ** 2 + (z_vals - prev_Z0) ** 2)
        closest_idx = np.argmin(dists)

        # Roll the arrays so closest_idx becomes index 0
        if closest_idx != 0:
            r_vals = np.roll(r_vals, -closest_idx)
            z_vals = np.roll(z_vals, -closest_idx)

        smoothed[phi] = (r_vals, z_vals)
        prev_R0, prev_Z0 = r_vals[0], z_vals[0]

    print(f"Smoothing complete.")
    return smoothed


def plot_cross_sections(results):
    """
    Plots the cross-sections for a selected set of angles.
    """
    plot_angles = [0, 15, 30, 45, 60, 75, 90]
    plt.figure(figsize=(8, 10))

    for angle in plot_angles:
        # Handle float keys in results
        angle_key = float(angle)
        if angle_key in results:
            r_vals, z_vals = results[angle_key]
            plt.plot(r_vals, z_vals, ".-", markersize=1, label=f"Phi={angle}°")
        else:
            # Try finding closest key if exact match fails (floating point issues)
            keys = np.array(list(results.keys()))
            if len(keys) > 0:
                closest_key = keys[np.argmin(np.abs(keys - angle_key))]
                if abs(closest_key - angle_key) < 1e-5:
                    r_vals, z_vals = results[closest_key]
                    plt.plot(r_vals, z_vals, ".-", markersize=1, label=f"Phi={angle}°")
                else:
                    print(f"Warning: Angle {angle} not found in results.")
            else:
                print(f"Warning: Angle {angle} not found in results.")

    plt.axis("equal")
    plt.xlabel("R [mm]")
    plt.ylabel("Z [mm]")
    plt.title("Vacuum Chamber Cross Sections")
    plt.legend()
    plt.grid(True)
    plt.show()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    filename = "chamber_surface.stl"

    try:
        # Load and Rotate
        mesh = trimesh.load(filename, process=False)
        mesh = rotate_mesh_to_q1(mesh)

        # Generate Slices (0.25° step for higher resolution)
        results = generate_slices(mesh, 0, 90, 0.25, 500)

        # Smooth toroidal continuity by propagating starting points
        results = smooth_toroidal_continuity(results)

        # Save to File
        save_to_csv(results, "chamber_coordinates_fixed.csv")

        # Plot Verification (commented for headless execution)
        # plot_cross_sections(results)

    except Exception as e:
        print(f"Error: {e}")
