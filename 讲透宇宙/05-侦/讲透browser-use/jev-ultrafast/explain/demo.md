# demo.py — 仅回环的本地演示服务器：命令分发、令牌校验、静态白名单

## 一、角色定位

demo.py 是 agent 循环的 HTTP 外壳与可视化入口，docstring（demo.py:1）一句话划定边界："Loopback-only inspector"——只绑 127.0.0.1 的检查器，不是产品服务。它把 Agent.command 的三段协议（tick/predict/act）原样暴露为 `/api/*` POST（demo.py:118），配合每进程随机令牌与 Host/Origin 校验构成"本地演示专用"的安全模型。经 pyproject 的 `[project.scripts] jev = "jev_ultrafast.demo:main"` 注册为 `uv run jev` 命令，是 README"Try it"一节的直接载体。它同时身兼二职：为 agent 的 fixture 场景提供页面源（scenario=travel/research 时 agent 导航到本服务器自己 serve 的 fixture.html，demo.py:57）。

## 二、内部结构

**模块级常量（demo.py:15-20）**：ROOT 指向包目录（静态资源根）；PORT 取环境 `TYPESAFE_DEMO_PORT` 默认 8766；ORIGIN 即 `http://127.0.0.1:{PORT}`；TOKEN 是 import 时生成的 `secrets.token_urlsafe(32)`（demo.py:18，每进程随机）；LOCK 是全局线程锁；AGENT 是全局单例句柄。

**load_environment（demo.py:23-29）**：极简 .env 解析器——逐行读工作目录 .env，跳过注释，按首个 `=` 切分后 `os.environ.setdefault` 注入。用 setdefault 而非赋值：**已存在的环境变量永远优先**，不会覆盖用户的显式配置。

**response_state（demo.py:32-34）**：无活跃 Agent 时返回 idle 骨架（page=None/status="idle"），有则返回 `AGENT.snapshot()`，两种情况都附加 text_model 环境值与 max_steps——前端据此展示模型名与预算。

**close_browser（demo.py:37-41）**：关闭全局 AGENT 并置 None；被 reset 流程（demo.py:53）与 atexit（demo.py:133）共同调用，保证进程退出释放浏览器。

**command（demo.py:44-67）**——命令分发器。reset 分支做三道校验：scenario 必须在 {travel, research, flights}（demo.py:47-49）；goal 非空且 ≤2000 字符（demo.py:50-52）；先 close 旧 Agent 再建新的（demo.py:53）。场景映射：flights 走真实 Google Flights URL，其余两个走本地 fixture（demo.py:54-61）；`record` 选项开启时 record_dir 指向 artifacts/frames 落帧。随后把 scenario 直接塞进 state（demo.py:62）——裸 dict 的灵活性在此被利用。非 reset 命令要求 AGENT 已存在，否则报"Start a demo first"（demo.py:64-66），其余原样透传给 Agent.command。

**Handler（demo.py:70-128）**——继承 BaseHTTPRequestHandler：

- send（demo.py:71-79）：统一响应，附 Cache-Control: no-store 与 X-Content-Type-Options: nosniff（demo.py:76-77）。
- do_GET（demo.py:81-102）：① **Host 头必须精确等于 `127.0.0.1:{PORT}`**（demo.py:82）——防 DNS rebinding 的第一道闸；② `/api/state` 在 LOCK 内返回状态（demo.py:85-87，阻塞式等当前步跑完）；③ `/demo.mp4` 直接回放 docs 下的演示视频（demo.py:88-91）；④ 其余路径只认 4 项白名单：`/`、`/app.js`、`/style.css`、`/fixture.html`（demo.py:92-97），命中后从 static 目录读文件并做 `__TOKEN__` 模板替换（demo.py:101）——**令牌是随 HTML 下发的**，前端从 `<meta name="demo-token">`（static/index.html:6）读取；不在白名单一律 404。
- do_POST（demo.py:104-125）：五道闸依次为 Host + X-Demo-Token + Origin 三重校验（demo.py:105-110，Origin 允许 None 以兼容非浏览器客户端）；**非阻塞抢锁**，抢不到立即 409 "A browser step is already running"（demo.py:111-112）——串行化 inspector 动作；请求体长度必须落在 (0, 8192)（demo.py:114-116）；命令名取自路径 `removeprefix("/api/")`（demo.py:118）；错误分级——ValueError/RuntimeError/TimeoutError 映射 400 携带原消息，其余异常统一 500 且文案固定为"no automatic retry. Reset to recover."（demo.py:120-123）。finally 释放锁（demo.py:124-125）。
- log_message 置空（demo.py:127-128）：不往 stdout 刷访问日志。

