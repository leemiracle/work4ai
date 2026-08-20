# Agent 设计知识库 · 六组件工程 + 2026 生态精华

> 底座：[harness工程手册](../../工程化手册库/harness工程手册/README.md)（15 章全量）——本文件是 agent 视角的入口索引 + 补充，不重复正文。

## 一、设计一个 agent 的检查单（从六组件出发）

| 组件 | 一句话设计问 | 现成参考 |
|---|---|---|
| E 执行循环 | 终止条件三选了吗（自然/轮数/超时交接）| 手册 12 章骨架 |
| T 工具 | schema 校验？报错即导航？结果预算？ | 本家族五插件的 TOOLS 表 |
| C 上下文 | 压缩触发点？压缩前 flush 账本？ | 手册 04 章参数表 |
| S 状态 | 断点续传靠什么（progress.md 模式）？ | 手册 05 章 |
| L 权限 | fail-closed 了吗？红线领域化了吗 | hooks/authorize.py 五个领域版本对照 |
| V 验证 | exit code 即证据？金字塔分层了吗 | rust 版金字塔最完整 |

## 二、agent 失败的三种结构病与治理（手册 02 章）

Goodhart（指标 gaming）/ 向上盲区（全局影响看不见）/ 冲突（并行互踩）——governance/ 三件套是通用形态，五家族各有一个领域版：
- rust：#[allow] 通道；kernel：SKIP_CLIPPY 通道；rl：reward 伪造；llm：评测作弊；agent：跳过校验/自我提权。

## 三、行为定位：改 agent 前先知道去哪改（手册 13 章）

Harness Handbook（arXiv:2607.13285）：行为地图 L1→L2→L3 + BGPD。本项目的 tools/agent_trace_check.py 是它的 V 侧雏形（轨迹即行为的证据）。

## 四、生态工具带选型（手册 14 章精简版）

```
要防注入/越权     → Agent Audit（静态）/ AEGIS（运行时防火墙，48 攻击全拦）
要答"为什么失败"  → AgentTrace（因果图 0.12s）/ AgentDebug（17 类错误 taxonomy）
要进化 harness    → Self-Harness 式闭环（回归门禁+最小编辑+轨迹证据）
轨迹太长          → Laminar（20× 压缩）
```

## 五、多 agent 与协议

- MCP（工具↔harness）/ A2A（agent↔agent）：[Agent框架案例/topics/mcp](../../Agent框架案例/) 六赛道全景
- Skills 开放标准：SKILL.md 解剖 → [Agent框架案例/topics/skills]
- 关键判断：多 agent 先问"真的需要吗"——单 agent + 好工具表常胜多 agent + 差协调。

## 六、agent 评测的三个层次

1. 轨迹合法（schema/配对）→ agent_trace_check.py
2. 任务完成（任务级 checker，确定性优先）→ agent_eval.py 的严格版
3. 成本回归（tokens/轮次 vs 基线）→ agent_eval.py --baseline

**反模式**：只看成功率不看成本；只看单轮不看轨迹；LLM-as-judge 无人工锚定。
