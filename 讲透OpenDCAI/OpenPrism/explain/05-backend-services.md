# 05 Node backend：入口、十组路由与领域服务

## 角色定位

`apps/backend/src/` 是 Node 18+ ESM + Fastify 单进程后端：API 面、LaTeX 编译、LLM 代理、文件管理、协作中枢全在此。**入口 index.js 仅 107 行**，职责是装配而非逻辑：注册三插件（cors/multipart/websocket，L25-31）、preHandler 鉴权门（L34-44）、**十组路由**（L7-16 import，L46-55 注册：health/arxiv/projects/compile/llm/vision/plot/agent/collab/transfer）、静态托管前端 dist 与 SPA fallback（L62-78）、启动 tunnel（L88-107）。README 结构图（README.md:584-592）只画 `routes/transfer.js` 一支，口径远小于十个路由文件的实况。

## 内部结构

鉴权门（L34-44）：非 `/api`、OPTIONS、`/api/health`、`/api/collab` 四类放行，其余走 `requireAuthIfRemote`——本机 IP 免鉴权、远程须协作 token（authUtils.js）。multipart 上限 200MB（L26-30）。

领域服务全景（`services/` 十个文件 + collab/transferAgent 子目录）：

- **compileService.js**：五引擎白名单 `SUPPORTED_ENGINES`（L9）；`buildCommand` L11-24 分引擎拼命令行；pdflatex/xelatex/lualatex 走"编译→bib→编译×2"三趟（L75-117），biber/bibtex 甄别靠嗅探 .aux 里的 `\abx@aux@`（L84）+ 源码 `\usepackage{biblatex}` 兜底（L91）；产物在 `.compile/<uuid>/` 读 base64 后整目录删（L119-133）；日志封顶 200KB（L57）。
- **mineruService.js**：预签名上传→轮询，`pollMineruResult` L118-167 循环 `MINERU_MAX_POLL_ATTEMPTS=200` 次、每次 sleep `MINERU_POLL_INTERVAL_MS=3000`（constants.js:22-23），**3 秒×200 轮=最长 10 分钟**轮询天花板。
- **agentService.js**：见第 3 篇（7 工具 LangChain agent）。
- **llmService.js**（64 行）：`normalizeChatEndpoint` L1-11 智能补 `/v1/chat/completions` 后缀，`callOpenAICompatible` 裸 fetch 直调兼容端点。
- 其余：arxivService（Atom 解析+bibtex+e-print 下载）、plotService、templateService（见第 6 篇）、projectService（10 行项目根定位）。

## 外部连接

出站依赖四类：本地 TeX 发行版（spawn pdflatex 等，不在 PATH 即报 "not available"）、MinerU 云 API、export.arxiv.org、用户自配 OpenAI 兼容 LLM 端点。入站除前端还可能接公网——tunnel.js 三供应商降级链：`auto` 模式按 localtunnel→cloudflared→ngrok 顺序尝试（L15-21），**全部动态 import**（L34/63/94），装了哪个用哪个零依赖启动；localtunnel 断线 3 秒重连（L43-52）；cloudflared 是 spawn 二进制（L65）从 stdout 正则抓 `*.trycloudflare.com` URL（L75，30 秒超时）。

## 数据流

一次编译：前端 `compileProject` → `/api/compile`（compile.js:5-14 校验白名单）→ `runCompile` → safeJoin 定位主文件 → `.compile/<uuid>` 三趟编译 → PDF base64 + log 回传 → 临时目录删除。一次 zip 导入：`/api/projects/import-zip`（projects.js:56-100）流式 `unzipper.Parse`（L74）→ **双层防穿越**：`sanitizeUploadPath` 剥 `..` 与绝对路径（pathUtils.js:11-16）+ `safeJoin` resolve 后必须仍在项目根内（pathUtils.js:3-9，L81 再拦）→ zip 内 `project.json` 主动丢弃（L77-78）→ 失败整体 `rm -rf`（L92）。

## 设计决策（含批判）

亮点：spawn 编译器而非 wasm 方案，保真多引擎；zip 双层防穿越 + autodrain 稳健；tunnel 动态 import 让远程协作成为可选件。批判三点：其一，`runCompile` 的 `code` 只保留最后一趟退出码（L115-116），bib 失败被吞，排查得肉眼读 log；其二，同步轮询 MinerU 200 轮无指数退避无早停；其三，`requireAuthIfRemote` 以 IP 判信任，tunnel 模式下请求经代理回环，安全模型退化为"有 token 才能写"，读接口是否豁免值得复核。

## 新人提示

路由必经三站：routes/ 薄壳 → services/ 逻辑 → utils/（safeJoin/fsUtils/i18n）。写新端点记得 preHandler 自动套鉴权，想豁免要改 index.js:35-38 前缀清单。编译失败先看 log 字段（200KB 截断）而非 error。部署 checklist：TeX 发行版装齐、`OPENPRISM_COLLAB_TOKEN_SECRET` 必设（第 4 篇）、tunnel 供应商任装其一。
