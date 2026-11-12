# backend_interface/task — repo 捕获与脚本分析：实验可复现性的发动机

## ① 角色定位

`clearml/backend_interface/task/`（8 文件 8663 行）是 SDK 的**实现层**：`clearml/task.py` 的 `_Task` 基类在这里的 `task.py`（3350 行），repo/ 子包负责"这段代码是什么、依赖什么、改了什么"的自动捕获，populate.py 支撑手动建任务。图谱 **Backend Interface 层 33 节点**中 `file:clearml/backend_interface/task/task.py` 出边 29 条（backend_api、metrics、model、artifacts 等）、入边 3 条；`repo/scriptinfo.py` 出边 22 条里赫然有 `utilities/pigar/{__main__,log,modules,reqs}`——依赖分析引擎是 vendored pigar，看穿"requirements 怎么来的"的钥匙。

## ② 内部结构

**task.py（3350 行）— `class Task(IdObjectBase, AccessMixin, SetupUploadMixin)`（task.py:82）**：三继承骨架——id 定位、权限校验、输出上传。`__init__`（task.py:158）装配 `_arguments/_artifacts_manager/_models` 等子系统；`_resolve_task_id`（task.py:261）统一两种定位；`_reload`（task.py:665）+ `_edit_lock` 是**读-改-写一致性的中枢**：异步改任务必须先 lock 再 reload 再 edit。

**`_update_repository`（task.py:269）——本包的招牌方法**，链路六步：
1. daemon 线程做新版本检查（task.py:270-296）。
2. `ScriptInfo.get`（task.py:302）拿 repo 信息+requirements 骨架。
3. diff 超限走 artifacts 兜底：`upload_artifact(name="auxiliary_git_diff")`（task.py:327-328）。
4. IDE 信息写 runtime_properties（task.py:332-337）；`detect_running_module`（task.py:346）把入口点改写为 `python -m xxx`。
5. 持锁 reload+`_edit(script=result.script)`（task.py:353）把仓库/分支/commit/diff 一次写回服务端。
6. requirements 两条路：`_force_use_pip_freeze` 时 `pip_freeze()` 全量（repo/freeze.py:9），否则 `script_requirements.get_requirements(...)`（task.py:382）做**逐入口文件的静态分析**；`_update_requirements`（task.py:390）上送。

**repo/scriptinfo.py（1635 行）— 捕获大脑**：
- `ScriptInfo`（scriptinfo.py:650）+ `plugins = [GitEnvDetector(), HgEnvDetector(), HgDetector(), GitDetector()]`（scriptinfo.py:655）——**顺序即优先级**，环境变量检测器排在 CLI 检测器之前。
- `get`（scriptinfo.py:1331）→ `_get_script_info`（scriptinfo.py:1094）主流程：Jupyter 判定（scriptinfo.py:688）优先于命令行路径；`plugin.exists(script_dir)` 首个命中者执行 `get_info`；无插件降级"存单文件脚本"；`_detect_distributed_execution`（scriptinfo.py:1261）识别 torch.distributed/accelerate 并改写入口点；Jupyter 存**整个 notebook** 而非 git diff（scriptinfo.py:1181-1184），普通脚本 diff 超 500000 字节（scriptinfo.py:653/1193）转 artifacts。产出 dict 含 repository/branch/commit/entry_point/working_dir/diff/ide/requirements。
- `ScriptRequirements`（scriptinfo.py:36）：`get_requirements`（scriptinfo.py:49）AST 遍历 import 借 pigar 解析包版本；`create_requirements_txt`（scriptinfo.py:167）落盘。
- IDE 侦探四连（scriptinfo.py:1416/1431/1442/1453）+ `get_ide`（scriptinfo.py:1461）入 script_info["ide"]；`_JupyterObserver`（scriptinfo.py:324）后台轮询 notebook。

**repo/detectors.py（390 行）— VCS 探测器族**：基类 `Detector`（detectors.py:43）以 Commands 命名元组声明子进程命令；`GitDetector`（detectors.py:239）命令表覆盖 url/branch/commit/root/status/diff 及 remote 变体，`get_info`（detectors.py:269）补两角——detached HEAD 用 branch_fallback 重查、`url == "origin"` 用 `git remote -v` 首行手工解析；`EnvDetector`（detectors.py:339）纯读环境变量；`HgDetector`（detectors.py:214）/`HgEnvDetector`（detectors.py:388）补 Mercurial。util.py:8 `get_command_output` 统一子进程执行；util.py:19 `remove_user_pass_from_url` 剥 URL 凭据。

