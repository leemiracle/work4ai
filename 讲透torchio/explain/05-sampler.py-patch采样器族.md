# 05 · `src/torchio/data/sampler.py`：patch 采样器族与 GridSampler

## 一、角色定位

这个文件定义"从体积里取 patch 的一切方式"：基类 `PatchSampler`（`sampler.py:23`）约定协议，四个实现分两派——`GridSampler`（`sampler.py:70`）在规则网格上稠密切块，服务于**推理**（保证全覆盖无死角）；`UniformSampler`（`sampler.py:171`）、`WeightedSampler`（`sampler.py:226`）、`LabelSampler`（`sampler.py:288`）随机抽样，服务于**训练**，分别对应均匀、按概率图加权、以标签前景为中心三种先验。它们与 Queue（04 篇）、`PatchAggregator`（`src/torchio/data/aggregator.py:12`）构成 patch 三件套：采样器切块、Queue 缓冲、聚合器拼回。

## 二、内部结构

375 行，一基类四采样器两辅助函数：

**`PatchSampler`**（`sampler.py:23`）：`__init__`（:31）把 int patch_size 广播成三元组；`__call__`（:36）是协议本体，子类必须覆写（基类直接 `NotImplementedError`，:51-52）；共享的 `_extract_patch`（:54）是切 patch 的唯一实现——`location.to_slices()`（:60）把 `PatchLocation`（`src/torchio/data/patch.py:11`）转成 slice 三元组，对每张图 `image[:, si, sj, sk]`（:63，走 02 篇的懒切路径），元数据原样透传（:64-65），并把 `patch_location` 写进新 Subject（:66）供聚合器对账。

**`GridSampler(PatchSampler, Dataset)`**（`sampler.py:70`）：注意双继承——它是 **map-style Dataset**（有 `__len__` :114 与随机访问 `__getitem__` :117），可直接交给 `DataLoader` 做批量推理。`__init__`（:97）接受 `patch_overlap`（相邻块重叠，须为偶数）与可选 `padding_mode`（:102，非 None 时 `_maybe_pad` :120 用 `Pad` 在四周补 `overlap//2`，:125-133，采样完的块在聚合时裁回）。核心是 `_compute_locations`（:142）：每轴 `step = max(patch - overlap, 1)`（:153）生成起点序列，**末块强制对齐到 `size - patch`**（:155-156 的补尾逻辑），保证边缘体素一定被某个 patch 完整覆盖——推理不漏块的数学保证。三轴笛卡尔积生成全部 `PatchLocation`（:159-167）。

**随机派三兄弟**：都是 `IterableDataset` 混入、都实现 `__call__(subject, num_patches)` 与 `__iter__`（:212/:276）。`UniformSampler` 均匀抽：`_random_index`（:215）每轴 `torch.randint(0, size - patch + 1)`（:220-221）。`WeightedSampler` 按图加权：把 subject 内名为 `probability_map` 的图像转成概率体（`_build_probability_map_for` :279），`torch.multinomial` 抽中心体素（:267），`np.unravel_index` 还原三维坐标（:269），再经 `_center_to_corner`（:271，实现在 :363）把中心换算成合法角点（:372-373 的 clamp）。`LabelSampler`（:288）是其子类，只重写 `_build_probability_map_for`（:320）：按 `label_probabilities` 字典给每个标签值赋权（:326-327 `prob[label_data == label] = weight`），无字典时全部非零标签等权（:329 `(label_data > 0).float()`）——类别不平衡时保证 patch 含前景。

**辅助**：`_mask_borders`（:342）把"放不下完整 patch 中心的边缘带"概率清零（:352-359），防止 multinomial 抽到边界后角点被 clamp 引入偏置；全零概率图在 `WeightedSampler.__call__` 里显式报错（:260-262）。

## 三、外部连接

