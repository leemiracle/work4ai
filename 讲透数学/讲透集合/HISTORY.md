# 讲透集合 · HISTORY

## 2026-09-06 创刊

- 宇宙合并日同批创刊（设计：`../../docs/superpowers/specs/2026-09-06-讲透数学宇宙合并-design.md`）
- README 目录宪法：五问 → 五章（分支X光五问模板首例）
- 00-体系结构：罗素悖论 → ZFC 十公理三分类（建设/限制/同一）→ V 分层 → 四大分支地图，六层讲透 + 3 个反直觉发现 + ✋🐍⚡ 练习
- experiments/00_cantor_diagonal.py：对角论证三连（|N|=|Q| / |N|<|R| / Cantor 定理），跑通
- experiments/00_zfc_finite_model.py：frozenset 构造 V₀…V₄，九条公理有限层逐条判定（无穷❌幂集❌顶层溢出⚠️），跑通
## 2026-09-06 全量发刊（01-04 章）

- 01-近五年创新：六方向文献实查版——Asperó–Schindler MM⁺⁺⇒(\*)（Ann. Math. 2021 公理合流）、
  Goldberg UA 纲领（2024 Hausdorff 奖章）、Martin 猜想（BSL 2021）、Flypitch/CH 形式化
  （arXiv:1904.10570 + Palomar 注册表 Lean4 移植）、Mathlib 生态、AlphaProof 距离评估
- 02-语言特征：∈ 语言表达力地图（Δ₀/Σ₁ 量词预算）、逻辑性格四问四答、Skolem 悖论、
  五路线规范化对照表（ZFC/NBG/MK/CZF/类型论）
- 03-可构造与结构：Def 算子、凝聚/覆盖引理与 0#、Mostowski 塌缩、有限层 L_n=V_n 巧合与 ω 悬崖
- 04-转代码：六条机械化走廊（数据结构/类型/布尔值模型/Borel code/SAT/力迫迭代）+
  三层不可机械化边界 + core 版 Cantor（本机 v4.33.1 编译通过）
- 新实验三连（全部跑通）：02_delta0_evaluator（绝对性对照——修复过 ∈ 原子句比较变量名的 bug）、
  03_constructible_L（Def 有限实现+塌缩器四图）、04_forcing_borel（半可判定+泛型 12/12 逃逸）
- 状态：五章 ✅，系列主体完成

