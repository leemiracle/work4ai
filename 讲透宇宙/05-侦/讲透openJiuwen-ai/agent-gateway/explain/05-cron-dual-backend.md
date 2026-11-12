# 05 · cron 双后端存储：调度线与存储真身的分家、File 双层锁与 Etcd CAS

> 锚定 commit `7af202253`。行号指 `agent_gateway/cron/`（调度线）与 `agent_gateway/runtime/cron/`（存储真身）下各文件。

## 一、角色定位

cron 子系统横跨两个包：`cron/` 是**调度线**——`CronSchedulerService`（scheduler.py 2501 行，唤醒-触发-推送的运行时）、`CronController`（controller.py，Web RPC 面单例）、proactive_cron_sync/dingtalk_routing/lifecycle_owners 等配套；`runtime/cron/` 是**存储真身**——models（693 行 CronJob/CronTarget）、store（FileCronJobStore 388 行）、etcd_store（EtcdCronJobStore 287 行）、cron_job_mutations（357 行构造/补丁/迁移纯函数）、factory（后端选择）。

两包的关系用了一个罕见的机制钉死：`cron/` 里的 `store.py`/`factory.py`/`models.py`/`store_base.py`/`cron_expr.py`/`dingtalk_routing.py` 六个文件都是 **sys.modules 别名 shim**——如 `cron/store.py` 全文只有"import 真身 + `sys.modules[__name__] = _implementation`"（cron/store.py:1-7），把旧导入路径整体替换为 `runtime.cron.store` 模块对象。这意味着 `from agent_gateway.cron.store import FileCronJobStore` 拿到的模块身份就是 runtime 侧那个，`isinstance`/monkey-patch 不会因路径不同而分裂——比 re-export 更彻底，是母仓拆分后保兼容的标准姿势。调度侧真正自有的实体（scheduler/controller/proactive_cron_sync/lifecycle_owners/cron_json_convert）不是 shim。包 docstring（`agent_gateway/cron/__init__.py:1-6`）概括职责：CronJob 模型与持久化（本地 cron_jobs.json 或 etcd 高可用）+ asyncio 调度器（push 前唤醒 agent、结果推渠道）。

## 二、内部结构

**后端选择 `create_gateway_cron_store`**（`runtime/cron/factory.py:25-56`）是全篇最短也最重要的函数，三段论：默认 `FileCronJobStore`（个人版）；`gateway.cron.store_backend=etcd` 显式 opt-in；**etcd 配置不全时打 error 日志"not falling back to local file"（factory.py:47-51）然后照样构造 EtcdCronJobStore**——不做静默降级。docstring（factory.py:30-32）把这层意图写死："etcd is opt-in via ``gateway.cron.store_backend=etcd`` and is **not** inferred from AgentOS routing or from a non-empty endpoints list"——即既不会因为检测到 AgentOS 部署就悄悄切 etcd，也不会因为 endpoints 非空就自作聪明。配置解析 `CronStoreSettings/load_cron_store_settings` 由 `common/cron_settings` 提供（gateway/runtime/server 三方共用，factory.py:3-5 注释"减少分叉面"）。

**存储协议 `CronJobStoreBackend`**（`runtime/cron/store_base.py:17-70`）是 structural Protocol：`supports_watch` 类属性 + list/get/create/update/delete/get_revision/watch/aclose 八个方法。两个注释值得记住：`CronRunState is never part of this protocol (memory-only)`（store_base.py:14-15）——运行态永不持久化；watch 的 docstring（store_base.py:60-63）"File backend does not implement this; scheduler uses ``supports_watch``"——能力声明而非异常约定。

**FileCronJobStore（文件后端）**，`runtime/cron/store.py:31-380`：
- **双层锁**是并发安全的骨架（store.py:33-38 docstring）：`asyncio.Lock` 管同进程协程互斥，`portalocker` 伴生 `cron_jobs.json.lock` 管跨进程（多 Gateway/Agent）互斥，"整个 read-modify-write 在双层锁内完成，避免 lost update"。执行链 `_run_locked`（store.py:66-69）：先拿 asyncio 锁、再 `asyncio.to_thread` 进文件锁——等待文件锁的阻塞被扔进线程池，不卡事件循环；锁超时 10s（store.py:28）。
- **原子写** `_write_json_unlocked`（store.py:350-356）：写 `.tmp` 临时文件后 `tmp.replace(path)` 原子替换；文件锁本身不会被 replace 覆盖（store.py:57 注释点破这个细节：锁是伴生 `.lock` 文件不是被写文件本身）。
- **修订号** `_file_revision`（store.py:71-80）：`(mtime_ns << 40) ^ (ctime_ns << 16) ^ size` 的异或混合——文件系统没有真 revision，这个指纹让调度器能感知变更。
- **惰性迁移**（store.py:85-107）：`list_jobs` 在同一把锁内 read + `migrate_work_mode_on_items` 补老 job 缺的 work_mode + writeback，替代启动期一次性迁移；写回失败只 warning 不阻断读取。
- **update_job 的单次持锁读改写**（store.py:226-259）：注释（store.py:231-233）直指母仓 #4964 修复——"调度器在触发点标 expired/enabled 与执行完成回写 last_session_id 是并发写入者，读与写分开加锁时后写者会基于过期快照整条覆盖前者的字段"。
- **watch 显式不支持**（store.py:358-360）：抛 `NotImplementedError("FileCronJobStore does not support etcd watch")`。
- **proactive 保护**：delete_job 非强制时先 `ensure_proactive_deletable`（store.py:265-266），主动任务的哨兵 job 不许普通删除。

