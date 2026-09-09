# Lab 08 — Exceptions & Interrupts：让 CPU 能响应外部事件

> **一句话目标**：在 L06 流水线 MIPS 上加 **异常/中断处理机制**——
> syscall、overflow、外部中断都能被正确捕获和分发。
> **这是从"CPU"到"OS 平台"的关键一步**。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch7 §7.7.3**（Exceptions）|
| 🎥 Mutlu | [Lecture 19: Exceptions & Interrupts](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 15–20 小时 |

---

## 1. 你将构建的机制

| # | 异常类型 | 触发 | 处理 |
|---|---------|------|------|
| 1 | `syscall` | 软件指令 | 跳到 0x80000180 |
| 2 | `overflow` | ALU 算术溢出 | 同上 |
| 3 | `undefined instruction` | 非法 op | 同上 |
| 4 | `external interrupt` | 外部信号（定时器/键盘）| 同上 |

---

## 2. 关键概念

### 2.1 异常 vs 中断

- **异常（Exception）**：CPU 内部触发（syscall、overflow、非法指令、对齐错误）
- **中断（Interrupt）**：外部触发（定时器、键盘、网卡、磁盘）

两者都用相同的处理机制（MIPS 统称"异常"）。

### 2.2 MIPS 异常处理流程

```
异常触发时：
1. 保存当前 PC 到 EPC（Exception Program Counter）
2. 设置 Cause 寄存器（异常类型 + 编号）
3. 把 Status.EXL（异常级别）置 1
4. PC 跳到 0x80000180（异常向量地址）
```

### 2.3 关键 CP0 寄存器

MIPS 用协处理器 0（CP0）维护异常状态：

| 寄存器 | 名字 | 用途 |
|--------|------|------|
| `$12` | Status | 全局中断使能（IE）+ 异常级（EXL）|
| `$13` | Cause | 异常原因（ExcCode 字段）|
| `$14` | EPC | 异常发生时的 PC |
| `$8`  | BadVAddr | 引起地址错误的目标地址 |

### 2.4 异常返回

```mips
eret    # 异常返回
        # 1. PC ← EPC
        # 2. Status.EXL ← 0（退出异常级）
```

---

## 3. Verilog 实现

### 3.1 在流水线中加入异常检测

```verilog
module exception_unit (
    // 触发源
    input             ex_alu_overflow,      // EX 阶段算术溢出
    input             id_undefined_instr,   // ID 阶段非法指令
    input             id_syscall,           // ID 阶段 syscall
    input             ext_interrupt,        // 外部中断

    // 控制
    input             status_ie,            // 全局中断使能
    input             status_exl,           // 当前已在异常级
    output            exception_taken,
    output [4:0]      cause_code,
    output [31:0]     epc_value,            // 要存到 EPC 的值
    output [31:0]     exception_pc          // 异常向量（0x80000180）
);
    // 异常优先级（高 → 低）：
    // 1. 外部中断（最低优先级，但只有 IE=1 且 EXL=0 才响应）
    // 2. undefined instruction
    // 3. overflow
    // 4. syscall

    wire external_active = ext_interrupt & status_ie & ~status_exl;

    assign exception_taken = ex_alu_overflow | id_undefined_instr |
                             id_syscall | external_active;

    assign cause_code =
        external_active        ? 5'b00000 :  // Int
        id_undefined_instr     ? 5'b01010 :  // RI
        ex_alu_overflow        ? 5'b01100 :  // Ov
        id_syscall             ? 5'b01000 :  // Sys
                                5'b00000;

    assign exception_pc = 32'h80000180;
    assign epc_value    = /* 取决于异常类型，一般是当前 PC */;
endmodule
```

### 3.2 修改 PC + Cause + EPC + Status 寄存器

需要在 `mips_top` 里加：

```verilog
// CP0 寄存器
reg [31:0] epc, cause, status;

// 异常时
always @(posedge clk, posedge reset)
    if (reset) begin
        status <= 32'h00000000;   // EXL=0, IE=0
        epc    <= 32'h00000000;
        cause  <= 32'h00000000;
    end else if (exception_taken) begin
        epc    <= epc_value;
        cause  <= {cause_code, 27'b0};
        status[1] <= 1'b1;   // EXL=1
    end else if (eret_instr) begin
        status[1] <= 1'b0;   // EXL=0
    end

// PC 跳转
always @(posedge clk)
    if (exception_taken)
        pc <= 32'h80000180;
    else if (eret_instr)
        pc <= epc;
    else
        pc <= normal_next_pc;
```

### 3.3 syscall 程序示例

```mips
# 用 syscall 打印 "Hello"
.data
msg: .asciiz "Hello\n"
.text
main:
    la   $v0, 1             # syscall 编号 1 = print_string
    la   $a0, msg
    syscall                 # 触发异常 → 跳到 OS handler
    li   $v0, 10            # syscall 10 = exit
    syscall

# OS handler（地址 0x80000180）
    .ktext 0x80000180
handler:
    mfc0 $k0, $13           # Cause
    andi $k0, $k0, 0x1F     # ExcCode
    beq  $k0, 8, do_syscall # syscall
    ...
do_syscall:
    # 根据 $v0 选择操作
    ...
    eret                    # 返回
```

---

## 4. 测试

### 4.1 触发 overflow

```mips
li   $t0, 0x7FFFFFFF
add  $t1, $t0, $t0    # 溢出！跳到 0x80000180
addi $t2, $zero, 999  # 不该执行到这里
```

### 4.2 触发外部中断

Vivado 仿真里可以**模拟按键**：

```verilog
// testbench
initial begin
    // ... 跑一段程序 ...
    #1000;
    irq = 1;   #10;   // 触发外部中断
    irq = 0;
end
```

---

## 5. 常见坑

### 坑 1：异常时流水线没刷干净

如果异常在 EX 阶段触发，但 IF/ID 和 ID/EX 里有未完成指令——
**必须 flush 整个流水线**，否则错误指令会写状态。

### 坑 2：EPC 保存的 PC 错了

对于不同异常类型，EPC 应该保存的 PC 不同：
- syscall：保存当前指令 PC
- overflow：保存当前指令 PC
- 外部中断：保存**下一条** PC（中断是异步的）

### 坑 3：异常嵌套没处理

异常里又触发异常怎么办？
MIPS 用 `Status.EXL` 标志位——**异常级时屏蔽所有中断**。

### 坑 4：eret 没恢复 Status

`eret` 必须把 `Status.EXL` 清零，否则后续中断永远不响应。

### 坑 5：异常的精确性

**MIPS 要求精确异常**（Precise Exceptions）——异常指令之前的指令全部完成，之后的指令像没执行过一样。
**乱序 CPU（飞腾）实现这个非常复杂**（需要 ROB 按序提交）。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/) 的连接

