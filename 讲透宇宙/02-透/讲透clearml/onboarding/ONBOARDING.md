# ClearML SDK 导览（ONBOARDING）

> 基于图谱（1944 节点/4435 边/16 层/16 步）撰写，锚定 `df0d7477`（SDK 2.1.12，`clearml/version.py:1`）；行号锚均经源码核实，冲突以源码为准。

## 1. 项目定位

clearml 是 allegroai 开源的 MLOps 实验管理 SDK（Apache-2.0），核心承诺"两行代码接入"：训练脚本调一次 `Task.init()`（`clearml/task.py:280`），即自动捕获指标/超参/模型/输出/git diff/依赖并上报 clearml-server（开源自托管）。仓库即一个 pip 包：`setup.py:110` 注册五个 console 命令，`clearml/__init__.py:3` 起 barrel 导出公共符号。

与同类差异：
- **vs wandb**：wandb 以手动 log 为主；clearml 主路径是框架 monkey-patch 自动绑定（L09），手动上报（`clearml/logger.py:169`）是补充。
- **vs mlflow**：mlflow 是记录库+工具箱；clearml 的 Task 是服务端一等实体，可 clone 远程重放，流水线/HPO/调度内建。
- 数据面：版本化 Dataset（`clearml/datasets/dataset.py:125`）+面向企业版 DataView 的 hyperdatasets。

## 2. 总体架构（16 层）

- L01 Vendored(40)｜上游库冻结拷贝｜`clearml/utilities/pyhocon/__init__.py`
- L02 Core Utilities(37)｜并发/IO/进程设施｜`clearml/utilities/process/mp.py:515`
- L03 Configuration(20)｜conf 装载与环境判定｜`clearml/config/__init__.py:75`
- L04 Backend API Client(69)｜会话/鉴权/端点封装｜`clearml/backend_api/session/session.py:67`
- L05 Storage(11)｜多协议存储抽象｜`clearml/storage/helper.py:3774`
- L06 Backend Interface(33)｜后端对象映射｜`clearml/backend_interface/task/task.py:82`
- L07 SDK Public API(8)｜用户编程门面｜`clearml/task.py:152`
- L08 Data Management(9)｜Dataset/HyperDataset｜`clearml/hyperdatasets/core.py:27`
- L09 Framework Bindings(24)｜框架自动插装｜`clearml/binding/import_bind.py:8`
- L10 Automation(16)｜流水线/HPO/调度｜`clearml/automation/controller.py:43`
- L11 CLI & Router(17)｜命令行与本地代理｜`clearml/router/router.py`
- L12 Examples: Frameworks(96)｜九大框架样板｜`examples/frameworks/pytorch_mnist.py`
- L13-L14 Examples(103)｜数据/流水线/报表｜`examples/cicd/`
- L15 Documentation(14)｜API 文档与教程｜`docs/clearml.conf`
- L16 Build & CI(11)｜打包与质量门禁｜`setup.py:39`

## 3. 核心数据流：Task.init() 到指标落库

1. **`Task.init()`**（`clearml/task.py:280`）：进程单例+模式分叉——`clearml/task.py:578` 查 `running_remotely()`（定义于 `clearml/config/__init__.py:144`）；本地开发走 `clearml/task.py:4403` 的 `_create_dev_task`。
2. **环境抓取**：`clearml/backend_interface/task/repo/scriptinfo.py:650` 收集 git/入口/包信息，配 `clearml/backend_interface/task/repo/freeze.py:9`（pip_freeze）生成依赖快照，由 `clearml/backend_interface/task/populate.py:20` 灌入新 Task——"clone 即复现"的物理基础。
3. **指标上报**：`clearml/logger.py:200` 转发到 Reporter；`clearml/backend_interface/metrics/reporter.py:276` 为后台线程消费者，`reporter.py:230` 批量取事件交 Metrics。
4. **事件信封**：基类 `clearml/backend_interface/metrics/events.py:25`（MetricsEventAdapter），`events.py:161`（ScalarEvent）等子类转 API 请求。
5. **批量落库**：`clearml/backend_interface/metrics/interface.py:85`→`:153`（先传文件再打批量）→`:290` 构造 `AddBatchRequest` 后 `self.send()`（`clearml/backend_interface/base.py:144`→`clearml/backend_api/session/session.py:651`）。图片先经 StorageHelper 上传 output_uri，URL 写进事件。
6. **退出兜底**：`clearml/task.py:4998`（_at_exit）flush 残余事件；`clearml/task.py:2728`（mark_started）对应起点。

