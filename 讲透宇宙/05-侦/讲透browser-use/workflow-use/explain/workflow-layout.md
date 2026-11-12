# workflow-layout.tsx 精讲——ui 主布局组件（ReactFlow 工作流可视化画布与状态中枢）

## ① 角色定位

`ui/src/components/workflow-layout.tsx`（263 行）是 L13「ui React 可视化前端」的骨架组件：左侧 Sidebar 列工作流、右侧 ReactFlow 画布把工作流 JSON 画成节点流图、右上角 PlayButton 触发执行、点节点弹出 NodeConfigMenu 编辑步骤。它自己就是整个 ui 的组合根——`App.tsx` 仅 17 行，渲染的正是这个组件。

它的独特之处在于承担三重职责：**数据层**（openapi-react-query 拉后端 REST）、**状态层**（选中项/节点/边/元数据/已存节点坐标五组 useState）、**视图层**（ReactFlow 画布与子组件编排）。理解它就理解了 ui 的全部数据流。

## ② 内部结构

组件内按功能分六块：

**ReactFlow 状态**（L32-33）：`useNodesState`/`useEdgesState`（@xyflow/react v12）——受控节点/边 + 内置的拖拽、选择、位置变更处理。

**查询层**（L44-80）：三个 `$api` 钩子——`useQuery("get", "/api/workflows")` 拉列表（L44-45）；`useQuery("get", "/api/workflows/{name}")` 拉选中项（L53-65，`enabled: !!selected` 条件启用，未选中时传 `name: ""` 占位保持 query key 稳定）；`useMutation("post", "/api/workflows/update-metadata")` 存元数据（L68-71）。

**选中与菜单**（L31/L34/L90-97）：`selected` 工作流名、`selectedNode` 待编辑节点、`onNodeClick` 进菜单、`closeNodeMenu` 关菜单。

**布局记忆**（L37-39）：`savedNodePositions`——`Record<工作流名, Record<节点id, {x,y}>>` 两级字典，`onNodeDragStop`（L137-153）在拖拽松手时写入。

**同步 effect 三个**：fitView（L100-106，useLayoutEffect + requestAnimationFrame，节点数变化时重适配视口）；workflow→nodes 同步（L109-134，`jsonToFlow` 转换 + 套用已存位置）；自动选中首个工作流（L156-160）。

**渲染树**（L164-260）：加载态旋转 logo（L164-175）→ 空态 NoWorkflowsMessage（L177）→ 主布局：Sidebar（L181-191，传元数据更新回调）+ ReactFlow 画布（L196-210，colorMode="dark"，Background/MiniMap/Controls 三件套）+ 动作区（L213-243：PlayButton 与 Refresh 按钮）+ 条件渲染 NodeConfigMenu（L251-257）。

## ③ 外部连接

- **API 层**：所有请求经 `../lib/api` 的 `$api`（openapi-fetch + openapi-react-query，baseUrl 硬编码 `http://localhost:8000`，index.ts L6）。`paths` 类型来自 `./apigen`——由 `npm run type-gen`（openapi-typescript 吃 openapi.json）生成，`postinstall` 钩子自动跑（package.json）；端点路径字符串（如 `"/api/workflows/{name}"`）因此是**类型级校验**的，拼错路径编译不过。
- **兄弟组件**：Sidebar（工作流列表+元数据编辑）、NodeConfigMenu（步骤配置，收 `node`/`workflowFilename`）、PlayButton（执行+日志轮询，收 `workflowName`/`workflowMetadata`）、NoWorkflowsMessage。子组件经 props 回调上行，无全局 store。
- **工具**：`jsonToFlow`（utils/json-to-flow.ts）把后端返回的工作流 JSON 字符串转 `{nodes, edges, metadata}`——steps 逐个成节点（id=数组下标，y=idx×100 纵向排布，json-to-flow.ts L11-20）、相邻步骤连 animated 边（L22-27）。
- **类型**：`WorkflowMetadata`（types/workflow-layout.types.ts L52-58：name/description/version/input_schema/workflow_analysis）与 NodeData/StepData（node-config-menu.types）。

## ④ 数据流

初始化流：挂载 → useQuery 拉列表 → 空则 NoWorkflowsMessage，非空自动 setSelected(workflows[0])（L157-159）→ enabled 变真拉详情 → effect 调 jsonToFlow → setNodes/setEdges/setWorkflowMetadata → rAF 后 fitView。

交互流两环：**查看环**——点 Sidebar 项换 selected → 新详情 → effect 重建节点（若该工作流在 savedNodePositions 有记忆则套用旧坐标，L114-126）；**编辑环**——点画布节点 → NodeConfigMenu（提交时自己调 update 端点）→ 拖节点 → onNodeDragStop 记坐标 → savedNodePositions 变更触发 L109 effect 重跑 → jsonToFlow 重算（位置取记忆值，视觉无跳变）。

