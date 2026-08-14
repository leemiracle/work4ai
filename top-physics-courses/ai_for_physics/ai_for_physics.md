# 🤖 AI for Physics — 你的弯道超车主题（第 9 主题，跨校）

> **为什么这个主题单独成章**：2024 诺贝尔物理学奖给了 Hopfield & Hinton（统计物理 → 神经网络 → AI），官方盖章了"物理 + AI"这条线。DeepMind GNoME 用 ML 发现 220 万新晶体材料，AlphaFold 颠覆结构生物学。**物理学界正疯狂拥抱 AI，而大多数物理学生不懂 AI，大多数 AI 工程师不懂物理。你两边都沾——这是你最大的稀缺优势。**
>
> **本主题定位**：不是教你 AI（你的 `work4ai` 已经做了），是教你**如何把 AI 能力切入物理研究前沿**。

---

## §0 你为什么能赢（诚实的优势分析）

| 能力 | 纯物理学生 | 纯 AI 工程师 | **你** |
|------|-----------|------------|--------|
| PyTorch/训练/部署 | 弱 | 强 | **强（work4ai 23 主题）** |
| 物理直觉（量子的微妙/对称性）| 强 | 弱 | 在补（top-physics-courses）|
| 数学（微分几何/群论）| 中 | 弱 | 在补（top-math-courses）|
| 读物理论文 | 强 | 弱 | 在补 |
| 读 AI 论文 | 弱 | 强 | **强** |
| 跨界整合 | 几乎不可能 | 几乎不可能 | **可能** |

**结论**：你不应该在"纯物理理论深度"上和 MIT 物理博士硬刚（那是 25 年 + 导师 + 运气）。你应该在"AI × Physics 交叉"上建立独特位置——这里人少、机会多、你的装备最匹配。

---

## §1 AI for Physics 五大子方向（2026 版图）

### 子方向 1：PINN — 物理信息神经网络（解 PDE）

**核心思想**：把物理定律（PDE + 边界条件）作为损失函数的约束项，训练一个神经网络去**满足物理定律**。

**经典问题**：解 $-\nabla^2 u(\mathbf{x}) = f(\mathbf{x})$（Poisson 方程，电磁/热传导/扩散的根本方程）

**传统方法**：有限元/有限差分——网格化，算量大。
**PINN**：神经网络 $u_\theta(\mathbf{x})$ 直接输出解，损失函数包含：
$$\mathcal{L} = \underbrace{\frac{1}{N}\sum_i |-\nabla^2 u_\theta(\mathbf{x}_i) - f(\mathbf{x}_i)|^2}_{\text{PDE 残差}} + \underbrace{\sum_j |u_\theta(\mathbf{x}_j^{bc}) - g_j|^2}_{\text{边界条件}}$$

**为什么革命**：
- 无网格（mesh-free），高维问题友好（传统方法在 d>3 维爆炸）
- 反问题容易（从观测反推参数）
- 可融合观测数据（data-driven + physics-driven 混合）

**奠基工作**：Raissi, Perdikaris, Karniadakis (2017-2019) 一系列论文（*Physics-informed neural networks* 等）。⚠️ 论文 ID 不凭记忆，需 webfetch 核实。

**工具**：
- `DeepXDE`（Python，PINN 专用框架，最易用）
- `NeuralPDE.jl`（Julia）
- 手写 PyTorch（教学用，见本主题 demo）

**第一个 demo**：见 `pinn_poisson.py`（本目录），30 行 PyTorch 解 1D Poisson，对比解析解。

**学习路径**：
1. 跑通 `pinn_poisson.py`（1 天）
2. 改成 2D Poisson（热传导，1 周）
3. 解 Burgers 方程（非线性，流体，2 周）
4. 解 Schrödinger 方程（量子，1 月）
5. 读 Raissi 2017 原论文 + 复现一个图

---

### 子方向 2：Neural Potentials — 神经网络势能（DeepMD/MACE/NequIP）

