# Harness × Ensemble × 领域 Harnessing：三线综述合并解析

> card_id: harness-ensemble-domain-synthesis
> universe: 前沿与媒体 / harness 镜
> burke: 场景=生产级 LLM 系统；主体=AI 工程师；能动=合并三线综述；行动=解析→落地→NFL 分析；目的=可执行的架构决策；张力=harness 收益巨大 vs 每个选择都有代价；弧线=从"模型决定论"到"系统决定论"再到"组合权衡论"
> status: done
> refs: 全部引用经一手核实，见 [.research/harness-survey/引用核实报告.md](./.research/harness-survey/引用核实报告.md)
> updated: 2026-08-17
> 来源：用户提供的"三篇综述拆解"（含 6 处错误，已全部修复——修复明细见引用核实报告 F1-F6）

---

## 〇、文献地图（修正版速览）

拆解文本把 harness 综述当成两篇，实际经核实是**四篇**（2026 上半年密集涌现）+ Ensemble 一篇 + 领域四篇：

| 综述 | 出处 | 核心贡献 | 关系 |
|---|---|---|---|
| **Meng et al. 2026.04** | preprints 202604.0428 v3 | 六组件 **H=(E,T,C,S,L,V)** + 23 系统 Completeness Matrix | 枚举式分类学 |
| **Li et al. 2026** | OpenReview (Agent Harness Engineering: A Survey) | 七层 **ETCLOVG**（Observability/Governance 独立成层） | 生产控制面视角 |
| **Ning et al. 2026.05** | arXiv:2605.18747 | **Code as Agent Harness** 三层（Interface/Mechanisms/Scaling） | 代码中心视角 |
| **Guo et al. 2026.06** | arXiv:2606.20683 | **model–harness 耦合**六运行时责任 + 四范式演化 | 工程范式史视角 |
| **Chen et al. v6** | arXiv:2502.18036 | LLM Ensemble 三阶段分类（before/during/after inference） | 模型选择侧 |
| **Chen Z. et al. TMLR 2024** | arXiv:2405.01769 | FHL（金融/医疗/法律）领域综述 | 领域压力侧 |
| ACM TGCare 2025 | DOI 10.1145/3744660 | 临床信息提取（**85 篇**，非 129） | 领域 |
| Multimodal Trans. 2026 | DOI 10.1016/j.multra.2026.100308 | 智能交通（129 篇） | 领域 |

**拆解文本的六处已修复错误**（详见核实报告）：①六组件归属张冠李戴（实为 Meng et al.，非 Li et al.）；②临床综述 129→85 篇；③Hybrid LLM 是 ICLR **2024** 非 2025；④2605.18747 是独立 survey（主标题 Code as Agent Harness）；⑤"TerminalBench +26%/数学+4.7pp"摘要级来源未证实（Meng 原文只说 order-of-magnitude，AHE 论文在 Terminal-Bench 2 实测 +7.3pp）；⑥Edd Mann 博客正确标题 "Around the Loop: Building a Coding Agent Harness in Python"。
**Ensemble 分类学修正**：v6 的 (a1)/(a2) 划分是 **Discrete Utility / Continuous Utility**（旧版/拆解文本的 "Pretrained/Non-pretrained Router" 已废弃）；"Park et al. 2024"（LE-MCTS）属 (b3) process-level 而非 token-level Selection。

---

## 一、任务 1：完整合并解析

### 1.1 统一世界观：一个公式接两条线

```
生产级 AI 系统 = Harness( Model(s), Tools, Context, State, ... )

  Ensemble 回答：Model(s) 位置放什么、放几个、何时换   ← 模型选择
  Harness 回答：这个位置周围的一切如何安全地运转      ← 运行时治理
  领域 Harnessing 回答：在 FHL/交通/临床的约束下，上面两者怎么改
```

三条综述线不是并列关系，而是**同一系统的三个正交切面**：
- **Guo et al. 的四范式演化**给出历史动量：prompt engineering（怎么问）→ workflow/context engineering（给什么信息）→ **harness engineering**（怎么闭环）→ agent-native co-evolution（模型与 harness 共同进化）。每次迁移都是因为前一范式撞墙：prompt 解决"表达问题"解决不了"信息问题"；context engineering 是前馈的，解决不了"漂移检测与错误恢复"——harness 闭环才解决。
- Ensemble 是"多模型"维度在同一演化轴上的展开：Guo et al. 明确指出 Phase 3 内部正在出现 multi-model harness（运行时路由/委派/组合异构模型），Ensemble 综述正是这个子空间的方法全集。
- 领域综述提供压力测试：FHL 五共通约束（专业知识/机密数据/多模态文档/法律风险/可解释公平）是 harness 配置的强制边界条件。

