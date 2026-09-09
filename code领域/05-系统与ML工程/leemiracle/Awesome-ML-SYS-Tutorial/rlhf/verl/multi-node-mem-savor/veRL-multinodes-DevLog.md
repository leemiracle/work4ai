## 背景
目前的 main 上的并行写法等价于限制了 `tp<=8`，为了支持 deepseek 相关的训练，需要 verl engine 的跨 node 支持。

## Proposal

https://gist.github.com/fzyzcjy/01b851e045b970f16e63580b12dbf7ab

## Step by step setup

**1.** 登陆 novita_h20_1

```bash
ssh novita_h20_1
docker exec -it {YOUR CONTAINER NAME} /bin/zsh
```

**2.** 安装 verl-sglang 需要的依赖

```bash
apt install python3.10-venv

# 创建 venv
python3 -m venv .venv --upgrade-deps
source .venv/bin/activate
pip install build wheel

# 安装 SGlang
git clone -b v0.4.4.post3 https://github.com/sgl-project/sglang.git
cd sglang
pip install --upgrade pip
pip install -e "python[all]" --find-links https://flashinfer.ai/whl/cu124/torch2.5/flashinfer-python

# 安装 verl
cd ..
git clone https://github.com/ocss884/verl.git verl-sglang
cd verl-sglang
git switch sglang_multinode
pip install ".[gpu]"
```

**3.** 设置 Huggingface 的环境变量

novita的磁盘空间不大，注意用以下配置共享模型权重和数据集文件：

```bash
# Huggingface
export HF_DATASETS_CACHE="/model/shared/.cache/huggingface/datasets"
export HF_HOME="/model/shared/.cached/huggingface"
```

**3.** 在 **novita_h20_1** 启动 ray

```bash
ray start --head --dashboard-host=0.0.0.0
```

运行结束后会看到下面的信息：

<img src=../img/gcs-address.png />

记住上面的 GCS address

**4.** 在在 **novita_h20_2** 加入 ray cluster

在 novita_h20_2 重复上面的 1-3 配置好环境后，运行下面的命令，令 node2 加入 cluster

```bash
ray start --address='10.94.16.4:6379'
```

看到下面的信息说明加入成功：

<img src=../img/ray-runtime-start.png />

运行完毕后回到 novita_h20_1，运行：

```bash
ray status
```
可以看到此时有两个 node 加入了！CHEERS！

<img width="506" src=../img/multi-node-status.png />

**5.** 运行实验

多机实验启动脚本，本次实验使用 Qwen2-7B-Instruct，2 机 4 卡。测试环境如下：

<details>
<summary>torchrun DP=2，TP=2 （跨机TP）</summary>
 
```bash
#在node0上
torchrun --nnodes=2 --nproc_per_node=2 --master_addr=<NODE0 IP> --master_port=34567 --node_rank 0 torchrun_verlengine.py
#在node1上
torchrun --nnodes=2 --nproc_per_node=2 --master_addr=<NODE0 IP> --master_port=34567 --node_rank 1 torchrun_verlengine.py
```
</details>

<details>
<summary>verl rollout DP=2，TP=2 （跨机TP）</summary>
 
```bash
set -x

gsm8k_train_path=$HOME/data/gsm8k/train.parquet
gsm8k_test_path=$HOME/data/gsm8k/test.parquet

train_files="['$gsm8k_train_path']"
test_files="['$gsm8k_test_path']"

python3 -m verl.trainer.main_ppo \
    data.train_files="$train_files" \
    data.val_files="$test_files" \
    data.train_batch_size=1024 \
    data.max_prompt_length=1024 \
    data.max_response_length=1 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    actor_rollout_ref.model.path=Qwen/Qwen2-7B-Instruct \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=256 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=4 \
    actor_rollout_ref.rollout.name=sglang \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=16 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    critic.optim.lr=1e-5 \
    critic.model.use_remove_padding=True \
    critic.model.path=Qwen/Qwen2-7B-Instruct \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_micro_batch_size_per_gpu=8 \
    critic.model.fsdp_config.param_offload=True \
    critic.model.fsdp_config.optimizer_offload=True \
    algorithm.kl_ctrl.kl_coef=0.0001 \
    trainer.critic_warmup=0 \
    trainer.logger=['console'] \
    trainer.n_gpus_per_node=2 \
    trainer.nnodes=2 \
    trainer.save_freq=-1 \
    trainer.test_freq=10 \
    trainer.total_epochs=15 $@
```
</details>

<details>
<summary>verl rollout DP=1，TP=4 （单机TP）</summary>
 
