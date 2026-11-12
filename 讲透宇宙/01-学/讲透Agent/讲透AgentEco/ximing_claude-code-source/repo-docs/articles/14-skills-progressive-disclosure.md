---
title: Claude Code 源码拆解 14：Skills 渐进式披露的实现
date: "2026-04-11 14:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 14/20 篇 · 对应主题：能力按需加载

# Skills 的定位：把能力做成可分页的资源

Claude Code 的 skill 不是工具（Tool），而是一段按需注入的 prompt。一个会话可能挂着几十上百个 skill，如果每个 skill 的全文都进系统提示，上下文预算立刻耗尽。Claude Code 的解法是渐进式披露（progressive disclosure）：平时只把"名称 + 一句话描述"注入上下文（每个约几十 token）；模型决定调用某个 skill 时，才把 SKILL.md 全文作为工具结果展开；skill 目录里的附带文件（脚本、示例、参考文档）则永远不进 prompt，只在 SKILL.md 里告诉模型"Base directory 在哪，自己去 Read"。

这三层分别对应三个代码位置：清单注入在 `src/tools/SkillTool/prompt.ts`，全文展开在 `createSkillCommand` 的 `getPromptForCommand`（src/skills/loadSkillsDir.ts:344），附带文件机制在 `src/skills/bundledSkills.ts` 的 `files` 字段与 `skillRoot` 目录。

## 发现与解析：loadSkillsDir

`loadSkillsDir.ts`（1086 行）负责从磁盘发现 skill。新格式只支持目录形态：`skill-name/SKILL.md`，单个 `.md` 文件在 `/skills/` 目录下被直接跳过（src/skills/loadSkillsDir.ts:424-428）。加载入口 `getSkillDirCommands` 被 `memoize` 包裹，并行扫五个来源：managed（企业策略）、user（`~/.claude/skills`）、project（从 cwd 向上到 home 的各级 `.claude/skills`）、`--add-dir` 附加目录、以及 legacy `/commands/` 目录（src/skills/loadSkillsDir.ts:679-714）。

同一文件可能经符号链接或重叠目录被扫到两次，去重不靠路径字符串比较，而是用 `realpath` 解析出规范路径作为文件身份。注释里明确说这是为了规避某些虚拟文件系统上报不可靠 inode 的问题（src/skills/loadSkillsDir.ts:107-124）。去重是 first-wins：排在前面的 managed 优先于 project。

每个 SKILL.md 经 `parseFrontmatter` 拆出 YAML frontmatter，再由 `parseSkillFrontmatterFields` 统一解析字段：`description`、`when_to_use`、`allowed-tools`、`model`、`user-invocable`、`context: fork`、`agent`、`hooks`、`effort` 等（src/skills/loadSkillsDir.ts:185-265）。这个函数同时被磁盘加载和 MCP skill 加载复用，保证两种来源的 frontmatter 语义一致。几个默认值值得记下：`user-invocable` 缺省为 true，置 false 会让 `isHidden` 变 true，此时 skill 从斜杠菜单消失但仍可被模型调用（src/skills/loadSkillsDir.ts:216-219、335）；`model: inherit` 被显式映射为 undefined，即跟随会话当前模型（src/skills/loadSkillsDir.ts:221-226）；description 缺失时回退到从 markdown 正文提取（src/skills/loadSkillsDir.ts:208-214）。

legacy `/commands/` 目录走另一条路径：允许单文件 `.md`，命名支持子目录命名空间：`buildNamespace` 把相对路径的目录层级用冒号拼成 `review:pr` 这样的限定名，而目录形态的 SKILL.md 一律继承父目录名（src/skills/loadSkillsDir.ts:523-559）。同目录下既有 SKILL.md 又有其他 md 时，`transformSkillFiles` 只保留 SKILL.md（src/skills/loadSkillsDir.ts:493-521）。`--bare` 模式则砍掉全部自动发现，只加载 `--add-dir` 显式给出的目录（src/skills/loadSkillsDir.ts:654-675）。

effort 门控在这里只是解析与校验：

