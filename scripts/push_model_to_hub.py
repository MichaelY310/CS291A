#!/usr/bin/env python
# encoding: utf-8
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfApi, create_repo
import torch
import fire
from glob import glob
from collections import defaultdict
import os
from pathlib import Path


def main(fsdp_checkpoint_path, huggingface_model_path, token=None):
    """
    Combine model shards and upload to Hugging Face Hub.
    
    Args:
        fsdp_checkpoint_path: Path to directory containing model shards
        huggingface_model_path: Original model path on Hugging Face (e.g., Qwen/Qwen2.5-Coder-0.5B-Instruct)
        token: Hugging Face API token (optional, can be set via HF_TOKEN environment variable)
    """
    # Get token from args or environment
    token = token or os.environ.get("HF_TOKEN")
    if not token:
        raise ValueError("Hugging Face token must be provided either as argument or HF_TOKEN environment variable")

    # Extract model name from path for repo name
    model_name = Path(fsdp_checkpoint_path).parent.parent.name
    repo_id = f"CS291A/{model_name}"

    # Create repo if it doesn't exist
    api = HfApi(token=token)
    try:
        create_repo(repo_id, token=token, repo_type="model", exist_ok=True)
    except Exception as e:
        print(f"Error creating repo: {e}")
        return

    print("Loading and combining model shards...")
    state_dict = defaultdict(list)

    # Find world size from the first matching file
    model_files = glob(f"{fsdp_checkpoint_path}/model_world_size_*_rank_*.pt")
    if not model_files:
        raise ValueError(f"No model shard files found in {fsdp_checkpoint_path}")
    
    # Extract world size from filename
    world_size = int(model_files[0].split("world_size_")[1].split("_")[0])
    
    for rank in range(world_size):
        filepath = f"{fsdp_checkpoint_path}/model_world_size_{world_size}_rank_{rank}.pt"
        print('Loading', filepath)
        # Set weights_only=False to handle PyTorch 2.6's default behavior change
        this_state_dict = torch.load(filepath, weights_only=False)
        for key, value in this_state_dict.items():
            state_dict[key].append(value.to_local())

    for key in state_dict:
        state_dict[key] = torch.cat(state_dict[key], dim=0)

    print("Initializing model with base model config...")
    config = AutoConfig.from_pretrained(huggingface_model_path)
    model = AutoModelForCausalLM.from_config(config)
    model.load_state_dict(state_dict)

    print(f"Pushing model to {repo_id}...")
    model.push_to_hub(repo_id, token=token)

    print("Loading and pushing tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(huggingface_model_path)
    tokenizer.push_to_hub(repo_id, token=token)

    # Add model card
    model_card = f"""---
language: en
license: other
base_model: {huggingface_model_path}
tags:
- code
- code-generation
- instruction-tuning
---

# Model Description

This model is fine-tuned from {huggingface_model_path} for code generation tasks.
"""
    
    api.upload_file(
        path_or_fileobj=model_card.encode(),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
        token=token
    )

    print(f"Model successfully uploaded to https://huggingface.co/{repo_id}")


if __name__ == "__main__":
    fire.Fire(main)
