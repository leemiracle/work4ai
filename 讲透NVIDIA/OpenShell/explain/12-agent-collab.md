# 12 · Agent 协作层：双层技能体系、AGENTS.md 总纲与 reviewer 记忆体

## 一、角色定位

这个仓库把 coding agent 当**一等协作者**来经营。AGENTS.md 开宗明义："OpenShell is built agent-first. We design systems and use agents to implement them — this is not vibe coding"——产品是给自主 agent 用的安全沙箱，项目自身又用同一套 agent 工作流开发（自举）。整个协作层四件套：`AGENTS.md` 总纲（注入每次交互的主指令面）、`CLAUDE.md`（全文就一行 `@AGENTS.md`——Claude Code 引用语法，单一事实源零复制）、`.agents/skills/` 内部贡献者技能、`skills/` 公开使用技能。外加 `.claude/agents/` 与 `.opencode/agents/` 的跨 harness reviewer 人格及其持久记忆。AGENTS.md 自己提醒读者："Do not rely on this file for a full inventory"——完整技能表在 CONTRIBUTING.md。

## 二、内部结构

**双层技能体系**。公开层 `skills/` 四个：debug-inference、debug-openshell-cluster、generate-sandbox-policy、openshell-cli——设计约束是"必须在源码 checkout 之外可用"，事实源是已安装 CLI 的 help 与已发布文档（CONTRIBUTING.md:86），用户 `npx skills add NVIDIA/OpenShell` 安装。内部层 `.agents/skills/` **18 个**技能（build-from-issue / build-openshell-mxc-windows / create-github-issue / create-github-pr / create-rfc / create-spike / fix-security-issue / helm-dev-environment / launch-openshell-gator / review-github-pr / review-security-issue / sbom / sync-agent-infra / test-release-canary / triage-issue / tui-development / update-docs / watch-github-actions），全部带 `metadata: internal: true`——CONTRIBUTING.md:90 澄清这是**发现过滤器不是访问控制边界**。技能可携带自己的 agent 配置（create-rfc/agents/openai.yaml）。每个 SKILL.md 是 frontmatter（name/description/触发词）+ 工作流正文，如 create-rfc 的八步流程（读 rfc/README → 选下一个 NNNN → 拷模板 → "Preserve uncertainty in Open questions instead of silently deciding unknowns"）。

**`sync-agent-infra` 是体系的自反维护技能**：一张"改了什么→检查哪些技能"的维护映射表（issue/PR 惯例→四个技能；CLI 变更→openshell-cli；发布工件→test-release-canary……），在动工作流相关的 PR 前跑。

**Reviewer 人格双注册**。`.claude/agents/principal-engineer-reviewer.md` 与 `.opencode/agents/principal-engineer-reviewer.md` 同一人格两份 harness 配置；.claude 版 frontmatter 声明 `memory: project` + 工具白名单（Read/Grep/Glob/Bash/WebFetch/WebSearch）。人格定义三等权优先级（务实/用户共情/安全），安全审查框架直接点名 **CWE / OWASP ASVS Level 3 / OWASP Top 10 for LLM Applications（特指 Insecure Plugin Design 与 Prompt Injection）/ CAPEC**；还有一整套"务实校准"细则（预存在缺陷不阻塞、无证据不挖旧代码、修复方案要与风险成比例）与 LSM 兼容性清单（SELinux 下 `/proc/<pid>/exe` 跨域 readlink 返回 ENOENT 这类实战坑）。`memory: project` 落地为 `.claude/agent-memory/principal-engineer-reviewer/MEMORY.md`——项目结构速查 + 观察到的评审偏好（"Conventional commits required""**No AI attribution in commits**"）。

## 三、外部连接

