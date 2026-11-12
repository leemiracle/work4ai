# 02 · agent_runtime/tools.py — 13 个内置工具与注册表

> 源文件：`agent_runtime/tools.py`（407 行）。行号锚均从源码核实（commit fd4b72e7）。

## 1. 角色定位

如果说 loop.py 是 agent 的"脑循环"，tools.py 就是 agent 的"手"。这个文件做三件事：定义工具的**数据形状**（ToolSpec/ToolArgumentSchema）、实现**注册表**（ToolRegistry：名字解析、参数校验、schema 转换、分发执行）、以及装配 **13 个内置工具**（tools.py:390-404）——读写文件、glob、文本搜索、记忆、todo、看图、sleep、shell。ViMax 特有的三大管线工具不在此文件，由 vimax_adapters.py:45-97 构造 ToolSpec 后经 `build_builtin_registry` 的 `adapter_specs` 参数（tools.py:405-406）追加进来，与内置 13 件合成 agent 的完整工具面。

这个文件也是运行时的**安全边界**：`safe_path` 防路径逃逸（tools.py:192-196），`run_shell` 的环境变量闸门 + 危险命令黑名单（tools.py:362-370）。

## 2. 内部结构

**数据形状**（tools.py:17-37）：
- `ToolHandler` 类型别名（tools.py:17）：`Callable[..., Awaitable[ToolResult] | ToolResult]`——同步异步 handler 都收。
- `ToolArgumentSchema`（tools.py:21-26）：极简三字段（type/required/default），type 可以是类型元组（如 `(dict, list)`，tools.py:393）。
- `ToolSpec`（tools.py:28-37）：name/description/handler + 别名（aliases）、permission_mode（默认 "workspace-write"，view_image 标 "read-only"，tools.py:397）、json_schema 直通位、concurrency_safe 并发安全位（默认 False）。

**ToolRuntimeContext（tools.py:40-77）——handler 与运行时的通信线**。三个发射器：`emit_progress`（tools.py:49-59）把 `{type: "tool_progress", stage, message, metadata}` 塞给进度回调；`emit_terminal`（tools.py:61-69）转发子进程输出行；`is_cancelled`/`raise_if_cancelled`（tools.py:71-76）读 `cancel_event`（threading.Event，注意是**线程**原语——loop.py 的 TurnControl 在异步世界里用了线程事件做取消信号）。vimax_adapters.py 里的管线工具全靠 `emit_progress` 把分钟级渲染进度穿透到前端。

**ToolRegistry（tools.py:79-163）**，六个方法逐个看：
- `register`（tools.py:86-89）：登记主名 + 别名映射；`resolve_name`（tools.py:104-106）strip + 别名查表，旧名字/模型拼错的名字都能被 aliases 兜住。
- `list_tools`（tools.py:91-92）给提示词用；`list_function_tools`（tools.py:94-99）给 LLM 用——OpenAI function calling 格式，参数 schema 优先取 `json_schema` 直通位，否则由 `_argument_schema_to_json_schema`（tools.py:166-179）现场转换（`additionalProperties: False` 严格 object；required 判定是"required 且 default is None"，tools.py:174——适配器工具用 `required=True, default=""` 声明的参数实际是可选带默认值，刻意的语法糖）。
- `validate_arguments`（tools.py:108-135）：缺 required 补 default、类型检查前先做**宽容强转**——字符串 "true"/"false" 转 bool（tools.py:123-125）、数字字符串转 int（tools.py:126-131），给"模型把数字参数输出成字符串"留缓冲；类型不符返回可读错误而非抛异常。
- `partition_calls`（tools.py:141-148）：把连续的 concurrency_safe 调用聚成批——**但全仓 grep 无任何调用方**（loop.py:98 逐个串行执行），属"预埋未启用"的并发批处理基础设施。
- `execute`（tools.py:150-163）：`inspect.signature`（tools.py:157）探测 handler 是否收第二个参数（runtime context），按需单参/双参调用，`inspect.isawaitable`（tools.py:159）自动 await；一切异常吞成 `error_type: "exception"` 的 ToolResult（tools.py:162-163）——**工具异常永不击穿主循环**。

**13 个内置工具（tools.py:390-404）与各自的 handler 闭包**：