## 4. 关键模块深潜

**task.py 门面**：5711 行全仓第一大文件。`clearml/task.py:152` 的 `class Task(_Task)` 继承 backend_interface 实现，构造函数以 private 参数做创建保护（`clearml/task.py:237`）。要点：`connect` 族（`clearml/task.py:2082`）配 `clearml/utilities/proxy_object.py` 的 LazyEvalWrapper 实现"参数先记后放"（远程时被服务端反向覆盖）；单例+atexit 让忘 close 也不丢数据。

**backend_api/session 通信层**：`session.py:67` 的 `Session(TokenManager)` 管 API 语义（`:99` 最低 "2.9"，登录后协商升至 v2_23），`request.py`/`response.py`/`datamodel.py:168` 是自动生成模型基座（165 请求/168 响应类），`clearml/backend_api/api_proxy.py:10` 懒加载 `clearml/backend_api/services/__init__.py:8` 等 42 个服务对象。DevOps 二开从 `clearml/backend_api/session/client/client.py:509`（APIClient）和 `:98`（StrictSession，失败即抛）进门。

**backend_interface 对象映射**：`base.py:189`（IdObjectBase）叠加带 id 实体语义；控制台捕获在 `clearml/backend_interface/logger.py:11`（StdStreamPatch 劫持 stdout/stderr）+ `clearml/backend_interface/task/log.py:214`（TaskHandler 转 log 事件）。

**automation/controller**：`clearml/automation/controller.py:43`（PipelineController，5634 行）把 DAG 步骤映射成服务端 Task 派生树，`:1055`（start）支持本地/远程执行；`clearml/automation/job.py:516` 是节点执行体；`clearml/automation/__init__.py:3` 另导出 HPO 家族。

**binding 机制**：钥匙是 `clearml/binding/import_bind.py:8`（PostImportHookPatching）——替换 `builtins.__import__`（`import_bind.py:18`），为"将来才 import"的框架注册回调；回调用 `clearml/binding/frameworks/__init__.py:24`（_patched_call）挂补丁：`pytorch_bind.py:55` 劫持 `torch.save`、`tensorflow_bind.py:1966` 接管 Keras 序列化、`xgboost_bind.py:42` 包装 save_model、`:49` 包住 `xgb.train`；模型 IO 统一走 `frameworks/__init__.py:58`。这是"没写上报代码却有指标"的全部原因。

**vendored 哲学**：pyhocon/pigar/plotlympl/gpu/jsonmodels 均为冻结拷贝——裸机开箱即用+免疫上游漂移，惯例不改不细读。

## 5. 测试与质量体系（特殊结构，钉版）

**本仓无 tests 目录**——全仓无 `tests/`、无 `test_*.py`；`setup.py:75` 排除的 'tests' 是不存在目录（内部 monorepo 残留）。质量体系三替代：
1. 静态门禁：`.github/workflows/codeql-analysis.yml` 仅存质量 workflow 且只 cron 定时；`git_issue_to_pylon.yml` 只是 issue 同步。
2. examples 即冒烟：199 个示例兼文档与集成测试面。
3. 真实单测在 allegroai 内部仓；契约靠 services 自动生成。

二开含义：无本地单测，验证=跑 examples 样板+对照服务端 UI。

## 6. 周边生态

- **clearml-server / clearml-agent**：两个独立开源仓——前者=docker 服务端（契约即 L04 services 来源），后者=worker 执行器（`clearml/config/defs.py` 定义 `CLEARML_TASK_ID` 等注入变量协议）。
- **allegroai 企业版**：`clearml/backend_interface/task/populate.py:521` 生成的补丁优先 `from allegroai import Task` 再回退 clearml——allegroai 命名空间是企业版专有 SDK（功能超集），hyperdatasets/DataView 全量能力亦依赖企业版；前身 trains（`docs/clearml.conf:44` 留有 "allegroai-style"）。
- **框架集成面**：PyTorch/TensorFlow/XGBoost/sklearn/LightGBM/CatBoost/FastAI/MXNet + matplotlib 捕获 + argparse/click/hydra 绑定，全按需懒挂；另有 `docs/clearml-task.md` 等三份 API 文档。