**EtcdCronJobStore（etcd 后端）**，`runtime/cron/etcd_store.py:34-287`：
- **per-job key 布局** `/jiuwenswarm/cron/jobs/{job_id}`（etcd_store.py:29、etcd_store.py:35），对比文件版的整文件 JSON——粒度从"全库一把锁"降到"单 job 一次 CAS"。
- **连接失败不阻塞启动**（etcd_store.py:37-39 docstring）：`list_jobs` 在 etcd 不可达时返回 `[]`（etcd_store.py:85-89），watch 循环带退避重连后 reload。
- **CAS 更新**（etcd_store.py:216-254）：`update_job` 先 `_get_job_with_rev` 取 mod_revision，`put_if_mod_revision` 条件写；`EtcdCasError` 时**重读-重放一次**（etcd_store.py:235-249，patch 是语义补丁所以重放安全），再失败才向上抛。同样受进程内 `asyncio.Lock` 串行化（etcd_store.py:220）。
- **watch 退避**（etcd_store.py:271-284）：初始 1s、指数翻倍、上限 30s（etcd_store.py:30-31）；回调先执行一次（首载），随后 `watch_prefix` 每次事件触发 `callback()`；异常统一 catch 重睡。
- **endpoints 为空的特殊处理**（etcd_store.py:65-74）：`_unavailable` 只打一次 error（`_logged_empty_endpoints` 去重，etcd_store.py:66-72），错误信息与 factory 一致——"not falling back to local file"。

## 三、外部连接

- **装配**：`app_gateway.py:2024-2042`——`create_gateway_cron_store()` → `CronSchedulerService(store, agent_client, message_handler)` → `CronController.get_instance(store, scheduler)` 单例 + `bind_agent_client`；随后把工厂注册进 provider 注入点 `"cron_store_factory"`（app_gateway.py:2048），common 层 model_resource 处理器经它反向创建 gateway 侧 store。file 后端时才跑 `migrate_legacy_cron_selections`（app_gateway.py:2030-2034，注释：共享 etcd 任务需要目标用户的 catalog，那迁移属于 per-user 资源边界、绝不用 Gateway 的 catalog）。
- **watch 消费**：scheduler 在 `start()` 里检查 `supports_watch`（scheduler.py:548-553）——真则起 `cron-store-watch` 任务走 `store.watch(self.reload)`（scheduler.py:555-562），假则走 revision 轮询/事件路径（scheduler.py:375-389 的 get_revision 消费）。
- **CronController 单例**（controller.py:70-145）：`get_instance` 未初始化时要求 store+scheduler 双参，语义与 MessageHandler 同款。
- **credential_ref 凭据绑定**：`CronJob.credential_ref`（models.py:434）是"登录会话捕获凭据绑定"（models.py:264）——定时任务执行时的模型凭据不内嵌 token，只挂句柄，执行侧凭据注入只认这个 ref（与 02 篇 `_handle_login_credential_refresh_push` 的续期链路呼应：ref 失效可 revoke，任务跑不了但凭据不泄漏）。models.py:430-434 注释还钉了一个身份边界："路由 user_id 与华为账号是两套"，老数据无字段兜底为空串=未绑定（models.py:610-611）。
- **cron push 回程**：调度结果经 MessageHandler 的 server_push `cron.response` 通道回流（含属主双校验，见 02 篇 message_handler.py:3378-3406）。

## 四、数据流

**写路径**（前端建/改任务）：CronController RPC → store.create_job/update_job。文件版：`build_new_cron_job` 构造校验（mutations 模块）→ `_run_locked`（asyncio 锁 → to_thread → portalocker）内 read JSON → apply patch/upsert → `.tmp` 写 + 原子 replace → 释放。etcd 版：build → `put`（create，etcd_store.py:206-214）或 get_mod_rev + CAS put（update，etcd_store.py:216-254）。两条线的**构造校验完全同源**（都走 cron_job_mutations），这是"一套语义两个后端"的关键。

