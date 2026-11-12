# TransformerLens ONBOARDING · 机制可解释性导览

> 依据：知识图谱 commit `2a05c15`（4507 节点/10361 边/14 层/14 步导览）+ 源码。版本：3.x（v3=TransformerBridge，legacy=HookedTransformer）。

## 1. 项目总览

TransformerLens 是**机制可解释性（mech interp）**研究的 PyTorch 库，Neel Nanda 创建、Bryce Meyer 维护，使命是对语言模型做**逆向工程**：不问"模型输出什么"，而问"内部哪段算法产生了这个输出"。原生 HF transformers 是黑盒——拿得到 logits，拿不到第 3 层第 7 个头的注意力模式，更无法干预激活做因果观察。本库补上缺口，哲学是"让研究像玩"（短反馈环）。

四大能力：①**激活访问**——每个头/每层 MLP/残差流位置皆可经 HookPoint 挂钩；②**激活干预**——编辑/消融/替换激活做因果实验；③**模型加载**——v3 支持 9,000+ HF 模型、50+ 架构族；④**分析工具**——patching/logit lens/DLA/SVD 开箱即用。

最重要的全局认知是**双系统并存**：`TransformerBridge`（v3，新默认）直接包装 HF 模型加钩子，权重保持原生数值；`HookedTransformer`（legacy，3.0 起维护模式）自带重写组件，加载时折叠 LN+中心化权重（数学等价但数值不与 HF 对齐）。两系统共享 hook 机制与分析词汇，官方要求行为变更镜像同步。

## 2. 架构分层说明（14 层）

```
   用户研究代码 / demos
          │
 ┌────────┴─────────────┐
 │ v3: TransformerBridge │←包装 HF 模型
 │ legacy: HookedTransformer│←自带组件
 └───┬─────────┬────────┘
 Adapter 协议   components/
 141 适配器+工厂      │
 generalized_components─┤
      │              │
      └hook_points.py─┘
       (全库基石)
          │
 ActivationCache│patching/evals
          │
 HuggingFace transformers
```

| # | 层 | 节点 | 职责 |
|---|---|---|---|
| 1 | legacy-core | 38 | 四大 Hooked 模型+components/ 22 组件+加载入口 |
| 2 | activation-cache | 5 | ActivationCache（29 方法）/FactoredMatrix/KV 缓存 |
| 3 | transformer-bridge | 26 | Bridge 主类/Adapter 协议/sources 模型源 |
| 4 | architecture-adapters | 142 | 141 适配器+157 项注册表 |
| 5 | generalized-components | 52 | 47 个桥组件，fan-in 第一 |
| 6 | weight-conversion | 50 | 12 转换原语+家族权重重排 |
| 7 | analysis-tools | 26 | patching/evals/SVD/head_detector |
| 8 | benchmarks | 21 | 九 Phase 基准（HF 对照/多模态等） |
| 9 | utilities | 39 | 设备/激活函数/tokenize 等 |
| 10 | model-registry | 5 | HT 与 Bridge 双注册表 |
| 11 | tests | 544 | unit 329/integration 173/acceptance 27 |
| 12 | demos | 35 | 33 个教程 notebook |
| 13 | documentation | 43 | Sphinx 源/模型表/adapter 指南 |
| 14 | build-ci | 34 | Actions/makefile/pyproject |

依赖自上而下：研究代码→门面→适配器/组件→hook→HF；缓存与分析工具横切各层。

## 3. 核心模块

**legacy 四大件**：`HookedTransformer.py`（2814 行）——from_pretrained/run_with_cache/generate/逐头权重属性/QK-OV；`components/`——AbstractAttention 统一 QKV/rotary/掩码/KV cache，mlps/ 含 GatedMLP 与 MoE；`loading_from_pretrained.py`（2323 行）——30+ HF config 翻译+权重重排；`HookedRootModule.py`——run_with_hooks/run_with_cache 根实现。

**hook_points.py（451 行，全库基石）**：HookPoint 是 forward 恒等的哑模块，包住任何激活即成挂钩位；LensHandle 记录永久性与 context_level。灵感来自 Anthropic 的 Garcon。

**ActivationCache.py（1578 行，29 方法）**：全部激活的 dict 容器+分析工作台——accumulated_resid（logit lens）/logit_attrs（DLA）/get_full_resid_decomposition。

**v3 三件套**：`bridge.py`（5614 行，128 方法）——boot_transformers 挂 HF 模型不复制权重，注册原生钩子+HT 别名，enable_compatibility_mode() 一键 HT 等价数值；`architecture_adapter.py`——component_mapping+能力开关；`supported_architectures/`141 文件+工厂路由。

**支撑**：权重转换 12 原语、model_registry（9,000+ 模型单一事实来源）、benchmarks 数值对照。

## 4. 关键概念（14 个）

