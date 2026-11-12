# 10 · 测试体系：CI 六 job 矩阵、反跳过 gate 与惰性导入模式

> 对象：`.github/workflows/python-ci.yml`（160 行）、`scripts/ci_required_tests.py`、`scripts/ci_smoke_installed.py`、`datamind/tests/`（45 个测试文件）+ `plugins/datamind-context/tests/` + 仓根 `tests/`（2 个多模态 e2e）。

## 一、角色定位

DataMind 的测试体系解决一个具体矛盾：核心栈（Chroma/LanceDB/SQLite）零外部服务就能测，但可选栈（MySQL、Dolt、cocoindex、官方 Codex SDK）装不上时 pytest 会安静地 skip——**安静跳过等于假绿**。CI 的答案是把测试拆进六个独立 job，可选依赖在各自 job 里真装（MySQL 起容器、Dolt 下载钉版二进制、codex 装官方 SDK），再用一个自定义 pytest 插件把"跳过"升级成"失败"，最后用 `always()` gate 强制所有 job 都过关才能合。

## 二、内部结构（六 job 矩阵）

1. **test**（python-ci.yml L12-38）：`python-version: ["3.11","3.12"]` 矩阵且 `fail-fast: false`（L16-18）；L29 装 `.[dev]`；**L32 `python -m compileall -q datamind` 先做语法闸**；L35 跑 `datamind/tests` + `plugins/datamind-context/tests`；L38 附带 `verify_sqlite_demo`（确定性无网络冒烟）。
2. **versioning**（L40-59）：装 `.[dev,cocoindex,dolt]` 三 extra（L50），跑 kb_versioning、kb_ingest、pr28_regressions、workspace_revisions、workspace_incremental、ingestion_skills 六件（L52-59），全经 `scripts/ci_required_tests.py` 包一层（反跳过）。
3. **databases**（L61-100）：`timeout-minutes: 15`；services 起 **mysql:8.4 容器**（L67，health-cmd L72-76），env 注入 `DATAMIND_TEST_MYSQL_DSN`（L78）；**Dolt 二进制钉版**——L90 拉 releases `v2.5.0`，L91 用 sha256 校验和 `639b8042...557c93` 锁死，L93 装进 `/usr/local/bin`；无 skip 跑 db_ingest、db_versioning、workspace_native_db（L95-100）。
4. **package**（L102-119）：`python -m build --wheel`（L112）→ 独立 venv 装 wheel（L114-116）→ **working-directory 切到 /tmp** 跑 `ci_smoke_installed.py`（L117-119），测安装产物而非 checkout。
5. **codex**（L121-141）：装 `.[dev,codex]`（L131，官方 openai-codex SDK），压七条 host/MCP 契约：direct_data_plane、codex_host、unified_host、cli_codex、http_api、experiment_faults、datamind_mcp（L132-141）——这正是 09 篇的插件双入口 stdio 测试所在。
6. **gate**（L143-160）：**`if: always()`**（L145）保证前序有失败也执行；`needs: [test, versioning, databases, package, codex]`（L146）；L150-159 内联 Python 解析 `toJSON(needs)`，任何 job result 非 success 就 `SystemExit`——这是 GitHub Actions matrix job 之外自己实现的总闸，防止"某 job 被跳过所以没红"。

**两个 CI 辅助脚本**：`ci_required_tests.py` 核心是 `RequireExecutedTests` 插件（L7-16）在 `pytest_sessionfinish` 钩子里查 terminalreporter 的 `skipped` 统计，**非空就把 exitstatus 改成 TESTS_FAILED**——docstring L1 说破动机："missing services/dependencies must fail CI"。`ci_smoke_installed.py` 用 importlib.resources 断言 wheel 完整性：app.html 在包里（L13）、skills 且至少一个 SKILL.md（L14-15）、`dolt`/`lancedb` 在注册表（L16）、默认 chroma+direct（L17-18）、**L19-20 断言 import 的 datamind 不在 checkout 下**（防假测源码）、L28 起 MCP definitions 与 data_plane 可导入。

## 三、外部连接

