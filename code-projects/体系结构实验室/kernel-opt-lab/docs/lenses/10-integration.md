# 视角 10：应用集成工程师（Application Integration Engineer）

> **审查时间**：2026-06-30
> **审查者**：councillor delegate（gentle-golden-falcon），扮演 10+ 年经验、曾集成 PyTorch/oneDNN/llama.cpp/MNN 的应用集成工程师
> **方法**：read-only 审查 API 一致性、ABI、与主流框架的集成路径

---

我已完整审查项目。证据确凿：全仓 **0 个 `.h` 文件**，**所有 38 个 kernel 函数都是 `static`**，**每个 `.c` 都带 `main()`**，无 `include/`/`lib/`/`bindings/` 目录。下面是应用集成工程师视角的审查报告。

## 1. 视角定位（80 字）

10 年算子库集成老兵，把 GEMM/Attention 接入过 PyTorch / oneDNN / llama.cpp / MNN。我不看 GFLOPS——我看**这玩意儿能不能被框架调用、能不能进生产 SDK**。当前 lab 性能惊艳（98% 峰值），但**离"可集成"还有一道结构性鸿沟**。

## 2. 八大盲区（"独立 main()" 模式的结构性缺陷）

对全仓做了证据级核查，结论是**可调用性 = 0**：

| # | 盲区 | 证据 |
|---|---|---|
| **B1** | **零 header / 零导出符号** | `glob **/*.h` 返回空。所有 38 个 kernel（如 `gemm_f32_v5_mr8`）都是 `static`，跨编译单元**无法链接**。外部代码 `#include` 不到任何东西。 |
| **B2** | **kernel 与 driver 耦合死** | 每个 `.c` 顶部是 `#define M 1024` + `static` kernel，底部是 `int main(){...printf...}`。生产库要的是 `gemm(A,B,C,M,N,K)`，这里给的是"跑个 1024³ 打印 GFLOPS"。 |
| **B3** | **无 .so/.a 构建产物** | Makefile 只有 `$(BIN_DIR)/%` 可执行目标规则，**无 `libkernel_lab.so` / `.a` target**。`-fPIC` 没开，链接进框架会重定位失败。 |
| **B4** | **无 tensor abstraction** | 形参全是裸 `const float*`，无 dtype enum、无 strides、无 layout(NCHW/NHWC)、无 device handle。框架传入的 tensor 是 `strided + offset` 的，这里假设 `row-major contiguous + 零偏移`，**一接框架必崩**。 |
| **B5** | **无 zero-copy / 无生命周期** | 每次 `main()` 里 `posix_memalign` 后 `free`，没有 workspace pool、没有 buffer registry、没有"调用方管内存"的约定。PyTorch `torch::Tensor.data_ptr()` 要的是**借用不拥有**。 |
| **B6** | **无 error handling 规范** | 全部 `void` 返回，无 errno、无返回码、无 `kl_status_t`。NULL 指针 / 维度不合法 / OOM 全是 UB。 |
| **B7** | **无 ABI versioning / 无 async** | 无 `KL_API_VERSION` 宏、无 symbol version script、无 `kl_stream_t`。D3000 多核要 stream 调度，当前裸 `#pragma omp parallel` 与框架线程池**必然打架**。 |
| **B8** | **无任何框架 binding** | 无 `bindings/`、无 Python、无 pybind11、无 ONNX `OrtCustomOp`、无 llama.cpp `ggml_cgraph` 节点。README 待办里写了"嵌入 ONNX Runtime"，但**零代码**。 |

## 3. 改造建议（P0/P1/P2，具体到文件 + 签名）

### 🔴 P0 — 最小可集成骨架（1 周内）

**P0.1 新增 `include/kernel_lab.h` 统一头**（当前完全不存在）：
```c
// include/kernel_lab.h
#ifndef KERNEL_LAB_H
#define KERNEL_LAB_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef enum { KL_F32=0, KL_F16=1, KL_S8=2, KL_BF16=3 } kl_dtype_t;
typedef enum { KL_OK=0, KL_EINVAL=-1, KL_OOM=-2 } kl_status_t;
#define KL_API_VERSION 1

kl_status_t kl_gemm(kl_dtype_t dt, const void* A, const void* B,
    void* C, int M,int N,int K, int lda,int ldb,int ldc, int nthreads);

#ifdef __cplusplus
}
#endif
#endif
```

