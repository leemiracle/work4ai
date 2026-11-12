# 12 · e2e 测试体系：60+ 场景背后的框架工程

## 角色定位（L06 测试与质量保障层）

在 16 层架构里，`controller/test/` 对应 L06「测试与质量保障层」，它是 agentgateway 的**总验收闸门**：translator（L01）、xDS 管线（L03）、数据面过滤器（L05/06 各协议）的每一处行为变更，最终都要在这里以"真实 kind 集群 + 真实 Envoy 数据面 + 真实流量"的方式被验证。规模实证：`controller/test/e2e/` 下 38 个顶层 `Test*` 函数、115 处 `t.Run` 子测试、`testdata/` 31 个场景目录（apikeyauth/a2a/mcp/modelrouting/guardrail 全谱系），叠加 conformance 双线，远超"60+ 场景"。

这一层的哲学是"**改任何东西先想 e2e 怎么写**"：框架把 Kubernetes 装卸、Helm 生命周期、轮询断言、失败取证全部封装成 API，写一个新场景只剩三件事——写 YAML、`t.Apply`、`t.Send`+期望。反过来，任何 CRD/翻译器改动若没有对应场景覆盖，CI 的 `controller-e2e` job（`.github/workflows/pull_request.yml:161`）就是最后防线。

它与另外两条质量线互补：`crates/llm/src/golden_tests.rs`（Rust 单元级快照，17 种 provider 的请求/响应翻译矩阵，`golden_tests.rs:32-55` 定义 provider 常量表）锁数据面纯函数行为；`controller/test/deployer`+`test/helm` 的 golden 快照（Makefile `golden-deployer`/`golden-helm` 目标，`controller/Makefile:203,210`）锁 Helm 渲染产物。e2e 则锁"整条链路在真实集群里的端到端语义"，三层互不替代。

## 内部结构

框架分四个子包 + 两套脚本，全部围绕一个核心抽象 `TestInstallation` 展开。

**TestInstallation：Helm 生命周期容器**（`controller/test/e2e/test.go`）。它是"一次 agentgateway 安装"的 Go 映射：结构体持有 RuntimeContext（谁在跑测试）、ClusterContext（哪个集群）、InstallNamespace、ValuesManifestFile、Helm client 与 GeneratedFiles（`test.go:106-127`）。装卸对称四步：

- `InstallFromLocalChart`（`test.go:160-163`）先装 CRD chart 再装主 chart。CRD chart 路径锚定 `controller/install/helm/agentgateway-crds`（`test.go:179`），主 chart 可被 `AGW_E2E_CORE_CHART_PATH` 环境变量替换（`test.go:206-209`）——这是给"魔改 chart 跑 e2e"留的口子。
- 装主 chart 时若设了 `VERSION`，自动追加 `--set-string image.tag=$VERSION`（`test.go:219-221`），让本地构建镜像优先于 registry 默认 appVersion。
- 装完不是盲等：`assertions.EventuallyGatewayInstallSucceeded`（`test.go:238`）轮询 `app.kubernetes.io/name=agentgateway` 标签的 Pod 全部 Running+Ready（`assertions.go:221-224`）。
- `Uninstall`（`test.go:254-257`）反序卸主 chart、CRD chart，各自带 `--wait`（`test.go:277`），卸完断言 Pod 数归零（`assertions.go:226-238`）。`releaseExists`（`test.go:344-356`）直接 List Helm 的 owner Secret 判断 release 存在，支撑 PERSIST_INSTALL 的"已装跳过"。

生命周期有精细的本地迭代模式，全在 `test/testutils/env.go` 定义：`SKIP_INSTALL`（env.go:13）复用外部安装、`PERSIST_INSTALL`（:18）"装过就跳过+不卸载"、`FAIL_FAST_AND_PERSIST`（:38）失败时保留现场供取证（其 22-37 行注释把四种组合的行为矩阵写得极清楚，是理解本框架的最佳入口）、`SKIP_ALL_TEARDOWN`（:46）、`USE_PORTFORWARD`（:84，无 LoadBalancer 环境走本地端口转发）。