```
set -x

gsm8k_train_path=$HOME/data/gsm8k/train.parquet
gsm8k_test_path=$HOME/data/gsm8k/test.parquet

train_files="['$gsm8k_train_path']"
test_files="['$gsm8k_test_path']"

python3 -m verl.trainer.main_ppo \
    data.train_files="$train_files" \
    data.val_files="$test_files" \
    data.train_batch_size=1024 \
    data.max_prompt_length=1024 \
    data.max_response_length=1 \
    data.filter_overlong_prompts=True \
    data.truncation='error' \
    actor_rollout_ref.model.path=Qwen/Qwen2-7B-Instruct \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.actor.ppo_mini_batch_size=256 \
    actor_rollout_ref.actor.ppo_micro_batch_size_per_gpu=8 \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    actor_rollout_ref.rollout.log_prob_micro_batch_size_per_gpu=16 \
    actor_rollout_ref.rollout.tensor_model_parallel_size=2 \
    actor_rollout_ref.rollout.name=sglang \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.6 \
    actor_rollout_ref.ref.log_prob_micro_batch_size_per_gpu=16 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    critic.optim.lr=1e-5 \
    critic.model.use_remove_padding=True \
    critic.model.path=Qwen/Qwen2-7B-Instruct \
    critic.model.enable_gradient_checkpointing=True \
    critic.ppo_micro_batch_size_per_gpu=8 \
    critic.model.fsdp_config.param_offload=True \
    critic.model.fsdp_config.optimizer_offload=True \
    algorithm.kl_ctrl.kl_coef=0.0001 \
    trainer.critic_warmup=0 \
    trainer.logger=['console'] \
    trainer.n_gpus_per_node=2 \
    trainer.nnodes=2 \
    trainer.save_freq=-1 \
    trainer.test_freq=10 \
    trainer.total_epochs=15 $@
```
</details>

注：verl rollout均可直接使用`multinode_sglang.sh`文件来测试

## 常见问题

**1.** `pip install .[sglang]` 失败  
   这里错误种类很多，不全部列举，只写几个我印象比较深的错误：
  - Cargo 不存在
  - pip resolve deps 耗时特别久后突然 fail  
  ...

请运行下面的命令将你的 `pip` 升级到最新的 `25.0.1`。目前使用旧版（如 py3.10 自带的 pip==22.0）安装 verl-sglang 可能会出现 pip 无法正确解析依赖的情况：

```bash
pip install --upgrade pip
```

## Debug记录（priority 1-5）
- [x] `CUDA initialization: Unexpected` error from cudaGetDeviceCount() (**5**)

`CUDA_VISIBLE_DEVICES`不合法的设置导致，注意检查sglang_rollout里替换`CUDA_VISIBLE_DEVICES`时是否会all gather出如`0,1,0,1`这种不合法的值

- [ ] `VerlEngine`无法启动`deepseek-ai/deepseek-llm-7b-chat` (**4**)

[模型结构](https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat/blob/main/config.json)其实就是`Llama`，我(linjunrong)已经尝试过
- python -m sglang.launch_server --tp 4 --model-path deepseek-ai/deepseek-llm-7b-chat --host 0.0.0.0
- engine = Engine(model_path="deepseek-ai/deepseek-llm-7b-chat", tp_size=4, node_rank=0, nnodes=1)

