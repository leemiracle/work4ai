# 06 repair_llm_raw_output 修复闭环：utils/repair_llm_raw_output.py + custom_decoder

## 一、角色定位

开源模型时代 LLM 输出不可信：大小写漂移、`[CONTENT]` 闭合标签丢斜杠、JSON 尾巴多 `]`、注释混进值里。这两个文件是 MetaGPT 对此的整套防御工事：repair_llm_raw_output.py（398 行）提供六类修复函数 + tenacity 重试闭环；custom_decoder.py（297 行）是 CPython json.decoder 纯 Python 实现的 fork，把宽容解析（单引号/三引号/裸控制字符）下沉到扫描器层。它们服务两条不同消费链：主链是 ActionNode._aask_v1 的 JSON 输出修复；旁链是 Role._think 状态抽取（extract_state_value_from_output）与 RoleZero 命令的 LaTeX 转义修复（repair_escape_error）——NOTES-DIGEST 103 明确区分了这三条线。

## 二、内部结构（行号锚）

**修复函数族（repair_llm_raw_output.py）**：
- :17-21 `RepairType` 四态枚举：CS（大小写）/RKPM（键对缺失）/SCM（特殊字符缺失）/JSON（格式）。
- :24-41 `repair_case_sensitivity`：schema 字段 "Shared Knowledge" 被模型写成小写 k 时整段替换。
- :67-105 `repair_required_key_pair_missing`：补 `[/CONTENT]` 闭合标签；:87-96 judge_potential_json 用 rfind("}")/rindex("]") 截潜在 JSON 尾。
- :108-140 `repair_json_format`：剥 `[{`/`}]` 多余括号；:124-139 逐行正则剥离 `#` 与 `//` 注释（:129 finditer 区分字符串值与注释）。
- :184-242 `repair_invalid_json`：解析 JSONDecodeError 的 "line N column M"（:191-196）定位坏行，九分支修补（多余 `]`/`}`、缺逗号、三引号、反斜杠逃逸……）。
- :309-339 `extract_content_from_output`：正则抽 `[CONTENT]...[/CONTENT]`；:322 pattern 硬编码、right_key 参数没进 pattern（:320 TODO 自认）。

**重试闭环（同文件）**：
- :245-280 `run_after_exp_and_passon_next_retry`：tenacity after 钩子。失败时从 retry_state.args/kwargs 取原输出（:264-268），调 repair_invalid_json 修补后 **:278 `retry_state.kwargs["output"] = repaired_output` 改写参数注入下一轮**——修复与重试的粘合点。
- :283-284 `repair_stop_after_attempt`：按 Config 动态给 3 或 0 次（开关关闭即不重试）。
- :287-306 `retry_parse_json_text`：@retry 包装 CustomDecoder(strict=False).decode（:304）；:296-299 docstring 自述与外层 _aask_v1 构成 3×3 两层重试环。
- :157-181 入口 `repair_llm_raw_output`：:174-176 被 config.repair_llm_output 短路（config2.py:75 **默认 False**）。

**CustomDecoder（custom_decoder.py）**：
- :4 `from json.decoder import _decode_uXXXX`——**依赖 CPython 私有 API**，下划线开头无兼容承诺，解释器升级有破坏风险。
- :10-70 `py_make_scanner` fork：:28-36 新增三引号分支（`"""`/`'''` 整段按字符串吃掉）；单双引号统一走 delimiter 参数化。
- :73-76 四个 STRINGCHUNK 正则（单/双/三双/三单）；:91 JSONObject、:195 `py_scanstring(s, end, strict, ..., delimiter='"')` 签名比 stdlib 多 delimiter。
- :296 `decode`：_w 参数沿用 json.decoder.WHITESPACE。

**相邻截断陷阱（provider/base_llm.py）**：
- base_llm.py:340-410 `compress_messages`：POST 分支 :386 `msg["content"][-(keep_token - current_token_count):]`——剩余额度为 0 时 `-0 == 0`，切片退化为 `[0:]` **保留全文，截断判定失效**（NOTES-DIGEST 16）；PRE 分支 :404 `[:0]` 返回空串无此问题。

