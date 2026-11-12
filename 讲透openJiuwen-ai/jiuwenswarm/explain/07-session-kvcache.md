# 07 会话管理与 KV Cache

> 对应导览 S09。代表文件：`jiuwenswarm/server/runtime/session/session_manager.py`、`session_history.py`、`kv_cache/` 五件套。

## 一、角色定位

session 子系统是 AgentServer 的"任务交通管制 + 上下文记忆经济"双重角色。管制面由 `SessionManager` 承担：把并发请求按 session 分道限行，保证同一 session 内任务串行、新任务优先（session_manager.py:21-25）；记忆面由 `session_history.py` 落盘 jsonl 历史，并由 `kv_cache/` 五件套管理推理 KV Cache 的换入换出——prefetch（预取回显存）与 offload（卸载释放）的时机判断。它不执行 agent 逻辑，只决定"谁先跑、上下文从哪来、空闲时显存怎么还"。

## 二、内部结构

**SessionManager**（session_manager.py:402 行）持六个字典：`_session_tasks`（当前执行中 Task）、`_session_priorities`（优先级计数器）、`_session_queues`（每 session 一个 `asyncio.PriorityQueue`）、`_session_processors`（常驻消费协程）、`_task_result_futures`、`_closing_tasks`（session_manager.py:28-33）。核心技巧在"递减优先级"：`submit_task` 每次先 `self._session_priorities[session_id] -= 1` 再把负数 priority 入队（session_manager.py:312-317），PriorityQueue 是小根堆，越新的任务 priority 越小越先出队——"先进后出，新任务优先"由此一行实现，无需时间戳或重排序。

processor 协程 `process_session_queue` 有三处防泄漏设计：①任务用 `asyncio.create_task(task_func(), context=task_ctx)` 以**调用方快照的 ContextVars** 创建（session_manager.py:249-253），避免继承 processor 旧上下文导致 workspace/cwd 漂移；②每轮结束主动把闭包变量置 None，防 `queue.get()` 保留协程帧持有对象图（session_manager.py:267-269）；③一次性 session（`health_check_/heartbeat/cron` 前缀，session_manager.py:41-48）在 `submit_and_wait` 收尾投递 `(1_000_000_000, None, None, None)` 哨兵（session_manager.py:365-368），大优先级确保排在所有已入队任务之后，让 processor 退出 while 循环走既有清理，否则协程永久阻塞在 `queue.get()`。

**kv_cache/ 是"反 barrel 五拆"教科书**：`__init__.py` 明文声明"按职责刻意拆分、不 re-export 任何符号，调用方必须显式 import 所属模块，使配置、产品状态与 Runtime 所有权保持可区分"（jiuwenswarm/server/runtime/session/kv_cache/__init__.py:3-14）。五模块各管一段：`kv_cache_application_runtime` 持有进程级共享 `KVCacheRuntime` 单例（kv_cache_application_runtime.py:15,46）；`kv_cache_model_provider` 只负责历史会话 fallback 模型的构造（kv_cache_model_provider.py:84）；`kv_cache_task_guard` 把产品事实转成去重后的逻辑动作、不持 provider 不写文件（kv_cache_task_guard.py:5-7）；`kv_cache_session_lifecycle_participant` 把 Runtime 生命周期事件适配到这些动作；`kv_cache_application_owner` 管发布与最终关停。

**TaskGuard 的状态机**：`SessionKVCFacts` 记录前台视图集合、运行任务数、是否完成过推理、是否已请求 prefetch（kv_cache_task_guard.py:26-36）。动作只有两种 `KVCGuardAction = Literal["offload", "prefetch"]`（kv_cache_task_guard.py:16）。去重靠 `last_prepare_intent_id`：同一 intent 重复的 prepare 直接返回 None（kv_cache_task_guard.py:92-97）。offload 条件在 `_maybe_offload`：已删除/还有运行任务/还有前台视图都不卸载；且"仅看过历史"不算——必须有 `has_completed_inference` 或曾经 `has_requested_prefetch`，保证纯浏览零副作用（kv_cache_task_guard.py:177-193）。

## 三、外部连接

