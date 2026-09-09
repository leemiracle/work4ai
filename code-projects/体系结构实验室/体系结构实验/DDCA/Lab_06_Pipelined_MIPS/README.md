# Lab 06 — Pipelined MIPS：5 级流水线 + 冒险 + 前递

> **一句话目标**：把 L05 单周期 MIPS 改造成 **5 级流水线（IF/ID/EX/MEM/WB）**，
> 加上**数据冒险检测 + 转发单元 + Load-Use stall** + **分支预测初探**——
> **这是 DDCA 最难、最核心的 lab**。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch7 §7.5.3**（Pipelining）|
| 🎥 Mutlu | [Lecture 14-15: Pipelined MIPS](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 40–60 小时（DDCA 最难）|

---

## 1. 为什么要流水线？

### 1.1 单周期的瓶颈

单周期 MIPS 的时钟周期 = **最慢指令**（`lw`）的延迟 ≈ 8 ns。

```
单周期：每条指令 1 拍 = 8 ns
                  指令 1     指令 2     指令 3
                  ───────    ───────    ───────
时间：            0    8    8   16   16   24
IPC = 1，但每拍 8 ns → CPI × 时钟周期 = 8 ns/指令
```

### 1.2 流水线的解法

把指令分成 5 级，每级 1.6 ns，**重叠执行**：

```
流水线（5 级）：每条指令 5 拍 = 8 ns，但每拍 1.6 ns

指令 1：  IF | ID | EX | MEM | WB |
指令 2：     IF | ID | EX | MEM | WB |
指令 3：        IF | ID | EX | MEM | WB |
指令 4：           IF | ID | EX | MEM | WB |
指令 5：              IF | ID | EX | MEM | WB |
                ↓
          每拍完成 1 条（稳态），IPC = 1
          但每拍只 1.6 ns → CPI × 时钟周期 = 1.6 ns/指令（**5 倍加速**）
```

### 1.3 流水线的代价

- **引入冒险**（Hazard）：相邻指令之间可能冲突
- **增加硬件**：4 个流水线寄存器（IF/ID, ID/EX, EX/MEM, MEM/WB）
- **分支预测错误**代价：错误预测要刷流水线

---

## 2. 三种冒险

### 2.1 数据冒险（Data Hazard）

```mips
add  $t0, $t1, $t2   # 修改 $t0
sub  $t3, $t0, $t4   # 紧接着用 $t0  ← RAW 冒险！
```

**`sub` 的 ID 阶段读 `$t0`，但 `add` 还没写回**。

**解法 1：转发（Forwarding）**——
把 `add` 的 EX/MEM 阶段结果**直接转发**给 `sub` 的 EX 阶段，**不等 WB**。

**解法 2：插泡（Stall）**——
当 `add` 是 `lw`（Load-Use 冒险）时，必须插 1 拍。

### 2.2 控制冒险（Control Hazard）

```mips
beq  $t0, $zero, target   # 分支
add  $t1, $t2, $t3        # 紧接着，但可能不该执行
```

**分支结果在 EX/MEM 才出来，但 IF/ID 已经取了下一条**。

**解法 1：预测**（Predict）——预测分支是否跳转。
**解法 2：延迟分支**（Delay Slot）——MIPS 经典做法，分支后强制执行 1 条指令。
**解法 3：提前分支**（Early Branch）——把分支判定从 EX 移到 ID。

### 2.3 结构冒险（Structural Hazard）

如果 IF 和 MEM 同时访问同一存储器端口，会冲突。
**解法**：Harvard 架构（指令存储器和数据存储器分离）——MIPS 默认就这样。

---

## 3. 5 级流水线数据通路

```
   IF        ID          EX         MEM         WB
   ───       ───         ───        ───         ───
   PC      RegFile      ALU       D-Mem       RegFile
   IMem    Ctrl         Forward    (Write     (Write
   IF/ID   ID/EX        Unit      back)       back)
   Reg     Reg         _mux
```

### 3.1 流水线寄存器（4 个）

```verilog
module if_id_reg (
    input         clk, reset, stall, flush,
    input  [31:0] pc_plus_4_in, instr_in,
    output [31:0] pc_plus_4_out, instr_out
);
    reg [31:0] pc_plus_4, instr;

    always @(posedge clk, posedge reset)
        if (reset) begin
            pc_plus_4 <= 0;
            instr <= 0;   // NOP
        end else if (flush) begin
            instr <= 32'h00000000;   // NOP（清空流水线）
        end else if (!stall) begin
            pc_plus_4 <= pc_plus_4_in;
            instr <= instr_in;
        end

    assign pc_plus_4_out = pc_plus_4;
    assign instr_out = instr;
endmodule
```

**关键控制信号**：
- `stall`：保持原值（用于 Load-Use）
- `flush`：清为 NOP（用于分支预测错误）

### 3.2 转发单元（Forwarding Unit）

```verilog
module forwarding_unit (
    input  [4:0] id_ex_rs, id_ex_rt,
    input  [4:0] ex_mem_rd, mem_wb_rd,
    input        ex_mem_reg_write, mem_wb_reg_write,
    output [1:0] forward_a, forward_b
);
    // forward_a/b: 00 = regfile, 01 = mem_wb, 10 = ex_mem

    // EX/MEM hazard（最优先）
    always @(*) begin
        // Forward A (rs)
        if (ex_mem_reg_write && (ex_mem_rd != 0) && (ex_mem_rd == id_ex_rs))
            forward_a = 2'b10;
        else if (mem_wb_reg_write && (mem_wb_rd != 0) && (mem_wb_rd == id_ex_rs))
            forward_a = 2'b01;
        else
            forward_a = 2'b00;

        // Forward B (rt)
        if (ex_mem_reg_write && (ex_mem_rd != 0) && (ex_mem_rd == id_ex_rt))
            forward_b = 2'b10;
        else if (mem_wb_reg_write && (mem_wb_rd != 0) && (mem_wb_rd == id_ex_rt))
            forward_b = 2'b01;
        else
            forward_b = 2'b00;
    end
endmodule
```

**关键**：EX/MEM 优先于 MEM/WB（更新的数据优先）。

### 3.3 Load-Use 冒险检测

```verilog
module hazard_unit (
    input  [4:0] id_ex_rt,
    input  [4:0] if_id_rs, if_id_rt,
    input        id_ex_mem_read,   // 上一条是 lw 吗？
    output       stall_pc, stall_if_id, flush_id_ex,
    input        branch_taken      // 来自 EX（或 ID，如 early branch）
);
    // Load-Use 冒险检测
    wire load_use_hazard = id_ex_mem_read &&
                           ((id_ex_rt == if_id_rs) || (id_ex_rt == if_id_rt));

    assign stall_pc = load_use_hazard;
    assign stall_if_id = load_use_hazard;
    assign flush_id_ex = load_use_hazard | branch_taken;
endmodule
```

**关键**：
- 检测到 Load-Use：PC 和 IF/ID 不动，ID/EX 置 NOP
- 分支预测错误：刷 IF/ID 和 ID/EX

---

## 4. 测试用例（必须有冒险）

### 4.1 RAW 冒险（被 forwarding 解决）

```mips
add  $t0, $t1, $t2    # 修改 $t0
sub  $t3, $t0, $t4    # 立即用 $t0 → forwarding 解决
and  $t5, $t0, $t6    # 也用 $t0 → forwarding 解决
or   $t7, $t0, $t8    # 还用 $t0 → 从 MEM/WB 转发
```

### 4.2 Load-Use 冒险（必须 stall 1 拍）

```mips
lw   $t0, 0($sp)
add  $t1, $t0, $t2   # 必须等 lw 完成
```

→ 流水线会自动插 1 拍 NOP。

### 4.3 控制冒险

```mips
beq  $t0, $zero, label
add  $t1, $t2, $t3   # 分支不跳时执行；跳时不执行
label:
sub  $t4, $t5, $t6
```

→ 不带预测时，每次分支都 stall 1-3 拍。

---

## 5. 完整测试：跑一个冒泡排序

```mips
# bubble_sort.asm（MIPS）
.data
arr:    .word 5, 3, 8, 1, 9, 2, 7, 4, 6
.text
main:
    la   $t0, arr
    li   $t1, 9          # n = 9
    li   $t2, 0          # i = 0
outer:
    bge  $t2, $t1, end   # if i >= n, exit
    li   $t3, 0          # j = 0
    sub  $t4, $t1, $t2
    subi $t4, $t4, 1     # n - i - 1
inner:
    bge  $t3, $t4, outer_end
    # if arr[j] > arr[j+1], swap
    ...
```

→ 用 MARS 汇编，把 `.hex` 文件喂给你的 CPU，看 `arr` 是否被正确排序。

---

## 6. 常见坑

### 坑 1：转发 vs 写回优先级

EX/MEM 转发必须**优先于** MEM/WB 转发——
因为 EX/MEM 是更新的数据。

### 坑 2：忘记排除 `$zero`

```verilog
if (ex_mem_rd == id_ex_rs) forward_a = 2'b10;  // ❌ 没排除 $zero
```

→ 即使源是 `$zero`，也会触发转发，导致 `$zero` 被错误覆盖。
**必须加 `(ex_mem_rd != 0)` 条件**。

### 坑 3：Load-Use stall 时漏更新 PC

```verilog
// stall 时
pc <= pc + 4;   // ❌ PC 还是 +4 了，导致跳了一条指令
```

→ **stall 时 PC 必须保持不变**（重复当前指令）。

### 坑 4：分支预测错误时没刷流水线

```verilog
// 分支跳转
if (branch_taken) pc <= branch_target;
// 但没刷 IF/ID 和 ID/EX！
```

→ **必须 flush**，否则错误的指令会继续走流水线。

### 坑 5：MEM 阶段没把 `lw` 数据送到 WB

`lw` 指令在 MEM 阶段读数据存储器，必须把读出值**通过 MEM/WB 寄存器**送到 WB。

### 坑 6：jal/jr 没特殊处理

`jal` 要在 EX 阶段算 PC+8 写到 `$ra`（不是 PC+4，因为下一条已经 IF）。
`jr` 要把 `$ra` 值送给 PC（通过 forwarding 也能解决）。

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`Lab02_流水线与ILP`](../../Lab02_流水线与ILP/) 的连接

