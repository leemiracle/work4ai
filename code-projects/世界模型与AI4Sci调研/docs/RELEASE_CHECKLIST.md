# 发布前检查清单 · Release Checklist

> 从 v2.1.7 到"可对外发布"需要做的所有事
> 产出：2026-07-23（v2.1.8）

---

## 审计结果（自动扫描）

| 检查项 | 状态 | 说明 |
|---|---|---|
| git 未提交文件 | ⚠️ **57** | 十九轮全部变更未版本化 |
| LICENSE | ❌ **缺失** | 开源发布必须有 |
| .gitignore | ✅ 存在 | — |
| README.md | ✅ 存在 | 需更新到 v2.1.7 |
| CHANGELOG.md | ✅ 存在 | 最新 v2.1.7 |
| Python 实验 | ✅ 118 个 | 含 v2.1.7 新增 4 个 |
| markdown 文件 | ✅ 143 个 | 含 docs/ 27 个 |
| research-execution/ | ✅ 8 个文件 | Thesis + 3 报告 + 4 .py |

---

## 发布前必须做的 6 件事

### 1. ⚠️ Git Commit（最紧急）

```bash
cd /data/usershare/ai/world-ai4sci-math
git add -A
git commit -m "v2.1.7: 十九轮增量

- v2.0.1-2: 信创+形式化双线（模块13§13 / 模块14§11 等）
- v2.0.3-4: 全项目自审（1148 arXiv / 4 bug / 100% 跑通）
- v2.0.5-6: 2026-07 前沿跟踪（简报 + 5 深化 + 吸收）
- v2.0.7-8: 50 课题 + 10 路径 + AlphaProof Nexus
- v2.0.9: 使用说明书
- v2.1.0: 10 教训 + 20 洞察
- v2.1.1-6: 3 课题执行 + 统一 Thesis + 分布依赖深化
- v2.1.7: 实验脚本独立化"
```

**为什么最紧急**：57 个文件的变更在 working directory 里——一次误操作就全丢了。

### 2. ❌ 添加 LICENSE

```bash
# 如果开源（推荐 MIT）
cd /data/usershare/ai/world-ai4sci-math
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2026 [your name]

Permission is hereby granted, free of charge, to any person obtaining a copy
...
EOF
```

### 3. README 最终更新

README 需要反映 v2.1.7 的全部增量：
- 总量从 v2.0 的 "154 md / 111 py" 更新到 "175 md / 118 py"
- 新增 docs/ 导航层说明（使用说明书 / 50课题 / 10路径 / 10教训 / 20洞察 / 前沿简报 / 5深化 / Thesis）
- 模块 13 从 12 章更新到 13 章
- 模块 14 §05 从 11 章更新到 12 章

### 4. 最终验证（可选但推荐）

```bash
# 跑全部实验（确认无回归）
cd /data/usershare/ai/world-ai4sci-math
python3 -c "
import subprocess, os
root = '.'
for d,_,fs in os.walk(root):
    if '.git' in d or '.opencode' in d: continue
    for f in fs:
        if f.endswith('.py'):
            p = os.path.join(d, f)
            try:
                r = subprocess.run(['python3', p], timeout=5, capture_output=True)
                status = '✅' if r.returncode == 0 else '❌'
            except: status = '⏱️'
            print(f'{status} {p}')
"

# 检查死链
python3 -c "
import os, re
root = '.'
dead = 0
for d,_,fs in os.walk(root):
    if '.git' in d or '.opencode' in d: continue
    for f in fs:
        if not f.endswith('.md'): continue
        path = os.path.join(d, f)
        with open(path) as fp:
            for m in re.finditer(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', fp.read()):
                link = m.group(2).split('#')[0]
                if '://' in link or not link: continue
                target = os.path.normpath(os.path.join(d, link))
                if not os.path.exists(target): dead += 1
print(f'项目内死链: {dead}')
"
```

### 5. Release Notes（可选）

从 CHANGELOG 提取 v2.0 → v2.1.7 的 17 个版本，写一份 Release Notes。

### 6. .gitignore 清理

确保临时文件不被提交：
```bash
# 检查是否有大文件/临时文件
find /data/usershare/ai/world-ai4sci-math -size +10M -not -path "*/.git/*" 2>/dev/null
```

---

## 发布后的推广建议

1. **HuggingFace Spaces / GitHub Pages**：放一份交互版的使用说明书
2. **知乎/小红书技术帖**：以"20 个核心洞察"为标题发帖
3. **学术会议**：Thesis（"经典理论在 AI 中保守"）可投 NeurIPS Position Paper
4. **开源社区**：50 课题 + 10 路径可以作为"AI 研究入门导航"分享

---

## 版本号建议

如果完成上述 6 步，版本号应为 **v2.2.0**（从 v2.1.x 升到 v2.2.x，标志"发布就绪"）。

```
v1.0-v2.0：内容建设期
v2.0.1-v2.1.7：深化+验证+执行期（十九轮"不要停"）
v2.2.0：发布就绪 ← 下一步
```