### 1.2 Harness 解剖学：四种切法的对照与统一

四篇综述对同一对象切了四刀，刀刀不同但互补：

| 切法 | 组件 | 独有洞察 |
|---|---|---|
| Meng 六组件 | E 执行循环 / T 工具注册 / C 上下文 / S 状态存储 / L 生命周期钩子 / V 评估接口 | **Completeness Matrix 实证**：生产级系统全部六组件齐备；缺 L 无法执行安全策略，缺 V 无法调试，缺 S 无法崩溃恢复 |
| Li 七层 ETCLOVG | E/T/C/L + **O 可观测性 + V 验证 + G 治理** | O 和 G 在生产中各有独立工具栈、归不同团队——所以必须独立成层，不是 T 或 L 的附属 |
| Ning 三层 | Interface（code for reasoning/acting/environment）/ Mechanisms（planning/memory/tool use/control）/ Scaling（multi-agent 共享工件） | **代码为什么是最佳 harness 媒介**：可执行（形式验证）、可检视（结构化 trace）、有状态（程序=任务进度）。scope 边界：code 不替代感知/意图/隐式推理，只使其可执行化 |
| Guo 六责任 | observation / context / control / action / state / verification-governance | **运行时视角**而非组件清单：memory 在功能环里是 state，在部署中由 context 选择+工件存储+检索索引+checkpoint 任一实现；action 由 schema+权限+沙箱+API 中介 |

**统一最小共识集**（四刀的交集，即"任何生产 harness 不可少"）：

```
1. 执行循环 E（observe-think-act + 终止条件 + 错误恢复）
2. 工具/动作接口 T（类型化 schema、路由、校验、监控）
3. 上下文管理 C（什么进窗口、压缩、检索）
4. 状态持久化 S（跨轮/跨会话、崩溃恢复）
5. 验证与治理 V+G（测试、断言、权限门、沙箱、回滚、审计）
6. 可观测性 O（每个决策留痕——Li 独立成层的理由）
```

Meng 的 L（lifecycle hooks）与 Guo 的 verification-governance 在实践中融合：`prepare_context / authorize_tool_call / process_tool_result / on_event` 这类钩子正是挂载权限门与审计日志的位置（注意：这组钩子名来自 harness 实现层如 Pi/AWS harness-sdk，非 Meng 论文原文——拆解文本混入了实现细节）。

### 1.3 核心实证：harness 是瓶颈的证据链

| 证据 | 数字 | 来源 |
|---|---|---|
| Anthropic 对照实验（同模型同任务，仅改 harness） | 无 harness $9/20min 产出不可用 → 全套 harness $200/6h 产出可玩游戏 | walkinglabs 教程转述（二手） |
| Meng et al. 调研结论 | **order-of-magnitude** 可靠性提升（模型不变，仅 harness 重设计） | preprints 202604.0428 摘要 |
| AHE 自动进化 harness（GPT-5.4-high） | Terminal-Bench 2: 69.7%→77.0%（**+7.3pp**，超人工设计 Codex 71.9%）；冻结迁移 SWE-bench-verified 最高聚合成功且省 12% token；跨 3 个模型家族 +5.1~+10.1pp | arXiv:2604.25850 |
| AHE 消融（关键！） | 增益定位在 **tools/middleware/长期记忆**；**仅改 system prompt 反而回退** | 同上 |
| 拆解文本称"TerminalBench +26%/数学+4.7pp" | ❌ 摘要级来源未证实，暂不采用 | 核实报告 F5 |

**解读**：harness 收益是**结构性**的（代码化工件承载协调模式），不是**文案性**的（提示词）。这与 Ning 的"code as harness"论点互为印证：可执行/可检视/有状态的媒介才承得住可靠性。

### 1.4 Context Management：趋同解的精确参数（已核实，可直接引用）

四大 harness（Pi / OpenClaw / Claude Code / Letta）独立收敛到同一套模式（Arize 2026-04-28 一手分析）：

