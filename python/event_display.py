import os
import argparse

import numpy as np
import uproot as up
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import tkinter as tk
import awkward as ak

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable


plt.rcParams['savefig.format'] = 'pdf'

#matplotlib.use('Agg')
#os.environ["XDG_SESSION_TYPE"] = "xcb" # to avoid error with tkinter on some systems

# Some useful detector dimensions (in cm) ======================================================================================

detector_geom = {
  'SK': {'height': 3620.0, 'cylinder_radius': 3368.15/2, 'PMT_radius': 25.4}, 
  'HK': {'height': 6575.1, 'cylinder_radius': 6480/2, 'PMT_radius': 25.4}, 
  'WCTE': {'height': 271.4235, 'cylinder_radius': 307.5926/2, 'PMT_radius': 4.0}
}


# Utility functions =======================================================================================

def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x


def rescale_color_inv(x_r, x0, sigma) : # inverse sigmoid to get back to original color scale

    return x0 + sigma * np.log(x_r/(1-x_r)) 


def compute_PMT_marker_size(PMT_radius, fig, ax) : # compute the size of PMT scatter markers in points^2 given the PMT radius in cm for a given figure and axes
    
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    dpi = fig.get_dpi()
    fig_width, fig_height = fig.get_size_inches() * dpi
    x_points_per_data_unit = fig_width / (xlim[1] - xlim[0])
    y_points_per_data_unit = fig_height / (ylim[1] - ylim[0])

    avg_points_per_data_unit = (x_points_per_data_unit + y_points_per_data_unit) / 2

    sizes_in_points2 = (PMT_radius * avg_points_per_data_unit) ** 2

    return sizes_in_points2


def events_index_bounds(events_to_display, n_events) : # get the bounds of the events to display

  if events_to_display == 'all' : # display all events
      event_indices = [i for i in range(n_events)]

  elif isinstance(events_to_display, tuple) : # display only a subrange of events

    if events_to_display[0] < 0 or events_to_display[1] > n_events or events_to_display[0] > events_to_display[1] :
      print('Error: events index out of bounds. Displaying first event instead.')
      event_indices = [0]

    else :
      event_indices = [event_index for event_index in range(events_to_display[0], events_to_display[-1])]

  elif isinstance(events_to_display, list) : # display a list of specific event indices
    event_indices = events_to_display
    
  elif isinstance(events_to_display, int) : # display only one event

    if events_to_display < 0 or events_to_display >= n_events :
      print('Error: event index out of bounds. Displaying first event instead.')
      event_indices = [0]

    else :
      event_indices = [events_to_display]

  else :
    print('Error: events_to_display should be an integer, a tuple or "all". Displaying first event instead.')
    event_indices = [0]

  return event_indices


def plot_event_3D(path2events, events_file, event_index, detector_geom, experiment) : # simple 3D plot of a given event, just to check if everything is in order
  
  file = up.open(path2events + events_file)
  events_root = file['root_event'] # TTree of events variables {'hitx', 'hity', 'hitz', 'charge', 'time'}
  hitx = events_root['hitx'].array()
  hity = events_root['hity'].array()
  hitz = events_root['hitz'].array()
  charge = events_root['charge'].array()
  PMT_radius = detector_geom[experiment]['PMT_radius']
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.scatter(hitx[event_index], hity[event_index], hitz[event_index], s=1, c=rescale_color(charge[event_index]), cmap='plasma')
  plt.show()


# Deal with data =======================================================================================

