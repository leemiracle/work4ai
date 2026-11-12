# 09 · DisplayPort 库：EventSink 事件体系与 MST 协议栈的完整实现

> 仓库 @ 615.71.09。本篇覆盖 `src/common/displayport/`（inc/ 45 头 + src/ 34 个 .cpp，合计约 45,900 行 C++）。

## 一、角色定位：跨 OS 的 DP 协议栈，NVKMS 的"协议大脑"

这是仓内最大的 C++ 组件，一个与 OS、与硬件都解耦的 DisplayPort 协议库。它实现 DP 标准里所有"软件侧"内容：AUX 通道读写与重试（DPCD 寄存器空间）、链路训练（link training）、MST 拓扑发现与带宽管理（侧带消息 SIDEBOARD_MSG）、HDCP 1.x/2.x 能力协商、DSC（显示流压缩）能力判定、EDID/DisplayID 2.x 解析、以及一整套针对残血面板的 workaround 数据库。开源构建中它的唯一编译消费者是 nvidia-modeset（`src/nvidia-modeset/srcs.mk:98-105` 起的 34 条 `SRCS_CXX += ../common/displayport/src/*.cpp`），经 `src/nvidia-modeset/src/dp/nvdp-*` 适配层接入（第 10 篇详述）。GSP 固件内部的 DCP 显示驱动有同源实现，但那是固件二进制内的事，不在开源构建链上。

库用**五个纯虚基类**定义平台契约，全部通过构造注入：

| 抽象 | 头文件 | 职责 |
|---|---|---|
| `MainLink` | dp_mainlink.h | 链路训练执行、测试图案、SOR 索引、regkey 查询 |
| `AuxBus` | dp_auxbus.h:37 | AUX 原生/I2C 读写，四态返回（success/defer/nack/unSupported，dp_auxbus.h:41-46） |
| `Timer` | dp_timer.h | 定时回调（:61 `TimerCallback::expired(context)`） |
| `EvoInterface` | dp_evoadapter.h:50 | 平台后门：`rmControl0073/rmControl5070` 直发 RM 控制命令 |
| `Connector::EventSink` | dp_connector.h:417 | 库→宿主的全部上行事件 |

这种"全虚接口"风格使同一份协议代码可跑在 NVKMS（内核态）与其他 OS 的驱动里，宿主差异被压缩到五个适配类。

## 二、内部结构：ConnectorImpl 枢纽与双协议代实现

**枢纽是 `ConnectorImpl`**（声明于 `inc/dp_connectorimpl.h:94`），一个四重继承的巨型结构：

```cpp
struct ConnectorImpl : public Connector,
                       DiscoveryManager::DiscoveryManagerEventSink,
                       Timer::TimerCallback,
                       MessageManager::MessageReceiver::MessageReceiverEventSink
```

它同时"扮演"连接器门面、拓扑发现监听者、定时器回调对象、侧带消息接收者四个角色——DP 库所有异步事件最终汇入这一个类。构造函数（dp_connectorimpl.h:465）吃四个注入（MainLink/AuxBus/Timer/EventSink），实现文件 `dp_connectorimpl.cpp` 9891 行是全库最大源文件。

**协议代际双实现**是本库的骨架性分叉：`dp_connectorimpl.cpp`（9891 行）实现 DP 1.x–1.4a 语义（RBR/HBR/HBR2/HBR3 链路速率，MST 基于 8.1 Gbps 半双工侧带）；`dp_connectorimpl2x.cpp`（2279 行）实现 DP 2.x（头文件注释明言"DP connector implementation for DP2.x"），配套 `dp_evoadapter2x.cpp`（1500 行）与 `dp_configcaps2x.cpp`（971 行），覆盖 UHBR 10/13.5/20（即 10/13.5/20 Gbps/lane，128b/132b 编码）。共享代码（EDID、消息编解码、水位管理）不复制，两代实现只重写速率相关的训练与能力路径。

