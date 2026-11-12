# 05 · 模型客户端（Model Client）

> 本文解析 `phone_agent/model/client.py`（290 行）。
> 这一层负责与 AutoGLM-Phone-9B 模型服务通信，**流式**接收响应并**实时**分离 thinking/action。

## 文件地图

| 文件 | 行数 | 作用 |
|------|------|------|
| `phone_agent/model/__init__.py` | 5 | 导出 `ModelClient`, `ModelConfig` |
| `phone_agent/model/client.py` | 290 | **ModelClient** + `ModelConfig` + `ModelResponse` + `MessageBuilder` |

## 三个核心类

```python
@dataclass
class ModelConfig:        # client.py:13-25
    base_url: str = "http://localhost:8000/v1"
    api_key: str = "EMPTY"
    model_name: str = "autoglm-phone-9b"
    max_tokens: int = 3000
    temperature: float = 0.0
    top_p: float = 0.85
    frequency_penalty: float = 0.2
    extra_body: dict[str, Any] = field(default_factory=dict)
    lang: str = "cn"

@dataclass
class ModelResponse:      # client.py:28-38
    thinking: str
    action: str
    raw_content: str
    time_to_first_token: float | None = None    # 性能指标
    time_to_thinking_end: float | None = None
    total_time: float | None = None

class ModelClient:        # client.py:41-216
    def __init__(config: ModelConfig | None = None)
    def request(messages) -> ModelResponse       # 流式请求 + 解析
    def _parse_response(content) -> (thinking, action)
```

外加辅助类 `MessageBuilder`（`client.py:219-290`），提供 OpenAI 消息构造工具。

## 关键设计：OpenAI 兼容

```python
from openai import OpenAI
self.client = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)
```

**直接用官方 `openai` SDK**，不改协议。好处：
- 任何 OpenAI 兼容的推理引擎都能接（vLLM / SGLang / TGI / lmdeploy）
- 第三方托管服务（BigModel / ModelScope / OpenRouter）也能接
- SDK 自动处理流式 chunk 解析、错误重试等

**代价**：被 OpenAI 消息格式锁定。如果想用非 OpenAI 格式的模型（如某些原生多模态 API），需要适配层。

## `request`：流式请求 + 实时分离

`client.py:53-174`。这是最复杂的方法，分 4 段。

### 段 1：发起流式请求（53-80）

```python
def request(self, messages: list[dict[str, Any]]) -> ModelResponse:
    start_time = time.time()
    time_to_first_token = None
    time_to_thinking_end = None

    stream = self.client.chat.completions.create(
        messages=messages,
        model=self.config.model_name,
        max_tokens=self.config.max_tokens,
        temperature=self.config.temperature,
        top_p=self.config.top_p,
        frequency_penalty=self.config.frequency_penalty,
        extra_body=self.config.extra_body,
        stream=True,    # ★ 流式
    )
```

**为什么 `stream=True` 而非一次性请求？**
- AutoGLM 的 thinking 部分可能很长（几百 token），非流式要等全部生成完才能看到任何内容
- 流式可以**实时打印 thinking** 给用户看，体验好很多（类似 ChatGPT 的打字效果）
- 可以采集 `time_to_first_token` 等性能指标

### 段 2：流式 chunk 处理（82-140，核心难点）

这是整个文件最绕的部分。问题：**如何在流式中区分 thinking 和 action？**

模型流式输出可能是这样的 chunk 序列：

```
"用户想"  →  "搜索美食"  →  "，需要先点"  →  "击搜索框。\n"  →  "do(act"  →  "ion=\"Tap\""  →  ", element=[500, 120])"
```

前 5 个 chunk 是 thinking，后 3 个 chunk 是 action。但**收到第 5 个 chunk `do(act` 时还不知道它是 marker 的开始**——可能只是 thinking 里的文字。

**算法**（带缓冲的 marker 检测器）：

