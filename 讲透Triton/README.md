# 讲透 Triton · GPU Kernel 语言与编译器全量知识库

> **triton-lang/triton（NVIDIA 维护）** @ commit `e08ec196`（2026-09-02）· 收官补齐 2026-09-20
> 三步流水线：DeepWiki 全量镜像（09-05 已抓）→ understand 中文知识图谱（本轮）→ onboard + explain 精讲（本轮）

Triton 是用 Python 写 GPU kernel 的开源语言与编译器（OpenAI 发起、NVIDIA 维护）：`@triton.jit` 装饰 Python 函数 → AST 经 TTIR/TTGIR（MLIR）四级 IR 优化 → 降级 LLVM → PTX/cubin。FlashAttention 等顶级算子均由此产出。

---

## 📦 资产导航

| 资产 | 内容 | 位置 |
|---|---|---|
| **DeepWiki 镜像** | 54 页（09-05 抓取）：语言/内核/编译器/调试/后端/实验特性 | [`deepwiki/`](./deepwiki/) |
| **知识图谱** | **2793 节点 / 5559 边 / 13 层架构 / 15 步导览**（file 490 + function 1592 + class 630 + document 57；imports 1559 全量对账；0 issues，fingerprints 487 code 基线） | 仓内 `.understand-anything/knowledge-graph.json`（2.4MB） |
| **新人上手指南** | 8 节 5991 字 | [`onboarding/ONBOARDING.md`](./onboarding/ONBOARDING.md) |
| **重要文件精讲** | 6 篇×六节结构 | [`explain/`](./explain/) 见下表 |

### explain 六篇（按学习顺序）

| # | 文件 | 主题 |
|---|---|---|
| 1 | [language-core.md](./explain/language-core.md) | tl DSL 语义心脏：builtin/_semantic 注入、tl.dot→builder.create_dot |
| 2 | [runtime-jit.md](./explain/runtime-jit.md) | JITFunction：依赖 hash、参数特化、两级缓存、run() 五步 launch |
| 3 | [compiler-driver.md](./explain/compiler-driver.md) | 编译驱动：compile() 六步、CompiledKernel 装载与缓存 |
| 4 | [make-ttgir.md](./explain/make-ttgir.md) | TTGIR 优化编排（真身 third_party/nvidia/backend/compiler.py L292-377） |
| 5 | [autotuner.md](./explain/autotuner.md) | @triton.autotune：多配置基准、prune/热身/缓存 |
| 6 | [triton-kernels.md](./explain/triton-kernels.md) | triton_kernels 参考算子库工业化写法 |

---

## 🗺️ 十三层架构速览

```
Python 前端                              MLIR C++ 后端
├─ 包入口与全局设施 14                    ├─ Dialect/IR 核心 193
├─ language DSL 语义层 9                  ├─ 转换 Pass 与分析 75
├─ 编译器前端驱动 5                       ├─ 编译器工具(bin) 6
├─ 运行时与后端抽象 13                    └─ Gluon/GSAN 实验 61
├─ pybind11 C++ 桥接 11
└─ Python 工具链 22 + triton_kernels 73
横切：构建体系 62 · CI/CD 与文档 27
```

编译主线一句话：**Python 语义 → AST 访问器 → TTIR（架构无关）→ TTGIR（布局/流水线，pass 编排在 third_party/nvidia/backend/compiler.py）→ LLVM IR → PTX → cubin**。

## 🚀 推荐路径

1. **30 分钟版**：ONBOARDING §1-3 → explain #1/#2（DSL+jit）
2. **半天版**：+ explain #3/#4（编译管线深潜）+ DeepWiki 编译器章
3. **深度版**：图谱 tour 15 步（全景→包门面→tl DSL→jit→编译驱动→TTIR/TTGIR→软件流水→LLVM→后端启动→调优→算子库→C++ 深潜×2→Gluon/GSAN→构建）

## 关联

- 上游：https://github.com/triton-lang/triton
- 姊妹单元：[讲透TIRx](../讲透TIRx/README.md)（kernel 方向姊妹篇）· [讲透vLLM](../讲透vLLM/README.md)（消费方）· [讲透MLC-LLM](../讲透MLC-LLM/README.md)（同类编译路线 TVM 系）
- 13 仓流水线收官仓之二（2026-09-20）
