# 01 · Selector Protocol 与 data_selection 核心机制

## 角色定位

`data-selection/src/data_selection/` 是基准"数据选择"板块的框架核心，给十种选数策略套上统一接口，让随机基线、困惑度过滤、嵌入相似度、质量打分、LLM 裁判可在同一条管线互换。全包仅六模块：`protocol.py`（接口）、`runner.py`（编排）、`dataset.py`（归一化）、`score_cache.py`（断点续跑）、`utils.py`（IO）、`selectors/`。核心抽象全部落在 protocol.py:7-24 的 24 行里。

## 内部结构

**Selector Protocol（protocol.py:7-24）**：`class Selector(Protocol)` 只声明 `select(samples) -> list[dict]`。这是 `typing.Protocol` 结构化子类型——任何有兼容 `select` 方法的类自动满足协议，**无需显式继承**（仓内十选择器无一继承它，唯一 import 在 composite.py:6 且仅为类型标注）。docstring 约定：所有策略参数（含 k）在 `__init__` 配置；返回值每条附 `meta` dict（分数/种子/来源），随样本落盘供审计。

**Runner 编排（runner.py:11-70）**：`run_selection` 四步——构造 DatasetConfig → read_jsonl 归一化 → 解析 k（None 取 `selector.k`、int 包单元素列表、Sequence 转列表，L40-45）→ 按选择器类型分叉。关键一行 L47：

```python
is_score_based = getattr(type(selector), "_score_based", False)
```

取**类属性**而非实例属性。`_score_based = True` 是分数型选择器类体里声明的哨兵（如 deita_quality.py:18），两个作用：其一，多 k 优化——排序结果对任意前缀有效，L49-58 只跑一次 `max(k)` 再 `all_selected[:kk]` 截断，把十 GPU 小时的打分摊到多预算档；其二，随机型不走截断（L59-70 每 k 独立跑）——随机截断会破坏种子确定性。输出路径由 `_resolve_output_path`（L73-77）处理：`{k}` 占位符替换，否则扩展名前插 `_k`。

**ScoreCache（score_cache.py:21-79）**：append-only JSONL，每行 `{"idx":0,"scores":{...}}`。构造全量加载内存 dict（L29-39）；`put`/`put_batch`（L49-67）**立即落盘**；`missing_indices(total)`（L73-75）返回差集，选择器只对 missing 调昂贵打分器，每批打完立刻持久化，中断重启从断点继续。

**DatasetConfig（dataset.py:7-51）**：dataclass 持三个键名。`format()` 归一化为 `messages`：conversations 键存在时三分支——`role/content` 标准对、`from/value` ShareGPT 对（L51 `_role_map` 把 human/gpt 映射为 user/assistant）、嵌套 messages 数组；否则退回 instruction/output（L40-46）。返回 `{**sample, "messages":[...]}`，原字段保留。

## 外部连接

上游吃 JSONL 数据文件；下游选中子集交 LlamaFactory 微调（根 README"Training"节）。`utils.py:11-34` 的 read/write_jsonl 与 extract_text 是共享 IO 层；main.py:6-21 是五条样本的冒烟脚本。核心四件套零第三方依赖；模型驱动档选择器外依 `dataflow`/`dataflex` 两包。

## 数据流

```
input.jsonl --read_jsonl--> format 归一化（带 messages）
  --> selector.select [ScoreCache: missing 才打分，每批落盘]
  --> 结果挂 meta --write_jsonl--> output{_k}.jsonl
多 k：分数型 max(k) 一次排序+截断；随机型逐 k 独立 select
```

## 设计决策（含批判）

1. **Protocol 而非 ABC**：外部策略零侵入接入，代价是 runner.py:12 形参只能写 `Any`，静态检查放弃这层防护。
2. **哨兵不进 Protocol**：协议保持最小面，截断优化是 runner 与选择器间的私有约定。批判：新增选择器忘写 `_score_based` 不报错，只是默默失去多 k 优化（贵而不错）。
3. **ScoreCache 以下标 idx 为键**：隐含"同一文件同一顺序"假设——输入行序变化或换文件复用缓存路径，分数会静默错位，无内容哈希校验，是断点续跑最脆一环。
4. **截断正确性前提**：分数型必须纯按分数排序。依赖 k 本身的策略（如 k-center）不可截断——`DiversityKCenterSelector` 确实没设哨兵，说明作者意识到了。

## 新人提示

入门：跑 `uv run python main.py` 看 RandomSelector，再读 examples/random.py 与 runner.py（78 行全读），protocol.py 当字典查。动手任务：给 ScoreCache 加输入文件 sha1 前缀校验修复错位风险；写一个 `_score_based=True` 的自定义选择器验证截断路径。铁律两条：策略参数全进 `__init__`；meta 必须挂。
