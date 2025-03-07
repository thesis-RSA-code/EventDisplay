
import numpy as np
import pyvista as pv

from utils.global_viz_utils import rescale_color
from utils.detector_geometries import DETECTOR_GEOM



def base_display(experiment, features, pos, edge_indices):

    plotter = pv.Plotter()

    print("\nCreating point cloud...\n")

    # Create a point cloud with color mapping
    point_cloud = pv.PolyData(pos)
    point_cloud["features"] = rescale_color(features[:, 0])  # Use feature values for coloring

    # Create spheres at detector positions
    sphere = pv.Sphere(radius=DETECTOR_GEOM[experiment]['PMT_radius']-1, theta_resolution=8, phi_resolution=8)  # Adjust radius as needed
    spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)

    plotter.add_mesh(spheres, scalars='features', cmap='plasma')  # Light detectors

    print("\nCreating edges...\n")

    # Create a single line mesh for efficiency
    lines = []
    for edge_index in edge_indices.T:
        lines.extend([2, edge_index[0], edge_index[1]])  # "2" indicates a line between two points

    line_mesh = pv.PolyData()
    line_mesh.points = pos
    line_mesh.lines = lines

    # Add all edges as a single mesh
    plotter.add_mesh(line_mesh, color="black", line_width=2, opacity=0.5, style="wireframe")

    print("\nDisplaying graph...\n")

    # Show the plot
    plotter.show()

