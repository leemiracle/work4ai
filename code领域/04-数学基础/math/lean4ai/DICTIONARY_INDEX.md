# Lean4 AI 知识库 - 文档索引

**形式化验证 + AI辅助 + 知识词典的完整解决方案**

---

## 目录结构

```
lean4ai/
├── README.md                 # 项目总览
├── START_HERE.md            # 快速开始
├── DICTIONARY_INDEX.md      # 本文件
├── QUICK_REFERENCE.md       # 快速参考
├── LEARNING_PATHS.md        # 学习路径
├── CONTRIBUTING.md          # 贡献指南
├── CHANGELOG.md             # 更新日志
├── GIT_WORKFLOW.md          # Git工作流
├── SUMMARY.md               # 项目总结
├── NEXT_STEPS.md            # 后续计划
│
└── docs/
    ├── math/                # 数学词典 (12卷)
    ├── physics/             # 物理学词典 (7卷)
    ├── ai/                  # AI/LLM词典 (12个文件)
    ├── lean4/               # Lean4相关文档
    ├── integrations/        # 项目集成文档
    ├── overviews/           # 综合概览文档
    ├── guides/              # 指南和报告
    ├── philosophy_dictionary/  # 哲学词典 (8卷)
    ├── anthropology_dictionary/ # 人类学词典
    └── encyclopedia/        # 百科全书
```

---

## 核心词典模块

### 1. AI & LLM 词典 → [docs/ai/](./docs/ai/)

| 文件 | 内容 |
|------|------|
| [LLM_CORE_DICTIONARY.md](./docs/ai/LLM_CORE_DICTIONARY.md) | Transformer、训练、推理 |
| [MODEL_ENCYCLOPEDIA.md](./docs/ai/MODEL_ENCYCLOPEDIA.md) | GPT、Claude、Llama等40+模型 |
| [AI_AGENT_GUIDE.md](./docs/ai/AI_AGENT_GUIDE.md) | Agent架构、工具、多Agent协作 |
| [AI_APP_DEVELOPMENT.md](./docs/ai/AI_APP_DEVELOPMENT.md) | Prompt工程、RAG、部署 |
| [LEAN4_AI_DICTIONARY.md](./docs/ai/LEAN4_AI_DICTIONARY.md) | 形式化证明与AI |

### 2. 数学词典 → [docs/math/](./docs/math/)

12卷完整数学词典，包含：

| 卷 | 文件 | 主题 |
|----|------|------|
| 1 | [VOL1_PART1.md](./docs/math/MATH_DICTIONARY_VOL1_PART1.md) | 基础数学 |
| 1 | [VOL1_PART2.md](./docs/math/MATH_DICTIONARY_VOL1_PART2.md) | 基础数学续 |
| 2 | [VOL2.md](./docs/math/MATH_DICTIONARY_VOL2.md) | 代数学 |
| 3 | [VOL3.md](./docs/math/MATH_DICTIONARY_VOL3.md) | 分析学 |
| 4 | [VOL4.md](./docs/math/MATH_DICTIONARY_VOL4.md) | 几何学 |
| 5 | [VOL5.md](./docs/math/MATH_DICTIONARY_VOL5.md) | 拓扑学 |
| 6 | [VOL6.md](./docs/math/MATH_DICTIONARY_VOL6.md) | 概率统计 |
| 7 | [VOL7.md](./docs/math/MATH_DICTIONARY_VOL7.md) | 数论 |
| 8 | [VOL8.md](./docs/math/MATH_DICTIONARY_VOL8.md) | 组合数学 |
| 9 | [VOL9.md](./docs/math/MATH_DICTIONARY_VOL9.md) | 数理逻辑 |
| 10 | [VOL10.md](./docs/math/MATH_DICTIONARY_VOL10.md) | 应用数学 |
| 11 | [VOL11.md](./docs/math/MATH_DICTIONARY_VOL11.md) | 计算数学 |
| 12 | [VOL12.md](./docs/math/MATH_DICTIONARY_VOL12.md) | 数学前沿 |

索引: [MATH_DICTIONARY_INDEX.md](./docs/math/MATH_DICTIONARY_INDEX.md)

### 3. 物理学词典 → [docs/physics/](./docs/physics/)

