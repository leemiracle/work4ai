# 06 · switchyard-plugin：生产插件与示例的差异

## 角色定位

`plugins/switchyard-plugin/` 是仓库唯一的**生产**插件（Relay ID `nvidia.switchyard`），把受支持的模型请求经 Switchyard 部署路由——复用其 targets、client pools、路由算法、重试策略与路由校验（`plugins/switchyard-plugin/README.md:10-14`）。与三个示例的本质区别：**本目录没有一行插件运行时代码**，只有 5 个编排文件（README/release.toml/tasks.py/smoke_test.py/THIRD_PARTY_NOTICES.md，共约 270 行）。真正的 Rust crate `switchyard-nemo-relay-plugin` 活在 NVIDIA-NeMo/Switchyard 仓——本仓只负责"钉住 commit、构建、打包、发布"。对照：示例插件是 in-tree 源码 + 教学；switchyard 是 remote 源 + 供应链管控，这是把第三方生产代码纳进自家发布纪律的范式样本。

## 内部结构

**release.toml 的 remote 契约**（`plugins/switchyard-plugin/release.toml:16-21`）：`location="remote"` + `repository="https://github.com/NVIDIA-NeMo/Switchyard"` + `path="crates/switchyard-nemo-relay-plugin"` + `ref="release/0.3"` + `sha="45e424d050addfbbe3bed8a61f55c440e7689eda"`。schema 层强制 remote 必须 github.com + 40 位 sha（`schemas/release.schema.json:95-97`）；plan 层 `validate_source_tag_pins` 在 ref 是 tag 时校验解析结果等于 sha（`scripts/plugins.py:95-111`）——ref 记录"跟踪什么"，构建永远检出 sha（README 明示 `plugins/switchyard-plugin/README.md:53-56`）。版本三轨分离：插件 0.3.2（`:6`）、Relay 测试宿主 0.10.2（`:27-28`）、SDK 版本来自 Switchyard 自己的 Cargo lockfile（README `:59-61`）。

**tasks.py 纯编排**（57 行）：build/test 都是 `cargo --locked --release -p switchyard-nemo-relay-plugin`（`plugins/switchyard-plugin/tasks.py:19/:23`）；package 调用**上游仓库自带**的 `scripts/package_bundle.py`（`:30-40`）——打包逻辑归插件作者，本仓只传 library 与输出路径；随后 `write_attributions(ctx)` 生成归属（`:42`，经 `scripts/tasks.py:84-90`，remote 源 include_workspace=True 把 Switchyard workspace crate 也算进来），并把 `THIRD_PARTY_NOTICES.md` 与被链接 crate（protocol、switchyard-translation）的 LICENSE/NOTICE 逐一复制进 bundle（`:43-49`）——因为构建下载的是整个 Switchyard workspace，链接进共享库的 crate 都有署名义务。

**smoke_test.py 验证生产行为**：与三示例（字节级相同的那份）同框架但断言目标完全不同——注入完整 `switchyard_config`（llm_clients/targets/routes 三段，`plugins/switchyard-plugin/smoke_test.py:31-44`），请求 `switchyard/default`，断言路由真的解析成 target 的 `example/model` 且恰好打中上游一次（`:50-58`）。示例验证"插件拦截了请求"（头注入），生产验证"路由正确转发"。

**构建隔离**：run_plugin 对 remote 源先 `git init + fetch --depth=1 <sha>` 到独立工作目录并复验 HEAD（`scripts/host.py:64-100`，瞬时网络错误按 2^n 退避重试三次 `:73-88`）——绝不 clone 默认分支。

## 外部连接

- **上游**：NVIDIA-NeMo/Switchyard 仓（代码、打包脚本 `package_bundle.py`、crate 间依赖、上游文档 `crates/switchyard-nemo-relay-plugin#configure-relay`）。
- **工具链**：`scripts/plugins.py:139-143` 的 checkout 路径；`scripts/tasks.py:58-63` 的 manifest 物化；`scripts/bundles.py:25-59` 的 verify_bundle（native 分支要求 load.library 即被校验工件 `:37-39`）。
- **测试宿主**：`[relay]` 选择器经 `resolve_host` 解析（`scripts/host.py:39-62`），tag 必须解析到稳定 release。
- **发布**：`scripts/releases.py:55` 的 release_notes 只列影响本插件的 PR（文件清单不完整即失败）；`scripts/bundles.py:157-161` 的 verify_assets 终检 remote 源 commit 锁定。

## 数据流

发布一轮：改 `source.sha` 到新 commit（可选改 ref）→ plan 阶段解析 release/0.3 并校验 tag→sha（若是 tag）→ 各平台 runner `run_plugin`：checkout 精确 sha → cargo build/test --release → 上游打包脚本产 bundle → 归属+第三方通知注入 → 归档/解压回验 → 装进真实 Relay 网关冒烟（路由解析断言）→ 三件套上传 → 人工点发布。用户侧：下载归档 → `nemo-relay plugins add/enable nvidia.switchyard` → 配置 Switchyard 部署 → 重启 Relay 加载共享库。

## 设计决策

1. **代码与发布权分离**：插件逻辑归上游 Switchyard 仓演进，本仓持有发布节奏与版本号——升级 = 改一个 sha，diff 极小且可审计。
2. **钉 commit 而非分支**：branch ref 只表达跟踪意图，构建物永远来自 40 位 sha——上游 force-push 不影响可重现性。
3. **打包脚本归上游**：`package_bundle.py` 在 Switchyard 仓内（`plugins/switchyard-plugin/tasks.py:30-40`），bundle 结构的变化随插件代码原子演进，本仓不需要追。
4. **workspace 级归属**：remote 源的 attributions 开 include_workspace（`scripts/tasks.py:89`），并手工复制两个被链接 crate 的通知（`plugins/switchyard-plugin/tasks.py:44-49`）——法律边界比示例严格。
5. **测试宿主与 SDK 解耦**：`[relay]` 只影响测试宿主版本（README `:62-64`），不改变构建产物依赖——测试升级不动工件。
6. **HTTP 语义保真**：路由失败保留已知 provider HTTP 错误状态；响应头已发出后流式失败无法再改状态码（README `:68-70`）——把分布式系统的现实写进文档。

## 新人提示

- 找 switchyard 插件源码不要在本仓 grep——去 Switchyard 仓 `crates/switchyard-nemo-relay-plugin`（精确 commit 见 release.toml 的 sha）。
- 升级流程：上游合并 → 拿新 commit sha → 改 `plugins/switchyard-plugin/release.toml:21` → 全平台跑 `scripts.plugins run switchyard-plugin` → 走 RELEASE.md 发布。
- 插件 0.3.2 要求 Relay ≥0.10.1 且 <1.0（README `:62-64`）；改 `[relay]` tag 前先确认区间兼容。
- 没有 `relay-plugin.toml` 在本目录是正常的——运行时 manifest 由上游打包脚本在 bundle 里物化（本目录连模板都没有，与示例插件不同）。
- 本插件全七平台都测（README `:51`）：改 tasks.py 后别只跑本机，CI 矩阵 25 格里 7 格属于它。
