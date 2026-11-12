# 10-incremental · rc.5→rc.8 增量 + Agent Notes 决策制度 + context/compaction 深读

> 一句话：**647 commits / +61.7K 行的三周冲刺里，dsh 交出了 SQLite 压缩事件日志、外部 agent 子代理化、agent-teams 实验包——并用一套 544 篇 ADR 宪法管住了全部决策。**
>
> 基准：本地克隆 `~/ai/agent/awesome-agents/repos/deepseek-harness`，HEAD=`141eb6fef8`（rc.8，2026-08-19）；旧基线 47f943859b（rc.5，2026-08-13）。笔记 00-09 基于 rc.5，行号在 rc.6-8 可能漂移。
> 本篇由 2026-08-21 双 subagent 深读 + 主线抽查产出，路径缩写 `CTX/`=packages/context 等。

## 1. rc.5→rc.8 增量考古（647 commits, 1767 文件, +61,741/-11,652）

**版本主题**（notes 时间线代理法——release commit 无正文，用带日期门禁的 .agents/notes 交叉定位）：

| 版本 | 时段 | 主题 |
|---|---|---|
| rc.6 | 08-10~13 | 发布工程化（npm 序列/vendor rescope）；**preset/host 平面所有权大重构**；remote-event-delivery；session-log 版本机制；pwsh 持久 PTY |
| rc.7 | 08-15 附近 | **客户端动态包架构**；SQLite 物理 chunk 压缩；**实验性 agent-teams**（experimental- 前缀包）；DeepSeek 视觉输入直传；pi-ai wire 兼容 |
| rc.8 | 08-19 | 每轮回传 reasoning；subagent 命名多实例收尾；fix 流（code-runtime 版本对齐等） |

**变更热点**（git diff --name-only 分组）：client 445 / .agents/notes 333 / session 93 / acp-agent 示例 67 / subagent 60 / llm 47 / context 36。

## 2. Agent Notes：把 ADR 写成宪法（本仓最被低估的资产）

`.agents/notes/` = 仓库自有决策记录制度（为 agent 驱动开发设计）：

- **路径即状态机**：`{lifecycle}/{class}/yyyy-mm-dd-topic.md`，lifecycle ∈ proposed→implemented→rejected→archived（README.zh.md 布局节）；class 是封闭集（feature/bug-fix/architecture/process/simplification/testing），**分类门禁**拒绝其他文件夹
- **强制骨架**：Problem / Decision / Alternatives considered / Consequences 四段 + 中英双文件 + i18n sidecar，`verify-agent-note-format` 门禁；**每个非平凡 PR 必须同 PR 带一篇 note**（README.md:46）
- **implemented 与交付同步**：代码后续移动/重命名时 note 在同一变更中同步更新事实（仅事实，非决策）
- **rejected 只留仍有防错价值的**：否则整组三文件删除——拒绝信也在还债
- **故意不设 INDEX.md**（implemented/process/2026-07-19-remove-generated-agent-note-index.md）：生成式索引是 merge 热点且信息已被路径编码；生命周期目录树即库存清单
- **规模**：implemented ≈544 篇（architecture 140 / feature 183 / bug-fix 90 / process 71 / simplification 47 / testing 13，×3 文件形态）
- **质量样本**：sqlite-chunk-compression note 含 schema+105 会话基准+11 个被否决替代方案；rejected/prune-unused-skill-registry-api 明说"direct runtime skill registration 是留给第三方的刻意扩展点"——**拒绝了删 API 的简化提案，理由是保留接缝**

## 3. context 真相：packages/context 不是上下文引擎

**纠正预期**：CTX/ 只是"请求上下文扩展"插件族（agent-instructions 唯一默认启用 + time/tmux/session-reference/file-reference 六包），注入方式=持久化 user message 而非改 system prompt。真正的组装在 core 三件套：

- `SystemPrompt` 服务：有序 sections（约定 harness 身份 -100 / persona 0 / 工具 100-199，CORE/system-prompt/src/index.ts:53-75）+ waterfall + 严格 `{{var}}` 插值
- **稳定前缀=EpochHeader**：system+tools+config 打包，仅变化时追加 `request/header` 事件（agent.ts:484-489）——头部未变即前缀稳定，KV-cache 友好
- 动态上下文渲染成 "supersedes earlier snapshots" 的 user 快照（index.ts:236-240）

## 4. compaction：KV-cache 对齐 + 事件溯源内建审计

- **三路触发**：步间压力（0.8×窗口）/ 溢出恢复（捕 CONTEXT_WINDOW_EXCEEDED）/ 手动；**先跑免模型剪枝再重测**（pruner 阈值 8192，head 4096 > tail 1024——承认输出头部更重要）
- **切点**：尾向累计 retainTokens（默认 16%），回退到不切破 tool 配对处；**保留边界按配对不按整 turn**（可压超大 turn 的早期步）
- **摘要即缓存复用**：原样重放会话真前缀 + 压缩指令作最后一条 user message——**显式为复用 provider KV cache 省一次全量 prefill**（summarizer.ts:26-31）
- **输出**：8 节结构化 checkpoint（Primary Request/Files/Errors/Pending/Next Step…）——与 openclaw/Claude Code 同源模板
- **无独立 safeguard 层**，用事务不变量替代：摘要必须严格小于被压内容、拒图片、截断=失败、`compaction/start→end` 持久锁（**孤儿锁即崩溃信号**）、溯源全记录（provider/model/usage/rawOutput）
- **插件形态**：标准三角色 seam，生产实现仅 1 个（BasicCompactionEngine）