**P0.2 把 `static` kernel 拆成 `src/kernels/gemm_f32.c`（无 main），单独保留 `bench/gemm_f32_main.c`**。Makefile 加库目标：
```make
lib/libkernel_lab.so: $(wildcard src/kernels/*.c)
	$(CC) $(CFLAGS) -fPIC -shared $^ -o $@ -lm
```

### 🟡 P1 — 框架真实接入（2-4 周）

**P1.1 PyTorch Custom Op**（`bindings/python/torch_op.cpp`）：
```cpp
#include <torch/extension.h>
extern "C" kl_status_t kl_gemm(kl_dtype_t,const void*,const void*,
                               void*,int,int,int,int,int,int,int);
torch::Tensor ft_gemm(torch::Tensor A, torch::Tensor B){
    auto C = torch::empty({A.size(0),B.size(1)}, A.options());
    kl_gemm(KL_F32, A.data_ptr(), B.data_ptr(), C.data_ptr(),
            A.size(0),B.size(1),A.size(1),
            A.stride(0),B.stride(0),C.stride(0), 4);
    return C;
}
TORCH_LIBRARY(ftlab, m){ m.def("gemm", ft_gemm); }
```

**P1.2 ONNX Runtime Custom Op**（`bindings/onnx/kl_gemm.cc`）——满足 README 已承诺的"ONNX 端到端验证"。

**P1.3 llama.cpp GGML 节点**（`examples/llama_layer.c`）：替换默认 `GGML_OP_MUL_MAT`。

### 🟢 P2 — SDK 化（1-2 月）

- **P2.1 `kl_stream_t` async API**：消除裸 OpenMP 与 ATEN 线程池冲突
- **P2.2 `tools/gen_soname.sh` + version-script**：ABI 稳定后锁符号
- **P2.3 workspace pool**：`kl_workspace_alloc(Br,Bc)` 复用 Flash Attention 的 `S_blk`

## 4. 关键洞察

**算子实验室 ≠ 算子库**。实验室的 KPI 是"单算子 GFLOPS 上头条"；算子库的 KPI 是"框架集成零摩擦 + ABI 五年不破"。二者工程师思维方式对立：前者 `#define M 1024` 写死、`static` 藏私货、`printf` 报性能；后者 `void*+strides`、`extern "C"` 导出、返回 `status_t`。

当前项目卡在**"能跑"（98% 峰值）到"能用"（PyTorch 一行调用）的鸿沟**——这道沟不是性能问题，是**契约问题**：谁分配内存、谁管线程、出错怎么办、维度怎么传。`gemm_autotune.c` 已经长出了函数指针表 `gemm_fn candidates[]`，这是**全仓唯一接近"库思维"的种子**，P0.1 应该从这里长出去。

**最致命的一点**：38 个 `static` kernel 意味着**今天没有任何一个算子能被外部代码链接调用**。性能再高，对框架集成者而言就是"一堆截图"。

## 5. 新增实验 / 工具清单

| 路径 | 用途 | 验收标准 |
|---|---|---|
| `include/kernel_lab.h` | 统一 C ABI header（**当前缺失**）| `ctypes` 能 `dlsym("kl_gemm")` |
| `src/kernels/*.c` | 去 `static`、去 `main`、去 `#define M` 的纯内核 | 编出 `libkernel_lab.so` |
| `bindings/python/torch_op.cpp` | PyTorch custom op | `torch.ops.ftlab.gemm` 与 `torch.mm` 数值一致 |
| `bindings/python/pybind11.cpp` | 纯 Python 绑定 | `import kernel_lab` |
| `bindings/onnx/kl_gemm.cc` | ONNX Runtime custom op | ResNet conv 层替换后 top-1 持平 |
| `examples/llama_layer.c` | llama.cpp 单 Transformer block | FA + GEMM 跑通 forward |
| `examples/pytorch_resnet_block.py` | 替换 `nn.Conv2d` | 单 block 端到端加速 ≥3× |
| `tests/abistest.c` | ABI 回归：`dlopen`+符号存在性 | CI 中 `KL_API_VERSION` 断言 |
| `tools/gen_soname.sh` | 符号版本脚本 | `objdump -T` 无泄漏 |

**底线判定**：完成 P0 前，此项目对集成方的价值 = **一份性能白皮书**。完成 P1.1（PyTorch custom op）才是从"论文级"跨入"SDK 级"的分水岭。