学完 L06 后看飞腾真机的流水线：

| 方面 | L06 流水线 MIPS（5 级）| 飞腾 D3000M（15+ 级）|
|------|------------------------|----------------------|
| 流水级 | IF/ID/EX/MEM/WB | 取指/译码/重命名/Issue/EX/Load/Store/Commit |
| Issue | 顺序 1 wide | 顺序 → 乱序 → 顺序提交（4 wide）|
| 分支预测 | 简单 predict-not-taken | TAGE + RAS + BTB |
| Cache | 无（直接访问 imem/dmem）| L1+L2+L3 三层 |
| 寄存器堆 | 32 个 ISA | 32 ISA → 几百个 PRF（重命名）|
| Forwarding | EX→EX, MEM→EX | 多源、多目的、跨级 |

→ **L06 是飞腾流水线的"教学简化版"**——核心思想（流水线 + 冒险 + 前递）完全一样。

### 7.2 与 [`Lab04_超标量乱序`](../../Lab04_超标量乱序/) 的连接

L06 是**顺序执行**（in-order）——指令按程序顺序进流水线。
飞腾是**乱序执行**（out-of-order）——指令可以按数据就绪顺序执行。

OoO 在 L06 基础上加了：
- 寄存器重命名（消除假依赖）→ [`Lab04 §3.1`](../../Lab04_超标量乱序/)
- Issue Queue（按数据就绪等待）→ [`Lab04 §2.2`](../../Lab04_超标量乱序/)
- ROB（按程序顺序提交）→ [`Lab04 §3.2`](../../Lab04_超标量乱序/)

