# 05 · EasyTool：精简工具指令生产与四基准执行器

## 一、角色定位

EasyTool 子项目（`easytool/`）是同名论文（arXiv:2401.06201）的代码侧：核心主张"把冗长 API 文档清洗成精简指令（tool instruction）能提升 LLM 工具调用效果"。它由两半组成——离线的**指令生产**（`easytool/data_process.py` 下载 FuncQA/RestBench/ToolBench 原始数据并清洗，产物如 `data_toolbench/tool_instruction/toolbench_tool_instruction.json`）与在线的**四基准执行器**（`easytool/easytool/` 包，用精简指令驱动 LLM 完成"分解→选工具→选参数→调用→生成答案"全流程并落盘评测）。入口 `easytool/main.py:11-90` 是纯 argparse 调度——`__main__` 块即全部逻辑、无函数封装（NOTES-DIGEST 甄别），key 直接 `os.environ["OPENAI_API_KEY"]`（`easytool/main.py:9`）。

## 二、内部结构

**util.py 共享底座**（`easytool/easytool/util.py`）：JSON/JSONL 读写（`:7-25`）、递归删键（`:28-37`）、`build_index` 遍历 `.toolenv/tools/` 目录建类别→API 文件索引（`:52-59`，ToolBench 执行器定位工具文档用）、`change_name` 处理 Python 保留字参数名（`:62-66`，`from/class/id` 等加 `is_` 前缀）、`standardize` 正则清洗 API 名（`:69-89`）、进度文件断点续跑对（`:92-105`）。

**funcQA.py 的 FuncQA 执行器**（675 行）：单跳 `task_execution_oh`（`:605`）= 单步 `retrieval`+`answer_generation`；多跳 `task_execution_mh`（`:514`）= `task_decompose`（`:89`，问题拆子任务）→`task_topology`（`:129`，子任务组 DAG、dep 规整成 int 列表 `:154-168`）→ 逐任务 `retrieval`（`:323`：`choose_tool` 选工具→`choose_parameter`/`choose_parameter_depend` 选参数→`Call_function` 真调）→`answer_generation`/`answer_generation_depend`（`:398`/`:433`）→`answer_summarize`（`:474`）→`answer_check`（`:491`）。失败重试是"换工具"式：`tool_used` 名单排除已失败工具再选（`:570-575`），最多 `retrieval_num`（默认 5）轮（`:540`）。

**Call_function 的动态执行**（`funcQA.py:281-320`）：`importlib.util.spec_from_file_location` 从 `data_funcqa/funchub/math.py` 动态加载模块（`:283-285`），`getattr` 取函数执行（`:287-289`），失败时两层参数名修补重试（`:293-300`），仍失败写 `wrong_log.json`（`:304-310`）。math.py 的 16 个函数全带 `_` 尾巴避开内建（`easytool/data_funcqa/funchub/math.py`，`grep -c '^def'` 实证 16），文件头 `import math` 是标准库引用——图谱阶段曾误建自引用假边（NOTES-DIGEST 甄别，已剔除）。

**toolbench.py / toolbench_retrieve.py 的 90% 同构**：`easytool/easytool/toolbench_retrieve.py` 相对 `toolbench.py` 的 diff 仅三处——新增 `get_embedding`（`:45-51`，`openai.Embedding.create(engine="text-embedding-ada-002")`）与 `retrieve_reference`（`:53-60`，cosine 相似度 top-k）两函数；`task_execution` 开头多加载 `API_description_embeddings.pkl`（`:636-637`）；选工具前用嵌入检索召回 5 个相关工具替代全量 Tool_dic（`:668-669`）。其余 700 行（choose_API/choose_parameter/Call_function 真发 HTTP 调 RapidAPI/依赖感知生成等）逐行复制。**restbench.py**（111 行）是 TMDB 电影库单工具特化版。

## 三、外部连接

