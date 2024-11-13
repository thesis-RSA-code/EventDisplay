#!/bin/bash

file_path='/sps/t2k/mferey/WCSim2ML/Data/SK/30_mu-_1000MeV_GPS.root'
events='15'

sp='plots/SK/'

python event_display.py \
    -e 'SK' \
    -f $file_path \
    -d $events \
    -sp $sp\
    -c 'time'