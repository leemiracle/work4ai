# 03 · 指标系统：去中心化注册 + LLM First 调度

## 角色定位

指标系统回答「该用哪些指标打分」。它有两个正交扩展点：**注册侧**`@register_metric` 让实现模块自登记（core/metric_registry.py:54）；**推荐侧**`MetricDispatcher` 查表给规则建议（metrics/dispatcher.py:15），最终由 `MetricRecommendAgent` 按 LLM First 优先级裁决，执行落在 `MetricRunner`。

## 内部结构

**注册机制**：装饰器把函数连同 `desc/usage/categories/aliases/dimension` 装进全局 `_REGISTRY_CACHE`，别名进 `_ALIAS_MAP`（metric_registry.py:48-52, 94-98）；`name` 省略时自动剥 `compute_` 前缀（74-81）。`load_metric_implementations`（103）用 `pkgutil.walk_packages` 扫 `one_eval.metrics.common` 全模块触发注册；`ModuleNotFoundError` 降级为 info 日志跳过——注释明言可选依赖（langchain_openai、rouge_score）缺失不该吓到确定性评测用户（120-127）。`get_metric_fn` 惰性加载+别名解析（131-144）。

**查表调度**：`MetricDispatcher` 模块级单例 `metric_dispatcher`（dispatcher.py:100）；`DATASET_METRICS`（config.py:28）是 12 套可复用指标组×约 40 个数据集的静态映射；匹配用 `_normalize_key` 归一化后**子串包含、最长键优先**（39-42, 87-92）；命中后 `_inflate_metrics` 膨胀优先级——第一个 primary、四个诊断指标 diagnostic、其余 secondary（44-68）。

**LLM First 四级优先级**（metric_recommend_agent.py:212 的 run）：①**User Override**——bench.meta.metrics 直接生效不再问 LLM（235-244）；②**LLM 主路径**——所有 bench 一律交 LLM 分析，registry 建议只作上下文（251-253），指标库文档由注册表动态生成（267-268），并强制追加 `metric_summary_analyst`/`case_study_analyst` 两个诊断指标（317-325）；③**Registry 兜底**——LLM 漏答时回退查表建议（337-343）；④**exact_match 兜底**——表也没有就用 `exact_match`+`extraction_rate`（344-349）。HOW_TO_REGISTER_METRIC.md 是与此一致的官方契约。

**六实现模块**（metrics/common/，共 22 个注册指标）：general.py 12 个（exact_match/numerical_match/choice_accuracy/multilabel_f1/set_f1/extraction_rate 等）、text_gen.py 5 个（bleu/rouge_l/chrf/token_f1/jaccard_similarity）、analysis.py 2 个、code/math_verify/sql 各 1 个。`MetricRunner`（runner.py:18）对样本>100 的可并行指标按 CPU 数分块进 `ProcessPoolExecutor`（16, 31-47, 108-120），语料级指标走串行；`run_bench_with_contract`（139）面向 primary 指标带 parser/failure_policy 契约；pred/ref 字段名靠候选键表猜测（404-422）。

## 外部连接

上游：MetricRecommendNode/ScoreCalcNode 与 server 的 `/api/metrics/registry`（app.py:1909 直接返回 `get_registered_metrics_meta()`）。下游：`MetricPromptGenerator` 把注册表渲染成 LLM 菜单；one-eval-skill 的 custom_metrics/ 目录（现仅 .gitkeep，SKILL.md:143 约定用户新指标落这里）是用户侧扩展位。

## 数据流

bench 进 → 四级裁决出 `state.metric_plan[bench_name] = [{name, priority, args}]` → 回写 bench.meta 供前端（365-370）→ ScoreCalc 阶段 MetricRunner 按 plan 取 `get_metric_fn(name)` 逐个执行，已算结果经 `all_metric_results` 注入后续指标（runner.py:117-124）→ 结果带 score/details/priority 落 `eval_results`。

## 设计决策（含批判）

1. **去中心化注册优于中心清单**：新指标零配置被发现，可选依赖静默降级保住确定性主链；代价是 `_REGISTRY_CACHE` 为空才触发扫描（134-136），理论上存在半初始化窗口。
2. **LLM First 而非规则 First**：registry 只是参考不阻断 LLM（251-252），换灵活性；LLM 幻觉指标名被 `_validate_metrics` 滤掉，但「合法不合语境」的错选要靠 MetricReviewNode 人审把关。
3. **主动剔除 AUC/相关系数类**：注释直言推理产物只有文本拿不到概率/logits，那类指标恒返 0（metric_registry.py:29-37）——诚实的契约边界。
4. **pairwise 弱代理自曝**：config.py:18-21 承认 `_SUITE_WIN_RATE` 只是「与更优答案的词面接近度」诊断用，别当主分。

## 新人提示

加指标三步：在 metrics/common/ 建文件，写 `compute_xxx(preds, refs, **kwargs) -> {"score": float}` 加装饰器，可选往 DATASET_METRICS 加映射。返回字典必须有 `score`；desc/usage 直接进 LLM 指标库，写清楚等于帮 LLM 推荐。排查「指标没找到」先看日志有无「跳过可选 Metric 模块」——那是缺依赖不是 bug。
