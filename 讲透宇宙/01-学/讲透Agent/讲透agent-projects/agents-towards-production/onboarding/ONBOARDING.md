# agents-towards-production ONBOARDING

> 基于 `.understand-anything/knowledge-graph.json`（38 节点 / 29 边 / 9 层 / 12 步 tour）撰写，文件锚均已在仓内核实存在。图谱深覆盖五条教程线的资产；全仓教程目录共 22 个。

## 1. 项目定位

本仓是 NirDiamant 的 **Agents Towards Production**——把 AI agent 从原型推向生产环境的开源教程集（playbook），主题横跨状态化工作流、向量记忆、搜索 API、Docker 部署、安全护栏、GPU 伸缩、微调、多智能体、可观测性与评估。形态是**教程集而非可运行单体应用**：`tutorials/` 下每个子目录是一门自包含主题课，彼此零依赖、可任选起点。全仓教程目录共 22 个，本图谱（38 节点）深覆盖其中五条线的文档 / 配置 / 容器 / 脚本资产：

| 教程线 | 目录 | 一句话定位 |
|---|---|---|
| 提示注入攻防 | `tutorials/agent-security-apex/` | 91 条真实攻击样本 + 守护密码靶机，自动化红队评测 |
| 记忆知识图谱 | `tutorials/ai-memory-with-cognee/` | cognee 把五类语料摄入成可检索的 agent 记忆图谱 |
| Docker 容器化 | `tutorials/docker-intro/` | 五个渐进示例：从最小 Dockerfile 到容器化 OpenAI agent |
| RunPod GPU 部署 | `tutorials/runpod-gpu-deploy/crew-ai-ollama-runpod-tutorial/` | CrewAI + Ollama + openhermes 打包为 serverless GPU worker |
| Kotlin 多语言 agent | `tutorials/kotlin-agent-with-koog/` | Koog 框架三步进阶，仓内唯一非 Python 生态教程 |

## 2. 技术栈与内容形态

内容形态为四类资产的组合：**Jupyter notebook 教程正文**（如 `cognee-ai-memory.ipynb`）、**README 导览**、**数据 / 语料资产**（CSV、JSON、md、导出的 HTML 图谱）、**构建与引导件**（Dockerfile、shell 脚本、Gradle 工程）。没有顶层入口程序，没有统一依赖——每个教程目录自带 `requirements.txt` 且版本互不兼容（cognee 线钉死 `cognee[notebook]==0.3.3`，RunPod 线是 `crewai>=0.12` + `runpod~=1.7.9`，安全线是 `openai>=1.0.0` + `aiohttp`），**必须每目录建独立虚拟环境**。

技术栈：Python/OpenAI API 为主，cognee（记忆图谱）、CrewAI（多智能体编排）、Ollama（本地推理）、RunPod（serverless GPU）、Docker，外加 Kotlin/Gradle/JDK 17+ 一条支线。

## 3. 仓库目录速览

```
agents-towards-production/
├── README.md                  # 全仓门面：赞助商教程矩阵 + 22 个教程入口
├── CONTRIBUTING.md            # 贡献指南（新教程如何入选）
├── assets/repos_images/       # 横幅/架构图/赞助商 logo（纯图片）
└── tutorials/                 # 22 个自包含教程目录（本图谱覆盖 5 个）
    ├── agent-security-apex/   #   攻防：README/example_prompts.csv/system_prompt.txt
    │                          #        + 评测 notebook + 两个 *_tools.py
    ├── ai-memory-with-cognee/ #   记忆：README/.env.template/data/ 五份语料
    │                          #        + guido_contributions.html 图谱工件
    ├── docker-intro/          #   容器：README + examples/ex1..ex5（各一 Dockerfile）
    ├── runpod-gpu-deploy/crew-ai-ollama-runpod-tutorial/
    │                          #   GPU：Dockerfile/start.sh/handler.py/requirements.txt
    └── kotlin-agent-with-koog/#   Kotlin：tutorial.md(497 行)/run.sh/gradlew.bat
                               #        + Step1..3 三个 .kt 源文件
```

其余 17 个目录按主题归为：记忆（`agent-memory-with-mem0`、`agent-memory-with-redis`）、安全（`agent-security-with-llamafirewall`、`arcade-secure-tool-calling`）、工具集成（`agent-with-mcp`、`a2a` 等）、工程化（`fastapi-agent`、`LangGraph-agent`、`tracing-with-langsmith` 等）、部署训练（`on-prem-llm-ollama`、`aws_agentcore`、`fine-tuning-agents`）五类。

