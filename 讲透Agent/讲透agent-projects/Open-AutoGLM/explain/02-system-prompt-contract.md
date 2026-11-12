# 02 · 系统提示词契约（phone_agent/config/prompts*.py）

> 对应 tour 第 4 步「系统提示词契约」。Agent 的全部能力边界写在提示词里，本文逐段拆解。

## ① 角色定位

`config/` 下的 prompts 三件套是 PhoneAgent 的"动作协议说明书 + 任务执行军规"：模型能做什么（14 种伪代码操作）、怎么思考（`<think>/<answer>` 输出格式）、犯错了怎么办（18 条规则），全部以自然语言约束写在 system prompt 里。`AgentConfig.__post_init__`（`phone_agent/agent.py:26-28`）经 `get_system_prompt(lang)` 把它注入每轮对话首条 system 消息。**改 Agent 行为风格，第一入口在这里而不是代码**——例如新增一种动作，必须同步改提示词、`ActionHandler` 分派表与（若涉及新平台语义）设备栈，三处缺一模型就不会用。

## ② 内部结构

实际生效的是两个文件，由 `config/__init__.py` 装配：

- **`prompts_zh.py`（默认）**：模块加载时动态生成日期头——`datetime.today()` 取"星期几"并拼成 `2026年10月30日 星期五`（`phone_agent/config/prompts_zh.py:5-8`），随后 `SYSTEM_PROMPT`（`:10`）以 f-string 拼接日期与正文的巨型三引号串。
- **`prompts_en.py`**：英文镜像（`phone_agent/config/__init__.py:6` 导入）。
- **选择器**：`get_system_prompt(lang)` 只认 `"en"` 与其余（`phone_agent/config/__init__.py:29-31`），模块级 `SYSTEM_PROMPT = SYSTEM_PROMPT_ZH` 兜底向后兼容（`:35`）。

`SYSTEM_PROMPT` 正文四段结构（行号取 prompts_zh.py）：

1. **身份与输出格式**（`:14-21`）："你是一个智能体分析专家"，强制 `<think>{think}</think><answer>{action}</answer>` 双段输出——这直接决定了 `ModelClient._parse_response` 的解析契约（见 03 篇）。
2. **操作指令表**（`:23-55`）：14 种动作逐一给出调用样例与语义。要点：坐标是 **0-1000 相对坐标系**（左上 (0,0) 到右下 (999,999)，`:27`）；`do(action="Tap", …, message="重要操作")` 是敏感操作变体（`:28-29`），触发 handler 的确认回调；`Type` 的说明里内嵌了 ADB Keyboard 的可视化提示与"自动清文本"承诺（`:31`）——后者与 `_handle_type` 的 `clear_text` 调用（`phone_agent/actions/handler.py:162`）一一对应，是提示词与代码强耦合的典型；`Take_over`（`:46-47`）映射人工接管回调；`finish(message=…)`（`:54-55`）是唯一终止指令。
3. **必须遵循的规则**（`:57-75`）：18 条。前几条是导航卫生（先查目标 app 再 Launch，`:58`；无关页面 Back，`:59`；页面未加载最多连续 Wait 三次，`:60`）；中段是任务域经验（购物车全选/取消全选技巧 `:65`、外卖清购物车 `:66`、游戏自动战斗 `:73`）；最有工程价值的是**失效自愈规则**——点击不生效则等待→换位置→跳过并在 finish message 说明（`:71`）、滑动不生效则换起点/加距离/反向滑（`:72`，即日期选择器反方向查找 `:69` 的泛化）、多项目栏防死循环（`:70`）、搜索三次降级（`:74`）、结束前完整性自查（`:75`）。
4. **无独立结尾段**：规则 18 即收尾，全文一气呵成。

**勘误钉版**：`config/prompts.py`（不带后缀，75 行）与 `prompts_zh.py` 几乎逐字相同但**少了星期几**（`phone_agent/config/prompts.py:5-6` 无 weekday 计算），且全仓无任何 import 它（barrel 只导 `prompts_en`/`prompts_zh`，`phone_agent/config/__init__.py:6-7`）——它是遗留死代码，改提示词别改错文件。

