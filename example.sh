set -x

export CUDA_DEVICE_ORDER=PCI_BUS_ID
export CUDA_VISIBLE_DEVICES=4,5,6,7

cd /home/yuanyang/CS291A/verl

ray stop
CUDA_VISIBLE_DEVICES=4,5,6,7 ray start --head --port=6379 --num-gpus=4

# Run training with explicit GPU configuration
CUDA_VISIBLE_DEVICES=4,5,6,7 python3 -m verl.trainer.main_ppo \
   data.train_files=/home/yuanyang/CS291A/data/gsm8k/train.parquet \
   data.val_files=/home/yuanyang/CS291A/data/gsm8k/test.parquet \
   data.train_batch_size=128 \
   data.max_prompt_length=32768 \
   data.max_response_length=32768 \
   actor_rollout_ref.model.path='Qwen/Qwen2.5-Coder-0.5B' \
   actor_rollout_ref.actor.optim.lr=1e-6 \
   actor_rollout_ref.model.use_remove_padding=True \
   actor_rollout_ref.actor.ppo_mini_batch_size=32 \
   actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=4 \
   actor_rollout_ref.actor.fsdp_config.param_offload=True \
   actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
   actor_rollout_ref.model.enable_gradient_checkpointing=True \
   actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=4 \
   actor_rollout_ref.rollout.tensor_model_parallel_size=4 \
   actor_rollout_ref.rollout.name=vllm \
   actor_rollout_ref.rollout.gpu_memory_utilization=0.7 \
   actor_rollout_ref.rollout.max_num_batched_tokens=65536 \
   actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=4 \
   actor_rollout_ref.ref.fsdp_config.param_offload=True \
   critic.optim.lr=1e-5 \
   critic.model.use_remove_padding=True \
   critic.model.path='Qwen/Qwen2.5-Coder-0.5B' \
   critic.model.enable_gradient_checkpointing=True \
   critic.ppo_micro_batch_size_per_gpu=4 \
   critic.model.fsdp_config.param_offload=True \
   critic.model.fsdp_config.optimizer_offload=True \
   algorithm.kl_ctrl.kl_coef=0.001 \
   trainer.critic_warmup=0 \
   trainer.logger=['console','wandb'] \
   trainer.project_name='verl_example_gsm8k' \
   trainer.experiment_name='deepseek_llm_7b_function_rm' \
   trainer.n_gpus_per_node=4 \
   trainer.nnodes=1 \
   trainer.save_freq=-1 \
   trainer.test_freq=1 \
   trainer.total_epochs=15 $@

# Stop Ray cluster
ray stop

cd ..