| 机制 | Pi | OpenClaw | Claude Code | Letta |
|---|---|---|---|---|
| 文件读取上限 | 2000 行 / 50KB | 继承 Pi + bootstrap 12K/文件、60K 总量（75%头/25%尾） | **256KB byte 预检（stat）+ 25K token 读后计数双层门**；默认 2000 行；超 2000 字符行截断 | 按模型窗口分五档（5K/15K/25K/40K chars）；同时打开 3~15 个文件 LRU 驱逐 |
| 分页 | offset/limit + 续读提示 | 同 | 同（错误信息直接教模型用 offset/grep） | open/grep/semantic_search 三工具 |
| 工具结果上限 | ✓ | 16K chars 或 30% 窗口 | 50K chars/工具、200K chars/消息（每次 API 调用前预防性落盘+2KB 预览） | 30K bash/子代理、10K grep |
| 压缩触发 | contextWindow − 16384（保留最近 ~20K token，其余 LLM 摘要为合成 user 消息） | 历史 >50% 窗口；token 均衡分块丢最旧+多阶段摘要；**压缩前静默 agentic turn 把状态持久化到内存文件** | ~167K/200K（13K buffer）；9 部结构化摘要提示词；压缩后回挂最近 5 个文件 | 90% 窗口；滑动窗 30%起+10%步；溢出两级回退（工具结果截 5K → 30%头+30%尾） |
| 边界安全 | 压缩时回滚保证 tool_call/result 配对 | 同 | 同 | — |
| 子代理隔离 | 默认只给任务字符串 | 默认隔离；fork 仅复制 allowlist（AGENTS.md/TOOLS.md/SOUL.md） | 默认空白会话；fork 复制父 transcript+合成 assistant 消息+placeholder 结果 | 默认隔离 |

**趋同的深层原因**：上下文管理被重新定义为经典系统问题——**固定尺寸工作集管理**（"让 200K token 用起来像 200T"）。Arize 自家数据探索产品 Alyx（非编码域）独立收敛到同一套（10K token 工具上限、幂等去重、char/4 估算、50K checkpoint），证明这是任务无关的结构解而非编码域巧合。
另一条独立趋同线（Zylos 2026-07 分析）：三层渐进披露（常驻身份层 → 指针/引用层 → 按需全文层），且**稳定前缀必须放最前且永不修改**（缓存经济学），易变状态放最后（注意力经济学）。Claude Code 自己的 CLAUDE.md 指引："前沿模型可靠遵循的指令上限约 150-200 条，系统提示词已用掉约 50 条"——指令跟随是有预算的。

### 1.5 记忆系统四层（Meng/Ning 综述交叉）

| 层 | 管什么 | 代表 |
|---|---|---|
| Working Memory | 修复轨迹、运行时编辑状态 | SWE-agent, CodeMem |
| Semantic Memory | 仓库结构、代码证据、检索片段 | AutoCodeRover, RepoCoder |
| Experiential Memory | 轨迹反思、经验教训回放 | ExpeL, MemGovern |
| Long-term Memory | intent-to-code 映射、验证过的修复 | MemCoder, TALM |

2026 新趋势（Letta Context Repositories）：记忆=git 仓库——agent 自己写/合并/回滚记忆，多子代理在隔离 worktree 并发学习再 git 合并。与 work4ai 的 `.agent/MEMORY.md` 约定同构（策展规则=commit 规范）。

### 1.6 LLM Ensemble 完整分类学（v6 修正版）

