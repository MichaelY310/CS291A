import json

# Input files
file_without_delusion = "/scr/yuan/CS291A/results/14b_enriched.jsonl"
file_with_delusion = "/scr/yuan/CS291A/results/14b_enriched_with_delusion.jsonl"

def compare_files():
    # Load both files into dictionaries keyed by instance_id
    without_delusion_data = {}
    with_delusion_data = {}
    
    # Load file without delusion
    with open(file_without_delusion, 'r') as f:
        for line in f:
            entry = json.loads(line)
            without_delusion_data[entry['instance_id']] = entry
    
    # Load file with delusion
    with open(file_with_delusion, 'r') as f:
        for line in f:
            entry = json.loads(line)
            with_delusion_data[entry['instance_id']] = entry
    
    # Compare entries
    mismatches = []
    for instance_id in without_delusion_data:
        if instance_id in with_delusion_data:
            without_delusion_files = set(without_delusion_data[instance_id]['found_files'])
            with_delusion_files = set(with_delusion_data[instance_id]['actual_found_files'])
            
            if without_delusion_files != with_delusion_files:
                mismatches.append({
                    'instance_id': instance_id,
                    'without_delusion': list(without_delusion_files),
                    'with_delusion': list(with_delusion_files)
                })
    
    # Print results
    print(f"Total instances compared: {len(without_delusion_data)}")
    print(f"Number of mismatches: {len(mismatches)}")
    print("\nMismatches:")
    for mismatch in mismatches:
        print(f"\nInstance ID: {mismatch['instance_id']}")
        print(f"Without delusion: {mismatch['without_delusion']}")
        print(f"With delusion: {mismatch['with_delusion']}")

if __name__ == "__main__":
    compare_files() 