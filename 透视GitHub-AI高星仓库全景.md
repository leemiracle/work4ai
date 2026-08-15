# 透视 GitHub AI 高星仓库全景（topic:ai · stars>11K · 279 仓全量）

> 数据快照：2026-08-15 · 来源：GitHub Search API（`topic:ai stars:>11000`，按 star 降序 100×3 页全量分页）
> 三重校验：API total_count=279 = 解析条数 279 = 附录数据行 279 = 分类头合计 279 ✓ **零遗漏**
> 姊妹篇：本文件是「讲透」系列的生态观测锚点——所有技术单元（Agent/记忆/RAG/代码生成…）在真实开源世界的星力分布。
> 姊妹篇 II：[`透视GitHub-LLM高星仓库全景.md`](./透视GitHub-LLM高星仓库全景.md)（topic:llm · 240 仓 · 14 赛道全显式归类，2026-08-15 同日快照）——ai 镜看 Agent 基建热，llm 镜看全栈分层。
> 姊妹篇 III：[`透视GitHub-Harness高星仓库全景.md`](./透视GitHub-Harness高星仓库全景.md)（topic:harness · 37 仓 ≥1K★ · 2026-08-15 同日快照）——harness 镜看 2026 年爆发的新共识词（Agent=Model+Harness），本篇"harness 成为新共识"判断的专镜验证。
> **落地层**：44 个代表仓的真实代码深读用例卡见 [`用例库/`](./用例库/README.md)（带 文件:行号 证据）。

---

## 0. 一句话总纲

**开源 AI 的重心已经从"造模型"整体迁移到"造 Agent 的基础设施"**：279 个高星仓里，Agent 框架 + 编码 Agent + 研究 Agent + 自动化工作流合计 128 个（46%），而纯粹的训练/微调/推理引擎只有 20 个（7%）。模型层被巨头收敛，开源社区的熵减主战场在编排、执行、记忆与工具层。

---

## 1. 宏观统计（硬数据）

### 1.1 Star 分桶（幂律分布，头部极重）

| 区间 | 仓库数 | 占比 |
|---|---:|---:|
| 100K+ | 19 | 6.8% |
| 50K–100K | 35 | 12.5% |
| 30K–50K | 50 | 17.9% |
| 20K–30K | 62 | 22.2% |
| 11K–20K | 113 | 40.5% |

中位数 ≈ 24.9K；最低 11,007；最高 386,313（openclaw/openclaw）。

**Top 10**：

| # | 仓库 | Stars | 定位 |
|---:|---|---:|---|
| 1 | openclaw/openclaw | 386,313 | 个人 AI 助理（跨平台） |
| 2 | obra/superpowers | 272,197 | Agent 技能框架 + 软件开发方法论 |
| 3 | NousResearch/hermes-agent | 230,675 | 自成长 Agent |
| 4 | n8n-io/n8n | 200,641 | 工作流自动化（原生 AI） |
| 5 | Significant-Gravitas/AutoGPT | 186,604 | 自主 Agent 先驱 |
| 6 | firecrawl/firecrawl | 167,451 | 网页抓取/上下文 API |
| 7 | f/prompts.chat | 167,138 | Prompt 集合 |
| 8 | AUTOMATIC1111/stable-diffusion-webui | 164,501 | SD 图像生成 WebUI |
| 9 | Snailclimb/JavaGuide | 157,761 | Java 面试指南（AI 应用开发章节） |
| 10 | langgenius/dify | 152,446 | Agent 工作流平台 |

### 1.2 语言分布：Python + TypeScript 双寡头（62%）

| 语言 | 数量 | 占比 | 主战场 |
|---|---:|---:|---|
| Python | 104 | 37.3% | Agent 框架、训练微调、研究 |
| TypeScript | 69 | 24.7% | 产品化前端、开发工具、平台 |
| Go | 19 | 6.8% | 基础设施、终端 Agent |
| Rust | 17 | 6.1% | 高性能 runtime/存储（chroma、goose、screenpipe…） |
| JavaScript | 17 | 6.1% | 教育/工具/前端 |
| Jupyter | 12 | 4.3% | 教育课程 |
| Java | 6 | C++ 3 / C# 3 | 企业级、数据库引擎 |
| 其他/未标 | ~29 | 10.4% | 清单、文档、多语言 |

**规律：Python 造智能，TypeScript 造产品**——研究侧和产品侧几乎不重叠。Rust 是 agent runtime 层的崛起势力。

### 1.3 创建年份：三年内重建的版图

| 创建年 | ≤2019 | 2020–22 | 2023 | 2024 | 2025 | 2026(至8月) |
|---|---:|---:|---:|---:|---:|---:|
| 仓库数 | 44 | 29 | 67 | 44 | 63 | 30 |

- **2023 年后创建：204/279（73%）**——ChatGPT 引发的是生态级"相变"，不是增量。
- **2024 年后创建：137/279（49%）**——近一半的高星仓寿命不到三年；openclaw、superpowers 等用 3–12 个月冲上 10 万+ 星，star 通胀显著。
- 存量幸存者（≤2022 的 73 个）集中在：教育经典（JavaGuide）、图像生成（SD-webui）、基础设施（supabase/ClickHouse/kong）。

### 1.4 组织集中度：巨头多而不霸

microsoft 8 仓领跑（generative-ai-for-beginners、autogen、agent-framework…），langchain-ai 3 仓；google、huggingface、github、Lightning-AI、e2b-dev、dair-ai 等各 2 仓。**没有任何一家组织占据 Top 10 的两席以上**——高星榜主体是独立开源者和初创公司（obra、NousResearch、openclaw…）。

---

## 2. 十三条赛道分类图（全量见附录）

| 赛道 | 数量 | 头部代表 | 一句话判断 |
|---|---:|---|---|
| 01 Agent 框架与编排 | 52 | superpowers、autogen、crewAI、agno | 竞争最挤的赛道，harness/技能/sandbox 成为新共识词 |
| 02 编码 Agent 与开发工具 | 56 | hermes-agent、spec-kit、gemini-cli | **第一大赛道**：Claude Code/Codex 生态衍生品爆发 |
| 03 对话前端与个人助理 | 10 | openclaw、ChatGPT、SillyTavern | 前端已收敛，赢家通吃 |
| 04 RAG·记忆·知识库 | 47 | ragflow、mem0、supabase、quivr | 记忆层独立成科（mem0/letta/cognee/EverOS） |
| 05 训练微调与推理 | 20 | LlamaFactory、unsloth、ColossalAI | 模型层开源缩编，工具化生存 |
| 06 图像音视频生成 | 14 | ComfyUI、SD-webui、Deep-Live-Cam | 老牌赛道存量为主，新增向 agentic 视频生产演进 |
| 07 语音 Agent 与实时交互 | 6 | pipecat、livekit/agents、ten-framework | 小而快涨的 2025–26 新赛道 |
| 08 数据获取与研究 Agent | 11 | firecrawl、gpt-researcher、deep-research | "Context 工程"取代"爬虫"成为卖点 |
| 09 自动化与工作流 | 9 | n8n、skyvern、midscene | RPA 的 AI 重写 |
| 10 教育与学习 | 20 | generative-ai-for-beginners、LLMs-from-scratch | 学习资源的 star 效率高于多数工具 |
| 11 Prompt 与资源清单 | 14 | prompts.chat、awesome-mcp-servers | 含"提示词考古学"（泄露系统提示词合集 5 仓入榜） |
| 12 AI 基础设施与工具链 | 1* | dbeaver | *关键词分类局限，大量 infra 仓散落他类（见 §4 误差声明） |
| 13 垂直应用与其他 | 13+6 | OpenBB、frigate、AirSim | 金融/安防/仿真各据一角 |

