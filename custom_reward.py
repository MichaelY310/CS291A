from parse.parse_strings import parse_found_files_from_raw_output, parse_found_lines_from_raw_output, count_line_inclusions
import json

def switch_to_purdue_dir(dir):
    return dir.replace("/scr/structure", "/home/yuanyang/SURFI-p1/structure")

def compute_score(data_source, solution_str, ground_truth, extra_info=None):
    if data_source == "file_level":
        with open(switch_to_purdue_dir(extra_info["structure_file"]), "r") as f:
            structure = json.load(f)
        found_files = parse_found_files_from_raw_output(solution_str, structure)
        num_found = len(set(found_files).intersection(set(ground_truth.split("\n"))))
        print("=" * 100)
        print("File level: ")
        print("Found: ", sorted(found_files))
        print("Ground truth: ", sorted(ground_truth.split("\n")))
        print("Num found: ", num_found)
        print("=" * 100)
        total_num = len(set(ground_truth.split("\n")))
        return num_found / total_num
    elif data_source == "related_level":
        return 0.0
    elif data_source == "line_level":
        found_lines = parse_found_lines_from_raw_output(solution_str, extra_info["found_files"])
        ground_truth_lines = ground_truth.strip().split("\n")
        num_found = count_line_inclusions(ground_truth_lines, found_lines)
        print("=" * 100)
        print("Line level: ")
        print("Found: ", sorted(found_lines))
        print("Ground truth: ", sorted(ground_truth_lines))
        print("Num found: ", num_found)
        print("=" * 100)
        total_num = len(ground_truth_lines)
        return num_found / total_num

def compute_score_complicated(data_source, solution_str, ground_truth, extra_info=None):
    if data_source == "file_level":
        """
        k_max is the maximum number of files that the model can find
        here we expect the model to find 10 files at most
        """
        # Extract predicted and ground truth files
        with open(switch_to_purdue_dir(extra_info["structure_file"]), "r") as f:
            structure = json.load(f)
        found_files = parse_found_files_from_raw_output(solution_str, structure)
        ground_truth_files = set(ground_truth.strip().split("\n"))

        # Reward weights
        w_h = 0.6  # recall weight
        w_p = 0.5  # precision weight
        w_l = 0.25  # length penalty weight
        w_m = 0.5  # miss penalty weight
        k_max = 10

        n = len(found_files)
        h = len(set(found_files) & set(ground_truth_files))      # Intersection
        m = len(ground_truth_files) - h
        G_size = len(ground_truth_files)

        recall = h / G_size if G_size > 0 else 0
        precision = h / n if n > 0 else 0
        length_penalty = (n - 1) / (k_max - 1) if k_max > 1 else 0
        miss_penalty = m / G_size if G_size > 0 else 0

        reward = (
            w_h * recall +
            w_p * precision -
            w_l * length_penalty -
            w_m * miss_penalty
        )

        return reward

    elif data_source == "related_level":
        return 0.0
    elif data_source == "line_level":
        return 0.0