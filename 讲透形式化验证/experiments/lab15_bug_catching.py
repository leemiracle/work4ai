#!/usr/bin/env python3
"""lab15 · 漏洞捕捉:手写 WP 谓词变换子 + 契约/不变式检查 + 有界反例(15 章 §三/§四/§五)。
设计决定:谓词/表达式全部用闭包(σ→bool / σ→int)表示,WP 的"代入"退化为函数复合——
  wp(x:=e, Q) = λσ. Q(σ[x↦e(σ)])
于是不需要符号重写引擎,纯 Python 得到语义精确的 WP;四规则的推导记号随算随记,
供手推对照(15 章 §四的轨迹即本文件输出)。循环的 WP 是最小不动点,一般不可计算——
按 15-414 的做法由人提供不变式 I,检查三条验证义务(VC):
  入口 P ⟹ I / 保持 I∧b ⟹ wp(body,I) / 出口 I∧¬b ⟹ Q;或用 wp_while 卷成一条谓词。
有界检查 ≠ 证明:枚举小值域代替全称量词,这一步在真实工具里交给 SMT(03 章)。
E1 WP 四规则手推:y=x+1; if y>0 {z=y} else {z=-y},后置 z≥0 → 有界域全绿。
E2 契约破坏:同一程序期望 z≥1 → VC 在 x=-1 处破(0 的边界),mini-BMC 给出反例轨迹。
E3 不变式:求和循环 s=n(n-1)/2 正确版三条 VC 全过;换序 bug 版破在"保持"义务(归纳步)。
E4 终止性:while i≠0 { i:=i-2 } → 变式(度量)下界义务违规 + 有界执行超步——双重
  "不终止嫌疑"(终止性不可判定:变式是充分性证明,给出即证毕;违规≠必不终止,
  与超步联合才是强信号——9/30 Convergence 讲的定位)。
风格沿用系列:docstring 讲目的、分段 print 结论、末尾 assert 自检。"""
from itertools import product

# ---------- 表示:状态 σ = dict[str,int];表达式/谓词 = (fn, label) ----------

def E(fn, label):            # 表达式:σ → int
    return (fn, label)

def P(fn, label):            # 谓词:σ → bool
    return (fn, label)

def ev(e, s):                # 求值
    return e[0](s)

def pe(p, s):                # 求值(谓词)
    return p[0](s)

def upd(s, x, v):            # 函数式更新:返回新 σ(不改原字典)
    s2 = dict(s); s2[x] = v; return s2

# ---------- WP:四规则 + 分派(谓词的 C[0] 可调用,语句的 C[0] 是标签串) ----------

def wp_assign(x, e, Q):
    """规则 1(赋值):wp(x:=e, Q) = Q[e/x]。闭包实现:λσ. Q(σ[x↦e(σ)])——语义精确;
    label 只记录代入记号,供人对照。"""
    return P(lambda s: pe(Q, upd(s, x, ev(e, s))),
             f"{Q[1]}[{e[1]}/{x}]")

def wp_if(b, T, F, Q):
    """规则 3(条件):wp(if b T F, Q) = (b → wp(T,Q)) ∧ (¬b → wp(F,Q))。
    确定性语言里"→ 合取"与"按 b 选分支求值"等价,闭包取后者。"""
    wT, wF = wp(T, Q), wp(F, Q)
    return P(lambda s: pe(wT, s) if pe(b, s) else pe(wF, s),
             f"({b[1]} → {wT[1]}) ∧ (¬{b[1]} → {wF[1]})")

def wp_while(I, b, body, Q):
    """规则 4(循环):WP 是最小不动点,不可计算;由人供不变式 I,一次展开成一条
    可检查的谓词(9/18 Loops 讲的核心):
        wp(while b body, Q) ≜ I ∧ (¬b → Q) ∧ (b → wp(body, I))
    I∧¬b 蕴含出口后置 Q;I∧b 进一圈身体回到 I(归纳)。"""
    wb = wp(body, I)
    return P(lambda s: pe(I, s) and (pe(Q, s) if not pe(b, s) else pe(wb, s)),
             f"{I[1]} ∧ (¬{b[1]} → {Q[1]}) ∧ ({b[1]} → {wb[1]})")

def wp(C, Q):
    """规则分派:C 已是谓词则原样返回;语句按标签走四规则。规则 2(顺序):
    wp(C1;C2, Q) = wp(C1, wp(C2, Q)) —— 从后往前复合。"""
    if callable(C[0]):
        return C
    tag = C[0]
    if tag == "assign":
        return wp_assign(C[1], C[2], Q)
    if tag == "seq":
        return wp(C[1], wp(C[2], Q))
    if tag == "if":
        return wp_if(C[1], C[2], C[3], Q)
    if tag == "while":
        raise ValueError("while 的 WP 是不动点:请用 wp_while 提供不变式")
    raise ValueError(tag)

# ---------- 语义:结构化操作语义的解释器(15 章 §二) ----------

