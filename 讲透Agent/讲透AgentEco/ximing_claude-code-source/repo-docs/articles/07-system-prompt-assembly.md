---
title: Claude Code 源码拆解 07：系统提示词装配流水线
date: "2026-04-05 14:30"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 07/20 篇 · 对应主题：提示工程整理术

# 系统提示词装配流水线

Claude Code 每次请求 API 时发出的 system prompt 不是一段静态文本，而是一条多级装配流水线的产物：先由 `getSystemPrompt` 生成默认提示词数组，再经 `buildEffectiveSystemPrompt` 按优先级挑选或替换，然后拼上 git status、CLAUDE.md 等上下文，最后在发送前切成若干 cache block。这条流水线的每一环都围绕同一个约束设计：Anthropic API 的 prompt cache 按前缀匹配，任何变动都会使缓存失效，因此装配顺序必须把稳定内容放在前面、易变内容放在后面。

## 五级优先级链：buildEffectiveSystemPrompt

`buildEffectiveSystemPrompt`（src/utils/systemPrompt.ts:41）是整条流水线的调度器，其 JSDoc 明确列出优先级（src/utils/systemPrompt.ts:28-40）：override > coordinator > agent > `--system-prompt` > default，外加一个始终追加的 `appendSystemPrompt`。

```typescript
if (overrideSystemPrompt) {
  return asSystemPrompt([overrideSystemPrompt])
}
if (
  feature('COORDINATOR_MODE') &&
  isEnvTruthy(process.env.CLAUDE_CODE_COORDINATOR_MODE) &&
  !mainThreadAgentDefinition
) {
  const { getCoordinatorSystemPrompt } = require('../coordinator/coordinatorMode.js')
  return asSystemPrompt([
    getCoordinatorSystemPrompt(),
    ...(appendSystemPrompt ? [appendSystemPrompt] : []),
  ])
}
```

（src/utils/systemPrompt.ts:56-75）第一级 override 直接短路返回，连 `appendSystemPrompt` 都不拼，它是给 loop 模式这类需要完全控制提示词的场景用的。第二级 coordinator 模式用惰性 `require` 避免模块加载期的循环依赖（src/utils/systemPrompt.ts:67-70），这在源码里是反复出现的模式：提示词模块位于依赖图高处，不能随意 import 下游模块。

第三级 agent 提示词按模式分两种处理：proactive 模式下 agent 提示词是**追加**到默认提示词之后（包一层 `# Custom Agent Instructions`），否则**替换**默认提示词（src/utils/systemPrompt.ts:103-113）。注释解释了原因：proactive 的默认提示词已经很精简（自主 agent 身份 + memory + env），agent 在其上叠加领域行为，与 teammate 的模式一致。最后的兜底链（src/utils/systemPrompt.ts:115-122）是一个三选一：`agentSystemPrompt ?? customSystemPrompt ?? defaultSystemPrompt`，然后无条件追加 `appendSystemPrompt`。

agent 提示词的获取本身也分两路：内置 agent 的 `getSystemPrompt` 需要 `toolUseContext`，外部定义的 agent 不需要（src/utils/systemPrompt.ts:77-83）。如果 agent 带 memory 配置，这里还会顺手打一条 `tengu_agent_memory_loaded` 分析事件（src/utils/systemPrompt.ts:86-97）。优先级调度函数同时承担了埋点职责，因为所有提示词路径都必须经过它。

函数签名上还有一个细节：`toolUseContext` 的类型是 `Pick<ToolUseContext, 'options'>`（src/utils/systemPrompt.ts:50），只取 options 一个字段。提示词装配只需要配置，不需要 abortController、messages 等运行时状态，依赖面被收窄到最小。

## prompts.ts 主提示词：静态分节与边界标记

`getSystemPrompt`（src/constants/prompts.ts:444）生成默认提示词数组。整个文件 914 行，主体是一组 `get*Section()` 函数，每个产出一个以 `# 标题` 开头的分节：`# System`（src/constants/prompts.ts:186）、`# Doing tasks`（src/constants/prompts.ts:199）、`# Executing actions with care`（src/constants/prompts.ts:255）、`# Using your tools`（src/constants/prompts.ts:269）、`# Tone and style`（src/constants/prompts.ts:430）、`# Output efficiency`（src/constants/prompts.ts:403）。

