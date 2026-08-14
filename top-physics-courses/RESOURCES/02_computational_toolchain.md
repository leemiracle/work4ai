# 资源清单 §02 · 科研级计算工具链（P0）

> **为什么这是 P0**：项目的 `physics_demos.py` 全是纯标准库（`math`/`random`），适合"看现象"，离科研差 10 个数量级。**现代物理学 = 理论 + 实验 + 计算（第三支柱）**。不会科研级工具 = 不能做现代物理研究。
>
> **本文档**：从安装到"第一个跑通的 demo"，覆盖 Python 科研栈 + 物理专用工具 + HPC + 可复现工作流。
>
> **配套**：[EXPERT_PATH_2026.md §4.2](../EXPERT_PATH_2026.md)

---

## §1 工具链全景（一张图选你需要的）

```
                    物理科研计算
                         │
        ┌────────────────┼────────────────┐
   通用科学计算        物理专用模拟        高性能
        │                  │                │
   NumPy(数组)       Quantum ESPRESSO    Fortran(遗产)
   SciPy(算法)       (DFT 第一性原理)    C/C++(性能)
   SymPy(符号)       VASP(商业 DFT)      CUDA(GPU)
   matplotlib(画图)  LAMMPS(MD)          OpenMP(共享内存)
   Jupyter(笔记本)   GROMACS(生物MD)     MPI(分布式)
   pandas(数据)      PySCF(量子化学)     Slurm(集群调度)
        │            QuTiP(量子光学)         │
        │            ASE(原子模拟)      可复现工作流
        │            DeepMD(ML势能)     git + Docker
        │            NeuralPDE(PINN)    conda + Snakemake
        │                  │            Jupyter + nbconvert
        └──────────────────┴────────────────┘
                         │
                   AI for Physics(见 ai_for_physics/)
                   PyTorch / JAX / TensorFlow
```

**核心洞察**：你不需要学全部。按方向选：
- **凝聚态/材料**：Quantum ESPRESSO + LAMMPS + ASE
- **量子化学**：PySCF + Gaussian/ORCA
- **量子光学/信息**：QuTiP + Qiskit
- **AI for Physics**：PyTorch + JAX + DeepMD（你的主战场）
- **通用理论/计算**：NumPy + SciPy + SymPy + Mathematica

---

## §2 Python 科研栈（最低标配，1 个月搞定）

### 2.1 安装（一次性）

```bash
# 推荐：用 conda 管理环境（避免污染系统 Python）
# 安装 Miniconda: https://docs.conda.io/en/latest/miniconda.html
conda create -n physics python=3.11
conda activate physics

# 一次性装齐核心栈
conda install numpy scipy sympy matplotlib pandas jupyter ipython -c conda-forge

# 验证
python -c "import numpy, scipy, sympy, matplotlib, pandas; print('OK')"
```

### 2.2 每个库的"第一个 demo"

#### NumPy — 数组与线性代数
```python
import numpy as np
# 物理例子：氢原子能级（忽略精细结构）
n = np.arange(1, 5)  # 主量子数 1,2,3,4
E = -13.6 / n**2     # eV
print("能级:", dict(zip(n, E)))
# 矩阵对角化：求谐振子的能量本征值（数值法）
H = np.array([[1, -0.5, 0], [-0.5, 1, -0.5], [0, -0.5, 1]])
eigvals = np.linalg.eigvalsh(H)
print("本征值:", eigvals)
```

#### SciPy — 物理算法
```python
from scipy.integrate import odeint
from scipy.optimize import brentq
import numpy as np
# 物理例子：单摆运动方程数值解
def pend(y, t, b, g, L):
    theta, omega = y
    return [omega, -b*omega - (g/L)*np.sin(theta)]
t = np.linspace(0, 10, 200)
sol = odeint(pend, [np.pi/3, 0], t, args=(0.1, 9.8, 1.0))
print("末角度:", sol[-1, 0])
```

#### SymPy — 符号推导（物理学家最爱）
```python
from sympy import symbols, Function, diff, dsolve, sin, cos
t = symbols('t')
theta = Function('theta')(t)
# 单摆方程符号推导
g, L = symbols('g L', positive=True)
eq = diff(theta, t, 2) + (g/L)*sin(theta)
print("运动方程:", eq)
# 小角度线性化解
linear_eq = diff(theta, t, 2) + (g/L)*theta
sol = dsolve(linear_eq, theta)
print("小角度解:", sol)
```

