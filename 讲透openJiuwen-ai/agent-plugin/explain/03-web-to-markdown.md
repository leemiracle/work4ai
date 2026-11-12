# 03 · web-to-markdown：真实可用插件的完整形态

## 一、角色定位

`plugins/web-to-markdown/` 是全仓两个在架插件中的"实战派"：抓取网页正文并转换为 Markdown。与 example-plugin 的"教科书"定位不同，它演示的是**一个要直面互联网险恶环境的 tool 应该怎么写**——342 行的 `tools/web_to_markdown_tool.py`（全仓最大插件文件）塞进了四层防御（SSRF、重定向、Content-Type、响应体限长）和一个纯 stdlib 的 HTML→Markdown 转换器。docstring（`web_to_markdown_tool.py:3-11`）把设计边界说得极清楚：纯标准库（urllib + html.parser + ipaddress + socket）、import 期无副作用仅在 invoke 内联网、只返回文本不写文件、四项安全约束逐条列出。

包结构上是"瘦身版教科书"：manifest 只声明 skills + tools 两段（`plugins/web-to-markdown/manifest.json:50-69`），**没有 rails 段**——纯转换型工具没有需要监听的生命周期事件，三组件不是每个包都得凑齐。这个"缺一段"本身就是教学：组件按需声明。

## 二、内部结构

单文件三层：安全层（L41-93）→ 转换层 `_MarkdownExtractor`（L96-222）→ 组件层 `WebToMarkdownTool`（L225-342）。

**安全层四件套**：

1. `_SSRFBlocked` 异常（L41-42）与 `_is_forbidden_ip()`（L45-54）：六连判断 `loopback/private/link_local/multicast/reserved/unspecified`，凡命中即拒绝——云元数据地址 169.254.169.254 天然被 `is_link_local` 覆盖（测试 `test_web_to_markdown.py:120` 专门验证）。
2. `_validate_host()`（L57-72）：`socket.getaddrinfo(host, None, AF_UNSPEC, SOCK_STREAM)`（L60）取**全部**解析结果逐个检查（L65-72）——注释点名"含 DNS 多地址场景"：一个域名同时解析出公网 IP 与内网 IP 时，任一命中即拒绝，堵死 DNS rebinding 的常见变体。解析失败的 `gaierror` 也转成 `_SSRFBlocked`（L61-62）。
3. `_validate_url_host()`（L75-81）：URL → hostname → 前者，无主机名即拒绝。
4. `_SafeRedirectHandler`（L84-93）：继承 `HTTPRedirectHandler`，`redirect_request()` 里先对 **newurl** 逐跳复检再放行（L91-93）——防止首次校验通过后经 3xx 跳内网。

**转换层 `_MarkdownExtractor(HTMLParser)`**（L96-222）：事件驱动状态机。跳过集合 `_SKIP_TAGS = {script, style, noscript, template, head}`（L103-109）用**计数器 dict** `_skip_counts`（L116）而非布尔——嵌套同名标签（script 里再出现 script 文本）也能正确配对进出（starttag 自增 L133-134，endtag 自减 L173-177）；`<body>` 起点还会清空残留计数（L129-132），兜住 head 未闭合的畸形页。映射规则集中在 `handle_starttag`（L125-167）/`handle_endtag`（L169-208）：h1-h6 → `#`*n（L156-158）、a → `[text](href)`（L145-147, 186-192，`#` 开头的锚点 href 丢弃只留文字 L189-192）、img → `![alt](src)`（L148-151）、strong/b 与 em/i（L152-155）、pre/code 围栏（L139-144，pre 内不再加行内反引号 L143）、blockquote（L164-165）、容器标签闭合统一双换行（L207-208）。`convert_charrefs=True`（L113）让实体解码交给基类。收尾 `result()`（L218-222）两个 re.sub：行尾空白删除（L220）与三连以上换行折叠为双换行（L221）。

