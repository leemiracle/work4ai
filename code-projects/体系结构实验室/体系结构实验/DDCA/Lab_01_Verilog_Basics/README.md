# Lab 01 — Verilog Basics：用工业 HDL 写出第一个电路

> **一句话目标**：用 **IEEE 1364-2005 Verilog** 写出 4 个简单模块（mux/decoder/full-adder/dff）+ 配套 testbench——
> **学会 iverilog + GTKWave 工具链**，建立 Verilog 与 Nand2Tetris HDL 的对应关系。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch1-2**（数字抽象 + 组合逻辑）+ **Ch4 §4.1-4.3**（Verilog 入门）|
| 🎥 Mutlu | [Lecture 4-6: Verilog HDL](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| 🛠 工具 | iverilog + GTKWave |
| ⏱ 预计工时 | 8–12 小时 |

---

## 1. 你将构建的 4 个模块

| # | 模块 | 类型 | 难度 |
|---|------|------|------|
| 1 | `mux2_1` | 2 选 1 多路选择器 | ⭐ |
| 2 | `decoder3_8` | 3-8 译码器 | ⭐ |
| 3 | `fulladder` | 全加器 | ⭐ |
| 4 | `flopr` | 上升沿触发的寄存器 | ⭐⭐ |

每个模块都要写：
- `rtl/*.v`：模块实现
- `tb/*_tb.v`：自检 testbench
- 验证通过后用 GTKWave 看波形

---

## 2. 关键概念

### 2.1 Verilog 与 Nand2Tetris HDL 的对照

| 维度 | Nand2Tetris HDL | Verilog |
|------|-----------------|---------|
| 设计风格 | **纯结构化**（必须用低级芯片搭）| **混合**（行为级 + 结构级）|
| 一行能写什么 | 只能 `Nand(a=x, b=y, out=z);` | `assign z = x & y;`、`always @(posedge clk)`、`if-else`、`case` |
| 综合 | ❌ | ✅ 可综合 |
| 工业使用 | ❌ | ✅（IEEE 1364 标准）|
| 原语 | Nand | `&` `\|` `^` `~` `<` `>` 等 |
| 模块语法 | `CHIP X { IN ... OUT ... PARTS: ... }` | `module X(input ..., output ...); ... endmodule` |

**关键转变**：Verilog 允许**行为级描述**，例如直接写 `assign sum = a + b;`，不必关心底层用什么电路实现——综合工具会自动选 RCA 还是 CLA。

### 2.2 Verilog 模块的基本结构

```verilog
module mux2_1 (
    input  [3:0] d0, d1,    // 4 位数据输入
    input        s,         // 选择信号
    output [3:0] y          // 输出
);
    assign y = s ? d1 : d0;  // 三元表达式
endmodule
```

**核心语法**：
- `module X(...) ... endmodule`：模块定义
- `input/output/inout`：端口方向
- `[N:0]`：位宽（如 `[3:0]` 是 4 位）
- `assign`：组合逻辑连续赋值
- `always @(posedge clk)`：时序逻辑（时钟上升沿触发）
- `wire` / `reg`：信号类型（**`reg` 不一定是寄存器！**）

### 2.3 `wire` vs `reg`（最容易混淆）

| 类型 | 用途 | 赋值方式 |
|------|------|---------|
| `wire` | 组合逻辑的连线 | `assign` |
| `reg` | `always` 块里赋值的信号 | `=`（阻塞）或 `<=`（非阻塞）|

**重点**：`reg` **不一定综合成寄存器**——如果它在 `always @(*)` 里赋值，综合工具会生成组合逻辑。
"是否寄存器"取决于**赋值上下文**（时钟边沿 vs 组合逻辑），不是关键词。

### 2.4 阻塞 vs 非阻塞赋值

```verilog
// ❌ 错：时序逻辑用阻塞
always @(posedge clk) begin
    a = b;
    b = a;  // 这一行看到的是 a 的【新值】，会乱套
end

// ✅ 对：时序逻辑用非阻塞
always @(posedge clk) begin
    a <= b;
    b <= a;  // 同时采样上一拍，等价于交换
end
```

**口诀**：
- **时序逻辑（`always @(posedge clk)`）必须用 `<=`**
- **组合逻辑（`always @(*)` 或 `assign`）用 `=`**

---

## 3. 骨架代码

### 3.1 `mux2_1.v`

```verilog
module mux2_1 (
    input  [3:0] d0,
    input  [3:0] d1,
    input        s,
    output [3:0] y
);
    assign y = s ? d1 : d0;
endmodule
```

### 3.2 `decoder3_8.v`

```verilog
module decoder3_8 (
    input  [2:0] a,
    output [7:0] y
);
    assign y = (1'b1 << a);   // 1 左移 a 位
endmodule
```

**或等价的 case 写法**：

```verilog
module decoder3_8 (
    input  [2:0] a,
    output reg [7:0] y
);
    always @(*) begin
        case (a)
            3'd0: y = 8'b00000001;
            3'd1: y = 8'b00000010;
            3'd2: y = 8'b00000100;
            3'd3: y = 8'b00001000;
            3'd4: y = 8'b00010000;
            3'd5: y = 8'b00100000;
            3'd6: y = 8'b01000000;
            3'd7: y = 8'b10000000;
            default: y = 8'bxxxxxxxx;
        endcase
    end
endmodule
```

### 3.3 `fulladder.v`

```verilog
module fulladder (
    input  a, b, cin,
    output sum, cout
);
    assign {cout, sum} = a + b + cin;  // 用拼接运算符自动处理进位
endmodule
```

**或等价的门级描述**（让你看清结构）：

```verilog
module fulladder (
    input  a, b, cin,
    output sum, cout
);
    wire x1, x2, x3;
    xor (sum, a, b, cin);          // sum = a ^ b ^ cin
    and (x1, a, b);
    and (x2, a, cin);
    and (x3, b, cin);
    or  (cout, x1, x2, x3);        // cout = ab + acin + bcin
endmodule
```

### 3.4 `flopr.v`（reset-able register）

```verilog
module flopr #(parameter WIDTH = 8) (
    input             clk, reset,
    input  [WIDTH-1:0] d,
    output [WIDTH-1:0] q
);
    always @(posedge clk, posedge reset)
        if (reset) q <= 0;
        else       q <= d;
endmodule
```

**关键点**：
- `#(parameter WIDTH = 8)`：参数化宽度（与 Nand2Tetris 不同，Verilog 支持参数）
- `always @(posedge clk, posedge reset)`：异步 reset
- `<=`：非阻塞赋值（必须用）

---

## 4. Testbench 写法

```verilog
// tb_mux2_1.v
`timescale 1ns/1ps

module tb_mux2_1;
    reg  [3:0] d0, d1;
    reg        s;
    wire [3:0] y;

    // 实例化被测模块
    mux2_1 uut (
        .d0(d0), .d1(d1), .s(s), .y(y)
    );

    initial begin
        // 测试 1：s=0，输出 d0
        d0 = 4'hA; d1 = 4'h5; s = 0;
        #10;
        $display("Test 1: y = %h (expected a)", y);
        if (y !== 4'hA) $display("FAIL"); else $display("PASS");

        // 测试 2：s=1，输出 d1
        s = 1;
        #10;
        $display("Test 2: y = %h (expected 5)", y);
        if (y !== 4'h5) $display("FAIL"); else $display("PASS");

        $finish;
    end

    // 生成波形
    initial begin
        $dumpfile("mux2_1.vcd");
        $dumpvars(0, tb_mux2_1);
    end
endmodule
```

---

## 5. 运行与测试

```bash
cd DDCA/Lab_01_Verilog_Basics

# 1. 编译 RTL + testbench
iverilog -o sim/mux_tb rtl/mux2_1.v tb/tb_mux2_1.v

# 2. 跑仿真
vvp sim/mux_tb

# 3. 看波形
gtkwave mux2_1.vcd
```

**期望输出**：
```
Test 1: y = a (expected a)
PASS
Test 2: y = 5 (expected 5)
PASS
```

---

## 6. 常见坑

### 坑 1：`reg` 不等于寄存器

```verilog
reg [3:0] x;        // x 是 reg 类型
always @(*) x = a + b;   // 但这是【组合逻辑】！综合后是普通连线
```

→ **关键看上下文**，不是关键词。

### 坑 2：`always @(*)` vs `always @(posedge clk)`

```verilog
always @(*) a = b;       // 组合：b 变 a 立刻变
always @(posedge clk) a <= b;  // 时序：a 在时钟上升沿才更新
```

→ 写错了综合工具不会报错，但功能完全不对。

### 坑 3：忘记声明位宽

```verilog
input a, b;             // 1 位
input [7:0] c;          // 8 位
input d;                // 1 位（不是数组！）
```

→ 默认是 1 位。

### 坑 4：`initial` 在综合时被忽略

```verilog
initial a = 0;          // ❌ 不能综合（只用于 testbench）
```

→ FPGA 上电后需要用 reset 信号初始化，不能用 `initial`。

### 坑 5：阻塞 `=` 在时序逻辑里造成竞争

```verilog
always @(posedge clk) begin
    a = b;       // ❌ 阻塞：当前块内的下一条立刻看到新值
    c = a;       // 但别的 always 块可能看到旧值
end
```

→ **时序逻辑必须用 `<=`**。

---

## 7. 与本项目其他模块的连接

### 7.1 与 [`Nand2Tetris/Project_01`](../../Nand2Tetris/Project_01_BooleanLogic/) 的对照

| Nand2Tetris HDL | 等价 Verilog |
|-----------------|--------------|
| `CHIP Mux { IN a, b, sel; OUT out; PARTS: ...}` | `module Mux(input a, b, sel, output y); assign y = sel ? b : a; endmodule` |
| `And(a=x, b=y, out=z)` | `and (z, x, y);` 或 `assign z = x & y;` |
| 多位总线 `a[0..15]` | `[15:0] a` |
| 自带 clock | 必须显式 `input clk;` |

### 7.2 与 [`Expert_03_HW_Designer/rtl/alu.v`](../../Expert_03_HW_Designer/rtl/alu.v) 的连接

学完 L01-L04 后，直接打开本项目 Expert_03 的 Verilog 文件：
- `alu.v`：10 条 RV32I ALU 操作（与 L03 相似）
- `forwarding_unit.v`：流水线前递单元（与 L06 相似）
- `two_bit_predictor.v`：分支预测器（与 L06 配套）

→ **做完 L01-L04，Expert_03 的 Verilog 就完全能读懂**。

### 7.3 与 [`背景知识/处理器分层模型.md`](../../背景知识/处理器分层模型.md) 的连接

L01 让你建立了 **L2 微架构 + L1 物理实现** 的描述能力——
**Verilog 是连接"设计意图"和"物理电路"的工程语言**。

---

## 8. 扩展挑战

1. **用 Yosys 综合**：把你的 `mux2_1.v` 用 `yosys` 综合为门级网表，看综合后的电路图
2. **重写 Nand2Tetris P01 的 15 个芯片**：用 Verilog 表达式 1 小时全部完成
3. **用 SystemVerilog**：Verilog 的进阶版本（IEEE 1800-2017），加 `interface`、`enum`、`assertion`
4. **用 Formal Verification**：用 SymbiYosys + Yosys 验证你的模块符合规范

---

## 9. 检查清单

- [ ] 理解 `wire` vs `reg`（不再混淆）
- [ ] 理解阻塞 `=` vs 非阻塞 `<=`
- [ ] 能用 `assign` 写组合逻辑
- [ ] 能用 `always @(posedge clk)` 写时序逻辑
- [ ] 能写 testbench + `$dumpvars` 生成波形
- [ ] 能用 iverilog + GTKWave 跑通 4 个模块
- [ ] 能读懂 [`Expert_03/rtl/alu.v`](../../Expert_03_HW_Designer/rtl/alu.v) 的 80%

---

## 📌 下一步

完成 L01 后，进 [`Lab_02_Combinational/`](../Lab_02_Combinational/)。
你将实现 7 段数码管译码器（FPGA 板上最常见的输出设备）+ ALU 前置电路——
为 L03 的 MIPS ALU 做准备。
