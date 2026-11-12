# 03 · package_sources.py + bundles.py：包源下载验证与归档完整性

## 角色定位

这对模块构成供应链的"入口验证 + 出口验证"。`scripts/package_sources.py` 管**已发布包源**（wheel/crate）：从 release.toml 声明的 `source.location` 出发，严格校验 source.lock、下载校验和匹配的包档案、解剖出可构建的源树；`scripts/bundles.py` 管**归档与完整性**：bundle 的运行时 manifest 校验、可移植归档的创建与解包（防 Zip Slip/链接/设备文件）、发布资产的终检。一进一出，把"我们发布的每个字节都有据可查"变成代码强制。

## 内部结构

**package_sources 的三层闸门**：

1. `read_lock`（`scripts/package_sources.py:55-115`）——source.lock 结构校验：字段集合精确等于六元组（`:66`）、名字/版本/文件名走白名单正则（`:74-77`）、文件名唯一且后缀必须匹配 location（`:80-84`）、URL 必须 HTTPS 且无凭据无 fragment（`:85-89`）、sha256 必须 64 位十六进制（`:90-91`）、platforms 必须是 manifest 平台的非空无重子集（`:92-99`）；每个平台恰好一个精确版本的根包（`:100-112`）；crate 不允许携带依赖（`:113-114`，依赖归 Cargo.lock 管）。包名 `relay-wheel-environment` 被保留（`:78-79`）。
2. `download`（`:130-150`）——按 sha256 分桶缓存；下载时若被重定向离开 HTTPS 直接拒绝（`:140-141`），临时文件过完哈希校验才原子替换（`:143-145`），命中缓存也要复验（`:148-149`）——缓存不是信任边界。
3. `wheel_metadata`（`:153-200`）——把 wheel 当不可信档案解剖：成员名过 `_member` 防逃逸（`:158`，实现在 `scripts/bundles.py:83-90`）、拒绝符号链接（`:159-160`）与大小写碰撞路径（`:161-163`）、恰好一个 `.dist-info/METADATA`（`:164-166`）、依赖禁止直接 URL（`:168-171`）、RECORD 每行强哈希且覆盖每一个文件（`:179-199`）。

`prepare`（`:203-239`）串起全链：crate 解包后验 Cargo.toml 身份且必须含 Cargo.lock（`:210-216`）；wheel 逐个过 `wheel_metadata` 后进 wheelhouse（`:217-224`），解包保留可执行位（`:227-230`）；最后核对包内运行时 manifest 的 kind 与 release 类型一致（`:231-235`）并落 `package-source.json` 溯源（`:236-238`）。

**bundles 的三道验证**：`verify_bundle`（`scripts/bundles.py:25-59`）校验 bundle 内 manifest——工件 sha256 与 `integrity` 一致（`:31-32`）、kind 与 release 类型匹配（`:33-35`）、加载目标三分支：native 的 `load.library` 必须就是被校验工件（`:37-39`）、Python worker 的 entrypoint 必须指向包内模块文件（`:40-46`）、Rust worker 的可执行同理工件（`:47-48`）；再解析 config schema（`:49-50`）、拒绝符号链接与特殊文件（`:51-53`）、ATTRIBUTIONS 必须存在且非空（`:54-58`）。`extract_archive`（`:93-116`）解包前逐成员过 `_member`（重复/空名/`..` 拒绝 `:83-90`）并拒绝链接与设备（`:102-111`），tar 用 `filter="data"`（`:112`）。`verify_assets`（`:119-183`）是发布终检：身份四元组匹配（`:128-136`）、禁止本地宿主覆盖与脏树（`:137-140`）、verified 标志（`:141-142`）、Rust Linux 必须用计划镜像与 target（`:143-150`）、native musl 必须动态宿主测试（`:151-156`）、remote 源 commit 锁定（`:157-161`）、包源 provenance 重算比对（`:162-168`）、Relay 40 位 sha（`:169-170`）、校验和与文件集精确闭合（`:171-182`）。

