# 09 · a2ui-renderer：A2UI 协议的 React 渲染端与 v0.8→v0.9 迁移地层

## 角色定位（16 层架构中位置）

a2ui-renderer（`packages/a2ui-renderer`）在图谱第 12 层「a2ui 生成式 UI 渲染器」，与根 `skills/a2ui-renderer` 镜像同层。它是 A2UI 协议（Google 主导的 declarative UI 规范，`a2ui.org`）在本仓的 React 实现：上游接 LLM 流式输出的 A2UI 数据模型（LLM 在工具参数里产出结构化组件树 JSON），下游把组件树增量渲染成真实 React DOM。它在链路中的位置是——runtime 的 A2UI middleware（`packages/sdk-js/src/langgraph/middleware.ts` 的 generate_a2ui 工具）产出数据 → 前端 `react-core/src/v2/a2ui/` 的 A2UIMessageRenderer 接收 → 本包 A2uiSurface/A2UIRenderer 负责真正的组件树 diff 渲染。包本身 Apache 2.0 许可（`src/react-renderer/a2ui-react/` 文件头 Copyright 2025/2026 Google LLC），从 Google A2UI 项目 vendored 而来再行改造。

一句话：LLM 画图纸（组件树 JSON），这个包是施工队（React 渲染引擎）。

## 内部结构（关键文件+行号锚拆解）

**包根三件**：`src/index.ts` 是唯一发布入口（package.json exports 仅 `.` 与 `./package.json`）——`export * from "./react-renderer/index.js"`（`index.ts:17`）加 `DEFAULT_SURFACE_ID`（`:18`）；尾部的 `export const viewerTheme: Record<string, unknown> = {};`（`index.ts:22`）带注释 "Backward compat: viewerTheme (v0.9 themes handled internally)"（`:21`）——真实主题数据在 `src/theme/viewer-theme.ts`（443 行纯数据常量），但主线入口已不引用它。`src/a2ui-types.ts` 定义 Theme/A2UIClientEventMessage 等协议类型。

### A2uiSurface：增量渲染核心（react-renderer/a2ui-react/）

`A2uiSurface.tsx` 是 vendored A2UI React 内核的心脏：

- **快照身份方案**：`getSnapshot` 返回 `${comp.type}-${version}`（`A2uiSurface.tsx:100`，注释 `:98-99` 自述 "We use instance identity + version as the snapshot"）——version 是本地计数器，每次模型更新 `version++`（`:76-87` 两处）。这样设计使 **Button→Text 这类类型替换**（实例换了、内容可能相同）也能触发重渲染，因为 type 进了快照字符串。
- **订阅**：`useSyncExternalStore(store.subscribe, store.getSnapshot)`（`A2uiSurface.tsx:105`，import 见 `:17`）——React 18 并发安全的增量渲染入口，避免整树重挂载。
- **shimmer 骨架**：加载态用内联样式 `animation: "a2ui-shimmer 1.5s ease-in-out infinite"`（`:118`）+ 现场注入的 `<style>{'@keyframes a2ui-shimmer ...'}</style>`（`:122`）——keyframes 不入 CSS 文件而是组件内联，保证零样式依赖可移植。

### adapter.tsx：双工厂

- `createReactComponent<Api extends ComponentApi>`（`adapter.tsx:50`）——正规工厂：以 `useRef` 持有 `GenericBinder`（来自 `@a2ui/web_core/v0_9`，import 见 `:24`）；context 引用变化时 `dispose()` 旧 binder 再重建（`:79-85`），卸载时清理（`:102` `return () => binding.dispose()`）防订阅泄漏。
- `createBinderlessComponent`（`adapter.tsx:124`）——第二工厂：跳过数据绑定层的裸组件，给无需 schema 绑定的简单组件用。memo 比较器只比较 props 引用、`componentModel.id`、`dataContext.path` 三个轴（digest b1 钉版）。

### catalog 双目录对照：basic vs minimal

`catalog/basic/` 与 `catalog/minimal/` 是同一规范的两个实现档位：

