# 05 | runpod-gpu-deploy——CrewAI+Ollama 烧进镜像的 serverless GPU worker

## ① 角色定位

`tutorials/runpod-gpu-deploy/crew-ai-ollama-runpod-tutorial/` 对应图谱 L8"RunPod GPU 部署"层（Dockerfile、:pytorch 基镜像、start.sh、requirements.txt、README 五节点），持有全图谱仅有的两条真实部署语义边：Dockerfile→start.sh（deploys）与 Dockerfile→requirements.txt（depends_on）。它是五条线里唯一"交付生产工件"的教程：产物是一个可推到 registry、被 RunPod serverless 拉起的 GPU 容器镜像。tour step-10 的定位——把 agent 负载从本地推到按需计费的云端 GPU。

## ② 内部结构

五文件各司一职：
- **Dockerfile（67 行，最重文件）**：六段式。基镜像 `runpod/pytorch:2.0.1-py3.10-cuda11.8.0-devel-ubuntu22.04`（Dockerfile:1，CUDA 11.8 devel 全量）；deadsnakes PPA 装 python3.11+venv（Dockerfile:7-18）并建 `/app/venv`、PATH 前置（Dockerfile:21-22）、软链 python/python3（Dockerfile:25-26）；装 cudnn/wget/git（Dockerfile:29-33）；uv 加速装 requirements + langchain-community，并 `python -c "import crewai"` 做装后自检（Dockerfile:37-42）；**卸 litellm 换 justinwlin fork 修 tooling index array bug**（Dockerfile:44-46，注释原文）；curl 装 Ollama（Dockerfile:49）；**构建期后台 `ollama serve`+`sleep 25`+`ollama pull openhermes` 把模型烧进镜像**（Dockerfile:55-59）；ADD handler.py/start.sh（Dockerfile:62-64）；`CMD ["/start.sh"]`（Dockerfile:67）。
- **start.sh（40 行）**：单函数 `start_ollama`（start.sh:8-26）——nohup 起 ollama serve（start.sh:10）→ `until curl /api/version` 轮询就绪（start.sh:14-16）→ `ollama run openhermes` 载入（start.sh:20）→ `ollama list` 验证（start.sh:25）；主流程 start_ollama→`python handler.py`（start.sh:37）→`sleep infinity` 保活（start.sh:40）。
- **handler.py（136 行）**：RunPod worker 入口。模块级全局初始化——LLM 指 Ollama 端点 `ollama/openhermes`+`http://localhost:11434`（handler.py:10）；`@tool("Research Tool")` 伪研究工具返回预置假数据（handler.py:13-63，四主题词典 handler.py:22-47 + 默认回答 handler.py:50-55）；blog_writer Agent 一次构建复用（handler.py:66-78）；`create_blog_post` 组装 Task（handler.py:83-97，expected_output 500 词）与 Crew（handler.py:100-105）后 `crew.kickoff()` 取 `result.raw`（handler.py:109-110）；`handler(job)` 取 `topic` 默认 "technology"（handler.py:117），异常转 JSON error（handler.py:128-133）；末行 `runpod.serverless.start({"handler": handler})`（handler.py:136）挂上 serverless 循环。
- **requirements.txt**：仅三项 `crewai>=0.12`/`crewai-tools>=0.1`/`runpod~=1.7.9`（requirements.txt:2-4），与 handler.py:3-5 的三个 import 一一对应。
- **README.md**：两条部署路径——RunPod 模板一键部署（README.md:43-47，badge README.md:20）与自建镜像 push（README.md:49-62，build 命令带 `--platform linux/amd64` README.md:53，建议 24GB+ VRAM README.md:60）；API 用法（端点格式 README.md:69-71、curl 例 README.md:75-88、真实响应样例 README.md:92-104，delayTime 14836ms 冷启动实证）；handler/Dockerfile 代码讲解（README.md:108-187）；性能与扩展建议（README.md:189-201）。

## ③ 外部连接

