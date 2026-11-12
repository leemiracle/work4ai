# codex-plugin-cc 新人上手指南（ONBOARDING）

仓库：openai/codex-plugin-cc（本地 `/usr-data/data2/repos/agent-repos/openai/codex-plugin-cc`，HEAD db52e28，版本 1.0.6）。行号锚以该 commit 为准。

## 1. 插件定位与分发（.claude-plugin/marketplace.json）

OpenAI 官方的"反向桥"：把 codex CLI 以 Claude Code 插件形态接入，让 Claude 会话把代码评审、难题调查、长任务委派给 Codex（GPT-5.4 系），结果原样带回。README 开篇即此定位（`README.md:1`），交付物是八个斜杠命令（`README.md:10`）。

分发三层：marketplace 清单 `.claude-plugin/marketplace.json:2` 声明 `openai-codex`，`:18` 把唯一插件 codex 指向 `./plugins/codex`；用户侧 `/plugin marketplace add openai/codex-plugin-cc`（`README.md:27`）三步装好。插件清单 `plugins/codex/.claude-plugin/plugin.json:2` 只有 name/version/description，但 `plugins/codex/scripts/lib/app-server.mjs:19` 运行时读它，把版本填进发给 app-server 的 clientInfo。npm 包 `package.json:2` 零运行时依赖（`package.json:19`）。版本号五处冗余，由 `scripts/bump-version.mjs:6-67` TARGETS 表统一维护。

## 2. skills 地图

`plugins/codex/skills/` 三个技能全部 `user-invocable: false`——不是给用户敲的，是 codex-rescue 子代理运行时加载的内部契约：

- **codex-cli-runtime**：钉死"恰好一次 task 调用"的转发规则——剥 --background/--wait、--resume→--resume-last、spark→gpt-5.3-codex-spark（`skills/codex-cli-runtime/SKILL.md:23`）、默认 --write。
- **gpt-5-4-prompting**：GPT-5.4 提示词工程指南，"像操作员而非协作者下指令"（`skills/gpt-5-4-prompting/SKILL.md:11`）。
- **codex-result-handling**：结果呈现纪律——保 verdict/findings/next_steps 结构与严重度排序；`skills/codex-result-handling/SKILL.md:19` 的 CRITICAL 条款禁止评审后自动修代码。

references 弹药库：`references/prompt-blocks.md` 是 21 节 XML 块字典（task 块 `prompt-blocks.md:8`、verification_loop `:68`）；`references/codex-prompt-recipes.md` 五套配方（Diagnosis `:7`）；`references/codex-prompt-antipatterns.md` 七类反模式（`:5`、`:56`）。子代理定义在 `plugins/codex/agents/codex-rescue.md:4`：model sonnet、tools 仅 Bash。

## 3. gpt-5-4-prompting 提示词指南解剖

这套指南示范"提示词即 API 契约"。核心主张（`skills/gpt-5-4-prompting/SKILL.md:14-17`）：一次运行一个明确任务；显式说清"完成长什么样"；优先收紧契约而非提高推理档位（`SKILL.md:41`）；XML 标签稳定可解析。块选择矩阵按任务路由（`SKILL.md:27-31`）：编码加 completeness_contract+verification_loop，评审加 grounding_rules+structured_output_contract，研究加 research_mode+citation_rules，可写任务加 action_safety。反模式从失败侧补刀：`references/codex-prompt-antipatterns.md:56` 把 "Think harder" 重写成 verification_loop，`:72` 要求评审/修复/文档拆三次运行；Prompt-Patching 配方（`references/codex-prompt-recipes.md:127`）教续线程只发增量指令。

## 4. hooks 与 commands 机制

**hooks**（`plugins/codex/hooks/hooks.json`）三事件：SessionStart/SessionEnd 挂 `session-lifecycle-hook.mjs`（timeout 5s，`hooks.json:4`），Stop 挂 `stop-review-gate-hook.mjs`（timeout 900s，`hooks.json:32`）。SessionStart（`session-lifecycle-hook.mjs:77`）把 session_id/transcript_path/CLAUDE_PLUGIN_DATA 经 shellEscape（`:31`）写入 CLAUDE_ENV_FILE——后续命令靠它们归属会话、定位状态目录。SessionEnd（`:83`）全量回收：关 broker → cleanupSessionJobs（`:42`）杀本会话后台任务 → teardown 清残留。Stop hook 是停机评审门：config.stopReviewGate 开启才执行（`stop-review-gate-hook.mjs:154`），spawnSync 调 companion task --json（`:105`），按首行 ALLOW:/BLOCK:（`:80`）决定放行或 block；Codex 缺失降级提示不阻断（`:59`）。

