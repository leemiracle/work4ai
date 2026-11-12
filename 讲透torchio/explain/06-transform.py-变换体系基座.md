# 06 · `src/torchio/transforms/transform.py`：变换体系基座

## 一、角色定位

`Transform`（`transform.py:69`，`torch.nn.Module` 子类）是全部 50 余个变换的唯一父类，图谱 fan-out 视角下它是骨架枢纽（fan-in 46、被继承路径覆盖 transform-framework/spatial/intensity 三层）。它把三件事做进基类：**输入归一化**——任意类型输入统一包装成批再分派（"用户永远只调 `transform(x)`"）；**参数采样与历史**——`make_params`/`apply_transform` 两段式把随机性与执行分离，`AppliedTransform`（`transform.py:29`）记录可序列化参数，支撑可逆变换与逐元素回放；**逐实例增强**——`per_instance` 体系让批内每个样本独立采样参数（v2 的招牌特性）。文件同时定义两个语义分支 `SpatialTransform`（:668）与 `IntensityTransform`（:677），是写新变换时的父类分岔口。

## 二、内部结构

693 行，五段：

**记录与注册**：`AppliedTransform` dataclass（:29-43，name/params/include/exclude 四字段）；模块级 `_TRANSFORM_REGISTRY`（:47）经 `__init_subclass__`（:132-134）自动登记每个子类——CLI 的 `transform` 子命令（`cli.py:221`）就是靠它按名字查类。

**构造与运算糖**：`__init__`（:113）五个关键字参数：`p`（概率，范围校验 :123-125）、`copy`（执行前深拷贝，Compose 内层置 False 免重复拷贝）、`per_instance`（:118，默认 True）、`include`/`exclude`（按图像名限定作用域）。`__add__`（:173）映射 `+` 为 Compose、`__or__`（:183）映射 `|` 为 OneOf，且智能展平已有组合（:179-181）。`__repr__`（:158）只显示非默认参数。`_warn_if_noop`（:136）在无参构造的增强变换上警告 no-op——v2"随机性须显式请求"设计的用户提示层。

**forward 主流程**（:212-254）：先 `deepcopy`（:220-221）→ `_wrap`（:222，把任意输入包成 SubjectsBatch 并拿到 unwrap 函数）→ 批级概率门（:227，`rand >= p` 直接原样返回；逐元素门激活时跳过批级门）→ `make_params`（:229）采样 → `apply_transform`（:230）执行 → 写历史（:235-244：全元素被门掉则不记，避免回放时无谓的重采样）→ unwrap 并向可携带历史的输出传播（:245-253）。

**十个 forward 重载**（`transform.py:194-210`）：Subject/Image/Tensor/ndarray/SimpleITK/Nifti1Image/dict/ImagesBatch/SubjectsBatch 九个类型化 `@overload` 加 :212 的实现——ONBOARDING 勘误确认是 10 个签名而非图谱摘要的 11 个。

**包装/解包族**（模块级函数）：`_wrap`（:487）按 match 分派；`_wrap_scalar_input`（:519）把 Tensor 包成 `ScalarImage`、ndarray 先 `torch.as_tensor` 补通道维（:527-529）；`_wrap_dict`（:547）处理 MONAI 风格 dict；八个 `_unwrap_*`（:605-665）负责逆变换回原类型，`_unwrap_sitk`（:632）与 `_unwrap_nifti`（:648）还要重建几何元数据。`_collect_init_params`（:566）沿 MRO 收集 init 参数默认值，服务于 `__repr__` 与 `to_hydra`（:459，导出 `hydra.utils.instantiate` 兼容配置）。

**逐实例体系**（:256-393）：两个能力开关 `supports_per_instance_params`（:256）与 `supports_per_instance_p`（:267，仅形状保持变换可实现，:271-274 的 docstring 说明原因）；激活判定 `_per_instance_active`（:278，批>1 才生效）与 `_per_instance_p_active`（:291）；`_resolve_n`（:300）决定采一套还是 B 套参数；`_keep_mask`（:309）抽逐元素布尔门；`_mask_identity`（:330）把被门掉元素的参数替换为恒等值（如加性参数的 0.0）；`_tag_batched`（:366）往 params 里写 `_batch_size`/`_batched_keys`/`_keep` 簿记键，`SubjectsBatch.unbatch` 据此把历史拆给各 Subject（`batch.py:18` 的 `_BATCH_META_KEYS`）。

## 三、外部连接

