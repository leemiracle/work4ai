---
title: Claude Code 源码拆解 20：隐藏面：feature flag、彩蛋与对抗设计
date: "2026-04-12 21:00"
series: Claude Code 源码拆解
tags: ["Claude Code", "源码分析"]
---
> 系列第 20/20 篇 · 对应主题：收官

# 隐藏面：feature flag、彩蛋与对抗设计

前十九篇拆解的都是 Claude Code 摆在外面的能力：工具、权限、上下文、子代理。收官篇换一个视角，看那些不打算让你看见、或者看见了也无伤大雅的东西：编译期被抹掉的代码、运行时远程下发的开关、一只用 PRNG 抽卡孵化的终端宠物、给内部员工准备的"缄默模式"，以及一个直接写进 API 请求体的反蒸馏开关。它们共同构成一个产品的"隐藏面"：同一个仓库，两种构建，三种用户（外部用户、内部员工 ant、评测 harness），看到的程序完全不同。

## 双层门控：编译期 feature() 与运行时 GrowthBook

Claude Code 的功能开关分两层。第一层是编译期：`import { feature } from 'bun:bundle'`（src/entrypoints/cli.tsx:1），在打包时由 bundler 常量折叠。全仓库共出现 940 余处 `feature(...)` 调用，去重后 89 个不同的 flag。仅 cli.tsx 一个入口文件就展示了这套机制的用法：`DUMP_SYSTEM_PROMPT` 把渲染后的系统提示词直接打印给评测 harness（src/entrypoints/cli.tsx:53-71）、`DAEMON` 放行 `--daemon-worker` 和 `daemon` 子命令、`BG_SESSIONS` 放行 `ps/logs/attach/kill`、`BRIDGE_MODE` 放行 remote-control、`CHICAGO_MCP` 放行 computer-use MCP server、`TEMPLATES`、`BYOC_ENVIRONMENT_RUNNER`、`SELF_HOSTED_RUNNER` 各占一条快速分发路径（src/entrypoints/cli.tsx:86-245）。其余 flag 从名字就能读出一张产品路线图：`KAIROS_DREAM`、`PROACTIVE`、`VOICE_MODE`、`COORDINATOR_MODE`、`TEAMMEM`、`ULTRAPLAN`、`TREE_SITTER_BASH`、`WEB_BROWSER_TOOL`、`MONITOR_TOOL`。`feature(X)` 为 false 的分支被死代码消除（DCE）整个从外部构建里删掉，不只是不执行，而是不存在。cli.tsx 里的注释说得很直白："feature() must stay inline for build-time dead code elimination"（src/entrypoints/cli.tsx:225-226）。这就是为什么外部构建的二进制里 grep 不到内部子命令的实现，也是为什么这份"公开"源码里会出现 moreright 这样只剩存根的目录。

第二层是运行时的 GrowthBook 远程配置（src/services/analytics/growthbook.ts）。客户端以 `remoteEval: true` 初始化（src/services/analytics/growthbook.ts:530），即特征求值在服务端完成，客户端只拿结果，本地不做规则匹配，也就无从反推 targeting 规则。上报给 GrowthBook 的用户属性包括 deviceId、sessionId、平台、组织/账号 UUID、订阅类型、rateLimitTier、邮箱、app 版本，以及企业代理部署场景下的 `ANTHROPIC_BASE_URL` hostname，注释说明这是为了给走 apiKeyHelper 的企业代理用户提供一个可定向的稳定属性，否则他们没有任何组织级标识（src/services/analytics/growthbook.ts:439-449, 466-485）。这套实现里有几处防御性工程，每一处都对应一个真实事故：

- 空 payload 守卫：`processRemoteEvalPayload` 在 `Object.keys(payload.features).length === 0` 时直接返回 false，因为"transient server bug, truncated response"会导致 `{}` 被整体写盘，"total flag blackout for every process sharing ~/.claude.json"（src/services/analytics/growthbook.ts:334-340）。
- 响应格式修正：API 返回 `value` 而 SDK 期望 `defaultValue`，代码自己做转换并缓存进 `remoteEvalFeatureValues`，注释承认这是 "WORKAROUND"（src/services/analytics/growthbook.ts:330-356, 378-392）。
- 磁盘缓存：每次成功拿到 payload 就整体覆盖写入 `cachedGrowthBookFeatures`，启动热路径用 `getFeatureValue_CACHED_MAY_BE_STALE` 纯读缓存，不阻塞（src/services/analytics/growthbook.ts:407-417, 734-775）。
- 曝光去重：实验曝光事件每个 feature 每会话只上报一次，防止渲染循环里的热路径反复触发（src/services/analytics/growthbook.ts:86-89, 296-314）。

