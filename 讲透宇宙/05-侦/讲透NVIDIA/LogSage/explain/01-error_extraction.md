# 01 · error_extraction.py — 错误抽取与去重管线

> logsage/auto_resume_policy/error_extraction.py · 1030 行 · 行号 @3493d0fc 源码核实

## 角色定位

错误抽取引擎，整条流水线最重的一环：把百万行级的训练作业日志变成一份结构化 `ApplicationData`（错误全文/去重错误/迭代错误/stacktrace/训练与 checkpoint 状态）。核心 `return_application_errors`（:414）从 414 行绵延到 954 行，是全项目最大函数与数据流枢纽。上游只被 log_sage.py 的三条入口调用（如 log_sage.py:185，恰好 3 个实参），下游把产物交给 error_attribution 做归因决策。

## 内部结构

- **rank 工具族**：`extract_ranks`（:70）用正则 `^(?:\[rank)?(\d+])?:` 抽取 rank；`extract_numbers`（:111）把 rank 整除 DOMAIN_SIZE=8 折算成 node 号——这是贯穿全仓的 rank→node 映射约定。
- **三个聚类函数**：`create_clusters`（:237）是唯一接线的（在 :507 被调用）；`create_drain_clusters`（:163，真 Drain3 TemplateMiner，sim_th=0.4/depth=4）与 `create_clusters_without_drain`（:285，多进程）是未接线的替代实现，:594 只剩注释引用——三个方案里最终选了最朴素的自研模板化。
- **stacktrace 重建**：`return_stacktrace`（:339）按错误 pattern 聚合 rank，回看错误位置前 20 行原始日志（:366）拼出 traceback。
- **两个终审 LLM 谓词**：`check_real_error`（:993）问"这些是真实错误吗"，`check_crash`（:957）问"是否真崩溃"，都用 retry_operation 包裹并剥 `<think>`（:988）。

## 外部连接

依赖 utils 的模板化六连、`create_batches_long` 分批、`remove_not_errors`/`get_regex_errors` 正则过滤；依赖 prompts 的六个模板（迭代判定/checkpoint 判定/错误抽取两连/崩溃检查）；依赖 consts 的批参数与哨兵串。LLM 客户端由调用方注入（ChatNVIDIA 或测试的 FakeListLLM），因此整条管线可在无 API key 下被测试驱动。

## 数据流

`return_application_errors` 十二步（详见 ONBOARDING ④）。关键分支：迭代判定/抽取/验证/终审任一处 LLM 端点死掉都返回 `finished="LLM_FAILURE"`（:539、:703、:826）；三级确认中缓存命中的模板不再调 LLM（:658-663），LLM 判定结果按模板回写缓存 yes/no（:774-778）——缓存以模板 pattern 为键，跨行去重的同时跨调用复用。最后按"最后 checkpoint 之后的错误"截断（:879-887），因为 checkpoint 前的旧错已随恢复失效。`WITH_ERRORS` 需同时满足未完成+真错误+真崩溃三条件（:931）。

## 设计决策

1. **宽进严出**：ERROR_RE（:487）故意写 80+ 个子串、连 "in"/"no"/"slow" 都算错误嫌疑，先保召回，再靠 BENIGN_WORDS 表与两轮 LLM 验证压精度——日志噪声无法穷举，漏掉真错误代价更高。
2. **slurmstepd 特判**（:813-822）：CANCELLED AT + DUE TO TIME LIMIT 直接 break（管理员行为非故障）、CANCELLED 但非 NODE FAILURE 跳过；顺带一提 :820-821 通过过滤的 slurmstepd 错误会被 append 两次，疑似小 bug。
3. **迭代起点裁剪**（:471-480）：一旦识别训练已开始，之前所有行丢弃——故障几乎总发生在训练期。
4. **崩溃判定双通道**（:920-924）：LLM 判 crash 或日志含 slurmstepd 取消证据即算，正则兜 LLM 的底。

## 新人提示

读这个 541 行函数别顺序硬啃：先看 :931-954 的出口（WITH_ERRORS/NO_ERRORS），再从 :424 顺着数据变形读；把 test_error_extraction_comprehensive.py 的 FakeListLLM 用例当每一步的输入输出规格书。注意 main.py:87 对本函数的 8 元组解包是陈旧签名，以 :414 的 3 参签名为准。
