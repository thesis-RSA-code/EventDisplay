#!/usr/bin/env python3
"""
Visualize event augmentation side-by-side.

Shows original, rotated, and flipped versions of an event for comparison.
"""

import numpy as np
import h5py
import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

from event_augmentation import rotate_z_axis, flip_vertical


def load_event_from_hdf5(hdf5_path: Path, event_index: int) -> dict:
    """
    Load a single event from HDF5 file.
    
    Parameters
    ----------
    hdf5_path : Path
        Path to HDF5 file
    event_index : int
        Index of event to load
        
    Returns
    -------
    event_data : dict
        Dictionary containing event data
    """
    event_group_name = f"event_{event_index}"
    
    with h5py.File(hdf5_path, 'r') as f:
        if event_group_name not in f:
            available_events = len([k for k in f.keys() if k.startswith('event_')])
            raise KeyError(f"Event '{event_group_name}' not found in file. "
                          f"Available events: 0 to {available_events-1}")
        
        event_group = f[event_group_name]
        
        # Load all available data
        event_data = {}
        
        # Required fields
        for key in ['hitx', 'hity', 'hitz']:
            if key in event_group:
                event_data[key] = event_group[key][:]
        
        # Optional scalar fields
        for key in ['towall', 'energy', 'dwall', 'n_digi_hits', 'event_type', 'trigger_time']:
            if key in event_group:
                event_data[key] = event_group[key][()]
        
        # Optional feature fields
        for key in ['pmt_time', 'pmt_charge']:
            if key in event_group:
                event_data[key] = event_group[key][:]
        
        # Load vertex (handle both old and new formats)
        if 'vertex' in event_group:
            # Old format: single array
            event_data['vertex'] = event_group['vertex'][:]
        elif all(f'vertex_{coord}' in event_group for coord in ['x', 'y', 'z']):
            # New format: separate x, y, z
            event_data['vertex'] = np.array([
                event_group['vertex_x'][()],
                event_group['vertex_y'][()],
                event_group['vertex_z'][()]
            ])
        
        # Load particle start (vertex alias in new format)
        if all(f'particle_start_{coord}' in event_group for coord in ['x', 'y', 'z']):
            event_data['vertex'] = np.array([
                event_group['particle_start_x'][()],
                event_group['particle_start_y'][()],
                event_group['particle_start_z'][()]
            ])
        
        # Load particle stop (handle both old and new formats)
        if 'particleStop' in event_group:
            # Old format: single array
            event_data['particleStop'] = event_group['particleStop'][:]
        elif all(f'particle_stop_{coord}' in event_group for coord in ['x', 'y', 'z']):
            # New format: separate x, y, z
            event_data['particleStop'] = np.array([
                event_group['particle_stop_x'][()],
                event_group['particle_stop_y'][()],
                event_group['particle_stop_z'][()]
            ])
        
        # Load particle direction (handle both old and new formats)
        if 'particleDir' in event_group:
            # Old format: single array
            event_data['particleDir'] = event_group['particleDir'][:]
        elif all(f'particle_dir_{coord}' in event_group for coord in ['x', 'y', 'z']):
            # New format: separate x, y, z
            event_data['particleDir'] = np.array([
                event_group['particle_dir_x'][()],
                event_group['particle_dir_y'][()],
                event_group['particle_dir_z'][()]
            ])
    
    return event_data


def plot_event_comparison(original_data, rotated_data, flipped_data, 
                         rotation_angle, save_path=None):
    """
    Plot three versions of the event side-by-side.
    
    Parameters
    ----------
    original_data : dict
        Original event data
    rotated_data : dict
        Rotated event data
    flipped_data : dict
        Flipped event data
    rotation_angle : float
        Rotation angle applied (for title)
    save_path : str, optional
        Path to save the figure
    """
    fig = plt.figure(figsize=(18, 6))
    
    # Determine color scheme
    if 'pmt_charge' in original_data:
        color_data = original_data['pmt_charge']
        color_label = 'PMT Charge'
        cmap = 'plasma'
    elif 'pmt_time' in original_data:
        color_data = original_data['pmt_time']
        color_label = 'PMT Time'
        cmap = 'viridis'
    else:
        color_data = None
        color_label = None
        cmap = 'blue'
    
    # Calculate common axis limits for all three plots
    all_x = np.concatenate([original_data['hitx'], rotated_data['hitx'], flipped_data['hitx']])
    all_y = np.concatenate([original_data['hity'], rotated_data['hity'], flipped_data['hity']])
    all_z = np.concatenate([original_data['hitz'], rotated_data['hitz'], flipped_data['hitz']])
    
    max_range = np.array([all_x.max()-all_x.min(), 
                          all_y.max()-all_y.min(), 
                          all_z.max()-all_z.min()]).max() / 2.0
    
    mid_x = (all_x.max() + all_x.min()) * 0.5
    mid_y = (all_y.max() + all_y.min()) * 0.5
    mid_z = (all_z.max() + all_z.min()) * 0.5
    
    # Plot 1: Original
    ax1 = fig.add_subplot(1, 3, 1, projection='3d')
    plot_single_event(ax1, original_data, "Original Event", color_data, cmap,
                     mid_x, mid_y, mid_z, max_range)
    
    # Plot 2: Rotated
    ax2 = fig.add_subplot(1, 3, 2, projection='3d')
    plot_single_event(ax2, rotated_data, f"Rotated {rotation_angle}°", color_data, cmap,
                     mid_x, mid_y, mid_z, max_range)
    
    # Plot 3: Flipped
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    plot_single_event(ax3, flipped_data, "Vertically Flipped", color_data, cmap,
                     mid_x, mid_y, mid_z, max_range)
    
    # Add overall title with event info
    title_parts = []
    if 'energy' in original_data:
        title_parts.append(f"Energy: {original_data['energy']:.2f} MeV")
    if 'towall' in original_data:
        title_parts.append(f"Towall: {original_data['towall']:.2f} cm")
    if 'n_digi_hits' in original_data:
        title_parts.append(f"Hits: {int(original_data['n_digi_hits'])}")
    
    if title_parts:
        fig.suptitle(" | ".join(title_parts), fontsize=14, y=0.98)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved visualization to '{save_path}'")
    
    plt.show()


