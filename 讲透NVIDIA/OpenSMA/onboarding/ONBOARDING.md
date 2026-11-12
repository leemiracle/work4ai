# OpenSMA 深度导览（ONBOARDING）

> 基于知识图谱（7644 节点 / 9439 边 / 16 层 / 16 步 tour，fingerprints 3054 文件 @ commit 0c220c3a）与源码行号锚实证撰写。所有 `路径:行号` 均已在仓内核对。
> 仓库：NVIDIA/OpenSMA —— GPU 板卡上 MCXN 双核 MCU 的 SMA（System Management Architecture）诊断固件。

## 1. 这是什么项目：一张图先建立心智

OpenSMA 是跑在 NVIDIA GPU 板卡管理 MCU（NXP MCXN236/MCXN556 双核 Cortex-M33）上的固件，承担**带外管理**角色：主机（BMC/DCGM 等管理软件）通过 MCTP 总线发来查询，固件向上应答 NSM（NVIDIA 私有的 Node Scale Management 消息层），向下用 SPDM 完成设备身份认证、用 PLDM 完成固件更新，同时持续采样板卡传感器填充遥测缓存。一句话定位：**"GPU 的带外管家"——协议栈在 MCU，数据源在板卡，信任根在密码学**。

仓库四大块：`src/`（固件源码：协议栈+驱动+服务）、`corepdk/`（UBS 统一构建系统 + spdm/mctp-cpp/pldm-fd 三个模块）、`etc/`（构建配置与签名插件）、`libexec/`（工具与签名服务）。图谱把它切成 16 层：NSM 协议核心（L01）与 MCTP 传输（L02）是数据面主干；SPDM 应用层（L03）→pdk 适配（L04）→vendored libspdm（L05）→密码学三后端（L06）→OS stub（L07）构成纵深五层的信任面；证书数据海（L08）与测试/fuzzing（L09）是质量防线；Ada PLDM（L10）、硬件监控（L11）、系统服务（L12）、三平台（L13/L14）、工程设施（L15）、UBS/CI（L16）是落地支撑。

新人最常犯的路径直觉错误：NSM 协议不在 `src/nv/nsm/`（该目录不存在），而在 `src/nv/mctp/` 下——`nsm.cpp` 与 `driver.cpp` 同居一室（`src/nv/mctp/nsm.cpp` 3846 行全仓最大单文件，类声明 `src/nv/mctp/nsm.h:1391` class Nsm）；遥测缓存在 `src/nv/telemetry/`；SPDM 业务在 `src/nv/spdm/`。先记住这三个目录，图谱的边大多从这里辐射（命名空间总入口 `src/nv/nv.h`，62 行聚合版本与公共配置）。

## 2. 构建与交付：UBS 统一构建系统

README 交代环境：Ubuntu 24.04 + arm-gnu-toolchain-14.2.rel1 交叉编译器，pip 装 jsonschema 4.23.0 / ruamel.yaml 0.18.14 / spsdk 3.4.0，并 `ln -sf /usr/bin/make corepdk/ubs/bin/make` 把系统 make 挂进 UBS 私有 bin。构建入口是仓根 `mcu_build.sh`，参数矩阵（`mcu_build.sh:6-11`）：`PROJECT`（如 pg540）/`PLATFORM`（如 mcxn236）/`BOARD`（px9me/pd4a4/pd4b4 可选 FRDM-MCXN947 devkit 变体）/`MODE`（dev 等）/`SIGN_KEYSET`（S0 或 local/local-debug/local-prod）/`VERSION`/`STREAMBOOT`/`RUN_LOCAL`/`BUILD_ONLY`。

