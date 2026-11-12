# torch/csrc/autograd/engine.cpp — 反向传播引擎：一张图如何被多线程"倒着"执行

> 源文件：`torch/csrc/autograd/engine.cpp`（1856 行）+ `engine.h`（299 行，类接口）
> 知识图谱节点：`file:torch/csrc/autograd/engine.cpp`，complexity=complex，tags=[autograd, engine, multithreading, scheduler, core]
> 图谱定位：`layer:csrc-bindings`（C++ 核心绑定层）· Tour #3「Autograd 反向传播引擎与 Python 桥接」
> 图谱 commit：f634d0e91da4cc1d4d669a60ede149214b754854（2026-09-03 分析）

---

## 一、它在架构中的位置

一句话定位：**forward 建图，engine 拆图**。前向时每个可微算子在 ATen dispatcher 的
Autograd key 下创建 `Node`（`grad_fn`），用 `next_edges` 串成一张反向 DAG；当用户调用
`loss.backward()` 时，本文件负责把这张 DAG 按拓扑逆序、跨设备、多线程地求值，把梯度
一路送到叶子张量的 `.grad` 里。

调用链上游（图谱 + grep 证据）：

- `torch.autograd.backward()`（Python）→ `torch._C._EngineBase.run_backward` →
  `python_engine.cpp:THPEngine_run_backward`（L179）→ `autograd.cpp:run_backward`；
- `autograd.cpp:139` 处 `Engine::get_default_engine().execute(...)` 是唯一常规入口：
  roots 取自 `impl::gradient_edge(output)`（即 loss 的 grad_fn），`output_edges` 取自
  输入张量的 `grad_fn()` 或 `try_get_grad_accumulator`（叶子的 AccumulateGrad）；
- 引擎本体是**单例**：`get_base_engine()` 返回静态 `Engine`（L1566-1569），但 Python
  环境下被 `PythonEngine` 覆盖——通过 `set_default_engine_stub`（L1573-1575）注入工厂
  函数，`get_default_engine()`（L1577-1579）经 atomic stub 间接取实例。所以纯 C++ 进程
  里跑的是基类，`import torch` 后跑的永远是 PythonEngine（见第十节）。

其他消费者：`dist_engine.cpp:116`（分布式 autograd 复用引擎）、`reducer.cpp:945`
（DDP 用 `queue_callback` 在 backward 结束时触发梯度桶 allreduce）、`function.cpp:65`
（node_creation_hooks）、`saved_variable.cpp:110`（saved tensor hooks）。

图谱出边：`contains` 11 个函数节点（execute/thread_main/evaluate_function/
compute_dependencies/init_to_execute/start_device_threads/reentrant_thread_init/
thread_init/call_function/exec_post_processing/execute_with_graph_task），
`depends_on engine.h`，`imports c10/core/Stream.h + c10/util/Exception.h`。

---

## 二、三个核心数据结构（engine.h + graph_task.h）

**1. `NodeTask`（engine.h L52-74）**——一次待执行的节点求值：
`base_`（weak_ptr 指向 GraphTask，图出错被销毁时自动失效）、`fn_`（intrusive_ptr<Node>，
即 grad_fn）、`inputs_`（InputBuffer，已凑齐的上游梯度）、`isShutdownTask_`。

**2. `ReadyQueue`（engine.h L87-126，实现在 engine.cpp L230-271）**——带优先级的任务队列：
`std::priority_queue<NodeTask>` + `mutex_` + `condition_variable not_empty_`。
`pop()`（L258-265）在 `not_empty_.wait` 上阻塞，是所有工作线程的睡眠点。
`push()`（L230-242）在锁内 `++graph_task->outstanding_tasks_` 后入堆并 notify_one——
注意这个计数在 push 侧自增，在 thread_main 消费完一个任务后自减（L586），一进一出
配平，正是完成检测的基石。

