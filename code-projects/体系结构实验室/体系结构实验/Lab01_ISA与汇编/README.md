# Lab01 — ISA 与汇编：C 如何变成飞腾能懂的指令

> "你看不懂的汇编，机器每天都跑几十亿次。"
>
> 这是 Patterson 第 2 章的核心：理解 C 代码与汇编的对应关系。

---

## 0. 学习目标（一句话）

**看懂任何一段 C 代码编译出的 ARM64 汇编，并能手写关键的汇编片段**（NEON、内联汇编、调用约定）。

---

## 1. 对应教材与课程

| 来源 | 章节 | 重点 |
|------|------|------|
| 📘 Patterson RISC-V | **Ch2 (Instructions)** | RISC-V RV32I/RV64I 指令集 |
| 📘 Patterson RISC-V | **Ch2 §2.8** | 过程调用、栈帧（与 ARM 对照） |
| 📗 CAQA 5th | **Appendix A** | 指令集原则（巨细，作为参考） |
| 📕 姚永斌超标量 | **Ch5 (指令集体系)** | MIPS/ARM/RISC-V 对比 |
| 🎓 CS61C | Proj1/Proj2 | C ↔ RISC-V 汇编 + MNIST 神经网络 |
| 🎓 CSAPP | Ch3 (Machine-Level Representation) | x86 视角，但概念相通 |
| 📖 ARM ARM | "A64 Instruction Set" | ARMv8 权威参考 |

**关键对比**：飞腾是 ARM64（AArch64），但书 1 用 RISC-V。两者都是 RISC，但寄存器数、寻址方式、立即数编码都不同——这个差异本身就是学习点。

---

## 2. 核心概念速览

### 2.1 直觉：为什么先要看汇编？

```
你写的 C：      sum += a[i]
编译器看到的：   一堆规则
CPU 看到的：    ldr x0, [x1, x2, lsl #3]
                add x3, x3, x0
```

**性能优化的所有秘密都在汇编里**。优化器（如 PhyGCC）做了什么取舍、为什么飞腾特别爱用 NEON、为什么 `volatile` 让编译器没法消除——都只能在汇编层看到。

### 2.2 ARM64 (AArch64) vs RISC-V 关键差异

| 特性 | ARM64 (飞腾) | RISC-V (Patterson 书) |
|------|--------------|----------------------|
| 寄存器数 | **31 个通用** (X0-X30) | **31 个** (x0-x30) |
| 指令长度 | 32 位固定 | 32 位固定（RVC 扩展可 16 位）|
| SP/PC | SP=X31（隐式），PC 不可直接读 | sp=x31，pc 可读 |
| 返回地址 | LR=X30，BL/BLR/RET | ra=x1，jal/jalr |
| 调用约定前 8 个参数 | X0-X7 | x10-x17 (calling convention 不同) |
| 立即数 | 12 位 + 移位 / MOVZ+MOVK | 12 位 + 移位 / LUI+ADDI |
| 条件码 | NZCV（4 个标志） | **无**（用分支） |
| 条件执行 | `addeq`, `cbz`, `csel` | 不支持（除分支外） |
| SIMD | NEON（128-bit，V0-V31） | RVV（向量扩展，可变长） |
| 内存访问 | Load/Store，**寻址丰富** | Load/Store，仅 imm+reg |
| 寻址模式 | `[Xn, Xm]`, `[Xn, #imm]`, `[Xn, Xm, LSL #n]`, pre/post-index | `offset(rs1)` |

### 2.3 一张图：A64 函数调用栈帧

```
高地址
┌────────────────────┐
│  caller 的 X19-X29  │  ← callee-saved（必须保存）
│  (如果用了)         │
├────────────────────┤
│  FP (X29) →─────────┤ ← 帧指针
│  LR (X30)           │  ← caller 返回地址
├────────────────────┤
│  局部变量、溢出寄存器│
├────────────────────┤
│  给 callee 的参数   │  ← 栈上参数（超过 8 个时）
├────────────────────┤
│  ... ...            │
低地址
                  SP (X31) →
```

