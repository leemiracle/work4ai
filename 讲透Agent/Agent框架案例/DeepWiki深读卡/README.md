# DeepWiki 深读卡（awesome-agents 135 仓库全景）

> **来源**：[DeepWiki](https://deepwiki.com/) 对 `awesome-agents/repos/` 下全部 135 个 Agent 仓库的 AI 生成文档（含全部子页面 + mermaid 架构图）。
> **抓取方式**：DeepWiki MCP `read_wiki_structure` + `read_wiki_contents`（一次返回整仓库 wiki 全文）。
> **本地归档**：`~/ai/agent/awesome-agents/deepwiki/{name}/full.md`（全文）+ `structure.txt` + `skeleton.md`。
> **总索引**：`awesome-agents/DEEPWIKI-INDEX.md`（135 仓库状态 + 卡片进度枢纽）。

## 卡片格式（沿用 AgentRL生态深读 约定）

每张卡：**定位一句话 → 组件栈表（DeepWiki 蒸馏）→ 核心创新 → 架构关键入口（源码路径）→ 深读子页地图（全部子页中精选）→ 与讲透系列的对位 → 一句话总结**。

## 卡片清单（31 张，按主题分组）

### 横向总览
- [00-创新点与缺点总览](00-创新点与缺点总览.md) —— 31 框架的创新点★×缺点✗ 批判对照表 + 3 条跨流派洞察

### 编排框架流派
| 卡片 | 一句话定位 |
|---|---|
| [autogen-ms](autogen-ms-深读卡.md) | 微软 Actor 消息模型多 Agent 框架（⚠️维护模式→Microsoft Agent Framework） |
| [ag2](ag2-深读卡.md) | AutoGen 社区分叉继承者（ConversableAgent+GroupChat+Swarm/A2A） |
| [metagpt](metagpt-深读卡.md) | SOP 物化的软件公司流水线（watch 订阅拓扑+RoleZero） |
| [agentscope](agentscope-深读卡.md) | 阿里 model-driven 双层框架（不 imposing workflow） |
| [semantic-kernel](semantic-kernel-深读卡.md) | 微软三源函数归一+filter 切面（.NET/Python 双语言） |
| [haystack](haystack-深读卡.md) | 类型化 socket 组件 DAG+Snapshot 断点恢复 |
| [agency-swarm](agency-swarm-深读卡.md) | communication_flows 组织架构即代码 |
| [swarm](swarm-深读卡.md) | OpenAI 极简教育标本（handoff=函数返回值，已废弃） |
| [agentdock](agentdock-深读卡.md) | 可配置确定性 TypeScript 框架 |
| [agentgpt](agentgpt-深读卡.md) | 2023 前端跑循环架构标本（教具） |

### 编码 Agent 流派
| 卡片 | 一句话定位 |
|---|---|
| [aider](aider-深读卡.md) | SEARCH/REPLACE 容错级联+RepoMap PageRank |
| [cline](cline-深读卡.md) | VSCode Agent：Plan/Act 双模式+Focus Chain |
| [opencode](opencode-深读卡.md) | client-server 分离四端一体+三级上下文防御 |
| [openhands](openhands-深读卡.md) | CodeAct+沙盒即服务+EventStream（V0→V1 迁移中） |
| [plandex](plandex-深读卡.md) | 版本控制优先：plan 内建 git branch 沙盒 |
| [claw-code](claw-code-深读卡.md) | Rust 双轨+Worker Boot 状态机+Recovery Recipes |
| [codel](codel-深读卡.md) | Go 单步循环+LLM 选 Docker 镜像 |
| [agentk](agentk-深读卡.md) | LangGraph 微内核自进化（AgentSmith 造 Agent） |

### 研究/科学发现流派
| 卡片 | 一句话定位 |
|---|---|
| [gpt-researcher](gpt-researcher-深读卡.md) | Plan-and-Solve+三层 LLM+LangGraph 编辑部 |
| [ai-scientist](ai-scientist-深读卡.md) | idea→实验→论文→评审全闭环（$15/篇） |
| [adas](adas-深读卡.md) | Meta Agent Search：LLM 搜索发明 Agent 架构 |
| [aideml](aideml-深读卡.md) | Agentic Tree Search 的 Kaggle 竞赛 Agent |
| [actionbook](actionbook-深读卡.md) | 网站操作手册资产化（爬一次用千次） |

### 基础设施/记忆/自进化流派
| 卡片 | 一句话定位 |
|---|---|
| [phoenix](phoenix-深读卡.md) | OpenInference 数据契约+SpanFilter DSL |
| [screenpipe](screenpipe-深读卡.md) | 事件驱动屏幕捕获+pipe.md 声明式插件 |
| [aeon-agent](aeon-agent-深读卡.md) | GitHub Actions 当运行时+git 当数据库 |
| [agentic-context-engine](agentic-context-engine-深读卡.md) | Recursive Reflector+Skillbook 学习环 |
| [bernstein](bernstein-深读卡.md) | zero-LLM 协调+HMAC 审计链+确定性重放 |
| [aden-hive](aden-hive-深读卡.md) | Goal→Judge 验收驱动+coding agent 改图自进化 |
| [dspy](dspy-深读卡.md) | 声明式 Signature+编译器范式（prompt 优化=搜索问题） |
| [babyagi-ui](babyagi-ui-深读卡.md) | BabyAGI 五段循环 TS 标本（已归档教具） |

## 统计（2026-08-21 最终版）

- **135 仓库 = 98 有 DeepWiki 索引 + 37 未索引**
- **98 张深读卡全部完成**（每个已索引仓库一张，含创新点与缺点批判）
- 批判横向总览：[00-创新点与缺点总览.md](00-创新点与缺点总览.md)（98 框架 ★创新/✗缺点 全表 + 跨流派洞察）

## 目录结构

```
DeepWiki深读卡/
├── 00-创新点与缺点总览.md          # 98 框架批判总表（先看这个）
├── {name}-深读卡.md × 98           # 每仓库一张深读卡
├── 97-知识体系文档DeepWiki增补-副本.md   # AGENT-KNOWLEDGE-SYSTEM 第六部分副本
├── 98-生态分析文档DeepWiki增补-副本.md   # AWESOME-AGENTS-ANALYSIS 第七部分副本
├── 99-DEEPWIKI-135仓总索引.md      # 135 仓状态枢纽（wiki链接+归档状态+卡片进度）
└── skeletons/{name}-skeleton.md × 98   # 每仓库 wiki 导航骨架（页清单+标题树+行号）
```

**wiki 全文（full.md，54MB）**：数据源留在 `awesome-agents/deepwiki/{name}/full.md`（可再生——DeepWiki MCP 抓取脚本重跑即可）。精读路径：先看深读卡 → 查 `skeletons/{name}-skeleton.md` 定位页 → 按行号读 full.md 对应段落。

- 未索引名单见 99-索引（crewai/langchain/llama_index/memgpt/swe-agent/e2b 等大牌也在其中——DeepWiki 未索引 ≠ 不重要）

---
生成：2026-08-21 · 由 awesome-agents DeepWiki 全景抓取流水线驱动 · 98/98 完成
