# 09 · 部署运维线：双配置中心、watchdog 生命周期与模型服务舰队

> 定位层级：部署运维与 CLI 脚本。本篇覆盖 `deploy/` 17 个脚本（1172 行）、`script/` 的模型服务启动组、`docker-compose.yml` + `docker-compose.host.yml` + `script/nginx_echomimic.conf`。这条线回答一个问题：Paper2Any 这台"论文到多模态产物"的机器，怎么在一台多 GPU 服务器上活起来、活着、死了能爬起来。

## 一、角色定位

deploy/ 与 script/ 分工明确：**deploy/ 管应用进程**（FastAPI 后端 + Vite 前端的裸机启动/停止/守护），**script/ 管模型服务与 CLI**（SAM3、EchoMimic 等 GPU 舰队 + 各转换命令）。部署形态有两种：裸机（deploy/start.sh 系）与容器（docker 三件套），共享同一套 `.env` 约定。此外支持国产 GPU 适配：`DEPLOY_TARGET` 可取 generic/nv/muxi（沐曦），对应 `deploy/start_nv.sh`、`deploy/start_muxi.sh` 与 profiles/ 下的 nv.env/muxi.env。

## 二、内部结构

### 2.1 双配置中心

- **`deploy/app_config.sh`（31 行）**：裸机侧的变量宪法。L6-7 锚定 DEPLOY_DIR/PROJECT_ROOT，随后全带默认值的可覆盖变量：`DEPLOY_TARGET`（L9，默认 generic）、`APP_HOST/APP_PORT`（L10-11，8000）、`APP_WORKERS`、Python 发现链（APP_CONDA_ENV→APP_PYTHON→APP_FALLBACK_PYTHON=/opt/conda/bin/python3，L13-15）、前端三元组（FRONTEND_HOST/PORT=3000/DIR，L18-20）、`MODEL_SERVER_ENV_FILE=logs/model_servers.env`（L24，模型服务地址的回填文件）。
- **`deploy/docker_env.sh`（40 行）**：容器侧的等价物。核心是 `load_env_file`（L9-15，set -a/source/set + a 三连）串起**五级加载链**：docker.env.example（compose 级默认）→ fastapi_app/.env（后端运行时）→ frontend-workflow/.env（前端构建期）→ profiles/nv.env 或 muxi.env（机型）→ deploy/docker.env（本地覆盖，最后加载者赢）。L36-39 组装 `COMPOSE_FILE_ARGS`，`DOCKER_HOST_NETWORK=1` 时叠加 host.yml 覆盖文件。

两个中心不互相引用——裸机脚本 source app_config.sh，docker 三件 source docker_env.sh，是两条平行宇宙，机型变量（nv/muxi）是它们唯一的共同语言。

### 2.2 生命周期三件：start/stop/watchdog

- **`start.sh`（261 行）**：source 配置后做 Python 验证（L31-40 `validate_python` 用 heredoc 逐个 import cv2/cairosvg/fastapi/moviepy.editor/supabase/torch/uvicorn，缺哪个依赖直接判废），选择解释器、写 `logs/uvicorn.pid`、拉起 uvicorn。
- **`stop.sh`（163 行）/`stop_frontend.sh`（79 行）**：按 pidfile + 端口双口径收割进程。
- **`backend_watchdog.sh`（333 行）**：后端守护。参数族 L17-20（间隔 15s、连续失败阈值 2、重启冷却 30s、健康超时 5s、启动等待 25s）。**互斥用 mkdir 原子锁**：L112-113 `acquire_lock() { mkdir "$WATCHDOG_LOCK_DIR" 2>/dev/null; }`、L122-124 `rmdir` 释放——mkdir 的原子性天然防双实例，比 `pgrep -f` 判活可靠（后者有自匹配坑）。**守护化靠 `$0 run 自指**：L207-212 `start_watchdog` 里 `nohup setsid bash "$0" run ...&`，有 setsid 就建新会话脱离终端，没有则裸 nohup 降级。健康探测打 `http://127.0.0.1:$APP_PORT/health`（L33 `health_url`），失败计数达阈值即重启 uvicorn。

### 2.3 find_port_listener_pids：七脚本同构复制

