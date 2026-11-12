# spdm（spdmcpp）Onboarding — NVIDIA 的 DMTF SPDM C++ Requester 栈

> 基于图谱 1069 节点/1484 边（10 层/11 步 tour）与全量源码行号锚核实（commit 2c5e6d28，2026-10-24）。
> 所有 `路径:行号` 锚均相对仓根，写作时逐条 grep 核实。

## 1. 项目定位与解决的问题

spdm 是 NVIDIA 维护的 **DMTF SPDM 规范（DSP0274，Security Protocol and Data Model）的 C++ 实现**，Apache-2.0 协议，meson 工程版本 0.1.0（`meson.build:5`）。它解决的问题很具体：在 openBMC 环境里，BMC 作为 **Requester** 通过 MCTP 总线对带外部件（HGX 平台的 ERoT / GPU / Retimer 等）做**身份认证（证书链验证）与完整性度量（measurements）**——即 DSP0274 三大 flow：能力发现与协商（10.1）、Responder 身份认证（10.5）、固件与其他度量（10.10），这三条在 `libspdmcpp/headers_public/spdmcpp/connection.hpp:137-141` 的类文档里被逐条点名，是全库的"宪法条款"。

仓库交付四类产物：**libspdmcpp**（协议库本体）、**spdmd**（openBMC D-Bus 守护进程）、**spdmutil**（手工探测 CLI）、**fuzzer + tools**（模糊测试/负向注入/合规裁决/压力基准）。注意仓库是纯 Requester 侧实现——Responder 只在 fuzzer（伪造响应）和外部 DMTF emulator 中出现；spdmd 名字里的 "Responder" 指它在 D-Bus 上**呈现**远端 Responder 的数据（`spdmd/dbus_impl_responder.cpp`），不是自己实现 SPDM Responder 协议角色。

## 2. 总体架构与分层

meson 顶层只编排五个子目录：`meson.build:104-109` 依次 `subdir` libspdmcpp → tools/libmctppacketcorrupt → fuzzer → spdmd → spdmutil。对应图谱十层：

| 图谱层 | 内容 | 代表锚 |
|---|---|---|
| L01 治理/构建 | meson 选项、config.h、6 个 wrap 子项目 | `meson_options.txt:1-19` |
| L02 公共基础 | 传输抽象/上下文/枚举/日志/状态码 | `common.hpp:126`、`context.hpp:44` |
| L03 报文编解码 | 21 个报文结构头 + packet.hpp 总装 | `packet.hpp:104` |
| L04 连接状态机 | ConnectionClass 三件套 | `connection.hpp:144` |
| L05 spdmd 守护 | 端点发现 + D-Bus 同步 | `spdmd/spdmd.cpp:337` |
| L06 spdmutil CLI | 六子命令探测 | `spdmutil/cmds.hpp:75` |
| L07 fuzzer | 录制回放双队列 | `fuzzer/spdm_fuzzer_app.cpp:70` |
| L08 合规/注入 | spdmcompl.py + libmctppacketcorrupt | `pktcorrupt.c:149` |
| L09 压力数据海 | 47 请求 JSON + 32 CSV 批次 | `tools/stress-test/launch.sh` |
| L10 单元测试 | gtest 三大件 | `connection_test.cpp:501` |

分层接缝是两个抽象接口：`TransportClass`（把 SPDM 报文裹进某种传输协议，`common.hpp:126`，含嵌套 `LayerState` `common.hpp:132` 负责 buffer 内分层布局）与 `IOClass`（报文的实际读写介质，`common.hpp:261`）。`ContextClass`（`context.hpp:44`）持有 IO 注册表并把两者装配起来——构造函数里固定声明支持 SPDM 1.0/1.1/1.2 三个版本并倒序排（`context.hpp:49-51`）。依赖方向严格单向：spdmd/spdmutil/fuzzer → libspdmcpp → headers_public，无反向引用。

## 3. 核心子系统深讲

### 3.1 报文编解码层（L03）

