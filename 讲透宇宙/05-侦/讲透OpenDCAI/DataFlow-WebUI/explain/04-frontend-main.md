# 04 · Vue3 前端主链：main / router / stores / openapijs 生成层

## 角色定位

`frontend/src/` 的主链四件套——`main.js`（应用装配）、`router/`（hash 路由 + 动态懒加载）、`stores/`（三个 Pinia store）、`axios/`（openapijs 从后端 OpenAPI schema 生成的 API 层）——构成单页应用的骨架。前端是纯消费者：所有数据经生成层打后端 `/api/v1`，自身只有 i18n/主题/屏幕宽度三类本地状态。技术栈是 Vue 3.4（package.json:29）+ Options API 为主体 + Pinia + vue-router + Vue Flow 画布 + vfluent3/PowerEditor 两个内部组件库。

## 内部结构

`main.js:15-43` 装配链一读即懂：createApp → VueFluent（L16）→ PowerEditor（L18）→ Pinia（L20）→ router（L21）→ 四个全局属性 `$Go/$Back/$Jump/$Guid`（L23-39，路由跳转/回退/开新窗/短 guid）→ `apiPlugin`（L41，把 `$api`/`$axios` 挂上全局）→ mount。`App.vue` 只做三件初始化（L25-29）：`getConfig` 拉偏好（L40 调生成方法 `get_preferences_api_v1_preferences__get`，L41 判 `res.code === 200` 恢复语言/主题）、`i18nInit` 注入字典、`timerInit` 每 300ms 轮询 `screenWidth`（L56-58，响应式布局的土办法）。路由：`router/index.js:10` 用 `createWebHashHistory`（hash 模式，天然免服务端 fallback）；`Manage/index.js` 定义 `/m` 命名空间——L7 壳层 + 8 个子路由（''/serving/dm/prompts/schemas/dataviz/settings/analysis），全部经 `tools.js:4-17` 的 `AsyncLoad`（defineAsyncComponent + loading 组件 + 10s 超时）动态懒加载，共 9 个 chunk。stores 三件：`appConfig.js` 持 screenWidth/language/i18n 字典，`local()`（L22-30）是全站翻译函数——查字典命中返回对应语言、未命中返回原文；`dataflow.js`（326 行）是业务大本营，`getOperators`（L73-119）拉算子后按 `operatorStyleDict`（L15+，每类算子的图标/配色）组装并按 level_1 分组；`theme.js` 用 onecolor 派生渐变色系。

## 外部连接

`axios/api.js`（3188 行）是 openapijs（minskiter 生成器，文件头 L2 注明）从后端 OpenAPI 生成的 10 个域类：datasets（L11）/operators（L609）/tasks（L792）/pipelines（L1330）/prompts（L1688）/serving（L1986）/text2sql_database（L2406）/text2sql_database_manager（L2646）/preferences（L3004）/common（L3126），每个方法静态函数、URL 硬编码 `/api/v1/...`、统一处理 cancelToken/进度回调/blob。`axios/model.js`（2075 行）70 个导出类 = 31 个 `ApiResponse_*` 泛型包装（L1 起机械平铺五字段）+ 39 个领域 schema（DatasetIn/PipelineConfig/OperatorDetailSchema 等，含 Body_* 上传样板）——全为生成物，手写豁免。`axios/config.js:8-12`：生产模式 baseURL 取 `VITE_BACKEND_URL`，开发留空走 vite dev proxy；L14-31 请求拦截器把表单数据归一成 FormData。

## 数据流

启动流：main.js 装配 → App.vue mounted → 拉偏好恢复语言主题 → router 进 `/m`（home 跳板见 05 篇）→ 懒加载 dataflow 视图 → 视图经 mapActions 调 store → store 经 `proxy.$api.<域>.<方法>` 发请求 → 生成层 axios → 后端信封 → `res.code===200` 分支消费。屏幕宽度流：App.vue 300ms 轮询 → appConfig.setScreenWidth → 各组件 mapState 响应式布局。

## 设计决策（含批判）

- **生成层手写豁免但无门禁**：api.js/model.js 与后端 schema 的同步全靠手动重跑 openapijs，没有 skills 体系那样的 `--check` 漂移检测（对照 06 篇）——后端加端点后前端静默缺方法，只能在调用处报 undefined。文件头也没有 GENERATED banner 提示勿手编。
- **勘误·App.vue 双钩子名并存**：`App.vue:66` 用的是 Vue 2 的 `beforeDestroy`，而仓里其余 6 处组件（dataflow/index.vue:398、chatPanel:285 等）都用 Vue 3 的 `beforeUnmount`；项目无 @vue/compat，Vue 3 不会调用 beforeDestroy——App.vue 的 clearTimer 在卸载时实际不执行。幸运的是根组件永不卸载，无实害，但这是从 Vue 2 模板迁移的活化石，照抄它写新组件就会真踩坑。
- **判 200 而非判 success**：全站 `res.code === 200` 的成功判定依赖 `resp.ok()` 填 200 的实现细节（见 01 篇契约漂移），`success` 布尔字段反而无人使用。
- **Options API + Pinia 混搭**：mapActions/mapState（pinia 版）在 Options 组件里工作正常但属冷门用法，组合式 store（`defineStore(() => {...})`）与 Options 组件并存，新人容易迷路；300ms setInterval 轮询宽度也该换成 resize 监听。
- **hash 路由的取舍**：免去服务端 SPA fallback 配置（后端 main.py 的 `/ui` 兜底因此无关紧要），代价是 URL 带 `#`、SEO 不友好——对本地工具是正确取舍。

## 新人提示

加新页面：views/manage 下建目录 → Manage/index.js 加子路由（照抄懒加载写法）→ manage/index.vue 的 navList 加侧边项。调后端新端点：先重跑 openapijs 再在 store 里加方法，别手改 api.js。翻译用 `this.local('...')`（英文原文做 key），新词条要跑 translator.py（见 05 篇）进字典。生命周期钩子一律写 `beforeUnmount`，别抄 App.vue。