#### matplotlib — 物理画图
```python
import matplotlib.pyplot as plt
import numpy as np
# 黑体辐射谱（Planck 定律）
nu = np.linspace(1e13, 3e15, 500)
h, c, k = 6.626e-34, 3e8, 1.381e-23
for T in [3000, 4000, 5000, 6000]:
    B = (2*h*nu**3/c**2) / np.expm1(h*nu/(k*T))
    plt.plot(nu, B, label=f'T={T}K')
plt.xlabel('频率 (Hz)'); plt.ylabel('谱辐照度')
plt.legend(); plt.savefig('blackbody.png', dpi=100)
```

### 2.3 第一个"科研级"练习：用 NumPy 重写项目里的 demo

把 `~/ai/work4ai/top-physics-courses/cambridge-physics/physics_demos.py` 里的"卡文迪许称量地球"用 NumPy + matplotlib 重写，加上误差棒和图。**这是你的第一个科研级 portfolio 作品。**

---

## §3 物理专用工具（按方向选 1-2 个深入）

### 3.1 【凝聚态/材料】Quantum ESPRESSO（DFT 第一性原理）

**用途**：从薛定谔方程数值解出材料的电子结构、能带、电荷密度。凝聚态/材料方向**必装**。

```bash
# 安装（开源，免费）
conda install qe -c conda-forge  # 或从源码编译（更性能）
# 文档：https://www.quantum-espresso.org/
```

**第一个 demo**：算硅的能带结构（QE 官方有完整 tutorial）。
- 学完后能：回答"为什么硅是半导体？它的带隙多大？"

**替代/对比**：
- **VASP**（商业，~$5000/年，学校常有 license）— 工业标准，更稳
- **ABINIT** / **GPAW** / **Octopus**（开源）— 各有侧重

### 3.2 【分子动力学】LAMMPS

**用途**：大规模原子模拟（百万原子），化学反应、生物分子、材料力学。

```bash
conda install lammps -c conda-forge
# 文档：https://docs.lammps.org/
```

**第一个 demo**：氩原子的 Lennard-Jones 液体（LAMMPS 官方 example）。
- 学完后能：算液体的径向分布函数 g(r)、扩散系数。

**替代**：**GROMACS**（生物分子 MD，更快）、**HOOMD-blue**（GPU 加速，软物质）

### 3.3 【量子化学】PySCF（Python，可接 PyTorch/JAX）

**用途**：量子化学计算，**与 AI for Physics 结合的最佳桥梁**（纯 Python，可微分）。

```bash
pip install pyscf
# 文档：https://pyscf.org/
```

**第一个 demo**（你今天就能跑）：
```python
from pyscf import gto, scf
# 氢分子的 Hartree-Fock 计算
mol = gto.M(atom='H 0 0 0; H 0 0 0.74', basis='sto-3g', verbose=0)
mf = scf.RHF(mol)
energy = mf.kernel()
print(f'H2 总能量: {energy:.4f} Hartree = {energy*27.211:.2f} eV')
# 实验: -31.7 eV (解离能 ~4.5 eV)
```

**为什么 PySCF 对你重要**：它是纯 Python，可以接 JAX 自动微分，能做"可微量子化学"——这是 AI for Physics 的核心工具之一。

### 3.4 【量子光学/信息】QuTiP + Qiskit

**QuTiP**（Quantum Toolbox in Python）：开放量子系统模拟
```bash
pip install qutip
```
**第一个 demo**：双能级系统的 Rabi 振荡。

**Qiskit**（IBM 量子计算 SDK）：量子电路模拟+真实量子硬件
```bash
pip install qutip qiskit
```
**第一个 demo**：Bell 态制备 + 测量。

### 3.5 【原子模拟统一接口】ASE（Atomic Simulation Environment）

**用途**：统一接口调 QE/VASP/LAMMPS/GPAW 等不同后端， workflow 自动化。

```bash
pip install ase
# 文档：https://wiki.fysik.dtu.dk/ase/
```

**价值**：写一次脚本，换不同计算后端。凝聚态方向必备。

### 3.6 【ML 势能】DeepMD-kit（AI for Physics 核心）

**用途**：用神经网络拟合原子间势能，比经典势（LJ/Tersoff）精度高几个数量级，比 DFT 快几个数量级。**这是你的主战场**。

