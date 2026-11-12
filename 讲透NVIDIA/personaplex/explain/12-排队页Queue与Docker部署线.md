# 12 · 排队页 Queue、api/ 排队客户端残骸与 Docker 部署线

## ① 角色定位

`Queue.tsx`（216 行）是应用**唯一路由页**（`app.tsx:11-12`）：一个 Homepage↔Conversation 双态机，承担新人旅程全部准备工作——文本/音色人格选择、麦克风授权探测、AudioContext 与 AudioWorklet 初始化、解码 worker 预热。`api/` 子树（client.ts/validators.ts/errors/）是一套**完整的排队后端客户端**（入队/轮询/反馈），但当前全为死代码；`useUserEmail`/`useLocalStorage`/`Input.tsx` 同属外围。部署线：根 Dockerfile + docker-compose 单 GPU 容器跑 moshi 服务端，前端产物从 HF hub 分发。

## ② 内部结构

**Queue.tsx**。`Queue.tsx:1` 以 `?worker&url` 导入 audio-processor 的 worklet URL；L3 引 eruda；`VOICE_OPTIONS`（L11-16）18 音色四组（NAT F0-3/M0-3、VAR F0-4/M0-4）；`TEXT_PROMPT_PRESETS`（L18-35）四个人格预设——Assistant 教师、Medical office 医疗问诊、Bank 银行拒付核身、Astronaut 火星反应堆（PersonaPlex 客服/人格演练场景的直接证据）。

- **Homepage 内嵌组件**（L46-126）：预设 chips 一键填 prompt（L71-79）；textarea maxLength 1000 + 计数（L82-93）；音色下拉把 NAT/VAR 前缀显示为 NATURAL_/VARIETY_ 别名（L107-114）；麦克风未授权红字提示（L118-120）；Connect 按钮触发 startConnection（L122）。
- **Queue 主体**（L128-216）：`theme` 硬编码 "light"（L129，放弃 useSystemTheme 深色支持）；`?worker_addr=` 查询参数可直连指定 worker（L131，绕排队的正门）；eruda 仅 dev 启用（L140-149）；`getMicrophoneAccess`（L151-162）裸 `getUserMedia({audio:true})` 探测授权并置 `hasMicrophoneAccess`；`startProcessor`（L164-183）——AudioContext 惰性创建（L166）、**立刻预热解码 worker**（L169，注释明言"给 WASM 在用户授权期间加载的时间"）、worklet 已存在即幂等返回（L171-173）、`new AudioWorkletNode` 失败则 `addModule` 后重试（L177-181）、connect(destination)（L182）；`startConnection`（L185-191）串起两者；渲染条件 `hasMicrophoneAccess && audioContext.current && worklet.current`（L195）成立才切 Conversation（L196-203，`{...modelParams}` 全量 + 两个音频 ref 注入）。

**api/ 排队客户端（死代码）**。`client.ts:5-67` 的 `getAPIClient(url)` 工厂三方法：`addUser`（L6-21，`GET /add_user?queue_id=` 返回 session_id/session_auth_id）；`checkUser`（L22-37，`GET /check_user?session_id=&session_auth_id=` 轮询，zod 校验 `status: 'wait'|'ready'` 与 worker_addr——`validators.ts:15`）；`addFeedback`（L38-66，`/user_feedback` 六个参数全拼查询串）。两级错误：`APIError` 携带 HTTP status（`api_error.ts:1-9`），`ResponseError` 表示响应体过不了 zod（`response_error.ts:1-6`）。`useUserEmail.ts`：zod email 校验（L4）、`isBypass` 短路（L11-14）、validate 置错（L10-22）。

**useLocalStorage.ts（唯一活的外围 hook）**。`useState` 惰性初始化读 localStorage + JSON.parse（L4-12），`useEffect` 持久化（L14-20），`as const` 元组返回（L22）。全仓唯一消费者是 `useModelParams.ts:41` 的 randomSeed。

