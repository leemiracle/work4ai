# 02 · scripts/pred + run.sh — 预测侧：五家 Client、延迟 import 与三引擎服务

> 源码：`scripts/pred/call_api.py`（333 行）、`client_wrappers.py`（416 行）、`model_wrappers.py`、`serve_vllm.py`、`serve_trt.py` + `scripts/run.sh`（132 行）· 图谱定位：4 层第 4 层「预测服务与评测层」· client_wrappers fanOut=12

## 一、角色定位：三步流水线的第二步，吞吐也是被测对象

预测侧要回答的问题是：**任意模型（本地权重或云 API）如何被同一套循环驱动**。call_api.py 是统一入口，client_wrappers.py 提供客户端族，model_wrappers.py 提供进程内推理，两个 serve 脚本 + 外部 SGLang 构成三引擎服务侧。run.sh:132 在收尾打印 `Total time spent on call_api`——预测吞吐（tok/s）与精度并列为一等公民产出，这也是评测长上下文模型服务化效率的口径。

## 二、内部结构：get_llm 分发 + Client 族

**get_llm 的延迟导入**（scripts/pred/call_api.py）：按 server_type 分支，七处本仓模块导入全部在函数体内——TRTLLM/VLLM/SGL/OpenAI/Gemini 五家 Client 分别在 call_api.py:100/:116/:131/:146/:158，本地 HuggingFace/Mamba 包装在 call_api.py:170/:183。效果：装不起某后端依赖的用户 import 本文件零负担，五家并存互不干扰。注意勘误：顶层 import 并非"仅 stdlib"——tqdm（call_api.py:42）与 nemo 的 read_manifest（call_api.py:45）就在顶层；真正被延迟的是**本仓**模块。预测端还读生成端同一份任务常量：`importlib.import_module(f"data.{args.benchmark}.constants")`（call_api.py:209）。主流程多线程+进度条逐任务批量请求（call_api.py:230 起）落盘预测 jsonl。

**Client 族**（client_wrappers.py）：抽象基类 `Client(abc.ABC)`（client_wrappers.py:36）定义 `_single_call` 抽象（:52）与 `__call__` 批处理模板方法（:58-69，循环调 _single_call）。三家 HTTP 客户端继承它：TRTLLMClient（:108）、VLLMClient（:136）、SGLClient（:161）。横切设施：tenacity `@retry(wait_random_exponential(min=15, max=60), stop_after_attempt(3))`（:73）；SSH 隧道把 `import sshtunnel_requests` 藏进方法体（:76-78），支持跨机访问推理服务。**勘误钉版**：OpenAIClient（client_wrappers.py:188）与 GeminiClient（:342）是**裸类、不继承 Client**——图谱摘要"五个远程客户端均派生自抽象基类"不成立。OpenAIClient 自带云 API 三件：Azure 兼容 get_azure_api_key（:306，调用点 :242）、token 计数、独立重试（:264）；GeminiClient 走 google-generativeai SDK（:342，重试 :378）。

**本地线**（model_wrappers.py）：HuggingFaceModel（model_wrappers.py:22-94）transformers 权重直接前向（含对话模板），MambaModel 服务 Mamba/混合架构——server_type=base 时绕过 HTTP 进程内推理。

## 三、外部连接：run.sh 的三引擎拉起与配置传递

run.sh 先 source 两份配置（scripts/run.sh:34、:52），把 MODEL_SELECT 输出的冒号串用 `IFS=":" read` 一口解包成 MODEL_PATH/MODEL_TEMPLATE_TYPE/MODEL_FRAMEWORK/TOKENIZER_PATH/TOKENIZER_TYPE/OPENAI_API_KEY/GEMINI_API_KEY/AZURE_ID/AZURE_SECRET/AZURE_ENDPOINT 十个变量（run.sh:37）——**冒号拼接字符串是全仓配置协议**，scripts/config_models.sh:27 的 MODEL_SELECT 按 case 分支产出（llama2-7b-chat :33-37、llama3.1-8b-chat :38-42、jamba1.5-mini :43-45 等）。然后按框架三分支拉服务：vllm → `python pred/serve_vllm.py`（run.sh:62-63，FastAPI+AsyncLLMEngine 的 /health+/generate）；trtllm → `python pred/serve_trt.py`（run.sh:70-71，mpi4py 多进程起 ModelRunnerCpp 加载 engine，Flask+flask_restful 端点，WrapperServer 工作线程处理请求队列）；sglang → **无仓内服务脚本**，直接 `python -m sglang.launch_server`（run.sh:75-76，挂死用 killall_sglang.sh，注释 :82）。预测阶段 `--server_type ${MODEL_FRAMEWORK}` 把框架名直通 get_llm（run.sh:110-115）。

