# 01 · Agent 编排主循环（phone_agent/agent.py）

> 对应知识图谱 tour 第 3 步「Agent 主循环」。本文所有行号锚均从源码核实。

## ① 角色定位

`agent.py` 是整个 Open-AutoGLM 的心脏：`PhoneAgent`（`phone_agent/agent.py:42`）把"截图感知 → 组装多模态消息 → 请求 VLM → 解析伪代码动作 → 执行并回填历史"固化为一个可循环的感知-决策-执行环。它不直接碰任何设备命令、不直接拼 HTTP 请求——截图走 `DeviceFactory`（`phone_agent/agent.py:11` 导入），推理走 `ModelClient`（`:12`），动作走 `ActionHandler`（`:8`）。全文件 253 行，是典型的"薄编排层"：任何一环换实现，主循环代码不动。

仓库里还有一条平行的 iOS 线（`agent_ios.py` 的 `IOSPhoneAgent`），对等复刻本循环但绕过工厂直连 WDA——改动作协议时两处都要动，这是同构双线的代价（详见 05 篇）。

## ② 内部结构

文件由三个 dataclass/类构成：

- **`AgentConfig`**（`phone_agent/agent.py:16`）：五个字段——`max_steps=100`（`:20`）、`device_id`、`lang`（默认 "cn"）、`system_prompt`、`verbose`。`__post_init__`（`:26-28`）在 prompt 为空时按语言从 `get_system_prompt` 取默认值，这就是提示词契约的注入点。
- **`StepResult`**（`:31`）：`success/finished/action/thinking/message` 五字段，单步执行的统一回报体。
- **`PhoneAgent`**：构造函数（`:64-79`）只做三件事——建 `ModelClient`（`:74`）、建 `ActionHandler` 并把 `confirmation_callback`/`takeover_callback` 两个安全回调穿透下去（`:75-79`）、初始化 `_context` 历史与 `_step_count`（`:81-82`）。

驱动模式有两种：`run(task)`（`:84`）全自动——清空状态后先带任务执行第一步（`:98`），`finished` 则直接返回 message（`:100-101`），否则在 `max_steps` 内循环裸跑 `_execute_step`（`:104-108`），超限返回 `"Max steps reached"`（`:110`）。`step(task)`（`:112`）单步模式供调试/人工干预，`is_first` 由 `_context` 是否为空推断（`:124`），首步无任务直接 `ValueError`（`:126-127`）。

核心私有方法 `_execute_step`（`:136`）按顺序做六件事：

1. **感知**：`get_device_factory()` 取截图与前台应用（`:143-145`）。
2. **组装**：首步追加 system 消息 + "任务指令 + screen_info + 截图"（`:148-160`）；后续步只发 `"** Screen Info **"` + screen_info + 新截图（`:162-169`）。
3. **决策**：`model_client.request(self._context)`（`:177`）；异常时打印堆栈并返回 `finished=True` 的失败 StepResult（`:178-187`）——模型错误直接终止任务，不重试。
4. **解析**：`parse_action(response.action)`（`:191`）；`ValueError` 时的兜底是 `finish(message=response.action)`（`:192-195`）——解析失败被包装成"以原始输出为遗言的 finish"。
5. **瘦身**：`remove_images_from_message` 剥掉刚用过的截图（`:205`），历史里只留文本。
6. **执行回填**：`action_handler.execute(action, screenshot.width, screenshot.height)`（`:209-211`），异常同样降级为 finish（`:212-217`）；随后把模型输出重构成 `<think>…</think><answer>…</answer>` 追加进历史（`:220-224`）；`finished` 判定 = `_metadata == "finish" or result.should_finish`（`:227`）。

`context`/`step_count` 两个 property（`:245-253`）暴露只读状态。

## ③ 外部连接

- **imports**：`phone_agent.actions`（ActionHandler）、`actions.handler`（do/finish/parse_action）、`config`（get_messages/get_system_prompt）、`device_factory`、`model`（ModelClient/ModelConfig）、`model.client.MessageBuilder`（`phone_agent/agent.py:8-13`）——正好横跨图谱五个子系统。
- **被谁用**：`phone_agent/__init__.py` 只导出 `PhoneAgent` 与 `IOSPhoneAgent` 两个门面；CLI 入口 `main.py` 组装 `AgentConfig`（main.py:771）后调 `agent.run(args.task)`（main.py:823）与交互循环（main.py:841）；`examples/basic_usage.py` 等示例走同一 API。iOS 线的 `agent_ios.py` 是平级消费者而非复用者。

## ④ 数据流

一轮完整数据流（以"打开小红书搜美食"为例）：

```
task(str)
 └→ run(): _context=[] → _execute_step(task, is_first=True)
     截图(base64,w,h) + current_app(str)          ← DeviceFactory
     _context += [system, user(task+screen_info+图)]
     ModelResponse{thinking, action}               ← ModelClient(流式)
     action_dict ← parse_action(action 字符串)      ← handler 层纯函数
     _context[-1] 剥图 → execute(action, w, h)      ← ActionHandler→设备
     _context += [assistant(<think>…<answer>…)]
 ← StepResult{success, finished, action, thinking, message}
```

关键不变量：**历史里 user 消息曾带图、请求前带图、请求后被剥成纯文本**（`:205`），所以每步恰好一张"活图"；截图发生在动作执行**之前**（`:144`），下一轮截图自然反映上一步效果——"检查上一步是否生效"（提示词规则 14）依赖这个时序。

## ⑤ 设计决策与陷阱

1. **解析失败即 finish，不重试**（`:192-195`）：模型输出不合伪代码语法时任务直接以原始文本收尾。这避免了死循环，但也意味着一次格式抖动就终止任务；想要重试语义需在此处改写。
2. **动作执行异常同样降级为 finish**（`:215-217`）：设备侧崩溃被转成"以异常信息为 message 的结束"，循环永不抛出。
3. **上下文只增不截断**：历史无限累积（仅剥图），`max_steps=100` 是唯一的增长上限；长任务 token 成本线性上升。
4. **首步与后续步消息形态不同**：首步 system+任务（`:148-160`），后续步无任务只有 Screen Info（`:162-169`）——多任务续跑需 `reset()`（`:131`）显式清场。
5. **模型错误终止 vs 动作错误吞掉**的不对称（`:181-187` vs `:212-217`）：前者 `success=False, finished=True`，后者只写进 finish message——排障时先分清是哪条路径。
6. **勘误钉版**：ONBOARDING 所述"模型客户端见 `</answer>` 断流省 token"在当前源码中不存在——`client.py` 的流式循环无 break，标记只控制终端打印（见 03 篇）；省 token 的真正机制是本文件的剥图（`:205`）。

## ⑥ 新人提示

- 精读顺序：先 `run`/`step`/`_execute_step` 三个方法体（`:84-243`），再回头看 `AgentConfig.__post_init__`（`:26`）理解提示词注入。
- 想加"每步落盘轨迹"之类的观测点，`_execute_step` 的 `:202` 与 `:237` 之间是天然插桩位（动作已解析、结果已就绪）。
- 改 `max_steps`、默认语言这类行为参数走 `AgentConfig`，不要在循环里硬编码。
- 调试单步行为用 `step()` + 打印 `agent.context`（只读副本，`:248`），比 `run()` 全自动更可控。
- 记住本文件不做任何平台分支：若你发现自己在 agent.py 里写 `if android else harmonyos`，说明逻辑放错了层——应下沉到工厂或设备栈。
