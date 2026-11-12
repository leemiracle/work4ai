# 讲透 cuda-tile（NVIDIA CUDA Tile IR）

> NVIDIA 开源 MLIR dialect + bytecode 序列化层——闭源 tileiras 编译器（93.9MB，驱动 590 系内）的开源 IR 侧，对齐 **CUDA Toolkit 13.1**。本目录=cuda-tile 仓 understand 全链知识基座（图谱+onboarding+explain 12 篇）。

## 全链状态表

| 阶段 | 状态 | 产出 |
|---|---|---|
| deepwiki | —（本仓走 understand 图谱线，DeepWiki 未收录） | — |
| understand 图谱 | ✅ 2026-11-06 | 仓内 `.understand-anything/knowledge-graph.json`：**720n/1128e/16 层/15 步 tour，validator 0 issues 0 warnings，fingerprints 267@5b3fa4c0** |
| onboarding | ✅ 2026-11-06 | `onboarding/ONBOARDING.md`（8 节 6848 字符不计空格，34 锚全源码实证，终版抽验 10/10） |
| explain 12 篇 | ✅ 2026-11-06 | `explain/01-12` 合计 **64742 字符不计空格**，全量随机抽验 **90 锚 0 坏**（组1 核心链路 6 篇 243 锚+组2 外围工具测试 6 篇 68 锚，行号锚全源码核实） |

## 批分析战况（17 批）

四 worker 并行（1-4/5-8/9-12/13-17），两次进程级中断（1308/进程退出）均死前落盘+SendMessage 复活零重做。merge 720n→1128e（前缀错位悬空边 5 条全回补）；预检 267/267 文件全覆盖零跨批重复。分片合法产出：batch-2×3/batch-8×2/batch-11×3。

## 甄别精选（worker 源码级实证）

1. **covertSyntaxToSignature 系 upstream 拼写笔误**（SpecGen.cpp，应为 convert）——按源码保留并 notes 标注
2. **IncludeLLVM.cmake L29 实钉 LLVM commit c495a9b796c4** 与本仓 HEAD [LLVM-FIX] 提交一致，而 README 兼容区间表**滞后未列**
3. **BytecodeOpcodes 0x19-0x24 与 0x34-0x39 双跳洞坐实且无注释解释**（Exp2Op 0x18→ExtIOp 0x25）；Float8E5M3FNU（13.4）用 tag 0x82 **跳号预留 23-0x81**——操作码空间是版本演化的活化石
4. **Ops.td 精确口径：105 具体操作+2 辅助类型 def**（批分析初判 107 op 被 explain 组1 按源码精化）/10 分组，版本前向覆盖 13.2-13.4
5. **lib/Dialect/CudaTile/IR/CMakeLists 私有 include `../../../../compiler/include`**——印证本仓嵌入 tileiras 编译器仓的布局（开源侧只是闭源巨兽的露出面）
6. scanner 盲区三型钉版：纯声明头内部 #include 全盲（手补 13+24 条）、td/cmake/mlir 的 batchImportData 全空（TableGen include 手扫）、C 声明式头 tree-sitter 零提取（22 类节点手补）
7. fixture 魔数 `\x7fTileIR\0` + 版本字节 0d01-04 十六进制实证入 languageNotes（与逆向侧 libcuda 嗅探器发现同源互证）
8. C++ 方法重载同名 ID 冲突→按首重载建单节点+summary 注明重载族（fromTableGen×3 等）

## 与 CUDA-Stack-RE 逆向战役的互证关系

本仓图谱是 `work4ai/讲透CUDA-Stack-RE/REPORT.md` §9.2 TileIR 开源闭环的源码侧延伸：
- 逆向侧（libcuda 590.48.01）：fatbin entry **kind 0x80=TileIR**+nvJitLink 嗅探 magic `\x7fTileIR`+tileiras vtable 11 函数
- 开源侧（本仓）：BytecodeWriter.cpp:195 写同款 8B magic；`.tilebc` 12B 头（magic8+major u8+minor u8+tag u16LE）+8 类 Section；**注释勘误两条**（padding 实际 0xCB 非 0xCF；版本域定宽 LE 非 varint）
- 解析器：`reverse/cuda-stack/tools/tilebc_parser.py`（双验证通过）

## 工具

- 图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/cuda-tile/.understand-anything/`（knowledge-graph.json+fingerprints，支持增量更新）
- 流水线：pipeline-bin/understand/ 全套（prepare→dispatch→merge→fix_edge_prefixes→phase4→layers/tour→finalize→onboard_prep）

*2026-11-06 · cuda-stack 第七轮会话（舰队认领线）*
