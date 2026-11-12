# explain-12 · core/metrics.py——全部 dashboard 指标的定义与聚合中枢

## 角色定位

`xinference/core/metrics.py`（1306 行）是**唯一**的 Prometheus 指标定义处：Web UI dashboard 和 `/metrics` 端点上的每一个曲线，名字、类型、桶、标签都在这个文件声明（aioprometheus 风格，指标名统一 `xinference:` 前缀）。它同时解决三个进程角色"同一模块、不同指标子集"的分工问题——ModelActor/WorkerActor 打点 worker 侧指标，supervisor 侧的 REST 进程每 15 秒拉取集群数据刷新 gauges，worker 的独立 metrics 导出服务器也由本文件启动。

## 内部结构

指标按五节组织（节注释即文档）：①**worker 侧 LLM 推理指标**（`:37-56`）：`generate_tokens_total`/`time_to_first_token_seconds`（直方图桶 0.05s→30s→inf，`:47`）/input/output token 计数器；②**worker 侧服务质量指标**（`:58-100`，全模态）：request_total/errors_total/duration（桶精细到 0.01s-120s 十四档，`:72-87`）/serve_count/request_limit/last_load_duration；③**supervisor 侧集群 gauges**（`:102-165`）：uptime/workers_total/worker CPU·内存·GPU 六件套/model_info（value=1 的存在性指标）/model_status/model_gpu_binding（每副本每 GPU 一条序列）/model_gpu_memory/model_unexpected_termination；④**token router 指标族**（`:165-326`）：agent 连通性/管理状态/心跳年龄、assignment 期望态 vs 观测态、runtime revision 同步等 40+ 个 gauge——router 的整套可观测性矩阵；⑤**安全指标**（`:341-365`）：api_key 请求计数/时长/active/expired/banned IPs/keys。两份**角色清洗名单**是结构性关键：`_SUPERVISOR_ONLY_METRICS`（`:370-432`，50+ 个名字）与 `_WORKER_ONLY_METRICS`（`:437-448`）——因为模块级定义会全局注册，进程启动时按角色把不属于自己的一侧从 REGISTRY 摘除。

## 外部连接

打点方：ModelActor 的 `record_metrics`（`core/model.py:1419`）按**名字字符串**动态路由到本模块（`record_metrics(name, op, kwargs)`，`:494-502`，globals().get+getattr 反射，打点失败只记日志绝不影响推理）；worker 记录加载耗时（`core/worker.py:4587-4596`）与 build/config info（`:1457-1462`）。聚合方：REST 进程的 `_cluster_metrics_update_loop`（`api/restful_api.py:976-996`）每 15 秒调 `update_cluster_metrics(cluster_data, models_data)`（`:550`）+`update_security_gauges`（`:1213`）。导出方：双通道——supervisor 进程 `/metrics` 挂在主 FastAPI（`restful_api.py:895`），worker 的独立导出服务器由 `launch_metrics_export_server`（`:1266-1306`）启动：worker 侧先摘 supervisor-only 指标（`:1267-1271`），再起独立 uvicorn（带 Slowloris 硬化协议 `:1284-1286`），socket 地址经 queue 回传给 WorkerActor（`core/worker.py:882-894`）。

## 数据流

`update_cluster_metrics`（`:550-1210`）是 supervisor 侧的核心循环，数据来自 `supervisor.get_cluster_metrics_data()`（worker 上报的资源+GPU 快照）与 `list_models()`。每轮的固定套路：**set 当前帧 + drop 陈旧帧**——worker/gpu/model/gpu_binding/model_gpu_mem/unexpected 六组标签集合与 `_prev_*_labels` 全局变量做差集（`:453-460`），消失的序列用 `_drop_series` 从 collector.values 直接 pop（`:463-473`，docstring 点破 aioprometheus 无公开 remove API，零值与删序列语义不同）；新出现的 set 进来。典型片段：worker 资源三表按 `(addr)` 键控（`:621-626`），GPU 三表按 `(addr, gpu_idx, gpu_name)`（`:628-633`），model_info 支持两种形态——多 worker 副本走 `model_replica_distribution` 的 worker_distribution（`:646-667`），单机走 address 直报（`:668-688`）。`update_security_gauges`（`:1213`）则扫 auth DB 与 rate limiter 内部状态算 active/expired/banned 四个 gauge（注释：周期刷新保证无事件时 gauge 也有值）。`set_build_info`（`:505`）以标签携带版本号/python 版本/角色地址——Prometheus 生态的 build_info 惯例。

## 设计决策

①**定义集中、打点反射**：所有指标全局唯一命名集中本文件，打点方只需字符串——代价是重命名无编译期检查，收益是任意进程角色零依赖引用同一套名字；②**角色清洗而非条件定义**：模块级全量定义+启动时按角色 deregister（`:1267`/`restful_api.py:886-892`），保证 import 顺序无关、REST 重启不产生 worker 指标的空 HELP/TYPE 头（注释明言）；③**快照式 gauge 同步**：与其让各处增删 gauge，不如每 15 秒全量重设+差集清除，标签漂移（worker 改名/模型终止）自动收敛——`_drop_series` 直捅内部容器是权衡后的越界；④**指标失败不致命**：`record_metrics` 全吞异常（`:499-502`），观测永远不给推理路径添堵。

## 新人提示

加新指标的完整 checklist：本文件定义（带 `xinference:` 前缀与标签文档）→ 视角色加入 `_SUPERVISOR_ONLY_METRICS`/`_WORKER_ONLY_METRICS`（漏了会在另一角色的 /metrics 出现空序列）→ 若是 supervisor 侧 gauge，在 `update_cluster_metrics` 加 set+drop 逻辑（记得同步 `_prev_*` 集合）→ 打点处用 `record_metrics("名字", "add/set/observe", {...})`。排查"指标消失/残留"直接看差集逻辑：`_prev_*_labels` 是模块级可变全局，多事件循环共存的进程里要小心。dashboard 查询指标名一律加 `xinference:` 前缀；TTFT 的桶上限 30s+inf，长首 token 会全落 inf 桶，分析时注意。
