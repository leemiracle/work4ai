# 02 Attempt 数据总线：attempt.py + buffs 变换链

## 角色定位

`garak/attempt.py`（458 行）定义全仓唯一数据载体：`Attempt` 及三层信封 `Message → Turn → Conversation`。probe 造 prompt、generator 产输出、detector 打分、report 落盘，四方全通过同一 Attempt 对象交换——garak 的数据总线。`garak/buffs/` 是总线上的变换器族：不改 probe 代码，把一批 Attempt 的 prompt 加密/改写/翻译后再送模型。图谱 L01 层，被 probes/detectors/harnesses/report 四方向引用。

## 内部结构

三层信封：**Message**（`attempt.py:21`，dataclass）字段 `text/lang/data_path/data_type/data_checksum/notes`（:46-51），附件懒加载 property `data`（:53-67，首次访问才读文件+mimetypes 猜型+sha256），setter 强制设过 data_path 不可改（:69-82）；**Turn**（:90）= `role + content(Message)`，role 限 system/user/assistant（:18），`from_dict` 保留 str content legacy 分支（:110-113，fschat 兼容）；**Conversation**（:119）的 `last_message(role)` 倒序找最近消息（:132-145），`from_openai` 收 OpenAI 形 list[dict]（:156-170）。

**Attempt**（:173）非 dataclass。核心不变式（docstring :204-226）：一个 Attempt ↔ 一个源 prompt，`conversations` 是「每代一条历史」平行数组：

- `prompt` setter 只能设一次（:347-348 raise），深拷贝存不可变副本（:352-356）。
- `outputs` property（:318-333）取每条会话**最后一个 assistant turn**；`all_outputs`（:335-343）收全部 assistant turn。
- `outputs` setter（:361-378）：prompt 未设先 raise（:370-371）；一次给 >1 输出时 `_expand_prompt_to_histories`（:413-426）deepcopy 单历史成 N 线程，再 `_add_turn("assistant",...)`。
- `_add_turn`（:428-458）是对齐守卫：contents 数须等于线程数，否则 ValueError 带 uuid 与两侧计数（:438-442）；user turn 不允许在首次生成前追加（:443-446）。
- 多语言：`lang` 取 prompt 末 turn 语言（:313-316）；`prompt_for/outputs_for`（:380-411）跨语言时回退 `notes["pre_translation_prompt"]` 或 reverse_translation_outputs。
- 状态机 ATTEMPT_NEW/STARTED/COMPLETE（:12-16）；`as_dict()`（:268-301）落 report.jsonl 时带 `entry_type:"attempt"` 标签。

**buffs 链**（`buffs/base.py`）：`Buff(Configurable)`（:18）四方法——`transform()`（:69-73，生成器，一 attempt 可裂变多份）、`untransform()`（:75-77，仅 post_buff_hook 型需要）、`buff()` 批量入口（:79-96）。`_derive_new_attempt`（:45-67）复制源 attempt 并在 notes 写血统三元组 `buff_creator/buff_source_attempt_uuid/buff_source_seq`（:61-65）。四个 buff：`lowercase.Lowercase`（`buffs/lowercase.py:12`）、`encoding.Base64/CharCode`（`buffs/encoding.py:13/31`）、`paraphrase.PegasusT5/Fast`（`buffs/paraphrase.py:14/98`，混入 HFCompatible）、`low_resource_languages`（`buffs/low_resource_languages.py:7`，依赖 deepl）。

## 外部连接

- **probe 侧**：`_mint_attempt` 铸造（`probes/base.py:217-280`）；`_buff_hook` 串接 buff 链（:172-196）——`buffs_include_original_prompt` 保留原 attempt、`buff_max` 截断（:184-188）、post_buff_hook 探针置位（:189-190）。
- **generator 侧**：`this_attempt.outputs = generator.generate(...)`（`probes/base.py:312-314`）；buff hook 型生成后立即 untransform（:315-316）。
- **detector 侧**：`attempt.outputs_for(lang_spec)` 是标准读口（`detectors/base.py:160/222/282`）；`TriggerListDetector` 读 `notes["triggers"]`（`detectors/base.py:284-287`）；分数写回 `attempt.detector_results`。
- **report 侧**：每完成一个 attempt 立即 `json.dumps(as_dict())` 追加写 reportfile（`probes/base.py:351-354`）——崩溃不丢已完成结果。

## 数据流

```
probe._mint_attempt(prompt) → Attempt(conversations=[1条])
  → _buff_hook: Buff.buff → _derive_new_attempt ×N → transform() 裂变
  → outputs setter → _expand_prompt_to_histories(N) → N 条平行会话
  → generator.generate 返回 N 个 Message → _add_turn 对齐追加
  → (post_buff_hook? untransform) → deepcopy 冻结 → report.jsonl
  → detector.detect(attempt) → 分数写 detector_results
```

buff 在送模型**前**变换 prompt，检测在变换后输出上打分；只有 `post_buff_hook=True` 的 buff 才在生成后 untransform。

## 设计决策

1. **1 prompt : N histories 用拷贝非引用**：整份 deepcopy（:426），多代输出互不串扰、detector 可按索引对齐——一致性优先于内存。
2. **prompt 一次性写入**（:347-348）防 probe 中途偷换 prompt；多轮探针应追加 turn 而非改 prompt。
3. **buff 血统入 notes**：uuid 存 str（:62-64 注释「UUIDs don't serialise nicely」），report.jsonl 可回溯派生链。
4. **原始 prompt 不参与 buff**（`buffs/base.py:88` 注释引 issue #373）：只 yield 派生 attempt，防「加 buff 反而稀释攻击面」。
5. **多进程安全**：`Configurable.__getstate__` 把不可序列化属性置 None（`configurable.py:55-62`），Pool（`probes/base.py:345`）才能分发 attempt。

## 新人提示

- 写 probe 永远用 `_mint_attempt`——system_prompt、intent 继承、payload intent 优先级（`probes/base.py:263`）都在铸造函数里。
- 自定义 detector 拿输出用 `attempt.outputs_for(self.lang_spec)`，直接 `.outputs` 会读到未回译文本。
- 对齐错乱看 ValueError 里的 uuid（:440），可在 report.jsonl grep 同 uuid 还原现场。
- 写 buff 只需覆写 `transform()`；需还原输出才写 `untransform()` 并置 post_buff_hook=True，probe 端自动感知（`probes/base.py:189-190`）。
- generator 返回数不符在 generator 侧更早爆 `BadGeneratorException`（`generators/base.py:232-236`）——两道对齐防线职责不同。