| 维度 | basic | minimal |
|---|---|---|
| 目录组件文件 | 19 个（含 ChildList.tsx） | 6 个（含 ChildList.tsx） |
| catalog 实际注册 | **18 个**（`basic/index.ts:21-38` import 清单无 ChildList） | **5 个**（`minimal/index.ts:24-30` 数组：Text/Button/Row/Column/TextField，ChildList 同样未入列） |
| schema 来源 | 集中式 `Api`（`@a2ui/web_core` 的 basic_catalog 规范），`BASIC_FUNCTIONS` 直接从 `@a2ui/web_core/v0_9/basic_catalog` 导入（`basic/index.ts:18`） | 内联 zod（每个组件文件自带 `z.object` schema，CommonSchemas 复用） |
| 规范 URL | `https://a2ui.org/specification/v0_9/basic_catalog.json`（`basic/index.ts:62`） | `https://a2ui.org/specification/v0_9/catalogs/minimal/minimal_catalog.json`（`minimal/index.ts:35`） |
| 样式工具 | 依赖 utils.ts | 就地复制不依赖（自包含模式） |

甄别注：任务书"basic 18 组件 / minimal 5 组件"经核实是 **catalog 注册数**；目录文件数实为 19/6，多出的都是 ChildList.tsx（存在但未注册进 catalog 的孤儿组件）。basic 目录深嵌套 schema 有两个组件（ChoicePicker、Tabs）`z.infer` 推断失效，源码以 `any` 兜底并留作者注释自认（digest b1）。

minimal 目录的名实不符彩蛋：名为 `capitalize` 的函数实现实际执行 `val.toUpperCase()`（全大写化）——`minimal/index.ts:40` 声明 name，`:49` 实现 `return val.toUpperCase();`，非字符串输入直接 `as string` 原样返回（`:50-52`）。

### core/ 三件与 create-catalog

`core/A2UIProvider.tsx` 用双 Context 拆分：`A2UIActionsContext`（`:19`，actions 引用永不变存 ref）与 `A2UIStateContext`（`:24-25`，value 含 version，随状态更新）——教科书式 React 性能优化；`version` 是 `useState(0)` 计数器（`:84`），deleteSurface 等操作以 `{version: "v0.9", ...}` 信封发出（`:120`）。`core/A2UIRenderer.tsx` 是 `memo(function A2UIRenderer(...))` 包裹（tree-sitter 盲区，图谱节点手工补录）。`create-catalog.tsx` 承载 deprecated 旧代 API（`createA2UICatalog`/`extractA2UISchema`，`react-renderer/index.ts:50` 注释 "Catalog creation — deprecated API"），新代是 `createCatalog`/`extractSchema`；`PropsOf<D, K>` 泛型（`create-catalog.tsx:35`）从 Zod 定义推断组件 props，是"定义即契约"的类型驱动设计。

### v0.8 遗留尸骨（三处）

1. **A2UIViewer.tsx 不可编译**：`src/A2UIViewer.tsx:11` `import { initializeDefaultCatalog } from "./react-renderer/registry/defaultCatalog"`——`src/react-renderer/registry/` 目录**不存在**（find 实证）；`:13` 还 import 了现为空函数的 `injectStyles`。该文件不在发布入口（index.ts 不导出 A2UIViewer），属于 v0.8 时代的独立 viewer 组件残留，任何直接 tsc 全量编译都会在此炸裂。
2. **@a2ui/lit/0.8 幽灵依赖**：`A2UIViewer.tsx:4-5` `import type { Types } from "@a2ui/lit/0.8"` + `import type { v0_8 } from "@a2ui/lit"`；`tsdown.config.ts:13` 把 `@a2ui/lit` 列 external、`:37` UMD globals 把 `@a2ui/lit/0.8` 映射为全局 `A2UILit`——但 package.json dependencies **没有** `@a2ui/lit`（只有 `@a2ui/web_core: 0.9.0`、clsx、zod、zod-to-json-schema）。类型导入编译期擦除使其侥幸不炸，UMD 场景则假定宿主页面已加载 A2UILit 全局。
3. **styles 目录的空壳化**：v0.8 的外部样式注入架构在 v0.9 已内联进组件——`styles/index.ts` 的 `injectStyles()`（`:6-8`）与 `removeStyles()`（`:10-12`）全为 no-op，文件头注释 "v0.9: Styles are now handled by a2ui-react components internally"（`:1-4`）；`styles/index.d.ts` 仍声明 `structuralStyles/componentSpecificStyles` 导出（声明与实现代差）；同目录 README 描述的注入架构与"reset.ts"（磁盘不存在）都是历史代文档。

