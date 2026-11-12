# 12 · chart-render.test.mjs + Kind 三环境 + spdx/死测试：chart 的行为契约防线

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`helm/mosaic-stack/tests/chart-render.test.mjs`（1312 行，80 个 test）、`tests/kubernetes-kind-e2e.sh`（225 行）、`tests/remote-ssh-kind-e2e.sh`（221 行）、`tests/setup-kind-session-access-targets.sh`（HITL 环境）、`utils/spdx.test.mjs`（33 行）、`tests/test_bcm_docs.py`（67 行，死测试）
> 协同文件：`helm/afoa-inference/tests/chart-render.test.mjs`（59 行）、`.github/workflows/ci.yml`

## 一、角色定位

AFOA 的测试体系分三层，本篇覆盖后两层：

1. **单元层**（第 10/11 篇已见）：mcp-oauth-proxy、mosaic-mcp、observability 各自的 `.test.mjs`，测纯逻辑。
2. **渲染契约层**——`chart-render.test.mjs`：**每个测试都是一次真实的 `helm template` 执行**（`render()` 封装，`chart-render.test.mjs:76-80`），对渲染产物做文本/结构断言。它不跑 K8s，却把"这个 chart 装出来到底长什么样"钉死成 80 条可执行规范——改模板不改测试（或反之）在 CI 立刻爆。
3. **E2E 层**——Kind 双脚本：`kubernetes-kind-e2e.sh` 起两个 Kind 集群验证 k8s 插件的双集群访问与故障路径；`remote-ssh-kind-e2e.sh` 起一个集群验证 SSH 编辑通道全链；`setup-kind-session-access-targets.sh` 则是**人机协同（HITL）演练环境**的搭台脚本。

`spdx.test.mjs` 是横切合规层：全仓源文件 SPDX 头与命名规范。`test_bcm_docs.py` 是反面教材——一个引用悬空、CI 永不执行的死测试。

## 二、内部结构

### chart-render.test.mjs：1312 行 80 测的行为契约

按 `grep -c "^test("` 实测 **80 个 test 块**（任务简报"50+ 断言"实为低估）。基础设施三件：`render()`（`:76-80`，`helm template mosaic <chart> --namespace mosaic-test` + 任意 --set）、`renderDiagnostics()`（`:82-88`，预置 BCM/diagnostics 五个 --set 的便捷封装）、`configMapBlock()`（`:18-28`，从渲染文本里按 `key: |` 前缀切出 ConfigMap 块并反缩进——**文本级解析**是全文件的基调，不引 YAML 库）。

80 个测试的主题分布（按行号段清点）：

- **启动装配**（`:30-65`）：三个 approval hook 必须在启动清单里、**managed plugins 先删后装**（`:45-51` 遍历八个 extension 名断言 rm 路径存在——对应第 07 篇 init-config 的清场-重建）。
- **凭据面**（`:165-310`）：Hardware Agent 单一凭据双向共享（`:165`）、UI 机器凭据单源（`:266-296`）、chart 生成 Research Secret（`:377`）——每条都在防"同一个凭据两处定义"。
- **镜像纪律**（`:218-253`）：`renders only official OpenClaw and OpenShell runtime images`（`:218`）+ `pins every default runtime image`（`:233`）——供应链条款直接测试化。
- **profile 契约**（`:409-440`）：Super 单卡（`:409`）、Ultra 四卡（`:420`）、**废弃的 distributed 配置必须 fail**（`:429`，对应 `validation.yaml:73-75`）——渲染测试反向验证校验层。
- **edit/HITL 矩阵**（`:808-960`）：BCM admin 路径只在 edit 模式渲染（`:847`）、edit 关时适配器保持只读（`:874`）、edit 依赖校验（`:918`）——第 08 篇 validation 条款的镜像。
- **两个明星测试**值得单独讲：

**`preloads selected skill instructions from their authoritative files`**（`:1160-1173`）：对 gpu-networking/slurm 两个 skill，断言渲染出的 `AGENTS.md` **逐字包含** SKILL.md 源文件与全部 references 的内容（`:1165-1168` 直接 readFileSync 对比），且 `bootstrapMaxChars > instructions.length`（`:1171`）——预载预算必须真的装得下预载内容，防"配置说预载、长度截断吃掉"。

