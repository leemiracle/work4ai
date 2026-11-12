# OpenPrism ONBOARDING.md（新人入门）

> 依据图谱（285 节点/671 边/14 层/15 步 tour，commit d383c04）撰写，行号锚均经源码核实。

## 1. 一句话定位

OpenPrism 是 OpenDCAI org 下的 local-first「LaTeX+AI」学术写作平台：把 OpenAI Prism（2026-01 云端 LaTeX 产品）做成数据不出域的自托管开源替代（README_ZH.md:267）。npm workspaces 三区 monorepo——apps/frontend（React 18+Vite：CodeMirror 6+pdf.js+i18next 双语）、apps/backend（Fastify+LangChain/LangGraph+Yjs）、packages/shared（仅 1 文件）。五大能力：AI 助手三模式（chat/direct/tools）、服务器五引擎编译、会议模板库（ACL/CVPR/NeurIPS/ICML）、transferAgent 论文迁移（LangGraph 编排，Legacy/MinerU 双管线）、Yjs CRDT 协同（手写 y-protocols，非 y-websocket 库）；另有 vendored SwiftLaTeX pdfTeX wasm 免装编译。

## 2. 心智模型

- **双进程双端口**：backend 监听 8787（constants.js:10，README.md:325）；frontend Vite dev server 5173，/api（含 WebSocket）代理到 8787、/texlive 代理到 texlive.swiftlatex.com 供 wasm 拉宏包（vite.config.ts:7-19）。全仓不存在 8788 端口。
- **迁移编排在后端，前端只轮询**：legacy 线 graph.js 走 analyzeSource→analyzeTarget→draftPlan→applyTransfer→copyAssets→compile（graph.js:69-73）；MinerU 线 graphMineru.js 前置 compileSource→parsePdfWithMineru（graphMineru.js:72-76），两图共享状态与修复环。前端 TransferPanel.tsx 无流程图库（无 React Flow），只是 1 秒一轮轮询驱动。
- **协同是手写 Yjs**：docStore.js 用 lib0 手写 y-protocols 二进制 sync/awareness 协议（docStore.js:136,157,167）；provider.ts 手写 WebSocket 客户端（消息 0=sync、1=awareness）。没有 y-websocket，改协议必须两端同步改。
- **LLM 单一出口**：llmService.js 零依赖 fetch 实现 OpenAI 兼容调用，五线全走它，换模型只动 OPENPRISM_LLM_* 或前端设置。
- **鉴权**：本地免鉴权、远程强制 token（authUtils.js:36；隧道模式忽略 x-forwarded-for，:12-15）。

## 3. 代码地图（图谱 14 层）

- L01 门面：双语 README、根 package.json、packages/shared/types.ts（前后端唯一共享契约 AgentResponse）。
- L02 前端基座：main.tsx:10-18→App.tsx:10-14 四路由（/、/projects、/editor/:projectId、/collab）；vite.config.ts。
- L03 页面与 API：LandingPage、ProjectPage（列表/画廊/zip 与 arXiv SSE 导入）、api/client.ts（44 个导出函数；:94 Bearer、:100 x-lang）。
- L04 编辑器核心：EditorPage.tsx 5560 行巨兽（:1213 才是主组件）、latex/lang.ts、latex/engine.ts。
- L05 wasm 引擎：public/latex/swiftlatexpdftex.js+wasm（Worker 内建 /tex、/work 虚拟文件系统）。
- L06 后端基座：index.js（:34 preHandler、:46-55 十组路由、:71 SPA fallback、:82 listen、:88 隧道）、constants.js、i18n、authUtils。
- L07 常规路由：projects.js（23 端点+safeJoin 防穿越）、compile/health/arxiv/llm/vision/plot/agent 八件套。
- L08 领域服务：llmService（LLM 唯一出口）、compileService（:41 runCompile、:79-95 bibtex/biber 探测）、agentService（:34-138 七工具）、mineru/arxiv/template/project/plot/tunnel 等服务。
- L09 工具箱：fsUtils、pathUtils（safeJoin）、texUtils、diffUtils。
- L10 transferAgent（19 文件）：routes/transfer.js、graph.js/graphMineru.js、state.js:6（Annotation.Root 30+ 字段）、13 节点、utils.js、TransferPanel.tsx。
- L11 协同五件套：collab.js（:11 invite、:18 resolve、:37 flush、:47 status、:57 WebSocket）、docStore.js、tokenService.js、provider.ts、CollabJoinPage.tsx。
- L12/13 模板：ACL（acl.sty+1940 行 bst）与 CVPR（cvpr.sty+\input 分节+rebuttal.tex）官方包；arxiv/icml/neurips 骨架+manifest.json 注册表。
- L14 i18n 与样式：i18n/index.ts（中文整句作键，zh-CN.json 492 键）、App.css（3741 行纸张质感设计令牌）。

## 4. 核心链路走读：一次论文迁移（MinerU 模式，PDF→CVPR 模板）

