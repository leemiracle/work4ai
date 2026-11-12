# 13 · 遥测与反馈：GrowthBook、三通道事件、RL 数据飞轮

> 证据：minified 源码偏移考古 + 1634-chunk import 图分类 [S]。深报告
> （feature≥434/事件≥1689 全表+OTel 三通道全链+反馈四路）：
> `rea-claude/reports/13-telemetry.md`（37KB）。

## 1. 实验系统勘误：GrowthBook 非 statsig [S]

本版（v2.1.261）**无 statsig**（仅剩 `.claude/statsig` 遗留目录名）；实验系统
实为 **GrowthBook**：clientKey 走 api.anthropic.com 自建代理 remoteEval，
曝光事件 `growthbook_experiment` 与行为事件同管线汇合。经 import 图分类出
**feature ≥434 / 遥测事件 ≥1689**（含 Artifact 放量族等 codename 族谱）。

## 2. OTel 三通道 [S]

1. **1P 事件**：OTel Logger → `/api/event_logging/v2/batch`，磁盘持久化重试
   队列（发不出去先落盘）；
2. **Datadog 第二通道**：明文公钥 intake、197 事件白名单、字段清洗、
   userBucket 匿名分桶；
3. **beta tracing**：可导出完整 prompt（env 受项目级 settings 防投毒保护）。

## 3. 反馈四路 [S]

/bug 命令、SendFeedback 工具（模型起草反馈文本）、六型 survey（用户按键
responded 0-4）、claude doctor 诊断包。匿名化为**构造期白名单**（而非运行时
清洗——不在白名单的字段根本不进事件）。

## 4. RL 视角：数据飞轮（点睛）[S]

四级关联键齐全：session_id（贯穿）+ user_message_uuid（回合）+
request_id/queryChainId+depth（请求链）+ tool_use_id（工具调用）。
**这套遥测在事件粒度上就是完整的离线 RL 轨迹采集层**。十组三元组映射节选：

| 策略 | state | action | outcome/reward |
|---|---|---|---|
| 工具执行 | tengu_api_query{model,effort,depth} | tengu_tool_use_success{tool,durationMs,rssDelta} | 成败+时延+内存+**bash exit_code** |
| 回合终局 | tengu_started | turn 内 tool_use 序列 | **tengu_sdk_result{is_error,num_turns,saw_retry,saw_compact}**=episode 级信号 |
| 权限分类器 | tengu_auto_mode_decision | allow/deny/ask | tengu_auto_mode_outcome+用户否决=对分类器的 reward |
| **Edit 采纳** | file_operation | 模型 diff | **tengu_ext_diff_accepted/rejected——官方点名的 RLHF 信号**（法务条款明言 acceptance 构成可训练 Feedback） |
| 满意度 | survey appeared | 用户按键 | response 0-4（稀疏干净） |
| 成本策略 | cost_threshold_reached | lowpri/换模 | tengu_api_success 全量 token/时延账单 |
| 压缩策略 | attention_budget_cycle | precomputed_compact_{arm_gated,consumed}——**arm 字样=多臂实验** | compact_failed+token 节省 |
| 冗余检测 | file_history 快照 | Read 调用 | **tengu_file_read_dedup=harness 拦截的无效动作=负 reward 候选** |
| 自愈熔断 | 连续失败计数 | 再试/跳过 | auto_compact_circuit_breaker（episode 内策略切换） |
| 平台 bandit | growthbook_experiment | 臂分配 | 全部 outcome 按 variation_id 分组=off-policy eval 管线 |

**命名陷阱**：`tengu_rl_*` 是 rate-limit checkpoint，与 RL 无关。

**飞轮闭环**：客户端事件 → 落仓 → 四级键关联成轨迹 → 臂标签分层 →
sdk_result+diff_accepted+survey 混合 reward → 反哺训练与放量决策。
**Claude Code 本体=部署在百万终端上的 trajectory collector**。

## 5. 手搓启示（→ rl-and-agents/）

1. reward 不用发明：exit_code/采纳/去重拦截/熔断这些事件**早就该记**——
   mini agent 第一天就该埋 (state,action,outcome)，详见
   [agent-loop-的-RL-形式化.md](rl-and-agents/agent-loop-的-RL-形式化.md)；
2. 构造期白名单匿名化比运行时清洗可靠——字段不进白名单根本不存在；
3. 臂标签（experiment_id/variation_id）写进每个事件=免费获得 off-policy
   评估能力——自建产品抄这条就能做线上策略评估；
4. 四级关联键（session/turn/request/tool_use）是多粒度 credit assignment 的
   数据结构基础——先定键再定事件。
