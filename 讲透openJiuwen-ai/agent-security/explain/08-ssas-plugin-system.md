# 08 · ssas 插件装载枢纽：manager.py 的声明式检测模块体系

## 一、角色定位

`module_manager/manager.py`（587 行，下文简称 manager.py）是 agent_ssas 引擎里唯一的"装配车间"。检测模块（detection module）是这套系统的可插拔检测单元，定义是固定三元组：**1 个数据建模插件 + 1 个威胁分析插件 + 1 个独立存储管理器**（manager.py:76-97 的 `DetectionModule` dataclass）。manager 负责"扫描→加载→注册→订阅→存储"全生命周期，流水线（07 篇）运行时只向它问两个问题：谁订阅了这个事件（`get_subscribers_with_mode`）、给我模块实例和存储（`get_module`/`get_storage`）。

它解决的核心问题是**让新检测能力零代码接入**：写一个目录、放一份 `module.yaml`、实现一个 analyzer 类，引擎启动时自动发现并挂载——不需要改引擎任何一行代码。这与 agent_shield 走的"编译期固定管线"路线（见 03 篇）是同一仓里的两种哲学对照。

## 二、内部结构

### 扫描：约定优于配置的目录协议

`initialize()`（manager.py:131-158）扫描 `detection_modules/` 目录，规则极简：

- 只认子目录，且跳过 `_` 前缀目录与名为 `common` 的组件目录（manager.py:145-149）——common 是放共享组件的地方，自己不是模块；
- 子目录里必须有 `module.yaml`，否则静默跳过（manager.py:150-152）；
- 单个模块加载失败只 `logger.exception` 后继续（manager.py:153-158）——一个坏模块不能拖死整个引擎，这是 fail-open 在装配层的体现。

模块目录的定位不走相对路径，而是从已安装的 `agent_ssas.core` 包自省：优先 `__path__`（兼容命名空间包），回退 `__file__`（manager.py:217-225）。这直接呼应 pyproject.toml 的一处关键配置：`[tool.setuptools.package-data] agent_ssas = ["**/*.yaml"]`，其注释明言"缺失该配置会导致正式安装(非 editable)场景下检测模块无法加载"（agent_ssas/pyproject.toml:39-43）——module.yaml 是按安装路径定位的数据文件，必须随包分发。src layout 则由 `[tool.setuptools.packages.find] where = ["src"]`（agent_ssas/pyproject.toml:36-37）锚定。

### module.yaml：声明式绑定

以 security_rail_detection 为例（`agent_ssas/src/agent_ssas/core/detection_modules/security_rail_detection/module.yaml`）：

```yaml
name: security_rail_detection
subscribed_events:
  - "permission_interrupt_tool"    # 默认 notify 模式
analytic_type_id: 1
plugins:
  - type: data_modeling
    name: BlankDataModeler
    model_type: blank
  - type: threat_analysis
    name: SecurityRailAnalyzer
    expected_model_type: blank
```

`_parse_module_yaml`（manager.py:342-412）的校验只挑硬性的：根节点必须是 dict、必须有 name、plugins 必须是 list 且同时包含 `data_modeling` 与 `threat_analysis` 两个类型各至少一个（manager.py:392-399）。其余字段全部给默认值：`enabled: True`、`subscribed_events: ["*"]`、`auth_timeout_policy: "allow"`、`report_only_risks: False`、`analytic_type_id: 0`（manager.py:401-412）。

加载时还有一个配置覆盖链：`config.yaml` 的 `ssas.modules.<name>.enabled` 可以远程翻转模块开关（manager.py:243-249）——module.yaml 管声明，运行时配置管启停，两层分离。加载完还会反向审计：config.modules 里配了但没扫到的模块名（拼写错误）打 warning（manager.py:160-169），这是少数"配置错误有反馈"的地方。

### importlib 双路径动态加载

`_instantiate_plugin`（manager.py:414-486）是整个装载体系最有意思的 30 行。给定插件名，它按两条路径找类：

