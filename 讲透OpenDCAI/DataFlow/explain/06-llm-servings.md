# 06 · serving 五后端——同一契约下的 API、VLM、双 RAG 与 LiteLLM

## 角色定位

`dataflow/serving/` 下 14 个后端全部实现 `LLMServingABC`（`llm_serving.py:5`）的三抽象方法（`llm_serving.py:8-28`）。本篇聚焦五条主线：OpenAI 兼容 API、多模态 VLM、检索型 FlashRAG、图谱 RAG LightRAG、多供应商网关 LiteLLM。Pipeline 按类型别名 `LLM_SERVING_CLASSES`（`core/__init__.py:9`）探测算子里的后端并在引用计数归零时调 cleanup（`Pipeline.py:537-542`）。

## 内部结构

`APILLMServing_request`（`api_llm_serving_request.py:21`）：API key 从环境变量取（默认 `DF_API_KEY`，缺 key 直接 ValueError，`api_llm_serving_request.py:69-73`）；`requests.Session` 连接池按 max_workers 预热（`api_llm_serving_request.py:76-84`）；逐请求重试（`api_llm_serving_request.py:225`）；记录与预算模式（`api_llm_serving_request.py:37-52`）配合可被杀的独立 worker（`_bounded_api_worker.py:1-11`）；chat/对话/embedding 三个批量入口（`api_llm_serving_request.py:345/365/378`）。`APIVLMServing_openai`（`api_vlm_serving_openai.py:13`）：图片转 base64（`api_vlm_serving_openai.py:56`）、单图/多图两条链路（`api_vlm_serving_openai.py:176/294`），`generate_from_input` 桥接到单图（`api_vlm_serving_openai.py:355`）。`FlashRAGServing`（`flash_rag_serving.py:20`）是检索不是生成：返回 `List[List[str]]` 多文档（`flash_rag_serving.py:97`），`load_model` 建索引（`flash_rag_serving.py:67`）。`LightRAGServing`（`light_rag_serving.py:48`）：lightrag-hku 懒 import、缺包给安装提示（`light_rag_serving.py:62-73`）；因初始化必须 await，提供异步工厂 `create`（`light_rag_serving.py:92-113`）。`LiteLLMServing`（`lite_llm_serving.py:10`）用 litellm 统一多家供应商，litellm 在 `__init__` 懒加载（`lite_llm_serving.py:77-80`）。

## 外部连接与三处甄别

出口清单 `serving/__init__.py` import 了 13 个名字（`serving/__init__.py:1-15`），但 `__all__` 只列 10 项（`serving/__init__.py:18-29`）——甄别一：`LocalEmbeddingServing`（`serving/__init__.py:11` 已 import）漏出 `__all__`，star import 拿不到（具名 import 仍可用）；同病还有 `LightRAGServing`（`serving/__init__.py:12`）。甄别二（真 bug）：`FlashRAGServing` 没被 `__init__.py` 导入，而 `agentic_rag_multihop_core_pipeline.py:12` 写了 `from dataflow.serving import FlashRAGServing`（`:214` 确有实例化）——该 pipeline 一运行即 ImportError，修法是补导出或从 `flash_rag_serving` 直取。甄别三：`lite_llm_serving.py:22-24` 与 `lite_llm_serving.py:25-27` 连续两个同名 `def start_serving`，后者静默覆盖前者；两实现逐字相同故无症状，但属真重复定义。另有一处契约错位值得点名：FlashRAG 与 LightRAG 的 `cleanup`/`generate_from_input` 都是 `async def`（`flash_rag_serving.py:93/97`、`light_rag_serving.py:118/141`），而 ABC 契约与 Pipeline 调用全是同步——同步调用 async 方法只会拿到 coroutine 对象并不执行。

## 数据流

以 API 后端为例：算子把 prompt 列表交 `generate_from_input` → 组装 `id+payload+model` 任务参数（`api_llm_serving_request.py:350-361`）→ 线程池并发请求 → 按 id 回填保序（`api_llm_serving_request.py:318-343`）→ 返回与输入等长的列表。VLM 多一步图片编码；FlashRAG/LightRAG 把"生成"替换为"检索/图谱查询"，输出从字符串列表变文档列表。

## 设计决策

统一契约让算子对后端无感：同一算子换 serving 即换引擎，Pipeline 的探测/清理逻辑（`Pipeline.py:69/537-542`）只依赖 ABC；API key 一律走环境变量名注入避免入库。批判：契约声明落后于实现——`json_schema` 扩展参遍布各后端但 ABC 未声明；async/sync 双态后端说明三方法契约对异步生态过简；`__init__.py` 导出面与存量不同步（漏 2 缺 1），是最易踩的暗坑。

## 新人提示

新后端照抄三抽象方法签名即可接入，但注意 `json_schema` 已是事实参数。embedding 需求别用 `generate_from_input`——`LocalEmbeddingServing` 的该方法是 `[None]*n` 占位（`LocalSentenceLLMServing.py:178-180`），正确入口是 `generate_embedding_from_input`（`LocalSentenceLLMServing.py:118`）。跑 agentic_rag_multihop pipeline 前先修 `__init__.py` 导出；"协程未执行"类怪象先查后端是否 async 实现。
