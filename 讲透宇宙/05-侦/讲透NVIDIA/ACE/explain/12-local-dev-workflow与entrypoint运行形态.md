# 12 · local-dev-workflow 与 entrypoint——本地改码、集群验证的桥

> 源：`workflows/tokkio/5.0.0-ga/local-dev-workflow/`（start_dev.py 218 行 + config.py 86 行 + .env）与 `src/llm-rag/entrypoint.sh`（53 行）+ Dockerfile

## 一、角色定位

**start_dev.py 是"本地跑 ACE Controller 大脑、集群跑其余全家桶"的开发工具**（README.md 一段话定位：customized ACE Controller locally、Tokkio app in cluster、fast iterative）。Tokkio 十余个微服务里，开发者高频改的只有 bot.py 所在的 controller；此工具把集群里四个推理/基础服务凿洞成 NodePort 供本地进程连、把集群 UI 的 WebSocket 指回本地、监听集群相机事件流模拟 SDR 把会话切到本地——**改完代码保存即热重载生效，无需重建镜像重部署**。**entrypoint.sh 则是 llm-rag 容器的统一入口**：环境装配 + 参数解析 + uvicorn 热重载启动，一份脚本撑起容器/本地/换配置/换应用四种运行形态。

## 二、内部结构

### 2.1 TokkioDevTool 六方法（start_dev.py:29-188）

- `__init__`：load_kube_config + AppsV1/CoreV1 两 API 客户端（start_dev.py:31-33）；`deployment_env_dict`（:40）存 ENV 旧值供回滚。
- `get_k8_cluster_ip`（:42-47）：遍历节点取 InternalIP。
- `update_k8_deployment_env`（:49-62）：读 deployment→定位 container→定位 env；**传值=备份旧值+写新值，传 None=从备份还原**（:56-60）——一个方法双向用，patch_namespaced_deployment 落盘。
- `patch_service_to_node_port`（:64-87）：按 config 的 node_port_settings 把服务 patch 成 NodePort，回读实际 nodePort，套 url 模板替换 `<host>/<port>` 生成 ENV 值，**既写 os.environ 又追加进目标 .env 文件**（:81-87）。
- `handle_pipeline_trigger_event`（:114-163）：连 Redis（REDIS_URL，重试 10 次每次睡 2 秒，:118-130）→ 主循环 `xread(streams={vst_events: last_id}, block=0)` 与 stop_event 用 `asyncio.wait(FIRST_COMPLETED)` 赛跑（:134-137）；消息体取 `message["sensor.id"]` 解 JSON（:146），事件 `change` 值 ∈ {camera_streaming, camera_remove} 才处理（:147），**camera_url 里的 RTSP 主机被正则重写成 `<cluster_ip>:30554`**（:148，VMS 的 NodePort）——本地进程从集群 VMS 拉流。
- `trigger_pipeline`（:174-188）：httpx POST 本地 ACE Controller 的 `stream/add|remove`（services 表 sdr_op 映射，config.py:81-84）。
- `cleanup`（:89-104）：服务还原 ClusterIP + 部署 ENV 还原（走 None 分支）；scale 回滚块被注释（:95-97）。
- `main`（:190-212）：写 env 文件（源 .env + 自动生成行 → `../src/llm-rag/.env`，:193-199）→ 逐部署写 ENV（:205-207）→ 挂 SIGINT/SIGTERM/SIGHUP 三信号（:209-211）→ 进事件循环。

### 2.2 config.py 全部行为开关（config.py:16-86）

settings：namespace "app"、本地 ACE Controller http/ws 地址占位（:17-21）、env 文件 src `.env`→target `../src/llm-rag/.env`（:22-25）。**node_port_settings 四服务**（:39-53）：a2f(50010)→A2F_GRPC_URL、riva(50051)→RIVA_SERVER_URL、animation-graph(8020+51000)→ANIMGRAPH_URL/GRPC、redis-timeseries(6379)→REDIS_URL。**deployments 两组**（:56-75）：ace-controller-sdr 容器 WDM_MSG_KEY 塞 "dummy"（骗过集群侧 SDR 的消息键校验）、tokkio-ui 容器 ACE_CONTROLLER_WEBSOCKET_ENDPOINT 改指本地 ws——**集群 UI 前端从此连本地大脑**。services（:78-86）：本地 controller 的 stream/add|remove。

### 2.3 entrypoint.sh 四种运行形态（entrypoint.sh:11-53）

