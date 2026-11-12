# healing/service.py — 自愈服务：从"人做一遍"录制出可复用工作流

> 源文件：`workflows/workflow_use/healing/service.py`（898 行）

## 一、角色定位

`HealingService`（L41）是 workflow-use 的**生成端引擎**：给定一句自然语言任务，它先派 browser-use `Agent` 真枪实弹把任务做一遍（录制），再把 agent 的执行历史转换成 `WorkflowDefinitionSchema`（结构化、可复用、变量化的 YAML）。"自愈"的含义体现在生成链的层层修正：录制时捕获元素文本 → 转换（LLM 或确定性两条路线）→ 可选 AI 校正 → 模式变量识别与 YAML 瘦身。`generate_workflow_from_prompt`（L432）是全链总入口，CLI 与扩展（经 builder 层）都从这里拿工作流。

## 二、内部结构

- **构造开关群**（L42-58）：九个功能开关，关键默认值——`use_deterministic_conversion=False`（L46，**默认走 LLM 转换路线**，确定性转换器按需才创建，L78）、`enable_ai_validation=False`（L47）、`enable_pattern_variable_identification=True`（L49，注释标榜"no LLM, $0 cost!"）、`cleanup_yaml=True` 及三个 remove_* 字段开关（L52-55）、`enable_xpath_optimization=True`（L57）。
- **历史结构化** `_history_to_workflow_definition`（L183）：把 `AgentHistoryList` 逐条转成带截图的多模态 `UserMessage`。
- **两条转换路线**：`create_workflow_definition`（L288，LLM 路线）与 `_create_workflow_deterministically`（L343，确定性路线）。
- **后处理** `_post_process_workflow`（L92）：模式变量识别 + 删冗余字段。
- **质量看门** `_validate_workflow_quality`（L254）：警告 agent 步骤（"10-30x slower and cost money"，L263）并给语义化替代建议。
- **`_populate_selector_fields`（L276）已被架空**：docstring 明写 DISABLED，现返回原样（L281-286），保留只为兼容。

## 三、外部连接

browser-use 侧：`Agent`/`Browser`/`AgentHistoryList`（L8）、`DOMInteractedElement`（L9）、LLM 消息类型（L10-11）、`Controller`（L475 函数内导入并被子类化）。仓内：`BuilderService._get_available_actions_markdown` 为 prompt 提供动作清单（L13/L296）、healing 五兄弟（converter L14 / selector_generator L15 / validator L16 / variable_extractor L17 / views L18）。Prompt 文件按绝对路径加载 `_PROMPTS_DIR / 'workflow_creation_prompt.md'`（L38/L292）。注意 `_post_process_workflow` 用 `importlib.util.spec_from_file_location` **从文件路径直接加载** `workflow/variable_identifier.py`（L112-118）——绕过包导入的非常规手法，文件挪位只会打警告不会失败（L138）。

## 四、数据流

`generate_workflow_from_prompt(prompt, agent_llm, extraction_llm, ...)` 五阶段：

