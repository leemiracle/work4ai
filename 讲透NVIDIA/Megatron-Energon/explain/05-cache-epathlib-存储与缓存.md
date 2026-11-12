# 05 · cache 与 epathlib：存储抽象与本地缓存

## 角色定位

这两个子包是 Energon 的"脚下层"：`epathlib/` 把本地路径与远程对象存储（S3/GCS/Azure，经 NVIDIA Multi-Storage Client）统一成类 pathlib 的 `EPath`；`cache/` 在其上提供 `FileStore`（按键随机读数据集的抽象）与 `FileStoreCachePool`（本地 SSD 预取缓存池）。训练时 DataLoader 的 worker 经 worker.py:84-98 把 CachePool 注入 WorkerConfig 类变量，样本字段的惰性加载最终都落回这两个子包。相邻 top-level 模块 `local_copy.py`（远程文件本地化）与 `retry_stream.py`（容错读流）是同一条存储线的配件。

## 内部结构

cache/ 三层分工：`base.py` 定协议——`FileStore` 只需 `__getitem__` 返回 `(数据, SourceInfo)` 与 `get_path()`（base.py:14-48），`FileStoreWrapper` 的 `_get_raw/_decode_raw` 把"原始字节缓存+访问时解码"拆成两步（base.py:62-74）；`file_store.py` 给实现：`SystemFileStore` 直读文件系统、`DecodeFileStore` 包装解码，media 元数据从 index.sqlite 以只读 URI 打开（file_store.py:98）；`file_cache_pool.py` 是核心池，`no_cache.py` 的 `NoCachePool` 提供恒等直通对照。

epathlib/ 的 `EPath` 用 `__slots__` 持三态：POSIX 内部路径、MSC profile 名、StorageClient（epath.py:48）。构造按 `_split_protocol` 正则（epath.py:148）拆 `protocol://profile/path`，支持 msc:// 与 dss://（epath.py:84-94），rclone:// 已标废弃（epath.py:82-83）。`mapped_array.py` 两实现：本地走 `np.memmap`（mapped_array.py:157-163），远程走 seek/read 逐元素取（mapped_array.py:102-109），由 `map_epath` 按 `use_mmap and (is_local or copy_to_local)` 分派（mapped_array.py:188）。

## 外部连接

消费方遍布全仓：webdataset/jsonl/binidx 各 flavor 的 FileStore 经 file_store.py:117-130 的**模块级 `__getattr__`（PEP 562）惰性导入**——`WebdatasetFileStore` 等重量级类只在首次访问时 import，既打破 flavors→cache→flavors 的循环依赖又压低 import 开销，是 PEP 562 的教科书用法。`flavors/webdataset/itar.py:387` 用 `RetryReadStream` 容错读 tar。

## 数据流

一次 `get_lazy(ds, fname)`：以 `(ds.get_path(), fname)` 为键查 `_pending_tasks`，已有条目则 refcount+=1 共享同一 Future，否则提交 `_cache_out_task`（file_cache_pool.py:338-364）。后台任务先读数据（raw/pickle 两模式），再在 `_cache_space_available` 条件变量上**等空间**——超 max_cache_size/count 即挂起（file_cache_pool.py:295-303）；等待中被置 `require_data_now` 或池在关闭则放弃缓存返回 False。`FileCacheLazy.get()` 的五分支语义写在 `_get_data` docstring（file_cache_pool.py:216-226）：任务未启动→取消并直读；已跑→放锁等待、完成后从缓存读；等空间中→直读绕过缓存；失败→异常透传且保留给其他引用；被取消且还有引用→**重新入队**（file_cache_pool.py:266-273）。refcount 归零即删缓存文件并唤醒等待线程（file_cache_pool.py:389-455）。

## 设计决策

三个决策值得咀嚼。其一，**淘汰是引用计数而非 LRU**：缓存生命周期与样本生命周期绑定，样本消费完文件即删，容量压力来自并发在途样本数——默认 max_cache_count=10M（file_cache_pool.py:166）几乎不设限，真正闸门是默认 1024GB 容量。其二，**fork 安全靠随机目录+池重建**：`__before_fork__` 断言无 pending 任务并关闭线程池（file_cache_pool.py:457-465），`__after_fork__` 用 `os.getpid() ^ random` 播种生成随机后缀目录——注释点明全局 random 会被 fork 克隆、须混入 pid（file_cache_pool.py:473-486）。其三，**EPath 序列化刻意丢弃 fs**：`__getstate__` 只存路径与 profile，注释明言"避免泄漏凭据"（epath.py:105-110），`__setstate__` 时重解析客户端（epath.py:112-122）——StorageClient 含 AK/SK，pickle 落盘或跨进程传输都不该带上。另有一个**疑似 bug**：retry_stream.py 的 `read()` 在重试间用 `buf += res` 累积（retry_stream.py:46），完成时却 `return res` 只返回最后一段（retry_stream.py:52）——若首次读中途 IOError 后重开文件续读，出错前已读字节将被丢弃，正确应 return buf；目前 itar.py 是唯一消费方，调用模式可能恰好掩盖它。

## 新人提示

读 cache 必看 tests/test_file_cache_pool.py 测试矩阵：`MockFileStore` 是最小 FileStore 假实现（test_file_cache_pool.py:17-33）；`test_shared_references` 验证共享引用——两次 get_lazy 得同一 entry、refcount==2，都 get 后归零且缓存目录清空（test_file_cache_pool.py:149-171）；`test_cache_size_management` 是状态机式测试：75KB 容量配 6 个 25/50KB 文件，逐点断言每步后各 lazy 的 refcount 与 pending/cached/consumed 三态（test_file_cache_pool.py:224-301），注释里的 `Queue state: [...] cached out: [...] removed: [...]` 是理解淘汰时序的最佳材料。epathlib 侧改路径解析先跑 test_epathlib.py 的 `test_s3_glob_walk`（test_epathlib.py:200）。S3 测试走 `tests/s3_emulator/`——纯 stdlib 的 S3 兼容服务（ThreadingHTTPServer，server.py:69-73），其 `S3Auth` 自称"AWS Signature V4 极小子集"（auth.py:20-26）：实现四级 HMAC 签名链（auth.py:117-121）与 canonical 规范化（auth.py:179-212），但明言不支持 chunked upload 与 presigned URL；emulator 由 `setup_s3_emulator`（epath_s3_emulator.py:14-84）起随机端口并写 rclone 配置，其全局改写 HOME 的 hack 见 06 篇。注意 EPath 的 `mkdir()` 是 no-op（epath.py:312-313）——对象存储无目录概念。
