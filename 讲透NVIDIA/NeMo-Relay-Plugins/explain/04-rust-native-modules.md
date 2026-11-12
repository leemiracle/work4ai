# 04 · example-rust-native-plugin/src/：插件能力面全景

## 角色定位

`plugins/example-rust-native-plugin/` 是**能力面最全的示例**：六个源文件演示 native（rust_dynamic）插件能注册的全部中间件表面——观测（元数据注入/订阅者/九类脱敏守卫）、请求（策略守卫/工具打标/LLM 改写）、执行（注解/并发重调/流式标记）、运行时（mark/scope/隔离栈）。定位"教学 + 插件著作文档同款"：Python worker（explain/05）与之逐钩子对应，Switchyard（explain/06）是裁剪版。加载形态：编译成共享库由 Relay `dlopen`，经 `nemo_relay_register_plugin` 符号注册（`plugins/example-rust-native-plugin/relay-plugin.toml:33-35`）。

## 内部结构

**lib.rs（102 行）——插件生命周期**：`ExampleNativePlugin` 实现 `NativePlugin` trait（`plugins/example-rust-native-plugin/src/lib.rs:25`）：`plugin_kind` 返回 `examples.rust_native_policy（`:26-28`）、`executor_config` 声明 2 线程执行器（`:30-32`）、`allows_multiple_components` 为 false 即单组件限制（`:34-36`）。`validate` 聚合配置校验与执行器诊断（`:38-49`）；`register（`:51-84`）是注册总入口——解析配置后按需装注册管控守卫（`:59-78`，一对 block/allow 条件守卫演示"插件能拦截别的插件注册"），再依次调用三个模块的 `register（`:80-82`）。文件尾部 `nemo_relay_plugin!` 宏声明导出符号（`:102`）。模块外还导出 `validate_example_config（`:20-23`）——让测试无需加载 native 宿主即可校验配置。

**observe.rs（194 行）——观测面**：九个回调——事件元数据注入器（`plugins/example-rust-native-plugin/src/observe.rs:22-31`，给事件打 transport 标签）、订阅者（`:33-37`，对非本插件发起的 scope-start 事件回发 mark，逻辑在 `:177-187`）、mark/scope-start/scope-end 三脱敏守卫（`:44-62`，共用 `sanitize_event_fields` `:129-144`，data/metadata/category_profile 全脱敏+注 plugin_tag）、工具请求/响应脱敏（`:64-85`）、LLM 请求/响应脱敏（`:87-124`——请求侧经 codec decode→redact→encode 往返 `:95-102`，响应侧只 decode 探测 `:117-119`）。核心工具 `redact_json` 递归替换命中键为 `[REDACTED]（`:155-175`）；`add_header（`:189-194`）被 requests 模块复用。

**requests.rs（114 行）——请求面**：四个注册——工具条件执行守卫（`plugins/example-rust-native-plugin/src/requests.rs:21-32`，enforce 模式且命中 blocked_tools 才拒绝）、工具请求拦截（`:33-44`，给参数对象打 `plugin_tag`/`plugin_tool`，实现 `:105-114`）、LLM 条件守卫（`:46-64`，按 content.model 拒绝 blocked_models）、LLM 请求拦截（`:65-100`）——最后一个展示头注入（复用 `add_header`）、`LlmOptimizationContribution` 归因声明（`:81-86`）、`PendingMarkSpec` 挂起标记（`:87-95`）三个高级概念。

**execution.rs（105 行）——执行面**：工具执行拦截 ×2——专发 runtime 事件（`plugins/example-rust-native-plugin/src/execution.rs:19-36`，priority=0 抢先）、注解+pending mark（`:42-62`）；LLM 执行拦截演示 `repeat_downstream` 并发重调（`:64-84`，`tokio::join!` 双发取首个成功响应 `:74-79`）；LLM 流式拦截对每个 chunk 流式改写（`:86-102`，`Box::pin(stream.map(...))` 插入 `plugin_stream: true`）。

