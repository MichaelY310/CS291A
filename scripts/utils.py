import json

import re
import pandas as pd
import json
import libcst as cst
import os


def extract_diff_info(diff_text):
    file_changes = {}
    file_diff_pattern = re.compile(r'(diff --git a/(.*?) b/.*?)((?=diff --git a/)|\Z)', re.DOTALL)
    for file_diff in file_diff_pattern.finditer(diff_text):
        full_diff = file_diff.group(1)
        file_name = file_diff.group(2)

        line_changes = []
        line_num_pattern = re.compile(r'@@ -\d+,\d+ \+(\d+),(\d+) @@')
        for match in line_num_pattern.finditer(full_diff):
            start_line = int(match.group(1))
            line_changes.append(start_line)

        file_changes[file_name] = line_changes

    return file_changes

def load_jsonl(filepath):
    with open(filepath, "r") as file:
        return [json.loads(line) for line in file]
    

def get_full_file_paths_and_classes_and_functions(structure, current_path=""):
    """
    Recursively retrieve all file paths, classes, and functions within a directory structure.

    Arguments:
    structure -- a dictionary representing the directory structure
    current_path -- the path accumulated so far, used during recursion (default="")

    Returns:
    A tuple containing:
    - files: list of full file paths
    - classes: list of class details with file paths
    - functions: list of function details with file paths
    """
    files = []
    classes = []
    functions = []
    for name, content in structure.items():
        if isinstance(content, dict):
            if (
                not "functions" in content.keys()
                and not "classes" in content.keys()
                and not "text" in content.keys()
                and not "imports" in content.keys()
                and not "import_interval" in content.keys()
            ) or not len(content.keys()) == 5:
                # or guards against case where functions and classes are somehow part of the structure.
                next_path = f"{current_path}/{name}" if current_path else name
                (
                    sub_files,
                    sub_classes,
                    sub_functions,
                ) = get_full_file_paths_and_classes_and_functions(content, next_path)
                files.extend(sub_files)
                classes.extend(sub_classes)
                functions.extend(sub_functions)
            else:
                next_path = f"{current_path}/{name}" if current_path else name
                files.append((next_path, content.get("text", ""), content.get("imports", []), content.get("import_interval", [])))
                if "classes" in content:
                    for clazz in content["classes"]:
                        classes.append(
                            {
                                "file": next_path,
                                "name": clazz["name"],
                                "start_line": clazz["start_line"],
                                "end_line": clazz["end_line"],
                                "methods": [
                                    {
                                        "name": method["name"],
                                        "start_line": method["start_line"],
                                        "end_line": method["end_line"],
                                        "used_globals": method.get("used_globals",{}),
                                    }
                                    for method in clazz.get("methods", [])
                                ],
                            }
                        )
                if "functions" in content:
                    for function in content["functions"]:
                        function["file"] = next_path
                        functions.append(function)
        else:
            next_path = f"{current_path}/{name}" if current_path else name
            files.append(next_path)

    return files, classes, functions


def correct_file_paths(model_found_files, files, include_partial_paths=True):
    found_files = []
    if model_found_files:
        for model_file in model_found_files:
            if not model_file:
                continue
            found_match = False
            # Check if any model found file is a subset of the current file path
            for file_content in files:
                file = file_content[0]  # the first element is file path
                if model_file == file:
                    found_files.append(file)
                    found_match = True
            if include_partial_paths and not found_match:  # If exact match is not found, we do a partial match search
                for file_content in files:
                    file = file_content[0]
                    if file.endswith(model_file) or model_file.endswith(file):
                        found_files.append(file)
                        break  # No need to check further, we found a match
        return found_files
    else:
        return []
    

def ensure_file_directory(file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)


def extract_code_blocks(text):
    pattern = r"```\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    if len(matches) == 0:
        if "```" in text:
            return [text.split("```", 1)[-1].strip()]
    return matches


def extract_locs_for_files(locs, file_names):
    for i in range(len(locs)):
        locs[i] = locs[i].replace("method:", "function:")

    results = {fn: [] for fn in file_names}
    current_file_name = None
    for loc in locs:
        for line in loc.splitlines():
            if line.strip().endswith(".py"):
                current_file_name = line.strip()
            elif line.strip() and any(
                line.startswith(w)
                for w in ["line:", "function:", "class:", "variable:"]
            ):
                if current_file_name in results:
                    results[current_file_name].append(line)
                else:
                    pass
    return ["\n".join(results[fn]) for fn in file_names], file_names


def extract_locs_for_files_with_delusion(locs, file_names):
    for i in range(len(locs)):
        locs[i] = locs[i].replace("method:", "function:")

    results = {fn: [] for fn in file_names}
    current_file_name = None
    for loc in locs:
        for line in loc.splitlines():
            if line.strip().endswith(".py"):
                current_file_name = line.strip()
            elif line.strip() and any(
                line.startswith(w)
                for w in ["line:", "function:", "class:", "variable:"]
            ):
                if current_file_name in results:
                    results[current_file_name].append(line)
                else:
                    results[current_file_name] = [line]
    
    # Create ordered list of keys: file_names first, then any additional keys
    ordered_keys = list(file_names)  # Start with file_names in their original order
    additional_keys = [k for k in results.keys() if k not in file_names]  # Get keys not in file_names
    ordered_keys.extend(additional_keys)  # Add additional keys at the end
    
    return [["\n".join(results[fn])] for fn in ordered_keys], ordered_keys

