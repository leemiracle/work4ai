# llm_provider.py 精讲——多供应商抽象：14 分支工厂与两个 DeepSeek 适配器

> 源码：`/usr-data/data2/repos/browser-use/web-ui/src/utils/llm_provider.py`（355 行）
> 图谱层位：L03 LLM/MCP 共享服务层

## ① 角色定位

`llm_provider.py` 是全项目唯一的 **LLM 构造工厂**：输入一个 provider 名字加一组 kwargs，输出一个 LangChain `BaseChatModel` 实例。UI 上 Agent Settings 的 "LLM Provider" 下拉框每换一个选项，背后就是这里的某个分支被走到。文件由两部分构成：

1. **两个 DeepSeek-R1 推理模型适配器**（llm_provider.py:55-149）——处理 `<think>` 推理内容与正文分离的模型输出；
2. **工厂函数 `get_llm_model(provider, **kwargs)`（llm_provider.py:152-355）**——**14 个显式 provider 分支**（钉版勘误：是 14 个不是 15 个；逐一清点为 anthropic/mistral/openai/grok/deepseek/google/ollama/azure_openai/alibaba/ibm/moonshot/unbound/siliconflow/modelscope）+ 一个 `else: raise`（llm_provider.py:354-355）。

它的设计哲学是"**能用 OpenAI 兼容协议就用 ChatOpenAI 套壳**"：14 家里 9 家（openai/grok/deepseek-chat/alibaba/moonshot/unbound/siliconflow/modelscope/azure）最终落到 ChatOpenAI/AzureChatOpenAI，只有 5 家走各自的官方 LangChain 集成（ChatAnthropic/ChatMistralAI/ChatGoogleGenerativeAI/ChatOllama/ChatWatsonx）。

## ② 内部结构

**统一 API key 闸门（llm_provider.py:159-166）**：除 `ollama`/`bedrock` 外（llm_provider.py:159），所有 provider 先拼 `{PROVIDER}_API_KEY` 环境变量名，`kwargs["api_key"]` 与 `os.getenv` 双源取值，取不到就抛带 UI 提示的 ValueError（llm_provider.py:164-165，错误文案用 `config.PROVIDER_DISPLAY_NAMES` 做友好名映射）。通过后把解析出的 key 回写 `kwargs["api_key"]`（llm_provider.py:166），供各分支使用。

**DeepSeekR1ChatOpenAI（llm_provider.py:55-115）**：继承 ChatOpenAI，但 `__init__` 里在 `super().__init__` 之后**用裸 `openai.OpenAI` 客户端覆盖 `self.client`**（llm_provider.py:59-62）——动机是 deepseek-reasoner 返回的 `reasoning_content` 字段需要原生 SDK 才拿得到。`ainvoke`（llm_provider.py:64-88）与 `invoke`（llm_provider.py:90-114）是两段几乎逐行重复的代码：手写 LangChain 消息→OpenAI dict 的转换（System/AIMessage/其他三分支，llm_provider.py:72-79），调 `chat.completions.create`（llm_provider.py:81/107），再把 `reasoning_content` 和 `content` 一起装回 AIMessage（llm_provider.py:86-88/112-114）。

**DeepSeekR1ChatOllama（llm_provider.py:117-149）**：本机 Ollama 跑 deepseek-r1 的版本。核心是两行字符串手术：`reasoning_content = org_content.split("</think>")[0].replace("<think>", "")`、`content = org_content.split("</think>")[1]`（llm_provider.py:129-130/145-146），外加剥 Ollama 常见的 `**JSON Response:**` 前缀（llm_provider.py:131-132/147-148）。invoke/ainvoke 同样是同步异步双份重复。

**14 分支速查（行号锚）**：

| provider | 类 | 默认模型 | 分支行 |
|---|---|---|---|
| anthropic | ChatAnthropic | claude-3-5-sonnet-20241022 | llm_provider.py:168-179 |
| mistral | ChatMistralAI | mistral-large-latest | llm_provider.py:180-195 |
| openai | ChatOpenAI | gpt-4o | llm_provider.py:196-207 |
| grok | ChatOpenAI | grok-3 | llm_provider.py:208-219 |
| deepseek | 按 model 分流 | deepseek-chat / reasoner→R1 适配器 | llm_provider.py:220-239 |
| google | ChatGoogleGenerativeAI | gemini-2.0-flash-exp | llm_provider.py:240-245 |
| ollama | ChatOllama / R1-Ollama | qwen2.5:7b / deepseek-r1:14b | llm_provider.py:246-266 |
| azure_openai | AzureChatOpenAI | gpt-4o | llm_provider.py:267-279 |
| alibaba | ChatOpenAI | qwen-plus | llm_provider.py:280-291 |
| ibm | ChatWatsonx | ibm/granite-vision-3.1-2b-preview | llm_provider.py:292-308 |
| moonshot | ChatOpenAI | moonshot-v1-32k-vision-preview | llm_provider.py:309-315 |
| unbound | ChatOpenAI | gpt-4o-mini | llm_provider.py:316-322 |
| siliconflow | ChatOpenAI | Qwen/QwQ-32B | llm_provider.py:323-337 |
| modelscope | ChatOpenAI | Qwen/QwQ-32B | llm_provider.py:338-353 |