---

## 3. 实验列表

### 3.1 实验 1.1：C → 汇编反向工程（`c_to_asm.c`）

**现象**：同一段 C 代码，`-O0`、`-O1`、`-O2`、`-O3`、`-Ofast` 编译出来的汇编差异巨大。

**假设**（先写）：
- `-O0`：1:1 翻译，每行 C 都对应多条汇编，频繁访存
- `-O1`：寄存器分配优化，循环不变量外提
- `-O2`：循环展开 + 指令调度
- `-O3`：向量化（NEON）
- `-Ofast`：`-O3` + `-ffast-math`（允许浮点 reorder）

**关键代码**（一个非常简单的求和）：
```c
double sum_array(const double *a, int n) {
    double s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}
```

**运行**：
```bash
make c_to_asm
# 自动生成不同优化级别的汇编，并 diff
./disasm_diff.sh sum_array
```

**预期结果**：

| -O0 | -O2 | -O3 |
|-----|-----|-----|
| ~25 条指令，频繁 str/ldr 局部变量 | ~10 条，循环展开 2 次 | **NEON `fadd v0, v0, v1.2d`** |

**解释**：
- `-O0` 把所有局部变量放栈，每次 `i++` 都 ldr+add+str
- `-O2` 把 `s`、`i` 放寄存器，循环展开 2-4 次填充超标量
- `-O3` 识别出可向量化，每条 `fadd v0.2d` 同时算 2 个 double

**缺陷与陷阱**：
- `-ffast-math` 改变浮点结果（不可结合性失效）
- `volatile` 类型无法向量化
- 编译器对 `int n` vs `unsigned n` 可能给出完全不同的代码（有符号溢出是 UB）

**扩展思考**：
- 把 `double` 换成 `float`，看 NEON 一次能处理几个（4 个！）
- 用 `__restrict` 标注无别名，看 `-O3` 是否更激进

---

### 3.2 实验 1.2：调用约定（`calling_conv.c`）

**现象**：函数参数如何传？哪些寄存器需要 callee 保存？返回结构体时栈帧长什么样？

**假设**：
- 前 8 个整数参数走 X0-X7
- 前 8 个浮点参数走 V0-V7
- 第 9 个参数走栈
- X19-X28 是 callee-saved，被调用方必须保存
- X0 是返回值

**关键代码**：
```c
int test_8args(int a1, int a2, int a3, int a4, int a5, int a6, int a7, int a8, int a9) {
    return a1 + a9;
}

double test_4doubles(double a, double b, double c, double d) {
    return a + b + c + d;
}

// 一个 callee-saved 寄存器的探测
int test_callee_saved(void) {
    register int x asm("x19");  // 强制用 X19
    x = 0x1234;
    callee_that_clobbers();     // 调一个会破坏 X19 的函数
    return x;                    // 应该还是 0x1234
}
```

**运行**：
```bash
make calling_conv
./calling_conv
objdump -d calling_conv | sed -n '/<test_8args>:/,/ret/p'
```

**预期汇编**（`test_8args`）：
```asm
test_8args:
    // a1=X0, a9 在栈上 [SP+0]
    ldr w9, [sp]       // 取第 9 个参数
    add w0, w0, w9     // X0 = X0 + 栈上参数
    ret
```

**解释**：你看到 `ldr w9, [sp]` 就知道前 8 个参数寄存器满了，第 9 个从栈上拿。

**缺陷与陷阱**：
- 浮点 + 整型混合时，参数分配规则更复杂（看 AAPCS64 文档）
- 结构体若 ≤16 字节可走寄存器，更大走栈
- Variadic 函数（printf）有专门的栈布局规则

**扩展思考**：
- 看一段优化得好的代码，几乎所有函数都不溢出寄存器——这是怎么做到的？

