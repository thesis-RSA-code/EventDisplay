
import numpy as np


# Custom imports
from utils.root.load_data_from_root import load_data_from_root
from utils.root.project_2d_from_root import project2d


# To do (21/02 Erwan) : add graph support here (if graph else ...)
def prepare_data(file_path, tree_name, experiment, events_to_display):

  events_dict, n_events, event_indices = load_data_from_root(file_path, tree_name, events_to_display)

  print('Computing 2D projection...')
  Xproj, Yproj = project2d(events_dict['hitx'], events_dict['hity'], events_dict['hitz'], experiment)
  print("Done")
  events_dict['xproj'] = Xproj
  events_dict['yproj'] = Yproj

  return events_dict, n_events, event_indices


def compute_PMT_marker_size(pmt_radius, ax) : # compute the size of PMT scatter markers in points^2 given the PMT radius in cm for a given figure and axes
  
    M = ax.transData.get_matrix()
    xscale = M[0,0]
    yscale = M[1,1]

    return (xscale * pmt_radius)**2


def update_marker_size(event, PMT_radius, fig, ax, scatter, npoints) : # update the size of PMT scatter markers in points^2 given the PMT radius in cm for a given figure and axes
    
    new_size = compute_PMT_marker_size(PMT_radius, ax)
    scatter.set_sizes([new_size] * npoints)
    fig.canvas.flush_events()       # flush GUI event queue
    fig.canvas.draw_idle() 


def rescale_color_inv(x_r, x0, sigma) : # inverse sigmoid to get back to original color scale
  
    return x0 + sigma * np.log(x_r/(1-x_r)) 


def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x
