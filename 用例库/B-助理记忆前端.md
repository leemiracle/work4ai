# 分册 B · 个人助理 / 记忆 / 前端（11 仓深读）

> 深读材料：README（前 300 行）+ 关键源文件（≤350 行）+ 代码树指标。行号证据限于已读片段。

### openclaw/openclaw
- **架构模式**：单操作者个人助理——本地 Gateway 控制平面统一会话/工具/事件/消息渠道，多端 UI 挂接到同一 Gateway。
- **核心抽象**：Gateway（README L18、L56）；OpenClawCli（apps/linux/src-tauri/src/cli.rs:9，桌面端以子进程方式驱动 CLI）；GatewaySnapshot（main.rs:25，状态快照驱动托盘/UI）。
- **关键机制**：
  - 桌面壳进程 spawn CLI 并解析 JSON 输出（cli.rs:98-109 `json<T>` 泛型反序列化；cli.rs:36-56 三级 discover：env override → `~/.openclaw/bin` → PATH）。
  - Gateway 生命周期状态机（main.rs:203-292 `connect/install_cli/gateway_action`，串行 operation lock + WebSocket 重配 + watchdog）。
  - 配对审批安全模型：DM 渠道默认 pairing（README L65）、pending_approvals 轮询（main.rs:347）。
  - 扩展生态外置：tools/skills/plugins + ClawHub（README L61、98），主仓 32k 文件中 extensions[8791] 占比大。
- **工程亮点**：Rust/Tauri 壳 + Node 核心的双运行时分层；"deep link 路由在 Rust 侧收口"的安全注释（main.rs:52-55）。
- **教学映射**：透视Agent系统工程（多渠道网关/审批流/沙箱）。
- **一句话本质**：把"一个 AI 助理"做成跑在自己设备上的常驻服务，从你已有的聊天软件里可达。

### obra/superpowers
- **架构模式**：零运行时代码的方法论层——纯 Markdown/Shell 技能包，靠初始指令让任意 coding agent 自动触发一套软件开发流程。
- **核心抽象**：Skill（skills/ 目录，51 个）；bootstrap（package.json:6 `.opencode/plugins/superpowers.js`，package.json:15-22 pi.skills 声明）；subagent-driven-development（README L269）。
- **关键机制**：
  - 七步强制工作流：brainstorming → git-worktrees → writing-plans → subagent 执行 → TDD → code-review → 收尾（README L263-277，"Mandatory workflows, not suggestions"）。
  - 每任务派发全新 subagent + 两阶段评审（spec 合规→代码质量）（README L269）。
  - RED-GREEN-REFACTOR 硬约束，先于测试写的代码会被删（README L271）。
  - 15 个 harness 各自安装但内容同一份（README L49-259）；Hermes 因无 post-compaction hook 会丢 bootstrap（README L257-259）——暴露 hook 能力差异。
- **工程亮点**：用"流程知识"而非代码作为分发物；195 个文件中 94 个 .md、41 个 .sh，几乎无逻辑代码。
- **教学映射**：讲透多Agent协作、讲透代码生成。
- **一句话本质**：把资深工程师的工程纪律编码成自动触发的技能，防止 coding agent 上来就乱写。

### NousResearch/hermes-agent
- **架构模式**：自提升型单 agent——闭环学习（技能自创/自改 + 记忆 + 用户建模）挂在一个多渠道 gateway 进程上，执行层抽象出 7 种终端后端。
- **核心抽象**：learning loop（README L19）；ContextCompressor（acp_adapter/server.py:77-80）；LSP Service（agent/lsp/cli.py:21-30，给 write_file/patch 提供语义诊断）。
- **关键机制**：
  - ACP 适配器把同步 AIAgent 放进 ThreadPoolExecutor(max_workers=4) 并行跑（acp_adapter/server.py:198-199）。
  - 自定义 provider 目录：声明模型 + 凭据可用时活拉 `/models` 并合并（server.py:157-189），每 provider 上限 200 防 Zed 下拉框爆掉（server.py:205-211）。
  - 跨会话召回：FTS5 会话搜索 + LLM 摘要 + Honcho 辩证式用户建模（README L26）。
  - 多步管道折叠为零上下文成本的 RPC Python 脚本轮（README L28）。
  - 一键从 OpenClaw 迁移（README L115、187-199）。
