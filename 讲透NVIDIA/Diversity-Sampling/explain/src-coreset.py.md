# 精讲：src/coreset.py —— CoresetSampler 贪心最远点采样器

> 锚基线：仓库 @6e5352b2；行号引自 `src/coreset.py`（193 行），全部经源码核实。

## 1. 角色定位

全仓唯一的核心实现文件：一个类 `CoresetSampler`（`src/coreset.py:24`）扛起"从 n 个嵌入向量里选 m 个代表性子集"的全部逻辑。README 的算法描述（贪心 argmax 最远点 + GPU 距离 + 增量更新两个技巧）在这里逐行落地。tests 三测试与 notebook 全部依赖它，CI（`python-app.yml:35`）也只测它——单文件单类的极简架构。

## 2. 内部结构

类内三方法分工清晰：

- `__init__`（`src/coreset.py:47`）：存参数、建 `np.random.default_rng(seed)`（L76）；`initialization=="dbscan"` 时 `try: from cuml import DBSCAN`（L79-83），ImportError 打印一句提示后把 `self.initialization` 置空——**降级而非失败**。成功导入则 `DBSCAN(**dbscan_params)`（L90）。
- `initialize`（`src/coreset.py:92`）：种子集构造。随机路径一行（L112）；DBScan 路径：`fit` 后取 `labels_`——cuML 返回 cuDF Series，走 `.values.get()` 分支（L123），sklearn/cpu 兜底走 except（L125）；`np.bincount(self.dbscan_y + 1)`（L127）把 -1 噪声标签挪到第 0 桶实现跳过，`np.argsort(-counts[1:])`（L128）按簇规模降序，每簇 `rng.choice(np.where(y==label)[0])` 取一点（L129）。`force=False` 且已缓存时复用 `dbscan_y`（L115）。
- `sample`（`src/coreset.py:136`）：主循环。`init_ids is None` 则自动 initialize（L156）；`torch.from_numpy(embeddings).to(self.device)` 上卡（L164）；多种子时**预计算**前 k-1 个种子到全量的距离、`torch.cat(...).amin(1)` 得初始 `min_distances`（L169-175）；循环体每轮只算**最后一个入选点**的距离 `new_dist`（L181），`torch.minimum` 合并（L187），`argmax().item()` 取最远点（L190），append 进 ids。

## 3. 外部连接

上游只有三方库：torch（距离计算）、numpy（rng/索引）、tqdm（进度条，L177 `disable=self.tqdm_disable`）；可选 cuML DBSCAN。项目内下游两条边：`tests/test_coreset.py:19` `from src.coreset import CoresetSampler`（imports 边，scanner 唯一解析到的内部边）与 `tested_by` 反向边；notebook cell 6 经 `sys.path.append('../src/')` 运行时导入（scanner 解析不到，图谱 depends_on/calls 边为手补）。README 文档边（`README.md:60` 的快速上手示例）与 requirements 依赖边（torch 行 `requirements.txt:10`）。

## 4. 数据流

输入 `np.ndarray (n,d)` →（torch 化，device 上）→ 输出 `List[int]` 长度 n_samples。距离状态量 `min_distances` 是数据流的枢纽：形状 `(n,1)`，语义"每个点到已选集的最近距离平方"。注意它是**平方距离**——`((x-y)**2).sum(-1)` 不开根号，argmax 不受单调变换影响，省一次 sqrt。`initialize` 的 DBScan fit 是唯一 O(n·d·邻居) 重步骤（README 警告扩展性差，`README.md:28`）；主循环每轮一次 `(1,d)×(n,d)` 广播减法+归约，GPU 上毫秒级。

## 5. 设计决策

- **增量 min 而非全量重算**：把每轮 O(|S|·n) 距离降为 O(n)——README 称这是两个核心技巧之一（`README.md:20`）。种子预计算段 `ids[:-1]` 刻意排除最后一个种子（L173），因为循环体首轮会补上它——两段式拼接，初读易误以为漏算。
- **平方距离 + torch 广播**：无 kernel 化的纯张量写法，依赖 torch 的 fused kernel；对 10⁵ 量级点足够快。
- **rng 而非全局 random**：确定性契约由 `test_coreset_determinism`（`tests/test_coreset.py:42`）锁死；但 docstring 诚实声明 DBScan 初始化会破坏确定性（`src/coreset.py:67` "unless dbscan initialization is used"）——cuML 的 fit 本身不受此 rng 控制。
- **静默降级 vs notebook 硬失败**：库里 ImportError 降级（L82），notebook cell 4 却 `raise ImportError`——两种策略并存，库要鲁棒、演示要环境正确。

## 6. 新人提示

先读 `sample` 再读 `initialize`（主循环不依赖 DBScan 细节）；对照 `tests/test_coreset.py:22` 的埋点实验理解"离群点必被选中"；改算法优先动两处——种子策略（L129）与选择准则（L190 的 argmax，可换 D-采样/软最大）。**两个实测钉版的坑**：① `CoresetSampler` 的 `device` 默认 "cuda"（`src/coreset.py:51`），三测试构造时都没传 device，`sample` 里 `.to("cuda")`（L164）在无 GPU 机器上会抛错——即三个测试只能在 GPU 机器通过；② 之所以从未有人发现，是因为 **CI 从未运行过**：GitHub API 实证（2026-11-07 查询 actions/runs total_count=0）上游默认分支是 `main`（唯一分支），而 workflow 触发分支写死 `"master"`（`python-app.yml:8`）——`python-app.yml` 是一份从未生效的死配置，"CI 全绿"这一想象中的质量线实际不存在。

*（六节结构，不计空格约 2200 字符，锚 25+，2026-11-07）*
