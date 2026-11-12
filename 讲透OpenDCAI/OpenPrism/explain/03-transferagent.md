# 03 transferAgent：LangGraph 双管线与工具 Agent

## 角色定位

`apps/backend/src/services/transferAgent/` 是"论文模板迁移"引擎：把论文从模板 A 搬进模板 B 并保证可编译。两条 LangGraph 管线同构并存：`graph.js`（LaTeX→LaTeX 线，入口 `analyzeSource`）与 `graphMineru.js`（PDF→MD→LaTeX 线，入口 `compileSource`+`parsePdfWithMineru`），各 **11 节点**（graph.js:53-63 / graphMineru.js:56-66），后半程 8 节点共享。状态 `state.js` 用 `Annotation.Root`（L6-56），reducer 仅 `replace` 与 `appendList`（L3-4）。

## 内部结构

拓扑：线性段 `analyze* → draftPlan → applyTransfer → copyAssets → compile`；`afterCompile` 条件路由（graph.js:18-31）——成功且开 layoutCheck 则 `requestPageImages`，否则 `finalize`，失败且 `compileAttempt < maxCompileLoops`（默认 5，state.js:13）进 `fixCompile` 回环；`interruptBefore:['checkLayout']`（graph.js:104）暂停等前端提交页面截图；`afterLayoutCheck`（L36-44）决定 `fixLayout` 回环（默认 3 轮，state.js:14）或收官。节点分工：`analyzeSource` 递归解析 `\input/\include` 拼全文（L12-41 visited 防环）、`collectAssets` L59 收 bib/图/样式；`draftPlan` 让 LLM 出 sectionMapping/assetStrategy 计划（`invokeLLMForJSON` 带 schema 校验重试）；`applyTransfer` 用"保 preamble、只动 body、保留全部 cite/ref/label"10 条规则 prompt 让 LLM 整文件重写。MinerU 线 `compileSource` 见 `state.sourcePdfPath` 跳过编译（L16-21），`parsePdfWithMineru` 产物写 `_mineru_output/`。

## 外部连接

入口 `routes/transfer.js` 六端点，任务表是**模块级内存 Map**（L13）。前端 `TransferPanel.tsx` 泵送：`handleStart` L159 分模式调 `transferStart`/`mineruTransferStart`，`runGraph` L221-245 循环 `transferStep` 直到终态。工具侧 `agentService.runToolAgent`（L17-197）是独立于管线的 7 工具 agent（L187）：read_file/list_files/propose_patch/apply_patch/get_compile_log/arxiv_search/arxiv_bibtex。**arXiv Atom 解析是三胞胎复制**：arxivService.js:29-44、routes/arxiv.js:15-31、agentService 内 L117-132，三段 `feed.entry` 归一化代码逐行雷同。

## 数据流

`/api/transfer/start`（L24-93）：校验模板 → UUID 建新项目 → `copyDir` 拷入模板 → jobs.set。`/step`（L101-136）每次 `graph.invoke`：首调传 initialState，此后传 null 由 `MemorySaver` 按 `thread_id:jobId` 续跑（L115-117）。`/submit-images`（L143-170）把 pageImages 打进 checkpoint，下一 /step 从 checkLayout 恢复。`/upload-pdf`（L282-326）把 PDF 写进目标项目 `_uploaded_source.pdf` 并置 `sourcePdfPath`。`finalize` 按 compileResult 定终态。

## 设计决策（含批判）

亮点：编译修 5 轮 + 版面修 3 轮的自愈环；写文件全走 `writeFileWithSnapshot`（utils.js:165，带 jobId 快照）；`propose_patch/apply_patch` 都明写 "does NOT write"（L59/L77），改动先进 `pendingPatches`（L32）等用户确认，安全模型干净。批判四点：其一，jobs Map + MemorySaver 全内存，**后端重启 = 任务全部蒸发**，无持久化；其二，`transferSubmitImages`（client.ts:505）被 TransferPanel.tsx:6 导入后**全前端零调用**——图在 `waiting_images` 暂停后没有 UI 路径提交截图，layoutCheck 打开即死路，VLM 版面检查实际不可达；其三，`/step` 一次 invoke 跑到底，progressLog 是事后全量非实时流；其四，Atom 解析三处复制埋了"改一处漏两处"的地雷。

## 新人提示

先读 graph.js:18-44 两个条件函数，控制流即懂。layout 环"死锁"直接看 `status==='waiting_images'`（transfer.js:109-111）。加新节点三步：nodes/ 建文件 → 两份 graph 各 addNode+接线 → state.js 加字段（选对 reducer）。MinerU 线跑通前提是 `resolveMineruConfig` 拿到 token（mineruService.js:12-34）。
