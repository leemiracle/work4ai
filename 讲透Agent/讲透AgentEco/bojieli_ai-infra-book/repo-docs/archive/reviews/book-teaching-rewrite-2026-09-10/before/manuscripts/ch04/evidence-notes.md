# 第四章证据与实验记录

## 参考文献与计算说明

本章算例的完整输入、推导与原始测量见[配套资料](README.md)。版本、结果校验值、数值检查和图表生成记录保存在配套中；正文与图注给出理解各项结论所需的条件。

### qwen

Qwen3-8B 固定配置、张量索引与模型实现见[模型配置](../../calculations/configs/models/qwen3-8b/config.json)及[投影计算结果](../../calculations/results/projection-qwen3-8b-rtx4090-b256.md)。权重、头数与形状均沿用第二章基线。
### projection

[Q 投影，RTX 4090，M=1](../../calculations/results/projection-qwen3-8b-rtx4090-b1.md)；[M=256](../../calculations/results/projection-qwen3-8b-rtx4090-b256.md)。两项都使用 BF16 输入输出、FP32 累加、dense 与声明的冷内存访问。
### architecture

[加速器架构与执行比较](../../case-studies/accelerator-architecture.md)保存 NVIDIA、昇腾与 Apple 的对应关系及原始文档位置。它是取材与机制分析；实际测量采用本章实验记录。
### tpu

Jouppi 等，*In-Datacenter Performance Analysis of a Tensor Processing Unit*，ISCA 2017，[归档论文](../../references/files/papers/tpu-v1.pdf)，§2—4，特别是结构图、存储及版图面积说明。
### nvidia

[A100 架构白皮书](../../references/files/specs/nvidia-a100.pdf)、[H100 架构白皮书](../../references/files/specs/nvidia-h100.pdf)、[Hopper Tuning Guide](../../references/files/documents/nvidia-hopper-tuning.html)、[Blackwell 技术简报](../../references/files/specs/nvidia-blackwell-brief.pdf)与[CUTLASS Blackwell 功能](../../references/outline-checks/2026-09-07/systems-cases/cutlass-blackwell.html)。SM100／SM120 与具体产品形态分开使用。
### ascend

[昇腾 950 官方架构白皮书](../../references/files/specs/ascend-950-official.pdf)，§4.1—4.1.6；早期 DaVinci 与 CANN 分离架构的页级定位见[比较笔记](../../case-studies/accelerator-architecture.md)。未执行本书昇腾实机实验。
### nonmatrix

[从算子利用率到执行中的等待](../../case-studies/component-utilization-and-overlap.md)，采用 ASPLOS 2025 昇腾算子优化与 PICACHU 的声明正文范围，并对照已固定框架版本；[论文阅读记录](../../references/proceedings/ASPLOS/2025/ascend-components-reading.json)。活动时间分解和 RoPE 工作量是限定条件推算。
### apple

[M2 Pro／Max 官方规格](../../references/files/specs/apple-m2-pro-max.html)、[Apple GPU 架构说明](../../references/files/documents/apple-gpu-architecture.html)、[Metal 存储模式](../../references/files/documents/apple-metal-memory.json)、[M5 GPU Neural Accelerator 官方说明](../../references/outline-checks/2026-09-07/systems-cases/apple-m5-evolution.html)。
### fa4

*FlashAttention-4*，MLSys 2026，[论文](../../references/proceedings/MLSys/2026/papers/mlsys2026-ae8b0b5838ba510daff1198474e7b984.pdf)，§2.2、§3.1.1、公式 1—3 与表 1；[单 SM 独立复算](../../calculations/results/fa4-qwen8-resource-balance.md)。
### precision

[硬件精度审查](../../calculations/HARDWARE-AUDIT.md)、[V4 与 Qwen 逐阶段资源条件](../../calculations/research/stage-resource-bounds/README.md)、[低精度与执行路径调研](../../case-studies/kernel-orchestration-and-quantization.md)。硬件演进与成本归因的采用范围另见[成本下降调研](../../research/token-cost-2023-2026/report.md)。
### quant-exp

[实验 4-2](../../experiments/ch04/04-02/README.md)、[真实路由激活](../../experiments/ch04/04-02/routed-activations/README.md)、[128 元素分组](../../experiments/ch04/04-02/block-scales/README.md)、[单专家模型内替换](../../experiments/ch04/04-02/model-intervention/README.md)。这些实际专家输入来自该实验锁定的模型，不能当作 V4-Flash 专家实测。
### workspace

[实验 4-2 分配器峰值](../../experiments/ch04/04-02/workspace/README.md)。PyTorch allocated、reserved 与整卡显存分开；未把首次调用峰值当成后续峰值。
### capacity

[Qwen3-8B 配置](../../calculations/configs/models/qwen3-8b/config.json)；[存储代际完整结果](../../calculations/results/storage-generation-qwen8-235.md)。本节 BF16、2 GiB 工作区的简单容量例子由正文公式计算，不含完整运行峰值。
### evolution

[从负载变化理解芯片演进](../../case-studies/architecture-evolution.md)，保存片上缓冲、异步搬运与代际资源取舍的文档入口。
### storage

[存储代际比较结果](../../calculations/results/storage-generation-qwen8-235.md)及[计算说明](../../calculations/research/storage-generation-comparison/README.md)。量化采用逐张量、逐行尾组规则；全专家驻留、当前访问和 KV 追加分别计数。
### mess

