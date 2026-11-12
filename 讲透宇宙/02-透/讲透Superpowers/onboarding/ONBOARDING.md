# obra/superpowers 讲透 Onboarding

> 图谱基线：195 节点 / 297 边 / 16 层 / 16 步 tour，commit `f2cbfbef`，v5.1.0（2026-04-30）。本仓是"Claude Code 进程技能库"品类的定义者。

## 1. 库定位与安装

superpowers 自我定位为"给编码代理的完整软件开发方法论"（README.md:3）：一组可组合技能+让代理在正确时刻自动用它们的引导机制，覆盖八个宿主（README.md:7）。技能文本被定性为"塑造代理行为的代码"（CLAUDE.md:90），改动须走 writing-skills+压测+eval。

安装以插件分发：官方市场收录 `superpowers`（README.md:37），主清单 `.claude-plugin/plugin.json:2-4` 声明 v5.1.0，本地开发走 `.claude-plugin/marketplace.json:2` 的 `superpowers-dev`。发布纪律由 `.version-bump.json:2-9` 钉死——六清单版本原子同步，`scripts/bump-version.sh:26-32` 点路径转 jq 路径读写。

治理以反 AI-slop 闻名：CLAUDE.md:3 专设 "If You Are an AI Agent" 节，CLAUDE.md:7 披露 **94% PR 拒绝率**；验收测试=干净会话发 `Let's make a react todo list` 须自动触发 brainstorming（CLAUDE.md:75）。AGENTS.md 是 CLAUDE.md 的符号链接（RELEASE-NOTES.md:24）。

## 2. 技能地图：按进程分组

16 个技能按交付进程分五组：

- **引导**：`using-superpowers`（117 行母技能）——"哪怕 1% 可能性适用也必须调用技能"（skills/using-superpowers/SKILL.md:11），含子代理跳过标记（SKILL.md:6）与合理化对照表（SKILL.md:82-95）。
- **构思与计划**：brainstorming（HARD-GATE 禁止设计获批前写码，skills/brainstorming/SKILL.md:12）→ writing-plans（假设执行工程师零上下文，skills/writing-plans/SKILL.md:10）→ using-git-worktrees / executing-plans / finishing-a-development-branch。
- **质量纪律**：test-driven-development（铁律 `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST`，skills/test-driven-development/SKILL.md:34）+ testing-anti-patterns.md Iron Laws（skills/test-driven-development/testing-anti-patterns.md:13-19）。
- **诊断**：systematic-debugging（"无根因调查禁提修复"，skills/systematic-debugging/SKILL.md:19），配 root-cause-tracing / defense-in-depth / condition-based-waiting 与 find-polluter.sh。
- **执行与评审**：subagent-driven-development（两阶段评审铁三角）、requesting/receiving-code-review、verification-before-completion、dispatching-parallel-agents。

元层 `writing-skills`（655 行）把 RED-GREEN-REFACTOR 移植到技能创作（skills/writing-skills/SKILL.md:10），配套 testing-skills-with-subagents.md 压测方法论与 persuasion-principles.md（N=28,000 实证：合规率 33%→72%，skills/writing-skills/persuasion-principles.md:7）。

## 3. hooks 会话引导链

激活机关在 hooks/ 四文件。`hooks/hooks.json:3-11` 声明 SessionStart（matcher `startup|clear|compact`、`async:false`）调 `run-hook.cmd session-start`。`hooks/run-hook.cmd` 是 polyglot 双态启动器：L1 的 `: << 'CMDBLOCK'` 在 bash 眼里是 no-op+heredoc 吞掉整段批处理，在 cmd.exe 眼里 `:` 是标签、批处理正常执行（run-hook.cmd:37-43，另见 docs/windows/polyglot-hooks.md:33-50）；批处理段按标准路径找 Git Bash 再 fallback PATH（run-hook.cmd:21-35），找不到则静默退出（run-hook.cmd:37-39）。钩子刻意无扩展名规避 Windows 对 .sh 自动前缀 bash（run-hook.cmd:7-9）；`.gitattributes:3` 因此按完整路径强制 LF。

