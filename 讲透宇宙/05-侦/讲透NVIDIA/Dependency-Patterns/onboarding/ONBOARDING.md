# Dependency-Patterns 上手指南（ONBOARDING）

> NVIDIA 官方"代码生成依赖模式基准"仓库：5 个 C 模块 × 5 种构建依赖推断挑战，Make 与 Bazel 双轨解法并存。图谱 124 节点/159 边/9 层/14 步 tour（fingerprints 57 文件 @84a1450f）。本指南所有行号锚均经源码核实。

## 1. 这个仓库是什么（一句话定位）

一个刻意制造构建系统难题的 C 演示项目：5 个模块各自展示一种"依赖无法静态推断"的形态，README.md:6-8 点明动机——"每个 Makefile 都手写了全套依赖，期望是它们能被自动推断"。gcc/make 只是替身，README.md:207 明言"这些命令与文件类型是专有代码生成工具与流程的替身"。真正的展品不是 demo 程序本身，而是 Make/Bazel 两套构建系统如何对付"文件名在生成前不可知"的世界。

## 2. 五大依赖模式（仓库的骨架）

README.md:164-197 逐一定义，从易到难：

| 模式 | 模块 | 挑战 | 关键证据 |
|---|---|---|---|
| 1 可推断 | strutils | 单源单头，#include 扫描即可 | strutils/Makefile:25 手写 .i 依赖 |
| 2 多源共享头 | utils | memory.c+validation.c 同头 | utils/Makefile:29-33 双 .i 规则 |
| 3 生成依赖 | mathutils | 头源均由 perl 生成，依赖藏在生成物里 | gen_mathutils_c.pl:99 `s/q//g` 去混淆 |
| 4 不可预测名 | io | 生成源文件名=md5(seed) 前缀 | io/generate_io.py:238-244 |
| 5 动态名头+源 | protocol | 连头文件名都是哈希 | generate_protocol.py:204-207 |

模式 5 是 3+4 的叠加：generate_protocol.py:204 头名取 `md5(spec全文+seed)[:8]`，:228/:237/:246 源文件名取 `md5(seed)` 的不同位——两级哈希不同源，改 spec 尾部一个空行都会换掉全部文件名。

## 3. 总体架构与目录地图

```
Dependency-Patterns/
├── main.c              # 演示入口（链接 4 库，不含 protocol）
├── Makefile / BUILD    # 双轨顶层编排（口径一致：MODULES=4 模块）
├── strutils/           # 模式1：strutils.c(116行14函数)+strutils.h
├── utils/              # 模式2：memory.c(16函数)+validation.c(8函数)+utils.h
├── mathutils/          # 模式3：gen_mathutils_{c,h}.pl 两个 q 混淆生成器
├── io/                 # 模式4：generate_io.py+静态 io.h+SEED
├── protocol/           # 模式5：protocol.spec+generate_protocol.py+SEED
│   └── proto_impl/     # 9 个生成 .c + 9 个 .o（全部入库，过期产物）
├── .bazel_rules/       # Bazel 解法核心：4 条 .bzl+scan_includes.py+compile_c.sh
└── scaling/            # 规模化示例依赖图（已裁出图谱；.bazelignore:1 同样排除）
```

三段式构建贯穿全仓：`.c →(gcc -E)→ .i →(gcc -c)→ .o →(gcc -shared)→ .so`（README.md:203-205），Makefile 全部按此拆规则——这是模拟"专有代码生成器流水线"的刻意设计。

## 4. 双轨构建系统对照

**Make 轨（手写依赖的痛苦样本）**：根 Makefile:10 `MODULES = mathutils strutils io utils` 递归 make -C；io/Makefile:21-22 用 `$(shell python3 generate_io.py $(SEED) …)` 在变量展开期（非执行期）跑生成器来发现文件清单；protocol/Makefile:17 更进一步 `grep 'HEADER_FILE='` 从生成器 stdout 截取动态头名——生成器与 Makefile 存在隐式 stdout 契约（generate_protocol.py:255 是契约另一端），且每次 make 解析生成器可能被跑两遍。

**Bazel 轨（自动推断的参考实现）**：核心在 cc_rules.bzl。Phase1（cc_rules.bzl:77-87）跑 ScanCIncludes 动作；Phase2（:91-98）map_directory 回调在**执行期**解码 marker 文件名（:33-43，格式 `<src_idx>.deps_<dep_idx>.marker`，注释 :7 称约定来自 adventures_in_map_directory）逐源编译；Phase3 链接 .so 并组装 CcInfo。scan_includes.py:18-26 只认引号 #include 且只比 basename；:37 把依赖编码进 marker 文件名。io/mathutils/protocol 三条规则（io_rules.bzl/mathutils_rules.bzl/protocol_rules.bzl）用 tree artifact 吸收不可预测名：生成器写进目录产物，回调执行期枚举内容，如 protocol_rules.bzl:43 把动态头与 .c 拍平进同一目录后一个 -I 全解决。

