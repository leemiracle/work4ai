# 讲透分析进阶 · 从 Fourier 到泛函（基于 Stein-Shakarchi 4 卷）

> 用「直觉 → 数学 → 实验」讲透 Elias Stein & Rami Shakarchi 的 Princeton Lectures in Analysis 4 卷——公认的现代分析最优讲义。

---

## 〇、为什么 Stein-Shakarchi

### 0.1 4 卷结构

| 卷 | 主题 | 核心内容 |
|---|------|---------|
| I | **Fourier Analysis** | Fourier 级数 / 积分 / 分布 |
| II | **Complex Analysis** | 全纯函数 / 留数 / 共形映射 |
| III | **Real Analysis** | 测度论 / Lebesgue 积分 / $L^p$ 空间 |
| IV | **Functional Analysis** | Banach / Hilbert / 谱 |

### 0.2 与讲透实分析的关系

[`../讲透实分析/`](../讲透实分析/) 是本科入门（Tao Analysis I，ε-δ 极限）。
本系列是**研究生级**（Stein-Shakarchi，测度 / 复分析 / 泛函）。

### 0.3 你的应用

- **ML 理论**：$L^p$ 空间 + RKHS（卷 IV）
- **信号处理**：Fourier 分析（卷 I）
- **数论**：复分析（卷 II）+ 解析数论
- **概率论**：测度论（卷 III）是严格概率的基础

---

## 一、章节

| # | 文件 | 主题 | S-S 卷.章 | 状态 |
|---|------|------|---------|------|
| 00 | [`00-分析进阶是什么.md`](00-分析进阶是什么.md) | 4 卷总览 + 路径 | — | ✅ |
| 01 | `01-Fourier级数.md` | 收敛 / Parseval / 分布 | I.1-3 | 📝 |
| 02 | `02-Fourier积分.md` | Fourier 变换 / 反演 | I.5-6 | 📝 |
| 03 | `03-全纯函数.md` | Cauchy 定理 / 公式 | II.1-3 | 📝 |
| 04 | `04-留数与共形.md` | 留数定理 / 共形映射 | II.4-8 | 📝 |
| 05 | `05-Lebesgue测度.md` | 测度构造 / 可测 | III.1-2 | 📝 |
| 06 | `06-Lebesgue积分.md` | 收敛定理 / $L^p$ | III.3-6 | 📝 |
| 07 | `07-Banach空间.md` | 完备化 / Hahn-Banach | IV.1-3 | 📝 |
| 08 | `08-Hilbert空间.md` | 内积 / 正交 / 谱 | IV.4-7 | 📝 |

---

## 二、前置

- 实分析（见 [`../讲透实分析/`](../讲透实分析/)，Tao Analysis I 级别）
- 复数基础
- Python（实验用）

---

## 三、与 work4ai 联动

- [`../讲透实分析/`](../讲透实分析/) — 本系列的前置
- [`../讲透高维概率/`](../讲透高维概率/) — 用到 $L^p$ 空间
- [`../讲透信息论/`](../讲透信息论/) — Fourier 与信息论交叉
- [`../top-math-courses/TEXTBOOK_LIBRARY.md`](../top-math-courses/TEXTBOOK_LIBRARY.md) §一

---

📌 **下一步**：读 [`00-分析进阶是什么.md`](00-分析进阶是什么.md)。