元数据环：Sidebar 内编辑 → onUpdateMetadata 回调（L186-190）→ updateWorkflowMetadata → mutation POST → 后端 YAML 重写。

## ⑤ 设计决策与取舍

**类型安全的 API 客户端全靠生成链**：openapi-fetch 的价值是 URL/参数/响应全类型化，但代价是 apigen.d.ts 必须与后端同步生成——契约漂移时类型报错，这是"前端契约跟随后端"的正确姿势；相对地，后端一旦改端点而前端没重跑 type-gen-update，编译期就会拦住。

**节点位置只在内存**（L37）：savedNodePositions 是 useState，刷新即丢。名为"saved"实为会话内记忆——设计上接受了"用户重排不被持久化"，换取零后端写接口（后端也确实没有存位置的端点）。

**id=数组下标作为节点身份**（json-to-flow.ts L12）：最简单的稳定标识（后端 update 端点也用 nodeId 当 steps 下标，routers/service.py L135-136 两侧对齐），但插入/删除步骤后所有后续节点 id 平移——与"位置记忆按 id 存"组合时，改工作流内容会让旧坐标错配到新节点上。

**effect 依赖 savedNodePositions 引发的重算**（L134）：拖一次节点 → effect 整体重跑 jsonToFlow + setNodes。当前规模（几十步）无感，是"用声明式重算换代码简单"的取舍；节点多时会放大为卡顿。

**Refresh 按钮实际是"保存元数据"**（L222-226）：点击调 updateWorkflowMetadata 而非 refetch——语义错位（见⑥），但也暴露了设计意图：靠 mutation 的响应副作用让 React Query 失效相关缓存，间接达成刷新。

## ⑥ 新人提示（坑/勘误）

1. **Refresh 按钮不做刷新**（L219-242）：`title="Refresh workflow"` 但 onClick 调 `updateWorkflowMetadata(selected, workflowMetadata)`——把**当前内存里的元数据原样写回**，既不重新拉列表也不重拉详情。想让画布更新请改用 queryClient.invalidateQueries；现在的行为在元数据未变时是一次无意义写入。
2. **workflowSchema 是死校验器**（workflow-layout.types.ts L34-41）：zod schema 定义了完整工作流结构，但 jsonToFlow 只用 `JSON.parse(workflow) as Workflow`（json-to-flow.ts L10）做**类型断言**——zod 校验从未执行，畸形 JSON/缺字段的步骤会静默变成空 label 节点而非报错。
3. **step type 枚举与现实脱节**（types L21）：zod 枚举只有 `navigation/click/select_change/input` 四种，而 Python 引擎实际产出 `key_press/extract_page_content/scroll/go_back/go_forward` 等（deterministic_converter L769/L793/L809 等）——若哪天真启用 zod 校验会全军覆没；现在只是类型上"看不见"这些步骤类型。
4. **input_schema 类型枚举与后端不一致**：前端 `'string' | 'number' | 'boolean'`（types L10/L56），后端 variable_identifier 的 type_mapping 产出 `'string' | 'number' | 'bool'`（其 L449-461）——`bool` 值过 zod 枚举会 fail；当前因第 2 条（校验未启用）而未爆雷。
5. **openapi.json 0 字节 + apigen 不在盘上**：`npm run type-gen` 吃的 openapi.json 是 get-openapi（curl localhost:8000）的产物——后端没起时 curl -o 留空文件（当前盘上正是这个脏状态）。clone 后直接 npm install，postinstall 会对着空 json 生成（或失败）。正确姿势：先起后端，再 `npm run type-gen-update`。
6. **L57-61 的空名占位**：selected 为 null 时仍传 `path: { name: "" }`——不是 bug（enabled 挡住了请求），但空串占位使 query key 从 undefined 变 ""，缓存语义略怪；改成条件性构造 key 或 skipToken 更直白。
7. **onNodeDragStop 后的整图重算**（L134 依赖数组含 savedNodePositions）：拖拽每松手一次，jsonToFlow 全量重跑、全部节点对象重建——ReactFlow 靠 node id 复用 DOM 没有视觉跳变，但 React reconciliation 成本随步骤数线性涨。大工作流上拖节点出现卡顿先查这里。
8. **fitView 依赖 nodes.length 而非 selected**（L100-106）：切换工作流时若两者步骤数恰好相同（length 不变），fitView 不触发——视口停留在旧图缩放位置，需手动 Ctrl+1。