刷新频率也按用户身份区分：外部用户 6 小时一次，ant 20 分钟一次（src/services/analytics/growthbook.ts:1013-1016）。ant 还有两条特权覆盖通道：环境变量 `CLAUDE_INTERNAL_FC_OVERRIDES`（JSON 格式，供评测 harness 使用，优先级最高以保证确定性）和 `/config` 的 Gates 面板写入 `growthBookOverrides`（src/services/analytics/growthbook.ts:167-192, 211-220），两者都硬检查 `process.env.USER_TYPE === 'ant'`。

对于"宁可错放不可错杀"的门禁，还有专门的 `checkGate_CACHED_OR_BLOCKING`：磁盘缓存说 true 就直接放行，说 false 才去等最多约 5 秒的 init 拉新值，因为"stale `false` would unfairly block access but a stale `true` is acceptable"（src/services/analytics/growthbook.ts:904-935）。安全门禁走相反方向：`checkSecurityRestrictionGate` 优先信 Statsig 旧缓存，且在重新初始化进行中时会等待完成，保证登录切换后拿到新账号的值（src/services/analytics/growthbook.ts:851-889）。同一个 flag 系统，按业务语义分出"宁可旧 true""宁可旧 false""必须等新值"三种读取策略，是这个文件里最体现工程成熟度的部分。

代码中还留着迁移痕迹：`checkStatsigFeatureGate_CACHED_MAY_BE_STALE` 仍保留 Statsig 磁盘缓存的回退路径，注释标注 "MIGRATION ONLY"，说明 flag 系统正在从 Statsig 迁往 GrowthBook（src/services/analytics/growthbook.ts:792-837）。`tengu_` 前缀同时出现在 GrowthBook flag 名里（如 `tengu_anti_distill_fake_tool_injection`），与 undercover 提示词点名的内部代号 Tengu 互为印证。

## buddy：一只确定性孵化的电子宠物

`feature('BUDDY')` 门控下是 src/buddy/，一个蹲在输入框旁边、偶尔冒泡评论的电子宠物。它的抽卡系统做了一套专门的防作弊设计。

抽卡用 Mulberry32 种子 PRNG，注释自嘲 "good enough for picking ducks"（src/buddy/companion.ts:15-25）。种子是 `hashString(userId + SALT)`，盐值硬编码为 `'friend-2026-401'`（src/buddy/companion.ts:84）。抽卡流程一次 roll 出稀有度、物种、眼睛、帽子、闪光和五维属性（src/buddy/companion.ts:91-102）：

```typescript
function rollFrom(rng: () => number): Roll {
  const rarity = rollRarity(rng)
  const bones: CompanionBones = {
    rarity,
    species: pick(rng, SPECIES),
    eye: pick(rng, EYES),
    hat: rarity === 'common' ? 'none' : pick(rng, HATS),
    shiny: rng() < 0.01,
    stats: rollStats(rng, rarity),
  }
  return { bones, inspirationSeed: Math.floor(rng() * 1e9) }
}
```

稀有度权重 common 60 / uncommon 25 / rare 10 / epic 4 / legendary 1（src/buddy/types.ts:126-132），闪光独立 1%。普通种不戴帽子；帽子池有 crown、tophat、propeller、halo、wizard、beanie、tinyduck 七种（另有 none）（src/buddy/types.ts:79-89）。五维属性是 DEBUGGING、PATIENCE、CHAOS、WISDOM、SNARK（src/buddy/types.ts:91-98），roll 法是先定一个 peak、一个 dump，其余散点，地板值随稀有度从 5 抬到 50，peak 再加 50~80（src/buddy/companion.ts:53-82）。稀有度还各自映射星级（legendary 五星）与主题色（legendary 用 warning 色，即终端里最醒目的黄/橙）（src/buddy/types.ts:134-148）。

抽卡结果在三个热路径被反复读取（500ms 的精灵 tick、PromptInput 的每次击键、每轮的 observer），所以 `roll()` 对同一 userId 缓存一次结果（src/buddy/companion.ts:104-113）。

