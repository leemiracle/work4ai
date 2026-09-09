# Nand2Tetris 工具链使用指南

> 本文件汇总 12 个 project 所需的全部工具链（官方 + 替代品 + 本项目集成）。

---

## 1. 官方工具（必备）

### 1.1 下载

**主入口**：[nand2tetris.org/software](https://www.nand2tetris.org/software)

- 软件包名：`nand2tetris.zip`（约 5 MB）
- 免安装（绿色软件）
- 依赖：**Java 11+**（推荐 17 LTS）

### 1.2 解压后目录结构

```
nand2tetris/
├── tools/
│   ├── bin/
│   │   ├── HardwareSimulator.sh / .bat       ← P01-P03, P05
│   │   ├── CPUEmulator.sh / .bat             ← P04, P05
│   │   ├── VMEmulator.sh / .bat              ← P07-P12
│   │   ├── JackCompiler.sh / .bat            ← 官方参考
│   │   └── TextComparer.sh / .bat            ← 对比输出
│   ├── builtInVMCode/                        ← VMEmulator 启动时加载的标准库
│   │   ├── Sys.vm
│   │   ├── Math.vm
│   │   ├── String.vm
│   │   ├── Array.vm
│   │   ├── Memory.vm
│   │   ├── Output.vm
│   │   ├── Screen.vm
│   │   └── Keyboard.vm
│   └── OS/                                   ← Jack 源码版标准库（P12 参考）
├── projects/
│   ├── 01/                                   ← P01 测试脚本
│   ├── 02/                                   ← P02 测试脚本
│   ├── ... 12/
└── README.md
```

### 1.3 5 个核心工具

| 工具 | 用途 | 用于 Project | 关键操作 |
|------|------|-------------|---------|
| **HardwareSimulator** | 加载 `.hdl`，跑 `.tst` | P01, P02, P03, P05 | `Load Chip` / `Load Script` / Ctrl-R |
| **CPUEmulator** | 加载 `.hack`，跑 Hack 程序 | P04, P05 | `Load Program` / F5 单步 / Ctrl-R 跑完 |
| **VMEmulator** | 加载 `.vm`，跑 VM bytecode | P07-P12 | `Load Program`（目录或文件）/ 动画速度 |
| **JackCompiler** | 把 `.jack` 翻译为 `.vm` | 官方参考 | `JackCompiler.sh dirname/` |
| **TextComparer** | 比较输出与期望 | 所有 | `TextComparer.sh out.cmp got.txt` |

### 1.4 启动方式

```bash
# Linux/Mac
cd nand2tetris/tools/bin
sh HardwareSimulator.sh

# Windows
HardwareSimulator.bat
```

> 💡 **首次启动可能要等 5–10 秒**（Java 加载）。CPU 模拟器加载 VM 标准库也需要时间。

---

## 2. 替代工具（可选）

### 2.1 在线 Web IDE（无需安装）

**入口**：[nand2tetris.github.io/web-ide](https://nand2tetris.github.io/web-ide)

- 浏览器即开即用
- 支持全部 12 个 project
- 适合不想装 Java 的初学者
- 但**功能略少于桌面版**（如不能跑大型 Jack 程序）

### 2.2 用 Verilog 重写（结合本项目 Expert_03）

如果你想顺便学工业 Verilog，可以用 iverilog + 自写 Verilog 版本：

```bash
# 用 iverilog 编译
cd Expert_03_HW_Designer/rtl/
iverilog -o tb_alu tb_alu.v alu.v
vvp tb_alu
```

→ 见 [`Expert_03_HW_DesignER/rtl/`](../../Expert_03_HW_Designer/rtl/) 的 `alu.v` / `forwarding_unit.v` / `two_bit_predictor.v`。

### 2.3 Python 重写 HDL 模拟器（极客向）

如果你想多写一个项目，可以用 Python 自己实现 HardwareSimulator：
- 解析 `.hdl` 文件
- 实现组合电路 + 时序电路模拟
- 跑 `.tst` 测试脚本

→ 这是 Nand2Tetris 的"第 13 个 project"，完成难度堪比 P12。

---

## 3. 本项目集成

### 3.1 与本项目 [`Lab00`–`Lab07`](../) 的工具集

| Lab | 工具 | 与 Nand2Tetris 关系 |
|-----|------|---------------------|
| Lab00 | `arch_probe`, `null_loop`（C 程序 + perf）| 跟 Nand2Tetris 的 HardwareSimulator 是两个极端 |
| Lab01 | `gcc`, `objdump` | 与 Nand2Tetris P06（汇编器）反向：一个汇编、一个反汇编 |
| Lab02 | perf + branch counters | P05 的 PC vs 飞腾的 PC + 分支预测器 |
| Lab03 | perf + cache counters | P03 的 RAM vs 飞腾的 L1/L2/L3/DRAM |
| Lab04 | perf + PMU | P05 的单周期 vs 飞腾的乱序 + 重命名 |
| Lab05 | perf + SIMD counters | P02 的标量 ALU vs 飞腾的 NEON SIMD |
| Lab06 | perf + memory barriers | P12 的单线程 OS vs 飞腾的多核并发 |
| Lab07 | perf + crypto counters | P12 的 `Math.multiply` vs 飞腾的 SM 硬件加速 |

### 3.2 与本项目 [`Capstone/cpu_simulator`](../../Capstone/cpu_simulator/) 的关系

Capstone 的 `rv32i_sim.py` 是 RV32I 5 级流水线模拟器，**与 Nand2Tetris 的 HardwareSimulator 互补**：

| 方面 | HardwareSimulator | `rv32i_sim.py` |
|------|-------------------|----------------|
| 语言 | Java | Python |
| ISA | Hack（自定义）| RV32I（RISC-V）|
| 流水线 | 单周期 | 5 级（IF/ID/EX/MA/WB）|
| 时钟可视化 | ❌ | ✅ |
| 测试数 | nand2tetris 官方 | 77 个 pytest |
| 跑 Hack 程序 | ✅ | ❌ |
| 跑 RISC-V 程序 | ❌ | ✅ |

→ **做完 Nand2Tetris 后做 Capstone**，会有"从教学级到研究级"的清晰跨度。

---

## 4. 常用调试技巧

### 4.1 HardwareSimulator 调试 HDL

```tst
// 设置断点式调试：在 .tst 文件里加 output 看每拍状态
load CPU.hdl,
output-list pc A D RAM[0] RAM[1];
set pc 0, tick, tock, output;        // 看第 1 拍状态
set pc 1, tick, tock, output;
```

### 4.2 CPUEmulator 调试 Hack 程序

- F5：单步执行
- F8：跳到 ROM 中的特定地址
- View → RAM：查看任意 RAM 地址的值
- View → Screen：可视化屏幕

### 4.3 VMEmulator 调试 VM 程序

- 加载 `.vm` 文件（或整个目录）
- View → Stack：实时看栈状态
- View → Heap：看对象分配
- Speed → Slow：动画模式（推荐初次调试用）

### 4.4 在 Python 翻译器里加 print

```python
def translate(self, vm_line: str):
    print(f'[DEBUG] VM: {vm_line}', file=sys.stderr)
    ...
    for line in self.output[-10:]:
        print(f'    {line}', file=sys.stderr)
```

---

## 5. 性能与限制

| 工具 | 典型性能 | 限制 |
|------|---------|------|
| HardwareSimulator | 每秒 ~10K 拍 | Hack CPU 仿真（不能跑真实 Hack 硬件）|
| CPUEmulator | 每秒 ~100K 指令 | ROM 32K × 16 bit 上限 |
| VMEmulator | 每秒 ~10K VM 指令 | RAM 32K（含屏幕+键盘）|
| JackCompiler | 瞬时 | 单文件或单目录，无链接器 |
| `rv32i_sim.py` | 每秒 ~10K 指令 | 教学，无 MMU/中断/异常 |

→ **所有工具都是教学级**，不适合跑性能基准。
真要看工业级性能，**必须用飞腾真机 + perf**（[`Lab00`](../../Lab00_测量基础设施/)）。

---

## 6. 故障排除

### 6.1 Java 没装

```
Error: Java not found
```

→ 安装 [JDK 17 LTS](https://adoptium.net/)，重新打开终端。

### 6.2 中文路径

某些 Java 工具在中文路径下不工作：
```
# ❌ 错
/home/用户/我的文档/nand2tetris/

# ✅ 对
/home/user/work/nand2tetris/
```

→ 把 nand2tetris 放在**纯英文路径**下。

### 6.3 文件编码

`.hdl` / `.tst` / `.asm` 必须是 UTF-8 或 ASCII。
Windows 记事本默认可能是 UTF-16，要在另存为里改。

### 6.4 浮点数不支持

Hack CPU 是 16 位整数，**没有浮点**。
所有"看起来像浮点"的运算都要用定点（如 ×1024 表示小数）。

### 6.5 VMEmulator 加载 Jack 项目失败

需要先**用 JackCompiler 把 `.jack` 翻译为 `.vm`**：
```bash
JackCompiler.sh Pong/
# 然后在 VMEmulator 里 Load Program: Pong/  （整个目录）
```

---

## 📌 下一步

按 [`Nand2Tetris/README.md`](../README.md) §6 的路径选择一个起点，开始你的 12 个 project 之旅！
