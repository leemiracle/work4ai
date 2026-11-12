# AI Factory Operations Agent（AFOA）新人上手文档

> 依据知识图谱（312 节点/376 边/16 层/16 步导览，commit 47fdcc7）撰写，行号锚均经源码核实。

## 1. 一句话定位

AFOA 是 NVIDIA 开源的**部署专用 AI agents 治理 AI 工厂运维的实验性蓝图项目**——基于 NemoClaw/OpenClaw 搭代理化运维框架：专用 agent 跨集群系统（K8s/Prometheus/Grafana/Slurm/BCM）收集关联证据，产出根因摘要与建议，全程受治理可审计（README.md:10）。README.md:8 明示 experimental release，早期访问 chart 与镜像须受邀拉取（README.md:38）。形态=两个 Helm chart+一颗 OpenClaw 种子工作区，agent 的人格/技能/权限/工具全由种子驱动。

## 2. 仓库全景（16 层）

依赖走向：**治理文档（L01-03）定契约→种子（L04-05）定行为→插件（L06-08）定能力边界→独立服务（L09）补进程外桥→chart（L10-13）打包→测试（L14-15）守护→演示（L16）传播**。

1. **L01 治理文档**：README 蓝图+开源治理全套（DCO/IP 评审/4567 行许可清单）。
2. **L02 社区与 CI**：issue 表单；ci.yml 跑 node --test+helm lint 双 chart，docs.yml 部署 Sphinx 站。
3. **L03 文档站**：751 行 installation.md 总枢纽+安全模型/多租户/用例三核心文档。
4. **L04 人格与种子配置**：workspace 六件套+nemoclaw.json+Slack 幂等补丁。
5. **L05 运维技能库**：7 份 SKILL.md+三份 references（合计 10 个 markdown）。
6. **L06 访问治理插件**：automation-context/diagnostic-policy/mutation-ledger/automation-guard。
7. **L07 集群远程插件**：kubernetes 双级工具、remote-ssh、slurm、diagnostic-agent。
8. **L08 观测平台插件**：observability/grafana/dcgm/bcm/iraop。
9. **L09 独立服务**：bcm-mcp-ssh-server.py、mcp-oauth-proxy.mjs、slurm-evidence/server.mjs、utils/mosaic-mcp.mjs。
10. **L10 chart 骨架**：双 OCI 依赖、540 行 values 模块矩阵、3999 行 AgentSandbox CRD、vLLM 双 profile。
11. **L11 核心负载模板**：779 行 openclaw.yaml、种子 ConfigMap、vllm/validation/llm-compat。
12. **L12 界面与安全基线**：mosaic-ui/terminal/cluster-monitor、rbac、auth Secret 幂等。
13. **L13 afoa-inference 子 chart**：独立 GPU 集群示例 vLLM 部署。
14. **L14 单元与契约测试**：策略语义+源码级权限边界+chart 渲染契约三路守护。
15. **L15 Kind E2E**：双集群真跑 kubectl/SSH+最小面存储验证。
16. **L16 演示资产**：31 秒全合成宣传片管线。

## 3. 核心机制一：OpenClaw workspace 人格与技能库

agent 行为全部来自 `files/openclaw-seed/` 种子（经 configmap 打进工作区）：