先 `export $(cat .env | xargs)`（:11）+ CONFIG_PATH 默认 `./configs/config.yaml`（:12）；六个默认值 PORT 8000/HOST 0.0.0.0/APP_NAME src.bot:app/APP_DIR ./（:14-17）；参数 `--config/--extra-config/--port/--host/--app-name/--app-dir` 覆盖（:20-34）；CONFIG 文件不存在 exit 1（:36-39）；三把密钥文件落 ENV（:41-50）；最终 `uvicorn --reload --reload-dir $APP_DIR --reload-include $CONFIG_PATH`（:53）。四种形态：**① 容器默认**——APP_NAME=src.bot:app、PORT=8000、配置取镜像内挂载份；**② 本地开发**——同脚本在 src/llm-rag 下直跑，.env 由 start_dev.py 生成（含集群端点），CONFIG_PATH=configs/config.yaml 相对路径生效；**③ 换配置实验**——`--config=` 指其它 yaml，或 `--extra-config=`（设 EXTRA_CONFIG_PATH，**本仓零消费点**，仅 entrypoint.sh:24 一处 export，推测由 nvidia_pipecat 内部消费、仓内不可证）；**④ 换应用**——`--app-name=--app-dir=` 指向别的工作台（如 audio2face-3d-tuning 的 bot.py），APP_DIR 同时喂 --reload-dir 保持热重载。

## 三、外部连接

**K8s 侧**：四个被凿洞的 Service、两个被改 ENV 的 Deployment（ace-controller-sdr-envoy / tokkio-ui）、Redis Timeseries 的 vst_events 流（与 09 篇 params:152-156 的 message_broker_topic 同键）。**本地侧**：../src/llm-rag/.env 喂 bot.py（bot.py:70 load_dotenv）；本地 controller 起 8000 端口收集群来的 stream/add。**同仓脚本群**：scripts/debug/capture_debug_info.sh（139 行，集群取材器：events/pod 日志/helm values 打包时间戳目录，提工单用）；scripts/one-click/ 五平台（aws/aws-lite/azure/baremetal/gcp）Ansible 全栈部署——与 local-dev 是"首次部署"对"日常迭代"的分工。

## 四、数据流

迭代循环：启动 start_dev → 集群四服务转 NodePort + .env 生成 + UI 指回本地 → 开发者本地 `bash entrypoint.sh`（读 .env，热重载模式）→ 集群里相机/VMS 产生 vst_events 消息 → start_dev 收到 camera_streaming → camera_url 主机重写 → POST 本地 `stream/add` → 本地 bot.py 建管线：WS 控制面接集群 UI、A2F/Riva/AnimGraph/Redis 全走集群 NodePort、RTSP 从集群 VMS 拉 → 会话完整跑通。Ctrl+C → stop_event → 循环退出 → cleanup：ClusterIP 还原 + UI 的 WS 端点还原 + WDM_MSG_KEY 还原——**集群回到自治状态，下次再跑工具再切**。

## 五、设计决策

1. **凿洞而非镜像**：不把服务搬本地（模型服务动辄数 GB），只暴露端点——工具零 GPU 依赖，笔记本可跑。
2. **改部署 ENV 而非改服务**：UI 连哪由 env 决定，回滚=写回旧值（:59-60）；备份字典在工具进程内存，**工具崩溃未经 cleanup 则集群残留被切状态**——这是已知脆弱点，重跑工具会重新覆盖，但中途 UI 会连不上本地。
3. **vst_events 是切流的事实源**：不轮询会话表、不代理流量，只监听事件流把"该建流了"转告本地——最小侵入；正则重写 camera_url（:148）把"集群内 DNS"翻译成"NodePort 可达"。
4. **--reload-include 监听配置文件**：yaml 改动也触发重载（entrypoint.sh:53），与 10 篇 HotReload 链闭环。
5. **WDM_MSG_KEY="dummy"**（config.py:61-63）：集群 SDR envoy 会校验消息键，塞假值让它跳过真校验——工具化绕行生产检查的典型取舍。

## 六、新人提示

- 跑之前改 config.py:18-21 两个占位 URL 为本机可达地址（ws_url 是集群 UI 回连你的入口，写机器 IP 别写 localhost）。
- .env 里 NVIDIA_API_KEY 是占位 nvapi-xxx，真 key 写 local-dev-workflow/.env 源文件——start_dev 会原样合并进生成文件。
- 卡在"没事件来"先查 Redis 流：`XLEN vst_events`（工具不产生事件，只消费）；集群里没有相机/VMS 活动，本地就永远等。
- 中断后集群 UI 连不上：八成 cleanup 没跑完（kill -9 或崩溃），重跑 start_dev 再正常退出即可复原。
- EXTRA_CONFIG_PATH 目前仓内无消费者，指望 `--extra-config` 叠加配置前先在 nvidia_pipecat 侧求证。

## 甄别记录

任务书称 "四组 dev 脚本四种运行形态"；源码实证：**四种运行形态由 entrypoint.sh 的参数/环境矩阵给出**（容器默认/本地开发/换配置/换应用，:14-34+53），仓内 dev 相关脚本实为四组——local-dev-workflow/start_dev.py、src/llm-rag/entrypoint.sh、scripts/debug/capture_debug_info.sh、scripts/one-click/ 五平台组——前两组构成日常迭代环，后两组是取材与首装。图谱 summary 称 start_dev.py "217 行" 实测 218 行（含末尾 try/except）。