---

## 3. 七大洞察（已过反虚荣 + 欺骗动力学自检）

**① Agent 是新的"应用服务器"。** 128/279（46%）的仓在直接回答同一个问题："Agent 怎么跑起来？"——框架（autogen/crewAI）、运行时（goose/zeroclaw/elizaOS）、沙箱（daytona/e2b/OpenSandbox）、记忆（mem0/claude-mem）、技能（superpowers/taste-skill）、MCP 工具生态（awesome-mcp-servers 92K）。这对应本项目 [`讲透多Agent协作/`](./讲透多Agent协作/README.md) 与 `透视Agent系统工程/`（待写/未落盘）。

**② 编码是 Agent 第一落地场景，且长出了完整食物链。** 从模型 CLI（gemini-cli、qwen-code、opencode、crush）到 harness（SWE-agent、plandex、deepagents、herdr）到外围经济（caveman 省 token、CodexBar 计量、claude-mem 记忆、cockpit-tools 账号管理）——**"Claude Code 经济圈"本身就是一条 50+ 仓的产业链**。对应 [`讲透代码生成/`](./讲透代码生成/README.md)。

**③ 记忆层独立成科（2025–26 最大的新增品类之一）。** mem0 63K、claude-mem 90K、mempalace 58K、letta、cognee、EverOS、memvid、Memori——"给 Agent 装持久记忆"从 RAG 里分裂出来成为独立基础设施层。对应 [`讲透记忆/`](./讲透记忆/README.md)。

**④ token 经济学成为独立优化维度。** caveman 98K（砍 65% token）、headroom 66K（压缩工具输出省 20%）、repomix（仓库打包喂 LLM）、gitingest——当智能按 token 计价，"上下文压缩"就是新的性能工程。对应 [`讲透上下文缓存/`](./讲透上下文缓存/README.md)。

**⑤ 提示词考古学：灰色基岩。** prompts.chat 167K + 四个系统提示词泄露仓（合计 ~265K stars）——研究别人怎么给产品写 system prompt，已成为一种被 star 承认的"学科"。这既是学习资源也是攻击面。对应 [`欺骗动力学-Prompt篇.md`](./欺骗动力学-检测Prompt库.md)。

**⑥ 中文开源力量约 9%（25+ 仓）。** dify(152K)、ragflow(88K)、LlamaFactory(74K)、deer-flow(80K)、JeecgBoot、WeKnora、bisheng、AstrBot、Chat2DB、Fay、gold-miner、GitHubDaily… 在应用平台与 RAG 层占位明显，在模型/框架底层缺席。

**⑦ 中国互联网大厂 vs 独立开发者的分工。** 榜首军团（openclaw/obra/NousResearch）全是独立或研究组织；大厂仓（microsoft/google/bytedance/tencent/alibaba）提供框架与平台底座但无一进入 Top 5。开源 AI 的明星产出中心在社区，不在公司。

---

## 4. 方法论与误差声明（诚实边界）

1. **数据源**：GitHub Search REST API，`topic:ai stars:>11000`，2026-08-15 快照。star 数实时变动，本文件是时点数据。
2. **topic:ai ≠ AI 仓库全集**：topic 由仓库维护者自打，很多 AI 大仓（如未打此 topic 者）不在结果内；反之 netdata、kong、excelize、kratos、Dokploy 等非 AI 原生项目因自打 `ai` topic 入榜。**本报告结论只在"topic:ai 高星域"内成立。**
3. **分类为启发式关键词规则**（13 类，优先级有序），已知典型错分：ClickHouse/meilisearch/tidb（实为分析/搜索数据库，被归入 05）、supabase（Postgres 平台，被归入 04）、netdata/kong/excelize/kratos/Dokploy（基础设施，被归入 01）、open-webui（对话前端，被归入 04）、langchain/dify（Agent 平台，因描述含 RAG 被归入 04）。**附录保持脚本原样输出，修正以本节为准。**
4. **star 是虚荣指标的风险**（反虚荣视角）：2024+ 新仓的 star 增速含互推/营销通胀；hermes-agent 32,281 个 open issues 提示"高星 ≠ 健康维护"。本报告把 star 用作"注意力流量"代理变量，不作为质量或使用量断言。
5. 语言分布中 17 个"未标注"多为纯清单/文档仓。

---

## 5. 与 work4ai 的映射表

| 本项目单元 | 生态证据（附录编号） |
|---|---|
| 讲透多Agent协作 | 01 类：autogen、crewAI、langgraph、openai-agents-python |
| 讲透代码生成 | 02 类：spec-kit、SWE-agent、gpt-engineer、gpt-pilot |
| 讲透记忆 | 04 类：mem0、claude-mem、letta、cognee、EverOS |
| 讲透上下文缓存 | caveman、headroom、repomix（token 经济学） |
| 讲透RAG | ragflow、quivr、PageIndex、LEANN、WeKnora |
| 透视Agent系统工程 | 12-factor-agents、superpowers、harness 类仓 |
| 欺骗动力学 | 11 类提示词泄露仓 + L1B3RT4S（越狱提示集） |

---

## 附录：全量 279 仓分类清单（按类内 star 降序）



