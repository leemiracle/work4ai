# giselle 深读卡 —— 日本团队的可视化 AI 工作流平台：ReactFlow 画布 + 多 provider 引擎 + RAG 节点

> **定位**：giselles.ai（日本团队）的开源 AI 工作流编排平台——**节点画布**（ReactFlow）可视化设计工作流，多 provider LLM（OpenAI/Anthropic/Google/Fal-AI）+ RAG（文档/代码向量库）+ 工具执行（GitHub/web 搜索/DB 查询）+ 后台作业 + 实时流式。分层 monorepo：apps/*（studio 生产应用 + playground 开发场 + UI showcase）+ internal-packages/*（workflow-designer-ui / ui 组件库）+ 引擎包。
> **本地**：`repos/giselle`（giselles-ai/giselle）｜**深读**：deepwiki 37 子页归档 `deepwiki/giselle/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 应用层 apps/* | 生产/开发/展示三应用 | studio（Next.js 15，/api/giselle/* 路由）、playground、ui showcase |
| UI 组件层 | 画布与组件库 | @giselle-internal/workflow-designer-ui（ReactFlow+useEditorStore）、@giselle-internal/ui（Radix+theme） |
| 引擎层 | 执行引擎+SDK | giselleEngine（AI 执行管线） |
| 数据层 | RAG 与处理 | 文档/代码 vector store、数据处理系统 |
| 作业层 | 长任务 | background job processing |
| 流式 | 实时结果 | streaming generation |

## 二、核心机制

1. **节点画布三态分离**：设计态（ReactFlow 画布+editorStore）→ 数据态（工作流 JSON）→ 执行态（giselleEngine 消费）——与 ix（图存数据库编译 LCEL）同为可视化编排路线，Giselle 更现代（ReactFlow 生态+zustand）。
2. **RAG 作为画布一等节点**：向量库不是外挂而是画布上可连接的节点类型——数据流显式化。
3. **多 provider 引擎统一**：四家 LLM+Fal-AI（图像生成）统一在引擎层，画布不感知差异。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 节点画布编排 | ix/LangFlow 同路线对照（可视化图编排三代演进） |
| RAG 节点化 | 讲透NLP §RAG（数据流显式化设计） |
| ReactFlow+zustand | 前端工程参考 |

## 四、关键入口

```
apps/studio/                      # 生产应用（Next.js 15）
internal-packages/workflow-designer-ui/  # 画布组件（ReactFlow）
packages/giselle-engine（引擎）    # 执行层
```

## 五、深读子页地图（37 页精选 5）

Overview（分层 monorepo 架构图）｜Workflow Designer UI｜Core Engine and SDK｜Data Processing Systems（RAG）｜Studio Application。

## 六、与"我们"的关系（一句话）

可视化 Agent 工作流的"东方样本"——与 ix（2023 先驱）/LangFlow（同类头部）三仓对照可讲清"节点画布平台"的产品架构通式。

---
生成：2026-08-21 · deepwiki 37 页全归档
