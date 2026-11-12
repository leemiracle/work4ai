# RULER 新人上手文档（ONBOARDING）

> 基于知识图谱（88 节点 / 166 边 / 4 层 / 6 步导览，commit `c3f5e3b4`，fingerprints 29 文件基线）生成，全部行号锚经源码逐行核实。
> 仓库：`/usr-data/data2/repos/agent-repos/NVIDIA/RULER`（NVIDIA/RULER，"What is the Real Context Size of Your Long-Context Language Models?" 评测基准）

## 1. 项目定位与一句话理解

**一句话**：RULER 是 NVIDIA 的长上下文 LLM 合成基准——不信任何模型的"标称上下文长度"，而是用**可控长度、可控难度的合成任务**（4K 到 131K token 逐档加压）实测每个模型真实的有效上下文窗口，产出"长度×任务×模型"的能力曲线。

方法论上它与传统基准的根本区别：不做固定语料考试，而是**生成器造数据**——五族任务（NIAH 大海捞针/VT 变量跟踪/CWE 常词提取/FWE 频词提取/QA 问答阅读理解）各自有参数化生成器，按目标序列长度精确填满上下文（用目标模型自己的分词器计数对齐），难度可由 haystack 类型、needle 数量、链跳数等旋钮调节。三步流水线贯穿全仓：**生成数据（data/prepare.py）→ 请求预测（pred/call_api.py）→ 评测（eval/evaluate.py）**，由 scripts/run.sh 总编排。

对新人最有用的心智模型：这是个"控制面 shell + 数据面 Python"的双层结构——控制面两份 config（config_models.sh 定模型与长度阶梯、config_tasks.sh 定任务清单）全部以**环境变量**驱动；数据面按任务名动态加载生成器，与流水线零耦合。

## 2. 五分钟上手

```bash
# Docker 环境（nvcr pytorch:23.10-py3 基座，见 docker/Dockerfile:15）
cd docker && docker build -t ruler .

# 三步流水线全流程（容器内）
cd scripts
bash run.sh <model_name> <model_dir> <engine_dir> <data_dir>   # 总编排
```

run.sh 干四件事（scripts/run.sh:34-132）：source config_models.sh（run.sh:34）→ 把 MODEL_SELECT 输出的冒号串用 `IFS=":" read` 解包成 MODEL_PATH/MODEL_TEMPLATE_TYPE/MODEL_FRAMEWORK/TOKENIZER 等 10 个变量（run.sh:37）→ source config_tasks.sh（run.sh:52）→ 按 MODEL_FRAMEWORK 三分支拉推理服务：vllm 起 `pred/serve_vllm.py`（run.sh:62-63）、trtllm 起 `pred/serve_trt.py`（run.sh:70-71）、sglang 直接 `python -m sglang.launch_server`（run.sh:75-76）——**三引擎对齐三家推理栈**。然后对 SEQ_LENGTHS 每档长度循环造数（`python data/prepare.py`（run.sh:98））→ 预测（`python pred/call_api.py --server_type ${MODEL_FRAMEWORK}` run.sh:110/:115）→ 评测（`python eval/evaluate.py`（run.sh:127）），最后打印 call_api 总耗时（run.sh:132，吞吐也是被测对象）。

