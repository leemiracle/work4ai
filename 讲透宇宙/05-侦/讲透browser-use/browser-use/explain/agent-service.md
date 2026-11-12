# browser_use/agent/service.py 精讲——Agent 主循环，12 万星框架的心脏

## 一、角色定位

`browser_use/agent/service.py` 是整个框架的中枢：4188 行、单文件承载 `Agent` 类（L135，`Generic[Context, AgentStructuredOutput]`），把 LLM 推理、浏览器感知、动作执行、历史管理、遥测、事件总线粘合成"感知→决策→执行"循环。用户一行 `Agent(task, llm).run()` 之后的所有行为——何时截屏、怎么喂 DOM、动作失败怎么办、何时判定结束——全由此文件决定。分工上：`prompts.py` 提供系统提示词、`message_manager/` 维护消息历史、`tools/service.py`（Tools，旧名 Controller）执行动作、`browser/session.py` 提供感知原语。Agent 只做编排。

## 二、内部结构

**巨型构造器（L137-215）**：70 多个参数分六组——LLM 组（`llm`/`page_extraction_llm`/`fallback_llm`/`judge_llm`）、浏览器组、工具组（`tools`/`controller` 别名 L146）、技能组（`skill_ids`/`skills` 别名 L148-149，同传 raise，L337-338）、回调组、行为开关组。**别名即 API 演化史**：`browser`/`controller`/`skills` 都是后起新名。

构造器大量"隐式智能默认"：
- **LLM 兜底链**（L226-236）：`llm=None` 先查 `CONFIG.DEFAULT_LLM` 再兜底 `ChatBrowserUse()`；provider 是 browser-use 自动开 flash_mode（L239-240），而 flash_mode 用砍掉 plan 字段的 schema 结构性禁用规划（L242-244）。
- **按模型名猜超时**（L262-278）：gemini-3-pro 90s、groq 30s、claude/deepseek/o3 90s、默认 75s。
- **Claude Sonnet 截图自动缩放**（L248-252）：模型名 rsplit 掉网关前缀后以 `claude-sonnet` 开头即配 `(1400, 850)`。
- **坐标点击能力探测**（L327-334）：模型名含 `claude-sonnet-4`/`gemini-3-pro` 等才开启。
- **截图动作排除**（L320-325）：`use_vision != 'auto'` 时剔除 `screenshot` 动作。

**step() 五阶段管线（L1036-1086）**——全文件核心骨架：

1. **CAPTCHA 等待**（L1047-1060）：`wait_if_captcha_solving()` 阻塞到解决，等待时间不计入步时长（L1050 重置计时），结果注入 `ActionResult(long_term_memory=...)` 让模型看见。
2. **_prepare_context**（L1065→L1088-1161）：取浏览器状态（L1097-1099 恒 `include_screenshot=True`——**即使 use_vision=False 也截图**，注释明说为云端同步）；页面专属动作更新（L1114）；MessageManager 两段式装填（L1130 `prepare_step_state` + L1140 `create_state_messages`）；注入预算警告、重规划/探索/死循环检测 nudge（L1154-1158）。
3. **_get_next_action**（L1075→L1176）：`asyncio.wait_for(..., timeout=llm_timeout)`（L1185-1186），超时附"Keep your thinking and output short"。
4. **_execute_actions**（L1076→L1212）：交给 `multi_act`。
5. **_post_process + _finalize**（L1079/L1086）：下载检查、计划更新、失败计数、历史落盘、`n_steps += 1`（L1416）。

L1071-1072 在 LLM 调用前清空 `last_model_output`/`last_result`，防超时残留旧数据——踩坑后补的防御。

**错误处理单点化（L1259-1315）**：try/except 把所有异常引到 `_handle_step_error`：InterruptedError 是正常打断；连接类错误先等重连（L1273-1278），成功则本步作废重试；真浏览器关闭才置 `stopped`。其余计入 `consecutive_failures`，达到上限才升 ERROR。熔断在 run 主循环：失败数 ≥ `max_failures + int(final_response_after_failure)` 即 break（L2630-2635）。

**multi_act 双层页面守卫（L2755-2873）**：第一层静态标志——动作标了 `terminates_sequence=True`（navigate/search/go_back）自动作废后续（L2840-2845）；第二层运行时——每动作后比对 URL 与焦点目标，变了就跳过剩余（L2848-2853）。`done` 只允许单动作（L2786-2790）。

