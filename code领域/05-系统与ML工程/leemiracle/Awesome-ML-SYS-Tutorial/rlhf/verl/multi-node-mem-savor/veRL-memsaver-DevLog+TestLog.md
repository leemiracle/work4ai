# VeRL-SGLang-memsaver Installation and Testing Guide
## 背景
SGLang进入训练框架之后，需要保持`enable_memory_saver=True`开启以便在rollout结束后释放显存给别的模块使用

## verl 完整的memory saver PR需要
- [x] memory saver找不到头文件安装失败 https://github.com/fzyzcjy/torch_memory_saver/pull/2
- [x] 跨进程传tensor错误 https://github.com/sgl-project/sglang/pull/4565
- [x] 更新verl-sglang[镜像](https://hub.docker.com/repository/docker/ocss884/verl-sglang/tags/ngc-th2.5.1-cu126-sglang0.4.4.post3/sha256:d70a80468cb2dc60597ce3aaeb2b29df5ac247c3d908b5ac24f7ab2ce7f6d810)至0.4.4.post3
- [x] 在verl engine中默认开启memory saver
- [x] 更新verl对sglang rollout的依赖

verl的pr，等待CI通过后即可merge
- https://github.com/volcengine/verl/pull/756

## 环境配置

### 创建新的 Python 虚拟环境

```bash
python3 -m venv ~/.python/veRL-mem-saver
source ~/.python/veRL-mem-saver/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade uv
```

## 安装和配置

### 安装 veRL 和依赖

```bash
# 克隆 veRL 代码库
git clone https://github.com/SwordFaith/verl.git
cd verl

# 安装 veRL 的SGLang依赖
python3 -m uv pip install ".[sglang]"
python3 -m uv pip install ".[gpu]"
```

### 创建数据集

```bash
# 创建 GSM8K 数据集
cd ~/verl  # 确保你在 verl 目录下
python examples/data_preprocess/gsm8k.py
```

## 运行测试

使用以下命令运行测试脚本：

```bash
DATA_DIR=$HOME/data/gsm8k
TIME=$(date +"%Y-%m-%d-%H-%M")
python3 -m verl.trainer.main_ppo \
    actor_rollout_ref.rollout.name=sglang \
    data.train_files=$DATA_DIR/train.parquet \
    data.val_files=$DATA_DIR/test.parquet \
    data.train_batch_size=64 \
    data.val_batch_size=1312 \
    data.max_prompt_length=512 \
    data.max_response_length=1 \
    actor_rollout_ref.model.path=Qwen/Qwen2-7B-Instruct \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=64 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=16 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=4 \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \
    actor_rollout_ref.rollout.free_cache_engine=True \
    actor_rollout_ref.ref.log_prob_micro_batch_size=16 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    critic.optim.lr=1e-5 \
    critic.model.use_remove_padding=True \
    critic.model.path=Qwen/Qwen2-7B-Instruct \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_micro_batch_size=16 \
    critic.model.fsdp_config.param_offload=True \
    critic.model.fsdp_config.optimizer_offload=True \
    algorithm.kl_ctrl.kl_coef=0.001 \
    trainer.critic_warmup=0 \
    trainer.logger=['console'] \
    +trainer.val_before_train=True \
    trainer.default_hdfs_dir=null \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=10 \
    trainer.total_epochs=1 2>&1 | tee verl_demo.log
```

运行脚本后，日志文件 `verl_demo.log` 将保存在当前目录中。您可以使用以下命令查找它：

```bash
find / -name verl_demo.log 2>/dev/null
```

