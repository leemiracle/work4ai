# tl-adapter-system · ArchitectureAdapter 体系精讲

> 目标文件：`model_bridge/architecture_adapter.py`（1135 行）+ `model_bridge/supported_architectures/`（141 文件）+ `factories/architecture_adapter_factory.py`（157 项注册表）· 图谱定位：v3 "9,000+ 模型支持"的实现现场。

## 1. 角色定位

适配器体系是 v3 的"巴别塔方案"：每个 HF 架构族一个 adapter 文件，把 HF 模块路径**声明式**映射到 TransformerLens 规范名，Bridge 据此自动装配钩子。基类定义协议（component_mapping+权重转换+能力开关），141 个子类只做声明不写逻辑，工厂按 HF config 的 architectures 字段路由。这兑现了 v3 核心承诺：新增模型家族=写一个几百行映射文件+四点注册（adapter 文件/注册表/包导出/integration 对拍），核心零改动。全库 fan-in 季军（116 处引用）。

## 2. 内部结构

**基类四组能力**（1135 行）：
- **映射声明**：`components` property 返回 ComponentMapping（HF 路径→TL 规范名，如 transformer.h.0.attn→blocks.0.attn）；`_gated_mlp/_ungated_mlp` 辅助构造；`_reprefix_components` 改前缀复用；`_canonical_layer_types` 识别混合架构层型序列（attention/mamba/moe…）。
- **权重翻译**：`preprocess_weights`（加载前重排）、`_qkvo_weight_conversions`（GQA/融合矩阵处理）、`convert_hf_key_to_tl_key`/`translate_transformer_lens_path`（双向键名翻译）。
- **能力开关**：`supports_generation/kv_cache/batched_generation`——adapter 如实申报本架构能做什么，bridge 据此降级。
- **生命周期**：`prepare_loading`（下载前）/`prepare_model`（模型到手后）/`create_stateful_cache`/`setup_component_testing`（基准装配）。

**141 个子类的光谱**：gpt2.py 最简（几十行）；qwen2.py 处理硬编码 q/k/v 偏置并充当 Qwen 系基类；deepseek_v3/glm4_moe/gpt_oss 代表 MoE；jamba/nemotron_h 注意力+Mamba 混合；rwkv7/mamba2 免注意力；llada 掩码扩散；hubert 音频。**工厂**：注册表 157 项，支持外部注册与 entry-point 发现——第三方包不进主仓也能注册新架构。

## 3. 外部连接

上游：TransformerBridgeConfig、generalized_components 全家（映射目标端全是桥组件）、conversion_utils 的 12 种转换步骤。被 bridge.py 的 boot/generate/state_dict 全链路消费；tools/model_registry 的 verify_models 是适配器的考官；tests 的 helpers.py（被引 77 次）是对拍共享设施。supported_architectures/AGENTS.md 专门立规：按架构族写、四点注册、新适配器必带 HF logits 对拍。

## 4. 数据流

注册流：adapter 子类→加入 SUPPORTED_ARCHITECTURES→包 __init__ 导出。加载流：boot_transformers 拿 HF config→工厂查表实例化 adapter(cfg)→components 交 component_setup 递归挂载（HF 子模块被桥组件包住，HookPoint 注入）→preprocess_weights 在权重加载前跑转换→bridge 诞生。运行流：前向时 HF 模块照常计算，桥组件钩子按 TL 规范名触发；能力开关决定 generate 走自研还是 hf_generate。对拍流：setup_component_testing 装配基准输入→与 HF 原始输出对照→结果写进 model_registry 的 VerificationRecord，验证历史永久留痕。

## 5. 设计决策

① **声明式映射优于命令式接线**：adapter 是数据（映射表）而非代码，评审新适配器=检查一张表。② **按架构族而非模型粒度**：gpt2.py 覆盖全部 GPT-2 变体，避免 9,000 模型 9,000 文件。③ **能力开关诚实申报**：没有 kv_cache 就明说，比运行时神秘崩溃研究友好。④ **工厂可外部扩展**：entry-point 让闭源/私有架构不必进主仓。⑤ **映射与测试强绑定**："带 HF 对拍"写进官方 Done checklist——逆向工程库对正确性的执念在流程层落地。

## 6. 新人提示

- 学写 adapter：精读 gpt2.py（最简）→qwen2.py（偏置语义）→jamba.py（混合层型），对照 docs/source/content/adapter_development/ 指南。
- 调映射 bug 用 `adapter.get_component_mapping()` 打印、`convert_hf_key_to_tl_key` 单测某键名。
- 隐性大坑是 transformers 版本：HF 小版本重命名模块会打断映射。
- 混合架构先看 `_canonical_layer_types`——层型序列决定哪些分析 API 可用（SSM 层没有 pattern 钩子但有 ssm_state）。
- 141 个文件"读一个懂一族"，当查询表用。
