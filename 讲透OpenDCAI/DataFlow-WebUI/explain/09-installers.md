# 09 · 声明式安装体系：install.sh × lib × profiles × manifest

## 角色定位

这一层是这个仓库工程化程度最高的部分：一条 `./install.sh --profile <id>` 命令替代了过去三份复制粘贴的 setup 脚本，并且把"安装器会做什么/不会碰什么"从注释升格为**机器校验的契约**。参与者四类：入口 `install.sh`（486 行，纯流程编排，不含任何具体安装逻辑）；基础设施 `installers/lib/common.sh`（212 行，输出/JSON/版本比较/边界指纹）；原语库 `installers/lib/steps.sh`（465 行，profile manifest 里 `run:` 字段能点名的全部 `df_*` 函数）；声明文件 `installers/profiles/{webui,harness,skills}.json`（三份 manifest，各自声明步骤、预检、验证、禁区）。另有两个配套件：`installers/configure_agent.sh`（agent MCP 配置合并器，ADR-003 拆出来的独立命令）与 `installers/skills.manifest.json`（五技能的单源注册表）。

## 内部结构

**install.sh 四函数骨架。** `usage`（L29-64）输出帮助；`df_receipt_for_target`（L112-118）给每个 skills 目的地派发独立 receipt（路径哈希后缀，项目级与用户级安装互不可删对方的东西）；`df_ensure_uv`（L302-348）处理 uv 缺失——交互终端询问、非交互（CI/agent）自动装，绝不在无法回答的提示符上挂死；`cleanup`（L387）由 `trap ... EXIT` 兜底清 staging。主流程的顺序本身就是安全设计：参数解析（L84-101）→ `configure-agent` 子命令直接 `exec` 转发（L79-82，安装与配置分流）→ `--list`/`--uninstall` 短路 → manifest 解析（L246-251）→ 预检（L287-370，`--check` 到此为止只打印计划 L372-382）→ `mktemp` staging（L385）→ **先拍禁区快照再跑任何步骤**（L392 `df_snapshot_boundaries`）→ 逐步执行（L394-416，每步先试 `skip_if` 实现幂等）→ 边界断言（L418-425）→ verify 阶段（L427-445）→ receipt 落盘（L447-476）。

**common.sh：边界指纹是心脏。** `df_expand_boundary_path`（L101-114）把 manifest 的 `must_not_touch` 条目映射成绝对路径（`~/` 展开、`node_modules` 特判为 `frontend/node_modules`）；`df_boundary_fingerprint`（L116-134）对禁区路径产出"每文件相对路径+内容哈希"的清单；`df_verify_boundaries`（L156-184）安装前后 diff，任何增删改都判违约。`df_json`（L30-45）不假设 jq 存在（macOS/精简 Linux 没有），一切 manifest 读取走 python3。`df_check_prereq`（L70-98）的注释记录了一个真实教训：天真地剥离非数字会把 "pip 21.2.4 ... (python 3.9)" 拼成 bogus 版本号 21.2.43.9，所以只取第一个版本样式 token（L84-89）。哈希函数三级降级 shasum→sha256sum→wc -c（L186-195）。

**steps.sh：每个原语都要幂等 + 尊重 DF_DRY_RUN。** 文件头两条军规（"Each function must be idempotent"、"must honour DF_DRY_RUN by printing what it would do and changing nothing"）贯穿全部函数：`df_pip_install` dry-run 打印 plan 行、真跑走 uv（`df_uv_system_flag` 用 `sys.prefix != sys.base_prefix` 判 venv 决定要不要 `--system`）；`df_dataflow_framework_ready` 锁死 `open-dataflow==1.0.10`——注释解释了为什么不能只试 import："一个陈旧的 editable checkout 可以 import 却暴露不同的 CLI 与算子集"；`df_init_dataflow_core` 对不完整的 core 目录拒绝合并（宁可失败不留半成品）。最精细的是 `df_install_one_asset` 的**来源三态**：目标不存在→装并记 receipt；内容相同→skip 且**不记录**（uninstall 绝不能删它没写过的东西）；内容不同→只有 receipt 哈希能证明"这是我们自己写的旧产物"才 refresh，否则一律保留并警告"re-run with --force"——用户的任何手工修改都不可被静默覆盖。`df_install_agent_assets` 的注释记录了历史事故：早期版本整目录替换 `.cursor/skills/`，删掉过用户自写的技能，现在是逐条目安装。

**三份 profile 的差异化全部在声明里。** webui（7 步：open-dataflow→backend 依赖→前端构建→core 初始化→生成技能→装技能→装 agent 资产）；harness 砍掉 frontend-build（6 步），`must_not_touch` 加列 `node_modules`、`frontend/package.json`——注释明说这个 profile 必须能在完全没有 Node.js 的机器上装（计划项 P1-05）；skills 只剩三个纯文件步骤（不装任何包，Python 3.9 即可，"runs the skill generator only; not installed into"）。同一个 `df_install_skills core harness standalone` 调用，webui/harness 传三层、skills 传 `core standalone`——MCP 相关技能（harness 层）天然不进纯技能档。

