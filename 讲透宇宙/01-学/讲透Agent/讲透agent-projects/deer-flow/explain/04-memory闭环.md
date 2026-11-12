# 04 · memory 闭环：中间件→防抖队列→LLM 增量摘要→prompt 注入

## 角色定位

`agents/memory/` 四文件实现"全局用户记忆"：跨线程、跨会话的用户画像（六节摘要 + 离散事实），存 `backend/.deer-flow/memory.json`，经系统提示词注入影响后续所有对话。闭环四段：MemoryMiddleware（链上第 8 环，采集）→ MemoryUpdateQueue（30s 防抖，缓冲）→ MemoryUpdater（LLM 增量合并，加工）→ `_get_memory_context`（装配期注入）。另有一套 per-agent 记忆（`agent_name` 键控独立文件）与全局记忆并行，代码同路。

## 内部结构

**采集端 MemoryMiddleware**（memory_middleware.py:86）：`after_agent` 钩子（:108）在每轮 agent 结束后过滤消息——`_filter_messages_for_memory`（:20）只留人类消息与**无 tool_calls 的最终 AI 回复**（:74-80），中间工具往返全部丢弃。上传清洗是三级设计：剥离 `<uploaded_files>` 块（正则 :43），剥后为空则整轮跳过并置 `skip_next_ai` 连带跳过配对的 AI 回复（:58-62），剥后有问题则用 `copy(msg)` 重建干净消息（:65-69）。门槛校验：无 thread_id 或无消息直接跳（:123-132），过滤后必须同时有用户消息与 AI 回复才入队（:142-143），最后 `queue.add(thread_id, messages, agent_name)`（:146-147）。

**缓冲端 MemoryUpdateQueue**（queue.py:22）：threading.Lock + 守护 Timer 的防抖队列。`add` 里同 thread 待处理项**新替旧**（queue.py:58——一晚连续聊 N 轮，只有最后一次全量重进队列）；每次 add 都 `_reset_timer` 重置计时器（:62），Timer 线程 daemon=True 随进程退出（:79）。`_process_queue`（:84）在 Timer 到点后执行：函数体内延迟 import MemoryUpdater 规避循环依赖（:87，注释明示）；重入保护用 `_processing` 标志而非锁内执行（:90-93）——处理期间新到请求会重置计时器重新调度而非阻塞；处理时整批 swap 出队列（:99-101），逐条调 updater，多任务间 sleep 0.5s 防 LLM 限流（:124-125）。单例经 `get_memory_queue`（:173）双检锁提供，`flush`（:131）供测试与优雅停机强刷。

**加工端 MemoryUpdater**（updater.py:218）：`update_memory`（:235）流程——`get_memory_data` 读现记忆 → `format_conversation_for_update` 格式化对话 → MEMORY_UPDATE_PROMPT 组装 → `model.invoke` 同步调用 LLM（:271，模型每次重建不缓存、thinking 恒关 :229-233）→ 剥 markdown 围栏再 `json.loads`（:276-280）→ `_apply_updates` → 上传语句三级清洗（:289）→ 原子落盘。`_apply_updates`（:301）按 LLM 的 `shouldUpdate` 标志整节替换 user 三节（workContext/personalContext/topOfMind，:322-328）与 history 三节（recentMonths/earlierContext/longTermBackground，:331-338）；事实操作两条：factsToRemove 按 id 删（:341-343）、newFacts 过置信度阈值（config 默认 0.7，:348-349）后以 `fact_{uuid4 前 8 位}` 落账（:351）；超 max_facts（默认 100）按置信度降序截断（:361-367）。**上传三级清洗**的第三级在保存前：`_strip_upload_mentions_from_memory`（:153）用句边界正则（:142-150，匹配 upload/file document/`/mnt/user-data/uploads/`/`<uploaded_files>` 整句）从摘要与事实中删句——设计权衡在注释与正则里都写明：只删"上传事件句"、保留"用户处理 CSV 文件"这类长期事实（updater.py:139-141）。IO 安全：模块级 `_memory_cache` 按 agent_name 键控 (data, mtime) 写穿透缓存（:61），读时 mtime 变了自动失效（:87）；写走 `.tmp` + `replace` 原子替换（:196-201）。