- **工程亮点**：`$5 VPS 到 GPU 集群`的部署谱系靠后端抽象实现（serverless 休眠唤醒，README L29）。
- **教学映射**：讲透学习型Agent、讲透记忆。
- **一句话本质**：让 agent 在使用中积累可复用的技能与对用户的理解，而不只是会话内聪明。

### open-webui/open-webui
- **架构模式**：自托管离线 AI 平台——FastAPI 单体后端 + Svelte 前端，RAG/插件/权限全部内置并可插拔。
- **核心抽象**：插件五类 Filters/Actions/Pipes/Tools/Skills（README L36）；Loader 分发器（backend/open_webui/retrieval/loaders/main.py:248-259）；SPAStaticFiles（main.py:283-295，前端路由回退 index.html）。
- **关键机制**：
  - 文档加载引擎矩阵：Tika/Docling/Mistral OCR/PaddleOCR-vl/外部 loader（loaders/main.py:25-29、140-245），同步解析统一经 `asyncio.to_thread` 卸载防阻塞事件循环（loaders/main.py:261-278）。
  - CJK 编码防御：chardet 只作提示、GB2312→GB18030 超集映射、解码后验证确实含 CJK 字符（loaders/main.py:288-350）。
  - 混合检索 BM25+向量 + 重排 + 全文模式，9 种向量库可选（README L60、74）。
  - lifespan 启动编排：legacy 配置导入→种子默认值→管理员账户（main.py:325-345）。
- **工程亮点**：离线优先（README L15）与 RBAC/LDAP/SCIM 企业面并存；5031 文件中 3840 是 svg，产品化打磨痕迹。
- **教学映射**：讲透RAG、透视Agent系统工程。
- **一句话本质**：给 Ollama/OpenAI 兼容生态一个不联网也完整可用的 ChatGPT 级自托管前端。

### danny-avila/LibreChat
- **架构模式**：多用户 ChatGPT 克隆演进为 Agent 平台——Express/React 双端，Agents/工具/MCP 在统一 Agent Builder 里编排。
- **核心抽象**：React Context Provider 矩阵（client/src/Providers/index.ts:1-29，29 个导出：Chat/Agents/Artifact/ToolCallsMap…）；Agents + Subagents（README L91-101，子 agent 有独立上下文窗口）；SKILL.md 技能包（README L97）。
- **关键机制**：
  - 运行中干预：中断/steer/排队追问、reclaim 与 escalate（README L56）。
  - Human-in-the-loop：agent 暂停提问、表单收集最多 4 问、工具审批后续跑（README L57）。
  - 流式可靠性工程：自适应 provider 平滑、Redis delta 批量、流式熔断（README L69）。
  - 无代码 Agent 市场与组共享（README L94-95）。
- **工程亮点**：4046 文件、.ts 1900 + .tsx 1142，前后端契约与多租户安全（SSRF 检查、密钥加密，README L67）是重投入区。
- **教学映射**：讲透多Agent协作、透视Agent系统工程。
- **一句话本质**：让团队自托管一个能把各家模型、MCP 工具和子 agent 拼成产品的多用户 Agent 工作台。

### SillyTavern/SillyTavern
- **架构模式**：零构建 Node/Express 单进程 + 浏览器端重逻辑的 LLM 前端（README 仅存根，证据以 package.json 与 tree-metrics 为准）。
- **核心抽象**：public/ 直发前端（tree: public[591]、default[200]、src[110]，.html=110）；角色卡/预设体系（AGPL 前端 for power users，README L3）。
- **关键机制**：
  - Express + helmet/csurf/ip-matching 安全栈（package.json:51、57、61-64）。
  - 浏览器侧持久化 localforage + 服务端 node-persist（package.json:69、79）。
  - 扩展分发内嵌 git：isomorphic-git（package.json:67）。
  - 富媒体处理全在本地：Jimp 全家桶 + WASM 编解码（package.json:7-28）。
  - Handlebars 模板 + fuse.js 模糊搜索（package.json:54、56）。
- **工程亮点**：无打包、无构建步骤的"克隆即用"哲学，988 文件里 .js=347 全部直读。
- **教学映射**：透视Agent系统工程（反面对照：无框架前端如何长生命周期存活）；讲透上下文缓存（其核心玩法是 token 预算/上下文手工编排）。
- **一句话本质**：给 prompt 炼丹师一个可精细控制每一段上下文、角色与世界观的本地前端。