---

### 3.3 实验 1.3：内联汇编 + NEON SIMD（`inline_asm_neon.c`）

**现象**：手写汇编做 8 个 double 同时加法。

**假设**：
- 一条 `fadd v0.2d` 处理 2 个 double
- 一条 `fadd v0.4s` 处理 4 个 float
- NEON 寄存器 V0-V31，128 位宽

**关键代码**（内联汇编）：
```c
// 4 个 float 同时加（NEON 4-wide）
float dot4_neon(float a[4], float b[4]) {
    float result;
    __asm__ __volatile__(
        "ldr q0, %[a]\n\t"          // 加载 4 个 float 到 q0
        "ldr q1, %[b]\n\t"
        "fmla v0.4s, v0.4s, v1.4s\n\t"  // 4 路乘累加
        "str q0, %[out]\n\t"
        : [out] "=m"(result)
        : [a] "m"(*a), [b] "m"(*b)
        : "v0", "v1", "memory"
    );
    return result;
}
```

**用 NEON intrinsics（推荐）**：
```c
#include <arm_neon.h>
float dot4_intrin(const float *a, const float *b) {
    float32x4_t va = vld1q_f32(a);
    float32x4_t vb = vld1q_f32(b);
    float32x4_t prod = vmulq_f32(va, vb);
    return vaddvq_f32(prod);  // 横向 4 路加和
}
```

**运行**：
```bash
make inline_asm_neon
./inline_asm_neon
objdump -d inline_asm_neon | grep -A 5 "dot4_intrin"
```

**预期**：
- 朴素 C（无向量化）：~4 cycles / 4 元素
- NEON intrinsics：~1 cycle / 4 元素（4-wide）
- 加速 4 倍

**解释**：NEON 寄存器一次装 4 个 float 或 2 个 double，对应指令并行处理。这是后续 Lab05 GEMM 优化的基础。

**缺陷与陷阱**：
- 不要在内联汇编里 clobber 你没声明的寄存器，会破坏编译器的寄存器分配
- intrinsics 比 inline asm 更可移植（推荐用 intrinsics）
- NEON 没有水平加法的单周期指令（`vaddvq` 是多周期）

**扩展思考**：
- 用 NEON 实现 8x8 矩阵乘（一个寄存器装一行）
- 对比 intrinsic vs 内联汇编 vs 自动向量化，三者的代码质量

---

### 3.4 实验 1.4：整数 / 浮点算术（书 1 Ch3，`basic_math.c`）

**现象**：飞腾的整数乘法/除法/浮点 lat 是多少？PhyGCC 的 `-ffast-math` 对结果有多大影响？

**假设**：
- 整数乘法 3-cycle latency
- 整数除法 20+ cycles（除法器慢）
- 浮点加 4-cycle latency
- 浮点乘 5-cycle
- 浮点除 30+ cycles

**关键代码**：
```c
// 探测 latency 的标准方法：建立依赖链
uint64_t latency_mul(uint64_t x) {
    for (int i = 0; i < 1000; i++) {
        x = x * 0x12345ULL + 1;  // 必须依赖上一轮
    }
    return x;
}

uint64_t latency_div(uint64_t x) {
    for (int i = 0; i < 1000; i++) {
        x = x / 7ULL + 1;
    }
    return x;
}
```

**运行**：
```bash
make basic_math
./basic_math
```

**预期结果**（教科书典型值，飞腾实测对照见下）：
| 操作 | Latency (cycles) | Throughput (per cycle) |
|------|-----------------|----------------------|
| add | 1 | 2 |
| mul (int) | 3 | 1 |
| div (int) | ~20 | 0.05 |
| fadd | 4 | 1 |
| fmul | 5 | 1 |
| fdiv | ~30 | 0.05 |
| fsqrt | ~40 | 0.025 |

