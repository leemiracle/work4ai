# tinybus · 系统总线协议模拟器

> master 申请→arbiter 仲裁→读写 slave，多设备共享通道。参照 **PCI / AMBA AXI / Wishbone**。

## 概述

tinybus 模拟 SoC 内部的系统总线：多个 master（CPU/DMA）都要访问多个 slave（RAM/ROM/MMIO），总线仲裁器（Arbiter）决定谁能占用这一拍。这是「为什么硬件是并发」的最小模型。

## 核心概念

| # | 概念 | 一句话 |
|---|------|--------|
| 1 | **Master/Slave** | 发起方 vs 响应方，PCI/AXI 的基本角色 |
| 2 | **总线仲裁** | 多个 master 同时申请，arbiter 按优先级/轮转裁决 |
| 3 | **事务（Transaction）** | 一次读/写 = 申请 + 地址 + 数据 + 应答 |
| 4 | **MMIO** | 内存映射 IO：CPU 用 mov 指令就能控制设备 |

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 116 | 主入口 + 演示 |

## 快速开始

```bash
cd projects/tinybus
python3 main.py
```

## 学习要点

- Master/Slave：发起方 vs 响应方，PCI/AXI 的基本角色
- 总线仲裁：多个 master 同时申请，arbiter 按优先级/轮转裁决
- 事务（Transaction）：一次读/写 = 申请 + 地址 + 数据 + 应答
- MMIO：内存映射 IO：CPU 用 mov 指令就能控制设备

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinybus` | PCI / AMBA AXI / Wishbone |

## 相关 csdiy 资源

- notes/csapp-程序员视角.md（Ch6 IO 设备）

---

*本 README 由 gen_readmes.py 自动生成骨架 + 人工填充。*
