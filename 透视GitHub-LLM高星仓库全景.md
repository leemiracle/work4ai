# 透视 GitHub LLM 高星仓库全景（topic:llm · stars>10K · 240 仓全量）

> 数据快照：2026-08-15 · 来源：GitHub Search API（`topic:llm stars:>10000`，按 star 降序 100×3 页全量分页）
> 三重校验：API total_count=240 = 抓取条数 240 = 附录分类合计 240 ✓ **零遗漏**
> 姊妹篇：[`透视GitHub-AI高星仓库全景.md`](./透视GitHub-AI高星仓库全景.md)（topic:ai · 279 仓 · 2026-08-15 同日快照）——两篇合成 work4ai 的「开源生态观测双镜」：ai 镜看 Agent 基建热，llm 镜看全栈分层。
> 姊妹篇 II：[`透视GitHub-Harness高星仓库全景.md`](./透视GitHub-Harness高星仓库全景.md)（topic:harness · 37 仓 · 2026-08-15 同日快照）——harness 镜看 2026 年爆发的新共识词；本篇 §0 的"ECC 登顶"信号在 harness 镜得到 37 仓正面战场验证。
> 归类方法升级：240/240 **逐仓显式归类**（非姊妹篇的关键词启发式），14 赛道每仓唯一归属。

---

## 0. 一句话总纲

**topic:llm 高星域 = 「LLM 工程学的全栈分层教科书」**：240 仓恰好铺满 **模型权重 → 训练数据 → 推理部署 → 网关路由 → Agent 编排 → 上下文工程 → RAG → 记忆 → 对话前端 → 垂直应用** 的完整价值链，而**教育与资源清单是第一大类（38 仓，15.8%）**——「学 LLM」的 star 需求压过「做 LLM 产品」。对比 topic:ai 域（46% 在造 Agent 基建），llm 域**分层更完整、教育更重、infra 更实**。

---

## 1. 宏观统计（硬数据）

### 1.1 Star 分桶（幂律，但比 ai 域略平）

| 区间 | 仓库数 | 占比 |
|---|---:|---:|
| 100K+ | 15 | 6.3% |
| 50K–100K | 24 | 10.0% |
| 30K–50K | 35 | 14.6% |
| 20K–30K | 52 | 21.7% |
| 10K–20K | 114 | 47.5% |

中位数 21,183；最低 10,033（opencodex）；最高 240,191（affaan-m/ECC）。

**Top 10**：

| # | 仓库 | Stars | 定位 |
|---:|---|---:|---|
| 1 | affaan-m/ECC | 240,191 | Agent harness 性能优化系统（skills/instincts/memory/安全） |
| 2 | NousResearch/hermes-agent | 230,780 | 自成长 Agent |
| 3 | Significant-Gravitas/AutoGPT | 186,608 | 自主 Agent 先驱 |
| 4 | ollama/ollama | 178,533 | 本地模型一键运行 |
| 5 | firecrawl/firecrawl | 167,532 | 上下文 API（抓取为 LLM 服务） |
| 6 | f/prompts.chat | 167,141 | Prompt 集合 |
| 7 | huggingface/transformers | 164,092 | 模型定义框架 |
| 8 | langgenius/dify | 152,465 | Agent 工作流平台 |
| 9 | open-webui/open-webui | 148,816 | 自托管 AI 界面 |
| 10 | langchain-ai/langchain | 144,248 | Agent 工程平台 |

**与 topic:ai Top10 对照**：两域共享 hermes-agent/AutoGPT/firecrawl/prompts.chat/dify/open-webui/langchain 7 席——「Agent 与 LLM 的高注意力区已合流」；llm 域独有 ollama/transformers/open-webui（**跑模型的三件套**），且榜首换成 ECC（**给编码 Agent 做训练与优化的元工具**）。

### 1.2 语言分布：Python 一家独大（与 ai 域的双寡头不同）

| 语言 | 数量 | 占比 | 主战场 |
|---|---:|---:|---|
| Python | 122 | 50.8% | 全链条通吃：训练/推理/编排/教育 |
| TypeScript | 47 | 19.6% | 平台与产品（dify/open-webui/vercel-ai） |
| Jupyter Notebook | 14 | 5.8% | **教育类专用载体** |
| Go | 13 | 5.4% | 推理引擎（ollama/LocalAI）与 CLI |
| Rust | 12 | 5.0% | 高性能层（rtk/memvid/tensorzero/screenpipe） |
| JavaScript | 10 | 4.2% | 技能包与轻工具 |
| 其他/未标 | 22 | 9.2% | HTML 教程、清单、C++/Java/C# |

**规律：ai 域是「Python 造智能，TypeScript 造产品」双寡头（62%）；llm 域 Python 占半壁 + Jupyter 单独成势——llm 域的一半是「学出来的」，不是「做出来的」。**

### 1.3 创建年份：ChatGPT 相变更彻底

| 创建年 | ≤2022 | 2023 | 2024 | 2025 | 2026(至8月) |
|---|---:|---:|---:|---:|---:|
| 仓库数 | 32 | 80 | 39 | 53 | 36 |

- **2023 年后创建 208/240（86.7%）**——高于 ai 域的 73%：llm 这个 topic 本身就是 ChatGPT 相变的产物。
- **2025 年后创建 89/240（37.1%）**——三分之一的高星仓寿命不到两年；ECC/hermes-agent/rtk/headroom 等用半年冲上 10 万级，star 通胀在 llm 域同样显著。
- 存量幸存者（≤2022 的 32 仓）全是经典：transformers(2018)/milvus(2019)/ray(2016)/AutoGPT 前夜的 prompts.chat(2022)/langchain(2022)。

### 1.4 组织集中度：一个中文自学社区 = 一个科技巨头

datawhalechina 6 仓（hello-agents 73K、self-llm、happy-llm、llm-cookbook、easy-vibe、all-in-rag）与 microsoft 6 仓（unilm/agent-lightning/RD-Agent/semantic-kernel/promptflow/graphrag）**并列第一**；huggingface 4 仓（transformers/datasets/peft/chat-ui）第三；langchain-ai 3、NirDiamant 3（个人教育者！）。**没有任何组织占 Top10 两席以上**——llm 域的明星产出中心同样在社区，且「个人教育者」首次进入组织榜（NirDiamant 三仓全 10K+）。

---

## 2. 十四赛道分类图（240 仓全显式归类）

| 赛道 | 数量 | 头部代表 | 一句话判断 |
|---|---:|---|---|
| 01 推理与部署引擎 | 16 | ollama、vllm、sglang、LocalAI | 「跑起来」先于一切；本地化是绝对主线 |
| 02 训练微调与数据 | 13 | transformers、LlamaFactory、unsloth、peft | 模型层工具化生存：全参数→PEFT→数据集三段演进 |
| 03 模型与权重 | 7 | Qwen、ChatGLM2-6B、InternVL、ChatTTS | 权重仓缩编——模型层被巨头收敛，开源仓转向多模态 |
| 04 Agent框架与编排 | 29 | langchain、langgraph、dify、MetaGPT | 第二大类：编排层是 llm 域的「应用服务器」 |
| 05 编码Agent与CLI | 23 | ECC、hermes-agent、OpenHands、qwen-code | harness 工程主战场，Claude Code 经济圈产业链 |
| 06 RAG与知识库 | 17 | llama_index、LightRAG、graphrag、milvus | 检索范式之争（向量/图/无向量/LEANN）全谱系在榜 |
| 07 记忆层 | 8 | mem0、mempalace、letta、MemOS | 独立成科的确认年：腾讯入场，8 仓全 10K+ |
| 08 上下文工程与token经济 | 15 | firecrawl、context7、caveman、rtk | 「Context 工程」取代「爬虫」；省钱即产品 |
| 09 网关路由与LLMOps | 12 | litellm、langfuse、promptfoo、ragas | 生产化三件套：路由/评测/可观测 |
| 10 对话前端与平台 | 16 | open-webui、dify 系、FastGPT 系 | 前端收敛赢家通吃；IM 机器人是中文特色品类 |
| 11 安全红队与越狱 | 7 | system_prompts_leaks、L1B3RT4S、heretic | LLM 特有安全学：提示词考古 + 越狱 + 红队 |
| 12 教育与资源清单 | 38 | LLMs-from-scratch、llm-course、hello-agents | **第一大类**：学 LLM 的 star 压过用 LLM |
| 13 垂直应用与工作流 | 30 | TradingAgents、MoneyPrinterTurbo、browser-use | 金融/内容/浏览器/数据库四大落地方向 |
| 14 topic噪声与非LLM原生 | 9 | ray、kubesphere、casdoor、doocs/md | topic 自由标签的熵：3.75% 噪声率 |

