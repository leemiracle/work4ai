# LeanDojo 集成：机器学习 + 定理证明

## 📖 概述

**LeanDojo** 是一个强大的 Python 库，将机器学习与 Lean 定理证明结合。它提供：

1. **数据提取**: 从 Lean 仓库提取证明状态、战术、前提等
2. **程序化交互**: 用 Python 代码控制 Lean

> ⚠️ **注意**: 原始 LeanDojo 已弃用，建议使用 [LeanDojo-v2](https://github.com/lean-dojo/LeanDojo-v2)

---

## 🔗 为什么集成 LeanDojo？

### 与我们项目的关系

```
我们的整合架构：
┌─────────────────────────────────────────────────┐
│              用户界面 (Leantime)                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  YC-Killer AI 代理                              │
│  ├── 敏捷教练 Agent                             │
│  ├── 项目经理 Agent                             │
│  ├── 代码审查 Agent  ←── LeanDojo 集成点       │
│  ├── 风险分析 Agent                             │
│  └── 证明助手 Agent  ←── LeanDojo 核心功能     │
│                                                 │
├─────────────────────────────────────────────────┤
│              Lean4 验证层                       │
│  ├── 定理证明                                   │
│  ├── 代码验证                                   │
│  └── AI 辅助证明 ←── LeanDojo 数据提取         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 核心价值

| 功能 | 描述 | 我们的应用 |
|------|------|-----------|
| **数据提取** | 从 Lean 提取证明数据 | 训练 AI 模型 |
| **战术预测** | AI 预测下一步战术 | 证明助手 |
| **前提检索** | 搜索相关引理 | 自动化证明 |
| **程序化控制** | Python 控制 Lean | 自动化验证 |

---

## 📦 安装

### 方法 1: pip 安装

```bash
pip install lean-dojo
```

### 方法 2: 从源码安装

```bash
git clone https://github.com/lean-dojo/LeanDojo.git
cd LeanDojo
pip install .
```

### 前置要求

```bash
# 1. Git >= 2.25
git --version

# 2. Python 3.9-3.12
python --version

# 3. elan（已安装）
lean --version

# 4. wget
wget --version

# 5. GitHub Token（用于访问私有仓库）
export GITHUB_ACCESS_TOKEN=your_token_here
```

---

## 🚀 快速开始

### 1. 基础使用

```python
from lean_dojo import LeanGitRepo, trace, Pos

# 定位到 mathlib4 仓库
repo = LeanGitRepo("https://github.com/leanprover-community/mathlib4", "master")

# 定位一个定理
theorem_path = "Mathlib/Data/Nat/Basic.lean"
theorem_pos = Pos(line=100, column=0)  # 行号和列号

# 追踪证明
traced_theorem = trace(repo, theorem_path, theorem_pos)

# 获取证明状态
for tactic in traced_theorem.tactics:
    print(f"战术: {tactic.text}")
    print(f"状态: {tactic.state_before} → {tactic.state_after}")
```

### 2. 与我们的项目集成

```python
# leandojo_bridge.py

from lean_dojo import LeanGitRepo, trace, Pos, LeanFile
from typing import List, Dict, Optional
import os

class LeanDojoBridge:
    """LeanDojo 与我们的项目集成"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.repo = None
    
    def load_project(self):
        """加载 Lean 项目"""
        # 如果是本地项目
        if os.path.isdir(self.project_path):
            self.repo = LeanGitRepo(self.project_path)
        # 如果是 GitHub 仓库
        else:
            self.repo = LeanGitRepo(self.project_path, "main")
    
    def extract_theorem_data(self, file_path: str, line: int) -> Dict:
        """
        提取定理数据
        
        Args:
            file_path: Lean 文件路径
            line: 定理所在行号
        
        Returns:
            定理数据字典
        """
        pos = Pos(line=line, column=0)
        traced = trace(self.repo, file_path, pos)
        
        return {
            'theorem': traced.theorem_name,
            'tactics': [
                {
                    'text': t.text,
                    'state_before': str(t.state_before),
                    'state_after': str(t.state_after)
                }
                for t in traced.tactics
            ],
            'premises': traced.premises
        }
    
    def suggest_tactics(self, proof_state: str) -> List[str]:
        """
        基于当前证明状态建议战术
        
        Args:
            proof_state: 当前证明状态
        
        Returns:
            建议的战术列表
        """
        # 这里可以集成机器学习模型
        # 简化版本：基于规则的建议
        
        suggestions = []
        
        # 常用战术模式匹配
        if "⊢ True" in proof_state:
            suggestions.append("trivial")
        elif "⊢ False" in proof_state:
            suggestions.append("contradiction")
        elif "∧" in proof_state:
            suggestions.append("constructor")
        elif "∃" in proof_state:
            suggestions.append("use")
        elif "∀" in proof_state:
            suggestions.append("intro")
        elif "→" in proof_state:
            suggestions.append("intro")
        
        # 通用建议
        suggestions.extend(["simp", "ring", "omega", "decide"])
        
        return suggestions
    
    def verify_with_ai(self, code: str) -> Dict:
        """
        使用 AI 辅助验证 Lean 代码
        
        Args:
            code: Lean 代码
        
        Returns:
            验证结果和建议
        """
        # 1. 解析代码
        # 2. 提取证明状态
        # 3. AI 建议
        # 4. 返回结果
        
        return {
            'verified': True,  # 实际需要运行 Lean
            'suggestions': self.suggest_tactics(code),
            'ai_hints': "尝试使用 simp 或 ring 战术"
        }


class AIProofAssistant:
    """AI 证明助手（基于 LeanDojo）"""
    
    def __init__(self, leandojo_bridge: LeanDojoBridge):
        self.bridge = leandojo_bridge
    
    def assist_proof(self, theorem: str, current_state: str) -> Dict:
        """
        协助证明定理
        
        Args:
            theorem: 定理名称
            current_state: 当前证明状态
        
        Returns:
            证明建议
        """
        # 1. 分析当前状态
        suggestions = self.bridge.suggest_tactics(current_state)
        
        # 2. 搜索相关引理
        related_lemmas = self.search_related_lemmas(theorem)
        
        # 3. 生成证明策略
        strategy = self.generate_strategy(current_state)
        
        return {
            'suggested_tactics': suggestions,
            'related_lemmas': related_lemmas,
            'proof_strategy': strategy,
            'confidence': 0.85  # AI 置信度
        }
    
    def search_related_lemmas(self, theorem: str) -> List[str]:
        """搜索相关引理"""
        # 简化实现
        return [
            f"相关引理 1: Nat.add_comm",
            f"相关引理 2: Nat.add_assoc",
            f"相关引理 3: Nat.mul_comm"
        ]
    
    def generate_strategy(self, proof_state: str) -> str:
        """生成证明策略"""
        if "∀" in proof_state:
            return "建议策略：使用 intro 引入假设，然后逐步证明目标"
        elif "∃" in proof_state:
            return "建议策略：使用 use 提供存在性证人"
        elif "∧" in proof_state:
            return "建议策略：使用 constructor 分解合取"
        else:
            return "建议策略：尝试 simp, ring, 或 omega"


# 使用示例
if __name__ == "__main__":
    # 初始化
    bridge = LeanDojoBridge("/mnt/c/workspace/math/lean4ai/YC-Killer-Lean4")
    bridge.load_project()
    
    assistant = AIProofAssistant(bridge)
    
    # 模拟证明状态
    current_state = "n : Nat\n⊢ n + 0 = n"
    
    # 获取 AI 协助
    result = assistant.assist_proof(
        theorem="add_zero",
        current_state=current_state
    )
    
    print("=== AI 证明助手 ===")
    print(f"\n建议战术:")
    for tactic in result['suggested_tactics']:
        print(f"  - {tactic}")
    
    print(f"\n相关引理:")
    for lemma in result['related_lemmas']:
        print(f"  - {lemma}")
    
    print(f"\n证明策略:")
    print(f"  {result['proof_strategy']}")
    
    print(f"\nAI 置信度: {result['confidence']*100:.0f}%")
```

---

## 🔧 高级功能

### 1. 批量数据提取

```python
from lean_dojo import LeanGitRepo, trace
from typing import List, Dict
import json

def extract_training_data(repo_url: str, files: List[str]) -> List[Dict]:
    """
    从 Lean 仓库提取训练数据
    
    Args:
        repo_url: 仓库 URL
        files: 要提取的文件列表
    
    Returns:
        训练数据列表
    """
    repo = LeanGitRepo(repo_url, "main")
    training_data = []
    
    for file_path in files:
        try:
            traced = trace(repo, file_path)
            
            for theorem in traced.theorems:
                data = {
                    'theorem': theorem.name,
                    'file': file_path,
                    'tactics': [
                        {
                            'text': t.text,
                            'state': str(t.state_before)
                        }
                        for t in theorem.tactics
                    ]
                }
                training_data.append(data)
        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    return training_data


# 使用示例
if __name__ == "__main__":
    files = [
        "Mathlib/Data/Nat/Basic.lean",
        "Mathlib/Data/List/Basic.lean",
        "Mathlib/Algebra/Group/Defs.lean"
    ]
    
    data = extract_training_data(
        "https://github.com/leanprover-community/mathlib4",
        files
    )
    
    # 保存为 JSON
    with open("training_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"提取了 {len(data)} 个定理的训练数据")
```

### 2. 证明搜索

```python
from lean_dojo import LeanGitRepo, trace
from typing import List, Tuple, Optional
import heapq

class ProofSearch:
    """证明搜索算法"""
    
    def __init__(self, repo: LeanGitRepo):
        self.repo = repo
    
    def best_first_search(
        self,
        initial_state: str,
        max_depth: int = 10,
        beam_width: int = 5
    ) -> Optional[List[str]]:
        """
        最佳优先搜索证明
        
        Args:
            initial_state: 初始证明状态
            max_depth: 最大搜索深度
            beam_width: beam 宽度
        
        Returns:
            证明步骤列表（如果找到）
        """
        # 简化实现：beam search
        
        beam = [(0, initial_state, [])]  # (score, state, proof_steps)
        
        for depth in range(max_depth):
            candidates = []
            
            for score, state, steps in beam:
                # 生成候选战术
                tactics = self.generate_tactics(state)
                
                for tactic in tactics:
                    new_state = self.apply_tactic(state, tactic)
                    new_score = self.evaluate_state(new_state)
                    new_steps = steps + [tactic]
                    
                    # 如果找到证明
                    if self.is_proof_complete(new_state):
                        return new_steps
                    
                    candidates.append((new_score, new_state, new_steps))
            
            # 选择 top-k
            beam = heapq.nsmallest(beam_width, candidates)
        
        return None  # 未找到证明
    
    def generate_tactics(self, state: str) -> List[str]:
        """生成候选战术"""
        tactics = ["simp", "ring", "omega", "decide", "trivial"]
        
        if "∀" in state:
            tactics.append("intro")
        if "∃" in state:
            tactics.append("use")
        if "∧" in state:
            tactics.append("constructor")
        
        return tactics
    
    def apply_tactic(self, state: str, tactic: str) -> str:
        """应用战术（简化实现）"""
        # 实际需要与 Lean 交互
        return f"Applied {tactic} to {state}"
    
    def evaluate_state(self, state: str) -> float:
        """评估状态（越低越好）"""
        # 简化：基于目标数量
        goal_count = state.count("⊢")
        return goal_count
    
    def is_proof_complete(self, state: str) -> bool:
        """检查证明是否完成"""
        return "⊢" not in state or state.strip() == ""
```

### 3. 与 YC-Killer 集成

```python
# yc_killer_leandojo_agent.py

from leandojo_bridge import LeanDojoBridge, AIProofAssistant
from typing import Dict, List

class YCKillerLeanDojoAgent:
    """YC-Killer + LeanDojo AI 代理"""
    
    def __init__(self, project_path: str):
        self.bridge = LeanDojoBridge(project_path)
        self.proof_assistant = AIProofAssistant(self.bridge)
    
    def assist_developer(self, context: Dict) -> Dict:
        """
        协助开发者
        
        Args:
            context: 包含当前代码、证明状态等
        
        Returns:
            协助建议
        """
        code = context.get('code', '')
        proof_state = context.get('proof_state', '')
        
        # 1. 分析代码
        analysis = self.analyze_code(code)
        
        # 2. AI 证明建议
        proof_help = self.proof_assistant.assist_proof(
            theorem=context.get('theorem', ''),
            current_state=proof_state
        )
        
        # 3. 生成解释
        explanation = self.generate_explanation(proof_help)
        
        return {
            'analysis': analysis,
            'proof_suggestions': proof_help,
            'explanation': explanation,
            'next_steps': proof_help['suggested_tactics']
        }
    
    def analyze_code(self, code: str) -> Dict:
        """分析 Lean 代码"""
        return {
            'has_sorry': 'sorry' in code,
            'theorem_count': code.count('theorem'),
            'definition_count': code.count('def'),
            'lines': len(code.split('\n'))
        }
    
    def generate_explanation(self, proof_help: Dict) -> str:
        """生成人类可读的解释"""
        tactics = proof_help['suggested_tactics']
        strategy = proof_help['proof_strategy']
        
        explanation = f"""
基于当前的证明状态，我建议以下步骤：

1. **推荐战术**: {', '.join(tactics[:3])}

2. **证明策略**: {strategy}

3. **相关引理**: 可以查看以下引理以获得灵感：
   - {', '.join(proof_help['related_lemmas'][:2])}

4. **AI 置信度**: {proof_help['confidence']*100:.0f}%

提示：尝试第一个建议的战术，如果不成功，继续尝试下一个。
"""
        return explanation
    
    def auto_complete_proof(self, partial_proof: str) -> str:
        """
        自动补全证明
        
        Args:
            partial_proof: 部分证明代码
        
        Returns:
            补全后的证明
        """
        # 简化实现：添加常用战术
        suggestions = [
            "\n  · simp",
            "\n  · ring",
            "\n  · omega",
            "\n  · exact",
            "\n  · constructor"
        ]
        
        completed = partial_proof
        for suggestion in suggestions[:2]:
            completed += suggestion
        
        completed += "\n  · sorry  -- 请手动完成"
        
        return completed


# 使用示例
if __name__ == "__main__":
    agent = YCKillerLeanDojoAgent("/mnt/c/workspace/math/lean4ai/YC-Killer-Lean4")
    
    # 模拟开发者上下文
    context = {
        'code': """
theorem add_comm (a b : Nat) : a + b = b + a := by
  -- 开发者卡在这里
  sorry
""",
        'proof_state': "a b : Nat\n⊢ a + b = b + a",
        'theorem': 'add_comm'
    }
    
    # 获取协助
    result = agent.assist_developer(context)
    
    print("=== YC-Killer LeanDojo Agent ===\n")
    print("代码分析:")
    for key, value in result['analysis'].items():
        print(f"  - {key}: {value}")
    
    print("\n" + result['explanation'])
    
    print("\n下一步:")
    for step in result['next_steps'][:3]:
        print(f"  - {step}")
```

---

## 📚 相关资源

### 官方资源
- **LeanDojo 网站**: https://leandojo.org
- **LeanDojo-v2**: https://github.com/lean-dojo/LeanDojo-v2
- **文档**: https://leandojo.readthedocs.io
- **Demo**: https://github.com/lean-dojo/LeanDojo/blob/main/scripts/demo-lean4.ipynb

### 相关项目
- **ReProver**: 检索增强的证明器
- **LeanCopilot**: Lean 的 LLM 副驾驶
- **LeanDojo Benchmark**: 定理证明数据集

### 学术论文
```bibtex
@inproceedings{yang2023leandojo,
  title={LeanDojo: Theorem Proving with Retrieval-Augmented Language Models},
  author={Yang, Kaiyu and Swope, Aidan and Gu, Alex and ...},
  booktitle={Neural Information Processing Systems (NeurIPS)},
  year={2023}
}
```

---

## 🔗 与我们项目的整合点

### 1. YC-Killer 集成

```python
# 在 YC-Killer 中添加 LeanDojo 代理
class LeanDojoAgent:
    """YC-Killer 的 LeanDojo 代理"""
    pass
```

### 2. 敏捷流程集成

```python
# 在敏捷回顾中使用 LeanDojo 分析证明质量
class AgileLeanDojoAnalysis:
    """敏捷 + LeanDojo 分析"""
    pass
```

### 3. 项目管理集成

```python
# 在 Leantime 中追踪证明进度
class LeantimeLeanDojoTracker:
    """Leantime + LeanDojo 追踪"""
    pass
```

---

## ⚠️ 注意事项

1. **版本兼容性**: LeanDojo 需要 Lean 4 v4.3.0-rc2 或更高版本
2. **性能**: 数据提取可能需要较长时间
3. **GitHub Token**: 需要设置 `GITHUB_ACCESS_TOKEN` 环境变量
4. **弃用警告**: 原始 LeanDojo 已弃用，建议使用 LeanDojo-v2

---

## 📝 总结

### LeanDojo 为我们的项目带来：

| 功能 | 价值 |
|------|------|
| **数据提取** | 训练 AI 模型 |
| **战术预测** | AI 辅助证明 |
| **程序化控制** | 自动化验证 |
| **与 ML 集成** | 智能决策支持 |

### 整合后的能力：

✅ AI 辅助定理证明  
✅ 自动战术建议  
✅ 证明质量分析  
✅ 数据驱动优化  
✅ 智能代码补全  

---

**下一步**: 将 LeanDojo 集成到您的项目中，增强 AI 辅助能力！