关键设计在持久化：磁盘上只存 `CompanionSoul`（名字和性格，由模型生成），`bones` 永不落盘，每次读取时从 `hash(userId)` 重新生成（src/buddy/companion.ts:124-133）。注释解释了原因："species renames and SPECIES-array edits can't break stored companions, and editing config.companion can't fake a rarity"，即用户改配置文件改不出一只 legendary，因为稀有度由 userId 决定。同一个 userId 在任何机器上孵出的都是同一只宠物。

物种列表本身是另一个隐藏点：18 个物种名全部用 `String.fromCharCode(0x64, 0x75, ...)` 运行时构造（src/buddy/types.ts:14-52）。注释说明，其中一个物种名与 excluded-strings.txt 里的模型代号金丝雀字符串相撞，而该检查 grep 的是构建产物而非源码，运行时构造可以让字面量不进 bundle，同时保持检查对真正的代号继续生效（src/buddy/types.ts:10-13）。undercover 提示词里点名的动物代号正是 Capybara 和 Tengu（src/utils/undercover.ts:49），而 capybara 恰好是物种之一。

精灵是 5 行高、12 字符宽的 ASCII 画，每个物种 3 帧做 idle 抖动动画，第 0 行是帽子槽（src/buddy/sprites.ts:23-26）。模型侧通过 `companion_intro` attachment 被告知宠物的存在："You're not ${name} — it's a separate watcher... your job in that moment is to stay out of the way"（src/buddy/prompt.ts:7-13）。

## undercover：给内部构建的缄默协议

undercover 模式解决一个具体问题：Anthropic 员工（ant）用内部构建的 Claude Code 给公共开源仓库提 commit 和 PR 时，不能泄露内部模型代号、未发布的版本号和内部项目名。

激活逻辑是"默认开、无强制关"（src/utils/undercover.ts:28-37）：

```typescript
export function isUndercover(): boolean {
  if (process.env.USER_TYPE === 'ant') {
    if (isEnvTruthy(process.env.CLAUDE_CODE_UNDERCOVER)) return true
    return getRepoClassCached() !== 'internal'
  }
  return false
}
```

`CLAUDE_CODE_UNDERCOVER=1` 可以强制开；自动模式下，只有当仓库 remote 命中 `INTERNAL_MODEL_REPOS` 白名单（src/utils/commitAttribution.ts:30-75，包含 claude-cli-internal、casino、trellis 等 22 个确认私有的仓库，SSH 和 HTTPS 两种 URL 格式各列一遍）才关闭。`'external'`、`'none'`、甚至 `null`（检查尚未运行）全部判定为 ON，注释解释了为什么连 cwd 不是 git 仓库也要保持 undercover："Claude may push to public remotes from a CWD that isn't itself a git checkout (e.g. /tmp crash repro)"（src/utils/undercover.ts:13-15）。文件头注释写明设计意图："There is NO force-OFF... if we're not confident we're in an internal repo, we stay undercover"（src/utils/undercover.ts:16-17）。白名单刻意做成 repo 级而非 org 级，因为 anthropics org 下有公共仓库（包括 anthropics/claude-code 本身）（src/utils/commitAttribution.ts:24-28）。仓库分类通过 `getRemoteUrlForDir` 取 remote URL 后做子串匹配，结果按进程缓存一次（src/utils/commitAttribution.ts:114-129）。

开启后注入的提示词是一份详细的负面清单：不许出现动物代号、未发布版本号（opus-4-7、sonnet-4-8）、内部仓库名、go/ 短链、"Claude Code" 字样、任何 AI 身份暗示、Co-Authored-By 行（src/utils/undercover.ts:41-69），并给出正反例，"1-shotted by claude-opus-4-6" 被明确列为 BAD。

整个文件的代码路径都包在 `process.env.USER_TYPE === 'ant'` 里。注释指出 USER_TYPE 是 build-time `--define`，bundler 会常量折叠并 DCE 掉所有 ant 分支，"In external builds every function in this file reduces to a trivial return"（src/utils/undercover.ts:18-22）。配套地，`sanitizeModelName` 把内部模型名映射回公开名，未知模型一律归为 `'claude'`（src/utils/commitAttribution.ts:154-168）。

## anti-distillation：写进请求体的投毒开关

最"对抗性"的一段代码藏在 API 请求构造里（src/services/api/claude.ts:301-313）：