def run(C, s, trace=None, steps=(0,), limit=None):
    """大步解释器(与 15 章 §二的小步规则一一对应);limit 界内未结束则抛
    StepLimit——mini-BMC 的"超步 = 不终止嫌疑"。trace 记录赋值轨迹。"""
    tag = C[0]
    if tag == "assign":
        v = ev(C[2], s)
        if trace is not None:
            trace.append(f"{C[1]} := {C[2][1]}  (={v})")
        return upd(s, C[1], v)
    if tag == "seq":
        return run(C[2], run(C[1], s, trace, steps, limit), trace, steps, limit)
    if tag == "if":
        return run(C[2] if pe(C[1], s) else C[3], s, trace, steps, limit)
    if tag == "while":
        out = s
        while pe(C[1], out):
            if limit is not None:
                steps[0] += 1
                if steps[0] > limit:
                    raise RuntimeError("StepLimit")
            out = run(C[2], out, trace, steps, limit)
        return out
    raise ValueError(tag)

# ---------- 有界检查:枚举小值域代替全称量词 ----------

def domain(vars_ranges):
    """值域笛卡尔积 → σ 迭代器。"""
    names = list(vars_ranges)
    for vals in product(*[vars_ranges[v] for v in names]):
        yield dict(zip(names, vals))

def bounded_check(p, vars_ranges, assume=None):
    """有界域上检查 p 被'一切满足 assume 的状态'满足;返回违反例列表。
    有界全绿 ≠ 证明,违反即反例——03 章"SMT 全称量词"与"BMC 枚举"的分工。"""
    bad = []
    for s in domain(vars_ranges):
        if assume is None or pe(assume, s):
            if not pe(p, s):
                bad.append(s)
    return bad

# ================= E1 · WP 四规则手推 =================
print("=" * 68)
print("E1 · WP 四规则手推:y=x+1; if y>0 {z=y} else {z=-y},后置 z≥0")
print("=" * 68)
x, y = "x", "y"
PROG = ("seq",
        ("assign", y, E(lambda s: s[x] + 1, "x+1")),
        ("if", P(lambda s: s[y] > 0, "y>0"),
         ("assign", "z", E(lambda s: s[y], "y")),
         ("assign", "z", E(lambda s: -s[y], "-y"))))
Q0 = P(lambda s: s["z"] >= 0, "z≥0")
w = wp(PROG, Q0)
print("程序:  y := x+1;  if y>0 { z := y } else { z := -y }")
print("后置:  Q : z ≥ 0\n")
print("规则 2(顺序)  wp(C1;C2, Q) = wp(C1, wp(C2, Q)) —— 先算内层 if:")
print(f"  规则 3(条件)  wp(if, Q) = ({PROG[2][1][1]} → {wp(PROG[2][2], Q0)[1]}) ∧ (¬{PROG[2][1][1]} → {wp(PROG[2][3], Q0)[1]})")
print(f"  规则 1(赋值)  最外层把 y:=x+1 代入:")
print(f"  wp(程序, Q) = {w[1]}")
bad = bounded_check(w, {"x": range(-5, 6)})
print(f"\n有界检查(|x|≤5):{'全绿 —— wp 对每个 x 成立(此例它是重言式)' if not bad else f'违反于 {bad}'}")
assert not bad
print("→ E1 自检通过:四规则复合出的 wp 即'最弱前条件'——它成立则程序正确")

# ================= E2 · 契约破坏:mini-BMC 反例 =================
print("\n" + "=" * 68)
print("E2 · 契约破坏:期望 z≥1(忘了 y=0 的边界)→ WP 定位 + BMC 反例轨迹")
print("=" * 68)
Q1 = P(lambda s: s["z"] >= 1, "z≥1")
w1 = wp(PROG, Q1)
bad1 = bounded_check(w1, {"x": range(-5, 6)})
print(f"wp(程序, z≥1) = {w1[1]}")
print(f"有界检查:违反于 {[s['x'] for s in bad1]} —— x=-1 时 y=0,z=-0=0,z≥1 破")
assert [s["x"] for s in bad1] == [-1]
trace = []
end = run(PROG, {"x": -1}, trace)
print("mini-BMC 反例轨迹(反例 = 模型,可独立复算):")
print(f"  x = -1 ─┬─ {' ; '.join(trace)}")
print(f"          └─ 终态 z = {end['z']} → 后置 z≥1 假")
assert end["z"] == 0
print("→ E2 自检通过:WP 说'哪类前置违反',BMC 给'哪条具体轨迹'——一静一动")

# ================= E3 · 不变式:三条 VC =================
print("\n" + "=" * 68)
print("E3 · 循环不变式:s = Σ i = n(n-1)/2 —— 正确版 vs 换序 bug 版")
print("=" * 68)
PRE = P(lambda s: s["n"] >= 0, "n≥0")
INV = P(lambda s: 2 * s["s"] == s["i"] * (s["i"] - 1) and s["i"] <= s["n"],
        "2s = i(i-1) ∧ i ≤ n")
POST = P(lambda s: 2 * s["s"] == s["n"] * (s["n"] - 1) and s["i"] == s["n"],
         "2s = n(n-1) ∧ i = n")
