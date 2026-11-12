# 02 · gRPC API 协议：三 proto 与网关

## 1. 角色定位

`api/` 三 proto 定义 JAX↔vLLM 的全部线上契约，`controller/gateway.py` 是契约的参考实现——单进程 gRPC server 挂两个 servicer。controller.proto 是控制面（10 个 RPC，图谱 schema 节点 fanOut=44、全仓被引最多）；message_broker.proto 是极简 pub/sub 数据面；param_mapping.proto 是参数映射 DSL（详见第 3 篇）。三者统一 proto2（controller.proto:17 等）。网关把控制面 RPC 翻译成 topic 发布再由 broker 推给订阅者。

## 2. 内部结构（行号锚）

- **controller.proto**：KV 三对消息（:23-37）；GetNcclId 同步 RPC 返回 `repeated int32 ids`（:39-42）；HandshakeRequest（:57-64）含 response_topic/jax_parallelism/model_name/param_mapping_path；InferenceRequest（:101-110）：prompts=6、response_topic=4、config=5、batch_id=7、streaming=8；RolloutResult（:126-134）以 batch_id/prompt_index/rollout_index 三元组定位流式回执；服务 10 个 RPC（:146-166）。
- **message_broker.proto**：Topic/Message（:21-27），Message.payload 是 google.protobuf.Any；服务仅 SubscriptionStream（server-streaming）+ Publish（:45-48）。
- **gateway.py**：MessageQueues（:40-92）纯内存 pub/sub——subscribe 给每个订阅者建 Queue（:64）、persistent 消息回放给后来者（:65-67）、publish 逐队列阻塞 put（:91-92）。ControllerServicer（:95-163）：KV 按 metadata session-id 命名空间化（:102-105）；GetNcclId 直调 cupy nccl.get_unique_id()（:123-125）；AsyncHandshake 是唯一 persistent=True 的发布（:129）；Shutdown 用 context.add_callback 延迟停服（:149-152）。MessageBrokerServicer（:165-188）：SubscriptionStream 每 1 秒轮询队列保活（:174-176）、非 broker.Message 载荷 Pack 进 Any（:179-182）。run_gateway（:191-201）：10 worker 线程池 + GATEWAY_PORT（默认 50051）。
- **topic 常量**：controller/utils.py:24-30 定义 7 个默认 topic，:33-41 另有 SC_* 单控制器族。

## 3. 外部连接（图谱边佐证）

图谱中 gateway.py 是神经中枢（fanIn=12/fanOut=9），import 边连双 pb2(_grpc) 与 controller.utils；controller/utils.py（fanIn=12）被 gateway、rollout_client、session 与两个示例 controller 消费，是消息路由命名的单一事实源。构建期 pep517_backend.py 与 setup.py:23-35 把 proto 编译成 pb2，pyproject.toml:1-6 钉死 grpcio-tools 与 protobuf 版本。rollout_client.py（fanOut=17）是最大消费者：握手回执 publish 回 response_topic（:319-325），推理按 streaming 分流（:337-349），经 client_base.py:55-59 的 _publish_result 发出。

## 4. 数据流

握手（异步）：JAX leader 发 AsyncHandshake → gateway 发布到 handshake topic（persistent，gateway.py:127-130）→ vLLM RolloutClient Unpack 出请求、算出 mapping_specs → _publish_result 把 HandshakeResponse 发往请求指定的 response_topic → JAX 在 SubscriptionStream 上收到。AsyncInference 同构：requester 填好 response_topic（vllm_rollout_requester.py:181）→ gateway 转发到 inference_requests topic（gateway.py:142-145）→ vLLM 生成后 publish 结果回同一 topic。KV 用作服务发现：JAX controller 把 inference_response_topic 写入 KV（decoupled_synchronous/jax_controller.py:143-146），rollout 进程 KVGet 轮询发现（vllm_rollout_requester.py:119）。

## 5. 设计决策

- **控制面 RPC + 数据面 pub/sub 分离**：请求-响应语义（GetNcclId/KV/Shutdown）走直接 RPC；解耦/一对多（handshake/inference）走 topic。
- **Any 打包而非强类型消息**：Message.payload 是 Any（message_broker.proto:26），broker 无需知道载荷类型即可转发；代价是收端要自己 Unpack 对的类型。
- **persistent 只给 handshake**：晚启动的 vLLM 也能补收错过的握手请求（gateway.py:129）；其余 topic 不持久，订阅必须先于发布。
- **proto2 而非 proto3**：保留 optional 显式存在性语义（如 KVGetResponse.found），代价是删字段必须手工 reserved。
- **构建期编译 proto**：pep517_backend.py 在全部 5 个 build 钩子里先跑 build_package_protos(strict_mode=True)（:4-6、:9-31），安装即自动生成 pb2。

## 6. 新人提示（坑/勘误）

- **pb2 是生成物、不可直接 import**：源码树 api/ 只有 .proto（MANIFEST.in 只打包 proto），未构建的 checkout 里 import pb2 必然 ImportError，必须先 pip install . 或构建。
- **reserved 字段号是演进化石**：InferenceRequest `reserved 1, 2, 3`（controller.proto:102）说明现有字段前曾有 3 个被删字段；HandshakeRequest reserved 2 且留有 jax_n_devices 注释（:59-61）、HandshakeResponse reserved 2（:67）、JaxParallelism 注释掉的 pp=2（:51）；CreateTransportRequest 的 config_json 用 2 号、1 号空缺且未 reserved（:44-46）——旧日志字段号对不上是历史问题不是 bug。
- KV 的 session 隔离依赖客户端自觉传 session-id metadata：不传即全局命名空间、互相覆盖（gateway.py:107-108 有 overwriting warning）。
- MessageQueues 纯内存：网关重启即订阅与 KV 全丢，必须重新握手。
- persistent 消息无 TTL/清理（gateway.py:44 TODO），多次握手会堆积。
- ShutdownRequest.grace_period 默认 10 秒（controller.proto:137），而 session.shutdown 默认 1 秒（session.py:174），两处默认不一致。

---
本文 3489 字符（去空白），17 个行号锚。
