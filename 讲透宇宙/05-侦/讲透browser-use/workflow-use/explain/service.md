# workflow/service.py — Workflow 执行编排核心

> 源文件：`workflows/workflow_use/workflow/service.py`（1131 行）

## 一、角色定位

`Workflow` 类（L39）是整个 workflow-use 的**运行时心脏**：输入一份 `WorkflowDefinitionSchema`（YAML 加载或录制产物），按顺序执行其中的 steps，管理步骤间变量传递（context），最终产出 `WorkflowRunOutput`。它同时是三种执行形态的分派中枢——确定性步骤走 `WorkflowController`、语义步骤走 `SemanticWorkflowExecutor`、agent 步骤走 browser-use 的 `Agent`——并提供两个特殊入口：`run_as_tool`（把工作流包装成 LLM 可调用的工具，L1013）和 `run_with_no_ai`（纯语义执行、零 LLM 成本，L1047）。

在图谱中的位置：上游消费 `builder`/`healing` 产出的 schema，下游驱动 `browser_use` 的 Browser/Agent/Controller 三件套，是 schema 层与 browser-use 框架层之间的粘合剂。

## 二、内部结构

- **构造与加载**：`__init__`（L42-105）组装六大依赖——schema、controller（默认 `WorkflowController()`，L74）、browser（默认 `Browser(use_cloud=use_cloud)`，L76）、llm、page_extraction_llm、element_finder（`ElementFinder()` 多策略定位器，L100）。`load_from_file`（L108-136）用 `yaml.safe_load` 解析后经 Pydantic 校验。
- **三种步骤执行器**：`_run_deterministic_step`（L139）执行控制器动作；`_run_agent_step`（L329）起完整 Agent；`_run_extraction_step`（L354）是轻量提取——不起 agent，直接拿页面 markdown 喂一次 LLM。
- **上下文机制**：`_resolve_placeholders`（L508）递归地把 `{var}` 占位符用 `self.context` 格式化；`_store_output`（L586）把步骤产出按 `output` 字段写回 context。
- **主循环**：`run`（L851）与 `run_with_no_ai`（L1047）各有一个几乎相同的步进循环（等待→取消检查→截图→解析占位符→执行→存输出）。
- **输入模型工厂**：`_build_input_model`（L951）把 YAML 里的 `input_schema` 动态编译成 Pydantic 模型，供校验与 LLM 工具化复用。

## 三、外部连接

- **browser_use 框架**：`Agent`/`Browser`/`ActionResult`/`AgentHistoryList`（L11-12）、`BaseChatModel` 与 `SystemMessage`/`UserMessage`（L13-14）、`NoParamsAction`（L15）。
- **仓内模块**：`WorkflowController`（L18）、`get_best_element_handle`（L19）、schema 层五种步骤视图（L20-26）、`ElementFinder`（L27）、两个 prompt 常量 `AGENT_STEP_SYSTEM_PROMPT`/`STRUCTURED_OUTPUT_PROMPT`（L28）、`WorkflowStepAgentController`（L29）、`WorkflowRunOutput`（L30）。
- **延迟导入**：`SemanticWorkflowExecutor` 在 `_execute_step` 内按需 import（L655）并在实例上惰性缓存 `_semantic_executor`（L657-660）；`run_with_no_ai` 也在函数体内导入（L1068）。
- **消费方**：`cli.py` 与 MCP 层通过 `run`/`run_step`/`run_as_tool` 调用。

## 四、数据流

单次 `run(inputs)` 的完整链路：