### mem0ai/mem0
- **架构模式**：独立记忆层服务/SDK——单遍 ADD-only 抽取 + 多信号融合检索，User/Session/Agent 三级作用域。
- **核心抽象**：Memory add/search API（cli/node/src/index.ts:314-350）；实体链接与多信号检索（README L59-60）；Agent Mode 账户（README L88-107）。
- **关键机制**：
  - 新算法：一次 LLM 调用只做 ADD 不做 UPDATE/DELETE，记忆只增不改（README L57），LoCoMo 92.5/LongMemEval 94.4（README L47-52）。
  - 检索 = semantic + BM25 + entity 三路并行打分融合 + 时间感知排序（README L60-61）。
  - 作用域解析：显式 ID 优先、否则落 config 默认，避免过度过滤（index.ts:109-145 resolveIds）。
  - API key 启动即 ping 验证（5s 超时竞速），agent 可无人值守注册、人类事后 claim（index.ts:53-88；README L107）。
  - add 级控制项：--immutable、--expires、--no-infer、structured-data-schema（index.ts:324-346）。
- **工程亮点**：把"agent 是一等用户"做进注册流（--agent-caller 归因，index.ts:229-231）。
- **教学映射**：讲透记忆。
- **一句话本质**：给任何 agent 外挂一个跨会话、token 高效、可作用域隔离的长期记忆后端。

### thedotmack/claude-mem
- **架构模式**：Claude Code 生命周期 hook 旁挂系统——hook 捕获观察 → 后台 Worker 服务做摘要/存储 → MCP 工具按需渐进取回。
- **核心抽象**：Observation（openclaw/src/index.ts:133-149 SSE 载荷：facts/concepts/files_modified）；Worker Service（README L228，Bun 托管本地 HTTP）；OpenClawPluginApi 事件面（index.ts:99-131）。
- **关键机制**：
  - 5 个生命周期 hook：SessionStart/UserPromptSubmit/PostToolUse/Stop/SessionEnd（README L226）。
  - 三层检索省 token：search 索引（50-100 tok/条）→ timeline → get_observations 全文，约 10 倍节省（README L243-252）。
  - Worker 熔断器：CLOSED/OPEN/HALF_OPEN，3 次失败断 30s（index.ts:243-299）。
  - after_compaction 事件监听（index.ts:126）——压缩后记忆仍可回注。
  - SQLite + FTS5 关键词 + Chroma 向量混合（README L210-211）。
- **工程亮点**：同一核心以 plugin 形态同时接入 Claude Code 与 OpenClaw Gateway，observation SSE 可推送 Telegram 实时观察流（README L163-171）。
- **教学映射**：讲透记忆、讲透上下文缓存。
- **一句话本质**：把 coding agent 的工具使用痕迹自动变成可检索的项目长期记忆，且取回时按层付费。

### letta-ai/letta
- **架构模式**：MemGPT 延续——OS 式分页记忆的 agent 服务器：记忆块（block）+ 召回存储 + 消息历史三层，agent 自主编辑自己的记忆。
- **核心抽象**：BaseAgent.step（letta/agent.py:79-93，唯一抽象接口）；Memory blocks + BlockManager（agent.py:130、200-234，"LRW blocks"）；ToolRulesSolver（agent.py:116，工具调用状态机）。
- **关键机制**：
  - 记忆变更检测：new_memory.compile() 不在系统提示里则逐 block 更新并重建系统提示（agent.py:200-234）。
  - 只读块保护：read_only block 被改即抛错（agent.py:191-198）。
  - 上下文溢出自愈：捕获 ContextWindowExceededError 后 summarize_messages 截断（agent.py:L25、41、35 calculate_summarizer_cutoff）。
  - 工具规则约束 LLM：init/terminal tool rules + 强制首工具调用 + 失败工具短期禁用（agent.py:316-349）。
  - manager 群（Message/Passage/Block/Agent/Step，agent.py:141-148）把持久化拆细。
- **工程亮点**：本仓已是 legacy server（README L9 指向 letta-code），但 block 化记忆模型是业界被引用最多的先例。
- **教学映射**：讲透记忆、讲透学习型Agent。
- **一句话本质**：证明"让 agent 像操作系统管理内存一样管理自己的上下文"是可行的记忆架构。

