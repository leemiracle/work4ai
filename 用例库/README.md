# 用例库 · GitHub AI 高星仓库真实代码深读

> 来源：topic:ai 且 stars>11K 的 279 个仓库（2026-08-15 快照，姊妹篇：[`../透视GitHub-AI高星仓库全景.md`](../透视GitHub-AI高星仓库全景.md)）
> LLM 域姊妹篇：[`../透视GitHub-LLM高星仓库全景.md`](../透视GitHub-LLM高星仓库全景.md)（topic:llm · 240 仓）——两域 Top10 共享 7 席，重叠仓的用例卡可直接复用。
> 本库回答一个问题：**这些仓库的代码到底怎么写的？** 每张用例卡都落到 `文件:行号` 级证据。
> **2026-08-15 全量审计完成**：279/279 仓全部深读完毕（本页底部 E 系列索引）。

---

## 分档方法（全量三档 + DeepWiki 双源）

| 档 | 覆盖 | 手段 | 产出 |
|---|---|---|---|
| A 档（279/279） | 全部仓库 | GitHub API 元数据 + 278 个 README 画像 | 规模/关键词/文档质量画像 |
| B 档（279/279） | **全部仓库** | `git clone --filter=blob:none` 代码树 + 1135 个关键源文件（manifest/入口/核心模块） | 结构指纹 |
| C 档（279/279） | **全部仓库** | **DeepWiki（deepwiki.com）主文档+核心章节 × 本地 keyfiles 双源**，24 批并行深挖 | 279 张精化用例卡 |

**双源审计法**：DeepWiki 提供 AI 生成的代码级 wiki（带 源文件:行号 引用），本地 keyfiles 提供一手源码验证——两源交叉，防单一来源幻觉。DeepWiki 命中 233/235（2 个 dair-ai 清单仓未收录，用 README+keyfiles 补偿）。

## 用例卡分册

| 分册 | 仓库数 | 覆盖 |
|---|---:|---|
| [`A-框架与编排.md`](./A-框架与编排.md) | 11 | langchain/langgraph/autogen/crewAI/agno/dify/n8n/AutoGPT/deer-flow/skyvern/E2B |
| [`B-助理记忆前端.md`](./B-助理记忆前端.md) | 11 | openclaw/superpowers/hermes-agent/open-webui/LibreChat/SillyTavern/mem0/claude-mem/letta/spec-kit/caveman |
| [`C-编码研究基础设施.md`](./C-编码研究基础设施.md) | 11 | gemini-cli/goose/SWE-agent/continue/tabby/gpt-researcher/firecrawl/ragflow/daytona/LocalAI/ColossalAI |
| [`D-训练多模态语音教育.md`](./D-训练多模态语音教育.md) | 11 | LlamaFactory/unsloth/ComfyUI/SD-webui/Deep-Live-Cam/facefusion/upscayl/pipecat/livekit-agents/generative-ai-for-beginners/LLMs-from-scratch |

## E 系列 · 全量深挖分册（批 01-24，覆盖其余全部 235 仓）