def project2d(X, Y, Z, detector_geom, experiment) : # project 3D PMT positions of an event to 2D unfolded cylinder

  cylinder_radius = detector_geom[experiment]['cylinder_radius']
  zMax = detector_geom[experiment]['height']/2
  zMin = -detector_geom[experiment]['height']/2

  Xproj = ak.zeros_like(X)
  Yproj = ak.zeros_like(Y)

  if experiment == 'WCTE' : # WCTE bottom and top cap no symmetrical! top PMTs are further away from the last row of cylinder PMTs than the bottom PMTs, and beware of spherical structure of mPMTs
    # values adjusted by hand so as to correctly identify the top and bottom PMTs, maybe get info from WCSim in PMT id or something
    eps_top = 50
    eps_bottom = 50
    
    # WCTE is rotated in WCSim to have beam on the z axis, rotate it back to have cylinder axis on z axis like SK and HK, then rotate a tiny bit around z axis so as not to cut a column of PMTs in half (but also rotate the top and bottom caps though...)
    print('Rotating WCTE events...')
    thetax = np.pi/2
    thetaz = 4.53
    
    # rotate around x axis
    X_Rx = X
    Y_Rx = np.cos(thetax)*Y - np.sin(thetax)*Z
    Z_Rx = np.sin(thetax)*Y + np.cos(thetax)*Z

    # rotate around z axis
    X = np.cos(thetaz)*X_Rx + np.sin(thetaz)*Y_Rx
    Y = -np.sin(thetaz)*X_Rx + np.cos(thetaz)*Y_Rx
    Z = Z_Rx

  else :
    eps_top = 0.01
    eps_bottom = 0.01

  top_cap_mask = Z > zMax - eps_top
  bottom_cap_mask = Z < zMin + eps_bottom
  cylinder_mask = np.logical_not(top_cap_mask | bottom_cap_mask)

  # cylinder 

  azimuth = np.arctan2(Y, X)
  azimuth = ak.where(azimuth < 0, 2*np.pi + azimuth, azimuth)


  Xproj = ak.where(cylinder_mask, cylinder_radius * (azimuth - np.pi), Xproj)
  Yproj = ak.where(cylinder_mask, Z, Yproj)

  # top cap
  Xproj = ak.where(top_cap_mask, - Y, Xproj)
  Yproj = ak.where(top_cap_mask, X + zMax + cylinder_radius, Yproj)

  # bottom cap
  Xproj = ak.where(bottom_cap_mask, - Y, Xproj)
  Yproj = ak.where(bottom_cap_mask, - X + zMin - cylinder_radius, Yproj)

  return Xproj, Yproj


def load_data(file_path, tree_name, detector_geom, experiment, events_to_display='all') : # load data from root file and project it to 2D

    print('Loading data...')

    file = up.open(file_path)
    events_root = file[tree_name] # TTree of events variables {'hitx', 'hity', 'hitz', 'charge', 'time'}

    n_events = len(events_root['hitx'].array()) # number of events

    hitx = events_root['hitx'].array()
    hity = events_root['hity'].array()
    hitz = events_root['hitz'].array()
    charge = events_root['charge'].array()
    time = events_root['time'].array()

    event_indices = events_index_bounds(events_to_display, n_events)

    events_dic = {'xproj': ak.zeros_like(hitx), 'yproj': ak.zeros_like(hity), 'charge': ak.zeros_like(charge), 'time': ak.zeros_like(hitx)} # python dictionary to store data

    print('2D projection...')

    Xproj, Yproj = project2d(hitx[event_indices], hity[event_indices], hitz[event_indices], detector_geom, experiment)
    events_dic['xproj'] = Xproj
    events_dic['yproj'] = Yproj
    events_dic['charge'] = charge[event_indices]
    events_dic['time'] = time[event_indices]

    # additional info

    events_dic['add_info'] = []

    if 'new_twall' in events_root.keys() :
      events_dic['add_info'].append({'label': r'$t_\mathrm{wall}$', 'unit': 'cm', 'values': events_root['new_twall'].array()[event_indices]})

    if 'new_dwall' in events_root.keys() :
      events_dic['add_info'].append({'label': r'$d_\mathrm{wall}$', 'unit': 'cm', 'values': events_root['new_dwall'].array()[event_indices]})

    if 'energy' in events_root.keys() :
      events_dic['add_info'].append({'label': r'$E$', 'unit': 'MeV', 'values': events_root['energy'].array()[event_indices]})

    return events_dic, n_events


