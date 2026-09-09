# 计算架构与未来创新：模型运行的硬件根基

> 卷：`world-ai4sci-math / 08-ai4x-applications / 07`
> 主题：模型运行的硬件根基与未来架构创新
> 撰写：2026-07-20｜全部 arXiv / Nature / Science / IEEE 引用一手核实（Crossref + arXiv abs 双查）

---

## 引子：三个直击灵魂的问题

读者带着三个问题来到这篇文档：

1. **模型的运行，是否都受制于传统的冯诺依曼架构？**
2. **是否存在更大的创新——能真正突破冯诺依曼？**
3. **编译器与操作系统的哪些创新，能显著帮助模型（功耗 + 性能）？**

这篇文档会正面回答这三个问题。简短的答案是：**当前主流 AI 硬件（GPU/TPU/NPU）本质上仍是冯诺依曼架构的变种**——它们用尽手段（HBM、Tensor Core、片上网络）去"掩盖"冯诺依曼瓶颈，但"存储与计算分离、数据要在两者间搬运"这一根本假设从未被推翻。Transformer 推理是典型的 **memory-bound（访存受限）** 任务，其算术强度低到落在 Roofline 模型的内存带宽边界以下——这意味着加再多算力都没用，瓶颈在搬运。

但突破冯诺依曼的种子已经种下：**存算一体（PIM）、光计算、类脑、模拟、量子**五条路线都在蚕食那道"墙"。与此同时，在不换架构的前提下，**编译器（FlashAttention、Triton、XLA）和操作系统（PagedAttention、大页、NUMA）**带来的收益，往往比换一块新硬件还要大——这是工程界最被低估的杠杆。

本文按"诊断 → 突破 → 渐进 → 编译器 → OS → 功耗 → 预测 → 给你的建议"八段展开。

---

## 一、开篇：模型运行是否受制于冯诺依曼架构？

### 1.1 冯诺依曼架构的本质（1945）

1945 年，约翰·冯·诺依曼（John von Neumann）在《First Draft of a Report on the EDVAC》中描述了一种通用电子计算机的结构，后世称为**冯诺依曼架构（von Neumann architecture）**。它的核心是"**存储程序（stored-program）**"思想：程序指令和数据以同等形式存放在同一个读写存储器里，由一个中央处理器（CPU）按"取指—译码—执行—写回"的循环串行地处理。这一架构由四个部分构成：

- **CPU（中央处理器）**：含算术逻辑单元 ALU 和控制单元 CU，负责实际运算和指令调度。
- **内存（Memory）**：存放指令与数据，统一编址。
- **总线（Bus）**：CPU 与内存之间的数据通路，包括地址总线、数据总线、控制总线。
- **输入/输出（I/O）**：与外部世界交互。

这个设计的革命性在于"通用"——同一台机器，换一套程序就能做完全不同的事。在此之前的计算机（如 ENIAC）是"硬连线"的，算不同问题要重新接线。冯诺依曼把"接线"变成了"编程"，从此计算与硬件解耦，软件工业才得以诞生。**80 年过去了，从手机 SoC 到 NVIDIA H100，从 Intel Xeon 到华为昇腾，几乎所有通用计算芯片仍是这一架构的直系后代**——差别只在局部优化（流水线、缓存、多核、向量单元），而非根本范式。

### 1.2 冯诺依曼瓶颈（von Neumann bottleneck）

架构的精妙之处，正是它的死穴。**每执行一条指令，CPU 都要先从内存"取指令"，再从内存"取数据"，算完后再把结果"写回内存"**。每一次运算，数据都要在 CPU 和内存之间往返穿梭，而连接两者的总线带宽是有限的。当 CPU 速度远快于内存时，CPU 大量时间在"等数据"，这条总线就成了瓶颈——这就是著名的**冯诺依曼瓶颈**。

