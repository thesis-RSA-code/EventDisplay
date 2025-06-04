
import argparse

import numpy as np
import uproot as up

import pyvista as pv
import matplotlib.pyplot as plt



from utils.global_viz_utils import rescale_color, load_data_from_root
from utils.detector_geometries import DETECTOR_GEOM


def simple_display(events_root, experiment, plot_vertex=False, plot_stop=False, plot_dir=False, outline=False) : 
    r"""
    Simple 3D plot of a given event, just to check if everything is in order
    """  
    print('================================ Simple 3D display ===================================')

    hitx = events_root['hitx'][0]
    hity = events_root['hity'][0]
    hitz = events_root['hitz'][0]
    charge = events_root['charge'][0]

    cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
    zMax = DETECTOR_GEOM[experiment]['height']/2
    zMin = -DETECTOR_GEOM[experiment]['height']/2


    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    if experiment == "WCTE_r":
        ax.set_xlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_zlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_ylim(zMin-50, zMax+50)

    else:
        ax.set_xlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_ylim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_zlim(zMin-50, zMax+50)



    PMT_radius = DETECTOR_GEOM[experiment]['PMT_radius']
    #PMT_plot_size = compute_PMT_marker_size(PMT_radius, ax)

    ax.scatter(hitx, hity, hitz, s=5, c=rescale_color(charge), cmap='plasma')

    if plot_vertex:
        vertex = events_root['vertex'][0]
        ax.scatter(vertex[0], vertex[1], vertex[2], c='r', marker='o', s=100)

    if plot_stop:
        stop = events_root['particleStop'][0]
        ax.scatter(stop[0], stop[1], stop[2], c='g', marker='x', s=100)

    if plot_dir:
        direction = events_root['particleDir'][0]
        ax.quiver(vertex[0], vertex[1], vertex[2], direction[0], direction[1], direction[2], length=100, normalize=True)


    # draw cylinder limits
    if outline:
        if experiment == "WCTE_r":
            theta = np.linspace(0, 2 * np.pi, 20)  # Angular points
            y = np.linspace(zMin, zMax, 20)      # Height points along Y-axis
            Theta, Y = np.meshgrid(theta, y)       # Meshgrid for cylinder surface

            # Convert polar coordinates to Cartesian for plotting
            X = cylinder_radius * np.cos(Theta)
            Z = cylinder_radius * np.sin(Theta)


            # Plot cylinder surface
            ax.plot_surface(X, Y, Z, color='lightblue', alpha=0.6)

            # Top and bottom circular caps
            radius = np.linspace(0, cylinder_radius, 20)
            Theta_cap, Radius = np.meshgrid(theta, radius)
            X_cap = Radius * np.cos(Theta_cap)
            Z_cap = Radius * np.sin(Theta_cap)

            ax.plot_surface(X_cap, np.full_like(X_cap, zMax), Z_cap, color='lightblue', alpha=0.6)
            ax.plot_surface(X_cap, np.full_like(X_cap, zMin), Z_cap, color='lightblue', alpha=0.6)

        else:
            # Create a mesh for the cylinder
            theta = np.linspace(0, 2 * np.pi, 20)  # Angular points
            z = np.linspace(zMin, zMax, 20)      # Height points
            Theta, Z = np.meshgrid(theta, z)       # Meshgrid for cylinder surface

            # Convert polar coordinates to Cartesian for plotting
            X = (cylinder_radius+5) * np.cos(Theta)
            Y = (cylinder_radius+5) * np.sin(Theta)

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



