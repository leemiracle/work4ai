# NVIDIA/MatX 知识库（讲透MatX）

NVIDIA MatX——C++17 GPU 张量计算模板库（现代 NumPy 替代，header-only，MATX_VERSION 1.1.0 @ce764c01）。
核心架构：**operators/ 惰性算子（CRTP BaseOp）↔ transforms/ 立即执行双层贯穿全库**；cuda/lapack 双后端成对（chol/eig/lu/qr/svd/solve + matmul 六后端 + fft 三实现）；generators/ 零存储数据源；executors/（流/JIT/host）；streaming/ 流式；kernels/ 手写 kernel（含 fltflt 双 float 扩展精度）。

## 全链状态表

| 阶段 | 状态 | 产物 | 关键数字 |
|---|---|---|---|
| L0 deepwiki | ✅ TRUE_100 | [deepwiki/](deepwiki/INDEX.md) | 26 页 |
| 图谱（understand） | ✅ finalize 0 issues | 仓内 `.understand-anything/knowledge-graph.json` | **2884n / 4276e / 16 层 / 15 步 tour** |
| fingerprints | ✅ 基线落盘 | 仓内 `.understand-anything/fingerprints.json` | 1580 文件 @ce764c01 |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) | 11979 字符（不计空格）· 8 节 · 55 锚（抽验 0 坏） |
| explain 深讲 | ✅ 10 篇 | [explain/](explain/) | 44412 字符 · 锚合计 322（去重/篇）· 全量抽验 130+ 零坏 |

图谱分层：L01 根构建 47 / L02 core 张量 41 / L03 operators 惰性 111 / L04 transforms 立即 30 / L05 generators 19 / L06 双后端 28 / L07 kernels+executors 20 / L08 streaming+file_io 7 / L09 test 骨干 117 / L10 test 外围 44 / L11 bench 16 / L12 examples 41 / L13 docs api 259 / L14 docs 教程 71 / L15 vendored rapids-cmake 648 / L16 vendored cpm-cmake 81 = **1580/1580 全覆盖零重复**。

## explain 篇目

| # | 文件 | 主题 | 字符 |
|---|---|---|---|
| 01 | [01-tensor-core.md](explain/01-tensor-core.md) | core 张量三层体系（tensor_t/impl/desc+分配缓存） | 4789 |
| 02 | [02-operators-crtp.md](explain/02-operators-crtp.md) | operators CRTP 惰性层（BaseOp 分派链/类型标记） | 4791 |
| 03 | [03-transforms-exec.md](explain/03-transforms-exec.md) | transforms 立即执行（PreRun/Exec/PostRun 协议） | 4787 |
| 04 | [04-generators.md](explain/04-generators.md) | generators 零存储数据源（JIT 序列化/curand 双引擎） | 4134 |
| 05 | [05-dual-backend-linalg.md](explain/05-dual-backend-linalg.md) | 双后端线性代数（lu 成对/matmul 六后端） | 4788 |
| 06 | [06-fft.md](explain/06-fft.md) | FFT 三实现（cuFFT/cuFFTDx/FFTW+plan 缓存） | 4028 |
| 07 | [07-kernels-executors.md](explain/07-kernels-executors.md) | kernels 手写 kernel + executors（NVRTC 融合/LTOIR 缓存） | 4219 |
| 08 | [08-streaming-fileio.md](explain/08-streaming-fileio.md) | streaming 流式（一引擎三模式/生命周期卫兵）+ file_io | 3589 |
| 09 | [09-test-bench.md](explain/09-test-bench.md) | test 分区（81 算子测）+ bench nvbench + fltflt 基准 | 4510 |
| 10 | [10-docs-vendored.md](explain/10-docs-vendored.md) | docs 三层文档 + examples + rapids-cmake/cpm vendored | 4777 |

## 甄别清单（源码实证勘误）

1. **docs_input/api 实为 259 个 rst**（18 子目录），非任务书所记 217 页——图谱 fingerprints 为准。
2. **set 算子标记实名 `matx_setop`**（set.h:144），`is_matx_set_op` 只是 trait 函数名（type_utils_both.h:252）——常见文档笔误。
3. **file_io 的 CSV 读取整段被注释禁用**（file_io.h:70-98 cuDF 路径注释体）——宣称支持 CSV 读的文档超前于代码。
4. **generator1d.h 是参数化 1D 族骨架而非全部 1D 生成器的基类**（range.h:42 直接继承 BaseOp）。
5. **transforms 双后端子目录不含独立 cuda/lapack 顶层目录**——chol/eig/lu/qr/svd/solve 的 *_cuda.h+*_lapack.h 成对内嵌于 transforms/ 下（2+2+2+2+5+2=15 文件）+matmul 六后端 6+convert 3+fft 4=28 文件。
6. **public/ 下另有 rapids-cmake.txt/subtreeInstructions.txt 两个 subtree 指针**（vendored 层 81=79+2）。
7. **fft_common.h 共享的是类型推导**（ComplexInType/DeduceFFTTransformType），参数结构各后端自定义（FftCUDAParams_t/FftFFTWParams_t）。
8. **JIT 缓存双级**：LTOIR 按 cubin 文件名（nvrtc_helper.h:792-806）+ launch 参数按 device+sm（jit_cuda.h:133/:143）。
9. **BaseOp::run 分派链五路**（jit/dynamic-rank拒绝/mtie/set_op 四细分/PreRun-Exec-PostRun，base_operator.h:181-300）——dynamic-rank 表达式只能走 CUDAJITExecutor。
10. **hamming 窗 size==1 特判返回 1**（hamming.h:96）；fftfreq 是 NumPy 交错序语义。

## 流水线备注

- 1308 团灭一次（06:08 写作期，4 子代理+主会话同窗）：01/03/05 由死代理死前落盘+主会话查盘验收采纳（超限部分主会话修剪），04/06/07/08/09/10 六篇主会话自写；零最终损失。
- 锚验证口径：basename 消歧+界内感知，全量抽验 130+ 锚 0 坏。
- 字数口径：不计空格总字符（与历轮一致）。

*2026-11-09 生成 · understand-anything 全链*
