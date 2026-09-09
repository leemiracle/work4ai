# 可微物理引擎与可微编程：从 JAX-MD 到 Genesis

> **本卷第七章第三节**。如果说神经网络让 AI 学会了「从数据中拟合函数」，那么**可微物理（Differentiable Physics）**让 AI 学会了「从物理定律中求梯度」。这是 AI 与数学的黄金交叉点：它把两百年积累的连续介质力学、分析力学、最优控制理论，统一收编进自动微分（autodiff）的计算图里，让"物理仿真"本身变成一个可以被反向传播（backprop）训练的可优化对象。
>
> 本章从 1964 年 Wengert 的自动微分先驱论文出发，系统梳理自动微分原理、可微物理引擎谱系（Brax / Genesis / JAX-MD / DiffTaichi / PhiFlow / Mitsuba 3 / Warp / MuJoCo MJX）、可微 PDE 求解器与神经算子的关系、可微渲染、可微机器人控制，直到 2025–2026 年的最新前沿。所有 arXiv 编号均经一手核实。

---

## 1. 历史：可微模拟的思想谱系

「让物理仿真可微」并不是深度学习时代的发明，它的根扎在三个独立但又最终汇流的源头里。

**第一个源头是自动微分（Automatic Differentiation, AD）。** 1964 年，Wengert 在 *Communications of the ACM* 发表了《A Simple Automatic Derivative Evaluation Program》，第一次系统描述了如何把任意计算机程序分解为一组基本算子（加、乘、sin、exp……），再对每个算子套用链式法则，从而**精确地**（到机器精度，而非有限差分的截断误差）计算出程序的导数。Wengert 提出的就是今天所说的"前向模式（forward mode）自动微分"。几乎同期，控制论与最优控制学界发展出了"伴随方法（adjoint method）"——为了求解形如 $\min_\theta J(x_T(\theta))$ 的最优控制问题，人们推导出"伴随状态" $a(t)=\partial L/\partial x(t)$ 满足一个沿时间倒推的线性方程。这套伴随方法在 1970–80 年代被航空航天（轨迹优化）、石油（油藏反演）、气象（数据同化）等领域奉为圭臬，至今仍是大规模 PDE 反问题的主流梯度来源。

**第二个源头是机器学习里的反向传播。** Rumelhart、Hinton、Williams（1986）把链式法则倒过来用，得到 backpropagation 算法。令人惊叹的是：**backpropagation 在数学上就是伴随方法在离散时间、离散计算图上的特例**。但这两个社区长期互不相识——做 PDE 的人不知道神经网络的 autograd，做神经网络的人也不知道控制论早有 adjoint。这种"同一数学被两次发现"的现象，直到 2018 年 Neural ODE 才被彻底点破（见下）。

**第三个源头是图形学与物理动画。** 为了做布料、流体、软体动画的"反向设计"（给定目标形态，反推材料参数或受力），图形学社区从 2000 年代起就在研究"可微模拟"。但受限于当时的工具，每一篇论文都要**手写**伴随方程，极其痛苦且易错。

