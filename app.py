import tkinter as tk
from tkinter import filedialog, messagebox
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
from slice_chamber_final import rotate_mesh_to_q1, generate_slices, save_to_csv


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

        self.btn_load = tk.Button(
            root, text="Load STL File", command=self.load_file, width=20, height=2
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
            filetypes=[("STL Files", "*.stl"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.label_status.config(text=f"Loading {file_path}...")
                self.root.update()

                self.mesh = trimesh.load(file_path, process=False)
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
                    self.mesh, start_angle=0, end_angle=90, step=0.5, num_points=500
                )

                save_to_csv(results, filename=save_path)

                self.label_status.config(
                    text=f"Export complete!\nSaved to {save_path.split('/')[-1]}"
                )
                messagebox.showinfo("Success", "Data exported successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {e}")
                self.label_status.config(text="Error exporting data.")


if __name__ == "__main__":
    root = tk.Tk()
    app = KisslingerApp(root)
    root.mainloop()
