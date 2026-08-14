# 经典讲义逐本导读 — 整合 47 本（Tong + FLP + Berkeley + Landau + Susskind）

> **为什么有这个目录**：之前的 [RESOURCES/08_lectures_and_courses.md](../RESOURCES/08_lectures_and_courses.md) 和 [09_lectures_handbook.md](../RESOURCES/09_lectures_handbook.md) 是**清单**。本目录把这些经典讲义**逐本落盘成导读笔记**，整合进项目，成为学习的"黄金中段"资源。
>
> **每本笔记不是逐页翻译**，是：这本讲义讲什么 / 核心是什么 / 怎么读 / 做完哪些题 / 读完能干什么 / 配合项目哪章。

---

## 5 大系列，47 本讲义

| 系列 | 数量 | 定位 | 难度区间 |
|------|------|------|---------|
| **[tong/](tong/)** David Tong | 23 本 | **当代费曼，首选**。免费、全面、清晰 | ★ - ★★★★★ |
| **[feynman/](feynman/)** 费曼讲义 FLP | 3 卷 | 直觉与教学的圣经。免费在线 | ★★ - ★★★★ |
| **[berkeley/](berkeley/)** Berkeley Course | 5 卷 | 与费曼同时代，系统互补 | ★★ - ★★★★ |
| **[landau/](landau/)** Landau-Lifshitz | 10 卷 | 研究生圣经。最简洁深刻 | ★★★ - ★★★★★ |
| **[susskind/](susskind/)** 理论最小 | 6 本 | 科普→教材的桥梁 | ★★ - ★★★ |

---

## 整体阅读路径（从零到研究生）

### 阶段 0：科普级起点（零数学门槛）
- **[tong/01_particle_physics.md](tong/01_particle_physics.md)** — Tong 的粒子物理（只需高中数学）
- 配合 [../RESOURCES/00_popular_science.md](../RESOURCES/00_popular_science.md)（科普书单）

### 阶段 1：本科入门（牛顿力学 + 狭义相对论）
- **主读**：[tong/02_dynamics_relativity.md](tong/02_dynamics_relativity.md)
- **并行看**：[feynman/vol1_mechanics.md](feynman/vol1_mechanics.md)（费曼卷 1，直觉）
- **桥梁**：[susskind/01_classical_mechanics.md](susskind/01_classical_mechanics.md)
- **配合项目**：L01 力学

### 阶段 2：本科核心（电磁/量子/统计）
- **电磁**：[tong/05_electromagnetism.md](tong/05_electromagnetism.md) + [berkeley/vol2_purcell_em.md](berkeley/vol2_purcell_em.md)（Purcell 相对论视角）
- **量子**：[tong/06_quantum_mechanics.md](tong/06_quantum_mechanics.md) + [feynman/vol3_quantum.md](feynman/vol3_quantum.md)（费曼卷 3）
- **统计**：[tong/07_statistical_physics.md](tong/07_statistical_physics.md) + [berkeley/vol5_reif_statistical.md](berkeley/vol5_reif_statistical.md)（Reif 深化）
- **配合项目**：L02 电磁 / L08 量子 / L05 统计

### 阶段 3：本科进阶（拉氏/哈氏 + 数学方法）
- **[tong/04_classical_dynamics.md](tong/04_classical_dynamics.md)** — 拉格朗日/哈密顿（量子的前置）
- **[tong/03_vector_calculus.md](tong/03_vector_calculus.md)** — 矢量微积分
- **配合项目**：L06 数学方法

### 阶段 4：研究生入门（GR/QFT/粒子）
- **GR**：[tong/13_general_relativity.md](tong/13_general_relativity.md) + [susskind/04_gr.md](susskind/04_gr.md)
- **QFT**：[tong/14_qft.md](tong/14_qft.md)（**有视频！首选**）
- **粒子**：[tong/17_standard_model.md](tong/17_standard_model.md)
- **经典补充**：[landau/vol1_mechanics.md](landau/vol1_mechanics.md)（重读力学，研究生视角）
- **配合项目**：L10 GR / L11 QFT / L13 粒子

### 阶段 5：前沿（弦论/拓扑/SUSY）
- [tong/18_string_theory.md](tong/18_string_theory.md) / [tong/19_quantum_hall.md](tong/19_quantum_hall.md) / [tong/15_stat_field_theory.md](tong/15_stat_field_theory.md)
- [landau/](landau/) 全 10 卷（研究生参考）

---

## 每本笔记的标准结构

见 [TEMPLATE.md](TEMPLATE.md)。每本含：
- §0 基本信息（作者/难度/链接/配合项目）
- §1 一句话定位
- §2 前置知识
- §3 讲义全景（章节地图）
- §4 核心章节拆解（核心概念+关键公式+直觉图像+反直觉点）
- §5 必做习题
- §6 读完后你应该能（可勾选）
- §7 与项目的映射
- §8 延伸阅读
- §9 学习建议

---

## 反直觉铁律（最重要）

> **每主题只选 1 本主读，读完再开下一本。**
>
> 不要同时收藏 Tong + FLP + Berkeley + Landau 然后每本读 10 页。
> - 力学 → Tong *Dynamics and Relativity*
> - 电磁 → Purcell (Berkeley Vol 2)
> - 量子 → Tong QM + Feynman 卷 3
> - 统计 → Tong Statistical Physics
> - GR → Tong GR
> - QFT → **Tong QFT（首选，有视频）**
>
> **物理学不是比谁读得多，是比谁读得透。**

---

## 怎么用这些笔记

1. **选主题**：根据项目 L01-L15，找到你要学的主题
2. **选讲义**：查上面的"整体阅读路径"，选 1 本主读
3. **读笔记**：先读对应的导读笔记（本文档目录下），建立"这本讲什么"的预期
4. **读原文**：去讲义免费链接（davidtong.org / feynmanlectures.caltech.edu）下载 PDF
5. **做题**：按笔记的"必做习题"清单做
6. **验证**：对照笔记的"读完后你应该能"自检

---

## 与项目其他资源的关系

```
科普起点 (RESOURCES/00)
    ↓
经典讲义逐本导读 (本目录, classical_lectures/)  ← 你在这里
    ↓
项目 10 校课程笔记 (mit-physics/ caltech-physics/ ...)  L01-L15
    ↓
研究级资源 (RESOURCES/01-07: 数学/工具链/论文/训练/社区)
    ↓
AI for Physics (ai_for_physics/)  你的弯道超车
```

---

**完成日期**：2026-08-13
**状态**：✅ **全部深化完成 v2**。47 本讲义笔记全部从初版（~130 行/本）深化到 ~280-320 行/本。总计 54 md / **13377 行**（tong 6603 / feynman 917 / berkeley 1586 / landau 2350 / susskind 1727）。每本含 §4 详细推导 + §5 习题表格 + §10 常见误区 + §11 跨教材对比。
**核实**：Tong 讲义清单 webfetch 自 davidtong.org/teaching/（2026-08-13）；FLP 链接 feynmanlectures.caltech.edu
**定位**：留作未来 AI×Science 交叉参考档案（当前主线 interp + 数学，不投入物理学习时间）
