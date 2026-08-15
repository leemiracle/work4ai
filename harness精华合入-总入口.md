# harness 精华合入 · 总入口

> 来源：[GitHub topics/harness](https://github.com/topics/harness) 高星 37 仓（≥1K★，全量快照见 [透视GitHub-Harness高星仓库全景.md](./透视GitHub-Harness高星仓库全景.md)）。
> 精化产物：**1 个新 opencode skill**（`harness-engineering`），安装于 `~/.config/opencode/skills/`，opencode 启动时自动加载。
> 本文档是使用说明；蒸馏细节见 [harness精华笔记](./harness精华笔记.md)。

## 一、仓库 → skill 映射

| 仓库 | ★ | 类型 | 合入去向 |
|---|---|---|---|
| walkinglabs/learn-harness-engineering | 11.4k | 教学课程 | `harness-engineering`（五子系统+四层栈+会话生命周期） |
| walkinglabs/awesome-harness-engineering | 3.8k | 文献地图 | `harness-engineering`（产业共识与文献索引） |
| bytedance/deer-flow | 80k | SuperAgent harness | `harness-engineering`（skill 渐进加载+验证即证据条目） |
| ruvnet/ruflo | 67.9k | 元 harness | `harness-engineering`（Agent=Model+Harness 公式条目） |
| mindfold-ai/Trellis | 13.9k | 工程层 | `harness-engineering`（spec 晋升循环条目） |
| revfactory/harness | 8.8k | 元工厂 | `harness-engineering`（6 团队模式清单） |
| aden-hive/hive | 10.9k | 生产 harness | 不单设 skill——"一个 loop 控多个 loop" 已被 `orchestration-fleet`/`orchestration-dag` 覆盖 |
| zhayujie/CowAgent、nexent、Yuxi、qm 等 A 赛道 14 仓 | — | 全功能运行时 | 不合入（是产品不是方法；其思想已被公式/五子系统吸收） |
| agentmemory、memU、memsearch、puppyone | — | 记忆/上下文 | 不合入（记忆层已有 hermes 式 MEMORY.md 约定 + `orchestration-statemachine` 记忆图谱） |
| openai-agents-python、pydantic-ai、harness-sdk、eve、agenta、agentscope-java | — | SDK/框架 | 不合入（写代码时用库，不是 agent 行为纪律） |
| alibaba/open-code-review、Unity-Skills、modlens、Chorus、goclaw | — | 领域专用 | 不合入（域外） |
| polyaxon、llm-space、CommandCodeAI 等 | — | 工具/存量词 | 不合入（观测工具或非 agent 义） |

蒸馏原则：harness 镜与 orchestration 镜互补不重叠——**编排管流程（DAG/状态机/舰队），harness 管环境（指令/状态/验证/边界/生命周期）**；loop/graph 层交叉处归 orchestration-*，环境五子系统归本次新 skill。

## 二、skill 速查

### 本次新增（1 个）

| Skill | 来源 | 一句话 | 触发词示例 |
|---|---|---|---|
| `harness-engineering` | learn-harness + awesome + deer-flow/ruflo/Trellis/revfactory | 给模型造可靠工作环境：五子系统检查单、四层栈定位、会话生命周期仪式、最小四文件落地、6 团队模式 | "harness"、"装一个 harness"、"agent 不可靠"、"跑不完任务"、"会话接续"、"宣布完成" |

### 与既有 skill 的组合拳

| 场景 | 组合 |
|---|---|
| agent 干活不可靠/提前宣布完成 | `harness-engineering`（五子系统体检：验证即证据）→ 缺哪补哪 |
| 长任务跨会话 | `harness-engineering`（progress/feature_list/handoff）+ `orchestration-statemachine`（防跳步守卫） |
| 大型任务组织形态选型 | `harness-engineering` 的 6 团队模式选架构 → `orchestration-fleet` 并行执行 → `orchestration-hyperplan` 敌意审计划 |
| 造完 harness 要评测 | `harness-engineering` 的基准观（测 harness 不测模型）+ awesome 清单基准索引 |
| 方法论自改进 | Trellis 的 spec 晋升循环 + `orchestration-ultrawork` 完成审计 |

## 三、使用说明

1. **触发**：无需手动调用——命中描述词自动加载。也可显式说：`用 harness-engineering 的五子系统给这个项目做体检` / `按会话生命周期仪式收尾这次任务`。
2. **位置**：`C:\Users\mirac\.config\opencode\skills\harness-engineering\SKILL.md`；修改后重启 opencode 生效。
3. **克制**：skill ≤64 行一张纸读完；扩展细节写回本项目的 [harness精华笔记](./harness精华笔记.md)，不撑爆 skill。

## 四、后续候选（不合入但留观）

| 仓库 | ★ | 留观理由 |
|---|---|---|
| penguin-harness | 1.3k | RSI（自进化）若成主流，可能需要独立 skill；暂与 `orchestration-ultrawork` 完成审计重叠 |
| deer-flow/llm-space | 1.6k | harness IDE 思想（trace/replay）若 opencode 原生缺口扩大再议 |
| alibaba/open-code-review | 20.5k | 若项目引入 PR 自动评审，可提炼确定性管线+LLM 分工检查单 |

---
生成：2026-08-15 · 对齐 [orchestration精华合入-总入口.md](./orchestration精华合入-总入口.md) 的体例
