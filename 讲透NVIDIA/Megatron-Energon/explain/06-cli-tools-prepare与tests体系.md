# 06 · cli/tools 命令行层与 tests 体系

## 角色定位

`cli/main.py` 与 `tools/` 合成 `energon` 命令行：click group 注册七个子命令——prepare/prepare_media/preview/info/mount/checkpoint/analyze_debug（main.py:53-59）。prepare 为 webdataset 建 index.sqlite 与 dataset.yaml，mount 挂只读 FUSE，checkpoint 做 checkpoint 重分片；test_dataset_det.py（1082 行）是顺序确定性总验收，test_webdataset_prepare.py 验证建库批处理——守住可复现训练顺序、可重复建库两条承诺。

## 内部结构

tools/prepare.py 是 600 行**交互式向导**：`get_dataset_type` 先路由（prepare.py:238-262）——RECIPE 转 prepare_recipe、JSONL 直建、BINIDX 免准备、FILESYSTEM 拒绝并指向 prepare-media，剩下才是 webdataset 主流程。交互链：提示输入 split（prepare.py:317-320）→ 列出 part 类型，超过 10 种禁用交互 field_map（prepare.py:386-393）→ 用 `inspect.getmembers` 枚举 megatron.energon 全部 Sample 子类供编号选择（prepare.py:410-446），选中后 `inspect.getsource` 打印类源码（prepare.py:461-462）→ 逐字段问 field_map，支持 `json[field]` 取子键与 `jpg,png` 备选语法（prepare.py:508-554）→ 或生成带 TODO 的 sample_loader.py 模板（prepare.py:45-77，写入于 575-588）→ 落 dataset.yaml（prepare.py:590-592）。

tools/mount.py 的 `_EnergonFS(Operations)` 是 315 行 FUSE 实现，**整个类定义在 `try: from mfusepy import ...` 块内**（mount.py:22-344），mfusepy 缺席则 `EnergonFS = None` 静默降级。tools/checkpoint.py 围绕 `natural_sort_key`（checkpoint.py:14-21）做文件名数字模式识别，redist/info 双命令挂 command group（checkpoint.py:216-230）。tar_patcher 实际在 flavors/webdataset/tar_patcher.py：开头 `try: import numba except ImportError: raise ImportError("numba is required...")`（tar_patcher.py:21-27）是**穿 try 外衣的硬依赖**——except 立即重抛，`HAS_NUMBA = True`（tar_patcher.py:25）从此无人读取成死标志；模块含十余个手写签名 @njit 内核（类型别名 tar_patcher.py:29-34）与自带 click 组（tar_patcher.py:683-764）。

## 外部连接

prepare 的落点是 `BaseWebdatasetFactory.prepare_dataset`（prepare.py:355-367）；--fix-duplicates 时由 flavors/webdataset/prepare.py:552-570 动态 import TarPatcher 跑 dataset_scan→dataset_apply_prefix。checkpoint 的 command_redist 被 test_dataset_det.py:31 直接 import——CLI 与测试共享同一实现。

## 数据流

prepare 全流程：glob 全部 tar/tgz（prepare.py:284）→ 排除 regex → 多 worker 建索引 → 打印首尾 shard 与样本预览（prepare.py:373-384）→ 交互生成 dataset.yaml。mount 是"open 即全量入内存"：open 读整个 part 进 `_open_files` 返回哑 fd，read 只做内存切片，release 丢弃缓冲（mount.py:266-333）——简单但大文件撑内存；老数据集缺表退 slow_mode（mount.py:49-58），同 key 跨多 tar 以 MULTI_WARN 哨兵警示（mount.py:16/141-148）。tar_patcher 用 `np.memmap(mode="r+")` 原地改 tar 头，扫描遇"duplicates+不兼容"提前终止（tar_patcher.py:540-547）。

## 设计决策

其一，**确定性是测出来的产品特性**：test_dataset_det.py:233-306 验证同一 dataset 两次 fork 的 loader 序列完全相等（order4==order6）、不同 seed_offset/num_workers 则不同，并断言样本出现次数落 ±20% 区间；test_invariance_global_samples（test_dataset_det.py:751 起）固定全局 batch size，改变 world_size×num_workers 划分（1×4/2×2/4×1）后全局样本序不变。其二，**测试基建敢碰私有 API**：直接改 `torch.utils.data._utils.worker.MP_STATUS_CHECK_INTERVAL = 0.1` 加速坏 worker 检测（test_dataset_det.py:35-40）；setup_s3_emulator 更激进——全局改写 `os.environ["HOME"]` 与 XDG_CONFIG_HOME 且不恢复（epath_s3_emulator.py:69-70），再 `read_rclone_config.cache_clear()` 打掉 MSC 的 lru_cache（epath_s3_emulator.py:73），docstring 为此要求每个测试用不同 profile_name 防缓存串味（epath_s3_emulator.py:32-33）。**勘误两则**：test_dataset_det.py:42-56 的 `_norng_state` 摘要器当前树里只有定义与自递归、无调用点，是旧调试代码遗落的死助手；mount 的 try 块内类定义是 tree-sitter 已知盲区（条件上下文中的 315 行类），图谱中 `_EnergonFS` 节点系批分析人工补扫救回——引用该类以源码行号为准。

## 新人提示

`energon prepare` 的选项注释（prepare.py:93-192）比文档准确，先读它。测试入口顺序：test_webdataset_prepare.py 的 `BatchCollector`（test_webdataset_prepare.py:18-28）是最小 BaseAggregator——只收集批次列表，85 行验证两个关键语义：SqliteIndexWriter 遇重复 sample_key 抛 DuplicateSampleKeyError 且**整批回滚**（row_count==0，test_webdataset_prepare.py:38-65）；AggregatorPool 按 batch_size=2 切批 worker 输出（`[[1,2],[3],[4,5]]`，test_webdataset_prepare.py:67-82）。改 loader/savable 必跑 test_dataset_det.py 全部 11 个 test：restore_state_workers 真开多进程验证 checkpoint 恢复，determinism_taskencoder_save_restore 用 `@stateless(restore_seeds=True)` 验 TaskEncoder 随机数保存（test_dataset_det.py:306-425）。注意 S3 测试一旦运行，进程内 HOME 已被换掉——依赖真实 HOME 的测试须排在其前或自管环境。
