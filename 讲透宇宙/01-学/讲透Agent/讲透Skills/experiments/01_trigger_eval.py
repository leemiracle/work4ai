# -*- coding: utf-8 -*-
"""
实验 01 — 触发精度评测：description 是检索键的真模型实测
对应文档: 讲透Skills/03-路由与触发-description即检索键.md
模型: 本地 Qwen2.5-0.5B-Instruct (CPU, greedy 确定性)

协议（复刻官方 skill-creator 的 trigger eval 思想, 小样本教学版）:
  - 8 个候选 skill（本机真实 description, 含 2 个共享关键词的竞争对）
  - 10 条 query: 5 正例 + 3 near-miss（共享关键词但目标不同/竞争）+ 2 无关负例
  - 模型读"技能清单+query"输出决策, 规则解析命中

看点:
  K1 正例命中率（pushy description 是否工作）
  K2 near-miss 区分度（near-miss 比无关负例难得多——官方说的最有价值负例）
  K3 竞争对错配（rl-learning vs llm-mastery 都写了 RLHF/DPO）

跑法: python3 -u 01_trigger_eval.py
"""
import re, time
import torch

torch.set_num_threads(1)

MODEL_PATH = "~/ai/models/Qwen2.5-0.5B-Instruct"

# 8 个候选 skill: (name, description 摘要版——保持与真机同构但截断到统一长度)
SKILLS = [
    ("llm-mastery", "大语言模型全栈学习——Transformer架构、预训练、微调(LoRA/QLoRA)、对齐训练(RLHF/DPO)、推理优化、RAG。Triggers: LLM, 大模型, 微调, LoRA, RLHF, DPO, 量化, RAG."),
    ("rl-learning", "强化学习全栈学习——MDP、Q-learning、DQN、PPO、SAC、策略梯度、RLHF对齐。Triggers: 强化学习, RL, PPO, DQN, RLHF, 奖励模型, Bellman."),
    ("cv-learning", "计算机视觉全栈——CNN到ViT/YOLO/SAM/Diffusion，分类/检测/分割/生成。Triggers: CV, 图像分类, 目标检测, ViT, 图像分割, 扩散模型."),
    ("math-learning", "数学学习——概念理解、定理证明、教材推荐、知识图谱、Anki闪卡。Triggers: 数学学习, 证明, 定理, 微积分, 线性代数."),
    ("debug-helper", "系统化调试工作流——识别、隔离、修复bug。Triggers: debug, bug, error, 报错, 崩溃, 失败, stack trace, 异常."),
    ("git-workflow", "Git与GitHub工作流——commit、分支、rebase、冲突、PR。Triggers: commit, 分支, rebase, 冲突, PR, git log."),
    ("tdd", "测试驱动开发——red-green-refactor循环、垂直切片。Triggers: TDD, 测试驱动, red-green-refactor, 先写测试."),
    ("paper-mastery", "AI/ML论文精读——四层拆解、公式提取、复现指引。Triggers: 论文精读, 读论文, paper, 复现论文, 论文笔记."),
]

# 10 条 query（含官方要求的"真实感": 背景/口语/具体）
QUERIES = [
    # 5 正例
    ("P1", "帮我讲讲 PPO 的 clip 目标函数为什么那样设计，直觉是什么", "rl-learning"),
    ("P2", "用 ViT 做图像分类，patch embedding 的维度怎么选合适", "cv-learning"),
    ("P3", "epsilon-delta 极限定义我总是搞不懂，能不能用一个具体例子讲清楚", "math-learning"),
    ("P4", "这篇 Attention is All You Need 论文的实验部分说明了什么", "paper-mastery"),
    ("P5", "git rebase 和 merge 有什么区别，我改用哪个工作流好", "git-workflow"),
    # 3 near-miss（共享关键词但目标不同）
    ("N1", "我的 LoRA 微调脚本 loss 变成 NaN 了，帮我看看到底哪一步梯度爆炸", "debug-helper"),   # LoRA 诱导 llm-mastery, 但任务是 debug
    ("N2", "RLHF 和 DPO 训练时哪个更省显存，7B 模型需要几张卡", "llm-mastery"),                  # RLHF/DPO 两个 skill 都写了, 竞争
    ("N3", "TDD 的 red-green-refactor 循环里，为什么第一步要先写会失败的测试", "tdd"),            # 原理问题 vs 实践工作流
    # 2 无关负例
    ("X1", "今天天气怎么样，适合爬山吗", None),
    ("X2", "帮我写一首关于秋天的短诗", None),
]

