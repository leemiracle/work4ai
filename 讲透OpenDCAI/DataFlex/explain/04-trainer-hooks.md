# 04 · Trainer 系：三接缝 Mixin 与 monkey-patch 总编排

## 角色定位

`train/hooks.py`（185 行）与 `train/trainer/` 五个训练器、`cli.py`/`launcher.py` 两组 patch 函数，合起来回答：**如何不 fork LlamaFactory 而改变训练循环的用数、损失与批次来源**。这是 DataFlex 工程含金量最高的一层——替代了历史上三份 vendored 的 `_inner_training_loop` 拷贝。

## 内部结构

**hooks.py 三条接缝**：模块 docstring（:15-38）自述——曾三次整拷 `Trainer._inner_training_loop`（每份约 550 行、复述上游四分之三），每次 transformers 发版都要 re-diff 三份。现在只借三个公开方法：`get_batch_samples`（下一步用哪些样本）、`args.max_steps`（总步数）、`compute_loss`/`training_step`（损失）。

`DataflexTrainerMixin`（:95）要求子类声明三个 `dataflex_*` 方法（:107-128）：step_budget、initial_indices、next_indices（每步被问，返回索引/`WHOLE_DATASET` 哨兵/None 保持现状）。两条接缝：
- `train()`（:134-150）：预算写进 `args.max_steps` 再放行上游。不用 `set_initial_training_values` 的理由在注释——v4 循环从 `len(epoch_dataloader)` 取每轮迭代数，那条路在 v4 被静默忽略（:138-144）。
- `get_batch_samples()`（:156-176）：**故意无视**上游 epoch_iterator，从自己的 stage dataloader 拉批；拉批与 `num_items_in_batch` 计数仍交 `super()`（:166-171 注释：该计数决定累积窗内损失缩放并跨卡聚合，再实现一份就是埋静默 bug）。`_StageIterator`（:64-92）无尽迭代——区间跑干 set_epoch 重读，让步数预算而非数据长度决定何时结束；换 stage 顺手更新 `callback_handler.train_dataloader`（:183-184）。
- v4/v5 兼容在 `group_by_length_requested`（:52-61）：v5 把 `group_by_length` 改名 `train_sampling_strategy`，两处都读。

**SelectTrainer 循环基座**（select_trainer.py:51）：阶段表=`warmup_step + update_step × update_times`。`dataflex_next_indices`（:139-191）判边界→`_dataflex_sync` 对齐各卡（:193-199）→调 selector.select。adapt-inf 还有 checkpoint 断点续跑：`run_signature` 校验数据/算法/调度一致性（:293-309）、恢复重放 batches_seen（:367-391）、存档落 `dataflex_selection_rank_*.json`（:393-410）。

**五形态分发**：select（基座本体）/mix（返回 `WHOLE_DATASET` 整库重建快照 mix_trainer.py:177-186；DoReMi 在 compute_loss :222-285 按域加权，ODM 在 training_step :200-218 回填 reward）/weight（training_step 整体委托 weighter，weight_trainer.py:37-46）/reorder（`_ReorderAsSelector` 适配器，reorder_trainer.py:23-47；**强制 SequentialSampler**——:91-113 注释说透：洗牌采样器会静默吞掉课程顺序，跑成 random baseline 还看起来正常）/lego（`_PipelineAsSelector` 同法，第 5 篇）。

## 外部连接

**launcher monkey-patch 总编排**：`cli.py main`（:238-293）与 `launcher.py launch`（:215-231）是同一套 patch 双入口（多卡 torchrun 重启 launcher 走后者）。顺序：`patch_finetune_params`（:53-58，把 `DynamicFinetuningArguments`/`DataArguments` 换进 llamafactory.hparams，新增 train_type 等八个字段，dynamic_params.py:38-72）→ `patch_trainer`（:54-101，**五段式**：sft.trainer 模块→sft 包层→sft.workflow 引用→pt.trainer→pt.workflow，:85-100）→ 按 train_type 选数据 patch（dynamic_mix 换 get_dataset 四点 :104-129；dynamic_reorder 仅 static+raw 才真 patch :159-161；dynamic_lego 换 lego_get_dataset :183-203）→ 延迟导入 `run_exp`。`uncache`（:16-43）从 `sys.modules` 剔除 hparams 模块防命中旧类。

## 数据流

train_type 决定注入哪个 Trainer 类 → mixin 每优化步前问 `dataflex_next_indices` → 命中边界就换 Subset+dataloader → 上游循环照常拉批反传。损失侧 hook 按形态附加。

## 设计决策（含批判）

"三个 dataflex_* 声明+两个上游覆写"把版本耦合压到两个公开方法；但 docstring 自认 `get_batch_samples` 的契约"改变数据并非其宣传用途，是升级时第一个要复查的点"（:33-38）。批判：五段式 patch 是对 LlamaFactory 内部符号布局的经验清单而非契约，上游模块重组会静默漏 patch——漏掉的形态是"跑成 static 还看起来正常"，最难察觉。

## 新人提示

调试先看 `[PatchTrainer] Using trainer type` 与 `[Dataflex] step budget = N` 两行确认生效，再看边界的 "starting the Nth dynamic data selection"。读代码带着"哪三样是上游循环不给的"去看三条接缝——答案在 hooks.py:23-27。升级上游时 `get_batch_samples` 与 `num_items_in_batch` 计数规则是回归最小集。