- **上游**：`PatchLocation`（:16）与 `Subject`（:17）；`Pad` 仅在 TYPE_CHECKING 外的函数体内延迟导入（`sampler.py:123`），避免 data 层对 transforms 层的环向依赖。
- **下游**：Queue 以 `PatchSampler` 类型注解持有任意采样器（`queue.py:19`）；推理侧 `PatchAggregator.add_batch`（`aggregator.py:76`）吃 `(batch, patch_location)` 对，overlap 融合有 crop/average/hann 三模式（`aggregator.py:21-38`）；`Image.__getitem__` 的懒切（`image.py:901`）是 `_extract_patch` 高效的底层原因。
- **文档**：`docs/how-to/patch-inference.md`（GridSampler+Aggregator 完整配方）与 `docs/tutorials/large-volumes.md`；图谱 fan-out 20 大多指向这些使用方。

## 四、数据流

推理链走读（`GridSampler`）：

1. `sampler = tio.GridSampler(subject, patch_size=64, patch_overlap=8)` → `_compute_locations`（:142）算出如 `(I-64)/56+1` 每轴取整的三维网格，全部角点入 `self.locations`。
2. `DataLoader(sampler, batch_size=4)` 逐 index 调 `__getitem__`（:117）→ `_extract_patch`（:54）→ 各图 `image[:, si, sj, sk]` 懒切 → patch Subject 携带 `patch_location`。
3. 模型输出 `outputs` 后 `aggregator.add_batch(outputs, batch.patch_location)`（官方示例 `sampler.py:93`），聚合器按 location 写回大缓冲。
4. `aggregator.get_output()`（`aggregator.py:101`）得整卷预测；重叠区按 overlap_mode 融合。

训练链（`LabelSampler` + Queue）：`Queue._sample_patches`（`queue.py:164`）调 `iter(self.patch_sampler(subject))` → `__call__` 循环抽中心→换角点→切块，`islice` 截断到 `patches_per_volume`——每卷每 epoch 抽到的前景 patch 集合都在变。

## 五、设计决策（含批判）

**"map-style 推理 / iterable 训练"双继承拆分**是精准的：推理需要确定性全覆盖与随机访问（Dataset），训练需要无限流（IterableDataset）；`__call__` 协议让同一采样器既能进 Queue 又能手动迭代。`_compute_locations` 的补尾对齐（:155-156）看似细节，实则是"推理无死角"的正确性核心——漏掉它，边缘体素永远进不了任何 patch。

批判四点。其一，**重叠边界裁剪的认知成本**：`patch_overlap` 的语义是"相邻块重叠量"，配合聚合器的 crop 模式时输出有效区是中心 `patch-overlap` 部分，新手常误把重叠区当有效预测平均，average/hann 模式才需要真重叠融合。其二，`UniformSampler` 的均匀是**角点均匀**而非体素均匀（:215-223 抽的是起点），小目标在边缘时被采概率系统性偏低——这正是 LabelSampler 存在的理由，但文档未把三者概率语义放在一处对比。其三，`GridSampler._maybe_pad`（:120）用 `padding_mode` 预填边界后，`PatchAggregator` 需知道裁回——两组件间的隐式契约靠文档维系，拼错 overlap 不会报错只会悄悄丢边缘。其四，`_center_to_corner` 的 clamp（:373）与 `_mask_borders`（:342）共同保证合法角点，但当 `patch_size > spatial_shape` 时角点恒为 0，采样退化为反复取同一块，无告警。

## 六、新人提示

1. 训练用随机派（`UniformSampler` 起步，前景稀缺换 `LabelSampler`），推理必须 `GridSampler`——随机采样不能保证覆盖。
2. `patch_overlap` 取 patch_size 的 10-25%（如 64 配 8），配合 `overlap_mode="hann"`（`aggregator.py:21`）能显著缓解拼接缝伪影。
3. 训练侧不需要 GridSampler：Queue + 随机派即可；`GridSampler` 直接进 `DataLoader` 就够了，别再套 Queue。
4. 自定义采样器只需继承 `PatchSampler` 并实现 `__call__` 产出 `PatchLocation` 流，`_extract_patch`（:54）可直接复用。
5. patch_size 每轴都要 ≤ 各模态 `spatial_shape`（Subject 一致性校验保证各图同形），否则随机派恒取角落块、GridSampler 直接空网格。
