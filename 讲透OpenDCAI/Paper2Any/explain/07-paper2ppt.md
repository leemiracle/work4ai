# 07 · paper2ppt 深潜：5422 行四步工作流与三通道 PPTX 导出

> 定位层级：frontend 应用基座 → paper2ppt 组件家族。本篇覆盖 `frontend-workflow/src/components/Paper2PptPage.tsx`、`paper2ppt/` 目录全部 26 文件（合计 15060 行），是仓内最大的前端子系统。

## 一、角色定位

paper2ppt 是 Paper2Any 的招牌功能"论文转 PPT"的前端门面。入口文件名有欺骗性：`src/components/Paper2PptPage.tsx` 本身只有 7 行，是一个纯粹的 re-export 壳（L1-7：`import Paper2PptPage from './paper2ppt'` 加一层 `Paper2PptPageWrapper`），真身是 `paper2ppt/index.tsx`——**5422 行**，全仓最大单文件，一个文件装下了状态机、上传、大纲编辑、逐页生成、画布编辑、三套导出与 OnlyOffice 集成。

家族成员分工（按行数）：`index.tsx` 5422 行总控、`frontendSchemaRenderer.ts` 1789 行（blocks 渲染引擎）、`canvasPptxExporter.ts` 1228 行（canvas 导出）、`UploadStep.tsx` 1014 行、`FrontendGenerateStep.tsx` 688 行、`exportStructuredSlides.ts` 704 行、`FrontendSlidePreview.tsx` 634 行、`types.ts` 622 行（类型宪法）、`frontendSlideUtils.ts` 522 行、`StructuredSlideCanvas.tsx` 528 行。

## 二、内部结构

### 2.1 四步状态机

状态机骨架极简，`types.ts:1` 定义 `Step = 'upload' | 'outline' | 'generate' | 'complete'`；`index.tsx:88` 用 `useState<Step>('upload')` 持有当前步。四段的注释分界线在 index.tsx 内非常清晰：

- **Step 1 上传**（L2837 `// ============== Step 1: 上传处理 ==============`）：PDF 上传、解析结果获取，成功后 L3069 `setCurrentStep('outline')`；
- **Step 2 Outline 编辑**（L3091 分界）：用户增删改大纲条目，确认后 L3858 `setCurrentStep('generate')`；
- **Step 3 生成**（含 L4356 `Step 3: 重新生成单页`）：逐页生成幻灯片，支持单页重roll；
- **Step 4 完成**（L4771 分界）：三通道导出与在线编辑入口，L5102 `setCurrentStep('upload')` 支持重来一轮。

渲染分支对应 L5145（upload）、L5187（outline）、L5213（generate）、L5269（complete），四块条件渲染顺序即用户旅程。另有 `PptGenerationMode = 'image' | 'frontend'`（types.ts:2）区分"图像模式"（每页截图式）与"前端模式"（结构化可编辑），后者才是三通道导出的主场。

### 2.2 双渲染引擎与 canvas 默认

幻灯片有 `renderEngine: 'blocks' | 'canvas'` 两种引擎（types.ts:81）。关键口径在 index.tsx:2078-2079：后端返回的 `render_engine` 归一化时，**只有显式等于 `'blocks'` 才走 blocks，其余一律落到 canvas**——`const renderEngine = rawRenderEngine === 'blocks' ? 'blocks' : 'canvas'`。也就是说 canvas（容器/组件二叉树，`FrontendCanvasNode` types.ts:219 起）是事实默认引擎，blocks 是兼容旧数据的遗留路径。用户在前端插入画布节点时（L1365-1371），新页直接写死 `renderEngine: 'canvas'` 并附 `schemaVersion: 'ppt_canvas_schema_v1'`。

### 2.3 PPTX 导出三通道并立

Step 4 的"可编辑 PPTX"实际存在**三条并行通道**，代码全在且都能跑：

