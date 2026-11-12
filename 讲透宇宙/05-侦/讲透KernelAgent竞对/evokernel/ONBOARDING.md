# EvoKernel 数据集上手指南（ONBOARDING）

> 本指南基于仓库知识图谱（`.understand-anything/knowledge-graph.json`，86 节点/136 边/5 层/9 步导览，中文）与 README 生成。**图谱为采样式**：只收录全部 5 个 manifest、README 及每集合代表性 kernel 的完整解剖（如 AdaptiveAttentionCustom、FusedMhcKernelsCustom、ArgmaxOverADimensionCustom 及两个 CUDA best_code 样本）；**全集统计以审计报告的数字为准**（见 §1）。

## 1. 数据集 Overview

EvoKernel 是配套论文 **arXiv:2603.10846《Towards Cold-Start Drafting and Continual Refining: A Value-Driven Memory Approach with Application to NPU Kernel Synthesis》** 发布的 HuggingFace 数据集（noahli/EvoKernel）。论文方法定位三个关键词：

- **值驱动记忆（value-driven memory）**：agent 维护一个按"价值"筛选的 kernel 经验库，高价值条目驱动后续合成；
- **冷启动起草（cold-start drafting）**：新任务无历史时，从记忆检索相近经验直接起草初版 kernel；
- **持续精修（continual refining）**：以迭代评测反馈（910B 侧编译/正确性，CUDA 侧 NCU 性能剖析）不断精修候选。

本仓是**数据资产**而非代码仓：agent 框架本体**未开源**（evokernel.zhuo.li 仅为项目页），开源的是合成产物与任务定义。

**规模（审计数字）**：五个导出集合共 **567 个 kernel**——Ascend 910B 侧 58 attention + 15 MHC + 165 KernelBench 迁移算子，CUDA NCU 侧 79 attention + 250 KernelBench 选优产物；另有 `ops-exports-bundle.zip` 打包归档与 344 个 PyTorch 参照任务。**质量分布**：correctness 方面 910B attention、910B KernelBench、CUDA KernelBench 三合集均为 100%，CUDA attention 为 97.5%（79 中 2 失败），**MHC 分化最大（66.7%**，10/15 通过，5 个迭代触顶仍未编译）。**迭代量级**：outer_iter 中位数约 **21**（主体落在 18–30 并向上限集中），inner_iter 恒为 1。

语言与框架：Python / C++ / JSON / Markdown；PyTorch、Ascend CANN（op_host/op_kernel）、CUDA、HuggingFace Datasets。

## 2. 结构分层（5 层）

图谱将数据集划为五层（层内节点为采样代表）：

| 层 | 名称 | 内容 |
|---|---|---|
| L1 | **数据集定义层** | README 数据集卡片 + 5 个合集 `manifest.json`，承载 567 kernel 的编译率、正确率、outer_iter 分布等全局统计 |
| L2 | **Ascend 910B CANN 算子实现层** | 三个采样算子（AdaptiveAttention/ArgmaxOverADimension/FusedMhcKernels）的完整工程，统一遵循 op_host → op_kernel → CppExtension 三层布局 + 算子接口 json 契约 |
| L3 | **CUDA NCU 迭代选优产物层** | NCU 迭代选优终版 `best_code.py`（torch `load_inline` 内联 CUDA 源码而非 triton），attention 与 KernelBench 各采样一个，体现 warp 级快路径、向量化双路等选优痕迹 |
| L4 | **评测元数据层** | 5 个采样点的 `result.json` 单点评测记录（outer_iter/compiled/correctness/performance），其中 MHC 样本是带扩展 schema 的编译失败样本 |
| L5 | **PyTorch 参照任务层** | 与合成 kernel 一一对应的参照任务，统一 get_inputs/get_init_inputs/Model 三件套协议，是正确性与性能基线的源头 |

数据流向：**L5 定义任务 → agent 合成（L2 CANN 工程或 L3 CUDA 单文件）→ L4 记录单点结局 → L1 汇总为合集总账**。

## 3. 关键概念

**manifest schema**：每个合集根部的 `manifest.json` 是该合集的采样清单与质量总账，逐 kernel 记录迭代轮数、编译与正确性、性能统计（MHC 合集还含 mean_ms/基线耗时/加速比），并附 outer_iter 分布。做任何全集级分析先读 manifest。

**outer/inner iter**：评测记录中的迭代字段。outer_iter 反映"精修轮数"，中位数约 21，各合集上限不一（多数 30，**MHC 上限 39**——其 5 个失败样本恰好全部触顶 39，是"迭代预算耗尽"的直接证据）；inner_iter 全数据集恒为 1。

