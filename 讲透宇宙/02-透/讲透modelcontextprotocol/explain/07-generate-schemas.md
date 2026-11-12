# 07 · scripts/generate-schemas.ts —— schema 真源机制的编译器

## 1. 角色定位

本文件是知识图谱 L14「构建生成链与文档站点装配」层（20 节点）的核心 `file:` 节点：148 行的 TypeScript 脚本，把 `schema/<version>/schema.ts` 声明编译成机器可消费的 `schema.json`。MCP 规范仓的宪法是「TS 声明是 source of truth」——CLAUDE.md 的 Schema Generation 节明确要求 *Edit schema.ts → npm run generate:schema → Always regenerate after editing*，而这条宪法的执行者就是本脚本。它不做 mdx 渲染（那由 package.json L27 的 typedoc 链完成），只负责 JSON 一翼，但 JSON 是 SDK、校验器、IDE 补全共同消费的规范正本。

批分析在图谱中为本节点实证了 **12 条 depends_on 读写边**：对六版本各读 `schema/<v>/schema.ts`、各写 `schema/<v>/schema.json`（六读六写，如 `file:scripts/generate-schemas.ts -> file:schema/2025-11-25/schema.ts` 与 `-> config:schema/2025-11-25/schema.json`），另有 3 条 contains 边（三个函数）与来自 `config:package.json`、`config:.github/workflows/main.yml` 的 depends_on 入边——CI 的「Check schema.json files are up to date」步（main.yml L28）直接调用本脚本的 `--check` 模式。

## 2. 内部结构：148 行地图

- **L1** `#!/usr/bin/env tsx`：tsx 直跑，无需预编译。
- **L11/L14** 版本清单分代：`LEGACY_SCHEMAS = ['2024-11-05', '2025-03-26', '2025-06-18']`（保持 JSON Schema draft-07）；`MODERN_SCHEMAS = ['2025-11-25', '2026-07-28', 'draft']`（升 2020-12）。**L17** 合成 `ALL_SCHEMAS` 六版本，驱动全循环。
- **L20** `CHECK_MODE = process.argv.includes('--check')`：同一脚本双态——生成态与校验态。
- **L25-47** `applyJsonSchema202012Transformations()`：对已落盘 JSON 做三段正则替换——L29-32 把 `$schema` 从 `http://json-schema.org/draft-07/schema#` 换成 `https://json-schema.org/draft/2020-12/schema`；L35-38 把 `"definitions":` 换 `"$defs":`；L41-44 把引用 `#/definitions/` 换 `#/$defs/`。即 2020-12 化是**后处理文本手术**，不是编译器原生输出。
- **L52-110** `generateSchema(version, check)`：L53-55 拼出 `schema/<v>/` 三件套路径；生成态 L94-96 调 `npx typescript-json-schema --defaultNumberType integer --required --skipLibCheck "<schema.ts>" "*" -o "<schema.json>"`；L103-105 仅非 LEGACY 版本走后处理。校验态（L57-90）则不带 `-o` 让编译器吐 stdout，在内存里对非 LEGACY 做 L70-77 同款替换，再与盘上文件 **L80** `trim()` 后全字符串比对，不一致即 L81 报 `Schema ${version} is out of date!`。
- **L115-143** `main()`：两态都用 `Promise.all` 并行六版本（L119-121 / L135-137）；校验态任一失败则 L127 提示 `Run: npm run generate:schema:json` 并 L128 `exit(1)`；生成态收尾 L140-141 打印两代清单。
- **L145-148** 顶层 catch 兜底，失败即退出码 1。

`"*"` 传参让编译器导出 schema.ts 的**全部导出符号**；三参数里 `--required` 只把无 `?` 的属性收进 required 数组、`--skipLibCheck` 跳过依赖库类型检查、`--defaultNumberType integer` 把裸 `number` 映射为 integer 语义。

## 3. 外部连接

**上游（L09 层六版本 schema.ts）**：六份声明文件是真源输入，draft 版随 SEP 演进（schema/2025-11-25/schema.ts 达 2582 行，其 L14-15 `LATEST_PROTOCOL_VERSION = "2025-11-25"` 为协议版本常量）。

**下游**：① `schema/<v>/schema.json`（图谱 config: 节点，六份）；② 经 typedoc 链的 `docs/specification/<v>/schema.mdx`（document: 节点）。**勘误：`schema/<v>/schema.mdx` 是模板不是产物**——145 行骨架，只含 `{/* @category X */}` 占位标记；产物是 docs/ 下那份 1242 行成品。typedoc.plugin.mjs L19-24 自定义 `schemaPageTemplate` 选项、L26 注册 `schema-page` 输出，typedoc 读模板、按 category 标记注入类型渲染 HTML。

