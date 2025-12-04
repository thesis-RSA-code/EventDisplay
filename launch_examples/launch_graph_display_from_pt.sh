#!/bin/bash

experiment="WCTE"
graph_folder_path="/home/mathieu-ferey/Documents/These/Codes/Data/Graphs/WCTE_model_testing_WCSim_v1.12.18_nuPRISMBeamTest_16cShort_mPMT_200-1000MeV/f_logcharge_time_l_eventType_e_hit_k_5"
display_mode="base"
event_index=9000
verbose=1

python src/graph_display_from_pt.py \
    --experiment "$experiment" \
    --graph_folder_path "$graph_folder_path" \
    --display_mode "$display_mode" \
    --event_index "$event_index" \
    --verbose "$verbose"
