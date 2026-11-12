# 讲透推理服务（D3 学区首单元 · 2026-11-12 孵化）

> 知识地图治理清单"学区断层"第二单元（继 [讲透集合通信](../讲透集合通信/README.md) 之后）：D3 推理与服务层此前零教学单元，本单元从 02-透 区代表作 [讲透vLLM](../../02-透/讲透vLLM/README.md)（14454 节点图谱）/[讲透SGLang](../../02-透/讲透SGLang/README.md)（11615 节点）反向蒸馏成五幕教学体。

## 篇目表

| 幕 | 文件 | 一句话 |
|---|---|---|
| 一 · 直觉 | [01-直觉-从凑批到流式.md](01-直觉-从凑批到流式.md) | 餐厅排班比喻：static batching 的"等最慢食客"灾难 |
| 二 · 数学 | [02-数学-吞吐定律与KV账本.md](02-数学-吞吐定律与KV账本.md) | Little 定律 + KV cache 字节公式 + decode 的 memory-bound 本质 |
| 三 · 代码 | [03-代码-batching离散事件模拟.md](03-代码-batching离散事件模拟.md) | 模拟器真跑：continuous 吞吐 1.93x、批占用 7.7→14.9/16 |
| 四 · 不足 | [04-不足-推理引擎的暗面.md](04-不足-推理引擎的暗面.md) | 首 token 延迟、长尾饥饿、KV 碎片、调度器复杂度税 |
| 五 · 应用 | [05-应用-服务的真实战场.md](05-应用-服务的真实战场.md) | P/D 分离、KV 池化、投机解码、SLO 分级、端侧推理 |

## 核心数字速览（来自 03 幕真跑，200 请求/异构长度 8-128/B=16）

| 调度 | 吞吐(req/it) | 平均延迟 | 平均批占用 |
|---|---|---|---|
| static | 0.119 | 750.3 | 7.7/16 |
| continuous | 0.229 | 339.8 | 14.9/16 |

## 素材源（证据锚点，全部盘上核实）

- [讲透vLLM](../../02-透/讲透vLLM/README.md)（14454n 图谱+手术合并范式）、[讲透SGLang](../../02-透/讲透SGLang/README.md)（RadixAttention）
- [讲透LMCache](../../03-查/讲透LMCache/deepwiki/INDEX.md)、[讲透Mooncake 蒸馏卡](../../03-查/讲透Mooncake/DISTILLED.md)（KV 池化）
- [讲透DSpark](../../04-研/讲透DSpark/paper/PAPER-DEEPREAD.md)（投机解码）、[讲透DeepSeek-V3.2-Exp](../../02-透/讲透DeepSeek-V3.2-Exp/README.md)（DSA 稀疏注意力）
- [讲透XGrammar](../../02-透/讲透XGrammar/README.md)（结构化输出）、[讲透WebLLM](../../02-透/讲透WebLLM/README.md)（浏览器端）
