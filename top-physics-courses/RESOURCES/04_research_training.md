# 资源清单 §04 · 科研训练手册（P1）

> **为什么这是 P1**：项目让你"读懂"，但专家必须"做出来"。教材 → 论文 → 原创研究之间，需要**主动训练**：做题（建立直觉与熟练度）→ 复现（学会读+实现别人的工作）→ mini-paper（学会表达自己的发现）。
>
> **本文档**：给出三段式训练的具体项目、检查标准、产出物。
>
> **配套**：[EXPERT_PATH_2026.md §4.4](../EXPERT_PATH_2026.md) + [03_paper_reading_list.md](03_paper_reading_list.md)

---

## §1 第一段：做题（前 6-12 月，建立熟练度）

### 1.1 题库（按难度递进）

| 题源 | 难度 | 用途 | 获取 |
|------|------|------|------|
| **GRE Physics** 题库（4PracticeTests 等）| ★ | 速测广度，100 道约 5 小时 | 网上免费 PDF |
| **Morin** *Introduction to Classical Mechanics* 习题 | ★★ | 力学直觉，含 700+ 题 | 书 |
| **IPhO**（国际物理奥林匹克）历年题 | ★★ | 极佳的物理直觉训练 | ipho.org 免费 |
| **Pitman / Berkeley Stat 134** 习题 | ★★ | 概率直觉 | 书 |
| **Griffiths 量子/电动力** 全部章末题 | ★★ | 本科核心，必做 | 书 |
| **Sakurai** 习题 | ★★★ | 研究生量子 | 书 + 官方 solutions |
| **Peskin & Schroeder** 习题 | ★★★★ | 研究生 QFT | 书 + Stanford 解答 |
| **MIT/Princeton/Stanford qualifying exam**（公开）| ★★★★ | 博士资格考试级，深度 | 各校网站免费 |
| **CUSPEA** 老题（中国 80 年代赴美物理考试）| ★★★ | 经典综合题 | Lim *Problems and Solutions* 系列 |
| **Pathria** 统计力学习题 | ★★★ | 研究生统计 | 书 |

### 1.2 做题的三个层次
- **做出**：算出正确答案（60% 学生停在这）
- **做懂**：理解为什么这个方法有效（30% 学生到这）
- **做通**：能改造问题、提出变体、教别人（10% 学生到这）

### 1.3 做题纪律（自检表）
- [ ] 每章学完**合上书**做 5-10 题，不是看完解答再点头
- [ ] 做错的题**红笔标注**，一周后重做
- [ ] 每周做一道 qualifying exam 难度题（哪怕花 2 小时）
- [ ] 建一个 `problem_solutions/` 笔记本（手写或 LaTeX），记录关键技巧

### 1.4 速测（每月一次，纸笔 30 分钟）
1. 推导拉格朗日方程从最小作用量原理
2. 推导麦克斯韦方程→光速 $c$
3. 解无限深势阱能级
4. 解释熵增为什么是统计规律
5. 写出 Schwarzschild 度规

---

## §2 第二段：复现经典论文（6-18 月，学会实现）

### 2.1 复现 ≠ 读懂

**复现 = 用代码把论文结论跑出来**。这是从"读者"到"研究者"的关键一步。

### 2.2 复现项目清单（10 个，按难度）

#### ★ 入门（每个 1-2 天）

**项目 1：2D Ising 模型 Metropolis**
- **目标**：用 NumPy 实现 Metropolis 算法，扫描温度，画磁化率 ⟨|m|⟩ vs T
- **验证**：临界温度 $T_c = 2/\ln(1+\sqrt{2}) \approx 2.269$（Onsager 精确解）
- **工具**：NumPy + matplotlib
- **参考**：项目 `caltech-physics/physics_demos.py` 已有玩具版，升级到科研版

**项目 2：无限深势阱 + Crank-Nicolson**
- **目标**：数值解含时 Schrödinger 方程，演化波包
- **验证**：能量守恒（数值误差 < 1%）
- **工具**：NumPy + matplotlib
- **参考**：MIT 8.04 课程

**项目 3：双缝干涉数值模拟**
- **目标**：用 Fresnel 积分算干涉图样
- **验证**：条纹间距公式
- **工具**：NumPy

#### ★★ 进阶（每个 1-2 周）

