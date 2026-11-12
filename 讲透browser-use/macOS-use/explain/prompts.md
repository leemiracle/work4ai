# agent/prompts.py —— 提示词工厂：模型行为的"宪法"与"日报格式"

## 一、角色定位

`mlx_use/agent/prompts.py`（175 行）定义 Agent 与 LLM 之间的全部语言契约：`SystemPrompt` 生成系统消息（角色定位、输出 JSON 格式、七组规则、动态注入的动作函数清单），`AgentMessagePrompt` 生成每步的用户消息（步数、当前 App 状态、上轮动作结果）。它不调 LLM、不碰 AX API，却是整个系统能否运转的隐形骨架——agent/service.py 解析回的 `AgentOutput{current_state, action[]}` 结构、Controller 期待的 index/action 参数、element.py 序列化的 `[index][:]<AXButton> [interactive]` 格式，全部在这里预先"立法"。

选它而非 views.py 做精讲，是因为它是理解前五篇所涉行为的钥匙：为什么模型会自评上一目标（React 式反思）、为什么动作能批处理、遇到 -25212 模型为什么会自救——答案都写在这 175 行里。

## 二、内部结构

**`SystemPrompt`（prompts.py:6-131）** 三个构件：

- `important_rules()`（prompts.py:20-94）：七组规则。①RESPONSE FORMAT（prompts.py:22-39）——严格两键 JSON：`current_state{evaluation_previous_goal, memory, next_goal}` + `action[]`，评估字段的规定取值是 `Success|Failed|Unknown` 前缀（agent/service.py:330-343 的表情日志就靠子串匹配这三个词）。②ACTIONS 批处理策略（prompts.py:41-44）——"稳定 UI（如计算器）可一口气批量 max_actions_per_step 个动作；动态 UI（如邮件）一次一步"，这是与 Controller 熔断机制（controller/service.py:285 error 即断）配套的双保险。③APP HANDLING（prompts.py:47-55）——App 名大小写敏感、常见别名映射（Calendar/iCal、Messages/com.apple.MobileSMS）。④ELEMENT INTERACTION（prompts.py:57-62）——教模型读 `[index][:]<type>` 标记、"用元素 actions 列表属性选择点击动作"（这条与 actions.py 白名单闭环）。⑤TASK COMPLETION（prompts.py:64-75）——必须用上下文元素验证结果再 done、卡三次就带错误详情收尾。⑥NAVIGATION & ERROR HANDLING（prompts.py:77-83）——含 -25212/Window not found 的恢复策略（open_app 重开，见坑 3）。⑦APPLESCRIPT SUPPORT（prompts.py:85-91）——逃生通道示例（建备忘/说话/改文件名）。规则末尾动态拼接 `max_actions_per_step`（prompts.py:93）。
- `input_format()`（prompts.py:96-107）：宣告输入三段式（当前 App、元素清单、上轮动作结果），明确"UI 树带详细 AX 属性，请利用它们选对元素"。
- `get_system_message()`（prompts.py:109-131）：f-string 组装角色句（"You are a macOS automation agent..."，prompts.py:114）+ 时间戳 + 上述两块 + `Functions: {self.default_action_description}`——动作清单由 Registry.get_prompt_description() 运行期注入（agent/service.py:123 传入），**提示词与注册表永远同步**是这套动态动作体系的核心卖点。

**`AgentMessagePrompt`（prompts.py:133-175）**：构造器存 state/result/include_attributes/max_error_length/step_info（prompts.py:134-156），`get_user_message()`（prompts.py:158-175）拼 HumanMessage：步数行 `Step {n+1}/{max}`（prompts.py:160，+1 是因为 agent 的 n_steps 在成功调用后才自增，人机两套编号差一）、`CURRENT APPLICATION STATE` 大块（prompts.py:162-165）、逐条追加 `ACTION RESULT i:` 与 `ACTION ERROR i: ...{截断尾部}`（prompts.py:167-173，error 只保留最后 max_error_length 字符）。

## 三、外部连接

- **MessageManager**：唯一消费者。构造 SystemPrompt 实例并取系统消息（message_manager/service.py），每步 new 一个 AgentMessagePrompt（其 `add_state_message` 传 state/result/include_attributes）。
- **Registry/Controller**：`get_prompt_description()` 把七个注册动作渲染成 `{name: {param: schema}}` 文本注入 Functions 段（registry/views.py 的 `prompt_description`，滤掉 title 键）。
- **element.py/tree.py**：规则 4 描述的元素格式来自 `get_clickable_elements_string` 的输出；`-25212` 与 `Window not found` 文案对应 tree.py:320-321 的死分支（见坑 3）。
- **agent/service.py**：`_log_response` 的表情判定消费 `evaluation_previous_goal` 的 Success/Failed 子串（service.py:332-335）。