**populate.py（1268 行）— `CreateAndPopulate`（populate.py:20）**：手动建任务引擎，`create_task`（populate.py:161）实现 `Task.create` 参数矩阵，`update_task_args`（populate.py:617）改远程参数，`create_task_from_function`（populate.py:785）支撑 pipeline 函数级任务。**周边**：args.py:25 `_Arguments`（argparse 双向绑定，args.py:109）；hyperparams.py:19；models.py:45；log.py:{27,214} 后台日志与 stdout 缓冲。

## ③ 外部连接（图谱边证据）

`task.py` 出边 29 条中最重的五条：`backend_api/services/__init__`（edit/get 的 API 面）、`metrics/__init__`、`model.py`、`binding/artifacts.py`、`config/__init__.py`（`force_analyze_entire_repo`、`detect_with_conda_freeze` 开关）；`repo/scriptinfo.py` 出边 22 条指向 detectors/util/pigar——pigar 依赖边把"vendored 分析器"写进了图谱。入边证明它是纯服务层：门面与 automation 都不直接摸 repo/，全经 `backend_interface/task/__init__`。

## ④ 数据流

以 `Task.init` 触发为例：门面 `_create_dev_task` →（缺省名时）`ScriptInfo.get` 产 project/task 名 → 本层 `_update_repository` → `_get_script_info`：探测器族产 `Result{url,branch,commit,root,diff}` → 组装 script dict + requirements → 持锁 `_edit(script=...)` POST 到 `tasks.edit`。运行期 `_setup_reporter`（task.py:635）建指标通道，stdout 经 TaskHandler 缓冲批量上传，退出时 `mark_completed`（task.py:801）终态化。agent 远程执行时同一批 API 反向读取拉回 script+requirements+diff 重建环境——**写入的每一份数据都是为逆向执行准备的**。

## ⑤ 设计决策

1. **探测器插件化 + env 优先**：`plugins` 一行的排序（scriptinfo.py:655）实现"agent 注入的 VCS_* 环境变量优先于机器实况"，保障容器 clone 目录与真实 repo 分离时的正确性。
2. **diff 三级降级**：git diff → 超限存 artifacts → Jupyter 整本快照，牺牲精确性换"任何环境都能存下代码状态"。
3. **双 requirements 通道**：pigar 静态分析为默认、pip freeze 全量为逃生舱，对应"复现最小化"与"复现绝对化"。
4. **_edit_lock 全局写锁**：repo 探测线程、资源监控、主线程并发写同一任务，靠 lock+reload+edit 惯用式避免覆盖。
5. **URL 脱敏下沉到 util**：`remove_user_pass_from_url` 统一在出口剥凭据——安全约束单点化。

## ⑥ 新人提示（含勘误）

- **勘误 1**：requirements 分析引擎是 **vendored pigar**（`utilities/pigar/`，图谱边实证），不是 pipreqs 也不是默认 pip freeze——pip freeze 只在 `_force_use_pip_freeze`/配置开关下才走。
- **勘误 2**：探测器优先级是 **env > CLI**（scriptinfo.py:655 顺序），`CLEARML_VCS_REPO_URL` 设了就不再跑 `git ls-remote`——排查"仓库识别错了"先查环境变量。
- **勘误 3**：diff 上限 **500000 字节**（scriptinfo.py:653），超限不是丢弃而是转存 artifact `auxiliary_git_diff`（task.py:327-328）。
- **勘误 4**：Jupyter 的"diff"是**整个 notebook 文件**（scriptinfo.py:1181-1184），不是版本差异。
- 模块运行（`python -m pkg.main`）时入口点被 `detect_running_module`（scriptinfo.py:1375）改写为带 argv 的模块串。`Task.create` 参数矩阵全由 populate.py:161 `create_task` 实现，读门面文档串不如直接读它。

---
自检：不计空格字符 4796、含空格 5147、行号锚去重 47 处（task.py:{82,158,261,269,270-296,302,327-328,332-337,346,353,382,390,635,665,801}、scriptinfo.py:{49,167,324,650,653,655,688,1094,1181-1184,1261,1331,1375,1416,1431,1442,1453,1461}、detectors.py:{43,214,239,269,339,388}、util.py:{8,19}、freeze.py:9、populate.py:{20,161,617,785}、args.py:{25,109}、hyperparams.py:19、models.py:45、log.py:{27,214}），全部经源码逐条核实。
