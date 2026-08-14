# 03 · Skill 评价 6 维度

> **核心论点**："感觉好用的 skill"不算评价。6 维度 + 客观打分。
> **本文是什么**：参照 prompt 6 维度，为 skill 设计的评价框架。

---

## 🎯 6 维度速查

```
1. 准确性（Accuracy）       - skill 输出真的解决问题吗
2. 触发精度（Trigger Precision） - 该激活时激活，不该时不打扰
3. 资源质量（Resources）    - 链接 / 例子是否最新有效
4. 协作性（Composability）  - 能否与其他 skill 联动
5. 维护性（Maintainability）- 是否容易过时
6. 安全性（Safety）         - 是否暴露敏感信息 / 误导
```

---

## 📐 维度 1：准确性（Accuracy）

**核心问题**：skill 真的帮用户解决问题吗？

### 评价指标
- **任务完成率**：用 skill 后，用户问题解决了吗？
- **输出质量**：skill 产出的内容（建议 / 代码 / 文档）真的有用吗？
- **vs 直接 prompt**：用 skill 比直接 prompt 强多少？

### 测试方法
```
1. 准备 10 个典型任务
2. 一组用 skill，一组直接 prompt
3. 盲评（自己 / 同行）哪个更好
4. skill 应该 ≥ 70% 胜出
```

---

## 📐 维度 2：触发精度（Trigger Precision）

**核心问题**：skill 在该激活时激活了吗？不该激活时打扰了吗？

### 这是 skill 独有的维度（prompt 没有）

### 评价指标
- **True Positive**：用户问相关 → skill 激活 ✓
- **False Positive**：用户问无关 → skill 误激活 ✗
- **False Negative**：用户问相关 → skill 没激活 ✗

### 测试方法
```
1. 准备 20 个用户输入：
   - 10 个相关（应触发）
   - 10 个无关（不应触发）
2. 看每个输入是否激活 skill
3. 计算 Precision / Recall：
   - Precision = TP / (TP + FP)
   - Recall = TP / (TP + FN)
4. 目标：Precision ≥ 0.8, Recall ≥ 0.7
```

### 改进触发精度的方法
- description 写**具体关键词**（不要抽象）
- 多语言 triggers（中英混合）
- 加**反例**（"不要在 X 场景激活"）

---

## 📐 维度 3：资源质量（Resources）

**核心问题**：链接 / 例子是否最新有效？

### 评价指标
- **链接有效性**：所有 URL 还能访问吗？
- **时效性**：内容是 2026 当前版本吗？
- **覆盖度**：覆盖核心场景吗？

### 测试方法
```bash
# 用脚本扫所有链接
grep -oE 'https?://[^ )]+' SKILL.md | while read url; do
    status=$(curl -sI "$url" | head -1)
    echo "$url → $status"
done
```

### 维护节奏
- **每 3 月**：扫一次链接
- **每 6 月**：内容是否过时（特别是版本号 / API）
- **每 12 月**：是否需要重写

---

## 📐 维度 4：协作性（Composability）

**核心问题**：能否与其他 skill 联动？

### opencode 的核心优势是 skill 联动

### 评价指标
- **有"跨 Skill 协作"段**吗？
- **明确指向哪些 skill** 吗？
- **反向**：被其他 skill 指向吗？

### 好的协作设计
```
用户问 X → 当前 skill（核心讲解）
  ├─ 深挖 → skill-A
  ├─ 实战 → skill-B
  └─ 评估 → skill-C
```

### 反模式
- **孤岛 skill**：没协作段
- **过度协作**：指向 10 个 skill（用户晕）

---

## 📐 维度 5：维护性（Maintainability）

**核心问题**：是否容易过时？

### 评价指标
- **内容稳定性**：核心方法 5 年不变 vs 每月变
- **版本号**：是否有 `<!-- version: X.Y -->`
- **更新日期**：是否有 `<!-- updated: YYYY-MM-DD -->`

### 高维护性 skill（少改动）
- `git-workflow`：Git 基本不变
- `karpathy-guidelines`：编码原则稳定
- `learning-methodology`：学习方法稳定

### 低维护性 skill（频繁更新）
- `frontier-briefing`：每周都有新论文
- `prompt-engineering`：每季新工具
- `ai-deployment`：每年新框架

**对策**：低维护性 skill 必须每 3 月 review。

---

## 📐 维度 6：安全性（Safety）

**核心问题**：是否暴露敏感信息 / 误导用户？

### 评价指标
- **不含 API key / token**
- **不教违规操作**（如绕过 license）
- **危险操作有警告**
- **不会误导**（如"用 deprecated API"）

### 反模式
- 链接到恶意网站
- 教 SQL injection（即使举例）
- 推荐 deprecated 库

---

## 📊 6 维度评分卡（可直接用）

```
Skill: _______________
审计日期: _______________

| 维度 | 指标 | 分数 (1-5) | 备注 |
|---|---|---|---|
| 1. 准确性 | 任务完成率 / 输出质量 |  |  |
| 2. 触发精度 | Precision / Recall |  |  |
| 3. 资源质量 | 链接有效 / 时效 |  |  |
| 4. 协作性 | 跨 skill 段 / 被引用 |  |  |
| 5. 维护性 | 稳定性 / 版本号 |  |  |
| 6. 安全性 | 无敏感 / 无误导 |  |  |
| **总分** |  | **/30** |  |

红线：
- 任一维度 < 2 → 必须修复
- 总分 < 18 → 退役（删 / 重写）
```

---

## 🛠️ 自动化评估（用脚本）

参见 [`06-审计脚本`](../prompt-eval-demo/scripts/audit_skills.py)，可自动：
- 扫所有 SKILL.md
- 检查 description 完整性
- 检查链接有效性
- 估算行数 / 协作段
- 输出评分卡

---

## 📌 本周必做

1. [ ] 用 6 维度评分卡给 5 个你最常用的 skill 打分
2. [ ] 找出最弱的 2 个，按建议修复
3. [ ] 跑 [`06-审计脚本`](../prompt-eval-demo/scripts/audit_skills.py) 全量审计

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**Skill 不只是"能跑"，要"跑得好 + 该跑时跑"。6 维度评分 = 客观评价。**
