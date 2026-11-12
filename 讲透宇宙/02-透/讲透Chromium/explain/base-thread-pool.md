# 精讲 thread_pool_impl.cc —— Chromium 后台任务调度中枢

> `base/task/thread_pool/thread_pool_impl.cc`（759 行，头文件 241 行）
> 图谱：base 地基层调度中枢，1 file＋17 function 节点，41 边

## 一、角色定位

`ThreadPoolImpl` 是 `ThreadPoolInstance` 的默认实现（`thread_pool_impl.h:44-46` 三重继承 `ThreadPoolInstance`＋`ThreadGroup::Delegate`＋`PooledTaskRunnerDelegate`），全进程后台任务调度中枢，取代旧 `WorkerPool`/`SequencedWorkerPool`（2016 迁移）。

用户面入口在 `base/task/thread_pool.h`——本仓**已无** `base/task/post_task.h`（`thread_pool_instance.h:40` 明言应走 thread_pool.h），其 `PostTask/PostDelayedTask`（`thread_pool.h:77/87`）与四个 CreateXxxTaskRunner（`:172-222`）全路由到全局实例；`Start()` 前不建线程（`thread_pool_instance.h:35`）。调度语义由 `TaskTraits` 的 `TaskPriority` 三档决定（`task_traits.h:30`）：**BEST_EFFORT**/**USER_VISIBLE**/**USER_BLOCKING**，配 `ThreadPolicy` 决定落哪个组、谁让位。

## 二、内部结构

本文件不含队列结构，是**组装者与仲裁者**，拼五类协作者：

1. **五个 ThreadGroup（按线程优先级分环境）**：五个 `EnvironmentParams` 常量（`:42-55`）对应 Foreground/Utility/Presentation/Audio/Background 五档 `ThreadType`。构造无条件建 foreground 组（`:91`），`CanUseBackgroundThreadTypeForWorkerThread()` 为真才建 background 组（`:103-117`），utility/presentation/audio 在 `Start()` 按 feature 建（`:161-204`）。
2. **ServiceThread**（头文件 `:199`）：专用消息循环线程，POSIX/Fuchsia 跑 `MessagePumpType::IO` 支撑 worker 内 `FileDescriptorWatcher`（`:146-156`）。
3. **DelayedTaskManager＋PooledSingleThreadTaskRunnerManager＋TaskTracker**（头文件 `:198-201`）：延迟任务回投、SingleThread 专用/共享线程、生命周期账房（shutdown/fence/许可）。

`Start()`（`:133-278`）装配主线：BEST_EFFORT 并发上限 `min(kMaxBestEffortTasks=2, max_num_foreground_threads)`（`:67/143-144`）；`CHECK` 起 service thread；新组建完立即 `HandoffTaskSourcesToOtherThreadGroup*` 迁移 foreground 组存量任务源（`:173-203`）；两 manager Start 须在其后；五组依次 `Start`（`:236-275`）。析构（`:120-131`）按序 reset 五组。

## 三、外部连接

**TaskRunner 三形态分派**是四个工厂（`:334-367`）：`CreateTaskRunner`→`PooledParallelTaskRunner`、`CreateSequencedTaskRunner`→`PooledSequencedTaskRunner`、`CreateSingleThreadTaskRunner` 转交 manager、`CreateUpdateableSequencedTaskRunner` 运行中可改优先级（BEST_EFFORT 起步须显式 ThreadPolicy，`:663-668`）。`CreateSequencedTaskRunnerForResource`（`:369-386`）用 `flat_map` 做 per-路径 sequence 复用，同一路径天然串行。

**对下层仲裁**集中在 `GetThreadGroup(ThreadType, ThreadPolicy)`（`:703-724`）：kBackground＋PREFER_BACKGROUND→background；`<=kUtility`→utility；`>=kAudioProcessing`→audio；`>=kPresentation`→presentation；兜底 foreground。post/Job 入队/`ShouldYield`（`:567/618-646`）全走它——二维到五组唯一映射点。

**与 sequence_manager 分工**：本池只管无泵 worker 线程，UI/IO 等带泵线程内部调度属 `base/task/sequence_manager`；池规模由 embedder 经 `InitParams`（`thread_pool_instance.cc:38-51`）注入。

## 四、数据流

