#!/bin/bash

event_display_folder=/home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay
input_file=/home/mathieu-ferey/Documents/These/Codes/Data/WCTE/WCTE_uni_iso_100_mu-_fid_nohitthres_manda_cuts.root
experiment='WCTE'

python3 $event_display_folder/src/3D_display_from_root.py -f $input_file -e $experiment -i 33 --kind "simple" -v -d