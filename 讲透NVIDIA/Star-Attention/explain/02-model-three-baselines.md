# 精讲 02：model.py — Star/Ring/Dense 三基线编排中心

## 角色定位

model.py（395 行）是论文对照实验的代码形态：一个分布式基类 + 三种注意力策略实现，供 run_star_attn_inference.py:64-105 按 `--attn_type` 装载（:72 dense / :81 ring / :90 star）。所有评测入口（RULER/BabyLong/自定义数据）最终都落到这三个类的 `__call__(prompt_context, prompt_query)`。

## 内部结构

`DistributedInferenceBaseModel`（:24）管公共设施：tokenizer（:38）、模型装载（:41-47，bfloat16 + flash_attention_2 + device_map auto）、GPU 按 rank 切分（:67-72，每 rank 独占一段显存配额）、贪心生成循环 `_generate_output`（:118-153）、输出清洗 `_get_output_text`（:155-168，truncate 前缀 + stop_words 截断）。两个抽象方法 `_tokenize_and_partition_context`（:93）与 `_process_blockwise_context`（:104）由子类填。`StarAttentionModel`（:174）与 `RingAttentionModel`（:269）继承它；`DenseAttentionModel`（:337）是**独立类不继承**（:339 构造器自带 AutoModelForCausalLM :343）。

## 外部连接

对上：run_star_attn_inference.py 按名导入（:73/:82/:91），scripts/time_inference.py:59-90 同样三分支。对下：唯一的模型出口是 `from star_attention import LlamaForCausalLM`（:33）——Phase 1 传 `num_ring_steps=0, enable_star_attn=False`（:220-221）走局部，Phase 2 传 `enable_star_attn=True`（:137）走星核；Ring 则 `num_ring_steps=-1`（:302）启用完整环形。Dense 绕开本仓一切改造，直接 transformers 原生（:343-349）。

## 数据流

Star 主线（:240-266）：上下文 tokenize → block_size 缺省=ctx/world_size（:183-184）、pad 到块整数倍（:187-189）→ `tensor_split` 按世界数分块（:245-248）→ Phase 1 逐块算 KV：从第二块起前拼 anchor 段（:209-213，缺省=整个第一块 :199-200），算完丢弃 anchor 段 KV（:225-228）、块间拼接（:230-236）→ 末 rank 去除 padding KV（:252-257）→ Phase 2 query 从 ctx_len 起算位置（:260-262）进入生成循环；循环内**只有最后 rank 更新 KV**（:141-142）——最后一 rank 即 query host。Ring 主线（:308-334）对称差异：pad 到世界数整数倍（:281-283）、每 rank 恰一块（断言 :293）。Dense 最简单：context+query 拼整条（:389）。

## 设计决策与权衡

① **Phase 2 复用**：Ring 类注释明说"augmented with Phase 2 of Star Attention"（:270）——环注意力只换来 Phase 1 的精确 KV，生成阶段同样走星式合并，保证三基线只在 Phase 1 有差异。② **anchor 前缀化**：anchor_block_size 显式传入时只取 c₁ 的前缀（:210 切片），缺省整块——论文超参扫描即靠这两参数。③ **贪心解码手写循环**（:130-151）不用 model.generate()，绕开 KV cache 接口在分布式下的坑。④ stop_words 用 split 截断（:165-166）而非 logits 拦截，简单但可能截过头。

## 新人提示

调试入口选 `StarAttentionModel.__call__`（:240），沿 :251 Phase 1 → :262 Phase 2 读最快。三个高频疑惑的答案都在细节里：为什么单卡跑不了 star——`_init_distributed` 直接 raise（:80）且要求 torchrun 环境；为什么非最后 rank 不写 KV——:141-142 与 modeling_llama.py:136-137 是同一不变式的两端；`--use_cache` 断点续跑按样本 index 去重（run_star_attn_inference.py:51-61），重跑时输出文件追加模式（:148）。另外注意 Dense 类不走分布式基类，-np 多进程跑 dense 会各自独立加载整模型。

（锚点 24 个：model.py:24/33/38/41/67/80/93/104/118/137/141/174/183/187/199/209/220/225/245/252/269/281/293/302/337/343/389 等，均 @dadb4be9 核实）
