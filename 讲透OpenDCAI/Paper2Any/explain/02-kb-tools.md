# 02 · 知识库工作台与八工具：KnowledgeBase 前端全解

## 角色定位

`components/knowledge-base/`（index.tsx 861 行 + 7 视图 + tools 9 件）是平台"素材进、知识出"的中枢页面：左侧四节导航、中间素材列表、右侧八工具面板的三栏工作台。它与 01 篇的全局链路不同——这里自带一套"三数据源并存"的持久化策略（Supabase 两表 + localStorage 产出账本），并把八个生成工具（问答/检索/深研/报告/PPT/导图/播客/视频）做成同一 RightPanel 下的可切换面板。它是理解产品"个人知识资产化"定位的最佳入口。

## 内部结构

**容器与四节视图**：`KnowledgeBase`（index.tsx:18）持有全部状态：`activeSection`（SectionType 四值 `library|upload|output|settings`，types.ts:38）与 `activeTool`（ToolType 八值，types.ts:39）。Sidebar 四节按钮带计数徽章（Sidebar.tsx:47-51），折叠态宽度 72/260px 且状态持久到 localStorage（index.tsx:47-50、104-107）。中间区按节渲染 Library/Upload/Output/Settings 四视图。

**三数据源**：①素材库 = Supabase `knowledge_base_files` 表按 user_id 直查（index.tsx:145-149），行映射时把 storage_path 不含 `/outputs` 的改写为 `/outputs/kb_data/{email}/{file_name}`（index.tsx:164）；②知识库列表 = `knowledge_bases` 表（index.tsx:177-181）；③知识产出 = **localStorage 账本**而非数据库——`getOutputStorageKey()` 返回 `kb_outputs_{user.id}`（index.tsx:216-219），产出文件以 JSON 数组读写（index.tsx:66-97），换浏览器即丢。上传是两段式：先 POST `/api/v1/kb/upload` 拿 `static_url`（UploadView.tsx:104），再 insert `knowledge_base_files` 行登记（UploadView.tsx:119-125）。

**RightPanel 八工具装载**：ToolSelector 枚举八项（ToolSelector.tsx:11-18：智能问答/语义检索/深度研究/报告生成/PPT 生成/思维导图/知识播客/视频讲解）。RightPanel 的装载方式值得注意——**八工具全部同时挂载**，用 `translate-x-full opacity-0 pointer-events-none` 的 CSS 滑出动画切换（RightPanel.tsx:92-111）而非条件卸载，保状态但常驻内存。

**ChatTool 非流式问答**（320 行）：POST `/api/v1/kb/chat`（ChatTool.tsx:203-219），body 携勾选文件 url 列表 + query + history（welcome 消息剔除，ChatTool.tsx:198-201），等完整 JSON 一次性返回 `data.answer`（ChatTool.tsx:225-230）——无 SSE/WebSocket，长回答期间只有"思考中"骨架屏（ChatTool.tsx:288-295）。响应里的 `file_analyses` 以可折叠"思考过程/文件分析"渲染（ChatTool.tsx:273-284）。计费模式下前端自带 api_url/api_key 随请求透传（ChatTool.tsx:212-217）。

**手写 Markdown 渲染器**：ChatTool 没用 markdown 库，自写两级管线——`renderInline`（ChatTool.tsx:20-27）先 `escapeHtml` 再正则替换行内码/粗体/斜体/链接；`renderMarkdownToHtml`（ChatTool.tsx:29-109）先按 ``` 围栏切出代码块（保留语言名、内容再 escape），文本块逐行识别 heading（`#{1,6}`）/无序（`[-*]`）/有序（`\d+\.`）列表并维护 ul/ol 开闭栈，最后 `dangerouslySetInnerHTML` 注入（ChatTool.tsx:111-116）。