```typescript
const effortRaw = frontmatter['effort']
const effort =
  effortRaw !== undefined ? parseEffortValue(effortRaw) : undefined
if (effortRaw !== undefined && effort === undefined) {
  logForDebugging(
    `Skill ${resolvedName} has invalid effort '${effortRaw}'. Valid options: ${EFFORT_LEVELS.join(', ')} or an integer`,
  )
}
```
（src/skills/loadSkillsDir.ts:228-235）合法值为 `low/medium/high/max` 或整数（src/utils/effort.ts:13-17）。真正生效在执行时：SkillTool 的 `contextModifier` 用 `effortValue: effort` 覆盖 AppState（src/tools/SkillTool/SkillTool.ts:824-836），fork 模式则把 effort 合入子 agent 定义交给 `runAgent`（src/tools/SkillTool/SkillTool.ts:209-212）。所以 skill 作者声明"这个流程值得高 effort"后，加载期不会被拦，调用期才改写推理档位。

除了启动时扫描，还有两条动态通道。其一是 `discoverSkillDirsForPaths`：Read/Write/Edit 触到某个文件后，从该文件目录向上走到 cwd（不含 cwd），逐层探测 `.claude/skills` 是否存在；已探测过的路径记入 `dynamicSkillDirs` 避免重复 stat（注释说明这是为了避免每次文件操作都对不存在的目录重复失败 stat），且被 gitignore 的目录（如 `node_modules/pkg/.claude/skills`）会被 `git check-ignore` 跳过。注释同时交代了安全边界：git 仓库外 fail-open，真正的防线是调用时的信任确认（src/skills/loadSkillsDir.ts:861-915）。新发现的目录按深度排序、深者优先，加载后并入 `dynamicSkills` 并发出 `skillsLoaded` 信号（src/skills/loadSkillsDir.ts:911-975）。

其二是条件 skill：frontmatter 带 `paths` 的 skill 启动时不进清单。`parseSkillPaths` 复用 CLAUDE.md 规则的路径语法，剥掉 `/**` 后缀（ignore 库对裸路径本身就同时匹配路径与其内容），全部为 `**` 时按无条件处理（src/skills/loadSkillsDir.ts:159-178）。这些 skill 先挂在 `conditionalSkills` 里，等会话中碰到的文件路径被 gitignore 风格的 `ignore().ignores()` 命中，才移入 `dynamicSkills` 并触发 `skillsLoaded` 信号通知各缓存失效；已激活的名字记入 `activatedConditionalSkillNames`，会话内清缓存不会让它们退回潜伏态（src/skills/loadSkillsDir.ts:997-1058、826-829）。这是渐进式披露在"是否可见"维度上的延伸：不相关的 skill 连那几十 token 都不占。

## 第一层披露：清单注入与 1% 字符预算

SkillTool 自身的 prompt 是静态的（src/tools/SkillTool/prompt.ts:173-196），只说"可用 skill 在 system-reminder 里列出，匹配到就必须先调用本工具"。真正的清单通过 attachment 机制注入：`attachments.ts` 维护一个 `sentSkillNames` 集合，每轮把"还没发过的 skill"用 `formatCommandsWithinBudget` 格式化后包成 `skill_listing` attachment（src/utils/attachments.ts:2719-2748），渲染层再把它包成 system-reminder 形态的用户消息（src/utils/messages.ts:3728-3738）。已发送的不重复发；resume 时也会把存量标记为已发，只播报增量。

清单的 token 占用也进入了上下文统计：`analyzeContext` 按 `estimateSkillFrontmatterTokens` 逐个估算 skill 的 frontmatter 开销（src/utils/analyzeContext.ts:594），即"name + description + whenToUse"三个字段拼接后做粗略 token 估算（src/skills/loadSkillsDir.ts:100-105）。统计口径与注入口径一致：全文不计入，因为它此刻确实不在上下文里。

预算控制的核心常量在 prompt.ts 顶部：

```typescript
// Skill listing gets 1% of the context window (in characters)
export const SKILL_BUDGET_CONTEXT_PERCENT = 0.01
export const CHARS_PER_TOKEN = 4
export const DEFAULT_CHAR_BUDGET = 8_000 // Fallback: 1% of 200k × 4

export const MAX_LISTING_DESC_CHARS = 250
```
（src/tools/SkillTool/prompt.ts:20-29）清单总量被压到上下文窗口的 1%（按 4 字符 ≈ 1 token 折算），单条描述硬上限 250 字符。注释解释了为什么砍得这么狠：清单只服务于发现，全文在调用时才加载，冗长的 `whenToUse` 只会白白消耗首轮 cache_creation token。

