# 精讲 03：star_attention/modeling_llama.py — HF Llama 的星注意力注入层

## 角色定位

718 行的 modeling_llama.py 是整个仓库的"缝合层"：把 transformers 4.44 的 Llama 实现整树拷贝，仅把 flash_attention_2 槽位的注意力头换成 `StarLlamaFlashAttention2`（:74），让任意 HF Llama checkpoint 零训练获得两阶段分布式注意力。model.py:33 的 `from star_attention import LlamaForCausalLM`（经 star_attention/__init__.py:16 re-export）落到这里。

## 内部结构

四个类自底向上：① `StarLlamaFlashAttention2(LlamaFlashAttention2)`（:74-200）——唯一实质改动点；② `LlamaDecoderLayer`（:210-292）标准结构，但 forward 签名加 `num_ring_steps/enable_star_attn`（:232-233）并透传给注意力头（:272-274）；③ `LlamaModel`（:295-519）同样透传（:419-421）；④ `LlamaForCausalLM`（:522-718）收口 forward（:565-566 签名、:600-613 下传）。装配开关在模块级字典 `LLAMA_ATTENTION_CLASSES`（:203-207）：eager/sdpa 用 HF 原类（:204/:206），flash_attention_2 映射到星头（:205），DecoderLayer 按此实例化（:216）。

## 外部连接

上游 import 自 transformers.models.llama.modeling_llama 的九个符号（:49-59，权重结构零改动的基础），下游依赖本仓分发层 `_flash_attention_forward`（:62 import，:179-192 调用并传 num_ring_steps/enable_star_attn）。模块级副作用是最显眼的外部约束：import 时就读 `dist.get_rank()`（:67-69），dist 未初始化直接 RuntimeError（:71）——所以 star/ring 必须 torchrun 起进程后才 import 模型。

## 数据流

星头 forward（:81-200）关键四步：① 不变式检查——enable_star_attn 时非最后 rank 不得带非空 KV（:100-105）；② 投影+RoPE 照旧（:111-132）；③ KV cache 分叉：星模式且非最后 rank 时 key/value **被旧 cache 替换**而非追加（:136-137），其余情况正常 update（:138-143）——保证 query 只在最后 rank 写入；④ 注意力计算整体委托分发层（:179-192）。生成的 `prepare_inputs_for_generation` 也补了两个参数的 kwargs 透传（:714-715，num_ring_steps 缺省 -1），但本仓手写生成循环（model.py:130）不走这条 generate() 路径。

## 设计决策与权衡

① **整树拷贝而非 monkey-patch**：718 行里 700 行是 HF 4.44 原文，换来"版本钉死但行为完全可预期"——transformers==4.44.0（requirements.txt:5）之外任何版本都可能漂移。② **替换头而非子类化模型**：只动 LLAMA_ATTENTION_CLASSES 一个字典（:203），DecoderLayer/Model/CausalLM 的改造纯粹为了把两个 kwargs 穿 26 层传到头。③ **不变式前置**：:100-105 把"只有最后 rank 有新 KV"从约定变成硬检查，配对 model.py:141-142 的写端。④ eager/sdpa 保留原类（:204/:206）：不带分布式参数跑普通推理仍可用，退化路径完整。

## 新人提示

读这个文件别按顺序读：先 :203-207（装配点）→ :74-105（星头差异）→ :134-143（KV 分叉，全文件最核心的 10 行）→ :179-192（出口）。排查"为什么我的 transformers 版本报错"时，看 :45-59 import 的符号（如 `prepare_fa2_from_position_ids` 在 modeling_flash_attention_utils.py:35 来自 transformers.modeling_flash_attention_utils，4.44 之后路径多次变动）。改 Blockwise 细节时记得 :100-105/:136-137/:141-142 与 model.py 三处是一组不变式，动一处要同步动三处。

（锚点 18 个：modeling_llama.py:49/62/67/71/74/100/105/134/136/141/179/203/205/210/216/295/419/522/565/600/714，均 @dadb4be9 核实）
