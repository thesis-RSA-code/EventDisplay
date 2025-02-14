
# generic imports
import sys
import os.path as osp
import numpy as np
import pyvista as pv

# torch imports 
import torch

# pyg imports
from torch_geometric.data import InMemoryDataset
from torch_geometric.transforms import KNNGraph

pv.global_theme.colorbar_orientation = 'vertical'



# Graph loading code ===================================================================================================

"""
Notes :
    About the graph creation from an event : decision NOT TO USE the pre_transform
    parameter existing in the InMemoryDataset class of torch_geometric because 
        1. The name would not be explicit
        2. Is it supposed to be a list of functions to apply to the data points 
            before turning them into a graph. So it should not changes the nature 
            of the data. Or creating a graph changes the nature of the data.
        3. There should be only one function to call to create a graph, so a list
            of function is not adapted.
"""


class DatasetFromProcessed(InMemoryDataset):
    r"""" 
    This class is it never supposed to see .root files  
    It can :
        - load graphs from a .pt
        - compute edges using self.compute_edges()
    And a transform argument can be passed at initialization.
    
    If compute_edges() is called, self._data will be changed (not self.data)
    and self._data_list will set to None.
    These modifications will only live inside the class (so 'locally'), 
    not flushed on the disk.

    Args:
            graph_folder_path: str 
                Root directory where the dataset should be saved.
            graph_file_names: str
                Names of the .pt files
            nb_datapoints : int # À FAIRE
                Number of datapoints to keep from the original dataset.
            verbose: int  [0 ou 1]
                Degree of information printed during the traitement of the .root
            transform (Optional): (list of) function
                transform argument from torch_geometric InMemoryDataset class
    """

    def __init__(
            self, 
            graph_folder_path : str,
            graph_file_names : list=[''],
            transform = None,
            verbose : int = 0,
            transforms= None  # Do not use. Only for compatibility with watchmal. In discussion with Nick to solve this redundancy.
    ):

        self.verbose = verbose

        # Where to look for the data
        self.graph_folder_path = graph_folder_path
        self.graph_file_names  = graph_file_names

        # What to apply to the data
        self.transform       = transform

        # Load the pre_transform argument
        f = self.graph_folder_path + '/processed/pre_transform.pt'
        print(f"Looking for pre_transform.pt at : {f}")
        if not osp.exists(f):
            print(f"No pre_transform.pt found")
            self.pre_transform = None
        else :
            print(f"Found a pre_transorm.pt")
            self.pre_transform = torch.load(f)

        super().__init__(
            root=self.graph_folder_path, 
            pre_transform=self.pre_transform,
            transform=self.transform,          # composition of transforms argument should go there. (Équivalent to torchvision "transformCompose class")
        )

        # --- Load big Data into the RAM --- # 
        self.load(self.processed_paths[0])
        
        # --- Display info --- #
        print("")
        print(f"Processed path     : {self.processed_paths}")
        print(f"Pre_transform      :  {self.pre_transform}")
        print(f"Len of the dataset : {self.len()}")  


    @property
    def raw_file_names(self):
        # The fact that it points to existing file doesn't matter for torch_geometric
        #[self.root_folder_path + '/' + root_file_name for root_file_name in self.root_file_names]
        return self.root_file_names

    @property
    def processed_file_names(self):
        # if called it returns self.processed_path[0] + what is returned here
        return self.graph_file_names

    def compute_edges(self, k: int, num_workers: int = 1, cosine: bool = False):

        # Set kNN
        pre_transform = KNNGraph(k=k, num_workers=num_workers, cosine=cosine)

        if self.verbose >= 1:
            print()
            print(f"Starting to compute edges..")

        for idx, data in enumerate(self):

            if isinstance(data, dict): # Check in case a transform argument has been passed
                data = data['data']

            new_data = pre_transform(data)
            self._data_list[idx] = new_data

        if self.verbose >= 1:
            print(f"Finished.")
            print(f"Size of data_list (in MB) : {sys.getsizeof(self._data_list)}")

        self._data, self.slices = self.collate(self._data_list)
        self._data_list = None 

    def get(self, idx):
        # Caution : 
        # The pipeline for get is : (starting at the loader)
        # getitem (Dataset) -> get (this class) 
        # If you can super().get() in this class, it's the one from
        # InMemoryDataset, where the big Data is sliced in Data cached in _data_list.
        # then Dataset gets this data, and apply transform.

        # Conclusion : If transform is given in __init__(),
        # this data object will NOT have already be transformed.
        # (See torch_geometric.Data.Dataset.__getitem__() l.292 - 293)

        data = super().get(idx)
        data.idx = idx # for watchmal compatibility

        return data

    def map_labels(in_label, label_set):
        """
        Maps the labels of the dataset into a range of integers from 0 up to N-1, where N is the number of unique labels
        in the provided label set.

        Parameters
        ----------
        label_set: sequence of labels
            Set of all possible labels to map onto the range of integers from 0 to N-1, where N is the number of unique
            labels.
        """
        # This method is for watchmal compatibility
        # This kind of conversion is not currently supported
        # But it will need ot in the future
        # Conversions can be done with one line using label_set.index(PID) i think.
        # Pay attention to the compatibility with the engine
        pass 



