# 02 · log_sage.py — 编排层：会话状态与现行 CLI

> logsage/auto_resume_policy/log_sage.py · 459 行 · 行号 @3493d0fc 源码核实

## 角色定位

现行主编排模块（不是 main.py！）：负责 LLM 客户端初始化、归因会话状态管理，以及三条归因入口——文件（:142）、日志行（:224）、attribution_id（:303）。argparse CLI 的 main 在 :434，这是开源版唯一能跑的命令行入口。测试 test_log_sage.py 用 mock.patch 覆盖其三分支。

## 内部结构

- **模块级全局状态**（:39-54）：`logs_lock` 线程锁（:40）、`LOG_EXPIRY_SECONDS = 24*60*60`（:43）、百万容量的全局 `cache_dict`（:49）、`logs_dict` 会话字典（:52，值为 {timestamp, logs}）、attribution→jobid/userid 两张映射（:53-54）。全部进程内、无持久化。
- **get_llm**（:59-98）：PERSONAL_ENDPOINT 时 register_model 注册自定义端点（:72-81）；否则从 model.txt 读上次轮换到的模型（:83），创建失败回退默认模型。ChatNVIDIA 统一 temperature=0.0/top_p=1/max_tokens=CONTEXT_SIZE//2（:64-70）。
- **三条入口**：`get_attribution_from_file`（:142）latin-1 读文件（:182）；`get_attribution_from_logs`（:224）；`get_attribution_from_attribution_id`（:303）先 `clean_logs_dict`（:287-300 清 24h 过期项），锁内 pop 会话（:324），按 user_id 取/建独立 LRUCache（:332-339）。
- **会话 API**：`generate_attribution_id`（:387，uuid4 :390）+ `append_logs`（:407，追加时刷新时间戳 :419）。
- **split_by_cycle**（:101-139）：按 "Cycle: N" 切日志块——但全仓零调用，仅模块 README 提及，死代码。

## 外部连接

向上消费 error_extraction 的 `return_application_errors`（:185 等，三处均传 `(llm, log_lines, cache_dict)` 3 参）与 error_attribution 的 `get_proposed_solution_cat`（:204 等）；utils 只取 `handle_text_file`/`sanitize_xss` 两件。attribution_classes 提供 LRUCache 与全部 pydantic 模型。注意反向依赖：utils.py:80 在重试耗尽时 `from log_sage import config`——延迟导入打破循环，但意味着 utils 依赖编排层的全局 config 单例。

## 数据流

文件/日志行入口是同步直通：读日志→抽取（:185）→无错误早退→归因（:203 五元组解包）→XSS 清洗（:209-213，consts 的 XSS_FILTERING=True 默认开）→ErrorAttribution。attribution_id 入口是三段式：先建 ID 存空会话，客户端分批 append_logs（大日志可分片上传），最后消费时 pop——一次性语义，取过即删。三条入口对同一份日志共享全局缓存，而 attribution_id 入口用 per-user 缓存隔离多租户。

## 设计决策

1. **锁的粒度**：logs_lock 只护 logs_dict 读写（:290、:323-324），append_logs（:407-427）反而不加锁——extend/refresh 时间戳在 CPython GIL 下近似原子，属务实取舍而非严密并发设计。
2. **24h 过期 + 惰性清理**：不设后台线程，只在每次 id 消费前顺手清理（:287）——服务器长期运行时内存有界，代价是冷 ID 最长滞留 24h。
3. **编码选 latin-1**（:182）：latin-1 对任意字节不抛异常，训练日志常混二进制垃圾，utf-8 会直接崩——main.py:72 的 utf-8 是旧写法未同步。
4. **失败即哨兵**：端点缺失/LLM 初始化失败返回填满错误文案的 ErrorAttribution（:162-178），不抛异常，调用方（API 层）总能序列化。

## 新人提示

从 :434 main 倒着读最快：CLI→get_attribution_from_file→return_application_errors→get_proposed_solution_cat。改会话逻辑时记住 logs_dict 的旧格式兼容分支（:326-330、:417-424 支持裸 list 老数据）。测试清场看 test_log_sage.py 末尾 cleanup。**永远不要把 main.py 当入口读**——它的调用签名全是旧世界的（main.py:87 8 元组解包、:108 六参调用），照抄必 TypeError。
