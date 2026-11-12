# 06 · TaskBench：Back-Instruct 数据生成管线与图匹配评测

## 一、角色定位

TaskBench 子项目（`taskbench/`，arXiv:2311.18760）回答"任务自动化基准的数据怎么造、怎么评"两个问题。它用 Tool Graph 表示用户意图里的任务分解（节点=工具、边=资源/时序依赖），用 **Back-Instruct**（图→指令，反向于常规的指令→标注）靠 GPT-4 量产带金标任务图的样本，再用图匹配式指标评 LLM 的分解/调用/参数预测三能力。七个脚本分成生成链（`generate_graph.py`→`graph_sampler.py`→`data_engine.py`→`format_data.py`）与评测链（`inference.py`→`evaluate.py`→`batch_evaluate.sh`），三个域目录（`data_huggingface`/`data_multimedia`/`data_dailylifeapis`）各持五件套（tool_desc/graph_desc/data/user_requests/alignment_ids）。

## 二、内部结构

**生成链四步**：

1. `generate_graph.py`：工具图构建。resource 型（HF/多媒体域）按"工具 A 的 output-type 与工具 B 的 input-type 有交集即连边"全配对扫描（`taskbench/generate_graph.py:16-17`）；temporal 型（日常生活 API 域）所有工具对连 "complete" 边（`generate_graph.py:37-40`）——因为 API 无类型系统只能全连通。
2. `graph_sampler.py`：`GraphSampler`（`graph_sampler.py:8-9` 构造器）把 JSON 图载入 networkx DiGraph；`sample_subgraph`（`graph_sampler.py:39`）三种模式——single 取单节点、chain 双向生长成链（`graph_sampler.py:52-86`）、dag 按"已选节点随机挑邻居+输入类型过滤"长成有向无环图（`graph_sampler.py:88`）。
3. `data_engine.py`（354 行）：采样器抽子图后拼 prompt 让 GPT-4 反向生成 task_steps/user_request/invoking_graph（`taskbench/data_engine.py:237-256` 的七条要求），`check` 开启时追加"教师批改"字段（`data_engine.py:253-254` 拼入 check_by_teacher 段）；结构上 method_weights single:chain:dag=3:7:8（`data_engine.py:119-123`）、number_weights 工具数 2-10 加权（`data_engine.py:125-134`）；多 worker 双实现——asyncio.Semaphore（`data_engine.py:141-155`）或 ThreadPoolExecutor（`data_engine.py:184-215`）。生成后即时比对采样图与生成图是否对齐（`:331-352`）。
4. `format_data.py`：清洗断言关卡——参数引用改写为 `<node-j>` 标签（`taskbench/format_data.py:29-35`）、断言 nodes 与 task_steps 等长（`format_data.py:48`）、失败样本进 `data_error.json`（`format_data.py:63`），合格样本落 `data.json`+`user_requests.json`（`format_data.py:62-64`）。

**推理与评测**：`inference.py` click CLI 组装 prompt（resource/temporal 两套 schema，`taskbench/inference.py:175-187`），aiohttp+Semaphore 多 worker 打 OpenAI 兼容端点，断点=已推理 id 集（`:55-69`）；输出解析先截 "RESULT #:" 标记（`:235-237`）再切首尾花括号 json.loads（`:239-247`），失败可整段再发一次"重格式化"请求（`reformat`，`:249-293`，可换模型 reformat_by）。`evaluate.py` 的指标族：节点 F1（No Matching 直接集合法，`taskbench/evaluate.py:489-515`）、参数二元 F1（`:518-526`）、Levenshtein 序列编辑距离（`:528-536`）、边二元 F1（`:538-550`）、ROUGE/BERTScore（`:473-487`，cot 模式才开）；resource 域的金标边从 `<node-j>` 参数标签反推（`:361-376`）。

## 三、外部连接

