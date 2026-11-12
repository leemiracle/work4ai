# explain-07 · agent/engine.go — ReAct Agent 引擎主循环

> **文件**：`internal/agent/engine.go`（987 行）
> **所属层**：Agent 引擎与沙箱执行层（导览第 8 步）
> **一句话定位**：AgentEngine 的"脊柱"——定义引擎状态与跨轮无状态设计，实现 Think→Analyze→Act→Observe 主循环，内置上下文压缩、token 校准、中途插话三大生存机制。

## 1. 角色定位

Agent 模式让 LLM 自主调用工具，驱动者是 `AgentEngine` 的 ReAct 循环。本文件解决三层问题：**循环控制**（何时续/停/卡死怎么办）、**上下文经营**（长对话在窗口内活下来）、**事件输出**（经 EventBus 流给前端）。关键设计在 L29 注释：引擎**跨轮无状态**，历史每轮由调用方从 DB 重建传入。

## 2. 内部结构

- **结构体与构造**（L35-137）：约 25 字段五组——核心依赖、提示词素材（KB/pinned MCP/技能/记忆信封）、token 经营（双估算器+compactor+overflowRecovered）、插话注入、可选项（skillsManager、imageDescriber）；构造时继承上轮缩放比（L112）并组装 compactor（L127）。
- **token 估算**（L261-290）：上轮 API usage 是已计费基线，本轮只对**增量消息**做 BPE 估算（L270 跳过已计入 completion 的回复）；工具 schema 不计入（L248：232 个约 10.5 万 token，加了每轮误判超限）。
- **入口 Execute**（L294-414）：defer 清理工具（L303）；L326 顶层 agent.execute span；L370 组装消息并 `RefreshMCPTools`；L387 进主循环。
- **主循环 executeLoop**（L501-592）：L522 用 `WithoutCancel` 保证完成事件**恰好发一次**（含取消路径）；L535 条件=预算内或插话加时（负 MaxIterations=不限轮，L460）；L539 每轮查取消，有工具结果则"抢救"出答案；L587 轮次耗尽由 `handleMaxIterations` 兜底。
- **单轮 runReActIteration**（L616-914）：L681 压缩旧历史、L693 排空插话、L708 Think；L722 溢出时压缩重试一次；L755 **卡死检测**（连续多轮相同内容且无工具调用则收束）；L805 判定终止——含空回复重试（L809 追加催促消息）与收尾插话续跑（L859）；L898 Act+Observe。

## 3. 外部连接

import agent 子包与 models/chat、event。本文件是骨架，方法按阶段拆在兄弟文件：think.go（callLLMWithRetry L482）、act.go（executeToolCalls L225）、observe.go（analyzeResponse L372）、steer.go、finalize.go。创建方 agent_service.go:233；事件消费方 handler 层 agent_stream_handler.go（SSE）。

## 4. 数据流

"帮我把报表清洗后存回知识库"：agent_service 组装引擎（MCP 工具、沙箱、VLM）→ `Execute` 重建历史拼系统提示词 → 第 1 轮 LLM 返回思考"先读文件"+ `shell_exec` 调用 → 非终态 → 沙箱执行、输出追加进消息 → …… → 某轮自然停止且无工具调用 → 写 FinalAnswer → emitCompletion 持久化并通知前端；中途"停止"则 L539 合成抢救答案退出。

## 5. 设计决策

① "昂贵重试只许一次"（overflowRecovered/steerOverruns，L57/L83 注释写明理由）；② "usage 基线+增量估算"比纯本地估算准、比等 API 报错省；③ `iterOutcome` 枚举（L597）收拢分支，单轮装闭包让 defer 全覆盖。批评点：25 字段、13 个 Set*，构造知识分散在 agent_service。

## 6. 新人提示

① 改循环先读 L515 的"恰好一次完成事件"契约——handleComplete 靠它落库 RoundSteps，多发/漏发出错；② `IsComplete=false` 且带部分结果合法（取消路径），别假设有 FinalAnswer；③ 负 MaxIterations=不限轮，有卡死检测兜底；④ 搭配 DeepWiki《3.3 Agent System and ReAct Engine》的 ReAct Loop 节与《8.2 Agent and Conversation Configuration》。