`packet.hpp` 是报文层唯一对外入口，但它同时是**include 守卫环**的中心：它 include 各子头（`packet.hpp:104` 起），而每个子头（如 `packet_message_header.hpp:18`）反过来 `#include "../packet.hpp"` 并以 `#ifdef SPDMCPP_PACKET_HPP` 包住自身——聚合器与成员互指但靠宏防环，任何子头只能经由 packet.hpp 生效。全部报文结构头共 **21 个**（internal 根 6 + request/ 8 + response/ 7，见 README 勘误 #3）。

所有报文共享前缀 `PacketMessageHeader`（`packet_message_header.hpp:24`）：MessageVersion / requestResponseCode / Param1 / Param2 四字段；序列化不依赖内存布局，走显式 `endianHostSpdmCopy` 逐字段端序拷贝（`packet_message_header.hpp:93-98`）。消息码表与 DSP0274 对齐：GET_VERSION=0x84、GET_CAPABILITIES=0xE1、NEGOTIATE_ALGORITHMS=0xE3、GET_DIGESTS=0x81、GET_CERTIFICATE=0x82、GET_MEASUREMENTS=0xE0、RESPOND_IF_READY=0xFF（`enum_defs.hpp:117-125`）。变长报文一律 Min/Var 双形态：定长前缀 `PacketVersionResponseMin`（`packet_version_response.hpp:24`）+ 尾部变长 `PacketVersionResponseVar`（`:63`），请求侧最简例是 `PacketGetVersionRequest`（`packet_get_version_request.hpp:24`）。

### 3.2 连接状态机（L04）

`ConnectionClass`（`connection.hpp:144`）是协议交互中枢，三件套分工：hpp 声明（928 行）、`connection_inl.hpp` 放模板热路径（`sendRequest` `:27`、`interpretResponse` `:95`、`setupResponseWait` `:128`、`sendRequestSetupResponse` `:162`）、`connection.cpp`（1525 行，全仓最大单文件）放全部事务方法。注意 `connection.hpp:43-79` 躺着一整段被注释掉的 `FlowClass`/`QueryFlowClass` 早期状态机（含 STATE_GOT_VERSION 等枚举），全仓零引用——**活的状态推进在事务方法链里**：`tryGetVersion`（`connection.cpp:365`）→`tryGetCapabilities`（`:478`）→`tryNegotiateAlgorithms`（`:548`）→`tryGetDigest`（`:676`）→`tryGetCertificate`（`:917`，分块拉取在 `tryGetCertificateChunk` `:743`）→`tryGetMeasurements`（`:935`/`:968`）。版本选择在 `chooseVersion`（`:442`），证书链解析/验证在 `parseCertChain`（`:275`）与 `verifyCertificateChain`（`:332`）。

支撑结构：`TimingClass`（`connection.hpp:86`）实现 DSP0274 第 9 节时序——RTT 默认 6000ms、T1 WAR 值 24000ms、`setCTExponent` 把规范微秒时延换算成毫秒（移位实现并注明丢精度）；`SlotClass`（`connection.hpp:505`）存证书槽（Digest/Certificates/mbedtls RAII 证书数组/GotInfo 位图），槽数上限 `slotNum = 8`（`:155`，DSP0274 page 56）；收发缓冲用 `BufEnum` A/B/C/L 四槽（`:489`）。事件循环入口 `handleEvent`（`connection.cpp:1403`）分派 `EventReceiveClass`/`EventTimeoutClass`（定义在 `event.hpp:59`/`:73`）；RESPOND_IF_READY 轮询最多 4 次（`connection.hpp:906` 的 `maxRespondIfReadyRetries` 与 `connection.cpp:1236` 的计数检查）；重试策略集中在 `handleTimeoutOrRetry`（`:1426`）与 `retryTimeout`（`:1465`），延迟轮询特化在 `handleResponseIfReadyDelay`（`:1510`）。

### 3.3 spdmd 守护进程（L05）

