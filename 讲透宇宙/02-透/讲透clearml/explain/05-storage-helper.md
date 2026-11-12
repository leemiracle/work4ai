# 05 · Storage 五协议驱动——clearml/storage/helper.py（4804 行）

## ① 角色定位

helper.py 是 ClearML SDK 里**所有远程文件 I/O 的唯一网关**：artifact 上传下载、模型权重、数据集分块、调试样本图最终都收敛到这里。它把五种存储协议——本地 `file://`、HTTP(S)、S3（含一切 boto3 兼容对象存储）、`gs://`、`azure://`——统一进一个 `StorageHelper` 门面，上层（Artifacts、Model、Dataset、Logger）只认 URL 不感知协议。4804 行是 SDK 最大单文件，"helper"是谦辞：它是驱动层+门面层+缓存层三层叠放。

## ② 内部结构

**驱动层（继承 `_Driver` ABC，helper.py:109）**，契约方法 `get_container`/`upload_object_via_stream`/`list_container_objects`/`download_object`/`delete_object`/`test_upload`：

- `_HttpDriver`（helper.py:239，`schemes=("http","https")` 在 helper.py:247）：基于带重试的 requests session；只读——`list_container_objects`（helper.py:376）与 `delete_object`（helper.py:379）对 HTTP 不支持。
- `_Boto3Driver`（helper.py:592，`scheme="s3"` 在 helper.py:611）：最重的驱动，线程池流式下载（helper.py:650）、凭据探测 `_test_bucket_config`（helper.py:939）。
- `_GoogleCloudStorageDriver`（helper.py:1076，scheme 在 helper.py:1085）。
- `_AzureBlobServiceStorageDriver`（helper.py:1286，scheme 在 helper.py:1287），blob 名反解在 helper.py:1747。
- `_FileStorageDriver`（helper.py:1794，scheme 在 helper.py:1799）：唯一支持建容器/枚举容器的驱动。

`_Stream`（helper.py:492）把迭代器包装成 file-like 对象供流式 API 互通。

**门面层 `_StorageHelper`（helper.py:2372）**：三套桶配置全部 `deferred_config` 惰性读 clearml.conf——`_s3_configurations`（helper.py:2484，key `aws.s3`）、`_gs_configurations`（helper.py:2485，`google.storage`）、`_azure_configurations`（helper.py:2486，`azure.storage`）。工厂 `get()`（helper.py:2506）以 `base_url+线程id` 做实例缓存键（helper.py:2517）。`__init__`（helper.py:2565）做 **5 路 if/elif 协议分派**：azure（helper.py:2607）→ s3（helper.py:2626）→ gs（helper.py:2655）→ http(s)（helper.py:2660）→ 兜底本地驱动（helper.py:2668）。操作面：`upload_from_stream`（helper.py:3023）、`download_to_file`（helper.py:3197）、`download_as_stream`（helper.py:3360）、直通访问 `get_driver_direct_access`（helper.py:3449）、路径替换 `add_path_substitution`（helper.py:2835）。上传走异步线程池：`_initialize_upload_pool`（helper.py:3689）→ `_do_upload`（helper.py:3594）。

**缓存层 `StorageHelper`（helper.py:3774，继承门面）**：内嵌 `CacheConfigs`（helper.py:3781），默认磁盘水位 `cache_size_min_free_bytes="10GB"`（helper.py:3799）；`init_configs`（helper.py:3871）初始化 local+secondary 两缓存（环境变量 `CLEARML_SECONDARY_CACHE_DIR` 在 helper.py:3723）；重写 `download_to_file`（helper.py:4035）与 `download_as_stream`（helper.py:3990）走 `_multi_cache_download` 多级缓存。变体 `StorageHelperDiskSpaceFileSizeStrategy`（helper.py:4646）。模块尾导出协议集合 `driver_schemes`/`remote_driver_schemes`/`cloud_driver_schemes`（helper.py:4793/4803/4804）。