### 7.3 与 [`Expert_03_HW_Designer/rtl/forwarding_unit.v`](../../Expert_03_HW_Designer/rtl/) 的对照

直接打开本项目已有的 `forwarding_unit.v`：

```verilog
// Expert_03 的 forwarding unit（RV32I 版本）
module forwarding_unit (
    input  [4:0] ex_mem_rd,
    input  [4:0] mem_wb_rd,
    ...
);
```

→ 与 L06 的 forwarding unit **几乎完全相同**！只是 ISA 不同（MIPS vs RV32I）。

学完 L06，直接读懂 Expert_03 的所有 Verilog。

### 7.4 与 [`Capstone/cpu_simulator/rv32i_sim.py`](../../Capstone/cpu_simulator/) 的对照

Capstone 是 **5 级流水线 RV32I 的 Python 模拟**——
与 L06 是同一种思想（流水线 + 冒险 + 前递），只是用 Python 实现。

→ **做完 L06 再做 Capstone**：硬件直觉 + 软件模型，互相验证。

### 7.5 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

L06 让你彻底搞清 **L2 微架构** 的核心：**流水线 + 冒险 + 前递**。
所有现代 CPU（飞腾、Apple Silicon、AMD Zen、Intel Core）的微架构都建立在 L06 的概念之上。

---

## 8. 扩展挑战

1. **Early Branch**：把分支判定从 EX 移到 ID（缩短分支惩罚）
2. **Branch Target Buffer (BTB)**：缓存上次分支目标，提前取出
3. **2-bit 分支预测器**：参考 [`Expert_03/rtl/two_bit_predictor.v`](../../Expert_03_HW_Designer/rtl/)
4. **Delay Slot 优化**：让汇编器自动把有用指令插入 delay slot
5. **更深的流水线**：从 5 级扩到 7/10/15 级，看 IPC 变化（参考飞腾）
6. **超标量（2-wide）**：每周期发射 2 条指令——这等于跨入 [`Lab04`](../../Lab04_超标量乱序/) 范围

---

## 9. 检查清单

- [ ] 单周期 L05 的所有 30+ 指令在流水线版本里仍然正确
- [ ] RAW 冒险被 forwarding 正确解决
- [ ] Load-Use 冒险被 stall 1 拍解决
- [ ] 分支预测错误时正确 flush 流水线
- [ ] 用冒泡排序程序测试整个流水线
- [ ] 在波形里看到 5 条指令**重叠执行**

---

## 📌 下一步

🎉🎉 **完成后，你已具备完整的 CPU 微架构工程能力**。

- 进 [`Lab_07_Memory_IO/`](../Lab_07_Memory_IO/) 加 Cache
- 进 [`Lab_08_Exceptions/`](../Lab_08_Exceptions/) 加异常处理
- 进 [`Lab_09_Capstone_FPGA/`](../Lab_09_Capstone_FPGA/) 烧到 FPGA

或者**回到本项目 Lab**：
- [`Lab02`](../../Lab02_流水线与ILP/) 实测飞腾流水线 IPC
- [`Lab04`](../../Lab04_超标量乱序/) 学 OoO（L06 的下一步）
- [`Lab03`](../../Lab03_存储层次/) 学 Cache（L07 的下一步）

→ **现在你已经懂"硬件如何工作"**，可以开始**用 perf 观测真实工业硬件**了。
