
import numpy as np

import tkinter as tk
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

# Custom imports
from utils.detector_geometries import DETECTOR_GEOM
from utils.global_viz_utils import rescale_color, rescale_color_inv, compute_PMT_marker_size


# plot event display with tkinter animation
def tk_2d_display(events_dict, event_indices, experiment):
        
    if event_indices[0] == event_indices[-1] : # only one event to display
      event_indices = [event_indices[0]]

    
    print('Tkinter GUI =========================================================================================')

    PMT_radius = DETECTOR_GEOM[experiment]['PMT_radius']
    cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
    zMax = DETECTOR_GEOM[experiment]['height']/2
    zMin = -DETECTOR_GEOM[experiment]['height']/2

    # make WCTE subPMTs smaller than what they really are, otherwise their spherical disposition will appear cramped when projected
    if experiment == 'WCTE' : 
      PMT_radius -= 2

    print('Opening display...')

    times = events_dict['time']

    def update_time_slider(event_index) : # update time slider according to event_slider

      event_index = int(event_index) 
      time = times[event_index]
      time = np.sort(time)

      if len(time) == 0 :
        print(f'Warning: event {event_index} appears to be empty.')
        time = [0, 1]

      wt.config(from_=time[0], to=time[-1], resolution=(time[-1]-time[0])/100000)
      wt.set(time[-1])


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

      add_info_string = ', '.join([info['label'] + r'$ = $' + str(info['values'][event_index].round(2)) + ' ' + info['unit'] for info in events_dict['add_info']])
      plt.title(add_info_string)
      
      x2D, y2D, charge, time = events_dict['xproj'][event_index], events_dict['yproj'][event_index], events_dict['charge'][event_index], events_dict['time'][event_index]

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
