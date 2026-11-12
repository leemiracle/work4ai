# model.py — 模型访问层：TypeSafe 单请求双决策 + 可选小模型写文本

## 一、角色定位

model.py 是全仓唯一的联网点，docstring（model.py:1）分工明确：**TypeSafe 负责选择**（operation 与 target 都是受限枚举的 choice），**可选的小型 OpenAI 兼容模型只负责写字段值**。它把 agent 的"决策"问题翻译成一次结构化请求（operation 头 + 各操作独立的 target 头），把"打字"问题翻译成一次带 JSON schema 约束的 chat 调用。上游消费者只有 agent.py:8（choose/field_context/field_text/action_space）与 tests/test_agent.py:11；提示词文本全部来自 questions.py（model.py:10）。README 里"Two decisions, one network round trip"的性能主张由本文件的 choose 实现。

## 二、内部结构

**共享客户端与传输层（model.py:12-27）**：模块级 `httpx.Client(http2=True, timeout=25)`（model.py:12），HTTP/2 长连接复用是低延迟的一部分。post_json 最多 3 次尝试，仅对 429/529/503 按 `0.5 * 2**attempt` 指数退避（model.py:21-23）；网络异常与其他错误码一律转 RuntimeError 且语义都是"no action executed"——**传输失败绝不等价于执行了某动作**，这与 agent 层"决策先消费"配合形成闭环。

**validate_choice（model.py:30-45）**：对模型 choice 回答的全量结构校验，六条规则一次过：choice 在合法 id 集内；概率键集合与 id 集合完全相等；所有数值是 0-1 的有限数（math.isfinite 顺带挡 NaN/inf，model.py:37）；概率和为 1±0.02；被选项概率必须是最大值减 1e-6 以内（model.py:39）。任何 KeyError/TypeError/ValueError 都折叠为统一的"Invalid TypeSafe response"（model.py:41-44）。tests/test_agent.py:48-64 用 6 种变异（unknown/nan/missing/negative/non_max/confidence）逐一锁定。

**action_space（model.py:48-78）**：把 snapshot.js 产出的扁平 actions 折叠成三层结构。规则：**同一 DOM 节点只分一个递增索引**（model.py:58-66），click/fill/select 三种操作各建一个 target 组（operations 映射表在 model.py:51）；不在此三类的动作（wait/scroll/done 等）进 controls，键为 id 大写（model.py:54-55）。select 特殊：每个可选 option 单独一个目标，键为 `"index:序号"` 复合形式并携带 value（model.py:74-76）。元素条目保留 role/value/checked/selected/expanded 状态（model.py:61），label 取 `→` 前的主名（model.py:62）。

**choose（model.py:81-148）**——决策主函数：

1. 组 operation 问题：criteria 是"各操作语义说明 + controls 标签 + DONE/BLOCKED 定义"（model.py:83-90），instructions 携带 goal 与 NEXT_ACTION 规则（model.py:92）。
2. **投机式 target 头**：为每个出现的操作各建一个 `<op>_target` 问题（model.py:94-106），criteria 是该操作兼容的候选元素（含 index/element 标签/current_value/checked 等状态），instructions 的 rules 同时包含 NEXT_ACTION 与 TARGET（model.py:105）——两套头读同一份规则，tests/test_agent.py:128 断言了这种包含关系。
3. 请求体（model.py:107-117）：模型名取 `TYPESAFE_MODEL` 默认 jev-latest；state 只放 page 的 url/title/text、elements 表、最近 10 条动作摘要（recent_actions，model.py:112-114）——**不含截图**。
4. 单次 POST 到 `https://api.typesafe.ai/v1/systemone`（model.py:119）。
5. **只消费被选中操作对应的头**（model.py:120-133）：operation 回答先过 validate_choice；若选中 CLICK，则只校验 click_target 头，其余头（哪怕是垃圾）不参与执行（model.py:126 注释："Unused target heads cannot cause an action"）；目标概率再映射回动作 id（model.py:130）。controls/DONE/BLOCKED 则直接从 operation 概率取值（model.py:132-133）。tests/test_agent.py:99-113 证明"click 无法消费 type_text 头的答案"。
6. 返回值携带全套审计材料：两套 probabilities/confidence、raw_answers、model、usage、latency_ms 与原始 request（model.py:134-148）。

