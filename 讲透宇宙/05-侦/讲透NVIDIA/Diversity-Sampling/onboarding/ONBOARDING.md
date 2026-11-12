# Diversity-Sampling 新人导览（ONBOARDING）

> 图谱基座：`.understand-anything/knowledge-graph.json`（21 节点/34 边/7 层/12 步 tour，@6e5352b2）。全部行号锚经源码核实（2026-11-07）。

## 1. 项目速览

NVIDIA 开源的**主动学习多样性采样**参考实现（Apache-2.0，RAPDS 团队维护）：给定一组高维嵌入向量，用"coreset 最远点贪心"选出一个既覆盖各聚类模态、又保留离群点的代表性子集。核心卖点是**GPU 加速**——距离计算全部在 torch 张量上完成，DBScan 初始化可选 cuML GPU 版。全部核心逻辑收敛在一个 193 行的类里（`src/coreset.py:24` 的 `CoresetSampler`），配套一个 Wikipedia 子集演示 notebook（`notebooks/Demo_wiki.ipynb`，34 个 cell）、三个 pytest 性质测试（`tests/test_coreset.py:22`）和一条 GitHub Actions 流水线（`.github/workflows/python-app.yml:1`）。

为什么需要它（README `README.md:30` 动机节）：大数据集往往带强偏置——训练想用有限样本泛化，评测想让指标更稳健，两者都要"多样子集"。coreset 问题本身 NP-hard（`README.md:11`），所以工程上用两个技巧做近似：距离搬到 GPU 算；每步只算新点到全量的距离、与历史最小值取 min（`README.md:20`），把 O(m²·n) 压成 O(m·n) 次距离计算。

## 2. 算法核心：coreset 最远点贪心

数学形态：对数据集 $D \in \mathbb{R}^{n\times d}$ 构造子集 $S$（|S|=m），每步追加 $\hat{x} = \arg\max_{x \in D} \min_{s \in S} \|x - s\|$——离已选集最近距离最大的点。直觉：贪心地"撒网"，天然偏向还没被覆盖的区域，因此离群点和稀疏模态必被选中。

三段实现：

- **构造与降级**（`src/coreset.py:47` `__init__`）：绑定 `n_samples/initialization/device/random_seed`，`np.random.default_rng(seed)` 保证确定性。`initialization=="dbscan"` 时 `from cuml import DBSCAN`（`src/coreset.py:80`），ImportError 打印提示并静默降级为随机初始化——cuML 是可选依赖（`requirements.txt:11` 注释 "OPTIONAL BUT RECOMMENDED"）。
- **初始化**（`src/coreset.py:92` `initialize`）：默认随机一点；DBScan 模式下 `fit` 全量嵌入取 `labels_`（兼容 cuDF Series 的 `.values.get()` 分支在 `src/coreset.py:123`），`np.bincount(y+1)` 把 -1 噪声簇挪到第 0 桶后按簇规模降序**每簇随机取一点**做种子。README 的理由（`README.md:26`）：DBScan 不用指定簇数、也不必给每个点归簇。
- **主循环**（`src/coreset.py:136` `sample`）：嵌入 `torch.from_numpy(...).to(device)`（`src/coreset.py:164`）；多初始点时先一次性算各点到前 k-1 个种子的距离并 `amin` 成 `min_distances`（`src/coreset.py:169`）；此后每轮只算**新选点**到全量的距离 `new_dist`（`src/coreset.py:181`），`torch.minimum` 增量合并（`src/coreset.py:187`），`argmax` 取最远点入集（`src/coreset.py:190`）。

## 3. 目录与代码地图

```
Diversity-Sampling/
├── src/coreset.py        # 核心：CoresetSampler 类（L24）+ __init__(L47)/initialize(L92)/sample(L136)
├── src/plot.py           # 可视化：plot_tsne(L28)/plot_dbscan_results(L71)/plot_coreset_results(L105)
├── notebooks/Demo_wiki.ipynb  # 端到端演示（34 cell，依赖 Kaggle 数据集）
├── tests/test_coreset.py # 三测试：outliers(L22)/determinism(L42)/std(L63)
├── .github/workflows/python-app.yml  # CI：flake8 语法级 + pytest
├── README.md             # 算法动机与快速上手
├── CONTRIBUTING.md       # RAPDS 式贡献流程
└── requirements.txt      # numpy==1.24.0 锁版；torch 无版本；cuml 可选
```

图谱 7 层对应：文档与依赖 → CI 流水线 → 采样器类型与构造 → 算法主体 → 可视化 → 演示 notebook → 测试。依赖关系只有三条骨架边：`tests/test_coreset.py → src/coreset.py`（imports），`src/coreset.py → tests/test_coreset.py`（tested_by），以及 notebook 经 `sys.path.append('../src/')` 的运行时导入（`notebooks/Demo_wiki.ipynb` cell 6）——最后这条静态扫描器解析不到，图谱中的 depends_on/calls 边为人工补扫并经源码核实。

## 4. 数据流：从嵌入到采样索引

生产路径（库使用者视角）：`np.ndarray 嵌入矩阵 → CoresetSampler.sample() → List[int] 采样索引`。三条数据流变体都在 notebook 里演示过：

1. **聚类视图**：嵌入 + DBScan 标签 → `plot_dbscan_results`（`src/plot.py:71`）先按 `len//10000` 抽稀（t-SNE 收敛要求，docstring 见 `src/plot.py:80`）再降维出图；
2. **对照视图**：`plot_coreset_results`（`src/plot.py:105`）把抽稀下标与 coreset 索引**取并集**后一次 t-SNE（`src/plot.py:127`），左右两联共享坐标系，直接读出簇覆盖差异；
3. **量化对比**：notebook cell 29/30 对 7 个样本量各跑数次，比较 bertopic 主题多样性占比与 domain 分布的 KL 散度——coreset 稳定优于随机采样。