1. TransferPanel 传 PDF→/api/transfer/upload-pdf（transfer.js:282）；/api/transfer/start-mineru（:198）从模板建项目+建图，jobId→{graph,...,iterator} 存内存 Map（:13,83）。
2. compileSource：已有直传 PDF 则跳过，否则先把源项目编成 PDF。
3. parsePdfWithMineru（mineruService.js:318）：申请上传 URL→上传→3s×最多 200 轮询（constants.js:22-23）→下载 zip→解压 markdown+图片到 _mineru_output/。
4. analyzeTarget 展开模板提大纲；applyTransfer 走 Markdown→LaTeX 填模板 LLM 线，经 writeFileWithSnapshot 快照写回（utils.js:165）。legacy 线为整文迁移，前置 analyzeSource/draftPlan 做映射。
5. copyAssets 拷图片/bib；compile 调 runCompile（compileService.js:41）：三遍编译+按 .aux 标记探测 biber/bibtex（:79-95）。
6. 失败→fixCompile（读日志尾 8000 字符交 LLM 修）→compile 回环（graph.js:83）。
7. interruptBefore:['checkLayout']（graph.js:104、graphMineru.js:107）暂停置 waiting_images，前端渲染 PDF 截图回传（TransferPanel.tsx:230、transfer.js:143）；checkLayout 送 VLM 查溢出/重叠（最多 2 次纠错），有问题→fixLayout→compile 回环，finalize 判定成败。
8. 全程由前端 runGraph 每 1s 调 transferStep 步进（TransferPanel.tsx:221,225,235）。之后开协同：EditorPage.tsx:1512 以 yCollab 接入 Yjs，WebSocket 连 /api/collab（collab.js:57），docStore 广播并 800ms debounce 落盘（docStore.js:62-70）。

## 5. 运行与调试

- 本地：npm install→npm run dev（concurrently 起 8787+5173），访问 http://localhost:5173；可单起 dev:backend/dev:frontend。
- 隧道/生产三供应商：build 后 npm run tunnel（localtunnel）/tunnel:cf（cloudflared）/tunnel:ngrok——注入 OPENPRISM_TUNNEL 直起 backend 并托管 dist+SPA fallback（index.js:57-71）；tunnel.js 按序降级，失败仅告警。
- 环境变量全 OPENPRISM_* 前缀（constants.js）：DATA_DIR/LLM_*/COLLAB_TOKEN_SECRET/TUNNEL；MinerU 走 mineru.net/api/v4（:21）+自备 token。
- 调试：迁移卡住→GET /api/transfer/status/:jobId（transfer.js:176）看 progressLog；编译失败看返回 log；协同异常→GET /api/projects/:id/collab/status（collab.js:47）+POST flush（:37）。vite 代理仅 dev 有效。

## 6. 已知坑（第一次接触必读）

1. **协作密钥硬编码开发默认值（安全）**：不设 OPENPRISM_COLLAB_TOKEN_SECRET 时 fallback 'openprism-collab-dev'（constants.js:11），用于 HMAC 签协作邀请 token（tokenService.js:18）——开隧道公网暴露即邀请令牌可被伪造，生产必改（README_ZH 有专节警告）。
2. **transfer 任务态存内存，重启即丢**：jobs Map（transfer.js:13）+MemorySaver（graph.js:102）双内存态，重启全蒸发、多实例不可扩展；每步快照落盘（utils.js:165）是唯一救援。
3. **仓库根没有 LICENSE**：全仓唯一许可文本是 templates/arxiv/License.txt（上游作者的 MIT），二次分发前先补授权。
4. **templates/arxiv/ 未注册且自动补录指错入口**：manifest.json 只登记 acl/cvpr/neurips/icml；templateService.js:17-42 会把含 .tex 的未注册目录自动补录，但 mainFile 硬编码 'main.tex'（:34），而 arxiv/ 入口实为 template.tex 且无 main.tex——projects.js:381 按此取主文件会踩空，用前先正式注册。
5. **中英 README 代差**：ZH 760 行 vs EN 695 行；ZH 独有「最新动态」等节，且 :265-336 的「OpenPrism vs Prism 六节对照表」整体包在 HTML 注释里（GitHub 不渲染），英文版没有对比表——两边都读，源码为最终裁判。
6. **EditorPage.tsx 5560 行巨兽阅读法**：主组件 :1213 才开始，前 1212 行全是 helper/子组件；组件内 80 个 useState+28 个 useEffect。别顺序通读——先读 :1213 起 state 区，再按功能 grep：协同 :1512、幽灵补全 :1625-1789、pdf.js :15-17。
7. **packages/* workspace 名不副实**：共享包只有 types.ts 一个文件一个接口，前后端类型各自维护，改契约要两端手改。

## 7. 上游与生态

- **SwiftLaTeX**：public/latex/ 产物 vendored 自上游，浏览器端跑完整 pdfTeX，宏包从 texlive.swiftlatex.com 拉取——内网部署注意这条外网依赖。
- **MinerU**：云端 PDF 解析（mineru.net/api/v4），mineruService 是纯客户端；离线时 MinerU 模式不可用（legacy 线不受影响）。
- **Yjs**：CRDT 内核是正牌 yjs+y-protocols+lib0+y-codemirror.next，网络层全手写（等价精简版 y-websocket），读懂 docStore.js 即读懂 sync 协议。
- **LangChain/LangGraph**：agentService 七工具 agent 与 transferAgent 状态图（StateGraph+MemorySaver+interruptBefore 人机中断）是好的落地样本。
- **OpenDCAI org**：以 DataFlow 数据清洗闻名；OpenPrism 是 org 内独立写作工具仓，与其余仓无代码耦合，共享自托管语境。

## 8. 学习路径（15 步 tour 与 explain 6 篇怎么配）

tour 15 步分三段按序走：**前端段（01-05）** README 门面→启动链四路由→工作台与 client.ts→EditorPage 巨兽→wasm 引擎，配 explain 01/02 篇；**后端段（06-10）** 入口与鉴权闸→项目文件域→五引擎编译链→LLM 基础设施→工具 agent，配 05 篇；**特性段（11-15）** 迁移编排与节点内景（11-12）→协同链路（13）→模板群（14）→i18n 收尾（15），配 03/04/06 篇。

实操：npm run dev→CVPR 模板建项目体验编译→跑一次 MinerU 迁移盯 progressLog→双窗口走协同邀请→精读 transferAgent 节点与 docStore。一周节奏：D1-2 前端、D3 后端服务、D4 迁移子系统（密度最高）、D5 协同+模板，即可上手改 feature。
