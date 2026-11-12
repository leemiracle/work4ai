# 讲透 CUDALibrarySamples（NVIDIA/CUDALibrarySamples）

> NVIDIA CUDA 库官方示例总仓（25 个库域目录，1714 分析文件）的全链路知识库：DeepWiki 抓取 + understand 图谱 + ONBOARDING + explain 12 篇。
> 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/CUDALibrarySamples/`

## 全链路状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| DeepWiki | `deepwiki/`（overview+域页） | ✅ 完成（2026-10-26 轮） |
| understand 图谱 | 仓内 `.understand-anything/knowledge-graph.json`：**3189 节点 / 4547 边 / 16 层 / 16 步 tour / validator 0 issues / fingerprints 1714 文件 @ `07c4f092`**（2026-11-07 分析） | ✅ 完成 |
| ONBOARDING | `onboarding/ONBOARDING.md`（8 节，行号锚源码核实） | ✅ 完成 |
| explain 12 篇 | 本目录 `explain/01-12`（每篇 1500-2500 字符不计空格，六节结构，行号锚 10+） | ✅ 完成（组 1：01-06；组 2：07-12） |

## explain 索引（12 篇）

**组 1 · 稠密/稀疏代数主线**
1. `explain/01-cuBLAS经典主线.md` — Level-1/2/3 BLAS 教学阶梯与 cublas_utils 枢纽
2. `explain/02-cuBLASLt.md` — FP8→MXFP8→NVFP4 精度阶梯与启发式
3. `explain/03-cuBLASMp.md` — MPI+NCCL 张量并行算子田
4. `explain/04-cuSPARSE谱系.md` — 稀疏算子全谱系与格式矩阵
5. `explain/05-cuSPARSELt.md` — 2:4 结构化稀疏张量核
6. `explain/06-cuSOLVER家族.md` — 稠密分解到稀疏直接求解

**组 2 · FFT/随机/图像/专用域**
7. `explain/07-cuFFT与LTO.md` — LTO callback 四件套：`__device__` 回调+fatbin→bin2c 嵌入+cufft_utils 枢纽
8. `explain/08-MathDx枢纽链.md` — Dx 四族 common 头链+libmathdx+NVRTC arch 选项双拼法
9. `explain/09-cuRAND.md` — 引擎×分布矩阵、Host API 语义修正、nvcc/g++ 分野
10. `explain/10-图像三库.md` — nvJPEG ROI 693 行支撑头、nvJPEG2000 编码器两遍取流、vendored 甄别
11. `explain/11-NPP双平行.md` — NPP/NPP+ 同构对照（`nppi*` vs `nppPlusV::`）+dirent.h vendored
12. `explain/12-cuEST与cuTENSOR.md` — 量子化学最大域（RHF/UHF 双子）+cuTENSOR TF/torch einsum 双栈

## 勘误清单（14 条，全部源码核实 @ `07c4f092`）

**上游仓库内容勘误（README/构建脚本 vs 实际代码）**
1. **cuSPARSE/sddmm_bsr 标题误写 CSR**：`sddmm_bsr/README.md:1` 标题作 `cusparseSDDMM CSR`、:5 正文与 :13 配图（sddmm_csr.png）均称 CSR 存储；实际代码建的是 BSR 稀疏矩阵（`sddmm_bsr_example.c:160` `cusparseCreateBsr`）——标题从 sddmm_csr 复制后未改。
2. **cuSPARSE/axpby 标题误写 SpVV**：`axpby/README.md:1` 标题作 `cusparseSpVV`，正文 :5 讲的却是 `cusparseAxpby`（稀疏向量缩放累加）。
3. **cuSPARSE/scatter 文档链接锚误挂**：`scatter/README.md:7` 链接锚指向 `#cusparse-generic-function-spvv`，应为 scatter 自己的锚——SpVV 锚复制残留。
4. **cuSPARSE/spgemm_mem 与 spgemm README 完全同题**：两目录 README 标题均为 `cusparseSpGEMM`（仅 nvcc 命令行与 CUDA 版本要求两行不同）；spgemm_mem 的差异化 API `cusparseSpGEMM_estimateMemory`（`spgemm_mem_example.c:154/:164`）在标题层完全不可见。
5. **cuSPARSE/graph_capture Makefile 双横线**：`graph_capture/Makefile:18` 写作 `LIBS := --lcusparse`，全 cuSPARSE 其余 Makefile 均为单横线 `-lcusparse`（axpby/scatter/spgemm/sddmm_bsr 逐一对拍）——双横线传入会被编译器当未知长选项。
6. **cuRAND README sobol32 条目误写 scrambled**：`cuRAND/README.md:93-95` SOBOL32 条目描述为 "scrambled sobol32"，与 ：125 起的真 scrambled_sobol32 条目复制错位；sobol32 示例实际用 `CURAND_RNG_QUASI_SOBOL32` 无 scrambling（`curand_sobol32_uniform_example.cpp:48`）。
7. **nvJPEG2000 README 两处**：`nvJPEG2000/README.md` Examples 清单只列三个 Decoder，**Encoder 示例（1292 行，本域最大）缺席**；第三条链接写作 `nvjpeg2000-Decoder-Tile-Partial/`，实际目录名 `nvJPEG2000-Decoder-Tile-Partial`——大小写不匹配在大小写敏感文件系统上是死链。
8. **cuSOLVER/gesv 目录名与内容错位**：目录名 gesv，内含 `cusolver_irs_expert_cuda-10.2.cu`/`cusolver_irs_expert_cuda-11.cu`/`cusolver_irs_lapack.cu` 全套 IRS（迭代求精）示例；README:1 自述 "iterative refinement solver example"——目录应叫 irs 更准确。
9. **cuBLASLt/LtSgemmGreenContext 命名陷阱**：目录名 `...GreenContext` vs 源文件名 `sample_cublasLt_LtSgemmGreenCtx.cu`（后缀两种缩写）；且示例主体不是 cuBLASLt 新 API，而是 CUDA Green Context 家族：`cudaDevSmResourceSplitByCount`（:52）→`cudaGreenCtxCreate`（:54）→`cudaExecutionCtxStreamCreate`（:55）→`cudaExecutionCtxDestroy`（:114），cuBLASLt GEMM 只是跑在其上的负载。
10. **cuRAND/Host 目录语义修正**："Host" 指**宿主 API 族**而非"仅宿主执行"——每个示例都双跑 device 路径（`curandCreateGenerator`，philox 例 :48）与 host 路径（`curandCreateGeneratorHost`，:84）对照打印。
11. **NPP watershed 薄厚不对称**：NPP 版仅 115 行单图循环（`watershedSegmentation.cpp:91-96`），NPP+ 版 503 行含批量/多 pass/着色（`watershedSegmentationNPPPlus.cpp:232/:261/:384/:444`）——按"NPP 示例完整"直觉读 NPP 版会漏功能；另 NPP/nppCanny 目录内含 Python 孪生 `npp_canny_simple.py`，"NPP=纯 C++"是错觉。

