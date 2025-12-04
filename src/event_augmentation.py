#!/usr/bin/env python3
"""
Event Augmentation Module for Cylindrical Detector Data

This module provides geometric transformations for augmenting detector events
in cylindrical geometry. Supports rotation around z-axis and vertical flipping.

Author: Event Display Project
"""

import numpy as np
import h5py
from typing import Dict, Tuple, Optional, Union


def rotate_point_z(x: np.ndarray, y: np.ndarray, angle: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Rotate points around the z-axis by a given angle.
    
    Parameters
    ----------
    x : np.ndarray
        X coordinates
    y : np.ndarray
        Y coordinates
    angle : float
        Rotation angle in radians
        
    Returns
    -------
    x_rot, y_rot : tuple of np.ndarray
        Rotated x and y coordinates
    """
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)
    
    x_rot = x * cos_angle - y * sin_angle
    y_rot = x * sin_angle + y * cos_angle
    
    return x_rot, y_rot


def rotate_z_axis(data: Dict[str, np.ndarray], angle: float, degrees: bool = True) -> Dict[str, np.ndarray]:
    """
    Rotate event around the z-axis.
    
    This transformation rotates all spatial coordinates (x, y) around the z-axis
    while preserving the z coordinate. Applies to hit positions, vertex, particle
    stop position, and particle direction.
    
    Parameters
    ----------
    data : dict
        Dictionary containing event data with keys like 'hitx', 'hity', 'hitz',
        'vertex', 'particleStop', 'particleDir', etc.
    angle : float
        Rotation angle (default: degrees)
    degrees : bool, optional
        If True, angle is in degrees. If False, angle is in radians (default: True)
        
    Returns
    -------
    rotated_data : dict
        New dictionary with rotated coordinates
    """
    # Convert to radians if necessary
    angle_rad = np.radians(angle) if degrees else angle
    
    # Create a copy of the data
    rotated_data = data.copy()
    
    # Rotate hit positions if they exist
    if 'hitx' in data and 'hity' in data:
        hitx_rot, hity_rot = rotate_point_z(data['hitx'], data['hity'], angle_rad)
        rotated_data['hitx'] = hitx_rot
        rotated_data['hity'] = hity_rot
    
    # Rotate vertex if it exists
    if 'vertex' in data:
        vertex = np.array(data['vertex'])
        if vertex.ndim == 1 and len(vertex) >= 2:
            # Single vertex (x, y, z)
            vx_rot, vy_rot = rotate_point_z(vertex[0], vertex[1], angle_rad)
            rotated_data['vertex'] = np.array([vx_rot, vy_rot, vertex[2]])
        elif vertex.ndim == 2 and vertex.shape[1] >= 2:
            # Multiple vertices
            vx_rot, vy_rot = rotate_point_z(vertex[:, 0], vertex[:, 1], angle_rad)
            rotated_data['vertex'] = np.column_stack([vx_rot, vy_rot, vertex[:, 2]])
    
    # Rotate particle stop position if it exists
    if 'particleStop' in data:
        stop = np.array(data['particleStop'])
        if stop.ndim == 1 and len(stop) >= 2:
            sx_rot, sy_rot = rotate_point_z(stop[0], stop[1], angle_rad)
            rotated_data['particleStop'] = np.array([sx_rot, sy_rot, stop[2]])
        elif stop.ndim == 2 and stop.shape[1] >= 2:
            sx_rot, sy_rot = rotate_point_z(stop[:, 0], stop[:, 1], angle_rad)
            rotated_data['particleStop'] = np.column_stack([sx_rot, sy_rot, stop[:, 2]])
    
    # Rotate particle direction if it exists (direction is a vector, so it rotates the same way)
    if 'particleDir' in data:
        direction = np.array(data['particleDir'])
        if direction.ndim == 1 and len(direction) >= 2:
            dx_rot, dy_rot = rotate_point_z(direction[0], direction[1], angle_rad)
            rotated_data['particleDir'] = np.array([dx_rot, dy_rot, direction[2]])
        elif direction.ndim == 2 and direction.shape[1] >= 2:
            dx_rot, dy_rot = rotate_point_z(direction[:, 0], direction[:, 1], angle_rad)
            rotated_data['particleDir'] = np.column_stack([dx_rot, dy_rot, direction[:, 2]])
    
    return rotated_data


def flip_vertical(data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
    """
    Flip event vertically (invert top and bottom).
    
    This transformation inverts the z-axis (z → -z), effectively flipping
    the detector upside down. Applies to hit positions, vertex, particle
    stop position, and particle direction.
    
    Parameters
    ----------
    data : dict
        Dictionary containing event data
        
    Returns
    -------
    flipped_data : dict
        New dictionary with flipped z-coordinates
    """
    # Create a copy of the data
    flipped_data = data.copy()
    
    # Flip hit z positions
    if 'hitz' in data:
        flipped_data['hitz'] = -data['hitz']
    
    # Flip vertex z coordinate
    if 'vertex' in data:
        vertex = np.array(data['vertex'])
        if vertex.ndim == 1 and len(vertex) >= 3:
            flipped_data['vertex'] = np.array([vertex[0], vertex[1], -vertex[2]])
        elif vertex.ndim == 2 and vertex.shape[1] >= 3:
            flipped_data['vertex'] = np.column_stack([vertex[:, 0], vertex[:, 1], -vertex[:, 2]])
    
    # Flip particle stop z coordinate
    if 'particleStop' in data:
        stop = np.array(data['particleStop'])
        if stop.ndim == 1 and len(stop) >= 3:
            flipped_data['particleStop'] = np.array([stop[0], stop[1], -stop[2]])
        elif stop.ndim == 2 and stop.shape[1] >= 3:
            flipped_data['particleStop'] = np.column_stack([stop[:, 0], stop[:, 1], -stop[:, 2]])
    
    # Flip particle direction z component
    if 'particleDir' in data:
        direction = np.array(data['particleDir'])
        if direction.ndim == 1 and len(direction) >= 3:
            flipped_data['particleDir'] = np.array([direction[0], direction[1], -direction[2]])
        elif direction.ndim == 2 and direction.shape[1] >= 3:
            flipped_data['particleDir'] = np.column_stack([direction[:, 0], direction[:, 1], -direction[:, 2]])
    
    return flipped_data


def random_rotation_z(data: Dict[str, np.ndarray], 
                      min_angle: float = 0.0, 
                      max_angle: float = 360.0,
                      degrees: bool = True,
                      seed: Optional[int] = None) -> Dict[str, np.ndarray]:
    """
    Apply random rotation around z-axis with optional angle constraints.
    
    Parameters
    ----------
    data : dict
        Dictionary containing event data
    min_angle : float, optional
        Minimum rotation angle (default: 0.0)
    max_angle : float, optional
        Maximum rotation angle (default: 360.0)
    degrees : bool, optional
        If True, angles are in degrees. If False, in radians (default: True)
    seed : int, optional
        Random seed for reproducibility (default: None)
        
    Returns
    -------
    rotated_data : dict
        Dictionary with randomly rotated coordinates
        
    Examples
    --------
    >>> # Random rotation between 50° and 280°
    >>> augmented = random_rotation_z(data, min_angle=50, max_angle=280)
    
    >>> # Random rotation in full range with fixed seed
    >>> augmented = random_rotation_z(data, seed=42)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random angle in specified range
    angle = np.random.uniform(min_angle, max_angle)
    
    return rotate_z_axis(data, angle, degrees=degrees)


def apply_augmentation(data: Dict[str, np.ndarray],
                       rotation_angle: Optional[float] = None,
                       rotation_range: Optional[Tuple[float, float]] = None,
                       flip_vertical_axis: bool = False,
                       degrees: bool = True,
                       seed: Optional[int] = None) -> Dict[str, np.ndarray]:
    """
    Apply combined augmentation transformations to event data.
    
    This is the main function to use for data augmentation. It can apply
    rotation and/or vertical flipping in sequence.
    
    Parameters
    ----------
    data : dict
        Dictionary containing event data
    rotation_angle : float, optional
        Specific rotation angle to apply. If None and rotation_range is None,
        no rotation is applied
    rotation_range : tuple of (min, max), optional
        Range for random rotation. If provided, overrides rotation_angle
    flip_vertical_axis : bool, optional
        Whether to flip the event vertically (default: False)
    degrees : bool, optional
        If True, angles are in degrees (default: True)
    seed : int, optional
        Random seed for reproducibility (default: None)
        
    Returns
    -------
    augmented_data : dict
        Dictionary with augmented event data
        
    Examples
    --------
    >>> # Rotate by 45° and flip
    >>> aug_data = apply_augmentation(data, rotation_angle=45, flip_vertical_axis=True)
    
    >>> # Random rotation between 50° and 280°, no flip
    >>> aug_data = apply_augmentation(data, rotation_range=(50, 280))
    
    >>> # Only vertical flip, no rotation
    >>> aug_data = apply_augmentation(data, flip_vertical_axis=True)
    """
    augmented_data = data.copy()
    
    # Apply rotation if specified
    if rotation_range is not None:
        min_angle, max_angle = rotation_range
        augmented_data = random_rotation_z(augmented_data, min_angle, max_angle, 
                                          degrees=degrees, seed=seed)
    elif rotation_angle is not None:
        augmented_data = rotate_z_axis(augmented_data, rotation_angle, degrees=degrees)
    
    # Apply vertical flip if specified
    if flip_vertical_axis:
        augmented_data = flip_vertical(augmented_data)
    
    return augmented_data


def load_event_from_hdf5(hdf5_path: str, event_index: int) -> Dict[str, np.ndarray]:
    """
    Load a single event from HDF5 file into augmentation-ready format.
    
    Supports both old and new HDF5 formats:
    - Old: vertex, particleStop, particleDir as arrays
    - New: vertex_x/y/z, particle_start_x/y/z, particle_stop_x/y/z, particle_dir_x/y/z as scalars
    
    Parameters
    ----------
    hdf5_path : str
        Path to HDF5 file
    event_index : int
        Index of event to load (0-based)
        
    Returns
    -------
    event_data : dict
        Dictionary containing event data ready for augmentation
        
    Raises
    ------
    ImportError
        If h5py is not installed
    KeyError
        If event not found in file
        
    Examples
    --------
    >>> event = load_event_from_hdf5("data.h5", event_index=0)
    >>> augmented = apply_augmentation(event, rotation_angle=90)
    """
    event_group_name = f"event_{event_index}"
    
    with h5py.File(hdf5_path, 'r') as f:
        if event_group_name not in f:
            available_events = len([k for k in f.keys() if k.startswith('event_')])
            raise KeyError(f"Event '{event_group_name}' not found in file. "
                          f"Available events: 0 to {available_events-1}")
        
        event_group = f[event_group_name]
        event_data = {}
        
        # Load hit positions (required)
        for key in ['hitx', 'hity', 'hitz']:
            if key in event_group:
                event_data[key] = event_group[key][:]
        
        # Load scalar metadata
        for key in ['towall', 'energy', 'dwall', 'n_digi_hits', 'event_type', 'trigger_time']:
            if key in event_group:
                event_data[key] = event_group[key][()]
        
        # Load PMT features
        for key in ['pmt_time', 'pmt_charge']:
            if key in event_group:
                event_data[key] = event_group[key][:]
        
        # Load vertex (handle both formats)
        if 'vertex' in event_group:
            event_data['vertex'] = event_group['vertex'][:]
        elif all(f'vertex_{coord}' in event_group for coord in ['x', 'y', 'z']):
            event_data['vertex'] = np.array([
                event_group['vertex_x'][()],
                event_group['vertex_y'][()],
                event_group['vertex_z'][()]
            ])
        elif all(f'particle_start_{coord}' in event_group for coord in ['x', 'y', 'z']):
            # Use particle_start as vertex
            event_data['vertex'] = np.array([
                event_group['particle_start_x'][()],
                event_group['particle_start_y'][()],
                event_group['particle_start_z'][()]
            ])
        
        # Load particle stop
        if 'particleStop' in event_group:
            event_data['particleStop'] = event_group['particleStop'][:]
        elif all(f'particle_stop_{coord}' in event_group for coord in ['x', 'y', 'z']):
            event_data['particleStop'] = np.array([
                event_group['particle_stop_x'][()],
                event_group['particle_stop_y'][()],
                event_group['particle_stop_z'][()]
            ])
        
        # Load particle direction
        if 'particleDir' in event_group:
            event_data['particleDir'] = event_group['particleDir'][:]
        elif all(f'particle_dir_{coord}' in event_group for coord in ['x', 'y', 'z']):
            event_data['particleDir'] = np.array([
                event_group['particle_dir_x'][()],
                event_group['particle_dir_y'][()],
                event_group['particle_dir_z'][()]
            ])
    
    return event_data


def augment_batch(data_list: list, 
                  augmentation_params: Dict,
                  seed: Optional[int] = None) -> list:
    """
    Apply augmentation to a batch of events.
    
    Parameters
    ----------
    data_list : list of dict
        List of event dictionaries to augment
    augmentation_params : dict
        Parameters to pass to apply_augmentation for each event.
        If 'rotation_range' is provided, each event gets a different random rotation
    seed : int, optional
        Base random seed. Each event will use seed + event_index
        
    Returns
    -------
    augmented_list : list of dict
        List of augmented events
        
    Examples
    --------
    >>> params = {'rotation_range': (0, 360), 'flip_vertical_axis': False}
    >>> augmented_events = augment_batch(events, params, seed=42)
    """
    augmented_list = []
    
    for i, event_data in enumerate(data_list):
        event_seed = seed + i if seed is not None else None
        augmented_event = apply_augmentation(event_data, seed=event_seed, **augmentation_params)
        augmented_list.append(augmented_event)
    
    return augmented_list


if __name__ == "__main__":
    # Simple test
    print("Event Augmentation Module")
    print("=" * 50)
    print("\nAvailable functions:")
    print("  - load_event_from_hdf5(hdf5_path, event_index)")
    print("  - rotate_z_axis(data, angle, degrees=True)")
    print("  - flip_vertical(data)")
    print("  - random_rotation_z(data, min_angle, max_angle)")
    print("  - apply_augmentation(data, **kwargs)")
    print("  - augment_batch(data_list, params)")
    print("\nSupports both old and new HDF5 formats:")
    print("  Old: vertex, particleStop, particleDir as arrays")
    print("  New: vertex_x/y/z, particle_start_x/y/z, particle_stop_x/y/z, particle_dir_x/y/z")
    print("\nFor visualization, use: python src/visualize_augmentation.py --help")

