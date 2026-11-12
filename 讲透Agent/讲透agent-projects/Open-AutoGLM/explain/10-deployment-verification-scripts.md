# 10 · scripts/：部署验证工具链与样例消息资产

## ① 角色定位

Open-AutoGLM 本体不含模型，推理端要自己部署 `autoglm-phone-9b`（SGLang 或 vLLM，requirements.txt:12-14 的注释给出版本）。`scripts/check_deployment_cn.py` 与 `check_deployment_en.py` 是"部署完之后 30 秒确认能推理"的最短路径：携带一套真实的多模态样例消息直探 OpenAI 兼容端点，打印完整推理输出与 token 统计，成败由人眼判断。`scripts/sample_messages.json` / `sample_messages_en.json` 是配套资产——内嵌 1.2MB 真机截图 base64 与一帧系统提示词快照，构造出与 Agent 运行时完全同构的请求形态。

## ② 内部结构

两个脚本是同构双语版（en 版仅 help 文案与默认消息文件不同）。`check_deployment_cn.py` 全部逻辑在 `if __name__ == "__main__"` 内（:7-115）：argparse 八参数——`--base-url`（必填，:18-23）、`--apikey`（默认 EMPTY，:25-27）、`--model`（必填，:29-34）、`--messages-file`（默认 `scripts/sample_messages.json`，:36-41）、`--max-tokens` 3000（:43-45）、`--temperature` 0.0（:47-49）、`--top_p` 0.85（:51-53）、`--frequency_penalty` 0.2（:55-57）。主流程三步：读 JSON 文件为 messages 列表（:62-67）→`OpenAI(base_url, api_key)` 一次性非流式 `chat.completions.create`（:80-93）→打印 `response.choices[0].message.content` 全文（:95-98）与 `response.usage` 三项 token 计数（:100-104），结尾明说"请根据上述推理结果判断模型部署是否符合预期"（:106）。异常分支按类型给排查提示（:108-115）。

**sample_messages.json** 恰好 2 条消息：system 3403 字符（首行 `今天的日期是: 2025年12月11日 星期四`）+ user 消息（1218326 字符的 `data:image/png;base64` 截图 + 55 字符任务文本`这个牌子的洗发水, 去京东和淘宝上比价, 选择最便宜的平台下单`，附带 `{"current_app": "小红书"}` 状态行）。en 版任务更简单（`Open the chrome browser.`），system 快照日期 2025-12-12。

## ③ 外部连接

上游消费 SGLang/vLLM 暴露的 OpenAI 兼容 API（README 的自部署章节直接引用本脚本作为验收步骤）；与 `main.py:272-352` 的 `check_model_api` 互补——后者只发 `"Hi"` 5 token 探活，本脚本才是带真实视觉输入的深度验证。样例里的任务措辞、`current_app` 状态行格式与 `MessageBuilder`（`phone_agent/model/client.py`）运行时拼装的消息同构，可当作消息协议的静态标本读。脚本用相对路径默认值，**必须从仓库根目录运行**（:39），换目录要显式传 `--messages-file`。

## ④ 数据流

`python scripts/check_deployment_cn.py --base-url http://localhost:8000/v1 --apikey EMPTY --model autoglm-phone-9b`（epilog 示例，:12-14）：磁盘 JSON→`json.load` 得到完整 messages→原样塞进 create 调用（不经 MessageBuilder，无历史剥图逻辑）→同步等完整响应（`stream=False`，:92，与 Agent 的流式相反）→stdout 三段输出：推理结果全文、分隔线、token 统计。采样参数透传给服务端（:88-91），默认 0.0/0.85/0.2 即官方推荐的部署验收参数。失败时按 openai 异常信息打印 base_url/api_key/服务状态三类提示并 `exit(1)`（:108-115）。

## ⑤ 设计决策与陷阱

1. **快照漂移（钉版坑）**：样例 system 是某天提示词的静态快照，日期硬编码 2025-12-11/12；而现行 `phone_agent/config/prompts_zh.py:4-10` 已改为 `datetime.today()` 动态拼日期，且正文措辞已迭代——**快照前缀与当前 prompts 逐字比对不一致**（实证：`snap_cn[:50] in prompts_zh` 为 False）。改提示词后拿旧样例验证会测不到新行为，需手工重制消息文件。
2. **人工判定而非自动断言**：脚本没有任何 pass/fail 逻辑（:106 明言），token 统计只是参考——输出格式对不对（`<think>/<answer>`）、坐标合不合理，都得自己看。想接入 CI 必须自己加断言。
3. **非流式**：与 Agent 的流式消费（`</answer>` 提前断流，client.py:121-135）不同路径，验证不了流式行为；TTFT 类指标此脚本不可见。
4. **1.2MB 请求体**：截图 base64 全量内嵌，慢网络下请求耗时可能远超推理本身，不代表 Agent 端到端时延。
5. **双语差异不仅是文案**：en 版 system 快照（2442 字符）与 cn 版（3403 字符）不是互译，是两份独立快照，漂移程度可能不同。
6. **en 版默认路径**：`--messages-file` 默认 `scripts/sample_messages_en.json`（check_deployment_en.py:39-40），但相对路径语义同坑。

## ⑥ 新人提示

部署 SGLang/vLLM 后第一件事就是跑这对脚本（从仓库根目录），确认三件事：能连上、输出带 `<think>…</think><answer>…</answer>` 结构、token 用量在预期量级（prompt 应为千级——1.2MB 图 + 3.4K 系统提示）。要自制样例：参照 sample_messages.json 的两消息结构，system 用 `from phone_agent.config import get_system_prompt` 现取（而非手抄旧快照），user 消息按 `image_url`+text 顺序拼装即可。联调新提示词时建议 `--max-tokens` 调小先看格式。