| 工具 | handler | 位置 | 要点 |
|---|---|---|---|
| read_file | read_file | :250-257 | UTF-8 读取；不存在时先问 `_legacy_virtual_read` |
| read_json | read_json | :259-270 | 解析失败报 invalid_json |
| write_json | write_json | :272-276 | 自动 mkdir 父目录；dict/list 皆可写 |
| list_files | list_files | :278-283 | 只列一层直接子项 |
| glob_files | glob_files | :285-288 | recursive glob，截断前 200 条（:288） |
| search_text | search_text | :290-307 | 纯 Python 子串扫描 + `path:line:` 输出，默认 max_results=100（:305） |
| view_image | ViewImageHandler | image_tools.py:17 | 唯一 read-only 权限工具，返回 model_content 图像块（image_tools.py:59-60） |
| memory_read / memory_write | :309-314 | :309 | 读写 .vimax/memory.md 用户偏好 |
| todo_read / todo_write | :319-350 | :319 | .vimax/todo.json；todo_write 逐项校验 content 非空 + status 三态（:340-345） |
| sleep | sleep_tool | :352-359 | 上限 300s（:354），异步等待 |
| run_shell | run_shell | :361-388 | 见下 |

**run_shell 的四层防御（tools.py:361-388）**：① 环境闸门——`VIMAX_ENABLE_RUN_SHELL != "1"` 直接拒（:362-363）；② 黑名单——`rm `/`sudo`/`chmod`/`curl `/`wget `/`ssh `/`printenv`/`env`/`export`/fork 炸弹 `:(){` 等 16 个 token 小写子串匹配（:367-370），连 env/export 都禁是为了堵**环境变量泄密**通道；③ 超时钳制 1-120s、输出钳制 1000-50000 字符（:365-366），超时 kill 进程（:376-379）；④ 全程 cwd 锁在 workspace root（:373）。成功与否以 `proc.returncode == 0` 判定（:388）。

**`_legacy_virtual_read`（tools.py:198-248）——幻觉路径的兜底别名层**，本文件最有趣的设计。docstring（:199-204）明说：会话真身在 `.vimax/sessions.json`、日志在 `.vimax/logs/*.jsonl`，但旧提示词/某些模型会幻觉出 `.working_dir/<session>/session.json`、`.vimax/logs/<session>.log` 这类"看起来该存在"的路径。read_file/read_json 找不到文件时不报错，而是来这里查询：命中 `session.json` 模式就从 SessionIndex 现场拼 payload 返回（:211-223，metadata 标 `virtual_path: True` 和真源）；命中 `.log` 模式就 grep 三类 JSONL 日志中含该 session_id 的行（:224-247）。**承认模型会幻觉，然后给幻觉一个正确的落点**——比在提示词里反复纠正更稳。

**safe_path（tools.py:192-196）**：`(root / raw).resolve()` 后检查 `root not in path.parents and path != root` 即抛"Path escapes workspace"。所有文件类工具共用这一道闸。注意 `root` 是 `Path(workspace_root).resolve()`（:189），符号链接被 resolve 展开后校验。

## 3. 外部连接

**依赖上游**：`.image_tools.ViewImageHandler`（tools.py:14，PIL 图片转 base64 data_url）；`.models.ToolCall/ToolResult`（:15）；标准库 asyncio/glob/inspect/json/os/subprocess。

**被依赖下游**：
- loop.py:15 `from .tools import ToolRegistry, build_builtin_registry`——主循环拿 `list_function_tools` 喂 LLM、拿 registry 间接经 ToolExecutor 执行；
- tool_executor.py:9 引 ToolRegistry/ToolRuntimeContext——执行前调 `validate_arguments`（tool_executor.py:34）与 `resolve_name`（:31）；
- vimax_adapters.py:34 引 ToolArgumentSchema/ToolRuntimeContext/ToolSpec 构造三大管线工具，:48/:68/:84 三个 ToolSpec 实例；
- 测试直接消费：tests/test_agent_loop.py:14（含 slow_tool/view_image 假 handler，:63/:84/:163）、tests/test_robustness.py:22。

## 4. 数据流：模型一次 view_image 调用穿过本文件

