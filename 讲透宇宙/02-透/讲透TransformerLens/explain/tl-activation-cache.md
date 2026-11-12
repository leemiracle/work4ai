# tl-activation-cache · ActivationCache.py 精讲（1578 行）

> 目标文件：`transformer_lens/ActivationCache.py` · 图谱定位：激活缓存层中枢，"run_with_cache 之后一切分析"的数据底座，docstring 自称"at the core of Transformer Lens"。

## 1. 角色定位

ActivationCache 是一次前向中**所有钩子点激活的字典容器 + 分析方法集**。mech interp 标准工作流"先缓存、后分析"：run_with_cache 把激活按名存进来，之后的一切——logit lens、直接 logit 归因（DLA）、残差分解、逐头堆叠——都在这个对象上完成，无需再跑模型。29 个方法让它从 dict 包装器升格为研究工作台。双系统通用：legacy 与 v3 的 run_with_cache 都返回它（Bridge 侧由 hook_conversion 保证形状对齐）。同层还有 FactoredMatrix 与 cache/ 的 KV 缓存。

## 2. 内部结构

29 方法分五组：
- **容器基础**：`__init__(cache_dict, model, has_batch_dim)`；`__getitem__` 双语法——全名 `cache["blocks.0.attn.hook_q"]` 与简写 `cache["q", 0, 5]`（层/头号）；keys/values/items；`remove_batch_dim`、`apply_slice_to_batch_dim`（自定义 Slice）；`to`；`toggle_autodiff`（关梯度省内存）。
- **logit lens 族**：`accumulated_resid(layer, apply_ln, pos_slice)`——截至 layer 的残差累加，可选过 final LN，看"中途预测"。
- **归因族**：`logit_attrs`（分量投影到目标 logit 方向，DLA 主力）、`decompose_resid(mode="attn"/"mlp"/"all")`、`get_full_resid_decomposition`（逐头+逐神经元最细粒度）、`apply_ln_to_stack`。
- **堆叠族**：`stack_head_results`、`stack_activation`、`compute_head_results`（z×W_O）、`get_neuron_results`/`stack_neuron_results`。
- **SSM 族**（v3 新增）：`ssm_layers`、`compute_ssm_effective_attention`（SSM 状态拟成"等效注意力矩阵"）、`compute_ssm_state`——让 Mamba 层也能用注意力词汇分析。

## 3. 外部连接

上游：由 HookedRootModule/TransformerBridge 的 caching hooks 填充；`model` 参数反指模型对象，用于取 ln_final/unembed/cfg（这是它能 apply_ln/project 的原因）。下游是分析工具层：patching.py 的干预位置、direct_logit_attribution、head_detector 都直接吃 cache；demos 的 Exploratory_Analysis_Demo 整篇围绕它。docstring 警告：为"全量缓存 HookedTransformer/Bridge"设计，部分方法在缺项缓存或外来模型上会断。

## 4. 数据流

创建流：run_with_cache 给每个钩子注册 caching hook，前向结束按钩子名收进 dict。消费三主线：①logit lens——`accumulated_resid(apply_ln=True)`→乘 W_U→每层中途 logits；②DLA——`decompose_resid` 得分量栈→`logit_attrs(方向=答案 token 的残差方向)`→argmax 找最负责分量（docstring 的 chicken→road 例定位到 3_attn_out）；③堆叠——`stack_head_results(apply_ln=True)` 做逐头输出的可加分解（残差流线性叠加假设的操作化）。维度跟踪是隐形主线：头拆分张量 [batch,pos,head,d_head] 与残差张量 [batch,pos,d_model] 两族形状贯穿所有方法。

## 5. 设计决策

① **缓存与模型分离**：cache 持 model 引用不持权重，分析完可丢，内存可控。② **双索引语法**：`["q",0,5]` 的层/头元组索引比记 30 字符钩子名友好得多——研究交互的重大效率优化。③ **apply_ln 参数化而非内置**：看 logit 必须加 LN、看残差演化别加——语义选择交给用户而非库。④ **批维鲁棒性承诺**：remove_batch_dim 后所有方法仍工作，类型注解专门定义 batch_and_pos_dims 三形态。⑤ **SSM 等效注意力**：承认"注意力词汇"是社区通用语，给 SSM 造等效量也不逼研究者换语言——概念层的兼容设计。

## 6. 新人提示

- 背 docstring 形状表（q/k/v/z=[batch,pos,head,d_head]，pattern=[batch,head,query,key]，resid 族=[batch,pos,d_model]）——官方自述"最大 footgun 是索引与维度"。
- `cache["pattern",0]` 等价全名；`"q",0,5` 再深到头。
- logit_attrs 的 directions 用 `model.tokens_to_residual_directions(answer_token)` 取，答案是**下一个** token。
- 这层 API 双系统已统一，学一套用两处；docstring 例子自带 doctest，tiny-stories-1M 上跑一遍最快上手。
