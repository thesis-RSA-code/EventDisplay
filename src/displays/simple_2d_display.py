"""
Simple 2D event display for cylindrical detectors.
Minimal options, just the essentials.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from utils.detector_geometries import DETECTOR_GEOM


def simple_2d_display(
    hitx, hity, hitz,
    color_data,
    color_name,
    experiment,
    event_info=None,
    show=True,
    save_path=None
):
    """
    Simple 2D unfolded cylinder display.
    
    Args:
        hitx, hity, hitz: 3D hit positions
        color_data: Values for coloring (charge or time)
        color_name: Name of the color variable (for label)
        experiment: Detector name (e.g., 'HK_realistic')
        event_info: Dict with event-level info to display (e.g., {'energy': 500, 'dwall': 300})
        show: Whether to show the plot
        save_path: Path to save figure (if None, don't save)
    """
    
    # Get detector geometry
    geom = DETECTOR_GEOM[experiment]
    pmt_radius = geom['PMT_radius']
    cylinder_radius = geom['cylinder_radius']
    height = geom['height']
    z_max = height / 2
    z_min = -height / 2
    
    # Project onto 2D (unfold cylinder)
    theta = np.arctan2(hity, hitx)
    x_proj = theta * cylinder_radius  # Unfolded x
    y_proj = hitz  # Keep z as y
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Title with event info
    title = f"{experiment} Event Display"
    if event_info:
        info_str = ', '.join([f"{k}={v}" for k, v in event_info.items()])
        title += f"\n{info_str}"
    fig.suptitle(title, fontsize=14)
    
    # Draw detector background
    ax.add_patch(plt.Rectangle(
        (-np.pi * cylinder_radius, z_min),
        2 * np.pi * cylinder_radius,
        height,
        fill=True, color='black', alpha=0.8
    ))
    
    # Draw top/bottom caps
    ax.add_patch(plt.Circle((0, z_max + cylinder_radius), cylinder_radius, 
                            fill=True, color='black', alpha=0.8))
    ax.add_patch(plt.Circle((0, z_min - cylinder_radius), cylinder_radius, 
                            fill=True, color='black', alpha=0.8))
    
    # Plot hits
    scatter = ax.scatter(
        x_proj, y_proj,
        c=color_data,
        s=pmt_radius * 2,
        cmap='plasma',
        alpha=0.8,
        edgecolors='white',
        linewidths=0.3
    )
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, label=color_name)
    
    # Set limits and labels
    pad = 30
    ax.set_xlim(-np.pi * cylinder_radius - pad, np.pi * cylinder_radius + pad)
    ax.set_ylim(z_min - 2 * cylinder_radius - pad, z_max + 2 * cylinder_radius + pad)
    ax.set_aspect('equal')
    ax.set_xlabel('Unfolded φ (cm)', fontsize=12)
    ax.set_ylabel('z (cm)', fontsize=12)
    ax.grid(alpha=0.2)
    
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        print(f"Figure saved to: {save_path}")
    
    # Show if requested
    if show:
        plt.show()