**3. `GraphTask`（graph_task.h，构造在 engine.cpp L655-672）**——一次 backward 调用的
全部状态：
- `outstanding_tasks_`（atomic）：还在队列里/正在执行的 NodeTask 数；
- `dependencies_`：`unordered_map<Node*, int>`，每个节点还差几条输入梯度；
- `not_ready_`：`unordered_map<Node*, InputBuffer>`，梯度没凑齐的节点的暂存缓冲；
- `exec_info_`：哪些节点需要执行、捕获哪些输出（服务 `grad()` 与 hooks）；
- `cpu_ready_queue_`：本 GraphTask 专属的 CPU 队列（关键设计，见第七节）；
- `owner_`：发起本次 backward 的线程的 worker_device；
- `future_result_`：`at::ivalue::Future`，完成时写入梯度列表，`execute()` 在它上面 wait；
- `leaf_streams` / `caller_current_streams_`：CUDA 流同步账本（见第八节）。

---

## 三、调度算法：依赖计数 + 优先级堆 = 动态拓扑排序

这本质是 **Kahn 拓扑排序的在线/并行版**，分两步：

**离线计数（execute 时一次）**：`compute_dependencies`（L1295-1361）从 GraphRoot 做
BFS，对每条 `next_edge` 执行 `dependencies[next_ptr] += 1`（L1347）——统计每个节点在
反向图中的入度（= 前向中有几个消费者）。`topological_nr() < min_topo_nr` 的子树被剪枝
（L1323-1325）：比最早 output 还"老"的分支不可能通向任何要求的输出。顺带统计设备分布
打 API usage 埋点（L1329-1343，评估多设备 backward 的使用率）。

**在线调度（每执行一个节点）**：`evaluate_function` 尾部（L1214-1279）拿到节点输出的
每条梯度，对下游 `next.function` 做 `--dependencies`（L1230）：
- 减到 0 → `is_ready`，立刻 `queue->push(NodeTask(...))`（L1255-1258）；
- 没到 0 → 梯度暂存进 `not_ready_[next.function]` 的 InputBuffer（L1260），等最后一条
  梯度到达时合并（`InputBuffer::add` 累加同一槽位的梯度）再入队（L1273-1276）。

正确性完全由这个计数保证；**堆只是调度启发式**。`CompareNodeTaskTime`（engine.h
L91-105）定义的优先级：shutdown 任务 > 空任务（叫醒用 dummy）> 更浅的 reentrant 深度 >
**更大的 `sequence_nr()`**。sequence_nr 在前向单调递增，越大离 loss 越近，backward
要先跑——所以堆按"新者先出"逼近拓扑逆序。反例恰恰是 AccumulateGrad（叶子），它没有
正常的 sequence_nr 语义，`get_current_graph_task_execution_order`（L423-483）的注释
（L453-457）明确点破：即使有 sequence_nr 仍必须数依赖，不能只看序号。

---

## 四、`Engine::execute()` 主入口走读（L1363-1473）

1. **L1370-1374** `validate_outputs`：校验初始 grad_outputs 的数量/dtype/layout/device，
   不合法立刻报错（实现见 L956-1053 的 `validate_outputs_impl`，含 `maybe_reduce` 即
   自动 `sum_to`、grad dtype 提升 L991-1001）。
2. **L1375-1382** `accumulate_grad && create_graph`（`backward(create_graph=True)`）触发
   TORCH_WARN_ONCE：参数与梯度之间形成引用环会内存泄漏。
3. **L1397** `init_local_ready_queue()`（L1605-1614）：调用线程若无 thread_local 队列则
   新建一个——它成为本 GraphTask 的 `cpu_ready_queue_`。**L1398** `worker_device ==
   NO_DEVICE` 区分"全新调用"与"重入调用"（工作线程里又调了 backward）。
4. **L1407-1412** 构造 GraphTask（记录 keep_graph/create_graph/reentrant_depth/
   cpu_ready_queue_/roots）。**L1415-1421** 单 root 且非 compiled autograd 时直接用该
   root，跳过 dummy `GraphRoot` 节点；多 root 则包一层 GraphRoot（basic_ops.h）扇出。
