# Lab 02 — Combinational Logic：组合电路设计实战

> **一句话目标**：实现 **7 段数码管译码器 + 算术比较器 + 优先编码器**——
> 掌握 Verilog 的 `case` / `if-else` / `for` 在组合逻辑中的用法。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch2 §2.7-2.10**（组合电路 + Verilog 实战）|
| 🎥 Mutlu | [Lecture 3: Combinational Logic Design](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 10–15 小时 |

---

## 1. 你将构建的 3 个模块

| # | 模块 | 功能 | 难度 |
|---|------|------|------|
| 1 | `seg7_decoder` | 16 进制 → 7 段数码管 | ⭐⭐ |
| 2 | `comparator_32` | 32 位有符号比较（输出 <, =, > 三个标志）| ⭐⭐ |
| 3 | `priority_encoder_8` | 8 路 priority encoder | ⭐⭐⭐ |

---

## 2. 关键概念

### 2.1 7 段数码管原理

FPGA 板上的数码管长这样（每段是独立 LED）：

```
 ─aa─
|    |
ff  bb
|    |
 ─gg─
|    |
ee  cc
|    |
 ─dd─   ·dp
```

每个段对应 1 bit，1 表示亮。**共阴 vs 共阳**接法不同（Nexys 4 是共阳，0 = 亮）。

| 数字 | 段码（共阳）|
|------|------------|
| 0 | `1000000` |
| 1 | `1111001` |
| ... | ... |

### 2.2 优先编码器

如果多个输入同时为 1，输出**优先级最高**的那个。

| 输入 | 输出 |
|------|------|
| `00000001` | `000` |
| `00000010` | `001` |
| `00000100` | `010` |
| ... | ... |

→ 这是中断控制器的核心组件。

---

## 3. 骨架代码

### 3.1 `seg7_decoder.v`

```verilog
module seg7_decoder (
    input      [3:0]  hex_digit,
    output reg [6:0]  seg     // {g, f, e, d, c, b, a}
);
    always @(*) begin
        case (hex_digit)
            4'h0: seg = 7'b1000000;
            4'h1: seg = 7'b1111001;
            4'h2: seg = 7'b0100100;
            4'h3: seg = 7'b0110000;
            4'h4: seg = 7'b0011001;
            4'h5: seg = 7'b0010010;
            4'h6: seg = 7'b0000010;
            4'h7: seg = 7'b1111000;
            4'h8: seg = 7'b0000000;
            4'h9: seg = 7'b0010000;
            4'hA: seg = 7'b0001000;
            4'hB: seg = 7'b0000011;
            4'hC: seg = 7'b1000110;
            4'hD: seg = 7'b0100001;
            4'hE: seg = 7'b0000110;
            4'hF: seg = 7'b0001110;
            default: seg = 7'bxxxxxxx;
        endcase
    end
endmodule
```

### 3.2 `comparator_32.v`

```verilog
module comparator_32 (
    input  signed [31:0] a, b,
    output                lt, eq, gt
);
    assign lt = (a < b);
    assign eq = (a == b);
    assign gt = (a > b);
endmodule
```

### 3.3 `priority_encoder_8.v`

```verilog
module priority_encoder_8 (
    input      [7:0] req,
    output reg [2:0] y,
    output reg       valid
);
    integer i;
    always @(*) begin
        y = 3'b000;
        valid = 1'b0;
        for (i = 7; i >= 0; i = i - 1) begin
            if (req[i]) begin
                y = i[2:0];
                valid = 1'b1;
            end
        end
    end
endmodule
```

→ **关键技巧**：从高位往低位扫，找到第一个 1 就锁定。

---

## 4. 测试

每个模块都写自检 testbench，跑全部真值表项。

---

## 5. 常见坑

### 坑 1：`always @(*)` 的敏感列表

```verilog
always @(a)              // ❌ 漏了 b
    y = a & b;

always @(*)              // ✅ 通配符，自动包含所有右边信号
    y = a & b;
```

### 坑 2：`case` 漏了 default

```verilog
always @(*) case (sel)
    2'b00: y = a;
    2'b01: y = b;
    // ❌ 没写 default，sel 为 2'b10/11 时是 latch！
endcase
```

→ **所有组合 `case` 必须有 `default`**，否则综合时生成**锁存器**（不是寄存器），导致功能错乱。

### 坑 3：用 `=` 而不是 `<=` in `always @(*)`

```verilog
always @(*) begin
    a = b;     // ✅ 在组合逻辑里应该用 =
    c = a + 1; // 看到上一行的新值，符合预期
end
```

→ **组合逻辑用 `=`，时序逻辑用 `<=`**——前面讲过的口诀。

### 坑 4：signed 必须两个 operand 都 signed

```verilog
input signed [31:0] a;
input        [31:0] b;
wire signed [31:0] sum = a + b;   // ❌ b 是无符号，比较时 a 也变无符号

input signed [31:0] a, b;          // ✅ 两个都 signed
```

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Expert_03_HW_Designer/rtl/two_bit_predictor.v`](../../Expert_03_HW_Designer/rtl/) 的连接

L02 的优先编码器原理 = 分支预测器里的"优先级冲突解决"。
直接读 `two_bit_predictor.v`（状态机用 `case`），与本 lab 风格一致。

### 6.2 与 [`Nand2Tetris/Project_01`](../../Nand2Tetris/Project_01_BooleanLogic/) 的对照

Nand2Tetris 的 DMux4Way（用 1 分 4）= Verilog 的 `case(sel)` 写法。
但 Nand2Tetris 必须用芯片搭，Verilog 直接描述行为，简洁 100 倍。

---

## 7. 检查清单

- [ ] 能用 `case` 写组合逻辑（必须有 default）
- [ ] 能用 `for` 在 testbench 里跑遍真值表
- [ ] 理解 signed/unsigned 的区别
- [ ] 7 段数码管译码器全 16 种输入测试通过

---

## 📌 下一步

完成 L02 后，进 [`Lab_03_ALU/`](../Lab_03_ALU/)。
你将实现 **MIPS ALU**——这是 L05 单周期 MIPS 的核心组件。