## 5. 生成器与哈希链（仓库的灵魂）

三个生成器三种语言三种策略：
- **perl+混淆**：gen_mathutils_c.pl:99 去混淆后写出 10 个数学函数；heredoc 里的 `iqnqtq aqddq(…)` 之类 q 填充让 #include 依赖在生成器源码中字面不可见——模式 3 的挑战是动真格的。
- **python+一级哈希**：io/generate_io.py:238-244 五组实现（file/text/binary/dir/console）分别以 md5(seed)[0..4] 命名；:246-257 重名字符追加 `_<counter>` 消歧。
- **python+两级哈希**：generate_protocol.py 解析 protocol.spec:7-18 的三消息（LoginRequest/StatusUpdate/DataPacket）DSL，每消息生成 encode/decode/free 三件套共 9 个 .c + 1 个动态名头。

**重磅甄别——盘上产物是过期哈希链**：按当前 protocol/SEED=22797 重算，头名应为 `protocol_cfb3dca6.h`（md5(spec+22797)[:8]），源名前缀应为 6/c/b/e/9/8/6/b/0；但盘上是 `protocol_0d23cd47.h` 与 0/1/3/5/7/a/b/e（暴力反推 0-2M 未找到匹配 seed）。整套 protocol_0d23cd47.h+9 .c+9 .o+libprotocol.so 均为历史 seed 的遗留产物，重跑生成器会产出全新一套名字而旧文件残留（只有 clean 清理）。

## 6. 关键数据流（一次 make 的完整旅程）

以 `make run` 为例：根 Makefile 先按 MODULES 顺序递归各子目录 → mathutils 跑两个 perl 生成 mathutils.c/h → io/protocol 在变量展开期就执行 python 生成器 → 各模块走 .c→.i→.o→.so → lib*.so 拷回根目录 → main.c 预处理时解析四个 include（main.c:11 的 mathutils/mathutils.h 此刻才存在）→ 链接 demo → main.c:16 起 main() 依次演示四模块 API。Bazel 轨等价旅程：bazel 分析期只看 BUILD 声明，全部文件名发现推迟到执行期回调，动作图仍显式声明每个 .c 的输入输出（io_rules.bzl:12-15 docstring 自述这是 incremental build 与 sandboxing 正确性的来源）。

## 7. 甄别与勘误清单（源码实证）

1. **protocol 产物过期**（上节详述）——盘上 .c/.o/.so 与当前 SEED 哈希链不符。
2. **strutils"不引自头"是改名事故非设计**：README.md:17 明说模块 `renamed from string`——strutils.c:6 引号 `#include "string.h"` 原是引号包含自家旧头 string.h 的残留（现在 fallback 到系统头）、strutils.h:6-7 guard 叫 `STRING_H` 而非 STRUTILS_H 同为化石；"strutils.c→strutils.h" 依赖只活在 strutils/Makefile:25 的手写规则里。
3. **strcasecmp 隐式声明**：strutils.c:24-27 用 strcasecmp 却未 include <strings.h>，-Wall 下有隐式声明警告。
4. **io_rules.bzl:141 rstrip 坑**：`header.dirname.rstrip("/io")` 删的是字符集不是后缀——dirname='io' 恰好全由被删字符组成才得到空串（workspace root）；目录名若含集合外字符即出错，属碰巧正确。
5. **mathutils_rules.bzl:143 的"唯一让步"**：显式 cp 生成头到 bin/<pkg>/，docstring 自辩这是"规则接口属性而非生成文件内部依赖"。
6. **.o/.so 构建产物入库**：9 个 .o 与 libprotocol.so 均提交 git，属基准形态特例（供不跑构建者检视）。
7. **README"5 模块构建"与实际 4 模块**：README.md:216-223 列 5 个 `make -C`，但根 Makefile:10 MODULES 只有 4 个（protocol 排除），BUILD:4-5 注释与 Makefile 口径一致。
8. **生成的 mathutils.c 含 subtract() 但 main.c 未调用**（生成器模板 10 函数 vs main 演示 8 个）。

## 8. 上手路线（按 tour 14 步）

1. 读 README.md 全文（258 行，含 5 张 graphviz 依赖图）→ 2. 对照根 Makefile 与 BUILD 看 4 模块编排 → 3. 跑读 main.c 找 mathutils.h 盲区 → 4-6. 按 strutils→utils→io 顺序读三个"静态/半静态"模块 → 7-8. 精读两个生成器（perl 混淆版与 io 哈希版）→ 9. 对读 io/protocol 两个 Makefile 的 $(shell) 野路数 → 10-13. protocol 全链（spec→生成器→过期产物→.o/.so 实体）→ 14. 收官 .bazel_rules/ 四条规则，重点 cc_rules.bzl 的 marker 协议与三条 tree artifact 规则的差异。深入单文件可接着读同目录 explain/ 系列四篇精讲。

（完 · 2026-11-07 · 锚点 38 处，全部源码核实）
