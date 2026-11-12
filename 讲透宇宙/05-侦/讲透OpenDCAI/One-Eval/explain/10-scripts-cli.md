# 10 · scripts 星型拓扑：one-eval-skill 的 CLI 集群

## 角色定位

`one-eval-skill/scripts/`（10 文件 3760 行）是 Web 后端之外的第二条驱动路径：命令行门户。围绕共享层 `_common.py`（415 行）组成**星型拓扑**——九个 CLI 卫星全部 import `_common`，彼此零横向依赖、可任意组合。设计哲学写在模块 docstring L10："**直接 import one_eval，不拷贝评测内核**"——skill 层是薄编排，确定性内核只有一份。

## 内部结构

**_common.py 四职责**：

1. **路径与导入引导**（L19-35）：`REPO_ROOT` 上溯两级（L20-21）+ `sys.path.insert(0, REPO_ROOT)`（L23-24）——不装包也能跑，脚本不依赖 pip install。路径常量：eval_outputs/、cache/、.local_state.json、custom_metrics/（L30-33）。
2. **evalspec 规范化**（L96-166）：兼容五种历史写法（顶层 benchmark/benchmark_name、字符串数组、dict 数组）全归一为 `benchmarks:[{bench_name:...}]`；别名冲突显式报错（L109-113）不做静默选择。
3. **构造桥**（L255-330）：`build_model_config`/`build_bench_info` 把 YAML 变内核 ModelConfig/BenchInfo，白名单过滤（L262-267）、key_mapping 必填校验（L309-314）。**六范式硬契约**在此复刻：VALID_EVAL_TYPES（L236-243）与 REQUIRED_KEYS（L246-253），和前端（07 篇）、内核三方手工镜像。
4. **本地状态与 metric 扩展**（L333-415）：`.local_state.json` 记 READY 三元组 dataset_path/eval_type/key_mapping（L349-358）；`ensure_metrics_loaded` 把 custom_metrics/*.py 加 sys.path 逐个 import 触发 @register_metric（L397-412）——内核只扫 one_eval.metrics.common，自定义指标靠这里补装载。

bench 双轨常量（L69-75）：`dataflow`（走内核）与 `external_repo`（外部仓自执行，`enrich_external_bench` L204-225 从 gallery 按名回填 meta.repo_eval，spec 显式字段优先）。

**九个 CLI 卫星**：

| 脚本 | 行数 | 入口锚 | 职责 |
|---|---|---|---|
| run_eval.py | 535 | L436-440 | 核心执行器（spec+--smoke+--output-dir） |
| check_model.py | 193 | L148-156 | 连通性（API 轻探 L39/vLLM 探 L112） |
| prepare_bench.py | 203 | L147-153 | HF 下载+嵌套 key 预览（_flatten_keys L41） |
| run_metrics.py | 375 | L258 | 指标计算+每范式默认 evaluation（L90） |
| make_plots.py | 223 | L185-189 | 三图：分数条 L69/样本有效率 L106/热力 L134 |
| render_leaderboard.py | 176 | L149-154 | vs 公开分数表排名 markdown |
| render_report.py | 1303 | L1247 | **自包含 HTML 报告** |
| doctor.py | 181 | L142 | 环境体检（模块/隔离/skill 注册 L52-142） |
| build_gallery_md.py | 138 | L117-120 | bench_gallery.json→markdown |

run_eval 三细节：断点续跑 `_load_done_benches`（L60）按已完成 bench 增量跳过；`--smoke` 用 `_truncate_jsonl`（L88）截每 bench 3 条；external 分线 `_run_external_repo`（L151）短路出内核外。

**render_report.py 零依赖单文件**：约 700 行是 CSS/JS/SAMPLE_JS 三段字符串常量，L1240-1244 拼成单 HTML，样本数据经 `_json_for_script`（L44）转义内嵌（L1178）。file:// 打开即用：hash 路由 `#bench/<name>`、逐样本浏览器（搜索/仅看错误/隐藏空值/分页/导出过滤 jsonl）；明细缺失/移动/解析错误/截断全有 notice 提示。

## 外部连接

- 唯一重依赖是内核：`_common.py` L257/L277/L393 懒 import ModelConfig/BenchInfo/load_metric_implementations——耦合面就这三个符号加 DataFlowEvalTool 调用。
- bench_gallery.json（L27 指向 one_eval/utils/bench_table/）：external 回填与 leaderboard 分数的数据源（04 篇）。
- 上游：huggingface_hub、yaml（L368-371）、matplotlib。
- 被 SKILL.md 规程引用（11 篇）：每个 CLI 的调用时机写在规程里。

## 数据流

```
evalspec.yaml（bench_name + model 段）
  → check_model.py --spec：先探连通（省得跑一半崩）
  → prepare_bench.py：下载数据到 cache/、展平嵌套 key 供填 key_mapping
  → run_eval.py [--smoke]：_common 规范化→构造桥→
      dataflow 分线：DataFlowEvalTool.run_eval 内核
      external 分线：_run_external_repo 外部执行回填（05 篇）
      → eval_outputs/runs/<run_id>/（run_id 时间戳 L38-44，latest_run.txt 指针 L52）
  → run_metrics.py → metric_results.json
  → make_plots / render_leaderboard / render_report 三路可视化
  → mark_bench_ready 写 .local_state.json，下次同 bench 复用验证过的配置
```

每步产物是纯 JSON/JSONL，任何一步可单独重跑（改报告样式只重跑 render_report 不重评测）。

## 设计决策（含批判）

1. sys.path 注入而非 pip 依赖是 skill 分发务实选择——克隆即用；代价是单脚本脱离 `_common.py` 即断，与 pip 装版并存时可能加载旧内核。
2. **六范式三方手工镜像是全仓最大 schema 漂移面**，且已实锤不一致：`REQUIRED_KEYS` 的 key3_q_a_rejected 只列两项（L252），前端同名表（EvalComponents.tsx L258）要求三项含 input_question_key——两份"必填"打架，改动极易漏同步。
3. READY 状态本地化思路好但无版本号字段——内核升级改范式语义后旧记录可能带病复用。
4. render_report 把 JS/CSS 写成 Python 常量：单文件交付合理，但 700 行 JS 无 lint 无测试，浏览器侧 bug 只能肉眼发现。
5. 九脚本重复实现 `_load`/`_metric_result_index`/`_primary_score_from_metric_row`（render_leaderboard L33-53、make_plots L47-67、render_report L49-99 三份近似拷贝）——共享层没覆盖"读结果文件"这一最高频操作。
6. `sanitize_model_config` 落盘把 api_key 脱敏为 "***"（L65-66），结果文件可分享不泄密——安全亮点。

## 新人提示

- 第一次跑先 `doctor.py`：把"环境不对"从两小时后的崩溃提前到三十秒。
- evalspec 五种兼容形态看 `normalize_evalspec` docstring（L128-141）；新代码一律写标准 `bench_name`。
- 断点续跑是默认行为：中断后**重跑同一条命令**即跳过已完成 bench（L60），别删 eval_outputs。
- 找结果：`eval_outputs/latest_run.txt`（L52）指向最新 run 目录，产物全在 run 目录内闭环。
- 改报告模板先 `--out` 存一份基线 HTML 作对照——CSS/JS 常量改坏一处整页白屏。
