# 06 nvmsgconv + nvds_msgapi：消息转换三版本 schema 与协议适配器

## 一、角色定位

管线跑到这里，视频侧的故事结束了：帧看过了、目标检出了、轨迹连上了、ROI 判完了。最后一公里是把批元数据**变成一条条消息发给外部世界**（消息总线/云平台/后续业务系统）。DeepStream 把这件事拆成两个正交的插件 + 两层可替换库：

- **`gst-nvmsgconv`**（转换器）：NvDsMeta → 结构化 payload（JSON/protobuf）。它把转换算法做成可 dlopen 的 **msg2p 库**（`msg2p-lib-name`），仓库自带三个版本：原版 `nvmsgconv`、增强版 `nvmsgconv_mega`（3D 检测/分割/拥挤/LLM 字段）、`nvmsgconv_mega2d`（2D+3D 融合，2D 框带 embedding）。
- **`gst-nvmsgbroker`**（发送器）：payload → 网络。传输协议同样做成可 dlopen 的**协议适配器**（`proto-lib`），`src/utils/nvds_msgapi/` 下有 kafka/mqtt/amqp/azure(+redis) 四套开源实现，契约是 230 行的 `includes/nvds_msgapi.h`。

两插件通常相邻（conv 的 payload 经 user meta 随 buffer 流到 broker），但解耦彻底：换消息格式不动网络代码，换消息队列不动 schema——这是"最后一步永远在变"的工程现实的解法。

## 二、内部结构

**msg2p 库契约**（nvmsgconv.h，原版 nvmsgconv.cpp 实现）：

- 六个导出函数：`nvds_msg2p_ctx_create/destroy`（上下文）、`nvds_msg2p_generate/generate_multiple`（旧 API，吃 `NvDsEvent` 事件数组）、`nvds_msg2p_generate_new/generate_multiple_new`（新 API，吃 `NvDsMsg2pMetaInfo{frameMeta,objMeta,datamap}`——`datamap` 非空即走 DS3D 3D 数据分支）。
- `ctx_create`（nvmsgconv.cpp L35-96）按扩展名三路分派配置：`.csv`→传感器/场所静态表；`.yml/.yaml`→YAML；其他→key=value。full schema 必须给配置（L46 `g_return_val_if_fail`），minimal 可选。
- payload 类型四选一（L116-151 分派）：`DEEPSTREAM`（full JSON）、`MINIMAL`（精简 JSON）、`PROTOBUF`（schema.pb 序列化）、`CUSTOM`（返回占位串 `"CUSTOM Schema"`——给你自己换库的样板）。

**三版本 schema 的演进**（都以 `generate_event_message` 为核心，deepstream_schema.cpp 三版本字节级相同，差异全在 eventmsg_payload.cpp）：

- **原版**（1322 行）：消息 = uuid（`uuid_generate_random` 每消息唯一 id，eventmsg_payload.cpp L746-750）+ `mdsversion/@timestamp` + 五大对象：`place`（场所）/`sensor`（相机）/`analyticsModule`/`object`（目标框+速度+轨迹）/`event`（类型/计数）。还有 minimal（L873）与 protobuf（L1133）两条平行路径。
- **mega**（1891 行，为 3D/激光雷达场景扩容）：root 对象追加可选成员——`bbox3d`（`boxes_3d[10]` 八角点+scores/labels/instance_ids+`instance_feats` 嵌入向量，L743-768）、`segmentation`（掩码数组）、`fov`/`interactions`/`congestions` 数组、`llm` 对象（L1115-1118）——自动驾驶/空间分析的消息形态。配套 `lidar_schema.pb`。
- **mega2d**（1443 行）：在 mega 基础上把 2D 与 3D 统一——2D bbox 加 `confidence` 与 `embeddings`（ReID 向量直接进消息，diff 段 L621-637）、pose 支持 `pose_type==2`、confidence 从 int 改 double、并修复了 mega 里 `json_object_new` 在条件外创建的泄漏（jobject 移入 if 块内）。

**`gst-nvmsgconv` 插件**（gstnvmsgconv.cpp 1202 行）：

- 属性十一项：`config-file`/`msg2p-lib-name`/`payload-type`/`component-id`/`debug-payload-dir`/`multiple-payloads`/`msg2p-new-api`/`frame-interval`/`dummy-payload`/`embedding-filter` 等。
- msg2p 库 dlopen + 六符号 dlsym（L509-525）；不配 lib 则直连内置实现（L533）。
- 输入类型自识别：caps 是 `video/x-raw`→视频、含 `ds3d`→DS3D、否则音频（`gst_nvmsgconv_get_input_type`）；transform_ip 按此三分派（ds3d/sparse4d/video_audio 三路径）。
- **payload 生命周期挂 GstBuffer**：生成的 payload 包成 user meta 附加，`gst_nvmsgconv_free_meta`（release 回调）在 buffer 释放时归还；`numActivePayloads` 原子计数（free_meta 里递减）守着"最后一个 payload 释放且已 stop 才销毁 ctx/dlclose"——broker 异步发送未完成时插件不能先拆台。

