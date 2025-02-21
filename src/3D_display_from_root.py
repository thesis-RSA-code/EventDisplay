
import argparse

import numpy as np
import uproot as up

import pyvista as pv
import matplotlib.pyplot as plt



from src.utils.global_viz_utils import rescale_color, track_style, DETECTOR_GEOM


def debug_3D_display(events_root, event_index, experiment) : 
    r"""
    Simple 3D plot of a given event, just to check if everything is in order
    """  

    hitx = events_root['hitx'].array()
    hity = events_root['hity'].array()
    hitz = events_root['hitz'].array()
    charge = events_root['charge'].array()

    #PMT_radius = DETECTOR_GEOM[experiment]['PMT_radius']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(hitx[event_index], hity[event_index], hitz[event_index], s=1, c=rescale_color(charge[event_index]), cmap='plasma')
    plt.show()



def plot_3D_display(tree, event_index) :

    hitx = tree["hitx"].array()[event_index]
    hity = tree["hity"].array()[event_index]
    hitz = tree["hitz"].array()[event_index]
    charge = tree["charge"].array()[event_index]
    vertex = tree["vertex"].array()[event_index]

    # pyvista plot
    plotter = pv.Plotter(window_size=(800, 600))

    # Add detector hits as points
    print("Adding detector hits as points...")
   
    points = np.column_stack((hitx.to_numpy(), hity.to_numpy(), hitz.to_numpy()))
    point_cloud = pv.PolyData(points)
    point_cloud['charge'] = rescale_color(charge)

    # Create spheres at detector positions
    sphere = pv.Sphere(radius=DETECTOR_GEOM['PMT_radius'], theta_resolution=8, phi_resolution=8)  # Adjust radius as needed
    spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)

    plotter.add_mesh(spheres, scalars='charge', cmap='plasma')  # Light detectors


    # draw detector
    print("Drawing detector...")

    cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=DETECTOR_GEOM['cylinder_radius'], height=DETECTOR_GEOM['height'])
    plotter.add_mesh(cylinder, color='black')

    for z in [-DETECTOR_GEOM['height'] / 2 + 10, DETECTOR_GEOM['height']/2-10]:

        # Parameters for the circle
        radius = DETECTOR_GEOM['cylinder_radius'] - 10 # Radius of the circle
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
        "--debug", type=bool, default=False,
        help="Print a fast 3D display. (Default : False)"
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

    if args.debug:
        debug_3D_display(tree, event_index)
    else : plot_3D_display(tree, event_index)


