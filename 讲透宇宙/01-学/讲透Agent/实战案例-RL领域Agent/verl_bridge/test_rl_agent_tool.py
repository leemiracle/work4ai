#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_rl_agent_tool.py —— rl_agent_tool 的本地协议测试（Layer 1 验收，零 GPU 零 ray）
跑法：cd 讲透Agent/实战案例-RL领域Agent && python3 verl_bridge/test_rl_agent_tool.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rl_agent_tool import RlAgentTool                     # noqa: E402
from verl_tool.servers.tools.base import registered_tools  # noqa: E402（经 rl_agent_tool 的 sys.path）

TID = "traj-test-001"
def check(name, cond):
    print(f"  {'✅' if cond else '❌'} {name}")
    assert cond, name

tool = RlAgentTool(num_workers=1)

print("[1] 注册机制（verl_tool 协议）")
check("registered_tools 含 rl_agent", "rl_agent" in registered_tools)
check("usage_inst 含全部动作 tag", all(t in tool.get_usage_inst() for t in ("<search>", "<run_experiment>", "<recall>", "<answer>")))

print("[2] 轨迹 1：search → answer（正常路径）")
task = "GRPO 和 PPO 的区别是什么？"
obs1, done1, valid1 = tool.conduct_action(TID, "让我先检索 <search>GRPO PPO 区别</search>", {"task": task})
check("search 返回证据", "讲透" in obs1 or ".md:" in obs1)
check("search 未终止", done1 is False and valid1 is True)
obs2, done2, _ = tool.conduct_action(TID, "基于证据，<answer>GRPO 省掉了价值网络，用组内相对奖励作 baseline</answer>", {"task": task})
check("answer 终止轨迹", done2 is True)
env = tool.load_env(TID)
check("env 记录 chain", "kb_search" in env.get("chain", []))
check("env 记录 answer", "价值网络" in env.get("answer", ""))
score = RlAgentTool.compute_score(task, env["answer"], env["chain"], ["价值网络", "组"])
print(f"  [score] {score}")
check("reward ∈ (0, 1.2] 且含证据分", 0.5 < score <= 1.2)

print("[3] 轨迹 2：非法动作 + 超步数熔断 + RLVR 反短路")
tid2 = "traj-test-002"
obs, done, valid = tool.conduct_action(tid2, "你好呀", {"task": task})
check("无 tag → invalid", valid is False)
tool.delete_env(tid2)
for i in range(10):                                                    # 灌满步数
    obs, done, valid = tool.conduct_action(tid2, f"<search>第{i}次</search>", {"task": task})
check("超步数强制终止", done is True and "强制终止" in obs)
s0 = RlAgentTool.compute_score(task, "", [], ["价值网络"])              # 无 answer
check("无 answer → 0 分（RLVR）", s0 == 0.0)
s_no_ev = RlAgentTool.compute_score(task, "价值网络", ["recall"], ["价值网络"])
s_ev = RlAgentTool.compute_score(task, "价值网络", ["kb_search"], ["价值网络"])
check("证据塑形分（+0.2 有检索）", abs(s_ev - s_no_ev - 0.2) < 1e-6)

print("[4] parse_action 边界")
check("多 tag 取最后", tool.parse_action("<search>a</search> 然后 <answer>b</answer>")[0][0] == "answer")
check("空 recall 可解析", tool.parse_action("想想 <recall></recall>")[0][0] == "recall")

tool.delete_env(TID); tool.delete_env(tid2)
print("\n=== 全部通过：rl_agent 任务环境已可被 verl_tool 消费（Layer 1 ✅）===")
