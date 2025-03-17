#!/bin/bash

input_file=/home/mathieu-ferey/Documents/These/Codes/Data/WCTE_all_tracks/WCSim_v1.12.18_nuPRISMBeamTest_16cShort_mPMT/e-/500MeV/1/root_output_1events.root

python3 /home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/python/showering_display.py -f $input_file -i 0 -e "WCTE" -r