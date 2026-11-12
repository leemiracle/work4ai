# 06 · ui/src/cli.tsx — Ink/React 终端前端与 Python 引擎拉起链

> 源文件：`ui/src/cli.tsx`（600 行）。行号锚均从源码核实（commit fd4b72e7）。

## 1. 角色定位

cli.tsx 是 TUI（终端用户界面）前端的全部：入口、进程管理、输入法、渲染器一炉烩。它用 **Ink**（把 React 渲染到终端的库）画出一个"ViMax Workspace"面板——渐变边框、会话头、对话行、忙碌动画、斜杠命令弹窗、带块状光标的输入框；同时它自己就是**进程管理者**：`vimax tui` 命令经 bash 分发器 exec `tsx ui/src/cli.tsx`（vimax:102），本文件再 spawn Python 引擎 `main_agent.py --jsonl --stdin-repl`（cli.tsx:110,:250）并归约其 stdout JSONL 为界面行。ONBOARDING 的架构叙事"一个引擎、两个壳"里，它是壳之一（另一个是 web/），且与 Web 壳共享同一个无头 CLI 与同一套事件协议——视图层完全不掺业务。

本文件 600 行里大约只有 150 行与"逻辑"有关（spawn、行缓冲、事件归约、busy 状态机），其余是终端绘制的苦活：等宽折行、光标建模、resize 处理、渐变边框。这个比例本身就是教训：自绘 TUI 的成本大头永远在绘制层。

## 2. 内部结构

**模块级启动序列（:14-25, :593-600）**：ESM 下手工算 `__dirname`（:14-15，`fileURLToPath` → `path.resolve('..','..')` 得仓根）；:25 在 import 时就同步解析 CLI 参数（`--new-session` / `--session <id>` / `--help`，:27-48，未知参数直接抛错 :45——白名单式解析）；:599-600 先清屏再 `render(<App />)`。清屏可经 `VIMAX_TUI_NO_CLEAR=1` 跳过（:594），供测试/嵌入场景复用输出。

**`agentCommand()`（:113-128）——spawn 回退链**，五级：
1. `VIMAX_AGENT_COMMAND`（自定义命令 + `VIMAX_AGENT_ARGS` 空格切分，:114-116）——测试替身注入口；
2. `VIMAX_PYTHON_CMD`（:117-119）；
3. `VIMAX_UV_CMD` → `uv run python`（:120-122）；
4. 仓内 `.venv/bin/python3`（存在即用，:123-126）；
5. 裸 `uv run python` 兜底（:127）。
参数固定为 `main_agent.py --jsonl --stdin-repl` + 会话参数（:109-111）。**注意与 web/server.mjs 的链不同序**：Web 侧在 `.venv` 之前多试一个 `~/.local/bin/uv`（server.mjs:251-252），TUI 侧 `VIMAX_UV_CMD` 后直奔 `.venv`——同一台机器两个壳可能拉起不同解释器，排障时先对链。

**`App` 组件的状态面（:139-156）**：`lines`（WorkspaceLine[]，界面行）、`input`/`cursor`（含 ref 镜像 :142-143——useInput 回调里必须读 ref 避免 stale closure）、`busy`（一轮进行中，锁输入 :191）、`activityText`（状态栏文案）、`workspaceMeta`（路径/会话/压缩进度，:146-152）、`stateRef`（lineMapping 的归约状态）、`childRef`（子进程）、`bufferRef`（行缓冲）、`responseIdleTimerRef`（token 流式结束的 1.5s 判定，:329-335）。

**`useInput` 键盘处理（:185-246）——手工输入法**：Ctrl-C 杀子进程退出（:186-189）；busy 时吞键（:191）；左右/Home/End 移动光标（:194-209）；**粘贴含换行的文本只取第一行提交**（:210-216，`value.split(/[\r\n]/, 1)`）——多行粘贴防误发；退格/删除键的判定除了 ink 的 key 标志还比对原始转义序列（``、`[3~` 等，:221-222），Delete 在行尾退化为退格（:235-238）；普通可见字符按码点插入（:241-245）。所有编辑都过 `updateInput`（:176-183），其中 `Array.from` 保证按 **Unicode 码点**而非 UTF-16 码元计算光标——中文与 emoji 不会把光标弄丢。

**spawn 副作用（:248-289）**：与 Web 桥同款的**手写行缓冲器**（:254-260：累积 chunk → split('\n') → pop 回填残行）；stderr 逐行以 `[stderr]:` 前缀入界面（:263-269）；exit 非 0 报 error、被信号杀报 status（:275-283）；卸载时杀子进程（:285-288）。

