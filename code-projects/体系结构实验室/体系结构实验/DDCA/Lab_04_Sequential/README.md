# Lab 04 — Sequential Logic：寄存器、计数器与有限状态机

> **一句话目标**：实现 **寄存器堆、程序计数器（PC）、FSM（红绿灯控制器）**——
> 时序逻辑是 L05 单周期 MIPS 的另一半基础。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch3**（Sequential Logic）+ **Ch5 §5.5**（Memory）|
| 🎥 Mutlu | [Lecture 9-10: Sequential Circuits](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 10–15 小时 |

---

## 1. 你将构建的 4 个模块

| # | 模块 | 功能 | 难度 |
|---|------|------|------|
| 1 | `regfile_32x32` | 32×32 寄存器堆（MIPS 标准）| ⭐⭐ |
| 2 | `pc` | 程序计数器 + 4 + 跳转 | ⭐ |
| 3 | `traffic_light_fsm` | 红绿灯 FSM（经典案例）| ⭐⭐⭐ |
| 4 | `lfsr_8` | 8 位线性反馈移位寄存器（伪随机）| ⭐⭐ |

---

## 2. 关键概念

### 2.1 时序电路的三要素

| 要素 | 含义 | 实例 |
|------|------|------|
| **状态** | 电路记住的东西 | PC 值、寄存器内容 |
| **输入** | 当前要响应的信号 | next_pc、load |
| **输出** | 当前拍对外暴露的值 | 当前 PC、寄存器读出值 |

### 2.2 寄存器堆（Register File）

MIPS 有 32 个通用寄存器，每个 32 位：

```
          addr1 ──┐
                  │
          addr2 ──┤
                  │
       we (write  │
        enable)──┤
                  │
       wd[31:0] ──┤     ┌──────────────────┐
                  ├────►│   32 × 32 bit     │
                  │     │   Register File   │
       clk ───────┤     │                  ├── rd1[31:0]
                  │     │                  │
                  │     └──────────────────┴── rd2[31:0]
                  │
       wa[4:0] ───┘   (write address)
```

**关键**：通常 **2 读 1 写**（MIPS R-type 指令需要两个源 + 一个目标）。

### 2.3 PC 的设计

MIPS 单周期 PC 行为：
- 默认：`PC <= PC + 4`
- 跳转（`J` / `JAL`）：`PC <= jump_target`
- 分支（`BEQ` / `BNE` 且条件满足）：`PC <= PC + 4 + imm << 2`

```verilog
module pc (
    input             clk, reset,
    input             branch_taken,
    input      [31:0] branch_target,
    input             jump,
    input      [31:0] jump_target,
    output reg [31:0] pc
);
    wire [31:0] next_pc =
        jump        ? jump_target :
        branch_taken ? branch_target :
                      pc + 32'd4;

    always @(posedge clk, posedge reset)
        if (reset) pc <= 32'h00000000;
        else       pc <= next_pc;
endmodule
```

### 2.4 FSM（红绿灯）

经典案例：东西向 + 南北向红绿灯，按钮请求行人优先。

```
       state diagram
       
       ┌─────┐
       │ S0  │ ←─ 东西绿 / 南北红
       └──┬──┘
          │ timeout
       ┌──▼──┐
       │ S1  │ ←─ 东西黄
       └──┬──┘
          │ timeout
       ┌──▼──┐
       │ S2  │ ←─ 东西红 / 南北绿
       └──┬──┘
          │ timeout
       ┌──▼──┐
       │ S3  │ ←─ 南北黄
       └──┬──┘
          │
       ┌──▼──┐
       │ S0  │ （回到初始）
       └─────┘
```

**Moore vs Mealy**：
- **Moore**：输出只依赖当前状态（更安全，但慢）
- **Mealy**：输出依赖当前状态 + 输入（更快，但可能 glitches）

---

## 3. Verilog 实现

### 3.1 `regfile_32x32.v`（核心模块）

```verilog
module regfile_32x32 (
    input             clk, we3,
    input      [4:0]  ra1, ra2, wa3,
    input      [31:0] wd3,
    output     [31:0] rd1, rd2
);
    reg [31:0] rf [31:0];   // 32 个 32 位寄存器

    // 同步写
    always @(posedge clk)
        if (we3 && (wa3 != 5'd0))   // $zero 永远是 0
            rf[wa3] <= wd3;

    // 异步读（组合）
    assign rd1 = (ra1 == 5'd0) ? 32'h0 : rf[ra1];
    assign rd2 = (ra2 == 5'd0) ? 32'h0 : rf[ra2];
endmodule
```

**关键设计**：
- `$zero`（寄存器 0）写什么都无效，读出永远 0（MIPS 标准）
- 写同步、读异步——这是单周期 CPU 的标准做法

### 3.2 `pc.v`（已在 §2.3 给出）

### 3.3 `traffic_light_fsm.v`

```verilog
module traffic_light_fsm (
    input             clk, reset,
    input             pedestrian_request,
    output reg [2:0]  lights_ew,  // {red, yellow, green}
    output reg [2:0]  lights_ns
);
    localparam S_EW_GREEN = 2'd0;
    localparam S_EW_YELLOW = 2'd1;
    localparam S_NS_GREEN = 2'd2;
    localparam S_NS_YELLOW = 2'd3;

    reg [1:0]  state, next_state;
    reg [19:0] timer;          // 5 秒计数器（50MHz × 5s）
    reg        timer_reset;

    // 状态寄存器
    always @(posedge clk, posedge reset)
        if (reset) state <= S_EW_GREEN;
        else       state <= next_state;

    // 定时器
    always @(posedge clk, posedge reset) begin
        if (reset || timer_reset) timer <= 0;
        else                       timer <= timer + 1;
    end

    // 状态转移（组合）
    always @(*) begin
        next_state = state;
        timer_reset = 0;
        case (state)
            S_EW_GREEN: if (timer >= 20'd250_000_000) begin
                            next_state = S_EW_YELLOW;
                            timer_reset = 1;
                        end
            S_EW_YELLOW: if (timer >= 20'd25_000_000) begin
                            next_state = S_NS_GREEN;
                            timer_reset = 1;
                        end
            S_NS_GREEN: if (timer >= 20'd250_000_000) begin
                            next_state = S_NS_YELLOW;
                            timer_reset = 1;
                        end
            S_NS_YELLOW: if (timer >= 20'd25_000_000) begin
                            next_state = S_EW_GREEN;
                            timer_reset = 1;
                        end
        endcase
    end

    // 输出（组合）
    always @(*) begin
        lights_ew = 3'b000;   // 默认全灭
        lights_ns = 3'b000;
        case (state)
            S_EW_GREEN:  lights_ew = 3'b001;
            S_EW_YELLOW: lights_ew = 3'b010;
            S_NS_GREEN:  begin lights_ew = 3'b100; lights_ns = 3'b001; end
            S_NS_YELLOW: begin lights_ew = 3'b100; lights_ns = 3'b010; end
            default:     begin lights_ew = 3'b100; lights_ns = 3'b100; end
        endcase
    end
endmodule
```

### 3.4 `lfsr_8.v`（伪随机数）

```verilog
module lfsr_8 (
    input             clk, reset,
    output reg [7:0]  q
);
    always @(posedge clk, posedge reset)
        if (reset) q <= 8'h01;
        else       q <= {q[6:0], q[7] ^ q[5] ^ q[4] ^ q[3]};  // 反馈
endmodule
```

---

## 4. Testbench

测试寄存器堆要写**两个端口同时读**：

```verilog
module tb_regfile;
    reg        clk = 0, we3;
    reg  [4:0] ra1, ra2, wa3;
    reg  [31:0] wd3;
    wire [31:0] rd1, rd2;

    regfile_32x32 uut (
        .clk(clk), .we3(we3),
        .ra1(ra1), .ra2(ra2), .wa3(wa3), .wd3(wd3),
        .rd1(rd1), .rd2(rd2)
    );

    always #5 clk = ~clk;   // 100 MHz

    initial begin
        we3 = 0;
        // 写 $t0 = 0x12345678
        @(negedge clk);
        we3 = 1; wa3 = 5'd8; wd3 = 32'h12345678;
        @(negedge clk);
        we3 = 0;

        // 读 $t0
        ra1 = 5'd8; ra2 = 5'd0;  // 读 $t0 和 $zero
        @(negedge clk);
        $display("$t0 = %h (expected 12345678)", rd1);
        $display("$zero = %h (expected 0)", rd2);

        $finish;
    end
endmodule
```

---

## 5. 常见坑

### 坑 1：寄存器堆写同步、读异步搞反

```verilog
always @(*) rf[wa3] <= wd3;   // ❌ 组合写：会变成锁存器
```

→ **写必须 `posedge clk`**，读可以异步（单周期 CPU 需要）。

### 坑 2：FSM 忘记 reset 默认状态

```verilog
always @(posedge clk, posedge reset)
    if (reset) state <= ??;   // ❌ 必须明确写
```

→ **状态机必须有 reset 后的明确初始状态**，否则综合后上电是 X（不确定）。

### 坑 3：Mealy 机的 glitch

Mealy FSM 输出可能产生**毛刺**（短暂错误值）——在状态转移瞬间。
解决：用 Moore，或加输出寄存器。

### 坑 4：寄存器堆 `$zero` 没特殊处理

```verilog
assign rd1 = rf[ra1];   // ❌ 读 ra1=0 时会读到非法值
```

→ **必须显式特殊处理 ra1 == 0**。

### 坑 5：阻塞 vs 非阻塞混用

```verilog
always @(posedge clk) begin
    state <= next_state;   // ✅ 非阻塞
    if (something) a = b;  // ❌ 阻塞
end
```

→ **同一个时序 always 块必须全部用 `<=`**。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Nand2Tetris/Project_03`](../../Nand2Tetris/Project_03_SequentialLogic/) 的对照

| 方面 | Nand2Tetris 时序 | DDCA L04 |
|------|------------------|----------|
| 寄存器 | 16 位 Register | 32 位 × 32 个寄存器堆 |
| RAM | 16K × 16 | 不在 L04 范围（L07 才做）|
| PC | 16 位 | 32 位 + MIPS PC+4 |
| FSM | 不学 | **红绿灯 FSM（核心）** |
| 写法 | HDL 结构化 | Verilog 行为级 |

### 6.2 与 [`Lab04_超标量乱序`](../../Lab04_超标量乱序/) 的对照

L04 的 regfile 是**经典寄存器堆**（写同步读异步）。
飞腾的真机 regfile 复杂得多：
- 32 个 ISA 可见寄存器 → 重命名为几百个**物理寄存器**
- 多读多写（4-wide issue 需要 8 读 4 写端口）
- 配 ROB + Issue Queue 实现 OoO

→ [`Lab04`](../../Lab04_超标量乱序/) 用 PMU 反推这些工业级特性。

### 6.3 与 [`Expert_03_HW_Designer/rtl/two_bit_predictor.v`](../../Expert_03_HW_Designer/rtl/) 的连接

`two_bit_predictor.v` 是一个 **2 状态 FSM**：
- S0（强不跳）/ S1（弱不跳）/ S2（弱跳）/ S3（强跳）
- 这是分支预测器的核心

→ 学完 L04 FSM 后直接读懂 Expert_03。

---

## 7. 扩展挑战

1. **优先级中断控制器**：用 FSM 实现可嵌套的中断处理
2. **流水化寄存器堆**：把读也变成同步（流水化），对比 IPC 影响
3. **多端口寄存器堆**：8 读 4 写（4-wide 超标量所需）—— 难度跳跃
4. **CAM（Content-Addressable Memory）**：用于全关联 Cache

---

## 8. 检查清单

- [ ] 寄存器堆读写正确，`$zero` 特殊处理
- [ ] PC 能 +4、能跳转、能分支
- [ ] FSM 能正确状态转移
- [ ] 用 testbench 验证时序波形

---

## 📌 下一步

完成 L04 后，**DDCA 的硬件基础就齐了**——
[`Lab_05_SingleCycle_MIPS/`](../Lab_05_SingleCycle_MIPS/) 是高潮：
你将把 L01-L04 的所有部件拼成**一台完整的 MIPS CPU**。
