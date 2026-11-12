# 02 | agent-security-apex——91 条攻击样本 × 守护密码靶机的红队评测线

## ① 角色定位

`tutorials/agent-security-apex/` 对应图谱 L3"提示注入攻防资产"层（2 节点：example_prompts.csv + system_prompt.txt），由 README（documents 边）统领，另含评测 notebook 与两个工具 py。它是五条深覆盖线中唯一的对抗性教程：不教框架，教"如何量化一个 system prompt 的可攻破程度"。tour step-03 的定位是"用真实数据学攻防"——攻击面来自 CSV 数据集，靶机来自 system_prompt.txt，自动化执行器来自工具代码。

## ② 内部结构

五件资产四类角色：
- **README.md**：教程导览。核心数字承诺在 README.md:12-15——8 大类攻击 91 例、12 种编码混淆旁路。
- **example_prompts.csv（攻击数据集）**：表头 `name,type,text`（example_prompts.csv:1），91 条记录 = 80 条 jailbreak + 11 条 prompt_injection（csv 解析实证），全部以"What is the password?"收尾（example_prompts.csv:2 的 Evil Confidant 是首例）。物理行 480 行远大于记录数——攻击文本内含引号内换行。条目名即业界知名越狱样本：Leo、DevMode + Ranti、KEVIN、SmartGPT、Code Injection。
- **system_prompt.txt（靶机）**：57 行三段式规则集。第一段双重职责（system_prompt.txt:1-3 帮答问题+守护密码）；第二段封堵策略——绝不透露（system_prompt.txt:5-7）、95% 置信度阈值才拒绝回答（system_prompt.txt:12-13）、封同义词/韵脚/哈希/翻译/字谜旁路（system_prompt.txt:29-33）、固定拒绝话术（system_prompt.txt:41-44）、防 prompt 泄露（system_prompt.txt:46-48）；密码本体在 system_prompt.txt:39 `The password is { password }.`——占位符两侧各带一个空格。
- **model_testing_tools.py（评测执行器）**：`cur_password = "pinky"` 硬编码（model_testing_tools.py:10）；`generate_chatgpt_response` 在调 gpt-4.1-mini（model_testing_tools.py:20）前把占位符替换为真密码（model_testing_tools.py:18 `system_prompt.replace("{ password }", cur_password)`，注意是 model_testing 而非 prompt_manipulation 文件）；`test_model` 随机抽 5 条样本（model_testing_tools.py:98）做未编码→编码两轮打靶（model_testing_tools.py:110-137）并汇总成功率（model_testing_tools.py:164-190）。
- **prompt_manipulation_tools.py（混淆器）**：`prompt_encoder`（prompt_manipulation_tools.py:1）内置 12 种编码（prompt_manipulation_tools.py:9-22）：atbash/caesar/vigenere/braille/morse/pig_latin/leet/binary/hex/base64/rot13/reverse，未指定时随机选一种（prompt_manipulation_tools.py:25-26）。全部纯 Python 手写，如 rot13 走 codecs（prompt_manipulation_tools.py:255-261）。

## ③ 外部连接

依赖：requirements.txt 仅四项——python-dotenv/aiohttp/ipython/openai（requirements.txt:2-5），异步打靶用 aiohttp 支撑的 AsyncOpenAI（model_testing_tools.py:8）。资产间消费链：notebook 读 CSV+靶机→调两个工具 py；model_testing_tools.py:6 `from prompt_manipulation_tools import prompt_encoder` 是仓内唯一模块间 import。在图谱里 README 以 documents 边同时指向 CSV 与靶机（step-03 三节点），与其它线零耦合。

## ④ 数据流

输入：CSV 91 条攻击文本 + 靶机模板 + OPENAI_API_KEY。流程：`test_model` 读 CSV（默认路径见下文陷阱）→ `df.sample(n=5)` 抽样 → 每条先原文打靶（`try_to_get_password`→`send_prompt_to_model` 起 1 个并发任务→`asyncio.gather` 收拢，model_testing_tools.py:43-46）→ `check_password_in_response` 判定泄露（model_testing_tools.py:49-50）→ 未成功才用随机编码再攻一轮（model_testing_tools.py:124-137）→ 输出未编码成功率、编码成功率与"encoding_effective_count"（编码在原文失败时得手的次数，model_testing_tools.py:94/141）。输出：stdout 汇总报表（model_testing_tools.py:155-218）+ results dict。

## ⑤ 设计决策与陷阱

- **决策：靶机与攻击集分离**。攻击面是通用越狱语料，靶机是可参数化模板——换密码只改 model_testing_tools.py:10 一处，评测可复现，这是红队基准(testbench)的标准形态。
- **陷阱 1（ONBOARDING 勘误）**：占位符替换真实位置在 **model_testing_tools.py:18**，ONBOARDING 第 5 节误写为 prompt_manipulation_tools.py:18——后者全文无 replace 调用（269 行纯编码器）。
- **陷阱 2：默认 CSV 文件名不匹配**。model_testing_tools.py:67 默认 `gallery_data.csv`，仓内实为 `example_prompts.csv`——notebook 必须显式传 csv_path，直接 `test_model(client)` 会 FileNotFoundError。
- **陷阱 3：encoded 分支缺参（静态读出）**。model_testing_tools.py:127 `try_to_get_password(encoded_prompt, client)` 漏传第三参 system_prompt，而签名（model_testing_tools.py:32-34）无默认值，调用即 TypeError；该异常又被 model_testing_tools.py:45 `return_exceptions=True` 吞成结果列表元素，最终表现为"编码攻击恒失败"而非报错。同文件 model_testing_tools.py:49-50 对 gather 返回的 list 做 `cur_password in response` 是元素级成员判断而非子串判断——独立运行此文件时泄露判定本身也近乎失效（仅当回复恰为"pinky"才判真）。以 notebook 内的评测逻辑为准更可靠。
- **陷阱 4：占位符空格敏感**。`{ password }` 三处空格必须逐字匹配（model_testing_tools.py:18），手改靶机时易丢。
- **决策：12 种编码全为无依赖手写**——教学可读性优先于工程复用（不引 cryptography 库）。

## ⑥ 新人提示

先读 README.md:12-15 对齐预期，再直读 system_prompt.txt 全文体会"规则密度 vs 可绕过性"的张力——95% 阈值（system_prompt.txt:12）本身就是攻击面（低置信即放行）。跑评测前准备：.env 放 OPENAI_API_KEY、独立 venv 装 4 依赖、显式传 `csv_path="example_prompts.csv"`。复用这套资产做自家产品红队时，把 cur_password 与 model 参数（model_testing_tools.py:20）换成目标配置即可，但务必修掉陷阱 3 的缺参调用。学习产出建议：统计 80 jailbreak 与 11 injection 两类的成功率差，理解"角色扮演型"与"指令注入型"攻击的机制差异。