1. **框架预置插件**：`agent_ssas.core.framework.data_modeler.plugins` 或 `...threat_analyzer.plugins`（manager.py:451-463）——通用插件（如 BlankDataModeler/BlankThreatAnalyzer 透传件）住这里，全模块共享；
2. **模块专属插件**：把 PascalCase 类名转 snake_case 推导文件名（`SecurityRailAnalyzer` → `security_rail_analyzer`，manager.py:488-503），拼出 `agent_ssas.core.detection_modules.<模块名>.<文件名>` 再 import（manager.py:466-474）。

两处都 `getattr(mod, plugin_name, None)`，拿不到就是 None，两路皆空抛 ImportError（manager.py:476-479）。实例化时先尝试 `cls(plugin_config["config"])` 注入专有配置，构造函数不收参数就 TypeError 回退到无参 `cls()`（manager.py:481-486）——兼容"空白插件"最简写法。

### 订阅注册：语法糖与展开

`_register_subscription`（manager.py:283-327）解析三种事件规格：

- `"tool_input"`：基础事件，notify 模式；
- `"tool_input:auth"`：冒号后缀声明 auth 模式（manager.py:295-297）；
- `"one_toolcall_event"`：聚合事件，按 `_AGGREGATE_EVENT_MAP` 展开成基础事件子订阅，auth 只落在结束事件上（07 篇详述）；
- `"*"`：通配一切，**强制 notify**（manager.py:300-306）——通配者不可能拿到同步阻断权，这是硬编码的安全边界，get_subscribers_with_mode 同样把通配订阅者的模式钉死为 notify（manager.py:527-531）。

订阅表双结构：`_subscriptions`（event_type → 订阅列表）+ `_subscriber_counts`（引用计数）。计数存在的意义是让"聚合事件订阅"能被 `has_subscribers` 感知——某基础事件即使无人直接订阅，只要被聚合事件间接覆盖，预处理器就知道这条链不能丢（manager.py:549-565）。

### 存储隔离

每个模块一个 `ModuleStorageManager`（manager.py:259-260），目录结构 `<ssas_home>/ssas/modules/<module_name>/{process.db, result.db, config/}`（module_store.py:26-27）。注意懒创建语义：result.db 立即建（告警审计常驻），process.db 延到首次访问才建——注释给出理由："v0.1 无写入方,立即创建会产生空库与常驻连接开销"（module_store.py:31-32, 98）。

## 三、外部连接

- **上游**：`AgentSSASBackend.initialize()` 是唯一触发者（agent_backend.py:113，经由 07 篇的防竞态守卫）；`close()`/`cleanup_all()` 分别在 backend 关闭与 TTL 清理时回调（manager.py:171-202）。
- **下游**：`ThreatAnalysisPipeline` 通过 `get_subscribers_with_mode` 拿订阅、`get_module` 拿插件实例直接调 `module.modeler.build_model` / `module.analyzer.analyze`（pipeline.py:379-395）。
- **插件协议**：`DataModelerPlugin`/`ThreatAnalyzerPlugin` 同样是 `runtime_checkable` Protocol（data_modeler/interfaces.py:15-25、threat_analyzer/interfaces.py），各声明一个 async 方法 + 一个配对字段（`model_type` ↔ `expected_model_type`）。
- **配置系统**：`AgentSSASConfig`（settings.py）注入 storage 路径与 modules 覆盖段；环境变量映射如 `SSAS_AUTH_TIMEOUT`（settings.py:233）。

## 四、数据流

一次引擎冷启动的装配数据流：

```
AgentSSASBackend.initialize()
  → DetectionModuleManager.initialize()
    → 扫描 detection_modules/（跳过 _* 与 common）
    → 逐目录: _parse_module_yaml（校验+拆 plugins）
    → config.modules 覆盖 enabled（module.yaml ← settings）
    → _instantiate_plugin ×2:
        modeler: BlankDataModeler ← framework/data_modeler/plugins
        analyzer: SecurityRailAnalyzer ← detection_modules/<name>/security_rail_analyzer
    → ModuleStorageManager(name, ssas_home) → result.db 建库
    → _register_subscription × N → _subscriptions + _subscriber_counts
  → 首事件到达 → pipeline.get_subscribers_with_mode(event_type)
    → [("security_rail_detection", "notify")] → 后台四步流水线
```

写一个新模块的最小清单也因此确定：目录名（=模块名=Python 包名）、module.yaml（name + plugins 两条 + subscribed_events）、analyzer 文件名必须等于类名的 snake_case——文件名约定是隐式契约，起错名就是 ImportError。

