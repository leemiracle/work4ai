# mlx_use/telemetry/service.py 精讲——遥测单例与硬编码上游 PostHog key 的安全发现

## 一、角色定位

`mlx_use/telemetry/service.py`（103 行，配套事件定义 `telemetry/views.py` 61 行）是全仓的**产品遥测出口**：`ProductTelemetry` 单例类把 agent 运行事件打包发给 PostHog 分析平台。它的代码量在全仓几乎垫底，却是安全审计意义上最重要的文件——**L32 硬编码着上游 browser-use 项目的 PostHog project API key，L33 指向其欧盟实例**，fork 时未做任何替换。这意味着 macOS-use 用户的一切遥测并未发给本仓维护者，而是原封不动流进了 browser-use 团队的分析账户。本文除了讲机制，还要把这个发现的完整链条钉清楚。

图谱 fanIn 3 / fanOut 7：`agent/service.py`、`controller/registry/service.py` 构造并调用它，`telemetry/views.py` 提供事件类型；下游连到 posthog SDK、dotenv、uuid 与 `mlx_use/utils.py` 的 singleton 装饰器（L46）。

## 二、内部结构

**类常量区（L31-34）是全文件的雷区**：`USER_ID_PATH`（L31）指向 `~/.cache/browser_use/telemetry_user_id`——注意目录名是 `browser_use` 不是 `macos_use`，fork 连缓存目录都没改名，与上游用户共享同一身份文件；`PROJECT_API_KEY`（L32）即硬编码的上游 PostHog key（`phc_F8J...caUh`），PostHog 的 project API key 本是设计为客户端可见的公开标识，但**谁拥有这个 key，数据就归谁**——此处归上游团队；`HOST`（L33）是 `https://eu.i.posthog.com` 欧盟实例；`UNKNOWN_USER_ID`（L34）是文件读取失败时的兜底身份。

**__init__（L38-58）**：L39 读 `ANONYMIZED_TELEMETRY` 环境变量，**默认值 'true'——即默认开启、opt-out 模式**；L40 读 `BROWSER_USE_LOGGING_LEVEL`（又一个上游变量名残留）决定 debug 日志。遥测开启时 L46-50 构造 Posthog 客户端（`disable_geoip=False`，即允许 IP 地理定位），L45 打出提示——文案里的"更多信息"链接指向 `github.com/browser-use/browser-use`，即上游仓库而非本仓；L53-55 在非 debug 时直接禁用 posthog 自己的 logger，让数据外发静默无声。

**capture（L60-66）**：唯一对外入口。客户端为 None 直接返回；debug 模式先在本地日志打出事件名与属性；否则进 `_direct_capture`（L68-82）——注释 L70 写着 "Should not be thread blocking because posthog magically handles it"，SDK 内部有队列异步发送，这里的 try/except（L75-82）保证网络失败只留 error 日志不炸主流程。

**user_id property（L84-103）**：懒加载的持久匿名身份。首次调用时建目录、生成 uuid4 写入 `USER_ID_PATH`（L92-97），之后每次读文件（L99-100）；任何文件系统异常都吞掉并落为 `UNKNOWN_USER_ID`（L101-102）。配合 L18-20 的 `POSTHOG_EVENT_SETTINGS = {'process_person_profile': True}`，这个 uuid 在 PostHog 侧被识别为"人"——跨项目、跨运行可追踪。

**views.py 事件族**：`BaseTelemetryEvent`（L8-17）是 ABC＋dataclass 混血——`name` 抽象属性 + `properties` 把 dataclass 字段（除 name）转 dict；五个具体事件：`ControllerRegisteredFunctionsTelemetryEvent`（L26-29，注册函数清单）、`AgentStepTelemetryEvent`（L32-39，含 **`actions: list[dict]` 全量动作参数**）、`AgentRunTelemetryEvent`（L42-51，含 **`task: str` 任务原文**、model_name、chat_model_library、version、source）、`AgentEndTelemetryEvent`（L54-61，成败与错误列表）、载体 `RegisteredFunction`（L20-23）。

## 三、外部连接

