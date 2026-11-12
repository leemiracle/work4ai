# Dockerfile + docker-compose.yml 精讲——一条命令拉起的"带桌面直播"浏览器工作站

> 源码：`/usr-data/data2/repos/browser-use/web-ui/Dockerfile`（89 行）+ `docker-compose.yml`（80 行）
> 图谱层位：L09 容器镜像与进程编排

## ① 角色定位

这两个文件回答一个问题：**不给用户装 Python、不给他装 Chrome、也不强迫 headless**——`docker compose up` 之后，得到一个 7788 端口的 WebUI、一个 6080 端口的 noVNC 网页直播（浏览器里看 agent 操作浏览器）、5901 传统 VNC 口与 9222 Chrome 调试口。Dockerfile 负责"单镜像自足"（Python 3.11-slim + X11 桌面栈 + Chromium + Node + noVNC，Dockerfile:1-89），compose 负责"环境变量面 + 资源边界"（20 余个 LLM 密钥端点、显存级 shm、健康检查，docker-compose.yml:15-80）。

## ② 内部结构

**Dockerfile 六段**：

1. 系统依赖（Dockerfile:8-48）：除 curl/git/vim 外重点是 X11 桌面栈——`xvfb`（虚拟帧缓冲）、`x11vnc` + `tigervnc-tools`（VNC 服务与密码工具）、`supervisor`（进程守护）、三类字体（liberation/noto-color-emoji/unifont，emoji 渲染是网页 agent 的刚需）。
2. noVNC（Dockerfile:51-53）：`git clone` noVNC 与 websockify 并软链 `vnc.html → index.html`——没有官方 apt 包时的标准做法。
3. Node.js 20（Dockerfile:55-64）：走 NodeSource 密钥环 + apt 源，并 `node -v && npm -v && npx -v` 自验——Playwright 的 driver 需要 Node。
4. Python 依赖（Dockerfile:70-71）：先单拷 requirements.txt 再 pip install，保住层缓存。
5. Playwright Chromium（Dockerfile:74-78）：`PLAYWRIGHT_BROWSERS_PATH=/ms-browsers` 隔离存放，`playwright install chromium` 不带 `--with-deps`（系统库已由第 1 段装齐）。
6. 收尾（Dockerfile:81-89）：COPY 全码、落 supervisord.conf、EXPOSE 7788/6080/5901/9222、CMD 交给 supervisord。

**compose 五块**：build args（`TARGETPLATFORM` 缺省 linux/amd64，docker-compose.yml:8-9）、ports 四口（10-14）、environment 三组——LLM 密钥/端点（17-40）、应用开关（43-44）、浏览器与显示（47-62）、资源与运维（volumes 挂 `/tmp/.X11-unix`、`shm_size: "2gb"`、`cap_add: SYS_ADMIN`、tmpfs、healthcheck，67-80）。

## ③ 外部连接

- **IN_DOCKER 透传链（本篇核心，且实测断裂）**：上游 browser_use 0.1.48 定义 `IN_DOCKER = os.environ.get('IN_DOCKER', 'false')...`（browser/browser.py:39）与 `CHROME_DOCKER_ARGS = ['--no-sandbox', '--disable-gpu-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--no-xshm']`（browser/chrome.py:35-42）；web-ui 的 CustomBrowser 在拼 Chrome 启动参数时引用两者（custom_browser.py:69）。但**全仓 Dockerfile/compose/supervisord/.env.example 无一处设置 IN_DOCKER**（grep 实证零命中）——这条上游预留的透传链在本项目镜像里是死路。
- **VNC 密码三文件一致**：`.env.example:71`、`docker-compose.yml:65`（`${VNC_PASSWORD:-youvncpassword}`）、`supervisord.conf:21`（`%(ENV_VNC_PASSWORD)s` 进 vncpasswd），默认值三处同为 `youvncpassword`，README:145-146 明文公示。
- **入口链**：compose 未写 command → 走 Dockerfile:89 的 supervisord → 由 supervisord.conf:69 起 `webui.py --ip 0.0.0.0 --port 7788`；webui.py:1-2 在模块顶层 `load_dotenv()`（COPY . . 带进来的 .env 生效于容器内）。
- **运行时反哺**：compose 的 `BROWSER_PATH=`/`USE_OWN_BROWSER=false`（47-51）对应 browser_settings_tab.py:55 的 strtobool 初值；`BROWSER_DEBUGGING_PORT=9222`（49）对应 EXPOSE 的调试口。

## ④ 数据流

以 `docker compose up` 为起点：compose 读宿主 `.env` → 按 `${VAR:-default}` 折算后注入容器环境 → supervisord 用 `%(ENV_RESOLUTION)s`/`%(ENV_VNC_PASSWORD)s` 把显示分辨率与 VNC 密码继续传给 Xvfb 与 vncpasswd（supervisord.conf:9、21）→ Xvfb 在 `:99` 起虚拟屏（DISPLAY=:99，compose:56）→ x11vnc 把 :99 投到 5901 → noVNC 把 5901 转 WebSocket 到 6080 → webui 起 7788。浏览器视像流：Chromium 画到 Xvfb → VNC → 用户浏览器 6080 页；agent 视像流：headless 模式下另走 browser_use_agent_tab.py:660-682 的截图直播进 Gradio 页。

## ⑤ 设计决策与取舍

- **不用 --no-sandbox 的补偿方案**：上游注释明言 "--no-sandbox ... otherwise we need cap_add: SYS_ADMIN"（chrome.py:38）；本项目既然没开 IN_DOCKER，就选择保住 Chrome 自带沙箱、用 `cap_add: SYS_ADMIN`（compose:72-73）+ `shm_size: 2gb`（71，绕开 75MB 默认共享内存不足）+ tmpfs `/tmp`（74-75）三件套兜底——安全性换权限面，是深思熟虑而非疏漏。
- **显示参数化**：RESOLUTION/RESOLUTION_WIDTH/RESOLUTION_HEIGHT 三变量（60-62）供 Xvfb 与窗口逻辑分别消费。
- **healthcheck 探 5901 而非 7788**（76-80）：VNC 链是五级进程里最脆弱的一环（Xvfb→passwd→x11vnc→noVNC），探它最能代表"桌面栈整体活着"；webui 挂了有 supervisord autorestart 兜底。
- **单阶段构建**：牺牲镜像体积换取 Dockerfile 可读性，配合 CI 侧 buildx 缓存。

## ⑥ 新人提示（坑/勘误）

1. **默认 VNC 密码是公网裸奔**：`youvncpassword` 三文件同步默认，公网开放 6080/5901 前必须改 `.env`；healthcheck 用的 `nc` 来自 apt 的 netcat-traditional（Dockerfile:10）。
2. **/tmp/.X11-unix 挂载存疑**：X server 是容器内的 Xvfb，并非复用宿主 X——该 volume 属防御性/历史配置，删掉通常无害；真正依赖宿主的是无。
3. **TARGETPLATFORM 缺省 amd64**：arm 宿主直接 `docker build` 会拿 amd64 预期（其实 Buildx 会自动覆盖），只有绕过 buildx 时才咬人。
4. **EXPOSE 9222 是调试口不是必须口**：BROWSER_CDP（53）留空时无消费者，对外映射 9222 纯为远程调试便利，公网同样危险。
5. **`.env` 会被 COPY . . 打进镜像**：若在构建机上放了真实密钥的 .env，镜像即含密钥——发布镜像前须确认 .dockerignore 或使用 build-arg/运行期注入。