`hooks/session-start` 拼载荷：读母技能全文（session-start:18），`escape_for_json` 参数替换式转义（比逐字符循环快数量级，session-start:20-31），拼 `<EXTREMELY_IMPORTANT>` 上下文（session-start:35），按平台三选一输出 JSON——Cursor 用 `additional_context`、Claude Code 用嵌套 `hookSpecificOutput.additionalContext`、Copilot 用顶层 `additionalContext`（session-start:46-55），只发一字段因 Claude Code 双读不去重（session-start:41-42）；printf 替代 heredoc 规避 bash 5.3+ 挂起（session-start:44）。`hooks/hooks-cursor.json:4-7` 是 Cursor camelCase 变体。

## 4. 核心链路：一次真实使用旅程

用户说"帮我做个 todo 应用"：

1. **冷启动**：SessionStart hook 注入母技能全文，代理获得技能发现纪律。
2. **brainstorm**：九步清单（探索上下文→按需提议可视化伴侣→一次一问→2-3 方案→分节呈现→写 spec→内联自检→用户审阅→调用 writing-plans，skills/brainstorming/SKILL.md:22-32）；伴侣 offer 独立成消息（SKILL.md:154）；spec 自检四查：占位符/一致性/范围/歧义（SKILL.md:116-124）；**唯一出口是 writing-plans**（SKILL.md:66）。
3. **plan**：每任务写明文件+完整代码+验证命令，一步一事（skills/writing-plans/SKILL.md:38-43）；禁 TBD/"类似 Task N"（SKILL.md:106-114）。
4. **隔离执行**：worktrees 三级优先级——检测已有隔离（GIT_DIR≠GIT_COMMON+子模块守卫，skills/using-git-worktrees/SKILL.md:20-33）→ 平台原生工具（SKILL.md:51-57）→ git 兜底（SKILL.md:59-110）。
5. **SDD/TDD/调试**：每任务派全新实现者子代理（控制器喂全文不让其读计划文件），两阶段评审强排序，四态汇报（skills/subagent-driven-development/SKILL.md:104-120）；遇 bug 走调试四阶段（skills/systematic-debugging/SKILL.md:46-213），3 次修复失败=架构问题（SKILL.md:199）。
6. **评审验证**：每任务后派 Senior Reviewer（skills/requesting-code-review/SKILL.md:14-17）；"无新鲜验证证据不得宣称完成"（skills/verification-before-completion/SKILL.md:19）。
7. **收尾**：环境检测→四选项（skills/finishing-a-development-branch/SKILL.md:68-79）→按出处清理（SKILL.md:183-192）。

## 5. 关键设计决策

- **技能=被测代码**：全库核心哲学。先跑压力场景记录无技能基线（RED）、写最小技能文本（GREEN）、发现新合理化就堵漏（REFACTOR）（skills/writing-skills/SKILL.md:533-560）；铁律 `NO SKILL WITHOUT A FAILING TEST FIRST` 对新写与编辑同等生效（SKILL.md:374-392）。
- **CSO 搜索优化**：description 只写触发条件、绝不概述工作流——实测一总结流程 Claude 就走捷径不读正文（skills/writing-skills/SKILL.md:150-158）。
- **零依赖**：为省 714 个 node_modules 文件，brainstorm 服务器手写 RFC 6455（docs/superpowers/specs/2026-03-11-zero-dep-brainstorm-server-design.md:3）；依赖型 PR 拒收（CLAUDE.md:29）。
- **评审降噪**：v5.0.6 用内联自检替换子代理评审循环——回归测试（5 版本×5 试次）零增益却多耗 ~25 分钟（RELEASE-NOTES.md:100-107）。
- **防合理化**：红旗表+借口对照表+显式否定三重冗余；根基是说服七原则（skills/writing-skills/persuasion-principles.md:9）。

