# browser_use/agent/prompts.py 精讲——系统提示词装配与七路模板选择

## 一、角色定位

`browser_use/agent/prompts.py`（601 行）是 Agent 的"嘴"：`SystemPrompt` 决定模型以什么身份与规则行事，`AgentMessagePrompt` 决定模型每步看到的世界快照。行为模板本体存在 `agent/system_prompts/` 的 markdown 里，本文件只做**选模板、填参数、拼上下文**三件事。但装配顺序与块结构直接决定 provider 端 prompt caching 命中率与成本——"看起来只是拼字符串、实则处处是工程"。

## 二、内部结构

**SystemPrompt（L28-101）**。五个互相关联开关：`use_thinking`/`flash_mode`/`is_anthropic`/`is_browser_use_model`/`model_name`。装配逻辑：

1. `override_system_message` 非空则整体替换（L49-50）；
2. 否则 `_load_prompt_template()`（L60-92）七路优先级选模板（与 `system_prompts/` 文件一一对应）：`is_browser_use_model`（官方微调模型）三分支——flash→`system_prompt_browser_use_flash.md`、thinking→`system_prompt_browser_use.md`、否则 no_thinking 版（L65-71）；`is_anthropic_4_5 and flash`→`system_prompt_anthropic_flash.md`（L73-74）；`flash and is_anthropic`→`system_prompt_flash_anthropic.md`（L75-76，与上一条文件名镜像，是两个不同文件）；`flash`→`system_prompt_flash.md`（L77-78）；`use_thinking`→`system_prompt.md`（L79-80）；兜底 no_thinking 版（L81-82）。
3. 模板用 `importlib.resources.files(...)` 读（L85-90，注释明说兼顾开发态与打包安装态）。
4. `.format(max_actions=...)` 填唯一占位符（L53）——`max_actions_per_step` 直接进 prompt。
5. `extend_system_message` 追加尾部（L55-56）；最终 `SystemMessage(content=prompt, cache=True)`（L58）——**cache=True 是给 provider 缓存的前缀标记**。

辅助函数 `_is_anthropic_4_5_model`（L17-25）按模型名子串判 Opus/Haiku 4.5，注释给动机：**Anthropic 4.5 系要求 prompt ≥4096 token 才命中缓存**，故有单独加长模板。加载失败统一 RuntimeError 带原因（L91-92）。

**AgentMessagePrompt（L104-506）**——每步的用户消息工厂，20 个上下文参数（L107-128），`get_user_message()`（L404-506）产出 UserMessage。文本块组装顺序（L411-435）刻意排布：

```
<user_request> → <agent_history> → <agent_state> → <browser_state>
→ [<read_state>] → [<page_specific_actions>] → [不可用技能提示] → <step_info>
```

关键注释在 L433-434 与 L365-367：**step_info（步数、当天日期）这类每步必变的元数据钉在消息尾部**，之前内容理论上都是可缓存前缀——变化点后置就是为 prompt cache 让路。

子块生成器：
- `_extract_page_statistics`（L150-221）：递归遍历简化 DOM 数出 links/iframes/shadow open-closed/scroll containers/interactive/total/text_chars 九项统计；shadow host 判 closed/open 细分（L196-206）。
- `_get_browser_state_description`（L224-335）：拼 `<page_stats>` 块。两处智能化：元素总数 <10 提示"页面可能空，考虑等待"（L230-231）；骨架屏判定要"网络请求在飞 + 元素>20 + 文本密度<每元素5字符"三条件同成立（L232-242，注释点明低文本密度只有在请求进行中才意味着加载中）。元素文本超 `max_clickable_elements_length`（默认 40000）截断并标注（L254-256）。`<page_info>` 把滚动位置换算成"上/下方还有几页"（L267-275）。当前标签用 URL+标题双匹配，唯一匹配才标 Current，多个同名宁可不标（L287-294）。PDF 查看器直接指示"别用 extract，去 read_file 已下载的 PDF"（L306-313）。
- `_get_agent_state_description`（L337-359）：文件系统清单、todo.md（空则提示填）、计划、`<sensitive_data>` 占位符说明、文件路径白名单。
- `_resize_screenshot`（L375-401）：`llm_screenshot_size` 配置时 PIL LANCZOS 缩放重编码，异常回退原图（L399-400）。

