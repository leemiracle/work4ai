# 08 · Agent 线：NVIDIA 的 Agent 新贵——硬件厂为什么突然造起了"管家公寓"

> 《NVIDIA 全栈深讲系列》第 08 篇。主仓 NemoClaw / OpenShell / SkillSpector（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/`），辅仓 NeMo-Agent-Toolkit、skills、SkillEvaluator、NeMo-Relay、Personal-AI-Router。star 数据取自 `_org_repos.NVIDIA.jsonl`（2026-10-01 快照）：NemoClaw 22615 = org 第一（压过 Megatron-LM 的 18042），SkillSpector 18809 = 第二，OpenShell 12713 = 第八。所有行号锚均从本地源码核实。

## 一、第一性原理设问：一家卖 FLOPs 的公司，为什么要写 agent 软件？

先摆矛盾：NVIDIA 的商业模式是把算力（FLOPs）和带宽（HBM/互连）装进机箱卖出去。编译器、NCCL 这些仓可以理解——它们直接让卡跑得快（前七篇的主线）。但 agent 软件？agent 的"智能"跑在哪家的模型上都行，NemoClaw 自己**没有 agent loop**（下文源码为证）。一个不直接消耗一张卡的软件层，凭什么发布 7 个多月就冲上 org star 第一？

推导分三步，每步都有数据。

**第一步：负载重心迁移——推理超过训练，agentic 超过 chat。** GTC 2026 上黄仁勋明说推理已超过训练成为主导 AI 负载（CIQ 转述）；OpenRouter 口径下 agent 推动token 用量自 2025 年初增长约 34 倍（Data Center Frontier 二手转述，原始口径未直接核验）。更硬的证据在自家文档：TRT-LLM 官方博客直接承认优化边界变了——`TensorRT-LLM/docs/source/blogs/tech_blog/blog26_..._Agentic_Workload_Optimizations.md:319`："Agentic workloads change the optimization boundary: dynamic multi-turn prompts, very high KV reuse, conversation locality, routing, and serialization become part of the critical path"。

**第二步：agentic 负载的物理特征，恰好打在 GPU 经济学的软肋上。** chat 是一问一答，agent 是"子 agent 扇出 × 多轮工具调用 × 反思"——blog23（`blog23_Joint_Optimization_of_Agent_Applications_and_TensorRT-LLM.md:145`）的原话："Agent applications are more KV cache-intensive due to several compounding factors"，扇出成倍放大 KV 占用，工具调用-消化-反思的循环让 cache 密度远超 chatbot。配套博客 blog27 用真实 agent 轨迹回放证明：**token 级指标和 job 级指标可以给出相反的结论**（固定形状基准上三种并行策略几乎重合，真实轨迹上 TP4+EP4 全程领先），且性能天花板由**前缀缓存命中率**而非算力决定（Coder 轨迹上限 ~0.97，eviction 一掉悬崖性能就崩）。评测口径因此整个换了：Artificial Analysis 推出 AA-AgentPerf（2026-06-12 首发），指标不再是 tok/s 而是"满足输出速度与 TTFT 双 SLO 的最大并发 agent 数"。NVIDIA 拿 GB300 跑出 **57.5 agents/GPU（SLO20 档）、19.2（SLO60 档）**，由 Artificial Analysis 独立运行验证（blog26:63）。注意这个单位的含义：**每张 GPU 能同时养活多少个常驻 agent**——这就是"agent 效率 = GPU 卖量"的直接换算式。

**第三步：需求侧的"最后一公里"是信任，而信任恰好没人做。** 2026 年初 OpenClaw（血统：Clawdbot → Moltbot → OpenClaw，Wikipedia/CNBC 2026-02）现象级爆红——一个住在聊天软件里、跑在你自己电脑上、拿着你凭证的 always-on 管家——同时也爆红出安全争议：它读你的文件、用你的 API key、永远在线。企业想要"每家公司都需要 OpenClaw 战略"（当时 Reddit 的标题），但没人敢让员工把公司凭证交给一个 npm 装出来的数字生命。NVIDIA 在 GTC 2026（2026-03-16 官方公告）回应的正是这一格空白：NemoClaw——把 OpenClaw 装进沙箱、把推理拉到本地 GPU、把策略变成可验证的对象。

三步合起来的答案：**NVIDIA 做 agent 软件不是转型，是给 GPU 需求侧修水渠**。agentic 负载把推理需求乘了一个系数（多轮×扇出×常驻），而落地的瓶颈从"模型能力"挪到了"敢不敢用"。谁把"敢用"做成产品，谁就掌握分发渠道；渠道里的水（推理）默认流向两处——云端 `integrate.api.nvidia.com`，或本地 DGX（下文 blueprint 源码为证）。这正是"新贵"们的位置：NemoClaw（22615）/ SkillSpector（18809）/ OpenShell（12713）三个 2026 年新仓挤进 org 前十，背后是一条从"卖卡"延伸到"卖可部署 agent 栈"的完整叙事。

## 二、直觉层：管家、公寓、物业与背景审查

把 always-on agent 想成一个**住家管家**：OpenClaw 是从 WhatsApp/Telegram 搬进你电脑的管家，勤快、能干，但你把家门钥匙、银行卡、通讯录全给了它，还让它 24 小时自由行动。直接装在工作站上 = 请个陌生管家再配全套钥匙。

NVIDIA 的三件套各管一段：

- **OpenShell = 带门禁的公寓楼**。管家不是住你家，是住进一间单间：水电（文件/网络/系统调用）都过楼里的总闸（内核级强制），钥匙（凭证）不发给住户，由物业前台在确认收件人是"已批准的端点"后才代为签收。换房（策略变更）前还有结构工程师（形式化验证）先审图纸。
- **NemoClaw = 物业公司**。不管家管的脑子（agent 是 OpenClaw/Hermes/DeepAgents 的），管入住流程（blueprint）、供电（managed inference——云端 NIM 或本地 vLLM/llama-cpp）、门禁模板（policy presets）、房屋快照与迁移。一句话：**它不造 agent，它造"让 agent 可以被企业签收的那层纸"**。
- **SkillSpector + skills + SkillEvaluator = 管家市场的背景审查与技能认证**。技能（skill）是 agent 的劳动力商品——SKILL.md 一装就能干活，也意味着 SKILL.md 一装就有代码在你沙箱里跑。NVIDIA 的答案是"Verified Skills"流水线：扫描（SkillSpector，71 个漏洞模式+YARA 恶意样本）→ 评估（SkillEvaluator，沙箱实测技能是否真提升表现）→ 签名分发（skills 镜像仓）。

为什么和 LangChain 类框架长得完全不同？因为它们回答的问题不同。LangChain/LangGraph 造的是**大脑的骨架**（链、图、状态机），假设执行环境是安全的；NVIDIA 的三件套造的是**身体的合规宿舍**，假设大脑是别人家的、不可信的。前者优化"agent 能不能想出来"，后者优化"企业敢不敢让它跑"。这也是为什么 NemoClaw 支持列表里 OpenClaw 旁边还站着 Hermes 和 LangChain Deep Agents Code——宿客可以换，公寓照开。至于 NeMo-Agent-Toolkit（前身 NeMo-Skills），那是同一物业公司在工业区盖的另一栋楼：给企业流水线上的**工作流**（而非对话管家）用的编排 DSL（机制层 3.4 节详述）。

## 三、机制层：四块源码实证

### 3.1 NemoClaw：把"企业签收单"写成一份 YAML

NemoClaw 的核心构件是 `nemoclaw-blueprint/blueprint.yaml`（102 行）——沙箱镜像、推理后端、路由器、策略基线全部声明式钉死。三个细节值得逐行看：

**推理水的流向，二选一写在 profile 里**（`blueprint.yaml:17-22` 声明五档：default/ncp/nim-local/vllm/routed）。default 档指向云端：`endpoint: https://integrate.api.nvidia.com/v1` + `model: nvidia/nemotron-3-super-120b-a12b`（`blueprint.yaml:58-59`）；vllm 档指向本机：`http://localhost:8000/v1` + `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8`（`:80-83`）；routed 档指向本机 4000 端口的路由器（`:88-98`）。云和本地 DGX 是同一张清单上的选项——这就是"隐私敏感买 DGX"的产品化落点。配套的 `managed-inference/presets/` 里有 26 个按**硬件×引擎×模型×量化**组合的预设（`vllm.dgx-spark-gb10.single.nemotron-3-nano-4b-fp8.yaml` 这类命名），每个预设带 readiness 硬件资格门：`kind: qualification, id: host.platform.dgx_spark, status: qualified`（该文件 `:21-24`，`validation.level: hardware` 在 `:12`）——**推理按"这块卡是什么"发牌，不是按模型**。

