# 12 Helm 部署、dev/compose 本地编排与 dashboard/portal 双 SPA

## 角色定位

部署面三件套：`nemo_retriever/helm/` 是生产级 Kubernetes chart（1608 行 values，主 Deployment + NIM Operator 子模板群）；`nemo_retriever/dev/compose/` 是开发本地编排（compose 明说"development-only，生产走 Helm"，README 首段）；UI 面是两个无构建 CDN SPA——服务侧 `service/dashboard/`（gateway 挂载的作业观察台）与 harness 侧 `harness/portal/`（评测运行门户）。NIM 子模板实际 **9 个**（任务书称八，按源码核为九：answer-llm/audio/rerank-vl/embed/nano-omni/ocr-v2/page-elements-v3/parse/table-structure-v1）。

## 内部结构

**Helm chart**。主 Deployment 模板支持双拓扑：`topology.mode` standalone（默认，单 Deployment 进程内跑 realtime+batch 双池，`deployment.yaml:38-52`，策略 Recreate）与 split（三 Deployment：gateway/realtime/batch，roles 循环 `deployment.yaml:237`，gateway 强制 Recreate、worker RollingUpdate `:252`；realtime/batch 是 ClusterIP 不直接暴露，`values.yaml:232-233` 注释）。两道模板期断言：split 模式 gateway replicas 必须=1（进程本地调度器，`deployment.yaml:25-27` 直接 fail）；`installFfmpeg` 与 env 里的 INSTALL_FFMPEG 互斥（`deployment.yaml:29-36`）。split 的 worker 带 `wait-for-gateway` init 容器轮询网关存活（`deployment.yaml:284-294`）。GPU 按 role 注入 `nvidia.com/gpu` limit（`deployment.yaml:168`），探针可关（`:197-201`）。

`templates/nims/` 九个子模板，每个产出 **NIMCache+NIMService 一对** CR（`apps.nvidia.com/v1alpha1`，见 `nemotron-ocr-v2.yaml:4-5`），由 NVIDIA NIM Operator reconcile；模板开头双条件——集群有 NIM CRD 且 `nims.enabled` 且对应 `nimOperator.<x>.enabled` 才渲染（`nemotron-ocr-v2.yaml:1`）。模型从 NGC 拉（`modelPuller: nvcr.io/...`，`nemotron-ocr-v2.yaml:10`），auth/pull Secret 走 helper（`:11-12`），每 NIM 独立 PVC 存储。`values.yaml:956` 起 nimOperator 块集中默认值。周边设施齐：HPA（`hpa.yaml`）、ServiceMonitor+Prometheus adapter 自定义指标（`servicemonitor.yaml`、`prometheus-adapter-rules.yaml`）、OTel collector Deployment/ConfigMap、Zipkin、Ingress、三个 PVC、NGC 两 Secret（registry+api，`values.yaml:38/53`）。服务默认 NodePort 7670（`values.yaml:210-212`）。

**dev/compose**。`service-mode.compose.yaml` 零配置默认只起 retriever+LanceDB，推理走 NVIDIA hosted 端点（README 明确提示数据出域，`dev/compose/README.md:24-27`）；`x-nim-service` 锚点定义 NIM 容器公共形态：nvidia runtime+16gb shm+`/v1/health/ready` healthcheck 40 次重试（`service-mode.compose.yaml:30-39`）。全量 NIM 栈按需拉起，镜像全部 nvcr.io/nim：ocr-v2（`:152`）、embed-1b（`:175`）、rerank-vl（`:189`）、parse（`:198`）、caption nano-omni（`:207`）、answer lightning（`:216`）、parakeet 音频（`:237`）、page-elements/table-structure（`:108/:130`）+OTel collector（`:251`）。认证三层：NGC_API_KEY（registry，与运行时 NVIDIA_API_KEY 分开，README:13-17）、NRL_API_TOKEN（对外 bearer）、NRL_INTERNAL_VDB_TOKEN（Retriever→VectorDB 内部跳独立凭据，`README.md:40-47`）。`presets/` 六个 env 文件按场景组合（nims-core/nim-answer/nim-audio/nim-caption/local-models/observability）；另有 `service-mode.local-models.compose.yaml`（HF 本地模型变体）、`neo4j.compose.yaml`（表格线）、`judge.compose.yaml`。