**`consumeJsonLine`（:300-321）——JSONL→行**：解析失败整行作为 error 行展示（:307，不丢信息）；先更新 workspaceMeta 与 activityText，再 `applyStreamEvent(stripThinking(current), state, event)`（:316-320）——真正的归约逻辑在姊妹模块 `lineMapping.ts` 的纯函数里（token 拼接、tool_start/progress/result 行、done 收束），本文件只管状态壳。`done/error/session` 三类事件解除 busy（:312-315）。

**`updateActivity`（:337-373）——状态栏文案状态机**：tool_start/progress → "tool X: stage"；tool_result → 回到"ViMax thinking"；token → "ViMax responding" **并启动 1.5s 空闲计时器**（:354-357, :329-335）——LLM 流式输出无显式结束信号时，靠"1.5 秒没新 token"判定回复完。

**`updateWorkspaceMeta`（:375-399）**：prompt_trace 事件更新压缩用量（:376-388），且有**节流**——百分比没变且增量 <100 token 就不重渲染（:383）；session 事件更新会话路径/ID/阶段（:389-398）。头部三行由此而来：Path / Session·Stage / compactionLabel（:493-508）。

**渲染层（:418-558）**：布局 = WorkspacePanel + 斜杠弹窗（输入以 `/` 开头且不 busy 时显示，最多 6 条，:449-467）+ 输入框；`InputText`（:431-447）用反色块模拟光标，busy 时置灰锁显；`WorkspacePanel`（:469-491）画渐变上下边框（`GradientBorderLine` :532-543，逐字符上色）+ 头部 + 逐行内容 + busy 动画行（`useThinkingFrame` :68-79，220ms 轮播 `.''..'...'`）；`wrapText`（:560-580）用 `string-width` 按显示宽度折行（中文占 2 列的正确处理）；`lineColor`（:582-591）按行类型着色（user 黄/assistant 白/tool 品红/error 红/terminal 青）。

**`useTerminalWidth`（:81-106）——resize 的血泪处理**：resize 事件 60ms 防抖后**先发全屏清屏转义序列再强制重渲**（:90-96）——注释（:88-89）直言 Ink 在快速 resize 时不清除旧帧细胞，不清屏会留残影。宽度下限 20 列（:82）。

## 3. 外部连接

**依赖上游**：react + ink（:1-2）+ string-width（:3）——ui 工作区仅有的运行时依赖；node 内建 child_process/fs/path/url/process（:4-8）；本地三模块：`lineMapping.js`（:9，事件→行的纯归约，带 lineMapping.test.ts 单测）、`slashCommands.js`（:10，命令匹配，亦有单测）、`workspaceMeta.js`（:11，路径解析与压缩条文案，带单测）+ `types.js`（:12）。**三个姊妹模块全部有测试而 cli.tsx 本体没有**——逻辑被刻意挤进可测的纯函数，壳保持薄。

**被依赖/下游**：唯一上游是 `vimax` bash 分发器的 tui 分支（vimax:102 `exec tsx ui/src/cli.tsx`，tsx 由 ui/node_modules 提供，缺失时 :98-101 报错提示 npm install）；它 spawn 的 `main_agent.py`（--jsonl --stdin-repl，main_agent.py:24,26）是全部下游。与 web/server.mjs 是**平行关系**：同一引擎的两个壳，事件 schema（StreamEvent 类型）与归约思路（lineMapping.ts ↔ web/src/events.ts）互为镜像。

## 4. 数据流：`vimax tui` 的一次完整交互

1. 用户敲 `vimax tui resume abc123` → bash 分发器（vimax:95-103）把 `resume` 翻译成参数传给 tsx exec 本文件 → :25 解析出 `--session abc123`（:35-41）。
2. 模块加载即清屏（:599），render App → spawn 副作用（:248）按回退链找到解释器（如 `.venv/bin/python3`），拉起 `main_agent.py --jsonl --stdin-repl --session abc123`。
3. Python 侧激活会话后吐出 session 事件 → 行缓冲器拼出完整行 → consumeJsonLine → updateWorkspaceMeta 刷新头部（Session: abc123 · Created）→ applyStreamEvent 无界面行产出（turn/status 事件被归约层显式忽略，lineMapping.ts:12-14）。
4. 用户输入"做个赛博朋克短片"回车 → submit（:401-416）：busy 锁输入、用户行入列、**归约状态重置**（:412）、`child.stdin.write(prompt + '\n')`（:415）。
5. 引擎循环开转：status(sampling_assistant) → 状态栏"ViMax thinking"+动画帧；tool_start(vimax_narrative_planning) → "tool vimax_narrative_planning running" 品红行；随后分钟级 tool_progress 流水逐条成行；token 事件拼接 assistant 文本；done → busy 解除（:312-315）。
6. 期间用户 resize 终端 → 防抖清屏重渲，面板按新宽度重折所有行。
7. Ctrl-C → 杀子进程 → exit（:186-189）。