二者均可以成功，需要检查一下verlengine使用什么的额外参数导致了下面的报错。[related issue](https://github.com/pytorch/pytorch/issues/145168) from youkaichao
<details>
 <summary>error</summary>
 
```shell
[2025-04-01 23:22:06 TP1] Scheduler hit an exception: Traceback (most recent call last):
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/managers/scheduler.py", line 1999, in run_scheduler_process
    scheduler = Scheduler(server_args, port_args, gpu_id, tp_rank, dp_rank)
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/managers/scheduler.py", line 249, in __init__
    self.tp_worker = TpWorkerClass(
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/managers/tp_worker_overlap_thread.py", line 63, in __init__
    self.worker = TpModelWorker(server_args, gpu_id, tp_rank, dp_rank, nccl_port)
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/managers/tp_worker.py", line 74, in __init__
    self.model_runner = ModelRunner(
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_executor/model_runner.py", line 169, in __init__
    self.initialize(min_per_gpu_memory)
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_executor/model_runner.py", line 179, in initialize
    self.load_model()
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_executor/model_runner.py", line 392, in load_model
    self.model = get_model(
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_loader/__init__.py", line 22, in get_model
    return loader.load_model(
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_loader/loader.py", line 370, in load_model
    model.load_weights(self._get_all_weights(model_config, model))
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/models/llama.py", line 481, in load_weights
    for name, loaded_weight in weights:
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_loader/loader.py", line 343, in _get_all_weights
    yield from self._get_weights_iterator(primary_weights)
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_loader/loader.py", line 329, in <genexpr>
    return ((source.prefix + name, tensor) for (name, tensor) in weights_iterator)
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/sglang/srt/model_loader/weight_utils.py", line 460, in pt_weights_iterator
    torch.cuda.empty_cache()
  File "/data/gpu-use/verl-sglang/.venv/lib/python3.10/site-packages/torch/cuda/memory.py", line 192, in empty_cache
    torch._C._cuda_emptyCache()
RuntimeError: captures_underway.empty() INTERNAL ASSERT FAILED at "../c10/cuda/CUDACachingAllocator.cpp":2967, please report a bug to PyTorch.
```
</details>

<details>
 <summary>sglang.check_env</summary>
 
 ```bash
 Python: 3.10.12 (main, Feb  4 2025, 14:57:36) [GCC 11.4.0]
CUDA available: True
GPU 0,1,2,3: NVIDIA H800
GPU 0,1,2,3 Compute Capability: 9.0
CUDA_HOME: /data/cuda/cuda-12.4/cuda
NVCC: Cuda compilation tools, release 12.4, V12.4.131
CUDA Driver Version: 535.129.03
PyTorch: 2.5.1+cu124
sglang: 0.4.4.post3
sgl_kernel: 0.0.5.post4
flashinfer: Module Not Found
triton: 3.1.0
transformers: 4.50.0
torchao: 0.9.0
numpy: 2.2.4
aiohttp: 3.11.14
fastapi: 0.115.12
hf_transfer: 0.1.9
huggingface_hub: 0.30.0
interegular: 0.3.3
modelscope: 1.24.1
orjson: 3.10.16
outlines: 0.1.11
packaging: 24.2
psutil: 7.0.0
pydantic: 2.11.1
multipart: Module Not Found
zmq: Module Not Found
uvicorn: 0.34.0
uvloop: 0.21.0
vllm: Module Not Found
xgrammar: 0.1.17
openai: 1.69.0
tiktoken: 0.9.0
anthropic: 0.49.0
litellm: 1.65.0
decord: 0.6.0
NVIDIA Topology: 
	[4mGPU0	GPU1	GPU2	GPU3	NIC0	NIC1	NIC2	NIC3	NIC4	NIC5	NIC6	NIC7	NIC8	NIC9	NIC10	NIC11	NIC12	NIC13	NIC14	NIC15	NIC16	CPU Affinity	NUMA Affinity	GPU NUMA ID[0m
GPU0	 X 	NV8	NV8	NV8	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS				N/A
GPU1	NV8	 X 	NV8	NV8	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS				N/A
GPU2	NV8	NV8	 X 	NV8	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS				N/A
GPU3	NV8	NV8	NV8	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX				N/A
NIC0	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS				
NIC1	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS				
NIC2	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS				
NIC3	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS				
NIC4	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS				
NIC5	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS				
NIC6	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS				
NIC7	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS				
NIC8	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX				
NIC9	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS	SYS				
NIC10	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS	SYS				
NIC11	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS	SYS				
NIC12	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS	SYS				
NIC13	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS	SYS				
NIC14	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS	SYS				
NIC15	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 	SYS				
NIC16	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	SYS	PIX	SYS	SYS	SYS	SYS	SYS	SYS	SYS	 X 				

Legend:

  X    = Self
  SYS  = Connection traversing PCIe as well as the SMP interconnect between NUMA nodes (e.g., QPI/UPI)
  NODE = Connection traversing PCIe as well as the interconnect between PCIe Host Bridges within a NUMA node
  PHB  = Connection traversing PCIe as well as a PCIe Host Bridge (typically the CPU)
  PXB  = Connection traversing multiple PCIe bridges (without traversing the PCIe Host Bridge)
  PIX  = Connection traversing at most a single PCIe bridge
  NV#  = Connection traversing a bonded set of # NVLinks

NIC Legend:

  NIC0: mlx5_0
  NIC1: mlx5_1
  NIC2: mlx5_2
  NIC3: mlx5_3
  NIC4: mlx5_4
  NIC5: mlx5_5
  NIC6: mlx5_6
  NIC7: mlx5_7
  NIC8: mlx5_8
  NIC9: mlx5_9
  NIC10: mlx5_10
  NIC11: mlx5_11
  NIC12: mlx5_12
  NIC13: mlx5_13
  NIC14: mlx5_14
  NIC15: mlx5_15
  NIC16: mlx5_16


ulimit soft: 524288

 ```
</details>

<details>
 <summary>复现脚本，单机 DP=1 TP=4 </summary>
 
 1. 将`torchrun_verlengine.py`的`== Parallel ==`部分改为
 ```
 dp, tp, pp = 1, 4, 1
 device_count = 4
 model_name = "deepseek-ai/deepseek-llm-7b-chat"
 ```
 
 2.运行下面的命令
 ```bash
 torchrun --nnodes=1 --nproc_per_node=4 --master_addr=<NODE0 IP> --master_port=34567 torchrun_verlengine.py
 ```
</details>

- [ ] `[torch_memory_saver.cpp] CUresult error  result=2 file=csrc/torch_memory_saver.cpp func=cu_mem_create line=103` (**5**)

```bash
ValueError: TP rank 0 could finish the model loading, but there are other ranks that didn't finish loading. It is likely due to unexpected failures (e.g., OOM) or a slow node
```

 1. 将`torchrun_verlengine.py`中`== Parallel ==`部分改为
```
dp, tp, pp = 1, 8, 1
device_count = 8
model_name = "moonshotai/Moonlight-16B-A3B-Instruct"
```

 2.运行下面的命令
 ```bash
 torchrun --nnodes=1 --nproc_per_node=8 --master_addr=<NODE0 IP> --master_port=34567 torchrun_verlengine.py
 ```

测试使用的月暗家用了deepseekV3结构的小模型，看起来memory saver和deepseekV3结构存在一定冲突，当前优先级最高的事项