*Mess*，MICRO 2024，[作者接受稿](../../references/proceedings/MICRO/2024/paper-011.pdf)，选读物理页 3—6；[访存并发算例及限制](../../case-studies/memory-bandwidth-and-concurrency.md)。未采用存在版本疑点的设备延迟表值。
### coordinates

[V4 共享专家搬运坐标结果](../../calculations/results/v4-copy-coordinates-m32.md)与[源级计数说明](../../calculations/research/v4-copy-coordinates/README.md)。未采集所分析内核的最终地址指令、描述符或 HBM 计数器。
### transfer

[Hopper Tuning Guide](../../references/files/documents/nvidia-hopper-tuning.html)、[昇腾 950 白皮书](../../references/files/specs/ascend-950-official.pdf)、[Rubin 官方架构说明](../../references/outline-checks/2026-09-07/systems-cases/rubin-rechecked.html)。采用已归档的机制描述；未将官方平台倍率用于本章定量时间线。
### pipeline

[Qwen 注意力输入流水基线](../../calculations/results/attention-input-base.md)、[矩阵速率翻倍](../../calculations/results/attention-input-matrix-double.md)、[建模与独立检查](../../calculations/research/attention-input-pipeline/README.md)。完成点是 QK 累加器，未含 Softmax、PV 与最终写回。
### handoff

[矩阵—向量交接说明](../../calculations/research/matrix-vector-handoff/README.md)、[32 行两槽直接路径](../../calculations/results/matrix-vector-direct-rows32-slots2.md)。结果来自声明的非抢占调度，不声称全局最优。
### package

[Blackwell 技术简报](../../references/files/specs/nvidia-blackwell-brief.pdf)、[CloudMatrix384 v2](../../references/files/papers/cloudmatrix384-v2.pdf)，§3.3.1 与 §4.2.2、[Vera Rubin 平台](../../references/files/specs/nvidia-rubin-system.html)、[UB 与昇腾核对](../../references/UB-ASCEND-NOTES.md)。CloudMatrix v2 与 v3 的删改在比较笔记中分别保留。
### tpu8

[Inside the Eighth-Generation TPU: An Architecture Deep Dive](../../references/files/specs/google-tpu8.html)，采用归档官方文章对 8t／8i 的任务分工及资源组织说明。
### special

[Groq TSP 论文](../../references/files/papers/groq-tsp.pdf)、[IPU Programming Model](../../references/files/documents/graphcore-programming.html)、[Cerebras WSE-3 数据表](../../references/files/specs/cerebras-wse3-spec.pdf)、[SambaNova SN40L 论文](../../references/files/papers/sambanova-sn40l-paper.pdf)。各产品的容量、聚合带宽与局部访问能力不可互换。
### author

[作者材料与技术判断](../../case-studies/author-context-and-design.md)。Groq 的历史容量观察与专用化经验按各自写作时点使用，历史售价假设不作为现价。
### opentallas

[OpenTallas 案例](../../case-studies/opentallas.md)，采用锁定的 `39b96158d35b24bd2bcd49061a689aea6893d2ed` 分析版本及案例 A、C、F。作者与项目的关系在正文披露；性能、lane 和回本例子分别使用自己的输入范围。
### stage

[逐阶段资源界建模说明](../../calculations/research/stage-resource-bounds/README.md)；实际模型算子范围见[Qwen3-8B prefill128 资源结果](../../calculations/results/stage-resources-qwen8-b1-prefill128.md)。默认缺少速率时不填造完整时间。
### hardware

[硬件来源与精度审查](../../calculations/HARDWARE-AUDIT.md)及[官方基础表](../../calculations/results/hardware.md)。4090 的累加条件反例来自官方 RTX 架构白皮书附录；字段未公开不代表硬件缺失该能力。
### measurement

[实验 4-6 全部说明与原始记录](../../experiments/ch04/04-06/README.md)、[投影计时汇总](../../experiments/ch04/04-06/results/projection-summary.json)、[实际 DRAM／L2 计数](../../experiments/ch04/04-06/results/projection-traffic.json)。常规计时和插桩采集独立，环境非独占。输入为合成张量，并非 checkpoint 权重；两端均对 FP64 参考做容差检查。CUDA 关闭 BF16 reduced-precision reduction，MPS 接口未提供独立的内部 FP32 累加证明。256 行 Mac 复用／轮换原值为 1835.375／1835.224 μs，正文合并表述。单行路径为 cuBLAS GEMV，256 行为 GEMM 加 split-K reduce；兼容内核名称不等于设备架构。配套另有注意力默认路径（MPS math、CUDA FlashAttention）与 256 MiB 复制测试，后者约 192／734 GB/s 为特定 GPU 计时下载荷速率，不是主机传输或直接 DRAM 带宽测量。
### paired

[配对投影费用与平均功率条件](../../calculations/results/paired-projection-unknown.md)。持平比仅描述该墙钟时间代理，不是整模型质量、价格或能耗结论。

### host

主机、DMA 与统一地址的术语见 [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)。本节的 64 MiB、32 GB/s 与 1 TB/s，以及多 die 例子的容量和速率均为独立教学输入，不对应某个具体产品的测量。

### pipeline-extra

本次补充的三槽流水、计算翻倍变体及设计转折点由[教学推导脚本](derive.py)生成，完整时序见[推导数据](teaching-data.json)。原计算项目的枚举为 1、2、4、8 槽；新增三槽计算保存在本章配套。
