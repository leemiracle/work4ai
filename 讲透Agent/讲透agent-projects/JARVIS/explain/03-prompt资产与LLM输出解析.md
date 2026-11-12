# 03 · prompt 资产与 LLM 输出解析：从三段模板到 eval 重试

## 一、角色定位

JARVIS 没有任何结构化输出机制（2023 年 JSON mode/function calling 尚不存在），三段决策全靠"prompt 资产 + 约束解码 + 解析容错"三板斧。资产侧的主角是 `hugginggpt/server/configs/config.default.yaml` 的 prompt 三元组与 `hugginggpt/server/demos/` 三份 few-shot；解析侧的主角是 `awesome_chat.py` 的 `find_json`/`field_extract` 与 `hugginggpt/server/get_token_ids.py` 的约束解码支撑。姊妹项目 EasyTool 则展示了同一时代另一所学校的做法——`while True + eval()` 异常驱动重试。把两套放一起读，能完整理解"前 JSON mode 时代"agent 如何与 LLM 输出搏斗。

## 二、内部结构

**HuggingGPT 的 prompt 三元组**，每阶段三件（`awesome_chat.py:133-143` 装配）：

1. **tprompt**（系统提示，`config.default.yaml:30-36`）：定义角色与输出契约。parse_task 版（`:32`）规定任务 JSON schema、`args` 仅允许 text/image/audio 三键、34 种任务类型枚举、`<GENERATED>-dep_id` 占位写法、"解析不了就回 `[]`"的逃生门；choose_model 版（`:34`）要求聚焦模型描述并偏好本地端点；response_results 版（`:36`）要求先直接答再复述工作流。
2. **prompt**（用户模板，`config.default.yaml:41-46`）：`replace_slot`（`awesome_chat.py:215`）做 `{{key}}` 占位替换——注意值里的引号换成单引号、换行删光（`:219`），防 JSON 注入式断裂。
3. **demos**（few-shot，`demos/demo_parse_task.json` 4269 字节/`demo_choose_model.json` 142/`demo_response_results.json` 316）：直接 `json.loads` 成 messages 数组拼在前面（`awesome_chat.py:319-320`）。

**约束解码**：`get_token_ids.py:43-47` 把 34 个任务名+字段名关键词编码成 token id 集合，`get_token_ids_for_choose_model`（`:49-53`）只编码 `{"id": "reason"}` 结构词；`awesome_chat.py:343/:369` 分别以偏置 0.1/5 挂进 `logit_bias`。编码器映射表（`:3-18`）硬编码 14 个模型名到 cl100k/p50k/r50k 三种编码，上下文长度表（`:20-35`）同款——加新模型必须两表同补。

**解析容错三层**：`json.loads` 直解→`find_json`（`awesome_chat.py:222-228`，单引号全换双引号、首 `{` 到尾 `}` 硬切、去换行）→`field_extract`（`:230-237`，双正则兜底抽 id/reason）。EasyTool 的对应物是每个 LLM 函数一只 `while True`：如 `easytool/easytool/funcQA.py:71-85`（choose_tool）、`:114-125`（task_decompose）、`:218-233`（choose_parameter）、`:262-277`（choose_parameter_depend），循环体 `eval(result...)` 吃异常，`ind > 10` 放弃返 -1——靠异常驱动重试而非结构化输出（NOTES-DIGEST 甄别第一条）。

## 三、外部连接

tprompt 的任务枚举（`config.default.yaml:32`）与 `get_token_ids.py:44` 的关键词文本必须一字不差地同步——加任务类型漏改后者，logit_bias 就不再压制非法输出，parse_task 的可解析率会悄悄劣化。demos 文件路径本身也写在配置里（`config.default.yaml:37-40`），换 demo 零代码。EasyTool 的 prompt 全部内嵌在函数体字符串（如 `funcQA.py:50-61` 的 choose_tool 模板），LangChain `ChatPromptTemplate` 变量注入（`:63`），两项目风格迥异但同属"prompt 即代码"。

## 四、数据流

parse_task 一次调用的组装：demo messages + system(tprompt) + user(prompt)（`awesome_chat.py:319-330`）；上下文超限时从对话头开始每次丢 2 条消息（一轮 user+assistant）重算 token（`:323-336`），直到 `get_max_context_length - count_tokens > 800`——避免请求被 4096 截断。`count_tokens` 用 tiktoken 精确计数（`get_token_ids.py:37-38`）。EasyTool 的 choose_parameter 多一道"Python 化"预处理：把 `: true/:true` 替换成 `: True` 再 eval（`funcQA.py:223-224`）——因为 eval 只认 Python 字面量不认 JSON 的 true/false，这暴露了 eval 路线的根本别扭：LLM 输出的是 JSON，解析器要的是 Python 表达式，中间全靠字符串手术弥合。

## 五、设计决策

1. **prompt 即配置**：三段提示词直接以 YAML 多行字符串内嵌，改 prompt 即改配置零代码（NOTES-DIGEST 甄别）。代价：`config.default.yaml:46` 尾部那个孤立 `}` 是多行字符串 artifact，会被原样拼进 prompt（gradio 配置同款）——无害但说明无 lint。
2. **偏置值不对称**：parse_task 用 0.1（34 个任务词轻推方向）而 choose_model 用 5（强压输出只能是 `{"id","reason"}` 结构）——按输出空间大小反向配力度。
3. **`eval` 的安全性**：EasyTool 对 LLM 原文直接 `eval()`（`funcQA.py:75/:117/:153` 等）——LLM 输出若含恶意表达式即任意代码执行。2023 年基准脚本普遍如此，复用前必须换成 `json.loads` 或 `ast.literal_eval`。
4. **`answer_check` 的裸 eval 无重试**（`funcQA.py:508`）：`eval(result)["Choice"]` 不包 while——同文件里唯一无重试的 LLM 调用，解析失败即抛异常终止该样本，属于疏漏而非设计。
5. **重试上限分层**：选工具/分解/拓扑/参数 10 次（`funcQA.py:82` 等），answer_generation 仅 2 次（`:426`）——按"失败容忍度"配额，生成类任务重试意义小。

## 六、新人提示

研究这套 prompt 的最短路径：并排打开 `config.default.yaml:30-46` 与三份 demo JSON，对照 `awesome_chat.py:317-398` 三个函数看拼装顺序；再打开 `logs/debug.log`（`config.default.yaml:12`）看真实发出的完整 messages。想体验"约束解码失效"的对照实验：把 `logit_bias.parse_task` 改 0 重跑，数 `logs/log_fail.jsonl` 里 "task parsing fail" 的占比变化。复用 EasyTool 代码时三件事必做：eval→literal_eval、`openai.api_key = os.environ["OPENAI_API_KEY"]`（`easytool/main.py:9`，环境变量缺失时 KeyError 即崩的硬依赖）改为温和报错、`langchain 0.0.260` 的 LLMChain 迁到新 API。两套解析体系对照读的价值在于：HuggingGPT 用三层降级把解析失败概率压到可接受，EasyTool 用重试次数硬扛——前者适合在线服务，后者适合离线刷榜。
