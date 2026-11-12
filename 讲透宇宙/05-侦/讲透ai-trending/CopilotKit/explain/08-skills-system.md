# 08 · skills 体系：双层镜像结构与快照漂移的考古地层

## 角色定位（16 层架构中位置）

skills 体系横跨图谱两处：第 15 层「CopilotKit 技能资产」（根 `skills/` 下 8 个独立 lifecycle 技能）与三个包内镜像位（第 7 层「runtime 知识镜像」、第 10 层「react-core 知识镜像」、第 12 层 a2ui 层的 `packages/a2ui-renderer/skills/`）。它不是运行时代码——零 npm 消费者——而是**面向 AI 编码代理的知识分发层**：每个 skill 是一份 SKILL.md + references/ 参考文档 + 可选 eval.yaml 评测与 assets/ 模板的集合，通过 `.claude-plugin/plugin.json`（Claude Code plugin 清单）对外发布为 marketplace 条目。生成与漂移检测由 `scripts/sync-plugin-skills.ts`（第 16 层工具链）驱动，挂进 lefthook pre-commit（`lefthook.yml:90-96`，glob 覆盖三组镜像与 `.claude-plugin/**`）。

一句话：这是仓库"教 AI 用 CopilotKit"的教材库，教材有两套存档（源+镜像），而教材内容本身带着历史地层。

## 内部结构（关键文件+行号锚拆解）

### 双层结构：8 独立 + 3 镜像

根 `skills/` 共 11 个目录，分两类：

**8 个独立 lifecycle skill**——由 `RESERVED_LIFECYCLE_SLUGS` 钉版（`scripts/sync-plugin-skills.ts:9-19`）：copilotkit-setup / copilotkit-develop / copilotkit-agui / copilotkit-integrations / copilotkit-debug / copilotkit-upgrade / copilotkit-contribute / copilotkit-self-update。它们**不**从 packages 生成，免除孤儿检测（注释原文 `sync-plugin-skills.ts:10`）。内容形态各异：copilotkit-setup 最全（SKILL.md + references 3 篇 + assets 3 模板 + eval.yaml）；copilotkit-self-update 最小（仅 SKILL.md，零项目内引用的自含教程）；copilotkit-agui 带 4 篇 references（building-agents / client-sdk / event-flow-diagrams / protocol-spec）。

**3 组镜像 skill**——源头在包内 `packages/<pkg>/skills/<slug>/`，根 `skills/<slug>/` 是同步产物：`packages/runtime/skills/runtime` → `skills/runtime`（17 篇 references，含 agent-runners 四部曲与 wiring 外部框架系列）、`packages/react-core/skills/react-core` → `skills/react-core`（references 6 篇）、`packages/a2ui-renderer/skills/a2ui-renderer` → `skills/a2ui-renderer`（仅 SKILL.md）。镜像经 `diff -r` 逐字节验证与源相同（a2ui/react-core/runtime 三组全部 identical）。

### 同步器 sync-plugin-skills.ts（251 行）

- **源发现**：`findPackageSkills` 扫 `packages/*/skills/*`（`sync-plugin-skills.ts:49-68`）；
- **命名冲突防线**：包 skill slug 撞上保留名直接报错（`sync-plugin-skills.ts:91-99`，"collides with reserved lifecycle slug. Rename the package skill."）——保证镜像域与 lifecycle 域永不相交；
- **write/check 双模式**（`SyncMode`，`:26`）：write 逐文件 `writeFile`（`:120-123`）并**清除孤儿**（`:183-189` 的 `rm recursive`）；check 只比对字节差异（`:112-119`）；
- **孤儿检测双层**：文件级（mirror 有而 source 无，`:127-134`）+ 目录级（source 包整体被删，`:137-151` 全目录扫描，主循环覆盖不到的场景注释写明 `:137-139`）；
- **退出码语义**：`exitCode: 0 | 1 | 2`（`:34`）——0 干净（"plugin skill mirror in sync"，`:160`）、1 漂移（changed/orphans/versionDrift 任一非空，`:176-179`）、2 保留给冲突错误（`:93-98` 的早返回）；
- **版本同步**：`VERSION_SOURCE_PACKAGE_JSON = "packages/runtime/package.json"`（`:22`）→ 写入 `.claude-plugin/plugin.json` 与 `marketplace.json`（`:23-24`，`handleVersionSync` 调用点 `:154`）——plugin 版本永远追随 runtime 包版本。

### 活样本：版本漂移现场

`.claude-plugin/plugin.json` 的 `"version": "1.58.0"` vs `packages/runtime/package.json` 的 `"version": "1.59.5"`——本仓库快照本身处于 check 模式会报 `version drift` 的状态，跑 `pnpm check:plugin-skills`（`package.json:35`）即可复现；修复命令 `pnpm sync:plugin-skills`（`package.json:36`，漂移输出里也自带此提示 `:178`）。

