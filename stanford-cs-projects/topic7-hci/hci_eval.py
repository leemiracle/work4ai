"""
CS147 + CS347 - HCI 设计与评估
覆盖课程模块：CS147 设计思维 + CS347 评估方法 + CS547 周五嘉宾议题

实现内容：
1. 用户画像 / Scenario
2. 启发式评估（Nielsen 10 heuristics）
3. 用户研究模拟（A/B 测试 + 统计）
4. 可访问性审计（WCAG 简化）
"""
from __future__ import annotations
import random
import math
from dataclasses import dataclass, field
from typing import Optional


# ============ 1. 用户画像 ============

@dataclass
class Persona:
    name: str
    age: int
    occupation: str
    tech_literacy: int  # 1-5
    goals: list = field(default_factory=list)
    pain_points: list = field(default_factory=list)
    accessibility_needs: list = field(default_factory=list)


def design_thinking_template():
    """CS147 L9 设计思维五步"""
    return {
        "1_empathize": "访谈 5-10 个真实用户，理解他们的痛点",
        "2_define": "提炼 problem statement：'How might we...'",
        "3_ideate": "头脑风暴 20+ 解决方案，不评判",
        "4_prototype": "低保真 → 中保真 → 高保真",
        "5_test": "可用性测试（5 个用户能发现 85% 的问题）",
    }


# ============ 2. Nielsen 10 Heuristics ============

NIELSEN_HEURISTICS = [
    ("visibility_of_system_status", "系统状态可见"),
    ("match_between_system_and_real_world", "符合现实世界语言"),
    ("user_control_and_freedom", "用户控制与自由"),
    ("consistency_and_standards", "一致性与标准"),
    ("error_prevention", "错误预防"),
    ("recognition_over_recall", "识别优于回忆"),
    ("flexibility_and_efficiency", "灵活性与效率"),
    ("aesthetic_and_minimalist_design", "美学与极简"),
    ("help_users_recover_from_errors", "错误恢复"),
    ("help_and_documentation", "帮助与文档"),
]


@dataclass
class HeuristicIssue:
    heuristic: str
    severity: int  # 0-4 (Nielsen severity)
    description: str
    location: str


def evaluate_heuristics(design_elements: list[str]) -> list[HeuristicIssue]:
    """模拟启发式评估：检查设计元素"""
    issues = []
    for elem in design_elements:
        # Mock：每个元素 30% 概率有问题
        if random.random() < 0.3:
            h = random.choice(NIELSEN_HEURISTICS)
            issues.append(HeuristicIssue(
                heuristic=h[0],
                severity=random.randint(0, 4),
                description=f"在 '{elem}' 中可能违反 {h[1]}",
                location=elem,
            ))
    return issues


# ============ 3. 用户研究 - A/B 测试 ============

def ab_test(a_conversions: list[bool], b_conversions: list[bool]) -> dict:
    """
    简单 A/B 测试 + 统计显著性（z-test for proportions）
    """
    n_a, n_b = len(a_conversions), len(b_conversions)
    p_a = sum(a_conversions) / max(n_a, 1)
    p_b = sum(b_conversions) / max(n_b, 1)
    # Pooled p
    p_pool = (sum(a_conversions) + sum(b_conversions)) / max(n_a + n_b, 1)
    # Standard error
    if p_pool == 0 or p_pool == 1:
        return {"p_a": p_a, "p_b": p_b, "significant": False, "z": 0}
    se = math.sqrt(p_pool * (1 - p_pool) * (1/max(n_a,1) + 1/max(n_b,1)))
    z = (p_b - p_a) / max(se, 1e-10)
    # |z| > 1.96 → p < 0.05
    significant = abs(z) > 1.96
    return {
        "p_a": p_a, "p_b": p_b,
        "lift": p_b - p_a,
        "z_score": z,
        "significant": significant,
        "conclusion": "B 更好" if z > 1.96 else ("A 更好" if z < -1.96 else "无显著差异"),
    }


# ============ 4. WCAG 审计（简化） ============

WCAG_CRITERIA = [
    ("1.1.1_non_text_content", "非文本内容有替代"),
    ("1.4.3_contrast_minimum", "对比度 ≥ 4.5:1"),
    ("2.1.1_keyboard", "可键盘操作"),
    ("2.4.6_headings_and_labels", "标题/标签描述性"),
    ("3.3.2_labels_or_instructions", "输入有标签/说明"),
    ("4.1.2_name_role_value", "组件有 name/role/value"),
]