**消息层**是 MST 的核心：每个 DP 标准侧带请求/回复都是一个 `MessageManager::Message` 子类——`LinkAddressMessage`（拓扑枚举）、`EnumPathResMessage`（路径资源查询）、`AllocatePayloadMessage`（带宽分配）、`ClearPayloadIdTableMessage`（流清场）、`ConnStatusNotifyMessage`（连接状态通知，作为 MessageReceiver 挂常驻监听）。编解码由 dp_messagecodings.cpp（795 行）按 DP 规范位布局手工实现，dp_bitstream（BitStreamReader/Writer）提供位级原语。

**Device 抽象**（dp_connector.h:212）有 100+ 个纯虚方法，语义密度极高，几个非标准概念值得单独记忆：`isZombie()`（:224）——"head 已附着但设备实际失联"的 MST 半死态；`isCableOk()`（:225）——HPD 在但 AUX 不通的线缆坏态；`isRedundant()`/`isLoop()`——MST 拓扑环路与冗余路径检测。这些状态是 DP 多流拓扑运维经验的结晶，普通"连上/断开"二值模型覆盖不了。

**EventSink 体系**（dp_connector.h:417）：44 个 `virtual void`、其中 43 个纯虚、1 个（notifyHDCPEnabled）带空默认实现。分四族：设备拓扑事件（newDevice/lostDevice，注意头注释明言"Device object ceases to exist after this call"——回调返回后对象即销毁，宿主不得缓存裸指针）、协商通知（notifyMustDisconnect/bandwidthChangeNotification）、HDCP 生命周期（notifyHDCPCapDone/notifyHDCPEnabled）、脉冲通知（notifyLongPulse/notifyShortPulse，对应 DP HPD 长短脉冲语义）与 modeset 事务钩子（notifyAttachEnd/notifyDetachBegin/End、dpPreModeset/dpPostModeset）。

## 三、外部连接：一条 AUX 通路 + 一个 RM 后门

对下（硬件侧），库只见 `AuxBus` 抽象。AUX 四态语义（dp_auxbus.h:41-46）直接映射 DP 规范：`defer` 是"Sink 忙，稍后重试"（包装层 AuxRetry 负责退避），`nack` 是明确拒绝，`unSupported` 是地址/长度不合法。`CreateAuxLogger`（dp_auxbus.h:86）可包一层全量打印的装饰器用于调试。

对旁路（平台侧），`EvoInterface`（dp_evoadapter.h:50）是显式"后门"：`rmControl0073/rmControl5070` 两个虚方法让库直接向 RM 的显示控制对象（NV0073 display 根 / NV5070 nvdisplay）发控制命令——链路训练要的 SOR/链路参数设置走这条路；`monitorDenylistInfo` 让宿主提供显示器黑名单数据；`getMaxLinkConfigFromUefi` 处理 UEFI 阶段已训练链路的继承（POST 期间 GOP 训练的链路不能被内核驱动无脑重训，否则屏幕会闪）。

对上（宿主侧），EventSink 是唯一出口；库从不阻塞等待宿主，异步结果一律转事件。`enableLinkHandsOff`/`releaseLinkHandsOff`（dp_connectorimpl.cpp:2813 起）是交接协议：宿主做自己的 modeset 前先"接管"链路，完成后归还。

## 四、数据流：一次 MST 显示器热插拔的完整旅程

1. **长脉冲**（HPD assert > 2ms）：宿主 `notifyLongPulse(true)` → 库启动 `DiscoveryManager`（dp_discovery.cpp，1021 行）发 `LinkAddressMessage`，从根设备开始递归枚举每级分支/端点（每设备经 DID2ReadMultistream 读 DisplayID）。
2. **设备注册**：枚举出视频汇聚点后库回调 `sink->newDevice(dev)`；宿主收到后拉 `getEDID()`（EDID 读取由 EdidReadMultistream 异步完成，dp_edid.cpp 解析与校验和验证）、查 HDCP 能力（DeviceHDCPDetection 状态机异步探测 1.x/2.x 链）。
3. **带宽分配**：宿主决定启用流后，库经 `beginCompoundQuery` 批量核算全链路各跳的可用时隙（watermark 体系，dp_watermark.cpp 881 行维护"每跳剩余带宽"水位表），再发 `AllocatePayloadMessage` 沿路径预留。
4. **链路训练**：`train()`（MainLink 接口）驱动 PHY 侧 clock/lanes 对齐；失败进 `dp_wardatabase.cpp`（782 行）的 workaround 路径——按 EDID 厂商/产品 ID 与 OUI 匹配已知劣质面板降速率重试，重试上限 `WAR_MAX_REASSESS_ATTEMPT/RETRAIN_ATTEMPT` 均为 3（dp_wardatabase.h:38-39）。
5. **稳态监控**：短脉冲（<2ms）触发 `notifyShortPulse` → `ConnectorImpl::detectSinkCountChange()`（dp_connectorimpl.cpp:8836）查 sink 计数，拓扑变化则重新枚举；设备拔除经 `lostDevice`（:3110/:3256 两处调用点）上报并销毁对象。

