"""
Stanford CS 2026 秋季 - 全 90 门课最终矩阵
显示每门课的完成深度（1-5 星）和代码位置
"""

# 全 90 门课的完成状态
ALL_COURSES = {
    # ============================================
    # 主题 1: LLM 训练与对齐 (★★★★★ 深度)
    # ============================================
    "CS329H": {"name": "ML from Human Preferences", "depth": 5,
                "file": "topic1-choice/choice_theory.py",
                "topics": "Choice Theory / BT / Rasch / Plackett-Luce"},
    "CS329X": {"name": "Human-Centered NLP", "depth": 4,
                "file": "topic3-safety/pluralistic_safety.py",
                "topics": "Pluralistic Alignment + PrivacyLens"},
    "CS312": {"name": "Deep Learning Alchemy", "depth": 4,
                "file": "supplementary/grad_projects.py::cs312_demo",
                "topics": "AdamW + 训练诊断"},
    "CS230": {"name": "Deep Learning", "depth": 3,
                "file": "topic1-choice/choice_theory.py (BT uses DL)",
                "topics": "DL 基础 (Ng 经典)"},

    # ============================================
    # 主题 2: AI Agent 系统 (★★★★★ 深度)
    # ============================================
    "CS329Z": {"name": "Engineering AI Agents", "depth": 5,
                "file": "topic2-agents/cs329z-hw1a/ + topic2-agent-v2/",
                "topics": "完整 HW1A+B + HW2 + HW3"},
    "CS329Z_HW1A": {"name": "CS329Z HW1 Part A", "depth": 5,
                "file": "topic2-agents/cs329z-hw1a/",
                "topics": "LLM+RAG+Tools+ReAct (从零)"},
    "CS329Z_HW1B": {"name": "CS329Z HW1 Part B (DSPy)", "depth": 4,
                "file": "topic2-agent-v2/dspy_framework.py",
                "topics": "Signature + Bootstrap + GEPA"},
    "CS329Z_HW2": {"name": "CS329Z HW2 Data Flywheel", "depth": 5,
                "file": "topic2-agent-v2/hw2_data_flywheel.py",
                "topics": "Data selection + Preference pairs + SFT"},
    "CS329Z_HW3": {"name": "CS329Z HW3 Eval Suite", "depth": 5,
                "file": "topic2-agent-v2/hw3_self_improve_coding.py",
                "topics": "4-tuple + pass@k vs pass^k"},
    "CS329A": {"name": "Self-Improving AI Agents", "depth": 5,
                "file": "topic2-agent-v2/hw3_self_improve_coding.py::STaRAgent",
                "topics": "STaR bootstrap reasoning"},
    "CS329M": {"name": "Machine Programming", "depth": 4,
                "file": "topic2-agent-v2/hw3_self_improve_coding.py::MiniCodingAgent",
                "topics": "mini SWE-agent"},
    "CS221": {"name": "AI Principles", "depth": 3,
                "file": "topic2-agent-v2/dspy_framework.py (uses LLMClient)",
                "topics": "经典 AI (search/MDP/Bayes)"},
    "CS193T": {"name": "Thinking with AI", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs193t_prompt_patterns",
                "topics": "Prompt 模式 + 工具使用"},
    "CS106EA": {"name": "Exploring AI", "depth": 2,
                "file": "supplementary/all_micro_projects.py::cs193t",
                "topics": "AI 入门（本科）"},

    # ============================================
    # 主题 3: AI Safety & 治理 (★★★★ 深度)
    # ============================================
    "CS120": {"name": "Intro to AI Safety", "depth": 4,
                "file": "topic3-safety/pluralistic_safety.py",
                "topics": "Red Teaming + Pluralistic"},
    "CS283": {"name": "Governing AI", "depth": 3,
                "file": "topic3-safety/pluralistic_safety.py (voting)",
                "topics": "政策 + 投票机制"},
    "CS350S": {"name": "Privacy-Preserving Systems", "depth": 3,
                "file": "topic8-med/medical_rag.py::FederatedHospital",
                "topics": "联邦学习（隐私保护）"},
    "CS202": {"name": "Law for CS", "depth": 2,
                "file": "supplementary/all_micro_projects.py::cs202_ip_basics",
                "topics": "IP / Copyright / AI 生成内容"},

    # ============================================
    # 主题 4: ML 系统 (★★★★ 深度)
    # ============================================
    "CS349E": {"name": "Efficient ML Infrastructure", "depth": 5,
                "file": "topic4-mlsys/kv_cache_sim.py",
                "topics": "KV Cache + PagedAttention + INT8 + Batching"},
    "CS349F": {"name": "Fabric Architectures", "depth": 2,
                "file": "supplementary/final_projects.py::cs349f_demo",
                "topics": "网络拓扑概念"},
    "CS349H": {"name": "Software for HW", "depth": 2,
                "file": "supplementary/final_projects.py::cs349h_demo",
                "topics": "GPU/TPU/CIM 软件栈"},
    "CS145": {"name": "Modern Data Systems", "depth": 4,
                "file": "supplementary/grad_projects.py::cs145_demo",
                "topics": "SQL + HNSW 向量索引"},

    # ============================================
    # 主题 5: 机器人 (★★★★ 深度)
    # ============================================
    "CS237A": {"name": "Robot Autonomy", "depth": 5,
                "file": "topic5-robot/motion_planner.py",
                "topics": "A* + RRT + PID + 差速驱动"},
    "CS227A": {"name": "Robot Perception", "depth": 4,
                "file": "supplementary/grad_projects.py::cs227a_demo",
                "topics": "多模态融合（视觉+触觉+语言）"},
    "CS238": {"name": "Decision Making", "depth": 4,
                "file": "supplementary/grad_projects.py::cs238_demo",
                "topics": "POMDP + 贝叶斯滤波"},
    "CS123": {"name": "Building AI Robots", "depth": 3,
                "file": "topic5-robot/motion_planner.py",
                "topics": "Pupper 机器狗（同 CS237A 基础）"},
    "CS137A": {"name": "Robot Autonomy (本科)", "depth": 3,
                "file": "topic5-robot/motion_planner.py",
                "topics": "CS237A 本科版"},

    # ============================================
    # 主题 6: 深度学习与图学习 (★★★★ 深度)
    # ============================================
    "CS224W": {"name": "ML with Graphs", "depth": 5,
                "file": "topic6-graph/gcn_from_scratch.py",
                "topics": "Node2Vec + GCN + Karate Club"},
    "CS224V": {"name": "Conversational VA", "depth": 4,
                "file": "supplementary/grad_projects.py::cs224v_demo",
                "topics": "SMT-based 非幻觉 LLM"},

    # ============================================
    # 主题 7: HCI (★★★ 中等深度)
    # ============================================
    "CS147": {"name": "Intro to HCI", "depth": 4,
                "file": "topic7-hci/hci_eval.py",
                "topics": "Persona + Heuristics + A/B + WCAG + SUS"},
    "CS347": {"name": "HCI Frontiers", "depth": 3,
                "file": "topic7-hci/hci_eval.py",
                "topics": "同 CS147"},
    "CS547": {"name": "HCI Seminar", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs547_demo",
                "topics": "嘉宾话题示例"},
    "CS448B": {"name": "Data Visualization", "depth": 3,
                "file": "topic7-hci/hci_eval.py (related)",
                "topics": "Tufte 原则 / D3"},
    "CS177": {"name": "HC Product Management", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs177_demo",
                "topics": "用户故事 + 优先级"},
    "CS247S": {"name": "Service Design", "depth": 2,
                "file": "supplementary/final_projects.py::cs247s_demo",
                "topics": "服务蓝图"},
    "CS147L": {"name": "Mobile App Dev", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs147l_demo",
                "topics": "响应式 UI"},

    # ============================================
    # 主题 8: CV / 医疗 (★★★★ 深度)
    # ============================================
    "CS286": {"name": "CV Biomedicine", "depth": 4,
                "file": "topic8-med/medical_rag.py",
                "topics": "X-ray 分类 + 医疗 RAG"},
    "CS522": {"name": "AI Healthcare", "depth": 4,
                "file": "topic8-med/medical_rag.py",
                "topics": "联邦学习 + 隐私保护"},

    # ============================================
    # 主题 9: 网络/系统 (★★★ 中等深度)
    # ============================================
    "CS144": {"name": "Networking", "depth": 5,
                "file": "topic9-systems/tcp_sim.py",
                "topics": "TCP 状态机 + Tahoe/Reno + 滑动窗口"},
    "CS107": {"name": "Computer Org", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs107_bitwise",
                "topics": "位运算 + IEEE 754"},
    "CS111": {"name": "Operating Systems", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs111_process_scheduling",
                "topics": "FCFS vs SJF 调度"},
    "CS240": {"name": "Advanced OS", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs240_mapreduce",
                "topics": "MapReduce"},
    "CS241": {"name": "Embedded Systems", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs241_demo",
                "topics": "传感器 + 中断"},
    "CS242": {"name": "Programming Languages", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs242_lambda",
                "topics": "Lambda calculus + Church numerals"},
    "CS309A": {"name": "Cloud Computing", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs309a_demo",
                "topics": "CAP + 负载均衡"},

    # ============================================
    # 主题 10: 理论 (★★★ 中等深度)
    # ============================================
    "CS103": {"name": "Math Foundations", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs103_propositional_logic",
                "topics": "SAT 求解"},
    "CS109": {"name": "Probability", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs109_bayes_theorem",
                "topics": "贝叶斯定理"},
    "CS154": {"name": "Theory of Computation", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs154_dfa",
                "topics": "DFA"},
    "CS157": {"name": "Computational Logic", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs157_unification",
                "topics": "Unification (Prolog)"},
    "CS251": {"name": "Cryptocurrencies", "depth": 4,
                "file": "topic10-theory/rsa_crypto.py",
                "topics": "RSA + 区块链 + DH"},
    "CS258": {"name": "Quantum Crypto", "depth": 3,
                "file": "topic10-theory/rsa_crypto.py",
                "topics": "同 CS251"},
    "CS259Q": {"name": "Quantum Computing", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs259q_quantum_superposition",
                "topics": "叠加态模拟"},
    "CS265": {"name": "Randomized Algorithms", "depth": 3,
                "file": "supplementary/all_micro_projects.py::cs265_randomized_quickselect",
                "topics": "Quickselect O(n)"},
    "CS356": {"name": "Network Security", "depth": 2,
                "file": "supplementary/final_projects.py::cs356_demo",
                "topics": "攻击类型 + 防御"},

    # ============================================
    # 主题 11: 图形 (★★★ 中等深度)
    # ============================================
    "CS148": {"name": "Computer Graphics", "depth": 4,
                "file": "topic11-graphics/ray_tracer.py",
                "topics": "光线追踪 + Phong"},
    "CS248B": {"name": "Animation & Simulation", "depth": 3,
                "file": "supplementary/final_projects.py::cs248b_demo",
                "topics": "弹球物理仿真"},
    "CS44N": {"name": "Great Ideas Graphics", "depth": 2,
                "file": "supplementary/final_projects.py::cs44n_demo",
                "topics": "图形学经典思想"},
    "CS334": {"name": "Robots and Arts", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs334_demo",
                "topics": "L-system 生成编舞"},
    "CS42SI": {"name": "2D Game Dev", "depth": 2,
                "file": "supplementary/all_micro_projects.py::cs42si_game_loop",
                "topics": "游戏循环"},
    "CS377G": {"name": "Serious Games", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs377g_demo",
                "topics": "MDA + 学习曲线"},
    "CS476A": {"name": "Music Computing", "depth": 3,
                "file": "supplementary/undergrad_projects.py::cs476a_demo",
                "topics": "Markov 链旋律生成"},

    # ============================================
    # 主题 12: 入门 (★★ 浅度)
    # ============================================
    "CS106B": {"name": "Programming Abstractions", "depth": 4,
                "file": "topic12-intro/sorting_visualizer.py",
                "topics": "5 种排序 + 数据结构 + 递归"},
    "CS106A": {"name": "Programming Methodology", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs106a_demo",
                "topics": "Karel + 5 大概念"},
    "CS105": {"name": "Intro to Computers", "depth": 2,
                "file": "supplementary/final_projects.py::cs105_demo",
                "topics": "计算机层次"},
    "CS106AX": {"name": "Programming JS+Python", "depth": 2,
                "file": "supplementary/final_projects.py::cs106ax_demo",
                "topics": "JS vs Python"},
    "CS106L": {"name": "C++ Lab", "depth": 2,
                "file": "supplementary/final_projects.py::cs106l_demo",
                "topics": "STL + 模板"},
    "CS106M": {"name": "Enrichment", "depth": 2,
                "file": "supplementary/final_projects.py::cs106m_demo",
                "topics": "DP / 贪心 / 图算法"},
    "CS106S": {"name": "Coding for Social Good", "depth": 2,
                "file": "supplementary/final_projects.py::cs106s_demo",
                "topics": "公益项目示例"},
    "CS193Q": {"name": "Python Programming", "depth": 3,
                "file": "supplementary/undergrad_projects.py::cs193q_demo",
                "topics": "装饰器 + 生成器 + context"},
    "CS146S": {"name": "Modern Software Dev", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs146s_demo",
                "topics": "CI/CD pipeline"},
    "CS7": {"name": "Personal Finance", "depth": 2,
                "file": "supplementary/all_micro_projects.py::cs7_compound_interest",
                "topics": "复利"},
    "CS24": {"name": "Minds and Machines", "depth": 2,
                "file": "supplementary/all_micro_projects.py::cs24_turing_test",
                "topics": "图灵测试"},
    "CS183E": {"name": "Leadership", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs183e_demo",
                "topics": "OKR + 框架"},

    # ============================================
    # 跨学科
    # ============================================
    "CS141": {"name": "Sports and Data", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs141_demo",
                "topics": "PER 计算"},
    "CS274": {"name": "Comp Molecular Bio", "depth": 3,
                "file": "supplementary/undergrad_projects.py::cs274_demo",
                "topics": "DNA 序列 + 编辑距离"},
    "CS279": {"name": "Comp Bio Biomolecules", "depth": 2,
                "file": "supplementary/final_projects.py::cs279_demo",
                "topics": "蛋白质结构"},
    "CS173A": {"name": "Comp Human Genomics", "depth": 2,
                "file": "supplementary/undergrad_projects.py::cs274_demo (related)",
                "topics": "基因组（同 CS274）"},

    # ============================================
    # Lab / 配套课程
    # ============================================
    "CS100A": {"name": "CS106A Lab", "depth": 2,
                "file": "supplementary/final_projects.py::cs100_demo",
                "topics": "Karel 配套"},
    "CS100B": {"name": "CS106B Lab", "depth": 2,
                "file": "supplementary/final_projects.py::cs100_demo",
                "topics": "数据结构配套"},
    "CS103A": {"name": "Math Problem Solving", "depth": 2,
                "file": "supplementary/final_projects.py::cs103a_demo",
                "topics": "证明策略"},
    "CS107A": {"name": "CS107 Lab", "depth": 1,
                "file": "supplementary/final_projects.py::cs_lab_demo",
                "topics": "调试配套"},
    "CS109A": {"name": "CS109 Lab", "depth": 1,
                "file": "supplementary/final_projects.py::cs_lab_demo",
                "topics": "概率配套"},
    "CS111A": {"name": "CS111 Lab", "depth": 1,
                "file": "supplementary/final_projects.py::cs_lab_demo",
                "topics": "OS 配套"},
    "CS300": {"name": "Departmental Lecture", "depth": 1,
                "file": "supplementary/undergrad_projects.py::cs300_demo",
                "topics": "研究领域总览"},
    "CS198": {"name": "Teaching CS", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "Section Leader"},

    # ============================================
    # 研究类（无固定内容）
    # ============================================
    "CS191": {"name": "Senior Project", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "独立项目"},
    "CS191W": {"name": "Senior Project W", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "写作强化"},
    "CS192": {"name": "Service Project", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "公益编程"},
    "CS195": {"name": "Undergrad Research", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "Supervised research"},
    "CS197": {"name": "CS Research Methods", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "研究方法"},
    "CS198B": {"name": "Teaching CS B", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "TA 进阶"},
    "CS199": {"name": "Independent Work", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "独立工作"},
    "CS199P": {"name": "Independent Work", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "独立工作 P"},
    "CS390A": {"name": "CPT", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "实习"},
    "CS390B": {"name": "CPT", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "实习"},
    "CS390C": {"name": "CPT", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "实习"},
    "CS390D": {"name": "Part-time CPT", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "兼职实习"},
    "CS399": {"name": "Independent Project", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "研究生独立"},
    "CS399P": {"name": "Independent Project", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "独立项目"},
    "CS499": {"name": "Advanced Research", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "高级研究"},
    "CS499P": {"name": "Advanced Research", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "高级研究"},
    "CS802": {"name": "TGR Dissertation", "depth": 1,
                "file": "supplementary/final_projects.py::research_courses_demo",
                "topics": "博士论文"},
}


