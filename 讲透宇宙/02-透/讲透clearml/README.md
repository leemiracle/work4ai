# 讲透 clearml（MLOps 实验追踪 SDK）

> 2026-10-22 全链收官。DeepWiki 未索引 → understand 图谱是唯一知识源。本地仓 /usr-data/data2/repos/pytorch-landscape/repos/clearml @df0d7477（v2.1.3 系）。

| 产物 | 状态 | 规模 |
|---|---|---|
| 批分析 | ✅ 30/30（62 产物文件含分片；批 4 曾被 429 杀死经 SendMessage 复活零损失） | — |
| 知识图谱 | ✅ 0 issues/0 warnings | **1944 节点/4435 边/16 层/16 步 tour**，fingerprints 508 文件 |
| ONBOARDING | ✅ 8 节 | 7607 去空格字符/62 行号锚 |
| explain | ✅ 12 篇+索引 | 12 篇合计约 59000 字符/474 行号锚（26/26 抽验命中） |

## 流水线纪要

- 30 批 4 并发滚动（10:54-12:05 约 71 分钟，含 1 次 429 复活、1 次 stdlib 误映射批次内自愈）；merge 悬空边 4 条全定位回补（get_tasks 实为 Task 类方法 task.py:1516、exact_match_regex 函数节点漏建补建+tags 补齐、requirements/README 前缀 file:→document:）
- layers 16 层（Vendored 40→Core Utils→Config→Backend API Client 69→Storage→Backend Interface→SDK 门面→Data Mgmt→Bindings→Automation→CLI&Router→Examples 三维拆层（96/39/64）→Docs→Build&CI），508 文件全覆盖零重复
- finalize 0 issues/0 warnings；清理阶段零事故（anomalib 轮的嵌套目录坑未复现）

## 源码级实证勘误（批分析+写作累积）

1. **clearml 仓无 tests 目录**（全仓 find 实证，质量靠 CI workflow+examples 冒烟）——tested_by 边全仓为零属结构事实
2. errata 文档写的 APIClient 导入路径 `session.client` 实际在 `backend_api/session/client/client.py:509`（差一层）；文档片段 `ImportModel` 系笔误（正确为 InputModel）
3. cicd workflow YAML 实际运行的 `check_clearml_task_running.py`/`--script task.py` 磁盘不存在（README 记载为 check_remotely_runnable.py/example_task.py）——文档-workflow 漂移
4. Lightning 集成新旧分代：`lightning.pytorch.*`↔cli.py 新代 / `pytorch_lightning.*`↔old.py 旧代（callbacks class_path 命名空间精确对应）
5. `from collections/enum import ...` 的 stdlib 误映射假边三批出现（batch-9/12/15 各剔除 1-2 条）——scanner 同名目录陷阱钉版
6. AST 符号导入回退规则：`from X import 符号` 必须回退解析到 X/包 __init__.py，否则相对导入全量漏报（batch-6 首跑 ast=4 vs scan=81 假阴性实证）
7. transformer notebook 无 import 级耦合（%env 凭据+!pip install+report_to 三段式）——按运行时依赖发 depends_on 0.6
8. model_embedding.py 示例不 import clearml SDK（grep 实证）；qa_entries_sample.json 全仓零代码引用（孤立演示数据）
9. pynvml.py 为 NVIDIA 官方完整 vendored 绑定（393 导出符号）；pigar/pyhocon/requests-toolbelt/pyrsmi/distutils_version 同为 vendored
10. kerastuner 新旧两版接入方式不同（ClearmlTunerCallback 走 callbacks vs ClearmlTunerLogger 走 Hyperband logger，try/except else 分支内定义 tree-sitter 会漏）
11. HttpRouter 实际在 `clearml/router/`（直觉路径 utilities/http_router/ 不存在）；gpustat 头注释"copied from gpu-stat 0.6.0"严重低估实际改动量
12. pyrsmi 源自 PyTorch ROCm 诊断绑定；AMD 路径的温度/利用率为占位值；huggingface 示例仅 notebook 无 .py
13. vendored 内嵌库共**六个**（jsonmodels/pigar/requests_toolbelt/pyrsmi/pynvml/pyhocon+distutils_version）——pyhocon 常被漏计；pigar 接口已与上游分叉；jsonmodels 内嵌版勿 pip install 同名包替代
14. sdk.conf 顶层无 `sdk{}` 包裹（直接键值）；`trains.conf` 先于 `clearml.conf` 加载（历史兼容）；APIClient 即 apiproxy 角色（apiproxy 文件不存在）；默认 HTTP 方法 GET
15. Task._create_dev_task 有 24h 复用窗口；requirements 探测引擎=vendored pigar；env 探测优先于 CLI；diff 上限 500000B

目录：onboarding/ONBOARDING.md · explain/(12 篇+README) · 图谱在仓内 .understand-anything/knowledge-graph.json
