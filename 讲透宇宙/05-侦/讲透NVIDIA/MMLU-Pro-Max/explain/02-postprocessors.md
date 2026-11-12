# 02 · postprocessors.py —— 三路答案抽取器

## 角色定位

`postprocessors.py`（81 行）是推理结果的"最后一公里"：模型对着 manifest 生成的原文装在 JSONL 的 generation 字段里（README:21 约定），本模块三个子类从自由文本抽出结构化答案写入 extracted_answer 列，对应三种评测形态——判断题（Binary）、选择题（MCQ）、开放生成（Gen），与 MMLUProMax.py 的扰动族一一配对。

## 内部结构

**基类 Postprocessor**（postprocessors.py:1-17）：构造时确定两个列名——输入 generation_key 默认 "generation"、输出 answer_key 默认 "extracted_answer"（postprocessors.py:8-14）；`process()` 恒等返回（postprocessors.py:16-17）由子类覆写。与 MMLUProMax.py 的 ABC 同款风格：靠约定而非 abc.ABC 强制。

**BinaryPostprocessor**（postprocessors.py:20-37）：按行切开、滤空行、取**最后一行**（postprocessors.py:23-25）——判定句总在推理末尾；对末行按 "the answer is" 切割取尾段（postprocessors.py:25），没切动（split 结果列表长度为 1）再退回 "the answer provided is"（postprocessors.py:26-27）——双话术兜底；仍空返回 "unparsed" 哨兵（postprocessors.py:28-29）；最后取首词只留字母（postprocessors.py:30）——"correct."/"Correct" 都归一为 "correct"。

**MCQPostprocessor**（postprocessors.py:40-66）：三个分割串按序尝试 "the answer is"/"the best answer is"/"the final answer is"（postprocessors.py:45）；命中后取尾段、清洗噪声字符（postprocessors.py:49-50）；恰好单字符且在 A-K 内则大写返回（postprocessors.py:51-53），越界打印 "101"（postprocessors.py:54-55）、空串打印 "102"（postprocessors.py:57-59）；**全不命中时返回整个 generation 原文**（postprocessors.py:60）——没有 "unparsed" 哨兵，脏数据直接混进结果列。

**GenPostprocessor**（postprocessors.py:69-81）：按 `boxed{` 切割取尾段（postprocessors.py:72），以 `}$` 结尾则剥掉（postprocessors.py:73-74）——对应模板要求的 `'The answer is: $\boxed{answer}$'` 输出格式；无 boxed 时同样回退全文。

三个子类共享防覆盖断言：extracted_answer 列已存在即抛 ValueError（postprocessors.py:33-34/:62-63/:77-78），统一 apply 落列（postprocessors.py:36/:65/:80）。

## 外部连接

输入契约：DataFrame 含 generation 列（NeMo-Skills `ns generate` 输出即满足）。输出契约：追加 extracted_answer 列——MCQ/Binary 变体与 manifest 的 answer/always_same_option/binary_answer 列对比算准确率；Gen 变体把 extracted_answer 喂给 config/judge.yaml 的裁判模板（judge.yaml:9-10 占位）做 LLM 等价判定。抽取规则与 MMLUProMax.py 的模板话术**成对演化**：改模板必须同步改分割串。

## 数据流

逐行纯函数映射：generation 原文 → split 过滤 → 分割串定位 → 字符清洗 → 归一化 → extracted_answer。无状态、无 IO、无随机性；三个子类差异只在"定位话术"与"归一化规则"。DataFrame 级语义是列追加+防覆盖。

## 设计决策

- **哨兵 vs 静默全文的双标**：Binary 有 "unparsed"（postprocessors.py:29）而 MCQ/Gen 静默回退原文（postprocessors.py:60/:72）——同一文件两种失败哲学并存，统计准确率前应对 extracted_answer 做长度/词表过滤兜底。
- **末行优先**（postprocessors.py:23-25）隐含"CoT 后置结论"假设；配合模板收尾指令自洽，但对把结论写开头的模型会切错。
- **101/102 打印错误码**（postprocessors.py:54/:58）而非计数聚合：长跑刷屏且不进结果文件。
- **防覆盖断言**把幂等性交给调用方：重复 process 同一 DataFrame 必炸，重放需先 drop 该列。

## 新人提示

接入顺序：跑完推理 → 选对子类（对应表看 MMLUProMax.py 各 PROMPT_KEY）→ process(df) → MCQ/Binary 直接 groupby 算分、Gen 走裁判。验证抽取质量最快办法：抽 20 行人眼比对 extracted_answer 与 generation 尾部，重点盯 "the answer is" 不命中的样本（它们整段进了结果列）。扩新输出话术改 postprocessors.py:45 的 splitStrings，但须同步确认模板收尾指令。

——锚核对于 2026-11-08，commit dd20018b。