**读路径 + 变更感知**：启动时 scheduler 读一次 list_jobs 拿全量与 revision；之后文件版靠 revision 指纹（mtime/ctime/size 混合）轮询对比，etcd 版靠 watch 前缀推送。`reload` 内部置 `_reload_event`（scheduler.py:800/1025/1113），调度主循环在事件等待点消费（scheduler.py:1170-1173）——重载是惰性合并进下一轮调度判断的，不打断在途执行。

**etcd 故障路径**：不可达时 list 返回空表（任务"消失"但不报错）→ watch 退避重连（1s→2s→…→30s）→ 恢复后 callback 触发 reload 全量回填。整个过程中 Gateway 主流程（chat/渠道）不受影响——cron 只是旁路服务，这正是"连接失败不阻塞 Gateway start"的设计边界。

**调度触发路径**（scheduler 侧）：到点 → wake_offset 提前唤醒 agent → 经 agent_client 发起执行 → 结果按 CronTarget 渠道投递（web/feishu/tui 的广播分支见 03 篇）；`_push_to_targets` 对 tui 置空 session_id 的决策在 tui_channel.py:94-103 注释有交叉引用。

## 五、设计决策与权衡

1. **显式 opt-in vs 静默降级**：etcd 配置错误时宁可让 store 带病运行（list 恒空 + error 日志），也不回退本地文件。理由藏在部署形态里： appliance 主备 Gateway 下，静默降级会让备机把任务写进本地文件，主机恢复后两边数据分叉——**数据分叉比暂不可用更难修复**。error 日志去重（etcd_store.py:66-72）则避免退避循环刷屏。
2. **锁策略双轨**：文件版双层锁 + 全量 JSON 读写（简单、可人读、单机够用，代价是 O(全库) 写放大与跨进程锁等待）；etcd 版 per-job key + CAS（细粒度、多写者安全，代价是依赖外部队列与退避复杂度）。协议 `CronJobStoreBackend` 只约束行为不约束实现，scheduler 用 `supports_watch` 做能力探测——典型的 capability-based 后端抽象。
3. **CAS 失败重放一次而非循环**：patch 是声明式语义补丁，重放幂等；无限重试在热键上会活锁，一次重放覆盖了绝大多数并发窗口，两次都撞说明真有持续写者，交给上层报错更诚实。
4. **shim 用 sys.modules 而非 re-export**：re-export 后两个模块对象并存，`sys.modules["agent_gateway.cron.store"] is sys.modules["agent_gateway.runtime.cron.store"]` 为 False，isinstance 与类型注解解析都可能分叉；整模块替换让旧路径彻底"变成"新模块（cron/store.py:7），迁移期零成本，代价是 shim 文件里看不到任何 API 面——读代码必须跳到 runtime 侧。
5. **CronRunState 永不入库**（store_base.py:14-15）：运行态（在途执行、暂停标记）只存内存，重启即丢——接受"重启后运行态清零"换取存储协议的极简，避免"持久化了过期运行态"这类一致性泥潭。

## 六、新人提示与坑

- **找 cron 存储实现别在 `cron/` 下读**：store/factory/models/store_base/cron_expr/dingtalk_routing 六个文件是 shim，真身在 `runtime/cron/`。改实现只改 runtime 侧；shim 一个都不要动。
- **文件后端下多进程并发**靠 portalocker 伴生锁（store.py:62-64），删 `.lock` 文件"清理垃圾"会直接打开 lost update 的门；锁超时 10s（store.py:28），锁竞争激烈时优先排查是不是有第二个 Gateway 实例在跑（app_gateway 有 gateway_lock 防同机双开，跨机共享 home 目录的部署要自己保证）。
- **`update_job` 必须整段在锁内**（store.py:231-233 引母仓 #4964）：任何"先 get 再另起锁 update"的重构都会复活"过期快照整条覆盖"的老 bug——调度器标 expired 与执行完成回写就是真实并发的两个写入者。
- **etcd 后端 list 空不等于没任务**：不可达返回 []（etcd_store.py:85-89），监控/排障要先看 `[Cron] etcd` 前缀日志再下"任务丢了"的结论。
- **加 CronJob 字段**要过四处：models（字段+to_dict/from_dict 兜底）→ store_base 协议签名 → 两个 store 的 create_job 形参（文件版经 build_job、etcd 版直传）→ cron_json_convert（前后端 JSON 映射）。`credential_ref` 的老数据兜底（models.py:610-611）是范本：新字段必须容忍旧数据缺省。
- **不要给 FileCronJobStore 实现 watch**：调度器按 `supports_watch` 分流，文件版塞个轮询 watch 会与 scheduler 自己的 revision 轮询形成双份重载。