- **上游**：`SubjectsBatch`/`ImagesBatch`（:22-23，批世界与单样本世界的交界）、`Subject`/`Image`/`ScalarImage`（:24-26）。
- **下游**：spatial 14 文件 + intensity/label 23 文件全部继承它；`Compose/OneOf/SomeOf`（`compose.py`）组合它；`inverse.py:15/64`（`get_inverse_transform`/`apply_inverse_transform`）消费它写的历史；`cli.py:223` 读它的注册表；`to_hydra` 被 `tests/test_hydra.py:8` 验证。
- **参数语言**：`Choice`（`parameter_range.py:27`）与 `_ParameterRange`（`parameter_range.py:143`）提供"标量确定/二元组均匀/逐轴/分布"四形态统一采样——`is_constant`（`parameter_range.py:186`）支撑 no-op 警告。

## 四、数据流

`transform(subject)` 一次调用的完整路径：

1. `Transform.forward`（:212）→ 深拷贝输入（:220）。
2. `_wrap`（:487）→ `SubjectsBatch.from_subjects([subject])`（:502），记下 `_unwrap_subject`。
3. 概率门（:227）：单元素批不激活逐元素门，走批级 `rand < p` 判定。
4. `make_params`（:395，基类空实现，子类覆写）→ 如 `Motion` 采样 rigid 参数表（`motion.py:84`）。
5. `apply_transform`（:408，抽象，子类必须实现）在 5D 张量 `(B,C,I,J,K)` 上执行——docstring（:415-418）明确要求用负索引 `-3/-2/-1` 取空间维。
6. 写 `AppliedTransform`（:236-244）→ `unwrap`（:613 `batch.unbatch()[0]`）→ 历史传播回 Subject（:245-253）。

批输入时步骤 2 跳过包装，步骤 4 走 `_resolve_n`（:300）采 B 套参数，子类的向量化实现（08 篇）保证逐元素等价——这正是 12 篇门禁守护的契约。

## 五、设计决策（含批判）

**"一切输入皆批"**（`docs/concepts/transforms.md` 自述）是全文件最具野心的决策：单 Subject、裸 Tensor、甚至 SimpleITK 图像都被升维成批，变换实现者只需写一种 5D 向量化代码。收益：批增强一次 kernel 调用、GPU 友好、逐实例语义天然成立。代价是**包装税**——单样本路径每次调用都要 `from_subjects`/`unbatch` 往返（:502/:613），轻量变换的批处理收益可能被包装开销吃掉。

批判四点。其一，**`make_params`/`apply_transform` 两段式的纪律靠约定维系**：在 `apply_transform` 里继续采样的子类（如 Noise，见 `tests/conftest.py:26-29` 的说明）会破坏逐元素回放等价性，基类无法强制，只能靠 12 篇的门禁测试网住——所以门禁白名单外的变换要自觉。其二，十个 forward 重载（:194-210）是类型注解的胜利也是维护负担：新增输入类型要同时改 `_wrap_scalar_input`（:519）、match 分派（:495）与对应 unwrap，漏一处即静默走 `case _:` 报 TypeError。其三，`copy=True` 默认深拷贝（:117）对大卷是显著开销，Compose 深知这一点做了顶层一次拷贝的内层豁免（docstring :95-98），但**用户手写循环逐个调用时拷贝税照交**，文档提示不足。其四，`_TRANSFORM_REGISTRY`（:47）以类名作键，用户自定义类撞名内置类会静默覆盖注册表。

## 六、新人提示

1. 写新变换的最小清单：选 `SpatialTransform` 或 `IntensityTransform` 父类 → 实现 `make_params`（随机性全放这里）与 `apply_transform`（纯函数式用 params）→ 需要逐实例就覆写两个 `supports_per_instance_*` 属性（:372 的 `Spatial` 是范本）。
2. 调试"变换没生效"先看两处：`p` 概率门（:227）与 no-op 警告（:136）；无参构造的增强变换是恒等的，必须给范围参数。
3. `include=['t1']`/`exclude=['seg']`（:450 `_get_images`）比在子类里 isinstance 过滤更通用——历史记录还会带上作用域（:239-240）。
4. 查历史：`subject.applied_transforms` 是 `AppliedTransform` 列表（:29），`params` 可 JSON 序列化（:354 `_serialize_param`），打印它是最快的参数对账方式。
5. 想让变换可逆：覆写 `invertible`（:429 返回 True）与 `inverse(params)`（:434），参考 `Spatial.inverse`（`spatial.py:617`）。
