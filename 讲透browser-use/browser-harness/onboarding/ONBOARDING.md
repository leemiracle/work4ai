# browser-harness 新人上手文档（ONBOARDING）

> 基于知识图谱（275 节点/480 边/13 层/15 步导览，commit 4ced8e0）+ 源码逐锚核实。

## 1. 项目一句话定位

browser-harness 是**面向 LLM agent 的极简浏览器 harness**：让编码 agent 通过 CDP 直接驱动**用户真实、已登录的 Chrome**。两个支点：**可整读**——核心 13 个 Python 文件约 6600 行，BU Bench V2.1 得分与 Playwright MCP 无显著差异但 2.1M token/$0.042 成本七工具最低（README.md:67/72）；**可自愈**——`agent-workspace/agent_helpers.py` 是仅含 docstring 的存根，agent 追加原语后被动态注入 helpers 命名空间（helpers.py:653-668），下次调用即可直接用。

**生态关系**：属 browser-use 组织，是主框架 browser-use 之外的"薄 harness"产品线。下游实证：jev-ultrafast 的 pyproject.toml:8 以 `browser-harness==0.1.13`（当前版本 pyproject.toml:10）为 pip 依赖。包名/CLI=`browser-harness`，skill 身份归属 browser-use（详见勘误 4）。

## 2. 总体架构（13 层）

13 层归并为四圈：**进程边界圈（L01-03）**paths.py 是文件系统布局唯一权威（BH_HOME→BROWSER_HARNESS_HOME→XDG_CONFIG_HOME→~/.config/browser-harness 四级解析 paths.py:9-13，目录统一 0700）；daemon.py 持有唯一 CDP WebSocket 连接（每 BU_NAME 一实例）；admin.py（1588 行，仓内最大）管生命周期/诊断/自更新。**操作面与入口圈（L04-06）**：helpers.py（fanIn 23 全仓最高）指令全经 `_send`（helpers.py:52）走 IPC；recorder/telemetry 观测线；bash 启动器+run.py 入口。**增值线圈（L07-08）**：video.py+video_render.py+video-template.html=录像→证据视频；src/mcp_server.py（src 顶层，pyproject `py-modules` 打包）暴露 MCP stdio。**知识配套圈（L09-13）**：SKILL.md 三形态、interaction-skills 18 篇、项目文档、打包与测试。

核心四文件（AGENTS.md）：admin 管生命周期、daemon 是长驻中间人、helpers 是 CDP 包装、run 是 CLI。

## 3. 核心链路

口诀"**两个进程、一根 socket**"：agent 进程永不直连 Chrome，指令全发给常驻 daemon。

**IPC 基石（_ipc.py）**：sock/pid/log 按 BU_NAME 派生（_ipc.py:41-43，共享目录用 `bu-<NAME>` 词干）——多 daemon 隔离的全部机制。POSIX 走 AF_UNIX，`serve()` bind 前 `os.umask(0o077)`（_ipc.py:171-174）socket 即 0600、无 TOCTOU 窗口；Windows 走 TCP 回环+端口文件带 token（_ipc.py:180）。

**daemon（daemon.py）**：模块级 `_load_env()` 在 import 时读 .env 派生常量（daemon.py:31-36，刻意导入期副作用）；attach 与 set_session 后把 Page/DOM/Runtime/Network 四域 `asyncio.gather` 并行 enable（daemon.py:541-563，否则 tab 切换后 network_idle 失聪）；🐴 tab-marker 纯装饰（daemon.py:613，BH_TAB_MARKER=0 关）。

**run CLI（run.py）**：读 stdin（run.py:220）预导入 helpers 后 exec，即 SKILL.md:21 的 heredoc 范式。**daemon 引导决策链（run.py:384-403）是全仓最重要的安全逻辑**：显式 CDP 端点保护>云端认证（需 BU_AUTOSPAWN）>本地探测>ensure_daemon——显式指定 BU_CDP_URL/BU_CDP_WS 时绝不云自启，否则静默向用户计费（run.py:95-100）。

**helpers 操作面**：goto_url/click_at_xy/new_tab/js 等原语全经 `_send` 发 IPC；`cdp()` 可发任意 CDP 方法，薄而不封闭。`goto_url`（helpers.py:152）带域技能钩子：BH_DOMAIN_SKILLS=1 时把 domain-skills/<host>/ 的 md 文件名附进返回值（helpers.py:154-157）。

## 4. 关键模块深读

**helpers↔recorder 刻意循环依赖**：helpers.py:648-650 注释明言在文件**末尾**才 import recorder，使 recorder 的 `from . import helpers` 看到完整模块——底部 import 是刻意受控环。

**agent_helpers 动态注入**：`_load_agent_helpers()`（helpers.py:653-665）用 importlib 读 agent-workspace/agent_helpers.py，非下划线属性灌进 `globals()` 立即执行；AGENTS.md 规定 agent 只许编辑 agent-workspace/。

**video.py 编译器**：SENSITIVE/ROUTE_UNSAFE 隐私正则（video.py:18/23）与 ACTION_KEYS/BRIEF_KEYS 严格 schema（video.py:56/70）；`write_source_manifest`（video.py:146-157）落源帧 sha256 清单，`verify_source_manifest`（video.py:160-173）导出前比对防篡改；`compile_brief`（video.py:473）把 recording-summary+edit-brief 编译为 composition.js（L619）。video_render.py 是运行时：本地 HTTP 服务（video_render.py:91）+真实浏览器+MediaRecorder→ffmpeg 转 MP4（video_render.py:417-418）；video.py 惰性导入 video_render，又一受控环。

