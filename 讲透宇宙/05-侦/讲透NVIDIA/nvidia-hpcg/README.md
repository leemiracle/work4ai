# 讲透 nvidia-hpcg（NVIDIA/nvidia-hpcg）

> NVIDIA 版 HPCG 基准：HPCG 3.1 的 NVIDIA 加速改写——SELL-P 重排 + cuSPARSE/NVPL Sparse 下沉
> + GPU-only/CPU-only(Grace)/GPU+CPU 异构三模式。本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-hpcg`（commit abe78e0，Build v0.6.2）。

## 流水线状态

| 步骤 | 状态 | 产物 |
| --- | --- | --- |
| DeepWiki 全量抓取 | ✅ 既有 | `deepwiki/`（15 内容页=5 章+10 子页，wiki_full.md 142KB，含 INDEX/_coverage-check） |
| understand 图谱 | ✅ 2026-11-09 | 仓内 `.understand-anything/knowledge-graph.json`：258 节点/481 边/10 层/12 步 tour，fingerprints 126 文件基线@abe78e03（meta/project.name=nvidia-hpcg，hubs 为 src/SparseMatrix.hpp 等本仓实体，已复核自洽） |
| onboarding | ✅ 2026-11-09 | `onboarding/ONBOARDING.md`（5798 非空白字符，8 节，64 唯一行号锚——**源码直读法**，锚逐条核实） |
| explain | ✅ 2026-11-09 | `explain/` 2 篇：01-CudaKernels.cu GPU 单体（3225 字/32 锚）、02-SELL-P 重排+MIDR 派发+hpcg.sh 亲和（3411 字/36 锚） |

> **勘正注记（2026-11-09）**：本轮初判"仓内图谱被 nvidia-resiliency-ext 串拷污染"系**误报**——写手会话的工作目录恰为 nvidia-resiliency-ext 仓，相对路径读到的 `.understand-anything/` 是父会话仓的图谱（meta 608 文件@af2a108b）。复核本仓绝对路径下 meta（126 文件@abe78e03）与 hubs 全为本仓实体，图谱无污染。三件套按源码直读产出、全部行号锚逐条核实，结论不受影响。

## 源码级实证勘误（vs DeepWiki 快照 / README / 注释）

1. **DeepWiki 切片默认值错误**：wiki 称 `gpu_slice_size: 2048 if not specified`（`deepwiki/wiki_full.md:1796`），实码默认 **4096**（`src/init.cpp:426`）。
2. **DeepWiki 着色机制描述失真**：wiki 称"bit-reversal hashing + **atomic operations** for conflict-free parallel coloring"（`deepwiki/wiki_full.md:2597`）；实际两路径都无原子操作——GPU 靠 min/max 选择天然无写冲突 + thrust 计数/排序（`src/CudaKernels.cu:1459-1498`），CPU 注释明言"Sequential instead of atomics"（`src/CpuKernels.cpp:792`）。
3. **README 夸大 cuSPARSE 门槛**：README:30 要求 "cuSPARSE 12.3+"，运行时实际闸门是 **≥12.2**（`src/main.cpp:387`）；另有第二道 **≥12.5** 闸仅在粗层行数 < slice size 时触发（`src/main.cpp:631`）。
4. **README 低估支持架构**：README:23 只写 Ampere(sm80)/Hopper(sm90)，构建系统实际按 CTK 版本门控追加 Blackwell sm_100/103/120 与 Rubin **sm_107**（`setup/Make.CUDA_X86:186-197`）。
5. **init.cpp 注释与实码反向**：`src/init.cpp:359` 注释"0: CPU only | 1: GPU only"，下一行实码 `iparams[10]==1 ? CPUONLY : GPUONLY`（`src/init.cpp:360`）——0 才是 GPU-only（与 `src/main.cpp:212` 报错文案互证）。
6. **build_sample.sh 条件变量错配**：`build_sample.sh:25-27` 判空的是 `${CUDA_PATH}` 却赋值 `MATHLIBS_PATH`（复制粘贴错误；CUDA_PATH 在 33-35 行再次判空，MATHLIBS_PATH 自身反而无守卫）。
7. **configure 引用不存在的文件**：`configure:44-47` 试图拷贝 `bin/hpcg.dat`，仓库 bin/ 无此文件（只有 `sample-dat/`），cp 静默失败；上游 HPCG 靠它提供默认输入。
8. **MPI_Ibarrier 优化已被编译关闭**：`src/ComputeSYMGS.cpp:160` 仍在传 `use_ibarrier=1`（注释称可改善 Allreduce），但 `ExchangeHaloCuda` 内两处 `MPI_Ibarrier` 均被 `#if 0` 禁用（`src/CudaKernels.cu:1349`、`src/CudaKernels.cu:1387`）——当前构建下是死参数。
9. **守卫宏拼写不一致**：`src/main.cpp:905` 用 `#ifndef HPCG_NOMPI`，全仓其余处均为 `HPCG_NO_MPI`（如 `src/main.cpp:147`）——该拼错的宏永不为真，此 MPI_Barrier 无条件编译。
10. **totalColors 硬编码忽略输出**：`src/OptimizeProblem.cpp:79` 定死 `totalColors=8` 后在 `:89` 直接写 `A->totalColors`，`ColorMatrixCuda` 辛苦算出的 `num_colors` 出参被丢弃（27 点模板 ≤8 色的先验写死）。

## 口径说明

- 字数=不计空格总字符；锚=唯一 `file:line`（可含行区间），全部经 `sed -n`/`grep -n` 对源码核实。