**`packaged product and GPU documentation installs locally...`**（`:1175-1235`，60 行最长）：这是一次**真执行**测试——`helm package` 打包 chart（`:1178`）→ 离线 values 全模块关闭渲染（`:1180-1184`）→ 从渲染产物手工解码 binaryData/data 还原 /seed 目录（`:1191-1204`）→ **切出 init-config 的 shell 脚本并在宿主机真跑**（`:1205-1209` 的 `execFileSync("sh", ["-eu", "-c", script])`）→ 断言：旧文档 skill 被删（`:1210`）、产品文档与 git 里 README/docs 逐字节一致（`:1213-1217`）、既有手工文档未被覆盖（`:1219`）、GPU 文档无外链且内部相对引用全部存在（`:1227-1230`）。一个测试跑通了"打包→离线安装→幂等→自包含"四重属性。

另有一处巧思：`preserves the Slurm evidence apiVersion after its SPDX header`（`:1126-1138`）——专门守护"SPDX 版权头插进 YAML 后不破坏首个 apiVersion 解析"，合规与渲染的交界事故预防。

### afoa-inference 版渲染测试（59 行 4 测）

`afoa-inference/tests/chart-render.test.mjs`：默认只出 GPU 负载+Service、不产 Secret（`:12`）；站点硬件/存储/凭据三件可独立配置（`:22`）；ingress 只路由 /v1 且引用站点 TLS（`:39`）；**缺认证或缺 TLS 的 install 必须在安装前 fail**（`:48`）——把 `values.yaml:13-15` 的"先建 Secret"约定与 `ingress.yaml:19-20` 的 required 变成可执行契约。

### Kind 三环境

**`kubernetes-kind-e2e.sh`（双集群）**：一个脚本起 `mosaic-kubernetes-local-e2e-*` 与 `mosaic-kubernetes-external-e2e-*` 两个 Kind 集群（`:30-31`），模拟"in-cluster + 外部注册集群"双目标。两集群各装渲染出的 rbac.yaml（local 侧带 edit 开关，`:52-54`）、各起一个 busybox 日志源 Pod（`:57`）；随后为 openclaw ServiceAccount 签 1 小时 token（`:61-62`）手工拼出两份 kubeconfig 灌成 Secret（`:67-108`）——完整复刻第 07 篇 `openclaw.yaml:189-212` 的 in-cluster 配置生成与 `:754-761` 的 external Secret 挂载形态。测试主体是 Pod 内 `node --experimental-strip-types /test/e2e.ts`（`:152`）跑真插件的 policy/runner；**负路径同样入测**：故意引用不存在的 `missing-external-kubeconfig` Secret，轮询断言 Pod 事件里出现 `secret ... not found`（`:196-225`）——"配置缺失时的失败形态"是被测试保护的行为。

**`remote-ssh-kind-e2e.sh`（SSH 通道）**：现场 `ssh-keygen` 生成客户端/主机两对 ed25519（`:42-45`），known_hosts 直写主机公钥，灌成两个 Secret；目标侧起 alpine sshd Pod。三个镜像全部 digest 钉死后 `docker save`→`ctr images import` 导入 Kind（`:36-38`）——E2E 也要供应链纪律。测试 Pod 用 openclaw 镜像真跑 remote-ssh 插件的 runner。

**`setup-kind-session-access-targets.sh`（HITL 演练）**：context 名直接叫 `kind-mosaic-hitl`（`:7`），起 `mosaic-hitl-node-a/b` 双目标节点（`:33,82`），SSH 密钥对双 Secret（`:24-25`）——这是给**人**用的环境：真 OpenClaw 起来后，审批流（Slack editUserIds / UI HITL）在这个集群上手动演练。它不是 CI 的一部分，算"第 2.5 层"。

### spdx.test.mjs 与死测试

`spdx.test.mjs` 两条：①17 类源码扩展的 git 跟踪文件，头 12 行内必须先版权行后许可行双 SPDX（`spdx.test.mjs:18-27`）；②**helm/ 目录外的 Markdown 禁止出现缩写 "BCM"**（`:29-33`）——公开文档用全称 "cluster manager"，品牌合规写进测试。

`test_bcm_docs.py` 是三层死法：`SCRIPT = parents[1]/"files/docs/download_bcm_docs.py"`（`test_bcm_docs.py:11`）**该文件在工作树不存在**（`ls files/docs` 报 No such file，且 `git log --diff-filter=D` 无删除记录=从未入库）；实测运行 `python -m unittest test_bcm_docs` 在模块加载期即 `FileNotFoundError`（`:15` 的 exec_module）；且 CI 命令 `node --test ...helm/mosaic-stack/tests/*.test.mjs`（`ci.yml:57`）的 glob **根本匹配不到 .py 文件**——悬空、跑不过、不被跑。对照组是同目录 `test_bcm_server.py`：它测的 `files/bcm-mcp-ssh-server.py` 真实存在，且在加载前手工构造全套假模块树塞进 `sys.modules`（`test_bcm_server.py:56-75`，FakeMCP/FakeBCMServer/空 bcm_mcp_tools 包），实测 5 测全绿——**同为 Python 测试，一个做对了隔离，一个是无人问津的尸体**。

