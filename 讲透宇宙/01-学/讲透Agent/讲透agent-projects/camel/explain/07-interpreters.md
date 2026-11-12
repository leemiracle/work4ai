# 07 沙箱解释器：camel/interpreters/

## 1. 角色定位

camel/interpreters/ 是 agent 执行生成代码的唯一通道：LLM 产出的代码字符串经这里的解释器落进 Python/bash/R/Node 四种运行环境。包内 1 个抽象基类 + 6 个实现，隔离强度呈谱系分布——InternalPythonInterpreter（进程内 AST 解释）→ SubprocessInterpreter（裸子进程）→ JupyterKernelInterpreter（jupyter 内核）→ DockerInterpreter（本地容器）→ E2BInterpreter / MicrosandboxInterpreter（外部沙箱云）。两个消费方：EmbodiedAgent 默认装配（embodied_agent.py:81/83，未指定时二选一 InternalPythonInterpreter/SubprocessInterpreter），以及 CodeExecutionToolkit（camel/toolkits/code_execution.py:16）把全部实现导出为工具。契约只有四个方法：`run`（执行代码）、`supported_code_types`、`update_action_space`、`execute_command`（camel/interpreters/base.py:22-62 全部 @abstractmethod）。

## 2. 内部结构

**InternalPythonInterpreter（camel/interpreters/internal_python_interpreter.py，610 行）**是谱系里最特殊的一档：改自 HuggingFace transformers 的 python_interpreter.py（docstring 自述血统），不落子进程，而是 `ast.parse` 后逐节点解释执行（camel/interpreters/internal_python_interpreter.py:211 的 `execute`）。安全模型三层：`action_space` 白名单字典（:89 构造，:108 `_add_safe_builtins` 注入 print/len 等 36 个"安全内置"）、`import_white_list` 导入白名单、`fuzz_state` 模糊变量名匹配（:99，image 可被 input_image 访问到）。`run`（:151）在 `unsafe_mode=True` 时直接 `exec(code, self.action_space)`（:189）跳过全部 AST 检查。

**SubprocessInterpreter（subprocess_interpreter.py）**是本机直跑档：代码写临时文件后按 `_CODE_EXECUTE_CMD_MAPPING`（:51）拼 `python {file_name}` 起子进程。最有巧思的是 run_file 的 REPL 回显（:110-159）：用 `ast.parse` 把末尾非 print 的表达式语句改写为 `print(repr(...))` 再经 `astor.to_source`（:159）回转源码——模拟 notebook 尾表达式回显；AST 解析失败则回退原文件直跑。

**DockerInterpreter（docker_interpreter.py）**：懒初始化容器（:94 `self._container` 初值 None），首次 run 时现场从包内 Dockerfile 构建镜像 camel-interpreter:latest；每次 run 把代码打包成 uuid4 命名文件 put_archive 进容器 /tmp（:144-160）。该 Dockerfile 是多语言沙箱镜像（Ubuntu 24.04 + deadsnakes python3.10 + Node 22 + R + shell），且 `ln -sf /opt/venv/bin/python /usr/bin/python`（docker/Dockerfile:36）把系统 python 劫持到 venv——容器内"python"实际是 /opt/venv 解释器。

**其余三家**：JupyterKernelInterpreter（注意：文件名是 ipython_interpreter.py:28，类里没有 IPython，底层是 jupyter_client 的 KernelManager）；E2BInterpreter / MicrosandboxInterpreter 是外部 SaaS 沙箱客户端。interpreter_error.py 全仓单类 19 行，文件头自带上游 TODO "Do we need a file to store this error class?"（:15）。

## 3. 外部连接

- **EmbodiedAgent**（agents/embodied_agent.py:20-23）：action_space 概念的源头——embodied agent 的可执行动作注入解释器白名单。
- **CodeExecutionToolkit**（camel/toolkits/code_execution.py:16）：唯一同时导出全部 6 实现的地方，含 E2B/Microsandbox。
- **camel/prompts/base.py:17** 也有条反向引用：CodePrompt.verify 直接 `SubprocessInterpreter().run(...)`（camel/prompts/base.py:196）验证生成代码可执行——prompts 层对 interpreters 的硬依赖。
- **camel/interpreters/docker/Dockerfile**：非部署文件，是 docker_interpreter 运行时 build 的素材（deploys 边方向钉版）。

