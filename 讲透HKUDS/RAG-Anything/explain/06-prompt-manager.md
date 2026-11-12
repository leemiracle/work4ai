# 06 · prompt_manager.py —— 双语 prompt 的运行时切换与延迟加载

> 源码：`raganything/prompt_manager.py`（156 行，commit 2cd2b332），搭档 `prompt.py`（416 行，英文正本）与 `prompts_zh.py`（345 行，中文译本）。动机 issue #85（`prompt_manager.py:5`）。

## 1. 角色定位

三件套的**调度层**：`prompt.py` 定义 prompt 注册表与全部模板（英文默认），`prompts_zh.py` 提供中文对照，`prompt_manager.py` 负责在**进程运行中**把整套 prompt 原子切换语言。用户侧一句话生效：`set_prompt_language("zh")`（docstring 用例，`prompt_manager.py:7-15`）。核心设计约束写在 docstring 与锁注释里：PROMPTS 是全仓共享的全局对象、processor/query 处处直接索引（如 `processor.py:1420` 的 `PROMPTS["image_chunk"]`），切换必须**不让任何读者看到半空字典**（`prompt_manager.py:117-119`）。

**源码核实勘误**：ONBOARDING 记「prompt.py 约 40 键」，实测正则全量统计 `prompt.py` 恰为 **27 键**、`prompts_zh.py` 亦 27 键且**逐键 1:1 对齐、零缺口**（en-not-in-zh 与 zh-not-in-en 均为空集）——按源码为准。

## 2. 内部结构

模块级四件套（`prompt_manager.py:29-40`）：

- `_ENGLISH_PROMPTS = PROMPTS.snapshot()`（:29）：import 时对英文正本拍快照，此后永不变异——它是「权威回退基线」，用户即便运行中改了 `PROMPTS["x"]`，reset 仍回到这份初始快照。
- `_PROMPT_LANGUAGES`（:32-34）：语言注册表，初始只有 `{"en": ...}`。
- `_current_language`（:37）：当前语言，模块级全局。
- `_PROMPTS_LOCK = threading.RLock()`（:40）：切换互斥。

五个公开函数：

- **`set_prompt_language`**（:84-131）主入口，三步走：①归一化语言码（`_normalize_language_code` strip+lower，:43-52，非串/空串分别抛 TypeError/ValueError）；②未注册则尝试 `_lazy_load_language`（:103-106）——**zh 的延迟加载就在这里**：`from raganything.prompts_zh import PROMPTS_ZH`（:58）只在首次切换时执行 import，345 行中文模板不进默认 import 链；加载不到则报错并列出可用语言（:108-113）；③**先解析后换血**：以英文键集为骨架逐键填目标语言模板、缺失键回填英文（:120-125），整份 resolved 字典在锁内一次 `PROMPTS.swap(resolved)`（:127-128）——锁外先算好、锁内只做指针级替换，临界区缩到最短。
- **`register_prompt_language`**（:64-81）：第三方语言扩展点，ISO 639-1 码 + 与英文同键的字典（docstring 示例注册日语，:72-77）；注册时 `dict(prompts)` 拷贝防外部变异（:80）。
- **`get_prompt_language`**（:134-136）读当前语言。
- **`reset_prompts`**（:139-145）锁内 swap 回英文快照。
- **`get_available_languages`**（:148-156）：注册表 ∪ `{"zh"}`（:155）——因为 zh 未加载前不在注册表里，这里显式并集保证它始终可见（docstring :151-152 解释此怪癖）。

**搭档 `prompt.py` 的 `PromptRegistry`**（`prompt.py:13`）是配套基础设施：内部 `_data` 字典（:20）+ 两个原子操作——`swap` 整体替换（:23，"Atomically replace the active prompt snapshot"）与 `snapshot` 拷贝快照（:27），再实现完整 Mapping 协议（`__getitem__` :31、`__contains__`、`__iter__`、get/keys/items/values 等）——读者拿到的是注册表对象引用而非字典引用，语言切换换掉底层数据时引用不失效，这正是「读者无感切换」的实现根基。27 个键覆盖四类：模态分析 system prompts（IMAGE/TABLE/EQUATION/GENERIC_ANALYSIS_SYSTEM 等）、模态模板（vision_prompt 多行下标形式 `prompt.py:85-86`、image_chunk/table_chunk/equation_chunk/generic_chunk）、查询线 QUERY_* 键（QUERY_ENHANCEMENT_SUFFIX 在 `prompt.py:414`、QUERY_IMAGE/ TABLE/ EQUATION_ANALYSIS 系列被 `query.py:527-630` 消费）。

