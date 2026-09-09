# ab.py 深度解析：同 GPU 配对 A/B 基准编排

> 源码：`tirx_kernels/bench_suite/ab.py`（587 行）｜图谱节点 `file:tirx_kernels/bench_suite/ab.py`（complexity=complex，tested）

## 角色定位：在 14 层架构中的位置

ab.py 与 run.py、ratio_diff.py 同属**基准编排层（bench-harness）**，是 run.py 的"配对实验"变体。常规回归流程拿当前 run 与 pinned baseline.json 比较，但两次 run 之间隔着的可能是不同天、不同卡、不同温度与时钟状态——GPU 基准的批间噪声足以淹没 1% 级别的回归信号。ab.py 的解法是实验设计的经典手段：**把 before/after 两个代码版本在同一块物理 GPU 上背靠背运行**，用配对消去环境变量，让对比只剩"代码本身"这一个自变量。它不是独立 CLI，而是 run.py `--ab-before REV` 分流的执行体（run.py 2339-2381 行转交 `run_ab`），产出直接喂给 ratio_diff 的配对模式门禁。

## 内部结构：7 个函数的战役流水线

图谱 contains 边只列 7 个函数，但结构紧凑：

- **`_InterferenceError` / `_PairResult`**（38-51 行）：一为"单侧被干扰、整对作废"的哨兵异常，一为一次成功配对的冻结记录（index、workload、GPU、运行顺序、attempt、双侧 payload）。
- **`_repository_state` / `_extract_before_tree` / `_copy_shared_harness`**（60-78 行）：战役完整性基建。前者对仓库做 porcelain + binary diff 三重快照；后两者用 `git archive` 把 before revision 抽到临时目录，并把 `_SHARED_HARNESS_PATHS`（bench/bench_suite/runner.py/_runtime.py）从 after 树**复制覆盖**过去。
- **`_validate_side_payload`**（107-136 行）：单侧结果的守门员——恰好一条结果、身份一致、status=ok、`physical_gpu_uuids == [gpu_uuid]` 硬校验、恰好一个 our 实现、pipeline provenance 齐备；任何干扰重试痕迹（interference_retry_count / interfered / retry_in_place）抛 `_InterferenceError`。
- **`_run_side` / `_run_pair`**（154-281 行）：单侧执行与配对循环。
- **`_aggregate_side`**（292-344 行）：把 N 个配对聚合成单侧 payload。
- **`_available_gpus`**（347-367 行）：复用 run.py 的 GpuPool 找空闲可见卡。
- **`run_ab`**（370-587 行）：战役主入口。

## 外部连接：图谱边视图

- **imports →** `impls.our_impls`（判定哪条实现是"我们的"）、`ratio_diff.build_report`（配对门禁）、`runner.AB_CURRENT_BENCHMARK_ROOT_ENV`（环境变量契约）。
- **延迟 imports →** run.py 的 `GpuPool`/`_visible_gpu_rows`/`detect_usable_gpus`/`_tir_repo_root`/`gpu_compile_profile`/`partition_workloads_by_arch`/`validate_workload_archs`（349-414 行，函数体内 import，避免模块级循环并支持 run.py 独立执行）。
- **被 imports ←** `tests/test_bench_suite_ab.py`（tested_by 边）；被 run.py 的 main 延迟调用。
- 值得注意的函数级 calls 边：测试直接调 `_run_pair`（干扰后双侧重启）与 `_side_environment`（仅 before 侧收到 benchmark root）——这两个是测试锚定的行为契约。

## 数据流：run_ab 主流程走读

