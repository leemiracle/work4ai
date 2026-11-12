# 01 · llmapi 服务入口：LLM/LLMArgs 与服务栈的第一公里

## 角色定位

`tensorrt_llm/llmapi/` 是用户面对的第一层：Python 批处理 API（`LLM`）、完整配置 schema（`llm_args.py` 7182 行，全仓最大 Python 文件）与模型装载（`llm_utils.py` 698 行）。上游由 `trtllm-serve` CLI（`tensorrt_llm/commands/serve.py:1331` 的 `serve()`）与 `serve/openai_server.py` 消费；下游把一切收敛到 PyTorch 执行器。配置面即产品面，是这层的直接写照。

## 内部结构

`llmapi/llm.py`（2073 行，wc -l 实证）是三层类塔：`BaseLLM`（llm.py:350，约 1450 行巨类）持有 generate 家族统一入口、usage 上报（`_start_usage_reporting` llm.py:511）与 logits processor 管理；`_TorchLLM`（llm.py:1804）是 PyTorch 后端实现，llm.py:1874 拉起 usage 上报；`LLM`（llm.py:2047）直接继承 `_TorchLLM` 成对外门面。同步 `generate` 在 llm.py:659，异步 `generate_async` 在 llm.py:764。两代 `_build_model` 分层：Base 侧 llm.py:1609 用 `CachedModelLoader` 取 HF 目录；Torch 侧 llm.py:1951 再装 tokenizer/HF/generation config 并经 `create_input_processor` 处理多模态词表（llm.py:1953 注释钉死顺序契约：下载→tokenizer→ExecutorConfig）。

`llm_args.py` 以 `StrictBaseModel`（utils.py:37，禁额外字段）为根：`BaseLlmArgs`（llm_args.py:4879）与 `TorchLlmArgs`（llm_args.py:5611）两大主干，中段是配置族博物馆——CUDA Graph 族（llm_args.py:164/294）、稀疏注意力五家（QSA llm_args.py:736 / MiniMaxM3 llm_args.py:858 / DeepSeek llm_args.py:1093 / DeepSeekV4 llm_args.py:1341）、`MoeConfig`（llm_args.py:1681）、`KvCacheConfig`（llm_args.py:4174）、统一 `speculative_config`（llm_args.py:5075，旧 eagle/mtp 字段 deprecated）。批量更新走 `update_llm_args_with_extra_dict`（llm_args.py:7031）。

## 外部连接

- **模型默认值三方协议**：模型类实现 `get_model_defaults(cls, llm_args)`（`_torch/models/modeling_utils.py:652`），由 `_torch/pyexecutor/model_loader.py:806-811` 调用并经 `apply_model_defaults_to_llm_args`（llm_utils.py:508）做三层深度合并（当前值→模型默认→用户覆盖）——"新模型零配置跑起来"的机制底座。
- **工具解析器**：`serve/tool_parser/` 15 个文件 **14 家注册类**（`tool_parser_factory.py:63-78` 实证：qwen3/qwen3_coder/kimi_k2/k3/deepseek_v3/v31/v32/v4/gemma4/glm4/glm47/minimax_m2/m3/poolside_v1；图谱摘要"15 家"按类数应为 14，`MODEL_TYPE_TO_TOOL_PARSER` 映射表则是 22 键，tool_parser_factory.py:21）。`resolve_auto_tool_parser`（tool_parser_factory.py:49）读 config.json 的 model_type 自动选型；`openai_server.py:241-246` 消费 `ToolParserFactory.parsers` 并汇总各解析器 `needs_compact_special_tokens` 能力。
- **web_search 五 provider**：`serve/web_search.py:376` 的 `_PROVIDERS` 注册 wikipedia/mojeek/brave/tavily/searxng（:346/:256/:276/:301/:326 各自搜索函数），默认 `off`，`TRTLLM_WEB_SEARCH` 显式开启——docstring 明言"启用必须是显式、可审计的决定"。Responses 侧 `responses_web_search.py:124` 把内置工具改写为模型可见的 `search(query)` 函数定义。
- **周边**：`mpi_session.py`（1154 行）管多进程编排；`serialization.py:147` 白名单 Unpickler 阻断 pickle 注入；`rlhf_utils.py:19` 的 `_preserve_cuda_graph_refit_caches` 修 Qwen3.5 权重热更新时 CUDA graph refit 地址漂移。

## 数据流

启动：`LLM(model, **kwargs)` → BaseLLM.__init__（llm.py:354）pop `executor_cls`、处理 env_overrides；llm.py:382-394 的 backend 分支**只认 'pytorch'**，其余 ValueError——TRT engine 后端已从这套 API 撤除；llm.py:400-402 `assert_backend_can_route`（modeling_v2 require 模式无 fallback）；llm.py:404-413 kwargs 白名单校验。随后 `_build_model` 装载、model_loader 套默认、构造 GenerationExecutor。请求：`generate_async` 产出流式 `RequestOutput`（llm.py:71，多重继承两个结果基类）；服务路径经 openai_server → tool_parser 流式增量解析 → 回填 tool_calls。

## 设计决策

1. **单后端收敛**：硬 raise+无 fallback 断言彻底消灭静默回退。
2. **禁令式防御合并**：llm_utils.py:521 禁止模型默认值携带 `cache_transceiver_config`——deep-merge 可能物化用户未开启的传输层配置，宁可拒绝。
3. **配置即 schema**：7182 行 pydantic 树换来类型检查与 golden manifest（`usage/llm_args_golden_manifest.json`，AGENTS.md 规定改字段必须重生成，API 签名受 api_stability 测试保护）。

## 新人提示

- 入口读码顺序：llm.py:354 → llm_args.py:5611 → llm_utils.py:508 → tool_parser_factory.py:62。
- 加配置字段只加在 TorchLlmArgs/子配置，跑 `scripts/generate_llm_args_golden_manifest.py`；加模型工具格式需实现 BaseToolParser 两套接口（整串 `extract_tool_calls`+流式 `on_tool_call_delta`，base_tool_parser.py:53），在 factory 注册并补映射表。
- 勘误：仓内文档说"15 家解析器"，源码注册表为 14 类——数文件（15 个 parser .py 含 base/core_types/utils 非注册类）易混淆。
