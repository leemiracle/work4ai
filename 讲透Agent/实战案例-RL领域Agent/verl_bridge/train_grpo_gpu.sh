#!/bin/bash
# train_grpo_gpu.sh —— Layer 3 GPU 配方：Qwen2.5-1.5B + GRPO + rl_agent 任务环境
# ⚠️ 本机无 GPU 未实跑（诚实标注）；骨架逐行对照 verl-tool/examples/train/mathcoder/train_1.5b.sh
# 硬件需求：≥4×A100-40G（1.5B+FSDP+vLLM，do_offload=True 时可压到 2×24G 卡但需调 gpu_memory_utilization≤0.4）
# 前置：
#   1. verl-tool 与 verl 已安装（pip install -e ~/ai/verl-tool -e ~/ai/verl，需 vllm/ray）
#   2. 工具已 symlink 安装：bash verl_bridge/install_tool.sh
#   3. 数据已生成：python3 verl_bridge/make_dataset.py
set -ex

HOST=127.0.0.1
PORT=5055
TOOL_SERVER_URL=http://$HOST:$PORT/get_observation

# ① 起 tool server（rl_agent 环境：4 动作 + RLVR 判分）
python -m verl_tool.servers.serve --host $HOST --port $PORT --tool_type rl_agent --workers_per_tool 8 &
SERVER_PID=$!
trap "kill -9 $SERVER_PID" EXIT

# ② GRPO 训练（verl_tool 的 agent-loop trainer；参数名对照 mathcoder 官方配方）
PYTHONUNBUFFERED=1 python3 -m verl_tool.trainer.main_ppo \
    data.train_files=$PWD/verl_bridge/rl_agent_train.parquet \
    data.val_files=$PWD/verl_bridge/rl_agent_train.parquet \
    data.train_batch_size=64 \
    data.max_prompt_length=512 \
    data.max_response_length=1024 \
    actor_rollout_ref.model.path=Qwen/Qwen2.5-1.5B-Instruct \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.5 \
    actor_rollout_ref.rollout.temperature=1.0 \
    actor_rollout_ref.agent.tool_server_url=$TOOL_SERVER_URL \
    actor_rollout_ref.agent.max_turns=4 \
    algorithm.adv_estimator=grpo \
    trainer.n_gpus_per_node=4 \
    trainer.nnodes=1 \
    trainer.total_epochs=3 \
    trainer.project_name=rl-agent-verl \
    trainer.experiment_name=qwen1.5b-grpo-rlagent-env

# ③ reward 接入说明（配方外手动）：
#    verl_tool.trainer 的 reward manager 需注册 RlAgentTool.compute_score——
#    在 verl_tool/trainer/main_ppo.py 的 custom reward 挂点处 import：
#    from rl_agent_tool import RlAgentTool; reward_fn = RlAgentTool.compute_score
#    （Search-R1 同款分工：tool server 管轨迹，reward fn 管判分）