**供应链钉死到字节**：沙箱镜像用双字段 digest 锁版本（顶层 `digest:` 在 `:15`，`components.sandbox.image` 在 `:35`，注释明说防 registry 被攻破或 `:latest` force-push 静默换镜像），`test/onboarding/validate-blueprint.test.ts` 拒绝 mutable tag 与 digest 不匹配。连宿主 OpenShell 版本都钉死单点：`min_openshell_version: "0.0.116"`、`max_openshell_version: "0.0.116"`（`:6-7`）——既是纪律，也是 API 剧烈变动期的化石证据（批判层再谈）。

**GPU 证明 fail-closed**：`src/lib/container-gpu-proof.ts:19-22` 的接口注释写明：`passed` 为真**仅当真实 CUDA 工作负载成功**，"not just nvidia-smi"——专门区分真 Windows-on-Arm N1X GPU 与"装了 nvidia-smi shim 但没有可用设备"的 Snapdragon 环境（注释引用 issue #3988/#4424/#4565）。实现（`:67-71`）钉死多架构 `nvcr.io/nvidia/k8s/cuda-sample` 镜像，逐设备 `CUDA_VISIBLE_DEVICES=<uuid>` 跑 vectorAdd。这个文件是全篇叙事的微缩：**NVIDIA 连"有没有卡"都要用跑一次 kernel 来证明，而不是问驱动**。

