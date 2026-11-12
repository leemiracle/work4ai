# 09 · 子代理与编排：注册表、隔离、通知回传

> 证据：minified 源码偏移考古（Agent 工具 `LGo`[o=3510332]、注册表 `e7r`[o=1483294]、
> 生命周期状态机实测还原）[S]。深报告（19 字段 frontmatter 全表+90+ 遥测事件六类+
> fork 专路径）：`rea-claude/reports/09-subagents.md`（47KB）。

## 1. Agent/Task 工具 [S]

输入 schema：description（派发清单预览）/prompt/subagent_type/model（枚举
sonnet-opus-haiku-fable）/name（≤64 字符）/run_in_background（**默认 true**）/
isolation（worktree/remote）/cwd 互斥。

**spawn 前置检查链 12 道有序闸**：深度帽（嵌套 spawn 限制）→ teammate 扁平化 →
类型权限规则（`Agent(type)` 可 deny）→ 预算 → **并发槽（默认 20）** → fork 前置
（禁 remote isolation+禁递归 fork）→ requiredMcp 30s 等待 → **agent.spawn hook
（可改写或拒绝 spawn）**……

模型四级解析链：tool 参数 > frontmatter > env（CLAUDE_CODE_SUBAGENT_MODEL）>
inherit（父模型），带家族降级。

## 2. agent 定义注册表 [S]

- **五源加载**：policy > flag > project（`.claude/agents/*.md` + 附加目录）>
  user > plugin > builtin，同名后写覆盖 + inode 去重 + `pu()` 热失效；
- **frontmatter 19 字段**：name/description/tools/model/effort/permissionMode/
  maxTurns/background/memory(user/project/local)/observer/hooks/mcpServers/…；
- settings JSON agents 与插件版同构（插件版的 permissionMode/hooks/mcpServers
  被忽略并告警——**插件不能自带提权**）；
- fork 是内置定义（maxTurns 200/model inherit/permissionMode bubble）。

## 3. 隔离边界 [S]

子代理跑在**独立 AsyncLocalStorage**（agentContext：独立 transcript/
pendingMessages/看门狗/TaskRegistry）。

**关键实证（非推测）**：普通子代理经 `dDn` **intent forwarding** 只继承
"近期用户意图种子"，**不是全量对话历史**——只有 fork 才继承全量上下文+
replayLog+共享 prompt cache。这是"子代理看不到父会话"提示词声明的机制基础。

权限边界：permissionMode bubble（子代理权限在父会话沙泡内）；
worktree isolation：git worktree 独立工作区（EnterWorktree/ExitWorktree 配套）。

## 4. 生命周期与回传 [S]

```
spawn → queued → running → (keepalive 停靠可暂缓) → completed/failed/killed/blocked
                                    ↓
final report = _ut 提取末条 assistant 文本块（findings 切分 + 10 万字符帽）
                                    ↓
<task-notification> 六段（task-id/status/result/usage/worktree）作为 user 消息
回传 owner 会话
```

- 断点 resume：SendMessage 可从 transcript 断点复活死代理（本流水线 1308 团灭
  复活实操即此机制）；
- 失败恢复：watchdog、逐 agent 看门狗、后台任务事件通知。

## 5. 跨会话通信 [S]

- **SendMessage 路由 13 种 kind**：main / agent-live（→pendingMessages 下个
  tool round 排水）/ agent-stopped（→resume）/ agent-evicted（→mailbox）/
  uds / bridge / desktop_host…；
- **notify_when_idle**：一次性空闲订阅（仅主会话、有 cap、9 种失败原因）；
- **身份 pin `i2n`**：[name+ref] 防名漂移（重名时 latest wins，ref 消歧）；
- ListAgents = listAllPeers + 格式化。

## 6. 勘误与对照 [S]

- **propose_skills 不是 agent 动态注册**（是技能提案卡片工具）；agent 动态性
  来自插件安装/settings JSON/热失效三机制；
- 内嵌 Agent Design Patterns 文档的"独立 transcript/结果只回传摘要/并发限流/
  停止恢复"模式在二进制全部有对应实现，且 Claude Code 额外做了 keepalive 停靠、
  watchdog、identity pin 等文档未提的加固；
- 云侧 Managed Agents Multi-Agent 与本机同构（parent/child session、resume
  语义、spawn 权限 relay），差异=云侧服务端托管。

## 7. 手搓启示（→ rl-and-agents/）

1. **intent forwarding 是多代理上下文经济学的核心设计**：给子代理"意图种子"
   而非全量历史——fork 才是全量继承，两者是不同工具；
2. final report 提取规则（末条 assistant 文本+截断帽）简单但必须显式设计——
   否则子代理结论会散落在中间消息里；
3. task-notification 用 user-role 消息回传+五段 XML 结构：父会话无需任何特殊
   API 就能"看见"子代理完成——**通知即消息**；
4. 12 道前置闸的顺序（深度→权限→预算→并发→hook）是防御纵深的教科书排序：
   最便宜的检查最先做。
