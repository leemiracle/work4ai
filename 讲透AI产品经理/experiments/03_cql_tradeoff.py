#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
成本-质量-延迟三角 + 单位经济学模拟器
====================================
03.4 门槛经济学 + 04.1 三角座位 + 07.1 单位毛利的可运行版。

场景：客服 agent 的模型档位选择
  - 三档配置（小模型/大模型/分层路由），各有质量、单次成本、延迟
  - 质量误差有真实成本：漏错善后成本 C_err；低置信转人工成本 C_human
  - 扫描"漏错成本"参数，看最优配置如何切换——门槛经济学：同一技术栈，
    不同错误成本结构下最优解完全不同（消费客服 vs 法律/医疗级产品）

运行：python3 03_cql_tradeoff.py
"""

# ---------------- 三档配置（数值为教学示例，量级对齐 2026 行业常识） ----------------
CONFIGS = {
    #      质量(自动答对率)  单次推理成本   P95延迟   低置信率(触发转人工)
    "小模型 8B":   dict(acc=0.75, cost=0.01, p95=1.2, unsure=0.10),
    "大模型 72B":  dict(acc=0.91, cost=0.15, p95=4.5, unsure=0.08),
    "分层路由":    dict(acc=0.88, cost=0.05, p95=2.8, unsure=0.12),
    # 路由：80% 流量走小模型（答对率打折）、20% 升大模型——质量略低于纯大模型，
    # 成本远低；unsure=自报低置信、触发 04.3 L4 降级转人工的比例
}

PRICE = 1.00    # 每次会话计价（按量定价）
C_HUMAN = 1.0   # 转人工一次的完全成本
C_ERR_BASE = 1.0  # 消费客服基线：错答一次的善后成本（道歉+小额补偿）

def unit_economics(cfg: dict, c_err: float, c_human: float = C_HUMAN) -> dict:
    """单会话经济账：
    成本 = 推理 + 低置信转人工 + 漏错善后
    简化假设：unsure 全部被降级设计拦住（不出错，只花钱）；
    剩余错误 = (1 - acc - unsure 全拦截后残余) 以 (1-acc) 计，全部漏到用户。
    """
    leaked = (1.0 - cfg["acc"])          # 漏到用户的错误率
    cost = cfg["cost"] + cfg["unsure"] * c_human + leaked * c_err
    return dict(cost=cost, margin=PRICE - cost,
                margin_pct=(PRICE - cost) / PRICE)

def main():
    print(f"计价：{PRICE:.2f} 元/会话；转人工成本 {C_HUMAN:.1f} 元\n")

    # Part 1: 基准——消费客服（漏错成本低）
    print("== Part 1  基准：消费客服（漏错成本 1 元）==")
    print(f"{'配置':<12}{'质量':>7}{'单位成本':>9}{'毛利率':>8}")
    for name, cfg in CONFIGS.items():
        ue = unit_economics(cfg, C_ERR_BASE)
        print(f"{name:<12}{cfg['acc']:>7.0%}{ue['cost']:>9.2f}{ue['margin_pct']:>8.0%}")

    # Part 2: 门槛经济学——扫描漏错成本，最优档位切换
    print("\n== Part 2  门槛经济学：错误成本扫描（最优配置切换点）==")
    print(f"{'漏错成本':>8} | " + " | ".join(f"{n}" for n in CONFIGS) + " | 最优")
    for c_err in [0.3, 0.5, 1, 2, 3, 5, 12, 30, 100]:
        margins = {n: unit_economics(c, c_err)["margin"] for n, c in CONFIGS.items()}
        winner = max(margins, key=margins.get)
        row = " | ".join(f"{margins[n]:>7.2f}" for n in CONFIGS)
        print(f"{c_err:>8} | {row} | {winner}")

    # Part 3: 延迟的隐性代价（三角第三维）
    print("\n== Part 3  延迟维度（三角不可兼得提醒）==")
    for name, cfg in CONFIGS.items():
        verdict = "✓ 用户可等" if cfg["p95"] <= 3.0 else "✗ 超出会话容忍(>3s)"
        print(f"  {name:<12} P95={cfg['p95']:>4.1f}s  {verdict}")

    print("""
结论：
1. 门槛经济学实证：漏错成本 <=0.3 元（批量/轻损失场景）小模型赢；
   0.5~1 元（消费客服主流场景）分层路由赢；>=2 元（专业级场景）大模型赢。
   同一技术栈，最优档位由错误成本结构决定——这就是 03 章说的
   "PM 独有的决策权"：技术团队给不了这个答案。
2. 三角不可兼得的完整形态：漏错成本 >=3 元时大模型在成本-质量二维最优，
   但 P95=4.5s 超出会话容忍——真正的产品决策变成三选一：
   接受延迟 / 提价补偿（换PRICE）/ 为路由档追加质量投资。
   这正是法律产品（Harvey 类）PM 面对的现实取舍。
3. 单位毛利是三角选择的直接结果：换档位=换毛利结构（07.1）；
   转人工（HITL）不是成本负担，是用 1 元买"错误不漏到用户"的保险（04.3 L4）。""")

if __name__ == "__main__":
    main()
