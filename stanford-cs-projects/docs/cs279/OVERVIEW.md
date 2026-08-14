# CS279: Computational Biology — Biomolecules

> Stanford University, Autumn 2026
> 领域: 计算结构生物学 / 蛋白质
> Prerequisites: CS274 或生物化学基础
> Units: 3-4
> Difficulty: ⭐⭐⭐⭐

---

## 📚 定位

聚焦生物大分子（蛋白质 / RNA）的结构与功能——从 Ramachandran 图到 AlphaFold，计算方法驱动现代药物设计。

---

## 🎯 学习目标

- 理解蛋白质结构与折叠层级（一级→四级）
- 掌握分子动力学仿真的基本原理
- 理解结构预测方法的演化（同源建模 → 深度学习）
- 能使用 PDB 数据库与 PyMOL 等工具

---

## 📅 核心模块

### Module 1: 蛋白质结构基础
- 氨基酸与肽键
- 二级结构：α螺旋、β折叠、转角
- Ramachandran 图（φ/ψ 角度分布）
- 三级 / 四级结构与折叠

### Module 2: 结构测定实验方法
- X 射线晶体学
- 核磁共振（NMR）
- 冷冻电镜（Cryo-EM）—— 2017 诺奖

### Module 3: 结构预测
- 同源建模（Homology Modeling）
- 穿线法（Threading）
- **AlphaFold 系列**: CNN → Evoformer → 复合物
- CASP 竞赛历程

### Module 4: 分子动力学
- 力场（AMBER、CHARMM）
- Verlet 积分与时间步
- 自由能计算与药物对接（Docking）

### Module 5: 功能基因组学
- 蛋白质功能注释
- 酶动力学模拟
- 蛋白质-蛋白质相互作用网络

---

## 💻 项目代码

📁 `supplementary/final_projects.py::cs279_demo`

**实现内容**:
1. ✅ 蛋白质二级结构 φ/ψ 角度可视化
2. ✅ Alpha Helix / Beta Sheet / Turn 特征展示
3. ✅ AlphaFold 三代演化总结

**运行**:
```bash
cd supplementary
python3 final_projects.py
```

**输出示例**:
```
蛋白质二级结构（φ, ψ 角度）:
  Alpha Helix    : φ= -60.0°, ψ= -45.0° (螺旋)
  Beta Sheet     : φ=-120.0°, ψ= 120.0° (伸展)
  Turn           : φ= -90.0°, ψ=   0.0° (转角)

AlphaFold 突破:
  - 2018 AlphaFold 1: CNN 预测距离
  - 2020 AlphaFold 2: Evoformer + 结构模块
  - 2024 AlphaFold 3: RNA / 配体 / 复合物
```

---

## 📊 关键概念/论文

| 概念 | 说明 |
|------|------|
| **Ramachandran 图** | 骨架构象允许区域 |
| **Evoformer** | AlphaFold2 核心架构 |
| **CASP** | 结构预测关键评估竞赛 |
| **PDB** | 蛋白质数据库（22万+结构） |

### 关键论文
1. **Jumper et al. 2021** — AlphaFold2 (Nature)
2. **Abramson et al. 2024** — AlphaFold3 (Nature)
3. Dill & MacCallum 2012 — 蛋白质折叠问题

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **想做结构生物学** | CS279 → AlphaFold 研究 |
| **药物设计方向** | Docking + 分子动力学 |
| **AI for Science** | 蛋白质是 DL 最佳应用场景 |
| **CS274 进阶** | 从序列到结构 |

---

## 🚀 扩展方向

1. 用 PyMOL / ChimeraX 可视化真实 PDB 结构
2. 探索 ESMFold（Meta 快速结构预测）
3. 阅读 DeepMind AlphaFold 博客系列
4. 尝试 RFdiffusion（蛋白质从头设计）

---

**对应代码**: `supplementary/final_projects.py::cs279_demo`