## 五、设计决策与权衡

1. **声明式 YAML 而非注册代码**。加模块不改引擎源码，代价是绑定关系散落两处（yaml 的 name ↔ 类名 ↔ 文件名 snake_case）。改名时三处必须同步，错一处只在运行时暴露。
2. **model_type 配对是文档约定，不是加载期校验**。`model_type: blank` ↔ `expected_model_type: blank` 的配对只写进 interface 注释（data_modeler/interfaces.py:23）与 yaml 字段，manager 加载时不做任何相等性检查——配错了照样装配成功，运行时 analyzer 拿到不认识的数据靠自身的防御分支兜底（SecurityRailAnalyzer 先查 event_class，security_rail_analyzer.py:53-60）。灵活但脆弱。
3. **通配订阅钉死 notify**。"*" 订阅者天然是观测者，不能变成阻断者（manager.py:300-306）——把权限边界做进语法而非纪律。
4. **失败隔离到模块粒度**。单个模块 yaml 坏/插件缺失/实例化异常，只丢该模块（manager.py:153-158）；配合 config.modules 拼写审计（manager.py:160-169），装配错误可见但不致命。
5. **保留了一个未接线的驱动器层**。`data_modeler/modeler.py` 的 `DataModeler` 与 `threat_analyzer/analyzer.py` 的 `ThreatAnalyzer`（按模块名分发插件的驱动器类，modeler.py:20-40）在包 `__init__` 里导出，但全仓无任何消费点——pipeline 直接持有 `module.modeler/analyzer` 属性调用（pipeline.py:386, 395）。它们与 07 篇的 `AccessAdapter` 同属"0.1 版为扩展预留的空转层"。
6. **存储按模块分库而非共库分表**。process.db/result.db 独立于主库 ssas_core.db（module_store.py:26-27），模块的中间数据生命周期与主库解耦，TTL 语义也分开（event_ttl_days vs alert_ttl_days，manager.py:184-202）；代价是跨模块关联查询要走应用层。

## 六、新人提示与坑

- **agent_moss 是文档幽灵**。agent_ssas/README.md:52 与设计文档（design/AgentSSAS_01_整体架构设计文档.md:893-899）都宣称 0.1 版内置 3 个检测模块：agent_moss（规则+行为链+Agent Behavior Graph 数据泄露分析）、security_rail_detection、test_detection。但发行目录里只有后两个 + common。agent_moss 的建模器/分析器/测试（design/test-reports/AgentSSAS_测试报告.md:397 的 test_agent_moss.py 7 用例）全不在仓内。以 README 为准排障必然扑空，以目录为准才是事实。
- **test_detection 默认 disabled 且订阅 `*`**（test_detection/module.yaml:5-6）。一旦你在 config.modules 里把它的 enabled 翻开，它会以 notify 模式吃所有事件——链路验证利器，生产环境噪音源。
- **插件实例化回退掩盖配置错误**。`cls(cfg)` TypeError 后静默回退 `cls()`（manager.py:481-486）：如果你的插件构造函数签名写错（比如多了一个必填参数），不会报"参数不匹配"，而是拿到一个没有配置的实例，表现为"插件行为和 yaml 里的 config 不一致"。排查时先看构造函数签名。
- **框架插件优先于模块插件**。同名类在两处都有定义时，framework 目录赢（manager.py:459-465 的顺序）——想在模块目录里覆写框架插件是行不通的。
- **模块目录名进 import 路径**。`agent_ssas.core.detection_modules.<module_dir_name>` 要求目录名是合法 Python 包名；module.yaml 里的 `name` 字段理论上可以与目录名不同，但存储管理器用 config name（manager.py:260）、插件查找用目录名（manager.py:467-469），两者不一致时会出现"存储目录叫 A、代码包叫 B"的分裂态——实践上必须保持一致。
- **包数据陷阱**：editable 安装（`pip install -e`）下 yaml 永远能找到（源码树就在），正式安装才暴露 package-data 缺失问题。pyproject 的注释（agent_ssas/pyproject.toml:39-43）说明作者踩过这个坑，改动打包配置时别把 `**/*.yaml` 弄丢。
