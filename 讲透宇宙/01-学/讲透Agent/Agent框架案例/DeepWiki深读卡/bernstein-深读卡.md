# bernstein 深读卡 —— 零 LLM 协调的确定性多 Agent 编排平台：纯 Python 指挥家调度 40+ CLI coding agents

> **定位**：bernstein（致敬指挥家 Leonard Bernstein）是为 CLI coding agents（Claude Code、Aider、Codex 等 40+ adapter）打造的确定性多 Agent 编排平台。核心哲学是 **zero-LLM coordination**——协调逻辑全用纯 Python 状态机实现，LLM 只在每个 agent 内部生成代码，从而杜绝递归 Agent 系统常见的幻觉循环，且"昨天生成的 plan 今天重放得到完全一致的任务图"。配套 HMAC-SHA256 audit chain、签名 lineage、air-gap 部署，面向受监管团队的审计级工程。

> **本地**：`repos/bernstein`（sipyourdrink-ltd/bernstein）｜**深读**：deepwiki 48 子页归档 `deepwiki/bernstein/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 前端层（CLI/TUI/Web） | 提交 goal、监控进度、审批 | `src/bernstein/cli/`、`tui/app.py`（Textual）、React Dashboard + PWA |
| Task Server（FastAPI，默认 :8052） | 任务状态枢纽：生命周期、认证/限流、审计、SSE 事件 | `core/routes/`、`core/server/server_supervisor.py` |
| Orchestrator | 单线程确定性 tick 循环：调度/认领/监控 | `orchestration/orchestrator.py`、`tick_pipeline.py` |
| Planning | goal → Plan YAML（任务 DAG）→ 分解/refinement | `planning/`、`TaskPlan`、Manager role + Adversary Veto |
| Agent 执行 | 每 Task 一个 ephemeral 进程 + Git worktree 隔离 | `agents/spawner_core.py`、Role catalog（manager/backend/qa…）、Agent Card（JWS 签名） |
| Adapters（40+） | 统一封装各家 CLI agent | `adapters/base.py: CLIAdapter`（claude/aider/codex/gemini/cursor…） |
| 持久化 | 文件状态即真相，崩溃可恢复 | `.sdd/`（tasks JSONL、runtime 信号、wal/）、WAL + `WALRecovery`、可选 PostgreSQL/Redis |
| 验证与合规 | 完成信号、防篡改审计、溯源 | Janitor、Completion Signals、`security/audit_chain.py`、Lineage v1/v2、`bernstein-verify` |
| 智能层（边缘） | 模型选择/成本/自进化（均在编排环**外**） | `routing/bandit_router.py`（contextual bandit）、prompt cache locality、`bernstein evolve`（L0–L3 风险分级） |

## 二、核心机制

1. **单线程分频 tick 循环**（来源：Orchestrator and Task Lifecycle, L1636）：Fast Path 每 tick（心跳刷新/死 agent reap/文件锁）、Normal Tick 每 6 ticks（`fetch_all_tasks()` → `group_by_role()` → `claim_and_spawn_batches()`）、Slow Tick 每 30 ticks（知识库刷新/成本 rollup/janitor 验证）。单线程设计从根本上避开状态迁移的并发危险。
2. **Task 状态机 + 文件所有权互斥**（来源：Core Concepts L654 + Orchestrator L1636）：`OPEN → CLAIMED → IN_PROGRESS → DONE → CLOSED`（或 `FAILED`）严格校验迁移；批派发前做依赖过滤 + `infer_affected_paths()` 推断文件占用，`_file_ownership` 地图拦截文件重叠的任务并发，防 merge 冲突。
3. **WAL + DLQ + Drain 三重可靠性**（来源：Orchestrator L1636）：claim/complete/fail 先写 `WALEntry` 再落 TaskStore；启动时 `WALRecovery` 重放（如孤儿 CLAIMED 复位 OPEN）；反复失败任务进 Dead Letter Queue 隔离；`SIGTERM` 触发 drain——向 `.sdd/runtime/signals/` 投 SHUTDOWN 哨兵，agent 自觉 `git commit -m "[WIP]"` 存档，超时 60s 后 SIGKILL，最后 flush WAL。
4. **审计级确定性**（来源：Overview L6 + Core Concepts L654）：每个调度决策入 HMAC 链式 audit log（每事件含前一事件 HMAC，可离线验证）；每个 artifact 有 Lineage 溯源回 task 与 agent session；agent 开工即签发 Agent Card（detached JWS）——三者合起来支撑"重放即复现"的可审计承诺。

## 三、与讲透系列的对位

| 讲透系列 / 我们的项目 | bernstein 对位 | 对照要点 |
|---|---|---|
| agent-development（LangChain/LangGraph/CrewAI 选型） | zero-LLM 编排 vs LLM-in-the-loop | 第三条路线：协调确定性、LLM 只当"乐手" |
| 讲透Agent / LangGraph 图执行 | Plan YAML 任务 DAG + tick 调度 | 声明式 DAG 相同，执行器是纯 Python 状态机 |
| rl-learning（bandit/PPO） | Model Router：contextual bandit 选模型 | 学习只出现在路由边缘，不入协调环 |
| llm-mastery 推理优化（KV Cache） | Prompt Engineering and Cache Locality | 按 cache key 组织 prompt 前缀，控漂移 |
| neo-os / ai-os-dd（可解释、可验证） | audit chain + deterministic replay | 同一哲学：可审计确定性 > 涌现智能 |
| Git worktree 工作流 | Worktree isolation + drain 时 [WIP] commit | 与我们 worktree/devcontainer 会话机制互鉴 |

## 四、关键入口

```
repos/bernstein/
├── src/bernstein/cli/main.py                    # CLI 总入口（init/run/doctor/status/evolve）
├── src/bernstein/core/orchestration/orchestrator.py  # tick 循环 + WAL 心脏
├── src/bernstein/core/orchestration/tick_pipeline.py # 分批/依赖过滤/派发
├── src/bernstein/core/tasks/{models,task_lifecycle,task_store_core}.py  # Task 状态机
├── src/bernstein/core/agents/spawner_core.py    # spawn/watchdog/reap + shutdown 哨兵
├── src/bernstein/adapters/base.py               # CLIAdapter 基类（40+ adapter 之根）
├── src/bernstein/core/security/audit_chain.py   # HMAC 审计链
├── bernstein.yaml                               # 项目配置
└── .sdd/                                        # 运行时状态真相（tasks/runtime/agents/wal）
```

## 五、深读子页地图（48 页精选 6）

| 页 | full.md 行 | 为何值得读 |
|---|---|---|
| Core Concepts and Terminology | L654 | 全部核心抽象一张表：Task/Role/Janitor/Agent Card/.sdd |
| Architecture | L966 | 三层模型 + 文件状态模型的全景图 |
| Orchestrator and Task Lifecycle | L1636 | tick 分频/状态机/WAL/DLQ/drain，机制最密集 |
| Audit Chain, Lineage, and Compliance | L4799 | HMAC 链 + JWS 签名 + Sigstore/SLSA-3 合规栈 |
| Model Router and Contextual Bandit | L6353 | "智能"如何被限制在路由边缘 |
| Self-Evolution Loop | L7000 | `bernstein evolve`：L0–L3 风险分级的自我改造管线 |

## 六、与"我们"的关系（一句话）

bernstein 是"用工程确定性驯服多 Agent"的教科书级开源范本——讲透Agent 系列讲框架原理，bernstein 给出可审计可重放的工业实现，其 zero-LLM 协调哲学与 neo-os 的可解释性路线同源，值得作为 agent-development 的对照案例库。

---
生成：2026-08-21 · deepwiki 48 页全归档
