
import argparse

import numpy as np
import uproot as up

import pyvista as pv
import matplotlib.pyplot as plt



from utils.global_viz_utils import rescale_color, compute_PMT_marker_size
from utils.detector_geometries import DETECTOR_GEOM





def simple_display(events_root, event_index, experiment, plot_vertex=False, plot_dir=False, outline=False) : 
    r"""
    Simple 3D plot of a given event, just to check if everything is in order
    """  
    print('================================ Simple 3D display ===================================')

    hitx = events_root['hitx'].array()
    hity = events_root['hity'].array()
    hitz = events_root['hitz'].array()
    charge = events_root['charge'].array()

    cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
    zMax = DETECTOR_GEOM[experiment]['height']/2
    zMin = -DETECTOR_GEOM[experiment]['height']/2


    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    if experiment == "WCTE":
        ax.set_xlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_zlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_ylim(zMin-50, zMax+50)

    else:
        ax.set_xlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_ylim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_zlim(zMin-50, zMax+50)



    PMT_radius = DETECTOR_GEOM[experiment]['PMT_radius']
    PMT_plot_size = compute_PMT_marker_size(PMT_radius, fig, ax)

    ax.scatter(hitx[event_index], hity[event_index], hitz[event_index], s=PMT_plot_size, c=rescale_color(charge[event_index]), cmap='plasma')

    if plot_vertex:
        vertex = events_root['vertex'].array()
        ax.scatter(vertex[event_index][0], vertex[event_index][1], vertex[event_index][2], c='r', marker='o', s=100)

    if plot_dir:
        direction = events_root['particleDir'].array()
        ax.quiver(vertex[event_index][0], vertex[event_index][1], vertex[event_index][2], direction[event_index][0], direction[event_index][1], direction[event_index][2], length=100, normalize=True)

    # draw cylinder limits
    if outline:
        # Create a mesh for the cylinder
        theta = np.linspace(0, 2 * np.pi, 20)  # Angular points
        z = np.linspace(zMin, zMax, 20)      # Height points
        Theta, Z = np.meshgrid(theta, z)       # Meshgrid for cylinder surface

        # Convert polar coordinates to Cartesian for plotting
        X = cylinder_radius * np.cos(Theta)
        Y = cylinder_radius * np.sin(Theta)

        # Plot cylinder surface
        ax.plot_surface(X, Y, Z, color='lightblue', alpha=0.6)

        # Top and bottom circular caps
        theta_cap = np.linspace(0, 2 * np.pi, 20)
        x_cap = cylinder_radius * np.cos(theta_cap)
        y_cap = cylinder_radius * np.sin(theta_cap)

        ax.plot_trisurf(x_cap, y_cap, np.full_like(x_cap, zMax), color='lightblue', alpha=0.6)
        ax.plot_trisurf(x_cap, y_cap, np.full_like(x_cap, zMin), color='lightblue', alpha=0.6)


    ax.set_xlabel(r'$x$ (cm)')
    ax.set_ylabel(r'$y$ (cm)')
    ax.set_zlabel(r'$z$ (cm)')
    ax.set_title(experiment + ' Event Display')

    ax.set_aspect('equal')

    plt.show()



