# 10 · 安装档与 CI 负向断言：契约、五 job 与发布单一事实源

## 角色定位

如果说 09 篇讲的是安装体系"怎么装"，本篇讲的是"怎么保证它永远按声明的方式装"。这套仓库的 CI（`.github/workflows/checks.yml`，五个 job）几乎全部由**负向断言**构成——不验证功能正常，验证"坏事没发生"：dry-run 没改文件、安装器没碰禁区、卸载没删别人的东西、MCP 合并器没改坏配置、发布包没绑 0.0.0.0。发布线（`.github/workflows/release.yml` + `scripts/build_release.sh`）则把"zip 的内容"收敛为单一事实源。这一层的存在理由写在 checks.yml 开头注释里："catch the 'found at runtime after release' class of bug this repo kept hitting"。

## 内部结构

**三档防漂移契约。** 每份 profile manifest 的 `must_not_touch` 就是档位间的互不侵犯条约：webui 禁碰 `backend/app`、`frontend/src`、`.mcp.json`、`~/.codex/config.toml`、`~/.cursor/mcp.json`（5 项）；harness 追加 `frontend/package.json` 与 `node_modules`（6 项）——因为它的承诺是"没有 Node.js 的机器也能装"；skills 追加 `backend/app`（7 项），承诺是"不装任何包"。契约的执行不是靠人读文档：install.sh 在任何步骤跑之前先对禁区逐文件拍指纹快照，跑完 diff，违约 exit 1（见 09 篇）。`--dry-run` 是契约的只读投影——CI 的 static job 让三档各跑一遍。

**checks.yml 五个 job：**

1. **static**（无需装 DataFlow 的快速守卫）：shellcheck；`check_skills.py`（manifest/frontmatter/链接/条件指令）；生成器先跑一遍再 `--check` 断言确定性（手改生成物 = build 失败）；`check_mcp_whitelist.py`（白名单↔路由对账）；`check_profiles.py`、`check_docs.py`；三档 dry-run；然后两条关键负向断言——"Dry run creates nothing"：`.dataflow-install` 不得存在 **且** `git status --porcelain` 必须为空（dry-run 连工作树都不能碰）；以及 "MCP config merge refuses unsafe edits"。
2. **install-skills**（真装纯文件档，端到端）：先断言 fresh checkout 没有 `.claude/skills`（生成物不入 git）；装完断言 skills 档**不含 MCP 指引**——`grep validate_pipeline_config` 必须不命中 SKILL.md，这正是 ADR-001 条件渲染（`@if mcp==yes`）的可验证产物；AGENTS.md 行数 ≤200（"must stay a routing table, not an inlined dump"）；双 agent 目录下每个 managed skill 的 SKILL.md 逐一存在；退役规则（`dataflow-pipeline.mdc` 等）不得存活；重跑必须零重写（输出里不得再出现安装成功行）；卸载必须干净（技能与 receipt 全消）；最后两个"不误删"场景——用户自写的 Cursor 技能与自写的 AGENTS.md 在安装后必须原样，内容与官方一致但非本次安装的技能在卸载后必须幸存。
3. **operator-builder**（写用户仓库的技能的安产行为）：`--dry-run` 连 `$HOME` 下的 `usage.jsonl` 都不许写；非交互、无确认、无 `--yes` 时必须干净拒绝且零产出；第三个场景注释点明真实回归："a LATER target already exists, so the per-file check only tripped after the first few files were on disk"——预置一个排在后面的目标文件，断言 before/after 文件数相等（不允许部分生成）且用户文件内容原样；显式 `--overwrite skip-existing` 策略则正常生成其余文件。
4. **release-package**：见下文发布线。
5. **backend**（Harness 运行时）：clean checkout 里真装 harness 档（"must exercise the product path, not merely install the package list"）→ `pip check` 依赖一致性 → `import app.main`（含 MCP 挂载）→ pytest。

**MCP 合并的负向断言细节**（static job）。四组用例全部"必须失败且零修改"：喂 `this is [not valid toml` 给 `codex_config.py`——退出非零 **且** md5 前后不变；喂 `[mcp_servers.dataflow] command = "python"`（stdio 型条目）——必须 exit 4 拒绝（把 SSE url 混进 command 定义会产出两头不是的怪物）；喂指向 `http://elsewhere/mcp` 的 JSON 条目——exit 4（用户可能是有意指向别处）；喂 `[mcp_servers."dataflow"]` 带引号表名——必须原地更新且输出里 `mcp_servers` 只出现一次（防重复表）。前面还有一个前置守卫：先断言 TOML 解析器可达，否则"冲突测试因错误原因通过"（配置器正确拒绝 exit 2 也会被当成通过）。

