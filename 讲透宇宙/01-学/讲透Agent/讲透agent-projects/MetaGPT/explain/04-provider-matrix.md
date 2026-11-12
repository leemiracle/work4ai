# 04 LLM Provider 矩阵：metagpt/provider/

## 一、角色定位

provider/ 是模型接入层：14 个 LLM 类（provider/__init__.py:8-21 统一 re-export）各包一家 API，全部继承 base_llm.py 的 BaseLLM，向上只暴露 aask/acompletion 等统一异步接口。分派核心是 llm_provider_registry.py 的注册表：config2.yaml 的 api_type 枚举值 → provider 类。这层的三个看点：反向注册的装饰器机制、openai 兼容层吃掉大半"API 类型"、以及两家深度魔改（智谱绕 SDK、Bedrock 双计费）。

## 二、内部结构（行号锚）

**注册表（provider/llm_provider_registry.py，48 行）**：
- llm_provider_registry.py:11-18 `LLMProviderRegistry`：朴素 dict，register/get_provider 两方法。
- llm_provider_registry.py:24-36 `register_provider(keys)` 装饰器：支持单键或列表键，装饰即注册。
- llm_provider_registry.py:38-45 `create_llm_instance(config)`：`LLM_REGISTRY.get_provider(config.api_type)(config)` 工厂 + o1 系 use_system_prompt 修正。
- llm_provider_registry.py:48 模块级 `LLM_REGISTRY` 单例。

**OpenAI 兼容层（provider/openai_api.py）**：
- openai_api.py:43-57 `@register_provider` 挂 11 键：OPENAI/FIREWORKS/OPEN_LLM/MOONSHOT/MISTRAL/YI/OPEN_ROUTER(:51)/DEEPSEEK/SILICONFLOW/OPENROUTER(:55)/LLAMA_API——**OPEN_ROUTER 与 OPENROUTER 双名并存**，同一类注册两次（命名迁移遗留勘误），DeepSeek/Moonshot 等都走 OpenAI 协议。

**Anthropic（provider/anthropic_api.py）**：
- anthropic_api.py:14 `@register_provider([LLMType.ANTHROPIC, LLMType.CLAUDE])`——claude 是 anthropic 的列表别名而非独立 provider（映射勘误：按 claude_api.py 找文件会扑空）。

**智谱双轨（provider/zhipuai_api.py + zhipuai/ 子包）**：
- zhipuai_api.py:26 `@register_provider(LLMType.ZHIPUAI)` 走本地 zhipuai/ 包。
- zhipuai/zhipu_model_api.py:8 `class ZhiPuModelAPI(ZhipuAI)`——继承外部 pip 包 zhipuai 的 ZhipuAI 却绕开其 HTTP 层：:15-21 `split_zhipu_api_url` 硬编码 `https://open.bigmodel.cn/api/paas/v4/chat/completions` 再 split 重组，把请求转给 MetaGPT 自家 GeneralAPIRequestor（注释明言防 SDK 版本升级断链）。
- 同名共存陷阱：zhipu_model_api.py 里 `from zhipuai import ZhipuAI`（pip 包）与 `from metagpt.provider.zhipuai...`（本地包）在同一文件——解析 import 时勿混淆。

**vendored fork（provider/general_api_base.py）**：
- general_api_base.py:2 头注释 `refs to openai 0.x sdk`——整文件是 openai 0.x APIRequestor 的 fork：品牌化请求头（LLM-Organization/X-LLM-Client-User-Agent）但 ValueError 文案仍留 'openai.proxy'；其 _interpret_response 是空壳，只有子类 GeneralAPIRequestor 可用。消费者：ollama_api/zhipu_model_api/openrouter_reasoning。

**Bedrock（provider/bedrock_api.py）**：
- bedrock_api.py:163-164 从响应头 `x-amzn-bedrock-input/output-token-count` 取 token 记一次成本（经 :89 _update_costs）；:134-136 流式收尾又把 provider.usage（AnthropicProvider message_stop 填的 invocationMetrics，同源数字）再记一次——**流式路径成本双计**（疑似 bug，账面翻倍）。

