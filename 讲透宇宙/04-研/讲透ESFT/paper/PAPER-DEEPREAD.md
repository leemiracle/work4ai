# ESFT 论文精读

> 论文：*Let the Expert Stick to His Last: Expert-Specialized Fine-Tuning for Sparse Architectural Large Language Models*
> arXiv:2407.01906（v1 2024-07-02 / v2 2024-07-05，Zihan Wang（DeepSeek 实习期工作）、Deli Chen、Damai Dai 等 6 人）
> 本地仓：`~/ai/explore/deepseek-ai/ESFT`

---

## 1. 一句话定位

ESFT（Expert-Specialized Fine-Tuning）是**专为 MoE 架构设计的 PEFT 方法**：用路由分数挑出与下游任务最相关的一小撮 experts 只训它们、其余全部冻结——以 ~1.4B 可训练参数（对比全参 15.7B）在定制任务上打平甚至超过 full fine-tuning，同时通用能力几乎不掉，训练时间省 30%、存储省 90%。标题化用英语谚语 "let the cobbler stick to his last"（鞋匠守鞋楦）：让每个 expert 守好自己擅长的领域，别在全参微调里被迫学不擅长的事。

**团队背景**：DeepSeek AI（作者与 DeepSeekMoE/DeepSeek-V2 架构组高度重合），出发点非常实际——DeepSeek 系 MoE 模型动辄百亿千亿参数，下游定制全参微调成本爆炸。

## 2. 动机与痛点

PEFT（LoRA、Adapter、P-Tuning 等）几乎全部为 **dense 架构**设计，MoE 模型的 PEFT 是空白。而 MoE 恰恰是最需要也最适合 PEFT 的架构，原因有二：

- **全参微调（FFT）伤专业化**：MoE 的性能来自 expert 分工，FFT 让不擅长该任务的所有 experts 也被更新，破坏路由系统学到的分工（论文称之为 specialized 的退化），还带来通用能力灾难性遗忘；
- **MoE 天然自带"选择维度"**：dense 模型的 PEFT 只能在参数空间做文章（低秩、稀疏、加新参数），MoE 多出一个**结构化的选择轴——按 expert 整块选**，这是稀疏架构独有的 PEFT 自由度。

两个前置洞察实验（在 DeepSeek-V2-Lite 上做的探测）：

1. **同一任务内路由高度集中**：把每层 experts 按归一化 gate 值排序，少量 experts 承载了绝大多数 gate 值——任务数据只激活一小撮专家；
2. **跨任务激活的 experts 显著不同**：对每对任务统计 Top-6 experts 的平均共享数，**对角线≈6、非对角≈0**——同任务复用几乎同一组 experts，不同任务各用各的。

这两条合起来就是 ESFT 的立项依据：既然任务→expert 组合的映射既集中又互斥，"只训相关 experts"既省算力又保分工。

## 3. 核心方法

### 3.1 Expert 相关性打分（两种 score）

从训练集随机采样子集 $D_s$（实证 **32 条拼接样本、每条定长 L=4096** 即足够稳定，见附录 C）。对每层每个 expert 打分：

**ESFT-Gate（平均 gate 分数）**：
$$g_i^l=\frac{1}{N_s}\sum_{j=1}^{N_s}\frac{1}{L_j}\sum_{k=1}^{L_j}g_{i,k}^l$$

**ESFT-Token（token 选择比率）**：
$$r_i^l=\frac{1}{N_s}\sum_{j=1}^{N_s}\frac{1}{L_j}\sum_{k=1}^{L_j}\frac{\mathbb{1}(g_{i,k}^l>0)}{K}$$

前者衡量路由权重质量，后者只看"被选中"的频率（被选即 gate>0）。$K$ 为每 token 激活的 expert 数。

### 3.2 阈值式选择与微调

对每层，按分数降序累计选择，直到覆盖总相关性比例达到阈值 $p$：

$$\sum_{i\in E_s^l} R_i^l \geqslant p$$

微调阶段**只更新被选中的 experts**（可选是否连 shared experts、attention/router 等 non-expert 模块一起训），其余 experts 与模块全部冻结。**注意推理/训练时路由不设限**——token 仍可被路由到任何 expert，被冻结的 expert 照常计算，只是参数不更新。

超参设定：ESFT-Gate 用 $p=0.1$、ESFT-Token 用 $p=0.2$（学习率 1e-5，FFT 3e-5、LoRA 1e-4）。

### 3.3 为什么这样设计（与 LoRA 的本质区别）

LoRA 在**所有**参数矩阵上叠低秩增量——它把"任务适配"弥散到全模型，既动 shared experts 也动 attention；ESFT 按 **expert 整块**选，天然对齐 MoE 的功能分区内治。后文 Table 3 的冻结消融会证明：动 shared 参数才是通用能力遗忘的元凶，而 ESFT 恰好绕开了它。

