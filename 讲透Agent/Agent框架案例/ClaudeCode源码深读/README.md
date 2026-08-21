# Claude Code 源码深读 🏛️ 512K 行 TS 的工业级 Agent Harness

> 一句话定位：**2026-03-31 经 npm `.map` 文件意外泄露的 Claude Code v2.1.x 完整 TypeScript 源码（1884 文件/512,664 行实测）——迄今最完整的商业级 AI Agent harness 实例，本卡对其核心子系统做 file:line 级源码深读。**
>
> 本地源码树：`~/ai/agent/awesome-agents/repos/claude-code-source/src/`（GitHub: ximing/claude-code-source，钉版 `091cde4` 2026-04-12，含 20 篇配套拆解文章）
> 源码规模实测：**1884 个 .ts/.tsx / 512,664 行**；main.tsx 4,683 行 / query.ts 1,729 行 / QueryEngine.ts 1,295 行 / api/claude.ts 3,419 行 / hooks.ts 5,022 行 / BashTool 目录 1.2 万行+ / tools/ 43 个工具目录
> 验证状态（2026-08-20）：抽查 6 处关键行号引用（State 10 字段/DYNAMIC_BOUNDARY/ABLATION_BASELINE/feature() require/SALT/p99.99 常量）**全部与源码逐字一致**——本仓文章的 file:line 引用可信

## 它是什么 / 不是什么

- **是**：泄露源码的还原树（部分文件保留 React Compiler 编译后形态，辨析法见 01 篇）+ 20 篇逐行拆解
- **不是**：claw-code（那是净室重写仓，Rust 正典，见[姊妹卡](../claw-code/README.md)）；也不是 anthropics/claude-code 官方仓
- 用户提供的两条知乎链接（p/2022605516262614921 / p/2022389695955346888）因反爬 403 未能直读；同期公开解读（新智元/掘金/WaveSpeed/唐靖凯/s-blog/MoYan/CSDN）已交叉印证，文献地图见 claw-code 卡 01 篇

## 为什么值得深读（讲透Agent 宇宙的第一教材）

1. **agent 主循环的完整解剖标本**：`queryLoop` 显式状态机（7 个 continue 点/10 种 Terminal reason），比任何论文都具体（02 篇）
2. **上下文工程三件套的工业实现**：系统提示装配流水线 + prompt cache 工程 + **五层压缩体系**——"能用便宜的无损手段就绝不用昂贵的有损摘要"（04 篇）
3. **安全纵深防御的教科书**：Bash 三层防线（AST 解析→策略→沙箱）+ 权限编号求值步骤——23 项解析器差异攻击编目（03/06 篇）
4. **记忆不是向量库**：文件即记忆 + 四类型学 + autoDream 四阶段"做梦"整理 + 团队共享（05 篇）
5. **多 Agent 的账本**：隔离 vs 共享的每处取舍都带量化理由（每周 34M 次 Explore 派生省 5-15 Gtok）（07 篇）
6. **隐藏面 = 同一仓库两种构建三种用户**：89 个编译期 feature flag + GrowthBook 运行时开关 + buddy 电子宠物 + undercover 缄默协议 + anti-distillation 反蒸馏投毒（07 篇）

## 阅读顺序

| # | 笔记 | 覆盖源码 | 回答的问题 |
|---|---|---|---|
| 1 | [01-启动链路与架构](notes/01-启动链路与架构.md) | cli.tsx/main.tsx/init.ts/state.ts/tools.ts/commands.ts | 51 万行怎么组织、启动为什么快、全局状态怎么管 |
| 2 | [02-Agent主循环](notes/02-Agent主循环.md) | query.ts/QueryEngine.ts/query/* | 思考-行动-观察循环的显式状态机实现 |
| 3 | [03-工具系统与Bash三层防线](notes/03-工具系统与Bash三层防线.md) | Tool.ts/tools.ts/toolOrchestration/toolExecution/BashTool/* | 43 工具的注册调度并发 + 最危险工具的纵深防御 |
| 4 | [04-上下文工程三件套](notes/04-上下文工程三件套.md) | prompts.ts/systemPrompt.ts/claude.ts/compact/* | 提示装配/缓存/五层压缩如何咬合 |
| 5 | [05-记忆系统](notes/05-记忆系统.md) | memdir/*/extractMemories/autoDream/SessionMemory/teamMemorySync | 没有 DB 的记忆体系怎么记得住 |
| 6 | [06-权限管线与沙箱](notes/06-权限管线与沙箱.md) | utils/permissions/*/sandbox/upstreamproxy | 一次工具调用的 allow/deny/ask 怎么裁决 |
| 7 | [07-多Agent与隐藏面](notes/07-多Agent与隐藏面.md) | AgentTool/swarm/coordinator/buddy/undercover/insights | 三层多 Agent 体系 + 不打算让你看见的东西 |

## 审计总命令

```bash
cd ~/ai/agent/awesome-agents/repos/claude-code-source
git log -1 --format=%h                      # 钉版 091cde4（漂移则行号需重验）
find src -name '*.ts' -o -name '*.tsx' | xargs wc -l | tail -1   # 512,664
wc -l src/main.tsx src/query.ts src/QueryEngine.ts               # 4683/1729/1295
ls src/tools/ | wc -l                       # 43 工具目录
ls articles/                                # 20 篇拆解
```

## 20 篇原文索引（articles/，全部 file:line 钉版）

**核心循环与工具**：01 启动架构 · 02 Agent 主循环 · 03 流式与 API 客户端 · 04 工具系统 · 05 Bash 三层防线 · 06 文件与搜索工具（为什么是 grep 不是向量索引）
**上下文与记忆**：07 系统提示装配 · 08 提示缓存与成本 · 09 上下文压缩 · 10 记忆系统
**安全与扩展**：11 权限管线 · 12 沙箱与出口代理 · 13 MCP 客户端 · 14 Skills 渐进披露 · 15 Subagent 与多 Agent · 16 Hooks 引擎（5022 行/27 事件/五形态）
**持久化与收官**：17 会话持久化与恢复 · 18 TUI 渲染（重度 fork 的 Ink） · 19 任务系统与自动化 · 20 隐藏面

## 项目内交叉引用

- **净室重写对照**：[claw-code](../claw-code/README.md)（Rust 重写仓，每个机制都有"泄露版 vs 净室版"对照点，散见各篇）
- **同维度案例**：[openclaw](../openclaw/README.md)（插件宿主）· [deepseek-harness插件化框架](../deepseek-harness插件化框架/README.md)（官方插件化）
- **理论底座**：[harness工程手册](../../../工程化手册库/harness工程手册/README.md)（六组件模型——02/03 篇逐件对表）
- **Skills 生态**：[Skills生态全景](../Skills生态全景/README.md)（14 篇渐进披露是其实现在 CC 内核侧的锚点）
- **MCP 生态**：[MCP协议生态全景](../MCP协议生态全景/README.md)（13 篇六种传输是客户端侧锚点）
