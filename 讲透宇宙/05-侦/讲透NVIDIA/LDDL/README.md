# 讲透 LDDL

> Language Datasets and Data Loaders：NVIDIA 的 BERT 类预训练数据准备库，最小化数据集检索/预处理/加载摩擦。四后端架构：dask（分布式 ETL）/ torch / torch_mp（多进程）/ paddle，加 benchmarks、examples 与 Docker/Slurm 部署件。

## 全链状态表（2026-11-08）

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析 | ✅ 5 批（6 文件，批 1 拆 2 part） | 194 节点 / 384 边 |
| merge | ✅ | 批内去重 383 + importMap 恢复 16 = 399 边，零真悬空 |
| layers/tour | ✅ | 9 层（配置文档→共享基础库→下载器→Dask 引擎→BART/负载均衡→torch→torch_mp→paddle→基准部署）/ 14 步 |
| finalize | ✅ validator 0/0 | knowledge-graph.json（194n/399e） |
| fingerprints | ✅ | 50 files @ e4006d2b |
| onboarding | ✅ | ONBOARDING.md 4996 字 / 37 锚 |
| explain | ✅ 3 篇 | pretrain（2323 字/7 锚）/ random（1960 字/8 锚）/ load_balance（2116 字/8 锚） |
| 锚终验 | ✅ 真坏 0 | 60 锚；24 个 FILE_NOT_FOUND 全为多后端同名文件（pretrain.py×2、datasets.py×3、dataloader.py×3）消歧缺口，内容验证行号界内且语义同源（各后端为移植拷贝） |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/LDDL/.understand-anything/knowledge-graph.json`。

## 源码甄别（写作期实证）

1. **884 行核心文件是 `lddl/dask/bert/pretrain.py`**——`lddl/dask/bert.py` 路径不存在（派发任务书路径笔误，按源码修正）。
2. **`_truncate`（pretrain.py:144，连同 _cut/_adjust 子词边界保护）为死代码**——实际生效的是 `_truncate_seq_pair`（:161）。
3. **`Shard.balance`（load_balance.py:129）既无 self 也无 @staticmethod**——靠实例绑定填槽位才能正确工作，怪异设计。
4. setup.py:56/:60 重复声明 wikiextractor（PyPI + git 双条目）。
5. pretrain.py:481 实例级 monkey-patch 覆写 `pairs.to_dataframe`。
6. `--wikipedia-lang` choices 含 zh 但 help 自认仅支持 en。
7. **scanner 系统性 stdlib 撞名误解析（17 条假边已剔除）**：`import random/torch/paddle` 分别被解析到项目内 `lddl/random.py`、`lddl/torch/__init__.py`、`lddl/paddle/__init__.py`，其中 lddl/random.py 产生自引用边；真值以 `from lddl.xxx import` 显式语句为准。
8. 血统：bert/pretrain 算法源自 Google BERT create_pretraining_data 移植；binning.py 内联 dask 源码（DASK_LICENSE）；`lddl/random.py` 的 rng_state 显式传递=全库确定性洗牌基石（多 worker 断点续跑可复现）。
9. setup.py 注册 8 个 console_scripts（build/preprocess/balance 等全家桶入口）。

## 阅读路线

`onboarding/ONBOARDING.md` 八节；深读 explain 三篇：01 dask/bert/pretrain.py（BERT 预处理核心）→ 02 random.py（rng_state 确定性洗牌）→ 03 load_balance.py（「同构决策、单点 IO」MPI 负载均衡——全库最独特的工程设计）。