# Fast plot one event =========================================================================================================================

def show_event_display_plt(file_path, tree_name, detector_geom, experiment, events_to_display=0, color='charge', show=True, save_path='', save_file='') : # fast plot event display for a single event with matplotlib, possibility to save as pdf
    
    print('Fast display =========================================================================================')

    PMT_radius = detector_geom[experiment]['PMT_radius']
    cylinder_radius = detector_geom[experiment]['cylinder_radius']
    zMax = detector_geom[experiment]['height']/2
    zMin = -detector_geom[experiment]['height']/2

    if experiment == 'WCTE' : # make WCTE subPMTs smaller than what they really are, otherwise their spherical disposition will appear cramped when projected
      PMT_radius -= 2

      
    if not isinstance(events_to_display, int) :
      print('Error: only one event can be displayed with this function. Displaying first event instead.')
      events_to_display = 0

    events_dic, n_events = load_data(file_path, tree_name, detector_geom, experiment, events_to_display=events_to_display)

    print('Creating display...')

    # set figure and axes

    fig, ax = plt.subplots(figsize = (6,6))

    fig.suptitle(experiment + ' Event Display')

    add_info_string = ', '.join([info['label'] + r'$ = $' + str(info['values'][0].round(2)) + ' ' + info['unit'] for info in events_dic['add_info']])
    plt.title(add_info_string)

    ax.set_xlim(-np.pi*cylinder_radius - 10, np.pi*cylinder_radius + 10)
    ax.set_ylim(zMin-2*cylinder_radius - 10, zMax+2*cylinder_radius + 10)
    ax.set_aspect('equal')      
    ax.set_xlabel(r'$x$ (cm)')
    ax.set_ylabel(r'$z$ (cm)')

    # draw detector
    ax.add_patch(plt.Rectangle((-np.pi*cylinder_radius, zMin), 2*np.pi*cylinder_radius, 2*zMax, fill=True, color='black'))
    ax.add_patch(plt.Circle((0, zMax+cylinder_radius), cylinder_radius, fill=True, color='black'))
    ax.add_patch(plt.Circle((0, zMin-cylinder_radius), cylinder_radius, fill=True, color='black'))

    #ax.set_facecolor('grey')

    # draw event
    c = rescale_color(events_dic[color][0])
    norm = Normalize(vmin=np.min(c), vmax=np.max(c))
    scatter = ax.scatter(events_dic['xproj'][0], events_dic['yproj'][0], s=compute_PMT_marker_size(PMT_radius, fig, ax), c=c, cmap='plasma', norm=norm)
    
    # nice colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    cbar = plt.colorbar(scatter, label=color, cax=cax)

    ticks = np.linspace(np.min(c), np.max(c), num=4)
    tick_labels = [f"{rescale_color_inv(tick, np.median(events_dic[color][0]), np.std(events_dic[color][0])):.1f}" for tick in ticks]
    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)

    #ax.set_axis_off()
    

    if save_path != '' :
      print('Saving figure...')

      if save_file == '' :
        save_file = file_path.split('/')[-1].split('.')[0] + '_' + str(events_to_display) + '.pdf'

      plt.savefig(save_path + save_file, bbox_inches="tight", transparent=True, dpi=300)

    if show : plt.show()


# Tkinter GUI =======================================================================================================================

