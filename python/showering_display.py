import argparse

import numpy as np
import awkward as ak
import uproot as up
import pyvista as pv
import pickle as pck

#np.bool = bool


def track_style(pid):
    if pid == 11:
        color='blue'
        ls = '-'
        alpha = 1
        lw = 2
    elif pid == -11:
        color='red'
        ls = '-'
        alpha = 1
        lw = 2
    elif pid == 13:
        color='green'
        ls = '-'
        alpha = 1
        lw = 2
    elif pid == -13:
        color='purple'
        ls = '-'
        alpha = 1
        lw = 2
    elif pid == 22:
        color='orange'
        ls = '--'
        alpha = 0.3
        lw = 0.5
    elif pid == 0:
        color='gold'
        ls = '-'
        alpha=0.05
        lw = 0.2
    else:
        color='black'
        ls = '-'
        alpha = 1
        lw = 2

    return color, ls, alpha, lw


def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x


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


def load_data(root_file, tree_name, event_index) :

    print("Loading event and track data...")

    event_tree = up.open(root_file)[tree_name]

    # event data
    energy = event_tree['energy'].array()[event_index]
    hitx = event_tree['hitx'].array()[event_index]
    hity = event_tree['hity'].array()[event_index]
    hitz = event_tree['hitz'].array()[event_index]
    charge = event_tree['charge'].array()[event_index]

    # tracks data
    particleStart = event_tree['particleStart'].array()[event_index]
    particleStop = event_tree['particleStop'].array()[event_index]
    pId = event_tree['pID'].array()[event_index]
    trackId = event_tree['trackId'].array()[event_index]
    parentId = event_tree['parentId'].array()[event_index]
    flag = event_tree['flag'].array()[event_index]
    creatorProcess = event_tree['CreatorProcess'].array()[event_index]

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
    
    data = {
    "energy": energy,
    "trackId": trackId,
    "pId": pId,
    "particleStart": particleStart,
    "particleStop": particleStop,
    "tracks": tracks,
    "creatorProcess": creatorProcess,
    "primaryId": primaryId,
    "gammaStart": gammaStart,
    "gammaStop": gammaStop,
    "gammaId": gammaId,
    "hitx": hitx,
    "hity": hity,
    "hitz": hitz,
    "charge": charge
    }

    return data


def plot_display(data, detector_geom, plot_Chgamma=False) :

    energy = data["energy"]
    hitx = data["hitx"]
    hity = data["hity"]
    hitz = data["hitz"]
    charge = data["charge"]

    trackId = data["trackId"]
    pId = data["pId"]
    particleStart = data["particleStart"]
    particleStop = data["particleStop"]
    tracks = data["tracks"]
    creatorProcess = data["creatorProcess"]
    primaryId = data["primaryId"]
    gammaStart = data["gammaStart"]
    gammaStop = data["gammaStop"]


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
        line = pv.PolyData(vertices)
        line.lines = np.array([[len(vertices), *range(len(vertices))]] )

        color, ls, alpha, lw = track_style(pId[trackId == track])
            
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
            line = pv.Line(start, stop)
            line.lines = np.array([[2, 0, 1]])
            color, ls, alpha, lw = track_style(0)
            plotter.add_mesh(line, color=color, line_width=lw, opacity=alpha)


    # Add detector hits as points
    print("Adding detector hits as points...")
   
    points = np.column_stack((hitx.to_numpy(), hity.to_numpy(), hitz.to_numpy()))
    point_cloud = pv.PolyData(points)
    point_cloud['charge'] = rescale_color(charge)

    # Create spheres at detector positions
    sphere = pv.Sphere(radius=detector_geom['PMT_radius'], theta_resolution=8, phi_resolution=8)  # Adjust radius as needed
    spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)

    plotter.add_mesh(spheres, scalars='charge', cmap='plasma')  # Light detectors


    # draw detector
    print("Drawing detector...")

    cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=detector_geom['cylinder_radius'], height=detector_geom['height'])
    plotter.add_mesh(cylinder, color='black')

    for z in [-detector_geom['height']/2+10, detector_geom['height']/2-10]:

        # Parameters for the circle
        radius = detector_geom['cylinder_radius'] - 10 # Radius of the circle
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
        particleStart[trackId == primaryId][0]-ak.Array([200, 0, -200]),   # Camera position (x, y, z)
        particleStop[trackId == primaryId][0],   # Focal point (center of the view)
        (0, 0, 1),   # View up vector (defines the "up" direction)
    ]

    plotter.add_text(f"Energy={energy}MeV", position='upper_edge', font_size=10, color="white")
    plotter.camera.view_angle = 90  # Set FOV to 90 degrees for a wide angle

    # Add axes labels
    plotter.remove_scalar_bar()
    plotter.add_axes()
    plotter.show()




if __name__ == "__main__":


    detector_geom = {'SK': {'height': 3620.0, 'cylinder_radius': 3368.15/2, 'PMT_radius': 25.4}, 'HK': {'height': 6575.1, 'cylinder_radius': 6480/2, 'PMT_radius': 25.4}, 'WCTE': {'height': 338.0, 'cylinder_radius': 369.6/2, 'PMT_radius': 4.0}}

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
        "-g", "--plot_Chgamma", action="store_true",
        help="Plot Cherenkov gamma tracks."
    )

    args = parser.parse_args()
    root_file = args.file
    tree_name = args.tree
    event_index = args.index

    data = load_data(root_file, tree_name, event_index)

    plot_display(data, detector_geom['SK'], args.plot_Chgamma)


