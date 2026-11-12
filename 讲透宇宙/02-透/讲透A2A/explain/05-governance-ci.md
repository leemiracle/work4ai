# 05 · 治理与 CI 体系：规范仓的质量生产线

> 对应图谱 8 层架构中的 L06「治理与社区」（18 节点）与 L07「CI 与 lint 体系」（28 节点），tour 第 6/7 步。本文全部事实取自仓内源文件（路径相对仓根），行号经逐条 grep 核实；推断处显式标注。

## 角色定位

A2A 是一个「规范优先」的仓库：真正的产品是 `specification/a2a.proto` 和围绕它的文档，代码只有 9 个 shell/Python 脚本。这种仓型决定了它的两条治理主线：

**主线一：社区治理（L06）**。项目由九家公司组成的 TSC（Technical Steering Committee）掌舵——GOVERNANCE.md:3 明言 "The Committee has nine seats"，GOVERNANCE.md:7-15 列出 Google/Microsoft/Cisco/AWS/Salesforce/ServiceNow/SAP/IBM/Bloomberg 九席代表。治理不是纸面文章：`.gitvote.yml` 把投票规则做成机器可读配置（pass_threshold: 51，见 `.gitvote.yml:30`），`adrs/` 把 TSC 决策固化为 ADR 文档，CODEOWNERS 把最敏感文件（章程、投票配置、License）锁成 TSC 独占审批（CODEOWNERS:16-19）。

**主线二：代码与文档质量（L07）**。`.github/workflows/` 下 11 个 workflow 构成一条完整生产线：commit 规范（conventional-commits）→ 聚合 lint（super-linter）→ 拼写（check-spelling）→ 链接（lychee）→ 文档构建（mkdocs）→ 自动发布（release-please）。规范仓的「代码」主要是 Markdown 和 proto，所以 lint 栈的重心是 markdownlint（`linters/.markdownlint.json`）、protolint（`linters/.protolint.yaml`）和 api-linter（linter.yaml:31 的独立 job），而非传统编译器。

两条线在 ADR-001 汇合：那次 TSC 投票决定了 proto→JSON 的序列化规范，决策人一栏写着 "Technical Steering Committee (TSC)"（`adrs/adr-001-protojson-serialization.md:7`）——治理层的技术裁决直接落成了今天的协议语义。

## 内部结构

### 治理文档链

链路是「章程分级 → 机器投票 → 决策记录」三级：

