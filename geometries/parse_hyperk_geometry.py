#!/usr/bin/env python3
"""
Parse Hyper-K geometry file and convert to pandas-readable format.

Extracts 20" PMT data with position, direction, tube ID, and region classification.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import argparse


def parse_hyperk_geometry(
    geometry_path: Path,
    z_cap_threshold: float = 3200.0,
) -> pd.DataFrame:
    """
    Parse Hyper-K geometry file and extract 20" PMT data.
    
    The 20" ID PMTs are encoded as:
    - Type 0: Top cap (z ≈ +3296.5, dir_z = -1)
    - Type 1: Barrel (r ≈ 3243, dir_z = 0)  
    - Type 2: Bottom cap (z ≈ -3296.5, dir_z = +1)
    
    Parameters
    ----------
    geometry_path : Path
        Path to geometry text file
    z_cap_threshold : float
        Z threshold to classify top/bottom caps (default: 3200 cm)
        
    Returns
    -------
    df : pd.DataFrame
        DataFrame with columns:
        - tube_id: PMT identifier
        - x, y, z: position in cm
        - r: radial distance from z-axis
        - theta: azimuthal angle in radians
        - cos_theta: cosine of azimuthal angle
        - sin_theta: sine of azimuthal angle
        - dir_x, dir_y, dir_z: direction vector (pointing inward)
        - region: 'barrel', 'top_cap', or 'bottom_cap'
    """
    pmts = []
    
    # 20" ID PMT types: 0=top_cap, 1=barrel, 2=bottom_cap
    ID_PMT_TYPES = {0, 1, 2}
    TYPE_TO_REGION = {
        0: 'top_cap',
        1: 'barrel',
        2: 'bottom_cap',
    }
    
    # Read header info
    with open(geometry_path, 'r') as f:
        # Line 1: "Detector radius & height  3242.96 6701.41"
        header_line = f.readline().strip()
        parts = header_line.split()
        # Numbers are at the end
        detector_radius = float(parts[-2])
        detector_height = float(parts[-1])
        
        print(f"Detector dimensions:")
        print(f"  Radius: {detector_radius:.2f} cm")
        print(f"  Height: {detector_height:.2f} cm")
        
        # Skip remaining header lines (lines 2-5)
        for _ in range(4):
            f.readline()
        
        # Parse PMT data
        for line in f:
            parts = line.strip().split()
            if len(parts) < 10:
                continue
            
            try:
                tube_id = int(parts[0])
                # parts[1] is secondary ID
                # parts[2] is some flag
                x = float(parts[3])
                y = float(parts[4])
                z = float(parts[5])
                dir_x = float(parts[6])
                dir_y = float(parts[7])
                dir_z = float(parts[8])
                pmt_type = int(parts[9])
                
                # Only keep 20" ID PMTs (types 0, 1, 2)
                if pmt_type not in ID_PMT_TYPES:
                    continue
                
                pmts.append({
                    'tube_id': tube_id,
                    'x': x,
                    'y': y,
                    'z': z,
                    'dir_x': dir_x,
                    'dir_y': dir_y,
                    'dir_z': dir_z,
                    'pmt_type': pmt_type,
                })
                
            except (ValueError, IndexError) as e:
                continue
    
    # Convert to DataFrame
    df = pd.DataFrame(pmts)
    
    if len(df) == 0:
        raise ValueError("No 20\" PMTs found in geometry file")
    
    # Add derived columns
    df['r'] = np.sqrt(df['x']**2 + df['y']**2)
    df['theta'] = np.arctan2(df['y'], df['x'])
    df['cos_theta'] = np.cos(df['theta'])
    df['sin_theta'] = np.sin(df['theta'])
    
    # Map pmt_type to region name
    df['region'] = df['pmt_type'].map(TYPE_TO_REGION)
    
    # Drop pmt_type column (region is more readable)
    df = df.drop(columns=['pmt_type'])
    
    # Reorder columns for clarity
    df = df[['tube_id', 'x', 'y', 'z', 'r', 'theta', 'cos_theta', 'sin_theta', 'dir_x', 'dir_y', 'dir_z', 'region']]
    
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Parse Hyper-K geometry and export to pandas-readable format"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=Path(__file__).parent / "Hyper_K_blablabla.txt",
        help="Input geometry file"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file path (default: same dir as input, .csv extension)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=['csv', 'parquet', 'both'],
        default='both',
        help="Output format (default: both)"
    )
    parser.add_argument(
        "--z-threshold",
        type=float,
        default=3200.0,
        help="Z threshold for cap classification (default: 3200 cm)"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    # Set default output path
    if args.output is None:
        args.output = args.input.parent / "hyperk_20inch_pmts"
    
    print("=" * 60)
    print("Parsing Hyper-K Geometry File")
    print("=" * 60)
    print(f"Input: {args.input}")
    
    # Parse geometry
    df = parse_hyperk_geometry(args.input, args.z_threshold)
    
    print(f"\n✓ Parsed {len(df)} 20\" PMTs")
    
    # Print summary stats
    print("\nRegion breakdown:")
    for region in ['barrel', 'bottom_cap', 'top_cap']:
        count = (df['region'] == region).sum()
        print(f"  {region}: {count} PMTs")
    
    print(f"\nPosition ranges:")
    print(f"  X: [{df['x'].min():.1f}, {df['x'].max():.1f}] cm")
    print(f"  Y: [{df['y'].min():.1f}, {df['y'].max():.1f}] cm")
    print(f"  Z: [{df['z'].min():.1f}, {df['z'].max():.1f}] cm")
    print(f"  R: [{df['r'].min():.1f}, {df['r'].max():.1f}] cm")
    
    # Save output
    print("\n" + "=" * 60)
    print("Saving output...")
    
    if args.format in ['csv', 'both']:
        csv_path = args.output.with_suffix('.csv')
        df.to_csv(csv_path, index=False)
        print(f"✓ Saved CSV: {csv_path}")
    
    if args.format in ['parquet', 'both']:
        parquet_path = args.output.with_suffix('.parquet')
        df.to_parquet(parquet_path, index=False)
        print(f"✓ Saved Parquet: {parquet_path}")
    
    print("\n" + "=" * 60)
    print("Sample data (first 5 rows):")
    print("=" * 60)
    print(df.head().to_string())
    
    print("\n" + "=" * 60)
    print("✓ Done!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())

