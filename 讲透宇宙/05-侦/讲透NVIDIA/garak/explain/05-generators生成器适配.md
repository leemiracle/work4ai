# 05 generators 生成器适配：双基类与 Configurable 装配

## 角色定位

`garak/generators/`（26 个模块，图谱 L04）把被测模型抽象成统一接口 `generate(Conversation) -> List[Message]`。工程问题是**适配器爆炸**——OpenAI 系、HuggingFace 本地、Rest/WebSocket、LiteLLM/Bedrock/watsonx 全要接。garak 双基类分治：`generators/base.py` 的 `Generator` 定契约与生成编排；`generators/openai.py:135` 的 `OpenAICompatible` 吸收「一切 OpenAI 协议兼容端点」（vLLM/NIM/Groq 等十余子类只改 ENV_VAR/uri）；本地权重装载由 `resources/api/huggingface.py:11` 的 `HFCompatible` mixin 独立供给（generators/huggingface、detectors/HFDetector、buffs/paraphrase 三处共享）。所有类站在 `configurable.py:24` 的 `Configurable` 地基上。

## 内部结构

**Generator**（`generators/base.py:21`）：DEFAULT_PARAMS 只留采样通用项 max_tokens=150/temperature/top_k/context_len/skip_seq（:25-32）；`_run_params={"deprefix","seed"}`、`_system_params`（:34-35）声明全局回灌面；`supports_multiple_generations=False`（:46-48）。模板方法 `generate()`（:138-244）四分支：单代直调（:169-170）；多代且支持则一次 n 代（:172-173）；多代且 `parallel_requests>1` 走 `Pool.imap_unordered([prompt]*n)`（:176-216），pool_size=min(n, parallel_requests, max_workers)（:191-195），每结果过 `_verify_target_result` 断言（:89-97：list、单元素、Message|None）；兜底串行（:218-230）。出口：数量不符 raise `BadGeneratorException`（:232-236）→ post hook（:238）→ skip_seq 剪枝（:240-242；`_prune_skip_sequences` :107-136 三条正则剥标记段）。子类契约「覆写 `_call_model`，别碰 generate」（:146）；`_conversation_to_list`（:246-256）压平 Conversation 为 OpenAI 形 dict。

**OpenAICompatible**（`openai.py:135`）：`ENV_VAR` 占位待覆写（:138）；DEFAULT_PARAMS 补 uri=`http://localhost:8000/v1/`（vLLM 惯例）、stop、`transient_retry_codes=[408,429,502,503,504]`、`suppressed_params`（:145-157）。`__init__`（:205-224）先 `_validate_uri_connectivity`（:188-200，httpx 5s 预检，不通即 BadGeneratorException）再 `_load_unsafe`（:178-186）。`_call_model`（:295-418）三讲究：**create_args 反射装配**（:311-323）遍历 `inspect.signature(generator.create).parameters`，实例同名属性自动带上——新 API 参数零代码适配，`suppressed_params` 黑名单逃生；**异常分类学**（:352-386）——401/403 **离帧前**转 GarakException（:354-369，注释引 issue #1357：openai 异常携带不可 pickle 的 httpx.Response，在 Pool worker 里 TypeError 掩盖真错），瞬时码 raise `GeneratorBackoffTrigger` 交 `@backoff.fibo, max_value=70` 斐波那契退避（:284-294）；**多模态重载**（:226-281）把 Message.data base64 内联为 image_url/input_audio part。末端 `OpenAIGenerator`（:421）按模型名单分派 chat/completions（:447-459）；`OpenAIReasoningGenerator`（:475）屏蔽 o 系不支持的参数（:486）；`DEFAULT_CLASS`（:492）供 `-m openai` 短名解析。

**HFCompatible**（`resources/api/huggingface.py:11`）五工具：`_gather_hf_params`（:20-88）签名反射把 `hf_args` 映射到 from_pretrained/pipeline 参数（torch_dtype 转属性 :58-61；device_map 优先 :63-79；trust_remote_code 锁 False :82-86）；`_gather_generation_params`（:90-97）对齐 GenerationConfig；`_select_hf_device`（:99-129）cuda→mps→cpu 并开 MPS fallback（:122-124）。

