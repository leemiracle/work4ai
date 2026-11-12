# 09 · clearml-task CLI：远程执行的命令行入口

## ① 角色定位

`clearml-task` 是 ClearML SDK 自带的五个 console_script 之一（setup.py:108-112 列出 init/data/task/param-search/debug 五兄弟），映射关系钉在 setup.py:110：`clearml-task = clearml.cli.task.__main__:main`。它的职责一句话讲清：**把"本地的一份代码/脚本/离线会话"变成 ClearML 服务器上的一个 draft Task，并可选地投递到队列**，之后由远端机器上的 clearml-agent 拉取并复现执行——所谓"零额外代码把任何代码库送上远程机器"（docs/clearml-task.md:1 的标题即 "Execute ANY python code on a remote machine"）。整个工具是单文件 350 行的扁平 CLI（`clearml/cli/task/__main__.py`），无子命令、无交互式向导，与 `clearml-init`（向导式）风格截然不同。图谱中该文件被 `document:docs/clearml-task.md` 以 documents 边指向，是全仓库少数有专属文档页的 CLI。

## ② 内部结构

**模块加载即注册**：`__main__.py:11` 在 import 时就调用 `Session.add_client("clearml-task", __version__)`，把工具名与版本挂进 API 会话客户端标识——服务器端因此能区分"这是 clearml-task 发起的请求"。

**setup_parser()（__main__.py:14）**：约 30 个参数，按语义分五组——
- 源三选一：`--repo`（远程 git URL，:39）、`--folder`（本地已有 git 仓，help 文案 :59-65 明言会记录当前 commit 与未提交改动并在远端复现）、`--base-task-id`（克隆既有 Task，:170）；
- 入口：`--script`（.py/.ipynb/.sh，:68-79）、`--module`（与 --script 互斥，:87-94）、`--binary`、`--cwd`；
- 依赖：`--requirements`/`--packages`/`--force-no-requirements`；
- 容器：`--docker`/`--docker_args`/`--docker_bash_setup_script`（:142-147）；
- 特殊：`--import-offline-session`（:178-182，导入离线会话）、`--pipeline` 系列（:201-216）。

**cli() 主流程（__main__.py:219）**：
1. `:236-237` 无 `--name` 且非导入离线会话直接 ValueError；
2. `:239-246` 若 `--docker_bash_setup_script` 是文件路径则读入内容并剥掉首行 shebang——注意传给后端的是**脚本内容**而非路径；
3. `:253-254` `--skip-python-env-install` 通过往 docker_args 追加 `-e CLEARML_AGENT_SKIP_PYTHON_ENV_INSTALL=1` 实现，即 CLI 层不直接支持该语义而是转成 agent 侧环境变量；
4. `:257-258` 检测 `.sh` 后缀打印提示（真正的 binary 设置在 agent 侧）；
5. `--pipeline` 分支（:259-286）：手工把 `--args` 按 `=` 切成二元组（格式错即 :263-264 报错），调 `PipelineController.create`（:266-285），拿 `pipeline._task` 当产出；
6. 常规分支（:288-310）：构造 **CreateAndPopulate**（`clearml/backend_interface/task/populate.py:20`），这是真正干活的类——它负责分析本地 git 仓（diff、未提交变更）、解析 requirements、必要时给入口脚本注入 `Task.init()` 调用（populate.py:475 `add_task_init_call` 分支）；
7. `:312` 与 `:316` **update_task_args 被调用两次**——第一次在创建 Task 前校验参数合法性（注释 "verify args before creating the Task"），第二次在 `create_task()`（:314，populate.py:161）之后真正写入超参；
8. `:323` 打 runtime property `_CLEARML_TASK: True`，供 Web UI 识别"此 Task 由 CLI 创建"；
9. `:327-329` 无 `--queue` 则留在 draft 模式退出（这是特性：先创建后手动入队）；
10. `:331` `Task.enqueue(created_task, queue_name=...)` 投递，随后打印执行日志页 URL。

**main()（__main__.py:339-346）**：捕获 KeyboardInterrupt 打印 "User aborted"；其余异常统一 `print(f"\nError: {ex}")` + `exit(1)`。

## ③ 外部连接（图谱边证据）

- imports 边 4 条：`file:clearml/__init__.py`（取 Task/PipelineController）、`file:clearml/backend_api/session/__init__.py`、`file:clearml/backend_interface/task/populate.py`（核心依赖）、`file:clearml/version.py`；
- documents 边 1 条：`document:docs/clearml-task.md → 本文件`，全仓 CLI 中仅此一份；
- contains/exports 边：setup_parser、cli 两个函数。
- 代码内部（grep 实证）：CreateAndPopulate 位于 backend_interface 层，与 `Task.create`/`Task.clone` 共享同一套"组装脚本+diff+依赖"的机制；`Task.enqueue` 走 backend_api 的 tasks service。

## ④ 数据流

argv → argparse（setup_parser）→ 分流（pipeline / 常规 / 离线导入）→ CreateAndPopulate 扫描本地仓：git diff 聚合为脚本附带 diff、requirements 解析为 `script.requirements`、entry_point 定位 → `create_task()` 在服务器创建 draft Task（脚本、diff、依赖、docker 配置全部随 Task 元数据上传）→ 校验后的 `--args` 覆写超参 → 打 `_CLEARML_TASK` runtime property → `Task.enqueue` 推入目标队列 → 远端 clearml-agent 按队列消费：clone Task、还原 diff、安装依赖（除非 skip）、注入或尊重 Task.init、执行并回传指标。`--base-task-id` 路径则跳过本地分析，直接在克隆体上覆写。

## ⑤ 设计决策

1. **验证先于创建**：update_task_args 两段式（:312 校验/:316 写入）让参数错误在创建 Task 前就失败，避免服务器留垃圾 draft。
2. **本地状态完整复制哲学**：`--folder` 模式连 uncommitted changes 都以 diff 形式记录（:62-65 help），复现优先于简洁。
3. **CLI 只做编排不做执行**：一切环境语义（skip-python-env-install 等）转译为 agent 侧约定（env/docker_args），保持 CLI 与 agent 解耦。
4. **bash 脚本以内容内嵌**：shebang 剥离（:243-244）保证跨端执行不依赖源机路径。
5. **--queue 缺省不报错**：支持"先备好 Task 再挑队列"的两步工作流（:115 help 明示）。

## ⑥ 新人提示（含勘误）

- **勘误 1**：`clearml/cli/task/__init__.py` 是空文件，不要去找 task.py——全部逻辑在 `__main__.py`；目录名 "task" 只是为了与其他 CLI 子包（config/data/hpo/debug）对齐。
- **勘误 2**：`--args` 只支持 argparse 风格的 `key=value`（:106-108 help 与 :262-264 解析双重限定），click/absl 等参数风格不能直接传。
- **勘误 3**：`main()` 把所有异常压成一行 print（:344-346），exit code 恒为 1——CI 里无法靠退出码区分错误类型，需解析 stdout。
- `--script xxx.sh` 的 binary 自动切 `/bin/bash` 只是打印提示（:257-258），实际切换发生在 agent；若显式给了 `--binary` 则以用户为准。
- 无 `--queue` 时 Task 停在 draft 是设计行为（:327-329 的 Warning），不是投递失败。
- 想本地预演不真正建 Task，可参考 CreateAndPopulate.create_task 的 dry_run 参数（populate.py:161 签名），CLI 未暴露但 API 可用。
