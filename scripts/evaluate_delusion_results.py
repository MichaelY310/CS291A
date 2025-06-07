import re
import pandas as pd
import json
import libcst as cst
from parse.parse_strings import parse_golden_patch

map_id_to_patch_loc = parse_golden_patch("test")

instances_retrieve_files_incomplete = []
instances_lineno_incomplete = []
has_search_result = []
aaanum = 0
# parse the log of agentless to find retrieved locations
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/14B_5k_hybrid_3in1__1/loc_outputs.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/14B_5k_hybrid_direct_line__1/loc_outputs.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/7B_5k_hybrid_3in1__1/loc_outputs.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/7B_5k_hybrid_direct_line__1/loc_outputs.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/14b__enriched__1/loc_outputs.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/7b__enriched__1/loc_outputs.jsonl', 'r',
with open('/scr/yuan/CS291A/results/14b_enriched_with_delusion.jsonl', 'r',
# with open('/scr/yuan/CS291A/results/14b_enriched.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/32B_genloc_3in1__1/loc_outputs.jsonl', 'r',
# with open('/scratch/yuanyang/SURFI-p1-results/result_rebuttle/results_ablation/location/14b_enriched_2000/loc_outputs.jsonl', 'r',
          encoding='utf-8') as file:
    for line in file:
        aaanum = aaanum + 1
        data = json.loads(line)
        instance_id = data['instance_id']
        file_line_dict = {}
        retrieved_files = data['actual_found_files'][5:]
        for edit_locs_set in data['found_edit_locs']:
            for index, edit_locs in enumerate(edit_locs_set):
                if len(edit_locs) == 0:
                    continue
                if type(edit_locs) == str:
                    line_numbers = re.findall(r'line:\s*(\d+)', edit_locs)
                else:
                    line_numbers = re.findall(r'line:\s*(\d+)', edit_locs[0])
                for line_num in line_numbers:
                    # map file to line numbers
                    line_num = int(line_num)
                    if data['actual_found_files'][index] not in file_line_dict:
                        file_line_dict[data['actual_found_files'][index]] = set()
                    for i in range(-20, 21):
                        file_line_dict[data['actual_found_files'][index]].add(line_num + i)
                if line_numbers == [] and data['actual_found_files'][index] not in file_line_dict:
                    # if edit_locs[0] != '':
                    file_line_dict[data['actual_found_files'][index]] = set()

        # check whether all real patched files and linenos are included in the retrieved context
        incomplete_lineno = 0
        for real_mod_file in map_id_to_patch_loc[data['instance_id']]:
            if real_mod_file not in file_line_dict:
                instances_retrieve_files_incomplete.append(data['instance_id'])
                instances_lineno_incomplete.append(data['instance_id'])
                break

            for real_line_num in map_id_to_patch_loc[data['instance_id']][real_mod_file]:
                if real_line_num not in file_line_dict[real_mod_file]:
                    instances_lineno_incomplete.append(data['instance_id'])
                    incomplete_lineno = 1
                    break
            if incomplete_lineno == 1:
                break

print("length of instances_retrieve_files_incomplete: ", instances_retrieve_files_incomplete)
print("length of instances_retrieve_files_incomplete: ", len(instances_retrieve_files_incomplete))
print("length of instances_lineno_incomplete", len(instances_lineno_incomplete))