**项目 4：Bell 不等式 CHSH 数值**
- **目标**：用 QuTiP 或 NumPy 模拟纠缠态，计算 CHSH 量 $S > 2$
- **验证**：量子预测 $S = 2\sqrt{2} \approx 2.828$
- **工具**：QuTiP 或纯 NumPy
- **论文**：#2 Bell + #4 Aspect（[03_paper_reading_list](03_paper_reading_list.md)）

**项目 5：氢分子解离曲线**
- **目标**：用 PySCF 算 H₂ 键长 0.3-3.0 Å 的能量曲线
- **验证**：平衡键长 0.74 Å，解离能 4.5 eV
- **工具**：PySCF
- **延伸**：对比 HF / CISD / CCSD 方法

**项目 6：Planck 黑体辐射 + CMB**
- **目标**：拟合真实 COBE/FIRAS 数据，得宇宙温度 $T \approx 2.725$ K
- **验证**：与教科书值一致
- **工具**：NumPy + scipy.optimize.curve_fit + 真实数据（NASA LAB 免费）

**项目 7：Lennard-Jones 液体 MD**
- **目标**：用 LAMMPS 或手写 MD，算径向分布函数 $g(r)$
- **验证**：液态氩的 $g(r)$ 第一峰位置 ~3.4 Å
- **工具**：LAMMPS 或 ASE

#### ★★★ 高阶（每个 2-4 周）

**项目 8：神经网络量子态（Carleo-Troyer 复现）**
- **目标**：用 RBM 表示 1D Heisenberg 链的基态波函数
- **验证**：基态能量与精确解（Bethe ansatz）误差 < 1%
- **论文**：#54 Carleo & Troyer (2017)
- **工具**：PyTorch

**项目 9：PINN 解 Burgers 方程**
- **目标**：扩展 `pinn_poisson.py` 到非线性流体方程
- **验证**：激波形成位置与解析解（特定初值有解）
- **工具**：PyTorch 或纯 NumPy（你的 `ai_for_physics/pinn_poisson.py`）
- **论文**：#53 Raissi

**项目 10：DMRG 解 1D Heisenberg 链**
- **目标**：用密度矩阵重整化群算 100 自旋链的基态
- **验证**：基态能量 $E/N \approx -0.4431$（精确）
- **工具**：TeNPy（Python）或 ITensor

### 2.3 复现的标准产出

每个复现项目必须有：
1. **GitHub repo**，含 README.md 说明
2. **Jupyter notebook**，逐步可执行
3. **复现报告**：你算的值 vs 论文/精确解值，误差分析
4. **可视化**：至少 1 张图（matplotlib，带标签）
5. **环境文件**：`requirements.txt` 或 `environment.yml`

> **这些 repo 就是你未来的科研 portfolio**——比简历有力 10 倍。

---

## §3 第三段：mini-paper（18 月以后，学会表达）

### 3.1 为什么要写

- **教是最好的学**（费曼学习法）：写不出 = 没真懂
- **建立可见度**：GitHub + arXiv = 你的科研 ID
- **训练科学写作**：未来投顶刊的必备技能

### 3.2 选题原则

✅ **好的 mini-paper 选题**：
- 一个**小而清晰**的开放问题（不要宏大叙事）
- 你能用现有工具（NumPy/PySCF/PyTorch）解决
- 有可量化的结果（一个数字、一张图、一个对比）
- 有教学价值（让别人能从你的工作学到东西）

❌ **坏的选题**：
- "证明 Riemann 假设"（不可能）
- "用 ML 解决所有材料问题"（太空）
- "我对量子的哲学思考"（不是研究）

### 3.3 mini-paper 候选（按你的方向）

| # | 选题 | 工具 | 难度 |
|---|------|------|------|
| A | "用 PINN 解 XXZ 模型的基态" | PyTorch | ★★★ |
| B | "对比 HF/CISD/CCSD 在 H₂ 解离的失败模式" | PySCF | ★★ |
| C | "用等变 GNN 预测 QM9 分子的 HOMO-LUMO gap" | PyG | ★★★ |
| D | "DeepMD 训练水的势能：精度 vs 数据量" | DeepMD | ★★★ |
| E | "Lean4 形式化验证 XXX 物理定理"（你的优势）| Lean4 | ★★★ |
| F | "某 PINN 在高维 Poisson 的失效分析" | PyTorch | ★★ |

### 3.4 IMRAD 结构（物理论文标准）

```
1. Introduction     — 问题是什么？为什么重要？前人做了什么？
2. Methods          — 你用了什么方法？（数学+算法+实现）
3. Results          — 你得到了什么数字/图？
4. Discussion       — 数字意味着什么？局限？未来工作？
```

