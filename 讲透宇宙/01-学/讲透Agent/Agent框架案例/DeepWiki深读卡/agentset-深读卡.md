# agentset 深读卡 —— 生产级 RAG 平台全家桶：摄取/向量/搜索/Playground/托管一条龙（多租户）

> **定位**：agentset-ai 的开源 RAG/agentic 应用平台——构建/评估/部署生产级 RAG 的端到端工具链：文档摄取（上传/爬站/YouTube/文本）、向量索引、语义搜索、chat playground、**自定义域名公共托管**。多租户架构（每组织隔离 namespace），模型无关（多 LLM/embedding/向量库）。核心包：`@agentset/jobs`（Trigger.dev 摄取任务）+ `@agentset/engine`（检索引擎，Pinecone/Turbopuffer）。
> **本地**：`repos/agentset`（agentset-ai/agentset）｜**深读**：deepwiki 41 子页归档 `deepwiki/agentset/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Web 应用 | UI+托管 | apps/web（Next.js） |
| 摄取 | 多源入库 | @agentset/jobs（Trigger.dev：文件/爬虫/YouTube/文本） |
| 引擎 | 检索 | @agentset/engine（Pinecone/Turbopuffer） |
| 文档处理 | 解析管线 | Document Processing 子系统 |
| 搜索/RAG | 语义检索+生成 | RAG and Search System |
| 多租户 | 隔离 | 组织 namespace |

## 二、核心机制

1. **摄取即任务**：文档入库全部走 Trigger.dev 后台任务（异步/重试/可观测）——摄取规模化不阻塞交互。
2. **引擎包可独立复用**：@agentset/engine 封装多向量库 provider——检索层与 Web 层解耦。
3. **公共托管+自定义域**：RAG 应用一键发布为带域名服务——从内部工具到对外产品的最后一公里内建。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 摄取/索引/检索/托管全链 | 讲透NLP §RAG 工程化完整版 |
| 多租户 namespace | ai-deployment §SaaS 化 |

## 四、关键入口

```
apps/web/            # Next.js 主应用
packages/jobs/       # 摄取任务
packages/engine/     # 检索引擎
```

## 五、深读子页地图（41 页精选 5）

Overview｜Architecture｜Data Layer｜Document Processing｜RAG and Search System。

## 六、与"我们"的关系（一句话）

RAG 平台工程的"全家桶样本"——与 localgpt（本地单机版）对照讲 RAG 从个人工具到多租户 SaaS 的工程阶梯。

---
生成：2026-08-21 · deepwiki 41 页全归档
