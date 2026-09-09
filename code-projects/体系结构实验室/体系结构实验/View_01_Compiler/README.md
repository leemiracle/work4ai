# View_01_Compiler — 编译器视角

> **切入问题**：同一份 C 代码，不同 `-O` 等级、不同编译器、不同选项，
> 会**变成什么指令**？为什么 `-O3` 比 `-O2` 快？什么时候快、什么时候反而更慢？
>
> **主导思维**：工程决策——不直接看硬件，而是看"**编译器替你做了什么决定**"。

---

## 1. 为什么需要这个视角？

[Lab00-Lab07](../) 全部是"假设编译器已经把 C 变成最优指令"。
但实际上：

1. **`-O0` 和 `-O2` 差 4× 性能**（本项目实测，见下表）
2. **`-O3` 和 `-Ofast` 又能差 4×**（fast-math 允许重关联）
3. **同一段代码，gcc vs clang vs PhyGCC 选不同指令**
4. **`-ftree-vectorize` 失败的原因**就是优化的真正瓶颈

**编译器是你和硬件之间的"翻译官"**——它翻译得好不好，直接决定 Lab 测的数据是否反映真实硬件能力。

---

## 2. 实测：同一代码 × 6 个 `-O` 等级

源代码：[`src/opt_compare.c`](./src/opt_compare.c)（点积 / 条件累加 / 多项式 / 死代码 / 手展开）

跑 `make compare` 自动生成：

| Opt-level | 时间 (ms) | 二进制 (B) | dot_product 反汇编行数 |
|-----------|---------:|---------:|--------------------:|
| `-O0` | 13.05 | 13824 | 33 |
| `-O1` | 3.39 | 13872 | 16 |
| `-O2` | 3.34 | 13872 | 14 |
| `-O3` | 3.27 | 13896 | 54 |
| `-Os` | 4.94 | 13872 | **12**（最紧凑） |
| `-Ofast` | **0.83** 🚀 | 15208 | 50 |

> **飞腾 D3000M / gcc 9.3.1 / 1000 次 N=4096 点积**

### 关键观察

- **`-O0 → -O1`：4× 加速**——寄存器分配 + 死代码消除 + 简单指令融合
- **`-O1 → -O2/O3`：基本持平**——点积循环已经很紧凑，进一步优化空间小
- **`-O3 → -Ofast`：又一个 4×**——`-ffast-math` 允许 FP 重关联（`(a+b)+c ≠ a+(b+c)`），可重排成 4 路并行 NEON `fmla`
- **`-Os` 反而比 `-O2` 慢**——它优先缩代码大小，不做激进展开
- **`-O3` 代码行数 54 比 `-O0` 的 33 还多**——展开 + 向量化增加代码，但每条指令做的事更多

---

## 3. 向量化报告（`make vectorize`）

gcc 提供 `-fopt-info-vec*` 系列选项告诉你**为什么向量化成功 / 失败**：

### 成功的向量化
```
opt_compare.c:25:5: optimized: loop vectorized using 16 byte vectors
```
→ `dot_product` 被自动向量化成 NEON `fmla v0.4s, v1.4s, v2.4s`（4 路并行）

### 失败的向量化（更教学）
```
opt_compare.c:34:5: missed: couldn't vectorize loop
opt_compare.c:34:5: missed: not vectorized: control flow in loop.
```
→ `conditional_sum` 循环里有 `if (a[i] > threshold)`——**分支阻止向量化**。
**修法**：改成无分支的 mask 累加，或用 `__builtin_expect` + cmov。

```
opt_compare.c:46:5: missed: couldn't vectorize loop
```
→ `poly_eval` 用 Horner 法 `result = result * x + coef[i]`，**循环携带依赖**，不可能并行。
**修法**：改成 4 路 Horner 并行（4 个独立多项式同时算）。

### 别名分析
```
opt_compare.c:64:5: optimized: loop versioned for vectorization because of possible aliasing
```
→ `manual_unroll` 里 `out[]` 和 `in[]` 可能重叠（编译器不知道），所以**生成两个版本**：
运行时检查若不重叠走向量化版，否则走标量版。这是 `-frestrict` 关键词的意义。

---

## 4. 决策树：什么时候选哪个 `-O`？

