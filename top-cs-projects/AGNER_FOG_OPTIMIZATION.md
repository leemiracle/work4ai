# ⚙️ Agner Fog 优化手册 · 完全综合：从硬件真相到指令级优化

> **本文档定位**：[CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md) 的**指令级续作**。
>
> CSAPP 告诉你"为什么 row-major 比 col-major 快 50×"（原理层）。
> Agner Fog 告诉你"在 Skylake-Zen4 上，`idiv` 延迟 20-30 cycle，怎么用乘法倒近似替代它，怎么让 GCC 自动向量化，怎么用 CPU dispatch 在运行时选最优实现"（手法层）。
>
> **来源**：[agner.org/optimize/](https://www.agner.org/optimize/)（Agner Fog 个人维护 25+ 年，x86 微架构优化的全球公认圣经，5 卷手册 + 4 个配套工具，**2026 年仍在每周级更新**）。
>
> **配套代码**：[`./cmu-cs-projects/topic2-systems/agner_optimization_demo.py`](./cmu-cs-projects/topic2-systems/agner_optimization_demo.py)（7 个可运行优化模式 demo）。
>
> ⚠️ **前置条件**：Agner 手册明确说"not for beginners"。本文假设你已读完 CSAPP_HARDWARE_TRUTHS.md 的 8 个硬件真相。

---

## 📚 第 0 部分：资源总览（2026-08 最新）

### 5 卷手册（全部免费 PDF）

| # | 手册 | 最新版本 | 大小 | 核心价值 |
|---|------|---------|------|---------|
| **Vol 1** | [Optimizing software in C++](https://www.agner.org/optimize/optimizing_cpp.pdf) | 2026-07-12 | 1.28 MB | C++ 工程师必读：编译器选择、容器效率、向量化、CPU dispatch |
| **Vol 2** | [Optimizing subroutines in assembly language](https://www.agner.org/optimize/optimizing_assembly.pdf) | 2025-12-18 | 1.09 MB | 汇编/intrinsic 工程师：跨编译器链接、循环、向量化编程 |
| **Vol 3** | [The microarchitecture of Intel, AMD and VIA CPUs](https://www.agner.org/optimize/microarchitecture.pdf) | 2026-05-23 | 1.87 MB | ⭐ **最权威一卷**：CPU 内部流水线/ROB/RS/端口/分支预测器，**厂商手册里查不到** |
| **Vol 4** | [Instruction tables: latencies, throughputs, μops](https://www.agner.org/optimize/instruction_tables.pdf) | 2025-09-20 | 2.25 MB | 每条指令的延迟/吞吐/μop 分解/执行端口，**几万条数据**，[ODS 表格版](https://www.agner.org/optimize/instruction_tables.ods) |
| **Vol 5** | [Calling conventions for different C++ compilers and OSes](https://www.agner.org/optimize/calling_conventions.pdf) | 2023-07-01 | 1.08 MB | 跨平台 ABI：参数传递、寄存器分类、name mangling、对齐 |

### 4 个配套工具（开源）

| 工具 | 最新版本 | 用途 |
|------|---------|------|
| **[VCL (Vector Class Library)](https://github.com/vectorclass/version2)** | 持续更新 | C++ 向量类库，统一封装 SSE/AVX/AVX2/AVX-512/FMA，**比手写 intrinsic 安全 10×** |
| **[testp](https://www.agner.org/optimize/testp.zip)** | 2025-08-28 | 测量**小段代码**的时钟周期和 PMU 计数器（cache miss、branch mispredict、resource stall）。`perf` 测整程序，testp 测函数级 |
| **[objconv](https://www.agner.org/optimize/objconv.zip)** | 2026-05-14 | 跨平台目标文件转换器 + 反汇编器，支持 AVX-512/FMA/XOP，**比 objdump 强** |
| **[asmlib](https://www.agner.org/optimize/asmlib.zip)** | 2023-05-03 | 优化的 asm 函数库：memcpy/strlen/strpbrk/整数除法等，**比 glibc 快** |

### 最新论文

| 论文 | 日期 | 价值 |
|------|------|------|
| **[Floating point exception tracking and NaN propagation](https://www.agner.org/optimize/nan_propagation.pdf)** | 2026-08-08 | 解决 OoO + SIMD 下的浮点异常追踪难题，NaN 传播方案 |

### 相关外部资源（Agner 推荐）

- **[uops.info](https://uops.info/)** —— 比 Agner Vol 4 更新更频繁的指令延迟数据库（机械测量）
- **[instlatx64.atw.hu](http://instlatx64.atw.hu/)** —— 社区测量的指令延迟
- **[Godbolt Compiler Explorer](https://godbolt.org/)** —— 在线看不同编译器怎么处理你的代码（支持 VCL）
- **[likwid](https://github.com/RRZE-HPC/likwid)** —— Linux 性能测量工具，比 `perf` 易用
- **[Bit Twiddling Hacks](https://graphics.stanford.edu/~seander/bithacks.html)** —— 位运算技巧集

---

## 🎯 第 1 部分：Agner 的方法论 —— 先 Profile，再谈优化

> "Premature optimization is the root of all evil." — Knuth
>
> "But premature *pessimization* is even worse." — Agner（隐含）

Agner 在 Vol 1 §1 反复强调：**90% 的"优化"是无效的，因为开发者优化错了地方**。正确流程是：

### 1.1 性能剖析 4 步法（Agner Vol 1 §1.5）

```
1. 确定目标        → 用户感知的延迟？吞吐？能耗？
2. 全程序 profile  → 用 perf / VTune / likwid 找最热的 20% 函数
3. 热点深入        → 用 testp / pmu-tools 分析热点的微架构瓶颈
4. 假设-修改-验证  → 改一处、测一处、不要批量改
```

### 1.2 性能瓶颈的 4 大类（Agner Vol 1 §1.7，必背）

Agner 把所有性能问题归结为 **4 类瓶颈**。看到热点代码，先判断它属于哪一类：

| 瓶颈类型 | 典型症状（perf 输出） | 根因 | 解药章节 |
|---------|-------------------|------|---------|
| **1️⃣ 内存访问** | `cache-misses` 高、`LLC-load-misses` 高 | Cache miss、TLB miss、跨 page、未对齐 | 第 2 部分 §1-3 |
| **2️⃣ 分支预测** | `branch-misses` 高 | if/else 难预测、switch 大跳表 | 第 2 部分 §4 |
| **3️⃣ 指令级并行（ILP）** | IPC < 1.0、`uops-executed/uops-issued` 低 | 数据依赖链过长 | 第 2 部分 §5 |
| **4️⃣ μop 吞吐（执行端口）** | `resource_stalls.sb` 高、port X 利用率 100% | 某类指令集中在少数 port | 第 3 部分 + Vol 4 查表 |

### 1.3 一个诊断口诀

```
IPC > 3.0  → 不是 CPU 瓶颈（看内存/IO）
IPC < 1.0  → ILP 受限 → 找最长依赖链
cache-miss-rate > 10% → 内存瓶颈，先改数据布局
branch-mispred-rate > 5% → 分支瓶颈，找难预测 if
```

🧪 见 [`agner_optimization_demo.py`](./cmu-cs-projects/topic2-systems/agner_optimization_demo.py) §1 `diagnose_bottleneck` —— 给定一组 PMU 计数器，自动判定属于哪类瓶颈。

---

## ⚙️ 第 2 部分：10 大通用优化原则（跨 CPU 家族）

> 这些原则在 P6（1995）到 Zen4/Skylake（2024）都成立。是 Agner 25 年测量沉淀的**稳定知识**。

### 原则 1：数据布局优先于算法（CSAPP 真相 1 的延伸）

**问题**：算法复杂度 `O(n)` 的代码，因 cache miss 实测可能比 `O(n²)` 还慢。

**Agner 的解药**（Vol 1 §7 + Vol 2 §6）：
1. **结构数组 → 数组结构（SoA）**：
   ```cpp
   // ❌ AoS：每个 Particle 一个 cache line 跨字段
   struct Particle { float x, y, z, vx, vy, vz; };
   std::vector<Particle> particles;
   // ✅ SoA：只遍历 x 时，cache 100% 利用
   struct Particles { std::vector<float> x, y, z, vx, vy, vz; };
   ```
2. **热字段分离（hot/cold splitting）**：频繁访问的字段放前面，罕见的放另一个结构。
3. **对齐**：`alignas(64)` 让热结构独占 cache line（同时治伪共享）。

### 原则 2：分支 → 无分支（CSAPP 真相 4 的延伸）

**问题**：现代 CPU 流水线 14-19 级，分支预测失败成本 15-20 cycle。**随 CPU 进步，预测失败成本不降反升**。

**Agner 的解药**（Vol 1 §8 + Vol 2 §9）：
1. **位运算消除分支**：
   ```cpp
   // ❌ 难预测的 if
   if (x < 0) x = -x;  // abs
   // ✅ 位运算（无分支）
   int mask = x >> 31;
   x = (x ^ mask) - mask;
   ```
2. **条件传送 `cmov`**：编译器在 `-O3` 自动生成；手写用 `std::min/std::max`（编译器能识别）。
3. **数据有序化**：如果分支判断依赖的数据可排序，先排再循环（参见 CSAPP 真相 4）。
4. **`__builtin_expect` / C++20 `[[likely]]` / `[[unlikely]]`**：告诉编译器哪条路常走。

⚠️ **反例**：分支预测准确率 > 95% 时，**不要**强行去分支——`cmov` 引入数据依赖，反而更慢。

### 原则 3：打破数据依赖链（ILP 是免费午餐）

**问题**：CPU 有多个执行端口（Skylake 8 个），但若指令相互依赖，只能串行。

**经典案例**（Agner Vol 1 §9.6）—— 数组求和：
```cpp
// ❌ 单 accumulator —— 串行依赖，IPC < 1
float sum = 0;
for (float x : arr) sum += x;  // 每条 add 等上一条

// ✅ 多 accumulator —— 打破依赖，IPC ≈ 4
float s0=0, s1=0, s2=0, s3=0;
for (size_t i = 0; i+3 < n; i += 4) {
    s0 += arr[i+0];
    s1 += arr[i+1];
    s2 += arr[i+2];
    s3 += arr[i+3];
}
float sum = (s0+s1) + (s2+s3);
```

编译器**通常不会**自动多 accumulator（涉及浮点结合律不可假定的语义），需要手动 + `-ffast-math` 或 `-fassociative-math`。

🧪 见 demo §3 `demo_ilp_accumulator` —— 模拟单/多 accumulator 的 cycle 数对比。

### 原则 4：内存对齐（CSAPP 真相 5 的延伸）

**问题**：未对齐访问在某些 CPU（特别 ARM）触发 fault；在 x86 触发跨 cache line 慢访问。

**Agner 的解药**（Vol 2 §7）：
```cpp
// C++17
struct alignas(64) HotCounter { std::atomic<long> v{0}; };  // 独占 cache line
alignas(16) float vec[4];  // 16 字节对齐（SSE）
alignas(32) float vec8[8]; // 32 字节对齐（AVX）
```

`malloc` 默认只 16 字节对齐；要 32/64 字节用 `aligned_alloc`（C11）或 `posix_memalign`。

### 原则 5：向量化（SIMD）—— 免费的 4-16×

**问题**：标量循环每个 cycle 算 1 个 float；AVX2 每个 cycle 算 8 个；AVX-512 算 16 个。

**Agner 的解药**（Vol 1 §10 + Vol 2 §11）：
1. **让编译器自动向量化**：
   ```bash
   gcc -O3 -ftree-vectorize -fopt-info-vec-optimized  # 看哪些循环被向量化
   gcc -O3 -march=native   # 启用本机支持的所有 SIMD 指令
   ```
2. **写"向量化友好"的代码**：
   - 无分支（用 `?:` 而非 `if`，前者更易向量化）
   - 连续内存访问（不要 stride）
   - 循环边界已知且可展开
3. **用 VCL 而非手写 intrinsic**：
   ```cpp
   #include <vectorclass.h>
   Vec8f a(...), b(...);
   Vec8f c = a + b;  // 自动选 AVX2/AVX-512
   ```
4. **关键热路径手写 intrinsic**：用 `<immintrin.h>` 的 `_mm256_add_ps` 等。

🧪 见 demo §4 `demo_simd_throughput` —— 模拟标量/SSE/AVX/AVX-512 的吞吐差异。

### 原则 6：避免 μop 解码瓶颈

**问题**：复杂指令（string ops、`pusha`、`imul` 多 μop）堵塞解码单元。

**Agner 的解药**（Vol 3 §解码器）：
1. 避免在热循环用 `rep movsb`（虽然现代 CPU 优化过，但仍非最快）。
2. 用 `memcpy` 替代循环字节拷贝（`memcpy` 调用 asmlib/VCL 版本）。
3. **指令缓存（I-cache）友好**：函数别太大；热点循环塞进 16 KB L1 I-cache。

### 原则 7：循环展开的收益与代价

**收益**：减少 loop overhead（cmp/jcc）、增加 ILP。
**代价**：代码膨胀 → I-cache 压力、register pressure。

**Agner 的黄金法则**（Vol 2 §12）：
- 展开因子 = 执行端口数 × 依赖链长度（经验值 4-16）。
- **不要过度展开**：超过 L1 I-cache 的展开会让性能断崖。
- 编译器 `-funroll-loops` 通常比手动展开更聪明。

### 原则 8：浮点除法/模运算极慢，用近似替代

**问题**（Vol 4 数据）：
- `idiv`（整数除法）：**20-30 cycle**
- `divsd`（double 除法）：**13-14 cycle**
- `imul`（整数乘法）：**3 cycle**
- `mulsd`（double 乘法）：**4-5 cycle**

除法比乘法慢 **5-10×**。

**Agner 的解药**（Vol 1 §11.8）：
1. **常量除法变常量乘法倒**：
   ```cpp
   // ❌ 慢
   int y = x / 7;
   // ✅ GCC -O2 自动转换成乘法（看汇编验证）
   // 等价于 y = (int)((int64_t)x * 0x92492493 >> 34);
   ```
2. **浮点倒数近似**：`rcpss`/`vrcp14sd`（精度低但快 3×），需要 Newton-Raphson 修正。
3. **避免循环里的 `%`**：用计数器递增+reset 替代。

🧪 见 demo §7 `demo_float_reciprocal` —— Newton-Raphson 倒数迭代的精度/性能权衡。

### 原则 9：CPU Dispatching —— 运行时选最优实现

**问题**：编译时 `-march=native` 只优化本机；分发到客户的二进制不能这样。

**Agner 的解药**（Vol 1 §12 + Vol 2 §13）：
```cpp
// 运行时检测 CPU 特性，分发到最优实现
#include <cpuid.h>

enum class CpuFeat { SSE2, AVX2, AVX512 };

CpuFeat detect_cpu() {
    unsigned a, b, c, d;
    __get_cpuid(7, &a, &b, &c, &d);
    if (b & bit_AVX512F) return CpuFeat::AVX512;
    if (b & bit_AVX2)    return CpuFeat::AVX2;
    return CpuFeat::SSE2;
}

void (*kernel)(const float*, float*, size_t) =
    detect_cpu() == CpuFeat::AVX512 ? &kernel_avx512 :
    detect_cpu() == CpuFeat::AVX2   ? &kernel_avx2   : &kernel_sse2;
// 注意：ifunc / __attribute__((target_clones)) 是 GCC/Clang 的更优雅写法
```

**真实案例**：glibc 的 memcpy/strlen 就是这么做的（运行时 dispatch 到不同的 SSE/AVX 实现）。

🧪 见 demo §6 `demo_cpu_dispatch` —— 用 Python 模拟 CPUID 检测 + dispatch 决策。

### 原则 10：编译器是你的朋友，但要会读汇编

**Agner 的建议**（Vol 1 §4 + Godbolt）：
1. 用 `-O3 -march=native -flto` 作生产 baseline。
2. **每次优化后用 `-S` 或 Godbolt 看汇编**：验证编译器是否真的生成了你想要的代码（向量化是否生效？是否被 cmov 化？是否常量折叠？）。
3. **不同编译器差异巨大**：
   - GCC：保守、稳定、Linux 默认
   - Clang：激进、向量化强、macOS 默认
   - MSVC：Windows 默认、向量化较弱
   - ICX（Intel oneAPI）：Intel CPU 上最强，已基于 LLVM
4. **`restrict` / `__restrict` 关键字**：告诉编译器"指针不重叠"，解锁更多优化。

---

## 🔬 第 3 部分：Intel / AMD 微架构家族对比

> 数据来源：Agner Vol 3（2026-05）+ [uops.info](https://uops.info/)。**厂商手册里查不到**的细节都在这里。

### 3.1 现代 CPU 的关键参数（决定优化的天花板）

| 参数 | Intel Skylake (2015) | Intel Golden Cove (Alder Lake P-core, 2021) | AMD Zen 3 (2020) | AMD Zen 4 (2022) | 含义 |
|------|------|------|------|------|------|
| **解码宽度** | 4-5 指令/cycle | 6 | 4 | 4 | 每周期解码几条 x86 指令 |
| **μop 调度宽度** | 6 | 6 | 6 | 6 | 每周期发射几条 μop 到执行端口 |
| **退役宽度** | 4 | 6 | 4 | 4 | 每周期完成几条 μop |
| **ROB（Reorder Buffer）** | 224 | 512 | 256 | 320 | 在飞 μop 上限，决定 ILP 上限 |
| **RS（Reservation Station）** | 97 | 2×64 | 96（统一） | 96 | 等待数据的 μop 容量 |
| **执行端口数** | 8 | 12 | 10 | 10 | 每周期最多几条 μop 同时执行 |
| **L1 D-cache** | 32 KB / 8 way | 48 KB / 12 way | 32 KB / 8 way | 32 KB / 8 way | 延迟 4-5 cycle |
| **L2 cache** | 256 KB / 4 cycle | 1.25 MB / 14 cycle | 512 KB / 12 cycle | 1 MB / 14 cycle | 延迟 |
| **分支预测器** | TAGE | TAGE + IT-TAGE | Perceptron | Perceptron | 误预测率 |
| **分支误预测代价** | 15-20 cycle | 18-22 cycle | 19 cycle | 19 cycle | 流水线 flush 成本 |

**优化启示**：
- Golden Cove（Alder Lake+ P-core）的 ROB 翻倍到 512，**ILP 容量大幅提升**，依赖链稍长也能掩盖。
- Alder Lake 的 **P-core + E-core 混合架构**是优化噩梦：E-core（Gracemont）ROB 只有 64，跑同样的代码速度可能差 3×。**异构 CPU 必须做线程亲和性绑定**。
- AMD Zen 用 **Perceptron 分支预测器**（神经网络），对重复模式预测更准。

### 3.2 执行端口（Skylake 为例，Vol 3 §Skylake）

```
Port 0:  ALU, SIMD ALU, FMA, mul, div, AES
Port 1:  ALU, SIMD ALU, FMA, mul
Port 2:  Load (地址生成)
Port 3:  Load (地址生成)
Port 4:  Store (数据写)
Port 5:  ALU, SIMD ALU
Port 6:  ALU, branch
Port 7:  Store (地址生成)
```

**优化启示**：
- 两个 Load 端口（2, 3）→ 每周期可同时做 2 次内存读 → 数据预取友好。
- 一个 Store 数据端口（4）→ 写比读慢。
- 浮点 FMA 在 port 0/1 → 2 个 FMA / cycle → 矩阵乘理论峰值 16 flop/cycle（AVX-512）。

🧪 见 demo §2 `demo_uop_scheduling` —— 模拟 Skylake 8 端口调度器，看不同 μop 序列的实际吞吐。

### 3.3 关键反直觉发现（Agner 实测）

1. **μop 融合（μop fusion）**：`add eax, [mem]` 在解码层是 1 个 μop（不是 2 个），因 macro-op fusion。
2. **register file 比 ROB 大**：Skylake 物理寄存器堆 180+ 项（整数）/ 168 项（向量），寄存器重命名让你"看起来"只有 16 个 GPR 但实际很多。
3. **store-to-load forwarding**：写后立刻读同一地址，可以从 store buffer 直接转发，不用等 L1。
4. **`bsf/bsr` 在不同 CPU 上延迟差 10×**：Zen3 上是 1 cycle（硬件优化），Skylake 上是 3 cycle。
5. **AVX-512 在 Skylake-X 上降频**：使用 AVX-512 触发 license level 2/3，CPU 主频降 100-300 MHz——**轻度 AVX-512 可能反而慢**（Vol 3 §Skylake-X）。

---

## 📊 第 4 部分：指令延迟 / 吞吐 / μop 查表方法论

### 4.1 三个核心指标（必背定义）

| 指标 | 定义 | 含义 |
|------|------|------|
| **Latency（延迟）** | 一条指令从输入就绪到输出可用的 cycle 数 | 数据依赖链的累积延迟 |
| **Throughput（吞吐）** | 同类型连续指令，每条平均占用端口的 cycle 数 | 独立指令流的吞吐瓶颈 |
| **μop 数** | 一条指令解码成的微操作数 | 解码器压力 |

**例子**（Skylake，Vol 4 数据）：
- `add r32, r32`：latency 1，throughput 0.25，μops 1
  - 4 条独立 `add` 可在 1 cycle 完成（吞吐 0.25 = 1/4 cycle per instr）
- `imul r32, r32`：latency 3，throughput 1，μops 1
  - 链式 `imul`：3 cycle/条；独立 `imul`：1 cycle/条
- `idiv r32`：latency **20-30**，throughput **20-30**，μops 10
  - 极慢，除法永远是热点嫌疑
- `vfmadd231ps zmm, zmm, zmm`：latency 4，throughput 0.5，μops 1
  - AVX-512 FMA：2 条独立 FMA / cycle，每条算 16 个 float 乘加 → **32 flop/cycle 理论峰值**

### 4.2 关键热点指令替换表（Agner Vol 4 + Vol 1 §11 综合）

| 慢操作 | cycle | 替代 | cycle | 提速 | 适用条件 |
|--------|-------|------|-------|------|---------|
| `idiv r, 7` | 20-30 | `imul r, magic`（编译器自动） | 3 | **7-10×** | 除数是编译期常量 |
| `x % 8` | 20-30 | `x & 7` | 1 | **20×** | 模 2 的幂 |
| `x / 16` | 20-30 | `x >> 4` | 1 | **20×** | 除 2 的幂 |
| `divsd`（double 除）| 13-14 | `mulsd` × Newton-Raphson | ~6 | **2×** | 可接受近似 |
| `if (x<0) x=-x`（难预测）| 15-20 flush | `(x^mask)-mask` | 1 | **15×** | 分支不可预测时 |
| `__builtin_popcount` | 3 | （直接用）POPCNT 指令 | 3 | — | 现代 CPU 已是单指令 |
| `std::max(a,b)`（难预测）| 15-20 | `cmov`（编译器自动）| 2 | **8×** | 分支不可预测时 |
| `memcpy` 循环 | n×1 | `memcpy`（asmlib/glibc）| n/16 | **16×** | 大块拷贝 |
| `std::sin`（精度满）| 50-100 | 多项式近似 | 5-10 | **10×** | 牺牲精度 |

### 4.3 怎么查（Vol 4 用法）

```
1. 用 objdump -d / Compiler Explorer 看热点循环的汇编
2. 在 Vol 4 PDF（或 instruction_tables.ods）按指令查找
3. 计算理论 cycle = max(latency 依赖链, Σthroughput per port)
4. 用 testp 实测验证
5. 找到最大占比的指令，优先优化
```

🧪 见 demo §5 `demo_instruction_substitution` —— 用模拟器对比 div/mul/branch/cmov 的 cycle 数。

---

## 🚀 第 5 部分：SIMD 向量化工程实战

### 5.1 SIMD 指令集谱系

| 指令集 | 寄存器宽度 | 同时算几个 float | 几时普及 | 备注 |
|--------|----------|----------------|---------|------|
| **SSE/SSE2** | 128 bit | 4 | 1999-2001 | x86-64 标配 |
| **AVX/AVX2** | 256 bit | 8 | 2011-2013 | 现代 CPU 标配 |
| **AVX-512** | 512 bit | 16 | 2017+ | 服务器/HPC |
| **FMA3** | 256/512 | 8/16 乘加 | 2013+ | `a*b+c` 单指令 |
| **AMX** | 1024 bit | 矩阵 | 2023+ | Sapphire Rapids 矩阵乘加速 |

### 5.2 自动向量化 vs 手动向量化

**自动向量化**（Agner Vol 1 §10.5）：
```bash
gcc -O3 -ftree-vectorize -fopt-info-vec-optimized main.cpp
# 输出：main.cpp:12:5: optimized: loop vectorized using 16 byte vectors
```

**让代码可被自动向量化**：
1. 无数据依赖（循环里不写 `arr[i] = arr[i-1] + 1`）
2. 边界已知（避免 `while (*p)` 这种）
3. 无函数调用（或用 `__attribute__((always_inline))`）
4. 用 `restrict` 标注指针不重叠

**手动向量化优先级**：
1. **VCL（Vector Class Library）**：最安全、最易维护
2. **C++ intrinsic**（`<immintrin.h>`）：性能极致、可移植性需处理
3. **内联汇编**：除非编译器实在不生成想要的代码，否则不用

### 5.3 AVX-512 的两个陷阱（Agner Vol 3 §Skylake-X）

1. **降频**：用 AVX-512 触发 license level，主频降 100-300 MHz。**短循环可能净亏**。解药：用 "light" AVX-512（只用 128/256 寄存器，不降频）。
2. **opmask 寄存器**：AVX-512 的掩码操作很强大（如"只对偶数元素加 1"），但滥用会让代码可读性归零。

🧪 见 demo §4 `demo_simd_throughput` —— SSE/AVX/AVX-512 的吞吐对比 + 降频模拟。

---

## 🌐 第 6 部分：调用约定与 ABI 陷阱（Vol 5）

### 6.1 三大主流 ABI 对比

| 平台 | 整数参数寄存器 | 浮点参数寄存器 | 返回值 | callee-saved |
|------|------------|-------------|-------|------------|
| **System V AMD64**（Linux/macOS）| rdi, rsi, rdx, rcx, r8, r9 | xmm0-xmm7 | rax / xmm0 | rbx, rbp, r12-r15 |
| **Windows x64** | rcx, rdx, r8, r9 | xmm0-xmm3 | rax / xmm0 | rbx, rbp, rdi, rsi, r12-r15 |
| **ARM64 (AAPCS64)** | x0-x7 | v0-v7 | x0 / v0 | x19-x29 |

### 6.2 跨平台代码的 3 个陷阱

1. **影子空间（shadow space）**：Windows x64 调用者必须在栈上预留 32 字节给被调用者使用；System V 不需要。
2. **变长参数（variadic）**：System V 浮点参数要同时写入整数寄存器（xmm0 + rdi 等）；macOS 也变种。
3. **结构体返回**：>16 字节的结构体（System V）通过隐藏指针返回；Windows 阈值是 8 字节。

### 6.3 name mangling（C++ 符号修饰）

```bash
# 看 mangled symbol
nm libfoo.so | grep foo
# _Z3fooii  →  Itanium ABI（GCC/Clang）：foo(int, int)
# ?foo@@YAHHH@Z  →  MSVC ABI
```

**跨编译器链接 .o 文件**：必须用 `extern "C"` 关闭 mangling，且 ABI 兼容。否则链接失败或运行时栈崩。

🧪 见 demo §8（在 demo 文件里）`demo_calling_convention` —— 模拟三种 ABI 的寄存器使用。

---

## 🎯 第 7 部分：浮点优化与 NaN 传播（含 2026-08 最新论文）

### 7.1 浮点的 4 个性能陷阱

1. **除法慢 5-10×**（见第 4 部分）
2. **非规格化数慢 10-100×**（见 [CSAPP_HARDWARE_TRUTHS.md](CSAPP_HARDWARE_TRUTHS.md) 真相 8）
3. **transcendental 函数慢 50-100×**（`sin/cos/exp/log`）→ 用多项式近似（SLEEF / FDlibm）
4. **`-ffast-math` 的代价**：打破 IEEE 754 严格语义，换性能；可能改变 NaN/Inf 行为

### 7.2 nan_propagation（Agner 2026-08 最新论文）

**问题**：在 OoO + SIMD 下，浮点异常（除零、溢出）**何时上报**？传统 x87 的 `#P/#U/#O` 异常在乱序执行下失去了精确位置。

**Agner 的方案**：
- **不再依赖硬件异常**，改用 **NaN 编码**：每个异常产生带 payload 的 NaN，沿计算流传播。
- 检查时扫描结果里的 NaN payload，即可定位异常源头。
- 这是 JavaScript `Math.f16` / WebAssembly exception handling / ML 训练框架（PyTorch/JAX）正在采用的方案。

**对工程的影响**：
- AI 训练里常见的 NaN loss，**不再靠 try/catch**，而是靠 NaN payload 反向追踪到具体的算子。
- C++23 `std::float16_t` / `std::bfloat16_t` 已引入；GPU 厂商（NVIDIA/AMD）在硬件层支持 NaN payload。

---

## 🗺️ 第 8 部分：与 CSAPP 8 真相的映射（完整链路）

| CSAPP 真相 | Agner 深化卷 | 具体优化手法 | demo 章节 |
|-----------|------------|------------|----------|
| 真相 1 Cache | Vol 1 §7 + Vol 2 §6 | AoS→SoA、热字段分离、`alignas` | demo §1 |
| 真相 2 虚拟内存 | Vol 4 内存指令延迟 | 大页、`mlock`、避免跨 page | demo §1 |
| 真相 3 栈溢出 | Vol 5 调用约定 | ABI、shadow space、name mangling | demo §8 |
| 真相 4 分支预测 | Vol 1 §8 + Vol 3 §分支预测器 | 位运算、cmov、TAGE/Perceptron | demo §2 §5 |
| 真相 5 伪共享 | Vol 2 §7 | `alignas(64)`、padding | （见 hardware_truths_demo §5）|
| 真相 6 syscall | （Agner 不涉及）| io_uring、零拷贝 | （见 hardware_truths_demo §6）|
| 真相 7 内存乱序 | Vol 3 §store buffer | Store forwarding、memory fence | demo §2 |
| 真相 8 IEEE754 | Vol 1 §11 + nan_propagation | FTZ/DAZ、Newton-Raphson 倒数、NaN payload | demo §7 |

---

## 🧰 第 9 部分：工具链使用指南

### 9.1 VCL（Vector Class Library）—— SIMD 的安全壳

```bash
# 安装
git clone https://github.com/vectorclass/version2
cd version2 && make
```

```cpp
#include "vectorclass.h"
// 同一份代码自动适配 SSE/AVX/AVX-512
Vec8f a = Vec8f(arr);   // AVX2: 8 floats
Vec8f b = Vec8f(arr+8);
Vec8f c = a + b * 2.0f; // 自动生成 vfmadd
c.store(out);
```

### 9.2 testp —— 函数级微基准测试

```bash
unzip testp.zip && cd testp
make
./testp  # 交互式选 CPU、设置 PMU 计数器、跑一小段 asm/c 代码
```

**用途**：测 `a*b+c` 在 Skylake 上到底是 4 cycle 还是 5 cycle（perf 测不出来，因为 perf 是程序级）。

### 9.3 objconv —— 比 objdump 强的反汇编器

```bash
./objconv -f asm binary.out binary.asm
# 支持 AVX-512、FMA、掩码寄存器，输出比 objdump -d 更可读
```

### 9.4 asmlib —— 比 glibc 快的 asm 函数

```cpp
// 替换 <string.h> 的等价函数
extern "C" size_t A_strlen(const char*);
extern "C" void* A_memcpy(void*, const void*, size_t);
// 链接 asmlib 的 .a/.lib 即可，比 glibc 快 1.5-3×
```

### 9.5 perf / VTune / likwid —— 全程序 profile

```bash
# Linux 通用
perf stat -e cycles,instructions,cache-misses,branch-misses ./a.out
perf record -g ./a.out && perf report

# Intel VTune（GUI，最强）
# AMD uProf
# 跨平台轻量级 likwid
likwid-perfctr -g L3_CACHE ./a.out
```

---

## 🛣️ 第 10 部分：学习路径（按角色）

### 编译器工程师（最高强度）
1. **Vol 3 全卷精读**（每个 CPU 家族）
2. **Vol 4 完整指令表**（写入编译器 cost model）
3. **Vol 5 ABI**（生成跨平台调用代码）
4. 论文：TAGE 分支预测器、ROB 设计、register renaming
5. 实战：给 LLVM / GCC 提一个 cost model 修复 PR

### 游戏引擎 / 实时渲染
1. **Vol 1 §7-§12**（C++ 数据布局、向量化、CPU dispatch）
2. **VCL** 全套
3. **Vol 3 §Skylake-X / Zen**（目标平台微架构）
4. 实战：手写一个 SIMD 矩阵乘（4×4 matrix），用 testp 测 cycle

### 数据库内核 / 高频交易
1. **Vol 1 全卷**（容器、内存、并发）
2. **Vol 3 §store buffer / cache 一致性**（CSAPP 真相 5+7 的深化）
3. **asmlib** memcpy/strlen
4. 实战：写一个 lock-free ring buffer，用 perf c2c 测伪共享

### HPC / AI 算子优化
1. **Vol 1 §10 向量化** + **Vol 2 §11 SIMD 编程**
2. **AVX-512 / AMX** 指令集手册
3. **nan_propagation** 论文（NaN 在训练中的传播）
4. 实战：手写一个 AVX-512 矩阵乘（参考 [mit 6.5940](https://hanlab.mit.edu/courses/2023-fall-65940)）

### 嵌入式 / RTOS / 系统
1. **Vol 5 调用约定**
2. **Vol 1 §5 平台选择**
3. 实战：把一段裸 C 代码改成跨 GCC/IAR/Keil 都能链接

---

## 🎓 第 11 部分：必做实战清单（按 ROI 排序）

| # | 任务 | 投入 | 学到的 |
|---|------|------|-------|
| 1 | 用 `-O3 -fopt-info-vec-optimized` 看一段循环是否被向量化 | 1h | 自动向量化诊断 |
| 2 | 用 Godbolt 对比 `-O0/-O2/-O3/-march=native` 生成的汇编 | 2h | 编译器优化直觉 |
| 3 | 手写 AoS vs SoA 的粒子系统，perf 测 cache-miss | 3h | 数据布局收益 |
| 4 | 把单 accumulator 改成 4-way，测加速比 | 2h | ILP 打破依赖 |
| 5 | 用 VCL 写一段 SIMD 浮点运算，测 AVX2 加速比 | 4h | SIMD 工程化 |
| 6 | 用 testp 测 `idiv` vs `imul` 的实际 cycle | 2h | 微基准方法 |
| 7 | 实现一个 CPU dispatch 函数（SSE/AVX2/AVX512 三路） | 4h | 运行时分发 |
| 8 | 写一个 lock-free counter，`alignas(64)` 前后对比 perf c2c | 3h | 伪共享根治 |
| 9 | 用 Newton-Raphson 写一个近似 `1/x`，测精度 vs 速度 | 3h | 浮点近似 |
| 10 | 用 perf stat 完整剖析一个真实程序，找瓶颈 | 5h | profile 方法论 |

---

## 📚 第 12 部分：核心参考资料

### 必读（免费 PDF）
- ⭐ **Agner Vol 1-5**：[agner.org/optimize/](https://www.agner.org/optimize/)
- **Drepper "What Every Programmer Should Know About Memory"**（2007，lwn.net）—— 内存层次最权威长文
- **Intel SDM Vol 2B（指令集参考）+ Vol 3A（系统编程）**
- **Intel Optimization Reference Manual**

### 工具
- **[Godbolt](https://godbolt.org/)**：在线编译器对比，**最高频使用工具**
- **[uops.info](https://uops.info/)**：指令延迟在线数据库（机械测量）
- **[Perf Wiki](https://perf.wiki.kernel.org/)**：Linux perf 完整文档
- **[Likwid](https://github.com/RRZE-HPC/likwid)**：易用的 PMU 工具

### 经典论文（Agner 多次引用）
- **TAGE branch predictor**（Seznec，2006）
- ** Understanding the Linux Kernel (ULK)** —— 内核侧
- **Smith "Cache Memories" 1982 IEEE** —— cache 设计基础

### 高级课程
- **MIT 6.5940**（Han Lab）：AI 算子优化（AVX-512 / AMX）
- **CMU 15-418/618 Parallel Computer Architecture**（同构/异构并行）
- **Stanford CS149**：并行计算 + 性能剖析

---

## 🔗 与本项目的关联

| 本文档章节 | CSAPP 真相 | UNIFIED_ROADMAP | 项目代码 |
|-----------|----------|----------------|---------|
| 第 2 部分 10 原则 | 真相 1-8 综合 | L03 | [csapp.py](./cmu-cs-projects/topic2-systems/csapp.py) + [hardware_truths_demo.py](./cmu-cs-projects/topic2-systems/hardware_truths_demo.py) |
| 第 3 部分 微架构 | 真相 1, 4 | L03 + L21 (MLSys) | [agner_optimization_demo.py](./cmu-cs-projects/topic2-systems/agner_optimization_demo.py) §2 |
| 第 4 部分 指令表 | 真相 4, 8 | L03 | demo §5 |
| 第 5 部分 SIMD | — | L11 + L14 (CV) | demo §4 |
| 第 7 部分 浮点 | 真相 8 | L11 + L21 | demo §7 |

> 📖 **本文档是 x86 阵营的圣经**。ARM/RISC-V 阵营的差异巨大（VLA SIMD、弱内存模型、厂商实现差异），见对称续作 **[ARM_AND_RISCV_OPTIMIZATION.md](ARM_AND_RISCV_OPTIMIZATION.md)**（含 Apple Silicon 逆向 / AWS Graviton 实战 / RISC-V RVV / OSACA 工具 / 跨平台 dispatch）。

---

**完成日期**：2026-08-12
**作者**：AI Mentor (ai-mentor) + 学生
**版本**：v1.0
**配套**：CSAPP_HARDWARE_TRUTHS.md（原理前置）+ INSIGHTS_FULL_PICTURE.md（元洞察）+ agner_optimization_demo.py（可跑 demo）
**数据时效**：基于 Agner 手册 2025-09 ~ 2026-08 最新版本