# load graphs ===========================================================================================================


print("\nLoading graphs...\n")

config = {
    "graph_folder_path":"/home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/graph_examples",
    "graph_file_names":"data.pt",
    "verbose":1
}

config_pos = {
    "graph_folder_path":"/home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/graph_examples",
    "graph_file_names":"data_pos.pt",
    "verbose":1

}

graph = DatasetFromProcessed(**config)
graph_pos = DatasetFromProcessed(**config_pos)


# process event ========================================================================================================

print("\nProcessing event...\n")

event_index = 0

features = graph[event_index].x.detach().numpy()
pos = graph_pos[event_index].pos.detach().numpy()
edge_indices = graph[event_index].edge_index.detach().numpy()


# display graph ==============================================================================================================

# Some useful detector dimensions (in cm), to be used for adapted node sizes

detector_geom = {
  'SK': {'height': 3620.0, 'cylinder_radius': 3368.15/2, 'PMT_radius': 25.4}, 
  'HK': {'height': 6575.1, 'cylinder_radius': 6480/2, 'PMT_radius': 25.4}, 
  'WCTE': {'height': 271.4235, 'cylinder_radius': 307.5926/2, 'PMT_radius': 4.0}
}

experiment='WCTE'

def rescale_color(x) : # rescale colors with sigmoid to have better color range
  if len(x) > 1 :
    return 1 / (1 + np.exp(-(x-np.median(x))/np.std(x))) # sigmoid
    #return 1 / (1 + np.exp(-x)/np.std(x)) # sigmoid
  return x

plotter = pv.Plotter()

print("\nCreating point cloud...\n")

# Create a point cloud with color mapping
point_cloud = pv.PolyData(pos)
point_cloud["features"] = rescale_color(features[:, 0])  # Use feature values for coloring

# Create spheres at detector positions
sphere = pv.Sphere(radius=detector_geom[experiment]['PMT_radius']-1, theta_resolution=8, phi_resolution=8)  # Adjust radius as needed
spheres = point_cloud.glyph(scale=False, geom=sphere, orient=False)

plotter.add_mesh(spheres, scalars='features', cmap='plasma')  # Light detectors

print("\nCreating edges...\n")

# Create a single line mesh for efficiency
lines = []
for edge_index in edge_indices.T:
    lines.extend([2, edge_index[0], edge_index[1]])  # "2" indicates a line between two points

line_mesh = pv.PolyData()
line_mesh.points = pos
line_mesh.lines = lines

# Add all edges as a single mesh
plotter.add_mesh(line_mesh, color="black", line_width=2, opacity=0.5, style="wireframe")

print("\nDisplaying graph...\n")

# Show the plot
plotter.show()