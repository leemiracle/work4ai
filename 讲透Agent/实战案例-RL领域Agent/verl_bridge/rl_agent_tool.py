#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rl_agent_tool.py —— rl_agent 任务环境 → verl_tool 协议适配器（三层集成 Layer 1）
================================================================================
关系定位（一句话）：rl_agent 给 verl 贡献的是【任务环境】（工具+判分器+kb），
不是 brain——verl 训练时 policy=LLM 权重更新；rl_agent 的 RLBrain/Q 表是 toy policy 不参与。
这补上了 prompt工程手册/11 章方案对决的缺口：Ctx-APO 是 A 形态（不动权重），verl 是 B 深水区（动权重）。

接入协议（verl_tool/servers/tools/base.py）：
  - 子类 BaseTool + @register_tool，文件名（symlink 名）= tool_type = "rl_agent"
  - parse_action(raw_llm_output) → (action, valid)：解析 LLM 的动作 tag
  - conduct_action(trajectory_id, action, extra_field) → (observation, done, valid)
  - env_cache 按轨迹隔离状态（chain）——正好承载多轮工具循环
  - compute_score(trajectory) → float：外部 RLVR reward（verl reward manager 调用，Search-R1 同款分工）

动作协议（LLM 输出侧，与 rl_agent 4 动作对齐 + finish）：
  <search>query</search>            → kb_search（真实检索项目知识库）
  <run_experiment>bandit</run_experiment> → 真跑 toy 实验
  <recall></recall>                 → 注入历史教训
  <answer>最终答案</answer>          → finish（done=True）

本地测试（无需 GPU/ray/verl 安装）：python3 verl_bridge/test_rl_agent_tool.py
GPU 训练配方：见 train_grpo_gpu.sh（Layer 3）
"""
import re, sys, os

# ---- rl_agent 模块导入（零安装：直接指案例目录）----
_BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
_CASE_DIR = os.path.dirname(_BRIDGE_DIR)
if _CASE_DIR not in sys.path:
    sys.path.insert(0, _CASE_DIR)

# ---- verl_tool 导入（两种模式：symlink 进包内 / 直接 import base）----
try:
    from verl_tool.servers.tools.base import BaseTool, register_tool   # pip -e 或包内
except ImportError:                                                     # 本地开发：直接指 verl-tool 仓库
    _VT = None
    for _p in (os.path.join(os.path.dirname(_CASE_DIR), "..", "..", "..", "verl-tool"),
               "~/ai/verl-tool"):
        _p = os.path.abspath(_p)
        if os.path.isdir(_p):
            _VT = _p; break
    if _VT is None:
        raise ImportError("verl-tool 未找到：pip install -e verl-tool 或检查路径 ~/ai/verl-tool")
    sys.path.insert(0, _VT)
    from verl_tool.servers.tools.base import BaseTool, register_tool

import rl_agent as RA   # 案例本体：kb_search/run_experiment/recall/classify_state/EXPERIMENTS

MAX_TURNS = 8

@register_tool
class RlAgentTool(BaseTool):
    """rl_agent 任务环境的 verl_tool 包装：4 动作 + answer 终止 + RLVR 外部判分。"""
    tool_type = "rl_agent"

    def get_usage_inst(self):                                          # 给 LLM 的使用说明（进 system prompt）
        return ("你可以使用工具回答强化学习问题：\n"
                "<search>查询词</search> 检索项目知识库\n"
                "<run_experiment>实验名</run_experiment> 真跑实验（可选: " + "/".join(sorted(RA.EXPERIMENTS)) + "）\n"
                "<recall></recall> 查看历史教训\n"
                "找到答案后用 <answer>简洁答案</answer> 结束。实验类问题必须先跑实验再作答。")

    def parse_action(self, action: str):
        """从 LLM 原始输出提取动作。多 tag 时取最后一个（Search-R1 惯例）。"""
        for tag, kind in (("answer", "answer"), ("run_experiment", "exp"),
                          ("search", "search"), ("recall", "recall")):
            ms = re.findall(rf"<{tag}>(.*?)</{tag}>", action, re.DOTALL)
            if ms:
                return (kind, ms[-1].strip()), True
        return ("none", ""), False                                    # 无合法动作 → invalid（verl 侧可罚）

    def conduct_action(self, trajectory_id, action, extra_field):
        parsed, valid = self.parse_action(action)
        env = self.load_env(trajectory_id)
        task = extra_field.get("task", "") if isinstance(extra_field, dict) else ""
        kind, arg = parsed
        obs, done = "", False
        if not valid:
            obs = "未识别到合法动作。可用：<search>q</search> / <run_experiment>name</run_experiment> / <recall></recall> / <answer>a</answer>"
        elif kind == "search":
            hits = RA.kb_search(arg or task, RA.DEFAULT_PROMPT, topk=3)
            obs = "\n".join(f"  {f}「{l}」" for _, f, l in hits) if hits else "无命中（换实义词或先 recall）"
            env.setdefault("chain", []).append("kb_search")
        elif kind == "exp":
            name = arg.lower()
            if name in RA.EXPERIMENTS:
                ok, out = RA.run_experiment(name)                       # 真跑（RLVR 反短路：实验题必须真跑）
                obs, done = str(out), False
                env.setdefault("chain", []).append("run_experiment")
            else:
                obs = f"未知实验 {arg}。可选: {'/'.join(sorted(RA.EXPERIMENTS))}"
        elif kind == "recall":
            obs = RA.recall(RA.classify_state(task), task)
            env.setdefault("chain", []).append("recall")
        elif kind == "answer":
            env["answer"] = arg
            obs, done = arg, True
        turns = env["metadata"]["turns"] + 1
        if turns >= MAX_TURNS and not done:                            # 超步数强制终止（Agents手册 S·Safety：无最大步数=烧钱）
            obs, done = obs + "\n[强制终止] 超过最大步数", True
        self.update_env(trajectory_id, env, parsed, valid, extra_field, obs)
        self.save_env(trajectory_id, env)
        return obs, done, valid

    # ---------------- 外部 RLVR reward（verl reward manager 调用）----------------
    @staticmethod
    def compute_score(task: str, answer: str, chain: list, gold_keywords: list) -> float:
        """Search-R1 式分工：tool 只管轨迹，reward 外部算。
        score = 1.0·关键词命中 + 0.2·证据存在 + (-0.05)·步数塑形；无 answer=0。
        诚实声明：关键词 EM 是 toy 判分；生产用 LLM judge 须先建裁判黄金集（手册08）。"""
        if not answer:
            return 0.0
        hit = sum(1 for k in gold_keywords if k in answer) / max(len(gold_keywords), 1)
        evidence = 1 if any(t in chain for t in ("kb_search", "run_experiment")) else 0
        return round(1.0 * hit + 0.2 * evidence - 0.05 * len(chain), 4)
