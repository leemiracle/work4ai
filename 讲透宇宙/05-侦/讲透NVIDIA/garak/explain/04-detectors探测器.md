# 04 detectors 探测器：评分基类与 matching/scoring 复用工具

## 角色定位

`garak/detectors/`（31 个模块）是评分层：Detector 吃一个 Attempt，吐与 outputs 等长的分数列表（0.0=未命中，1.0=命中，None=无法评判）。与 probe 的多基类分场景不同，detector 体系刻意**单根扁平**：一个 `Detector` 基类 + 三个开箱半成品（String/TriggerList/File）+ 模型派 HFDetector，全目录 60+ 探测器（图谱 L03）几乎全落在这四条线上。公共算法不在 detectors/ 而在 `garak/resources/matching.py` 与 `scoring.py` 两个小工具——模糊匹配与聚合计分，detectors 与 analyze 管线双消费。

## 内部结构

**Detector 基类**（`detectors/base.py:21`，继承 Configurable）：`lang_spec`（:25）、`active=True`（:28，与 probe 相反默认可用）、`hit_desc/pass_desc`（:33-34）、`modality {"out":{"text"}}`（:40）、`DEFAULT_PARAMS {"skip": False}`（:42-44）。契约唯一方法 `detect(attempt) -> Iterable[float|None]`（:74-79）。

**四个模板类**：`HFDetector(Detector, HFCompatible)`（:82）构造器（:91-154）拉 `AutoModelForSequenceClassification + TextClassificationPipeline`，显式 `mp.set_start_method("spawn", force=True)` 防 fork 死锁（:107-109）；`detect()`（:156-194）精华是**分数归一化**：HF 的 label+score 映射 `(1.0 ± score)/2`（:185-189）——命中目标类落 (0.5,1]，非命中落 [0,0.5)；`graceful_fail` 把推理异常吞成全 None（:171-178）。`StringDetector`（:197）：`matchtype ∈ {str, word, startswith}`（:200-204）；`detect`（:220-272）先归一触发子串（:228-234，非法 normalize 值降级全 None），`word` 型用 `\b` 边界正则（:261）。`TriggerListDetector`（:275）读 `attempt.notes["triggers"]`（:284-287），无键返回全 None。`FileDetector`（:307）以 `valid_format` 哨兵校验 notes["format"]（:314/:320-330）。

**always.py 哨兵族**（`detectors/always.py`）：`Fail/Pass`（:15/:23）恒 1.0/0.0；`Passthru`（:31）转发 attempt 已有分数（:42-46），`DEFAULT_PARAMS {"skip": True}`（:39-41）——专供 TreeSearchProbe 已打分 attempts 免二次计算；`Random`（:47）管线自检。

**两个复用工具**：`resources/matching.py:5` `ngram_contained_match(target, context, n=4)`——字符 n-gram **不对称包含度**（:8-13 docstring 明示 asymmetry）：target 的 n-gram 有多少出现在 context 任意位置，target 短于 n 返 0.0（:17-18）。消费者 `detectors/encoding.py:11/:59`（编码类「近似解码」）与 `detectors/sysprompt_extraction.py:12/:95`（系统提示泄露模糊召回），均取 best_match 最大化（`detectors/encoding.py:63-66`）。`resources/scoring.py:10` `aggregate(scores, aggregation_function="lower_quartile")`：六种聚合（:20-39），未知函数名回退 minimum 并置标志（:40-42）；`proportion_passing` 引 `ABSOLUTE_DEFCON_BOUNDS.BELOW_AVG`（:7/:37-39）。消费者在 `analyze/report_digest.py:269`（报告聚合），不在运行时路径。

## 外部连接

- **上游 harness**：`harnesses/probewise.py:16-19` `_load_detector` 按探针推荐加载，选择公式三分支（primary+extended / 仅 primary / recommended 兜底 deprecated，:98-117）；harness 逐 attempt 调 detect 并写 `attempt.detector_results[detector_name]`。
- **契约对齐**：返回长度必须等于 `len(attempt.outputs)`；None=不评判，evaluator 聚合剔除；`outputs_for(lang_spec)`（`detectors/base.py:160/222/282`）保证跨语言拿回译文。
- **HFCompatible 混入**（`resources/api/huggingface.py:11`）：HFDetector、generators/huggingface、buffs/paraphrase 三处共享 `_gather_hf_params/_select_hf_device` 等五方法（:20-129），`trust_remote_code` 默认锁 False（:82-86）。
- **组合关系**：`detectors/any.py` 多探测器取或；`judge.py` LLM 评 LLM（其 EvaluationJudge 是 `attempt.py:110` legacy 分支出处）；harness `strict_modality_match`（`harnesses/base.py:66`）按 out-modality 过滤。

## 数据流

```
harness: for attempt in probe_results:
    score_list = detector.detect(attempt)   # 读 outputs_for(lang_spec) / notes
    attempt.detector_results[fullname] = score_list
  → evaluator.evaluate（ThresholdEvaluator 按 eval_threshold 二值化，cli.py:125-129）
  → report.jsonl 随 as_dict 落盘（attempt.py:290）
  → analyze/report_digest: scoring.aggregate（report_digest.py:269）
```

两条消费链时序分离：detect 在运行时（在线），aggregate 在报告期（离线 digest）。

## 设计决策

1. **连续分数而非布尔**：`(1±s)/2` 映射（:185-189）把阈值判定权交给 evaluator 的 `eval_threshold`——同一 detector 服务不同严格度的报告。
2. **None 是一等公民**：无法评判（空输出/格式不符/推理异常）一律 None 而非 0.0，不把「不知道」误记成「安全」——安全工具的诚实性设计。
3. **小工具下沉 resources/**：n-gram 匹配仅 28 行（`matching.py:5-27`）服务两个 detector 模块；与 `resources/common.py` 的 `REJECTION_STRINGS/load_advbench`（BEAST 复用，`resources/beast/beast_attack.py:13`）同属「算法与数据分离」。
4. **异常降级不扩散**：非法 normalize（:232-234）、推理异常（:171-178）、格式不符（:324-329）全降级 None+warning——单个 detector 配置错不拖垮扫描。
5. **skip 参数**（:43）：配置文件可按名禁用个别 detector，不必改 spec。

## 新人提示

- 新 detector 首选继承 `StringDetector`（传 substrings 即成品）；评分非匹配型才落裸 `Detector`。
- 返回长度对齐是硬约束：`len(result)==len(attempt.outputs)`，否则 evaluator 索引错位且无报错——用 `[None]*len(all_outputs)` 填充。
- 模糊匹配直接用 `ngram_contained_match`，n=4 是仓默认，调 n 即调召回/精度。
- HFDetector 调优先看 `hf_args.device`（默认 cpu，:86）与 `detector_target_class`（:187）——label 名对不上分数会映反。
- 报告组分数偏低先查聚合口径：digest 默认 lower_quartile（`scoring.py:26-30`），单条命中被悲观聚合稀释，改 `proportion_passing` 更直观。
