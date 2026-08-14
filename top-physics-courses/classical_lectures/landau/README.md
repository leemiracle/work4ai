# Landau-Lifshitz 理论物理教程导读笔记（10 卷全集）

> **为什么有这个目录**：Landau-Lifshitz《理论物理学教程》（*Course of Theoretical Physics*）是 20 世纪理论物理的"圣经"——Lev Landau 和 Evgeny Lifshitz 主编，10 卷覆盖从力学到凝聚态的整个理论物理。它以**极致的简洁、优雅和深刻**著称，每页都是物理智慧的精华。
>
> **定位**：**研究生级参考书**。本科先读卷 1（力学），其余作为参考和进阶。不是通读的教材，是查字典式的圣经——遇到某个主题需要深刻理解时，查 Landau 对应章节。
>
> **核心思想**：Landau 几乎全书从**对称性与最小作用量原理**出发推导一切。力学不是 $F=ma$，是变分原理；量子力学不是矩阵，是 Galilean 不变性 + 叠加原理。

---

## 10 卷索引（按难度梯度） | 卷 | 标题 | 笔记 | 难度 | 配合项目 |
|----|------|------|------|---------|
| 1 | 力学（拉氏视角，本科可读）| [vol1_mechanics.md](vol1_mechanics.md) | ★★★ | L01 进阶 |
| 2 | 经典场论（电磁+相对论）| [vol2_classical_fields.md](vol2_classical_fields.md) | ★★★★ | L07, L10 |
| 3 | 非相对论量子力学 | [vol3_quantum.md](vol3_quantum.md) | ★★★★ | L08, L09 |
| 4 | QED（量子电动力学）| [vol4_qed.md](vol4_qed.md) | ★★★★★ | L11 |
| 5 | 统计物理上 | [vol5_stat_phys1.md](vol5_stat_phys1.md) | ★★★★ | L05 |
| 6 | 流体力学 | [vol6_fluid.md](vol6_fluid.md) | ★★★★ | L20 |
| 7 | 弹性理论 | [vol7_elasticity.md](vol7_elasticity.md) | ★★★ | 选读 |
| 8 | 连续介质电动力学 | [vol8_em_continuous.md](vol8_em_continuous.md) | ★★★★ | L02 进阶 |
| 9 | 统计物理下（凝聚态）| [vol9_stat_phys2.md](vol9_stat_phys2.md) | ★★★★★ | L05, L12 |
| 10 | 物理动力论 | [vol10_kinetics.md](vol10_kinetics.md) | ★★★★ | L05 非平衡 |

---

## 怎么读 Landau（最重要）

> **Landau 不是用来"通读"的，是用来"反复重读"的。**

### 入口卷：先读 Vol 1 力学（~170 页）
- 展示了 Landau 全套方法论的"种子"：**最小作用量 + 对称性 → 一切**
- 读 Vol 1 时不需要高深前置，本科力学够了。它是体验 Landau 风格的最佳入口

### 三条阅读路径

**路径 A：理论物理核心（24-36 月，研究生水平）**
```
Vol 1 力学（入口）
→ Vol 3 量子力学
→ Vol 5 统计物理 Part 1
→ Vol 2 经典场论
→ Vol 4 QED（最难，最后）
```

**路径 B：凝聚态 / 统计方向**
```
Vol 1 → Vol 5 统计 Part 1 → Vol 9 统计 Part 2（凝聚态）
→ Vol 6 流体力学 / Vol 10 物理动力论
```

**路径 C：AI for Physics**
- Landau 是**参考手册**，不是主读。主读用 Tong 系列
- 但 Vol 5（统计）、Vol 9（凝聚态）、Vol 2（场论）的理论框架是理解 AI for Physics 论文的**物理地基**
- 策略：做哪个主题的 AI for Physics 项目，就去 Landau 对应卷查"标准物理是怎么处理的"

---

## Landau 的方法论（为什么他的书这么短）

1. **从对称性出发，不从实验出发**：先写"物理定律必须满足什么对称性"，再推导出具体形式
2. **最小作用量原理是上帝视角**：$S = \int L\,dt$ 取极值 → 一切运动方程。力只是导出概念
3. **极度压缩**：不证明能直觉看出的步骤，不重复。一句顶别人三页。代价：跳一行就跟不上

---

## 与其他讲义的关系

| 主题 | 本科主读 | Landau 重读（研究生）|
|------|---------|-------------------|
| 力学 | Tong *Dynamics & Relativity* | **Vol 1**（重写你的力学直觉）|
| 量子 | Tong QM + 费曼卷 3 | **Vol 3**（最深的非相对论 QM）|
| 统计 | Tong Statistical Physics | **Vol 5**（标准参考）|
| 场论/相对论 | Tong GR | **Vol 2**（场论 + GR 合一）|
| QFT | Tong QFT | **Vol 4**（参考，太硬）|

> **反直觉铁律**：每主题先读 Tong（学会），再用 Landau 重读（深化）。**不要用 Landau 当第一本**——会读废。

---

## 模板

每本笔记遵循 [../TEMPLATE.md](../TEMPLATE.md) 的 §0-§9 结构。

---

**完成日期**：2026-08-13
**核实**：Landau-Lifshitz 10 卷标准编号与作者（Vol 1-3 Landau & Lifshitz；Vol 4 Berestetskii/Lifshitz/Pitaevskii；Vol 9-10 Lifshitz & Pitaevskii）
