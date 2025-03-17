
import numpy as np
import pyvista as pv


from utils.detector_geometries import DETECTOR_GEOM
from utils.global_viz_utils import rescale_color


def unfold_v1_display(experiment, features, pos, edge_indices):

    # --- Unfold the Cylinder into 2D ---
    R = DETECTOR_GEOM[experiment]['cylinder_radius']
    theta = np.arctan2(pos[:, 1], pos[:, 0])
    theta = np.mod(theta, 2 * np.pi)  # Map angles to [0, 2pi]
    # New 2D coordinates: (arc_length, z) with arc_length = R * theta.
    pos_unfolded = np.column_stack((R * theta, pos[:, 2], np.zeros_like(theta)))

    # --- Prepare PyVista objects ---
    plotter = pv.Plotter()

    # Set an initial scale factor.
    scale_factor_initial = 1.0
    pos_scaled = pos_unfolded * scale_factor_initial

    # Create the point cloud for nodes.
    point_cloud = pv.PolyData(pos_scaled)
    point_cloud["features"] = rescale_color(features[:, 0])

    # Create spheres (glyphs) for nodes.
    sphere = pv.Sphere(radius=DETECTOR_GEOM[experiment]['PMT_radius'] - 1, theta_resolution=8, phi_resolution=8)
    spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)
    plotter.add_mesh(spheres, scalars='features', cmap='plasma')

    # Create a line mesh for the edges.
    lines = []
    for edge_index in edge_indices.T:
        lines.extend([2, edge_index[0], edge_index[1]])  # "2" indicates a line between two points

    line_mesh = pv.PolyData(pos_scaled)
    line_mesh.lines = lines
    plotter.add_mesh(line_mesh, color="black", line_width=2, opacity=0.5, style="wireframe")

    # --- Callback function to update scale ---
    def update_scale(value):
        # Compute new coordinates based on the slider value.
        new_coords = pos_unfolded * value
        point_cloud.points = new_coords
        line_mesh.points = new_coords
        plotter.render()

    # --- Add a slider widget ---
    plotter.add_slider_widget(
        callback=update_scale,
        rng=[0.5, 3.0],             # Range of scale factors.
        value=scale_factor_initial, # Initial scale factor.
        title="Scale Factor",
        pointa=(0.1, 0.1),          # Slider start position in normalized display coordinates.
        pointb=(0.9, 0.1)           # Slider end position.
    )

    print("\nDisplaying graph...\n")
    plotter.show()
