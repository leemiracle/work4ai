# 05 · Data-Agent-Evaluation：三 CLI 评测链与两个开箱即跑的坑

## 角色定位

`Data-Agent-Evaluation/` 是基准的"裁判席"：构造出的数据训完模型（LlamaFactory + Qwen2.5-7B/Llama-3.1-8B），回这里测六域下游能力（README.md:13-18：Math/General/Science/Business/Medicine/Law）。两条腿：math/general/science 三域**外包**给三个 submodule 框架按各自原始协议跑；business/law/medicine 走自研 `simple-evaluation/` 统一管线。

## 内部结构

**inference.py**：AsyncOpenAI 批量推理。`process_one`（L16-59）透传 completion_args（L32-37），回复 append 进 messages、raw_response 留痕（L42-47）；三次重试（L56），最终失败写占位串 `"Fail to generate response"`（L52）而非跳过——记录完整，判定留给 judge。

**judge.py（39KB，核心）**：统一裁判。dispatcher `judge_one`（L772-795）按 `metadata.source` 分派七基准（fincdm/xfinbench/legalbench/lexglue/medcasereasoning/medmcqa/medrbench），每个 judge 都**规则优先、LLM 兜底**：fincdm 先正则抽选项字母（L58-65），规则命中直接判分不花裁判钱（L98-99）；不匹配才请 LLM 并解析 JSON 回复（L68-81 双重容错）。**0.5 是贯穿全文件的"未知/出错"哨兵**（L127/234/559/729/738/758/795 七处返回点）。断点续跑：`compute_stable_id`（L823-839）对领域元数据+messages 做 SHA256 取 16 位——**内容寻址而非行号寻址**，重跑顺序变了也对得上（L947-953 注释明示）；should_retry 记录不进 done 集合下次自动重判。L1009-1020 早依赖检查：lex-glue-extra 三个 arrow 目录 + MedRBench-extra.json 缺失即 sys.exit(1)。

**extract_score.py**：按 source 分桶过 AGGREGATORS（L210-218 七聚合器）与 DOMAIN_BENCHMARKS（L220-224 三域映射）。指标各异：legalbench 用 balanced_accuracy（L54-74）；lexglue 的 eurlex/unfair_tos 多标签——分子"命中 gold 标签数"、分母"gold 标签总数"（L158-165）；medrbench 聚合前滤掉 should_retry（L199）。

**run_evaluation.sh** 三步流水线：起 vLLM serve（8002 端口，L154-161）→ /health 轮询（L107-134）→ 依次 inference（L185）→ judge（L206）→ extract_score（L222）；`trap cleanup_vllm EXIT`（L101）任何退出路径都杀服务。

## 外部连接

数据从 HuggingFace `lhpku20010120/Data-Prep-Bench` eval/ 入 `simple-evaluation/data/{domain}.jsonl`（README.md:33-43）；医学真值库 `MedRBench-extra.json`（15MB，实测 **957 案例**，键为 PMC 论文 id，gold 在 `generate_case.diagnosis_results`——judge.py:698 取的正是它）；法律标签表在 lex-glue-extra/*.arrow。裁判走 OpenAI 兼容 API（默认 gpt-4o）。

## 数据流

```
data/{domain}.jsonl → inference.py(被测模型) → inference_results.jsonl
  → judge.py(裁判模型) → judge_results.jsonl + failed/error 分流
  → extract_score.py → calculated_scores.json
```

## 设计决策（含批判）——两个必踩的开箱坑

1. **三个 submodule 全未初始化，math/general/science 线不可运行**。`git submodule status` 三条记录全带 `-` 前缀，目录空壳。而 run_all_bench.sh:35-37 的 MATH_DIR/GENERAL_DIR/SCIENCE_DIR 恰指向这三个目录，cd 进去即失败。克隆后必须 `git submodule update --init`，且脚本还假定名为 math/general/science 的三个 conda 环境（L63/114/146）。business/law/medicine 不受影响（管线在主仓内完整）。
2. **`MedRBench_instructions/acc_diagnose.txt` 全仓不存在，medrbench 裁判恒 0.5**。judge.py:735 用**相对路径**读提示词模板（还要求 CWD=simple-evaluation/），L736-738：模板缺失 → 每条 medrbench 记录返回 0.5 + should_retry=True，全进 error.jsonl。连锁到 extract_score.py:199：should_retry 全被滤掉 → total=0，accuracy 报 0.0。该文件**不在 L1009-1020 早检查清单**——启动正常，跑完 957 条才发现全废。修复：补 acc_diagnose.txt 并加进早检查。
3. 批判：0.5 哨兵混载"裁判挂了/真值缺失/模板缺失"三种异因，extract 层无法区分；规则优先省裁判费值得肯定。

## 新人提示

首跑 `./run_evaluation.sh <model> business <outdir>`（依赖最少）；先 `--debug-limit 20 --mock-openai`（judge.py:913-915）验证贯通再放全量。读 judge.py 抓三锚：judge_one 分派表、0.5 七处返回点、resume 的 stable_id。动手任务：为 acc_diagnose.txt 写最小模板（契约=L743 的 `template.format(pred_diagnose=..., gt_diagnose=...)`）。
