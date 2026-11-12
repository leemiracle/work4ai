# 02 · 确定性洗牌基石：lddl/random.py（55 行）

> 全库最小（去掉 24 行 MIT 许可证头只剩约 30 行）却支撑三套加载后端的可复现性。行号锚均经源码核实。

## 角色定位

`lddl/random.py` 解决一个分布式数据加载的经典难题：多个 DataLoader worker、多个 bin、多个随机决策点共享同一个 Python 全局 `random` 时，谁先消费随机数谁的序列就变——顺序不可复现且互相污染。它给出的答案是**把 RNG 状态当值传递**：randrange/shuffle/sample/choices 四个函数（random.py:34/:40/:46/:52）都接受可选 `rng_state`，用完把新状态返回给调用方继续接力。图谱中它 fanIn=10，是 torch/torch_mp/paddle 三套 datasets 与 dataloader 的共同依赖。

## 内部结构

全部机关在 `_swap_rng_state`（:28-31）：保存全局 random 当前状态→换入调用方给的状态→执行→把旧状态换回并返回执行后的新状态。四个公开函数全是同一模板的三行变体：`shuffle`（:40-43）原地洗牌并返回新状态；`sample`/`choices`/`randrange` 返回 (结果, 新状态) 二元组。`import random`（:25）在 Python 3 绝对导入下解析到 stdlib——这也是图谱 scanner 曾把全库 `import random` 误连到本文件、产生 17 条假边的撞名根源（本文件自身还产生了自引用假边，已剔除）。

## 外部连接

消费者分两级：**world 级**（所有 rank 必须做出完全相同的决策）——torch/datasets.py:227 `_world_identical_sample` 用 `sample(files, k=len(files), rng_state=self._world_rng_state)` 让每个 rank 拿到同一份文件洗牌序；torch/dataloader.py:64 `_choices` 让各 rank 以同一 `world_rng_state` 加权选同一个 bin。**worker 级**（各 worker 独立）——datasets.py:74-79 ShuffleBuffer 的 `_randrange`/`_shuffle` 携带自己的 rng_state 链。

## 数据流

状态的生灭周期在 `ParquetDataset._init_rng_states`（torch/datasets.py:247-256）：先暂存全局状态，`seed(base_seed + epoch)` 派生 world 态（:250-251），再 `seed(base_seed + (epoch*world_size + rank)*nworkers + worker_rank)` 派生 worker 态（:253-255），最后恢复全局状态（:258）——函数本身零副作用。之后每个 `__iter__`（:260）里，world 态驱动"全体一致的文件顺序"（:266），worker 态注入 ShuffleBuffer（:283）驱动"各自的弹出顺序"。Binned 选桶同理：`_init_rng_states`（torch/dataloader.py:44-50）按 epoch 派生，`__iter__` 内每次 `choices(bins, weights=剩余样本量)`（:79-83）选桶后更新状态。

## 设计决策

- **为什么换状态而不是传 Random 实例**：状态是可 pickle 的元组，能随对象进 DataLoader worker 进程边界，也能作为纯值在函数间接力，避开全局单例的竞态；代价是每次调用两回 setstate 的小开销——对数据加载频率（每样本一次）完全可接受。
- **权重即进度**：Binned 选桶的 weights 用"各桶剩余样本数"（dataloader.py:81），使全局样本流在桶间均匀展开，桶耗尽自然降权——无需中心调度。
- **确定性边界诚实**：本文件只保证加载侧洗牌可复现；预处理侧（dask worker 内的 stdlib random）仍非确定，二者不要混为一谈。

## 新人提示

改动任何消费方时切记：rng_state 必须按"返回值接住再传回"的接力方式用（对照 datasets.py:75-79 的 `_randrange` 写法），漏接一次状态就会让后续序列分叉且极难排查。调试时可打印 `_world_rng_state` 的前几个字节验证各 rank 是否一致。若要给新后端（如 JAX）加支持，直接复制 torch 版 datasets/dataloader 的 rng 接线即可——三套现有后端就是这么互相"复制-改框架 API"的。
