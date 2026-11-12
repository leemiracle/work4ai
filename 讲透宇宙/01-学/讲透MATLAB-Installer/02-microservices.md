# 02 · 微服务总线：OSGi for C++

## 机制

每个业务 so 是一个 **CppMicroServices bundle**：用 objcopy 把 zip（含 `manifest.json`）嵌进二进制（`_binary_..._metadata_zip_start/_end` 符号为证）。manifest 用 **SCR（声明式服务）**描述：实现类 + 提供接口 + 引用注入 + 配置 PID。运行时由 `libCppMicroServices.so.3.8.3 + libusServiceComponent.so + libConfigurationAdmin.so + mwManagementAgentImpl.so` 组成容器。

manifest 样例（urlmanager）：
```json
{"scr":{"components":[{
  "implementation-class":"foundation::urlmanager::impl::UrlManager",
  "service":{"interfaces":["foundation::urlmanager::UrlManager"]},
  "references":[{"interface":"cppmicroservices::logservice::LogService"}],
  "configuration-pid":["mw.UrlManager"]}]}}
```

## 服务全景（64 bundle / 130 组件，提取自全部内嵌 manifest）

**foundation 地基**：UrlManager（端点注册表，pid `mw.UrlManager`）· HttpClient/WebSocketClientFactory · LibCurlInitializer · ProxySelector · SessionIdRegistrar

**agent 环境**：Realm（**prod/dev 双实现**，prod 组件属性 `matlabservicesmode=prod`，pid `mw.agent.realm.Realm`）· SPF 服务框架（ServiceProvider/Serialisation/ServicePublisher/ThreadPool 四 provider）

**install 安装域**：RepositoryAdapter 三实现（folder 本地 / online_product 在线产品 / online_supportpackage 支持包）· ActivationWSClient · ActivationService · DeviceBasedUtils（设备激活）

**connector 本地总线（14 so）**：HttpServer/HttpRouter/HttpSessionManager/StaticContentService · **BayeuxServer(CometD 长轮询)** · ContainerDispatcher(v1) · JsonSerializer · **NonceService**（防重放）· HitchhikerService · RequestResponseRegistry · Administration/CommandProvider · MessageServiceFactory · LifecyclePlugin · BinaryStreamFactory

**CEF 宿主**：X11DisplayManager · webwindowManager_extprocess · **CatapultMessageProtocol**（CEF 外进程控制）· DDUX LoggingService（遥测）

**mf0 模型层**：`mf::zero::services::*`——MetamodelLoader（元模型加载，`mwinstall_datamodels_*_ms_gen.so` 自动生成）/ IOFormatProvider / ArborealFormatProvider（树形格式）/ ModelIdNormalizer

**其它**：ITripwire（熔断）· ApplicationLauncher（interactivelauncher）· DesktopServicesRealm

## 怎么理解这个设计

1. **安装器=迷你应用服务器**。MathWorks 把 Eclipse OSGi 模型搬到 C++：功能热插拔、接口注入、配置中心（ConfigurationAdmin）。团队可以按 bundle 独立开发发布（每 so 独立签名独立版本节奏）。
2. **UI 是本地 Web 应用**。CEF 前端通过 Connector 的本地 HTTP+Bayeux 总线消费服务——同一套 UI 可跑在浏览器（MathWorks Online 同款栈）。
3. **dev/prod 同构**。dev realm bundle 让同一安装器连 MathWorks 内部开发环境（配 03 册 WS_ENV），内部 dogfood 与外部发布同一二进制。
4. **每个 bundle 一个配置 PID**（`mw.UrlManager`、`mw.agent.realm.Realm`...）——运维/测试有正规注入位，也是攻击者的正规注入位（07 册安全观察）。

## 与 Claude Code 对照

Claude Code（Bun 单文件 215MB）与 MATLAB 安装器（64 bundle 微服务）是分发的两个极端：前者优化"拷一个文件就能跑"，后者优化"百人团队并行演进"。共同点：UI 都 Web 化、都把网络层做成独立抽象。
