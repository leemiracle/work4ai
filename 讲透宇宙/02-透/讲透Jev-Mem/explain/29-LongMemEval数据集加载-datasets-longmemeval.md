> 标题：LongMemEval 数据集加载器——自包含问题结构精讲 · 源文件：jev_mem/datasets/longmemeval.py（181 行）· 图谱标签：数据集层 / 入口模块

## 角色定位

LongMemEval 基准的数据入口：把 JSON 数据集解析成强类型 dataclass 链。模块头（longmemeval.py:1-8）点明它与 LoCoMo 的**结构性差异**："Each question is self-contained with its own haystack sessions"——LoCoMo 是一个 sample 一整段对话历史共享所有问题，LongMemEval 是每道题自带一捆 haystack session（干草堆），问题、答案、证据会话打包在一个条目里。这个差异决定了 benchmark 侧必须按题建记忆（而非按样本建一次），也让本加载器的输出结构成为 `jev_mem/benchmarks/longmemeval.py` 全部构建策略的输入契约。

它是 `jev_mem.datasets` 包的 LongMemEval 侧成员，与 `jev_mem/datasets/locomo.py` 平行；根目录另有 `load_longmemeval.py` 兼容垫片把它别名为老路径（见外部连接），属"包化重构后保旧 import 路径"的迁移设计。

## 内部结构

- 三个 dataclass 定义纯净数据模型：`LongMemMessage`（longmemeval.py:16-18，role+content 两字段）；`LongMemSession`（22-27，session_id+date+messages 列表）；`LongMemQuestion`（29-40）是聚合根——question_id/question_type/question/question_date/answer 五个问题域字段，加 answer_session_ids（证据会话指针）、haystack_dates/haystack_session_ids/haystack_sessions 三组干草堆字段（40）。全部字段无默认值无方法，纯数据载体
- `parse_session`（longmemeval.py:42-54）：单 session 解析——逐 turn 取 role（缺省 "user"，47）与 content（缺省空串，48）组 LongMemMessage；防御性默认值让脏数据不炸解析
- `load_longmemeval_dataset`（longmemeval.py:56-129）：主入口。Path 包装与存在性检查（68-71，FileNotFoundError 带路径）；json.load 一次读全量（73-74）；start_idx/end_idx 切片支持分段加载（56、76-78，end_idx 缺省取全长）；主循环 zip 三元组同步遍历 haystack_sessions/ids/dates（88-92）逐个 parse_session（93），边解析边累加消息与会话计数（95、97）；组 LongMemQuestion 时 answer_session_ids 用 .get 默认空列表（105）——数据集版本差异的兼容点；type 计数（112-113）；异常处理 print 后 re-raise（115-117）——报错可见但不吞；末尾打印统计块：问题数/会话数/消息数/两会均值/题型分布（119-127）
- `get_dataset_statistics`（longmemeval.py:131-158）：对已加载问题列表重算同款统计，与加载时打印的区别是返回 Dict 而非打印，且空列表有守卫（156-157 的 `if questions else 0`）
- `main`（longmemeval.py:160-177）：冒烟入口——写死相对路径 data/longmemeval_s_cleaned.json（161），加载前五题（164），打印第一题全貌（166-173）

## 外部连接

import（longmemeval.py:10-14）：json/typing/dataclasses/datetime/pathlib 全标准库。**datetime 是死导入**——全文无一处使用（实测 grep 为零），dataclass 装饰器（12）与 Path（68、161）在用。fanOut 实测五处：`jev_mem/benchmarks/longmemeval.py:25` import load_longmemeval_dataset 与 LongMemQuestion（后者在 372、506、1374、1638 四处类型注解），`jev_mem/benchmarks/longmemeval.py:2206` 主流程调用加载；兼容垫片 `load_longmemeval.py:1-9`——import 实现模块后用 `sys.modules[__name__] = _implementation`（9）把自身整体替换，注释明言 "Preserve class identity, module globals, and legacy monkeypatch targets"；`tests/test_project_layout.py:17` 校验别名对存在、25-29 行验证新路径可导入且 **pickle 身份一致**（`pickle.loads(b"cload_longmemeval\nLongMemQuestion\n.") is LongMemQuestion`）——老路径 pickle 出来的对象与新路径类是同一个类，别名替换保的是类对象身份而非再导出；`tests/test_longmemeval_jev.py:10-26` 直接构造 LongMemSession/LongMemQuestion 做时间排序测试（"later"/"earlier" 两 session 造时间型问题）。public-release-files.txt:40 与 45 分别收录实现与垫片。

## 数据流

基准跑一次的取数路径：原始 JSON（LongMemEval 官方格式）→load_longmemeval_dataset 按 start/end 切片→每条目解析成 LongMemQuestion（含全部 haystack session 的强类型展开）→benchmark 拿到后两条消费线：构建线按题把 haystack_sessions 喂进记忆系统（每题独立建/复用缓存），评测线用 question_type 分流判分（feeding 给第 25 篇讲的题型感知评测）。answer_session_ids 与 haystack_session_ids 的"证据指针/干草堆全体"二层结构是 LongMemEval 的信息检索语义——证据可定位但检索器必须自己在干草堆里找，加载器如实保留这层区分（37-39 两字段并列）。

独立冒烟线：`python -m jev_mem.datasets.longmemeval` 走 main 只加载前五题打印概览——新数据文件到手先跑这条确认格式，再进 benchmark。

## 设计决策

**sys.modules 别名替换**（load_longmemeval.py:9）是本族最值得学的一手：相比 `from ... import *` 再导出，整体模块替换让老路径下的**一切**——类身份、模块全局、甚至 monkeypatch 目标——与新路径完全同一，test_project_layout.py:29 的 pickle 一致性断言把这个性质钉死成回归测试。代价是老模块的 `__main__` 分支要单独处理（load_longmemeval.py:5-6 的显式转发），因为替换发生在 import 时而 `python load_longmemeval.py` 不触发替换。

批判性发现三处：①加载统计打印块（123-124）用 `total_sessions/len(questions)` 裸除——start_idx 越界或空切片时 questions 为空列表直接 ZeroDivisionError，而隔壁 get_dataset_statistics 同款计算有守卫（156-157）——同文件内防御口径分裂，加载器自己反而没设防；②异常处理 print+raise（116-117）双重输出且不走 logging——benchmark 侧已有 logger，这里 print 属口径不一致的小噪音；③main 写死相对路径（161）依赖运行目录在仓库根，data/ 目录又被发布检查列黑（第 27 篇的 private_path），意味着冒烟入口在公开发布包里必然 FileNotFoundError——它只是开发期工具不是用户入口，使用者需自知。

## 新人提示

三个 dataclass（16-40）两分钟读完，重点记 LongMemQuestion 十字段——benchmark 全文以它为货币流通，字段名就是检索键。然后读 load 主循环（85-117）看三元 zip 如何对齐三组平行数组，这是数据集格式的精髓：session 内容、id、日期是三个等长数组靠位置对应。

三个坑：分段加载记得 end_idx 是切片语义不含端点（78 行 data[start:end]）；遇到 ZeroDivisionError 先查切片范围是否越界产出空集（123 的裸除）；想动数据模型字段时先跑 tests/test_project_layout.py:29 的 pickle 一致性测试——它同时守着兼容垫片的类身份契约，改字段名会同时打断新路径与历史 pickle 两样东西。