## 4. 实验与结果

**设置**：backbone 为 **DeepSeek-V2-Lite**（每层 66 experts：64 routed + 2 shared，细粒度架构）；先在**剔除数学/代码**的对齐数据上训练得到 vanilla 基线（保证 Math/Code 有提升空间）；2 节点×8 A100。

**任务**：模型增强（Math：MetaMathQA 训 → GSM8K/MATH 评；Code：evol-codealpaca Python 子集训 → HumanEval/MBPP 评）+ 模型适应（Intent 意图识别 / Summary 摘要 / Law 法律判决预测 / Translation 切罗基语→英语低资源翻译，后四者用 GPT-4 打分 0-10）。

**定制任务表现（Table 1，8 任务平均）**：

| 方法 | Math | Code | Intent | Law | Trans | **平均** |
|---|---|---|---|---|---|---|
| Vanilla | 19.6/55.9(MATH/GSM8K) | 42.1/44.6 | 16.8 | 17.1 | 14.5 | 33.6 |
| FFT | 23.4/66.4 | 42.1/42.2 | 78.8 | 47.0 | 38.4 | 51.0 |
| LoRA | 20.6/58.9 | 39.6/44.8 | 67.8 | 39.7 | 23.1 | 44.9 |
| ESFT-Token | 22.6/66.0 | 41.5/42.6 | 75.6 | 45.7 | 36.2 | 49.4 |
| **ESFT-Gate** | 23.2/64.9 | **43.3**/41.8 | 78.6 | **49.1** | 35.2 | **50.2** |

ESFT-Gate 平均 50.2 几乎追平 FFT 51.0，大幅甩开 LoRA 44.9；Law（49.1）与 HumanEval（43.3）甚至是全场最佳。

**通用能力保持（Table 2，7 基准平均）**：Vanilla 62.4 → **ESFT-Token 61.5** / ESFT-Gate 60.6 > LoRA 59.1 > FFT 58.8。FFT 在 IFEval 上从 42.5 崩到 34.2，ESFT 只微降到 40.7——**省参数的方案反而更不忘本**。

**效率（Table 对比）**：训练时间 ESFT 19.8/20.9 min vs FFT 28.5（省 ~30%，LoRA 16.5）；存储 ESFT 2.57/3.20 GB vs FFT 28.6 GB（**省 90%**）；每层实选 experts 仅 **2-15 / 64**（可训参数少 75%-95%），且越靠中间的层选得越少（分工最集中区）。

**关键消融一：训什么参数重要吗（Table 3，精华）**：

| 配置 | 可训参数 | 专用 | 通用 | 平均 |
|---|---|---|---|---|
| 只训相关非共享 experts | 1.4B | 49.4 | **61.5** | 55.4 |
| 相关 experts + shared + non-expert | 2.7B | **50.8** | 60.3 | **55.6** |
| 全部非共享 experts | 15.7B | 51.0 | 58.8 | 54.9 |
| 只训 shared + non-expert（不训 experts） | 1.3B | 49.0 | 60.0 | 54.5 |

结论三条：①专用性能随可训参数单调升；②**通用遗忘与"训 shared 参数"强相关**（任何含 shared/attention 的配置通用分都掉到 ≤60.3）；③只训相关非共享 experts 是性价比之王（1.4B 拿 55.4）。由此给出两种推荐策略：冲专用 → shared+相关 experts 全开；求均衡 → 只训相关非共享 experts。

**关键消融二：打分函数真有用吗**：把选中 experts 换成同数量随机 experts，ESFT-Gate 平均掉 4.4 分、翻译任务崩掉 20.4 分——选择不是玄学，是信号。

**关键消融三：细粒度架构是前提吗**：用贪心搜索把 64 个 experts 分组绑定模拟粗粒度 MoE（组内共享平均 affinity，保持每 token 1/8 计算量），组越大 ESFT 相对 FFT 退化越严重——**ESFT 的收益依赖细粒度专家切分**（DeepSeekMoE 式架构），在 Mixtral 型粗粒度 MoE 上此法先天不足。

**p 的行为**：ESFT-Token 在 p=0.5 处专用/通用双峰值，p=0.2 后饱和；ESFT-Gate p=0.3/p=0.1 峰值、p=0.1 饱和——大部分 experts 对任务确实无关。

## 5. 局限与后续

论文自认局限：①细粒度 MoE 当时只有 DeepSeek 系可得，**全部实验只在 DeepSeek-V2-Lite 一个底座上做**，外部效度待验；②粗细粒度对比缺乏参数量与结构对齐的真实模型，用的是"分组绑定"模拟法，结论强度打折。