### 文档目录快照漂移（三层地层）

skills 文档是某历史时点的仓库快照，与现行目录结构存在系统性错位，考古价值极高：

1. **第一层：packages/v2 目录已消亡**。`skills/copilotkit-develop/sources.md:7-18` 的 43 条路径全部以 `packages/v2/react/src/...` 开头（use-frontend-tool.tsx、use-agent.tsx 等 hooks 清单），该目录 `ls` 实证不存在。机械迁移规则：`packages/v2/react/src` → `packages/react-core/src/v2`（chat 组件 kebab-case 同步改 PascalCase：copilot-chat.tsx → CopilotChat.tsx）；`packages/v2/runtime/src` → `packages/runtime/src/v2/runtime`（transcription 目录改名 transcription-service）；`packages/v2/agent/src` → `packages/runtime/src/agent`（agent 包已并入 runtime）。5 条死引用无映射（labels.ts、slot.ts 等已并入大文件）。
2. **第二层：包名代差**。`skills/copilotkit-contribute/references/pr-guidelines.md` 结尾仍指引 "New features go in packages/v2/"；`skills/copilotkit-upgrade/SKILL.md` 的依赖映射表（L63-69）声称 react-core/react-ui 将合并为 `@copilotkit/react`、sdk-js 变 `@copilotkit/agent`——但这两个包名在仓内 20 个 package.json 中零定义（grep 实证），合并从未发生，文档超前描述了未来发布状态。
3. **第三层：混淆占位符**。`skills/copilotkit-contribute/SKILL.md` L12 与 L62 两处 namespace 标注写重——"internal v2 packages use the @copilotkit/* namespace. The public API that users install is @copilotkit/*"，前后两个名字相同，系模板替换失败的自曝。

### eval.yaml 与 SKILL.md v1.1.2 的自相矛盾（判 0 分问题）

`skills/copilotkit-setup/SKILL.md` frontmatter `version: 1.1.2`，教学内容是**现行正确**的：装 `@copilotkit/react-core @copilotkit/runtime hono`（`SKILL.md:52`）、用 `createCopilotHonoHandler`（`SKILL.md:80-108`，两代端点工厂的正确现代名）、引 `@copilotkit/react-core/v2/styles.css`（`SKILL.md:232`）。但同目录 `eval.yaml` 的 deterministic grader 检查的全是**旧代**：任务 instruction 要求装 `@copilotkit/react, @copilotkit/core`（`eval.yaml:23-24` 附近）、grader 用 `jq -e '.dependencies["@copilotkit/react"]'` 判分、检查 `@copilotkit/react/styles.css`（`eval.yaml:100/174`）、且要求 deprecated 别名 `createCopilotEndpoint`（`eval.yaml:22`、`:99`）。**按 SKILL.md v1.1.2 指引完成的任务会被自家 eval 判 0 分**——教程与考卷来自两个年代。另有 `workspace: vite-react` 悬空目录引用。

### publicApiKey 主字段三证（skills 文档反向）

`skills/react-core/SKILL.md:91` 声称 "publicLicenseKey is canonical. publicApiKey is a deprecated alias"——**与源码相反**。三证钉版：

1. `packages/react-core/src/v2/providers/CopilotKitProvider.tsx:102` —— `publicApiKey?: string;` 是主字段声明（JSDoc "The Copilot Cloud public API key."）；
2. `CopilotKitProvider.tsx:106` —— `publicLicenseKey?: string;` 的 JSDoc 自述 "Alias for `publicApiKey`"（`:104`）；
3. `CopilotKitProvider.tsx:380` —— 解析顺序 `const resolvedPublicKey = publicApiKey ?? publicLicenseKey;`，publicApiKey 优先。

有趣的是 `skills/runtime/SKILL.md`（L58 附近 Invariants 节）持相反立场："publicLicenseKey 为 canonical、publicApiKey 为 deprecated 别名"——两个 skill 对同一字段各说各话，只有源码是裁判。

## 外部连接（imports 边上下游）