---

## 3. 七大洞察（已过反虚荣自检）

**① 14 层价值链与「讲透LLM」篇目同构——LLM 工程学已成分层产业。** 附录 14 类从模型(03)到垂直(13)无一层缺位：每层都有 10K+ 星玩家、独立工具链和头部组织。这不是巧合，是**LLM 生产关系成熟的标志**：就像 Web 时代「浏览器-服务器-数据库-框架-应用」分层复现。本项目的 [`讲透LLM/`](./讲透LLM/README.md)（00 是什么→01 怎么来的→02 全景图→03 全栈→04 训练与部署→05 前沿）恰好是这条链的**理论镜像**——本附录是其**生态证据**。

**② 推理引擎是第一基础设施，且「本地/端侧」是绝对主线。** 01 类 16 仓合计约 55 万星：ollama 179K 一仓超过大多数赛道总和。更值得注意的是本地化的**极限竞赛**：浏览器内推理（web-llm 18.6K）、4GB 显存跑 70B（airllm 31.2K）、Apple Silicon SSD 缓存（omlx 18.7K）、Rust 单二进制（runanywhere）。「让模型在最差的硬件上跑起来」和「让 Agent 在最贵的模型上省钱」（洞察④）是同一条经济学。

**③ 教育是第一大类（38 仓）——「学 LLM」比「用 LLM」更被需要。** LLMs-from-scratch 103.7K 是 star 效率之王（教程仓击败 99% 的工具仓）；datawhalechina 6 仓约 19 万星构成**中文自学生态**；NirDiamant 一人三仓（GenAI_Agents/RAG_Techniques/agents-towards-production）证明个人教育者可以撬动组织级注意力；llm_interview_note 14.9K、AccumulateMore/CV 23.3K——**面试与转行压力是 star 的直接变现通道**。对本项目的启示：讲透系列的「教学价值」正踩在这个最大赛道上。

**④ token 经济学在 llm 域显学化。** caveman 98.3K（省 65% token）+ rtk 76.2K（CLI 代理省 60-90%）+ headroom 66.4K（压缩工具输出）+ context7 60.8K（最新文档供给）+ repomix 27.9K + toon 25.2K ≈ **38 万星**。当智能按 token 计价，「上下文压缩/供给/格式优化」就是新的性能工程。对应 [`讲透上下文缓存/`](./讲透上下文缓存/README.md)。

**⑤ 记忆层独立成科被最终确认：8 仓全 10K+，大厂入场。** mem0 63.3K + mempalace 58.4K + letta 24.2K + TencentDB-Agent-Memory 21.8K（腾讯把「对话/文档/代码→四类可复用记忆资产」做成团队级产品）+ memvid 16.2K + Memori 16.0K + EverOS 12.0K + MemOS 10.7K ≈ 22 万星。与 ai 域观察互证：「给 Agent 装持久记忆」已从 RAG 分裂为独立基础设施层。对应 [`讲透记忆/`](./讲透记忆/README.md)。

**⑥ 提示词泄露/越狱是 LLM 特有的安全学，攻防两侧都被 star 承认。** 攻：system_prompts_leaks 62.9K + L1B3RT4S 21.0K（越狱提示集）+ heretic 27.6K（自动去除审查）；防：Anthropic-Cybersecurity-Skills 27.8K（817 个结构化安全技能）；红队工具化：promptfoo 24.2K + PentestGPT 14.9K + hexstrike 11.0K ≈ **合计 18 万星**。「研究别人怎么给产品写 system prompt」在 llm 域是被 star 承认的学科。对应 [`欺骗动力学-检测Prompt库.md`](./欺骗动力学-检测Prompt库.md)。

**⑦ topic 是注意力市场，有 3.75% 的熵——且榜首揭示了新王。** 9 个非 LLM 原生仓（ray/kubesphere/casdoor/doocs-md/gitleaks/Halfrost-Field 等）靠自打 llm 标签蹭进榜单，做生态研究必须显式剥离（本文设 14 类兜底）。更重要的信号：**榜首 ECC 240K 不是模型、不是框架，而是「给 Claude Code/Codex 等编码 Agent 做训练与性能优化的 harness 系统」**——元工具（训练 Agent 的工具）登顶，与 ai 域观察的「harness 成为新共识词」互证。对应 [`讲透Agent/`](./讲透Agent/) 与 [`Agent架构模式参考/`](./Agent架构模式参考/)。

---

## 4. 方法论与误差声明（诚实边界）

1. **数据源**：GitHub Search REST API，`topic:llm stars:>10000`，2026-08-15 快照。star 实时变动，本文件是时点数据。
2. **topic:llm ≠ LLM 仓库全集**：topic 由维护者自打，OpenAI/Anthropic 官方仓等大量 LLM 核心仓未打此 topic 不在内；反之 9 个非 LLM 原生仓因蹭标签入榜（已归入 14 类并显式标注）。**结论只在「topic:llm 高星域」内成立。**
3. **分类为逐仓显式归类**（240/240 人工判读名称+描述，非关键词规则）：比姊妹篇的启发式分类更强，但仍可能有个别边界争议（如 dyad 归编码Agent、MaxKB 归前端平台），争议仓不影响赛道级结论。
4. **与姊妹篇阈值不同**：本文 10K / ai 篇 11K；两域头部大量重叠（Top10 共享 7 席），跨篇对比时注意口径。
5. **star 是注意力代理变量**（反虚荣视角）：2025+ 新仓半年冲 10 万级含营销通胀；ECC/hermes-agent 类新高星的「使用量 vs 关注量」未验证。

---

## 5. 与 work4ai 的映射表（融合入口）

| 本项目单元 | 生态证据（附录赛道） |
|---|---|
| [`讲透LLM/`](./讲透LLM/README.md) | 全链镜像：01/02/03 类 ↔ 00-05 篇目 |
| [`讲透RAG/`](./讲透RAG/README.md) | 06 类：向量/图/无向量/LEANN 范式之争全谱系 |
| [`讲透记忆/`](./讲透记忆/README.md) | 07 类：8 仓 22 万星 + 腾讯产品化 |
| [`讲透Agent/`](./讲透Agent/) · [`讲透多Agent协作/`](./讲透多Agent协作/README.md) | 04/05 类：编排 + harness 产业链（ECC 登顶） |
| [`讲透上下文缓存/`](./讲透上下文缓存/README.md) | 08 类：token 经济学 ≈38 万星 |
| [`讲透微调/`](./讲透微调/) | 02 类：LlamaFactory/unsloth/peft/ms-swift |
| [`讲透Prompt/`](./讲透Prompt/) | 09/12 类：promptfoo/prompt-optimizer/prompts.chat |
| [`讲透代码生成/`](./讲透代码生成/README.md) | 05 类 23 仓：编码 Agent 食物链 |
| [`欺骗动力学`](./欺骗动力学-检测Prompt库.md) | 11 类：泄露/越狱/红队攻防 |
| [`用例库/`](./用例库/README.md) | 44 仓已在 topic:ai 深读，重叠仓用例卡直接复用 |

---

## 6. 双域分歧地图（topic:llm × topic:ai 交叉审计）

> 2026-08-15 同日双快照的集合运算：ai 域 279 仓 × llm 域 240 仓。

| 集合 | 仓库数 | 占比 | 含义 |
|---|---:|---:|---|
| **交集**（双标签） | 97 | llm 域的 40.4% | 自我定位同时是「AI 应用」和「LLM 工程」 |
| **llm 独有** | 143 | llm 域的 59.6% | 只认「LLM」身份：全栈工程层 |
| **ai 独有** | 182 | ai 域的 65.2% | 只认「AI」身份：Agent 基建与多模态 |

**三个结构性发现**：