超预算时 `formatCommandsWithinBudget` 逐级降级：先试全量描述；放不下就把 bundled skill 划出来保留全文（它们被 `source === 'bundled'` 判定、永不截断），其余 skill 平分剩余预算；平分后单条不足 20 字符的极端情况下，非 bundled skill 退化为只列名字（src/tools/SkillTool/prompt.ts:88-142）。清单里每条的内容是 `description + " - " + whenToUse`（src/tools/SkillTool/prompt.ts:43-46）。这两个字段是唯一常驻上下文的 skill 文本，`estimateSkillFrontmatterTokens` 也只按 name/description/whenToUse 估算占用（src/skills/loadSkillsDir.ts:100-105），注释写明"full content is only loaded on invocation"。

## 第二层披露：调用时展开 SKILL.md 全文

模型调用 `Skill(skill: "commit", args: "...")` 后，SkillTool 的 `call` 走两条路。`context: 'fork'` 的 skill 进入 `executeForkedSkill`，把 skill prompt 作为独立子 agent 的初始消息运行，有自己的 token 预算（src/tools/SkillTool/SkillTool.ts:122-289）；默认 inline 路径则走 `processPromptSlashCommand`，展开成新消息插回主循环，并通过 `contextModifier` 把 `allowed-tools` 并入 alwaysAllowRules、应用 model 覆盖（保留 `[1m]` 后缀以免掉上下文窗口）和 effort 覆盖（src/tools/SkillTool/SkillTool.ts:766-840）。

展开动作在 `getPromptForCommand` 里完成：

```typescript
async getPromptForCommand(args, toolUseContext) {
  let finalContent = baseDir
    ? `Base directory for this skill: ${baseDir}\n\n${markdownContent}`
    : markdownContent

  finalContent = substituteArguments(finalContent, args, true, argumentNames)

  if (baseDir) {
    const skillDir =
      process.platform === 'win32' ? baseDir.replace(/\\/g, '/') : baseDir
    finalContent = finalContent.replace(/\$\{CLAUDE_SKILL_DIR\}/g, skillDir)
  }

  finalContent = finalContent.replace(
    /\$\{CLAUDE_SESSION_ID\}/g,
    getSessionId(),
  )
```
（src/skills/loadSkillsDir.ts:344-369）注入点有三个：顶部一行 Base directory 宣告（第三层披露的入口）、`$ARGUMENTS`/命名参数替换、以及 `${CLAUDE_SKILL_DIR}` 和 `${CLAUDE_SESSION_ID}` 两个宏。随后 SKILL.md 里的 `` !`...` `` 内联 shell 会被 `executeShellCommandsInPrompt` 实际执行，但对 MCP 来源的 skill 显式禁用（`loadedFrom !== 'mcp'`，src/skills/loadSkillsDir.ts:371-396），因为远程内容不可信。

调用前的校验和权限各自独立成层。`validateInput` 做四件事：去首尾空白与前导斜杠（带斜杠会记一条 `tengu_skill_tool_slash_prefix` 遥测）、查命令是否存在、拒绝 `disable-model-invocation` 的 skill、拒绝非 prompt 型命令（src/tools/SkillTool/SkillTool.ts:354-430）。`checkPermissions` 先查 deny 规则（支持 `review:*` 前缀通配），再查 allow 规则，然后是一条自动放行规则：`skillHasOnlySafeProperties` 用一个 allowlist 检查 skill 是否只含安全属性，未来新增的 frontmatter 字段默认落入需要询问的一档（src/tools/SkillTool/SkillTool.ts:525-538）；都不命中则 ask，并附带两条规则建议（精确名与 `name:*` 前缀）写入 localSettings（src/tools/SkillTool/SkillTool.ts:542-577）。

SkillTool 拿到展开后的 prompt 并不替模型"执行"它，而是返回 `newMessages` 让主循环把这些消息作为后续上下文继续推理，skill 的"执行"因此就是一次受控的 prompt 注入。这些新消息被 `tagMessagesWithToolUseID` 打上来源标签，在工具结果返回前保持 transient，command-message 展示消息则被过滤掉避免重复渲染（src/tools/SkillTool/SkillTool.ts:734-755）。工具描述里那句 BLOCKING REQUIREMENT（src/tools/SkillTool/prompt.ts:190）和"看到 `<command-name>` 标签就说明 skill 已加载、直接照做、不要重复调用"（src/tools/SkillTool/prompt.ts:194）共同构成了这个协议的两端。fork 路径的输出 schema 与 inline 分开定义：fork 返回 `status: 'forked'`、agentId 和子 agent 的结论文本，inline 返回 allowedTools 与 model 覆盖（src/tools/SkillTool/SkillTool.ts:301-326）。