```
你的代码是...
│
├─→ 调试 / 学汇编      : -O0 -g（最忠实源码，每行对应多条指令）
│
├─→ 生产默认           : -O2（最佳投资回报率）
│                         ├ 不开启激进向量化（避免代码膨胀）
│                         ├ 不开启 fast-math（保留 FP 语义）
│                         └ 不开启激进 inline（避免 I-cache 压力）
│
├─→ 数值密集（HPC/ML）  : -O3 -march=native
│                         ├ -ftree-vectorize（默认 -O3 开）
│                         ├ -funroll-loops
│                         └ 加 -ffast-math **当且仅当** 不在意 IEEE 754 严格语义
│
├─→ 嵌入式 / Flash 紧  : -Os（代码最小）
│                         └ 性能损失 10-30%，但 binary 小 30%+
│
└─→ 极致性能            : -Ofast（含 -ffast-math）
                          └ 警告：FP 结果可能与 -O2 不同（重关联）
```

---

## 5. PhyGCC vs 主线 GCC

飞腾平台专用 [PhyGCC](https://...)（`kpgcc`）在 `-mcpu=ftc86x` 上做了调优：
- 调度器知道飞腾的具体流水线端口分布
- NEON 指令选择更精准
- LSE/FP16 等 ARMv8.x 扩展默认开启

**对比方法**（如果机器装了 PhyGCC）：
```bash
gcc -O2 -march=armv8.2-a+simd+lse src/opt_compare.c -o build/gcc_O2
kpgcc -O2 -mcpu=ftc86x src/opt_compare.c -o build/kpgcc_O2
# 比较性能 + 反汇编
```

通常 PhyGCC 比主线 gcc 快 5–15%，主要来自指令调度。

---

## 6. 内联汇编 vs C intrinsic

飞腾 NEON 可以两种方式调用：

```c
// 方式 1: 内联汇编（最控制力，最难写）
asm volatile ("fmla v0.4s, v1.4s, v2.4s" : "+w"(acc) : "w"(b), "w"(c));

// 方式 2: C intrinsic（推荐，编译器能寄存器分配/调度）
#include <arm_neon.h>
float32x4_t acc = vdupq_n_f32(0);
acc = vfmaq_f32(acc, b, c);
```

**为什么推荐 intrinsic**：
- 编译器知道指令语义，能跨 intrinsic 调度
- 不阻碍 `-O3` 向量化其他部分
- 跨平台（同一份代码 ARM NEON / x86 AVX 可移植到不同头文件）

详见 [Lab05/gemm_full_stack.c](../Lab05_并行与SIMD/src/gemm_full_stack.c) 第 4 步 NEON 优化。

---

## 7. 常见编译器陷阱

### 7.1 `volatile` 滥用
```c
volatile int x;  // 每次访问都强制访存，禁止寄存器缓存
```
教学实验里用 volatile 防 DCE 是对的，**但生产代码千万别滥用**——它会拖慢 5-10×。

### 7.2 `__attribute__((optimize("O3")))`
单函数级别开 `-O3` 看似精准，实际**破坏全局优化**（LTO/IPPA 失效）。
**正确做法**：把热函数拆到单独 `.c` 文件，对该文件单独设 `-O3`。

### 7.3 `-ffast-math` 的隐性副作用
- 假设 FP 不会 NaN/Inf（异常检测失效）
- 允许 `(a+b)+c ≠ a+(b+c)`（Kahan 求和失精度）
- 假设除以零不会发生
**安全替代**：`-fno-math-errno`（不影响语义但允许部分优化）。

### 7.4 别名陷阱
```c
void add(float *a, float *b, float *c, int n) {
    for (int i = 0; i < n; i++) c[i] = a[i] + b[i];  // 可能别名？
}
```
若 `c` 与 `a` 重叠，向量化会出错。编译器保守起见生成双版本。
**修法**：`restrict` 关键字 `float * restrict c`。

---

## 8. 跑这个视角

```bash
cd View_01_Compiler
make compare    # 编译 6 个 -O 版本 + 性能对比
make disasm     # 反汇编 + dot_product 函数大小对比
make vectorize  # 向量化报告（成功 vs 失败）
```

📌 **下一步**：去 [View_02_Security](../View_02_Security/) 看"攻击者视角"——
当编译器/硬件的优化被恶意利用时会发生什么（Spectre/cache timing）。
