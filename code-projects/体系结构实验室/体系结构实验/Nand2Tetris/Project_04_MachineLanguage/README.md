# Project 04 — Machine Language：手写 Hack 汇编

> **一句话目标**：用 Hack 汇编语言手写两个程序——`Mult.hack`（乘法）和 `Fill.hack`（键盘交互）。
> **这一关不写 HDL，纯写汇编**——为 P05 造出 CPU 后能跑你写的程序做准备。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch4**（Machine Language）|
| 🎥 Coursera | [Unit 4.1-4.5](https://www.coursera.org/learn/build-a-computer) |
| 🛠 工具 | **CPUEmulator**（nand2tetris 软件套件）|
| ⏱ 预计工时 | 4–8 小时 |

---

## 1. Hack ISA 速览

Hack 是极简 ISA：**只有 2 种指令**。

### 1.1 A 指令（Address）

```
@value      ← 把 value 写入 A 寄存器，同时 M 隐式指向 RAM[value]
```

例：
```
@5          // A = 5；之后 M = RAM[5]
@100        // A = 100；之后 M = RAM[100]
@END        // A = 符号 END 的地址（用汇编器解析）
```

**二进制编码**：`0vvvvvvvvvvvvvvv`（1 位 0 + 15 位地址）。

### 1.2 C 指令（Compute）

```
dest = comp ; jump
```

例：
```
D = M            // D 寄存器 ← RAM[A]
M = D + 1        // RAM[A] ← D + 1
D = M; JGT       // D ← M，然后如果 D > 0 就跳到 @A 的地址
0; JMP           // 无条件跳到 @A 的地址
```

**二进制编码**：`111 a cccccc ddd jjj`（13 位控制）。
其中：
- `a`：选 `M`（a=1）还是 `A`（a=0）作为 ALU 的 y 输入
- `cccccc`：6 个 ALU 控制位（P02 那张表）
- `ddd`：目的（A/D/M/MD/AM/AMD/...）
- `jjj`：跳转（JGT/JEQ/JGE/JLT/JNE/JLE/JMP）

### 1.3 寄存器与内存

| 资源 | Hack | 说明 |
|------|------|------|
| 通用寄存器 | A, D | A 可当地址，D 是数据 |
| RAM | 16K × 16 位（地址 0–16383）| 字寻址 |
| 屏幕映射 | RAM[16384–24575] | 256 × 512 像素 = 32K 字（每字 16 像素）|
| 键盘映射 | RAM[24576] | 按下时存扫描码，松开时为 0 |
| ROM | 32K × 16 位 | 存程序 |

**M 的特殊性**：M 永远代表 `RAM[A]`，所以 A 寄存器既是数据也是地址——这是 Hack 的关键设计权衡（简化）。

### 1.4 符号

| 符号类型 | 例子 | 范围 |
|---------|------|------|
| 预定义 | R0–R15, SCREEN, KBD, SP, LCL, ARG, THIS, THAT | 见书 §4.2.4 |
| 标号 | `(END)` | 在程序里定义，可被 `@END` 引用 |
| 变量 | `@sum` | 汇编器自动分配（从 RAM[16] 开始）|

---

## 2. 你将写的两个程序

### 2.1 `Mult.hack`

**功能**：计算 `R0 * R1`，结果存入 `R2`。
**约束**：
- 不能用乘法指令（Hack 没有乘法）
- 用循环 + 加法实现

**思路**：
```
i = R1
sum = 0
while i > 0:
    sum += R0
    i -= 1
R2 = sum
```

**Hack 汇编**（让你自己写，这里只给伪码 + 提示）：

```asm
// Mult.asm
    @R1
    D=M        // D = R1
    @i
    M=D        // i = R1

    @sum
    M=0        // sum = 0

(LOOP)
    @i
    D=M        // D = i
    @END
    D;JLE      // if i <= 0 goto END

    @R0
    D=M        // D = R0
    @sum
    M=D+M      // sum += R0

    @i
    M=M-1      // i -= 1

    @LOOP
    0;JMP      // goto LOOP

(END)
    @sum
    D=M
    @R2
    M=D        // R2 = sum

    @END
    0;JMP      // 死循环
```

**测试**：
1. 把上面汇编保存到 `asm/Mult.asm`
2. 用 P06 的汇编器（或官方汇编器）翻译成 `Mult.hack`
3. 在 CPUEmulator 里 `Load Program → Mult.hack`
4. 在 RAM 里设置 R0=3, R1=4
5. Run → 应得 R2=12

### 2.2 `Fill.hack`（键盘交互）

**功能**：
- 按下任意键 → 整个屏幕变黑
- 松开 → 整个屏幕变白

**思路**：
```
while True:
    if KBD != 0:
        把 SCREEN 到 SCREEN+8192 全部填 -1（全 1 = 黑）
    else:
        把 SCREEN 到 SCREEN+8192 全部填 0（白）
```

**关键技巧**：
- 屏幕字地址范围：`16384`（SCREEN）到 `24575`
- 一字 = 16 像素，全黑 = `0xFFFF` = `-1`
- 用循环索引 j 从 0 到 8191，写 `RAM[SCREEN + j]`

**留给你写**——提示：
1. 外层死循环
2. 读 `KBD`（地址 24576）
3. 内层循环 8192 次，每次写一个字

---

## 3. 常见坑

### 坑 1：Hack 不区分有符号/无符号

`@32768` 在 Hack 里会被解释为 `-32768`（补码）。
Hack 的 A 寄存器**同时**当地址（无符号）和数据（有符号），所以负数当地址时会从 RAM[32768] 开始读——
但 RAM 只有 16K，会越界。

### 坑 2：M 的别名容易混

```asm
@5
M = D          // RAM[5] = D
A = 10
M = D          // 这里的 M 是 RAM[10]！不是 RAM[5]
```

**记住**：每次 `A` 变，`M` 就变了。读 `M` 前必须先 `@addr`。

### 坑 3：跳转目标必须是 A 寄存器的值

```asm
@END
0;JMP          // 跳到 END 标号所在的 ROM 地址
```

跳转的本质是：把 A 寄存器的值写进 PC。

### 坑 4：循环变量初始化顺序

```asm
(LOOP)
    @R0
    D=M
    @R1
    M=D       // ❌ M 改了 A 就改不了 R0
    @R0
    ...
```

应该先用 `D` 暂存重要值，再 `@` 其他地址。

### 坑 5：Fill 程序性能

朴素实现：每次循环都查 8192 个字。
**优化**：只重写屏幕**改变的部分**——但 P04 不要求优化。

---

## 4. 与本项目其他模块的连接

### 4.1 与 [`Lab01_ISA与汇编`](../../Lab01_ISA与汇编/) 的对照

| 特性 | Hack（教学）| ARMv8-A（飞腾）|
|------|-------------|----------------|
| 寄存器数 | 2（A, D）+ M 别名 | 31 |
| 指令格式 | A（地址）+ C（计算）2 种 | 几十种编码格式 |
| 立即数范围 | 0–32767（A 指令）| 12 位 + 移位 / MOVZ+MOVK |
| 条件码 | zr/ng + 3 位 jump 码 | NZCV + 条件执行（`addeq`, `cbz`）|
| 内存访问 | M = RAM[A]（隐式）| LDR/STR + 寻址模式 |
| 调用约定 | 无（自己管栈）| AAPCS64（X0-X7 参数）|
| SIMD | 无 | NEON（128 位）|

→ **学完 Hack 汇编再看 ARM64，你会觉得 ARM64 寄存器多到奢侈，但 Hack 的"少而精"反而让你理解了寄存器到底在干什么**。

### 4.2 与 [`Capstone/cpu_simulator/assembler.py`](../../Capstone/cpu_simulator/assembler.py) 的连接

本项目 Capstone 有一个 **RV32I 汇编器**（Python），对应 P06 你要写的 Hack 汇编器。
做完 P06 后回头看 `assembler.py`，会发现 90% 的结构相同——只是 ISA 不同。

### 4.3 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

P04 让你**亲手摸到了 L3 ISA 层**——Hack 的 ISA 契约。
你现在用汇编写的程序，等 P05 造出 CPU 后就能跑——**这就是 ISA 作为"软硬件契约"的实操体验**。

---

## 5. 扩展挑战

1. **重写 `Mult.hack` 用 Booth 算法**（处理负数乘法）—— 难度跳跃
2. **手写 Hack 操作系统调用 `printf`**（用 RAM 模拟栈）
3. **`Fill` 加键盘码识别**：按 1 黑、按 2 白、按其他键灰色
4. **写一个 Hack 程序，把 RAM[0..99] 排序**（冒泡即可）

---

## 6. 检查清单

- [ ] 能默写 Hack 的 2 种指令格式
- [ ] 理解 M = RAM[A] 的别名机制
- [ ] 能在 30 分钟内手写 Mult.asm（不看答案）
- [ ] 理解 zr/ng 标志如何支持条件跳转
- [ ] 知道 KBD 和 SCREEN 的内存映射地址

---

## 📌 下一步

完成 P04 后，**Part I 的高潮来了**——[`Project_05_ComputerArchitecture/`](../Project_05_ComputerArchitecture/)。
你将用 P01-P03 造的所有部件（ALU + Register + RAM + PC）**拼出完整的 CPU**——
**Computer.hdl 跑通你的 Mult.hack 那一刻，是整个 Nand2Tetris 旅程最激动的瞬间**。