| 分册 | 覆盖要点（10 仓/册，E24 为 5 仓） |
|---|---|
| [`E01-批01深挖.md`](./E01-批01深挖.md) | prompts.chat/JavaGuide/系统提示词泄露库/supabase/awesome-mcp/worldmonitor/lobehub/netdata/taste-skill/Scrapling |
| [`E02-批02深挖.md`](./E02-批02深挖.md) | OpenBB/oh-my-openagent/headroom-CCR/AI-For-Beginners/OpenSpec/docling/claude-code-best-practice/career-ops/泄露prompts/TrendRadar |
| [`E03-批03深挖.md`](./E03-批03深挖.md) | meilisearch/MemPalace/private-gpt/gpt-engineer/lencx-ChatGPT/dbeaver/voicebox/ClickHouse/OpenMontage/GitHubDaily |
| [`E04-批04深挖.md`](./E04-批04深挖.md) | JeecgBoot/CL4R1T4S/ai-engineering-from-scratch/CowAgent/kong/Fabric/hyperframes/tidb/photoprism/mindshub |
| [`E05-批05深挖.md`](./E05-批05深挖.md) | quivr/AstrBot/Folo/google-research/awesome-copilot/Open-Assistant/ai-engineering-hub/MockingBird/CopilotKit-AGUI/dokploy |
| [`E06-批06深挖.md`](./E06-批06深挖.md) | khoj/AgentGPT/PageIndex-vectorless/frigate/next-ai-draw-io/gold-miner/spaCy/gpt-pilot/netron/zeroclaw |
| [`E07-批07深挖.md`](./E07-批07深挖.md) | AionUi/网站克隆worktree/ai-job-search/onyx/pytorch-lightning/AI-Expert-Roadmap/openclaude/cognee/composio/Ranedeer |
| [`E08-批08深挖.md`](./E08-批08深挖.md) | awesome-ai-agents/sim-DAG/herdr屏幕考古/meetily/RAG_Techniques/chroma-WAL3/h4cker/openai-agents/page-agent/semantic-kernel |
| [`E09-批09深挖.md`](./E09-批09深挖.md) | opendataloader-pdf/OfficeCLI/so-vits-svc/serena/claude-task-master/Chat2DB/repomix/deepagents/mlflow/crush |
| [`E10-批10深挖.md`](./E10-批10深挖.md) | mastra/agentmemory/qwen-code/kilocode/agenticSeek/modular/onlook/haystack/kratos/blender-mcp |
| [`E11-批11深挖.md`](./E11-批11深挖.md) | 12-factor-agents/gin-vue-admin/NeoPass/dash/stagehand/vanna/GenAI_Agents/pandas-ai/Archon/learnopencv |
| [`E12-批12深挖.md`](./E12-批12深挖.md) | go-micro/openui/gpt-crawler/recommenders/datasets/onnx/adk-python/screenpipe/L1B3RT4S/excelize |
| [`E13-批13深挖.md`](./E13-批13深挖.md) | vercel-chatbot/cube/CodexBar/suna/daily/WeKnora/deep-research/dia/eliza/easy-vibe |
| [`E14-批14深挖.md`](./E14-批14深挖.md) | agent-zero/ml-engineering/iii/llama-cookbook/LifeOS/bit/AirSim/ai-guide/nuclear/DocsGPT |
| [`E15-批15深挖.md`](./E15-批15深挖.md) | agentic/magika/SuperAGI/deepwiki-open/AISystem/jcode/leon/ML-YouTube-Courses/rowboat/carrot |
| [`E16-批16深挖.md`](./E16-批16深挖.md) | kubesphere/ai-pdf-chatbot/plate/memvid/mcp-toolbox/trigger.dev/Memori/sd-webui-colab/SurfSense/gitdiagram |
| [`E17-批17深挖.md`](./E17-批17深挖.md) | dvc/awesome-ai/doris/cockpit-tools/Figma-Context-MCP/VideoCaptioner/plandex/ai-berkshire/open-saas/gitingest |
| [`E18-批18深挖.md`](./E18-批18深挖.md) | self-hosted-ai-starter-kit/onedev/leaked-system-prompts/KeepChatGPT/botpress/electerm/OpenMythos/dbx/midscene/carla |
| [`E19-批19深挖.md`](./E19-批19深挖.md) | RD-Agent/claude-seo/ImageToolbox/awesome-mlops/ai-goofish-monitor/cc-haha/hermes-desktop/Toonflow/opencode/litgpt |
| [`E20-批20深挖.md`](./E20-批20深挖.md) | draw-a-ui/qm/nanobrowser/Fay/unity-mcp/awesome-ai-apps/Open-LLM-VTuber/omi/puck/OpenSandbox |
| [`E21-批21深挖.md`](./E21-批21深挖.md) | AI-Papers-of-the-Week/dalai/txtai/agent-framework/RemoveWindowsAI/LEANN/InsForge/MiMo-Code/eino/nofx |
| [`E22-批22深挖.md`](./E22-批22深挖.md) | speech-to-speech/awesome-generative-ai/simonw-llm/video-subtitle-remover/MidJourney-Reference/chandra/EverOS/inbox-zero/fastapi_mcp/h2ogpt |
| [`E23-批23深挖.md`](./E23-批23深挖.md) | bisheng/tensorzero/AI-Research-SKILLs/awesome-chatgpt-zh/ida-pro-mcp/Crucix/learn-harness/cocoindex/humanlayer/wandb |
| [`E24-批24深挖.md`](./E24-批24深挖.md) | promptflow/tambo/bytebot/ten-framework/hexstrike-ai |
| [`E25-LLM域独有批01.md`](./E25-LLM域独有批01.md) | **topic:llm 独有 Top10**（A+档）：ECC/ollama/transformers/browser-use/graphify/MoneyPrinterTurbo/ponytail/TradingAgents/vllm/OpenHands |
| [`E26-LLM域独有批02.md`](./E26-LLM域独有批02.md) | llm-course/rtk/learn-claude-code/hello-agents/MetaGPT/anything-llm/daily_stock_analysis/context7/llm-app/litellm |
| [`E27-LLM域独有批03.md`](./E27-LLM域独有批03.md) | awesome-claude-code/llama_index/milvus/jan/ray/CodeWhale/ChatTTS/LightRAG/Langchain-Chatchat/langextract |
| [`E28-LLM域独有批04.md`](./E28-LLM域独有批04.md) | ai-agent-book/Vane/graphrag/DeepSeek-Reasonix/prompt-optimizer/langfuse/happy-llm/sglang/self-llm/llmfit |
| [`E29-LLM域独有批05.md`](./E29-LLM域独有批05.md) | airllm/Vibe-Trading/code-review-graph/Scrapegraph-ai/FastGPT/agentscope/void/gitleaks/Hands-On-LLM/Anthropic-Cybersecurity-Skills |
| [`E30-LLM域独有批06.md`](./E30-LLM域独有批06.md) | heretic/vercel-ai(⚠)/9router/toon(⚠)/llm-action/oh-my-pi/llm-cookbook/promptfoo/CV/mlc-llm |
| [`E31-LLM域独有批07.md`](./E31-LLM域独有批07.md) | Awesome-Chinese-LLM/MaxKB/opcode/unilm/TencentDB-Agent-Memory/Qwen/peft/opik/agents-towards-production/dyad |
| [`E32-LLM域独有批08.md`](./E32-LLM域独有批08.md) | architecture/DeepResearch/DB-GPT/khazix-skills/agency-agents-zh/pydantic-ai/Chinese-LLaMA-Alpaca/omlx/web-llm/parlant |
| [`E33-LLM域独有批09.md`](./E33-LLM域独有批09.md) | WeClone/openfang/Janus/GCP-generative-ai/agent-lightning/LangBot/WrenAI/browser-harness/edict/MNN |
| [`E34-LLM域独有批10.md`](./E34-LLM域独有批10.md) | awesome-codex-skills/ChatGLM2-6B/banana-slides/ragas/unstructured/ms-swift/nano-vllm/llm_interview_note/PentestGPT/llmware |
| [`E35-LLM域独有批11.md`](./E35-LLM域独有批11.md) | easy-dataset/Llama-Chinese/ARIS/casdoor/Halfrost-Field/BrowserOS/doocs-md/gorilla/PaddleNLP/CogVideo |
| [`E36-LLM域独有批12.md`](./E36-LLM域独有批12.md) | langchain4j/open-llms/gateway/note-gen/PocketFlow-Tutorial/OpenLLM/chainlit(⚠)/axolotl/shell_gpt/LLMSurvey |
| [`E37-LLM域独有批13.md`](./E37-LLM域独有批13.md) | FlagEmbedding/trae-agent/jina-reader/ludwig/prompt-master/LMCache/llama-gpt/chat-ui/mistral-inference/MemOS |
| [`E38-LLM域独有批14.md`](./E38-LLM域独有批14.md) | NarratoAI/open-swe/loop-engineering/voltagent/all-in-rag/aichat/astrid/runanywhere-sdks/hermes-studio/metaflow |
| [`E39-LLM域独有批15.md`](./E39-LLM域独有批15.md) | InternVL/PandaWiki/opencodex（收官：**llm 独有 143 仓全覆盖**） |

