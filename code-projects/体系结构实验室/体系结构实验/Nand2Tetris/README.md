# Nand2Tetris：从一块 NAND 门到能跑俄罗斯方块的完整计算机

> **一句话定位**：你用 12 个 project，从**一个 NAND 门**开始，亲手构建出**一整台能跑俄罗斯方块的计算机**——
> 不用任何黑盒，每个抽象层都是你自己造的。
>
> 这是 Noam Nisan & Shimon Schocken 的 **"From Nand to Tetris"** 课程（2005 第 1 版，2021 第 2 版）
> 在中文世界的译名《计算机系统要素：从零开始构建现代计算机》。
>
> 它是**所有体系结构入门书单的常驻第一名**——因为它把"计算机是怎么从硅变成程序的"这件事，
> 用 12 步可执行的练习彻底打通。

---

## 0. 本目录在项目中的位置

本项目（飞腾 D3000M 体系结构实验）已有 **5 层结构**：

| 层 | 现有内容 | **本目录补的维度** |
|----|---------|-------------------|
| ① 思想母题 | [`Great_Ideas`](../背景知识/Great_Ideas_体系结构思想.md) + [`处理器分层模型`](../背景知识/处理器分层模型.md) | — |
| ② 实验观测层 | [`Lab00`–`Lab07`](../) — **用 perf 在真机上观测** | **本目录：用 HDL 自己造一台**（"观测"↔"构建" 对偶）|
| ③ 专家视角层 | [`Expert_01`–`Expert_23`](../) | — |
| ④ 异质透镜层 | [`Lenses/`](../Lenses/) | — |
| ⑤ 事实锚点层 | [`战略锚点.md`](../战略锚点.md) | — |

**Nand2Tetris 与 Lab/Capstone 的对偶关系**：

```
         ┌──────────────────────────────────────────────────┐
         │  Lab 00–07：用 perf + PMU 观测【飞腾真机】        │  自上而下
         │  ——这是真实工业 CPU（14nm、4-wide OoO、ARMv8.4-A）│  （已有）
         └──────────────────────────────────────────────────┘
                              ↕  对偶
         ┌──────────────────────────────────────────────────┐
         │  Capstone/cpu_simulator：Python 模拟【RV32I】     │  自中而内
         │  ——5 级流水线 + 77 测试用例                       │  （已有）
         └──────────────────────────────────────────────────┘
                              ↕  对偶
         ┌──────────────────────────────────────────────────┐
         │  Nand2Tetris：从 Nand 一路造到【俄罗斯方块】      │  自下而上
         │  ——教学级 CPU（Hack）+ 编译器 + OS + App          │  （本目录）
         └──────────────────────────────────────────────────┘
```

**三个层次的教学价值互补**：
- **Lab**：教你**看懂**真实工业 CPU 在干什么（perf 实测）
- **Capstone**：教你**模拟**一台精简 RISC CPU 的内部状态
- **Nand2Tetris**：教你**构建**一台计算机的全部抽象层（从硅到 App）

> 💡 **学习建议**：先做 Nand2Tetris 的 **P01-P06**（半年），再做本项目的 Lab00-Lab07（半年），
> 最后做 Capstone（一年）——三年走完，你已经具备了**所有体系结构领域**的扎实直觉。

---

## 1. 这门课/这本书是什么？

### 1.1 作者与起源

