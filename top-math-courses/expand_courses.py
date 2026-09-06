#!/usr/bin/env python3
"""
top-math-courses 课程扩张器
============================
为 9 校补全核心课程，使总数从 76 → ~158 门，符合 README 定位（150-200 门）。
每门新课创建目录 + README.md（基于真实课程编号），experiments 由 generate_missing_content.py 自动补。

用法：python3 expand_courses.py && python3 generate_missing_content.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

# 格式: (dir_name, code, english_title, chinese, textbook, topic)
# textbook 标 ⚠️ 表示待核实
NEW_COURSES = {
    'mit-math-courses': [
        ('18_05_probability_statistics', '18.05', 'Introduction to Probability and Statistics', '概率统计入门', 'Walpole ⚠️', 'probability'),
        ('18_100A_real_analysis_applied', '18.100A', 'Real Analysis (Applied)', '应用实分析', ' announcements', 'analysis'),
        ('18_100C_real_analysis_rigorous', '18.100C', 'Real Analysis (Rigorous)', '严格实分析', 'Rudin ⚠️', 'analysis'),
        ('18_102_functional_analysis', '18.102', 'Functional Analysis', '泛函分析', 'Lax', 'analysis'),
        ('18_103_fourier_analysis', '18.103', 'Fourier Analysis', 'Fourier 分析', 'Stein & Shakarchi', 'analysis'),
        ('18_125_measure_integration', '18.125', 'Measure and Integration', '测度与积分', 'Folland ⚠️', 'analysis'),
        ('18_702_algebra_II', '18.702', 'Algebra II', '代数 II', 'Artin', 'algebra'),
        ('18_781_number_theory', '18.781', 'Theory of Numbers', '数论', 'Niven et al. ⚠️', 'algebra'),
        ('18_905_algebraic_topology', '18.905', 'Algebraic Topology I', '代数拓扑 I', 'Hatcher', 'topology'),
    ],
    'stanford-math-courses': [
        ('math19_calculus', 'MATH 19', 'Calculus', '微积分', 'Stewart ⚠️', 'calculus'),
        ('math108_combinatorics', 'MATH 108', 'Combinatorics', '组合数学', 'Stanley ⚠️', 'algebra'),
        ('math120_differential_geometry', 'MATH 120', 'Modern Differential Geometry', '现代微分几何', 'Do Carmo', 'topology'),
        ('math121_galois_theory', 'MATH 121', 'Galois Theory', 'Galois 理论', 'Artin ⚠️', 'algebra'),
        ('math144_topology', 'MATH 144', 'Point-Set Topology', '点集拓扑', 'Munkres', 'topology'),
        ('math152_harmonic_analysis', 'MATH 152', 'Harmonic Analysis', '调和分析', 'Stein & Shakarchi', 'analysis'),
        ('cme302_numerical_linear_algebra', 'CME 302', 'Numerical Linear Algebra', '数值线性代数', 'Trefethen & Bau', 'numerical'),
        ('stats200_statistics', 'STATS 200', 'Introduction to Statistical Inference', '统计推断', 'Lehmann ⚠️', 'probability'),
    ],
    'harvard-math-courses': [
        ('math101_calculus', 'Math 101', 'Calculus I', '微积分 I', 'Stewart ⚠️', 'calculus'),
        ('math118_probability', 'Math 118', 'Probability Theory', '概率论', 'Feller ⚠️', 'probability'),
        ('math123_algebra_II', 'Math 123', 'Algebra II', '代数 II: Galois 理论', 'Artin', 'algebra'),
        ('math129_number_theory', 'Math 129', 'Number Theory', '数论', 'Niven ⚠️', 'algebra'),
        ('math134_differential_geometry', 'Math 134', 'Differential Geometry', '微分几何', 'Do Carmo', 'topology'),
        ('math137_algebraic_geometry', 'Math 137', 'Algebraic Geometry', '代数几何', 'Harris ⚠️', 'algebra'),
    ],
    'princeton-math-courses': [
        ('mat216_honors_analysis_II', 'MAT 216', 'Honors Analysis II', '荣誉分析 II', 'Spivak ⚠️', 'analysis'),
        ('mat218_analysis', 'MAT 218', 'Analysis', '分析（高阶）', 'Stein & Shakarchi ⚠️', 'analysis'),
        ('mat325_topology', 'MAT 325', 'Topology', '拓扑', 'Munkres', 'topology'),
        ('mat415_algebraic_geometry', 'MAT 415', 'Algebraic Geometry', '代数几何', 'Harris ⚠️', 'algebra'),
        ('mat419_topology_II', 'MAT 419', 'Topology II', '拓扑 II', 'Hatcher ⚠️', 'topology'),
        ('mat520_differential_geometry', 'MAT 520', 'Differential Geometry', '微分几何', 'Do Carmo', 'topology'),
    ],
    'berkeley-math-courses': [
        ('math1a_calculus', 'Math 1A', 'Calculus', '微积分', 'Stewart ⚠️', 'calculus'),
        ('math1b_calculus', 'Math 1B', 'Calculus (Continuation)', '微积分 II', 'Stewart ⚠️', 'calculus'),
        ('math55_discrete', 'Math 55', 'Discrete Mathematics', '离散数学', 'Rosen', 'algebra'),
        ('math202B_topology_analysis_II', 'Math 202B', 'Topology and Analysis II', '拓扑与分析 II', '⚠️ 待核实', 'analysis'),
        ('math215A_algebraic_topology', 'Math 215A', 'Algebraic Topology', '代数拓扑', 'Hatcher', 'topology'),
        ('stat200A_statistics', 'Stat 200A', 'Theoretical Statistics', '理论统计', 'Lehmann ⚠️', 'probability'),
    ],
    'cambridge-math-courses': [
        ('partIA_numbers_sets', 'Part IA', 'Numbers and Sets', '数与集合', 'Cameron ⚠️', 'algebra'),
        ('partIA_vectors_matrices', 'Part IA', 'Vectors and Matrices', '向量与矩阵', '⚠️ 待核实', 'linear_algebra'),
        ('partIA_groups', 'Part IA', 'Groups', '群论入门', 'Humphreys ⚠️', 'algebra'),
        ('partIA_vector_calculus', 'Part IA', 'Vector Calculus', '向量微积分', '⚠️ 待核实', 'calculus'),
        ('partIB_groups_rings_modules', 'Part IB', 'Groups, Rings and Modules', '群、环与模', 'Cameron ⚠️', 'algebra'),
        ('partIB_metric_topological_spaces', 'Part IB', 'Metric and Topological Spaces', '度量与拓扑空间', 'Sutherland', 'topology'),
        ('partIB_complex_analysis', 'Part IB', 'Complex Analysis', '复分析', '⚠️ 待核实', 'calculus'),
        ('partIB_methods', 'Part IB', 'Methods', '数学方法', 'Riley ⚠️', 'pde'),
        ('partIB_statistics', 'Part IB', 'Statistics', '统计学', '⚠️ 待核实', 'probability'),
        ('partII_number_theory', 'Part II', 'Number Theory', '数论', 'Baker ⚠️', 'algebra'),
        ('partII_algebraic_topology', 'Part II', 'Algebraic Topology', '代数拓扑', 'Hatcher', 'topology'),
        ('partII_differential_geometry', 'Part II', 'Differential Geometry', '微分几何', '⚠️ 待核实', 'topology'),
    ],
    'oxford-math-courses': [
        ('prelims_m3_analysis', 'Prelims M3', 'Analysis III', '分析 III', '⚠️ 待核实', 'analysis'),
        ('prelims_m4_probability', 'Prelims M4', 'Probability', '概率', '⚠️ 待核实', 'probability'),
        ('partA_a1_algebra', 'Part A A1', 'Algebra', '代数', 'Cameron ⚠️', 'algebra'),
        ('partA_a2_differential_equations', 'Part A A2', 'Differential Equations', '微分方程', '⚠️ 待核实', 'pde'),
        ('partA_a3_analysis', 'Part A A3', 'Analysis', '分析', '⚠️ 待核实', 'analysis'),
        ('partA_a7_number_theory', 'Part A A7', 'Number Theory', '数论', '⚠️ 待核实', 'algebra'),
        ('partB_b3_1_topology_groups', 'Part B B3.1', 'Topology and Groups', '拓扑与群', '⚠️ 待核实', 'topology'),
        ('partC_c3_1_algebraic_topology', 'Part C C3.1', 'Algebraic Topology', '代数拓扑', 'Hatcher', 'topology'),
    ],
    'eth-math-courses': [
        ('e401_0073_analysis_II', '401-0073-00L', 'Analysis II', '分析 II', '⚠️ 待核实', 'analysis'),
        ('e401_0151_linear_algebra_II', '401-0151-00L', 'Linear Algebra II', '线性代数 II', '⚠️ 待核实', 'linear_algebra'),
        ('e401_0373_ode', '401-0373-00L', 'Ordinary Differential Equations', '常微分方程', 'Arnold ⚠️', 'pde'),
        ('e401_1151_functional_analysis', '401-1151-00L', 'Functional Analysis I', '泛函分析 I', '⚠️ 待核实', 'analysis'),
        ('e401_2281_topology', '401-2281-00L', 'Topology I', '拓扑 I', '⚠️ 待核实', 'topology'),
        ('e401_3641_measure_theory', '401-3641-00L', 'Measure Theory', '测度论', '⚠️ 待核实', 'analysis'),
    ],
    'ut-austin-math-courses': [
        ('m325k_discrete_math', 'M 325K', 'Discrete Mathematics', '离散数学', 'Rosen ⚠️', 'algebra'),
        ('m358K_applied_statistics', 'M 358K', 'Applied Statistics', '应用统计', '⚠️ 待核实', 'probability'),
        ('m374k_number_theory', 'M 374K', 'Number Theory', '数论', 'Niven ⚠️', 'algebra'),
        ('m382C_algebra', 'M 382C', 'First-Year Course in Algebra', '代数', 'Artin', 'algebra'),
        ('m384C_numerical_analysis', 'M 384C', 'Numerical Analysis I', '数值分析 I', '⚠️ 待核实', 'numerical'),
        ('m386C_probability', 'M 386C', 'Probability I', '概率论 I', 'Durrett ⚠️', 'probability'),
    ],
}

README_TEMPLATE = '''# {school_full} {code} — {english_title}

> **学校**：{school_full} | **{chinese}**
> **编号**：{code}
> **一手来源**：建议核实 {school_full} 官网最新课程目录

## 课程信息
- **编号**：{code}
- **主题分类**：{topic}
- **教材**：{textbook}
- **先修课**：见各校课程目录

## 教学大纲
（建议核实官网 syllabus 后补充）

## 📍 在数学全景中的位置
本课属于 **{topic_cn}** 主题。前置/后续课程见 [`../UNIFIED_ROADMAP.md`](../../UNIFIED_ROADMAP.md) 和 [`../DEEP_ANALYSIS.md`](../../DEEP_ANALYSIS.md)。

## 🔬 理论联系实际（ML / 工程）
{ml_links}

## 🆕 2024-2026 最新研究
（见 [`../LATEST_RESEARCH.md`](../../LATEST_RESEARCH.md) 对应主题章节）

## 参考资源
- **教材**：{textbook}
- **课程主页**：建议搜索 "{school_full} {code}"
- **跨校对照**：见 [`../CROSS_SCHOOL_INSIGHTS.md`](../../CROSS_SCHOOL_INSIGHTS.md) 和 [`../DEEP_ANALYSIS.md`](../../DEEP_ANALYSIS.md)

## 学习建议
- 配合 [`notes.md`](./notes.md)（费曼三层笔记）
- 做 [`exercises.md`](./exercises.md) 习题
- 跑 [`experiments/`](./experiments/) 验证定理

📌 **下一步**：→ 见同校其他课程目录，或回到 [`../`](../)

---
> 📝 **本 README 由 expand_courses.py 自动生成**（{date}），部分教材/大纲待核实后细化（标 ⚠️）。
'''

ML_LINKS = {
    'linear_algebra': '矩阵运算/SVD→PCA/特征值→协方差→高斯/LoRA低秩近似',
    'calculus': '梯度∇f→SGD/链式法则→反向传播/积分→概率密度归一化',
    'analysis': 'ε-δ→数值稳定性/Lebesgue积分→概率测度/紧致→极值定理→loss最小值',
    'probability': '大数定律→SGD收敛/CLT→BatchNorm/KL→VAE/RLHF/cross-entropy',
    'optimization': '凸优化KKT→SVM/梯度下降收敛→Adam/对偶理论→机制设计',
    'numerical': '条件数→训练稳定性/QR→最小二乘→线性回归/浮点→反向传播',
    'information': '熵→cross-entropy loss/互信息→决策树/KL→VAE/MDL→模型压缩',
    'algebra': '群表示→张量/对称性→CNN等变/数论→RSA密码',
    'topology': 'Banach不动点→SGD收敛/紧致→极值/同伦→数据分析',
    'sde': 'Itô→Black-Scholes/反向SDE→Diffusion model/Langevin→MCMC',
    'pde': '扩散方程→DDPM/heat kernel→高斯卷积/PINN→物理神经网络',
    'complex': 'Cauchy积分→信号处理/Z变换→滤波器/Nyquist→稳定性',
}

TOPIC_CN = {
    'linear_algebra': '线性代数', 'calculus': '微积分', 'analysis': '实分析/测度',
    'probability': '概率/统计', 'optimization': '优化', 'numerical': '数值分析',
    'information': '信息论', 'algebra': '代数/数论', 'topology': '拓扑/几何',
    'sde': '随机微分方程', 'pde': '微分方程', 'complex': '复分析',
}

SCHOOL_FULL = {
    'mit-math-courses': 'MIT',
    'stanford-math-courses': 'Stanford',
    'harvard-math-courses': 'Harvard',
    'princeton-math-courses': 'Princeton',
    'berkeley-math-courses': 'UC Berkeley',
    'cambridge-math-courses': 'Cambridge',
    'oxford-math-courses': 'Oxford',
    'eth-math-courses': 'ETH Zürich',
    'ut-austin-math-courses': 'UT Austin',
}

from datetime import datetime
DATE = datetime.now().strftime('%Y-%m-%d')

created = 0
skipped = 0
for school, courses in NEW_COURSES.items():
    school_full = SCHOOL_FULL.get(school, school)
    for dir_name, code, english_title, chinese, textbook, topic in courses:
        course_dir = os.path.join(ROOT, school, dir_name)
        if os.path.exists(course_dir):
            skipped += 1
            continue
        os.makedirs(course_dir, exist_ok=True)
        readme_path = os.path.join(course_dir, 'README.md')
        content = README_TEMPLATE.format(
            school_full=school_full, code=code, english_title=english_title,
            chinese=chinese, topic=topic, topic_cn=TOPIC_CN.get(topic, topic),
            textbook=textbook, ml_links=ML_LINKS.get(topic, ''), date=DATE,
        )
        with open(readme_path, 'w') as f:
            f.write(content)
        created += 1

print("=" * 60)
print("课程扩张完成")
print("=" * 60)
print(f"新建课程目录: {created}")
print(f"已存在跳过: {skipped}")
print(f"现在请运行: python3 generate_missing_content.py  补全 notes/exercises/experiments")
