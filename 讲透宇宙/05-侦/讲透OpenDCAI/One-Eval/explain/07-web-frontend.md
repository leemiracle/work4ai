# 07 · one-eval-web 前端：巨石页面与双模式驱动

## 角色定位

`one-eval-web/` 是 React 单页前端（Vite + TS + TailwindCSS + framer-motion + recharts），把后端 FastAPI 的 LangGraph 工作流包装成"聊天式评测控制台"。它不承载任何评测逻辑，职责三件事：**把用户意图翻译成 workflow 启动参数、把 1.5 秒一次的轮询渲染成进度、把 LangGraph interrupt 转成人可操作的审批表单**。路由极简（`src/App.tsx:9-23`）：`/` Home、`/eval` 主战场、`/settings`、`/gallery`，4 个页面里 `Eval.tsx` 一个文件吃掉大半复杂度。

## 内部结构

**Eval.tsx 巨石**：2520 行、43 处 `useState`（L56-115 声明区），状态分六簇：工作流（threadId/status/state/currentNode/interruptToken，L62-67）、历史（L70-71）、双模式 `workMode: "agent" | "manual"`（L57-60，localStorage `oneEval.workMode` 持久化）、手动模式专属（manualBenches/manualModelPath 等，L99-108）、interrupt 编辑态（editBenches/editMetricPlan）、UI 杂项。`apiBaseUrl` 用空依赖 useMemo 从 localStorage 读、默认 `http://localhost:8000`（L163）——**改了后端地址必须刷新页面**，这是新人第一个坑。

**12 端点矩阵**（全裸 axios）：GET `/api/models`(L291)、`/api/metrics/registry`(L300)、`/api/config/judge_model`(L308)、`/api/workflow/history`(L341)、`/api/workflow/status/{id}`(L359 轮询+L653 历史装载)；POST `start`(L522)、`resume/{id}`(L630)、`redownload/{id}`(L813)、`rerun_execution/{id}`(L832)、`manual_start`(L860)、`stop/{id}`(L875)；DELETE `history/{id}`(L713)。轮询核心 L354-431：`setInterval` 1500ms，终止于 completed/failed/stopped 或 `isResuming`（L355）——resume 后关轮询 3 秒（L635）防旧状态覆盖乐观更新。

**interrupt 审批**：轮询见 `interrupted`（L380-386）拼 token `threadId|next_node|JSON(interruptValue)` 存 `interruptToken` 去重弹窗。`handleResume`（L560-641）两道闸：PreEvalReviewNode 阶段任一 bench 的 eval_type 空或 unknown 即拒绝（L565-587）；启用了 llm-as-judge 但 Settings 无 judge 模型即拦截（L336）。resume payload 按节点差异化：非 MetricReviewNode 带 editBenches、MetricReviewNode 带 editMetricPlan（L603-628）——靠 `currentNode?.includes(...)` 字符串匹配路由（L611/L625）。

**编辑态合并**（L390-418）：interrupted 期间轮询只把远端状态性字段（download_status/dataset_cache/eval_status/meta.download_error）按 bench_name 合并进本地编辑副本，结构字段保留用户版；渲染层同约定 `{status === "interrupted" ? editBenches : state.benches}`（L1603/L1719）。

**BenchCard 六范式表单**（EvalComponents.tsx L239-1021，近 800 行）：三张静态表钉死六范式——`EVAL_TYPE_OPTIONS`（L244-251：key1_text_score/key2_qa/key2_q_ma/key3_q_choices_a/key3_q_choices_as/key3_q_a_rejected）、`EVAL_TYPE_REQUIRED_KEYS`（L252-259）、`EVAL_TYPE_GUIDE`（L260-285）。选范式→按必填映射生成 key_mapping 表单→存回 bench.meta。

**Settings.tsx**（1145 行、33 useState）四张 SettingsCard：Agent 服务(L575)/HuggingFace(L684)/目标模型注册表(L745)/Judge 模型(L980)，各带 test_request/test_load 连通测试（L440/L504/L536）。**Gallery.tsx**（1052 行、14 useState，L321-336）做三维过滤浏览+HF/本地双通道添加弹窗（L331 addMode、L334-335 上传表单）。

## 外部连接

- 唯一上游是 FastAPI 后端（06 篇），CORS 放行、可独立部署（apiBaseUrl 存 localStorage）。
- **@/ 别名体系**：`vite.config.ts` L9-11 `resolve.alias` 映射 `@→./src`，`tsconfig.app.json` L27-29 `paths` 对齐——双处必须同改，否则"运行时能跑、IDE 报错"。
- **i18n 自制**（`src/lib/i18n.ts`）：`t({zh,en})` 字典函数+localStorage `oneEval.lang`+自定义事件跨组件同步（L21），无 i18next 依赖，文案全内联双语。
- localStorage 键位全集：`oneEval.workMode` / `oneEval.apiBaseUrl` / `oneEval.lang`。

## 数据流

```
用户输入 query → handleRunClick(L899) 四路分派
  ├─ running → handleStop(L872) POST stop
  ├─ manual → handleManualStart(L841) POST manual_start
  │    （benches 只带 name/dataset_cache/eval_type/meta 四字段 L853-858）
  ├─ interrupted → handleResume(L560) 两道闸 → POST resume + state_updates
  └─ 默认 → handleStart(L505) POST start（25 字段 payload L522-547）
→ setThreadId → 轮询 1.5s/次 → running↔interrupted（token 去重）→ completed
→ WorkflowBlock 三段式(search/prep/exec) + SummaryPanel(recharts) 渲染
```

前端从不预测状态，一切以后端轮询事实为准；唯一乐观更新在 resume（L592-594），靠 isResuming 窗口保护。

## 设计决策（含批判）

1. 巨石单文件是主动选择也是债：数据流一眼望穿 vs 43 个 useState 依赖全靠脑记。拆 hook 时注意轮询 effect 依赖 `[threadId, status, isResuming, t]`（L431），status 每变即重建 interval，时序语义易丢。
2. 轮询而非 SSE：实现最简、断线自愈；代价是审批平均 0.75s 感知延迟+每次全量序列化 state_values。
3. interrupt 路由靠节点名字符串匹配是脆弱契约，后端改名前端静默失效；应后端带显式 `interrupt_kind`。
4. 六范式三张表与后端枚举手工镜像，schema 漂移隐患（10 篇批判 2 有实锤不一致）。
5. 构建产物入库：`tsconfig.app.tsbuildinfo`/`vite.config.js`/`vite.config.d.ts` 被提交（详见 12 篇 C2）。

## 新人提示

- 后端改端口前端"没反应"：查 `localStorage.oneEval.apiBaseUrl`（L163）后刷新页面。
- interrupt 不弹审批：先看轮询返回 `interrupts[0].value` 非空，再查 token 三元组是否变化。
- 找下拉选项来源：搜 `EVAL_TYPE_OPTIONS`（EvalComponents.tsx L244），全在静态表。
- 阅读序：App.tsx → i18n.ts → Eval.tsx L54-120（状态区）→ L354-431（轮询）→ L899-925（Run 分派）→ BenchCard 表单。
