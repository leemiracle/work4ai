# 02 EditorPage.tsx：5560 行编辑器巨兽与 CodeMirror6 集成

## 角色定位

`apps/frontend/src/app/EditorPage.tsx` 是产品心脏：三栏工作台（文件树/编辑器/PDF 预览）+ AI 补全 + agent + arXiv 检索 + 协同，全在一个文件。结构"两段式"：L92-1211 约 1120 行**模块级纯函数**（折叠算法、大纲解析、JSON 清洗、diff）；L1213 起主组件 `EditorPage()` 一路写到文件尾——**4348 行单组件**，占全文件 78%。

## 内部结构

纯函数四簇：LaTeX 折叠（`latexFoldService` L342，环境/章节/条件块/display math 四种折叠器）；文件树与大纲（`buildTree` L416 按 fileOrder 排序、`parseOutline` L492 正则扫 section）；LLM 输出防炸（`safeJsonParse` L628）；补全（`latexCompletionSource` L644-703 内置 12 个 snippet）。装饰三件套：`GhostWidget` L707 + `ghostField` L724-750（AI 幽灵文本，`setGhostEffect` L705 驱动）；环境深度着色（`computeEnvDepths` L761 配平 `\begin/\end` → `envDepthField` L783 → `ScopeMarker` L791 彩色嵌套条 → `scopeGutter` L806，六色 `SCOPE_COLORS` L752）；`editorTheme` L816。编辑器创建 L1697-1721：`EditorState.create` 挂 `latex()` 语法包、`foldService.of(latexFoldService)`、`collabCompartment.of([])`、`autocompletion({override:[latexCompletionSource]})`，再 `new EditorView`。

## 外部连接

导入面极宽（L1-48）：CodeMirror 六包、`pdfjs-dist`（L49 worker 走 `?url`）、`diff` 库、`yjs`/`y-protocols`/`y-codemirror.next`（L40-43）、client.ts 24 个函数（L21-42）。**localStorage 键 `openprism-settings-v1` 是三方契约**：本文件 L110 定义、`loadSettings` L127-147 读取（仅校验 `compileEngine` 枚举）、`persistSettings` L149-156 全量写回；ProjectPage.tsx:25/58 用 `{...prev,...s}` 增量写；TransferPanel.tsx:47/59-77 额外读写 `mineruApiBase/mineruToken`——这两个字段**不在** EditorPage 的 `AppSettings` 类型（L73-86），全靠 `...parsed` 展开侥幸存活，哪天改成白名单构造就静默丢配置。

## 数据流

幽灵补全主线：`Alt-/` 或 `Mod-Space`（keymap L1650-1660，capture 阶段 `handleAltSlash` L1723 兜底 Mac `÷` 键）→ `requestInlineSuggestion` L1864 取光标前 4000/后 400 字符 + 标题 + 环境 → `runAgent({task:'autocomplete',mode:'direct'})` L1879 → set 进 `ghostField` L1902-1904。采纳两级：`Tab` 全收（L1679 → `acceptInlineSuggestion` L1804），`ArrowRight` 逐词收（L1666 → `acceptSuggestionChunk` L1817，剩余重新挂回幽灵位）。协同支线 effect L1493-1542：`new Y.Doc()` → `new Awareness` → `new CollabProvider` L1500 → `collabCompartment.reconfigure(yCollab(ytext,awareness))` L1512，断线 reconfigure 空数组（L1467/1479/1539），编辑器不重建。

## 设计决策（含批判）

亮点是 CodeMirror6 扩展架构用得地道：三块自研能力全走 StateField+Decoration 正规军，主组件只 dispatch effect。批判三点：4348 行单组件 = 40+ useState 与十余 effect 纠缠，`requestSuggestionRef` 类补丁就是 ref 依赖债的利息；幽灵文本自造轮子不用官方 inline suggestion API，滚动同步要手写（`updateSuggestionPosition` L1839-1863）；`latexCompletionSource` 的 12 个 options 每次 keystroke 重建数组，与静态数据不匹配。

## 新人提示

改文件先确认落点：纯函数段随便加（无状态可测），主组件内先 grep 现有 ref/state。设置字段三处消费者任何 schema 变更要三方核对，尤其 mineru 两字段的"类型外"生存方式。补全调不出按链路排查：快捷键→`isSuggesting` 互斥→llmConfig→`res.suggestion||res.reply` 回退 L1899。折叠改动务必跑 `stripLatexComment` L219 路径——注释里的 `\begin` 会骗过裸正则。