1. **「Top10 合流、长尾分化」**：两域头部共享 7/10 席（hermes-agent/AutoGPT/firecrawl/prompts.chat/dify/open-webui/langchain），但全量只共享四成——注意力在头部合流，身份认同在长尾分裂。
2. **llm 独有区 = 工程全栈层**：Top25 独有仓里是 ollama/transformers/vllm/litellm/milvus/llama_index 这类**基础设施**——它们从不自称「ai 应用」，只自称「llm 工具」。**llm 域比 ai 域更底层**。
3. **中文力量分布逆转**：中文仓在 llm 域占 **23.3%（56 仓 / 144 万星）**，是 ai 域（9%）的 2.6 倍。原因：datawhale 教育系（6 仓）+ 中文模型/微调生态（Qwen/ChatGLM/self-llm/LlamaFactory）都自然打 llm 标签，而 ai 域头部被英文个人开发者占据。**中文社区在「llm 域」是主力玩家，在「ai 域」是边缘玩家。**

---

## 7. 新生代相变观测（2025+ 创建的 89 仓聚类）

> 按「复杂系统」视角（[`复杂系统迭代work4ai.md`](./复杂系统迭代work4ai.md)），2025+ 新生代是生态的**升温期产物**——聚类后显现两条明确的**相变线**：

| 相变线 | 聚类规模 | 成员特征 | 相变判读 |
|---|---:|---|---|
| **harness/技能化** | 31 仓 | ECC(240K)/hermes-agent(231K)/graphify(106K)/caveman(98K)/deer-flow(80K)/learn-claude-code(74K)/awesome-claude-code(52K)… | 从「写 Agent」到「**给 Agent 装器官**」（skills/instincts/hooks/memory）：Agent 主体已由巨头定型，社区创新转移到外挂层 |
| **记忆/AgentOS 化** | 27 仓 | mempalace(58K)/TencentDB-Agent-Memory(22K)/EverOS(12K)/MemOS(11K) + ECC 的 Memory Vault、deer-flow 的 memories… | 「记忆」从 RAG 配件升格为**操作系统**——多家同时用 OS 隐喻，是序参量跃迁的语言学证据 |
| token 经济化 | 12 仓 | caveman/rtk(76K)/headroom(66K)/context7(61K)/toon(25K)… | §3-④ 的年龄切片：**全部是 2025+ 新生代** |
| 多Agent 编排回潮 | 5 仓 | agency-agents-zh/edict(三省六部制)/ai-berkshire/cc-haha | 编排范式从「图框架」（2023 届 langgraph）转向「**角色制+审计链**」（2026 届） |

**与 ai 域姊妹篇互证**：ai 域观察到「harness 成为新共识词」，llm 域的 2025+ 聚类给出定量确认——**89 个新生代仓中 65%（58 仓）属于 harness 或记忆两条相变线**。生态的「序参量」已从「模型能力」切换为「Agent 治理」。

---

## 8. star 效率榜（星/月，反虚荣修正）

> 绝对星数偏向存量仓；星/月速率才反映**当下的注意力温度 T**。计算：当前星 ÷ 创建至今月数。

| # | 仓库 | 星/月 | 总星 | 创建 | 一句话 |
|---:|---|---:|---:|---:|---|
| 1 | DietrichGebert/ponytail | ~51,450 | 102.9K | 2026 | 「最懒资深工程师」技能包 |
| 2 | affaan-m/ECC | ~40,031 | 240.2K | 2026 | Agent harness 优化系统 |
| 3 | Graphify-Labs/graphify | ~26,612 | 106.5K | 2026 | 代码库→知识图谱技能 |
| 4 | JuliusBrussee/caveman | ~24,567 | 98.3K | 2026 | 穴居人语省 65% token |
| 5 | NousResearch/hermes-agent | ~19,231 | 230.8K | 2025 | 自成长 Agent |
| 6 | MemPalace/mempalace | ~14,595 | 58.4K | 2026 | 基准最强的开源记忆系统 |
| 7 | rtk-ai/rtk | ~12,696 | 76.2K | 2026 | Rust CLI 省 60-90% token |
| 8 | esengine/DeepSeek-Reasonix | ~11,531 | 34.6K | 2026 | 前缀缓存稳定的编码 Agent |
| 9 | lidge-jun/opencodex | ~10,033 | 10.0K | 2026 | Codex/Claude Code 通用代理 |
| 10 | headroomlabs-ai/headroom | ~9,485 | 66.4K | 2026 | 工具输出压缩器 |

**三个判读**：

1. **2026 届速度是 2023 届的 8-10 倍**：ponytail 51K/月 vs AutoGPT ≈5K/月（2023）。star 通胀实锤——**跨届比较绝对星数已失效，生态观测必须用速率口径**。
2. **效率榜 Top10 全部是 Claude Code 经济圈**（harness/技能/token/记忆四件套）——注意力温度最高的不是模型层，是 **Agent 治理层**，与 §7 相变观测互证。
3. **监测落地**：`.tools/eco_temp_monitor.py` 月度重跑本快照，星/月速率即生态温度 T 的时间序列（对应复杂系统文件 4.1 的「温度」指标）。

> **落地层（2026-08-15 全量完成）**：llm 独有 143 仓（本文件 §6 交集 97 仓已由 topic:ai E01-E24 深读覆盖）的全部用例卡见 [`用例库/`](./用例库/README.md) **E25-E39 十五册**（A+ 档 README 深画像，140 成功 + 3 仓降级元数据卡显式标注 ⚠）——240 仓深读覆盖率 100%。
> **opencode 集成层（2026-08-15）**：全量 240 仓已结构化为 `~/.config/opencode/skills/llm-landscape/`（SKILL.md 十四赛道决策矩阵 + catalog.tsv 数据层）+ `/stack` 选型命令——本文件从"观测报告"升级为**可查询的生态决策资产**（查询协议见 SKILL.md 使用协议节）。

---

## 附录：全量 240 仓分类清单（按类内 star 降序）

