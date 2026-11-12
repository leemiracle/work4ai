# 06 · hooks 会话引导链、测试体系与四平台变体

## 角色定位

本篇覆盖技能库的"基础设施三件套"：hooks 引导链是技能在真实会话里的激活通道——没有它，技能只是躺在磁盘上的死文档；测试体系验证"技能被触发/被遵循"这一行为本身；四平台变体把同一份内容辐射到异构宿主。CLAUDE.md:67 起的 New Harness Support 一节说透了三者的关系：真集成=会话开始就加载 using-superpowers bootstrap，手动拷贝技能文件、npx 包装、按会话 opt-in 都不算——验收测试是干净会话发 "Let's make a react todo list" 必须自动触发 brainstorming（CLAUDE.md:75），并要求 PR 附完整会话转录。

## 内部结构

**hooks 引导链（4 文件）**：`hooks/hooks.json:3-11` 声明 SessionStart——matcher `startup|clear|compact` 覆盖启动/清屏/压缩三时机、`async:false` 同步，命令调用 run-hook.cmd（路径加引号因 Windows 目录可能含空格，docs/windows/polyglot-hooks.md:81）。`hooks/run-hook.cmd` 是 polyglot 双态启动器：首行 `: << 'CMDBLOCK'` 是机关——bash 把 `:` 当 no-op、整段批处理吞进 heredoc 直到 L40 结束符，从 L42 起执行 `exec bash <script>`（run-hook.cmd:42-46）；cmd.exe 把 `:` 当标签忽略、正常跑批处理段——按 Git Bash 标准路径（L21-24）、x86 路径（L25-28）、PATH（L30-35）三级查找，找不到就静默 exit 0"插件仍可用，只是没有 SessionStart 注入"（L37-39）。钩子刻意无扩展名：Windows 下 Claude Code 会对含 .sh 的命令自动前缀 bash 造成干扰（L7-9 注释），故 `.gitattributes:3` 对 hooks/session-start 按完整路径强制 LF，`*.cmd` 保持 LF 是它被两种 shell 同时解析的前提（.gitattributes:5-6）。`hooks/session-start`：探测遗留目录则生成迁移警告（session-start:10-15）；读母技能全文（L18）；`escape_for_json` 参数替换逐段转义——注释明言比逐字符循环快数量级（L20-31）；拼 `<EXTREMELY_IMPORTANT>` 上下文（L35）；**按平台三选一输出**——Cursor 输出 snake_case `additional_context`、Claude Code 输出嵌套 `hookSpecificOutput.additionalContext`、Copilot/未知平台输出顶层 `additionalContext`（L46-55），只发一个字段因 Claude Code 双读不去重（L41-42）；printf 替代 heredoc 绕开 bash 5.3+ 挂起（L44-45，issue #571）。`hooks/hooks-cursor.json:4-7` 是 Cursor 扁平 camelCase 变体。

**测试体系（tests/ 七目录）**：docs/testing.md:7 定调——复杂技能必须跑真实无头会话并核验转录。三层：①无头中枢 tests/claude-code/——run-skill-tests.sh:74-83 硬编码清单：fast 仅 SDD 单测，integration=SDD 集成+requesting-code-review（10-30 分钟级，L56）；test-document-review-system.sh 与 test-worktree-native-preference.sh **不在默认清单**，需 `--test` 指定。test-helpers.sh 被五个脚本 source：`run_claude`（L6-29）封装 `claude -p`、四类断言（L33-123）、计划夹具（L127-192）；analyze-token-usage.py 按 agent 分解 input/output/cache/成本（L12-30）。②行为实验室——skill-triggering/（隐式）与 explicit-skill-requests/（显式）两族，统一判据 grep stream-json 转录 `"skill":"([^"]:)?<技能名>"`（run-test.sh:61，可选命名空间前缀兼容带/不带 superpowers:）；explicit 侧额外检测"过早行动"——首条 Skill 调用前的非规划类 tool_use（过滤 TodoWrite，run-test.sh:103-121）；变体四脚本：multiturn 拉长对话历史复现"聊久了不调技能"（run-multiturn-test.sh:5-6）、claude-describes-sdd 复现原始失败、haiku 用便宜模型+用户真实 CLAUDE.md 加压（run-haiku-test.sh:2-3——"便宜模型更容易失败"被当作要暴露的维度）。③端到端与平台——subagent-driven-dev/ 双栈夹具（go-fractals 10 任务/svelte-todo 12 任务，scaffold.sh:14-40 建仓+预置权限）；opencode/ 的 setup.sh:9-36 建 mktemp 隔离 HOME 并按 OpenCode 真实读取路径装 skills+插件符号链接；test-priority.sh:3-5 自我声明"记录现状、不加插件 workaround——保持集成套件诚实"；test-bootstrap-caching.sh:13-29 双语种验引导缓存；codex-plugin-sync/ 的 615 行测试用 write_fake_gh 假 gh 拦截真实 GitHub 调用。

