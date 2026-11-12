# 02 · 十选择器族巡礼：基线档 vs 模型驱动档

## 角色定位

`data-selection/src/data_selection/selectors/` 的十个选择器是框架的"弹匣"——核心四件套提供枪膛，这里提供可换弹药。README.md:29-40 的表格是官方名录，按依赖天然分两档：**基线档**三个（纯标准库秒级跑通）与**模型驱动档**七个（dataflow 打分器 ×4、dataflex 嵌入算法 ×2、LLM 裁判 ×1，加组合器）。这个梯度即基准方法论：任何花哨策略必须先和 RandomSelector 掰手腕。

## 内部结构

**基线档**。`random_selection.py:8-23` RandomSelector：`random.Random(seed)` 采样，meta 记种子。`source_balanced_random.py:9-50`：按 `source` 字段分桶配额采样——`k // n_sources` 加余数轮转（L28-36），先 `rng.shuffle(sources)` 让余数分配随机。`length_based.py:9-26`：按 extract_text 长度取最长。**勘误：README.md:105 声称有 `strategy="shortest"` 参数，源码不存在**——只有最长一档，文档超前于实现。

**打分器系（依赖 dataflow）**。`perplexity_based.py:14-103`：Kenlm 困惑度三策略——low/high 升降序；`mid` 最讲究（L90-91）：按 `|log(ppl) − log(mean)|` 排序，专挑"不平凡也不垃圾"的中间带。`deita_quality.py:15-114`：quality × complexity **乘积**复合分（L99，DEITA 原配方），逐批缓存。`quality_scorer.py:13-135`：FineWebEdu/PairQual/composite 三策略（L31-32 白名单校验），composite 是 `(e+p)/2`（L120）——与 DEITA 乘积语义不同。`llm_selector.py:13-75`：MetaScorer 多维打分取平均（L48），维度分进 meta。

**嵌入系（依赖 dataflex）**。`embedding_similarity.py:15-137`（NEAR）：目标集三级回退——query_path JSONL（推荐）> domain_proxy_text 单句 > 候选自相似（L84-98）；排序取**质心余弦**而非 top 邻居：目标嵌入均值归一化后与候选矩阵点积（L117-122），所有目标样本共同贡献方向。`diversity_kcenter.py:15-83`（TSDS）：KDE+FAISS 的贪心 k-center，概率向量 `argsort(-probs)` 取前 k（L69），`max_K=min(5000, max(n,2k))`（L62）。两者共享 `max_chars=2000` 截断——注释（embedding_similarity.py:51-55）写明：SentenceTransformer 按 batch 最长序列 padding，注意力 O(L²)，几条 12k 字符样本就打爆显存。

**组合器**。`composite.py:9-24`：前一个输出作下一个输入顺序过滤（L20-24）。

## 外部连接

打分器系 import `dataflow.operators.eval`（Perplexity/Deita/FineWebEdu/PairQual/MetaScorer），嵌入系 import `dataflex.offline_selector`（near/tsds），两包随 uv 环境装、不在本仓。dataflow 系接口统一 `scorer.eval(df, input_key=...)` 吃 DataFrame，故各选择器都有 pd.DataFrame 转换与 text_key 缺列补列逻辑。每选择器在 examples/ 有同名示例。

## 数据流

三类形态：打分系——批量组 DataFrame → 外部打分器 → ScoreCache 逐批落盘 → 汇总排序截 k；嵌入系——extract_text 写 Alpaca JSON 进临时目录（`_write_alpaca_json`，tempfile 包裹）→ DataFlex 落地执行 → 概率/相似度回读排序；基线系内存直排。共同出口：`{**s, "meta":{...}}` 交 runner 落盘。

## 设计决策（含批判）

1. **外部算法当库调用而非重写**：NEAR/TSDS/DEITA 引用原实现保证与论文对齐；代价是嵌入系走"写临时文件→外部库读回"边界，调试看不见中间态。
2. **LLMAsSelector 静默降级是坑**：llm_selector.py:49-51，scorer 为 None 不报错而退化为**按词数排序**——以为在跑 LLM 裁判，实际在跑长度选择器，只有 meta 能看出。构造时务必传 scorer。
3. **llm_selector.py:58 的 `samples.index(s)` 是 O(n²)**，且重复样本 dict 相等时都命中第一个下标，维度分数会错位。
4. **CompositeSelector 的 k 是摆设**：构造收 k（L15）但 select 不用（L20-24），实际截断量由链上最后一个选择器决定；也未设 `_score_based`，多 k 退化为逐档重跑。
5. 两档梯度让"策略增益"可归因：任何模型驱动档的提升都能折算成打分成本值不值。

## 新人提示

先跑 examples/random.py 建立基线直觉，再读 deita_quality（打分系模板）与 embedding_similarity（嵌入系模板，重点三级回退与 max_chars 注释）。动手任务：为 LengthBasedSelector 补上 README 承诺的 strategy 参数；组"QualityScorer 前 5 万 + DiversityKCenter 前 1 千"并解释顺序合理性。
