# 06 · 权限与沙箱：三态规则、六模式、三沙箱

> 证据：minified 源码偏移考古（求值器 rho[chunk-1kyfp16b offset=2271929]、
> bwrap 构造器 YLt[offset=938395] 等）[S]。深报告（完整参数表+总伪代码）：
> `rea-claude/reports/06-permissions.md`（41KB）。

## 1. 规则模型 [S]

规则字符串 → `{toolName, ruleContent?}`。三态 allow/deny/ask，**硬序：
deny > ask > allow > 兜底 ask**。

- **Bash 类匹配**（ruleContentField="command"）三分类：
  `git diff:*`（冒号星号）= **prefix 语义**；`git diff *`（空格星号）= wildcard
  （单星结尾时裸命令也匹配）；其余 exact。默认**大小写敏感**；
- **Read/Edit 类**：编译成 **gitignore 语义的 ignore 实例**，按 root 分组匹配，
  allow 要求**每个候选路径（含 realpath）都被覆盖**——防 symlink 逃逸；
- 工具名匹配含别名与 family 上卷（Task 子工具映射回父工具规则）；
- 来源全序（先匹配先赢）：userSettings → projectSettings → localSettings →
  flagSettings → policySettings → cliArg → command → session → toolsNarrowing
  → mcpServerPolicy → hostCredential（10 个来源槽）。

**危险规则过滤**：`Bash(*)`、`Bash(curl*)`、`iex` 类宽放行在展平时直接跳过
（遥测 tengu_ant_overly_broad_bash_detected）；startup 还有拼写体检
（"matches no known tool — check for typos"）。

## 2. 六种权限模式（不是四种）[S]

| 模式 | 语义 |
|---|---|
| default | 完整求值，兜底 ask |
| acceptEdits | 工作区内文件读写放行，Bash 仍问 |
| plan | 只读白名单；plan 期间暂停沙箱自动放行；退出还原前模式 |
| bypassPermissions | 全放行（需 --dangerously-skip-permissions 启动 + 未被 disable） |
| **dontAsk** | 走到 ask 一律改判 deny（不弹窗的 headless 场景） |
| **auto** | **审查模型分类器审批**：快路径 acceptEdits 模拟 → 安全 allowlist → 分类器两阶段 → ask 硬顶回落 |

Shift+Tab 循环序：plan → default → acceptEdits → auto(可用时) →
bypass(可用时) → 回 plan。dontAsk 不进循环。

## 3. ask 的三条出口 [S]

1. SDK `canUseTool` 回调（宿主注入）；
2. CLI ConsentRow 弹窗（**用 AskUserQuestion 组件渲染**）——选项即权限更新预览：
   一次性 Yes/No、"always allow <paths> from this project"（写 localSettings）、
   会话级目录宽限、"switch to <mode>"、Bash 沙箱弹窗的 "Don't sandbox this
   command"（写 excludedCommands）；
3. 远程 relay（control_request 帧回宿主，ask/deny 都按 deny 回传——远程无交互面）。

always-allow 写回 `.claude/settings.local.json`（Oc 纯函数 reducer，
六型 update：setMode/addRules/replaceRules/removeRules/add/removeDirectories）。

## 4. 沙箱：三实现（勘误：无 landlock）[S]

| 平台 | 实现 |
|---|---|
| macOS | seatbelt（sandbox-exec -p，deny-default 白名单式 SBPL） |
| Linux/WSL2 | **bubblewrap**：--unshare-net/pid/user + cap-drop ALL、全盘 ro-bind 基线 + 写白名单 bind + denyRead tmpfs + 祖先 pin；网络经 socat 代理桥 + **seccomp 封禁 Unix socket**（@anthropic-ai/sandbox-runtime） |
| Windows | srt-win.exe + 专用沙箱用户 + **WFP 网络过滤** |

> **勘误**：全产物 `grep -ri landlock` 零命中——v2.1.261 无 landlock 实现。

沙箱 profile 五节：network（allowedDomains+CEL 表达式+proxy）、filesystem
（allowWrite/denyWrite/denyRead 与 Edit/Read 规则**双向合并**）、credentials
（envVars deny/mask/注入；文件 mask=哨兵替换+jwt decode）、excludedCommands、
强度（strict/relaxed）。管控键矩阵：大部分键 project settings 无发言权。

`autoAllowBashIfSandboxed`（默认 true）：**沙箱内 Bash 自动放行**——沙箱是
权限的加速器不是减速器。初始化失败：failIfUnavailable 则停，否则本会话降级告警。

## 5. 文件写守卫与逃生门 [S]

- Bash 命令内**静态分析**提取路径入闸（写白名单外 → 走 Edit 权限通道）；
- `dangerouslyDisableSandbox:true` 且无豁免 → 改判 ask
  （decisionReason=sandboxOverride）；remote sandbox:"required" 无全封闭沙箱
  → 直接拒绝；
- deny 规则与硬 safetyCheck **永不被 hook/模式豁免**。

## 6. 手搓启示（→ rl-and-agents/）

1. 三态+硬序（deny>ask>allow>兜底 ask）是 20 行就能复刻的骨架，gitignore 语义
   的路径匹配直接用 ignore npm 包——不要手写；
2. auto 模式的四级快路径设计（模拟 acceptEdits→allowlist→分类器→ask 回落）
   是"LLM 审批"的工程化范本：分类器是最后一档不是第一档；
3. 沙箱=权限的加速器（sandboxed → auto-allow）而非纯枷锁——安全与流畅不对立；
4. 危险规则静默跳过+拼写体检：**配置层的防线同样重要**（用户写的 allow 规则
   本身就是攻击面）。
