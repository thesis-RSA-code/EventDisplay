import os
import sys 
import argparse

import matplotlib.pyplot as plt


# Custom imports
from displays.fast_single_event_2d_display import plt_only_display
from displays.tk_2d_display import tk_2d_display


from utils.global_viz_utils import prepare_data
from utils.detector_geometries import DETECTOR_GEOM


#matplotlib.use('Agg')
#os.environ["XDG_SESSION_TYPE"] = "xcb" # to avoid error with tkinter on some systems


def main(tk, file_path, tree_name, experiment, events_to_display='all', extra_data_keys=[], extra_data_units=[], color='charge', show=True, save_path='', save_file='') : 

  # Fetch the data
  #data_keys = ["hitx", "hity", "hitz", "charge", "time"]
  events_dict, n_events, event_indices = prepare_data(file_path, tree_name, experiment, events_to_display, extra_data_keys, extra_data_units)

  # main function to display events
  if tk:
    tk_2d_display(events_dict, event_indices, experiment)
  else :
    plt_only_display(file_path, events_dict, experiment, events_to_display, color, show, save_path, save_file)



if __name__ == "__main__":

  parser = argparse.ArgumentParser(description="Access events root file and display specified events.")

  # MANDATORY arguments
  parser.add_argument(
      "-e", "--experiment", type=str, choices=DETECTOR_GEOM.keys(),
      required=True, help=f"Experiment type {DETECTOR_GEOM.keys()}."
  )
  parser.add_argument(
      "-f", "--file", type=str, required=True,
      help="Full path to the events root file."
  )
  
  # OPTIONAL arguments
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
        "-ed", "--extra_data", type=str, nargs='*', default=[],
        help="Extra data keys to be loaded from the root file. Provide as space-separated values."
  )
  parser.add_argument(
        "-eu", "--extra_data_units", type=str, nargs='*', default=[],
        help="Units for the extra data keys. Provide as space-separated values. Must match the order and lenghts of extra_data."
  )
  parser.add_argument(
      "-tk", "--tkinter_GUI", action="store_true",
      help="Use tkinter GUI to display events."
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
  parser.add_argument(
    "-st", "--save_type", type=str, default="pdf",
    help="Type of the file to save the event display of a single event. Will be passed to plt.rcParams. Default is pdf."
  )
  parser.add_argument(
      "-s", "--show", action="store_true",
      help="Show the event display of a single event. Supposed to be way faster that multiple events display" 
  )

  args = parser.parse_args()


  # Parse `events_to_display`
  if args.display.lower() == "all":
      events_to_display = "all"
      
  elif ":" in args.display: # Parse range of events, e.g., "3:10"
      start, end = map(int, args.display.split(":"))
      events_to_display = list(range(start, end + 1))
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
  print(f"Use tkinter GUI: {args.tkinter_GUI}")
  
  # If saving (only possible in single display mode), defined the storage format
  if args.save_path:
    plt.rcParams['savefig.format'] = args.save_type

  # Check if using tk-based display
  tk_display = args.tkinter_GUI or isinstance(events_to_display, (tuple, list)) or events_to_display == 'all'

  extra_data_keys = args.extra_data
  extra_data_units = args.extra_data_units

  print(f"Extra data keys: {extra_data_keys}")

  if len(extra_data_keys) != len(extra_data_units):
      print("Error: The number of extra data keys must match the number of extra data units.")
      sys.exit(1)

  main(
    tk_display,
    args.file,
    args.tree, 
    args.experiment,
    events_to_display=events_to_display,
    extra_data_keys=extra_data_keys,
    extra_data_units=extra_data_units,
    color=args.color, 
    show=args.show, 
    save_path=args.save_path, 
    save_file=args.save_file
    )


