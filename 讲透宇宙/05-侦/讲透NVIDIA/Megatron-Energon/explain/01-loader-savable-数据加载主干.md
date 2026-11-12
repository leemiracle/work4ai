# 01 · loader.py 与 savable_loader.py：数据加载主干与断点续训状态机

## 角色定位

flavors（格式）与 wrappers（变换）构成 Energon 的"数据集树"，`loader.py` 与 `savable_loader.py` 是驱动器：把 `SavableDataset` 树跑起来喂给 Megatron 训练循环，并维护"数据侧可恢复"承诺。`loader.py` 仅 122 行用户门面——`get_savable_loader`（loader.py:16）产出支持存档的 `SavableDataLoader`，`get_loader`（loader.py:79）产出无存档的 `BasicDataLoader`（val/eval 用）。复杂度全部沉淀在 1474 行的 `savable_loader.py`：多进程命令通道、周期 checkpoint、跨 rank 聚合与回退重放式恢复协议。

根本矛盾：PyTorch 多进程 DataLoader 的迭代状态对主进程是黑盒，而千卡断点恢复要求每 rank 精确到样本。Energon 不依赖 torch 内部状态，自建可序列化状态机。

## 内部结构

四组构件自底向上：

1. 状态载体（edataclass）：`SavableDatasetState`（savable_loader.py:178）= 全系统随机态 + 整树递归状态（`FlexState` 即纯 dict 别名，state.py:5）+ sample_index；`SavableCheckpoint`（:195）加时间戳；`SavableDataLoaderState`（:619）是含全部 worker 状态的 loader 级封包。
2. 迭代包装器：`SimpleSavableDatasetWrapper`（:86）用于零 worker 路径，`__iter__`（:124）是"重启式"循环，`_state_restored` 标志让 restore 后整轮重来；`SavableDatasetWrapper`（:220）是多进程灵魂，兼具 IterableDataset 与 RPC 服务端身份。
3. 两个 DataLoader（:633/:1251）继承 torch DataLoader，batch_size=None、shuffle=False（:821）——批组装与打乱全由数据集树完成，loader 只解包 `(worker_id, sample_index, sample)` 三元组（:883）；`_close_data_loader`（:52）按序释放迭代器/workers/数据集。

装配链在 `__init__`（:709）：数据集先套 WatchdogDataset（:755 看门狗）再套 GcDataset（:764 周期 gc 控内存），然后有 worker 走 SavableDatasetWrapper（:785），无 worker 走 Simple（:796）。

## 外部连接

- Megatron 训练循环：周期调 `save_state_global`（:1094）只在主 rank 落盘，重启时各 rank `restore_state_global`（:1160）；旧名经 @deprecated 转发（:1084）。
- torch.distributed：gather_object 收集（:1137）、scatter_object_list 广播（:1221），尊重 `worker_config.data_parallel_group`（:1126 处理跨组边界）。
- WorkerConfig：worker 种子（:817）、`worker_id_offset` 轮转（:365）来自它；取样本前后 worker_activate/deactivate（:401）切换激活态供缓存池感知。
- wrappers 的 gc/watchdog 以 loader 为唯一默认挂载点；base_dataset 的 add_sample_restore_key 给每样本打 `("SavableDatasetWrapper", global_worker_id, sample_index)` 根键（:423）。

## 数据流

多进程模式单样本旅程：

1. worker 进程内 `__iter__`（:363）先起命令线程（:368 daemon+weakref.proxy 防泄漏），恢复待恢复态（:383）或存初始 checkpoint（:395）。
2. 主循环迭代内层（:406），先按 `_workers_skip_samples` 跳过恢复点后已产出样本（:410），打 restore 键（:423）、推进索引、存 checkpoint（:427）。
3. 关键并发窗口：yield 前释放 `_command_lock`（:429）、yield 后重获（:437）——get_checkpoint 命令只能在"样本已产出、不在途取数"的安全点插入。
4. 样本经 torch 内部队列到主进程 `_epoch_iter`（:868）：`_worker_sample_counters`（:884）记录各 worker 最后样本号，`_next_worker_id`（:886）补偿 torch 无法恢复 worker 轮转次序的缺陷（:658）。
5. 保存：`save_state_rank`（:971）经 `_worker_command`（:940）广播-收集，让每 worker 从 `_last_checkpoints` 环形历史找"sample_index ≤ 请求值"的最近点（:510），返回状态+offset。
6. 恢复：`restore_state_rank`（:1007）拆回各 worker 的 restore_from/skip_samples（:537），重启后先 restore 再按偏移跳；micro batch size 变更规则见 :1039-1063。

checkpoint 节流（:455）：距上次超默认 60s 且样本增量达 workers×2 才存，保留 n_checkpoints 份（默认 prefetch×workers+1，:778）；:811 断言强制 checkpoint 历史深度 ≥ 在途样本数，否则最老 checkpoint 追不上预取队列、恢复必丢数据——全文件最核心的不变量。

## 设计决策

- 绕开 torch 迭代器状态：类 docstring（:647）记录完整推导——在途样本使状态不可直接读取，故"定期存过去时态 checkpoint + 记录各 worker 最后样本号 + 恢复时回退+跳过"。代价是恢复要重放至多一个间隔的样本。
- 命令线程 weakref+RLock（:297）：命令须在 worker 进程执行（状态只在那边完整），而 worker 阻塞在取数上；独立线程+"仅 yield 窗口持锁"使 get_checkpoint 与取数互不阻塞。
- rank 级/global 级双 API：save_state_rank 不依赖 torch distributed、单进程可测，global 只是套 gather/scatter；BasicDataLoader 复用 Simple 包装但只留 restore_sample 调试入口（:1438）。
- fork 而非 spawn（:807）+ persistent_workers（:804）摊平创建成本，fork 前 gc.collect()（:1329）防旧 worker 引用带进子进程。

## 新人提示

1. worker_config 建数据集时传，loader 只校验并告弃用（loader.py:54-63）。
2. loader 拥有读取资源：记得 close() 或 with（loader.py:52）；watchdog 默认 60s（loader.py:85），首迭代慢可用 watchdog_initial_timeout_seconds 放宽。
3. 改 prefetch_factor 必须同步加 n_checkpoints（:811 是安全下限）；断点不匹配先查 `config()` 指纹（:1238），micro batch size 只能等比缩小（:1045）。
4. 排查恢复后样本重复/丢失：自定义 wrapper 必须正确实现 save_state/restore_state（基类按 _savable_fields 反射收集，base_dataset.py:263）；自定义 RNG 挂进 SystemRng 才能被存档（:496 兜底）。
5. `restore_sample`（:1234）是独立于 checkpoint 的单样本调试通道，键来自样本 `__restore_key__`，要求全链路确定性。