路由这一层同样值得看：`nemoclaw-blueprint/router/pool-config.yaml:11-20` 配的是 NVIDIA LLM Router v3——`Qwen3.5-0.8B` 编码器对每个请求预测各模型的 P(correct)，`tolerance: 0.20` 表示允许选比最优置信度低 20pp 内的最便宜模型（候选是 $0.052/M 的 gpt-oss-20b 与 $0.10/M 的 nemotron-3-super-120b）。把"每次调用都值得为它单独定价"做成了基础设施。

### 3.2 OpenShell：内核强制 + Z3 形式化验证的策略面

OpenShell 是 Rust 单仓 40+ crates（gateway/supervisor/sandbox 三平面，driver 覆盖 docker/podman/k8s/vm），两处设计在 agent 生态里罕见：

**策略变更先过形式化验证**。`crates/openshell-prover/src/lib.rs:4-6` 模块文档：把沙箱策略、二进制能力表、凭证作用域编码为 **Z3 SMT 约束**，跑可达性查询检测**数据外泄路径与写绕过**；`prove()`（`:33`）以退出码表达结论——0=无发现或全部 risk 已接受，1=存在未接受发现。也就是说，一条"允许访问某新 host"的策略变更在人审之前，先被机器穷举过"这个组合会不会拼出一条把凭证送出去的通道"。

**授权的单位是端点增量，不是工具调用**。`e2e/policy-advisor/existing-endpoint-auto-approve.sh` 把策略分层：已有端点的策略变更自动批，**新端点必须人审**——信任按增量发放。策略本身分层到 L7：`crates/openshell-policy/src/l7_validate.rs`（696 行）做 MCP/JSON-RPC 级 method+path 校验（NemoClaw blueprint `:5` 注明依赖 OpenShell#1865）；`skills/generate-sandbox-policy/SKILL.md:22` 起的三档表把粒度讲得很直白——用户给 host+意图就生成 L4/preset 策略，给全份 API 文档就生成逐端点 method+path 的 L7 规则。凭证则由 gateway 注入：沙箱内 agent 永远看不到真实 key，请求离开沙箱、确认目标是已批准端点后才被签上（README："Agents never see real credentials"）。

### 3.3 技能供应链：SkillSpector / skills / SkillEvaluator

SkillSpector 是给 SKILL.md 做的 SAST。`src/skillspector/graph.py:46-52` 用 LangGraph `StateGraph` 串管线：resolve_input → build_context →（并行分析器，`is_available()` 探测不可用即跳过并告警）→ meta_analyzer → report，每个分析器节点包在 inspection ledger 的 guard 里——**没扫到不等于通过**（fail-closed 三态门禁）。分析器四层：静态正则/AST 污点、MCP 专用、YARA（`src/skillspector/yara_rules/` 下就是 `cryptominers.yar`、`hacktools.yar`、`webshells.yar` 这些杀毒引擎同款规则）、语义 LLM（71 个漏洞模式/17 类，输出 SARIF 2.1.0，OSV.dev 实时查依赖 CVE、断网回退内置表，`--transitive` 递归扫外部仓但预算硬顶 32 目标/10MB/1 万文件防递归 DoS）。耐人寻味的是 `model_registry.yaml`：语义层模型清单从 gpt-5.2、1.05M 上下文的 gpt-5.6-sol 到 claude-opus-4-5，deepwiki 记载默认 provider 是 NVIDIA Build 上的 `z-ai/glm-5.2`——**NVIDIA 的质量门禁并不押注自家模型**。

