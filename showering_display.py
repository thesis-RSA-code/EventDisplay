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

    return color, ls, alpha, lw


def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x


detector_geom = {'SK': {'height': 3620.0, 'cylinder_radius': 3368.15/2, 'PMT_radius': 25.4}, 'HK': {'height': 6575.1, 'cylinder_radius': 6480/2, 'PMT_radius': 25.4}, 'WCTE': {'height': 338.0, 'cylinder_radius': 369.6/2, 'PMT_radius': 4.0}}

# load track data
print("Loading track data...")

with open("track_data_e.pkl", "rb") as file:  # "rb" mode for reading binary
    track_data = pck.load(file)

trackId = track_data["trackId"]
parentId = track_data["parentId"]
pId = track_data["pId"]
particleStart = track_data["particleStart"]
particleStop = track_data["particleStop"]
tracks = track_data["tracks"]
primary_index = track_data["primary_index"]
gammaStart = track_data["gammaStart"]
gammaStop = track_data["gammaStop"]
gammaId = track_data["gammaId"]

# load hit data

hitx = track_data["hitx"]
hity = track_data["hity"]
hitz = track_data["hitz"]
charge = track_data["charge"]


# pyvista plot

plotter = pv.Plotter(window_size=(800, 600))

# Plot particle tracks
print("Plotting particle tracks...")
for track in trackId:
    if track == 0:
        continue

    if pId[trackId == track] == 0:
        continue

    vertices = tracks[str(track)].to_numpy()
    line = pv.PolyData(vertices)
    line.lines = np.array([[len(vertices), *range(len(vertices))]])


    color, ls, alpha, lw = track_style(pId[trackId == track])
    plotter.add_mesh(line, color=color, line_width=lw, point_size=0.1, opacity=alpha)

# Plot gamma tracks
plot_gamma = False

if plot_gamma: 
    print("Plotting gamma tracks...")
    for start, stop in zip(gammaStart, gammaStop):
        if np.dot(stop - start, particleStop[primary_index]-particleStart[primary_index]) < 0:
            continue

        line = pv.Line(start, stop)
        line.lines = np.array([[2, 0, 1]])
        color, ls, alpha, lw = track_style(0)
        plotter.add_mesh(line, color=color, line_width=lw, opacity=alpha)


# Add detector hits as points
print("Adding detector hits as points...")
points = np.column_stack((hitx.to_numpy(), hity.to_numpy(), hitz.to_numpy()))
point_cloud = pv.PolyData(points)
plotter.add_points(
    point_cloud,
    scalars=rescale_color(charge),
    cmap="plasma",
    point_size=10,
    opacity=0.7,
    render_points_as_spheres=True,
)


# draw detector

print("Drawing detector...")

cylinder = pv.Cylinder(center=(0, 0, 0), direction=(0, 0, 1), radius=detector_geom['SK']['cylinder_radius'], height=detector_geom['SK']['height'])
plotter.add_mesh(cylinder, color="black")

for z in [-detector_geom['SK']['height']/2+10, detector_geom['SK']['height']/2-10]:

    # Parameters for the circle
    radius = detector_geom['SK']['cylinder_radius'] - 10 # Radius of the circle
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


# Set the plotter's view bounds
#radius = 3  # Adjust this based on your detector geometry
#plotter.set_scale(xscale=radius, yscale=radius, zscale=radius)

# Set camera position

print("Setting camera...")

# Set camera position
plotter.camera_position = [
    particleStart[primary_index]-np.array([200, 0, -200]),   # Camera position (x, y, z)
    particleStop[primary_index],   # Focal point (center of the view)
    (0, 0, 1),   # View up vector (defines the "up" direction)
]

plotter.camera.view_angle = 90  # Set FOV to 90 degrees for a wide angle

# Add axes labels
plotter.remove_scalar_bar()
plotter.add_axes()
plotter.show()