## 第三层披露：附带文件按需读取

SKILL.md 全文也可能很长，所以更重的材料不进 markdown 正文，而是作为文件留在 skill 目录里，模型按 Base directory 提示自行 Read/Grep。磁盘 skill 天然如此；bundled skill 编译进二进制，需要把内嵌的 `files` 先落盘。`registerBundledSkill` 检测到 `files` 非空时包一层 `getPromptForCommand`：首次调用时把文件解到 `getBundledSkillsRoot()/<name>` 下（按 promise memoize，并发调用共享同一次解包），再在返回内容前 prepend Base directory 行（src/skills/bundledSkills.ts:59-73）。

落盘做了三层防护：解包根目录带 per-process nonce；写入用 `O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW` 加 0o600/0o700 权限；相对路径经 `resolveSkillFilePath` 归一化并拒绝 `..` 逃逸（src/skills/bundledSkills.ts:169-206）。注释说明这是防"预先种好的符号链接"攻击，且不 unlink 重试因为 unlink 本身也会跟随中间符号链接。

`verify` skill 是这套机制的标准用例：`SKILL_FILES` 在构建期由 Bun 的 text loader 把 `verify/examples/cli.md`、`server.md` 内联为字符串，运行时才解包（src/skills/bundled/verifyContent.ts:1-13）。清单层、正文层、文件层的 token 成本逐层递增，触及概率逐层递减。

## 内置 skills 实例

`initBundledSkills` 在启动时注册全部内置 skill（src/skills/bundled/index.ts:24-79），其中一部分受 feature flag 门控（`loop` 挂 `AGENT_TRIGGERS`，`claudeApi` 挂 `BUILDING_CLAUDE_APPS`，`dream` 挂 `KAIROS`），`verify` 则只在 `USER_TYPE === 'ant'` 时注册（src/skills/bundled/verify.ts:13-15）。除下面细看的五个外，注册表里还有 keybindings（改键位）、debug、remember、batch、stuck 等，形态一致：一段常驻描述加一份调用时才展开的操作手册。bundled skill 与用户 skill 走同一 `Command` 抽象、同一清单、同一 SkillTool 入口，区别只在 `source: 'bundled'`，以及前文提到的清单降级时永不截断的特权。

- `skillify`（src/skills/bundled/skillify.ts）：把当前会话变成可复用 skill 的元 skill。它的 prompt 注入两段会话证据：session memory 摘要和全部用户消息（`{{sessionMemory}}`、`{{userMessages}}`，src/skills/bundled/skillify.ts:26-36），然后指导模型做四步：分析会话中的可重复流程、用 AskUserQuestion 分轮访谈（命名/目标/参数/inline 还是 fork/存 repo 还是存 user）、按固定模板写出 SKILL.md、确认触发语。这套机制在这里用到了自己身上：会话中重复出现的流程被压缩回一个几十 token 的清单条目。
- `update-config`（src/skills/bundled/updateConfig.ts:446-473）：settings.json 配置向导。描述接近 700 字符，远超 250 的清单上限，注入时按上限截断。描述枚举了"from now on when X"类自动化必须走 hooks、权限、环境变量等触发场景。`allowedTools: ['Read']`，运行时动态生成 settings 的 JSON Schema 拼进 prompt，保证文档与类型同步。
- `loop`（src/skills/bundled/loop.ts:74-92）：把自然语言周期任务解析成 cron 表达式并调 CronCreate。prompt 主体是一张 interval→cron 的换算表和"调度后立即先跑一次"的行为约定。`whenToUse` 里明确写了反例"Do NOT invoke for one-off tasks"。
- `verify`：验证代码改动真的生效，做法是跑应用、点界面。内容层用 `files` 带示例文件，是第三层披露的样板。
- `simplify`（src/skills/bundled/simplify.ts:55-69）：对 `git diff` 并行起三个 review 子 agent（复用、质量、效率各一），汇总后直接修复。它的 SKILL 正文本身就是一份多 agent 编排脚本。

## MCP skills：mcpSkillBuilders 与 MCP_SKILLS

MCP server 声明的 skill 也走同一套 Command 抽象。`client.ts` 在 `feature('MCP_SKILLS')` 门控下 `require('../../skills/mcpSkills.js')`，连接时与 tools/prompts 并行拉取 `fetchMcpSkillsForClient(client)`，合并进 `commands`（src/services/mcp/client.ts:117-122、2171-2179）。

