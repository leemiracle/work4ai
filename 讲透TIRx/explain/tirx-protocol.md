# tirx-protocol.md — _protocol.py：KernelModule Protocol，契约即文档

> 源码：`tirx_kernels/_protocol.py`（73 行，四文件中最短，近半是 docstring）｜图谱层：`layer:core-registry`

## 角色定位

core-registry 层的**类型基础**：定义可被 registry 发现的 kernel 模块必须满足的结构化接口 `KernelModule`（`@runtime_checkable` 的 `typing.Protocol`）。它在 14 层架构中的角色不是运行时组件，而是**契约的单一成文处**——把"kernel 模块长什么样"从 README 散文升级为可被 IDE、类型检查器、人类三方共同阅读的代码，是四篇解析里体量最小、地位却最基础的一篇。

这个文件最有趣的事实来自图谱与 grep 的交叉验证：**全库零运行时 importer**。图谱上它 0 条 imports/calls 出边，入边只有两条 `documents`（README.md 与 `.agents/skills/tirx-kernel-integration/SKILL.md`）；grep 证实没有任何 `from tirx_kernels._protocol import KernelModule`。它是"可执行的规范文档"（executable spec）——registry 用 tokenize 读 `KERNEL_META` 字面量时结构对齐但不类型依赖。它的目标读者其实有两类：人类新人，以及接入本库写 kernel 的 **AI coding agent**——`.agents/skills/tirx-kernel-integration` 技能文档把它当作"生成一个合规 kernel 模块"的机读规格来引用，Protocol 代码恰好是双方都能消费的公共媒介。下划线前缀 `_protocol` 也印证：私有模块，非公共 API。

## 内部结构

仅一个子节点：`KernelModule` Protocol（图谱标签 type-definition/protocol/interface-contract/core）。73 行里代码只占 15 行左右——"规范文件"的典型形状：docstring 承载键级细节，代码只画骨架。声明面三部分：

- **属性**：`KERNEL_META: dict[str, Any]`（公开身份）与 `CONFIGS: list[dict[str, Any]]`（配置矩阵）；
- **静态方法**：`get_kernel(**cfg)`（返回 pre-lowering 的 PrimFunc/IRModule/嵌套集合）、`prepare_data(**cfg)`（返回参数名→tensor 的 dict）、`check_correctness(outputs, **cfg)`（失配抛 AssertionError）；
- **docstring 规范**：`KERNEL_META` 必填键 name/category/runtime_cuda_archs，可选 `reference_requirements`（每项含 package/import + PEP 440 specifier 或 canonical URL + 完整 SHA 的 git 身份二选一）；`get_baselines(**cfg)` 为可选扩展。

## 外部连接

如上：0 出边、2 条 documents 入边。隐式连接更有分量——`tests/test_low_level_ir.py` 里定义了三个**同名 duck-type stub** `class KernelModule:`（本地造的测试替身，喂给 `run_kernel_test(registry=...)`），说明测试作者也把它当作"模块该长这样"的心智模型在用。真正 enforce 契约的机制分散在别处：registry 校验 `KERNEL_META` 内容，runner 依赖 `run_test/run_bench/prepare_bench`（其 docstring 是事实上的第二份契约）。

## 数据流

没有运行时数据流——它是静态契约。逻辑数据流是：kernel 作者按此形状写模块 → `KERNEL_META` 字面量被 registry 提取进索引 → CLI/bench_suite 展开 `CONFIGS` 为 (name, label) 工作负载对 → `get_kernel` 产出待编译的 TIRx 函数 → `prepare_data` 造数据 → 校验。以 rmsnorm 实况对照：

| Protocol 声明 | rmsnorm 实况 | 说明 |
|---|---|---|
| `KERNEL_META` 必填键 | ✅ 含 reference_requirements（flashinfer git+SHA、cutlass-dsl specifier） | 与 registry 校验完全对齐 |
| `CONFIGS` 带 label | ✅ 36 个配置（4 隐藏宽 × 9 批量） | label 格式 `hs{X}_bs{Y}` |
| `get_kernel` | ✅ 返回 PrimFunc | |
| `prepare_data` | ✅ 返回 (input, weights) 元组而非 dict | 轻微偏离声明 |
| `check_correctness` | ❌ 无——由 `run_test` 内部包办 | **契约漂移点** |
| （未声明）`run_test`/`prepare_bench`/`run_bench` | ✅ 全有 | runner 事实契约 |