def show_event_display_tk(file_path, tree_name, detector_geom, experiment, events_to_display='all') : # plot event display with tkinter animation

    print('Tkinter GUI =========================================================================================')

    PMT_radius = detector_geom[experiment]['PMT_radius']
    cylinder_radius = detector_geom[experiment]['cylinder_radius']
    zMax = detector_geom[experiment]['height']/2
    zMin = -detector_geom[experiment]['height']/2

    if experiment == 'WCTE' : # make WCTE subPMTs smaller than what they really are, otherwise their spherical disposition will appear cramped when projected
      PMT_radius -= 2

    events_dic, n_events = load_data(file_path, tree_name, detector_geom, experiment, events_to_display=events_to_display)

    print('Opening display...')

    times = events_dic['time']

    def update_time_slider(event_index) : # update time slider according to event_slider

      event_index = int(event_index) 
      time = times[event_index]
      time = np.sort(time)

      wt.config(from_=time[0], to=time[-1], resolution=(time[-1]-time[0])/100000)
      wt.set(times[event_index][-1])


    fig, ax = plt.subplots(figsize = (6,6))


    def plot(input): # plot command to be called by tkinter slider

      # set figure and axes
      ax.clear()

      fig.suptitle(experiment + ' Event Display')

      ax.set_xlim(-np.pi*cylinder_radius - 10, np.pi*cylinder_radius + 10)
      ax.set_ylim(zMin-2*cylinder_radius - 10, zMax+2*cylinder_radius + 10)
      ax.set_aspect('equal')
      ax.set_xlabel(r'$x$ (cm)')
      ax.set_ylabel(r'$z$ (cm)')

      # draw detector
      ax.add_patch(plt.Rectangle((-np.pi*cylinder_radius, zMin), 2*np.pi*cylinder_radius, 2*zMax, fill=True, color='black'))
      ax.add_patch(plt.Circle((0, zMax+cylinder_radius), cylinder_radius, fill=True, color='black'))
      ax.add_patch(plt.Circle((0, zMin-cylinder_radius), cylinder_radius, fill=True, color='black'))

      # get event
      if input == 'event_slider':

        event_index = wE.get()
        wB.delete(0, tk.END)  # Clear any existing value
        wB.insert(0, event_indices[event_index]) 
        update_time_slider(event_index)
      
      elif input == 'entry_box':

        event_index_original = wB.get()

        if not(event_index_original.isdigit()) :
          print('Error: event index should be an integer. Displaying first event instead.')
          event_index = 0
          wB.delete(0, tk.END)
          wB.insert(0, event_index)

        else :
          event_index_original = int(event_index_original)

        if not(event_index_original in event_indices) :
          print('Error: event index out of bounds. Displaying first event instead.')
          event_index_original = event_indices[0]
          wB.delete(0, tk.END)
          wB.insert(0, event_index_original)

        event_index = event_indices.index(event_index_original)
        wE.set(event_index)
        update_time_slider(event_index)

      elif input == 'time_slider':

        event_index = int(wE.get())

      else :
        event_index = 0

      add_info_string = ', '.join([info['label'] + r'$ = $' + str(info['values'][event_index].round(2)) + ' ' + info['unit'] for info in events_dic['add_info']])
      plt.title(add_info_string)
      
      x2D, y2D, charge, time = events_dic['xproj'][event_index], events_dic['yproj'][event_index], events_dic['charge'][event_index], events_dic['time'][event_index]

      sorting_indices = np.argsort(time) # sort by time of trigger, so as to display them accordingly
      x2D, y2D, charge, time = x2D[sorting_indices], y2D[sorting_indices], charge[sorting_indices], time[sorting_indices]

      tmax = wt.get()

      x_before_t, y_before_t, charge_before_t = x2D[time < tmax], y2D[time < tmax], charge[time < tmax]
      scatter = ax.scatter(x_before_t, y_before_t, s = compute_PMT_marker_size(PMT_radius, fig, ax), c=rescale_color(charge_before_t), cmap='plasma')

      canvas.draw()

    # defining tkinter window ==========================
    root = tk.Tk()
    root.wm_title("Event Display")

    # embedding matplotlib figure in tkinter window ==============
    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()

    event_indices = events_index_bounds(events_to_display, n_events)

    # event slider =====================================================
    tk.Label(root, text = 'Slide events').pack()
    wE = tk.Scale(root, from_=0, to=len(event_indices)-1, orient=tk.HORIZONTAL, command=lambda _: plot('event_slider'), showvalue=0)
    wE.pack()

    # entry box =========================================================
    wB = tk.Entry(root)
    wB.pack()
    tk.Label(root, text='', width=2).pack()
    wB.insert(0, event_indices[0])

    button = tk.Button(root, text='Display Event', command=lambda : plot('entry_box'))
    button.pack()

    # time slider =======================================================
    tk.Label(root, text = 'Time').pack()
    wt = tk.Scale(root, orient=tk.HORIZONTAL, command=lambda _: plot('time_slider'))
    wt.pack()

    # custop label for slider ===========================================

    update_time_slider(0)

    def _quit():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _quit)    
    plot('0')
    root.mainloop()


