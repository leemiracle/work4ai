# 08 · openshell-gateway 与 gateway-interceptors：组装边界与 25 方法拦截面

## 一、角色定位

这对组合一个极薄一个极重。`openshell-gateway` 是**组装边界**：main.rs 全文 10 行（crates/openshell-gateway/src/main.rs:4-10），只做一件事——把 `install_default_compute_drivers()` 注册表传给 server 的 `run_cli_with_compute_drivers`。crates/openshell-gateway/src/lib.rs:4-7 自述"server 保持后端无关，本 crate 是把一方 compute 驱动链接进网关二进制的组合边界"。`openshell-gateway-interceptors` 则是**策略外挂执行框架**：在 gRPC 路由边界统一挂钩，把 unary 请求解码成 protobuf-JSON 形状给外部策略服务做修改/校验/事后观察，再重编码回 tonic 处理器（crates/openshell-gateway-interceptors/src/lib.rs:4-10）。设计出自 RFC 0010-gateway-interceptors。

## 二、内部结构

**gateway/lib.rs 的注册表**。`install_default_compute_drivers`（:47-65）按平台装驱动：非 Windows 侧 kubernetes/podman/docker/vm 四工厂，Windows 侧 mxc + 四个"显式不支持"占位工厂（:78-102，报"unsupported on Windows"而非链接失败）。每个注册带 `detection_priority`：kubernetes=100（:184，探测 `KUBERNETES_SERVICE_HOST` 环境变量）、podman=200（:196）、docker=300（:209）、vm=u16::MAX（:219，**永不被自动探测选中，只能显式配置**）。数字越小越优先——集群里装了 docker 也会选 k8s。:511-518 的测试断言 Linux 内建注册表名字恰为 `["docker","kubernetes","podman","vm"]`（BTreeMap 排序）。另一处硬约束：网关开 TLS 时本地驱动（docker/podman/vm）必须配 `guest_tls_ca`，否则启动报错（`validate_local_driver_guest_tls` :468-479）——防"网关加密、沙箱明文"的断链。feature 陷阱也有编译期防线：`telemetry` 与 `defaults-without-telemetry` 互斥直接 `compile_error!`（:13-17），因为 Cargo 减不掉默认 feature，别名叠加会造出"名字像无遥测实际带遥测"的构建。

**interceptors 的五模块**。`routes.rs` 管"哪些方法可拦截"；`plan.rs`（1370 行）解析配置成 `BindingPlan`（:132-142：selector+phase+failure_policy+timeout+max_response_bytes+max_patches+gRPC client）；`proto_json.rs` 管 protobuf↔JSON 转码与秘密遮蔽；`runtime.rs`（1429 行）是执行引擎；`profile_source.rs` 给拦截器下发 provider profile 快照。入口两个：`initialize`（crates/openshell-gateway-interceptors/src/lib.rs:54）与带轮换 bearer-token 槽位的 `initialize_authenticated`（:64-69）——槽位可原地更新而不重建执行计划。

## 三、外部连接

上游唯一消费者是 `openshell-server`：启动时 `initialize_authenticated`（crates/openshell-server/src/lib.rs:707-713）、CLI 校验静态配置（crates/openshell-server/src/cli.rs:933）、`ServerState.gateway_interceptors`（:347-349）持有运行时。真正的挂钩点在 multiplex.rs:334-471 的 `GatewayInterceptorGrpcService`——tower Service 包装层，tonic 分发之前拦截。下游是任意 gRPC 策略服务（经 `openshell-extension-core` 的 bearer-token 通道连接）。crates/openshell-server/src/lib.rs:691-713 还把扩展 JWT issuer 与拦截器绑定：有 issuer 时为每个配置的拦截器铸 token。

## 四、数据流