- **GOVERNANCE.md**（86 行）是总章程。关键条款：TSC 现处于 Startup Phase，每家组织任命一名投票成员（GOVERNANCE.md:34）；18 个月后转入 Steady State 重新议定产生方式（GOVERNANCE.md:38）；表决需过半数出席的法定人数（quorum 为全体投票成员的 50%，GOVERNANCE.md:71）；连续六周不出席会议（以 LFX 考勤为准）的成员转为不活跃、不计入法定人数（GOVERNANCE.md:73）。
- **.gitvote.yml** 把章程投票条款翻译成 GitVote 机器人配置：投票期长达 52 周、通过门槛 51%（`.gitvote.yml:29-30`）、允许投票者限定 `a2a-tsc` 团队（`.gitvote.yml:34`）、通过即自动关票（`.gitvote.yml:36`）、结果广播到 GitHub Discussions 的 announcements 分类（`.gitvote.yml:38-39`）。51% 门槛与章程「majority vote」一一对应，这是「章程可执行化」的样本。注意 `.gitvote.yml:9-26` 的 automation 段整段是注释掉的示例——当前没有任何按路径自动开票的规则（推断：TSC 更倾向手动开票）。
- **adrs/** 目前两件：`adr-template.md`（Nygard 风格模板：Context/Decision Drivers/Considered Options/Consequences）与 `adr-001-protojson-serialization.md`（2025-11-18，Accepted）。ADR-001 记录了采用 ProtoJSON 的完整权衡，负作用写得毫不客气：枚举值改用 SCREAMING_SNAKE_CASE 属破坏性变更（adr-001:52）、未知字段无法 roundtrip（adr-001:53），但决策「reversible」（adr-001:36）。
- **MAINTAINERS.md** 按 8 个子仓（a2a/a2a-dotnet/a2a-go/a2a-java/a2a-js/a2a-python/a2a-rs/a2a-samples）列 role:maintain 与 role:admin 两组名单（MAINTAINERS.md:9 起本仓 4 名 maintainer）。注意它与 CODEOWNERS 是两套体系：前者是「谁有权合并」的人册，后者是「谁被强制拉进 review」的路径映射。
- 配套件：SECURITY.md 全文仅 7 行，安全漏洞只走 GitHub Security Advisories 私密通道（SECURITY.md:3）；PULL_REQUEST_TEMPLATE/become_a_repo_maintainer.md 是申请 maintainer 身份的专用模板，明言 "TSC voting majority will be required"（become_a_repo_maintainer.md:11）。

### 11 个 workflow 的分工

按触发方式分三组：

**PR 门禁组（5 个）**：conventional-commits.yml（PR 标题校验）、spelling.yaml（拼写，全分支）、linter.yaml（super-linter + api-linter）、links.yaml 的 PR job（只查变更文件里的链接）、sort-spelling-allowlist.yml（allow.txt 排序回写）、check-linked-issues.yml（PR 必须关联 issue，用 `pull_request_target` 以仓库权限运行，check-linked-issues.yml:4）。

**main 推送组（3 个）**：docs.yml（构建并部署文档站）、release-please.yml（自动攒 CHANGELOG 与 Release PR）、dispatch-a2a-update.yml（specification/** 一变就通知 a2a-python 仓，dispatch-a2a-update.yml:20-21）。

**定时组（3 个）**：links.yaml（每日 06:00 UTC 全站链接巡检，links.yaml:7）、stale.yaml（每日 22:30 UTC 标记不活跃 issue/PR，stale.yaml:11）、issue-metrics.yml（每月 1 日 02:03 UTC 出上月 issue 报告，issue-metrics.yml:5）。

### lint 三层栈

第一层是 **super-linter 聚合器**：linter.yaml:27 用 `super-linter/super-linter/slim@v8` 镜像，linter.yaml:22-24 先把 `.github/super-linter.env` 过滤空行注释后注入 `GITHUB_ENV`。该 env 开了 16 类校验（VALIDATE_BASH/MARKDOWN/PROTOBUF/YAML 等，super-linter.env:4-19），并声明 `VALIDATE_ALL_CODEBASE=false`（super-linter.env:2，只 lint 变更文件）与排除规则 `FILTER_REGEX_EXCLUDE`（super-linter.env:3，把 .github/、.vscode/ 及四份治理文档挡在门外）。Python 规则由 `VALIDATE_PYTHON_RUFF=true`（super-linter.env:15）交给根目录 `.ruff.toml`——那份 125 行配置逐条对照 Google Python Style Guide（`.ruff.toml:8` 的 80 列限宽即引 §3.2），并全面禁用相对导入（`.ruff.toml:110`）。

第二层是 **各语言独立 linter**：api-linter 作为独立 job 跑在 super-linter 之外（linter.yaml:31-63），用 v1.67.6 二进制（linter.yaml:55）加 `specification/.api-linter.yaml` 规则集对 `specification/a2a.proto` 做 Google AIP 合规检查（linter.yaml:63）。该规则集禁掉了 16+ 条 AIP 规则（specification/.api-linter.yaml:6-21 起，如 `core::0140::abbreviations`），另有一批标着 TODO 待评估（specification/.api-linter.yaml:23-30）——proto 是协议契约，AIP 的 request/response 命名类规则与 RPC 风格冲突，只能逐条豁免。

第三层是 **细配置**：`linters/` 下 5 件（任务书以为 6 件，实为 5）——`.markdownlint.json` 关掉行宽 MD013/重复标题 MD024（linters/.markdownlint.json:3,9），`.protolint.yaml` 只移除 MAX_LINE_LENGTH 一条规则（linters/.protolint.yaml:4），`.eslintrc.js`/`.stylelintrc.json`/`.jscpd.json` 分别管 TS、CSS/SCSS、复制粘贴检测（jscpd 阈值 3 行且忽略 samples/tests，linters/.jscpd.json:11）。

### spelling 自动回写环

拼写系统是「检查 + 自动修复」闭环：

- spelling.yaml:30 用 `check-spelling/check-spelling@v0.0.26`，只查 PR 变更文件（spelling.yaml:78 `only_check_changed_files: true`），词典从 cspell 官方仓库按前缀拉 34 部（spelling.yaml:41 定义 `dictionary_source_prefixes` 指向 cspell-dicts，spelling.yaml:42-76 从 aws/software-terms 到 typescript）——所以「cspell」在本仓只是词典源，引擎是 check-spelling。
- 词表资产在 `.github/actions/spelling/`：`allow.txt`（420 行白名单）、`excludes.txt`（93 行排除规则，把二进制/锁文件/CI 自身全排除，excludes.txt:83-92 连 spelling workflow、lychee.toml 都不查）、`expect.txt`（11 个暂挂词条，如 AWS 代表的姓 Siwach/Abhimanyu——与 GOVERNANCE.md:10 同源，推断为待定夺的过渡清单）、`line_forbidden.patterns`（299 行正则禁令，远超拼写范畴：禁 `GenAI` 拼法（:158）、禁 "Google Gemini's Gemini" 式营销措辞（:194）、禁智能引号（:287）、禁 Google 内网链接 corp.google.com 泄漏（:293））。
- 回写环：sort-spelling-allowlist.yml:3-10 监听任何动了 `allow.txt` 的 PR，跑 `scripts/sort_spelling.sh`（内部就一句 `LC_ALL=C sort -u`，sort_spelling.sh:16，按字节序排序去重），同仓分支由 bot 自动 commit "ci: sort and unique allow.txt"（sort-spelling-allowlist.yml:47），fork 分支则直接报错要求贡献者本地跑（sort-spelling-allowlist.yml:53）。配套细节：spelling.yaml:23-26 的 concurrency 组特意 `cancel-in-progress: false`，注释说明因为用了 only_check_changed_files，bot 自己的回写 push 不能把进行中的检查取消掉。

## 外部连接

**conventional-commits 的路径感知是整个仓的枢纽**。它用 dorny/paths-filter 先判 PR 动了什么（conventional-commits.yml:25-32）：动了 `docs/specification.md` 而没动 proto，标题必须 `docs(spec):` 且 scope 强制（conventional-commits.yml:36-46 `requireScope: true`）；动了 `specification/a2a.proto`，标题必须是 feat/fix/chore/refactor 且禁用 spec scope（conventional-commits.yml:50-62）；其余情况走通用清单（docs/chore/ci/test/refactor/style/perf/build/revert，conventional-commits.yml:72-81）。这个分类直接驱动两条级联：其一，docs.yml:15 把 `specification/a2a.proto` 列入触发路径，proto 一改文档站必须重建（JSON schema 从 proto 再生成）；其二，CONTRIBUTING.md:86-87 的 TIP 反向要求「改文档若影响协议用法，顺手也改 .proto 触发新协议发布」——人机两侧共同保证规范双源同步。

**跨仓通知**：dispatch-a2a-update.yml 监听 main 上 specification/** 的推送（dispatch-a2a-update.yml:7-8），用 `A2A_BOT_PAT` 令牌向 a2a-python 发 `repository_dispatch` 事件 `a2a_json_update`（:20-21），附带 ref/sha/message 载荷——SDK 仓据此重新生成绑定。同一枚 bot 令牌也用于 release-please.yml:20，说明存在一个跨仓的机器人身份。links.yaml:4 自身也挂了 `repository_dispatch` 入口，即本仓链接检查可被外部触发。

**dependabot 的真实策略（勘误）**：任务书与图谱批次记载本仓 dependabot 为「全 ecosystem limit: 0、只留安全 PR」（agentgateway 先例），经源码核实**不成立**。`.github/dependabot.yml` 实际是三路 monthly 分组更新：npm（/types 目录，dependabot.yml:3-10）、github-actions（dependabot.yml:11-18）、pip（dependabot.yml:19-26），每路 `groups` 都以 `patterns: '*'` 把所有依赖并成单 PR；文件中不存在任何 `open-pull-requests-limit` 字段。git 历史同样反证：commit 1205f459 就是 dependabot 一次「bump the github-actions group with 4 updates」的常规功能更新 PR。agentgateway 的 limit: 0 策略是那个仓的，不能外推到 A2A。

**release-please 自动 CHANGELOG**：release-please.yml:18-21 用 googleapis/release-please-action@v5、release-type simple，从 conventional commit 标题自动攒出 Release PR 与根目录 CHANGELOG.md——这就是为什么标题 lint 如此严苛：标题即 changelog 语料。links.yaml 的 exclude_path 也把 `CHANGELOG.md` 排除出链接检查（lychee.toml:80，机器生成文件不背死链责任）。

## 数据流

一次普通文档 PR 的门禁旅程（时间序）：

1. **PR 创建/更新**。三个 workflow 同秒起跑：conventional-commits（标题三选一校验）、spelling（只查变更文件）、check-linked-issues（`pull_request_target` 反查正文里的 "Fixes #N"）。PULL_REQUEST_TEMPLATE.md:7 把标题规则直接印在模板里提醒贡献者。
2. **改动落盘后**。若 PR 只碰 md，links.yaml 的 PR job 用 tj-actions/changed-files@v47（links.yaml:36）筛出 *.md/*.mdx/*.html 等文件，逐个过 lychee（links.yaml:60 带 `--config lychee.toml`）；若碰了 docs/**/mkdocs.yml/requirements-docs.txt/a2a.proto（docs.yml:19-27），docs.yml 加跑一次 `mkdocs build` 纯校验不部署（docs.yml:108-110）。
3. **lint 主门禁**。linter.yaml 两个 job 并行：super-linter 按 env 白名单跑 16 类校验；api-linter 仅在 proto 变更时有实质内容。
4. **拼写失败时**。check-spelling 在 PR 上留评（advice.md:6-17 指导贡献者分流：该排除进 excludes.txt、该写正则进 patterns.txt）；若只是加词，贡献者改 allow.txt 会触发 sort-spelling-allowlist.yml 自动排序回写，回写 push 又会重跑 spelling（这就是 cancel-in-progress 必须为 false 的原因）。
5. **merge 进 main**。release-please 汇拢 commit 攒 Release PR；docs.yml 部署 dev 版并设 latest 别名（docs.yml:112-121，mike deploy --push --update-aliases dev latest，再跑 deploy_root_files.sh 部署 404 页）；若动了 specification/**，dispatch 通知 a2a-python。
6. **release published**。docs.yml:123-137 用 release tag 名部署正式版并覆盖 latest。
7. **日常无人值守**。每日 06:00 UTC links.yaml 全量 job：先完整构建文档站（links.yaml:117-118 复用 build_docs.sh），清缓存（links.yaml:121），再对 site/ 目录全站扫链（links.yaml:132 用 `--root-dir` 解决根相对链接）；失败则 create-issue-from-file 开/复用 "Link Checker Report" issue（links.yaml:139-144），成功则用 gh CLI 自动关闭上次的报告 issue（links.yaml:159-160）。同一时刻线上还有 stale 机器人在 14 天无活动后打标、再 13 天后关闭（stale.yaml:26-27），但只作用于带 `status:awaiting response`/`status:more data needed` 标签的条目（stale.yaml:30），`override-stale` 标签可豁免（stale.yaml:47-49）。

防误触发的保险丝贯穿全程：docs.yml:45 与 links.yaml:25/67 都有 `if: github.repository == 'a2aproject/A2A'`/事件名判断，确保 fork 与非 PR 场景不会消耗部署令牌；release-please 与 dispatch 也限 `github.repository_owner == 'a2aproject'`（release-please.yml:15）。

## 设计决策

**lychee 版本钉死避 CVE（links.yaml:52-58 注释原文给出三层理由）**：action 钉在 v2.9.0，一是 CVE-2024-48908 要求 ≥2.0.2；二是 ≥2.6.1 才把 lychee tarball 解压到 RUNNER_TEMP，否则其自带 docs/README.md 会覆盖本仓同名文件；三是 lychee **二进制**版本刻意不钉——注释明说 Dependabot 看不见 `lycheeVersion` 输入参数，显式钉死会「goes stale silently」，继承 action 默认值反而让两者保持同步。这个决策同时反证 dependabot 的 github-actions 更新通道是活跃且被依赖的（git 历史的 7295b180 "chore: bump lychee version" 即其产物）。

**链接检查的反误报工程**。lychee.toml:11 把 403/429/503 也列为可接受状态码（反爬与限流常态）；失败重试 3 次、每次间隔 30 秒（lychee.toml:111,114，注释估算每 URL 约 90 秒以压速率限制误报）；exclude 名单里 40+ 条模式每条都有归因注释，例如合作方站点 crubyt 证书过期但特意保留 partners.md 本身受检（lychee.toml:35-37）、mkdocs-material 注入的 Google Fonts 根路径对 HEAD/GET 返回 404（lychee.toml:70-72）。PR 增量查与全站查共用一份 toml，但 exclude_path 用两段式覆盖源文件（lychee.toml:84-93）与构建产物（lychee.toml:94-104）两套路径。

**本地 lint.sh 与 CI 同栈双跑（有注释佐证）**。scripts/lint.sh:14-15 注释原文 "This mirrors the configuration used in GitHub Actions to provide consistent linting behavior"，实现上是 `--env-file` 直接挂载 CI 同一份 `.github/super-linter.env`（lint.sh:24），镜像也用同一个 `ghcr.io/super-linter/super-linter:slim-v8`（lint.sh:25）——不是「同款配置」而是「同一份配置文件」，杜绝本地/CI 漂移。代价是贡献者必须装 Docker（CONTRIBUTING.md:14 明示 "Required for running the local linter"）。

**拼写治理选择 bot 回写而非人工纪律**。允许列表的排序一致性不靠 review 把关，而是让机器人直接替你 commit（同仓分支）或挡你（fork 分支）。为什么用 `LC_ALL=C`：固定字节序排序，使任何环境本地跑 sort_spelling.sh 结果与 CI 逐字节一致（推断依据：脚本仅此一行实质逻辑，且 workflow 用 `git diff --quiet` 判定零差异）。

**过滤式 lint 而非全量**。super-linter.env:2 关掉全仓扫描省时间；但 super-linter.env:3 同时排除治理四文档（CODE_OF_CONDUCT/CHANGELOG/GOVERNANCE/MAINTAINERS）——法定文本与机器生成物不接受 lint 改写（推断：这些文件的措辞稳定性优先于格式规范）。

**已发现的死配置块（坑）**：`.github/conventional-commit-lint.yaml` 全文仅 2 行（`enabled: true`/`always_check_pr_title: true`，conventional-commit-lint.yaml:1-2），由 commit fe760439 添加，但当前仓内无任何 workflow 或脚本引用它——实际标题校验规则全部内联在 conventional-commits.yml 的三个 step 里。推断它服务于某个外部 lint 集成或历史方案，如今是孤儿文件；改 commit 规则时别改它，要改 workflow。

## 新人提示

**提交前本地检查清单**（按 CONTRIBUTING.md:102-109 工作流压缩）：

1. `./scripts/format.sh` 自动修 markdown 格式；`./scripts/lint.sh` 跑与 CI 完全同栈的 super-linter（需 Docker）。
2. 先想清楚动了哪类文件再写 PR 标题：规范文档 `docs(spec):`、一般文档 `docs:`、proto 专属 `feat:`/`fix:`——改错 scope 会在标题门禁直接红。
3. PR 正文写 `Fixes #<issue号>`，否则 check-linked-issues 会拦（release/dependabot/release-please 分支豁免，check-linked-issues.yml:18）。
4. 改文档若影响协议语义，记得顺手碰一下 a2a.proto（哪怕只改注释），否则不会触发协议发布（CONTRIBUTING.md:87）。

**spelling 误报处理三步**（advice.md:6-17 官方分流）：整文件不该查 → excludes.txt 加路径正则；可用正则刻画 → patterns.txt；确系合法词汇 → allow.txt 加词，然后**本地跑 `bash scripts/sort_spelling.sh`**——否则 bot 会替你排序再提交一次，fork PR 则直接红（sort-spelling-allowlist.yml:53）。专有名词先查 allow.txt/expect.txt 是否已在；品牌写法看 line_forbidden.patterns 的判例（如必须写 "Gen AI" 不写 GenAI）。

**ADR 流程**：影响协议互操作性的决策走 TSC——复制 adrs/adr-template.md 起草（Status 置 Proposed），提交 PR（adrs/ 目录归 TSC+project-maintainers 审，CODEOWNERS:11），TSC 投票（现在经 GitVote 机器人，51% 过线即自动关票）后置 Accepted。ADR-001 是范本：连负作用与「可逆性」都成文。

**值得知道的坑**：

- conventional-commit-lint.yaml 是死配置，真规则在 workflow 内联（见上文设计决策）。
- 改 .github/workflows/ 自身也会触发 docs/links 重建（两者 paths 都含自家 workflow 路径，docs.yml:8/links.yaml:12），提 CI PR 时别对「为什么文档检查也跑了」惊讶。
- dependabot 每月会同时开 3 个分组更新 PR；lychee 二进制随 action 默认值走，别在 workflow 里手钉 `lycheeVersion`（links.yaml:55-57 注释解释了为何那是陷阱）。
- spelling job 在**所有分支**开（spelling.yaml:5-6 `"**"`），包括你尚未提 PR 的 WIP 分支 push；dependabot 的 push 被显式抑制（spelling.yaml:32）。
- MAINTAINERS.md 列的是全部 8 个子仓的权限名册，本仓（a2a 小节，MAINTAINERS.md:7-13）只有 4 名 maintainer；想加入按 become_a_repo_maintainer.md 模板提 PR，需 TSC 多数票批准。
- 治理文档改动（GOVERNANCE/.gitvote/LICENSE/CODEOWNERS）只有 @a2aproject/a2a-tsc 一个团队能批（CODEOWNERS:16-19），普通 maintainer 的 review 不算数。
