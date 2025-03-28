
import uproot as up
import awkward as ak


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
    return True, [i for i in range(n_events)]
  

  elif isinstance(events_to_display, int): # one event display

    if events_to_display < 0 or events_to_display >= n_events:
      print('Error: event index out of bounds. Displaying first event instead.')
      return True, (0, 1)

    return True, (events_to_display, events_to_display)

  elif isinstance(events_to_display, tuple):
    start, stop = events_to_display

    if start < 0 or stop > n_events or start > stop:
      print('Error: events index out of bounds. Displaying first event instead.')
      return True, (0, 1)
  
    return True, (start, stop)

  elif isinstance(events_to_display, list):
    indices = sorted(events_to_display)
  
    if not indices:
      print('Error: empty list provided for events_to_display. Displaying first event instead.')
      return True, (0, 1)
  
    if indices[0] < 0 or indices[-1] >= n_events:
      print('Error: some event indices are out of bounds. Displaying first event instead.')
      return True, (0, 1)
  
    # Check if the list is contiguous.
    if indices[-1] - indices[0] == len(indices) - 1:
      return True, indices
  
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
    extra_data_keys = ['energy'] + [var for var in ('dwall', 'towall') if var in tree.keys()] + ['n_hits']
    extra_data_units = ['MeV'] + ['cm' for var in ('dwall', 'towall') if var in tree.keys()] + ['']

    all_keys = data_keys + extra_data_keys

    # Determine the selection method for uproot
    # in case of isinstance(events_to_display) == list, returns the list (if indices are coherent)
    is_contiguous, bounds = events_index_bounds(events_to_display, n_events)

    if is_contiguous:      
      entry_start, entry_stop = bounds[0], bounds[-1] + 1
      all_data = tree.arrays(all_keys, entry_start=entry_start, entry_stop=entry_stop)
  
    else: # Non-contiguous: fetch each event one by one.
      temp_data_list = []
      all_keys = data_keys + extra_data_keys

      for idx in bounds:  
        one_event_data = tree.arrays(all_keys, entry_start=idx, entry_stop=idx+1)
        temp_data_list.append(one_event_data[0])
      
      all_data = ak.Array(temp_data_list)
        
  events_dict = {k: all_data[k] for k in data_keys}
  events_dict['add_info'] = []
  
  for key, unit in zip(extra_data_keys, extra_data_units):
    #nice_litteral = {'label': r'$t_\mathrm{wall}$', 'unit': 'cm', 'values': }
    litteral = {'label': key, 'unit': unit, 'values': all_data[key]}
    events_dict['add_info'].append(litteral)

  return events_dict, len(events_dict['hitx']), bounds