1. `_validate_inputs`（L873 调用于 L495 定义）用动态 Pydantic 模型校验输入；
2. `context = runtime_inputs.copy()`（L875）——注意是**全新 context**，重复 run 互不污染；
3. `browser.start()`（L889）后进入步进循环：步间等待取**前一步**的 `wait_time`（`is not None` 判断允许显式 0 跳过，L896-899）；
4. `_resolve_placeholders` 对 step 做字符串格式化——`data.format(**self.context)`（L517），KeyError 时原样返回（L520-523）；
5. `_execute_step`（L630）分派：`extract`/`extract_page_content` 走轻量提取（L641-644）；`click/input/key_press/select_change` **无 cssSelector 但有 target_text** 时转入 `SemanticWorkflowExecutor`（L647-661）；其余走确定性控制器；
6. `_store_output`（L586）提取产出——`ActionResult` 优先 `extracted_content`（尝试 json.loads，L607），`AgentHistoryList` 则倒序扫最后一条 history 里最近一个非空 `extracted_content`（L613-617）；
7. 全部结束后若给了 `output_model`，`_convert_results_to_output_model`（L723）汇总所有 extracted_content（连 agent history 里的也收，注释自嘲"this might be incorrect; but it helps A LOT"，L749），用 `STRUCTURED_OUTPUT_PROMPT` 强制结构化输出（L763-768）。

确定性步骤内部的细则：`model_dump(exclude_none=True)` 后过滤 14 个工作流元数据字段（L147-162），但 `type` **不**过滤（L146 注释明说 navigation 需要它）；`go_back`/`go_forward` 换成 `NoParamsAction()`（L231-233）；执行后 `networkidle` 等待（timeout 10s，L254），且若**下一步**带 cssSelector 会提前用 `get_best_element_handle` 等元素出现（超时常量 `WAIT_FOR_ELEMENT_TIMEOUT = 2500`，L34，实现在 L264-281）。

## 五、设计决策与取舍

- **fallback 到 agent 实际上已禁用**：`fallback_to_agent=True` 仍是构造默认值（L50），但真正的 `_fallback_to_agent` 整个被注释掉（L421-493），`_execute_step` 失败路径只 raise（L675），L691-696 的 fallback 调用也是注释。参数保留是兼容性考虑，行为上是"fail fast"。
- **不可达代码**：`_execute_step` 的 agent 分支里 L709 raise 之后的 L711-718 永远执行不到——阅读时别被那段 fallback 日志误导。
- **语义路径的 XPath 降级**：多策略查找若命中 xpath 策略，service 层只打警告并回落全量控制器（L191-194），因为 xpath 返回字符串而非索引，语义执行归 `semantic_executor` 管——这是两个模块的职责边界。
- **target_text 验证是硬失败**：给了 target_text 但全部策略未命中时直接 raise RuntimeError（L217-221），不静默降级，避免点错元素。
- **keep_alive 黑客手段**：构造时 `keep_alive = True`（L78-79）防止 agent 接管后浏览器被关；`run` 结束时在 finally 里复位为 False 再 stop（L941-943）——异常路径也能收尾。
- **双 LLM 分层**：`page_extraction_llm` 专供页面提取/语义执行（便宜模型），`llm` 供 agent 与最终结构化转换（贵模型），L376 的 `self.page_extraction_llm or self.llm` 是典型降级。
- **轻量提取的代价控制**：页面文本截断到 10000 字符（L380），单条 UserMessage 直调（L401-402），比起一个 Agent 便宜一个数量级。

## 六、新人提示（坑/勘误）

1. **行号勘误**：`_run_extraction_step` 里 `page._extract_clean_markdown()` 是带下划线的私有 API（L372），browser-use 升级随时可能改签名。
2. `run_step` 末尾硬编码 `asyncio.sleep(5)`（L803）保浏览器存活 5 秒，单步调试时会觉得"卡住"，不是 bug。
3. `_resolve_placeholders` 只在字符串同时含 `{` 和 `}` 时才 format（L516）；InputStep 有兜底——value 为空或占位符未解析成功时改用 `default_value`（L557-576）。
4. 多策略查找的结果存在实例属性 `self._current_strategy_attempts`（L182）供错误上报用，单实例并发跑多个 step 会互相覆盖。
5. `_build_input_model` 的类型映射只支持 string/number/bool 三类（L965-969），YAML 里写 `integer` 会直接 ValueError（L980）。
6. debug 模式截图按 before/after/error 三前缀落盘（L913/923/926），文件名带时间戳与清洗后的描述（L828-839），默认目录 `./logs/workflow_debug`（L88）。
