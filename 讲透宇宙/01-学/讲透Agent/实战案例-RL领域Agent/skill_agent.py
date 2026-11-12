#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_agent —— rl_agent v3：skill 库为一等公民（融合 skills 全技术 × RL 自进化）
================================================================================
skills 技术融合清单（对齐 deepseek-harness 插件机制全景六要素 + deer-flow + opencode）：
  1. Plugin 形态    → skill = JSON 文件（name/description/triggers/body/meta），
                      语义对齐 opencode SKILL.md（name/description/triggers）
  2. Loader / HMR   → SkillStore.scan() 每任务前热重扫（新 skill 落盘即生效）
  3. 渐进披露       → 决策只看 description，body 执行时才展开（省上下文 ← deer-flow）
  4. scope          → triggers 限定激活状态（experiment/concept/paper/mixed）
  5. 自修改         → evolve_skills()：生成/变异/淘汰（← 讲透Agent/05 What 轴 + PaperAgent §九
                      SkillWeaver 思想：agent 自己造工具）
  6. preset / hook  → seed_skills() 专属 RL 领域 8 技；execute 前后 hook（meta 统计+reflect 联动）

RL 融合（v2 → v3 的核心升级）：
  - 动作空间 = 原子工具 + skills（v2 固定 4 工具 → v3 动态 N+4）
  - Q(state, skill) ε-greedy；reward = RLVR（skill 产出被采纳=1）
  - skill.meta{usage,success} = 谱系统计 → 变异/淘汰依据（统计即压力，进化即学习）
  - evolve 触发：失败教训聚类 → 生成；低成功率 → 变异；持续失败 → 归档

