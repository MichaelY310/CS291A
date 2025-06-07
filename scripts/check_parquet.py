#!/usr/bin/env python3

import pandas as pd
import argparse
import sys

def display_parquet_info(file_path):
    try:
        # Read the parquet file
        df = pd.read_parquet(file_path)
        
        # Display basic information
        print("\n=== Parquet File Information ===")
        print(f"Number of rows: {len(df)}")
        print(f"Number of columns: {len(df.columns)}")
        
        # Get the first row
        first_row = df.iloc[0]
        
        print("\n=== First Row Data ===")
        for column in df.columns:
            print(f"{column}: {first_row[column]}")
        
        print("\n=== Column Names and Data Types ===")
        print(df.dtypes)
        
        print("\n=== First 5 rows of data ===")
        print(df.head())
        
        print("\n=== Basic Statistics ===")
        print(df.describe())
        
    except Exception as e:
        print(f"Error reading parquet file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():    
    # display_parquet_info("/scr/yuan/CS291A/verl/data/gsm8k/test.parquet")
    display_parquet_info("/scr/yuan/CS291A/data/parquet/file_level/433-enriched_claude3-7_val.parquet")

if __name__ == "__main__":
    main()