### 01-推理与部署引擎（16 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 178533 | [ollama/ollama](https://github.com/ollama/ollama) | Go | 2023 | Get up and running with Kimi-K2.6, GLM-5.2, MiniMax, DeepSeek, gpt-oss, Qwen, Gemma and ot… |
| 89081 | [vllm-project/vllm](https://github.com/vllm-project/vllm) | Python | 2023 | A high-throughput and memory-efficient inference and serving engine for LLMs |
| 48472 | [mudler/LocalAI](https://github.com/mudler/LocalAI) | Go | 2023 | LocalAI is the open-source AI engine. Run any model - LLMs, vision, voice, image, video - … |
| 31835 | [sgl-project/sglang](https://github.com/sgl-project/sglang) | Python | 2024 | SGLang is a high-performance serving framework for large language models and multimodal mo… |
| 31498 | [AlexsJones/llmfit](https://github.com/AlexsJones/llmfit) | Rust | 2026 | Hundreds of models & providers. One command to find what runs on your hardware. |
| 31150 | [lyogavin/airllm](https://github.com/lyogavin/airllm) | Jupyter Notebook | 2023 | AirLLM 70B inference with single 4GB GPU |
| 23060 | [mlc-ai/mlc-llm](https://github.com/mlc-ai/mlc-llm) | Python | 2023 | Universal LLM Deployment Engine with ML Compilation |
| 18707 | [jundot/omlx](https://github.com/jundot/omlx) | Python | 2026 | LLM inference server with continuous batching & SSD caching for Apple Silicon — managed fr… |
| 18561 | [mlc-ai/web-llm](https://github.com/mlc-ai/web-llm) | TypeScript | 2023 | High-performance In-browser LLM Inference Engine |
| 15881 | [alibaba/MNN](https://github.com/alibaba/MNN) | C++ | 2019 | MNN: A blazing-fast, lightweight inference engine battle-tested by Alibaba, powering high-… |
| 15005 | [GeeeekExplorer/nano-vllm](https://github.com/GeeeekExplorer/nano-vllm) | Python | 2025 | Nano vLLM |
| 12898 | [cocktailpeanut/dalai](https://github.com/cocktailpeanut/dalai) | CSS | 2023 | The simplest way to run LLaMA on your local machine |
| 12485 | [bentoml/OpenLLM](https://github.com/bentoml/OpenLLM) | Python | 2023 | Run any open-source LLMs, such as DeepSeek and Llama, as OpenAI compatible API endpoint in… |
| 11150 | [LMCache/LMCache](https://github.com/LMCache/LMCache) | Python | 2024 | LMCache: Supercharge Your LLM with the Fastest KV Cache Layer |
| 10836 | [mistralai/mistral-inference](https://github.com/mistralai/mistral-inference) | Jupyter Notebook | 2023 | Official inference library for Mistral models |
| 10298 | [RunanywhereAI/runanywhere-sdks](https://github.com/RunanywhereAI/runanywhere-sdks) | C++ | 2025 | Production ready toolkit to run AI locally |

### 02-训练微调与数据（13 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 164092 | [huggingface/transformers](https://github.com/huggingface/transformers) | Python | 2018 | Transformers: the model-definition framework for state-of-the-art machine learning models … |
| 74107 | [hiyouga/LlamaFactory](https://github.com/hiyouga/LlamaFactory) | Python | 2023 | Unified Efficient Fine-Tuning of 100+ LLMs & VLMs (ACL 2024) |
| 71621 | [unslothai/unsloth](https://github.com/unslothai/unsloth) | Python | 2023 | Local UI to run and train LLMs and diffusion models, including Qwen3.8, Kimi K3, MiniMax-H… |
| 22188 | [microsoft/unilm](https://github.com/microsoft/unilm) | Python | 2019 | Large-scale Self-supervised Pre-training Across Tasks, Languages, and Modalities |
| 21839 | [huggingface/datasets](https://github.com/huggingface/datasets) | Python | 2020 | The largest hub of ready-to-use datasets for AI models with fast, easy-to-use and efficien… |
| 21550 | [huggingface/peft](https://github.com/huggingface/peft) | Python | 2022 | PEFT: State-of-the-art Parameter-Efficient Fine-Tuning. |
| 15170 | [modelscope/ms-swift](https://github.com/modelscope/ms-swift) | Python | 2023 | Use PEFT or Full-parameter to CPT/SFT/DPO/GRPO 600+ LLMs (Qwen3.6, DeepSeek-V4, GLM-5.1, I… |
| 14790 | [ConardLi/easy-dataset](https://github.com/ConardLi/easy-dataset) | JavaScript | 2025 | A powerful tool for creating datasets for LLM fine-tuning 、RAG and Eval |
| 13616 | [Lightning-AI/litgpt](https://github.com/Lightning-AI/litgpt) | Python | 2023 | 20+ high-performance LLMs with recipes to pretrain, finetune and deploy at scale. |
| 12994 | [ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla) | Python | 2023 | Gorilla: Training and Evaluating LLMs for Function Calls (Tool Calls) |
| 12960 | [PaddlePaddle/PaddleNLP](https://github.com/PaddlePaddle/PaddleNLP) | Python | 2021 | Easy-to-use and powerful LLM and SLM library with awesome model zoo. |
| 12360 | [axolotl-ai-cloud/axolotl](https://github.com/axolotl-ai-cloud/axolotl) | Python | 2023 | Go ahead and axolotl questions |
| 11747 | [ludwig-ai/ludwig](https://github.com/ludwig-ai/ludwig) | Python | 2018 | Low-code framework for building custom LLMs, neural networks, and other AI models |

### 03-模型与权重（7 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 39765 | [2noise/ChatTTS](https://github.com/2noise/ChatTTS) | Python | 2024 | A generative speech model for daily dialogue. |
| 21590 | [QwenLM/Qwen](https://github.com/QwenLM/Qwen) | Python | 2023 | The official repo of Qwen (通义千问) chat & pretrained large language model proposed by Alibab… |
| 18936 | [ymcui/Chinese-LLaMA-Alpaca](https://github.com/ymcui/Chinese-LLaMA-Alpaca) | Python | 2023 | 中文LLaMA&Alpaca大语言模型+本地CPU/GPU训练部署 (Chinese LLaMA & Alpaca LLMs) |
| 17753 | [deepseek-ai/Janus](https://github.com/deepseek-ai/Janus) | Python | 2024 | Janus-Series: Unified Multimodal Understanding and Generation Models |
| 15530 | [zai-org/ChatGLM2-6B](https://github.com/zai-org/ChatGLM2-6B) | Python | 2023 | ChatGLM2-6B: An Open Bilingual Chat LLM 开源双语对话语言模型 |
| 12955 | [zai-org/CogVideo](https://github.com/zai-org/CogVideo) | Python | 2022 | text and image to video generation: CogVideoX (2024) and CogVideo (ICLR 2023) |
| 10130 | [OpenGVLab/InternVL](https://github.com/OpenGVLab/InternVL) | Python | 2023 | [CVPR 2024 Oral] InternVL Family: A Pioneering Open-Source Alternative to GPT-4o. 接近GPT-4o… |

### 04-Agent框架与编排（29 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 186608 | [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | Python | 2023 | AutoGPT is the vision of accessible AI for everyone, to use and to build on. Our mission i… |
| 152465 | [langgenius/dify](https://github.com/langgenius/dify) | TypeScript | 2023 | Build Agentic workflows, RAG pipelines, with rich AI model and tool support on one collabo… |
| 144248 | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | Python | 2022 | The agent engineering platform. |
| 80027 | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | Python | 2025 | An open-source long-horizon SuperAgent harness that researches, codes, and creates. With t… |
| 69820 | [FoundationAgents/MetaGPT](https://github.com/FoundationAgents/MetaGPT) | Python | 2023 | The Multi-Agent Framework: First AI Software Company, Towards Natural Language Programming |
| 39704 | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Python | 2023 | Build resilient agents. |
| 36770 | [CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) | TypeScript | 2023 | The Frontend Stack for Agents & Generative UI. React, Angular, Mobile, Slack, and more. Ma… |
| 36309 | [reworkd/AgentGPT](https://github.com/reworkd/AgentGPT) | TypeScript | 2023 | Assemble, configure, and deploy autonomous AI Agents in your browser. |
| 29693 | [ComposioHQ/composio](https://github.com/ComposioHQ/composio) | TypeScript | 2024 | Composio powers 1000+ toolkits, tool search, context management, authentication, and a san… |
| 28958 | [agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope) | Python | 2024 | Build and run agents you can see, understand and trust. |
| 28649 | [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | Python | 2025 | A lightweight, powerful framework for multi-agent workflows |
| 28449 | [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) | C# | 2023 | Integrate cutting-edge LLM technology quickly and easily into your apps |
| 27209 | [mastra-ai/mastra](https://github.com/mastra-ai/mastra) | TypeScript | 2024 | Mastra is the modern TypeScript framework for AI-powered applications and agents. |
| 26839 | [Fosowl/agenticSeek](https://github.com/Fosowl/agenticSeek) | Python | 2025 | Fully Local Manus AI. No APIs, No $200 monthly bills. Enjoy an autonomous agent that think… |
| 26213 | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | Python | 2019 | Open-source AI orchestration framework for building context-engineered, production-ready L… |
| 26202 | [vercel/ai](https://github.com/vercel/ai) | TypeScript | 2023 | The AI Toolkit for TypeScript. From the creators of Next.js, the AI SDK is a free open-sou… |
| 21119 | [google/adk-python](https://github.com/google/adk-python) | Python | 2025 | An open-source, code-first Python toolkit for building, evaluating, and deploying sophisti… |
| 19302 | [pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai) | Python | 2024 | How Python does AI: agents, realtime voice, image generation, embeddings. Every model, eve… |
| 18253 | [emcie-co/parlant](https://github.com/emcie-co/parlant) | Python | 2024 | Build reliable customer-facing AI agents with Parlant: an interaction control harness opti… |
| 18115 | [RightNow-AI/openfang](https://github.com/RightNow-AI/openfang) | Rust | 2026 | Open-source Agent Operating System |
| 17653 | [TransformerOptimus/SuperAGI](https://github.com/TransformerOptimus/SuperAGI) | Python | 2023 | <> SuperAGI - A dev-first open source autonomous AI agent framework. Enabling developers t… |
| 17482 | [microsoft/agent-lightning](https://github.com/microsoft/agent-lightning) | Python | 2025 | The absolute trainer to light up AI agents. |
| 16374 | [cft0808/edict](https://github.com/cft0808/edict) | Python | 2026 | 三省六部制 · OpenClaw Multi-Agent Orchestration System — 9 specialized AI agents with real-time… |
| 16178 | [googleapis/mcp-toolbox](https://github.com/googleapis/mcp-toolbox) | Go | 2024 | MCP Toolbox for Databases is an open source MCP server for databases. |
| 14230 | [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | Python | 2024 | Research and development (R&D) is crucial for the enhancement of industrial productivity, … |
| 13410 | [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | Python | 2023 | Open-source, secure environment with real-world tools for enterprise-grade agents. |
| 12872 | [langchain4j/langchain4j](https://github.com/langchain4j/langchain4j) | Java | 2023 | LangChain4j is an idiomatic, open-source Java library for building LLM-powered application… |
| 11984 | [tadata-org/fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) | Python | 2025 | Expose your FastAPI endpoints as Model Context Protocol (MCP) tools, with Auth! |
| 10361 | [VoltAgent/voltagent](https://github.com/VoltAgent/voltagent) | TypeScript | 2025 | AI Agent Engineering Platform built on an Open Source TypeScript AI Agent Framework |

### 05-编码Agent与CLI（23 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 240191 | [affaan-m/ECC](https://github.com/affaan-m/ECC) | JavaScript | 2026 | The agent harness performance optimization system. Skills, instincts, memory, security, an… |
| 230781 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | Python | 2025 | The agent that grows with you |
| 102900 | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | JavaScript | 2026 | Makes your AI agent think like the laziest senior dev in the room. The best code is the co… |
| 84082 | [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | TypeScript | 2024 | OpenHands: AI-Driven Development |
| 40790 | [Hmbown/CodeWhale](https://github.com/Hmbown/CodeWhale) | Rust | 2026 | Open-source, community-driven agent harness |
| 34593 | [esengine/DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix) | Go | 2026 | DeepSeek-native AI coding agent for your terminal. Engineered around prefix-cache stabilit… |
| 28844 | [voideditor/void](https://github.com/voideditor/void) | TypeScript | 2024 | — |
| 27019 | [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) | TypeScript | 2025 | An open-source AI coding agent that lives in your terminal. |
| 24889 | [can1357/oh-my-pi](https://github.com/can1357/oh-my-pi) | TypeScript | 2025 | ⌥ AI Coding agent for the terminal — hash-anchored edits, optimized tool harness, LSP, Pyt… |
| 22364 | [winfunc/opcode](https://github.com/winfunc/opcode) | TypeScript | 2025 | A powerful GUI app and Toolkit for Claude Code - Create custom agents, manage interactive … |
| 21247 | [dyad-sh/dyad](https://github.com/dyad-sh/dyad) | TypeScript | 2025 | Local, open-source AI app builder for power users  v0 / Lovable / Replit / Bolt alternativ… |
| 20057 | [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | Python | 2024 | SWE-agent takes a GitHub issue and tries to automatically fix it, using your LM of choice.… |
| 17583 | [1jehuang/jcode](https://github.com/1jehuang/jcode) | Rust | 2026 | The most RAM efficient harness |
| 15587 | [plandex-ai/plandex](https://github.com/plandex-ai/plandex) | Go | 2023 | Open source AI coding agent. Designed for large projects and real world tasks. |
| 14127 | [NanmiCoder/cc-haha](https://github.com/NanmiCoder/cc-haha) | TypeScript | 2026 | Local-first cross-platform desktop workspace for Claude Code / agents: multi-agent, Git wo… |
| 13896 | [fathah/hermes-desktop](https://github.com/fathah/hermes-desktop) | TypeScript | 2026 | Desktop Companion for Hermes Agent |
| 13652 | [opencode-ai/opencode](https://github.com/opencode-ai/opencode) | Go | 2025 | A powerful AI coding agent. Built for the terminal. |
| 12234 | [TheR1D/shell_gpt](https://github.com/TheR1D/shell_gpt) | Python | 2023 | A command-line productivity tool powered by AI large language models like GPT-5, will help… |
| 12021 | [bytedance/trae-agent](https://github.com/bytedance/trae-agent) | Python | 2025 | Trae Agent is an LLM-based agent for general purpose software engineering tasks. |
| 11283 | [humanlayer/humanlayer](https://github.com/humanlayer/humanlayer) | TypeScript | 2024 | The best way to get AI coding agents to solve hard problems in complex codebases. |
| 10556 | [langchain-ai/open-swe](https://github.com/langchain-ai/open-swe) | Python | 2025 | An Open-Source Asynchronous Coding Agent |
| 10349 | [sigoden/aichat](https://github.com/sigoden/aichat) | Rust | 2023 | All-in-one LLM CLI tool featuring Shell Assistant, Chat-REPL, RAG, AI Tools & Agents, with… |
| 10249 | [EKKOLearnAI/hermes-studio](https://github.com/EKKOLearnAI/hermes-studio) | TypeScript | 2026 | Web dashboard for Hermes Agent — multi-platform AI chat, session management, scheduled job… |

### 06-RAG与知识库（17 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 59045 | [pathwaycom/llm-app](https://github.com/pathwaycom/llm-app) | Jupyter Notebook | 2023 | Ready-to-run cloud templates for RAG, AI pipelines, and enterprise search with live data. … |
| 51649 | [run-llama/llama_index](https://github.com/run-llama/llama_index) | Python | 2022 | LlamaIndex is the leading document agent and OCR platform |
| 45643 | [milvus-io/milvus](https://github.com/milvus-io/milvus) | Go | 2019 | Milvus is a high-performance, cloud-native vector database built for scalable vector ANN s… |
| 39398 | [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr) | Python | 2023 | Opiniated RAG for integrating GenAI in your apps  Focus on your product rather than the RA… |
| 38876 | [HKUDS/LightRAG](https://github.com/HKUDS/LightRAG) | Python | 2024 | [EMNLP2025] LightRAG: Simple and Fast Retrieval-Augmented Generation |
| 38546 | [chatchat-space/Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) | Python | 2023 | Langchain-Chatchat（原Langchain-ChatGLM）基于 Langchain 与 ChatGLM, Qwen 与 Llama 等语言模型的 RAG 与 Ag… |
| 35503 | [microsoft/graphrag](https://github.com/microsoft/graphrag) | Python | 2024 | A modular graph-based Retrieval-Augmented Generation (RAG) system |
| 35189 | [VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex) | Python | 2025 | PageIndex: Document Index for Vectorless, Reasoning-based RAG |
| 29359 | [labring/FastGPT](https://github.com/labring/FastGPT) | TypeScript | 2023 | FastGPT is a knowledge-based platform built on the LLMs, offers a comprehensive suite of o… |
| 19895 | [Tencent/WeKnora](https://github.com/Tencent/WeKnora) | Go | 2025 | Open-source LLM knowledge platform: turn raw documents into a queryable RAG, an autonomous… |
| 18217 | [arc53/DocsGPT](https://github.com/arc53/DocsGPT) | Python | 2023 | Private AI platform for agents, assistants and enterprise search. Built-in Agent Builder, … |
| 14851 | [llmware-ai/llmware](https://github.com/llmware-ai/llmware) | Python | 2023 | Unified framework for building enterprise RAG pipelines with small, specialized models |
| 12890 | [neuml/txtai](https://github.com/neuml/txtai) | Python | 2020 | All-in-one AI framework for semantic search, LLM orchestration and language model workflow… |
| 12786 | [StarTrail-org/LEANN](https://github.com/StarTrail-org/LEANN) | Python | 2025 | [MLsys2026]: RAG on Everything with LEANN. Enjoy 97% storage savings while running a fast,… |
| 12051 | [FlagOpen/FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding) | Python | 2023 | Retrieval and Retrieval-augmented LLMs |
| 11974 | [h2oai/h2ogpt](https://github.com/h2oai/h2ogpt) | Python | 2023 | Private chat with local GPT with document, images, video, etc. 100% private, Apache 2.0. S… |
| 10119 | [chaitin/PandaWiki](https://github.com/chaitin/PandaWiki) | TypeScript | 2025 | PandaWiki 是一款 AI 大模型驱动的开源知识库搭建系统，帮助你快速构建智能化的 产品文档、技术文档、FAQ、博客系统，借助大模型的力量为你提供 AI 创作、AI 问答、A… |

### 07-记忆层（8 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 63298 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | Python | 2023 | Universal memory layer for AI Agents |
| 58381 | [MemPalace/mempalace](https://github.com/MemPalace/mempalace) | Python | 2026 | The best-benchmarked open-source AI memory system. And it's free. |
| 24248 | [letta-ai/letta](https://github.com/letta-ai/letta) | Python | 2023 | Platform for stateful agents: AI with advanced memory that can learn and self-improve over… |
| 21794 | [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | TypeScript | 2026 | TencentDB Agent Memory is a team-level memory hub for AI Agents — turning conversations, d… |
| 16217 | [memvid/memvid](https://github.com/memvid/memvid) | Rust | 2025 | Memory layer for AI Agents. Replace complex RAG pipelines with a serverless, single-file m… |
| 16021 | [MemoriLabs/Memori](https://github.com/MemoriLabs/Memori) | Python | 2025 | Memori is agent-native memory infrastructure. A LLM-agnostic layer that turns agent execut… |
| 12034 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | Python | 2025 | One portable memory layer for every AI agent: local-first, Markdown-native, user-owned, an… |
| 10726 | [MemTensor/MemOS](https://github.com/MemTensor/MemOS) | TypeScript | 2025 | Self-evolving memory OS for LLM & AI Agents: ultra-persistent memory, hybrid-retrieval, an… |

### 08-上下文工程与token经济（15 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 167532 | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | TypeScript | 2024 | The context API to search, scrape, and interact with the web at scale. |
| 106451 | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | Python | 2026 | Turn any codebase, with its docs, SQL schemas, configs, and PDFs, into a queryable knowled… |
| 98268 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Go | 2026 | why use many token when few token do trick — Claude Code skill that cuts 65% of tokens by … |
| 76178 | [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | Rust | 2026 | CLI proxy that reduces LLM token consumption by 60-90% on common dev commands. Single Rust… |
| 66396 | [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | Python | 2026 | Compress tool outputs, logs, files, and RAG chunks before they reach the LLM. 20% fewer to… |
| 60774 | [upstash/context7](https://github.com/upstash/context7) | TypeScript | 2025 | Context7 Platform -- Up-to-date code documentation for LLMs and AI code editors |
| 38384 | [google/langextract](https://github.com/google/langextract) | Python | 2025 | A Python library for extracting structured information from unstructured text using LLMs w… |
| 30193 | [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) | Python | 2026 | Local-first code intelligence graph for MCP and CLI. Builds a persistent map of your codeb… |
| 29555 | [ScrapeGraphAI/Scrapegraph-ai](https://github.com/ScrapeGraphAI/Scrapegraph-ai) | Python | 2024 | Python scraper based on AI |
| 27862 | [yamadashy/repomix](https://github.com/yamadashy/repomix) | TypeScript | 2024 | Repomix is a powerful tool that packs your entire repository into a single, AI-friendly fi… |
| 25161 | [toon-format/toon](https://github.com/toon-format/toon) | TypeScript | 2025 | Token-Oriented Object Notation (TOON) – compact, human-readable serialization of JSON data… |
| 19829 | [Alibaba-NLP/DeepResearch](https://github.com/Alibaba-NLP/DeepResearch) | Python | 2025 | Tongyi Deep Research, the Leading Open-source Deep Research Agent |
| 15312 | [Unstructured-IO/unstructured](https://github.com/Unstructured-IO/unstructured) | HTML | 2022 | Convert documents to structured data effortlessly. Unstructured is open-source ETL solutio… |
| 11869 | [jina-ai/reader](https://github.com/jina-ai/reader) | TypeScript | 2024 | Convert any URL to an LLM-friendly input with a simple prefix https://r.jina.ai/ |
| 11320 | [cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex) | Rust | 2025 | Incremental engine for long horizon agents  Star if you like it! |

### 09-网关路由与LLMOps（12 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 56376 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | Python | 2023 | The fastest, litest AI Gateway. Rust core with Python SDK. Call 100+ LLM APIs in OpenAI (o… |
| 33133 | [linshenkx/prompt-optimizer](https://github.com/linshenkx/prompt-optimizer) | TypeScript | 2025 | An AI prompt optimizer for writing better prompts and getting better AI results. |
| 33131 | [langfuse/langfuse](https://github.com/langfuse/langfuse) | TypeScript | 2023 | Open source AI engineering platform: LLM evals, observability, metrics, prompt management,… |
| 25471 | [decolua/9router](https://github.com/decolua/9router) | JavaScript | 2026 | Unlimited FREE AI coding. Connect Claude Code, Codex, Cursor, Cline, Copilot, Antigravity … |
| 24244 | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | TypeScript | 2023 | Test your prompts, agents, and RAGs. Red teaming/pentesting/vulnerability scanning for AI.… |
| 21395 | [comet-ml/opik](https://github.com/comet-ml/opik) | Python | 2023 | Debug, evaluate, and monitor your LLM applications, RAG systems, and agentic workflows wit… |
| 15317 | [vibrantlabsai/ragas](https://github.com/vibrantlabsai/ragas) | Python | 2023 | Supercharge Your LLM Application Evaluations |
| 12725 | [Portkey-AI/gateway](https://github.com/Portkey-AI/gateway) | TypeScript | 2023 | A blazing fast AI Gateway with integrated guardrails. Route to 1,600+ LLMs, 50+ AI Guardra… |
| 11723 | [tensorzero/tensorzero](https://github.com/tensorzero/tensorzero) | Rust | 2024 | TensorZero is an open-source LLMOps platform that unifies an LLM gateway, observability, e… |
| 11218 | [microsoft/promptflow](https://github.com/microsoft/promptflow) | Python | 2023 | Build high-quality LLM apps - from prototyping, testing to production deployment and monit… |
| 11173 | [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master) | — | 2026 | A Claude skill that writes the accurate prompts for any AI tool. Zero tokens or credits wa… |
| 10033 | [lidge-jun/opencodex](https://github.com/lidge-jun/opencodex) | TypeScript | 2026 | Universal provider proxy for OpenAI Codex & Claude Code — use any LLM (Claude, Gemini, Gro… |

### 10-对话前端与平台（16 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 148816 | [open-webui/open-webui](https://github.com/open-webui/open-webui) | Python | 2023 | User-friendly AI Interface (Supports Ollama, OpenAI API, ...) |
| 64722 | [Mintplex-Labs/anything-llm](https://github.com/Mintplex-Labs/anything-llm) | JavaScript | 2023 | Stop renting your intelligence. Own it with AnythingLLM. Everything you need for a powerfu… |
| 46510 | [zhayujie/CowAgent](https://github.com/zhayujie/CowAgent) | Python | 2022 | Open-source super AI assistant & Agent Harness. Plans tasks, runs tools and skills, self-e… |
| 44003 | [janhq/jan](https://github.com/janhq/jan) | TypeScript | 2023 | Jan is an open source alternative to ChatGPT that runs 100% offline on your computer. |
| 39187 | [AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot) | Python | 2022 | AI Agent Assistant & development framework that integrates lots of IM platforms, LLMs, plu… |
| 36499 | [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | Python | 2021 | Your AI second brain. Self-hostable. Get answers from the web or your docs. Build custom a… |
| 32134 | [SillyTavern/SillyTavern](https://github.com/SillyTavern/SillyTavern) | JavaScript | 2023 | LLM Frontend for Power Users. |
| 32002 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | TypeScript | 2025 | Open-source 24/7 Cowork app for OpenClaw, Hermes, Claude Code, Codex, OpenCode and 20+ mor… |
| 31604 | [onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx) | Python | 2023 | Open Source AI Platform - AI Chat with advanced features that works with every LLM |
| 22508 | [1Panel-dev/MaxKB](https://github.com/1Panel-dev/MaxKB) | Python | 2023 | MaxKB is an open-source platform for building enterprise-grade agents. 强大易用的开源企业级智能体平台。 |
| 17416 | [langbot-app/LangBot](https://github.com/langbot-app/LangBot) | Python | 2022 | Production-grade platform for building agentic IM bots - 生产级多平台智能机器人开发平台/ Agent、知识库编排、插件系统… |
| 14868 | [botpress/botpress](https://github.com/botpress/botpress) | TypeScript | 2016 | The open-source hub to build & deploy GPT/LLM Agents |
| 12383 | [Chainlit/chainlit](https://github.com/Chainlit/chainlit) | Python | 2023 | Build Conversational AI in minutes |
| 11860 | [dataelement/bisheng](https://github.com/dataelement/bisheng) | Python | 2023 | BISHENG is an open LLM devops platform for next generation Enterprise AI applications. Pow… |
| 10936 | [getumbrel/llama-gpt](https://github.com/getumbrel/llama-gpt) | TypeScript | 2023 | A self-hosted, offline, ChatGPT-like chatbot. Powered by Llama 2. 100% private, with no da… |
| 10887 | [huggingface/chat-ui](https://github.com/huggingface/chat-ui) | TypeScript | 2023 | The open source codebase powering HuggingChat |

### 11-安全红队与越狱（7 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 62940 | [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) | JavaScript | 2025 | Extracted system prompts from Anthropic - Claude Fable 5, Opus 5, Claude Design, Claude Co… |
| 27794 | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | Python | 2026 | 817 structured cybersecurity skills for AI agents · Mapped to 6 frameworks: MITRE ATT&CK, … |
| 27585 | [p-e-w/heretic](https://github.com/p-e-w/heretic) | Python | 2025 | Fully automatic censorship removal for language models |
| 20959 | [elder-plinius/L1B3RT4S](https://github.com/elder-plinius/L1B3RT4S) | — | 2024 | TOTALLY HARMLESS LIBERATION PROMPTS FOR GOOD LIL AI'S! <NEW_PARADIGM> [DISREGARD PREV. INS… |
| 14901 | [jujumilk3/leaked-system-prompts](https://github.com/jujumilk3/leaked-system-prompts) | — | 2023 | Collection of leaked system prompts |
| 14864 | [GreyDGL/PentestGPT](https://github.com/GreyDGL/PentestGPT) | Python | 2023 | Automated Penetration Testing Agentic Framework Powered by Large Language Models |
| 11011 | [0x4m4/hexstrike-ai](https://github.com/0x4m4/hexstrike-ai) | Python | 2025 | HexStrike AI MCP Agents is an advanced MCP server that lets AI agents (Claude, GPT, Copilo… |

### 12-教育与资源清单（38 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 167142 | [f/prompts.chat](https://github.com/f/prompts.chat) | HTML | 2022 | f.k.a. Awesome ChatGPT Prompts. Share, discover, and collect prompts from the community. F… |
| 102687 | [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | Jupyter Notebook | 2023 | Implement a ChatGPT-like LLM in PyTorch from scratch, step by step |
| 81679 | [mlabonne/llm-course](https://github.com/mlabonne/llm-course) | — | 2023 | Course to get into Large Language Models (LLMs) with roadmaps and Colab notebooks. |
| 74271 | [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | Python | 2025 | Bash is all you need - A nano claude code–like 「agent harness」, built from 0 to 1 |
| 73013 | [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) | Python | 2025 | 《从零开始构建智能体》——从零开始的智能体原理与实践教程 |
| 52325 | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Python | 2025 | A hand-picked collection of the finest of resources for the most awesome of agents, Claude… |
| 46763 | [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | Python | 2026 | Learn it. Build it. Ship it for others. |
| 37436 | [bojieli/ai-agent-book](https://github.com/bojieli/ai-agent-book) | Python | 2025 | 《深入理解 AI Agent：设计原理与工程实践》（李博杰 著）开源主仓库：全书正文、编译版 PDF 与按章配套代码 |
| 32965 | [datawhalechina/happy-llm](https://github.com/datawhalechina/happy-llm) | Jupyter Notebook | 2024 | 从零开始构建大模型 |
| 31717 | [datawhalechina/self-llm](https://github.com/datawhalechina/self-llm) | Jupyter Notebook | 2023 | 《开源大模型食用指南》针对中国宝宝量身打造的基于Linux环境快速微调（全参数/Lora）、部署国内外开源大模型（LLM）/多模态大模型（MLLM）教程 |
| 29601 | [JushBJJ/Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor) | — | 2023 | A GPT-4 AI Tutor Prompt for customizable personalized learning experiences. |
| 29068 | [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | Jupyter Notebook | 2024 | This repository showcases various advanced techniques for Retrieval-Augmented Generation (… |
| 28235 | [HandsOnLLM/Hands-On-Large-Language-Models](https://github.com/HandsOnLLM/Hands-On-Large-Language-Models) | Jupyter Notebook | 2024 | Official code repo for the O'Reilly Book - "Hands-On Large Language Models" |
| 24895 | [liguodongiot/llm-action](https://github.com/liguodongiot/llm-action) | HTML | 2023 | 本项目旨在分享大模型相关技术原理以及实战经验（大模型工程化、大模型应用落地） |
| 24542 | [datawhalechina/llm-cookbook](https://github.com/datawhalechina/llm-cookbook) | Jupyter Notebook | 2023 | 面向开发者的 LLM 入门教程，吴恩达大模型系列课程中文版 |
| 23796 | [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | Jupyter Notebook | 2024 | 50+ tutorials and implementations for Generative AI Agent techniques, from basic conversat… |
| 23298 | [AccumulateMore/CV](https://github.com/AccumulateMore/CV) | Jupyter Notebook | 2022 | （已完结）超级全面的 深度学习 笔记【土堆 Pytorch】【李沐 动手学深度学习】【吴恩达 深度学习】【大飞 大模型Agent】 |
| 22735 | [AiHubCN/Awesome-Chinese-LLM](https://github.com/AiHubCN/Awesome-Chinese-LLM) | — | 2023 | 整理开源的中文大语言模型，以规模较小、可私有化部署、训练成本较低的模型为主，包括底座模型，垂直领域微调及应用，数据集与教程等。 |
| 21285 | [NirDiamant/agents-towards-production](https://github.com/NirDiamant/agents-towards-production) | Jupyter Notebook | 2025 | End-to-end, code-first tutorials for building production-grade GenAI agents. From prototyp… |
| 19690 | [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) | Python | 2026 | 数字生命卡兹克开源的 AI Skills 合集 Agent Skills: leader（帮你定义目标）, neat-freak 洁癖, hv-analysis, khazix-w… |
| 19459 | [jnMetaCode/agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) | Shell | 2026 | 267 个即插即用的 AI 专家角色 — 支持 Hermes Agent/Claude Code/Cursor/Copilot 等 18 种工具，覆盖工程/设计/营销/金融等 20… |
| 18940 | [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe) | JavaScript | 2025 | vibe coding 101｜The first course for AI-native product builders. |
| 18621 | [stas00/ml-engineering](https://github.com/stas00/ml-engineering) | Python | 2020 | Machine Learning Engineering Open Book |
| 18554 | [meta-llama/llama-cookbook](https://github.com/meta-llama/llama-cookbook) | Jupyter Notebook | 2023 | Welcome to the Llama Cookbook! This is your go to guide for Building with Llama: Getting s… |
| 18423 | [liyupi/ai-guide](https://github.com/liyupi/ai-guide) | JavaScript | 2025 | 程序员鱼皮的 AI 资源大全 + Vibe Coding 零基础教程，分享 OpenClaw 保姆级教程、大模型玩法（DeepSeek / GPT / Gemini / Claud… |
| 17587 | [GoogleCloudPlatform/generative-ai](https://github.com/GoogleCloudPlatform/generative-ai) | Jupyter Notebook | 2023 | Sample code and notebooks for Generative AI on Google Cloud, with Gemini Enterprise Agent … |
| 15844 | [composio-community/awesome-codex-skills](https://github.com/composio-community/awesome-codex-skills) | Python | 2026 | A curated list of practical Codex skills for automating workflows across the Codex CLI and… |
| 14906 | [wdndev/llm_interview_note](https://github.com/wdndev/llm_interview_note) | HTML | 2023 | 主要记录大语言大模型（LLMs） 算法（应用）工程师相关的知识及面试题 |
| 14742 | [LlamaChinese/Llama-Chinese](https://github.com/LlamaChinese/Llama-Chinese) | Python | 2023 | Llama中文社区，实时汇总最新Llama学习资料，构建最好的中文Llama大模型开源生态，完全开源可商用 |
| 14710 | [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | Python | 2026 | ARIS  (Auto-Research-In-Sleep) — Lightweight Markdown-only skills for autonomous ML resear… |
| 13375 | [Arindam200/awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps) | Python | 2025 | A collection of projects showcasing RAG, agents, workflows, and other AI use cases |
| 12849 | [eugeneyan/open-llms](https://github.com/eugeneyan/open-llms) | — | 2023 | A list of open LLMs available for commercial use. |
| 12616 | [The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge](https://github.com/The-Pocket/PocketFlow-Tutorial-Codebase-Knowledge) | Python | 2025 | Pocket Flow: Codebase to Tutorial |
| 12498 | [steven2358/awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai) | — | 2022 | A curated list of modern Generative Artificial Intelligence projects and services |
| 12205 | [RUCAIBox/LLMSurvey](https://github.com/RUCAIBox/LLMSurvey) | Python | 2023 | The official GitHub page for the survey paper "A Survey of Large Language Models". |
| 11351 | [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) | TypeScript | 2026 | Harness engineering beginner tutorial, from 0 to 1 |
| 10383 | [cobusgreyling/loop-engineering](https://github.com/cobusgreyling/loop-engineering) | JavaScript | 2026 | Practical patterns, starters & CLI tools for loop engineering with AI coding agents. Desig… |
| 10353 | [datawhalechina/all-in-rag](https://github.com/datawhalechina/all-in-rag) | Python | 2025 | 大模型应用开发实战一：RAG 技术全栈指南，在线阅读地址：https://datawhalechina.github.io/all-in-rag/ |

### 13-垂直应用与工作流（30 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 109272 | [browser-use/browser-use](https://github.com/browser-use/browser-use) | Python | 2024 | Make websites accessible for AI agents. Automate tasks online with ease. |
| 103696 | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | Python | 2024 | 利用 AI 大模型和自动化工作流，根据主题或关键词一键生成高清短视频。Generate HD short videos from a topic or keyword with a… |
| 98221 | [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | Python | 2024 | TradingAgents: Multi-Agents LLM Financial Trading Framework |
| 62913 | [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | Python | 2026 | LLM 驱动的多市场股票智能分析系统：多源行情、实时新闻、决策看板与自动推送，支持零成本定时运行。 LLM-powered multi-market stock analysis … |
| 61474 | [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | Python | 2025 | ⭐AI-driven public opinion & trend monitor with multi-platform aggregation, RSS, and smart … |
| 47397 | [jeecgboot/JeecgBoot](https://github.com/jeecgboot/JeecgBoot) | Java | 2018 | 【低代码迈入v2.0时代，一句话即可生成整个系统】企业级AI低代码平台，一键生成前后端代码甚至整个系统。 AI Skills 一句话画流程、设计表单、生成报表、大屏。内置 AI应用… |
| 36157 | [ItzCrazyKns/Vane](https://github.com/ItzCrazyKns/Vane) | TypeScript | 2024 | Vane is an AI-powered answering engine. |
| 30876 | [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | Python | 2026 | "Vibe-Trading: Your Personal Trading Agent" |
| 29148 | [Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily) | Rust | 2024 | Privacy first, AI meeting assistant with 4x faster Parakeet/Whisper live transcription, sp… |
| 27960 | [OtterMind/Chat2DB](https://github.com/OtterMind/Chat2DB) | Java | 2023 | Chat2DB is a free, cross-platform, local-first database client and SQL workspace for devel… |
| 25859 | [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | Python | 2025 | Community plugin to control Blender 3D with any LLM of your choice |
| 23828 | [vanna-ai/vanna](https://github.com/vanna-ai/vanna) | Python | 2023 | Chat with your SQL database . Accurate Text-to-SQL Generation via LLMs using Agentic Retri… |
| 23743 | [sinaptik-ai/pandas-ai](https://github.com/sinaptik-ai/pandas-ai) | Python | 2023 | Chat with your database or your datalake (SQL, CSV, parquet). PandasAI makes data analysis… |
| 22755 | [Skyvern-AI/skyvern](https://github.com/Skyvern-AI/skyvern) | Python | 2024 | Automate browser based workflows with AI |
| 20962 | [screenpipe/screenpipe](https://github.com/screenpipe/screenpipe) | Rust | 2024 | YC (S26) Record your screen 24/7 and plug into your agents. Local, private, secure. Connec… |
| 20100 | [kortix-ai/suna](https://github.com/kortix-ai/suna) | TypeScript | 2024 | The open-source AI Management System |
| 19729 | [eosphoros-ai/DB-GPT](https://github.com/eosphoros-ai/DB-GPT) | Python | 2023 | open-source agentic AI data assistant for the next generation of AI + Data products. |
| 18137 | [xming521/WeClone](https://github.com/xming521/WeClone) | Python | 2024 | One-stop solution for creating your AI twin from chat history  Fine-tune LLMs with your ch… |
| 17270 | [Canner/WrenAI](https://github.com/Canner/WrenAI) | Python | 2024 | GenBI (Generative BI) for AI agents, an open-source, governed text-to-SQL through an open … |
| 17253 | [rowboatlabs/rowboat](https://github.com/rowboatlabs/rowboat) | TypeScript | 2025 | Open-source AI coworker, with memory |
| 16698 | [browser-use/browser-harness](https://github.com/browser-use/browser-harness) | Python | 2026 | Browser Harness Self-healing harness that enables LLMs to complete any task. |
| 15551 | [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) | Python | 2026 | AI 时代的伯克希尔：基于 Claude Code / Codex 的价值投资研究框架。巴菲特·芒格·段永平·李录四大师方法论 + 多Agent并行研究。 AI-era Berks… |
| 15471 | [Anionex/banana-slides](https://github.com/Anionex/banana-slides) | TypeScript | 2025 | 一个基于nano banana pro的原生AI PPT生成应用，迈向＂Vibe PPT＂; 支持上传任意模板图片，上传任意素材&智能解析，一句话/大纲/页面描述自动生成PPT，口… |
| 13910 | [HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | TypeScript | 2026 | Toonflow 是开源一站式 AI 短剧创作工具，将小说、剧本快速转化为动画短剧。集成 AI 编剧、智能分镜、角色与视频生成，跨平台桌面端轻量部署，助力创作者低成本批量产出视觉内… |
| 13404 | [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | C# | 2025 | Unity MCP acts as a bridge between AI assistants and your Unity Editor. Give your LLM tool… |
| 13250 | [Open-LLM-VTuber/Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber) | Python | 2023 | Talk to any LLM with hands-free voice interaction, voice interruption, and Live2D taking f… |
| 13202 | [browseros-ai/BrowserOS](https://github.com/browseros-ai/BrowserOS) | TypeScript | 2025 | The open-source Agentic browser; alternative to ChatGPT Atlas, Perplexity Comet, Dia. |
| 12628 | [codexu/note-gen](https://github.com/codexu/note-gen) | TypeScript | 2024 | Capture first. Organize later. A local-first Markdown app that turns scattered records int… |
| 11088 | [bytebot-ai/bytebot](https://github.com/bytebot-ai/bytebot) | TypeScript | 2025 | Bytebot is a self-hosted AI desktop agent that automates computer tasks through natural la… |
| 10718 | [linyqh/NarratoAI](https://github.com/linyqh/NarratoAI) | Python | 2024 | 利用 AI 大模型，一键解说并剪辑视频 |

### 14-topic噪声与非LLM原生（9 个）

| Stars | 仓库 | 语言 | 年份 | 一句话定位 |
|---:|---|---|---|---|
| 43516 | [ray-project/ray](https://github.com/ray-project/ray) | Python | 2016 | Ray is an AI compute engine. Ray consists of a core distributed runtime and a set of AI Li… |
| 28726 | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | Go | 2018 | Find secrets with Gitleaks |
| 20786 | [davideuler/architecture.of.internet-product](https://github.com/davideuler/architecture.of.internet-product) | HTML | 2018 | 互联网公司技术架构，微信/淘宝/微博/腾讯/阿里/美团点评/百度/OpenAI/Google/Facebook/Amazon/eBay的架构，欢迎PR补充 |
| 17031 | [kubesphere/kubesphere](https://github.com/kubesphere/kubesphere) | Go | 2018 | The container platform tailored for Kubernetes multi-cloud, datacenter, and edge managemen… |
| 14192 | [casdoor/casdoor](https://github.com/casdoor/casdoor) | Go | 2020 | An open-source Agent-first Identity and Access Management (IAM) /LLM MCP & agent gateway a… |
| 13214 | [halfrost/Halfrost-Field](https://github.com/halfrost/Halfrost-Field) | Go | 2017 | Source Code Deep Dives, System Design & Engineering Blogs Halfrost-Field 冰霜之地：源码解析、系统设计与工程… |
| 13181 | [doocs/md](https://github.com/doocs/md) | TypeScript | 2019 | WeChat Markdown Editor 一款高度简洁的微信 Markdown 编辑器：支持 Markdown 语法、自定义主题样式、内容管理、多图床、AI 助手等特性 |
| 10303 | [astrid-runtime/astrid](https://github.com/astrid-runtime/astrid) | Rust | 2026 | Astrid is a portable, capability-secure operating system for composable software. |
| 10215 | [Netflix/metaflow](https://github.com/Netflix/metaflow) | Python | 2019 | Build, Manage and Deploy AI/ML Systems |

