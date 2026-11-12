# 讲透 GFMBench-api（NVIDIA Genomic Foundation Model Bench）

基因组基础模型（GFM）基准测试套件：一套标准化接口横跨分类/变异效应预测/零样本评测等下游任务（论文 bioRxiv 2026, doi:10.64898/2026.02.19.706811）。

## 全链状态表（2026-11-07 实例B）

| 阶段 | 状态 | 产物 |
|---|---|---|
| prepare | ✅ | 102 文件/8 批（既有） |
| 批分析 8 批 | ✅ | 279n/677e（imports 204=202 scanner+2 手扫全对账；scanner 对 Python 近乎零漏报） |
| 终验 | ✅ | 0 问题/0 重复 ID/0 悬空 |
| merge+phase4 | ✅ | assembled 279n/677e → 102 file 级/235 边 |
| layers/tour | ✅ | 10 层/15 步/102 节点全覆盖零交集（含 L01..L10 id） |
| finalize | ✅ | **knowledge-graph.json 279n/677e/10层/15步，issues=0 warnings=0，fingerprints=102@a80bde0f（444 锁）** |
| onboarding | ✅ | onboarding/ONBOARDING.md 7864 字 8 节 55 锚（0 坏） |
| explain | ✅ | 3 篇 17,498 字符/65 锚（0 真坏） |
| README | ✅ | 本文件 |

图谱在仓内：`/usr-data/data2/repos/agent-repos/NVIDIA/GFMBench-api/.understand-anything/knowledge-graph.json`

## 十层架构

L01 文档依赖(5) → L02 通用工具日志(8) → L03 任务抽象协议(13) → L04 评测指标库(19) → L05 结果聚合(2) → L06 有监督任务(14) → L07 零样本任务(10) → L08 CLI 入口微调(4) → L09 模型适配器示例(8) → L10 测试夹具(19)

## explain 索引

1. `explain/01-run-benchmark-pipeline.md` — run_benchmark 执行链（importlib 动态加载/任务循环/聚合/日志线）
2. `explain/02-task-hierarchy.md` — 任务基类族谱与双契约（BaseTask 族谱/BaseGFMModel 7 方法/具体任务深案例）
3. `explain/03-metrics-and-testing.md` — 17 指标类体系与测试金字塔（mock//fixtures/sanity 基线）

## 源码级甄别清单（钉版）

1. **TASK_REGISTRY 22 项=12 有监督（全分类）+10 零样本**；任务类实为 23（有监督 13+零样本 10），唯一未注册=lrb_cage_task.py:32 回归（微调器仅支持分类，run_benchmark.py:388-390 NotImplementedError）。
2. **BaseGFMModel 契约=6 @abstractmethod+infer_sequence_to_regression**（base_gfm_model.py:59 非抽象默认 None）。
3. **模型适配器混合继承风格**：显式继承 BaseGFMModel（dna_bert/ntv3/isolated_mock）vs 纯鸭子类型（dna_bert2=nn.Module/hyena_dna/evo2=普通类）——"零 import 适配器"表述需精确化。
4. **brca1 的 predict_evo2 三函数（_run_predict_evo2/_write_dedup_fasta/_load_predictions）全仓零调用**（brca1_task.py:324-358）——离线批量打分预留，未接线。
5. **logutils.get_log_prefix if/else 写反 bug**（:407/:414-415：显式传 log_path 反得 "unknown"），且 get_log_prefix/get_stamp_from_log 全仓零调用者（死代码区潜伏 bug）。
6. **bend_vep 双文件 docstring 同错**：写 1048576bp 实返 512（从 traitgym/brca1 模板复制残留；brca1 本尊 :65-66 确为 1048576）。
7. **traitgym 孪生精确 5 处差异**（:127/:129/:152/:155/:163），共享 helper _load_traitgym_dataset（:53-122）整段复制。
8. **padding 越界字符分裂**：pad_sequence 用 N、pad_sequence_centered_variant 用 P（preprocutils.py:74 vs :140）。
9. **Evo2 强制 --linear_prob**（run_benchmark.py:296-297+evo2_model.py:94）；MODEL_REGISTRY 7 条目对应 6 适配器类（NTv3_8M/100M 共用模块）。
10. **tests/README 计数漂移**：caching 单测自称 13 个实为 11（grep -c "def test_"）。
11. run_benchmark.py:147 importlib 动态加载（非常量参数）6 适配器；isolated_mock 的 --worker 分支在导入宿主依赖前 SystemExit（隔离机制核心）。
12. conftest fixtures_root 整树 shutil.copytree；ipynb monkey-patch 双套同名 infer_*（RandomMockModel cell10-20/SimpleNTv3Model cell34-44）。
13. heavy 基线动态命名 f"{safe}_sanity_baseline.csv"（test_heavy.py:103）；atol 双轨（写基线 0.005:52/缺列兜底 0.02 baseline_utils.py:76）。
14. gfmbench_api/__init__.py 与 tasks/__init__.py 是内容相同的双 barrel（各再导出 10 基类）；utils/__init__.py 是纯 SPDX 空文件非 barrel。

## 流水线备注

- 台账：仓内 `.understand-anything/PROGRESS.md`
- 字数口径：不计空格字符；explain 5.3-6.3K（系列 norm）
- 锚归位记录：explain 02/03 的 `…` 简写锚 14 处已改写为 `gfmbench_api/tasks/base/base_gfm_*` 全路径（真实文件名带 base_gfm_ 前缀）
