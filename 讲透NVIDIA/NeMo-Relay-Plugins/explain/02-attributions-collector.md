# 02 · attributions_lockfile_md.py：1072 行双语言归属收集器

## 角色定位

`scripts/licensing/attributions_lockfile_md.py`（1072 行，仓内最大脚本）是许可归属机器的心脏：从锁文件出发，为 Rust（Cargo.lock/cargo-about）与 Python（uv.lock）两条语言线收集每个第三方包的许可标签与全文，渲染成 NVIDIA Dynamo 风格的 ATTRIBUTIONS markdown。它有双重身份——既是独立 CLI（`main`，`scripts/licensing/attributions_lockfile_md.py:1050-1068`，`python/rust` 二选一 + `--root/--output`），又是整个 licensing 目录的函数库：五个兄弟模块 import 它复用内部函数。产物 `ATTRIBUTIONS-Rust.md`（72190 行/536 包节）与 `ATTRIBUTIONS-Python.md`（2794 行/30 节）是生成物，头部自带勿手改声明（`:60-61`、`:71-72`）。

## 内部结构

**Rust 线**（cmd_rust，`:1020-1027`）：`_cargo_about_json` 跑 `cargo about generate --locked --all-features --workspace --fail`（`:278-303`）拿许可分组 JSON；`_render_rust_attributions`（`:451-478`）跳过 workspace 成员 crate（`:426-428`）渲染每包一节；对账关键在 `_rust_missing_cargo_about_packages`（`:407-419`）——`_cargo_lock_registry_package_keys`（`:311-323`）从 Cargo.lock 提取全部 registry 包键，减去已渲染键，差集中的每个包用 `_render_rust_metadata_fallback_attribution`（`:377-404`）从 cargo metadata 回退渲染，缺许可文本直接 `raise ValueError`（`:402`）——fail closed。

**Python 线**（cmd_python，`:1030-1047`）：`_lockfile_external_packages`（`:189-201`）只取 uv.lock 中带 registry/git source 的外部包；`_lockfile_only_python_package`（`:940-957`）是单包管线：git 源走 `_git_python_license`，否则 `_artifact_metadata_from_lockfile`（`:808-824`，sdist 优先、wheel 兜底）；文本仍缺时 `_python_upstream_licenses`（`:911-937`）从 wheel METADATA 的 Project-URL 找 GitHub 仓库、`git ls-remote` 解析版本 tag（`:925-934`）再抓上游；三级兜底全空才抛错（`:948-949`）。

**不可变上游抓取**：`_upstream_licenses` 是全脚本的安全基石（`:866-897`）——正则强制 github.com 仓库 + 40 位 sha（`:869-871`），按 LICENSE/LICENSE.md/LICENSE.txt/LICENSE-MIT/LICENSE-APACHE/NOTICE 候选清单从 `raw.githubusercontent.com/<repo>/<sha>/` 抓取（`:876-886`），404 跳过、其他 HTTP 错误上抛，绝不碰分支名。Rust 侧的精确 commit 来自 crates.io 发布档案里的 `.cargo_vcs_info.json`（`_rust_upstream_licenses`，`:900-908`）。

**元数据启发式**：`_metadata_license_name`（`:551-567`）按 License-Expression → License → Trove classifier 三级取标签，超 200 字符降级"See package metadata"；许可文本标题反推（`:156-181` 的 heading map + `:143-153` 的 MIT 形状六要素检测）；wheel/sdist 各自的声明文件优先（`:686-701`/`:752-765`）、启发式候选按 `_license_name_rank`（`:601-634`）与路径深度（`:637-640`）排序选最佳。

## 外部连接