函数开头有两个快速路径。`CLAUDE_CODE_SIMPLE` 环境变量为真时直接返回一句话提示词加 CWD 和日期（src/constants/prompts.ts:450-454），用于调试和最小化场景。正常路径先并行拉取 skill 命令列表、output style 配置和 env 信息（src/constants/prompts.ts:457-461），再把工具列表转成 `Set` 供各分节做存在性判断（src/constants/prompts.ts:464）。很多分节的内容取决于某个工具是否启用，比如 `# Using your tools` 里 TaskCreate 和 TodoWrite 哪个存在就用哪个名字（src/constants/prompts.ts:270-272）。

分节文本的组装统一走 `prependBullets` 工具函数（src/constants/prompts.ts:167-173）：单字符串展开成 ` - item`，数组展开成缩进两格的子项 `  - subitem`。整个文件没有手写 markdown 列表符号的地方，格式一致性由这一个函数保证。

这些分节的写法有一个共同特征：规则高度可判定。例如 `# Doing tasks` 里不写"保持代码整洁"，而写"不要为一次性操作创建 helper""三行相似的代码好过 premature abstraction"（src/constants/prompts.ts:203）；`# Using your tools` 里直接点名"读文件用 Read 而不是 cat/head/tail/sed"（src/constants/prompts.ts:292）。每条规则都能被模型映射到具体动作，几乎没有需要主观权衡的措辞。另一条主线是反模式枚举：`# Executing actions with care` 用一整段列举需要确认的操作：删除文件、force-push、修改 CI/CD、向第三方服务上传内容（src/constants/prompts.ts:260-264），即把"危险"这个模糊概念转成可判定的清单。

返回值的分段决定缓存边界（src/constants/prompts.ts:560-577）：

```typescript
return [
  // --- Static content (cacheable) ---
  getSimpleIntroSection(outputStyleConfig),
  getSimpleSystemSection(),
  outputStyleConfig === null ||
  outputStyleConfig.keepCodingInstructions === true
    ? getSimpleDoingTasksSection()
    : null,
  getActionsSection(),
  getUsingYourToolsSection(enabledTools),
  getSimpleToneAndStyleSection(),
  getOutputEfficiencySection(),
  // === BOUNDARY MARKER - DO NOT MOVE OR REMOVE ===
  ...(shouldUseGlobalCacheScope() ? [SYSTEM_PROMPT_DYNAMIC_BOUNDARY] : []),
  // --- Dynamic content (registry-managed) ---
  ...resolvedDynamicSections,
].filter(s => s !== null)
```

`SYSTEM_PROMPT_DYNAMIC_BOUNDARY` 是一个字符串哨兵 `'__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'`（src/constants/prompts.ts:114），把数组切成两半：之前的跨用户、跨会话都相同的静态内容可以打 `scope: 'global'` 缓存标记，之后的用户/会话相关内容不能。文件头部注释警告：移动或删除这个标记必须同步修改 `splitSysPromptPrefix` 和 `buildSystemPromptBlocks`（src/constants/prompts.ts:110-113）。三个文件靠一个字符串字面量维持隐式契约。

静态区也不是无条件静态。`getSessionSpecificGuidanceSection` 的注释记录了教训：任何依赖会话状态的字符串（是否有 AskUserQuestion 工具、是否交互模式、是否启用 fork subagent）如果放进静态前缀，会让前缀哈希的变体数按 2^N 增长，直接击穿缓存（src/constants/prompts.ts:343-351）。所以它被整体挪到边界之后。

边界之后的动态分节里能看到同一类权衡的更多样本。`token_budget` 分节当前是无条件缓存的，注释说明它曾经是 `DANGEROUS_uncached`：每次预算开关翻转要浪费约 2 万 token 的缓存，后来靠改写措辞（"When the user specifies..."使其在无预算时成为空操作）换回了缓存资格（src/constants/prompts.ts:538-550）。这个案例的做法不是接受缓存失效，而是改写提示词文本，让它在两种状态下字面相等。env 信息也走动态区：`computeSimpleEnvInfo` 产出 `# Environment` 分节，包含工作目录、是否 git 仓库、平台、shell、OS 版本、模型名和知识截止（src/constants/prompts.ts:651-710），其中 worktree 会话会额外插入"不要 cd 回主仓库"的指令（src/constants/prompts.ts:679-681）。