**伴生脚本**：`validate-examples.ts`（check:schema:examples，package.json L36）拿生成的 JSON 校验 examples/ 目录；`check-mdx-comments.ts`（L40）管 mdx 注释卫生；`check:schema:md`（L37）用 `cmp` 逐版本比对 mdx 产物是否新鲜。`typescript-json-schema` 锁死 `0.68.0` 精确版本（package.json L62）——编译器行为变化会直接改写产物，锁版保证可复现。

## 4. 数据流：从改一行到规范站发布

1. 工程师编辑 `schema/draft/schema.ts`（tsc --noEmit 由 check:schema:ts 兜底，package.json L34）。
2. `npm run generate:schema:json`（L26）→ 本脚本并行六版本：编译 draft 版 → 后处理 2020-12 化 → 落盘。
3. 同一条 `generate:schema`（L25，`&` + `wait` 并联两子任务）触发 `generate:schema:md`（L27）：find 遍历六份模板，typedoc 渲染出 docs/specification/<v>/schema.mdx。
4. `npm run check`（L32-33）四连：TS 静态检查 → 本脚本 `--check` 比对 JSON → examples 校验 → mdx 比对。
5. PR 推上 GitHub，main.yml L25/L28/L31 三步在 CI 复跑同款检查；cut-release 工作流在出版时再次 `npm run generate`（cut-release.yml L133-136，注释明言 schema.json/schema.mdx 由 schema.ts 再生）并冻结为带日期的新版本目录。
6. Mintlify 站点发布 schema.mdx 成品；SDK 作者从 schema.json 生成客户端类型。真源唯一，漂移在每一道闸口被拦截。

## 5. 设计决策

**为何 TS 当真源**：手写 JSON 无类型检查器兜底，`$ref` 指错、required 漏写都是静默漂移；TS 声明享受 tsc+eslint+prettier 三重基建（L34），编译产物必然与声明一致。代价是引入 `--required` 的语义近似：实证 schema/2025-11-25/schema.json 的 145 个 defs 中 102 个带 required（如 JSONRPCErrorResponse 的 `required: ['error', 'jsonrpc']`，`id?` 被豁免），Result 类型全 optional 故无 required 键；additionalProperties 仅 2 处——生成器不默认封死额外字段，宽松度靠 TS 侧手工控制。

**为何方言分代而非全量升级**：已发布版本的 JSON 是外部世界已消费的契约，draft-07 的 `definitions` 字面量被无数 `$ref` 引用；强行统一会破坏老 SDK。2020-12 的收益（`$defs` 规范化、`unevaluatedProperties` 等）只给新版本（2025-11-25 起）享受。后处理手术（L29-44）而非换编译器，是因为 typescript-json-schema 0.68 只输出 draft-07——这是工具限制倒逼出的最短路径。

**--check 与生成同脚本**：单一真相入口，CI 校验与本地生成不可能使用不同逻辑；`Promise.all` 并行六版本把等待压到最慢一份的编译时长。

## 6. 新人提示

- **改 schema 后忘 regenerate**：本地无感，PR 的 CI 在 main.yml L28「Check schema.json files are up to date」一步变红——本脚本 `--check` 比对盘上 JSON 与内存重编结果，一个字符差即 exit 1。修复永远是回本地跑 `npm run generate:schema:json` 提交产物，而非手改 JSON。
- **`npm run generate` 与 `prep` 的关系**：generate（L24）= schema JSON+mdx 再生 + SEPs 渲染；prep（L45）= 先 check:schema:ts 再 generate 再 check:docs/check:seps 再 format——是提交前的全量仪式，CLAUDE.md 要求 push/PR 前零警告通过。
- **六版本都要改吗**：不用。已发布五版本是冻结契约，日常只改 `schema/draft/schema.ts`；版本镜像发生在 cut-release 出版流程（复制 draft 为新日期目录后统一再生成），不靠人肉同步。
- 改了 schema.ts 里的 JSDoc 描述也会改 JSON——描述文本进 `description` 字段，同样触发 CI 漂移红。
- 别直接编辑 `schema/<v>/schema.json`：它是纯产物，下一次 generate 会无声覆盖你的修改。

---

> 非空白字符 4540 / 锚 49（L 锚出现次数；覆盖 generate-schemas.ts / package.json / main.yml / cut-release.yml / typedoc.plugin.mjs / schema.ts / schema.json 各版本头部，全部源码逐条核实）