**双 CDN SPA**。两个 UI 都是"无构建"React：JSX 源码直接进浏览器由 Babel standalone 现场编译。dashboard 用 unpkg（React/ReactDOM/Babel，`service/dashboard/static/index.html:193-195`），portal 用 jsdelivr 且多带 Chart.js+Luxon 时序图栈（`harness/portal/static/index.html:10-15`）。dashboard 路由 `service/routers/dashboard.py:26` 挂 `/v1/dashboard`（`service/app.py:333-335`），**仅 gateway 模式挂载**（`app.py:328` 的 mode 判断；router 文件头注明 gateway-only）；overview 接口扇出问每个 worker pod 的池状态（`routers/admin.py:8` 注释）；作业流是 SSE——`/api/jobs` StreamingResponse 同时推 job_update 与 job_lifecycle 两类事件（`routers/dashboard.py:182-204`），前端 `EventSource` 消费（`views/jobs.jsx:67`）+REST 列表（`:40`）。视图五件：overview/jobs/job_detail/vdb（向量库观察）/layout。portal 是 harness 运行门户（`harness/portal/app.py:208` FastAPI），自带 MCP server 挂 `/mcp`（`app.py:211`，fastmcp 缺失则降级跳过 `:206`），视图含 run-detail/ingestion/models/runners——与 dashboard 完全不同的域（评测 harness vs 服务作业）。

## 外部连接

Helm 依赖 K8s 生态：NIM Operator CRD（apps.nvidia.com）、cert-manager 级 Ingress、Prometheus Operator、OTel/Zipkin 链路。compose 依赖 NVCR 镜像仓与 NGC 凭据。dashboard 前端零 npm 依赖纯 CDN；后端连篇 7 模型接入层与 ingest 路由（`routers/ingest.py:2296` 注释提 dashboard 特权事件流）。portal 连 harness runfiles 与 Ray 作业。两者静态目录同构（static/index.html+nvidia-logo.svg+views/*.jsx），明显同模板 fork——但 CDN 与视图域已分叉。

## 数据流

生产部署：helm install → 渲染主 Deployment（standalone 单体或 gateway+realtime+batch 三体）+ 按需九 NIM CR → NIM Operator 拉 NGC 模型建缓存与服务 → 流量从 NodePort/Ingress 进 gateway → dashboard SSE 从 gateway 聚合各 worker 的作业事件推浏览器。本地开发：`docker compose -f service-mode.compose.yaml up` → retriever 服务起在 7670，按 presets env 决定推理走 hosted 端点还是本地 NIM 容器 → `/v1/health` 验活。

## 设计决策

1. **拓扑双模一套模板**：standalone/split 共用 deployment.yaml，roles 循环消重；非法组合（split 多 gateway、ffmpeg 双设）渲染期 fail 而非运行期炸。
2. **NIM 声明式托管**：检索器自身的模型服务交给 NIM Operator CR，chart 只管 enabled 开关与存储——运维面与模型面解耦。
3. **CRD 探测式降级**：`Capabilities.APIVolumes.Has` 让 chart 在无 Operator 集群安静跳过 NIM 块。
4. **零构建 SPA**：JSX+CDN Babel 换掉 npm 工具链——镜像里无 node_modules，改 UI 即改文件。
5. **双 token 内外分离**：对外 API token 与内部 VDB token 独立，最小权限。
6. **SSE 而非轮询**：dashboard 作业流推送式，配 snapshot/list REST 兜底。

## 新人提示

- split 模式的 gateway 是单点（replicas 锁 1，进程内调度），扩容前先读 `deployment.yaml:25` 的注释再改。
- dashboard 看不到？先确认服务以 gateway 模式跑——standalone 单体模式不挂 dashboard 路由。
- 两个 SPA 的 CDN 一个 unpkg 一个 jsdelivr，离线/内网环境都会白屏，需自托管静态资源。
- compose 的 NGC_API_KEY（拉镜像/模型）与 NVIDIA_API_KEY（hosted 推理）是两套凭据，403 与 401 分别查谁别搞混（README:13-17 有对照）。
- NIM 子模板的条件链是三层 and（CRD+总开关+分开关），NIM 没起来时逐层查 values 而不是只看 `nims.enabled`。
