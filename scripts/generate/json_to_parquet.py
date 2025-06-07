import json
import os
import random
import pandas as pd
from pathlib import Path
from utils import *

# Configuration parameters
INPUT_FILE = "/scr/yuan/CS291A/data/verl_training_data/file_level/433-enriched_claude3-7.jsonl"
TRAIN_RATIO = 0.8
RANDOM_SEED = 42

def split_and_convert_jsonl_to_parquet(input_file, train_ratio=0.8, random_seed=42):
    # Set random seed for reproducibility
    random.seed(random_seed)
    
    # Read the JSONL file
    data = load_jsonl(input_file)
    
    random.shuffle(data)
    
    # Split into train and validation sets
    split_idx = int(len(data) * train_ratio)
    train_data = data[:split_idx]
    val_data = data[split_idx:]

    for i in range(len(val_data)):
        tmp = val_data[i]
        tmp["extra_info"]["split"] = "test"
        val_data[i] = tmp
    
    # Create output paths
    input_path = Path(input_file)
    base_name = input_path.stem
    parent_dir = input_path.parent.name  # Get the parent directory name (e.g., 'file_level')
    
    # Create output directories
    parquet_base_dir = Path("/scr/yuan/CS291A/data/parquet")
    parquet_dir = parquet_base_dir / parent_dir
    os.makedirs(parquet_dir, exist_ok=True)
    
    # Save train and val JSONL files
    train_jsonl_path = input_path.parent / f"{base_name}_train.jsonl"
    val_jsonl_path = input_path.parent / f"{base_name}_val.jsonl"
    
    with open(train_jsonl_path, 'w') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
    
    with open(val_jsonl_path, 'w') as f:
        for item in val_data:
            f.write(json.dumps(item) + '\n')
    
    # Convert to parquet
    train_parquet_path = parquet_dir / f"{base_name}_train.parquet"
    val_parquet_path = parquet_dir / f"{base_name}_val.parquet"
    
    # Convert to DataFrame and save as parquet
    pd.DataFrame(train_data).to_parquet(train_parquet_path, index=False)
    pd.DataFrame(val_data).to_parquet(val_parquet_path, index=False)
    
    print(f"Processed {len(data)} examples:")
    print(f"Train set: {len(train_data)} examples")
    print(f"Validation set: {len(val_data)} examples")
    print(f"\nOutput files:")
    print(f"Train JSONL: {train_jsonl_path}")
    print(f"Val JSONL: {val_jsonl_path}")
    print(f"Train Parquet: {train_parquet_path}")
    print(f"Val Parquet: {val_parquet_path}")

if __name__ == "__main__":
    split_and_convert_jsonl_to_parquet(
        INPUT_FILE,
        train_ratio=TRAIN_RATIO,
        random_seed=RANDOM_SEED
    )
