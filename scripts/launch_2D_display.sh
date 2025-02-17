#! /bin/bash


base_folder=/home/amaterasu/work/cm_meeting_hk/EventDisplay
file_path=/home/amaterasu/work/cm_meeting_hk/datasets/processed_root_datasets/e_mu_20k_v1_processed.root

save_event_display=/home/amaterasu/work/cm_meeting_hk/viz/

#events='50|15000|25000|30000'
events=5
tree_name='tree_with_cuts'
detector_type='DEMO'



#####
# -- Executed code No modifications needed below
#####
cd $base_folder

python python/event_display.py \
    -e $detector_type \
    -f $file_path \
    -c 'charge' \
    -t $tree_name \
    -d $events \
    -s \
    -sp $save_event_display \