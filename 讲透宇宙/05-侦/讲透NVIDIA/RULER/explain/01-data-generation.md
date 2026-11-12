# 01 · scripts/data — 造数流水线：五任务生成器与公平性机制

> 源码：`scripts/data/prepare.py`（165 行）+ `synthetic/` 五生成器 + `tokenizer.py`/`template.py`/`synthetic/constants.py` · 图谱定位：4 层第 2/3 层「数据生成流水线层 + 五任务生成器与语料资产层」· constants.py fanIn=6（生成端/预测端/评测端共同消费）

## 一、角色定位：三步流水线的第一步，也是基准的灵魂

RULER 的立论是"合成任务可控"——长度可控（按 token 精确填满）、难度可控（参数旋钮）、任务可控（五族覆盖检索/聚合/理解三类能力）。这一切都由 data/ 目录兑现：prepare.py 是调度器，synthetic/ 下五个生成器是智力内核，tokenizer.py 与 template.py 是两个公平性机制，constants.py 是生成与评测共享的口径注册表。没有这一层，后两步（预测/评测）只是普通的推理脚手架。

## 二、内部结构：动态加载的调度器 + 五个同构生成器

**prepare.py 的解耦设计**：`importlib.import_module(f"{args.benchmark}.constants")` 按任务名动态取常量（scripts/data/prepare.py:72），生成器同理按 `{task}` 名加载——新增任务零侵入流水线。模板套壳：断言 model_template_type 必须在 Templates 里（prepare.py:87），取 `Templates[args.model_template_type]`（:88），非法则回落 `Templates['base']`（:94）。

**五个生成器同构三层**：`main()`（生成+write_manifest 登记清单）→ `generate_samples()`（批量循环+tokenizer 长度对齐）→ `generate_input_output()`（单条样本构造）。差异全在第三层：

- **NIAH**（scripts/data/synthetic/niah.py）：`generate_random` 按 type_needle 分发数字/单词/UUID 值生成器（niah.py:120-128）；`generate_input_output` 按 haystack（essay/words/repeat/uuid）×needle 组合埋键值对（niah.py:130-206）；`generate_samples` 对齐 max_seq_length 落盘（niah.py:209-294）。八变体（single_1/2/3、multikey_1/2/3、multivalue、multiquery）由 scripts/synthetic.yaml:15-85 参数化。
- **VT**（variable_tracking.py）：`generate_chains` 造 num_chains 条赋值链（variable_tracking.py:93-114），`shuffle_sublists_heap` 堆打散乱序（:116-128），`generate_input_output` 混噪声赋值（:130-177）——多跳聚合考题。
- **CWE**（common_words_extraction.py）：`get_example` 从 wonderwords 词表抽词（common_words_extraction.py:85-98），高频 10 词混入随机词（:100-129），`sys_word_pair_random` 主循环（:131-203）。
- **FWE**（freq_words_extraction.py）：scipy zeta Zipf 采样编码词（freq_words_extraction.py:74-107、:109-155）。
- **QA**（qa.py）：`read_squad`/`read_hotpotqa` 解析两数据集（qa.py:73-94、:97-113），相似/随机双策略干扰文档池拼长文（:153-223）。

**注册表**（scripts/data/synthetic/constants.py:24 的 TASKS 字典）：每任务 tokens_to_generate（niah 128 :26、vt 30 :32、cwe 120 :38、fwe 50 :44）与 answer_prefix（:28/:34/:40/:46）——answer_prefix 是答案切分口径，评测端必须同源。

## 三、外部连接：谁消费它、它依赖谁

上游：scripts/run.sh:98 在每档 SEQ_LENGTHS 循环里调 prepare.py；scripts/synthetic.yaml 提供任务参数矩阵；scripts/config_tasks.sh:32 的 synthetic 数组给定 13 个任务变体清单（NUM_SAMPLES=500 见 config_tasks.sh:15）。下游：预测端 call_api.py 经 `importlib.import_module(f"data.{args.benchmark}.constants")` 读**同一份** TASKS（scripts/pred/call_api.py:209）——生成与推理模板一致性由"同一文件"而非"复制粘贴"保证。语料资产四件套被生成器消费：PaulGrahamEssays_URLs.txt（217 篇索引）→ download_paulgraham_essay.py 抓取转文本；download_qa_dataset.sh 拉 SQuAD/HotpotQA；english_words.json（LFS 指针，size 8564991）供词堆任务。

## 四、数据流：一条 NIAH 样本的诞生

run.sh 把当前长度档传给 prepare.py → 任务名 niah_single_2 经 importlib 找到 synthetic.yaml:25 的参数（haystack=words、needle=uuids…）→ generate_samples 循环：generate_input_output 先按 haystack 类型铺干草堆，generate_random 造 needle 值（niah.py:120-128），插入键值对 → tokenizer 反复计数补齐/裁剪到 max_seq_length → 从 constants.py TASKS 取 prompt 模板与 answer_prefix（scripts/data/synthetic/constants.py:26-28）→ prepare.py 套 Templates['meta-llama3'] 外壳（prepare.py:88）→ 写 jsonl + write_manifest。预测端与评测端各按 manifest 找到这份文件。关键不变量：**上下文长度是目标模型真实 token 数**（下一节 tokenizer）而非字符数——这是全部"4K/8K/131K 档位"可比的地基。

## 五、设计决策：三个值得偷师的机制

1. **importlib 注册表模式**：prepare.py:72 与 call_api.py:209 都按名字动态加载——任务矩阵扩展（synthetic.yaml 加键+config_tasks.sh 数组追加）对流水线零改动；代价是静态分析工具（含知识图谱 scanner）看不见这些边，必须按源码手补。
2. **同一份 constants 双端消费**：answer_prefix 若在生成端与评测端各写一份，切分口径漂移即分数不可比——RULER 用文件级单源消灭这个隐患。
3. **12 种→11 种模板的现实**：templates 是配置不是代码（scripts/data/template.py:16-36 实数 11 种：base/meta-chat/vicuna-chat/lwm-chat/command-r-chat/chatglm-chat/RWKV/Phi3/meta-llama3/jamba/nemotron5-instruct），加新模型外壳只改一个字典项；图谱层摘要写"12 种"是错的，以源码计数为准。

## 六、新人提示

- 跑不起来先查 LFS：`git lfs pull` 拉回 english_words.json 本体（.gitattributes:1-3 把全部 json 划走）。
- 调试单个任务不必跑全管线：`python data/prepare.py --benchmark synthetic --task niah_single_1 ...` 直接出 jsonl。
- 想自造任务：抄 variable_tracking.py 的三层结构（最短约 230 行），answer_prefix 接入 constants.py TASKS，评测端在 scripts/eval/synthetic/constants.py:35-47 的 TASK_METRICS 里映射到 string_match_part（:24）或 string_match_all（:28）。
- 改长度档位在 scripts/config_models.sh:18-25（131072 递降到 4096），不在生成器里——生成器只认 max_seq_length 参数。
- 验证练习：把 NUM_SAMPLES 降到 4（config_tasks.sh:15）、SEQ_LENGTHS 只留 4096 一档，跑通一次 prepare→call_api→evaluate 全链，你会对"三步流水线"有肌肉记忆。
