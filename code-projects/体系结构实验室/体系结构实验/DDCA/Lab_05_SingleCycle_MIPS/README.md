# Lab 05 — Single-Cycle MIPS：用 Verilog 拼出一台完整 CPU

> **一句话目标**：用 L01-L04 的所有部件（ALU + RegFile + PC + Memory）**拼出一台完整的单周期 MIPS CPU**——
> 能跑真实的 MIPS 程序。**这是 DDCA 的第一个高潮**。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch6**（MIPS ISA）+ **Ch7 §7.1-7.4**（单周期微架构）|
| 🎥 Mutlu | [Lecture 11-13: MIPS ISA + Single-Cycle](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 30–50 小时（DDCA 最重要的 lab）|

---

## 1. MIPS ISA 速览

### 1.1 MIPS 的 3 种指令格式

```
R-type:  op(6)  rs(5)  rt(5)  rd(5)  shamt(5)  funct(6)
I-type:  op(6)  rs(5)  rt(5)  imm(16)
J-type:  op(6)  addr(26)
```

- **R-type**：寄存器操作（add, sub, and, or, slt, jr...）
- **I-type**：立即数 / 访存 / 条件分支（addi, lw, sw, beq, bne...）
- **J-type**：无条件跳转（j, jal）

### 1.2 必须实现的 ~30 条指令

| 类型 | 指令 | 二进制 op/funct |
|------|------|----------------|
| **R-type 算术** | `add, addu, sub, subu` | op=0, funct=0x20/21/22/23 |
| **R-type 逻辑** | `and, or, xor, nor` | funct=0x24/25/26/27 |
| **R-type 移位** | `sll, srl, sra` | funct=0x00/02/03 |
| **R-type 比较** | `slt, sltu` | funct=0x2a/2b |
| **R-type 跳转** | `jr, jalr` | funct=0x08/09 |
| **I-type 算术** | `addi, addiu, andi, ori, xori` | op=0x08/09/0c/0d/0e |
| **I-type 访存** | `lw, sw, lb, sb, lh, sh` | op=0x23/2b/20/28/21/29 |
| **I-type 立即数** | `lui`（load upper imm）| op=0x0f |
| **I-type 分支** | `beq, bne` | op=0x04/05 |
| **J-type 跳转** | `j, jal` | op=0x02/03 |

### 1.3 寄存器约定

| 寄存器 | 名字 | 用途 |
|--------|------|------|
| 0 | `$zero` | 永远 0 |
| 1 | `$at` | assembler temporary |
| 2-3 | `$v0, $v1` | 函数返回值 |
| 4-7 | `$a0-$a3` | 函数参数 |
| 8-15 | `$t0-$t7` | 临时 |
| 16-23 | `$s0-$s7` | saved（callee 保存）|
| 24-25 | `$t8-$t9` | 临时 |
| 26-27 | `$k0-$k1` | kernel 用 |
| 28 | `$gp` | global pointer |
| 29 | `$sp` | stack pointer |
| 30 | `$fp` | frame pointer |
| 31 | `$ra` | return address |

---

## 2. 单周期 MIPS 数据通路

```
                    ┌──────────────────┐
                    │   Control Unit   │
                    │ (combinational)  │
                    └────────┬─────────┘
                             │ control signals
                             ▼
   ┌────────┐  ┌─────────┐  ┌─────┐  ┌────────┐
   │  PC    │─►│Instruct.│─►│ Reg │─►│  ALU   │─►┐
   │ (+4 or │  │ Memory  │  │File │  │        │  │
   │ branch)│  └─────────┘  └─────┘  └────────┘  │
   └────────┘                    ▲              │
        ▲                        │              ▼
        │                        │       ┌──────────┐
        └────────────────────────┴──────►│Data Memory│◄─┐
                                              └──┬───┘   │
                                                 │       │
                                                 └──write-back──┘
```

### 2.1 关键控制信号

| 信号 | 位数 | 含义 |
|------|------|------|
| `RegWrite` | 1 | 是否写寄存器堆 |
| `RegDst` | 1 | 写地址：rt（I-type） vs rd（R-type）|
| `ALUSrc` | 1 | ALU 第二源：寄存器（R）vs 立即数（I）|
| `MemWrite` | 1 | 是否写数据存储器 |
| `MemToReg` | 1 | 写回内容：ALU 结果 vs 内存读出 |
| `Branch` | 1 | 是否是条件分支 |
| `Jump` | 1 | 是否是无条件跳转 |
| `ALUControl` | 3 | ALU 操作码 |

### 2.2 5 个阶段（单周期每条指令都走完这 5 步）

```
IF (Instruction Fetch) ─── ID (Decode) ─── EX (Execute) ─── MEM ─── WB (WriteBack)
       取指                译码+读寄存器    ALU 计算         访存      写回寄存器
```

**单周期**：5 个阶段**在一个时钟周期内**全部完成。
**流水线**（L06）：5 个阶段**重叠**在 5 个周期里。

---

## 3. Verilog 模块化设计

L05 的 MIPS CPU 拆为 ~10 个模块：

```
mips_top.v                  ← 顶层模块（连一切）
├── pc.v
├── imem.v                  ← 指令存储器（只读）
├── control.v               ← 主控制单元
├── alu_control.v           ← ALU 控制位生成
├── regfile_32x32.v         ← 寄存器堆
├── mips_alu.v              ← ALU（L03 已做）
├── dmem.v                  ← 数据存储器
├── sign_extend.v           ← 立即数符号扩展
├── mux_2to1_32.v           ← 各种 2 选 1
└── adder_32.v              ← PC+4 + branch 计算
```

### 3.1 `mips_top.v`（顶层）

```verilog
module mips_top (
    input             clk, reset,
    output     [31:0] pc,
    output     [31:0] instr,
    output     [31:0] alu_result,
    output            mem_write
);
    // 内部信号
    wire [31:0] pc_next, pc_plus_4, pc_branch;
    wire [31:0] instr_read;
    wire [31:0] rd1, rd2, wd3;
    wire [4:0]  ra1, ra2, wa3;
    wire        we3, reg_dst, alu_src, mem_to_reg;
    wire        branch, jump, mem_write_ctrl, mem_read;
    wire [2:0]  alu_control;
    wire [1:0]  alu_op;
    wire [31:0] alu_result_internal, mem_read_data;
    wire [31:0] sign_ext_imm;
    wire [31:0] alu_src_b;
    wire [31:0] write_data;
    wire [4:0]  write_reg;
    wire [31:0] jump_target;

    // PC
    pc mips_pc (
        .clk(clk), .reset(reset),
        .branch_taken(branch & (alu_result_internal == 32'h0)),
        .branch_target(pc_branch),
        .jump(jump),
        .jump_target(jump_target),
        .pc(pc)
    );

    // Instruction Memory
    imem mips_imem (.a(pc), .rd(instr_read));
    assign instr = instr_read;

    // Control
    control mips_control (
        .op(instr_read[31:26]),
        .reg_dst(reg_dst), .alu_src(alu_src),
        .mem_to_reg(mem_to_reg), .reg_write(we3),
        .mem_write(mem_write_ctrl), .mem_read(mem_read),
        .branch(branch), .jump(jump), .alu_op(alu_op)
    );

    // RegFile
    assign ra1 = instr_read[25:21];
    assign ra2 = instr_read[20:16];
    regfile_32x32 mips_rf (
        .clk(clk), .we3(we3),
        .ra1(ra1), .ra2(ra2), .wa3(write_reg), .wd3(write_data),
        .rd1(rd1), .rd2(rd2)
    );

    // 写寄存器地址选择（R-type: rd, I-type: rt）
    assign write_reg = reg_dst ? instr_read[15:11] : instr_read[20:16];

    // 立即数符号扩展
    sign_extend mips_se (.imm(instr_read[15:0]), .ext(sign_ext_imm));

    // ALU 控制位生成
    alu_control mips_alu_ctrl (
        .alu_op(alu_op),
        .funct(instr_read[5:0]),
        .alu_control(alu_control)
    );

    // ALU 第二源选择
    assign alu_src_b = alu_src ? sign_ext_imm : rd2;

    // ALU
    mips_alu mips_alu_unit (
        .a(rd1), .b(alu_src_b),
        .alucont({1'b0, alu_control}),
        .result(alu_result_internal),
        .zero(), .overflow()
    );

    // Data Memory
    dmem mips_dmem (
        .clk(clk), .we(mem_write_ctrl),
        .a(alu_result_internal), .wd(rd2),
        .rd(mem_read_data)
    );

    // 写回选择（ALU 结果 vs 内存读出）
    assign write_data = mem_to_reg ? mem_read_data : alu_result_internal;

    // Branch target
    assign pc_branch = pc_plus_4 + {sign_ext_imm[29:0], 2'b00};
    assign pc_plus_4 = pc + 32'd4;

    // Jump target
    assign jump_target = {pc_plus_4[31:28], instr_read[25:0], 2'b00};

    // 输出
    assign alu_result = alu_result_internal;
    assign mem_write = mem_write_ctrl;
endmodule
```

### 3.2 `control.v`（主控制单元）

```verilog
module control (
    input  [5:0] op,
    output       reg_dst, alu_src, mem_to_reg, reg_write,
    output       mem_write, mem_read, branch, jump,
    output [1:0] alu_op
);
    reg [9:0] controls;
    assign {reg_dst, alu_src, mem_to_reg, reg_write,
            mem_write, mem_read, branch, jump, alu_op} = controls;

    always @(*) begin
        case (op)
            6'b000000:    controls = 10'b1_0_0_1_0_0_0_0_10;  // R-type
            6'b100011:    controls = 10'b0_1_1_1_0_1_0_0_00;  // lw
            6'b101011:    controls = 10'b0_1_0_0_1_0_0_0_00;  // sw
            6'b000100:    controls = 10'b0_0_0_0_0_0_1_0_01;  // beq
            6'b001000:    controls = 10'b0_1_0_1_0_0_0_0_00;  // addi
            6'b000010:    controls = 10'b0_0_0_0_0_0_0_1_00;  // j
            default:      controls = 10'b0_0_0_0_0_0_0_0_00;  // illegal
        endcase
    end
endmodule
```

### 3.3 `alu_control.v`

```verilog
module alu_control (
    input  [1:0] alu_op,
    input  [5:0] funct,
    output reg [2:0] alu_control
);
    always @(*) begin
        case (alu_op)
            2'b00: alu_control = 3'b010;  // ADD (for lw/sw/addi)
            2'b01: alu_control = 3'b110;  // SUB (for beq)
            2'b10:                             // R-type, look at funct
                case (funct)
                    6'b100000: alu_control = 3'b010;  // add
                    6'b100010: alu_control = 3'b110;  // sub
                    6'b100100: alu_control = 3'b000;  // and
                    6'b100101: alu_control = 3'b001;  // or
                    6'b101010: alu_control = 3'b111;  // slt
                    default:   alu_control = 3'bxxx;
                endcase
            default: alu_control = 3'bxxx;
        endcase
    end
endmodule
```

---

## 4. 测试程序（MIPS 汇编）

### 4.1 简单测试：5 + 3 = 8

```mips
# test_add.asm（MIPS 汇编）
addi $t0, $zero, 5    # $t0 = 5
addi $t1, $zero, 3    # $t1 = 3
add  $t2, $t0, $t1    # $t2 = 8
sw   $t2, 0($zero)    # mem[0] = 8
```

机器码（用 MARS / SPIM 汇编）：
```
0x20080005  # addi $t0, $zero, 5
0x20090003  # addi $t1, $zero, 3
0x01095020  # add  $t2, $t0, $t1
0xac020000  # sw   $t2, 0($zero)
```

### 4.2 把机器码塞进 imem

```verilog
module imem (
    input  [31:0] a,
    output [31:0] rd
);
    reg [31:0] RAM [63:0];
    initial begin
        $readmemh("test_program.hex", RAM);   // 从文件加载
    end
    assign rd = RAM[a[7:2]];   // 字地址（按字对齐）
endmodule
```

`test_program.hex`：
```
20080005
20090003
01095020
ac020000
```

---

## 5. 测试流程

```bash
cd DDCA/Lab_05_SingleCycle_MIPS

# 1. 编译所有模块 + testbench
iverilog -o sim/mips_tb \
    rtl/mips_top.v rtl/control.v rtl/alu_control.v \
    rtl/regfile_32x32.v rtl/mips_alu.v rtl/imem.v rtl/dmem.v \
    rtl/sign_extend.v rtl/pc.v \
    tb/tb_mips.v

# 2. 跑仿真
vvp sim/mips_tb

# 3. 看波形（验证每个时钟周期的状态）
gtkwave mips.vcd
```

**期望**：4 个周期后 `mem[0] = 8`。

---

## 6. 常见坑

### 坑 1：指令存储器错位

```verilog
assign rd = RAM[a];   // ❌ a 是字节地址，应该按字对齐
assign rd = RAM[a[7:2]];  // ✅
```

MIPS 是字节寻址，但每条指令 4 字节。

### 坑 2：RegFile 的写回竞争

```verilog
regfile rf (
    .wa3(write_reg),
    .wd3(alu_result),
    ...
);
```

如果是 `lw` 指令，应该写回的是**内存读出**而不是 ALU 结果。
**必须用 mem_to_reg 多路选择**。

### 坑 3：jal 没保存返回地址

`jal` 要把 PC+4 写到 `$ra`（reg 31）。
**很多初学者忘了这一步**。

### 坑 4：jr 没走专用通路

`jr $ra` 要把 `$ra` 的值作为下一拍的 PC。
**必须有一个 mux 把 regfile 的读出送到 PC**。

### 坑 5：分支偏移算错

```
beq target    # target 是相对 PC+4 的偏移（按字）
```

```verilog
assign pc_branch = pc + 4 + {sign_ext_imm[29:0], 2'b00};
//                          ^^^^^                 ^^^^^^
//                          注意是 PC+4 不是 PC    左移 2 位（字地址 → 字节地址）
```

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`Capstone/cpu_simulator/rv32i_sim.py`](../../Capstone/cpu_simulator/) 的对照

