# 03 · 模型客户端与消息构建（phone_agent/model/client.py）

> 对应 tour 第 5 步「模型客户端与消息构建」。含一处对 ONBOARDING 的重要勘误。

## ① 角色定位

`client.py` 是 Agent 与 VLM 之间唯一的边界：`ModelClient`（`phone_agent/model/client.py:41`）封装 OpenAI 兼容流式请求、把原始输出切成 thinking/action 两段并计时；`MessageBuilder`（`:219`）负责 system/user/assistant 三种消息与 base64 截图的拼装。它对上是纯函数式接口（`request(messages) -> ModelResponse`），对下只依赖 `openai` SDK 与 i18n 文案——换模型供应商（BigModel/ModelScope/自部署 vLLM/SGLang）只动 `ModelConfig`，不动本文件。

## ② 内部结构

**`ModelConfig`**（`:13-25`）：`base_url` 默认 `http://localhost:8000/v1`（`:17`）、`api_key="EMPTY"`（`:18`）、`model_name="autoglm-phone-9b"`（`:19`）、`max_tokens=3000`（`:20`）、`temperature=0.0`（`:21`）、`top_p=0.85`（`:22`）、`frequency_penalty=0.2`（`:23`）、`extra_body` 透传 dict（`:24`）——temperature 归零是为动作决策的可复现性，这是 GUI Agent 与闲聊模型配置的分水岭。

**`ModelResponse`**（`:28-38`）：`thinking/action/raw_content` 三字段 + 三个性能指标槽位（TTFT `:36`、thinking 结束时间 `:37`、总耗时 `:38`）。

**`ModelClient.request`**（`:53`）分四段：

1. **建流**：`chat.completions.create(..., stream=True)`（`:71-80`），全部采样参数来自 config。
2. **流式消费**（`:82-140`）：核心状态是 `raw_content`（全量累积）、`buffer`（待打印缓冲）、`action_markers = ["finish(message=", "do(action="]`（`:84`）、`in_action_phase` 旗标（`:85`）。每个 chunk 先记 TTFT（`:96-98`）；一旦 buffer 中出现任一 marker，打印 marker 之前的 thinking 段、置 `in_action_phase=True` 并记录 thinking 结束时间（`:108-121`）；此后内容只进 `raw_content` 不再打印（`:100-102`）。打印侧还有"疑似 marker 前缀"的Hold逻辑——buffer 尾部若是某 marker 的前缀就暂不打印，防止把 `do(act` 半截打到终端（`:126-140`）。
3. **解析**：`_parse_response(raw_content)`（`:146`）。
4. **指标打印**：双语 `get_message` 输出三项耗时（`:149-165`）。

**`_parse_response`**（`:176`）四级降级：规则 1 含 `finish(message=` 则一切之前为 thinking（`:195-199`）；规则 2 含 `do(action=` 同理（`:202-206`）；规则 3 回退遗留 `<answer>` XML 标签解析（`:209-213`）；规则 4 无任何标记则 thinking 置空、全文当 action（`:215-216`）。规则 3/4 保证了对接任意 OpenAI 兼容模型时即便不守 AutoGLM 格式也能拿到内容往下走。

**`MessageBuilder`**（全静态方法）：`create_system_message` 纯字符串（`:223-225`）；`create_user_message` 把截图放在 content 数组**第一位**、文本第二位（`:241-252`）；`create_assistant_message`（`:256-258`）；`remove_images_from_message` 只保留 `type=="text"` 的 part（`:271-274`）；`build_screen_info` 把 `current_app` 与额外信息 dumps 成 JSON 串（`:278-290`）。

## ③ 外部连接

- **imports**：`openai.OpenAI`（`:8`）与 `config.i18n.get_message`（`:10`）——后者让性能报告随 `ModelConfig.lang` 切换中英文案（`i18n.py` 的 `MESSAGES_ZH/MESSAGES_EN` 双字典 `phone_agent/config/i18n.py:4,29`，`get_message` 缺键回退键名 `:81`）。
- **被谁用**：`agent.py` 构造期建客户端（`phone_agent/agent.py:74`）、每步调 `request`（`:177`）并用 `MessageBuilder` 三兄弟组装/瘦身历史（`:149-169,205,220-224`）；`agent_ios.py` 平行复用；`main.py:748` 从命令行参数组装 `ModelConfig`；`scripts/check_deployment_cn.py` 携样例直探自部署端点。`model/__init__.py` 只导出 `ModelClient/ModelConfig` 两个名字。

## ④ 数据流

```
agent._context(含 system + 历史 + 本轮截图)
 → request(): OpenAI stream
    chunk流 ─┬─ raw_content(全量) ─→ _parse_response → (thinking, action)
              └─ buffer → 终端实时打印 thinking，见 marker 停印
 → ModelResponse{thinking, action, raw_content, TTFT, t_thinking_end, total}
 → agent 侧: parse_action(action) 进入动作层
```

与 01 篇合看：**上下文瘦身发生在 agent 侧**（请求后剥图），本模块的 `raw_content` 只是每轮临时产物，不回写历史；assistant 历史由 agent 重构为 `<think>…</think><answer>…</answer>` 文本（`phone_agent/agent.py:222`），注意这与流式打印用的 marker 协议（`do(action=`）**不是**同一套标记——历史回放用的是 XML 标签格式，当前轮解析用的是函数调用格式，两套标记在规则 3 处汇合。

## ⑤ 设计决策与陷阱

1. **勘误钉版（重要）**：ONBOARDING 与 tour 描述称"见 `</answer>` 提前终止省 token"——**当前源码没有这个 break**。`for chunk in stream` 循环跑满全程（`:88-140`），`in_action_phase` 只是停止终端打印（`:100-102`），token 照常消费到流结束。动作标记是 `finish(message=`/`do(action=`（`:84`），不是 `</answer>`；`<answer>` 只出现在解析降级规则 3（`:209`）。若要省 token 需自行加 break——但注意提前断流会让 `raw_content` 缺尾、`_parse_response` 截断 action。
2. **打印与解析双轨**：流式打印为人类观察设计（marker Hold 防半截 `:126-135`），解析走完整 `raw_content`——两者解耦，终端显示不全不代表解析丢内容。
3. **temperature=0 但 `frequency_penalty=0.2`**（`:21,23`）：组合意图是"确定性格式 + 抑制复读"，长任务里若动作文本重复率高可调。
4. **thinking/action 切分点取第一个 marker**（`split(…, 1)` `:196,203`）：若 thinking 文本里模型自己写了示例 `do(action=…)`，会被误切——规则 4 的全文当 action 是最后的兜底。
5. **图片在消息最前**（`:244-249`）：部分推理服务对多模态 part 顺序敏感，调整前先验证端点行为。
6. **TTFT 等指标只打印不落盘**（`:149-165`）：做延迟统计需自行采集 `ModelResponse` 返回值。

## ⑥ 新人提示

- 换端点三步：`ModelConfig(base_url=…, api_key=…, model_name=…)` → 用 `scripts/check_deployment_cn.py` 探活 → `main.py --base-url/--model-name` 直接跑。
- 调"模型输出解析老失败"时，先 `print(ModelResponse.raw_content)` 看原始串落在 `_parse_response` 哪条规则（`:195-216`），90% 是模型没按伪代码格式输出。
- 加新采样参数走 `extra_body`（`:24`）透传，别扩散构造函数签名。
- `MessageBuilder` 是静态类，测试里可直接伪造 `agent._context` 结构（dict 列表）单测主循环，无需起真模型。
- 本模块 print 较多（含每轮指标块），要接 GUI 前端需先把这些 stdout 输出改造为日志/回调。
