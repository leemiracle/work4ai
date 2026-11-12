# 讲透 NVIDIA garak —— LLM 漏洞扫描器知识基座

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/garak`（NVIDIA/garak v0.17.1.pre1，HEAD `8d1259ef`）
> 定位：LLM 界的 nmap——probe×generator×detector 扫描矩阵 + 意图分类学 + 报告可视化全链。

## 产物状态表

| 产物 | 状态 | 规模 | 备注 |
|---|---|---|---|
| deepwiki | ✅ 真一百分 | 40 结构页全命中（44 文件含索引/终判） | 2026-10-26 MCP 通道；结构外 11 页为导航滞后增量保留 |
| 知识图谱 | ✅ 全链 | **1690 节点 / 4052 边 / 14 层 / 16 步 tour / validator 0 issues** | fingerprints 861 文件基线 @ `8d1259ef`，图谱在仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ | ONBOARDING.md 195 行 8 节 | 2026-11-08，锚源码逐一核实 |
| explain | ✅ 12/12 | 组 1（01-06 核心链路）+ 组 2（07-12 评测资产线） | 全部行号锚源码核实，六节结构 |

## explain 索引（12 篇）

**组 1 · 核心链路**（CLI→数据总线→三类插件→资源库）：
01-CLI与run核心 / 02-Attempt数据总线 / 03-probes探测族 / 04-detectors探测器 / 05-generators生成器适配 / 06-attacks资源库

**组 2 · 评测资产线**（执行→报告→前端→分析→迁移→数据）：
07-evaluators与harnesses（执行模型+调度闭环；evaluator 判分/harness 四方编排/IntentProbe 动态 detector）
08-report与digest（report_digest.py 814 行摘要器：sqlite 内存库→DEFCON 双轨→digest 回写；report.py 174 行 AVID）
09-garak-report前端（React 19+KUI vendor tarball；构建产物回写 Python 仓；__GARAK_INSERT_HERE__ 三通道契约）
10-analyze分析管线（11 个独立 `python -m` 工具；聚合白名单；CI/校准统计层；extracted_digest.json 夹具契约）
11-fixer迁移族与intents（时间戳文件名迁移链 29 子类；Migration 动态发现；Intent 3 行基类+Stub 家族）
12-data资产与反直觉消费链（harmbench→fitd / cloze→leakreplay / xss→web_injection / payloads 断链披露）

## 勘误清单（16 条，[源码核实]/[图谱口径]/[NOTES] 标注）

1. **[口径]** 814 行的是 `garak/analyze/report_digest.py`（digest 管线），`garak/report.py` 仅 174 行（AVID 导出 Report 类）——"report.py 814 行"为两文件混称。
2. **[源码核实]** harmbench 数据反直觉消费链：`data/harmbench/` 唯一消费者是 `probes/fitd.py:249`（当红队种子 prompts，random.sample 抽 5 条），**仓内不存在 harmbench probe**——数据集名 ≠ probe 名。
3. **[源码核实]** `data/payloads/python_code_execution.json` 盘删披露：git 索引在册（8d1259e 内 new file）但工作区 ` D` 已删；`probes/exploitation.py:73` 默认 payload_name + `detectors/exploitation.py:78,119` 三处消费，此状态下跑 exploitation 必抛 PayloadFailure。
4. **[NOTES+核实]** `data/beast/suffixes.txt` 为空占位：真实对抗后缀由 `resources/beast/beast_attack.py` 运行时生成，`probes/suffix.py` 只引用生成器不读该文件。
5. **[源码核实]** 仓根 `requirements.txt` 是聚合视图非安装真源：与 `pyproject.toml` [project].dependencies 双份并行（首项逐条一致），安装走 pyproject，requirements.txt 的 tests/lint/calibration/audio 分组注释对应 optional-dependencies——文档性质。
6. **[源码核实]** 14 个 GitHub workflow 中 `nightly.yml` 唯一 steps=0（纯调度触发器），workflow 提取器对它无 steps 可提。
7. **[源码核实]** xss→web_injection 改名不对等：probe/detector 两侧已改名（`fixer/20250908_xss_rename.py` 四组 rename），`data/xss/` 目录名保留旧名，数据与 API 表面解耦。
8. **[NOTES+核实]** `data/confidence_intervals/confidence_intervals.pkl` 全仓零引用（garak/tests/tools 三域 grep 无 .pkl 路径），判定外部工具产出存档，图谱不挂消费边是正确口径。
9. **[源码核实]** Migration 子类全量是 **29 个非 12 个**：fixer/ 11 个迁移文件中 `20250224_lightweight_probe_defaults.py` 一家 17 个子类（:8-253+），图谱批阶段补建的"基类+12 子类"为部分补建。
10. **[源码核实]** Intent 基类真 3 行（`garak/intents/base.py:9-11`，仅 `stubs()->Set` 契约）：意图体系的实体在 `data/cas/` JSON 数据侧（trait_typology.json + intent_detectors.json + intent_stubs/），代码侧刻意极简——微型基类补建案例。
11. **[图谱口径]** TS barrel 星号再导出链：`garak-report/src/components/index.ts`（49 行）大量 `export { default as X }` / `export type` 再导出无本地实现，tree-sitter 对该模式提取不全，exports 边靠正则补齐。
12. **[图谱口径]** 227 条 inherits 边修复：批阶段对 tree-sitter 漏提取的继承关系全量回补。
13. **[图谱口径]** 自导入伪影 3 处：scan 侧自引用边，甄别剔除不入图谱。
14. **[源码核实]** 前端夹具路径断链：`vite.config.ts:32` example 构建读 `public/reports/extracted_digest.json`，该路径不存在（public/ 仅 index.html），失败走 catch 静默（只 console.error）；夹具真身在 `garak-report/extracted_digest.json`（7425 行，单对象四顶层键）。
15. **[源码核实]** 前端构建产物回写 Python 仓：`vite.config.ts:73` 正式构建 outDir=`../garak/analyze/ui`（实测 1.75MB 单文件 HTML，含 2 处裸 `__GARAK_INSERT_HERE__` 标记供 report_digest.py:715 文本替换）——前端是后端模板资产，非独立应用。
16. **[源码核实]** 两代 AVID 导出器并存：`report.py:64` 找新格式 `entry_type=="start_run setup"`，`analyze/report_avid.py:26` 仍找旧 `"config"`——后者未跟上 entry_type 演进，旧报告专用。

另录：`tests/generators/test_muiltiprocessing_support.py` 文件名误拼为仓内原样（multiprocessing 之误）；`tests/generators/test_generators_base.py` 仅含 SPDX 声明无测试体；HEAD 8d1259e 本身是 github-actions bot 的 plugin_cache.json 自动更新提交（工具链 `tools/rebuild_plugin_cache.sh` 以 mtime 欺骗触发缓存失效）。

## 阅读路径建议

新人按 01→02→03/04/05（插件三柱）→07（执行闭环）→08/09/10（报告与前端）走；做数据/插件扩展的直接跳 11（改名与迁移规范）与 12（资产消费链避坑）。深度背景先读 onboarding/ONBOARDING.md 第 1-2 节（矩阵语义+14 层分层），再按需进 explain。DeepWiki 快照（10-26）不含 intent 世代细节，以源码核实口径为准。