- **workspace 六件套**：AGENTS.md 主提示词——每条消息必须可见回复、排查按预载 skill 证据序列推进（观察/候选解释/已验证原因分开）、不臆造硬件指标；**它是 Helm 模板**：`{{- if .Values.modules.edit.enabled }}` 按开关裁剪 Session Access Modes 节（workspace/AGENTS.md:29），`{{ range .Values.openclaw.bootstrapSkills }}` 注入预载技能（workspace/AGENTS.md:104），渲染点在 openclaw-seed-configmap.yaml:36 的 tpl。余下四件：SOUL.md 人格准则（会话无记忆、workspace 即持久记忆）、IDENTITY.md 身份卡、TOOLS.md 工具纪律、HEARTBEAT.md 心跳模板。
- **nemoclaw.json（373 行）**：网关与 agent 主配置——gateway 18789 端口 token 鉴权、主模型指向 `llm/<mosaic-stack.llmModel>`、sandbox 全走 openshell；**同为 Helm 模板化 JSON**：开头即 `{{- $managedMcpServers := dict -}}`，secretHeaders 经 sha256 截断映射 `MOSAIC_MCP_*` 环境变量（nemoclaw.json:1-12）。
- **技能库**：bcm（清单优先只读 cmsh、禁臆造子命令）、hardware-agent（198 行最大：开 NVDebug 采集前必须告知 5-30 分钟耗时并等答复）、gpu-networking（测量/诊断两段式、逐台 participating host 记录）、iraop/observability/grafana/slurm（作业失败先 slurm_job_evidence、证据源断了继续用其余）+三份 references。技能与 L08 插件一一呼应：技能教何时用哪个工具，插件实现工具。docs/skills/ 下另有 headless SKILL.md（170 行）。
- **slack-enterprise-grid-patch.mjs**：幂等补丁，给 OpenClaw Slack 插件打 Enterprise Grid 兼容，已打则退出 0。

## 4. 核心机制二：TS 扩展插件族三域

`extensions/` 下全部是 OpenClaw TS 插件，按职能分三域：

**访问治理**：automation-context.ts（231 行）是访问控制单一事实源——ALWAYS_MUTATING/READ_ONLY 清单+per-server 策略表，导出 17 个判定函数（toolAccess/toolRequiresEdit 等，automation-context.ts:210/229）；自动化会话一律只读、非法值回退 view。diagnostic-policy.ts（97 行）为 **36 个诊断工具**定义 argv 白名单（RULES 表 diagnostic-policy.ts:53），三形态：exact() 固定 argv 矩阵、flags(regex) 旗标正则、专用校验函数（nvidiaSmi/journalctl）；唯一出口 isAllowedDiagnosticArgv（diagnostic-policy.ts:91）——过白名单只读免审批，未过走 Edit 审批。mutation-ledger.ts（158 行）：runMutationOnce 以 toolCallId+sha256 指纹保证变更幂等重放（mutation-ledger.ts:80-84）。automation-guard 拦截变更类调用阻断或转 HITL；slack-approval.ts 生成 allow/deny 按钮，**决策者必须是发起请求的同一 Edit 用户、超时按 deny**。

**集群远程**：kubernetes 双级——run_kubectl 只读白名单（get/logs/describe/top 等 10 命令），run_kubectl_admin 仅 editEnabled 注册走审批；policy.ts:9-14 列 18 个 FORBIDDEN_FLAGS（--as/--token/--kubeconfig 等覆盖类）、Secret 资源不可读（policy.ts:15）、shell 语法拒绝；runner.ts（88 行）最小 env spawn（shell:false）、超时 SIGKILL、kubeconfig 脱敏 `<kubeconfig>`；多集群 resolveCluster 路由。remote-ssh：buildSshArgs 生成 19 个 `-o` 加固参数（-F /dev/null、公钥强制、StrictHostKeyChecking=yes、ProxyCommand=none，remote-ssh/runner.ts:19-47）；policy 只认 host+argv、拒嵌套 ssh。slurm 插件（108 行）bearer 只读代理 slurm-evidence；diagnostic-agent（500 行）桥 NVDebug REST 注册 hardware_* 五工具。

**观测平台**：observability——Prometheus/VM 只读查询+Loki LogQL（窗口 24h、limit 1-1000），compactResult 抽稀防上下文爆炸（observability/index.ts:102）；grafana.ts（516 行）核心 validatePanels（observability/grafana.ts:169）建盘前逐面板试跑查询全过才创建；dcgm（376 行）聚合 dcgm-exporter 指标为每 GPU 快照（dcgm/index.ts:37）出五只读工具；bcm/index.ts（935 行最重）streamable HTTP/SSE 桥 bcm-mcp-tools，60s 去重缓存 RPC（bcm/index.ts:17）+约 14 个条件注册工具；iraop（469 行）**自实现 MCP 客户端**：callMcpTool（iraop/index.ts:107 起 177 行）完整走 initialize→tools/call（iraop/index.ts:257-266），每调用新开 SSE 流。

