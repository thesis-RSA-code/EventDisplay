#!/bin/bash

#####
# -- Variables configurations
#####

event_display_folder=/path/to/EventDisplay/code
input_file=/path/to/root/file
experiment='WCTE'

event_index=1

#####
# -- Execute code
#####

cd $event_display_folder

python3 $event_display_folder/src/3D_display_from_root.py \
    -f $input_file \
    -e $experiment -i $event_index \
    --kind "immersive" \
    -v \
    --stop \
    -d \