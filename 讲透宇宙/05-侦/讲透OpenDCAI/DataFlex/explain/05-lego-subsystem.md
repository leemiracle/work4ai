# 05 · train/lego 组合子系统：把组件当积木

## 角色定位

`src/dataflex/train/lego/` 实现 `train_type: dynamic_lego`：在**单次训练**内串联多条数据策略——粗过滤→调域配比→排课程→逐样本加权，一条 YAML 管线全说了算。它不新写算法，全部从四大组件族既有预设取积木（pipeline.py:43-48），是"组合优于新增"哲学的集中体现。

## 内部结构

**SchedulePipeline 双插座**（pipeline.py:42）：索引空间 `IndexStage.apply(plan, ctx) -> plan` 变换索引；损失空间 `LossStage.weights(losses, ctx) -> tensor` 出逐样本乘子，合成公式 `L = mean_i(∏_k w_i^(k) · l_i)`（:353-396）。两插座类型在 stages.py:140-150。

`from_config`（pipeline.py:79-140）逐条解析 `{family, component, warmup_step, every, enabled}`：每 stage 用 load_component 拿同名预设再 `REGISTRY.build`，**每 stage 配独立 cache_dir**（:110-115）——否则 selector 按 `step_{id}.json` 缓存，跨流水线混用会静默读到尺寸不对的旧产物。DoReMi 这类按域加权的 mixer 同时注册一个损失空间孪生 stage 并继承其 warmup 时钟（:128-138），避免损失侧从第 0 步加权而索引侧还在暖身。

**_validate 三条硬规则**（:168-220）：①索引序强制 select→mix→reorder（stages.py:31），YAML 写乱自动重排+警告——理由在 stages.py:27-30：比例按幸存者算、块已知才能排、排序之后任何 stage 都会毁掉它；②恰好一个 taker（吃掉本轮预算），多个只认最后者、select 的 draw 后跟 taker 报错，零 taker 补 `_UniformTakeStage`（:206-211、:423-443）；③只给标量损失的 weighter 不能与其他损失贡献共存（:213-220）。

**build_plan 向上封闭触发**（:235-278）：任一 stage 到期重算、下游连锁重算、上游未触发者保留缓存池——`_stage_out` 每级独立槽位（:65-71 注释解释共享槽为何错：会把某 stage 自己的旧输出当上游喂回去、池逐边界萎缩）。预算强制 `_enforce_budget`（:286-322）：ordered 砍头（课程下一段）、无序均匀采样（避免低索引=第一域偏置）、不足循环铺满。

**ScoreBoard 每边界只算一次**（scoreboard.py:51）：稠密 NaN 数组+按位置记龄（:74-84，注释 :76-80 讲清为何按位置非按指标：部分回填会让整列显得新鲜）；`compute_calls/cache_hits` 可观测共享是否生效。stages.py:89-127 的 `board_score_fn` 是"loss 选择器与动态 reorder 要同一信号"的落地：第一个付前向，后来查表。

**stages.py 八类**：三 ABC（Stage :35 / IndexStage :140 / LossStage :146）+五适配器：SelectStage（filter/draw 双模式 :178-237）、MixStage（比例→无放回域配额，largest-remainder 保精确和 :421-436；识别 DoReMi 类后索引侧直通 :293-301）、ReorderStage（拒绝 apply_at=raw 进管线 :499-506）、WeightStage、DomainWeightStage（域权重按 batch 的 domain_id 查表成乘子 :587-614）。

**DomainView 零改动兼容**（domain_view.py:26）：mixer 只读 mixture_manager 的 names/initial_proportions/sources 三样；DomainView 用"拼接数据集+domain_ids 标签"回答（sources 惰性 select 物化），既有 mixer 一行不改跑在组合表示上——MixedProportionManager"每源一数据集"表示做不到（留给选择器/重排的是 train_dataset=None）。

## 外部连接

`LegoTrainer`（lego_trainer.py:54）经 `_PipelineAsSelector`（:24-42）把管线伪装成 selector，借走 SelectTrainer 的循环（"避免第五份 ~550 行拷贝"）；`compute_loss`（:192-233）剥掉非模型输入的 domain_id 后前向，走可微的 `_per_sample_loss_grad`（打分用的 loss_utils 是 detach 版）；`training_step`（:260-288）回填 ODM reward 并驱动 DoReMi 批内更新。数据侧 `lego_get_dataset`（loader.py:536）给每行注入 domain_id。

## 数据流

边界 → PlanContext（context.py：一个对象满足所有族的签名偏食）→ build_plan 跑索引链 → DataPlan（plan.py:16-20，int64 数组：千万行语料下 Python list 约 1GB、数组只几百 MB 且切片不拷贝）→ Subset+顺序采样器进训练 → 每步 compute_loss 查损失栈。

## 设计决策（含批判）

"触发向上封闭+每级缓存槽"是组合调度正确性关键，但也让行为推演变难：`score_max_age` 允许复用陈旧信号，与 `max_samples` cap 组合时 cap 可能静默不生效（stages.py:104-113 专门警告）。批判：validate 的自动重排/自动补 taker 是"猜用户意图"，老手省事、新手可能掩盖配置误解（日志警告是唯一防线）；DomainView.sources 对大域全量物化的内存无上限。

## 新人提示

从 `select_then_reorder` 两段管线（components.yaml:606-619）入手，hierarchical 四段（:578-603）是完整范本——注意 2.5 步插 reorder 的注释。`save_plans: true` 把每轮计划落盘，配合启动日志 `index[...] loss[...]`（pipeline.py:222-225）复盘调度。单家族对照用 `select_only`，验证组合路径与 dynamic_select 一致。