## 外部连接

- 上游：`scripts/catalog.py` 的 `discover` 在 wheel/crate 源时调用 `read_lock`（`scripts/catalog.py:91-94`）；`scripts/plugins.py:144-151` 的 run_plugin 调 `prepare` 并把 wheelhouse/`PACKAGE_PYTHON`（`install_wheels`，`scripts/package_sources.py:29-48`）注入命令环境。
- 下游：`scripts/tasks.py:93-154` 的 `package_wheel` 把 wheel 源物化为可安装 bundle（复制 `wheel_backend` 为 `relay_wheel_backend.py` `:126`）；`scripts/bundles.py:162-168` 反过来 import `provenance` 做发布终检——同一身份函数在构建与发布两端各跑一次。
- 测试防线：`tests/test_package_sources.py` 全链路覆盖（source.lock 拒绝矩阵、下载哈希失败、RECORD 篡改），`tests/test_bundles.py` 覆盖路径逃逸与链接拒绝；CI 层 `tests/test_catalog.py:273` 确保 lockfiles 不被 ignore。

## 数据流

发布一个 wheel 插件：release.toml 声明 `location="wheel" + package + version + manifest` → `read_lock` 校 source.lock → 按 sha256 下载（缓存命中也复验）→ `wheel_metadata` 解剖每个 wheel → wheelhouse + `package-source.json` → build/test/package 命令在物化源树上执行 → `verify_bundle`（打包前 `scripts/plugins.py:219-220`）→ `create_archive`（`:67-81`，Windows zip/其余 tar.gz，归档不得在 bundle 内 `:68-69`）→ 解压回验 + smoke（`:224-228`）→ `verify_assets` 收口。crate 同构但依赖解析交给 Cargo.lock，wheelhouse 换成 cargo 注册表缓存。

## 设计决策

1. **信任最小化**：缓存复验（`scripts/package_sources.py:148-149`）、HTTPS 重定向拒绝（`:140-141`）、RECORD 全覆盖（`:198-199`）都在回答"如果上游被投毒会怎样"。
2. **crate 与 wheel 的依赖模型差异显式化**：crate 要求 Cargo.lock 随包发布（`:215-216`），wheel 要求依赖全部以锁定 wheel 形式进 source.lock——两者都不允许构建期联网解析。
3. **`_member` 复用而非重写**：wheel 成员校验直接调 bundles 的 `_member`（`:158`），逃逸规则单点维护。
4. **zip 与 tar 的危险面不同**：zip 只查链接（`:102-104`），tar 还要挡设备文件并用 `filter="data"`（`:110-112`）——Python 官方对 tar 的默认防护被显式启用。
5. **`.json` 边车是机器可读的发布证书**：`verify_assets` 把 verified/dirty/override/build_image 全部写死检查（`scripts/bundles.py:137-156`），发布产物自我描述且不可撒谎。
6. **保留字机制**：`relay-wheel-environment`（`scripts/package_sources.py:78-79`）与 bundle 保留路径（`scripts/tasks.py:116-123`）防止插件包与适配器命名空间冲突。

## 新人提示

- 发布新包版本的操作手册在 `docs/package-sources.md`（含冒烟与归属更新流程）；先改 source.lock 再跑 `python -m scripts.plugins validate`。
- `install_wheels` 用 `uv pip install --no-index` + `uv pip check`（`scripts/package_sources.py:35-47`）——依赖闭包在本地验证，不依赖 PyPI。
- 看到 "wheel RECORD does not cover every file" 别改校验——那是包本身的问题，换版本或联系上游。
- `provenance` 输出会原样进 bundle 边车，发布终检逐字段重算比对；手改边车必被 `verify_assets` 抓住。
- 解压目录必须为空（`:95-96`）且归档必须只有单一根目录（`:113-115`）——写插件打包脚本时保证 `create_archive` 的 prefix 结构。