```python
raw_content = ""
buffer = ""
action_markers = ["finish(message=", "do(action="]
in_action_phase = False
first_token_received = False

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        content = chunk.choices[0].delta.content
        raw_content += content

        # 采集首 token 时间
        if not first_token_received:
            time_to_first_token = time.time() - start_time
            first_token_received = True

        # 已进入 action 阶段:静默累积
        if in_action_phase:
            continue

        buffer += content

        # 检测完整 marker
        marker_found = False
        for marker in action_markers:
            if marker in buffer:
                thinking_part = buffer.split(marker, 1)[0]
                print(thinking_part, end="", flush=True)
                print()
                in_action_phase = True
                marker_found = True
                if time_to_thinking_end is None:
                    time_to_thinking_end = time.time() - start_time
                break

        if marker_found:
            continue

        # 检测 marker 前缀(防止把 marker 片段提前打出)
        is_potential_marker = False
        for marker in action_markers:
            for i in range(1, len(marker)):
                if buffer.endswith(marker[:i]):
                    is_potential_marker = True
                    break
            if is_potential_marker:
                break

        # 安全:buffer 不像 marker 前缀,可以打印
        if not is_potential_marker:
            print(buffer, end="", flush=True)
            buffer = ""
```

**逻辑拆解**：

1. **`raw_content`**：累积所有 chunk 的原始内容，最后用来解析 thinking/action。
2. **`buffer`**：临时缓冲，用来检测 marker。
3. **`in_action_phase`**：一旦检测到完整 marker，置 True，之后所有 chunk 只进 `raw_content` 不打印。
4. **前缀检测**：如果 buffer 末尾是某个 marker 的前缀（如 buffer=`"思考完成。do(ac"`，结尾 `"do(ac"` 是 `"do(action="` 的前缀），就**不打印**，等下个 chunk 确认。如果不是任何 marker 的前缀，就安全打印并清空 buffer。

**效果**：
- thinking 部分**实时逐字符**打印到 stdout
- action 部分**静默**累积
- 不会把 marker 片段（如 `"do(ac"`）误打到屏幕

### 段 3：解析 thinking/action（142-146）

```python
total_time = time.time() - start_time
thinking, action = self._parse_response(raw_content)
```

### 段 4：打印性能指标（148-174）

```python
lang = self.config.lang
print()
print("=" * 50)
print(f"⏱️  {get_message('performance_metrics', lang)}:")
print("-" * 50)
if time_to_first_token is not None:
    print(f"{get_message('time_to_first_token', lang)}: {time_to_first_token:.3f}s")
if time_to_thinking_end is not None:
    print(f"{get_message('time_to_thinking_end', lang)}:        {time_to_thinking_end:.3f}s")
print(f"{get_message('total_inference_time', lang)}:          {total_time:.3f}s")
print("=" * 50)

return ModelResponse(
    thinking=thinking, action=action, raw_content=raw_content,
    time_to_first_token=time_to_first_token,
    time_to_thinking_end=time_to_thinking_end,
    total_time=total_time,
)
```

**三个性能指标的含义**：

| 指标 | 含义 | 典型值（vLLM, A100） | 含义 |
|------|------|---------------------|------|
| `time_to_first_token` | 首 token 延迟 | 0.3-1.0s | prefill 阶段时长（处理图片+上下文）|
| `time_to_thinking_end` | thinking 完成时刻 | 2-5s | thinking 生成完成，开始生成 action |
| `total_time` | 总推理时间 | 3-8s | 整个响应完成 |

**性能调优洞察**：
- 如果 `time_to_first_token` 高 → prefill 慢，可能是图片分辨率太高或上下文太长
- 如果 `total_time - time_to_thinking_end` 高 → action 生成慢（少见，action 通常很短）
- 如果 `time_to_thinking_end - time_to_first_token` 高 → 模型 thinking 太长，考虑限制 `max_tokens` 或改 prompt 让它简洁

## `_parse_response`：解析规则

`client.py:176-216`。**四条优先级规则**：