这里的依赖图有一个循环问题：mcpSkills 需要 `createSkillCommand` 和 `parseSkillFrontmatterFields`，但 loadSkillsDir 传递依赖几乎整个代码库，直接 import 会构成 `client.ts → mcpSkills.ts → loadSkillsDir.ts → … → client.ts` 循环；字面量的动态 import 能被 dep-cruiser 抓到，变量形式的动态 import 在 Bun 打包产物里又解析不到模块。解法是 `mcpSkillBuilders.ts` 这个只 import 类型的叶子模块：loadSkillsDir 在模块初始化时把两个函数写进注册表（src/skills/loadSkillsDir.ts:1083-1086），mcpSkills 运行时经 `getMCPSkillBuilders()` 取出（src/skills/mcpSkillBuilders.ts:37-44）。注释把三种方案为什么两条不可行写得很清楚（src/skills/mcpSkillBuilders.ts:6-24）。

MCP skill 进入 SkillTool 时有额外的信任边界：`getAllCommands` 只收 `loadedFrom === 'mcp'` 的 prompt 型命令，把普通 MCP prompt 挡在外面；注释说明此前模型可以靠猜 `mcp__server__prompt` 名字调到本不该可达的 prompt（src/tools/SkillTool/SkillTool.ts:81-94）；展开时又跳过内联 shell 执行（前述 loadSkillsDir.ts:371-374）。远程 skill 与本地 skill 共享披露协议，但被剥掉了代码执行面。

## 描述写作与加载时机的关联

三层披露结构直接决定了 skill 描述的写法约束，源码里能看到这些约束被当作契约执行：

1. description + when_to_use 是唯一常驻文本。它们决定模型会不会选中这个 skill，且合计被 250 字符截断（prompt.ts:29、43-50）。所以内置 skill 的描述都写成"触发条件枚举"：update-config 把用户可能说的原话（"allow X"、"move permission to"、"set X=Y"）直接列进描述；loop 的 `whenToUse` 给出正例（"check the deploy every 5 minutes"）和反例（one-off 任务不要调）。
2. 清单只负责发现，不负责教学。prompt.ts 的注释明说详细 `whenToUse` 不提升命中率、只浪费 cache_creation（src/tools/SkillTool/prompt.ts:25-28），所以操作细节应该放 SKILL.md 正文，那是第二层，调用时才付费。
3. 正文可以引用文件，不该内联文件。Base directory 约定（loadSkillsDir.ts:345-347）让模型自己去读附带材料，verify 的 examples 就是按这个契约组织的。

反过来说，这个结构也解释了加载时机的设计：frontmatter 在启动时全量解析（便宜），全文和附带文件延迟到调用（贵但按需），条件 skill 和动态发现把"进入清单"本身也推迟到路径命中（loadSkillsDir.ts:997-1058）。每一层都把成本推到确定需要之后：清单常驻开销只有几十 token，全文和附带文件只在调用时才产生开销。

## 本篇涉及的源码文件

- `src/skills/loadSkillsDir.ts`：skill 目录发现、frontmatter 解析、去重、条件/动态 skill、MCP builders 注册
- `src/skills/bundledSkills.ts`：bundled skill 注册表与附带文件的安全解包
- `src/skills/mcpSkillBuilders.ts`：打破 import 循环的 write-once 函数注册表
- `src/tools/SkillTool/SkillTool.ts`：skill 调用入口：校验、权限、inline/fork 两种执行路径、contextModifier
- `src/tools/SkillTool/prompt.ts`：SkillTool 静态 prompt 与清单的 1% 预算格式化
- `src/skills/bundled/index.ts`：内置 skill 的统一注册与 feature flag 门控
- `src/skills/bundled/skillify.ts`：把会话变成可复用 skill 的元 skill
- `src/skills/bundled/updateConfig.ts`：settings.json 配置向导 skill
- `src/skills/bundled/loop.ts`：自然语言周期任务转 cron 的 skill
- `src/skills/bundled/verify.ts` / `verifyContent.ts`：使用 `files` 附带文件的样板 skill
- `src/skills/bundled/simplify.ts`：三 agent 并行 review 的编排型 skill
- `src/utils/attachments.ts`：skill 清单的增量注入（sentSkillNames）
- `src/utils/messages.ts`：`skill_listing` attachment 渲染为 system-reminder
- `src/utils/effort.ts`：effort 档位定义与解析
- `src/services/mcp/client.ts`：MCP_SKILLS 门控下的 MCP skill 拉取
