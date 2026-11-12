# 04 · dcgmi CLI：Command 命令模式与子命令族

## 角色定位

dcgmi 是用户与 nv-hostengine 对话的唯一官方 CLI。它的骨架是教科书级命令模式（Command pattern）：dcgmi/Command.h 定义基类，dcgmi/ 目录下 30 余个 Dcgmi*.cpp 每个是一片子命令族（Query/Policy/Group/FieldGroup/Config/Health/Diag/Module/Settings/Test/Nvlink/Introspect/MnDiag/DeviceMonitor/ProcessStats/Environment…），参数解析总枢纽 CommandLineParser.cpp 有 **3168 行**。入口极薄：main_dcgmi.cpp 全文 84 行，main 在 :54，只做 ProcessCommandLine 分发（main_dcgmi.cpp:74）。

## 内部结构

基类 Command（dcgmi/Command.h:27-69）是模板方法模式的范本：公开非虚的 Execute（Command.h:49）与 Connect（:37）固化执行骨架，子类只须实现纯虚 DoExecuteConnected（Command.h:57）；连接失败可覆写 DoExecuteConnectionFailure（:59）。执行链在 Command.cpp:83-91——Execute → Connect（:48）→ dcgmConnect_v3 建真实连接（Command.cpp:69，参数 dcgmConnectV3Params_t :50）→ 成功调 DoExecuteConnected（:91），失败走 :88。关键语义 persistAfterDisconnect（Command.h:44 的 SetPersistAfterDisconnect，成员声明 :64-66）被透传进连接参数（Command.cpp:65-66）：dcgmi dmon 这类常驻采集进程退出后 watch 是否保留，由这一位决定。成员还携带 m_hostName/m_dcgmHandle/m_timeout/m_json/m_silent（Command.h:61-68），所有子命令共享远程主机与输出模式。

参数枢纽：CommandLineParser::StaticConstructor（CommandLineParser.cpp:101）把 17 个子系统名注册进 m_functionMap 函数指针表（:104-120：discovery/policy/group/fieldgroup/config/health/diag/stats/topo/introspect/nvlink/dmon/modules/profile/set/test/mndiag）；ProcessCommandLine（:125）用 TCLAP::CmdLine（:132）与 OneOf 约束（:148-150）解析出子系统名后查表分派。最大的分派目标是 ProcessDiagCommandLine（403 行，:1979），diag 是选项最多的子命令；policy/health 各 250/184 行（:358/:1218）。横切辅助有 NormalizeUnixSocketPath（42 行）、GetHostListVector（133 行）、ValidateClocksEventMask（56 行）、多节点诊断合并校验 ProcessAndValidateMnDiagParams（134 行）。

## 外部连接

向下全部经 dcgmlib 公共 API：连接（dcgmConnect_v3）、profiling（DcgmiProfile.cpp:45 的 dcgmProfGetSupportedMetricGroups、:101/:106 的 dcgmProfPause/dcgmProfResume）。字段元数据查 DcgmFieldGetById（DcgmiProfile.cpp:67）。向上是三类消费者：运维脚本（dmon/topo/stats）、诊断流水线（diag/mndiag）、CI（dcgmi/tests/ 的 CommandLineParserTests.cpp 约 1600 行，ScopedCommandExecutor 挂执行钩子免起 hostengine；mock/MockDcgmiStatus.cpp 与 MockDcgmiGroupInfo.cpp 提供预置返回，StdoutRedirect/TempFile 在 tests/DcgmiTestHelpers.hpp 捕获输出）。

## 数据流

以 `dcgmi profile --list` 为例：main（main_dcgmi.cpp:54）→ ProcessCommandLine 查表命中 "profile"（CommandLineParser.cpp:117）→ ProcessProfileCommandLine 解析 -l/--pause → 构造 DcgmiProfileList（DcgmiProfile.cpp:122-132，构造期把 hostname/json 存入基类成员）→ Execute：Connect 成功后 SetGpuIdFromEntityList 用 EntityListWithMigAndUuidParser 解析实体串（DcgmiProfile.cpp:135-143）→ RunProfileList（:34-91）调 dcgmProfGetSupportedMetricGroups 拿 metricGroups，逐字段查 tag 填 DcgmiOutputColumns/Json（:37-39 二选一），majorId 映射为 A/B/C 字母组名（:77），最后 out.str() 一次性渲染。错误统一经 errorString 翻译成可读串（:48 模式）。

## 设计决策

1) **模板方法而非全虚**：Execute/Connect 非虚，连接协议升级只改一处，30+ 子命令零改动。2) **persistAfterDisconnect 放在连接层**而非 watch 层，让"短命令"与"常驻采集"共用同一 Command 骨架，语义分界一个布尔位。3) **函数指针注册表**新增子命令只动 StaticConstructor 一行 + 一个 Process* 函数，主流程不碰。4) **输出与逻辑分离**：DcgmiOutput.h 的 Boxer/Tree/Columns/Json 四渲染器让同一数据天然支持人类可读与 -j JSON，子命令不写 printf。5) TCLAP 之上再包 DCGMEntryOutput（CommandLineParser.cpp:135-136）定制 usage 分组（:198-199 addToGroup）。6) mock + stdout 捕获的测试体系使 3168 行解析逻辑可离线回归，这是 dcgmi 少数有成建制单测的模块。

## 新人提示

新增子命令清单：写 DcgmiXxx.h/.cpp 继承 Command → 实现 DoExecuteConnected → StaticConstructor 注册（CommandLineParser.cpp:104-120）→ 写 ProcessXxxCommandLine → 补 TCLAP 参数与 usage 分组。调试时先看 Command.cpp:83-91 确认死在 Connect 还是 DoExecuteConnected；DCGM_ST_CONNECTION_NOT_VALID 多半是 hostengine 未起或 socket 路径不匹配（NormalizeUnixSocketPath 会改写它）。profile 的 --pause 是全局开关（RunProfileSetPause 无 GPU 参数，DcgmiProfile.cpp:94-119），影响所有 GPM 采集，别当 per-GPU 用。测试先抄 CommandLineParserTests.cpp 的 RequireParserOkAndExecuted 模式，别自建脚手架。
