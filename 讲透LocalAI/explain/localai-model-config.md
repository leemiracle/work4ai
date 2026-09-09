# localai-model-config — 2342 行的"配置即模型"类型系统

> 源码：`core/config/model_config.go`（2342 行，图谱 70 个子类型/方法，全仓 460 个文件引用它——最高扇入之一）

## 角色定位

18 层架构的"配置中枢层"。LocalAI 的核心抽象不是模型文件，而是**模型 YAML**：一份配置声明权重来源（URL/HF repo/artifacts）、后端引擎、提示模板、采样参数、能力 usecase、PII 脱敏策略、路由规则、云代理、资源限制……`ModelConfig` 就是这份 YAML 的 Go 投影。它被三处消费：启动期 loader（读 models 目录落库）、请求期中间件（按模型名取出并合并请求级覆盖）、分布式调度器（按配置估算 VRAM 与装箱）。存在理由：把"一个模型怎么跑"的全部知识收进一个可校验、可默认值化、可猜测能力的类型——任何子系统需要模型信息时都来问它，而不是各自 parse。

## 内部结构

**主结构 `ModelConfig`**（45-163 行，119 行）：嵌入 `schema.PredictionOptions`（采样参数，yaml `parameters`）与 `LLMConfig`（`yaml:",inline"`——llama.cpp 装载参数直接平铺进根级）；组合 20+ 子配置节：`TemplateConfig`（模板）、`Pipeline`（语音/对话管线 80 行大类）、`FunctionsConfig`/`ReasoningConfig`/`Compression`、`Diffusers`（图像管线）、`GRPC`（外部后端直连）、`TTSConfig`、`MCP`/`Agent`/`PII`/`PIIDetection`/`Router`/`Proxy`/`MITM`/`Limits`。**私有字段带 `yaml:"-"`**：`modelConfigFile`、`persistedConfigRevision`（48-56 行长注释：请求管线会用调用方采样参数改写配置副本，装载期盖 revision 戳才能让控制器"每配置一个修订号"而非"每请求一个"）、`RequestMetadata`（中间件注入的请求级元数据）。

**子配置群**（168-1379 行）值得点名的设计：`Alias`（61-65 行）让配置成为纯重定向；`ProxyConfig`（224-270）passthrough/translate 双模式 + APIKeyFile（K8s secret 挂载）+ Anthropic prompt-cache 断点；`MITMModelConfig`（205-209）host 与 PII 策略一对一绑定；`RouterConfig`（310-316+）声明"depth-1 不变量"——候选不得再带 router，保调度图无环；`LimitsConfig`（182-195）准入控制（503+Retry-After）。

**方法层**（1380-2342 行）四根支柱：`UnmarshalYAML`（1380）、`SetDefaults`（1476）、`Validate`（1568）、`GuessUsecases`（2078）。另有 `ModelID`/`ModelFileName`（artifacts 快照优先）、PII 门面方法群、`ApplyReasoningEffort`（reasoning_effort→chat_template 参数）等。

## 外部连接

460 个 importers 覆盖 core/application（装载与热更）、core/http（请求中间件取配置）、core/services（分布式调度/VRAM 预算）、pkg/backend（把 LLMConfig 翻译成引擎参数）。它反向依赖 schema（PredictionOptions/OpenAI 类型）、pkg/modelartifacts（artifacts 归一化）、downloader（URI 判断）、functions（grammar 配置）。图谱 in_edges 460 条 imports 之外还有 1 条 documents——它是仓内被文档引用最多的实现文件之一。

## 数据流

一份 YAML 的完整旅程：

1. **反序列化**（1380-1391）：`UnmarshalYAML` 用 `type BCAAlias ModelConfig` 别名类型绕开自定义 unmarshal 的无限递归（Go 惯用法），decode 后 `syncKnownUsecasesFromString()` 把字符串列表同步进位标志集合。
2. **默认值化**（1476-1566）：一条**分层默认值链**——`ApplyInferenceDefaults`（模型家族特定参数，先跑）→ `ApplyServingDefaults`（前缀缓存等策略）→ `ApplyGenericDefaults`（通用回填，只填空）→ LoadOptions 的 CLI ctx/threads/f16（在 hooks 前应用防被覆盖）→ `runBackendHooks`（GGUF 元数据猜测 context size）→ Go 侧 pooling 时自动注入 `pooling:none` 给 llama.cpp（1550-1554，跨后端契约适配）→ `ApplyHardwareDefaults`（**最后**跑：Blackwell 大 batch 依赖最终确定的 context size，注释明确顺序原因）。
3. **校验**（1568-1639+）：compression 取值域、alias 纯净性（不得带 backend/model/artifacts、不得自指）、artifacts 名称唯一 + **primary 必须在 [0]**（Artifacts[0] 是所有消费者的装载目标，ModelFileName/体积估算/暂存都按下标取）、文件名合法性。跨配置的约束（alias 目标存在、无 router 链）留给持有全量配置的 loader。
4. **能力猜测**（2078-2237+）：`GuessUsecases(u)` 按位 flag 逐项判定——chat 需要模板且后端不在 nonTextGenBackends 黑名单；transcript 必须是 whisper 且非 vad_only；3D 只认 trellis2cpp；vad 认 silero-vad/sherpa-onnx/whisper+vad_only……`FLAG_VISION` 分支的注释（2165-2177）记录了一个自噬 bug：猜测结果经 `syncKnownUsecasesFromString` **写回**配置后，下一轮 sync 把它当显式声明解析，反向击穿 `VisionSupported` 的显式信号检查——修复即"猜测必须走与显式信号相同的判据"。
5. **运行期**：请求中间件深拷贝配置、合并请求参数（这就是 persistedConfigRevision 存在的原因），推理层用 `IsMultimodal`/`FunctionToCall`/`ResolvedStoreName` 等门面方法查询。

## 设计决策

1. **配置即模型（config-as-model）**：Name 是 API 可见的模型 ID，一切能力（能 chat 吗、能出图吗）从配置推导而非运行探测——`GuessUsecases` 让裸 YAML 也能自动挂到正确端点。
2. **三层默认值（家族→策略→通用→硬件）+ 顺序契约**：注释把"谁先谁后"写成不变式（硬件默认必须见最终 ctx size），防止后来者插错层。
3. **持久层与请求层的字段隔离**：`yaml:"-"` 系私有字段让同一结构体安全穿越"落盘→改写→回写"循环而指纹不漂移。
4. **校验分两级**：单配置能查的（Validate）vs 需全量集合的（alias 目标、router 环）分置——validate 保持纯函数性。
5. **枚举外置成字符串+白名单方法**（backend 名、usecase flag）：新增后端不必改核心类型，GuessUsecases 的切片扩一行即可。

## 新人提示

- 切入点：45-163 主结构通读 → SetDefaults（1476）→ GuessUsecases（2078）；中间 1200 行子配置当字典查。
- 易混淆点一：`Model`（权重路径/URL）vs `Name`（API 模型名）vs `ModelID()`（Name 优先回退 Model）——路由、prefix-cache 盐、ACL 三者必须用 ModelID 才一致（1431-1441 注释）。
- 易混淆点二：`Artifacts`（新式控制器管理快照）与 `DownloadFiles`/`Model` URL（旧式）并存——ModelFileName 的解析顺序是 artifacts 优先。
- 易混淆点三：`PII`（本模型被过滤）与 `PIIDetection`（本模型当过滤器用）是角色相反的两个节。
- 调试配置问题时先跑 `local-ai util usecase-heuristic <config>`（run.go 启动错误信息里也提示它），Validate+GuessUsecases 的诊断输出比肉眼读 YAML 快。