## 7. 新人上手路径（按 16 步导览排 4-6 周）

- **第 1 周（T01-T02）**：读 `README.md` 与 `setup.py`（核心仅 20 行 requirements，云存储全是 extras）；跑通 `examples/frameworks/pytorch_mnist.py`；精读 `clearml/task.py` 的 init/connect 主干。
- **第 2 周（T03-T06）**：对照 `docs/clearml.conf` 读配置层；clearml-init 生成配置；按第 3 节数据流走一遍 Session/services。
- **第 3 周（T07-T09）**：从 `reporter.py` 后台线程模型读起（`mp.py` fork 原语）；手写 artifact 上传看 StorageHelper 分发；`examples/datasets/` 练版本化。
- **第 4 周（T10-T12）**：跑 `examples/pipeline/`；在 `import_bind.py` 打断点看补丁挂载时机；对照 T15 示例验证"哪行触发哪个补丁"。
- **第 5-6 周（T13-T16）**：读 CLI 四子命令与 `clearml/router/`；实操入门 notebook；回读 `docs/errata_breaking_change_gcs_sdk_1_11_x.md`。

## 8. 常见坑与勘误（按危害排序）

1. **APIClient 路径差一层**：常被写成 `backend_api/session/client.py`——实际 `clearml/backend_api/session/client/client.py:509`（client 是目录）。
2. **官方 errata 自带笔误**：`docs/errata_breaking_change_gcs_sdk_1_11_x.md:17` 写 `from clearml import Task, ImportModel`，但 SDK 无 `ImportModel`（`:30` 实际用 `InputModel`，`clearml/model.py:1635`）——照抄会 NameError。
3. **cicd 示例双漂移**：`examples/cicd/run_clearml_checks.yml:70` 用 `--script task.py`、`:73` 调 `check_clearml_task_running.py`，两者都不存在，实际为 `example_task.py`/`check_remotely_runnable.py`（README 才对）。
4. **Lightning 分两代命名空间**：新代 `examples/frameworks/jsonargparse/pytorch_lightning_cli.py:2` 用 `lightning.pytorch.*`，旧代同目录 `pytorch_lightning_cli_old.py:26` 用 `pytorch_lightning.*`，API 不通用。
5. **tour 节点名漂移**：导览 T09 的 `hyper_dataset.py`/`hyper_dataset_data_view.py` 不存在——HyperDataset 在 `clearml/hyperdatasets/core.py:27`，DataView 在 `data_view.py:247`。
6. **孤立数据双拷贝**：`examples/hyperdatasets/qa_entries_sample.json` 与其 `samples/` 副本无脚本硬引用，只能手动传 `create_qa_entries.py` --qa-json。
7. **scriptinfo 位置反直觉**：三件套在 `backend_interface/task/repo/` 子目录而非 task/ 直下。
8. **StorageHelper 双层迷路**：`helper.py:2549` 与 `:4133` 各有一个 `get_local_copy`（内部 `_StorageHelper` 与外层壳 `:3774`），先认类再追。
9. **api 版本协商**：`session.py:99` 的 "2.9" 只是最低线，运行期按服务端升至 v2_23，特性判断必须走 `check_min_api_version()`；另 tests 排除项是摆设（见第 5 节）。

## 自检报告

- **字数双口径**：不计空格总字符 6,994（达标 5000-7000）；纯汉字 1,271+英文词/代码锚 496（锚密度所致）。
- **锚数量**：`路径:行号` 精确锚 61 个（去重）+文件级锚 17 个，合计 78，满足 60+ 硬性要求。
- **核实方式**：行号锚全部经 `grep -n`/`sed -n` 在 `df0d7477` 现场核实（与图谱 meta 一致），零凭记忆；勘误 9 条中 7 条任务书给定+本文复核，第 5/8 条为新发现；冲突（tour 节点名、cicd YAML、errata 文档）一律以磁盘源码为准。
