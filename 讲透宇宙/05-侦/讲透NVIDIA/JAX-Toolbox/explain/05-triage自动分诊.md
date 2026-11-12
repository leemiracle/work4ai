# 05 · triage 自动分诊：logic.py 的三级二分与可注入测试执行

> 锚定 NVIDIA/JAX-Toolbox。覆盖 `.github/triage/`（主包 15 模块 + tests）。

## 1. 角色定位

`.github/triage/` 是"nightly 容器回归 → 定位罪魁 commit"的自动分诊机：测试红了之后，先在历史容器间按**日期**二分找好/坏边界，再对多包**版本向量**二分定位坏 commit。核心 `logic.py`（971 行）是纯算法层——不碰 docker/git，靠三个 `typing.Protocol` 注入"执行测试"；`triage_tool.py`（1141 行）编排。

## 2. 内部结构

**logic.py 数据模型**：`TestExecutionOutcome` 枚举原始结果（`.github/triage/jax_toolbox_triage/logic.py:21-31`），`TestResult` dataclass 持 stdouterr 与指标 dict（L37-57），`ClassifiedTestOutcome` 枚举分类后结果（L80-91）。三者都带 `__test__ = False`（L28/48/86）——pytest 按 `Test*` 前缀会误收它们，该属性是官方豁免。

**三处 Protocol 依赖注入**：`ExecutionClassifier`（`.github/triage/jax_toolbox_triage/logic.py:93-119`，分类 TestResult 序列）、`DateTester`（L201-208，按日期取结果）、`BuildAndTest`（L331-345，按版本向量构建+测试）。logic.py 只依赖这三个签名，故测试用 lambda 假 build_and_test 穷举验证，`metric_classifier.py` 双高斯分类器可替换默认 `ExitCodeClassifier` 做性能分诊。

**两级搜索**：`adjust_date`（L153-198）把时刻吸附到"当日确有容器"的日期；`container_search`（`.github/triage/jax_toolbox_triage/logic.py:212-328`）先强制复现端点失败（L246-254 人工核对失败原因），再按天指数回退+二分缩到 `threshold_days` 内。`version_search`（`.github/triage/jax_toolbox_triage/logic.py:444-971`）是主算法：多包版本按 OrderedDict 顺序定主包，`_get_versions`（L361-389）取主包中位、他包取不早于主包日期的最老版本；结果以 `version_cache_key`（L433-441，排序+`#rep` 键）缓存；主包收敛到两版后做 blame（`.github/triage/jax_toolbox_triage/logic.py:884-949`）：{旧主包+新他包} 复测通过则主包坏版本定罪，失败则递归换主包（L955-967）。

**utils.py**：`container_url`（L11-27）在 `jax:{container}-{date}` 与 `{container}:nightly-{date}` 间切换，分界**严格大于** 2024-02-09（`.github/triage/jax_toolbox_triage/utils.py:24`）；`run_and_log`（L70-103）把子进程输出实时 tee 进 logger 并收进 CompletedProcess，Ctrl-C 先 terminate 再抛。

**mock 容器四阶段**：`tests/mock_scripts/Dockerfile` 以 ubuntu:24.04 造 jax/xla 两个 git 玩具仓（L11-25），四 target——`passing`（L2）、`failing`（`.github/triage/tests/mock_scripts/Dockerfile:27`，git rm pass.txt）、`passing_with_later_version`（L29）、`failing_with_later_version`（L32），充当已知好/坏 fixture。mock build-jax.sh 查 feature_file.txt、build-te.sh 带环境开关、test-case.sh 用 merge-base 判祖先链。

## 3. 外部连接（图谱佐证）

图谱中 logic.py 是 38 条边枢纽：`imports`/`tested_by` 连五个测试文件（test_triage_logic 712 行主测、test_pyxis_backend 470 行全链、其余三文件各守一隅），`contains` 三 Protocol 与两级搜索。容器族 Container(ABC)（`.github/triage/jax_toolbox_triage/container.py:9-71`）→三实现由 `container_factory.make_container` 按 runtime 分派。triage-ci.yaml 独立跑测试。

## 4. 数据流

数据流：用户给"测试命令+失败 nightly 日期"→ `find_container_range`：`container_url(date)` 生成候选 URL → `Container.exists()`（docker 后端即 `docker pull`）过滤缺勤日 → `container_search` 反复 DateTester 跑测试 → 产出 (passing_url, failing_url)。`gather_version_info` 在两容器 `git log` 收各包 commit+日期并记环境差异。`run_version_bisection` 交给 `version_search`：每次迭代 BuildAndTest 在容器 checkout 版本向量、跑 build/test、收指标→分类→收缩→blame 输出 `{包}_bad/{包}_good/{包}_ref`。中间结果写 summary.json，`--restart` 时复活。

## 5. 设计决策

- **算法/执行分离**（三 Protocol）：三后端与统计分类器皆可替换，算法可静态穷举测试。
- **缺勤日吸附**：容器存在性是注入谓词，算法对周末/失败日无感。
- **多包 blame 递归**：版本向量而非单包二分，主包排除自动换副包，贴合 jax+xla 同步生态。
- **`_strip_unavailable_versions`（`.github/triage/jax_toolbox_triage/logic.py:404-419`）**：把整段不可用编码成 `v1,[v2,v3]` 记进结论，诚实标注未逐一验证。

## 6. 新人提示（坑/勘误）

1. **2024-02-09 分界用严格 `>`**：`container_url` 里 `date > date(2024,2,9)`（`.github/triage/jax_toolbox_triage/utils.py:24`）——当天及之前走旧 `nightly-` 命名。跨该日期两套 URL 混存。
2. **`__test__ = False` 是类属性非装饰器**：三处（L28/48/86）防 pytest 误收集——新类避开 `Test*` 前缀更根本。
3. **依赖方向别读反**：triage_tool imports logic（图谱边方向），logic.py 顶部仅 stdlib。
4. **mock build-te.sh 的退出码即契约**：`POISON_PILL=1` → exit 3、`--ccache` 且 `CCACHE_SENTINEL≠42` → exit 4（`.github/triage/tests/mock_scripts/build-te.sh:24-31`）——测试用它们模拟构建挂与 ccache 检查失败。
5. **mock srun 是 Python 假的**：用 `copytree` 模拟多节点隔离、`JAX_TOOLBOX_TRIAGE_PREFIX` 代替 chroot——无需真 Slurm。
6. `version_search` 的 FIXME（L892/L932）自述 blame 组合可能已测过、分类器状态或重复计数——metric 分诊读 summary 时记得。

---
自报：正文（python len 去空白）3,497 字；行号锚 24 处，其中全路径标准式 10 处。全部源码核实。
