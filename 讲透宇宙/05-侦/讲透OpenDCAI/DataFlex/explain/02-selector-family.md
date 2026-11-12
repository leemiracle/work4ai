# 02 · Selector 族：在线选择与离线预选的两条腿

## 角色定位

`src/dataflex/train/selector/` 是"选哪些样本进下一个训练区间"技能的全部实现：15 个注册选择器加一层契约 ABC。每个调度边界，模型暂停、选择器看当前模型状态、吐出下一段训练用的索引列表。互补的 `src/dataflex/offline_selector/` 是训练前的离线预选腿。

## 内部结构

**契约层** `base_selector.py`：`Selector(ABC)`（:9）构造收四依赖 dataset/accelerator/data_collator/cache_dir（:10-15）；抽象方法只有 `select(model, step_id, num_samples, **kwargs)`（:128）；`warmup`（:100-126）在 rank0 生成随机暖身索引再 broadcast 对齐各卡。为第 5 篇的 lego 组合预留两个挂钩：`set_candidate_pool`（:29，上游过滤后限制打分范围）与 `set_score_source`（:59，共享打分源，`_scores_for` :73-90 统一决定走共享源还是 `_compute_losses`）。

**影响函数系**（谁对 eval 集有用就选谁）：
- `less`：训练/eval 梯度做 TRAK 随机投影再点积。TRAK 延迟到运行时才 import（less_selector.py:15-29）；ZeRO-3 适配——参数量用 `ds_numel`（:71-85）、优化器矩用 `safe_get_full_optimizer_state`（:87-114）。
- `tracin`：全量 SGD 梯度+多 checkpoint 累积（TracInCP），继承聚类基类但不聚类，docstring 自认"最贵的方法——每轮对全量 N 样本前向+反向"（tracin_selector.py:1-8）。
- `cluster_*` 三兄弟：`ClusterBaseSelector`（cluster_base_selector.py:47）只管"聚成簇、每簇抽代表点"，聚类一次建缓存；cluster_less/cluster_tracin/cluster_loss 子类自带评分，把全量打分降为代表点打分。
- `icons`：多任务 consensus 投票，`task_boundaries`/`pool_groups` 对齐参考实现（icons_selector.py:114）。
- `coincide`（EMNLP'24）：无梯度、无 eval_dataset 的多模态共核选择（coincide_selector.py:39）。

**轻量信号系**：loss/delta_loss/random/custom/tsds/near/adapt_inf/nice。

## 外部连接

在线侧由 SelectTrainer 驱动（第 4 篇）。离线侧三件套：

1. `offline_near_selector.py` 与 `offline_tsds_selector.py`：嵌入+FAISS IVFFlat 检索，TSDS 再加 KDE 密度与贪心预算优化，产物 `.npy`。二者**游离于 Registry 之外**（未注册），由运行时 `near`/`tsds` 消费：near_selector.py:12-33 对索引矩阵做形状/整数性/越界硬校验。
2. `offline_presel_selector.py`：`dataflex-cli presel` 入口（cli.py:244-248），reference→extract→score→select 四阶段。**双预算口径**：`--budget-unit record`（官方 LLaVA 口径：固定 5% 参考/15% 终选）vs `image`（唯一图像为预算单位，图像-指令扩展被显式记录而非静默摊平，docstring :1-7 与 argparse :772-774）。
3. `record_presel_selector.py`：上游 PreSel（MIT）原样移植的记录 ID 选择核心，配合 `record_presel_pipeline.py` 做记录预算三阶段。

**离线↔运行时双向环**：presel reference 导参考集 → `presel_reference.yaml` 运行时训练出参考模型 → `training-manifest` 认证 → `score` 用该 checkpoint 逐对打分 → `select` 导出 15% 子集 → `presel_static.yaml` 运行时消费。这是**工作流层的环**而非 Python import 环——offline 模块只 import `dataflex.utils`，代码层无循环依赖。

## 数据流

边界处 `select()` 返回索引列表 → SelectTrainer 包成 `torch.utils.data.Subset` 换 dataloader（第 4 篇）。每个选择器把结果写 `cache_dir/step_{id}.json`（selector_io 的 save/load），重跑同 step 直接读缓存并 broadcast，天然幂等断点续跑。

## 设计决策（含批判）

按列去重的 near 选择（near_selector.py:36-70，第 k 近邻优先于第 j 个 query）体现"逐列扫描近邻矩阵"的语义；但 tsds 的 `np.random.choice` 没接种子（tsds_selector.py:33-40），与 base 的 `seed=42` 不相通——同配置重跑结果不同，复现性短板。tracin 的全量开销、icons 的投票超参都应在小数据集先演练。

## 新人提示

跑通顺序：random → loss → less。less 族需 `pip install dataflex[less]`（报错信息写在 less_selector.py:26）。读影响函数系先建直觉：影响分数≈训练样本梯度与 eval 样本梯度的相似度，LESS 用投影降维、TracIn 用 checkpoint 序列近似训练轨迹、ICONS 把单任务分数变多任务投票。离线产物路径写死在 components.yaml（tsds 的 probs_path、near 的 indices_path），换数据集记得同步改。