## 5. session 日志：双后端 + "Model-visible ⟺ logged" 的运行时强制

- **事件信封** `{type,seq,time,data,surfaceOp?,sourceEventSeqs?}`；关系不变量（seq 单调/turn 包络/tool 配对）在加载时 replay 校验（invariant.ts:55-166）
- **JSONL 默认**：zstd 帧拼接 + POSIX 硬链接无覆盖发布 + fsync；崩溃保留完整尾帧并合成修复闭合器；packed row 省 ~60%
- **SQLite opt-in**（rc.7 新）：schema-17 物理 packed row（≤1024 事件/1MiB、≥4KiB 走 zstd-3、varint+ZigZag）——**250 万逻辑事件→6.6 万行，小 89.4%**；`synchronous=FULL`
- **反欺骗断言**（agent-loop/src/invariant.ts:39-42）：dev 模式逐请求校验 `JSON.stringify(options.messages) === JSON.stringify(session.deriveMessages())`，失配报 "log-reconstruction desync"；loop 取消息唯一路径=`deriveMessages()`，注入必须走 `inject()`→排队成 user/message 事件
- **压缩五步事务**：start(锁)→摘要→summary→唯一 surface 变异（一条 user/message 带 replace span）→end；replace 是**遮蔽非删除**，raw log 恒 append-only

## 6. 与 openclaw 的两极（速览，详见对照卡）

| 维度 | openclaw | dsh |
|---|---|---|
| 长期记忆 | 165K 行子系统（MEMORY.md+dreaming+溯源） | **没有**——"工作区是唯一跨轮长期记忆"（tool-ralph/README.md:90） |
| 上下文 | 集中式 context engine（可插拔） | core 数据面+事件协议，context/ 只是扩展插件 |
| 压缩审计 | 独立 safeguard 层（纯代码判分） | 事件溯源内建（无第二双眼睛） |
| token 计数 | chars/4 估算 | 估算+**usage 锚定增量维护**（TokenMeter） |
| 子代理 | sessions_spawn | **subagent-codex / subagent-claude-code**（把竞品当可插拔子代理） |

## 7. 附录：端侧/Android 定位澄清（2026-08-21 补）

**官方支持 = 零**（钉版 rc.8 全仓 grep 证据）：

- `"android"` 全仓唯一命中是测试夹具假目录名（`packages/client/connection/src/client/fixture.ts:1596` 的虚构项目列表 `deepseek-android`）
- **无 Termux 支持**（对比 openclaw 有 `resolveTermuxHome` 正则 + Bionic libc 专门处理的代码级支持，dsh 一行都没有）
- 分发面刻意锁死桌面：Python SDK wheel 只有 `manylinux_2_28` / `macosx_14_0_arm64` 标签，**构建钩子主动拒绝**其他平台（python/sdk-runtime README：拒 `py3-none-any` 与不支持标签）；Android Bionic libc 进不了官方分发链
- 主形态 Node ≥22 CLI/Web + native/landlock-run 沙箱（Linux LSM，Android 内核不带）

**三条真实路径**：

1. **瘦客户端（正统）**：手机浏览器访问 `<server>:3080` Web UI，或 Android 原生 app 做 ACP 客户端连远程 dsh（subagent-acp + examples/acp-agent）——与 openclaw"手机是 node 不是主机"同构，2026 年 agent 框架共识：推理和 harness 不上手机
2. **Termux 源码路线（社区可行性，非可用级）**：比 openclaw 更崎岖——node-pty 原生模块需 Termux 编译、landlock 沙箱缺失会退化
3. **架构移植（真正价值）**：dsh 对端侧的意义是**教科书而非运行时**——可抄清单：append-only 事件日志 + zstd chunk 压缩（250 万事件→6.6 万行=89.4%，为低存储设备准备；崩溃合成修复闭合器匹配移动端进程被杀现实）；"Model-visible ⟺ logged" 断言（端侧隐私审计刚需）；免模型剪枝（端侧小窗口省钱标配）；"工作区即记忆"（端侧记忆=本地文件，规避隐私审查）；subagent-codex/claude-code 范式（端侧本地小模型路由 + 云 agent 即插件）。**端侧四层模型栈（对话/嵌入/感知/规则）dsh 一个都不提供**——它不是端侧玩家

**与 work4ai 的关系**：本土五成员 harness 中 **rust-harness 是唯一可能真上 Android 的**（Rust+NDK 交叉编译，无 Node/Bionic 依赖）——dsh 的接缝三角色 + 事件溯源可用 Rust 在端侧复刻。

## 审计命令

```bash
cd ~/ai/agent/awesome-agents/repos/deepseek-harness
git log -1 --format=%h                      # 141eb6fef8 (rc.8)
git log --oneline 47f943859b..HEAD | wc -l  # 647
ls .agents/notes/implemented/*/ | wc -l     # ADR 分部
cat packages/workflow/tool-ralph/README.md | grep -n "only cross-round"   # 记忆哲学
grep -n "log-reconstruction" packages/core/agent-loop/src/invariant.ts    # 反欺骗断言
```
