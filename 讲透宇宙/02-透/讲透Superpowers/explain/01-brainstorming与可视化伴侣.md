# 01 · brainstorming 与可视化伴侣：从想法到 spec 的强制停留点

## 角色定位

brainstorming 是 superpowers 工作流的第一环：任何创造性工作（新功能、新组件、行为修改）动手之前，必须先探索用户意图、需求与设计。它是"行为塑形代码"哲学的极端样本——核心机关是一个 `<HARD-GATE>`：设计未获用户批准前，禁止调用任何实现技能、写任何代码、脚手架任何项目（skills/brainstorming/SKILL.md:12-14）。技能还专门内置反模式"这太简单不需要设计"：todo list、单函数工具、配置修改全部要走流程，"简单"项目恰是未审视假设造成最大浪费的地方（SKILL.md:16-18）。

它解决的问题很具体：编码代理的本能是收到需求立刻写代码。brainstorming 强迫代理先问"你到底想做什么"，把闲聊挤压成一份可实施的 spec，然后交接给 writing-plans——技能明文规定**唯一出口是调用 writing-plans**，不许转向 frontend-design 或任何实现技能（SKILL.md:66）。

可视化伴侣（visual companion）是 brainstorming 的可选伴侣子系统：一个本地浏览器页面，agent 把 mockup/线框/架构图推上去给用户看，用户点击选择、答案回传终端。它让"展示给我看"取代"描述给你听"，是仓内唯一的运行时服务。

## 内部结构

