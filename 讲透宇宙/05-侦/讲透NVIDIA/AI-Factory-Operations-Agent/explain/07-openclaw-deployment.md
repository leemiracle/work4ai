# 07 · templates/openclaw.yaml：OpenClaw 主负载——chart 里最重的"装配流水线"

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`helm/mosaic-stack/templates/openclaw.yaml`（779 行 = Deployment + Service 两个资源）
> 协同文件：`templates/openclaw-seed-configmap.yaml`（163 行，播种内容的事实源）、`files/openclaw-seed/nemoclaw.json`（373 行 Helm 模板化 JSON）

## 一、角色定位

整个 chart 的产出物里，`openclaw.yaml` 是唯一"活着"的 agent 进程：单副本 Deployment（`openclaw.yaml:17` 的 `replicas: 1`）跑 OpenClaw gateway（容器命令 `node /app/dist/index.js gateway run`，`openclaw.yaml:509`），对外以 ClusterIP Service 暴露 18789 端口（`openclaw.yaml:650-778`）。所有 extension/skill/persona 文件都不是打进镜像的，而是由这份模板在**部署期**从 ConfigMap 播种进持久卷——这是它 779 行的来源：主容器定义只占约 200 行，其余 500 多行是 9 个 initContainer 组成的装配流水线。

模板第一行就是双重闸门：`{{- if and .Values.modules.execution.enabled .Values.openclaw.enabled }}`（`openclaw.yaml:4`）——execution 模块关了或 openclaw 显式关了，Deployment 与 Service 整体消失。这个写法与 seed ConfigMap 的闸门完全同构（`openclaw-seed-configmap.yaml:4`），保证播种内容与消费者同生同灭。

与之配套的 `openclaw-seed-configmap.yaml` 是内容侧事实源：extension 源码、SKILL.md、persona 文档全部经 `.Files.Get` 内联进 ConfigMap（如 `openclaw-seed-configmap.yaml:29-30` 无条件内联 `gpu-networking/SKILL.md`），`agent-documentation.tar.gz` 走 `binaryData` + base64（`openclaw-seed-configmap.yaml:12`）。两份模板一装一载，构成"内容-装配"分离。

## 二、内部结构

### 9 个 initContainer 的装配序列

按 Pod 内执行顺序（k8s 保证 initContainer 串行）：

1. **install-kubectl**（`openclaw.yaml:41-70`，仅 `modules.kubernetes.enabled`）：从 `dl.k8s.io` 下载 kubectl，按 `uname -m` 选 amd64/arm64 并用 values 里钉死的 sha256 校验（`openclaw.yaml:51-58`），`chmod 0555` 落到共享 `runtime-tools` emptyDir。网络工具装在启动期而不是镜像里，换来"镜像不含 kubectl、版本由 chart 值统一管理"。
2. **install-openssh-client**（`openclaw.yaml:71-100`）：从 alpine/musl 镜像里**搬运** ssh/scp/sftp 二进制和 `ld-musl` loader/libcrypto/libz，再为每个命令写一个 wrapper 脚本显式指定 `--library-path`（`openclaw.yaml:86-90`）。remote-ssh 插件因此能在任意基础镜像里获得静态化 SSH 客户端。
3. **init-perms**（`openclaw.yaml:101-110`）：唯一 root 容器，只做 `chown 1000:1000`——PVC 首次创建时属主是 root，node 用户写不进。
4. **init-config**（`openclaw.yaml:111-281`）：核心播种器，见下节。
5. **init-remote-ssh-credentials**（`openclaw.yaml:282-308`，条件 `modules.edit.enabled && modules.edit.ssh.enabled`）：把用户 Secret 里的私钥/known_hosts 拷进 `medium: Memory` 的 emptyDir（`openclaw.yaml:742-744`），权限收紧到 0400/0444。**私钥永不落盘**——emptyDir 的 Memory 卷随 Pod 消亡。
6. **init-slack-plugin**（`openclaw.yaml:309-330`）：`plugins install @openclaw/slack@版本 --force` + 执行 `slack-enterprise-grid-patch.mjs` 补 Enterprise Grid 事件订阅。
7. **init-web-search-plugin**（`openclaw.yaml:331-357`，Brave 专属）：npm tgz 下载 + sha256 校验 + 解包安装。
8. **init-bcm-docs**（`openclaw.yaml:358-380`，BCM 启用时）：从 mosaic-ui 镜像里的 `/opt/nemoclaw/bcm-docs.tar.gz` 解出 BCM 手册到 workspace——**部署期零网络**，手册随镜像走。
9. **install-openshell-assets / init-openshell-plugin**（`openclaw.yaml:381-504`）：下载 OpenShell CLI（sha256 校验）并写一个 46 行的 `sandbox create` 包装脚本（`openclaw.yaml:402-448`）——后台起 create、轮询 `sandbox exec --name ... -- true` 最多 180 秒等 SSH 就绪（`openclaw.yaml:434-442`），解决"create 返回了但沙箱还没法用"的竞态。