- **Gator 自举闭环**：`launch-openshell-gator` 技能操作 `scripts/agents/run.sh` 拉起无头 gator 沙箱 agent 跑 issue/PR 验证，评审策略是烧进 gator payload 的 `gator-gate` 技能——**用 OpenShell 沙箱审查 OpenShell 的 PR**，reviewer 人格里"When the task supplies the Gator review findings contract, return only its JSON envelope"就是对接这条线。
- **rfc/ 流程**：0000-template + 0001~0014（编号有洞：0007/0008 不存在），create-rfc/review 技能与 RFC 目录互为表里；RFC 0010（gateway interceptors）、0012（isolation backend）、0013（native Windows MXC）直接对应前三篇讲过的子系统。
- **`.claude/README.md` 钉版权属**："Agent skills are canonical in `.agents/skills/` and shared across all harnesses…This directory contains only Claude Code-specific configuration"——.claude/ 只留 harness 特有的东西（人格 frontmatter、运行时记忆）。
- **CONTRIBUTING.md** 是人类侧入口：CONTRIBUTING.md:16 "Do use the skills"；CONTRIBUTING.md:69 强调 agent 转录不能替代贡献者自己的理解（PR 要解释改了什么怎么测的）。
- `.agents/skills/create-rfc/agents/openai.yaml` 表明技能包还能携带第三方 harness 的 agent 配置。

## 四、数据流

贡献一条 PR 的 agent 全流程：认领 issue（triage-issue → create-spike/build-from-issue）→ 设计走 create-rfc 出 RFC 草案 → 实现（AGENTS.md 的架构表与 proto/README 约束在上下文里）→ 自测（TESTING.md/CI.md + tasks/*.toml）→ create-github-pr（模板含 vouch 行为约定，review-github-pr 引用同一惯例）→ reviewer 人格（或 gator 沙箱）审阅，产出 Critical/Warning/Suggestion 分级 findings，跨修订版靠"prior review feedback ledger"不重翻旧账 → 合并前后 sync-agent-infra 对账技能/文档/模板是否同步 → watch-github-actions 看 CI。reviewer 的记忆体跨会话累积：MEMORY.md 记项目结构与偏好，下次会话直接带着历史判断开工。

## 五、设计决策

1. **单一事实源的指令文件**：CLAUDE.md 引用 AGENTS.md 而非复制，跨 harness 一份内容多份入口——`.claude/`、`.opencode/` 只存"翻译层"。
2. **公开/内部技能物理分目录 + 元数据标记**，而不是仓库分家：内部技能留在仓里让"repository-aware harness 原生发现"（AGENTS.md），同时 Agent Skills CLI 靠 internal 标记过滤公开市场——一个目录树两种可见性。
3. **技能=流程的代码化**：18 个技能覆盖从 issue 到发布的完整生命周期，等于把 maintainer SOP 变成 agent 可执行资产；sync-agent-infra 再给这套资产配了"改 A 必查 B"的一致性守卫。
4. **记忆体 harness 私有、人格跨 harness 公有**：MEMORY.md 明说"Claude Code runtime state, not portable across tools"——把会腐烂的状态与可移植的定义分开。
5. **Gator 是产品的持续自证**：吃自己的狗粮不是口号而是 PR 门禁。

## 六、新人提示

- **勘误一：内部技能是 18 个不是 20 个**（`ls .agents/skills/ | wc -l` 实测；任务书口径 20 已过期——技能集合在活跃增删，引用数量前先数）。
- **勘误二：AGENTS.md 架构表列了 `.agents/agents/`（"Sub-agent definitions (e.g., reviewer)"，该目录并不存在**——人格实际在 `.claude/agents/` 与 `.opencode/agents/`。文档漂移的活例。
- **勘误三：sync-agent-infra 维护映射引用 `update-docs-from-commits`，实际目录名是 `update-docs`**——照表跑核对时会扑空。
- **记忆会过期**：MEMORY.md 还指着 `crates/openshell-server/src/grpc.rs` 单文件（现为 grpc/ 目录，见第 07 篇）——agent 记忆是缓存不是真理，落地前照记忆里的路径 ls 一下。
- 提交规范两条硬规矩来自记忆体：Conventional commits、**提交里禁止 AI 署名**。
- 别把 `metadata: internal: true` 当权限控制（CONTRIBUTING.md:90 原话），敏感操作的安全边界在仓外（SECURITY.md 流程 + fix-security-issue/review-security-issue 技能），不在技能可见性上。
