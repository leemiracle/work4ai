# 讲透 DeepEP

> DeepSeek MoE 专家并行高性能通信库（DeepEveryParallel）：NVLink+RDMA 的 all-to-all dispatch/combine 内核，FP8 低精度，零/极低 SM 占用 · commit `01dc3aa`（2026-08-04）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 37 页 |
| onboarding/ | 2495 字（不计空格字符） |
| explain/ | 4 篇精讲 |
| 知识图谱 | 290 节点 / 552 边 / 9 层 / 11 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南
- [explain/](explain/) 4 篇文件级精讲：buffers-legacy.py / buffers-elastic.py / jit-handle.hpp / impls-dispatch.cuh（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/DeepEP`，212KB）
- 规模：290 节点 / 552 边 / 9 层 / 11 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——库分层与 JIT 编译模型全景
2. [explain/01](explain/01-deep_ep-buffers-legacy.py.md)→[04](explain/04-deep_ep-impls-dispatch.cuh.md)——Python 缓冲区门面到 CUDA dispatch 内核逐层下钻
3. [deepwiki/](deepwiki/) 1-overview 起按章节补全
4. 知识图谱 11 步导览做源码漫游收尾

## 姊妹篇

- [讲透EPLB](../讲透EPLB/) / [讲透LPLB](../讲透LPLB/)——专家并行负载均衡两兄弟（LPLB 的负载统计可直取 DeepEP buffer）
- [讲透DualPipe](../讲透DualPipe/)——流水线并行的通信重叠
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