UBS 本体在 `corepdk/ubs/`（91 文件）双语言实现：`corepdk/ubs/src/ubs/ubs.py`（509 行 34 函数）做构建流程编排与目标派发——装饰器与日志族在 `ubs.py:28`（ubs_export）/`ubs.py:35`（ubs_info）/`ubs.py:45`（ubs_error）/`ubs.py:61`（ubs_expect_fatal）；makefile 阶段族（ubs-main.mk 等）定义各阶段。构建变体在 `etc/platforms`（mcxn556-core0/core1 双核各自镜像），签名插件在 `etc/plugins/sign-request.mk` 与 `etc/plugins/local-sign.mk`。最后一公里在 `libexec/tools/sma-mcxn556-signing-service/`：签名脚本 `src/scripts/sign.py`、密钥策略 `src/scripts/policy.json:29`（KeyPrefix MCXN556_S00_ECDSA_P384）与 `policy.json:30`（PqcKeyPrefix **MCXN556_S00_MLDSA_87**）——ECDSA P384 与 MLDSA-87 后量子双算法 keystore（配 `src/scripts/gen_pqc_isk_cert.py` 生成 PQC ISK 证书）。CI 是 `.gitlab-ci.yml:20`（PLATFORM mcxn556-both）与 `.gitlab-ci.yml:24`（mcxn556-core0）双工程矩阵。

## 3. NSM 协议核心：nsm.cpp 与 Type 处理器族

NSM 是 NVIDIA 在 MCTP 之上的管理消息层，报文先验 NVIDIA PCI vendor id 再分发（`src/nv/mctp/nsm.cpp:1474` 的 `Nsm::process`）。命令按 `nv_msg_type` 分文件实现（分发 switch 在 `src/nv/mctp/nsm.cpp:1496`）：

- **Type2（131 行）**：PCI 链路管理，如 `src/nv/mctp/nsm_type_2.cpp:32` 的 validatePcieLinkResetValue；
- **Type3（1572 行）**：遥测数值查询——电压/电流/功率/温度（`src/nv/mctp/nsm_type_3.cpp`）；
- **Type4（1048 行）**：事件与日志（`src/nv/mctp/nsm_type_4.cpp:42` 起引用 telemetry Cache 常量与 perf_mon CPU 利用率），含 debug token 通道 `src/nv/mctp/nsm_type4_debug_token.cpp`；
- **Type5（1843 行）**：PCIe 电容/固件信息——Type 族最大，`src/nv/mctp/nsm_type_5.cpp:47` 定义 ProtocolTypeMask（payload_type 低 6 位）；
- **TypeFF（438 行）**：NV 内部扩展，`src/nv/mctp/nsm_type_ff.cpp:37` 的 load_nv_internal_request 与 `src/nv/mctp/nsm_type_ff.cpp:81` 的 dispatch_nv_internal_get。

`nsm.cpp` 本体（3846 行）承担 Nsm 类公共逻辑：设备能力发现 `process_device_capability_discovery`（`src/nv/mctp/nsm.cpp:1284`，DCD 命令族 `src/nv/mctp/nsm.cpp:939` on_dcd_ping、`:1224` on_dcd_query_device_id、`:1238` on_dcd_get_device_capabilities_v2）、固件管理 `process_firmware`（`src/nv/mctp/nsm.cpp:1397`；槽位判定 `:354` get_active_slot/`:366` get_inactive_slot、冗余策略 `:217`、后台拷贝探测 `:59`、OTP 撤销资格 `:81`）、事件订阅 `on_dcd_set_event_subscription`（`src/nv/mctp/nsm.cpp:1111`）与版本串生成 `generate_fw_version`（`src/nv/mctp/nsm.cpp:340`）。公共结构在 `src/nv/mctp/nsm_common.h:26`（WriteProtectionGpioConfig）与 `src/nv/mctp/nsm_msg_bitmask.h:26-27`（支持命令/事件数常量）；事件上报在 `src/nv/mctp/nsm_event.cpp:34`（PrepareEventMessage）与 `src/nv/mctp/nsm_event.cpp:112`（ProcessType0Event）。

## 4. 遥测数据面：缓存、SMB 组装与弱符号钩子

Type3 查询**不直接碰总线**——数据流是：传感器驱动后台轮询 → 写入缓存 → NSM 查询命中缓存即刻应答。缓存本体 `src/nv/telemetry/cache.h:27`（class Cache，单例 `src/nv/telemetry/cache.cpp:29` 的 Cache::inst），以 TelemId 枚举为索引、容量即 `src/nv/telemetry/cache.h:36` 的 CacheSize=TelemId::MaxItem，提供 set_cache/get_cache（`src/nv/telemetry/cache.cpp:46`/`:63`）、错误项管理（`src/nv/telemetry/cache.cpp:83` set_error/`:91` clear_error）与 `src/nv/telemetry/cache.cpp:99` 的 refresh 维护告警项与阈值。`src/nv/telemetry/smb_telemetry.cpp:35`（weak get_end_address）从缓存填充遥测记录并组装 SMBus 侧 NSM 响应；Type3 侧把功率传感器映射到 TelemId（`src/nv/mctp/nsm_type_3.cpp:54` 的 cachePowerSensorsMap：Gpu1Power/Gpu2Power/ModulePower）。

