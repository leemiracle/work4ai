# 06 · server.py 巨石 FastAPI：23+ 路由与 interrupt 竞态治理

## 角色定位

`one_eval/server/app.py`（2133 行单文件）是 WebUI 的全部后端：配置管理、工作流编排、模型管理、bench gallery、本地 bench 上传五块塞一处。启动时 `uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio")`，注释明言禁 uvloop 是给同步节点里的 nest_asyncio 让路（app.py:2131-2133）。路由实测 27 个装饰器（/health+26 个 /api/*），其中 `/api/workflow/*` 路径 9 个——任务书/图谱口径「23 路由/11 端点」与源码不符，以源码为准。

## 内部结构

**早期环境块**（24-73 行）：启动先解析 `env.sh` 注入 os.environ（47-73，仅填缺失键，shell 可覆盖）；`load_server_config`（162-251）读 `_data/config.json` 三块 hf/agent/judge_model 并补默认值；agent 配置双写 `OE_*`/`DF_*` 两套环境变量（363-380）。DB 固定 `checkpoints/eval.db`（40 行）。

**interrupt 内存缓存**：模块级 `_thread_interrupt_cache: Dict[str, bool]`（45 行）。`run_graph_background`（902）的 `ainvoke` 返回值若含 `__interrupt__` 立即置 True（922-924），正常完成则 pop（928）；stop/resume 也会 pop（966/1173）。存在理由：`get_status` 查 checkpoint 判断中断态有竞态——`interrupt()` 触发到持久化之间有窗口，next=() 且 interrupts=[] 的瞬间既可能是完成也可能是中断执行中。`get_status`（980）因此做了两层防御：先把三节点名 `INTERRUPT_NODES=("HumanReviewNode","PreEvalReviewNode","MetricReviewNode")` 当中断信号（1040-1045）；对「next 空且无中断」的场景查内存缓存，再退一步竞态重试最多 8 次、100→300ms 递增（1021-1065）。

**vLLM 显存释放**：`run_graph_background` 的 finally 里，仅当线程**不是** interrupt 态才调 `DataFlowEvalTool.release_serving()`（942-949）——类级缓存的 vLLM serving cleanup 置空（dataflow_eval_tool.py:98-107）。设计意图：人审暂停后 resume 还要用同一模型，此时释放等于自废武功；只有真正跑完才回收 16GB 级显存。

**九个 workflow 端点**：start（850）、stop（960，task.cancel+标记 stopped）、status（980）、resume（1085）、rerun_execution（1177）、manual_start（1247，前端选好 bench 直入评测）、redownload（1554，后台重下）、history GET/DELETE（1596/1673）。三个细节：resume 先把 `state_updates` 经 `aupdate_state` 写进 checkpoint（1129-1133），action=approved 且停在 PreEvalReview 时前置校验每 bench 的 eval_type（1144-1169）；rerun 清 `eval_result/eval_detail_path/eval_error/eval_abnormality` 四键、`eval_cursor=0`，再 `Command(goto=...)`（1238-1244）；同线程重启先 cancel 旧 task（951-958）。

**其余路由**：config 三组 GET/POST+连通测试（494-709）；models CRUD+`test_load`（1725-1843，真起 `LocalModelLLMServing_vllm`，1828）；benches gallery GET/POST/DELETE+upload（1904-2088）；metrics registry（1909）返回注册表元数据。

## 外部连接

被 one-eval-web 前端消费；graph 侧每次请求现场 `build_complete_workflow`（同一 checkpointer DB）；配置写 `_data/` 三文件；bench 数据走 04 篇的 BenchRegistry。

## 数据流

start → uuid thread_id → `_launch_graph_task` 起 asyncio 后台任务 → 图跑至 interrupt 或完成 → 前端轮询 status（读 checkpoint+内存缓存+progress_store 进度）→ 人审 resume 带 state_updates → 续跑 → finally 释放显存并写 thread_meta 时间戳。

## 设计决策（含批判）

1. **2133 行巨石**：五块职责一文件，路由+业务+持久化+环境管理混杂——分层拆分是最大欠账。
2. **CORS `allow_origins=["*"]` 与 `allow_credentials=True` 并存**（482-488）：按 cookie 语义是矛盾组合，Starlette 实际回显任意 Origin，等于全放开+带凭据，公网部署是洞。
3. **内存态三件套**（RUNNING_WORKFLOW_TASKS/_thread_interrupt_cache/thread_meta.json）：任务表与中断缓存在进程内存，多 worker/水平扩展即失效；thread_meta 又落盘，半内存半持久的一致性要小心维护。
4. **status 竞态治理是亮点**：内存缓存+节点名判定+定时重试三层，比单纯信任 checkpoint 可靠。

## 新人提示

起服务后先 GET /health 与 /api/config/agent 排环境；调人审卡死看三处：`_thread_interrupt_cache` 日志、thread_meta 的 stopped 标记、checkpoint 的 snap.next。改配置优先走 /api/config/*（有默认值合并逻辑）而非手改 config.json。「workflow 结束但显存没掉」别慌——interrupt 态故意不释放，resume 复用是特性。
