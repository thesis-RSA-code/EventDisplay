#!/bin/bash


file_path=/sps/t2k/eleblevec/WCSimPackage/GraphDatasets/RootExplorer/outputs/test_c_v1.root
events='8637:8640' # Attention à bien faire event + 1
tree_name='filtered_tree'

python event_display.py \
    -e 'HK' \
    -t $tree_name \
    -f $file_path \
    -d $events