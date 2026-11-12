# llamafile/sgemm.cpp + tinyblas + iqk 精讲 — SIMD 矩阵乘三件套

## 角色定位

这是 llamafile 性能皇冠上的宝石。LLM 推理 95% 以上时间耗在矩阵乘，llamafile 用三件套在 CPU 上逼近理论上限：`sgemm.cpp`（238 行）是运行时分发器——启动时按 CPUID/auxv 探测微架构，把函数指针指向最优微内核；`tinyblas_cpu.h`（1338 行模板）+ ISA 包装实现 F32/F16/BF16/Q8_0 矩阵乘；`iqk_mul_mat.inc`（3130 行，来自 iqk_quantization 项目）处理 Q4_K/Q5_K/Q6_K 等 K-quant。三件套经 `GGML_USE_LLAMAFILE` 补丁钩进 ggml-cpu 算子层，失败回退原生。

## 内部结构

**sgemm.cpp 的分发核心**是文件级静态对象 `GemmFuncs funcs`——构造函数在 main 之前执行，按能力位逐级收窄选内核（x86：AVX→FMA→AVX2→AVX512F→AVXVNNI→Zen4 全套；ARM：auxv 探测 FPHP/ASIMDHP/ASIMDDP 则 arm82，否则 arm80）。函数指针表六组：sgemm（通用 matmul）、mixmul（MoE 专家张量乘）、iqk_mixmul（量化 matmul）、fa_vec_dot_f16 等 CPU FlashAttention 三助手。每个指针都有 `*_unsupported` 兜底返回 false，调用方回退上游；`LLAMAFILE_DISABLE_SGEMM=1` 全链关闭供 A/B 测试，`llamafile_sgemm_name()` 返回内核名供诊断。

**多 ISA 单二进制**：`tinyblas_cpu_sgemm_amd_zen4.cpp` 全文件仅 5 行——`#define llamafile_sgemm llamafile_sgemm_amd_zen4` + `#include "tinyblas_cpu_sgemm.inc"`。同一 .inc 被 7+ 个包装以不同符号名实例化，BUILD.mk 给每个 .o 配 `TARGET_ARCH += -Xx86_64-mtune=znver4 ...`（cosmocc 多目标编译）——BLIS/oneDNN 微内核分发的单文件复刻。

**tinyblas_cpu.h** 模板骨架：`C = Aᵀ·B` 列主序，CHUNK 8 分块、64/4096 字节对齐、按 VECTOR_REGISTERS（16/32）展开累加器；为 F32/F16/BF16 定义每 ISA 的向量重载与 ggml_type_trait 映射。文件头引 justine.lol/matmul 文章，舍入误差按「尺规函数」对数增长（分块求和的结构性好处）。

**iqk_mul_mat.inc** 核心思想在文件头注释：量化矩阵乘瓶颈在解包，QX×Q8_Y 时一次解包的 QX 块可复用于多个 Q8 列——GEMM tiling 省的是重复 load/unpack，实测 prompt processing 提速 150-400%。ARM 路径定义 block_q8_1_x4 交错打包布局；显式 IQK_NOINLINE/IQK_ALWAYS_INLINE 控制内联。入口抽象是 `mul_mat_t` 函数指针 + `DataInfo`（封装输出寻址与 MoE row_mapping）。

**tinyblas.cu**（1082 行）是 GPU 镜像：cuBLAS API 兼容的 CUDA/ROCm 模板内核，经典 tiling、Kahan 补偿乘加、warp shuffle 归约；编译成独立 DSO 供 cuda.c dlopen。

## 外部连接

上游钩子：ggml-cpu ops.cpp 补丁在 MUL_MAT 算子入口插 `#if GGML_USE_LLAMAFILE → llamafile_sgemm(...)`，返回 false 回退原生——错误处理协议就是布尔值。配套：compute.cpp/h（CPU 描述与线程参数）、sgemm.h（内核原型）。GPU 侧由 cuda.c/metal.c 加载 tinyblas DSO。测试：tests/sgemm/ 验证数值正确性。

## 数据流

```
ggml MUL_MAT (A[QX/F16..], B[Q8/F32])
  │ llamafile_sgemm(...)
  ▼
GemmFuncs 选定内核（如 llamafile_sgemm_amd_zen4）
  ├─ F16/BF16/F32: tinyblas 模板 ─ CHUNK8分块 ─ 向量fmadd累加 ─ 写C
  ├─ Q4_K/Q5_K/Q6_K: iqk_mixmul ─ 解包QX块复用 ─ 多列dot
  └─ 不支持组合 → false → ggml 原生路径
GPU: cuda.c dlopen tinyblas DSO → cuBLAS兼容符号 → 同一C=AᵀB语义
```
线程模型：params->ith/nth 由 ggml 线程池传入，微内核按行切分（compute.h 协调）。

## 设计决策

1. **构造函数分发而非惰性 if 链**：静态对象初始化一次定表，热路径零分支。
2. **布尔回退协议**：每个能力都有 unsupported 兜底，新内核不覆盖的组合自动落上游。
3. **.inc 单模板多实例**优于手写 N 份：算法改动只改一处，ISA 差异交给编译器 flag。
4. **iqk 独立引入而非改 tinyblas**：量化解包复用逻辑与通用 GEMM 结构差异大，两套各自最优。
5. **GPU 侧重写而非链 cuBLAS**：摆脱闭源依赖，单文件分发自洽。
6. **诊断先行**：内核名 + 一键全关，对照可答。

## 新人提示

- 验证改动用 tests/sgemm 数值测试，别靠肉眼比 token 输出。
- 看不懂 iqk_mul_mat.inc 先读文件头 60 行注释（tiling 思想全在那里），再从 DataInfo::store 反向追输出寻址。
- 加新 ISA 路径四处缺一即链接失败：包装 .cpp（5 行）+ BUILD.mk TARGET_ARCH 行 + sgemm.cpp 分发树 + sgemm.h 原型。
- F16C 位是 iqk 在旧 AMD 上的门槛，值得亲手推一遍路径。