```typescript
// Anti-distillation: send fake_tools opt-in for 1P CLI only
if (
  feature('ANTI_DISTILLATION_CC')
    ? process.env.CLAUDE_CODE_ENTRYPOINT === 'cli' &&
      shouldIncludeFirstPartyOnlyBetas() &&
      getFeatureValue_CACHED_MAY_BE_STALE(
        'tengu_anti_distill_fake_tool_injection',
        false,
      )
    : false
) {
  result.anti_distillation = ['fake_tools']
}
```

四重门控叠加：编译期 flag、入口必须是 cli、必须是第一方请求、再叠一个 GrowthBook 运行时 flag（默认 false）。全部通过后在 API extra body 里写入 `anti_distillation: ['fake_tools']`，让服务端在响应里注入虚假工具定义。如果有人抓包第一方流量去蒸馏（复制）这套 harness 的行为，学到的工具集里就混着不存在的工具。客户端只发一个 opt-in 标记，投毒发生在服务端、对客户端完全透明，本机抓包看到的响应里同样带着假工具，进一步提高了蒸馏者分辨成本。投毒只针对 1P，第三方 Bedrock/Vertex 流量天然免疫，运行时 flag 又给了随时按人群灰度或紧急关停的能力。这是客户端代码里少见的主动对抗措施：不信任自己流量会被怎样使用。

## ABLATION_BASELINE：一行开关回到 L0

cli.tsx 顶部有一段在任何模块加载之前执行的代码（src/entrypoints/cli.tsx:21-26）：

```typescript
if (feature('ABLATION_BASELINE') && process.env.CLAUDE_CODE_ABLATION_BASELINE) {
  for (const k of ['CLAUDE_CODE_SIMPLE', 'CLAUDE_CODE_DISABLE_THINKING', 'DISABLE_INTERLEAVED_THINKING', 'DISABLE_COMPACT', 'DISABLE_AUTO_COMPACT', 'CLAUDE_CODE_DISABLE_AUTO_MEMORY', 'CLAUDE_CODE_DISABLE_BACKGROUND_TASKS']) {
    process.env[k] ??= '1';
  }
}
```

注释称之为 "Harness-science L0 ablation baseline"：设一个环境变量，就同时关掉 thinking、交错 thinking、手动/自动 compact、自动记忆、后台任务共 7 个能力，把 harness 打回裸模型基线。必须内联在入口而非 init.ts，因为 BashTool/AgentTool/PowerShellTool 在 import 时就把 `DISABLE_BACKGROUND_TASKS` 捕获进模块级常量，init() 跑得太晚（src/entrypoints/cli.tsx:16-19）。`??=` 的写法保留了显式设置的值，允许消融时单独恢复某一项做对照组。这个开关的存在说明内部对 harness 每个组件的贡献做系统性消融测量：本系列前十九篇拆解的每个子系统，在这里都对应一个可以被单独关掉的变量。模型评测里说的 harness 增益，落实到代码里就是这组可以精确加减的环境变量。

## /insights 与 thinkback：用模型分析你自己

`/insights` 是整个 commands 目录里最重的单文件命令：3200 行（src/commands/insights.ts:3039-3045）。它读取 `~/.claude/projects/` 下全部历史会话日志，对每个会话调用 Opus 提取结构化 facet：用户根本目标、目标分类、达成度、满意度、帮助度、会话类型、摩擦点、主要成功因素、一句话总结（src/commands/insights.ts:1010-1024），facet 和 session meta 都缓存到磁盘避免重复计费。长 transcript 先分块摘要再喂给 facet 提取（src/commands/insights.ts:881-934）。

聚合之后，再用一组并行 prompt 生成叙事性章节：project_areas、interaction_style、what_works、friction_analysis、suggestions、on_the_horizon、cc_team_improvements、model_behavior_improvements、fun_ending（src/commands/insights.ts:1338-1484）。每个章节的 prompt 都要求模型用第二人称 "you" 输出，并要求给出可复制的 copyable_prompt，让用户能把建议直接粘回去试用，而不是只读一遍分析。其中 cc_team_improvements 和 model_behavior_improvements 是给 CC 团队和模型团队的反馈，由用户自己的数据反哺产品；facet 提取请求带 `querySource: 'insights'`，服务端可以据此统计这条链路的花费（src/commands/insights.ts:1026-1039）。最终产出一份可分享的 HTML 报告并上传生成 reportUrl，命令最后让模型逐字输出一段固定话术告诉用户报告地址（src/commands/insights.ts:3046-3068 及文件尾部）。两个模型 getter 都固定返回 `getDefaultOpusModel()`，注释 "best quality"（src/commands/insights.ts:40-48）。ant 还有专属的 `--homespaces` 参数，通过 `coder list -o json` 收集远程 homespace 里正在运行的 workspace 会话（src/commands/insights.ts:60-80）。文件里甚至有一个 `detectMultiClauding`，用 30 分钟滑动窗口检测 "session1 -> session2 -> session1" 的多开模式（src/commands/insights.ts:1057-1062），multi-clauding 由此成为一个被正式命名并量化的使用行为。

