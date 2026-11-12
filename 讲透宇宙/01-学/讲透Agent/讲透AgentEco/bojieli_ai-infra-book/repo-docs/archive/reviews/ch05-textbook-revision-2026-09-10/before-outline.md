# 第 5 章 算子与运行时

> 写作大纲 · 循环变换、执行组织与请求验证重组 · 2026-09-10

本章从 Qwen3 的 FFN 投影—激活—量化片段出发，先解释主机提交、输入输出复制和完成顺序，再依次选择分块、融合、编译与运行方式，最后把优化放回固定请求。注意力链作为第二个代表案例，用 FlashAttention 解释归约状态、分块与流水如何共同改变 IO。

**本章判断：** 少一次写回、少一个 kernel 或更快的独占内核都要接受整条链的检验；复用、并发和缓冲寿命共同决定搬移代价。

**前置与交付：** 依赖第 4 章的资源、存储层次与布局知识；交付实际读写、融合边界、缓冲寿命、执行时间与准备成本。第 6 章扩大到多卡，第 8 章加入动态请求与服务目标。

**阅读安排：** 核心练习为实验 5-2、实验 5-8、实验 5-9，分别检查融合、运行时与完整请求；其余练习为延伸。核心路径可用配套计算与轨迹独立完成，实验 5-9 不要求先做 Agent 优化。完整参数、实现版本与实验变体见[扩写资料](extensions/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md)。

**从模型算子到实际执行：** 章首先给两张小表和执行简图：FFN 的 gate/up 投影—SiLU/Mul—输入量化—down 投影，以及 QKV—QK Norm—RoPE—注意力。量化节点按选定的低精度实现标出，不视为所有模型路径的必经步骤。固定配置后列形状、中间张量字节与生产／消费关系，沿第 2 章模型定义建立独立执行基线。

逻辑算子、库调用、设备 kernel 与主机提交分别标记，它们并非一一对应。每节在同一基线图上修改循环、数据边或执行时间线；正文保留一笔主要计算、一个改变选择的反例与必要实测，完整模型清单放入扩写资料。

## 5.1 一次设备执行：提交、搬运与同步

从 CPU 准备输入、H2D、设备计算、D2H 到 CPU 使用结果，先建立完整执行过程，再进入优化。术语第一次出现时解释含义，用同一张时间线区分提交、开始和完成。

### 5.1.1 从框架调用到 kernel launch

解释框架分派、运行时提交与设备执行的关系，区分算子、kernel 和 launch。简述 CUDA 的 thread、thread block、grid，说明数据分块与线程块的对应由程序决定。异步调用返回不代表设备完成，小算子可能等主机提交。

### 5.1.2 数据在哪里：H2D、D2H 与 D2D

按方向和实际对象解释复制，区分权重加载、每批输入、设备内中间结果和输出回传。模型与 KV 可以常驻，GPU 读取显存不等于 H2D。用 64 MiB／24 GiB/s 的已有教学算例解释传输时间，补充小传输的固定开销、pageable/pinned memory 和临时锁页的成本。

### 5.1.3 stream、event 与完成顺序

先讲同流顺序，再讲跨流事件依赖和 CPU 等待。分别说明 H2D 源、设备输入、D2H 源和主机目标的复用或读取时刻。异步 API 不保证设备重叠；需要独立工作、复制引擎、带宽与缓冲。默认流语义依配置说明。

### 5.1.4 怎样读时间线和测量时间

用 CPU 提交 3 μs、H2D 8 μs、kernel 20 μs、D2H 4 μs 的串行教学时序区分提交时间、内核时间与结果可用时间。说明 CPU 时钟、CUDA event 和 profiler 各自测什么，首轮准备与预热分开。随文练习不新增实验编号；原有九个实验继续使用已有记录。

