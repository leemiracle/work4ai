# 01 · catalog.py + plugins.py：七平台矩阵与 plan 体系

## 角色定位

`scripts/catalog.py` 与 `scripts/plugins.py` 是发布工具链的躯干：前者提供"已校验的 manifest 清单 + 路径影响规则"，后者提供本地与 GitHub Actions 共用的 CLI（`scripts/plugins.py:4`）。`python -m scripts.plugins` 的七个子命令（validate/list/validate-tag/plan/run/notes/release，`scripts/plugins.py:278-301`）中，`plan` 是 CI 的入口——把 tag/PR/push 事件翻译成构建矩阵，`run` 是开发者的入口——在本机原生平台完整走一遍 build→test→package→smoke。两者共享同一套 manifest 发现与校验逻辑，保证"CI 测的"与"本地跑的"是同一条流水线。

## 内部结构

**catalog.py 的三块静态事实**：七平台表 `PLATFORMS` 把每个平台映射到 GitHub runner 与 Rust target（`scripts/catalog.py:17-25`，如 linux-arm64→ubuntu-24.04-arm + aarch64-unknown-linux-gnu）；`LINUX_IMAGES` 为 Linux 四平台钉住与 Relay CLI 打包完全相同的不可变镜像 digest（`scripts/catalog.py:27-32`）；`SHARED_PREFIXES`/`SHARED_FILES`（`:33-45`）定义"改动哪些文件算影响所有插件"——scripts/、schemas/、workflow 目录加上 11 个仓级文件。

**discover() 的强校验链**（`scripts/catalog.py:58-100`）：读每个 `plugins/*/release.toml` → jsonschema 校验 → name 必须唯一且等于目录名（`:73-75`）→ 五个路径字段逐一过 `inside()` 防逃逸（`:48-55`，拒绝绝对路径、反斜杠、冒号与 `..`）→ wheel/crate 源就地读 source.lock（`:91-94`）且 crate 必须声明 rust 工具链（`:95-96`）。`tag_plugin`（`:103-109`）要求 tag 精确等于 `<name>-<version>`，杜绝模糊匹配。

**plugins.py 的 plan 体系**：`make_plan`（`scripts/plugins.py:47-92`）按事件三分——tag ref 走 `tag_plugin` 选且仅选一个插件（`:56-57`）；PR 用 base/head 的 merge-base 求 diff（`:58-67`）；push 用 before..head（`:68-69`）。`select` + `affects`（`scripts/catalog.py:112-116/:143-145`）把变更路径过滤成受影响插件集。矩阵行在 `:79-91` 生成：每插件×每平台一行，带 runner/target/python/rust，且只有声明 rust 工具链的插件才注入 `build_image`（`:85-87`）。

**run_plugin 的四阶段**（`scripts/plugins.py:123-272`）：解析源（remote→`checkout` 钉 sha `:139-143`；wheel/crate→`prepare` `:144-151`；in-tree→仓内目录）、装 Relay 测试宿主（musl native 用动态链接宿主 `:155-156`）、组装环境变量（清掉 `VIRTUAL_ENV` 防污染 `:158-159`；rust 注入 RUSTUP_TOOLCHAIN/CARGO_BUILD_TARGET `:190-192`，glibc native 追加 `-Wl,-z,nodelete` `:196-206`），然后 build/test/package 顺序执行（`:217-218`），归档前后各验一次 bundle（`:219-226`），解压后跑 smoke（`:224-228`），最后写三件套与 `.json` 边车（`:229-270`）。

## 外部连接

- **CI**：`.github/workflows/plugins.yml:40-46` 的 plan job 调 `scripts.plugins plan` 并把 matrix/has_plugins/is_tag 写进 step output（`scripts/plugins.py:330-334`）；build job 用 `fromJSON` 展开 matrix（`.github/workflows/plugins.yml:57-60`）；tag 构建禁并发取消（`:13-15`）。
- **被 import**：`scripts/bundles.py:17` 取 PLATFORMS/LINUX_IMAGES/inside；`scripts/package_sources.py:24-25` 取 inside；`scripts/tasks.py` 间接消费环境契约。
- **GitHub API**：经 `scripts/github.py` 的 GitHub 封装查 release/tag，`resolve_host` 决定测试宿主版本。
- **测试防线**：`tests/test_catalog.py:23` 验证 25 平台目标计数（4 插件×平台数的全景不变量）、`:53` 的 13 组无效 manifest 矩阵、`:137` 宿主只解析一次、`:177` tag/sha 不匹配拒绝、`:206` branch ref 跳过校验、`:254` musl 本地平台判定。

## 数据流

一次 push 的旅程：event payload → `changed_paths`（`scripts/catalog.py:123-141`，先 `rev-parse --verify --end-of-options` 把事件控制的值解析成 hash 再进 revision 参数——注入防御在 `:130-131` 注释写明；PR 走 merge-base `:132-133`；`--no-renames -z` 让跨插件移动的报告同时含新旧路径 `:134-137`）→ `select` → 每 manifest 的 relay 选择器 JSON 序列化后做 key，相同选择器只 `resolve_host` 一次（`scripts/plugins.py:75-78`）→ matrix 注入 GitHub Actions → 每个矩阵格在本机/runner 上 `run_plugin` → `dist/<name>/<platform>/` 三件套。命令执行永不经过 shell：`expand`（`:114-120`）只对 argv 每个词做 `${VAR}` 正则替换，未定义变量直接抛错。

## 设计决策

1. **plan 与 run 共用 `run_plugin`**：CI 的 `--plan` 参数（`scripts/plugins.py:338-349`）校验 checkout 与计划 commit 一致、矩阵成员资格，防止"计划了 A 构建了 B"；本地 `--relay-bin`/`--host-resolution` 覆盖与 CI 计划互斥（`:339-340`）。
2. **tag 钉死语义**：`validate_source_tag_pins`（`scripts/plugins.py:95-111`）强制 remote 源的 tag 解析结果等于 `source.sha`——上游 tag 被移动即构建失败；branch ref 则跳过校验（switchyard 跟踪分支的场景）。
3. **只在本机原生平台构建**（`scripts/plugins.py:127-128`）：交叉编译产物的测试无意义，平台正确性交给 CI 矩阵的 25 个格子。
4. **`local_platform` 用 sysconfig 判 musl**（`:37-44`）而非 uname——只有编译进 Python 的 HOST_GNU_TYPE 能区分 glibc/musl。
5. **错误处理收敛**：main 捕获 ValueError/KeyError/OSError/CalledProcessError 后 `sys.exit(str(error))`（`scripts/plugins.py:391-395`），CI 日志直接可读。

## 新人提示

- 改 `PLATFORMS`/`LINUX_IMAGES` 后先跑 `tests/test_catalog.py:23`（25 目标计数会提醒你平台×插件的全景变化）。
- 给共享脚本加按插件名分支是仓库红线（`AGENTS.md:10`）；平台差异应进 release.toml 的 `platforms` 字段与 `${VAR}` 展开。
- `discover()` 在任何子命令前运行（`scripts/plugins.py:309`），manifest 语法错误会让所有命令（包括 `validate` 本身）失败——这是故意的，契约先于工具。
- 看不懂 matrix 为空？检查 `affects`：PR 只动 `docs/` 时矩阵为空、`has_plugins=false`，build job 直接跳过（`.github/workflows/plugins.yml:57`）。
