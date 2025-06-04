#!/bin/bash

#####
# -- Variables configurations
#####

event_display_folder=/path/to/EventDisplay/code
input_file=$event_display_folder/showering_examples/1electron_SK.root
tree_name=pure_root_tree
experiment="SK"

event_index=0



#####
# -- Execute code
#####

cd $event_display_folder

python3 /home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/src/showering_display.py \
    -f $input_file \
    -t $tree_name \
    -i $event_index \
    -e $experiment
