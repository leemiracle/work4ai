# 12 · 端到端验证闭环：ReAct 双臂与集成示例

## ① 角色定位

这个仓最核心的架构主张是「决策与执行分离」：Router 只选模型不调模型，宿主自己执行并回报。三份文件把主张钉成可运行的证据：`tests/react_agent.rs`（234 行）是 Rust 臂——纯内核侧最小 ReAct 宿主，`#[test]` 直接断言路由轨迹；`tests/react_agent.py`（167 行）是 Python 臂——同一剧本经 PyO3 桥跑一遍；`examples/python_integration.py`（101 行）是接入者向的最小闭环示例（无 ReAct/测试框架）。docstring 各自明言「模型由脚本化 mock 扮演，不发真实网络」（react_agent.rs:5、react_agent.py:5、python_integration.py:13-14）——端到端验证的是**协议闭环**（route→report→排除→换模），不是模型质量。

两臂同剧本不是冗余：Rust 臂证明内核自身闭环成立；Python 臂证明 PyO3 边界（08 篇 convert 层）没破坏闭环——同一剧本在桥另一端重演出同一轨迹，两臂互为正确性证人。

## ② 内部结构

**Rust 臂**：PROFILE 内嵌 TOML（react_agent.rs:12-18）——passthrough 算法+memory state+两个 target。`MockBackend::invoke`（`:24-33`）是剧本核心：`fast-local` 一律 Err("unavailable")，prompt 含 "Observation:" 则回 Final Answer: 42，否则回 Action: calc[21*2]。`parse_turn`（`:49-67`）把输出解析成 LlmTurn 枚举（`:36-46`），`run_tool`（`:85-91`）断言只有 calc 工具并真算乘法。`ReActAgent`（`:93-215`）四方法恰是宿主契约清单：`route`（`:120-144`）调模型前构造 RouteRequest 问 Router 并记 trace；`report`（`:146-152`）把 `decision.route_id` 原样带回 Feedback——注释点明这是「state 把 query 与 report 对上」的钥匙；`call_model`（`:154-180`）最多 4 次尝试，失败 report Unavailable 后重试（下一轮 snapshot 会排除该目标）；`run`（`:183-214`）主循环最多 4 步。测试体（`:217-234`）三段断言：algorithm_name、answer=="42"、**trace 精确等于三元组**——`:229-232` 行内注释就是闭环逐步解说：passthrough 首选 fast-local→mock 不可用→report 后 state 排除→第二次选中 strong-cloud→后续走可用模型。

**Python 臂**：与 Rust 逐段镜像——PROFILE 换 dict 形态（react_agent.py:24-28，替 08 篇 profile_from_dict 线做实测）；MockBackend/Unavailable（`:31-43`）；`parse_turn` 用元组代替枚举（`:61-70`）；ReActAgent（`:80-151`）同样的结构，差异在 `route_sync`（`:101-105`）与 `report`（`:107-115`）。入口 `main()`（`:158-163`）+`build_router`（`:154-155`），docstring（`:8-9`）给出直跑命令。

**pytest 接线**：`tests/test_react_agent.py:5` 先 `pytest.importorskip("openjiuwen._openjiuwen")`——扩展没编译就整文件跳过而非报错；`:10-19` 复刻 Rust 测试同名断言（answer==42、trace 三元组逐项相等）。`tests/conftest.py:7-8` 把 `python/` 插到 sys.path 最前，`from react_agent import`（test_react_agent.py:7）因此可达。

**集成示例**：python_integration.py 的 PROFILE（`:22-26`）注释说与 config/edge.toml 等价且加了 ttl_secs/max_entries，演示 dict 直传。`invoke_with_routing`（`:44-85`）是「宿主调用模板」精华：本地 `exclusions` 列表（`:47`）每次请求带上（`:48-53`），失败时 `Feedback.ok(selection, ..., outcome=Outcome.UNAVAILABLE)` **并** `exclusions.append`（`:62-72`），成功报 OK（`:74-82`）；`:29-30` 注释另立纪律——SESSION_ID/AGENT_ID 必须 route 与 report 同组。`main`（`:88-97`）跑两次调用，第二次注释（`:95`）预告亲和效果。

## ③ 外部连接

