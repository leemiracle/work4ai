# batch-024 semantic data (pi-ai types tail, llm-retry, plugin-package-inventory-deepseek, token-meter)
BATCH = {
 'files': {
  'packages/llm/llm-pi-ai/src/types.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': 'pi-ai 传输头贡献者可见的请求元数据类型：PiAiRequestHeaderContext 从精确准备的适配器调用暴露 provider/model/sessionId/purpose 与解析端点（模型隐藏的路由元数据）。',
   'tags': ['type-definition', 'request-metadata']},
  'packages/llm/llm-pi-ai/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-llm-pi-ai 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/llm/llm-retry/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-llm-retry 包参考：在 agent 循环的请求恢复扩展点上执行 provider 路由的模型请求重试策略——普通有界与 always 无界两种模式、指数退避+jitter、每次调度在可取消等待前持久化。',
   'tags': ['documentation', 'package-reference', 'retry']},
  'packages/llm/llm-retry/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-llm-retry 包清单：LLM 请求重试插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/llm/llm-retry/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '重试策略执行器（name=llm-retry，inject=agents+sessionProjections）：消费 RequestErrorAction 恢复点，按 provider 注册的 retryPolicy（always 无界或 retryableCodes 有界）计算指数退避+jitter 延迟，可取消等待后再提交决策；重试状态经投影持久化。',
   'tags': ['retry', 'plugin', 'backoff', 'durable-state'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 120, 'end': 257,
     'summary': '安装 provider 路由的请求恢复：激活期接纳的恢复等待投影注册就绪，注册失败传播，取消/销毁抑制后续重试；策略与状态键由 provider+policy 派生。',
     'tags': ['plugin-entry', 'apply', 'recovery', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'cancellableDelay', 'start': 83, 'end': 96,
     'summary': '可中止的退避等待：AbortSignal 触发即提前返回 false，重试调度在等待前已持久化。',
     'tags': ['delay', 'cancellation'], 'complexity': 'moderate'}]},
  'packages/llm/llm-retry/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-llm-retry 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/llm/llm-retry/tsdown.config.ts': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-llm-retry 的 tsdown 打包配置：把包根构建为自包含 ESM bundle。',
   'tags': ['configuration', 'tsdown', 'build-system']},
  'packages/llm/plugin-package-inventory-deepseek/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-plugin-package-inventory-deepseek 包参考：把活跃插件包清单（名称+版本）作为 dsh_plugin_packages 顶层字段贡献到官方 DeepSeek 请求，供提供方侧生态统计。',
   'tags': ['documentation', 'package-reference', 'inventory']},
  'packages/llm/plugin-package-inventory-deepseek/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-plugin-package-inventory-deepseek 包清单：请求扩展型清单插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/llm/plugin-package-inventory-deepseek/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '清单插件实现：PackageIdentityResolver 以每进程不可变缓存解析 Loader 活跃条目的所属包（裸包名查 manifest/最近 package.json），按会话叠加 agent preset 组合模块，经 deepseekLlmApiExtensions 注册 dsh_plugin_packages 字段；不可读身份只告警一次并省略。',
   'tags': ['plugin', 'inventory', 'request-extensions', 'loader'],
   'members': [
    {'kind': 'class', 'name': 'PackageIdentityResolver', 'start': 100, 'end': 134,
     'summary': '精确包身份解析器：按锚点 URL 集合缓存 manifest 解析结果，裸包名必达（失败抛错），cordis: 前缀与散模块回退最近 package.json。',
     'tags': ['resolver', 'manifest', 'cache'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'collectActivePluginPackages', 'start': 154, 'end': 192,
     'summary': '收集一次请求的活跃包身份：Loader 活跃条目+会话 preset 组合模块，去重后按确定性文本序（无 ICU/locale 依赖）排序。',
     'tags': ['collection', 'deterministic-order'], 'complexity': 'complex'},
    {'kind': 'function', 'name': 'apply', 'start': 199, 'end': 214,
     'summary': '插件 apply：enabled 默认开，构造解析器并向请求扩展注册表认领 dsh_plugin_packages 字段（prepare 返回版本化清单）。',
     'tags': ['plugin-entry', 'apply', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/plugin-package-inventory-deepseek/src/types.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '清单类型：DeepSeekPluginPackageIdentity（name/version）与 dsh_plugin_packages 扩展载荷结构。',
   'tags': ['type-definition', 'inventory']},
  'packages/llm/plugin-package-inventory-deepseek/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-plugin-package-inventory-deepseek 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/llm/token-meter/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-token-meter 包参考：回放感知的请求与表面压力计量服务——固定密度启发式定价、会话投影的用量/占用/分解折叠、路由图像定价与每 turn 精确用量聚合。',
   'tags': ['documentation', 'package-reference', 'token-meter', 'projections']},
  'packages/llm/token-meter/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-token-meter 包清单：token 计量服务。',
   'tags': ['configuration', 'package-manifest']},
  'packages/llm/token-meter/src/breakdown-projection.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '当前保留表面的启发式组成投影（与路由图像定价和提供方用量独立）：状态只保留按序存活的系统提示与一个滚动表面总量，其余节点只按增量计价——状态规模跟随系统提示而非消息数。',
   'tags': ['projection', 'breakdown', 'session-projection'],
   'members': [
    {'kind': 'function', 'name': 'placeSurfaceEvent', 'start': 73, 'end': 115,
     'summary': '把一个表面事件放置到组成状态：新增/替换/删除节点时维护系统提示序与滚动总量。',
     'tags': ['projection', 'events'], 'complexity': 'complex'}]},
  'packages/llm/token-meter/src/estimate.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '固定密度启发式 token 定价（CHARS_PER_TOKEN=4+块结构开销 4）：计量服务与纯上下文分解投影共用，保证两个表面把相同内容计成相同数字。',
   'tags': ['estimation', 'heuristics', 'shared'],
   'members': [
    {'kind': 'function', 'name': 'estimateContent', 'start': 42, 'end': 63,
     'summary': '按内容块类型（文本/推理/图像/文件/工具调用）估算 token 数。',
     'tags': ['estimation', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/token-meter/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '单一回放感知 token 计量服务入口：TokenMeter（ctx.tokenMeter，inject=sessionProjections）注册测量/用量/上下文压力/上下文分解四个会话投影，每会话隔离折叠（WeakMap 状态），不支持任何设置键（写死配置即失败）。',
   'tags': ['entry-point', 'service-definition', 'projections', 'token-meter'],
   'members': [
    {'kind': 'class', 'name': 'TokenMeter', 'start': 87, 'end': 294,
     'summary': 'ctx.tokenMeter 的 Cordis Service Definition：Service.init 时注册四个投影并急切观察限界；对外提供按会话的测量/用量/压力读取与测量快照重建。',
     'tags': ['service-definition', 'cordis', 'projections', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/token-meter/src/measurement-projection.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '固定大小恢复事实投影：从会话事件重建测量状态（每保留节点的身份/启发式价/路由定价要替换的附件明细），位置附件价保持为可重建缓存。',
   'tags': ['projection', 'measurement', 'recovery'],
   'members': [
    {'kind': 'function', 'name': 'advanceMeasurement', 'start': 44, 'end': 82,
     'summary': '把一个会话事件折叠进测量状态（含 zod 校验的用量恢复与助手流组装）。',
     'tags': ['projection', 'fold', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/token-meter/src/projection.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '纯 client 安全的 token 投影词汇：TokenUsageProjection（四桶不相交累积用量，reasoning 已含在 outputTokens）与 ContextPressureProjection。',
   'tags': ['type-definition', 'projections', 'client-safe']},
  'packages/llm/token-meter/src/route-pricing.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '请求投影的表面路由定价：把附件块启发式替换为发送到路由模型的真实图像/文件表示计价（priceSurface）。',
   'tags': ['pricing', 'route', 'images'],
   'members': [
    {'kind': 'function', 'name': 'priceSurface', 'start': 32, 'end': 76,
     'summary': '为一条请求路由计价整个表面：公开节点+总量，附件出现按路由表示替换启发式价格。',
     'tags': ['pricing', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/token-meter/src/surface-fold.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '测量用的位置定价折叠（plan/commit 对）：planSurfaceTokens 只读跑全部可失败步骤，commitSurfaceTokens 原地变更——抛错不碰调用方状态且同一坏事件每次重试同样失败；节点携带持久附件出现与结构价。',
   'tags': ['fold', 'plan-commit', 'pricing'],
   'members': [
    {'kind': 'function', 'name': 'planSurfaceTokens', 'start': 107, 'end': 128,
     'summary': '只读规划一次表面 token 折叠：逐事件解析附件与节点价，可失败步骤不落状态。',
     'tags': ['fold', 'read-only', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'analyzeNode', 'start': 73, 'end': 96,
     'summary': '分析单个表面节点：身份、启发式价与路由定价所需的附件明细。',
     'tags': ['analysis', 'nodes'], 'complexity': 'moderate'}]},
  'packages/llm/token-meter/src/surface-projection.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '上下文压力投影的 O(1) 表面 token 折叠：检查点只存标量总量，替换走 compact seam 的影子价协议（替换事件前一个计量事件声明被换区间的启发式价）——无 armed claim 的替换按零增量折叠，保回放代价是可能漂移。',
   'tags': ['projection', 'o1-fold', 'shadow-price'],
   'members': [
    {'kind': 'function', 'name': 'foldSurfaceProjection', 'start': 64, 'end': 96,
     'summary': '把表面事件折叠进标量压力状态：追加按固定估计器计价、替换消费至多一个 pending claim。',
     'tags': ['fold', 'projection', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/token-meter/src/turn-usage.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '单 turn 精确用量核算：deriveTurnTokenUsage 聚合一个完成 Turn 内每次计费请求尝试的 provider 报告用量（未缓存输入/输出/缓存读写四桶+按路由分组），配额从助手流最后块恢复。',
   'tags': ['usage', 'aggregation', 'turn'],
   'members': [
    {'kind': 'function', 'name': 'deriveTurnTokenUsage', 'start': 178, 'end': 274,
     'summary': '从会话事件推导一个 Turn 的精确用量：识别尝试边界、归一化各提供方用量、聚合四桶与路由明细。',
     'tags': ['aggregation', 'usage', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'aggregateAttempts', 'start': 126, 'end': 159,
     'summary': '把多次尝试的归一化用量聚合为 turn 总量（同尝试去重）。',
     'tags': ['aggregation'], 'complexity': 'moderate'}]},
  'packages/llm/token-meter/src/usage-projection.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '持久提供方用量与上下文占用的纯折叠：tokenUsage/contextPressure 两个 ProjectionDefinition（zod 校验恢复），从助手流末块提取每事件用量，压力状态复用 foldSurfaceProjection。',
   'tags': ['projection', 'pure-fold', 'usage'],
   'members': [
    {'kind': 'function', 'name': 'addReplacing', 'start': 34, 'end': 43,
     'summary': '按序号替换式累加用量桶（同键旧值被新快照替换而非叠加）。',
     'tags': ['fold', 'buckets'], 'complexity': 'simple'}]},
  'packages/llm/token-meter/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-token-meter 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
 },
 'extra_edges': [
  {'source': 'function:packages/llm/plugin-package-inventory-deepseek/src/index.ts:apply', 'target': 'class:packages/llm/deepseek-llm-api-extensions/src/index.ts:DeepSeekLlmApiExtensionRegistry', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/token-meter/src/breakdown-projection.ts:placeSurfaceEvent', 'target': 'function:packages/llm/token-meter/src/estimate.ts:estimateContent', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/llm/token-meter/src/index.ts:TokenMeter', 'target': 'function:packages/llm/token-meter/src/measurement-projection.ts:advanceMeasurement', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/llm/token-meter/src/index.ts:TokenMeter', 'target': 'function:packages/llm/token-meter/src/surface-fold.ts:planSurfaceTokens', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/token-meter/src/usage-projection.ts:addReplacing', 'target': 'function:packages/llm/token-meter/src/surface-projection.ts:foldSurfaceProjection', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
