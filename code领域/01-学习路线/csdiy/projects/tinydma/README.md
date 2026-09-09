# tinydma · DMA 控制器模拟器

> 让外设直接读写内存，把 CPU 从搬运工解放出来。参照 **Intel 8237 / 现代 SoC DMA**。

## 概述

tinydma 模拟直接内存访问控制器：CPU 配好「源地址/目的地址/长度」后，DMA 自己完成搬运，CPU 该干嘛干嘛；搬运完了用中断通知。这是「零拷贝（zero-copy）为什么快」的硬件根基。

## 核心概念

| # | 概念 | 一句话 |
|---|------|--------|
| 1 | **DMA 描述符** | 一段内存描述一笔传输：src/dst/len/next |
| 2 | **Scatter-Gather** | 链表式描述符，一次 DMA 完成多段不连续传输 |
| 3 | **Cache Coherency 陷阱** | DMA 改了内存，CPU cache 还是旧值 → 需要 cache flush/invalidate |
| 4 | **与中断协作** | DMA 完成后触发中断，CPU 在 ISR 里收尾 |

## 代码结构

| 文件 | 行数 | 内容 |
|------|------|------|
| `main.py` | 117 | 主入口 + 演示 |

## 快速开始

```bash
cd projects/tinydma
python3 main.py
```

## 学习要点

- DMA 描述符：一段内存描述一笔传输：src/dst/len/next
- Scatter-Gather：链表式描述符，一次 DMA 完成多段不连续传输
- Cache Coherency 陷阱：DMA 改了内存，CPU cache 还是旧值 → 需要 cache flush/invalidate
- 与中断协作：DMA 完成后触发中断，CPU 在 ISR 里收尾

## 参照真实项目

| tiny | 真实 |
|------|------|
| `tinydma` | Intel 8237 / 现代 SoC DMA |

## 相关 csdiy 资源

- source-reading/numa-architecture-精读.md
- notes/perf-程序员视角-定位与优化.md（zero-copy）

---

*本 README 由 gen_readmes.py 自动生成骨架 + 人工填充。*
