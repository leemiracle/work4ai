# Project 03 — Sequential Logic：从组合电路到带状态的时序电路

> **一句话目标**：引入**时钟**和**状态**，搭出 **DFF → Bit → Register → RAM8/64/512/4K/16K → PC**——
> **没有时序，计算机无法存储任何东西**。这一关之后你才能造出"内存"。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch3**（Sequential Logic）|
| 🎥 Coursera | [Unit 3.1-3.5](https://www.coursera.org/learn/build-a-computer) |
| 🛠 工具 | **HardwareSimulator**（支持 `clocked` 芯片）|
| ⏱ 预计工时 | 8–12 小时 |

---

## 1. 你将构建的 11 个芯片

| # | 芯片 | 功能 | 是否时序 |
|---|------|------|---------|
| 1 | `Bit` | 1 位寄存器 | ⏱ |
| 2 | `Register` | 16 位寄存器 | ⏱ |
| 3 | `PC` | 16 位程序计数器 | ⏱ |
| 4 | `RAM8` | 8 字 × 16 位 | ⏱ |
| 5 | `RAM64` | 64 字 | ⏱ |
| 6 | `RAM512` | 512 字 | ⏱ |
| 7 | `RAM4K` | 4K 字 | ⏱ |
| 8 | `RAM16K` | 16K 字 | ⏱ |
| 9 | `ROM32K` | 32K 字（指令存储器，只读）| ⏱ |
| 10 | `ARegister` | A 寄存器（Hack 用）| ⏱ |
| 11 | `DRegister` | D 寄存器（Hack 用）| ⏱ |

> 💡 **Nand2Tetris 把 DFF（Data Flip-Flop）作为内置原语**，相当于组合电路里的 Nand。
> 你不需要自己用 Nand 搭 DFF（工业上 DFF 也是用 Nand/Nor + 反馈搭的，但教学上跳过）。

---

## 2. 关键概念

### 2.1 组合电路 vs 时序电路

| 类型 | 输出依赖 | 有无状态 | 例子 |
|------|---------|---------|------|
| **组合**（P01-P02）| 仅当前输入 | 无 | And, ALU |
| **时序**（P03）| 当前输入 + **历史状态** | 有 | Register, RAM, PC |

### 2.2 时钟

```
       ┌──────┐      ┌──────┐      ┌──────┐
tick ──┘      └──────┘      └──────┘      └──
       ↑                ↑                ↑
       状态在上升沿更新   状态在上升沿更新
```

- 所有时序芯片**同步**于同一个时钟
- **在上升沿**：芯片把 `input` 锁存到 `state`
- **在两次上升沿之间**：芯片输出**当前 state**（不变）

### 2.3 DFF（Data Flip-Flop）

DFF 是时序电路的**原语**（类似 Nand 在组合电路）：

```hdl
CHIP DFF {
    IN  in;
    OUT out;
    // 语义：out(t) = in(t-1)
    // 即输出 = 上一拍的输入
}
```

→ DFF 是"延迟一拍"的元件。所有时序电路都是基于 DFF 搭的。

### 2.4 1 位寄存器（Bit）的实现

```hdl
CHIP Bit {
    IN  in, load;     // load=1 时下一拍存入 in
    OUT out;
    PARTS:
    Mux(a=outDFF, b=in, sel=load, out=muxOut);
    DFF(in=muxOut, out=outDFF);
    // 此时 out 应该 = outDFF，需要把内部 wire 暴露出来
}
```

**关键思想**：当 `load=0`，DFF 的 in 来自自己的 out（保持状态）；
当 `load=1`，DFF 的 in 来自外部 in（更新状态）。

### 2.5 RAM 的本质：寄存器阵列 + 解码器

```
RAM8 的结构：
              地址 addr[0..2]
                   │
              ┌────┴────┐
              │ DMux8Way │       ← 把 load 信号"分配"到选中的那个 Register
              └────┬────┘
                   │
       ┌───┬───┬───┬───┬───┬───┬───┬───┐
       │ R │ R │ R │ R │ R │ R │ R │ R │  ← 8 个 Register
       └─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┘
         │   │   │   │   │   │   │   │
         └───┴───┴───┴───┴───┴───┴───┴───┐
              Mux8Way16  ←─ 把选中的 Register 的输出送出去
                   │
                  out
```

### 2.6 PC（程序计数器）

Hack 的 PC 有 3 个控制信号：

| 信号 | 含义 |
|------|------|
| `reset` | 强制下一拍 = 0（重启）|
| `load`  | 下一拍 = in（跳转）|
| `inc`   | 下一拍 = 当前 + 1（默认）|

**优先级**：`reset > load > inc`。

---

## 3. 骨架代码

### 3.1 `Bit.hdl`

```hdl
CHIP Bit {
    IN in, load;
    OUT out;
    PARTS:
    Mux(a=dffOut, b=in, sel=load, out=dffIn);
    DFF(in=dffIn, out=dffOut);
    Or(a=false, b=dffOut, out=out);    // 让 out 出现在输出端口
}
```

> 💡 `Or(a=false, b=dffOut, out=out)` 是一种技巧，因为 HDL 不允许内部 wire 直接绑到端口。
> 也可以用 `Mux(a=dffOut, b=false, sel=true, out=out)` 等。

### 3.2 `Register.hdl`

```hdl
CHIP Register {
    IN in[16], load;
    OUT out[16];
    PARTS:
    Bit(in=in[0],  load=load, out=out[0]);
    Bit(in=in[1],  load=load, out=out[1]);
    // ... 重复 16 次 ...
    Bit(in=in[15], load=load, out=out[15]);
}
```

### 3.3 `RAM8.hdl`（8 字存储）

```hdl
CHIP RAM8 {
    IN in[16], addr[3], load;
    OUT out[16];
    PARTS:
    DMux8Way(in=load, sel=addr,
             a=l0, b=l1, c=l2, d=l3,
             e=l4, f=l5, g=l6, h=l7);

    Register(in=in, load=l0, out=o0);
    Register(in=in, load=l1, out=o1);
    Register(in=in, load=l2, out=o2);
    Register(in=in, load=l3, out=o3);
    Register(in=in, load=l4, out=o4);
    Register(in=in, load=l5, out=o5);
    Register(in=in, load=l6, out=o6);
    Register(in=in, load=l7, out=o7);

    Mux8Way16(a=o0, b=o1, c=o2, d=o3,
              e=o4, f=o5, g=o6, h=o7,
              sel=addr, out=out);
}
```

### 3.4 RAM64 / RAM512 / RAM4K / RAM16K

**关键模式**：用上一级 RAM 搭下一级。

```
RAM64   = 8 × RAM8    + DMux8Way + Mux8Way16
RAM512  = 8 × RAM64   + DMux8Way + Mux8Way16
RAM4K   = 8 × RAM512  + DMux8Way + Mux8Way16
RAM16K  = 4 × RAM4K   + DMux4Way + Mux4Way16    ← 注意是 4 不是 8
```

### 3.5 `PC.hdl`

```hdl
CHIP PC {
    IN in[16], reset, load, inc;
    OUT out[16];
    PARTS:
    // 1. 当前值 +1
    Inc16(in=regOut, out=incOut);

    // 2. 选择下一拍：reset > load > inc
    Mux16(a=incOut, b=in,     sel=load,  out=loadOrInc);
    Mux16(a=loadOrInc, b=false, sel=reset, out=falseOrOther);  // false 即 0
    // 注：上面这行应该是 Mux16(a=loadOrInc, b=0, sel=reset)，但 HDL 需要 b[0..15]=false

    // 3. 写入 Register
    Register(in=nextState, load=true, out=regOut);

    // 4. 输出
    Or16(a=false, b=regOut, out=out);
}
```

> ⚠️ 上面的 `nextState` 需要**自己想清楚怎么连**——这是 PC 设计的核心练习。

---

## 4. 测试

时序芯片的测试比组合芯片**多了 `tick` / `tock` 指令**：

```tst
// RAM8.tst 片段
load RAM8.hdl,
output-list addr in load out;

set addr %B000, set in 10, set load 1, tick, tock, output;   // 写 addr=0
set addr %B001, set in 20, set load 1, tick, tock, output;   // 写 addr=1
set addr %B000, set load 0, tick, tock, output;              // 读 addr=0 应为 10
```

**`tick` + `tock` 一起组成一个完整时钟周期**。在 `tick` 末尾锁存数据。

---

## 5. 常见坑

### 坑 1：忘了 `tick`/`tock`

时序芯片的状态**只在 `tock` 时更新**。如果只 set 不 tick，写不进去。

### 坑 2：DFF 不能"自己写"

```hdl
// ❌ 错：想自己搭 DFF
CHIP DFF { ... }    // DFF 是内置的，不能重写
```

### 坑 3：RAM 多路复用搞反了

写时用 `DMux`（把 load 分发到选中的 Register）；
读时用 `Mux`（把选中的 Register 的输出送出）。

**容易把这两个搞反**——记住：DMux 是"分发"，Mux 是"汇集"。

### 坑 4：PC 的优先级

PC 的优先级是 `reset > load > inc`。如果你用单层 Mux，会得到错误的逻辑。
**正确做法**：用两级 Mux，先 `inc vs load`，再 `result vs reset`。

### 坑 5：16 位 Register 一次性写

```hdl
// ❌ 错：试图用 1 个 Bit 存 16 位
Bit(in=in, load=load, out=out);

// ✅ 对：必须 16 个 Bit
Bit(in=in[0], load=load, out=out[0]);
... 16 次 ...
```

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Lab03_存储层次`](../../Lab03_存储层次/) 的连接

读完 P03 后看本项目 Lab03 的实测数据：

| 存储层级 | Hack（教学）| 飞腾 D3000M（`[实测]`）|
|---------|-------------|------------------------|
| Register（最接近 ALU）| 1 个 DRegister + 1 个 ARegister | 31 个通用 + 31 个浮点 + 系统寄存器（重命名后是 PRF）|
| L1 D-Cache | — | **64 KB / 4-way @ 1.61 ns** |
| L2 Cache | — | **512 KB / 8-way @ 4.78 ns** |
| L3 Cache | — | **8 MB shared @ 14 ns** |
| 主存（RAM） | **16K × 16 位 = 32 KB**（合并） | **DRAM @ 130 ns** |

→ **Hack 的 RAM 是单层结构**，飞腾是**多层缓存金字塔**。
P03 让你理解"什么是 RAM"，Lab03 让你理解"为什么真实 RAM 必须配 Cache"。

### 6.2 与 [`Lab04_超标量乱序`](../../Lab04_超标量乱序/) 的连接

Hack 的 PC 是**单值**寄存器；飞腾的 PC 后面有**复杂的分支预测器 + ROB**——
预测错误的指令会被刷掉，PC 被恢复到正确位置。这些都是 P03 的 PC 之上叠加的微架构层。

### 6.3 与 [`背景知识/Great_Ideas`](../../背景知识/Great_Ideas_体系结构思想.md) 的连接

- **Great Idea #6：Memory Hierarchy（存储层次）** ← P03 是这条思想的起点

---

## 7. 扩展挑战

1. **用 DFF + Nand 自己搭 DFF**（不使用内置原语）—— 这是研究生级任务
2. **双端口 RAM**：同时支持两个读写请求（Hack 不要求，工业 GPU 必需）
3. **Cache 模拟**：用 Python 模拟一个 4-way Set-Associative L1 Cache（[`Lab03`](../../Lab03_存储层次/) 的逆向练习）
4. **SDRAM 控制器**：阅读 *Harris & Harris* §5.8，理解真实 DRAM 的刷新机制

---

## 8. 检查清单

- [ ] 能解释"组合电路 vs 时序电路"的区别
- [ ] 理解 DFF 的语义 `out(t) = in(t-1)`
- [ ] 能在 1 小时内搭出 Register.hdl（不看答案）
- [ ] 理解 `tick` / `tock` 测试语义
- [ ] 知道 RAM 是"Register 阵列 + 地址译码器"
- [ ] 理解 PC 的 reset/load/inc 优先级
- [ ] 全部 11 个芯片测试通过

---

## 📌 下一步

完成 P03 后，**Pause 一下，做 P04**（写 Hack 汇编）——
因为 P05（Computer.hdl）会用到你对 Hack ISA 的理解，先用 P04 建立汇编直觉。

P04 比 P01-P03 都简单，但**学懂它你才能造出"可编程的"CPU**。
