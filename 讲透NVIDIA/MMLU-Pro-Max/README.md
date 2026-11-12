# 讲透 MMLU-Pro-Max

> MMLU-Pro 的多层鲁棒性改造基准：用 7 种转换器变体（格式/措辞/选项结构三类扰动）对同一题面做多口径评测，测传统 MCQ 测不出的输入敏感度。本仓只负责「造题」——推理执行与评分在外部 NeMo-Skills。

## 全链状态表（2026-11-08）

| 阶段 | 状态 | 产出 |
|---|---|---|
| 批分析 | ✅ 1 批 | 21 节点 / 41 边（7 转换器类+4 后处理器类全建节点，inherits 9 条） |
| merge | ✅ 零丢失 | 无悬空边 |
| layers/tour | ✅ | 6 层 / 12 步 |
| finalize | ✅ validator 0/0 | knowledge-graph.json（21n/41e） |
| fingerprints | ✅ | 9 files @ dd20018b |
| onboarding | ✅ | ONBOARDING.md 4794 字 / 27 锚 |
| explain | ✅ 3 篇 | MMLUProMax（2343 字/30 锚）/ postprocessors（2453 字/24 锚）/ convert_and_save（2457 字/14 锚） |
| 锚终验 | ✅ 真坏 0 | 106 锚全好（onboard 29/29 + explain 77/77） |

图谱在仓内 `/usr-data/data2/repos/agent-repos/NVIDIA/MMLU-Pro-Max/.understand-anything/knowledge-graph.json`。

## 源码甄别（写作期逐行实证）

1. **prompts.json 当前 HEAD 第 17 行结尾有尾逗号，json 严格解析必抛 JSONDecodeError**——MMLUProMax.py:36 在任何子类实例化时即触发，开箱即崩（写作期新发现，最重一条）。
2. **README 第 70 行 EMPTY_PROMPT_PATH=data/empty_prompt.yaml 与实际 config/ 路径不一致**。
3. **ABC 用 @abstractmethod 却未继承 abc.ABC**（MMLUProMax.py:22）——抽象性不强制，忘实现钩子的子类运行到 `pass` 才静默产出空结果。
4. **失败哲学双标**：BinaryPostprocessor 有 "unparsed" 哨兵，MCQ/Gen 全不命中时静默返回整个 generation 原文——脏数据直接混进 extracted_answer 列，统计前需过滤兜底。
5. 101/102 错误码用 print 而非聚合（postprocessors.py:54/:58）——长跑刷屏且不进结果文件。
6. MCQ 三个分割串与模板话术成对演化（改模板必须同步改 postprocessors.py:45 的 splitStrings）。
7. generative_ids 为 4755 个整数 id 的单行数组；转换器模板路径是相对路径 `./data/prompts.json`，必须仓根运行。
8. 防覆盖断言：extracted_answer 列已存在即抛 ValueError，重复 process 必炸（幂等性交给调用方）。

## 阅读路线

`onboarding/ONBOARDING.md` 八节；深读 explain 三篇：01 MMLUProMax.py（模板方法骨架+答案缺失/格式措辞/任务形态三族扰动）→ 02 postprocessors.py（三路答案抽取+哨兵双标）→ 03 convert_and_save.py（7 转换器编排入口）。