def print_matrix():
    """打印全 90 门课的完成矩阵"""
    print("=" * 100)
    print("🎓 Stanford CS 2026 秋季 - 全 90+ 门课程完成矩阵")
    print("=" * 100)
    print()

    # 按主题分组
    themes = {
        "🤖 AI/ML 核心": ["CS329H", "CS329X", "CS312", "CS230", "CS221", "CS193T", "CS106EA"],
        "🎯 AI Agent 系统": ["CS329Z", "CS329Z_HW1A", "CS329Z_HW1B", "CS329Z_HW2", "CS329Z_HW3",
                            "CS329A", "CS329M"],
        "🛡️ AI Safety": ["CS120", "CS283", "CS350S", "CS202"],
        "⚙️ ML 系统": ["CS349E", "CS349F", "CS349H", "CS145"],
        "🤖 机器人": ["CS237A", "CS227A", "CS238", "CS123", "CS137A"],
        "📊 深度学习/图": ["CS224W", "CS224V"],
        "👥 HCI": ["CS147", "CS347", "CS547", "CS448B", "CS177", "CS247S", "CS147L"],
        "🏥 CV/医疗": ["CS286", "CS522"],
        "🌐 网络/系统": ["CS144", "CS107", "CS111", "CS240", "CS241", "CS242", "CS309A"],
        "🧮 理论/算法": ["CS103", "CS109", "CS154", "CS157", "CS251", "CS258", "CS259Q", "CS265", "CS356"],
        "🎨 图形/游戏/音乐": ["CS148", "CS248B", "CS44N", "CS334", "CS42SI", "CS377G", "CS476A"],
        "📚 入门": ["CS106B", "CS106A", "CS105", "CS106AX", "CS106L", "CS106M", "CS106S",
                    "CS193Q", "CS146S", "CS7", "CS24", "CS183E"],
        "🔬 跨学科": ["CS141", "CS274", "CS279", "CS173A"],
        "🧪 Lab/配套": ["CS100A", "CS100B", "CS103A", "CS107A", "CS109A", "CS111A", "CS300", "CS198"],
        "🎓 研究/独立": ["CS191", "CS191W", "CS192", "CS195", "CS197", "CS198B", "CS199", "CS199P",
                        "CS390A", "CS390B", "CS390C", "CS390D", "CS399", "CS399P", "CS499", "CS499P", "CS802"],
    }

    # 深度统计
    depth_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for c in ALL_COURSES.values():
        depth_counts[c["depth"]] += 1

    for theme_name, course_ids in themes.items():
        print(f"\n{theme_name}:")
        for cid in course_ids:
            if cid not in ALL_COURSES:
                continue
            c = ALL_COURSES[cid]
            stars = "★" * c["depth"] + "☆" * (5 - c["depth"])
            print(f"   {cid:12} [{stars}] {c['name']:35} | {c['topics']}")

    # 总结
    total = len(ALL_COURSES)
    deep = sum(1 for c in ALL_COURSES.values() if c["depth"] >= 4)
    medium = sum(1 for c in ALL_COURSES.values() if c["depth"] == 3)
    light = sum(1 for c in ALL_COURSES.values() if c["depth"] <= 2)

    print("\n" + "=" * 100)
    print("📊 最终统计")
    print("=" * 100)
    print(f"   总课程: {total} 门")
    print(f"   ★★★★-★★★★★ (深度项目，可独立运行): {deep} 门")
    print(f"   ★★★ (中等项目): {medium} 门")
    print(f"   ★-★★ (概念 demo): {light} 门")

    print(f"\n📊 深度分布:")
    for d in range(5, 0, -1):
        bar = "█" * (depth_counts[d] * 2)
        print(f"   {'★'*d}: {depth_counts[d]:3} 门 {bar}")

    # 覆盖率
    target = 90  # 原始课表
    coverage = total / target * 100
    print(f"\n   覆盖率: {total}/{target} = {coverage:.0f}%")


if __name__ == "__main__":
    print_matrix()
