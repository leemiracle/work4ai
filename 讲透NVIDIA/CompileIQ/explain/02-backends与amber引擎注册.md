# 02 · backends 与 amber：entry-point 注册的引擎世界

## 角色定位
`compileiq/backends.py`（451 行）是前端的引擎抽象层：定义引擎怎么被选中、怎么被发现、必须实现什么。CompileIQ 1.1 的架构分水岭就在这里——编译版 NSGA-III 运行时 `amber` 经 entry point 注册**取代了原 socket IPC 搜索核心**（`docs/install.md:14`），前端与引擎从此同进程。

## 内部结构
三件套：`EngineConfig`（`backends.py:27`，frozen Pydantic）选引擎；`SearchBackend` ABC（`backends.py:165`）规定 `ask`/`tell`/`checkpoint`/`restore`/`is_complete` 等契约；注册发现链 `register_backend`（`backends.py:289`）→ `_load_entry_point_backends`（`backends.py:326`）→ `importlib.metadata.entry_points()` 按 group `"compileiq.backends"` 过滤（`backends.py:339-341`）→ `create_backend`（`backends.py:391`）实例化。错误体系分层：`BackendNotFoundError`/`BackendCapabilityError`/`SearchSpaceExhaustedError`（`backends.py:50-82`）。

## 外部连接
amber 以二进制 wheel 形态存在：`native-runtime-wheels/` 是 4 Python（cp311-314）× 4 平台（linux x86_64/aarch64、macosx_15 arm64、win amd64）的 **16 格矩阵**，每格一份 manifest json。manifest 三级溯源：`outputs`（filename/sha256/size）+ `provenance`（job_id/pipeline_id/source_commit）+ `runtime`（abi/python/platform/wheel 标签组）+ schema_version——任何一格都能追到构建它的 CI 作业与源提交。注意 whl 是 Git LFS 指针（`.gitattributes` filter=lfs），clone 后必须 `git lfs pull`。

## 数据流
Search 构造 → 解析引擎名 → entry-point 发现 → registrar 调 `register_backend` → `create_backend` 进程内建实例 → ask/tell 直接方法调用（无 IPC）。源码 checkout 场景由 `dev/materialize_native_runtime.py` 在 16 格中按主机**唯一匹配**物化（`_select_runtime_artifact`，`materialize_native_runtime.py:97`），且 `_reject_lfs_pointer`（`materialize_native_runtime.py:29`）显式拒绝把 LFS 指针当真轮子。

## 设计决策
entry-point 注册取代 socket IPC 的收益：去掉序列化往返、部署面收敛为"一个包一个平台标签"。代价是平台标签绑死，换来 `dev/compose_compileiq_wheel.py` 的 "one distribution one platform tag" 硬约束（`compose_wheel`，`compose_compileiq_wheel.py:236`；manylinux 归一 `_normalize_wheel_tag:64`；entry points 合并 `_parse_entry_points:177`）。文档化行为差异：`amber` 从不重复候选（`docs/install.md:18`），小搜索空间会提前触发空间耗尽异常。ACF 合并的原生绑定在 `compileiq/utils/_libciq.py`：ctypes 声明 `merge_controls` 的 restype/argtypes（`_libciq.py:78-89`），错误码经 `MERGE_ERRORS`（`_libciq.py:30`）映射为 Python 异常，**库侧结果缓冲合并后必须显式 `library.free_buffer(result)` 释放**（`_libciq.py:187`）——手动缓冲管理是这类 C 边界的纪律点。

## 新人提示
排障顺序：先确认 amber 装了没有（`pip show compileiq-native-runtime` 或看 `make materialize-native-runtime` 输出），再看 entry point 是否注册（失败信息会点名 registrar 路径）。开发自编 libciq 用 `CIQ_LIBCIQ_PATH`（`_libciq.py:25`，`load_libciq` 在 `_libciq.py:98`）。
