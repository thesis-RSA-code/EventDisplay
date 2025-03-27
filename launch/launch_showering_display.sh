#!/bin/bash

input_file=/home/mathieu-ferey/Documents/These/Codes/Data/SK_all_tracks/WCSim_v1.12.20_SK_default/pi0/500MeV/1/root_output_2events.root

python3 /home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/src/showering_display.py -f $input_file -i 0 -e "SK"