**`gst-nvmsgbroker` 插件**（gstnvmsgbroker.cpp 846 行）：

- `proto-lib`（L185）dlopen（L415，`RTLD_LAZY`）+ dlsym `nvds_msgapi_connect/send/disconnect`（L424-430）；`async-send` 默认 TRUE（L236），再取 `nvds_msgapi_send_async` 与 `nvds_msgapi_do_work`（L431-436）。
- transform 里把 user meta 里的 payload 发出：异步走 `nvds_msgapi_send_async`（L560/L610，带回调），同步走 `nvds_msgapi_send`（L575/L625）。

**协议适配器**（`src/utils/nvds_msgapi/`，统一导出 nvds_msgapi 七函数：connect/send/send_async/subscribe/disconnect/do_work/connection_signature）：

- **kafka**（kafka_protocol_adaptor/，librdkafka）：连接串 `host;port[;topic]` 向后兼容（nvds_kafka_proto.cpp L282）；配置文件可指定 `partition-key-field` 从消息 JSON 里抽分区键（L44，同 key 进同分区保序）；还有个调试彩蛋——设 `NVDS_JSON_DUMP_FILE` 环境变量就不连 broker 直接落盘（L319）。
- **mqtt**（mqtt_protocol_adaptor/，mosquitto 库）：回调族 connect/publish/disconnect（nvds_mqtt_proto.cpp L448/L481/L430）；**只支持 MQTT v5 broker**——v3 连接直接报错并明说"Try connecting to an MQTT v5 broker"（L466-467）。
- **amqp**（amqp_protocol_adaptor/，rabbitmq-c：`amqp_tcp_socket.h/amqp_framing.h`，amqp_client.cpp L31-33）：单/双连接句柄（`conn`/`conn_consume` 分离，L88-89），消费队列向量。
- **azure**（azure_protocol_adaptor/，IoT Hub SDK，**device_client 与 module_client 两个变体**）：连接串三给法（完整串 L192 注释、或 config 文件、或 Edge 环境），`IoTHub_Init/Destroy` 管生命周期（L89-91/L323）。

## 三、外部连接

- **上游（msgconv）**：读 `NvDsBatchMeta`，事件源头是**应用在 probe 里挂的 `NvDsEventMsgMeta` 用户元数据**（deepstream-app 的 demo 逻辑：analytics 状态变化→`nvds_msgconv` 消费），frame/object 级还有第 5 篇 analytics 的 user meta；`NVDS_CUSTOM_MSG_SPARSE4D`（Sparse4D 3D 检测）走专用分支。
- **conv→broker**：payload 作为 user meta 随 buffer 流动，broker 在 transform 里取出发送——中间可以插 OSD 等任意元素。
- **broker 下游**：Kafka/MQTT/AMQP/Azure IoT Hub/Redis——即企业消息生态。订阅反向通道（`nvds_msgapi_subscribe`）供云下发指令。
- **应用侧**：自定义 msg2p 库（改 JSON 结构对接自家平台）与自定义适配器（如 HTTP/gRPC 直发）都只需按两个头文件实现符号，deepstream-app/config 里换一个 so 路径。

## 四、数据流

以 video/audio 主路径（`gst_nvmsgconv_transform_ip_video_audio`）为线：

1. **事件收集**：遍历 `batch_meta->batch_user_meta_list`——发现 `NVDS_CUSTOM_MSG_SPARSE4D` 即转专用分支；否则逐帧扫 `frame_user_meta_list` 找 `NvDsEventMsgMeta`。
2. **抽帧节流**：`msg2p-new-api` 下 `frameInterval` 生效——`frame_num % frameInterval != 0` 的帧跳过生成（每 N 帧一条消息，消息风暴的第一道闸）。
3. **payload 生成**：调 msg2p 库（新/旧 API、单/多 payload 由属性定）。库内部：full schema 先用配置文件把 sensor/place 的静态信息（id、坐标、描述）查出来，再从事件元数据取动态部分（bbox、class、置信度、轨迹、analytics 状态串），json-glib 组对象树→`json_to_string` 紧凑输出；protobuf 路径则 `SerializeToString`。
4. **挂载**：payload 包成 user meta（copy/release 函数对保证 tee 分支安全），附到 frame/batch meta，随 buffer 下行。`debug-payload-dir` 时同时按 RFC3339 时间戳落盘 txt。
5. **发送（broker）**：transform 里取 user meta payload → `nvds_msgapi_send_async(conn, topic, payload, cb)`（默认异步，回调里计数释放）→ 适配器内部（kafka 例：librdkafka producer 队列+后台 poll 线程；mqtt 例：mosquitto 异步 publish+`mosquitto_loop_start`）→ broker 网络。
6. **清理**：buffer 引用归零 → msgconv 的 release 回调 → payload 释放、计数递减；EOS 时 broker `nvds_msgapi_disconnect`。

