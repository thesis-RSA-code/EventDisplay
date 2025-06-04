
import numpy as np
import pyvista as pv


# Custom imports
from utils.root.load_data_from_root import load_data_from_root
from utils.root.project_2d_from_root import project2d



# To do (21/02 Erwan) : add graph support here (if graph else ...)
def prepare_data(file_path, tree_name, experiment, events_to_display, extra_data_keys=[], extra_data_units=[]):
  
  events_dict, n_events, event_indices = load_data_from_root(file_path, tree_name, events_to_display, extra_data_keys=extra_data_keys, extra_data_units=extra_data_units)

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
        self.size_data= size
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


# ============================ Showering display utilities =======================================


def make_dashed_line(vertices, dash_length=1.0, gap_length=0.5):
    points = []
    lines = []
    count = 0

    # Go segment by segment
    total_len = 0.0
    for i in range(len(vertices) - 1):
        p0 = vertices[i]
        p1 = vertices[i + 1]
        seg_vec = p1 - p0
        seg_len = np.linalg.norm(seg_vec)

        if seg_len == 0:
            continue  # skip degenerate segments

        direction = seg_vec / seg_len
        t = 0.0

        # Step along the segment with dash+gap cycles
        while t < seg_len:
            dash_start = p0 + direction * t
            t_end = min(t + dash_length, seg_len)
            dash_end = p0 + direction * t_end
            points.extend([dash_start, dash_end])
            lines.append([2, count, count + 1])
            count += 2
            t += dash_length + gap_length

    poly = pv.PolyData()
    poly.points = np.array(points)
    poly.lines = np.hstack(lines)
    return poly


# color, linestyle, alpha, linewidth of tracks for showering_display
def track_style(pid):
    match pid:
        case 11:
            color, ls, alpha, lw = 'blue', '-', 1, 2
        case -11:
            color, ls, alpha, lw = 'blue', '--', 1, 2
        case 13:
            color, ls, alpha, lw = 'green', '-', 1, 2
        case -13:
            color, ls, alpha, lw = 'green', '--', 1, 2
        case 12:
            color, ls, alpha, lw = 'skyblue', '-', 0.5, 1
        case -12:
            color, ls, alpha, lw = 'skyblue', '--', 0.5, 1
        case 14:
            color, ls, alpha, lw = 'mediumseagreen', '-', 0.5, 1
        case -14:
            color, ls, alpha, lw = 'mediumseagreen', '--', 0.5, 1
        case 211:
            color, ls, alpha, lw = 'red', '-', 1, 2
        case -211:
            color, ls, alpha, lw = 'red', '--', 1, 2
        case 111:
            color, ls, alpha, lw = 'purple', '-', 1, 2
        case 2112:
            color, ls, alpha, lw = 'navy', '-', 1, 4
        case 2212:
            color, ls, alpha, lw = 'darkred', '-', 1, 4
        case 22:
            color, ls, alpha, lw = 'orange', '-', 0.5, 0.5
        case 0:
            color, ls, alpha, lw = 'gold', '-', 0.15, 0.5
        case _:
            # Default case – you can adjust the default values as needed.
            color, ls, alpha, lw = 'grey', '-', 1, 1
    return color, ls, alpha, lw


def add_custom_legend(plotter, pId):

    # flavour legend
    flavour_id  = np.unique(np.abs(pId))
    legend_entries = [(str(int(id)), track_style(id)[0], 'rectangle') for id in flavour_id]

    # particle/antiparticle legend
    #legend_entries.append({'label': 'particle', 'color': 'black', 'face': pv.Line()})

    # for pid in np.unique(np.abs(pId)):
    #     color, ls, alpha, lw = track_style(pid)
    #     line = pv.Line()
    #     plotter.add_mesh(line, line_width=lw, color=color, opacity=alpha, label=str(pid))

    plotter.add_legend(legend_entries, bcolor='grey', loc='upper right', size=(0.12, 0.12), border=True, background_opacity=0.5)


