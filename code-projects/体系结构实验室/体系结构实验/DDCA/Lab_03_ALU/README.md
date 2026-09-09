# Lab 03 — ALU：实现 MIPS 算术逻辑单元

> **一句话目标**：实现 **MIPS 32 位 ALU**，支持 **add / sub / and / or / slt / shift-left / shift-right** 等 10 种运算——
> 这是 L05 单周期 MIPS 的核心。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch5 §5.2**（Arithmetic Circuits）+ **Ch5 §5.3**（ALU 设计）|
| 🎥 Mutlu | [Lecture 7-8: Arithmetic + ALU](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 12–18 小时 |

---

## 1. 你将构建的 ALU

```
                ┌─────────────────────────────┐
                │                             │
   a [31:0] ────┤                             │
                │       MIPS ALU (32-bit)     ├── result [31:0]
   b [31:0] ────┤                             │
                │                             ├── zero
   alucont[3:0]─┤                             │
                │                             ├── overflow
                └─────────────────────────────┘
```

### 1.1 ALU 控制位（Harris 表 5.1）

| alucont | 功能 | a op b |
|---------|------|--------|
| `0000` | AND | a & b |
| `0001` | OR  | a \| b |
| `0010` | ADD | a + b |
| `0110` | SUB | a - b |
| `0111` | SLT | (a < b) ? 1 : 0 |
| `1100` | NOR | ~(a \| b) |

### 1.2 关键子模块

| 子模块 | 功能 | 难度 |
|--------|------|------|
| `adder_32` | 32 位行波进位加法器 | ⭐ |
| `shifter` | 算术/逻辑移位 | ⭐⭐ |
| `comparator` | 有符号比较（基于减法）| ⭐ |
| `mux4` | 4 选 1（按 alucont 选输出）| ⭐ |

---

## 2. 关键概念

### 2.1 Adder 优化：CLA（Carry-Lookahead Adder）

行波进位加法器（RCA）慢——32 位 RCA 需要 32 级 full-adder 串行进位。

**CLA** 把进位生成抽象为：

```
G_i = a_i & b_i                // 生成位
P_i = a_i XOR b_i              // 传播位
C_{i+1} = G_i | (P_i & C_i)    // 进位公式
```

CLA 把进位链"并行化"，32 位 CLA 比 RCA 快 5-8 倍。

→ **飞腾 ALU**（[`Lab01 §3.4`](../../Lab01_ISA与汇编/) 实测 add 1 cyc @ 2.5GHz）就是用 CLA + 前递流水。

### 2.2 溢出检测（Overflow）

对于补码加法：

```
overflow = (a[31] == b[31]) && (result[31] != a[31])
```

即：两个同号数相加，结果符号变了 → 溢出。

### 2.3 SLT（Set Less Than）的实现

```verilog
wire signed [31:0] diff = $signed(a) - $signed(b);
assign slt_result = diff[31] ? 32'h1 : 32'h0;   // 差为负 = a < b
```

或直接用 `<`：

```verilog
assign slt_result = ($signed(a) < $signed(b)) ? 32'h1 : 32'h0;
```

---

## 3. Verilog 实现

### 3.1 `mips_alu.v`（核心模块）

```verilog
module mips_alu (
    input  [31:0] a, b,
    input  [3:0]  alucont,
    output reg [31:0] result,
    output        zero,
    output        overflow
);
    // 内部信号
    wire [31:0] add_result, sub_result;
    wire        add_overflow, sub_overflow;

    // 加减法（统一用加法器，sub 时取反 + 1）
    assign add_result = a + b;
    assign sub_result = a - b;

    // 溢出检测
    assign add_overflow = (a[31] == b[31]) && (add_result[31] != a[31]);
    assign sub_overflow = (a[31] != b[31]) && (sub_result[31] != a[31]);

    // 主选择逻辑
    always @(*) begin
        case (alucont)
            4'b0000: result = a & b;
            4'b0001: result = a | b;
            4'b0010: result = add_result;
            4'b0110: result = sub_result;
            4'b0111: result = ($signed(a) < $signed(b)) ? 32'h1 : 32'h0;
            4'b1100: result = ~(a | b);
            default: result = 32'hxxxxxxxx;
        endcase
    end

    assign zero = (result == 32'h0);
    assign overflow = (alucont == 4'b0010) ? add_overflow :
                      (alucont == 4'b0110) ? sub_overflow : 1'b0;
endmodule
```

### 3.2 `rca_32.v`（如果你想手写 adder）

```verilog
module rca_32 (
    input  [31:0] a, b,
    input         cin,
    output [31:0] sum,
    output        cout
);
    wire [32:0] c;
    assign c[0] = cin;

    genvar i;
    generate
        for (i = 0; i < 32; i = i + 1) begin : fulladder_chain
            wire p, g;
            assign p = a[i] ^ b[i];
            assign g = a[i] & b[i];
            assign sum[i] = p ^ c[i];
            assign c[i+1] = g | (p & c[i]);
        end
    endgenerate

    assign cout = c[32];
endmodule
```

→ 这是 **行为级 + generate** 的工业级写法。

---

## 4. Testbench

```verilog
module tb_mips_alu;
    reg  [31:0] a, b;
    reg  [3:0]  alucont;
    wire [31:0] result;
    wire        zero, overflow;

    mips_alu uut (
        .a(a), .b(b), .alucont(alucont),
        .result(result), .zero(zero), .overflow(overflow)
    );

    initial begin
        // ADD 测试
        a = 32'd5; b = 32'd3; alucont = 4'b0010; #10;
        $display("ADD: %d + %d = %d", a, b, result);
        assert(result === 32'd8) else $error("ADD failed");

        // SUB
        a = 32'd10; b = 32'd7; alucont = 4'b0110; #10;
        $display("SUB: %d - %d = %d", a, b, result);

        // SLT
        a = 32'hFFFFFFFF; b = 32'h00000001; alucont = 4'b0111; #10;
        // a = -1 (signed), b = 1 → a < b → 1
        $display("SLT: signed(%d) < %d = %d", $signed(a), $signed(b), result);

        // Overflow
        a = 32'h7FFFFFFF; b = 32'h00000001; alucont = 4'b0010; #10;
        $display("ADD overflow: %d + %d = %d, ov=%b", a, b, result, overflow);

        $finish;
    end
endmodule
```

---

## 5. 常见坑

### 坑 1：signed 与 unsigned 混用

```verilog
wire [31:0] r = a + b;  // ❌ a, b 是 signed，r 是 unsigned，加法变成 unsigned
wire signed [31:0] r = a + b;  // ✅ r 也是 signed
```

→ **凡是有符号运算，所有信号都要 `signed`**。

### 坑 2：SLT 用 unsigned 比较

```verilog
result = (a < b) ? 1 : 0;   // ❌ a, b 是 unsigned，-1 < 1 是 false（因为 -1 = 0xFFFFFFFF）
result = ($signed(a) < $signed(b)) ? 1 : 0;  // ✅ 有符号比较
```

### 坑 3：忘记 generate

```verilog
for (i = 0; i < 32; i = i + 1)
    fulladder fa(...);   // ❌ Verilog 不允许 module 调用在 for 里
```

→ 必须用 `generate ... endgenerate`。

### 坑 4：overflow 检测漏掉 SUB

```verilog
assign overflow = (a[31] == b[31]) && (result[31] != a[31]);   // ❌ 只对 ADD 正确
```

→ SUB 时是 `a[31] != b[31]` 才可能溢出。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Expert_03_HW_Designer/rtl/alu.v`](../../Expert_03_HW_Designer/rtl/) 的对照

直接对比本项目已有的 RV32I ALU：

| 特性 | L03 MIPS ALU（本 lab）| RV32I ALU（Expert_03）|
|------|---------------------|----------------------|
| 指令集 | MIPS（10 条）| RV32I（10 条）|
| 位宽 | 32 | 32 |
| 加法器 | RCA 或 CLA | RCA |
| 溢出 | 显式输出 | 不显式（ISA 不要求）|
| SLT | ✅ | ✅（`slt` 指令）|
| Verilog 风格 | case 选择 | case 选择 |

→ **90% 相同**，只是 ISA 不同。学完 L03 直接读懂 Expert_03 的 alu.v。

### 6.2 与 [`Nand2Tetris/Project_02`](../../Nand2Tetris/Project_02_BooleanArithmetic/) 的对照

| 方面 | Nand2Tetris ALU | L03 MIPS ALU |
|------|----------------|--------------|
| 控制位 | 6 位 | 4 位 |
| 位数 | 16 | 32 |
| 实现 | 全 Nand 拼出 | Verilog 行为级描述 |
| 工程量 | 8 小时拼 HDL | 4 小时写 Verilog |
| 可综合 | ❌ | ✅ |

→ **Nand2Tetris 让你懂原理，DDCA 让你懂工程**。

### 6.3 与 [`Lab01 §3.4`](../../Lab01_ISA与汇编/) 的对照

学完 L03 后看飞腾真机的 ALU 实测数据：

| 运算 | L03 MIPS ALU（理论）| 飞腾 D3000M（`[实测]`）|
|------|---------------------|------------------------|
| add | 32 级 RCA = ~10 门延迟 | **1 cyc @ 2.5GHz = 0.4 ns**（CLA + 流水）|
| mul | 软件（移位 + 加）| **3 cyc**（硬件 Booth 乘法器）|
| div | 软件（长除法）| **10.4 cyc**（SRT 除法器）|

---

## 7. 扩展挑战

1. **CLA 实现**：把 RCA 替换为 4-bit CLA 链，比较关键路径延迟
2. **乘法器**：实现 32×32 → 64 位有符号 Booth 乘法器（与 Nand2Tetris 不同，工业必需）
3. **除法器**：实现 32 位 SRT 除法器
4. **FMA（Fused Multiply-Add）**：实现 `a*b + c`（高性能计算核心）
5. **流水化**：把 ALU 切成 3 级流水（Input/Compute/Output），看吞吐量

---

## 8. 检查清单

- [ ] 6 种基本运算（AND/OR/ADD/SUB/SLT/NOR）测试通过
- [ ] overflow 检测对 ADD 和 SUB 都正确
- [ ] SLT 用有符号比较（`$signed`）
- [ ] 全部 32 位测试，含边界（0, -1, MAX_INT, MIN_INT）

---

## 📌 下一步

完成 L03 后，进 [`Lab_04_Sequential/`](../Lab_04_Sequential/)。
你将实现 **寄存器、计数器、有限状态机（FSM）**——
为 L05 的 PC + control unit 做准备。