入口 `spdmd/spdmd.cpp`：CLI 解析、连接 MCTP、按发现结果动态建 Responder 对象——`discoveryUpdateResponder`（`spdmd.cpp:295`）按 UUID 去重，`needRecreateResponder`（`:226`）判定传输介质变化需重建，`createResponder`（`:337`）最终 `make_shared<dbus_api::Responder>`（`:370`）。度量策略可配置：`--all` 发现即取测量但受 `cached_measurements_delay` 节流（`spdmd.cpp:62`/`:67`/`:94-98`）。

发现引擎 `mctp_endpoint_discovery.cpp`（1611 行）是 openBMC 异步 D-Bus 风格的教科书：`MctpDiscovery` 构造（`:41`）→ `setupMCTPServices`（`:246`）监听 ObjectManager → `issueGetManagedObjects`（`:284`）拉全量对象，失败由 `scheduleGetManagedObjectsRetry`（`:335`）/`scheduleMapperRetry`（`:436`）退避重试；增量信号 `mctpNewObjectSignal`（`:491`）与 `inventoryNewObjectSignal`（`:897`）、UUID 属性变化 `inventoryUUIDChangedSignal`（`:710`）；启动期 `scanExistingInventoryUUIDs`（`:764`）扫存量。UUID↔MCTP 对象关联经 `getUUID`（`:1158`）、`getMCTPObjectAsync`（`:1240`）、`getInventoryPathAsync`（`:1314`）三级异步回调；传输介质判别 `getMediumType`（`:1450`）/`getBindingType`（`:1494`）；`initCsmStatus`（`:1530`）处理 CCSM 服务态。结果落 D-Bus：`dbus_impl_responder.cpp` 把版本（`:111`）、测量哈希（`:245`）、测量签名（`:257`）、测量块（`:267`）写入属性，签名验证失败明文告警（`:308`），版本号转字符串在 `getVersionStr`（`:39`）。systemd 单元是 D-Bus 激活 + 60s 看门狗 + pldmd 依赖（`spdmd/service_files/spdmd.service:8-10`）；端点显示策略由 `spdmd/conf_files/spdmd_conf.json` 的 endpoints 列表控制。

### 3.4 spdmutil CLI（L06）

六个子命令恰好对应状态机六类事务：`VerCmd/CapabCmd/NegAlgoCmd/CertCmd/MeasCmd/DigestCmd` 组成 std::variant（`spdmutil/cmds.hpp:27-75`）。主实现 `spdm_tool.cpp`（949 行）：`parseArgs`（`:64`）→ `connectMctp`（`:741`）→ `runComm`（`:482`）按命令发请求，`parseResp`（`:644`）分发到各 `handleRecv<T>` 特化（版本 `:261`、证书 `:372`、摘要 `:425`、度量 `:454`），证书链 PEM 化输出在 `parseCertChain`（`:803`）；`runEnumerate`（`:929`）调用 `enumerateMCTPDBusObjects`（`enumerate_endpoints.cpp:47`）收集 EID/UUID（`ResponderInfo` 组装 `:92`）。它是手工调 SPDM 链路的首选：一条命令一行结果，配合 fuzzer/合规工具形成调试三角。

### 3.5 MCTP 传输与 mbedTLS 密码支撑

`mctp_support.hpp` 用 Unix/AF_MCTP socket 落地两层抽象：`MctpTransportClass`（`:56`，内部 `HeaderType` `:154` 处理 MCTP 头的 tag/TO 位）与 `MctpIoClass`（`:200`，发送侧 5s 超时 `:205`）。关键常量：`MCTP_TAG_SPDM = 1`（`:42`）与 `MCTP_TYPE_SPDM = 5`（`:44`）是**两个不同维度的值**（tag vs 消息类型），README 的 "5 reserved for SPDM" 指后者（`README.md:49`）；单报文上限 `mctpMaxMessageSize = 4096`（`:49`）。内核态路径直接 `sendto` 到 `sockaddr_mctp`（`:430`）。密码侧 `HashClass`（`hash.hpp:113`）与 signature.hpp 基于 mbedTLS 完成摘要与签名验证上下文；`mbedtls_support.hpp` 做算法组 ID 映射与证书信息包装。