## 五、设计决策

- **"转换"与"传输"分离，且各自可 dlopen**：消息格式（业务侧，天天改）与传输协议（运维侧，相对稳）的变化速率不同——两根扩展点让两类变化互不惊扰。自定义成本极低：两份头文件、若干符号、一个 so。
- **三版本 schema 并存而非替换**：原版是事实标准（大量下游系统按它解析）；mega/mega2d 面向 3D/空间智能新场景加字段。都以 root+place/sensor/object/event 骨架兼容——**加可选字段不破坏旧解析器**，这是 JSON schema 演进的保守正确姿势。mega2d 还顺手修了 mega 的内存泄漏（diff 可见 jobject 创建移入条件块），提示 mega→mega2d 不是纯增量而是带勘误的迭代。
- **payload 生命周期锚定 GstBuffer 引用计数**：msgconv 不维护发送队列，payload 的所有权随 user meta 走，buffer 死即 payload 死；配合原子计数确保异步发送在途时不销毁 ctx。比自建队列少一套状态机，也自然支持 tee 多分支（copy 回调各自深拷）。
- **UUID 做消息幂等键**：每条 full 消息 `uuid_generate_random`（eventmsg L746-750），下游可安全去重/重排——网络侧至少一次投递语义下的标配。
- **frame-interval 是吞吐阀门**：每帧发消息在 64 路×30fps 下就是 1920 msg/s 的洪水；把节流做成 conv 层属性（而非靠业务层抽帧）让消息量可独立于视频管线调。
- **Kafka 分区键从消息体提取**：`partition-key-field` 让"同一相机的消息进同一分区"——保序需求（事件顺序）由配置声明式解决，不用业务侧做 key 路由。
- **MQTT 只支持 v5**：v5 的共享订阅/原因码是 DeepStream 多实例消费的前提，宁可不兼容 v3 也不背双协议栈。
- **file-dump 后门**（kafka 的 `NVDS_JSON_DUMP_FILE`）：不连网就能验收消息格式——调试/CI 的贴心设计，也侧面说明消息层是排错重灾区。

## 六、新人提示

1. **先跑 `debug-payload-dir`**：`gst-nvmsgconv debug-payload-dir=/tmp/out` 每条消息落盘，jq 一看结构就懂——比读 schema 文档快十倍。kafka 适配器的 `NVDS_JSON_DUMP_FILE` 是免 broker 版同款。
2. **事件不是自动有的**：`NvDsEventMsgMeta` 要应用在 pad probe 里生成（参考 deepstream-app 的 `generate_event_meta` 回调，通常挂在 analytics 之后、只在状态变化时发）。光接 msgconv 不写 probe，你只会得到空帧消息。
3. **三版本选型**：下游是传统 VMS/平台→原版；有 3D 检测（Sparse4D 类）/分割/拥挤统计→mega；2D+3D 混合且要 ReID embedding 进消息→mega2d。切版本只改 `msg2p-lib-name`，但注意 mega2d 依赖新版 `NvDsEventMsgMeta` 结构（metadata 头文件同步演进）。
4. **配置文件三格式**：csv/yaml/key-value 按扩展名自动识别（nvmsgconv.cpp L51-60）；sensor/place 的 id 必须与 deepstream-app 配置里的 source id 对齐，否则消息里 place/sensor 全空——这是"消息里怎么没有地点"的头号原因。
5. **azure 双客户端别选错**：直连 IoT Hub 用 device_client，跑在 IoT Edge 容器里用 module_client（走 EdgeHub）；连接串给错变体报错很隐晦（L270-276 的格式检查才拦）。
6. **消息量三道闸全用上**：conv 的 `frame-interval`（帧级）+ probe 里的事件触发条件（状态变化才发）+ broker 侧异步发送（不阻塞管线）。同步 `async-send=0` 模式下 broker 卡顿会直接背压整条视频管线——一般只用于调试。
7. **自定义 msg2p 库从 CUSTOM 模板起步**：复制 nvmsgconv.cpp 的六函数骨架，`NVDS_PAYLOAD_CUSTOM` 分支就是留给你填的空位；记住所有 `g_malloc` 的 payload 由插件的 release 回调 `g_free`，返回裸指针即可，别自己管理释放。

> 注：本篇行号基于 DeepStream 9.1 源码（`src/utils/nvmsgconv*/`、`src/utils/nvds_msgapi/`、`src/gst-plugins/gst-nvmsgconv/`、`src/gst-plugins/gst-nvmsgbroker/`、`includes/nvds_msgapi.h`）核实；三版本差异结论由文件 diff 直接比对得出。redis 适配器（redis_protocol_adaptor/）为第五协议实现，本篇以任务指定的四协议为主线。
