# 05 · openclaw workspace：人格六件套与运维技能库

> 目录：`helm/mosaic-stack/files/openclaw-seed/workspace/`（六件套）+ `skills/`（技能库）
> 关键事实：`AGENTS.md` 不是普通 markdown，是 **Helm 模板**——chart 渲染期才生成 agent 真正读到的系统提示词

## 一、角色定位

openclaw-seed 是随 chart 播种的 agent 初始工作区。workspace 六件套（AGENTS/IDENTITY/SOUL/TOOLS/USER/HEARTBEAT.md）定义"这个 agent 是谁、怎么做事"；skills 目录放"做事的方法论"。它们不是文档——是 OpenClaw 每次会话装载的**运行时人格与操作纪律**。

血统值得先看清：六件套每个文件头都有双重 SPDX 版权行——`Copyright (c) 2025 Peter Steinberger`（MIT）+ `Copyright (c) 2026 NVIDIA`（如 `workspace/SOUL.md:2-4`）。这套人格框架来自 OpenClaw 上游（Peter Steinberger 的开源项目），NVIDIA 在其上注入了运维内容：SOUL/IDENTITY/HEARTBEAT 基本是上游原味，AGENTS.md/TOOLS.md/USER.md 被重度改写为 SRE 操作系统。

### AGENTS.md 是 Helm 模板：一文件渲染出多种部署人格

`AGENTS.md:29` `{{- if .Values.modules.edit.enabled }}` 与 `AGENTS.md:45 {{- else }}`/`AGENTS.md:51 {{- end }}` 把系统提示词切成两个世界：Edit 开启时渲染"Session Access Modes"整节（View/Edit/Auto 三模式语义，`:31-43`）；未开启时只渲染两行"Read-only Mode"（`:47-49`）。嵌套条件 `AGENTS.md:41 {{- if .Values.modules.edit.ssh.enabled }}` 再细分 SSH 变更工具是否在册。`AGENTS.md:97 {{- if .Values.modules.webSearch.enabled }}` 同理控制 Web Search 节。

最巧妙的是技能装载（`AGENTS.md:104-115`）：`{{ range .Values.openclaw.bootstrapSkills }}` 遍历装机指定的技能列表，用 `$.Files.Get`（`AGENTS.md:109`）把每份 SKILL.md **全文内联**进系统提示词，references 目录用 `Files.Glob` 逐个追加（`AGENTS.md:110-114`）。关键在 `required` 函数（`AGENTS.md:109`）——values 里声明了不存在的技能，**chart 渲染直接失败**。部署配置错误在 helm install 时爆炸，而不是 agent 上线后人格残缺。这就是"预载技能"（preloaded skill）的实现：不是运行时读文件，是编译期内联。

同目录的 `nemoclaw.json`（373 行）同样以 `{{- ... }}` 模板语法开头——openclaw-seed 里所有"配置文件"其实都是模板源，chart 渲染后才有真身。

## 二、内部结构

### 六件套各自的角色分工

**AGENTS.md（131 行）——操作纪律主文档**。除模板结构外，值得逐条记的硬纪律：

- `AGENTS.md:11` 每条用户消息必须有可见回复，"Never respond with NO_REPLY"——对抗 agent 学到的"静默成功"坏习惯；
- `AGENTS.md:15` 证据三分法：观察（observations）、候选解释（candidate explanations）、已验证原因（verified causes）必须保持区分——"A warning on an unused resource does not explain the workload"（未用资源上的告警解释不了工作负载）是全文最精辟的一句；
- `AGENTS.md:33` 模式语义权威化：`[Runtime Context]` 里的 `ai_factory_operations_agent_access_mode` 是权威，**Edit 模式下"立即调用变更工具"——工具调用本身会弹审批 UI，禁止在对话里问"可以吗"或编造审批命令**；
- `AGENTS.md:39` 审批≠成功："Approval authorizes an execution attempt; it does not mean the command succeeded"——区分审批、执行、结果三事件；
- `AGENTS.md:62-68` 集群边界认知：一个 K8s 集群只含注册节点，"空 GPU 清单不能推出机房里没有 GPU"；发现主机不等于获授权（"Inventory discovery does not authorize access to newly found hosts"）；
- `AGENTS.md:119` 性能评级必须有实测参照或文档目标，否则只报观测值不分类——硬件清单与健康检查通过不构成性能预期；
- `AGENTS.md:121` concise mode（`ai_factory_operations_agent_concierge_mode=true` 时启用简洁回复风格）；`AGENTS.md:127` 禁 emoji；`AGENTS.md:131` 附件标记必须对应真实产物，禁止占位路径。

**IDENTITY.md（26 行）——身份卡**：Creature/Vibe/Emoji/Avatar 四槽（`workspace/IDENTITY.md:11-17`），预置 `AI assistant`/`formal`/🛡️——盾牌 emoji 是运维人格的点睛。文件明说这是"第一次对话时填写的起点"（`workspace/IDENTITY.md:9`）。