**field_context / field_text（model.py:151-198）**——文本助手。field_context 组装 goal、字段三元组（label/role/value）、页面标题与截断到 6000 字符的正文、最近 6 条动作（model.py:151-157）。field_text 三道闸：① 无 `TEXT_MODEL_API_KEY` 直接抛错，"no text is hardcoded or guessed"（model.py:161-163）；② 按端点自动配思考开关——deepseek 域关 thinking，其余 reasoning effort=low，`TEXT_MODEL_REASONING=none` 再覆盖（model.py:166-168）；③ 严格解析：响应必须是 `response_format=json_object` 的 chat 结果，内容必须解析为**恰好一个 text 键**、值为非空字符串且 ≤2000 字符（model.py:187-193），否则"nothing typed"。返回值附带 helper 元数据（模型名/延迟/usage，model.py:194-198），供 agent 记入 text_calls。注意 TEXT_VALUE 提示词允许返回 `{"text": null}`（缺值信号），但代码对 null 同样抛错——**null 是受控失败路径，不是"跳过输入"**。

## 三、外部连接

依赖：httpx（唯一第三方直接依赖）+ questions.py 的 NEXT_ACTION/TARGET/TEXT_VALUE（model.py:10，消费点在 model.py:92、105、179）。环境变量四个：TYPESAFE_API_KEY（必需）、TYPESAFE_MODEL、TEXT_MODEL_API_KEY/BASE_URL/MODEL/REASONING。被 agent.py 与 tests 消费；tests 用 monkeypatch 替换 post_json（tests/test_agent.py:92、144、310）实现零付费 API 的离线验证。

## 四、数据流

进：choose 收 state（观察字典，用其 actions/url/title/text）、goal、history。出：decision 字典（choice 是 action id 或 DONE/BLOCKED 串，operation 是大写操作名，target 是索引或 "index:n"）；field_text 出 (value 字符串, helper 元数据)。中间数据形态：请求体的 questions 结构即 TypeSafe 的 fan-out 模式（一次请求多个独立问题）；raw_answers 保留模型原话用于前端展示与审计。

## 五、设计决策与取舍

1. **投机 fan-out 换延迟**：一次网络往返同时拿 operation 与全部 target 头，代价是浪费了未被选中的头的推理；换来的是串行两次调用的延迟消除（README：两决策一往返）。2. **校验即安全边界**：所有模型输出必须通过 validate_choice / JSON 解析闸，模型永远无法产出选择器、坐标或代码——executor 侧只认 int 型节点 ID（browser.py:141-142）。3. **未选头不校验**：只校验被消费的头，避免无关头的噪声触发整个决策失败。4. **文本生成与决策分离**：选哪个字段由 TypeSafe 决定，字段值由小模型生成——主模型不必为"填什么值"分心，且文本模型可独立换型（deepseek/mercury/glm 等皆可）。5. **重试只覆盖"未执行"的失败**：post_json 重试纯传输层，任何已到达执行层的错误都不重试，与"变异不可重试"宪法一致。6. **上下文极简**：10 条动作摘要 + 6000 字符正文，控制 token 成本与噪声。

## 六、新人提示

- 默认端点硬编码为 `https://api.typesafe.ai/v1/systemone`（model.py:119），文本助手默认 deepseek（model.py:164-165）但 README 的推荐配置是 OpenRouter 的 mercury——两种配置都合法，别被默认值误导。
- validate_choice 的概率和容差是 0.02、最大值容差 1e-6（model.py:38-39）：前者容忍模型算术误差，后者是严格的"选中即最大"约束。
- field_text 的 `set(output) != {"text"}` 检查（model.py:190）意味着任何附带键（哪怕有用的解释）都判废——这是刻意换取的可预测性。
- reasoning 配置的匹配串是 `"api.deepseek.com/" in base`（model.py:166），自建代理若路径里含这个域也会命中 deepseek 分支。
- usage 字段用 `result.get("usage", {})` 容错（model.py:145），端点不回 usage 不会崩。
- 图谱 hub 对本文件的概括（单请求 operation+target 头、退避重试、概率校验）与源码一致；tour 第 3 步"唯一联网点"的说法亦核实无误。