`easytool/data_process.py:7-10` 的 urls 字典是数据来源清单：FuncQA 与 ToolBench 走 Google Drive（gdown），RestBench 直接拉 RestGPT 仓的 tmdb.json。执行器对外的唯一网络依赖是 OpenAI API（`funcQA.py:26`）与 ToolBench 真调用时的 RapidAPI endpoints。三个 `data_*/tool_instruction/` 目录是"精简指令"资产的实物：`data_funcqa/tool_instruction/functions_data.json`（函数说明）+`tool_dic.jsonl`（问题类型→函数映射）；`data_toolbench/tool_instruction/API_description_embeddings.zip` 是嵌入预计算产物（解压后即 `:636` 加载的 pkl）。产出侧：每基准一个 `*_easytool.jsonl` 结果文件（`funcQA.py:581`、`toolbench_retrieve.py:716`）与进度文件（`easytool/main.py:25/:36/:45` 按任务命名）。

## 四、数据流

FuncQA 多跳一题的完整走读（`funcQA.py:514-602`）：问题"23 km/h 转 km/min 再乘 45 分钟"→`task_decompose` 产出 `["Convert 23 km/h to X by 'divide_'", "Multiply X by 45 by 'multiply_'"]`→`task_topology` 给两任务挂 id/dep→任务 1 无依赖走 `choose_parameter`（无 previous_log 版 `:195`），`Call_function('divide_', {'input': [...]})` 真执行得 X→写入 `task_depend`（`:577`）→任务 2 依赖 1 走 `choose_parameter_depend`（`:237`，prompt 里带前序日志）拿参数、`answer_generation_depend` 生成中间答案→`answer_summarize` 汇总→`answer_check` JSON 判定 YES/NO→整题连同 `execute_log`（api/call/tool_instruction 四列表）追加进结果 jsonl（`:581-598`）→`update_progress` 写进度（`:601`）。中途任何 LLM 输出解析失败都进各自的 `while True` 重试（`ind>10` 弃，见 `:82/:122/:173` 等十处）。

## 五、设计决策

1. **"精简指令"落在数据文件而非代码**：执行器代码完全通用，基准差异全在 tool_instruction 数据——论文学主张与工程实现的干净分离。
2. **检索版与全量版分叉维护**：toolbench_retrieve 用嵌入检索应对 RapidAPI 海量工具池（LLM 上下文装不下），funcqa 只有 16 个函数无需检索——但实现方式是整文件复制而非参数化，90% 同构是复制粘贴式变体（NOTES-DIGEST 甄别；diff 实证差异仅 `toolbench_retrieve.py:45-60` 与 `:668-669`）。改一处 bug 必须记得同步两文件。
3. **`depend_id = [1]` 硬编码**（`funcQA.py:539` 与 `:623`）：循环内从未更新，首个无依赖子任务也恒走"带依赖"分支——靠 `task_depend` 里预置的 Original Question 兜底不崩，但多消耗 previous_log token。
4. **失败重试=换工具**：`tool_used` 排除法（`:570-575`）把"参数选错"与"工具选错"混为一谈——参数问题换工具也救不回来，属可改进点。
5. **eval 风险与 true/false 手术**：全模块十处 `eval(result...)` 直执 LLM 原文，`choose_parameter` 还要做 JSON→Python 字面量替换（`:223-224`）；`answer_check`（`:508`）是全文件唯一无重试的裸 eval。

## 六、新人提示

跑法：`export OPENAI_API_KEY=sk-...` 后 `python main.py --task funcqa --data_type funcqa_mh`（`easytool/main.py:13-17` 的参数面）；断点续跑靠同名进度文件，重跑前删掉即可从头来。读代码顺序：`util.py`→`funcQA.py`（注释最全）→按 diff 读 `toolbench_retrieve.py`。三个坑：`.toolenv/tools/` 工具文档树需要另行准备（`--tool_root_dir`，`:16`）；`openai==0.27.8` 旧 API（`easytool/requirements.txt:1`）；结果文件名内嵌模型名（`:581`），换模型重跑不会覆盖旧结果。想复用"精简指令"思想到自己的 agent：看 `data_process.py:28+` 的 toolbench_process 怎么把原始 API JSON 压成标准四字段，那是论文方法的实体。