# Main ==============================================================================================================

def show_event_display(file_path, tree_name, detector_geom, experiment, events_to_display='all', tk=False, color='charge', show=True, save_path='', save_file='') : # main function to display events

  if tk:
    show_event_display_tk(file_path, tree_name, detector_geom, experiment, events_to_display)

  else :
    show_event_display_plt(file_path, tree_name, detector_geom, experiment, events_to_display, color, show, save_path, save_file)
   

if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Access events root file and display specified events.")

  # Define mandatory arguments
  parser.add_argument(
      "-e", "--experiment", type=str, choices=["SK", "HK", "WCTE"],
      required=True, help="Experiment type ('SK', 'HK', or 'WCTE')."
  )
  parser.add_argument(
      "-f", "--file", type=str, required=True,
      help="Full path to the events root file."
  )

  # Define optional arguments
  parser.add_argument(
      "-d", "--display", type=str, default="0",
      help="Events to display: 'all' to display all events, a single integer for a specific event index (e.g. '10'), "
             "a range 'start:end' (e.g., '3:10') or a list of event indices separated by | (e.g. '1|76|356'). Default first event."
  )
  parser.add_argument(
      "-t", "--tree", type=str, default="root_event",
      help="Name of the TTree inside the root file (default: 'root_event')."
  )
  parser.add_argument(
      "-tk", "--tkinter_GUI", action="store_true",
      help="Use tkinter GUI to display events."
  )
  parser.add_argument(
      "-s", "--show", action="store_true",
      help="Show the event display of a single event." 
  )
  parser.add_argument(
      "-c", "--color", type=str, default="charge", choices=["charge", "time"],
      help="Color scheme for the single event event display: 'charge' or 'time'."
  )
  parser.add_argument(
      "-sp", "--save_path", type=str, default="",
      help="Path where to save the event display of a single event. If empty, the event display will not be saved."
  )
  parser.add_argument(
      "-sf", "--save_file", type=str, default="",
      help="Name of the file to save the event display of a single event. When it is not specified but save_path is, the file name will be the name of the root file followed by the event index. Only used when save_path is not empty. Default format is pdf."
  )


  args = parser.parse_args()


  # Parse `events_to_display`
  if args.display.lower() == "all":
      events_to_display = "all"
      
  elif ":" in args.display: # Parse range of events, e.g., "3:10"
      start, end = map(int, args.display.split(":"))
      events_to_display = (start, end)
  elif "|" in args.display:
      # Parse a list of events, e.g. "3|49|107"
      events_to_display = [int(index) for index in args.display.split("|")]
  else:
      # Single event index
      events_to_display = int(args.display)

    
  # Output the parsed arguments
  print("Parsed Arguments:")
  print(f"Experiment: {args.experiment}")
  print(f"Path to Events File: {args.file}")
  print(f"Event(s) to Display: {events_to_display}")
  print(f"TTree Name: {args.tree}")


  if args.tkinter_GUI or isinstance(events_to_display, tuple) or ( events_to_display == 'all') or (isinstance(events_to_display, list)) :
    tk_display = True
  else:

    tk_display = False
    if args.save_path != "" :
      print(f"Save Path: {args.save_path + args.save_file}")

    #print(f"Color Scheme: {args.color}")


  # Call the main function
  show_event_display(args.file, args.tree, detector_geom, args.experiment, events_to_display=events_to_display, tk=tk_display, color=args.color, show=args.show, save_path=args.save_path, save_file=args.save_file)




