---
title: Claude Code 源码拆解 05：Bash 工具的三层防线
date: "2026-04-04 21:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 05/20 篇 · 对应主题：护栏在工具层

# Bash 工具的三层防线

Bash 是 Claude Code 里能力最大、风险也最大的工具：模型可以发出任意 shell 字符串。源码对这个工具的处理不是一道"权限弹窗"，而是一条纵深防御流水线。所有决策汇聚在一个函数里：`bashToolHasPermission`（src/tools/BashTool/bashPermissions.ts:1663）。从它的代码组织可以清楚看出三层结构：

1. 静态解析：先用 tree-sitter AST 解析命令，回答"这个字符串能不能被信任地拆开"（src/tools/BashTool/bashPermissions.ts:1670-1739）；
2. 策略：规则匹配、分类器、只读推断，回答"策略上允不允许"（src/tools/BashTool/bashPermissions.ts:1845-2292）；
3. 运行时：路径约束与沙箱，回答"执行时被限制在什么边界内"（src/tools/BashTool/pathValidation.ts:1013，src/tools/BashTool/shouldUseSandbox.ts:130）。

## 第一层：AST 解析与注入检测

`bashToolHasPermission` 的第一步不是查规则，而是调 `parseCommandRaw` 做 tree-sitter 解析（src/tools/BashTool/bashPermissions.ts:1692）。解析结果有三种形态：`simple`（干净的子命令列表）、`too-complex`（含命令替换、展开、控制流等无法静态分析的结构）、`parse-unavailable`（WASM 未加载）。`too-complex` 直接转 `ask`，但会先跑 `checkEarlyExitDeny` 保证显式 deny 规则不被降级成 ask（src/tools/BashTool/bashPermissions.ts:1741-1768）。`simple` 则把 AST 切出的子命令、重定向、argv 缓存下来供下游使用，避免下游再用有已知 bug 的正则/shell-quote 重解析（src/tools/BashTool/bashPermissions.ts:1795-1806）。

tree-sitter 不可用时回退到 legacy 路径，核心是 `bashCommandIsSafe_DEPRECATED`（src/tools/BashTool/bashSecurity.ts:2257）。这个 2592 行的文件是一份"解析器差异攻击"编目：每一项检查都对应一种"我们的解析器看到的"与"bash 实际执行的"不一致的方式。检查项以数字 ID 登记，共 23 项（src/tools/BashTool/bashSecurity.ts:77-101），包括 IFS 注入、`/proc/*/environ` 访问、Unicode 空白、反斜杠转义操作符、花括号展开、zsh 专属危险内建等。例如 `COMMAND_SUBSTITUTION_PATTERNS` 不仅封 `$()` 和 `${}` 展开，还封 zsh 的 `=cmd` 等号展开，因为 `=curl evil.com` 会被 zsh 展开成 `/usr/bin/curl evil.com`，绕过 `Bash(curl:*)` 前缀规则（src/tools/BashTool/bashSecurity.ts:20-27）。

验证器的执行顺序也有讲究。`validateCarriageReturn` 被明确标记为 misparsing 类问题而 LF 换行不是：shell-quote 的 `[^\s]` 把 CR 当词分隔符，bash 的 IFS 却不含 CR，`splitCommand` 会把 CR 折叠成空格造成错切（src/tools/BashTool/bashSecurity.ts:2339-2346）。返回 `ask` 的验证器分两类：misparsing 类会设置 `isBashSecurityCheckForMisparsing` 标志并被权限层提前拦截；非 misparsing 类（LF、重定向）走普通审批流。为了不短路，非 misparsing 的 ask 会被"延迟"，继续跑完所有 misparsing 验证器再决定（src/tools/BashTool/bashSecurity.ts:2380-2407）。注释里给了具体攻击串：`cat safe.txt \; echo /etc/passwd > ./out`，如果 `validateRedirections` 先短路，`\;` 就漏检了。

## 策略防线：规则匹配

规则匹配的核心是 `filterRulesByContentsMatchingInput`（src/tools/BashTool/bashPermissions.ts:778）。规则分 exact / prefix / wildcard 三种（src/tools/BashTool/bashPermissions.ts:364），匹配前对命令做一系列归一化：先剥离输出重定向，让 `Bash(python:*)` 能匹配 `python script.py > out.txt`（src/tools/BashTool/bashPermissions.ts:789-793）；再剥离 `timeout`、`nice`、`nohup` 等"安全包装命令"和前缀环境变量，让 `Bash(npm install:*)` 能匹配 `timeout 10 npm install foo`（src/tools/BashTool/bashPermissions.ts:803-809）。