跑法：python3 skill_agent.py demo | evolve | chat | --task "..."
"""
import json, os, random, re, statistics as st, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rl_agent import (P, classify_state, kb_search, run_experiment, paper_locate, recall,
                      reflect, load_lessons, save_json, load_json, append_progress,
                      EPSILON, ALPHA, Q_INIT, MAX_STEPS, MEMORY, LESSONS_F)

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.join(MEMORY, "skills")
ARCHIVE_DIR = os.path.join(MEMORY, "skills-archive")
QTABLE_F = os.path.join(MEMORY, "skill_qtable.json")

# ============================================================
# ① Skill 形态 + Loader/HMR（Plugin 机制 ← deepseek-harness 02-插件机制全景）
# ============================================================
def new_skill(name, desc, triggers, body):
    return {"name": name, "description": desc, "triggers": triggers, "body": body,
            "meta": {"usage": 0, "success": 0, "born": time.strftime("%m-%d %H:%M"),
                     "origin": "seed", "generations": 0}}

class SkillStore:
    """skill 注册表。scan()=Loader/HMR：每任务前重扫，落盘即生效。"""
    def scan(self):
        os.makedirs(SKILL_DIR, exist_ok=True)
        out = {}
        for fn in sorted(os.listdir(SKILL_DIR)):
            if fn.endswith(".json"):
                try:
                    s = load_json(os.path.join(SKILL_DIR, fn), None)
                    if s and s.get("name") and s.get("body"): out[s["name"]] = s
                except Exception: pass                                    # 坏 skill 隔离跳过（记忆校验 ← security）
        return out
    def save(self, skill):
        os.makedirs(SKILL_DIR, exist_ok=True)
        save_json(os.path.join(SKILL_DIR, skill["name"] + ".json"), skill)
    def archive(self, name):
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        src = os.path.join(SKILL_DIR, name + ".json")
        if os.path.exists(src): os.replace(src, os.path.join(ARCHIVE_DIR, name + ".json"))
    def active_for(self, state, skills):
        """scope：只返回 triggers 含该状态的 skill（渐进披露——只暴露 name+desc）。"""
        return [s for s in skills.values() if state in s["triggers"] or "any" in s["triggers"]]

# ============================================================
# ② preset：专属 RL 领域种子 8 技（body=组合配方：kb_keys/experiment/anchors/answer_mode）
# ============================================================
def seed_skills(store: SkillStore):
    seeds = [
        ("q_learning_tutor", "Q-learning/TD/DQN 概念与公式讲解", ["concept", "mixed"],
         {"kb_keys": ["Q-learning", "TD", "更新"], "experiment": None, "anchors": ["讲透RL/01"], "answer_mode": "CoT"}),
        ("grpo_group_lab", "GRPO 组采样实验：baseline 降方差实测", ["experiment", "mixed"],
         {"kb_keys": ["GRPO", "组内", "baseline"], "experiment": "grpo", "anchors": ["讲透RL/03"], "answer_mode": "ReAct"}),
        ("bandit_playground", "探索-利用三雄对比实验（ε-greedy/UCB/Thompson）", ["experiment", "mixed"],
         {"kb_keys": ["bandit", "regret", "探索"], "experiment": "bandit", "anchors": ["讲透RL/09"], "answer_mode": "ReAct"}),
        ("dqn_replay_guide", "DQN 经验回放+目标网络 toy", ["experiment", "concept"],
         {"kb_keys": ["DQN", "经验回放", "target"], "experiment": "dqn", "anchors": ["讲透RL/01"], "answer_mode": "ReAct"}),
        ("paper_wh_locator", "自进化论文 What/When/信号 三轴定位", ["paper", "mixed"],
         {"kb_keys": ["What", "进化", "arXiv"], "experiment": None, "anchors": ["讲透Agent/05", "PaperAgent"], "answer_mode": "CoT"}),
        ("rlvr_reward_consult", "可验证奖励/奖励五分类设计咨询", ["concept", "paper"],
         {"kb_keys": ["可验证", "奖励", "RLVR"], "experiment": None, "anchors": ["讲透RL/05"], "answer_mode": "CoT"}),
        ("pomdp_explainer", "POMDP/状态观察/Agentic RL 形式化", ["concept", "mixed"],
         {"kb_keys": ["POMDP", "状态", "Agentic"], "experiment": None, "anchors": ["PaperAgent"], "answer_mode": "CoT"}),
        ("meta_prompt_tuner", "meta-skill：调 agent 自身的 tool_prior/停用词（APO 接口）", ["any"],
         {"kb_keys": ["prompt", "先验", "APO"], "experiment": None, "anchors": ["讲透Prompt/09"], "answer_mode": "Reflexion"}),
    ]
    for name, desc, trig, body in seeds:
        store.save(new_skill(name, desc, trig, body))

# ============================================================
# ③ skill 执行器（body=配方 → 原子能力组合）+ 前后 hook（meta 统计）
# ============================================================
def _zh_words(text, top=8):
    """中文分词（无依赖启发式）：ASCII 词 + CJK 二元组，去重取前 top。"""
    words = re.findall(r"[A-Za-z0-9\-\.]{2,}", text)
    cjk = re.sub(r"[^\u4e00-\u9fff]", "", text)
    words += [cjk[i:i+2] for i in range(len(cjk) - 1)]
    stop = {"什么", "怎么", "如何", "设计", "一个", "这个", "在", "的", "是"}
    return [w for w in dict.fromkeys(words) if w not in stop][:top]

def execute_skill(skill, task, store: SkillStore):
    """渐进披露的另一半：此处才展开 body。返回 (ok, obs)。
    相关性闸门（anti reward-hacking）：罐头 kb_keys 命中 ≠ 证据——返回行必须含任务实义词
    （bigram 分词）；且实验只对 experiment 态任务是充分证据（概念题跑实验 ≠ 回答了问题）。"""
    body = skill["body"]
    state = classify_state(task)
    task_words = _zh_words(task)
    parts, exp_ok = [], False
    if body.get("experiment"):
        exp_ok, out_e = run_experiment(body["experiment"])
        parts.append(("exp", exp_ok, out_e))
    keys = body.get("kb_keys", [])
    hits = kb_search(" ".join(task_words[:6] + keys), topk=6)
    anchored = [h for h in hits if any(a in h[1] for a in body.get("anchors", []))]
    use = anchored or hits
    relevant = [h for h in use if any(w in h[2] for w in task_words)]
    if relevant:
        parts.append(("kb", True, "\n".join(f"  {f}「{l}」" for _, f, l in relevant[:4])))
        ok = True
    else:
        parts.append(("kb", False, "[skill 闸门] 命中与任务词无关（罐头 keys/无关实验 ≠ 证据）"))
        ok = exp_ok and state == "experiment"                      # 实验仅对 experiment 态充分
    skill["meta"]["usage"] += 1
    return ok, "\n".join(str(o) for _, _, o in parts if o)[:500]

def skill_success_hook(skill, r):
    skill["meta"]["success"] += r
    skill["meta"]["last_reward"] = r

# ============================================================
# ④ SkillBrain：动态动作空间（原子工具 + scope 内 skills）
# ============================================================
ATOMIC_DESC = {"kb_search": "检索 项目 知识库", "run_experiment": "实验 跑 对比",
               "paper_locate": "论文 arXiv 综述 定位"}
def desc_match_bonus(name, task, active_skills):
    """渐进披露的真正价值（opencode SKILL.md 同款机制）：按 description 语义匹配加先验。
    active_skills 是 scope 内 skill dict 列表（v3.0.1 修复：list 而非 dict 查找）。"""
    smap = {s["name"]: s for s in active_skills} if active_skills and isinstance(active_skills[0], dict) else {}
    desc = f"{name} {ATOMIC_DESC.get(name, '')}"
    if name in smap:
        desc = f"{smap[name]['name']} {smap[name]['description']}"
    return 0.05 * sum(1 for w in _zh_words(task) if w.lower() in desc.lower())

class SkillBrain:
    def __init__(self):
        self.Q = load_json(QTABLE_F, {})
    def pick(self, state, rng, skills, exclude=frozenset(), task=""):
        atomic = ["kb_search", "run_experiment", "paper_locate"]
        avail_sk = [s["name"] for s in skills if state in s["triggers"] or "any" in s["triggers"]]
        # skill 优先序（冷启动发现）+ description 语义匹配先验（渐进披露的选型机制）
        avail = [a for a in avail_sk + atomic if a not in exclude] or atomic
        row = self.Q.get(state, {})
        if rng.random() < EPSILON: return rng.choice(avail)                # 探索（新 skill 由此被发现）
        return max(avail, key=lambda a: round(row.get(a, Q_INIT)
                    + desc_match_bonus(a, task, skills), 4))              # 利用 + 语义先验（Q 学习值会逐渐盖过）
    def update(self, state, a, r):
        row = self.Q.setdefault(state, {})
        row[a] = row.get(a, Q_INIT) + ALPHA * (r - row.get(a, Q_INIT))
        save_json(QTABLE_F, self.Q)

def act(name, task, skills, store):
    """统一动作分发：原子工具 or skill。"""
    if name in skills:
        return execute_skill(skills[name], task, store)
    if name == "kb_search":
        hits = kb_search(task)
        return (bool(hits), "\n".join(f"  {f}「{l}」" for _, f, l in hits[:4]) or "无命中")
    if name == "run_experiment":
        exp = next((e for e in ["gridworld", "dqn", "bandit", "grpo", "dpo", "curriculum"] if e in task.lower()), None)
        if not exp: return False, "未指明实验名"
        return run_experiment(exp)
    if name == "paper_locate": return paper_locate(task)
    return False, "unknown"

# ============================================================
# ⑤ skill-aware ReAct 主循环
# ============================================================
def solve(task, brain: SkillBrain, store: SkillStore, rng, verbose=True):
    state = classify_state(task)
    skills = store.scan()                                                 # ← Loader/HMR：每任务热加载
    if verbose: P(f"◆ 任务: {task}\n  [Thought] 状态={state}｜可用 skill {len(skills)} 个（渐进披露："
                  + ", ".join(f"{s['name']}({s['meta']['usage']}用{s['meta']['success']}成)" for s in store.active_for(state, skills))[:100] + "）")
    got, ev_skill, chain, failed = False, None, [], set()
    for step in range(MAX_STEPS):
        a = brain.pick(state, rng, store.active_for(state, skills), exclude=failed, task=task)
        ok, obs = act(a, task, skills, store)
        chain.append(a)
        if verbose: P(f"  [Act {step+1}] {a} → {str(obs)[:140]}")
        if ok:
            got, ev_skill = True, (a if a in skills else None)
            if a in skills:
                skill_success_hook(skills[a], 1.0)                         # 后 hook：先记成功（若终局反转再修正）
                store.save(skills[a])
            break
        failed.add(a)
    # 终局 RLVR（experiment 态防短路 ← v2 教训）
    r = 1.0 if (got and (state != "experiment" or any(c in skills or c == "run_experiment" for c in chain))) else 0.0
    for a in set(chain): brain.update(state, a, r if (got and a == chain[-1]) else 0.0)
    if not got and verbose: P("  [Final] ⚠ 未能取证")
    if r == 0.0:
        lesson = f"「{task[:40]}」失败于{chain}(state={state})"
        msg = reflect(task, state, chain, lesson)
        if verbose: P(f"  [Reflexion] {msg}")
    append_progress(task, chain, r)
    return {"task": task, "state": state, "chain": chain, "reward": r}

# ============================================================
# ⑥ 自修改：evolve_skills（生成/变异/淘汰 ← SkillWeaver + What 轴）
# ============================================================
MUTATIONS = {
    "扩检索词":  lambda b: {**b, "kb_keys": b.get("kb_keys", []) + ["原理", "推导", "公式"]},
    "换实验":   lambda b: {**b, "experiment": "curriculum" if b.get("experiment") != "curriculum" else "gridworld"},
    "answer→ReAct": lambda b: {**b, "answer_mode": "ReAct"},
    "加停用词": lambda b: {**b, "stopwords_extra": ["一下", "怎么"]},
}
def _zh_words_flat(texts, top=6):
    """多条文本展平去重取词（evolve 生成用）。"""
    seen = []
    for t in texts:
        for w in _zh_words(t, top=20):
            if w not in seen: seen.append(w)
    return seen[:top]

def evolve_skills(store: SkillStore, verbose=True):
    """进化三操作。依据=谱系统计（meta）+ 教训聚类（lessons）——统计即压力。"""
    skills = store.scan()
    lessons = load_lessons()
    report = {"born": [], "mutated": [], "archived": []}
    # (a) 生成：同 state 失败≥2 且该 state 无 success_rate≥0.5 的 skill → 从失败任务词生成新 skill
    from collections import Counter
    fail_states = Counter(l["state"] for l in lessons if l.get("state"))
    for state, n in fail_states.items():
        if n < 2: continue
        words = _zh_words_flat([l["task"] for l in lessons if l["state"] == state], top=6)
        local = [s for s in skills.values() if state in s["triggers"]]
        covered = any(any(w in json.dumps(s, ensure_ascii=False) for w in words) for s in local)
        if covered: continue                                              # 守卫=覆盖检查：已有 skill 键命中失败词则不重复造
        name = f"adaptive_{state}_{len(skills)+1}"
        sk = new_skill(name, f"进化生成：{state} 态自适应（源自 {n} 条失败教训）", [state, "any"],
                       {"kb_keys": words, "experiment": None, "anchors": [], "answer_mode": "CoT"})
        sk["meta"]["origin"] = "evolved"
        store.save(sk); report["born"].append(name)
        if verbose: P(f"  🧬 生成 {name}（kb_keys={words}）← {n} 条 {state} 态教训")
    # (b) 变异：usage≥2 且 success/usage<0.5
    for s in store.scan().values():
        u, sc = s["meta"]["usage"], s["meta"]["success"]
        if u >= 2 and sc / u < 0.5 and s["meta"].get("origin") != "just_mutated":
            mname = random.choice(list(MUTATIONS))
            s["body"] = MUTATIONS[mname](s["body"])
            s["meta"]["generations"] += 1; s["meta"]["origin"] = "just_mutated"
            store.save(s); report["mutated"].append(f"{s['name']}←{mname}")
            if verbose: P(f"  🔁 变异 {s['name']} ← {mname}（{sc}/{u} 成功率低）")
    # (c) 淘汰：usage≥3 且 success/usage<0.3 → 归档（遗忘 ← 记忆6操作）
    for s in store.scan().values():
        u, sc = s["meta"]["usage"], s["meta"]["success"]
        if u >= 3 and sc / u < 0.3 and s["meta"]["origin"] != "seed":
            store.archive(s["name"]); report["archived"].append(s["name"])
            if verbose: P(f"  🗑️ 归档 {s['name']}（{sc}/{u}）")
    return report

# ============================================================
# demo：种子→RL 选技→失败→进化→再战 全链路
# ============================================================
DEMO = [
    ("什么是 Q-learning 的时间差分更新？", "concept → desc 语义选型应选 q_learning_tutor"),
    ("跑一个 GRPO 组采样实验", "experiment → grpo_group_lab 实验技能"),
    ("ε 衰减调度在探索利用里怎么设计？", "冷门措辞 → 探索/利用 bigram 命中 KB 真证据（合法成功）"),
    ("qqwwzzpp", "真缺口（乱码）→ 全链失败，教训落盘"),
    ("qqwwzzpp", "再失败 → 教训聚类≥2 → 触发 🧬 skill 库自修改"),
    ("qqwwzzpp", "三战：新生 adaptive skill 优先被探索 → 诚实仍败（进化造结构不造知识）"),
]
def demo():
    store = SkillStore()
    if not store.scan():                                                  # preset
        seed_skills(store); P("[preset] 播种 8 个 RL 领域专属 skill")
    # demo 隔离：清旧教训，保证进化弧线确定性（chat/CLI 不清——持久记忆是特性）
    if os.path.exists(LESSONS_F): os.remove(LESSONS_F)
    brain, rng = SkillBrain(), random.Random(42)
    P("=" * 68); P("skill_agent v3 demo —— skill 库 × RL 自进化"); P("=" * 68)
    P("[Loader] 注册表（渐进披露——name: description）:")
    for s in store.scan().values(): P(f"  · {s['name']}: {s['description'][:44]}")
    stats = []
    for i, (task, note) in enumerate(DEMO):
        P("─" * 60); P(f"【场景{i+1}】{note}")
        if i in (4, 5):                                                   # 教训累积后两度触发自修改
            P("  [evolve] 触发 skill 库自修改：")
            evolve_skills(store)
        stats.append(solve(task, brain, store, rng))
    P("─" * 60)
    P("[终态 skill 谱系] " + " | ".join(
        f"{s['name']}({s['meta']['usage']}用/{s['meta']['success']}成/第{s['meta']['generations']}代)"
        for s in store.scan().values() if s["meta"]["usage"] > 0))
    P(f"[战报] {sum(r['reward'] for r in stats)}/{len(stats)}（KB 覆盖的题全胜；乱码缺口诚实失败 ×3）")
    P("[Q表] " + json.dumps(brain.Q, ensure_ascii=False)[:300])

if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or argv[0] == "demo": demo()
    elif argv[0] == "evolve": SkillStore() and (lambda s: (P(json.dumps(evolve_skills(s), ensure_ascii=False))))(SkillStore())
    elif argv[0] == "--task" and len(argv) > 1:
        solve(argv[1], SkillBrain(), SkillStore(), random.Random(7))
    elif argv[0] == "chat":
        store, brain, rng = SkillStore(), SkillBrain(), random.Random()
        if not store.scan(): seed_skills(store)
        P("skill_agent chat — q 退出")
        while True:
            try: t = input("你> ").strip()
            except EOFError: break
            if t in ("q", "", "quit"): break
            solve(t, brain, store, rng); P()
    else: P(__doc__)
