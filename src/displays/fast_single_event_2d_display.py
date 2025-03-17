
# General imports
import sys
import numpy as np  

import matplotlib.pyplot as plt

from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Custom imports
from utils.global_viz_utils import rescale_color, compute_PMT_marker_size, rescale_color_inv
from utils.detector_geometries import DETECTOR_GEOM



def plt_only_display(
  file_path,
  events_dic, 
  experiment, 
  events_to_display=0, 
  color='charge', 
  show=True, 
  save_path='', 
  save_file=''
  ):
  
  r"""
  Fast plot event display for a single event with matplotlib, possibility to save as pdf
  """
  
  print('Fast display =========================================================================================')

  PMT_radius = DETECTOR_GEOM[experiment]['PMT_radius']
  cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
  zMax = DETECTOR_GEOM[experiment]['height']/2
  zMin = -DETECTOR_GEOM[experiment]['height']/2

  if experiment == 'WCTE' : # make WCTE subPMTs smaller than what they really are, otherwise their spherical disposition will appear cramped when projected
    PMT_radius -= 2

    
  if not isinstance(events_to_display, int) :
    print('Error: only one event can be displayed with this function. Displaying first event instead.')
    events_to_display = 0

  print('Making the figure...')

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
  ax.add_patch(plt.Rectangle((-np.pi*cylinder_radius, zMin), 2*np.pi*cylinder_radius, 2*zMax, fill=False))
  ax.add_patch(plt.Circle((0, zMax+cylinder_radius), cylinder_radius, fill=False))
  ax.add_patch(plt.Circle((0, zMin-cylinder_radius), cylinder_radius, fill=False))

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

  if save_path:
    print('Saving figure...')

    if not save_file:
      save_file = file_path.split('/')[-1].split('.')[0] + '_' + str(events_to_display) + f".{plt.rcParams['savefig.format']}"

    print(f"Save Path: {save_path + '/' + save_file}")
    plt.savefig(save_path + save_file, bbox_inches="tight", transparent=True, dpi=300)

  if show : plt.show()
