

import pyvista as pv


from utils.detector_geometries import DETECTOR_GEOM
from utils.global_viz_utils import rescale_color


def scale_factor_bar_display(experiment, features, pos, edge_indices, show_nodes=True, show_edges=True):
    """
    Display the graph in 3D with an interactive slider to adjust the scale factor.
    Also adds checkbox buttons to toggle node and edge visibility.
    
    Parameters:
      experiment   : string key to select detector geometry.
      features     : node features array.
      pos          : node positions (Nx3 array).
      edge_indices : edge index array (2 x num_edges).
      show_nodes   : initial visibility of node glyphs.
      show_edges   : initial visibility of edge mesh.
    """

       # Create the PyVista Plotter
    plotter = pv.Plotter()
    scale_factor_initial = 1.0
    pos_scaled = pos * scale_factor_initial

    # Create the base PolyData for the nodes and set the features
    point_cloud = pv.PolyData(pos_scaled)
    point_cloud["features"] = rescale_color(features[:, 0])

    # Create a sphere to represent each node (PMT)
    sphere = pv.Sphere(radius=DETECTOR_GEOM[experiment]['PMT_radius'] - 1,
                       theta_resolution=8, phi_resolution=8)
    # Create glyphs from the node positions
    nodes_glyph = point_cloud.glyph(scale=False, geom=sphere, orient=False)
    nodes_actor = plotter.add_mesh(nodes_glyph, scalars="features", cmap="plasma", name="nodes")

    # Create edge mesh using the scaled positions
    lines = []
    for edge_index in edge_indices.T:
        # "2" indicates a line connecting two points
        lines.extend([2, edge_index[0], edge_index[1]])
    edge_mesh = pv.PolyData(pos_scaled)
    edge_mesh.lines = lines
    edges_actor = plotter.add_mesh(edge_mesh, color="black", line_width=2,
                                   opacity=0.5, style="wireframe", name="edges")

    # Callback to update the scale factor for both nodes and edges
    def update_scale(value):
        new_coords = pos * value  # Compute new positions from the base positions.
        # Update edge positions.
        edge_mesh.points = new_coords
        # Update node positions by modifying the underlying point cloud...
        point_cloud.points = new_coords
        # ...and recomputing the glyphs.
        new_glyphs = point_cloud.glyph(scale=False, geom=sphere, orient=False)
        nodes_actor.mapper.SetInputData(new_glyphs)
        plotter.render()

    # Add the slider widget for the scale factor.
    plotter.add_slider_widget(callback=update_scale,
                                rng=[0.5, 3.0],
                                value=scale_factor_initial,
                                title="Scale Factor",
                                pointa=(0.1, 0.05),
                                pointb=(0.9, 0.05))

    # Callback to toggle node (PMT) visibility.
    def toggle_nodes(flag):
        nodes_actor.SetVisibility(flag)
        plotter.render()

    # Callback to toggle edge visibility.
    def toggle_edges(flag):
        edges_actor.SetVisibility(flag)
        plotter.render()

    # Add checkbox widgets for interactive toggling.
    # (Positions and colors can be adjusted as desired.)
    plotter.add_checkbox_button_widget(callback=toggle_nodes, value=show_nodes,
                                       position=(10, 10), size=25,
                                       color_on="green", color_off="red")
    plotter.add_checkbox_button_widget(callback=toggle_edges, value=show_edges,
                                       position=(10, 40), size=25,
                                       color_on="green", color_off="red")

    plotter.show()


def fast_scale_bar_display(experiment, features, pos, edge_indices, show_nodes=True, show_edges=True):
    """
    Display the graph in 3D with two interactive sliders:
      - One to adjust the scale factor for the edges (fast update).
      - A second to adjust the scale factor for the nodes (recomputes glyphs).
    Also adds checkbox buttons to toggle node (PMT) and edge visibility.

    Parameters:
      experiment   : string key to select detector geometry.
      features     : node features array (NxD numpy array).
      pos          : node positions (Nx3 numpy array).
      edge_indices : edge index array (2 x num_edges numpy array).
      show_nodes   : initial visibility of node glyphs.
      show_edges   : initial visibility of edge mesh.
    """

    # --- Set up the PyVista Plotter ---
    plotter = pv.Plotter()

    # --- Create the edge mesh actor ---
    # We'll update this actor quickly on slider changes.
    edge_scale_initial = 1.0
    pos_edges = pos * edge_scale_initial
    lines = []
    for edge_index in edge_indices.T:
        lines.extend([2, edge_index[0], edge_index[1]])  # "2" indicates a line segment
    edge_mesh = pv.PolyData(pos_edges)
    edge_mesh.lines = lines
    edges_actor = plotter.add_mesh(edge_mesh, color="black", line_width=2,
                                   opacity=0.5, style="wireframe", name="edges")

    # --- Create the node actor ---
    # We'll create a point cloud for nodes and then glyph them as spheres.
    node_scale_initial = 1.0
    pos_nodes = pos * node_scale_initial
    point_cloud = pv.PolyData(pos_nodes)
    point_cloud["features"] = rescale_color(features[:, 0])
    
    # Create a sphere to represent each node.
    sphere = pv.Sphere(radius=DETECTOR_GEOM[experiment]['PMT_radius'] - 1,
                       theta_resolution=8, phi_resolution=8)
    # Glyph the point cloud. (scale=False ensures that the sphere size remains constant.)
    nodes_glyph = point_cloud.glyph(scale=False, geom=sphere, orient=False)
    nodes_actor = plotter.add_mesh(nodes_glyph, scalars="features",
                                   cmap="plasma", name="nodes")

    # --- Slider callback for edges ---
    def update_edge_scale(value):
        new_pos_edges = pos * value
        edge_mesh.points = new_pos_edges
        plotter.render()

    # --- Slider callback for nodes ---
    def update_node_scale(value):
        new_pos_nodes = pos * value
        point_cloud.points = new_pos_nodes
        # Re-run the glyph filter with updated node positions.
        new_glyphs = point_cloud.glyph(scale=False, geom=sphere, orient=False)
        # Update the nodes actor's geometry.
        nodes_actor.mapper.SetInputData(new_glyphs)
        plotter.render()

    # --- Add slider widget for edge scale factor ---
    plotter.add_slider_widget(callback=update_edge_scale,
                              rng=[0.5, 3.0],
                              value=edge_scale_initial,
                              title="Edge Scale Factor",
                              pointa=(0.1, 0.05),
                              pointb=(0.9, 0.05))

    # --- Add slider widget for node scale factor ---
    plotter.add_slider_widget(callback=update_node_scale,
                              rng=[0.5, 3.0],
                              value=node_scale_initial,
                              title="Node Scale Factor",
                              pointa=(0.1, 0.10),
                              pointb=(0.9, 0.10))

    # --- Checkbox callbacks to toggle visibility ---
    def toggle_nodes(flag):
        nodes_actor.SetVisibility(flag)
        plotter.render()

    def toggle_edges(flag):
        edges_actor.SetVisibility(flag)
        plotter.render()

    # --- Add checkbox widgets for toggling ---
    plotter.add_checkbox_button_widget(callback=toggle_nodes, value=show_nodes,
                                       position=(10, 10), size=25,
                                       color_on="green", color_off="red")
    plotter.add_checkbox_button_widget(callback=toggle_edges, value=show_edges,
                                       position=(10, 40), size=25,
                                       color_on="green", color_off="red")

    plotter.show()
