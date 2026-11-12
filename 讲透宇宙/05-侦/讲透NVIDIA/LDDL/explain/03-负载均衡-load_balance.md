# 03 · 负载均衡器：lddl/dask/load_balance.py（455 行）

> 四阶段流水线的第三阶段：把预处理产出的不均衡 parquet 分片重组成"任意两 shard 样本数至多差 1"的均衡 shard。行号锚均经源码核实。

## 角色定位

Dask 落盘的分片大小只是估计值（pretrain.py:792-793 help 自认"cannot guarantee perfect load balance"），直接给加载器用会导致各 rank 文件数/样本数不齐、迭代末期空转。本文件注册为两个命令（setup.py:71-72）：`balance_dask_output` 主均衡器、`generate_num_samples_cache` 补生成缓存。它的输出形态是下游 torch/torch_mp/paddle 三套 ParquetDataset 的存在前提——torch/datasets.py:142-143 直接断言 `len(file_paths) % num_nodes == 0`、:147 断言 `max == min+1`，不均衡的数据根本跑不起来。

## 内部结构

三个角色类/函数：**Shard**（load_balance.py:41）封装一个输出 shard 的输入文件集 + 输出文件簿记，`num_samples` 属性（:52-60）= 输入文件样本和 + 已落盘输出样本；**Progress**（load_balance.py:159）贪心调度器，初始化时把总样本均分出目标直方图（:163-168：base 与 base+1 两档），`report`（:190-203）每轮把 shard 分成"达标/过小/过大"三类；MPI 封装（:210-223）包住 COMM_WORLD 的 size/rank/barrier/allreduce（:223 用 MPI.IN_PLACE 原地归约）。

## 外部连接

上游消费 `lddl.utils` 的 parquet 发现工具（:35-38 导入）与 `lddl/types.py:26` 的 File 类做元数据货币；下游把 `.num_samples.json`（:377 落盘）留给加载侧当缓存（torch/datasets.py:173 优先读它，免得为统计样本数而读整个 parquet）。均衡按 bin 分组独立执行（main :405 循环），输出带 `_<bin_id>` 后缀（:415）——与预处理期的 `<partition>_<bin_id>` 命名对齐，保证"每 rank 每 bin 文件数相等"这一加载侧不变量。

## 数据流

`_balance` 主循环（load_balance.py:321）①`_build_files`（:226-242）各 rank 按 stride 认领文件读样本数、allreduce 汇总、按样本数排序；②`_build_shards`（:245-254）用 `files[idx::num_shards]` 蛇形分配，天然让各 shard 初始量级相近；③循环至 Progress.completed（:341）：report 分类后，过小 shard 升序、过大 shard 降序（:350-357），配对执行 `larger_shard.balance(smaller_shard, i)`（:361），每次转移 `larger - (larger+smaller)//2` 个样本（:131-133，一轮到位而非逐个搬）；④barrier 同步（:362）后重组列表迭代；⑤收尾 flush（:366）把残余输入文件并进输出 shard。

## 设计决策

- **"同构决策、单点 IO"的 MPI 模式**：全体 rank 持有相同的 num_samples 簿记、执行相同的贪心决策序列，但只有 `idx % world_size == rank` 的 rank 真正读写表（:138 与 :143 的归属判定）。非归属 rank 的 `_store(table=None)`（:84-104）只递增计数不碰磁盘——零通信、零锁、零竞态，是本文件最精彩的一手。
- **IO 即删除**：`_read_table` 在 keep_orig=False 时读完即 `os.remove`（:75-77），均衡过程同时完成原地整理，省一倍磁盘；代价是不可回退。
- **签名陷阱**：`def balance(larger_shard, smaller_shard, idx)`（:129）无 self 也无 @staticmethod，全靠 :361 实例调用时绑定实例恰好落进 `larger_shard` 形参——能跑但脆弱，子类化或改成函数调用都会炸。

## 新人提示

排障先看 rank 0 的迭代日志（:343-349 每轮打印左右集合的均值/方差）。若断言 `f.num_samples == len(table)`（:81）炸了，多半是 `.num_samples.json` 缓存与实际 parquet 失配——删缓存重跑 generate_num_samples_cache（:428）即可。num_shards 的选取必须与训练侧 `num_nodes`（或 dp_size×workers）对齐，否则加载侧 :142 的整除断言失败；官方向导是"一个 rank 一个 shard 一轮"。