各分支的公共套路：base_url 优先取 kwargs、否则读 `{PROVIDER}_ENDPOINT` 环境变量（如 OPENAI_ENDPOINT，llm_provider.py:198）；temperature 默认 0.0（浏览器操作要确定性，这是全文件最一致的设计取向）；ollama 分支额外带 `num_ctx=32000`（llm_provider.py:256/263）与普通模型的 `num_predict=1024`（llm_provider.py:264）；azure 分支的 `api_version` 默认 `2025-01-01-preview`（llm_provider.py:272）并注意它传的是 `azure_endpoint=` 而非 `base_url=`（llm_provider.py:277）；modelscope 分支带 `extra_body={"enable_thinking": False}`（llm_provider.py:352）压 QwQ 的思考输出。

## ③ 外部连接

**消费方两处**：`browser_use_agent_tab.py:51`（主 agent 与 planner_llm 都从这里构造，planner 读 Agent Settings 的 planner_llm_* 六控件）和 `deep_research_agent_tab.py:27`（深研究编排 LLM）。两处传入的 kwargs 直接来自 agent_settings 注册的 22 个控件（llm_provider/llm_model_name/llm_temperature/use_vision/ollama_num_ctx/llm_base_url/llm_api_key 等，agent_settings_tab.py 的 `tab_components.update(dict(...))` 段）。

**配置联动**：`src/utils/config.py` 的 `model_names`（config.py:15 起）是 UI 下拉的模型清单来源（agent_settings_tab.py:65/73 引用），`PROVIDER_DISPLAY_NAMES`（config.py:1）服务报错文案。**新增 provider 需要三处同步**：本文件加分支、config.py 两张表加条目、（可选）requirements.txt 装官方集成包——漏任何一处，UI 上要么选不到、要么选中即崩。

**上游包依赖**：langchain-openai/anthropic/mistralai/google-genai/ollama/ibm/aws 全家桶（llm_provider.py:43-49 的导入块），这就是 web-ui 依赖树比 browser-use 本体还重的主因。

## ④ 数据流

一次"点 Run Agent"的 LLM 构造流：

```
UI 控件值（22 控件，含 llm_provider/llm_api_key/llm_base_url…）
  → browser_use_agent_tab 回调组装 kwargs
  → get_llm_model(provider, **kwargs)               llm_provider.py:152
  → key 闸门：{PROVIDER}_API_KEY 双源校验             :159-166
  → 命中 14 分支之一
      ├─ 兼容系 → ChatOpenAI(base_url, api_key, model_name, temperature)
      ├─ deepseek + model_name 含 reasoner → DeepSeekR1ChatOpenAI
      ├─ ollama + model_name 含 deepseek-r1 → DeepSeekR1ChatOllama
      └─ 官方集成系 → 各自 ChatXxx
  → BaseChatModel 实例
  → BrowserUseAgent(llm=main_llm)（browser_use_agent_tab.py:529）
  → 上游 Agent.step() 每步调用 llm.ainvoke(...)（R1 适配器在此接管消息转换）
```

R1 适配器的运行时数据流值得单独看：LangChain 消息列表 → 手写转 OpenAI dict（llm_provider.py:72-79）→ 同步 `create` 调用 → 从响应里**同时抽出** `reasoning_content` 与 `content`（llm_provider.py:86-87）→ AIMessage 携带双字段返回——上游 browser-use 正是靠 `reasoning_content` 的存在识别 R1 类模型并跳过函数调用、改走 raw JSON 输出（与 browser_use_agent.py:34 的 `is_model_without_tool_support` 判定呼应）。

## ⑤ 设计决策与取舍

**14 个 if/elif 而非注册表**。用 `{provider: factory}` 字典或策略对象当然更优雅，但显式分支让"改一个供应商"的 diff 完全局部化，新手也能照抄一段加新供应商——这是社区项目对可贡献性的妥协。代价是 300 行的长函数与大量重复的 base_url 三行套话。

