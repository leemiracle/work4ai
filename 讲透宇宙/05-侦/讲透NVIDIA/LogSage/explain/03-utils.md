# 03 · utils.py — 56 函数公共工具层

> logsage/auto_resume_policy/utils.py · 1622 行 · 行号 @3493d0fc 源码核实

## 角色定位

全仓公共依赖层（图谱 fanOut=117 最高）：模板化与去重、四族上下文压缩、LLM 重试与模型轮换、输出解析与安全清洗。error_extraction/error_attribution/log_sage 三个生产模块都 import 它，test_utils.py 33 用例横扫。没有它，百万行日志塞不进 100k 窗口，LLM 端点抖动也没有防线。

## 内部结构

- **重试与轮换**：`retry_operation`（:53）max_retries=5、间隔 0.5s（:102）；耗尽后解析 MODEL_LIST 环形切换下一个模型写入 model.txt（:75-98），返回哨兵串 LLM_ENDPOINT_FAILED（:100）而非抛异常——"失败也是数据"贯穿全仓。`get_next_text`（:105）是环形取值器。
- **模板化六连**：路径 <PATH>（:121）→引号文本 <TEXT>（:163）→标点加空格（:177）→十六进制 <HEX>（:208）→长词 <LONG>（:194，docstring 说 10 字符代码实为 14，:205）→数字 <NUMBER>（:135）；`get_templating`（:1434）按此序串成管线，`get_templating_multiprocessing`（:1466）用 min(cpu_count(),8) 进程池加速并失败回退单线程（:1477）。另有词边界版 `convert_only_numbers_to_token`（:149）。
- **四族压缩**：`compress_application_log`（:568，模板分组+round_robin（:434）交错+按模板均分配额）；`_ordered`（:605，保序+stacktrace 嵌回）；`_ordered_cut`（:770，策略主用：倒数第 5 次迭代截断 :869-879、迭代后首个非迭代错误起截断 flag_remove :889-891、95% 相似去重 :713、剥 NCCL watchdog 尾噪 :907-921）；`_ordered_user_rec`（:1005，面向基础设施归因保留更完整上下文）。`compress_application_log_not_ordered_cut`（:926）全仓零调用，死代码。
- **签名检测**：`check_if_iteration`（:1130）11 组关键词启发式识别训练进度行（:1181 的 "â" 是 tqdm 进度条 UTF-8 箭头被 latin-1 读出的 mojibake，反而是真实日志特征）；`check_finished`（:1199，含 yotta "Finished" :1216）；`check_checkpoint`（:1221）。
- **过滤三表**：BENIGN/ERROR/HARDWARE 三组词表分别对应 :1243/:1295/:1316。
- **输出侧**：`extract_answer` 剥 <think>（:1573）；`extract_attribution_explanation`（:1507）解析归因两字段，但 :1521 返回的 attribution 是原始全文而非解析值——下游拿到的是整段回答，疑缺陷或有意保真；`sanitize_xss`（:1568）nh3 清洗；`prepare_log_for_llm`（:1493）花括号替换+尾部截断。

## 外部连接

consts 提供三张词表与 CONTEXT_SIZE；log_sage 的 config 被延迟反向导入（:80）用于轮换开关；nh3/numpy/pandas 三个运行时依赖全在此层。相似度有两套口径：词频重叠版 `similar_with_duplicates`（:464，阈值 0.4）与 Jaccard 版 `similarity_score`（:1358，@lru_cache(1024)），分别服务去重与找相似行。

## 数据流

以策略生成为例（error_attribution.py:314 调 _ordered_cut）：错误三元组 (log, pattern, i) 输入 →按模板分均分配额、倒序保留尾部（最新错误优先）→迭代剪裁四连→watchdog 剥尾→截到 CONTEXT_SIZE 内返回 (压缩日志, flag_remove)。flag_remove 决定用哪套 policy 指令模板（error_attribution.py:359-365）——压缩算法直接改变后续 LLM 提示词的选型。

## 设计决策

1. **尾部优先**：所有压缩都从最后往前取（sorted reverse :829）——训练故障的关键证据几乎总在日志末尾。
2. **模板配额而非行数配额**：compress_length / 模板数 / 行长 三级分摊（:816-822），保证每个错误模式至少留代表行。
3. **多进程只做模板化**：六连全是纯函数无共享态，天然可并行；聚类判定留在主进程。
4. **check_less_three 的 IP 特例**（:1416）：2 个 IP+4 节点也放行——IB 网络故障常成对出现，机械限制 3 会误杀。

## 新人提示

先读六连与 _ordered_cut 两块（全仓调用量最大），再按需查表。测试入口 test_utils.py 的 9 类；test_error_extraction.py 名不符实，测的其实是本文件的数字 token 化（:19）。改压缩函数务必跑 test_error_attribution.py 全量——5 条 UUID 会话链路对压缩输出的格式敏感。
