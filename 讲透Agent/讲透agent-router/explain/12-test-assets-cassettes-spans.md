# 12 · 测试资产三层：cassettes 重放、spans 对偶与真进程环境拼装

## 一、角色定位

本仓测试哲学是**确定性重放**：预录真实厂商交互，此后免凭据、零成本、毫秒级回归。三层资产各司其职：tests/internal/testopenai 用 go-vcr 盒带按 `X-Cassette-Name` 头重放 HTTP 响应（翻译器断言的"真值"）；tests/internal/testopeninference 对偶地预录 OpenInference span（tracing 断言的真值，10 篇）；tests/internal/dataplaneenv 把编译出的 extproc 二进制+func-e 拉起的 Envoy+假上游拼成无 K8s 的完整数据面。`make test-data-plane`（Makefile:210-215，依赖 build.extproc，先校验 func-e 存在 :213，bench 跑一遍加覆盖 :215）就是三层的总装入口；MCP 变体 test-data-plane-mcp 额外构建 aigw（Makefile:222-227）。

## 二、内部结构

**盒带注册中枢 cassettes.go**：`Cassette` 是 int 枚举（:23），40+ 个命名常量覆盖 chat/completions/embeddings/images/audio/azure 六族（如 CassetteChatBasic :29、流式 usage :65-66、真实 OpenAI Agents SDK 流量 :71-73）；`_cassetteNameEnd` 哨兵（:160）驱动 `cassettes()` 的有序遍历（:267-275）；stringValues 映射出文件名（:164）；`NewRequest`（:227）按六个请求表派发构造 POST（:281-299 统一设 `X-Cassette-Name` 头 :296）；`buildPath`（:249）让 azure- 前缀盒带走 `/openai/deployments/<model>/...` 路径（:250-253）；`ResponseBody`（:259）直接把盒带响应体交给测试当期望值——**重放即断言基准**。

**重放 handler.go**：cassetteHandler（:31）四路：指定盒带→遍历 interactions 语义匹配（:66-71）；找到盒带但无一匹配→409 并在错误信息里教你怎么重录（:74-81：删哪个文件、设哪个 env）；盒带不存在且有 API key→现场录制（:103 recordNewInteraction）；无头则全量扫描兜底（:111-119）。错误信息都走 `X-TestOpenAI-Error` 头标记（:130）。

**录制与脱敏 vcr.go**：盒带 `//go:embed`（:31-32）+启动时全量加载（allVCRCassettes :42）；requestHeadersToRedact 列 Authorization/Api-Key/cookie 及**全部 trace 头**（:51-58）——重放匹配时忽略它们（requestMatcher :76：method/url 相等 :78-83、头过滤后 DeepEqual :86-88、JSON 体语义比较忽略键序 :105-107、multipart 直接跳过体 :110-112）；recorderOptions（:64-71）ReplayWithNewEpisodes 模式+自定义 matcher+AfterCaptureHook；afterCaptureHook（:121）录制后清洗：Azure URL 抹掉私有资源名（:122-130）、敏感头删除（:134-140）、multipart 体替换占位符（:152-155）、gzip 解压（:172-187）、JSON pretty print（:143/:190）——落盘盒带既脱敏又可读。

**testopenai Server（server.go）**：newServer（:44）绑定 `:port` 全接口——注释 :46 说明是给 Docker 容器访问用的；录制目标从环境变量解析（Azure 优先 :55-71，OpenAI 兜底 :73-79）。

**span 对偶 testopeninference**：GetSpan（spans.go:19）入口；server.getSpan（server.go:69）缓存优先（:71），缺失且 `RECORD_SPANS=true` 才录制（:78）；录制流水线 recordSpan（recorder.go:46）：起 testopenai（:50）→起 OTLP collector（:57）→起代理容器（:64）→发请求（:71）→流式则读到 `data: [DONE]`（:109-120）。代理容器是**Python 的 OpenInference 参考实现**（openai_proxy.go:24，testcontainers 从 Dockerfile 构建 :46-56），env 注入 OTLP endpoint/BSP 延迟 100ms（:25-31）、azure 盒带切换凭据环境（:35-44）。断言 RequireSpanEqual（assertions.go:27）：normalizeSpanForComparison（:56）清时间戳/排序属性，filterSpanAttrs 剔除零值属性（:110），normalizeJSON（:163）把属性值再归一——**预录 span 与网关产出 span 的全等比较**，词汇表漂移立现。

