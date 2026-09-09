# Lean4 AI 知识库项目

**形式化验证 + AI辅助 + 知识词典 + 代码验证的完整解决方案**

包含 **900,000+ 字** 的知识词典系统，整合 **8大开源项目**。

---

## 快速导航

| 文档 | 描述 |
|------|------|
| [START_HERE.md](./START_HERE.md) | 快速开始指南 |
| [DICTIONARY_INDEX.md](./DICTIONARY_INDEX.md) | 文档索引 ⭐ |
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | 快速参考 |
| [LEARNING_PATHS.md](./LEARNING_PATHS.md) | 学习路径 |

---

## 词典系统

### AI & LLM → [docs/ai/](./docs/ai/)
- [LLM核心词典](./docs/ai/LLM_CORE_DICTIONARY.md) - Transformer、训练、推理
- [模型大全](./docs/ai/MODEL_ENCYCLOPEDIA.md) - 40+模型详解
- [AI Agent指南](./docs/ai/AI_AGENT_GUIDE.md) - Agent架构与协作
- [AI应用开发](./docs/ai/AI_APP_DEVELOPMENT.md) - Prompt、RAG、部署

### 数学 → [docs/math/](./docs/math/)
- 12卷完整数学词典
- [索引](./docs/math/MATH_DICTIONARY_INDEX.md)

### 物理 → [docs/physics/](./docs/physics/)
- 7卷物理学词典
- [索引](./docs/physics/PHYSICS_INDEX.md)

### 哲学 → [docs/philosophy_dictionary/](./docs/philosophy_dictionary/)
- 8卷哲学词典

### 其他
- [人类学词典](./docs/anthropology_dictionary/)
- [百科全书](./docs/encyclopedia/)
- [军事词典](./docs/military_dictionary.md)

---

## 整合项目

| 项目 | 类型 | 描述 |
|------|------|------|
| [Lean4](https://github.com/leanprover/lean4) | 编程语言 | 定理证明器 |
| [Mathlib4](https://github.com/leanprover-community/mathlib4) | 数学库 | 100万+行代码 |
| [YC-Killer](https://github.com/sahibzada-allahyar/YC-Killer) | AI代理 | 7个企业级代理 |
| [Awesome Agile](https://github.com/lorabv/awesome-agile) | 敏捷实践 | 最佳实践 |
| [Leantime](https://github.com/Leantime/leantime) | 项目管理 | 神经多样性友好 |
| [LeanDojo](https://leandojo.org) | ML工具 | ML+定理证明 |
| [Aeneas](https://github.com/AeneasVerif/aeneas) | 验证工具 | Rust验证 ⭐ |

---

## 技术文档

### Lean4 → [docs/lean4/](./docs/lean4/)
- [Mathlib指南](./docs/lean4/MATHLIB_GUIDE.md)
- [项目分析](./docs/lean4/LEAN4_PROJECTS_ANALYSIS.md)
- [生态报告](./docs/lean4/LEAN_ECOSYSTEM_REPORT.md)

### 集成文档 → [docs/integrations/](./docs/integrations/)
- [最终整合](./docs/integrations/FINAL_INTEGRATION.md)
- [LeanDojo集成](./docs/integrations/LEANDOJO_INTEGRATION.md)
- [YC-Killer集成](./docs/integrations/YCKILLER_LEAN4_INTEGRATION.md)
- 等16个集成文档

### 概览文档 → [docs/overviews/](./docs/overviews/)
- [八合一总览](./docs/overviews/EIGHT_IN_ONE_OVERVIEW.md)
- [十九合一总览](./docs/overviews/NINETEEN_IN_ONE_OVERVIEW.md)

---

## 快速开始

```bash
# 1. 环境检查
lean --version  # 4.28.0

# 2. 安装依赖
pip install lean-dojo

# 3. 运行示例
cd YC-Killer-Lean4
python3 lean4_bridge.py
```

---

## 项目统计

```
词典系统: 120+ 文件, 900,000+ 字
├── 数学词典: 23 文件
├── AI/LLM: 12 文件
├── 物理词典: 8 文件
├── 哲学词典: 60+ 文件
└── 其他: 20+ 文件

整合项目: 8 个
技术文档: 30+ 个
```

---

## 外部资源

- **Lean4**: https://lean-lang.org
- **Mathlib4**: https://github.com/leanprover-community/mathlib4
- **LeanDojo**: https://leandojo.org
- **Aeneas**: https://github.com/AeneasVerif/aeneas

---

**版本**: 5.0.0 | **状态**: ✅ 生产就绪 | **更新**: 2025-03-26
