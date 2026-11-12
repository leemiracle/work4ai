# llamafile/chatbot_* 精讲 — REPL 对话引擎：双后端、历史栈与 bestline

## 角色定位

chatbot 是 llamafile 的终端对话体验层，15 个 chatbot_*.cpp 按职责切分（无单一 chatbot.cpp）：`--chat` 直接加载模型跑 REPL，combined 模式以 HTTP 客户端连本地 server，`--cli` 复用同一管线做单次问答。推理细节被 `ChatBackend` 抽象隔离，REPL 只关心消息、渲染与历史。

## 内部结构

**后端抽象**（chatbot_backend.h）：`ChatBackend` 纯虚基类——`complete(messages, on_token)` 流式接口（回调返回 false 停止）、context_used/max、五个历史操作、两个能力探针。

- **DirectBackend**（chatbot_direct.cpp，`--chat`）：采样循环 `common_sampler_sample → eval_token → is_eog 终止`；think 类模型经 `common_chat_parse` 增量解析，切成 content/reasoning 两通道回调。
- **ApiBackend**（chatbot_api.cpp，combined）：解析 `http://host:port`，把 g_messages 序列化为 OpenAI JSON（内嵌 data:image URI 拆多模态 parts），POST `/v1/chat/completions` 走 SSE 流式。

**REPL 主循环**（chatbot_repl.cpp）：单次 SIGINT 语义（第一次打断生成，第二次退出——combined 模式刻意覆盖 server 的处理器，改由 REPL 退出时经 shutdown_fn 关停）；每轮 `record_undo → bestlineWithHistory(">>> ")` 读行；空行在 manual 模式轮换角色；`/命令` 交 chatbot_comm.cpp；渲染用 `ColorBleeder` 包裹 `HighlightMarkdown` 流式高亮，推理内容 FAINT 暗色打印。

**历史栈**（chatbot_hist.cpp）：`g_history` 全量 token 序列；`g_undo` 记交互前位置；`g_stack` 是 /push /pop 保存点。`rewind(pos)` = `llama_memory_seq_rm` 截断 KV cache + g_history.resize，零拷贝；/forget 在 seq_rm 后还要 `llama_memory_seq_add` 前移后续位置，再 `adjust_stacks` 重映射两栈。

**eval 层**（chatbot_eval.cpp）：`eval_tokens` 按 n_batch=256 分批 llama_decode；多模态 `eval_mtmd_chunks` 复用 server 同款 mtmd helper，显式跟踪 n_past（M-RoPE 的 n_pos≠n_tokens），图片以 IMAGE_PLACEHOLDER_TOKEN(-31337) 记账。

**其余**：chatbot_main.cpp 三入口 `main/api_main/cli_main` 服务三模式；bestline.c（4092 行 linenoise 分支）承担行编辑与历史。

## 外部连接

上游：llama.h/common（采样、chat 模板、mtmd）、bestline.h、highlight/。llamafile 侧：llamafile.h（FLAG_nologo/nothink、tokenize 包装）、main.cpp（三入口调用方与 shutdown_fn 提供方）。chatbot 是 highlight 库与图片解码链在终端侧的唯一消费者。

## 数据流

```
用户输入 ─bestlineWithHistory─▶ line
   ├─ /命令 ─▶ handle_command ─▶ on_* 分发（含 backend 历史操作）
   └─ 消息  ─▶ user_msg(/upload合并) ─▶ g_messages.push
        ├─ Direct: 套jinja模板 → eval → token进g_history+KV cache
        └─ Api:    OpenAI JSON → SSE流
        on_token(content_Δ, reasoning_Δ) ─▶ ColorBleeder 流式高亮打印
        assistant_content ─▶ g_messages.push / g_undo 记账
```
三栈记账：g_history 只在 eval 成功后追加；undo 记交互边界；栈位置随 erase 平移。

## 设计决策

1. **推理流与正文流分离渲染**：解析交给 llama.cpp chat 解析器（DEEPSEEK reasoning format），REPL 只做展示层着色。
2. **undo 用 token 位置而非消息快照**：任何前缀都可能被回退，位置+KV cache 截断最省内存。
3. **SIGINT 双击语义**：打断≠退出；关停权经 shutdown_fn 收回，避免一次 Ctrl+C 杀掉 combined 进程。
4. **manual 模式仅限 DirectBackend**：手工轮换角色需裸 eval 绕过模板，能力探针让 REPL 优雅拒绝。

## 新人提示

- 全局状态（g_ctx/g_model/g_messages 等）集中声明于 chatbot.h，api 模式下 g_model 为空——同时服务两后端的代码必须判空（is_base_model 已示范）。
- 改命令表三处同步：chatbot_comm.cpp 的 handle_command 链 + chatbot_help.cpp 帮助文本 + main.cpp 的 chat help。
- base 模型（无 chat_template 元数据）走 RAW COMPLETION：不套模板、消息历史不启用——测试选模型先看 is_base_model。
- bestline 是 vendored 代码，改它之前先确认需求不能用回调（hint/completion/history）满足。
