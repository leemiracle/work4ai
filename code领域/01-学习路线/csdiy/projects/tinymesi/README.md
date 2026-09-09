# tinymesi · MESI 缓存一致性协议模拟器

> 多核 L1 cache 如何避免彼此踩踏——M/E/S/I 状态机。参照 **Patterson & Hennessy §5.5 / Intel SDM**。

## 概述

tinymesi 模拟多核 CPU 的 L1 cache 一致性。每个核有自己的 cache，但共享主存；MESI 协议通过 4 个状态（Modified / Exclusive / Shared / Invalid）和总线嗅探（snoop）保证：任意核读到的数据都是最新版本。这是「并发一高就崩」的硬件层根源。

## 核心概念

| # | 概念 | 一句话 |
|---|------|--------|
| 1 | **4 个状态** | M=已改独占 / E=未改独占 / S=未改共享 / I=无效 |
| 2 | **总线嗅探（Snoop）** | 每个 cache 监听总线事务，按状态机迁移 |
| 3 | **写传播** | 一个核写入，其他核的对应 cache line 必须失效或更新 |
| 4 | **False Sharing** | 两个变量同在一个 cache line，不同核各写一个 → cache 颠簸 |
| 5 | **从 MESI 到 MOESI/MESIF** | 真实 CPU 的扩展协议（Owner/Forward 状态） |

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `__init__.py` | 2 | tinymesi — 参照 Patterson Hennessy §5.5 的 MESI 缓存一致性 |
| `demo.py` | 71 | 演示脚本 |
| `mesi.py` | 151 | MESI 协议核心 |

## 快速开始

```bash
cd projects/tinymesi
python3 demo.py
```

## 学习要点

- 4 个状态：M=已改独占 / E=未改独占 / S=未改共享 / I=无效
- 总线嗅探（Snoop）：每个 cache 监听总线事务，按状态机迁移
- 写传播：一个核写入，其他核的对应 cache line 必须失效或更新
- False Sharing：两个变量同在一个 cache line，不同核各写一个 → cache 颠簸
- 从 MESI 到 MOESI/MESIF：真实 CPU 的扩展协议（Owner/Forward 状态）

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinymesi` | Patterson & Hennessy §5.5 / Intel SDM |

## 相关 csdiy 资源

- notes/os-程序员视角-从bug到原理.md（并发原子性）
- notes/csapp-程序员视角.md（Ch6 存储器层次）

---

*本 README 由 gen_readmes.py 自动生成骨架 + 人工填充。*