**独立进程（L09）**：bcm-mcp-ssh-server.py（298 行：SSH 到头节点执行 cmsh，HMAC 恒定时间 token 校验+主机白名单）、mcp-oauth-proxy.mjs（78 行零依赖 OAuth 前置代理）、slurm-evidence/server.mjs（230 行：EVIDENCE_ROOTS 白名单 realpath 防逃逸）、utils/mosaic-mcp.mjs（127 行：Mosaic UI 工具面暴露为 stdio MCP）。

## 5. 核心机制三：安全模型三模式矩阵与多租户

**「模型指令不是安全边界」是第一公理**（docs/security_model.md）：观察/变更分离做在工具、凭据、会话三层——浏览器与 MCP 客户端不接触集群凭据，各模块工具各持凭据。访问模式矩阵（security_model.md:13-15）：

| 模式 | 只读工具 | 诊断 SSH | 变更工具 |
|---|---|---|---|
| View | 自动 | 自动（白名单内） | 阻断 |
| Edit | 自动 | 自动 | hitl=true 须审批 |
| Auto | 自动 | 自动 | 免审批，用户须先接受警告 |

铁律：自动化会话恒为 View 不可改（security_model.md:17）；Edit 审批 fail-closed——拒绝/过期/服务不可用都算拒绝，一次审批只覆盖一个操作（security_model.md:61）；Auto 警告是确认非执法，RBAC 与审计照常生效（security_model.md:63）。默认 `modules.edit.enabled=false` **不装任何变更凭据**；RBAC 是最终权威——Auto 绕过的是审批不是 RBAC。

**多租户**：operator/tenant 各起独立 Helm release（独立登录/状态/审计/凭据），**operator 看硬件与系统，tenant 只看自己的作业**（docs/multitenancy.md:3）；tenant 只开三模块、经 kubeconfigSecretRef 连自己的集群。

## 6. 部署面：Helm chart 双栈

**mosaic-stack 主 chart**：Chart.yaml 两个 OCI 依赖（openshell@ghcr.io + iraop-stack@nvcr.io 私仓）；540 行 values.yaml（modules 矩阵 values.yaml:40 起）驱动全模块开关，镜像 digest 钉死。要点：

- **779 行 openclaw.yaml**（最大模板）：多 initContainer（kubectl/openssh/perms/config）铺垫 /home/node/.openclaw；checksum/openclaw-seed 注解（openclaw.yaml:28）使**种子任何变更即滚动重启**。
- **3999 行 AgentSandbox CRD**（crds/agent-sandbox.yaml）：沙箱工作负载完整 schema（网络/文件系统/系统调用策略），是 agent-sandbox-controller 的 API 契约，随 chart 分发。
- **342 行 validation.yaml 零资源 fail-fast**：llm.mode 枚举、vllm profile/gpuCount/TP 一致性、Slack 白名单、BCM 依赖链、K8s 地址必须 https——任一不满足即终止渲染（validation.yaml:5 起）。
- **secrets 三层链幂等**：gateway token 用户值→lookup 既有→自动生成；四类 auth Secret 统一 lookup 模式——**upgrade 不覆盖手工轮换的凭据**。
- **vLLM profiles**：super-1gpu 单卡 Nemotron-3.5-Super-VL-120B-A12B-NVFP4（TP=1，vllm-super-1gpu.yaml:12-15，262k 上下文）；ultra-4gpu 四卡 TP=4 Nemotron-3-Ultra-550B-A55B-NVFP4（FP8 KV+专家并行+2Ti 缓存），安装时 -f 叠加。
- **llm-compat**：内嵌 Node 反代（ConfigMap 里的 server.js），仅改写 POST /chat/completions，修补 OpenClaw 与 LLM 端点格式差异。

