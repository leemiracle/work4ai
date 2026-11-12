# 讲透 NVPLSamples（NVIDIA Performance Libraries 示例集）

[NVIDIA/NVPLSamples](https://github.com/NVIDIA/NVPLSamples) @78c53b0b（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/NVPLSamples`）：NVIDIA Performance Libraries 七库官方示例集——BLAS/LAPACK/FFT/Sparse/Rand/ScaLAPACK/Tensor，面向 aarch64 CPU-only（Grace/Vera/GB10/Graviton），零 CUDA 依赖，drop-in 替代标准 C/Fortran 数学 API。522 文件（C 179/C++ 89/Fortran 202/构建与文档 52）。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| 批分析 27/27 | ✅ 2026-11-09 | 仓内 `.understand-anything/`（intermediate 已被 finalize 清理，scan-result 保留） |
| merge | ✅ 零损耗 | 1141n/1874e（0 悬空丢弃、0 imports 恢复需求） |
| layers/tour | ✅ | 12 层（按库分组）+16 步 tour |
| finalize | ✅ validator 0 issues 0 warnings | 仓内 `knowledge-graph.json`（852K）+ fingerprints 522@78c53b0b |
| onboarding | ✅ 7999 字 8 节 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) |
| explain 6 篇 | ✅ 31334 字符 | [explain/](explain)（01-06，字数口径=不计空格字符） |
| 锚终验 | ✅ 157 锚 0 真坏 | 主会话独立消歧验证（basename+缩写归位+界内+内容级抽验） |

图谱统计：**1141 节点 / 1874 边 / 12 层 / 16 步 tour / fingerprints 522 文件**。

## 产物索引

- 图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/NVPLSamples/.understand-anything/knowledge-graph.json`
- 入门导览：`onboarding/ONBOARDING.md`（8 节：全景/目录地图/构建体系/四段式骨架/双接口模式/图谱导航/上手路径/坑与勘误）
- 深讲 6 篇（`explain/`）：
  - [01-blas-c-examples.md](explain/01-blas-c-examples.md)——BLAS C 示例体系（160 个 .c）与 example_helper.h 共享辅助
  - [02-blas-f77-fortran-interface.md](explain/02-blas-f77-fortran-interface.md)——F77 对偶体系（170 个 .f）、common_func.f、外部 .fi 接口机制
  - [03-lapack-dual-interface.md](explain/03-lapack-dual-interface.md)——LAPACKE vs NVPL_LAPACK 双接口、ILP64、厂商扩展
  - [04-fft-fftw-compat.md](explain/04-fft-fftw-compat.md)——FFTW API 兼容层、精度评估三件套、wisdom、OpenMP 规划
  - [05-scalapack-distributed.md](explain/05-scalapack-distributed.md)——BLACS+PxGESV 分布式 LU、.dat 数据、MPI 变体
  - [06-sparse-rand-tensor.md](explain/06-sparse-rand-tensor.md)——Sparse 三格式 / Rand 双引擎 / Tensor 描述符 API

## 源码级甄别与勘误（全部亲自核实，行号锚在对应文档内）

**上游真实笔误/缺陷（4 条）**
1. `nvpl_scalapack/f77/pzscaex.f:14-15`：声明 `CP16SZ` 却在 PARAMETER 写 `CPLXSZ=8`（pcscaex 复制残留）——CP16SZ 从未赋值即用于 :104/:114 的 LIPIJ 计算（未定义值）；同文件 NPCOL 被批量误改名 NPZOL（声明使用一致，疑自动替换误伤）。
2. `nvpl_fft/cxx/utils.h:1-2`：include guard 拼写 `NVPLFFT_EXAMPLE_UNTILS_H_`（UNTILS，上游笔误）。
3. `nvpl_lapack/cpp/utils.cpp:6-12`：`is_element_complex` 类型 trait 全仓零引用——死代码。
4. BLAS 示例复制文案瑕疵一族：`nvpl_blas/c/dsyr2.c`/`ssyr2.c` 与 `nvpl_blas/f77/ssyr2.f` 的 printf 头称 "packed Hermitian rank-2 update"（实为全存储非 Hermitian 的对称秩-2 更新）；`ccopy.f`/`zcopy.f` 的 format 文案误写 "SCOPY"；`ctrmm.f` 误写 "STRMM"；`nvpl_blas/c/idamax.c` 族注释 `// call cblas_isamax` 复制残留；`nvpl_fft/cxx/auxiliary_apis_example.cpp` 的 `inpout_data` 变量名笔误。

**认知坑（容易搞错的事实）**
- f77 示例的 `print_*/fill_*` 辅助例程真身在**仓内** `nvpl_blas/f77/common_func.f`（26 例程）与 `nvpl_lapack/f77/common_func.f`，而非 include 的 `.fi`——`.fi`/`fftw3.f03`/`fftw3.f` 均为 NVPL 安装包外部接口文件（仓内不存在）。
- `nvpl_rand/CMakeLists.txt:41`：`set(CUDAToolkit_FOUND FALSE CACHE BOOL "")` 硬编码关闭 CUDA 探测——两个 cuRAND 对照示例默认走 xor 哈希兜底分支（Philox 金常数 `0xc7042bf2`、SOBOL64 `0xa75c795246aa956c`）。
- BLAS f77 示例是**固定格式**（`program XXX_MAIN`），LAPACK f77 示例却是**自由格式**（`program usageexample`，CMake 传 -ffree-form）——同仓两种 Fortran 方言刻意分层。
- C 与 F77 示例集不完全对偶：f77 独有 10 例（cgemm3m/zgemm3m、crotg/zrotg/csrot/zdrot、i?amin 四件套），C 独有 dgemm_64；SAXPBY/ZAXPBY 为 NVPL 厂商扩展（标准 BLAS 无 axpby）。
- `nvpl_sparse/c/CMakeLists.txt:8`：示例链接裸名 `nvpl_sparse` 而非命名空间目标 `nvpl::sparse`（与根 README 推荐写法不一致）。
- ScaLAPACK 示例全部是 PxGESV 分布式 LU（GETRF+GETRS），无 Schur 分解调用（若见"舒尔"表述为讹传）；`pdscaexinfo.f` 存在 RETURN 之后的死代码。

## 工程要点（流水线钉版增量）

- tree-sitter 对 Fortran（f/f90）零提取：27 批中 Fortran 文件全部靠子代理逐文件手补 program/subroutine 节点。
- scanner importMap 248 边完备：零 import 目录（tensor/scalapack/lapack-f77）均为纯外部 include，属正确空结果而非盲区；唯一补扫 1 条（`nvpl_fft/cxx/common.h:9 → utils.h`）。
- f77 示例→common_func.f 的 calls 边经主会话统一补齐（b20-b24 +305 条）：三个批 worker 对辅助例程归属判断不一（.fi vs 仓内），终验阶段以 common_func.f 定义集 grep 甄别后统一回补。
