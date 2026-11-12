# -*- coding: utf-8 -*-
"""
垃圾桶模型：组织决策四流仿真（走廊1：决策仿真）
对应章：讲透行政学/04-行政学转代码.md（00/03 章引用）

Cohen-March-Olsen (1972) 能量框架的简化复现：选择机会/问题/方案/参与者
四流在时序中耦合；每个选择机会的"可用能量"（参与者数）与"问题负载"
（附着问题的能量需求之和）比较，产生三种决策风格：
  解决 resolution：能量≥负载 → 附着问题真被处理
  飞行 flight：能量不足时问题逃逸他处，选择机会随后"空转"成事
  疏忽 oversight：无问题附着时也照常拍板（议程惯性）

四组断言（固定种子）：
  [1] 能量充裕配置的"解决"数与问题解决率显著高于能量匮乏配置
      （CMO 原论文核心结论：负载决定决策风格）
  [2] 能量匮乏配置的问题"飞行"事件更多（问题四处逃逸，组织忙而不决）
  [3] 参与者流动（每期重派）比冻结编制解决更多问题（能量再分配效应）
  [4] 固定种子完全可复现
口径：参数为教学化简化设定（作风格演示，非原论文参数复刻）；
随机性全部来自 random.Random(seed)。
"""
import random


def run_gc(seed, n_participants, n_problems, n_choices=4, periods=300,
           flight_prob=0.5, fluid=True):
    """返回统计字典与期末未解决问题数。"""
    rng = random.Random(seed)
    problems = [{"e": rng.uniform(1.0, 4.0), "c": rng.randrange(n_choices)}
                for _ in range(n_problems)]
    choice_req = [rng.uniform(1.0, 3.0) for _ in range(n_choices)]
    members = [rng.randrange(n_choices) for _ in range(n_participants)]
    stats = {"resolution": 0, "oversight": 0, "flight_decision": 0,
             "flight_events": 0, "resolved_problems": 0}
    fled_this_period = [False] * n_choices

    for _ in range(periods):
        if fluid:  # 参与者每期重新流入可及的选择机会
            members = [rng.randrange(n_choices) for _ in range(n_participants)]
        energy = [0.0] * n_choices
        for c in members:
            energy[c] += 1.0
        load = [0.0] * n_choices
        for p in problems:
            load[p["c"]] += p["e"]

        # 决策阶段
        for ci in range(n_choices):
            attached = [p for p in problems if p["c"] == ci]
            if energy[ci] >= load[ci] + choice_req[ci]:
                if attached:
                    stats["resolution" if not fled_this_period[ci]
                          else "flight_decision"] += 1
                    stats["resolved_problems"] += len(attached)
                    problems = [p for p in problems if p["c"] != ci]
                else:
                    stats["oversight"] += 1
        # 飞行阶段：能量不足的选择上，问题按概率逃逸
        fled_this_period = [False] * n_choices
        energy = [0.0] * n_choices
        for c in members:
            energy[c] += 1.0
        load = [0.0] * n_choices
        for p in problems:
            load[p["c"]] += p["e"]
        for ci in range(n_choices):
            if energy[ci] < load[ci] + choice_req[ci]:
                for p in problems:
                    if p["c"] == ci and rng.random() < flight_prob:
                        p["c"] = rng.randrange(n_choices)
                        stats["flight_events"] += 1
                        fled_this_period[ci] = True
    stats["open_problems"] = len(problems)
    return stats


def main():
    hi = run_gc(20260907, n_participants=30, n_problems=8)   # 能量充裕
    lo = run_gc(20260907, n_participants=5, n_problems=8)    # 能量匮乏
    # [1] 解决数与解决率：充裕 >> 匮乏
    assert hi["resolved_problems"] == 8 and lo["resolved_problems"] < 8, (hi, lo)
    assert hi["resolution"] > lo["resolution"]
    print(f"[1] 实际解决的问题：能量充裕 {hi['resolved_problems']}/8 全清"
          f"（{hi['resolution']} 次'解决'事件）vs 匮乏 {lo['resolved_problems']}/8"
          f"（{lo['resolution']} 次）——负载决定决策风格（CMO 核心）")

    # [2] 飞行事件：匮乏 >> 充裕（问题四处逃逸）
    assert lo["flight_events"] > 10 * hi["flight_events"], (hi, lo)
    print(f"[2] 问题飞行事件：匮乏 {lo['flight_events']} 次 >> 充裕 "
          f"{hi['flight_events']} 次——能量不足的组织里问题永不落停"
          "（'忙而不决'的数学像）")

    # [3] 流动 vs 冻结编制：流动解决更多
    fluid = run_gc(7, n_participants=10, n_problems=8, fluid=True)
    frozen = run_gc(7, n_participants=10, n_problems=8, fluid=False)
    assert fluid["resolved_problems"] > frozen["resolved_problems"], (fluid, frozen)
    print(f"[3] 同样 10 名参与者：每期流动解决 {fluid['resolved_problems']} 个问题"
          f" > 冻结编制 {frozen['resolved_problems']} 个——能量再分配本身"
          "就是组织生产力（轮岗/抽调的模型依据）")

    # [4] 可复现性
    again = run_gc(20260907, n_participants=30, n_problems=8)
    assert again == hi
    print("[4] 固定种子重复运行：统计完全一致 ✓（仿真=可审计的实验）")

    total_hi = hi["resolution"] + hi["oversight"] + hi["flight_decision"]
    total_lo = lo["resolution"] + lo["oversight"] + lo["flight_decision"]
    print(f"    附注：总拍板次数 充裕 {total_hi} vs 匮乏 {total_lo}——匮乏组织"
          "拍板更少且多为'飞行/疏忽'风格；充裕组织清空问题后大量决策"
          "变成无议题的疏忽拍板（议程惯性）")
    print("\n全部断言通过 ✓（垃圾桶=组织决策的风洞：四流耦合可仿真、"
          "风格规律可复现）")


if __name__ == "__main__":
    main()
