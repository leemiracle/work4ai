# 11 · 文档与 ADR：三份架构决策与一次 19 分支审计

## 角色定位

`docs/architecture/` 下三份 ADR（均 2026-07-29 accepted）加一份 branch-audit，构成了这个仓库的"决策记忆"。它们不是事后补写的说明文——每份 ADR 的 Context 节都带着**带数字的事故现场**，Decision 节都连着可执行的 CI 断言（09/10 篇的边界指纹、确定性对账、0.0.0.0 禁令分别是 ADR-003/001/002 的执法形态）。docs 目录本身是纯索引结构：`docs/README.md` 挂三张 profile 说明页、`agents/SETUP.md`（agent 安装程序/授权边界/成功标准）、architecture 与 migration 两组。旧入口 `AGENT_SETUP.md`（仓根）是历史文件，与 `docs/agents/SETUP.md` 并存。

## 内部结构

**ADR-001：技能单一真源。** 决策前同一份技能内容存在于五处：外部 `OpenDCAI/DataFlow-Skills` 仓、本仓 `.claude/skills/`、`.cursor/skills/` 第二副本、`.cursor/rules/` 手写浓缩版、由技能生成的 `AGENTS.md`。实测漂移：四个 SKILL.md 在 Claude 与 Cursor 两处全部不同，Cursor 副本缺了 MCP 规则（"call `validate_pipeline_config` before create/update" 与 init/run 参数桶规则）——后果被一针见血地点破："读 Cursor 副本的 agent 跳过了 Claude 副本要求的校验，产出的 pipeline 在执行时而非创建时失败"；本仓 pipeline 技能六处 `../core_text/` 引用全是死链；`dataflow-dev` 的 "WebUI change policy" 节与已放松该政策的 CLAUDE.md 互相矛盾。决策：`skills/canonical/` 是唯一手编源，agent/profile 差异用文件内**条件指令**表达（`<!-- @if mcp==yes -->`），由 `mcp` 与 per-agent 两个变量驱动渲染；CI 的 `--check` 再生对账让漂移"不可能"而非"不鼓励"。外部 DataFlow-Skills 降级为兼容桥（其安装器委托本仓 skills 档）。三条备选（反向同步/手动多副本/每 agent 独立维护）各有一条具体的否决理由——双向同步正是漂移的成因。运行时面就是 09 篇的 `skills.manifest.json`：`handwritten_cursor_rules` 四条白名单（真手写规则不动）与 `retired_cursor_rules` 两条（重生成时删除）。

**ADR-002：npm 定选。** Context 节罗列的"仓库与自己打架"清单：`frontend/yarn.lock` 被追踪、`frontend/README.md` 教 Yarn、`scripts/setup_all.sh` 跑 `npm install`、`build_release.sh` 有 package-lock 才 `npm ci` 否则绕开（注释明说 yarn.lock 含平台特定 optional 包破坏 Linux 发布构建）、`skills-agent` 分支配过 `cache: npm` + `cache-dependency-path: frontend/yarn.lock` 的不协调组合。决策落在一个点：`installers/config.sh` 钉死 `DF_NODE_PM="npm"`，一切安装路径与文档引用该变量。**最诚实的是 Follow-up required 节**：列出四步未完成事项（Linux 生成 `frontend/package-lock.json` → 验证构建 → 删 yarn.lock → build_release.sh 无条件 `npm ci` + CI 开 npm cache），并承认"在此之前构建不可字节复现"。互证此 follow-up 至今未落地：`frontend/package-lock.json` 当前不存在（实测），`yarn.lock` 仍在——yarn.lock 被定性为"stale artifact, not an input"，即一个被追踪却无消费者的文件。否决 Yarn 的理由务实：每条能用的安装路径和发布管线全得改，而记录在案的 yarn.lock 平台问题 npm 此处没有。

**ADR-003：安装永不写 agent 配置。** 旧 `setup_all.sh` 收尾时调 `setup_agent.sh all` 的两宗罪：用户装本地工具没同意却被改 `$HOME`（无预览）；Cursor 路径仅靠 `grep "dataflow"` 守卫——一个有其他 MCP server 但无 dataflow 条目的用户级配置会被**整文件覆写**。决策拆成两条命令（install / configure-agent）+ 六条规则（默认 project scope、写前 diff、解析器先行只合并不替换、冲突拒绝而非消解、永不碰凭据、幂等），并把边界从文档升格为断言："The boundary is asserted, not just documented"。Codex 特例的处理是全文最见功力的一句：它只读 `~/.codex/config.toml` 且无重定向 flag，所以 `--scope project` 被**拒绝**——"refuse rather than pretend"，拒绝写一个必然被忽略的文件。否决三条备选的理由同样干净：安全默认不该 opt-in、装中提问不可脚本化且易被无脑确认、只写 project 则 Codex 无路可走——答案是知情同意（diff+y/N），不是砍掉路径。