上游：`interface.py:1562` 在 `JiuWenSwarm` 门面构造时实例化 `SessionManager`；`jiuwenswarm/server/agent_ws_server.py:2411-2417` 通过 `get_kv_cache_application_owner().attach_runtime(registry)` 把 KVC participant 以**租约**形式挂进 `RuntimeParticipantRegistry`（session_lifecycle.py:131,139）；Worker 进程收尾时 `jiuwenswarm/server/worker/runtime_host.py:89-92` 调 owner.close()。下游：TaskGuard 产出的动作由 participant 的 `_dispatch` 消化——按 is_team 选择 `create_agent_session/create_agent_team_session` 工厂，调 `session.suspend_kvc()`（offload）或 `session.prepare_kvc()`（prefetch）（kv_cache_session_lifecycle_participant.py:177-192），全部落到 openjiuwen SDK 的 `KVCacheRuntime`。横向：diff_service.py 的双软删除标记 `rewound_out`（diff_service.py:45）与 `discarded_out`（diff_service.py:51）与本文 rewind 链路呼应——redo 只恢复 discarded_out、不触碰 conversation rewind 的 rewound_out（diff_service.py:48-51,2475-2480,2561）。

## 四、数据流

一次用户输入的生命周期：chat.send → SessionManager.submit_and_wait 入队（负数优先级+ContextVar 快照+result_future 三件套，session_manager.py:319-359）→ processor 弹出并 create_task → 与此同时 Runtime 发 `SessionInputIntentEvent`，participant 调 `guard.set_foreground(visible=True)`（仅记录视图，**不触发 prefetch**，kv_cache_task_guard.py:69-71）再 `guard.prepare()`：有历史才请求 prefetch（kv_cache_task_guard.py:98-100）→ prefetch 作为独立 asyncio.Task 调度，chat 主流程**从不等待**远端 I/O（kv_cache_session_lifecycle_participant.py:167-172）→ 任务结束 `task_finished` 尝试 offload → 用户切走视图后 `_maybe_offload` 放行。删除流程则相反：`before_delete` 先打本地 tombstone 防晚到事件（kv_cache_session_lifecycle_participant.py:46-54）→ `release_resources` 走 `session.release_kvc()` 终局驱逐（带 `KVC_TERMINAL_CLEANUP_TIMEOUT_SECONDS` 超时，kv_cache_session_lifecycle_participant.py:72-73）→ 删除失败且未开始破坏性步骤时 `restore_after_failed_delete` 只回滚本地墓碑（kv_cache_task_guard.py:152-157）→ 提交成功后 `forget` 丢弃事实防止字典终身增长（kv_cache_session_lifecycle_participant.py:87-90）。

## 五、设计决策

①**fail-open 的 KVC**：`get_kv_cache_runtime` 任何配置异常都降级为 None 保持禁用（kv_cache_application_runtime.py:37-49）；owner 的六态状态机（DISABLED/ENABLED/TERMINAL_ONLY/SUSPENDED/CLOSING/CLOSED，kv_cache_application_owner.py:17-31）中 TERMINAL_ONLY 保留删除清理但抑制活动提示，SUSPENDED 完全不发布 participant——AgentServer 停止态保证离线删除不做远端 KVC 管理。②**租约不等于所有权**：进程可创建多个 Session Runtime/registry，都借同一个 participant；释放租约绝不关闭共享 runtime（kv_cache_application_owner.py:56-63），避免一个会话销毁误伤全进程 KV。③**拒绝猜测的模型选择**：`_select_unique_affinity_entry` 要求全部候选收敛到唯一物理目标（七元组 identity 含 provider/api_base/model_name/endpoint_profile/api_key/custom_headers/kv_cache，kv_cache_model_provider.py:34-63），`len(targets) != 1` 就返回 None（kv_cache_model_provider.py:79-81）——多目标宁可不启用也不猜。④**有界关停**：runtime.close 包在 `asyncio.wait` 超时内（kv_cache_application_runtime.py:63-65），且子任务取消被解释为 KVC 结果而非取消 server.stop（kv_cache_application_runtime.py:67-70）。⑤**世代防误删**：processor finally 清理前核对映射仍属于本代 queue/processor 才 pop（session_manager.py:283-290），允许同 session_id 在旧 processor 退出前重连。

## 六、新人提示

- 调试"同 session 任务顺序不对"先看 `_session_priorities` 的递减序，再排查是否有别处绕过 submit 直接 create_task。
- kv_cache 目录**禁止往 `__init__.py` 加 re-export**——那是刻意的反 barrel 设计，import 必须指到所属模块。
- `has_active_tasks` 专供 dreaming busy_checker（session_manager.py:400-402），判断"是否能进入做梦"用它而非 `_session_tasks` 非空。
- session_history 的写路径是 20000 容量的 `WRITE_QUEUE` 后台 worker（session_history.py:31,1349），测试里要 `flush_history_writes()`（session_history.py:778）才能看到落盘结果。
- rewind 相关风险在官方审计文档有 5+6 条 open issue（非原子跨存储回退、context_ok=false 仍返回 ok=true 等，`.doc_project_maintainer/code/.../_handle_session_rewind_*/risks.md`），改 rewind 链路先读它们。