注意 CUML 兼容垫片出现两次（`src/plot.py:96`、`src/plot.py:138`）：cumm/tsne 返回 cuDF 时 `.values.get()` 拉回 host，否则原样使用。

## 5. 关键设计决策

- **贪心而非最优**：coreset NP-hard，接受近似解换取 O(m) 轮 GPU 距离（`README.md:11`）。
- **DBScan 而非 KMeans 初始化**：免簇数、免全量归类；代价是 README 明言的扩展性警告（`README.md:28` "DBScan does not scale well"）。
- **cuml 可选、torch 必选**：两处 try/except 降级（`src/coreset.py:79`、`src/plot.py:22`）让 CPU-only 环境能跑（变慢但正确）。
- **确定性契约**：`random_seed` 参数 + `default_rng`，测试 `test_coreset_determinism`（`tests/test_coreset.py:42`）锁死该契约；但注意 DBScan 初始化路径下 cuML 自身非确定性会破坏它（docstring 明示 "unless dbscan initialization is used"，`src/coreset.py:67`）。
- **notebook 直连源码**：不打包不安装，`sys.path.append` 直接 import——微仓零分发的取舍。

## 6. 测试与 CI

三个测试各锁一条性质：**离群点覆盖**（`tests/test_coreset.py:22` 手埋 x[14,0]=-100 / x[77,1]=100 两个极端点，断言必被选中——最远点贪心的核心卖点）；**确定性**（`tests/test_coreset.py:42` 同种子两次采样 bit 级一致）；**多样性代理**（`tests/test_coreset.py:63` coreset 索引的 std 严格大于等量随机采样）。CI（`.github/workflows/python-app.yml:29`）flake8 只对 E9/F63/F7/F82（语法错误/未定义名）阻断、风格 exit-zero 放行，随后 `python -m pytest tests`（`.github/workflows/python-app.yml:35`）。**但注意：这份 CI 从未运行过**（GitHub API 实证 actions/runs 计数为 0）——触发分支写死 `"master"` 而上游唯一分支是 `main`（见第 7 节勘误 7），且三测试未传 device 参数、默认 "cuda" 在无 GPU runner 上必失败，两个问题因 CI 死配置而互相掩埋。

## 7. 坑与勘误（图谱甄别记录）

1. **README 代码结构树与实际不符**：`README.md:80` 写 `src/input/`（输入数据目录）实际不存在，notebook 期望的是根下 `input/`（`README.md:52`）。
2. **README 快速上手代码引用方式与库不一致**：`README.md:58` 写 `from coreset import CoresetSampler`——只在 notebook 的 sys.path 环境成立；作为库应 `from src.coreset import CoresetSampler`（tests 即此写法，`tests/test_coreset.py:19`）。
3. **dbscan_params 默认可变参陷阱已规避**：签名用 `dbscan_params: Dict = None` + None 时换新 dict（`src/coreset.py:86`），未踩经典 mutable default 坑。
4. **min_distances 初始化只算前 k-1 个种子**（`src/coreset.py:173` 的 `ids[:-1]`）：循环体首轮会用最后一个种子补齐——两段式实现，读代码时容易误以为漏算。
5. **`initialize(force=False)` 的缓存只缓存 dbscan_y**（`src/coreset.py:115`）：返回的 init_ids 每次重新随机抽取，"复用初始化"语义仅指簇标签，不指种子点。
6. notebook cell 4 对 cuml 是**硬失败**（`raise ImportError`），与库里的静默降级策略相反——notebook 假定 GPU 环境。
7. **CI 是从未生效的死配置**（GitHub API 实证，2026-11-07 查询 actions/runs total_count=0）：workflow 触发分支写死 `"master"`（`python-app.yml:8`），而上游默认且唯一的分支是 `main`——push/PR 永不触发。连带效应：三测试构造 `CoresetSampler` 均未传 device（默认 "cuda"，`src/coreset.py:51`），无 GPU 的 ubuntu runner 上 `.to("cuda")`（`src/coreset.py:164`）必抛错——"CI 会兜底测试"的假设不成立，这两个缺陷互相掩埋至今。

## 8. 新人上手路径

1. 读 `README.md` 算法节（10 分钟），建立"贪心最远点 + 增量距离"的心智模型；
2. 直读 `src/coreset.py`（193 行，一个类三个方法，半小时可通读）——先 `sample` 后 `initialize`，对照第 2 节三段实现；
3. 跑 `pytest tests/`（无 GPU 也能过：三测试都不用 dbscan 初始化）；再看 `tests/test_coreset.py:22` 如何用 2 个埋点离群验证覆盖性；
4. 有 RAPIDS 环境时跑 `Demo_wiki.ipynb`（先从 Kaggle 下载数据到 `input/`），重点看 cell 29/30 的量化对比曲线；
5. 想改算法：入口在 `sample` 的 argmax 选择策略（`src/coreset.py:190`）与 `initialize` 的种子策略（`src/coreset.py:129`）两处；改完先补一条性质测试再提 PR（CONTRIBUTING 流程，`CONTRIBUTING.md:36` 起的九步）。

---

*图谱指纹基线 8 文件 @6e5352b2；本文件 8 节，锚 30+，2026-11-07 生成。*
