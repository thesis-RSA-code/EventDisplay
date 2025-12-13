#!/usr/bin/env python3
"""
Compute pairwise distances between all PMTs and save as NumPy array.

This creates a symmetric distance matrix (N x N) where N is the number of PMTs.
The matrix can be used for fast KNN lookups at runtime.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import argparse
from scipy.spatial.distance import cdist
from typing import Tuple
import sys


def compute_distance_matrix(
    pmt_df: pd.DataFrame,
    chunk_size: int = 1000,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute pairwise Euclidean distances between all PMTs.
    
    Uses chunking to handle large matrices efficiently.
    
    Parameters
    ----------
    pmt_df : pd.DataFrame
        DataFrame with PMT data (must have 'tube_id', 'x', 'y', 'z' columns)
    chunk_size : int
        Chunk size for processing (default: 1000)
        
    Returns
    -------
    distance_matrix : np.ndarray
        Distance matrix as numpy array (N x N, float32)
    tube_ids : np.ndarray
        Array of tube_ids corresponding to matrix indices
    """
    n_pmts = len(pmt_df)
    print(f"Computing distance matrix for {n_pmts} PMTs...")
    print(f"Matrix size: {n_pmts} x {n_pmts} = {n_pmts**2:,} entries")
    
    # Extract positions
    positions = pmt_df[['x', 'y', 'z']].values
    tube_ids = pmt_df['tube_id'].values
    
    # Initialize distance matrix
    print("Allocating distance matrix...")
    distance_matrix = np.zeros((n_pmts, n_pmts), dtype=np.float32)
    
    # Compute distances in chunks to manage memory
    print(f"Computing distances (chunk size: {chunk_size})...")
    n_chunks = (n_pmts + chunk_size - 1) // chunk_size
    
    for i in range(n_chunks):
        start_i = i * chunk_size
        end_i = min((i + 1) * chunk_size, n_pmts)
        
        if (i + 1) % 10 == 0 or i == 0:
            print(f"  Processing chunk {i+1}/{n_chunks} (rows {start_i}-{end_i-1})...")
        
        # Compute distances for this chunk
        chunk_positions = positions[start_i:end_i]
        distances = cdist(chunk_positions, positions, metric='euclidean')
        distance_matrix[start_i:end_i, :] = distances
    
    return distance_matrix, tube_ids


def main():
    parser = argparse.ArgumentParser(
        description="Compute pairwise PMT distances and save as NumPy array"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=Path(__file__).parent / "hyperk_20inch_pmts_cyl_coords.csv",
        help="Input PMT CSV file (default: hyperk_20inch_pmts_cyl_coords.csv)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output .npy file path (default: pmt_distance_matrix.npy)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size for processing (default: 1000)"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    # Set default output path
    if args.output is None:
        args.output = args.input.parent / "pmt_distance_matrix.npy"
    else:
        # Ensure .npy extension
        if args.output.suffix != '.npy':
            args.output = args.output.with_suffix('.npy')
    
    # Tube IDs output path
    tube_ids_output = args.output.with_name(args.output.stem + '_tube_ids.npy')
    
    print("=" * 60)
    print("Computing PMT Distance Matrix")
    print("=" * 60)
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    
    # Load PMT data
    print("\nLoading PMT data...")
    pmt_df = pd.read_csv(args.input)
    print(f"✓ Loaded {len(pmt_df)} PMTs")
    
    # Verify required columns
    required_cols = ['tube_id', 'x', 'y', 'z']
    missing_cols = [col for col in required_cols if col not in pmt_df.columns]
    if missing_cols:
        print(f"Error: Missing required columns: {missing_cols}")
        return 1
    
    # Compute distance matrix
    print("\n" + "=" * 60)
    distance_matrix, tube_ids = compute_distance_matrix(pmt_df, args.chunk_size)
    
    # Print some statistics
    print("\n" + "=" * 60)
    print("Distance Statistics:")
    print("=" * 60)
    # Get upper triangle (excluding diagonal) for stats
    upper_triangle = np.triu(distance_matrix, k=1)
    upper_triangle = upper_triangle[upper_triangle > 0]
    
    print(f"  Min distance: {upper_triangle.min():.2f} cm")
    print(f"  Max distance: {upper_triangle.max():.2f} cm")
    print(f"  Mean distance: {upper_triangle.mean():.2f} cm")
    print(f"  Median distance: {np.median(upper_triangle):.2f} cm")
    
    # Save to NumPy array
    print("\n" + "=" * 60)
    print("Saving distance matrix to NumPy array...")
    print("=" * 60)
    print(f"Matrix shape: {distance_matrix.shape}")
    print(f"Data type: {distance_matrix.dtype}")
    print(f"Estimated file size: ~{distance_matrix.nbytes / (1024**3):.2f} GB")
    
    # Save distance matrix
    np.save(args.output, distance_matrix)
    print(f"✓ Saved distance matrix: {args.output}")
    
    # Save tube_ids mapping
    np.save(tube_ids_output, tube_ids)
    print(f"✓ Saved tube IDs mapping: {tube_ids_output}")
    
    # Get actual file sizes
    matrix_size = args.output.stat().st_size
    ids_size = tube_ids_output.stat().st_size
    print(f"  Distance matrix file size: {matrix_size / (1024**3):.2f} GB")
    print(f"  Tube IDs file size: {ids_size / (1024**2):.2f} MB")
    
    print("\n" + "=" * 60)
    print("Sample (first 5x5 submatrix):")
    print("=" * 60)
    print(f"Tube IDs: {tube_ids[:5]}")
    print(distance_matrix[:5, :5])
    
    print("\n" + "=" * 60)
    print("✓ Done!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())