**CANN 三层布局**（910B 每个 kernel 目录的标准形态）：
1. **op_host**：CPU 侧调度决策。TilingFunc 从输入 shape 推导切分参数写入 tiling buffer（如 B/H/S/D → totalRows/sTile/dTile）；复杂算子还带动态 shape 推理（FusedMhcKernels 的 InferN 由输出列数反推 n=floor(√outCols)、Ceil8 对齐）。
2. **op_kernel**：AscendC 设备实现，Init/Process 生命周期；`*_tiling.h` 定义的 TilingData 结构体是 host↔device **唯一数据通道**（op_host 生产、op_kernel 经 GET_TILING_DATA 消费）。
3. **CppExtension**：PyTorch 桥接——check_inputs 校验后经 EXEC_NPU_CMD 启动算子，TORCH_LIBRARY(_IMPL) 注册 NPU/PrivateUse1 后端，PYBIND11_MODULE 导出 Python 接口。
另有算子接口 `.json` 声明输入输出契约（如 FusedMhcKernelsCustom 声明 10 输入 3 输出）。

**best_code**：CUDA 合集的终版产物形态——单文件 `best_code.py`，经 `torch.utils.cpp_extension.load_inline` 内联 CUDA 源码（**非 triton**），带 `--use_fast_math -O3`。优化指纹示例：attention 样本 D==64 走每 warp 2 query 的 warp 级 flash-attention 快路径（无共享内存无 __syncthreads）；KernelBench 样本 vec4/scalar 双路 + 2× ILP + occupancy 感知 grid + 单 kernel epilogue 融合。

**pytorch 参照协议**：`pytorch-references/` 下任务统一采用 **get_inputs / get_init_inputs / Model 三件套**（与 KernelBench 上游同构），既定义正确性比对真值，也提供性能基线。四个任务族各有代表性：Attention 族含动态路由（MHA/GQA/MQA 按样本选择）；KernelBench L1→L3 构成从单算子（HingeLoss）到融合链（ConvTranspose3d+clamp+divide）再到整网（ResNet-101）的复杂度阶梯；MHC 族为对数域 Sinkhorn-Knopp 双随机归一化。注意个别任务存在配置透传不完整的小漂移（如 Attention/10 的 get_init_inputs 未透传 n_kv_heads_options，靠模块级默认值兜底；ResNet-101 的 docstring 提及 block 参数但签名不含）——复现基线时应以 Model.__init__ 实际签名为准。

**correctness/performance 字段口径**：910B 与 CUDA 标准记录为六字段（outer_iter/inner_iter/compiled/correctness/performance.mean 等）；CUDA 合集带 `num_trials=5`，**910B 合集 num_trials=null**；**MHC 是唯一带 speedup_vs_baseline 字段的集合**（扩展 schema：mean_ms/speedup_vs_baseline/log2_speedup/relative_change_pct/baseline_mean_ms）。编译失败样本的扩展字段全 null（correctness 亦为 null）。

## 4. Guided Tour（9 步）

1. **数据集卡片总览**：从 README.md 认识五大合集（567 kernel）与参照任务的组织方式。
2. **五大合集统计清单**：读 5 个 manifest 总账——910B 三合集编译/正确率均 100%，CUDA attention 97.5%；MHC 分化最大（最优 SinkhornKnoppCustom 加速 41.96×，最差反慢约 86×，5 个触顶 39 未编译）；对照 outer_iter 分布（众数 29/30 集中于上限）读出迭代预算消耗模式。
3. **910B 三层布局（上）**：以 AdaptiveAttentionCustom 看 `adaptive_attention_custom.json` 接口契约（q/k/v→y）与 op_host 的 TilingFunc 切分推导。
4. **910B 三层布局（下）**：op_kernel 的在线 softmax(QK^T)·V（LoadKTile/LoadVTile 搬入 UB、在线归一化）与 CppExtension 的校验→EXEC_NPU_CMD→TORCH_LIBRARY 注册链路，闭合"tiling 决策→设备执行→框架桥接"。
5. **MHC 融合核**：FusedMhcKernelsCustom 是承载力上限——10 输入 3 输出、唯一动态 shape 推理、431 行设备代码按行融合 RMSNorm→GEMV→Sinkhorn-Knopp（N4 特化 + log-space 防溢出 Generic 双路径）、最厚桥接层（9 输入统一设备与 dtype）。"融合度与工程复杂度同增"的最佳教材。
6. **KernelBench 910B 迁移样例**：ArgmaxOverADimensionCustom 结构最简，适合作为 165 个迁移算子的**模板对照**；与 attention 样例对比可见切分契约字段由归约语义决定、三层布局本身不变。
7. **CUDA NCU 迭代选优产物**：两个 best_code.py 对照——warp 级 flash-attention 快路径 vs vec4/ILP/occupancy 感知，两种典型 NCU 优化指纹。
8. **评测元数据对照**：五个 result.json 与第 2 步总账互证——性能从 3.84ms 到 2181ms 跨三个量级；FusedMhcKernelsCustom 是编译失败样本（触顶 39、扩展字段全 null），其 schema 揭示 MHC 协议差异。
9. **PyTorch 参照与评测协议**：回到源头看三件套协议与四个任务族（动态路由 attention、L1→L3 从单算子到 ResNet-101 的复杂度阶梯、对数域 Sinkhorn-Knopp），理解"任务定义→kernel 合成→评测闭环"的最后一环。

