# 精讲 01 · 连接状态机三件套：connection.hpp / connection_inl.hpp / connection.cpp

## 角色定位

libspdmcpp 的协议心脏：`ConnectionClass`（`libspdmcpp/headers_public/spdmcpp/connection.hpp:144`）面向一个 SPDM Responder 管理"握手→认证→取数"全生命周期，类文档直引 DSP0274_1.1.1 的 10.1/10.5/10.10 三大 flow（`connection.hpp:137`）。分工是声明/热路径/实现三段：hpp 928 行放类型契约，inl 184 行放每报文类型实例化的模板，cpp 1525 行（全仓最大单文件）放全部事务方法。spdmd、spdmutil、fuzzer 三个上层都只经它说话。

## 内部结构

先排雷：`connection.hpp:43` 起的 FlowClass/QueryFlowClass 状态机整段躺在 `/* */` 注释里（至 `:79`），零引用。真骨架：`TimingClass`（`connection.hpp:86`）实现规范第 9 节时序（RTT 6000ms、T1 WAR 值 24000ms、setCTExponent 微秒换毫秒）；`BufEnum`（`:489`）A/B/C/L 四缓冲槽；`SlotClass`（`:505`）存证书槽（Digest/Certificates/mbedtls RAII 数组/GotInfo 位图），槽数上限 8（`:155`）；RESPOND_IF_READY 轮询上限 4（`:906`）。inl 四模板：`sendRequest`（`connection_inl.hpp:27`）、`interpretResponse`（`:95`）、`setupResponseWait`（`:128`）、`sendRequestSetupResponse`（`:162`）。cpp 事务链：`tryGetVersion`（`libspdmcpp/connection.cpp:365`）→`tryGetCapabilities`（`:478`）→`tryNegotiateAlgorithms`（`:548`）→`tryGetDigest`（`:676`）→`tryGetCertificate`（`:917`，分块 `:743`）→`tryGetMeasurements`（`:935`）；证书解析/验证 `parseCertChain`（`:275`）/`verifyCertificateChain`（`:332`）；选版 `chooseVersion`（`:442`）。

## 外部连接

向下依赖 `TransportClass`/`IOClass` 两抽象（`common.hpp:126`/`:261`）——编码后调 encodePre/encodePost 裹传输层；版本池来自 `ContextClass`（`context.hpp:49`，1.0/1.1/1.2 倒序）。向上三消费方：spdmd 的 Responder 对象持有它取数（`spdmd/dbus_impl_responder.cpp:111` 读 getMessageVersion）、spdmutil 复用 interpretResponse（`spdmutil/spdm_tool.cpp:261`）、fuzzer 的 Requester 驱动全流程。

## 数据流

一次取数：上层调 refresh → `sendRequestSetupResponse` 三连 → Transport 编码进 MCTP socket → 响应到达成 `EventReceiveClass`（`event.hpp:59`）→ `handleEvent`（`connection.cpp:1403`）→ `handleRecv`（`:1174`）按消息码路由到 `handleRecv<T>` 特化（`:384`）→ 更新 SlotClass/度量缓存。异常三岔：解码失败返回错误；超时走 `retryTimeout`（`:1465`）；Responder 回 Busy 则轮询计数，超 4 次（`:1236` 对 `connection.hpp:906`）放弃复位。transcript 哈希随收发增量更新（fuzzer 对称实现 `spdm_fuzzer_responder.cpp:166` 可对照）。

## 设计决策

其一，模板 inline 而非虚函数——每报文类型编解码零间接开销，代价是实现横跨三文件。其二，状态推进用事务方法链而非显式状态机——被注释的 FlowClass 证明作者试过后者并放弃（`connection.hpp:146` 自嘲 spaghetti）；链式收益是每个 tryGet 可独立失败重入。其三，时序参数集中 TimingClass 并保留 TODO 痕迹——RTT 硬编码 6000ms 是 qemu 慢速环境的现实妥协。其四，四槽缓冲轮转避免同事务请求/响应互相踩踏。

## 新人提示

阅读顺序：hpp 类型 → inl 模板 → cpp 按事务链号读（365→935 一条线）。改报文结构必跑 `libspdmcpp/tests/packet_basic_test.cpp:324` 伪随机往返（编码契约守门员）；改流程跑 `connection_test.cpp:501` 起的 FullFlow 算法矩阵（桩 `ConnectionFixture` `:119`）。`-v` 日志会打出收发报文内容（`connection_inl.hpp:31`）；遇 RESPOND_IF_READY 死循环先查 `maxRespondIfReadyRetries`（4 次）是否被改。
