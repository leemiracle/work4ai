# 12 · scripts/validate-examples.ts —— schema 样例的合规门禁（构建生成链三部曲收官）

## 1. 角色定位

120 行 TypeScript，图谱 L14「构建生成链与文档站点装配」层，是构建生成链三部曲的收官一环。三部曲的方向各不相同：07 篇 generate-schemas.ts 把 `schema/<v>/schema.ts` 声明**正向编译**成 schema.json（真源→产物），08 篇 render-seps.ts 把 `seps/` markdown **桥接**成文档站页面，本脚本则**反向消费**编译产物——读 schema.json、现场编译成 Ajv 校验器、逐个验证 `schema/<v>/examples/` 下的 JSON 样例是否类型合规。一句话：规范"长什么样"由 schema.ts 定义，"例子是否举对了"由本脚本守门。它还兼管第二件事：把孤儿样例目录（类型已改名/删除后遗留的）判红。

入口在 package.json L36 `check:schema:examples: tsx scripts/validate-examples.ts`，挂进 L33 `check:schema` 四连（ts → json → examples → md）与 L32 `check` 聚合。

**两处勘误（目录与 CI 实证）**：① 它常被称作"CI 门禁"，但 grep `.github/workflows/` 全部 yml 零命中——main.yml 只跑 check:schema:ts（L25）/check:schema:json（L28）/check:schema:md（L31）三步便结束，**没有 examples 这一步**；连 `npm run prep`（package.json L45）也不含它。这个门禁今天只活在 `npm run check` 本地路径上，属荣誉制而非强制（详见外部连接节）。② 样例根目录不是直觉上的根级 `schema/examples/`，而是**按版本分目录** `schema/<version>/examples/<TypeName>/`（CLAUDE.md Schema Examples 节同款约定）——脚本 L50 用 `join(schemaDir, "examples")` 拼的就是这个位置。

## 2. 内部结构：120 行地图

- **L1** `#!/usr/bin/env tsx` 直跑无需预编译。**L3-8** 依赖导入：Ajv 主类与 `ValidateFunction` 类型、`Ajv2020`（`ajv/dist/2020`，2020-12 方言实现）、`addFormats`（补 `format` 关键字校验）、`Dirent`、`readFile`/`readdir`、`join`。
- **L10** `type ValidationResult = [name: string, errors: Promise<string[]>]`——错误以 **Promise 形态存进元组**（见设计决策）。
- **L15-29** `validateExample()`：L20 读文件并 `JSON.parse`——解析失败落 L26-28 catch，坏 JSON 本身就构成一条错误；L22 同步执行 `validate`；L23-25 把 Ajv 的 errors 映射成 `` `${err.instancePath || "/"}: ${err.message}` `` 单行文案——instancePath 直接指向样例里出错的字段层级。
- **L31-84** `validateSchemaExamples(schemaDir)`，每版本一实例，依次：
  - L36-38 读该版本 `schema.json`；
  - L40 **方言自检测**：`schema.$schema.includes("2020-12")`——从产物自身的 `$schema` 字段判断方言，而非硬编码版本清单（与 generate-schemas.ts L11/L14 的硬编码分代形成鲜明对照）；
  - L42-44 按方言选编译器：is2020 走 L43 `Ajv2020`，否则 L44 经典 `Ajv`，共同配置 `{ allErrors: true, strict: false }`（收集全部错误、容忍非标准关键字）；L45 `addFormats`；
  - L47-48 `defsKey = is2020 ? "$defs" : "definitions"`——双方言键名兼容，恰好镜像 generate-schemas.ts L35-38 的 `definitions` → `$defs` 后处理改名；
  - L50-55 读 `examples/` 目录，**目录不存在即静默通过**（L53 readdir 抛错 → L54-55 catch 返回空结果）；
  - L58-81 双层循环：外层遍历类型目录（L59 跳过非目录项），L60 取目录名即 typeName；L64 查 `defs?.[typeName]` 命中后 L65-69 **现场编译该类型的专属校验器**——拼 `{$schema, [defsKey]: 全量 defs, ...defs[typeName]}` 为新根 schema 再 `ajv.compile`，让样例直接对着类型本体校验、又保留全量 defs 供跨类型 `$ref` 解析；未命中则 validate 保持 undefined；
  - 内层 L72-80 遍历文件：L73 只认 `.json` 后缀；L75-76 有校验器则真验，L77-78 没有则推入合成错误 `Type "${typeName}" not found in schema`——**孤儿目录检测**。
