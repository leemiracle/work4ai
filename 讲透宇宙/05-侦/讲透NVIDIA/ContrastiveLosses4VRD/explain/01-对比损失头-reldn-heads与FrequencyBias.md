# 01 · 对比损失头：reldn_heads 与 FrequencyBias

## 角色定位

`lib/modeling_rel/reldn_heads.py`（345 行）是仓名 ContrastiveLosses4VRD 的落点：ReLDN 谓词分类头 `reldn_head`（`reldn_heads.py:22`）+ 三个对比损失变体；`lib/modeling_rel/sparse_targets_rel.py` 提供 `FrequencyBias`（`sparse_targets_rel.py:23`）频率先验。两者共同回答：给定主宾框，谓词怎么分类，如何把"同节点下被错配的谓词"压下去。

## 内部结构

`reldn_head.__init__` 按 cfg 组装四条可选支路：谓词 MLP 分类器 `prd_cls_feats/prd_cls_scores`（`reldn_heads.py:38-43`）；FrequencyBias 查表支路（`reldn_heads.py:45-50`）；28 维空间特征支路（`reldn_heads.py:52-58`）；主宾得分支路（`reldn_heads.py:60-62`）。forward（`reldn_heads.py:78`）把 spo_feat 过 MLP 出 prd_vis_scores（`reldn_heads.py:94-95`），再按开关注入先验：freq_bias 查表 `reldn_heads.py:101`、spt 支路 `reldn_heads.py:103-108`；ADD_SCORES_ALL 时四路相加成 ttl_cls_scores（`reldn_heads.py:116-123`）。

损失侧：谓词交叉熵 `reldn_losses`（`reldn_heads.py:139`）打底；三个对比损失——spo 无差别 `reldn_contrastive_losses`（`reldn_heads.py:150`）、so 感知 `reldn_so_contrastive_losses`（`reldn_heads.py:165`）、p 感知 `reldn_p_contrastive_losses`（`reldn_heads.py:184`），各配 split_pos_neg_* 分组配对函数（`reldn_heads.py:207/233/302`）。分组用 `1 - prd_probs[:, 0]` 取"非背景概率"作正性度量（`reldn_heads.py:209`），组内正例取 min、组外负例取 max（`reldn_heads.py:223-224`），批量用哑样本防空（`reldn_heads.py:211-212`），最终 `F.margin_ranking_loss` 拉开（`reldn_heads.py:155/172/193`）。

## 外部连接

上游被 Generalized_RCNN 调用——`model_builder_rel.py:477-505` 先构造 sbj/obj 两路 spo_feat，再在 `model_builder_rel.py:506-520` 分发三损失。FrequencyBias 数据来自 get_dataset_counts_rel.py 的 get_rel_counts 共现统计，按数据集名归一化（vg/oi/vrd 三分支，`sparse_targets_rel.py:32-39`），must_overlap 由 USE_OVLP_FILTER 决定（`sparse_targets_rel.py:41-44`）。`import nn as mynn`（`reldn_heads.py:14`）来自父仓。

## 数据流

训练前向：RelPN rel blob → spo_feat → reldn_head 六元组返回（`reldn_heads.py:136`）→ `_add_loss` 分发 → 与交叉熵一起回传。FrequencyBias 内部：fg/bg 矩阵 → bg 塞进 fg 第 0 列（`sparse_targets_rel.py:46-47`）→ 对数条件分布（`sparse_targets_rel.py:49`）→ nn.Embedding（`sparse_targets_rel.py:54`）→ rel_index_with_labels 查表（`sparse_targets_rel.py:59-64`）。

## 设计决策

1. **三开关独立而非枚举**：没有 CONTRASTIVE_VERSION 选择子，三个 USE_NODE_CONTRASTIVE_* 布尔（`config.py:454-464`）可叠加——六个主配置 yaml 全部三开（spo 1.0/so 0.5/p 0.1 权重梯度）。
2. **p 感知负例用模型自身检测标签** prd_labels_det（`reldn_heads.py:305`）而非真值——模拟推理期对负例谓词的真实信念，避免 train/test 偏差。
3. so 感知在无同标签负例组时用 USE_SPO_AGNOSTIC_COMPENSATION（`reldn_heads.py:268`）回退全局配对，防长尾分组饿死。
4. spt 特征是 28 维（6+6+6+5+5，boxes_rel.py:65-72），与 `reldn_heads.py:54` 互证——图谱摘要写"20 维"是错的。
5. RUN_BASELINE 模式（`reldn_heads.py:33-36`）直接把 freq_bias softmax 当谓词输出，纯频率基线消融对照。

## 新人提示

按顺序读：`__init__` → forward → `reldn_losses` → 三个 loss → 三个 split_pos_neg_*。重点体会"节点分组"（inds_unique/inds_reverse 来自 RelPN blob）如何把逐样本 loss 变成图结构对比；改 margin 只需动 yaml 的 NODE_CONTRASTIVE_*_MARGIN。`reldn_heads.py:209` 的 `1 - P(background)` 惯例贯穿三个 split 函数。