**base 包：测试作者日常用的 API**（`controller/test/e2e/base/`）。`Test` 结构（`base/test.go:32-42`）内嵌 `*testing.T`，提供：`Send(target, expect, opts...)`（`test.go:138-141`）发 HTTP——target 可以是 `"/get"`、`"host/path"` 或完整 URL，`targetOptions`（`test.go:167-198`）自动拆解成 curl 的 host/path/scheme 选项；期望值用 `Expect(status)`/`ExpectOK()`/`ExpectForbidden(body)` 构造（`test.go:145-165`），返回 gomega matcher 结构。`Apply(manifests...)`（`base/manifest.go:88-101`）apply YAML 后自动 `waitForResources`——解析 manifest 里声明的 Pod/Deployment，等 `app.kubernetes.io/name=<name>` 的 Pod 全 Ready（`manifest.go:61-84`），再通过 `testutils.Cleanup` 注册反删（删除前 `stripNamespaceResources` 剥掉 Namespace 对象防误删，`manifest.go:160-177`）；对 Gateway 还会动态推导同名 Deployment/Service 一起等（`manifest.go:229-245`）。`ApplyPersistent`（`manifest.go:118-133`）给昂贵共享依赖（如 testbox）用，PERSIST_INSTALL 下不清理。`Manifest(pathParts...)`（`manifest.go:144-150`）用 `runtime.Caller(1)` 解析到**调用者所在包**的 testdata，天然支持多包复用。

**断言库**：`testutils/assertions/assertions.go` 15 个 `Eventually*` 函数（Pods/GatewayCondition/ListenerAttachedRoutes/HTTPRouteCondition/GRPCRouteCondition/InferencePoolCondition/AgwBackendCondition/AgwPolicyStatus/GatewayAddress…），每个都是 `retry.UntilSuccessOrFail` 包一次 Get+gomega Match（如 `EventuallyGatewayCondition`，`assertions.go:55-64`）。gomega 自定义 matchers 在 `test/gomega/matchers/`（pod/have_condition/have_kubegateway_status/have_http_response/contain_substrings 五个文件）+ `gomega/transforms/`——任务书称"七件套"，实数是 5 matcher + 1 transform + 1 assertions 门面（按源码为准）。

**testbox：十合一多协议 mock 二进制**（`controller/hack/testbox/`）。单进程同时起 10 个假后端：dummy-idp、extproc、ext-authz、ext-mcp、mcp-website-fetcher、mcp-admin-server、a2a、llm、echo app、raw-headers（`main.go:31-40` 顺序 start，每个返回 shutdown 闭包，SIGTERM 后倒序优雅关闭，`main.go:45-52`）。端口契约写在 `README.md:5-12`（8443=IdP、18080=ext-proc、9000=ext-authz、9999=a2a 等）。镜像基于 `cgr.dev/chainguard/static` 空基础（`Dockerfile:1`）以 nonroot 跑（`:5`）。**这是独立 Pod 而非 sidecar**：`make testbox-docker kind-load-testbox`（`controller/Makefile:491,497`）构建后 `kind load` 进节点，e2e manifest 里的 Deployment 直接引用 `ghcr.io/agentgateway/testbox:0.0.1`（预载清单 `test/setup/e2e-images.txt:9`）。

**外部测试包模式**：所有场景文件是 `package e2e_test`（如 `e2e/apikeyauth_test.go:3`），通过 `New(tt)`（`e2e/main_test.go:52-72`）进入框架。`TestMain`（`main_test.go:28-50`）收尾：正常时 Uninstall+Finalize；`FAIL_FAST_AND_PERSIST` 且失败时保留集群（`main_test.go:37-43`）。共享安装由 `sync.Once` 保证只装一次（`main_test.go:55`），五步 setup 依次是解析命名空间→创建安装→装 chart→apply `agent-gateway-base.yaml`→`SetupBaseGateway` 等待并解析出全局 `BaseGateway` 地址（`main_test.go:95-107`，`base/gateway.go:40-49`）。每个测试失败时自动触发 `PreFailHandler`（`main_test.go:63-67`）。

**crdgen**（`hack/crdgen/main.go`）是 CRD 代码生成器，内置四个自定义 kubebuilder 校验 marker（`main.go:28-31`：AtLeastOneFieldSet/ConditionalPolicy/IfThenOnlyFields/OverrideXValidation），由 `hack/generate.sh:56-60` 调用替代 stock controller-gen，保证 CRD schema 与 API 类型一致——e2e 里 apply 的每个 CRD 都源于这条链。

## 外部连接