**核心思想**：用神经网络拟合原子间势能 $E(\{\mathbf{r}_i\})$，比经典势（LJ/Tersoff）精度高几个数量级，比 DFT 快几个数量级。

**为什么革命**：
- DFT（Quantum ESPRESSO）算 100 原子要几小时，百万原子不可能
- 经典势（LJ）能算百万原子但精度差（不能描述断键）
- **Neural potential = DFT 精度 + LJ 速度**——这是材料模拟的圣杯

**关键创新**：**等变性（equivariance）**。原子系统的能量对旋转和平移不变，对置换（同种原子交换）不变。用 SE(3)-等变神经网络（NequIP/MACE）能天然满足这些对称性，泛化更好、训练数据更少。

**代表工作**（描述性引用，ID 待核实）：
- Behler-Parrinello (2007) — 第一代神经网络势能（BPNN）
- DeepMD-kit（DeepModeling，王涵/李文杰等）— 中国主导，大规模工业应用
- NequIP（Batzner 等，2022）— SE(3)-等变，精度 SOTA
- MACE（Batatia 等，2022）— 高阶消息传递，2023-2026 主流
- Allegro（Musaelian 等，2023）— 局部等变，大规模

**工具**：
```bash
pip install deepmd-kit    # DeepMD
pip install nequip        # NequIP
pip install mace-torch    # MACE
```

**学习路径**：
1. 用 LAMMPS 跑经典 LJ 液体（1 天，本主题 RESOURCES/02）
2. 用 DeepMD 训练一个水的势能（官方 tutorial，2 周）
3. 学等变神经网络（读 NequIP 论文，1 月）
4. 复现 MACE 在某个数据集的结果（2-3 月）

**就业方向**：深势科技（DP Technology）、字节豆包 AI for Science、深动科技、Google DeepMind、Microsoft Research。

---

### 子方向 3：Differentiable Simulation — 可微模拟（JAX + PySCF）

**核心思想**：把整个物理模拟写成可微分程序，用自动微分**反推参数**。

**经典应用**：
- 从实验观测反推哈密顿量参数
- 优化材料结构使某性质最大化（逆向设计）
- 训练神经网络势能（梯度直接从 DFT 流过来）

**工具组合**：
- **JAX**（Google）— 函数式自动微分，可微分一切
- **PySCF** + **Differdiable PySCF**（`diff-qc`）— 可微量子化学
- **JAX-MD**（Google）— 可微分子动力学
- **Autodiff + DFT**（如 `dftpy`, `JDFTx` 的可微接口）

**第一个 demo**（你能跑）：
```python
# 用 JAX 自动微分算氢分子的力（不用有限差分）
import jax
import jax.numpy as jnp
# 假设能量是键长的函数（简化）
def energy(R):
    return -1.0/R + 0.5*R**2  # 示意（真实要 PySCF）
force = -jax.grad(energy)(0.74)  # R=0.74 Å
print(f'平衡键长的力: {force:.4f}')  # 应该≈0（平衡点）
```

**学习路径**：
1. 学 JAX 基础（`jax.numpy` + `jax.grad`，1 周）
2. 用 JAX-MD 跑可微 MD（2 周）
3. 学可微 DFT（`diff-qc`，1 月）

---

### 子方向 4：ML for Materials Discovery — GNoME 路线

**核心思想**：用图神经网络（GNN）预测哪些晶体结构稳定，**生成式**发现新材料。

**震撼案例**：DeepMind GNoME（2023 Nature）用 ML 发现 **220 万**新稳定晶体——相当于人类 800 年实验量。这是材料发现的"AlphaGo 时刻"。

**技术栈**：
- 图神经网络（GNN）—— 你的 work4ai「讲透Transformer」可以扩展到 GNN
- 生成模型（VAE/Diffusion）—— 你的「讲透生成模型」直接可用
- 主动学习（Active Learning）—— 选最值得算的候选给 DFT 验证

