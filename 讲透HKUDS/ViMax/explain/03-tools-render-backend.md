# 03 · tools/render_backend.py — YAML class_path 动态装配的渲染工厂

> 源文件：`tools/render_backend.py`（62 行——全仓最短的重点文件之一）。行号锚均从源码核实（commit fd4b72e7）。

## 1. 角色定位

render_backend.py 是 ViMax"可插拔渲染矩阵"的装配车间。全仓有 4 个图像生成器 + 6 个视频生成器类（tools/ 目录 9 个 generator 文件，其中 omni 一个文件导出两个类名，见 tools/__init__.py:12），分别对接 Google 官方 SDK、yunwu 网关、OpenRouter、豆包 Seedream/Seedance 等不同供应商。这个文件回答的问题是：**管线代码如何做到不认识任何具体生成器？** 答案是只认 YAML：`RenderBackend.from_config(config)` 读配置里的 `image_generator` / `video_generator` 两节，按 `class_path` 字符串动态 import 类并实例化，同时按节里的 RPM/RPD 数字自动装配双窗口限流器。换供应商 = 改两行配置，零代码改动。

一个必须先钉版的**勘误**（以源码为准，修正 ONBOARDING §3 步骤 5 的表述）：RenderBackend **只服务无头管线入口**——`main_idea2video.py:22` 与 `main_script2video.py:29` 经各管线的 `init_from_config` 走 YAML → RenderBackend 这条路。而 agent 会话路径（TUI/Web 里模型调 `vimax_render_video` 工具）**不经过本文件**：vimax_adapters.py:577-599 的 `_build_image_generator`/`_build_video_generator` 按 base_url/provider 前缀直接 new 具体类。两条装配路径并存：YAML class_path（本文件，声明式）与代码分发（vimax_adapters，环境变量驱动）。本篇讲前者。

## 2. 内部结构

62 行代码只有三个构件：

**`RenderBackend` dataclass（render_backend.py:22-27）**：两个字段 `image_generator` / `video_generator`，类型都标 `Any`——这不是偷懒，而是配合 tools/protocols.py:14-35 的 `runtime_checkable Protocol`（ImageGenerator/VideoGenerator）：任何暴露 `generate_single_image`/`generate_single_video` 协议方法的类都合规，**无需继承**任何基类。鸭子类型契约让"新增一个生成器"的最小实现就是写一个独立的类文件。

**`from_config` 类方法（render_backend.py:29-45）**：取 `config["image_generator"]` 与 `config["video_generator"]` 两节（:36-37，缺节直接 KeyError——配置错误在装配期爆掉，符合 fail-fast）；各自调用 `_instantiate(cfg, _build_rate_limiter(cfg))`（:39-40）；最后 logging.info 打印两个 class_path（:42-43）——排查"到底加载了哪个生成器"看这行日志即可。

**`_build_rate_limiter`（render_backend.py:48-53）**：节里有 `max_requests_per_minute` 或 `max_requests_per_day` 任一非空就构造 `RateLimiter`（utils/rate_limiter.py:6），否则返回 None（无限流）。configs/script2video.yaml:17-18 的 `2/50`（每分钟 2 次、每天 50 次）就是典型值——Veo/Nano Banana 的免费配额量级。

**`_instantiate`（render_backend.py:56-62）**——动态加载核心，四行：
1. `section["class_path"].rsplit(".", 1)`（:57）把 `"tools.ImageGeneratorNanobananaGoogleAPI"` 切成模块路径与类名——用 rplit 是为了容忍模块路径里带点；
2. `getattr(importlib.import_module(module_path), cls_name)`（:58）import 模块并取类；
3. `section.get("init_args", {})`（:59）把 YAML 里的构造参数原样透传（如 api_key）；
4. 若限流器非空，**注入** `init_args["rate_limiter"]`（:60-61）——生成器构造函数必须收这个可选 kwarg（tools/image_generator_nanobanana_google_api.py:19-25 实证 `rate_limiter: Optional[RateLimiter] = None`），调用方在 YAML 里永远不用写它，工厂代管。

## 3. 外部连接

**依赖上游**：`importlib`（标准库动态加载）；`utils.rate_limiter.RateLimiter`（:19）。RateLimiter 值得一句：双窗口（分钟/天）滑动限流，`acquire()`（rate_limiter.py:39）在锁内只做检查与记账、睡眠在锁外（:45-48 docstring 明说——否则等日窗口的人会阻塞所有并发调用者）；日窗口可达 24h 等待，等待后**重新检查**（另一调用者可能已占位）。

**被依赖下游**：
- `pipelines/idea2video_pipeline.py:12` 与 `pipelines/script2video_pipeline.py:18` import RenderBackend，各自的 `init_from_config`（idea2video_pipeline.py:47-60、script2video_pipeline.py:188-201）`yaml.safe_load` 后调 `from_config`，拆出 `backend.image_generator` / `backend.video_generator` 注入管线构造函数；
- `main_idea2video.py:22`、`main_script2video.py:29` 是最终消费入口（CLI 无头模式）；
- `tools/__init__.py:3` barrel 导出 RenderBackend 与全部生成器类——**这正是 `class_path: tools.XXX` 能被 importlib 解析的前提**：生成器必须在该包顶层可寻址。