```bash
pip install deepmd-kit  # 或从源码编译（带 GPU 支持）
# 文档：https://docs.deepmodeling.com/projects/deepmd/
```

**关系**：DeepMind、字节、深势科技（DP Technology）都在做这个。你 work4ai 的 AI 能力直接可用。

### 3.7 【符号计算】Mathematica / SageMath / SymPy

| 工具 | 优劣 |
|------|------|
| **Mathematica**（商业）| 物理系标配，符号+数值+可视化一体，学生版 ~$150 |
| **SageMath**（开源）| 免费，Python 接口，功能接近 Mathematica 80% |
| **SymPy**（Python 库）| 已在 §2.1 装，轻量，够用 90% |

**建议**：先用 SymPy（已装、免费、够用），需要更强时上 SageMath 或 Mathematica。

---

## §4 高性能计算（HPC）必备技能

物理研究到一定规模（DFT 大体系、MD 百万原子、QCD 格点）必须用集群。

### 4.1 编程语言

| 语言 | 为什么要学 |
|------|----------|
| **Fortran** | Quantum ESPRESSO / LAMMPS 内核仍是 Fortran，要改源码必须会。学 Fortran 90/2003 即可 |
| **C/C++** | 性能关键代码、GPU 内核。C++ 学到能读懂 Eigen 即可 |
| **CUDA** | GPU 加速（JAX/PyTorch 底层）。学编程模型即可，不必精通 |
| **Julia**（可选）| 物理+数值的新星，语法像 Python 速度像 C。值得跟进 |

### 4.2 并行计算

| 技术 | 用途 |
|------|------|
| **OpenMP** | 单节点多核共享内存并行（最简单，`#pragma omp parallel for`）|
| **MPI**（Message Passing Interface）| 跨节点分布式并行（集群标配）。学 6 个基本函数即可 |
| **GPU**（CUDA / HIP / SYCL）| 大规模数据并行（DFT/MD/QCD）|

**学习资源**：
- OpenMP/MPI：Lawrence Livermore 的免费教程（computing.llnl.gov/tutorials）
- GPU：CUDA C++ Programming Guide（NVIDIA 官方）

### 4.3 集群使用

| 工具 | 用途 |
|------|------|
| **Slurm** | 几乎所有学术超算的作业调度系统。学 5 个命令（sbatch/squeue/scancel/sinfo/sacct）|
| **SSH + tmux** | 远程会话管理 |
| **模块系统**（`module load`）| 加载不同软件版本 |

**实习机会**：申请国家超算中心（无锡/天津/广州/北京）的账号。学生通常免费。

---

## §5 可复现科研工作流

**为什么重要**：现代科研要求"可复现"——别人能从你的代码+数据复现你的结果。这是顶刊（Nature/Science/PRL）的硬要求。

### 5.1 工具栈

| 工具 | 用途 | 你该做的 |
|------|------|---------|
| **git + GitHub/GitLab** | 版本控制 | 每个项目一个 repo，commit message 写清 |
| **conda / mamba** | 环境管理 | 每个项目一个 `environment.yml` |
| **Docker / Singularity** | 环境封装 | 集群跑用 Singularity（HPC 友好）|
| **Snakemake / Nextflow** | 流水线 | 多步骤计算自动化（DFT→后处理→画图）|
| **Jupyter + nbconvert** | 笔记本自动化 | 重要 notebook 转成脚本跑 |
| **DVC**（Data Version Control）| 大数据版本 | 数据集和模型权重版本化 |
| **Zenodo / figshare** | DOI 永久存档 | 论文发表时给代码+数据分配 DOI |

### 5.2 一个标准的科研项目结构

```
my_physics_project/
├── README.md              # 项目说明 + 如何复现
├── environment.yml        # conda 环境
├── data/                  # 原始数据（用 DVC 管理）
├── src/                   # 源代码
│   ├── __init__.py
│   ├── model.py
│   └── utils.py
├── notebooks/             # 探索性 Jupyter
│   └── 01_first_look.ipynb
├── scripts/               # 生产脚本
│   └── run_dft.sh
├── results/               # 输出（不进 git）
└── paper/                 # LaTeX 论文
    └── main.tex
```

---

## §6 一个完整的"我学会了"自检项目（2-4 周）

