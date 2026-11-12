# 03 · Mixer / Weighter / Reorder：配比、加权与排序三族巡礼

## 角色定位

这三族覆盖数据为中心训练的另三种干预维度：Mixer 管**域级配比**（下一区间各领域抽多少）、Weighter 管**样本级损失加权**（样本不换、loss 乘系数）、Reorder 管**训练顺序**（数量与权重都不动，只排课程）。三族与 Selector 构成四大组件族，注册装配同源（见第 1 篇）。

## 内部结构

**Mixer 五实现**（契约 `base_mixer.py`：持有 mixture_manager，`mix(model, step_id)` 返回域比例向量）：
- `static`：固定比例或均匀（static_mixer.py:7）。
- `random`：固定 seed 生成一次比例反复用（random_mixer.py:14-20，不是每步重掷）。
- `doremi`：Algorithm 1 落地。超额损失 **token 级先 clamp 再平均**：`excess = clamp(proxy − ref, min=0)`（doremi_mixer.py:163-202）；域权重更新前减均值再 clip ±5 防爆炸（:203-217）；关键语义：`mix()` 返回 **uniform 采样比例**而真实权重 α_t 走损失加权（:218-253）——采样与加权两分离，正是论文原意。
- `odm`：Exp3 变体，核心公式 `R̂_t = α·R̂_{t-1} + (1−α)·(reward/π_{t-1})`，源码注释明言"用移动平均替代累计和是 ODM 对标准 Exp3 的关键差异"（odm_mixer.py:139-174）；探索率 `ε_t = max{min_eps, min{1/K, √(lnK/(Kt))}}` 带退火下限（:80-90）；指数项减最大值再 clip [−5,0] 防溢出（:109-111）。
- `dynamic_moe`：按 MoE gate loads 估均衡度调比例（dynamic_moe_mixer.py:28）。

**Weighter 七实现**（契约 `base_weighter.py`：抽象 `get_weighted_loss`，`training_step` 全托管前向/加权/反传）：`loss`（ICLR'25 动态重加权，linupper 等四策略，loss_weighter.py:15）、`adapt`（锚向量余弦）、`joint_update_aware`（解 `max_w s^Tw − (β/2)w^TSw + τH(w)`）、`custom`，加多模态三件——本族的公式密集区：multimodal_loss 单前向 `s = L(R|Q,I)`；multimodal_deltaloss **双前向** `s = L(R|Q) − L(R|Q,I)`（把视觉 token 删掉再前向一次，multimodal_deltaloss_weighter.py:1-6、:174、:217）——加图后 loss 降得越多越依赖视觉、权重越高；multimodal_adapt 与锚集余弦。三件共用打分管线：全池打分→分位截断→min-max 到 [−δ,δ]→linupper→exp→均值归一（:182-199 `_score_to_weight`），token/sample 归约可对齐 HF 口径（:113-117）。

**Reorder**：patterns.py 移植自 microsoft/data-efficacy 的七种排序模式（`_DISPATCH` patterns.py:261-269：shuffle/sorting/folding/zigzag/segment/stair/saw，对应论文 G1-G4 指引）。三个正交轴：pattern（怎么排）、score_source（分数从哪来：precomputed/model_loss/model_perplexity/cached，score_provider.py:1-19）、apply_at（raw 预处理前排原始行 / index 训练期按索引排）。极性协议 `POLARITIES` 统一"高分在后还是在头"，接受 higher_is_better 别名（base_reorder.py:24-26）。**两处刻意改进**：①过渡区重叠时上游静默用 cursor clamp 合并，这里改为直接报错（patterns.py:139-141）；②SEG 参考实现写死升序、这里让 `ascending` 全模式统一生效（:237 注释）。

## 外部连接

Mixer 由 MixTrainer 驱动、靠 `mixture_manager` 重建混合快照；Weighter 由 WeightTrainer 在 `training_step` 委托（weight_trainer.py:37-46）；Reorder 由 ReorderTrainer 经 `_ReorderAsSelector` 适配器复用 SelectTrainer 循环（第 4 篇）。三族又都能作为 lego 管线的积木（第 5 篇）。

## 数据流

Mixer 边界返回比例→mixture_manager.set_proportions+rebuild 快照（DoReMi 例外：返回 uniform，权重走 compute_loss）。Weighter 每 step 拿 `(losses, ctx, model, inputs)` 出加权标量。Reorder 静态路在 raw 行排一次序由数据加载透传，动态路每边界用当前模型对剩余样本打分重排（consume_once 保单轮语义，components.yaml:496-532）。

## 设计决策（含批判）

DoReMi 的 token 级 clamp 顺序（先截断再平均）直接决定算法行为，源码注释钉死；ODM 的移动平均对非平稳 loss 更稳，但 reward_scale=15 的手调放大系数未见消融。Reorder 的 dynamic 预设用 loss 当"难度"而非论文的"质量分"，components.yaml:495 注释诚实声明"要对齐论文数字请用 static 预设配真实质量分"。批判：RandomMixer 固定 seed 使每步输出相同，等价于一次随机固定比例；multimodal 三件的全池打分成本随数据集线性增长，refresh_interval 是唯一成本阀门。

## 新人提示

从 components.yaml 的 reorders 注释块（:349-371）入门最快——三轴+极性+window_size 语义全在注释里。跑 DoReMi 必须走三步链（第 6 篇），单跑 step2 缺参考模型直接报错。改 weighter 先读 base_weighter.training_step 的防呆检查，理解 `use_weighter=False` 暖身语义再动公式。
