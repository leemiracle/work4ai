# batch-023 semantic data (llm-deepseek-account, llm-deepseek-api-key, llm-pi-ai part 1)
BATCH = {
 'files': {
  'packages/llm/llm-deepseek-account/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-llm-deepseek-account 包参考：账号 token 认证、失效处理与 deepseek-account 路由的模型发现；认证独占来自账号服务，模型目录经账号 listing 端点+版本门控。',
   'tags': ['documentation', 'package-reference', 'account-auth']},
  'packages/llm/llm-deepseek-account/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-llm-deepseek-account 包清单：DeepSeek 账号路由插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/llm/llm-deepseek-account/src/config.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '账号路由配置：Messages 设置 + 模型 listing 端点 + 按模型 id 的字段覆盖（modelOverrides 叠加在账号 listing 与内置目录之上），复用协议包的 schemastery 字段定义。',
   'tags': ['configuration', 'schemastery', 'model-overrides'],
   'members': [
    {'kind': 'function', 'name': 'resolveAccountOptions', 'start': 84, 'end': 97,
     'summary': '读取一代账号路由配置：协议字段+listing 配置+覆盖表解析为 ResolvedAccountOptions。',
     'tags': ['resolution', 'config', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek-account/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'deepseek-account 路由插件入口（name=llm-deepseek-account，inject=llm）：apply 注册 provider，token 走 x-dsh-auth-token 头，未登录抛 ACCOUNT_SIGN_IN_REQUIRED，账号配额超限映射专用 code，模型目录走账号 listing+版本门控。',
   'tags': ['entry-point', 'plugin', 'account-auth', 'provider-registration'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 29, 'end': 99,
     'summary': '插件 apply：解析设置、注册 DeepSeek provider（账号 token 认证头+请求错误回调）、创建模型目录缓存并处理账号配额失效。',
     'tags': ['plugin-entry', 'apply', 'cordis', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-deepseek-account/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-llm-deepseek-account 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/llm/llm-deepseek-api-key/README.md': {
   'type': 'document', 'complexity': 'moderate',
   'summary': 'dsh-llm-deepseek-api-key 包参考：API-key 认证、凭据门控发现与官方路由的模型 listing（仅官方 origin 的 /models 被跟随）。',
   'tags': ['documentation', 'package-reference', 'api-key']},
  'packages/llm/llm-deepseek-api-key/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-llm-deepseek-api-key 包清单：DeepSeek 官方路由 API-key 插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/llm/llm-deepseek-api-key/src/config.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': 'API-key 配置与端点代际解析：apiKeyEnv 凭据引用默认 DEEPSEEK_API_KEY，仅官方 origin 且目录未改时跟随官方 /models listing，端点与凭据引用来自同一配置代际。',
   'tags': ['configuration', 'credentials', 'listing'],
   'members': [
    {'kind': 'function', 'name': 'resolveAdapterOptions', 'start': 51, 'end': 61,
     'summary': '读取一代官方路由配置：协议字段+凭据引用+可选 listing 设置解析为连接快照。',
     'tags': ['resolution', 'config', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-deepseek-api-key/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'deepseek-official 路由插件入口（name=llm-deepseek-api-key，inject=llm）：apply 凭据门控地解析 API key（无 key 时给出可行动错误），注册 provider、模型目录缓存与凭据门控发现。',
   'tags': ['entry-point', 'plugin', 'api-key', 'provider-registration'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 34, 'end': 124,
     'summary': '插件 apply：解析设置、按凭据引用解析 key、注册 DeepSeek provider 与目录缓存、发布可配置 provider 目录项供 GUI 选择。',
     'tags': ['plugin-entry', 'apply', 'cordis', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-deepseek-api-key/tsconfig.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': 'dsh-llm-deepseek-api-key 的 TypeScript 编译配置。',
   'tags': ['configuration', 'typescript']},
  'packages/llm/llm-pi-ai/README.md': {
   'type': 'document', 'complexity': 'complex',
   'summary': 'dsh-llm-pi-ai 包参考：经 pi-ai 目录与线缆协议服务已配置的 provider 路由（含手工声明的网关），一次解析一个不可变快照、请求级冻结、凭据经 harness seam 以 apiKey 选项最高优先级注入。',
   'tags': ['documentation', 'package-reference', 'pi-ai', 'multi-provider']},
  'packages/llm/llm-pi-ai/package.json': {
   'type': 'config', 'complexity': 'simple',
   'summary': '@deepseek-ai/dsh-llm-pi-ai 包清单：pi-ai 多 provider 适配器插件。',
   'tags': ['configuration', 'package-manifest']},
  'packages/llm/llm-pi-ai/scripts/gen-provider-data.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '构建期生成脚本：经 pi-ai 公共目录与 auth 上下文产出 provider 展示元数据（env 变量、默认端点、原生认证方式）到 provider-data.generated.ts，用 TypeScript API 原地重写。',
   'tags': ['codegen', 'build-script', 'provider-metadata'],
   'members': [
    {'kind': 'function', 'name': 'generateProviderData', 'start': 92, 'end': 120,
     'summary': '从安装的 pi-ai 内置 provider 集合提取展示元数据（不执行认证）。',
     'tags': ['codegen', 'extraction', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'syncProviderData', 'start': 127, 'end': 155,
     'summary': '用 TypeScript printer 原地重写 provider-data.generated.ts，保持生成文件与安装版本同步。',
     'tags': ['codegen', 'typescript-api', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-pi-ai/src/adapter.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'pi-ai 支撑的通用 LLM seam 实现：每次解析产出不可变快照（profiles+Models 集合），操作在首个 await 前捕获整个快照——Models.streamSimple 惰性解析使配置变更只影响下一步而非在途请求；凭据引用经 harness seam 解析后作为请求 apiKey 选项（pi-ai 视为最高优先级覆盖）。',
   'tags': ['adapter', 'pi-ai', 'snapshot-freeze', 'service-provider'],
   'members': [
    {'kind': 'class', 'name': 'PiAiAdapter', 'start': 273, 'end': 500,
     'summary': '继承 LlmAdapter 的 pi-ai 通用适配器：按路由构建 Provider/Models 快照，dispatch 把 harness 请求转 pi-ai Context 并把事件流翻译回 harness 块流（推理力度/请求头诊断/图像管线齐备）。',
     'tags': ['adapter', 'pi-ai', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'requestHeaders', 'start': 240, 'end': 266,
     'summary': '组装请求头（含归因头与诊断字段），供请求头问题诊断。',
     'tags': ['headers', 'diagnostics'], 'complexity': 'moderate'}]},
  'packages/llm/llm-pi-ai/src/catalog.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'pi-ai 目录物化（987 行）：安装目录按模型 id 提供默认，profile 自有模型逐字段覆盖；严格解析在设置写入前拒绝不可服务模型，宽松解析保留诊断使目录漂移不阻碍检视/修复；兼容协议门控与 thinking 级别解析。',
   'tags': ['catalog', 'materialization', 'compat', 'validation'],
   'members': [
    {'kind': 'class', 'name': 'PiAiCatalogError', 'start': 674, 'end': 679,
     'summary': '目录解析错误（继承 Error）：携带定位与原因，供设置面展示。',
     'tags': ['error-handling', 'catalog', 'exported'], 'complexity': 'simple', 'exported': True},
    {'kind': 'function', 'name': 'resolveRouteModels', 'start': 858, 'end': 987,
     'summary': '解析一条路由的模型集合：目录默认+profile 覆盖+兼容门控+推理级别归一，输出可服务模型与诊断并列。',
     'tags': ['catalog', 'resolution', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'resolveModelReasoning', 'start': 720, 'end': 774,
     'summary': '把 pi-ai 模型思考级别解析为 harness 推理力度元数据（off/low/high/max 语义映射）。',
     'tags': ['reasoning', 'resolution'], 'complexity': 'complex'}]},
  'packages/llm/llm-pi-ai/src/config.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'pi-ai 适配器的配置 schema 与 provider-profile 校验（551 行）：profile 按路由为键的 dict，组合基与用户设置层按 provider 合并；路由键不必是已安装 provider（命名即继承默认，未命名即整体声明）；写入前校验每个变更 provider。',
   'tags': ['configuration', 'schemastery', 'profiles', 'validation'],
   'members': [
    {'kind': 'function', 'name': 'resolveProfiles', 'start': 441, 'end': 551,
     'summary': '把组合基配置与用户设置层逐 provider 合并解析为路由 profile 集（含移除字段拒绝与请求头校验）。',
     'tags': ['resolution', 'merge', 'profiles', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'assertValidHeaders', 'start': 420, 'end': 431,
     'summary': '校验 profile 自定义请求头（键值合法性），坏值在写入前失败。',
     'tags': ['validation', 'headers'], 'complexity': 'simple'}]},
  'packages/llm/llm-pi-ai/src/context.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'harness 请求历史→pi-ai Context 词汇的转换：系统提示拆分、开发者/共享历史追加、工具结果映射、图像准备（offload 投影+请求目标解析）与 text-only 降级。',
   'tags': ['translation', 'context', 'history'],
   'members': [
    {'kind': 'function', 'name': 'toPiContext', 'start': 315, 'end': 350,
     'summary': '主转换（三个重载组 315-401）：GenerateOptions 的消息/工具/系统提示→pi-ai Context，含图像与 text-only 变体。',
     'tags': ['translation', 'context', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'appendSharedHistory', 'start': 217, 'end': 246,
     'summary': '把共享历史消息追加到 pi-ai 上下文（含回放 assistant 重建与外来消息降级）。',
     'tags': ['history', 'translation'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'textOnlyContext', 'start': 248, 'end': 269,
     'summary': '为无图像能力的路由构造纯文本 pi-ai 上下文。',
     'tags': ['text-only', 'context'], 'complexity': 'moderate'}]},
  'packages/llm/llm-pi-ai/src/discovery.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '回答「该 provider 能服务哪些模型」：目录内路由直接从安装目录回答（零网络），目录外路由（网关/自托管）才线上询问 OpenAI 兼容与 Anthropic Messages 协议；结果不落盘，仅供配置面采纳。',
   'tags': ['discovery', 'models', 'catalog', 'http'],
   'members': [
    {'kind': 'function', 'name': 'discoverModels', 'start': 269, 'end': 363,
     'summary': '发现入口：按路由来源选择目录回答或线上询问，产出候选模型元数据列表。',
     'tags': ['discovery', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'readListing', 'start': 181, 'end': 230,
     'summary': '有界读取远端模型 listing 端点并解析为候选条目。',
     'tags': ['http', 'listing'], 'complexity': 'complex'}]},
  'packages/llm/llm-pi-ai/src/index.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'pi-ai 适配器插件入口：apply 拥有路由 dict——凭据/端点/模型变化下一请求生效，路由集变化原位重注册同一适配器实例；注册可配置 provider 目录项（nativeAuth/默认端点来自生成数据）。',
   'tags': ['entry-point', 'plugin', 'route-dict', 're-registration'],
   'members': [
    {'kind': 'function', 'name': 'apply', 'start': 175, 'end': 344,
     'summary': '插件 apply（170 行）：构建 PiAiAdapter、注册路由集与目录项、挂接登录流与设置面发现，路由集变更时原位重注册。',
     'tags': ['plugin-entry', 'apply', 'cordis', 'exported'], 'complexity': 'complex', 'exported': True}]},
  'packages/llm/llm-pi-ai/src/login.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'pi-ai 自带登录 provider 的授权流：harness 中立 notice/prompt 词汇与 pi-ai AuthInteraction 的全部翻译层（relay 转发事件、restate 复述提示）。',
   'tags': ['login', 'authorization', 'translation'],
   'members': [
    {'kind': 'function', 'name': 'registerPiAiFlows', 'start': 131, 'end': 172,
     'summary': '把 pi-ai 登录流注册到 harness 授权服务（AuthorizationSession 适配 AuthInteraction）。',
     'tags': ['authorization', 'registration', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'relay', 'start': 58, 'end': 87,
     'summary': '把 pi-ai 授权事件转发为 harness 授权方法通知。',
     'tags': ['events', 'authorization'], 'complexity': 'moderate'}]},
  'packages/llm/llm-pi-ai/src/models.ts': {
   'type': 'file', 'complexity': 'moderate',
   'summary': '从公共窄入口组装 pi-ai 模型助手：createModels 构建 Models 集合、thinking 级别查询与会话更新（conversationUpdates）。',
   'tags': ['models', 'factory', 'pi-ai'],
   'members': [
    {'kind': 'function', 'name': 'conversationUpdates', 'start': 75, 'end': 92,
     'summary': '订阅 pi-ai 模型目录变更并转发为 harness 的 models-updated 通知。',
     'tags': ['events', 'models', 'exported'], 'complexity': 'moderate', 'exported': True}]},
  'packages/llm/llm-pi-ai/src/provider-data.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': '配置面用的已安装 provider 默认值：读生成的 PROVIDER_DATA 表，不执行认证；未记录 provider 仅暴露固定公共端点。',
   'tags': ['provider-metadata', 'generated-data', 'config-surface'],
   'members': [
    {'kind': 'function', 'name': 'providerDefaultsOf', 'start': 12, 'end': 19,
     'summary': '按 provider id 返回展示元数据（nativeAuth/默认端点/环境变量），未记录者给保守默认。',
     'tags': ['metadata', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/llm/llm-pi-ai/src/provider.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '为一条配置路由构造 pi-ai Provider 的双路径决策：目录内且未改协议的路由复用目录 Provider（只换模型集，保留 Bedrock Smithy 等无法重建的 API 实现）；其余路由经协议表 createProvider 构建。凭据不进本模块存储。',
   'tags': ['provider-construction', 'reuse', 'protocols'],
   'members': [
    {'kind': 'function', 'name': 'buildProvider', 'start': 167, 'end': 192,
     'summary': '构造入口：按路由是否目录内+协议是否被覆盖选择复用或重建 Provider。',
     'tags': ['factory', 'provider', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'reuseCatalogProvider', 'start': 144, 'end': 159,
     'summary': '复用目录 Provider 并替换其模型集合，保留目录方 API 实现。',
     'tags': ['reuse', 'catalog'], 'complexity': 'moderate'}]},
  'packages/llm/llm-pi-ai/src/replay.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': '持久 pi-ai 回放元数据与 assistant 历史重建：harness 内容仍是文本/工具调用的持久源，本模块只存重建 pi-ai assistant 消息所需的原生元数据（用量、签名、参数对象），外来/跨模型历史降级。',
   'tags': ['replay', 'metadata', 'history-reconstruction'],
   'members': [
    {'kind': 'function', 'name': 'toPiReplayState', 'start': 77, 'end': 110,
     'summary': '把 harness assistant 块与 pi-ai 原生元数据打包为回放 envelope。',
     'tags': ['replay', 'serialization', 'exported'], 'complexity': 'moderate', 'exported': True},
    {'kind': 'function', 'name': 'readReplayState', 'start': 117, 'end': 149,
     'summary': '读取并校验持久回放状态，外来或损坏 envelope 降级为无回放。',
     'tags': ['replay', 'validation'], 'complexity': 'moderate'},
    {'kind': 'function', 'name': 'replayedAssistant', 'start': 187, 'end': 232,
     'summary': '从持久内容+回放元数据重建 pi-ai assistant 消息（工具参数从原始 JSON 恢复）。',
     'tags': ['replay', 'reconstruction'], 'complexity': 'complex'},
    {'kind': 'function', 'name': 'toPiAssistant', 'start': 247, 'end': 259,
     'summary': 'assistant 消息转换导出面：harness 块→pi-ai AssistantMessage（含回放元数据路径）。',
     'tags': ['translation', 'assistant', 'exported'], 'complexity': 'simple', 'exported': True}]},
  'packages/llm/llm-pi-ai/src/stream.ts': {
   'type': 'file', 'complexity': 'complex',
   'summary': 'pi-ai assistant 事件→harness 流协议翻译：工具参数从解析对象还原原始 JSON 表示，pi-ai 终止失败事件映射为 harness finish 块（上下文溢出/配额/空响应分类）。',
   'tags': ['streaming', 'translation', 'error-classification'],
   'members': [
    {'kind': 'function', 'name': 'toStreamChunks', 'start': 144, 'end': 244,
     'summary': '主翻译：pi-ai AssistantMessageEvent 流→StreamChunk 序列（文本/推理增量、工具调用、用量与终止原因映射）。',
     'tags': ['streaming', 'translation', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'mapStopReason', 'start': 80, 'end': 128,
     'summary': '把 pi-ai 终止原因映射为 harness FinishReason（含失败类终止的失败快照构造）。',
     'tags': ['mapping', 'finish-reason', 'exported'], 'complexity': 'complex', 'exported': True},
    {'kind': 'function', 'name': 'classifyPiAiError', 'start': 42, 'end': 68,
     'summary': '把 pi-ai 错误分类为 harness 错误 code（上下文超限/配额超限/空响应等）。',
     'tags': ['error-classification'], 'complexity': 'moderate'}]},
  'packages/llm/llm-pi-ai/src/types.ts': {
   'type': 'file', 'complexity': 'simple',
   'summary': 'llm-pi-ai 类型面：路由 profile 解析结果与适配器内部结构类型。',
   'tags': ['type-definition']},
 },
 'extra_edges': [
  {'source': 'class:packages/llm/llm-pi-ai/src/adapter.ts:PiAiAdapter', 'target': 'class:packages/llm/llm/src/index.ts:LlmAdapter', 'type': 'inherits', 'direction': 'forward', 'weight': 0.9},
  {'source': 'function:packages/llm/llm-pi-ai/src/index.ts:apply', 'target': 'class:packages/llm/llm-pi-ai/src/adapter.ts:PiAiAdapter', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-pi-ai/src/index.ts:apply', 'target': 'function:packages/llm/llm-pi-ai/src/login.ts:registerPiAiFlows', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-pi-ai/src/index.ts:apply', 'target': 'function:packages/llm/llm-pi-ai/src/config.ts:resolveProfiles', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/llm/llm-pi-ai/src/adapter.ts:PiAiAdapter', 'target': 'function:packages/llm/llm-pi-ai/src/context.ts:toPiContext', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'class:packages/llm/llm-pi-ai/src/adapter.ts:PiAiAdapter', 'target': 'function:packages/llm/llm-pi-ai/src/stream.ts:toStreamChunks', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-pi-ai/src/context.ts:appendSharedHistory', 'target': 'function:packages/llm/llm-pi-ai/src/replay.ts:toPiAssistant', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-deepseek-account/src/index.ts:apply', 'target': 'function:packages/llm/llm-deepseek/src/host.ts:registerDeepSeekProvider', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
  {'source': 'function:packages/llm/llm-deepseek-api-key/src/index.ts:apply', 'target': 'function:packages/llm/llm-deepseek/src/host.ts:registerDeepSeekProvider', 'type': 'calls', 'direction': 'forward', 'weight': 0.8},
 ],
}
