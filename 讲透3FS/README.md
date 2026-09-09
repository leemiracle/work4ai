# 讲透 3FS

> DeepSeek 开源的高性能分布式文件系统（Fire-Flyer File System）：SSD + RDMA 打造面向 AI 训练/推理负载的共享存储层 · commit `22fca04`（2026-05-07）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 50 页 |
| paper/ | 1 篇（SC24 Fire-Flyer AI-HPC，arXiv:2408.14158） |
| 知识图谱 | 2880 节点 / 5617 边 / 14 层 / 13 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [paper/PAPER-DEEPREAD.md](paper/PAPER-DEEPREAD.md) 论文精读——3FS 无独立论文，精读主线为 SC24 的 Fire-Flyer AI-HPC 论文（3FS 为其存储子系统章节，seesaw 调度 / FP8 crossover 等设计细节全核过）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（本仓 `~/ai/explore/deepseek-ai/3FS`，1.9MB）
- 规模：2880 节点 / 5617 边 / 14 层 / 13 步导览
- fingerprints 基线已生成，支持增量更新（代码变更后只重析变动文件）

## 推荐阅读顺序

1. [paper/PAPER-DEEPREAD.md](paper/PAPER-DEEPREAD.md)——先建立 Fire-Flyer AI-HPC 全局图景与 3FS 在其中的位置
2. [deepwiki/](deepwiki/) 1-overview → 部署与设计章节——系统结构与运维视角
3. 知识图谱 13 步导览——按依赖链深入源码（USRBIO API、消息队列、元数据服务等模块）

## 姊妹篇

- [讲透smallpond](../讲透smallpond/)——建在 3FS 之上的轻量数据处理框架
- [讲透DeepEP](../讲透DeepEP/)——同为 V3 训推基础设施三件套
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
