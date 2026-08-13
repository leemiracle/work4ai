# 讲透Artin抽代 · 群/环/域/Galois（基于 Artin Algebra 2e）

> 用「直觉 → 数学 → Python → Lean」讲透 Michael Artin《Algebra》2e（MIT 18.701/702 教材，代数方向全球标准）。
>
> Artin 是 Emmy Noether 徒孙——抽象代数最现代、最几何的入门。

---

## 〇、为什么 Artin

### Artin vs Dummit-Foote vs Lang

| 书 | 风格 | 适合 |
|---|------|------|
| **Artin** | 几何直觉 + 现代风格 | 自学首选 |
| Dummit-Foote | 全 reference | 查 |
| Lang | 冷酷完备 | PhD 必备 |

### 与讲透群论的关系

[`../讲透群论/`](../讲透群论/) 基于 Milne（更紧凑）。本系列基于 Artin（更几何 + 更广，含环/域/Galois）。

---

## 一、章节（基于 Artin 2e）

| # | 文件 | 主题 | Artin 章 | 状态 |
|---|------|------|---------|------|
| 00 | [`00-Artin抽代是什么.md`](00-Artin抽代是什么.md) | 总览 + Artin 风格 | 前言 | ✅ |
| 01 | `01-矩阵与群.md` | 矩阵群入门（Artin 特色）| Ch 1 | 📝 |
| 02 | `02-群.md` | 群论深化（接讲透群论）| Ch 2 | 📝 |
| 03 | `03-环与域.md` | 环/理想/商环 | Ch 3-4 | 📝 |
| 04 | `04-因子分解.md` | PID / UFD / 多项式环 | Ch 5-6 | 📝 |
| 05 | `05-Galois理论.md` | Galois 群 / 基本定理 | Ch 16 | 📝 |
| 06 | `06-表示论入门.md` | 群表示 / 特征标 | Ch 9-10 | 📝 |

---

## 二、前置

- 群论基础（见 [`../讲透群论/`](../讲透群论/)）
- 线性代数（Axler LADR 级别）

---

## 三、Artin 的特色

### 几何直觉

Artin 从**矩阵群**（GL_n, O_n, SL_n）开始，不是抽象定义。让你"看见"群。

### 现代

Artin 含表示论 + Lie 代数入门——很多其他教材不包含。

### 历史 + 几何

Artin 经常联系几何（如 Galois 理论 ↔ 覆叠空间 ↔ Riemann 面）。

---

📌 **下一步**：读 [`00-Artin抽代是什么.md`](00-Artin抽代是什么.md)。