1. **canvas 通道**（`canvasPptxExporter.ts` 1228 行）：`buildCanvasSlidesPptxBlob`（L1153）把 canvas 节点树递归展开成 PptxGenJS 的 textbox/shape/image。主页面首选：index.tsx:4792 先 `canExportCanvasSlidesToPptx(slidesForExport)`（canvasPptxExporter.ts:1223 的守卫函数）再 L4794 调 blob 导出。
2. **HTML 通道**（`htmlDeckArtifact.ts` 112 行 + `html2pptxExport.ts` 108 行）：`buildHtmlDeckArtifact`（htmlDeckArtifact.ts:88）先把幻灯片组编成一份自包含 HTML 原稿，`exportHtmlDeckToPptx` 动态注入 `/vendor/dom-to-pptx.bundle.js`（html2pptxExport.ts:3 的 `DOM_TO_PPTX_BUNDLE_URL`），在沙盒 DOM 里把 HTML 转成 PPTX。流程见 index.tsx:4847-4870：HTML 上传结果列表 → 转 PPTX → 再上传 → 拿到 `download_url` 进在线编辑。
3. **结构化通道**（`exportStructuredSlides.ts` 704 行）：`exportStructuredSlidesToPptx`（L178）按 `StructuredSlideLayoutType`（types.ts:442 起的 Cover/Section/Bullets/TwoColumn/Cards2x2/ImageFocus/Comparison/Timeline 家族）走 pptxgenjs 布局模板。**批判点：这条通道在 index.tsx 里只被 import（L50）却没有任何调用点**，唯一消费者是 Node 侧 CLI `frontend-workflow/scripts/run_paper2ppt_structured_export_cli.ts:181`——主页面用户实际摸不到它，属于"半下线"状态。

### 2.4 OnlyOffice 在线编辑（v2 线）

HTML 通道产出的 PPTX 不止下载，还能进 OnlyOffice iframe 编辑。机制是 postMessage 注入：index.tsx:68 定义 `OnlyOfficeEditorPayload`，L144-149 一组 onlyOffice state（config/modalOpen/sessionId/frameRef），L2789-2806 `postOnlyOfficeFrameConfig` 把配置 post 给 iframe 的 contentWindow。后端配套在 `fastapi_app/routers/files.py`：L347 `GET /onlyoffice/config` 下发编辑器配置（L104-107 懒加载 `OnlyOfficeFileService`），L365 `/onlyoffice/download/{document_key}.pptx` 双方法路由给 OnlyOffice 回源取文档。

## 三、外部连接

- **后端生成链**：上传/大纲/生成走 fastapi_app 的 paper2ppt 相关 router（经 portal bridge 与任务轮询拿结果，L2766/L5082 两处 fetch 下载产物）。
- **文件服务**：三通道产物通过 `uploadGeneratedResultBlob` 回传结果列表（L4849-4851、L4861-4863），OnlyOffice 再从 files.py 回源。
- **门户统计**：index.tsx:339-341 直接 fetch 三个 GitHub API（OpenDCAI/DataFlow、OpenDCAI/Paper2Any、OpenDCAI/DataFlex）——页面上展示的是姊妹仓 star 数。
- **CLI 旁路**：`run_paper2ppt_structured_export_cli.ts` 在 Node 环境复用结构化导出，与 `script/run_paper2ppt_frontend_cli.py`、`script/run_paper2ppt_cli.py` 构成"无浏览器"验证线。
- **姊妹页面**：`Pdf2PptPage.tsx`、`Image2PptPage.tsx`、`Ppt2PolishPage.tsx` 复用同一家族的组件与 i18n 命名空间（见第 11 篇）。

## 四、数据流

一次完整旅程：用户上传 PDF（Step1）→ 后端解析出文本/图表 → 前端拿到初始 outline（Step2 编辑，条目级增删）→ 逐页生成（Step3，每页产出 `FrontendSlide`，含 `renderEngine`、canvas 树或 blocks、`visual_spec`、review 状态）→ Step4 归一化 `normalizeFrontendSlides(serializeFrontendSlide(...))` 后按通道分流：canvas 可导则 canvas 直出 blob；HTML 线是"HTML 原稿上传 → dom-to-pptx 转换 → PPTX 上传 → OnlyOffice 会话"；结构化线仅 CLI 可达。导入侧对称：后端 JSON 字段做 snake/camel 双兼容（L2078 `slide.render_engine || slide.renderEngine`），`renderEngine` 归一后 canvas 页会清空 blocks（L2092 `blocks: renderEngine === 'canvas' ? [] : blocks`）防止双份数据打架。