Rust 臂经 `crates/runtime/Cargo.toml:33-34` 的 `[[test]]`（name="react_agent"，path="../../tests/react_agent.rs"）挂进 runtime crate——virtual workspace 根目录不是 package，测试必须由成员认领；`cargo test` 即跑（runtime 在 default-members 内）。Python 臂依赖 09 篇门面（Router/Feedback/Message/Outcome 重导出）与 pyproject.toml:27-29 的 `pythonpath=["python"]`。三份文件的 Feedback 形态恰好覆盖 08 篇 convert 层三条路径：Rust 臂用原生 `Feedback::ok`+改 outcome（react_agent.rs:148-151）；Python 臂用**位置参数 typed 构造器**（react_agent.py:109-115）；示例用 **classmethod Feedback.ok(selection,...)**（python_integration.py:63-70）——后者自动从 selection 提取 route_id（types.rs:673-682），Python 臂则没传（对比 Rust 臂 react_agent.rs:149 特意 clone）。

## ④ 数据流

以 Python 臂一次运行为例：`build_router` → from_config(dict) → `run("What is 21 * 2?")`：第 1 步 route_sync → passthrough 选 targets[0]="fast-local" → MockBackend 抛 Unavailable → report_sync(UNAVAILABLE) → memory state 把 fast-local 写进该 RoutingKey 排除表 → 第 2 次尝试 route → snapshot 带排除 → 选 strong-cloud → mock 回 Action → 宿主跑 calc 得 42 → Observation 拼回 prompt → 第 2 步（仍 strong-cloud）→ mock 见 Observation 回 Final Answer: 42 → report OK（affinity 建立）→ 断言 trace==["fast-local","strong-cloud","strong-cloud"]。Rust 臂逐点相同，仅 Feedback 携带 route_id 使 query/report 关联更完整。示例臂多演示一层：第二次 invoke 时 affinity 命中。

## ⑤ 设计决策与权衡

1. **mock 剧本而非真模型**：被验证的是路由协议（选择→失败→排除→换模→成功），模型质量与路由无关；mock 让测试确定可断言（trace 逐项相等），CI 无网络无 GPU。代价是「真模型下其他算法的表现」不在保障范围——那靠 tests/test_x_router_live.py 单独承担。
2. **trace 三元组是最小而完备的闭环断言**：只断言选中序列，就把「首选顺序/排除生效/亲和保持」三个行为一次锁死（react_agent.rs:226-233、test_react_agent.py:15-19）。两臂断言逐字相同——diff 两文件即可确认桥无行为漂移。
3. **双臂 Feedback 形态故意不同**：typed 构造器与 classmethod ok 都在真代码里出现，把 08 篇宽容 API 的两条路径各自钉进回归。Python 臂缺 route_id 也有教学价值：memory state 按 RoutingKey 工作，缺席不破坏本剧本；但换 BanditStore（11 篇按 route_id 配对）就必须用 Feedback.ok(selection,...)——示例用的正是后者。
4. **importorskip 而非 fail**（test_react_agent.py:5）：仓库定位是「未 maturin develop 也能开发纯 Python 半边」（09 篇），跳过与之一致；Rust 臂 cargo test 天然自足。
5. **示例即文档**：python_integration.py:13-14 直说「接入真实业务时把 call_model 换成你的模型客户端即可，路由相关代码不需要改动」——可运行文件替代接入文档。

## ⑥ 新人提示与坑

- **先 `maturin develop` 再跑 Python 臂**：`python tests/react_agent.py` 在扩展缺失时会 ImportError（`python/openjiuwen/__init__.py:117-123`）；pytest 则静默 skip（test_react_agent.py:5），**skip 不等于 pass**——CI 要盯 skip 计数，否则桥坏了也全绿。
- **Rust 臂文件位置有迷惑性**：`tests/react_agent.rs` 在仓库根 tests/ 下但不属于任何根 package——没有 `crates/runtime/Cargo.toml:33-34` 的挂接不会被编译；新加根级 Rust 集成测试照此认领。
- **route_id 是 state 配对的钥匙**：Python 臂的 `report`（react_agent.py:107-115）没带 route_id 在 memory 后端没事，照抄到 BanditStore 场景会 unknown 剧增（bandit_store.py:296-297）——生产代码学 python_integration.py:63-70 的 `Feedback.ok(selection, ...)`。
- **passthrough 的「首选」= targets[0]**：trace 首项是 fast-local 只因它在 models 列表首位（react_agent.rs:16-17）；5 路算法是同构 stub（已知勘误），换算法名不改本剧本行为。
- **SESSION_ID/AGENT_ID 稳定性**（python_integration.py:28-30 注释）：route 与 report 用不同标识，排除/亲和全失效且无报错——最安静的坑。
- **README 目录树漏 stage_router.toml**（已知勘误）：config/ 实有四份配置文件。
