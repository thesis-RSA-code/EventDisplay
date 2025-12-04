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

def load_event_from_flat_hdf5(data_file, edge_file, event_index, feature_name):
    """
    Load a specific event from flat HDF5 format.
    
    Args:
        data_file: h5py.File object for node features and scalars
        edge_file: h5py.File object for edges and masks
        event_index: int, index of the event to load
        feature_name: str, name of the feature to use for coloring
        
    Returns:
        node_features: array of shape (n_nodes,)
        pos: array of shape (n_nodes, 3)
        edge_index: array of shape (2, n_edges)
        metadata: dict with scalar values
    """
    # Get the total number of events
    n_events = len(data_file['index_pointer']) - 1
    
    if event_index < 0 or event_index >= n_events:
        raise ValueError(f"Event index {event_index} out of range [0, {n_events-1}]")
    
    # --- Load Node Features and Scalars ---
    # Get the slice indices for this event
    node_start = data_file['index_pointer'][event_index]
    node_end = data_file['index_pointer'][event_index + 1]
    n_nodes_total = node_end - node_start
    
    # Load spatial coordinates (before masking)
    hitx = data_file['features/hitx'][node_start:node_end]
    hity = data_file['features/hity'][node_start:node_end]
    hitz = data_file['features/hitz'][node_start:node_end]
    
    # Load the requested feature (before masking)
    if feature_name not in data_file['features']:
        raise KeyError(f"Feature '{feature_name}' not found in features group. "
                      f"Available: {list(data_file['features'].keys())}")
    
    node_features_full = data_file['features'][feature_name][node_start:node_end]
    
    # --- Load Mask ---
    # Get the mask slice for this event
    mask_start = edge_file['mask_pointer'][event_index]
    mask_end = edge_file['mask_pointer'][event_index + 1]
    node_mask = edge_file['masks'][mask_start:mask_end].astype(bool)
    
    # Verify mask size matches node count
    if len(node_mask) != n_nodes_total:
        raise ValueError(f"Mask size {len(node_mask)} doesn't match node count {n_nodes_total}")
    
    # Apply mask to features and positions
    node_features = node_features_full[node_mask]
    pos = np.stack([
        hitx[node_mask],
        hity[node_mask],
        hitz[node_mask]
    ], axis=1)
    
    # --- Load Edges ---
    edge_start = edge_file['edge_pointer'][event_index]
    edge_end = edge_file['edge_pointer'][event_index + 1]
    edge_index = edge_file['edges'][:, edge_start:edge_end]
    
    # --- Load Scalar Metadata ---
    metadata = {}
    for key in data_file['scalars'].keys():
        metadata[key] = data_file['scalars'][key][event_index]
    
    return node_features, pos, edge_index, metadata

def main(args):
    """
    Fonction principale pour charger un graphe spécifique depuis des fichiers HDF5 plats
    et l'afficher.
    """
    
    # --- 1. Valider les fichiers ---
    if not args.input_file.exists():
        raise FileNotFoundError(f"Le fichier d'entrée '{args.input_file}' n'a pas été trouvé.")
    
    if not args.edge_file.exists():
        raise FileNotFoundError(f"Le fichier d'arêtes '{args.edge_file}' n'a pas été trouvé.")
    
    # --- 2. Charger les données de l'événement spécifique depuis les HDF5 plats ---
    print(f"Chargement de l'événement {args.event_index} depuis les fichiers plats...")
    print(f"  - Fichier de données: '{args.input_file}'")
    print(f"  - Fichier d'arêtes: '{args.edge_file}'")

    with h5py.File(args.input_file, 'r') as data_file, h5py.File(args.edge_file, 'r') as edge_file:
        
        # Check number of events available
        n_events = len(data_file['index_pointer']) - 1
        print(f"  - Nombre d'événements disponibles: {n_events}")
        
        if args.event_index < 0 or args.event_index >= n_events:
            raise ValueError(f"L'index d'événement {args.event_index} est hors limites [0, {n_events-1}]")
        
        # Load the event
        node_features, pos, edge_index, metadata = load_event_from_flat_hdf5(
            data_file, edge_file, args.event_index, args.feature_name
        )
        
    print(f"\nGraphe chargé avec succès :")
    print(f"  - Nombre de noeuds (hits) : {pos.shape[0]}")
    print(f"  - Nombre d'arêtes : {edge_index.shape[1]}")
    print(f"  - Dimensions des positions : {pos.shape[1]}D")
    print(f"  - Feature utilisée : {args.feature_name}")
    print(f"\nMétadonnées de l'événement :")
    for key, value in metadata.items():
        if isinstance(value, (int, np.integer)):
            print(f"  - {key}: {value}")
        else:
            print(f"  - {key}: {value:.4f}")

    # --- 3. Afficher le graphe ---
    if args.display_mode == "base":
        print("\nUtilisation de l'affichage de base 'base_display'...")
        base_display(args.experiment, node_features, pos, edge_index)

    elif args.display_mode == "unfold":
        print("\nUtilisation de l'affichage déplié 'unfold_v1_display'...")
        unfold_v1_display(args.experiment, node_features, pos, edge_index)
    else:
        print(f"Mode d'affichage inconnu : {args.display_mode}")
        return 1

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Affiche un graphe spécifique depuis des fichiers HDF5 au format plat/colonnaire."
    )
    
    parser.add_argument("--input-file", type=Path, required=True,
                        help="Chemin vers le fichier HDF5 plat contenant les features et scalaires.")
    
    parser.add_argument("--edge-file", type=Path, required=True,
                        help="Chemin vers le fichier HDF5 plat contenant les arêtes et masques.")
    
    parser.add_argument("--event-index", type=int, required=True,
                        help="Index de l'événement à afficher (ex: 0, 1, 99).")
    
    parser.add_argument("--display-mode", type=str, choices=["base", "unfold"],
                        default="base", help="Mode d'affichage: 'base' ou 'unfold'.")

    parser.add_argument("--feature-name", type=str, default="pmt_time", 
                        choices=["pmt_time", "pmt_charge"],
                        help="Nom de la feature à utiliser pour la coloration. Default 'pmt_time'.")
    
    parser.add_argument("--experiment", type=str, default="HK_realistic",
                        help="Nom de l'expérience (doit être une clé valide dans vos fichiers de géométrie).")

    args = parser.parse_args()

    main(args)

