# tvm understand 图谱 · 全链产物

> apache/tvm 定制 fork @15b607d（2026-09-02 快照；tir→tirx+s_tir 拆分/src/target→src/backend 改名/LLM 定制线）· 产物 2026-11-10 · 真源本目录

## 状态

| 产物 | 规模 | 状态 |
|---|---|---|
| knowledge-graph.json | **10713 节点 / 21401 边 / 16 层 / 16 步 tour**（8.4MB） | ✅ validator 双验 0 issues 0 warnings |
| fingerprints 基线 | 1979 文件 @15b607d | ✅ 支持增量 |
| ONBOARDING.md | 8 节完整（~9k 字符） | ✅ |
| explain/ | 12 篇 54977 字符 | ✅ 工人自验 13 锚命中；主文件模型抽验 491 好锚（多文件篇 L 锚需上下文归位，见验证局限） |

## 裁剪口径

tests(680)/tutorials/docs/apps/docker/ci/jvm/web/3rdparty/licenses/cmake 全裁 → 1979 文件 + **补录 58 个 target 目录文件**（batch 73-75：scanner 把名为 target 的目录误判为构建产物跳过——src/target 40 含 LLVM 后端核心、python/tvm/target 13、include/tvm/target 5；落地后全仓 132 条悬空引用清零）。

## 批分析实录（72+3 补批 / 2037 文件，跨 3 个 1308 窗口）

- **旧代隔离**：intermediate/ 有 2026-09-21 旧轮 230 个批产物（旧批号体系），按 mtime 整体隔离至 ../old-20260921/ 后干净重跑——"计数含旧代假计数"坑钉版
- 手扫补 imports 合计 ~900 条（C++ .h 头零提取+include/-I 链全漏是主盲区；Python TYPE_CHECKING/延迟 import）
- fork 特征钉版（多批工人独立证实）：tir→tirx+s_tir 拆分、TVM_FFI_STATIC_INIT_BLOCK+refl::GlobalDef 取代 TVM_REGISTER_GLOBAL、tvm_ffi 独立外部包（3rdparty/tvm-ffi submodule 未 checkout 空目录实证）、KVCacheLegacy 直接继承 ffi::Object 绕开新体系
- tree-sitter 盲区实证：**src/target/llvm 全目录 #ifdef TVM_LLVM_VERSION 包裹致 25/40 文件零提取**（含 codegen_llvm.cc 2568 行），批 73 工人自建"注释剥离+预处理分支裁剪+花括号匹配"提取器恢复 186 函数+33 类；`Type* func(` 星号贴返回类型；.cu/.cuh/.mm 语言不支持零提取
- 源码勘误入 notes：unary.h 等 4 文件许可证头 'See'→'Sex' 篡改、view.h ensure_aligned 死声明（实现已更名 ensure_zero_offset）、lift_thread_binding.cc 等 3 文件头注释残留旧文件名、gpu_generic docstring 误写 Metal、sm90/sm100 注册同名全局靠架构宏互斥

## 16 层速览

根配置 CI(39) → include 公共头三域(104+51+34) → python 包入口/FFI(76) → python ir/te/arith(120) → python tirx(138) → python relax 前端(212) → python topi(70) → python s_tir/dlight/meta(107) → python backend/target(178+13 补) → src ir/tirx 核心(162+217) → src s_tir/relax(176+136) → src 后端 codegen(159+40 补) → src runtime(212+含 contrib) → CI/github/杂项

## 使用

- 新人：ONBOARDING.md → tour 16 步 → explain/ 12 篇（FFI→Pass→tirx→调度→dlight→meta_schedule→relax→PagedKVCache LLM 线→LLVM 后端→VM→topi）
- agent：knowledge-graph.json（10713n）+ work4ai/讲透TVM
- 增量：代码变更后重跑 prepare（fingerprints 跳过未变）