**DeepResearch 双模式**：`mode: 'llm' | 'web'`（DeepResearchTool.tsx:33）。llm 模式纯模型总结；web 模式追加搜索参数 `search_provider/search_engine/search_num/brave_summarizer`，且 google_cse 必须填 cx（DeepResearchTool.tsx:99-107）。POST `/api/v1/kb/deep-research`（DeepResearchTool.tsx:115）一次返回 `report_markdown/search_results/summaries/report_path`（DeepResearchTool.tsx:159-163），产出自动登记进 output 账本。错误文案直接教用户排查（401 提示 VITE_API_KEY 与后端一致、404 提示后端未加载路由，DeepResearchTool.tsx:146-151）。

**Podcast 双 TTS 家族切换**：按 `tts_model` 名字分流——`isOpenAITtsModel` 匹配 `gpt-4o-mini-tts` 或 `tts-1` 前缀（PodcastTool.tsx:53-56），`isCosyVoiceTtsModel` 匹配 `cosyvoice-v3-flash/v3-plus/v2` 白名单（PodcastTool.tsx:10、58-60）；OpenAI 系显示 voice 下拉，CosyVoice 系 voice 置空由后端音色参数接管（PodcastTool.tsx:92-94、108）。默认脚本模型 gpt-5.1 + TTS cosyvoice-v3-flash（PodcastTool.tsx:84-85），双声部 A/B（voice_name/voice_name_b）。POST `/api/v1/kb/generate-podcast`（PodcastTool.tsx:147）。

**MindMapFlowEditor 三层双向转换**（300 行）：Mermaid 文本 ↔ TreeNode 树 ↔ ReactFlow 图三层表示。`buildTreeFromMermaid`（MindMapFlowEditor.tsx:27-68）按缩进栈解析（每 2 空格一层深度，L42），`normalizeLabel` 剥 `root((x))` 与 `[x]` 语法（L18-25）；`buildFlowFromTree`（L70-111）做 depth×240 / 序号×110 的网格布局，smoothstep 边；`flowToMermaid`（L113-151）反向：以"无入边节点"定位根（L119-120）、子节点按 y 坐标排序恢复顺序（L131-133）、两空格缩进序列化。双向触发：外部 mermaidCode 变化 useEffect 重建画布（L163-168），画布编辑后"应用到代码"按钮 `onApply(flowToMermaid(...))` 回写（L232）。全屏编辑用 createPortal 挂 document.body（L271-297）。

**Mermaid 预览**：MermaidPreview 用 mermaid npm 包客户端渲染——`mermaid.initialize` 暗色主题（MermaidPreview.tsx:26）、`mermaid.render(id, code)` 得 svg 注入（MermaidPreview.tsx:56-57），渲染失败降级显示错误与原文。

**导图草稿保存**：预览抽屉里 mindmap 草稿可保存回后端——POST `/api/v1/kb/save-mindmap`（index.tsx:314），成功后把预览文件 url 替换为返回的 `mindmap_path`（index.tsx:333-335），草稿/预览码双态（`mindmapViewMode: 'visual' | 'code'`，index.tsx:40）。

## 外部连接

- **FastAPI kb 路由族**：`/api/v1/kb/{upload,chat,deep-research,generate-podcast,save-mindmap}` 等八个端点，全部经 backendFetch 双鉴权；后端再下沉到 services 与 wf_kb_* 工作流图（见 03/06 篇）。
- **Supabase**：knowledge_base_files/knowledge_bases 两表读写 + RLS；删除素材直接 delete 行（index.tsx:268-274）。
- **secureAssetService**：受保护文件预览走 `getSecureAssetUrl` 换临时访问链接（index.tsx:123），文本读取 `fetchProtectedText` 同链路（index.tsx:230-237）。
- **用户 API 设置**：apiSettingsService 按用户存自备 LLM 网关地址/密钥（ChatTool.tsx:157-163），计费模式（useRuntimeBilling 的 userApiConfigRequired）决定是否随请求上送。
- **App 壳**：由 App.tsx `activePage === 'knowledge'` 挂载（App.tsx:256）。

## 数据流

