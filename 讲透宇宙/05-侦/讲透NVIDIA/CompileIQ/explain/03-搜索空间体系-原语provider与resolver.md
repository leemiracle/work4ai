# 03 · 搜索空间体系：原语、加密 provider 与 resolver

## 角色定位
`compileiq/search_spaces/`（5 个模块：base.py 185 行 / compilers.py 102 行 / models.py 110 行 / manifest.py 144 行 / resolver.py 423 行）回答一个问题：**搜索在什么域上进行**。它分三层——用户可见的原语、NVIDIA 资产化的加密 provider、把远程资产落到本地的 resolver。

## 内部结构
原语层只有四个构造函数：`range`（`base.py:12`）、`choice`（`base.py:83`）、`literal`（`base.py:124`）、`log_sampling`（`base.py:157`），全部返回 `models.py` 的 Pydantic 配置对象（`RangeParamConfig` 等）。**`range` 刻意遮蔽 Python 内建名**——惯用法 `from compileiq.search_spaces import range`，语义是闭区间（`range(0,8,2)` 产生 `[0,2,4,6,8]`，`base.py:20-22` docstring），并扩展了 `knockout_prob`/`seed_low`/`seed_high` 三个编译器调优特有参数。provider 层：`SearchSpaceProvider` 是 Protocol（`compilers.py:21`，`retrieve() -> dict | pathlib.Path`）；`CompilerSearchSpaceBase`（`compilers.py:32`）承载 GitHub-release 加密空间；`PtxasSearchSpace`（`compilers.py:66`）与 `NvccSearchSpace`（`compilers.py:75`）是两个具体实现；`LocalSearchSpaceBin`（`compilers.py:84`，`retrieve` 在 `compilers.py:101`）走本地 .bin。

## 外部连接
下游被 `Search` 的 `_do_setup`（`ciq.py:523`）解析消费；发布侧由 `schemas/search-space-manifest-v1.schema.json` 约束目录结构，`manifest.py` 的 `SearchSpaceManifestModel`（`manifest.py:75`，`extra="forbid"`，重复选择器拒绝 `manifest.py:92`）是运行时镜像；dev 层 `build_search_space_release.py` 等脚本按同一 schema 出资产。

## 数据流
用户给 provider（或原语 dict）→ resolver 解析：latest-tag 三级容错 → 下载 .bin → sha256+size 校验 → 落 `~/.cache/compileiq/<tag>/`（`_cache_root`，`resolver.py:104`）→ 返回路径/字典给 Search。hub 级入口 `resolve_with_metadata` 顺带带回溯源元数据（tracker 记账用）。

## 设计决策
**latest-tag 三级缓存**是 resolver 的灵魂：(1) 进程内 `@functools.lru_cache(maxsize=8)`（`resolver.py:223-224`）；(2) 磁盘缓存带 TTL，默认 7 天、`CIQ_SS_LATEST_TTL_DAYS` 可调（`resolver.py:54-55`），缓存键为 repo+tag_prefix 哈希（`resolver.py:132-135`）；(3) GitHub 失败时**回退过期缓存**并告警（`resolver.py:241-248`）——离线可用的代价是可能拿到旧 tag，所以告警不静默。第二个甄别点：**LocalSearchSpaceBin 是协议独立实现**，不是 `CompilerSearchSpaceBase` 子类——两个 provider 体系只共享 Protocol，不共享基类；判断"能不能当 provider 用"看结构类型而非继承。加密 .bin + manifest 校验的动机：控制项合法域是随编译器版本演进的 NVIDIA 资产，发布在 Release 而非硬编码，前端可引用最新域又不暴露明文。

## 新人提示
写自定义空间从 base.py 四原语拼装即可；离线/内网环境直接 `LocalSearchSpaceBin(path=...)`（`compilers.py:9` docstring 即此建议）。缓存排查入口：`make clean-search-cache`（清 `~/.cache/compileiq/`）。