## 四、数据流：一条预测请求的旅程

prepare 落盘的 jsonl（含 input 与 answer_prefix）→ call_api 按任务读入，经 constants 拿 tokens_to_generate（call_api.py:209 加载同一份 TASKS）→ get_llm(server_type) 返回客户端/包装实例 → 多线程池对每条样本调 `client(prompt)`：__call__（client_wrappers.py:58）逐条路由 _single_call（HTTP 家族发 JSON 到对应端点；OpenAI/Gemini 走各自 SDK，重试与 SSH 隧道横切）→ 输出剥壳后写 pred jsonl → run.sh 记录该阶段耗时（run.sh:132）→ 交给 eval/evaluate.py（run.sh:127 调用）。服务端视角：serve_vllm 的 /generate 收到 prompt+采样参数（greedy：config_models.sh:15 `TEMPERATURE="0.0"`、TOP_P 1.0 :16、TOP_K 32 :17）经 AsyncLLMEngine 出 token 流。

## 五、设计决策：四个值得偷师的取舍

1. **延迟 import 做后端插件化**：五家互斥后端共存一仓零冲突（call_api.py:100-183）——比 try/except ImportError 顶层导入干净，比插件目录轻量；代价是静态 import 图残缺，跨文件依赖要靠人读源码（本仓图谱已手补边）。
2. **模板方法批处理**：基类 __call__ 固定批循环骨架，子类只写 _single_call（client_wrappers.py:52-69）——五家后端的批量/重试/隧道行为天然一致。
3. **冒号串配置协议**：shell 侧一个字符串传递全部模型配置（run.sh:37 IFS 解包），跨容器/跨机复制粘贴即可——比 JSON 配置文件更适合"实验参数随手改"的场景，代价是无类型无校验，字段顺序错一位全线崩。
4. **三引擎对齐三家推理栈**：vLLM/TRT-LLM/SGLang 各有独立 serve 路径（run.sh:62-76），同一批数据可在三栈横评——评测框架顺带成为推理栈基准，这是 RULER 结构上的意外红利。

## 六、新人提示

- 接新后端四步：client_wrappers.py 加 XxxClient（继承 Client 基类，写 _single_call）、call_api.py 的 get_llm 加分支（照 :116-:130 的 vLLM 分支抄）、config_models.sh 的 MODEL_SELECT 加 case、run.sh 加 serve 分支。
- 云 API 评测注意 OpenAIClient 的 Azure 路径（client_wrappers.py:242/:306）——Azure 凭据走三元组（ID/SECRET/ENDPOINT），与 OPENAI_API_KEY 并列在冒号串后三位（run.sh:37）。
- 跨机评测用 SSH 隧道：client 构造参数给 ssh_server/ssh_key_path，sshtunnel_requests 在 _single_call 内建立（client_wrappers.py:76-78）。
- 复现环境别只装 requirements.txt：Mamba/Jamba 类模型另需 Dockerfile 四包（flash-attn/rotary/causal-conv1d/mamba-ssm，docker/Dockerfile:22-25，--no-build-isolation 源码编译）。
- 验证练习：server_type=openai + 任意小任务，把 NUM_SAMPLES 降到 4 跑一遍 call_api——确认预测 jsonl 的 output 字段与 answer_prefix 拼接格式，为读评测端 string_match（scripts/eval/synthetic/constants.py:24-28）做准备。