**testotel（internal/testing）**：内存 SDK（mem.go:20 RecordNewSpan/:34 recordWithSpan 用 InMemoryExporter，清空时间戳 :47-52）；OTLPCollector（collector.go:88）单 gRPC server 三通道收 trace/metrics/logs（:99-101），Env()（:138）吐出 OTEL_* 环境变量（:109-117，delta temporality 防子测试间累积），TakeSpan（:153）带超时取单条。

**环境拼装 dataplaneenv.go**：extprocBin 在 init 按需构建（:37，BuildGoBinaryOnDemand build.go:20-33：设了 EXTPROC_BIN 环境变量则直接用——本地复用二进制的逃生口）；StartTestEnvironment（:81）依次起 extproc（:142）与 Envoy（:155）；requireEnvoy（:218）把配置模板里的端口 token 替换成临时端口（:225-233），func-e run 拉起 Envoy 且 `--base-id` 随机化支持并行（:254-259）；上下文特意不用 t.Context 的注释（:245-253）解释了清理次序陷阱；最后连接自检（:170-179）。tests/data-plane/extproc_test.go 的 TestMain（:176）嵌入 envoy.yaml 模板（:171-172）、预起两台恒 500 错误服务器（明文+TLS :178-212）供 failover 场景用，假上游是 testupstreamlib.Server（:230）。

## 三、外部连接

- **translator/extproc 测试**：tests/data-plane 全部断言消费这三层——`make test-data-plane` 即 03 篅盒带对照的运行形态。
- **tracing 测试**：data-plane 断言网关产出的 span 与 GetSpan 预录值全等（10 篇出口的验证器）。
- **controller/e2e 层**：envtest（test-controller Makefile:233-236）与 kind e2e（e2elib 走 kubectl）是另外两层，不碰盒带。
- **real_providers_test.go**：tests/data-plane 里的显式真厂商模式，与盒带模式互补。

## 四、数据流

给一个新翻译断言的完整路径：cassettes.go 加枚举+请求体（chat_requests.go 等按端点分文件）→（首次需开 API key 录制，409 文案会告诉你删哪个文件）→ data-plane 测试里 `testopenai.NewRequest` 打网关 listener → 断言响应体=盒带原文（ResponseBody 直取）→ 需要验证 trace 时再取 GetSpan 断言属性全等。整条链无 K8s、无真厂商、无凭据，且对 JSON 键序/trace 头扰动免疫。

## 五、设计决策

1. **录制与重放同体**：一个 handler 两种身份（handler.go:62-107），409 错误文案就是操作手册（:79-81）——盒带过期的修复动作被编码进报错本身。
2. **脱敏在 capture hook 而非事后脚本**（vcr.go:121-203）：一次录制即得干净盒带，杜绝"先落敏感数据再洗"的窗口；trace 头全列 redact 让重放对采样器/传播器变化零敏感。
3. **span 用外部参考实现录制**（openai_proxy.go Python 容器）：断言"网关实现的 OpenInference"对照"OpenInference 官方实现"，避免自家实现自证清白——这是对偶设计的精髓。
4. **二进制按需构建+环境变量逃生口**（build.go:20-30）：默认保证测试打的是当前代码，EXTPROC_BIN 又让调试会话复用带断点的二进制。
5. **配置模板端口 token 化**（dataplaneenv.go:225-233）：同一份 envoy.yaml 在 CI 并行、Docker、本机三种形态下复用。

## 六、新人提示

新增盒带：先写请求体与枚举，跑测试看 500 报错里的操作提示（设 key 重录）；盒带 YAML 是 pretty 过的，别手改格式否则下次录制 diff 会噪音。排查顺序：409=盒带内 interactions 全不匹配（看 method/url/头差异）→ 500 无头=测试没带 X-Cassette-Name。坑三处：multipart 体在盒带里是占位符（vcr.go:154）；RECORD_SPANS 需要 Docker（openai_proxy 容器）；bench 用 `-benchtime=1x` 只跑一遍（Makefile:215 注释），别指望它做性能测量。