```python
def _parse_response(self, content: str) -> tuple[str, str]:
    # 规则 1: finish(message= 优先级最高
    if "finish(message=" in content:
        parts = content.split("finish(message=", 1)
        return parts[0].strip(), "finish(message=" + parts[1]

    # 规则 2: do(action=
    if "do(action=" in content:
        parts = content.split("do(action=", 1)
        return parts[0].strip(), "do(action=" + parts[1]

    # 规则 3: legacy XML tag 兜底
    if "<answer>" in content:
        parts = content.split("<answer>", 1)
        thinking = parts[0].replace("<think>", "").replace("</think>", "").strip()
        action = parts[1].replace("</answer>", "").strip()
        return thinking, action

    # 规则 4: 无 marker,全部当 action
    return "", content
```

**协议演进洞察**：

prompt（`prompts_zh.py`）要求模型输出 `<think>...</think><answer>...</answer>` XML 格式，但 parser **优先匹配裸函数调用**（规则 1、2），XML 是 fallback（规则 3）。

这说明：**模型实际行为已演化为直接输出 `do(...)`/`finish(...)`，不带 XML 包裹**，而 prompt 描述滞后。证据：
- 流式打印的 marker 是 `["finish(message=", "do(action="]`，不是 `<answer>`
- 规则 1、2 的优先级高于规则 3

**为什么规则 1 优先于规则 2？**

如果 thinking 里提到了 `do(action=`（比如模型在思考"我应该用 do(action=Tap)"），而最终输出是 `finish`，规则 1 先匹配 `finish` 能正确分离。反之如果先匹配 `do`，会把 thinking 里的 `do(action=` 误当 action 边界。

实际中这种情况罕见，但规则 1 优先更安全。

## `MessageBuilder`：消息构造工具

`client.py:219-290`。4 个静态方法：

### `create_system_message(content)`

```python
{"role": "system", "content": content}
```

### `create_user_message(text, image_base64=None)`

```python
{
    "role": "user",
    "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
        {"type": "text", "text": text}
    ]
}
```

**注意顺序**：**图片在前，文字在后**。这是 AutoGLM 模型偏好的格式（也可能影响其他 VLM）。如果你想换模型，可能需要调整顺序。

### `create_assistant_message(content)`

```python
{"role": "assistant", "content": content}
```

content 是字符串（不是 list），因为 assistant 回复不含图片。

### `remove_images_from_message(message)`

```python
if isinstance(message.get("content"), list):
    message["content"] = [item for item in message["content"] if item.get("type") == "text"]
return message
```