## 分节缓存：systemPromptSections

边界之后的动态分节由一个小型注册表管理（src/constants/systemPromptSections.ts）。`systemPromptSection(name, compute)` 声明一个可缓存分节（src/constants/systemPromptSections.ts:20-25），计算结果缓存到 `/clear` 或 `/compact` 为止（src/constants/systemPromptSections.ts:65-68）；`DANGEROUS_uncachedSystemPromptSection(name, compute, _reason)` 声明每轮重算的分节，且强制要求填写理由（src/constants/systemPromptSections.ts:32-38）。函数名里的 `DANGEROUS_` 前缀和必填的 `_reason` 参数是把"这会击穿缓存"写进 API 形态的手段。

主提示词里唯一的 uncached 分节是 `mcp_instructions`，理由注明"MCP servers connect/disconnect between turns"（src/constants/prompts.ts:513-520）。MCP 服务器可能在两轮之间连接或断开，instructions 必须反映当前状态，只能牺牲缓存。其余如 memory、env_info、language、output_style 都是普通缓存分节（src/constants/prompts.ts:491-555）。

`resolveSystemPromptSections` 的实现只有十几行（src/constants/systemPromptSections.ts:43-58）：缓存命中直接返回，未命中则并发执行所有 `compute` 并写回缓存。并发用 `Promise.all` 对所有分节统一处理，不管命中与否，简化了"部分命中"的中间态。清缓存的入口 `clearSystemPromptSections` 同时重置 beta header latches（src/constants/systemPromptSections.ts:65-68）。`/clear` 和 `/compact` 是提示词生命周期里仅有的两个重置点。

## getSystemContext / getUserContext：注入位置

git status 和 CLAUDE.md 不在 system prompt 数组里，而是作为 user 消息注入。两个采集函数都在 src/context.ts，都用 `memoize` 缓存整个会话。

`getGitStatus`（src/context.ts:36-111）并行执行 branch、default branch、`status --short`、`log --oneline -n 5`、`config user.name` 五条命令（src/context.ts:61-77），status 超过 2000 字符截断并提示"如需更多信息用 BashTool 跑 git status"（src/context.ts:85-89）。输出文本自带一句防误解说明："这是会话开始时的快照，不会在会话中更新"（src/context.ts:97），防止模型把旧 status 当实时状态。

`getSystemContext`（src/context.ts:116-150）打包 gitStatus；`getUserContext`（src/context.ts:155-189）打包 claudeMd 和 `currentDate`。注入发生在 src/utils/api.ts：gitStatus 走 `appendSystemContext`，以 `key: value` 形式追加为 system prompt 的最后一段（src/utils/api.ts:437-447）；claudeMd 走 `prependUserContext`，包成一条 `<system-reminder>` 的 meta user 消息插到消息列表头部（src/utils/api.ts:449-474）。同为上下文，一个进 system 尾部、一个进 user 消息，区别在语义归属：git status 是环境事实，CLAUDE.md 是需要模型"当作用户指令对待"的内容。`prependUserContext` 生成的 system-reminder 里还自带一句"this context may or may not be relevant... should not respond to this context"（src/utils/api.ts:469），防止模型对上下文本身作出回应。

`getSystemContext` 里有一个 ant-only 的调试通道：`setSystemPromptInjection` 设置注入文本后会立即清空两个 context 的 memoize 缓存（src/context.ts:29-34），注入内容以 `[CACHE_BREAKER: ...]` 形式进入 systemContext（src/context.ts:141-147），这是故意击穿提示词缓存的开关，用于缓存相关的内部调试。git status 在两种情况下被跳过：`CLAUDE_CODE_REMOTE` 环境（resume 时的不必要开销）或设置里关闭了 git 指令（src/context.ts:124-128）。

`--system-prompt` 与这套机制互斥：`fetchSystemPromptParts` 在 `customSystemPrompt` 存在时跳过默认提示词构建，并且 `systemContext` 直接返回空对象（src/utils/queryContext.ts:62-71）。自定义提示词整体替换默认提示词，git status 也就无处依附。

## claudemd.ts：层级向上查找

