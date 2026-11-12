# 03 · 会话总路由与 agent 适配——SessionPipeline/AgentDispatch/SessionController

## 一、角色定位

这组文件回答：**一个请求进来，由谁执行、以什么身份执行、执行前如何证明"你还有资格"**。

- `computer_use_engine/interaction/pipeline.py`（57 行）的 `SessionPipeline` 是会话内**唯一路由器**：所有 `InteractionRequest` 按双轴 key 分支——"谁发的"（公共句柄 vs 会话内部）×"什么效应"（read/write/query）。
- `computer_use_engine/interaction/agent/pipeline.py`（580 行）是**agent 适配层**：`AgentDispatch` 把 9 种 `InterfaceRequest`（`agent/requests.py:160-170` 的 TypeAlias：ObserveUI/ObserveDesktop/ObserveElement/ObserveText/DiscoverApps/ResolveElement/ActOnElement/UIKeyboard/UIPointer）分派给 `AgentInterfacePipeline`；后者持有公共引用注册表，把"句柄"翻译成"受约会话执行"。
- `computer_use_engine/interaction/controller.py`（276 行）的 `SessionController` 是**组装与委托中枢**：创建 Connection/Port/读者/写引擎，暴露 `pipeline.interfaces`（controller.py:75-76）。

最关键的一句在 `pipeline.py:27-29`：**"The adapter composes the same write and lookup instances directly, without re-entering this router"**——适配器直接复用共享 write/lookup 子流，绝不递归重入路由器。

## 二、内部结构

**路由层**：`select_route`（`interaction/passes/select_route.py:39-48`）纯函数，按 `_ROUTES`（L30-36）isinstance 顺序返回 5 个 key（L26-27）：`agent:read/agent:write/agent:query` + 内部 `write/query`。双轴编码让 trace 永远带效应类别。`SessionPipeline.build`（pipeline.py:43-53）一个 `Select` 完成全部路由：三 agent 键同指 `AgentDispatch`（L49），再加共享的 write/lookup 分支（L50-51）。

**适配层**（agent/pipeline.py）：`AgentInterfacePipeline`（L57）构造（L74-86）持 controller、共享 write/lookup、`references/text_cursors` 注册表、discovery 与 read_pipeline。翻译方法群：`application`（L88-112，发布号→AppState）、`window`（L117-163，成员目录查证+视图缓存）、`read`（L165-176）、`read_desktop`（L178-237）、`validate_snapshot`（L239-309）、`element`（L311-406）、`keyboard_context`（L408-461）、`act_element`（L469-501）等。`AgentDispatch`（L536-574）：构造时 `self.children = (interfaces.write, interfaces.lookup)`（L548）把共享子流挂进诊断树；`_arun`（L551-571）九连 isinstance 分发；`_run` 直接 `TypeError("Agent interface requests require arun()")`（L573-574）——agent 面只有异步通道。

**中枢层**（controller.py）：构造（L50-76）transport 优先取注入 port，否则自建 `Connection(self.invalidate, protocol_version=...)`（L65-69）——第一参数是失效回调；`HostPolicy(desktop_mode(), os.environ.get("COMPUTER_USE_FOREGROUND_ASSIST") == "1")`（L70-72）。`run`（L78-99）五个 `@overload` narrowing 返回型，实现一行 `await self.pipeline.arun(request)`。服务面：`invalidate`（L110-115，native 换代时 reset 桌面存储+bindings+广播事件，但**句柄保留旧 session 身份**以便校验识别过期）、`_remember/_snapshots`（L120-168，`ordinary()` L140-153 判定容器性）、`act/act_element/_execute`（L170-243）。

## 三、外部连接

- 上游：`client/` 门面经 `controller.run` 进入（03→12 篇衔接）；下游：read/views、read/acquisition、write/ui、query/instances 各域。
- 注册表闭环：`ApplicationReferences.publish` 在 `read_desktop`（L208-210）与 discovery 双路写号，`references.resolve` 在 `application()`（L100）读号。
- 依赖纪律：agent/pipeline.py 对 `native/scopes`、`session/state` 的 import 全部**延迟到函数体**（L97-98、L127-128）——运行时 import 切断 interaction 构造环。

## 四、数据流

以「点击先前读到的元素」为例：SDK 造 `ActOnElement` → `controller.run` → `select_route` 返回 `agent:write` → `AgentDispatch._arun`（L565-566）→ `act_element`。**两段资格校验**（L484-488）：先 `validate_snapshot(allow_unknown=True)`（尚未到不可逆点，UNKNOWN 可过）→ 有 anchor 则 `refresh` 刷目录 → 再 `validate_snapshot`（严格模式，UNKNOWN 即 `observation_incomplete` 拒绝，L297-304）。"UNKNOWN 绝不授权"在此落成两段闸门。通过后 `self.write.arun(ExecuteAction(...))`（L499-501）——直接调共享实例绕过路由器，错误码沿途不改写。输入侧 `keyboard`（L463-467）：refresh → `keyboard_context` 选接收窗 → 意图名归一（`type_text→insert`、`press_key→key`）→ write。

## 五、设计决策与权衡

1. **单 Select 路由**：决策集中在纯函数（`Pass.define` 声明 `Contract(object, str)`，select_route.py:51-55）；新增请求只改 `_ROUTES` 与 requests 分组元组（agent/requests.py:152-155）。
2. **两段 validate 的 allow_unknown 语义**：参数 docstring 写死（L245-247）"never native observation or input authorization"——UNKNOWN 只在"未到不可逆点"时被容忍。这是三值知识模型（native/contracts.py 的 `Knowledge`）在路由层的执法点。
3. **错误码即合同**：`element()`（L386-403）对多命中/范围未观测/零命中分别给 `ambiguous_target/observation_incomplete/element_not_found`，每个 `local_failure` 带"事实+恢复指引"——错误本身成为 prompt 的一部分。
4. **代际失效回调注入 Connection**：`Connection(self.invalidate, ...)`（controller.py:68）把"native 换代"与"句柄集体过期"焊死；`invalidate` 刻意不清 bindings 的 session 身份（L114-115 注释）——让校验报"过期"而非"查无此人"。

## 六、新人提示与坑

- **勘误（图谱 tour 措辞）**：S04 摘要说"AgentDispatch……每步先做 validate_session/in_scope 校验"——`AgentDispatch._arun`（L551-571）只做 isinstance 分发，**校验分散在各 adapter 方法内**（window L130、element L354、keyboard 走 refresh L464）。
- **`_snapshot_needs_refresh` 优先级坑**（L533）：`a and b or c` 等价 `(a and b) or c`——逻辑没错但极易误读，改前先加括号。
- **`read_desktop` 捕 `BaseException`**（L193-198）：连 KeyboardInterrupt 也会 reset 桌面存储并发事件后 re-raise——不是 bug。
- **`element()` 的 int 直查不刷新目录**（L331-342）：整型引用走 `ui._instance.refs` 快路径；名字/路径查找才聚合多 owner 逐个 lookup，超时预算按 owner 顺序扣减（L374）。
- **大量 `app._instance` 私有访问**（L133 等，遍布 pylint disable）：适配器与句柄是同仓 conspirator，被接受的模式，但别在 client 层模仿。
- **包名映射**：import 全写 `computer_use.*`，磁盘是 `computer_use_engine/`（setup.py PACKAGE_ROOTS 别名）。
- 风格小瑕疵：`agent/pipeline.py:577-580` 与 `controller.py:261-276` 各有**两个连续 `if TYPE_CHECKING:` 块**——合法但冗余，别在这两段找运行时逻辑。
