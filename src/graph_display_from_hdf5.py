#!/usr/bin/env python3

import numpy as np
import h5py
import argparse
from pathlib import Path

try:
    from displays.basic_3D_from_graph import base_display
    from displays.unfold_cylinder_3D_from_graph import unfold_v1_display
except ImportError:
    print("Avertissement: Impossible d'importer les modules d'affichage.")
    print("Assurez-vous que le script est dans le bon répertoire.")
    def base_display(*args, **kwargs):
        print("Fonction 'base_display' non disponible.")
    def unfold_v1_display(*args, **kwargs):
        print("Fonction 'unfold_v1_display' non disponible.")

def main(args):
    """
    Fonction principale pour charger un graphe spécifique depuis un fichier HDF5
    et l'afficher.
    """
    
    # --- 1. Valider le fichier et l'index de l'événement ---
    if not args.input_file.exists():
        raise FileNotFoundError(f"Le fichier d'entrée '{args.input_file}' n'a pas été trouvé.")
    
    # Le nom du groupe est basé sur l'index fourni
    event_group_name = f"event_{args.event_index}"
    
    # --- 2. Charger les données de l'événement spécifique depuis le HDF5 ---
    print(f"Chargement de l'événement '{event_group_name}' depuis '{args.input_file}'...")
    print(f"Chargement des arêtes de l'événement '{event_group_name}' depuis '{args.edge_file}'...")

    with h5py.File(args.input_file, 'r') as input_data_file, h5py.File(args.edge_file, 'r') as input_edge_file:
        # Vérifier si l'événement existe dans le fichier
        if event_group_name not in input_data_file:
            raise KeyError(f"L'événement '{event_group_name}' n'a pas été trouvé dans le fichier HDF5. "
                           f"Nombre d'événements disponibles: {len(input_data_file.keys())}")
        
        if event_group_name not in input_edge_file:
            raise KeyError(f"L'événement '{event_group_name}' n'a pas été trouvé dans le fichier HDF5. "
                           f"Nombre d'événements disponibles: {len(input_edge_file.keys())}")
        
        event_group = input_data_file[event_group_name]
        for feature in ["hitx", "hity", "hitz", "towall", "energy", "dwall", "n_digi_hits"]:
            if feature not in event_group:
                raise KeyError(f"La feature '{feature}' n'a pas été trouvée dans le fichier HDF5. "
                               f"Features disponibles: {event_group.keys()}")
        
        edge_index = input_edge_file[event_group_name][:]
        
        # Check if mask exists (only if selection was applied)
        mask_name = event_group_name + "_mask"
        if mask_name in input_edge_file:
            node_mask = input_edge_file[mask_name][:].astype(bool)  # Convert uint8 back to bool
        else:
            # No mask saved, use all nodes
            n_nodes = len(event_group[args.feature_name][:])
            node_mask = np.ones(n_nodes, dtype=bool)
        
        # Apply mask to features
        node_features = event_group[args.feature_name][:][node_mask]
        
        # Apply mask to spatial coordinates
        pos = np.stack([
            event_group["hitx"][:][node_mask],
            event_group["hity"][:][node_mask],
            event_group["hitz"][:][node_mask]
        ], axis=1)

        towall = event_group['towall'][()]
        energy = event_group['energy'][()]
        dwall = event_group['dwall'][()]
        n_digi_hits = event_group['n_digi_hits'][()]
        
    print(f"Graphe chargé avec succès :")
    print(f"  - Nombre de noeuds (hits) : {pos.shape[0]}")
    print(f"  - Nombre d'arêtes : {edge_index.shape}")
    print(f"  - Dimensions des positions : {pos.shape[1]}D")
    print(f"  - Towall : {towall:.2f}")
    print(f"  - Energy : {energy:.2f}")
    print(f"  - Dwall : {dwall:.2f}")
    print(f"  - N_digi_hits : {n_digi_hits:.2f}")

    if args.display_mode == "base":
        print("Utilisation de l'affichage de base 'base_display'...")
        base_display(args.experiment, node_features, pos, edge_index)

    elif args.display_mode == "unfold":
        print("Utilisation de l'affichage déplié 'unfold_v1_display'...")
        unfold_v1_display(args.experiment, node_features, pos, edge_index)
    else:
        print(f"Mode d'affichage inconnu : {args.display_mode}")
        return 1

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Affiche un graphe spécifique depuis un fichier HDF5."
    )
    
    parser.add_argument("--input-file", type=Path,
                        help="Chemin vers le fichier HDF5 contenant les graphes.")
    
    parser.add_argument("--edge-file", type=Path,
                        help="Chemin vers le fichier HDF5 contenant les arêtes.")
    
    parser.add_argument("--event-index", type=int,
                        help="Index de l'événement à afficher (ex: 0, 1, 99).")
    
    parser.add_argument("--display-mode", type=str, choices=["base", "unfold"],
                        default="base", help="Mode d'affichage: 'base' ou 'unfold'.")

    parser.add_argument("--feature-name", type=str, default="pmt_time", choices=["pmt_time", "pmt_charge"],
                        help="Nom de la feature à utiliser pour la coloration. Default 'pmt_time'.")
    
    parser.add_argument("--experiment", type=str, default="HK_realistic",
                        help="Nom de l'expérience (doit être une clé valide dans vos fichiers de géométrie).")

    args = parser.parse_args()

    main(args)