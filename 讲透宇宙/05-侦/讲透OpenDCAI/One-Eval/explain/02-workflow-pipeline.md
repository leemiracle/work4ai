# 02 · 七阶段主管线 workflow_all 与人审环

## 角色定位

`one_eval/graph/workflow_all.py` 是全流程主编线：把 01 篇的 13 个节点拼成「自然语言进、评测报告出」的 LangGraph 图。同目录另有 8 张子图（nl2bench/download/eval/task_infer/metric_recommend/bench_verify/bench_gallery 与单节点 demo 的 workflow.py），其中 `workflow_nl2bench.py` 是主管线 Phase 1 的独立精简版。

## 内部结构

`build_complete_workflow`（workflow_all.py:44）按 docstring 七阶段拼装（48-67 行）：**Phase1** QueryUnderstand→BenchSearch→HumanReviewNode（InterruptNode 实例，成功去 DatasetStructure、失败直接 END，77-85）；**Phase2 下载** DatasetStructure→BenchConfigRecommend→Download；**Phase3** DatasetKeys→BenchTaskInfer；**Phase4 评测** 前置 PreEvalReviewNode（108-109，一次性闸门）+ DataFlowEvalNode；**Phase5** MetricRecommend；**Phase5.5** MetricReviewNode（119-127，第二处 InterruptNode）；**Phase6** ScoreCalc；**Phase7** ReportGen→END。DataFlowEval 出口是唯一条件边 `_route_after_eval`（36-41）：`eval_cursor < len(benches)` 回自身循环下一个 bench，否则去 MetricRecommend。

**nl2bench 特殊线**（workflow_nl2bench.py:23-75）：仅三节点，且 success_node 与 failure_node 都是 END（52-53）——审核通过即收工，因为产出就是 bench 候选清单本身。

**审批环三件套**：①`interrupt_node.py:82` 用 `interrupt({node, validator_id, check_result})` 暂停图等人输入；②`HumanInLoopAgent`（human_in_loop_agent.py:41）把节点说明、校验结果、人类反馈喂给 LLM，产出 `{action, target_node, state_update, approve_validator}` 决策——`goto_node` 目标不在 allowed_nodes 白名单强制改 continue（133-139），输出非 dict 默认 continue+approve（113-122）；③InterruptNode 按决策 `Command(goto=...)` 回跳或放行（172-178），命中过的 validator id 进 `approved_warning_ids` 白名单避免重复拦截（54-61）。MetricReviewNode 有快捷通道：approved 输入直接放行、跳过 Agent（101-112）。`PreEvalReviewNode` 最简：confirm_id 已在白名单直通 DataFlow（pre_eval_review_node.py:17-19），否则 interrupt 一次、记账放行（25-40）。

## 外部连接

checkpoint 落 `checkpoints/eval.db`（workflow_all.py:181-183 经 `get_checkpointer`）；生产入口不是 `__main__` 而是 server/app.py 的 `/api/workflow/start`（自建图、同 DB）；DataFlowEvalNode 经 DataFlowEvalTool 接 DataFlow 推理管线；`utils/validators.py` 供两处 validator，`utils/node_docs.py` 是 HITL 的节点说明书。

## 数据流

`run_full_pipeline`（178）：无 checkpoint 则 `NodeState(user_query, target_model=...)` 起跑；有则查 `snap.next` 是否停在三个人审节点，是就 `Command(resume="approved")` 续跑，否则 `ainvoke(None)` 断点续跑（203-230）。多 bench 靠 `benches`+`eval_cursor` 游标推进；DataFlowEvalNode 校验 `bench_dataflow_eval_type` 须在六个合法枚举内（dataflow_eval_node.py:17-24），评测失败清 confirm_id 并 `Command(goto="PreEvalReviewNode")` 带错误回跳（275-286），成功 cursor+1（287）。

## 设计决策（含批判）

1. **三处人审闸门各司其职**：HumanReview 管 bench 清单、PreEvalReview 管评测前放行、MetricReview 管指标组合。白名单让「批准过的不再问」，但粒度是 validator id，同 id 换 bench 不会再拦。
2. **HITL 决策交给 LLM**：回跳哪步由模型拍板，虽有 allowed_nodes 硬约束，选错仍浪费一轮重跑。
3. **默认模型硬编码** `/mnt/DataFlow/models/Qwen2.5-7B-Instruct`（workflow_all.py:211），演示便利与生产洁癖冲突。
4. **MetricReview→Score 显式边被注释**（168 行），全靠 Command 动态路由——静态图不完整，可视化易失真。

## 新人提示

最小闭环看 workflow_nl2bench.py（159 行）；全链读 workflow_all.py 的 docstring 与边表对照。调人审三查：`approved_warning_ids` 是否含该 validator、`snap.next` 停在哪、HumanInLoopAgent 的 decision 日志。resume 语义一句话：`Command(resume=值)` 是给 `interrupt()` 的返回值赋值。