**Configurable**（`configurable.py:24`）：`_load_config`（:72-116）按 `plugins.<type>.<namespace>[.<Class>]` 三层取配置；`_apply_config`（:118-148）尊重调用方显式传参（:137-145）；`_validate_env_var`（:169-183）自动取环境变量 key，缺失抛 APIKeyMissingError 带修复提示；`__getstate__/__setstate__`（:55-70）pickle 时把 `_unsafe_attributes` 置 None、反序列化后 `_load_unsafe` 重建——Pool 分发根基。

## 外部连接

- **上游**：`cli.py:744-746` `load_plugin(f"generators.{target_type}")` 唯一实例化入口；TAP/AutoDAN 动态探针二次实例化辅助 generator（`probes/tap.py:136/:142` 双模型）。
- **下游 probe**：`probe()` 持引用并要求 `parallel_capable`（`probes/base.py:330`）；GCG/BEAST 直接摸 `generator.model/tokenizer`（`resources/beast/beast_attack.py:370-381` 校验存在性）。
- **家族面**：rest/guardails 走 HTTP 泛化；langchain/function 走函数包装；test.py 假 generator；nvcf/nim/azure/groq 均为 OpenAICompatible 后代。HTTP UA 由 `get/set_http_lib_agents` 包裹全流程（`cli.py:332/:793`）。

## 数据流

```
load_plugin → Generator.__init__（Configurable 装配：env key → DEFAULT_PARAMS → 配置文件 → run/system 回灌）
probe._execute_attempt → generator.generate(Conversation, generations_this_call)
  → 四分支编排 → _call_model（子类唯一必写）
     OpenAICompatible: create_args 反射组装 → backoff 重试环 → response.choices → List[Message]
  → _verify_target_result → post hook → skip_seq 剪枝 → 返回
→ attempt.outputs setter 接收（02 篇总线）
```

## 设计决策

1. **模板方法锁死编排**：`generate()` 集中并行/多代/校验/剪枝，26 个适配器只写 `_call_model`——并行语义全家族一致，probe 不感知后端差异。
2. **pickle 安全前置**：`_unsafe_attributes`+`__setstate__` 重建（`configurable.py:65-70`）与 OpenAI「异常离帧前转译」（`openai.py:358-363`）是同一主题两半：一切可在 Pool 间安全运输。
3. **签名反射代替手写参数表**：create_args（:311-319）与 `_gather_hf_params`（huggingface.py:37-51）读被调方签名对号入座，API 演进零改动；撞车靠 suppressed_params 逃生。
4. **连通性预检 fail-fast**（:188-200）：端点写错从扫描中期提前到构造期。
5. **DEFAULT_PARAMS 用 dict 非类属性**（`base.py:24` 注释点明防类变量共享陷阱）；子类 `Parent.DEFAULT_PARAMS | {...}` 合成（`openai.py:145`）。

## 新人提示

- 接新后端先判协议：OpenAI 兼容→继承 OpenAICompatible 只改 `ENV_VAR/uri/generator_family_name`（参照 groq.py）；非标 HTTP→rest.py；本地权重→huggingface.py+HFCompatible。
- 「无返回」合法：`_call_model` 可返 `[None]`（:370-374），detector 以 None 对齐；坏请求别 raise。
- `supports_multiple_generations` 设 True 但 API 忽略 n 参数会触发 :232-236 数量断言，报错文案即提示检查该标志。
- seed 双重生效：实例 `_rng`（:64-66）+ generate 每次重播种（:154-155），复现实验必须 `--seed`。
- 配置没生效排查：`_apply_config` 显式传参优先（:137-145）+ `_instance_configured` 一次性锁（:73-74）——构造后改配置无效，多层继承只装一次。
