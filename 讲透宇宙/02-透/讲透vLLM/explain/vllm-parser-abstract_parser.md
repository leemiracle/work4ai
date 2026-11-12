# vllm/parser/abstract_parser.py — Parser 统一门面：命令式双 parser 到声明式引擎的迁移枢纽

> 源码：`vllm/parser/abstract_parser.py`（1051 行）｜vllm/parser/ 包 45 个 py（engine/ 9 件）｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

`abstract_parser.py` 是 vLLM **模型输出解析层的统一门面**：`Parser` 基类（vllm/parser/abstract_parser.py:108）把过去两套独立体系——`vllm/reasoning/` 的 ReasoningParser 与 `vllm/tool_parsers/` 的 ToolParser——收编为"serving 层每请求一个对象、只调一组方法"的单一抽象。docstring（:111）钉死：`ParserEngine` 用单个声明式引擎实现全部成员，`DelegatingParser`（:344）组合一对 legacy parser。这是解析栈的形态级迁移：老代"每厂商一个手写正则 parser"（注册表 57 个名字，vllm/tool_parsers/__init__.py:24）正被 engine/ 声明式引擎逐个替代——已挂 11 个 `*_engine_tool_parser.py` 薄壳，vllm/tool_parsers/deepseekv32_engine_tool_parser.py:4 整个文件只有一行类声明，用户敲 `--tool-call-parser deepseek_v32` 拿到的已是新引擎。

## ② 内部结构

文件四段：**StreamState**（:66-105）、**Parser 抽象基类**（:108-278）、**结构化输出→xgrammar 映射**（:281-341）、**DelegatingParser**（:344-1051）。

`StreamState`（:66）是每流一份的可变状态：reasoning 是否结束、kimi_k2 历史调用计数（:75）、`engine_based` 标志（:81）。`advance`/`commit`（:83/:95）双模分流：legacy 模式全量拼接 previous_text，engine 模式引擎自缓冲、门面只透传 delta——新旧两代共存于同一门面的关键开关。

`Parser` 基类靠**类属性注入**组合子 parser：`reasoning_parser_cls`/`tool_parser_cls`（:119-120）由子类或 ParserManager 动态绑定；`__init__`（:126）对 `ParserEngineToolAdapter` 子类走带 `model_config` 的新式构造（:145-150）。`_engine_based`（:152）当两侧都支持 engine 流式时置真；若无 reasoning parser 则设 `skip_reasoning_parsing`（:156-166）——reasoning 标记此时是普通文本须原样放行。三个抽象方法 `is_reasoning_end`（:226）/`parse`（:241）/`parse_delta`（:262）是 serving 层可见的全部协议。

`DelegatingParser` 是 700 行编排器。非流式 `parse`（:841）= extract_reasoning（:357）→`_extract_tool_calls`（:391），后者按 tool_choice 四分支（none/required/named/auto）处理，required 分支用 pydantic `TypeAdapter` 验证整段 JSON（:440）。`_apply_structural_tag`（:503）把工具约束编译成 `StructuralTag` 写回 `request.structured_outputs`（:601-608），交结构化输出引擎在采样期硬约束。流式 `parse_delta`（:857）是两阶段状态机：reasoning 阶段（:889-936）靠 prompt 预检（:869）定起点，迁移时机 legacy 走 token 扫描、engine 走 `has_engine_confirmed_reasoning_end()`（:899-906）；tool 阶段（:939-978）进入时清空 previous_text 重整增量（:940-945）。收尾 `finalize_generation`（:819）补捞未流式化参数，`_flush_engine_parsers`（:1015）冲刷 engine 缓冲（:1028 特意跳过已迁移后的 reasoning 冲刷防漏杂字符）。

## ③ 外部连接

- **依赖**：被组合的旧双轨 `vllm/tool_parsers/`（streaming 三件套 :52-55）与 `vllm/reasoning/`；新轨 engine/——适配器 vllm/parser/engine/adapters.py（`ParserEngineToolAdapter`:165）、声明式配置 parser_engine_config.py（`ParserEngineConfig`:60，terminals/transitions/content_events :72/:76/:80，`ParserState` 八态 :37）、引擎 parser_engine.py（`ParserEngine`:111）+streaming_parser_engine.py（:90）+词法双件 incremental_lexer.py（`IncrementalLexer`:82）/token_id_scanner.py（`TokenIDScanner`:31）；xgrammar（:12-22）承担约束编译。
- **被依赖**：`ParserManager`（vllm/parser/parser_manager.py:20）`get_parser`（:98）→`_compose_parser`（:152）运行期 `type()` 动态拼 `_Parser(DelegatingParser)`（:264-274）；两条 serving 线启动期取类（vllm/entrypoints/openai/chat_completion/serving.py:166、vllm/entrypoints/openai/responses/serving.py:141）。18 个引擎 parser 经 registered_adapters.py:31-124 的 `make_adapters`（vllm/parser/engine/adapters.py:247）双注册回旧两张注册表，**引擎由此反向流入旧世界**。