```
(a) Ensemble BEFORE Inference —— 推理前路由（粒度: response ♣ 目标: 性能+成本）
 ├─ (a1) Discrete Utility（离散效用）
 │   ├─ Classification-based：二元"满意/不满意"多标签分类 → 加成本加权选模型
 │   │   代表: Hybrid-LLM (ICLR 2024, DeBERTa 路由器, 40% 少调大模型无质量损失)、
 │   │         SelectLLM、Routoo、CSCR、RADAR、FORC
 │   └─ Comparison-based：只学成对偏好 (q, M1, M2, y)，降低监督难度
 │        代表: RouteLLM、P2L、Bench-CoE、Meta-Router、Eagle
 └─ (a2) Continuous Utility（连续效用：回归/策略学习）
     代表: MetaLLM、MixLLM、IRT-Router、OmniRouter、TO-Router、HomoRouter、
           PickLLM、LLM-Bandit (Li et al., 多目标策略梯度)

(b) Ensemble DURING Inference —— 推理中融合（粒度: token ♣♣♣ 目标: 性能）
 ├─ (b1) Token-level
 │   ├─ Aggregation-normal：先解决词表不对齐！
 │   │   GaC(并字典)、DeePEn/EVA(相对表示空间, Xu et al. 2024)、
 │   │   UniTe(Yao et al. 2024, TOP-K 截断聚合省算力)、PackLLM(perplexity 加权)
 │   ├─ Aggregation-specific-goal：DeRa(解码时重对齐)、MOD(多目标解码)、
 │   │   版权/投毒缓解(Li et al.: 小模型 token 掺入大模型)
 │   ├─ Aggregation-finetuning：Copilot/LLMBoost(boosting+SFT)、UltraFuser(MoE 门控)
 │   └─ Selection：CDS(Jin et al. 2024, critical-token 分类器→pretrained 贪心解码)、
 │        Co-LLM(潜变量 defer, ACL 2024)、CITER(RL 策略)、ABE(一致性交集)
 ├─ (b2) Span-level：生成-评估-选择管线，perplexity 互评
 │   Cool-Fusion(词边界)、SweetSpan/SpecFuse(定长)、CoS(投机解码加速)
 └─ (b3) Process-level：推理链逐步选择
     LE-MCTS (Park et al., MCTS 逐步选最高奖励) ←拆解文本误置于 token-level

(c) Ensemble AFTER Inference —— 推理后整合（粒度: response ♣）
 ├─ (c1) Non-cascade
 │   ├─ Selection: Agent-Forest(同模型多次采样 MV+scaling 律)、
 │   │   Smoothie(NeurIPS 2024, 嵌入质心距离=弱监督质量分, 免标签)、
 │   │   LLM-PeerReview(LLM-as-Judge 互评)、MoRE(随机森林监督选择)
 │   └─ Selection-then-regeneration: LLM-Blender(PairRanker+GenFuser 开山)、
 │       LLM-TOPLA(最大化多样性选子集)、URG(端到端统一)
 └─ (c2) Cascade：deferral rule 是灵魂
     ├─ Unsupervised: EcoAssistant(用户判断)、答案一致性(多提示采样)、
     │   class-uncertainty 家族(MSP/到均匀分布距离/margin/熵)、
     │   Model Cascading(先驱)、neural caching(蒸馏)、Cascade Routing(路由+级联)
     └─ Supervised: post-hoc deferral(Jitkrittum, 同时估下一级模型的不确定性)、
         FrugalGPT(TMLR 2024, DistilBERT 评分+阈值链, 98% 降本 or +4% 同成本)、
         Gupta et al.(ICLR 2024, token 级不确定性的分位数特征)、
         AutoMix(Aggarwal, MDP)、DER(Hu, MDP+答案一致性)

基准: MixInstruct(after)、RouterEval/RouterBench/FusionFactory/RouterArena/LLMRouterBench(before)
综述自提四方向: ①标签高效模型画像 ②开放动态设置(模型池随时间变) ③span-level 潜力 ④cascade×routing 组合
```

**关键机制补全**（拆解文本没讲透的三点）：
1. **词表对齐是 token 聚合的拦路虎**——不同 LLM 词表不同无法直接平均分布，GaC/DeePEn 的对齐技术是一切 (b1) 聚合的前置。
2. **Selection 与 Aggregation 的本质差异**=硬投票 vs 软融合；regeneration 最贵（要训练数据+训练生成器）。
3. **Cascade 的 deferral rule 谱系**：用户判断 → 答案一致性 → 不确定性（无监督）→ 评分函数/MDP（监督）——越往右越准越贵。post-hoc deferral 的巧思：不只看当前模型不确定性，还预估**下一级更强模型**能不能救——这是对"级联误判成本"的直接回应（任务 3 会回来用）。

### 1.7 Harness × Ensemble 的接缝：router 住在哪里

合并两线后，多模型系统的分层架构：

```
┌─ V/G 治理层（权限、审计、预算、回滚）
├─ O 可观测层（每次模型调用+路由决策留痕）
├─ E 执行循环 ──┐
│              ├─ Router/Ensemble 决策点（Ensemble 综述的全部方法住这层）
├─ T 工具注册 ──┘     ↓ 单次/多次调用
├─ Model Providers（N 个异构模型 = harness 的 "provider 抽象"层）
├─ C 上下文管理（压缩/分页/检索——对路由后的模型透明）
└─ S 状态存储（会话/记忆/工件）
```

- Edd Mann 七环中的 **provider 环**就是 router 的宿主：provider-agnostic 抽象（OpenAI/Anthropic/兼容 API）+ 可插拔选择策略。
- Ensemble 综述的 Direction 4（cascade×routing 组合）= 把 (a) 的预判与 (c2) 的后验止损叠加——正好对应 Cascade Routing（eth-sri）与 Dekoninck et al. 的 "cascade routing" 理论统一（最优性证明）。
- **C 组件对多模型的新约束**（拆解文本完全遗漏）：不同模型窗口尺寸不同（Letta 按模型分五档就是先例）、压缩摘要的模型选择、fork 子代理用便宜模型压缩+贵模型执行的分工——harness 的上下文策略开始依赖 router 的决策。

