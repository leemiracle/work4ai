# 06 · detection 四路后端：GuardrailBackend 抽象与 torch 惰性隔离

> 定位：`agent_shield/detection/` 是与 `tool_permission` 完全正交的子系统——facade docstring 一句话分清两者：tool_permission 是 "F1 动作决策：对工具调用输出**确定性**结论（allow/ask/deny）"（`tool_permission/__init__.py:3`），detection 是 "F3 内容检测：对进入模型的内容做注入等检测，输出**概率性软信号**"（`detection/__init__.py:3`）。本篇讲 `backends.py` 的四路预置后端（规则/LLM/API 模型/本地模型）、`context.py` 的两个模型输出 parser（BertBinaryParser 的 <0.7 保守归 SAFE、QwenGuardParser 的四格式解析），以及 LocalModelBackend 对 torch/transformers 的惰性隔离。

## 一、角色定位

detection 子系统回答的问题是"**这段内容有没有风险**"而不是"这次调用放不放行"。它的输出 `RiskAssessment`/`GuardrailResult` 是概率性信号（带 confidence），拦不拦是宿主的决定——`GuardrailResult.block` docstring 强调 "it does not perform execution blocking by itself"（`detection/models.py:71-72`）。这正是第 01 篇分区判据在子系统级的映射：F1 阻断主业务所以 fail-closed，F3 是旁路信号所以允许"不确定就当没看见"（BertBinaryParser 的保守阈值）。

模块 docstring 给出四条设计原则（`detection/backends.py:10-14`）：不假设具体检测方法（LLM/规则皆可）；**配置走构造函数而非类变量**（支持多实例不同配置）；analyze 收 `GuardrailContext` 而非裸 dict；预置常用后端。

`GuardrailBackend` 是唯一的抽象（L39-82）：`async analyze(ctx) -> RiskAssessment`，异常**原样上抛**——docstring 明言 "Exceptions propagate to the caller. This method does not turn them into a RiskAssessment"（L78-80）。检测器崩溃不被伪装成"安全"，与 engine 层组件异常 re-raise（第 01 篇）一脉相承。

## 二、内部结构

### 四路后端一览

| 后端 | 行号 | 依赖 | 输入 → 输出 |
|---|---|---|---|
| `RuleBasedPromptInjectionBackend` | `backends.py:127-190` | 纯 re | 正则命中 → HIGH/SAFE，confidence 1.0 |
| `LLMPromptInjectionBackend` | L193-244 | 无（占位） | **回落规则后端**，不发真实 LLM 调用 |
| `APIModelBackend` | L250-331 | httpx（方法内惰性 import） | POST `/detect` → parser.parse(json) |
| `LocalModelBackend` | L334-503 | torch/transformers（类级惰性） | 本地推理 logits → parser.parse |

每路都有对应的 `*Config` dataclass（L88-122），同时保留关键字参数直传的兼容形态（如 L140-146 config 与 patterns 二选一）。

**RuleBased** 的默认 pattern 表只有 6 条（L181-190）：`ignore.*previous.*instructions`、`disregard.*prior.*commands`、`system.*prompt`、`you.*are.*now`、`act.*as`、`forget.*everything`。注意 `act.*as` 与 `system.*prompt` 极宽（命中即 HIGH，confidence 硬编码 1.0）——**示例级**默认而非生产级，真实部署必须自带 patterns 或换后端。

**LLM 后端是占位**：`analyze` 收到文本后调 `_fallback_analysis`（L221-244），注释直说 "For now, fall back to rule-based analysis as an example"（L232-233）——构造函数收 api_endpoint/api_key/model_name，但**从不发请求**；中文系统提示词模板（L208-210）只是为将来接线预置的资产。今天它就是规则后端的别名。

**APIModelBackend** 的 httpx import 在 `_call_api` 方法体内（L314-317）——模块导入零网络依赖；请求形态固定 `{"text": text}` POST + Bearer 头（L318-331），`raise_for_status` 让 HTTP 错误沿异常契约上抛，响应交给注入的 parser（L312）。

**LocalModelBackend** 的惰性隔离是本篇最重的工程设计：torch/transformers 挂**类级**变量（L351-352），首次 `_lazy_import_torch`（L407-418）才 import，失败抛带安装指引的 ImportError；模型在**首次 analyze** 才加载（`_ensure_model_loaded` L401-405 → `_load_model` L433-448：AutoTokenizer + AutoModelForSequenceClassification，device auto 按 cuda 可用性选，加载后 `.eval()`）；推理 `_inference`（L450-467）tokenizer 截断 max_length=512、`torch.no_grad()`、返回 `{"logits": [...]}`——**softmax/阈值判定全部交给 parser**；`cleanup`（L469-481）释放模型并 `torch.cuda.empty_cache()`；`is_model_loaded`/`get_model_info`（L483-503）暴露自省。

### context.py：契约与两个 parser