**扩写资料：** [执行基础与官方文档](extensions/05-算子与运行时.md#detail-5.1)。

## 5.2 单算子：分块、布局与实际访存

沿 FFN 的矩阵投影，从数学上必需的数据走到实现中的重复访问。承接第 4 章的存储层次与资源预算，本节选择循环、分块和布局，不重复硬件结构介绍。

### 5.2.1 矩阵形状与重复读取

用朴素矩阵乘展示反复读取、循环顺序和数据复用，先把实际访问与第 4 章的预测对上。区别数学工作量与实现产生的流量。

沿章首 FFN 投影固定矩阵形状，先数输入、权重和输出各读写一次的逻辑字节，再按朴素循环数重读。源码访问、L2 服务的访问和 HBM 流量分别标记，后续优化始终注明统计接口。

### 5.2.2 容量约束下的分块复用

由片上容量推出 tiling，再比较三种硬件怎样分配工作。用块太小、太大和边界不齐的例子说明为什么没有通用的最佳块形状。

先给一个可手算的片上预算：三个矩阵块至少占 `b(mk + kn + mn)` 字节，再加入累加格式和双缓冲。枚举少数可行块，比较复用与并发；自动调优在这一步之后出现。

沿 Qwen3-8B 的 `[1024,4096] × [4096,12288]` 单支投影继续算：128 MiB 是输入输出各走一次的最低流量；在给定循环下，64×64 与 128×128 输出块分别需要 24／80 KiB 活动空间，产生 3,096／1,560 MiB 的下一层访问。用 Orojenesis 引出容量约束下的复用，再区分某个方案的计数、搜索所得最好结果和流量下界；L2 能服务的重读不应全部记成 HBM 流量。[计算条件](../case-studies/buffer-capacity-and-data-movement.md)留作扩写依据。

### 5.2.3 布局与归约的并行代价

先用相同逻辑矩阵的行／列访问说明连续访问与布局的关系；bank 映射作为第 4 章布局知识的应用，完整 padding 枚举放入延伸。再用 RMSNorm 的 `[M,4096]` 行归约，比较单 token decode 与多 token prefill：行数决定可并行的组数，行宽决定组内工作。

扩大行宽后比较一组一行与拆分归约，计算增加的 partial buffer、输入重读、同步与第二次归约。此处先回答并行度是否值得；浮点累加顺序改变的反例到 5.4.3 统一解释。

> **实验 5-1 ★〔延伸〕：矩阵分块与访存计数**
>
> 块多大才划算？ 实现小矩阵的两种循环与分块，先数访问再测量；报告最佳块随形状改变的原因。 归约延伸沿同节 RMSNorm：固定行宽改变行数，再扩大归约宽度，比较一组一行与拆分归约的并行度、额外缓冲及第二次归约。
>
> 条件：基础·CPU；可选单设备。

**实测结果（5-1）：** M2 Max 改排连续访问快约5.3–9.1倍，细分块反而更慢。[GPU分块](../experiments/ch05/05-01/gpu-tiles/README.md)的最佳候选随行数改变，L2重读不能全部算在显存上。[归约对照](../experiments/ch05/05-01/rmsnorm-split/README.md)显示宽行实现的寄存器溢出会混入拆分收益；通过误差容限也不代表逐位相同。[代码、数据与图](../experiments/ch05/05-01/README.md)。

> **图 5-1：循环顺序与分块改变了哪些访问（配图计划）**
>
> 自绘 SVG；配实验 5-1 的计数与测量。用同一 Qwen3 矩阵画容量与流量的关系，分别标出最低逻辑字节、已枚举方案与实测点，存储层次写在坐标旁。增加局部 bank 映射示意，让相同请求的集中与分散可直接对照。

**扩写资料：** [本节完整计算、版本与实验变体](extensions/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#detail-5.2)。

## 5.3 算子链：融合、缓冲与流水

从单个内核扩大到相邻算子。先计算取消中间写回的收益，再检查布局交接和缓冲寿命，最后用 FlashAttention 综合这些机制。

### 5.3.1 中间张量与融合边界

从矩阵乘后接逐元素运算进入融合，计算写回与读取；随后加入寄存器、缓冲占用和并发，解释融合收益为什么会有转折。

先算最容易看见的收益：若中间张量有 X 字节，取消一次写回和读取，理想上少走约 `2X` 字节；再问这些数据能否留在片上、会不会挤掉并行工作。本节先在 FFN 激活链上算清这一取舍，5.3.3 再扩大到注意力。

> **实验 5-2 ★〔核心〕：融合的流量与资源占用**
>
> 融合省下的流量够不够抵消资源占用？ 对同一算子链比较融合前后，记录字节、缓冲和时间；无加速器时做容量模型。
>
> 选做变体用五个 16 KiB 块的生产／消费时刻求 FIFO 峰值，再加入重排缓冲，比较保持进度、允许背压和统一布局三个选择，见[流式交接算例](../case-studies/stream-order-and-buffer.md)。
>
> 条件：基础·编程／计算。

**实测结果（5-2）：** RTX PRO 6000 上，1,024-token 的 SwiGLU 激活链融合后从 14.20 μs 降至 7.68 μs，省去 24 MiB 中间张量；块更大未必更快。此为共享 GPU、热缓存与图重放下的局部测量。[实验、原始数据与图](../experiments/ch05/05-02/README.md)。

### 5.3.2 布局交接、缓冲寿命与双缓冲

布局也沿整条链计价：分别选出两个最快的独立内核后，还要加上中间转换；比较接受同一布局、另做重排和由生产者直接写出消费方布局。沿前节投影的 24 MiB BF16 输出，另行物化一份完整重排结果要增加一次读和一次写，再判断能否在现有交接中完成。

用双缓冲时序解释重叠条件；在 NVIDIA、昇腾、Apple 的对应机制上标出缓冲寿命和同步。矩阵与向量交接同第 4 章连接起来。

用生产／消费时间线标出每块数据产生、就绪、最后消费与复用的时刻；双缓冲必须同时满足容量与依赖。相同形状若访问顺序不同，还需要排队或重排。正文保留一次容量不足导致背压的反例，FIFO 完整推算和主机锁页／异步复制变体见扩写资料。

### 5.3.3 FlashAttention：分块与在线 Softmax

从完整注意力分数矩阵的容量问题出发，依次讲分块、在线 Softmax 的局部状态与合并、减少中间写回及训练时重计算，再讨论 FA2／FA3 的调度和异步流水。版本演进紧随其解决的问题出现。

先呈现完整注意力矩阵的存储问题，再讲分块、在线 Softmax 和重计算。取 Qwen3 的单个头、8192 token、head_dim=128，在明确的 128 KiB 混合精度预算中，推算 Q/O 驻留与 K/V 重读：K/V 块从 64 行缩至 1 行，选定接口流量由 304 MiB 降至 204 MiB，但循环更新与输出缩放增加。借 AttenIO 的分块思路和 FA2 的实际实现，解释块形状还要匹配计算单元与流水；[计算条件](../case-studies/attention-tiles-and-io.md)区分抽象访问、实际缓存和 GPU 时间。

> **实验 5-3 ★〔延伸〕：分块 Softmax 与注意力 IO**
>
> FlashAttention 为什么能少访问内存？ 小张量验证分块 Softmax 的结果，再逐项列出 Q、K/V、部分输出与统计量的容量，比较三种块形状的重读和缩放次数。加入预取槽后重新求可行块大小；有设备时对照实际后端的流量与时间，不用 CPU 时间代替 GPU 加速比。
>
> 条件：基础·Python。

**实测结果（5-3）：** RTX 热缓存下，8192-token 单头注意力的数学与 Flash 后端分别为 2.64 ms、79.5 μs，新增分配峰值分别约 848、22.2 MiB。实际 DRAM 与 L2 计数分开记录。[代码、原始计数与图](../experiments/ch05/05-03/README.md)。

> **图 5-2：融合、缓冲与注意力分块（配图计划）**
>
> 采用三个独立面板，分别随 5.3.1、5.3.2、5.3.3 阅读：FFN 中间写回前后对照；两个 tile 的生产、消费与缓冲复用时间线；FlashAttention 的 Q/O 驻留、K/V 扫描及在线状态。主机搬运与 FIFO 累计曲线保留在扩写资料，不叠加到同一张主图。

**扩写资料：** [本节完整计算、版本与实验变体](extensions/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#detail-5.3)。

## 5.4 编译器：表达、变换与选择

把前两节的手工选择交给编译器表达与检查。AKG 的核心技术多面体编译通过可读的循环变换进入正文，再分别判断依赖、数值和性能。

### 5.4.1 AKG：为什么需要跨算子选择

沿作者参与的 AKG 工作，先讲一个独立算子已经优化、整条模型链仍反复写回的设计问题。重建当时可考虑的接口保留、手工融合和编译选择，说明形状、布局及维护组合为什么让局部判断不够；亲历细节依据原有材料，未记录的失败过程由作者补充。

正文只沿 Qwen3 的注意力链和激活量化链推进：先算中间字节，再算片上活动空间和合法依赖。含 k 个算子的线性链仅相邻边界就有 2^(k−1) 种形式划分；合法性和硬件预算筛掉一部分后，再用成本估计与实测选择。Korch 中 kernel 数增加却整链更快的子图作为反例，检验真正影响时间的量。

章首两条链的基线图在这里补上候选融合边界和布局，复用已有形状与字节，不重新展开模型目录。V4 压缩、索引与专家链作为迁移检验，完整模型清单留在扩写资料。

### 5.4.2 Polyhedral Compilation：用循环变换表达优化

以 FFN 的矩阵乘接逐元素激活为贯穿例，先写出 i、j、k 三层循环和后续激活循环，再用 Halide／TVM 风格的 schedule 逐步改变执行方式。每一步并排画变换前后的循环、访问位置和临时缓冲，让读者能用第 5.2、5.3 节的方法复算。

依次演示：split／tile 把输出行列拆成外层块与块内循环；reorder 把同一 tile 的工作放在一起以复用输入；在所选循环层级安排生产者计算与缓存，把中间结果留在局部；输出 tile 完成全部 k 归约后，接上激活以省去完整中间张量。用 Halide 的 compute_at、TVM 的 compute_at／reverse_compute_at 等概念解释计算位置，具体 API 方向与合法条件随所选版本核对。循环 fuse 表示合并迭代维度，与算子融合分别说明。

在读者看懂上述动作后，明确介绍 AKG 的核心技术 **Polyhedral Compilation（多面体编译）**：编译器表示循环中有哪些计算、每步读写哪些元素，以及哪些计算必须先完成，再在保持依赖的前提下组织循环、分块、融合与数据搬运，生成适配硬件的代码。用依赖箭头和循环伪代码解释“允许怎样移动”，不以 affine transformation 的矩阵、集合或证明作为正文入口；多面体表示与 isl 的形式细节留作延伸。

Halide／TVM 的算法与 schedule 分离用于帮助读者理解“算什么”与“按什么顺序、在哪里算”。它们是讲解循环变换的直观入口，不将 AKG 描述成几个 schedule API 的包装，也不把 Halide、TVM 和 AKG 的内部表示与自动化能力混同。AKG PLDI 2021 的机制按原论文说明，当前 TensorIR 的接口另固定版本。

对照 CUDA、Triton、Ascend C 与 Metal 时，只选同一个 tile，标出工作分配、布局、同步与边界由谁控制。作者从 HLS 接口封装转向识别原语和读写依赖的经历作为短例，来源见[作者材料](../case-studies/author-context-and-design.md)；完整代码和其他后端进入扩写资料。

### 5.4.3 变换合法性与数值正确性

先在上一节的循环例中画一个合法变换和一个非法变换：独立输出可调整遍历顺序；一个输出尚未完成 k 维累加时，通常不能直接做 SiLU 并把各块激活结果相加。是否允许拆分归约，需要说明保留什么局部状态、怎样合并，以及允许怎样的数值误差。

把三个判断分开：依赖分析检查必要先后关系；数值检查覆盖累加顺序、cast 舍入与量化尺度；性能检查再计完整流量、资源占用与并发。多面体依赖分析不会自动保证任意浮点重关联逐位等价，也不直接给出最快方案。

沿 RMSNorm 的拆分归约比较固定形状重复运行与不同 batch 下的结果，区分误差容限和逐位一致；给第 8、10 章的可复现性留下明确接口。接在线 Softmax 和 FP8 融合，各保留一个会改变选择的反例。

接续在线 Softmax，用 RedFuser 说明编译器怎样从归约依赖推导可合并的局部状态，再生成顺序或分段执行。随后给量化链加入 FP8 cast，检查分块是否改变舍入；沿 Qwen3 专家投影计算取消中间张量后，各输出块是否反复读取更宽的输入。让读者分别判断变换合法性、精度与完整流量，[推算与来源](../case-studies/fusion-legality-and-precision.md)留作扩写依据。

接回当前 vLLM 的 SiLU+Mul→量化路径：从 v0.6.0 的手工激活算子，走到编译 pass 对跨算子模式的匹配。以 Qwen3 的 `[1024,24576]` gate-up 输出计算省掉的 48 MiB 中间读写，再单独推算活动张量峰值。编译器可见的表达也可能被 Inductor 自行融合，因此比较实际图和 trace；禁用某个自定义融合 pass 不等于恢复了两个独立 kernel。

> **实验 5-4 ★〔延伸〕：模型算子与融合组合**
>
> 按固定模型配置和实现生成算子表；对 Qwen3-8B 与 V4-Flash 各选一条链，计算独立执行与两种合法融合的中间字节、片上占用和启动边界。先预测收益，有设备时对照实际 trace；其他模型用报告与实现补全逻辑清单，缺失项保留。
>
> 选做 Qwen3 专家投影的 FP8 变体：比较整行尺度与前缀尺度，先找出数值不同的输入，再按相同输出块数计读取。将误差合同与缓存条件写清后，才比较实际时间。
>
> 条件：基础·代码阅读／计算；可选设备。

**实测结果（5-4）：** Qwen 形状的 SwiGLU→FP8 链融合后确实减少 kernel，但默认编译路径改变了中间舍入与尺度；显式保留 RNE 舍入后尺度归零一致，仍有少量 FP8 位差。同轮 Graph 与 eager 交错 132 批次表明，提交间隙与算子内部成本必须分开看，少一个 kernel 不保证更快。V4 专家激活子链保留裁剪与路由权重的先后关系后，实际执行从 8 个 kernel 降到 2 个或 1 个；这不代表完整专家推理获得同等加速。[记录、数值差异与 V4 子链](../experiments/ch05/05-04/README.md)。

> **部分实测**：Qwen形状的SwiGLU→FP8链可减少kernel，但默认编译路径改变了中间舍入和尺度；显式保留舍入后尺度一致，仍有少量FP8位差，同轮Graph对照表明，提交间隙与算子内部成本须分开看，单kernel也不保证相同速度。[记录与数值差异](../experiments/ch05/05-04/README.md)。

> V4专家激活子链保留裁剪与路由权重的先后关系后，实际执行从8个kernel降至2个或1个；这不代表完整专家推理获得同等加速。[子链实测](../experiments/ch05/05-04/v4/README.md)。

> 指定RedFuser量化生成核的实际运行确认：改变块顺序可将输出从1变为0.98193359375，全零输入还会产生NaN；必须先明确数值合同。[后端复核](../experiments/ch05/05-04/redfuser/README.md)。

> **图 5-3：算子接口与图算融合的边界（配图计划）**
>
> 自绘 SVG；用同一条计算链显示独立优化后的写回、重新分块后的融合与保留边界。模型—算子对照表由实验 5-4 的固定输入生成，逻辑节点与内核启动分别标注；激活量化链另画张量生存期，区分消除的中间张量、峰值容量下降和读写量减少。
>
> 自动归约变体标出局部状态与合并位置；量化变体标出 cast 前后的位宽、尺度生效时间和输出块的重复读取。由同一计算记录生成 SVG。

### 5.4.4 成本估计、自动调优与实测反馈

先沿 5.4.2 的同一个循环变换检查生成代码，再比较规则 schedule、测量驱动搜索和允许修改实现的 Agent。成本模型筛选候选，实际 profiling 校准缓存、寄存器溢出与并发；预测失准不等于依赖分析失效。调优成本在 5.5.3 与执行复用次数一起核算。

> **实验 5-5 ★〔延伸〕：编译变换与硬件代码**
>
> 编译器替程序员做了什么？ 对同一分块程序查看指定后端的生成表示／代码，记录隐式变换与仍需调优的部分。
>
> 条件：基础·编译工具／配套记录。

**实测结果（5-5）：** 同一转置程序随输入步长生成不同的共享内存与指令路径；RTX 上把 16×16 块改为 32×32 后，一组连续输入从 7.87 μs 降至 2.92 μs，继续增大未改善。[生成代码、数据与图](../experiments/ch05/05-05/README.md)。

> **图 5-4：一次优化如何在几种编程方式中表达（配图计划）**
>
> 沿 5.4.2 的矩阵乘接激活，画原始循环、split／tile、reorder、局部缓存与 tile 完成后融合的五个面板；用读写依赖箭头说明可移动范围。Halide／TVM 风格的 schedule 与前后循环并排排版，另标一个提前执行激活的非法反例；形式化 affine transformation 不进入主图。

用同一热点比较规则 schedule、测量驱动搜索和允许修改实现的 Agent。三种方法都先固定语义与资源，再提出候选、验证正确性、计时及撤回退化项；Agent 的特点是候选空间与验证成本变化，传统自动调优已经使用实际测量反馈。

核心论证保留一次预测失准后的修正：独占更快的候选可能挤慢并发 attention 或通信。记录改变的字节、寄存器、布局与等待，再回到实验 5-9 检查完整请求。KernelAgent、FlashInfer-Bench、CUDA Agent 及考核版本的具体入口和完整迭代记录放入延伸材料。

借 LOOPRAG 与 FlashInfer-Bench 比较候选成绩和部署收益：正确性参考、性能基线、超时与容差分别固定；用两个形状说明加速比平均更高，按实际调用频数计算却可能更慢。再加入分派与回退成本，沿[评测与部署算例](../case-studies/optimization-evaluation-and-deployment.md)检查候选是否真的被引擎使用。

> **实验 5-6 ★★〔延伸〕：自动 profile 与算子优化**
>
> 用固定 KernelAgent 或一个小型工具调用 Agent，优化从 Qwen3-8B 的 vLLM／SGLang trace 提取的 RMSNorm／SwiGLU 热点。比较默认编译、等预算的 schedule 搜索和带 profiler 反馈的 Agent；限定候选数及 GPU 时间，由 Agent 修改内核，读者负责给出问题和判断结果。每次先对固定参考实现校验，再在独占计时窗口预热与重复测量；对原路径存在并发的热点，补测同一并发片段的资源争用。保留未参与搜索的形状、边界输入和退化案例，固定独立验证入口、参考实现与设备资源；优化后的候选不能自行降低校验条件。报告优化花费、稳态收益与摊销次数，最后回到实验 5-9 检查请求是否变快。
>
> 条件：进阶·单 GPU＋模型 API／本地模型；无设备时分析配套完整迭代记录。
>
> 同时报告形状平均分数与按实际频数汇总的时间；验证失败项计入回退，分派和准备花费计入部署预算。固定模型算子定义，不能直接移用 B200 比赛的 MoE／DSA／GDN 容差。

**实测结果（5-6）：** 从真实 Qwen3-8B trace 定位 72 次 SwiGLU 并捕获 36 层输入输出；默认编译与 6 个 schedule 候选通过冻结参考与 5 项留出检查，132 批随机交错完成。两轮真实工具调用 Agent 各 6 次**均未产出可用的新内核**（复制 AST 或重复候选被拒），负结果按协议完整保留。等 GPU 预算的独占窗口、并发争用与 profiler 反馈回路仍未覆盖，不用已有微基准替代。[迭代记录、候选与负结果](../experiments/ch05/05-06/README.md)。

**实测（部分）：** [固定验证与真实Agent记录](../experiments/ch05/05-06/README.md)保留两轮各6次调用：首轮反复提交相同代码，次轮重复提交被拒绝，未发现新优化。计时波动不作为收益，完整请求验证仍待。

> **图 5-5：算子优化的反馈过程（配图计划）**
>
> 自绘 SVG 连接假设、候选、校验与 profiling；实验 5-6 生成逐轮耗时及瓶颈变化，失败候选保留可见。
>
> 同一份记录分别生成候选分数和含回退的部署时间，标出调用频数改变后的选择。

**扩写资料：** [本节完整计算、版本与实验变体](extensions/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#detail-5.4)。

## 5.5 运行时：提交、重放与动态形状

内核确定之后，主机准备、提交和设备等待仍影响完成时间。先读执行时间线，再讲图重放，最后加入动态形状与准备成本。

### 5.5.1 主机提交与设备执行

从一次小算子的执行轨迹引入任务队列、提交、事件和等待，把 CPU 准备和 GPU 时间放入同一依赖图。把主机开销放回关键路径，而不按 API 个数估算执行时间。随后用 vLLM v0.6.0 的分进程、GIL 与异步执行案例作对照；版本总收益仅说明该组合，单项贡献需要同条件消融。依据：[成本下降调研](../research/token-cost-2023-2026/report.md#runtime)。

**后端对照〔延伸〕：** Ollama 的加载、runner、Metal／CUDA／MLX 内核与命令提交用于核对硬件到执行的映射；完整版本与精度条件见扩写资料。章末固定使用同一 vLLM／SGLang 路径完成前后比较。

### 5.5.2 CUDA Graph 的捕获与重放

沿同一条计算链比较 eager、分段图和完整重放。图执行减少重复提交，仍需满足地址、数据就绪与形状条件；准备时间、padding、固定缓冲与 KV 争用一起计入。先用 trace 找暴露的提交间隙，再决定哪些段值得捕获。

给两种边界：生产者直接写入固定缓冲，或每次复制外部输入后重放。按张量字节求额外拷贝时间，与可消除的等待比较；同一个模型可以保留一部分 eager。FlashInfer plan/run、vLLM 图分派、SGLang BCG 与 GraCE 提供不同实现证据，完整版本与支持组合放入本节延伸材料。

释放显存但保留虚拟地址可以减少重新准备，内容有效性仍需恢复。第 10 章权重交接用同一缓冲寿命规则解释这个边界。

用 256／2048 个 BF16 token 的 2／16 MiB 输入比较图重放：在同一组教学开销下，小输入的复制仍能被提交收益覆盖，大输入则可能抵消收益。沿[计算记录](../calculations/results/graph-small-input.md)求交点，再改变输入来源和调用次数；第 8 章承接这笔账，加入真实请求的形状分布。

实验 5-8 的轨迹用于区分两种收益：三次执行从 18 次主机启动降到 3 次，设备仍有 18 个 kernel；融合后才降到 15 个。保留[原始轨迹的复核](../calculations/results/runtime-ffn-token32.md)，用这组观测解释减少提交与减少设备工作为何不能混为一谈；具体时间线随实验展示。

### 5.5.3 动态形状、分桶与特化摊销

对比卷积训练的常见形状与 LLM 的长度、并发和专家负载变化，解释 mask、运行时 tiling、分桶与特化为何出现。

比较第一次执行、稳定复用和偶发形状；核算编译摊销、缓存和回退。以 CloudMatrix384 的 MTP／MLA 实现与 GPU 服务路径作例子。

用同一 Qwen3 FFN 比较通用、分桶与逐形状特化：短寿命调用可能来不及收回编译成本，频繁复用才值得更深特化。保留一组形状分布，计算“准备成本＋重复次数×每次执行成本”的交点；[完整扫描](../calculations/results/specialization-medium.md)用于实验 5-7，服务率和准备时间均为教学输入。

图 5-6 使用[已生成的总时间曲线](../calculations/figures/specialization/figure.svg)，让通用、分桶和特化三种选择随复用次数发生变化；输入、精确交点与重绘命令保存在本节扩写资料。

> **实验 5-7 ★〔延伸〕：形状特化的复用阈值**
>
> 为每种长度编译一份程序值不值？ 给定形状分布，先手算通用、分桶和特化的编译加执行总时间，再用短脚本扫描复用阈值。
>
> 条件：基础·计算／短脚本。

**计算结果（5-7）：** 在给定形状分布上有两个交点：约 60 次复用时通用程序输给分桶，约 100 次时分桶输给逐形状特化。短寿命调用来不及收回编译成本，只有频繁复用才值得更深特化。分桶胜出的中间区间靠的是准备与执行都居中，代价是把 256 的调用 pad 到 512 执行。编译成本翻倍会把阈值整体右移退回通用；特化产物已缓存则让特化立刻胜出——缓存把“为每种长度编译一份”从投资问题变成查表问题。[扫描、变体与限制](../experiments/ch05/05-07/README.md)。

> **图 5-6：不同形状策略的总时间如何交叉（配图计划）**
>
> 实验 5-7 脚本生成 SVG，包含编译成本。

**运行时综合练习：** 完成提交、重放与形状选择后做实验 5-8；下面的 persistent 专题为进阶选读。

> **实验 5-8 ★★〔核心〕：图重放与算子融合**
>
> 对 Qwen3 的代表算子链比较普通提交、融合、CUDA Graph 与组合执行，使用 Nsight Systems 记录主机与设备间隙，计入捕获、padding 和缓冲容量。以 MPK 的匹配模型／硬件案例补充 persistent 路径，不能把独立论文的加速比相乘；说明增加微批何时会使启动开销更大。
>
> 核心部分分析配套的普通提交、融合、图重放与组合执行四组轨迹，无设备可直接完成；自行采集与 persistent 路径为延伸。
>
> 条件：基础·配套轨迹分析；进阶·单设备实跑。

**实测结果（5-8）：** RTX 的完整 FFN 链中，图重放把三次执行的主机启动从 18 次减到 3 次，设备仍执行 18 个 kernel；融合后才降到 15 个。整链耗时并未同比缩短，补齐与顺序微批还会增加代价。[实跑、时间线与论文对照](../experiments/ch05/05-08/README.md)。 [FlashInfer计划复用实测](../experiments/ch05/05-08/flashinfer-plan/README.md)中，相同36层调用由逐层规划改为一次规划，两组中位从2.04／2.35降至0.72／0.75 ms，kernel数不变；元数据变化仍需更新计划。

> **图 5-7：普通提交、融合和图重放的执行差异（配图计划）**
>
> 从实验 5-8 轨迹生成 SVG，保留主机与设备两条时间线。

### 5.5.4 Persistent Kernel 与细粒度调度〔进阶〕

用 Mirage Persistent Kernel／MPK（2025 初稿、2026 修订）把一个算子拆成 SM 级任务，解释为什么“每个算子一个 kernel”的边界会阻碍 tile 就绪后立即开始通信。设备内任务与事件可以表达跨算子流水，但也增加调度、同步和资源驻留开销。

比较 CUDA Graph、融合、persistent kernel 与 pipelining 各自省掉什么。增大 batch 可以摊薄单 token 启动成本；切微批有助于重叠，却也可能增加启动次数和小矩阵损失。下一章继续讨论跨卡数据，8.1 和 9.4 再用真实服务判断这些方法的适用条件。

用 up 投影接 SiLU 的八块教学任务比较整算子屏障与按块就绪：一次主机启动仍有 16 个设备任务，需要分派和依赖通知。逐步增加调度成本，找到流水收益被抵消的条件；[任务与缓冲计算](../calculations/results/persistent-tiles-base.md)留作延伸，供给速率属于教学输入。

**扩写资料：** [本节完整计算、版本与实验变体](extensions/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#detail-5.5)。

## 5.6 从局部优化到完整请求

回到同一模型、引擎、精度和固定请求，确认候选实际生效并解释局部收益。第 8 章再加入排队、连续批处理与服务目标。

### 5.6.1 确认优化进入实际执行路径

沿章首 FFN 激活链，在固定模型、引擎、精度、输入和图模式下接入已验证候选。用算子分派、编译图与同路径 trace 确认替换生效，记录回退、准备工作和实际 kernel；不能只凭自定义 pass 开关判断执行方式。

核心练习直接使用实验 5-9 配套的已验证候选与替换前后记录，不依赖读者完成实验 5-6。完成 Agent 延伸练习的读者可以替换为自己的候选，但必须经过相同验证。

### 5.6.2 热点占比、依赖与关键路径

先用固定请求的依赖图定位关键路径，区分 kernel 时间之和、采集区间占比与请求墙钟时间。热点变快之后，其他分支、提交等待和共享资源可能成为新限制，不能把热点占比直接套成必然的端到端收益。

保留一组教学时间说明关键路径切换，再用实际 trace 核对；完整依赖图、微批重叠与资源争用计算见扩写资料。优化候选要在原有并发片段中复测，局部独占更快也可能挤慢其他工作。

### 5.6.3 固定请求的前后对照与设计决定

> **实验 5-9 ★★〔核心〕：内核优化与请求加速**
>
> 使用配套已验证候选与替换记录，在同一模型、引擎、精度与输入下检查候选内核；完成实验 5-6 者可选用自己的已验证候选，比较热点占比推算的上限与完整请求的变化。固定图模式、缓存状态与并发，确认替换实际生效，再解释 TTFT、逐 token 延迟与吞吐的变化；若候选没有收益，沿原始 trace 说明限制。无设备时分析同一组替换前后记录。
>
> 条件：进阶·固定 vLLM／SGLang 与 GPU／配套运行记录。

**实测结果（5-9）：** 同一 eager 引擎上实际替换 36 层 SwiGLU，原生与选定 schedule 共 11 对固定 7,239／32 token 请求，全部输出一致；TTFT 未改善，总时延只有微小波动，不作为稳定收益。两份同口径完整 Nsight 显示该热点只占 1.597%，decode 局部缩短而 prefill 不变，热点与其他内核的并发交集为 0——条件上限由此明确：即使把热点清零，完整请求也快不了多少。其他形状、并发与稳态摊销仍待。[替换审计、trace 与限制](../experiments/ch05/05-09/README.md)。

**实测（部分）：** [36层实际替换记录](../experiments/ch05/05-09/README.md)中，11对固定请求输出一致，TTFT未见改善，总时延配对中位数仅缩短1.34ms（基线约817ms），不足以认定稳定收益。局部Graph加速不能直接移用到eager请求。 同口径完整trace中，原生热点仅占采集区间约1.60%，候选主要缩短decode激活，prefill几乎不变。

> **图 5-8：同一引擎内优化前后的完整请求（配图计划）**
>
> 用实验 5-9 的同条件记录展示候选进入执行路径的证据、prefill／decode 时间分解与请求完成时间；教学关键路径另作面板并标明输入性质。Ollama 后端图随 5.5.1 的延伸材料阅读。

**扩写资料：** [本节完整计算、版本与实验变体](extensions/05-%E7%AE%97%E5%AD%90%E4%B8%8E%E8%BF%90%E8%A1%8C%E6%97%B6.md#detail-5.6)。

## 本章的设计决定

为两条主算子链保存分块、布局、融合边界及缓冲生命周期，对照预测和完整请求 trace。明确局部收益在哪个并发条件下失效；将真实状态和交接需求交给第 6 章。 将预测、证据和修改分别填入[跨章设计决定](decision-record.md)。

## 写作资料

- 选读原稿：[StreamTensor](../references/proceedings/MICRO/2025/paper-014.pdf)，仅采用配套笔记所列设计与实验范围。

- 5.3 的流式交接：[顺序、累计生产／消费与缓冲预算](../case-studies/stream-order-and-buffer.md)；StreamTensor 的 FPGA 与 GPU 比较条件见配套阅读记录。

- 5.2–5.3 的容量与复用：[Orojenesis，ISCA 2024 作者公开稿](../references/proceedings/ISCA/2024/public/paper-011-author.pdf)、[Qwen3 分块计数与读取范围](../case-studies/buffer-capacity-and-data-movement.md)。

- 公开考核、Agent 记录与方案审阅：[证据、推算及实验条件](../case-studies/evaluation-and-agent-records.md)。

- 5.5 的图段与拷贝取舍：[GraCE，OSDI 2026](../references/proceedings/OSDI/2026/selected/osdi26-ghosh.pdf)、[vLLM 2024–2026 与 SGLang BCG 的来源](../references/framework-history/2026-09-08/graph-selection/README.md)、[教学时间、padding 和适用条件](../case-studies/graph-execution-tradeoffs.md)。

- 归约与可复现性：[同形状重复、batch 变化和跨引擎的数值对照](../case-studies/rl-state-and-reproducibility.md)，接第 8、10 章的真实推理框架实验。

- 并发下的性能反馈：[NanoFlow 正式会议稿](../references/proceedings/OSDI/2025/selected/osdi25-zhu-kan.pdf)、[切分与争用推算](../case-studies/resource-sharing-and-placement.md)。

- 注意力流水与实际后端：[FlashAttention-4，MLSys 2026](../references/proceedings/MLSys/2026/papers/mlsys2026-ae8b0b5838ba510daff1198474e7b984.pdf)、[固定 CuTeDSL、vLLM／SGLang 路径](../references/framework-history/2026-09-08/attention/README.md)。

- 动态规划与图执行：[FlashInfer，MLSys 2025](../references/proceedings/MLSys/2025/papers/mlsys2025-dbf02b21d77409a2db30e56866a8ab3a.pdf)、[当前 Attention API 快照](../references/framework-history/2026-09-07/flashinfer/attention.html)。历史版本与教学推算见[执行与状态取舍笔记](../case-studies/cache-and-reconfiguration.md)。

- 近两年框架演进：[SGLang Advanced CUDA Graph，2026-08](../references/outline-checks/2026-09-07/framework-evolution/sglang-graphs.html)、[Ollama MLX 预览，2026-03](../references/outline-checks/2026-09-07/framework-evolution/ollama-mlx.html)、[Ollama MLX 多 token 预测，2026-06](../references/outline-checks/2026-09-07/framework-evolution/ollama-mtp.html)。章节与实验对应见[框架演进笔记](../case-studies/framework-evolution.md)。

- 新增性能反馈与运行方式：[KernelAgent](../references/outline-checks/2026-09-07/execution-feedback/kernelagent.html)、[FlashInfer-Bench](../references/outline-checks/2026-09-07/execution-feedback/flashinfer-bench.html)、[CUDA Agent](../references/outline-checks/2026-09-07/execution-feedback/cuda-agent.pdf)、[TVM MetaSchedule](../references/outline-checks/2026-09-07/execution-feedback/tvm-meta-schedule.html)、[Ansor](../references/outline-checks/2026-09-07/execution-feedback/ansor.pdf)、[MPK v2](../references/outline-checks/2026-09-07/execution-feedback/mpk-v2.html)、[vLLM CUDA Graphs](../references/outline-checks/2026-09-07/execution-feedback/vllm-graphs.html)。落点与实验范围见[执行优化笔记](../case-studies/execution-feedback.md)。

- 5.2–5.4 的研究与编译：[AKG: Automatic Kernel Generation for Neural Processing Units using Polyhedral Transformations](../references/files/papers/akg-pldi21.pdf)；[TVM: An Automated End-to-End Optimizing Compiler for Deep Learning](../references/files/papers/tvm.pdf)；[TensorIR: An Abstraction for Automatic Tensorized Program Optimization](../references/files/papers/tensorir.pdf)；[Presburger Formulas and Polyhedral Compilation](../references/files/documents/isl-tutorial.pdf)。
- 5.3 的算法与实现演进：[FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](../references/files/papers/flashattention.pdf)；[FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning](../references/files/papers/flashattention2.pdf)；[FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision](../references/files/papers/flashattention3.pdf)。
- 5.4–5.5 的同题比较：[Triton Tutorial: Matrix Multiplication](../references/files/documents/triton-matmul.html)；[CANN 8.1.RC1.alpha002 Ascend C 算子开发指南](../references/files/specs/ascend-c-guide.pdf)；[NVIDIA Hopper Tuning Guide](../references/files/documents/nvidia-hopper-tuning.html)；[Serving Large Language Models on Huawei CloudMatrix384, v2](../references/files/papers/cloudmatrix384-v2.pdf)。
- 5.5 的图执行：[CUDA Graph Best Practice for PyTorch: CUDA Graph](../references/files/documents/cuda-graphs.html)；[vLLM CUDA Graphs Design](../references/files/documents/vllm-cuda-graphs.html)。
- 5.5.1 延伸的实际后端：[Ollama v0.20.7 Apple device and working-set discovery](../references/files/documents/ollama-metal-device.txt)；[Ollama v0.20.7 bundled ggml Metal kernels](../references/files/documents/ollama-ggml-metal-kernels.txt)；[Ollama v0.20.7 bundled ggml Metal device and buffers](../references/files/documents/ollama-ggml-metal-memory.txt)；[MLX official README](../references/files/documents/mlx.md)；[KTransformers 0.3 AMX design notes](../references/files/documents/kt-amx.md)。

- 5.4 的具体模型与实现：[模型与算子核对笔记](../case-studies/model-operator-examples.md)；[Qwen3 固定实现](../references/outline-checks/2026-09-07/scaling-history/vllm-qwen3.py)；[V4-Flash 官方参考实现](../references/outline-checks/2026-09-07/scaling-history/deepseek-v4-flash-inference-model.py)。

原文版本、参数差异与扩写时需补的材料见[编辑笔记](editorial-notes.md#ch-05)。
