# Neo-OS · 方法论继承层（Methodology）

> 本目录是 **Neo-OS 与 work4ai 的契约层**——不复制 work4ai 任何内容，
> 只建立"引用什么、对应到哪层、如何 trace-native 升级"的映射。
>
> work4ai 不仅是知识库，**是 Neo-OS 解释引擎的方法论内核**。
> 详见 [02-research/LOCAL_ASSETS.md](../02-research/LOCAL_ASSETS.md) 的完整资产映射。

---

## 为什么单独成目录？

| 之前 | 现在 |
|---|---|
| work4ai 关系藏在 `LOCAL_ASSETS.md` 一份文档里 | **结构本身就是契约**——任何人 `ls 03-methodology/` 就懂 |
| L3 实现散在 prototype，看不到方法论来源 | L3 实现引用本目录，**provenance 一目了然** |
| "trace-native 升级"是隐含的设计 | 单独成文，可作为论文 contribution 章节 |

---

## 本目录文件

| 文件 | 内容 |
|---|---|
| [`from-work4ai.md`](./from-work4ai.md) | **引用索引**：work4ai 每个核心资产 → Neo-OS 哪一层 → 当前用途与状态 |
| [`trace-native-upgrade.md`](./trace-native-upgrade.md) | **Neo-OS 原创贡献**：把 work4ai 的"代码实证层"升级为"trace 实证层"的设计 |

---

## 核心契约（5 条，源自 [02-research/LOCAL_ASSETS.md](../02-research/LOCAL_ASSETS.md) §4）

调用 work4ai 资产时必须遵守：

1. **方法论优先**：先复用"三层 × 17 视角 × 费曼"方法论，再取具体技术
2. **三层互锁**：任何引入的概念，必须三层呈现（直觉→数学→trace 证据）
3. **费曼把关**：任何解释，必须过 F1-F4 检验
4. **trace 接地**：work4ai 的"代码实证层"在 Neo-OS 里升级为 trace 实证
5. **诚实标注 provenance**：每个资产标注来源路径 + 对 Neo-OS 的具体映射

---

## 与四层架构的对应

```
L3  English Interface  ← 继承 work4ai 三层讲解 × 17 视角 × 费曼门
L2.5 Formal Rules      ← 借鉴 work4ai 讲透因果推断/符号主义/控制论
L2  World Model        ← 借鉴 work4ai 讲透基础模型/世界模型/微调
L1  Event Ontology     ← 借鉴 work4ai 讲透分布式AI系统/GPU与系统级
L0  Hardware           ← 借鉴 work4ai 讲透GPU（FlashAttention/量化）
```

每个具体引用见 [`from-work4ai.md`](./from-work4ai.md)。

---

*本目录是"声称-验证差距校正"的结构化抓手。任何 Neo-OS 解释引擎的声称，
必须能回到这里，指向 work4ai 的具体方法论文件作为 provenance。*