**configure_agent.sh：合并器而非写入器。** `merge_mcp_json`（L158-183）委托 `lib/mcp_json_config.py`：先验证可解析（exit 3 绝不回写）、拒绝改向他人配置（exit 4 须 `--force`）、保留全部其他键。三家 agent 各有现实约束被如实建模：claude 只认启动目录的 `.mcp.json`，`--scope user` 直接劝退退出（L238-243）；cursor 双 scope 都行；codex 只读 `~/.codex/config.toml` 且无重定向 flag，`--scope project` 会被**拒绝**而非写一个被忽略的文件（L271-281，exit 2）——"拒绝比假装成功诚实"。user scope 强制 diff 预览 + y/N 确认（L113-126）。

**skills.manifest.json：五技能单源。** 每个 skill 声明 id/canonical 路径/layer/agents/summary：`generating-dataflow-pipeline`（layer=core，三档全带）、`dataflow-dev`、`dataflow-operator-builder`、`prompt-template-builder`（standalone）、`core_text`（standalone，`kind: reference`、`invocable: false`，"read by generating-dataflow-pipeline, never invoked directly"）。同文件还管 routing_triggers（AGENTS.md 路由表的话术）、四个手写 Cursor 规则的白名单、两个已退役规则名（重生成时删除）。

## 外部连接

上游是用户与 CI：checks.yml 的 `static` job 对三档各跑一次 `--dry-run` 并断言工作树零改动；`install-skills` job 真装 skills 档并验证幂等/卸载/不误删。下游是 `generate_agent_assets.py`（staging 里渲染三 agent 技能包）、`backend/requirements.txt`、npm（`config.sh` 钉死 `DF_NODE_PM="npm"`，ADR-002）、`scripts/start.sh`（next_steps 指向它）。旧入口 `scripts/setup_all.sh`/`setup_agent.sh` 降级为打 deprecation 警告的转发壳。`Makefile` 提供 `make skills`（生成资产）与 `make check`（本地复跑 CI 静态检查）。

## 数据流

一次 `./install.sh --profile webui`：读 manifest → 打印 will/won't install 清单 → 预检（python/node/npm 版本）→ mktemp staging → 对 5 个禁区路径逐文件拍哈希快照 → 逐步执行：pip/uv 装 open-dataflow 与 backend 依赖、npm 构建前端、`dataflow.cli init` 初始化 core、生成器渲染技能进 staging、逐技能带来源检查复制进 `.claude/skills`、装 Cursor/Codex 资产 → 全部步骤后 diff 禁区快照（违约即 exit 1）→ verify 五项（import app.main / dist 存在 / MCP 白名单 / 技能 SKILL.md / agent 资产）→ 把本次真正写入的路径+树哈希写进 `.dataflow-install/receipt-<hash>`。

## 设计决策（含批判）

**声明式 profile + 受限原语**——manifest 的 `run:` 只能点名 common.sh/steps.sh 里评审过的函数（common.sh 头部注释明示），不能任意 shell。这是"一条流程而非三份拷贝"的实现根基，三档防漂移由此变成结构性质。批判：`skip_if`/`run` 终究是 `eval` 的字符串（install.sh L405/L411），原语白名单靠约定而非解析器强制；好在 steps.sh 函数面窄、CI 有 dry-run 断言兜底。

**来源三态 + receipt 哈希**——安装器对"不属于我的文件"零触碰、卸载对"变过的文件"零删除，是这套体系最值得抄的设计。批判：receipt 是文本文件无签名，用户手工把某技能改回与安装时完全一致的内容会被误判为"未变过"而可删——概率低但语义上"内容哈希=来源证明"是近似而非证明。

**uv 默认 + pip 显式回退**——新工具更快但承认环境多样。批判：非交互场景自动 `curl | sh` 装 uv（L325-327）在离线/受管环境会失败得很吵，错误信息倒是把 `--pip` 逃生口写在每一层。

## 新人提示

1. 加一个安装步骤的正确位置：steps.sh 写幂等原语 → 对应 profile 的 JSON 加 step（带 `skip_if` 与 `produces`）→ 若它可能碰禁区，先想清楚要不要进 `must_not_touch`。直接在 install.sh 里写命令是违规。
2. 调试用 `--dry-run --verbose`：每个原语都会打印 plan 行，禁区快照/断言全流程可见且零副作用，CI 正是用此特性做回归。
3. 改了 `skills/canonical/` 之后要 `make skills` 重新生成三处资产；CI 的 `--check` 会 diff 出任何手改生成物的漂移（ADR-001）。
4. 想知道"这台机器上装过什么、能不能干净卸载"，直接看 `.dataflow-install/receipt-*`：第一行是 skills 目的地，其后每行 `路径\t哈希\t标签`。
