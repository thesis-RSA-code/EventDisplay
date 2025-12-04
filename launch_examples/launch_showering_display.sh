#!/bin/bash

#####
# -- Variables configurations
#####

event_display_folder=/home/amaterasu/work/EventDisplay

input_file=/home/amaterasu/work/hkfd_analysis/wcsim12.20_corrTrig_study/e-/100-1000MeV/all_tracks/understanding_event356.root
tree_name=pure_root_tree
experiment="HK_realistic"

event_index=9

#####
# -- Execute code
#####

cd $event_display_folder

python3 src/showering_display.py \
    -f $input_file \
    -t $tree_name \
    -i $event_index \
    -e $experiment
