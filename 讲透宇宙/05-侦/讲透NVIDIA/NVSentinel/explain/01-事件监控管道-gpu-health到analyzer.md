# 01 事件监控管道：gpu-health-monitor → health-events-analyzer

> 锚基座：本地仓 @fbe7ec29，行号实测；图谱 L04/L07 层主线。

## 角色定位

这条管道是 NVSentinel 的"感觉神经"：gpu-health-monitor 在每个 GPU 节点上把 DCGM 原始指标翻译成标准化 HealthEvent，经 UDS gRPC 送进平台连接器与存储；health-events-analyzer 在下游把离散事件聚合成节点级结论（如 XID 突发）。它回答的问题是："这块 GPU 现在健康吗？恶化到什么程度了？"

## 内部结构

**Python 传感器侧**（health-monitors/gpu-health-monitor/）：`gpu_health_monitor/cli.py:318` 装配 socket 路径等配置并启动 watcher；真主体是 `gpu_health_monitor/dcgm_watcher/dcgm.py:230` 的 `DCGWatcher` 类（全文件 1337 行，Python 侧最大实现）。四个关键子机制：热裕度监控走 DCGM field 153（dcgm.py:248-252，字段不可用时显式降级告警而非静默）；`ProbeWatchdog`（dcgm.py:137，运行循环 :221）把"探针没返回"本身当故障——堵住轮询挂死的盲区；未桥接 PCIe/NVLink down 事件可配置压制（dcgm.py:303）；`_run_dcgm_server`（dcgm.py:53）支持远端 DCGM 地址回退。镜像三段式构建（Python builder→DCGM runtime，digest 固定）。

**Go 分析侧**（health-events-analyzer/）：`main.go:54` 入口四步装配——数据库配置→分析管线→拨号平台连接器（main.go:115 的日志同时打印 socket 与 token 开关）→事件消费循环。突发检测核心 `pkg/analyzer/xid_burst_detector.go:349` `ProcessEvent`：按节点/GPU 维护 XID 错误码滑动窗口历史，窗口内计数越限即判定 burst，支持 sticky XID 延续与逐 GPU 统计；参数不必手配——:143 `ParseXidConfigFromPipeline` 能从管线配置字符串反解析（lookback 窗口 :175、burst 阈值 :203）。恢复侧由 `pkg/reconciler/node_recovery_controller.go` 调和派生条件（ADR-059）。

## 外部连接

上游：DCGM（指标源）与 kubelet（节点身份）。下游：platform-connectors（转发中枢）、store-client（落库）。事件出口契约是 `data-models/protobufs/health_event.proto:54` 的 `service PlatformConnector` 与 :94 `HealthEvent` 消息；XID 原始语义参考 syslog 侧码表（`syslog-health-monitor/pkg/xid/parser/factory.go:48` 从内嵌 Excel 加载 XID→处置映射，:121 sidecar 服务按驱动版本解码）。姐妹件 event-exporter（`event-exporter/main.go:45`）把同一事件流导出到外部 sink。

## 数据流

DCGM 轮询→DCGMWatcher 判定（热裕度/NVLink/probe 看门狗）→构造 HealthEvent（isHealthy/isFatal/errorCode/entitiesImpacted）→cli 经 commons healthpub 拨号发布（`commons/pkg/healthpub/dial.go:86`，直连模式重试拦截器 :222、重试上限 :214）→连接器盖时间戳写 K8s+存储→analyzer 经 change stream 消费→burst 判定结果回写存储→fault-quarantine/fault-remediation 消费决策。

## 设计决策

ADR-001（`docs/designs/001-health-event-detection-interface.md:19`）否决"监控器直写 K8s API"与"共享数据库"，选 UDS gRPC：监控器不带 K8s 客户端、语言无关（GPU 监控因此敢用 Python）、本地 socket 零网络面。`:25` 钉死 socket 路径、:26 钉死 RPC 名 `HealthEventOccuredV1`。burst 检测参数挂在管线配置里而非独立 CR，是"配置即代码"取向——代价是 :143 那类反解析函数必须存在。

## 新人提示

先读 dcgm.py 的类注释再读代码，注释密度接近设计文档。注意 `docs/DATA_FLOW.md:17-20` 的"Mongo change streams pub-sub"是存储分发层视角，别误读为监控器直写 Mongo——节点内永远是 UDS gRPC 两跳。改 proto 后 `*.pb.go`/`*_pb2.py` 全是生成物勿手改。热裕度降级日志（dcgm.py:252）在老驱动上常见，属预期不是 bug。