冷启动：user 就绪 → 并行拉 library files 与 knowledge_bases（index.tsx:59-64），output 账本从 localStorage 恢复（index.tsx:66-91）。上传流：UploadView 选文件 → POST /api/v1/kb/upload 落静态目录 → insert 元数据行 → 回调刷新素材库并跳回 library 节（index.tsx:277-281）。生成流：勾选素材（selectedIds Set，index.tsx:263-271）→ RightPanel 工具取 files×selectedIds 过滤出 url 列表 → POST 对应端点 → onGenerateSuccess 把新产出 unshift 进 outputFiles 并写回 localStorage（index.tsx:283-286）。问答流：Enter 发送 → 历史拼接 → 一次性响应 → 消息列表追加。导图流：MindMapTool 生成 mermaid → 预览（MermaidPreview）→ FlowEditor 可视化编辑 → apply 回写 code → save-mindmap 持久化。

## 设计决策（含批判）

1. **三数据源异构并存是"快糙猛"与产品现实的折中**：素材进 Postgres（Supabase）、产出进 localStorage，语义上"产出只是素材的衍生视图、丢了可重生成"，但用户视角产出与素材同等珍贵——清浏览器数据即静默丢失产出索引（文件本体仍在后端 outputs/，只是入口没了）。
2. **八工具全挂载 + CSS 切换**：切换零成本、状态全保留，代价是首挂载即渲染八棵组件树；对重型工具（Ppt/Video 表单）可接受，若未来加流式长任务工具会放大内存驻留。
3. **手写 Markdown 渲染器是脆弱性热点**：正则管线不支持表格/引用/嵌套列表，`escapeHtml` 先行保证了 XSS 基线安全（LLM 输出先转义再替换），但 `**bold**` 与 `[link](url)` 的正则互作用在边角文本（如未配对星号）会产生怪异输出；同仓明明已有 react-markdown（index.tsx:16 导入 ReactMarkdown），ChatTool 却手写一套——两套渲染并存是明显的不一致。
4. **非流式问答的体验取舍**：实现简单、错误处理集中，但长报告式回答用户要盯 30s+ 骨架屏；后端已有 SSE 能力（见 03 篇 paper2ppt 线）却未用于 chat，属于工具间体验不齐。
5. **Podcast 按模型名分流是隐式协议**：`tts_model` 字符串同时承担"选择供应商"与"选择模型"两个语义（OpenAI 前缀探测 vs CosyVoice 白名单），新增 TTS 供应商要同时改前端探测函数与后端路由，容易漏；显式的 provider 字段更稳。
6. **MindMapFlowEditor 的解析器只认规整缩进**：每 2 空格一层的假设（L42）遇上 tab 混排靠 L30 的 tab→2 空格预处理兜住，但奇数缩进会被 floor 吞层；flowToMermaid 用 y 坐标排序恢复子节点顺序（L131-133）意味着用户手动拖乱节点后"应用"会按位置重排语义——拖拽即重排序，既是特性也是坑。
7. **错误文案内嵌运维知识**：DeepResearch 的 401/404 提示直接写默认 key 值（DeepResearchTool.tsx:147），对用户友好，但也把内部默认凭据印在前端文案里，属可接受的取舍。

## 新人提示

- 加第九个工具的清单：types.ts:39 加 ToolType 值 → ToolSelector.tsx:11-18 加枚举 → RightPanel.tsx 加一块 translate-x 面板（import 并传 `files/selectedIds/onGenerateSuccess` 三件套），容器无需改动。
- 产出文件在 UI 里删不掉本体：`handleRemoveOutput` 只改 localStorage 账本（index.tsx:288-293），后端文件与素材库记录不受影响；素材库删除才动 Supabase 行（index.tsx:268-274）。
- 调试三数据源：素材看 Supabase 表 `knowledge_base_files`，产出看 DevTools → Application → Local Storage → `kb_outputs_{user.id}`；侧栏宽度/折叠也各自持久化（`kb_right_panel_width`/`kb_sidebar_collapsed`）。
- 预览受保护文件时若空白，先查 secureAssetService 换链是否 401——所有 `/outputs/` 资产都要先换临时访问 URL（index.tsx:109-141 的 previewAccess 状态机）。
- 手写 Markdown 渲染改样式直接编辑 ChatTool.tsx:29-109 的模板字符串；要支持表格请直接换 react-markdown，别往正则管线里加规则。