`GuardrailContext`（L20-76）是 ConcreteGuardrail（事件绑定与预处理）与 Backend（检测逻辑）之间的契约：`content_type`（TEXT/MESSAGES/TOOL_CALL/RAW 四值，`enums.py:33-42`）+ `content` + `event` + `metadata`；取数器 `get_text()`/`get_messages()`/`get_tool_name()` 做类型守卫（content_type 不符返回 None）。

`ModelOutputParser`（L82-99）是第二层抽象：把任意模型输出转 `RiskAssessment`。

**BertBinaryParser**（L102-200）的二分类保守映射是 docstring 级承诺（L104-121）：

```
class=1（攻击）时：
  confidence < 0.7   → SAFE（"too uncertain, avoid false positive"）
  0.7 ≤ c < 0.85     → LOW
  0.85 ≤ c < 0.95    → MEDIUM
  c ≥ 0.95           → HIGH
class=0 时：无论置信度一律 SAFE
```

阈值常量 `DEFAULT_THRESHOLDS = {"low": 0.7, "medium": 0.85, "high": 0.95}`（L123-127），构造可覆盖（L129-137，`attack_class_id` 也可换，适配 label 顺序相反的模型）。`_extract_prediction`（L155-189）兼容**五种输出形态**：`{predicted_class, confidence}`、`{label, score}`、`{probabilities: [p0, p1]}`、`{logits: [...]}`（手写 softmax，L171-180——正是 LocalModelBackend 的输出形态）、裸二元组/标量。`parse` 的 details 里 `attack_confidence` 按预测类换算（预测安全时给 1-confidence，L149-152），保证这个字段语义恒为"攻击类置信度"。

**QwenGuardParser**（L203-442）面向 Qwen3Guard 类生成式安全模型：标准输出是两行文本 `Safety: Unsafe` / `Categories: Violent`（L207-215）；解析层级：先试整 JSON / 首尾大括号截取（L247-262），dict 输入按四格式分派（`safety`/`analysis`/`judgment`/`severity_level`，L323-332），兜底 `_parse_generic_dict`；纯文本逐行找 `Safety:`/`Categories:` 键（L264-321）。风险映射 Safe→SAFE、Controversial→MEDIUM、Unsafe→HIGH（L221-225）；`_map_risk_level` 对未知值做最长关键词包含匹配（L434-442），`default_risk_level` 缺省 SAFE——**解析不出的东西当安全**，与 BertBinaryParser 保守方向一致。

### models.py：两级结果对象

`RiskAssessment`（L92-111）是后端输出；`GuardrailResult`（L20-89）是框架级结果，两者经 `to_guardrail_result` 转换——转换函数 docstring 特别记录了一处迁移修复："Preserves the backend's confidence score, **unlike the pre-migration detect() path which discarded it**"（L116-118）。`GuardrailResult` 带 `is_safe`/`risk_level`/`modified_data`（消毒后数据位）/`event`，工厂方法 `pass_`/`block`。RiskLevel 五级：SAFE/LOW/MEDIUM/HIGH/CRITICAL（`enums.py:16-30`）——注意它比 PermissionLevel（allow/ask/undetermined/deny）多一层语义维度，两套枚举永不互转，转换逻辑（什么 risk_level 映射成 ask/deny）属于宿主 guardrail 框架，不在这两个子系统内。

## 三、外部连接

- **facade**：`detection/__init__.py` 导出全部 16 个名字（枚举 2 + 模型 3 + context/parser 4 + backend 7）；调用方只从 `agent_shield.detection` 导入（第 02 篇纪律）。
- **与 tool_permission 的关系：零连接**。grep 全仓没有任何 `tool_permission` ↔ `detection` 的 import——F1 与 F3 的组合发生在宿主（jiuwenswarm 把 F3 软信号接到 F1 配置或 HITL 流程），agent_shield 内部不预设组合方式。
- **依赖面**：`backends.py` 顶层只 import re/abc/dataclass/typing；httpx/torch/transformers 全部惰性（方法内/类级懒加载）；parser 的 math/json/re 也都在方法内 import。整个 detection 子系统**顶层导入零第三方依赖**——第 02 篇"包根零加载"纪律在 detection 侧不被破坏。
- **测试**：`tests/detection/` 四文件（test_parsers/test_backends/test_models/__init__）。

## 四、数据流

以"本地 BERT 注入检测"为典型链路：

1. 宿主 guardrail 在某事件（如 `llm_invoke_input`）把原始数据预处理成 `GuardrailContext(content_type=TEXT, content=text, event=…, metadata=…)`；
2. `LocalModelBackend.analyze(ctx)`：空文本短路返回 SAFE confidence 1.0（L389-395）；否则惰性加载模型 → `_inference` 得 `{"logits": [l0, l1]}`；
3. `BertBinaryParser.parse`：`_extract_prediction` 对 logits 手写 softmax（exp/sum，L171-177）得 (predicted_class, confidence) → `_determine_risk_level` 按 0.7/0.85/0.95 三档映射 → 组装 `RiskAssessment`（has_risk = level≠SAFE，details 带 predicted_class 与换算后的 attack_confidence）；
4. 宿主拿 RiskAssessment 决定动作：`to_guardrail_result` 转框架结果、按自身策略决定 pass/block/打标。

