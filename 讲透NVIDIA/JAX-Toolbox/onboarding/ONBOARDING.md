# JAX-Toolbox 新人上手文档（ONBOARDING）

> 基于知识图谱（866 节点/1466 边/16 层/16 步 tour，commit f9d55b6，2026-10-14）编写，行号锚已对照源码核实。

## 1. 仓库定位与一句话画像

**一句话画像**：NVIDIA 官方的「JAX/XLA on GPUs 之家」，双生态共生——核心是 `jax-inference-offloading`（JAX-vLLM 推理卸载框架），外围是占六成体量的 `.github/` CI 设施（NGC 容器矩阵的构建、测试、云上验证与回归分诊）。

量化画像（tracked 339 文件）：`.github/` 209 个（约 62%）、`jax-inference-offloading/` 77 个（约 23%）、`docs/`+`fern/` 45 个（约 13%）。README.md:28 把卸载框架列为 Experimental projects，README.md:31 起的 Latest news 主体是 NGC 容器月度发布要闻（当前 26.09：CUDA 13.4、JAX 0.11.1）。框架定位见 jax-inference-offloading/README.md:5：RL 每轮迭代要生成大量 rollout、常主导总算力——让训练留在 JAX、生成卸载给 vLLM。一句话：**训练用 JAX、生成用 vLLM、控制面走 gRPC 网关、数据面走 NCCL 星型直连**。

## 2. 顶层目录地图

- `jax-inference-offloading/`：框架本体——包 jax_inference_offloading/（api/controller/transport/engines/vllm/models/sharding）、examples 三形态、tests、dockerfile/oss.dockerfile、pep517_backend.py。
- `.github/workflows/`：32 个 YAML。入口 ci.yaml、jax-vllm-offloading.yml 系（框架专线）；下划线前缀 `_*` 均为被复用子流程。
- `.github/container/`：多阶段 Dockerfile（base/jax/maxtext/alphafold/equinox/torchax/nccl-gke/mpi 共 8 类）+ 构建脚本 + manifest.yaml（上游 18 包「世界状态」）+ nsys_jax/ 性能剖析包。
- `.github/triage/`：40 文件 triage 机器人，CI 回归时按 bisect/git 历史定位肇事提交。
- `.github/actions/`：10 个 composite actions（build-container、gke-xpk、eks-jobset 等），被上百处引用。
- `.github/gke-workflow/` + `eks-workflow-files/`：GCP/AWS 云验证线——XPK 补丁、GPU Operator helm 栈、NCCL 多机脚本、JobSet 模板（jio-eks 的 gateway/vllm-node/jax-node 三作业）。
- `docs/` + `fern/`：Fern 文档站，docs/index.yml:16 定义八大节导航；根配置另有 Makefile/package.json/.pre-commit-config.yaml（禁直推 main）。

**新人最常见误读**：根 Makefile:3-21 只有 docs-dev 等五个目标，全是文档站入口——**容器构建不在 Makefile**，在 .github/container/ 里。

## 3. 架构分层（图谱 16 层）

16 层天然归三大块。**CI/基础设施侧（L01-L07）**：L01 根配置 → L02 复合 Actions（build-container 与 gke-xpk 是最高扇入枢纽）→ L03 镜像构建（Dockerfile.base 是全部镜像地基，jax 镜像用 bazel 从源码构建）→ L04 nsys_jax（nsys 报告解析为 DataFrame）→ L05 triage → L06 CI 工作流 → L07 GKE/EKS 云部署。

**框架侧（L08-L15）**：L08 打包（自研 pep517 后端 + oss.dockerfile 三阶段）→ L09 gRPC 协议（三 proto 契约）→ L10 Controller 编排（gateway+客户端底座+SPMD）→ L11 NCCL 传输（tensor 级 star + model 级 fused/grouped/unfused）→ L12 vLLM 引擎集成 → L13 模型切分会话（session、checkpoint、PolymorphicMesh）→ L14 示例（single_controller 与解耦同步/异步 + Llama 映射 JSON）→ L15 测试。

**文档站（L16）**：Fern 源文件、GPU 特性长文、Ray 容错示例、生态栈交互图。主干关系：proto 契约（L09）是宪法，L10-L13 围绕它展开；L02 的 actions 是 L06/L07 的积木。

## 4. 核心链路数据流

### 4.1 推理卸载主线（decoupled_synchronous 形态）

编排脚本按序拉起四进程：decoupled_sync.sh:272 Gateway（无 GPU）、:282 vLLM Worker、:290 JAX Controller、:296 Prompt Dispatcher。

