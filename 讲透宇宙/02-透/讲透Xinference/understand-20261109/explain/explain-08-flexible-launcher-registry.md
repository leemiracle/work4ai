# explain-08 · flexible 模型与 get_launcher——自定义模型启动器注册机制

## 角色定位

任务书写的 `deploy/launcher/utils.py` 在本仓**不存在**——启动器机制的实际载体是 `model/flexible/` 子系统（core.py/custom.py/utils.py/launchers/）。它是 Xinference 的"逃生舱"模态：八模态之外的任何模型（YOLO 检测、HF 任意 pipeline、ModelScope 模型、图像处理函数）都能通过**注册 spec + 指向一个 Python launcher 函数**接入集群，复用下载/GPU/生命周期/虚拟环境的全套基础设施。入口三件：`FlexibleModelSpec`（`model/flexible/core.py:28`）是注册协议，`FlexibleModel`（`:81`）是运行时基类，`get_launcher`（`model/flexible/utils.py:18`）是动态加载器。

## 内部结构

`FlexibleModelSpec` 继承 `CacheableModelSpec`+`ModelInstanceInfoMixin`（`model/core.py:148` 的跨模态基类），关键字段四个：`model_uri`（权重/代码位置）、`launcher`（**点分模块路径字符串**，如 `xinference.model.flexible.launchers.yolo_launcher.launcher`）、`launcher_args`（JSON 字符串，`parser_args()` 即 `json.loads`，`:37-38`）、`virtualenv`（`VirtualEnvSettings`，复用 worker 的 venv 管线装依赖）。`Config.extra = "allow"`（`:40-41`）允许 spec 携带任意附加字段。注册走 `RegistryManager.get_registry("flexible")`（`custom.py:58-62`），与 LLM 等模态的 custom 注册同构。`FlexibleModel` 基类极简：四个只读 property（model_uid/model_path/device/config）+ 空的 `load()` + 抛 NotImplementedError 的 `infer()`（`:96-105`）——**协议就是"load 可选、infer 必须可调"**。`get_launcher`（`utils.py:18-33`）只有 15 行：`rfind(".")` 切分模块与函数名、`importlib.import_module` 导入、`getattr` 取函数；无点的裸名分支有个已知局限——`locals().get(launcher_name)` 在函数作用域里几乎永远取不到，真正可靠的是点分路径形式。

## 外部连接

上游链路完整复用主流程：REST 注册（`register_model` model_type="flexible"）→ `create_model_instance` 的 flexible 分支（`model/core.py:139-143`，注意它**不传** engine/format/quantization——flexible 没有引擎概念）→ `create_flexible_model_instance`（`core.py:133-150`）：match spec → 合并 `launcher_args` 进 kwargs → `get_launcher(launcher_name)(model_uid=..., model_spec=..., **kwargs)` 实例化。worker 侧与 LLM 同等待遇：virtualenv 安装（`core/worker.py:4475`）、GPU 分配、ModelActor 子进程隔离、`to_description()` 报告 address/accelerators（`core.py:43-51`，由 worker 启动后回填 `core/worker.py:4535-4536`）。推理入口是 REST `create_flexible_infer`（`api/restful_api.py:2985-3009`）：payload 的 `args` 列表解包成位置参数、其余键作 kwargs，直接 `model.infer(*args, **kwargs)`，返回值原样 JSON 化——**协议形状由 launcher 作者全权定义**。内置四个 launcher 在 `launchers/`：`transformers_launcher.py`（按 task 分派三种 HF pipeline 模型，`:44-75`）、`yolo_launcher.py`（UltralyticsModel，`infer` 里用 `inspect.signature` 绑参并自动 base64 解码 source 成 PIL 图像，`:35-50`）、`modelscope_launcher.py`、`image_process_launcher.py`。

## 数据流

以注册一个 YOLO 检测模型为例：①PUT 注册 spec（model_name/launcher=点分路径/launcher_args='{"device":"cuda:0"}'/virtualenv={packages:[ultralytics]}）→ RegistryManager 持久化；②launch：supervisor → worker `launch_builtin_model` → flexible 分支命中 → venv 里 `pip install ultralytics` → `get_launcher` 动态导入 → `launcher()` 工厂返回 `UltralyticsModel`（此时未 load）；③worker 创建 ModelActor、`model_ref.load()` 触发 `YOLO(model_path)` 真正初始化；④推理：POST `/v1/flexible/infer`，`args=["<base64图>"]` → ModelActor `infer` → signature 绑参+解码 → `predict` → JSON 结果原样回传。整条链上 Xinference 不理解模型语义，只提供进程/资源/协议容器。

## 设计决策

①**launcher 是"模块.函数"字符串而非类名**——函数式工厂最灵活（可按 kwargs 分派不同类，transformers_launcher 的 task 分支就是例子），且 importlib 动态导入让第三方包可以自带 launcher 而不必进 xinference 代码树；②**launcher_args 用 JSON 字符串而非结构化字段**——牺牲校验换完全自由，`extra="allow"` 同理，这个模态的定位就是"框架不管细节"；③**infer 协议裸奔**（args/kwargs 直通）而非模仿 OpenAI——flexible 模型多数根本不是生成式模型，硬套 chat 协议只会两头别扭；④内置 launcher 里 `yolo_launcher` 展示了参数适配的规范做法（signature 绑参+类型自动转换），新写 launcher 应抄它。

## 新人提示

写自定义 launcher 的最小模板：一个 `FlexibleModel` 子类（实现 `infer`，可选 `load`）+ 一个模块级 `launcher(model_uid, model_spec, **kwargs)` 工厂函数；spec 里 `launcher` 字段填 `完整包路径.launcher`。两个坑：`get_launcher` 裸名分支（无点）实际不可用（`utils.py:25-26` 的 `locals()` 拿不到模块级名字），永远用点分路径；launcher 在 worker 子进程里执行，launcher_args 里的重型依赖应写进 `virtualenv.packages` 让 worker 预装，而不是在 `load()` 里临时 pip。调试看 `to_version_info()`（`core.py:53-60`）——Web UI 模型列表里显示的 launcher/launcher_args 就来自它。
