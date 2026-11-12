# 06 · 数据加载管线：从 LeRobot episode 到混合单步样本流

> 覆盖：`gr00t/data/dataset/lerobot_episode_loader.py` · `factory.py` · `sharded_mixture_dataset.py` · `sharded_single_step_dataset.py`

## 一、角色定位

四文件构成训练数据供给链，职责递进：`LeRobotEpisodeLoader` 做 episode 级解析（元数据/parquet/视频/统计）；`ShardedSingleStepDataset` 把 episode 切成单步样本并组成均衡 shard；`ShardedMixtureDataset`（IterableDataset）按权重混合多数据集、管分布式分片与后台预取；`DatasetFactory` 装配入口。设计核心是把"昂贵的 episode 解码"与"廉价的单步采样"解耦。

## 二、内部结构

**LeRobotEpisodeLoader（`lerobot_episode_loader.py:80`）**。元数据常量五件套在 `:51-57`。`__init__`（`:115-142`）：`_load_metadata`（`:144-203`）→ 校验 modality_configs（`:220-299`）→ 算 episode 长度。`_load_metadata` 两个硬行为：stats.json 缺失直接断言失败并提示用 `gr00t/data/stats.py` 生成（`:180-182`）；relative_stats.json 先 pop 掉 `__fingerprints__` 缓存键再挂 `stats["relative_action"]`（`:186-194`），sidecar 混入会被消费者误当 stats 组。`_parse_and_validate_modality_configs`（`:220-299`）两条契约：language 多键只留第一个且 delta_indices 必须 `[0]`（`:260-276`）；video 键与 modality.json 不一致时按位置自动映射（`:281-297`，N1.6↔N1.7 命名代差兼容）。读取三方法：`_extract_joint_groups`（`:305-344`）按 start/end 切片（`:331-336`），键缺失只 warning 产出空列（`:340-342`）；`_load_parquet_data`（`:346-398`）按 `episode_index // chunk_size` 定位文件（`:362-364`），language 列经 tasks_map 翻成文本（`:370-384`）；`_load_video_data`（`:400-448`）用键映射解析文件名、回退 `observation.images.{key}`（`:425-427`）逐视角解码（`:442-446`）。`get_dataset_statistics`（`:500-535`）切出每键 mean/std/min/max/q01/q99（`:523-530`）。`__getitem__`（`:565-621`）合成 episode DataFrame：语言可来自元数据（`:537-563`），实际长度取 `min(len(df), nominal)`（`:600-601`），视频/mask 帧数必须与行数相等（`:608-611`）。

**ShardedSingleStepDataset（`sharded_single_step_dataset.py:82`）**。模块级 `extract_step_data`（`:27-79`）是采样原子操作：按 `step_index + delta_index` 生成索引（`:40`），`allow_padding` 时钳位 `[0, len-1]`（`:41-42`）；state/action `np.vstack` 转 float32（`:50-57`）；language 恰一键（`:68`）后组装 `VLAStepData`（`:71-78`）。`action_horizon = max−min+1`（`:149-150`），有效步数=原长−horizon+1（`:233-236`）。`shard_dataset`（`:160-231`）：episode 置换（`:175`），`num_splits = int(1/episode_sampling_rate)`（`:176`），步索引洗牌后按 `i::num_splits` 分层切段（`:186-193`）；shard 数取 `min(ceil(total/shard_size), len(splits))`（`:202`）；round-robin 保每 shard 一段、其余贪心塞最短 shard（`:211-219`）。`get_shard`（`:275-295`）对每 episode 只解码一次（`:292`），逐 step 走 processor 包成 EPISODE_STEP 消息（`:260-269`）。

