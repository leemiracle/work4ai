# 07 · distributed_c10d.py — 分布式通信塔基

> 源码: `torch/distributed/distributed_c10d.py` (8200 行) | 图层: `layer:distributed-training` | 复杂度: complex
> 一句话:它是 torch.distributed 的**总入口与全局账本**——init_process_group 完成 rendezvous、
> 按设备选出 NCCL/Gloo 后端构造 ProcessGroup,再用 `_world` 里的几张 dict 管住所有进程组,
> 并把 all_reduce/broadcast/barrier 等集合通信包装成统一的 Python API。tour 13 把分布式能力
> 描述成一座金字塔,本文件就是塔基:c10d → DeviceMesh → DTensor → FSDP。

---

## 1. 架构位置:金字塔塔基,谁踩在它上面

knowledge graph 的 incoming 边精确刻画了"塔"的结构(15 条):

- **device_mesh.py** `depends_on` 本文件——DeviceMesh 按维度切 mesh 时,每个维度调
  `new_group`/`split_group` 建一个 ProcessGroup(L556-640),mesh 本身只是 PG 之上的"排布";
- **_functional_collectives(_impl).py**——DTensor/torch.compile 的函数式集合通信底座,
  通过 `_resolve_group_name_by_ranks_and_tag` 等内部 API 把 `(DeviceMesh, dim)` 解析回 PG;
- **fsdp/_fully_shard/_fsdp_collectives.py**(FSDP2)与 **fsdp/_init_utils.py**——
  foreach all-gather/reduce-scatter 直接消费 `GroupMember.WORLD`;
- **_symmetric_memory/__init__.py**、**checkpoint/state_dict_saver.py**——
  单边通信的 rendezvous 与 checkpoint 的进程组都从 `_get_default_group()` 起步。

唯一的 outgoing import 是 `torch/__init__.py`(拿 device/serialization 等工具);真正的
通信实现在 C++ 侧——文件头 L38-66 直接从 `torch._C._distributed_c10d` 拉出
`ProcessGroup/Store/PrefixStore/Work/ReduceOp` 以及
`_register_process_group/_resolve_process_group`(这几个下文 §6 会用到,是 pickle 安全的关键)。

## 2. init_process_group:分布式训练的第一行代码 (L2370-2699)

分布式程序的第一句 `dist.init_process_group("nccl")` 走这条 330 行的流水线:

1. **防重入**: `GroupMember.WORLD is not None` 则抛 "trying to initialize the default
   process group twice!"(L2481)。`GroupMember.WORLD` 是类属性,经 `_WorldMeta` metaclass
   的 property 委托到 `_world.default_pg`(L1440-1454)——初始化完成的唯一标志。
2. **store vs init_method 互斥**(L2497-2506):两条 rendezvous 路线——
   - 显式传 `store/rank/world_size`(弹性训练、torchelastic 常用);
   - 传 `init_method` URL(默认 `"env://"`),L2623-2626 `rendezvous(init_method, rank,
     world_size)` 迭代器吐出 `(store, rank, world_size)`——TCPStore/FileStore 等在此诞生。
3. **backend 解析的三级降级**(L2544-2553):显式字符串 > `device_id` 查
   `Backend.default_device_backend_map`(L509-514: cuda→nccl, cpu→gloo, xpu→xccl,
   mps→gloo)> 置 `"undefined"` 交给 `BackendConfig` 运行时再探测。还支持
   `"cpu:gloo,cuda:nccl"` 多后端串(TorchComms 路径 L2558-2576 会自动补全)。
4. **timeout 缺省**(L2581-2584, `_get_default_timeout` L1467-1480):NCCL 10 分钟、
   其他后端 30 分钟(constants.py)。语义见 §7。
5. **建组**(L2633-2645):核心委托给 `_new_process_group_helper`(§4)。
   store 先包一层 `PrefixStore("default_pg", store)`(L2631)——键前缀隔离,防止多租户
   共享 store 时互相踩键。
6. **登记默认组**(L2649-2653):`_update_default_pg(default_pg)` 即写入
   `_world.default_pg`;`_world.pg_group_ranks[default_pg] = {i: i}`——默认组的
   global rank ↔ group rank 是恒等映射。
