# Kisslinger Coordinates Exporter

A Python desktop application for loading STL files of vacuum chambers (or other rotationally symmetric objects), visualizing them in 3D, and exporting "Kisslinger coordinates" (R, Z slices) to a CSV file.

## Features

- **Load STL**: Open and load binary or ASCII STL files.
- **Auto-Rotation**: Automatically detects and rotates the mesh to the first quadrant (0-90 degrees) if needed.
- **3D Visualization**: View the loaded mesh using a built-in Matplotlib 3D viewer.
- **Slicing & Export**: 
  - Generates cross-sectional slices from 0° to 90° at 0.5° intervals.
  - Interpolates 500 points per slice.
  - Exports data to a CSV file (`Phi_Deg`, `Point_Index`, `R_mm`, `Z_mm`).

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This app requires `tkinter` for the GUI. On most Python installations it is included, but on Linux you may need to install it separately (e.g., `sudo apt-get install python3-tk`).*

## Usage

Run the application:

```bash
python3 app.py
```

1. Click **Load STL File** to select your geometry.
2. Click **View 3D Mesh** to inspect the object.
3. Click **Export Coordinates** to generate the CSV file.

## Files

- `app.py`: Main GUI application entry point.
- `slice_chamber_final.py`: Core logic for mesh processing, slicing, and saving.
- `requirements.txt`: List of Python dependencies.