## 5. 文件/目录地图

```
EvoKernel/
├── README.md                          # HF 数据集卡片（引用、格式约定）
├── ops-exports-bundle.zip             # 五合集打包归档
├── ops-attention-910b/                # 58 个 CANN attention 算子（correctness 100%）
├── ops-mhc-910b/                      # 15 个 MHC 算子（66.7% 通过；唯一带 speedup 字段）
├── ops-kernelbench-910b/              # 165 个 KernelBench 迁移算子（correctness 100%）
├── ops-attention-cuda-ncu/            # 79 个 CUDA attention（97.5%）
├── ops-kernelbench-cuda-ncu/          # 250 个 CUDA KernelBench（100%）
│   （每个 ops-* 合集根部一个 manifest.json）
└── pytorch-references/
    ├── Attention/                     # 79 个参照任务
    ├── MHC/                           # 15 个参照任务
    └── KernelBench/                   # level1(100)/level2(100)/level3(50)
                                       # + 上游 changelog 与 dataset.json
```

**每个 kernel 目录的构成**：

- 910B 算子（`<OpName>Custom/`）：`<op>.json`（接口契约）+ `op_host/<op>.cpp`（tiling）+ `op_host/<op>_tiling.h`（host↔device 契约）+ `op_kernel/<op>.cpp`（AscendC 实现）+ `CppExtension/csrc/op.cpp`（PyTorch 桥接）+ `result.json`。
- CUDA 任务（`<Task>/`）：`best_code.py`（load_inline 内联终版）+ `result.json`。

## 6. 使用建议与热点

**复杂度热点（谨慎进入区）**：① `ops-mhc-910b/FusedMhcKernelsCustom/op_kernel/`（431 行，全库最复杂设备实现，Sinkhorn 双路径 + 多项式近似 + PipeBarrier）；② `ops-attention-910b/AdaptiveAttentionCustom/op_kernel/`（在线归一化流式计算）；③ 两个 CUDA `best_code.py`（warp 级分支与向量化双路）；④ 5 个 manifest（字段口径不一，见下）。入门正道：先走完 §4 的 9 步，再以 ArgmaxOverADimensionCustom（最简三层布局）做模板通读。

**抽取 kernel 做迁移实验的建议**：
- **从 manifest 分层抽样**：按合集 × correctness（正/负样本）× outer_iter（低/中/触顶）分层，MHC 合集额外可用 speedup_vs_baseline 区分快/慢样本；负样本（MHC 5 个触顶失败 + CUDA attention 2 个失败）是研究"迭代为何失效"的稀缺材料。
- **任务侧锚点**：每个 kernel 都能经编号对回 `pytorch-references/` 的三件套任务（如 910B 的 ArgmaxOverADimensionCustom ↔ KernelBench 参照；CUDA 的 10_AdaptiveAttention/best_code.py ↔ Attention/10_AdaptiveAttention.py），可本地跑 PyTorch 参照复现基线。
- **复用形态模板**：向 910B 迁移新算子时，照抄 ArgmaxOverADimensionCustom 的目录骨架，只改 tiling 字段与归约语义；CUDA 侧则以 best_code.py 的 load_inline 单文件形态为容器。
- **迭代维度可作分层轴**：outer_iter 中位数约 21 且向上限集中（多数合集上限 30），意味着相当比例 kernel 是"预算耗尽前最后一次通过"——做迭代效率研究时可按 outer_iter 分桶（≤10 快通 / 11–25 常规 / 触顶）对照正确率与性能。
- 910B 工程与 CUDA 单文件是两种不可混评的产物形态，跨后端结论须分别陈述；同后端内亦有合集差异（attention-910b 的 manifest 标注 faster_than_baseline=0，即全部正确但无一快过基线，与 MHC 的 6/15 快于基线形成对照——挑选"有加速故事"的样本时须先核对 manifest）。

**评测口径注意（易踩坑）**：
- **`performance.mean` 跨集合单位/协议可能不一致**——采样点从 3.84ms 到 2181ms 跨三个量级，且 910B 无 num_trials（null）、CUDA 为 5 trials；跨集合比较性能前先核对 manifest 字段与量纲，不要直接拉通排名。
- 正确性口径：失败样本的 correctness 为 null（非 false），统计通过率时须区分"未编译/未评测"。
- MHC 扩展 schema（speedup 等）与其他四集合标准六字段不同，合并分析需做字段对齐；其 outer_iter 上限 39 也与其他合集（30）不同。
- 图谱为采样式：以本指南定位代表样本，全集结论务必回到 manifest 与审计数字。

**引用**：使用本数据集请按 README 尾部 bibtex 引用（zheng2026evokernel，arXiv:2603.10846）；agent 框架本体不在本仓，复现方法侧需参考项目页 evokernel.zhuo.li。