**mcp_server.py 薄包装**：`_tool` 装饰器（mcp_server.py:116）统一三件事——先 ensure_daemon()、执行期 stdout 重定向到 stderr（mcp_server.py:99-100，MCP 中线即 stdout）、异常转 ToolError。L139-289 共 23 个工具，每个 3-8 行签名翻译。

## 5. 数据流与制品

**录制线**：被追踪动作成功后调 `recorder.observe()`（recorder.py:239），仅 ACTIONS 集合动作（recorder.py:31）落 JPEG（recorder.py:284）+events.jsonl 一行。**脱敏强制**：recorder.py:41-47 定义凭据参数正则（code/token/password/secret 等 10 类），`_scrub_url`（recorder.py:52）洗每条写盘 URL，密码框打码，失败一律吞掉；marker 文件（recorder.py:93）跨调用携带激活态。视频线 init/review/export 三步：帧+轨迹→composition.js→MP4，全链 sha256 复验。

**遥测线**：opt-out PostHog EU，三环境变量任一 falsy 关停（telemetry.py:20）。`_safe_properties`（telemetry.py:128）三重清洗：黑名单键丢弃（telemetry.py:22-41）、含 `://` 值整体 `[redacted]`+120 字符截断（telemetry.py:142-143）；`_send_detached`（telemetry.py:189）派生分离子进程，CLI 永不阻塞。

## 6. 设计决策与取舍

1. **daemon 导入期副作用**：daemon.py:31 模块级 `_load_env()` 即读 .env——牺牲 import 洁癖换 spawn 免传参。
2. **_ipc 导入期 mkdir**：_ipc.py:24-25 加载即建目录，import 即写盘（测试需隔离）。
3. **identify 防 bool-PID**：_ipc.py:148-157 用 `type(pid) is int` 而非 isinstance——`isinstance(True,int)` 为 True，`{"pid":True}` 会被当 PID 1；并拒 0/负 PID。
4. **umask 0o077 防 TOCTOU**：_ipc.py:171 注释明言"no TOCTOU window before chmod"。
5. **PID 启动时间指纹**：admin.py:17 取指纹、发布写 `{"pid","started"}`（admin.py:224）、动手前校验（admin.py:185-187）防 PID 复用误杀。
6. **PyPI Trusted Publishing 零 token**：release.yml 走 OIDC，仓库零 PyPI 长期 token。
7. **三份 SKILL.md md5 相同**：根/skills//src/ 三份 276 行全同，src 副本经 package-data 分发，test_skill.py 校验 frontmatter 防漂移——改文档必须三份同步。
8. **坐标点击优先**：SKILL.md:185-186 工作流 getFullAXTree→getBoxModel 盒中心→click_at_xy→js 验证；真实鼠标事件难过反自动化检测。
9. **单 daemon 共享**：默认一 daemon 多 agent 复用，tab 纪律（SKILL.md:28-42）是正确性问题。

## 7. 上手路径（按 tour 15 步）

**首日上午（01-03）**：README→AGENTS.md（四文件地图+红线）→`./browser-harness --doctor`+heredoc 冒烟 `print(page_info())`→精读 paths.py 与 _ipc.py。

**首日下午（04-09）**：daemon.py 通读（L541-563/L613）→admin.py 精读 ensure_daemon（L525 起）与 PID 指纹→helpers.py 全读+往 agent_helpers.py 写个新原语体验自愈→run.py 引导链（L384-403）。

**第二日起（10-15）**：视频线跟做 make-video.md→docs/MCP.md+mcp_server.py→根 SKILL.md 全文→interaction-skills 四篇必读 connection/tabs/screenshots/scrolling→跑 tests/unit，抽读 test_ipc.py 与 test_recorder.py。

## 8. 常见坑与勘误

**新手坑**：
- **interaction-skills 18 篇中 10 篇是占位**：cookies/cross-origin-iframes/downloads/drag-and-drop/dropdowns/iframes/network-requests/print-as-pdf/shadow-dom/uploads 各仅 1-2 非空行；实体为 connection/tabs/screenshots/scrolling/dialogs/viewport/make-video/profile-sync。
- **截图是设备像素**：2× 屏产 4592×2286 PNG，点击坐标是 CSS 像素须除以 devicePixelRatio；常规传 max_dim=1800 规避 LLM 拒收 >2000px（interaction-skills/screenshots.md）。
- **activate_tab 是用户可见操作**：switch_tab 只在 CDP 层切换，自动 activate_tab 抢前台被禁（SKILL.md:40-42）。
- **mcp_server 不在包内**：import 名是 `mcp_server`；改核心源码后要 `--reload`（daemon 长驻）。

**勘误（图谱/文档 vs 源码，以源码为准）**：
1. 遥测黑名单是 **18** 个词非图谱所称 16：telemetry.py:22-41 实数（api_key/cookie/email/href/key/password/secret/token/url 等 18 个）。
2. MCP 工具是 **23** 个非图谱"约 20"亦非 docs/MCP.md 的 17：mcp_server.py L139-289 共 23 个 @_tool 注册的 def browser_*。
3. **tests/unit/test_mcp_server.py:7 引用仓库不存在的模块**：`from mcp_types import CallToolRequestParams`——全仓无 mcp_types.py 且 git 历史从未提交，pytest 收集即 ImportError。
4. **skill 身份表述不一致**：AGENTS.md 称"Skill identity = browser-use (do not rename)"，但三份 SKILL.md frontmatter `name:` 实为 browser-harness（SKILL.md:2）。
5. **Windows token 表述**：`secrets.token_hex(32)`（_ipc.py:180）是 32 **字节**随机数的 64 字符 hex 表达，非"32 位字符串"。

---

*understand-anything onboarding 子代理 2026-11-01，行号锚经源码复核。*
