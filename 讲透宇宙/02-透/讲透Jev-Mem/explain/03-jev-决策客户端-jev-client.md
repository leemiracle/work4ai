> 标题：Jev 决策客户端——JevClient 精讲 · 源文件：memory/jev_client.py（300 行）· 图谱标签：System-One 决策控制层 / 扇出枢纽（file:memory/jev_client.py，fanOut=13）

## 角色定位

`JevClient`（`memory/jev_client.py:80`）是所有 System-One 决策的唯一出口：写路径的 admission/typing/关系判定、读路径的路由/停止/遍历，最终都汇到 `evaluate()`（140）这一个方法，由它统一处理缓存、预算、重试、校验、审计。文件头（1-5）写明架构立场："Central Jev SDK adapter for mixed Noul/Choice decisions. The outer retry loop owns Jev-Mem's call/deadline budget; SDK retries are disabled."——重试权威在本层，`typesafe_sdk` 侧的 `RetryPolicy(max_retries=0, timeout=None)`（104）只是配合。这层存在的意义：Jev 决策是高频小调用（一次查询可能十几次），必须有一个懂预算、懂缓存、懂失败降级的守门人，否则延迟与费用直接失控。

它还是三种后端的汇合点：远程 jev API（190-193）、本地 Laya 模型（182-189）、确定性 mock（175-181），由 `JevMemConfig.decision_backend` 选择，调用方对后端差异完全无感。

## 内部结构

- `JevUnavailable`（33-34）：RuntimeError 子类，预算耗尽或 fail-closed 模式下的失败信号。
- `CallBudget`（37-51）：跨多次 evaluate 共享的预算账本——`maximum_calls`/`deadline`（monotonic 时钟）/已用 `calls`/`cache_hits`/`fallback_events`；`consume()`（48-51）超限即抛 `budget_exhausted`。查询级预算（`maximum_jev_calls=10`、`max_latency_seconds=15.0`）由 `jev_mem_retrieval.py` 构造后传入——单次决策与查询是两层预算。
- `ProbabilityResult`（54-61）：frozen 结果载体。docstring 立规矩："Noul probabilities and complete Choice answers, never conflated"——概率（`values`）与选择题答案（`choices`）分字段存，`source` 记录来自 mock/cache/jev/laya。
- `DecisionLog`（64-77）：JSONL 审计，`sort_keys=True` + `allow_nan=False`（71）保证行稳定可 diff，文件追加在锁内（73-77）。
- `JevClient.__init__`（81-96）：api_key 解析有讲究（85）——显式传入优先于环境变量，**包括显式空串**（注释 "including an empty key (fail closed)"），防止测试以为配了 key 实际读到空字符串；94-96 行 Laya 后端在构造期就位（非懒加载）。
- `_get_sdk`（98-106）：单例构造 `TypeSafeClient`，retry 归零。`close`（119-125）关 laya 与 sdk；`__enter__`/`__exit__`（127-131）支持 with；`retrieval_slot`（108-117）：Laya 后端返回 `_retrieval_lock` 把本地推理串行化（docstring 109-114 解释：让一个检索把模型队列用完，而不是多个查询的 deadline 在队列里一起过期），远程后端返回 `nullcontext` 保持并行。
- `probabilities`（133-138）：兼容旧 Noul-only 调用方的糖衣——str 自动包成 `Noul(instructions=...)`，混入 Choice 就 raise（137）。
- `evaluate`（140-225）：核心方法，见数据流。
- `_question_payload`（227-240）：入参契约——非空 dict、ID 非空 str、值必须是 `Noul`/`Choice`、instructions 必填（236 行注释 "IDs are not sent to the model"）、Choice 至少两选项。
- `_probability`（242-246）与 `_validate`（248-271）：把模型输出当不可信数据，见设计决策。
- `_retry_after`（273-288）：解析 `retry-after-ms`/`retry-after`，支持秒数与 HTTP 日期两种格式。
- `_log`（290-293）与 `_failure`（295-300）。

## 外部连接

import：`typesafe_sdk` 六个符号（23-26，含三个异常类）、`.jev_mem_config.JevMemConfig`（28）、延迟 `from .laya_backend import LayaBackend`（95）。被 import：`memory/query_engine.py:55`、`memory/memory_builder.py:62`（两处都是"没有就自建"），`memory/jev_mem_retrieval.py:11` 只拿 `CallBudget`。图谱 fanIn=3 / fanOut=13——扇出全仓最高之一，典型的依赖汇聚点。实例拓扑要注意：`MemoryBuilder` 建一个自用（`memory/memory_builder.py:65`），`QueryEngine` 复用 builder 的同一个实例（`jev_mem/system.py:23` 传的是 `memory_builder.jev`）——全系统共享一份 LRU 缓存与审计流，mock/测试时改一处即全局生效。

