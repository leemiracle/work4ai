# src/composition/：组合根与手写依赖注入

## 角色定位

`src/composition/` 是 REA 的**唯一生产装配层**（composition root）：应用层定义接口与编排，适配器层（src/ghidra、src/hopper、src/ida…）对接外部引擎，本目录把两者焊接。核心文件注释即架构宣言："This is the sole production wiring point, so both adapters share identical provider selection, profile, lifecycle, and Evidence semantics"（src/composition/binary.ts:14-18）——CLI 与 MCP 不允许各接各的线，否则行为漂移。图谱中 binary.ts fan-out=17、fan-in=5，典型"窄腰"节点。

## 内部结构

目录 18 个文件分三类：

- **会话装配**：`createBinarySession` 是心脏——三个原生 provider（Hopper/Ghidra/Ida）装进 `AnalysisProviderRegistry`，叠加惰性辅助 provider，`composeBinarySession` 收口（src/composition/binary.ts:19-35）；`createManagedBinarySession` 装配无原生引擎的 .NET 会话（src/composition/binary.ts:38-43）。
- **辅助声明**：`auxiliaryAnalysisProviderDeclarations()` 返回 Artifact/NativeMacOS/ManagedStatic 三项声明，各含 identity、capabilities 与动态 `import()` 的 load（src/composition/auxiliaryAnalysisProviders.ts:19-40），经 `LazyAnalysisProvider` 包裹进注册表（src/composition/binary.ts:31-33）。
- **直连与可选观测**：directAnalysis.ts 用 `bind(undefined, dependencies)` 把会话工厂偏应用进应用层函数（src/composition/directAnalysis.ts:13-46）；optionalObservationProviders.ts 为五个观测端口各配动态 import 工厂（src/composition/optionalObservationProviders.ts:17-37）。

配置解析同属组合根：src/config.ts 是两行 barrel（src/config.ts:1-2），实体 `parseConfig` 返回 `Result<AppConfig, ConfigurationError>`（src/config/parseConfig.ts:38-44），内置 macOS/Linux 两套 Hopper 默认路径探测（src/config/parseConfig.ts:11-28）。

## 外部连接

上游只有两个适配器：src/main.ts:61 调 `createBinarySession` 建 MCP 长驻会话；CLI 命令经 directAnalysis.ts 绑定函数获得隔离会话（src/composition/directAnalysis.ts:19-28）。下游引用 application 层的 `BinarySession`/`AnalysisProviderRegistry` 与三个引擎 provider 构造器（src/composition/binary.ts:1-12）。五个观测 provider 组合文件只在运行时被动态加载——重依赖（Playwright 驱动等）不拖累核心启动。

## 数据流

以 CLI 一次 `rea analyze` 为例：命令层调 `runDirectAnalysis` → 组合根已把会话工厂烤进函数（src/composition/directAnalysis.ts:13-16）→ registry 依 `config.analysisProvider` 或能力协商选主 provider → 执行 → Evidence 回填 → 会话销毁；MCP 链相同但会话存活整个进程。可选端口加载走 Result 通道：`loadPort` 捕获异常返回 `err`（src/composition/optionalObservationProviders.ts:39-45），主调方只降级不崩溃。

## 设计决策

- **手写 DI 而非容器**：无 reflect-metadata、无装饰器，注入就是构造器传参 + bind 偏应用，零魔法且类型可追踪；代价是新增 provider 必改这一处——这正是组合根本义：装配变更集中化。
- **惰性加载辅助 provider**：声明只留 `load: async () => import(...)`（src/composition/auxiliaryAnalysisProviders.ts:29-33），registry 先看 capabilities 选择，选中才付加载成本。
- **Result 出现在每个边界**：parseConfig、可选端口加载、会话 open 全返回 `Result`，错误是值不是异常。
- **平台参数显式注入**：`auxiliaryAnalysisProviderDeclarations(platform = process.platform)` 允许测试传假平台。

## 新人提示

新增 provider 清单：实现类 → Metadata 加 identity/capabilities → 进 auxiliaryAnalysisProviderDeclarations 或 binary.ts 主列表 → 补 config 环境变量；漏掉组合根这步 provider 永远不会实例化。不要在 src/application/ import 具体 provider——那会打破 "sole wiring point"。改 `createBinarySession` 签名要过 CLI/MCP 两处调用方；`createManagedBinarySession` 是无引擎降级路径，CI 无头 Linux 靠它跑 .NET 测试，别删。调试先看 `rea providers`（src/composition/directAnalysis.ts:37-40）。
