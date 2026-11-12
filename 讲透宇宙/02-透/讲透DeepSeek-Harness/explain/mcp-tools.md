# mcp-client/src/tools.ts — MCP 工具桥：外部工具的确定性融入

> 原文件：[`packages/mcp/mcp-client/src/tools.ts`](../../../explore/deepseek-ai/deepseek-harness/packages/mcp/mcp-client/src/tools.ts)（560 行）

## 角色定位

这个文件是 MCP（Model Context Protocol）与 harness 工具体系之间的**桥接层**：`syncTools` 拉取 MCP 服务器的工具清单，为每个工具计算一个**确定性公共名**注册进 `ctx.tools`（ToolRuntime）；模型调用这个公共名时，桥把调用映射回服务器的原始工具名发往 MCP 服务器，再把返回内容（文本与图像）投影成 Harness 的工具结果。一句话：让外部 MCP 工具用起来和本地工具一模一样，且跨重启名字不变。

## 内部结构

**命名契约**：公共名由**服务器名 + 工具名（+ 短哈希消歧）**构成（`mcp__<serverName>__<rawName>` 模式），并规范化到 DeepSeek 函数名的字符约束。三条铁律：确定性（同样的服务器与工具永远算出同名——会话日志里记录的工具调用可重放）；**原始名只上线**（wire 上发给服务器的 `tools/call` 用 raw name）；**公共名永不反解析**（不存在"从公共名拆回服务器名"的路径，杜绝歧义与注入面）。短哈希负责同名冲突时的消歧。

**注册与再同步**：`syncTools` 在连接建立与服务器工具清单变化时触发 re-sync——增删工具即时反映到注册表。`ToolBridgeOptions` 携带 `serverName`、`toolCallTimeoutMs` 与 `registrationFailure: 'contain' | 'throw'`：contain 模式下单服务器注册失败被遏制（记日志、跳过），throw 模式直接上抛——策略显式可选。

**内容投影**：MCP 工具返回文本与图像两类内容。文本直出；图像走完整准入链：base64 校验 → 准入策略（模型模态与会话 header 双重检查——纯文本模型收不下图像）→ 保存进 `AttachmentStore` 附件存储、结果里留引用。`isImageAdmissionError` 把"图像被拒"识别为可分类的错误而非崩溃。

**输出 schema 校验**：MCP 工具声明的输出 schema 经 JSON Schema **白名单**校验——只接受 harness 模型面能表达的子集，超出的部分拒绝注册（fail-loud 而非截断）。

## 外部连接

包内：`connection.ts` 持有本桥（每个服务器连接建立后调 syncTools）；入口 `index.ts` 管 Config（stdio/http 服务器清单与重连参数）、经 effect 启动连接并挂 dispose。跨包：`ctx.tools`（注册目标，享受 ToolRuntime 的管线与遮蔽）；`AttachmentStore`（图像落点）；模型侧消费经 agent-loop 的工具执行。图谱确认 import 面干净（无包内静态依赖），被 `connection.ts` 单点消费。

连接层的另一半值得了解：`connection.ts` 的 `startConnection` 在 stdio 与 http 两种传输上管理服务器会话，`resolveReconnectPolicy` 把 Config 里的重连参数解析成策略——断线重连成功、服务器工具清单变化，都会触发本桥 re-sync，注册表随之差异更新。入口 `index.ts` 用 effect 启动每条连接并挂 dispose，活跃服务器名集合维持着"当前有哪些桥活着"的真相。

## 数据流

注册期：服务器连接就绪 → 拉取工具清单 → 逐工具计算公共名 + 校验输入/输出 schema → 注册进 ToolRuntime（contain 或 throw）→ 模型从此看得见这些工具。调用期：模型 tool_call（公共名）→ 桥定位服务器与 raw name → 组装 `tools/call`（带超时）→ 服务器返回内容序列 → 文本直出、图像走准入链入附件 → 规范化为工具结果 → 落会话日志。维护期：服务器清单变化 → re-sync → 注册表差异更新；连接断开 → 注册随连接 dispose。

## 设计决策

**确定性命名是全部技巧的支点**：会话重放要求"日志里的工具调用在当时与现在都指向同一工具"。随机后缀或序号都会破坏这一点，所以公共名是纯函数计算的结果，短哈希只在真冲突时介入且同样确定。

**raw-on-wire-only + 永不反解析**：桥内部持有"公共名 ↔ (服务器, 原始名)"的映射，映射不外泄。若允许从公共名字符串反解出服务器，一个恶意服务器名就能伪造他人的工具——单向设计把这条攻击路径物理删除。

**contain/throw 显式二选一**：单服务器故障要不要拖垮整个桥，是部署策略不是技术对错，因此做成选项而非硬编码。

**图像准入双重检查**：模型模态（能不能收图）与会话 header（该不该收图）分别判定——任何一个说不，图像就以受控错误落账，而不是塞给模型一个它处理不了的结果。

**schema 白名单而非全量透传**：MCP 的 schema 表达力超出模型面约束时，拒绝比截断诚实——静默截断的 schema 会制造"模型以为有字段其实没有"的幻觉。

## 新人提示

调试 MCP 工具问题时的第一开关是 `registrationFailure: 'throw'`——把遏制改成上抛，注册期错误立刻现形（contain 模式下它们只躺在日志里）。"模型看不见某工具"按三步查：连接是否就绪（`index.ts` 的重连策略）、schema 是否过了白名单、公共名是否被作用域层遮蔽。"图像没出现"则查准入链两道门：模型模态与会话 header。想理解命名契约，最好的办法是手动算一遍某个工具的公共名，再用它反查会话日志里的调用记录——你会看到重放为什么成立。给桥加功能时守住一条底线：任何新行为都不要引入"从公共名反解"的接口，那是最容易在不经意间凿穿的墙。再加一条运维直觉：工具"时有时无"通常是 re-sync 在起作用——服务器清单变了注册表就变，这是特性；想锁定行为就得锁定服务器端的工具版本。
