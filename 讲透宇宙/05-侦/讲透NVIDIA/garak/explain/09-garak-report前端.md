# 09 · garak-report 前端：React 组件族与单文件注入契约

## 一、角色定位

`garak-report/` 是 garak 报告的 React 前端（package.json `@nvidia/garak-report` 0.1.0），职责是把后端 digest JSON 渲染成交互式 HTML。它的特殊性在于**不是独立部署的 web 应用，而是 garak Python 包的编译期资产**：正式构建产物直接写入 `../garak/analyze/ui`（vite.config.ts:73），被 report_digest 的 build_html 当模板使用（见 08 篇）。技术栈：React 19.1 + Vite + Tailwind 4.1 + ECharts 5.6（package.json dependencies），NVIDIA 内部 UI 框架 KUI 以 vendor tarball 锁版本（`@kui/react: ./src/assets/kui-foundations-react-external-0.504.1.tgz`），不落外部 registry。

## 二、内部结构

入口链 `src/main.tsx → App.tsx → pages/Report.tsx`。App.tsx 管 KUI ThemeProvider 与主题持久化：localStorage 读写 `kui-theme`（App.tsx:26-36），手动给 html 元素挂 nv-dark/nv-light class 而非依赖全局 prop（App.tsx:39-55，注释自述 workaround）。Report.tsx（169 行）是唯一页面：四个顶层钩子 useReportData / useFlattenedModules / useModuleFilters / useThemeMode（Report.tsx:45-55），按 `technique_intent_matrix` 是否非空切两种布局——有则 Tabs 双页"Modules / Techniques & Intents"（:147-161），无则保留旧单栏（:159-161），三处 ErrorBoundary 分区兜底（:97, :115, :133）。

组件族分七层（`src/components/index.ts` 49 行 barrel 统一导出）：Layout（Header/Footer）、Report（ReportDetails/ReportFilterBar/ModuleAccordion/SummaryStatsCard/DefconSummaryPanel）、Chart（ProbesChart/DetectorsView）、三个子目录族——TechniqueIntent（Panel/AxisList/CellChart，index.ts:16-18）、ProbeChart（BarChart/Header/TagsList，index.ts:35）、DetectorChart（LollipopChart/ResultsTable/Filters，index.ts:36）、UI（DefconBadge/ColorLegend/ErrorBoundary）、Display（CalibrationSummary/SetupSection/MetadataSection/双 Logo/ProgressBar）。注意 index.ts 里 default 与具名导出混排（:16-17 default，:31-32 具名）——**图谱构建时 TS barrel 的 re-export 边是正则补齐的**，tree-sitter 对 `export { default as X } from` 模式提取不全，这是本域的图谱补建口径。hooks 17 个文件对应图表配置（useProbeChartOptions/useDetectorChartOptions/useTaxonomyCellChartOptions）、排序过滤（useSortedDetectors/useModuleFilters/useGroupedDetectors）、格式化（useValueFormatter/formatPercentage）等，全部纯函数式可单测。

## 三、外部连接

与 Python 后端的契约点是同一个字符串 `__GARAK_INSERT_HERE__`，三条通道共用它：① 构建期 Vite define 替换——仅 example 构建 `BUILD_EXAMPLE=true` 时把它映射到 `window.__GARAK_INSERT_HERE__`（vite.config.ts:78-80），数据由 injectExampleData 插件从 `public/reports/extracted_digest.json` 读出注入 script 标签（:30-39）；② 运行期 Python 文本替换——report_digest.py:715 把构建产物 HTML 里保留的裸标记替换为 digest 数组；③ 前端读取——useReportData.ts:21 用 `typeof __GARAK_INSERT_HERE__ !== "undefined"` 守卫取编译期常量，配 @ts-expect-error 压住未声明标识符的类型错，失败再退 `window.reportsData`（:64-66）。仓根 `garak-report/extracted_digest.json`（7425 行）是联调夹具真身：**单对象**（entry_type/meta/eval/technique_intent_matrix 四顶层键），而 vite.config.ts:32 引用的是 `public/reports/extracted_digest.json`——该路径当前不存在（public/ 下仅 index.html），build:example 会走 catch 分支静默失败，属夹具就位断链。

## 四、数据流

digest 注入后的消费路径：useReportData 取数组首元素（:62-63，**多报告只渲染第一份**）→ 派生 calibrationData/setupData（:70-73）→ useFlattenedModules 把 eval 树拍平成模块列表 → useModuleFilters 做 DEFCON 勾选过滤与排序 → ModuleAccordion 按组折叠渲染，ProbeChart/DetectorChart 内部用 ECharts 画条形/棒棒糖图 → TechniqueIntentPanel 消费 matrix + intent_typology 渲染技术×意图热区。渲染期产物是**单文件 HTML**：viteSingleFile 插件仅在正式构建启用（vite.config.ts:57），assetsInlineLimit=Infinity + cssCodeSplit=false（:74-75），最终 ui/index.html 实测 1.75MB、内联全部 JS/CSS/SVG。

## 五、设计决策

1. **构建产物写回 Python 仓**（vite.config.ts:73）：前端不是独立服务，是后端模板；emptyOutDir=false（:76）防止误删 ui 目录其他文件。
2. **单标记三通道复用**：同一 `__GARAK_INSERT_HERE__` 既做 Vite define 常量又做 Python 文本替换锚——产物 HTML 里实测存留 2 处裸标记（typeof 守卫处与取值处），替换后 `typeof [json]` 恒真，机制成立但依赖构建器不做标识符改名。
3. **HMR 保卫战**：viteSingleFile 的 base:"./" 会弄死 dev HMR，故 build-only（:54-57 注释）；macOS fsevents 休眠后 watcher 静默死，用 usePolling 兜底（:62-70）。
4. **KUI vendor tarball**：内网框架不走 registry，版本精确到 0.504.1 补丁号。
5. **coverage 门槛 85% 四项全卡**（vite.config.ts:94-99），exclude 名单排除纯展示组件与 SVG（:114-121）——测试文化重（38 个 *.test.* 文件）。
6. **旧脚本通道清理**：正式构建正则删除 `/reports/reports.js` 标签（:26-28），index.html 与 public/index.html 的差异只剩相对/绝对路径（后者 :11 用 `./`）。

## 六、新人提示

改前端的正确回路：`yarn dev` 起本地（数据从 window.reportsData 或夹具来）→ 改组件 → `yarn build` 落盘到 ../garak/analyze/ui → 用 `python -m garak.analyze.report_digest -r <report>` 验证注入。三个坑：① build:example 依赖的 public/reports/ 夹具缺失是静默失败（catch 只 console.error，vite.config.ts:40-42），先确认夹具就位；② 别在 useReportData 之外再开数据入口——主题外的全局状态都在这一个钩子收敛；③ 老报告没有 technique_intent_matrix 字段时布局自动退化为单栏（Report.tsx:57-60），测新功能时用仓根 extracted_digest.json 这类新格式夹具，否则 Tabs 页根本不出现。