1. **网关就位**：run_gateway()（gateway.py:191-201）单进程 gRPC server 挂 CouplingController 与 MessageBroker 两个 servicer，共享内存 MessageQueues（gateway.py:40）——网关本质是「带 KV 存储的进程内 pub/sub 交换机」。
2. **握手**：OffloadingSession（session.py:67-100）建双 stub，经 _do_handshake（session.py:114-153）生成随机 response topic、调 AsyncHandshake（session.py:139）；网关 persistent 发布（gateway.py:127-130）；vLLM 侧 make_rollout_client（rollout_client.py:372）订阅、加载参数映射并回 HandshakeResponse；session 解析 mapping_specs 与两侧 TP（session.py:103-107），断言 TP 为 2 的幂（session.py:147-151）。
3. **建传输**：VLLMTransferEngine（vllm_transfer_engine.py:38）在 leader 上先 GetNcclId（网关经 cupy nccl.get_unique_id() 分发，gateway.py:123-125），再 CreateTransport 推 config_json 给 vLLM。NcclStarTransport.configure（nccl_star.py:54-58）按 trainer_ranks>=rollout_ranks 定 fan-in/fan-out。
4. **权重更新**：update_weights（vllm_transfer_engine.py:151-189）接受 dict/nnx.State/nnx.Module 三种参数——默认 grouped 模式把全部 reshape/reshard 编进单个 jit，在 buffer_callback 内以 nccl.groupStart/groupEnd（nccl_grouped.py:120-130）合并为一个 NCCL 组。JAX/vLLM TP 任意非素数比的 reshard 由 PolymorphicMesh（mesh.py:26）素因子分解支撑（util.py:17）。
5. **推理回路**：Dispatcher 发 AsyncInference（gateway.py:142-145），vLLM 结果经 SubscriptionStream 服务端流（gateway.py:169-188，Any 信封）流回 JAX，由 RolloutAccumulator 按 (batch_id, prompt_index) 聚齐成组。

### 4.2 CI 链（容器矩阵）

ci.yaml 触发：每日 07:00 伦敦时区 schedule（ci.yaml:4-6）+ push 分支 `pull-request/[0-9]+`（copy-pr-bot PR，ci.yaml:9-11），md/docs 改动被 paths-ignore 排除（ci.yaml:12-22）。流程：可选 bump manifest（ci.yaml:30-34）→ 双架构调 _ci.yaml 构建测试全部容器 → 合并 manifest list → 发布 GHCR → finalize 汇总 badge。框架专线的 jax-vllm-offloading.yml 构建发布 oss.dockerfile 后经 gke-xpk 在 GKE 跑 8B 冒烟（jax-vllm-offloading.yml:233-240 直接调 decoupled_sync.sh）。

## 5. 关键模块深潜

### 5.1 gateway.py + session.py：神经中枢与门面

ControllerServicer（gateway.py:95）实现 KV 存取（以 session-id 元数据做命名空间，:101-110）、NCCL ID 分发与握手/传输/权重更新/推理/profiler/关停入口，全部是「发布到 topic 即返回」的异步风格；Shutdown（:147-153）用 add_callback 在宽限期后停 server。topic 命名契约集中在 controller/utils.py:24-41（默认族+SC_* 单控制器族）。

### 5.2 api/ 三 proto：通信宪法

controller.proto:146-165 定义 CouplingController 的 10 个 RPC 与 26 个消息。关键设计是**异步应答不走 RPC 返回值**——AsyncHandshake/AsyncInference 都返回 Empty，应答经 message_broker.proto 的 SubscriptionStream 按 topic 推送（请求自带 response_topic/batch_id）。param_mapping.proto 是映射 DSL：VllmParam 与 JaxParam 经 ParamMapping 配对；add_sharding_specs（mapping_util.py:302）经 collective_rpc 向 vLLM 查询各 TP rank 真实 sharding spec 回填。

### 5.3 transport/：NCCL 星型传输

nccl_base.py:73 的 NcclTransport ABC 提供 dtype 映射与 unique id 的 base85 编解码；nccl_star.py 的 rank 编排是精髓：fan-in 下 k 个 JAX rank + 1 个 vLLM rank 组成 world，JAX 侧 rank = dev.id % k + 1（nccl_star.py:93-95，rank 0 留给星心 rollout peer）；fan-out 反过来，JAX 在星心恒为 rank 0。model 级三模式按参数粒度递增：unfused（逐参）→ grouped（默认，单 jit+单 NCCL 组）→ fused（全部进一个 jax.jit，仅 fan-in）。

### 5.4 engines + rollout_client：两端引擎

transfer engine 按模式分派三 transport（vllm_transfer_engine.py:76-104），并把自身作为「gateway 代理」传入。AsyncRolloutClient（rollout_client.py:382）实现有界陈旧度（max_staleness，:394-407）：处理满 N 个 prompt 后排队等权重更新——异步 RL 吞吐与一致性的折中，更新后排空队列并失效 prefix cache。

### 5.5 triage/logic.py：回归分诊引擎

container_search（logic.py:212）按日期在好/坏容器 Nightly 序列二分定位回归边界；version_search（:444）对多包版本组合做笛卡尔二分（compulsory_software=["xla","jax"]，args.py:16）。结果分类双实现：ExitCodeClassifier（logic.py:122）按退出码、MetricClassifier（metric_classifier.py:17）把 pass/fail 建为双高斯用对数证据比分类。TriageTool（triage_tool.py:109）总编排，容器工厂支持 local/docker/Pyxis(Slurm) 三运行时。