1. 模型输出 `{"name": "view_image", "arguments": {"path": "novel2video/frames/kf_001.png"}}`。
2. loop.py 拿到 tool_calls → tool_executor.execute → `registry.resolve_name("view_image")`（无别名，原样返回）→ `validate_arguments` 校验 path 是 str 且必填（tools.py:397 的 schema）→ 通过。
3. `registry.execute`（tools.py:150）取 spec.handler=ViewImageHandler 实例，`inspect.signature` 探测到 `__call__(self, args)` 只收一个参数（runtime 感知失败是预期——view_image 不需要进度），同步调用。
4. ViewImageHandler（image_tools.py:17-60）：`get_or_create_active()` 拿活动会话 → path 解析到会话 working_dir 下 → PIL 打开、按 `VIMAX_IMAGE_VIEW_MAX_DIMENSION`（默认 1568，image_tools.py:29）压缩 → base64 data_url → 返回带 `model_content=[{type:"image_url",...}]` 的 ToolResult（image_tools.py:59-60）。
5. 回到 loop.py:119-120：`model_content` 被收集，工具轮结束后以"图像观测"user 消息注入 runtime_messages（loop.py:121-133），下一轮采样时模型真的"看"到这张关键帧——多候选举优（VLM 选图）的基础。
6. ToolExecutor 同时把参数预览、结果预览、耗时写进 `.vimax/logs/tool_calls.jsonl`（tool_executor.py:45）。

## 5. 设计决策

- **声明式微 schema 而非 pydantic 模型**：ToolArgumentSchema 只有三个字段，`_argument_schema_to_json_schema` 一遍转成 OpenAI 格式。轻，但代价是没有嵌套类型描述——需要复杂 schema 的工具（如适配器的结构化参数）只能描述成扁平 str 参数，让 agent 在 handler 内部再解析。
- **同步/异步 handler 双态兼容**（tools.py:157-161）：内置 11 个同步 + sleep/run_shell 两个异步共存一个接口；inspect 探测参数个数则免掉每个 handler 都写 `runtime=None` 占位参数。
- **run_shell 默认禁用是产品决策不是缺陷**：agent 有文件读写就够了，shell 是逃生舱。ONBOARDING §6 也钉版了这一点。
- **虚拟读层选择"别名"而非"改提示词"**：模型幻觉路径是概率现象，堵提示词永远堵不完；在工具层给幻觉路径一个真实数据源，鲁棒且零 token 成本。
- **异常全部就地消化**（tools.py:162-163）：单工具失败变成一条失败的 ToolResult 回填给模型，模型可以自我纠正（换路径/改参数）重试；这是 agent 循环能长跑 50 轮的前提。
- **partition_calls 的"预埋"**：并发批处理逻辑写好了但没接线——loop.py 保持串行。读代码时别误以为工具是并发执行的；concurrency_safe=True 目前只影响 schema 无行为（若未来接线，write_json 等写工具天然在非并发批里）。

## 6. 新人提示

- **加新内置工具的三步**：写 handler 闭包（在 build_builtin_registry 内，能吃到 root/session_index 闭包变量）→ 在 specs 列表（tools.py:390-404）加 ToolSpec（标 concurrency_safe 前先想清楚是否有写副作用）→ 不需要改 loop.py，schema 自动进 LLM 工具面。
- **别绕过 safe_path**：任何新文件类工具都必须走 `(root / raw).resolve()` + parents 校验这一套，直接 open(args["path"]) 会打开沙箱缺口。
- run_shell 黑名单是**子串**匹配（tools.py:369 `token in lowered`）："dd " 带尾空格会漏掉 "dd"（无参数无意义，可接受），但也会误伤包含 "env" 的正常词（如 "environment" 会被拒——`"env"` 是裸 token，`"environment"` 含 `env` 子串，确实会命中）。给模型写提示词时避免让 run_shell 跑含这些子串的命令。
- `validate_arguments` 只处理 schema 里**声明过**的字段，多余字段原样透传（`additionalProperties: False` 只出现在给 LLM 看的 JSON schema 里，运行时不删多余键）——handler 要自己防御未知参数。
- todo_write 是**整表替换**不是增量更新（tools.py:332-350），模型每次要传全量 items；提示词里要写清这一点，否则模型会以为在追加。
- memory_write 同理是整文件替换 .vimax/memory.md（tools.py:312-314），且描述里限定"user preference notes only"——存任务状态请走 todo，别塞 memory。
- 改 13 这个数字时要同步改两处文档性锚点：ONBOARDING §4 与 vimax 分发器提示词对工具数的描述；grep "13" 确认。
- glob_files 截断 200 条（tools.py:288）、search_text 默认 100 条（:305）——大目录下模型可能"看不到"部分结果，属预期截断而非 bug。