三股力量的真正汇流发生在 2017–2020 年。催化剂有三个：(1) JAX（Google，2018）把"函数式 + 自动微分 + XLA 编译"打包成一套 Python 框架，让任意数值代码都能 `jax.grad`；(2) PyTorch 的 `autograd` 让反向传播成为深度学习默认设施；(3) Chen、Rubanova、Bettencourt、Duvenaud 的 **Neural ODE** [arXiv:1806.07366](https://arxiv.org/abs/1806.07366)（NeurIPS 2018）用一篇论文明确指出：**通过 ODE 求解器做反向传播，等价于求解伴随 ODE**，从而把"可微连续动力学"与"神经网络训练"焊接在了一起。从那时起，"可微物理引擎"作为一类系统级软件开始爆发。

> **论文**：Chen et al., *Neural Ordinary Differential Equations* [arXiv:1806.07366](https://arxiv.org/abs/1806.07366)（NeurIPS 2018）。这是可微物理的"统一宣言"——它证明了 backprop 和 adjoint 是同一件事。

---

## 2. 自动微分原理：前向、反向与计算图

要理解可微物理引擎为何能"自动求梯度"，必须先吃透自动微分的两种模式。设有一个从参数到标量损失的函数 $L=g(f(x))$，中间变量为 $y=f(x)$，我们想求 $\partial L/\partial x$。

### 2.1 前向模式（Forward-mode / Jacobian-Vector Product, JVP）

前向模式与函数求值同步进行：在算 $y=f(x)$ 的同时，把"切向量" $\dot y=(\partial y/\partial x)\dot x$ 也一起往前推。对每个基本算子，导数也是已知的，于是链式法则沿计算方向逐步展开：

$$\dot y = \frac{\partial f}{\partial x}\dot x,\qquad \dot L = \frac{\partial g}{\partial y}\dot y.$$

一次前向传播就得到雅可比矩阵 $J=\partial L/\partial x$ 与给定方向 $\dot x$ 的乘积 $J\dot x$，即 **JVP**。它的代价约等于一次函数求值。若输入维度为 $n$、输出维度为 $m$，要拿到完整雅可比需要跑 $n$ 次 JVP——**前向模式适合 $n \ll m$（输入少、输出多）**，例如灵敏度分析中只有少数设计变量。

### 2.2 反向模式（Reverse-mode / Vector-Jacobian Product, VJP）

反向模式先做一次完整的前向求值并把所有中间变量存下来，然后**从输出端往输入端**反向传播"伴随" $\bar y=\partial L/\partial y$：

$$\bar y = \frac{\partial L}{\partial y},\qquad \bar x = \bar y\,\frac{\partial f}{\partial x}.$$

对每个节点，把上游传来的伴随乘以本节点的局部雅可比，得到传给下游的伴随。一次反向传播得到的是 $\bar x = (\partial L/\partial x)^\top \cdot 1$，即**雅可比的转置与一个向量的乘积 VJP**。对 $n\gg m$（输入多、输出少，例如百万参数、标量损失）只需一次反向就能拿到整个梯度向量——**这正是深度学习训练的标准配置**，也是 backpropagation 的本质。

> **核心洞察**：反向模式 AD = backpropagation = 离散伴随方法。三者是同一套链式法则的三种表述。可微物理引擎做的，就是把一整段物理仿真塞进这个反向传播的计算图里。

### 2.3 JAX 与 PyTorch 的内部机制

- **JAX** 采用**函数式、无副作用**的设计。`jax.grad(f)` 返回一个新函数，调用它时先 `jax.vjp` 构造前向计算图与所有 VJP 规则，再反向遍历。因为纯函数，JAX 可以做 `jit`（XLA 编译）、`vmap`（自动批处理）、`pmap`（多设备并行）与 `grad` 任意组合——这就是 Brax / JAX-MD 能在单张 TPU 上跑百万级并行环境的原因。JAX 的反向模式要求中间状态可序列化，因此对**不可微操作**（如 `argmax`、控制流）需要 `custom_vjp` / `stop_gradient` 显式处理。
- **PyTorch** 采用**命令式、动态图**。每次前向运算在 C++ 后端动态构建一个有向无环图（DAG），记录每个 `Tensor` 的 `grad_fn`；调用 `.backward()` 时沿 DAG 反向。好处是写起来像普通 Python，控制流天然支持；代价是动态图的开销与难以像 JAX 那样整体编译。

二者的可微物理库因此气质不同：**Brax / JAX-MD / MJX 走 JAX 函数式路线**（极致并行、易编译），**DiffTaichi / Genesis 走命令式 + 自研编译器路线**（更灵活、对 GPU kernel 控制更细）。

---

## 3. 可微物理引擎谱系

下表汇总当前主流可微物理引擎，每一行都经过 arXiv/官网一手核实：

| 引擎 | 出处 | 后端 | 可微范围 | 论文/出处 |
|---|---|---|---|---|
| **JAX-MD** | Google (Schoenholz) | JAX/XLA | 分子动力学全程可微 | NeurIPS 2020, [arXiv:1912.04232](https://arxiv.org/abs/1912.04232) |
| **Brax** | Google | JAX/XLA | 刚体（最大规模并行） | NeurIPS 2021 D&B, [arXiv:2106.13281](https://arxiv.org/abs/2106.13281) |
| **MuJoCo MJX** | Google DeepMind | JAX/XLA | 刚体（MuJoCo 的 JAX 重写） | MuJoCo 开源，MJX 随仓库发布 |
| **DiffTaichi** | MIT (Yuanming Hu) | Taichi (LLVM/CUDA) | 弹性体/流体/刚体通用 | ICLR 2020, [arXiv:1910.00935](https://arxiv.org/abs/1910.00935) |
| **PhiFlow** | TUM (Thuerey) | PyTorch/TensorFlow | 流体 PDE | ICLR 2020, [arXiv:2001.07457](https://arxiv.org/abs/2001.07457) |
| **Mitsuba 3** | EPFL (Jakob) | Dr.Jit (LLVM/CUDA) | 光传输（可微渲染） | 软件 v3.1.1, 2022（前作 Mitsuba 2: ACM TOG 2019） |
| **Warp** | NVIDIA | CUDA (Python) | 刚体/布料/FEM | NVIDIA 开源框架（无 arXiv） |
| **Genesis** | Genesis-Embodied-AI | Taichi | MPM/Tool 已可微，刚体规划中 | GitHub 2024（**无正式 arXiv 论文**） |

### 3.1 JAX-MD：可微分子动力学的起点

Schoenholz 与 Cubuk 的 JAX-MD [arXiv:1912.04232](https://arxiv.org/abs/1912.04232)（NeurIPS 2020）是"可微物理"概念最干净的实现。分子动力学的核心方程是牛顿第二定律 $m_i\ddot{\mathbf r}_i=-\nabla_i U(\mathbf r)$，其中 $U$ 是势能。传统 MD 包（LAMMPS、HOOMD）需要**手写**势能的梯度来算力。JAX-MD 的天才之处在于：**只写势能函数 $U$，力自动由 `jax.grad` 给出**：

$$\mathbf F_i = -\frac{\partial U}{\partial \mathbf r_i}\quad\text{(由 autograd 自动计算)}.$$

更进一步，整条仿真轨迹 $\{\mathbf r_0,\dots,\mathbf r_T\}$ 都是参数 $\theta$（如势能参数、初始构型）的可微函数，于是可以用梯度下降去**逆向设计材料**——给定目标宏观性质（如玻璃形成能力、自组装结构），反推微观势能参数。JAX-MD 提供 Lennard-Jones、Morse、Tersoff、Stillinger-Weber、EAM 等经典势，以及 Behler-Parrinello、图神经网络等神经势能，全部端到端可微。

### 3.2 Brax：大规模可微刚体

Freeman 等人的 Brax [arXiv:2106.13281](https://arxiv.org/abs/2106.13281)（NeurIPS 2021 Datasets & Benchmarks Track）把刚体动力学（铰接体、关节、接触）用 JAX 重写，能在单张 TPU/GPU 上并行跑数百万个环境步/秒。其设计哲学是"环境与学习算法编译到同一设备"——PPO/SAC 与物理仿真同在 XLA 计算图里，无需 CPU↔GPU 数据搬运。Brax 的可微性使其支持"直接策略优化"（对仿真求梯度直接更新策略），这是 GPU 并行可微仿真给强化学习带来的新范式。

### 3.3 Genesis：通用物理平台（重要勘误）

Genesis 由 Genesis-Embodied-AI 团队于 2024 年 12 月开源，定位为面向机器人/具身 AI 的**通用物理平台**，集成刚体、MPM（物质点法）、SPH（光滑粒子流体）、FEM（有限元）、PBD（位置约束）、Stable Fluid 多种求解器及其耦合，并原生支持光线追踪渲染与（部分）可微。性能上，单张 RTX 4090 跑 Franka 机械臂可达 4300 万 FPS。

> **⚠️ 勘误（一手核实）**：原始任务描述把 Genesis 关联到 "arXiv:2410.11498"。经直接抓取 arXiv 页面核实，**arXiv:2410.11498 是一篇等离子体物理论文**——Fabien Widmer 等人《Linear and Nonlinear Dynamics of Self-Consistent Collisionless Tearing Modes in Toroidal Gyrokinetic Simulations》（physics.plasm-ph，2024-10-15 提交），与 Genesis **毫无关系**。Genesis **没有正式的 arXiv 预印本**，其唯一引用是 GitHub 仓库（`@misc{Genesis, year=2024}`）。这是典型的"arXiv ID 不可臆测"（铁律#7）。Genesis 的技术细节散见其关联论文（FluidLab [arXiv:2303.02346]、SoftZoo [arXiv:2303.09555]、RoboGen [arXiv:2311.01455] 等）。

Genesis 的可微能力目前覆盖 MPM 求解器与 Tool Solver，刚体求解器的可微版本仍在开发中。它大量复用 Taichi 作为计算后端，与 DiffTaichi 一脉相承。

### 3.4 DiffTaichi：命令式可微编程

Hu 等人的 DiffTaichi [arXiv:1910.00935](https://arxiv.org/abs/1910.00935)（ICLR 2020）建立在 Taichi 编程语言之上。Taichi 用 Python 写"类 C 的命令式"代码，编译器自动将其降级为 LLVM（CPU）或 CUDA/Metal（GPU）kernel。DiffTaichi 的贡献是给这套命令式语言加上**自动微分**：它为每个 kernel 生成反向 kernel，并采用**双重方法（双反向传播）+ 检查点（checkpointing）** 来处理稀疏数据结构与巨大内存开销。DiffTaichi 演示了弹性体、流体、刚体的可微仿真，是命令式可微物理的奠基之作。

### 3.5 PhiFlow：可微流体

Holl、Thuerey、Koltun 的《Learning to Control PDEs with Differentiable Physics》[arXiv:2001.07457](https://arxiv.org/abs/2001.07457)（ICLR 2020）既是 PhiFlow 框架的奠基论文，也是"可微物理 + 神经网络"协同训练的范例。它把流体求解器（Navier-Stokes 的投影法）做成可微，再插入一个卷积网络做控制策略，二者共享梯度——神经网络学习"如何影响流场"，物理求解器提供"流场如何演化"的可微先验。PhiFlow 后台支持 PyTorch 与 TensorFlow。

### 3.6 Mitsuba 3：可微渲染

EPFL 的 Jakob 团队开发的 Mitsuba 3 建立在专用的 JIT 编译器 **Dr.Jit** 之上（前作 Mitsuba 2 发表于 ACM TOG 2019，doi:10.1145/3355089.3356498）。它能对**整条光传输路径**（相机姿态、几何、BSDF 材质、纹理、参与介质体积）求导，实现逆向渲染（inverse rendering）——从照片反推场景参数。这是可微物理思想在"光的物理"上的延伸，是 3D 重建、材质捕获、数字孪生的核心工具。Mitsuba 3 的可微渲染处理了路径采样这种**离散/随机**操作的梯度（通过专门的可微蒙特卡洛估计器），难度极高。

### 3.7 MuJoCo MJX 与 NVIDIA Warp

**MuJoCo MJX** 是 Google DeepMind 收购 MuJoCo 后用 JAX 重写的版本（MuJoCo XLA），把经典接触丰富的刚体引擎搬上 XLA，享受 JAX 的自动并行与可微能力。**NVIDIA Warp** 是 NVIDIA 用 Python 编写、编译到 CUDA 的高性能仿真框架，支持刚体、布料、FEM，强调与 Omniverse 的集成与生产级性能（开源，无 arXiv 论文）。

---

## 4. 可微 PDE 求解器：与神经算子的关系

可微物理与神经算子（Neural Operator）常被并列，但二者解决的是**对偶问题**：

- **可微 PDE 求解器**：保留经典数值方法（有限差分/有限元/谱方法），用 autograd 让整个求解过程可微，从而支持基于梯度的参数反演、最优控制。优点是**物理保真、可解释**；缺点是计算昂贵、内存随时间步线性增长。
- **神经算子（如 FNO）**：Li 等人的 Fourier Neural Operator [arXiv:2010.08895](https://arxiv.org/abs/2010.08895)（ICLR 2021）直接学习从函数空间到函数空间的映射（参数→解算子），一旦训练好，推理比经典求解器快几个数量级。优点是**推理快**；缺点是需要大量数据、外推性依赖训练分布。

二者的融合是当前热点：用神经算子做**粗粒度快速预测**，用可微物理做**精细校正与梯度来源**；或用可微物理生成训练数据来训练神经算子。

> **论文**：Li et al., *Fourier Neural Operator for Parametric Partial Differential Equations* [arXiv:2010.08895](https://arxiv.org/abs/2010.08895)（ICLR 2021）。

### 4.1 PINN 的可微视角

物理信息神经网络（Physics-Informed Neural Network, PINN；Raissi、Perdikaris、Karniadakis，*J. Computational Physics* 378:686–707, 2019）用神经网络逼近 PDE 解 $u(x,t)$，把 PDE 残差（如 $\partial_t u + \mathcal{N}[u]=0$）作为损失项。PINN 之所以能"嵌入物理"，靠的正是 autograd：用 `jax.grad` / PyTorch autograd 对网络输出求时空导数，构造 PDE 残差。**PINN 本质上是可微编程在 PDE 上的一个特例**——只不过它求导的对象是神经网络，而不是数值求解器本身。可微 PDE 求解器则更进一步：连网格、时间步进、线性求解都进计算图。

### 4.2 应用

- **流体**：PhiFlow、DiffTaichi 做 Navier-Stokes 反演（从烟雾序列反推初始涡量场）。
- **固体**：DiffTaichi、Genesis MPM 做弹性体/弹塑性体参数标定。
- **电磁**：可微 FDTD 把时域有限差分做成可微，用于超材料逆向设计。

---

## 5. 可微渲染

可微渲染（Differentiable Rendering）是可微物理在"光"上的对应物：渲染方程

$$L_o(\mathbf x,\omega_o)=\int_{\Omega^+} L_i(\mathbf x,\omega_i)\,f_r(\omega_i,\omega_o)\,(\omega_i\cdot\mathbf n)\,d\omega_i$$

是一个关于场景参数（几何 $\mathbf x$、材质 $f_r$、光源）的高维积分。Mitsuba 3 通过 Dr.Jit 把蒙特卡洛路径采样过程做成可微，能对上式求梯度。难点在于**可见性（visibility）** 是不连续的——几何边界处积分核突变，梯度不存在。现代可微渲染用边缘采样（edge sampling）或投影法（如 Loubet et al. 的可微光栅化）来构造有意义的"广义梯度"。可微渲染支撑了从单张照片重建材质、几何、光照的逆向管线，是 3D 内容生成（NeRF/3DGS/生成式 3D）的下游标定工具。

---

## 6. 可微物理与机器人

可微物理在机器人领域的杀手级应用是 **sim-to-real 与形态优化**。

### 6.1 可微仿真用于控制

传统强化学习靠"试错+无梯度策略梯度"在仿真里学策略，样本效率低。可微物理给出了一条捷径：**直接对仿真求梯度，用基于梯度的优化更新策略或控制器**。例如可微模型预测控制（Differentiable MPC）把滚动时域优化的内层求解做成可微，外层策略网络通过梯度学习如何设定 MPC 的代价权重。

### 6.2 形态学优化（Morphological Optimization）

可微物理的真正威力在于"**软体机器人设计**"：给定任务（如爬行、抓取），同时优化机器人的**形态**（形状、材料分布）与**控制**（充气时序）。SoftZoo [arXiv:2303.09555](https://arxiv.org/abs/2303.09555) 与 DiffuseBot 等工作用可微物理 + 生成模型，自动"繁育"出适应特定环境的软体机器人。这超越了传统"先定形态再学控制"的范式。

### 6.3 实战：sim-to-real 的梯度桥梁

Genesis、Brax、MJX 都瞄准"在 GPU 上并行跑成千上万个机器人实例，用可微仿真缩小仿真与现实的差距（domain randomization + 可微校正）"。2025 年的可微仿真已成为人形机器人策略训练的基础设施之一。

---

## 7. 可微科学计算生态

### 7.1 JAX 生态

JAX 不仅是可微物理的载体，本身是一个完整的科学计算栈：**Optax**（优化器）、**Flax**（神经网络）、**Haiku**（DeepMind 的函数式 NN）、**jax-md**（分子动力学）、**jax-finufft**（非均匀 FFT）、**Diffrax**（可微 ODE/SDE 求解器，Neural ODE 的工程化）。这套生态的统一哲学是"一切皆纯函数，一切皆可 `grad/jit/vmap`"。

### 7.2 Julia DifferentialEquations.jl + Zygote

Julia 语言以**多重派发（multiple dispatch）** 和"两语言问题"的解决著称。Chris Rackauckas 的 **DifferentialEquations.jl** 是目前最全面的 ODE/SDE/DDE/DAE 求解器套件；**Zygote.jl** 是 Julia 的源到源自动微分。二者结合形成 **SciML（Scientific Machine Learning）** 生态：Universal Differential Equations（UDE）把神经网络嵌入 ODE 右端项，用可微求解器同时学习数值项与神经项。SciML 是 PINN/Neural ODE 在科学计算上的工程化集大成者。

### 7.3 语言之争

- **JAX（函数式 AD）**：极致并行与编译，适合大规模批量仿真，调试较难。
- **Taichi（命令式 AD）**：贴近物理学家直觉，GPU kernel 控制精细，生态较新。
- **Julia（多重派发 + 源到源 AD）**：科学计算表达力最强，性能接近 C，但社区规模小。
- **Swift for TensorFlow（已终止）**：Google 曾试图把 AD 做进语言层面，但 2021 年项目终止——教训是"语言级 AD 工程量巨大，且没有足够用户规模支撑"。可微编程更适合作为**库**而非**语言**来演进。

---

## 8. 核心技术深讲

### 8.1 通过仿真的反向传播：离散伴随

设仿真由时间步进算子 $\Phi$ 定义：$\mathbf x_{t+1}=\Phi(\mathbf x_t,\theta)$，损失 $L(\mathbf x_T)$ 只依赖终态。对参数求梯度：

$$\frac{\partial L}{\partial\theta}=\sum_{t=0}^{T-1}\underbrace{\frac{\partial L}{\partial\mathbf x_T}\prod_{\tau=t+1}^{T-1}\frac{\partial \mathbf x_{\tau+1}}{\partial\mathbf x_\tau}}_{\text{伴随 }a_{t+1}}\cdot\frac{\partial \mathbf x_{t+1}}{\partial\theta}.$$

定义伴随 $a_t=\partial L/\partial\mathbf x_t$，则递推 $a_t=a_{t+1}\,(\partial\mathbf x_{t+1}/\partial\mathbf x_t)$，沿时间倒推。这正是 backprop-through-time，也是离散伴随方法。**内存代价 $O(T)$**（要存所有中间态），这是可微物理的"原罪"。缓解手段：**检查点（checkpointing）** 把 $O(T)$ 降到 $O(\sqrt T)$，或**可逆仿真（reversible integration）** 用可逆时间积分避免存中间态。

### 8.2 Neural ODE 的连续伴随

当仿真由 ODE $\dot{\mathbf x}=f(\mathbf x,t,\theta)$ 给定时，Chen 等人 [arXiv:1806.07366](https://arxiv.org/abs/1806.07366) 推导出连续伴随方程：

$$\frac{d a}{dt}=-a^\top\frac{\partial f}{\partial\mathbf x},\qquad \frac{\partial L}{\partial\theta}=-\int_{t_0}^{t_1}a(t)^\top\frac{\partial f}{\partial\theta}\,dt.$$

通过反向求解伴随 ODE，可用 $O(1)$ 内存反向传播过任意黑盒 ODE 求解器。这是可微物理"内存友好"的理论基石。

### 8.3 刚体接触的可微处理

刚体接触的难点是**非光滑性**：碰撞瞬间速度发生跳跃。标准模型是**互补问题（Linear/Nonlinear Complementarity Problem, LCP/NCP）**：接触力 $\mathbf c\ge 0$、非穿透约束 $g(\mathbf x)\ge 0$、且互补条件 $\mathbf c\odot g(\mathbf x)=0$（二者不能同时为正）。对这样一个含不等式的系统直接求导是不可行的。主流处理方案有三：

1. **软化/惩罚接触（soft contact）**：用光滑的指数/样条势能近似硬接触，牺牲物理保真换取可微性（Brax、许多游戏物理引擎的默认做法）。
2. **隐式微分 KKT 条件**：把互补问题的解看作 KKT 系统的不动点，用隐函数定理对其求导 $\partial\mathbf x^*/\partial\theta=-(\partial G/\partial\mathbf x)^{-1}(\partial G/\partial\theta)$，可保持物理保真但实现复杂。
3. **随机化/ smoothed NCP**：对接触的法向做概率松弛，得到有意义的期望梯度。

这是可微物理最活跃也最难的研究前沿之一。

### 8.4 流体的可微（SPH 与 Navier-Stokes）

光滑粒子流体动力学（SPH）把连续场用粒子核函数插值：密度 $\rho_i=\sum_j m_j W(\mathbf r_i-\mathbf r_j,h)$，压力由状态方程 $p=k(\rho-\rho_0)$ 给出，压力力 $-\nabla p$。所有这些算子都是粒子位置的光滑函数，**天然可微**——这就是 Genesis、DiffTaichi 用 SPH 做可微流体的原因。相对地，基于网格的投影法（解压力 Poisson 方程）可微化需要对线性求解器做隐式微分，更重但更精确。

### 8.5 隐式时间积分与隐函数定理

向后欧拉 $\mathbf x_{t+1}=\mathbf x_t+\Delta t\,f(\mathbf x_{t+1})$ 需解非线性方程 $G(\mathbf x_{t+1})=\mathbf x_{t+1}-\mathbf x_t-\Delta t\,f(\mathbf x_{t+1})=0$（通常用牛顿法）。对其求导用**隐函数定理**：若 $G(\mathbf x^*,\theta)=0$，则

$$\frac{\partial\mathbf x^*}{\partial\theta}=-\left(\frac{\partial G}{\partial\mathbf x}\right)^{-1}\frac{\partial G}{\partial\theta}.$$

这把"求雅可比的逆"从 $O(n^3)$ 的高斯消元，转化为"解一个线性系统"，是可微隐式求解器（含可微 FEM、可微牛顿）的核心技巧。

### 8.6 梯度的病理：混沌与不可微

可微物理不是万能药。Metz、Freeman、Schoenholz、Kachman 在《Gradients Are Not All You Need》中指出：对**混沌系统**（如湍流、多体引力），仿真对初始条件的敏感性指数放大，导致梯度方向爆炸式振荡，反向传播得到的梯度毫无意义。这是可微物理在长时序、高雷诺数场景失效的根本原因，也是无梯度方法（进化、强化学习）仍有生存空间的原因。

> **论文**：Metz et al., *Gradients are Not All You Need* [arXiv:2111.05803](https://arxiv.org/abs/2111.05803)。

---

## 9. 应用案例

1. **材料微观结构逆向设计**：用 JAX-MD 的可微 MD，给定目标宏观弹性模量，梯度反推原子间势能参数或粒子"贴片"几何（King et al., *PNAS* 121(27):e2311891121, 2024，"Programming patchy particles"）。
2. **风洞参数反演**：用可微流体求解器，从实验测得的流场照片反推边界条件或物面粗糙度，比传统伴随方法实现成本低一个数量级。
3. **机器人形态优化**：SoftZoo [arXiv:2303.09555](https://arxiv.org/abs/2303.09555) 在可微物理中同时优化软体机器人的形态与步态，自动搜索出适应沙地、水、雪的最优设计。
4. **数字人/服装仿真**：Dress-1-to-3 [arXiv:2502.03449](https://arxiv.org/abs/2502.03449)（ACM TOG 2025）用扩散先验 + 可微物理，从单张图像生成可直接仿真的 3D 服装。

---

## 10. 可微编程语言与库的对比

| 系统 | AD 范式 | 优势 | 短板 |
|---|---|---|---|
| **JAX** | 函数式 reverse-mode | `jit/vmap/grad` 正交组合，极致并行 | 调试难，副作用受限 |
| **Taichi** | 命令式 reverse-mode（自研编译器） | 贴近物理直觉，稀疏数据结构强 | 生态新，文档少 |
| **Julia + Zygote** | 源到源 reverse-mode | 表达力最强，科学计算生态厚 | 社区小，二进制依赖 |
| **PyTorch autograd** | 动态图 reverse-mode | 主流，易用，控制流天然 | 难整体编译，并行不如 JAX |
| **Swift for TensorFlow** | 语言级 AD（已终止） | 理论优美 | 2021 终止，无后续 |

---

## 11. 2025–2026 关键前沿（均经 DBLP 一手核实）

- **DiffGen**（IROS 2025）：用可微物理仿真 + 可微渲染 + 视觉语言模型，自动生成机器人演示数据。
- **SAM-RL**（IJRR 2025）：感知驱动的 model-based RL，用可微物理 + 可微渲染做主动感知与策略学习。
- **Differentiable Physics-Neural Models for Non-Markovian Closures** [arXiv:2511.21369](https://arxiv.org/abs/2511.21369)（2025）：可微物理 + 神经网络学习粗粒化仿真的非马尔可夫闭合项。
- **Dress-1-to-3** [arXiv:2502.03449](https://arxiv.org/abs/2502.03449)（ACM TOG 2025）：单图→可仿真 3D 服装。
- **Physics-Grounded Differentiable Simulation for Soft Growing Robots** [arXiv:2501.17963](https://arxiv.org/abs/2501.17963)（RoboSoft 2025）：面向藤蔓式软体生长机器人的可微仿真。
- **evoxels** [arXiv:2507.21748](https://arxiv.org/abs/2507.21748)（2025）：体素化微结构模拟的可微物理框架。
- **DiffPhysCam** [arXiv:2508.08831](https://arxiv.org/abs/2508.08831)（2025）：可微物理相机仿真，用于逆向渲染与具身 AI。

趋势判断：2025–2026 的可微物理正从"单一求解器可微"走向"**多物理耦合 + 可微渲染 + 生成模型**"的三位一体（Genesis 是这一趋势的旗舰），并与大模型结合做数据飞轮（DiffGen/SAM-RL）。

---

## 12. 代码示例：用 JAX-MD 跑可微分子动力学

下面三段代码均可独立运行（`pip install jax jax-md`，CPU 即可）。它们展示了可微物理最核心的三件事：**力 = 势能的自动梯度**、**仿真轨迹对参数可微**、**用梯度逆向设计**。

### 示例 1：势能 → 力（autograd 的魔力）

```python
import jax
import jax.numpy as jnp
from jax_md import space, energy, quantity

# 开放边界，2D 空间
displacement_fn, shift_fn = space.free()

# 100 个粒子随机初始化
R = jax.random.uniform(jax.random.PRNGKey(0), (100, 2), minval=0.0, maxval=10.0)

# 只写势能函数 —— 力自动由 autograd 给出
energy_fn = energy.lennard_jones_pair(displacement_fn, sigma=1.0, epsilon=1.0)
force_fn = quantity.force(energy_fn)   # 内部即 -jax.grad(energy)

print("E =", energy_fn(R))
print("|F|^2 =", jnp.sum(force_fn(R) ** 2))
```

关键点：`quantity.force` 内部就是 $-\nabla U$，由 `jax.grad` 自动生成。传统 MD 包要手写 LJ 力的解析表达式，这里零手写导数。

### 示例 2：仿真轨迹对势能参数可微

```python
from jax_md import simulate, minimize

dt, T = 1e-3, 100
# NVT（恒温）Langevin 动力学
init, apply = simulate.nvt_langevin(energy_fn, shift_fn, dt, kT=0.5)

def trajectory_final_energy(epsilon):
    e_fn = energy.lennard_jones_pair(displacement_fn, sigma=1.0, epsilon=epsilon)
    init_, apply_ = simulate.nvt_langevin(e_fn, shift_fn, dt, kT=0.5)
    state = init_(jax.random.PRNGKey(1), R)
    for _ in range(T):
        state = apply_(state)
    return e_fn(state.position)   # 终态势能 = 参数 epsilon 的可微函数

# 直接对势能参数 epsilon 求梯度
grad_eps = jax.grad(trajectory_final_energy)(1.0)
print("dE_final/d_epsilon =", grad_eps)
```

这行 `jax.grad` 穿透了 100 步 Langevin 积分器——整条轨迹都对 $\epsilon$ 可微。这就是"可微物理"的全部魔法。

### 示例 3：用梯度逆向"设计"目标能量极小构型

```python
# 把初始位置当作可优化变量，用梯度下降找能量极小构型
@jax.jit
def step(R, lr=1e-2):
    g = jax.grad(energy_fn)(R)        # 能量对位置的梯度
    return R - lr * g                 # 梯度下降

R_opt = R
for i in range(200):
    R_opt = step(R_opt)
    if i % 50 == 0:
        print(f"step {i}: E = {energy_fn(R_opt):.4f}")
```

把"找能量极小"从手写共轭梯度，变成一行 `jax.grad` + 标准优化器。把 `R` 换成势能参数、把 `energy_fn(R)` 换成"目标宏观性质的负值"，这就是材料逆向设计。

> **延伸**：将示例 2 的损失改为"终态位置距目标位置的均方误差"，就得到了**可微物理做控制**的最小原型——这正是 Brax/MJX 上机器人策略梯度训练的内核。

---

## 13. 给用户的建议：可微物理是 AI + 数学的黄金交叉

对你的定位（应用数学研究型工程师、零数学基础起步、偏好可视化与工程落地），可微物理几乎是为你量身定制的切入点：

1. **它把最优化、分析力学、PDE、概率拧成一股绳**。学可微物理会逼你同时啃下链式法则、伴随方法、隐函数定理、互补问题——这些都是应用数学的核心装备，而且每一步都有**可视化的物理对应**（粒子排布、流场、布料褶皱），不会陷入纯符号推导的枯燥。
2. **工程入口极低**：从 JAX-MD 的三行代码起步，`pip install` 即可跑通，不需要超算。建议路线：JAX-MD 官方 cookbook（LJ 极小化 → NVT 仿真 → 神经网络势能）→ PhiFlow 流体反演 → Brax/MJX 刚体控制 → DiffTaichi 软体设计。
3. **研究机会密集**：可微接触（互补问题的可微化）、混沌系统的可靠梯度、可微物理 + 生成模型的耦合，都是 2025–2026 公开的硬核开放问题，适合作为长期研究方向。
4. **与你的 world-ai4sci-math 卷天然衔接**：可微物理是 02-ai4science（材料/流体/气候）与 04-synthesis（超越纯概率 LLM）的工程桥梁——"让物理定律进入梯度"正是回应你"LLM 只是概率性的，一切受限于物理数学公理"命题的技术落点。

一句话：**别把可微物理当成又一个 AI 流派，把它当成"用 autograd 重新发现两百年数学物理"的入口。**

---

## 📌 进一步阅读

- **入门（代码优先）**：JAX-MD 官方 cookbook 与 colab notebooks（[github.com/jax-md/jax-md](https://github.com/jax-md/jax-md)）；PhiFlow 教程（[github.com/tum-pbs/PhiFlow](https://github.com/tum-pbs/PhiFlow)）。
- **奠基论文**：Neural ODE [arXiv:1806.07366](https://arxiv.org/abs/1806.07366)；DiffTaichi [arXiv:1910.00935](https://arxiv.org/abs/1910.00935)；JAX-MD [arXiv:1912.04232](https://arxiv.org/abs/1912.04232)；Brax [arXiv:2106.13281](https://arxiv.org/abs/2106.13281)；PhiFlow [arXiv:2001.07457](https://arxiv.org/abs/2001.07457)。
- **进阶理论**：Baydin et al., *Automatic Differentiation in Machine Learning: a Survey*, JMLR 2018（前向/反向模式的完整梳理）；Griewank & Walther, *Evaluating Derivatives*, SIAM（AD 的数学圣经）。
- **可微渲染**：Mitsuba 3 文档（[mitsuba.readthedocs.io](https://mitsuba.readthedocs.io)）；Vicini et al. 可微光传输系列。
- **SciML**：Chris Rackauckas 的 SciML 教程与 Universal Differential Equations 论文。
- **系统软件**：Genesis 文档（[genesis-world.readthedocs.io](https://genesis-world.readthedocs.io)）；Taichi 语言文档；NVIDIA Warp 文档。

---

## ✍️ 思考题

1. **前向 vs 反向的本质**：为什么在"百万参数、标量损失"的深度学习里必须用反向模式？如果反过来是"3 个设计变量、千万维输出"的灵敏度分析，应该用哪种模式？请从雅可比矩阵的形状推导代价。
2. **伴随 = backprop 的统一**：请把一阶离散伴随递推 $a_t=a_{t+1}(\partial\mathbf x_{t+1}/\partial\mathbf x_t)$ 与 RNN 的 backprop-through-time 逐项对应，指出二者在哪一步完全等价。
3. **可微接触的两难**：硬接触互补问题不可微，软化接触牺牲保真。请设计一个实验，量化"软化程度"对反演精度与梯度可用性的权衡曲线。提示：用 Genesis 或 DiffTaichi 的软体接触，扫描惩罚刚度。
4. **Neural ODE 的内存红利**：连续伴随为何能做到 $O(1)$ 内存？请用检查点的 $O(\sqrt T)$ 内存做对比，说明在多长的仿真时序上连续伴随开始显著占优。
5. **混沌的梯度失效**：请用 JAX-MD 跑一个高能量 LJ 系统（混沌），对初始位置求 100 步后的梯度，观察梯度范数随步数的指数增长。基于此，提出一种"在混沌系统中仍可获得有用梯度"的工程策略（如伴随截断、随机化、或改用无梯度优化）。

---

<!-- delegate 直接写入，2026-07-20 -->
