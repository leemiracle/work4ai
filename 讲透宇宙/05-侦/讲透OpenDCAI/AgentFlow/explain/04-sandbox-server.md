# 04 · sandbox 服务端：HTTPServiceServer、Backend 抽象与 VM 双 provider

## 角色定位

`sandbox/server/` 是工具执行的**服务端容器**：把 01 篇的协议、02 篇的工具、05 篇的 OSWorld 虚机能力组装成一个可独立部署的 HTTP 服务。它的架构立场是「容器不干活」——server 只持有与调度，资源生命周期（warmup/initialize/cleanup/shutdown）全部下放给 Backend 实现；无状态工具则连 Backend 都不要，装饰器注册即可。三种后端（VM/RAG/MCP）+ 一组无状态 API 工具在同一进程里以 resource_type 为键共存，靠会话路由表隔离状态。

## 内部结构

**HTTPServiceServer**（app.py L60，638 行）。核心是三层数据结构（L115-125）：`_tools`（全名→函数，L117）、`_tool_name_index`（简名→全名列表，L121）、`_tool_resource_types`（全名→资源类型，L125）。`register_tool`（L159）写入三层：带冒号的名字自动拆出 resource_type 与 simple_name（L177-186）；`rag:search` 与裸 `search` 在 index 里共享一个简名桶——这是简名歧义处理的数据基础。`load_backend`（L329）反射扫描 `@tool` 标记并注册（L350），`scan_and_register`（L298）遍历对象属性找 TOOL_MARKER。`__init__` 里 ToolExecutor 的接线用了 lambda 延迟绑定（L136-142）：executor 拿到的 warmup_callback 是闭包而非方法引用，避免构造期循环依赖。FastAPI 应用在 `create_app`（L532）惰性构建，lifespan（L536）里起清理任务。

**Backend ABC**（backends/base.py L107，307 行）。四个生命周期钩子全部可覆写：`warmup`（L177，进程级，加载模型/连接池）、`initialize`（L199，会话级，返回值存入 session_info["data"]）、`cleanup`（L237，会话销毁）、`shutdown`（L261，进程级释放）。L120-151 的 ASCII 生命周期图是全文件精华——server 调用时序、session_info 流向一图讲清。`bind_server`（L286）建立双向引用，供 backend 需要回查 server 时用（MCP backend 的 bind_server 覆写就在此挂 438 桥接工具）。`BackendConfig`（L87）只有 enabled/default_config/description/metadata 四字段，克制。

**ResourceRouter**（core/resource_router.py L19，406 行）——会话路由表。`_generate_session_name`（L135）生成可读名：worker_id 经正则清洗（L143，非 [A-Za-z0-9_-] 转 `-`）、截 32 字符（L146-147），计数器三位编号（L149-154），格式 `{resource_type}_{worker}_{001}`。`get_or_create_session`（L160）是热路径：已存在则顺手续 TTL（L197-204）；新建时调 initializer（L228-237），**无 initializer 的资源类型不报错而是标记 compatibility_mode**（L244-250）——优雅降级让「先调工具后注册」也能工作。`cleanup_expired`（L360）供周期任务收割过期会话。

**ToolExecutor**（core/tool_executor.py L49，486 行）。两步解析：`_normalize_tool_name`（L86-111）把 `resource.action/resource_action/resource-action` 三种分隔符变体归一为冒号形态——但仅当前缀是已注册资源且组合名命中注册表（L108），防误伤普通工具名；`_resolve_tool`（L113-153）先精确匹配全名，简名桶命中唯一候选才放行，**多候选返回 None 强制调用方写全名**（L149-151），execute 里给出带候选列表的结构化错误（L205-216）。执行期自动 warmup（L229-235，兼容同步/异步回调）+ get_or_create 会话（L242）。

**config_loader**（config_loader.py，540 行）。`expand_env_vars`（L44-84）递归展开 `${VAR}` 与 `${VAR:-default}`（正则 L60），缺省且无默认时保留原占位符并告警（L72-74）——不崩、可审计。`load_class`（L277-293）是 backend 的字符串定位器：`rsplit(".", 1)` 拆模块与类名（L288）、`importlib.import_module` 动态加载（L289）——配置文件里的 `backend_class: "sandbox.server.backends.resources.vm.VMBackend"` 就是靠它变成类对象。`create_server`（L295-366）组装全流程：L314-316 两行函数内 import 破循环（app 反向依赖 core→backends），L333-352 遍历资源动态实例化 backend 并 load_backend，单个失败只 error 不中断（L354-355）；L368-423 `_load_api_tools` 第三处延迟 import（L381）拉注册表挂无状态工具。三处函数内延迟 import 与 rollout 两处 `__getattr__`、sandbox/mineru 两处包级懒加载合为仓内 7 处先例（03 篇已总述）。

