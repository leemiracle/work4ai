# tinymmu · 虚拟内存管理单元（MMU）模拟器

> 页表 + TLB + 缺页处理，理解虚拟地址如何变成物理地址。参照 **CSAPP Ch9 / Linux mm**。

## 概述

tinymmu 实现了 CSAPP Ch9 的核心：多级页表、TLB 缓存、Page Fault 处理。它让你看见：一个 `*ptr = 42` 背后，硬件和 OS 协同完成了多少事。所有 OOM、smaps、ASAN 报错的根源都在这里。

## 核心概念

| # | 概念 | 一句话 |
|---|------|--------|
| 1 | **虚拟地址空间** | 4GB 看似连续，实际由页表映射到散落的物理页 |
| 2 | **多级页表** | PageDirectory → PageTable → PTE，用层级换空间（只有用到的才分配） |
| 3 | **TLB 缓存** | 地址翻译极高频，必须 L1 cache 化；miss 触发 page walk |
| 4 | **Page Fault** | PTE.present=0 时陷入 OS，分配新页或触发 OOM Killer |
| 5 | **写时拷贝/共享内存** | 通过 PTE 标志位实现 fork() 和 mmap() |

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `__init__.py` | 5 | tinymmu — 参照 csapp Ch9 的虚拟内存管理单元 |
| `demo.py` | 122 | 演示脚本 |
| `mmu.py` | 115 | MMU 核心 |
| `page_table.py` | 68 | 页表 |
| `tlb.py` | 57 | TLB 缓存 |

## 快速开始

```bash
cd projects/tinymmu
python3 demo.py
```

## 学习要点

- 虚拟地址空间：4GB 看似连续，实际由页表映射到散落的物理页
- 多级页表：PageDirectory → PageTable → PTE，用层级换空间（只有用到的才分配）
- TLB 缓存：地址翻译极高频，必须 L1 cache 化；miss 触发 page walk
- Page Fault：PTE.present=0 时陷入 OS，分配新页或触发 OOM Killer
- 写时拷贝/共享内存：通过 PTE 标志位实现 fork() 和 mmap()

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinymmu` | CSAPP Ch9 / Linux mm |

## 相关 csdiy 资源

- notes/csapp-程序员视角.md（Ch9 虚拟内存）
- notes/os-程序员视角-从bug到原理.md（OOM）

---

*本 README 由 gen_readmes.py 自动生成骨架 + 人工填充。*
