#!/bin/bash

input_file=/home/mathieu-ferey/Documents/These/Codes/Data/SK/SK_e-_200-1000MeV_1000_1.root
experiment='SK'

python3 /home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/python/3D_display.py -f $input_file -e $experiment -i 678