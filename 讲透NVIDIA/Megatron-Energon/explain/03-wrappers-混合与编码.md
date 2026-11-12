# 03 · wrappers：混合与编码

## 角色定位

`wrappers/` 是数据集树的变换层：混合、串联、批组装、序列打包都是 `SavableDataset` 包 `SavableDataset` 的洋葱结构。基类 `BaseWrapperDataset`（wrappers/base.py:23）默认把状态存取委托内层（:100），子类只用 `_savable_fields` 声明增量状态。本篇聚焦四件套 BlendDataset/ConcatDataset/BatchDataset/PackingDataset 与 skip/forked 横切机制。

## 内部结构

- **BlendDataset**（blend_dataset.py:16）：按权重随机混合多流，"输入可无限、本数据集恒无限"（:19）；`_savable_fields=("exhausted","_worker_rng")`（:28）。`__iter__`（:59）先给本 worker 无样本的流清零权重（:70），主循环用 `WorkerRng.choice_idx` 抽流（:93，worker 级 RNG 保证恢复后重放一致）；StopIteration 置 exhausted 清权重（:101），全耗尽才结束、收尾重置（:110）支持 epoch 循环；样本加 ds_idx 键（:108）。
  - 勘误：task_encoder/loader.py 三处 docstring（:129/:200/:255）引用 `megatron.energon.MixDataset`，全仓无此类——真名 `BlendDataset`（`__init__.py:143`），属文档滞后。
- **ConcatDataset**（concat_dataset.py:13）：串行拼接，构造断言有限（:27），明言"仅对 val/test 有用"（:16-18）；无自身状态（:29），键加 ds_idx（:38）。51 行是自定义 wrapper 最小范本。
- **BatchDataset**（batch_dataset.py:28）：batcher 把 N 样本合一批，满批 flush（:129）；generator 型可断点——`_generator_sample_keys/_generator_offset`（:39/:99）存批成员键与已 yield 子位，恢复时重放到中断处。`restore_sample`（:179）是"解一层前缀+逐成员委托内层"范式（:183）；can_restore 要求 batcher_stateless（:168）。
- **PackingDataset**（packing_dataset.py:34）：LLM 序列打包。三段流水：`pre_packer` 从 reading_buffer 选组（:243），组扁平存缓冲、组界存 `_pre_packing_lengths`（:264，buffer 不支持嵌套）；`sample_encoder` 逐样本编码（:221）；`final_packer` 合 pack（:269，generator 型可一 pack 出多子批 :283）。六项进 `_savable_fields`（:76），packing 中途可存档。
- **skip.py**：`SkipSample` 弃用别名（:8-17），构造即告警并转发顶层版本——wrapper 抛它表示跳过一个样本或整个缓冲。
- **fork_hook.py**（包根部，fork 卫生）：`WeakCallbacks` 弱引用注册表+文件尾 `os.register_at_fork` 挂三时机钩子；`ForkMixin` 让类声明 `__before_fork__` 等方法即自动注册（消费者如 file_cache_pool），fork 后句柄/锁得以重置。

## 外部连接

- `task_encoder/base.py:595` 是 PackingDataset 唯一构造点（`sample_encoder=postencode_sample`，:601）——"重写 postencode + packing"的训练代码都踩在这条流水线上。
- BatchDataset 由同文件 build_batch 组装；BlendDataset 由 recipe 的 `DatasetBlendMode` 驱动（recipe.py:509，blend 与 blend_epochized 不可混）。
- 键协议来自 base_dataset.py：`add_sample_restore_key`（:410）前缀追加（成员用）、`set_sample_restore_key`（:432）整体替换（成品用）——成品键即重放指令。
- mix_batch/group_batch 是批级变体；Gc/Watchdog 由 loader 挂载（见 01 篇）。

## 数据流

PackingDataset 主循环（:309-349）：填 reading_buffer（:198 判满算双缓冲合计）→ 无组则 pre_pack（:324，空产出计 round、超限报错 :310）→ 逐组 final_pack yield → 源耗尽后冲刷剩余组与残缓冲（:339）。

键的旅程（可恢复的根基）：内层键 → encoder 加前缀（:235）→ final_pack 收集成员键（:280）→ `set_sample_restore_key` 合成品（:300）。恢复即逐层剥：外层解包取成员键→每成员剥一层 encoder 前缀→`dataset.restore_sample(inner)`（:386）重放内层。

## 设计决策

- **restore_sample L381-384 双重剥键疑似 bug 详析**：restore_sample（:366）有三处成对重复行——:370-371/:374-375 对 restore_key 重复解包是无害幂等；但 :381-383 在 encoder 路径对成员键**连续两次**解包是破坏性的。写入端只加过一次前缀（:235-240）：第一次剥离后断言通过、inner_idx 已是内层完整键；第二次剥掉内层的类名前缀（如 "MapDataset"），:384 断言必失败 → AssertionError。结论：**packing+sample_encoder 组合的 restore_sample 必炸**（恰是重写 postencode_sample 的用户）；无 encoder 路径（:380）不受影响。对照 BatchDataset 单次解包（batch_dataset.py:183-188）可证属笔误级缺陷；文件由单 commit 82d5aa9 引入、重复行与生俱来，tests/ 无 packing restore 用例——疑似合并事故，仅嵌套 PackingDataset 偶然成立。修法：删 :383（连同 :371/:375）。
- 无限/有限分工：Blend 恒无限、Concat 必有限、Packing 的 len_worker 返回内层长度并注释承认真实长度依赖 packing（:172）。
- 失败容忍三计数器（各 100，:120）+ 空产出 round 上限（:314）防 packer 死循环。
- add/set 键二分：add 保溯源链（pack 出问题能找回成员），set 表达"成品即指令"——任意深度 wrapper 链皆可单样本重放。
- fork 卫生走 `os.register_at_fork` 而非 multiprocessing 回调：本仓唯一多进程上下文即 fork（savable_loader.py:807）。

## 新人提示

1. Blend 权重须全 >0（:68）；某 worker 所有流无样本会 RuntimeError（:79），小数据集+多 worker 先调小 parallel_shard_iters。
2. packing 断点续训要求两个 stateless 标记同真（:351-364），自定义 packer 记得标 `@stateless`。
3. 单样本调试 pack 先 `can_restore_sample()`（:351）；encoder 路径踩双重剥键，需先修 :381-384。
4. 文档里的 MixDataset 一律读作 BlendDataset（task_encoder/loader.py:129 等）。
5. 自定义 wrapper 三件套 `_savable_fields`/`reset_state_own`/`len_worker`，拿 concat_dataset.py 当模板。
6. SkipSample 从包根 import（wrappers.skip 为弃用别名）；抛它跳过当前样本/缓冲。
