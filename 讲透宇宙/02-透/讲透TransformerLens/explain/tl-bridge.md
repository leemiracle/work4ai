# tl-bridge · model_bridge/bridge.py 精讲（5614 行）

> 目标文件：`transformer_lens/model_bridge/bridge.py` · 图谱定位：transformer-bridge 层核心、fan-in 前五，v3 唯一门面，3.0 架构转向全浓缩在这一个类里。

## 1. 角色定位

TransformerBridge（128 个 def，全库最大类）是 v3 万能门面：把 HuggingFace 原生模型**直接包装**成可解释研究台——不复制权重、不重写组件，靠 adapter 映射在 HF 模块上"外挂"钩子。这解决了 legacy 的根本困境：HookedTransformer 每支持新架构都要重写组件+数值验证，追不上 HF 架构增速；Bridge 反转方向——模型留在 HF 生态，钩子体系适配过去，9,000+ 模型、50+ 架构族一夜可用。对用户提供与 HookedTransformer 几乎同形的 API（to_tokens/run_with_cache/generate/权重属性），迁移成本刻意压低。

## 2. 内部结构

5614 行按方法簇分六区（唯一有效读法）：
- **构造与别名区**（192-985）：`__init__(model, adapter, tokenizer)`；`boot_transformers`（主加载）与 `boot_native`；别名机制群——`_register_aliases`/`_compute_hook_aliases_cached`/`_scan_existing_hooks` 把原生钩子名（blocks.0.attn.q.hook_out）与 HT 别名（blocks.0.hook_q）双向登记；`hook_dict` 汇总 HookPoint。
- **兼容与权重区**：`enable_compatibility_mode()`（HT 等价数值一键开关）、`process_weights`。
- **tokenizer 区**：与 HT 同名的 to_tokens 群，BOS 与 chat-template 处理增强。
- **权重属性区**（1529-1947）：`stack_params_for` 动态堆叠（异构架构只能按需取）；W_Q…W_out/QK/OV；`tl_parameters` 规范名参数面。
- **前向与缓存区**（2089-3045）：forward 437 行（多模态/seq2seq/causal 分支）；run_with_cache（hook_conversion 保证 HT 形状）。
- **生成与状态区**（3046-5614）：`generate`（619 行）/`generate_stream`/`diffusion_generate`/`hf_generate`（委托保数值）；钩子管理；`state_dict/load_state_dict`（TL 名↔HF 名翻译）。

## 3. 外部连接

上游：ArchitectureAdapter（映射协议）、generalized_components（钩子载体）、component_setup（装配）、StopAtLayerException（截断）、ActivationCache/FactoredMatrix（复用 legacy 分析资产）。下游：model_bridge/__init__ 导出、tools/analysis 双系统工具、benchmarks 对照主线。特殊连接：`__getattr__` 把未定义属性透传给被包装 HF 模型，HF 生态细节无缝可达。

## 4. 数据流

加载流：`boot_transformers`→sources/transformers.py 构造 HF 模型→工厂按 config.architectures 路由→_bridge_builder 翻译 config、探测 BOS 行为→构造 bridge（模型不动）→component_mapping 经 component_setup 挂成具名子模块（桥组件包住 HF 子模块，HookPoint 就位）→别名注册。前向流：tokens→原生 HF 模型逐层计算，桥组件在"进出"处触发钩子（经 hook_conversion 转成 HT 形状）→logits。缓存流与 HT 一致。干预流：add_hook 按别名或原生名命中，返回张量即替换。

## 5. 设计决策

① **包装而非重写**：v3 灵魂决策。权重留在 HF 布局（默认与 HF 逐位一致），可解释性作为外挂层；legacy 的干净权重视图退化为 compatibility_mode 选项。② **双命名+别名注册**：原生名忠实于结构、HT 别名保证存量代码可迁移——兼容成本由库承担。③ **lru_cache 别名计算**：百层×几十钩子的映射构建不便宜，缓存避免重建。④ **__setattr__/__getattr__ 双向定制**：既要拦截 blocks 容器所有权，又要透传 HF 属性——小心"骑"过 nn.Module 注册协议。⑤ **生成三路并存**：自研 generate（可挂钩）、hf_generate（委托保数值）、diffusion_generate——承认一个生成器打天下不现实。

## 6. 新人提示

- 心智模型：**bridge=HF 模型+adapter 映射+钩子外挂**；"行为为什么和 HT 不一样"先查是否没开 compatibility_mode。
- 三行上手：`bridge = TransformerBridge.boot_transformers("gpt2"); logits, cache = bridge.run_with_cache("Hello")`——cache 用法与 HT 一致。
- 读码走三条链：boot_transformers→run_with_cache→add_hook；generate 与 forward 留最后。
- 钩子名 debug 用 `bridge.hook_dict.keys()` 与 `list_hooks()`。
- 改 bridge 的 PR 必查 HT 侧镜像+218 个单测+integration 对拍。