**配置侧**：4 份管线 YAML 都写好了 class_path——configs/idea2video.yaml:13,23 与 script2video.yaml:14,24 用 Google 官方（`tools.ImageGeneratorNanobananaGoogleAPI` / `tools.VideoGeneratorVeoGoogleAPI`）；两份 minimax 变体（idea2video_minimax.yaml:20,27）同样指向 Google 官方生成器，只换 chat_model 供应商。注意 YAML 里的 `chat_model` 节**没有** class_path——它由管线侧的 `resolve_chat_model_config` 单独处理，RenderBackend 只管两个 generator 节。

## 4. 数据流：`python main_script2video.py` 的装配瞬间

1. `main_script2video.py:29` 调 `Script2VideoPipeline.init_from_config(config_path="configs/script2video.yaml")`。
2. `yaml.safe_load` 读入整份配置（script2video_pipeline.py:190 附近）。
3. `RenderBackend.from_config(config)`：取 `image_generator` 节 → `_build_rate_limiter` 见 rpm=2/rpd=50 构造限流器 → `_instantiate`：rsplit 得 `("tools", "ImageGeneratorNanobananaGoogleAPI")` → importlib 加载 tools 包（连带 barrel 里全部生成器）→ 取类 → `cls(api_key=None, rate_limiter=limiter)`。video_generator 同理得 VideoGeneratorVeoGoogleAPI。
4. 管线拿到两个生成器实例。此后每次关键帧生成：管线调用 `image_generator.generate_single_image(prompt, reference_image_paths=[...])`，生成器内部先 `await rate_limiter.acquire()`（分钟窗口满则睡到释放、日窗口满则睡数小时），再打 Google SDK。
5. 渲染产物落 `working_dir`（YAML 末节，script2video.yaml:33 `.working_dir/script2video`）——已存在的关键帧直接复用（idea2video_pipeline.py:59 附近的断点续跑逻辑），这就是 ONBOARDING"一切落盘"决策的执行面。

## 5. 设计决策

- **class_path 动态加载 vs 硬编码 if/else 工厂**：硬编码工厂每加供应商都要改工厂代码；class_path 方案把"选谁"完全外置到 YAML，工厂代码零增长。代价是**拼错类名直到运行时才 ModuleNotFoundError/AttributeError**，且静态分析工具（IDE 跳转、grep 调用图）看不见这条实例化边——图谱阶段这类边只能靠 YAML 与 importlib 的语义关联补齐。
- **限流器由工厂注入而非生成器自建**：生成器不感知配置解析，测试时可以传 None 或假 limiter；RPM/RPD 语义在工厂层统一，避免 9 个生成器各自实现出 9 种 subtly-broken 的限流。
- **dataclass + Any 类型 + Protocol 契约**：装配产物没有共同基类，合规性靠 protocols.py 的 `@runtime_checkable` 鸭子类型（test_generator_protocol.py 还用 `inspect.signature` 强制所有视频生成器收 `**kwargs`——管线要传 progress 回调）。这是"结构化契约"而非"名义化继承"，与 Python 生态惯例一致。
- **fail-fast 的 KeyError**：缺 generator 节直接崩，不默默降级——渲染管线没有"无生成器"的合理默认。
- **为什么 agent 路径不走这里**：vimax_adapters 需要按"会话内当前配置"（环境变量/agent.local.yaml）在运行时反复切换供应商，且渲染只是 agent 的一个工具而非整个进程的使命；为单一 turn 拉起 YAML 装配反而绕远。两条装配路径是对"配置文件驱动的批处理"与"交互式会话驱动的即时装配"两种场景的分别回应。

## 6. 新人提示

- **新增一个生成器的完整清单**：tools/ 下写类文件（构造函数收 `rate_limiter: Optional[RateLimiter] = None`，方法签名带 `**kwargs`）→ tools/__init__.py 注册 import 与 `__all__` → YAML 里改 class_path 指向它。三步缺一不可：漏 barrel 注册则 class_path 解析不到类。
- class_path 必须从**包顶层**可寻址（`tools.XXX`），写模块文件名（`tools.image_generator_xxx_api.XXX`）也能工作但不合仓内惯例——4 份 YAML 全部走 barrel 短路径。
- 改 `_instantiate` 时别动 `init_args` 的 dict 拷贝语义（:59 `dict(...)`）：YAML 解析出的 dict 是共享对象，直接往里塞 rate_limiter 会污染原始配置引用。
- RateLimiter 的日窗口等待可达小时级（rate_limiter.py:71-73），`acquire()` 期间不占锁但会挂起调用协程——Web 会话里表现为"渲染中"长时间无进度事件，属限流等待而非死锁，排查时先看日志里的 "Daily rate limit reached"。
- 测试本文件不需要真实 API key：写个假生成器类 + 内存 dict 配置即可（tests/test_image_selection.py 与 test_minimax_integration.py 已有 RenderBackend 相关用例可参考）。
- `from_config` 不读 `chat_model`、`image_selection`、`working_dir` 节——它们各有归属（resolve_chat_model_config / image_selection.py / 管线自身）；别误以为改这里能影响模型选择。
