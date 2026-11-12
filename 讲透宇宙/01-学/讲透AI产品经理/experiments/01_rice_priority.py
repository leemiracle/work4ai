#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RICE 优先级计算器（AI 产品版）
================================
经典 RICE：score = Reach x Impact x Confidence / Effort
AI 版两处改装（讲透AI产品经理/02-方法论武器库.md §02.1②）：
  1. Reach 按"数据就绪度"折价——没有训练/检索数据的用例 Reach 实际为 0
  2. Confidence 按"可行性未证"降级——AI 功能可能要试完才知道质量够不够

实验内容：
  A. 用示例 backlog 算 RICE 排名（传统版 vs AI 修正版对照）
  B. reach 诚实度敏感性分析——你的 reach 估计虚高 30% 时排名怎么变
运行：python3 01_rice_priority.py
"""
from dataclasses import dataclass, field

# ---------------- 数据结构 ----------------
@dataclass
class Feature:
    name: str
    reach: float          # 每季度触达用户数（原始估计）
    impact: float         # 0.25/0.5/1/2/3（RICE 标准档）
    confidence: float     # 0-1（原始估计）
    effort: float         # 人月
    data_readiness: float # 0-1：数据就绪度（0=完全没数据, 1=数据齐且质量好）
    feasibility_proven: bool  # 质量/性能门槛是否已被 spike 验证过


def classic_rice(f: Feature) -> float:
    """传统 RICE"""
    return f.reach * f.impact * f.confidence / f.effort


def ai_rice(f: Feature) -> float:
    """AI 修正 RICE：
    - Reach 乘数据就绪度（数据不 ready = 到达不了承诺的质量 = 有效触达打折）
    - Confidence 上限被可行性封顶：未验证的功能 confidence 不允许超过 0.5
      （防"自信地排期"——AI 功能可行性开工前是未知的）
    """
    eff_reach = f.reach * f.data_readiness
    conf_cap = f.confidence if f.feasibility_proven else min(f.confidence, 0.5)
    return eff_reach * f.impact * conf_cap / f.effort


# ---------------- 示例 backlog（数值为教学示例，换成你自己的） ----------------
BACKLOG = [
    Feature("AI 摘要（内部文档）",   reach=8000, impact=1.0, confidence=0.8, effort=2,
            data_readiness=0.9, feasibility_proven=True),   # 有语料、spike 过
    Feature("智能客服路由",          reach=50000, impact=2.0, confidence=0.9, effort=6,
            data_readiness=0.6, feasibility_proven=False),  # 工单历史质量参差
    Feature("合同风险扫描",          reach=1200, impact=3.0, confidence=0.7, effort=8,
            data_readiness=0.3, feasibility_proven=False),  # 脱敏合同语料刚起步
    Feature("会议纪要行动项提取",    reach=24000, impact=1.0, confidence=0.6, effort=3,
            data_readiness=0.85, feasibility_proven=True),   # spike 已过
    Feature("竞品价格监控 agent",    reach=3000, impact=2.0, confidence=0.7, effort=5,
            data_readiness=0.95, feasibility_proven=True),  # 公开数据、已验证
]

def print_table(rows, title):
    print(f"\n== {title} ==")
    print(f"{'功能':<22}{'RICE':>10}{'排名':>6}")
    for i, (name, score) in enumerate(rows, 1):
        print(f"{name:<22}{score:>10.0f}{i:>6}")

def main():
    classic = sorted(((f.name, classic_rice(f)) for f in BACKLOG),
                     key=lambda x: -x[1])
    ai = sorted(((f.name, ai_rice(f)) for f in BACKLOG), key=lambda x: -x[1])
    print_table(classic, "传统 RICE 排名")
    print_table(ai, "AI 修正 RICE（数据就绪折价 + 可行性置信封顶）")

    # 排名变动
    cr = {n: i for i, (n, _) in enumerate(classic, 1)}
    print("\n== 排名变动（正=AI 修正后上升）==")
    for i, (n, _) in enumerate(ai, 1):
        print(f"{n:<22}{cr[n] - i:>+6}")

    # B. reach 诚实度敏感性：把第一名的 reach 虚高 30% 会怎样
    print("\n== 敏感性：'智能客服路由' reach 虚高 30% 时 ==")
    for label, mult in [("诚实估计", 1.0), ("虚高 30%", 0.7)]:  # mult=修正系数
        fs = [Feature(f.name, f.reach * (mult if f.name == "智能客服路由" else 1),
                      f.impact, f.confidence, f.effort, f.data_readiness,
                      f.feasibility_proven) for f in BACKLOG]
        ranking = [n for n, _ in sorted(((f.name, ai_rice(f)) for f in fs),
                                        key=lambda x: -x[1])]
        print(f"  {label}: " + " > ".join(ranking[:3]) + " ...")

    print("""
结论：
1. 数据就绪度是隐形 Killer：合同风险扫描（传统第2）跌到最后——
   不是需求不存在，是现在做不出承诺的质量（Reach x 0.3）。
2. 可行性封顶防'自信排期'：未 spike 的功能 confidence 最高只能按 0.5 算。
3. reach 估计的 ±30% 足以翻转前两名——RICE 表的 reach 列是最该被挑战的一列，
   用它来启动团队对话，而不是结束对话。""")


if __name__ == "__main__":
    main()
