# 讲透 nv-one-logger（NVIDIA/nv-one-logger）

NVIDIA 统一遥测 Python 库：span/event/attribute 数据模型 + 多后端导出（OpenTelemetry / Weights & Biases / JSON 文件·日志）+ PyTorch Lightning 无侵入接入。五包 monorepo，核心承诺"遥测故障永不打断训练进程"（safe_execution.py:4）。

## 全链状态表

| 阶段 | 状态 | 产物/数据 |
|---|---|---|
| deepwiki | ✅ 完成 | `deepwiki/`（6 章 + 子页，INDEX.md + _coverage-check.md） |
| understand 图谱 | ✅ 完成 | 仓内 `.understand-anything/knowledge-graph.json`：560 节点 / 1341 边 / 11 层 / 12 步 tour / 校验 0 issues；fingerprints 153 文件 @ c382dd51 |
| onboarding | ✅ 完成 | `onboarding/ONBOARDING.md` 8 节，60+ 行号锚（源码逐条核实） |
| explain | ✅ 完成 | `explain/` 4 篇（六节结构，1500-2500 非空白字符、锚 12+） |
| 勘误 | ✅ 完成 | 见下方 8 条源码级实证勘误 |

## explain 索引

- `explain/01-core与PEP420命名空间.md` —— 五包共存机制、OneLoggerProvider 单例、api/core/internal 四子包
- `explain/02-training_telemetry与TrainingRecorder.md` —— 1068 行主实现、_TrainingState/生产力度量、标准 span 词汇表
- `explain/03-exporter插件与三大后端.md` —— entry-points 发现、OTel/W&B 双实现（子进程异步）、JSON 系、Lightning 三路径
- `explain/04-测试体系与工程链.md` —— 31 文件 382 测试、五子流水线、Poetry+semantic-release、内网源流实证

## 源码级实证勘误（8 条）

1. **语言预期推翻**：不是 C++ 日志库，是纯 Python 五包 monorepo（Poetry + src-layout，pyproject.toml 五份实证）。任何"one-logger C++"的说法均不成立。
2. **空 stub 甄别**：`one_logger_training_telemetry/src/nv_one_logger/training_recorder.py` 是 **0 字节空文件**（wc -l 实证），真身在 `training_telemetry/api/training_recorder.py`（1068 行）。文件名高度误导，按图索骥必踩坑——上游兼容遗留占位。
3. **上游拼写错误 singletong**：测试工具函数名 `reset_singletong_providers_for_test`（tests/nv_one_logger/training_telemetry/api/utils.py:17 定义，conftest.py:12,20、test_training_recorder.py:646,649、test_training_telemetry_provider.py:29,61,64、integration_test.py:451,460 共四处文件引用）——正确拼写 singleton。引用时须用错误拼写否则 import 失败。
4. **PEP 420 命名空间对 scanner 全盲**：`src/nv_one_logger/` 无 `__init__.py`（no_init.md 明令禁止添加，且该警告自身还有 "init.py"/"directorty" 两处笔误），五发行版共享顶层命名空间，静态 import 分析跨包不可见——图谱阶段 imports 边大量依赖人工补扫核对，依赖真值以五份 pyproject 为准。
5. **标准 span 名大小写不一致**：`TESTING_SINGLE_ITERATION = "TESTING_SINGLE_ITERATION"`（spans.py:63）枚举值是大写字符串，而同族 18 个值全是小写 snake_case（如 :59 `TRAINING_SINGLE_ITERATION = "training_single_iteration"`、:61 validation 用小写）。按名字过滤 span 时此键大小写敏感，易漏。
6. **CI/构建双轨**：根 .gitlab-ci.yml include 五子包流水线（GitLab 体系），Makefile 的 GIT_URL 指向内网 gitlab-master.nvidia.com/hwinf-dcm——GitHub 仓是开源镜像而非源头；.github/workflows 不存在。
7. **wandb 异步版是子进程而非线程**：WandBExporterAsync 用 `mp.Pipe(duplex=True)` + daemon 子进程（wandb_exporter.py:362-363），且 wandb 初始化前临时改 WANDB_RUN_ID/WANDB_SERVICE 环境变量（:57-61）避免与用户自己的 wandb 记录互相干扰——"多进程双后端"的准确含义是 sync/async 两实现 + 进程隔离，不是多线程。
8. **hook_trainer_cls 覆盖面有限**：docstring 明言只拦截**同步** save_checkpoint 路径，异步 checkpointing 不在 hook 范围（pytorch_lightning.py:194-195）；需要存档全遥测必须走 OneLoggerPTLTrainer 子类（:251）。

## 快速上手

源码仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nv-one-logger`（commit c382dd51）。阅读顺序：README 的 How to use → core/api/one_logger_provider.py（95 行）→ default_recorder.py docstring → spans.py/events.py 标准词汇表 → training_recorder.py 的 _TrainingState 段（:95-184）。