### 1.8 领域 Harnessing：领域压力 → harness 配置映射

Guo et al. 的"任务压力画像"方法 + 领域综述的实证：

| 领域 | 强制约束 | harness 配置的含义 |
|---|---|---|
| 金融/医疗/法律（FHL） | 五共通：专业知识、机密数据、多模态文档、法律风险、可解释公平 | L 组件升权（合规钩子前置）；V 组件必含审计 trace；本地部署/私有化模型优先（机密数据）；多模态文档→C 组件需结构化解析；免责/人工审核门 |
| 临床信息提取（85 篇） | 实体抽取 49 篇为最大子类；跨机构泛化差 | LLM 优于 BERT 的场景=低资源+跨机构（i2b2 上 NER +7% F1），但吞吐慢 28 倍——**router 按机构/任务切 BERT↔LLM 是天然 cascade** |
| 智能交通（129 篇） | 不规则空间拓扑、对简单统计模型的实证增益不稳定、实时性 | 不一致实证增益→cascade 先跑便宜统计模型，LLM 只处理复杂时空推理；多模态感知融合是开放方向 |
| 系统综述辅助（SE） | 抽取一致性 62-72%（Gemini Pro 72%）不可盲信 | **human-in-the-loop 是 harness 硬件**而非附件：AIDE 模式=LLM 抽取→人确认每格 |

**领域综述的元教训**：领域差异不改变六组件，只改变**组件的权重与实现选择**。FHL 把 L/V 从"生产控制面"升为"产品本体"；临床把 router 变成"模型家族切换器"；交通把 cascade 变成"统计模型→LLM"跨范式级联。

### 1.9 开放挑战合并（三线汇总）

| # | 挑战 | 来源 | 现状 |
|---|---|---|---|
| 1 | 形式化安全模型（OWASP for harness 攻击面） | Meng | 范畴论尝试（arXiv:2605.12239 证书保持同态）刚起步 |
| 2 | 跨 harness 可移植性 | Meng | Trellis 22 平台同构是工程解；Cross-Harness Benchmark 未建成 |
| 3 | 协议互操作 MCP/A2A（工具级 vs agent 级） | Meng | 工具级(MCP)成熟快于 agent 级(A2A) |
| 4 | 百万 token/任务的上下文经济学 | Meng | 三层渐进披露+压缩趋同解是当前实践；经济学最优未解 |
| 5 | 多智能体拜占庭容错 | Meng | 未解 |
| 6 | 组合式验证 | Meng | 2605.12239 直接回应；未实用化 |
| 7 | 运行时监控与干预 | Meng | AHE 的三观测性支柱给出实例 |
| 8 | 动态沙箱与工具权限 | Meng | deer-flow 诚实声明 allowed-tools 非 hard boundary |
| 9 | 人机边界治理 | Meng | Chorus Reversed Conversation / Harness-MU fail-closed |
| 10 | 标签高效模型画像（router 冷启动） | Ensemble D1 | Smoothie 是方向 |
| 11 | 开放动态模型池（新模型随时上下线） | Ensemble D2 | 几乎空白 |
| 12 | 价值感知评估（超越任务成功率：成本/延迟/安全/漂移） | Guo | Harness Evolver/AHE 的 benchmark 观是雏形 |

---

## 二、任务 2：转为具体工程内容

### 2.1 决策树：你的系统该投资哪一层

```
你的痛点是什么？
├─ "模型太笨" → 先确认不是 harness 问题（同模型跑 SWE-bench 对照）→ 真笨才换/加模型
├─ "成本太高"
│   ├─ 单一流量、查询难度可预判 → (a) Router: Hybrid-LLM 式分类路由（40% 降本无损失）
│   ├─ 难度不可预判、可事后验证 → (c2) Cascade: FrugalGPT 式评分级联（98% 降本上限）
│   └─ 两者都要 → Cascade Routing 组合（Ensemble D4 + Dekoninck 最优性）
├─ "长任务跑不完/中途失忆" → C+S 组件：压缩+状态落盘（参数抄 §2.3）
├─ "agent 不可靠/提前宣布完成" → V 组件：验证即证据（测试不过=没完成）
├─ "上下文爆炸" → C 组件：文件上限+分页+工具结果预算+子代理隔离
└─ "高合规领域" → L/V 组件升权 + 私有化 + HITL 门（§2.5）
```