## 五、设计决策

1. **C++ 虚接口全抽象**：在内核态用 C++ 本身就是选择——DP 协议的设备树/消息对象模型用 C 模拟会非常痛苦。代价是内核 C++ 子集约束（无异常/无 RTTI/无动态分配随意用），库内可见大量手写 List（dp_list）与 Object 基类引用计数。
2. **事件单向化**：库到宿主只有 EventSink 一个通道且对象生命周期规则苛刻（lostDevice 后指针失效），杜绝宿主侧悬垂指针类 bug 的常见来源。
3. **zombie/cableOk 等中间态建模**：拒绝把"连接"布尔化。MST 大拓扑里"显示流还在但设备已消失"（zombie）必须显式建模才能做正确的恢复——直接断流会黑屏，保持假活才能等设备回来或有序迁移。
4. **workaround 数据库集中化**：782 行 wardatabase 把市面上问题面板的 EDID/OUI 特征集中一处，而非散布在训练代码里。这类数据库只能随驱动版本迭代累积，是显示栈的"灰产日志"。
5. **双代实现共存不抽象**：DP2.x 没有抽象成 1.x 的策略插件，而是平行 ConnectorImpl2x。理由很实际：128b/132b 编码下训练状态机差异太大，强行统一会把两个都变慢。
6. **regkey 热开关贯穿**：EvoInterface::getRegkeyValue 让每个 workaround 都可被注册表/模块参数关闭——显示兼容性问题的一线处置永远是"关掉那个 workaround"。

## 六、新人提示

- **读码顺序**：dp_connector.h（Device/Group/Connector/EventSink 三接口一夜读完）→ dp_auxbus.h + dp_timer.h（平台契约）→ dp_connectorimpl.h:94 的 ConnectorImpl 成员表 → 按第四节旅程逐段读 dp_connectorimpl.cpp。
- **别在内核语境惊讶 C++**：这是 nvidia-modeset.ko 里唯一的 C++ 区，编译单元在 srcs.mk 的 `SRCS_CXX` 段；nvkms 主体是 C，两语言在模块内共存。
- 调 MST 问题先开 AuxLogger（dp_auxbus.h:86），AUX trace 里 defer 刷屏通常是面板固件慢，nack 才是协议错误。
- `isMultistream()` 与"设备在 MST 拓扑里"不是一回事：分支器下挂的 SST 显示器也在拓扑里但自身非多流。判定看 Device 语义而非父节点。
- EDID 有三层：getRawEDID（原样字节）、getEDID（库修正后）、isFallbackEdid（读取失败时的兜底假 EDID）。面板兼容性问题先确认拿到的是哪层。
- 与 RM 侧的边界：一切 SOR/链路硬件态经 EvoInterface 的 rmControl0073/5070 落到 RM；本库不直接碰显示寄存器。

---

**本篇甄别备注**：任务描述称 EventSink 体系"33 类"，源码实测 dp_connector.h 内类声明 5 个（Object 族外：Device/Group/Connector/EventSink/EvoInterface 前向），EventSink 方法 44 个（43 纯虚）；全库 inc/ 头文件去重类声明 93 个（含消息类/辅助类），"33 类"未能对应任何单一计数口径，文中按源码实测数字表述。