## 三、外部连接

- CI 全景（`ci.yml:57-64`）：`node --test utils/*.test.mjs helm/mosaic-stack/tests/*.test.mjs tests/docs/*.test.mjs` + afoa-inference 一组——注意 **Kind E2E 不在 CI**（需要 docker/Kind 的环境自跑），`.py` 测试不在任何 CI job 里。
- 渲染测试 ↔ 模板：80 测就是 80 份模板行为的"客户"；第 07/08 篇的每个条件块几乎都能在这里找到对应断言（如 `:45-51` ↔ openclaw.yaml 清场、`:429` ↔ validation.yaml:73-75）。
- `configMapBlock` ↔ seed ConfigMap 的块格式：`key: |-` + 四空格缩进——若有人改 ConfigMap 缩进风格，一半渲染测试会先红。

## 四、数据流

CI 一次 PR 的验证流：lint/spdx（秒级）→ 80 渲染测（每次 render 都是独立 helm 进程，全量约分钟级）→ afoa 4 测 → docs 测。开发者本地加模块时：改模板 → 跑 `node --test helm/mosaic-stack/tests/chart-render.test.mjs` 看哪些行为契约被触碰 → 补/改测试 → （涉及 k8s 交互时）跑对应 Kind 脚本。Kind 脚本的产物（集群、Secret、测试 Pod）随脚本退出清理（`trap cleanup EXIT`，`kubernetes-kind-e2e.sh:20-25`），不留现场。

## 五、设计决策

- **渲染测试选文本断言而非对象断言**：`assert.match(output, /regex/)` 占绝对多数——渲染产物是 YAML 文本，锚定文本即锚定最终交付物，不引入解析层偏差；代价是断言脆（格式变化即红），但对"配置即产品"的 chart 这份脆正是保护。
- **真执行 init-config 脚本**（`:1209`）：把 shell 播种脚本当可执行规格测试——单元测试测不出 `set -eu` 下的次序错误，真跑一遍才是端到端。
- **E2E 负路径一等公民**：missing Secret 的失败形态（`:217-223`）被轮询断言——"错误信息是否可诊断"本身是产品属性。
- **Kind 双集群在一个脚本里**：外部集群的 kubeconfig 生成逻辑（`:87-105`）与生产 openclaw.yaml 的 external 挂载同构，测试环境逼真度优先于脚本简洁。

## 六、新人提示

- 加新模块的 checklist：模板条件块（第 07 篇）→ validation 条款（第 08 篇）→ **chart-render 断言**（本篇）——三件套缺一即"无契约的行为"。
- 别给 `.py` 测试文件用 `test_*.py` 命名就以为进了 CI——**当前 CI 只收 `.test.mjs` glob**（`ci.yml:57`）；要么改成 node 测试，要么明确它在 CI 之外的存在理由，要么删掉（test_bcm_docs.py 建议归档或删除，它的三个用例描述的下载器本仓已不存在）。
- 跑 Kind E2E 前确认 docker 与 kind 在 PATH（脚本可 `KIND_BIN/KUBECTL_BIN/HELM_BIN/DOCKER_BIN` 覆盖，`kubernetes-kind-e2e.sh:8-11`），全程需要外网拉 busybox/openclaw 镜像。
- 调试单条渲染测试：`node --test --test-name-pattern "edit mode" helm/mosaic-stack/tests/chart-render.test.mjs` 按名过滤，比全量快一个量级。
- ⚠️ 甄别记录：任务简报"1312 行 50+ 断言"——实测 **80 个 test 块**（`grep -c "^test("`），50+ 属保守下界。"test_bcm_docs.py 引用悬空死测试"经三重实证（文件不存在/FileNotFoundError 实测/CI glob 不匹配）；对照组 test_bcm_server.py 实测 5 测全绿。HITL 环境脚本为 `setup-kind-session-access-targets.sh`（context `kind-mosaic-hitl`，`:7`）。图谱 summary 与源码一致（其对 test_bcm_docs.py 已标注悬空警示）。

（行号锚基于当前工作树源码逐条核实。）
