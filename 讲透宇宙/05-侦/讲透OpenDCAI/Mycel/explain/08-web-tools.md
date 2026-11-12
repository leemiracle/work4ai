# 08 · web 工具族与 LSP / 文件系统服务

## 角色定位

core/tools/ 下除 command/search 外的三块"外部世界接口"：`web/` 给 agent 联网能力（WebSearch 搜索 + WebFetch 抓取并 AI 提取），`lsp/` 给代码智能（9 种 LSP 操作双通道实现），`filesystem/` 给受控文件读写（Read/Write/Edit/list_dir 四工具）。三者共性：全部走 ToolRegistry 注册、Web/LSP 是 DEFERRED 模式（按需暴露给模型）、filesystem 是 INLINE 模式；LSP 与 Read/list_dir 标 read-only+concurrency-safe，Edit/Write 不是——这个标志位直接决定 runtime 能否并行调度。

## 内部结构

**WebService**（core/tools/web/service.py）注册 WebSearch/WebFetch 两个 DEFERRED 工具。构造函数按 **API key 有无**顺序装配 provider 列表（service.py:34-45）：searchers 依次 Tavily→Exa→Firecrawl；fetchers 是 Jina（有 key 才加）→ Markdownify（无条件兜底）。**关键事实：执行时只取 `[0]`**——`_web_search` 里 `searcher = self._searchers[0][1]`（service.py:136），`_web_fetch` 里 `fetcher = self._fetchers[0][1]`（service.py:152）。构造顺序即优先级，**没有任何降级链**：首选 searcher 抛错整个工具报错，不会轮询第二家。WebFetch 抓回内容超 100,000 字符截断（service.py:161-163），然后 `_ai_extract` 用注入的 extraction model 做定向提取（30s 超时，`callbacks=[]` 防递归追踪，service.py:180-183）；模型未注入直接 RuntimeError（:170）。

**searchers 三家**（各 69-77 行）实现差异是安全与语义的重点：
- Tavily（tavily.py:31-36）：**api_key 塞进 POST 请求体**（`payload["api_key"]`），不走 Authorization 头——key 会进代理日志/请求体 dump 的暴露面；include/exclude_domains 由服务端执行（tavily.py:38-42）。
- Exa（exa.py:31-50）：Bearer 头 + `type: "neural"` + useAutopilot，domains 过滤同样服务端。
- Firecrawl（firecrawl.py:50-54）：Bearer 头，但 **include/exclude_domains 是客户端子串过滤** `domain in url`——语义与服务端过滤不同：子串匹配会把 `notexample.com` 判中 `example.com`；且过滤发生在取回全部结果**之后**，`limit` 个结果被过滤后实际返回更少。

**fetchers 两级**：JinaFetcher（jina.py:27-30）走 r.jina.ai Reader，Bearer 头 + `X-Return-Format: markdown`，标题取首个 `#` 行（:45-47）。MarkdownifyFetcher（markdownify.py:85-90）是三级递降的本地 HTML 处理：markdownify 库可用→bs4 提取→纯正则剥标签；统一先 decompose script/style/nav/footer/header/aside（:108），主体选择 main→article→div.content→body（:111），浏览器 UA 伪装（:29）。

**LSP 双通道**（core/tools/lsp/service.py，746 行）：
- 9 个操作（:33-43），8 语言后缀映射（:74-86）。`_ADVANCED_OPS` 四操作（goToImplementation/prepareCallHierarchy/incomingCalls/outgoingCalls，:458）在 Python 走 **pyright 手写通道**，其余全部走 **multilspy 通道**。
- `_PyrightSession`（:101-281）是从零手写的 JSON-RPC 帧协议：Content-Length 头解析读循环（:141-157）、future 路由表 `_pending`（:166-172）、服务端反向请求自动应答（:162-165）、其余通知静默丢弃（:173）。
- `_LSPSession`（:284-397）包装 multilspy（注释称 core dep always available，:305），multilspy 对空响应 assert 崩溃被 except AssertionError 吞成空列表（:330-334）。
- `_LSPSessionPool`（:400-449）按 (language, workspace_root) 去重，in-flight start task 防并发重复起服务。
- 边界约定：@@@dt-04-lsp-position-contract——对外 1-based、进 LSP 前 -1（:642-646）；10MB 文件闸（:15，_check_file :490-499）；结果过 `git check-ignore` 过滤且 fail-open（:501-518），50 条一批（:520-524）。

