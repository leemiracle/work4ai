# 12 · Infra 与文档：容器编排、运维脚本与文档代差考古

## 角色定位

本篇收尾三个"工程外围"系统：`docker/`（1303 行编排资产：双 compose + 双 nginx 反代 + 独立 provisioner 镜像）、`scripts/`（9 个 shell + 2 个 Python 的本地运维入口）、`backend/docs/`（18 篇设计文档）。它们回答的问题是同一组的另外两面——"这套双进程系统怎么部署进容器/集群"与"写下的架构认知哪些还作数"。第三面尤其值得认真：DeerFlow 的文档呈现清晰的三方代差，读错一代就会被路径漂移带进沟里。

## 内部结构

**docker/ 三件套。** ① `docker-compose.yaml`（156 行，生产版）：gateway/langgraph/frontend/nginx 四常驻服务 + provisioner 可选 profile（`docker-compose.yaml:125-127`）；langgraph 服务用 `langgraph dev` 跑生产——`:89-90` 的 TODO 注释实证这是许可证规避的临时态（langchain/langgraph-api 商业镜像待 license），`:96` 是完整 command。② `docker-compose-dev.yaml`（189 行，开发版）：目录直挂开发流，`gateway-venv` 具名卷保住镜像内构建的 .venv 不被 backend/ 整目录挂载遮蔽（`:116-118`），这是"代码热挂载 + 依赖保卷"的经典 trick。③ `docker/provisioner/`：独立 FastAPI 编排器（app.py 515 行 + 极简 Dockerfile），每个 sandbox_id 一个 Pod + NodePort Service（`app.py:214` 的 `_build_pod`、`:312-325` NodePort manifest），挂载点 `/mnt/skills`（`app.py:275`）与 `/mnt/user-data`（`app.py:280`）跟 harness 虚拟路径系统同名对齐。

**nginx 双反代。** `nginx.conf`（容器版，230 行）三 upstream：gateway/langgraph/frontend（`:21`-`29`）；provisioner 路由用请求时变量解析——`set $provisioner_upstream provisioner:8002` + `proxy_pass http://$provisioner_upstream`（`nginx.conf:201-202`），配合 `resolver 127.0.0.11`（`nginx.conf:18`，Docker 内嵌 DNS）。这是为了 provisioner 属可选 profile：默认 upstream 写法会在其不在线时让 nginx 拒绝启动，变量写法把解析推迟到请求一刻。`nginx.local.conf`（本地版）两处实质差异：upstream 指向 127.0.0.1 而非 Docker 服务名（`nginx.local.conf:18`）、无 provisioner 路由块，日志走文件而非 stdout（`:14`）。

**scripts/ 九 shell。** `serve.sh`（本地全栈起服）、`deploy.sh`/`docker.sh`（生产/开发容器编排）、`start-daemon.sh`（nohup 守护）、`check.sh`+`check.py`（依赖体检）、`config-upgrade.sh`（配置迁移）、`cleanup-containers.sh`、`wait-for-port.sh`（四级端口探测）、`tool-error-degradation-detection.sh`（工具降级检测）。

## 外部连接

**provisioner 是纯部署单元。** app.py 全部依赖为 fastapi/kubernetes/pydantic/urllib3，零仓内 import——与 harness 无代码耦合，仅经 HTTP + K8s API 交互（`:181` 的 `app = FastAPI(title="DeerFlow Sandbox Provisioner")` 是唯一身份锚）。生产 compose 给它挂宿主 `~/.kube/config` 只读（`docker-compose.yaml:133`）并改写 `K8S_API_SERVER=https://host.docker.internal:26443`（`:141`）——kubeconfig 里的 127.0.0.1 从容器内不可达，必须指向网关别名。

**DooD 链路的环境变量桥。** backend 容器内跑 docker CLI（backend/Dockerfile:20 从官方 docker:cli 镜像 COPY 而非 apt 装），宿主 skills 目录经 `DEER_FLOW_HOST_SKILLS_PATH` 注入（`docker-compose-dev.yaml:131`、`:167`），由 `deploy.sh:37-39` 导出的 `DEER_FLOW_REPO_ROOT` 推导——沙箱容器再挂这份宿主路径到 `/mnt/skills`，三级路径翻译全靠这两个变量对齐。AIO 容器侧的隐患明写在代码里：`local_backend.py:230` 给 Docker 加 `--security-opt seccomp=unconfined`，牺牲系统调用过滤换兼容性。

**脚本与 config 的弱类型接口。** `deploy.sh:105` 的 `detect_sandbox_mode` 用 awk 区块扫描 config.yaml 的 sandbox.use/provisioner_url 判 local/aio/provisioner 三态——**不 import YAML**、按缩进文本解析，与 `docker.sh:18` 的同名函数构成双实现。两处逻辑一旦与 pydantic schema 演进不同步就会误判模式（有 test_docker_sandbox_mode_detection.py 回归测试兜底）。