| 方面 | L05 MIPS CPU（Verilog）| RV32I Simulator（Python）|
|------|----------------------|--------------------------|
| ISA | MIPS | RV32I（RISC-V）|
| 风格 | 单周期硬件描述 | 5 级流水软件模拟 |
| 工具 | iverilog | Python |
| 测试 | iverilog + GTKWave | pytest（77 个测试）|
| 概念相同点 | datapath + control | datapath + control |
| 概念不同点 | 真硬件可综合 | 纯软件，可加 print 调试 |

→ **L05 + Capstone 形成完整对照**：硬件 vs 软件实现同一概念。

### 7.2 与 [`Lab02_流水线与ILP`](../../Lab02_流水线与ILP/) 的连接

L05 是**单周期**——每条指令 1 拍完成，**时钟周期等于最慢指令的延迟**（`lw` 约 8 ns）。
**飞腾真机是流水线**——每条指令 1 拍，但每拍 < 0.4 ns。

→ [`Lab02`](../../Lab02_流水线与ILP/) 用 perf 实测飞腾 IPC，与单周期 L05 形成强烈对比。

### 7.3 与 [`Nand2Tetris/Project_05`](../../Nand2Tetris/Project_05_ComputerArchitecture/) 的对照

| 方面 | Hack CPU（Nand2Tetris P05）| MIPS CPU（DDCA L05）|
|------|---------------------------|---------------------|
| ISA | Hack（2 种指令）| MIPS（30+ 指令）|
| 位宽 | 16 位 | 32 位 |
| 寄存器 | 2（A, D）| 32 |
| 写法 | 自定义 HDL | Verilog |
| 可综合 | ❌ | ✅ |
| 工程量 | 8 小时 | 30 小时 |
| **概念相同点** | datapath + control | 同 |

