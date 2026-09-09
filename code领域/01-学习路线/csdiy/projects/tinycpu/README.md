# tinycpu · 5 级流水线 CPU 模拟器

> 从单周期到流水线，理解 CPU 数据通路。参照 **RISC-V / MIPS / CSAPP Ch4**。

## 概述

tinycpu 是一个教学用的 CPU 模拟器，从最基础的单周期 ALU 执行逐步演化到 5 级流水线。它让你看见：一条 `ADD R1, R2, R3` 指令在硬件上是如何一步步变成寄存器写入的。对应 CSAPP 第 4 章「处理器体系结构」的 LAB Ch4。

## 核心概念

| # | 概念 | 一句话 |
|---|------|--------|
| 1 | **指令集（ISA）** | OpCode + AluOp + CondCode + Instruction，定义机器能听懂的最小语言 |
| 2 | **单周期数据通路** | 取指→译码→执行→访存→写回，一拍完成，简单但慢 |
| 3 | **5 级流水线** | IF/ID/EX/MEM/WB 重叠执行，吞吐量 ×5，但需处理冒险 |
| 4 | **数据冒险与转发** | EX 产物转发回 EX 入口，避免流水线气泡 |
| 5 | **条件码与分支** | check_cond 处理 EQ/NE/LT/GT，对应 cmov 化优化 |

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `__init__.py` | 4 | tinycpu — 参照 csapp Ch4 的 CPU 模拟器 |
| `core.py` | 124 | 核心实现 |
| `demo.py` | 120 | 演示脚本 |
| `isa.py` | 109 | 指令集定义 |
| `pipeline.py` | 135 | 流水线实现 |

## 快速开始

```bash
cd projects/tinycpu
python3 demo.py
```

## 学习要点

- 指令集（ISA）：OpCode + AluOp + CondCode + Instruction，定义机器能听懂的最小语言
- 单周期数据通路：取指→译码→执行→访存→写回，一拍完成，简单但慢
- 5 级流水线：IF/ID/EX/MEM/WB 重叠执行，吞吐量 ×5，但需处理冒险
- 数据冒险与转发：EX 产物转发回 EX 入口，避免流水线气泡
- 条件码与分支：check_cond 处理 EQ/NE/LT/GT，对应 cmov 化优化

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinycpu` | RISC-V / MIPS / CSAPP Ch4 |

## 相关 csdiy 资源

- notes/csapp-程序员视角.md（Ch4 处理器）
- source-reading/branch-prediction-精读.md

---

*本 README 由 gen_readmes.py 自动生成骨架 + 人工填充。*