## 四、数据流

组装流向是单向的：`Registry → 动作描述文本`、`datetime → 时间戳`、`SystemPrompt 三构件 → SystemMessage`，在 MessageManager 构造时一次性入史；此后每步 `AgentMessagePrompt(state, last_results)` 生成临时 HumanMessage，阅后即焚（agent/service.py:217/227）。模型输出的 `current_state.memory` 字段是给**下一轮模型自己**的便签——经 `add_model_output` 永久入史后，成为跨步记忆的唯一载体；`evaluation_previous_goal` 强迫模型对上一步成败先表态再行动，是抑制"幻觉式推进"的关键设计。

## 五、设计决策与取舍

- **JSON 约定而非纯自由文本**：规则 1 用整段 JSON 示例锁死输出形状，配合 `with_structured_output`（service.py:313-315）双保险；对 Gemini 这类结构化输出较弱的模型，提示词层的格式教化比 API 层约束更有效——README.md:42 承认"OAI/Anthropic 最稳，Gemini 免费但没那么可靠"，这套冗长到近乎啰嗦的格式规则正是为弱模型加的护栏。
- **稳定/动态 UI 二分法**（prompts.py:43-44,74-75）：把"批量还是单步"的决策交给模型的场景判断，而非运行时检测——省了 UI 稳定性检测器这个大件，代价是判断错时靠 Controller 熔断兜底。
- **验证文化**（规则 5）：计算类任务必须从上下文元素（AXStaticText 的 value）读回结果验证后才能 done——把"评估"变成模型流程的强制节拍。
- **每步状态消息不含历史**：AgentMessagePrompt 只带本轮 state+上轮 result，跨步连贯性全押在 `memory` 字段上——上下文预算与记忆保真的折中。

## 六、新人提示（坑与勘误）

1. **规则 7 有挤行笔误（prompts.py:86）**：`"...UI interactions fail after retries.   - Use this for complex operations..."`——两个要点挤在一行（换行丢失），渲染后第二条规则视觉上消失在第一条的长段里。改提示词时别被它误导成"只有一条"。
2. **`include_attributes` 参数被接收但从未消费（prompts.py:138,155）**：`AgentMessagePrompt` 收下它存进 self，`get_user_message` 全程不读——它从 agent/service.py:69-80（HTML 属性默认值）一路传到这里，是"参数链路完整、末端无消费者"的装饰性参数链，与 agent 篇坑 4 同源。
3. **`-25212` 教了自救、代码却接不住（prompts.py:82 vs tree.py:320-321）**：提示词明确教模型"遇到 -25212/Window not found 就重新 open_app"，但 tree.py 对应分支 `if error == '-25212'` 是整数比字符串的永假死代码——该错误码实际会走通用失败路径（build_tree 返回 None → state 维持开场白），模型的"自救知识"半数靠运气生效。提示词与实现脱节的标本。
4. **步数显示差一（prompts.py:160）**：`step_number + 1` 补偿 agent/service.py:326 的后置自增；读对话记录时注意"Step 3/10"实际是第二次成功的 LLM 调用（失败重试不显示也不计步）。
5. **错误截断从头保尾（prompts.py:172-173）**：`result.error[-self.max_error_length:]` 只留错误尾部加 `...` 前缀——pydantic 校验错误最关键的 schema 描述常在开头，被截掉后模型只能靠"Return a valid JSON object"提示（service.py:275-277 追加的那句）猜方向。
6. **格式示例 `1[:]<AXButton>` 的 `[:]` 是字面量**：element.py 序列化输出的就是 `1[:]<AXButton ...>`（`[: ]` 无变量含义，疑似上游模板语法的化石），提示词照抄保持一致——自己写序列化器时务必同步这里，否则模型会对不上号。

（行号锚：prompts.py:6-131,20-94,22-39,41-44,47-55,57-62,64-75,77-83,82,85-91,86,93,96-107,109-131,114,133-175,134-156,158-175,160,162-165,167-173；agent/service.py:69-80,123,217,227,275-277,313-315,326,330-343,332-335；tree.py:320-321；controller/service.py:285；README.md:42）