### init-config：幂等重建 workspace

播种脚本先**清场**再装配：`rm -rf` 九个 extension 目录、八个 skill 目录和三个散装 ts 文件（`openclaw.yaml:121-141`），然后按模块开关逐个 `mkdir + cp /seed/...`。清场-重建（而非增量）是有意的：升级时被禁用模块的残留文件必须消失，PVC 里的旧内容不可信。`/seed` 就是挂载的 openclaw-seed ConfigMap（`openclaw.yaml:726-728`）。

两个结构性细节：

- **skills 的 references 目录按内容寻址**：`{{ range .Files.Glob "files/openclaw-seed/skills/**/references/**" }}` 生成 `skill-reference-{sha256}` 键（`openclaw-seed-configmap.yaml:31-34`），装配侧先确认该 skill 的 SKILL.md 已就位才拷 references（`openclaw.yaml:264-267`）——孤儿引用不会落盘。
- **modules.edit 条件块三处联动**：extension 播种（`openclaw.yaml:165-172`）、initContainer（`openclaw.yaml:282-308`）、卷与挂载（`openclaw.yaml:709-713`、`733-745`）。改 edit/ssh 相关逻辑时四处必须一起动，漏一处就是"插件在、密钥不在"的哑弹。

### 主容器与配置注入

gateway 容器是全 chart 环境变量最密集的点：`OPENCLAW_GATEWAY_TOKEN` 走 chart 管理的 Secret（`openclaw.yaml:525-529`）；managed/external MCP server 的 secretHeaders 统一编译成 `MOSAIC_MCP_{sha256前16位大写}` 环境变量名（`openclaw.yaml:534,544`），与 nemoclaw.json 里的 `${MOSAIC_MCP_...}` 占位符（`nemoclaw.json:8-9`）精确咬合——**secret 值从不进 ConfigMap，只经 env 注入**。观测、Slack、Brave、BCM、诊断、iraop、Slurm evidence 的凭据同样全部 `secretKeyRef`（`openclaw.yaml:566-649`）。

容器安全面：`readOnlyRootFilesystem: true`（`openclaw.yaml:676`），可写区只有 PVC 里的 `/home/node/.openclaw` 和经 subPath 挂到 `/tmp` 的同一块 PVC（`openclaw.yaml:683-685`）；探测用 exec 跑 node 单行 HTTP 检查 `/readyz`、`/healthz`（`openclaw.yaml:653-664`）。

## 三、外部连接

- **PVC**：`openclaw-home` 挂 `openclaw-home-pvc`（`openclaw.yaml:723-725`），由 `templates/pvcs.yaml` 供给；workspace、persona、速记全部持久化于此——重建 Pod 不丢人格。
- **checksum 注解链**：`checksum/openclaw-seed: {{ include ".../openclaw-seed-configmap.yaml" . | sha256sum }}`（`openclaw.yaml:28`）把 seed ConfigMap 的**渲染产物**哈希进 Deployment 注解——任何 extension/skill/SKILL.md 改动都会改变哈希、触发滚动重启，无需改镜像标签。第二条 `checksum/bcm-auth-config`（`openclaw.yaml:29`）对 BCM token 的 secret 名/键/值三元组做同样的事。
- **nemoclaw.json → openclaw.json**：`tpl (.Files.Get "files/openclaw-seed/nemoclaw.json")`（`openclaw-seed-configmap.yaml:28`）把 373 行模板渲染进 ConfigMap 键 `openclaw.json`，装配脚本 `cp /seed/openclaw.json ~/.openclaw/openclaw.json`（`openclaw.yaml:213`）。文件名叫 nemoclaw、落盘叫 openclaw，是历史名残留（详见第 11 篇）。
- **Slack/HITL/审批链**：edit 模式与 Slack 审批人的联动校验在 `validation.yaml:16-26`，本模板只负责按开关装配文件。