- **L86-118** `main()`：L90-92 **动态发现** `schema/` 下全部子目录（不列版本清单，未来新增版本目录自动纳入校验范围）；L95 `Promise.all` 并行各版本再 flat；L97-113 汇报相——L102 逐条 `await errorsPromise`（并行验证、顺序输出），L104/L107 打 ✓/✗ 并计数；L115 汇总行；L117 `failed > 0` 即 `process.exit(1)`——**退出码就是门禁信号**。L120 裸调 `main()`，**无顶层 catch**（对照 generate-schemas.ts L145-148 的兜底仪式）。

## 3. 外部连接

**上游产物**：六版本 `schema.json`（07 篇编译产物）。实证盘点（本仓快照）：仅 **2026-07-28 与 draft 两版本有 examples**——各 88 个类型目录 / 129 个样例文件，且 `diff -rq` 字节级完全一致（cut-release 复制 draft 为新日期目录时连带复制，两者都是真实目录非 symlink）；老四版本（2024-11-05、2025-03-26、2025-06-18、2025-11-25）**没有 examples 目录**，全部走 L54-55 静默通过——"校验六版本"是机制潜能，当下实际受验的只有两版本。

**样例对账**（draft 实测）：schema.json 含 155 个 `$defs`，examples 覆盖 88 类型（67 类型无样例），孤儿目录 0 个。覆盖是选择性的：错误码与核心请求/响应优先——CallToolResult 有 4 个样例（含正反例 `invalid-tool-input-error.json`），ClientCapabilities 多达 7 个。

**文档链上游（样例的第二生命）**：样例不止被校验，还被**引用进规范正文**——`schema/draft/schema.ts` 有 126 处 `@includeCode` JSDoc 标记（如 L324 `{@includeCode ./examples/ParseError/invalid-json.json}`），typedoc（package.json L27 生成链）渲染时把样例内容内嵌进 schema.mdx。一份数据两处消费：本脚本保证它合规，typedoc 保证它被读者看见。

**npm 钩子**：L36 定义、L33 挂四连、L32 进聚合。**不在 L45 prep**——prep = check:schema:ts + generate + check:docs + check:seps + format，用 generate 重生成代替了 json/md 漂移检查，但 examples 校验验的是**人写的样例**而非产物，无"重生成"等价物，却也未被纳入 prep，属覆盖缺口。依赖在 devDependencies（L47 块）：L49 `ajv ^8.20.0`、L50 `ajv-formats ^3.0.1`——`^` 语义化范围，与 07 篇 typescript-json-schema 精确锁 0.68.0 形成对照：编译器行为变化会改写产物必须锁死，校验器行为面窄可放宽。

**CI 现状（勘误核心）**：main.yml（push main + 全部 PR 触发）L25/L28/L31 三步后**戛然而止**；其余 workflow 亦不触达——cut-release.yml L136 只跑 `npm run generate`（L24：schema json+mdx 与 seps 再生），render-seps/sep-lifecycle 各管各的。样例合规目前唯一防线是贡献者自觉跑 `npm run check`——而 CLAUDE.md 的官方指引"push 前跑 npm run prep"恰好绕开了这一步。若上游意图是 CI 强制，修法很便宜：main.yml L31 后补一行 `npm run check:schema:examples`。

## 4. 数据流：一个样例从落盘到过闸

1. 工程师在 `schema/draft/examples/NewType/basic.json` 写样例，并在 schema.ts 对应类型 JSDoc 里加 `@includeCode` 引用。
2. 本地 `npm run check` → L32 → L33 → L36 → tsx 启动本脚本（cwd 为仓根，L90 的相对路径 `"schema"` 依赖 npm script 保证）。
3. L90 发现六个版本目录 → 老四版本 L53 readdir 失败静默跳过 → 2026-07-28 与 draft 各自走编译校验全流程。
4. draft 分支：L40 读到 `$schema` 含 "2020-12" → L43 Ajv2020 + L47 `$defs` 键 → NewType 目录在 defs 命中 → L65-69 现场编译 → L20 读 basic.json → L22 校验。
5. 三种红法：JSON 语法坏（L26-28 原样返回解析错误）；类型不合规（L23-25 列出 instancePath 级错误明细）；目录名在 defs 查无（L78 合成 `Type not found` 错误）。
6. L102-112 逐条汇报 ✓/✗，任一红 → L117 exit 1，npm script 非零退出，门禁落下。
7. 绿样例的另一生命：typedoc 经 @includeCode 把同一文件嵌进 `docs/specification/draft/schema.mdx`，成为规范正文的一部分。

