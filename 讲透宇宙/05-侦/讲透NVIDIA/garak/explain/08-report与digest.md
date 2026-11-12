# 08 · report 与 digest：814 行摘要器与落盘链

## 一、角色定位

两个文件承担 garak 的"事后叙事"：`garak/report.py`（174 行）是旧的 Report 类——读 report.jsonl 出 AVID 格式报告；`garak/analyze/report_digest.py`（814 行，全仓最大单文件之一）才是现代摘要管线核心——把 JSONL 原始记录重组成 digest 结构并注入 HTML 模板。任务口径勘误：**814 行的是 report_digest.py，report.py 仅 174 行**；两者非同一文件的 两半，而是新旧两代导出器并存（analyze/report_avid.py:26 还在找旧版 `entry_type=="config"` 记录，report.py:64 已改用 `"start_run setup"`）。

## 二、内部结构

report_digest.py 的模块级副作用很重：导入即 `load_config`（:31-32）、读 tags.misp.tsv 建 tag 描述表（:34-40）、读 cas/trait_typology.json 建 intent 人名表（:43-48）。核心函数链：`_parse_report`（:58-101）把 JSONL 分拣为 init/setup/payloads/evals/plugin_cache/probe_summaries 六路，plugin_cache 缺失时 deepcopy 当前安装的 PluginCache 兜底（:96-100）；`_init_populate_result_db`（:165-240）**建 sqlite3 内存库** results 表（:172-183），taxonomy 模式按 probe 标签分组、无标签归 "other"（:215-221）；`_get_group_aggregate_score`（:257-276）调 resources.scoring.aggregate；`_get_group_info`（:279-309）在无 taxonomy 时 importlib 加载 probes 模块取 docstring 当组描述（:287-291）。`_get_probe_detector_details`（:378-476）是评分语义深水区：z-score 校准（:406-412）、clean sheet（absolute=1.0）时把相对/绝对 DEFCON 双锁为 5（:429-430）、tier==1 的 probe 取绝对与相对的较优值（:436-441）、**CI 反转**——CI 按 ASR（失败率）算而 absolute_score 是通过率，故 pass rate CI = [1-ci_upper, 1-ci_lower]（:459-464 注释明示）。`_compute_technique_intent_matrix`（:507-578）把各 eval 的 intents 按 probe 的 `demon:` 标签池化成技术×意图矩阵。`build_digest`（:581-689）串起全链并写 meta（taxonomy/calibration_used/plugin_cache_source 等，:677-682）。`build_html`（:692-716）读 `garak/analyze/ui/index.html` 模板，把 digest JSON 数组替换进 `__GARAK_INSERT_HERE__` 标记，模板缺失时降级纯 JSON dump（:695-699）。`__main__` CLI（:727-810）支持 `-r/-o/-w/-t`，`-t None` 显式回归 probe 家族分组（:766-769），未指定 taxonomy 时从原报告 setup 继承（:771-779），已有 digest 默认复用、仅当显式给 taxonomy 才重建（:784-786）。

## 三、外部连接

落盘链上游是 `garak/command.py:124` 的 `end_run()`：run 完成时把 report 文件名 `.jsonl→.html` 得 digest_filename（command.py:147），调 `write_report_digest`（command.py:411-419）——build_digest 后先 `append_report_object`（report_digest.py:498-504，seek 到末尾检查末字符是否换行、缺则补）把 digest 追加回 report.jsonl 本体，再写 HTML。异常被 end_run 整体捕获，JSONL 保留（command.py:148-154）。旁支：`analyze/aggregate_reports.py:62` 复用 `_extract_to_probespec`，:181 调 build_digest 重建聚合报告的 digest；`_config.py:117` 专门预留 `reporting.taxonomy=None` 让本模块可被直接调用。report.py 的 Report 类则由 `cli.py:298` 的 AVID 选项触达，依赖 pandas/numpy/avidtools 三方件，export 时给每个 probe 生成一份 AVID 报告、avid 标签统一挂 L05（report.py:163）。

## 四、数据流

digest 输入是运行期累积的六类 entry_type 记录，输出三份产物：① 追加进 report.jsonl 的 digest 行（供 aggregate 与前端直接取用）；② `.html` 摘要（digest JSON 内嵌单文件）；③ 前端再消费同结构。分数流：eval 记录的 passed/total → sqlite results 表 score 列（passed/instances，:193）→ 组聚合 → DEFCON 分级（analyze/__init__.py:48 的 score_to_defcon，绝对/相对两套界标 :7-18）。意图流：eval.intents → demon 标签池化 → matrix 单元 score=passed/total（:560）。

## 五、设计决策

1. **sqlite 内存库当中间层**（:167）：分组/聚合/排序全下推 SQL（如 :314 的 min(score) 按组取最差探测器），免手写聚合。
2. **CI 语义反转内联处理**（:459-464）：不在源头（evaluator）统一口径，而在展示层翻转——两套口径并存的债。
3. **digest 回写报告本体**（append_report_object）：报告自包含，前端/聚合器不必重算，代价是同一文件兼作原始记录与派生摘要。
4. **plugin_cache 双保险**（:96-100）：报告缺插件快照时用当前安装补齐——跨版本报告靠 `_resolve_plugin_info` 抛 ReportIncompatibleError 拦截（:210-214, 333-337），错误文案直指"换 garak 版本"。
5. **模板缺标记降级 JSON**（:704-711）：HTML 坏了至少数据还在。
6. **报告类（report.py）导入 probe 类实例化取 tags**（report.py:72-76）：离线工具带运行时副作用，report_avid.py:29-31 同款写法。

## 六、新人提示

改 digest 结构时先跑 `python -m garak.analyze.report_digest -r <report>`（:734 的 prog 名）比对输出，别等端到端。三个坑：① 模块导入即读数据文件+加载配置，测试环境下 MISP 文件缺失时 tag_descriptions 为空表而非报错（:36 守卫）；② taxonomy 参数三态（未指定=继承报告 / "None" 字符串=清空 / 值=强制重建，:766-786），CLI 行为差异全在这；③ append_report_object 依赖文件末尾换行判断（:499-503），手改过报告文件后 -w 追加可能拼出坏行。Report 类与 report_digest 是两代——给 AVID 数据库交报告走 report.py，给人看的 HTML 走 digest，别混用。
