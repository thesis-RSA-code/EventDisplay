#!/bin/bash

file_path=/home/mathieu-ferey/Documents/These/Codes/Data/WCTE_e-_200-1000MeV_20000_extra/WCTE_e-_200-1000MeV_20000_extra.root
events='1404'

sp='/home/mathieu-ferey/Documents/These/Group_Meeting/Plots/'
sf='WCTE_group_meeting.pdf'

python event_display.py \
    -e 'WCTE' \
    -f $file_path \
    -d $events \
    -s \
    -t 'pure_root_tree' \
    -sp $sp \
    -sf $sf