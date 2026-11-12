# 11 SWE Agent：Princeton 命令集的 Python 嫁接与 Bash 环境契约

## 1. 角色定位

SWEAgent 是"自主修 GitHub issue"的角色：给它一个仓库 checkout 和 issue 文本，它滚动 open/edit/search/submit 命令直到产出 diff。选址勘误：任务描述给的 `metagpt/ext/swe_agent/` 不存在，实际由三块组成——`metagpt/roles/di/swe_agent.py`（83 行角色主体，`class SWEAgent(RoleZero)` L17，name "Swen"）、`metagpt/tools/swe_agent_commands/`（8 个 shell 脚本命令集，provenance 是 princeton-nlp/SWE-agent 原版 + OpenDevin 修改版，见 __init__.py 与 setup_default.sh:6 的上游 commit 链接）、`metagpt/prompts/di/swe_agent.py`（模板与 few-shot）。它不是从零写的 agent，而是把 SWE-bench 的 bash 命令协议嫁接到 RoleZero 命令循环上——LLM 输出的 "Bash.run" 命令直达一个被 shell 函数武装过的持久会话。

## 2. 内部结构

角色侧只做三件事：`_update_tool_execution`（swe_agent.py:38）把 "Bash.run" 绑到 terminal、把 "git_create_pull" 绑到 PR 工具；`_format_instruction`（L46-54）每轮 think 前先 `await self.terminal.run("state")`（L52）、`json.loads` 其输出（L53）、用 `CURRENT_BASH_STATE.format(**bash_state)`（L54）把"当前打开文件/工作目录"填进指令模板（prompts/di/swe_agent.py:241-245）；`_parse_commands_for_eval`（L62-80）在 todo 归 None 的终轮跑 `git diff --cached`（L74）并经延迟导入的 `extract_patch`（L71，swe_agent_utils.py:7）从 `<<SUBMISSION START||...||SUBMISSION DONE>>` 标记对中切出 `diff --git` 起始的补丁存 `output_diff`——这是 SWE-bench 评测专用出口，`run_eval=False`（L31）时整体旁路。经验侧 `_retrieve_experience`（L82）直接返回 MINIMAL_EXAMPLE（prompts/di/swe_agent.py:7）——内嵌真实 issue geekan/MetaGPT#1275（openai_api.py 流式 usage NoneType 崩溃）的完整修复轨迹作 few-shot。

## 3. 外部连接

核心契约链四方咬合：`tools/libs/terminal.py:185` 的 `Bash` 在 `__init__` 里 `os.environ["SWE_CMD_WORK_DIR"] = str(Config.default().workspace.path)`（L193）注入工作目录；`Bash.start()`（L197-199）`source {SWE_SETUP_PATH}`——该常量在 `metagpt/const.py:155` 指向 setup_default.sh；setup_default.sh（L3 先 `pip install flake8`，L7-8 用 BASH_SOURCE 定位自身避免 source 后 CUR_DIR=/bin）按序 source `_setup_default_env.sh`（L10，导出 WINDOW=100/OVERLAP=2/CURRENT_LINE/CURRENT_FILE 并定义 `state()`，_setup_default_env.sh:13-20）与 defaults/search/edit_linting 三个命令脚本（L15-17），L13 把目录挂进 PATH 使 `_split_string` 可执行，L19 echo 确认 SWE_CMD_WORK_DIR。SWE_CMD_WORK_DIR 的两个消费点都在脚本侧：edit_linting.sh:71/141/164 用它存取编辑备份，defaults.sh:183-185 submit 时反向 apply test.patch。向上 SWEAgent 继承 RoleZero 全套（Editor/Browser/exp_cache），向上游则对齐 SWE-bench 的 ACI（agent-computer interface）。

## 4. 数据流

一轮循环：issue 文本入 memory → `_think` 先 format_instruction（state 命令→JSON→当前文件/目录拼进 prompt）→ LLM 产出命令（如 Bash.run("open metagpt/llm.py")、Bash.run("edit 50:55 ...")）→ 持久 bash 会话执行 shell 函数 → 函数 echo 结果（含 lint 报错/窗口内容）回给 agent 当观测 → 循环至 LLM 发 submit → `_parse_commands_for_eval` 抽 diff。全部状态（CURRENT_FILE/CURRENT_LINE/SEARCH_RESULTS）活在 bash 环境变量里，Python 侧每轮只通过 state() 这个窄窗口窥视——两个语言边界只交换 JSON 字符串，这是整个设计最干净的地方。

## 5. 设计决策

其一，命令即 shell 函数：把 SWE-bench 验证过的 ACI 原样搬来（open/scroll/edit 带窗口语义、edit 带 lint 门禁），LLM 迁移成本为零。其二，lint 门禁是"只拦新增"——edit_linting.sh:51 先存 `original_lint_output`，L81 编辑后再跑 flake8，L92-93 把行:列 sed 归一化为 `:LINE:COL:` 后 `cmp -s` 比较（L97），只有引入新错误才拒绝（L118）；仓库原有 lint 错误不阻塞编辑，这对烂尾仓库友好但意味着 agent 可能带着存量错误提交。其三，评测路径与生产路径同体但开关隔离。四处钉版坑：defaults.sh:139 scroll_up 的 `# docstring: moves the window down {WINDOW} lines` 是上游复制粘贴笔误原样保留（scroll_down L125 才真是 down）——docstring 是 LLM 看的命令说明，笔误会误导模型；`_split_string` 与 `_split_string.py` md5 同为 e8dda12c 字节级双副本，无扩展名那份专为 PATH 执行存在（setup_default.sh:12-13），改一份必忘另一份；search.sh 的 `search_dir_and_preview` 对同一目录做 4 次独立 find+grep 全量扫描（L30/L35/L101/L102 分别取 matches/带行号/文件名/行号），大仓库下是移植自 OpenDevin 的性能坑；swe_agent_utils.py:29 `np.array(...)` 算完即丢的死代码、L18 `existing_ids: list = []` 可变默认参数。另注意 jq 是硬依赖——_print/_constrain_line/open/goto/scroll 的行号算术全走 `jq -n`，与 flake8 一样被 setup 脚本假定存在。

## 6. 新人提示

跑起来最小条件：Python 侧 `Bash.start()` 会 source 全套脚本并 pip install flake8，确保 jq 在 PATH；workspace 即 SWE_CMD_WORK_DIR，issue 仓库要先 checkout 进去。调"为什么 agent 总说 no file open"沿契约链查：terminal.py:193 的环境变量→setup_default.sh:19 的 echo→_setup_default_env.sh:7 的 CURRENT_FILE 初值。给新仓库适配时优先改 edit_linting.sh 的 flake8 规则集（L51/L81 的 --select 列表）与 WINDOW 大小，别动 state() 的 JSON 键名——swe_agent.py:53 的 `json.loads` 与 CURRENT_BASH_STATE 的 `{open_file}` 占位符两头咬合，改一边必崩。做 SWE-bench 复现记得 run_eval=True 并在终轮前显式 `git add`，否则 `git diff --cached` 拿到空补丁。想读懂命令语义别看函数名，看每个函数头的 `@yaml docstring`——那是发给 LLM 的说明书（也是 scroll_up 笔误的病灶所在）。
