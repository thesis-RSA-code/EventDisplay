#!/usr/bin/env python3
import os.path as osp
import argparse

from displays.basic_3D_from_graph import base_display
from displays.unfold_cylinder_3D_from_graph import unfold_v1_display

from utils.detector_geometries import NORMALIZED_VALUES
from utils.graphs.dataset_from_processed import DatasetFromProcessed

import numpy as np


def main(config, config_pos, experiment, event_index, display_mode):

    # --- Load the graph dataset ---
    print(f"Loading graphs from {config['graph_folder_path']}...\n")
    print("Loading the dataset (graph/data.pt)...\n")
    graph = DatasetFromProcessed(**config)

    print(f"First graph of data.pt {graph[0]}")

    print("Loading the dataset (graph/data_pos.pt)...\n")
    graph_pos = DatasetFromProcessed(**config_pos)
    print(f"First graph of data_pos.pot : {graph_pos[0]}")

    # --- Fetch the selected graph ---
    features = graph[event_index].x.numpy()
    edge_index = graph[event_index].edge_index.numpy()

    if hasattr(graph_pos[event_index], "hitx"):
        hitx = graph_pos[event_index].hitx.numpy()
        hity = graph_pos[event_index].hity.numpy()
        hitz = graph_pos[event_index].hitz.numpy()
    
    elif hasattr(graph_pos[event_index], "pos"):
        # hitx = graph_pos[event_index].pos[:, 1].numpy()
        # hity = graph_pos[event_index].pos[:, 2].numpy()
        # hitz = graph_pos[event_index].pos[:, 3].numpy()
        hitx = graph_pos[event_index].pos[:, 0].numpy()
        hity = graph_pos[event_index].pos[:, 1].numpy()
        hitz = graph_pos[event_index].pos[:, 2].numpy()
    else:
        raise ValueError("No hitx, hity, hitz or pos attribut found in the graph_pos dataset.")
    
    hitx = hitx * ( NORMALIZED_VALUES['hitx'][1] - NORMALIZED_VALUES['hitx'][0] ) + NORMALIZED_VALUES['hitx'][0]
    hity = hity * ( NORMALIZED_VALUES['hity'][1] - NORMALIZED_VALUES['hity'][0] ) + NORMALIZED_VALUES['hity'][0]
    hitz = hitz * ( NORMALIZED_VALUES['hitz'][1] - NORMALIZED_VALUES['hitz'][0] ) + NORMALIZED_VALUES['hitz'][0]
    
    pos = np.stack([hitx, hity, hitz], axis=0).T
    print(pos.shape)
    print(f"Min : {np.min(pos)}, max: {np.max(pos)}")

    
    # Select the display mode
    if display_mode == "base":
        print("Using base display...")
        base_display(experiment, features, pos, edge_index)

    elif display_mode == "unfold":
        print("Using unfolded display...")
        unfold_v1_display(experiment, features, pos, edge_index)
    else:
        print(f"Unknown display mode: {display_mode}")
        return 1
    
    # For future (Erwan - 07/03/2025)
    # elif display_mode == "scale":
    #     print("Using interactive scale factor display...")
    #     scale_factor_bar_display(experiment, features, pos, edge_index)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Display graph with different methods using preprocessed .pt graph files."
    )
    parser.add_argument("--experiment", type=str, default="Demo",
                        help="Experiment name. Default: 'Demo'")
    parser.add_argument("--graph_folder_path", type=str,
                        default="/home/amaterasu/work/cm_meeting_hk/datasets/graph_datasets/demo_v1",
                        help="Path to the graph dataset folder.")
    parser.add_argument("--display_mode", type=str, choices=["base", "unfold", "scale"],
                        default="base", help="Display mode: 'base', 'unfold', or 'scale'. Default: 'base'")
    parser.add_argument("--event_index", type=int, default=1,
                        help="Index of the event to display. Default: 1")
    parser.add_argument("--verbose", type=int, default=1,
                        help="Verbosity level. Default: 1")

    args = parser.parse_args()

    config = {
        "graph_folder_path": args.graph_folder_path,
        "graph_file_names": "data.pt",
        "verbose": args.verbose,
    }
    config_pos = {
        "graph_folder_path": args.graph_folder_path,
        "graph_file_names": "data_pos.pt",
        "verbose": args.verbose,
    }

    main(config, config_pos, args.experiment, args.event_index, args.display_mode)
