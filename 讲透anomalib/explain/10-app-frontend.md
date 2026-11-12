# 10 · anomalib Studio 前端（application/ui/）

## 一、角色定位

`application/ui/` 是 anomalib Studio 的 React 19 SPA（图谱 app-frontend 层，279 节点，其中 `src/features/inspect/` 特性域独占 196 文件），技术栈 Rsbuild + openapi-fetch/openapi-react-query 类型化数据层 + @geti-ui/ui 组件库 + MSW/vitest/playwright。它不实现任何检测逻辑，tour T13 定位一针见血：**把后端 API 当可视化投影**。理解顺序不是组件树而是用户旅程：Welcome → Dataset 页上传图片 → Train model 对话框发起训练 → Models 视图看进度 → 打开 pipeline 开关进入 Stream 实时检测。前后端唯一契约是后端 OpenAPI schema 生成的 `src/api/openapi-spec`；URL 查询参数 `?mode=Dataset|Models` 承担"页签即路由"。

## 二、内部结构

**routes/router.tsx:18（71 行）**：`Redirect`（L18-27）是首页智能跳转——L19 `$api.useSuspenseQuery('get', '/api/projects')`，空则去 welcome（L22），否则跳第一个项目的 `?mode=Dataset`（L26）。L29-71 路由树：根布局（Toast+Suspense+Outlet，L33-41）下挂 index/welcome/project(Layout>Inspect)/openapi，L66-68 通配也交 Redirect。"无项目引导建项目、有项目直达工作区"零手动配置。

**api/client.ts:12（44 行，全站唯一 API 出口）**：L12 `API_BASE_URL = import.meta.env.PUBLIC_API_BASE_URL || (isTauri() ? 'http://localhost:8000' : '')` 一行解决双形态——Tauri 桌面壳页面来自 `tauri://localhost` 必须写死绝对地址，Docker/浏览器同源走相对路径。L14-16 `createFetchClient<paths>` + `createClient` 产出 `$api`，组件经 `$api.useQuery/useMutation` 获端到端类型推导。L31-44 `getApiUrl` 专为 EventSource/`<img>` 等直连场景拼绝对 URL（SSE 与 MJPEG 流都靠它）。

**train-model-dialog.component.tsx:28（139 行，旅程起点）**：`TrainModelDialog`（L28）聚合 `useTrainingDevice()` 设备列表（L35）与本地 `selectedModel`（L36）。L31-33 `useMutation('post', '/api/jobs:train', { meta: { invalidates: [['get', '/api/jobs']] } })` 是典型写法——成功自动失效缓存。`startTraining`（L41-59）POST `{project_id, model_name, device:{type,index}}`（L46-52），随后关框、dismiss toast、L57-58 切 `mode=Models`。模型选项 `TrainableModelListBox`（L105）由后端 trainable-models 供货（见 09 篇）。

**models-view.component.tsx:52（168 行，中转）**：核心是**job 与 model 合成一张表**。`useCompletedModels()` 出已完成模型（L57），`useProjectTrainingJobs()` 出进行中任务（L53）；L61-83 把未完成 job 映射成伪 ModelData（L73 状态显示 Training/Failed，L77 带 progress），L85 `useShowModels` 合并并把模型 id 翻译成 trainable-models 显示名（L44）。L87-93 `tableSelectedKeys` 从 `pipeline.model?.id` 反推选中行——活跃流水线的模型自动高亮，这就是"投影"。L129-147 已完成模型名是可点 Link（onModelSelect）+ 进度徽章。

**dataset.component.tsx:12（33 行）**：极简容器，L19-20 标题右侧放 `UploadImages`/`TrainModelButton`，主体交 `DatasetList`——逻辑在 dataset/ 特性域 31 个兄弟组件（上传/缩略图/推理预览）。

**stream-container.tsx:14（82 行，终点）**：状态机容器。L15-17 三钩子：`usePipeline`、`useStreamConnection`、`useActivateAndRunPipeline({onSuccess: start})`。L12 `RECONNECT_CLEANUP_DELAY_MS = 300` 是踩坑产物——重连（L19-36）先 `stop()` 等 300ms 清理；pipeline 已 running 直接 `start()`，否则先激活再由 onSuccess 开播。L54-79 按 status 分流：idle→播放钮，disconnected/failed→Reconnect，connecting/connected→`<Stream/>`。