**投资顺序经验律**（综合 AHE 消融 + walkinglabs 教程）：验证闭环(V) > 工具与中间件(T) > 状态与记忆(S) > 上下文策略(C) > 提示词优化(最后)。AHE 证明 prompt-only 收益为负——文案层是 harness 投资的最后一站不是第一站。

### 2.2 最小生产 harness 清单（六组件 × 最小实现）

| 组件 | 最小实现 | 参考 |
|---|---|---|
| E | while 循环 + max_turns 上限 + stop_reason 分支（tool_use 则执行工具回灌） | Edd Mann "Around the Loop"；Thorsten Ball 400 行 Go 先例 |
| T | Pydantic 定义 schema → JSON Schema 导出 → 参数校验 → 执行 → 错误回传 | futureagi 六层指南 |
| C | 文件读取 2000 行/50KB 上限 + offset/limit + 工具结果 16-50K 预算 + 超限落盘留预览 | §2.3 全参数表 |
| S | JSONL 追加式会话日志（禁止整文件重写）+ progress.md + feature_list.json | walkinglabs 最小四文件 |
| L/V | pre-call 权限钩子 + post-call 审计日志 + 测试不过不算完成 | AHE / Trellis Verify |
| O | 每步决策一行日志（时间/模型/token/工具/结果摘要） | Li 的 O 层最小化 |

最小四文件起步（walkinglabs 实证"四个文件，会话立刻显著稳定"）：`AGENTS.md`（指令宪法）+ `init.sh`（环境自检）+ `feature_list.json`（任务账本）+ `progress.md`（进度+证据）。
会话生命周期仪式：START 读四件套 → SELECT 挑一个 → EXECUTE 实现+验证+记证据 → WRAP UP 更新账本+干净提交。

### 2.3 上下文管理参数速查表（可直接抄的核实数字）

```python
# 文件读取（趋同解）
FILE_MAX_LINES = 2000          # 四大 harness 一致
FILE_MAX_BYTES = 50_000        # Pi/OpenClaw; Claude Code 预检 256KB
LINE_MAX_CHARS = 2000          # Claude Code 超长行截断

# 双层防御（token 密集文件会漏过 byte 门）
PRE_READ_BYTE_GATE = 262_144   # stat 预检, 256KB
POST_READ_TOKEN_GATE = 25_000  # 读后计数

# 工具结果预算
TOOL_RESULT_CAP = 50_000       # chars/工具 (Claude Code)
MESSAGE_AGGREGATE_CAP = 200_000 # chars/消息
OVERSIZED_FALLBACK = "落盘 + 2KB 预览"

# 压缩触发（三档任选其一）
PI:      trigger = context_window - 16_384;  keep_recent = 20_000
OPENCLAW: trigger = 0.5 * context_window;     分块丢最旧+多阶段摘要; 压缩前 flush 状态
CLAUDE:  trigger = context_window - 13_000    # ~167K/200K
LETTA:   trigger = 0.9 * context_window;      滑动窗 30%→+10% 步进

# token 估算启发式
ESTIMATED_TOKENS = total_chars // 4           # Alyx char/4

# 子代理
默认: 只传任务字符串, 不传父历史
fork: 复制父 transcript + 合成 assistant 消息 + placeholder 结果（Claude Code）
      或只复制 allowlist 文件 AGENTS/TOOLS/SOUL.md（OpenClaw）

# 系统提示词预算
INSTRUCTION_BUDGET = 150-200 条  # 前沿模型可靠遵循上限; 系统自身已占 ~50
CLAUDE_MD_ADVICE = "<200 行 / 40KB"
```

### 2.4 多模型成本优化 playbook

**Step 1 判断任务类型**：EM-G（精确匹配：数学/代码/事实 QA）→ cascade 的评分函数好写，先上 cascade。OE-G（开放生成）→ 评分难，router 或 Smoothie 式相似度选择。

**Step 2 三层渐进部署**：
1. **零成本层**：置信度 cascade（无监督：MSP/熵阈值）——一天可上线，收益 40-80% 降本；
2. **低成本层**：Smoothie（免标签，嵌入质心距离路由，多任务混合流量最适用）；
3. **投资层**：训练 router（Hybrid-LLM：DeBERTa 300M，10K 标注样本，MixInstruct 起步）或 FrugalGPT 评分函数（DistilBERT 回归器+每级阈值）。

