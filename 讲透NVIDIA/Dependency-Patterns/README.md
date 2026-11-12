# 讲透 Dependency-Patterns（NVIDIA/Dependency-Patterns）

NVLink 团队的"代码生成依赖模式基准"仓库：5 个 C 模块 × 5 种构建依赖推断挑战，Make 与 Bazel 双轨解法并存，gcc/make 三段式流水线是专有代码生成工具的替身。本目录是 understand 全链知识库产物。

## 全链状态表

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki | —（本仓走 understand 图谱路线，无独立 deepwiki 步） | — |
| prepare | ✅ 2026-11-07 | 57 文件/5 批（scaling/ 语料已按 .understandignore 裁剪） |
| 批分析 | ✅ 5/5 批（batch-1..5.json+.bak） | C #include 手扫补 9 条 scanner 盲区边；tree-sitter C 盲区补 12 函数 |
| merge | ✅ 124n/159e（0 悬空丢弃/0 recovery） | .understand-anything/knowledge-graph.json |
| layers/tour | ✅ 9 层/14 步（124/124 全覆盖零重复） | 同上 |
| validate | ✅ 0 issues 0 warnings | fingerprints 57 文件 @84a1450f |
| onboarding | ✅ 4451 字符 8 节 26 锚 0 坏 | onboarding/ONBOARDING.md |
| explain | ✅ 4 篇 9857 字符 41 锚 0 坏 | explain/01..04 |
| README | ✅ 本文件 | — |

## 仓库速览

- **定位**：README.md:6-8——"每个 Makefile 都手写了全套依赖，期望是它们能被自动推断"；命令与文件类型是专有代码生成流程的替身（:207）。
- **五模式**：①strutils 单源可推断 ②utils 双源共享头 ③mathutils 生成依赖藏生成器（perl q 混淆） ④io 生成源名不可预测（md5(seed) 前缀） ⑤protocol 动态名头+源（两级哈希，3+4 叠加）。
- **双轨构建**：Make 手写依赖+$(shell) 野路数；Bazel 9.1.1 自定义规则（cc_rules.bzl 的 marker 协议 + io/mathutils/protocol 三条 tree artifact 规则，map_directory 执行期发现）。
- **主链 4 模块**：根 Makefile:10 MODULES 与 BUILD:7-12 一致排除 protocol（BUILD:4-5 注释明示原因）。

## 甄别精选（全部源码/哈希重算实证）

1. **盘上 protocol 产物是过期哈希链（重磅）**：当前 protocol/SEED=22797 重算头名应为 protocol_cfb3dca6.h（md5(spec+seed)[:8]）、源名前缀 6/c/b/e/9/8/6/b/0；盘上却是 protocol_0d23cd47.h 与 0/1/3/5/7/a/b/e——入库的 1 头+9 .c+9 .o+libprotocol.so 全部出自历史 seed（暴力 0-2M 未反推出匹配 seed），重跑生成器将新旧并存。
2. **strutils"不引自头"是改名事故**：README.md:17 `renamed from string` 三化石互证——strutils.c:6 引号 `#include "string.h"`（原自家头名）、strutils.h:6 guard `STRING_H`、Makefile:25 被迫手写依赖；strutils.h 实际 14 声明与 14 实现一一对应。
3. **mathutils perl 生成器 q 混淆**：gen_mathutils_c.pl:99 `s/q//g` 去混淆——#include 依赖在生成器源码中字面不可见，模式 3 的挑战动真格。
4. **io_rules.bzl:141 rstrip 字符集陷阱**：`dirname.rstrip("/io")` 恰因目录名 'io' 全由被删字符组成才得到空串，属碰巧正确。
5. **strcasecmp 隐式声明**：strutils.c:24-27 未 include <strings.h>。
6. **mathutils_rules.bzl:143 的"唯一让步"**：显式 cp 生成头到 bin/<pkg>/，docstring 自辩为规则接口属性。
7. **scanner 树盲区**：tree-sitter 对 proto_impl 9 个 .c 的 encode/decode 函数与 memory.c 前 3 个 safe_* 全漏（手补 12 函数节点）；C 仓 importMap 仅 5 条（手扫 #include 磁盘验证补 9 条 proto_impl→生成头）。
8. **io_impl/ 未入库**：io 模块生成产物目录盘上不存在（与 protocol 产物入库策略相反），io SEED=8472997 → md5 前缀 1/e/e/0/5。

## 产物目录

```
讲透NVIDIA/Dependency-Patterns/
├── README.md            # 本文件（状态表+甄别）
├── onboarding/ONBOARDING.md   # 上手指南（8 节）
└── explain/
    ├── 01-main-c-基准入口.md           # main.c：include 生成头的盲区+四段演示
    ├── 02-静态三模块-strutils-utils-io.md  # 模式 1/2/4 的静态侧+改名事故
    ├── 03-generate_io-py-语料生成器.md     # 模式 4 核心：MD5 命名+消歧
    └── 04-protocol与mathutils-生成侧双子星.md  # 模式 3/5：q 混淆+两级哈希+过期产物
```

图谱在仓内 `.understand-anything/knowledge-graph.json`（124 节点/159 边/9 层/14 步 tour，validator 0 issues，fingerprints 57@84a1450f，支持增量）。

## 裁剪说明

- `scaling/`（规模化示例依赖图，README.md:255-258 声明不参与主构建）已裁出图谱，与 .bazelignore:1 的 Bazel 排除口径一致。
- `MODULE.bazel.lock`（50KB 锁文件）按 *.lock 规则裁剪。
- `protocol/proto_impl/*.o` 与 `libprotocol.so` 为入库 ELF 构建产物，作为 benchmark 形态保留入图（带 stale-artifact 标签）。

（2026-11-07 · understand 全链收官）
