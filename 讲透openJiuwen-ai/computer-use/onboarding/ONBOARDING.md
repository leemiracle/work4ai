# computer-use 仓库 Onboarding（openJiuwen-ai）

> 仓库 `/usr-data/data2/repos/agent-repos/openJiuwen-ai/computer-use`（commit 8a21429e）；图谱 3238 节点/8174 边/16 层/16 步导览，fingerprints 1020。锚均经源码核实。

## 1. 项目定位：GUI 操作 Agent 引擎

openJiuwen computer-use 是华为开源的**桌面操作 Agent 引擎**——openJiuwen Agent 体系服务层的桌面操作组件（`README.md:17`）。它读无障碍树（AX/UIA/AT-SPI）与截图，让模型"像人一样"点击、输入、滚动，返回 `dispatched`/`verified` 回执而非裸事件注入。四层架构（`README.md:206`）：interfaces → agent assembly → 执行引擎 → OS adapters；两种接入：MCP 工具 `computer_use(title, code)`（持久命名空间跑 Python 驱动 `Computer → App/Window → Element`）或组装好的 DeepAgent（`computer_use_agent/agent.py:20`）。生态位对标 Anthropic computer-use SDK，差异在**安全工程**：三值安全模型、取消补发 reset、单次写入永不重试——"操作可能已发生"的不确定性是一等公民。图谱 1020 文件中 Python 约 2/3，Swift/C# 各占一翼。

## 2. 技术栈与代码形态：多语言三态 + 包名映射五重

**语言三态**：公共引擎与 Linux 驱动是 Python 3.12+（引擎依赖仅 regex/mcp/pillow）；macOS 驱动是 Swift 6 单 executable（`os_adapter/macos/Package.swift:5-9`，macOS 14+，SwiftPM）；Windows 驱动是 C#（`os_adapter/windows/Sources`+`Workers`，.NET 构建）。三平台驱动各自实现同一个 **Protocol 6** JSON-lines 协议，引擎只认协议不认平台。

**包名映射五重**（源码目录 ≠ import 名，`setup.py:21-26` `PACKAGE_ROOTS`）：

| import 包名 | 源码目录 |
|---|---|
| `computer_use` | `computer_use_engine/` |
| `computer_use_agent` | `computer_use_agent/` |
| `computer_use_mcp` | `interface_adapter/mcp/` |
| `computer_use_native_tools` | `scripts/` |
| `computer_use_linux`（独立 pip 包 computer-use-linux） | `os_adapter/linux/src/` |

Linux 驱动是**独立可安装包**（`os_adapter/linux/pyproject.toml:4`），依赖 python-xlib+Pillow，与主发行版分开。五个 CLI 入口在 `pyproject.toml:40-45`（mcp/build/permissions/linux-session/agent）。三平台驱动源码另被 `setup.py:52` 收进 `computer_use/_resources` 随 wheel 分发（sha256 manifest）。

## 3. 目录结构导览（图谱 16 层）

| 层 | 目录 | 职责 |
|---|---|---|
| L01 | 根 | 构建配置 + AGENTS.md 设计宪法 |
| L02 | `computer_use_engine/`（pipeline/protocol/session） | 组合框架根 `pipeline/core.py`、wire 契约 `protocol/records.py`（入度 101）、App 状态属主 `session/state.py` |
| L03 | `os_adapter/linux/src/` | Linux 驱动独立包：AT-SPI/X11 |
| L04-05 | `os_adapter/macos/Sources/` | Swift 驱动基座（Runtime/Contracts/Windowing）+ 读屏控制（Read/Control） |
| L06 | `os_adapter/windows/Sources/` | C# 驱动全栈（stdin 行协议分发器+UIA+WGC 截屏） |
| L07 | `engine/native/` | 驱动子进程桥接：`connection.py` 947 行、`contracts.py` 三值安全（入度 95）、`port.py` NativePort |
| L08 | `engine/interaction/` 根 | `pipeline.py` SessionPipeline 总路由、`agent/` AgentDispatch、`query/` FindElement |
| L09-10 | `interaction/read/` | 采集（acquisition 有界循环）、视图（views）、应用读取（app_read）、编号（numbering）、投递（delivery） |
| L11 | `interaction/read/presentation/` | 呈现压缩：RULES 11 条规则+IR+validate_projection |
| L12 | `interaction/write/` | 写入五段管线+routes/resolution |
| L13 | `engine/client/` | SDK 门面：Computer/App/Window/Element+factory/host |
| L14 | `computer_use_agent/` | DeepAgent 组装+CLI |
| L15 | `interface_adapter/mcp/` | MCP 父/子进程：server 两工具+ExecutionSession 监督 |
| L16 | `scripts/`+`os_adapter/assets/` | 构建 CLI+pointer.py 双语言指针资产生成器 |