1. **录制**（L463-839）：内联定义 `CapturingController(Controller)`（L477），在每次 `act` 前抓 `browser_session.get_selector_map()`（L492）建 index→元素数据映射。文本提取是核心工程（L520-676）：多字段名兼容（text/inner_text/node_value/textContent/innerText，L534）；过滤 `javascript:` 伪 href（L540-541）；a/button 的"贫文本"判定（空、≤2 字符、'link/click/here'、8 位随机 ID，L552-557）后按 aria-label→title→alt→placeholder→value 取语义属性（L561-568）；甚至从 id/class 推断 Search/Submit、从 href 尾段提词（L573-625，硬编码排除清单 `'www.edison.com'` 等 L612-616 是特定客户现场的化石）。每元素经 `selector_generator.generate_strategies_dict` 生成多策略（L664），映射存 `self.captured_element_text_map`（L830）。
2. **增强 prompt**（L796-811）：强制 agent 在推理里输出 `[ELEMENT: "exact visible text"]` 结构化标签——为转换阶段准备锚文本；Agent 配置 `use_vision=True`、`max_failures=10`（L816-827）。
3. **转换**（L851-860）：`use_deterministic_conversion` 为 True 走确定性路线（L853-856），否则走 LLM 路线（L858）——**默认后者**。LLM 路线（L288）= prompt 模板 + 全部历史消息 → `ainvoke(output_format=WorkflowDefinitionSchema)`（L305）一步结构化产出；确定性路线（L343）用 `DeterministicWorkflowConverter.convert_history_to_steps` 零 LLM 转步骤，再从 captured_map 或 history 按 highlight_index 回填元素哈希（L365-402）。两条路线都过 `_validate_workflow_quality`，且可选跑 `variable_extractor.suggest_variables` 二次变量建议（只打日志不自动应用，L335）。
4. **AI 校正**（L862-889，默认关）：`WorkflowValidator(extraction_llm)`（L867）审校，`corrected_workflow` 非空则整体替换（L879-881）。
5. **后处理**（L894）：`identify_variables_in_workflow(use_llm=False)` 模式识别变量（L121-123，置信度阈值 0.5，L50）；随后删 description/verification_checks/expected_outcome 三类字段（L152-161）——生成的 YAML 只保留可执行骨架。

## 五、设计决策与取舍

- **默认 LLM 转换而非确定性转换**：确定性路线快且保证零 agent 步骤，但 LLM 路线能理解意图、命名步骤、识别变量——默认选质量弃速度。确定性路线是留给成本敏感/离线场景的开关。
- **录制期文本抢救的深度**：CapturingController 里近 160 行文本启发式（L520-676）说明"拿到可见文本"是整条链最难的一环——agent 的 `[ELEMENT: ...]` 标签（L796）与 selector_map 捕获是双保险。
- **correction 替换而非合并**：AI 校正直接整体替换 workflow（L881），不做 diff 合并——简单但会丢弃原生成的任何校正器看不到的优点。
- **YAML 瘦身默认开**：description 等字段录制期有价值（人读）、执行期是噪音（LLM token），生成后删除是正确时点；代价是 `Workflow` 运行时日志里的步骤描述退化为"No description provided"。
- **进度回调防御**：`_emit_status_update` 吞掉回调异常（L26-34），UI 回调抛错不能中断生成——CLI 与扩展共用此服务的边界设计。
- **`_populate_selector_fields` 的战略性放弃**（L276-286）：从"填充 xpath/cssSelector"退到"纯语义匹配"，与 semantic_executor 的文本优先哲学一致——选择器从生成产物中全面撤退。

## 六、新人提示（坑/勘误）

1. **甄别素材钉版**：`use_deterministic_conversion=False`（L46）默认 LLM 路线属实；deterministic_converter 的推理文本优先级 memory > thought > evaluation_previous_goal 在 `deterministic_converter.py` L48-54 属实。
2. `_history_to_workflow_definition` 的元素哈希是 `sha256(f'{tag_name}_{element.element_hash}')[:10]`（L201）——与 `_create_workflow_deterministically` 里 converter 的 element_hash_map 键（index）是**两套键空间**，L374-375 做的是 index→hash 的桥接。
3. CapturingController 的 DEBUG 块（L500-518）对前 3 个元素全字段打印，生产环境会刷屏；`is_poor_text` 的 8 位字母数字判定（L556）会把恰好 8 字符的正常英文单词（如 "Settings"）误判为随机 ID——有语义属性时不致命，但注意。
4. 硬编码域名排除清单（L612-616 `www.edison.com/edison.com/investors`）是特定录制现场的残留，泛化场景无害但暴露了启发式的来源。
5. `create_workflow_definition` 失败时会再裸调一次 `llm.ainvoke` 打印原始响应（L311-314）——排障钩子，勿在异常路径上期待它有结构化语义。
6. 双 LLM 显式分层（L435-436）：`agent_llm` 决策、`extraction_llm` 提取兼校验（L864-867 注释明说校验用 extraction_llm "more reliable than the main agent LLM"）。
