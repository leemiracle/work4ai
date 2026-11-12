# 03 · SPDM 安全纵深：从业务任务到 vendored libspdm 的五层切面

## 角色定位

SPDM（DMTF Security Protocol and Data Model）是设备身份认证协议：主机用它验证 GPU 板卡真伪（证书链+质询）、读取安全度量。OpenSMA 在这条链上扮演 **responder**（被验证方），实现纵贯五层：业务层（src/nv/spdm）→ PDK 适配（pdk-spdm-app-res-*）→ vendored libspdm（协议状态机）→ 密码学三后端（cryptlib_*）→ OS stub。理解每层接缝在哪，就能安全地改任何一层。

## 内部结构

**业务层**：`src/nv/spdm/task.cpp`（497 行）——`Task::make`（`src/nv/spdm/task.cpp:235`）分配栈并注册 entrypoint（Priority::Spdm，`:244`），初始化调 `src/nv/spdm/task.cpp:245`（spdm_init_all_measurement_cache）；任务循环 `src/nv/spdm/task.cpp:248`（Task::entrypoint）；度量缓存经 `src/nv/spdm/task.cpp:221`（get_measurement_cache）取数，成员存储在 `src/nv/spdm/task.h:110`，声明 `src/nv/spdm/task.h:92`；收发双通道：`spdm_tx`（`src/nv/spdm/task.cpp:257`）发送、事件位 UsbRxBit（`src/nv/spdm/task.cpp:285`）/I2cRxBit（`:289`）唤醒接收。`src/nv/spdm/spdm_cert_chain.cpp`（1577 行）构建/解析 DER 证书链：物理证书位置随当前启动槽位选择（`src/nv/spdm/spdm_cert_chain.cpp:121`，bootloader::Driver::current_boot_index()；`:342` 同款二处），CSR 解析带防御性长度校验（`src/nv/spdm/spdm_cert_chain.cpp:436` 起的 CsrHeader 边界检查，防越界读）。`src/nv/spdm/spdm_get_measurement.cpp`（956 行）应答 GET_MEASUREMENT，缓存类型 `src/nv/spdm/spdm_get_measurement.h:42`（MeasurementCacheT）。crypto_helper 封装签名/验签/密钥协商，密码学原语走队列（`src/nv/spdm/spdm_crypto_primitive_queue.cpp:38` is_valid_requester_core 校验请求核、`:86` set_request_metadata 投递元数据）。

**适配层**（`corepdk/modules/spdm/src/app/`）：pdk-spdm-app-res-* 钩子族——capabilities/certificate/digests/measurements/version/library/memory/algorithms 逐能力一文件；能力位经 `corepdk/modules/spdm/src/app/pdk-spdm-app-res-capabilities.h:203` 起的 `spdm_library_get_capabilites_*` 函数族暴露（:203-209：ct_exponent/cache/cert/chal/meas/meas_fresh）；入口 main.cpp/main.adb 双语言。

**libspdm 层**（vendored DMTF 参考实现，155 文件协议核心）：spdm_requester_lib 36 文件（内部头 `corepdk/modules/spdm/src/app/libspdm/include/internal/libspdm_requester_lib.h`，667 行）——本固件主要当 responder，requester 完整保留用于互操作测试与 encap 反向消息；spdm_responder_lib 38 文件（`corepdk/modules/spdm/src/app/libspdm/include/internal/libspdm_responder_lib.h` 1007 行；逐命令实现如 `libspdm_rsp_capabilities.c:164` 的 libspdm_get_response_capabilities、`libspdm_rsp_certificate.c:10` 的 libspdm_get_response_certificate）；common/secured_message 管会话密钥派生与加解密封装（`libspdm_secured_message_lib.h` 474 行）；transport 绑定四种（MCTP/PCIeDOE/TCP/Storage），本仓启用 MCTP。

## 外部连接

上接 MCTP（`src/nv/spdm/task.cpp:257` spdm_tx 走 `src/nv/mctp/driver.cpp:381` forward），下接密码学三后端与设备密钥库，横向连 bootloader（`src/nv/spdm/spdm_cert_chain.cpp:121` 证书槽位选择）与度量子系统（`src/nv/spdm/spdm_ap_measurement.cpp` AP 侧度量、ak/ik_generate_helper 密钥生成辅助）。

## 数据流

一次质询认证：主机 GET_VERSION/GET_CAPABILITIES 协商 → GET_DIGESTS/GET_CERTIFICATE 拉证书链（业务层从 flash 槽位组装，`src/nv/spdm/spdm_cert_chain.cpp:121`；vendored 侧应答入口 `libspdm_rsp_certificate.c:10`）→ CHALLENGE 质询 → 业务层经 crypto_helper 签名（走 cryptlib 后端，原语经 `src/nv/spdm/spdm_crypto_primitive_queue.cpp:38` 的核校验入队）→ secured_message 若启用会话则用会话密钥加密应答。度量查询 GET_MEASUREMENT（`src/nv/spdm/spdm_get_measurement.cpp`）命中 measurement cache（`src/nv/spdm/task.cpp:221`）。所有报文经 MCTP 封装。

## 设计决策

①**vendored 而非依赖管理**——libspdm 整树入仓（含 887 文件证书样例与 fuzzing 语料），保证固件供应链可复现、可审计，代价是仓体膨胀与升级摩擦；②**responder 为主但保留 requester**——互操作测试与 encap 场景需要，裁掉反而破坏测试矩阵；③**证书槽位绑定 boot index**——A/B 固件槽各配证书，防止"旧固件配新证书"错配（`src/nv/spdm/spdm_cert_chain.cpp:121` 的设计意图）；④**能力位函数族集中**——`pdk-spdm-app-res-capabilities.h:203` 一处看全设备暴露面。

## 新人提示

定位 SPDM 问题先分层：报文没到 → 查 MCTP（`src/nv/spdm/task.cpp:285`/`:289` 事件位）；应答错 → 查业务层（`src/nv/spdm/task.cpp:248` 循环内分发）；协议状态机问题 → vendored 层一般不动，先查适配层钩子是否正确翻译。改能力位在 `corepdk/modules/spdm/src/app/pdk-spdm-app-res-capabilities.h:203`。证书链问题优先打印 boot index 与槽位（`src/nv/spdm/spdm_cert_chain.cpp:121`）。红线：`os_stub/spdm_device_secret_lib_sample/spdm_device_secret_lib_internal.h`（159 行）是样例密钥库，生产构建必须换成真实现——样例私钥进产线等于裸奔。