### github/spec-kit
- **架构模式**：Spec-Driven Development 工具链——specify CLI 把模板/斜杠命令装进 30+ agent，规格成为可执行物直接生成实现。
- **核心抽象**：specify CLI（pyproject.toml:19-20）；模板优先级栈 overrides > presets > extensions > core（README L198-209）；Bundle（README L243-255，角色化组件包 + catalog 栈）。
- **关键机制**：
  - 五段流程：constitution → specify → plan → tasks → implement（README L95-131），辅以 clarify/analyze/checklist（README L186-188）。
  - 核心资产全部打进 wheel，离线可用（pyproject.toml:29-54 force-include core_pack）。
  - 模板运行时解析取首个匹配，扩展/预设装时落盘、卸载自动降级（README L205-209）。
  - bundle 可验证、幂等、remove 不动他包依赖（README L292-295）。
  - ruff S602/S604/S605 锁死 shell=True，需显式 noqa（pyproject.toml:82-90）。
- **工程亮点**：纯"文档工程"——539 文件中 .py=295 但核心交付物是模板与流程。
- **教学映射**：讲透代码生成、软件即熵治理（规格先行正是熵治理）。
- **一句话本质**：在写代码之前强制把"要建什么"写成机器可执行的规格，杜绝 agent 对着一句模糊需求开干。

### JuliusBrussee/caveman
- **架构模式**：分层 token 缩减栈——MIT skill 管输出措辞，本地 Proxy+Engine 压输入负载，CCR 存储保证被压字节可精确还原。
- **核心抽象**：Caveman Engine + CCR 恢复库（README L90；browse/cmd/caveman-browse/main.go:61-81 `ccr.Store` 落盘 ~/.caveman/ccr.db）；Skill 即系统提示（benchmarks/run.py:56-57 直接 read SKILL.md 当 system）；MCP stdio 工具服务器（main.go:54-58）。
- **关键机制**：
  - browse 双模式：无参时 MCP stdio server（CDPDriver+Engine），带参时 direct CLI：snapshot/act/eval/recover（main.go:24-59、98-160），recover 用 recovery_handle 取回原始字节。
  - 基准方法学：normal vs caveman 各 N trial、取中位数算节省率（run.py:105-150）；.env.local 只读 ANTHROPIC_API_KEY 一个键防 exfil（run.py:19-35）。
  - 诚实数字声明：只省输出、skill 本身每轮 +1-1.5k 输入，可能净负（README L156-157）。
  - 分发三档独立采用：skill / proxy wrap / browse（README L45-69），Proxy 33.2% 输入节省（README L11、177）。
- **工程亮点**：压缩-恢复闭环（引擎存每个被移字节）+ MIT/BSL 边界清晰的许可证分层（README L92-94）。
- **教学映射**：讲透上下文缓存（更准确说是上下文压缩与恢复经济）。
- **一句话本质**：在不动 agent 的前提下，把进出模型的每一个字节都变便宜且可逆。

---

## 组内横向对比

**记忆三家的机制差异**：mem0 是"外部记忆服务"——抽取（单遍 ADD-only）与检索（semantic+BM25+entity 三路融合）都是 API 内的独立阶段，token 效率靠检索预算控制，记忆本体是扁平事实。letta 是"操作系统式记忆"——block 化、agent 自己用工具改记忆、只读块保护、溢出时摘要自愈，记忆是 agent 状态的一部分。claude-mem 是"痕迹考古式记忆"——不主动抽取对话，而是 hook 捕获工具观察，靠三层渐进披露（search→timeline→get_observations）在取回侧省 token。三者恰好覆盖《讲透记忆》的三讲：抽取层（mem0）、架构层（letta）、消费层（claude-mem）。

**个人助理谱系（openclaw/hermes/superpowers）**：openclaw 是"平台派"——Gateway/渠道/插件生态，工程重心在系统工程；hermes 是"能力派"——同构的 gateway+渠道外壳（甚至能从 openclaw 迁移），但差异化押在自提升闭环（技能自创、用户建模、LSP 反馈）；superpowers 是"无运行时派"——不建平台，只把方法论编译成技能注入别人的 agent。三者正好是助理架构的三个注入层级：基础设施（openclaw）、agent 内核（hermes）、提示层（superpowers）。

**caveman 的定位**：它是这组里唯一的"经济层"工具——不生产能力，只削减 token 成本，且与所有上层兼容（wrap openclaw/hermes 均可）。与 claude-mem 互补：claude-mem 省的是"要不要把记忆放进上下文"（信息选择），caveman 省的是"放进来的每个 payload 本身"（字节压缩+可逆恢复）。二者叠加即《讲透上下文缓存》的完整课程骨架。
