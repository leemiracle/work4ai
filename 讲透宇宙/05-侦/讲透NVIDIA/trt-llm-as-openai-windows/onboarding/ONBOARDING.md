# trt-llm-as-openai-windows ONBOARDING

> 仓库：NVIDIA/trt-llm-as-openai-windows @ 515434ef（merge PR#4 release/1.0）· 3 个 Python 文件共 829 行 + README/model 占位 · 图谱 23 节点 / 35 边 / 2 层 / 4 步
> MIT 协议（LICENSE.md，NVIDIA 2023）。行号锚全部源码实证。

## 1. 一句话定位

把 **TensorRT-LLM v0.6.1** 编译出的 Llama-2-13B / CodeLlama-13B（AWQ int4）引擎包一层 **OpenAI 兼容的 Flask REST API**，让 Windows 上跑 TRT-LLM 的模型能直接被 OpenAI 生态客户端消费（README.md:1-5）。它是"胶水示范仓"而非框架：没有 setup.py、没有包结构、根目录平铺三文件。

## 2. 文件地图（全部家当）

- **app.py**（217 行）：Flask 入口。argparse 收引擎路径/名称/tokenizer 目录（app.py:32-39）后实例化全局单例 `llm = TrtLlmAPI(...)`（app.py:75-85），注册四个路由：`/v1/models/Llama2`（app.py:88-97）、`/v1/models`（:100-114）、`/v1/chat/completions`（:117-171）、`/v1/completions`（:174-213）；末尾 `app.run(debug=True, threaded=False)`（:217）。
- **trt_llama_api.py**（481 行）：TRT-LLM 运行时封装。`LLMMetadata`（:144）与核心类 `TrtLlmAPI`（:158，pydantic BaseModel）——`__init__` 读引擎 config.json 解析 TP/PP/头数等构造 `ModelConfig`（:220-249）、加载 tokenizer（:260）、组 `SamplingConfig`（:261-264）、从 engine 文件读 buffer 建 `GenerationSession`（:266-273）；推理路径 `complete_common`（:313，非流式）与 `stream_complete_common`（:416，SSE 流式，生成器 `gen()` :434-479 逐 delta `yield 'data: {...}\n'`）；辅助 `parse_input`（:367，encode+去 padding）、`remove_extra_eos_ids`（:388）、`get_output`（:396）；响应体构造 `make_resData`（:75）/`make_resData_stream`（:111）。
- **utils.py**（131 行）：提示词模板。`MessageRole`（:64）/`ChatMessage`（:74）消息模型 + `messages_to_prompt`（:84，把 OpenAI messages 数组拼成 Llama2 `[INST]/<<SYS>>` 格式，BOS/EOS/B_INST 常量 :54-56，DEFAULT_SYSTEM_PROMPT :57-62）+ `completion_to_prompt`（:125）。
- **model/**：占位目录——`model/README.md` 仅 1 行"Place tokenizers and the model's config.json in this directory"，内含空 engine/ 子目录；真正引擎由用户按 README 先用 TRT-LLM `build.py` 编译（README.md:22-40，int4_awq/per_group 参数）再放入 model/engine。

## 3. 请求生命周期（数据流）

以 `POST /v1/chat/completions` 为例：Flask 进 handler（app.py:119）→ 断言 JSON Content-Type → 解析 stream/temperature（:124-127）→ 把 body["messages"] 逐条转 `ChatMessage`（role 映射 system/user/assistant/function 四种，:135-152）→ 无系统消息时注入 DEFAULT_SYSTEM_PROMPT（:154-156）→ `messages_to_prompt` 拼成单条 Llama2 提示词（utils.py:84-122，严格 user/assistant 交替假设，:97-100,117 两处 assert）→ `llm.complete_common(prompt, chat=True, ...)`（app.py:169）：encode 成 input_ids（trt_llama_api.py:367-386）→ `GenerationSession.setup/decode`（:328-333，beam=1 固定）→ `get_output` 切出输出段并洗掉多余 EOS（:396-408）→ `make_resData` 组 OpenAI 格式响应（choices/usage，:75-108）。流式路径走 `stream_complete_common`（:416）：`decode(streaming=True)` 返回增量迭代器，`gen()` 每个 delta 算 `output_txt[len(text):]` 差分后 yield SSE chunk（:454-467），stop_strings 在文本层逐条 `in` 检测（:469-472）。

## 4. 设计要点

- **TrtLlmAPI 复刻 llama_index LLM 协议**：字段结构（model_path/temperature/max_new_tokens/context_window/messages_to_prompt/completion_to_prompt/generate_kwargs/model_kwargs，trt_llama_api.py:159-179）与 `metadata` property（:298-305）、`chat_complete/complete/stream_chat_complete/stream_complete` 四入口（:307-314,410-414）都是 llama_index `LLM` 基类的形状——本仓前身即 llama_index 的 TRT 示例，utils.py 的模板函数与 llama_index 默认模板同源（NOTES-DIGEST 钉版）。
- **pydantic v1/v2 双兼容**：两个文件都 `try: from pydantic.v1 import ...` 回退裸 pydantic（utils.py:25-52，trt_llama_api.py:45-72）——requirements 钉 pydantic 2.3.0（requirements.txt:6）。
- **多来源拼装痕迹**：argparse 里混着 llama-cpp-python 风格的 `--host/--port/--max_output_tokens/--no_system_prompt`（app.py:44-49）；模型 id 硬编码 Llama2（:88-114）。
- **约束**：Python runtime 不支持流水并行（`assert pp_size == 1`，trt_llama_api.py:251）；引擎 world_size 必须等于运行时 MPI world size（:227-228）。

## 5. 快速上手（README 路线）

1. 装 TRT-LLM v0.6.1 Windows 版（README.md:9）；2. 从 HF 拉 Llama-2-13b-chat 或 CodeLlama-13b 权重 + NGC 拉 AWQ int4 checkpoint（:20-26）；3. 用 TRT-LLM examples/llama 的 build.py 编引擎（:31-40）；4. tokenizer+config.json 放 model/、引擎放 model/engine/（:48-53）；5. `pip install -r requirements.txt` 后 `python app.py --trt_engine_path ... --trt_engine_name ... --tokenizer_dir_path ...`（:55-60）；curl 验证（:62+）。

## 6. 边界与坑（8 条）

详见 README.md 勘误节：`type=bool` argparse 陷阱（app.py:49）；模型名三处不一致（app.py:92 vs trt_llama_api.py:81）；requirements 死依赖（flask-marshmallow/Flask-Migrate 全仓零引用）；非流式 stop_strings 是 TODO（trt_llama_api.py:317）；messages 交替强断言（utils.py:97-100）；prompts.txt 服务端落盘用户输入（app.py:197-203）；流式 delta/removesuffix 顺序易错（trt_llama_api.py:461-462）；`app.run(debug=True)` 生产风险（app.py:217）。

## 7. 与 TensorRT-LLM 主仓的关系

本仓只消费 `tensorrt_llm.runtime` 的四个对象：`ModelConfig`/`SamplingConfig`/`Mapping`/`GenerationSession`（trt_llama_api.py:31,269）——不依赖主仓 Python API 的其余部分；引擎构建完全在主仓完成。它相当于 v0.6.1 时代 Windows 部署的"最后一公里示例"，此后该职责由 TRT-LLM 自带的 OpenAI 兼容 Triton backend 取代。

## 8. 上手路线建议

通读顺序 app.py → utils.py → trt_llama_api.py（共 829 行，一小时可全读）。想改模型：全局搜 "Llama2"（app.py:92,107）与 EOS_TOKEN=2（trt_llama_api.py:39）三处硬编码。想换非 Llama 系模型：utils.py 的 [INST] 模板与 tokenizer 特殊 token 全部要换——本仓与模型家族强耦合，不是通用 OpenAI 层。