→ **L05 = 工业级的 Nand2Tetris P05**。

### 7.4 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

L05 让你**亲手实现了 L3 ISA + L2 微架构**——
现在你完全理解"ISA 是契约，微架构是实现"的精确含义。

---

## 8. 扩展挑战

1. **加 `mult/div/mfhi/mflo`**：硬件乘除法（用 L03 的乘法器）
2. **加 syscall**：实现简单的系统调用接口（参考 L08）
3. **加 Cache（L07 内容）**：在 imem/dmem 前加直接映射 Cache
4. **加异常**：syscall/overflow/IRQ（L08 内容）
5. **流水化（L06 内容）**：5 级流水 + 前递

---

## 9. 检查清单

- [ ] 实现 30+ 条 MIPS 指令
- [ ] 跑通基础测试（add/sub/lw/sw/beq/j）
- [ ] PC+4 / branch / jump 三种地址更新都能跑
- [ ] RegFile 的 $zero 永远 0
- [ ] 用 GTKWave 看完整波形
- [ ] 跑一个真实小程序（如排序）

---

## 📌 下一步

🎉 完成后，**你已经造出了一台真正的 MIPS CPU**！

进 [`Lab_06_Pipelined_MIPS/`](../Lab_06_Pipelined_MIPS/)——
你把单周期 CPU **改造为 5 级流水线**，加上**冒险检测**和**前递单元**。
**这是 DDCA 最难的 lab，也是性能工程的起点**。