L08 的异常处理 = OS 内核的入口机制。
飞腾真机的 Linux 内核运行时：

| 异常类型 | L08 MIPS（你造的）| 飞腾 + Linux（实测）|
|---------|------------------|---------------------|
| syscall | 跳 0x80000180 | 跳 `el0_sync`（[`Expert_04`](../../Expert_04_OS_Kernel/)）|
| Page fault | 无（L08 不做虚拟内存）| 触发 do_page_fault |
| IRQ | 跳 0x80000180 | GIC → `gic_handle_irq` |
| Timer | 无 | `arch_timer_handler` |

→ [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/) 实测 syscall 延迟（syscall_bench.c），
这是 L08 思想的工业实现。

### 6.2 与 [`Lab02_流水线与ILP`](../../Lab02_流水线与ILP/) 的连接

L08 的异常**精确性**是流水线 CPU 的难点——
飞腾用**ROB 按序提交**保证精确异常（[`Lab04`](../../Lab04_超标量乱序/)）。

---

## 7. 扩展挑战

1. **加虚拟内存**：在 dcache 前加 MMU + TLB + 页表
2. **加 nested exception**：在异常级里允许更高优先级异常（Status.EXL 联合 Status.IE）
3. **加 NMI**（Non-Maskable Interrupt）：不可屏蔽中断
4. **加 watchdog**：定时器中断 + 看门狗重置

---

## 8. 检查清单

- [ ] syscall 触发后正确跳到 0x80000180
- [ ] overflow 被检测
- [ ] 外部中断在 IE=1 时被响应
- [ ] 异常返回 eret 正确恢复
- [ ] 精确异常保证（前面的指令都完成）

---

## 📌 下一步

进 [`Lab_09_Capstone_FPGA/`](../Lab_09_Capstone_FPGA/)——
把整套 MIPS CPU 烧到真实 FPGA 板，**用按钮控制 CPU，看七段显示**。