1. **前置校验**（388-398）：只接受单 GPU 工作负载；**after 检出必须干净已提交**（`_repository_state` 非空即拒）；`rev-parse` 解析出 before/after 两个 commit 及其 `tirx_kernels` 目录的 git **tree SHA**（内容指纹，后面写进聚合 payload）。
2. **GPU 与架构**（402-432）：探测 TIR 依赖仓的干净度；`_available_gpus` 找空闲卡；`gpu_compile_profile` 要求同构并得到 cuda_arch；default 模式按架构分流，targeted 模式校验兼容。
3. **战役目录**（434-443）：`out_dir/ab/<时间戳>-<名字>/`，一次战役一个目录，`exist_ok=False` 防覆盖。
4. **并行配对**（461-529）：临时目录里抽出 before 树、复制共享 harness；`ThreadPoolExecutor` 给每块 GPU 一个 worker，从 `queue.Queue` 领 workload。每个 workload 走 `_run_pair`（217-281）：写出单条 workload YAML；**运行顺序按 index 奇偶交替**（`("before","after") if index % 2 else ("after","before")`，236 行）；`_run_side` 以子进程跑 `python -m tirx_kernels.bench_suite --workloads ... --max-prepare-processes 1 --ready-backlog 1 --no-probe --no-report`。这组参数是精心挑选的极简形态：单 work、单准备进程、单积压，把 run.py 的三线程流水线压成**完全串行的一次性子进程**——配对实验要的是确定性而非吞吐，任何并发调度引入的时序抖动都是污染源；`--no-probe` 因为外层 `_available_gpus` 已经探测过，重复探测只是浪费时间；子进程退出非零时读取 side.log 尾部 20 行附进异常消息，保证失败可诊断；成功后 `_validate_side_payload` 校验，任一侧抛 `_InterferenceError` 就把这次 attempt 记入 `rejected` 并 `continue` **整对从头重跑**（不做半对拼接）。`_PairResult` 用 frozen dataclass 承载成功配对：双侧 payload 在冻结瞬间定档，后续聚合只能复制不能改写。
5. **环境变量不对称**（139-151）：只有 before 侧注入 `AB_CURRENT_BENCHMARK_ROOT_ENV` 指向 after 的 benchmark root——before 树是旧代码，它不知道新的数据目录约定，这个变量让两侧行为对齐。
6. **聚合与门禁**（531-587）：战后先复核两个仓库的 `_repository_state` 与战前快照**逐字节相同**（544-547，战役期间谁动了工作树直接报错）；`_aggregate_side` 以首个 payload 为模板 deepcopy，逐对校验 `_shared_provenance` 一致（剔除 tirx-kernels 自身 git/tree 后必须全程不变——即 **TVM 等共享依赖在战役内不许变**），回填 probe/pipeline/ab 元数据与 revision/tree；双侧 payload 落盘 before.json/after.json；`build_report(before, after, paired=True)` 出报告，失败行 exit 3，workload 失败 exit 1。

## 设计决策：值得学习的模式

- **配对实验设计落到工程细节**：同物理 GPU 不靠"分配同一索引"而靠 **UUID 硬校验**（`physical_gpu_uuids == [gpu_uuid]`，119 行）——索引会因 CUDA_VISIBLE_DEVICES 重排，UUID 不会。ratio_diff 配对模式还会逐行复核双侧 UUID 一致，形成双保险。
- **交替顺序抵消漂移**：奇数 workload 先 before 后 after、偶数反着来。若 GPU 随时间缓慢降频（热漂移），两种顺序的系统性偏差方向相反，跨 workload 汇总时相互抵消——这是比"随机顺序"更强的设计，因为可复现。
- **harness 统一化**：被对比的只能是 kernel 代码，测量管线本身（bench_suite、runner）必须同一份——`_copy_shared_harness` 把 after 的 harness 覆盖进 before 树。否则你可能在比较"新 kernel + 旧计时器"与"旧 kernel + 新计时器"，结论失效。
- **干扰的颗粒度是"对"不是"侧"**：配对数据的统计效力来自同环境背靠背；一侧被干扰后另一侧的数据就失去配对意义，所以 `_InterferenceError` 丢弃整对重跑，宁可慢不可脏。
- **战役完整性用快照断言**：战前战后两次 `_repository_state` 全量对比，把"基准运行期间代码被动过"这一最隐蔽的失效模式变成显式错误。
- **共享状态的三把锁**：`rejected_lock` 保护干扰记录、`result_lock` 保护结果与失败列表、`work` 队列自带线程安全——每个 GPU worker 线程并发写汇总结构前都必须持锁，这是 ThreadPool 编排里最容易被忽略的细节；campaign.json 在所有 future 收尾后单线程写出，天然免锁。
- **聚合时共享 provenance 的减法**：`_shared_provenance` 剔掉 tirx-kernels 自身（它就是要变的），只要求其余（tvm、baselines）不变——"允许变的白名单 + 必须不变的黑名单"比一刀切更适合 A/B 语义。

## 新人提示

- 阅读切入点：从 `run_ab` 顺读，然后跳 `_run_pair` 看 attempt 循环；`tests/test_bench_suite_ab.py` 是最佳活例（图谱显示它直测 `_run_pair` 的干扰重启与 `_side_environment` 的不对称注入）。
- 易混淆点一：`rejected` 与 `failures` 是两个列表两种语义——前者是干扰导致的**丢弃的 attempt**（战役仍成功），后者是**真失败**（直接 exit 1）。聚合 payload 的 `ab.rejected_pair_attempts` 记前者，CI 看后者。
- 易混淆点二：before 树住在 `tempfile.TemporaryDirectory`，with 块结束即销毁——别指望去那里 debug，日志与 payload 都在 campaign_root 下（workloads/NNN/attempt-N/{before,after}/side.log）。
- 易混淆点三：退出码沿袭 run.py 语义（1=失败、3=回归），CI 不需要为 A/B 单写判定逻辑。
- `_aggregate_side` 里 `pipeline.interference_retry_count: 0` 不是撒谎——单 work 的子进程里干扰重试已转化为 `_InterferenceError` 整对重跑，聚合层看到的是"零原地重试"的真话。
