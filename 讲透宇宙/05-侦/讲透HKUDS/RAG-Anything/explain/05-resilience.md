# 05 · resilience.py —— retry 双子与 generation 代数熔断器

> 源码：`raganything/resilience.py`（414 行，commit 2cd2b332）。动机钉在文件头：issue #172——网络瞬时故障把 `process_document_complete` 卡死（`resilience.py:7-8`）。

## 1. 角色定位

面向用户的**瞬时故障工具箱**，三个公开件：`retry`（同步重试装饰器，`resilience.py:59`）、`async_retry`（异步孪生，:144）、`CircuitBreaker`（熔断器，:229，本身也是可调用装饰器工厂）。注意它的定位是**库级出口而非内部管线组件**：grep 实证 raganything/ 与 examples/ 内部零消费，仅经 `__init__.py:21-24` 的 try/except ImportError 门控导出（`__all__` 动态扩展 `__init__.py:101-106`）——供用户给自己的 `llm_model_func`/embedding 函数包壳，从源头消灭 #172 那类卡死。测试面 27 例：`test_resilience.py` 25 例钉 retry 行为，`test_circuit_breaker_stale_results.py` 2 例专钉迟到结果。

## 2. 内部结构

**（a）可重试异常白名单 `_DEFAULT_RETRYABLE`**（`resilience.py:29-32`）：只含 `ConnectionError` 与 `TimeoutError`，注释言明设计边界——本地编程错误（TypeError/ValueError/KeyError）与多数 OSError 子类（FileNotFoundError/PermissionError）**不该重试**。随后两段条件扩充：装了 httpx 加 ConnectError/ReadTimeout/WriteTimeout/PoolTimeout（:34-44），装了 openai 加 APIConnectionError/APITimeoutError/RateLimitError/InternalServerError（:46-56）。import 失败静默跳过，白名单随环境自适应生长。

**（b）retry 双子**。参数完全对称：`max_attempts=3`（含首次的总尝试数）、`base_delay=1.0`、`max_delay=60.0`、`exponential_base=2.0`、`jitter=True`、`retryable_exceptions`、`on_retry` 回调（:60-66）。退避公式 `base_delay * base^(attempt-1)`，jitter 乘 `1.0+uniform(0,0.5)`（0–50% 随机增量，:120-124），封顶 max_delay（:125）——注释点名动机：多 worker 同时撞限流时的 thundering-herd 抑制（:70-71）。每次重试前调 `on_retry(exc, attempt, delay)`（:126-127），异步版对回调返回值做 `iscoroutine` 判断、协程回调可 await（:209-212）。唯一差异是睡眠原语：同步 `time.sleep`（:136）vs 异步 `asyncio.sleep`（:221）——异步版用阻塞 sleep 会卡死整个事件循环，这正是它存在的理由。

**（c）CircuitBreaker——本文件的心脏**。三态机 closed/open/half-open（`_state`，:267）：closed 态失败计数（窗口外的陈旧失败先清零再计数，:300-307）达 `failure_threshold=5`（:249）→ generation+1 并 open（:310-313）；open 经过 `reset_timeout=60.0`（:250）→ half-open，只放行**一个**试验调用（single-flight，trial token 是裸 `object()`，:353-362）；试验成功→generation+1 回 closed（:286-289），失败→立即重开（:296-298）。

**generation 代数是整个设计的精髓**（ONBOARDING 钉版的 :271,323）。问题场景：熔断 open 期间某慢调用仍在飞；reset 后 half-open 试验成功、breaker 已回 closed 并进入新代数，此时**旧调用才失败返回**——若不设防，这个迟到的失败会被计入新周期、冤枉地重新打开刚恢复的熔断器。解法：`_acquire_permission` 发号时返回当前 `_generation`（:362,365），`_record_outcome` 入账前核对代数（:323-324），代数不符直接丢弃。代数在每次状态跃迁（成功关闭 :287、打开 :311）时递增，等价于给每个恢复周期编版号。