五个消费模块 import 它当函数库：`scripts/licensing/packages.py:10`（已发布包源去重渲染，用 `_wheel_metadata_from_bytes`/`_infer_license_name`/`_rendered_python_package_inventory`/`_render_python_package`，`scripts/licensing/packages.py:44-60`）；`scripts/licensing/python_local.py:9`（本地路径包，用 `_normalize_package_name`/`_lockfile_only_python_package`，`scripts/licensing/python_local.py:98` 与 `scripts/licensing/python_local.py:119`）；`scripts/licensing/dependency_inventory.py:15`（用 `_cargo_metadata`，`scripts/licensing/dependency_inventory.py:298` 与 `scripts/licensing/dependency_inventory.py:349`）；`scripts/licensing/generate.py:17`（编排器——用 `project_context` 暂存并改写模块级 `ROOT` 指向各插件源 `:22-30`，再调 `_cargo_about_json`/`_render_rust_attributions`/`_rust_license_inventory` `scripts/licensing/generate.py:113-125`）；`scripts/licensing/license_diff.py:29`（diff 审计，import 类型 `LicenseInventoryEntry`）。渲染三件套（`_render_python_package` `:204-220`、`_rendered_python_package_inventory` `:486-490`、`_rust_license_inventory` `:493-519`）与类型 `RenderedPythonPackage`/`LicenseInventoryEntry`（`:38-52`）构成事实公共 API。上游还有外部进程：cargo/cargo-about/git ls-remote/urllib。

## 数据流

Rust：Cargo.lock ∪ cargo-about JSON → 差集 → metadata 回退 → 本地 license 文件（`_rust_license_files`，`:339-345`，license_file 声明 + 目录扫描 LICENSE*/COPYING*）→ 缺失则 `.cargo_vcs_info.json` sha → raw.githubusercontent → 排序输出（`:475-478`）。Python：uv.lock 包 → sdist/wheel 下载（`_download_locked_artifact` `:530-536`，哈希不匹配即 fail）→ METADATA/PKG-INFO → License-File 声明 → 启发式候选 → 标签反推 → 排序渲染。两条线在 `scripts/licensing/generate.py:37` 的 `projects()` 发现的每个项目（仓根 + 各插件源，remote 源含 workspace crate）上重跑，聚合进各自 ATTRIBUTIONS。

## 设计决策

1. **锁文件优先而非环境**：从 uv.lock/Cargo.lock 读依赖而非 `pip list`/`cargo tree`——归属跟着发布工件走，构建机装了什么无关紧要。
2. **fail closed 三连**：下载哈希不符抛错（`:534-535`）、缺许可文本抛错（`:402`、`:948-949`）、身份不符抛错（git 包 pyproject 校验 `:977-981`）——宁可构建失败也不产出"UNKNOWN"归属。
3. **精确 revision 不可协商**：`_upstream_licenses` 拒绝一切默认分支（`:869-871`）；Python git 包要求 sha fragment（`:967-972`）。
4. **lru_cache 全局缓存**（`:866`）：同一 sha 的上游文本跨包复用，536 包规模下省大量请求。
5. **渲染确定性**：全部按 (name.lower(), version) 排序（`:475/:516`），diff 审计（license_diff）才能逐行比较。
6. **模块级 ROOT 全局**：CLI 与库两种用法共享 `ROOT`（`:31`），generate.py 靠 try/finally 交换（`scripts/licensing/generate.py:22-30`）——代价是并发不安全，只能串行调用。

## 新人提示

- 永远不要手改 ATTRIBUTIONS-*.md；pre-commit 的 aggregation 钩子会重生成并覆盖（连删除提交也跑）。
- 跑 Rust 线需要 `cargo-about 0.9.1 --locked`（`README.md:105`）与网络（crates.io + raw.githubusercontent）。
- 加新依赖后 CI 失败时先看是不是"Missing upstream license text"——这是设计行为，需要给包找到真实许可文件而不是放宽检查。
- 改内部函数签名前 grep 五个消费模块：下划线不代表私有（见外部连接清单）。
- `spdx_url`（`:76-86`）对复合表达式（OR/AND/括号）退回 SPDX 首页而非拼错链接——渲染上的小防御。