第一道坎是数据：**.gitattributes 把 *.jsonl/*.jsonls/*.json 全部走 Git LFS**（.gitattributes:1-3）——克隆后 scripts/data/synthetic/json/english_words.json 只是 3 行指针（oid sha256:affcd6d4...、size 8564991），词堆类 NIAH/CWE 任务的 8.5MB 词表本体要 `git lfs pull` 才有；README 没提醒这一点，是"克隆后跑不起来"的第一嫌疑人。

## 3. 架构总览（按 4 层图谱）

**L01 基准编排与运行环境层**（8 文件）：run.sh 总编排；config_models.sh 定采样与长度——`TEMPERATURE="0.0" # greedy`（config_models.sh:15）、TOP_K=32（config_models.sh:17）、SEQ_LENGTHS 从 131072 降到 4096 六档（config_models.sh:18-25）、MODEL_SELECT 按 case 输出配置串（config_models.sh:27 起，llama2-7b-chat config_models.sh:33-37、llama3.1-8b-chat config_models.sh:38-42、jamba1.5-mini config_models.sh:43-45）；config_tasks.sh 的 `NUM_SAMPLES=500`（config_tasks.sh:15）与 synthetic 数组（config_tasks.sh:32）；synthetic.yaml 是 13 键任务矩阵（niah_single_1 synthetic.yaml:15 … niah_multiquery synthetic.yaml:85、vt synthetic.yaml:95、cwe synthetic.yaml:102、fwe synthetic.yaml:109、qa_1 synthetic.yaml:114、qa_2 synthetic.yaml:119）；Dockerfile 与 requirements.txt（pin vllm==0.5.4/transformers==4.44.2）。

**L02 数据生成流水线层**（5 文件）：prepare.py 用 `importlib.import_module(f"{args.benchmark}.constants")` 动态取任务常量（scripts/data/prepare.py:72）、模板经 Templates 套壳（scripts/data/prepare.py:87-88，非法类型回落 'base' scripts/data/prepare.py:94）；tokenizer.py 的 select_tokenizer 工厂（scripts/data/tokenizer.py:26）分发五个实现类（NeMoSentencePiece scripts/data/tokenizer.py:41、NeMoTikToken scripts/data/tokenizer.py:57、HF scripts/data/tokenizer.py:74、OpenAI scripts/data/tokenizer.py:91、Gemini scripts/data/tokenizer.py:108）；template.py 的 Templates 字典；synthetic/constants.py 的 TASKS 注册表；manifest_utils.py 的 write_manifest。

**L03 五任务生成器与语料资产层**（9 文件）：niah.py / variable_tracking.py / common_words_extraction.py / freq_words_extraction.py / qa.py 五个生成器 + 语料四件套（PaulGrahamEssays_URLs.txt 索引 217 篇文章、download_paulgraham_essay.py 抓取转纯文本、download_qa_dataset.sh 拉 SQuAD/HotpotQA、english_words.json 词表）。

**L04 预测服务与评测层**（7 文件）：call_api.py / client_wrappers.py / model_wrappers.py（本地 HuggingFace call_api.py:170、Mamba call_api.py:183 延迟导入）+ 双服务脚本 serve_vllm.py（FastAPI+AsyncLLMEngine /generate）与 serve_trt.py（mpi4py 多进程 + Flask）+ evaluate.py 与 eval/synthetic/constants.py 指标库。

依赖方向：L01 驱动 L02→L03 造数、L04 预测评测；constants.py 被生成端与预测端（call_api.py:209 动态加载同一份）共同消费——模板一致性靠"同一文件"保证。

## 4. 深潜一：五任务生成器——基准的智力内核

五个生成器五种考法（均含 `main() → generate_samples → generate_input_output` 三层结构与 write_manifest 收尾）：

- **NIAH 大海捞针**（niah.py）：在 Paul Graham 文章/英文单词/UUID/数字干草堆中埋键值对 needle。`generate_random` 按 type_needle 分发数字/单词/UUID 三种值生成器（niah.py:120-128），`generate_input_output` 按 haystack×needle 组合构造上下文（niah.py:130-206），`generate_samples` 批量循环并用 tokenizer 对齐 max_seq_length（niah.py:209-294）。八变体由 synthetic.yaml 参数化：haystack 类型 × needle 类型 × key/value/query 数量（niah_single_1/2/3、multikey_1/2/3、multivalue、multiquery，synthetic.yaml:15-85）。
- **VT 变量跟踪**（variable_tracking.py）：`generate_chains` 生成 num_chains 条赋值链（variable_tracking.py:93-114）、`shuffle_sublists_heap` 用堆打散乱序（variable_tracking.py:116-128）、`generate_input_output` 混入噪声赋值（variable_tracking.py:130-177）——考多跳聚合：找出链上所有等于目标值的变量。
- **CWE 常词提取**（common_words_extraction.py）：`get_example` 从 wonderwords 词表抽词（common_words_extraction.py:85-98）、`generate_input_output` 把 10 个高频词混入随机词填满长度（common_words_extraction.py:100-129）、`sys_word_pair_random` 主循环（common_words_extraction.py:131-203）——考统计聚合。
- **FWE 频词提取**（freq_words_extraction.py）：Zipf 分布（scipy zeta）采样编码词（`generate_input_output` freq_words_extraction.py:74-107、`sys_kwext` freq_words_extraction.py:109-155）——CWE 的无序变体，考无序频率感知。
- **QA 问答**（qa.py）：`read_squad`/`read_hotpotqa` 解析两个数据集（qa.py:73-94/qa.py:97-113）、`generate_samples` 为每个问题构造相似/随机两种干扰文档池拼超长上下文（qa.py:153-223）——考长文阅读理解而非检索。

任务注册表在 synthetic/constants.py 的 TASKS 字典（scripts/data/synthetic/constants.py:24）：每任务一个 prompt 模板（{context}/{query} 槽位）、tokens_to_generate（niah 128 scripts/data/synthetic/constants.py:26、vt 30 scripts/data/synthetic/constants.py:32、cwe 120 scripts/data/synthetic/constants.py:38、fwe 50 scripts/data/synthetic/constants.py:44）与 answer_prefix（scripts/data/synthetic/constants.py:28/scripts/data/synthetic/constants.py:34/scripts/data/synthetic/constants.py:40/scripts/data/synthetic/constants.py:46）——answer_prefix 是评测切分答案的口径约定，生成与评测必须同源。

## 5. 深潜二：预测侧——五家 Client、延迟 import 与三引擎

**call_api.py 的分发核心 get_llm 按 server_type 分支延迟导入**——七处 `from client_wrappers import ...` / `from model_wrappers import ...` 全在函数体内（call_api.py:100/call_api.py:116/call_api.py:131/call_api.py:146/call_api.py:158 TRTLLM/VLLM/SGL/OpenAI/Gemini 五家 + call_api.py:170/call_api.py:183 本地 HuggingFace/Mamba）：本地模块延迟导入使任意后端组合可并存且启动零负担；此外预测端读生成端同一份常量也走 importlib（`import_module(f"data.{args.benchmark}.constants")` call_api.py:209）。多线程+进度条批量请求落盘预测 jsonl 并计吞吐（call_api.py:230 起）。

**client_wrappers.py 的客户端族**：抽象基类 `Client(abc.ABC)`（client_wrappers.py:36）定 `_single_call`（client_wrappers.py:52）与 `__call__` 批处理模板方法（client_wrappers.py:58-69）；tenacity 重试装饰器 `@retry(wait_random_exponential(15,60), stop_after_attempt(3))`（client_wrappers.py:73）；SSH 隧道支持把 `import sshtunnel_requests` 藏在方法体内（client_wrappers.py:76-78），跨机访问推理服务。三家 HTTP 客户端继承基类：TRTLLMClient client_wrappers.py:108、VLLMClient client_wrappers.py:136、SGLClient client_wrappers.py:161。**勘误钉版：OpenAIClient（client_wrappers.py:188）与 GeminiClient（client_wrappers.py:342）是裸类，不继承 Client**——图谱摘要称"五个远程客户端均派生自抽象基类"不成立，实际只有三家 HTTP 客户端继承；OpenAIClient 另有 Azure 兼容（get_azure_api_key client_wrappers.py:306，调用点 client_wrappers.py:242）与自带重试（client_wrappers.py:264）。

**三引擎服务侧**：serve_trt.py 以 mpi4py 多进程起 TensorRT-LLM（ModelRunnerCpp 加载 engine）套 Flask+flask_restful 端点，WrapperServer 工作线程处理请求队列；serve_vllm.py 是 FastAPI+AsyncLLMEngine 的 /health+/generate；SGLang 没有仓内服务脚本——由 run.sh 直接 `python -m sglang.launch_server` 外部拉起（run.sh:75-76，注释 run.sh:82 提示挂死用 killall_sglang.sh）。这正是 RULER 能横评 vLLM/TRT-LLM/SGLang 三家推理栈的结构基础。

**环境侧一枚暗雷**：Dockerfile 在 requirements 之外单独源码编译四个包——flash-attn==2.6.0.post1 `--no-build-isolation`（docker/Dockerfile:22）、rotary（flash-attention 仓 csrc 子目录 git 安装 docker/Dockerfile:23）、causal-conv1d==1.4.0（docker/Dockerfile:24）、mamba-ssm==2.2.2（docker/Dockerfile:25）——它们是 vLLM 服务 Mamba/Jamba 架构的硬依赖，版本与 requirements.txt 是两套并行清单。

## 6. 深潜三：评测闭环——string_match 双指标与公平性设计

evaluate.py 读预测 jsonl 与参考答案，经 importlib 动态加载 `eval/<benchmark>/constants.py` 的指标函数，按任务跑分后聚合写 evaluation 结果与 submission。指标只有一对：**string_match_part**（预测命中任一参考答案即得分，scripts/eval/synthetic/constants.py:24——服务 NIAH 多值答案）与 **string_match_all**（须全部命中，scripts/eval/synthetic/constants.py:28——服务 VT 全变量列举），TASK_METRICS 把 13 个任务变体映射到两者（scripts/eval/synthetic/constants.py:35-47）。评测端与生成端共享 data/synthetic/constants.py 的 answer_prefix 约定——答案切分口径一致，分数才可比。

公平性三支柱值得钉版：① **采样锁死**——greedy `TEMPERATURE="0.0"`（config_models.sh:15）在控制面统一；② **长度真对齐**——tokenizer.py 五种分词器（select_tokenizer tokenizer.py:26 分发）保证"4K 上下文"是按目标模型的真实 token 数算的，不是字符数；③ **提示等价**——template.py 的 Templates 字典给 11 种模型对话外壳（base template.py:16、meta-chat template.py:18、vicuna-chat template.py:20、chatglm-chat template.py:26、RWKV template.py:28、meta-llama3 template.py:32、jamba template.py:34、nemotron5-instruct template.py:36 等），prepare.py 把任务模板嵌进对应外壳（prepare.py:87-88），同一任务在不同模型上提示等价。

## 7. 新人路线图与避坑

**阅读路线**：README（动机）→ run.sh 132 行（流水线骨架）→ config_models.sh/config_tasks.sh（控制面词汇表）→ prepare.py + 任意一个生成器（推荐 niah.py）→ call_api.py 的 get_llm → eval/synthetic/constants.py 49 行（裁决规则）。

**勘误与陷阱清单**（全部源码实证）：

1. **english_words.json 是 LFS 指针**：磁盘上只有 3 行（version/oid/size 8564991），不 `git lfs pull` 则词堆类任务必炸——.gitattributes:1-3 的 LFS 规则覆盖全部 json。
2. **OpenAIClient/GeminiClient 不继承 Client 基类**（client_wrappers.py:188/client_wrappers.py:342 裸类声明），继承基类的只有 TRTLLM/VLLM/SGL 三家（client_wrappers.py:108/client_wrappers.py:136/client_wrappers.py:161）——图谱摘要"五客户端均派生"是错的。
3. **对话模板是 11 种不是 12 种**（template.py:16-36 实数；图谱/层摘要写 12）。
4. **"顶层 import 仅 stdlib"说法不准**：call_api.py 顶层有 tqdm（call_api.py:42）与 nemo 的 read_manifest（call_api.py:45）；真正延迟的是**本仓** client_wrappers/model_wrappers 的 7 处函数体内 import（call_api.py:100-call_api.py:183）——静态 import 图对这类文件必然不全（图谱已按源码补边）。
5. **依赖是两套清单**：requirements.txt 之外 Dockerfile 单独 pin 四个 Mamba 系硬依赖（Dockerfile:22-25）且绕过 requirements 以 --no-build-isolation 源码编译；复现环境别只装 requirements。
6. 三引擎中 SGLang 无仓内服务脚本（run.sh:75-76 外部拉起），serve_vllm/serve_trt 才是仓内资产。
7. 想加新任务三步即可：synthetic/<task>.py 写 generate_samples → synthetic.yaml 加键 → config_tasks.sh 数组追加——prepare.py 的 importlib 动态加载（prepare.py:72）保证流水线零改动。
