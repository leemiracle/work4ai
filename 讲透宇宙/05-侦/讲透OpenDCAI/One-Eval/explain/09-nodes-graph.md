# 09 · nodes 双闸门与 graph 工作流编排

## 角色定位

`one_eval/nodes/`（15 文件）与 `one_eval/graph/`（8 文件）构成 LangGraph 执行层：nodes 是"一步"（包一个 Agent 或确定性逻辑成 `run(state)`），graph 是"一条路"（串节点+决定何时打断）。灵魂是**双闸门**：两个 `InterruptNode` 实例（HumanReviewNode、MetricReviewNode）加 PreEvalReviewNode，在"基准选择后"与"指标计划后"两个人机协作点用 LangGraph `interrupt()` 冻结工作流，决定权交给前端用户（07 篇审批 UI）。

## 内部结构

**workflow_all 七阶段**（`graph/workflow_all.py` `build_complete_workflow` L44-175，docstring L46-67）：①NL2Bench：QueryUnderstand→BenchSearch→HumanReviewNode（闸 1）②Download：DatasetStructure→BenchConfigRecommend→Download ③TaskInfer：DatasetKeys→BenchTaskInfer ④Eval：PreEvalReview→DataFlowEval（条件自循环）⑤MetricRecommend ⑥MetricReview（闸 2）⑦ScoreCalc→ReportGen→END。唯一条件边 `_route_after_eval`（L36-41）比较 `eval_cursor` 与 benches 长度，没评完回 DataFlowEvalNode——**逐 bench 游标循环**，前端 eval_progress 的 generated/total 对应此游标。

两闸门差异化配置（L77-85 vs L119-127）：HumanReview 的 rewind_nodes 可打回 Query/BenchSearch（重新搜基准）、决策模型 gpt-4o；MetricReview 的 rewind 只到 MetricRecommend、`model_name=None` 且 L101-112 专用短路——前端已确认指标组合时直接放行，省一轮 LLM。

**InterruptNode 审批协议**（interrupt_node.py `run` L51-190）：逐 validator 校验（L56），已在 `state.approved_warning_ids` 白名单的直接跳过（L59-61，**批一次永久放行**）；触发拦截即 `interrupt({...})` 冻结等人（L82-88，payload 带 node/validator_id/check_result）；反馈经 HumanInLoopAgent 决策出四元组 `{action,target_node,state_update,approve_validator}`（L124-140）；三出口全返回 LangGraph `Command`——goto_node 回跳（L172-174）、continue 放行（L176-178）、非法决策或 Agent 崩溃走 `_handle_rejection`（L183-187/L192-220）置 error_flag 并 goto failure_node=END。

**BenchSearchNode 两阶段**（bench_search_node.py L29-38）：先 `BenchNameSuggestNode` TF-IDF/RAG 检索（**不调 LLM**，L33），再 `BenchResolveAgent` 把名称解析成本地表+HF 可用配置（L35-39）。检索与解析分离，大部分推荐零 LLM 成本。

**node_docs SET/dict 静默错位（必读 bug）**：`utils/node_docs.py` L1-15 本意是节点说明字典，但三引号起始位写错——`"""QueryUnderstandNode": "..."` 把整个"键值对"吞成一个字符串字面量，外层花括号内无映射。**运行时实测：`type is set`、len 2、元素以 `QueryUnderstandNode": "解析...` 开头**。消费链四处 Dict 注解全拿 set：workflow_all.py L84/L126（InterruptNode 构造）→ interrupt_node.py L26（注解 Optional[Dict]）/L35（`or {}` 兜底对非空 set 失效）/L138（转传）→ human_in_loop_agent.py L49/L62/L75。终点 `_safe_dump`：`json.dumps(set)` 抛 TypeError（实测 "Object of type set is not JSON serializable"），被 L71-72 `except Exception: return str(obj)` 吞掉，prompt 里 `{node_docs}`（utils/prompts.py L208-210）填的是 set 的 repr。**全链静默无日志**，HumanInLoopAgent 决策上下文受损。修复：改成真正的 `"NodeName": "doc"` 映射。workflow_nl2bench.py L59 同样在传。