1. **HookPoint**：恒等哑模块即观察点——不改数学，只开"测孔"。
2. **HookedRootModule**：hook 生命周期根类；setup() 给 HookPoint 命名，layer() 解析层号。
3. **add_hook/add_perma_hook**：临时（run 后清理）vs 永久（跨 run，steering 用）；context_level 支持嵌套。
4. **run_with_cache**：一次前向缓存全部激活返回 (logits, cache)。
5. **ActivationCache 双索引**：cache["pattern",0] 与 cache["q",0,5]（层/头简写）。
6. **logit lens**：accumulated_resid 看中途残差流的预测演化。
7. **activation patching**：clean/corrupt 互换激活定位因果组件；源自 ROME。
8. **FactoredMatrix**：A·B 低秩积，不显式相乘算 norm/SVD/切片——OV 分析标配。
9. **QK/OV 分解**：QK="找什么"、OV="做什么"——circuits 理论的操作化。
10. **Adapter 模式**：adapter 只声明映射，Bridge 自动装配；新增架构=新增声明文件。
11. **双系统数值**：legacy 折叠 LN+中心化（不匹配 HF）；v3 原始权重（bit 级对齐）。
12. **hook 命名双轨**：HT canonical（hook_resid_pre）vs Bridge 原生（attn.q.hook_out）+别名。
13. **注册表**：HT 用 supported_models.py；Bridge 权威=supported_models.json。
14. **stop_at_layer**：抛 StopAtLayerException 截断前向，逐层 probing 省半算力。

## 5. 推荐学习路径（14 步导览改写）

1. 读 README：为什么逆向工程 Transformer。
2. `__init__.py`：barrel=全库 API 地图。
3. hook_points.py+HookedRootModule.py："一切激活皆可干预"。
4. HookedTransformer+components/：forward 主链，每块积木可单独 hook。
5. 配置：HookedTransformerConfig vs TransformerBridgeConfig。
6. ActivationCache+FactoredMatrix：练索引与 logit lens。
7. 分析工具箱：跑 patching、induction loss、head_detector。
8. v3 入口 bridge.py：boot_transformers+Adapter 协议。
9. generalized_components：适配器的积木库。
10. 适配器体系：精读 gpt2/llama/qwen2，看工厂路由。
11. 权重转换三层协作。
12. 模型注册表：单一事实来源。
13. 测试体系：test_match_huggingface 对拍=金标准。
14. 回 demos/：Main_Demo 全流程收官。

## 6. 文件地图（按层精选）

**层1 legacy**：HookedTransformer.py；HookedEncoder/HookedEncoderDecoder/HookedAudioEncoder.py；HookedRootModule.py；loading_from_pretrained.py；components/（attention/abstract_attention/transformer_block/pos_embed/mlps 三种）。
**层2 缓存**：ActivationCache.py；FactoredMatrix.py；cache/key_value_cache.py。
**层3 v3 核心**：model_bridge/（bridge/architecture_adapter/component_setup/compat）；sources/（transformers.py 主加载/_bridge_builder/native）。
**层4 适配器**：supported_architectures/ 的 gpt2（入门）/llama/qwen2（Qwen 系基类）/deepseek_v3/glm4_moe/gpt_oss/jamba（混合）/mamba2/rwkv7/llada（扩散）/hubert（音频）等 141 个；factories/architecture_adapter_factory.py。
**层5 通用组件**：generalized_components/ 的 base/attention（937 行）/block/mlp_bridge/moe/moe_router/ssm2_mixer/rms_normalization/rotary_embedding 等 47 个。
**层6 权重转换**：conversion_utils/conversion_steps/（12 原语）；param_processing_conversion.py；pretrained/weight_conversions/（gpt2=Conv1D 转置）；weight_processing.py。
**层7 分析**：patching.py；evals.py；SVDInterpreter.py；head_detector.py；tools/analysis/ 与 tools/model_registry/ 两目录。
**层9 工具**：utilities/ 的 devices/multi_gpu/activation_functions/tokenize_utils/slice/quantization/exploratory_utils（test_prompt）。
**层10 注册表**：supported_models.py（HT）；supported_models.json（Bridge 权威）。

## 7. 复杂度热点

| 热点 | 规模 | 策略 |
|---|---|---|
| bridge.py | 5614 行/128 方法 | v3 枢纽，按方法簇读 |
| HookedTransformer.py | 2814 行，forward 5 重载 | 权重处理需 LN 代数，先读加载与缓存链路 |
| loading_from_pretrained.py | 2323 行 | 30+ 架构 if-else，当查询表 |
| ActivationCache.py | 1578 行/29 方法 | 维度跟踪是最大坑，先背形状表 |
| architecture_adapter.py | 1135 行 | 抓 mapping/weights/capability 三主线 |
| generalized_components/attention.py | 937 行 | 配测试对照读 |

横切提醒：双系统行为镜像同步是 PR 硬规则；transformers>=5.4 的版本 bump 会打断 component-mapping，是真实测试关口。

## 8. 与生态关系

**上游**：HF transformers（模型来源）、PyTorch（hook 语义）；HookPoint 灵感来自 Anthropic 的 Garcon（README 致谢 Chris Olah）。

**Neel Nanda 研究生态**（本库是基础设施）：transformer circuits 实证（ICLR'23 Spotlight, arXiv:2301.05217）、Sparse Probing（2305.01610）、自动电路发现 ACT（2304.14997）均用它完成；配套 ARENA 教程、200 Concrete Open Problems。

**vs nnsight**：nnsight 走"追踪任意模型执行图"的通用干预路线；本库走"电路分析专用词汇表"路线——cache/logit lens/QK-OV 开箱即用；v3 正吸收其"不重写模型"优点。

**vs CircuitsVis**：配套可视化组件库，TL 产生活化、它渲染，互补非竞争。

**vs ecco**：更早的探索工具，偏整体归因可视化；TL 以细粒度因果干预胜出，成为社区事实标准。

**下游**：ARENA 课程、ACT 等自动电路发现工具链、大量 mech interp 论文以本库为底座。

---

📌 **下一步**：跑 demos/Main_Demo.ipynb → test_prompt 玩小模型 → 按 explain 五篇逐个深入。