## A 档全量画像聚合（278 仓 README 统计）

- 平均 README 体积 25.6KB，中位标题数 17——文档即产品是普遍共识
- **221/278（80%）带 shields.io 徽章**，170/278（61%）含 ≥3 个代码块
- **60/278（22%）的 README 显著提及 MCP**——MCP 已成为 AI 工具的事实连接标准
- 双峰分布：20 仓 README >50KB（awesome 类清单 + TrendRadar 等重文档仓），34 仓 <5KB（caveman 等极简主义）

## 十大横断结论（跨 44 仓首轮深读综合，E 系列后有增补）

1. **Agent-as-Tool / 图嵌图是多 Agent 的收敛形态**：AutoGPT 的 `AgentExecutorBlock`、n8n 的 `DelegateSubAgentTool`、ragflow 的 `SubAgentTool`、autogen 的 `AgentTool` 是同一机制的四次独立发明，且都带递归限深（max_sub_agent_depth=8、DEFAULT_SUB_AGENT_MAX_CHILDREN）。
2. **记忆三层分科**：抽取层（mem0 单遍 ADD-only）/ 架构层（letta block 化 OS 式记忆）/ 消费层（claude-mem 三层渐进披露 10 倍省 token）——恰好对应《讲透记忆》的三讲。
3. **中间件栈取代 monolithic agent loop**：deer-flow 用 15+ 中间件（限深/循环检测/压缩/审批）横切 Agent 行为，是 harness 工程化的方向标。
4. **会话即资产**：gemini-cli 的 checkpointing、goose 的 Recipe、SWE-agent 的 trajectory 都把交互历史沉淀为可复现制品。
5. **执行层独立成基础设施**：E2B（微 VM）、daytona（三平面沙箱）、gVisor（ragflow）——"AI 代码在哪跑"已从框架内嵌 subprocess 进化为独立层。
6. **BSP 图执行 + checkpoint = durable execution**：LangGraph（Pregel 式）是"长时会崩溃的 Agent"的标准解，节点级 Retry/Cache/Timeout 三策略内建。
7. **压缩-恢复闭环**：caveman 把每个被压字节存 CCR 库可精确还原——上下文经济学从"省着用"进化到"可逆压缩"。
8. **跨平台 GPU 兼容靠启动期探测硬啃**：unsloth 在 torch import 前抢跑 ROCm DLL 注入、Deep-Live-Cam 的 CDLL 预载——系统层工程是本土训练工具的真正护城河。
9. **节点图范式在多模态生产端胜出**：ComfyUI 的 DAG JSON 使工作流成为可商品化资产，单体 WebUI（SD-webui）定义用户预期但止步于消费者。
10. **规格先行（spec-kit 五段流程）与技能化（superpowers 七步强制流）**：两者都把"工程师纪律"编码为机器可执行的流程资产——这正是《软件即熵治理》的核心论点在Agent时代的回声。