功率平滑是"弱符号钩子"模式的教科书案例：`src/nv/mctp/nsm_pwr_smoothing_handlers_weak.cpp:43` 用 `__attribute__((weak))` 提供"功能不存在"的默认实现（文件头注释 `src/nv/mctp/nsm_pwr_smoothing_handlers_weak.cpp:23` 明说链接期被 strong 覆盖）；真实现是 `src/nv/soc_pwr_smoothing/nsm_pwr_smoothing_handlers.cpp`（452 行，strong 符号，覆盖 AC ramp rate/SoC 热刹车/机架平滑参数；域逻辑在 `src/nv/soc_pwr_smoothing/soc_pwr_smoothing.cpp:44` 起的命名空间）。**注意两个文件分居 src/nv/mctp 与 src/nv/soc_pwr_smoothing 两个目录**，grep 时必须双目录都看。同模式还有 `src/nv/flash/pds_pwr_smoothing_defaults_weak.cpp` 与 `src/nv/soc_pwr_smoothing/pds_pwr_smoothing_defaults.cpp` 的 PDS 默认值对。

## 5. MCTP 传输层：三协议共用的信封

NSM/SPDM/PLDM 消息都走 MCTP（DMTF 管理组件传输协议）总线。`src/nv/mctp/driver.cpp`（1096 行）是传输引擎：构造函数 `src/nv/mctp/driver.cpp:64`（路由队列 ipc::Queue::make(RoutingTable) 在 `:73`、validator 挂 control.router() 在 `:67`）、EID 端点管理（`src/nv/mctp/driver.cpp:256` on_get_eid_probe_response 校验 `:260` 的 dst_eid==0 广播探测、`src/nv/mctp/driver.cpp:456` update_eid 学习端点）、消息接收与分片重组 `src/nv/mctp/driver.cpp:269`（on_receive）、转发 `src/nv/mctp/driver.cpp:381`（forward）与 `src/nv/mctp/driver.cpp:443`（on_forward_message），主循环是 `src/nv/mctp/driver.cpp:141` 的 `[[noreturn]] Driver::main`。协议任务循环挂在 `src/nv/mctp/task.cpp:32`（Task::make）与 `src/nv/mctp/task.cpp:75`（Task::entrypoint）；层间接口 `src/nv/mctp/interface.h:23` 起定义 Packet 与消息类型标签；`src/nv/mctp/enums.h:27`（using MsgType）起 741 行别名表把 pdk::mctp 枚举逐项 using 进 nv::mctp 命名空间。

PDK 侧包装在 `corepdk/modules/mctp-cpp/src/app/`：`pdk-mctp-app-composer.h`/`.cpp` 组装 tx 报文头与缓冲布局、`pdk-mctp-app-router.cpp` 路由、`pdk-mctp-app-packet.cpp` 报文、`pdk-mctp-app-vendor.h` 厂商消息、control 命令分发——模块在 modules 与 platforms/mcxn236 各有一份平台特化。USB 侧还有备份通道：`src/nv/usb/mctp_router.cpp:98`（update_routing_table）与 `src/nv/usb/usb_mctp_header.h`，经 `src/nv/usb/hid_smb.cpp:44`（i2c_manual_nack）HID-SMBus 桥，任务循环在 `src/nv/usb/task.cpp:48`/`:59`。

## 6. SPDM 安全纵深五层：从业务到密码学

