
import uproot as up
import awkward as ak

import uproot as up
import numpy as np



def events_index_bounds(events_to_display, n_events):
  """
  Returns a tuple (is_contiguous, bounds) where:
    - If events_to_display is 'all', returns (True, (0, n_events)).
    - If events_to_display is a tuple or an int, returns (True, (start, stop)).
    - If events_to_display is a list:
      * If the list is contiguous, returns (True, (start, stop)).
      * Otherwise, returns (False, indices) so that events are fetched one by one.
  """
  if events_to_display == 'all':
    return True, (0, n_events)

  elif isinstance(events_to_display, tuple):
    start, stop = events_to_display

    if start < 0 or stop > n_events or start > stop:
      print('Error: events index out of bounds. Displaying first event instead.')
      return True, (0, 1)
  
    return True, (start, stop)

  elif isinstance(events_to_display, int):
  
    if events_to_display < 0 or events_to_display >= n_events:
      print('Error: event index out of bounds. Displaying first event instead.')
      return True, (0, 1)
  
    return True, (events_to_display, events_to_display + 1)

  elif isinstance(events_to_display, list):
    indices = sorted(set(events_to_display))
  
    if not indices:
      print('Error: empty list provided for events_to_display. Displaying first event instead.')
      return True, (0, 1)
  
    if indices[0] < 0 or indices[-1] >= n_events:
      print('Error: some event indices are out of bounds. Displaying first event instead.')
      return True, (0, 1)
  
    # Check if the list is contiguous.
    if indices[-1] - indices[0] == len(indices) - 1:
      return True, (indices[0], indices[-1] + 1)
  
    else:
      return False, indices
  
  else:
    print('Error: events_to_display should be an integer, a tuple, a list, or "all". Displaying first event instead.')
    return True, (0, 1)




def load_data_from_root(file_path, tree_name, events_to_display):
  """
  Load data from a ROOT file using uproot and project to 2D.

  - For 'all', a tuple/int, or a contiguous list, fetch the entire block via slicing.
  - For a non-contiguous list of indices, fetch each event one by one.
  """

  print('Loading data...')
  
  with up.open(file_path) as file:
    tree = file[tree_name]
    n_events = tree.num_entries
      
    data_keys = ['hitx', 'hity', 'hitz', 'charge', 'time']
    extra_data_keys = ['energy'] + [var for var in ('dwall', 'towall') if var in tree.keys()]

    # Determine the selection method for uproot
    is_contiguous, bounds = events_index_bounds(events_to_display, n_events)

    if is_contiguous:      
      entry_start, entry_stop = bounds
      all_data = tree.arrays(data_keys + extra_data_keys, entry_start=entry_start, entry_stop=entry_stop)
  
    else: # Non-contiguous: fetch each event one by one.
      
      event_indices = bounds  # This is a list of event indices.
      hitx_list, hity_list, hitz_list, charge_list, time_list = [], [], [], [], []
      extra_data_lists = [[] for _ in range(len(extra_data_keys))]

      for idx in event_indices:

        one_event_data = tree.arrays(data_keys + extra_data_keys, entry_start=idx, entry_stop=idx+1)
      
        # Each field is an array of length 1; extract the single element.
        hitx_list.append(one_event_data['hitx'][0])
        hity_list.append(one_event_data['hity'][0])
        hitz_list.append(one_event_data['hitz'][0])
        charge_list.append(one_event_data['charge'][0])
        time_list.append(one_event_data['time'][0])


        # To do : find a good way to extract & store one by one 
        # does it really needs to be optimized ?..
        # Pay attention to fit the all_data values type in the output
        # numpy arrays might be ok
        for key in zip(extra_data_keys, extra_data_lists):
          pass
        #energy_list.append(one_event_data['time'][0])


        
      hitx   = np.array(hitx_list)
      hity   = np.array(hity_list)
      hitz   = np.array(hitz_list)
      charge = np.array(charge_list)
      time   = np.array(time_list)
        
  events_dict = {k: all_data[k] for k in data_keys}
  events_dict['add_info'] = []
  
  for key in extra_data_keys:
    #nice_litteral = {'label': r'$t_\mathrm{wall}$', 'unit': 'cm', 'values': }
    litteral = {'label': key, 'unit': 'cm', 'values': all_data[key]}
    events_dict['add_info'].append(litteral)


  return events_dict, len(events_dict['hitx']), bounds