**注入端**（memory/prompt.py + lead_agent/prompt.py:285）：`_get_memory_context` 在每次装配 agent 时延迟 import（prompt.py:295）读记忆，`format_memory_for_injection`（prompt.py:186）格式化，`max_tokens=config.max_injection_tokens`（默认 2000，config.example.yaml:389）装箱，包 `<memory>` 标签进系统提示词（prompt.py:308-310）。token 计数 tiktoken 可选、缺失降级 `len//4` 估算（prompt.py:158-160）。**装箱算法是两段式增量**（prompt.py:254-281）：基础段落（User Context + History）只编码一次，Facts 节先按置信度排序（:240-250）再逐行增量计数（首行无换行符 :274），超预算即停（:277-281），避免每加一条就全串重编码的 O(n²)。兜底：总串仍超限时按字符/token 比例砍到 95%（:292-298）。NaN/inf 置信度会被 `_coerce_confidence` 钳回 [0,1]（:170-183），防 LLM 输出脏值主导排序。

## 外部连接

上游：MemoryMiddleware 是 lead 链必选环（agent.py:234 装配，位于 Title 之后）；Queue 是进程级单例，LangGraph Server 与 Gateway 两个进程各自一份。下游：注入发生在 `make_lead_agent`→`apply_prompt_template`→`_get_memory_context`，Gateway 的 `/api/memory` 四端点与 DeerFlowClient 的 get/reload 方法共享 `get_memory_data/reload_memory_data`。配置面（config.example.yaml:382-389）：enabled/injection_enabled 双总闸、storage_path 相对 backend 目录、debounce_seconds=30、model_name=null 走默认模型、max_facts=100、fact_confidence_threshold=0.7、max_injection_tokens=2000。

## 数据流

一轮对话的记忆流水线：after_agent 触发 → 三级过滤（工具消息弃、上传块剥、空轮连带跳）→ 队列新替旧 → 30s 计时器（每轮重置，用户还在聊就一直推迟）→ 到点批量 swap → 逐线程 LLM 增量合并（现记忆全量进 prompt，LLM 返回六节 shouldUpdate + newFacts/factsToRemove）→ 置信度过滤/截断 → 上传句正则清洗 → tmp+replace 原子写 → 缓存更新 → 下一轮装配时 mtime 校验读新 → tiktoken 装箱 top 事实注入 `<memory>`。注意更新是**滞后一轮**的：本轮对话不会立刻影响本轮行为。

## 设计决策

1. **防抖而非即时**：记忆写是慢操作（LLM 调用），30s 窗口合并连续对话，代价是进程崩溃丢最后窗口——daemon Timer 不持久化，属可接受的最终一致。
2. **全量进 prompt 增量返回**：LLM 看到完整现记忆 + 新对话，自己决定哪些节 shouldUpdate——避免 diff 算法，把合并智能外包给模型；代价是记忆膨胀后 prompt 成本线性涨。
3. **上传信息三道防线**（中间件剥离/格式化跳空轮/保存前句删除）：同一诉求（会话态文件不该进长期记忆）在三个时间点各设一道，防御纵深而非单点信任 LLM 的 prompt 规则（prompt.py:113-115 也写了规则，但代码不信任它）。
4. **json 文件而非数据库**：单用户部署假设下最简可靠，mtime 缓存 + 原子写覆盖了并发与崩溃场景。

## 新人提示

- 测试记忆行为用 `reset_memory_queue`/`flush`（queue.py:131/:186），别 sleep 30s。
- LLM 返回非 JSON 只打日志返回 False（updater.py:294-299），静默失败——排查"记忆没更新"先看 stdout 的 "Failed to parse"。
- `get_memory_data` 是带 mtime 校验的缓存读，Gateway 改文件后 LangGraph 侧下次装配自动可见，无需手动 reload（reload_memory_data 只给 API 强刷用）。
- prompt.py 的 .format() 模板里 JSON 花括号全部双写转义（prompt.py:85-100），改 MEMORY_UPDATE_PROMPT 时最易踩。