**SOUL.md（44 行）——人格准则**，五条 Core Truths：真有用而非表演式（`workspace/SOUL.md:15`，别"Great question!"开场）；有自己的观点（`workspace/SOUL.md:17`，"no personality is just a search engine with extra steps"）；先自行排查再求助（`workspace/SOUL.md:19`）；以能力赢得信任（`workspace/SOUL.md:21`，外部动作谨慎、内部动作大胆）；记住自己是 guest（`workspace/SOUL.md:23`，能访问别人的系统是一种亲密，须尊重）。边界四条（`workspace/SOUL.md:26-30`：隐私、外部动作先问、不发半成品、群聊里不代表用户发言）。连续性哲学（`workspace/SOUL.md:36-40`）："Each session, you wake up fresh. These files are your memory."——文件即记忆，改 SOUL 要告知用户（`workspace/SOUL.md:40`）。

**TOOLS.md——部署级工具笔记**（`workspace/TOOLS.md:9` 定位清楚："Skills define how tools work; this file is for deployment-specific notes"）：集群指标优先 observability 工具而非裸 shell（`workspace/TOOLS.md:13`）、`/k8s` 前缀路由（`workspace/TOOLS.md:15`）、工具被拒时的应答纪律（`workspace/TOOLS.md:16`）。

**USER.md——用户画像**：服务对象是 "Team SRE"（`workspace/USER.md:11-14`），备注"通过安装器启用的模块运维 NVIDIA 集群的 SRE 团队"（`workspace/USER.md:20`）。`workspace/USER.md:24` 的提醒很有人味："你在了解一个人，不是在建档案。"

**HEARTBEAT.md（13 行）——心跳模板**：文件保持为空（或仅注释）即跳过周期心跳 API 调用（`workspace/HEARTBEAT.md:10`）；写入任务则 agent 周期检查——一个空文件的开关语义。

### 技能库：7 份 SKILL.md + 3 份参考文档

图谱"运维技能库"层的 10 个节点 = `skills/` 下 7 份 SKILL.md（bcm 46 行/gpu-networking 45/grafana 62/hardware-agent 198/iraop 35/observability 122/slurm 30）+ gpu-networking 的 3 份 references。按重量级读三份代表：

**bcm/SKILL.md（46 行）——工具路由纪律**：清单/类别/健康类问题优先 `bcm_execute_cmsh`（只读 CMSH 身份，`skills/bcm/SKILL.md:17`）；`bcm_health` 大集群上慢、"不要为了开个 /cluster-management 请求就调它"（`skills/bcm/SKILL.md:17`）；**禁止发明 CMSH 语法**——`cluster` 不是合法 mode、`device health ...` 不是合法命令（`skills/bcm/SKILL.md:17`）；CMSH 手册是本地 markdown 文件，用 `exec` 只读命令查 `/sandbox/workspace/skills/bcm/docs`，**"Never call bcm_search_docs; that tool is not available"**（`skills/bcm/SKILL.md:19`——预判模型会幻觉一个不存在的工具）；变更前必须先用只读通道 `help <command>` 验证语法（`skills/bcm/SKILL.md:27`），"help-only 请求不需要审批"。

**gpu-networking/SKILL.md（45 行）——最重的方法论**：测量/诊断/纠正三段式。诊断五步序列（`:19-23`）要求**每台参与主机**（不是抽一台代表）都映射 GPU UUID→HCA→PCI 地址→sysfs 祖先链全量清单；区分能力与启用（ACS 要看 `ACSCtl` 重定向位而非 `ACSCap`，`skills/gpu-networking/SKILL.md:22`）；纠正段给出精确到 bit 的操作规范——运行时 ACS 纠正只清 `0x0004`/`0x0008` 两个重定向位、保留其余位、无需重启（`skills/gpu-networking/SKILL.md:33`）；纠正完成判据（`skills/gpu-networking/SKILL.md:35`）：每台主机每座桥的写入都要读回对账，最后一次变更之后的新测量才算验证——"变更前的样本不能验证变更后的状态"。

**hardware-agent/SKILL.md（198 行，frontmatter 即纪律）**：开新 NVDebug 采集前**必须**先说 "A fresh NVDebug collection can take 5-30 minutes. Do you want me to start it?" 并等待答复（frontmatter description 内嵌）——把等待成本前置告知用户；"backend owns DUT lookup and credentials; do not prompt for BMC credentials"（不要向用户要 BMC 凭据——那是后端的事）。

其余：slurm（30 行）以 `backend` 字段区分 vanilla 文件系统采集与 BCM WLM 两种证据来源（`skills/slurm/SKILL.md:17`）；iraop（35 行）默认 `depth: "quick"`（`skills/iraop/SKILL.md:29`）、给用户的 kubectl 示例**只准 apply -f - <<EOF 形态，禁止 kubectl create**（`skills/iraop/SKILL.md:35`——apply 幂等，误复制重跑无害）；observability/grafana 管指标/日志/仪表盘的路由。