**runtime.rs（54 行）——事件发射**：`emit_configured_runtime_events`（`plugins/example-rust-native-plugin/src/runtime.rs:9-54`）演示 mark、scope 开闭（`:23-30`）、隔离 scope 栈（`:32-51`）。

**config.rs（307 行）**：六组配置结构与 serde 默认值（`plugins/example-rust-native-plugin/src/config.rs:12-66`）；`parse` 剥离 `executor` 键再反序列化（`:141-148`——该键属于宿主）；`validate` 做未知字段 Warning + 语义 Error 双层诊断（`:150-186`；白名单 `:239-253`）。

## 外部连接

依赖 `nemo_relay_plugin` SDK crate（trait/类型/宏的全部来源）。运行时 manifest 由 `plugins/example-rust-native-plugin/relay-plugin.toml` 声明（kind=rust_dynamic、native_api=1、占位符工件由 `scripts/tasks.py:58-63` 打包时物化）。构建编排走 `plugins/example-rust-native-plugin/release.toml`（type=native、rust 1.96.1、四阶段命令 `:24-44`）。冒烟 `smoke_test.py` 与另两示例字节级相同（共享 `scripts/smoke.py` 基座）。Python/Rust worker 示例逐钩子对应本插件（`_register_observation` 对应 observe.rs，锚 `plugins/example-python-grpc-worker-plugin/nemo_relay_python_grpc_worker_example/worker.py:123-196`）。

## 数据流

一次托管 LLM 请求穿过插件：请求脱敏守卫（codec 往返）→ 条件守卫（model 黑名单）→ 请求拦截（注头+归因+pending mark）→ Relay 转发 → 执行拦截（可选并发重调）→ 流式逐 chunk 标记 → 响应脱敏。旁路上订阅者对 scope-start 回发 mark，元数据注入器补 transport 标签。回调跑在自声明的 2 线程执行器（`plugins/example-rust-native-plugin/src/lib.rs:30-32`），不占 Relay 主线程。

## 设计决策

1. **配置分组 = 注册面分组**：observe/requests/execution/runtime/registration_control 六组配置（`plugins/example-rust-native-plugin/src/config.rs:12-66`）与 register 的按需装配一一对应（`plugins/example-rust-native-plugin/src/lib.rs:59-82`）——示例即文档。
2. **enforce/observe 双模式**：守卫统一判 `mode == "enforce"` 才拒绝（`plugins/example-rust-native-plugin/src/requests.rs:28/:59`），observe 模式只记账不拦截——策略插件的通用形态。
3. **优先级编排**：runtime 事件拦截器 priority=0 抢在业务拦截器前（`plugins/example-rust-native-plugin/src/execution.rs:20`），默认业务 priority 20/30（`plugins/example-rust-native-plugin/src/config.rs:99/:109`）——数字是示例也是约定。
4. **codec 往返脱敏**：LLM 请求可能是压缩编码的，必须 decode→redact→encode（`plugins/example-rust-native-plugin/src/observe.rs:95-102`）——直接对字节脱敏会破坏编码。
5. **`validate_example_config` 独立导出**（`plugins/example-rust-native-plugin/src/lib.rs:20-23`）：配置校验不依赖宿主，CI 可在纯单测环境跑。
6. **未知字段只 Warning**（`plugins/example-rust-native-plugin/src/config.rs:296-307`）：向前兼容宿主新键；Python 版对未知字段是 Error——两示例刻意展示两种取舍。

## 新人提示

- 读码顺序：register（lib.rs）→ requests.rs → observe.rs → execution.rs → runtime.rs。
- `#[serde(default)]` + 手写 Default（`plugins/example-rust-native-plugin/src/config.rs:68-135`）保证部分配置可反序列化——加字段两处都要改。
- Rust 一律 release 构建测试（`AGENTS.md:14`）；本插件测试由 `tasks.py test` 走 `cargo test --release`。
- 改完跑 `scripts.plugins run example-rust-native-plugin` 全链验证（`README.md:111-117`）。
- 中间件名全部以 `documentation_` 开头——Relay 的注册名空间是共享的，前缀防撞。