def immersive_display(tree, event_index, experiment) :

    hitx = tree["hitx"].array()[event_index]
    hity = tree["hity"].array()[event_index]
    hitz = tree["hitz"].array()[event_index]
    charge = tree["charge"].array()[event_index]
    vertex = tree["vertex"].array()[event_index]

    annotations = []
    for var in ['towall', 'dwall', 'energy']:
        if var in tree.keys():
            value = tree[var].array()[event_index]
            annotations.append(f"{var}: {value:.3f}")

    # pyvista plot
    plotter = pv.Plotter(window_size=(800, 600))

    # Add detector hits as points
    print("Adding detector hits as points...")
   
    points = np.column_stack((hitx.to_numpy(), hity.to_numpy(), hitz.to_numpy()))
    point_cloud = pv.PolyData(points)
    point_cloud['charge'] = rescale_color(charge)

    # Create spheres at detector positions
    sphere = pv.Sphere(radius=DETECTOR_GEOM[experiment]['PMT_radius'], theta_resolution=8, phi_resolution=8)  # Adjust radius as needed
    spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)

    plotter.add_mesh(spheres, scalars='charge', cmap='plasma')  # Light detectors


    # draw detector
    print("Drawing detector...")

    cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=DETECTOR_GEOM[experiment]['cylinder_radius'], height=DETECTOR_GEOM[experiment]['height'])
    plotter.add_mesh(cylinder, color='black')

    for z in [-DETECTOR_GEOM[experiment]['height'] / 2 + 10, DETECTOR_GEOM[experiment]['height']/2-10]:

        # Parameters for the circle
        radius = DETECTOR_GEOM[experiment]['cylinder_radius'] - 10 # Radius of the circle
        center = (0, 0, z)  # Center of the circle
        resolution = 100    # Number of points around the circle

        z = z*np.ones(resolution)
        # Generate points for the circle
        theta = np.linspace(0, 2 * np.pi, resolution)
        x = center[0] + radius * np.cos(theta)
        y = center[1] + radius * np.sin(theta)

        # Create a PolyData object for the circle
        points = np.column_stack((x, y, z))
        circle = pv.PolyData(points)
        circle.lines = np.array([[len(points), *range(len(points))]])

        # Plot the circle
        plotter.add_mesh(circle, color="grey", point_size=0.01, line_width=5, opacity=0.5)  # Add points

    # Set camera position
    print("Setting camera...")

    plotter.camera_position = [
        vertex,   # Camera position (x, y, z)
        (np.mean(hitx), np.mean(hity), np.mean(hitz)),   # Focal point (center of the view)
        (0, 0, 1),   # View up vector (defines the "up" direction)
    ]

    plotter.camera.view_angle = 90  # Set FOV to 90 degrees for a wide angle

    # Add the extra event information as text (if available)
    if annotations:
        annotation_text = "\n".join(annotations)
        plotter.add_text(annotation_text, position="upper_left", font_size=12, color="white")


    # Add axes labels
    plotter.remove_scalar_bar()
    plotter.add_axes()
    plotter.show()



if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Access events root file and display showering tracks.")

    parser.add_argument(
        "-f", "--file", type=str,
        help="Path to the root file containing event data." 
    )
    
    parser.add_argument(
        "-t", "--tree", type=str, default="pure_root_tree",
        help="Name of the TTree inside the root file (default: 'root_event')."
    )

    parser.add_argument(
        "-e", "--experiment", type=str, default="SK",
        help="Name of the experiment (SK/HK/WCTE) (default: 'SK')."
    )

    parser.add_argument(
        "-i", "--index", type=int, default=0,
        help="Index of the event to display (default: 0)."
    )

    parser.add_argument(
        "--kind", type=str, default='simple',
        help="Define the kind of 3D display ( simple / immersive). (Default : simple)"
    )

    parser.add_argument(
        "-v", "--vertex", action="store_true",
        help="Plot the vertex of the event. Only for simple display."
    )

    parser.add_argument(
        "-d", "--direction", action="store_true",
        help="Plot the particule direction of the event. Only for simple display."
    )

    parser.add_argument(
        "--outline", action="store_true",
        help="Plot the detector outline. Only for simple display."
    )


    args = parser.parse_args()
    root_file = args.file
    tree_name = args.tree
    experiment = args.experiment
    event_index = args.index

    # loading data
    print("Loading data...")
    file = up.open(root_file)
    tree = file[tree_name]

    if args.kind == 'simple':
        simple_display(tree, event_index, experiment, plot_vertex=args.vertex, plot_dir=args.direction, outline=args.outline)
    else : 
        immersive_display(tree, event_index, experiment)