这条命令本身就是对前几篇主题的一次回收：它复用第 5 篇拆过的 sessionStorage 读取层、第 2 篇的 queryWithModel 单轮查询通道，把历史会话数据从被动读取变成了主动分析。

姊妹命令 `/think-back` 是年终回顾："Your 2025 Claude Code Year in Review"，由 `tengu_thinkback` gate 控制可见性（src/commands/thinkback/index.ts:6-10）。

## 彩蛋两则：moreright 存根与 spinnerVerbs

src/moreright/useMoreRight.tsx 的存根本体只有 25 行，是一个"外部构建存根"：导出与内部 hook 相同的签名（onBeforeQuery / onTurnComplete / render），全部返回空操作，注释 "the real hook is internal only"（src/moreright/useMoreRight.tsx:1-5）。文件末尾还内嵌了一条 base64 data URL source map（src/moreright/useMoreRight.tsx:26），解码后 sourcesContent 与这个存根文件自身逐字一致。一个承认自己身份的存根，还自带出生证明。moreright 是什么，外部构建无从得知；hook 名暗示它在每次查询前后和每轮结束时有钩子，也许与本系列第 2 篇的主循环同级。这是"隐藏面"最直接的一个例子：存根告诉你这里缺了一块，但不告诉你缺的是什么。

spinnerVerbs.ts 则是完全公开的恶趣味：204 行文件里是一个约 190 词的动词表， loading 时随机展示（src/constants/spinnerVerbs.ts:16-204）。词表混着正常词（Thinking、Working、Computing）、厨房词（Caramelizing、Julienning、Flambéing、Proofing）、无厘头词（Flibbertigibbeting、Discombobulating、Shenaniganing、Whatchamacalliting）和自指词，如 `Clauding`（src/constants/spinnerVerbs.ts:45）与 `Honking`（呼应 goose）。用户可以在 settings 里用 `mode: 'replace'` 整体替换或追加自己的动词（src/constants/spinnerVerbs.ts:3-13）。这个数组一分钟就能写完，却是每个用户在每次等待时都会看到的部分。

## 本篇涉及的源码文件

- `src/services/analytics/growthbook.ts`：GrowthBook 运行时 flag 客户端，含 remote eval、磁盘缓存、曝光去重、ant 覆盖通道
- `src/entrypoints/cli.tsx`：CLI 入口，feature() 编译期门控巡礼、ABLATION_BASELINE 消融基线
- `src/buddy/companion.ts`：电子宠物抽卡，Mulberry32 种子 PRNG、稀有度/属性 roll、防作弊的 bones 重生成
- `src/buddy/types.ts`：物种/帽子/稀有度常量表，charCode 运行时构造规避金丝雀检查
- `src/buddy/sprites.ts`：18 物种 ASCII 精灵画，每物种 3 帧动画
- `src/buddy/prompt.ts`：companion_intro attachment，告知模型宠物的存在与边界
- `src/utils/undercover.ts`：undercover 模式，ant 内部构建在公共仓库隐藏代号与版本号，无强制关
- `src/utils/commitAttribution.ts`：INTERNAL_MODEL_REPOS 白名单、模型名脱敏、commit 归属统计
- `src/services/api/claude.ts`：getExtraBodyParams，anti_distillation fake_tools 投毒注入（仅 1P）
- `src/commands/insights.ts`：/insights，3200 行，用 Opus 分析你自己的历史会话并生成可分享报告
- `src/commands/thinkback/index.ts`：/think-back 年终回顾命令入口
- `src/moreright/useMoreRight.tsx`：外部构建存根，内嵌 base64 source map 自证身份
- `src/constants/spinnerVerbs.ts`：约 190 词的 loading 动词表