cond = P(lambda s: s["i"] < s["n"], "i<n")
body_ok = ("seq", ("assign", "s", E(lambda s: s["s"] + s["i"], "s+i")),
           ("assign", "i", E(lambda s: s["i"] + 1, "i+1")))
body_bug = ("seq", ("assign", "i", E(lambda s: s["i"] + 1, "i+1")),
            ("assign", "s", E(lambda s: s["s"] + s["i"], "s+i")))   # 先加一再累加 → 多加一项
init = ("seq", ("assign", "i", E(lambda s: 0, "0")),
        ("assign", "s", E(lambda s: 0, "0")))

def check_vcs(body, name):
    """三条 VC 分开查(便于定位);保持/出口义务要对'一切满足 I∧b(或 I∧¬b)的循环头
    状态'成立——不只可达的那些,所以枚举 (i,s,n) 全小域再用 I∧b 过滤:把全称量词
    交给枚举(真实工具里这步是 SMT)。"""
    v_entry = bounded_check(wp(init, INV), {"n": range(0, 7)})
    keep_bad = bounded_check(wp(body, INV),
                             {"i": range(0, 7), "s": range(0, 30), "n": range(0, 7)},
                             assume=P(lambda s: pe(INV, s) and pe(cond, s), "I∧i<n"))
    exit_bad = bounded_check(POST,
                             {"i": range(0, 7), "s": range(0, 30), "n": range(0, 7)},
                             assume=P(lambda s: pe(INV, s) and not pe(cond, s), "I∧i≥n"))
    print(f"[{name}] 入口违例 {len(v_entry)} | 保持违例 {len(keep_bad)} | 出口违例 {len(exit_bad)}")
    if keep_bad:
        w0 = keep_bad[0]
        tr = []
        end0 = run(body, dict(w0), tr)
        print(f"  保持义务破于循环头 σ={w0} → 身体执行 {' ; '.join(tr)} → 终态 s={end0['s']},i={end0['i']}(I 不再成立)")
    return not v_entry and not keep_bad and not exit_bad

ok = check_vcs(body_ok, "正确版")
assert ok, "正确版三条 VC 应全过"
bug = check_vcs(body_bug, "bug 版(先 i+1 再累加)")
assert not bug, "bug 版应破在保持义务"

# 同一件事的"一条谓词"形态:wp_while 把三条义务卷起来,在入口域上一次判完
for tag, body in (("正确版", body_ok), ("bug 版 ", body_bug)):
    wpw = wp_while(INV, cond, body, POST)
    bad_all = [n for n in range(0, 7) if pe(PRE, {"n": n}) and not pe(wpw, run(init, {"n": n}))]
    print(f"wp_while 卷一条谓词[{tag}]:入口 n∈0..6 违反 {len(bad_all)} 个 —— {wpw[1][:60]}…")
    if tag == "正确版":
        assert not bad_all
    else:
        assert len(bad_all) >= 1
print("→ E3 自检通过:不变式 = 归纳假设;保持义务破 = 归纳步断,bug 被钉死在循环头")

# ================= E4 · 终止性:变式 + 超步 =================
print("\n" + "=" * 68)
print("E4 · 终止性:while i≠0 { i := i-2 } —— 变式义务违规 + 有界超步双重信号")
print("=" * 68)
b4 = P(lambda s: s["i"] != 0, "i≠0")
body4 = ("assign", "i", E(lambda s: s["i"] - 2, "i-2"))
# 终止性证明 = 找变式 v:循环头 v 有下界(整数域)且每圈严格递减 → v 必触界,b 变假。
# 提名 v := i。"严格递减"恒成立(每圈 -2);待验的是下界保持:
#   循环头 i≠0 时 body 执行后仍有 i ≥ 0 —— 即 wp(body, i≥0) 在循环头域上成立。
wp_body_inv = wp(body4, P(lambda s: s["i"] >= 0, "i≥0"))
viol = bounded_check(wp_body_inv, {"i": range(1, 9)},
                     assume=P(lambda s: s["i"] != 0, "i≠0"))
print("程序:while i≠0 { i := i-2 },提名变式 v := i(每圈严格递减 ✓,下界 0 待验)")
print(f"变式义务 wp(body, i≥0) 的一步违反例:i = {[s['i'] for s in viol]} —— i=1 直接跳过 0 变 -1;")
print("  更深的奇数 3→1→-1 迟早走到这一步;偶数则安全到 0。变式证毕的可能性被排除。")
assert [s["i"] for s in viol] == [1]
try:
    steps = [0]
    run(("while", b4, body4), {"i": 1}, None, steps, limit=50)
    raise AssertionError("不应到达")
except RuntimeError as e:
    assert e.args == ("StepLimit",)
    print("有界执行(k=50)从 i=1 起超步:1 → -1 → -3 → … 永不触 0 → 不终止(此例确凿)")
print("→ E4 自检通过:变式违规(证明侧)+ 超步(执行侧)联合;单独的变式违规只是嫌疑,")
print("   因为变式是充分性证明——换一个更聪明的变式也许仍能证毕(终止性不可判定)")

print("\nlab15 全部自检通过")