依赖链全在 Dockerfile 内声明：COPY requirements.txt（Dockerfile:36）→uv 安装→crewai 自检（Dockerfile:41）；ADD start.sh/handler.py（Dockerfile:62-63）→CMD 触发 start.sh（Dockerfile:67）→start.sh 起 handler.py（start.sh:37）→handler 连 localhost:11434 的 Ollama（handler.py:10，由 start.sh:10 拉起）。运行时外部依赖仅 RunPod 平台（job 分发/计费）与 Docker Hub（push 镜像）。图谱外还有一个上层 `tutorials/runpod-gpu-deploy/README.md`（306 行总览，非图谱节点）链接本目录。与 docker-intro 线是同语法递进：EXPOSE/ENTRYPOINT 没用到，但 FROM/ENV/RUN/COPY/CMD 五件套全部在场。

## ④ 数据流

构建期（一次性、分钟级昂贵）：Dockerfile + requirements + handler/start.sh → 镜像（内含 CUDA 运行时、venv、CrewAI 栈、Ollama 二进制、openhermes 权重）。运行期每次请求：RunPod 投递 job → 容器冷启动跑 /start.sh → Ollama 就绪+模型载入 → handler 收 `{"input":{"topic":...}}` → CrewAI 单 agent 单 task 流程（LLM 多轮调 fake_research 工具）→ `{"status":"success","blog_post":...}` JSON 返回（handler.py:124-127）。输入输出都是 RunPod 约定的 job schema；worker count min:0（README.md:61）意味着闲时零成本、请求触发冷启动。

## ⑤ 设计决策与陷阱

- **决策：模型烧进镜像**。Dockerfile:55-59 构建期 pull openhermes——牺牲镜像体积换冷启动免下载（README.md:192 明说 pre-loading 提升响应时间）；sleep 25/10 是经验等待值，网络慢时构建即失败。
- **决策：litellm 换 fork**。Dockerfile:44-46 注释直说上游有 tooling index array bug——生产镜像钉死修复源的示范，也意味着**随手升级 crewai/litellm 会回归该 bug**。
- **决策：伪研究工具**。handler.py:14 起全是假数据——教程把变量收敛到"部署链路正确性"，排除外部搜索 API 的不确定性；接真搜索是 README.md:198 留的扩展作业。
- **陷阱 1：README 的 Dockerfile 片段是删节版**。README.md:168-187 略去 deadsnakes/venv/litellm fork/ollama 安装等关键段——以仓库 Dockerfile 原文为准，别照 README 片段自建镜像。
- **陷阱 2：成本敏感**。基镜像是 cuda devel 全量 + 构建期拉模型，构建慢且推 registry 体积大；GPU 实例按秒计费，第一次跑优先走模板路径（README.md:43）。
- **陷阱 3：单 agent "Crew"**。名为 CrewAI 教程，实为 agents=[blog_writer] 单成员（handler.py:100-101）——多智能体编排不是本线主题，别在此找 Crew 深度用法。
- **陷阱 4：端口耦合**。handler.py:10 硬编码 localhost:11434 与 start.sh:14 的探活端口必须一致，改动任一侧要同步。

## ⑥ 新人提示

阅读顺序建议：crew README 的 How It Works（README.md:22-37）→ Dockerfile 逐行（重点 Dockerfile:44-46/Dockerfile:55-59 两段"生产味"最浓的 RUN）→ start.sh 40 行全读（体会"容器内自编排"模式：serve/wait/load/verify 四拍）→ handler.py 的模块级初始化（handler.py:8-78，为什么放全局：worker 常驻、模型只载一次）。上手路径：先用 RunPod 模板发一个 topic 请求看 README.md:92-104 的响应长啥样，再走自建镜像路径并故意改 handler 的 system prompt 验证镜像替换生效。迁移练习：把 Ollama 模型换成 qwen 系或把 fake_research 接上真搜索 API——改 Dockerfile:57 的模型名与 handler.py:22-47 的工具实现各一处即可，其余链路不动，这正是这套镜像模板的生产价值。