对 deny/ask 规则，剥离更激进：迭代地对候选命令做 `stripAllLeadingEnvVars` 和 `stripSafeWrappers` 直到不动点，处理 `nohup FOO=bar timeout 5 claude` 这种多层交错（src/tools/BashTool/bashPermissions.ts:826-853）。allow 规则有意不这么做，注释引用了 HackerOne #3543050，allow 规则只能剥离安全白名单内的环境变量，否则 `LD_PRELOAD=evil allowed_cmd` 会被放行。同一函数里还有两条防绕过：prefix/wildcard 规则不允许匹配复合命令，因为 `cd src\&\& python3 evil.py` 经转义后可能被错切成单条以 `cd ` 开头的"命令"（src/tools/BashTool/bashPermissions.ts:884-893）；prefix 匹配强制词边界，防止 `ls:*` 匹配到 `lsof`（src/tools/BashTool/bashPermissions.ts:894-901）。

规则之后是分类器。deny 和 ask 的自然语言规则用 Haiku 并行分类，deny 优先（src/tools/BashTool/bashPermissions.ts:1876-1932）。allow 方向有一个"推测性分类器"设计：`startSpeculativeClassifierCheck` 在 pre-tool hooks 和权限弹窗准备阶段就提前发起 allow 分类请求，结果暂存在 `speculativeChecks` Map 里（src/tools/BashTool/bashPermissions.ts:1497-1527）；弹窗展示期间 `executeAsyncClassifierCheck` 消费这个结果，若分类器高置信放行且用户尚未与弹窗交互，就自动批准（src/tools/BashTool/bashPermissions.ts:1605-1657）。这把一次网络调用的延迟藏进了用户看弹窗的时间里。所有需要用户决策的 `ask` 分支都会附挂 `pendingClassifierCheck`（如 src/tools/BashTool/bashPermissions.ts:1760-1767），形成统一的"弹窗 + 后台分类器竞速"模式。

## 策略防线：只读推断

只读命令自动放行由 `checkReadOnlyConstraints` 完成（src/tools/BashTool/readOnlyValidation.ts:1876），它被 `BashTool.isReadOnly` 调用，同时决定 `isConcurrencySafe`：只读命令可以并行执行（src/tools/BashTool/BashTool.tsx:434-441）。

判定分两步。第一步整体安检：命令必须能解析、通过 `bashCommandIsSafe_DEPRECATED`、不含易受 WebDAV 攻击的 Windows UNC 路径（src/tools/BashTool/readOnlyValidation.ts:1883-1909）。随后是三条 git 相关守卫：复合命令同时含 cd 和 git 不放行（防 `cd /malicious/dir && git status` 触发恶意仓库的 core.fsmonitor/hooks）；当前目录呈 bare 仓库结构时 git 命令不放行；复合命令写 git 内部路径（HEAD、objects/、refs/、hooks/）再跑 git 不放行（src/tools/BashTool/readOnlyValidation.ts:1914-1949）。第二步逐子命令判定：`splitCommand_DEPRECATED` 切开后每条都要过 `isCommandReadOnly`（src/tools/BashTool/readOnlyValidation.ts:1969-1976）。

单条命令的只读判定是"白名单 + flag 解析"，而不是正则黑名单。`COMMAND_ALLOWLIST`（src/tools/BashTool/readOnlyValidation.ts:128）为每个命令声明 `safeFlags` 表、可选 regex、可选危险回调。`isCommandSafeViaFlagParsing` 先拒绝带操作符的命令，再按多词模式（`git diff`、`git stash list`）匹配配置，然后做三件事（src/tools/BashTool/readOnlyValidation.ts:1246-1408）：

- 拒绝任何含 `$` 的 token。shell-quote 解析时 `$VAR` 被保留为字面量，但 bash 运行时会展开（未设置则展开为空），造成解析器差异：`git diff "$Z--output=/tmp/pwned"` 在校验器眼里是位置参数，在 bash 眼里是 `--output=` 任意文件写（src/tools/BashTool/readOnlyValidation.ts:1328-1357）；
- 拒绝同时含 `{` 与 `,`/`..` 的 token（花括号展开混淆）（src/tools/BashTool/readOnlyValidation.ts:1358-1368）；
- 逐 flag 对照白名单校验，再跑命令专属 regex 和危险回调（src/tools/BashTool/readOnlyValidation.ts:1371-1405）。

