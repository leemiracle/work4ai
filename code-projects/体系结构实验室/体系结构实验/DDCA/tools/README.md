# DDCA 工具链使用指南

> Verilog 仿真 + 综合工具 + FPGA 板使用大全。

---

## 1. 开源工具链（必备）

### 1.1 Icarus Verilog (iverilog)

最流行的开源 Verilog 仿真器。

**安装**：
```bash
# Ubuntu/Debian
sudo apt install iverilog

# macOS
brew install icarus-verilog

# Windows
# 下载 https://bleyer.org/icarus/ 安装
```

**使用**：
```bash
# 编译（多个文件一起）
iverilog -o sim.out rtl/mips_alu.v tb/tb_mips_alu.v

# 运行
vvp sim.out

# 看输出
# PASS: ADD = 8
# ✅ All tests passed!
```

**常用选项**：
- `-g2012`：启用 SystemVerilog 2012 语法
- `-Wall`：所有警告
- `-o OUT`：输出文件名

### 1.2 GTKWave（波形查看器）

```bash
# 在 testbench 里加：
initial begin
    $dumpfile("waves.vcd");
    $dumpvars(0, tb_mips_alu);
end

# 跑仿真后
gtkwave waves.vcd
```

**GTKWave 操作**：
- 左侧信号列表 → 双击或拖到右侧
- `+`/`-` 缩放
- 鼠标滚轮平移
- `Ctrl-S` 保存波形配置

### 1.3 Verilator（高速替代）

iverilog 慢（每秒 ~10K 拍）。Verilator 把 Verilog 编译成 C++，**快 100 倍**。

```bash
# 安装
sudo apt install verilator

# 编译
verilator --cc --exe --build rtl/mips_top.v tb/tb_mips.cpp

# 跑
./obj_dir/Vmips_top
```

→ **L05/L06 的复杂 CPU 推荐用 Verilator**（iverilog 跑长测试要几小时）。

### 1.4 Yosys（开源综合）

把 Verilog 综合到门级网表或 FPGA 比特流：

```bash
sudo apt install yosys

# 综合
yosys -p "synth_ice40 -top mips_top -json mips.json" rtl/*.v

# 看综合后的电路图
yosys -p "show mips_top" rtl/*.v
```

---

## 2. 商业工具（学校常有 license）

### 2.1 Vivado（Xilinx）

**用于**：L09 FPGA 综合 + 烧录

