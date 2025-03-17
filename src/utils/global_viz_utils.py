
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

def compute_PMT_marker_size(pmt_radius, fig, ax) : # compute the size of PMT scatter markers in points^2 given the PMT radius in cm for a given figure and axes
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    dpi = fig.get_dpi()
    fig_width, fig_height = fig.get_size_inches() * dpi
    x_points_per_data_unit = fig_width / (xlim[1] - xlim[0])
    y_points_per_data_unit = fig_height / (ylim[1] - ylim[0])

    avg_points_per_data_unit = (x_points_per_data_unit + y_points_per_data_unit) / 2
    sizes_in_points2 = (pmt_radius * avg_points_per_data_unit) ** 2

    return sizes_in_points2


def rescale_color_inv(x_r, x0, sigma) : # inverse sigmoid to get back to original color scale
    return x0 + sigma * np.log(x_r/(1-x_r)) 

def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x
