# 讲透Chromium 文档层索引（DeepWiki 替代方案 · 2026-10-09）

> DeepWiki NORESET（见 ../deepwiki/_PROBE.md），文档层 = **官方源双层替代**：
> ① 仓内设计文档 1818 篇（`../repo-docs/src/`，与 HEAD 8fe2331 同步，最权威）
> ② 在线经典架构文档 8 篇（本目录，chromium.org 抓取 2026-10-09）

## 在线经典架构文档（本目录）

| 文档 | 主题 | 字符 |
|---|---|---|
| [multi-process-architecture.md](multi-process-architecture.md) | 多进程架构（2006 经典原文：为何渲染引擎必须进程隔离） | 8.7K |
| [displaying-a-web-page-in-chrome.md](displaying-a-web-page-in-chrome.md) | Chromium 如何显示网页（renderer→compositor→GPU 全链） | 15K |
| [inter-process-communication.md](inter-process-communication.md) | 进程间通信（IPC/Mojo 前史） | 15K |
| [multi-process-resource-loading.md](multi-process-resource-loading.md) | 多进程资源加载 | 4K |
| [compositor-thread-architecture.md](compositor-thread-architecture.md) | 合成器线程架构 | 15K |
| [gpu-accelerated-compositing-in-chrome.md](gpu-accelerated-compositing-in-chrome.md) | GPU 加速合成（最长最全） | 47K |
| [site-isolation.md](site-isolation.md) | 站点隔离（安全架构核心） | 19K |
| [rendering-architecture-diagrams.md](rendering-architecture-diagrams.md) | 渲染架构图（图为主） | 1.1K |

抓取失败 2 篇（正文过短疑重定向页）：browser-components、process-models——内容已被仓内 `repo-docs/src/docs/` 覆盖。

## 仓内文档层（../repo-docs/src/，1818 篇 / 20MB）

按子系统分布（md 篇数）：docs **722**（含 design/ 设计文档群）、chrome 425、components 435、content 71、net 49、services 47、ui 43、base 36、mojo 24、media 17、sandbox 9、cc 9。
关键入口：`docs/`（贡献者文档+设计索引）、`docs/design/`（sandbox/threading/startup 官方设计文档）、各子系统 `README.md`。

## 使用说明

- 图谱（深入分析主菜）在仓内 `src/.understand-anything/knowledge-graph.json`
- 本文档层 = ONBOARDING/explain 写作时的权威引用源，行号引用以仓内 HEAD 8fe2331 为准
