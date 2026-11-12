# 04 · protocol + mathutils 生成侧——两级哈希与 q 混淆的双子星

## 角色定位

两个模块把"依赖推断"逼到墙角：mathutils（模式 3）证明**依赖关系本身**可以藏在生成器背后；protocol（模式 5，全仓难度天花板）再叠加上**文件名不可预测**。一个是 perl+混淆的极简酷演示，一个是 python+spec 驱动的完整代码生成器——合起来覆盖真实硬件厂商代码生成流水线（本仓的真实原型）最恶劣的两类依赖形态。

## 内部结构

**mathutils 两个 perl（38/104 行）**：gen_mathutils_h.pl:14-31 与 gen_mathutils_c.pl 的 heredoc 内容全部被 'q' 字符填充——`iqnqtq aqddq(...)`、`#qiqnqcqlquqdqeq q"qmqaqtqhquqtqiqlqsq.qhq"q`——直到 gen_mathutils_h.pl:33 与 gen_mathutils_c.pl:99 的 `=~ s/q//g;` 一刀切掉所有 q，写出正常的 mathutils.h（10 声明）与 mathutils.c（10 实现：add/subtract/multiply/divide/power/factorial/gcd/lcm/is_prime/fibonacci）。

**protocol/generate_protocol.py（258 行）**：九个函数三段分工——解析段 parse_protocol_spec（L17-42，手写 MESSAGE/FIELD 行解析器，# 注释跳过）+ c_type_for_field（L44-51，string→const char*/int→int/其余→void*）；模板段 generate_header（L53-80，动态 guard 的 typedef struct 头）+ generate_encoder（L82-115，"消息名|"前缀+逐字段 snprintf 竖线拼接）+ generate_decoder（L117-159，strndup+strtok 切分、首 token 校验消息名）+ generate_free_function（L161-179，string 字段强转 free）；编排段 main（L181-255）：L204-207 头名 `md5(spec全文+seed)[:8]`、L223-252 每消息以 `hash_idx=(i*3)%32` 取 md5(seed) 三连位命名 encode/decode/free 三件套、L255 打印 `HEADER_FILE=` 契约行。

## 外部连接

- protocol.spec（21 行 DSL，L7-18 声明 LoginRequest/StatusUpdate/DataPacket 三消息）+ SEED 是 generate_protocol.py 的两个输入；**spec 全文按字节参与头名哈希**（L202-204 读文件全文拼接），尾部空行都是哈希输入。
- 下游即盘上那套过期产物：protocol_0d23cd47.h（3 struct+9 声明，guard PROTOCOL_0D23CD47_H）+ proto_impl/ 九个 .c（每个恰好 1 个函数）+ 九个 .o + libprotocol.so。
- Make 侧 protocol/Makefile:17 靠 grep 生成器 stdout 拿头名；Bazel 侧 protocol_rules.bzl:38-46 把动态头与 .c 拍平进同一 tree artifact，回调 :78-79 按扩展名分头/源、一个 -I 全解决。
- mathutils 的下游只有一个抽象消费者：main.c:11 的 include 与 Bazel 侧 mathutils_rules.bzl:143 的 hdr_out cp（"唯一让步"，docstring 自辩这是规则接口属性）。

## 数据流

**protocol 双哈希链**（本仓最精妙的设计）：头名链 `md5(protocol.spec 全文 + '22797')[:8]` 与源名链 `md5('22797')[i]` 完全独立——同一 seed、两级哈希、不同输入。按当前盘上 SEED 重算：头名=cfb3dca6、源名前缀=6/c/b、e/9/8、6/b/0；盘上却是 0d23cd47 与 0/1/3、5/7/a、b/e/e。**结论：整套入库产物出自历史 seed**（暴力扫描 0-2M 未命中当前 spec 的匹配 seed，真实 seed 更大或 spec 曾改版）。重跑生成器会在 proto_impl/ 留下新旧两套文件并存——模式 5 的"不可预测名"连产物管理都成了难题，只有 clean（protocol/Makefile:40 连 protocol_*.h 一起删）能收拾。

**mathutils 单文件链**：两个 perl 并行各写一文件 → mathutils.c 里的 `#include "mathutils.h"`（被 q 混淆掩埋在生成器里，只有产物里可见）→ .i 规则依赖生成头（mathutils/Makefile:28）。

## 设计决策

1. **q 混淆不是加密，是"语义噪声"**：它精准打击静态依赖分析——扫描 gen_mathutils_c.pl 找 #include 会得到 `q"qmqaqtqhquqtqiqlqsq.qhq"`这样的乱码，README.md:182 "Perl 脚本不含依赖信息"在本仓是字面事实。选 'q' 大概因为 C 代码里 q 罕见（本例内容零自伤）。
2. **两级哈希不同源**：源名只依赖 seed（好复算），头名掺入 spec 全文（改 spec 即换头名）——刻意让"改协议定义"与"换种子"产生不同的文件名扰动半径。
3. **竖线文本协议**：encode/decode 用 strtok('|') 是演示级弱协议（字段值含 '|' 即注入），README.md:207 已声明 gcc/协议都是替身，别按生产协议标准苛责。
4. **stdout 契约**：L255 `HEADER_FILE=` 行是生成器与 protocol/Makefile:17 的隐式接口——跨进程传动态文件名的最朴素方案，代价是任何 stdout 噪声都会破坏 grep。

## 新人提示

三个验证动作帮你吃透这对双子星（均无需编译）：① `python3 -c "import hashlib;print(hashlib.md5(b'22797').hexdigest())"` 得 6cbe986b…，对照盘上 proto_0/1/3/5/7/a/b/e 立见不符；② 读 gen_mathutils_h.pl 任一行在心里删掉所有 q，即可"人肉运行"生成器；③ 对照 protocol.spec:7-18 三消息与 protocol_0d23cd47.h:8-24 三个 struct 的字段一一对应关系（username/password、code/message、id/payload/size），能直观看到 spec→头的全息映射。注意 free 函数对 `const char*` 字段的 `(void*)` 强转 free（proto_e_free.c:9-10）是 const 语义与释放需求的妥协写法，真实项目应统一所有权约定。

（04/04 · 锚 21 处）
