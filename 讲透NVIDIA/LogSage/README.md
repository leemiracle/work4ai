# 讲透 LogSage

> NVIDIA 的 LLM 驱动训练作业日志分析工具：从 SLURM 作业日志抽取/去重错误、LLM 根因归因、推荐自动恢复策略，减少 GPU 空转浪费。核心包 logsage/auto_resume_policy/。

## 全链状态表（2026-11-08）

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析 | ✅ 7 批（8 文件，批 3 拆 2 part） | 169 节点 / 352 边（imports 31=scanner 30+AST 手补 1） |
| merge | ✅ 零丢失 | 无悬空边 |
| layers/tour | ✅ | 8 层 / 12 步 |
| finalize | ✅ validator 0/0 | knowledge-graph.json（169n/352e） |
| fingerprints | ✅ | 40 files @ 3493d0fc |
| onboarding | ✅ | ONBOARDING.md 4980 字 / 27 唯一锚 |
| explain | ✅ 3 篇 | error_extraction（1983 字）/ log_sage（2208 字）/ utils（2356 字），锚 30/44/48 |
| 锚终验 | ✅ 真坏 0 | 本轮产物 onboarding 33/33 + explain 完整式 7/7 全好；裸行号锚（篇首声明主文件风格）抽验 5/5 行内容命中；deepwiki/ 老快照的 OOB 非本轮产物不计 |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/LogSage/.understand-anything/knowledge-graph.json`。deepwiki/ 为 2026-10-26 L0 轮产物（深讲九篇在 讲透NVIDIA/深讲/）。

## 源码甄别（写作期逐行实证）

1. **main.py 是陈旧死入口**：`return_application_errors` 实际签名仅 3 参 `(llm, tm_text, cache_dict) -> ApplicationData`（error_extraction.py:414 实证），main 却解包 8 元组、`get_proposed_solution_cat` 传 6 参——运行必 TypeError；现行有效 CLI 是 `log_sage.py:main`。
2. **README「Running the API」引用的 server.py/run_server/fetcher 全不存在**——内网完整版文档，开源版裁掉了 FastAPI 层；tests/README 同样引用不存在的 test_server.py/attribution_tests.py（同内网版口径）。
3. LICENSE.txt=Apache-2.0 而 pyproject classifier=MIT 矛盾；CONTRIBUTING 称 3.9+ 与 requires-python>=3.11 矛盾。
4. categorize_errors L515-517 LLM 失败分支 `list(...)` 无 return 疑似真 bug。
5. **三个聚类函数只有 create_clusters（:237，:507 接线）生效**——create_drain_clusters（:163，真 Drain3 TemplateMiner）与 create_clusters_without_drain（:285，多进程）是未接线的替代实现，:594 只剩注释引用。
6. tests/test_error_extraction.py 名不符实，实际测 utils 数字 token 化（tested_by 按真实依赖指向 utils）。
7. 死代码：`split_by_cycle`（log_sage.py:101）、`compress_application_log_not_ordered_cut`（utils.py:926）零调用。
8. prompts.py 实为 24 个模板——第 24 个 `suggest_yes_checkpoint_stop_extension`（:493）仅存于注释；utils.py:194 docstring 长词阈值 10 vs 代码 14；error_extraction.py:820-821 slurmstepd 错误双重 append 小 bug。
9. utils.py:1521 `extract_attribution_explanation` 返回原文 text 而非解析值；devcontainer Dockerfile python3.12 与 CI 3.11 次版本漂移。
10. 批分析期 AST 手补 1 条边：utils 的 retry_operation 函数体内延迟 import log_sage（循环依赖打破，scanner 盲区）。

## 阅读路线

`onboarding/ONBOARDING.md` 八节；深读 explain 三篇：01 error_extraction.py（1030 行错误抽取引擎，return_application_errors 414→954 全项目最大函数）→ 02 log_sage.py（编排层+现行 CLI）→ 03 utils.py（1622 行 56 函数工具层）。