## 数据流

以写路径关系判定为例走全程：`WritePolicy.relations` 组好 `{pair_0_semantic: Noul(...), ...}` → `evaluate("relations", {new_memory: ..., candidates: ...}, questions)`（`memory/jev_mem_policies.py:138`）→ 147 行 `_question_payload` 转 wire → 148-151 组 payload（backend/model/state/questions 全进缓存键）→ 152 行 `hashlib.sha256(json.dumps(..., sort_keys=True))` → 153-155 无外部预算则自建一份（max_retries+1 次调用、timeout×(max_retries+1) 截止）→ 156-157 deadline 已过直接 `_failure("deadline")` → 158-167 缓存命中路径：锁内 `move_to_end` + `deepcopy`，命中后 `replace(source="cache", usage={})`、`budget.cache_hits += 1` → 未命中进 169 行重试循环：172-173 jev 后端无 key 抛 `missing_typesafe_api_key`；174 行 `budget.consume()`；175-193 按 backend 三路取 `raw`（laya 的 timeout 取 `min(timeout_seconds, remaining)`，183）；194 行 `_validate`；195-198 再查 deadline 并组 `ProbabilityResult`；199-204 写缓存并 LRU 淘汰（`popitem(last=False)`）；205-206 审计 `jev_decision` 返回。

失败侧：207-209 `JevUnavailable` 不重试直接 break；210-211 响应校验失败记 `invalid_response`（可重试）；212-216 HTTP 错误按 status 分类——4xx（除 408/429）不重试，5xx 与限流可重试并解析 Retry-After；217-219 连接错误/ValueError/KeyError/TypeError 只记异常类名（218 行注释 "No response bodies, request state, or credentials in failure logs."——审计不留敏感信息）；220-224 退避 = Retry-After 或 `min(5.0, 0.5·2^attempt) × uniform(0.75, 1.0)` 抖动，且 delay 会吃掉剩余 deadline 就放弃（223 行注释即此意）。最终失败走 `_failure`（295-300）：记 `fallback_events` 与 `jev_fallback` 审计；`fallback_to_magma=True`（默认）返回 None——调用方（如 `memory/memory_builder.py:173-174`）见 None 转 MAGMA 基线。

## 设计决策

三个值得抄的工程决策。① **双层重试收敛为一层**：SDK retry 归零、外层按预算重试（104 与 169），调用次数与延迟有单一权威账本，杜绝 SDK 悄悄重试打穿预算。② **校验即防线**（248-271）：Noul 答案必须 type 匹配且概率在 [0,1]（242-246）；Choice 答案的分布必须**恰好覆盖**请求的选项集（262-263）、和≈1（265，abs_tol 1e-3）、且**选中项必须是最高概率选项**（267-268，1e-6 容差）——模型说"选 B"却给 A 最高概率，这种自相矛盾直接判 invalid 触发重试。③ **失败即降级而非崩溃**：默认 `fallback_to_magma` 让 Jev 不可用时系统退回基线（线上与实验都不断电）；要做严格评估就关掉它，`JevUnavailable` 会抛出来（298-299）。

批判地看局限：缓存键含 state 全文（152），长对话里 state 单调增长会稀释命中率；`deepcopy` 进出缓存（162、201）对高频小结果有可测开销；`evaluate` 近 90 行承担三路后端 + 重试 + 缓存 + 校验，圈复杂度高，拆 `_call_backend` 会更可测。

## 新人提示

先把 `evaluate`（140-225）通读一遍再看其它。三个误解高发：① **返回 None 不是异常**——它是"配置允许降级"的正常返回，忘判 None 是本仓最常见 bug 模式（`memory/memory_builder.py:145/156/173` 三处都必须判）；② `probabilities()` 与 `evaluate()` 不是新旧两套 API——前者只是 Noul-only 糖衣（133-138）；③ `JevUnavailable` 只在 `fallback_to_magma=False` 时抛（299），默认配置下几乎见不到它。调试顺序：先看 audit JSONL 的 `jev_decision`/`jev_fallback` 事件（290-297），再看 `budget.fallback_events` 归因是 deadline/http/invalid 哪一种。