白名单的注释本身就是攻击史。`fd` 的 `-x/--exec` 被刻意排除，因为会对每个搜索结果执行任意命令；`-l/--list-details` 也被排除，因为它内部 fork `ls` 子进程，存在 PATH 劫持风险（src/tools/BashTool/readOnlyValidation.ts:52-55, 77-79）。`xargs` 的 `-i` 和 `-e` 被移除：GNU getopt 的可选附着参数语义下，`xargs -e EOF echo foo` 中 `EOF` 实际是目标命令名而非 `-e` 的参数，校验器与 xargs 对参数消耗的理解不一致可直接导致代码执行（src/tools/BashTool/readOnlyValidation.ts:132-150）。`containsUnquotedExpansion` 则处理 glob 与 `$` 的字面扫描，并修正了单引号内反斜杠的转义处理：bash 中 `'\'` 是字面反斜杠，若按可转义处理会让引号状态机失步，`ls '\' *` 中的 glob 就检测不到（src/tools/BashTool/readOnlyValidation.ts:1615-1629）。

整个权限函数有一条贯穿始终的原则：deny 不可被降级为 ask。`too-complex` 分支先跑 `checkEarlyExitDeny` 再 ask（src/tools/BashTool/bashPermissions.ts:1741-1747）；`checkSemantics` 不过时先跑 `checkSemanticsDeny`，注释明确说"有 `Bash(eval:*)` deny 的用户期望 `eval "rm"` 被 block，而不是降级成 ask"（src/tools/BashTool/bashPermissions.ts:1774-1783）；`checkSandboxAutoAllow` 里复合命令的子命令 deny 检查必须跑在全命令 ask 返回之前，否则一条匹配全命令的通配 ask 规则会把子命令上的 prefix deny 降级（src/tools/BashTool/bashPermissions.ts:1295-1336）；子命令决策聚合时先找 deny 再找 ask（src/tools/BashTool/bashPermissions.ts:2248-2266）。规则匹配层面同样如此：deny/ask 规则必须能匹配复合命令，防止把被拒命令包进复合表达式绕过（src/tools/BashTool/bashPermissions.ts:858-860）。这条原则保证了三层防线的单调性：任何一层升级严格的判断都不会被后续层放松。

## 运行时防线：路径约束与沙箱

`checkPathConstraints`（src/tools/BashTool/pathValidation.ts:1013）在规则检查之后对原始命令复核：进程替换 `>(cmd)` 直接 ask，因为 `echo secret > >(tee .git/config)` 的写入目标不出现在重定向里（src/tools/BashTool/pathValidation.ts:1021-1038）；有 AST 数据时直接用 AST 的重定向和 argv，绕开 shell-quote 的单引号反斜杠 bug（src/tools/BashTool/pathValidation.ts:1040-1048, 1072-1088）。权限层里还有一处修复痕迹：管道各段被 allow 后仍须对原始命令跑路径检查，因为分段处理会剥掉重定向，`echo 'x' | xargs printf '%s' >> /tmp/file` 的 `>>` 会漏检（src/tools/BashTool/bashPermissions.ts:1984-2055）。

沙箱决策在 `shouldUseSandbox`（src/tools/BashTool/shouldUseSandbox.ts:130）：沙箱未启用、模型传了 `dangerouslyDisableSandbox` 且策略允许、或命令命中排除清单时不用沙箱。排除清单的匹配也做不动点剥离，但文件顶部明确声明：`excludedCommands` 是便利特性而非安全边界，真正的安全控制是"会弹窗的沙箱权限系统"（src/tools/BashTool/shouldUseSandbox.ts:18-20）。当沙箱启用且开启 `autoAllowBashIfSandboxed` 时，权限层会在规则检查前先走 `checkSandboxAutoAllow`：无显式 deny/ask 规则的命令直接在沙箱内放行，弹窗这一步被沙箱隔离替代（src/tools/BashTool/bashPermissions.ts:1270-1359, 1829-1843）。这就是"护栏在工具层"的典型权衡：把信任从"逐条审批模型行为"转移到"限制执行环境的爆炸半径"。