把 user message 里的图片 strip 掉，只留文字。**这是 token 省钱的关键**（见 [02-agent-loop.md](02-agent-loop.md#段-5图片清理--动作执行204-217)）。

> **注意**：这是**原地修改** message dict 并返回，不是创建新 dict。所以调用方 `self._context[-1] = MessageBuilder.remove_images_from_message(self._context[-1])` 看似多余，实际是必要的（虽然原地改了，但赋值回去更明确）。

### `build_screen_info(current_app, **extra_info)`

```python
info = {"current_app": current_app, **extra_info}
return json.dumps(info, ensure_ascii=False)
```

生成 `{"current_app": "小红书"}` 这样的 JSON 字符串。`**extra_info` 预留扩展（目前没人传 extra）。

## 配置参数详解

| 参数 | 默认 | 调参建议 |
|------|------|---------|
| `base_url` | `http://localhost:8000/v1` | 模型服务地址，必须以 `/v1` 结尾（OpenAI 协议）|
| `api_key` | `"EMPTY"` | 本地部署用 EMPTY；托管服务用真实 key |
| `model_name` | `autoglm-phone-9b` | 必须与服务端 `--served-model-name` 一致 |
| `max_tokens` | `3000` | thinking + action 总长度上限。太小会截断 thinking |
| `temperature` | `0.0` | **0 = 贪心**，最确定性。Agent 任务推荐低温度 |
| `top_p` | `0.85` | nucleus sampling，与 temperature 协同 |
| `frequency_penalty` | `0.2` | 轻微惩罚重复，防止 thinking 车轱辘话 |
| `extra_body` | `{}` | 传非标准参数给推理引擎（如 vLLM 专属选项）|
| `lang` | `"cn"` | 只影响**性能指标打印语言**，不影响模型行为 |

### 为什么 temperature=0？

Agent 任务要求**确定性**——同一任务+同一截图应该产生同一动作。`temperature=0` 让模型几乎贪心解码（vLLM 等引擎在 T=0 时可能仍用贪婪或 argmax）。

如果你想增加多样性（如探索不同解法路径），可以提到 0.1-0.3，但**会牺牲可复现性**。

### frequency_penalty=0.2 的作用

防止模型在 thinking 里反复说同一句话（LLM 常见 degeneration 模式）。0.2 是轻微惩罚，不会影响正常表达。

## 换模型的注意事项

如果你想用其他 VLM（如 GPT-4V、Qwen-VL、InternVL）替换 AutoGLM-Phone-9B：

| 维度 | 需要改什么 |
|------|----------|
| API 兼容 | 大多数 OpenAI 兼容，直接改 `base_url`/`model_name` 即可 |
| **输出格式** | ⚠️ **必须**确认新模型能输出 `do(action=...)` 格式。否则要改 prompt 和 `_parse_response` |
| 图片顺序 | `MessageBuilder` 是图前文后，某些模型偏好文前图后 |
| Token 限制 | 不同模型 `max_tokens` 上限不同 |
| 流式支持 | 必须支持 SSE 流式，否则 `request` 会挂 |

**最大障碍是输出格式**。AutoGLM 是**专门训练**输出 `do(...)` 格式的，换通用 VLM 几乎肯定要先 fine-tune 或改 prompt + parser。

## 与 model/__init__.py 的关系

`model/__init__.py` 只导出 `ModelClient` 和 `ModelConfig`：

```python
from phone_agent.actions.handler import do, finish, parse_action  # 隐藏依赖
from phone_agent.model.client import ModelClient, ModelConfig, ModelResponse, MessageBuilder
```

`ModelResponse` 和 `MessageBuilder` **没有被包级导出**，但被 agent.py 直接从 `model.client` import。这是个小的不一致——理想情况下应该都从 `phone_agent.model` 导入。

## 性能指标采集的局限

当前性能指标只记录时间，不记录 token 数。如果你想算 tokens/second：

```python
# 估算(不精确)
thinking_tokens = len(response.thinking) / 3   # 粗略 3 字符/token
action_tokens = len(response.action) / 3
total_tokens = thinking_tokens + action_tokens
tps = total_tokens / response.total_time
```

精确做法是在请求里加 `stream_options={"include_usage": True}`，让 OpenAI SDK 在最后一个 chunk 返回 usage。当前代码没启用。

## 常见陷阱

### 1. base_url 必须以 /v1 结尾

`http://localhost:8000` ❌（缺 /v1）
`http://localhost:8000/v1` ✅

OpenAI SDK 会在 base_url 后拼接 `/chat/completions`，少了 `/v1` 会 404。

### 2. model_name 必须匹配服务端

vLLM/SGLang 启动时的 `--served-model-name autoglm-phone-9b` 必须与 `ModelConfig.model_name` 完全一致（区分大小写）。否则服务端返回 model not found。

### 3. 流式 chunk 可能为空

```python
if len(chunk.choices) == 0:
    continue
if chunk.choices[0].delta.content is not None:
    ...
```

某些 chunk 只有 usage 没有 content（最后一个 chunk），必须 null check，否则 AttributeError。

### 4. 性能指标打印无法关闭

`request` 总是打印性能指标，不受 `verbose` 控制。如果你想静默，需要改 `client.py:148-165` 加 `if self.config.verbose:`（但 `ModelConfig` 没有 verbose 字段，要加）。

## 下一步

- 想了解 message 怎么组装 → [02-agent-loop.md](02-agent-loop.md#段-2组装消息147-169)
- 想了解 action 怎么解析 → [04-action-handler.md](04-action-handler.md#parse_action-解析逻辑)
- 想改用非 OpenAI 格式模型 → 改 `ModelClient.__init__` 换 SDK + 改 `request` 适配响应格式
- 想换 prompt → [06-config-prompts.md](06-config-prompts.md)

---
