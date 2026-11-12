# 05 · 视图与组件：dataflow 大批、跳板页与 i18n 字典

## 角色定位

`views/` 与 `components/` 承载全部界面。两大区：`views/manage/` 是工作台八视图（dataflow 画布/serving/dm/prompts/schemas/dataviz/settings/analysis），`views/client/home/` 是理论上的实验室介绍页、实际是跳板。组件侧最重的是 `components/manage/mainFlow/`（画布容器：nodes/edges/panels/pipeline/tools）与 `chatPanel/`（Agent 对话）。本篇聚焦 dataflow 视图族的三个关键文件与 i18n 双语机制。

## 内部结构

`views/manage/dataflow/index.vue`（1181 行）是画布总控：`agentSyncPayload`（L300-340）处理 Agent 建好的 pipeline——优先走 `renderPipeline` 完整重建（L305 注释钉版"nodes/edges 字段已废弃，仅兼容"，无 config 才退回手动 addNodes），渲染前并发刷新 datasets/pipelines（L331-336，因 Agent 可能刚注册过数据集）；`beforeUnmount`（L398）兜底清拖拽监听。`hooks/dataflow/usePipelineOperation.js` 的 `renderPipeline`（L51-179）是出图核心：`$reset` 清画布 → `input_dataset` 双形状兼容（L77-80：Agent 存的裸字符串 id vs 前端存的对象，注释记录了只认对象形状导致孤立算子的旧 bug）→ 并发拉每个算子详情（L102-131）→ 自动水平布局（L142 的 `LAYOUT = { startX: 350, gapX: 320, y: 160 }`，L139-141 注释解释"不信任存储/agent 给的坐标"）→ 等 db-node 进图（L151-156）→ 连边（L159-178）。`useEdgeSync.js` 管"字段流"边：`decHandle`（L17-32）解析 `name::direction::edgeType` 手柄串；`syncRunValue`（L40-57）沿边把源算子参数值同步进下游同名 run 参数；`autoConnectRunEdges`（L67-95）按同名参数自动连 `run_key` 边。`components/manage/mainFlow/pipeline/index.vue` 是左侧模板抽屉：`selectPipeline`（L259-274）选模板后同样委托 `usePipelineOperation().renderPipeline`。

## 外部连接

视图层全部经 mapState/mapActions 挂 `stores/dataflow.js`（算子样式分组、serving、任务执行态都在那）；`chatPanel` 的 ws 事件（03 篇）最终也汇到 `agentSyncPayload`。`views/manage/index.vue`（254 行）是壳：L4 `fv-navigation-view` 侧边栏 + L28 `<router-view>`，navList（L61）与 Manage 路由一一对应。`views/client/home/index.vue` 全是 DAIR Lab 介绍内容，但 L102-104 `mounted() { this.$Go('/m') }` 一进即跳工作台——真身不可见。

## 数据流

模板选择流：pipeline 抽屉 selectPipeline → renderPipeline 重置画布出图。Agent 流：chatPanel 收 `sync_pipeline` → dataflow 视图 `agentSyncPayload` → 刷新三列表 → renderPipeline → 画布呈现节点/参数/边。字段流：用户在 operatorNode 改 run 参数 → useEdgeSync.syncRunValue 沿 run_key 边传播到下游同名参数——画布上的"数据依赖"是真的参数管道，不只是装饰。i18n 流：App.vue 启动把 `js/i18n.js` 字典灌进 appConfig → 全站 353 处 `local('...')` 调用按语言键取词。

## 设计决策（含批判）

- **勘误·addPipelineNode 死方法**：`pipeline/index.vue:237` 定义了一个 `addPipelineNode`，但全文件仅此一处出现（定义即终点，无模板/无调用引用）——真身是 `usePipelineOperation.js:16`（renderPipeline L148 消费）。这是抽取 hook 时漏删的旧副本，读代码时别把它当成出图路径。
- **勘误·getOperators 套娃笔误**：`operatorPanel.vue:158` 写成 `this.getOperators(this.getOperators(this.language === 'cn' ? 'zh' : 'en'))`——内层先发一次正确 lang 的请求，其返回值（Promise）又被当作 lang 参数传给外层再发一次：打开算子面板必然双请求，且第二次 lang 是脏值。L120 的正常单层调用是对照正解。
- **i18n.js 字典机制**：319 条 en/cn 词条（`"cn":` 计数），key 即英文原文，`appConfig.local()` 未命中返回原文——所以漏翻译不报错只退化成英文，是宽容也是隐患。
- **translator.py import 即执行回写**：`js/translator.py` 是 66 行笔记本式脚本（`# %%` 分节），顶层直接干活：L33-59 读 i18n.js、正则扫 `../` 下所有 local('...') 用法、缺词走 Google 翻译（L9-22 抓 translate.google.com/m 页面正则解析，L52-55 还硬编码替换"聊天→会话"等术语），L62-64 **回写 i18n.js**。没有 `if __name__ == "__main__"` 保护——任何模块 import 它都会触发网络请求 + 改写字典文件。只能手动在 js/ 目录裸跑，且依赖 Google 可达。
- **批判·1181 行视图**：dataflow/index.vue 混着画布控制、Agent 同步、Serving、执行、拖拽布局多类关注点，mapState 列表 L344-353 一屏放不下；`renderPipeline` 的 8 参数签名（L51，全靠位置传 proxy/$nextTick/$emit/$Guid）是典型坏味道——参数对象化或 provide/inject 更稳。

## 新人提示

改画布行为先分清两套节点流：结构（node 边，usePipelineOperation）与字段（run_key 边，useEdgeSync）。调"Agent 建完图没出现"看 agentSyncPayload 的刷新时序；调"算子面板数据怪"先看 L158 是不是又被抄出双调用。加翻译词：英文原文做 key 直接写 local()，跑 translator.py 补字典，但务必在 js/ 目录手动跑、别 import。home 页面改动无意义——它只活在 mounted 的一瞬间。
