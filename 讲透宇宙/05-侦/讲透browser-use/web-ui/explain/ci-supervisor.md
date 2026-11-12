# build.yml + supervisord.conf 精讲——双架构发布流水线与容器内六进程守护

> 源码：`/usr-data/data2/repos/browser-use/web-ui/.github/workflows/build.yml`（124 行）+ `supervisord.conf`（79 行）
> 图谱层位：L10 CI 多架构发布流水线 / L09 容器镜像与进程编排

## ① 角色定位

两个文件分踹镜像的"生"与"活"：`build.yml` 在 GitHub release 发布或 push main 时，构建 amd64/arm64 双架构镜像并以 digest-then-manifest 两段式发布到 ghcr.io（build.yml:3-7、47-57、116-120）；`supervisord.conf` 则是容器 PID 1 的配置单（Dockerfile:89 的 CMD），按优先级拉起 Xvfb→VNC→noVNC→WebUI 六个进程（supervisord.conf:8-80）。它们与 docker-deploy 篇构成完整闭环：CI 产出镜像 → 镜像内 supervisor 定义运行时形态。

## ② 内部结构

**build.yml 双 job**：

- `build`（build.yml:13-71）：matrix 双平台 `fail-fast: false`（16-20，一个架构挂掉不影响另一个出 digest）；Prepare 步把 `linux/amd64` 规整成 `linux-amd64` 作 artifact 名（22-25）；随后 docker/metadata-action@v5 取标签、login-action 登 GHCR（27-39）、QEMU+Buildx 备好跨架构工具链（41-45）；核心是 build-push-action@v6 以 `outputs: type=image,push-by-digest=true` **只按 digest 推送不打 tag**（47-57），digest 写空文件存 artifact（59-71，retention 1 天）。
- `merge`（73-124）：下载两架构 digest 合并（78-83）、二次跑 metadata 拿 `type=ref/semver` 系列 tag（95-105）、"Docker tags" 步用 jq 拼 `-t` 串并对空标签兜底打 `github.ref_name`（107-114）、`docker buildx imagetools create` 把两个 digest 组装成单一 manifest list 推出（116-120）、最后 inspect 验证（122-124）。

**supervisord.conf 六 program**（priority 即启动序）：`xvfb`（p100，`:99` 屏 + GLX 扩展，8-18）、`vnc_setup`（p150，一次性写 vncpasswd，`autorestart=false`，20-28）、`x11vnc`（p200，睡 5 秒等 X 再起、`depends_on=vnc_setup,xvfb`，30-42）、`x11vnc_log`（p250，tail -f 日志，44-54）、`novnc`（p300，睡 5 秒等 VNC 再起，56-66）、`webui`（p400，`python webui.py --ip 0.0.0.0 --port 7788`，68-80）。全局段 `nodaemon=true` + 日志全指 `/dev/stdout` 且 `maxbytes=0`（1-6），保证前台运行、日志直通 `docker logs` 且不轮转。

## ③ 外部连接

- **TARGETPLATFORM 贯通**：build.yml 把 matrix.platform 作为 build-args 传给 Dockerfile（build.yml:55-56 → Dockerfile:4），compose 侧同名变量（docker-compose.yml:8-9）与之呼应。
- **GHCR 命名**：`ghcr.io/${{ github.repository }}`（build.yml:10），登录凭据是内置 `secrets.GITHUB_TOKEN`（39、90）——零配置发布。
- **supervisord 的环境变量消费**：`%(ENV_RESOLUTION)s`（supervisord.conf:9）与 `%(ENV_VNC_PASSWORD)s`（21）直接读容器 env，来源是 compose 透传（docker-compose.yml:60-65）——CI 不参与，纯运行时。
- **webui 进程**：directory=/app（supervisord.conf:70），与 Dockerfile WORKDIR 一致；`startsecs=3`/`startretries=3` 给 Gradio 冷启动留余量。

## ④ 数据流

发布流：release/push main 触发 → 两架构并行构建（各自产 digest）→ digest 文件作为 artifact 汇入 merge job → imagetools create 引用 `repo@sha256:...` 组合出带版本/分支 tag 的 manifest list → inspect 输出最终架构清单。运行流：容器启动 → supervisord 按 priority 升序 spawn：Xvfb 先就位（startsecs=3）→ vncpasswd 落 `~/.vnc/passwd` → x11vnc 挂 :99 出 5901 → 日志 tail 起来 → noVNC 代理 6080 → webui 最后起 7788。进程死亡由 `autorestart=true` 就地复活，只有 vnc_setup 例外（一次性任务，失败即留待重启容器）。

## ⑤ 设计决策与取舍

- **digest 两段式**：多架构如果直接在 matrix 里打 tag，两个 job 会互相覆盖对方的 tag——按 digest 推送再合并 manifest 是 Docker 官方文档推荐的标准解法，本文件是其忠实实现（含空文件存 digest 的技巧）。
- **fail-fast: false**：arm64 构建慢且偶发宿主问题，放行单架构出片可保 amd64 用户不受牵连。
- **supervisor 无依赖树的补偿**：supervisor 不支持进程依赖，只能用 priority 排序 + `sleep 5`（supervisord.conf:31、57）+ `startsecs`/`startretries`（38-39、64-65）拼出"等上游就绪"的伪依赖；`depends_on` 只控制启动顺序，不保证端口 ready。
- **日志策略**：x11vnc 先写 `/var/log/x11vnc.log` 再由独立 program tail 出来（31 与 45），因为 x11vnc 自身 `-o` 重定向与 supervisor 的 stdout 捕获不兼容——多一层 tail 进程换日志可见性。
- **webui 放 p400**：即使前面桌面栈未齐 webui 也会照起（Gradio 不依赖 X），用户先见 UI 后见直播，体验优先。

## ⑥ 新人提示（坑/勘误）

1. **inspect 依赖隐藏环境变量**：build.yml:124 用的 `DOCKER_METADATA_OUTPUT_VERSION` 正常路径由 metadata-action 自动导出；仅当标签全空时才由 111 行手写 `GITHUB_ENV`——两条路径都要在心里有数，改 workflow 时别删兜底步。
2. **merge 的 tags 兜底**：jq 分支（110-113）只在 metadata 输出空 tags 时触发（如非 semver 的裸 push），平时静默。
3. **sleep 5 是竞态赌注**：慢宿主上 5 秒可能不够 Xvfb 起 X socket，x11vnc 首次失败靠 `startretries=10` 硬重试补——改分辨率或加负载时若 VNC 起不来，先看这里。
4. **healthcheck 与 autorestart 双保险但不同层**：compose 探 5901 决定容器级重启（docker-compose.yml:76-80），supervisord 的 autorestart 决定进程级复活——前者动作粗得多。
5. **build.yml 不跑任何测试**：发布流水线零质量门，主线保护全靠 PR 习惯——想加 CI 检查需另起 workflow，别指望这一条。
