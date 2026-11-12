# 04 · NVTXW 后端注入与 sample-injection：Payload 解析参考实现

## 角色定位
NVTXW 是 NVTX 的"可替换写出后端"协议：应用不再依赖 Nsight 注入，而是把事件流交给自选后端（写文件、转 JSON、送自研分析器）。`tools/sample-injection/`（15 文件）是官方给出的完整范本——既是 C/C++ 测试的注入库（PrintInjection 一线的扩展版），也是第三方工具接入 NVTX 的抄写模板。

## 内部结构
入口 `tools/sample-injection/Source/NvtxSampleInjection.cpp`（594 行）四段式：`InitializeInjectionNvtx2:523` 导出入口握手（`:532` 打印进程号/时间戳的调试横幅）→ `GetFunctionTable:105` 按 `NvtxCallbackModule` 从应用导出表取各模块函数表（`:548` 取 `NVTX_CB_MODULE_CORE`）→ `InitializePayloadExtension:458` 注册 Payload 扩展模块（SchemaRegister/EnumRegister/事件回调，`:87` 注释说明 typeInfo 就绪后才构造解析器）→ `TearDownDetector:91-93` 析构钩子做进程退出清理。

Payload 解析子系统（`Source/Payload/`）三层：
- **数据模型** `NvtxPayloadSchema.h`：`PayloadSchemaEntry`（字段条目）、`PayloadSchema`（定稿 schema）、`PayloadEnum`（枚举）与布局处理器接口。
- **注册表** `NvtxPayloadRegistry`（`NvtxPayloadRegistry.cpp`）：`AddSchema/AddEnum` 从 NVTX 属性数组构建工具侧注册表（HasId 去重），`VisitPayloads` 委托解析器。
- **解码引擎** `NvtxPayloadParser.cpp`（976 行，核心）：`BuildFieldDecodeInfo` 预计算每字段解码信息，`Emit*Field` 族按类型（整数/浮点/C 字符串/枚举/嵌套/预定义）从原始负载字节读取，经 `PayloadStreamVisitor` 抽象接口（`NvtxPayloadParser.h`，`OnPayloadBegin/OnFieldBegin/OnSignedInteger` 等 18 回调）输出；`NvtxPayloadSchema.cpp`（528 行）的 `FinalizeSchema` 递归计算嵌套布局并校验。辅助件 `NvtxPayloadUtils.h`（类型分类/对齐/数组长度）、`UtfStringConversion.h`（UTF-16/32→UTF-8 含代理对）。

适配层 `NvtxPayloadInjectionAdapter.cpp`：`RegisterSchema/RegisterEnum` 动态分配 id 与静态 id 校验，`DescribePayloads` 把事件负载交给格式化器。两个格式化器对称：`NvtxPayloadJsonFormatter.cpp`（EscapeJson 转义+十六进制字节）与 `NvtxPayloadTextFormatter.cpp`（缩进字段树）。

## 外部连接
上游是 `nvToolsExtPayload.h`（1794 行）的结构化负载 API：schema 描述 `nvtxPayloadSchemaEntry_t:991-1078`、注册 `nvtxPayloadSchemaRegister:1343`/`nvtxPayloadEnumRegister:1356`、事件 `nvtxRangePushPayload:1399`。下游测试线：`tests/src/MockNvtxwBackend.h`（602 行）实现完整 `nvtxwInterface_v2` 函数表并录制一切到单例 Recorder；`tests/src/CoverageNvtxwE2E.c`（314 行）经 setup/lifecycle 助手走完整会话（域/作用域/流/时间域）做端到端断言；`tests/src/CoverageNvtxwC.c`/`CoverageNvtxwCpp.cpp` 双翻译单元验证 helper 头 C/C++ 皆可编译。Python 侧 `python/src/nvtx/writer.py:19-29`（docstring）是同一思想的 Python 化：显式时间戳事后写出，nsys_writer 即其后端。

## 数据流
应用注册 schema（C 数组描述字段布局）→ 事件携带 schemaId+原始结构体字节 → 注入库收到扩展回调 → Registry 查表 → Parser 按预计算的 offset/size/类型逐字段读字节（处理符号扩展、UTF-16/32 解码、变长数组）→ visitor 回调流 → JSON/Text 格式化器落地。字节级细节（符号扩展、C 字符串解码）在 `NvtxPayloadParser.cpp` 全部可见，是 schema 驱动解码的教学级实现。

## 设计决策
- **visitor 模式**分离解码与输出：一个解码引擎配多个格式化器，新增输出格式零解码改动。
- **注册表镜像**：工具侧重建一份 schema/枚举注册表而非每次回调解析属性数组，解码热路径只查表。
- **adapter 层隔离注入协议与解析子系统**：换掉 NvtxSampleInjection 的握手方式不影响 Payload 管线。
- 测试用**录制式 mock 后端**（不落盘只录制）换取逐字段断言能力。

## 新人提示
通读顺序：`NvtxSampleInjection.cpp:523`（握手）→ `NvtxPayloadInjectionAdapter.cpp`（桥接）→ `NvtxPayloadParser.cpp` 的 `Emit*Field` 族（解码）。自建 NVTXW 后端时先抄 `InitializeInjectionNvtx2` 与 `GetFunctionTable:105` 的模块化取表逻辑；验证解码正确性用 `tests/src/PayloadEntriesHelper.h:31-32` 的 `NVTX_DEFINE_STRUCT_WITH_SCHEMA` 宏生成 3..7 字段对照结构。JSON 输出的十六进制字节段是排查 schema 与实际内存布局不一致的第一现场。