## 三、外部连接

- **上游**：chart values（`modules.edit.enabled`、`openclaw.bootstrapSkills`）→ AGENTS.md 模板渲染 → openclaw-seed ConfigMap → agent 容器挂载。技能库同理经 `Files.Get/Files.Glob` 进提示词（`AGENTS.md:109-114`）。
- **下游工具锚**：AGENTS.md 的纪律全部指向第 1-4 篇的代码边界——`:25` 的 run_remote_ssh 只读 argv 对应 diagnostic-policy，`:70/:72` 的 run_kubectl 纪律对应 kubernetes 插件双级工具，`:33` 的模式语义对应 automation-context。提示词纪律与代码边界互为镜像，**代码强制为主、提示词为辅**（`docs/security_model.md:3`："Model instructions... are not a security boundary"）。
- `slack-enterprise-grid-patch.mjs`（同层）与 nemoclaw.json（模板）构成 seed 的其余配置面。
- 全仓第 8 份 SKILL.md 在 `docs/skills/ai-factory-operations-agent-headless/SKILL.md`（170 行）——教编码 agent 无浏览器调用 AFOA，属文档树不进 seed。

## 四、数据流

一次部署的人格生成流：

```
helm install --set modules.edit.enabled=false --set openclaw.bootstrapSkills={bcm,slurm,...}
  → AGENTS.md 模板渲染：
      :29 条件假 → 丢弃 :31-43 三模式节 → 渲染 :47-49 "Read-only Mode"
      :104 range bootstrapSkills → bcm/SKILL.md 全文内联 + 其 references 逐个追加
      （required 校验：列表里有不存在的技能 → helm install 失败）
  → 渲染产物随 openclaw-seed 挂载为 agent workspace
  → OpenClaw 每会话装载 AGENTS.md + SOUL/IDENTITY/USER/TOOLS/HEARTBEAT
```

运行期一次故障排查的纪律流（AGENTS.md:13-15）：进预载技能的证据序列 → 观察与候选解释分离 → 需要研究时走 iraop 技能（带实测事实提问）→ 验证研究建议于真实资源 → 矛盾证据先解决 → 只报告有证据支撑的结论。

## 五、设计决策

1. **人格与纪律分层**：SOUL/IDENTITY 管"是谁"（上游通用），AGENTS/TOOLS 管"怎么做事"（NVIDIA 运维特化）——升级上游人格框架不冲突运维纪律的演进。
2. **编译期内联而非运行时加载**：技能进系统提示词用 `Files.Get`（`AGENTS.md:109`），预载技能=每会话可见、不占一次工具调用；代价是提示词体积，故 SKILL.md 都很短、重参考另放 references 按需读。
3. **`required` 让配置错误前移**（`AGENTS.md:109`）：技能名拼错在 helm 期爆炸，好过 agent 上线后静默缺技能。
4. **纪律写行为不写原理**："不要问审批、直接调工具"（`AGENTS.md:33`）、"未用资源的告警解释不了负载"（`AGENTS.md:15`）——提示词工程的有效形态是可执行指令，不是安全说教。
5. **空文件当开关**（`workspace/HEARTBEAT.md:10`）：心跳由"文件是否为空"决定，无配置项、无 env——最朴素的机制最不容易配错。

## 六、新人提示

- 改 AGENTS.md 时**必须过 helm template 验证**：它是模板，一个漏掉的 `{{- end }}` 只在渲染期暴露；改完跑 `helm template` 或 chart-render 测试。
- 加新技能的三步：`skills/<name>/SKILL.md` 写好 → values 的 `openclaw.bootstrapSkills` 登记 → 渲染验证。忘了第二步技能就只是盘上的死文件。
- SKILL.md 里可以引用工具名约束装配前提（iraop 的 frontmatter `requires.tools`，`skills/iraop/SKILL.md:9`）——运行时工具不在册时技能应自我降级（bcm:21 的"工具缺失就明说不可用"）。
- USER.md 会被 agent 长期改写积累——它是活档案不是静态配置；重置人格时别忘了它的存在。
- ⚠️ 甄别记录：任务简报称"十份 SKILL.md 运维技能库"——源码核实 `SKILL.md` 文件全仓共 **8 份**（openclaw-seed 7 份 + docs/skills/headless 1 份）；图谱"运维技能库"层的 10 个节点实为 **7 份 SKILL.md + 3 份 gpu-networking references**（gpu-network-path/measurement-interpretation/platform-contracts）。"人格六件套"与源码一致（workspace 六文件齐全）。本文按源码口径撰写。

（行号锚基于当前工作树源码逐条核实。）