5. **L1423-1430** `compute_min_topological_nr`（L1282-1293，取所有 output 边下游节点的
   最小拓扑号）→ `compute_dependencies` → outputs 非空时 `init_to_execute`（L1744-1854）。
6. **L1432-1444** compiled autograd 分支：`torch.compile` 的编译版 backward 经
   `the_compiled_autograd` 函数指针整体接管（要求无重入，L1433-1435）。
7. **L1447-1465** 把 root 包成首个 NodeTask（单 root 路径还细致地做了 InputBuffer 流
   记录）交给 `execute_with_graph_task`；**L1469-1472** `fut->wait()` 阻塞到 Future 完成，
   回放 warning，返回 `toTensorVector()`。

`init_to_execute`（L1744-1854）值得单独看：`.backward()`（accumulate_grad=true）把所有
output 边的 `exec_info_[fn].needed_ = true`（L1782-1785）；`.grad()` 则登记
`captures_`（L1790-1793），求值时把中间梯度抄进 `captured_vars_`（L1156-1172）——这就是
`grad()` 能返回中间梯度而 `.backward()` 只写叶子的分叉点。之后用显式 Frame 栈（L1798+
）做迭代 DFS，从 outputs 向 root 反向传播"需要执行"标记，`needed_=false` 的节点在
`evaluate_function` 里被跳过（L1147-1155, L1173-1176）——不计算无效分支。

---

## 五、`thread_main` 事件循环与 `evaluate_function`（引擎心脏）

`thread_main`（L516-609）有三种身份（文件头注释 L500-515 写得很清楚）：设备线程的永久
自旋、CPU 调用线程的同步驱动、重入 backward 的临时接棒。循环体：

- **L534** `local_ready_queue->pop()` 阻塞取任务；**L537-540** shutdown 任务 → break；
- **L549** `set_device(worker_device)`：遍历 `device_guard_impl_registry` 把本线程的
  current device 设为目标设备（L873-894，不用 DeviceGuard 是因为 device 是 thread-local
  的、无需恢复）；
- **L555-577** 依次套上：`ThreadLocalStateGuard`（恢复调用方 TLS，如 autocast/
  dispatch keys）、warning handler guard、`GraphTaskGuard`（L387-397，设置
  `current_graph_task` TLS——`queue_callback` 靠它找到宿主）、`NodeGuard`，
  然后 `RECORD_FUNCTION` + `evaluate_function`；
- **L578-581** 异常 → `thread_on_exception`（虚函数，PythonEngine 覆盖为转 Python 异常），
  `has_error_` 置位后同图后续任务全部跳过（L551 判断）；
- **L586** `--outstanding_tasks_`；**L589-607** 若 `completed()`（`outstanding_tasks_==0`
  或 `exit_on_error_ && has_error_`，L674-677）→ `mark_as_completed_and_run_post_processing`
  （L679-704：`future_completed_` exchange 保证单线程进入 → 锁内
  `exec_post_processing` → `future_result_->markCompleted(vars)`）。若完成者不是 owner
  线程，还要给 owner 的队列推一个空 NodeTask 把可能睡在 `pop()` 上的 owner 叫醒
  （L601-606，空任务在堆里优先级仅次于 shutdown）。

`evaluate_function`（L1103-1280）单节点求值全流程：
1. **L1117-1121** 取 parent stream（优先 InputBuffer 上被 stale-capture 覆盖的记录），
   `OptionalStreamGuard` 进入该流；
2. **L1124-1140** 对每个 accelerator 输入：生产者流 ≠ 消费流时 `wait(ready_event)`
   ——跨流梯度的消费者侧同步点（事件由 `InputBuffer::add` 在生产者流上 record）；
3. **L1144-1177** exec_info 处理：captures 抄录、needed_=false 提前 return；
4. **L1179** `call_function`（L1055-1101）：tensor pre-hooks → pre-hooks →（keep_graph=
   false 时 `will_release_variables`）→ **`fn(std::move(inputs))` 真正执行 backward
   公式**（L1088/L1090）→ `validate_outputs` 校验输出梯度 → post-hooks；