**get_model_output 与降级链（L1943-2023）**：发送前长 URL 缩短替换省 token（L1946），`ainvoke(messages, output_format=self.AgentOutput)` 走结构化输出（L1950-1953），返回后还原 URL、截断到 `max_actions_per_step`。捕获 `ModelRateLimitError/ModelProviderError` 后尝试 `_try_switch_to_fallback_llm`（L1981-2023）：可重试码 `{401,402,429,500,502,503,504}`（L2001），切换一次性（L1989），切完递归重调。

**空输出救援（L1668-1702）**：空 action 时追加"你忘了返回动作"重试一次；再空就手工注入 `done(success=False)` 安全 noop（L1691-1700）——状态机永远能前进。

## 三、外部连接

- **调用** `browser/session.py`：`get_browser_state_summary`（L1097）、`wait_if_captcha_solving`（L1047）、`is_reconnecting`（L1272-1273）。
- **调用** `tools/service.py`：`Tools.act(...)`（L2807-2815，传 browser_session/file_system/page_extraction_llm/sensitive_data/available_file_paths/extraction_schema 七类上下文）
- **被调**：`run()`（L2521）/`run_sync()`（L4086）是 SDK 入口；`take_step`（L2272）供外层编排器逐步驱动；`rerun_history`（L3128）支撑回放。
- **事件总线**：bubus EventBus，run 开始派发 `CreateAgentSessionEvent`/`CreateAgentTaskEvent`（L2572/L2578），每步 `CreateAgentStepEvent`（L1406-1413），结束 `UpdateAgentTaskEvent`（L2726）——云端面板靠这条流渲染
- **LLM 层**：只依赖 `llm/base.py` 的 `BaseChatModel` Protocol（L27），不 import 任何具体 provider——依赖倒置样本。

## 四、数据流

一步内：`BrowserSession.get_browser_state_summary()` → `BrowserStateSummary`（url/tabs/DOM/截图）→ MessageManager 装成 `input_messages` → `llm.ainvoke(output_format=AgentOutput)` → `AgentOutput`（current_state 评估 + action 列表）→ `multi_act` 逐个执行 → `list[ActionResult]` → `_finalize` 打包 `AgentHistory`（截图路径、interacted_element、计时 metadata）追加进 `AgentHistoryList`。run 结束时 `token_cost_service.get_usage_summary()` 汇总成本（L2674）。

输入侧另有 `_extract_start_url`（L2307-2454）从任务文本抽 URL 实现自动导航——排除邮箱、60 多种文件扩展名（L2323-2392）、占位符 URL、"Never go to this URL"式否定语境（L2431-2436）、多 URL 歧义放弃（L2444-2448）。

## 五、设计决策与取舍

1. **别名优先+冲突即报错**：三组新旧参数并存，同传抛 ValueError 而非静默选一（L292-293、L337-338）——宁可炸醒用户。
2. **错误处理收口一处**：五个阶段不各自 try/except，统一漏斗到 `_handle_step_error`，失败语义全局一致。
3. **flash_mode 用 schema 而非提示词禁规划**（L242-244）：砍输出字段让"不规划"结构性成立，比 prompt 里说"别规划"可靠。
4. **extraction_schema 刻意不继承 output_model_schema**（L367-372 长注释）：最终结果 schema 与单页抽取 schema 形状不同，继承会打崩网关的动作协议——真实踩坑产物。
5. **降级链一次性单程**：切换后不回切（L1989），防限流模型间乒乓。
6. **run 与 take_step 双入口**：run 自带循环；take_step 返回 `(is_done, is_valid)` 把循环控制权让渡给外部——同一内核服务两种集成深度。

## 六、新人提示（坑/勘误）

- **别按行数找重点**：近半是 rerun/日志美化外围（L3128-4185），主循环看 L1036-1416 + L2519-2751 即够。
- **sensitive_data 是消息层脱敏**：L1135/L1147 传 MessageManager 处理，执行时 Tools 再替换真值——两端都要过，单看一端会以为明文泄漏。
- **`use_vision=False` 也在截屏**（L1098 注释）：为云端同步，不是 bug。
- **步数上限语义**：循环条件 `n_steps <= max_steps`（L2620），`_finalize` 完成后才 +1（L1416），max_steps=1 恰执行一步；超限走 else 补失败历史（L2654-2670）。
- **方法名勘误**：`_process_messsages_and_replace_long_urls_shorter_ones`（L1838）三个 s 是源码真实拼写。
