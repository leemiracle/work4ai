# orchestration 精华合入 · 总入口

> 来源：[GitHub topics/orchestration](https://github.com/topics/orchestration) 中 **>10k stars** 的 17 个仓库。
> 精化产物：**7 个 opencode skill**（3 个先期 + 4 个本次新增），安装于 `~/.config/opencode/skills/`，opencode 启动时自动加载。
> 本文档是使用说明；蒸馏细节见 [orchestration精华笔记](./orchestration精华笔记.md)。

## 一、仓库 → skill 映射

| 仓库 | ★ | 类型 | 合入去向 |
|---|---|---|---|
| langgenius/dify | 152k | Agentic 工作流平台 | `orchestration-governance`（节点原语半） |
| code-yeongyu/oh-my-openagent | 67.9k | opencode 专用 harness | `orchestration-fleet` / `hyperplan` / `ultrawork`（先期） |
| apache/airflow | 46.5k | DAG 调度引擎 | `orchestration-dag` |
| stablyai/orca | 45.8k | 并行 agent 舰队 | `orchestration-fleet`（先期） |
| wshobson/agents | 38.8k | 多 harness 插件市场 | `orchestration-hyperplan`（先期） |
| statelyai/xstate | 30k | 状态机/actor | `orchestration-statemachine`（xstate 半） |
| kestra-io/kestra | 27.8k | 事件驱动编排 | `orchestration-dag` |
| deepset-ai/haystack | 26.2k | LLM 管道/上下文工程 | `orchestration-12factor`（haystack 增补） |
| humanlayer/12-factor-agents | 25.3k | Agent 工程原则 | `orchestration-12factor` |
| PrefectHQ/prefect | 23.6k | Python 工作流 | `orchestration-dag` |
| rowboatlabs/rowboat | 17.3k | 带记忆 AI coworker | `orchestration-statemachine`（rowboat 半） |
| cft0808/edict | 16.4k | 三省六部 multi-agent | `orchestration-governance`（edict 半） |
| triggerdotdev/trigger.dev | 16k | Durable AI 任务 | `orchestration-dag` |
| dagster-io/dagster | 16k | 资产/血缘编排 | `orchestration-dag` |
| apache/dolphinscheduler | 14.4k | 数据编排 | `orchestration-dag` |
| juspay/hyperswitch | 43.5k | 支付路由 | 不合入（支付域，与 AI agent 无关） |
| docker/compose · rancher | 38.1k/25.9k | 容器编排 | 不合入（基础设施域） |

同类仓库合并蒸馏原则：六大工作流引擎（airflow/prefect/dagster/kestra/dolphinscheduler/trigger.dev）的共同内核只有一套，不重复建 skill。

## 二、7 个 skill 速查

### 先期已有（3 个）

| Skill | 一句话 | 触发词示例 |
|---|---|---|
| `orchestration-fleet` | 并行子代理舰队：DAG 分解→按类别路由→写冲突隔离→汇合裁决 | "并行 agent"、"worktree 并行"、"同时调查" |
| `orchestration-hyperplan` | 写第一行代码前的五视角敌意计划评审 | "hyperplan"、"审计划"、"攻击这个计划" |
| `orchestration-ultrawork` | 不间断执行纪律循环，做完为止过完成审计 | "ultrawork"、"任务做完为止"、"不要停" |

### 本次新增（4 个）

| Skill | 来源 | 一句话 | 触发词示例 |
|---|---|---|---|
| `orchestration-12factor` | 12-factor-agents + haystack | Agent 工程十二原则：上下文裁剪、错误即文本、小而专 agent、无状态 reducer | "12-factor"、"压缩上下文"、"会话恢复"、"错误自愈" |
| `orchestration-dag` | airflow/prefect/dagster/kestra/dolphinscheduler/trigger.dev | 工作流引擎内核：幂等+内容寻址缓存、检查点续跑、显式 DAG、产物血缘、回填 | "幂等"、"断点续跑"、"重跑"、"血缘"、"批量" |
| `orchestration-statemachine` | xstate + rowboat | 显式状态机+guard 防跳步防假完成；Markdown 双向链接记忆图谱跨会话复利 | "状态机"、"防跳步"、"守卫"、"项目记忆"、"跨会话" |
| `orchestration-governance` | dify + edict | 变量契约+分权审核：规划-审议-调度-执行四权分立，封驳返工，全链审计 | "审核关卡"、"封驳"、"审计"、"迭代批处理"、"防死循环" |

## 三、使用说明

### 1. 触发方式
skill 无需手动调用——描述里定义的触发词命中时 opencode 自动加载。也可以显式说：
```
用 orchestration-governance 的分权审核流程处理这次重构
按 orchestration-dag 的幂等检查点协议跑这批分析
```

### 2. 组合拳（推荐的编排套路）

| 场景 | 组合 |
|---|---|
| 大型重构/迁移 | `hyperplan`（敌意审计划）→ `governance`（独立审议准奏）→ `statemachine`（状态机执行）→ `ultrawork`（做完为止） |
| 批量分析 N 个文件/仓库 | `dag`（幂等落盘+断点续跑）+ `fleet`（并行只读 worker）+ `governance` 的迭代错误分级（skip 策略） |
| 长会话防失控 | `12factor`（上下文裁剪+错误自愈）+ `statemachine`（进度快照落盘，压缩后可恢复） |
| 高风险变更 | `governance`（规划者≠审议者，封驳返工循环）+ `dag`（审计落盘） |

### 3. 维护
- 位置：`C:\Users\mirac\.config\opencode\skills\orchestration-*\SKILL.md`
- 修改后重启 opencode 生效（配置不热加载）。
- 每个 skill ≤64 行，刻意保持"一张纸能读完"；扩展细节写回本项目的笔记文档，不撑爆 skill。

## 四、明确不合入的仓库及理由

| 仓库 | ★ | 理由 |
|---|---|---|
| juspay/hyperswitch | 43.5k | 支付路由编排，域外 |
| docker/compose | 38.1k | 容器编排，基础设施域 |
| rancher/rancher | 25.9k | K8s 容器管理，基础设施域 |
| Avaiga/taipy | 19.4k | 数据应用 GUI 框架，与 agent 编排无关 |
| jina-ai/serve | 21.9k | 模型服务化部署，运维域（其 pipeline 思想已由 haystack 覆盖） |

---
生成：2026-08-15 · 由 opencode 从 GitHub topics/orchestration 蒸馏
