# 04 · `src/torchio/data/queue.py`：Queue——随机 patch 训练缓冲

## 一、角色定位

`Queue`（`queue.py:23`，`torch.utils.data.IterableDataset` 子类）是 patch 化训练的调度中枢：把"加载 subject → 应用增强 transform → 按采样器抽 patch"整条链放到后台线程执行，以 `max_length` 为上限缓冲产出，对下游就是一串可迭代的 Subject。它解决的是医学影像训练的经典矛盾——整卷太大装不下显存、逐 patch 现算又喂不饱 GPU：Queue 用"整卷级增强 + patch 级缓冲"折中，让 `DataLoader`/`SubjectsLoader`（`src/torchio/loader.py:39`）始终有货可取。docstring（`queue.py:24-27`）一句话概括职责：loads and preprocesses subjects in background threads, extracts random patches via a sampler。

## 二、内部结构

208 行，一个类，两个协作路径：

**构造**（`queue.py:65-91`）：九个参数里四个决定行为——`patch_sampler`（必须接受 `subject` 与 `num_patches` 的可调用，即 05 篇的采样器）、`max_length`（缓冲上限，默认 300）、`patches_per_volume`（每卷最多抽几个 patch，默认 10）、`num_workers`（后台线程数，0 为同步）。`subject_sampler`（:75）接受任意 `torch.utils.data.Sampler`（如 `DistributedSampler`）接管 subject 顺序，此时 `shuffle_subjects` 必须 False，构造期即校验（`queue.py:77-82`）。

**迭代双路径**：`__iter__`（:93）每次 epoch 重建迭代器，按 `num_workers` 分流到 `_iter_sync`（:103，串行）或 `_iter_threaded`（:114，`ThreadPoolExecutor` :119 + futures 双端队列 :120）。

**流水线小函数**：`_prepare`（:157）= `subject.load()` + 可选 `transform(subject)`，是唯一重 IO/CPU 的步骤；`_sample_patches`（:164）用 `islice` 截取 `patches_per_volume` 个 patch（:167）；`_drain_if_full`（:145）缓冲达 `max_length` 才放行；`_flush`（:150）可选洗牌（:152-153）后 `buffer.pop()` 清空；`_collect_ready`（:134）只从 futures 队首收已完成的（`futures[0].done()` :140）；`_make_subject_iter`（:169）组装每轮 subject 顺序（sampler 优先、否则拷贝后洗牌）。

**预算属性**：`num_subjects`（:179）、`patches_per_epoch`（:191，上界=两因子乘积）、`max_memory`（:196，按 float32 每体素 4 字节估算：`4 * channels * voxels * max_length`，:199-203）、`max_memory_pretty`（:205，humanize 格式化）。

## 三、外部连接

- **上游**：`PatchSampler` 协议（`queue.py:19` 导入，实现在 `data/sampler.py:23`）与 `Subject`（:20）。Queue 不 import 具体采样器——依赖倒置，任何"可调用且产 patch 流"的对象都能接。
- **下游**：`SubjectsLoader`（`src/torchio/loader.py:39`）+ `collate_subjects`（`loader.py:15`）把它的产出堆成 `SubjectsBatch`；官方用法即 docstring 示例（`queue.py:60`）`SubjectsLoader(queue, batch_size=16)`。
- **transform 边界**：`transform` 参数作用于**整卷**而非 patch（`_prepare` :157-161 里先 transform 后 `_sample_patches`）——增强一次、切块多次，省算力但随机性粒度是"每卷每 epoch 一次"。
- **测试**：`tests/test_queue.py`（图谱 out 边）；文档 `docs/how-to/patch-training.md` 与 `docs/reference/patches.md` 引用它（in 边）。

## 四、数据流

线程路径（`num_workers=4`）一次 epoch 的完整走读：

1. `for patch in queue`（或 DataLoader 驱动）→ `__iter__`（:93）→ `_make_subject_iter`（:169）洗牌产出 subject 流。
2. `_iter_threaded`（:114）起线程池，对每个 subject `pool.submit(self._prepare, raw)`（:123）——4 个线程并行做 load+增强，GIL 由 nibabel/SimpleITK/torch CPU 算子释放，是真并行。
3. 每提交一个就 `_collect_ready`（:124 → :134）：从队首收走已完成的 future，`_sample_patches` 把增强后的整卷拆成 ≤`patches_per_volume` 个 patch 入缓冲。
4. `_drain_if_full`（:125 → :145）：缓冲 < `max_length` 时**不放行**，生成器继续内循环提交下一个 subject；一旦达到上限，`_flush`（:148）洗牌后逐个 `yield buffer.pop()`——生成器停在 yield 处，消费节奏反向节制提交节奏，背压由此形成。
5. subject 流尽后收尾：drain 剩余 futures（:128-130）→ `_flush` 清底（:132）。
6. 下游 `collate_subjects`（`loader.py:15`）把 batch 个 patch 堆叠，模型消费 `batch.t1.data`。

同步路径（:103）结构相同，只是提交与执行合一。

## 五、设计决策（含批判）

**"整卷增强 → patch 采样 → 缓冲洗牌"三层解耦**是本文件最聪明的设计：增强在整卷上做一次（同一卷的全部 patch 共享一次几何增强，保证多模态/标签一致），洗牌在 patch 缓冲上做（跨卷混合），既省算力又保随机性。v2 实现比 v1 简洁得多——用 `ThreadPoolExecutor` + future deque 替代了 v1 手写的条件变量生产者-消费者。

批判视角四点。其一，**缓冲粒度是"全冲全放"**：`_flush` 一次清空整个缓冲（:150-155），epoch 内 patch 供给呈"攒一波、放一波"的脉冲，短 epoch 时等效批间分布不均。其二，**`max_length` 不是硬内存上限**：它只约束 patch 缓冲；futures 里还压着最多"在途 subject 数 × 整卷大小"的增强副本（:123 无界提交直到缓冲满），大卷+高 `patches_per_volume` 时实际内存显著高于 `max_memory`（:196）的估算——该估算也只按 float32 算 patch 本体。其三，**每 epoch 重新增强同一卷**：正确（随机性需要）但意味着 CPU 是持续热点，GPU 快的训练会被 `_prepare` 卡住，官方对策是加线程数或把确定性预处理（重采样等）前移出 transform。其四，`patches_per_epoch`（:191）是上界而非承诺——采样器提前耗尽合法位置时实际产出更少，依赖精确步数的训练循环要用 `len()` 之外的计数器。

## 六、新人提示

1. 标准配方照抄 docstring（`queue.py:52-63`）：`tio.Queue(subjects, patch_sampler, max_length, patches_per_volume, num_workers)` + `SubjectsLoader`。`max_length` 设为 batch_size 的 10-20 倍起步。
2. 分布式训练：传 `subject_sampler=DistributedSampler(dataset)` 并置 `shuffle_subjects=False`（:77 的校验会拦住忘改的人）。
3. 排查 OOM 三问：`max_memory_pretty`（:205）多大？`patches_per_volume` 是否过大？transform 里是否混入了本该离线做的确定性预处理？
4. patch 里的 `patch_location` 键（由 `sampler.py:66` 写入）在推理聚合时是 `PatchAggregator.add_batch` 的必需品——训练时忽略它无妨，调试定位时有它很方便。
5. epoch 概念对 IterableDataset 是弱保证：`num_subjects`（:179）乘 `patches_per_volume` 只是名义值，日志里按实际 yield 数对账。