`find_port_listener_pids` 是"查端口占用 PID"的三级降级函数（lsof → ss → netstat，各取 `pid=` 解析去重），定义于**七处**：`deploy/backend_watchdog.sh:37`、`deploy/start.sh:156`、`deploy/stop.sh:87`、`deploy/start_frontend.sh:28`、`deploy/stop_frontend.sh:12`、`script/start_model_servers.sh:49`、`script/stop_model_servers.sh:11`。七份拷贝逐字同构（连 awk 端口正则都一致），改一处必须同步六处——这是典型的"复制优先"运维脚本风格，正确做法是沉进 app_config.sh 或独立 lib.sh。

### 2.4 script/ 模型服务：三通道 GPU + SAM3 舰队 + EchoMimic 编队

**`start_model_servers.sh`（474 行）**是模型侧总指挥：

- **三通道 GPU 发现**（`discover_available_gpus` L148-190）：`SAM3_GPU_MODE=manual` 时直接吃 `SAM3_GPUS` 列表；auto 时按 `DEPLOY_TARGET` 选工具——muxi 走 `mx-smi -L`（L167-174）、nv 走 `nvidia-smi --query-gpu=index`（L161）、generic 走**内联 Python + torch**（L177-190，用 `torch.cuda.mem_get_info` 按空闲显存降序输出 GPU 序号）。前置的 CUDA 可用性探测（L135-146）同样是 heredoc Python。
- **SAM3 多实例**：`SAM3_INSTANCES_PER_GPU`（L25，每卡副本数）、`SAM3_START_PORT=8021`（L27）、启动策略 sequential/parallel（L29、L404-406，串行时失败即中止）、单实例健康超时 360s（L31，SAM3 加载大 checkpoint 慢）。端口规划段 L269 一次扫描 `SAM3_START_PORT` 起 32 个端口清场。`launch_sam3_instance`（L302 起）按 `sam3_gpu${gpu_id}_inst${instance_id}_port${port}.log`（L306）落日志。路径解析 `prepare_sam3_paths`（L192 起）按 env → 仓内 models/sam3/ → PAPER2ANY_ASSET_ROOT 遗产路径三级回退。
- **`stop_model_servers.sh`** 对称回收，PID 记账同样落 logs/。

**`start_echomimic_apis.sh`**：EchoMimic 数字人视频的 8 实例编队。L17 一行硬编码分配表：`INSTANCES=( "4:8040" "4:8041" "5:8050" "5:8051" "5:8052" "6:8060" "6:8061" "6:8062" )`——GPU4×2、GPU5×3、GPU6×3。L12-13 的 `ECHOMIMIC_PYTHON=/root/miniconda3/envs/echomimic/bin/python`、`ECHOMIMIC_CWD=/data/users/ligang/EchoMimic` 是**某台具体机器的用户路径**（ligang 的家目录），换机必改，详见第 12 篇。

**`nginx_echomimic.conf`**：8 后端的统一门面。upstream `echomimic_backend`（L11-19）轮询 8040-8062 八个 server（max_fails=2 fail_timeout=30s 自动摘除），单入口 8200，`client_max_body_size 200M`（L26）。文件头注释（L3-5）钉版过一个运维坑：Nginx 默认把请求体缓冲写盘，/var 分区满时 pwrite 失败直接 500 且后端零感知，故配了 `proxy_request_buffering off` 流式直通。

### 2.5 docker 三件与 !reset 覆盖

`docker-build.sh`/`docker-up.sh`/`docker-down.sh`（10-16 行的薄壳）统一 source docker_env.sh 后执行 `docker compose "${COMPOSE_FILE_ARGS[@]}" build/up -d --build/down`，up 额外支持 `DOCKER_WITH_SAM3=1` 挂 `--profile sam3`。主 compose 三服务：backend（8000）、frontend（3000→80）、sam3（8021，checkpoint/bpe 路径经 env 注入，L110-112）。`docker-compose.host.yml` 是 host 网络覆盖：三个服务都改 `network_mode: host` 并用 **`ports: !reset []`**（L4/8/12）清空基础文件的端口映射——`!reset` 是 compose v2.24+ 才支持的 YAML 标签，老版本 docker compose 会直接解析报错，这是"容器方案在旧 Docker 上跑不起来"的第一嫌疑点。

## 三、外部连接