- **Makefile e2e 目标链**：`make e2e-test`（`controller/Makefile:188-193`）先依赖 `testbox-docker`+`kind-load-testbox` 构建/装载 mock 镜像，再以 `TEST_TAG=e2e` 跑 go test；测试参数 `E2E_GO_TEST_ARGS ?= -vet=off -timeout=25m`（`Makefile:233`），25 分钟是按最长 setup 实测定的（其上注释明确说明）。`-race` 被刻意排除（`Makefile:231` 注释：e2e 只执行测试代码，race 需二次编译全仓且无价值）。
- **setup-kind-ci.sh 集群装配**（`controller/test/setup/setup-kind-ci.sh`，注意在 test/setup/ 而非 hack/——任务书路径有误）：`TEST_MODE` 三值决定预载哪份镜像清单（`:25`，`e2e-images.txt`/`conformance-images.txt`/`gie-conformance-images.txt`）。装配是一个手工 DAG（`main():331-357`）：建 kind 集群、编 controller/proxy 二进制、helm 预热三条边并行，再用 `await` 串联"registry 就绪+controller 编完→推镜像"、"kind 就绪→部署 metallb/registry/GW API CRD/预载镜像"、"全部就绪→helm deploy"（`step_deploy_helm:259-269` 以 localhost:5000 tag 装主 chart 并开 inferenceExtension/agentgatewayModels）。亮点：kind 集群给 kube-api-burst=500/qps=250（`:98-99`）扛 e2e 高频 apply；MetalLB 从 docker kind 网段尾部取 100 个 IP 做 LoadBalancer 池（`:117-121`），并额外切出一个 `autoAssign:false` 的 `static-conformance-pool` 单 IP（`:134-168`）给 conformance 静态地址测试，避免与并行 LB 分配竞争；本地 registry 通过给每个 kind 节点写 containerd `hosts.toml`（`:222-227`）让 localhost:5000 可达；`step_preload_images`（`:273-291`）用 `grep -vxFf` 对节点已有镜像做差集后并行 pull+load；`step_warm_test`（`:295`）用 `-exec=true -toolexec=go-compile-without-link` 只编译不链接预热 e2e 包，为正式跑测试省下编译时间。退出时 `trap cleanup_controller_images`（`:359`）清本地 registry 镜像。
- **CI 触发**：`pull_request.yml` 三个 job 对应 TEST_MODE 三值——`controller-e2e`（:161-181，`TEST_MODE=e2e` 装配后 `PERSIST_INSTALL=true go test -tags=e2e,agent,disable_pgv -v ./controller/test/e2e`，:176/179）、`controller-conformance`（:213-216，`make agw-conformance`）、`controller-gie-conformance`（:266-269，`make gie-conformance`）。失败时上传 bug report 目录（:182-186）。每个 job 末尾跑 `verify-kind-images.sh`（:181/218/271）对账镜像清单，防止"pull 悄悄失败→测试打到旧镜像"的假绿。
- **conformance 线**：`agw-conformance`（`Makefile:718-720`）以 `-tags conformance` 跑 `test/conformance/`（`conformance_test.go:1` build tag），直接复用上游 `sigs.k8s.io/gateway-api/conformance` 套件；`gie-conformance`（`Makefile:746-757`）shallow clone 上游 gateway-api-inference-extension 仓用其自身 go.mod 跑，报告落 `$(TEST_ASSET_DIR)/conformance/`。
- **golden 快照互补**：如上节所述，`crates/llm/src/golden_tests.rs`（fixture 在 `src/tests/`，`:15` 的 `fixture_path` 与 `snapshot_path_and_name`）与 `test/deployer`/`test/helm` golden（Makefile:203/210，`REFRESH_GOLDEN=true` 刷新）分别锁 Rust 翻译层与 Helm 渲染层，构成"单元快照→部署快照→集群 e2e"三级金字塔。

## 数据流

以 `TestApiKeyAuth`（`e2e/apikeyauth_test.go:14`）为例，一个场景从启动到断言的完整路径：