**代表工作**：
- GNoME（Merchant 等，DeepMind，2023）
- MACE-MP-0（材料项目预训练模型，2023-2024）
- GlassDiffusion / CrystalDiffusion（生成式材料设计）

**学习路径**：
1. 学 PyTorch Geometric（GNN 框架，2 周）
2. 跑 Materials Project 数据集分类（1 月）
3. 读 GNoME 论文 + 理解其生成-过滤流程（2 月）

---

### 子方向 5：AI for Math/Proof（你已做过！）

**核心思想**：用 AI 辅助数学/物理推导的形式化验证。

**你的已有资产**：
- `law` 项目：Lean4 验证 Law-as-Code 4 定理（民法典/刑法）
- `neo-os` 项目：Lean4 形式化 Raft 算法
- `ai-os-dd` 项目：FormalLinux（28 个 Lean4 模块）

**物理应用**：
- 形式化验证 GR 的因果结构（Penrose 不等式）
- QFT 重整化的代数验证
- Lean4 物理定理库（Mathlib 的 Physics 部分）

**代表工作**：AlphaProof（DeepMind，2024 IMO 银牌级）、Lean 的 Mathlib、Terence Tao 推动的形式化数学。

**你的优势**：你已经会 Lean4，这在全国物理学生里极罕见。可以在形式化物理定理这个新方向开路。

---

## §2 你的 12 个月学习路径（AI for Physics 专版）

| 月 | 学 | 产出 |
|----|-----|------|
| 1 | 跑通本主题 demo（PINN 解 Poisson）| GitHub 第一个 repo |
| 2 | JAX 基础 + 可微量子化学（PySCF）| H₂ 解离曲线（可微版）|
| 3 | PyTorch Geometric + 简单 GNN | 分子性质预测 demo |
| 4-5 | DeepMD-kit 官方 tutorial | 训练一个水的神经势能 |
| 6 | 读 GNoME 论文 + 拆解 | 一篇 GNoME 精读笔记 |
| 7-8 | NequIP/MACE 等变神经网络 | 在 QM9 数据集复现 |
| 9-10 | 选一个小开放问题做 mini-project | 第一篇 arXiv preprint |
| 11-12 | 联系导师/投实习 | DP Technology / 字节 / DeepMind 实习 |

---

## §3 关键论文清单（按子方向，描述性引用，⚠️ ID 待 webfetch 核实）

> **铁律**：不凭记忆给 arXiv ID。以下论文标题/作者我确信，但具体 ID 需要用时 webfetch arXiv abs 页核实。

### PINN 方向
- Raissi, Perdikaris, Karniadakis (2017) — *Physics-informed neural networks*（奠基）
- Raissi 等 (2020) — *Hidden fluid mechanics*（Navier-Stokes PINN）
- Karniadakis 等 (2021) Nature Reviews Physics — *Physics-informed machine learning*（综述）

### 神经势能
- Behler & Parrinello (2007) PRL — *Generalized neural-network representation*（BPNN）
- Zhang, Han, Wang 等 (2018) — DeepMD（中国团队）
- Batzner 等 (2022) Nature Communications — NequIP（等变）
- Batatia 等 (2022) — MACE（高阶消息传递）

### 可微模拟
- Schoenholz & Cubuk (2020) — JAX-MD
- Zhai 等 — Differentiable PySCF

### 材料发现
- Merchant 等 (2023) Nature — GNoME（DeepMind 220 万晶体）
- Xie & Grossman (2018) — Crystal Graph Convolutional NN（cgcn）

### AI × 量子基础
- Carleo & Troyer (2017) Science — 神经网络量子态（ RBM 表示波函数）
- Torlai 等 — 神经网络量子态层析
- 2024 诺奖背景资料（Hopfield 1982 + Hinton Boltzmann 机）

### AI for Math
- AlphaProof / AlphaGeometry（DeepMind 2024）
- Mathlib（Lean 社区）