- **上游**：fastapi_app 读取 docker_env.sh 注入的环境（Supabase、各模型服务地址）；`MODEL_SERVER_ENV_FILE`（app_config.sh L24）是 start_model_servers 写、start.sh 读（L18-23 `maybe_source_model_server_env`）的进程间通信文件——模型舰队起完后把 SAM3/OCR 端口回填给后端。
- **下游**：OCR 服务 8003（start_model_servers.sh L39）；EchoMimic 8 实例 8040-8062 + nginx 8200；前端 3000；后端 8000。整套端口规划（8000/8003/8021+32/8040-8062/8200）就是这台机器的隐性契约。
- **文档**：`DEPLOY.md` 是部署总入口，`docs/guides/open_source_deployment.md` 是开源版精简（见第 11 篇）。

## 四、数据流

裸机启动序：`start_model_servers.sh`（探测 GPU → 逐实例拉 SAM3 → 健康等待 → 写 model_servers.env）→ `start.sh`（source app_config → 验 Python → 起 uvicorn → 写 pid）→ `backend_watchdog.sh start`（mkdir 锁 → `$0 run` 守护化 → 每 15s 探 /health，连续 2 败且过 30s 冷却即重启）。容器路径则由 docker_env.sh 五级 env 链喂 compose，host 模式走覆盖文件。停止链对称：stop/stop_frontend/stop_model_servers 按 pidfile+端口双保险回收。

## 五、设计决策（含批判）

1. **mkdir 锁 + $0 run 是亮点**：比起常见的 pidfile 判活（pgrep 自匹配误杀、僵尸 pid 文件误判），mkdir 原子锁在 shell 层是无竞态的；`bash "$0" run` 自我再入避免复制启动逻辑，setsid 降级兜底也做了。这两个惯用法值得原样抄走。
2. **七份同构复制是反模式**：find_port_listener_pids 的七处拷贝意味着"加一个 fuser 通道"要改七个文件；deploy 目录没有 lib.sh 是历史欠账。
3. **Python heredoc 探测 GPU 很聪明也很脆**：generic 通道依赖当前解释器能 import torch 且 CUDA 可用——若默认 python 是系统 python 而 torch 装在 conda env，探测直接 exit 1，脚本不会告诉你为什么（静默走向"无 GPU"分支）。PAPER2ANY_PYTHON 的解析顺序因此成为暗知识。
4. **EchoMimic 编队是"单机拓扑快照"**：8 实例 GPU 分配表、他人用户名路径、900s 超时，全是针对一台特定 8 卡机的手工调参。开源用户照抄必然路径不存在——它是团队内部脚本漏进开源树的典型样本。
5. **!reset 依赖新 compose**：host.yml 用标签清端口是干净做法，但 CI 或老旧环境常被这一行卡死；加一个"compose 版本检查"或在文档标注最低版本是欠着的功课。
6. **双配置中心不交叉**：app_config.sh 与 docker_env.sh 各自为政，同一变量（如端口）在两个世界重复定义，改端口要动两处加 N 个 env 文件。

## 六、新人提示

- 先读 `DEPLOY.md` 再读脚本；源码侧从 `deploy/start.sh` → `app_config.sh` → `backend_watchdog.sh` 顺序建立全局感。
- "后端起不来"排查顺序：logs/uvicorn.log（uvicorn 自身）→ logs/backend_watchdog.log（守护视角）→ `find_port_listener_pids 8000`（端口冲突，注意该函数在七个脚本里任选一个抄）。validate_python 失败时先确认 APP_PYTHON/APP_FALLBACK_PYTHON 指向的解释器确实装齐六个依赖。
- 玩 GPU 舰队先看 `SAM3_GPU_MODE=manual SAM3_GPUS=0` 单实例演练，再放全量；`logs/sam3_gpu*_inst*_port*.log` 命名能直接对上实例。
- docker compose 报 unknown tag `!reset` 时，是 Docker 版本问题不是配置写错——升级 compose 或删掉 host.yml 的 ports 行。
- nginx 8200 返回 500 且 EchoMimic 日志无请求时，回看 nginx_echomimic.conf 头注释的 /var 磁盘满坑——配置已内置 proxy_request_buffering off，但老部署可能没更新这份配置。
