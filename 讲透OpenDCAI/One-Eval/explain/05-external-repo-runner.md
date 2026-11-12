# 05 · ExternalRepoRunner：外评挂载与 Docker 评测桥

## 角色定位

`one_eval/toolkits/external_repo_runner.py`（1059 行）跑「不归确定性内核管」的 10 个 external_repo 基准（mathvista/mmmu/mmmu_pro/livecodebench/humanevalplus/mbppplus/bfcl/tau2_bench/gaia/omniabench）：clone 上游评测仓 → 独立 venv → 打补丁 → 宿主机或 Docker 沙箱执行上游脚本 → 从结果文件抠分数。docstring 自述修了三个阻塞级问题：URL/ref 隔离+`.setup_complete` 标记、argv+shell=False 防注入与密钥泄露、每仓独立 venv（5-8 行）。

## 内部结构

**安装链 `setup_repo`**（175 起）：目录 `cache/external_repos/{repo_name}/{ref}/`（63-83），下分 repo/+.venv+.setup_complete。已装则 `_verify_repo` 用 `git remote get-url origin`+`rev-parse` 双校验（100-173），并按 mtime 热更新 patch（222-232）。全新安装：clone（254）→checkout（273），失败即 rmtree 清场；`uv venv --python X.Y` 版本从 env_requires 提取（296-320）；复制 patch（352-367）；setup 命令串的 `{{uv}}/{{repo_dir}}/{{venv_path}}/{{python}}/{{oneeval_root}}` 占位符替换（375-395）；写 `.setup_complete`（419-425）。

**Docker 沙箱**：`env_requires.sandbox=="docker"` 触发（435-444）；`_ensure_docker_image`（466-545）先 `docker image inspect` 探镜像（482-488），没有则按 `repo_config.dockerfile` 构建——context 复制清单硬编码 `["pyproject.toml","setup.py","setup.cfg","lcb_runner","README.md"]`（520），build 超时 3600s、首次 10-20 分钟（529-533）。`_build_docker_argv`（547-655）：`-v` 挂仓库与输出目录 rw（592-593），另挂 pip/uv/HF 三缓存卷（595-597）；`--memory 16g --cpus 4 --cap-drop ALL --security-opt no-new-privileges`（587-591）；API key 走 `--env` 不落盘（603-604）；宿主代理 localhost 改写 host.docker.internal（612-618）；容器内命令=`pip install uv`+`uv pip install --system`（630-640）——「uv 就地安装」：镜像只预装 uv，依赖容器里现装。

**执行解析 `run_evaluation`**（657）：`run.argv` 模板+`{{params_argv}}` 展开参数（722-725）；超时 57600s=16h（789/799）；返回码非 0 读日志尾 2000 字分类 network_ssl/network_download 给建议+retryable（802-837），**返回码 0 也查 "skipping this combination"**（843）防假成功。`parse_results`（900）glob 找结果文件、多个取 mtime 最新（952-960），score_path 点路径取分（1045-1057）。

**评测桥族考古**：patches/ 下 5 个 Dockerfile（bfcl/gaia/humanevalplus/livecodebench/mbppplus）。humanevalplus 与 mbppplus 的 Dockerfile 逐字节相同（python:3.11-slim+`evalplus openai httpx`）；且 gallery 里 mbppplus 的 patch_files 直接引用 `one_eval/patches/humanevalplus/run_humanevalplus_oneeval.py`——EvalPlus 双子星共用同一上游工具链与同一桥。livecodebench 特殊：`COPY repo /tmp/repo` 预装依赖、运行时被 volume 覆盖（Dockerfile:9-10 注释），并钉 `datasets<3.0`。

**必现 bug**：`patches/livecodebench/utils_execute.py:81` 的 `multiprocessing.Process(target=unsafe_execute,...)`——`unsafe_execute` 全文件 0 处定义（grep 实证仅此 1 处引用）。该 patch 从 OpenAI human-eval execution.py 改写、本意修 Manager 泄漏与僵尸进程（18-22 注释），但把 `unsafe_execute` 函数体裁掉了：每道代码题判分必 NameError。收录级发现：补丁自身带 bug，且藏在「clone 后复制进外部仓」链路里，主仓测试永远看不见。

## 外部连接

配置全来自 bench_gallery.json 的 `meta.repo_eval`（04 篇）。调用方**不是** server 主链，而是 one-eval-skill 的 `run_eval.py:158/179`——skill 遇 `bench_kind=="external_repo"` 分流到本 Runner，DataFlowEvalTool 只管 dataflow 类。`model_interface:"api"` 的仓靠 env_vars 注入 OPENAI_API_KEY/BASE。

## 数据流

gallery.repo_eval → setup_repo（clone/venv/patch/setup）→ run_evaluation（argv 渲染→docker 或宿主执行）→ parse_results（glob→score_path 取分）→ 分数回填。

## 设计决策（含批判）

1. **隔离三件套**（ref 目录隔离/独立 venv/沙箱）把「外部仓不可信」当前提，姿态正确；代价是每仓首装 10-20 分钟、磁盘双份。
2. **镜像发现-构建一体**：inspect 失败自动 build；但 context 清单硬编码 `lcb_runner`，新仓装非标准布局依赖就得改源码。
3. **返回码 0 仍查跳过日志**（843）是实战防御——上游脚本失败常以 0 退场。
4. **patch 热更新按 mtime**（229）有同刻风险；mbppplus 借 humanevalplus 桥说明桥按「上游工具链」划分，命名不表义。

## 新人提示

跑前确认 docker 可用（446）；排障读 `cache/external_repos/<repo>/<ref>/` 的 external_repo.log 尾部；重装删整个 ref 目录（`.setup_complete` 在里面）。改补丁 mtime 变化自动热更，依赖变化必须删目录重装。livecodebench 判分全崩先查本篇 NameError，别急着怀疑模型。