### 3.6 fuzzer：录制-回放模糊测试（L07）

`spdm_fuzzer_app.cpp:37` 的 main 装配 Requester/Responder **同进程对打**：两把 `FixtureIOClass`（`spdm_fuzzer_fixture.hpp:49`）以交叉双队列互联（`spdm_fuzzer_app.cpp:70` 的 run 里 queue1/queue2 互换注册），`FixtureTransportClass`（`spdm_fuzzer_fixture.hpp:36`）假扮传输。Responder 侧 `FuzzingResponder`（1121 行）可随机发脏数据（`sendRandomData` `spdm_fuzzer_responder.cpp:87`）、按预定义序列应答、并维护 transcript 哈希一致性（`getHash` `:81`、`updateHash` `:166`、`resetState` `:155`），甚至本地算签名（`computeSignature` 调用点 `:433`）。logConverter.sh 把运行日志转回放格式，logsOK/logsFail 留档 emu/hmc 两套用例。

### 3.7 libmctppacketcorrupt：负向注入（L08）

纯 C 写的 LD_PRELOAD 库，对**真实** MCTP 流量做字节级破坏。拦截机制在 `syscalls_wrap.c`：`dlsym(RTLD_NEXT, "recv")` 取真函数（`:117`），wrapper `_iosys_recv`（`:112`）收包后交 `corrupt_recv_packet` 改写（`:141`）；发送侧 `_iosys_send`（`:148`）；并用 `__asm__(".symver _iosys_recv,recv@GLIBC_2.4")`（`:145`/`:179`）钉死 glibc 符号版本防止绕过，还包了 connect（`:69`）与 close（`:186`）。破坏逻辑在 `pktcorrupt.c`：`is_packet_should_be_modifed`（`:36`，函数名原文即拼写错误）按 `corrupt_context`（`:33`）的 m/n 概率或指定序号决定是否下手，`packet_modify_buffer`（`:149`）按模式分派——cmds/reserved/msglen/version/certlen/unsupalgo/各 fields 修改（`:155-166` 与 `:60-98`），模式枚举定义在 `apptypes.h:54`。配置全走环境变量（MCTP_CORRUPT_MODE/RAND_LEVEL/DROP_EIDS/TYPES，`readme.md:10`/`:43`），丢包闸门是 `/tmp/corrupt_drop_enable` 文件存在性（`readme.md:49`）。

### 3.8 合规、压力与单测（L08-L10）

合规工具 `tools/compliance/spdmcompl.py`（494 行）：`load_config`（`:28`）读配置逐项裁决，`spdmt_cmd_exec`（`:57`）驱动 spdmutil，`enumerate_spdm_endpoints`（`:89`）、`load_measurements`（`:146`）等组织检查项，BMC 通道由 bmc_connection.py 封装 SSH/串口。压力侧两套：`tools/stress-test/`（launch.sh + **47 个**请求 JSON：fpga 11/hmc 11/indices 12/parallel 13）与 `tools/stress-test-bash/`（**32 张** CSV 批次 + process-results.py 统计延迟/成功率）——HGX ERoT 部件×测量索引的数据海。单测三大件守住行为基线：`connection_test.cpp` 的 `ConnectionFixture`（`:119`）用桩传输跑 FullFlow 算法矩阵（ECDSA×SHA 组合自 `:501` 起）；`packet_basic_test.cpp` 对全部报文做伪随机填充→编码→解码→比对往返（`returnPseudorandomPacket` `:144`，TEST 自 `:324`）；`mctp_endpoint_discovery_test.cpp`（1879 行）以 `MockSpdmdApp`（`:293`）+ `MctpDiscoveryTest` 套件（`:306`，用例自 `:334`）覆盖发现/重试/属性变化全路径。