brainstorming 技能本体 164 行，骨架是九步清单（SKILL.md:22-32）：探索项目上下文 → 按需提议可视化伴侣（独立消息）→ 一次一问澄清 → 提 2-3 方案权衡 → 分节呈现设计 → 写 spec 到 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`（SKILL.md:29）→ spec 内联自检 → 用户审阅 spec 文件 → 调用 writing-plans。设计原则段强调"一次只问一个问题、优先多选题、YAGNI 无情"（SKILL.md:138-145）；scope 检查要求发现 spec 覆盖多个独立子系统时立即提出拆分，不要对需要分解的项目精雕细琢（SKILL.md:73-74）。

可视化伴侣的运行时由五个文件组成（skills/brainstorming/scripts/）：

- **server.cjs（354 行，零依赖核心）**：只用 Node 内置模块（crypto/http/fs/path，server.cjs:1-4）手写 RFC 6455 WebSocket。握手用 SHA1+magic GUID 算 Sec-WebSocket-Accept（server.cjs:11-13）；`encodeFrame` 处理 <126/16 位/64 位三种长度头（server.cjs:15-37）；`decodeFrame` 强制客户端帧必须掩码并做 XOR 解掩（server.cjs:39-72）。HTTP 层取内容目录最新 HTML 推送（按 mtime 排序，server.cjs:116-125），文件不是完整文档就自动包进 frame 模板（server.cjs:107-114）。
- **frame-template.html**：双主题 CSS 框架（OS 级明暗自适应），内置 options 选项卡/cards/mockup 容器/split 并排/pros-cons 组件类（visual-companion.md:158-236），内容经 `<!-- CONTENT -->` 占位注释注入。
- **helper.js**：被注入每个推送页面的 IIFE——建立 WebSocket、断线 1 秒重连、离线事件入队（helper.js:21-33），捕获 `[data-choice]` 点击回传终端（helper.js:36-45），维护单选/多选状态并更新指示条文案（helper.js:47-61），暴露 `window.brainstorm.send/choice` API（helper.js:82-85）。
- **start-server.sh / stop-server.sh**：生命周期管理（下文详述）。

## 外部连接

上游：hooks/session-start 注入的母技能让 brainstorming 在会话开头就处于"待触发"状态；CLAUDE.md 的验收测试（干净会话说 "Let's make a react todo list" 必须自动触发本技能，CLAUDE.md:75）就是以它为探针。下游：唯一出边指向 writing-plans（SKILL.md:135-136）。横向：spec 落盘路径 `docs/superpowers/specs/` 由 v5.0.0 目录重组确立（RELEASE-NOTES.md:287 起）；同目录的 spec-document-reviewer-prompt.md 曾是它的评审循环载荷，v5.0.6 后成为死资产（见 05 篇）。

测试连接：tests/brainstorm-server/ 三件套白盒验证——ws-protocol.test.js 直连 server.cjs 导出的四个协议函数（ws-protocol.test.js:7-11,19），server.test.js 真实 spawn 服务器并用 ws 包作测试客户端跑全链路（server.test.js:7-18，注意 ws 是仅测试依赖不随插件分发），windows-lifecycle.test.sh 验证 MSYS2 下 PID 命名空间不可见时的存活。

## 数据流

一次可视化会话的完整回路：

1. agent 调 `start-server.sh --project-dir <项目根>`，脚本按会话 ID（`$$-时间戳`）建 `.superpowers/brainstorm/<pid>-<ts>/{content,state}` 目录（start-server.sh:77-91）。
2. 三级环境探测决定运行模式：CODEX_CI 存在自动转前台（Codex 收割后台进程，start-server.sh:62-65）；MSYS/Cygwin/mingw OSTYPE 或 MSYSTEM 存在也转前台（Windows Git Bash 收割 nohup，start-server.sh:67-75）；其余走 nohup 后台+disown（start-server.sh:119-121）。
3. 解析祖父 PID 作 OWNER 传给服务器——$PPID 是 harness 派生的临时 shell、脚本退出即死，宿主本身是它的父进程（start-server.sh:102-108）；随后轮询日志 5 秒等 `server-started` JSON，并有"启动后被杀"二次存活校验（start-server.sh:124-144）。
4. agent 写 HTML 片段到 content/ 新文件（**绝不复用文件名**——服务器按 mtime 取最新，visual-companion.md:98-101），服务器 fs.watch 100ms 去抖后广播 `{type:'reload'}`（server.cjs:276-298），浏览器整页刷新。
5. 用户点击 `[data-choice]` 元素，helper.js 经 WebSocket 回传 JSON 事件，服务器落盘 `state/events`（JSONL，server.cjs:224-238）；agent 下一轮读 events 文件与终端文字合并判断（visual-companion.md:108-111）。
6. 生命周期保险丝：60 秒一次巡检，owner 进程死了或 30 分钟无活动就优雅退出并写 `server-stopped` 标记（server.cjs:319-323）；启动时校验 owner PID，已死则放弃监控只靠空闲超时（WSL/Tailscale 场景 PID 解析常错，server.cjs:326-337）；EPERM 视为存活（server.cjs:314-317）。
7. 收尾 `stop-server.sh`：SIGTERM 等 2 秒→SIGKILL 升级（stop-server.sh:22-39），仅 `/tmp` 会话整目录删除，`.superpowers/` 持久目录保留 mockup 供回看（stop-server.sh:5-7,48-51）。

## 设计决策

- **"浏览器只做展示，命令全在终端"**：2026-02 可视化重构（docs/superpowers/specs/2026-02-19-visual-brainstorming-refactor-design.md）确立的分工——浏览器负责视觉呈现与点击采集，所有执行动作仍在终端 agent 手里，浏览器永远不是控制面。
- **零依赖是硬性目标而非审美**：设计稿明言为消除 express/ws/chokidar 共 714 个被跟踪的 node_modules 文件（docs/superpowers/specs/2026-03-11-zero-dep-brainstorm-server-design.md:3），代价是手写 RFC 6455 帧编解码；这也是全仓"零第三方依赖"哲学最极端的样本（CLAUDE.md:29 明拒依赖型 PR）。
- **按问题决策而非按会话**：伴侣被接受≠每个问题都走浏览器；每问一次都要判断"看比读更好懂吗"（SKILL.md:156-161）——UI 话题的问题不自动是视觉问题（visual-companion.md:25）。offer 必须独立成一条消息且等待回应（SKILL.md:154），防止搭售式同意。
- **进程收割对抗是重点工程**：三种宿主（Codex CI、Windows Git Bash、某些容器）会收割脱离的子进程，start-server.sh 用环境探测自动前台化 + 调用方配 run_in_background/is_background 让进程跨轮存活（visual-companion.md:50-81 记录五平台启动差异，远程容器用 `--host 0.0.0.0`，L83-92）。
- **内容片段优于完整文档**：agent 默认只写内容 div，服务器自动包 frame 模板注入 helper（visual-companion.md:31）——既省 agent 的 token（不用每次写整套 HTML），又保证主题与交互基建一致。

## 勘误与新人提示

勘误三条：(1) tests/brainstorm-server/windows-lifecycle.test.sh:23 的 `SERVER_JS` 指向 `server.js`，磁盘实际是 `server.cjs`（v5.0.5 因 Node 22+ ESM 改名，RELEASE-NOTES.md 记载 PR #784），该 Windows 三测的 `node "$SERVER_JS"` 将直接模块缺失——重构后未同步的陈旧引用；(2) 零依赖设计稿写 `start-server.sh` 只需改一行 `index.js`→`server.js`，实际落地又改了一次名到 `.cjs`（specs/2026-03-11:103）；(3) 同目录 spec-document-reviewer-prompt.md 现无人消费。

新人提示：读 SKILL.md 时注意九步清单要求先建 TodoWrite 任务再逐项完成；若只是想理解服务器，从 server.cjs 的三段常量（等待页/模板注入/L58 去抖监视）入手比通读 354 行快得多；调试 companion 时先查 `state/server-info` 与 `server-stopped` 两个状态文件（visual-companion.md:46,97），30 分钟空闲自杀是最常见的"服务器不见了"原因。
