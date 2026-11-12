# explain-02 · src/core/unit.c — Unit 抽象：状态机、依赖图与多态基座

## 一、角色定位

unit.c（7327 行）实现 systemd 最核心的抽象 `Unit`：一切可被调度的对象（service/socket/mount/target/scope…）的公共基类。它做三件事：一是维护 unit 的命名/别名/合并身份；二是维护**依赖图**（Requires=/Wants=/After= 全部折叠进一个嵌套 Hashmap）；三是实现高层状态机 `unit_notify()`——所有类型殊异的低层状态变化最终都汇入这里完成全局语义（时间戳、job 完成、审计、OnFailure 触发、紧急动作）。它本身不知道怎么启动一个进程，多态通过 `UnitVTable`（unit.h:529，约 40 个回调槽：init/load/start/stop/reload/sigchld_event/serialize…）下放给各类型文件。事务引擎（transaction.c/job.c）以它为节点做依赖求解。

## 二、内部结构

`Unit` 结构体（unit.h:228）关键字段：`id`（识别名）+ `aliases` 集合 + `merged_into`（合并目标）；`dependencies`——注释写明结构是 `Hashmap(UnitDependency → Hashmap(Unit* → UnitDependencyInfo))`（unit.h 依赖字段注释），第二层的 value 记录"依赖从哪来"（mask/generation），支持 daemon-reload 时精确撤销；`load_state`/`fragment_mtime`/`dropin_paths` 跟踪单元文件来源；`job` 与 `nop_job` 挂当前事务作业（unit.h 注释明确 JOB_NOP 可与真 job 并存）。

身份系统：`unit_new_for_name()`（unit.c:133）分配并注册；`unit_add_name()`（unit.c:234）加别名；`unit_choose_id()`（unit.c:329）在多个名字里挑主名；`unit_merge()`（unit.c:1149）把两个同型 unit 合并——先 `unit_merge_names()`（unit.c:932）搬名字、再 `unit_reserve_dependencies()`（unit.c:958）预占依赖槽位、最后 `unit_merge_dependencies()`（unit.c:1059）搬依赖边，三段式保证失败可回滚。加载管线 `unit_load()`（unit.c:1699）从 UNIT_STUB 出发，调 `UNIT_VTABLE(u)->load(u)`（unit.c:1727），成功后补挂 target_deps/slice/mount/oomd 四类默认依赖（unit.c:1732-1740+）。

## 三、外部连接

上游是 manager.c 的加载队列与 D-Bus 层（unit_load_fragment_and_dropin，unit.c:1450）；下游横向连接极广：job.c（unit_process_job 在 unit_notify 内被调）、slice.c（并发上限）、systemd-oomd（`manager_varlink_send_managed_oom_update`，unit.c:2775）、audit/plymouth（unit.c:2832-2834）、cgroup（`unit_prune_cgroup`，unit.c:2800）。pid 观察走 `unit_watch_pidref()`（unit.c:2915）注册进 manager 的 watch_pids。D-Bus 名字追踪走 `unit_watch_bus_name()`（unit.c:3745）——为 BusName= 服务装 NameOwnerChanged match（unit.c:3621）。`UNIT_HAS_EXEC_CONTEXT`/`UNIT_HAS_CGROUP_CONTEXT` 宏（unit.h:813-814）用 vtable 里的 offset>0 判断类型是否内嵌 exec/cgroup 上下文，是 C 里"继承字段"的惯用实现。

## 四、数据流

启动路径 `unit_start()`（unit.c:1954）是一道精心排序的闸门链：子系统限速（mount 的 mountinfo 监视，unit.c:1962）→ 幂等检查（已 active 返回 -EALREADY，unit.c:1975）→ 条件 Condition*=（unit.c:1991，ECOMM）→ 断言 Assert*=（unit.c:1996，EPROTO）→ 类型支持（unit.c:2003）→ 依赖再验证 `unit_verify_deps`（unit.c:2009）→ following 重定向（device/unit 组合型 unit 转发给主对象，unit.c:2013-2017）→ 冻结检查（unit.c:2020）→ slice 三级并发上限（hard 返回 -ETOOMANYREFS、soft/activating 返回 -EAGAIN 留队列，unit.c:2043-2053）。这个 errno 即调度语义的设计（EAGAIN=重排队）是 job 引擎能优雅重试的关键。

状态汇报路径 `unit_notify()`（unit.c:2751）是反向汇聚点：类型代码在低层状态变化时调用它，函数依次完成——挂 D-Bus 队列（unit.c:2764）→ 通知 oomd → 更新四个 dual_timestamp（unit.c:2777-2790）→ 维护 failed_units 集（unit.c:2793）→ 进 inactive 时清 cgroup/状态文件/marker（unit.c:2796-2801）→ `unit_process_job()`（unit.c:2814）驱动 job 完成 → 无 job 的"意外"状态变化回溯触发 `retroactively_start/stop_dependencies`（unit.c:2822-2827）→ OnSuccess/OnFailure 依赖（unit.c:2844-2847）→ FailureAction/SuccessAction 走 `emergency_action()`（unit.c:2858-2864，可直达 reboot/poweroff）→ 把相关 unit 挂入 stop_when_unneeded 等慢队列（函数尾部）。re-exec 恢复则走 `unit_coldplug()`（unit.c:3842，从序列化流重建在飞状态）与 `unit_catchup()`（unit.c:3869）。

## 五、设计决策

1. **C 语言多态**：vtable + offset 内嵌上下文（unit.h:529/813），每个类型文件只实现关心的槽，未实现的槽为 NULL 即"不支持"，`unit_can_start` 等能力查询据此返回。
2. **依赖边带溯源信息**：`UnitDependencyInfo` 记录来源 mask 与 generation（unit.h dependencies 注释），使依赖既可来自单元文件也可来自 path/udev 动态生成，且 reload 时能按代际差量撤销——`unit_clear_dependencies()`（unit.c:654）配合使用。
3. **两层状态语义**：低层 substate（各类型私有）映射到公共 UnitActiveState（13 值），unit_notify 只看高层，注释明确"ns==os 也合法，remount 会重复调用"（unit.c:2756-2758）。
4. **错误码即控制流**：-EALREADY/-EAGAIN/-EALREADY 语义在 unit_start 里被 job 引擎直接消费（unit.c:1970-1977 注释），省去显式重试队列协议。
5. **快慢分离**：即时事件（审计、emergency）在 notify 内同步做；组合判断（unneeded/bound/upheld）挂慢队列由 manager 循环统一裁决（unit.c:2867 起注释）——防止状态风暴时 O(n²) 传播。

## 六、新人提示

先读 unit.h:228 的 Unit 结构体与 unit.h:529 的 vtable，再读 unit_notify（unit.c:2751）——它是理解"一个服务启动完成到底发生了什么"的最佳单点。排障时 `systemctl show` 输出的每个字段几乎都能在 Unit 结构体里找到对应；`fragment_mtime` 与 `unit_need_daemon_reload()`（unit.c:3903）配合可解释著名的 "unit file changed on disk" 警告。改依赖逻辑务必从 `unit_add_dependency_impl()`（unit.c:3113）入手并理解 reserve/merge 的两阶段性，直接改 Hashmap 会破坏 reload 撤销。Unit 合并（alias 场景）是最易踩坑的路径：名字搬完不等于依赖搬完，回滚顺序与提交顺序严格相反。Condition 与 Assert 的区别只在失败后果（跳过 vs 失败，unit.c:1992/1997 的日志级别不同），面试常考。
