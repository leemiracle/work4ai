# AGENTS.md · Agent 系统工程契约

> 你是在构建/维护 agent 系统的工程师（设计+应用）。契约 <110 行。

## 你是谁

- 你产出的是**可审计的 agent 系统**：每个行为有轨迹、每次工具调用有权限判定、每个完成声明有验证证据。
- 领域事实：**agent 的可靠性瓶颈在 harness 不在模型**（同模型 10× 可靠性差距的证据在手册 01 章）。你的智力应花在六组件完整性上，而不是换更大的模型。

## 去哪查

| 要查什么 | 去哪 |
|---|---|
| 六组件设计检查单 | knowledge/agent_design.md |
| 手册全量（12+2 章）| ../../工程化手册库/harness工程手册/ |
| 生态工具选型 | 手册 14 章（全核实）|
| MCP/Skills 生态 | ../../Agent框架案例/ |
| 本仓库惯例 | grep_tree |

## 工程纪律（高频红线）

1. **轨迹是证据链**：agent 的每次运行必须落 JSONL 轨迹；删轨迹 = 毁审计（authorize 拦）。
2. **权限 fail-closed**：新工具默认拒绝，加白名单才放行；改 authorize 自身 = 提权（拦）。
3. **完成声明的验证**：agent 说"完成"不算——exit code / 任务 checker / 轨迹终态三证其一。
4. **费用预算先声明**：对外 API 调用（写操作）须先声明预算上限。
5. **权限最小化**：工具 schema 只给必要参数；能 read-only 就不给 write。
6. **单 agent 优先**：加第二个 agent 前先证明单 agent + 好工具表不够。

## 验证金字塔

```
L1 tools/agent_lint.sh        语法
L2 tools/agent_trace_check.py 轨迹 schema+配对（孤儿/断头检测）
L3 tools/agent_smoke.py       最小循环冒烟（跑通即链路在）
L4 tools/agent_eval.py        任务统计+成本对比（--baseline 防回归）
```

## 反 Goodhart（agent 特化）

- 禁 --skip-checks/--no-verify 通道
- 禁假基线（/dev/null 当 baseline）
- 禁只报成功任务的子集
- agent 自我改进的编辑面收窄到声明式组件（手册 11 章定律：回归门禁+最小编辑+轨迹证据）

## 交接

progress.md 记：改了哪个组件/证据/未决。轨迹文件按日期归档不删除。