**四平台变体**：`.codex-plugin/plugin.json` 最丰富——interface 展示块含 displayName/category Coding/capabilities/defaultPrompt/品牌色 #F59E0B（.codex-plugin/plugin.json:24-46）；`.cursor-plugin/plugin.json:21-24` 唯一把 hooks 挂接写进清单；`gemini-extension.json`+GEMINI.md 组成 Gemini 入口——GEMINI.md 仅两行 @ 引用（GEMINI.md:1-2）靠 contextFile 机制在会话头展开。`.opencode/plugins/superpowers.js`（135 行）是最深适配：`config` 钩子把 skills 目录塞进 OpenCode 配置免符号链接（Config.get() 缓存单例使惰性发现可见，superpowers.js:100-109）；`experimental.chat.messages.transform` 把 bootstrap 并入首条用户消息而非系统消息——系统消息每轮重复致 token 膨胀（#750）、多系统消息破坏 Qwen（#894）（L111-119）；钩子每 agent step 重放（OpenCode 每步从 DB 重载消息），故用模块级 `_bootstrapCache` 双态缓存（undefined=未加载/null=缺失，L49-53，issue #1202），重复注入靠检测首条消息已含 EXTREMELY_IMPORTANT 拦截（L126-129）。

## 外部连接

引导链上游是插件系统（SessionStart 事件由宿主触发），下游直接决定母技能的注入面。平台变体共享同一 skills/ 内容源：版本号六清单原子同步（.version-bump.json:2-9，bump-version.sh 统一升降）；`scripts/sync-to-codex-plugin.sh:39-44` 的 EXCLUDES 全部锚定根（`/.claude/`、`/.opencode/` 等）——注释明言不锚定的 `scripts/` 会误伤 skills/brainstorming/scripts/ 嵌套目录；fork（prime-radiant-inc/openai-codex-plugins）每轮全新克隆+rsync+开 PR，`--deterministic` 同一上游 SHA 两跑产 identical diff（脚本自验哲学，L12-13）。测试体系向上验证全部 16 技能，向下依赖 `claude -p`/`--plugin-dir`/`--output-format stream-json` CLI 面。

## 数据流

一次冷启动的注入流：宿主触发 SessionStart → hooks.json 路由到 run-hook.cmd → Windows 走批处理段找 Git Bash 执行 session-start；Unix 直接 exec bash → session-start 读母技能、转义、按平台拼对应 JSON 字段 → 宿主把 additionalContext 注入会话上下文 → 代理看到"哪怕 1% 可能性也要调技能"并开始宣告式使用技能。行为实验室的验证流：prompt 夹具 → `claude -p --plugin-dir <仓> --dangerously-skip-permissions --max-turns 3 --output-format stream-json`（run-test.sh:48-53）→ 转录落盘 → SKILL_PATTERN 判定触发 → 过早行动扫描 → 额外打印"本次实际触发的全部技能"帮助归因（run-test.sh:70-73）。一个已知测量细节：executing-plans.txt 夹具 122 字节无尾换行，scanner 曾误记 sizeLines=0——文件实有内容，按源码事实修正。

## 设计决策

- **polyglot 而非双文件**：一份 run-hook.cmd 同时服务 cmd/bash，代价是每行都要兼顾两种语法；备选方案（.sh+.cmd 两份入口+宿主选择）被弃，因为 Claude Code 的 Windows .sh 自动前缀行为不可控。
- **Windows 路径的教训**：docs/windows/polyglot-hooks.md 记录的坑——`${CLAUDE_PLUGIN_ROOT}` 在 Windows 展开成反斜杠结尾路径再拼 `/hooks/...` 会得到混合分隔符，需 cygpath 转换（polyglot-hooks.md:196）；hooks.json 命令整体加引号防空格路径（L81）。
- **"技能触发"本身是被测行为**：这是本仓测试体系最有原创性的维度——不是测代码而是测代理行为；隐式组（自然语言不点名）与显式组（点名+边界表述）构成对照组，multiturn/haiku 是加压轴。
- **诚实测试哲学**：test-priority.sh 宁可记录现状也不加 workaround（tests/opencode/test-priority.sh:3-5）；文档列出的测试不在默认清单这件事本身也写进文档——测试基础设施不粉饰自身。
- **一源多宿主的成本观**：技能写一次、五平台运行靠三份工具映射表（codex/copilot/gemini-tools.md，如 Task→spawn_agent/wait_agent 需 config.toml 开 features.multi_agent，codex-tools.md:25）；Gemini 用两行 @ 引用获得零代码适配，OpenCode 则需要 135 行插件——宿主机制决定适配深度。

## 勘误与新人提示

勘误：(1) tests/brainstorm-server/windows-lifecycle.test.sh:23 `SERVER_JS` 指向 server.js，磁盘实为 server.cjs（v5.0.5 ESM 重命名未同步），Windows 三测将模块缺失；(2) hooks-cursor.json 曾带 UTF-8 BOM 导致 Cursor 解析失败，已修复（RELEASE-NOTES 记载）——改造该文件时确认无 BOM；(3) docs/windows/polyglot-hooks.md:57-58 的目录树示例写 session-start.cmd/session-start.sh 双文件布局，实际仓库是 run-hook.cmd+无扩展名 session-start 单脚本模式（run-hook.cmd:7-9 的注释解释了为何放弃 .sh）——文档示例与实现有代差。

新人提示：跑 tests/claude-code 前须本地装好 superpowers-dev marketplace（docs/testing.md:38）；调试 hook 时先手跑 `bash hooks/session-start` 看三个分支各输出什么；给新 harness 提 PR 前自测验收测试并保存完整转录；改 hooks-cursor.json 记得以 `git diff` 确认没引入 BOM。