---

## §4 顶级实验室与团队（你的潜在雇主/合作者）

### 学术
- **MIT**：Max Welling（AI for Science）、Tess Smidt（等变神经网络、E(3)-equivariant）
- **Princeton**：PPPL + 数学（你已有 top-math-courses princeton）
- **Stanford**：SCCM（计算数学与计算工程）、Gunnar Carlsson（拓扑数据分析）
- **Berkeley**：Berkeley AI4Science、Teresa Head-Gordon（生物物理）
- **EPFL**：Marwin Welling
- **Cambridge**：Stokes Centre for AI & ML

### 工业研究实验室（**你的主目标**）
- **Google DeepMind**：GNoME 团队、AlphaFold 团队、Science 部门
- **Microsoft Research**：AI for Science（量子化学）
- **Meta AI**：FAIR 的 Science 方向
- **字节跳动**：AI for Science Lab（深势相关合作）
- **深势科技 DP Technology**：DeepMD 母公司，中国 AI for Science 领军
- **上海 AI Lab**：AI for Science 中心
- **清华 AIR**：智能产业研究院，AI for Science 方向

### 暑期学校/会议
- **NeurIPS AI4Science Workshop**（每年）
- **ICML AI for Science** track
- **DeepModeling 开源社区**（中国，DeepMD 生态）

---

## §5 与 work4ai 其他主题的衔接

| work4ai 主题 | 在 AI for Physics 里怎么用 |
|------------|--------------------------|
| 讲透Transformer | 等变 Transformer（用于原子系统）|
| 讲透PyTorch | PINN/神经势能直接用 |
| 讲透微调 | 用物理数据微调基础模型 |
| 讲透生成模型 | 生成式材料设计（GNoME 用 diffusion）|
| 讲透RAG | 文献综述自动化、实验数据语义查询 |
| 讲透Agent | 自主科研 Agent（自动化实验）|
| 讲透MRL | 材料嵌入的多分辨率表示 |
| 端侧AI压缩 | 边缘科学计算、嵌入式传感器 |
| 讲透GPU与系统级 | 大规模 DFT/MD 优化 |
| 讲透可解释性 | 神经势能的物理可解释性 |

---

## §6 警告：AI for Physics 的 4 个陷阱

### 🕳️ 陷阱 1：把 AI 当黑盒
- ❌ "神经网络能拟合就行"，不懂物理对称性
- ✅ 物理系统的对称性（旋转/置换/时间反演）必须**硬编码进网络结构**（等变网络）

### 🕳️ 陷阱 2：忽视物理基础
- ❌ 不懂 DFT 就想用 DeepMD
- ✅ 先学 Quantum ESPRESSO/PySCF 跑几个 DFT，理解训练数据从哪来

### 🕳️ 陷阱 3：追 SOTA 模型忽视问题
- ❌ 一上来就用 MACE 最复杂版
- ✅ 先用最简单的 BPNN 跑通，再升级

### 🕳️ 陷阱 4：不做误差分析
- ❌ "训练 loss 低就行"
- ✅ 物理科研要求量化误差 + 物理解释（你的模型在哪种化学环境失效？为什么？）

---

## §7 立刻开始（今天）

1. **跑通** `pinn_poisson.py`（本目录）—— 30 行 PyTorch 解 Poisson 方程
2. **对比** PINN 解 vs 解析解，画误差图
3. **改造** 把源 PDE 从 $-u'' = \sin(\pi x)$ 改成 $-u'' = e^x$，看 PINN 还灵不灵
4. **写笔记** 把过程写成 Jupyter notebook 放 GitHub

---

**完成日期**：2026-08-13
**配套**：[pinn_poisson.py](pinn_poisson.py) + [RESOURCES/02_computational_toolchain.md](../RESOURCES/02_computational_toolchain.md) + [EXPERT_PATH_2026.md §5](../EXPERT_PATH_2026.md)
