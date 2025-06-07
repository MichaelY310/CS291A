import json
import os
from parse.parse_strings import localize_line_from_coarse_function_locs

line_level_data = "/scr/yuan/CS291A/data/reasoning_data/line_level/14b_enriched.jsonl"
file_level_data = "/scr/yuan/CS291A/data/reasoning_data/file_level/14b_enriched.jsonl"
output_file = "/scr/yuan/CS291A/data/reasoning_data/line_level/14b_enriched_with_delusion.jsonl"

def process_data():
    # Read file level data to get found_files
    file_level_entries = {}
    with open(file_level_data, 'r') as f:
        for line in f:
            entry = json.loads(line)
            file_level_entries[entry['instance_id']] = entry['found_files']

    # Process original data and update found_edit_locs
    with open(line_level_data, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            entry = json.loads(line)
            instance_id = entry['instance_id']
            
            file_names = file_level_entries.get(instance_id, [])
            entry['original_file_names'] = file_names
            
            # Get answer_contents from response
            answer_contents = entry['response']
            reasoning_contents = entry['reasoning_content']
            for i in range(len(answer_contents)):
                answer_contents[i] = answer_contents[i][len(reasoning_contents[i])+len("<think><\think>"):]
            
            found_edit_locs_dicts = []
            for answer_content in answer_contents:
                # Update found_edit_locs using localize_line_from_coarse_function_locs
                found_edit_locs, file_names = localize_line_from_coarse_function_locs(
                    answer_content=answer_content,
                    file_names=file_names,
                    with_delusion=True
                )
                found_edit_locs_dicts.append(dict(zip(file_names, found_edit_locs)))
            
            file_freq_map = {}
            for found_edit_locs_dict in found_edit_locs_dicts:
                for file_name in found_edit_locs_dict.keys():
                    if file_name not in file_freq_map:
                        file_freq_map[file_name] = 0
                    if len(found_edit_locs_dict[file_name]) != 0:
                        file_freq_map[file_name] += 1
            top_5_files = sorted(file_freq_map.items(), key=lambda x: x[1], reverse=True)[:5]
            top_5_file_names = [file for file, freq in top_5_files]
            
            for i in range(len(found_edit_locs_dicts)):
                found_edit_locs_dicts[i] = {k: v for k, v in found_edit_locs_dicts[i].items() if k in top_5_file_names}
                for file_name in top_5_file_names:
                    if file_name not in found_edit_locs_dicts[i]:
                        found_edit_locs_dicts[i][file_name] = []                
                found_edit_locs_dicts[i] = {k: found_edit_locs_dicts[i][k] for k in top_5_file_names}
            
            # Update the entry with new found_edit_locs and file_names
            # Convert each dictionary's values to a list and maintain the order
            entry['found_edit_locs'] = [[found_edit_locs_dicts[i][k] for k in top_5_file_names] for i in range(len(found_edit_locs_dicts))]
            entry['file_names'] = top_5_file_names
            
            # Write updated entry to output file
            f_out.write(json.dumps(entry) + '\n')

if __name__ == "__main__":
    process_data()