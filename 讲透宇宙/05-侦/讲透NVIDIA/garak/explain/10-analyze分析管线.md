# 10 · analyze 分析管线：11 个独立工具与 digest 数据契约

## 一、角色定位

`garak/analyze/` 是运行后的分析工具集：17 个文件 4212 行，**没有统一的 `garak analyze` 子命令**——cli.py 里不存在 analyze 分支，全部入口是 `python -m garak.analyze.<module>`（11 个文件带 `__main__`：report_digest / aggregate_reports / report_avid / analyze_log / misp / qual_review / perf_stats / count_tokens / get_tree / tbsa / rebuild_cis）。管线主干只跑一个：run 收尾时 command.py:150 自动调 write_report_digest；其余是人工触发的旁路工具。共享底座 analyze/__init__.py 定义 DEFCON 语义：绝对界标 ABSOLUTE_DEFCON_BOUNDS（:7-11，0.05/0.4/0.8/0.99）与相对 Z 分界标（:14-18），`score_to_defcon`（:48-58）做 1-5 分级（1 最差），MINIMUM_STD_DEV=1/30（:45）做拉普拉斯平滑防 σ→0 出不可用 Z 分——注释交代了"容忍 30+ 次 probe 里 1 次误判"的取值依据。

## 二、内部结构

按职能四层：① 摘要层 report_digest.py 814 行（08 篇详解）；② **聚合层 aggregate_reports.py**（190 行）把同模型多份报告合成一份——`_process_file_body`（:21）逐行白名单过滤（attempt/eval/probe_summary/plugin_cache 四类，:31-37），遇 digest 行即停（:29-31，旧摘要不搬运由尾部重建），未完成 attempt（status!=2）跳过（:38-41）；头两行 setup/init 从 lead 文件提取，后续文件断言 target_type/target_name/garak 版本三一致（:169-171）否则拒绝聚合；旧字段 model_type/model_name 顺手迁移（:115/:164），三个 legacy selection 键丢弃（:126-131），聚合 probespec 写进 transient.active_probes（:132）；尾部 build_digest+append 重建摘要（:181）。③ **统计层**：calibration.py（119 行）的 Calibration 类管理跨模型校准数据、get_z_score 供相对评分，:39-45 有个 Windows git 把 symlink 检出成文本文件的 workaround（正则识别目标名重定向路径）；detector_metrics.py 的 DetectorMetrics 单例（:15-16 模块级缓存）加载 `data/detectors_eval/detector_metrics_summary.json` 取每 detector 的 Se/Sp，缺省 (1.0,1.0)（:20-50）——TODO 注明 detector 性能其实依赖 probe，对级指标是未来工作；bootstrap_ci.py（105 行）与 ci_calculator.py（276 行）、rebuild_cis.py（241 行，为存量报告补算 CI）构成置信区间工具族。④ 外围单件工具：count_tokens / get_tree / misp / perf_stats / qual_review / tbsa / analyze_log / report_avid。

## 三、外部连接

上游三个消费源：evaluator（evaluators/base.py:43, 48 在 show_z / bootstrap 模式下即时装载 Calibration 与 DetectorMetrics——分析模块反向成为运行时依赖）；harnesses（attempt 状态经 probe_summary 进入管线）；cli.py:298 的 AVID 选项触达 report_avid.py。下游一个：garak-report 前端吃 digest 结构。**联调夹具 garak-report/extracted_digest.json（7425 行）是管线的地面真值**：单 JSON 对象，顶层 entry_type/meta/eval/technique_intent_matrix 四键，与 append_report_object 追加进 report.jsonl 的 digest 记录、build_html 注入模板的数组元素同构——一份结构三处复用（报告存档/HTML 注入/前端开发）。meta.calibration_used、meta.aggregation_unknown 等旗标（report_digest.py:678-679）让前端能区分"没算"与"算不了"。

## 四、数据流

标准流：report.jsonl（六类记录）→ build_digest 六路分拣 → sqlite 内存库 → 组/probe/detector 三级嵌套 digest → 追加回报告 + 注入 HTML 模板 → 前端渲染。聚合流：多份 report.jsonl → 白名单行过滤 + 头部一致性断言 → 聚合报告 → 重建 digest。CI 补算流：存量报告 → rebuild_cis 读 eval 记录 → bootstrap 重采样（evaluator 同款 [1]*fails+[0]*passes 构造）→ 回写 confidence 三字段。校准流：data/calibration/ 下的跨模型分数统计 → Calibration Z 分 → digest 的 relative_score/relative_defcon → show_z 模式的终端彩色符号（SYMBOL_SET emoji）。

## 五、设计决策

1. **无统一命令、纯模块工具集**：11 个 `__main__` 各带自己的 argparse（如 report_digest.py:732-758），利于独立演进但发现性差——本篇存在的原因之一。
2. **聚合不搬 digest**（aggregate_reports.py:28-29）：摘要永远由当前安装重建，避免旧版本 digest 结构滞留——与 ReportIncompatibleError 拦截（report_digest.py:210-214）同一哲学：报告兼容性以插件元数据为准。
3. **Se/Sp 缺省完美值**（detector_metrics.py:20-50）：无评测数据时 CI 退化为朴素 bootstrap，管线不因数据缺失而断。
4. **DEFCON 双轨制**：绝对分（对全体）与相对 Z 分（对同侪模型）并行，tier==1 probe 取较优（report_digest.py:436-441）——承认"评测难度不均"的统计现实。
5. **文件级断言防错配聚合**（:171-173）：版本不一致直接 assert 崩，不做跨版本聚合的幻想。
6. **头部兼容迁移内嵌**（:129-135）：老报告的 model_type 在聚合时顺手升格 target_type，与分析解耦但顺路完成。

## 六、新人提示

想跑通最小分析回路：`python -m garak.analyze.report_digest -r <report.jsonl> -o out.html` 即可，不必重跑扫描。四个注意：① 聚合前确认各报告同版本（三断言），混合版本会半途崩且输出文件已建；② show_z / bootstrap 是运行期旗标（`--show_z` / reporting.confidence_interval_method），报告里没有的字段事后只有 rebuild_cis 能补；③ extracted_digest.json 夹具放 garak-report 仓根而非 vite 期待的 public/reports/（09 篇勘误），复制即位即可 build:example；④ 改 digest 字段名是破坏性变更——前端 types/（ReportEntry.ts 等）、build_html 模板、aggregate 白名单三处都要同步，漏一处前端白屏且 ErrorBoundary 只给笼统文案。