**下载**：[Xilinx Vivado](https://www.xilinx.com/support/download.html)（约 50 GB，学校 license 可免费）

**主要功能**：
- Synthesis：Verilog → 门级网表
- Implementation：布局布线
- Bitstream Generation：生成 .bit 文件
- Hardware Manager：烧到 FPGA 板
- Integrated Logic Analyzer (ila)：板级调试

**教学替代**：WebPACK 版（免费，但只能用小芯片如 Artix-7）。

### 2.2 ModelSim / QuestaSim

行业标准 HDL 仿真器（比 iverilog 快 5-10 倍）。

**ETH 提供**：通过学校课程可获取。

### 2.3 Quartus Prime（Intel/Altera）

如果你用 Intel FPGA 板（如 DE10-Lite），用 Quartus 替代 Vivado。

---

## 3. MIPS 汇编器

DDCA lab 需要把 MIPS 汇编编译成机器码（.hex 文件）。

### 3.1 MARS（推荐教学）

[MARS (MIPS Assembler and Runtime Simulator)](https://courses.missouristate.edu/KenVollmar/MARS/)

- Java 写的，跨平台
- 有 GUI，可视化寄存器/内存
- 可生成机器码供 Verilog 用

**导出 .hex 文件**：
1. File → Open 你的 .asm 文件
2. Run → Assemble
3. File → Dump Memory → 选 .text → 格式选 Hexadecimal → 保存

### 3.2 SPIM

[SPIM](https://sourceware.org/spim/)：经典 MIPS 模拟器。

### 3.3 GNU as（gas）

```bash
# 安装
sudo apt install binutils-mips-linux-gnu

# 汇编
mips-linux-gnu-as -o test.o test.asm
mips-linux-gnu-objcopy -O binary test.o test.bin

# 转 hex
xxd -p test.bin > test.hex
```

---

## 4. FPGA 板使用

### 4.1 Nexys 4 DDR（推荐）

| 特性 | 详情 |
|------|------|
| 芯片 | Xilinx Artix-7 XC7A100T |
| 资源 | 101K logic cells, 4.86Mb BRAM, 240 DSP |
| 时钟 | 100 MHz 单端 |
| 外设 | 16 switches, 5 buttons, 16 LEDs, 8 七段, VGA, USB-UART, Mic, Accel, Temp |
| 价格 | ~$270（学校课程常免费提供）|
| 购买 | [Digilent](https://store.digilentinc.com/nexys-4-ddr-artix-7-fpga-trainer-board-recommended-for-ece-curriculum/) |

### 4.2 Basys 3（便宜版）

| 特性 | 详情 |
|------|------|
| 芯片 | Artix-7 XC7A35T |
| 资源 | 33K logic cells（Nexys 的 1/3）|
| 价格 | ~$150 |

### 4.3 Tang Primer 20K（开源国产）

| 特性 | 详情 |
|------|------|
| 芯片 | Anlogic EG20K（200K logic cells）|
| 价格 | ~$50 |
| 工具 | 开源 Yosys + nextpnr |

→ 国产板便宜，但**配套教程少**，不推荐初学者。

### 4.4 烧录流程

1. USB 连接板子（板上 USB-JTAG 口）
2. 电源开关拨到 ON
3. Vivado → Open Hardware Manager → Auto Connect
4. 看到 `xc7a100t_0` 表示连上
5. Program Device → 选 .bit 文件 → Program
6. 板子开始按你的 Verilog 工作

---

## 5. 常用 Makefile 模板

每个 Lab 都用类似的 Makefile：

```makefile
# Makefile for DDCA Lab XX

RTL_DIR = rtl
TB_DIR  = tb
SIM_DIR = sim

RTL_FILES = $(wildcard $(RTL_DIR)/*.v)
TB_FILES  = $(wildcard $(TB_DIR)/*.v)

# 默认：编译所有 testbench 并跑
all: $(SIM_DIR) compile test

$(SIM_DIR):
	mkdir -p $(SIM_DIR)

compile:
	for tb in $(TB_FILES); do \
		name=$$(basename $$tb .v); \
		iverilog -o $(SIM_DIR)/$$name.out $(RTL_FILES) $$tb; \
	done

test:
	for sim in $(SIM_DIR)/*.out; do \
		echo "=== Running $$sim ==="; \
		vvp $$sim; \
	done

# 跑特定模块
run-%:
	iverilog -o $(SIM_DIR)/$*.out $(RTL_FILES) $(TB_DIR)/tb_$*.v
	vvp $(SIM_DIR)/$*.out

# 看波形
wave-%:
	gtkwave $(SIM_DIR)/$*.vcd &

# 清理
clean:
	rm -rf $(SIM_DIR)

.PHONY: all compile test clean
```

使用：
```bash
make           # 跑所有 testbench
make run-mips_alu   # 跑 mips_alu
make wave-mips_alu  # 看波形
make clean
```

---

## 6. 与本项目其他工具链的对照

| 工具 | 仿真层级 | 项目里对应 |
|------|---------|-----------|
| iverilog | L2（RTL）| [`Expert_03/rtl/`](../../Expert_03_HW_DesignER/rtl/) |
| Verilator | L2（高速）| [`Capstone/cpu_simulator`](../../Capstone/cpu_simulator/)（Python）|
| Vivado | L1-L2（可综合）| — |
| nand2tetris HardwareSimulator | L2（教学）| [`Nand2Tetris`](../../Nand2Tetris/) |
| perf + PMU | L1-L5 | [`Lab00-Lab07`](../../) |

---

## 7. 故障排除

### Q1：iverilog 报 `Unknown module`
```
tb_mips_alu.v:5: error: Unknown module type: mips_alu
```

→ 把所有 RTL 文件一起编译：`iverilog -o sim rtl/*.v tb/tb_*.v`

### Q2：GTKWave 看不到波形

→ testbench 必须加 `$dumpvars`：
```verilog
initial begin
    $dumpfile("waves.vcd");
    $dumpvars(0, tb_xxx);   // 0 = 全部 depth
end
```

### Q3：Vivado 找不到板

→ 看 USB 线是不是数据线；板上 jumper J6 在 JTAG 模式。

### Q4：综合时 timing 不达标

→ 看 timing report，找最长的关键路径。常见解法：
- 流水化（拆成多级）
- 用更快的器件
- 优化 RTL（少用 `*` `/` `%`）

### Q5：烧上去不工作

→ 用 Integrated Logic Analyzer（ila）抓波形：
```verilog
ila_0 your_ila (.clk(clk), .probe0(signal_to_watch));
```

---

## 📌 下一步

按 [`DDCA/README.md`](../README.md) §6 的路径选一个起点开始。
