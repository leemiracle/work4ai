# KernelMem agents/query_server.py + llm_local.py 深解：LLM 后端统一接口

> 对象：`agents/query_server.py`（354 行）与 `agents/llm_local.py`（131 行）。图谱定位：layer「LLM 后端接口层」——"封装本地推理与查询服务式的大模型调用接口（query_server→llm_local），为生成与裁判环节提供统一推理通道"。

## ① 角色定位：把"用哪个模型"与"怎么跑进化"解耦

KernelMem 的进化主循环（main_memory_latest.py，1800+ 行）里所有需要 LLM 的环节——生成种子 kernel、瓶颈判定、编译失败修复、优化提议、裁判打分——都汇到同一个函数 `query_server()`。它是一个**多后端路由器**：吃统一的 prompt + 采样参数 + `server_type` 字符串，吐统一的文本回复，内部再分派到 10 种后端（本地 vLLM、sglang、OpenAI-Azure、DeepSeek、Fireworks、Anthropic、Google、Together、SambaNova、legacy local）。`llm_local.py` 则是其本地分支的实现：一个 vLLM OpenAI 兼容客户端的薄封装。价值在于：换模型供应商时主循环零改动，只需改 CLI 的 `--server_type/--model_name`。

## ② 内部结构

### query_server.py：三分件 + 主函数

- **模块级密钥区（L7-17）**：启动即读 8 个环境变量（TOGETHER/DEEPSEEK/AZURE_OPENAI/GEMINI/SGLANG/ANTHROPIC/SAMBANOVA/FIREWORKS）及 Azure 的 endpoint/deployment_name。
- **`retry_with_backoff`（L22-57）**：指数退避重试器，1s 起步、×2 增长、封顶 300s；`max_retries=None` 默认**无限重试**；可重试异常限定 OpenAI 的 `APIConnectionError/APITimeoutError/RateLimitError` 三类（与 llm_local 的副本唯一差异：本版支持注入自定义异常元组）。
- **`colorize_finish_reason`（L60-77）**：finish_reason→ANSI 颜色映射（stop 绿 / length 黄 / content_filter 红 / tool_calls 蓝 / 未知灰），终端一眼识别截断。
- **`query_server`（L79-354）主函数**，`match/case` 十分支建客户端后走四条执行路径：
  1. **local/vllm 路径**：仅接受 str prompt，经 `llm_local.get_llm()` 拿 LLM 实例调 `chat()`（vllm 会把 server_url 指向 `http://{addr}:{port}/v1`；local 是 legacy 直连默认 localhost:8000）。
  2. **google 路径**：`genai.GenerativeModel` + system_instruction，返回 `response.text`。
  3. **anthropic 路径**：reasoning 模型走 `beta.messages.create` + `thinking budget_tokens` + 128k beta 头；普通模型走标准 messages API 带采样参数。
  4. **通用 OpenAI 兼容路径**（sglang/deepseek/fireworks/together/sambanova/openai）：`chat.completions.create`；当 `server_type=="openai"` 且 `is_reasoning_model` 时改注入 `reasoning_effort` 且**不传采样参数**。

  各云路径末尾都有同构的 usage 记账块：把 In/Out/Total tokens 连同 timestamp/round_idx/call_type 追加写入 CSV（log_path 提供 时）。

### llm_local.py：本地推理路径

`GenerationConfig` dataclass（max_new_tokens/temperature/top_p/top_k/repetition_penalty/seed/stream，默认偏保守：temp 0.2、top_p 0.9）；`LLM` 类以 dummy `api_key="EMPTY"` 连 vLLM 的 OpenAI 兼容端点，`chat()` 拼 system+user 消息走 chat 接口，遇 MPT/deepseek-coder 等非对话模型自动回退 `generate()`（拼纯文本走 completions 接口），两者均套自带的重试器；`get_llm()` 用 `lru_cache(maxsize=2)` 复用客户端实例。

## ③ 外部连接：一个调用方，八种角色

