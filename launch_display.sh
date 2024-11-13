#!/bin/bash

file_path=/sps/t2k/eleblevec/WCSimPackage/GraphDatasets/RootExplorer/outputs/test_c_v1.root
events='0:1900'
tree_name=filtered_tree

sp=/sps/t2k/eleblevec/BigBrother/EventDisplay/outputs/
sf=one_display_test.png

python event_display.py \
    -e 'HK' \
    -t $tree_name \
    -f $file_path \
    -d $events \
    -sp $sp \