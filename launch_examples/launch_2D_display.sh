#! /bin/bash


#####
# -- Variables configurations
#####

event_display_folder=/path/to/EventDisplay/code

root_file_path=/path/to/root/file
tree_name='pure_root_tree'
experiment='WCTE'


save_path=/path/to/save/images
save_type=jpg
save_file=imagename


#events='all' # to display all events in the root file
#events='10' # to display the 10th event
events='1|100|650' # to display several events


# to add additional info in the title. Has to be the name of available branches in the root tree
extra_data='energy dwall towall'
extra_data_units='MeV cm cm'


#####
# -- Execute code
#####

cd $event_display_folder

# to use tk interactive display
python src/2D_display_from_root.py \
    -e $experiment \
    -f $root_file_path \
    -c 'charge' \
    -t $tree_name \
    -ed $extra_data \
    -eu $extra_data_units \
    -d $events \
    -tk

# to use matplotlib single event display
# python src/2D_display_from_root.py \
#     -e $experiment \
#     -f $root_file_path \
#     -c 'charge' \
#     -t $tree_name \
#     -ed $extra_data \
#     -eu $extra_data_units \
#     -d $events \
#     -sp $save_path \
#     -sf $save_file \
#     -st $save_type \
#     -s