**FileSystemService**（core/tools/filesystem/service.py，780 行）核心是**读后编辑门**：`_ReadFileStateCache` 是 OrderedDict LRU（默认 100 条，:43-63），Read 时记录 (mtime, is_partial)；`_check_file_staleness`（:449-461）三连拒：没读过 / 只读了部分 / mtime 变了。`_edit_file`（:685-752）在 `threading.Lock` 临界区里做 **两次** staleness 检查（:707 与 :718，@@@edit-critical-staleness 注释说明第二次防 preflight 后外部写入）。Write 强制 LF 归一（:482-483）；Read preflight 按 `file_size//4` 估 token 超限强制分页（:373-386，错误码 READ_REQUIRES_PAGINATION）。

## 外部连接

WebService 的四个 key 来自 runtime.json tools.web 节（tavily/exa/firecrawl/jina_api_key）；extraction_model 由 agent 装配时注入。LSP pyright 通道要求 pyright-langserver 可执行（`_find_pyright` 优先当前 venv bin，:89-98）。FileSystemService 的 backend 可换——本地 LocalBackend 或远端 sandbox 的 FileSystemBackend（远端路径统一 PurePosixPath，@@@remote-posix-path-contract :31-34），远程特殊文件走 download_bytes 钩子临时落盘复用本地解析器（:604-642）。operation_recorder 把每次写/编辑的前后全文记进 thread 检查点（:528-555）。

## 数据流

WebSearch：模型调用（query/max_results/allowed_domains）→ 首选 searcher.search → error 即 RuntimeError → format_output 文本返回。WebFetch：URL → 首选 fetcher → markdown → 截断 → LLM 提取 prompt（"URL+网页内容+用户请求"三段式，:172-178）→ 答案文本。LSP：operation+file_path → 语言探测/显式 language → 池取会话（必要时启动，60s 超时）→ 1-based 转 0-based → 会话请求 → gitignore 过滤 → 统一 _fmt_location/_fmt_symbol JSON 返回。Edit：preflight（路径+扩展名+.ipynb 拒绝）→ 临界区：读全文→两次 staleness→唯一性检查（count>1 且非 replace_all 拒绝）→ 写回→更新 LRU→记录 operation。

## 设计决策（含批判）

- **`[0]` 而非降级链**：列表结构暗示多 provider，实现只用第一个——配了 Tavily 又配 Exa 的用户会以为有容错，实际 Exa 纯摆设。要么改成轮询降级，要么构造时就只留一个，别留半成品抽象。
- **Tavily key 走请求体**是历史 API 风格，但与另两家 Bearer 头不一致，安全审计时是明显的不一致点。
- **LSP 双通道是务实妥协**：multilspy（Jedi 后端）不支持 callHierarchy/implementation，作者没等上游，直接为 Python 手写 pyright 帧协议——代价是 180 行协议代码要自己维护读循环竞态。
- **Edit 双重 staleness + 锁**把"两个并发编辑基于同一快照提交"的竞态堵死，这是对标 Claude Code 行为（dt-01/te-06 注释）的正确工程；但 `threading.Lock` 在 asyncio 单线程模型里主要防的是线程池路径，纯 async 下第一道检查已够。
- **is_error 字符串启发式**（runner 侧）与 Firecrawl 客户端过滤一样，都是"能跑但对边界不友好"的典型。

## 新人提示

1. 加新 searcher 别只往 `_searchers` 列表 append——记住只有 `[0]` 生效，想真生效得调整构造顺序（改 if 链）。
2. LSP 调试先看会话池：服务起不来 60s 超时报错，多半是语言服务器二进制缺失（pyright 要 `pip install pyright`，:113）。
3. Edit 报 "File has not been read yet / modified since last read" 不是 bug 是设计：先 Read 全文（不能带 offset/limit，partial 也拒），这是给模型的护栏。
4. 远端沙箱里路径全是 POSIX 语义，Windows 宿主上调试时别用 `\\` 拼路径。