**VMBackend**（resources/vm.py L292，全仓最大 2198 行）。19 个 `@tool` 标记从 L907（vm:screenshot）铺到 L1981（vm:evaluate），覆盖鼠标/键盘/滚动/拖拽/pyautogui 透传全套桌面动作。配置默认值（L345-369）锚定 provider="docker"、四端口 5000/9222/8006/8080、client_password 默认 "password"。会话级 VM 用对象池管理：`_vm_pool` deque + asyncio.Lock（L373-377），`_create_pool_item`（L449）经工厂 `create_vm_manager_and_provider`（L456）拿 manager/provider，start_emulator 有 TypeError 双签名兼容（L466-468——os_type 第三参是本仓对上游接口演化的适配补丁），VM 地址字符串 `host:server:chromium:vnc:vlc` 由 `_parse_vm_address`（L415-447）拆解、缺省端口从默认回填。收尾的 `vm:evaluate`（L1981）是 OSWorld 评测协议的服务化：吃 evaluator 配置（func/result/expected/options/conj），postconfig 可先跑 setup（L2012-2027，含惰性 proxy 就绪），infeasible 判定与 last_action_failed 短路（L2035-2052），再 `_resolve_metric`/`_resolve_getter`（L2093-2105）把字符串名映射到 desktop_env 的 metrics/getters 模块函数逐条算分。

**VM 双 provider**（utils/desktop_env/providers/）：`Provider` 与 `VMManager` 双 ABC（base.py L4/L47）——前者管单 VM 生命周期（start_emulator/get_ip_address/save_state/revert_to_snapshot/stop_emulator 五操作），后者管注册表（add/delete/occupy/list_free/check_clean）。工厂 `create_vm_manager_and_provider`（providers/__init__.py L5-28）按名分发 docker/aliyun，两个分支各自函数内 import（L16-17、L20-21）——不用的 provider 的重依赖（如 aliyun SDK）永不加载。Docker 版 184 行：`_get_available_port(9222)` 从默认口起探可用口（provider.py L96）、端口绑定 `"9222/tcp": self.chromium_port`（L135）、地址串拼装（L160）。Aliyun 版 430 行，ECS 云主机路径。

## 外部连接

上游：client.py/rollout 经 HTTP 驱动（routes.py 把 17 个协议端点挂到 FastAPI）；无状态工具与 tool_schemas 见 02 篇。下游：VMBackend 内嵌 desktop_env（05 篇）的 controllers/setup.py（SetupController）与 evaluators；config_loader 消费 configs/sandbox-server/*.json（GUI/ds/rag/web/doc/mcp/text2sql 七份 profile 与四场景一一对应）；`start_sandbox_server.sh` 与 cli/sandbox-server.py 是两种启动入口。

## 数据流

服务端视角的一次冷启动：配置 JSON → ConfigLoader.load（env 展开）→ create_server（动态类加载三 backend + 注册表挂 API 工具）→ FastAPI lifespan 起 TTL 清理循环 → 首次 execute("vm:screenshot") 触发 ensure_backend_warmed_up（VMBackend 建池）→ get_or_create_session（initialize 拉起一台 VM，地址端口回填 session_info["data"]）→ 后续动作复用该会话直达 controller → 会话 TTL 到期或显式销毁 → cleanup 归还 VM 入池（pool_reset 决定是否 revert 快照）。

## 设计决策（含批判）

- 「容器不干活」+ 三层映射：server 极薄、测试极易（mock 一个 Backend 即可起全链路）；代价是 register_tool 三结构必须手工保持一致，任何绕过 register_tool 直改 dict 的代码都会腐蚀索引。
- **简名歧义显式失败**（L149-151）：比「按注册顺序取第一个」诚实得多——rag:search 与 doc:search 并存时裸 `search` 会得到带候选的 4002，agent 能自行消歧。
- **compatibility_mode 会话**（resource_router L244-250）：未注册 initializer 的资源照样建会话，代价是「配错 resource_type」的 bug 会被降级成正常响应，直到工具执行才暴露——调试期建议关掉。
- **backend 加载失败仅日志不中断**（config_loader L354-355）：单 backend 崩不拖垮全服务（韧性），但也让「默认配置引用不存在的 bash/browser/code_executor」这类错误（sandbox.py L52-78）能静默存活——上线前务必核对日志里的 ❌ 行。
- **字符串定位类**（load_class）：配置驱动、增 backend 零代码改动；但拼写错误要到运行时才炸，且给了任意 import 的能力面——配置文件的受信等级因此提升为代码同级。
- **client_password 默认 "password"**（vm.py L362）：便利与安全的折中写死在默认值里，生产部署必须显式覆盖。

## 新人提示

1. 读码顺序：base.py（先看 L120-151 生命周期图）→ app.py 三层结构 → tool_executor 两步解析 → 任意一个 Backend。VMBackend 2198 行不必通读，抓 L292-380 配置与 L1981 evaluate 两段即可。
2. 新增有状态后端：继承 Backend、定 name、方法挂 `@tool("xx:yy")`、配置文件加 backend_class 字符串——四步内 server 侧零改动。
3. 排查「工具找不到/名字歧义」直接看 execute 返回的 candidates 字段；排查「VM 起不来」先看 `_parse_vm_address` 拆出的四端口与 docker ps 的绑定是否一致。
4. 改配置记得 `${VAR}` 展开发生在 load 时——运行中改环境变量不会生效，需重启服务。