## 3. 外部连接（对齐图谱边）

- → `prompt.py`：`from raganything.prompt import PROMPTS`（`prompt_manager.py:24`），一切操作都作用在这个全局注册表上。
- → `prompts_zh.py`：仅 `_lazy_load_language` 一条延迟 import 边（:58）——这是 ONBOARDING「函数体延迟 import」条款的实例。
- → `__init__.py`：`set_prompt_language` 经 try/except 门控导出（`__init__.py:68-69`，`__all__` 动态扩展 :120-123）。
- ← PROMPTS 消费者（切换的受益面）：`processor.py:1420,1439,1454,1487`（四类 chunk 模板——多模态入库时的图谱实体描述语言）、`query.py:527,578-630`（查询增强与分析 prompt——检索时 VLM 的分析语言）、`modalprocessors.py:1091`（image_chunk）、`modalprocessors_video.py:361`（IMAGE_ANALYSIS_SYSTEM，关键帧描述）。

## 4. 数据流

**切换流**：用户调 `set_prompt_language("zh")` → 归一化 → 注册表无 zh → 延迟 import PROMPTS_ZH 入注册表 → 以 27 个英文键为序构建 resolved（zh 有 27/27，全命中；若第三方语言只译了 10 个键，其余 17 个自动英文兜底）→ RLock 内 `PROMPTS.swap(resolved)` + `_current_language="zh"`。此后所有 `PROMPTS["..."]` 索引立即拿到中文模板——**正在进行中的调用不受影响**（它们持有的是 registry 引用，且 swap 是原子替换；Python 的 GIL 保证引用赋值不撕裂）。**回交流**：`reset_prompts()` 锁内换回 `_ENGLISH_PROMPTS` 快照。**扩展流**：`register_prompt_language("ja", {...})` 后同样可切换，缺键英文兜底机制天然容忍部分翻译。

## 5. 设计决策

- **换血而非双语双表**：没有搞 `PROMPTS_EN`/`PROMPTS_ZH` 两个对象让消费者按语言选择——那样全部消费点都要改；保持单一全局 PROMPTS、整体 swap，27 个消费点零改动。代价是进程级粒度：切换影响全进程所有请求，不支持 per-request 语言。
- **先解析后入锁**：resolved 字典在锁外构建（:120-125）、锁内只 swap（:127-129），把临界区从 O(键数×模板拷贝) 压到 O(1)——RLock 保护的是 swap 与 `_current_language` 的一致性，不是构建过程。
- **英文为权威骨架**：键集以英文快照为准（遍历 `_ENGLISH_PROMPTS` :121），目标语言只能覆盖不能增键——杜绝「切换后冒出消费者不认识的新键」；反向缺口由英文兜底。
- **延迟加载 zh**：默认安装的 import 链完全不碰 prompts_zh，切换时才加载——呼应全仓「可选能力不付常价」的取向（与 resilience/audio/video 的门控同族）。
- **快照基线不可变**：`_ENGLISH_PROMPTS` 在 import 时刻固化，运行期对 PROMPTS 的就地修改（PromptRegistry 支持 `__setitem__` :35-36）不会污染回退基线。

## 6. 新人提示

1. 切换是**进程级全局**：多租户/并发服务里不同请求要不同语言，这套机制不支持——需要 per-request 语言得在调用侧选模板，别指望 prompt_manager。
2. 在 `process_file` 之前切换才影响本次摄入的实体描述语言；中途切换会导致同一文档内多模态描述语言混杂（文本线走 LightRAG 自己的 prompt，本机制管不到）。
3. 自定义语言先 `register_prompt_language` 再 `set_prompt_language`；只译核心几个键也能跑（缺键英文兜底），但 chunk 模板的 `.format()` 占位符（section_path/captions 等）必须原样保留，否则运行时 KeyError。
4. 排查「切换后某个 prompt 还是英文」：先 `get_available_languages()` 确认语言在册，再看该键是否在译文里——兜底机制静默生效，日志只记一条 "Prompt language set"（:131），不会逐键报告。
5. 想恢复出厂状态用 `reset_prompts()` 而非 `set_prompt_language("en")`——前者换回 import 时刻的快照，后者换的是注册表里的 en 引用；两者在有人运行期改过单个键时行为不同。