## 4. 关键数据流

**握手-取数主流程（Requester 视角）**：上层（spdmd/spdmutil）调 refresh 系方法（`connection.cpp:121` 起的 `refreshMeasurements` 家族）→ 事务链按序推进 GET_VERSION→VERSION（`tryGetVersion` `connection.cpp:365`，选版 `chooseVersion` `:442`）→ GET_CAPABILITIES（`:478`）→ NEGOTIATE_ALGORITHMS（`:548`）→ GET_DIGESTS（`:676`）→ GET_CERTIFICATE 分块循环（`:743`→整链验证 `:917`→`verifyCertificateChain` `:332`）→ GET_MEASUREMENTS（`:935`）。

**单次请求-响应**：`sendRequest`（`connection_inl.hpp:27`）模板编码报文 → TransportClass `encodePre/encodePost`（契约见 `common.hpp:126` 起接口注释）在 buffer 里预留/补齐传输层 → IOClass 写 socket（MCTP 路径 `mctp_support.hpp:430` 的 AF_MCTP sendto）→ `setupResponseWait`（`connection_inl.hpp:128`）挂超时 → 数据到达成 `EventReceiveClass`（`event.hpp:59`）→ `handleEvent`（`connection.cpp:1403`）→ `handleRecv` 模板（`connection.cpp:1174`）→ `interpretResponse`（`connection_inl.hpp:95`）按 PacketDecodeInfo 解码，错包/超时走 `handleTimeoutOrRetry`（`:1426`）/`retryTimeout`（`:1465`）。

**spdmd 发现流**：MCTP ObjectManager 信号 → `mctpNewObjectSignal`（`mctp_endpoint_discovery.cpp:491`）→ 查 inventory UUID（`inventoryUUIDChangedSignal` `:710` / `getInventoryPathAsync` `:1314`）→ `discoveryUpdateResponder`（`spdmd.cpp:295`）→ `createResponder`（`:337`）建 D-Bus 对象 → Responder 拉取证书/度量并写属性（`dbus_impl_responder.cpp:245-267`）→ openBMC 消费。

**fuzzer 数据流**：requester 发包进 queue1 → responder 从 queue1 读、按模式生成应答（随机/预定义/篡改）并维护 transcript 哈希 → 写 queue2 → requester 校验 → 失败即退出码报告，日志可被 logConverter.sh 转为下轮回放输入。

## 5. 构建 / 运行 / 入口

- **构建**：`meson build && ninja`（C++23、warning_level=3、-Werror，`meson.build:7`/`:19`）。mbedTLS 优先系统库、缺失回落 wrap 子项目（`meson.build:58-76`）；版本与特性宏由 config.h.in 生成（`meson.build:29-52`）。
- **meson 选项**（`meson_options.txt:1-19`）：tests/spdmd/systemd 默认开；`enable-in-kernel-mctp`（`:17`）切内核 MCTP 栈（默认关=用户态 demux daemon）；`discovery_only_from_mctp_control`（`:5`）改发现源；`fetch_serialnumber_from_responder`（`:7`）取序列号写 pldm inventory；`use_fuzz`（`:15`）开模糊测试；**`emu`（`:9`）是死选项**——见勘误 #1。
- **spdmd**：systemd D-Bus 激活（`spdmd.service:8` Type=dbus，BusName=xyz.openbmc_project.SPDM `:10`），60s 看门狗（`:9`）；配置文件路径可由 `conf_file_name` 改（默认 /etc/spdmd_conf.json）。
- **spdmutil**：六命令直连 MCTP 总线探测；`LD_PRELOAD=libpacketcorrupt.so spdmd` 即可对守护进程注入损坏（`tools/libmctppacketcorrupt/readme.md:60`）。
- **合规**：`spdmcompl.py` 按配置文件逐项裁决，输出 5 级日志。

## 6. 设计决策与权衡

