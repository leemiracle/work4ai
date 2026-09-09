# Lab 07 — Memory & I/O：实现 Cache 与简单 I/O

> **一句话目标**：在 L06 流水线 MIPS 上加 **直接映射 Cache** + **内存映射 I/O**——
> 这是真实 CPU 与外部世界交互的基础。

---

## 0. 对应资源

| 资源 | 位置 |
|------|------|
| 📘 书 | Harris & Harris **Ch8 §8.1-8.3**（Cache + 虚拟内存基础）|
| 🎥 Mutlu | [Lecture 16-18: Memory Systems](https://www.youtube.com/playlist?list=PL5Q2soXY2Zi_FRrj0UE0HHTiii6eDm4M5) |
| ⏱ 预计工时 | 15–25 小时 |

---

## 1. 你将构建的两个模块

| # | 模块 | 功能 | 难度 |
|---|------|------|------|
| 1 | `dcache_direct_mapped` | 8 KB 直接映射 L1 D-Cache（4 字节块，2 路可选）| ⭐⭐⭐ |
| 2 | `mmio_uart` | 简单 UART 发送（内存映射）| ⭐⭐ |

---

## 2. 关键概念

### 2.1 为什么需要 Cache？

```
CPU 速度 vs DRAM 速度（按 MIPS 简化）：
CPU: 1 GHz（1 ns/拍）
L1 Cache: 1-2 拍（1-2 ns）
L2 Cache: 10 拍（10 ns）
L3 Cache: 30-50 拍
DRAM: 100-300 拍（100-300 ns）
```

→ **CPU 与 DRAM 速度差距 ~100 倍**，没有 Cache，CPU 几乎所有时间都在等内存。

### 2.2 局部性原理

- **时间局部性**：刚用过的数据很可能再用（循环）
- **空间局部性**：邻近的数据很可能一起用（数组）

Cache 把"常用的数据"缓存到 SRAM，让 CPU 大多数访问只等 1-2 拍。

### 2.3 直接映射 Cache 结构

```
地址拆分（32 位地址）：
┌────────────┬──────────┬──────┐
│   Tag      │  Index   │ Offset│
└────────────┴──────────┴──────┘

例：8KB Cache，4 字节块
- Offset: 2 位（4 字节）
- Index:  11 位（8KB / 4 = 2K = 2^11 行）
- Tag:    19 位
```

```
Cache 行结构：
┌──────┬─────┬──────────┐
│Valid │ Tag │  Data    │
│  1   │ 19  │  32 bit  │
└──────┴─────┴──────────┘
```

### 2.4 内存映射 I/O

FPGA 板的外设（七段、按钮、UART）映射到特定内存地址：

```
0xFFFF0000 → 七段数码管
0xFFFF0010 → 按钮
0xFFFF0020 → UART 数据寄存器
0xFFFF0024 → UART 状态寄存器
```

CPU 用 `sw` / `lw` 访问这些地址，硬件根据地址解码到对应外设。

---

## 3. Verilog 实现

### 3.1 直接映射 Cache

```verilog
module dcache_direct_mapped (
    input             clk, reset,
    input             cpu_req,    // CPU 发起读
    input  [31:0]     cpu_addr,
    output [31:0]     cpu_data,
    output            cpu_ready,  // 1 = 命中，0 = miss
    // 主存接口
    output            mem_req,
    output [31:0]     mem_addr,
    input  [31:0]     mem_data,
    input             mem_ready
);
    // Cache 配置
    localparam NUM_LINES = 2048;     // 8 KB / 4 B = 2K 行
    localparam INDEX_BITS = 11;
    localparam TAG_BITS = 32 - INDEX_BITS - 2;  // 19

    // 存储体
    reg                 valid [NUM_LINES-1:0];
    reg [TAG_BITS-1:0]  tag   [NUM_LINES-1:0];
    reg [31:0]          data  [NUM_LINES-1:0];

    // 地址拆分
    wire [1:0]            offset = cpu_addr[1:0];
    wire [INDEX_BITS-1:0] index  = cpu_addr[INDEX_BITS+1:2];
    wire [TAG_BITS-1:0]   req_tag = cpu_addr[31:INDEX_BITS+2];

    // 命中判断
    wire hit = valid[index] && (tag[index] == req_tag);

    // 状态机（处理 miss）
    localparam S_IDLE = 0, S_MISS_REQ = 1, S_MISS_WAIT = 2, S_REFILL = 3;
    reg [2:0] state;

    always @(posedge clk, posedge reset) begin
        if (reset) begin
            state <= S_IDLE;
            // 清空 valid
        end else begin
            case (state)
                S_IDLE:
                    if (cpu_req && !hit) state <= S_MISS_REQ;
                S_MISS_REQ:
                    if (mem_ready) state <= S_REFILL;
                S_REFILL: begin
                    valid[index] <= 1'b1;
                    tag[index]   <= req_tag;
                    data[index]  <= mem_data;
                    state        <= S_IDLE;
                end
            endcase
        end
    end

    assign cpu_data  = data[index];
    assign cpu_ready = (state == S_IDLE) && (!cpu_req || hit);
    assign mem_req   = (state == S_MISS_REQ);
    assign mem_addr  = {cpu_addr[31:2], 2'b00};
endmodule
```

### 3.2 简单内存映射 I/O（七段显示）

```verilog
module mmio_segment (
    input         clk,
    input  [31:0] addr,
    input  [31:0] write_data,
    input         write_en,
    output        cs,                // chip select（地址 0xFFFF0000）
    output [6:0]  seg,
    output [3:0]  an                 // 4 位数字选择
);
    assign cs = (addr == 32'hFFFF0000) && write_en;

    reg [15:0] display_data;   // 4 位 16 进制数字

    always @(posedge clk)
        if (cs) display_data <= write_data[15:0];

    // 4 位数码管多路复用（每 1ms 切一个）
    reg [19:0] refresh_counter;
    always @(posedge clk) refresh_counter <= refresh_counter + 1;

    wire [1:0] active_digit = refresh_counter[19:18];   // 0-3 循环

    assign an = ~(1 << active_digit);   // 共阳，0 = 亮

    reg [3:0] current_digit;
    always @(*) begin
        case (active_digit)
            2'd0: current_digit = display_data[3:0];
            2'd1: current_digit = display_data[7:4];
            2'd2: current_digit = display_data[11:8];
            2'd3: current_digit = display_data[15:12];
        endcase
    end

    seg7_decoder seg_decoder (
        .hex_digit(current_digit),
        .seg(seg)
    );
endmodule
```

---

## 4. 测试：测 Cache 命中率

```mips
# 用一个 8KB 数组（等于 Cache 大小），看每次访问是否命中
.data
array:  .space 8192    # 8KB
.text
main:
    la   $t0, array
    li   $t1, 2048      # 2048 个 4 字节
loop:
    lw   $t2, 0($t0)
    addi $t0, $t0, 4
    addi $t1, $t1, -1
    bne  $t1, $zero, loop
```

**期望**：
- 第 1 次循环：每个 `lw` 都 miss（冷启动）
- 第 2 次循环：每个 `lw` 都命中（如果整个数组还在 Cache）

---

## 5. 常见坑

### 坑 1：直接映射 Cache 的冲突

如果两个常用变量的地址差正好是 8KB 的倍数，它们映射到同一 Cache 行，**互相刷**。

**解法**：用 2-way 或 4-way 组相联。

### 坑 2：Write Policy

- **Write-through**：写 Cache 同时写主存。简单但慢。
- **Write-back**：只写 Cache，主存等替换时才更新。复杂但快。

教学版用 write-through。

### 坑 3：MMIO 区域不能进 Cache

外设状态随时变化，**不能缓存**。
地址解码时要识别 MMIO 区域，绕过 Cache。

---

## 6. 与本项目其他模块的连接

### 6.1 与 [`Lab03_存储层次`](../../Lab03_存储层次/) 的连接

学完 L07 后看飞腾真机的 Cache 实测：

| 层级 | L07 Cache（你造的）| 飞腾 D3000M（`[实测]`）|
|------|---------------------|------------------------|
| L1 D | 8KB 直接映射 | **64KB / 4-way @ 1.61 ns** |
| L2 | 无 | **512KB / 8-way @ 4.78 ns** |
| L3 | 无 | **8MB shared @ 14 ns** |
| 写策略 | write-through | write-back + write-allocate |
| 替换策略 | 直接映射（无替换）| LRU pseudo |

→ [`Lab03`](../../Lab03_存储层次/) 用 perf + cache counters 实测这些。

### 6.2 与 [`Expert_04_OS_Kernel`](../../Expert_04_OS_Kernel/) 的连接

L07 的 MMIO 与飞腾真机的设备驱动是同一思想：
- 七段显示 ↔ MMIO 写 0xFFFF0000
- 键盘轮询 ↔ MMIO 读 0xFFFF0010
- 真实工业：MMIO 操作网卡、GPU、磁盘

---

## 7. 扩展挑战

1. **2-way 组相联**：减少冲突 miss
2. **Write-back**：实现脏位 + 替换时回写
3. **Cache Line 增大**：从 4 字节扩到 32/64 字节（提升空间局部性）
4. **预取**：在 CPU 之前提前取下一行
5. ** Victim Cache**：减少冲突 miss

---

## 8. 检查清单

- [ ] 直接映射 Cache 实现 + 测试
- [ ] 命中率正确反映局部性
- [ ] MMIO 七段显示能亮数字
- [ ] Cache miss 时正确 stall CPU

---

## 📌 下一步

进 [`Lab_08_Exceptions/`](../Lab_08_Exceptions/) 加异常处理。
