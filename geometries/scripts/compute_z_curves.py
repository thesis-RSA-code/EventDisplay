import pandas as pd
import numpy as np
import torch

def expand_bits(v):
    """
    Spreads the bits of an integer v (up to 10 bits) 
    so that there are two zeros between each bit.
    Example: 1111 -> 1001001001
    Adapted for 3D Morton coding.
    """
    v = (v * 0x00010001) & 0xFF0000FF
    v = (v * 0x00000101) & 0x0F00F00F
    v = (v * 0x00000011) & 0xC30C30C3
    v = (v * 0x00000005) & 0x49249249
    return v

def morton_3d(x, y, z):
    """
    Interleaves bits of x, y, z.
    We cast to native python int() to avoid NumPy overflow warnings/errors.
    """
    # Force conversion to Python native int (arbitrary precision)
    xx = expand_bits(int(x))
    yy = expand_bits(int(y))
    zz = expand_bits(int(z))
    return (xx << 2) + (yy << 1) + zz

def generate_z_curve_lookup(csv_path, output_path="hk_pmt_z_curve.pt"):
    print(f"Loading geometry from {csv_path}...")
    df = pd.read_csv(csv_path)

    # 1. Extract Coordinates
    # We use x, y, z. 
    # Even though HK is a cylinder, a 3D Z-curve works perfectly fine 
    # to preserve locality on the manifold surface.
    coords = df[['x', 'y', 'z']].values.astype(np.float32)
    tube_ids = df['tube_id'].values.astype(np.int64)

    print(f"Found {len(tube_ids)} PMTs.")

    # 2. Normalize to [0, 1] range
    min_c = coords.min(axis=0)
    max_c = coords.max(axis=0)
    
    # Add a tiny epsilon to max to avoid getting exactly 1.0 (which would floor to out of bounds)
    norm_coords = (coords - min_c) / (max_c - min_c + 1e-6)

    # 3. Quantize to 10-bit integers (0 to 1023)
    # 1024^3 grid is enough resolution to separate ~40k PMTs
    resolution = 1024 
    quantized = (norm_coords * resolution).astype(np.uint32)

    # 4. Compute Morton Code (Z-value)
    print("Computing Morton Codes...")
    # Vectorized function application is tricky with bitwise ops in pure numpy across columns 
    # efficiently without C++, but a simple list comprehension is fast enough for 40k rows.
    z_codes = [
        morton_3d(q[0], q[1], q[2]) 
        for q in quantized
    ]
    df['z_code'] = z_codes

    # 5. Determine the Rank
    # We sort the dataframe by the Morton code.
    # The new row order defines the "Rank" (0 to N-1)
    df_sorted = df.sort_values('z_code').reset_index(drop=True)
    
    # Create a mapping: tube_id -> Rank
    # rank_map = { tube_id: rank }
    # But since we want a fast tensor lookup, we'll build a sparse-like tensor.
    
    # Map back to original IDs
    # df_sorted['tube_id'] is the PMT ID
    # df_sorted.index is the Rank (0, 1, 2...)
    
    # We create an array where array[tube_id] = Rank
    max_id = tube_ids.max()
    lookup_tensor = torch.zeros(max_id + 1, dtype=torch.long)
    
    # Fill with -1 (or 0) to detect errors if an ID is missing, 
    # though 0 is safer if valid IDs start at 0.
    lookup_tensor[:] = 0 
    
    # Fill the values
    sorted_ids = df_sorted['tube_id'].values
    ranks = np.arange(len(sorted_ids))
    
    # lookup_tensor[ID] = Rank
    lookup_tensor[sorted_ids] = torch.from_numpy(ranks)

    print("Example Check:")
    print(f"PMT ID {sorted_ids[0]} -> Rank 0 (Start of curve)")
    print(f"PMT ID {sorted_ids[-1]} -> Rank {ranks[-1]} (End of curve)")

    # 6. Save
    torch.save(lookup_tensor, output_path)
    print(f"Saved lookup tensor to {output_path}")
    print(f"Tensor shape: {lookup_tensor.shape}")
    print("Usage: ranks = loaded_tensor[hit_pmt_ids]")

# Example usage:
if __name__ == "__main__":
    # Replace with your actual CSV path
    geom_csv_path =  "/home/amaterasu/work/EventDisplay/geometries/hyperk_20inch_pmts.csv"
    output_path = "/home/amaterasu/work/EventDisplay/geometries/hk_pmt_z_curve.pt"
    generate_z_curve_lookup(geom_csv_path, output_path)