## 6. 构建与运行方式（只描述，勿在仓内直接执行）

- **proto 编译进打包**：pep517_backend.py 包装 setuptools 五个钩子，每个钩子先经 grpc.tools 的 build_package_protos 编译仓内 proto（pep517_backend.py:4-11）；setup.py 注册 cmdclass 兼容旧构建。**仓内看不到 *_pb2.py**——IDE 报 import 错属正常，先 pip install -e .。
- **oss.dockerfile 三阶段**：base（:27-43，cuda-dl-base 上装 apt+pip-tools）→ mealkit（:49-78，SSH mount 从 GitHub sparse-checkout 源码，装 cuda_package_skiplist.py 为 CLI）→ final（:84-104，pip-compile 锁定→skiplist 剔除基础镜像已带 CUDA 的 wheel→--no-deps 安装→mark-installed→pip check）。
- **CI 镜像矩阵**：manifest.yaml 是唯一「世界状态」（每包 url/tracking_ref/latest_verified_commit/mode，含 PR 补丁路由）；build-jax.sh 用 bazel 从源码构建 jaxlib。
- **文档站**：根 Makefile 五目标全包装 npm run docs:*（fern-api CLI 5.56.3）。
- **框架运行入口**：examples 三形态编排脚本；云上等价物是 EKS jio-jobset.yaml。

## 7. 新人上手路径（16 步 tour 浓缩为四阶段）

**阶段一·全景（1-2 天）**：README 与 docs/getting-started 的 introduction.md、build-status.md 建立「双生态」认知与容器矩阵/nightly 规则。不写代码，只建地图。

**阶段二·框架主线（3-7 天，L08-L15）**：按依赖序——(1) 三个 proto；(2) controller/：utils topic 表→gateway→rollout_client；(3) transport/：nccl_base→nccl_star→model 三模式；(4) engines/ 与 vllm/；(5) session.py+models/checkpoint.py+sharding/mesh.py；(6) examples 从 decoupled_synchronous 读起，对照 mappings/llama3_1b_param_mapping.json；(7) tests 反向验证：test_handshake/test_sync_roundtrip/test_async_roundtrip 各守护一条链路，conftest.py:72-149 的 FakeLLM+真实网关 ephemeral 端口让 CPU 也能跑。

**阶段三·CI 侧（8-10 天，L02-L07）**：manifest.yaml 入手→Dockerfile.base/jax→ci.yaml 与 _ci.yaml 调用关系→build-container/gke-xpk 两个最高扇入 action→GKE/EKS 双线（jio-jobset.yaml 是框架与云设施的交点）。

**阶段四·专题按需（L04/L05/L16）**：回归排查读 triage（mock 测试可离线理解）；性能读 nsys_jax 与三篇特性长文（GPU_performance、NATIVE_FP8、PGLE）；容错参考 docs/resiliency 的 Ray 示例。

## 8. 已知坑与勘误（批分析甄别 + 源码逐条核实）

1. **broken import**：integrations/simple/__init__.py:19 写 `from jax_inference_offloading.integrations.standalone.model import Llama3`——仓内无 standalone/ 包（Llama3 实际在同目录 model.py），导入必 ImportError。
2. **gemma 分支 NameError**：vllm/llm.py:63 在 vLLM<=0.9.1 且 gemma 模型时执行 torch.tensor(...)，但全文件从未导入 torch——触发即 NameError。
3. **build-te.sh 顶层 return**：build-te.sh:93 的 `return 1` 在函数外主脚本体，直接执行报「can only return from a function or sourced script」。
4. **clean.sh 双坑**：clean.sh:12 同为函数外 `return 0`；clean.sh:21 调用的 log_warn 全文件未定义，kubectl wait 失败分支二次报 command not found。
5. **PyYAML 解析即崩**：_test_nccl_gke.yaml:30 的 `BUILD_DATE: 0000-00-00` 是合法 Actions 值，但 PyYAML safe_load 抛 `ValueError: year 0 is out of range`（实测复现）——用 python yaml 解析 workflows 的工具链会在此崩；该值最终进 OCI label（build-container/action.yml:145）。
6. **requirements 重复追加**：Dockerfile.maxtext:19-29 与 :31-44 两个 RUN 块把相同三行（editable、base_requirements、google-jetstream 回补）各追加一次——复制粘贴残留。
7. **pb2 构建期生成物**：api/ 只有 .proto 无 *_pb2.py（pep517_backend.py:4-6 构建时编译）——grep 找 controller_pb2 无果属正常。
8. **parallel-launch 不聚合失败码**：parallel-launch:24-26 的 wait 循环在 set -e 下遇首个失败进程即退出——只透传一个失败码、不等其余进程。
9. **导航与安全**：根 Makefile 只管文档站；Dockerfile.nccl-gke:7-9 开 root 空密码 SSH 仅供 GKE NCCL 测试互信，勿复用。

---

**自报**：正文 7997 字（python len 去空白口径），行号锚 51 个，8 节齐全。
