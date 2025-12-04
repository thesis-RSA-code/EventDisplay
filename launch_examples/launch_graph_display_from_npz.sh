#!/bin/bash

# Note :
# Pour les graphes avec --node-features charge time. Alors time est à l'index 1.

file_path="/home/amaterasu/work/RootToGraph/playground/newg_graph_builders/11/event_99_graph.npz"
display_mode="base"
feature_index=1

python src/graph_display_from_npz.py \
    $file_path \
    --display_mode $display_mode \
    --feature_index $feature_index