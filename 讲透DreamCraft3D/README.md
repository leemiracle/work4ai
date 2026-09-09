# 讲透 DreamCraft3D

> 层级化 3D 内容生成开源实现：2D 参考图引导几何雕刻与纹理增强两阶段，核心贡献 Bootstrapped Score Distillation 解决一致性 · commit `5829ef1`（2025-04-22）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 21 页 |
| onboarding/ | 5024 字（不计空格字符） |
| paper/ | 1 篇（ICLR 2024，arXiv:2310.16818） |
| 知识图谱 | 795 节点 / 1933 边 / 8 层 / 10 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南（本仓无 explain，onboarding 承担精讲）
- [paper/PAPER-DEEPREAD.md](paper/PAPER-DEEPREAD.md) 论文精读——BSD 公式链与三阶段代码映射全核过

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/DreamCraft3D`，720KB）
- 规模：795 节点 / 1933 边 / 8 层 / 10 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [paper/PAPER-DEEPREAD.md](paper/PAPER-DEEPREAD.md)——先建立 BSD（Bootstrapped Score Distillation）与两阶段生成的理论图景
2. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——代码库结构与训练/推理入口
3. [deepwiki/](deepwiki/) Stage-1 粗几何 → Stage-2 精修章节对照
4. 知识图谱 10 步导览做源码漫游收尾

## 姊妹篇

- [讲透DeepSeek-VL](../讲透DeepSeek-VL/) / [讲透Janus](../讲透Janus/)——多模态理解与统一理解生成路线
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
