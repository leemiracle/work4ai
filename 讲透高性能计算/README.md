# 讲透高性能计算（HPC for AI）

> **HPC 是 AI 的物理层。** 大模型的一切"慢/贵/爆显存"，最终都能还原成三件事：算力天花板（Roofline）、数据搬运（内存层级与带宽）、并行极限（Amdahl 定律）。本系列把这些**第一性原理**讲透，并用 **MLSys 2019–2026 全部 448 篇论文**作为实证锚点——每个原理在顶会系统论文里如何被利用/被绕过/被推翻。
>
> **三系列分层**（互不重叠）：
> - **本系列（物理层）**：为什么快不起来——定律、数学、数值格式
> - [`讲透GPU与系统级`](../讲透GPU与系统级/)（kernel 层）：怎么写得快——FlashAttention/CUDA/Triton/vLLM
> - [`讲透分布式AI系统`](../讲透分布式AI系统/)（策略层）：怎么切模型——DDP/ZeRO/TP/PP/Ray

---

## 篇目表（目录宪法）

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [为什么 AI 工程师必须懂 HPC](./00-开场-HPC是AI的物理层.md) | ✅ | 物理层世界观、三系列分层图、MLSys 会议地图 |
| **01** | [Amdahl 定律与并行极限](./01-Amdahl与并行极限.md) | ✅ | 串行 fraction 卡死加速比、Gustafson、通信修正项 |
| **02** | [Roofline 模型](./02-Roofline算力天花板.md) | ✅ | 算力 vs 带宽双限、arithmetic intensity、GEMM 三笔账 |
| **03** | [内存层级与缓存](./03-内存层级与缓存.md) | ✅ | AMAT、cache line、分块、recomputation 换算力 |
| **04** | [SIMD 与向量化](./04-SIMD与向量化.md) | ✅ | 数据并行指令、numpy 向量化实测、sub-8bit SIMD |
| **05** | GPU / MACA 体系结构（大纲） | 🟡 | SM/warp/HBM 拓扑；深入 kernel 见 [`讲透GPU与系统级/06`](../讲透GPU与系统级/06-CUDA-kernel.md) |
| **06** | [集合通信数学](./06-集合通信数学.md) | ✅ | Ring AllReduce 通信量 2(N−1)K/N 与卡数无关、树 vs 环、in-network 聚合 |
| **07** | [混合精度数值](./07-混合精度数值.md) | ✅ | FP16/BF16/FP8 位宽分解、loss scaling 数学、量化误差 |
| **08** | [集群调度与容错](./08-集群调度与容错.md) | ✅ | 排队论/等待成本、checkpoint 平方根公式、gang scheduling、straggler |
| **09** | [性能分析方法论](./09-性能分析.md) | ✅ | 测量科学（SE/CI/Karp-Flatt/三层保真度）+ 1.5 节方法论正典（Gregg USE/TMAM/Queue） |
| **10** | [批判收尾：HPC 的代价](./10-批判收尾-HPC的代价.md) | ✅ | 能耗/复杂度/基准谬误/"好算法打败好硬件" |
| 📚 | [`mlsys-papers/`](./mlsys-papers/README.md) | ✅ | **MLSys 2019–2026 全 448 篇分届目录 + HPC 主题地图** |
| 🎓 | [`resources/`](./resources/README.md) | ✅ | **课程×书×GPU×HPC 资源中心**：9 门课深读卡（10-414/15-442/智能计算系统/6.5940/MLC/CSE234/CS149×15-418/6.172）+ perf-book + gpuengineering/gpumode + awesome-hpc |
| 📝 | [`blogs/`](./blogs/README.md) | ✅ | **四源博客知识体系 + 35+ 博客逐家深读卡（deepreads/）**：Gregg 方法论 / Lemire CPU 学派 / Milovidov 清单全量展开 / ACM Queue 正典；配套六聚类 skills（blog-cpu-kernels 等） |

---

## 怎么用

- **想懂"为什么慢"**：00 → 01 → 02（Amdahl + Roofline 两大定律是全系列钥匙）
- **想读懂 MLSys 论文**：00 → 本科兴趣章 → 对着 [`mlsys-papers/主题地图`](./mlsys-papers/README.md) 按主题切片读
- **想优化自己代码**：03 → 04 → 09（缓存 + 向量化 + profiling 是 CPU 侧三板斧），工具书 [`resources/perf-book`](./resources/perf-book.md)、方法论 [`blogs/`](./blogs/README.md)
- **想系统上课**：[`resources/courses/`](./resources/courses/README.md) 课程矩阵 + 四条学习路径（AI 工程师 / kernel 工程师 / 国产硬件 / 推理优化）
- **做大模型训练/推理**：06 → 07，然后进 [`讲透分布式AI系统`](../讲透分布式AI系统/) 与 [`讲透GPU与系统级`](../讲透GPU与系统级/)

## 实验环境声明

- 本系列全部实验**纯 CPU 可跑**（本机 ARM Linux 验证），零 GPU 依赖——HPC 的定律在玩具规模即可复现
- 实验脚本：[`experiments/`](./experiments/)（每篇配 png）；练习：[`exercises/EXERCISES.md`](./exercises/EXERCISES.md)
- 远程 13 节点（2×C500 / MACA）作为上机延伸：见 `remote/` 脚本群

> 🔗 数学优化与性能优化之桥见 [`讲透优化`](../讲透优化/README.md)（其 26 章为两系列方法论合流点）。

## 📚 MLSys 论文库（本系列实证锚点）

[`mlsys-papers/`](./mlsys-papers/README.md)：8 届 448 篇（2019:32 / 2020:34 / 2021:52 / 2022:51 / 2023:46 / 2024:37 / 2025:61 / 2026:135），**全部一手核实**于 proceedings.mlsys.org（2026-09-02 抓取）。

---

🔗 交叉链接：[`高效AI前沿-2025-2026顶会精选.md`](../高效AI前沿-2025-2026顶会精选.md)（MLSys 2025-26 推理方向精选）· [`前沿与媒体/12-AI硬件与算力专题.md`](../前沿与媒体/12-AI硬件与算力专题.md)

🔗 理论锚点：Amdahl/Roofline 的形式化边界 ↔ [`讲透复杂系统`](../讲透复杂系统/)（约束与瓶颈的普适数学）；能耗批判 ↔ 复杂系统四视角之热力学视角

> 🔗 **源码深读专区（2026-09-03 补）**：本系列讲物理层定律，源码级延伸见 `../讲透PyTorch源码/`（DeepWiki 80 页+KG 4730 节点）与 `../讲透vLLM/`（64 页+11615 节点）；统一组织轴=四层编译管线（Python→算子图→算子→硬件指令），总索引 `/data/usershare/ai/hpc-agent/docs/FOUR-LAYER-PIPELINE.md`。
