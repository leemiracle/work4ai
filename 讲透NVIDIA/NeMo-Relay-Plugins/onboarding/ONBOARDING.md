# NeMo-Relay-Plugins Onboarding

> 知识图谱（276 节点/441 边/11 层）+ 源码核实，commit `115b2ae8`。

## 1. 仓库定位：插件联邦的四种角色

本仓为 [NVIDIA NeMo Relay](https://github.com/NVIDIA/NeMo-Relay) 构建并发布插件。`plugins/` 下每个目录是独立插件，有自己的版本、平台、依赖与工件（`README.md:8-11`）。四个插件构成"三示例 + 一生产"的联邦（`README.md:17-22`）：

| 插件 | Relay plugin ID | 形态 | 职责 |
| --- | --- | --- | --- |
| switchyard-plugin | `nvidia.switchyard` | native 共享库 | 把受支持模型请求经 Switchyard 部署路由 |
| example-python-grpc-worker-plugin | `examples.python_grpc_worker` | worker 进程 | Python 全钩子教学范式 |
| example-rust-grpc-worker-plugin | `examples.rust_grpc_worker` | worker 进程 | Rust 逐钩子对应实现 |
| example-rust-native-plugin | `examples.rust_native_policy` | native 共享库 | 进程内中间件能力面全景 |



仓本体几乎不含运行时代码：三示例约 1.5k 行，Switchyard 代码在另一仓（§7）；主体是 `scripts/` 工具链（约 4.3k 行）与许可归属机器。Rust 插件支持全七平台，Python worker 只声明四平台（`plugins/example-python-grpc-worker-plugin/release.toml:8`）。

## 2. AGENTS.md：AI 协作开发宪法

`AGENTS.md` 是面向 AI 代理与贡献者的十条铁律（`AGENTS.md:8-18`），按边界分五类：

- **社交边界**：未经明确批准不得回应 PR/MR/issue（`AGENTS.md:8`）。
- **归属权边界**：插件命令、打包、冒烟测试留在各自目录；共享脚本禁止按插件名分支、禁止含任何插件的包名或输出文件名（`AGENTS.md:10`）——仓库最核心的架构约束，`scripts/tasks.py:5` docstring"no plugin registry or recipes"是其落地。
- **质量边界**：Rust 一律 release 模式构建测试（`AGENTS.md:14`，含测试加载插件的构建）；不跳过平台测试、不自动发布草稿（`AGENTS.md:15`）。
- **供应链边界**：外部 Action 钉完整 commit SHA 并注释记录 tag（`AGENTS.md:16`，实例 `.github/workflows/plugins.yml:33`）；Python 用最低支持版 3.11（`AGENTS.md:17`）。
- **文档边界**：面向高中读者写作，许可声明逐字保留（`AGENTS.md:18`）。

## 3. 插件双形态：native 共享库 vs worker 进程

**worker 是独立进程，native 是加载进 Relay 进程的库**（`README.md:24-27`）。对照：

- **native**（rust_dynamic）：产物是 `.so/.dll/.dylib`，manifest 用 `load.library + load.symbol` 声明加载目标与注册符号 `nemo_relay_register_plugin`（`plugins/example-rust-native-plugin/relay-plugin.toml:30-35`）；代码直接在 Relay 线程池执行（示例声明 2 线程执行器，`plugins/example-rust-native-plugin/src/lib.rs:30-32`）。
- **worker**（grpc-v1）：Python worker 走 `load.runtime="python" + entrypoint`（`plugins/example-python-grpc-worker-plugin/relay-plugin.toml:30-31`），Relay 建 Python 环境并拉起独立进程经 gRPC 通信；Rust worker 是独立可执行文件。worker 崩溃不连累 Relay，native 零跨进程开销。

native 有真实工程坑：glibc 2.17 缺 `__cxa_thread_atexit_impl`，Rust TLS 析构可能在 dlclose 后跳进未映射代码，故 native glibc 库链接 `-Wl,-z,nodelete` 常驻内存直到 Relay 退出（`README.md:49-51`，旗标注入 `scripts/plugins.py:196-206`）；musl native 要求宿主动态链接 musl，CI 从解析的 Relay commit 构建测试宿主（`scripts/plugins.py:155-156`，`README.md:45-47`）。

## 4. manifest 双轨：运行时与发布契约分离

每个插件有两份 manifest，职责严格分离：

- **`relay-plugin.toml`（运行时）**：告诉 Relay 如何校验与加载——`plugin.id/kind`、`compat.relay` 区间与 `native_api`/`worker_protocol`、`defaults.enabled=false`（注册不激活，`README.md:64`）、`integrity.sha256`（Relay 加载前核验哈希，`README.md:91-92`）。源模板占位符由 `scripts/tasks.py:58-63` 的 `write_runtime_manifest` 在打包时物化。
- **`release.toml`（发布）**：告诉工具链如何取源、构建、测试、打包。顶层 11 组属性由 `schemas/release.schema.json`（473 行，Draft 2020-12）严格校验：`source.location` 枚举 in-tree/remote/wheel/crate 且各态字段互斥（`schemas/release.schema.json:75-77`），remote 必须 github.com 仓库 + 40 位 sha（`:95-97`），顶层 `additionalProperties=false`（`:3`）。

`scripts/catalog.py:58-100` 的 `discover()` 是唯一入口：逐插件校验 schema、name 唯一且匹配目录名（`:73-75`）、路径可移植且不逃逸（`inside()`，`:48-55`）、wheel/crate 源顺带读 source.lock（`:91-94`）。

## 5. 发布工具链主干

`scripts/plugins.py` 是本地与 CI 共用的 CLI（`scripts/plugins.py:4`），子命令 validate/list/validate-tag/plan/run/notes/release：

- **plan 体系**：`make_plan`（`scripts/plugins.py:47-92`）把 CI 事件映射为构建矩阵——tag 事件选且仅选该插件（`tag_plugin`，`scripts/catalog.py:103-109`）；PR 用 merge-base 对比（`:132-133`）；push 用 before..head。路径影响判定 `affects()`（`:112-116`）：命中 `plugins/<name>/` 或共享前缀/文件集（`:33-45`）。相同 relay 选择器只解析一次宿主（`scripts/plugins.py:75-78`）；remote 源 tag 必须解析到钉住 sha（`:95-111`）。
- **七平台矩阵**：`scripts/catalog.py:17-25` 定义七平台各自的 runner 与 Rust target；Linux 四平台用与 Relay CLI 相同的钉住镜像（sha256 写死，`:27-32`）。CI 以 `fail-fast: false` matrix 展开全平台（`.github/workflows/plugins.yml:57-60`），tag 构建禁并发取消（`:13-15`）。
- **run_plugin 四阶段**（`scripts/plugins.py:123-272`）：build/test/package + 归档解压后 smoke（`:217-228`）；命令只做 `${VAR}` 数组替换、永不经过 shell（`:114-120`）；只能在本机原生平台跑（`:127-128`）。产物三件套：归档 + `.sha256` + `.json` 边车（`:269-270`），边车含 `verified 标志（`:267`）与仓库清洁标志（`:235`）。
- **`releases.py`** 提供 `publish_draft`/`release_notes`（`scripts/releases.py:55/:127`），发布永远人工点。

## 6. 许可归属机器

`scripts/licensing/attributions_lockfile_md.py` 是仓内最大脚本（1072 行），为 Rust/Python 两条语言线生成 ATTRIBUTIONS：

- **Rust 线**：`cargo about generate --locked --all-features --fail` 出 JSON（`scripts/licensing/attributions_lockfile_md.py:281-296`），与 `Cargo.lock` registry 包键对账；漏渲染的包走 cargo metadata 回退（`:407-419`），回退必须有许可文本，本地没有就按 `.cargo_vcs_info.json` 记录的发布 commit 去 GitHub 抓 LICENSE（`:900-908`）；抓取强制 40 位 sha + github.com 域、不碰默认分支（`:866-897`）；仍找不到即抛错（`:402`）。
- **Python 线**：直接解析 `uv.lock` 的 registry/git 包（`:189-201`），逐包下载哈希校验的 sdist/wheel 读许可文本（sdist 优先，`:808-824`）；git 源按锁定 commit 校验 pyproject 身份（`:960-985`）；UNKNOWN 标签从文本标题反推（`:156-181`；MIT 形状检测 `:143-153`）。
- **编排与消费**：`scripts/licensing/generate.py:37` 的 `projects()` 发现仓根与各插件源；本脚本被 5 个兄弟模块当函数库（`scripts/licensing/packages.py:10` 等），下划线"私有"函数实为事实公共 API；pre-commit 连删除提交也重跑聚合。

## 7. Switchyard 生产插件

switchyard-plugin 是唯一非示例插件，且**代码不在本仓**：`release.toml` 用 `source.location="remote"` 把源钉在 NVIDIA-NeMo/Switchyard 的精确 commit（`plugins/switchyard-plugin/release.toml:16-21`：ref `release/0.3` 只是"要跟踪什么"，构建检出 `sha=45e424d…`）。本地 `tasks.py` 只做编排：`cargo build/test --locked --release -p switchyard-nemo-relay-plugin`（`plugins/switchyard-plugin/tasks.py:19/:23`），打包调上游 `scripts/package_bundle.py`（`:30-40`），并把被链接 crate（protocol、switchyard-translation）的 LICENSE/NOTICE 复制进 bundle（`:44-49`）。插件版本 0.3.2 与 Switchyard workspace 版本解耦，Relay 测试宿主钉 0.10.2（`plugins/switchyard-plugin/release.toml:6/:27-28`）。`checkout()` 用 `git init + fetch --depth=1` 拉精确 sha 并复验 HEAD（`scripts/host.py:64-100`）。冒烟注入完整 switchyard_config 验证 `switchyard/default` 路由解析（`plugins/switchyard-plugin/smoke_test.py:31-58`）。

## 8. 陷阱与勘误（源码实证）

1. **三示例 smoke_test.py 字节级相同**：diff 实证完全一致——同一脚本靠 `scripts/smoke.py` 基座按 `samefile` 匹配 manifest（`scripts/smoke.py:28-39`）；改冒烟逻辑须同步三处。
2. **ATTRIBUTIONS 是生成物**：`ATTRIBUTIONS-Rust.md` 72190 行、536 个 `##` 包节；`ATTRIBUTIONS-Python.md` 2794 行、30 节；头部自带勿手改声明（`scripts/licensing/attributions_lockfile_md.py:60-61`）。
3. **wheel_backend 被复制进 bundle**：`scripts/wheel_backend.py`（纯 stdlib PEP 517 后端）打包时复制为 bundle 内 `relay_wheel_backend.py`（`scripts/tasks.py:126`）；包名 `relay-wheel-environment` 是保留字（`scripts/package_sources.py:78-79`；保留路径检查 `scripts/tasks.py:116-123`）。
4. **"37 测试"口径**：`test_worker.py` 实为 36 个测试函数（`plugins/example-python-grpc-worker-plugin/tests/test_worker.py:93-596`），两处 `parametrize`（`plugins/example-python-grpc-worker-plugin/tests/test_worker.py:153`）展开后 40 个收集项，37 与任一口径不符。
5. **占位符 manifest 不可直接用**：仓内 `relay-plugin.toml` 的 `<platform-library-file>` 等是模板占位，只有 bundle 内物化版能被 Relay 加载。
6. **共享脚本洁癖是硬约束**：给 `scripts/` 加按插件名分支违反 `AGENTS.md:10`；平台差异已抽象进 release.toml 与 `${VAR}` 展开。

## 新人三步

`scripts.plugins list` 看清单（`README.md:110`）→ `run example-rust-native-plugin` 全链跑通（`README.md:111`）→ 读 `plugins/example-rust-native-plugin/src/lib.rs:51-84` 对照 `explain/04`。
