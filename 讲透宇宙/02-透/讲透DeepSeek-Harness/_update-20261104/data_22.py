# batch-022 semantic data (llm-deepseek part 2: transport, files, listing, replay)
BATCH = {
 'files': {
  'packages/llm/llm-deepseek/src/file-store.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'DeepSeek Files API 上传复用、失效与配额恢复：DeepSeekFileStore 按（端点+认证头哈希）隔离上传复用，管理文件过期/主动刷新窗口/配额清理批量，上传等待可中止。',
   'tags': ['files', 'upload-reuse', 'quota', 'deepseek'],
   'members': [
    {'kind': 'class', 'name': 'DeepSeekFileStore', 'start': 121, 'end': 336,
     'summary': '共享 Files 存储门面：对每个请求图像执行上传复用（32MiB 上限）、陈旧 file-id 恢复与配额超限时的批量清理重试，原生凭据不落盘。',
     'tags': ['file-store', 'upload-reuse', 'recovery'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'waitForUpload', 'start': 69, 'end': 103,
     'summary': '并发上传的去重等待：同一附件的上传只执行一次，后来者等待既有 promise 并在中止时给出确定性行为。',
     'tags': ['concurrency', 'dedup', 'upload'], 'complexity': 'moderate'}]},
  'packages/llm/llm-deepseek/src/files-api.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'DeepSeek Files API 传输层：DeepSeekFilesClient 封装 list/upload/retrieve 的 HTTP 调用与文件对象校验（大小 128MiB 上限、数量 1 万、存储 25GiB 配额常量），配额错误可被 isFilesQuotaError 识别。',
   'tags': ['files', 'http-client', 'quota', 'deepseek'],
   'members': [
    {'kind': 'class', 'name': 'DeepSeekFilesError', 'start': 39, 'end': 59,
     'summary': 'Files API 专用错误（继承 LlmError）：携带配额标志与提供方细节，供上层区分可恢复配额超限。',
     'tags': ['error-handling', 'files', 'exported'], 'complexity': 'simple', 'exported': True},
    {'kind': 'class', 'name': 'DeepSeekFilesClient', 'start': 131, 'end': 262,
     'summary': 'Files API HTTP 客户端：统一认证头与归因头，解析响应 JSON 并校验文件对象结构，错误归一为 DeepSeekFilesError。',
     'tags': ['http-client', 'files', 'validation'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'parseFileObject', 'start': 95, 'end': 114,
     'summary': '校验并解析提供方文件元数据（id/bytes/createdAt/filename/expiresAt）为 DeepSeekFileObject。',
     'tags': ['validation', 'parsing'], 'complexity': 'moderate'}]},
  'packages/llm/llm-deepseek/src/host.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'DeepSeek 协议适配器的共享 Host 接线：registerDeepSeekProvider 组合适配器+模型目录缓存注册一条路由，createModelListingCache 拥有目录刷新、stderr 诊断与目录变更通知的生命周期。',
   'tags': ['host-wiring', 'provider-registration', 'listing'],
   'members': [
    {'kind': 'function', 'name': 'createModelListingCache', 'start': 21, 'end': 36,
     'summary': '为一条路由创建 ModelListingCache 并接管目录刷新调度与诊断日志，随 provider 生命周期销毁。',
     'tags': ['factory', 'listing-cache', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'registerDeepSeekProvider', 'start': 44, 'end': 91,
     'summary': '在 ctx.llm 注册一条 DeepSeek 路由：组装 DeepSeekAdapter 依赖（凭据/设置/图像访问解析）并挂接目录缓存与目录变更事件。',
     'tags': ['registration', 'provider', 'cordis', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-deepseek/src/image-tokens.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'DeepSeek 视觉 token 计算器（v41 配置逐字移植）：小于 544×544 的图放缩上去、14px patch 网格对齐、3:1 降采样为 token 格、单图 1024 token 上限内解最大保持纵横比网格；计数精确无对齐填充。',
   'tags': ['vision-tokens', 'calculator', 'deepseek'],
   'members': [
    {'kind': 'function', 'name': 'solveResizeRatio', 'start': 49, 'end': 75,
     'summary': '在 1024 token 预算内解出最大保持纵横比的放缩比例，token 网格求解的核心。',
     'tags': ['solver', 'aspect-ratio', 'tokens'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'deepSeekRequestImageTokens', 'start': 147, 'end': 157,
     'summary': '按提供方公布的算法计算一张请求图像的精确视觉 token 数（实际用量仍以提供方为准）。',
     'tags': ['tokens', 'images', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/llm/llm-deepseek/src/images.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'Messages 图像确定性准备：prepareImages 投影历史并按模型读取归一化图像请求版本（要求视觉模型+附件服务，图像仅允许 user/tool 消息），inlineImages 强制超预算图像先记录 offload，prepareFileIds 输出文件引用。',
   'tags': ['images', 'preparation', 'files', 'deepseek'],
   'members': [
    {'kind': 'function', 'name': 'prepareImages', 'start': 38, 'end': 61,
     'summary': '主图像准备管线：offload 投影→视觉模型与消息角色校验→按附件 id 读取归一化请求版本→原始表示边界断言。',
     'tags': ['images', 'pipeline', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'inlineImages', 'start': 69, 'end': 75,
     'summary': '内联回退前的边界检查：超出内联预算的图像必须先走记录 offload 再重试。',
     'tags': ['images', 'inline', 'exported'], 'complexity': 'simple', 'exported': True},
    {'kind': 'function', 'name': 'prepareFileIds', 'start': 99, 'end': 111,
     'summary': '把准备好的图像版本转换为 Files API 的 file-id 引用表示。',
     'tags': ['images', 'file-ids', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/llm/llm-deepseek/src/index.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': 'dsh-llm-deepseek 包入口 barrel：统一再导出凭据解析、配置解析、默认值、适配器、图像 token、文件存储/上传索引、目录与定价等全部公共面。',
   'tags': ['entry-point', 'barrel', 'exports']},
  'packages/llm/llm-deepseek/src/listed-catalog.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '已列目录的解析：版本门控（semver 对照 build 支持范围）、本 build 的模型知识与部署覆盖三层合并；网络 I/O 之前即可拒绝不支持的已列模型并给出原因。',
   'tags': ['catalog', 'version-gating', 'models'],
   'members': [
    {'kind': 'function', 'name': 'resolveListedCatalog', 'start': 103, 'end': 164,
     'summary': '把 GET /models 列表解析为已列目录：逐条门控+覆盖合并+拒绝原因标注，产出可展示的目录事实。',
     'tags': ['catalog', 'resolution', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'refuseListedModel', 'start': 172, 'end': 186,
     'summary': '为一条被拒模型生成带原因的目录拒绝（供 GUI 与诊断展示）。',
     'tags': ['refusal', 'catalog', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek/src/listing-cache.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '凭据作用域的 /models 缓存：单飞加载、后台自动刷新、最后已知良好保留；缓存键含认证头哈希，凭据轮换自然失效。',
   'tags': ['cache', 'single-flight', 'listing', 'credentials'],
   'members': [
    {'kind': 'class', 'name': 'ModelListingCache', 'start': 49, 'end': 202,
     'summary': '凭据作用域模型目录缓存：settings 引用驱动自动跟随刷新，刷新失败保留最后已知良好值，活跃工作完成后再销毁。',
     'tags': ['cache', 'background-refresh', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-deepseek/src/listing-config.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '目录刷新时序配置：schemastery 声明的 TTL/超时字段与 resolveListingTiming 解析（含计时器上限钳制）。',
   'tags': ['configuration', 'schemastery', 'timing'],
   'members': [
    {'kind': 'function', 'name': 'resolveListingTiming', 'start': 55, 'end': 64,
     'summary': '把目录刷新配置解析为可用的时序参数（TTL、超时、刷新余量）。',
     'tags': ['resolution', 'timing', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/llm/llm-deepseek/src/listing.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'DeepSeek GET /models 列表：一次带认证与归因头的请求 + 逐条解码（模态、能力、badge 文本按字素与不可见字符校验、最长 12 字符限制、本地化翻译校验）。',
   'tags': ['listing', 'http', 'validation', 'badges'],
   'members': [
    {'kind': 'function', 'name': 'badgeOf', 'start': 150, 'end': 170,
     'summary': '校验并规范化单条目录 badge（文本、tone、本地化表），不可读字符直接拒绝。',
     'tags': ['badges', 'validation', 'localization'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'capabilitiesOf', 'start': 172, 'end': 199,
     'summary': '把目录条目的原始能力字段解码为 harness 的模型能力结构。',
     'tags': ['capabilities', 'decoding'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'parseModelListing', 'start': 207, 'end': 229,
     'summary': '整体校验 /models 响应结构并逐条解析为 ModelListing（坏条目带定位失败）。',
     'tags': ['validation', 'parsing', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'requestModelListing', 'start': 241, 'end': 269,
     'summary': '执行一次带认证与归因头的 /models 请求并解析，超时由 timeoutOf 控制。',
     'tags': ['http', 'listing', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek/src/messages-api.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '共享 Messages API 端点与头策略：messagesApiRoot 去重显式版本路径，MESSAGES_FILES_BETA / MESSAGES_TOOL_CHANGES_BETA 两个 opt-in beta 头常量。',
   'tags': ['endpoints', 'beta-headers', 'constants']},
  'packages/llm/llm-deepseek/src/model-info.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '协议无关的模型能力与推理力度选择：off/low/high/max 四档推理力度元数据，modelInfo 把目录模型+连接选项解析为 LlmResolvedModelInfo。',
   'tags': ['model-info', 'reasoning-effort', 'resolution'],
   'members': [
    {'kind': 'function', 'name': 'modelInfo', 'start': 63, 'end': 102,
     'summary': '把 DeepSeekCatalogModel 与连接选项解析为 harness 的 LlmResolvedModelInfo（上下文窗口、输出上限、模态、推理力度集合）。',
     'tags': ['resolution', 'model-info', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek/src/models.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '默认 DeepSeek 模型目录：deepseek-flash（V4.1-Flash）与 deepseek-chat（V4 Pro）两条咨询条目，上下文 1,048,576，text+image 输入，部署可整体替换。',
   'tags': ['models', 'catalog', 'constants']},
  'packages/llm/llm-deepseek/src/replay.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '原生 thinking 回放的极小元数据：ReplayBlock（text/reasoning/tool-call 的 signature 对齐索引）+ envelope 构造与读取校验；持久 harness 块拥有全部响应文本。',
   'tags': ['replay', 'metadata', 'validation'],
   'members': [
    {'kind': 'function', 'name': 'readReplay', 'start': 39, 'end': 46,
     'summary': '读取并校验原生回放元数据：外来/跨模型/降级历史返回 undefined 并回调诊断原因。',
     'tags': ['replay', 'validation', 'exported'], 'complexity': 'simple', 'exported': True},
    {'kind': 'function', 'name': 'validateReplay', 'start': 48, 'end': 64,
     'summary': '回放结构校验器：envelope/response 逐层校验，坏结构抛 INVALID_REPLAY_STATE。',
     'tags': ['validation', 'replay'], 'complexity': 'moderate'}]},
  'packages/llm/llm-deepseek/src/request-extensions.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '把插件贡献的请求字段并入序列化后的 Messages 请求：拒绝替换基础字段与基字段冲突（REQUEST_EXTENSION 带原因链），序列化失败退回基请求，accept 失败只报告不影响请求。',
   'tags': ['request-extensions', 'merge', 'error-handling'],
   'members': [
    {'kind': 'function', 'name': 'prepareRequestExtensions', 'start': 21, 'end': 59,
     'summary': '调用注册表 prepare 并合并贡献字段到基请求体，处理冲突报告与序列化失败回退，返回 accept 提交通道。',
     'tags': ['merge', 'request-extensions', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek/src/request-files.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '共享 Files 解析、有界陈旧 id 恢复与归一化图像诊断：RequestFiles 把请求中的文件/图像引用解析为可用表示，file-id 失效时按有界策略恢复重传，归一化图像被拒时给出带 wire 定位的诊断。',
   'tags': ['files', 'recovery', 'diagnostics'],
   'members': [
    {'kind': 'class', 'name': 'RequestFiles', 'start': 94, 'end': 158,
     'summary': '请求文件解析器：按消息定位文件/图像引用，经 DeepSeekFileStore 解析 file-id，陈旧映射触发有界恢复，失败以 FileResolutionFailure 报告。',
     'tags': ['files', 'resolution', 'recovery'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'normalizedImageDiagnostic', 'start': 72, 'end': 90,
     'summary': '为被提供方拒绝的归一化图像构造带消息/图像定位的诊断事实。',
     'tags': ['diagnostics', 'images'], 'complexity': 'moderate'}]},
  'packages/llm/llm-deepseek/src/request-pricing.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '提供方侧请求图像定价：按模型请求目标对保留的表面出现逐一定价（发布视觉 token 记账），offload 出现按占位文本计价；token meter 经 LlmAdapter.imageRequestPricing 同步消费，提供方用量仍是权威锚。',
   'tags': ['pricing', 'images', 'token-meter'],
   'members': [
    {'kind': 'function', 'name': 'deepSeekImageRequestPricing', 'start': 90, 'end': 111,
     'summary': '计算一条请求的图像定价投影：每个保留出现按请求目标+视觉 token 记账，offload 出现按占位文本计。',
     'tags': ['pricing', 'projection', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek/src/serialize.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '把系统快照、工具变更与对话轮次映射为 Messages 线缆格式：不支持的内容类型显式抛 UNSUPPORTED_CONTENT，回放状态经 readReplay 读取以恢复原生 thinking。',
   'tags': ['serialization', 'wire-format', 'messages'],
   'members': [
    {'kind': 'function', 'name': 'serialize', 'start': 57, 'end': 169,
     'summary': '主序列化器：GenerateOptions→WireRequest，处理系统消息、工具声明/更新块、多轮消息（含图像 file-id/base64 引用）与采样参数。',
     'tags': ['serialization', 'wire-request', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-deepseek/src/sse.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': 'SSE 帧解码委托 eventsource-parser：parseSse 把响应字节流转为 JSON 事件流（心跳注释脉冲空闲看门狗），未终止尾帧不算事件，JSON 错误保持提供方失败语义。',
   'tags': ['sse', 'streaming', 'parsing'],
   'members': [
    {'kind': 'function', 'name': 'parseSse', 'start': 13, 'end': 28,
     'summary': '解码完整 SSE 帧为 JSON 事件异步生成器，注释帧驱动活动脉冲，完成事件由翻译器裁决。',
     'tags': ['sse', 'generator', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/llm/llm-deepseek/src/translate.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'Messages 事件→harness 块流翻译：保持块序与累积用量，维护每块的回放元数据（signature），stop 原因映射与坏事件以 MALFORMED_RESPONSE 拒绝。',
   'tags': ['translation', 'streaming', 'replay'],
   'members': [
    {'kind': 'function', 'name': 'deltaChunk', 'start': 65, 'end': 88,
     'summary': '把内容增量事件转换为 harness 的 delta 块（文本/推理/工具参数增量），维护部分块状态。',
     'tags': ['translation', 'deltas'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'translate', 'start': 104, 'end': 166,
     'summary': '主翻译循环：消费 JSON 事件流产出 StreamChunk 序列，处理块开始/增量/结束、用量累积与终止原因映射。',
     'tags': ['translation', 'streaming', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-deepseek/src/transport.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '把 HTTP 与带内 Messages 错误归一为 provider 中立失败：providerErrorDetail 只读取 code/type/message 三字段，上下文超限/配额超限映射到规范 code。',
   'tags': ['error-handling', 'normalization', 'http'],
   'members': [
    {'kind': 'function', 'name': 'providerError', 'start': 22, 'end': 44,
     'summary': '把提供方 HTTP/带内错误转换为 LlmError（含 ProviderRequestId），分类上下文超限与配额超限。',
     'tags': ['error-handling', 'classification', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek/src/types.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'llm-deepseek 类型面：DeepSeekConnectionOptions 连接选项、DeepSeekCatalogModel 目录条目、适配器依赖注入接口（凭据/附件/图像访问解析器）。',
   'tags': ['type-definition', 'connection-options', 'di']},
  'packages/llm/llm-deepseek/src/upload-index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '持久附件→file-id 上传索引：DeepSeekUploadIndex 以原子写+文件锁维护 DSH home 下的 JSON 索引，记录哈希命中的可复用上传（过期/配额字段），损坏索引显式报 InvalidUploadIndexError。',
   'tags': ['upload-index', 'persistence', 'atomic-write', 'file-lock'],
   'members': [
    {'kind': 'class', 'name': 'DeepSeekUploadIndex', 'start': 112, 'end': 224,
     'summary': '持久上传索引：按（附件 id+变体+内容哈希+端点+认证头哈希）判定可复用上传，原子更新与并发文件锁保护。',
     'tags': ['index', 'persistence', 'reuse'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'parseIndex', 'start': 83, 'end': 105,
     'summary': '校验并解析磁盘索引 JSON 为记录表，坏结构抛 InvalidUploadIndexError。',
     'tags': ['validation', 'parsing'], 'complexity': 'moderate'}]},
  'packages/llm/llm-deepseek/src/wire-types.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': 'DeepSeek 支持的 Anthropic Messages 协议子集的线缆类型：WireInput（text/base64 图像/file 引用）、WireBlock、WireMessage、WireRequest。',
   'tags': ['type-definition', 'wire-format', 'messages']},
  'packages/llm/llm-deepseek/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-llm-deepseek 的 TypeScript 编译配置：strict + NodeNext + 工作区路径别名。',
   'tags': ['configuration', 'typescript', 'build-system']},
 },
 'extra_edges': [
  {'source': 'class:packages/llm/llm-deepseek/src/files-api.ts:DeepSeekFilesError', 'target': 'class:packages/llm/llm/src/index.ts:LlmError', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'class:packages/llm/llm-deepseek/src/file-store.ts:DeepSeekFileStore', 'target': 'class:packages/llm/llm-deepseek/src/files-api.ts:DeepSeekFilesClient', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/llm/llm-deepseek/src/file-store.ts:DeepSeekFileStore', 'target': 'class:packages/llm/llm-deepseek/src/upload-index.ts:DeepSeekUploadIndex', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-deepseek/src/host.ts:registerDeepSeekProvider', 'target': 'class:packages/llm/llm-deepseek/src/adapter.ts:DeepSeekAdapter', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-deepseek/src/host.ts:registerDeepSeekProvider', 'target': 'function:packages/llm/llm-deepseek/src/host.ts:createModelListingCache', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/llm/llm-deepseek/src/listing-cache.ts:ModelListingCache', 'target': 'function:packages/llm/llm-deepseek/src/listing.ts:requestModelListing', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-deepseek/src/serialize.ts:serialize', 'target': 'function:packages/llm/llm-deepseek/src/replay.ts:readReplay', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-deepseek/src/translate.ts:translate', 'target': 'function:packages/llm/llm-deepseek/src/replay.ts:replayState', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