## 五、设计决策（含批判）

1. **单文件巨石 vs 家族拆分**：index.tsx 5422 行扛了状态机+UI+三通道编排，Step 组件虽已拆出（UploadStep 1014 行也不小），但总控仍持有全部跨步状态（L91/112/124/135 四段注释即四个状态簇）。改动任何一个 Step 的交互几乎都要动 index.tsx，回归面大。
2. **三通道并立是演进痕迹而非设计**：结构化（最早，布局模板硬编码）→ canvas（主力，表达力强）→ HTML+OnlyOffice（最新，保真编辑）。三者共存意味着同一份 slide 数据有三套序列化逻辑，types.ts 被迫同时供养三套类型。结构化通道在主页面零调用（仅 CLI 消费）却仍占 704 行与全套类型，属于该退役未退役。
3. **types.ts 成段重复（必收录 bug 级）**：`types.ts` L301-440 与 L160-299 是**成段的 interface 重复**——`FrontendCanvasNodeStyle`(160/301)、`FrontendCanvasVisualStyle`(176/317)、`FrontendCanvasVisualSpec`(194/335)、`FrontendCanvasNode`(219/360)、`FrontendCanvasContentAsset`(228/369)、`FrontendCanvasValidationIssue`(237/378)、`FrontendCanvasValidation`(246/387)、`FrontendLayoutIRNode`(256/397)、`FrontendLayoutIR`(270/411)、`FrontendDeckPalette`(282/423)、`FrontendDeckTypography`(292/433) 十一个接口两连发。更夸张的是 **`FrontendDeckPalette` 达 3 次**：L282、L423 之外，L566（`FrontendThemeLock` 之后的第三套 Deck 主题家族段）再来一次。TypeScript 的 interface 声明合并让编译器一声不吭，但三处字段一旦改动不同步，"同名字段类型不一致"的报错会离奇难懂。这是典型的大文件迁移残留——canvas v2 类型段整段粘贴后旧段没删。
4. **canvas 默认的隐式契约**：归一化把一切非 'blocks' 值（空串、拼写错、旧字段名）都归为 canvas，宽容归一降低了后端耦合，但也意味着后端拼写错误永远静默降级，不会在导入时暴露。
5. **导出走前端内存**：canvas/HTML 通道都在浏览器里生成 blob（对大 deck 的内存压力），再上传回后端——"服务端渲染下载"这条路完全让位给前端，换取 OnlyOffice 会话的文件回传闭环。

## 六、新人提示

- 别从 `Paper2PptPage.tsx` 开始读，直接进 `paper2ppt/index.tsx`，先搜四段 `=====` 注释（L2837/L3091/L4356/L4771）建立地图，再按 `currentStep` 渲染分支（L5145 起）对照。
- 改类型先查重：在 types.ts 里 `grep -n "interface X"` 确认没有第二第三处定义再动手，尤其 Palette/Typography/CanvasVisual 三族。
- 想验证导出效果又没有后端时，跑 `frontend-workflow/scripts/run_paper2ppt_structured_export_cli.ts`（Node 环境直调 L181 的 `exportStructuredSlidesToPptx`），它是不起浏览器最快的烟雾测试。
- 排查"导出按钮没反应"时记住优先级链：`canExportCanvasSlidesToPptx` 守卫失败（页面缺 canvas 树）→ 落到 HTML 线 → HTML 线依赖 `/vendor/dom-to-pptx.bundle.js` 静态资源加载（html2pptxExport.ts:43-46 onerror 才抛"资源加载失败"），三段各有各的失败静默点。
- OnlyOffice 会话不通时查两处：前端 L2790 的 `enabled` 短路（config 未启用直接 return），后端 files.py:347 config 端点与 L365 download 端点是否可达。