**部署线**。根 `Dockerfile`：`nvcr.io/nvidia/cuda:12.4.1-runtime-ubuntu22.04` 基底（L1-2）；拷 uv（L6）；装 build-essential + **libopus-dev**（L8-12，Opus 编解码的系统依赖）；`uv venv` + `uv sync`（L17-18）；EXPOSE 8998（L22）；CMD 起 `moshi.server --ssl /app/ssl`（L25）。`docker-compose.yaml`：映射 8998（L7）、`NO_TORCH_COMPILE=1` 环境变量（L9，跳过 torch.compile 换启动速度）、GPU 预留一块（L12-18）、`.cache` 卷持久化模型权重（L19-20）。UI 供给：`server.py:344` 默认从 HF hub `nvidia/personaplex-7b/v1` 拉 `dist.tgz`（L341-350 解包），`--static` 可指本地。

## ③ 外部连接

`.env.local:1-2` 定义 `VITE_QUEUE_API_PATH=/api` 与 `VITE_QUEUE_API_URL=https://moshi.chat`——dev 期 `/api` 代理指向 Kyutai 官方排队服务；生产浏览器直连 8998 的 moshi 服务端。client README 记载 `/?worker_addr={HOST:PORT}` 单机直连姿势（与 L131 对应）。排队的三个端点（add_user/check_user/user_feedback）在本仓**没有服务端实现**（moshi/server.py 仅注册 `/api/chat`，L460），属于外部排队服务的客户端残骸。

## ④ 数据流

现行流（无排队）：Homepage Connect → startProcessor（音频基建 + WASM 预热）→ getUserMedia 授权 → setState 触发重渲染 → 条件成立切 Conversation。设计意图的排队流（读死代码还原）：addUser 换 session 双 id → 定时 checkUser 轮询 → `wait` 显示排队位次（current_position）→ `ready` 时拿 worker_addr/worker_auth_id → 携 id 建 WS → 会话结束 addFeedback 评价。两条 id（session_auth_id 防顶替、worker_auth_id 防白嫖）在 buildURL（`Conversation.tsx:57-59`）仍有接入口，说明拆掉排队时只删了轮询壳。

## ⑤ 设计决策

- **预热前置到首页点击**（L167-169 注释）：把 WASM 下载与浏览器授权弹窗的等待时间重叠，是全链路首帧延迟最划算的优化。
- **音频基建 refs 由 Queue 持有**：跨 Homepage↔Conversation 切换存活，且天然规避"AudioContext 必须在用户手势中创建"的限制（Connect 点击即手势）。
- **worker_addr URL 参数即部署拓扑开关**：同一前端既可以排队多 worker，也可以 `?worker_addr=` 单机直连——demo 与生产共用一份代码。
- 排队客户端按"工厂 + zod + 两级错误类"的完整形态写好再弃用，保留了随时接回外部排队服务的能力。

## ⑥ 新人提示（坑与勘误）

- **Queue useEffect 死清理（钉版勘误）**：L140-149 的 eruda 效果里，L144-148 的清理函数是**裸箭头函数表达式语句**（`() => {...}` 没有返回）——`eruda.destroy()` 永远不会执行，卸载后控制台 DOM 残留。应写 `return () => {...}`。
- **startConnection 空分支**：`if (hasAccess) { // 值已在 modelParams }`（L188-190）是纯注释空体——真正的门控在渲染条件 L195，读代码时别在这里找逻辑。
- **api/ 三文件 + useUserEmail + Input.tsx 全部死代码**：grep 实证零导入。`Input.tsx:9` 还有一处 className 双 `p-2` 冗余（死代码里的死细节）。二次开发要么删掉要么接回，别在死 UI 上加功能。
- **useUserEmail 的 useCallback 依赖缺 isBypass**（L22 只列 setError）：isBypass 变化后 validate 闭包陈旧——当前无调用方所以无症状，复用前先补。
- **client/Dockerfile 与根部署线是两套**：client 镜像 CMD 是 `npm run dev`（`client/Dockerfile:21`），根 compose 只跑 moshi 服务端、UI 走 HF dist.tgz——见 07 篇，别把 client 镜像当生产前端。
- docker-compose 的 `.env` 文件（L10-11）不在仓库，直接 `docker compose up` 会因缺文件失败，需按 README 先建。
