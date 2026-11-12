# 精讲：src/plot.py —— t-SNE 可视化三件套

> 锚基线：仓库 @6e5352b2；行号引自 `src/plot.py`（165 行），全部经源码核实。

## 1. 角色定位

采样结果的"眼睛"：三个纯绘图函数把高维嵌入上的聚类/采样结果投到 2D 让人看。不做任何计算采样逻辑，但承载了两个工程细节——cuml/sklearn TSNE 的**运行时双后端**与 **t-SNE 万点抽稀约定**。被 notebook 的可视化段消费（cell 20/25/31）。

## 2. 内部结构

- `plot_tsne`（`src/plot.py:28`）：原子散点绘制器。按 `np.unique(y)` 分组（L49），-1 噪声簇灰点 s=0.1（L53）；大簇（`counts[label+1] > min_size`，L55）s=10 且进图例，小簇 s=1 静默（L58）——"只给大簇名字"的降噪设计。图例句柄统一改 marker 尺寸 30（L62-63），关坐标轴（L65）。
- `plot_dbscan_results`（`src/plot.py:71`）：DBScan 全景图。`S = len(embeds) // 10000` 抽稀步长（L89，docstring L80 明言"~10000 points for t-SNE to converge"）；`TSNE(n_components=2, **tsne_params).fit_transform(embeds[::S])`（L91-93）；cuml 返回 cuDF 时的 `.values.get()` 兼容（L96-98）；20x20 画布（L100）。
- `plot_coreset_results`（`src/plot.py:105`）：采样前后对照。核心技巧在 `kept_tsne = np.sort(np.unique(np.concatenate([np.arange(len(embeds))[::S], coreset_ids])))`（L127-128）——抽稀下标与 coreset 全量索引**取并集**，保证被采样点（哪怕未被抽稀命中）全部进 t-SNE；`kept_coreset` 记录它们在新下标序列中的位置（L129-131）；一次 fit_transform 后左右两联 subplot 分别画全体与仅 coreset（L145-163），共享同一投影坐标系，簇覆盖差异一目了然。

## 3. 外部连接

依赖 matplotlib + numpy + TSNE（`src/plot.py:22-25` 的 try cuml/sklearn 回退是文件级唯一条件导入）。项目内：README documents 边（结构清单 `README.md:86`）、requirements related 边（matplotlib 行 `requirements.txt:3`）、notebook 两处调用（cell 20 `plot_dbscan_results(...)`、cell 25 `plot_coreset_results(...)`，图谱 calls 边）。与 `src/coreset.py` 无直接代码依赖——两者只在 notebook 汇合。

## 4. 数据流

输入三类：嵌入矩阵（抽稀后送 TSNE）、簇标签 y（`::S` 同步抽稀，L101）、簇规模 counts（决定图例门槛）。`plot_coreset_results` 多一路 coreset_ids 索引流，经并集-去重-排序-回定位四步映射到抽稀坐标系的行号。输出纯副作用（plt.show），无返回值——notebook 内联使用形态。

## 5. 设计决策

- **双后端回退在导入期**（L22-25）：cuml GPU 版优先，sklearn 兜底——与 coreset.py 的 DBScan 降级（运行期 try）相位不同：TSNE 导入失败直接换库，DBSCAN 导入失败改初始化策略，各自匹配"功能等价可替换"vs"功能缺失需改路"的语义。
- **抽稀而非采样**：`[::S]` 等距抽稀保序保分布形态，比随机抽样更稳地保留 t-SNE 的全局结构观感；代价是 coreset 对照图需要并集技巧补偿（被采样点可能恰好落在抽稀空洞）。
- **counts[label+1] 的偏移约定**：与 coreset.py 的 `bincount(y+1)`（`src/coreset.py:127`）共享"噪声簇占第 0 桶"的隐式契约——跨文件的数组语义对齐，改一处必须同步另一处。
- min_size=100 默认值两函数一致（L33/L75/L109），是 Wikipedia 演示调出的经验值。

## 6. 新人提示

读图顺序：先 `plot_dbscan_results` 看簇结构，再 `plot_coreset_results` 看采样覆盖；改 `min_size` 观察图例噪声；复用 `plot_tsne` 时记得传 counts 且标签含 -1。坑：`tsne_params` 直接透传（L91/L134），cuml 与 sklearn 参数名不完全兼容（如 method/n_neighbors 差异），跨后端传参要查各自签名；`.values.get()` 兼容垫片在 L96 与 L138 出现两次——新加绘图函数时别漏抄。

*（六节结构，不计空格约 1600 字符，锚 18，2026-11-07）*
