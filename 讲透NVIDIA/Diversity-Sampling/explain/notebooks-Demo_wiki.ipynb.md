# 精讲：notebooks/Demo_wiki.ipynb —— Wikipedia 子集端到端演示

> 锚基线：仓库 @6e5352b2；锚格式为 cell 序号（34 cell 全读核实）+ 关联源码行号。

## 1. 角色定位

仓库的"验收现场"：34 个 cell 把 src 两模块串成完整故事——读 Wikipedia 文章嵌入 → DBScan 初始化 coreset 采样 → 浏览 top 簇样文 → **coreset vs 随机采样的量化对比**（多样性占比 + KL 散度，7 个样本量）。README 承诺的 "Refer to the notebook for more details"（`README.md:72`）全部兑现于此。数据来自 Kaggle `theoviel/diversity-sampling-demo-data`（`README.md:52`），需放 `input/`。

## 2. 内部结构

四段式：**环境段**（cell 3-6）——import 全家桶、`try: import cuml` 硬失败（cell 4 `raise ImportError`，与库内静默降级相反）、`assert torch.cuda.is_available()`（cell 5）、`sys.path.append('../src/')` 后 `from coreset import CoresetSampler; from plot import plot_dbscan_results, plot_coreset_results`（cell 6）。**数据段**（cell 8-10）——`pd.read_parquet('../input/df.parquet')`、`np.load('../input/embeds.npy')`；df 含 title/text/domain/bertopic_class 列。**采样段**（cell 12-25）——EPS=0.85/MIN_SAMPLES=100/N_SAMPLES=1000 三参数（cell 12），构造 `CoresetSampler(n_samples=N_SAMPLES, initialization="dbscan", dbscan_params={...}, tqdm_disable=False, verbose=1)`（cell 13，对应 `src/coreset.py:47` 签名）；`%%time` 跑 initialize（cell 15）；数簇、看 top-10 簇规模（cell 17-18）；`plot_dbscan_results` 出全景（cell 20）；cell 22 逐簇抽样文浏览。**对比段**（cell 26-33）——`ids = coreset.sample(embeds)`（cell 24）、前后对照图（cell 25）；N_TEXTS=[100..5000]（cell 27），**重建** `CoresetSampler(initialization="", dbscan_params={"eps": EPS, "min_samples": MIN_SAMPLES}, tqdm_disable=True, verbose=0)`（cell 28，注意 `initialization=""`——对比实验用的是随机单点初始化的纯贪心 coreset，dbscan_params 传了但不生效）；coreset 臂每 n 跑 3 次取均值（cell 29，注释 "3 -> 1 for faster execution"），随机臂跑 10 次（cell 30）；度量=主题多样性 `len(unique bertopic_class)/n` 与 domain 分布对均匀分布的 KL 散度 `Σ p·log(p·K)`（cell 29 同一循环内）；画曲线收尾（cell 31-32），结论 cell 33：采样文本比随机更好捕捉数据集多样性。

## 3. 外部连接

运行时导入 `src/coreset.py` 与 `src/plot.py`（cell 6 的 sys.path 方式——静态扫描器解析不到，图谱 depends_on/calls 边为手补并核实）；数据依赖 Kaggle parquet+npy 双文件；README documents 边指向本文件（`README.md:83` 结构清单）；CI 不覆盖 notebook（`python-app.yml:35` 只跑 tests）。

## 4. 数据流

parquet 元数据（df）与 npy 嵌入（embeds）平行流入：embeds → CoresetSampler（fit/采样）→ ids；df.iloc[ids] → 采样子集 df_s → 两度量。DBScan 标签 y 与 counts 从 `coreset.dbscan_y` 取出（cell 16）复用于簇浏览与绘图——`initialize` 的缓存语义（`src/coreset.py:115`）在此被实际消费。对比段的 KL 散度以 domain 列的经验分布对均匀基线计算，衡量"采样是否偏科"。

## 5. 设计决策

- **量化而不止看图**：t-SNE 图观感 + 双指标曲线互证——KL 散度选均匀基线（而非全量分布）使"越低越均匀多样"的解释直观；这是演示说服力的核心设计。
- **两臂实验次数不对称**（3 vs 10，cell 29/30）：coreset 确定性高（同种子同输出）3 次足够，随机臂需要更多次压方差——次数选择本身就是对算法性质的注释。
- **cell 28 对比臂刻意 `initialization=""`**：量化对比用的是随机单点初始化的**纯贪心 coreset**（dbscan_params 原样传入但因 initialization 为空而不生效）——把 DBScan 初始化的贡献从对比中剥离，只测最远点贪心本身的多样性收益，是干净的消融设计；README 里 DBScan 初始化的卖点并未进入这条对比曲线。
- **硬失败环境断言**：cell 4/5 直接 raise/assert，宁可不跑也不慢跑——演示的可信度优先于可达性。

## 6. 新人提示

复现路径：下 Kaggle 数据 → `input/` → 装 RAPIDS + GPU torch → 从头跑；无 GPU 时 cell 5 即断。想换自己的数据：只需 df（含可数类别列）+ embeds.npy 同长对齐，把 domain/bertopic_class 换成自己的元数据列。注意 cell 29 注释里的 "3 -> 1" 是作者的提速改动痕迹——正式复现实验建议恢复更多次取均值；另外 notebook 会**原地**消耗 `coreset.dbscan_y` 缓存，重复运行对比段前重跑 cell 13/15 以避免 stale 状态。

*（六节结构，不计空格约 1900 字符，锚 20+，2026-11-07）*
