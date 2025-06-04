import argparse

import numpy as np
import awkward as ak
import uproot as up
import pyvista as pv
import pickle as pck

#np.bool = bool

from utils.global_viz_utils import make_dashed_line, track_style, add_custom_legend, rescale_color
from utils.detector_geometries import DETECTOR_GEOM
from utils.root.load_data_from_root import load_data_from_root



def compute_tracks(trackId, parentId, particleStart, particleStop) :

    tracks = {str(track): [] for track in trackId}

    for track in trackId:
        daughters = trackId[parentId==track]
        vertices = [particleStart[trackId==track]]
        for daughter in daughters:
            vertices.append(particleStart[trackId==daughter])
        vertices.append(particleStop[trackId==track])

        tracks[str(track)] = ak.flatten(vertices)

    return tracks


def plot_display(data, experiment, plot_Chgamma=False) :

    PMT_radius = DETECTOR_GEOM[experiment]['PMT_radius']
    cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
    detector_height = DETECTOR_GEOM[experiment]['height']

    hitx = data["hitx"][0]
    hity = data["hity"][0]
    hitz = data["hitz"][0]
    charge = data["charge"][0]

    trackId = data["trackId"][0]
    pId = data["pID"][0]
    parentId = data["parentId"][0]
    flag = data["flag"][0]
    particleStart = data["particleStart"][0]
    particleStop = data["particleStop"][0]
    creatorProcess = data["CreatorProcess"][0]

    # select primary particle (flag == 0 and parentId == 0)
    primaryId = trackId[(flag == 0) & (parentId == 0)][0]

    # select Cherenkov photons
    gammaStart = particleStart[pId == 0]
    gammaStop = particleStop[pId == 0]
    gammaId = trackId[pId == 0]

    # remove Cherenkov photons from tracks
    particleStart = particleStart[pId != 0]
    particleStop = particleStop[pId != 0]
    trackId = trackId[pId != 0]
    parentId = parentId[pId != 0]
    creatorProcess = creatorProcess[pId != 0]
    pId = pId[pId != 0]

    # Compute tracks vertices
    print("Computing tracks vertices...")
    tracks = compute_tracks(trackId, parentId, particleStart, particleStop)


    # pyvista plot
    plotter = pv.Plotter(window_size=(800, 600))

    # Plot particle tracks
    print("Plotting particle tracks...")

    track_actors = {}

    for track in trackId:
        if track == 0:
            continue

        if pId[trackId == track] == 0:
            continue
        
        vertices = tracks[str(track)].to_numpy()

        color, ls, alpha, lw = track_style(pId[trackId == track])

        if ls == '--':
            line = make_dashed_line(vertices, dash_length=0.3, gap_length=0.3)
        else:
    
            line = pv.PolyData(vertices)
            line.lines = np.array([[len(vertices), *range(len(vertices))]] )

            
        actor = plotter.add_mesh(line, color=color, line_width=lw, point_size=0.1, opacity=alpha)

        # Store actor by creatorProcess
        process = creatorProcess[trackId == track][0]  # Get process name

        if process not in track_actors:
            track_actors[process] = []
        track_actors[process].append(actor)

    # Checkbox widget callback function
    def toggle_tracks(process, flag):
        for actor in track_actors[process]:
            actor.SetVisibility(flag)
        plotter.render()

    # Create checkboxes for each creatorProcess
    for i, process in enumerate(track_actors.keys()):
        plotter.add_checkbox_button_widget(
            lambda flag, p=process: toggle_tracks(p, flag), 
            value=True, 
            position=(10, 50 + i * 30),
            size=20,
            border_size=2
        )
        text_pos = (60, 50 + i * 30)  # Adjust position next to checkbox
        plotter.add_text(process, position=text_pos, font_size=10, color="white")

 
    # Plot Cherenkov gamma tracks
    if plot_Chgamma: 
        print("Plotting gamma tracks...")
        for start, stop in zip(gammaStart, gammaStop):
            #if np.dot(stop - start, particleStop[trackId == primaryId]-particleStart[trackId == primaryId]) < 0:
                #continue
            color, ls, alpha, lw = track_style(0)
            line = pv.Line(start, stop)
            line.lines = np.array([[2, 0, 1]])
            plotter.add_mesh(line, color=color, line_width=lw, opacity=alpha)


    # Add detector hits as points
    print("Adding detector hits as points...")
   
    points = np.column_stack((hitx.to_numpy(), hity.to_numpy(), hitz.to_numpy()))
    point_cloud = pv.PolyData(points)
    point_cloud['charge'] = rescale_color(charge)

    # Create spheres at detector positions
    sphere = pv.Sphere(radius=PMT_radius, theta_resolution=8, phi_resolution=8)  # Adjust radius as needed
    spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)

    plotter.add_mesh(spheres, scalars='charge', cmap='plasma')  # Light detectors


    # draw detector
    print("Drawing detector...")

    if experiment == "WCTE" :
        cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=cylinder_radius+5, height=detector_height+10) # fine-tuned for WCTE
    else :
        cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=cylinder_radius, height=detector_height) # fine-tuned for SK



    plotter.add_mesh(cylinder, color='black')

    for z in [-detector_height/2+57/2, detector_height/2-57/2]:

        # Parameters for the circle
        radius = cylinder_radius - 25 # Radius of the circle
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

    # Set camera position
    plotter.camera_position = [
        particleStart[trackId == primaryId][0]-ak.Array([20, 0, -20]),   # Camera position (x, y, z)
        particleStop[trackId == primaryId][0],   # Focal point (center of the view)
        (0, 0, 1),   # View up vector (defines the "up" direction)
    ]

    add_info_string = ', '.join([info['label'] + r'$ = $' + str(info['values'][0].round(2)) + ' ' + info['unit'] for info in data['add_info']])

    plotter.add_text(add_info_string, position='upper_edge', font_size=10, color="white")


    # add custom legend
    add_custom_legend(plotter, pId)

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
        "-i", "--index", type=int, default=0,
        help="Index of the event to display (default: 0)."
    )

    parser.add_argument(
        "-e", "--experiment", type=str, default="SK",
        help="Name of the experiment (default: 'SK'. Possibilities are SK, HK, WCTE)."
    )

    parser.add_argument(
        "-g", "--plot_Chgamma", action="store_true",
        help="Plot Cherenkov gamma tracks."
    )

    parser.add_argument(
        "-r", "--rotate", action="store_true",
        help="Whether to rotate the detector or not (useful for WCTE)."
    )

    args = parser.parse_args()
    root_file = args.file
    tree_name = args.tree
    event_index = args.index
    experiment = args.experiment
    rotate = args.rotate

    data_keys = ["hitx",
                 "hity",
                 "hitz",
                 "charge",
                 "time",  
                 "trackId",
                 "pID",
                 "parentId",
                 "flag",
                 "particleStart",
                 "particleStop",
                 "CreatorProcess"]
    
    extra_data_keys = ["energy"]
    
    extra_data_units = ["MeV"]

    data, n_data, _ = load_data_from_root(root_file, tree_name, event_index, data_keys, extra_data_keys, extra_data_units, rotate, showering=True)
    
    plot_display(data, experiment, plot_Chgamma=args.plot_Chgamma)


