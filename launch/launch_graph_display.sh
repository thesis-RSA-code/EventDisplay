#!/bin/bash

experiment="DEMO"
graph_folder_path="/home/amaterasu/work/cm_meeting_hk/datasets/graph_datasets/demo_v1"
display_mode="base"
event_index=15
verbose=1

python src/display_from_graph.py \
    --experiment "$experiment" \
    --graph_folder_path "$graph_folder_path" \
    --display_mode "$display_mode" \
    --event_index "$event_index" \
    --verbose "$verbose"
