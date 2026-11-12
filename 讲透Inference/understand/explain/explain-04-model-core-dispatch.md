# explain-04 · model/core.py——八模态分发总闸 create_model_instance

## 角色定位

`xinference/model/core.py`（165 行）是模型世界的**唯一总分发点**：`create_model_instance`（`model/core.py:20`）按 `model_type` 把一次模型创建请求路由到八个模态工厂——`LLM`（`:55`）/`embedding`（`:68`）/`image`（`:82`）/`rerank`（`:95`）/`audio`（`:107`）/`video`（`:117`）/`world`（`:129`）/`flexible`（`:139`）。它不加载权重、不碰 GPU，职责是"参数归一 + 分流"：真正干活的是各模态 `core.py` 的 `create_*_model_instance`（如 `model/llm/core.py:39` 的 `create_llm_model_instance`）。之所以值得单读，是因为所有跨模态的公共语义（下载源解析、参数清洗）都收口在这 145 行里，改这里会同时影响八个模态。

## 内部结构

函数体只有三个动作。**第一，懒导入八个工厂**（`:35-43`）——全部放在函数内 import 是刻意的：这个模块被 worker/CLI 高频引用，而 audio/video/world 各自拖着 torch/diffusers 级的重依赖，模块级 import 会让 `xinference` 启动变慢一个量级。**第二，解析下载源**：`resolve_download_hub(download_hub, model_path)`（`:46-49`，实现在 `model/utils.py:786`）把 `"auto"` 或未指定解析成四个具体 hub 之一；注释特意说明"resolve 后永远不会返回 auto，所以 narrowing cast 安全"（`:45`）——这是 mypy 视角下的类型收紧。`resolve_download_hub` 的语义分层：显式 `auto` 走连通性探测；未指定时若 `XINFERENCE_MODEL_SRC` 钉了具体源直接返回；有本地 `model_path` 则无需下载（`model/utils.py:797-805`）。**第三，逐模态清洗 kwargs 后分发**，两个清洗规则值得记住：`enable_thinking` 只对 LLM 有意义，非 LLM 一律 `pop` 掉（`:52-53`）；`trust_remote_code` 只有 LLM 与 vLLM 引擎的 embedding 保留（`:70-71`），其余模态全部剥离（`:83/:96/:108/:118/:130/:140`）——防目录穿越/任意代码执行的安全默认。

## 外部连接

唯一的生产调用方是 WorkerActor 的下载管线 `_download_model_files`（`core/worker.py:3904-3985`）：worker 把它包在 `CancellableDownloader`（可取消下载器）+ 进度上报线程 + `asyncio.to_thread` 里执行（`:3928-3970`），注释点明"`create_model_instance` 是拥有全部模型特定缓存步骤（draft model/projector/ControlNet/GGUF/lightning artifacts）的既有家族分发器，本助手特意停在 virtualenv/子池/actor 创建之前"（`core/worker.py:3921-3925`）——即下载与加载的切分线就画在这条调用上。下载并发被临时压进 `HF_HUB_DOWNLOAD_WORKERS` 环境变量（`:3944-3947`）以减小 GIL 争用。文件尾部还有两个跨模态 pydantic 模型：`CacheableModelSpec`（`:148-153`，模型名+仓库 ID+revision+hub+缓存配置，供缓存预下载对账）与 `VirtualEnvSettings`（`:156-164`，virtualenv 的 pip 镜像全套参数——index_url/extra_index_url/find_links/trusted_host/index_strategy/no_build_isolation），被 worker 的虚拟环境管理器消费（`core/worker.py:80` 导入）。

## 数据流

一次典型调用：REST `launch_model` → supervisor `launch_builtin_model` → worker `launch_builtin_model` → `_download_model_files`（线程池）→ **本函数**：`model_type` 判定（LLM 默认兜底发生在 worker 层 `core/worker.py:3096`，这里 `:144-145` 对未知类型直接 `ValueError`）→ hub 解析（四次连接探测可能发生在此）→ kwargs 清洗 → 调对应工厂。工厂返回的是**尚未 load 的模型对象**（如 `LLM` 分支返回 `create_llm_model_instance` 的产物，内部已完成 spec 匹配与文件下载），随后 worker 才创建 ModelActor 并 `model_ref.load()`。`model_path` 参数全程是"本地已有权重"的短路信号：有它时 `resolve_download_hub` 返回 None（不探测网络），各工厂直接用本地路径。

## 设计决策

三个朴素但重要的选择：①**if/elif 而非注册表**——八个分支各自签名不同（image 传 `peft_model_config` 在前、audio/video/world 用关键字传 engine），用 dict 注册反而要造统一签名，分支直白胜过抽象；②**清洗逻辑放分发层而非各工厂**——`enable_thinking`/`trust_remote_code` 的删除写一次管八处，若下沉到工厂会有人漏改；③**类型安全靠 cast+注释而非 ignore**——`:46-49` 的写法把"为什么安全"写进代码，是仓内 mypy 纪律的样板。注意 `flexible` 分支不接收 `model_engine/model_format/quantization`（`:141-143`）——flexible 模型是纯 Python 函数式模型（自定义 infer 逻辑），没有引擎概念，这是八模态里唯一的"无引擎"形态。

## 新人提示

加新模态的 checklist 就藏在这个文件里：①在 `model/<新模态>/core.py` 写 `create_*_model_instance`；②回到 `:35-43` 加 import；③加 elif 分支（记得决定 `trust_remote_code` 去留）；④supervisor/worker 两层的 `_custom_register_type_to_cls` 表也要同步（`core/supervisor.py:971-1008`、`core/worker.py:1367-1416`，worker 侧有九类）。排查"为什么我的 kwargs 没传到模型"时先查这里的 pop 清单——`enable_thinking`/`trust_remote_code` 被静默吃掉是最常见的哑弹；排查下载源选错则看 `model/utils.py:808-817` 的 `download_from_modelscope`：中文 locale 环境未配置时默认走 modelscope，海外部署会意外命中。
