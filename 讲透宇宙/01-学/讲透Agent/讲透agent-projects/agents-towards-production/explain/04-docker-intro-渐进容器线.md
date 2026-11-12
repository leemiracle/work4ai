# 04 | docker-intro——五个示例只加一个概念的渐进容器线

## ① 角色定位

`tutorials/docker-intro/` 占图谱 L6"基础示例"（ex1/ex2）与 L7"应用容器"（ex3/ex4/ex5）两层共 10 节点（5 个 Dockerfile + 5 个 `:python` 基镜像阶段节点）。教学法钉在 tour step-08：**每个示例只加一个概念**。ex2→ex1、ex3→ex2 的 related 边在图谱里显式编码了这条渐进链。它回答的问题是：agent 代码如何从"我机器上能跑"变成"任何地方可复现"。

## ② 内部结构

**README.md（685 行，Rami Krispin 执笔 README.md:684）**是教程正文，六个大节：Why Docker for Agents（README.md:9-11）→ 可复现性五因素（版本/随机种子/软件版本/OS/硬件，README.md:101-115）→ Docker 工作流与 image vs container 之辨（README.md:151-158）→ Dockerfile 指令表（README.md:205-215）→ build 与层缓存（README.md:219-452）→ run/卷挂载（README.md:454-564）→ Dockerize AI Agent（README.md:566-675）。

**五个 Dockerfile 逐个看**：
- `examples/ex1/Dockerfile`（6 行）：`FROM python:3.10`（ex1/Dockerfile:1）+ `LABEL example=1`（ex1/Dockerfile:3）+ `ENV PYTHON_VER=3.10`（ex1/Dockerfile:5）+ `RUN apt-get ... curl`（ex1/Dockerfile:6）——最小四指令集。
- `examples/ex2/Dockerfile`：唯一增量是第二条 `RUN ... vim`（ex2/Dockerfile:9），LABEL 升为 example=2（ex2/Dockerfile:3）；演示层缓存复用——README.md:385 构建输出里 curl 层显示 CACHED。
- `examples/ex3/Dockerfile`：唯一增量 `CMD ["/bin/sh","-c","bash"]`（ex3/Dockerfile:11），配 hello-world.py:1 一行脚本演示卷挂载执行。
- `examples/ex4/Dockerfile`：换基镜像 `python:3.10-slim`（ex4/Dockerfile:1）+ `RUN pip install --no-cache-dir openai`（ex4/Dockerfile:3）+ `COPY ./examples/ex4/simple_agent.py /app/`（ex4/Dockerfile:5）+ CMD 起脚本（ex4/Dockerfile:6）。simple_agent.py 共 10 行：`client = OpenAI()` 无参构造（simple_agent.py:3），问题硬编码（simple_agent.py:7）。
- `examples/ex5/Dockerfile`：唯一增量 `ENV QUESTION="What is the capital of France?"`（ex5/Dockerfile:7）；dynamic_agent.py:6 `os.getenv("QUESTION", 默认值)` 把问题参数化，dynamic_agent.py:13-14 打印问与答。

## ③ 外部连接

每个 Dockerfile 节点 contains 一条 `:python` 边指向其 FROM 的基镜像阶段（ex1-ex3 是 python:3.10 全量镜像，ex4/ex5 是 slim 变体——同层内的分野就是"学指令"与"打包应用"的分野）。ex4/ex5 的 COPY 依赖仓内 simple_agent.py/dynamic_agent.py（构建上下文=教程根目录，README.md:229 解释 context 语义）。agent 脚本 import openai（simple_agent.py:1），运行期依赖环境变量 OPENAI_API_KEY（README.md:609 的 -e 注入）。与 runpod 线的关系：本线是地基，runpod-gpu-deploy 的 Dockerfile 是同一语法在 GPU 场景的全量展开。

## ④ 数据流

构建期：Dockerfile + build context → `docker build . -f ./examples/exN/Dockerfile -t rkrispin/...:exN`（README.md:223-224 格式）→ 分层镜像；FROM/RUN 成层、LABEL/ENV/CMD 成元数据（README.md:287），ex1 的 python:3.10 自带 8 层所以成品 9 层（README.md:320 实证）。运行期：ex1-ex3 交互式容器（`docker run --interactive --tty`，README.md:490）；ex3 加 `-v ./examples/ex3:/ex3` 挂载本地脚本（README.md:549）；ex4/ex5 是一次性任务容器——CMD 起 python 脚本→脚本调 OpenAI→打印答案→容器退出，输入=环境变量（OPENAI_API_KEY 必给，ex5 另有 QUESTION），输出=stdout 一行答案（README.md:616）。

## ⑤ 设计决策与陷阱

- **决策：渐进链 + 层缓存作为第一课**。把 vim 安装故意拆成第二条 RUN（README.md:355 自述"should add it to the same apt-get... for the purpose of showing caching"）——反工程直觉但教学最优。
- **决策：密钥永不入镜像**。README.md:606 明文 best practice：构建期不烧 key，运行期 `-e OPENAI_API_KEY` 注入；脚本侧 `OpenAI()` 无参构造（simple_agent.py:3）正是为此。
- **陷阱 1：README 目录名笔误**。README.md:224 `./examples/ex-1/Dockerfile`、README.md:374 `./examples/ex-2/Dockerfile`——实际目录是 `ex1`/`ex2` 无连字符，照抄命令报 path not found。
- **陷阱 2：指令表 ENDPOINT 拼错**。README.md:215 写 `ENDPOINT`，Docker 真实指令是 `ENTRYPOINT`。
- **陷阱 3：README 代码片段与文件漂移**。README.md:362 引 ex2 片段写 `LABEL example=1`，实文件已是 example=2（ex2/Dockerfile:3）——片段是 ex1 复制后未同步。
- **陷阱 4：build context 必须是 docker-intro/**。COPY 路径 `./examples/ex4/...`（ex4/Dockerfile:5）以教程根为基准；在 examples/ex4/ 目录里直接 build 会找不到文件。
- **陷阱 5：卷挂载叙述自相矛盾**。README.md:541 命令挂到 `/ex3`、README.md:549 挂到 python:3.10 而非 ex3 镜像、README.md:551-556 文字却说映射到 my_python_scripts（拼写还是 scipts）——此节命令以实际可运行为准需自行修正。
- **决策：ex4 起换 slim 基镜像**——打包应用时镜像体积开始重要，这是从学习环境到交付物的第一次取舍示范。

## ⑥ 新人提示

按 ex1→ex5 顺序跑，每步先 diff 上一个 Dockerfile（ex2/Dockerfile:9、ex3/Dockerfile:11、ex5/Dockerfile:7 就是三处唯一增量），把"一行一个概念"内化为写 Dockerfile 的肌肉记忆。缓存实验必做：改 ex2 的 vim 行位置观察缓存失效边界（README.md:429-450 讲透"稳定层放前面"原则）。跑 ex4/ex5 记住两条命令三件套：`docker build -f ./examples/ex4/Dockerfile -t agent:ex4 .`（在 docker-intro/ 下）→ `docker run -e OPENAI_API_KEY=$OPENAI_API_KEY agent:ex4`；ex5 再加 `-e QUESTION="..."` 体会 ENV 参数化。学完直接进 runpod 线，那里是同一语法+CUDA+Ollama 的生产级全量版。
