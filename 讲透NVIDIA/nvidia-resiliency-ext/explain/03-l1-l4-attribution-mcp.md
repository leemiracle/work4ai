# 03 · L1-L4 分层分析、归因编排与 MCP 生态

## 角色定位

L1-L4 是 restart_agent 五层流水线的后四层：L1 让 LLM 带工具分析证据，L2 把模型输出钉回真实日志防幻觉，L3 累积跨 cycle 历史，L4 落成重启/升级策略。四层各一个子包（`src/nvidia_resiliency_ext/attribution/restart_agent/l{1,2,3,4}/`），加上外围 orchestration/（服务化编排）与 mcp_integration/（工具协议），构成 NVRx 归因的"智能层"。设计文档 L1.md/L2.md/L3.md/L4.md/TOOLS.md/TAXONOMY.md 一一对应。

## 内部结构

- **L1（l1/，13 件+categories.json）**：最大件是 `openai_compatible.py`（2185 行）——`LlmConfig`（:63）、`ToolLoopSession`（:271）、`ToolRoundExecutor`（:374）实现多轮工具循环；错误分型三连 `LlmCallError`（:223）/`ModelEvidenceParseError`（:240）/`ModelEvidenceContractError`（:244）。工具面在 tools.py（1012 行）+ tool_contracts.py + contracts.py（L1ExecutionAssessment、EvidenceTools）；类别体系 categories.py:102（CATEGORIES）从 categories.json 装载，schema 校验 categories.py:23（`restart_agent_categories.v1`）；provider 差异收在 provider_profiles.py，响应合法性由 response_contract.py（L1ResponseContract）+ validation.py 把守。
- **L2（l2/）**：grounding.py 的 `model_visible_line_numbers`（grounding.py:15）/`model_visible_line_texts`（:39）/`text_contains_exact_value`（:88）——模型引用的每个值必须能在可见行文本中找到；audit.py 与 failure_facts.py 把通过核验的输出固化为事实链。
- **L3（l3/history.py）**：`evaluate_history`（history.py:51）、`evaluate_cycle_history`（:233）、`_evaluate_job_progress`（:286）——用 attempt_records 的历史判断"老毛病还是新问题"。
- **L4（l4/policy.py）**：综合证据输出决策建议，对接 launcher 的 attribution STOP。
- **orchestration/**（服务化）：http_api.py:31（log_submit_payload）/:70（post_log）/:93（get_log_response）暴露 HTTP；analysis_pipeline.py（230 行）串采集→分析→响应；progressive.py 支持增量分析；types.py（299 行）定义 RawAnalysisResultItem/AttributionRecommendation 等；llm_output.py（216 行）把结果映射成建议 payload。
- **postprocessing/ + coalescing/**：slack.py:88（send_slack_notification）、:148（should_notify_slack）做推送判定；pipeline.py（296 行）加工结果；coalescing/（coalescer.py + coalesced_cache.py + types.py:173）合并重复触发去抖。
- **mcp_integration/**（1690 行）：mcp_server.py:44（NVRxMCPServer，319 行）+ registry.py（AttributionModuleRegistry，322 行）+ module_definitions.py（232 行）注册 restart_agent/fr_analyzer 为 MCP 模块；mcp_client.py（553 行）与 server_launcher.py（182 行）管生命周期，transport_errors.py（36 行）处理传输失败。

## 外部连接

L1 的 LlmConfig 对接 OpenAI 兼容端点（provider_profiles.py 适配多家）；凭据从 attribution/api_keys.py 读环境变量或密钥文件。orchestration 的 http_api 被 attrsvc 的 app.py:131（create_app）复用成 FastAPI 服务；MCP server 可被 Claude 等外部 agent 直接调用（skills/nvrx-attr 的 SKILL.md 教 agent 怎么用）。legacy_logsage/（combined_log_fr.py、llm_merge.py）是旧路径，仍被部分 flow 引用但排除在 wheel 外。

## 数据流

L0Bundle（02 篇）→ L1 工具循环：ToolRoundExecutor（openai_compatible.py:374）驱动模型经 tools.py 取数 → 原始响应 → validation/response_contract 契约检查（不过则触发重试或契约修复，测试 _ContractRepairEvidenceExtractor test_restart_agent.py:684 钉死该路径）→ 分类落 categories.json 的类别 → L2 grounding.py:15 用可见行号核验每个引用 → audit/failure_facts 固化 → L3 history.py:51 结合 attempt_records 评估 → L4 policy 出建议 → orchestration 包装成 HTTP 响应（http_api.py:93）/Slack 通知（slack.py:88）/MCP payload。

## 设计决策

- **契约先于解析**：ModelEvidenceContractError 与 ModelEvidenceParseError 分开（openai_compatible.py:240/:244）——"格式错可修，语义违约要重跑"，重试策略因此能分级。
- **防幻觉用白名单可见性**：L2 不是事后检测幻觉，而是"模型只能引用喂给它的行"（grounding.py:39 直接给文本），把幻觉空间结构性压掉。
- **类别数据外置**：categories.json + schema_version 校验（categories.py:23）让类别表可不改代码演进。
- **去抖优先于即时**：coalescing 合并风暴式触发，避免集群级故障时 Slack/API 被打爆。
- **MCP 化而非 SDK 化**：归因能力对外暴露为 MCP 工具（mcp_server.py:44），外部 agent 与内部 attrsvc 走同一协议。

## 新人提示

读序 L1.md → TOOLS.md → L2.md；在 categories.json 里挑一个类别顺藤摸瓜找到它的判定工具；用 test_restart_agent.py:816（_OutputLimitEvidenceExtractor）理解输出截断的降级路径；改 http_api 记得 attrsvc 的 routes.py 只是薄壳（26 行），真正的桥在 restart_agent_backend.py（1556 行）。