## 三、外部连接

上游：Context.llm（context.py:86-91）与 Action._update_private_llm（action.py:46-54）都经 create_llm_instance 拿实例；config/config2.yaml 的 api_type 经 configs/llm_config 的 LLMType 枚举进入注册表。下游：BaseLLM 的 cost_manager 上报 utils/cost_manager；postprocess/ 子包与 base_llm.py:340 compress_messages 同属输出处理线。方向性事实：**注册方向是反的**——llm_provider_registry.py 不 import 任何 provider，各 provider 文件 import 装饰器自注册（导入即注册的副作用模型），所以必须经 provider/__init__.py 或 config 触发导入，注册表才有货。

## 四、数据流

一次调用的路径：Role._act → Action.llm.aask → BaseLLM.aask（base_llm.py:207）组消息（system+history+user、mask_base64 打码图片日志）→ compress_messages 按配置截断（:207 调用）→ 具体 provider 的 acompletion → 流式聚合 → _update_costs 记 token 与费用（BudgetManager 汇总）→ 返回文本。配置侧：config2.yaml llm 段 → LLMConfig(api_type=...) → create_llm_instance 分派。roles 节还能按角色 className 覆写独立 LLM（config2.example.yaml）。

## 五、设计决策与勘误（证据锚）

- **Context.deserialize 丢返回值（NOTES-DIGEST 15）**：context.py:127 `self.cost_manager.model_validate_json(cost_manager)`——pydantic v2 该方法返回新对象而非原地更新，返回值被丢弃，恢复会话后费用账本是空的（预算护栏失效），Team.deserialize 断点续跑时尤其危险。
- **陈旧多模态白名单（NOTES-DIGEST 23）**：provider/constant.py:34 MULTI_MODAL_MODELS 停在 2024 模型代；base_llm.py:91-92 `support_image_input` 用子串匹配，新模型默认判为不支持图像。
- **AnthropicLLM timeout 形同虚设**：_achat_completion 接收 timeout 但从不传给 SDK（NOTES-DIGEST 24）。
- **bedrock 子包隐患（NOTES-DIGEST 19）**：bedrock_provider.get_provider 对 model_id 不含 '.' 的型号 UnboundLocalError；Cohere/Meta/Ai21 三个 Provider __init__ 不调 super()。
- **死枚举**：zhipuai_api.py 的 ZhiPuEvent 四态枚举定义后全链零引用。
- 设计上可取的是双轨智谱：ZhiPuAILLM（zhipuai_api.py:26）为协议层、ZhiPuModelAPI（zhipu_model_api.py:8）为传输层，fork openai 0.x 的 requestor 换来"SDK 升级不断链"的隔离——代价是两套同名 zhipuai 命名空间的心智负担。

## 六、新人提示

1. 加新供应商：若是 OpenAI 兼容协议，大概率只需在 config2.yaml 写 api_type: openai + base_url，不用写代码；写新 provider 才需要 @register_provider + 继承 BaseLLM。
2. api_type 到文件的映射有反直觉处：claude→anthropic_api.py、llama_api/openrouter→openai_api.py、gemini→google_gemini_api.py；openrouter_reasoning.py 只注册 OPENROUTER_REASONING，api_type=openrouter 不走它。
3. 排查成本翻倍先看 bedrock 流式（:89 与 :136 两处 _update_costs）；排查恢复会话预算失控看 context.py:127。
4. 改 general_api_base.py 前先确认依赖的模块级 openai.* 属性仍在（requirements 钉 openai~=1.64.0，暂无断链风险）。
5. 全部 provider 测试默认不跑（pytest.ini ignore 列表含 tests/metagpt/provider/zhipuai 等），本地改动后要手动点名跑对应测试文件。
