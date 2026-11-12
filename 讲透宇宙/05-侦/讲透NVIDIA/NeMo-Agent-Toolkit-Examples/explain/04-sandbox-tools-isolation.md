# 04 沙箱内工具族：shell/python/file_ops/browser 与隔离边界设计

## 角色定位

`src/nat_sandbox_agent/tools/sandbox/` 四个工具模块（execution.py 169 行含 shell+python、file_ops.py 187 行、browser.py 165 行、executor.py 71 行）定义 agent 在隔离容器内的全部能力面：跑命令、跑代码、读写文件、无头浏览器。它们与第 3 篇宿主工具的本质区别是**执行位置**：这里每个动作最终都变成第 2 篇 `BaseSandbox` 上的 `run_command/write_file` 调用，跑在容器里。隔离边界设计因此成为本篇主线——哪些约束放在容器外（路径白名单、转义）、哪些交给容器本身（资源限额、网络开关）、哪些靠提示词约定（工具分工），三层防线各管一段。工厂 `create_sandbox_tools`（tools/sandbox/__init__.py:37）先造唯一 `SandboxToolExecutor`（tools/sandbox/__init__.py:56-59），再派生五工具（tools/sandbox/__init__.py:61-67），include_tools 含未知名直接 ValueError（tools/sandbox/__init__.py:71-74）。

## 内部结构

**execution.py 双执行器**。`execute_shell`（execution.py:47-77）最薄：直接 `sandbox.run_command`，返回 stdout/stderr 双截断 + exit_code。`execute_python`（execution.py:80-122）三步：先把代码 `write_file` 到 `DEFAULT_SCRIPT_PATH=/workspace/temp/_script.py`（execution.py:99，常量定义在 base.py:36），再 `cd /workspace && python3` 执行（execution.py:110），最后 `list_generated_files` 扫 /workspace/output 收集产物清单一并返回（execution.py:115）。"落盘再执行"而非 `python -c` 内联，注释说明是为了**更好的错误信息**（execution.py:97）——traceback 带真实文件名与行号。两个 `create_*_tool` 的 description 是精心设计的互斥分工：shell 管 "SYSTEM OPERATIONS"（文件管理/装包/下载/进程/git，execution.py:137-143），python 管 "DATA PROCESSING"（pandas/计算/解析，execution.py:160-167），双方都带 "Do NOT use … use X instead" 负向约束。

**file_ops.py 带白名单的文件门**。模块级 `ALLOWED_BASE_PATHS=(PurePosixPath("/workspace"),)`（file_ops.py:31）；`_validate_path`（file_ops.py:34-59）做三查：posixpath.normpath 归一化消解 `..` 穿越（file_ops.py:47）、必须绝对路径（file_ops.py:50-51）、**组件感知的归属判定** `normalized == base or base in normalized.parents`（file_ops.py:55）——注释特意指出这比字符串 startswith 强：`/workspace2` 不会误匹配 `/workspace`（file_ops.py:53-54）。read/write 两函数（file_ops.py:75-113、116-151）先过校验再调沙箱，ValueError/FileNotFoundError 都转成 status=error 信封而非异常。

**browser.py 代码生成器**。`web_browse`（browser.py:57）不直接驱动浏览器，而是**现场生成一段 Playwright Python 脚本**塞进沙箱跑：URL 用 `json.dumps` 转义成安全字面量（browser.py:79）；selector 走 `_escape_css_selector` 三重清洗——反斜杠先转、引号再转、换行符删（browser.py:41-43）——再嵌入 f-string（browser.py:85-93）；无 selector 则取 body 文本（browser.py:95-97）。整段脚本（browser.py:99-130：launch headless chromium → goto domcontentloaded → title+content → print(json.dumps(result))）写到 `/workspace/temp/_browser_script.py`（browser.py:133-134）后 `python3` 执行、超时 60s（browser.py:135），stdout 解析 JSON 回传（browser.py:137-141），解析失败退回 stderr 信封（browser.py:143-146）。

## 外部连接

