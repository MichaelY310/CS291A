from utils import *


def parse_golden_patch(split):
    map_id_to_patch_loc = {}
    splits = {'dev': 'data/dev-00000-of-00001.parquet', 'test': 'data/test-00000-of-00001.parquet', 'train': 'data/train-00000-of-00001.parquet'}
    df_test = pd.read_parquet("hf://datasets/princeton-nlp/SWE-bench/" + splits[split])
    for index, row in df_test.iterrows():
        modifications = extract_diff_info(row['patch'])
        map_id_to_patch_loc[row['instance_id']] = modifications
    return map_id_to_patch_loc


def parse_found_files_from_raw_output(raw_output, structure):
    model_found_files = raw_output.strip().split("\n")
    files, classes, functions = get_full_file_paths_and_classes_and_functions(structure)
    found_files = correct_file_paths(model_found_files, files)
    return found_files

def parse_found_lines_from_raw_output(raw_output, file_names):
    model_found_locs, file_names = localize_line_from_coarse_function_locs(raw_output, file_names)
    found_lines = []
    for i in range(len(model_found_locs)):
        file_name = file_names[i]
        lines = model_found_locs[i]
        lines = re.findall(r'line:\s*(\d+)', lines)
        for line in lines:
            found_lines.append(f"{file_name}:{line}")
    return found_lines


def localize_line_from_coarse_function_locs(answer_content, file_names, with_delusion=False):
    model_found_locs = extract_code_blocks(answer_content)
    if with_delusion:
        model_found_locs_separated, file_names = extract_locs_for_files_with_delusion(
            model_found_locs, file_names
        )
    else:
        model_found_locs_separated, file_names = extract_locs_for_files(
            model_found_locs, file_names
        )

    return model_found_locs_separated, file_names

def count_line_inclusions(ground_truth_lines, found_lines):
    found_dict = {}
    for line in found_lines:
        if ":" not in line:
            continue
        file, lineno = line.split(":")
        try:
            lineno = int(lineno)
        except ValueError:
            continue
        if file not in found_dict:
            found_dict[file] = set()
        found_dict[file].add(lineno)

    count = 0
    for line in ground_truth_lines:
        if ":" not in line:
            continue
        file, lineno = line.split(":")
        try:
            lineno = int(lineno)
        except ValueError:
            continue
        if file in found_dict:
            for found_lineno in found_dict[file]:
                if abs(found_lineno - lineno) <= 20:
                    count += 1
                    break
    return count

if __name__ == "__main__":
    found_lines = ["file1.py:45", "file2.py:100"]
    ground_truth_lines = ["file1.py:50", "file2.py:120", "file3.py:10"]

    inclusions = count_line_inclusions(ground_truth_lines, found_lines)
    print(inclusions)