- **作者**：Noam Nisan（希伯来大学，理论计算机科学家）& Shimon Schocken（IDC Herzliya）
- **起源**：2000 年代初 Schocken 在 IDC 教体系结构课，发现学生只能背概念，于是和 Nisan 一起设计了"从零造一台"的课程
- **第一版**：2005，《The Elements of Computing Systems》（MIT Press）
- **第二版**：2021，更新了工具链、补了异步内容、加了云 IDE
- **课程**：[nand2tetris.org](https://www.nand2tetris.org/) + Coursera 两门课（Part I 硬件 / Part II 软件）
- **TED 演讲**：Shimon Schocken 2014 *The self-organizing computer course*（推荐先看，建立直觉）

### 1.2 核心哲学（一句话）

> **"Don't take anything on faith. Build every layer yourself, then nothing in computer science will ever feel like magic again."**
>
> —— 不要凭信仰接受任何事。每一层都自己造一遍，整个计算机科学从此再没有魔法。

### 1.3 为什么这门课有效

| 普通体系结构课 | Nand2Tetris |
|----------------|-------------|
| 老师画一张 CPU 框图，学生背下来 | 你用 HDL 把 CPU 拼出来，跑通自己的程序 |
| 老师讲"汇编器原理"，学生抄笔记 | 你用 Python 写一个汇编器，跑官方测试集 |
| 老师讲"编译器有前端后端"，学生抽象理解 | 你亲手写 tokenizer + parser + codegen |
| 一学期结束，记住一些名词 | 一年结束，**拥有一台完整的、自造的计算机** |

---

## 2. 12 个 Project 总览（一张图）

```
  ┌──────────────────────── Part I：硬件（书 Ch1–Ch6）────────────────────────┐
  │                                                                          │
  │  P01          P02          P03          P04          P05        P06      │
  │ 布尔逻辑  →  布尔算术  →  时序逻辑  →  机器语言  →  计算机架构  →  汇编器    │
  │ Nand门     半加器       DFF→Bit      Hack汇编    Hack CPU     Python    │
  │ Mux/DMux   全加器       Register     两段小程序   Memory       汇编器    │
  │            ★ALU★        RAM8/64/..   (手写汇编)   Computer.hdl           │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
                                          ↓ 你的硬件能跑 Hack 程序了
  ┌──────────────────────── Part II：软件（书 Ch7–Ch12）──────────────────────┐
  │                                                                          │
  │  P07          P08          P09          P10         P11         P12      │
  │ VM翻译器  →  VM翻译器   → 高级语言   → 编译器I   → 编译器II  →  OS       │
  │  (栈)        (完)         Jack        前端         后端       (Jack)    │
  │ push/pop   goto/if       写一个      Tokenizer   生成VM      Math      │
  │ add/sub    call/return   App         Parser                  String    │
  │                                                                          │
  └──────────────────────────────────────────────────────────────────────────┘
                                          ↓ 你的 OS 能跑 Jack 应用了
                              🎉 你的俄罗斯方块能跑了 🎉
```

### 2.1 全表：12 个 Project 一览

| # | 名称 | 你将构建 | 用什么语言写 | 输入 | 输出 |
|---|------|---------|-------------|------|------|
| **P01** | [Boolean Logic](./Project_01_BooleanLogic/) | Nand → Not/And/Or/Xor/Mux/DMux | Hack HDL | 真值表 | 15 个 .hdl |
| **P02** | [Boolean Arithmetic](./Project_02_BooleanArithmetic/) | HalfAdder → FullAdder → Adder → **ALU** | Hack HDL | ALU 控制位 | 4 个 .hdl |
| **P03** | [Sequential Logic](./Project_03_SequentialLogic/) | DFF → Bit → Register → RAM8/64/512/4K/16K → PC | Hack HDL | 时钟仿真 | 11 个 .hdl |
| **P04** | [Machine Language](./Project_04_MachineLanguage/) | 写 Hack 汇编：`Mult.hack` + `Fill.hack` | Hack 汇编 | 测试脚本 | 2 个 .hack |
| **P05** | [Computer Architecture](./Project_05_ComputerArchitecture/) | **Computer.hdl**（完整 CPU + Memory + ROM）| Hack HDL | Hack 程序 | 3 个 .hdl |
| **P06** | [Assembler](./Project_06_Assembler/) | 把 `.asm` 翻译成 `.hack` | Python/Java | .asm | .hack |
| **P07** | [VM Translator I](./Project_07_VMTranslator_I/) | 翻译栈运算（push/pop/arithmetic）| Python/Java | .vm | .asm |
| **P08** | [VM Translator II](./Project_08_VMTranslator_II/) | 完整 VM 翻译器（分支 + 函数）| Python/Java | .vm | .asm |
| **P09** | [High-Level Language](./Project_09_HighLevelLanguage/) | 用 Jack 写一个交互 App | Jack | 你自己设计 | 1 个 Jack App |
| **P10** | [Compiler I](./Project_10_Compiler_I/) | Tokenizer + Parser（语法分析）| Python/Java | .jack | .xml（语法树）|
| **P11** | [Compiler II](./Project_11_Compiler_II/) | 代码生成器（Jack → VM）| Python/Java | .jack | .vm |
| **P12** | [Operating System](./Project_12_OS/) | 用 Jack 写 OS：Math/String/Array/Memory/Output/Screen/Keyboard/Sys | Jack | 全栈 | 8 个 .jack |

---

## 3. Nand2Tetris 与本项目其他模块的交叉映射

> 这是把 nand2tetris 融入项目的核心价值——每个 project 都能在已有 Lab/Expert/Capstone 里找到**理论对照**和**真实工业实践**。

| Nand2Tetris Project | 知识点 | 对应 Lab（真机观测） | 对应 Expert（工业视角） | 对应 Capstone |
|---------------------|--------|---------------------|------------------------|---------------|
| P01 逻辑门 | 布尔代数、组合电路 | — | [`Expert_03_HW_Designer`](../Expert_03_HW_Designer/) RTL | — |
| P02 ALU | 算术逻辑单元 | [`Lab01 §3.4`](../Lab01_ISA与汇编/)（int/FDIV 实测）| [`Expert_03`](../Expert_03_HW_Designer/rtl/alu.v) | — |
| P03 时序 | 寄存器、RAM、DFF | [`Lab03`](../Lab03_存储层次/)（Cache 实测）| [`Expert_13`](../Expert_13_VLSI_Physical/) | — |
| P04 机器语言 | 汇编编程 | [`Lab01`](../Lab01_ISA与汇编/)（ARM64 汇编）| — | [`cpu_simulator/assembler.py`](../Capstone/cpu_simulator/assembler.py) |
| P05 CPU | 单周期 CPU 设计 | [`Lab02`](../Lab02_流水线与ILP/)（流水线）| [`Expert_03`](../Expert_03_HW_Designer/) | [`cpu_simulator/rv32i_sim.py`](../Capstone/cpu_simulator/rv32i_sim.py)（5 级流水）|
| P06 汇编器 | Two-pass assembler | [`Lab01`](../Lab01_ISA与汇编/) | [`Expert_11_Compiler_Research`](../Expert_11_Compiler_Research/) | [`cpu_simulator/assembler.py`](../Capstone/cpu_simulator/assembler.py) |
| P07-08 VM | 栈式虚拟机、字节码 | [`View_01_Compiler`](../View_01_Compiler/) | [`Expert_11`](../Expert_11_Compiler_Research/)（GCC/LLVM 内部）| — |
| P09 Jack | 高级语言、OOP | — | [`Expert_22`](../Expert_22_OpenSource_Ecosystem/) | — |
| P10-11 编译器 | 前端、后端、IR | [`View_01_Compiler`](../View_01_Compiler/) | [`Expert_11`](../Expert_11_Compiler_Research/) | — |
| P12 OS | 系统调用、内存管理、绘图 | [`Lab03`](../Lab03_存储层次/) + [`Lab06`](../Lab06_内存模型与并发/) | [`Expert_04_OS_Kernel`](../Expert_04_OS_Kernel/) | — |

**记忆口诀**：

> **Nand2Tetris 是"从零搭建"，Lab 是"用真机观测"，Capstone 是"模拟运行"——三个角度互不重叠。**

---

## 4. Hack vs RV32I vs ARM64 三种 ISA 对照

> 这是回答"为什么有了 Capstone 的 RV32I 还要做 Nand2Tetris 的 Hack？"——
> 因为 Hack 是**教学专用 ISA**，RV32I 是**研究/工业级 ISA**，ARM64 是**真实生产 ISA**。三者难度递增。

| 特性 | Hack（nand2tetris）| RV32I（Capstone）| ARM64（飞腾 D3000M）|
|------|---------------------|------------------|---------------------|
| 设计目的 | 教学（极简）| 研究/工业入门（精简 RISC）| 工业生产（手机/服务器主流）|
| 指令数 | 2 个 A 指令 + 2 个 C 指令（共 4 种）| 37 条基础 | ~1000 条（含 NEON/SVE）|
| 指令长度 | 16 位固定 | 32 位固定 | 32 位固定 |
| 寄存器数 | A, D, M（3 个，且 M 是内存别名）| 31 个通用 | 31 个通用 |
| 内存模型 | Harvard（指令/数据分离）| Princeton（统一）| Princeton（统一）|
| 流水线 | 单周期（5 拍）| 5 级流水（IF/ID/EX/MA/WB）| 15+ 级 OoO（FTC663）|
| 字长 | 16 位 | 32 位 | 64 位 |
| 寻址 | 直接 + 间接（M = RAM[A]）| imm + reg + 偏移 | imm + reg + 移位 + 偏移 |
| 中断 | 无 | 有 | 完整（4 个 EL）|
| 你能学到 | "CPU 的最小核心" | "RISC 流水线的设计权衡" | "现代 OoO 处理器的全部复杂度" |
| 实测可用 | nand2tetris HardwareSimulator | 本项目 `rv32i_sim.py` | 飞腾真机 + PMU |

> 📌 **三种 ISA 不替代，是叠加**：先做 Hack（懂 CPU 长啥样）→ 再做 RV32I（懂流水线/冒险）→ 再看 ARM64（懂乱序/分支预测/虚拟化）。

---

## 5. 工具链（必备）

### 5.1 nand2tetris 官方工具（Java，跨平台）

| 工具 | 用途 | 用于 Project |
|------|------|-------------|
| **HardwareSimulator** | 加载 .hdl，跑测试脚本 | P01, P02, P03, P05 |
| **CPUEmulator** | 加载 .hack / .asm，跑 Hack 程序 | P04, P05 |
| **VMEmulator** | 加载 .vm，跑 VM 字节码 | P07, P08, P09, P11, P12 |
| **JackCompiler** | 把 .jack 编译为 .vm | P09, P10, P11, P12 |
| **TextComparer** | 比较输出与期望 | 全部 |

**下载**：[nand2tetris Software Suite](https://www.nand2tetris.org/software)（约 5MB，免安装，只需 Java 11+）

### 5.2 替代工具（可选）

| 工具 | 优势 | 适合谁 |
|------|------|------|
| [nand2tetris Web IDE](https://nand2tetris.github.io/web-ide) | 浏览器即开即用，无需 Java | 不想装环境的初学者 |
| **iverilog + 自写 Verilog 版** | 学 Verilog 顺便做 nand2tetris | 想结合 [`Expert_03`](../Expert_03_HW_Designer/) RTL 一起练 |
| **Python 重写测试器** | 把 HDL 模拟器也自己造一遍 | 想再深一层的极客 |

### 5.3 与本项目的工具关系

| 工具 | 模拟层 | 项目里对应工具 |
|------|--------|---------------|
| HardwareSimulator | 晶体管 → ALU → CPU（L1-L2 早期）| [`Expert_03/rtl/`](../Expert_03_HW_Designer/rtl/)（iverilog）|
| CPUEmulator | 完整 CPU（L2 单周期）| [`Capstone/cpu_simulator`](../Capstone/cpu_simulator/) |
| VMEmulator | ISA → VM 抽象层 | 与本项目无对应（本项目聚焦硬件层）|
| **飞腾真机 + perf** | L2-L5 全部 | [`Lab00`–`Lab07`](../) |

---

## 6. 学习路径（不同读者的入口）

### 🌱 路径 A：完全零基础（推荐主流）

```
P01 (3 周) → P02 (3 周) → P03 (3 周) → P04 (1 周)
   ↓
P05 (4 周) ← 这是 Part I 的高潮，你将造出一台计算机！
   ↓
休息 + 复盘
   ↓
P06 (2 周) → P07 (3 周) → P08 (3 周) → P09 (4 周)
   ↓
P10 (3 周) → P11 (4 周) → P12 (4 周) ← 这是 Part II 的高潮，你将拥有 OS！
   ↓
🎉 此时你已具备读任何体系结构书的能力
   ↓
[进入本项目 Lab00] → 用 perf 观测真实飞腾 CPU
   ↓
[进入本项目 Capstone] → 用 Python 模拟 RV32I 流水线
```

**总耗时**：业余时间 18–24 个月。

### 🎓 路径 B：已会编程（Python/Java），想补硬件

跳过 P04（汇编你应该一看就懂），重点做：
- **P01-P03**（3 个月）：建立硬件直觉
- **P05**（4 周）：高潮
- **P06-P11**（4 个月）：补编译器栈
- 跳过 P09（写 App 没意思）和 P12（OS 太琐碎，留到后面看 [`Expert_04`](../Expert_04_OS_Kernel/) 实测）

### 🔬 路径 C：已懂硬件，想看教学级设计如何简化

只看高潮：
- **P02 的 ALU**（看 Nisan 怎么用"零 ALU 逻辑 + 全部用 Nand 表达"做出 ALU）
- **P05 的 Computer.hdl**（看 Hack 怎么用最少硬件拼出可运行的 CPU）
- **P07-P08 的 VM**（看栈式 VM 的最简形态）

读完去对比飞腾 D3000M，会有"教学极简 vs 工业极致"的强烈对照。

### 🏭 路径 D：工程师，想补全栈直觉

只做 P06 + P07 + P08 + P10 + P11（5 个核心 project），快速建立编译器栈直觉。
**约 3–4 个月**，从此看 [`Expert_11`](../Expert_11_Compiler_Research/) 不再抽象。

### 🎯 路径 E：与本项目 Lab 交替学习

| 阶段 | Nand2Tetris | 本项目 Lab |
|------|-------------|-----------|
| 1 | P01-P02（造 ALU） | — |
| 2 | P03（造 RAM） | — |
| 3 | — | [`Lab01`](../Lab01_ISA与汇编/)（看真机 ARM64 汇编）|
| 4 | P04-P05（造 CPU） | — |
| 5 | — | [`Lab02`](../Lab02_流水线与ILP/)（看真机流水线）|
| 6 | P06（造汇编器） | — |
| 7 | — | [`Lab04`](../Lab04_超标量乱序/)（看真机乱序）|
| 8 | P07-P08（造 VM） | — |
| 9 | — | [`Lab03`](../Lab03_存储层次/)（看真机 Cache）|
| 10 | P10-P11（造编译器） | — |
| 11 | — | [`View_01_Compiler`](../View_01_Compiler/)（看 GCC 优化级别）|

---

## 7. 与"思想母题"的连接

每个 Nand2Tetris Project 都对应 [`Great_Ideas_体系结构思想.md`](../背景知识/Great_Ideas_体系结构思想.md) 的若干条母题：

| Nand2Tetris Project | 对应的 Great Idea |
|---------------------|------------------|
| P01 逻辑门 | **抽象**（用 Nand 搭一切）|
| P02 ALU | **抽象**（运算的统一） + **接口**（ALU 是 CPU 的可插拔单元）|
| P03 时序 | **依赖前态**（状态机的本质）|
| P04 机器语言 | **抽象**（人 ↔ 机器的契约） + **接口**（ISA）|
| P05 CPU | **抽象**（CPU 内部多模块协作）+ **预测**（PC 自增）|
| P06 汇编器 | **抽象**（高级抽象 → 低级抽象）|
| P07-08 VM | **抽象**（ISA 之上的另一层抽象）|
| P09 高级语言 | **抽象**（人在语言层思考）|
| P10-11 编译器 | **抽象**（语言 → VM 的桥梁）|
| P12 OS | **抽象**（应用 ↔ 硬件的契约）+ **可靠性**（OS 负责资源管理）|

→ **做 Nand2Tetris 就是亲手触摸十大 Great Ideas 的过程**。

---

## 8. 与"分层模型"的连接

[`处理器分层模型.md`](../背景知识/处理器分层模型.md) 定义了 5 层抽象栈：

| 层 | Nand2Tetris 覆盖了哪一层？ |
|----|---------------------------|
| L5 应用 | ✅ P09（你写的 Jack App）|
| L4 OS + ABI | ✅ P12（你写的 Jack OS）|
| L3 ISA | ✅ P04-P05（Hack ISA）|
| L2 微架构 | ✅ P05（单周期 Hack CPU，无流水线 → 鼓励你之后做 RV32I 流水线）|
| L1 物理实现 | ❌（Nand2Tetris 只到 HDL 仿真，不涉及硅片）|

**这就是 Nand2Tetris 的边界**：它不涉及 L1 物理实现——但 [`Expert_13_VLSI_Physical`](../Expert_13_VLSI_Physical/) / [`Expert_14_Process_Manufacturing`](../Expert_14_Process_Manufacturing/) 会补全这一层。

---

## 9. 本目录的目录结构

```
Nand2Tetris/
├── README.md                          ← 本文（主入口）
├── Project_01_BooleanLogic/
│   ├── README.md                      ← P01 导读（必读）
│   └── hdl/                           ← 你的 .hdl 文件（待你写）
├── Project_02_BooleanArithmetic/      ← ALU
│   ├── README.md
│   └── hdl/
├── Project_03_SequentialLogic/        ← 寄存器 + RAM
│   ├── README.md
│   └── hdl/
├── Project_04_MachineLanguage/        ← 手写 Hack 汇编
│   ├── README.md
│   └── asm/
├── Project_05_ComputerArchitecture/   ← Computer.hdl（高潮 1）
│   ├── README.md
│   └── hdl/
├── Project_06_Assembler/              ← Python 汇编器
│   ├── README.md
│   ├── src/
│   └── tests/
├── Project_07_VMTranslator_I/         ← VM 翻译器（栈）
│   ├── README.md
│   └── src/
├── Project_08_VMTranslator_II/        ← VM 翻译器（完）
│   ├── README.md
│   └── src/
├── Project_09_HighLevelLanguage/      ← 用 Jack 写 App
│   ├── README.md
│   └── jack/
├── Project_10_Compiler_I/             ← 编译器前端
│   ├── README.md
│   └── src/
├── Project_11_Compiler_II/            ← 编译器后端
│   ├── README.md
│   └── src/
├── Project_12_OS/                     ← Jack OS
│   ├── README.md
│   └── jack/
├── tools/                             ← 测试脚本与说明
└── bibliography/                      ← 延伸阅读
```

每个 `Project_XX/README.md` 都按统一结构：
1. **目标**（一句话）
2. **对应书的章节 + 官方视频**
3. **你将构建什么**（交付物清单）
4. **关键概念**（理论速览）
5. **HDL/代码骨架**（部分核心 project 提供）
6. **测试脚本**
7. **常见坑**
8. **与本项目其他模块的连接**
9. **扩展挑战**
10. **检查清单（学完应该会什么）**

---

## 10. 参考文献

| 编号 | 文献 | 说明 |
|------|------|------|
| 📘 | **Nisan, N. & Schocken, S.** *The Elements of Computing Systems* 2nd ed. MIT Press, 2021 | 本课程指定教材 `[官方]` |
| 📙 | **Nisan & Schocken**《计算机系统要素：从零开始构建现代计算机》中文版 | 中文译本 |
| 🌐 | [nand2tetris.org](https://www.nand2tetris.org/) | 官方课程网站 |
| 🎓 | [Coursera: Build a Modern Computer from First Principles: From Nand to Tetris](https://www.coursera.org/learn/build-a-computer) | Part I（P01-P06）|
| 🎓 | [Coursera: Build a Modern Computer from First Principles: Nand to Tetris Part II](https://www.coursera.org/learn/nand2tetris2) | Part II（P07-P12）|
| 🎥 | Shimon Schocken, *The self-organizing computer course* (TED 2014) | 强烈推荐先看，建立直觉 |
| 🎥 | [nand2tetris YouTube 频道](https://www.youtube.com/@nand2tetris) | 官方视频讲座 |
| 📰 | Shimon Schocken's GitHub: [nand2tetris/web-ide](https://github.com/nand2tetris/web-ide) | 在线 IDE（开源）|

---

## 11. 常见问题

### Q1：必须做完全部 12 个 project 才能学懂体系结构吗？
**不必**。做 P01-P06（硬件部分）你就已经超过 95% 的"会写代码但不懂硬件"的程序员。
P07-P12 是软件栈，如果你已经懂编译器原理可以跳过。

### Q2：与 Ben Eater 的"用面包板搭 8 位 CPU"相比？
Ben Eater 是**真实硬件**（7400 系列 TTL + 面包板），节奏慢但看得见摸得着。
Nand2Tetris 是**仿真器**（HDL 文本），节奏快、可大规模复现。
**推荐先 Nand2Tetris 建立概念 → 再看 Ben Eater 增强直觉**。

### Q3：HDL 学了有用吗？工业上不是用 Verilog/VHDL 吗？
Nand2Tetris 的 HDL **只是教学语言，工业上不用**。但**学 HDL 思维**有用——
学完 Nand2Tetris 你再看 Verilog（[`Expert_03/rtl/`](../Expert_03_HW_Designer/rtl/)）会觉得"原来如此简单"。

### Q4：做完 Nand2Tetris 之后能直接看懂工业 CPU 吗？
不能。Nand2Tetris 的 Hack 是**单周期 CPU**，没有：
- 流水线（→ [`Lab02`](../Lab02_流水线与ILP/)、Capstone）
- Cache（→ [`Lab03`](../Lab03_存储层次/)）
- 乱序 / 分支预测 / 寄存器重命名（→ [`Lab04`](../Lab04_超标量乱序/)）
- 虚拟内存 / TLB（→ [`Lab03`](../Lab03_存储层次/)）
- 多核并发（→ [`Lab06`](../Lab06_内存模型与并发/)）

→ **做完 Nand2Tetris 再做本项目 Lab，正好补全这些"教学 CPU 没有的"工业特性**。

### Q5：Hack 与 RISC-V 哪个先学？
**Hack 先，RISC-V 后**。Hack 比 RV32I 简单 10 倍，先用 Hack 建立"CPU 是什么"的直觉，
再用 RV32I 学"工业 RISC 的设计权衡"。

### Q6：P09 写什么 App 好？
经典选择：
- **俄罗斯方块**（Tetris）—— 课程默认目标
- **Pong**（更简单，2 周可做完）
- **2048**（中等难度）
- **贪吃蛇**（经典）
- **计算器**（最简单）

### Q7：项目里能用别人的代码吗？
**理论上不能**——课程的灵魂就是"全部自己写"。但参考别人的实现是允许的。
本项目在每个 `Project_XX/README.md` 提供**思路与骨架**，**不会提供完整答案**。
完整参考实现可在 [nand2tetris GitHub](https://github.com/havivha/nand2tetris) 等社区找到（但请先自己写）。

---

## 📌 下一步

**如果你是第一次接触 Nand2Tetris**：

1. 先看 Shimon Schocken 的 [TED 演讲](https://www.ted.com/talks/shimon_schocken_the_self_organizing_computer_course)（15 分钟，强烈推荐）
2. 下载 [Software Suite](https://www.nand2tetris.org/software)（5MB，免安装）
3. 进 [`Project_01_BooleanLogic/`](./Project_01_BooleanLogic/)，从 Nand 搭出 Not 开始
4. 3 周后回到这里，进 Project 02

**如果你已经做过部分 Nand2Tetris**：

1. 在 §2.1 的总览表里找到你停下的位置
2. 跳到对应 Project 的 README
3. 用 §6 的路径选择适合你的下一步

**如果你只想了解、不打算做**：

1. 通读本文 §1-§4（30 分钟）
2. 浏览每个 Project 的 README（每个 5 分钟）
3. 把 Nand2Tetris 当作**理解本项目 Lab 的"反向视角"**——Lab 是观测真实 CPU，Nand2Tetris 是想象最简 CPU
