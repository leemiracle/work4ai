# OpenRLHF SGLang Version

## 环境配置

理论上只要同时安装 OpenRLHF SGLang 和 DeepSpeed 即可。但是这里推荐使用 OpenRLHF 的 docker 镜像，进行挂载：

```bash
docker run --runtime=nvidia -it --shm-size="40g" --cap-add=SYS_ADMIN   -v {YOUR_DATA_DIR}:/var/lib/docker   
nvcr.io/nvidia/pytorch:24.07-py3 bash
```

接着，把 docker commit 保存下来，`docker ps -a` 查找 `<container_id>`，然后 `docker commit <container_id> openrlhf`，下次直接 `docker run --gpus all -it openrlhf` 就可以直接进入 docker 了。

然后，进入 docker，安装 OpenRLHF-SGLang 发行版和 SGLang：

```bash
pip install torch
git clone -b dev_pr https://github.com/zhaochenyang20/OpenRLHF-SGLang.git
cd OpenRLHF-SGLang
pip install .
```

如果出现了 `flash_attn` 的安装错误，可以仿照修改 `~/.zshrc` 文件，添加：

```bash
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:/data/chayenne/miniconda3/envs/rlhf-sglang/lib/python3.11/site-packages/nvidia/cusparse/lib:$LD_LIBRARY_PATH
export CUDA_HOME=/usr/local/cuda-12.1
```

然后，安装 SGLang 的最新发行版：

```bash
git clone https://github.com/sgl-project/sglang.git
cd sglang

pip install --upgrade pip
pip install -e "python[all]" --find-links https://flashinfer.ai/whl/cu124/torch2.4/flashinfer/
```

## 运行 PPO

```bash
# 启动 ray，自行设置 RAY_TEMP_DIR，RLHF_CKPT_DIR WANDB_API_KEY 环境变量
ray start --head --node-ip-address 127.0.0.1 --num-gpus 3 --port 1234 --temp-dir=$RAY_TEMP_DIR

# 在 ray 的输出中找到 RAY_HEAD_IP，然后提交任务
ray job submit --address="<RAY_HEAD_IP>:1234" \
--runtime-env-json="{
  \"working_dir\": \"${RLHF_CKPT_DIR}\",
}" \
   -- python3 -m openrlhf.cli.train_ppo_ray \
   --backend sglang \
   --ref_num_nodes 1 \
   --ref_num_gpus_per_node 1 \
   --reward_num_nodes 1 \
   --reward_num_gpus_per_node 1 \
   --critic_num_nodes 1 \
   --critic_num_gpus_per_node 1 \
   --actor_num_nodes 1 \
   --actor_num_gpus_per_node 1 \
   --vllm_num_engines 1 \
   --vllm_tensor_parallel_size 1 \
   --colocate_critic_reward \
   --colocate_actor_ref \
   --pretrain OpenRLHF/Llama-3-8b-sft-mixture \
   --reward_pretrain OpenRLHF/Llama-3-8b-rm-mixture \
   --save_path ${RLHF_CKPT_DIR}/examples/llama3-8b-rlhf \
   --save_steps 5 \
   --micro_train_batch_size 8 \
   --train_batch_size 32 \
   --micro_rollout_batch_size 32 \
   --rollout_batch_size 1024 \
   --max_samples 100000 \
   --max_epochs 2 \
   --prompt_max_len 1024 \
   --generate_max_len 1024 \
   --zero_stage 3 \
   --bf16 \
   --actor_learning_rate 5e-7 \
   --critic_learning_rate 9e-6 \
   --init_kl_coef 0.01 \
   --prompt_data OpenRLHF/prompt-collection-v0.1 \
   --input_key context_messages \
   --apply_chat_template \
   --packing_samples \
   --normalize_reward \
   --adam_offload \
   --flash_attn \
   --gradient_checkpointing \
   --use_wandb $WANDB_API_KEY \
   --wandb_run_name sglang \
   --wandb_project openrlhf
```



