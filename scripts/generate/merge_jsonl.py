import json
import os

# Input files
first_file = "/scr/yuan/CS291A/data/reasoning_data/related_level/14b_1.jsonl"
second_file = "/scr/yuan/CS291A/data/reasoning_data/related_level/14b_1 copy.jsonl"

# Output file
output_file = "/scr/yuan/CS291A/data/reasoning_data/related_level/14b_enriched.jsonl"

def merge_jsonl_files():
    # First, load all entries from both files into dictionaries
    first_entries = {}
    second_entries = {}
    
    # Load first file
    with open(first_file, 'r') as f:
        for line in f:
            entry = json.loads(line)
            first_entries[entry['instance_id']] = entry
    
    # Load second file
    with open(second_file, 'r') as f:
        for line in f:
            entry = json.loads(line)
            second_entries[entry['instance_id']] = entry
    
    # Merge entries: overwrite existing ones and add new ones
    merged_entries = first_entries.copy()  # Start with all entries from first file
    merged_entries.update(second_entries)  # Update with entries from second file
    
    # Write all entries to output file
    with open(output_file, 'w') as f_out:
        for entry in merged_entries.values():
            f_out.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    merge_jsonl_files() 