- 六 job 的依赖面：test→基础 dev；versioning→cocoindex+dolt extra；databases→mysql/dolt/versioning extras+真容器+真二进制；package→build 工具链；codex→官方 SDK。**每个 job 只装自己需要的**，避免了"全量依赖互相打架"。
- 测试与被测层的对应（tested_by 全景，按 `datamind/tests/` 文件名归组）：db 线五件（test_db_sqlite/db_ingest/db_versioning/db_safeguard/db_engine_options/db_nl2sql_prompt）→ capabilities/db；kb 线（test_kb_ingest/test_kb_versioning/test_indexer/test_filters/test_retrievers）→ capabilities/kb；graph 线（test_graph/test_graph_ingest/test_graph_parallel_paths/test_graph_persistence_races/test_graph_revisions）→ capabilities/graph；workspace 线（test_workspace_incremental/test_workspace_native_db/test_workspace_revisions/test_two_agent_data_plane）→ 08 篇五文件；host/MCP 线（test_codex_host/test_unified_host/test_cli_codex/test_http_api）→ datamind/host.py 与 mcp.py；跨层回归件（test_pr28_regressions、test_replace_receipts、test_read_recovery、test_runtime_reliability、test_experiment_faults、test_review_cancelled_persist）对应历史事故：PR28 回归、回执豁免、读恢复、运行时可靠性、故障注入实验（experiment_faults 在 runtime.py L69-70 被装进 kb）、评审取消持久化。
- 仓根 `tests/` 只有 test_multimodal_e2e/test_multimodal_loading 两个文件，属于 legacy v0.1 线（07 篇），**CI 不收集它们**（L35 只点名 datamind/tests 与 plugins）。

## 四、数据流

PR 推送 → 六 job 并行。test job 的 pytest 进程加载 `datamind/tests`：模块顶层只有 stdlib+pytest+datamind 轻量 import；进到具体测试函数，才经 `_make_store(kind, ...)` 这类工厂在**函数体内**按需 `from datamind.capabilities.kb.providers.lancedb_store import LanceDBVectorStore`（test_kb_ingest.py L56）或 `...chroma_store import ChromaVectorStore`（L61）——provider 模块自己也把重依赖压进方法体（chroma_store.py L27 `import chromadb` 在函数内）。于是没装 lancedb 的环境跑 chroma 分支测试不炸不卡。databases job 里装好 Dolt 的环境跑同一批文件时，`ci_required_tests.py` 保证没有任何测试敢悄悄 skip。最后 gate job 聚合五 job 结果定红绿。

## 五、设计决策（含批判）

1. **skip 即失败**是本仓最有性格的决定：业界常见做法是 skip+黄标，这里直接红。收益是"可选依赖腐烂"立刻可见；代价是贡献者本地没装 dolt 时跑 required 切片必红——所以 `ci_required_tests.py` 只包在 CI 的三个 job 里，本地默认 pytest 不受影响。
2. **Dolt sha256 钉版**（L91）防供应链漂移，但 `dolt version` 只打日志不与期望比对——版本号本身没有断言，二进制被换成同哈希不可能、被上游删 release 则 curl 层失败，总体足够。
3. **MySQL 8.4 而不是 latest**：锁大版本防方言漂移（NL2SQL 的方言层对 MySQL 语法敏感），与 Dolt 钉版同一思路。
4. **惰性导入三明治**（测试工厂→provider 方法→真正的 chromadb/lancedb import）让"同一文件覆盖双栈"成为可能。批判：分支多了一层，`kind` 参数传错时会静默落到 chroma 分支（L61 的 else 无断言 kind 合法性）。
5. **gate 用 if: always() + 内联 Python** 而不是 GitHub 原生 branch protection 的 required checks——好处是矩阵 job 全名不用逐个登记，坏处是 branch protection 仍需把 `gate` 设为 required，否则这层闸没人强制。
6. 六 job 无缓存共享（各自 pip cache 键独立），装依赖时间是主要开销；对 15 分钟超时的 databases job 来说 Dolt 下载重试（L90 `--retry 3`）已经考虑了网络抖动。

## 六、新人提示

- 加新测试文件后先确认它在哪个 job 的收集范围：默认进 test job；涉及 dolt/mysql 才会被 databases/versioning job 真跑——记得把文件名加进对应 job 的清单（L52-59/L95-100/L132-141），**漏登记=永远只在无依赖环境跑**。
- 测试里要用向量库时，仿照 `test_kb_ingest.py` 的 `_make_store`（L54-63）在函数体内 import，不要在模块顶层拉 chromadb/lancedb，否则拖慢整个收集阶段。
- 本地复现 CI 红的最快路径：`python scripts/ci_required_tests.py -q datamind/tests/test_kb_versioning.py`——它会告诉你哪个测试被 skip 了。
- `test_pr28_regressions.py` 这类命名是历史事故账本，修 bug 请顺手加回归件并让它进某个 required 切片。
- 改 wheel 打包内容（static/skills）后，package job 的 L13-16 断言是最先红的地方；`datamind/static/` 与仓根 `static/` 双份拷贝不同步不会在 CI 暴露（只查包内那份）。

行号锚：python-ci.yml:12-38/16-18/32/35/38/40-59/50/61-100/64/67/72-76/78/87-94/90/91/95-100/102-119/112/114-119/121-141/131/143-160/145/146/150-159 · scripts/ci_required_tests.py:1/7-16 · scripts/ci_smoke_installed.py:13-20/28 · datamind/tests/test_kb_ingest.py:54-63 · datamind/capabilities/kb/providers/chroma_store.py:27 · datamind/runtime.py:69-70