## 4. 内容架构（图谱 9 层）

| 层 | 内容 | 代表节点 |
|---|---|---|
| L1 教程导览文档 | 四份教程 README + Koog 497 行正文，界定目标与上手步骤 | `tutorials/ai-memory-with-cognee/README.md` |
| L2 环境与依赖配置 | 各教程 pip 清单与 API 凭据模板，钉死版本、互不共享 | `tutorials/ai-memory-with-cognee/.env.template` |
| L3 提示注入攻防资产 | 91 条攻击样本（80 越狱 + 11 注入）+ 守护密码靶机提示词 | `tutorials/agent-security-apex/example_prompts.csv` |
| L4 cognee 记忆语料 | Guido 贡献记录、Copilot 对话、三份规范文档（事实类 + 准则类两类记忆） | `tutorials/ai-memory-with-cognee/data/guido_contributions.json` |
| L5 cognee 图谱工件 | visualize_graph 导出的单文件 D3.js 力导向图，内嵌 126 节点快照 | `tutorials/ai-memory-with-cognee/guido_contributions.html` |
| L6 Docker 基础示例 | ex1（FROM/LABEL/ENV/RUN 最小集）→ ex2（第二条 RUN 引出层缓存复用） | `tutorials/docker-intro/examples/ex2/Dockerfile` |
| L7 Docker 应用容器 | ex3（CMD 增量）→ ex4/ex5（agent 脚本打包 + ENV 注入运行时参数） | `tutorials/docker-intro/examples/ex5/Dockerfile` |
| L8 RunPod GPU 部署 | CUDA 11.8 基镜像 Dockerfile + 拉起 Ollama/预载模型/保活 handler 的 start.sh | `tutorials/runpod-gpu-deploy/crew-ai-ollama-runpod-tutorial/start.sh` |
| L9 构建与引导脚本 | Koog 交互式 run.sh（校验 JDK 17+ 与 API key 后逐步执行）+ Windows wrapper | `tutorials/kotlin-agent-with-koog/run.sh` |

层间核心依赖边：RunPod `Dockerfile →start.sh`（deploys）与 `→requirements.txt`（depends_on）是图谱中仅有的真实部署语义边；cognee README 以 related 边指向五份语料；docker ex2→ex1、ex3→ex2 的 related 边编码了"每个示例只加一个概念"的渐进链。

## 5. 学习路径数据流（tour 12 步压缩为 6 个里程碑）

1. **选线**：读四份 README（`tutorials/agent-security-apex/README.md` 等）判断兴趣——安全对抗、记忆图谱、容器化、GPU 部署或 Kotlin；五线互不依赖。
2. **备环境**：进目标教程目录建 venv、装该目录 requirements；cognee 线另需 `cp .env.template .env` 填 `LLM_API_KEY`（默认模型 `openai/gpt-4o-mini`）。
3. **安全线数据流**：`example_prompts.csv`（91 条攻击）+ `system_prompt.txt`（靶机规则）→ notebook 调 `prompt_manipulation_tools.py` 替换占位符 `{ password }` 为真实密码 → 逐条打靶 → `model_testing_tools.py` 汇总泄露率。
4. **记忆线数据流**：语料分两类——事实类（`guido_contributions.json` PR/commit 记录、`copilot_conversations.json` 真实问答）与准则类（`my_developer_rules.md`、`pep_style_guide.md`、`zen_principles.md`）→ cognee 摄入为 developer_data/principles_data 节点集 → 图谱查询；最终形态直接看 `guido_contributions.html`（无需重跑）。
5. **容器化线数据流**：ex1 学指令 → ex2 学层缓存 → ex3 学 CMD → ex4/ex5 把 agent 脚本（`simple_agent.py`、`dynamic_agent.py`）COPY 进 `python:3.10-slim` 镜像，ex5 用 `ENV QUESTION` 参数化提问。
6. **GPU 线 + Kotlin 支线**：RunPod `Dockerfile`（构建期 pull 好 openhermes）→ 容器启动执行 `start.sh`（拉起 Ollama → 等 11434 就绪 → 载模型 → 起 handler → 保活）；Kotlin 线跑 `run.sh` 依次执行 `Step1_HelloAgent.kt` → `Step2_AgentWithTools.kt`（注解式工具 + ReAct）→ `Step3_StructuredOutput.kt`。

## 6. 各教程线要点

