# tl-hooked-transformer · HookedTransformer.py 精讲（2814 行）

> 目标文件：`transformer_lens/HookedTransformer.py` · 图谱定位：legacy 旗舰，v3 之前的唯一门面，现维护模式但仍是存量研究代码的通用语言。

## 1. 角色定位

HookedTransformer 是"自带全套 HookPoint 的 GPT 风格解码器"：它**重写**了 Transformer 每个组件（而非包装 HF 模型），全按可解释视角组织——权重有规范名（W_Q/W_K/W_V/W_O/W_in/W_out）、激活有统一钩子名（blocks.{i}.attn.hook_q）。一个类覆盖研究者 90% 日常：from_pretrained 加载 70+ 模型、to_tokens、forward、run_with_cache、generate、逐头权重属性。双重身份：对用户是分析工具，对 v3 是"兼容模式的语义基准"——bridge 的 enable_compatibility_mode 复刻的就是它的数值行为。

## 2. 内部结构

单文件单主类（+Output NamedTuple），按行号分区：
- **初始化区**（146-280）：按 config 搭 embed→blocks→ln_final→unembed，组件全来自 components/。
- **tokenizer 区**（751-1064）：set_tokenizer（BOS/device 统一入口）、to_tokens/to_str_tokens/to_single_token、tokens_to_residual_directions（DLA 前置）。
- **前向区**（472-724）：forward 5 个 @overload（str/列表/tokens/tensor）。
- **加载区**（1159-1841，最大块）：from_pretrained 拿权重→load_and_process_state_dict 开关矩阵（fold_layer_norm/center_writing_weights/center_unembed/fold_value_biases）；from_pretrained_no_processing 跳过处理（HF 对齐）；init_weights 四族。
- **钩子开关区**（1842-1898）：set_use_attn_result 等——细粒度钩子按需开启（默认关省内存）。
- **生成区**（1899-2513）：generate（388 行自实现）与 generate_stream。
- **权重属性区**（2514-2760）：约 25 个 @property 堆叠 [n_layers,n_heads,d_model,d_head] 俯视图；QK/OV 返回 FactoredMatrix。

## 3. 外部连接

上游：HookedRootModule（生命周期）、components/（结构组件）、loading_from_pretrained（checkpoint 解析+权重转换）、ActivationCache、FactoredMatrix。下游：`__init__.py` re-export 即公共 API；demos/、ARENA 课程、海量研究代码直接用；evals/patching/head_detector 围绕它的钩子命名工作。与 v3 是"被桥接对象"：双系统工具用 named_parameters（HT）vs tl_parameters（Bridge）适配。

## 4. 数据流

加载流：模型名→loading_from_pretrained（HF config→HookedTransformerConfig；state_dict→weight_conversions 重排）→load_and_process_state_dict（按开关做 LN 折叠等）→组件吃进权重。注意**折叠改变数值**：fold_layer_norm 把 LN 参数吸进相邻线性权重（数学等价、浮点不等价）——legacy 与 HF 有细微差异是设计选择而非 bug。前向流：input→tokenizer→embed(+pos)→逐层 Block（attn 钩子群→resid_mid→mlp 钩子群→resid_post）→ln_final→unembed→logits，每步都有 HookPoint。分析流：run_with_cache 返回 (logits, ActivationCache)，钩子名与权重属性名呼应构成完整词汇表。

## 5. 设计决策

① **重写而非包装**（与 v3 最根本分歧）：换来统一钩子名与规范权重布局，代价是每支持新架构都要手写转换——v3 用 adapter 模式放弃此路线，但 legacy 的"标准词汇表"价值至今无可替代。② **默认折叠权重**：分析干净（消除 LN 干扰项），牺牲 HF 逐位一致。③ **细粒度钩子按需开启**：新手常惑"为什么没有 hook_result"——先 set_use_attn_result(True)；内存与观察粒度的显式权衡。④ **forward 重载群**：字符串直接进模型是"研究像玩"的体现。⑤ **生成自研**：为采样可挂钩，不调 HF generate。

## 6. 新人提示

- 入口三连：`from_pretrained("gpt2")` → `run_with_cache("Hello")` → `cache["blocks.0.attn.hook_pattern"]`。- `model.W_Q` 形状 [n_layers,n_heads,d_model,d_head]，与 `model.blocks[0].attn.W_Q` 同源不同形；只读。
- 想跟 HF 一模一样：from_pretrained_no_processing 或换 TransformerBridge。
- 3.0 后只收 bug fix，新功能去 bridge 侧。
- 读码顺序：set_tokenizer→forward→from_pretrained→权重属性。