正确性与"编译、运行"合进 `run_test` 是演进结果（runner docstring 明言 run_test 内部处理 compile→run→check），Protocol 未随之更新——registry 校验的是 `KERNEL_META` 本身，从不 isinstance 这个 Protocol，所以漂移静默发生。

## 设计决策

1. **为什么是 Protocol 而非 ABC/基类**：被约束的是**模块**而非类——模块无法"继承"一个基类，structural typing 是唯一贴合"有这些属性即合规"的类型工具。`@runtime_checkable` 留了 isinstance 诊断的口子，但要清楚它的边界：runtime 检查只验**属性存在**，不验签名与返回类型——所以即便有人拿它做 isinstance，也挡不住上面那类漂移，深度校验仍属 mypy 等静态检查器的领地。
2. **staticmethod 声明的语义**：kernel 模块里这三个是模块级函数，staticmethod 标注让 Protocol 形状与"模块属性是裸函数"这一事实精确匹配。
3. **注册即存在**：没有 register 装饰器、没有基类要求——"源码里写着字面量 `KERNEL_META`"本身就是注册（registry 扫描字面量）。Protocol 只是把这个隐式协议显式成文，让新人不必逆向 registry 才知道要写什么。
4. **键级精确的 docstring**：连 `reference_requirements` 的双身份（specifier vs git+SHA）都规定死——这份 docstring 是 registry `_validate_meta` 与 `parse_reference_requirements` 的规范源头。
5. **反面教训同样可学**：契约成文处与 enforcement 分离，漂移（`check_correctness` → `run_test`）无人监督。写接口文档型 Protocol 时，要么安排测试断言"每个样例模块满足 Protocol"（`isinstance(mod, KernelModule)` 一行就能拦住改名/删成员级别的漂移），要么接受它是快照而非法律。本库选了后者，代价是 rmsnorm 这类先行者早已跑在文档前面。

6. **面向 agent 的契约设计**：当仓库自带 agent 技能文档（`.agents/skills/`）时，接口契约的"第一读者"不再只是人。把规范写成 Protocol 而非散文，agent 拿到的是可解析、无歧义、与类型检查器共享的同一份事实——这是 AI 协作仓库里值得复制的模式。

## 新人提示

- 把它当"写一个新 kernel 的第一站"阅读，但**以 runner 的 docstring 和真实 kernel（`basic/rmsnorm.py`）为准**——两份契约有分工：`_protocol` = 发现期身份（registry 消费 KERNEL_META/CONFIGS），runner = 执行期行为（run_test/prepare_bench/run_bench）。
- 写新 kernel 最快路径：抄 rmsnorm 骨架——`KERNEL_META` 字面量 + `CONFIGS`（label 键是 CLI 与基准贯穿的标识）+ `get_kernel` + `prepare_data` + `run_test`（+ 要跑基准就加 `prepare_bench`）。
- 想验证自己的模块合规：`python -c "import tirx_kernels._protocol as p, tirx_kernels.basic.rmsnorm as m; print(isinstance(m, p.KernelModule))"` 一行可查属性级合规（签名级仍需肉眼或 mypy）。
- 别去 `import KernelModule` 做校验——库里没人这么用，类型检查器（如 mypy 结构匹配）才是它的正确消费方式。
- 易混淆：runner 里还有个同名机制的 `PreparedBenchmark` Protocol——那是"已准备基准对象"的契约，与 kernel **模块**契约是两个层次。
- 判断规范条文的效力归属：`KERNEL_META` 键与 arch 拼写由 registry 强制、`run_test` 等执行面由 runner 强制、`check_correctness` 这类无人消费的声明只是历史快照——读契约先问"谁在 enforce"，再决定信多深。
