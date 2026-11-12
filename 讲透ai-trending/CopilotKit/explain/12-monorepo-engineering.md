# 12 · monorepo 工程化：workspace、构建、lint 自研规则与发布线

## 角色定位（16 层架构中位置）

本篇对应图谱第 1 层「工作区与构建配置基座」与第 16 层「文档与工程工具链」——所有其它 14 层的地基与屋顶。地基侧：pnpm workspace 清单、nx 任务编排、tsconfig 双包（`packages/tsconfig` 仓内约定 + `packages/typescript-config` npm 发布）、tailwind-config。屋顶侧：`scripts/release/` 半自动发布线、`scripts/docs/` 文档生成、`scripts/sync-plugin-skills.ts` 技能同步（见第 08 篇）、oxlint 自研规则四件套。这一层不产出任何 @copilotkit 运行时代码，但它决定了 20 个包怎么一起编译、检查、发布——工程化决策的地层学全在这里。

一句话：这是"20 个包一条命令全绿"成立的那层胶水与规则。

## 内部结构（关键文件+行号锚拆解）

### pnpm-workspace：注释即架构决策

`pnpm-workspace.yaml` 的 packages 清单覆盖 packages/*、examples 三代布局（v1/v2/vue/angular/react-native，`:2-12`）、显式排除 `!examples/v1/_legacy`（`:13`）、showcase 三目录（`:14-16`）。最有价值的是 `:17-23` 的整段注释——**shell-dashboard 被刻意排除在 workspace 外**：它是平铺独立 Next.js 应用，自带 package-lock.json、用 `npm ci` 构建（见其 Dockerfile）；若纳入 pnpm workspace 会把它卷进 pnpm lockfile，破坏独立部署路径并使基于 npm 的 Docker 构建失效。注释同时说明 showcase/scripts **在** workspace 内的原因（harness 包 import 它且都用 pnpm）——纳入与否的每一条边界都有理由写进配置本身。`onlyBuiltDependencies: [better-sqlite3]`（`:24-25`）是 pnpm 的构建脚本白名单（只信这一个原生模块跑 postinstall）。根 package.json 钉 `packageManager: pnpm@10.33.4`（CONTRIBUTING.md 指引全局装 pnpm v9.x 存在主版本代差，digest b25）。

### nx 任务编排

`nx.json` 的 `targetDefaults` 定义 15 个目标（build/dev/test/test:watch/test:coverage/check-types/generate-graphql-schema/graphql-codegen/link:global/unlink:global/build:css/storybook:build/publint/attw/compat-check）。关键拓扑：`build` 的 `dependsOn: ["^build"]` + `inputs: ["production", "{projectRoot}/.env*"]` + `outputs: ["{projectRoot}/dist/**"]` + `cache: true`——先构建依赖图上游、产物可缓存；test 同构（dependsOn ^build 保证被测的是最新产物）。根 scripts 全部是 nx 薄壳：`build = nx run-many -t build --projects=packages/** --exclude=@copilotkit/demo-agents`、`dev = pnpm run build && nx watch --projects=packages/** -- pnpm run build`（文件监视增量重建）、`check:packages = nx run-many -t publint,attw`（发布物体检双件套）。`graph = nx graph` 可视化依赖图。

### tsdown 三格式构建与两个经典坑

各包 `tsdown.config.ts` 普遍三段式：ESM+CJS 主段 + React Native 段 + UMD 段（如 `packages/react-core/tsdown.config.ts:11-12` 主段 entry `["src/index.tsx", "src/v2/index.ts"]`、`:45-53` 第三段 format umd external `["react", "@copilotkit/core", "@copilotkit/shared"]`；`packages/a2ui-renderer/tsdown.config.ts:6` esm/cjs、`:20` umd、`:31` entryFileNames `[name].umd.js`、`:32` globals 映射）。

**坑一：banner 修 reflect-metadata 加载序**（`packages/runtime/tsdown.config.ts:18-26`）：banner 回调按 format 注入 `require("reflect-metadata");`（cjs）或 `import "reflect-metadata";`（esm）。注释 `:20-22` 讲透原因——rolldown 会把裸副作用 import **重排到 chunk 末尾**，破坏 type-graphql 对 reflect-metadata 的"必须最先执行"要求；banner 对 `_virtual/_rolldown/runtime` 产物传播，保证 reflect-metadata 永远第一行。没有这个 hack，runtime 的 GraphQL 装饰器在运行时拿不到类型反射。

**坑二：UMD globals 漏 external 将内联**：tsdown 的 `globals` 映射只在依赖同时列进 `external` 时生效——漏列则该依赖被直接打进 UMD bundle（体积膨胀且全局单例断裂）。仓内三种姿态：react-core UMD 段正确双列（external+globals 全量手工列举）；`packages/web-inspector/tsdown.config.ts` external 只列 lit 但 globals 声明 @copilotkit/core/lit/marked/lucide 全家——"其余依赖 globals 兜底或打进 bundle"（digest b61）；`packages/voice/tsdown.config.ts:24` 更极端：UMD 段 `external: []` 空数组而 `:28` 仍声明 globals——全部假定宿主已加载这些全局，是 UMD 分发策略的赌注式写法。

react-core 还有专属插件 `externalize-context`（`react-core/tsdown.config.ts:71-83`）：resolveId 钩子把相对 `../context` 导入改写为 external 的 `@copilotkit/react-core/v2/context` 包路径——**保证 v2 React context 在多包间共享同一单例**（否则每个包各持一份 context 实例，Provider 失效）。

### oxlint 自研规则四件套（packages/react-ui/oxlint-rules/）

`.oxlintrc.json` 经 `jsPlugins` 动态加载 `packages/react-ui/oxlint-rules/copilotkit-plugin.mjs`（14 行，`{meta, rules}` 对象字面量 + export default 的最小插件壳）。三条实规则按 severity 分层启用：

- **`require-cpk-prefix.mjs`（547 行，最大）**——Tailwind 类名必须带 `cpk:` 前缀（组件库防宿主样式冲突的命名空间纪律）。内含完整的 Tailwind 工具类识别器：`SINGLE_WORD_UTILITIES` 集合 + 110 余个前缀 + `VARIANT_RE` 变体正则（覆盖 has-[]/group-data-[] 任意值变体），检测逻辑复用自 `scripts/add-cpk-prefix.mjs`；`JS_VALUE_WORDS` 白名单防单词 JS 值被误判为类名。`.oxlintrc.json:13` 根级 "off"、`:57` 组件目录 "warn"、`:63` 再关——分层启用。
- **`no-single-arg-zod-record.mjs`（73 行）**——`z.record()` 单参数形态误用检查，`fixable: "code"` 自动修复（spread 参数无法安全改写时只报不修，digest b19）；`.oxlintrc.json:34` "error"。
- **`no-public-env-shell-read.mjs`（221 行）**——禁读 `process.env.PUBLIC_API_KEY` 类公开密钥进 shell；60 行头注释完整列出检测形态与**刻意不覆盖的盲区**（别名需作用域跟踪、批量迭代读、rest 解构），导出 `BANNED_KEYS` 供表驱动测试迭代同一 Set 防漂移；`.oxlintrc.json:85` "error"。

另有 `.oxlintrc.json` 全仓禁 `@a2ui/lit` 值导入（其注册 custom element 的副作用破坏 React Strict Mode——第 09 篇详述）。lint/format 用 oxlint + oxfmt（`lint = oxlint .`、`format = oxfmt --write .`），`.oxfmtrc.json` 刻意忽略 `**/package.json`（oxfmt --write 会把严格 JSON 重写成 JSON5 导致 pnpm ERR_PNPM_JSON_PARSE，digest b25）。

### 发布线：changesets 目录 + 自研 release 脚本双轨

`.changeset/` 目录存 10 个变更记录 md（angular-21-install-and-types / bump-license-verifier-ent-251 / fix-thread-switch-state-reset 等）但**没有 config.json**——changesets 只有"写变更单"的用法被保留。真正的发布执行是自研线 `scripts/release/`：

- `prepare-release.ts` / `prerelease.ts` / `publish-release.ts` / `bump-prerelease.ts` 四阶段 + `detect-py-version-changes.sh`（PyPI 版本检测，内嵌三段 python3 heredoc 无 shell 三方依赖）+ `generate-ai-release-notes.ts`（用原生 https.request 手写 Anthropic 调用，不依赖 SDK；无 key 优雅降级）；
- **build-release-notification 纯函数真值表**：`lib/build-release-notification.ts` 头部 40 行注释即完整失败模型文档——"deliberately a PURE function of its inputs so the full truth table can be unit-tested without any GitHub Actions / network involvement"。两条独立泳道（npm+PyPI）：dry-run 全静默；canary（prerelease）npm 泳道成功失败都不发（"npm canaries are noise"）；SUCCESS 行的 releaseUrl 空值守卫被标注 DEFENSE-IN-DEPTH——注释 `:20-26` 论证该状态**当前不可达**（tag step `if: success()`，失败会把 job 翻成 failure 走失败臂）但防未来有人改 continue-on-error；失败措辞刻意用 "release failed" 而非 "publish failed"（publish 步可能已成功、是后面的 tag/release 步失败）。薄 CLI 包装 `build-release-notification.ts` 解析 env、调纯函数、`writeGithubOutput` 用 `randomBytes(8)` 生成定界符（`:151`）防值内含定界符注入 GITHUB_OUTPUT；`KNOWN_JOB_RESULTS` 白名单（`:54`）对非法枚举 warn+回退默认。测试三件（lib 目录内 `*.test.ts` + wrapper 测试）由 `vitest.config.mts` 的 `include lib/**` 覆盖；
- **最小权限流水线**：prerelease.ts/publish-release.ts 头注释钉版职责切分——build/test/bump 在无 secrets 的 CI job，publish 步才接触 npm 凭据；bump-prerelease.ts 拆分动机是 secrets 隔离（build job 无 NPM_TOKEN）；
- `lib/versions.ts` 自实现 parseSemver（不引 semver 包），bumpPackages 会同步改写依赖里带 @copilotkit/ scope 前缀的 workspace 引用保证版本联动；`lib/notion.ts` 自带受限 markdown↔Notion blocks 双向转换器（只覆盖 release notes 用到的四类块）。

### typedoc 断链与系统性缺口

全仓 typedoc 消费者经 ls 实证为 **9 个**（任务书与 digest 快照的 7 个之上，磁盘新增 react-textarea 与 tsconfig 两个）：react-core / react-textarea / react-ui / runtime-client-gql / runtime / sdk-js / shared / tailwind-config / tsconfig 的 typedoc.json **全部** `"extends": ["../../typedoc.base.json"]`，而仓库根的 typedoc.base.json **不存在**（ls 与 git ls-files 双实证，上游从未提交或已删）。每包运行 typedoc 时才会暴露此断裂。第二层缺口是 entryPoints 只覆盖主入口：runtime 只 `src/index.ts`（v2 子入口 ./v2 不进文档）、sdk-js 只 `src/index.ts`（langchain/langgraph/langgraph-middlewares 三个 exports 子入口全部漏掉）、tailwind-config/tsconfig entryPoints 为空数组（实际无文档产出）。而仓内真实存在的共享 typedoc 基座 `packages/tsconfig/typedoc.json` 无任何包引用它。

### tailwind v3/v4 两代并存

`packages/tailwind-config/tailwind.config.js` 是 v3 JS 配置范式遗存（module.exports 配置对象）；`packages/web-inspector/src/styles/tailwind.css` 是 v4 CSS-first 范式（`@import "tailwindcss"` + `@source` 指令取代 JS 配置，:host 与 @layer base 适配 Lit shadow DOM）。同一 monorepo 两代范式并存的代价：类名前缀、暗色模式策略、内容扫描机制都不同，跨包复制样式时要先鉴定代际。

### AGENTS.md vs CLAUDE.md：一对双胞胎的真相分裂

两文件约 90% 重叠且都由 Nx 自动更新注释块维护，但在包结构描述上互相矛盾：`AGENTS.md:23` 说 "Some packages have `v1/` and `v2/` internal directories for backward compatibility"——**过时**（packages/ 下 find 零命中 v1/v2 目录）；`CLAUDE.md:23` 说 "all packages live directly under `packages/` (no `v1` or `v2` subdirectories)"——**与磁盘一致**。两份 AI 代理指令文件里一个带着旧世界观，面向 Claude 的那份是对的（digest b25 甄别）。

## 外部连接（imports 边上下游）

- **workspace 内部协议**：`workspace:*` 版本协议连接 20 包（scanner 不解析 JSON 配置的 import，图谱以 depends_on 边补记——digest b28）；`packages/tsconfig` 是纯目录约定（无包名无引用，7 个消费者全走相对路径 extends）；`packages/typescript-config` 相反——private:true + publishConfig.access=public 的 npm 发布资产，仓内 demo-agents 经裸包名 extends 它。
- **工具链上游**：nx（任务图）、oxlint/oxfmt（含 jsPlugins 动态加载能力）、tsdown/rolldown（构建）、lefthook（git hooks：pre-commit 6 命令含 check-plugin-skills）、changesets（仅变更单）、@size-limit（体积预算，gzip 口径）、es-check（compat-check 双档：模块 es2022/UMD es2018）。
- **发布下游**：npm（publish-release 用 `npm view` 防降级发布）+ PyPI（detect-py-version-changes.sh 检测 sdk-python 版本变化）+ Notion（release notes 同步）+ Slack（build-release-notification 的 GITHUB_OUTPUT 消费方是 publish-release.yml workflow 的 notify job）。
- **AI 代理接口**：AGENTS.md/CLAUDE.md（代理指令）+ `.mcp.json`（MCP 配置）+ skills/（第 08 篇）——工程化层是"人类 CI"与"AI 代理"的接壤地带。

## 数据流

一次从提交到发布的完整流水：

1. **提交**：lefthook pre-commit 六连（check-binaries/sync-promote-dropdown/sync-lockfile/lint-fix/test-and-check-packages/check-plugin-skills）——lint-fix 只对 staged 文件跑 oxlint/oxfmt 且排除 docs/** 与 .json*；check-plugin-skills 校验技能镜像零漂移（第 08 篇）；
2. **本地开发**：`pnpm dev` → 全量 build → nx watch 增量重建改动包的下游；test 目标 dependsOn ^build 保证测的是新鲜产物（nx 缓存命中则跳过）；
3. **变更单**：开发者写 `.changeset/xxx.md` 记录 semver 意图（人读）；
4. **发布准备**：`release:prepare` → `lib/versions.ts` bump 版本 + 同步 workspace 引用联动 → `generate-ai-release-notes.ts` 调 Anthropic 生成说明 → Notion 同步；
5. **发布执行**：CI 分离 job——无 secrets 的 build/test job + 持 NPM_TOKEN 的 publish job；PyPI 侧 detect-py-version-changes.sh 防重复版本上传；
6. **发布通知**：workflow 结束 → CLI 包装读 env → 纯函数真值表裁决发不发/发什么 → GITHUB_OUTPUT（randomBytes 定界符防注入）→ notify job 拼 Slack 消息；
7. **文档（断链的那条支线）**：typedoc 按 9 个包配置运行 → 全部撞上 ../../typedoc.base.json 不存在的断裂——这条支线当前事实上不可用。

## 设计决策

- **配置即文档**：pnpm-workspace 的 shell-dashboard 注释（`:17-23`）、.oxfmtrc 的 JSON5 防御、no-public-env-shell-read 的盲区清单——把"为什么这样配"写进配置本体，改动者动手前必然撞见理由。
- **自研发布线 vs changesets 全家桶**：只借 changesets 的变更单格式（团队语义习惯），执行链全部自研——因为需要双 registry（npm+PyPI）、最小权限 secrets 分离、Slack/Notion 集成这些 changesets 不覆盖的需求；代价是 ~1500 行脚本要自己维护，收益是每个环节可单测（lib/ 目录纯函数化）。
- **banner hack 是对打包器的防御性编程**：rolldown 的 import 重排对 99% 的代码无害，但对"加载顺序即语义"的 reflect-metadata 是致命的；用 banner 钉死第一行而不是改打包器配置，是承认"工具默认行为不可依赖"的务实姿态。
- **lint 规则防的是真实事故**：cpk: 前缀防组件库污染宿主样式、no-public-env-shell-read 防密钥泄漏进 shell 历史、禁 @a2ui/lit 值导入防 Strict Mode 崩溃——三条规则各对应一次真实事故的预防，且都带"刻意不覆盖盲区"的诚实清单（比假装全覆盖更安全）。
- **typedoc 断链 9 连是"没人用的功能"的证据**：9 个包配置全部指向不存在的基座且无人修复，说明 API 文档生成事实上不在这个团队的日常工作流里——README/skills 才是他们选择的文档形态（第 08 篇的知识分发层）。断链不是 bug 而是优先级的化石。
- **AGENTS/CLAUDE 分叉暴露维护真空**：两份 90% 相同的文件没有单一真源（Nx 注释块各自更新），目录重构后只改了 CLAUDE.md——多份"真理副本"必然漂移，与 skills 镜像的 sync-plugin-skills 方案（有同步器+CI 校验）形成对照组：镜像必须有机器校验，否则就是下一个 AGENTS.md。

## 新人提示

1. **先跑 `pnpm graph`**：nx 依赖图可视化是理解 20 包关系的最快方式；配合第 1 层图谱（pnpm-workspace/nx/tsconfig 节点）交叉阅读。
2. **改构建配置先读注释**：tsdown banner（`runtime/tsdown.config.ts:18-26`）、workspace 排除（`pnpm-workspace.yaml:17-23`）、.oxfmtrc 忽略——每处注释都是前人踩过的坑，删前先懂。
3. **UMD 段加依赖要三处同步**：external 列表、globals 映射、以及确认该依赖在宿主全局真的存在——漏 external 会静默内联（体积翻倍+单例断裂），这是最难在 code review 里发现的一类 bug。
4. **别信 AGENTS.md 的目录描述**（它还在说 v1/v2 子目录）；CLAUDE.md 是对的；最终裁判永远是 `ls packages/`。
5. **发布前本地演练**：`release:prepare:dry` / `release:prerelease:dry` 两个 dry-run scripts 就是为这个准备的；变更单写进 `.changeset/`（人读），版本计算由 lib/versions.ts（可单测）执行。
6. **想给 lint 加自研规则**：抄 no-single-arg-zod-record.mjs（73 行最小完整样本）——meta/create/messages/fix 四件；然后跑表驱动测试（BANNED_KEYS 模式）防规则与文档漂移；规则头注释写清不覆盖的盲区是这个仓的规范。