图谱 calls 边唯一指向 `main_memory_latest.py:_make_llm_caller`（L149-176）：它把 argparse 参数闭包成 `call_llm(prompt, sys_prompt, log_path, call_type, round_idx)`，list 结果压成 `res[0]`。该闭包在主循环中被 8 处调用，`call_type` 标注调用角色：**seed**（种子生成）、**problem_identify**（瓶颈判定）、**repair / compilation_timeout_*_analysis/_repair**（编译失败修复）、**judge_optimization**（裁判打分，L1413）、**optimization**（主优化步）。即**主循环与 judger 走同一入口**，仅靠 call_type 在记账 CSV 里区分。注意 main 的 `--server_type` 默认值是 `openai`（Azure），而函数签名默认 `sglang`——实际生效的是前者。query_server 自身还 import 了 `utils.print_utils.print_bold`（未使用的死导入）与 llm_local 的 `get_llm/GenerationConfig`。

## ④ 数据流：messages→API→文本回收

入参 `prompt: str | list[dict]`。本地路径强断言 str。云端 OpenAI 系：**str 则包装成 `[system, user]` 两条消息；list[dict] 则原样直通**——这意味着多轮对话历史可由调用方预组装好直接传入。响应回收阶段：逐 choice 打印彩色 finish_reason（`length` 时警告截断）、收集 `message.content`、usage 记账，最终 `outputs[0] if len(outputs)==1 else outputs`（仅通用路径的 `n=num_completions` 会产生多候选）。anthropic 路径逐 block 取 `.text`，非文本 block（如 thinking 块）打印 "Skipping" 后丢弃。**重要边界：query_server 不做任何 JSON 解析或围栏剥离**——```json 清洗是上游的责任（如 judge_gate 的特征提取侧）；它只保证"文本收齐 + 截断可见 + 用量入账"。

## ⑤ 设计决策与新人提示

1. **单入口换后端零成本**是核心收益，但代价是 350 行里三份复制粘贴的记账代码（google/anthropic/openai 系各一份）——改 CSV 格式需同步三处。
2. **返回契约不对称**：local/vllm/google 三路直接返回 str，通用路径按候选数返回 str 或 list（且 `num_completions` 只在通用路径经 `n` 参数生效，google/anthropic 压根没接）；上层 `_make_llm_caller` 用 `res[0]` 统一压平，所以这个不对称从未暴露——但绕过 call_llm 直接调 query_server 的人要自己兜。
2. **重试语义双轨甚至三轨**：sglang 设 `max_retries=0` 全靠外层无限重试；deepseek/fireworks 设 SDK 内建 `max_retries=3` 又被外层 retry_with_backoff 再包一层（实际重试次数被放大）；默认无限重试 + `timeout=10000000`（≈115 天）意味着**长跑实验可能静默挂在单次调用上**，排障先看终端的 "unlimited retries" 提示。
3. **Azure 坑**：`server_type="openai"` 时传入的 model_name 被忽略，实际用环境变量 `DEPLOYMENT_NAME`——换了模型名没生效先查这里。
4. **reasoning 模型参数受限**：openai+reasoning 走 `reasoning_effort` 不传采样参数；anthropic reasoning 需显式给 `budget_tokens`，否则 thinking 不开。
5. llm_local 的 `GenerationConfig.repetition_penalty` 与 `top_k` 声明了但**没传进 API**（静默失效，注释自认"仅为兼容保留"）；文件 docstring 还叫 `llm_vllm.py`（历史名）。
6. 本地起服务时注意端口约定：llm_local 默认 8000，sglang 默认 30000；`match/case` 语法要求 Python ≥3.10。
7. **排障路线**：先看终端彩色 finish_reason（黄=截断需调大 max_tokens，红=内容过滤）与 Usage 行；再查 usage CSV（按 call_type/round_idx 可复盘哪一环节烧了预算）；最后确认环境变量齐全——密钥全部模块级读取，进程启动后才 export 的 key 不生效。
