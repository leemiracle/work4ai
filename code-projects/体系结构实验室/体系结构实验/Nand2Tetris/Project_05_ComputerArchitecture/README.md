# Project 05 — Computer Architecture：从部件到完整的 CPU

> **一句话目标**：把 P01-P03 的所有部件拼在一起，造出 **CPU.hdl → Memory.hdl → Computer.hdl**——
> 一台能读 ROM、跑 Hack 程序的完整计算机。**这是 Part I 的高潮**。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | *Elements* 2nd ed. **Ch5**（Computer Architecture）|
| 🎥 Coursera | [Unit 5.1-5.5](https://www.coursera.org/learn/build-a-computer) |
| 🛠 工具 | **HardwareSimulator**（带 Computer 模式）|
| ⏱ 预计工时 | 8–15 小时（最难的硬件 project）|

---

## 1. 你将构建的 3 个芯片

| # | 芯片 | 内容 |
|---|------|------|
| 1 | **`CPU.hdl`** | Hack CPU 的完整实现（最复杂）|
| 2 | `Memory.hdl` | RAM16K + SCREEN + KBD 合并 |
| 3 | `Computer.hdl`** | CPU + ROM32K + Memory = 完整计算机 |

---

## 2. Hack CPU 的整体结构

```
       inM[16]  ────────┐
                       ↓
                  ┌─────────────┐
                  │   ALU       │←── y = M 或 A
   instruction    │             │←── x = D
        ↓         └─────┬───────┘
  ┌──────────┐          │
  │ Control  │── c-bits │
  │ (Decode) │          ↓
  │          │←──── outM[16]
  │          │          │
  │          │          ↓ writeM, addressM[15]
  │          │      ┌───────┐
  │          │      │ Memory│
  │          │      └───────┘
  │          │
  │          │←──── ALU 的 zr/ng（条件跳转）
  │          │
  └────┬─────┘
       │
       └──→ PC（pc[15], reset, load, inc）
            ↑
            └── jump 信号决定 PC 是否跳转
```

### 2.1 输入输出

```hdl
CHIP CPU {
    PARTS:
    // 输入
    IN  inM[16],           // 从内存读到的数据（M）
        instruction[16],   // 从 ROM 读到的指令
        reset;             // 重启信号

    // 输出
    OUT outM[16],          // 要写入内存的数据
        writeM,            // 是否写内存
        addressM[15],      // 内存地址（A 寄存器低 15 位）
        pc[15];            // 程序计数器
}
```

### 2.2 指令解码

`instruction[15]` 决定指令类型：
- `0`：A 指令，把 `instruction[0..14]` 装入 A 寄存器
- `1`：C 指令，按 `instruction[0..14]` 进一步解码为 `a cccccc ddd jjj`

### 2.3 写回逻辑

- A 指令：总是写 A 寄存器
- C 指令：按 `ddd` 决定写 A / D / M
  - `d1`：A 寄存器 ← ALU out
  - `d2`：D 寄存器 ← ALU out
  - `d3`：内存（M）← ALU out（即 `writeM = 1`）

### 2.4 跳转逻辑

`jump = jjj ≠ 000` 且 ALU 输出满足条件：
- `j1`（JGT）：`~ng & ~zr`
- `j2`（JEQ）：`zr`
- `j3`（JLT）：`ng`

跳转时把 A 寄存器的值装入 PC。

### 2.5 ALU 输入选择

```
ALU.x = D（始终）
ALU.y = ? 由 instruction[12]（a 位）决定
       a=0 → A 寄存器
       a=1 → M（inM）
```

---

## 3. 骨架代码

### 3.1 `CPU.hdl`（核心骨架）

> 这是 Part I 最难的芯片。我们给完整骨架，关键逻辑留空。

```hdl
CHIP CPU {
    IN  inM[16], instruction[16], reset;
    OUT outM[16], writeM, addressM[15], pc[15];
    PARTS:
    // ---- 1. 解码指令类型 ----
    Not(in=instruction[15], out=isAInstr);   // isAInstr=1 表示 A 指令
    // 对于 C 指令，提取控制位
    // a = instruction[12]
    // c1..c6 = instruction[6..11]
    // d1 = instruction[5] (写 A)
    // d2 = instruction[4] (写 D)
    // d3 = instruction[3] (写 M)
    // j1 = instruction[2] (JGT)
    // j2 = instruction[1] (JEQ)
    // j3 = instruction[0] (JLT)

    // ---- 2. A 寄存器的写入控制 ----
    // A 指令：load = 1
    // C 指令：load = (d1) （a 位决定 ALU 输出是否写入 A）
    // → AReg.load = isAInstr OR (cInstr AND d1)
    And(a=instruction[15], b=instruction[5], out=d1C);
    Or(a=isAInstr, b=d1C, out=aLoad);

    // ---- 3. A 寄存器的输入 ----
    // A 指令：直接来自 instruction[0..14]
    // C 指令（d1=1）：来自 ALU 输出
    // → AReg.in = Mux(isAInstr, instruction[0..14], aluOut)
    Mux16(a=aluOut, b=instruction, sel=isAInstr, out=aIn);
    ARegister(in=aIn, load=aLoad, out=aOut);

    // ---- 4. D 寄存器 ----
    And(a=instruction[15], b=instruction[4], out=dLoad);
    DRegister(in=aluOut, load=dLoad, out=dOut);

    // ---- 5. ALU 的 y 输入 ----
    Mux16(a=aOut, b=inM, sel=instruction[12], out=aluY);

    // ---- 6. ALU ----
    ALU(x=dOut, y=aluY,
        zx=instruction[11], nx=instruction[10],
        zy=instruction[9],  ny=instruction[8],
        f=instruction[7],   no=instruction[6],
        out=aluOut, zr=zr, ng=ng);

    // ---- 7. 写内存 ----
    And(a=instruction[15], b=instruction[3], out=writeM);

    // ---- 8. 跳转逻辑 ----
    // 三个条件
    And(a=~ng, b=~zr, out=gtCond);          // > 0
    // eqCond = zr                            // == 0
    // ltCond = ng                            // < 0

    // 与 jjj 对应位 AND
    // j1&JGT, j2&JEQ, j3&JLT，再 OR
    And(a=instruction[15], b=instruction[2], out=j1);
    And(a=j1, b=gtCond, out=j1Cond);

    And(a=instruction[15], b=instruction[1], out=j2);
    And(a=j2, b=zr, out=j2Cond);

    And(a=instruction[15], b=instruction[0], out=j3);
    And(a=j3, b=ng, out=j3Cond);

    Or(a=j1Cond, b=j2Cond, out=j12);
    Or(a=j12, b=j3Cond, out=jump);

    // ---- 9. PC ----
    PC(in=aOut, reset=reset, load=jump, inc=true, out[0..14]=pc);

    // ---- 10. 输出 ----
    Or16(a=aluOut, b=false, out=outM);
    Or(a=false, b=aOut[0..14], out=addressM);    // 简化示意
}
```

> ⚠️ 上面的 HDL 是**思路骨架**，不保证语法严格正确。**真正的练习是把它改对、跑通**。
> 提示：用 `Or16Way`、`Mux16` 等多位操作时要小心位宽匹配。

### 3.2 `Memory.hdl`

```hdl
CHIP Memory {
    IN in[16], load, address[15];
    OUT out[16];
    PARTS:
    // 内存映射：
    //   0–16383     → RAM16K
    //   16384–24575 → SCREEN
    //   24576       → KBD

    // 用 address[13] 和 address[14] 区分
    // address[13]=0, address[14]=0 → RAM
    // address[13]=1, address[14]=0 → SCREEN
    // address[13]=0, address[14]=1 → KBD

    // ... 你需要用 DMux4Way + Mux4Way16 搭 ...
}
```

### 3.3 `Computer.hdl`

```hdl
CHIP Computer {
    IN reset;
    PARTS:
    ROM32K(address=pc, out=instruction);
    CPU(inM=memOut, instruction=instruction, reset=reset,
        outM=cpuOut, writeM=writeM, addressM=addr, pc=pc);
    Memory(in=cpuOut, load=writeM, address=addr, out=memOut);
}
```

**这一行你写完，Computer.hdl 就跑起来了**——一台完整的、自造的计算机。

---

## 4. 测试

### 4.1 用官方测试 ROM

nand2tetris 提供 3 个测试程序：

| 测试 | 文件 | 验证什么 |
|------|------|---------|
| `Add.hack` | 加法 | ALU + 内存写回 |
| `Max.hack` | 求最大值 | 条件跳转 |
| `Rect.hack` | 画矩形 | 屏幕映射 |

### 4.2 跑你 P04 写的程序！

```bash
# 在 HardwareSimulator 里：
# 1. Load CHIP: Computer.hdl
# 2. Load ROM: Mult.hack （你 P04 写的）
# 3. 设置 RAM[0]=3, RAM[1]=4
# 4. Run → 应得 RAM[2]=12
```

**这一刻你会真切感受到"我用 Nand 造了一台能跑我程序的计算机"**——Nand2Tetris 的精神高潮。

---

## 5. 常见坑

### 坑 1：A 寄存器在 C 指令时也可能被写

C 指令 `AMD = D + M` 会同时写 A、D、M。
如果你把 A 写回条件简化为"只在 A 指令时写"，会丢失这种 C 指令的语义。

### 坑 2：addressM 是 15 位

ROM32K 和 RAM16K 都是 15 位地址（32K = 2^15）。从 A 寄存器取低 15 位送出。

### 坑 3：jump 信号是组合逻辑

jump 的判断**不依赖时钟**，必须在 C 指令的同一周期内决定 PC 是否跳转。
不要把 jump 接到时序芯片的 load 上。

### 坑 4：reset 的全局影响

reset 信号只接 PC，不接 A/D 寄存器。
**Hack CPU 上电后 A/D 是未定义的**，必须由程序自己初始化。

### 坑 5：Memory 的 KBD 处理

KBD 是**只读单字**，写它没意义。要在 Memory.hdl 里**忽略对 KBD 的写**。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Capstone/cpu_simulator/rv32i_sim.py`](../../Capstone/cpu_simulator/) 的对照

| 方面 | Hack CPU（教学）| RV32I 5 级流水线（Capstone）|
|------|----------------|-----------------------------|
| 设计风格 | 单周期 | 5 级流水（IF/ID/EX/MA/WB）|
| 时钟 | 一个周期完成一条指令 | 一个周期完成 5 条指令的不同阶段 |
| 性能 | IPC = 1（理想）| IPC ≈ 5（理想）/ IPC ≈ 1–2（实际）|
| 冒险 | 无（每条独立）| 数据冒险 + 控制冒险 + 结构冒险 |
| 旁路 | 不需要 | 必须有 EX→EX, MEM→EX, WB→EX |
| 分支预测 | 无（PC 静态）| 必须有，否则 IPC 暴跌 |
| 寄存器 | 2 个（A, D）| 31 个 + 重命名（[`Lab04`](../../Lab04_超标量乱序/)）|

→ **Hack CPU 让你懂 CPU 是什么，RV32I 让你懂 CPU 怎么变快，飞腾真机让你懂 CPU 怎么变得更快**。

### 6.2 与 [`Lab02_流水线与ILP`](../../Lab02_流水线与ILP/) 的连接

Hack CPU 是**单周期**——每条指令 1 拍完成。
工业 CPU 是**多级流水线**——每条指令拆成 5–20 拍，但每拍都在跑一条。

Lab02 用 perf 实测飞腾的 IPC，对比单周期（Hack）和流水线（飞腾）的差距。

### 6.3 与 [`Expert_03_HW_Designer/rtl/forwarding_unit.v`](../../Expert_03_HW_Designer/rtl/) 的连接

`forwarding_unit.v` 实现了**流水线前递**（forwarding）——
Hack CPU 不需要这个，因为它是单周期；但任何流水线 CPU 都必须有。

### 6.4 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

完成 P05 后，你已经造出了完整的 **L2 微架构 + L3 ISA**。
**L2 微架构**：你的 CPU.hdl 实现就是 Hack 的微架构
**L3 ISA**：Hack ISA 是 P04 学的，由你的 CPU 实现

→ 你现在可以**完整回答**：从硬件到 ISA 是怎么连起来的。

---

## 7. 扩展挑战

1. **加流水线**：把 CPU.hdl 改成 5 级流水线（IF/ID/EX/MA/WB）+ 前递 + 分支预测——这是 Capstone 的 RV32I 工作量
2. **加中断**：在 Hack ISA 上加 `INT` 指令和异常处理表（参考 RV32I 的 `mtvec`）
3. **加虚拟内存**：把 32K ROM 扩展为 16M 虚拟地址空间，加页表 + TLB——参考 [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/)
4. **加超标量**：让 Hack CPU 每周期发射 2 条指令——参考 [`Lab04`](../../Lab04_超标量乱序/)
5. **画出 CPU 的状态转移图**：每个状态对应一个时钟周期，用 LaTeX 或 draw.io

---

## 8. 检查清单

- [ ] 能默画 Hack CPU 的整体框图
- [ ] 理解指令解码（A 指令 vs C 指令的控制信号生成）
- [ ] 知道 writeM、addressM、pc 三个输出怎么来的
- [ ] 能解释 jump 条件（zr/ng → JGT/JEQ/JLT）的逻辑
- [ ] **Computer.hdl 跑通你的 Mult.hack**（最关键的检查！）
- [ ] 跑通 3 个官方测试（Add/Max/Rect）

---

## 📌 下一步

🎉 **恭喜你完成 Nand2Tetris Part I！**

你现在拥有一台**完整的、从 Nand 拼出来的、能跑 Hack 程序的计算机**。
这是 99% 程序员一辈子都没有的成就。

**Part II 开始**——从硬件转向软件：
- [`Project_06_Assembler/`](../Project_06_Assembler/)：写一个汇编器（Python/Java），把 `.asm` 翻译成 `.hack`
- [`Project_07-08`](../Project_07_VMTranslator_I/)：实现栈式 VM 翻译器
- [`Project_09`](../Project_09_HighLevelLanguage/)：用 Jack 写一个 App
- [`Project_10-11`](../Project_10_Compiler_I/)：写 Jack 编译器
- [`Project_12`](../Project_12_OS/)：用 Jack 写一个 OS

**也可以选择暂停 Nand2Tetris，回到本项目做 Lab**——
你刚学完"单周期 CPU"，正好可以进 [`Lab02`](../../Lab02_流水线与ILP/) 学"流水线 CPU"，对照鲜明。