- **agent/service.py**：L40-44 导入三个事件类；L109 构造 `ProductTelemetry()`；L247-248 每步发 `AgentStepTelemetryEvent`；L389-399 run 启动时发 `AgentRunTelemetryEvent`——**L393 `task=self.task`，用户任务的完整原文就在这里出仓**；L434-441 run 结束发 `AgentEndTelemetryEvent`（含 `errors=self.history.errors()` 错误文本）。
- **controller/registry/service.py L129-136**：`create_action_model()` 时上报全部注册动作的名字与完整 JSON schema（含自定义动作的业务参数名）。
- **mlx_use/utils.py L46 `singleton`**：闭包 `instance[0]` 单例装饰器，保证全进程一个客户端、一份 user_id。
- **.env.example L8/L11**：`ANONYMIZED_TELEMETRY=false` 与 `BROWSER_USE_LOGGING_LEVEL=info` 模板——注意示例文件默认关、代码默认开（L39），装了包但没抄 env 的用户是开启状态。
- **第二条遥测线（对照）**：gradio_app 的 `src/services/google_form.py` L8 硬编码 Google Form 端点，把用户 prompt 与终端输出发到维护者自己的 Sheet——同一仓里"官方收集"其实有两条互不相干的管道。

## 四、数据流

一次 `agent.run()` 的遥测时间线：

1. Agent 初始化：`ProductTelemetry()` 单例构造，读 env 决定开关；若某处首次调 `create_action_model`，注册函数清单事件先出仓；
2. run 开始（agent/service.py L389）：`AgentRunTelemetryEvent` 带着agent_id（uuid）、**task 原文**、模型名、模型库、版本、来源（Agent 构造参数 `source`，区分 py包/cli/自定义）发出；
3. 每步（L247）：`AgentStepTelemetryEvent` 带 step 序号、**该步全部动作及其参数**、连续失败数、错误列表；
4. 结束（L434）：`AgentEndTelemetryEvent` 带总步数、是否达上限、成功与否、全部错误文本。

接收端视角：PostHog 欧盟实例上，key 持有者（browser-use 团队）可以按 user_id 聚合看到——某个 uuid 的用户用什么模型、执行什么任务（原文）、每步点了什么、错了什么。所谓 "anonymized" 仅指身份是随机 uuid 而非邮箱；**内容一点都不匿名**，且 `process_person_profile=True` + geoip 开着，IP 与国别也在。

## 五、设计决策与取舍

- **opt-out 而非 opt-in**：默认开启是上游开源项目的常见取舍（牺牲隐私换采用率数据），fork 继承了它却没继承"数据归自己"的前提——决策没随所有权转移而重审，是这类遗留问题的根因。
- **吞异常保主流程**：capture 全链 try/except，遥测永不拖垮 agent——正确的工程选择，但也让"数据在悄悄外发"更难被察觉。
- **uuid 身份 + 本地文件持久化**：不采集机器码等强标识，比多数商业 SDK 克制；但 `~/.cache/browser_use` 与上游共享，同一台机器上装过两个项目的人会被合并成同一个"人"。
- **dataclass 而非 Pydantic 建模事件**：遥测数据不需要校验回读，轻量 dataclass + `asdict` 足够——与仓里其他 views.py 的 Pydantic 风格形成有意的对照。

## 六、新人提示（坑与勘误）

1. **头号安全发现：L32 硬编码上游 PostHog key + L33 上游欧盟 host**。fork 项目不改 key，等于把本仓用户的任务原文（agent/service.py L393）、动作序列（views.py L38）、错误文本、IP（L49 geoip 开启）全部送进上游团队的账户。处置：设 `ANONYMIZED_TELEMETRY=false`（.env.example L8 有模板），或改 key/host/删文件。
2. **"匿名"名不副实**：`AgentRunTelemetryEvent.task`（views.py L46）是任务全文。任何含密码、内部域名、客户名的自然语言任务都会出仓。
3. **默认开启且静默**：代码默认 'true'（L39），posthog logger 被禁（L53-55），不抓包几乎无感。审计 fork 项目的第一课：grep `posthog|telemetry`。
4. **三处 browser_use 命名残留**：L31 缓存路径、L40 环境变量名 `BROWSER_USE_LOGGING_LEVEL`、L45 提示文案链接——都指向 fork 前身，改目录名会导致老用户身份"重置"，属可接受的兼容行为，但要知情。
5. **单例的隐形坑**：`@singleton`（utils.py L46）把类名变成工厂函数，`ProductTelemetry` 不能再被继承或用 `isinstance(x, ProductTelemetry)` 检查（名字已不是类）。
6. **L102 写的是类常量名**：异常分支 `self._curr_user_id = 'UNKNOWN_USER_ID'` 赋的是字符串字面量而非 L34 的 `self.UNKNOWN_USER_ID`——恰好等价（同值字符串），但两处 'UNKNOWN' 定义各写一份，改一处会漂移。
7. **模块导入即 `load_dotenv()`**（L12）：import 该模块就读 .env 并触发环境固化，测试里想通过 env var 控制行为必须在 import 前设好。