**图谱构建管线勘误（scanner/tree-sitter 侧）**
12. **tree-sitter 对 `cu` 语言全盲**：scan-result.json 中 351 个 `.cu` 文件符号提取数为 **0**（language 标记 'cu' 无对应 parser）；最终图谱中 .cu 文件的 511 个 function 节点+2 个 class 节点全部来自批阶段 worker 手工/脚本补齐——引用 .cu 域函数级节点时须知道其出处是人工对账而非机器提取。
13. **大括号补扫器两 bug**：为补 .cu 盲区而用的字符级大括号配对器在构建期暴露两处缺陷（主会话构建实录），均由批阶段甄别修正；`tmp/cuest-helper-funcs.json`、`tmp/lt-mp-funcs.json` 保留了 cuEST 与 cuBLASLt/Lt cuBLASMp 两域的手工函数清单（含行号区间）可复核查证。
14. **CMakeLists.txt/Makefile 的节点类型重分类**：scanner 将全部 CMakeLists.txt 按 txt/docs 裸分类，构建期批量甄别为 config 节点、Makefile 归 pipeline 节点（NOTES-DIGEST 30+ 条记录）；引用这两类节点时类型语义已与原始 scan 输出不同。

## 与图谱/tour 的对应

explain 组 2 六篇分别锚定 tour 步 t07（cuFFT/LTO）、t08（MathDx）、t10（cuRAND）、t12（图像域）、t13（cuEST）、t14（cuTENSOR）；组 1 对应 t02-t06/t09。层级地图见 `onboarding/ONBOARDING.md`。