请求路径（multiplex.rs:374-470）：①无拦截器配置或 `should_intercept_path` 不命中（:385）→ 直通；②收集完整 gRPC body 到内存（:392，压缩帧直接拒绝——multiplex.rs:547"gateway interceptors do not support compressed gRPC frames"）；③对 UpdateProvider 特殊补水——update 请求故意省略不可变字段，此处从库里补全 provider 身份，让策略拦截器看到完整对象又保持"update 是纯写操作"的语义（:396-407，`UPDATE_PROVIDER_PATH` :473）；④`evaluate_request`（crates/openshell-gateway-interceptors/src/runtime.rs:121-176）：ModifyOperation 与 Validate 两相依次跑，每相内每个 binding 把**秘密遮蔽后的视图**递给拦截器（crates/openshell-gateway-interceptors/src/runtime.rs:227-230 `decode_bytes_to_interceptor_json`）；拦截器可拒绝（deny 变 gRPC 错误，crates/openshell-gateway-interceptors/src/runtime.rs:258-267）或回 JSON Patch（仅 ModifyOperation 相，:269-285）；⑤补丁校验→应用→重编码，最后做"编码后 JSON 与编码前一致"的发散检查（:163-167，防转码偷偷改语义）；⑥原始 body 存进 `OriginalMutation` 扩展供 mutation_replay 用（multiplex.rs:414-418）；⑦handler 返回后若配了 PostCommit 且响应 gRPC status=0，观察响应体再评估一次（:426-466）——**事后观察失败绝不改写已提交响应**，只计数告警。

## 五、设计决策

1. **可拦截面默认拒绝，且是白名单**。`INTERCEPTABLE_METHODS`（routes.rs:17-43）精确 **25 个** unary 写方法（沙箱 4+SSH/服务 4+provider 9+config 1+policy 5+2），注释（routes.rs:14-16）钉死语义："新方法在刻意加入前不可拦截"。读方法与流方法全部不可拦——拦截器不能拖慢 Watch 流也不能看读路径。`is_interceptable`（:94-98）三重判定：服务名匹配 + 是 unary + 在白名单。启动时 `validate_interceptable_list`（:118-139）还反向校验白名单没有过期方法/混入流方法，配置漂移直接 fail-fast。
2. **秘密三层处理**。第一层：proto 字段级注解 `openshell.options.v1.secret`（crates/openshell-gateway-interceptors/src/proto_json.rs:29），拦截器视图递归清空带注解字段（`omit_secrets` :135-147），连嵌套 map 里的凭据也遮蔽；第二层：补丁路径守卫——JSON Pointer 只要与秘密字段相交（含选中包含秘密的父消息）一律拒绝（`ensure_interceptor_patch_path_visible` :101-114 + `pointer_intersects_secret` :159+），拦截器不能借 replace 父对象间接改写被遮蔽的子孙；第三层：权威管线全程保持全保真 JSON↔protobuf 往返（evaluate_request 用的是 `decode_bytes_to_json` 非 遮蔽版，crates/openshell-gateway-interceptors/src/runtime.rs:135-138），秘密从未离开网关进程，重编码不丢。
3. **失败策略按相约束**。`FailurePolicy` 只有 FailClosed/FailOpen（plan.rs:79-82），默认 FailClosed（:256）。但 PostCommit 相**强制 FailOpen**（plan.rs:690-692/842-844 两处校验）——操作已提交，拦截器挂了没理由惩罚用户；且 PostCommit 契约"不能 deny 不能 mutate"（crates/openshell-gateway-interceptors/src/runtime.rs:420-423），违规按失败策略处理。默认预算：500ms 超时、1MiB 响应、32 个补丁（plan.rs:31-33）。
4. **结果契约先验证再应用**：补丁超量、非 ModifyOperation 相回补丁（crates/openshell-gateway-interceptors/src/runtime.rs:414-417）都算拦截器违约，走失败策略而非半应用。

## 六、新人提示

- **勘误：任务书与直觉都说"24 方法"，实际数下来是 25**（routes.rs:17-43 逐条 grep 可验）。
- 别在 handler 里找拦截钩子——框架设计就是"handler 无感"（interceptors crates/openshell-gateway-interceptors/src/lib.rs:10），一切发生在 multiplex 包装层。
- `defaults-without-telemetry` 是"默认集减 telemetry"的别名，正确用法 `--no-default-features --features defaults-without-telemetry`，直接叠加会撞 compile_error（gateway crates/openshell-gateway/src/lib.rs:9-17）。
- vm 驱动优先级 u16::MAX 意味着自动探测永远轮不到它——想要 microVM 必须显式配 driver 名，这是刻意把最重的隔离留给明确选择。
- PostCommit 观察阶段 body 收集失败只打点计数（counter `..._post_commit_observation_failures_total`，multiplex.rs:444-448），不重试不回滚；想在测试里断言拦截器事后行为要看这个指标。
- `grpc_endpoint` 空时 vm/docker 工厂会用 `http(s)://127.0.0.1:{gateway_port}` 兜底（gateway crates/openshell-gateway/src/lib.rs:389-396），排查"vm 驱动为何连本机"先看这段。
