#! /bin/bash


#####
# -- Variables configurations
#####

event_display_folder=/home/amaterasu/work/EventDisplay

root_file_path=/home/amaterasu/work/hk_fd_realistic/root_datasets/dr42_trth70_dw2k_mu1k_alltr_folder2_mandac_extrad.root

#root_file_path=/home/amaterasu/work/hk_fd_realistic/root_datasets/dr42_trth70_dw2k_mu1k_alltr_folder2.root

save_path=/home/amaterasu/work/EventDisplay/playground/
save_type=pdf

#events='50|15000|25000|30000'
events='5|10|498'
tree_name='pure_root_tree'
detector_type='HK'


#####
# -- Executed code No modifications needed below
#####
cd $event_display_folder

python src/2D_display_from_root.py \
    -e $detector_type \
    -f $root_file_path \
    -c 'time' \
    -t $tree_name \
    -d $events \