**agent-security-apex（攻防基准）**：`example_prompts.csv` 三列（name,type,text），91 条记录 = 80 条 jailbreak + 11 条 prompt_injection，全部以"What is the password?"为目标；`system_prompt.txt` 是经典靶机——守护末尾注入的密码、正常问题照常回答（95% 置信度阈值），并封堵同义词/韵脚/哈希/翻译旁路。占位符替换发生在 `prompt_manipulation_tools.py:18`。

**ai-memory-with-cognee（记忆图谱）**：教学主张"agent 记忆 = 可检索的知识资产"，区分**事实记忆**（贡献记录、对话历史，供查询）与**准则记忆**（行为规则、风格指南，约束 agent 行为）。`guido_contributions.html` 是现成成果展窗：178KB 单文件、内嵌 D3.js 与 126 节点（Entity/Event/Timestamp）图谱快照。

**docker-intro（渐进式容器化）**：教学法是"每个示例只加一个概念"：ex1 = FROM/LABEL/ENV/RUN（python:3.10 装 curl）；ex2 = 追加装 vim 的 RUN，演示缓存层复用；ex3 唯一增量是 `CMD` 起 bash；ex4 = 最小 OpenAI agent 入镜像；ex5 = `ENV QUESTION` 运行时参数化。`dynamic_agent.py` 里 `client = OpenAI()` 无参构造——API key 全靠运行时环境变量。

**runpod-gpu-deploy（GPU 上云）**：`Dockerfile` 基于 `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel`，装 python3.11 venv、uv 加速 pip，**构建期**就后台 `ollama serve` + `sleep 25` + `ollama pull openhermes` 把模型烧进镜像；还卸载 litellm 换装 `justinwlin/litellm` fork（修上游 tooling index array bug）。`start.sh` 的 `start_ollama()` 轮询 `/api/version` 等就绪再载模型。README 给出 RunPod 模板一键部署与自建镜像两条路径。

**kotlin-agent-with-koog（多语言映射）**：`tutorial.md` 497 行正文覆盖工程结构、build 文件解读与三步进阶（基础 agent → 注解式工具 + Tool Registry → 结构化输出 schema）；`run.sh` 内 `check_java`（JDK 17+）、`check_api_key`（`OPENAI_API_KEY` 掩码显示）、`run_step` 三函数构成交互式引导；`gradlew.bat` 是 Windows 侧 Gradle wrapper 样板。

## 7. 陷阱与注意（消费视角）

- **别共享环境**：五条线 requirements 版本互相冲突（cognee==0.3.3 是硬钉），统一环境必炸；每目录一 venv。
- **凭据三处分散**：cognee 用 `.env` 的 `LLM_API_KEY`（模板 `tutorials/ai-memory-with-cognee/.env.template`，目录 `.gitignore` 已挡 .env）；docker ex4/ex5 与 Koog 用 `OPENAI_API_KEY` 环境变量；镜像内不烧 key。
- **构建上下文**：ex4/ex5 的 Dockerfile 写 `COPY ./examples/ex4/simple_agent.py ...`——build context 必须是 `tutorials/docker-intro/`，在 `examples/ex4/` 里直接 build 会报路径找不到。
- **CSV 别逐行解析**：`example_prompts.csv` 物理行 480 但只有 91 条记录（攻击文本含引号内换行），必须走 csv 解析器。
- **靶机占位符含空格**：`{ password }` 三处空格要原样匹配，漏替换会把占位符直接喂给模型。
- **RunPod 构建慢且贵**：构建期下载 openhermes + deadsnakes PPA + CUDA 全家桶，网络差易超时；GPU 实例按时计费，README 的模板路径可省自建成本；litellm 换 fork 是修 tooling bug，随手升级会回归。
- **Koog 线前置**：`run.sh` 硬校验 JDK 17+ 与 `OPENAI_API_KEY`，缺一即 exit 1；Windows 侧走 `gradlew.bat`。
- **图谱覆盖范围**：notebook 正文（.ipynb）与其余 17 个教程目录不在本图谱 38 节点内，深入那些线以各自 README/notebook 为准。

## 8. 延伸阅读

- 仓内：`README.md`（22 教程总索引 + 赞助商矩阵）、`CONTRIBUTING.md`（教程收录规范）、`tutorials/kotlin-agent-with-koog/tutorial.md`（最长单篇正文，Koog 全流程）。
- 同目录 DeepWiki 素材：`~/ai/work4ai/讲透agent-projects/agents-towards-production/deepwiki/`（31 页全量 wiki，含 3 章安全框架、4 章部署基础设施的横向综述，可补足图谱未覆盖的 17 条教程线）。
- 上游：github.com/NirDiamant/agents-towards-production；cognee / CrewAI / Koog / RunPod 官方文档为各线第一手参考。