**组件层 `WebToMarkdownTool(Tool)`**（L225-342）：ToolCard 声明 id `web_to_markdown`（L231）、参数 `url` 必填 + `timeout_seconds` 可选（L238-251）；`invoke()`（L255-287）编排全流程；`_extract_url()` 校验 `https?://` 前缀（L301）；`_extract_timeout()` 做 bool 排除与 1..120 钳制（L303-312）；`_fetch()`（L314-336）串起安全层；`_fallback_title()`（L338-342）在无 `<title>` 时用 URL 末段兜底。

## 三、外部连接

- **openjiuwen SDK**：仅 L24 一行 `from openjiuwen.core.foundation.tool import Tool, ToolCard`——与 example-plugin 完全同构的耦合面。
- **skill 侧**：`skills/web-to-markdown/SKILL.md` 工作流第 2 步调用本工具（`SKILL.md:18`），第 3 步裁决 `success`（L19），第 4-5 步按模板输出并可保存 `.md` 文件（L20-30）——**文件写入在 skill/智能体侧完成，tool 只返回文本**（docstring L8 明言"不写文件"）。tool 的 description 同样反向声明"需配合 web-to-markdown skill 使用"（`web_to_markdown_tool.py:236`）。
- **与 scripts/publish.py 的隐性约定**：L31 注释"与 scripts/publish.py 的 MAX_RESPONSE_BYTES 一致"——`scripts/publish.py:38` 确有同名常量同值 2MB。**两处 2MB 靠注释人工同步，无共享模块**（scripts/ 不允许被插件 import），这是本仓"插件与工具链互不依赖"架构的代价。
- **测试线**：`tests/plugins/web-to-markdown/test_web_to_markdown.py` 12 个测试同样 `importorskip("openjiuwen")` 整体跳过，但 HTML 转换断言纯本地不联网（L6 docstring）。覆盖三组：SSRF 拒绝（loopback L109、私网 L114、云元数据 L120）、公网 IP 放行（L125）、畸形 HTML 容错（未闭合 form L91、未闭合 svg L100）。

## 四、数据流

`invoke({"url": "https://example.com/article"})` 的完整旅程：

1. **入参裁决**（L256-262）：`_extract_url` 非 string 或无 http(s) 前缀 → 返回 `{"success": False, "error": "缺少必填参数 url…"}`；`_extract_timeout` 非法值回退 15s，bool 显式排除（`isinstance(True, int)` 在 Python 里是 True 的经典陷阱，L310 单独拦截），超出 1..120 钳到边界（L312）。
2. **抓取**（L264 → `_fetch` L314-336）：先 `_validate_url_host(url)` 前置校验（L316）→ `build_opener(_SafeRedirectHandler(_validate_url_host))` 构造带逐跳复检的 opener（L318）→ 请求带自定义 UA `Mozilla/5.0 (compatible; JiuwenSwarm/1.0; +https://openjiuwen.com)`（L27-29, L322）与 Accept 头（L323）→ `opener.open(request, timeout=timeout)`（L326）→ Content-Type 白名单校验 `text/html` 等 5 种（L327-329，二进制直接拒）→ `response.read(_MAX_RESPONSE_BYTES + 1)` **一次读到 2MB+1 字节**（L330），长度超限即抛错（L331-334）——+1 的巧劲在于无需循环分块也能判定"是否超限"。字符集按响应头回退 utf-8，`errors="replace"` 解码（L335-336）。
3. **异常分类上报**（L265-272）：`_SSRFBlocked` → "安全校验失败"；`HTTPError` → "HTTP 错误 {code}"；`URLError` → "网络请求失败"；其余兜底"抓取失败"（L271 带 `noqa: BLE001` 注释，明言"兜底网络异常，如实上报"）。四类错误都变成模型可读的中文 error 字段。
4. **转换**（L274-276）：`extractor.feed(html)` 驱动状态机，`result()` 收尾正则清理。
5. **title 与空正文裁决**（L277-280）：title 取 `<title>` 累积值（`handle_data` 里 `_in_title` 分支 L211-213）或 URL 末段兜底；markdown 为空 → 显式报"网页正文为空"。
6. **成功返回**（L282-287）：`{"success": True, "url", "title", "markdown"}` 四字段，交给 skill 层按 `# {title}\n> 来源：{url}\n{markdown}` 模板成稿（`SKILL.md:22-28`）。

## 五、设计决策与权衡

