# 06 · Data Construction Skill 与 md_to_qa 四平行方案线

## 角色定位

`data_construction_skill/` 与 `md_to_qa/` 共同承担基准第一板块"数据构造"：把 Markdown 书籍变成 SFT 监督数据。同一目标在仓内留下**四代平行实现**——Agent 提示词 → LLM 裸脚本 → DataFlow 管线 → SKILL 规范，本身就是一部"造数据工程逐步规程化"的演化史。`data_construction_skill/` 是终态：615 行 SKILL.md（Text2QA Builder 技能，发布名 Data Construction Skill，_meta.json 版本 1.0.1）+ 五脚本，已作为独立技能上架 clawhub.ai（根 README.md:78）。

## 内部结构

**SKILL.md（615 行）** 纯规程零代码，把"怎么从书造数据"写成 agent 可执行的宪法：三监督形式 concept_qa（原子知识）/process_qa（有据推理）/case_application（场景迁移）（L18-20）；**完成判定外部化**（L35-48）——完成的唯一定义是 check_coverage 三条件全绿（unprocessed=0、无 status 缺失、无计数错配），明令"部分进度只能报进度、不许报完成"；skip_reason 九值封闭枚举（L159-169"不许发明新标签"）；命题类型与 question_type 各 14 值 schema（L177-193、L459-476）；反模式黑名单含中英双语禁语（L394-404："according to the passage"/"根据本节"一律禁——题目须脱离书本独立成立）。样本与 chunk_status 的 JSON schema 给到字段级（L478-592）。

**五脚本** 是规程的机械执行端：`build_manifest.py`（57 行）rglob 扫 md、sha1 前缀入清单；`split_markdown_book.py`（180 行）标题栈切节（L25 `title_stack[:level-1]+[title]` 点睛行），<1200 字瘦节向后合并、>3000 字按段落二次切块（L124-130），chunk_id 编码 `{stem}_{节号:04d}_{块号:02d}`（L80）；`next_unprocessed_chunks.py`（85 行）断点续跑——status 差集选批 limit 25（L76-81）；`merge_jsonl.py` 合批；`check_coverage.py`（182 行）chunk↔status↔样本三表对账，逐类型核对"声称数量 vs 实际样本数"（L117-132）。

**md_to_qa 四方案线**：① `Agent/prompt.txt` 仅 18 行，最原始任务书（instruction/response 双字段、限定源文件夹、自主运行）；② `LLM/script_domain.py`（250 行）单文件裸脚本——`MODEL = "claude-opus-4-6"` 硬编码默认（L10），三模型运行时表 gemini-3-pro-preview/gpt-5.2/claude-opus-4-6（L18-34，opus 档 SAFE_MAX_INPUT=80 万 token），tiktoken 计数截断（L62-79）、```json fence 解析（L125-147）；`batch_process_domain.py`（156 行）subprocess 批驱动、单文件 1200s 超时（L76）；③ `DataFlow/` 两管线——`dataflow_skill_md_to_qa_pipeline.py`（112 行）四步：KBCCleaning 清洗→Text2QA 生成→LLM 1-5 打分→GeneralFilter ≥4 过滤（gpt-4o @localhost:8000）；`dataflow_kbcleaning_pipeline.py`（72 行）token 512 切块→清洗→**多跳 QA** 生成（deepseek-v3.2，num_q=5）；④ `SKILL/` 技能的仓内工作版。

## 外部连接

两棵 SKILL 树同源演化：`md_to_qa/SKILL/SKILL.md` 与 `data_construction_skill/SKILL.md` **逐行 diff 仅名字不同**（Text2QA → Data Construction Skill，L2/L6），但五脚本有实质差异——发布版 check_coverage 182 行 vs 工作版 193 行、validate_qa_jsonl 233 行 vs 338 行。上游接 Markdown 书源；下游 supervision_merged.jsonl 进 LlamaFactory 训练再交 Data-Agent-Evaluation 评测，构成基准闭环；根 README.md:67-73 布局表是四线唯一导航。

## 数据流

```
md 目录 → build_manifest → split_markdown_book → *.chunks.jsonl
  → [agent 按 SKILL.md 规程逐批处理] ← next_unprocessed_chunks 喂批
  → supervision_batches + chunk_status.jsonl（每批双写）
  → merge → validate → check_coverage → 全绿才算完成 → 微调
```

## 设计决策（含批判）

1. **完成判定外部化是全仓最值得抄的设计**：不靠 agent 自觉，把"做完了吗"交给 check_coverage 机器判定（L42-48），与 harness 工程"完成定义必须外部化"原则同构——LLM 自报完成不可信，脚本审计才可信。
2. **chunk_status 双写纪律**（L107-121）：每批"样本与状态同步落盘、先状态后合并"，杜绝悬空记录，三表对账才有账可查。
3. **四方案并存是特性也是负担**：capability 从一句话 prompt 长到 615 行规程，但四线数据 schema 互不兼容（instruction/response vs QA_pairs vs sample_type），无迁移工具。
4. **script_domain.py 的 API_URL/API_KEY 是空字符串占位**（L8-9），MODEL 默认 claude-opus-4-6——直接跑打空端点，属"自带配置骨架、填了才能用"的示例代码。
5. 批判：SKILL 线把内容质量押在 agent 遵循度上，五脚本只管"覆盖与对账"不管"好坏"——DataFlow 线的打分过滤在 SKILL 线无对应物。

## 新人提示

按演化史读：prompt.txt（30 秒）→ script_domain.py（token 治理与 fence 解析）→ dataflow_skill 管线（"生成+打分+过滤"闭环）→ SKILL.md 全文（规程化终态）。最小闭环：拿任一 md 书跑 split，手写 3 个 chunk 的 batch 与 status，跑 check_coverage 看审计输出。动手任务：为 SKILL 线补 DataFlow 式打分脚本。