## 5. 设计决策

**按类型现场编译（L65-69）而非编译全量 schema 再走 `$ref`**：把类型本体摊平为根 schema（`...defs[typeName]` 在 spread 末位）并携带全量 defs 作 `$ref` 上下文——样例直接对类型本体校验，错误路径落在真实字段上而非 ref 包装层，也免去为每个样例写 `{"$ref": "#/$defs/Type"}` 壳。理论边界：spread 在后意味着类型 def 若自带 `$schema`/`$defs` 键会覆盖注入值（现网 155 个 defs 无此形态，纯理论风险）。

**方言自检测 vs 硬编码分代**：07 篇编译器靠硬编码版本清单（L11/L14）决定谁吃 2020-12 后处理；本脚本不信清单、只信产物自身的 `$schema` 字段（L40）——校验器与生成器解耦，schema.json 换方言不需要动本脚本。代价是经典 Ajv 分支（L44）当下为死路径：有 examples 的两版本都是 2020-12 方言，draft-07 支路是为"未来有人给老版本补样例"预付的休眠代码。

**静默跳过无 examples 的版本（L54-55）**：门禁只对"承诺了样例的版本"生效——历史版本没写样例不算失败，这是对冻结契约的正确姿态。但有副作用：**忘建 examples 目录 = 零校验零报错**，新增版本若漏建目录，门禁无声放行而非提醒——"没有样例"与"样例全坏"在该设计下等价沉默。

**Promise 元组（L10/L76/L102）**：验证在循环内即发即走（push 不 await），汇报阶段统一 await——文件 IO 并发、输出顺序稳定。实况是 Ajv validate 同步、样例文件都是几百字节，该并行收益趋零，更多是"能并发就并发"的惯例；代价是 `[name, Promise<string[]>]` 签名的可读性折扣。

**退出码即门禁、无兜底 catch**：L117 `exit(1)` 是给 npm/CI 的唯一信号；L120 裸调无 try-catch，意外异常靠 Node unhandled rejection 非零退出兜住——效果等价、栈信息不如 07 篇 L145-148 友好，120 行小工具省掉仪式感代码是合理取舍。

## 6. 新人提示

- **新增样例三步**：建 `schema/draft/examples/<TypeName>/<slug>.json`（目录名必须**精确等于** schema.json 的 `$defs` 键，大小写敏感；slug 自由命名，见 CallToolResult 的 4 文件命名法）→ 想进文档就在 schema.ts 对应类型 JSDoc 加 `{@includeCode ./examples/<Type>/<file>.json}`（参照 schema.ts L324）→ 跑 `npm run check:schema:examples` 本地过闸。**别指望 CI 兜底**——main.yml 没有这一步（本篇勘误①），样例写坏推上仓库不会变红。
- **排错读法**：`/message: must be string` 的 `/` 前缀即 instancePath，直接指向出错字段层级；`Type "X" not found in schema` 则是目录名拼错或该类型已在 schema.ts 里改名——两种红法的修法完全不同。
- **版本纪律**：日常只在 draft 维护样例；发布时 cut-release 复制 draft 为新日期目录（2026-07-28 与 draft 的字节级一致即此来历），老四版本不补样例——它们是冻结契约。
- **改 dialect 相关逻辑时**：L40/L43/L44/L47 四处是方言联动组，改一处查三处；`$defs`/`definitions` 双键兼容必须与 generate-schemas.ts L35-38 的后处理改名保持镜像，否则老方言版本一旦补样例即断。
- **本地必跑清单**：CLAUDE.md 指引的 `npm run prep` 不含 examples 校验（覆盖缺口），写完样例自觉补 `npm run check` 或单独跑 `npm run check:schema:examples`——这是当前仓库里该门禁的唯一触发方式。

> 非空白字符 6332 / 锚 102（覆盖 validate-examples.ts / package.json / main.yml / cut-release.yml / schema.ts / generate-schemas.ts（经 07 篇已核锚）/ examples 目录实测，全部源码逐条核实）
