# Agent 编排案例 · 索引

> 一句话定位：**Agent 的"指挥部"——orchestration（编排）层的开源实现精读与精化合入**：一个 lead 怎么把任务拆给多个并行 agent、怎么保持纪律跑到完成、怎么在写码前粉碎坏计划。
>
> 与 [`Agent框架案例/`](../Agent框架案例/)（框架层：进程/循环/工具/沙箱）、[`Agent上下文案例/`](../Agent上下文案例/)（上下文层）、[`Agent记忆系统案例/`](../Agent记忆系统案例/)（记忆层）、[`Agent多模态案例/`](../Agent多模态案例/)（多模态层）平行，本目录是**编排层**：多个 agent 之间的分治、调度与裁决。

## 文件

| 文件 | 内容 | 状态 |
|---|---|---|
| [01-编排全景-25仓速览.md](./01-编排全景-25仓速览.md) | GitHub `topic:orchestration & stars>10K` 全量 **25 仓**（2026-08-15 API 快照）：三代编排谱系（数据管道 → AI 工作流 → 编码 agent 舰队）、每仓一句话与"可偷什么" | 已完成 |
| [02-oh-my-openagent精读.md](./02-oh-my-openagent精读.md) | oh-my-openagent（67.9k★，OmO）源码级 README 精读：11 agent 编排体系 / ultrawork 纪律循环 / Team Mode / hash 锚定编辑 / 三大杀手级功能的数据证据 | 已完成 |
| [03-wshobson-agents市场精读.md](./03-wshobson-agents市场精读.md) | wshobson/agents（38.8k★）多 harness 插件市场：一份 Markdown 源 → 五 harness 原生产物 / 94 插件-203 agent-175 skill 分层 / plugin-eval 三层质量评估 | 已完成 |
| [04-opencode合入手册.md](./04-opencode合入手册.md) | **落地层**：从上述仓库精化合入本机 opencode 的 3 个原生技能（ultrawork 纪律循环 / hyperplan 五敌评审 / fleet 舰队编排）的使用说明 + 两个可选的整装安装路径 | 已完成 |

## 速查：什么问题查哪里

- **让 agent 不半途而废、跑到可验证的完成** → [04 手册](./04-opencode合入手册.md) 的 `orchestration-ultrawork`
- **动手前怕计划是错的** → `orchestration-hyperplan`（五批评者）
- **大批量独立文件/仓库/主题要处理** → `orchestration-fleet`（并行分治）
- **想装完整版第三方编排** → [04 手册](./04-opencode合入手册.md) §4（OmO 一行安装 / wshobson make 安装，含遥测关闭方法）
- **编排领域的星力分布与谱系** → [01 全景](./01-编排全景-25仓速览.md)

## 数据快照声明

星数与仓库信息均为 2026-08-15 GitHub Search API 实抓（`topic:orchestration stars:>10000`，total_count=25，incomplete_results=false）。OmO/wshobson 精读基于当日抓取的仓库 README；未逐行核对源码的论断均标注了来源层级。