1. **业务层**（`src/nv/spdm/`）：`task.cpp`（497 行）任务循环 `src/nv/spdm/task.cpp:248`（Task::entrypoint），构造 `src/nv/spdm/task.cpp:235`（Task::make）注册 Priority::Spdm 任务并调 `src/nv/spdm/task.cpp:245` 的 spdm_init_all_measurement_cache；度量缓存经 `src/nv/spdm/task.h:92`（get_measurement_cache 声明）/`src/nv/spdm/task.cpp:221` 取数，存储在 `src/nv/spdm/task.h:110` 的成员；收发双通道 `src/nv/spdm/task.cpp:257`（spdm_tx）、`:285`（UsbRxBit）/`:289`（I2cRxBit）。`spdm_cert_chain.cpp`（1577 行）构建解析 DER 证书链：物理证书位置随启动槽位选择（`src/nv/spdm/spdm_cert_chain.cpp:121`，bootloader::Driver::current_boot_index()）、CSR 解析防御 `src/nv/spdm/spdm_cert_chain.cpp:436` 起的 CsrHeader 边界检查。`spdm_get_measurement.cpp`（956 行）应答 GET_MEASUREMENT，缓存类型定义在 `src/nv/spdm/spdm_get_measurement.h:42`（MeasurementCacheT）。crypto_helper 封装签名/验签/密钥协商，密码学原语走 `src/nv/spdm/spdm_crypto_primitive_queue.cpp:38`（is_valid_requester_core）起的原语队列（多核互斥投递，`:86` set_request_metadata）。
2. **PDK 适配层**（`corepdk/modules/spdm/src/app/`）：pdk-spdm-app-res-\* 钩子族（algorithms/capabilities/certificate/digests/measurements/version/library/memory）把 libspdm 回调翻译到平台实现；能力位经 `corepdk/modules/spdm/src/app/pdk-spdm-app-res-capabilities.h:203` 起的 `spdm_library_get_capabilites_*` 函数族暴露（:203-209 六类：ct_exponent/cache/cert/chal/meas/meas_fresh）；crypto/ 子目录提供 AEAD/DH/hash 平台实现；入口 main.cpp/main.adb 双语言。
3. **libspdm 协议库**（vendored，155 文件协议核心）：spdm_requester_lib 36 文件（内部头 `corepdk/modules/spdm/src/app/libspdm/include/internal/libspdm_requester_lib.h`，667 行）+ spdm_responder_lib 38 文件（`libspdm_responder_lib.h` 1007 行；逐命令实现如 `libspdm_rsp_capabilities.c:164` 的 libspdm_get_response_capabilities、`libspdm_rsp_certificate.c:10` 的 libspdm_get_response_certificate）+ common/secured_message 会话密钥与加解密（`libspdm_secured_message_lib.h` 474 行）+ 四种 transport 绑定（MCTP/PCIeDOE/TCP/Storage）。
4. **密码学层**：spdm_crypt_lib（含 FIPS 自测族）定义协议原语；`os_stub/` 下三套可切换后端，同名文件对照是理解契约的捷径——`os_stub/cryptlib_mbedtls/cipher/aead_aes_gcm.c`（187 行）、`os_stub/cryptlib_openssl/cipher/aead_aes_gcm.c`（267 行）、`os_stub/cryptlib_null/cipher/aead_aes_gcm.c`（88 行），编译期择一链接。
5. **OS stub 层**：memlib/malloclib/debuglib/rnglib/platform_lib；设备密钥样例库 `os_stub/spdm_device_secret_lib_sample/spdm_device_secret_lib_internal.h`（159 行）——**生产构建必须替换为真实现**（安全审计第一检查点）；openssl 后端需 `os_stub/openssllib/include/crt_support.h`（364 行）补嵌入式 CRT。

## 7. 证书数据海与质量防线

`corepdk/modules/spdm/src/app/libspdm/unit_test/sample_key/` 是全仓最大单一目录：**887 个文件**的证书/私钥/CSR 二进制动物园——ecp256/384/521、ed25519/ed448、sm2（国密）、rsa2048~4096、rsa3072_Expiration 过期链、test_web_cert/test_csr、long_chains 319 个超长链场景；`auto_gen_cert.sh` + `raw_data_key_gen.py` + `openssl.cnf` 是再生成工具链。这解释了图谱 1184 个"测试数据"标签节点的来源。

