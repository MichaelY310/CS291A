import json
from utils import *
import os


delusion = True
# delusion = False

base_dir = "/scr/yuan/CS291A/data/reasoning_data"
result_dir = "/scr/yuan/CS291A/results"
file_name = "14b_enriched.jsonl"
file_level_result = os.path.join(base_dir, os.path.join("file_level", file_name))
related_level_result = os.path.join(base_dir, os.path.join("related_level", file_name))
line_level_result = os.path.join(base_dir, os.path.join("line_level", file_name))
if delusion:
    line_level_result = str(line_level_result).replace(".jsonl", "_with_delusion.jsonl")
    file_name = str(file_name).replace(".jsonl", "_with_delusion.jsonl")

file_level_data = load_jsonl(str(file_level_result))
related_level_data = load_jsonl(str(related_level_result))
line_level_data = load_jsonl(str(line_level_result))


instance_ids = [data["instance_id"] for data in line_level_data]

combined_result = []

for instance_id in instance_ids:
    for data in file_level_data:
        if data["instance_id"] == instance_id:
            file_level_result = data
            break

    for data in related_level_data:
        if data["instance_id"] == instance_id:
            related_level_result = data
            break

    for data in line_level_data:
        if data["instance_id"] == instance_id:
            line_level_result = data
            break

    combined_result.append({
        "instance_id": instance_id,
        "found_files": file_level_result["found_files"],
        "found_related_locs": related_level_result["found_related_locs"],
        "found_edit_locs": line_level_result["found_edit_locs"],
        "actual_found_files": line_level_result["file_names"]
    })

with open(os.path.join(result_dir, file_name), "a") as f:
    for result in combined_result:
        f.write(json.dumps(result) + "\n")