1. **build tag 门控**：`go test -tags=e2e` 前所有 e2e 文件不参与编译（每个文件首行 `//go:build e2e`，如 `test.go:1`）。CI 里 tag 组合是 `e2e,agent,disable_pgv`（`pull_request.yml:179`）。
2. **集群前置**：CI 由 setup-kind-ci.sh 完成 kind/metallb/registry/CRD/helm 的 DAG 装配；本地则 `make e2e-test` 前置 `testbox-docker`+`kind-load-testbox`。
3. **共享安装**：首个测试调 `New(tt)` → `agwSetupOnce.Do(setup)`（`main_test.go:55`）→ `CreateSharedTestInstallation`（`test.go:45`）经 `cluster.MustKindContext`（`testutils/cluster/kind.go:15-20`，从 KUBE_CTX 建 controller-runtime client + istio CLIClient）拿集群句柄 → `InstallFromLocalChart` 两段 helm upgrade（`test.go:181,224`）→ 轮询 Pod Ready → apply 基础 manifest → 等基础 Gateway Programmed+Accepted 并解析地址（ metallb LB IP 或 port-forward 本地端口，`base/gateway.go:99-126`）存入全局 `BaseGateway`。
4. **场景准备**：`t.Apply(manifest("apikeyauth","secured-route.yaml"),...)`（`apikeyauth_test.go:22-26`）apply 后等 Pod/Deployment Ready，Cleanup 队列挂上反删。
5. **流量探测**：`t.HTTPRouteAccepted(...)` 先等路由 Accepted（`base/test.go:130-133`→`assertions.go:102`）；`assertApiKeyResponse`→`t.Send(host, base.Expect(401))`（`apikeyauth_test.go:58-64`）→ `Gateway.Send`（`base/gateway.go:248`）以**单次 8s 超时**执行 curl（`gateway.go:262`，其上 259-261 行注释解释了为何单次超时必须远小于总预算：一个挂死的冷连接否则会吃光整个重试窗口），响应交给 `matchers.HaveHttpResponse` 判定（`gateway.go:275`），整体包在 30s 预算的 `retry.UntilSuccessOrFail` 里（`gateway.go:268-289`），成功后记录 attempts 数与耗时（`gateway.go:291-293`）。
6. **断言与收尾**：全部子测试跑完，`TestMain` 执行 Uninstall（Pod 归零断言）+Finalize 清 TempDir。任一测试中途失败：Cleanup 阶段先判 `ShouldSkipCleanup`（`env.go:195-203`），FAIL_FAST_AND_PERSIST 下跳过反删，并触发 `PreFailHandler`（`test.go:309-311`）dump 全集群状态到 bug_report/<cluster>/<TestName>/——排除 kube-system/metallb-system 等系统命名空间后（`test.go:332-338`）由 `StandardAgentgatewayDumpOnFail`（`helpers/kube_dump.go:35`，受 SKIP_DUMP 门控，5 分钟超时）落盘，CI 作为 artifact 上传。

## 设计决策

- **外部测试包（e2e_test）+ build tag 而非内联测试**：`//go:build e2e` 让 `make unit`/`go test ./...` 完全不编译需要集群的代码，单测提速且防误跑（`Makefile:176-186` 注释详细论证，甚至讨论过"改用 E2E=true 环境变量+Skip"的替代方案及其缺点——忘了打 tag 会让 unit 在无集群环境炸掉）。外部包 `e2e_test` 则强制测试只消费导出 API，框架内部可自由重构（`base` 里 `configureTest`/`interceptManifestFiles` 是包级函数变量，`base/manifest_interceptor.go:24-30`，留了注入缝却不必暴露给测试作者）。
- **Eventually 轮询而非 watch**：15 个 `Eventually*` 全部基于 istio 的 `retry.UntilSuccessOrFail`（默认预算见 `helpers/timeouts.go:11-12`：20s/50ms），而非 informer/watch。推断动机：e2e 断言对象是"最终状态"而非"事件流"，轮询实现简单、失败信息可携带完整当前状态（如 `assertions.go:76-81` 把 `gw.Status` 全量打进错误消息），且不依赖任何 controller-runtime manager 基础设施；代价是 50ms 粒度的 API 压力——这正是 setup-kind-ci 给 kube-apiserver 加 burst=500/qps=250 补丁（`setup-kind-ci.sh:98-99`）的对冲。
- **testbox 独立二进制而非每协议一个 mock 或 sidecar**：十个假后端合成一个静态镜像，一次 `kind load` 覆盖所有场景（`main.go:31-40`），chainguard static 基础使镜像极小。README 注释明言 "Single e2e helper image used by multiple tests"（`README.md:3`）——集中换取维护成本最低；对比 kgateway 原版的多镜像方案（本框架血统源自 kgateway，`hack/run-e2e-test.sh:9,53` 头注释仍留着 `TestKgateway`/`TestCookieSessionPersistence` 等 kgateway 示例名），这是有意的收敛。
- **失败即取证**：PreFailHandler + FAIL_FAST_AND_PERSIST + SKIP_DUMP 三级开关（`env.go:22-49` 注释矩阵）把"调试体验"做进框架——失败自动留集群、自动 dump、可再叠加 SKIP_ALL_TEARDOWN 单测复跑。
- **静态 IP 池拆分**（`setup-kind-ci.sh:134-168`，代码注释明言）：把 conformance 专用静态 IP 从自动分配池切走，消除并行 LB 分配的竞争窗口——注释原文 "one static-only IP that conformance can request without racing parallel LoadBalancer allocations"。
- **镜像预载对账**：`verify-kind-images.sh` 与差集预载（`:281`）双向保证"测试用的就是清单里的镜像"，CI 假绿防线。

