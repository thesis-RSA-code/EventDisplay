
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


class scatter(): # new scatter class to update the size of the markers when resizing the figure, from https://stackoverflow.com/questions/48172928/scale-matplotlib-pyplot-axes-scatter-markersize-by-x-scale/48174228#48174228
    
    def __init__(self, x, y, ax, pmt_radius, size=1, **kwargs):
        
        self.n = len(x)
        self.ax = ax
        self.ax.figure.canvas.draw()
        self.size_data=size
        self.size = size
        self.pmt_radius = pmt_radius

        self.sc = ax.scatter(x,y,s=self.size,**kwargs)
    
        self._resize()
        self.cid = ax.figure.canvas.mpl_connect('draw_event', self._resize)

    def _resize(self, event=None):
        
        pmt_radius = self.pmt_radius
        M = self.ax.transData.get_matrix()
        xscale = M[0,0]
        ppd=72./self.ax.figure.dpi
        s = xscale * 2 * pmt_radius * ppd

        if s != self.size:
            self.sc.set_sizes(s**2*np.ones(self.n))
            self.size = s
            self._redraw_later()
    
    def _redraw_later(self):
        
        self.timer = self.ax.figure.canvas.new_timer(interval=10)
        self.timer.single_shot = True
        self.timer.add_callback(lambda : self.ax.figure.canvas.draw_idle())
        self.timer.start()


def rescale_color_inv(x_r, x0, sigma) : # inverse sigmoid to get back to original color scale
  
    return x0 + sigma * np.log(x_r/(1-x_r)) 


def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x
