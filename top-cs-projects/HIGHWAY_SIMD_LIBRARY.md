# 🛣️ Google Highway SIMD 库完全综合：跨架构向量化的工程化答案

> **本文档定位**：[AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) 与 [ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md) 的**应用层续作** —— 三部曲的终章。
>
> | 文档 | 层次 | 回答的问题 |
> |------|------|----------|
> | [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md) | **原理层** | 为什么内存/分支/浮点硬件真相会击穿软件幻觉？ |
> | [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) | **手法层（x86）** | 在 Skylake/Zen4 上，怎么用 CPU dispatch、自取向量化、intrinsic 把代码榨干？ |
> | [ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md) | **手法层（非 x86）** | ARM SVE2 / RISC-V RVV 的 VLA、弱内存模型、Perceptron 分支预测器跟 x86 有什么本质差异？ |
> | **本文** | **工程层（跨架构）** | **同一份 C++ 源码，怎么在 7 大架构、27 种指令集上跑出原生性能，并在运行时自动选最优？** |
>
> **答案就是 [Google Highway](https://github.com/google/highway)**：被 JPEG XL / libjxl / Chromium / Firefox / gemma.cpp / ScaNN / TensorFlow / libvips / ghostty / Drake（MIT robotics）等上百个主流项目作为底层 SIMD 抽象。Agner Fog README 里明确写："If you only require x86 support, you may also use [VCL](https://github.com/vectorclass)"—— Highway 是 VCL 的**跨架构继任者**。
>
> **来源**：[google/highway](https://github.com/google/highway)（Apache-2.0 / BSD-3 双许可，1.0 版本承诺向后兼容，C++11，2026-08 仍在每周级更新）。本文所有 API/数据均对照 master 分支与 `g3doc/` 官方文档。
>
> **配套代码**：[`../cmu-cs-projects/topic2-systems/highway_simd_demo.py`](../cmu-cs-projects/topic2-systems/highway_simd_demo.py)（7 个可运行 demo：lane 概念 / AOS vs SOA / strip-mining 4 策略 / 静态 vs 动态分发 / Mask 谓词 / Highway API 速查 / SAXPY 真实案例）。

---

## 📚 第 0 部分：资源总览（2026-08 验证）

### 0.1 官方一手资源

| 资源 | 类型 | 价值 |
|------|------|------|
| ⭐⭐ **[README.md](https://github.com/google/highway/blob/master/README.md)** | 官方 | 5 分钟入门 + 27 target 全表 + 所有使用 Highway 的项目列表（仿 README 引用） |
| ⭐⭐ **[g3doc/quick_reference.md](https://github.com/google/highway/blob/master/g3doc/quick_reference.md)** | 官方 | **Highway API 的完整速查表**（所有 op 一页纸），最快入手 |
| ⭐⭐ **[g3doc/design_philosophy.md](https://github.com/google/highway/blob/master/g3doc/design_philosophy.md)** | 官方 | **为什么这样设计**：与 P0214R5/std::simd/Vc/UME::SIMD 的 9 点差异 |
| ⭐ **[g3doc/faq.md](https://github.com/google/highway/blob/master/g3doc/faq.md)** | 官方 | 35 个常见问题：boilerplate、`HWY_NAMESPACE`、include guard、sizeless 类型、`d` 参数、降频陷阱 |
| ⭐ **[g3doc/impl_details.md](https://github.com/google/highway/blob/master/g3doc/impl_details.md)** | 官方 | 内部实现细节（适合贡献者 / 深度使用者） |
| ⭐ **[g3doc/instruction_matrix.pdf](https://github.com/google/highway/blob/master/g3doc/instruction_matrix.pdf)** | 官方 | **每个 Highway op 在 7 架构上的指令数矩阵**（决定 op 的"性能可移植性"） |
| **[g3doc/highway_intro.pdf](https://github.com/google/highway/blob/master/g3doc/highway_intro.pdf)** | 官方 slides | 入门幻灯片 |
| **[在线文档](https://google.github.io/highway/en/master/)**（含[中文翻译](https://google.github.io/highway/zh/master/)）| Sphinx | 完整 HTML 文档 |
| **[hwy/examples/](https://github.com/google/highway/tree/master/hwy/examples)** | 源码 | skeleton.cc / benchmark.cc（拷贝即用的 boilerplate） |

### 0.2 入门视频与外部教程（README 推荐）

| 资源 | 作者 | 价值 |
|------|------|------|
| ⭐ **[SIMD programming with Highway](https://www.youtube.com/watch?v=R57biOOhnJM)** | YouTube | Highway 作者 Jan Wassenberg 亲讲 |
| ⭐ **[SIMD for C++ Developers](http://const.me/articles/simd/simd.pdf)** | const.me | C++ 工程师向的 SIMD 教程 PDF |
| ⭐ **[Algorithms for Modern Hardware](https://en.algorithmica.org/hpc/)** | Algorithmica | 在线书：SIMD 友好算法设计 + #pragma omp + profiling |
| **[Agner Fog - Optimizing C++](https://agner.org/optimize/optimizing_cpp.pdf)** | Agner Fog | Highway README 明确推荐（与本文档姊妹篇直接对接） |
| **[Improving performance with SIMD intrinsics in three use cases](https://stackoverflow.blog/2020/07/08/improving-performance-with-simd-intrinsics-in-three-use-use-cases/)** | StackOverflow Blog | 三个真实工程案例 |
| **[kfjahnke 的多 ISA 指南](https://github.com/kfjahnke/zimt/blob/main/examples/multi_isa_example/multi_simd_isa.md)** | @kfjahnke | 静态 vs 动态分发的可视化讲法 |

### 0.3 在线 Playground（无需装环境）

| Playground | 用途 |
|-----------|------|
| ⭐ **[Godbolt: 动态分发示例](https://gcc.godbolt.org/z/KM3ben7ET)** | 看一份 Highway 源码如何编译成多份 ISA 代码 |
| ⭐ **[Godbolt: 静态单 target 示例](https://gcc.godbolt.org/z/rGnjMevKG)** | 最简单的入门：单 ISA + `-m` flags |
| **[Godbolt + llvm-mca](https://gcc.godbolt.org/z/n-KcQ-)** | 看 Highway 代码的端口占用 / 吞吐预测 |

### 0.4 包管理器（开箱即用）

`alpinelinux` / `conan-io` / `conda-forge` / `freebsd` / `microsoft/vcpkg` / `MSYS2` / `openSUSE` / `NetBSD` / `DragonFlyBSD` —— 几乎所有主流包管理器都有 `highway`：
```bash
vcpkg install highway              # Windows / 跨平台
sudo apt install libhwy-dev        # Debian/Ubuntu
brew install highway               # macOS
```

---

## 🎯 第 1 部分：Highway 解决了什么（为什么不能只用 intrinsic / autovectorization）

> Agner Fog 在 Vol 1 §12 说："编译器自取向量化是免费的午餐，但只对**最简单**的循环有效"。
> Highway README 说："Highway 比 autovectorization **更可预测、对代码改动 / 编译器升级更鲁棒**"。

### 1.1 三种 SIMD 编程方式的对比

| 方式 | 写法 | 优点 | 致命缺点 |
|------|------|------|---------|
| **1. 自取向量化**（autovectorization） | 普通 `for` + `-O3 -ftree-vectorize` | 零工作量 | ❌ 编译器版本/小改动会失效；❌ 难预测；❌ 跨架构行为不一致 |
| **2. 平台 intrinsic**（`<immintrin.h>` / `<arm_neon.h>`）| `_mm256_add_ps()` / `vaddq_f32()` | 性能最优 | ❌ **一份代码只能跑一种架构**；❌ x86 代码无法在 ARM 跑；❌ 27 种 ISA 要写 27 份 |
| **3. Highway** | `hn::Add(v1, v2)` | ✅ **一份源码 7 架构 27 target**；✅ 运行时自动 dispatch；✅ 与 intrinsic 同性能（无抽象惩罚）| ⚠️ 学习曲线（boilerplate + namespace 规则） |

### 1.2 Highway vs 同类 SIMD 抽象库

| 库 | 范围 | 是否推荐 | Highway 的优势 |
|----|------|---------|--------------|
| ⭐ **Highway** | **7 架构** | ✅ 推荐 | 本文主角 |
| [VCL (Agner Fog Vector Class)](https://github.com/vectorclass/version2) | 仅 x86 | 仅限 x86-only 项目 | Highway README 明确说："If you only require x86, you may also use VCL" |
| [SIMDe](https://github.com/simd-everywhere/simde) | 跨架构**模拟**已有 intrinsic | 移植旧代码用 | SIMDe 是"把 x86/NEON intrinsic 翻译到其他架构"；Highway 是"提供一套更上层的新 API" |
| [std::experimental::simd (P0214R5)](https://goo.gl/zKW4SA) | 标准化提案 | ❌ **不推荐**（design_philosophy.md 第 9 点差异）| Highway README 设计哲学列了 P0214R5 的 9 个问题：不支持 sizeless vector、强制 wrapper class、`simd_cast` 用 stack、不能保证访问底层 intrinsic…… |
| [UME::SIMD](https://goo.gl/yPeVZx) | 跨架构 | ❌ 不推荐 | API 是所有平台能力的**并集**，spec 209 页、实现 500K LOC，难学难实现，**不保证性能可移植** |
| [Vc (P0214R5 基础)](https://github.com/VcDevel/Vc) | 跨架构 | ❌ 已过时 | Vc 不支持同一 binary 链接多个 ISA，建议 ifunc（编译器相关、ODR 风险）|

### 1.3 一个 30 行的直观例子（Highway README §Quick Start 浓缩）

> 计算 `dst[i] = src[i] * k + add[i]`（SAXPY，BLAS 一级基础）。

**自取向量化版本**（可能 SIMD，也可能不会，看编译器心情）：
```cpp
void saxpy_autovec(float k, const float* src, const float* add, float* dst, size_t n) {
    for (size_t i = 0; i < n; ++i) dst[i] = src[i] * k + add[i];
}
```

**x86 AVX2 intrinsic 版本**（仅 AVX2，换 ARM 全推倒重写）：
```cpp
#include <immintrin.h>
void saxpy_avx2(float k, const float* src, const float* add, float* dst, size_t n) {
    __m256 vk = _mm256_set1_ps(k);
    for (size_t i = 0; i < n; i += 8) {
        __m256 vs = _mm256_loadu_ps(src + i);
        __m256 va = _mm256_loadu_ps(add + i);
        _mm256_storeu_ps(dst + i, _mm256_fmadd_ps(vs, vk, va));
    }
}
```

**Highway 版本**（同一份源码，27 target 自动选最优，运行时 dispatch）：
```cpp
#include "hwy/highway.h"
HWY_BEFORE_NAMESPACE();
namespace hwy { namespace HWY_NAMESPACE { namespace gh = hwy::HWY_NAMESPACE;

void Saxpy(float k, const float* HWY_RESTRICT src, const float* HWY_RESTRICT add,
           float* HWY_RESTRICT dst, size_t n) {
    const ScalableTag<float> d;              // 自动选最宽向量类型
    const auto vk = Set(d, k);               // broadcast k 到所有 lane
    for (size_t i = 0; i < n; i += Lanes(d)) {
        auto vs = LoadU(d, src + i);         // unaligned load（Highway 风格）
        auto va = LoadU(d, add + i);
        Store(MulAdd(vs, vk, va), d, dst + i);  // FMA：vs * vk + va
    }
}

}}  // namespace
HWY_AFTER_NAMESPACE();

void CallSaxpy(float k, const float* src, const float* add, float* dst, size_t n) {
    HWY_DYNAMIC_DISPATCH(Saxpy)(k, src, add, dst, n);   // 运行时选最优 ISA
}
```

**三个反直觉点**：
1. **`ScalableTag<float>` 在 AVX2 上是 8 lane，AVX-512 上 16 lane，SVE 上 VLEN/32 lane，**同一份代码自动适配**。
2. **`HWY_DYNAMIC_DISPATCH` 在程序首次调用时做一次 CPU 检测**，之后查表，开销 < 1 ns。比 Agner Fog Vol 1 §12 手写的 CPU dispatch 更轻。
3. **`MulAdd` 在 SSE4/NEON（无 FMA）上会展开成两指令，在 AVX2/AVX-512/SVE 上是一条 FMA**，行为完全一致。

🧪 见 demo §7 `demo_saxpy_three_ways` —— 标量 / Highway 风格 / numpy 三种写法的对照。

---

## 🧱 第 2 部分：核心抽象——Tag / Vec / Mask 三件套

> Highway design_philosophy.md 第一段："We rely on overloaded functions... a dedicated tag type `Simd` for overloading, abbreviated to `D` for template arguments and `d` in lvalues."

Highway 的全部 API 围绕**三个核心类型**展开。理解这三件套，就理解了 Highway 90% 的设计。

### 2.1 Tag（`D` / `d`）—— "我要什么样的向量"

```cpp
ScalableTag<float> d;              // 默认：当前 CPU 最宽的 float 向量
CappedTag<float, 4> d4;            // 最多 4 lane（向上取整到 2 的幂）
FixedTag<float, 4> d_fixed;        // 恰好 4 lane（必须是 2 的幂）
```

**Tag 是零大小类型**（zero-sized），只用于重载解析，运行时**不占任何存储**（FAQ Q3.1）。

**为什么不用 class wrapper？** 因为 ARM SVE / RISC-V RVV 的 vector 是 **sizeless 类型**，不能被 class 包裹（FAQ Q4.3、Q4.4）。这是 Highway 与 P0214R5 最根本的分歧。

### 2.2 Vec（`V` / `v`）—— "向量数据"

```cpp
auto v1 = Zero(d);                 // 全 0
auto v2 = Set(d, 3.14f);           // broadcast
auto v3 = LoadU(d, ptr);           // unaligned load
auto v4 = Add(v1, v2);             // v1 + v2
auto v5 = MulAdd(v3, v2, v1);      // v3 * v2 + v1  (FMA)
Store(v5, d, ptr_out);             // aligned store
```

**类型推导**：用 `auto` 即可，或显式 `Vec<D>` / `VFromD<D>`（FAQ Q3.4）。

**禁止事项**（FAQ Q4.2-Q4.5）：
- ❌ 不能数组 `Vec v[4]`（sizeless 不能成数组）
- ❌ 不能 class 成员 `struct { Vec v; }`（同上）
- ❌ 不能 `static/thread_local Vec v`（运行时分发时会崩）
- ❌ 不能用 `operator+ / == / <`（用 `Add / Eq / Lt` 函数）

### 2.3 Mask（`M` / `m`）—— "谓词"

```cpp
auto m = Lt(v1, v2);               // v1 < v2 逐 lane 比较
auto v3 = IfThenElse(m, v1, v2);   // 三元：m ? v1 : v2
auto cnt = CountTrue(d, m);        // 数 true lane
auto all = AllTrue(d, m);          // 是否全 true
```

**为什么单独有 Mask 类型？** 因为 AVX-512 引入了专用 mask 寄存器（每 lane 1 bit），与 SSE/AVX2 的"全 1 / 全 0 向量 lane"完全不同。Highway 的 `Mask<D>` 在 AVX-512 上是原生 `__mmask16`，在其他平台零开销模拟（design_philosophy.md §Masks）。

### 2.4 三件套的完整调用模式

```cpp
const ScalableTag<float> d;        // ① 选 Tag
const auto k = Set(d, 2.0f);       // ② 用 Tag 制造 Vec
auto v = LoadU(d, ptr);            // ②
auto m = Gt(v, k);                 // ③ 比较 → Mask
auto r = IfThenElse(m, v, k);      // ③ 用 Mask 选
Store(r, d, out);                  // ② 写回
```

**所有 Highway op 都是 `namespace hwy::HWY_NAMESPACE` 下的自由函数**，参数决定重载。

🧪 见 demo §6 `demo_highway_api_cheatsheet` —— 用 numpy 模拟 Tag/Vec/Mask 三件套的完整行为。

---

## 🌍 第 3 部分：7 架构 × 27 target 矩阵（README §Current status）

> Highway 的"性能可移植性"靠这张表支撑。这是 2026 年 SIMD 生态最完整的一张图。

### 3.1 27 个 target（按架构分组）

| 架构 | Targets | 代表硬件 |
|------|---------|---------|
| **Any（保底）** | `EMU128`、`SCALAR` | 任何 CPU，128b 软件模拟 / 纯标量 fallback |
| **Armv7+** | `NEON_WITHOUT_AES`、`NEON`、`NEON_BF16`、`SVE`、`SVE2`、`SVE_256`、`SVE2_128` | Cortex-A / Apple Silicon / Graviton / A64FX |
| **IBM Z** | `Z14`、`Z15` | IBM 大型机 |
| **LoongArch** | `LSX`、`LASX` | 龙芯（中国国产）|
| **POWER** | `PPC8` (v2.07)、`PPC9` (v3.0)、`PPC10` (v3.1B，编译器 bug 待修)| IBM POWER / OpenPOWER |
| **RISC-V** | `RVV` (1.0) | SiFive / 平头哥 / 未来 HPC |
| **WebAssembly** | `WASM`、`WASM_EMU256`（`HWY_WANT_WASM2`，2× unroll）| 浏览器 / edge runtime |
| **x86** | `SSE2` / `SSSE3` / `SSE4` / `AVX2` / `AVX3` / `AVX3_DL` / `AVX3_ZEN4` / `AVX3_SPR` / `AVX10_2` | Intel / AMD 全系 |

**SSE4 自动包含 AES + CLMUL；AVX2 自动包含 BMI2 + F16 + FMA；AVX3 = AVX-512F/BW/CD/DQ/VL；AVX3_DL = AVX3 + BitAlg + CLMUL + GFNI + VAES + VBMI + VBMI2 + VNNI + VPOPCNT；AVX3_SPR 加 AVX-512FP16。**

### 3.2 这张表为什么是 SIMD 生态的事实标准

- **唯一同时覆盖 SVE2 和 RVV 的成熟库**——其他库要么只支持固定宽度（VCL/UME::SIMD），要么还在实验阶段（std::simd）
- **policy**：target 会保持支持，只要它能被 current Clang/GCC 编译 + QEMU 测试
- **27 target 全 CI 测**（README §Testing）：x86 native + ARM/RISC-V via QEMU

### 3.3 runtime dispatch 的核心机制

```cpp
// 你的源码只写一遍
HWY_EXPORT(Saxpy);                                  // 生成多份编译
HWY_ATTR void Saxpy(...) { /* SIMD 代码 */ }

// 调用时
HWY_DYNAMIC_DISPATCH(Saxpy)(args);                  // 运行时选最优
// 或静态（编译期决定，零开销但只一份 ISA）
HWY_STATIC_DISPATCH(Saxpy)(args);
```

底层通过 `foreach_target.h` 把同一个 `.cc` 文件**重复预处理 27 次**，每次定义不同的 `HWY_NAMESPACE`，链到一个 binary 里；运行时 CPUID 查表选最优（机制详见 §4）。

🧪 见 demo §4 `demo_static_vs_dynamic_dispatch` —— 用 Python 模拟"多份编译 + 函数指针表"的 dispatch 机制。

---

## 🧩 第 4 部分：静态分发 vs 动态分发（与 Agner Fog CPU dispatch 的衔接）

> Agner Fog Vol 1 §12 + asmlib 实现了手写的 CPU dispatch。Highway 把这件事工程化到了极致。

### 4.1 何时用静态 / 何时用动态？

| 模式 | API | 何时用 | 开销 |
|------|-----|-------|------|
| **静态分发** | `HWY_STATIC_DISPATCH` | ① 嵌入式：知道只跑一种 ISA；② 内核模块：不能多次编译；③ 极致 binary 大小 | **0**（编译期决定） |
| **动态分发** | `HWY_DYNAMIC_DISPATCH` | ① 通用库（JPEG XL、gemma.cpp、浏览器）；② 云上 heterogeneous fleet | 首次调用 ~50 ns（CPUID），之后查表 < 1 ns |

### 4.2 boilerplate（必读，新手 90% 卡这里）

> **FAQ Q5.1**：boilerplate = 支持运行时分发的"模板代码"。**强烈建议从 `hwy/examples/skeleton.cc` 拷贝起步**。

**完整的最小可运行模板**（ Highway README §Quick Start 提炼）：

```cpp
// my_simd.cc
#include "hwy/highway.h"
HWY_BEFORE_NAMESPACE();                  // ① pragma：让后续函数都带 SIMD attr

namespace myproj {                       // 项目 namespace
namespace HWY_NAMESPACE {                // ② Highway 自动改名（每 ISA 一份）

void MyFunc(const float* HWY_RESTRICT in, float* HWY_RESTRICT out, size_t n) {
    const hwy::HWY_NAMESPACE::ScalableTag<float> d;
    for (size_t i = 0; i < n; i += Lanes(d)) {
        Store(Add(LoadU(d, in + i), Set(d, 1.0f)), d, out + i);
    }
}

}  // namespace HWY_NAMESPACE
}  // namespace myproj
HWY_AFTER_NAMESPACE();                   // ③ 关闭 SIMD attr

// ④ 导出 + dispatch
HWY_EXPORT(MyFunc);                      // 让函数能被多次编译

void my_proj_entry(const float* in, float* out, size_t n) {
    HWY_DYNAMIC_DISPATCH(MyFunc)(in, out, n);
}
```

### 4.3 共享头文件的特殊 include guard（FAQ Q5.4）

当 SIMD 代码要在多个 `.cc` 间共享时，写成 `-inl.h` 头文件，但**不能用普通 include guard**，因为 `foreach_target.h` 要重复 include 同一文件。约定：

```cpp
// my_simd-inl.h
#if defined(MYPROJ_MY_SIMD_INL_H_) == defined(HWY_TARGET_TOGGLE)
#ifdef MYPROJ_MY_SIMD_INL_H_
#undef MYPROJ_MY_SIMD_INL_H_
#else
#define MYPROJ_MY_SIMD_INL_H_
#endif

#include "hwy/highway.h"
// ... 你的 SIMD 代码 ...

#endif  // per-target guard
```

这个奇葩的 `X == defined(HWY_TARGET_TOGGLE)` 模式是 Highway 在每次重新 include 前翻转 `HWY_TARGET_TOGGLE`，从而让 guard 重新打开。

### 4.4 与 Agner Fog 手写 dispatch 的对比

| 维度 | Agner Fog asmlib（手写）| Highway（库化） |
|------|------------------------|---------------|
| ISA 数 | 仅 x86（SSE2/AVX2/AVX-512）| **7 架构 27 target** |
| 检测代码 | 手写 CPUID + feature flag | `hwy::SupportedTargets()` 内建 |
| 升级 ISA | 重写所有函数指针表 | 加 target 定义即可 |
| 共享代码 | 汇编 `asmlib/*.asm` | C++ `*-inl.h` |
| 推荐场景 | 单 x86 项目极致优化 | 任何跨架构项目 |

> **结论**：Agner 教会你 dispatch 的原理（手写一次就懂），Highway 让你再也不用手写（用一次就回不去）。

---

## 🔁 第 5 部分：Strip-mining 4 种策略（README §Strip-mining loops，必背）

> 这是 SIMD 编程**最实用的工程模式**：循环的 `count` 不能整除 `Lanes(d)` 时怎么办？Highway README 给出 **4 种策略**，按推荐顺序：

### 5.1 策略对比表

| # | 策略 | 代码模式 | 限制 | 推荐度 |
|---|------|---------|------|-------|
| **1** | **Padding** | `for (i=0; i<count; i+=N) LoopBody(i)` | 输入必须 padded | ⭐⭐⭐ 默认 |
| **2** | **重做最后一段** | `for (i=0; i<count; i+=N) LoopBody(HWY_MIN(i, count-N))` | `count>=N` 且 idempotent | ⭐⭐ |
| **3** | **Transform 库** | `Transform1(d, x, n, y, lambda)` | C++14 lambda | ⭐⭐⭐ 推荐默认 |
| **4a** | **向量 + 标量尾巴** | 主循环 + `for (; i<count; ++i) scalar()` | 简单 | ⭐ |
| **4b** | **向量 + Mask 尾巴** | 主循环 + `BlendedStore(v, FirstN(d, r), d, p)` | `!HWY_MEM_OPS_MIGHT_FAULT` | ⭐⭐ |

### 5.2 四种策略代码片段

```cpp
// 设 d = ScalableTag<float>(), N = Lanes(d), count = 数组长度

// ① Padding（最简单，输入要保证 pad 到 N 倍数）
for (size_t i = 0; i < count; i += N) LoopBody(i);

// ② 重做最后一段（idempotent 操作如 max/min/xor，可重复算同样元素）
for (size_t i = 0; i < count; i += N) LoopBody(HWY_MIN(i, count - N));

// ③ Transform 库（最省心，自动处理尾巴）
Transform1(d, x, n, y, [](auto d, auto v, auto v1) HWY_ATTR {
    return MulAdd(Set(d, alpha), v, v1);    // SAXPY 一行搞定
});

// ④a 向量 + 标量尾巴
size_t i = 0;
for (; i + N <= count; i += N) LoopBody(i);
for (; i < count; ++i) ScalarBody(i);

// ④b 向量 + Mask 尾巴（推荐，只多一次循环但需保证不 fault）
size_t i = 0;
for (; i + N <= count; i += N) LoopBody(i);
if (i < count) {
    auto m = FirstN(d, count - i);
    auto v = MaskedLoad(m, d, ptr + i);
    BlendedStore(process(v), m, d, ptr_out + i);
}
```

> **README 原话**："This is a good default when it is infeasible to ensure vectors are padded, but is only safe `#if !HWY_MEM_OPS_MIGHT_FAULT_F`!"

🧪 见 demo §3 `demo_strip_mining_strategies` —— 4 种策略的 Python 模拟对比，可看出每种适合什么场景。

---

## ⚠️ 第 6 部分：常见陷阱（FAQ 精选 + impl_details）

### 6.1 sizeless 类型的 5 大限制（FAQ Q4.2-Q4.5）

SVE / RVV 的 vector 是 sizeless type，clang/GCC 限制：
- ❌ 不能数组 `Vec arr[4]`
- ❌ 不能 class 成员 `struct S { Vec v; };`
- ❌ 不能 `static / thread_local / 全局` Vec
- ❌ 不能用 `operator+` `<` `==`（重载不能用于 builtin type）
- ❌ 栈上数组 lane 可能爆栈（RVV LMUL=8 时单 vector 64 KiB）

**正确做法**：用 lane 类型数组 `float arr[N]` + `AllocateAligned<T>(Lanes(d))`。

### 6.2 namespace / HWY_ATTR 三选一（FAQ Q5.2）

调用 Highway op 的函数，必须满足下列之一：
```cpp
// 方式 A：完全放进 namespace（推荐）
namespace hwy { namespace HWY_NAMESPACE { void f() { LoadU(...); } }}

// 方式 B：alias
namespace hn = hwy::HWY_NAMESPACE;
void f() { hn::LoadU(...); }

// 方式 C：using declaration
using hwy::HWY_NAMESPACE::LoadU;
void f() { LoadU(...); }

// 任何方式下，函数本身必须有 SIMD attr：
// - 住进 HWY_BEFORE_NAMESPACE()/HWY_AFTER_NAMESPACE() 之间；或
// - 加 HWY_ATTR 前缀；lambda 也必须 HWY_ATTR
```

### 6.3 全局 Vec 初始化 = SIGILL 灾难（README §Quick Start）

> README 红字警告："Do not use namespace-scope nor static initializers for SIMD vectors because this can cause SIGILL when using runtime dispatch."

```cpp
// ❌ 错误：在静态初始化期 Set(d, 1.0f)，可能用了当前 CPU 不支持的 ISA
static const auto kBad = Set(ScalableTag<float>(), 1.0f);

// ✅ 正确：函数内 const，每次调用时按当前 dispatched ISA 构造
void f() {
    const ScalableTag<float> d;
    const auto k = Set(d, 1.0f);    // 局部，安全
}
```

### 6.4 AVX-512 降频陷阱（FAQ Q6.3，Agner Fog 也有讨论）

- 早期 Intel（Skylake-X）跑 AVX-512 会降频 3-4%（[Lemire 实测](https://lemire.me/blog/2018/08/15/the-dangers-of-avx-512-throttling-a-3-impact/)）
- 但**整体吞吐提升远大于降频**：JPEG XL 用 AVX-512 比 AVX2 快 1.4-1.6×
- **Icelake/Rocket Lake 之后不再降频**；AMD 全系不降频
- Highway 的 [vectorized Quicksort](https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md#study-of-avx-512-downclocking) 实测：80 KiB 以上输入用 AVX-512 划算

### 6.5 浮点跨平台不一致（FAQ Q2.2）

`MulAdd` 在 SSE4/NEON（无 FMA）展开成两指令，**多一次 rounding**；在 AVX2/AVX-512/SVE 是单 FMA，**单 rounding**。同一段代码跨架构结果可能差 ~10⁻⁵。

**对策**：测试时用 **relative + absolute tolerance**（FAQ 推荐）。`-ffast-math` 危险（破坏 NaN），Highway 不推荐。

### 6.6 Gather/Scatter 慢得吓人（FAQ Q6.5）

Gather/Scatter（按 index 散列读写）通常**每 cycle 只处理 1 lane**（vs 普通 Load/Store 一次能处理 2-3 个 vector）。算法层面优先改 SOA（§7.2）避开 gather。

### 6.7 unaligned 仍然要区分（FAQ Q6.1）

虽然 Haswell 之后 unaligned load 几乎不罚，但：
- 用两个 load port → dot product 类低算术强度算法会慢
- unaligned store 任何平台都更贵
- **Highway 推荐：能对齐就 `AllocateAligned<T>` + aligned `Store`**

🧪 见 demo §2 `demo_aos_vs_soa` —— AOS 与 SOA 的 cache 行为差异。

---

## 🤖 第 7 部分：AI 场景的真实应用（README §Examples 实例化）

> Highway 不是玩具——它驱动着 2025-2026 年最重要的 AI/多媒体基础设施。

### 7.1 ML / LLM 推理

| 项目 | 用 Highway 干什么 |
|------|----------------|
| ⭐ **[gemma.cpp](https://github.com/google/gemma.cpp)** | Google Gemma 模型的**纯 C++ CPU 推理引擎**，Highway 是核心依赖 |
| ⭐ **[TensorFlow](https://github.com/tensorflow/tensorflow)** | 部分 CPU kernel 用 Highway 重写（跨架构代替手写 intrinsic）|
| **[ScaNN](https://github.com/google-research/google-research/tree/master/scann)** | Google 向量检索库（最大内积搜索）核心 SIMD 抽象 |
| **[BPCells](https://github.com/bnprks/BPCells)** | 生信 RNA 分析，矩阵运算 |
| **[SimpleInfer](https://github.com/zpye/SimpleInfer)** | 端侧推理框架 |
| **[deepx](https://github.com/array2d/deepx)** | C++ 深度学习库 |

### 7.2 多媒体 / 压缩

| 项目 | 用 Highway 干什么 |
|------|----------------|
| ⭐ **[JPEG XL / libjxl](https://github.com/libjxl/libjjxl)** | **Highway 的发源地**（同一作者 Jan Wassenberg）。AVX-512 比 AVX2 快 1.4-1.6× |
| **[JPEGli](https://github.com/google/jpegli)** | Google 的高质量 JPEG 编码器 |
| **[libaom](https://aomedia.googlesource.com/aom/)** | AV1 视频编码器参考实现 |
| **[Grok JPEG 2000](https://github.com/GrokImageCompression/grok)** / **[OpenHTJ2K](https://github.com/osamu620/OpenHTJ2K)** | JPEG 2000 编解码 |
| **[libvips](https://github.com/libvips/libvips)** | 图像处理库 |
| **[ssimulacra2](https://github.com/cloudinary/ssimulacra2)** | 图像质量评估 |

### 7.3 浏览器 / runtime

| 项目 | 用 Highway 干什么 |
|------|----------------|
| **Chromium** + Vivaldi | 浏览器内核图像/视频解码 |
| **Firefox** + floorp/librewolf/Waterfox | 同上 |
| **[V8](https://v8.dev/)** / **[bun](https://bun.sh/)** / **[codon](https://github.com/exaloop/codon)** | JS / Python runtime 的 SIMD |
| **WASM runtime** | Highway 的 `WASM` target 让 C++ SIMD 代码跑在浏览器里 |

### 7.4 算法库（contrib/）

Highway 自带 `hwy/contrib/` 提供开箱即用的高阶 SIMD 算法：

| 子目录 | 功能 |
|--------|------|
| **[sort/](https://github.com/google/highway/tree/master/hwy/contrib/sort)** | ⭐ 向量化 Quicksort（[arXiv:2205.05982](https://arxiv.org/abs/2205.05982) 论文），比 `std::sort` 快 10×+ |
| **[algo/](https://github.com/google/highway/tree/master/hwy/contrib/algo)** | `Transform1/Transform2/Generate` —— strip-mining 自动化（§5 策略 3）|
| **[math/](https://github.com/google/highway/tree/master/hwy/contrib/math)** | 16 个数学函数（三角、对数、指数），跨架构 |
| **[dot/](https://github.com/google/highway/tree/master/hwy/contrib/dot)** | 向量内积（BLAS dot）|
| **[matvec/](https://github.com/google/highway/tree/master/hwy/contrib/matvec)** | 矩阵-向量乘（BLAS gemv）|
| **[random/](https://github.com/google/highway/tree/master/hwy/contrib/random)** | 向量化 PRNG |
| **[bit_pack/](https://github.com/google/highway/tree/master/hwy/contrib/bit_pack)** | 位压缩（每 bit 存）|
| **[thread_pool/](https://github.com/google/highway/tree/master/hwy/contrib/thread_pool)** | 线程池（配合 SIMD 多核）|
| **[unroller/](https://github.com/google/highway/tree/master/hwy/contrib/unroller)** | 循环展开器 |
| **[image/](https://github.com/google/highway/tree/master/hwy/contrib/image)** | 对齐行图像类 |

### 7.5 一个真实案例：gemma.cpp 怎么用 Highway

> [gemma.cpp](https://github.com/google/gemma.cpp) 是 Gemma 模型（Google 开源 LLM）的官方纯 C++ 推理引擎。它的核心 matmul kernel 就是 Highway 写的：

```cpp
// 简化自 gemma.cpp 的 MatMul 思路
namespace hwy { namespace HWY_NAMESPACE {
void MatMul(const float* A, const float* B, float* C, size_t M, size_t N, size_t K) {
    const ScalableTag<float> d;
    for (size_t i = 0; i < M; ++i) {
        for (size_t j = 0; j < N; j += Lanes(d)) {
            auto acc = Zero(d);
            for (size_t k = 0; k < K; ++k) {
                acc = MulAdd(Set(d, A[i*K + k]), LoadU(d, B + k*N + j), acc);
            }
            StoreU(acc, d, C + i*N + j);
        }
    }
}
}}  // namespace
```

**为什么不用 BLAS？** 因为 gemma.cpp 要：① 嵌入式部署（手机/edge）；② 跨 7 架构；③ 单二进制运行时分发。**Highway 是唯一同时满足三者的方案**。

---

## 🗺️ 第 8 部分：源码导航（怎么看 Highway 源码）

> Highway 源码 ~5 万行，组织清晰。理解这个目录结构后，看任何 Highway 程序都不再迷路。

### 8.1 顶层目录

```
google/highway/
├── hwy/                       ← 库主体
│   ├── highway.h              ← 唯一 #include 入口（聚合 ops/*）
│   ├── base.h                 ← 编译器/平台宏（HWY_RESTRICT 等，可独立使用）
│   ├── aligned_allocator.{h,cc} ← AllocateAligned<T>()，对齐内存
│   ├── targets.{h,cc}         ← 运行时 CPU 检测（SupportedTargets()）
│   ├── foreach_target.h       ← 多 target 编译的魔法（§3.3）
│   ├── detect_targets.h       ← target 名 → 宏的映射表
│   ├── detect_compiler_arch.h ← 编译器/架构检测
│   ├── cache_control.h        ← prefetch / clflush
│   ├── print.{h,cc}           ← 调试用：打印 Vec
│   ├── timer.{h,cc}           ← 高精度计时（profiling）
│   ├── profiler.{h,cc}        ← 函数级 profiler
│   ├── abort.{h,cc}           ← HWY_ABORT 宏
│   ├── nanobenchmark.{h,cc}   ← 纳秒级 microbenchmark（避免 perf 噪声）
│   ├── robust_statistics.h    ← median/MAD（microbenchmark 用）
│   ├── stats.{h,cc}           ← 性能统计（mean/prefix sum）
│   ├── auto_tune.h            ← 自动调参（strip-mine 大小等）
│   ├── bit_set.h              ← 位集合
│   ├── per_target.{h,cc}      ← 按 target 名查询能力
│   ├── x86_cpuid.h            ← x86 CPUID intrinsic 包装
│   ├── ops/                   ← ⭐⭐ 各架构实现（最核心）
│   ├── contrib/               ← ⭐ 高阶算法库（§7.4）
│   ├── examples/              ← skeleton.cc / benchmark.cc（拷贝起步）
│   └── tests/                 ← 每个 op 一份单元测试（54 个）
├── g3doc/                     ← 官方文档（本文 §0.1）
├── CMakeLists.txt             ← CMake 构建
├── BUILD                      ← Bazel 构建
├── meson.build                ← Meson 构建
└── hwy.gni / hwy_tests.bzl    ← GN / Bazel test 规则
```

### 8.2 `hwy/ops/` —— 每架构一对 `-inl.h`

> 这是 Highway 的"心脏"——每个 ISA 一份 op 实现，全部用 `inline` 函数。

| 文件 | 架构 | 关键 target |
|------|------|-----------|
| **`x86_128-inl.h`** | x86 SSE2/SSSE3/SSE4 | `SSE2`/`SSSE3`/`SSE4` |
| **`x86_256-inl.h`** | x86 AVX2 | `AVX2` |
| **`x86_512-inl.h`** | x86 AVX-512F/BW/CD/DQ/VL | `AVX3` |
| **`x86_avx3-inl.h`** | x86 AVX-512 高级（DL/SPR/ZEN4）| `AVX3_DL`/`AVX3_SPR`/`AVX3_ZEN4` |
| **`arm_neon-inl.h`** | ARM NEON | `NEON`/`NEON_BF16` |
| **`arm_sve-inl.h`** | ARM SVE/SVE2 | `SVE`/`SVE2`/`SVE_256`/`SVE2_128` |
| **`rvv-inl.h`** | RISC-V Vector | `RVV` |
| **`wasm_128-inl.h`** / **`wasm_256-inl.h`** | WebAssembly | `WASM`/`WASM_EMU256` |
| **`ppc_vsx-inl.h`** | POWER VSX | `PPC8`/`PPC9`/`PPC10` |
| **`loongarch_lsx-inl.h`** / **`_lasx-inl.h`** | 龙芯 | `LSX`/`LASX` |
| **`scalar-inl.h`** | 纯标量 | `SCALAR` |
| **`emu128-inl.h`** | 128b 软件模拟 | `EMU128` |
| **`generic_ops-inl.h`** | 通用模板（被各架构 `#include`）| - |
| **`set_macros-inl.h`** | 设置 `#pragma target` | - |
| **`inside-inl.h`** / **`shared-inl.h`** | 内部辅助 | - |

### 8.3 看一份典型 op 实现（`Add` 在 x86_256）

```cpp
// hwy/ops/x86_256-inl.h（简化）
template <class T>
HWY_API Vec256<T> Add(Vec256<T> a, Vec256<T> b) {
    return Vec256<T>(_mm256_add_ps(b.raw, a.raw));  // 直接调 intrinsic
}
```

**注意**：每个 op 在每个架构都是一份**独立 inline 函数**。这就是"performance portability without abstraction penalty"的实现机制——零虚函数、零类型擦除、所有信息编译期已知。

### 8.4 `hwy/tests/` —— 54 个 op 测试

每个 op 一份 `_test.cc`，会在**所有支持 target** 上跑一遍。这是 Highway 1.0 兼容承诺的工程基础。

| 测试文件 | op |
|---------|-----|
| `arithmetic_test.cc` | Add/Sub/Mul/Div |
| `fma_test.cc` | MulAdd/MulSub/NegMulAdd |
| `mask_test.cc` | IfThenElse/IfThenZeroElse |
| `memory_test.cc` | Load/LoadU/Store/BlendedStore |
| `reduction_test.cc` | SumOfLanes/MinOfLanes |
| `compress_test.cc` | CompressStore（AVX-512 + NEON 模拟）|
| `swizzle_test.cc` | Shuffle/TableLookupBytes |
| ...共 54 个 | |

### 8.5 学习路径（建议顺序）

1. **跑 examples**：`hwy/examples/skeleton.cc`（最小可运行）
2. **看 quick_reference**：1 小时过完所有 op 名字
3. **挑一个 op 看实现**：如 `Add` 在 `x86_256-inl.h` + `arm_neon-inl.h` + `rvv-inl.h` 三处对比
4. **看 contrib/algo/transform-inl.h**：学 Highway 风格的"高阶抽象"
5. **看 contrib/sort/**：看 SIMD 友好算法（[arXiv:2205.05982](https://arxiv.org/abs/2205.05982) 论文配套代码）
6. **看 nanobenchmark.cc + stats.cc**：学 SIMD 程序怎么正确测速

---

## 🚀 第 9 部分：5 分钟上手 + Godbolt

### 9.1 最小 CMakeLists.txt（拷贝即用）

```cmake
cmake_minimum_required(VERSION 3.10)
project(my_simd_proj CXX)
set(CMAKE_CXX_STANDARD 11)            # Highway 只要 C++11

# 方式 A：用系统装的 Highway
find_package(HWY 1.0 REQUIRED)
add_executable(my_app main.cc)
target_link_libraries(my_app PRIVATE hwy)

# 方式 B：用 submodule（推荐，跨机器一致）
# add_subdirectory(third_party/highway)
# target_link_libraries(my_app PRIVATE hwy)
```

### 9.2 最小 main.cc（拷贝即用）

```cpp
#include <cstdio>
#include <cstddef>
#include "hwy/highway.h"

HWY_BEFORE_NAMESPACE();
namespace myproj { namespace HWY_NAMESPACE {

void AddOne(const float* HWY_RESTRICT in, float* HWY_RESTRICT out, size_t n) {
    const hwy::HWY_NAMESPACE::ScalableTag<float> d;
    const auto one = Set(d, 1.0f);
    for (size_t i = 0; i < n; i += Lanes(d)) {
        Store(Add(LoadU(d, in + i), one), d, out + i);
    }
}

}}  // namespace
HWY_AFTER_NAMESPACE();
HWY_EXPORT(AddOne);

int main() {
    float in[1024], out[1024];
    for (int i = 0; i < 1024; ++i) in[i] = float(i);
    HWY_DYNAMIC_DISPATCH(AddOne)(in, out, 1024);
    std::printf("out[0]=%.1f out[1023]=%.1f\n", out[0], out[1023]);
    // 期望：out[0]=1.0, out[1023]=1024.0
}
```

### 9.3 Godbolt 速查（不用装环境）

| 链接 | 演示 |
|------|------|
| ⭐ **[单 ISA 静态分发](https://gcc.godbolt.org/z/rGnjMevKG)** | 最简单：`-mavx2` 一份 ISA |
| ⭐ **[动态分发](https://gcc.godbolt.org/z/KM3ben7ET)** | 看 `HWY_DYNAMIC_DISPATCH` 怎么编译出多份代码 |
| **[llvm-mca 分析](https://gcc.godbolt.org/z/n-KcQ-)** | 看你的 Highway 代码占哪些端口 |

### 9.4 编译 flag 速查

| 平台 | 推荐 flag |
|------|---------|
| **Clang / GCC** | `-O2` 足够（不要 `-O0`，SIMD 不 inline 会慢 10-100×）|
| **MSVC** | `/Gv`（vectorcall）+ `/arch:AVX2`（如要用 AVX2 target）|
| **ARM 32-bit** | `-DHWY_CMAKE_ARM7:BOOL=ON`（编译器限制，issue #834）|
| **强制单 ISA** | `-DHWY_COMPILE_ONLY_STATIC=ON` |

---

## 🎓 第 10 部分：与已有三旗舰的衔接（学习路径建议）

> 本文档是 [AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) + [ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md) 的应用层终章。三份一起读才完整。

### 10.1 四份文档的依赖关系

```
            CSAPP_HARDWARE_TRUTHS.md（原理层）
                        │
                        ▼
            AGNER_FOG_OPTIMIZATION.md（手法层 x86）
                        │
                        ▼
            ARM_AND_RISCV_OPTIMIZATION.md（手法层非 x86）
                        │
                        ▼
            HIGHWAY_SIMD_LIBRARY.md（工程层，本文）  ← 跨架构应用
```

### 10.2 不同目标的阅读路径

| 你的目标 | 推荐顺序 |
|---------|---------|
| **写跨架构 SIMD 库**（gemma.cpp / 推理引擎）| 直接从本文开始 → 必要时回查 Agner 第 5 卷 / ARM SOG |
| **优化某个 x86 热点** | CSAPP → Agner → 本文（用 Highway 重写代替 intrinsic）|
| **优化 ARM/RISC-V** | CSAPP → ARM_AND_RISCV → 本文（用 Highway 抹平差异）|
| **学术研究 SIMD 算法** | 本文 §5（strip-mining）+ §7.4（contrib/）+ arXiv:2205.05982（向量 Quicksort）|
| **学习编译器/ ISA** | 本文 §8（源码导航）+ Agner Vol 2/3 + ARM ARM + RISC-V spec |

### 10.3 本文关键反直觉发现回顾

1. **Highway 不是"另一个 VCL"**：它解决了 P0214R5/std::simd 都没解决的 sizeless vector 问题（§2.1）
2. **同一份源码 7 架构 27 target**：靠 `foreach_target.h` 重复预处理 + namespace 改名实现（§3.3）
3. **静态分发开销 0，动态分发开销 < 1 ns**（§4）
4. **AVX-512 降频是历史包袱**：Icelake 之后 / AMD 全系不降；JPEG XL 用 AVX-512 比 AVX2 快 1.4-1.6×（§6.4）
5. **Highway 是 JPEG XL / libjxl / gemma.cpp / ScaNN / Chromium / Firefox 的共同底座**（§7）
6. **gemma.cpp 不用 BLAS 用 Highway**：因为要嵌入式部署 + 跨 7 架构 + 单二进制（§7.5）

---

## 📌 附：本文的 AI 场景定位（讲透系列枢纽）

本文同时是以下"讲透"系列的**应用层证据**：

| 关联主题 | 本文为它提供了什么 |
|---------|-----------------|
| [`../讲透GPU与系统级/`](../讲透GPU与系统级/) | CPU SIMD 是 GPU 之外另一条并行路；高算术强度（§7.1）+ 单 binary 跨 fleet 是 CPU 不可替代的场景 |
| [`../讲透PyTorch/`](../讲透PyTorch/) | PyTorch CPU kernel 部分用类似抽象；gemma.cpp 是"不用 PyTorch 也能跑 LLM"的证据 |
| [`../讲透NLP/`](../讲透NLP/) | gemma.cpp / ScaNN 是 NLP 推理 + 检索的 SIMD 工程化 |
| [`../端侧AI压缩技术/`](../端侧AI压缩技术/) | 跨架构单 binary 是端侧 AI 部署的关键技术（vs 动态下载架构专用二进制）|
| [`../cmu-cs-projects/topic2-systems/`](../cmu-cs-projects/topic2-systems/) | CSAPP → Agner → Highway 是 CMU 15-213 性能优化路线的应用层闭环 |

---

## ✍️ 下一步 / 练习

**📌 推荐学习路径**：
1. 跑通 [`highway_simd_demo.py`](../cmu-cs-projects/topic2-systems/highway_simd_demo.py) 的 7 个 demo（纯 Python，10 分钟）
2. 打开 [Godbolt 静态分发示例](https://gcc.godbolt.org/z/rGnjMevKG)，改 `-mavx2` → `-mavx512f`，看汇编变化
3. clone Highway，跑 `hwy/examples/skeleton.cc`（5 分钟编译运行）
4. 读 `g3doc/quick_reference.md`（1 小时过完所有 op）
5. 挑一个 op（如 `MulAdd`），看它在 `x86_256-inl.h` + `arm_neon-inl.h` + `rvv-inl.h` 三处的实现差异
6. 读 [`hwy/contrib/sort/` 的论文](https://arxiv.org/abs/2205.05982)（向量 Quicksort）

**✍️ 实战练习**（难度递增）：
- ⭐ **L1**：用 Highway 写一个 `mul_scalar(float* x, float k, size_t n)` —— 标量乘法
- ⭐⭐ **L2**：用 `Transform1` 写 SAXPY（一行 lambda，§5 策略 3）
- ⭐⭐⭐ **L3**：用 Highway 写向量内积（dot product），用 `SumOfLanes` 做 reduction
- ⭐⭐⭐⭐ **L4**：用 `MaskedLoad + BlendedStore` 处理 `n % Lanes(d) != 0` 的尾巴（§5 策略 4b）
- ⭐⭐⭐⭐⭐ **L5**：用 Highway 写一个 `matmul(M, N, K)`，对比 `gemma.cpp` 的实现
- ⭐⭐⭐⭐⭐ **L6**：把 Agner Fog 的[ Newton-Raphson 倒数近似](../cmu-cs-projects/topic2-systems/agner_optimization_demo.py §7)用 Highway 跨架构重写（5-10 行核心代码）

**📌 进阶**：
- 读 [`hwy/contrib/sort/README.md`](https://github.com/google/highway/blob/master/hwy/contrib/sort/README.md) —— AVX-512 降频实测分析
- 读 [设计哲学原文](https://github.com/google/highway/blob/master/g3doc/design_philosophy.md) —— 9 点与 std::simd 的差异
- 读 [gemma.cpp 源码](https://github.com/google/gemma.cpp) —— 真实 LLM 推理引擎怎么用 Highway

---

**作者**：AI Mentor (ai-mentor) + 学生
**完成日期**：2026-08-12
**版本**：v1.0（对照 google/highway master 分支）
**姊妹文档**：[AGNER_FOG_OPTIMIZATION.md](AGNER_FOG_OPTIMIZATION.md) · [ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md) · [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md)
**配套代码**：[`../cmu-cs-projects/topic2-systems/highway_simd_demo.py`](../cmu-cs-projects/topic2-systems/highway_simd_demo.py)（7 个可运行 demo）