生成链依赖 GPT-4 端点（`--api_addr/--api_port/--api_key`，`data_engine.py:47-49`）；推理链同样 OpenAI 兼容（`inference.py:43`）。三域实况（逐行解析）：huggingface 域 23 工具/225 边/7458 样本、multimedia 40/449/5555、dailylifeapis 40/1560/4318（dag 型最少：795/550/275）。`alignment_ids.json` 提供五档对齐子集（node/link/both/self-check/all，全对齐档仅 1741+3526+3189 内的更小交集），评测时 `--alignment` 选用（`evaluate.py:265-273`）。`batch_evaluate.sh:8-13` 按目录名自动切 dependency_type（dailylifeapis=temporal 其余=resource），对 predictions 目录下每个模型 json 逐个评（`:15-26`）。

## 四、数据流

一条样本的诞生：`sample()` 起手 `sampler.sample_subgraph(tool_number, method)` 抽出子图（`data_engine.py:233-236`），工具与边拼成文本（`data_engine.py:241-245`）+随机 seed（`data_engine.py:240`）防重复，GPT-4 返回的 JSON 经 ```json 围栏剥离（`data_engine.py:289-297`）解析，节点边各自排序后与采样图打包（`data_engine.py:310-316`）写 `data_raw.json`；`format_data.py` 把 `input` 字段改 `arguments`、工具名下划线换空格、参数引用换 `<node-j>`（`format_data.py:21-35`），断言全过才成正式样本。评测侧一条样本的旅程：prediction 的 task_nodes 与金标 task_nodes 并排（`evaluate.py:344-345`），节点名统一空格化（`:357-358`），参数展平成 `task-argname(-value)` 字符串（`:415-423`），边/参数/节点分别进 flatten 二元化（`:73-110`）后 sklearn prfs 出 P/R/F1，Levenshtein 用工具 id 序列算（`evaluate.py:529-535`，工具名→id 映射 `evaluate.py:213`）。

## 五、设计决策

1. **Back-Instruct 反向造数**：图先于指令，保证金标任务图天然对齐采样结构——规避"先有指令再标注"的标注歧义。教师批改字段（check_by_teacher）是 LLM-as-critic 的早期形态。
2. **resource/temporal 双依赖语义**：HF/多媒体工具有类型系统可用资源依赖（output-type 喂 input-type），日常生活 API 无类型只能时序全连通——一个基准两种依赖建模，评测与推理 prompt 全部双轨。
3. **重格式化二次调用**（`inference.py:249-293`）：JSON 解析失败让（可换的）模型重排格式再试——比静默丢样本多救回一截，比无限重试省钱。
4. **关键勘误——匈牙利匹配是死代码**：`evaluate.py:60-62` 的 `matching()` 与 `:55-58` 的 `compute_assignment_matrix`（内含 `linear_sum_assignment`，`:57`）全文件零调用；实际产出的所有 node 指标都是 `_no_matching` 后缀的直接集合 F1（`:499-515`）。论文叙事的"图匹配评测"在代码里未走通，metric 字典键名（`:506-511`）就是自证。
5. **两处实锤 bug**：`inference.py:161` 的 `results +=` 在默认参数下 NameError（`results` 仅当 `--log_first_detail` 真时于 `:154` 定义）——推理脚本首跑必崩；`evaluate.py:415-423` 变量交叉（预测侧追加进 `label_task_arg_name*`、金标侧进 `predcition_task_arg_name*`，`:518/:523` 互换喂 flatten），binary F1 靠对称性数值幸存但 P/R 语义镜像。
6. **README 口径差**：宣称 28271 样本，仓内 `data.json` 实数 17331 条（7458+5555+4318，逐行解析实证）——用此基准做实验时以盘上数据为准。

## 六、新人提示

复现实验三步：`inference.py --data_dir data_huggingface --api_addr <端点> --llm <模型> --log_first_detail true`（**必须带这个参数**，否则踩 `:161` 的 NameError）→ `evaluate.py --data_dir data_huggingface --prediction_dir predictions --llm <模型> -m all` → 或直接 `bash batch_evaluate.sh data_huggingface predictions` 批量。读代码顺序：先 `data_engine.py:233-260` 的 sample() 拿到"一条样本怎么造"，再 `evaluate.py:344-434` 的解析段看"预测怎么变成指标"。改指标注意 flatten 的二元化语义（并集做槽位、缺失记 0，`:79-109`）——多算/漏算一个工具名会同时动 P 和 R。想画工具图自查用 `visualize_graph.py`（36 行，spring_layout 出 PDF）。