7. **excepthook 加 rank 前缀**(L2655-2676):把 stderr 回溯逐行加 `[rank0]:` 前缀,
   多机日志聚合时能定位是哪个进程崩了。这个细节是分布式调试的救命稻草。
8. **可选尾部 barrier**(L2678-2699):`TORCH_DIST_INIT_BARRIER=1` 时做一次
   `_store_based_barrier`,保证返回后所有 rank 的全局状态一致。注释里记着 2023/04 的
   取舍:大规模下这次 barrier 又贵又不可扩展,默认关。

**_store_based_barrier (L1658-1723)**:实现是 `store.add(key, 1)` 计数 + 轮询
`store.wait([last_worker_key], interval)`。两个工程细节:logging_interval 随规模放大
(L1687, `10s + world_size/1000`,经验值防误判超时);超时抛 `DistStoreError` 并报出
`num_workers_joined`——"卡在初始化"时第一个该看的数字。

## 3. 后端体系:Backend 注册表 + BackendConfig 设备映射

**Backend (L473-653)** 是个伪装成 enum 的 `str` 子类:GLOO/NCCL/UCC/MPI/XCCL/FAKE
(L492-498),外加两张能力表——`backend_capability`(gloo: [cpu,cuda], nccl: [cuda]...,
L516-523)和 `default_device_backend_map`。真正让它活起来的是插件机制:
`Backend.register_backend(name, func)`(L580-653)允许第三方(如 HCCL)注册
out-of-tree 后端;`_ensure_backend_registered`(L545-577)甚至能扫
`entry_points(group="torch.distributed.backends")` 懒加载——pip 装个包就能加后端。

**BackendConfig (L962-1055)** 是新一代配置对象,核心是 `device_backend_map:
dict[device, backend]`:
- `backend="undefined"` → 探测当前 accelerator,查默认映射(L971-987);
- 单名 `"nccl"` → 展开为其支持的所有设备(L996-1002);
- `"cpu:gloo,cuda:nccl"` → 逐对解析(L1020-1044)。

它回答的问题:**同一个 ProcessGroup 可以在不同设备上挂不同后端**(一个 PG 内部
按 device 注册多个 backend 实例,见 §4),这是 2.6+ 多后端实验特性的地基。

## 4. _new_process_group_helper:ProcessGroup 工厂 (L2786-3120)

所有建组路径(默认组/new_group/split_group)最终都到这。关键步骤:

- **全员到达约定**(L2800-2808):"必须由全局组**所有** rank 调用,哪怕不是新组成员"——
  非成员返回 `GroupMember.NON_GROUP_MEMBER`(哨兵 `-100`,L1464)。原因在 NCCL:
  communicator 的创建/分裂本身是 collective,少一个 rank 全体挂起。
- **tag 去重**(L2826-2831):`_find_pg_by_ranks_and_tag(pg_tag, ranks)` 命中则直接
  返回已有 PG——**同 tag + 同 rank 集合 = 同一个 ProcessGroup**。这是 DeviceMesh
  缓存维度组、functional collectives 幂等解析的语义基础。
- **ncclCommSplit 快路径**(L2844-2847, 2854-2868):若默认组绑定了 `device_id`
  (eager 初始化过),子组直接从父 communicator split;非成员 rank 也必须调
  `perform_nocolor_split` 保持同步。
- **构造**(L2874-2881):store 再包一层 `PrefixStore(f"{group_name}/", store)`
  (一个物理 store 被所有组按名分区复用),然后 `ProcessGroup(prefix_store,
  group_rank, group_size)`——这是 C++ 对象,自带按 device 的 backend 路由表。
- **逐设备装后端**(L2901-3068):对 `BackendConfig.get_device_backend_map()` 每个
  `(device, backend_str)`:查 `Backend._plugins` 拿 creator_fn——legacy API 传
  `(store, rank, size, timeout)`,extended API 传 `_DistributedBackendOptions`
  (含 split_from/process_group 引用,L2998-3014);然后
  `pg._register_backend(torch.device(device), backend_type, backend_class)`(L3068)。
  gloo/nccl 的 creator(`_create_gloo_process_group` 等)返回的 `ProcessGroupGloo/
  ProcessGroupNCCL` 就此挂进 PG。