评估侧的 SkillEvaluator 是三层框架：Tier1 静态（以子进程调 SkillSpector，0-100 风险分映射内部严重度）→ Tier2 语义去重 → Tier3 沙箱实测（六指标聚合成五质量维度，LLM 判官 PASS 线 0.70）。核心指标 **Skill Lift = with_skill − baseline，±0.05 为改进/回归阈值**——技能的价值被定义为可测量的增量，而不是作者的自我声明。分发侧的 `skills` 仓则是镜像聚合：技能在各产品上游仓维护，`components.d/` 注册表每日 sync；格式遵循开放的 agentskills.io 规范（Claude Code/Codex/Cursor 通吃），NVIDIA 附加 `license` 必填等约束。

### 3.4 两条外围线：NeMo-Agent-Toolkit 与 NeMo-Relay

NeMo-Agent-Toolkit（NAT，2652 star）血统可溯到 NVIDIA-NeMo/Skills（"improve skills of LLMs"的 SFT/RL/评测流水线，AIMO2 Kaggle 夺冠那套，2025-06 开发者博客），现品牌化为统一 agent 框架。它与 LangChain 的关系是**元框架**而非替代：一套 Pydantic+YAML 配置（`_type` 字符串判别组件）接入 LangChain/LlamaIndex/CrewAI/AutoGen 等 9 个框架的既有 agent，外面统一挂中间件（超时/重试/HITL/PII/Guardrails）与评估观测（ATIF/ATOF 轨迹格式、OTel、遗传算法+Optuna 自动调参）；编排原语是 `sequential_executor`/`parallel_executor`/`router_agent` 加 react/rewoo/MoA 等 agent `_type`。与 GPU 栈的绑定点在 `NIMModelConfig`/`DynamoModelConfig`（本地 NIM、Dynamo 优化，worker 是 SGLang/vLLM）。NeMo-Relay 则是 agent 之下的可移植执行运行时（Rust 核心+PyO3/NAPI/Go 绑定）：策略与遥测打包一次跨框架复用，`nemo-relay claude/codex/pi` 用 TransparentRun 透明包住 Claude Code 进程（把 `ANTHROPIC_BASE_URL` 指向本地网关 sidecar）——**NVIDIA 愿意给竞品的大脑配自己的身体**。Personal-AI-Router（1535 star）是这根线的家用端：Electron+13 个 Go 服务管一组局域网机器上的 Ollama/LM Studio，mDNS 发现、抢占 11434/1234 默认端口实现零配置接管、按"模型可用+GPU 压力 0-3 级"打分路由、EAP-NOOB+6 位 PIN 配对 mTLS。

### 3.5 横向对照：三种 agent 治理学

把 DeepSeek dsh-superagent、Claude Code、NVIDIA 栈放在同一张桌上，差异一目了然：

| 维度 | DeepSeek dsh | Claude Code 式 CLI | NVIDIA 栈（OpenShell/NemoClaw） |
| --- | --- | --- | --- |
| 大脑 | 自家 harness | 自家模型+CLI | 不管：OpenClaw/Hermes/DeepAgents 都行 |
| 授权单位 | Eval→Mandate（不可变授权物） | 会话内逐次 permission prompt | 策略变更的差异（Z3 预验证+新端点人审） |
| 信任实现 | 提示词五级层级+host 强制 | host 权限系统 | **内核强制+形式化验证+网关注入凭证** |
| 注意力/成本经济学 | 一次一个问题、安静为默认 | 人在环 REPL | tolerance=0.20 的 P(correct) 成本路由 |
| 影子模式 | observe（研判只记录不执行） | plan mode | prover 报告+已有端点自动批/新端点冻结 |

三家其实在解同一道题——**稀缺资源（人的注意力、token 成本、信任）怎么定价和发放**——但押注的层不同：dsh 押在"授权模型"（工单/准入表），Claude Code 押在"交互协议"（会话内权限），NVIDIA 押在"基础设施"（OS 层强制+形式化+SARIF 供应链）。NVIDIA 的差异化一言以蔽之：**不做更聪明的 agent，做让企业 CISO 敢签字的那一层，然后把推理水流引向 NIM 云或 DGX 本地**。OpenClaw 爆红出的安全真空，被它做成了带 GPU 出货的销售话术。