## E 系列增补的八大新发现（跨 235 仓全量综合）

11. **"LLM 提意图，确定性层做决定"是全生态第一公理**：TrendRadar 服务端解析日期、OpenSpec 声明序破拓扑平局、oh-my-openagent realpath 门禁、E21 批"AI 只建议、确定性系统执行风控"——24 批中 15+ 批独立复现此模式。
12. **上下文治理三派：丢/压/避**：Quivr 倒序丢弃 → AstrBot/lobehub/CowAgent 摘要压缩（阈值+保留比+蒸馏）→ Ralph Loop 每轮全新 session 状态落盘。压缩已阶梯化（qwen-code 三级阈值熔断）。
13. **可逆性成为压缩的新标准**：headroom CCR（hash+retrieve 工具）、caveman CCR 库、docling `$ref`+Prov 溯源——"信息不能 silently 丢失"从原则变工程。
14. **文件系统当数据库（Markdown-as-Database）**：career-ops/OpenSpec/Skills 生态（E23 批 4 仓互证）/E14 批"127.0.0.1 回环桥"——平面文件+确定性脚本族替代传统 DB 成 Agent 时代默认。
15. **暂停点=唯一 ID+完整快照**：chroma WAL3 ETag 条件写、sim ExecutionSnapshot、openai RunState、herdr live_handoff、kilo git 回滚——长任务可恢复性被四层独立发明。
16. **反思先于行动成为工业惯例**：page-agent 把 {evaluation/memory/next_goal} 编进工具 schema 强制输出——CoT 从提示技巧升格为接口契约。
17. **MCP 吞噬一切接口层**：从 E18 批桌面/DevOps 工具（onedev/dbx/electerm/midscene）到 E20 批"万能外设总线"（游戏引擎/知识库/沙箱/虚拟形象）——22% README 提及率只是下限。
18. **生态时间箭头可观测**：旧平台包袱（dbx/electerm 双分支）vs AI 工具链激进（botpress TS7 预览）、三种项目"死法"（归档/DW 冻结/CLI 化石）、DeepWiki 快照时滞（gitdiagram 案）——开源生态自身的熵增与治理也是教材。

## 与讲透单元的映射索引