## 4. 数据流

以 EmbodiedAgent 一次动作为例：agent 的 action（代码字符串）→ `run(code, code_type)` → code_type 经 `_CODE_TYPE_MAPPING` 归一化（subprocess:63 / docker:66 的字典把 py3/js/bash/shell 全折叠到四主类型）→ 确认循环（见下）→ 执行环境落点（进程内 dict / 子进程 / 容器）→ stdout/stderr 字符串回传给 LLM 作为观察。InternalPythonInterpreter 的 state 会跨 run 保留（:216 `keep_state=True` 默认），变量在多次执行间存活——这也是它像 REPL 的原因；clear_state（:283）重置回 action_space 拷贝。

## 5. 设计决策

1. **"沙箱"二字要打折**：InternalPythonInterpreter 的白名单只覆盖 `execute()` 的 AST 通道；`execute_command`（:588）用 `subprocess.Popen(..., shell=True)`（:598-604）直接跑任意 shell 命令，白名单对命令通道零约束；unsafe_mode 更连 AST 通道也放弃。图谱钉版结论：它是"代码解释器"而非安全沙箱，真隔离只有 Docker/E2B/Microsandbox 三档。
2. **update_action_space 的三态度**（BaseInterpreter 定为抽象方法强制表态，camel/interpreters/base.py:47）：InternalPythonInterpreter 唯一真正支持（:203 merge 进 action_space）；Docker（docker:289）/E2B（e2b:228）/Jupyter（ipython:184）/Subprocess（subprocess:389）四家 raise RuntimeError；Microsandbox 只 logger.warning 静默降级（microsandbox:328）——六实现三态度，调用方须按实现感知。
3. **[Y/n] 确认循环四份拷贝漂移**：docker_interpreter.py:242 与 subprocess_interpreter.py:299 的 choice 列表含 `""`（空回车=Y）；e2b_interpreter.py:141 与 microsandbox_interpreter.py:300 不含——同份代码复制后语义分叉，空回车在后两者会 continue 死循环追问。
4. **Docker 的 /tmp 泄漏**：run 成功路径不清理注入文件（docker_interpreter.py:257 注释 "Clean up after execution" 之下并无动作），容器复用到 `__del__`/cleanup()（:194）；每次 run 注入新 uuid4 文件随容器累积。
5. **懒初始化 + 构造零副作用**：Docker 解释器构造不连 Docker daemon，首次执行才 build 镜像——import 期不碰重依赖是全包惯例（docker/e2b/jupyter/microsandbox SDK 全部函数体内延迟 import）。

## 6. 新人提示

- **按文件名找类会扑空**：ipython_interpreter.py 里没有 IPythonInterpreter，导出的是 JupyterKernelInterpreter（barrel 第 20 行）；按 `class IPython` grep 零命中。
- **要真隔离就别用前两档**：InternalPythonInterpreter 与 SubprocessInterpreter 都在本机进程内/旁执行，require_confirm=True 是唯一人工闸门；agent 自主循环场景务必显式关确认或换 Docker/E2B。
- **astor 是运行时硬依赖**：subprocess_interpreter 的回显技巧依赖 astor 且放在函数体内 import（:110），pyproject 未装时首次 run_file 才爆 ImportError——测试环境要预装。
- **多语言沙箱镜像的 python 陷阱**：Dockerfile 同时装 pip/uv/poetry 三套包管理器且劫持 /usr/bin/python；在容器内 `python3` 与 `python` 可能指向不同解释器（3.10 venv vs 系统），调试时先 `which` 确认。
- **E2B/Microsandbox 需要 API key 与外网**：构造期无 key 校验（延迟到连接时），CI 里忘了配会到 run 阶段才失败，报错离根因远。