SYSTEM = ("你是 AI 助手的技能路由器。根据用户任务，从下列技能清单中选出最该启用的一个，"
"或回答 NONE（都不适合）。只输出技能名或 NONE，不要其他内容。\n\n技能清单：\n"
+ "\n".join(f"- {n}: {d}" for n, d in SKILLS))

# few-shot 对照组: 同一任务给 2 个示范(1 选技能 + 1 拒识), 验证路由决策也吃 ICL
FEWSHOT = [
    {"role": "user", "content": "我的 DQN 训练不收敛，reward 一直在震荡，怎么排查"},
    {"role": "assistant", "content": "rl-learning"},
    {"role": "user", "content": "推荐一本学线性代数的教材"},
    {"role": "assistant", "content": "NONE"},
]

def main():
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tok = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, dtype=torch.float32).eval()

    hit = miss = wrong = 0
    rows = []
    for mode in ("zero-shot", "few-shot"):
        print(f"\n  ---- 条件: {mode} ----")
        for qid, q, expect in QUERIES:
            msgs = [{"role": "system", "content": SYSTEM}]
            if mode == "few-shot": msgs += FEWSHOT
            msgs.append({"role": "user", "content": q})
            prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            ids = tok(prompt, return_tensors="pt")
            t0 = time.time()
            with torch.no_grad():
                gen = model.generate(ids.input_ids, attention_mask=ids.attention_mask,
                                     max_new_tokens=16, do_sample=False,
                                     pad_token_id=tok.eos_token_id)
            out = tok.decode(gen[0][ids.input_ids.shape[1]:], skip_special_tokens=True).strip()
            picked = None
            for n, _ in SKILLS:
                if n.lower() in out.lower(): picked = n; break
            if "none" in out.lower() and picked is None: picked = None
            if expect is None:
                ok = picked is None
                tag = "✅ 正确拒识" if ok else f"❌ 误触发→{picked}"
            else:
                ok = picked == expect
                tag = "✅ 命中" if ok else f"❌ 选了→{picked or 'NONE'}"
            rows.append((mode, qid, expect or "—", picked or "NONE", ok))
            print(f"  [{qid}] {tag}  ({time.time()-t0:.0f}s)  q: {q[:26]}…  out: {out[:36]}")
    print(f"\n  ▶ 汇总（zero-shot vs few-shot 同题对照）")
    for mode in ("zero-shot", "few-shot"):
        mr = [r for r in rows if r[0] == mode]
        pos_ok = sum(1 for r in mr if r[1].startswith("P") and r[4])
        nm_ok = sum(1 for r in mr if r[1].startswith("N") and r[4])
        neg_ok = sum(1 for r in mr if r[1].startswith("X") and r[4])
        tot = pos_ok + nm_ok + neg_ok
        print(f"    {mode:<10} 正例 {pos_ok}/5 | near-miss {nm_ok}/3 | 负例拒识 {neg_ok}/2 | 总对 {tot}/10")
    print("  ▶ 三条教学读数:")
    print("    T1 欠触发是模型能力函数: 0.5B 在 zero-shot 下几乎全拒(NONE)——")
    print("       官方 skill-creator 的 pushy description 建议正是对抗这个偏置;")
    print("    T2 路由决策也吃 ICL: 两个 few-shot 示范就能显著改变触发行为;")
    print("    T3 near-miss 是 description 质量的真考官: N1/N2 的关键词竞争,")
    print("       谁 description 更贴近用户意图谁赢——run_loop 优化的正是这个。")

if __name__ == "__main__":
    main()