> 📌 **飞腾 D3000M 实测**（诊断报告 §3，2026-07-02）：div(int) **10.4** / fadd **2.0** / fmul **3.0** / fdiv **13.1** cyc。
> 飞腾的 ALU/FP 流水线比教科书"典型值"更快（更深的流水 + 更激进的前递），实测普遍只有典型值的 40-65%。

**解释**：除法和开方是流水线"硬骨头"——它们要么是迭代算法，要么占大量芯片面积。这也是为什么硬件 FFT 比 DFT 快得多（避免除法）。

**扩展思考**：
- 用 PhyTune 的 `dutpro` 工具验证：`sudo /opt/phytune/.../fpmac_workload`
- 对比不同 -O 级别下编译器是否用位运算替代了除法（`x/8` → `x>>3`）

---

## 4. 学完应该掌握的检查清单

- [ ] 看到任意一段 ARM64 汇编，能识别：函数入口、参数寄存器、返回、栈分配
- [ ] 能解释 `-O0` vs `-O2` vs `-O3` 的具体差异（至少 3 处）
- [ ] 能用 NEON intrinsic 写一个 4-wide SIMD 函数
- [ ] 能用内联汇编写一段不依赖编译器的精确指令序列
- [ ] 能解释为什么 `x/8` 编译后看不到 `sdiv`（编译器优化成移位）
- [ ] 能识别 callee-saved vs caller-saved 寄存器
- [ ] 能用 `objdump -d` 看任意 binary 的反汇编

---

## 5. 参考文献

| 编号 | 文献 | 章节/页码 |
|------|------|----------|
| 📘 | Patterson & Hennessy RISC-V 第2版 | Ch2 §2.1-2.10 |
| 📗 | CAQA 5th | Appendix A.1-A.8 |
| 📕 | 姚永斌超标量 | Ch5 指令集体系 |
| 📖 | **ARM ARM (DDI 0487G.b)** | "A64 Instruction Set"（权威）|
| 📖 | **本项目 [`isa_reference/`](../isa_reference/)** | 从 ARM ARM 提取的指令级深度参考（18 个 md 文件 / 755 条 A64 指令） |
| 📖 | **ARM AAPCS64** | Procedure Call Standard（调用约定）|
| 🎓 | CSAPP Ch3 | x86 版本，但概念通用 |
| 🎓 | CS61C Lecture 5-8 | RISC-V 汇编 |
| 🛠 | `objdump(1)`, `gcc(1)` | `-S` 看汇编，`-d` 反汇编 |

**学 Lab01 时配合读的 isa_reference 章节**：
- 想看 `ADD/LDR/STR/B/BL/MOV/BFM` 等基础指令编码 → [`a64_base_overview.md`](../isa_reference/a64_base_overview.md)
- 想看 `STP/LDP/RET/BLR` 调用约定相关 → [`a64_base_overview.md`](../isa_reference/a64_base_overview.md)
- 想看 `FMLA/LD1/ST1` NEON SIMD → [`v8.0_asimd.md`](../isa_reference/v8.0_asimd.md)
- 想看 `UDOT/SDOT` int8 点积 → [`v8.4_dotprod.md`](../isa_reference/v8.4_dotprod.md)
- 想看 `FCMLA/FCADD` 复数运算 → [`v8.3_fcma.md`](../isa_reference/v8.3_fcma.md)

---

## 6. 编译与运行

```bash
cd Lab01_ISA与汇编
make                 # 编译所有
./c_to_asm           # 看 C 到汇编
./disasm_diff.sh sum_array  # 不同 -O 级别的 diff
./calling_conv       # 调用约定
./inline_asm_neon    # NEON 实战
./basic_math         # 算术 lat/throughput
```

---

📌 **下一步**：完成 Lab01 后，进入 [`Lab02_流水线与ILP/`](../Lab02_流水线与ILP/)。在那里你将看到**为什么 `a = a * 0.5 + b * 0.5` 比 `(a+b)/2` 快得多**——流水线冒险的真面目。
