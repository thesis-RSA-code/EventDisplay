#! /bin/bash


#####
# -- Variables configurations
#####

event_display_folder=/home/mathieu-ferey/Documents/These/Codes/CAVERNS/EventDisplay

root_file_path=/home/mathieu-ferey/Documents/These/Codes/Data/Graphs/WCTE_model_testing_WCSim_v1.12.18_nuPRISMBeamTest_16cShort_mPMT_200-1000MeV/muons.root

#root_file_path=/home/amaterasu/work/hk_fd_realistic/root_datasets/dr42_trth70_dw2k_mu1k_alltr_folder2.root

save_path=/home/amaterasu/work/EventDisplay/playground/
save_type=pdf

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
