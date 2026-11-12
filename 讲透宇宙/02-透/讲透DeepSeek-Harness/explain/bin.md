# bin.ts — dsh 命令行入口：50 行的分发壳

> 原文件：[`apps/cli/src/bin.ts`](../../../explore/deepseek-ai/deepseek-harness/apps/cli/src/bin.ts)（50 行 · 仓库版本 0.1.2-rc.1）

## 角色定位

`bin.ts` 是整个 deepseek-harness（下称 dsh）唯一支持的命令行入口，模块标识 `@deepseek-ai/dsh/bin`。仓库有一条硬规则：**只有 `dsh` 的 profile 启动路径才是受支持的 Node 应用启动方式**，包内 bin、demo、公共 SDK 的 argv 逃生门都被禁止——所以这个文件就是"产品的大门"，没有侧门。

它的大门外貌是刻意做成的：整个文件只有 50 行，不含任何业务逻辑，只做三件事——读版本号、解析命令行、按解析结果把工作分发给三个 runner 之一。理解这个文件的价值不在于它本身有多少东西，而在于它是追踪启动链的第一站：所有 profile 装配、插件加载、沙箱建立的开端，都能从第 26 行那个 `switch` 顺藤摸瓜找到。

## 内部结构

文件由四个小块组成：

**`readVersion()`**：用 `fileURLToPath(new URL('../package.json', import.meta.url))` 读同级上层目录的 manifest，取 `version` 字段；若不是字符串则回退 `'0.0.0'`。这里有一段值得细读的注释：源码树（`apps/cli/src`）和打包产物（`apps/cli/lib`）都位于 `apps/cli` 的下一级，所以同一个相对跳转 `../package.json` 在两种形态下都命中正确的 manifest——版本号永远单源，不会出现源码与产物各记一份的漂移。

**参数解析**：`parseDshArgs(process.argv.slice(2), readVersion())` 返回 `invocation` 对象。解析逻辑全部在 `./args.ts` 里（同步 import，是本文件唯一的静态业务依赖），`invocation` 是带 `mode` 判别标签的联合类型。

**三分支分发**（`switch (invocation.mode)`）：

- `case 'profile'`：动态 `await import('./profile-boot.ts')` 取 `runProfile`，以 `{ environment: loadLayeredEnv('dsh'), profile, patchFiles: invocation.patches, args }` 调用。这是正式启动路径——分层环境先装配，再把 profile 名、补丁文件与剩余参数交给 profile 引导器。
- `case 'plugin'`：动态 import `./plugin.ts` 的 `runPlugin`，用其返回值直接 `process.exit`，是同步退出的插件工具路径。
- `case 'dump-config'`：动态 import `./dump-config.ts` 的 `runDumpConfig`，打印生效配置（支持 `defaultOnly` 与补丁参数），用于检查 profile 层叠结果。

**穷尽性兜底**：`default` 分支先写 `invocation satisfies never`，再抛出带完整 invocation JSON 的错误。

另外文件顶部有 `/* v8 ignore file */` 注释：内置 bin 的验收测试会真实执行这个自分发文件，覆盖率统计反而覆盖不到，因此整体忽略。

## 外部连接

图谱上这个文件没有入边（它是进程入口，由 package.json 的 `bin` 字段指向），出边清晰：

- **同步依赖**：`./args.ts`（参数解析）、`node:fs`/`node:url`（读 manifest）。
- **动态依赖**：`./profile-boot.ts`、`./plugin.ts`、`./dump-config.ts` 三个 runner，全部按需加载。
- **跨包依赖**：`@deepseek-ai/dsh-app-boot` 的 `loadLayeredEnv('dsh')`——分层环境解析器，`DSH_` 前缀的环境变量按层级覆盖后形成启动环境。

## 数据流

一次 `dsh --profile headless "任务"` 的旅程：argv 进入 → `parseDshArgs` 结合版本号产出 `invocation`（mode='profile'，附 profile 名、patches、剩余 args）→ `loadLayeredEnv('dsh')` 装配 environment → `runProfile` 在 profile 引导器里读取 cordis.yml、加载插件、建立应用上下文，控制权从此离开本文件。`plugin` 与 `dump-config` 两条支路则分别在打印结果/返回退出码后终结。

## 设计决策

**薄入口 + 动态 import**：三个 runner 都是 `await import()` 而非顶部静态导入。收益有二：入口启动开销最小化；可选能力只在对应 mode 才加载——不走 profile 就完全不必解析 profile 引导器及其依赖树。

**`satisfies never` 的穷尽性检查**：这是仓库约定"闭联合用判别标签 switch、结尾断言"在入口处的落地。未来给 `parseDshArgs` 增加新 mode 时，TypeScript 会在编译期强迫开发者回到这个 switch 补分支，否则 `invocation` 在 default 分支不再是 `never`，编译直接失败。运行期的 throw 只是双保险。

**版本号单源**：从相邻 manifest 读取而非硬编码，且注释明确说明了源码/产物两种布局下的路径一致性依据。

**v8 忽略的理由写进注释**：为什么一个 100% 被真实执行的文件反而要忽略覆盖率——因为验收测试从构建产物发起，统计归属不清。这种"注释记录事实而非复述代码"的风格是仓库明文要求。

**入口的唯一性是制度而非习惯**：仓库约定"应用启动"只有 `dsh` 的 profile 路径是受支持的 Node 应用启动方式——各包自带 bin、demo 入口与公共 SDK 的 argv 逃生门一律禁止；`bundle/` 目录提供的是可安装到 profile 的补丁层捆绑，而不是另一条启动路径。还有一条容易被忽略的契约：`dsh` CLI 从源码启动时走 tsx 的 ESM-only hook（`node --import tsx/esm`），它能到达的模块必须保持 ESM 导出、不能引入仅 CJS 的依赖——在支持的引擎区间内 Node 原生 TypeScript 模式不可用，这条约束记录在源码启动契约笔记里，入口的简洁因此还承担着"别把不可达的依赖引进来"的守门职责。

## 新人提示

把这个文件当作仓库地图的图例：三分支对应三种使用方式（正式运行 / 插件工具 / 配置检查），你后续要读的代码几乎都在 `profile-boot.ts` 之后的世界里。三个实用建议：一，先用 `dsh dump-config` 看一次生效配置，理解 profile 与 patches 如何层叠，比读配置代码更直观；二，追踪启动链时按 `bin.ts → args.ts → profile-boot.ts → loadLayeredEnv` 的顺序读，每步只回答一个问题；三，如果你改了 `args.ts` 增加新 mode，记得 `satisfies never` 会在这里拦住你直到补全 switch——这不是报错，是设计好的编译期护栏。真实跑任务（如 `pnpm dsh --profile headless "任务"`）需要 `DEEPSEEK_API_KEY` 与根目录 `.env`；profile 的补丁可以来自 `bundle/` 的可安装补丁层，`dump-config` 直接验证补丁叠加后的最终形态——把三个入口模式各跑一遍，这个 50 行文件的地就算踩实了。最后留意一个细节：兜底错误信息里带着完整 invocation 的 JSON——入口层的失败永远自带上下文，这是全仓库"失败要响亮且可诊断"风气的起点。