**commands** 两形态：cancel/result/status/transfer 是 bang 单行直执行（`commands/cancel.md:8`）；review/adversarial-review/rescue/setup 是完整 prompt 规格。frontmatter 三件套：argument-hint、allowed-tools（`commands/review.md:5`）、disable-model-invocation 防模型自调（rescue 例外）。`commands/review.md:38` 澄清边界：真正的 Claude 侧后台化靠 `Bash(run_in_background: true)`。

## 5. 核心链路：cc 会话如何调起 codex

1. Claude 按 `commands/review.md` 规格估体量、AskUserQuestion 选模式，Bash 调 `scripts/codex-companion.mjs review "$ARGUMENTS"`。
2. main 分发（`codex-companion.mjs:1024`）→ handleReviewCommand（`:712`）解析参数（args.mjs 整串切词 `args.mjs:76`）→ resolveReviewTarget 选目标。
3. executeReviewRun（`:358`）分叉：原生路 runAppServerReview；对抗路 collectReviewContext（`git.mjs:300`，超预算降级 self-collect）→ 插值 `prompts/adversarial-review.md`（契约块 `:48`）→ runAppServerTurn 带 outputSchema。
4. runAppServerTurn（`codex.mjs:1095`）→ withAppServer（`:613`，broker 忙自动降级直连）→ 工厂 connect（`app-server.mjs:335`）。
5. 传输二选一：直接 spawn `codex app-server`（`app-server.mjs:190`）或连共享 broker——`app-server-broker.mjs` 单 owner 串行化多会话访问，忙时回 -32001（`:179`）；broker 由 ensureBrokerSession 幂等管理（`broker-lifecycle.mjs:113`）。
6. captureTurn（`codex.mjs:559`）用 TurnCaptureState 状态机吃通知流；完成推断最难——final_answer 后等子代理排空，250ms 定时器兜底（`codex.mjs:373`）。
7. render.mjs 渲染（severity 排序 `render.mjs:251`）→ verbatim 呈现。后台变体：enqueueBackgroundTask（`codex-companion.mjs:684`）spawn detached task-worker，matchJobReference（`job-control.mjs:191`）支持前缀引用。

## 6. 设计决策

- **共享 broker + 忙时拒绝**：多会话复用一个 codex 进程，-32001 由 withAppServer 降级直连兜底（`codex.mjs:613`）。
- **默认关流式 delta**：`app-server.mjs:36` optOutNotificationMethods 排除四类 delta——要结果不要打字机。
- **git 上下文预算制**：内联 diff 限 2 文件/256KB、untracked 单文件 24KB（`git.mjs:7-9`），超限改让 Codex 自己跑只读 git——上下文成本从 token 转给工具调用。
- **git 调用一律 shell:false**（`git.mjs:13`），仓库派生参数绝不过 shell。
- **评审只读、结果 verbatim**：`skills/codex-result-handling/SKILL.md:19` CRITICAL 钉死"评审后停下问用户"；rescue 默认 --write 是唯一例外。
- **文档即规格**：`tests/commands.test.mjs:15` 对命令 markdown 逐条正则断言，改坏措辞 CI 红。
- **零依赖**：全 Node 标准库；tsconfig 只覆盖五个核心文件。

## 7. 扩展点

- **新斜杠命令**：commands/ 加 md + companion 加 handleXxx 与 main switch case（`codex-companion.mjs:1031`）+ tests/commands.test.mjs 加断言。
- **新 prompt 模板**：放 prompts/，loadPromptTemplate 按名加载（`prompts.mjs:4`），{{VAR}} 插值。
- **新技能**：skills/<name>/SKILL.md 设 user-invocable:false，可挂 agents/codex-rescue.md 的 skills 列表。
- **协议方法**：`app-server-protocol.d.ts:59` AppServerMethodMap 加映射；底层类型由 prebuild `codex app-server generate-ts` 再生成（`package.json:14`），.generated/ 不入库。
- **配置开关**：state.mjs config 键加新开关，hooks/commands 读它分流。

## 8. 新人上手

阅读顺序：README（Install `README.md:22`、Typical Flows `:239`）→ `commands/review.md` 看规格写法 → `codex-companion.mjs:75` printUsage 总览十个子命令 → `lib/codex.mjs:10-36` TurnCaptureState typedef（全仓最核心数据结构）→ `tests/fake-codex-fixture.mjs:7` 看 644 行假 codex 如何撑起端到端测试。

跑测试 `npm ci && npm test`（`package.json:17`）；CI 另装真 Codex（`.github/workflows/pull-request-ci.yml:29`）。调试：状态目录在 CLAUDE_PLUGIN_DATA/state/<slug>-<hash>（`state.mjs:29`），jobs/<id>.json 与 .log 是后台任务第一现场。三个易混点：companion `--background` 只入队 detached worker（Claude 侧后台化是 Bash run_in_background）；原生 review 不带 focus text（要 focus 走 adversarial-review）；spark 是别名不是模型名（`codex-companion.mjs:72`）。
