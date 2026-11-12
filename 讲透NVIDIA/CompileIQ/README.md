# 讲透 NVIDIA/CompileIQ

NVIDIA 编译器控制项超参优化框架（Python 前端 + amber 编译版 NSGA-III 引擎，ask/evaluate/tell 循环调优 ptxas/nvcc/Triton 等工具链控制项）。本目录是全链知识库产物：DeepWiki 抓取 + 源码知识图谱 + 中文 onboarding + 12 篇级精讲。

## 状态表

| 环节 | 状态 | 产物 | 备注 |
| --- | --- | --- | --- |
| deepwiki | ✅ | `deepwiki/`（INDEX + 全页 + wiki_full + _coverage-check） | 既有产物；快照为 1.0 socket IPC 时代口径，见勘误 #1 |
| understand 图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json` | **582 节点 / 920 边 / 12 层 / 13 步 tour / 0 issues**，fingerprints 262 文件 @ `4df0d5c8` |
| onboarding | ✅ | `onboarding/ONBOARDING.md` | 8 节，汉字 3008，锚 112（终验 0 坏） |
| explain | ✅ | `explain/` 6 篇 | 每篇 1852-2151 非空白字符、六节结构、锚 12-29；六篇锚合计终验 0 坏（224 唯一锚含 onboarding） |

图谱节点类型分布：file 179 / function 181 / class 109 / document 55 / step 30 / config 24 / pipeline 3 / schema 1。

## explain 索引

| 篇 | 主题 |
| --- | --- |
| `explain/01-core搜索引擎-Search门面与ask-evaluate-tell.md` | ciq.py 1695 行 Search 门面、tell 三重校验零残留、RuntimeObjective pickle 契约、range 遮蔽内建名 |
| `explain/02-backends与amber引擎注册.md` | entry-point 注册（1.1 取代 socket IPC）、16 格 whl 矩阵、manifest 三级溯源、_libciq 手动缓冲管理 |
| `explain/03-搜索空间体系-原语provider与resolver.md` | 四原语、加密 provider、LocalSearchSpaceBin 协议独立实现甄别、latest-tag 三级容错缓存 |
| `explain/04-编译器调优示例五族.md` | ptxas 溢出最小化 / nvcc 编译计时 / triton 双变体 / nvbench 对接 / cutile 单脚本 |
| `explain/05-xla_ciq深水区-dump到TMA到bundle.md` | XLA dump 索引、HLO→CUDA 序 TensorMap、TMA box 枚举（16 字节对齐+seed 钉扎）、protobuf bundle |
| `explain/06-agent-skills与发布工程.md` | 7 技能+三件套安装器、dev 组装/验证/守卫、CI 15 job fail-closed、测试反向锚定 CI 配置 |

## 勘误清单（全部源码级实证）

1. **DeepWiki 快照的 `compileiq/core/` 模块已不存在**。deepwiki/ 页面大量引用 `compileiq/core/core_comms.py`、`core_types.py`（socket IPC 搜索核心）与 `tests/integration/test_core_integration.py`——当前仓（`4df0d5c8`）无 `compileiq/core/` 目录，CompileIQ 1.1 已用 amber entry-point 架构取代 socket IPC（`AGENTS.md` Project Overview："CompileIQ 1.1 replaced the original search core and its socket IPC with `amber`"；`docs/install.md:14` 同证）。读 deepwiki 时凡涉 core/ 与 IPC 的段落一律以源码为准。
2. **test_backends.py 测试函数数实测 87 非 95**。`tests/unit/test_backends.py` 共 2417 行、`grep -c "def test_"` = 87。fake 类有两种口径：fake **引擎**恰 3 个（模块级 `FakeSealedBackend:40` + 测试内局部 `RecordingBackend:2263`/`ExhaustingBackend:2323`），另有 4 个 fake **worker**（`SynchronousWorker:146` 及其三个子类）——"95 测试 + 6 fake"与"只建 3 fake"是口径混写，精确说法是 87 测试 + 3 fake 引擎 + 4 fake worker。
3. **图谱 step 层 Makefile 覆盖 13/55**。Makefile 共 55 个 target，图谱 step 节点只收 13 个开发高频项（install/validate/lint/test-*/build/docs/help 等）；search-space 与 booster 发布流水线约 26 个 target 未入 step 层——按图谱 step 层做"全部构建入口"分析会漏发布线。
4. **native-runtime-wheels/ 的 16 个 whl 是 Git LFS 指针**（`.gitattributes` filter=lfs，指针文件头 `version https://git-lfs.github.com/spec/v1`）。clone 后必须 `git lfs pull` 才有真轮子；`dev/materialize_native_runtime.py:29` 的 `_reject_lfs_pointer` 专门防呆这一点。以文件存在判断运行时可用会踩坑。
5. **xla_ciq_bundle.proto 在子项目 schemas/ 而非仓根**。proto 源在 `examples/compilers/xla_ciq_example/schemas/xla_ciq_bundle.proto`；仓根 `schemas/` 只有 `search-space-manifest-v1.schema.json`。批甄别笔记"schemas/xla_ciq_bundle.proto"是相对子项目根的路径，按仓根找会扑空。
6. **nvbench_example/CMakeLists.txt 归 document 节点而非 pipeline**。图谱将其归型为 document（外部 CMake/nvbench 消费的构建定义，无本仓执行语义）——甄别原则是"有无执行语义"而非"是否构建文件"；它是全仓唯一 CMakeLists，不要按 pipeline 检索。
7. **"5 个 checkpoint 数据类"的精确口径**：4 个 Pydantic 数据类（`ciq.py:173/236/270/281`）+ 1 个 `UserWarning` 子类（`ciq.py:152`）。说"5 个数据类"会把警告类也算进去。
8. **ci-pass 的 fail-closed 有一处显式例外**。"任何 job 缺席即失败"须带限定：PR 上允许跳过 `verify-and-test-complete-wheel`（`ci.yml:647-651` 的 `ALLOWED_SKIPS`，注释解释 PR 接受 compose 阶段的 Linux x86_64 轮），main 与 release tag 则必须全跑——引用该设计时别漏这个条件分支。
9. **ptx_spill.py 与 w8_spill.ptx 是两个文件**。脚本是 `examples/compilers/ptxas_example/ptx_spill.py`（优化入口，objective 在 :24），负载是同目录 `w8_spill.ptx`（2772 行故意溢出内核，被 `ptx_spill.py:21` 引用）——两个"spill"命名相近极易混淆。
10. **docs 计数口径**：`docs/` 下 19 篇 markdown（最深 `search_strategy.md` 435 行、`workers.md` 385 行）+ 2 个 rst（index/api）+ conf.py；"19 篇文档"指 md 不含 rst。

## 阅读路径

新人：`onboarding/ONBOARDING.md` 第 1-4 节 → `explain/01` → `examples/single_objective.py`。
深入：`explain/03`（搜索空间）+ `docs/search_strategy.md`；XLA 用户加 `explain/05` + 子项目 `workflow.md`。
发布/CI 维护者：`explain/06` + 本页勘误 #3/#4/#8。

（本 README 状态表与勘误基于 commit `4df0d5c8` 源码核实；字数口径：onboarding 按汉字计、explain 按非空白字符计。）