同类兼容 no-op 家族：`react-renderer/index.ts:90-96` 的 `registerDefaultCatalog()`/`initializeDefaultCatalog()`（注释 "v0.9: catalog is built-in"）、`:98-99` 的 `defaultTheme`/`litTheme` 空对象、包根 `index.ts:22` 的 `viewerTheme` 空对象、`:7-8` 的 `useA2UIStore`/`useA2UIStoreSelector` @deprecated 标记——整个包以"空函数保签名"的策略维持 v0.8→v0.9 平滑迁移。

### A2UIToolCallRenderer 退役（react-core 侧姊妹件）

退役机制的消费端在 `packages/react-core/src/v2/a2ui/A2UIToolCallRenderer.tsx`（44 行）：导出 `RENDER_A2UI_TOOL_NAME = "render_a2ui"`（`:9`）与 `A2UIBuiltInToolCallRenderer(): null`（`:25`，渲染 null 的组件）。它在 useEffect 里注册一个 no-op 渲染器 `render: () => <></>`（`:33`），让 `render_a2ui` 工具的原始流式参数永不出现在聊天记录。注释 `:15-20` 钉版退役原因（OSS-182 工单语义，源码写 OSS-162）：生成骨架/重试/失败 UX 已归 A2UI middleware 驱动的 `a2ui-surface` activity（单一稳定 messageId，building→retrying→failed→painted 生命周期），旧的"每个 tool call 一个骨架"在重试/多次调用时产生重复骨架且 painted 后残留。用户仍可用 `useRenderTool({ name: "render_a2ui" })` 覆盖（hook 优先于 prop 注册，`:22-23` 注释）。

## 外部连接（imports 边上下游）

- **上游强依赖**：`@a2ui/web_core` 0.9.0（Catalog 类、GenericBinder、BASIC_FUNCTIONS、createFunctionImplementation 全从它的 `/v0_9` 子路径导入）——A2UI 协议核心在本包之外，本包只是 React 方言。
- **react 家族**：peerDependencies `react ^18 || ^19 || ^19.0.0-rc`；clsx 做类名合并（测试里还有 `__tests__/clsx-shim.ts`）。
- **下游消费者**：`packages/react-core` 的 v2 a2ui 线（A2UIMessageRenderer/A2UICatalogContext/A2UIRecoveryStates）是唯一仓内消费面——react-core 通过 `@lit-labs/react`（Web Component 互操作）与本包协同；`.oxlintrc.json` 全仓规则**禁止 `@a2ui/lit` 值导入**（其注册 custom element 的副作用会破坏 React Strict Mode，digest b25），把幽灵依赖锁死在 type-only。
- **知识镜像**：`packages/a2ui-renderer/skills/a2ui-renderer/SKILL.md` frontmatter 锚定 5 个真实源文件（本包 2 + react-core/v2 2 + runtime/v2 1），经 sync-plugin-skills 镜像到根 `skills/a2ui-renderer/`（逐字节相同）。

## 数据流

一次 A2UI 生成-渲染闭环：

1. **生成**：Python/JS agent 的 A2UI middleware 在 `wrapModelCall` 注入 generate_a2ui 工具，LLM 流式输出组件树 JSON 作为工具参数（逐 token 到达）；
2. **流式解析**：runtime 侧 OpenGenerativeUI 式的增量 JSON 解析让"html/组件参数写一半先渲染一半"（clarinet SAX）；
3. **接入**：react-core 的 A2UIMessageRenderer 等到首个非空 updateDataModel 才交接（onReady 驱动，8 秒 setTimeout 仅兜底）；
4. **更新**：A2uiSurface 的 store 收到新的组件树 → `version++` → `getSnapshot` 字符串变化 → `useSyncExternalStore`（`A2uiSurface.tsx:105`）触发最小重渲染；类型替换（如 Text→TextField）因快照含 type 而必然命中；
5. **绑定**：GenericBinder 把组件的 dataContext.path 绑到模型节点，用户输入经 dispatch 闭包桥接回 `context.dispatchAction`（create-catalog.tsx）；
6. **骨架与恢复**：流式期间 shimmer 骨架（`:118-122`）占位；失败/重试由 react-core 侧 A2UIRecoveryStates 在同一 `a2ui-surface` activity 上原位交换状态（stable messageId + replace:true），本包只管 painted 后的真实渲染。