## 四、程序员实操：三条上手路线

**路线 A：先碰公寓（OpenShell 最小闭环，任何 Linux/Mac ARM 机器）**

```bash
curl -LsSf https://raw.githubusercontent.com/NVIDIA/OpenShell/main/install.sh | sh
openshell sandbox create --name demo        # 默认最小 Ubuntu，无 agent
```

跑真 agent 按 docs 的 "Run Your First Agent"（官方例子用 OpenCode + 免费 OpenRouter 模型，顺带体验"新端点等人审"的审批流）。再给自己常用的 coding agent 装官方技能：`npx skills add NVIDIA/OpenShell`——四个技能（`openshell-cli`/`generate-sandbox-policy`/`debug-inference`/`debug-openshell-cluster`）教它驱动 CLI、写沙箱策略、排查推理路由。

**路线 B：全托管管家（NemoClaw，DGX 或 WSL 主机）**

跑 `install.sh`，在 `Run express install with these settings? [Y/n]` 直接回车走推荐预设（默认装 OpenClaw）；输 `n` 可交互选 Hermes/DeepAgents、沙箱名、推理 provider 与模型。想改门禁就往 `nemoclaw-blueprint/policies/presets/` 加 YAML（仓里有 `github.yaml`/`brave.yaml` 样板）；本地推理选 `nim-local`/`vllm` profile，DGX Spark/Station 用户直接套 26 个 managed-inference 预设，readiness 检查会自己判定你的硬件资格。

**路线 C：技能编写-扫描-评估-分发闭环（供应链工程师视角）**

1. 写 `SKILL.md`：agentskills.io 规范的 frontmatter（`name`/`description`/`license`——NVIDIA 仓 license 必填）+ 步骤正文；
2. 扫描：`skillspector scan ./my-skill/ --no-llm` 先过零依赖静态层（regex/AST/YARA），`--format sarif --output report.sarif` 直进 CI；要语义层再配 LLM provider；
3. 评估：SkillEvaluator Tier3 沙箱实测拿 Skill Lift（with_skill vs baseline，±0.05 判改进/回归）；
4. 分发：PR 进产品上游仓，`components.d/` 注册表每日 sync 到 `NVIDIA/skills` 镜像。

**调试锚点**：策略想改先看 prover 报告（`openshell` 的 policy diff 会标出新授予的访问）；本地 vLLM 预设不就绪时看 GPU proof 的 diagnostic（它区分"没卡"和"卡在但驱动撒谎"）；做 agentic serving 评测直接抄 TRT-LLM blog27 的轨迹回放+job 级指标方法论（`docs/source/blogs/tech_blog/blog27_*.md`）。

## 五、批判边界：新贵的另一面

1. **alpha 是自称，不是谦虚**。NemoClaw README 原文："NemoClaw is an alpha project...best effort basis without guaranteed response timelines"；blueprint 把 OpenShell 版本钉死在单一 `0.0.116`（`blueprint.yaml:6-7`）——这是接口还在剧烈震荡的直接证据，升级一次全链重验。三仓成熟度：OpenShell（0.1.x 稳定节奏+升级指南）> SkillSpector > NemoClaw。
2. **star 与生产的距离**。22615 star 的仓，2026-10-01 还在修"选沙箱 pod 时 DNS 生成后缀匹配"这类基础缺陷（本地镜像最新提交 ccf68da）。GTC 发布+官方"周末项目"视频带 star 的速度远超工程收敛速度。真要上生产：NAT（企业编排线，历史更长）与 OpenShell 可试；NemoClaw 的自我定位就是 **reference stack**（参考栈）——名字已经劝退生产用途。
3. **隐私叙事与云端默认的张力**。卖点之一是"数据不出内网"，但 default 推理 profile 指向 `integrate.api.nvidia.com`；本地化要自跑 NIM/vLLM，且预设的 readiness 门以 DGX 硬件资格为前提——**隐私是可选配的，且默认要花钱买硬件**。
4. **形式化验证的边界**。prover 验证的是"策略+能力注册表+凭证作用域"这个**模型**的性质；binary capability registry 靠嵌入维护，注册表漏登一个二进制的能力，"无发现"就是假阴性。验证模型 ≠ 验证世界。
5. **扫描器的漏报面**。SkillSpector 语义层 precision-over-recall（confidence≥0.6 才报）——供应链门禁选择"少打扰"，代价是定制混淆天然漏；Skill Lift 的 ±0.05 阈值依赖 baseline 稳定，LLM 评测方差可能吃掉信号。
6. **四条编排线并行的战略噪音**。NAT（工作流编排）、NemoClaw（托管 agent）、TRT-LLM 仓里的 agent-flow（torch 风格多 agent 编排）、NeMo-Relay（执行运行时）——2026 年的 NVIDIA 自己在同时下四注，学习者应先按场景选线（个人管家=NemoClaw 系；企业流水线=NAT；serving 评测=agent-flow），别贪全。