**目标**：把 `physics_demos.py` 的玩具级升级到科研级。选 1 个完成：

### 项目 A（凝聚态方向）：Ising 模型相变
1. 用 NumPy 实现 2D Ising 模型的 Metropolis 算法（项目 caltech demo 已有玩具版）
2. 扫描温度 T ∈ [1.0, 4.0]，计算磁化率 ⟨|m|⟩ 和比热 C
3. 画 ⟨|m|⟩ vs T，标出临界温度 $T_c = 2/\ln(1+\sqrt{2}) \approx 2.269$
4. 用 Bayesian 拟合确认相变类型
5. 写成 Jupyter notebook，放 GitHub，README 写清你的发现

### 项目 B（量子方向）：氢分子解离曲线
1. 用 PySCF 算 H₂ 在键长 0.3-3.0 Å 范围的总能量
2. 画能量 vs 键长曲线，找平衡键长（实验值 0.74 Å）
3. 算解离能（实验值 4.5 eV）
4. 对比 HF vs CISD vs CCSD 方法（看多体效应的重要性）
5. notebook 上 GitHub

### 项目 C（AI for Physics）：PINN 解 Poisson 方程
1. 用 PyTorch 实现一个最小 PINN（5 层 MLP，tanh 激活）
2. 解 $-u''(x) = f(x)$ 在 [0,1]，边界 $u(0)=u(1)=0$
3. 对比 PINN 解 vs 有限元解（SciPy）
4. notebook 上 GitHub
5. 这是 `ai_for_physics/` 主题的核心 demo（见该主题文档）

---

## §7 安装优先级清单（按月）

| 月 | 装 | 学 |
|----|-----|---|
| 1 | NumPy/SciPy/SymPy/matplotlib/Jupyter | §2 所有 demo |
| 2 | PySCF + Qiskit | 氢分子 + Bell 态 |
| 3 | LAMMPS 或 Quantum ESPRESSO（选方向）| 第一个 example |
| 4 | git + conda + GitHub | 建你的科研 repo |
| 6 | Snakemake 或 Nextflow | 自动化流水线 |
| 12 | DeepMD 或 NeuralPDE（AI for Physics）| 第一个 ML 势能 |
| 18 | MPI + Slurm（如果要用集群）| 第一个集群作业 |

---

## §8 常见坑与建议

### 🕳️ 坑 1：装一堆软件但都不深入
- ❌ 装了 QE + VASP + LAMMPS + GROMACS + Gaussian，每个只会跑 example
- ✅ 选 1 个方向（凝聚态 OR 量子化学 OR MD），把对应工具学到能改源码

### 🕳️ 坑 2：不写 README 和环境文件
- ❌ 半年后你自己都跑不起来自己的代码
- ✅ 每个项目必有 `README.md` + `environment.yml`

### 🕳️ 坑 3：Jupyter 用过头
- ❌ 把生产代码写在 notebook 里（不可复现、难调试）
- ✅ notebook 用于探索，定型后搬到 `src/*.py`

### 🕳️ 坑 4：追新工具忽视经典
- ❌ 听说 JAX 火就切 JAX，连 NumPy 都没学透
- ✅ NumPy + SciPy 是永恒地基，先透后扩

### 🕳️ 坑 5：不会读错误信息
- ❌ 报错就问 AI / Google
- ✅ 先读 traceback，定位是 API 用错（看官方文档）还是物理理解错

---

## §9 与你 AI 能力的衔接

你的 `work4ai` 已有 23+ AI 主题。直接可迁移：

| work4ai 能力 | 物理科研用途 |
|------------|------------|
| PyTorch（讲透PyTorch）| PINN、神经势能、神经网络量子态 |
| LLM/RAG（讲透LLM/RAG）| 文献综述自动化、实验数据语义查询 |
| 端侧部署（端侧AI压缩）| 边缘科学计算、嵌入式传感器 |
| 微调（讲透微调）| 用物理数据微调基础模型 |
| Agent（讲透Agent）| 自动化实验设计、自主科研 Agent |
| Transformer（讲透Transformer）| 等变神经网络（用于原子系统）|

**详见** `ai_for_physics/` 主题。

---

**完成日期**：2026-08-13
**配套**：[01_mathematics.md](01_mathematics.md) + [ai_for_physics/](../ai_for_physics/) + [EXPERT_PATH_2026.md](../EXPERT_PATH_2026.md)