- **可观测性挂件**:`TORCH_DISTRIBUTED_DEBUG=DETAIL` 时包一层 wrapper PG 做
  集合通信错位检测(L3028-3051);`TORCH_DIST_NAN_CHECK=1` 挂 `NanCheckHook`
  (L3081-3082);FlightRecorder 钩子记录每个 collective 的飞行日志(L3091-3093,
  事后 dump 分析 hang 的第一工具)。
- **登记进 _world**(L3100-3119):`_register_pg_in_world`(L7998-8057)一次性填
  pg_map/pg_names/pg_backend_config/tags 双向表,tag 缺省 `"ptd:{group_name}"`
  (ptd = pytorch distributed 内部命名空间),用户 tag 记为 `"user:{tag}"`。

## 5. 集合通信 wrapper:统一的五步模式

`all_reduce` (L3971-4074) 是所有 collective wrapper 的模板:

1. `has_torch_function` → `handle_torch_function` 重定向(L4030-4038)——注释挑明:
   Dynamo 会把 legacy 分布式 op 映射成 functional collectives,这里给非 Dynamo 路径
   (如 non-strict export)提供同构的 torch function mode;
2. `_rank_not_in_group` → `_warn_not_in_group` + 返回 None(L4041-4043)——不在组里
   不报错只警告,保证全员调用约定下的静默跳过;
3. 特殊 dtype 适配:complex 转 `view_as_real`(L4045-4048),broadcast 里 FP8 在
   sm90 以下转 uint8(L3937-3939);
4. 填 `AllreduceOptions`(reduceOp/asyncOp)后 `group.allreduce([tensor], opts)`
   (L4050-4065)——**真正的一行通信**;
5. async 语义(L4067-4074):`async_op=True` 返回 `Work` 句柄(用户后续 `work.wait()`);
   False 时 Python 层 `work.wait()` 兜底——注释说明部分后端已在 C++ 层同步过,
   `work is not None` 的判断是向后兼容。

**Work 句柄**就是异步 collectives 的 future:NCCL 把 kernel 排到独立 CUDA stream,
`wait()` 里做 stream sync,计算通信重叠全靠它。

**coalescing 批处理**:`_coalescing_manager` 上下文(L3625+)把 `_world.pg_coalesce_
state[group]` 置为待发列表,期间所有 collective wrapper 只往里 append `_CollOp`
描述符(all_reduce 的 L4056-4063),退出时统一提交、摊薄每个 op 的启动开销。
期间 `async_op=True` 会拿到 `_IllegalWork`(L3598-3609)——一个任何属性访问都
raise 的 Work 子类,防止用户在错误时机 wait。

**barrier (L6441-6515)**:文档注解(L6465-6470)藏着经典坑——NCCL 的 barrier 实现
是"对 1 元素张量做 all_reduce",必须选一台设备分配它,选择顺序:device_ids 参数 >
init_process_group 的 device_id > 该 PG 首次通信用过的设备 > `rank % 本机设备数`;
全不匹配就当前上下文设备(rank 0 warn 一次,L6499-6504)——"所有进程在 device 0
建 context"的告警即源于此。

**monitored_barrier (L6518+)**:仅 GLOO 的"看门狗 barrier"——rank 0 等所有人的
send/recv 并**点名超时的 rank**(wait_all_ranks=True 列全名单)。它和正常 barrier 的
区别:正常 barrier 挂住时全体沉默 hang,它会把"谁没来"喊出来,是排查 rank 掉队/
错位的第一诊断工具。

**object collectives**(all_gather_object 等,L4281+):`_pickler = pickle.Pickler`
(L303-304)序列化 → uint8 张量 → 走普通张量 collective → 反序列化。L310-317 顺手把
所有内建异常类和 StackSummary 加进 `add_safe_globals`,让 `weights_only=True` 也能
传 traceback(错误传播场景)。文档反复警告:pickle 不安全,可信环境才可用。

## 6. 向上通道:new_group/tag/GroupName——塔基如何被踩

**new_group (L6955) → _new_group_with_tag (L7059)**:建子组的公开入口。校验 ranks
(L7117-7146)后走 §4 工厂,并写 rank 映射表(L7193-7196):
`_world.pg_group_ranks[pg] = {global_rank: group_rank ...}`——**global↔group rank 的
双向翻译全靠这张表**(get_group_rank/get_global_rank/_get_group_ranks 都是它的查询
接口,L1744+)。`use_local_synchronization=True` 时非成员不必到场(大规模建小组的
加速器,但重叠组建错序会死锁,文档 L7034-7036 直言)。