| 文件 | 主题 |
|------|------|
| [PHYSICS_INDEX.md](./docs/physics/PHYSICS_INDEX.md) | 物理学导航 |
| [PHYSICS_CLASSICAL_MECHANICS.md](./docs/physics/PHYSICS_CLASSICAL_MECHANICS.md) | 经典力学 |
| [PHYSICS_ELECTROMAGNETISM.md](./docs/physics/PHYSICS_ELECTROMAGNETISM.md) | 电磁学 |
| [PHYSICS_QUANTUM_MECHANICS.md](./docs/physics/PHYSICS_QUANTUM_MECHANICS.md) | 量子力学 |
| [PHYSICS_SPECIAL_RELATIVITY.md](./docs/physics/PHYSICS_SPECIAL_RELATIVITY.md) | 狭义相对论 |
| [PHYSICS_GENERAL_RELATIVITY.md](./docs/physics/PHYSICS_GENERAL_RELATIVITY.md) | 广义相对论 |
| [PHYSICS_PARTICLE_PHYSICS.md](./docs/physics/PHYSICS_PARTICLE_PHYSICS.md) | 粒子物理 |
| [PHYSICS_QUANTUM_INFO.md](./docs/physics/PHYSICS_QUANTUM_INFO.md) | 量子信息 |

### 4. 哲学词典 → [docs/philosophy_dictionary/](./docs/philosophy_dictionary/)

8卷完整哲学词典：形而上学、认识论、伦理学、语言/逻辑、心灵、科学、历史、当代

### 5. 其他词典

- [军事词典](./docs/military_dictionary.md)
- [人类学词典](./docs/anthropology_dictionary/)
- [百科全书](./docs/encyclopedia/)

---

## 技术文档

### Lean4 相关 → [docs/lean4/](./docs/lean4/)

- [MATHLIB_GUIDE.md](./docs/lean4/MATHLIB_GUIDE.md) - Mathlib4指南
- [LEAN4_PROJECTS_ANALYSIS.md](./docs/lean4/LEAN4_PROJECTS_ANALYSIS.md) - 项目分析
- [LEAN4_REPO_MANAGEMENT.md](./docs/lean4/LEAN4_REPO_MANAGEMENT.md) - 仓库管理
- [LEAN_ECOSYSTEM_REPORT.md](./docs/lean4/LEAN_ECOSYSTEM_REPORT.md) - 生态报告

### 项目集成 → [docs/integrations/](./docs/integrations/)

- [FINAL_INTEGRATION.md](./docs/integrations/FINAL_INTEGRATION.md) - 最终整合
- [LEANDOJO_INTEGRATION.md](./docs/integrations/LEANDOJO_INTEGRATION.md) - LeanDojo集成
- [YCKILLER_LEAN4_INTEGRATION.md](./docs/integrations/YCKILLER_LEAN4_INTEGRATION.md) - YC-Killer集成
- [AESOP_INTEGRATION.md](./docs/integrations/AESOP_INTEGRATION.md) - AESOP集成
- 等16个集成文档

### 综合概览 → [docs/overviews/](./docs/overviews/)

- [EIGHT_IN_ONE_OVERVIEW.md](./docs/overviews/EIGHT_IN_ONE_OVERVIEW.md) - 八合一总览
- [NINETEEN_IN_ONE_OVERVIEW.md](./docs/overviews/NINETEEN_IN_ONE_OVERVIEW.md) - 十九合一总览
- [LEARNING_RESOURCES_OVERVIEW.md](./docs/overviews/LEARNING_RESOURCES_OVERVIEW.md) - 学习资源概览

---

## 快速导航

### 按角色

| 角色 | 推荐起点 |
|------|----------|
| **初学者** | [START_HERE.md](./START_HERE.md) → [LLM核心词典](./docs/ai/LLM_CORE_DICTIONARY.md) |
| **开发者** | [AI应用开发](./docs/ai/AI_APP_DEVELOPMENT.md) |
| **研究者** | [模型大全](./docs/ai/MODEL_ENCYCLOPEDIA.md) |
| **Lean4用户** | [MATHLIB指南](./docs/lean4/MATHLIB_GUIDE.md) |

### 按任务

| 任务 | 推荐文档 |
|------|----------|
| 学习AI | [AI词典系列](./docs/ai/) |
| 学习数学 | [数学词典索引](./docs/math/MATH_DICTIONARY_INDEX.md) |
| 学习物理 | [物理词典索引](./docs/physics/PHYSICS_INDEX.md) |
| Lean4开发 | [Lean4文档](./docs/lean4/) |
| 项目集成 | [集成文档](./docs/integrations/) |

---

## 统计

| 类别 | 文件数 | 字数 |
|------|--------|------|
| 数学词典 | 23 | 400,000+ |
| AI/LLM词典 | 12 | 100,000+ |
| 物理词典 | 8 | 85,000+ |
| 哲学词典 | 60+ | 200,000+ |
| 集成文档 | 16 | 150,000+ |
| **总计** | **120+** | **900,000+** |

---

*整理完成 | 2025-03-26*
