# 讲透 WeKnora —— 腾讯开源企业级 LLM 知识管理框架全景知识库

> 生成日期：2026-09-20 · 对应仓库 [Tencent/WeKnora](https://github.com/Tencent/WeKnora) commit `5c5d46d9`（v0.8.0）
> 流水线：DeepWiki 全量抓取（90/90 页）→ understand 中文知识图谱（12951 节点 / 112010 边 / 12 层 / 15 步导览）→ 新人上手指南 → 重要文件精讲

**WeKnora（维娜拉）** 是腾讯开源的、基于大语言模型的知识管理框架，围绕三大核心能力构建：
**RAG 快速问答**（文档摄取→分块→嵌入→混合检索→引用生成）、**ReAct Agent 智能推理**（Think-Act-Observe 循环，自主编排知识检索、MCP 工具、技能目录、Docker/E2B/Cube 沙箱与网络搜索）、**Wiki 模式**（Agent 从原始文档自治生成互链 Markdown 知识库与可视化图谱，支持人工编辑与版本回滚）。

技术栈：Go + Gin 后端（internal/ 2067 文件）· Vue 3 + **TDesign** + Pinia + Vite 前端（frontend/src 747 文件）· Python docreader 文档解析（独立 gRPC 服务）· miniprogram 微信小程序 · Wails 桌面端 · Docker Compose/Helm 部署。

---

## 📂 目录导航

| 目录 | 内容 | 规模 |
|---|---|---|
| `deepwiki/` | DeepWiki 全量中文转档（15 章 90 页，100% 覆盖，含源码行号引用） | 1.5 MB |
| `onboarding/` | 新人上手指南（8 节：架构说明、核心模块、学习路径） | 5962 字 |
| `explain/` | 重要文件精讲（12 篇，六节结构，行号级源码解读） | 30336 字（不计空格） |
| `knowledge-graph.json` | （在仓库 `.understand-anything/` 内）交互式知识图谱 | 12951 节点 |

## 🗺️ 三份资料的用法

1. **快速了解项目** → `onboarding/ONBOARDING.md`（15 分钟读完，12 层架构+两条数据流主线）
2. **系统学习某个子系统** → `deepwiki/INDEX.md` 找对应章节（如 3.3 Agent 系统、11.6 混合检索）
3. **深入具体文件** → `explain/` 对 12 个核心文件的行号级精讲（DI 容器/RBAC/ReAct 引擎/MCP/沙箱/Wiki/模型网关/前端主界面等）

## 🏗️ 12 层架构速览（understand 图谱实证）

| 层 | 节点数 | 职责 |
|---|---|---|
| HTTP 接口与服务启动层 | 156 | handler/router/middleware/SSE 流/cmd 入口/DI 容器 |
| CLI 命令行工具层 | 151 | weknora CLI（agent/kb/chat/search/profile 子命令树） |
| 应用服务层 | 215 | application/service + access（含 chat_pipeline 管线插件与 memory） |
| Agent 引擎与沙箱执行层 | 182 | agent ReAct 循环/modelcontext/browserskill/sandbox |
| 数据访问与存储层 | 96 | repository 向量库/retriever 引擎 + database 迁移 |
| 领域类型与契约层 | 140 | internal/types（全仓被依赖之冠，洋葱最内核） |
| 模型接入层 | 108 | models 多供应商 chat/embedding/rerank/vlm + Langfuse |
| 外部集成层 | 104 | im 九平台适配器 + datasource 连接器 + mcp 客户端 |
| 共享基础设施层 | 105 | infrastructure/chunker/搜索/事件总线/横切工具 |
| 前端应用层 | 568 | Vue3 SPA 全部视图/组件/store/composables |
| 辅助服务与多端客户端层 | 171 | docreader Python/miniprogram/packages/client/mcp-server |
| 部署运维与项目资料层 | 183 | docker/helm/CI/scripts/config/dataset/根文档 |

依赖方向（洋葱结构，图谱实证）：handler → application → agent/models/sandbox → repository → **types（零反向依赖内核）**；CLI/前端作为独立入口垂直切入。

## 🚶 15 步导览路线（understand tour）

1. 项目总览：WeKnora 是什么 → 2. 服务启动与依赖注入容器 → 3. HTTP 接口：路由、认证与 SSE 流 → 4. 领域契约层：类型与接口 → 5. 应用服务层与 RBAC 授权决策 → 6. chat_pipeline：RAG 问答管线 → 7. 检索存储：向量库与混合引擎 → 8. ReAct Agent 引擎：Think-Act-Observe → 9. 沙箱执行与 MCP 工具生态 → 10. 长期记忆与 Wiki 自动生成 → 11. 模型接入网关：二十余家供应商 → 12. docreader：Python 文档解析服务 → 13. 多源连接器与 IM 机器人 → 14. 前端管理台与多端客户端 → 15. 部署运维：从 Compose 到 CI

## 📚 项目内文档地图（仓库自带）

- `README_CN.md` / `docs/开发指南.md` / `docs/快速开发模式说明.md` —— 入门与开发流程
- `docs/RBAC说明.md` / `docs/MCP功能使用说明.md` / `docs/KnowledgeGraph.md` / `docs/Langfuse集成.md` —— 专项功能
- `docs/agent-tools-design.md` / `docs/agent-prompt-assembly.md` / `docs/agent-skills.md` —— Agent 设计文档三件套
- `docs/sandbox-{protocol,docker-backend,cluster,desktop}.md` —— 沙箱体系四篇
- `docs/CHUNKING.md` / `docs/BUILTIN_MODELS.md` / `docs/BUILTIN_MCP_SERVICES.md` —— 内置机制
- `website-docs/` —— 官网文档（01-getting-started/02-architecture/03-features/04-api/05-clients/06-development，66 篇）
- `docs/api/` + `docs/swagger.yaml` —— API 契约

## 🔍 质量与口径说明

- DeepWiki 页面中 mermaid 图块为空（div 内图表不进正文文本流，转换已知限制），文字无损
- understand 图谱裁剪范围（.understandignore）：`**/*_test.go`（1125 个测试文件）、`docs/`、`website-docs/`、`migrations/`（269 个 SQL）、`third_party/`、`examples/`、`testdata/` —— 图谱覆盖 2112 个核心源码文件，项目文档另行纳入本知识库
- 校验：图谱 0 issues（dangling 边仅指向被裁剪文件，属预期）；DeepWiki 覆盖率 links=90 files=90 missing=0 empty=0