**多模态分支（L444-506）**：有截图或 read_state 图片时 UserMessage 变 content_parts——文本描述在前，sample_images 次之，截图逐张带标签（最后一张 `Current screenshot:`，其余 `Previous screenshot:`，L452-457），read_file 图片按扩展名猜 media_type 追加（L477-502）。新标签页强制关 vision（L407-408，只有占位截图）；`PLACEHOLDER_4PX_SCREENSHOT` 的 4 像素占位图被过滤（L442）。

文件尾部三个自由函数服务 rerun：`get_rerun_summary_prompt`（L509）回放总结提示；`get_ai_step_system_prompt`（L556）+ `get_ai_step_user_prompt`（L588）是 rerun AI 步骤的抽取模板。

## 三、外部连接

- **被 Agent 构造**：agent/service.py L509 实例化 SystemPrompt，灌入八个参数；`is_anthropic` 取自 LLM provider 名，`is_browser_use_model` 取自 provider == 'browser-use'。
- **被 MessageManager 调**：`AgentMessagePrompt` 由 message_manager 在 `create_state_messages` 时构造；`agent_history_description`/`read_state_description` 等都是 MessageManager 预处理好的字符串。
- **上游数据**：`dom_state.llm_representation()`（L252）来自 dom/service.py 的序列化链；`page_info`/`pending_network_requests`/`closed_popup_messages`/`is_pdf_viewer` 来自 BrowserSession 状态采集。
- **模板目录**：`agent/system_prompts/` 九个 md（8 候选 + `__init__.py`）。

## 四、数据流

一步内：SystemPrompt 产出的系统消息放消息流头部（全程不变、可缓存）；上一轮模型输出摘要+动作结果进 history；本轮 `BrowserStateSummary` 构造 `AgentMessagePrompt` 调 `get_user_message(use_vision)`。文本块按 XML 标签顺序拼接、整体过 `sanitize_surrogates`（L438，防 UTF-8 代理对编码崩）。视觉开启时附加截图链。最终 `UserMessage(cache=True)` 发出——两个 cache 标记夹住"稳定系统前缀 + 每步状态消息"的两级缓存结构。

## 五、设计决策与取舍

1. **模板外置 markdown 而非硬编码**：prompt 是核心资产，外置便于 diff、评审、A/B；Python 侧只留选择逻辑。七路分支看似多实则正交：模型家族（browser-use 微调 / Anthropic 4.5 / Anthropic / 通用）× 模式（flash / thinking）。
2. **缓存友好的块排序**：变化最频繁的 step_info 钉尾——这是与 provider prompt caching 的契约。改块顺序前先想会不会把缓存打散。
3. **override 与 extend 两档定制**：override 完全接管（失去默认约束，慎用），extend 只追加。绝大多数场景该用 extend。
4. **统计先行**：`<page_stats>` 放元素列表前，模型先拿全景再读细节；启发式（空页/骨架屏）提前给行为建议，减少烂页面上的无效动作。
5. **placeholder 过滤**：4px 占位截图、新标签页假图都拦在消息外，防模型对占位图做视觉推理。

## 六、新人提示（坑/勘误）

- **两个 anthropic flash 模板别搞混**：`system_prompt_anthropic_flash.md`（4.5 分支，L74）与 `system_prompt_flash_anthropic.md`（普通分支，L76）名字镜像、内容不同，改错文件会"改了没生效"。
- **`override_system_message` 是全量替换**：跳过模板加载（L49-52），输出格式与动作约束全部丢失——要定制优先 extend。
- **`max_actions_per_step` 两处约束**：prompt 告知模型（L53）+ 代码硬截断（agent/service.py L1961-1962），只改一边会不一致。
- **当前标签可能不标注**：多标签 URL+标题全同时 current_target_id 为 None（L294）——保守选择防误导，不是 bug。
- **日期直接进 prompt**：`datetime.now()`（L372）每步变化——这也是它被钉在 step_info 尾部的原因之一。
- **`format(` 只有模板一处**：L53 是唯一占位符注入点，加变量要同时改模板与这里，漏一边 KeyError。