## ④ 数据流

```
启动：vllm/entrypoints/openai/chat_completion/serving.py:166 ParserManager.get_parser(...)
  → _compose_parser: harmony/response_template/kimi_k3/cohere/minicpmv 特判
    （parser_manager.py:179/:187/:222/:235/:251）→ 通用 _Parser(DelegatingParser)
每请求：parser_cls(tokenizer, tools, model_config)
  非流式：parse() @:841 → (reasoning, content, tool_calls)
  流式：parse_delta() @:857 每 delta
    → prompt 预检 @:869（prompt 已过 </think> 则直入 tool 阶段）
    → reasoning 阶段 @:889（engine 结束迁移走 finish_streaming 冲刷 @:914）
    → tool 阶段 @:939（kimi_k2 计数自增 @:976）
    → finished → finalize @:819 + flush @:1015 → DeltaMessage（reasoning 抑制 @:999）
反向：adjust_request @:493 → _apply_structural_tag @:503 → 采样期硬约束
```

## ⑤ 设计决策

1. **门面先行、双轨收敛**：AGENTS.md（vllm/parser/AGENTS.md）钉版"新格式别再用 DelegatingParser"——它存在的唯一意义是让 57 个 legacy 名字零改动流进新门面；新格式一律 `ParserEngine`+声明式 config（vllm/parser/deepseek_v4.py:146 用 `@functools.cache` 缓存转移表，production 拼写变体收在 :54-57）。
2. **一次状态机同时抽 reasoning 与 tool call**：旧架构 `</think>` 后紧跟 `<tool_call>` 的跨界文本要两套 parser 各自猜边界，新引擎一个转移表管到底。`DelegatingParser.parse_delta` 在 :907-936 用大量手工缝合复刻同等语义——这段复杂度正是引擎要消灭的对象。
3. **token_id_terminals 是硬规则**：特殊 token 到达引擎时是 token id 不是文本，流式下文本终端横跨特殊 token 永远匹配不上（AGENTS.md 明示）；`ParserEngineConfig` 为此单设该字段（parser_engine_config.py:74）。
4. **py/rust 双栈为镜像而非调用链**：rust/src/parser/ 是独立 crate `vllm-parser`（90 个 rs：unified/、tool/、reasoning/ 等），消费方是 rust 前端 chat crate（rust/src/chat/Cargo.toml:38，rust/src/chat/src/output/default/unified.rs:20 驱动流式解析）；**无 pyo3 绑定、Python 侧零引用**——两栈平行实现，rust 侧 rust/src/parser/src/unified/kimi_k3.rs:6 注释明言"Original Python implementations"移植自 vllm/reasoning/ 与 vllm/tool_parsers/。情报"py/rust 双栈"属实，方向是 py 为源、rust 为 rust 前端专属镜像。
5. **测量埋点进 finally**（:650-655）：`record_tool_parser_invocation` 连异常路径也计数（vllm/parser/metrics.py），支撑解析成功率观测。

## ⑥ 新人提示

- 读法：先 :108-170（基类组合）→ :857-1007（parse_delta 状态机）→ 再跳 parser_engine_config.py 看 `ParserEngineConfig` 字段注释（arg_value_extender 的 prefix-safe JSON 协议 :109-119 讲透流式 JSON 增量合法性难点）。
- 加新 parser 三步：抄 glm47_moe.py 模板写 config → `make_adapters` 挂进 registered_adapters.py → 补 `*_engine_tool_parser.py` 薄壳挂回旧注册表。
- 改 engine/ 或 abstract_parser.py 的门槛被 AGENTS.md 钉死："对所有 parser 都是错的"才能动公共层，模型 quirk 收在各自 `<model>.py`。
- 调试流式丢字：先看 `engine_based`（:81）走哪条 advance/commit 分支，再看 :940-945 首 delta 重整——新旧模式边界行为不同，历史 bug 高发区。
