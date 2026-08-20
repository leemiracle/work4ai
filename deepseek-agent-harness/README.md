# deepseek-agent-harness

> DeepSeek 引擎 + 六组件骨架 + **Agent 设计与应用领域插件**（2026-08-20 新建）。
> 家族第五成员，也是"自举"成员：**用 harness 的方法论造 agent 系统**——知识底座直接挂网 [harness工程手册](../工程化手册库/harness工程手册/README.md) 15 章全量。

## 定位

- **设计侧**：六组件完整性工程（检查单驱动，knowledge/agent_design.md）
- **应用侧**：agent 系统的验证与审计（轨迹=证据链）

## Agent 版金字塔

| 层 | 工具 | 防的失败 |
|---|---|---|
| L2 | agent_trace_check.py | 轨迹断头/孤儿工具结果（循环中断不可见） |
| L3 | agent_smoke.py | 循环→轨迹→校验 链路缺失 |
| L4 | agent_eval.py | 成本回归看不见（--baseline 对比 tokens/轮次） |

governance 三病 agent 形态：Goodhart = **跳过校验/假基线/选择性报告 + 自我提权（改 authorize 被拦）**；盲区 = 六组件任一改动的影响面；冲突 = 轨迹/状态目录。

## 特色： authorize 的"自举"红线

本插件把 `hooks/authorize.py` 自身设为保护对象——**agent 改自己的权限规则 = 提权，fail-closed 拦截**。这是手册 11 章"进化闭环须有门禁"在权限层的落地。

## 快速开始

```bash
python3 agent_host.py --self-test
python3 tools/agent_trace_check.py --write-sample && python3 tools/agent_trace_check.py sample_trace.jsonl
python3 tools/agent_smoke.py
export KH_API_KEY=... AGENT_PROJECT=/path/to/agent-code
python3 agent_host.py --task "给 agent 的 write_file 工具加路径白名单并过 L2-L4"
```

## 结构

```
agent_host.py        宿主：六组件 + cascade，agent 工具表
engines/ governance/ 家族复用；hooks/authorize.py agent 特化（拦删轨迹/无预算对外/提权写）
tools/agent_lint.sh / agent_test.sh          L1/L2
tools/agent_trace_check.py   L2 轨迹校验（schema+配对，含 --write-sample 样例）
tools/agent_smoke.py         L3 循环冒烟（零 API 依赖）
tools/agent_eval.py          L4 任务+成本统计（--baseline）
knowledge/agent_design.md    六组件检查单+生态工具带+手册/Agent框架案例 挂网
AGENTS.md                    agent 工程契约（轨迹是证据链/权限 fail-closed/单 agent 优先）
```