def draw_all_vertices(tree, experiment) :

    vertices = tree["vertex"][0]

    cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
    zMax = DETECTOR_GEOM[experiment]['height']/2
    zMin = -DETECTOR_GEOM[experiment]['height']/2


    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    if experiment == "WCTE_r":
        ax.set_xlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_zlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_ylim(zMin-50, zMax+50)

    else:
        ax.set_xlim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_ylim(-cylinder_radius-50, cylinder_radius+50)
        ax.set_zlim(zMin-50, zMax+50)

    # draw vertices
    ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], c='r', marker='o', s=100)

    # draw cylinder
    if experiment == "WCTE_r":
        theta = np.linspace(0, 2 * np.pi, 20)  # Angular points
        y = np.linspace(zMin, zMax, 20)      # Height points along Y-axis
        Theta, Y = np.meshgrid(theta, y)       # Meshgrid for cylinder surface
        # Convert polar coordinates to Cartesian for plotting
        X = cylinder_radius * np.cos(Theta)
        Z = cylinder_radius * np.sin(Theta)

        # Plot cylinder surface
        ax.plot_surface(X, Y, Z, color='lightblue', alpha=0.6)

        # Top and bottom circular caps
        radius = np.linspace(0, cylinder_radius, 20)
        Theta_cap, Radius = np.meshgrid(theta, radius)
        X_cap = Radius * np.cos(Theta_cap)
        Z_cap = Radius * np.sin(Theta_cap)

        ax.plot_surface(X_cap, np.full_like(X_cap, zMax), Z_cap, color='lightblue', alpha=0.6)
        ax.plot_surface(X_cap, np.full_like(X_cap, zMin), Z_cap, color='lightblue', alpha=0.6)

    else:
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

    ax.set_aspect('equal')
    plt.show()


def immersive_display(tree, experiment, plot_vertex=False, plot_stop=False, plot_dir=False) :

    hitx = tree["hitx"][0]
    hity = tree["hity"][0]
    hitz = tree["hitz"][0]
    charge = tree["charge"][0]
    vertex = tree["vertex"][0]

    annotations = []
    for var in ['towall', 'dwall', 'energy']:
        if var in tree.keys():
            value = tree[var][0]
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

    cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=DETECTOR_GEOM[experiment]['cylinder_radius']+10, height=DETECTOR_GEOM[experiment]['height']+10)
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

    # Add vertex if requested
    if plot_vertex:
        print("Adding vertex...")
        vertex = np.array(vertex)
        vertex_sphere = pv.Sphere(radius=2, center=vertex, theta_resolution=8, phi_resolution=8)
        plotter.add_mesh(vertex_sphere, color='red', name='Vertex')
    # Add stop position if requested
    if plot_stop:
        print("Adding stop position...")
        stop = tree["particleStop"][0]
        stop_sphere = pv.Sphere(radius=2, center=stop, theta_resolution=8, phi_resolution=8)
        plotter.add_mesh(stop_sphere, color='green', name='Stop Position')
    # Add particle direction if requested
    if plot_dir:
        print("Adding particle direction...")
        direction = tree["particleDir"][0]
        start = vertex
        end = start + direction * 50  # Scale the direction vector for visibility
        plotter.add_lines(np.array([start, end]), color='blue', width=2, name='Particle Direction')

    # Set camera position
    print("Setting camera...")

    plotter.camera_position = [
        (0, 0, 0),   # Camera position (x, y, z)
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
        "-s", "--stop", action="store_true",
        help="Plot the stop position of the particle. Only for simple display."
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
    data_keys = ["hitx",
                 "hity",
                 "hitz",
                 "charge",
                 "time",
                 "vertex",
                 "particleStop",
                 "particleDir"
                ]

    data, n_data, _ = load_data_from_root(root_file, tree_name, event_index, data_keys)

    if args.kind == 'simple':
        simple_display(data, experiment, plot_vertex=args.vertex, plot_stop=args.stop, plot_dir=args.direction, outline=args.outline)
    elif args.kind == 'immersive' : 
        immersive_display(data, experiment, plot_vertex=args.vertex, plot_stop=args.stop, plot_dir=args.direction)
    elif args.kind == 'all vertices' :
        draw_all_vertices(data, experiment)
    else :
        print("Unknown display kind, please choose between 'simple', 'immersive' or 'all vertices'.")
        exit(1)