社区定位与后续：ESFT 属于"MoE 原生 PEFT"早期代表（与 MoLE、MoRA 等同期线并列），其 expert 选择思想被后续 LoRA-MoE 混合方法（按 expert 加 LoRA）反复引用。对 DeepSeek 自家脉络而言，它验证了细粒度专家分工的可解释性与可操作性，与 DeepSeekMoE 的"极致专家专业化"主张互为表里。实践提醒：V2/V3 之后的超大 MoE（共享专家承担比例更高、路由更复杂）上直接套用需重验阈值 p 与 score 函数。

## 6. 与代码的对照（论文 → 本仓文件）

| 论文概念 | 仓内位置 | 说明 |
|---|---|---|
| relevance score 收集 | `scripts/expert/get_expert_scores.py` | 前向跑采样数据，按层落盘每个 token 的 expert_ids + expert_weights |
| Eq.(6)/(7) 打分 | `scripts/expert/generate_expert_config.py` → `get_summary()` | `gate_scores`（累加权重）与 `token_scores`（`np.add.at(..., 1/TOP_K)`）双轨累计后归一化——公式逐行对应；常量 `TOP_K=6, N_EXPERTS=64, N_LAYERS=26`（V2-Lite：27 层中首层非 MoE） |
| Eq.(8) 阈值选择 | 同文件主流程：按分数排序 → `current_score += score` 直至 `>= args.top_p` | 产出 `expert_cfg.json`（`experts{层: [id]}` + `shared_experts` / `non_expert_modules` 开关）——**这两个开关正是 Table 3 消融矩阵的三个实验轴** |
| 冻结/解冻机制 | `esft.py` → `to_esft(model, adapter_config)` | 核心技巧：`to_buffer()` 把全模型参数转成 buffer（不可训练），再对被选 experts（及可选 shared_experts / 非 expert 模块）调 `to_param()` 转回参数——比 `requires_grad=False` 更彻底（连 optimizer 状态都不产生），`param_list` 记账以便转回 |
| ESFT 模型加载 | `esft.py` → `load_esft_model()/add_adapter()` | base 模型 + expert_cfg.json + adapter 权重（safetensors）三件套组装，`_get_expert_id` 解析 `model.layers.25.mlp.experts.10.*` 型键名 |
| MoE 底座 | `deepseek/modeling_deepseek.py` | `DeepseekV2MoE` 层实现（`to_esft` 中 `type(layer.mlp).__name__=='DeepseekV2MoE'` 判定） |
| 训练入口 | `train.py` / `train_ep.py`（expert parallel 版）/ `configs/base.yaml` | batch 32 / seq 4096 / 每 100 步评测一次 |
| 评测 | `benchmarks.py`、`eval_multigpu.py`、`scripts/eval*.sh` | 论文 8 个定制任务 + 7 个通用基准 |

读码路线建议：`get_expert_scores.py`（数据怎么来）→ `generate_expert_config.py`（论文公式落地，最短闭环）→ `esft.py` 的 `to_buffer/to_param`（PyTorch 冻结的花式实现，值得抄）→ `train.py`。

## 7. 学习路径

**前置**：①MoE 基础（gate/router、Top-K 路由、负载均衡）；②DeepSeekMoE 的两个主张——细粒度切分 + 共享专家隔离（本文的所有架构红利来自它）；③LoRA 原理（对比项）；④灾难性遗忘概念（本文"通用能力保持"的问题来源）。

**精读顺序**：Figure 2/3（两个探测实验——全文立论之本）→ §3.3 方法（三个小节很短，公式简单）→ Table 1/2 主结果 → **Table 3 冻结消融**（全文最重要的一张表，理解"shared 参数=遗忘元凶"）→ §6.4 粗细粒度分组实验 → 附录 C（为什么 32 个样本就够）。

**复现建议**：①门槛最低：下载 V2-Lite + 本仓脚本，跑 `get_expert_scores.py` → `generate_expert_config.py` 生成自己任务的 expert_cfg.json，可视化各层选中 experts（复现 Figure 4 的"中层选得少"现象）；②进阶：用 `train.py` 在自选小数据集（如法律/翻译）上复刻 ESFT vs LoRA vs FFT 三线对比，重点盯通用基准的遗忘曲线；③工程向：把 `to_buffer/to_param` 的冻结技巧移植到自己的训练框架（注意 optimizer 只需包住 param 部分）；④**不要**在 Mixtral 等粗粒度模型上直接照搬——先读 §6.4 明白为什么。

**延伸阅读**：DeepSeekMoE（架构前提）、DeepSeek-V2 技术报告（V2-Lite 细节）、LoRA 原文、Switch Transformers（粗粒度对照）、后续 MoE-PEFT 综述（MoLE/MoRA/SiRA 一线）。
