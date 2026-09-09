# Qwen2.5VL GRPO with SGLang

## 环境配置

### 创建新的 docker

使用前需要配置好 `WANDB_API_KEY`，参考[这个过程](https://community.wandb.ai/t/where-can-i-find-the-api-token-for-my-project/7914)。

```bash
# 如果你的系统没有配置过 HF_TOKEN 和 WANDB_API_KEY，请先配置好
# 这里的 cache 映射路径是在 atlas 集群上，如果需要使用自己的路径，请自行修改
docker run -it --name h100_verl_{your_name} --gpus all \
    --shm-size 32g \
    -v /.cache:/root/.cache \
    --env "HF_TOKEN=$HF_TOKEN" \
    --env "WANDB_API_KEY=$WANDB_API_KEY" \
    --ipc=host \
    lmsysorg/sglang:latest \
    /bin/bash
```

进入 docker 后，可以查看被映射的环境变量：

```bash
echo $HF_TOKEN
echo $WANDB_API_KEY
```

以后每次从 docker 里面 exit 出来，再用这个指令可以重启：

```bash
docker start -i h100_verl_{your_name}
```

### 基于源码安装 SGLang

配置 python 环境

```bash
mkdir -p /tmp
chmod 1777 /tmp
apt update
apt install -y python3.10 python3.10-venv
python3 -m ensurepip --upgrade
python3 -m venv ~/.python/verl-sglang
source ~/.python/verl-sglang/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade uv
```

先安装 veRL，再安装 SGLang。

```bash
cd ~
git clone https://github.com/volcengine/verl.git
cd verl
python3 -m uv pip install -e ".[sglang,geo]"
python3 -m uv pip install -r ./requirements.txt
```

> 如果遇到这个报错：
```
ModuleNotFoundError: No module named 'torch'

hint: This error likely indicates that `flash-attn@2.7.4.post1` depends on `torch`, but doesn't declare it as a build dependency. If
`flash-attn` is a first-party package, consider adding `torch` to its `build-system.requires`. Otherwise, `uv pip install torch` into the
environment and re-run with `--no-build-isolation`.
```
> 按照下面的步骤 fix
```
python3 -m uv pip install wheel
python3 -m uv pip install -r ./requirements.txt --no-build-isolation
```

后安装 SGLang，为了对齐 torch 版本。

```bash
cd ~
git clone https://github.com/sgl-project/sglang.git
cd sglang
python3 -m uv pip install --upgrade pip
python3 -m uv pip install -e "python[all]" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer-python
```
额外安装`qwen-vl`依赖：
```
uv pip install qwen_vl_utils
```

## 4 卡启动 Qwen2.5VL GRPO 训练脚本，并且使用 SGLang 作为 rollout 引擎

```bash
cd ~/verl
export CUDA_VISIBLE_DEVICES=0,1,2,3

# 拉取并预处理 geo3k 数据集
python examples/data_preprocess/geo3k.py --local_dir ~/data/geo3k
```

打开你 docker 里面的 `~/verl/examples/grpo_trainer/run_qwen2_5_vl-7b.sh` 文件，直接修改为下方脚本：

```bash
set -x
ENGINE=${1:-vllm}
export VLLM_ATTENTION_BACKEND=XFORMERS

python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files=$HOME/data/geo3k/train.parquet \
    data.val_files=$HOME/data/geo3k/test.parquet \
    data.train_batch_size=512 \
    data.max_prompt_length=1024 \
    data.max_response_length=2048 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    data.image_key=images \
    actor_rollout_ref.model.path=Qwen/Qwen2.5-VL-7B-Instruct \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=128 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=10 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.01 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=False \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=False \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=20 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
    actor_rollout_ref.rollout.name=$ENGINE \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.2 \
    actor_rollout_ref.rollout.enable_chunked_prefill=False \
    actor_rollout_ref.rollout.enforce_eager=False \
    actor_rollout_ref.rollout.free_cache_engine=False \
    actor_rollout_ref.rollout.n=5 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=20 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    algorithm.kl_ctrl.kl_coef=0.001 \
    trainer.critic_warmup=0 \
    trainer.logger=['console','wandb'] \
    trainer.project_name='verl_grpo_example_geo3k' \
    trainer.experiment_name='qwen2_5_vl_7b_function_rm' \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.save_freq=-1 \
    trainer.test_freq=5 \
    trainer.total_epochs=15
```

如果遇到了这个报错: `(TaskRunner pid=45593) RuntimeError: No backend type associated with device type cpu`:
修改:`sglang/python/sglang/srt/utils.py`: `force_cpu_device: bool = True,` -> `False`.

修改结束后，启动 4 卡训练，可以稳定报错：

```bash
# 启动 GRPO 训练脚本， 记得去掉 examples/grpo_trainer/run_qwen2_5_vl-7b.sh 结尾的 $@
# 注意，跑的是 qwen 2.5 的，不是 qwen2 的，别把文件弄混了
bash examples/grpo_trainer/run_qwen2_5_vl-7b.sh sglang
```