**发布单一事实源。** `release.yml` 只在 `v*` tag push 触发，构建步骤名就叫 "Build release zip (single source of truth)"：`./scripts/build_release.sh "${GITHUB_REF_NAME}"`。本地与 CI 打包是同一脚本——不存在"CI 打的包与文档描述的包不一样"。build_release.sh 自身带产物自校验：版本号推断（tag 或 `dev-<short hash>`）；`npm ci` 仅当 package-lock.json 存在，否则 `npm install --no-package-lock`（注释记录 yarn.lock 平台特定依赖破坏 Linux 构建的历史，ADR-002）；rsync 排除 tests/缓存；run.sh 由 heredoc 现场生成（仓库里没有这个文件）；结尾 `zip -T` 完整性 + REQUIRED 清单逐项核对 + 自查 run.sh 不含硬编码 0.0.0.0。release-package job 再独立复验一遍（注释："build_release.sh self-checks, but assert independently here so a regression in its own verification block cannot pass silently"）。

## 外部连接

上游触发：push/PR 到 main 跑 checks，tag push 跑 release。依赖 09 篇的全部原语（dry-run plan 行、receipt、来源三态）——CI 断言的每一句都锚在安装器的具体行为上。下游：GitHub Release 的 zip 是 README-release 双语文档承诺的全部交付物；run.sh/run.bat 由 build_release.sh 的 heredoc 注入（L95-127 区段），`DATAFLOW_HOST` 默认 `127.0.0.1`、绑定非 localhost 时打印"no authentication is enforced / anyone who can reach this port can run pipelines"两行警告。

## 数据流

PR 提交 → static 五分钟内给出全部负向断言结果（其中 dry-run 断言等价于"三档安装计划此刻是自洽的"）；skills/operator-builder 两条真装线各自在临时环境复现用户视角；release tag push → build_release.sh 在 CI 环境构建（node 20 + python 3.10）→ 产物 zip 附加到 GitHub Release。发布用户解压 → `./run.sh` → uvicorn 起在 127.0.0.1:8000。

## 设计决策（含批判）

**"Release does not bind 0.0.0.0 by default" 是本仓最重的一条断言。** 错误信息原文写得直白："run.sh hardcodes 0.0.0.0 — no auth, and pipelines are arbitrary code execution"。这个服务无认证（CLAUDE.md 钉死单用户本地工具，禁加登录），而 pipeline 执行含 `eval` 动态代码（见 08 篇）——绑定 0.0.0.0 等于把"任意代码执行"开放给局域网。断言不只 grep 禁 0.0.0.0，还要求 `DATAFLOW_HOST` 字符串必须在（文档承诺的逃生口必须真的接线）且 `127.0.0.1` 必须在（默认值必须是它）。批判：开发态 `scripts/start.sh` L23 仍是 `HOST="${DATAFLOW_HOST:-0.0.0.0}"`——双策略并存（详见 12 篇），CI 只守发布包，不守开发脚本。

**负向断言优先于正向测试。** 五个 job 里真正测业务逻辑的只有 backend 的 pytest；其余全在断言"边界没破"。这是对"安装器/生成器/合并器这类代码，回归的代价是破坏用户环境"的准确回应。批判：负向断言是枚举式的——防住了已知的坏法，新的坏法（例如某个新原语忘了实现 dry-run 分支）要等具体事故才会补进清单；`DF_DRY_RUN` 的遵守靠 steps.sh 文件头注释约束，没有自动检测"某函数在 dry-run 下是否真零写"的机制（release-package job 的 git status 断言只覆盖 install.sh 主流程）。

**卸载/误删断言用"内容相同也必须幸存"的最强形态。** install-skills job 最后一步专门构造"用户自装了一个与官方内容完全一致的技能"的场景——因为 `df_install_one_asset` 的来源判断依赖 receipt 而非内容比对，内容相同但无 receipt 就是用户的。把这条边界写进 CI，等于把 09 篇的三态语义钉死成契约。

## 新人提示

1. 改安装器的第一反应应是"CI 的哪条断言会拦我"：加了会写文件的步骤就去想 "Dry run creates nothing" 会不会红；碰了 `.mcp.json` 就想 boundary check；改 run.sh 生成模板就重读 0.0.0.0 断言的三连 grep。
2. 本地复现 CI：`make check` 跑静态部分；release 断言用 `./scripts/build_release.sh ci-test && unzip -Z1 DataFlow-WebUI-ci-test.zip` 对照清单。
3. static job 的 TOML 前置守卫值得模仿：任何"测试 X 会拒绝"的断言，都要先证明 X 不是因为环境缺失而拒绝（否则测的是拒绝本身还是解析器缺失都分不清）。
4. AGENTS.md 的 200 行上限是设计约束不是玩笑：它是 Codex 的路由表，塞满内容等于让 Codex 每次读全部技能——超限时把内容下沉回 `skills/canonical/` 再重新生成。
