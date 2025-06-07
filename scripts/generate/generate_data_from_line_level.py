import json
from datasets import load_dataset
from utils import *
from scripts.parse.parse_strings import parse_golden_patch, parse_found_files_from_raw_output
import os
from tqdm import tqdm
from generate_structure import regenerate_structure


data_source = "file_level"
data_source_file = "/scr/yuan/CS291A/data/reasoning_data/file_level/433-enriched_claude3-7.jsonl"
save_dir = os.path.join("/scr/yuan/CS291A/data/verl_training_data/file_level", data_source_file.split("/")[-1])
ensure_file_directory(save_dir)
if os.path.exists(save_dir):
    existing = load_jsonl(save_dir)
else:
    existing = []
existing = [e["extra_info"]["instance_id"] for e in existing]
with open("/scr/yuan/CS291A/bad_parse_structures.txt", 'r') as f:
    bad_parse_structures = f.read().split("\n")


benchmark = "full"
split = "train"
if benchmark == "lite":
    swe_bench_data = load_dataset("princeton-nlp/SWE-bench_Lite", split=split, download_mode="reuse_cache_if_exists")
elif benchmark == "verified":
    swe_bench_data = load_dataset("princeton-nlp/SWE-bench_Verified", split=split, download_mode="reuse_cache_if_exists")
elif benchmark == "full":
    swe_bench_data = load_dataset("princeton-nlp/SWE-bench", split=split, download_mode="reuse_cache_if_exists")
else:
    swe_bench_data = None
golden_patch_data = parse_golden_patch(split)



with open(data_source_file, "r") as f:
    reasoning_dataset = load_jsonl(data_source_file)
    found = False
    for reasoning_data in tqdm(reasoning_dataset):
        instance_id = reasoning_data["instance_id"]
        # if instance_id != "mesonbuild__meson-10630":
        #     continue
        if instance_id in existing or instance_id in bad_parse_structures:
            continue
        print(instance_id)
        for bench_data in swe_bench_data:
            if instance_id == bench_data["instance_id"]:
                regenerate_structure(bench_data)
                structure_dir = os.path.join("/scr/structure", f"{instance_id}.jsonl")
                with open(structure_dir, "r") as structure_file:
                    structure = json.load(structure_file)
                # print(structure)
                golden_patch = golden_patch_data[instance_id]
                golden_files = list(golden_patch.keys())



                for raw_output in reasoning_data["response"]:
                    found_files = parse_found_files_from_raw_output(raw_output, structure)

                    generated_training_data = {
                        "data_source": data_source,
                        "prompt": [{
                            "role": "user",
                            "content": reasoning_data["prompt"]
                        }],
                        "ability": "code",
                        "reward_model": {
                            "style": "rule",
                            "ground_truth": "\n".join(golden_files),
                        },
                        "extra_info": {
                            'split': split,
                            'instance_id': instance_id,
                            'found_files': found_files,
                            'index': 0
                        }
                    }
                found = True
                break
        assert found, "No matching instance found for instance_id: " + instance_id
        with open(save_dir, "a") as f:
            f.write(json.dumps(generated_training_data) + "\n")