### 01-Agent框架与编排（52 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 272197 | [obra/superpowers](https://github.com/obra/superpowers) | Shell | Agent 技能框架 + 软件开发方法论 |
| 81898 | [koala73/worldmonitor](https://github.com/koala73/worldmonitor) | TypeScript | 实时全球情报仪表盘：AI 驱动的多平台新闻聚合与分析 |
| 80183 | [netdata/netdata](https://github.com/netdata/netdata) | Go | AI 驱动的全栈可观测性平台，轻量团队也能用 |
| 71863 | [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) | Python | 面向分析师、量化交易者与 AI Agent 的开放数据平台 |
| 61467 | [sansan0/TrendRadar](https://github.com/sansan0/TrendRadar) | Python | AI 驱动的多平台舆情与趋势监控雷达 |
| 60426 | [microsoft/autogen](https://github.com/microsoft/autogen) | Python | Agent 化 AI 编程框架（微软） |
| 57083 | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | Python | 编排角色扮演型自主 AI Agent 的框架 |
| 52812 | [aaif-goose/goose](https://github.com/aaif-goose/goose) | Rust | 开源可扩展 AI Agent，超越代码补全的开发者助理 |
| 41714 | [agno-agi/agno](https://github.com/agno-agi/agno) | Python | 构建、运行与管理 Agent 平台的全栈框架 |
| 40988 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | TypeScript | 写 HTML 即可渲染视频，为 Agent 而生 |
| 39171 | [AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot) | Python | 接入多 IM 平台的 AI Agent 助手与开发框架 |
| 36606 | [Dokploy/dokploy](https://github.com/Dokploy/dokploy) | TypeScript | Vercel/Netlify/Heroku 的开源替代部署平台 |
| 36307 | [reworkd/AgentGPT](https://github.com/reworkd/AgentGPT) | TypeScript | 在浏览器中组装、配置与部署自主 AI Agent |
| 34869 | [DayuanJiang/next-ai-draw-io](https://github.com/DayuanJiang/next-ai-draw-io) | TypeScript | 把 AI 能力集成进 draw.io 的 Next.js 应用 |
| 32581 | [zeroclaw-labs/zeroclaw](https://github.com/zeroclaw-labs/zeroclaw) | Rust | 快速、轻量、完全自主的 AI 个人助理基础设施 |
| 29058 | [chroma-core/chroma](https://github.com/chroma-core/chroma) | Rust | 面向 AI 的搜索基础设施（向量数据库） |
| 28646 | [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | Python | 轻量强大的多 Agent 工作流框架（OpenAI 官方） |
| 28629 | [alibaba/page-agent](https://github.com/alibaba/page-agent) | TypeScript | 网页内嵌 GUI Agent：用自然语言操控网页界面 |
| 27779 | [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | Python | 电池全配齐（batteries-included）的 Agent harness |
| 27382 | [charmbracelet/crush](https://github.com/charmbracelet/crush) | Go | 高颜值终端 Agent 编码工具（Charm 出品） |
| 27202 | [mastra-ai/mastra](https://github.com/mastra-ai/mastra) | TypeScript | 现代化 TypeScript AI 应用框架 |
| 26833 | [Fosowl/agenticSeek](https://github.com/Fosowl/agenticSeek) | Python | 完全本地的 Manus 替代：无 API、无月费的自主 Agent |
| 25864 | [go-kratos/kratos](https://github.com/go-kratos/kratos) | Go | 云原生时代 Go 微服务框架（字节出品） |
| 24936 | [flipped-aurora/gin-vue-admin](https://github.com/flipped-aurora/gin-vue-admin) | Go | 🚀Vite+Vue3+Gin拥有AI辅助的基础开发平台，企业级业务AI+开发解决方案，内置mcp辅助服务，内置skills管理，支持TS和… |
| 23941 | [browserbase/stagehand](https://github.com/browserbase/stagehand) | TypeScript | 浏览器 Agent 的 SDK |
| 21116 | [google/adk-python](https://github.com/google/adk-python) | Python | 代码优先的 Python Agent 开发工具包（谷歌官方） |
| 20854 | [qax-os/excelize](https://github.com/qax-os/excelize) | Go | Go 语言的 Excel 读写库 |
| 20098 | [kortix-ai/suna](https://github.com/kortix-ai/suna) | TypeScript | 开源 AI 管理系统（全能自主助理） |
| 20057 | [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | Python | 接收 GitHub issue 并尝试自动修复的编码 Agent |
| 18871 | [agent0ai/agent-zero](https://github.com/agent0ai/agent-zero) | Python | 通用自主 Agent 框架（可自我构建工具） |
| 18598 | [iii-hq/iii](https://github.com/iii-hq/iii) | Rust | 实时组合、扩展与观测每个服务的分布式运行时 |
| 18505 | [danielmiessler/LifeOS](https://github.com/danielmiessler/LifeOS) | TypeScript | 通用爬山式 AI harness：帮你从现状人生爬向理想人生 |
| 18274 | [nukeop/nuclear](https://github.com/nukeop/nuclear) | TypeScript | 自动聚合免费音源的流媒体播放器 |
| 18114 | [transitive-bullshit/agentic](https://github.com/transitive-bullshit/agentic) | TypeScript | 把你的 API 一键变成付费 MCP 服务 |
| 17438 | [leon-ai/leon](https://github.com/leon-ai/leon) | TypeScript | 🧠 开源个人助理 |
| 17031 | [kubesphere/kubesphere](https://github.com/kubesphere/kubesphere) | Go | 面向多云数据中心的 Kubernetes 容器平台 |
| 16492 | [udecode/plate](https://github.com/udecode/plate) | TypeScript | 带 AI 能力的富文本编辑器（shadcn/ui 系） |
| 16175 | [googleapis/mcp-toolbox](https://github.com/googleapis/mcp-toolbox) | Go | 数据库 MCP 服务器（谷歌官方开源） |
| 16029 | [triggerdotdev/trigger.dev](https://github.com/triggerdotdev/trigger.dev) | TypeScript | 构建与部署全托管 AI Agent 与工作流 |
| 14868 | [botpress/botpress](https://github.com/botpress/botpress) | TypeScript | 构建与部署 LLM Agent 的开源枢纽 |
| 14116 | [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat) | Python | 语音 Agent/多模态应用/实时通信开源框架 |
| 13892 | [fathah/hermes-desktop](https://github.com/fathah/hermes-desktop) | TypeScript | Hermes Agent 的桌面伴侣 |
| 13559 | [yc-software/qm](https://github.com/yc-software/qm) | TypeScript | 多人协作的工作 Agent harness |
| 13416 | [xszyou/Fay](https://github.com/xszyou/Fay) | Python | fay是一个帮助数字人（2.5d、3d、移动、pc、网页）或大语言模型（openai兼容、deepseek）连通业务系统的agent框架。 |
| 13005 | [livekit/agents](https://github.com/livekit/agents) | Python | 构建实时语音 AI Agent 的框架 |
| 12805 | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | Python | 构建、编排与部署 AI Agent 与多 Agent 工作流的框架（微软） |
| 12714 | [cloudwego/eino](https://github.com/cloudwego/eino) | Go | Go 语言 LLM/AI 应用开发框架（字节 CloudWeGo） |
| 12520 | [huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech) | Python | 用开源模型构建本地语音 Agent |
| 11352 | [mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) | Python | AI 逆向工程助手：桥接 IDA Pro 与 LLM |
| 11330 | [calesthio/Crucix](https://github.com/calesthio/Crucix) | JavaScript | 个人情报 Agent：从多数据流盯世界 |
| 11164 | [tambo-ai/tambo](https://github.com/tambo-ai/tambo) | TypeScript | React 生成式 UI SDK |
| 11049 | [TEN-framework/ten-framework](https://github.com/TEN-framework/ten-framework) | Python | 对话式语音 AI Agent 开源框架 |

### 02-编码Agent与开发工具（56 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 230675 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | Python | 与你共同成长的自进化 Agent（NousResearch） |
| 186604 | [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | Python | 让所有人都能用、都能构建的 AI 愿景（自主 Agent 先驱） |
| 128544 | [github/spec-kit](https://github.com/github/spec-kit) | Python | 💫 规格驱动开发（SDD）入门工具包（GitHub 官方） |
| 106524 | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) | TypeScript | 把 Gemini 带进终端的开源 AI Agent（谷歌官方） |
| 98234 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Go | 🪨 省 token 的 Claude Code 技能：少量 token 办大事 |
| 76598 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | JavaScript | 给 AI 装上品味：阻止生成烂代码的技能 |
| 72018 | [daytonaio/daytona](https://github.com/daytonaio/daytona) | - | 运行 AI 生成代码的安全弹性沙箱基础设施 |
| 67872 | [code-yeongyu/oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) | TypeScript | 为 token 极客打造的编码 Agent（omo/lazycodex） |
| 64920 | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | TypeScript | 给 AI 编码助手的规格驱动开发（SDD） |
| 64481 | [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | HTML | 从氛围编码到 Agent 工程：Claude Code 最佳实践 |
| 55145 | [AntonOsika/gpt-engineer](https://github.com/AntonOsika/gpt-engineer) | Python | 代码生成 CLI 实验平台（Lovable 前身） |
| 43984 | [Kong/kong](https://github.com/Kong/kong) | Lua | 🦍 API 与 AI 网关 |
| 42044 | [danny-avila/LibreChat](https://github.com/danny-avila/LibreChat) | TypeScript | 增强版 ChatGPT 克隆：支持 Agent/MCP/多模型 |
| 39572 | [mindsdb/mindshub](https://github.com/mindsdb/mindshub) | Makefile | 开源模型替你干活的统一工作区（MindsDB） |
| 36767 | [CopilotKit/CopilotKit](https://github.com/CopilotKit/CopilotKit) | TypeScript | Agent 与生成式 UI 的前端技术栈（React/Angular/移动端） |
| 35482 | [continuedev/continue](https://github.com/continuedev/continue) | TypeScript | 开源编码 Agent（IDE 助手） |
| 33824 | [TabbyML/tabby](https://github.com/TabbyML/tabby) | Rust | 可自托管的 AI 编程助手 |
| 33698 | [Pythagora-io/gpt-pilot](https://github.com/Pythagora-io/gpt-pilot) | Python | 第一个"真正的 AI 开发者"：渐进式写整个应用 |
| 31987 | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | TypeScript | 多 Agent 常驻共事的开源桌面 App（接 OpenClaw/Hermes/Claude Code…） |
| 30652 | [Gitlawb/openclaude](https://github.com/Gitlawb/openclaude) | TypeScript | 随处运行、接任意模型的 Claude 替代 |
| 29691 | [ComposioHQ/composio](https://github.com/ComposioHQ/composio) | TypeScript | 1000+ 工具集成：工具检索/上下文管理/鉴权 |
| 29159 | [herdrdev/herdr](https://github.com/herdrdev/herdr) | Rust | 编码 Agent 生存其上的运行时 |
| 27994 | [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master) | JavaScript | 可嵌入 Cursor 等 IDE/CLI 的 AI 任务管理系统 |
| 27853 | [yamadashy/repomix](https://github.com/yamadashy/repomix) | TypeScript | 📦 把整个仓库打包成单文件喂给 LLM |
| 27009 | [QwenLM/qwen-code](https://github.com/QwenLM/qwen-code) | TypeScript | 住进终端的开源 AI 编码 Agent（Qwen 官方） |
| 26873 | [Kilo-Org/kilocode](https://github.com/Kilo-Org/kilocode) | TypeScript | 一体化 Agent 工程平台（VSCode 生态）：构建、交付… |
| 26488 | [onlook-dev/onlook](https://github.com/onlook-dev/onlook) | TypeScript | 设计师的 Cursor：开源 AI 优先可视化设计工具 |
| 25849 | [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | Python | 用任意 LLM 操控 Blender 3D 的社区插件 |
| 23196 | [coleam00/Archon](https://github.com/coleam00/Archon) | TypeScript | 首个开源 harness 构建器：让 AI 编码可设计 |
| 20108 | [steipete/CodexBar](https://github.com/steipete/CodexBar) | Swift | 菜单栏显示 Codex/Claude Code 用量统计（免登录） |
| 17652 | [TransformerOptimus/SuperAGI](https://github.com/TransformerOptimus/SuperAGI) | Python | <⚡️> 开发者优先的开源自主 Agent 框架 |
| 17565 | [1jehuang/jcode](https://github.com/1jehuang/jcode) | Rust | 内存效率最高的 Agent harness |
| 15889 | [ahmedkhaleel2004/gitdiagram](https://github.com/ahmedkhaleel2004/gitdiagram) | TypeScript | 为任意 GitHub 仓库免费生成交互式架构图 |
| 15764 | [jlcodes99/cockpit-tools](https://github.com/jlcodes99/cockpit-tools) | Rust | 🚀 通用 AI IDE 账号管理工具：支持 Antigravity / Codex / GitHub Copilot / Windsurf… |
| 15659 | [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP) | TypeScript | 把 Figma 布局信息喂给编码 Agent 的 MCP 服务器 |
| 15585 | [plandex-ai/plandex](https://github.com/plandex-ai/plandex) | Go | 为大型真实项目设计的开源编码 Agent |
| 15538 | [xbtlin/ai-berkshire](https://github.com/xbtlin/ai-berkshire) | Python | AI 时代的伯克希尔：基于 Claude Code / Codex 的价值投资研究框架。巴菲特·芒格·段永平·李录四大师方法论 + 多Age… |
| 15305 | [wasp-lang/open-saas](https://github.com/wasp-lang/open-saas) | MDX | 100% 免费的现代 JS SaaS 样板（React/NodeJS/Prisma） |
| 15301 | [coderamp-labs/gitingest](https://github.com/coderamp-labs/gitingest) | Python | GitHub URL 里 hub 改 ingest，一键得到 prompt 友好的仓库文本 |
| 15155 | [theonedev/onedev](https://github.com/theonedev/onedev) | Java | 统一自主开发平台（自托管 DevOps） |
| 14817 | [electerm/electerm](https://github.com/electerm/electerm) | JavaScript | 📻 一体化终端/ssh/sftp/ftp/RDP/VNC 客户端（跨平台） |
| 14801 | [kyegomez/OpenMythos](https://github.com/kyegomez/OpenMythos) | Python | Claude Mythos 架构的理论重构 |
| 14763 | [t8y2/dbx](https://github.com/t8y2/dbx) | Rust | 20MB 轻量跨平台数据库客户端（支持 70+ 数据库） |
| 14227 | [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent) | Python | AI 驱动的研发自动化循环（微软） |
| 14123 | [NanmiCoder/cc-haha](https://github.com/NanmiCoder/cc-haha) | TypeScript | 本地优先的 Claude Code/Agent 跨平台桌面工作区 |
| 13651 | [opencode-ai/opencode](https://github.com/opencode-ai/opencode) | Go | 为终端而生的强力 AI 编码 Agent（已归档，续于 crush） |
| 13406 | [e2b-dev/E2B](https://github.com/e2b-dev/E2B) | Python | 开源安全沙箱：企业级 AI 代码执行环境 |
| 13003 | [opensandbox-group/OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) | Python | AI Agent 的安全快速可扩展沙箱运行时 |
| 12792 | [zoicware/RemoveWindowsAI](https://github.com/zoicware/RemoveWindowsAI) | PowerShell | 强制移除 Win11 的 Copilot/Recall 等 AI 组件 |
| 12743 | [XiaomiMiMo/MiMo-Code](https://github.com/XiaomiMiMo/MiMo-Code) | TypeScript | 模型与 Agent 共进化（小米终端编码 Agent） |
| 12710 | [NoFxAiOS/nofx](https://github.com/NoFxAiOS/nofx) | Go | 美股/商品/外汇 AI 交易终端助理 |
| 11997 | [elie222/inbox-zero](https://github.com/elie222/inbox-zero) | TypeScript | 开源 AI 邮件助理：快速清零收件箱 |
| 11983 | [tadata-org/fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) | Python | 把 FastAPI 接口一键暴露为 MCP 工具 |
| 11705 | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | TeX | AI 研究与工程技能库（开源全科） |
| 11280 | [humanlayer/humanlayer](https://github.com/humanlayer/humanlayer) | TypeScript | 让 AI 编码 Agent 解决复杂工程难题的人机协同层 |
| 11218 | [microsoft/promptflow](https://github.com/microsoft/promptflow) | Python | 构建高质量 LLM 应用：原型→评测→生产（微软） |

### 03-对话前端与个人助理（10 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 386313 | [openclaw/openclaw](https://github.com/openclaw/openclaw) | TypeScript | 个人 AI 助理：任何系统、任何平台（龙虾之道） |
| 54434 | [lencx/ChatGPT](https://github.com/lencx/ChatGPT) | Rust | ❄️ ChatGPT 桌面应用（Win/Mac/Linux） |
| 37406 | [LAION-AI/Open-Assistant](https://github.com/LAION-AI/Open-Assistant) | Python | 开源对话助理：理解任务、可交互、可扩展（LAION） |
| 35101 | [blakeblackshear/frigate](https://github.com/blakeblackshear/frigate) | TypeScript | IP 摄像头本地实时目标检测 NVR |
| 32124 | [SillyTavern/SillyTavern](https://github.com/SillyTavern/SillyTavern) | JavaScript | 给高级玩家的 LLM 前端（角色扮演社区标配） |
| 24635 | [Max-Eee/NeoPass](https://github.com/Max-Eee/NeoPass) | JavaScript | Iamneo/NPTEL 在线考试伴侣（伪装防检测） |
| 20822 | [vercel/chatbot](https://github.com/vercel/chatbot) | TypeScript | Vercel 官方全功能可魔改 Next.js AI 聊天机器人 |
| 17159 | [xx025/carrot](https://github.com/xx025/carrot) | - | AI 工具导航大全，帮你快速筛选免费、实用、高效的网站资源 |
| 14896 | [xcanwin/KeepChatGPT](https://github.com/xcanwin/KeepChatGPT) | JavaScript | 这是一款提高ChatGPT的数据安全能力和效率的插件。并且免费共享大量创新功能，如：自动刷新、保持活跃、数据安全、取消审计、克隆对话、言无不… |
| 14134 | [Usagi-org/ai-goofish-monitor](https://github.com/Usagi-org/ai-goofish-monitor) | Python | 基于 Playwright 和AI实现的闲鱼多任务实时/定时监控与智能分析系统，配备了功能完善的后台管理UI。帮助用户从闲鱼海量商品中，找到… |

### 04-RAG记忆知识库（47 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 152446 | [langgenius/dify](https://github.com/langgenius/dify) | TypeScript | 构建 Agent 工作流与 RAG 管线（多模型多工具支持） |
| 148811 | [open-webui/open-webui](https://github.com/open-webui/open-webui) | Python | 易用的 AI 界面（支持 Ollama/OpenAI API 等） |
| 144237 | [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | Python | Agent 工程平台 |
| 107995 | [supabase/supabase](https://github.com/supabase/supabase) | TypeScript | Postgres 开发平台（开源 Firebase 替代） |
| 90776 | [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem) | JavaScript | 给每个 Agent 的跨会话持久上下文记忆 |
| 88400 | [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | Go | 领先的开源 RAG 引擎（深度文档理解） |
| 81698 | [lobehub/lobehub](https://github.com/lobehub/lobehub) | TypeScript | 🤯 Agent 总运营台：把你的 Agent 组织成生产力矩阵 |
| 66378 | [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | Python | 工具输出/日志/文件/RAG 分块的上下文压缩器 |
| 64775 | [docling-project/docling](https://github.com/docling-project/docling) | Python | 把文档准备好喂给生成式 AI（IBM 解析器） |
| 63277 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | Python | AI Agent 通用记忆层 |
| 58377 | [MemPalace/mempalace](https://github.com/MemPalace/mempalace) | Python | 基准测试最优的开源 AI 记忆系统（免费） |
| 48119 | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Python | 首个开源 Agent 化视频生产系统（12 产品线） |
| 47396 | [jeecgboot/JeecgBoot](https://github.com/jeecgboot/JeecgBoot) | Java | 【低代码迈入v2.0时代，一句话即可生成整个系统】企业级AI低代码平台，一键生成前后端代码甚至整个系统。 AI Skills 一句话画流程、… |
| 46511 | [zhayujie/CowAgent](https://github.com/zhayujie/CowAgent) | Python | 开源超级 AI 助理与 Agent harness：规划任务、跑工具… |
| 39696 | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | Python | 构建有韧性的 Agent（低层编排库） |
| 39397 | [QuivrHQ/quivr](https://github.com/QuivrHQ/quivr) | Python | 主见鲜明的 RAG 框架：把生成式 AI 接进你的应用 🧠 |
| 35185 | [VectifyAI/PageIndex](https://github.com/VectifyAI/PageIndex) | Python | 📑 无向量、推理式 RAG 的文档索引 |
| 31600 | [onyx-dot-app/onyx](https://github.com/onyx-dot-app/onyx) | Python | 开源 AI 平台：企业搜索 + AI 对话 |
| 30028 | [topoteretes/cognee](https://github.com/topoteretes/cognee) | Python | 开源 AI 记忆平台（知识图谱式，给 AI 装认知） |
| 29422 | [simstudioai/sim](https://github.com/simstudioai/sim) | TypeScript | 构建/部署/监控 AI Agent 的协作工作区（Sim Studio） |
| 28408 | [opendataloader-project/opendataloader-pdf](https://github.com/opendataloader-project/opendataloader-pdf) | Java | 面向 AI 就绪数据的开源 PDF 解析器 |
| 28035 | [oraios/serena](https://github.com/oraios/serena) | Python | 编码 MCP 工具包：语义检索 + 编辑 |
| 27958 | [OtterMind/Chat2DB](https://github.com/OtterMind/Chat2DB) | Java | 免费跨平台本地优先的 AI 数据库客户端与 SQL 助手 |
| 27020 | [rohitg00/agentmemory](https://github.com/rohitg00/agentmemory) | TypeScript | 实测基准第一的编码 Agent 持久记忆 |
| 26210 | [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | Python | 开源 AI 编排框架：构建上下文工程化应用（deepset） |
| 25308 | [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents) | TypeScript | 构建可托付 LLM 软件的十二因子原则 |
| 24246 | [letta-ai/letta](https://github.com/letta-ai/letta) | Python | 有状态 Agent 平台：会学习进化的高级记忆（MemGPT 后继） |
| 23827 | [vanna-ai/vanna](https://github.com/vanna-ai/vanna) | Python | 🤖 和 SQL 数据库对话 📊：RAG 训练的精准 Text-to-SQL |
| 23743 | [sinaptik-ai/pandas-ai](https://github.com/sinaptik-ai/pandas-ai) | Python | 和数据库/数据湖对话（SQL/CSV/parquet） |
| 20959 | [screenpipe/screenpipe](https://github.com/screenpipe/screenpipe) | Rust | YC (S26) 7×24 录屏喂给 Agent（本地隐私优先） |
| 20639 | [cube-js/cube](https://github.com/cube-js/cube) | Rust | 📊 面向 AI/BI/嵌入式分析的开源语义层 |
| 19891 | [Tencent/WeKnora](https://github.com/Tencent/WeKnora) | Go | 开源 LLM 知识平台：把原始文档变成可检索知识库（腾讯） |
| 19054 | [elizaOS/eliza](https://github.com/elizaOS/eliza) | TypeScript | 开源 Agent 操作系统（elizaOS） |
| 17647 | [AsyncFuncAI/deepwiki-open](https://github.com/AsyncFuncAI/deepwiki-open) | Python | 开源 DeepWiki：为 GitHub/GitLab/Bitbucket 代码仓生成 AI Wiki |
| 17248 | [rowboatlabs/rowboat](https://github.com/rowboatlabs/rowboat) | TypeScript | 带记忆的开源 AI 同事 |
| 16597 | [mayooear/ai-pdf-chatbot-langchain](https://github.com/mayooear/ai-pdf-chatbot-langchain) | TypeScript | LangChain/LangGraph 构建的 PDF 对话 Agent 样板 |
| 16216 | [memvid/memvid](https://github.com/memvid/memvid) | Rust | 把记忆存进视频文件的轻量方案（替代复杂 RAG 管线） |
| 15956 | [MemoriLabs/Memori](https://github.com/MemoriLabs/Memori) | Python | Agent 原生记忆基础设施（模型无关层） |
| 15769 | [apache/doris](https://github.com/apache/doris) | Java | Apache 实时分析 + 混合检索数据库 |
| 14172 | [T8RIN/ImageToolbox](https://github.com/T8RIN/ImageToolbox) | Kotlin | 🖼️ 安卓高级图像处理工具箱（离线 50+ 模块） |
| 12890 | [neuml/txtai](https://github.com/neuml/txtai) | Python | 💡 一体化 AI 框架：语义搜索 + LLM 编排 + Agent RAG |
| 12786 | [StarTrail-org/LEANN](https://github.com/StarTrail-org/LEANN) | Python | 万物皆可 RAG：省 97% 存储的检索方案（MLsys2026） |
| 12745 | [InsForge/InsForge](https://github.com/InsForge/InsForge) | TypeScript | Agent 编码的一体化开源后端平台 |
| 12049 | [datalab-to/chandra](https://github.com/datalab-to/chandra) | Python | 搞定复杂表格/表单/手写的全语言 OCR 模型 |
| 12025 | [EverMind-AI/EverOS](https://github.com/EverMind-AI/EverOS) | Python | 每个 Agent 一层便携记忆：本地优先、Markdown 原生 |
| 11974 | [h2oai/h2ogpt](https://github.com/h2oai/h2ogpt) | Python | 100% 私有的本地 GPT 对话（文档/图像/视频） |
| 11315 | [cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex) | Rust | 长程 Agent 的增量数据索引引擎 🌟 |

### 05-训练微调与推理（20 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 74104 | [hiyouga/LlamaFactory](https://github.com/hiyouga/LlamaFactory) | Python | 100+ LLM/VLM 统一高效微调（ACL 2024） |
| 71526 | [unslothai/unsloth](https://github.com/unslothai/unsloth) | Python | 本地运行与训练 LLM/扩散模型的 UI（显存省 80%） |
| 58964 | [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch) | Rust | 闪电般快的搜索引擎 API（AI 混合检索） |
| 57442 | [zylon-ai/private-gpt](https://github.com/zylon-ai/private-gpt) | Python | 本地模型私有 AI 应用的完整 API 层（RAG 等） |
| 49255 | [ClickHouse/ClickHouse](https://github.com/ClickHouse/ClickHouse) | C++ | 实时分析型数据库管理系统 |
| 48467 | [mudler/LocalAI](https://github.com/mudler/LocalAI) | Go | 开源 AI 引擎：本地跑任何模型（OpenAI 兼容 API） |
| 41435 | [hpcaitech/ColossalAI](https://github.com/hpcaitech/ColossalAI) | Python | 让大模型训练更便宜、更快、更普及 |
| 40427 | [pingcap/tidb](https://github.com/pingcap/tidb) | Go | 为不可预测增长的 Agent 负载构建的 HTAP 数据库 |
| 31286 | [Lightning-AI/pytorch-lightning](https://github.com/Lightning-AI/pytorch-lightning) | Python | 1 到万卡预训练/微调任意规模的 AI 模型 |
| 28131 | [svc-develop-team/so-vits-svc](https://github.com/svc-develop-team/so-vits-svc) | Python | SoftVC VITS 歌声转换 |
| 27521 | [mlflow/mlflow](https://github.com/mlflow/mlflow) | Python | Agent/LLM/ML 全周期开源工程平台 |
| 23013 | [micro/go-micro](https://github.com/micro/go-micro) | Go | Go 的 Agent harness 与微服务框架 |
| 22505 | [wandb/openui](https://github.com/wandb/openui) | TypeScript | 描述想象即见 UI 渲染（W&B 出品） |
| 18618 | [stas00/ml-engineering](https://github.com/stas00/ml-engineering) | Python | 机器学习工程开源手册 |
| 18454 | [teambit/bit](https://github.com/teambit/bit) | TypeScript | AI 驱动的可复用组件开发工作区 |
| 15818 | [treeverse/dvc](https://github.com/treeverse/dvc) | Python | 🦉 数据版本控制与 ML 实验管理 |
| 13616 | [Lightning-AI/litgpt](https://github.com/Lightning-AI/litgpt) | Python | 20+ 高性能 LLM：预训练/微调/部署配方 |
| 11860 | [dataelement/bisheng](https://github.com/dataelement/bisheng) | Python | 面向下一代企业的开源 LLM DevOps 平台 |
| 11723 | [tensorzero/tensorzero](https://github.com/tensorzero/tensorzero) | Rust | 统一网关 + 可观测 + 实验的开源 LLMOps 平台 |
| 11230 | [wandb/wandb](https://github.com/wandb/wandb) | Python | AI 开发者平台：训练/微调/实验跟踪（W&B） |

### 06-图像音视频生成（14 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 164501 | [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | Python | Stable Diffusion 网页前端（一代目） |
| 127608 | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Python | 最强模块化扩散模型 GUI/API/后端（节点式） |
| 95937 | [hacksider/Deep-Live-Cam](https://github.com/hacksider/Deep-Live-Cam) | Python | 单图实时换脸 + 一键视频 deepfake |
| 48268 | [upscayl/upscayl](https://github.com/upscayl/upscayl) | TypeScript | 🆙 第一免费开源 AI 图像超分工具（Linux/macOS/Win） |
| 43441 | [danielmiessler/Fabric](https://github.com/danielmiessler/Fabric) | Go | 用 AI 增强人类的开源 prompt 框架 |
| 40067 | [photoprism/photoprism](https://github.com/photoprism/photoprism) | Go | AI 驱动的自托管相册应用 🌈💎✨ |
| 33821 | [explosion/spaCy](https://github.com/explosion/spaCy) | Python | 💫 工业级 Python 自然语言处理库 |
| 29591 | [facefusion/facefusion](https://github.com/facefusion/facefusion) | Python | 业界领先的人脸操控平台（换脸/美化） |
| 15916 | [camenduru/stable-diffusion-webui-colab](https://github.com/camenduru/stable-diffusion-webui-colab) | Jupyter Notebook | SD webui 的 Colab 一键脚本集 |
| 15634 | [WEIFENG2333/VideoCaptioner](https://github.com/WEIFENG2333/VideoCaptioner) | Python | 🎬 卡卡字幕助手 / VideoCaptioner - 基于 LLM 的智能字幕助手 - 视频字幕生成、断句、校正、字幕翻译全流程处理！-… |
| 13891 | [HBAI-Ltd/Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | TypeScript | Toonflow 是开源一站式 AI 短剧创作工具，将小说、剧本快速转化为动画短剧。集成 AI 编剧、智能分镜、角色与视频生成，跨平台桌面端… |
| 13578 | [SawyerHood/draw-a-ui](https://github.com/SawyerHood/draw-a-ui) | TypeScript | 画个草图，生成对应 HTML |
| 12340 | [YaoFANGUK/video-subtitle-remover](https://github.com/YaoFANGUK/video-subtitle-remover) | Python | 基于AI的图片/视频硬字幕去除、文本水印去除，无损分辨率生成去字幕、去水印后的图片/视频文件。无需申请第三方API，本地实现。AI-base… |
| 12291 | [willwulfken/MidJourney-Styles-and-Keywords-Reference](https://github.com/willwulfken/MidJourney-Styles-and-Keywords-Reference) | - | MidJourney 风格与关键词查询参考 |

### 07-语音Agent与实时交互（6 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 50430 | [jamiepine/voicebox](https://github.com/jamiepine/voicebox) | TypeScript | 开源 AI 语音工作室：克隆/听写/创作 |
| 36909 | [babysor/MockingBird](https://github.com/babysor/MockingBird) | Python | 🚀 5 秒克隆声音，实时生成任意语音 |
| 29144 | [Zackriya-Solutions/meetily](https://github.com/Zackriya-Solutions/meetily) | Rust | 隐私优先的 AI 会议助理（本地转写 4 倍速） |
| 21837 | [huggingface/datasets](https://github.com/huggingface/datasets) | Python | 🤗 最大的 AI 就绪数据集枢纽（HF 官方） |
| 19365 | [nari-labs/dia](https://github.com/nari-labs/dia) | Python | 一遍前向生成超真实对话的 TTS 模型 |
| 13248 | [Open-LLM-VTuber/Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber) | Python | 免手持语音对话任意 LLM（可打断，VTuber 皮套） |

### 08-数据获取与研究Agent（11 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 167451 | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | TypeScript | 规模化搜索/抓取/交互网页的上下文 API |
| 80017 | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | Python | 开源长程 SuperAgent harness（字节：研究+编码） |
| 73999 | [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | Python | 🕷️ 自适应爬虫框架：从静态页到反反爬全覆盖 |
| 36494 | [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | Python | 可自托管的 AI 第二大脑（联网或查私有文档） |
| 31983 | [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) | JavaScript | 一条命令用 AI 编码 Agent 克隆任意网站（模板） |
| 28979 | [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | Python | 对任意主题做深度研究的自主研究 Agent |
| 22397 | [BuilderIO/gpt-crawler](https://github.com/BuilderIO/gpt-crawler) | TypeScript | 爬取站点生成知识文件，创建自定义 GPT |
| 19552 | [dzhng/deep-research](https://github.com/dzhng/deep-research) | TypeScript | 迭代式深度研究的 AI 研究助理（Gemini 驱动） |
| 18216 | [arc53/DocsGPT](https://github.com/arc53/DocsGPT) | Python | 私有化 AI 平台：Agent + 助理 + 企业搜索 |
| 15916 | [MODSetter/SurfSense](https://github.com/MODSetter/SurfSense) | Python | 开源 NotebookLM 替代：联网研究笔记 |
| 14191 | [AgriciDaniel/claude-seo](https://github.com/AgriciDaniel/claude-seo) | Python | Claude Code 通用 SEO 技能（25 子技能 + 18 子 Agent） |

### 09-自动化与工作流（9 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 200641 | [n8n-io/n8n](https://github.com/n8n-io/n8n) | TypeScript | 原生 AI 能力的公平码（fair-code）工作流自动化平台 |
| 28330 | [iOfficeAI/OfficeCLI](https://github.com/iOfficeAI/OfficeCLI) | C# | 首个专为 AI Agent 打造的 Office 套件 CLI |
| 22755 | [Skyvern-AI/skyvern](https://github.com/Skyvern-AI/skyvern) | Python | 用 AI 自动化浏览器工作流（视觉驱动） |
| 15174 | [n8n-io/self-hosted-ai-starter-kit](https://github.com/n8n-io/self-hosted-ai-starter-kit) | - | 自托管 AI 起步套件（n8n+Ollama+Qdrant 一键栈） |
| 14577 | [web-infra-dev/midscene](https://github.com/web-infra-dev/midscene) | TypeScript | 视觉驱动的全平台 AI UI 自动化（字节） |
| 13559 | [nanobrowser/nanobrowser](https://github.com/nanobrowser/nanobrowser) | TypeScript | Chrome 扩展形态的 AI 网页自动化（多 Agent） |
| 13397 | [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | C# | AI 助手与 Unity 编辑器之间的 MCP 桥 |
| 11089 | [bytebot-ai/bytebot](https://github.com/bytebot-ai/bytebot) | TypeScript | 自托管 AI 桌面 Agent：自动化电脑任务 |
| 11007 | [0x4m4/hexstrike-ai](https://github.com/0x4m4/hexstrike-ai) | Python | 进攻性安全 MCP 服务器：AI Agent 全流程渗透 |

### 10-教育与学习（20 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 157761 | [Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide) | JavaScript | Java 面试 & 后端通用面试指南，覆盖计算机基础、数据库、分布式、高并发、系统设计与 AI 应用开发 |
| 117750 | [microsoft/generative-ai-for-beginners](https://github.com/microsoft/generative-ai-for-beginners) | Jupyter Notebook | 21 课入门生成式 AI（微软官方课程） |
| 102668 | [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | Jupyter Notebook | PyTorch 从零逐步实现 ChatGPT 式 LLM |
| 64920 | [microsoft/AI-For-Beginners](https://github.com/microsoft/AI-For-Beginners) | Jupyter Notebook | 12 周 24 课的全民 AI 课程（微软） |
| 63861 | [santifer/career-ops](https://github.com/santifer/career-ops) | JavaScript | 开源 AI 求职：扫描岗位门户、智能评估列表… |
| 47482 | [GitHubDaily/GitHubDaily](https://github.com/GitHubDaily/GitHubDaily) | - | 坚持分享 GitHub 上高质量、有趣实用的开源技术教程、开发者工具、编程网站、技术资讯。A list cool, interesting … |
| 46746 | [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | Python | 从零学 AI 工程：学会、构建、交付他人 |
| 36997 | [patchy631/ai-engineering-hub](https://github.com/patchy631/ai-engineering-hub) | Jupyter Notebook | LLM/RAG/真实世界 AI Agent 应用深度教程 |
| 34330 | [xitu/gold-miner](https://github.com/xitu/gold-miner) | - | 🥇掘金翻译计划，可能是世界最大最好的英译中技术社区，最懂读者和译者的翻译平台： |
| 31705 | [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | TypeScript | 跑在本机的 AI 求职框架（自动投递） |
| 31207 | [AMAI-GmbH/AI-Expert-Roadmap](https://github.com/AMAI-GmbH/AI-Expert-Roadmap) | JavaScript | AI 专家成长路线图 |
| 29064 | [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | Jupyter Notebook | 检索增强生成（RAG）高级技术大全 |
| 23793 | [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | Jupyter Notebook | 50+ 生成式 AI Agent 技术教程与实现 |
| 23072 | [spmallick/learnopencv](https://github.com/spmallick/learnopencv) | Jupyter Notebook | OpenCV 学习：C++ 与 Python 示例 |
| 21852 | [recommenders-team/recommenders](https://github.com/recommenders-team/recommenders) | Python | 推荐系统最佳实践 |
| 18935 | [datawhalechina/easy-vibe](https://github.com/datawhalechina/easy-vibe) | JavaScript | 💻 氛围编程 101｜AI 原生产品构建者第一课 |
| 18554 | [meta-llama/llama-cookbook](https://github.com/meta-llama/llama-cookbook) | Jupyter Notebook | Llama 官方食谱：构建指南与最佳实践 |
| 18381 | [liyupi/ai-guide](https://github.com/liyupi/ai-guide) | JavaScript | 程序员鱼皮的 AI 资源大全 + Vibe Coding 零基础教程，分享 OpenClaw 保姆级教程、大模型玩法（DeepSeek / … |
| 17358 | [dair-ai/ML-YouTube-Courses](https://github.com/dair-ai/ML-YouTube-Courses) | - | 📺 发现最新的机器学习/AI 视频课程 |
| 11329 | [walkinglabs/learn-harness-engineering](https://github.com/walkinglabs/learn-harness-engineering) | TypeScript | Harness 工程 0 到 1 入门教程 |

### 11-Prompt与资源清单（14 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 167138 | [f/prompts.chat](https://github.com/f/prompts.chat) | HTML | 原名 Awesome ChatGPT Prompts：分享/发现/收藏提示词 |
| 142829 | [x1xhlol/system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools) | - | 主流 AI 工具系统提示词与模型全量收集 |
| 92330 | [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | - | MCP 服务器大全清单 |
| 62926 | [asgeirtj/system_prompts_leaks](https://github.com/asgeirtj/system_prompts_leaks) | JavaScript | Anthropic 等厂商模型系统提示词提取集 |
| 46893 | [elder-plinius/CL4R1T4S](https://github.com/elder-plinius/CL4R1T4S) | - | 各大 AI 产品泄露系统提示词合集 |
| 37850 | [github/awesome-copilot](https://github.com/github/awesome-copilot) | Python | 社区共建的 Copilot 指令/Agent/技能/配置 |
| 29422 | [e2b-dev/awesome-ai-agents](https://github.com/e2b-dev/awesome-ai-agents) | - | AI 自主 Agent 清单（E2B 维护） |
| 28961 | [The-Art-of-Hacking/h4cker](https://github.com/The-Art-of-Hacking/h4cker) | Jupyter Notebook | 网络安全/黑客学习资源全集（Omar Santos 维护） |
| 15779 | [owainlewis/awesome-artificial-intelligence](https://github.com/owainlewis/awesome-artificial-intelligence) | Python | AI 课程/书籍/视频/论文精选清单 |
| 14901 | [jujumilk3/leaked-system-prompts](https://github.com/jujumilk3/leaked-system-prompts) | - | 泄露系统提示词收藏 |
| 14160 | [visenger/awesome-mlops](https://github.com/visenger/awesome-mlops) | - | MLOps 参考资料精选清单 |
| 13373 | [Arindam200/awesome-ai-apps](https://github.com/Arindam200/awesome-ai-apps) | Python | RAG/Agent/工作流实战项目集 |
| 12497 | [steven2358/awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai) | - | 现代生成式 AI 项目与论文精选 |
| 11646 | [EmbraceAGI/awesome-chatgpt-zh](https://github.com/EmbraceAGI/awesome-chatgpt-zh) | Python | ChatGPT 中文指南🔥，ChatGPT 中文调教指南，指令指南，应用开发指南，精选资源清单，更好的使用 chatGPT 让你的生产力 … |

### 12-AI基础设施与工具链（1 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 51434 | [dbeaver/dbeaver](https://github.com/dbeaver/dbeaver) | Java | 免费万能数据库工具与 SQL 客户端 |

### 13-垂直应用与其他（19 个）

| Stars | 仓库 | 语言 | 一句话定位 |
|---:|---|---|---|
| 38806 | [RSSNext/Folo](https://github.com/RSSNext/Folo) | TypeScript | 🧡 AI 驱动的 RSS 阅读器（Follow 后继） |
| 38530 | [google-research/google-research](https://github.com/google-research/google-research) | Jupyter Notebook | 谷歌研究院论文与项目合集 |
| 33352 | [lutzroeder/netron](https://github.com/lutzroeder/netron) | JavaScript | 神经网络/深度学习/机器学习模型可视化器 |
| 29601 | [JushBJJ/Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor) | - | GPT-4 个性化 AI 家教提示词（可定制学习体验） |
| 28449 | [microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel) | C# | 把前沿 LLM 技术快速集成进应用的 SDK（微软） |
| 26807 | [modular/modular](https://github.com/modular/modular) | Mojo | Modular 平台（含 MAX 引擎与 Mojo 语言） |
| 24378 | [plotly/dash](https://github.com/plotly/dash) | Python | 纯 Python 数据应用与仪表盘（无需 JavaScript） |
| 21312 | [onnx/onnx](https://github.com/onnx/onnx) | Python | 机器学习互操作开放标准 |
| 20956 | [elder-plinius/L1B3RT4S](https://github.com/elder-plinius/L1B3RT4S) | - | AI 越狱提示词大全 |
| 20014 | [dailydotdev/daily](https://github.com/dailydotdev/daily) | JavaScript | 个性化开发者资讯流与社区 |
| 18401 | [microsoft/AirSim](https://github.com/microsoft/AirSim) | C++ | 基于虚幻引擎的开源自动驾驶模拟器（微软） |
| 17950 | [google/magika](https://github.com/google/magika) | Python | AI 驱动的文件类型快速精准识别（谷歌） |
| 17584 | [Infrasys-AI/AISystem](https://github.com/Infrasys-AI/AISystem) | Jupyter Notebook | AISystem 主要是指AI系统，包括AI芯片、AI编译器、AI推理和训练框架等AI全栈底层技术 |
| 14296 | [carla-simulator/carla](https://github.com/carla-simulator/carla) | C++ | 开源自动驾驶研究模拟器 |
| 13171 | [BasedHardware/omi](https://github.com/BasedHardware/omi) | Python | 看屏幕听对话、给你建议的可穿戴 AI |
| 13143 | [puckeditor/puck](https://github.com/puckeditor/puck) | TypeScript | React 可视化编辑器 |
| 12975 | [dair-ai/AI-Papers-of-the-Week](https://github.com/dair-ai/AI-Papers-of-the-Week) | - | 🔥 每周热门 ML 论文精选 |
| 12898 | [cocktailpeanut/dalai](https://github.com/cocktailpeanut/dalai) | CSS | 本机运行 LLaMA 的最简方式 |
| 12363 | [simonw/llm](https://github.com/simonw/llm) | Python | 命令行访问大语言模型 |

<!-- APPENDIX_TOTAL=279 -->