执行侧的沙箱接线只有一处：`runShellCommand` 调 `exec` 时把 `shouldUseSandbox(input)` 作为选项传入（src/tools/BashTool/BashTool.tsx:881-898），权限层的所有判断在此之前已完成。模型可以主动传 `dangerouslyDisableSandbox: true`，该参数写在公开 schema 里（src/tools/BashTool/BashTool.tsx:242），但是否生效取决于 `SandboxManager.areUnsandboxedCommandsAllowed()` 的策略位（src/tools/BashTool/shouldUseSandbox.ts:135-141），且每次绕过都会体现在输出结果的 `dangerouslyDisableSandbox` 标志上并触发审批（src/tools/BashTool/BashTool.tsx:813）。沙箱违规不会被静默吞掉：执行结束后 `SandboxManager.annotateStderrWithSandboxFailures` 会把违规信息写进输出，模型在后续轮次能读到失败原因（src/tools/BashTool/BashTool.tsx:709-710）。

## sed 特例：被当成编辑操作

`sed -i 's/a/b/' file` 语义上是文件编辑，不是 shell 执行。Claude Code 为此单独建了一条通道。`parseSedEditCommand` 用 shell-quote 把命令切词后做严格解析：必须含 `-i`、恰好一个表达式、恰好一个文件、表达式必须是 `/` 分隔的 `s/pattern/replacement/flags`、flags 只允许 `[gpimIM1-9]`；遇到 glob、未知 flag、多文件、多表达式一律返回 null 回退普通 bash 流程（src/tools/BashTool/sedEditParser.ts:49-238）。解析成功后，工具的用户可见名称直接渲染成 FileEdit 工具的名字（src/tools/BashTool/BashTool.tsx:489-496），权限弹窗走 SedEditPermissionRequest 的 diff 预览。

这条通道的做法是"预览即执行"：用户批准的是预览里的新文件内容，不是 sed 命令本身。批准后写入 `_simulatedSedEdit` 字段，`BashTool.call` 检测到该字段就走 `applySedEdit` 直接写文件，根本不执行 sed（src/tools/BashTool/BashTool.tsx:360-419, 627-629）。`_simulatedSedEdit` 被刻意从模型可见的 input schema 中剔除，否则模型可以用一条无害命令配上任意文件写来绕过权限与沙箱（src/tools/BashTool/BashTool.tsx:249-259）。替换本身在 JS 侧完成：`applySedSubstitution` 处理 BRE→ERE 转义方向反转（BRE 里 `\+` 是量词、`+` 是字面量），并用随机盐占位符防止替换串里 `&` 的注入（src/tools/BashTool/sedEditParser.ts:244-322）。配套的 `sedValidation.ts` 负责只读 sed（打印、不加 `-i` 的替换）的放行，`containsDangerousOperations` 按"保守拒绝"原则封掉非 ASCII、花括号块、取反地址、GNU 步进地址、替代分隔符等一切复杂形态（src/tools/BashTool/sedValidation.ts:473-540）。

## PowerShellTool：Windows 镜像

PowerShellTool 是同构的一套防线，但威胁模型按 PowerShell 语义重写。Bash 侧 acceptEdits 模式只按基命令名白名单放行 `mkdir/touch/rm/mv/cp/sed`（src/tools/BashTool/modeValidation.ts:7-15）；PowerShell 侧的 `checkPermissionMode` 要复杂得多：先用 AST 的 `deriveSecurityFlags` 拒绝含子表达式、脚本块、成员调用、splatting、赋值、可展开字符串的命令（src/tools/PowerShellTool/modeValidation.ts:163-180），再逐段检查：别名先归一到 canonical cmdlet（`rm`→`remove-item`），路径形态的命令名（`scripts\Remove-Item`）拒绝，参数元素类型必须是 StringConstant/Parameter（否则 `Remove-Item $env:PATH` 这种变量路径会在运行时才展开），冒号绑定参数里含 `$()@{[` 的拒绝（src/tools/PowerShellTool/modeValidation.ts:269-318）。

Bash 的 cd 守卫在 PowerShell 侧有对应物且更进一步：复合语句含 `Set-Location` 与写 cmdlet 组合时不自动放行（路径校验用的是过期 cwd）；此外还检测 `New-Item -ItemType SymbolicLink/Junction/HardLink`：刚创建的链接会让后续相对路径在运行时解析到校验器视野之外，构成 TOCTOU。该检测要处理 PowerShell 参数缩写（`-it`、`-ty`）、Unicode 破折号前缀、反引号转义（`-Item\`Type`）、冒号绑定值（`-it:Junction`）（src/tools/PowerShellTool/modeValidation.ts:56-117, 218-241）。`powershellSecurity.ts` 则对应 bashSecurity 的注入检测，覆盖 `Invoke-Expression`、编码命令（`-enc`）、download cradle（IWR 管道接 IEX、`Start-BitsTransfer`）、`Add-Type`、COM 对象与 `New-Object System.Net.WebClient` 类型实例化等 PowerShell 专属攻击面（src/tools/PowerShellTool/powershellSecurity.ts:106-451）。