**branch-audit.md：git cherry 方法论。** 2026-07-29 对 main@b64f2b9 的 19 个非 main 远程分支审计。方法论本身就是贡献：ahead/behind 计数在此仓误导（多数分支经 squash/rebase 合并，仍显示"ahead"而补丁早已在 main），所以用 `git cherry origin/main origin/<branch>` 比补丁内容，`-` 号即已入库。结论：16 可删（7 个严格祖先 + 9 个 cherry 全 `-`），3 个有未决工作——`fix/pipeline-compile-check-and-webui-ux`（PR #83 的后续 review 修复 1 commit）、`prompt_para_info`（5 commits，唯一实质未合并特性）、`frontend`（`c8da97f`，349 insertions/8 文件，与前者是**同一特性的两半**）。两个防呆点写成了加粗：**`frontend` 必须不删**（按 commit 数看似可弃，实际有独有工作）；`skills-agent` 是**净回归** ~762 行（main 已含其修复的等价物 `3b08491`，它却缺 LICENSE、compile_check、ray 改进）——"Do not merge it"，并纠正了清理计划 P0-04 的错误记账。推荐序列：先打 `archive/<branch>/日期` tag 再删（提交经 tag 保持可达）、两半特性捆绑裁决（"reviewing either alone will look incomplete"）、保护 main。

## 外部连接

ADR-001 的执法器是 `generate_agent_assets.py --check`（CI static job）与 `check_skills.py`；ADR-002 的事实源被 `config.sh` 消费、被 build_release.sh 的 npm 分支逻辑引用；ADR-003 的边界断言就是 install.sh 的 boundary check（09 篇）与 checks.yml 的 MCP 合并负向断言（10 篇）。branch-audit 的产物流向 git 流程（archive tags、main 保护）。迁移文档 `docs/migration/from-setup-scripts.md` 与 `from-dataflow-skills.md` 分别承接 ADR-003/001 的旧用户。旧脚本 `scripts/setup_all.sh`、`setup_agent.sh` 已是 deprecation 警告壳（10/09 篇）。

## 数据流

ADR 的生命周期：事故/分歧 → Context 记录带数字的证据 → Decision 收敛到单一事实源（canonical 目录 / config.sh 变量 / 命令拆分）→ CI 断言固化 → 后续贡献者改行为时先撞断言、断言报错信息指回修复命令（生成物 banner 与 CI 错误都点名 `skills/canonical/`）。branch-audit 则是单向快照：审计结论转为 tag/删除动作与 PR 待办，不再自动更新——分支状态变化需人工重跑 `git cherry -v`。

## 设计决策（含批判）

**ADR 带 Follow-up required 且明说"决策未完成"**——ADR-002 是范本：接受 npm 的同时公开承认构建不可复现、列四步收尾、说明"这是继承的现状不是本 ADR 引入的，但不该无限期搁置"。批判：四步 follow-up 无 owner、无期限、无 issue 链接，实际状态（package-lock 仍缺）说明它可能被无限期搁置——ADR 文档没有机制跟踪自己的未竟事项。

**git cherry 审计纠正自家计划簿**——branch-audit 对 P0-04 的勘误（skills-agent 从"需 review"改判"已入库且是净回归"）展示了"审计也要审计既有结论"。批判：审计是 2026-07-29 的单点快照，三个月后 `prompt_para_info`/`frontend` 两半特性的 owner 决策若仍未做，漂移成本只会继续涨——文档推荐了"decision date"但没写谁定。

**三份 ADR 同日 accepted**——像一次有意识的仓库治理冲刺（同日还有 skills.manifest 的 P0-09、config.sh 的 P1-06/07 计划项编号）。好处是决策互相咬合（001 的生成物断言依赖 003 的安装边界）；代价是当日之外的决策没有续篇——例如"动态代码 eval"这类安全敏感点（08 篇）没有 ADR 记录权衡。

## 新人提示

1. 改技能相关任何东西前先读 ADR-001 的否决理由——它挡住的三条路（反向同步/多副本/每 agent 独立）正是新人最常直觉选择的方案。
2. 想删一个"看起来没用了"的分支前，跑 `git cherry -v origin/main origin/<branch>` 而不是看 ahead 数；再对照 branch-audit 的三个特例名单。
3. 贡献前端依赖变更时记得 ADR-002 的现状：没有 package-lock，`npm install` 每次重新解析版本——你本地能跑不代表 CI 的树与你相同，锁定问题在 follow-up 落地前一直存在。
4. docs/README.md 是文档的入口表；新增文档先挂索引，check_docs.py 的链接断言（CI static job）会让孤儿/死链文档立刻可见。