1. **为什么没有 rail**：本包的全部行为都在"一次工具调用"内完成，没有跨轮状态、没有会话级监听需求。rail 的价值在横向切面（计数、审计、注入），纵向单一动作用不上——**组件为需求服务，不为架构对称性服务**。对比 example-plugin 特意放一个 rail 是为了教学，这里不放同样是一种表态。
2. **stdlib HTMLParser 而非 BeautifulSoup/readability**：docstring 锁死"纯标准库"。收益是插件零 pip 依赖、热加载无版本冲突风险（agent 宿主环境不可控，第三方依赖是插件分发第一杀手）；代价是没有 DOM 树、没有 readability 式正文抽取——嵌套表格、复杂布局的还原度有限，`_list_stack`（L120）只 push 不消费就是明证：列表嵌套层级信息被采集了但输出不区分缩进。这是"可依赖性优先于转换精度"的取舍。
3. **SSRF 防御做在插件层而非宿主层**：理论上宿主可以统一管控出网，但插件作为"不可信代码单元"自带防御纵深——即使宿主疏忽，插件也不成为内网探测跳板。`getaddrinfo` 全量检查（L60-72）与逐跳重定向复检（L91-93）堵的是 TOCTOU 与 rebinding 两条经典绕过路径。残余风险：校验后再次解析时 DNS 可换答案（check-then-connect 窗口），彻底解法是解析后直接连 IP——urllib 做不到，属已知边界。
4. **2MB 限长的三重动机**：内存保护（正文读入内存）、prompt 保护（返回值进上下文）、与 publish.py 对齐（Hub 上传同限 2MB，L31 注释）。
5. **`+1` 读法与 `headers` 出 with 块**：L330 一次 `read(N+1)` 避免分块循环；L335-336 在 `with` 块外访问 `response.headers`——HTTPResponse 的 headers 属性在 close 后仍可读（解析期已缓存），这是依赖 stdlib 实现细节的写法，换 requests 等库未必成立。
6. **错误信息即 prompt**：四类异常的中文 message 会进入模型上下文（L266-272），模型据此向用户解释或决定重试。"HTTP 错误 404：{url}" 比 traceback 对模型友好得多——与 02 篇同一范式在真实网络场景的重演。

## 六、新人提示与坑

1. **改抓取逻辑前先跑 SSRF 测试**：`test_validate_host_rejects_*` 三个测试（`test_web_to_markdown.py:109-123`）是安全底线。尤其别把 `_is_forbidden_ip` 的六连判断删成"只查 private"——`is_unspecified`（0.0.0.0）与 `is_reserved` 各有对应攻击面。
2. **`_SKIP_TAGS` 是计数器不是集合开关**：嵌套 skip 靠 `_skip_counts[tag]` 自增自减配对（L133-134, L173-177）。若改用 set 加删，遇到 `<template>` 内含未闭合 `<script>` 的页面会永久跳过后续正文。`<body>` 清计数（L129-132）是对未闭合 head 的最后兜底。
3. **锚点链接被有意丢弃**：`]({href})` 只在 href 非 `#` 开头时输出（L189-192）——页内锚对知识库笔记无意义还污染正文，想保留需改这两行。
4. **超时是连接+读取的总预算**：`opener.open(request, timeout=timeout)`（L326）的 timeout 作用于阻塞 socket 操作，多次 read 各自计时，慢网络大页面总耗时可能数倍于 timeout。硬时限要在外层加。
5. **fallback title 可能是乱码路径段**：`_fallback_title` 取 URL 末段（L338-342），中文路径段会进文件名——`SKILL.md:30`"文件名去除非法字符"的约束就是给这条后路擦屁股的。
6. **`timeout_seconds` 传 true 会被当默认值**：L310 的 bool 排除意味着 `"timeout_seconds": true` 不会变成 1 秒而是回落 15 秒——防御性默认优于报错，知道这个行为免得排查"为什么不生效"。
7. **图谱视角**：本文件到 publish.py 的"一致性"只有注释级连接（L31），图谱里没有这条边——分析常量漂移风险时全仓 grep `MAX_RESPONSE_BYTES` 才可靠。