## 4. 核心数据流：一次 read→压缩→喂 LLM→write 的旅程

1. **会话路由**：SDK 调用落进 `SessionPipeline`（`computer_use_engine/interaction/pipeline.py:22`）——单个 `Select`（:45）把 `agent:read/write/query` 三键接到共享子管线；适配器直接组合同一 write/lookup 实例，不重入路由器。
2. **read 半场**：`WindowObservationPipeline`（`interaction/read/pipeline.py:45`）三段 `Sequence`（:66-70）：Acquisition（有界采集）→ NumberedPresentation（编号呈现）→ AppDelivery（差分投递）。采集循环 `ReadRefreshLoop` 是 `Repeat max_iterations=2`（`acquisition/pipeline.py:338`），文件头钉死语义："A fixed-window read is a bounded acquisition loop, never an input retry"（`acquisition/pipeline.py:4`）——读重试有界，永不与输入重试混淆。
3. **呈现压缩**：`CompressionTraversal`（`presentation/compression/pipeline.py:189`）单次先序+后序遍历整树，`RULES` 注册表（:115）11 条规则各声明 reads/writes 契约；`export_projection` 前跑 `validate_projection`（`presentation/ir.py:632`）——**每个 caption 必须逐字等于源字段值**（`ir.py:645`），不认识/重复引用、无出处的省略一律 raise。这是喂给 LLM 前的防幻觉硬闸。
4. **LLM 决策**：模型拿压缩投影+截图，表达"点这个按钮/输入这段文字"。
5. **write 半场**：`WritePipeline`（`interaction/write/pipeline.py:44`）五段（:65-117）：Intent 解析→TargetBinding（resolve+pin，:100）→`Scope NativeOperationScope` 租约（:110）→`Repeat WriteReplanLoop`（:93，共享原调用期限/RouteKey/Attempts 上限，:98）→格式化回执。`status="verified"` 仅当 `Confirmation.CONFIRMED`，否则诚实报 `dispatched`（`write/progress.py:272`）。
6. **平台分派**：引擎经 `native/connection.py` 向驱动子进程发 Protocol 6 帧（begin/inspect/execute/finish/capture 五方法，`native/connection.py:301`）；三平台驱动各自落到 AT-SPI/AX/UIA。

## 5. 关键模块深潜

- **`pipeline/core.py`（626 行，入度 206）**：全仓继承根。三层词汇：元数据层 `Effect` 五值 PURE/QUERY/PREPARE/DISPATCH/RESOURCE（:45）+`Contract`（:56，声明 effects/requires/writes/failures）+`Event`/`Control`（:80/:107）；抽象层 `Step` Protocol（:188）+`Pipeline` ABC（:206，子类 build() 组合后交根步骤）+`Node`（:270，发 enter/exit/error 事件）；控制流原语 `Sequence`/`Select`/`Repeat`/`Scope`（:407/:443/:495/:582）+`Pass`（:332）。零仓内依赖。
- **`native/connection.py`（947 行）**：驱动全生命周期。`_negotiate`（:286）发 id=0 hello 协商 capabilities，超时整体关连接"no system command was sent"；`request()` 单飞行互斥（:268）；约 20 项 capability 门禁（:425 起，nativeScroll/nativeTextInput 等缺失即拒绝并给恢复指引）；close 跨代退休（:921）。
- **呈现压缩**：省略/折叠有溯源账本（elisions 记录去向，`ir.py:657`），改绑展示父节点被禁止——压缩不许破坏操作引用。
- **三 OS 驱动**：Linux `runtime/server.py:20` 单执行线程"reader only queues frames and cancels"，4MB 帧上限+BOM 拒绝（:54/:59）；`runtime/native.py:167` NativeExecution 组合根拼 15 个 native 单元并按桌面能力动态扩 capabilities；macOS `Runtime/Driver.swift:7` @MainActor Driver+RequestLedger（:13），hello 只许一次（:119），busy 拒绝（:213）；Windows `Runtime/Driver.cs:13` 分发器，64MB 帧上限（:325），请求去重三态 in_progress/request_expired（:217/:223，均标 effect "possible"）。

## 6. 设计决策与权衡