**main（demo.py:131-141）**：load_environment → atexit 注册清理 → ThreadingHTTPServer 绑定 127.0.0.1 → 打印 ORIGIN → serve_forever，KeyboardInterrupt 后 server_close。

## 三、外部连接

import 面干净：atexit/json/os/secrets/threading 标准库 + http.server + pathlib + urllib.parse，项目内仅依赖 `.agent.Agent`（demo.py:12）与 `.questions.MAX_STEPS`（demo.py:13）。前端搭档是 static/ 三件套：app.js 从 meta 读 token 后以 `X-Demo-Token` 头 POST `/api/{reset,predict,act,tick}`（static/app.js:2、22-24），并以轮询 `/api/state`（static/app.js:56）驱动渲染；fixture.html 既是静态资源也是 agent 的演练靶页。浏览器侧由 Browser 类经 browser-harness 独立连接，与 HTTP 服务无共享状态——除了 fixture 场景下 Chrome 会回头请求本服务器。

## 四、数据流

进：HTTP 请求——GET 无需令牌（状态只读），POST 携带 JSON body（goal/scenario/record 或 fingerprint）。出：JSON 化的 agent 快照（response_state，含 elements 元素表、history 轨迹、decisions、text_calls）。进程生命周期上：.env → 环境变量 → Agent 的 model.py 调用凭据；reset 请求 → 新 Browser 标签页 + 首帧观察；atexit → 浏览器清理。数据流的关键特征是**单 Agent 单锁**：所有 mutating 命令串行执行，/api/state 用阻塞锁避免读到中间态。

## 五、设计决策与取舍

1. **回环 + 三重校验而非通用鉴权**：Host 校验挡 rebinding、Origin 校验挡跨站表单、随机令牌挡未授权脚本——三层叠加后的信任模型是"只有本机拿到 HTML 的页面能驱动 agent"，够 demo 用且零依赖。2. **令牌随 HTML 模板注入**而非独立 /api/token 端点：少一次往返，代价是任何能读首页的本地进程都能拿到令牌——与回环边界一致。3. **非阻塞锁 + 409**：宁可拒绝并发也不排队，前端体验上"上一步没跑完就点下一步"得到明确反馈而非超时。4. **错误两级映射**：可预期的业务错误（ValueError 家族）透传原文，未知异常一律吞掉细节只给恢复指引——既便于调试又不泄露栈信息。5. **fixture 自托管**（demo.py:57）：演练场景不依赖外网，且 agent 观察的页面与用户看的控制台同源同进程，实验完全可复现。6. **stdlib http.server 而非框架**：145 行写完整个服务，无 FastAPI/Flask 依赖，与全仓"small enough to read"的美学一致。

## 六、新人提示

- 令牌是**每进程**随机（demo.py:18）——重启服务后旧页面里的 token 失效，必须刷新页面重新取。
- POST 的 Origin 检查允许 None（demo.py:108）：curl/无 Origin 头客户端可直调 API，这是刻意的本地调试便利，不是校验漏洞。
- /api/state 的 GET 不查令牌（demo.py:85-87）——状态被视为非敏感只读数据；若担心本机其他进程窥屏，需自行加校验。
- 命令分发是**白名单外的开放映射**：`/api/任意名` 都会进 Agent.command，未知名在 agent.py:160 抛"Unknown command"转 400——不是 404，排查时别找错层。
- reset 一个新 demo 会**静默关闭**上一个浏览器标签页（demo.py:53），录制中的 run 会被打断。
- 图谱 hub 称本文件"仅绑定 127.0.0.1……配合随机 token 与 Host/Origin 三重校验"——与源码逐条核对一致；tour 第 6 步"`/api/*` POST 直通 agent.command"的描述亦准确，无出入。