**Step 3 防 routing 事故三条铁律**：
- 路由错误比"全用大模型"更糟的场景（一次错误成本 >> 百次省下的费用）→ 设**风险不对称阈值**，难判样本默认升级不降级；
- 模型池变更（新版本上线）→ router 必须重评估（Ensemble D2 的开放问题，工程上=router 监控漂移+自动回退 all-at-large）；
- 打分函数与业务指标对齐（BARTscore 不等于你的用户满意度——Hybrid-LLM 论文自承认的开放问题）。

**Step 4 token 级（仅自托管）**：API 模型不给 logits/token 概率，(b1) 全家只对自部署开源模型可行。需要词表对齐（DeePEn）或同词表模型对。事实性场景首选 CDS：critical-token 分类器+pretrained 模型贪心解码（TriviaQA ~+6%）。

### 2.5 领域部署 checklist（FHL 向）

```
□ 数据边界: 机密数据 → 私有化部署/零保留 API 条款 (L 组件)
□ 审计: 每次生成留 trace (谁/何时/什么输入/什么输出/哪个模型) (O+V)
□ 免责边界: 诊断/投资建议/法律意见 → HITL 审核门, fail-closed (L)
□ 多模态文档: 表格/影像/音频 → C 组件前置结构化解析管线
□ 评测: 领域基准 (金融: 5 数据集 4 任务; 医疗: Table 4-7 4 任务; 法律: Table 9 3 任务)
        + 公平性/幻觉率单独报告, 不能只报 accuracy
□ 模型选择: 跨机构泛化差 → 按机构路由 (临床实证: LLM 低资源跨机构 +7% F1, 吞吐 -28×)
□ 合规映射: HIPAA/GDPR/SEC/MiFID II → 写进 L 组件策略而非提示词
```

---

## 三、任务 3：没有免费的午餐（NFL）分析

### 3.1 原则与为什么在 LLM 系统中加剧

NFL（Wolpert & Macready）：**对所有问题平均，任何两个优化/搜索算法表现相同**——不存在普适更优的选择。工程含义：每个"更优"都是在**特定任务分布**上的更优，代价在别处。

LLM 系统把 NFL 放大了三倍：
1. **任务分布漂移**：生产查询分布 ≠ 基准分布（RouterBench 自己发现简单 router 在复杂任务上泛化失败）；
2. **组合爆炸**：harness 六组件 × ensemble 三阶段，每层选择都任务依赖；
3. **指标多元冲突**：性能/成本/延迟/安全/公平天然互斥，优化任何一个都是对分布的押注。

### 3.2 十大 trade-off 矩阵

| # | 选择 | 得到的 | 失去的/风险 | 失效场景 | 缓解 |
|---|---|---|---|---|---|
| 1 | **投资 harness vs 升级模型** | 同模型 10× 可靠性 | 工程 人力+维护税；AHE 需 10 轮进化 | 模型本身能力不足时 harness 无米之炊（$9→$200 实验前提=模型够聪明） | 先跑同模型对照实验定位瓶颈真因 |
| 2 | **Router 预判 vs 全走大模型** | 40% 降本 | 路由错误直接吃掉收益；router 泛化到新任务/新模型会漂移 | 难判样本误降级 → 差答案+已付费 | 风险不对称阈值：难判默认升级；router 漂移监控+自动回退 |
| 3 | **Cascade vs 单模型** | 最坏 98% 降本 | 尾部延迟翻倍（全链触发时）；置信度校准差的任务评分函数失效 | 校准差的模型"自信地错" → 级联提前终止 | post-hoc deferral（同时估下一级能否救）；一致性检查双保险 |
| 4 | **Token 级聚合 vs Response 级** | 最细粒度分布信息 | 需 logits 访问（API 不可行）+词表对齐+同步解码算力 | 任何 API-only 场景直接出局 | API 场景退到 span/response 级 |
| 5 | **上下文压缩 vs 全量保留** | 窗口续命、成本降 | 摘要必有信息损失；"压缩后摘要仍丢局部 in-situ 细节"（context governance 实录） | 长任务后期引用早期被压缩掉的细节 → 静默漂移 | 压缩前状态 flush 落盘（OpenClaw）；摘要+工件双轨（细节在外存可回查） |
| 6 | **子代理隔离 vs 共享父上下文** | 干净窗口、省 token | 丢失父任务语境 → 子代理答非所问 | 需要全局视野的委派任务 | fork 模式显式选（复制+placeholder）；任务字符串写足上下文 |
| 7 | **趋同解照抄 vs 自研** | 站在四大 harness 肩上、少踩坑 | 趋同≠最优——可能只是"模仿+局部最优"（四家互相学习+同源作者圈） | 你的任务分布偏离编码场景（Alyx 趋同是强证据但非证明） | 参数抄默认值，但建自己的 harness 评测集回归验证 |
| 8 | **Ensemble 多模型 vs 单模型** | 互补强弱、鲁棒 | N 倍成本/延迟/运维面；一致性冲突（两模型答案都"对"） | 流量小到统计上无法验证 ensemble 收益 | Smoothie 免标签先试收益再决定固化 |
| 9 | **领域微调 vs 通用+RAG** | 领域精度、机密数据可控 | 灾难性遗忘、更新贵、域外崩 | 领域知识频繁更新（法规/指南每季变） | 知识走 RAG、风格走微调的二分法；临床实证: 跨机构=LLM 强, 单域大数据=BERT 够 |
| 10 | **自动化 harness 进化（AHE）vs 人工设计** | 持续改进、超人工（77% vs Codex 71.9%） | 对进化基准过拟合风险（AHE 自己用跨基准迁移实验防）；进化需要跑基准的算力 | 小团队没有 10 轮×全基准的预算 | 冻结迁移验证（AHE 模式：Terminal-Bench 进化→SWE-bench 验证） |