5. **L1197-1210** AnomalyMode 开启时检查输出 NaN，报错带上节点名；
6. **L1214-1279** 锁 `graph_task->mutex_`，做第三节的依赖递减与下游任务分发。输出为空
   的节点（L1186-1195）把 parent stream 记入 `leaf_streams` 后返回。

---

## 六、多线程执行模型：谁在跑这些任务？

三类线程（Note [Reentrant backwards]，L142-170）：

**1. CPU：调用线程自己干活，没有常驻 CPU 线程。** `execute_with_graph_task`（L1487-1561）
里 `worker_device == NO_DEVICE` 分支：`set_device(CPU_DEVICE)` → `graph_task->owner_ =
CPU_DEVICE` → 首个任务入队 → **调用线程直接进 `thread_main(graph_task)` 同步驱动**
（L1516），GraphTask 完成后 `worker_device` 复位 NO_DEVICE（L1522）。你的
`loss.backward()` 那一行代码所在的线程，就是 CPU 任务的执行者。

**2. 设备线程：每 GPU（号）一条，进程级共享、常驻自旋。** 首次 backward 时
`initialize_device_threads_pool`（L1475-1485，static-once）→ `start_device_threads`
（L1656-1700）：遍历 `device_guard_impl_registry` 取非 CPU 队列设备的最大 deviceCount
（Note [Allocating GPUs to autograd threads]，L356-372：**colocate 策略**——CUDA:0 与
XLA:0 共用 0 号线程，取 max 而非 sum），为每个设备号建一个 `device_ready_queues_[i]`
并 detach 一条 `thread_init` 线程。`thread_init`（L340-385）设线程名
`pt_autograd_<i>`、`worker_device = i`、绑定 local_ready_queue，然后 `thread_main(nullptr)`
永久循环直到收到 shutdown 任务。CPU/Meta/Lazy 设备的任务不走这些线程（`should_run_in_
cpu_ready_queue`，L62-68）。

**3. 重入线程池：解决"工作线程里又调 backward"的死锁。** 设备线程执行到一个 Node，
该 Node 的 backward 里再调 `.backward()`（如 double backward、checkpoint 重计算、自定义
Function 里嵌套）：按语义 execute 必须 wait，但本线程还欠着队列的活，直接等就死锁。
方案：`current_depth >= max_recursion_depth_`（MAX_DEPTH=60，engine.h L38，取自 TSAN
65 把锁上限）时 `add_thread_pool_task`（L1702-1722）把 GraphTask 丢进
`ThreadPoolShared::graphtasks_queue_` 并按需 spawn 池线程；池线程
`reentrant_thread_init`（L616-642）醒来后**接管 owner 的 cpu_ready_queue** 继续
thread_main，原线程则去 wait Future。未到深度上限时（L1542-1550）直接同线程嵌套
thread_main（current_depth/total_depth 配对增减）。

辅助设施：`in_bad_autograd_fork`（L45-60，pthread_atfork 追踪——fork 出的子进程没有
这些线程，再 backward 直接报错）；`stop()`（L282-320，析构时推 shutdown 任务，最多等
TORCH_AUTOGRAD_SHUTDOWN_WAIT_LIMIT 秒，超时泄漏线程）。

---

## 七、ready_queue 的 per-device 设计（易混淆的重点）

`ready_queue(cpu_ready_queue, device)`（L1618-1635）的路由规则：

1. `torch.autograd.set_multithreading_enabled(False)` → 一律走该 GraphTask 的
   cpu_ready_queue_（单线程 backward，常用于调试/compiled autograd）；
2. 设备类型 ∈ {CPU, Meta, Lazy} → 走 **GraphTask 私有** 的 `cpu_ready_queue_`；
3. 其余（CUDA 等）→ 走 **进程级共享** 的 `device_ready_queues_[device.index()]`。