## ③ 外部连接（图谱证据）

图谱中 helper.py 节点带 64 条边：入边来自 storage/cache.py、storage/manager.py；出边指向 bucket_config.py（凭据对象）、callbacks.py（上传/下载进度回调）、storage/hashing.py（sha256sum）、config.py、errors.py。跨子系统关键边：helper.py:61 `from clearml.utilities.requests_toolbelt import MultipartEncoderMonitor`——S3/HTTP 流式 multipart 上传用的是**内嵌副本**（详见 08 篇）。contains/exports 边覆盖上述全部驱动类与 StorageHelper。

## ④ 数据流

**上传**：`Artifacts.upload_artifact`（binding/artifacts.py:498）序列化对象 → `StorageHelper.get(url)`（URL 规整 `_canonize_url`+路径替换 helper.py:3464 → scheme 分派选驱动）→ `verify_upload` 验凭据（S3 走 `_test_bucket_config`，helper.py:3005）→ 任务入上传线程池 → 驱动 `upload_object_via_stream` 落桶，进度经 vendored MultipartEncoderMonitor 回调。**下载**：`download_to_file` 先查 `get_driver_direct_access`（file:// 直接返回本地路径零拷贝）→ 缓存版查 `cache_matchers`（默认 `[{"url":"*"}]` 全命中，helper.py:3802）→ miss 则驱动层下载（S3 分块并发）→ 写入 `<cache_dir>/storage/<url_path>` 镜像结构 → 磁盘超水位由单线程 ThreadPoolExecutor 后台清理（helper.py:3937）。

## ⑤ 设计决策

1. **驱动 ABC+门面单例**：五协议一份契约，上层零感知；协议差异压缩在驱动层，门面逻辑协议无关——代价是这个巨型文件。
2. **实例缓存键含线程 id**（helper.py:2517）：免锁线程隔离，副作用是每线程各持一份 boto3 资源。
3. **deferred_config 惰性读**：clearml.conf 可 import 后才写入，凭据解析延迟到首次使用。
4. **缓存用继承而非组合**，于是有 `_legacy_cache_override`（helper.py:3884）防御补丁：老 allegroai SDK 子类化时 `super().download_to_file()` 会绕回子类缓存造成无限递归，docstring 明言磁盘策略必须让位——历史兼容的化石。
5. **热路径性能**：`fast_urlsplit`（helper.py:3753）手写 URL 切分，注释明言不引入 urllib。
6. **重依赖全可选**：azure SDK try-import 探测（helper.py:86-100），boto3 延迟 import——没装云 SDK 时 file/http 照常。

## ⑥ 新人提示（含勘误）

- **勘误 1**："StorageHelper"有三个形态——`_StorageHelper`（helper.py:2372 无缓存基类）、`StorageHelper`（helper.py:3774 带缓存，实际入口）、`StorageHelperDiskSpaceFileSizeStrategy`（helper.py:4646）。grep 会三处命中，别混。
- **勘误 2**：协议分派是**硬编码 if/elif**（helper.py:2607-2668）不是注册表——新增协议必须改 `__init__`，只写驱动类路由不到。
- **勘误 3**：未识别 scheme **不报错**，静默走本地文件驱动（helper.py:2668 else 分支）——`weird://foo/bar` 被当相对路径，排查"下不到文件"先查 scheme 拼写。
- HTTP 驱动不支持列目录/删除（helper.py:376/379）。
- 桶配置层级是 `aws.s3`/`google.storage`/`azure.storage` 三段（helper.py:2484-2486），不是统一 `storage.*`。
- 多线程各持实例：凭据热更后老线程可能用旧配置，必要时传 `__force_create=True`（helper.py:2530）。

---
**自检报告**：不计空格字符 4383；汉字 799+英文词 343；行号锚 57 个（helper.py:109/239/247/592/611/2372/2484-2486/2506/2607-2668/3197/3774/3884/4035/4646 等，均 grep -n 核实）。
