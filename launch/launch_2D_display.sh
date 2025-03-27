#! /bin/bash


#####
# -- Variables configurations
#####

event_display_folder=/home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay

root_file_path=/home/mathieu-ferey/Documents/These/Codes/Data/WCTE/WCTE_uni_iso_100_e-.root


#root_file_path=/home/amaterasu/work/hk_fd_realistic/root_datasets/dr42_trth70_dw2k_mu1k_alltr_folder2.root

save_path=/home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay/plots
save_type=png
save_file=SK_pi0

#events='50|15000|25000|30000'
events='all'
tree_name='pure_root_tree'
detector_type='WCTE'


#####
# -- Executed code No modifications needed below
#####
cd $event_display_folder

python src/2D_display_from_root.py \
    -e $detector_type \
    -f $root_file_path \
    -c 'charge' \
    -t $tree_name \
    -d $events \
    -tk