## 三、外部连接

主链上游：ActionNode._aask_v1（action_node.py:441-444）→ provider/postprocess/llm_output_postprocess.py:12 → base_postprocess_plugin.py:50 `run` → :18-38 四步修复（repair_llm_raw_output→extract→JSON repair→retry_parse）。开关：config2.py:75 repair_llm_output。旁链：extract_state_value_from_output 被 role.py:368 消费（STATE_TEMPLATE 选号）；repair_escape_error 服务 RoleZero 命令解析（docstring :362-364 自述）；compress_messages 挂在 BaseLLM.aask（base_llm.py:207）。命名陷阱：本文件 :9 `import regex as re`（第三方 regex 库冒充 stdlib），custom_decoder.py:2 才是真 stdlib re——同名不同实现，改代码前先看清（NOTES-DIGEST 100）。

## 四、数据流

JSON schema 模式下的完整闭环：LLM 返回 raw → repair_llm_raw_output 按 schema 字段名修大小写 + 补标签 → extract_content_from_output 抽正文 → repair_json_format 剥注释/修括号 → retry_parse_json_text 进 tenacity 环：CustomDecoder 尝试解码 → JSONDecodeError 被 after 钩子捕获 → repair_invalid_json 按 line/column 修坏行 → 改写 kwargs 注入 → 下一轮用修好的文本再解码 → 三轮仍失败则异常上抛给 _aask_v1 的外层重试（再问模型）。整个链条的假设是"输出离合法只差几步机械修补"，不重新生成、纯本地修复，省钱且快。

## 五、设计决策

- **修补优先于重问**：修复环成本为零 token，外层重问才花钱——两层 3×3 设计把便宜手段放在内层。开关默认 False 则是对质量/兼容的取舍：闭源模型输出规整，修复反而可能误伤（repair_case_sensitivity 的 replace 是盲替换）。
- **fork stdlib 而非预处理字符串**：宽容解析做进扫描器（custom_decoder）而不是把单引号全局替换成双引号，保住了字符串值内部的引号语义——这是正确性上的关键选择，代价是 300 行 CPython fork + 私有 API 依赖，升级 CPython 时需要 diff stdlib json/decoder.py 同步。
- **after 钩子改写 kwargs（:278）是 tenacity 的非典型用法**：官方语义里 after 只该做日志，这里借 RetryCallState 可变性把修复结果走私进下一轮——精巧但脆弱，tenacity 大版本若改 RetryCallState 结构即断。
- **repair_invalid_json 的分支表是错误驱动增量**：九个 elif 每支对应一类实测过的模型错误，没有抽象只有案例；可维护性差但对长尾错误命中率高于通用方案。
- **compress_messages 的 -0 陷阱（base_llm.py:386）**：`[-0:]` 语义陷阱的经典案例——系统消息吃满预算时 POST 截断静默失效，超长消息原样发出，表现为"配了截断还是超上下文"。

## 六、新人提示

1. 输出解析报错先开 repair_llm_output（config2.yaml）再复现——很多"偶现解析失败"是开关默认关闭导致修复环根本没跑。
2. 排查解析失败别只看最终异常：日志里 grep "repair_invalid_json, raw error" 与 "parse json from content"，前者是钩子修补记录，后者才是真失败。
3. 改 custom_decoder.py 前对拍 CPython 源码（Lib/json/decoder.py），改造点只有引号宽容与 delimiter 参数，其余刻意保持同构。
4. 自定义 [REQ_KEY] 标签时注意 extract_content_from_output 的 pattern 硬编码 `[CONTENT]`（:322），换标签名必须同步改这个函数。
5. 在 Provider 层做长上下文截断时，先修 base_llm.py:386 的 -0 退化（改成 `[-max(keep_token - current_token_count, 0):]` 之类），否则空额度时不截断。