## 写给模型看的 prompt

工具描述是护栏的最后一层：让模型一开始就少生成会被拦的命令。`getSimplePrompt`（src/tools/BashTool/prompt.ts:275-369）做了几件事：把模型从 `find/grep/cat/sed/echo` 引导向专用工具（Glob/Grep/Read/Edit/Write），理由写得很直白：专用工具"provide a better user experience and make it easier to review tool calls and give permission"（src/tools/BashTool/prompt.ts:359-362）；给出复合命令约定（独立命令并行调用、依赖命令用 `&&`、不要用换行分隔）（src/tools/BashTool/prompt.ts:297-302）；把 git 安全协议（不 amend、不跳 hooks、不用 `-i` 交互式命令）和 commit/PR 的完整操作脚本内联进来（src/tools/BashTool/prompt.ts:81-160）。沙箱启用时，prompt 会把读写白名单、网络限制序列化进 `## Command sandbox` 一节，并明确告诉模型何时可以用 `dangerouslyDisableSandbox` 重试、以及"Do not suggest adding sensitive paths like ~/.ssh/* to the sandbox allowlist"（src/tools/BashTool/prompt.ts:228-261）。这里还有性能考量：沙箱配置先 dedup 再把 per-UID 临时目录归一成 `$TMPDIR`，保持跨用户的 prompt 缓存命中（src/tools/BashTool/prompt.ts:163-190）。PowerShellTool 的 prompt 则多了一个版本适配段：检测到 5.1 就告诉模型不要用 `&&`/三元/`??`，检测到 pwsh 7 则相反，因为模型训练数据同时覆盖两个版本却无法分辨目标（src/tools/PowerShellTool/prompt.ts:51-71）。

模型可见 schema 与内部 schema 分离也是护栏的一部分：`_simulatedSedEdit` 不出现在模型可见 schema 中（src/tools/BashTool/BashTool.tsx:254-259），`description` 字段的规范（主动语态、5-10 词）直接写在 schema 的 describe 里（src/tools/BashTool/BashTool.tsx:230-240）。

三层防线的组合逻辑是：解析防线保证"看到的即执行的"，策略防线在规则、分类器、只读推断之间取最快的放行路径，运行时防线保证即使前两层的判断出错，爆炸半径也被沙箱和路径约束限制住。这些护栏全部实现在工具代码里，而不是系统提示词里，这是 Bash 工具 1.2 万行代码背后的主要工程决策。代价也在这里：每出现一种新的解析器差异或绕过手法，都要在这些文件里登记一项对应的检查，bashSecurity.ts 的 23 项编号检测就是这样积累下来的。

## 本篇涉及的源码文件

- `src/tools/BashTool/BashTool.tsx`：工具定义、执行主流程、sandbox/后台化接线、`_simulatedSedEdit` 通道
- `src/tools/BashTool/bashPermissions.ts`：权限决策总线：AST 门控、规则匹配、分类器、子命令拆分
- `src/tools/BashTool/bashSecurity.ts`：23 项注入/解析器差异检测（legacy 正则防线）
- `src/tools/BashTool/readOnlyValidation.ts`：白名单 + flag 解析的只读命令推断
- `src/tools/BashTool/pathValidation.ts`：重定向与写路径约束
- `src/tools/BashTool/shouldUseSandbox.ts`：沙箱启用决策与排除清单
- `src/tools/BashTool/modeValidation.ts`：acceptEdits 模式的文件系统命令放行
- `src/tools/BashTool/sedEditParser.ts`：sed -i 命令解析与 JS 侧替换执行
- `src/tools/BashTool/sedValidation.ts`：只读 sed 的保守白名单校验
- `src/tools/BashTool/prompt.ts`：模型可见的工具描述与 git/沙箱行为约定
- `src/tools/PowerShellTool/modeValidation.ts`：PowerShell 侧 acceptEdits 校验与链接/cd TOCTOU 守卫
- `src/tools/PowerShellTool/powershellSecurity.ts`：PowerShell 专属攻击面检测（IEX、download cradle 等）
- `src/tools/PowerShellTool/prompt.ts`：PowerShell 工具描述与 5.1/7 版本语法适配