测试与 fuzzing：test_spdm_requester 48 文件、test_spdm_responder 40 文件逐命令断言（公共头 `unit_test/spdm_unit_test_common/spdm_unit_test.h` 180 行）；test_size 用 dummy/intrinsic 桩测最小镜像尺寸（安全裁剪证据）；fuzzing 234 文件带 AFL/AFL++/LibFuzzer/oss-fuzz 四套驱动与 seeds 语料。OpenSMA 自身测试框架在 `src/nv/ut/unittest.h:194`（TEST 宏）/`:197`（TEST_F），配 reporter/coverage；工程级自测走 testrunner 与 UBS selftests 142 文件。两侧合看才是完整测试地图。

## 8. Ada PLDM、三平台与上线路线

**PLDM 固件更新**（`corepdk/modules/pldm-fd/`，Ada）：命令应答核心 `src/fwupdate/pdk-pldm-fwupdate-cmd.adb`（2001 行）——`pdk-pldm-fwupdate-cmd.adb:225` 的 Pldmfw_Context_Init 初始化上下文（:235-296 的 Max_Transfer_Size/Last_Transfer_Size/Transfer_Fail_CC/Verify_Fail_CC 字段）、`:136` 的 Pldmfw_Generate_Update_Report、`:157` 的 Pldmfw_Is_Rate_Limit_Reached 限速判定；状态机独立在 `src/fwupdate/pdk-pldm-fwupdate-state.adb:29`（Pldmfw_Change_State）+ `:62`（Idle）/`:119`（Lc）/`:172`（Rdy_Xfer）三态 handler。发现命令 `src/base/pdk-pldm-base-cmd.adb:38`（Process_Base_Commands，GetTID/GetPLDMVersion；`:170` Fill_Resp_Header/`:185` Respond_Error），模块入口 `corepdk/modules/pldm-fd/src/main.adb:20`（procedure Main）。配套 `src/nv/fw_parser/fw_parser_mcu.h:26`（MCU 镜像解析命名空间）与 fw_parser_ap.cpp（AP 镜像）、`src/nv/pldm/` C++ 客户端、libexec 打包器构成带外固件更新链。

**三平台**：mcxn556（135 文件；`src/sys/mcxn556/sys/bootloader/bootloader.cpp:47` run_on_index 镜像选择、`:62` use_boot_rom、`:110` hw_init、`:119` no_stack_protector 的 set_stack_cookie；接口 `src/sys/mcxn556/sys/bootloader/bootloader.h:28` class Driver）、mcxn236（104 文件，量产主力）、x86（95 文件仿真：`src/sys/x86/sys/common/error-inject.cpp` 故障注入 + console 直写 stdout，配 `src/overrides/` libc/thread 覆盖）。硬件监控族是遥测物理源头：温度传感器 `src/nv/i2c/emc1812.cpp:22`（Emc1812 构造，port+address+TelemId 三参即接入缓存体系）；热插拔功率传感器 `src/nv/i2c/powersensor/device_manager.cpp:91`（identify_power_sensors 识别 LM5066I/MP5926）、`:210`（read_mfr_info）、`:302`（add_hsc_device）；电压/漏电 `src/nv/volt_mon/leak_detect.h` 与 `src/nv/volt_mon/leak_detect_pds_seed.h`（PDS seed）；热插拔状态机 `src/nv/ahs/ahs.cpp:47`-`:444`。跨核服务由 `src/nv/ipc/` 支撑（`src/nv/ipc/event.h:35` class Event、`src/nv/ipc/queue.h:35` class Queue、`src/nv/ipc/supervisor.h:37` class Supervisor、task.h 176 行任务基类），flash 门面 `src/nv/flash/flash.h`（130 行）与 `src/nv/flash/common.h:27` 起的跨核请求布局；日志 `src/nv/logger/log.h:35` class Logger；通用工具 `src/nv/common/utils.h`（222 行）。

**新人路线**（图谱 16 步 tour 顺序）：step01 全景与构建 → step02-03 NSM+遥测（本导览 §3/§4）→ step04 MCTP（§5）→ step05-09 SPDM 五层纵深（§6）→ step10-11 证书与测试（§7）→ step12-13 PLDM+UBS（§8）→ step14-16 三平台/硬件监控/端到端。最后把端到端线索背下来：传感器采样 → 遥测缓存 → MCTP 请求分片重组 → NSM Type3 命中缓存组包 → 响应回主机，旁路 SPDM 先认证——这就是 SMA 诊断的完整生命周期。
