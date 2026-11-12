# 03 · io/generate_io.py——语料生成器：MD5 决定文件名的艺术

## 角色定位

模式 4 的发电机：266 行 python 把一个整数 seed 变成 5 个名字无法预知的 C 实现文件。它演示的挑战是构建系统的经典噩梦——"构建输入的文件清单本身是构建产物"。Make 侧被逼出 `$(shell)` 野路数、Bazel 侧被逼出 tree artifact+map_directory，全部源起于此。与本仓另两个生成器（perl 混淆版、spec 驱动版）不同，它是唯一"内容固定、只有名字随机"的生成器。

## 内部结构

三段式结构清晰：

- **哈希原语 L9-10**：`md5sum(text)` 一行封装，str→hexdigest，是命名链的起点。
- **五个内容模板 L16-217**：generate_file_ops（L16，48 行，file_exists/file_size/file_copy/file_delete，含 stat 与逐字节 fgetc 复制）、generate_text_ops（L67，读/写/追加三函数，fread 后补 '\0'）、generate_binary_ops（L109，整块读写并严格校验字节数）、generate_dir_ops（L137，mkdir 0755/rmdir/readdir 跳过点号目录）、generate_console_ops（L176，print 三连+fgets 去换行+scanf 判 1）。每个函数接收 filename 入参但**忽略不用**（L17 起首行 `return '''#include "io.h"` 与参数无关），返回的是整段 C 源文本。
- **命名与落盘 L219-263**：main 校验整数参数（L220-228 两层防护）→ `md5_hash = md5sum(integer_arg)`（L231）→ L238-244 把 hash 前 5 个字符分别配给五组实现：`io_impl_{hash[0]}.c`=file、`{hash[1]}`=text、`{hash[2]}`=binary、`{hash[3]}`=dir、`{hash[4]}`=console → L246-257 重名消歧（十六进制字符只有 16 种，五文件必撞 16 种内重复：while 循环给撞名文件追加 `_<counter>`）→ L259-263 逐个写入 io_impl/ 并打印 Generated: 清单。

## 外部连接

- **上游**：io/SEED（单行整数 8472997）由 io/Makefile:20 的 `SEED = $(shell cat SEED)` 喂进来；命令行调用点两处——io/Makefile:21-22（变量展开期发现文件清单）与 :29-30（生成规则）；Bazel 侧 io_rules.bzl:44-58 在 mktemp 临时目录里跑它再 cp 进 tree artifact。
- **下游**：五个 io_impl_*.c 全部第一行 `#include "io.h"`（模板 L17/68/110/138/177），由 io_library 回调以 -I 指向 io.h 目录编译（io_rules.bzl:100-102）。
- 产物目录 io_impl/ **不入库**（盘上不存在），与 protocol 模块的"产物入库"策略形成对照。

## 数据流

seed 整数 → md5 十六进制串 → 前 5 字符作文件名前缀（当前 SEED=8472997 → md5='1ee0573ba2…' → 名义上生成 io_impl_1.c/io_impl_e.c/io_impl_e_1.c（消歧）/io_impl_0.c/io_impl_5.c）→ 五段 C 文本写入 io_impl/ → Make 变量展开期 glob 拿到清单 → .i/.o/.so 流水线。文件名与文件内容的**配对关系**（哪个名字装哪组实现）完全由 hash 字符位置决定，且消歧计数会进一步打破"hash 字符=文件名"的朴素预期——README.md:188 所说 "unpredictable generated file names" 是双层的：不看 seed 算不出名字，看了 seed 也得复现消歧逻辑才知道最终名。

## 设计决策

1. **为什么用 md5 而不是随机数**：确定性哈希保证同 seed 同输出，构建可复现；同时名字对"没跑生成器的人"完全不可预测——这正是要考构建系统的点。
2. **内容与命名解耦**：五个模板函数纯粹返回文本，命名逻辑集中在 main 的 L238-257——生成器自身的依赖图（模板间零调用）保持最简，让读者聚焦命名机制。
3. **消歧 while 循环**（L246-257）：诚实处理"hash 前缀碰撞"这一必然事件（5 个取自 16 种字符），而不是假设 seed 会避开碰撞——比很多真实项目的生成器严谨。

## 新人提示

验证命名链不必编译：`python3 -c "import hashlib;print(hashlib.md5(b'8472997').hexdigest())"` 得 1ee0573ba2…，前 5 字符 1/e/e/0/5 就是五组实现的前缀（第三组撞 e 被消歧成 e_1）。注意 generate_io.py L12-14 的 create_io_impl_dir 用相对路径 'io_impl'——生成器必须在 io/ 目录下运行（Bazel 侧 io_rules.bzl:52-57 专门 cd 进临时目录再以 $OLDPWD 引用脚本就是这个原因）；另外 L220-221 的 usage 提示 `python3 generate_io.py <integer>` 传非整数会 exit(1)，Makefile 传的 $(SEED) 来自 cat SEED，SEED 文件被改坏时错误会出现在 make 解析期而非执行期——排查时先看变量展开。

（03/04 · 锚 19 处）
