# 05 · MCP 安全三分析器：least_privilege · rug_pull · tool_poisoning

## 一、角色定位

skill 声明的 MCP 服务器与工具元数据有自己的攻击面，这是 SkillSpector 区别于普通 SAST 的特色线。三个分析器各守一角：`mcp_least_privilege`（735 行）对账"声明的权限 vs 代码实际能力"的差集；`mcp_rug_pull`（715 行）查版本钉扎与上线后偷改定义的风险指标；`mcp_tool_poisoning`（1874 行，MCP 线最重）查工具描述文本里的投毒信号（隐藏指令/Unicode 欺骗/override 短语），并用 LLM 做"描述-行为失配"判定（TP4）。三者都以 manifest 为门控——没有 manifest 就返回 not_applicable/MANIFEST_ABSENT 而非 failed（least_privilege :467-479、rug_pull :657-669、tool_poisoning :1655-1667）。docs/B.3.1-mcp-least-privilege.md 与 B.3.2-mcp-tool-poisoning.md 是官方设计文档。

## 二、内部结构

**mcp_least_privilege.py**：能力正则表 `_CAPABILITY_PATTERNS`（:63-113）六类——shell（subprocess/curl/wget/chmod…）、network（requests/httpx/fetch(…）、file_read/file_write（含 open 模式参数内联匹配）、env、mcp（MCPClient 等）；权限字符串→类别 `_PERM_TO_CAPABILITY`（:121）、Claude 工具名→类别 `_TOOL_TO_CAPABILITY`（:354，Read/Write/Bash→对应能力）。`node`（:460-735）流程：无 manifest 或无可执行文件→not_applicable（:467-495）→ 逐可执行文件 `_detect_capabilities`（:285，64K 窗口+4K 重叠，:52-53）→ 四规则：**LP2** 通配权限 *‌/all/full/any（:537-560，`_WILDCARD_PERMS` :60）、**LP3** 零声明但有能力（:562-588）、**LP1** 能力未被声明覆盖（:609-644，HIGH，测试文件独有的能力降置信 0.55 vs 0.75，:599-619）、**LP4** 过度声明（:672-678 附近，"over-declared permission maps"）。注释 :519-521 点明关键顺序约束：**超时绝不能把部分观察能力集误判成 LP4**——可执行文件先全部扫完才做整体比较。

**mcp_rug_pull.py**：`_RugPullBudget`（:68）的 `check_runtime`（:79-94）读共享时钟，超限抛携带 reason/metrics 的内部错误。规则：**RP1** 未钉扎引用（:210-389）——npx 无 @version（:219-251）、uvx 无 ==version（:254-284）、pip install 无 ==version 且包含 mcp（:287-310），命中行后 256 字符内查版本钉扎豁免；**RP2** manifest 权限扩张语言（:391-420，"未来可能请求更多权限"类表述，`_PERMISSION_EXPANSION_PATTERNS`）；**RP3** skill 版本未钉扎（:428-470，*‌/latest/any 或 >=/^ 宽约束）。`_check_manifest_changes`（:492-608）在新旧 manifest diff 上重放 RP1/RP2/RP3——工具参数增删改默认值（:595-607）也在其中。`node`（:651-715）按 planned_paths 逐文件出账本，超限时未完成路径记 PARTIAL（:697-708）。

**mcp_tool_poisoning.py**：静态三连 + LLM 一击。`_extract_metadata_texts`（:169）从 manifest 抽全部元数据文本并标注 is_identifier。**TP1** 隐藏指令（:242-413）：指令关键词（:213）、HTML/Markdown 注释（:219-222，正则刻意写 `<\\?!--` 容错转义形态）、零宽字符后跟可见字（:231，`_ZERO_WIDTH_RE`）、50+ 字符 base64 块（:234）、data:text/ base64 URI（:239）；**TP2** Unicode 欺骗（:514-677）：RTL 覆盖字符（:479）、不可见字符 U+00AD/U+034F/U+2060（:481）、同形字表 `_CONFUSABLES`（:137）、脚本前缀判定 `_get_script_prefix`（:484）抓"拉丁词里混西里尔字母"；**P9** 空白填充（:415-477，仅自由文本字段）；**TP3** 描述投毒短语（:712-875）：override 指令（:679-683）、系统提示词 token SYSTEM:/<system>/[INST]（:685-689）、外传动词（:691）、恶意默认 URL（:702-706）与 shell 命令（:708-710）。TP3 的 loopback 豁免注释（:695-701）值得细读：负向前瞻若不锚定主机边界，`http://localhost.evil.com/exfil` 会因前缀匹配 "localhost" 被误放行——已修复为 `(?:localhost|127\.0\.0\.1)(?:[:/?#]|$)`。**TP4** 描述-行为失配（LLM）：`_TP4AnalysisResult`（:882-898，Pydantic 含 confidence 校验器）+ `_TP4Analyzer`（:900-924，继承 LLMAnalyzerBase，response_schema 指向结果模型，build_prompt 直接用自制 prompt 不套通用文件包装）；`_check_tp4`（:1154-1650）预算极密：最多 128 文件/4MB 代码/64 批/每批 32K token（:74-83），markdown 围栏感知的代码切块 `_iter_tp4_markdown_fences`（:969）+ 行对齐分块 `_tp4_line_chunks`（:1050）。`node`（:1651-1874）的 `_consume_static`（:1691-1724）是"构造期预算"模式：在产出前查余量，超限即停并保留已产出前缀。

## 三、外部连接

manifest/component_metadata/llm_file_cache 均来自 build_context；TP4 依赖 llm_analyzer_base 的结构化输出绑定与批处理运行时、`get_max_input_tokens`/`estimate_tokens`（:1188、1205）；constants.py 的 `_MODEL_SLOTS`（:65-74）为三个分析器各留模型槽位（mcp_least_privilege/mcp_rug_pull/mcp_tool_poisoning）；`_FRAMEWORK_TAGS = ["ASI02", "AML.T0080"]`（tool_poisoning :72）对接 MITRE ATLAS 风格标签体系。MCP Registry 态势检查是另一条独立路径（`mcp_registry.scan_registry`，mcp_registry.py:466-485），由 CLI `--mcp-registry` 触发，不经过这三个分析器。

## 四、数据流

least_privilege：manifest.permissions/allowed-tools → 类别集合；可执行文件内容 → 能力正则扫描 → 集合差 → LP1/LP4、存在性判定 → LP2/LP3。rug_pull：file_cache 全文本 → RP1 三类命令正则；manifest 字符串化 → RP2；manifest.version → RP3；（previous_manifest 存在时）diff → 增量规则。tool_poisoning：manifest 元数据 → TP1/TP2/P9/TP3 正则族；manifest.description + 可执行/markdown 代码分块 → TP4 LLM 批判定 → mismatch 即 TP4 finding（`_tp4_finding` :1117）。三者产出统一 Finding + 逐路径账本事件 + analyzer_status。

## 五、设计决策

1. **not_applicable ≠ failed**：无 manifest/无执行面是正常形态，账本里显式记 not_applicable，完备性核算不把它当覆盖率损失。
2. **置信度分层表达不确定性**：LP1 测试文件 0.55/生产 0.75；RP3 >= 与 ^ 分别 0.40/0.50——下游 meta_analyzer 可按阈值裁决，而非硬性二值。
3. **防御性正则注释文化**：TP3 loopback 边界注释把历史漏洞写成正则旁注，改这些正则前必读。
4. **TP4 与静态规则共存**：LLM 只管"描述说的和代码做的不一致"这一语义判定，字面信号全部前置到确定性规则——LLM 失败时 TP1-TP3 仍完整。

## 六、新人提示（坑与勘误）

- **previous_manifest 在主流程恒为 None**：build_context.py:3420 硬编码 `"previous_manifest": None`，且无 reducer 的键会被节点返回值整体覆盖——即使调用方在初始 state 预置也会被刷掉，`_check_manifest_changes`（rug_pull :492）在默认扫描图里实际不可达，只有测试直接构造 state 才走到（tests/nodes/analyzers/test_mcp_rug_pull.py:70 起）。"上线后偷改定义"的完整 diff 检测当前是**预留能力**而非在跑能力。
- mcp_least_privilege 与 mcp_rug_pull 是纯静态分析器，却在 `_MODEL_SLOTS` 占模型槽位（constants.py:65-74）——预留位，别误以为它们调 LLM。
- LP 系规则文档写"LP1 through LP4"（least_privilege :16 docstring），但 LP4 在 node 主流程后段（:672），读代码容易漏。
- TP4 用 `llm_file_cache`（脱敏投影，tool_poisoning :1209-1212）而 RP1 用 `local_file_cache or file_cache`（rug_pull :654）——同一分析器族内两种缓存视图并存，混淆会导致测试断言对不上。
- 改 TP2 同形字表要同步 scripts/generate_unicode_confusables.py 的生成逻辑（仓内 scripts/ 目录），手改 _CONFUSABLES 会被再生成覆盖。