def audit_wcag(html_elements: list[dict]) -> list[dict]:
    """
    简化 WCAG 检查
    html_elements: [{"tag": "img", "attrs": {"alt": "..."}}, ...]
    """
    issues = []
    for el in html_elements:
        tag = el.get("tag", "")
        attrs = el.get("attrs", {})

        if tag == "img" and "alt" not in attrs:
            issues.append({"criterion": "1.1.1", "issue": "img 缺少 alt"})
        if tag == "button" and not attrs.get("aria-label", "") and not el.get("text"):
            issues.append({"criterion": "4.1.2", "issue": "button 无可访问名称"})
        if tag == "input" and not attrs.get("aria-label") and not attrs.get("id"):
            issues.append({"criterion": "3.3.2", "issue": "input 无标签"})
    return issues


# ============ 5. SUS (System Usability Scale) ============

def sus_score(responses: list[int]) -> float:
    """
    System Usability Scale (Brooke 1996)
    10 题，每题 1-5
    奇数题 (正向): score = r - 1
    偶数题 (反向): score = 5 - r
    总分 × 2.5 = 0-100
    """
    if len(responses) != 10:
        return 0.0
    total = 0
    for i, r in enumerate(responses):
        if i % 2 == 0:  # 奇数题（0-indexed 偶数）
            total += r - 1
        else:           # 偶数题
            total += 5 - r
    return total * 2.5


# ============ Demo ============

def demo():
    print("=" * 60)
    print("CS147 + CS347: HCI Design & Evaluation")
    print("=" * 60)

    # 1. Persona + Design Thinking
    print("\n📋 1. Persona + Design Thinking")
    persona = Persona(
        name="Alex (留学生)",
        age=22,
        occupation="Stanford 研一 CS",
        tech_literacy=4,
        goals=["快速理解课程要求", "规划学习路径"],
        pain_points=["课程信息分散", "英文术语难懂"],
        accessibility_needs=["色盲友好"],
    )
    print(f"   Persona: {persona.name}, {persona.age}, {persona.occupation}")
    print(f"   Tech literacy: {'⭐'*persona.tech_literacy}")
    print(f"   Design thinking 5 步:")
    for k, v in design_thinking_template().items():
        print(f"     {k}: {v}")

    # 2. Nielsen Heuristics
    print("\n📋 2. 启发式评估")
    design = ["导航栏", "搜索框", "登录表单", "结果列表", "分页控件", "错误提示"]
    random.seed(42)
    issues = evaluate_heuristics(design)
    for iss in issues:
        print(f"   [{iss.severity}] {iss.heuristic}: {iss.description}")
    severity_count = sum(i.severity for i in issues)
    print(f"   总 severity: {severity_count}")

    # 3. A/B Test
    print("\n📋 3. A/B Test (CTA 按钮)")
    random.seed(42)
    a = [random.random() < 0.10 for _ in range(1000)]  # 10% baseline
    b = [random.random() < 0.13 for _ in range(1000)]  # 13% new
    result = ab_test(a, b)
    print(f"   A: {result['p_a']:.1%} conversion")
    print(f"   B: {result['p_b']:.1%} conversion")
    print(f"   Lift: {result['lift']:+.1%}")
    print(f"   Z-score: {result['z_score']:.2f}")
    print(f"   Conclusion: {result['conclusion']} (significant={result['significant']})")

    # 4. WCAG 审计
    print("\n📋 4. WCAG 可访问性审计")
    elements = [
        {"tag": "img", "attrs": {"src": "logo.png"}},  # 缺 alt
        {"tag": "button", "text": ""},                  # 无文本
        {"tag": "input", "attrs": {"type": "text"}},   # 无 label
        {"tag": "img", "attrs": {"src": "ok.png", "alt": "确认"}},  # OK
    ]
    issues = audit_wcag(elements)
    for iss in issues:
        print(f"   ❌ WCAG {iss['criterion']}: {iss['issue']}")
    if not issues:
        print("   ✅ 所有元素通过")

    # 5. SUS
    print("\n📋 5. System Usability Scale (SUS)")
    # 模拟 10 个用户评估
    random.seed(42)
    all_scores = []
    for _ in range(10):
        responses = [random.randint(2, 5) for _ in range(10)]
        score = sus_score(responses)
        all_scores.append(score)
    avg = sum(all_scores) / len(all_scores)
    print(f"   平均 SUS: {avg:.1f} (>68 = 可用，>80 = 优秀)")
    print(f"   Interpretation: {'优秀' if avg > 80 else ('可用' if avg > 68 else '需改进')}")

    print("\n✅ CS147+347 完成！")


if __name__ == "__main__":
    demo()