**components/stream/stream-connection-provider.tsx:5（57 行）**：L5 五态 `'idle'|'connecting'|'connected'|'failed'|'disconnected'`；L15 `STREAM_ENDPOINT='/api/stream'`；L23-26 `start()` 置 connecting 并设 `streamUrl = getApiUrl('/api/stream')?ts=${Date.now()}`（时间戳防缓存）。真正消费在 `stream/stream.component.tsx`：L148-151 `<img key={streamUrl} src={streamUrl}>` 把 MJPEG 端点当图片 src；L119-122 `handleStopStream` 先把 src 置 `'data:,'` 再 stop——注释明说浏览器在 img 卸载后仍会继续拉 multipart 流，必须显式断。L139 `Fps` 仅 connected 时显示。

**api/fetch-sse.ts:4（48 行，第二信道）**：`fetchSSE`（L4）用 async generator 包装 EventSource：L10 `Promise.withResolvers` 手搓暂停/恢复，L13 收到 `DONE`/含 `COMPLETED` 即 close，L36 `yield JSON.parse(message)`。消费方是 footer 训练状态适配器与 job 日志查看器——训练进度走 SSE、检测画面走 MJPEG，两信道职责分明。

## 三、外部连接（图谱边证据）

router.tsx 的 imports 边连 inspect/layout/openapi/welcome/paths 与 client.ts，唯一入边来自 providers.tsx（应用装配点）。client.ts 是全图入度最高的前端节点之一：fetch-sse、stream-connection-provider、dataset 上传/预览、feedback 等十余文件 import 它——改基地址策略只动这 44 行。stream-connection-provider 入边覆盖 stream-container、stream.component、footer 状态栏与 5 个测试，是跨特性域共享状态。与后端对应：`/api/jobs:train`、`/api/trainable-models`、`/api/projects/{id}/pipeline`、`/api/stream` 一一成对。

## 四、数据流

三条流：①训练命令流：TrainModelDialog mutation → POST /api/jobs:train → invalidates 触发 jobs 重查 → Models 视图伪 ModelData 出现并刷新 progress → 完成后 useCompletedModels 出真模型、伪行消失（L61-64 差集）。②实时流：TogglePipelineButton → pipeline:run → onSuccess 触发 start → streamUrl 就绪 → `<img>` 建 MJPEG 长连接 → Fps 查帧率。③直通流：pipeline 未配模型时后端直接转发原图（09 篇 L72-75），前端无感。缓存失效全部经 `meta.invalidates` 声明式完成，无手写 refetch。

## 五、设计决策

1. **schema-first**：类型由后端 OpenAPI 生成，端点改名编译期报错；后端还有 create_openapi.py 专门导出 schema。
2. **双运行时一份产物**：isTauri() 运行时探测而非双构建，Docker 与桌面共用 bundle（client.ts L7-10 注释是设计说明书）。
3. **视频流用 MJPEG 而非 WebSocket/WebRTC**：`<img>` 原生 multipart 解码零依赖，代价单向无回传；被禁用的后端 WebRTC（09 篇）本是升级路线。
4. **状态机外置**：五态收敛在 Provider，StreamContainer 只做分流，重连时序坑（stop→300ms→start）集中一处消化。
5. **URL 即全局状态**：mode 查询参数承担页签，训练完成 setSearchParams 跳 Models（L57-58），刷新/分享可恢复现场。

## 六、新人提示（含勘误）

- **文档漂移**：provider 五态含 `'failed'`，但 provider 自身无任何代码置 failed——它只能由 `<Stream>` 的 img onerror 回调 setStatus 写入；在 provider 找 failed 来源会扑空，去 stream.component.tsx 找。
- **图谱口径勘误**：图谱摘要称 train-model-dialog"成功 toast、自动开播"——实际 L54-58 只 dismiss toast 并切 mode=Models；"自动开播"是 stream-container 的 onSuccess 行为，不在对话框内。
- toolbar 特性域 74 文件，toolbar.tsx 本身仅 49 行是装配层；tour T13 的"toolbar 流水线开关"指整域。
- MJPEG `<img>` 在 React 严格模式下双挂载，`key={streamUrl}` + 时间戳参数防重连风暴，勿删。
- `@anomalib-studio/api`/`hooks` 是 rsbuild 包别名不是 npm 依赖，grep import 时注意。
- 新页面：features/inspect 下建域目录 + main-content 的 mode 分发处注册，路由层通常不用动。

---
**自检**：总字符（不含换行）4682 / 去空格字符 4398；行号锚 38 个（router.tsx×5、client.ts×4、train-model-dialog×6、models-view×7、dataset×2、stream-container×6、provider×4、stream.component×3、fetch-sse×4，均经源文件核实；另补 file:line 路径锚 8 处——router.tsx:18、client.ts:12、train-model-dialog.component.tsx:28、models-view.component.tsx:52、dataset.component.tsx:12、stream-container.tsx:14、stream-connection-provider.tsx:5、fetch-sse.ts:4，均 grep -n 实证）。
