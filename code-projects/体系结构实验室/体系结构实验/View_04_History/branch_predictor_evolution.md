# 分支预测器代际演进史（1980s → 2025）

> **首席科学家视角**配套材料。每个现代 CPU 的分支预测器都是 40 年研究的集大成。
> 一条时间线看完所有关键 idea。

---

## 0. 一图概览

```
1981 ─── 1-bit predictor (Smith)               准确率 ~85%
  │
  1991 ─── 2-bit saturating (Smith)            ~90%
  │
  1992 ─── Two-Level Adaptive (Yeh & Patt)     ~93%
  │       (global + local history)
  │
  1993 ─── gshare (McFarling)                  ~94%
  │
  1995 ─── Tournament (Alpha 21264, DEC)       ~95%
  │       (全局 vs 局部自动选择)
  │
  1996 ─── Perceptron (Jiménez, 2001 推广)     ~96%
  │       (用线性分类器替代 2-bit 表)
  │
  2006 ─── TAGE (Seznec)                       ~97%
  │       (几何级数历史长度)
  │
  2014 ─── TAGE-SC-L (Seznec, CBP4 冠军)       ~97.5%
  │       (TAGE + Statistical Corrector + Loop)
  │
  2020s ── 神经网络预测器 (Gliders, etc.)      ~98%+
  │       (深度学习 + 推理硬件)
```

---

## 1. 1-bit Predictor（1981）

- **思想**：每个分支记住上次方向，下次按上次预测
- **结构**：1 bit/分支，PC 索引小表（256 entry）
- **失败模式**：嵌套循环的最后一次（`for(i=0;i<n;i++)` 出口）每次都被猜错
- **经典案例**：`for(i=0;i<10;i++)` 共 9 次 taken + 1 次 not-taken → 1-bit 准确率仅 80%

## 2. 2-bit Saturating（1991）

- **思想**：状态机 SN→WN→WT→ST，要连续 2 次失败才换方向
- **结构**：2 bit/分支
- **改进**：嵌套循环准确率 90%+（只有第一次出口失败）
- **关键**：Hysteresis（迟滞）让预测更稳

## 3. Two-Level Adaptive（Yeh & Patt 1992）

- **核心洞察**：**全局历史**包含有用信息（前几个分支影响当前分支）
- **结构**：
  - Level 1：`BHR`（Branch History Register）—— 12 位全局历史
  - Level 2：`PHT`（Pattern History Table）—— 用 BHR 索引 2-bit 表
- **效果**：循环嵌套、相关性强的代码 → 95%+

## 4. gshare（McFarling 1993）

- **思想**：把 PC XOR 全局历史作为索引（让不同分支即使 BHR 相同也能区分）
- **优点**：超简单，效果接近 Tournament
- **遗留**：Linux `git blame` 默认用 gshare-like 算法

## 5. Tournament（Alpha 21264, 1995）

- **思想**：**3 个预测器**并行跑：
  - 全局预测器（gshare 风格）
  - 局部预测器（per-PC history）
  - 选择器（metapredictor）决定本轮用哪个
- **效果**：自动适应不同代码风格
- **论文**：Kessler 1999（见 [Capstone-A](../Capstone/alpha_21264_study/notes.md)）

## 6. Perceptron（Jiménez & Lin 2001）

- **思想**：把分支预测当**线性分类问题**
- 每个 PC 有一个权重向量，`sign(weight · history) = taken?`
- **效果**：复杂相关分支 → 96-97%
- **缺点**：硬件实现复杂（乘加），时序压力大

## 7. TAGE（Seznec, 2006）

- **TAGE = TAgged GEometric**
- **思想**：多个不同历史长度的 predictor（几何级数：4, 8, 16, 32, 64, 128）
- 用 tag 匹配，最长匹配的 predictor 优先
- **效果**：工业级最佳，CBP（分支预测竞赛）多年冠军
- **应用**：Intel 自 2010s 部分采用 TAGE 思想；AMD Zen 系列类似

## 8. TAGE-SC-L（Seznec, 2014）

- **结构**：TAGE 主体 + Statistical Corrector (SC) + Loop Predictor (L)
- SC：对 TAGE 没把握的 case 用 perceptron 修正
- L：专门处理 loop（次数固定的循环）
- **当前主流**：Intel Golden Cove / AMD Zen 4 / Apple M1 都用 TAGE-SC-L 变种

## 9. 神经网络预测器（2020s）

- **思想**：用小型神经网络替代 perceptron（更深、更非线性）
- **代表**：Gliders（Dan Jiménez 2017）
- **挑战**：硬件推理延迟、训练复杂
- **现状**：研究阶段，未商用

---

## 10. 各代实际准确率（CBP 历年数据）

| 预测器 | 准确率 | 年代 |
|-------|------:|----:|
| 1-bit | ~85% | 1981 |
| 2-bit | ~89% | 1991 |
| gshare | ~93% | 1993 |
| Tournament | ~95% | 1995 |
| Perceptron | ~96% | 2001 |
| TAGE | ~96.5% | 2006 |
| TAGE-SC-L | ~97.5% | 2014 |
| 神经网络（仿真）| ~98.5% | 2020 |

---

## 11. 飞腾 D3000M 的位置

飞腾官方未公开其分支预测器细节，但基于：
- ARMv8.4-A 架构 + DSU 配套
- [Lab02/branch_predict](../Lab02_流水线与ILP/) 实测单调分支 100% 命中
- 与同时代 ARM Cortex-A76/A78 性能相当

**推测**：飞腾 FTC862 用 **TAGE-SC-L 变种**（与 Apple / AMD / Intel 同代）。

---

## 12. 参考文献（按年代）

1. Smith, "A Study of Branch Prediction Strategies" (MICRO 1981)
2. Yeh & Patt, "Two-Level Adaptive Branch Prediction" (MICRO 1991)
3. McFarling, "Combining Branch Predictors" (DEC WRL 1993)
4. Jiménez & Lin, "Dynamic Branch Prediction with Perceptrons" (HPCA 2001)
5. Seznec, "Analysis of the O-Geometric History Length Branch Predictor" (ISCA 2005)
6. Seznec, "TAGE-SC-L Branch Predictor" (CBP 2014)
7. Dan Jiménez, "Branch Prediction with Neural Networks" (2022 综述)
8. CBP (Championship Branch Prediction) 历年：[jilp.org/cbp2016](http://www.jilp.org/cbp2016)

📌 **下一步**：[cache_architecture_history.md](./cache_architecture_history.md) 看 Cache 的代际演进。