## 6. 测试体系：无头会话与行为实验室

docs/testing.md:7 定调：复杂技能必须以无头会话+转录验证。三层设施：

- **无头中枢** tests/claude-code/：`run-skill-tests.sh:74-83` 硬编码快速/集成清单（快速仅 SDD 单测；集成 10-30 分钟级，L56）；`test-helpers.sh:6-29` 的 `run_claude` 封装 `claude -p`、L33-123 四类断言；`analyze-token-usage.py:12-30` 按主会话/子代理分解 token（docs/testing.md:103-115）。
- **行为实验室**：tests/skill-triggering/ 测隐式触发——六份自然语言 prompt（如粘贴失败栈的 prompts/systematic-debugging.txt）不点名技能，run-test.sh:48-53 跑无头会话，L61-62 从 stream-json 转录判定 Skill 工具真被调用；tests/explicit-skill-requests/ 测显式边界——九份夹具覆盖裸名/please/时间压力（prompts/skip-formalities.txt），run-test.sh:103-121 还检测"过早行动"；run-haiku-test.sh:2-3 用便宜模型加压；test-worktree-native-preference.sh:1-14 三相结构（RED/GREEN/PRESSURE）50/50 全过。
- **端到端夹具** tests/subagent-driven-dev/：go-fractals（plan.md:3 首行即技能执行指令）与 svelte-todo 双栈，scaffold.sh:14-40 建仓+预置权限，让 Claude 走完派子代理全流程。另有 brainstorm 服务器白盒三件套（ws-protocol.test.js:19 直连 server.cjs、server.test.js:18 真实 spawn、windows-lifecycle.test.sh 验 MSYS2 PID）。

## 7. 四平台变体

一个内容源辐射四类宿主：`.codex-plugin/plugin.json:24-46` 最丰富（interface 展示块/品牌色）；`.cursor-plugin/plugin.json:21-24` 唯一把 hooks 挂接写进清单；`gemini-extension.json` + GEMINI.md（两行 @ 引用，GEMINI.md:1-2）组成 Gemini 入口。最重的适配是 `.opencode/plugins/superpowers.js`：`config` 钩子（L103-109）注入 skills 目录免符号链接；`experimental.chat.messages.transform`（L120-133）把引导并入首条用户消息——避开系统消息每轮膨胀（#750）与多系统消息破坏 Qwen（#894）；`_bootstrapCache` 双态缓存（L49-53）避免每 agent step 重复探测磁盘（issue #1202，tests/opencode/test-bootstrap-caching.sh:13-29 验证）。工具翻译靠 references/ 三份映射表（skills/using-superpowers/references/codex-tools.md:7,25）；`scripts/sync-to-codex-plugin.sh:39-58` 根锚定 EXCLUDES 镜像到 fork。

## 8. 新人上手

1. **先跑验收测试**：干净会话发 "Let's make a react todo list"，看 brainstorming 是否自动触发。
2. **读三个入口**：README.md → skills/using-superpowers/SKILL.md → hooks/session-start。
3. **沿核心链路各读一篇**：brainstorming → writing-plans → subagent-driven-development → test-driven-development。
4. **改技能前必读** writing-skills + testing-skills-with-subagents，并预览 CLAUDE.md 拒绝清单。
5. **勘误警示**（详见 explain 系列）：tests/brainstorm-server/windows-lifecycle.test.sh:23 引用 server.js 但磁盘是 server.cjs；systematic-debugging 压测文件仍写历史路径 skills/debugging/...（test-pressure-1.md:5 等）；skills/brainstorming/spec-document-reviewer-prompt.md 是死资产；RELEASE-NOTES 与 docs/plans/ 大量历史路径已漂移。

> 本篇 73 个行号锚全部现场核实于 commit f2cbfbef；素材另见图谱（onboard-input.json）与甄别笔记（NOTES-DIGEST.md）。