1. **include 守卫环**（packet.hpp ↔ 子头互指 + 宏守卫）：省掉 21 个头之间的依赖排序心智，代价是任何子头离开 packet.hpp 都编译不出——聚合器即命名空间。
2. **不依赖内存布局的序列化**：显式 `endianHostSpdmCopy` 逐字段端序拷贝，`#pragma pack(1)` 只在非 clang 下启用（`packet.hpp:100-102`，注释点名 LLVM bug 链接）——pack 是防御而非依赖，跨编译器安全。
3. **Transport/IO 双抽象**：传输封装与介质解耦，使 fuzzer 能插 FixtureIO 双队列、单测能插 MockTransport（transport_test.cpp），spdmd 能在内核/用户态 MCTP 间切换（meson 开关）。
4. **热路径模板 inline**：sendRequest/interpretResponse 留在 connection_inl.hpp，每个报文类型零虚函开销地复用收发框架；代价是连接实现横跨三文件。
5. **全异步 D-Bus 发现**：1611 行 discovery 全回调链 + 三级退避重试，换 openBMC 事件循环友好；也解释了为何 spdmd 能在端点热插拔下自愈（Recreate 逻辑 `spdmd.cpp:226-329`）。
6. **.symver 钉版本**：负向注入工具用 glibc 符号版本汇编技巧确保拦截不失效——测试基建比业务代码更"黑魔法"。
7. **工程诚实**：`connection.hpp:146` 直书 "TODO this has become extremely spaghetti"；时序类里两处 TODO 承认 RTT 硬编码与精度损失。读代码时把这些注释当路标而非噪音。
8. **测试金字塔**：伪随机编解码往返（快、确定性）→ 桩传输全流程（协议语义）→ Mock D-Bus（集成）→ 同进程对打 fuzzer（鲁棒性）→ 真机压力 CSV（性能/成功率）→ LD_PRELOAD 真流注入（负向）。

## 7. 已核实勘误（详版见仓级 README）

1. README 的构建/测试说明引用 `spdmcpp_emu/spdmcpp_requester_emu`（`README.md:21`/`:28`），该目标与目录在树中不存在，`emu` meson 选项是死开关（`meson_options.txt:9`）。
2. `connection.hpp:43-79` 的 FlowClass/QueryFlowClass 状态机整段在注释里，零引用；活状态机是 connection.cpp 事务方法链。
3. 报文结构头共 21 个（非 23/25），packet.hpp 的 packet 系 include 也是 21 条（总 #include 34 条）。
4. 压力数据实况：stress-test 47 个 JSON、stress-test-bash 32 张 CSV。
5. packetcorrupt 的 readme 称拦截 "read and write"（`readme.md:5`），实际包装的是 send/recv/connect/close。
6. MCTP TAG=1 与 TYPE=5 是两个维度常量，勿混（`mctp_support.hpp:42`/`:44`）。

## 8. 新人上手路线

**Day 1｜骨架**：README → `meson.build` → `common.hpp`（两个抽象接口精读）→ `context.hpp` → `packet.hpp` 加 GET_VERSION 请求/VERSION 响应一对（最小报文样本）。**Day 2｜协议核心**：connection.hpp 通读（先跳过 43-79 注释段）→ connection_inl.hpp 四个模板 → connection.cpp 按事务链顺序读 365→935 → 对照 `connection_test.cpp:501` 的 FullFlow 用例验证理解。**Day 3｜部署形态**：spdmd.cpp 主线 → discovery 异步链（491/710/897 三个信号入口）→ dbus_impl_responder 属性写入 → spdmd.service。**Day 4｜工具与质量**：spdmutil 六命令实操 → fuzzer 双队列机制 → pktcorrupt 环境变量玩法 → spdmcompl.py 配置一份。

改库必跑三件套：`connection_test`、`packet_basic_test`、`mctp_endpoint_discovery_test`（改发现逻辑时）。改报文结构时先跑 packet_basic_test 的伪随机往返——它是编码契约的守门员。需要真机联调时，spdmutil 单命令探测 + packetcorrupt 注入是最小复现工具对。
