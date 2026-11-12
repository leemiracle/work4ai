# LogSage 新人上手指南（ONBOARDING）

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/LogSage` @ 3493d0fc · 图谱 169n/352e/8 层/12 步 · 行号锚全部源码核实

## ① 项目定位与核心价值

LogSage 是 NVIDIA 开源的 **LLM 驱动训练作业日志分析工具**：读入 SLURM/GPU 集群作业日志，完成错误抽取与去重、根因归因（硬件/软件/基础设施）、恢复策略推荐（RESTART/STOP）与故障节点 cordon（隔离）建议，目标是**减少训练作业挂死后 GPU 空转的浪费**。全部业务代码集中在 `logsage/auto_resume_policy/` 单包（9 文件约 5000 行），LLM 交互走 LangChain + `ChatNVIDIA`（NVIDIA NIM 端点），无数据库、无前端——开源版是纯分析库 + CLI；README 描述的 FastAPI 服务层属内网版，仓内不存在（见⑦）；`logsage/fetcher/` 也只在 README.md:114 被提及。

## ② 总体架构

自底向上四层（对应图谱 L04-L06）：

- **声明层**：`attribution_classes.py`（LRUCache 基于 OrderedDict（:22）、ApplicationData、ErrorAttribution 系列 pydantic 模型）；`consts.py`（BATCH_WIDTH=1000/CONTEXT_SIZE=100k/BATCH_LLM_CALLS=50、DOMAIN_SIZE=8（Hopper 8 卡/Blackwell 4 卡，consts.py:21）、五组关键词表、阈值 HARDWARE_THR_CATEGORY=40/HARDWARE_THR_LINE=60（:95-96）、哨兵串 LLM_ENDPOINT_FAILED）；`prompts.py`（24 个模板常量，:16-589）；`config.py`（环境变量开关，PERSONAL_ENDPOINT 默认 "true"，:27）。
- **引擎层**：`error_extraction.py`（1030 行抽取管线）+ `error_attribution.py`（874 行归因决策）+ `utils.py`（1622 行 56 函数，fanOut=117 全仓最高）。
- **编排层**：`log_sage.py`（459 行，现行主编排 + CLI）；`main.py`（185 行，**陈旧死入口**，见⑦）。
- **工程外围**：Poetry + Makefile、GitLab CI（内网流水线）、Ruff/mypy/detect-secrets、devcontainer。

## ③ 核心模块地图

| 模块 | 行数 | 职责 |
|---|---|---|
| error_extraction.py | 1030 | 清洗→模板聚类去重→regex+LRU+LLM 三级判定→stacktrace 重建 |
| error_attribution.py | 874 | 硬件打分→cordon 决策树（:568）→恢复策略生成 |
| utils.py | 1622 | 模板化六连、四族压缩、重试/模型轮换、LLM 输出解析 |
| log_sage.py | 459 | LLM 初始化、会话状态、三条归因入口、CLI |
| prompts/consts/config/attribution_classes.py | 602/98/37/152 | 声明面 |

## ④ 数据流/控制流

**主管线** `return_application_errors(llm, tm_text, cache_dict)`（error_extraction.py:414，541 行全项目最大函数）：截断至 100 万行（:424）→rank 前缀归一（:430）→剔除噪声行（:438-444）→迭代起点裁剪→ERROR_RE 预筛（:487）→`create_clusters` 模板聚类去重（:507）→LLM 迭代/checkpoint 判定→**三级错误确认**：regex 表 + LRU 缓存命中（:658）+ LLM 批判（:701），结果回写缓存（:774-778）→三源并集（:781）→slurmstepd 特判（:813-822）→check_real_error/check_crash 终审→按最后 checkpoint 截断（:879-887）→组装 ApplicationData（三态 :931）。

**归因路由** `get_proposed_solution_cat`（error_attribution.py:157）：LLM 给 HARDWARE/NUMERICAL INSTABILITY 打分，过阈值（:216-222）走 `get_cordon_nodes` 隔离分支（categorize_errors 打分→rank 聚合故障域→全局判定→置信度<80 或节点数>ISOLATION_COUNT=2 回退，:754；逐 node 1o1 复核→"TEMPORAL ISOLATION + RESTART"），否则走 `get_proposed_solution_policies`（checkpoint 有无 × RESTART/STOP 四套提示词，:349-356）。

**会话流**：`generate_attribution_id`（uuid4，log_sage.py:390）→`append_logs`（:407）→`get_attribution_from_attribution_id`（:303，每 user 独立 LRUCache :332-339）。

## ⑤ 环境与运行方式

- 安装：`make install`（Poetry，Python >=3.11）；测试 `make test-coverage`；lint `make lint`（Ruff）。
- 环境变量：`NVIDIA_API_KEY`/`MODEL_NAME`/`MODEL_FUNCTION_ID` 必填；`PERSONAL_ENDPOINT`/`LOGSAGE_ATTRIBUTION`/`LOGSAGE_VERBOSE`/`LOGSAGE_ISOLATION` 开关（config.py:21-27）；`MODEL_LIST` 支持模型轮换。
- 现行 CLI：`python -m logsage.auto_resume_policy.log_sage <logfile> [--isolation --attribution --verbose]`（main 在 log_sage.py:434，**不是 main.py**）。

## ⑥ 设计决策与权衡

1. **三级判定省钱**：regex 表先答、LRU 缓存次之、LLM 只兜底未知模板且结果回写缓存——同一模板错误跨作业只问一次 LLM。
2. **模板化即去重**：六连 token 化（<PATH>/<TEXT>/<HEX>/<LONG>/<NUMBER>）把日志行折叠成 pattern 再聚类，百万行压进 100k 上下文。
3. **确定性优先**：temperature=0.0/top_p=1（log_sage.py:67-68），端点失败用哨兵串显式传播而非抛异常。
4. **会话状态轻量化**：进程内 dict + 线程锁（log_sage.py:40）+ 24h 过期（:43），无持久化，重启即丢，换零部署依赖。
5. **模型轮换外置**：model.txt 存当前模型，失败时环形切换 MODEL_LIST（utils.py:75-98），跨进程共享但无锁。

## ⑦ 已知问题与勘误（重要甄别）

1. **main.py 是陈旧死入口**：`return_application_errors` 实际签名仅 3 参 `(llm, tm_text, cache_dict)`（error_extraction.py:414），main.py:87 却解包 8 元组并传 `file_path=` 关键字参数；main.py:108 对 `get_proposed_solution_cat` 传 6 个位置参数（实际 5 参）——运行必 TypeError。现行有效 CLI 在 log_sage.py:434。另 main.py 读文件用 utf-8（:72）、log_sage.py:182 用 latin-1，口径不一。
2. **README 的 API 层不存在**：README.md:54/56/73 引用的 `run_server`/`server.py`/uvicorn 启动方式仓内无对应文件；tests/README.md:22 的 `test_server.py` 亦不存在——内网版文档，开源裁掉 FastAPI 层后未同步。
3. **许可证与版本矛盾**：LICENSE.txt 是 Apache-2.0，pyproject.toml:10 classifier 却写 MIT；CONTRIBUTING.md:31 称 Python 3.9+（:82 给 conda 3.9 命令），pyproject.toml:33 实为 `>=3.11`；CONTRIBUTING.md:334 提 black，实际工具链已是 Ruff。
4. **categorize_errors 疑似真 bug**：LLM 失败分支 error_attribution.py:515-516 是无 return 的表达式语句，随后 :519 会对哨兵字符串逐字符 enumerate，正确写法应提前 return。
5. **三个聚类函数只有 create_clusters 接线**（error_extraction.py:507）；`create_drain_clusters`（:163，真 Drain3）与 `create_clusters_without_drain`（:285，多进程）是未接线替代实现，仅 :594 注释引用。utils.py:926 `compress_application_log_not_ordered_cut` 与 log_sage.py:101 `split_by_cycle` 全仓零调用；prompts.py:493 `suggest_yes_checkpoint_stop_extension` 仅存于注释（error_attribution.py:355）。
6. **tests/test_error_extraction.py 名不符实**：:19 只 import utils 的两个数字 token 化函数；真抽取测试在 test_error_extraction_comprehensive.py。
7. **环境漂移**：devcontainer Dockerfile 用 python:3.12-bullseye，CI（.gitlab/common.yml:6）与 mypy 钉 3.11。
8. 次要：utils.py:1521 归因解析返回原始全文而非解析值；error_extraction.py:820-821 slurmstepd 错误会被 append 两次；utils.py:194 docstring 阈值 10 字符、代码实为 14（:205）。

## ⑧ 新人上手路线

1. 读 `logsage/auto_resume_policy/README.md`（模块权威文档）+ 本文②③；背词汇表 consts.py + ApplicationData 九字段。
2. 主线精读 return_application_errors（error_extraction.py:414-954），用 test_error_extraction_comprehensive.py 的 FakeListLLM 用例当规格书。
3. 归因线精读 get_proposed_solution_cat（error_attribution.py:157）→ get_cordon_nodes（:568），test_error_attribution.py 的 9 类恢复场景可当决策树用例集。
4. 编排线浏览 log_sage.py（跳过 :101 的 split_by_cycle 死代码）；**不要从 main.py 读起**。
5. 动手：`make test`（FakeListLLM 无需真实 API key），再带一份真实训练日志走 CLI。

---
*行号 @3493d0fc 源码核实*