为什么 CPU 队列私有、GPU 队列共享？因为 CPU 任务的执行者（调用线程/重入线程）本身是
每次 backward 专属的；而 GPU 任务必须由常驻设备线程执行，天然跨 GraphTask 复用。后果：
并发的两次纯 CPU backward 互不干扰（各自队列各自线程），而 GPU 任务会在这张共享队列
上**交错**——所以 GraphTask 的所有共享状态（dependencies_/not_ready_/captured_vars_/
leaf_streams）都由 `graph_task->mutex_` 保护，完成检测只用 atomic 的
`outstanding_tasks_`（TLS 注释 L123-138 对此有完整论述）。

---

## 八、CUDA stream 语义（Note [Streaming backwards]，L172-205）

用户视角的契约：backward 涉及的算子跑在**前向同一 stream** 上，且 backward 相对周围
op 的可见性语义与普通调用一致。实现分三段：

- **生产者侧**：`InputBuffer::add`（input_buffer.cpp L231+）在累加梯度时记录
  producer/consumer stream，必要时 record event 存进 `ready_events/ready_streams`；
- **消费者侧**：`evaluate_function` L1124-1140，不同流则 `parent_stream->wait(event)`；
- **收尾**：`exec_post_processing`（L706-820）把每个 leaf stream 与调用线程当初的当前流
  （`stash_current_streams`，L1726-1742，在 compute_dependencies L1355-1360 里按需记录）
  做 event 同步（L727-784），保证 final callbacks 与 backward 之后的用户代码能安全读
  `.grad`。其中 L752-779 处理 CUDA graph capture 边界：恰好一边在 capture 时同步会
  作废 capture——默认报可操作错误，`set_override_stale_capture_stream(True)` 下跳过。
  之后在 `MultiStreamGuard` 下跑 `final_callbacks_`（L804-818，`queue_callback` L1592-1599
  注册，DDP 的 reducer 就挂在这）。

---

## 九、AccumulateGrad 的特殊处理

引擎里没有 `dynamic_cast<AccumulateGrad*>` 这种硬编码分支，特殊处理被拆到四个协作点：

1. **入口语义**：`accumulate_grad` 参数（execute L1366）区分 `.backward()` 与 `.grad()`
   ——`init_to_execute` 里 true → 所有 output 边 `needed_=true`（梯度要流入叶子），
   false → 设 `captures_` 收集返回值（L1782-1794）；
2. **图结构**：叶子张量的 grad_fn 就是 AccumulateGrad 节点（autograd.cpp L116-136 用
   `try_get_grad_accumulator` 找到它作为 output 边）；
3. **引用计数契约**：`call_function` L1071-1087 的长注释——有 post hooks 时引擎会留一份
   `inputs_copy` 把梯度 refcount 抬到 2，accumulate_grad.cpp 因此用
   `use_count() <= 1 + !post_hooks().empty()` 判断能否**偷走（steal）**梯度避免深拷贝。
   这是 engine.cpp 与 accumulate_grad.cpp 之间的隐式协议，改一处必须同步另一处；
4. **缓冲累加**：`InputBuffer` 的 `can_accumulate_inplace`/`accumulate`
   （input_buffer.cpp L119-174）在 GradMode 关闭且独占引用且 dense 布局时用 `add_`
   原地累加——叶子 `.grad` 的省拷贝快路径。

---

## 十、Python 桥接：python_variable / python_function 如何接进来

- **python_engine.cpp（PythonEngine）**：加载 torch._C 时把 stub 换成 PythonEngine 工厂。
  三处虚函数覆盖：`thread_init`（L62-75，先建 PyThreadState 再**释放 GIL**，让
  thread_main 内部的 `gil_scoped_acquire` 能正常工作——设备线程默认不持 GIL）；
  `thread_on_exception`（把 C++ 异常转成带 traceback 的 Python 异常塞进 Future）；
  `execute`（注入 Python 错误状态与 anomaly 元数据）。`THPEngine_run_backward`（L179）
  绑定为 `torch._C._EngineBase.run_backward`：解析 tensors/grad_tensors/inputs 元组、
  accumulate_grad 等关键字，转成 edge_list 后进 C++ execute。