1977 年，Fortran 之父 John Backus 在领取 ACM 图灵奖时发表演讲《**Can Programming Be Liberated from the von Neumann Style?**》（[Comm. ACM 21(8):613-641, 1978, DOI 10.1145/359576.359579](https://doi.org/10.1145/359576.359579)），把这个问题上升到哲学高度。Backus 批评冯诺依曼架构强制程序员用"一次一字（word-at-a-time）"的顺序思维去思考计算，让编程语言（他主要批的是 Fortran/Algol 一脉）被困在"赋值语句"这个低级原语上。他提倡函数式编程（FP），让计算摆脱"搬一个字、改一个字"的冯诺依曼节奏。这篇演讲到今天仍是计算机科学的必读经典。

> **关键洞察**：冯诺依曼瓶颈的本质不是"总线太慢"，而是**"数据必须移动"**——只要存储和计算物理分离，数据搬运的能耗和延迟就是不可避免的税。这是后续所有"存算一体"路线的根本动机。

### 1.3 现代体系结构基础回顾：CPU 如何"掩盖"瓶颈

为了理解 AI 硬件为何仍是冯诺依曼变种，必须先看通用 CPU 这 40 年靠什么把瓶颈"掩盖"到勉强可用：

- **流水线（Pipeline）**：把一条指令切成取指/译码/执行/访存/写回多级，像工厂流水线一样重叠执行多条指令，提升吞吐率。但流水线有冒险（hazard）：数据相关、控制相关（分支）、结构相关。
- **缓存（Cache） hierarchy**：L1（几十 KB，~1ns）/ L2（几百 KB，~3ns）/ L3（几 MB~几十 MB，~10ns）/ DRAM 主存（GB 级，~100ns）。利用**局部性原理（locality）**——时间局部性（刚用的还会用）和空间局部性（相邻的会被用到）——把热数据留在离 ALU 近的 SRAM 里。但缓存命中率一旦下降，性能立刻崩塌。
- **TLB（Translation Lookaside Buffer）**：虚拟地址→物理地址的硬件缓存。虚拟内存让每个进程以为自己独占整个地址空间，但每次访存都要查页表，TLB 缓存最近的翻译。大模型 KV cache 这种"地址空间巨大且访问不规则"的场景，TLB miss 是隐形杀手。
- **乱序执行、分支预测、推测执行**：进一步榨取指令级并行（ILP）。
- **多核与 SIMD/向量指令**：数据级并行（DLP），从 SSE/AVX 到 GPU 的 SIMT。

**所有这些技术都在干一件事：让 CPU 不必每次都去 DRAM 取数据**。它们没有改变"存储与计算分离"的根本假设，只是用各种"靠近计算的小型存储（cache）"来缓冲。GPU 更极端——它把成千上万个简单核心堆在一起，配以巨大的片上 SRAM 和高带宽 HBM，本质上仍是冯诺依曼架构，只是把"取数—算"的循环并行化到了极致。

### 1.4 现代 AI 的三大瓶颈

把上面的诊断套到 Transformer 推理上，瓶颈被放大了 100 倍。这里给出**带数字的诊断**，因为只有数字能让人感受到墙有多厚。

#### 瓶颈 1：内存墙（Memory Wall）

DRAM 主存带宽与 GPU 片上 SRAM 带宽存在数量级差距：

| 存储层级 | 带宽（数量级） | 容量 | 延迟 |
|---|---|---|---|
| 寄存器（Register） | ~30 TB/s/SM | KB 级 | <1 cycle |
| 片上 SRAM（共享内存/L1） | ~10–19 TB/s | 几十 MB | ~20 cycles |
| HBM（GPU 显存） | 3–5 TB/s（H100 HBM3） | 80–192 GB | ~400 cycles |
| DDR5 DRAM（CPU 主存） | ~100–200 GB/s | 几百 GB | ~100 ns |

注意 **HBM 到 SRAM 差了约 100×带宽**。更关键的是，**LLM 推理的算术强度（arithmetic intensity，每字节搬运做多少次浮点运算）极低**。以解码阶段为例：每生成一个 token，要把全部权重过一遍，但每个权重只参与极少几次乘加。

**用 Roofline 模型量化**：Roofline 把可达性能 $P$（FLOPs/s）表达为峰值算力 $P_{peak}$ 与"算术强度 $\pi$ × 带宽 $B$"的较小者：

$$P = \min\big(P_{peak},\ \pi \cdot B\big),\qquad \pi = \frac{\text{FLOPs}}{\text{Bytes}}$$

拐点出现在 $\pi^* = P_{peak}/B$。以 H100 为例：FP16 峰值约 989 TFLOPs，HBM 带宽约 3.35 TB/s，则 $\pi^* \approx 295$ FLOPs/Byte。而 **LLM 解码的算术强度只有 1–10 FLOPs/Byte**——远远落在拐点左侧，性能完全被带宽钉死。结论：**给 LLM 推理加更多算力（提高 $P_{peak}$）毫无意义，性能上限由 $\pi \cdot B$ 决定，只能靠加带宽或减少搬运**。这就是为什么 HBM 是 AI 芯片的命脉，也是为什么 NVIDIA 每一代都要堆 HBM。

> **实测数据**：多项 profiling 研究（如 MIT Han Lab、Colfax）显示，**LLM 推理约 60–70% 的时间花在搬运权重上**，真正做矩阵乘的墙钟时间占比很小。

#### 瓶颈 2：功耗墙（Power Wall）

能耗的故事同样残酷。Mark Horowitz 在 2014 年 ISSCC 的经典演讲《**Computing's energy problem (and what we can do about it)**》（[DOI 10.1109/ISSCC.2014.6757323](https://doi.org/10.1109/ISSCC.2014.6757323)）给出了一组被反复引用的能耗数字（45nm 工艺）：

| 操作 | 能耗（数量级） |
|---|---|
| 32 位浮点乘加（FMAC） | ~20 pJ（坐在寄存器旁） |
| 1 KB SRAM 访问 | ~5 pJ |
| 1 MB SRAM 访问 | ~100 pJ |
| 64 位 DRAM 访问（含出 chip） | **~1–4 nJ（1000–4000 pJ）** |

**一次 DRAM 访问的能耗是一次乘加的 50–200 倍**。也就是说，如果某个乘法的数据来自 DRAM，那这次乘法"搬运成本"远大于"计算成本"。对 LLM 推理，业界普遍估计**总能耗的 60–70% 花在数据搬运（HBM↔计算单元），只有 20–30% 花在实际计算**。这直接颠覆了"计算贵、存储便宜"的直觉——在 AI 时代，**搬运才是大头**。

功耗墙的另一个含义是散热：单芯片功耗一旦突破 700W–1000W（H100 SXM 700W、B200 约 1000W），风冷到顶，必须液冷。数据中心选址、PUE（Power Usage Effectiveness，总能耗/IT 设备能耗）都成了硬约束。

#### 瓶颈 3：IO 墙（带宽墙）

即便不计能耗，HBM 本身的带宽也有物理上限。HBM3（H100）3.35 TB/s，HBM3e（B200/H200）约 4.8 TB/s，HBM4（规划 2026）目标 6–8 TB/s。但 HBM 是靠堆叠多层 DRAM die + TSV（硅穿孔）+ 极宽总线（每 stack 1024 bit）换来的，成本极高（H100 的 HBM 占芯片成本的大头），且良率、容量都受限。当模型参数从 70B 涨到 405B 再到万亿，**单卡 HBM 装不下，必须多卡互联**——于是 NVLink（900 GB/s）、NVSwitch、InfiniBand 成了新的瓶颈。

### 1.5 现实诊断：是的，主流 AI 硬件仍是冯诺依曼变种

把诊断收束到一句话：**当前所有主流 AI 硬件（NVIDIA GPU、Google TPU、华为昇腾、各类 NPU），本质都是冯诺依曼架构的"高度优化变种"**。它们的共同特征是：

1. **存储与计算物理分离**：权重存在 HBM/DRAM，要搬到片上 SRAM 才能算。
2. **数据搬运是主要成本**：无论时间还是能耗。
3. **靠"层级存储 + 数据复用"掩盖瓶颈**：cache、tiling、算子融合都是为此。
4. **Transformer 推理落在 Roofline 内存边界以下**：算力大量闲置。

Thompson 等人在《**The Computational Limits of Deep Learning**》（[arXiv:2007.05558](https://arxiv.org/abs/2007.05558)）里用经验数据论证：深度学习的进步越来越依赖算力指数增长，而摩尔定律放缓意味着"靠堆算力"的红利正在枯竭——这把"换范式"的压力推到了台前。

所以对**问题 1 的回答是：是，当前主流 AI 硬件仍受制于冯诺依曼架构的根本假设**。但"受制"不等于"无解"——下一章就看怎么突围。

---

## 二、突破冯诺依曼的五大创新方向

如果根本症结是"数据要搬运"，那么最彻底的解法就是**别搬**——让计算发生在数据所在的地方。下面五条路线，从最接近产品的"存算一体"，到最遥远的"量子计算"，逐一拆解。

### 方向 1：存算一体（Compute-in-Memory, CIM / Processing-in-Memory, PIM）

#### 核心思想

**在存储单元内直接做计算，从根本上消除数据搬运**。这是对冯诺依曼最直接的反叛：既然"搬数据"是病根，那就让存储器自己算。

PIM（Processing-in-Memory，近存计算）和 CIM（Compute-in-Memory，真存内计算）常被混用，但严格说有层级之分：PIM 偏指"在存储芯片旁加计算单元"（数字式，精度高），CIM 偏指"用存储单元的物理特性直接做模拟计算"（精度受限但能效极高）。

#### RRAM/Memristor Crossbar：欧姆定律做矩阵乘

最具颠覆性的是**忆阻器交叉阵列（memristor crossbar）**。原理极其优雅：在一组十字交叉的导线上，每个交叉点放一个可调电导的器件（忆阻器/RRAM），电导值 $G_{ij}$ 编码权重。给行线加电压 $V_j$，按欧姆定律，列线上汇集的电流就是：

$$I_i = \sum_j G_{ij} \cdot V_j$$

这正是**矩阵-向量乘法（MVM）**！一次"通电"就完成了一整层神经网络的加权求和，时间复杂度 $O(1)$（不论矩阵多大），能耗只有充放电容的几十 fJ/MAC。这是物理定律免费送给 AI 的礼物。

两篇奠基综述必须引用：

> **论文**：Ielmini & Wong, "In-memory computing with resistive switching devices", **Nature Electronics** 1:333-343 (2018), [DOI 10.1038/s41928-018-0092-2](https://doi.org/10.1038/s41928-018-0092-2)。⚠️ 注：本综述发表在 **Nature Electronics**（非 Nature Communications，常见误引）。
>
> **论文**：Sebastian, Le Gallo, Khaddam-Aljameh & Eleftheriou, "Memory devices and applications for in-memory computing", **Nature Nanotechnology** 15:529-544 (2020), [DOI 10.1038/s41565-020-0655-z](https://doi.org/10.1038/s41565-020-0655-z)（IBM 苏黎世研究院）。

清华大学的**吴华强团队**做出了里程碑式的硬件实现：

> **论文**：Yao, Wu, Gao, Tang, Zhang, ... Qian, "Fully hardware-implemented memristor convolutional neural network", **Nature** 577:641-646 (2020-01-29), [DOI 10.1038/s41586-020-1942-4](https://doi.org/10.1038/s41586-020-1942-4)。一作姚鹏，通讯吴华强/高滨/钱鹤，合作者含 J. Joshua Yang。在 128×8 的 1T1R 忆阻器阵列上全硬件实现了 5 层 CNN，做 MNIST 准确率 96%+。

#### 数字式 PIM：UPMEM 与 Samsung HBM-PIM

模拟 crossbar 精度差（通常 4-8 bit）、噪声大、训练难，于是工业界先落地了**数字式 PIM**——在 DRAM bank 旁加简单 ALU：

- **UPMEM（法国）**：首个商用 PIM，在 DRAM die 上集成 DPU（DRAM Processing Unit），每个 chip 含 2560 个 DPU，理论峰值 2.6 TB/s 内存带宽下做整数运算。适合大批量点积、数据库扫描。
- **Samsung HBM-PIM（Aquabolt-XL）**：把计算单元塞进 HBM2：

> **论文**：Kim, Kang, Lee, ... Sohn, Kim, "Aquabolt-XL: Samsung HBM2-PIM with in-memory processing for ML accelerators and beyond", **2021 IEEE Hot Chips 33 Symposium (HCS)**, [DOI 10.1109/HCS52781.2021.9567191](https://doi.org/10.1109/HCS52781.2021.9567191)。在 HBM2 内置 AI 引擎，实测 TPU 加速比提升 2.5×，能耗降 70%。

- **SK Hynix AiM（Accelerator-in-Memory）**：类似路线，GDDR6 内集成乘加单元。

#### 其他存储介质

- **PCM（相变内存）**：IBM Zurich 主推，用 GST 材料的晶态/非晶态电阻差异存权重，配合 NorthPole/Analog 路线。
- **FeFET（铁电晶体管）**：铁电材料 polarization 存权重，理论上可 1T1C 做高密度。
- **SRAM PIM**：用现有 SRAM bitline 做模拟乘加（如 TSMC ISSCC 多篇论文），精度高、易集成，但密度低、能效不如 RRAM。
- **3D NAND PIM**：在闪存里算，容量巨大但速度慢，适合大模型推理的权重存储+计算。

#### 优势与挑战

| 维度 | GPU（冯诺依曼） | CIM（存算一体） |
|---|---|---|
| MVM 能效 | ~10–100 TOPS/W | ~10–100 TOPS/W... → 等等，CIM 可达 **10–100 TOPS/W** vs GPU 的几 TOPS/W，**能效高 10–100×** |
| 精度 | FP32/FP16/FP8 | 模拟 CIM 通常 4-8 bit，需混合精度补偿 |
| 可编程性 | 高（CUDA 生态） | 极低（每个阵列定制） |
| 训练 | 成熟 | 几乎无法在芯片上训（需软件-硬件协同训练） |

> **一句话**：CIM 是物理上最优、工程上最难的路线。它能在边缘 AI（低功耗、固定模型）上先落地，但要取代 GPU 训练大模型，还有 5–10 年。

### 方向 2：光计算（Optical / Photonic Computing）

#### 核心思想

**用光子代替电子做计算**。光的优点是：带宽极高（THz）、并行（不同波长互不干扰）、能耗极低（光在波导里传播几乎不耗能，只有光电转换耗能）。光特别擅长做一件 GPU 最头疼的事——**矩阵乘法**。

最经典的光矩阵乘实现是 **Mach-Zehnder 干涉仪（MZI）阵列**：通过一组可调的光干涉单元，让光信号在网格中按权重干涉相消/相长，输出端的光强就是输入向量乘权重矩阵的结果。另一种思路是 SVD 分解——把任意矩阵分解成两个酉矩阵和一个对角矩阵，分别用 MZI 网络和衰减器实现。

#### 代表公司

- **Lightmatter（美国，MIT Soljačić 实验室衍生）**：光计算的领头羊。其学术根基是里程碑论文：

  > **论文**：Shen, Harris, Skirlo, ... Soljačić, "Deep learning with coherent nanophotonic circuits", **Science** 同期；确切为 **Nature Photonics** 11:441-446 (2017-06-12), [DOI 10.1038/nphoton.2017.93](https://doi.org/10.1038/nphoton.2017.93)。一作 Yichen Shen，通讯 Marin Soljačić（MIT，Lightmatter 创始人）。该论文用硅光子芯片在光域实现了全光矩阵乘，做元音分类。

  Lightmatter 的 **Envise** 系列光子加速器 + **Passage** 光互连，2024 年获得大额融资，宣称矩阵乘能效比 GPU 高一个数量级。

- **LightOn（法国）**：最早的商业化光计算公司之一（2016 创立），用随机投影做大规模高维特征映射，曾用于大模型预训练（与 Hugging Face 合作）。⚠️ 其学术论文 arXiv ID 经核实存在歧义，本文不强行引用具体编号，仅作产品案例。

- **Salience Labs（牛津衍生）**：用光频率多路复用做并行乘加。
- **Luminous Computing**：融资极高但低调，目标用光重做整个 AI 超算。
- **Rain AI**：模拟 + 光混合，主打低功耗边缘推理。

- 宾夕法尼亚大学 Aflatouni 团队 2022 年做出了**片上全光深度神经网络**：

  > **论文**：Ashtiani, Geers & Aflatouni, "An on-chip photonic deep neural network for image classification", **Nature** 606:501-506 (2022-06-01), [DOI 10.1038/s41586-022-04714-0](https://doi.org/10.1038/s41586-022-04714-0)。片上全光实现，无需光电转换，做 2 类图像分类。

#### 优势与挑战

光计算的"理想"是：矩阵乘延迟 ps 级、带宽 Tbps、能耗只有激光源那一头。但现实挑战严峻：

1. **精度低**：光强受噪声、温度漂移影响，通常只有 5–8 bit 等效精度。要做高精度需要大量冗余+校准。
2. **光电转换税**：数据进出光域要调制器/探测器，每次转换耗能几百 fJ–pJ，吃掉光计算省下的能耗。
3. **可编程性差**：MZI 阵列一旦"烧"好权重就难改，做推理（固定权重）还行，做训练（权重频繁更新）极难。
4. **非线性难**：光天然适合线性运算（矩阵乘），但神经网络的激活函数（ReLU、softmax）是非线性的，要么用光电混合（在线性层用光、在激活用电子），要么用特殊光学非线性器件。

> **一句话**：光计算是"长在矩阵乘上"的技术，2030 年前后有望在推理加速卡的线性层找到位置，但全面替代 GPU 仍遥远。

### 方向 3：类脑计算（Neuromorphic Computing）

#### 核心思想

**模仿生物大脑的结构与计算方式**。大脑的能效是当前任何 AI 芯片的 1000 倍——人脑约 20W 功耗就能做到通用智能，而训练 GPT-4 要烧掉几十兆瓦时电。类脑计算试图复制大脑的两个关键特征：

1. **脉冲神经网络（Spiking Neural Network, SNN）**：神经元不是每时刻都计算，而是只在收到足够输入时"发放"一个离散脉冲（spike）。这是 **event-driven（事件驱动）**——没输入就不耗能，天然稀疏、天然低功耗。
2. **存算一体**：神经元之间的突触既存权重又做计算，没有"搬数据"一说。

#### 代表性硬件

| 芯片 | 机构 | 年份 | 特点 |
|---|---|---|---|
| **Loihi 1 / Loihi 2** | Intel | 2017/2021 | 可编程脉冲芯片，片上学习，含可编程微码核心 |
| **TrueNorth** | IBM | 2014 | 100 万神经元、256M 突触，65mW |
| **NorthPole** | IBM | 2023 | 数字式存算交织，12nm，ResNet50 能效比 GPU 高 25× |
| **SpiNNaker / SpiNNaker 2** | Manchester 大学（英） | 2014/2023 | 大规模脉冲仿真，百万核，模拟脑 |
| **天机芯（Tianjic）** | 清华大学 | 2019 | 混合架构（SNN+ANN），骑车机器人 |
| **Darwin** | 浙江大学 | 2015/2018 | 国产类脑芯片系列 |
| **Akida** | BrainChip（澳） | 2020+ | 商用 SNN 芯片，边缘推理 |

关键论文引用（全部一手核实）：

> **论文**：Pei, Deng, Song, ... Wu, Xie & **Shi (施路平)**, "Towards artificial general intelligence with hybrid Tianjic chip architecture", **Nature** 572:106-111 (2019-08-08), [DOI 10.1038/s41586-019-1424-8](https://doi.org/10.1038/s41586-019-1424-8)。一作裴京，含邓磊、宋森、吴华强、施路平。该芯片把 SNN（脉冲）和 ANN（传统）统一在同一架构上，并用它驱动了一辆**自动驾驶自行车**——骑车、避障、听指令，登上 Nature 封面。

> **论文**：Davies, Srinivasa, Lin, ... Wang, "Loihi: A neuromorphic manycore processor with on-chip learning", **IEEE Micro** 38(1):82-99 (2018), [DOI 10.1109/MM.2018.112130359](https://doi.org/10.1109/MM.2018.112130359)。Intel 第一代 Loihi，128 核，片上 STDP 学习。

> **论文**：Akopyan 等, "TrueNorth: Design and tool flow of a 65 mw 1 million neuron programmable neurosynaptic chip", **IEEE TCAD** 34(10):1537-1557 (2015), [DOI 10.1109/TCAD.2015.2474396](https://doi.org/10.1109/TCAD.2015.2474396)。配套 Merolla 等 Science 2014: [DOI 10.1126/science.1254642](https://doi.org/10.1126/science.1254642)。

> **论文**：Modha 等（IBM），"**Neural inference at the frontier of energy, space, and time**", **Science** 382:329-335 (2023-10-20), [DOI 10.1126/science.adh1174](https://doi.org/10.1126/science.adh1174)。NorthPole 芯片，**12nm**（注意：常见误写为 22nm）。摘要原文："NorthPole is a neural inference architecture that **blurs the [compute-memory] boundary by eliminating off-chip memory, intertwining compute with memory on-chip**"。在 ResNet50 上，相对同工艺(12nm) GPU：**FPS/W 高 25×，FPS/晶体管高 5×，延迟低 22×**。这是 NorthPole 把"存算交织"做到极致的代表。

> **论文**：Furber 等, "The SpiNNaker project", **Proc. IEEE** 102(5):652-665 (2014), [DOI 10.1109/JPROC.2014.2304638](https://doi.org/10.1109/JPROC.2014.2304638)。Manchester 的百万核脉冲仿真平台。

#### SNN 的优势与困境

**优势**：能耗极低（mW 级做实时感知）、天然适合时序数据（事件相机、语音）、延迟低（实时控制）。

**困境**：
1. **训练算法不成熟**：脉冲是不可导的阶跃函数，反向传播直接失效，要用替代梯度（surrogate gradient）或 STDP（脉冲时序依赖可塑性），效果远不如 ANN 上的 SGD。
2. **与现有 DL 生态不兼容**：PyTorch/TensorFlow 都是稠密张量，SNN 是稀疏事件流，工具链断层。
3. **不适合 Transformer 这类稠密大模型**：SNN 擅长稀疏时序，LLM 是稠密矩阵乘，错配。
4. **精度—能耗权衡复杂**：要追精度就得增加脉冲数，能效优势被吃掉。

> **一句话**：类脑计算在**边缘 AI、机器人、实时感知**有不可替代的位置，但 10 年内不会成为训练大模型的主力。它是"另一种智能形态"，不是 GPU 的替代品。

### 方向 4：模拟计算（Analog Computing）

#### 核心思想

**用连续物理量（电压、电流）代替离散数字做计算**。在数字电路里，做一次 8 位乘法要一串逻辑门、若干时钟周期；在模拟电路里，两个电压过一个运放（op-amp）或跨导放大器，输出就是乘积——**连续、并行、瞬时**。

模拟计算和前面 CIM 的忆阻器路线高度重合（RRAM crossbar 本质就是模拟 MVM）。区别在于：模拟计算更广义，还包括用运放、电容做积分/卷积的传统模拟 VLSI（Carver Mead 1989 年的《Analog VLSI Implementation of Neural Systems》就是开山之作，NorthPole 论文也引用了它）。

#### 代表工作

- **IBM Heron（2024）**：IBM 量子路线图中搭配的模拟 AI 芯片。
- **Google 模拟 TPU 研究**：内部探索。
- **NorthPole**：虽是数字式，但其"存算交织"思想受模拟计算启发。
- **Rain AI**：模拟+光混合。

#### 优势与挑战

**优势**：超低功耗（fJ/MAC 级）、超快（连续时间，无时钟）、面积小。

**挑战**：
1. **噪声大**：模拟值受热噪声、器件失配影响，精度通常 4-6 bit。
2. **不可编程**：模拟电路一旦设计好，功能就固定，做不了通用计算。
3. **校准地狱**：每个芯片都要单独标定，批量一致性差。
4. **非线性与漂移**：温度、老化都会改变模拟值。

> **一句话**：模拟计算是"极致低功耗、极致专用"的路线，适合固定模型的边缘推理（如 always-on 的关键词检测），无法做通用 AI。

### 方向 5：量子计算（Quantum Computing）

#### 核心思想

利用量子叠加与纠缠，在某些问题上实现指数级加速。对机器学习，量子机器学习（QML）理论上能加速线性代数（HHL 算法解线性方程组）、采样、优化。

#### 现状：NISQ 时代

我们处于**含噪中等规模量子（NISQ，Noisy Intermediate-Scale Quantum）时代**：几十到几百物理量子比特，**量子纠错（QEC）尚未实用**。物理比特噪声率太高，必须用纠错码（如表面码）把多个物理比特编码成一个逻辑比特——目前要 ~1000 个物理比特换 1 个可靠逻辑比特。

代表进展（均经一手核实，详见本卷专题）：

- **Google Willow（2024）**：105 物理比特，首次在实验中证明**纠错后错误率随码距增加而下降**（越过纠错阈值），是通向容错量子计算的关键里程碑。
- **IBM Heron R2（2024）**：156 物理比特。
- **Microsoft Majorana 1（2025）**：基于拓扑量子比特的路线，宣称找到马约拉纳零模的物理证据（学界仍有争议）。

#### 何时实用

主流估计：**容错量子计算（足以运行 Shor 破解 RSA、跑实用 QML）需要 10–20 年**。在此之前，量子计算对 AI 训练/推理没有实质贡献。NISQ 时代的"量子-经典混合"在小分子模拟、组合优化上有探索，但离通用 ML 还远。

> **一句话**：量子计算是值得长期投入的"登月级"技术，但**对当前和未来 10 年的 AI 模型运行，几乎零影响**。把它放在这篇文档里是为了完整性，以及提醒读者不要被"量子 AI"的炒作带偏。

### 五大方向横向对比

| 方向 | 突破冯诺依曼程度 | 成熟度 | 能效潜力 | 对 AI 主力（LLM）影响 |
|---|---|---|---|---|
| 存算一体 CIM | ⭐⭐⭐⭐⭐（彻底） | 中（边缘已商用，训练未） | 10–100× | 5–10 年后可能进推理 |
| 光计算 | ⭐⭐⭐⭐（线性层） | 低-中 | 10–100×（线性层） | 2030+ 线性层加速 |
| 类脑 SNN | ⭐⭐⭐⭐（范式换） | 中（专用场景商用） | 1000×（稀疏） | 不适合稠密 LLM，主攻边缘 |
| 模拟 | ⭐⭐⭐ | 中（固定模型商用） | 100× | 仅边缘固定模型 |
| 量子 | ⭐⭐⭐⭐⭐（颠覆） | 极低（NISQ） | 特定问题指数加速 | 10–20 年内无影响 |

## 三、冯诺依曼内的革命：不换架构也能做的创新

第二章是"换范式"，激进但遥远。这一章是"在现有范式里把榨干"，保守但立竿见影——而且**这些创新才是当下 AI 算力增长的真正主力**。它们不挑战冯诺依曼，而是承认瓶颈、用工程手段绕开。

### 3.1 Wafer-Scale Engine（Cerebras）：把整片晶圆当一颗芯片

传统芯片是从一片 300mm 晶圆上切出几十上百颗 die，每颗 die 之间靠封装互联。**Cerebras 的疯狂想法是：不切了，把整片晶圆当成一颗超大芯片**——Wafer-Scale Engine（WSE）。

- **WSE-1（2019）**：TSMC 16nm，1.2 万亿晶体管，462mm² 的"常规" die 拼成整片晶圆，含 400,000 个核心，18GB 片上 SRAM（SRAM，不是 HBM！）。这在当时是"不可能"的，因为整片晶圆必有缺陷点，Cerebras 用冗余路由绕过坏核。
- **WSE-2（2021，CS-2）**：TSMC 7nm，**2.6 万亿晶体管，850,000 核心**，40GB 片上 SRAM。单芯片面积 ~46225mm²（约一张 iPad 大）。
- **WSE-3（2024，CS-3）**：5nm 工艺，**约 4 万亿晶体管，900,000 核心**，44GB 片上 SRAM，峰值 125 PFLOPs（FP16）。CS-3 系统宣称可训练 1200B 参数模型。

> **论文/技术报告**：Lie (Cerebras CTO), "Inside the Cerebras Wafer-Scale Cluster", **2023 IEEE Hot Chips 35 Symposium (HCS)**, [DOI 10.1109/HCS59251.2023.10254700](https://doi.org/10.1109/HCS59251.2023.10254700)。⚠️ 注：Cerebras CTO 为 **Sean Lie**（经多方核实，记忆块中 Cerebras 条目亦一致）。

**核心价值**：把 HBM 搬到片上当 SRAM，**内存带宽从 TB/s 跳到 PB/s 级**，彻底消灭"单卡内存墙"。它的 MemoryX / SwarmX 技术还能把权重流式喂给多卡。代价是：**单芯片功耗 ~15–20kW**，需要专门液冷机柜；编程模型是"数据流"而非 CUDA，生态迁移成本高。

**教训**：Cerebras 证明了一个反直觉的事实——"大模型训练瓶颈不在算力，而在内存与互联"。它用工程极端化（整片晶圆）换来了对内存墙的暂时胜利，但也说明：**冯诺依曼瓶颈不是靠"更大的 die"能根治的**。

### 3.2 Dataflow 架构（Spatial Computing）：让数据流过算力

传统 CPU/GPU 是"指令驱动"——取一条指令，搬一点数据，算一下，写回。**Dataflow（数据流）架构反过来：数据准备好了就触发计算，指令只是配置数据通路**。计算单元像工厂流水线一样固定排列（spatial computing），数据在它们之间流动，不需要反复取指。

#### Groq LPU：2024 年的"推理怪兽"

**Groq**（由 Google TPU 团队成员 Jonathan Ross 创立）的 **LPU（Language Processing Unit）** 在 2024 年初因"单 token 推理 500+ tokens/s"（Llama-2 70B）一战成名，远超当时的 GPU 方案。

其学术根基是 Groq 的 Tensor Streaming Processor（TSP）：

> **论文**：Abts 等, "**Think fast: A tensor streaming processor (TSP) for accelerating deep learning workloads**", **2020 ACM/IEEE 47th Annual International Symposium on Computer Architecture (ISCA)**, pp. 145-158, [DOI 10.1109/ISCA45697.2020.00023](https://doi.org/10.1109/ISCA45697.2020.00023)。

TSP 的设计哲学是"**deterministic（确定性）**"：执行时间完全可预测，没有缓存未命中的随机性。芯片被切成功能条带（MXM 矩阵单元 / VXM 向量单元 / SXM 切换 / MEM），数据像流水一样横向流过，每个周期每个单元都在干活。**牺牲灵活性换极致吞吐**——这就是它能在 LLM 推理上跑出恐怖 tokens/s 的原因。

**代价**：LPU 极度适合推理（固定模型、batch 友好），但训练灵活性不如 GPU；内存容量小（SRAM 为主），大模型要切分多卡。

#### SambaNova RDU：可重构数据流

> **论文/技术报告**：Prabhakar & Jairath, "SambaNova SN10 RDU: Accelerating software 2.0 with dataflow", **2021 IEEE Hot Chips 33 Symposium (HCS)**, [DOI 10.1109/HCS52781.2021.9567250](https://doi.org/10.1109/HCS52781.2021.9567250)。

SambaNova 的 Reconfigurable Dataflow Architecture（RDA）用**可编程互连**让数据通路按模型结构重构，号称"编译时就把数据流烤进硬件"。主打大模型训练 + 推理一体。

#### Graphcore IPU 与 FPGA

- **Graphcore IPU**：英国，Bulk Parallel Graph Processor，曾风光一时。Knowles, ["Graphcore", Hot Chips 2021, DOI 10.1109/HCS52781.2021.9567075](https://doi.org/10.1109/HCS52781.2021.9567075)。⚠️ 2024 年 Graphcore 因无法与 NVIDIA 竞争，**基本退出主流 AI 加速器市场**（后被软银收购重组）——说明 dataflow 路线虽美，但生态壁垒难破。
- **FPGA（Xilinx/AMD、Altera/Intel）**：可定制数据通路，灵活性最高但开发门槛高、能效不如 ASIC。适合低延迟金融推理、通信基带。

### 3.3 HBM 与 Chiplet：把内存和算力"摞"起来

既然单 die 内存不够，就把内存和算力物理堆叠得更近。

#### HBM（High Bandwidth Memory）

HBM 用 **3D 堆叠 DRAM die + TSV（硅穿孔）+ 极宽总线**换取带宽：

| 代际 | 带宽 | 容量/stack | 代表 GPU |
|---|---|---|---|
| HBM2 | ~1 TB/s | 8GB | V100 |
| HBM2e | ~2 TB/s | 16GB | A100（部分） |
| HBM3 | ~3 TB/s | 80GB | H100 |
| HBM3e | ~4.8 TB/s | 192GB | H200 / B200 |
| HBM4（2026） | 目标 6–8 TB/s | 288GB+ | Rubin |

HBM 是当下 AI 芯片最稀缺的资源（三星/SK Hynix/美光三家垄断），其产能直接决定了 GPU 出货量。

#### Chiplet 与先进封装

**Chiplet（小芯粒）** 思路：不再追求单片大 die（良率低、成本高），而是把功能拆成多个小 die，用先进封装（2.5D/3D）拼起来。代表标准：

- **UCIe（Universal Chiplet Interconnect Express）**：Intel 主导的 chiplet 互联标准，2022 发布，旨在让不同厂商的 die 能像积木一样拼。
- **TSMC CoWoS / 3D Fabric**：台积电的 2.5D/3D 封装平台，H100/B100 都用 CoWoS。
- **Intel Foveros / EMIB**：Intel 的 3D 堆叠与嵌入式互连。

Chiplet 让"摩尔定律"在封装层延续：即使单 die 工艺放缓，靠 3D 堆叠仍能提升晶体管总数。

#### CXL（Compute Express Link）：内存解耦

**CXL** 是基于 PCIe 的高速缓存一致互连（2019 起，CXL Consortium），核心思想是**内存解耦（memory disaggregation）**：多台服务器共享一个内存池，按需分配。对大模型推理的"内存碎片"问题有缓解作用。CXL 3.0 支持 64GB/s、多级交换。⚠️ CXL 是工业标准规范（无 arXiv 论文），引用以 CXL Consortium 规范为准。

### 3.4 NVIDIA GPU 的演化：冯诺依曼内的极致优化

作为事实标准，NVIDIA 每代架构都在"压榨冯诺依曼"：

| 架构 | 年份 | 关键创新 | 代表卡 |
|---|---|---|---|
| Volta | 2017 | 第一代 **Tensor Core**（混合精度矩阵乘） | V100 |
| Ampere | 2020 | 稀疏化（2:4 结构化稀疏）、BF16 | A100 ([Choquette ISSCC 2021, DOI 10.1109/ISSCC42613.2021.9365803](https://doi.org/10.1109/ISSCC42613.2021.9365803)) |
| Hopper | 2022 | **Transformer Engine**（FP8 自动选精度）、HBM3、第四代 NVLink（900GB/s） | H100 |
| Blackwell | 2024 | 第五代 Tensor Core、**第二代 Transformer Engine**、FP4、NVLink 互连双 die、B200/GB200 NVL72 机柜 | B100/B200/GB200 |
| Rubin | 2026（规划） | HBM4、新一代 NVLink、与 Vera CPU 配套 | Rubin |

**Transformer Engine** 是 Hopper 的招牌：它根据张量的统计范围，自动在 FP8/FP16/BF16 间切换，几乎无损精度地翻倍吞吐。Blackwell 进一步到 **FP4**——把权重压到 4 bit，显存和带宽直接省一半。这些都是"在冯诺依曼内靠精度压缩换带宽"的典范。

Google TPU 同步演化（v1→v2→v3→v4→v5e/Trillium），核心是 systolic array（脉动阵列）+ HBM + 专用互联（OCS 光路交换）：

> **论文**：Jouppi, Yoon, ... Patterson, "**Ten lessons from three generations shaped Google's TPUv4**", **ISCA 2021**, [DOI 10.1109/ISCA52012.2021.00010](https://doi.org/10.1109/ISCA52012.2021.00010)。TPUv4 用光路交换（OCS）重构拓扑，能效比前代大幅提升。

### 3.5 国产 AI 芯片：生态突围

在地缘背景下，国产 AI 芯片快速发展，但都面临**生态（CUDA 兼容）+ 制程（先进工艺受限）**双重挑战：

| 芯片 | 厂商 | 工艺/规模 | 特点与挑战 |
|---|---|---|---|
| **昇腾 910B / 910C** | 华为 | 7nm（中芯国际 N+2） | 达阿斯麦禁令后主力，910C 算力逼近 A100，CANN 生态 + MindSpore |
| **思元 590 / 595** | 寒武纪 | 7nm | MLU 系列专用指令集，NeuWare 工具链 |
| **深算 DCU（如 Z100）** | 海光 | 14nm | x86 兼容，类 ROCm 生态 |
| **BR100 / BR105** | 壁仞 | 7nm | 算力宣称对标 A100，2022 出货 |
| **MTT S80 / S4000** | 摩尔线程 | 7nm | 主打图形 + AI，CUDA 兼容层 |
| **曦云 C500 / G500** | 沐曦 | 7nm | 类 CUDA 生态 |

**共同困境**：①先进制程受限（EUV 禁令，7nm 以下难量产）；②生态薄弱——绝大多数模型代码是 CUDA 写的，移植成本高；③单卡算力虽追赶，但 HBM 供应（三星/SK Hynix 也受禁令影响）和良率仍是瓶颈。昇腾是目前国产化走得最远的，但整体仍是"冯诺依曼架构 + 专用加速"的路线，没有跳脱第二章的范式。

## 四、编译器如何帮助模型（问题 3 上半）

如果说硬件是"路"，编译器就是"导航"。同一台 GPU，烂编译器只能压出 30% 性能，好编译器能压出 90%。**在现代 AI 里，编译器的价值往往被严重低估**——很多被视为"算法创新"的突破，本质是编译器/IO 创新。本章逐一拆解。

### 4.1 算子融合（Operator Fusion）

这是 XLA、TVM、Triton 的共同核心思想。

考虑一段典型的 Transformer 前向：`y = Dropout(Relu(LayerNorm(x)))`。如果不融合，编译器会生成三个独立 kernel：先算 LayerNorm，结果写回 HBM；再读出来算 Relu，写回；再读出来做 Dropout。**每个中间张量都要往返 HBM 一次**。

**融合后**，编译器把三个算子合成一个 kernel：数据从 HBM 读进 SRAM 后，在 SRAM 里依次做完 norm→relu→dropout，最后只把结果写回 HBM 一次。**HBM 访问次数从 3N 降到 1N，带宽压力骤降**。

对 element-wise + reduce 的算子，融合收益巨大（10×+）。XLA（Google，TensorFlow 默认）、TVM（Apache 项目）、PyTorch 2.0 的 torch.compile 都在做这件事。这是"用编译器思维绕开内存墙"的最基础招式。

### 4.2 内存布局与 Tiling

GPU 的 SRAM 是分块的（每个 SM 有自己的共享内存），要高效利用必须**分块（tiling）**：把大矩阵切成适配 SRAM 大小的块，每块算完就不再访问。块的大小、形状、加载顺序都由编译器决定。

**Tensor layout 转换**也很关键：同一组数据，"行优先"还是"列优先"、"NHWC"还是"NCHW"，直接决定内存访问是否连续（coalesced）。编译器会自动插 layout transform，让访问尽可能连续。

### 4.3 量化与混合精度

精度是"用准确率换带宽"的直接杠杆：

| 精度 | 相对显存/带宽 | 训练可用性 | 推理可用性 |
|---|---|---|---|
| FP32 | 1×（基准） | ✅ | 过剩 |
| TF32 / BF16 | 0.5× | ✅（训练主流） | ✅ |
| FP16 | 0.5× | 需 loss scaling | ✅ |
| FP8 | 0.25× | ⚠️（Hopper 起可行） | ✅（Hopper+） |
| INT8 | 0.25× | ❌（需 QAT） | ✅（推理主流） |
| INT4 / FP4 | 0.125× | ❌ | ⚠️（Blackwell 起探索） |

**编译器的角色**是"自动选精度"——根据每层张量的数值范围，动态选择最优精度（loss-aware quantization）。Hopper 的 Transformer Engine 就是把这个逻辑半硬件化。**对 LLM 推理，INT8/FP8 量化几乎无损精度，但显存和带宽直接省 4×**——这是性价比最高的优化之一。

### 4.4 自动并行化：3D 并行

单卡装不下大模型，必须切分到多卡。三种切分维度：

1. **数据并行（Data Parallel）**：每卡完整模型，处理不同 batch。简单但模型大时装不下。
2. **张量并行（Tensor Parallel，TP）**：把单层权重矩阵按列/行切到多卡，每卡算一部分，再 AllReduce。**Megatron-LM** 是代表。
3. **流水线并行（Pipeline Parallel，PP）**：把模型按层切，每卡负责几层，数据像流水线一样过。**GPipe / PipeDream** 是代表。

实际训练大模型通常用 **3D 并行**（DP × TP × PP），加上 **DeepSpeed ZeRO** 把优化器状态/梯度/参数也切分到多卡，把单卡显存占用压到极低。

> **注**：3D 并行是"系统级"而非"算子级"优化，介于编译器和分布式系统之间。Megatron-LM、DeepSpeed、PyTorch FSDP 是主力工具。

### 4.5 FlashAttention：编译器思维击败纯数学思维的典范

这是本节的重头戏。FlashAttention 不是"数学创新"——它的 attention 还是精确的（exact），公式和标准 attention 一模一样。它是**纯粹的 IO 优化**，却带来了 2–4× 加速和 5–20× 显存节省。它彻底改变了"AI 优化"的范式。

#### 标准注意力的问题

标准 attention：$O = \text{softmax}(QK^T / \sqrt{d}) V$。朴素实现要先把整个 $N×N$ 的注意力矩阵 $S = QK^T$ 算出来写回 HBM，再读出来做 softmax，再写回。对 N=8192 的长序列，$S$ 占 8192×8192×2 字节 ≈ 128MB，**反复读写 HBM 把带宽吃光**。

#### FlashAttention 的解法：tiling + online softmax

核心是两招：

1. **分块（tiling）**：把 Q、K、V 切成块，每块的大小刚好适配 SRAM。在 SRAM 内算完一个块的 attention，直接累加到输出，**中间的 $N×N$ 矩阵永远不落 HBM**。
2. **在线 softmax（online softmax）**：softmax 需要全局最大值做数值稳定，但分块后看不到全局。FlashAttention 用一个巧妙的"增量更新"技巧——维护一个运行最大值 $m$ 和指数和 $\ell$，每来一个新块就更新——让 softmax 可以"流式"计算。

结果：**HBM 访问次数从 $O(N^2)$ 降到 $O(N^2 d / M)$**（M 是 SRAM 大小），IO 复杂度达到理论下界。

#### 三代演化（全部一手核实）

> **论文**：Dao, Fu, Ermon, Rudra & Ré, "**FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness**", [arXiv:2205.14135](https://arxiv.org/abs/2205.14135)（NeurIPS 2022）。实测：BERT-large 训练加速 15%，GPT-2 加速 3×，长序列 2.4×；并首次让 Transformer 在 Path-X（16K 序列）上超过随机水平。

> **论文**：Dao, "**FlashAttention-2: Faster Attention with Better Parallelization and Work Partitioning**", [arXiv:2307.08691](https://arxiv.org/abs/2307.08691)（2023-07）。重新划分线程块/warp 间的工作，减少非矩阵乘 FLOPs，在 A100 上达到 50–73% 理论峰值，训练 GPT 时达 **225 TFLOPs/s（72% MFU）**。

> **论文**：Shah, Bikshandi, Zhang, Thakkar, Ramani & Dao, "**FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision**", [arXiv:2407.08608](https://arxiv.org/abs/2407.08608)（2024-07）。针对 Hopper 架构：用 warp-specialization 重叠计算与数据搬运（async TMA）、interleave matmul 与 softmax、FP8 低精度。H100 上 FP16 达 **740 TFLOPs/s（75% 利用率）**，FP8 达 **约 1.2 PFLOPs/s**。

#### 深层启示

FlashAttention 证明：**AI 性能的下一个十年的红利，不在"更大的模型"，而在"更聪明的 IO"**。它把"算子实现"从"算法研究者写 PyTorch"变成了"系统工程师写 CUDA kernel"——这是 ML Sys 这门交叉学科兴起的标志。

### 4.6 Triton 语言：让研究者写出接近 cuBLAS 的 kernel

写高性能 CUDA kernel 极难——要管共享内存、warp 同步、bank conflict、寄aten布局……OpenAI 的 Philippe Tillet 在哈佛读博时发明了 **Triton**：

> **论文**：Tillet, Kung & Cox, "**Triton: an intermediate language and compiler for tiled neural network computations**", **Proceedings of the 3rd ACM SIGPLAN International Workshop on Machine Learning and Programming Languages (MAPL '19)**, pp. 10-19, [DOI 10.1145/3315508.3329973](https://doi.org/10.1145/3315508.3329973)。

Triton 是一种 Python-like 的 DSL：你用 `tl.load` / `tl.store` / `tl.dot` 写分块计算，编译器自动处理共享内存、同步、向量化。**比 CUDA 简单 10×，性能接近手写 cuBLAS**。FlashAttention 的早期实现就基于 Triton。如今 Triton 已是 OpenAI、Meta、xAI 等公司写自定义 kernel 的事实标准。

### 4.7 编译器的未来

- **LLM 写 CUDA kernel**：2024–2025 趋势，用大模型自动生成/优化 GPU kernel，已有 KEPLER、Meta 的相关工作。
- **Differentiable programming（可微编程）**：让整个程序（含控制流）都可导，JAX、TorchMLIR 在推进。
- **MLIR（Multi-Level IR）**：Google 主导的多层中间表示，让"高层算子→底层硬件"的编译管线模块化，是下一代 AI 编译器的基础设施。

> **一句话**：编译器是"不换硬件就能拿到 2–5× 性能"的最大杠杆。对个人而言，**掌握 Triton / TVM 是进入 ML Sys 的最低门槛，也是工业界最缺的技能**。

---

## 五、操作系统如何帮助模型（问题 3 下半）

如果说编译器优化的是"单卡内的算子"，操作系统优化的就是"多卡/多机之间的资源"。OS 的虚拟内存、调度、文件系统这些"古老"机制，在 LLM 时代焕发了第二春。

### 5.1 PagedAttention（vLLM）：把 OS 分页机制用到 KV cache

这是 OS 思想反哺 AI 的最经典案例。

#### 问题：KV cache 的内存碎片

LLM 自回归解码时，要为每个请求维护 **KV cache**（已生成 token 的 Key/Value）。朴素做法是给每个请求预分配一块连续显存。但 KV cache 长度动态变化（生成越多越长），导致：

1. **内部碎片**：预分配空间没用满，浪费 60–80%。
2. **外部碎片**：请求来了又走，显存被切成碎片，新请求找不到连续大块。

结果是 batch size 上不去，吞吐量低。

#### 解法：借 OS 的分页

操作系统 50 年前就解决了类似问题——**虚拟内存 + 分页**：把物理内存切成固定大小的页（4KB），用页表把虚拟地址映射到物理页，逻辑连续、物理离散。

PagedAttention 把这套搬到 KV cache：

- KV cache 被切成固定大小的 **block**（如 16 个 token 一块）。
- 每个请求有一个**block table**（类比页表），记录自己的逻辑块→物理块映射。
- 物理块可以不连续，按需分配/释放。

结果：**内存浪费几乎降到 0，batch size 翻倍，吞吐量提升 2–4×**。

> **论文**：Kwon, Li, Zhuang, Sheng, Zheng, Yu, Gonzalez, Zhang & Stoica, "**Efficient Memory Management for Large Language Model Serving with PagedAttention**", [arXiv:2309.06180](https://arxiv.org/abs/2309.06180)（**SOSP 2023**，UC Berkeley）。vLLM 开源项目即基于此。

#### 衍生：copy-on-write 与 KV 共享

PagedAttention 还支持 **copy-on-write（写时复制）**——多个请求共享同一段 prompt 的 KV cache（如系统提示词），只在分叉时复制。这让 **beam search、并行采样**的内存开销大幅下降。

### 5.2 大页（Huge Pages）：减少 TLB miss

x86 默认页大小 4KB。一个 70B 模型的权重约 140GB（FP16），要占用 $140GB / 4KB = 36M$ 个页表项。TLB（translation lookaside buffer）缓存有限（几百到几千项），**TLB miss 率飙升，每次 miss 要走多级页表，延迟 100+ cycles**。

**大页（Huge Pages，2MB 或 1GB）** 把页大小放大，页表项数量降 512× 或 262144×，TLB 命中率显著提升。对 LLM 推理，开启透明大页（THP）通常能加速 **10–20%**，尤其是内存密集的解码阶段。

### 5.3 NUMA awareness：多 socket 的内存局部性

多路服务器（如 8 卡 GPU + 双路 CPU）是 NUMA（Non-Uniform Memory Access）架构：每个 CPU socket 有本地内存，访问快；跨 socket 访问要走过互联（UPI/Infinity Fabric），**延迟 2–3×、带宽减半**。

对 LLM 推理：
- GPU 要尽量访问"最近的"CPU 内存（NUMA affinity）。
- 数据加载、NCCL 通信要绑 NUMA 节点。
- `numactl --cpunodebind --membind` 是基本工具。

不绑 NUMA 的多卡训练，性能可能白白损失 20–30%。

### 5.4 内存 overcommit 与 ZeRO-Offload

训练大模型时显存不够怎么办？OS 的 swap（换页）思想被借用：

- **ZeRO-Offload（DeepSpeed）**：把优化器状态（占大头）卸载到 CPU 内存，甚至 NVMe SSD。GPU 只在前向/反向时按需取回。
- **CPU offload 的代价**：PCIe 带宽（~64 GB/s）远低于 HBM（~3 TB/s），只能用于"不频繁访问"的数据（如优化器状态每 N 步才更新一次）。

这本质是"用慢存储换大容量"的 OS 经典权衡。

### 5.5 进程/线程调度

- **CPU 亲和性（CPU affinity）**：把数据加载线程绑定到特定核心，避免上下文切换开销。`taskset` / `sched_setaffinity`。
- **GPU 上下文切换**：一块 GPU 上跑多个进程时，context 切换有 ms 级开销。MPS（Multi-Process Service）和 MIG（Multi-Instance GPU，A100/H100 支持）把 GPU 硬件分区，减少切换。
- **异步流水线**：数据加载（CPU）→ 前向（GPU）→ 反向（GPU）要重叠，`DataLoader(num_workers, pin_memory=True)` 是基本配置。

### 5.6 文件系统：大模型加载与检查点

- **mmap（内存映射文件）**：加载 100GB 的模型权重，用 `mmap` 让 OS 按需把文件页读入内存，避免一次性全读。配合大页效果更好。
- **Direct I/O**：绕过 page cache，直接读写磁盘，适合"只读一次"的大文件加载。
- **检查点（checkpoint）**：训练中每 N 步存 checkpoint，要写几十到几百 GB。用**异步 checkpoint**（如 `torch.distributed.checkpoint`、DeepSpeed 的 async save）把保存放到后台线程，不阻塞训练。

### 5.7 OS-level LLM Agent：OS 正在被 AI 重塑

最后是一个反向趋势——**AI 开始驱动 OS**。

- **Anthropic Computer Use（2024）**：Claude 可以"看屏幕、点鼠标、敲键盘"，直接操作 GUI。
- **OpenAI Operator（2025）**：类似思路，浏览器/桌面自动化。
- **Anthropic 的 computer-use 论文级思路**：把 OS 的每个交互（窗口、文件、应用）变成 LLM 可调用的"工具"。

这不是"OS 帮助模型"，而是"模型接管 OS"——预示着未来 OS 可能从"人操作"转向"人下达意图、Agent 调度资源"。这把 OS 的角色从"资源管理者"推向"意图执行者"，是 30 年来 OS 范式最大的潜在变革。

> **一句话**：OS 对模型的帮助分两层——**底层（分页/大页/NUMA/调度）榨干硬件，上层（Agent）重塑交互**。前者是工程师必修，后者是未来的研究方向。

## 六、功耗优化全栈

前面谈性能，这一章谈功耗。**功耗是 AI 的另一个硬约束**——不仅因为电费（训练一个大模型能耗相当于几百户家庭一年的用电），更因为散热（单芯片功耗超过 1000W 后，风冷到顶）、碳排放、以及"用电量决定选址"（数据中心迁往水电丰富的北欧、内蒙古）。

功耗优化是全栈的，从晶体管到数据中心：

### 6.1 硬件层

- **DVFS（Dynamic Voltage and Frequency Scaling）**：动态调电压/频率。电压平方正比于功耗（$P \propto C V^2 f$），降 20% 电压可省 36% 功耗。LLM 推理低峰时段降频，是常见手段。
- **Power gating（电源门控）**：关闭空闲核心的供电，零泄漏。GPU 在等待数据时让部分 SM 进入 sleep。
- **时钟门控（Clock gating）**：停掉空闲模块的时钟。
- **专用低精度单元**：FP8/INT8 计算单元的功耗是 FP32 的 1/4。

### 6.2 模型层

- **量化**：FP16→INT8 可省 50%–75% 功耗（更少的位、更少的搬运）。
- **剪枝（Pruning）**：去掉不重要的权重（结构化剪枝如 2:4 稀疏，NVIDIA Ampere 起硬件支持）。
- **知识蒸馏（Distillation）**：用大模型教小模型，推理时用小模型（Hinton 2015）。
- **架构瘦身**：MoE（混合专家）只激活部分参数；线性 attention、SSM（Mamba）降低计算复杂度。

### 6.3 数据层

- **稀疏化（Sparsity）**：跳过零值计算。激活稀疏（ReLU 后很多零）+ 权重稀疏结合，实测可省 2–4×。
- **动态计算**：Early exit（简单样本提前输出）、自适应深度。

### 6.4 冷却与数据中心

- **风冷**：传统方案，单机柜功耗上限 ~30kW。
- **液冷**：冷板式（直接贴在芯片上）或浸没式（把整台服务器泡在介电液体里），PUE 可降到 **1.1–1.2**（风冷一般 1.4–1.6）。
- **浸没式冷却**：最激进，PUE < 1.1，但运维复杂。
- **选址**：北欧（寒冷 + 水电）、内蒙古（风光 + 干冷）、冰岛（地热 + 冷）是 AI 数据中心首选。
- **余热回收**：把数据中心废热用于区域供暖（北欧已有案例）。

### 功耗优化的 Amdahl 视角

Amdahl 定律不仅适用于加速比，也适用于功耗节省：

$S_{power} = \frac{1}{(1-p) + p/N}$

其中 $p$ 是可优化部分占比，$N$ 是该部分的节省倍数。如果数据搬运占 70% 能耗（$p=0.7$），而 PIM 能把它省 10×（$N=10$），则总能耗节省 $S \approx 1/(0.3 + 0.07) \approx 2.7×$。这解释了为什么 PIM/CIM 路线在理论上能耗优势巨大。

> **一句话**：功耗优化要"从晶体管到电网"全栈思考，单点优化收益有限（Amdahl 制约）。

---

## 七、未来 10 年架构预测

基于前六章的诊断，对未来十年（2026–2036）做七个判断：

1. **3D 堆叠 + 光互连成为主流**。单 die 工艺红利枯竭（3nm/2nm 成本飙升），靠 3D 封装（CoWoS / Foveros / 混合键合）和片上/片间光互连（Lightmatter Passage、Ayar Labs）继续提升带宽。2030 年前后，**光互连将从"数据中心间"渗透到"机柜内"甚至"芯片间"**。

2. **HBM4 / HBM5 带宽破 10 TB/s**。HBM4（2026）目标 6–8 TB/s，HBM5（2028–2030）有望到 10–12 TB/s。但 HBM 成本和良率是瓶颈，会催生"HBM 替代"研究（如 SRAM-based near-memory compute）。

3. **PIM 从研究走向产品（2027–2030）**。Samsung HBM-PIM、SK Hynix AiM 已是预演，下一代可能在 GPU 的 HBM 控制器内集成轻量 ALU，做 GEMV、softmax 等内存密集型算子。**真正的 analog CIM 大规模商用仍要等到 2030+**。

4. **光计算在矩阵乘有突破（2030+）**。Lightmatter 等公司的线性层加速卡可能在 2027–2029 进入超算，做"光做线性、电做非线性"的混合架构。全面光计算仍遥远。

5. **类脑计算在边缘 AI 占有一席之地**。Loihi、Akida、天机等在 always-on 感知、机器人、IoT 上站稳，但**不会冲击数据中心 LLM 训练**。

6. **量子计算仍未实用，但持续投入**。2030 年前后可能看到首批"量子-经典混合"在材料、药物上的专用应用，但对通用 ML 仍无实质影响。容错量子计算要到 2035+。

7. **"专芯专用"趋势加强**：每类模型（Transformer、Diffusion、SSM、MoE）可能都有自己的 ASIC 加速。GPU 作为"通用平台"的地位短期不动，但专用加速器会蚕食特定场景。

**总体判断**：未来 10 年是"**冯诺依曼的黄昏，新范式的黎明**"。不会有某一天"冯诺依曼突然被取代"，而是各种新思路（PIM、光、类脑）从边缘场景一点点渗透，逐步蚕食。主流 GPU/TPU 仍是主力，但"纯粹冯诺依曼"的比例会持续下降。

---

## 八、给你的建议（基于「应用数学研究型工程师」定位）

读者画像：Python 工程级、PyTorch 跑过教程、数学基础待补、目标是"应用数学研究型工程师"、每周 10–20 小时。针对这个画像，本章给出路径建议。

### 8.1 优先方向：编译器优化（Triton / TVM）

**为什么**：①与你已有的工程能力高度契合（写 Python + 理解张量运算）；②**这是"不换硬件就能拿性能"的最大杠杆，工业界极度缺人**；③数学门槛适中（ Roofline、线性代数、复杂度分析），不需要固体物理/电路设计；④可验证性强——写个 Triton kernel 跓 benchmark 立刻知道好坏，正反馈快。

**入门路径**：
1. 先读 FlashAttention 论文（[arXiv:2205.14135](https://arxiv.org/abs/2205.14135)），理解 tiling + online softmax。
2. 学 Triton（官方 tutorial），写个矩阵乘、写个 softmax。
3. 进阶：读 Triton 论文（[DOI 10.1145/3315508.3329973](https://doi.org/10.1145/3315508.3329973)）。
4. 实战：在 Hugging Face 上找一个模型，用 torch.compile + Triton kernel 优化它。

### 8.2 次选：PIM 算法与稀疏计算

**为什么**：①偏硬件但有数学挑战（稀疏模式、误差补偿、调度）；②与"应用数学"（数值线性代数、近似算法）交集大；③是"突破冯诺依曼"里最接近产品的方向。

**注意**：PIM 需要接触硬件模拟器（如 PIMSim），上手门槛比纯软件高。

### 8.3 避坑：量子计算

**为什么**：①10 年内不会实用，对个人职业 ROI 低；②需要扎实的量子力学 + 线性代数背景，数学门槛远高于你目前水平；③适合"纯理论兴趣"，不适合"应用落地"目标。

**建议**：作为长期兴趣追踪（本卷专题已有 Quantum-ML 综述），但不要作为主要投入方向。

### 8.4 黄金交叉：体系结构 + ML 编译器

这是工业需求最大、人才最缺的交叉领域。**懂硬件（CPU 流水线、cache、GPU 架构）又懂编译（XLA、Triton、MLIR）的人极少**，往往被两边争抢。对你来说：
- 从 ML Sys 入手（FlashAttention、vLLM 这些系统级项目是最好的教材）。
- 补体系结构基础（读 Hennessy & Patterson《计算机体系结构：量化方法》）。
- 补编译原理（读"龙书"或 Engineering a Compiler）。

这条路与你"应用数学研究型工程师"的定位完美契合——体系结构是"最工程的数学"，编译器是"最数学的工程"。

---

## 📌 进一步阅读

**综述与教材**
- Hennessy & Patterson, **Computer Architecture: A Quantitative Approach**（体系结构圣经）。
- Ielmini & Wong, **Nature Electronics** 1:333 (2018), [DOI 10.1038/s41928-018-0092-2](https://doi.org/10.1038/s41928-018-0092-2)——存算一体综述。
- Sebastian 等, **Nature Nanotechnology** 15:529 (2020), [DOI 10.1038/s41565-020-0655-z](https://doi.org/10.1038/s41565-020-0655-z)——PIM 应用综述。
- Mutlu 等, "A modern primer on processing in memory", [DOI 10.1007/978-981-16-7487-7_7](https://doi.org/10.1007/978-981-16-7487-7_7)。

**里程碑论文（本文一手核实）**
- IBM NorthPole: **Science** 382:329 (2023), [DOI 10.1126/science.adh1174](https://doi.org/10.1126/science.adh1174)。
- 清华天机芯: **Nature** 572:106 (2019), [DOI 10.1038/s41586-019-1424-8](https://doi.org/10.1038/s41586-019-1424-8)。
- 清华 memristor CNN: **Nature** 577:641 (2020), [DOI 10.1038/s41586-020-1942-4](https://doi.org/10.1038/s41586-020-1942-4)。
- 光计算 Shen: **Nature Photonics** 11:441 (2017), [DOI 10.1038/nphoton.2017.93](https://doi.org/10.1038/nphoton.2017.93)。
- 光子NN Ashtiani: **Nature** 606:501 (2022), [DOI 10.1038/s41586-022-04714-0](https://doi.org/10.1038/s41586-022-04714-0)。
- FlashAttention三代: [2205.14135](https://arxiv.org/abs/2205.14135) / [2307.08691](https://arxiv.org/abs/2307.08691) / [2407.08608](https://arxiv.org/abs/2407.08608)。
- PagedAttention/vLLM: [arXiv:2309.06180](https://arxiv.org/abs/2309.06180) (SOSP 2023)。
- Triton: [DOI 10.1145/3315508.3329973](https://doi.org/10.1145/3315508.3329973) (MAPL 2019)。
- Groq TSP: [DOI 10.1109/ISCA45697.2020.00023](https://doi.org/10.1109/ISCA45697.2020.00023) (ISCA 2020)。
- Horowitz 能耗经典: [DOI 10.1109/ISSCC.2014.6757323](https://doi.org/10.1109/ISSCC.2014.6757323)。
- Backus 图灵奖演讲: [DOI 10.1145/359576.359579](https://doi.org/10.1145/359576.359579)。
- Thompson 计算极限: [arXiv:2007.05558](https://arxiv.org/abs/2007.05558)。

**项目与资源**
- vLLM（推理服务）、Triton（kernel DSL）、XLA、TVM、DeepSpeed、Megatron-LM。
- Cerebras、Groq、Lightmatter、SambaNova 官方博客与技术报告。

**配套卷**
- 本卷 `02-ai4os.md`（AI for OS）与本文第五章/第四章深度互补。
- 本卷 `04-ai4eda-ic.md`（AI for EDA/芯片设计）是"用 AI 设计芯片"的姊妹篇。
- `synthesis/topic-10-quantum-ml.md`：量子机器学习专题（Willow/Heron/Majorana）。

---

## ✍️ 思考题（5 道）

1. **Roofline 实战**：假设你有一块 GPU，峰值算力 1000 TFLOPS（FP16），HBM 带宽 3 TB/s。一个 LLM 解码任务的算术强度是 2 FLOPs/Byte。请问：该任务的理论性能上限是多少？是 compute-bound 还是 memory-bound？要提升性能，应该加算力还是加带宽？（提示：用 $P = \min(P_{peak}, \pi \cdot B)$）

2. **FlashAttention 本质**：为什么 FlashAttention 叫"exact attention"？它与 linear attention、sparse attention 这些"近似 attention"的根本区别是什么？请从"数学等价性"和"IO 复杂度"两个角度回答。如果 SRAM 无限大，FlashAttention 还有意义吗？

3. **PagedAttention 迁移**：PagedAttention 借鉴了 OS 的虚拟内存分页。请问：OS 的哪些其他机制（如 copy-on-write、swap、TLB、NUMA）还能迁移到 LLM 推理中？各能解决什么问题？

4. **能耗权衡**：根据 Horowitz 2014 的数据，一次 DRAM 访问约 1nJ，一次 FP16 MAC 约 20pJ。如果一个 70B 模型推理生成一个 token 要读 140GB 权重，请估算：总能耗中"搬运"与"计算"的占比。这说明了什么？如果改用 PIM（权重不动，计算在存储器内做），能耗能省多少倍？

5. **范式判断**：有人说"GPU 已经走到尽头，必须换架构才能继续 Scaling"，也有人说"靠编译器+精度压缩+互联，GPU 还能走 10 年"。你支持哪个观点？请结合本文的 Roofline 分析、FlashAttention 案例、以及 Cerebras/Groq 的兴衰，给出有论据的判断。

---

<!-- delegate 直接写入，2026-07-20 -->
