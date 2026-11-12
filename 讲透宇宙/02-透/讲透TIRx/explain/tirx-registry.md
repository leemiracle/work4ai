# tirx-registry.md — registry.py：KERNEL_META 注册协议的唯一权威

> 源码：`tirx_kernels/registry.py`（374 行）｜图谱层：`layer:core-registry`｜fan-in 4

## 角色定位

在 14 层架构中，registry 与 runner、`_protocol` 同属 **注册与运行时核心层**——库级基础设施。它回答一个看似简单的问题："这个库里有哪些 kernel？"难点在于：kernel 模块的 import 是**重操作**（要拉起 torch、TVM、乃至 CUDA），列个清单绝不能把整棵 kernel 树 import 一遍。

它的解法构成存在理由：**kernel 公开身份的唯一权威是模块源码里的 `KERNEL_META` 字面量**。registry 只提取这个字面量建立索引（零导入），真正使用时才导入那一个模块，并校验运行时元数据没有撒谎。docstring 首段就是这句话的契约化表述。

## 内部结构

图谱 contains 边 13 个子节点，按流水线分四层：

- **发现层**：`discover_categories`（枚举含 `__init__.py` 的类别子包，跳过 bench/test/bench_suite/experimental）→ `_iter_kernel_module_names`（递归类别包，跳过 `utils` 等共享辅助子包与 `_` 前缀）→ `_candidate_sources`。
- **提取层**：`_literal_kernel_meta` —— 用 `tokenize` 流定位模块级 `KERNEL_META = {...}` 赋值：扫描 NAME token `KERNEL_META` + OP `=`，按括号深度收集 token 至深度 0 的换行，`untokenize` 后 `ast.literal_eval` 求值。全程不 parse 整个 AST、更不执行模块；重复赋值直接报错。
- **校验层**：`_validate_meta`（字段类型、非空、`category` 必须等于所在目录、arch 匹配 `sm_[1-9][0-9]*(a|f)?` 且去重、`parse_reference_requirements` 校验参考依赖）+ `_build_kernel_index`（组装 name→`KernelRecord`，重名抛 ValueError）。
- **导入层**：`kernel_index`（lru_cache 公开入口）→ `_import_record`（importlib 真导入 + 运行时 meta 与索引逐项比对）→ `load_kernel` / `discover_kernels` / `check_workload_imports`。

`KernelRecord` 是 frozen dataclass，六字段（name/category/runtime_cuda_archs/reference_requirements/module_name/source_path）恰是"精确导入一个 kernel 模块"所需的最小身份。文件尾部还内嵌 CLI（`--list --format text|json|benchrun --category --arch --strict`）：text 给人看（名称/类别/arch/配置数对齐表），json 给机器读（meta+configs 全量），benchrun 每行输出 `name|label|python -m tirx_kernels.bench ...` 供基准套件直接当任务清单调度——一个文件同时是库和命令行工具。

`reference_requirements` 的解析委托给同层的 `reference_requirements.py`：每项要求 distribution `package`、Python `import` 名，再加 PEP 440 `specifier`（如 `"==4.8.0.dev0"`）或指向 canonical URL + 完整 commit SHA 的 `git` 身份二选一。这套声明是正确性对照的"陪审团名册"——runner 的 `run_kernel_test` 在跑之前先查它，未满足就 `SkipTest`，让测试结果区分"kernel 错了"和"参考实现没装"。

## 外部连接

- **出边**：imports `tirx_kernels` 包自身与 `reference_requirements`（`parse_reference_requirements` 被 calls 3 次）；tested_by 两个测试文件。
- **入边**（15 条）：`bench_suite/run.py`（`main`/`load_config_dir`/`partition_workloads_by_arch` 三个入口消费它）、`tirx_kernels/test/__main__.py`（正确性 CLI）、`tests/test_registry.py`（5 个专项测试：runtime_cuda_archs 校验、源码索引精确性、运行时一致性、参考依赖一致性、非 canonical arch 拒绝）、`tests/test_correctness.py`。注意 runner 对 registry 是**函数内延迟导入**（`run_kernel_test` 里才 `from tirx_kernels.registry import ...`），图中无 runner→registry 的 imports 边——避免基础设施互相锁死。