- **三值安全模型 Knowledge**（`native/contracts.py:23`）：YES/NO/UNKNOWN——"读不到≠不存在"，UNKNOWN 绝不冒充 NO 去授权动作。配套 Dispatch 四态（notDispatched/dispatched/partial/unknown，:36）、Confirmation 四态（:43）、Cleanup 三态（:50）：**系统声明的能力、动作已发送、效果已确认是三个正交事实**。
- **单次写入永不重试宪法**：`write/progress.py:203` "The native continuation is a constraint, never an independent retry authorization"——只有 Gate 消费有限历史/预算；已派发/可能已派发一律停，恢复指引"read the current target before continuing; do not replay uncertain input"（:56）。effect 严重度三值 none/possible/partial 单调取大（:46-47）。
- **取消安全三层**（`computer_use_agent/connection.py`）：CancelError 置 `_needs_reset`（:103，取消无清理确认）；下次非 reset 调用先补发 reset（:87-90）；reset 成功才清旗（:97-98）。MCP 侧同构：45s 看门狗 stalled 即 reset（`interface_adapter/mcp/session.py:113`），cleanup 未完三段屏障拒绝新代码（:56-61）。
- **包名错位**：目录按职责、import 按稳定名（`setup.py:18` 注释钉版），防止把 Linux 驱动扫进公共命名空间。
- **TYPE_CHECKING 类型层**：`core.py:278` 抽象钩子只在 TYPE_CHECKING 下 abstract，运行时零 abc 开销；`_sync`（:251）把误返回的协程 close 后抛 TypeError（:261）。
- **Swift 无 import 的类型引用**：单 target 跨文件类型直接可见，图谱的 Swift"边"靠同名解析，读代码别找 import 语句。

## 7. 常见任务上手

- **理解 EFFECT 契约**：任何 Pass/驱动单元都声明 `Contract(effects=...)`；改副作用先改声明。效果光谱=Effect 五值（`core.py:45`）+macOS `Failure.swift:40` FailureEffect 三值并集 including（:43-47）。
- **加一个 Pass**：在所属 `passes/` 建单文件（`Pass.define(name=..., function=..., contract=...)`，模板 `write/passes/recognize_existing_completion.py:24`），再到父 `pipeline.py` 显式组合——不引入动态注册（AGENTS.md:45 禁）。
- **跑测试**：`pytest`（testpaths=tests）；开源仓测试薄（`tests/unit_tests/` 仅数个文件），行为回归主要靠 `tests/manual` 与真实任务验收（AGENTS.md:70）。
- **三平台构建**：`uv run computer-use-build`（`scripts/native.py:406`）按 `sys.platform` 分派（:139）：macOS swift 构建（:34）、Linux 装驱动资源（:77）、Windows 构建驱动（:150）。macOS 权限：`uv run computer-use-permissions --request`（README.md:74）。
- **改指针资产**：编辑 `os_adapter/assets/agent-pointer/{cursor.svg,motion.json}` 后跑 `scripts/pointer.py` 重生成 Swift/C# 双语言资产——生成物带 sha256，禁止手改。

## 8. 新人提示与坑

- **AGENTS.md 四死链**：`AGENTS.md:37` 引用的 `docs/design/{pipelines,read,control,native-ownership}.md` 不存在（仓内无 `docs/`）；:39 却声称"docs/ 与 tests/ 只维护这些核心组件"——设计宪法正文可用，链接勿点。
- **包名映射是第一坑**：`import computer_use` 找不到 `computer_use/` 目录是对的（见 §2 五重表）；`computer_use_linux` 得单独装。
- **Effects/状态常量别数错**：Effect 是 5 值、Knowledge 3 值、Dispatch 4 值、Confirmation 4 值、Cleanup 3 值、FailureEffect 3 值、INTENTS 11 种（`contracts.py:56`）——写代码前先查枚举本体。
- **生成文件 DO NOT EDIT**：`os_adapter/macos/Sources/Preview/AgentPointerAssets.swift:3` 与 Windows 对应物是 pointer.py 生成物，手改会被下次构建覆盖。
- **窗口身份四因子**：macOS 后台目标验证用 pid/startedSeconds/startedMicroseconds/executable 四因子（`BackgroundTarget.swift:162-163`）+AppKit 注册史（:115-116）双通道；身份漂移即 staleTarget，别按名字重绑（宪法 AGENTS.md:51）。
- **menu 匹配是精确唯一**：`match_menu_title.py:34` `name == title` 且必须恰好 1 个，失败时报真实候选清单——不做模糊匹配、不猜。
- **Linux 键盘文本永远只报 dispatched**：`native_typed_text.py:368` "Keyboard text recipe sent; read to verify its effect"——诚实回执文化，verified 需要字面证据。