## 设计决策

- **快照字符串而非对象引用**：`useSyncExternalStore` 的 getSnapshot 要求引用稳定否则死循环、又要变化才触发更新——`${type}-${version}` 把两者压进一个原始值，type 参与 diff 是对"LLM 可能把一个组件改写成另一个组件"这一特有场景的适配。
- **双 catalog 档位**：basic 对齐官方完整规范（18 组件+外部函数表），minimal 自包含（5 组件+内联 zod）——后者用于"宿主不想拉全套 @a2ui/web_core basic_catalog 依赖"的场景，代价是 schema 手工维护。两档同 URL 命名空间（a2ui.org/specification/v0_9/...）保证可互换。
- **no-op 保签名迁移策略**：v0.9 把样式、主题、catalog 初始化全部内部化，但没有删除 v0.8 API——全部降级为空函数/空对象（injectStyles、viewerTheme、litTheme、initializeDefaultCatalog 五族）。升级用户的代码继续编译，行为静默变化。代价是 styles/index.d.ts 等声明与实现的代差、以及"哪些函数是真活的"成为读码负担。
- **A2UIViewer 的安乐死选择**：registry 目录删除后 A2UIViewer.tsx 留在源码树但事实上不可编译——不删是因为 viewer-theme.ts（Apache 2.0 数据资产）与它的引用关系有待清理；不修是因为 v0.9 主线（Surface）已完全替代。这是"死代码作为待办"的活标本。
- **退役渲染器的一行禅**：A2UIToolCallRenderer 从"渲染骨架"退化为"注册空白"（`:33`），44 行里 24 行是注释——注释密度本身就是设计文档：为什么退役（重复骨架+残留）、退役后谁负责（a2ui-surface activity）、如何覆盖（useRenderTool 优先级）。改动日志内联在代码里。
- **ChildList 双双未注册**：basic 与 minimal 目录各有一个 ChildList.tsx 存在但未进 catalog 聚合数组——可能是"容器类组件由内核直接处理、不经 catalog 注册"的机制性遗漏，也可能是未完成迁移；阅读时勿把目录文件数当成组件能力数。

## 新人提示

1. **从 A2uiSurface.tsx 读起**（约 130 行），它是全包机制的浓缩：外部 store + 快照身份 + 内联骨架，读懂它就读懂了 A2UI 增量渲染。
2. **别 import A2UIViewer**——它 import 不存在的 `./react-renderer/registry/defaultCatalog`（`A2UIViewer.tsx:11`），真入口是 `src/index.ts` 导出的 Surface/A2UIRenderer 家族。
3. **@a2ui/lit 只许 type import**：oxlint 规则强制（`.oxlintrc.json`），值导入会注册 custom element 破坏 Strict Mode；且它不在 package.json 里，运行时 import 直接 ReferenceError。
4. **数组件看 catalog 数组不看目录**：basic 18（`basic/index.ts:21-38`）、minimal 5（`minimal/index.ts:24-30`），两个 ChildList.tsx 都是未注册孤儿。
5. **调 capitalize 别期待首字母大写**：它做的是 toUpperCase 全大写（`minimal/index.ts:49`），A2UI 规范函数名与实现的错位上游也存在。
6. **v0.8→v0.9 对照表**：外部样式注入→组件内联；viewerTheme/litTheme/defaultTheme→空对象；registry/defaultCatalog→built-in；`createA2UICatalog`→`createCatalog`。见到前者的现代用法一律是后者的别名或 no-op。
