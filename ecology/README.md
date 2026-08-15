# 生态学完全指南（存档）

> 由 ai-mentor 生成的六篇深度讲解 + 5 个已验证的数值实验。
> 覆盖：本质/历史 → 个体/种群/群落/生态系统 → 进化/行为/景观 → 保护/全球变化/临界点 → 论文精讲/数学推导 → eDNA/伦理/总结。
> 所有数学模型与算法均嵌入对应章节；实验代码可复现。

## 目录

| 文件 | 内容 |
|------|------|
| [01-essence-history-organism.md](01-essence-history-organism.md) | 本质 · 历史 · 组织层级 · 个体/生理生态 · 生活史对策 |
| [02-population-community.md](02-population-community.md) | 种群生态学全模型（逻辑斯谛/矩阵/LV/SIR）· 群落生态学（多样性/岛屿/食物网） |
| [03-ecosystem-evolution-behavior-landscape.md](03-ecosystem-evolution-behavior-landscape.md) | 生态系统能流/物质循环 · May 稳定性辩论 · 进化/行为生态 · 景观生态 |
| [04-conservation-global-change-frontiers.md](04-conservation-global-change-frontiers.md) | 保护生物学 · 全球变化 · 临界点/EWS · 地球边界 · 前沿 · 多视角批判 |
| [05-papers-derivations.md](05-papers-derivations.md) | 里程碑论文精讲（May/Scheffer/Hamilton/Hubbell）· 三个数学推导（May-Wigner/Hamilton 规则/边际值定理） |
| [06-edna-tipping-ethics-summary.md](06-edna-tipping-ethics-summary.md) | eDNA 流水线 · 9 大地球临界要素 · 生态伦理深辩 · 补充主题 · 全局总结 |

## 数值实验（experiments/，全部验证通过）

| 脚本 | 验证内容 | 关键结果 | 图 |
|------|---------|---------|-----|
| `chaos_logistic.py` | 离散逻辑斯谛混沌分岔（May 1976） | r=2.8→1点稳态, 3.2→2周期, 3.5→4周期, 3.83→周期3窗口, 3.9→混沌 | fig1 |
| `leslie_matrix.py` | Leslie 矩阵年龄结构模型 | λ1=1.527；稳定年龄分布；弹性分析（幼体存活弹性最大 0.304） | fig2 |
| `lotka_volterra.py` | 经典 LV + Rosenzweig-MacArthur | 中性中心 N\*=4,P\*=10；1/4 周期相位差；富营养悖论（高K→极限环） | fig3 |
| `ews_tipping.py` | 临界点早期预警信号 | Var τ=0.24(p=1.6e-5)↑, AR(1) τ=0.93(p=9.1e-63)↑；恢复速率慢 10× | fig4, fig4b |
| `may_stability.py` | May(1972) 稳定性判据数值验证 | σ√(SC)=0.9→1%失稳, 1.0→34%, 1.1→74%, 1.5→100%（sigmoid 跳变） | fig5 |

## 复现命令

```bash
cd ecology/experiments
python3 chaos_logistic.py      # 依赖: numpy, scipy, matplotlib
python3 leslie_matrix.py
python3 lotka_volterra.py
python3 ews_tipping.py
python3 may_stability.py
```

## 三句话记住整个生态学

1. **层级 + 涌现 + 尺度**——错尺度 = 错结论。个体 ≠ 种群 ≠ 群落 ≠ 生态系统。
2. **复杂性是双刃剑**：May 证明随机复杂 → 失稳；结构化复杂（弱连/嵌套/模块）→ 稳定 + 保险。多样性让"总量"稳、让"种群"波动。
3. **人类世的科学**：多个地球临界点逼近；critical slowing down 早期预警（Var↑、AR1↑）是生态学给复杂系统科学的方法论礼物；地球边界 9 项已越 6 项。

---
*生成日期：2026-08-14 · 环境：Python 3.10 + numpy 2.2 + scipy 1.15 + matplotlib 3.10*