### 3.5 LaTeX 写作

**模板**：用 Overleaf（在线，免费）或本地 TeX Live + VS Code。

```latex
\documentclass[11pt]{article}
\usepackage{amsmath,amssymb,graphicx,hyperref}
\title{...}
\author{...}
\begin{document}
\maketitle
\begin{abstract}...\end{abstract}
\section{Introduction}...
\section{Methods}...
\section{Results}...
\section{Discussion}...
\bibliographystyle{plain}
\bibliography{refs}
\end{document}
```

**物理论文模板**：用 **REVTeX**（AIP/APS 期刊标准，arXiv 兼容）。

### 3.6 arXiv 投稿（练手）

- arXiv 需 **endorsement**（领域内有人背书）
- 获取方式：① 发邮件给 arXiv 作者 ② 通过 Physics SE 认识的人 ③ 你的导师
- 投稿前用 `arXiv submit` 检查 LaTeX 编译
- **注意**：arXiv 没有 peer review，是 preprint。但它是物理圈的主要交流渠道。

### 3.7 学生期刊（有 peer review）

| 期刊 | 说明 |
|------|------|
| **Journal of Undergraduate Research** | 美国本科生 |
| **European Journal of Physics** | 教学级，适合 mini-paper |
| **American Journal of Physics** | 教学级，影响因子不高但严谨 |
| **Physical Review E** | 包含一些教学向内容 |

---

## §4 科研 Portfolio 构建（你的"无形简历"）

### 4.1 必备组件

| 组件 | 平台 | 重要性 |
|------|------|--------|
| **GitHub**（10+ repo，复现+mini-paper）| github.com | ★★★ 第一印象 |
| **个人主页**（介绍你 + 论文列表）| GitHub Pages / Notion | ★★★ |
| **arXiv 作者页**（1-3 篇 preprint）| arxiv.org/a/... | ★★★ |
| **Google Scholar**（被引用统计）| scholar.google.com | ★★ |
| **ORCID**（学术 ID）| orcid.org | ★★ |
| **Physics Stack Exchange**（1k+ 声望）| physics.stackexchange.com | ★★ |
| **LinkedIn**（工业实习用）| linkedin.com | ★ |

### 4.2 GitHub repo 标准模板

```
awesome-physics-repro/
├── README.md              # 项目说明 + 复现步骤 + 结果截图
├── environment.yml        # 可复现环境
├── LICENSE                # MIT 推荐
├── data/                  # 小数据（大的用 git-lfs 或外部链接）
├── notebooks/             # 探索 notebook
├── src/                   # 生产代码
├── results/               # 输出图/数字
└── paper/                 # LaTeX mini-paper
```

### 4.3 README 黄金法则

- 第一段：**这个项目做了什么？**（一句话）
- 第二段：**关键结果**（一个数字 + 一张图）
- 第三段：**如何复现**（3 行命令：clone → install → run）

---

## §5 自检清单（每月一次）

### 5.1 做题自检
- [ ] 本月做了 __ 道题（目标：30+）
- [ ] 错题重做率 __%
- [ ] 做对了 __ 道 qualifying exam 难度题

### 5.2 复现自检
- [ ] 本月完成 __ 个复现项目（目标：1）
- [ ] 每个 repo 有 README + notebook + 复现报告
- [ ] GitHub commit 频率：__ 次/周（目标：5+）

### 5.3 写作自检
- [ ] 本月写了 __ 页 LaTeX（目标：10+）
- [ ] 投了 __ 篇 arXiv（目标：6 个月 1 篇）
- [ ] 收到 __ 次反馈（来自 Physics SE / 同行 / AI）

### 5.4 总体进度（对照 EXPERT_PATH_2026 §6 里程碑）
| 月 | 应达到 | 你在哪 |
|----|-------|--------|
| 6 | 拉氏推单摆 / 势阱 / Ising Metropolis | __ |
| 12 | Maxwell→光速 / NumPy 氢能级 | __ |
| 18 | Bell 复现 / PySCF H₂ | __ |
| 24 | Peskin 前 3 章 / PINN PDE / SE 1k | __ |
| 36 | 第一篇 arXiv / 稳定合作者 | __ |

---

**完成日期**：2026-08-13
**配套**：[03_paper_reading_list.md](03_paper_reading_list.md) + [02_computational_toolchain.md](02_computational_toolchain.md) + [EXPERT_PATH_2026.md](../EXPERT_PATH_2026.md)