def plot_single_event(ax, data, title, color_data, cmap, mid_x, mid_y, mid_z, max_range):
    """
    Plot a single event on given axis.
    
    Parameters
    ----------
    ax : matplotlib 3D axis
        Axis to plot on
    data : dict
        Event data
    title : str
        Title for the subplot
    color_data : array or None
        Data to use for coloring
    cmap : str
        Colormap name
    mid_x, mid_y, mid_z : float
        Center coordinates for axis limits
    max_range : float
        Range for axis limits
    """
    hitx = data['hitx']
    hity = data['hity']
    hitz = data['hitz']
    
    # Plot hits
    if color_data is not None:
        scatter = ax.scatter(hitx, hity, hitz, s=5, c=color_data, cmap=cmap, alpha=0.6)
    else:
        scatter = ax.scatter(hitx, hity, hitz, s=5, c='blue', alpha=0.6)
    
    # Plot vertex if available (black cross)
    if 'vertex' in data:
        vertex = np.array(data['vertex'])
        if vertex.ndim == 1 and len(vertex) >= 3:
            ax.scatter(vertex[0], vertex[1], vertex[2], 
                      c='black', marker='x', s=200, 
                      linewidths=3, label='Vertex')
    
    # Plot stop if available
    if 'particleStop' in data:
        stop = np.array(data['particleStop'])
        if stop.ndim == 1 and len(stop) >= 3:
            ax.scatter(stop[0], stop[1], stop[2], 
                      c='green', marker='x', s=150, 
                      linewidths=3, label='Stop')
    
    # Plot direction if available (red arrow)
    if 'particleDir' in data and 'vertex' in data:
        direction = np.array(data['particleDir'])
        vertex = np.array(data['vertex'])
        if direction.ndim == 1 and vertex.ndim == 1 and len(direction) >= 3 and len(vertex) >= 3:
            # Scale direction for visibility
            scale = max_range * 0.3
            ax.quiver(vertex[0], vertex[1], vertex[2],
                     direction[0], direction[1], direction[2],
                     length=scale, normalize=True, 
                     color='red', linewidth=2, alpha=0.8, 
                     arrow_length_ratio=0.3, label='Direction')
    
    # Set labels and limits
    ax.set_xlabel('X (cm)', fontsize=10)
    ax.set_ylabel('Y (cm)', fontsize=10)
    ax.set_zlabel('Z (cm)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    
    # Set equal aspect ratio
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Add legend if there are special markers
    if 'vertex' in data or 'particleStop' in data:
        ax.legend(loc='upper left', fontsize=8)
    
    # Set viewing angle for better perspective
    ax.view_init(elev=20, azim=45)


def main():
    parser = argparse.ArgumentParser(
        description="Visualize original, rotated, and flipped event side-by-side"
    )
    
    parser.add_argument("--input-file", type=Path, required=True,
                        help="Path to HDF5 file")
    
    parser.add_argument("--event-index", type=int, default=0,
                        help="Index of event to load (default: 0)")
    
    parser.add_argument("--rotation-angle", type=float, default=90,
                        help="Rotation angle in degrees (default: 90)")
    
    parser.add_argument("--output", type=str, default=None,
                        help="Output file path for saving figure (default: display only)")
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.exists():
        print(f"Error: File not found: {args.input_file}")
        return 1
    
    # Load event
    print("="*70)
    print(f"Loading event {args.event_index} from {args.input_file.name}...")
    print("="*70)
    
    try:
        original_data = load_event_from_hdf5(args.input_file, args.event_index)
    except KeyError as e:
        print(f"Error: {e}")
        return 1
    
    print(f"✓ Event loaded successfully!")
    print(f"  - Number of hits: {len(original_data['hitx'])}")
    
    if 'energy' in original_data:
        print(f"  - Energy: {original_data['energy']:.2f} MeV")
    if 'towall' in original_data:
        print(f"  - Towall: {original_data['towall']:.2f} cm")
    if 'dwall' in original_data:
        print(f"  - Dwall: {original_data['dwall']:.2f} cm")
    
    # Apply augmentations
    print(f"\nApplying augmentations...")
    print(f"  - Rotation: {args.rotation_angle}°")
    print(f"  - Vertical flip")
    
    rotated_data = rotate_z_axis(original_data, args.rotation_angle, degrees=True)
    flipped_data = flip_vertical(original_data)
    
    print(f"✓ Augmentations applied!")
    
    # Determine output path
    if args.output is None:
        output_path = f"event_{args.event_index}_augmentation_comparison.png"
    else:
        output_path = args.output
    
    # Plot comparison
    print(f"\nGenerating visualization...")
    plot_event_comparison(original_data, rotated_data, flipped_data, 
                         args.rotation_angle, save_path=output_path)
    
    print("="*70)
    print("✓ Visualization complete!")
    print("="*70)


if __name__ == "__main__":
    main()