## ③ 外部连接

- **上游**：仅标准库 `datetime`。
- **下游**：`phone_agent/config/__init__.py:6-7` 唯一聚合点 → `agent.py` 构造期读取（`phone_agent/agent.py:10,28`）→ `MessageBuilder.create_system_message` 包成 `{"role":"system"}` 追加历史（`phone_agent/agent.py:149-151`）。
- **隐式契约方**：`ModelClient` 的 action_markers（`phone_agent/model/client.py:84`）匹配 `do(action=`/`finish(message=`——正是指令表里 `:24`、`:54` 两种格式的字符串；`ActionHandler._get_handler` 的 14 个键（`phone_agent/actions/handler.py:92-107`）与指令表的 action 名严格一致（多一个 `Type_Name` 别名）。`scripts/sample_messages.json` 内嵌了一份**静态快照**（日期硬编码），改提示词后它不会跟着变，用它做部署探针时要意识到版本漂移。

## ④ 数据流

```
import 时: prompts_zh 模块加载 → datetime 计算 → SYSTEM_PROMPT 字符串固化
运行时: AgentConfig(lang) → get_system_prompt → 首步 _execute_step
        → _context[0] = system 消息 → 之后每轮请求都携带
        模型输出 <answer>do(action=…)</answer>
        → 与指令表语法对齐 → parse_action 还原 dict
```

注意日期只在**模块导入时**计算一次（`phone_agent/config/prompts_zh.py:5`），长驻进程跨天后 system prompt 里的日期会陈旧——对"今天点外卖"类任务可能造成日期误判，重启进程即刷新。

## ⑤ 设计决策与陷阱

1. **提示词即 API**：动作语义、坐标系统、清文本行为都写死在自然语言里，代码侧是被动实现方。review 动作相关 PR 时，提示词 diff 与 handler diff 必须对照看。
2. **坐标系选择 0-1000 相对坐标**（`:27,37`）：模型输出与分辨率解耦，由 `_convert_relative_to_absolute`（`phone_agent/actions/handler.py:110-116`）换算像素；代价是黑图兜底（1080×2400 假分辨率）时换算基准失真（见 06 篇）。
3. **中文默认、英文镜像的双语策略**：结构完全平行但无自动化一致性检查，改中文规则后英文极易漏改。
4. **规则 8-11 是评测集蒸馏**：购物车/外卖/咖啡搜索案例（`:65-68`）明显来自特定 benchmark 的失败模式回填，属于"往提示词里塞任务先验"——迁移到新场景时这批规则可能是噪声甚至误导。
5. **死代码陷阱**（见②末）：`prompts.py` 与 `prompts_zh.py` 双胞胎，diff 只有 weekday——实际生效的是后者。
6. **快照漂移陷阱**：`sample_messages.json` 的 system 消息不会随源码更新，部署校验通过≠当前提示词可用。

## ⑥ 新人提示

- 想快速实验行为变化：复制 `prompts_zh.py` 的 `SYSTEM_PROMPT` 改后经 `AgentConfig(system_prompt=…)` 显式注入（`phone_agent/agent.py:23`），避免直接改仓库文件。
- 新增动作三步走：提示词指令表加样例 → `ActionHandler._get_handler` 加键（`phone_agent/actions/handler.py:92`）→ 设备栈实现对应原语；别忘英文版。
- 调"模型不听话"类问题时，先确认是不是规则冲突（如规则 6 放宽筛选 vs 用户意图严格匹配，`:63` vs `:68`），再怀疑模型能力。
- `Type` 动作说明里关于 ADB Keyboard 的整段提示（`:31`）是为视觉模型理解"键盘不占屏"设计的，删掉会引发模型反复检查键盘状态，慎动。
- 本篇与 04 篇（handler 分派表）、03 篇（解析标记）构成动作协议三角，改任何一角先读另两篇的契约段。