- **向下**：全部动作经 executor.py 的 `self.sandbox` 落到 BaseSandbox（executor.py:47）；`truncate` 复用 common.py:22-33。
- **向上**：register.py:173 经双工厂拿到五工具；system_prompt.py:23-33 的工具清单与各 description 互为镜像（"Do NOT use shell for data processing" 在 system_prompt.py:24-25 与 execution.py:143 各出现一次）。
- **横向**：browser 产物路径与 WORKSPACE_TEMP 常量体系（base.py:29）对齐；python 工具的 output 目录约定 /workspace/output 与 image_describe、list_generated_files（executor.py:55-64）三方共享。
- **环境前提**：Playwright/Chromium 必须预装在沙箱镜像内（config.yaml 用 `nat-sandbox:latest` 预装镜像而非裸 python:3.12-slim，原因在此）。

## 数据流

python 工具一次调用的完整链：LLM 产出 code → execute_python 落盘（execution.py:99）→ 容器内 `cd /workspace && python3 /workspace/temp/_script.py`（execution.py:110）→ DockerSandbox 包 `timeout 120 /bin/bash -c …`（docker_sandbox.py:175）→ stdout/stderr 解码回传 → 截断 → `ls -1 /workspace/output`（executor.py:58-60）附产物清单 → 模型看到 `{status, stdout, stderr, generated_files}`。web_browse 链多一跳：参数转义 → 生成脚本文本 → write_file 进沙箱 → run_command 跑脚本 → stdout JSON 解包。file_read 链最短：_validate_path → sandbox.read_file（tar 归档往返，见第 2 篇）→ 截断。所有出口都收敛到 status 信封 + executor.truncate，模型视角完全一致。

## 设计决策

1. **隔离是"容器硬边界 + 工具软边界"的叠加**。容器层管资源与网络（docker_sandbox.py:108-110），工具层管路径白名单（file_ops.py:31）与注入转义——为什么 file_ops 还要白名单？容器有 root 权限（system_prompt.py:53-54 明示），file_write 若不加约束，模型（或被注入的指令）可以改容器内任意文件；白名单把爆炸半径压回 /workspace 工作区。
2. **代码生成式工具是"沙箱内扩展"的低成本模式**。browser 不往镜像里塞常驻服务、不在宿主装 Playwright，而是每次生成一次性脚本——浏览器进程的崩溃、泄漏天然被容器生命周期兜底。代价是每调用一次付一次解释器启动开销。
3. **转义双保险针对两种注入面**：selector 来自 LLM（可能被网页内容污染），URL 用 json.dumps、selector 用专用转义器（browser.py:41-43、79、84），即便注入也只是改 selector 语义，出不了容器。
4. **python 落盘执行换来可调试性**（execution.py:97 注释）并顺带获得 generated_files 反馈回路——agent 能"看见"自己产出了哪些文件，闭环多模态产出任务（图/文档）。
5. **工具分工靠描述负向约束三处同步**（宪法 system_prompt、shell 描述、python 描述），用 prompt 力学减少工具误用，而非硬路由。

## 新人提示

- 新增沙箱工具的模板：写 `async def xxx_(executor, …)` 业务函数 + `create_xxx_tool` 包装 + 在 tools/sandbox/__init__.py:61-67 的 dict 注册；记得 description 写清与相邻工具的边界。
- file_ops 的白名单只覆盖 file_read/file_write 两个工具；shell/python 可以绕过它直接 `cat /etc/passwd`（白名单不是安全边界，容器才是）——别误以为加了 ALLOWED_BASE_PATHS 就万事大吉。
- browser 脚本的 content 截断用的是 `executor.max_output_chars` 直接内插进生成代码（browser.py:120），所以调小 max_output_chars 对 browser 同样生效。
- 排查"python 工具输出为空"先想起 system_prompt.py:69 的 print() 规则——大概率是模型又忘了打印表达式值。
- 测试锚：test_tools_sandbox.py（422 行）用 mock_sandbox 逐工具验证信封格式与截断行为，是改动工具返回结构前必看的契约快照。