## 数据流

**列举流**：`python -m tirx_kernels.registry --list` → `discover_kernels` → `kernel_index()` → `_source_snapshot()` 对全部候选源文件取 `(category, relname, path, mtime_ns, size)` 指纹 → `_build_kernel_index(snapshot)`（lru_cache 按指纹缓存）逐文件 `_literal_kernel_meta` → 校验通过则入索引。benchrun 格式再展开 `CONFIGS` 输出 `name|label|命令行` 三元组供基准套件调度。缓存失效的走查很直观：编辑任何一个 kernel 源文件 → 它的 `mtime_ns` 变了 → 整个快照元组不等 → lru_cache miss → 索引全量重建。删掉一个 kernel 或改名 likewise——不存在"缓存里留着幽灵 kernel"的中间态。提取器本身也值得信任：tokenize 工作在 token 层而非文本层，函数体内的注释、字符串里出现的 `KERNEL_META = ...` 都不会匹配到"模块级 NAME + 紧随 OP `=`"的模式；命中后 `ast.literal_eval` 只认字面量容器，连 `os.environ` 伪装都过不去。

**加载流**：`load_kernel("rmsnorm")` → 索引查 record（无则 KeyError）→ `importlib.import_module("tirx_kernels.basic.rmsnorm")`（**只导入这一个模块**）→ 取运行时 `KERNEL_META` 重新 `_validate_meta`，并逐项比对 name/runtime_cuda_archs/reference_requirements 与源码索引——strict 模式任何不一致即抛 ValueError，非 strict 记 warning 返回 None。

**bench 前置流**：`check_workload_imports(workloads)` 把基准配置里的 kernel 名去重后逐一 `load_kernel(strict=True)`——在长计时开始前把 import 失败（缺依赖、坏 meta）全部暴露，而不是让基准跑到一半才炸。`bench_suite/run.py` 的 `partition_workloads_by_arch` 则纯靠索引的 `runtime_cuda_archs` 字段分桶，同样零导入。

## 设计决策

1. **tokenize 零导入提取**。不用 `ast.parse` 解析全文件、不用 importlib 执行模块——解析期连 TVM 都不碰。`ast.literal_eval` 保证只接受字面量，安全且强制"meta 必须可静态读出"。
2. **快照指纹缓存失效**。lru_cache 的 key 是全量 `(路径, mtime_ns, size)` 元组：editable install 下改任何 kernel 源文件，指纹变化自动触发重建——缓存正确性不靠约定靠数据。
3. **双重校验防漂移**。源码字面量与运行时值各校验一次再互相比对，堵死"import 时动态计算 meta"（如按环境拼 arch 列表）的路——公开身份必须在源码里写死且运行时如实。
4. **早期重名检测**。索引构建期重名即 ValueError，而不是等两个 kernel 在不同 CLI 里撞名才发现。
5. **strict 双模式**。strict=True 是 CI import 门禁（第一个失败就炸），strict=False 是宽松列举（坏 meta 降级为诊断信息，不拖垮整个索引）。

## 新人提示

- 阅读切入点：先跑 `python -m tirx_kernels.registry --list` 看真实输出，再回头读 `_literal_kernel_meta` 那 40 行。
- 调试配方：索引行为异常时用 `python -m tirx_kernels.registry --list --strict`——第一个坏 meta 会带着完整诊断炸出来，而不是淹在 warning 里；`kernel_index(strict=False)` 的诊断信息也可以直接 `_log.warning` 里捞。
- **写 KERNEL_META 必须纯字面量**：f-string、变量拼接、函数调用都会让 tokenize 提取失败或 `literal_eval` 报错（落入 diagnostics，strict 下炸给你看）。
- `category` 字段必须与目录名一致，arch 必须是 canonical 形如 `sm_100a`——`100` 或 `SM_100A` 都会被正则拒收。
- 易混淆点：`kernel_index()`（纯源码索引，返回 KernelRecord）与 `discover_kernels()`（导入模块，返回 module）是两个世界；`load_kernel` 与后者的区别是"精确一个"而非"全部匹配"。
- 源码 L123 `item.string in ")]} ".rstrip()` 其实就是 `")]}"`——一个可读性欠佳但正确的小写法，别被绕住。