### 3.3 实证锚点：AHE 消融的"两个免费午餐都不免费"

AHE（arXiv:2604.25850）是 NFL 的现成实验证据：
- **harness 内部也没有免费午餐**：同是 harness 改动，tools/middleware/长期记忆每个单独承载全部增益，而 **system prompt 单独改动是负收益**——"harness 有收益"这个命题本身都是分布依赖的（结构层 ✓ / 文案层 ✗）。
- **跨模型迁移非线性**：+2.3~+10.1pp，离饱和越远的模型获益越大（deepseek-v4-flash +10.1 vs GPT-5.4-xhigh +2.3）——**harness 收益随模型能力饱和而衰减**，这直接反驳"harness 收益普适"的解读：它是对模型能力缺口的功能补偿。
- **同家族非单调**：medium +2.3 / high +7.3 / xhigh +2.3——因为 step budget 与 timeout 是按 high 调的，**harness 超参对模型是过拟合的**。

### 3.4 解决方案模式（把 NFL 从宿命变成方法）

1. **组合策略**（对冲分布押注）：cascade routing = 预判(router) + 后验止损(cascade) 的对冲组合；DeRa/MOD 把多目标显式加权而非单目标优化。NFL 说不存在单一最优，但组合策略可以**收窄最差情况**——工程上要的是 minimax 而非期望最优。
2. **任务压力画像**（Guo 方法论）：部署前先刻画三维度压力（任务长度/环境复杂度/风险不对称度），按画像选 harness 配置——把"哪个更好"变成"哪类任务下哪个更好"的可检验命题。
3. **验证即证据 + harness 评测**（评测对象从模型转向 harness）：awesome-harness 清单的 40+ 基准筛选标准="能不能测出 harness 质量而非模型质量"；自己的 harness 上回归测试集，模型/参数变更触发重跑——把 NFL 的分布依赖显式化为回归曲线。
4. **渐进披露的三层架构**（Zylos/多源趋同）：常驻层小而稳 → 指针层 → 按需层。本质是**把"什么进上下文"从一次性决策变成运行时可逆决策**，用检索的柔性对冲任何静态配置的分布错配。
5. **诚实声明边界**（文化解）：deer-flow 明说 allowed-tools 非 hard boundary、沙箱在凭据信任边界内；hive 说"不适合简单实验"——承认每个方案的失效域是 NFL 时代的设计美德。

---

## 四、互链

- 引用核实全文：[.research/harness-survey/引用核实报告.md](./.research/harness-survey/引用核实报告.md)
- harness 镜总入口：[harness精华合入-总入口.md](./harness精华合入-总入口.md)（37 仓蒸馏 + skill）
- harness 蒸馏附录：[harness精华笔记.md](./harness精华笔记.md)（六公理：Agent=Model+Harness/五子系统/验证即证据/渐进披露/诚实边界/元层生长）
- 教学落点：讲透模型宇宙 Part IV（17 能力地图/18 建与选/20 优化部署）——本文是其"多模型+harness"层的文献地基
- 生成本文的原对话拆解输入：用户 2026-08-17 会话（含 6 处已修复错误，勿直接引用原拆解文本的数字）

---
生成：2026-08-17 · 三批 webfetch 核实 + Ensemble v6 HTML 全文提取 · 引用错误修复 6+2 处