## 四、数据流

一次升级的完整链路：开发者改 `files/openclaw-seed/extensions/bcm/index.ts` → helm upgrade 渲染时该文件内容进 seed ConfigMap → ConfigMap 变化改变 `checksum/openclaw-seed` 注解（`openclaw.yaml:28`）→ Deployment 滚动重建 → init-config 清场后重新 cp 全部模块（含新 bcm/index.ts）→ gateway 启动加载新插件。**_ConfigMap 是唯一内容通道，PVC 是唯一持久状态，镜像只是运行时**——三者各司其职，没有旁路。

Pod 内顺序：initContainer 串行装配（kubectl→ssh→权限→播种→凭据→插件→文档→openshell）→ gateway 启动 → readinessProbe 15 秒初延后开始探测 → Slack/Discord 等 channel 进程连接外部。

## 五、设计决策

- **播种优于打镜像**：extension 以 ConfigMap 明文分发，升级=改 chart 值+滚动重启，不需要 CI 构建镜像。代价是 ConfigMap 上限 1MiB——agent-documentation.tar.gz 走 binaryData 已经接近这个量级的实用边界，再大的资产必须换 ImageVolume/对象存储。
- **清场-重建保证禁用模块真消失**：增量播种会让"关掉的模块还在磁盘上继续被加载"成为可能，rm-then-cp 把幂等性做在最简单的地方。
- **openshell create 包装脚本放在 initContainer 而非镜像**：等待 SSH 就绪的 180 秒轮询逻辑（`openclaw.yaml:434-442`）属于 chart 层的部署关切，升级它不需要动 OpenShell 发版节奏。
- **`strategy: Recreate`**（`openclaw.yaml:21-22`）：单副本+RWO PVC 的标准选择，RollingUpdate 会在新旧 Pod 间争抢卷。

## 六、新人提示

- 改 extension 逻辑只需动 `files/openclaw-seed/`，**不要**直接改本模板；本模板只管"哪些文件进 ConfigMap、哪些文件落盘"两张清单，且这两张清单（`openclaw-seed-configmap.yaml` 的 if 块与 `openclaw.yaml` 的 cp 块）必须同步维护。
- ⚠️ **grafana 模块的播种是断头的**：`grafana.SKILL.md` 与 `grafana/index.ts` 会进 seed ConfigMap（`openclaw-seed-configmap.yaml:97-100,155-162`），但 init-config 只 rm 不装——cp 清单里没有 grafana（`openclaw.yaml:121-141` 的 rm 覆盖了它，后续 cp 却从未出现），nemoclaw.json 的 skills 白名单也不含 grafana（`nemoclaw.json:67-74`）。在产的 Grafana 工具在 observability 插件的 `grafana.ts` 里（`openclaw.yaml:238` 装配）。给 grafana 模块加功能前先确认你要不要先接通这条播种链。
- `automountServiceAccountToken` 按 `modules.kubernetes.enabled && kubernetes.local.enabled` 动态决定（`openclaw.yaml:32`）——k8s 模块关闭时 Pod 无 ServiceAccount 令牌，不要默认它总在。
- 调试装配问题先看 init-config 日志：脚本 `set -eu`（`openclaw.yaml:118`），任何一步失败容器直接 CrashLoop，`kubectl logs <pod> -c init-config` 即现场。
- ⚠️ 甄别记录：任务简报"779 行 / modules.edit 条件块 / Files.Get 内联 / required fail-fast / checksum 注解"逐项与源码吻合；补充核实——required fail-fast 在本模板不存在，它在 seed ConfigMap（`openclaw-seed-configmap.yaml:12` 的 agent-documentation）与 ingress 模板（`afoa-inference/templates/ingress.yaml:19-20`）里。图谱 summary 与源码一致。

（行号锚基于当前工作树源码逐条核实。）