**tag 命名空间**就是塔基与上层的接缝:
- DeviceMesh 建维度组时优先 `split_group`(ncclCommSplit 一次调建齐整维子组),
  否则逐子组 `new_group`(device_mesh.py L600-629),拿到的是 `group_name` 字符串
  存进 `_dim_group_names`;
- functional collectives 的 `_resolve_group`(_functional_collectives.py L1300-1356)
  把 `(DeviceMesh, dim)` 解析成组名字符串,再经 `c10d._resolve_group_name_by_ranks_
  and_tag` 变回 PG;
- **pickle 关键**:ProcessGroup(C++ 对象)不能序列化,但 `GroupName = NewType
  ("GroupName", str)`(L319)可以。文件头引入的 `_register_process_group(group_name,
  pg)` / `_resolve_process_group`(L40-42)维护着 **C++ 侧的全局 名字→PG 注册表**
  (destroy 时 `_unregister_process_group` L3235)。于是 DeviceMesh 的
  `__getstate__` 干脆丢掉 `_pg_registry`,unpickle 后按组名重解析(device_mesh.py
  L414-420)——"组名是跨进程/跨 pickle 的 PG 身份证"是整个分布式栈最重要的惯用法。

## 7. timeout/watchdog:超时的三层语义

- **操作超时**(init 的 timeout 参数,docstring L2430-2435):collective 超时后
  **异步 abort 并让进程崩溃**——因为 CUDA 执行是异步的,失败的 NCCL op 之后继续跑
  用户代码等于在损坏数据上裸奔;`TORCH_NCCL_BLOCKING_WAIT=1` 改为阻塞等待。
  watchdog 线程本体在 C++ ProcessGroupNCCL 侧(Python 只负责传 timeout),
  `set_timeout`(L2311-2355)可运行时改 PG 与后端 options 的超时。
- **store 超时**:_store_based_barrier 的 rendezvous 超时(§2)。
- **monitored_barrier 超时**:点名式报告(§5)。

**destroy_process_group (L3123-3235)** 的两个工程细节:先 `pg._wait_for_pending_
works()` 等 Python onCompletion hooks 跑完(L3150-3159)——解释器退出后 hook 线程
抢 GIL 会 crash;全量销毁时**按组名倒序 shutdown**(L3166-3171),因为某些 NCCL
版本里 `ncclCommAbort()` 是 collective,乱序会死锁。销毁后 `_world` 各表清空、
`group_count` 归零(L3184-3192,为容错恢复后重建留干净现场)。

## 8. 值得记住的惯用法

1. **`_world` 单例做全局账本**:L1277-1287 顶格注释 "DO NOT USE THESE FIELDS
   DIRECTLY"——`_pg_map/_pg_names/_pg_group_ranks` 等本就是模块级 dict,
   `_World` 类(L1290-1433)用 property 把它们包成 `_world.pg_map` 风格访问,
   L1436 注释明说这是"experimental extension point to override it"——留出整个
   替换状态管理的口子。
2. **哨兵值代替异常**:`GroupMember.NON_GROUP_MEMBER = -100`(Literal 类型别名
   L434)贯穿所有建组 API——"不是成员"是正常控制流,不是错误。
3. **GroupName 是身份,PG 是实体**:名字进 C++ 注册表可 pickle/可跨 compile 边界,
   实体只在进程内存活。
4. **PrefixStore 套娃**:`default_pg` → `{group_name}/` → `{device}/`,一个
   TCPStore 服务所有组的 rendezvous,靠前缀分区。
5. **全员到达(collective 建组)+ 静默跳过(warning)**:分布式正确性的第一公理
   在 API 形状上的投影。
6. **新边疆已在文件尾部**:`_reconfigure`(L8120+,fault tolerance,基于 handle
   的 communicator 重建)与 `_new_window`(L8178+,one-sided RMA)——塔基还在生长。

---

**读码路线**:init_process_group → _new_process_group_helper → all_reduce →
_new_group_with_tag → _register_pg_in_world,五站走完,8200 行的骨架就握在手里了;
剩下的 7000 行是同一模式在 20+ 个 collective 上的展开。
