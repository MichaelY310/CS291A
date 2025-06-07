set -x

export RAY_TMPDIR=/home/yuanyang/tmp/
export TMPDIR=/home/yuanyang/tmp
export HYDRA_FULL_ERROR=1
export PYTHONPATH=/home/yuanyang/CS291A/scripts:$PYTHONPATH
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=0,1
export RAY_ADDRESS=127.0.0.1:6382

cd /home/yuanyang/CS291A/verl

ray start --head --port=6382

CUDA_VISIBLE_DEVICES=0,1 python3 -m verl.trainer.main_ppo \
   data.train_files='/home/yuanyang/CS291A/data/parquet/file_level/433-enriched_claude3-7_train.parquet' \
   data.val_files='/home/yuanyang/CS291A/data/parquet/file_level/433-enriched_claude3-7_val.parquet' \
   data.train_batch_size=4 \
   data.max_prompt_length=32768 \
   data.max_response_length=2048 \
   actor_rollout_ref.model.path='secmlr/SWE-BENCH-433-enriched-set-claude-3in1-localization-with-reasoning_qwen_code_0.5b_433_enriched' \
   actor_rollout_ref.actor.optim.lr=1e-6 \
   actor_rollout_ref.model.use_remove_padding=True \
   actor_rollout_ref.actor.ppo_mini_batch_size=4 \
   actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=1 \
   actor_rollout_ref.actor.fsdp_config.param_offload=True \
   actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
   actor_rollout_ref.model.enable_gradient_checkpointing=True \
   actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=1 \
   actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
   actor_rollout_ref.rollout.name=vllm \
   actor_rollout_ref.rollout.gpu_memory_utilization=0.9 \
   actor_rollout_ref.rollout.max_num_batched_tokens=35000 \
   actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=1 \
   actor_rollout_ref.ref.fsdp_config.param_offload=True \
   critic.optim.lr=1e-5 \
   critic.model.use_remove_padding=True \
   critic.model.path='secmlr/SWE-BENCH-433-enriched-set-claude-3in1-localization-with-reasoning_qwen_code_0.5b_433_enriched' \
   critic.model.enable_gradient_checkpointing=True \
   critic.ppo_micro_batch_size_per_gpu=1 \
   critic.model.fsdp_config.param_offload=True \
   critic.model.fsdp_config.optimizer_offload=True \
   algorithm.kl_ctrl.kl_coef=0.001 \
   trainer.critic_warmup=0 \
   trainer.logger=['console','wandb'] \
   trainer.project_name='verl_CS291A' \
   trainer.experiment_name='qwen-0.5b__433-enriched_claude3-7__file_level__finetuned__complex' \
   trainer.n_gpus_per_node=2 \
   trainer.nnodes=1 \
   trainer.save_freq=100 \
   trainer.test_freq=1 \
   trainer.total_epochs=15 \
   custom_reward_function.path='/home/yuanyang/CS291A/custom_reward.py' \
   custom_reward_function.name='compute_score_complicated' \
   reward_model.enable=False

cd ..