- **python_variable.cpp（THPVariable）**：`torch.Tensor` 的 C 类型。`.backward()` 的
  Python 侧（torch/autograd/__init__.py）最终经 `_execution_engine.run_backward` 进上
  述绑定；`.grad` setter（THPVariable_set_grad）做类型/别名校验后写入——它消费的正是
  引擎写入 AccumulateGrad 的结果。Tensor 与 THPVariable 的互转（unpack）发生在绑定层。
- **python_function.cpp（PyNode）**：用户自定义 `autograd.Function` 的 backward 被包成
  `PyNode : Node`，`apply` 里拿 GIL 回调 Python backward。对引擎而言它就是普通 Node
  ——同样进 ReadyQueue、同样被 evaluate_function 调用（L1088 的 `fn(...)`），Python/C++
  混合图因此无缝执行；PyNode 需要持 GIL，这也是 PythonEngine::thread_init 提前布置
  PyThreadState 的原因。

---

## 十一、值得吃透的惯用法与常见误区

- **完成检测靠计数不靠 join**：`outstanding_tasks_` 在 push 侧 ++、消费侧 --，归零即完
  成（L586/L589）。图谱 languageNotes 一句话点破："GraphTask 完成由 outstanding tasks
  计数驱动而非 join"——这是无阻塞 DAG 调度器的标准写法；
- **weak_ptr 防悬垂**：NodeTask.base_ 持 weak_ptr，GraphTask 提前死亡时任务自动作废
  （L207-217 还把失效任务的 reentrant 深度报成 INT_MAX，让它被优先弹出尽快暴露错误）；
- **future_completed_ 的 exchange 防双跑**（L681-687）：多个线程可能同时看到归零，只有
  第一个 exchange(true) 成功者做后处理，后来者 wait 兜底；
- 误区 1：*backward 是单线程的*——CPU 任务确实多在调用线程，但每个 GPU 各有一条并行
  设备线程，多卡 backward 天然并行；
- 误区 2：*优先队列保证拓扑序*——不，依赖计数才保证正确性，sequence_nr 只是让执行
  顺序贴近"自然的"逆拓扑，减少缓冲驻留；
- 误区 3：*graph task 嵌套成栈*——文件头 L485-498 的 NOTE 明确反驳：同一队列上多个
  GraphTask 的任务会交错，thread_main 每次按弹出的任务切换 current_graph_task。

---

## 附：快速行号索引

| 主题 | 位置 |
|---|---|
| Note [Reentrant backwards] / [Streaming backwards] | engine.cpp L142-170 / L172-205 |
| ReadyQueue push/pop、shutdown | L230-271；比较器 engine.h L91-105 |
| thread_init（设备线程入口）/ 线程命名 | L340-385 |
| thread_main 主循环 | L516-609 |
| reentrant_thread_init（池线程） | L616-642 |
| GraphTask 构造 / completed / 收尾 | L655-672 / L674-677 / L679-704 |
| exec_post_processing（流同步+回调） | L706-820 |
| validate_outputs | L956-1053 |
| call_function（含 AccumulateGrad 契约注释） | L1055-1101 |
| evaluate_function（调度分发核心） | L1103-1280 |
| compute_dependencies / min_topo | L1295-1361 / L1282-1293 |
| execute 主入口 | L1363-1473 |
| execute_with_graph_task（CPU 驱动/重入分叉） | L1487-1561 |
| 单例与 stub、queue_callback | L1566-1579 / L1592-1599 |
| ready_queue 路由 / start_device_threads | L1618-1635 / L1656-1700 |
| add_thread_pool_task / init_to_execute | L1702-1722 / L1744-1854 |
| MAX_DEPTH=60 | engine.h L38 |
| Python 桥 | python_engine.cpp L62-75, L179；autograd.cpp L139 |