## 六、费曼检验

合上文章自测三题：

1. **NemoClaw/OpenShell/OpenClaw 三者分工是什么？为什么没有 agent loop 的 NemoClaw 反而是 org star 第一？**（答不出"公寓/物业/管家"分工与"信任空白+GTC 叙事+GPU 水渠"三条，就回第一节。）
2. **OpenShell prover 在策略变更流程的哪一步、用什么工具、验证什么性质？为什么说 NVIDIA 栈的授权单位是"端点增量"而 Claude Code 是"工具调用"？**（答不出 Z3 SMT 可达性查询与新端点人审，回 3.2。）
3. **Skill Lift 怎么算、阈值多少？SkillSpector 为什么坚持 fail-closed 三态（没扫到≠通过）？**（答不出 with_skill−baseline±0.05 与 inspection ledger，回 3.3。）

**一句话总结**：NVIDIA 的 agent 新贵不造大脑、造"企业敢签收的那一层"——OpenShell 用内核强制+Z3 把信任下沉到基础设施，NemoClaw 用 blueprint 把推理水流引向 NIM 云或 DGX 本地，SkillSpector/skills 把技能做成有背景审查的供应链；而这一切的底层逻辑，是 agentic 负载把"每张 GPU 养活几个 agent"变成了新的卖卡单位。

## 勘误（版本矛盾与考据注记）

1. **deepwiki 滞后于源码**：NeMo-Agent-Toolkit 的 wiki 版本史仅覆盖 v1.7.0–v1.9.0，未记载 NeMo-Skills→Agent Toolkit 品牌化；前身身份由 NVIDIA-NeMo/Skills 仓（"pipelines to improve skills of LLMs"）与 2025-06-25 开发者博客（AIMO2 流水线）佐证，**官方改名公告查无**。
2. **两个易错命名（本文预研时的自我纠错）**：nurec-skills/instant-nurec 是**神经重建**（Neural Reconstruction，AV/机器人仿真的 3DGS 流水线）技能集，不是录音/会议 agent；personaplex（10589 star）是 Moshi 架构+Helium 7B 的全双工语音对话模型，不是 persona 管理平台。两者均未纳入主线。
3. **star 口径**：`_org_repos.NVIDIA.jsonl` 为 2026-10-01 快照；NemoClaw 本地镜像 3 天 17 个提交，数字与排位随时会变。
4. **时间线证据等级**：GTC 2026 发布（2026-03-16 nvidianews 公告）、OpenClaw 血统（Clawdbot→Moltbot→OpenClaw，Wikipedia/CNBC 2026-02-02）来自 web 二手权威源；本地镜像 git 历史截断（2026-09-29/30 起），无法本地考据发布史。
5. **"token 用量 34×"为二手转述**（Data Center Frontier 引黄仁勋引 OpenRouter），原始口径未直接核验；AA-AgentPerf 57.5/19.2 CPG、KV 命中率 0.97、+18.76% 前缀命中率均为 TRT-LLM 博客一手数据（blog26:63、blog27、blog23:190）。
6. **TRT-LLM 仓快照无 agentperf 脚本**：agentic 基准内容集中在 `docs/source/blogs/tech_blog/` 文档层，`benchmarks/` 目录不存在；deepwiki 亦无 AgentPerf 专页——引用一律以 blog 行号为准。
7. **SkillSpector 默认 LLM provider 随版本浮动**：deepwiki（2026-10-26 抓取）记为 NVIDIA Build 端点的 `z-ai/glm-5.2`，本地 `model_registry.yaml` 同时列 OpenAI/Anthropic 系——用前先 `--help` 确认，别按本文数字硬编码。