**post 全链**：`PostDelayedTask`（`:321-332`）把闭包包成 `Task`，并**新建单任务 `Sequence`**、mode 取 `kParallel`（`:329-331`），单发也走序列抽象。随后 `PostTaskWithSequence`（`:574-616`）：`CHECK(task.task)` 宁可早崩（`:578`）；`WillPostTask` 问 shutdown 态，拒绝时**故意泄漏** task（`:581-586`，析构可能跑 sequence-affine 代码）；无延迟走 now 路径，有延迟 `AddDelayedTask` 到期经 service thread 调回（`:597-613`）。

`PostTaskWithSequenceNow`（`:550-572`）四步入队：`WillPushImmediateTask` 判断是否需（重新）进队列→`RegisterTaskSource` 登记→`WillPostTaskNow` 检查→`PushImmediateTask` 压入→`PushTaskSourceAndWakeUpWorkers` 送进组内 PriorityQueue 并唤醒 worker。worker 从 `WaitForWork()` 睡眠点醒来（`worker_thread.h:89`），取最高 sort key 执行。

**执行中让位**：`ShouldYield`（`:618-629`）——thread_type 已变而组不对（`:624`）让出去对的组，或同组有更高优先级（`:628`）；`UpdatePriority`（`:655-691`）同组改排序、跨组 Remove＋Push 搬家（`:679-688`）。

**运行许可闸门**：fence 家族（`:516-540`）改计数后经 `CalculateCanRunPolicy`（`:726-738`，三态 kAll/kNone/kForegroundOnly）与 `UpdateCanRunPolicy`（`:740-757`）写入 TaskTracker 并广播五组＋manager。`Shutdown`（`:410-451`）顺序即安全：先停 delayed manager 再停 service thread（crbug.com/698140），放开 CanRunPolicy 让 BLOCK_SHUTDOWN 任务正常优先级跑（`:425-430`），五组 `OnShutdownStarted()` 后 `CompleteShutdown()` 阻塞清零。

## 五、设计决策

**泛型 TaskSource 抽象**：`TaskSourceExecutionMode` 仅 `kParallel/kSequenced/kJob`（`task_source.h:31-35`），三种 runner 共用同一套 PriorityQueue/WorkerThread/唤醒基建。`:325-331` 是红利注脚：一次性 post 直接构造 `kParallel` 单任务 Sequence，与长寿命序列同一管线。

**环境多样性**：五组按 `ThreadType` 隔离，audio/presentation 高优先级组保证 deadline 任务不被后台拖累；feature 开启后用 Handoff* 迁移存量而非重建（`:173-203`）。

**MayBlock 与线程饥饿防御**（三层）：①BEST_EFFORT 并发上限 2（`:67/143-144`），`:231-235` 注释直说 "always room for incoming foreground tasks"；②`ScopedBlockingCall` 中的 worker 视为 blocked（`thread_group.h:85`），组内增派替补 worker 并轮询检测解除（`thread_group.h:235`）；③优先级反转防御在 `environment_config.cc`：`Lock::HandlesMultipleThreadPriorities()` 为假则不起 background 组，防前台等后台线程的锁。

**生命周期安全**：`TrackedRefFactory` 给子组发不可空引用（头文件 `:235`）；延迟回调的 `Unretained(this)`（`:612`）靠先停 service thread 的顺序保证（`:415-423/489-496`）。

## 六、新人提示

- **最大坑是"五连 if"模式**：构造、Start、Shutdown、JoinForTesting（`:497-510`）、UpdateCanRunPolicy（`:740-757`）每个新 ThreadGroup 都要补一处；漏一处则闸门对该组失效。
- `WillPostTask` 拒收时的**故意泄漏**（`:584-586`）不是 bug 别"修复"；动 Shutdown/JoinForTesting 顺序前读其注释（crbug 698140/771701）。
- 加新环境三处联动：`EnvironmentParams` 常量（`:42-55`）、`ThreadGroupType` 枚举（`:59-65`）、`GetThreadGroup` 分派（`:705-723`）——if 顺序即语义（`<=kUtility`/`>=kAudioProcessing` 区间）。
- 测试看同目录 `thread_pool_unittest.cc`，指标史 historical_histogram_data.md；降载入口 `BeginRestrictedTasks`（`:289-303`）与 fence 家族（`:516-548`）；入口认准 thread_pool.h（post_task.h 本仓已无）。

---

*行号基线：/usr-data/data1/browser/chromium/src（commit 8fe2331），全部行号经 grep -n 实证。*
