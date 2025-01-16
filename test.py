import numpy as np
import matplotlib.pyplot as plt

import matplotlib.colors as mcolors
import awkward as ak
import uproot as up

from mpl_toolkits.mplot3d import Axes3D
from event_display import compute_PMT_marker_size, rescale_color

if __name__ == "__main__":

    path2events = '/home/mathieu-ferey/Documents/These/Codes/Data/SK/30_mu-_1000MeV_GPS.root'
    event_index = 6

    detector_geom = {
    'SK': {'height': 3620.0, 'cylinder_radius': 3368.15/2, 'PMT_radius': 25.4}, 
    'HK': {'height': 6575.1, 'cylinder_radius': 6480/2, 'PMT_radius': 25.4}, 
    'WCTE': {'height': 338.0, 'cylinder_radius': 369.6/2, 'PMT_radius': 4.0}
    }
    experiment = 'SK'

    file = up.open(path2events)

    events_root = file['root_event'] # TTree of events variables {'hitx', 'hity', 'hitz', 'charge', 'time'}
    hitx = events_root['hitx'].array()
    hity = events_root['hity'].array()
    hitz = events_root['hitz'].array()
    charge = events_root['charge'].array()
    PMT_radius = detector_geom[experiment]['PMT_radius']

    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(111, projection='3d')

    markersize = compute_PMT_marker_size(PMT_radius, fig, ax)
    ax.scatter(hitx[event_index], hity[event_index], hitz[event_index], s=30, c=rescale_color(charge[event_index]), cmap='plasma')




    #ax.set_xlim(-detector_geom[experiment]['cylinder_radius'], detector_geom[experiment]['cylinder_radius'])
    #ax.set_ylim(-detector_geom[experiment]['cylinder_radius'], detector_geom[experiment]['cylinder_radius'])
    #ax.set_zlim(-detector_geom[experiment]['height']/2, detector_geom[experiment]['height']/2)

    #ax.set_aspect('equal')
    #ax.set_axis_off()

    ax.view_init(elev=45, azim=0)
    ax.dist = 100
    ax.set_proj_type('persp')


    plt.show()