**workflow 家族**：workflow.py（80 行基座）、nl2bench（158 行三节点小图 L35-70，Phase 1 独立版）、bench_gallery（733 行最长，Gallery 后端）、bench_verify（304）、download（104）、eval（103）、metric_recommend（93），workflow_all 是超集。`run_full_pipeline`（L178-237）演示 checkpoint 协议：SqliteSaver 落 checkpoints/eval.db（L182）、interrupt 态用 `Command(resume="approved")` 恢复（L220-227）。

## 外部连接

- 上游：LangGraph（StateGraph/interrupt/Command，L5/L7-8）；utils/validators.py 的 benches_manual_review/metric_plan_review（L79/L121）。
- 下游：server 层按 thread_id 驱动前端轮询（06 篇）；`_save_state_json` 落 outputs/。
- Agent 层（08 篇）：InterruptNode→HumanInLoopAgent、BenchSearch→Suggest+Resolve，节点与 agent 一一对应。

## 数据流

```
POST /workflow/start → thread_id → 图启动
QueryUnderstand(NL→结构化) → BenchSearch(检索+解析)
→ HumanReviewNode：validators 校验 benches
   ├─ 全过 → Command(goto=DatasetStructureNode)（L189-190）
   └─ 拦截 → interrupt() 冻结 → 前端审批 → resume
        → HumanInLoopAgent 决策 → goto_node/continue/rejection
→ Structure→Config→Download→Keys→TaskInfer（确定性管道）
→ PreEvalReview → DataFlowEval ×N（游标循环 L36-41）
→ MetricRecommend → MetricReview（闸 2，短路 L101-112）
→ ScoreCalc → ReportGen → END（checkpointer 全程持久化）
```

单一 `NodeState` 贯穿：benches/eval_cursor/approved_warning_ids/llm_history/result 增量写入，interrupt 的 update_dict 是同 schema 局部补丁。

## 设计决策（含批判）

1. 双闸门+白名单是干净的人机协议：拦截原因结构化进 payload，批一次永久放行；但白名单只增不减（无过期无撤销），thread 内不可逆。
2. HumanInLoopAgent 让 LLM 解读反馈再路由很灵活，但决策失败兜底为 rejection 终止（L147-151）——一次 LLM 抖动可杀整条工作流，缺"重问一次"中间态；`if self.name == "MetricReviewNode"` 字符串硬编码短路（L101）又把专用逻辑焊进通用类。
3. node_docs 错位暴露无测试盲区：Dict 注解与运行时 set 并存四层无人察觉；"只进 prompt 的数据"也值得一行 `assert isinstance(node_docs, dict)`。
4. workflow 家族复制漂移：nl2bench/all/gallery 三份各自装配同名节点，改一忘二风险线性上升；run_full_pipeline 默认模型硬编码 `/mnt/DataFlow/models/Qwen2.5-7B-Instruct`（L210-214）裸跑必失败（12 篇 C1）。

## 新人提示

- 按七阶段 docstring（L46-67）对照 edges（L137-173）画图最快；L145-146 注释解释了为何 HumanReview 的 success 边不需显式 add_edge——Command(goto) 直接跳。
- 调试"卡在审核"：先查 approved_warning_ids 是否白名单短路，再看 server 日志 interrupt payload 的 validator_id。
- 改节点行为优先改对应 agent（08 篇）；nodes 层除 interrupt/dataflow_eval/bench_name_suggest 三个重文件外多是 30-90 行薄壳。
- 给 HumanInLoopAgent 加节点说明前，先修 utils/node_docs.py 的 set 错位。
- eval 进度不动时查 `eval_cursor` 是否被 DataFlowEvalNode 递增——游标不同步是高发 bug 点。