**key 闸门前置统一（llm_provider.py:159-166）** 是本文件最好的设计：一处报错逻辑、统一文案、双源（UI 输入优先于环境变量）。但见第 ⑥ 节——moonshot/ibm 两个分支没接住这份统一红利。

**temperature 一律默认 0.0**：浏览器自动化每步都是"看状态→出动作"的近确定性决策，高温只会增加误点。这和聊天产品的默认值哲学完全相反，是从领域倒推参数的示范。

**R1 适配器为什么"重复造轮子"而不是子类改 `_generate`**：LangChain 各版本 generate/agenerate/_stream 调用链差异大，作者选择只覆写最外层 invoke/ainvoke 两扇门，内部完全绕开父类管线——简单粗暴但对这两个特定模型足够。代价见下。

**模型名硬编码在分支里**（如 azure 默认 api_version、grok-3、gemini-2.0-flash-exp）：模型迭代快于代码库更新，这些默认值很多已过时；好在 UI 下拉允许自定义模型名（`allow_custom_value=True`，agent_settings_tab.py:76），默认值只是兜底。

## ⑥ 新人提示（坑与勘误）

1. **分支数钉版：14 个**（llm_provider.py:168/180/196/208/220/240/246/267/280/292/309/316/323/338），不是 15。值得注意的是豁免名单里出现了 **bedrock**（llm_provider.py:159），但 14 分支里**没有 bedrock**——选它直接落到 `else: raise ValueError(f"Unsupported provider: {provider}")`（llm_provider.py:354-355）。豁免检查是"key 校验跳过名单"，不是"支持名单"，两者不一致是隐蔽陷阱。
2. **DeepSeekR1ChatOpenAI 的 `ainvoke` 是假异步**：llm_provider.py:81/107 调的是**同步** `self.client.chat.completions.create`，跑在 async def 里会**阻塞整个事件循环**——Gradio 队列里所有并发回调（包括 UI 心跳）都会卡到推理完成。单用户无感，多用户/长推理就是全局冻结。要修应改用 `AsyncOpenAI` + `await`。
3. **moonshot/ibm 分支无视 UI 传入的 key**：moonshot 直接 `os.getenv("MOONSHOT_API_KEY")`（llm_provider.py:313-314）、ibm 直接 `os.getenv("IBM_API_KEY")`/`IBM_PROJECT_ID`（llm_provider.py:305-306），`kwargs["api_key"]`（llm_provider.py:166 已经解析好）被晾在一边——UI 里填 key 对这两家无效，只认环境变量。而统一闸门又允许 UI key 通过校验，形成"校验过了但没被使用"的错位。
4. **DeepSeekR1ChatOllama 的 `split("</think>")[1]`（llm_provider.py:130/146）在没有 think 标签的输出上直接 IndexError**——Ollama 某些模板不吐 `<think>` 时整个 agent 会话崩在这行；上游捕获后算作一步失败，连续多次即触发 max_failures 止损。
5. **环境变量名大小写不一**：绝大多数 `{PROVIDER}_API_KEY` 大写规整，但 siliconflow 用 `SiliconFLOW_API_KEY`/`SiliconFLOW_ENDPOINT`（llm_provider.py:325/329）、azure 用 `AZURE_OPENAI_ENDPOINT`（llm_provider.py:269）。.env 里写错大小写会静默取不到值（Linux 环境变量大小写敏感）。
6. **死导入考古层**：`get_llm_cache/dumpd/dumps/ChatGenerationChunk/LLMResult/RunInfo/message_chunk_to_message/convert_to_messages/AnyMessage/BaseMessageChunk/OutputParserLike`（llm_provider.py:4-33）在文件内均只出现在导入行（实测每个名字 grep 计数为 1）；`ChatOllama` 还在 llm_provider.py:29 与 :46 **重复导入两次**；`import pdb`（llm_provider.py:2）与 `import os`（:10 在中间又出现一次）同属遗留。这些说明本文件是从 browser-use 早期 `llm.py` 拷贝精简而来，精简只删了用法没删导入。
7. **新增供应商清单**（再强调三处同步）：llm_provider.py 加分支 + config.py 的 `model_names`/`PROVIDER_DISPLAY_NAMES` 加条目 + requirements.txt 装包。漏 config 那步会出现"代码支持但 UI 下拉没有"的幽灵供应商。

一句话总结：`get_llm_model` 是一张 14 路显式分发表，统一 key 闸门与 temperature=0 体现了工厂的纪律性；但两个 DeepSeek 适配器（假异步 ainvoke、脆弱的 `</think>` 切割）和 moonshot/ibm 的 key 错位是踩雷高发区——接新供应商前先通读 ⑤⑥ 两节能避开大部分坑。
