import tkinter as tk
from tkinter import filedialog, messagebox
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from slice_chamber_final import (
    rotate_mesh_to_q1,
    generate_slices,
    save_to_csv,
    plot_cross_sections,
)


class KisslingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kisslinger Coordinates Exporter")
        self.root.geometry("400x300")

        self.mesh = None
        self.filename = None

        # UI Elements
        self.label_status = tk.Label(
            root, text="Welcome! Please load an STL file.", wraplength=350
        )
        self.label_status.pack(pady=20)

        # Parameter Inputs
        self.frame_params = tk.Frame(root)
        self.frame_params.pack(pady=5)

        tk.Label(self.frame_params, text="Phi Resolution (°):").grid(
            row=0, column=0, padx=5
        )
        self.entry_step = tk.Entry(self.frame_params, width=10)
        self.entry_step.insert(0, "0.5")
        self.entry_step.grid(row=0, column=1, padx=5)

        tk.Label(self.frame_params, text="Points per Slice:").grid(
            row=1, column=0, padx=5
        )
        self.entry_points = tk.Entry(self.frame_params, width=10)
        self.entry_points.insert(0, "500")
        self.entry_points.grid(row=1, column=1, padx=5)

        self.btn_load = tk.Button(
            root,
            text="Load File (STL/STEP)",
            command=self.load_file,
            width=20,
            height=2,
        )
        self.btn_load.pack(pady=10)

        self.btn_view = tk.Button(
            root,
            text="View 3D Mesh",
            command=self.view_mesh,
            state=tk.DISABLED,
            width=20,
            height=2,
        )
        self.btn_view.pack(pady=10)

        self.btn_export = tk.Button(
            root,
            text="Export Coordinates",
            command=self.export_data,
            state=tk.DISABLED,
            width=20,
            height=2,
        )
        self.btn_export.pack(pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("3D Files", "*.stl *.step *.stp"),
                ("STL Files", "*.stl"),
                ("STEP Files", "*.step *.stp"),
                ("All Files", "*.*"),
            ]
        )
        if file_path:
            try:
                self.label_status.config(text=f"Loading {file_path}...")
                self.root.update()

                # Load the mesh (handles STL and STEP via gmsh if installed)
                loaded = trimesh.load(file_path, process=False)

                # Handle Scene objects (common with STEP files)
                if isinstance(loaded, trimesh.Scene):
                    if len(loaded.geometry) == 0:
                        raise ValueError("The loaded file contains no geometry.")
                    # Concatenate all geometries in the scene into a single mesh
                    self.mesh = trimesh.util.concatenate(
                        tuple(
                            trimesh.Trimesh(vertices=g.vertices, faces=g.faces)
                            for g in loaded.geometry.values()
                        )
                    )
                else:
                    self.mesh = loaded

                self.mesh = rotate_mesh_to_q1(self.mesh)
                self.filename = file_path

                self.label_status.config(
                    text=f"Loaded: {file_path.split('/')[-1]}\nMesh rotated to Q1."
                )
                self.btn_view.config(state=tk.NORMAL)
                self.btn_export.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
                self.label_status.config(text="Error loading file.")

    def view_mesh(self):
        if self.mesh:
            try:
                # Use matplotlib for viewing to avoid GLU dependency issues
                fig = plt.figure(figsize=(8, 8))
                ax = fig.add_subplot(111, projection="3d")

                # Create a Poly3DCollection
                mesh_collection = art3d.Poly3DCollection(self.mesh.triangles)
                mesh_collection.set_edgecolor("k")
                mesh_collection.set_alpha(0.5)

                ax.add_collection3d(mesh_collection)

                # Auto-scale the plot
                scale = self.mesh.vertices.flatten()
                ax.auto_scale_xyz(scale, scale, scale)

                ax.set_xlabel("X")
                ax.set_ylabel("Y")
                ax.set_zlabel("Z")
                ax.set_title("3D Mesh Viewer")

                plt.show()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to view mesh: {e}")

    def export_data(self):
        if not self.mesh:
            return

        try:
            step = float(self.entry_step.get())
            num_points = int(self.entry_points.get())
            if step <= 0 or num_points <= 0:
                raise ValueError("Values must be positive.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your parameters: {e}")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if save_path:
            try:
                self.label_status.config(
                    text="Generating slices... (This may take a moment)"
                )
                self.root.update()

                # Generate slices with the requested parameters
                results = generate_slices(
                    self.mesh,
                    start_angle=0,
                    end_angle=90,
                    step=step,
                    num_points=num_points,
                )

                save_to_csv(results, filename=save_path)

                self.label_status.config(
                    text=f"Export complete!\nSaved to {save_path.split('/')[-1]}"
                )
                messagebox.showinfo("Success", "Data exported successfully!")

                # Show the cross-section plot
                plot_cross_sections(results)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")
                self.label_status.config(text="Error exporting data.")


if __name__ == "__main__":
    root = tk.Tk()
    app = KisslingerApp(root)
    root.mainloop()
