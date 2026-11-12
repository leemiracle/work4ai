# 01 · 核心搜索引擎：Search 门面与 ask/evaluate/tell

## 角色定位
`compileiq/ciq.py`（1695 行）是 CompileIQ 的主入口与最大模块：`Search` 类（`ciq.py:341`）拥有 ask/evaluate/tell 生命周期、结果与 checkpoint 全部状态，是前端世界唯一"有状态"的骨架。引擎、worker、tracker 都是它组合进来的可替换件。

## 内部结构
46 个方法围绕四条主线：输入规范化（`normalize_search_config` `ciq.py:463`、`normalize_engine` `ciq.py:472`）；候选流（`sample` `ciq.py:723` 独立采样、`ask` `ciq.py:756`、`evaluate` `ciq.py:907`）；分数回流（`tell` `ciq.py:930`）；断点续搜（5 个 checkpoint 相关类：警告类 `ciq.py:152` + `CheckpointSearchConfig` `ciq.py:173` / `CheckpointResultRow` `ciq.py:236` / `CheckpointResultLedger` `ciq.py:270` / `CheckpointEnvelope` `ciq.py:281`，配 `save_checkpoint` `ciq.py:1170` 与 `from_checkpoint` `ciq.py:1389`）。主循环由 `start`（`ciq.py:1470`）托管。

## 外部连接
向下经 `backends.py` 的 `create_backend`（`backends.py:391`）进程内实例化引擎；向执行面把候选交给 `worker.py` 的五种 worker；配置类型全部来自 `types.py` 的 `SearchConfiguration`（`types.py:489`，`extra="forbid"` 拒绝未知字段），legacy 字段经 `to_legacy`/`from_legacy` 双向转换（`types.py:633`/`674`，带弃用警告）；结果落 `results.py` 的 `SearchResult`（`results.py:14`），提供 `get_best_result`（`results.py:253`）与 `pareto_front`（`results.py:303`）。

## 数据流
ask → 后端给候选（带稳定 `param_id`）→ evaluate → worker 并行跑目标函数 → tell → 三重校验 → 引擎接受 → 结果行追加。校验顺序固定：候选 ID 有效性（重复/未知/已上报即拒，`ciq.py:944-950`）→ 目标数匹配（`ciq.py:951-958`）→ 归一化分数合法（`ciq.py:966-980`）。

## 设计决策
最核心的契约是**拒绝零残留**：任何校验失败只 `raise ValueError`，全部状态写入（`_has_activity`、`_backend_impl.tell`、结果行）排在最后（`ciq.py:1029-1035`），被拒的 tell 不留半个副作用。第一代全失败保护（`_check_fail_count` `ciq.py:1691`，判据在 `ciq.py:996-1003`）把"目标函数整个写错"提前到第 0 代就报 RuntimeError。目标函数侧契约则由示例层的 `RuntimeObjective`（`examples/compilers/xla_ciq_example/src/xla_ciq/search/compileiq_runtime.py:54`）示范：docstring 明言"multiprocess workers cannot pickle nested defs"——模块级类实例才可 pickle 供子进程、可哈希供去重。

## 新人提示
先读 `examples/single_objective.py`（37 行）对照本篇数据流；写手动循环时牢记 tell 的列表顺序无关、但每项 `param_id` 必须来自未结清的 ask。搜索空间原语的 `range` 遮蔽内建名（`compileiq/search_spaces/base.py:12`），import 写法是 `from compileiq.search_spaces import range`——linter 报 shadowing 属预期，是刻意 API。
