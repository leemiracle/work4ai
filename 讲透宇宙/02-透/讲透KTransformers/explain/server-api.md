# server/main.py + api/openai/endpoints/chat.py：OpenAI 兼容 API 服务层主文件

> `server/api.py` 磁盘不存在（实为 `api/` 目录），精讲两个真主文件：`server/main.py`（183 行，FastAPI 装配）与 `api/openai/endpoints/chat.py`（508 行，核心端点）。图谱（31985f4）均属 `layer:api-service`（86 节点）。

## 1. 角色定位

main.py 是**服务装配器**：命令行解析→后端创建→FastAPI 组装→uvicorn 启动，外加 NPU 多进程 TP 编队。chat.py 是**协议翻译器**：把 OpenAI 协议译成对 `interface.inference()` 异步生成器的消费，反向把模型 token 流（含 DeepSeek tool call 标记文法）译回 OpenAI 格式。两者之间是 `create_interface.py` 工厂、`backend/base.py` 契约与 `backend/interfaces/` 四实现。

## 2. 内部结构

**main.py**：`main()`（L127）→`create_app()`（L37，可挂 `lifespan`、加全开 CORS）→`mount_app_routes()`（L29，建表+挂路由）→`mount_index_routes()`（L69，`website/dist` 挂 `/web`）→`run_api()`（L83）；`verify_arg()`（L111）限 NPU 参数域。路由聚合在 `api/__init__.py`，openai 侧以 `prefix='/v1'` 挂载。

**chat.py** 四块：①自带 Pydantic 模型（`Choice` L22 等），L19 挑明不 import OpenAI 包；②`getTools()`（L61）解析 DeepSeek `<｜tool▁calls▁begin｜>` 系标记文法，提取函数名与 json 参数；③`get_tool_instructions()`（L117）注入工具提示模板；④`chat_completion()`（L135-509）——逐项校验参数（temperature L163、top_p L173、penalty L183，违规回 400）→改写消息注入工具描述（L209/L220）→流式/非流式两分支。

## 3. 外部连接

chat.py 出边 `imports`：`schemas/endpoints/chat.py`（请求/块/用量 schema，含 prefill/decode 计时与 `return_speed` L78）、`schemas/assistants/streaming.py`、`backend/base.py`、`utils/create_interface.py`。后端选型在 `create_interface()`（L19）：按 `config.backend_type` 四选一塞进单例 `GlobalInterface.interface`——chat.py 的 `get_interface()`（L230）取的正是它。

## 4. 数据流

`POST /v1/chat/completions`（流式）：启动期 `main()` L145 `create_interface()` 装配后端（L99 `optimize_and_load_gguf`）→`chat_completion()` 调 `interface.inference(...)`（L266）→KTransformersInterface.inference（L410）持 `_infer_lock` 串行化，委托 TransformersInterface 逐 token yield `(token, finish_reason)`，收尾 yield `RawUsage`（tokenize/prefill/decode 计时）→`inner()` 消费：token 先归一化（L285）；嗅探 begin 标记（L287）则截断已积累正文先冲 chunk（L299），命中 end 后 `getTools()` 解析，连发 tool_calls 事件（L330-370）后 return；普通路径逐 token delta，buffer 200 字符滑窗（L313）→出口 L414 `chat_stream_response` 四层包装：过滤、DONE、SSE 帧、**断连检测**。

## 5. 设计决策

- **自建 schema 不 import openai 包**：免依赖锁版本，且塞 `prefill_time/decode_time` 把分速暴露成 API。
- **tool call 走文法嗅探而非 logit 级控制**：双层兜底（归一化映射+滑窗），不动内核即给任意模型补 function calling；代价是跨 chunk 标记判断脆，失败降级为正文（L376）。
- **单例 interface+`_infer_lock`**：一次一请求，简单换吞吐；批处理分流 `BalanceServeInterface`。
- 毛边：TP>1 非 rank0 死循环空转保进程组（L160）；api_key 用 `assert`（L233）；重复 import。

## 6. 新人提示

- 切入顺序：`schemas/endpoints/chat.py`（协议）→非流式分支（L415-509，无状态机干扰）→流式→`interfaces/transformers.py::inference`。
- 易错点：①改工具标记须同步 `getTools`/`get_tool_instructions`/`too_calls_dict`/流式四处副本；②非流式 usage 在 `locals()` 试探（L505）；③NPU 先看 `verify_arg`。
- 测试：`tests/function_call_test.py`、`local_chat_test.py`；api-service 层其余节点（assistants/crud/schemas）是卫星件。