**（d）两类异常区别对待**。装饰器 `__call__`（:367-391）与 `async_call`（:393-414）里，`_failure_exceptions` 命中→记失败（上游不稳）；其他 Exception/BaseException→**不计失败**但必须释放 half-open 试验闸门（:386-388,409-411）——否则一次应用 bug 或任务取消会把 trial token 永久占住，熔断器从此对所有调用报 "trial in progress"。异步版特意捕 `BaseException` 就是为 `CancelledError` 放行（:406-408 注释）。

## 3. 外部连接（对齐图谱边）

- → `httpx`/`openai`：仅 import 探测扩充白名单，缺席时降级不报错（:34-56）。
- → 标准库：threading.RLock 全状态变更互斥（:270）、time/asyncio 双睡眠、functools.wraps 保签名。
- → `__init__.py`：try/except 特性门控导出 retry/async_retry/CircuitBreaker（:21-24），`globals()` 检查动态扩展 `__all__`（:101-106）。
- → 测试：`test_resilience.py`（25 例：参数校验/退避曲线/jitter 边界/白名单分型）；`test_circuit_breaker_stale_results.py` 以**四把 Event**（started/release/probe_started/probe_release，:19-22,81-84）编排「旧调用悬挂→恢复周期完成→旧调用才失败」的交错时序，sync/async 各一例（:15,77）——这正是 generation 机制的行为规约。
- ↔ 消费者：仓内零内部调用（grep 实证），全部价值经公共 API 输出到用户侧。

## 4. 数据流

以用户给 embedding 函数包熔断为例：`breaker = CircuitBreaker(name="embedding")` → `embed = breaker.async_call(raw_embed)` → 每次调用先 `_acquire_permission`：closed 直接放行（返回 generation，trial=None）；open 未到期抛 `CircuitBreakerOpen`（:347-351）**不执行函数**——快速失败正是防 #172 卡死的本体；half-open 首个调用拿 trial token 通过、并发后来者被拒（:354-358）。执行结果回 `_record_outcome(generation, success)`：代数一致才入账。retry 装饰器则可叠在外层：「快速拒绝→稍后重试→试探恢复」三层配合，由用户自行组合。全部状态变更都在 RLock 内，线程安全；async 版用同一把线程锁（协程切换点不在临界区，无死锁面）。

## 5. 设计决策

- **白名单从窄不从宽**：默认只认网络瞬断，宁可漏重试也不掩盖编程错误——重试 TypeError 只会把崩溃延迟三倍。
- **代数检查优于时间戳检查**：迟到结果的本质问题是「周期身份」不是「时间早晚」，单调递增整数比对 O(1) 且无时钟依赖；测试用冻结时间+Event 编排而非真睡 60s。
- **trial token 用 object() 身份而非常尔**：并发 half-open 时只有 token 持有者能释放闸门（`is` 比较，:387,410），第二个调用误触发清理不会误伤在飞试验。
- **应用异常必须释放闸门但不计失败**：失败计数反映「上游健康度」，本地 bug 不应污染它；但闸门是并发资源，漏放就是死锁。
- **同步/异步成对提供而不可混用**：异步场景套同步 retry 会阻塞事件循环（time.sleep），反之亦然——两套实现 99% 镜像（:144 docstring 自述 "Async counterpart"）。

## 6. 新人提示

1. 包自己的 LLM 函数是推荐用法：`@async_retry(max_attempts=5)` 与 `CircuitBreaker().async_call` 可叠用；模型函数常同时暴露 openai 三类错与裸 ConnectionError，白名单已全覆盖。
2. 改 `failure_threshold`/`reset_timeout` 前先想清下游语义：阈值 5+60s 针对的是 LLM API 限流节律，嵌套调用场景建议每个下游独立 breaker（用 `name` 区分日志）。
3. 看到 "trial in progress" 异常堆积别急着加超时——先查是否有非白名单异常在 half-open 期逃逸（理论上已被 :386-411 兜住，这行注释就是回归线索）。
4. 测试熔断逻辑时抄 `test_circuit_breaker_stale_results.py` 的 Event 编排模式，不要真等 reset_timeout。
5. 该模块不在核心依赖链上（`__init__.py` 门控导入），精简安装下 `from raganything import retry` 会 ImportError——脚本顶部就该显式处理。