**afoa-inference 子 chart**：推理拆到独立 GPU 集群各自伸缩——digest 钉死、runtimeClassName nvidia、模型缓存 volumeClaimTemplates，默认与 super-1gpu 同款；chart-render.test.mjs 守护渲染契约。

## 7. 新人 16 步导览与已知坑

**路线**（tour t01-t16）：①README+use_cases+security_model 全局认知→②workspace 六件套→③技能库→④⑤访问治理四件套→⑥⑦kubernetes/remote-ssh/slurm/硬件诊断→⑧观测四插件→⑨bcm/iraop 平台桥→⑩values+CRD+profiles→⑪⑫⑬openclaw.yaml/种子/validation/rbac/managed-mcp→⑭测试→⑮Kind E2E→⑯演示。前 9 步是"agent 如何行为"，后 7 步是"如何部署守护"。

**已知坑**：
1. **nemoclaw.json 是 Helm 模板化 JSON 不是坏文件**——jq 解析会因 `{{ }}` 失败，看产物须 helm template；AGENTS.md 同理，源文件≠运行时文件。
2. **tests/test_bcm_docs.py 是引用悬空死测试**——指向不存在的 files/docs/download_bcm_docs.py，跑它直接报错。
3. **模板内嵌文件不能按标准解析**——bcm-mcp-ssh-server.py、server.mjs、llm-compat 的 server.js 都活在 ConfigMap 模板的 `{{ }}` 语境里，工具链对这类文件的解析全回落 regex。
4. **mutation-ledger 台账指纹不含敏感参数**——落盘只有 id+指纹+状态（mutation-ledger.ts:11-17），原始 args 只进哈希不落盘；审计查不到参数明文是设计。
5. **AGPL Grafana+GPL BusyBox 与 Apache-2.0 并存**（LICENSE-3rd-party.txt:24-25），分发合规要过这两关；spdx.test.mjs 管全仓双 SPDX 头与 BCM 缩写禁令。
6. **demo 全合成无实测**（assets/ai-factory-ops-demo/README.md:10-11）——合成遥测+合成音频，无真实集群会话，引用其数字做评估是错的。
7. 早期访问 chart/镜像须受邀（README.md:38），clone 后 `helm dependency update` 拉不到 OCI 依赖属预期。
8. 种子技能目录实为 **7 份 SKILL.md+3 份 references**（图谱"十份"按 md 总数计）；第 8 份 SKILL.md 在 docs/skills/（headless 用途）。

## 8. 与生态关系

- **OpenClaw/NemoClaw**：agent 运行时与网关，AFOA 的地基——nemoclaw.json 是其主配置，extensions/ 按 plugin 协议编写，workspace 六件套是其约定。
- **plugin-sdk**：扩展宿主 API——TS 扩展经 PluginApi 注册工具与可信策略（session-access/trustedToolPolicies 契约）。
- **MCP** 三处用法分清：bcm/iraop 扩展是**客户端**（iraop 手写协议）；managedMcpServers 是 chart **托管 server** 骨架（RunAI/VictoriaMetrics 接入）；utils/mosaic-mcp.mjs 把 AFOA 暴露为 **stdio server**。
- **BCM（Base Command Manager）**：NVIDIA 集群管理器——bcm 扩展+ssh-server 适配器+只读 cmsh 三层桥；仓外文档禁用 BCM 缩写。
- **RunAI/Slurm**：RunAI 经 managed-mcp 接入；Slurm 是调度器证据源（vanilla 走 DaemonSet 收集器、bcm 走 WLM，backend 三态选择）。
- **vLLM**：推理引擎——chart 内 vllm.yaml 与独立 afoa-inference 双形态，Nemotron NVFP4 两档 profile，OpenAI 兼容端点。
- **Kind**：E2E 环境——双集群+现场 ed25519 密钥对+alpine sshd Pod，权限策略进真集群验证。