- **上游（被同步）**：packages/runtime、packages/react-core、packages/a2ui-renderer 三个包的 skills/ 源目录是镜像的唯一真源；
- **下游（分发面）**：`.claude-plugin/plugin.json`（Claude Code plugin）+ `.claude-plugin/marketplace.json`（marketplace 名 copilotkit-plugins，skills 条目清单）；版本号从 runtime 包单向流出（`sync-plugin-skills.ts:22`）；
- **CI 链**：lefthook pre-commit 的 check-plugin-skills job（`lefthook.yml:90-96`）在 `packages/*/skills/**`、三组根镜像、`.claude-plugin/**` 任一变动时强制重新同步；
- **文档引用习惯**：lifecycle skills 之间显式互引（copilotkit-contribute 引 `../copilotkit-debug/SKILL.md` 的 MCP 配置节、copilotkit-debug 引 `.mcp.json`）；镜像 skill 与包内源按图谱规则**不发**同主题互引边（防重复计数）；
- **裁剪边界**：skills 文档引用的 examples/、docs/、showcase/ 目录不在扫描集，相关引用无图边——文档层的上下文完整性高于图谱覆盖。

## 数据流

教材生产与分发链：

1. **源撰写**：包维护者在 `packages/runtime/skills/runtime/` 写 SKILL.md 与 references（frontmatter `sources:` 列出锚定的真实源文件，如 runtime skill 的 14 条全部经磁盘验证存在）；
2. **提交拦截**：lefthook pre-commit 触发 `check-plugin-skills`（改动文件命中 glob 时）；
3. **同步**：`pnpm sync:plugin-skills` 逐字节复制到根 `skills/<slug>/`、prune 孤儿、把 runtime 版本写进 plugin.json/marketplace.json；
4. **分发**：用户（或 AI 代理宿主）通过 Claude Code marketplace 安装 plugin，lifecycle skills（setup/develop/debug 等 8 个）直接来自根 skills/，镜像 skills（runtime/react-core/a2ui-renderer）与包发布渠道双轨可达；
5. **消费**：AI 编码代理按 SKILL.md 的触发条件（frontmatter description）加载对应技能，读 references 获取带行号锚的源码指引，按 eval.yaml 在 Docker 沙箱（`base: node:20-slim`，eval.yaml defaults）跑 15 任务评测——评测链与教程链当前因包名代差互斥（见上）。

## 设计决策

- **为什么镜像而不是引用**：包内 skills 随 npm 包发布（开发者装包即可获得配套技能），根 skills/ 服务 plugin marketplace（不装包的 AI 代理也能用）——同一内容两个受众，同步器以字节级一致换双渠道分发，check 模式把一致性变成 CI 可执行约束。
- **保留名机制防止域名劫持**：lifecycle slug 与包 slug 的碰撞检查（`:91-99`）保证语义分层——"教你怎么装 CopilotKit"（lifecycle）与"讲某个包内部"（镜像）永不在同一命名空间打架。
- **版本锚定 runtime 而非根 package.json**：plugin 版本跟随 runtime 包（`:22` 注释 "plugin version tracks this package's version"），因为 skills 内容（尤其 runtime skill）的准确性以 runtime 版本为基准。
- **快照漂移是接受的代价而非 bug**：skills 文档生成于特定时点（多处 library_version: 1.56.2 vs 当前 1.59.5），官方选择"定期再生成"而非"实时联动"——代价是 packages/v2 时代地层被完整封存，反而为考古者提供了重构时间线的证据（2026-03 前后存在一次 v1/v2 目录大扁平化）。
- **eval 教程脱钩暴露流程缺口**：setup 的 SKILL.md 已升到 v1.1.2 新 API 而 eval.yaml 仍检旧包名，说明 eval 与教程没有同一审校管道——若有人在 CI 里启用该 eval，会得到"教程全错"的假阴性。

## 新人提示

1. **改 skills 先找真源**：改根 `skills/runtime/` 会被下次同步覆盖——lifecycle 8 个直接改根目录，镜像 3 个必须改 `packages/*/skills/` 再 `pnpm sync:plugin-skills`；
2. **读 skills 文档先做年代鉴定**：见到 `packages/v2/`、`@copilotkit/react`、`@copilotkit/agent`、`createCopilotEndpoint` 四个标志任一，即知该段是旧地层，按上文机械迁移规则换算到现行路径，再以源码为准；
3. **publicApiKey/publicLicenseKey 以源码为准**：`CopilotKitProvider.tsx:380` 的解析顺序是最终事实，两个 SKILL.md 的相反说法都别信；
4. **别用 setup 的 eval.yaml 验收**：它会把正确答案判 0 分；想跑评测先手工把包名换成 react-core/runtime 系；
5. **新增包内 skill 的 checklist**：slug 避开 8 个保留名 → 写 frontmatter（name/description/version/sources）→ 跑 `pnpm check:plugin-skills` 确认 mirror 待生成 → `pnpm sync:plugin-skills` → 提交时 lefthook 自动把关；
6. **skills 是理解本仓演进史的最佳入口**：sources.md 的死路径清单 = 目录重构前的仓库存档；对照 `git log --diff-filter=R` 可还原整个扁平化过程。