## 数据流

一次 `make dev` 的完整部署判定：deploy.sh 先 `detect_sandbox_mode`（`:162` 调用）读 config.yaml → 决定是否拉起 provisioner profile → compose 起四服务 + 可选 provisioner → nginx 按环境选配置（dev compose 的 `NGINX_CONF` 注释称默认 local 版 `docker-compose-dev.yaml:60-61`，volume 实际默认挂容器版 `./nginx/${NGINX_CONF:-nginx.conf}`（`:69`）——注释与配置漂移，上游笔误）→ frontend 打 `/api/langgraph/*` 进 langgraph、其余 `/api/*` 进 gateway。

provisioner 数据流独立成环：backend 经 nginx 变量路由打到 provisioner:8002 → `create_sandbox`（`app.py:373`）两处容忍 409 AlreadyExists 保证幂等（`app.py:400`）、Service 失败回滚 Pod 防孤儿资源 → 返回 `{NODE_HOST}:{NodePort}` 直连地址（`app.py:194`）→ backend 此后绕过 provisioner 直打沙箱 Pod。

## 设计决策

**① 供应链三设计 vs 裸 pip 弱项。** backend/Dockerfile 三处强化：NodeSource 经 keyring 签名安装（`:12-14`）、docker CLI 从官方镜像 COPY（`:20`）、uv 从钉版本镜像 `ghcr.io/astral-sh/uv:0.7.20` COPY（`:23`），全部规避 curl|sh 式不可信远程执行。对照 provisioner/Dockerfile 的 `RUN pip install --no-cache-dir`（`:9`）无锁文件无版本钉死——主镜像 uv sync 锁定 vs 编排器裸 pip，同一仓库两种供应链强度，provisioner 因"只编排不在容器内跑用户代码"被豁免。主 Dockerfile 也非完美：`:28` 注释写 "Copy frontend source code" 实际 COPY 的是 backend（上游注释笔误）。

**② 中间态生产的自觉。** 用 dev server 跑生产（`:96`）+ TODO 注释留档，而不是悄悄将就——比"看似生产级实则 dev"的沉默状态诚实得多。

**③ 文档三方代差考古（本篇核心甄别）。** backend 文档分三代：旧代 `backend/src/` 布局残留在 CONTRIBUTING.md 与 README.md 的 Project Structure 章节（磁盘不存在该目录）；中间代路径漂移散落在 docs/——`ARCHITECTURE.md:161` 引 `sandbox/local.py`（实际在 `sandbox/local/local_sandbox.py`）、`ARCHITECTURE.md:267` 引 `mcp/manager.py`（实际拆成 mcp/client.py+tools.py+cache.py）、`AUTO_TITLE_GENERATION.md:188`/`:247` 与 `TITLE_GENERATION_IMPLEMENTATION.md:16` 三处引 `agents/title_middleware.py`（实际在 agents/middlewares/ 下）——docs 合计可数五处路径漂移。**当代唯一权威是 backend/CLAUDE.md**：packages/harness + app 双层布局、11 项中间件链、双进程架构全部与磁盘一致；backend/AGENTS.md 实为对 CLAUDE.md 的 @path 转发（还带 architeture 拼写笔误）。读文档的正确姿势：CLAUDE.md 定基准，docs/ 当历史设计意图读，遇路径一律以磁盘为准。

**④ 旧名残留无害化。** `serve.sh:3` 文件头注释仍写 "start.sh"（文件已更名）；工具降级检测脚本用 heredoc Python 直接 import lead_agent 的私有函数 `_build_middlewares`（下划线 API 被检测脚本消费）——运维脚本与主代码的耦合松散但真实存在，重构 lead_agent 时这两个脚本会被波及。

## 新人提示

- 部署排障第一步永远是 `detect_sandbox_mode` 的输出：三态判定错则 provisioner/nginx 路由全错；模式对了再看 nginx 变量路由（`nginx.conf:201`）与 kubeconfig 改写（`docker-compose.yaml:141`）。
- 改 compose 或挂载后容器内 venv "消失"，是目录挂载遮蔽——dev compose 的 gateway-venv 卷（`:118`）就是解药，重建卷即可，别在容器里手动 pip。
- 读任何 backend/docs/ 文档先核对路径代差五处清单；引用文档结论前用 CLAUDE.md 或源码复核一遍，否则极易把 `mcp/manager.py` 这类不存在的路径写进自己的设计稿。
- provisioner 容器只装了 curl 一个系统包（健康探针用），想进去调试带不了工具——调试靠 K8s API 侧观察，别指望 exec 进容器。
- 加新运维入口优先挂 Makefile target（仓根 Makefile 已收敛 19 个 target），避免 scripts/ 再膨胀；shell 里解析 YAML 一律学 config-upgrade.sh 的 heredoc Python（`:39-40` 起）而不是 awk 文本扫描——后者已有双实现漂移的前科。