**ShardedMixtureDataset（`sharded_mixture_dataset.py:149`）**。类 docstring 钉死"分布式种子不变式"（`:171-195`）：seed 必须各 rank 相同，分片靠 `i % (world_size*num_workers) == rank*num_workers + worker_id` 取模（`:178`，实现 `:402`）；种子不对称时同一 shard 被多 rank 重复处理、另一些永不出现，loss 正常、只在 eval/部署期劣化（`:182-186`）。`__init__`（`:218-259`）生成初始调度并 `merge_statistics()`（`:261-303`）：按 embodiment 分组加权合并，`processor.set_statistics(..., override=...)`（`:299-301`）。公式在模块级 `merge_statistics`（`:44-146`）：`Var_combined = Σ(w_i(σ_i²+μ_i²)) − (Σw_iμ_i)²`（`:57`），min/max/q01/q99 取全局保守极值（`:127-134`）。`generate_shard_sampling_schedule`（`:309-367`）训练态用 `rng(seed+epoch)`（`:323`），权重先除以各数据集平均 shard 大小再归一（`:334-337`），`rng.choice` 抽 num_shards_per_epoch 次（`:340-342`），耗尽即重洗（`:353-359`）；eval 态全量枚举（`:362-366`）。`__iter__`（`:406-451`）单线程预取：`ThreadPoolExecutor(max_workers=1)`（`:418`）→ 取本 worker 份额（`:421`）→ 消费前等缓存（`:432`）、立刻提交下一 shard 后台加载（`:441`→`:473-475`）→ shard 内步序再洗牌（`:445-448`）→ 用完即删；调度耗尽自增 epoch 重生成（`:462-466`）。`reset_seed`（`:487-512`）与 `_assert_seed_rank_symmetric`（`:514-537`）把不变式落成 fail-fast。

**DatasetFactory.build（`factory.py:36-98`）**：断言 `eval_strategy == "no"`（`:40-42`）；rank0 先行生成 stats、其余 rank 屏障等待（`:56-60`）；逐 path 建数据集（`:61-69`）；权重=组内相对长度×mix_ratio（`:71-76`）；alpha 非空且多数据集时替换为幂律权重（`:78-85`）。

## 三、外部连接

向上：`factory.py:46-50` 消费 `config.data.datasets`，`:64` 按 embodiment_tag 索引 modality_configs（05 篇契约层）。向下：`ShardedSingleStepDataset` 组合 loader（`sharded_single_step_dataset.py:152-155`）；processor 统计由 mixture 注入（`:299-303`）。横向：`Gr00tTrainer.get_train_dataloader` 把 mixture 交给 torch DataLoader（`trainer.py:206-218`）；`experiment.py:333-334` 经 `get_initial_actions`（`:571-582`）导出 initial_actions.npz。

## 四、数据流

一次迭代：mixture `__iter__` 取 (dataset_idx, shard_idx) → 后台线程 `get_shard` → 逐 episode 走 loader `__getitem__`（parquet 切片+视频解码+语言合成）→ 逐 step `extract_step_data` 切时间窗、processor 归一化 → shard 就绪后步序洗牌逐条 yield → DataLoader 组批进 GPU。多数据集在 (dataset, shard) 抽样层混合，样本自带 embodiment 标签支撑跨本体训练。

## 五、设计决策

1. **shard 化而非逐样本索引**：episode 解码昂贵，1024 步一 shard 摊薄成本；shard 内步序再洗牌（`:445-448`）部分找回随机性。
2. **权重除以平均 shard 大小（`:334-337`）**：朴素按权重抽 shard 偏向小 shard 数据集，这步把采样单位校正回"步数"。
3. **种子对称性从文档走向断言（`:514-537`）**：per-rank 种子是静默腐败源（loss 正常、eval 劣化 `:182-186`），all_gather 变构造期异常——教科书级防御。
4. **resume 改重播种不跳数据（`trainer.py:181-192`）**：IterableDataset 无法 seek，用 `seed+global_step` 换随机流，代价是不可精确复现（`:193-195`）。
5. **统计合并按 embodiment 分组（`:269-282`）**：各本体归一化独立，避免 G1 关节范围污染 SO100；单线程预取（`:418`）显存可控。
## 六、新人提示

- `episode_sampling_rate=0.1` 语义是"每 episode 分层抽 10% 的步"（`:186-193`），不是丢 90% 的 episode。
- 首轮每 shard 打印 "Caching shard..."（`:468`）与等待秒数（`:437`），首轮慢是预期。
- stats.json 缺失报错在 loader 构造期（`:180-182`），但 factory 已在 rank0 自动跑 `generate_stats`（`factory.py:57-60`）。
- `allow_padding=False`（默认）时 episode 尾部不足 horizon 会在 `extract_step_data` 越界；effective length 已扣 action_horizon（`:233-236`）。
- modality 键拼错不爆炸，而是空列+warning（`:340-342`），最终以形状错误出现在 processor/模型，排查从这行开始。