CLAUDE.md 的发现逻辑在 src/utils/claudemd.ts，文件头部注释定义了四级记忆（src/utils/claudemd.ts:4-7）：Managed（如 /etc/claude-code/CLAUDE.md）、User（~/.claude/CLAUDE.md）、Project（CLAUDE.md、.claude/CLAUDE.md、.claude/rules/*.md）、Local（CLAUDE.local.md）。

`getMemoryFiles`（src/utils/claudemd.ts:790）按序采集：Managed 最先（"always loaded - policy settings"，src/utils/claudemd.ts:803），然后 User，然后是从 cwd 逐级向上的目录查找：

```typescript
const dirs: string[] = []
const originalCwd = getOriginalCwd()
let currentDir = originalCwd

while (currentDir !== parse(currentDir).root) {
  dirs.push(currentDir)
  currentDir = dirname(currentDir)
}
// Process from root downward to CWD
for (const dir of dirs.reverse()) {
```

（src/utils/claudemd.ts:850-878）先向上收集全部祖先目录，再 `reverse()` 从文件系统根向 cwd 处理，离 cwd 越远的 CLAUDE.md 越先进入数组。每一层尝试四个来源：`CLAUDE.md`（src/utils/claudemd.ts:888）、`.claude/CLAUDE.md`（src/utils/claudemd.ts:899）、`.claude/rules/*.md`（src/utils/claudemd.ts:910-919）、`CLAUDE.local.md`（src/utils/claudemd.ts:923-933）。嵌套 worktree 场景有专门处理：向上查找会同时经过 worktree 根和主仓库根，同一份 checked-in 文件会被加载两次，因此主仓库工作树内的 Project 类文件被跳过，但 gitignore 掉的 CLAUDE.local.md 仍加载（src/utils/claudemd.ts:859-875）。

记忆文件还支持 `@path` include 指令（src/utils/claudemd.ts:18-21），由 `processMemoryFile` 递归展开（src/utils/claudemd.ts:618）：主文件先入数组，被 include 的文件紧随其后并记录 parent 路径（src/utils/claudemd.ts:656-679），`processedPaths` 集合防止循环引用。include 目标限定为文本扩展名，二进制文件（图片、PDF）会被拒绝加载（src/utils/claudemd.ts:94-99）。单个记忆文件的推荐上限是 40000 字符（src/utils/claudemd.ts:92）。`.claude/rules/*.md` 目录由独立的 `processMdRules` 处理，支持 frontmatter 里的 paths 条件规则，只有匹配目标路径的 rule 才被加载（src/utils/claudemd.ts:697-704）。

最终 `getClaudeMds` 把所有文件拼成一个字符串，每个文件带类型标注，如"project instructions, checked into the codebase"（src/utils/claudemd.ts:1168-1177），并在开头加上一句硬性指令（src/utils/claudemd.ts:89-90）：

```typescript
const MEMORY_INSTRUCTION_PROMPT =
  'Codebase and user instructions are shown below. Be sure to adhere to these instructions. IMPORTANT: These instructions OVERRIDE any default behavior and you MUST follow them exactly as written.'
```

这句话是 CLAUDE.md 能压过默认行为的机制所在：优先级不是在代码里裁决的，而是在提示词文本里声明的。`getUserContext` 里还有两个开关：`CLAUDE_CODE_DISABLE_CLAUDE_MDS` 硬关闭，`--bare` 模式跳过自动发现但保留显式 `--add-dir`（src/context.ts:165-167）。

每一级记忆来源还受 settings source 开关的独立控制：Project 类文件要求 `projectSettings` 启用，CLAUDE.local.md 要求 `localSettings` 启用（src/utils/claudemd.ts:887, 923），SDK 调用方可以通过 settingSources 精确裁剪加载面。`--add-dir` 附加目录的 CLAUDE.md 默认不加载，需要 `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` 显式开启（src/utils/claudemd.ts:936-941），注释给出的理由是 `--add-dir` 是显式用户动作、不走 projectSettings 开关，但仍需环境变量授权，默认收敛。

## buildSystemPromptBlocks：分块与缓存友好排序

发送前的最后一步是 `buildSystemPromptBlocks`（src/services/api/claude.ts:3213），它把字符串数组映射为 `TextBlockParam[]`，按块打 `cache_control` 标记，函数体第一行注释写着"Do not add any more blocks for caching or you will get a 400"（src/services/api/claude.ts:3221），API 对 cache breakpoint 数量有限制。实际分块逻辑委托给 `splitSysPromptPrefix`（src/utils/api.ts:321），其 docstring 列出三种模式（src/utils/api.ts:300-320）：有 MCP 工具时全部走 org 级缓存；全局缓存模式且找到边界标记时，切成 attribution header、CLI 前缀、静态段（`cacheScope: 'global'`）、动态段（不缓存）四块（src/utils/api.ts:387-396）；默认模式（3P provider 或找不到边界）退化为 org 级缓存三块。

调用点在 src/services/api/claude.ts:1358-1379，发送前还会往数组头部塞两块：计费 attribution header 和 CLI 标识前缀。最终排序落实了"稳定内容前置"原则：attribution header 虽然每块都不同，但它被排在最前且不参与缓存；静态主提示词紧随其后享受全局缓存；env、git status、CLAUDE.md 等易变内容被压到数组尾部，变动时只损失尾部缓存。

分块顺序不是简单的数组顺序遍历。`splitSysPromptPrefix` 在各模式下都先把 attribution header（按 `x-anthropic-billing-header` 前缀识别）和 CLI 前缀（按 `CLI_SYSPROMPT_PREFIXES` 集合匹配）从数组里挑出来单独成块，剩余内容按边界位置归入静态或动态桶，再各自 `join('\n\n')` 合并（src/utils/api.ts:336-358, 372-396）。也就是说，装配阶段切细的数组在发送前又被合并成大块：数组结构服务装配期的灵活性，分块结构服务缓存。发送前 `logAPIPrefix` 会对首块算 sha256 并上报（src/utils/api.ts:281-294），用于线上分析各用户前缀的分布和命中率。

## output styles 与 appendSystemPrompt 的叠加

output style 通过 `getOutputStyleConfig` 解析（src/constants/outputStyles.ts:181-211），plugin 强制的 style 优先于用户设置。它从三个位置渗入系统提示词：intro 句会根据有无 style 切换措辞（src/constants/prompts.ts:180）；`keepCodingInstructions === false` 的 style 会整块移除 `# Doing tasks`（src/constants/prompts.ts:564-567）；style 自身的 prompt 作为 `# Output Style: <name>` 分节进入动态区（src/constants/prompts.ts:151-158, 505-507）。

`appendSystemPrompt`（来自 `--append-system-prompt`）则是另一条独立通道，在 `buildEffectiveSystemPrompt` 末尾无条件追加（src/utils/systemPrompt.ts:121）。两条通道互不感知：output style 改变的是提示词的身份框架和分节构成，append 追加的是尾部指令。装配顺序保证了两者的稳定叠加：style 分节在动态区，append 在所有分节之后，谁的文本都不会因为对方的存在而移位，缓存前缀保持不变。

主循环里的完整调用现场可以在 REPL 看到：`getSystemPrompt`、`getUserContext`、`getSystemContext` 并行拉取，然后交给 `buildEffectiveSystemPrompt` 合并（src/screens/REPL.tsx:2535-2542）。合并结果存进 `toolUseContext.renderedSystemPrompt`（src/screens/REPL.tsx:2543），供后续轮次复用，装配不是每轮重做，memoize 和分节缓存保证同一个会话内大部分计算只发生一次。从静态分节、动态注册表、文件系统记忆到 API cache block，一次请求发出前提示词经过的环节就是这些。

## 本篇涉及的源码文件

- `src/utils/systemPrompt.ts`：buildEffectiveSystemPrompt 五级优先级链调度器
- `src/constants/prompts.ts`：914 行默认系统提示词主体，分节函数与动态边界标记
- `src/constants/systemPromptSections.ts`：分节缓存注册表与 DANGEROUS_uncached 声明
- `src/context.ts`：getSystemContext/getUserContext，git status 与 CLAUDE.md 采集
- `src/utils/claudemd.ts`：CLAUDE.md 四级记忆发现、层级向上查找与 @include 展开
- `src/services/api/claude.ts`：buildSystemPromptBlocks，发送前的 cache block 切分
- `src/utils/api.ts`：splitSysPromptPrefix 三种缓存模式与 prependUserContext 注入
- `src/utils/queryContext.ts`：fetchSystemPromptParts，customSystemPrompt 的互斥逻辑
- `src/constants/outputStyles.ts`：getOutputStyleConfig 解析 output style 配置
- `src/screens/REPL.tsx`：主循环中提示词装配的调用现场