## 新人提示

**写一个新 e2e 场景的模板**（参照 `apikeyauth_test.go` 全文 71 行的极简范式）：

```go
//go:build e2e

package e2e_test

func TestMyFeature(tt *testing.T) {
    t := New(tt)                                   // 进入框架，首次触发共享安装
    t.Run("SubCase", func(t base.Test) {
        t.Apply(manifest("myfeature", "route.yaml")) // ① YAML 落 testdata/myfeature/
        t.HTTPRouteAccepted("my-route", base.Namespace) // ② 等路由 Accepted
        t.Send("myhost.com/get", base.ExpectOK())      // ③ 发流量断言
    })
}
```

三步之外框架包办：Pod 就绪等待、失败取证、Cleanup 反删。新场景目录建在 `controller/test/e2e/testdata/<name>/`（现有 31 个目录可抄），需要 mock 后端时查 `testbox/README.md` 端口表；若涉及新 Gateway API 字段，记得 `base.WithMinGwApiVersion`（`base/test.go:48-52`）防旧 CRD 环境假失败。

**本地跑单场景**：首选 `./controller/hack/run-e2e-test.sh TestApiKeyAuth`（`run-e2e-test.sh:35-62` 用法块；脚本用 git grep 自动生成最精确的 `-run` 模式，`GO_TEST_USER_ARGS="-failfast -run '...'"` 注入见 `:702,731`）。迭代期加 `--persist`（PERSIST_INSTALL）跳过重复 make setup；调试失败现场加默认已有的 FAIL_FAST_AND_PERSIST 并 `SKIP_BUG_REPORT=true` 提速。

**调试 flakes**：注意——任务书提到的 `get-recent-flakes` 工具**在本仓不存在**（controller/hack/ 与 Makefile 均无此目标，系 kgateway 上游工具）。本仓实际手法：① `FAIL_FAST_AND_PERSIST=true go test -failfast -tags=e2e ./controller/test/e2e -run 'TestX'` 循环复跑单测（`env.go:34-36` 注释即此配方），失败自动保留集群+bug report；② `SKIP_ALL_TEARDOWN` 跑"带垃圾现场"的重复测试（`env.go:42-45` 注释指出它不如 FAIL_FAST_AND_PERSIST 适合复现 flake，因为无法在 litter 状态下单测循环）；③ 读 `AGW_E2E_TRACE=1`（`env.go:87`）输出的 setup/apply/wait 各步耗时（`base/trace.go:17-31` 的 TraceStep 计时），定位慢在哪一步；④ Send 层自带 attempts>1 或耗时>1s 的日志（`base/gateway.go:291-293`），重试细节不用猜。

**坑**：① 忘写 `//go:build e2e` 的测试文件会混进 unit 编译并在无集群环境炸（`Makefile:178-181` 注释警告过）；② testdata 路径由 `runtime.Caller` 解析，跨包复用 manifest 必须通过本包薄封装转发（`e2e/main_test.go:111-113` 的 `manifest()` 即此用）；③ KIND 节点镜像版本升级要同步改三份 images 清单 + KIND_NODE_IMAGE（`setup-kind-ci.sh:21`）+ verify 对账，漏一处 CI 假红；④ bug report 会 dump 几乎全部命名空间（`test.go:332-338` 只排除 5 个系统 ns），本地大集群注意磁盘；⑤ e2e 的 25m timeout 是全局预算（`Makefile:233`），新场景 setup 太重会挤爆整个包。