| work4ai 单元 | 用例卡锚点 |
|---|---|
| 讲透记忆 | mem0/letta/claude-mem（B册）、mempalace/zeroclaw/cognee/openclaude（E03/E06/E07）、CowAgent dream diary（E04）、记忆三层化（E21） |
| 讲透多Agent协作 | langgraph/autogen/crewAI（A册）、openai handoff 公理系/page-agent（E08）、worktree 空间并行 vs Drafter-Reviewer 时间迭代（E07） |
| 讲透代码生成 | spec-kit/superpowers/SWE-agent（B册）、gpt-pilot LLM-as-file-filter（E06）、13 步 XML 修复管线（E06）、plandex 自纠环（E17） |
| 讲透RAG | ragflow/gpt-researcher/firecrawl 取-炼-用三层（C册）、PageIndex vectorless 树检索（E06）、onyx ACL 过滤器（E07）、Corrective/Graph RAG 配方（E05）、chroma WAL3 物理层（E08）、LEANN 存算两极（E21） |
| 讲透上下文缓存 | caveman/claude-mem（B册）、headroom CCR 可逆压缩（E02）、Folo 上下文块化 UI（E05）、压缩阶梯（E10） |
| 讲透Prompt | prompt-optimizer/promptfoo/ragas/opik/promptflow（LLM 镜 09 类，E28/E30/E31/E34）、system_prompts_leaks 提示词考古（11 类）；六仓已集成 opencode 工具链（[`Agent框架案例/prompt工程工具链`](../Agent框架案例/prompt工程工具链/README.md)） |
| 讲透CV/多模态 | ComfyUI/SD-webui/facefusion（D册）、frigate 边缘检测（E06）、meetily TDT 流式转写（E08）、hyperframes 确定性渲染（E04） |
| 讲透PyTorch/Transformer | LLMs-from-scratch/LlamaFactory（D册）、pytorch-lightning hook 契约（E07）、Value autograd 微缩原型（E02）、netron 模型考古（E06） |
| 讲透世界模型 | skyvern 视觉-行动（A册）、page-agent 网页坍缩为文本世界（E08）、worldmonitor 国家压力指数（E01） |
| 讲透学习型Agent | hermes 自提升（B册）、netdata 18 模型全票共识（E01）、CowAgent 保守自进化（E04）、7 文件画像（E07） |
| 透视Agent系统工程 | openclaw Gateway（B册）、deer-flow 中间件（A册）、herdr 屏幕考古（E08）、AG-UI 协议（E05）、全生态 MCP 化（E18/E20）、DeepSeek Harness 官方旗舰特写（[`Agent框架案例/deepseek-harness插件化框架`](../Agent框架案例/deepseek-harness插件化框架/README.md)，发布晚于 279 快照故未入册） |

### 姊妹索引：本地仓库全景

C:\workspace 本地 21 仓（自有项目/知识库/外部参考库）已全量深读，卡片与合并清单见 [`../本地仓库全景-Cworkspace迭代索引.md`](../本地仓库全景-Cworkspace迭代索引.md)（2026-08-15，含 neo-os/world-ai4sci-math/ai-os-dd/mips-sim 等高价值姊妹库的桥接方案）。
| 软件即熵治理 | superpowers/spec-kit 流程资产（B册）、tidb Raft 三元组恢复（E04）、SK ADR 双语言治理（E08）、规则外置为数据（E08/E17） |

## 误差与边界声明

1. C 档深读基于每仓 DeepWiki 主文档+1-2 核心章节 + 1-7 个关键源文件（≤400 行）+ 树指标交叉，非逐行全审计；行号证据限于已读片段（DeepWiki 引用可回溯到具体文件）。
2. **DeepWiki 是 AI 生成 wiki，存在快照时滞**（gitdiagram 案例实锤：DW 仍描述已删除架构）——所有关键论断已尽量用本地 keyfiles 一手源码交叉验证，单源论断标注 DW 引用。
3. daytona 2026-06 起核心转闭源，用例卡基于 README 证据（卡内标注）。
4. 2 个 dair-ai 清单仓 DeepWiki 未收录（DW:FAIL），用 README+keyfiles 补偿。
5. dalai（279 之一）README 抓取失败；continue/autogen 处于归档/维护模式——作为"框架生命周期"教材保留。
6. star 数为 2026-08-15 快照；分类沿用全景报告 13 赛道（见姊妹篇误差声明）。