APIModelBackend 链路同构，只是第 2 步换成 httpx POST（超时默认 30s，`APIModelBackendConfig.timeout` L102）、第 3 步的 parser 解析的是远端 JSON。RuleBased 链路无模型：正则逐条 `re.search`（IGNORECASE），首条命中即返回（L165-173）。

注意各后端对**空输入的一致处理**：LLM/API/Local 三家都在 analyze 开头判空文本 → SAFE + confidence 1.0（L225-230、L304-309、L390-395）。"没内容就没风险"在这里是安全的（检测空串确实无意义），但写宿主逻辑时别把这个语义搬到"content 字段缺失"的场景——那是数据错误，应当异常而不是 SAFE。

## 五、设计决策与权衡

**为什么 parser 与 backend 分离？** 同一个 BERT 二分类模型可以本地跑（LocalModelBackend）也可以远端服务化（APIModelBackend），分类阈值逻辑（0.7/0.85/0.95）是**模型属性**而不是部署属性——parser 注入让阈值策略跟着模型走。代价是配置面多一个对象，但换来"换部署不改判定语义"。

**BertBinaryParser 为什么 <0.7 直接归 SAFE（而不是 LOW）？** docstring 给了三条理由（L109-113）：预测类为主指示、高阈值防误报、保守风险映射。深层原因回到 F3 定位：内容检测是旁路软信号，误报会污染下游所有依赖该信号的流程，而漏报还有 F1 的确定性防线兜着——**宁可漏报给 F1 兜底，不可误报打断体验**，与 delguard 的 fail-open 同一判据。

**torch 惰性隔离挂在类级而非实例级的取舍。** 类变量（L351-352）让同进程多实例共享一次 import（省时），但每实例仍各自 `_model`/`_tokenizer`（L382-384）各自占显存——"同模型多配置"得靠宿主单例包装。细节：`_lazy_import_torch` 成功后写回类变量（L411-412），**失败不缓存**——装上 torch 后无需重启进程即可用。

**`analyze` 全 async 而推理是同步阻塞的。** LocalModelBackend 的 `_inference` 在 async 方法里同步跑模型——大模型会卡事件循环。这是刻意的简单化：高频部署应把推理放独立线程/进程（宿主责任）。APIModelBackend 用 httpx.AsyncClient 是真异步（L324-331），两种形态并存说明框架对"检测耗时"没有统一假设。

**LLM 后端保留占位而不是删掉。** 留着"配置齐全但不发请求"的类，给接入方一个稳定的类型槽位——宿主可先写好配置装载与依赖注入，接线时只改后端内部实现。

## 六、新人提示与坑

1. **LLMPromptInjectionBackend 今天不发任何 LLM 调用**（L232-244 回落规则）——code review 里看到它被用于"LLM 检测"要立即指出；真需要远端 LLM 检测用 APIModelBackend + 自定义 parser。
2. **RuleBased 默认 pattern 太宽**（`act.*as` 命中 "fact as" 之外的一切 "act as"；`system.*prompt` 命中任何讨论系统提示词的正文）。生产必须显式传 patterns；示例 docstring（L134-137）也是用自定义 patterns 演示的。
3. **BertBinaryParser 的 SAFE 有两种来源**：class=0（真预测安全）与 class=1 但 confidence<0.7（不确定）。排查"为什么明显攻击没标出来"时看 details.predicted_class——如果是 1 且 attack_confidence 0.6x，那是阈值设计而非模型失灵。
4. **`_extract_prediction` 五种形态的优先级**：dict 键依次 `predicted_class` > `label` > `probabilities` > `logits`（L155-180），全不中还有 list/标量兜底，最后 `(0, 0.0)`——返回 (0, 0.0) 意味着 SAFE，parser 对完全看不懂的输出**当安全处理**。自定义远端 API 时务必让它至少输出四种可识别形态之一。
5. **LocalModelBackend 首次调用最慢**（模型加载在第一次 analyze），对延迟敏感的路径要在启动期用一条空/样例文本预热——或者直接调 `get_model_info()` 观察 `model_loaded` 别忘了它只反映加载状态不触发加载。
6. **两套枚举别混用**：RiskLevel（safe~critical）是检测语义，PermissionLevel（allow/ask/undetermined/deny）是裁决语义，仓内没有任何映射函数——写宿主桥接层时这是你的代码，风险映射策略（什么 level 拦、什么 level 只记）要显式写测试。
7. **detection 与 tool_permission 是平行宇宙**：想在 engine 组件里消费 detection 结果，没有现成通道——需要新建组件（implement PermissionComponent 协议）并遵守第 01 篇的合并语义（最严者胜），别试图让 detection 后端直接返回 PermissionResult。
