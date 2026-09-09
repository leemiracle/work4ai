# veRL 开发记录

## Quick Start

参考官方的 docker 镜像来配置环境：

```shell
docker run --runtime=nvidia -it --shm-size="40g" --gpus all -v /opt/dlami/nvme/.cache:/root/.cache --cap-add=SYS_ADMIN verlai/verl:vemlp-th2.4.0-cu124-vllm0.6.3-ray2.10-te1.7-v0.0.3

git clone https://github.com/volcengine/verl && cd verl && pip install .
```

接着，使用 PPO 对 Qwen2.5-0.5B-Instruct 在 GSM8K 上进行训练。GSM8K 是一个小学数学问题集，参考一个 example：

```python
input = "Katy makes coffee using teaspoons of sugar and cups of water in the ratio of 7:13. If she used a total of 120 teaspoons of sugar and cups of water, calculate the number of teaspoonfuls of sugar she used."

output = "The total ratio representing the ingredients she used to make the coffee is 7+13 = <<7+13=20>>20 Since the fraction representing the number of teaspoons she used is 7/20, she used 7/20120 = <<7/20120=42>>42 #### 42"
```

接着将 GSM8K 的数据预处理为 `parquet` 格式：

```bash
python3 examples/data_preprocess/gsm8k.py --local_dir ~/data/gsm8k
```

**设置奖励**：我们的测例采用显式的奖励函数来取代奖励模型。具体来说，强制模型生成的答案在 4 个 `#` 之后（比如 `#### 42`），然后正则匹配提取出答案并和 reference 做对比。正确答案分配 1 分，错误答案分配 0.1 分，没有答案分配 0 分。

**启动训练**：使用如下shell代码启动PPO训练：

```bash
CUDA_VISIBLE_DEVICES=7 PYTHONUNBUFFERED=1
python3 -m verl.trainer.main_ppo \
  data.train_files=$HOME/data/gsm8k/train.parquet \
  data.val_files=$HOME/data/gsm8k/test.parquet \
  data.train_batch_size=256 \
  data.val_batch_size=1312 \
  data.max_prompt_length=512 \
  data.max_response_length=256 \
  actor_rollout_ref.model.path=Qwen/Qwen2.5-0.5B-Instruct \
  actor_rollout_ref.actor.optim.lr=1e-6 \
  actor_rollout_ref.actor.ppo_mini_batch_size=64 \
  actor_rollout_ref.actor.ppo_micro_batch_size=4 \
  actor_rollout_ref.rollout.log_prob_micro_batch_size=8 \
  actor_rollout_ref.rollout.tensor_model_parallel_size=1 \
  actor_rollout_ref.rollout.gpu_memory_utilization=0.4 \
  actor_rollout_ref.ref.log_prob_micro_batch_size=4 \
  critic.optim.lr=1e-5 \
  critic.model.path=Qwen/Qwen2.5-0.5B-Instruct \
  critic.ppo_micro_batch_size=4 \
  algorithm.kl_ctrl.kl_coef=0.001 \
  trainer.logger=['console'] \
  +trainer.val_before_train=False \
  trainer.default_hdfs_dir=null \
  trainer.n_gpus_per_node=1 \
  trainer.nnodes=1 \
  trainer.save_freq=10 \
  trainer.test_freq=10 \
  trainer.total_epochs=15 2>&1 | tee verl_demo.log
```

训练启动成功后，关键指标 `val/test_score/openai/gsm8k` 每 `trainer.test_freq`步计算一次。具体的checkpoint 默认保存在: `checkpoints/${trainer.project_name}/${trainer.experiment_name}`