## 5. 设计决策

- **React/Ink 而非 ncurses/裸 ANSI**：声明式 UI 让"行列表 + 光标 + 弹窗"的状态组合免于手写差分刷新；代价是 Ink 的终端兼容性坑（resize 残影要自己清屏补，:88-96）与约 600 行里大半是绘制代码。
- **输入法全手写**：ink 的 useInput 只给原始键值，Backspace/Delete/Home/End 的跨终端差异要自己比对转义序列（:221-222）；`Array.from` 码点光标是对"终端按显示列、字符串按码元"这层错配的防御。
- **粘贴取首行即发**（:210-216）：终端粘贴多行文本时 ink 会把每行当一次回车——TUI 常见的"粘贴炸弹"问题，这里选择最简单的策略（首行提交、其余丢弃），配合提示词里"用文件上传长文本"的产品约定。
- **1.5s token 空闲判定**（:329-335）：协议里 token 流没有 EOS 事件，与其改协议不如前端定时——但意味着 busy 状态最多晚 1.5s 解除（done 事件到达则立即，:312-315 双保险）。
- **归约逻辑外置纯函数 + 本体零测试**：lineMapping/slashCommands/workspaceMeta 三个模块各有 .test.ts，cli.tsx 的壳逻辑（spawn/键盘）靠 e2e 手测——测试预算花在刀刃上的典型取舍。
- **引擎选择链与环境变量注入口**：`VIMAX_AGENT_COMMAND` 让 `web/test/fake-agent.mjs` 式替身可复用于 TUI；五级回退保证"clone 完没配环境也能跑"（.venv → uv 自动装）。
- **prompt_trace 节流**（:383）：压缩进度条每轮采样才更新一次，百分比不变就不触发 React 重渲——终端全量重绘的成本意识。

## 6. 新人提示

- **改事件处理先看 lineMapping.ts**：cli.tsx 的 consumeJsonLine 只做壳，"某事件显示成什么行"全在姊妹模块；新增事件类型要同时改 types.ts（StreamEvent 联合类型）与 lineMapping（以及 web/src/events.ts，双壳同步）。
- busy 锁是**单向门**（:191 busy 时 useInput 直接 return）：任何"busy 期间允许 Ctrl-C 之外的键"的需求都要在那个 return 之前插分支。
- spawn 副作用的依赖数组是空 `[]`（:289）且内部用了 setState——React 18 StrictMode 双挂载会 spawn 两个 Python 进程；本文件没开 StrictMode，**别顺手加**，加了要先把 spawn 改成幂等。
- 行缓冲器（:254-260）与 web/server.mjs:158-167 是同构代码但**各自维护**：改 JSONL 分帧逻辑（如引入 \r\n 兼容）记得两处同步。
- `agentCommand` 链与 web 侧不同序（本文件 :123-126 先 .venv；server.mjs:251-252 先 ~/.local/bin/uv）：用户报"Web 好的 TUI 报错"时先 `VIMAX_PYTHON_CMD` 钉死解释器排除变量。
- workspaceMeta 的 compactionTarget 来自 `compactTargetFromEnv`（:151，读 VIMAX_CONTEXT_WINDOW_TOKENS 等环境变量，见 01 篇压缩阈值）——头部的百分比条与 Python 侧压缩行为共享同一组环境变量约定，改名要三端（cli.tsx / workspaceMeta.ts / context_compactor.py）一起改。
- 渐变边框 `GradientBorderLine` 对每列一个 `<Text>`（:537-539）——面板 120 列就是 120 个 React 元素/行，纯装饰的渲染成本大户；若要做性能优化这是第一刀，但对单屏 TUI 无所谓。
- `displayStage`（:518-530）硬编码了会话阶段→人话的映射表：session_index 新增阶段（如 novel_scene_rendered 已在表外，走 :529 的下划线替换兜底）记得补表，否则用户看到生肉枚举名。
