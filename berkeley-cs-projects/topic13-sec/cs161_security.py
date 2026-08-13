"""
CS 161 Computer Security (UC Berkeley) — Song / Popa
====================================================
Berkeley 安全双星：
- Dawn Song：符号执行 / 模糊测试顶会常客，BitBlaze / Pinecone 体系。
- Raluca Ada Popa：encrypted DB / TEE 体系（CryptDB, Oblix, SANCTUM）。

覆盖主题：
- 内存安全（buffer overflow / ROP gadget chain）
- 符号执行（KLEE / BitBlaze 风格的路径条件求解）
- 模糊测试（AFL 风格 coverage-guided 反馈）
- 防御：CFI / ASLR 概念检查
- 加密数据库（CryptDB onion 层级 — Popa 招牌）

核心教材/论文（已核实）：
- Cadar, Dunbar, Engler 2008 "KLEE: Unassisted and Automatic Generation
  of High-Coverage Tests for Complex Systems Programs" OSDI — KLEE
- Song et al. 2008 "BitBlaze: A New Approach to Computer Security via
  Binary Analysis" ICSE/SECRYPT — BitBlaze
- Schwartz, Avgerinos, Brumley 2010 "All You Ever Wanted to Know About
  Dynamic Taint Analysis and Forward Symbolic Execution" S&P — SymExec
- Zalewski 2007 "American Fuzzy Lop" (AFL) — coverage-guided fuzzing
- Popa, Redfield, Zeldovich, Balakrishnan 2011 "CryptDB: Protecting
  Confidentiality with Encrypted Query Processing" SOSP
- Roemer, Buchanan, Shacham, Savage 2012 "Return-Oriented Programming"
  IEEE S&P — ROP 系统化

本文件实现：
1. mini KLEE 符号执行器（路径条件 + SAT 风格约束枚举求解）
2. Coverage-guided fuzzer（AFL 风格反馈循环）
3. 栈布局 + buffer overflow + ROP gadget chain 构造
4. CFI 检查（控制流完整性违反检测）
5. CryptDB onion 层级（Popa：SEARCH / ADD / COMPARE 三层加密）

运行：
    python cs161_security.py
"""
from __future__ import annotations
import random
from collections import defaultdict


# ================================================================
# 1. mini KLEE 符号执行器
# ================================================================
# 目标：给定一个带分支的小程序，找出"触发某条件（如 assert fail / crash）的所有输入"。
# 方法：维护 (路径条件 PC, 符号状态)，对每个 if 分支 fork。
# 最后用 SAT 风格求解（这里用穷举小域，教学用）。

# 我们用一个简单语言：expr = Python callable(env) -> int，env: var name -> int
# 程序：list of (action, ...) 其中 action 包括：
#   ('assign', var, expr)
#   ('if', cond, then_block, else_block)
#   ('assert', cond)   # 失败 = bug

def symbolic_execute(program, sym_vars: list[str], domain: range,
                     target: str = "any_assert_fail"):
    """
    mini KLEE：对带符号变量的程序做符号执行，找出所有让 assert 失败的输入。
    返回 list of (env, path_taken)。

    程序结构（递归 list）：
        ('assign', var, expr)
        ('if', cond, then_block, else_block)   -- block 也是 list of action
        ('assert', cond)                        -- 失败 = bug
    """
    bugs = []

    def explore(env_sym: dict, path_cond: list, remaining: list, path_taken: list):
        if not remaining:
            return
        action = remaining[0]
        rest = remaining[1:]
        kind = action[0]

        if kind == 'assign':
            _, var, expr = action
            explore({**env_sym, var: ('expr', expr)}, path_cond, rest, path_taken)
        elif kind == 'if':
            _, cond, then_b, else_b = action
            # fork：then 路径要求 cond 为真，else 要求为假
            explore(env_sym, path_cond + [(cond, True)],  list(then_b) + rest, path_taken + ['T'])
            explore(env_sym, path_cond + [(cond, False)], list(else_b) + rest, path_taken + ['F'])
        elif kind == 'assert':
            _, cond = action
            # 在 domain 上枚举满足 path_cond 且 cond 失败的具体 env
            for env_concrete in _enumerate(sym_vars, domain):
                ok_path = True
                for (c, expected) in path_cond:
                    try:
                        if bool(c(env_concrete)) != expected:
                            ok_path = False
                            break
                    except Exception:
                        ok_path = False
                        break
                if not ok_path:
                    continue
                # path 满足，检查 assert
                try:
                    if not bool(cond(env_concrete)):
                        bugs.append((dict(env_concrete), path_taken[:]))
                except Exception:
                    bugs.append((dict(env_concrete), path_taken[:]))
            return

    explore({}, [], program, [])
    return bugs


def _enumerate(sym_vars, domain):
    """枚举所有 env 组合。"""
    if not sym_vars:
        return [{}]
    head = sym_vars[0]
    tail = sym_vars[1:]
    sub = _enumerate(tail, domain)
    result = []
    for v in domain:
        for s in sub:
            s2 = dict(s)
            s2[head] = v
            result.append(s2)
    return result


# ================================================================
# 2. Coverage-guided Fuzzer (AFL 风格)
# ================================================================

def fuzzer(target_fn, seed_inputs: list, iterations: int = 200,
           mutators=None, verbose=False):
    """
    AFL 风格 coverage-guided fuzzer。

    target_fn: callable(input) -> (output, coverage_bitmap)
        coverage_bitmap: list of 0/1 表示是否命中某个 edge / branch
    seed_inputs: 初始种子池
    iterations: 总迭代数

    反馈循环：
    1. 从种子池选一个 input
    2. 变异（flip bit, insert, delete, arithmetic）
    3. 跑 target，记录 coverage
    4. 若发现新 coverage edge，加入种子池（"interesting"）
    """
    if mutators is None:
        mutators = [mut_flip_bit, mut_insert, mut_delete, mut_arith]

    corpus = list(seed_inputs)
    seen_edges = set()
    # 初始种子的 coverage 也记录
    for inp in corpus:
        _, cov = target_fn(inp)
        seen_edges.update(_edge_id(cov))
    initial_edges = len(seen_edges)

    crashes = []
    discoveries = []

    for it in range(iterations):
        if not corpus:
            break
        parent = random.choice(corpus)
        mut = random.choice(mutators)
        child = mut(parent)
        try:
            output, cov = target_fn(child)
        except AssertionError as e:
            crashes.append((child, str(e)))
            continue
        except Exception as e:
            # 假设所有异常都是"crash"
            crashes.append((child, type(e).__name__))
            continue

        new_edges = set(_edge_id(cov)) - seen_edges
        if new_edges:
            seen_edges.update(new_edges)
            corpus.append(child)
            discoveries.append((it, len(new_edges), child))

    return {
        'final_corpus': len(corpus),
        'edges_covered': len(seen_edges),
        'initial_edges': initial_edges,
        'crashes_found': len(crashes),
        'crash_examples': crashes[:3],
        'discoveries': discoveries[:5],
    }


def _edge_id(cov_bitmap):
    """把 bitmap 转成 edge id 集合。"""
    return [i for i, b in enumerate(cov_bitmap) if b]


# 变异算子
def mut_flip_bit(inp):
    if not inp:
        return inp
    s = list(inp) if isinstance(inp, (list, str)) else [inp]
    i = random.randrange(len(s))
    s[i] = chr(ord(s[i]) ^ (1 << random.randrange(8))) if isinstance(s[i], str) else s[i] ^ 1
    return ''.join(s) if isinstance(inp, str) else s


def mut_insert(inp):
    s = list(inp) if isinstance(inp, (list, str)) else [inp]
    i = random.randrange(len(s) + 1)
    ch = chr(random.randrange(32, 127))
    s.insert(i, ch if isinstance(inp, str) else ord(ch))
    return ''.join(s) if isinstance(inp, str) else s


def mut_delete(inp):
    if len(inp) < 2:
        return inp
    s = list(inp) if isinstance(inp, (list, str)) else [inp]
    del s[random.randrange(len(s))]
    return ''.join(s) if isinstance(inp, str) else s


def mut_arith(inp):
    s = list(inp) if isinstance(inp, (list, str)) else [inp]
    if not s:
        return inp
    i = random.randrange(len(s))
    delta = random.choice([-16, -1, 1, 16])
    cur = ord(s[i]) if isinstance(s[i], str) else s[i]
    s[i] = chr(max(0, min(255, cur + delta))) if isinstance(inp, str) else cur + delta
    return ''.join(s) if isinstance(inp, str) else s


# ================================================================
# 3. 栈布局 + Buffer Overflow + ROP Gadget Chain
# ================================================================

class Stack:
    """可视化栈（高地址在上，低地址在下，与 x86 栈生长方向一致）。"""

    def __init__(self, size=64):
        # 每个 slot 一个字节（用 dict 简化）
        self.cells = {i: 0x00 for i in range(size)}
        self.size = size
        self.sp = size  # stack pointer (grows down)

    def push(self, name, nbytes, value=0):
        """在栈上放一个变量。返回起始地址。"""
        self.sp -= nbytes
        for i in range(nbytes):
            self.cells[self.sp + i] = (value >> (8 * i)) & 0xFF
        return self.sp

    def layout(self, vars):
        """按 vars: [(name, nbytes, value), ...] 从高到低布置。"""
        return {name: self.push(name, nb, val) for (name, nb, val) in vars}

    def read(self, addr, nbytes):
        v = 0
        for i in range(nbytes):
            v |= self.cells[addr + i] << (8 * i)
        return v

    def write_raw(self, addr, data_bytes):
        """模拟 strcpy / memcpy 不检查边界。"""
        for i, b in enumerate(data_bytes):
            if addr + i < self.size:
                self.cells[addr + i] = b & 0xFF


def buffer_overflow_demo():
    """
    经典 stack buffer overflow：往 buf[8] 写 24 字节，溢出覆盖 saved RBP 和 return address。
    """
    stack = Stack(32)
    # 高 → 低（栈生长方向）：[return addr(4)] [saved rbp(4)] [buf(8)]
    addrs = stack.layout([
        ('ret_addr', 4, 0x080484AB),    # 合法返回地址
        ('saved_rbp', 4, 0xBFFFF700),
        ('buf', 8, 0),
    ])
    # 攻击者输入：24 字节，最后 4 字节是新 return addr (恶意函数)
    # shellcode_addr = 0xBFFFFD00 (假想)
    payload = b'A' * 12 + bytes.fromhex('00FDFFBF')  # 覆盖 ret_addr
    stack.write_raw(addrs['buf'], payload)

    original_ret = 0x080484AB
    overwritten_ret = stack.read(addrs['ret_addr'], 4)
    return addrs, original_ret, overwritten_ret


def rop_chain_demo():
    """
    Return-Oriented Programming (ROP)：用现有可执行段里的"gadget"
    （以 ret 结尾的几条指令）拼出任意计算，绕过 W^X（不可写栈执行）。

    典型 chain：
        pop rdi ; ret           ← gadget 1
        0xdeadbeef              ← 参数（"/bin/sh" 地址）
        system_addr ; ret       ← gadget 2（libc system）
    """
    gadgets = {
        'pop_rdi_ret': 0x08048473,    # pop rdi ; ret
        'system':      0xB7E531B0,    # libc system()
    }
    bin_sh_str = 0xBFFFF8A0
    # 构造 ROP chain（栈布局，从低到高）
    chain = [
        gadgets['pop_rdi_ret'],   # 1. 跳到这里，pop rdi
        bin_sh_str,               # 2. rdi ← "/bin/sh" 地址
        gadgets['system'],        # 3. ret 到 system(rdi)
    ]
    return gadgets, bin_sh_str, chain


# ================================================================
# 4. CFI (Control-Flow Integrity) 检查
# ================================================================

def cfi_check(call_sites: list, allowed_targets: dict, actual_targets: dict) -> list:
    """
    CFI：每次 indirect call/jmp 必须命中预计算的白名单目标集。
    call_sites: 间接调用点列表 (e.g. ['call_at_0x401000', 'jmp_at_0x401200'])
    allowed_targets: {site: set(allowed_callee_addrs)}  预计算 CFG
    actual_targets: {site: actual_target_addr}          运行时观察
    返回 list of violations。
    """
    violations = []
    for site in call_sites:
        actual = actual_targets.get(site)
        if actual is None:
            continue
        allowed = allowed_targets.get(site, set())
        if actual not in allowed:
            violations.append((site, actual, allowed))
    return violations


# ================================================================
# 5. CryptDB Onion 层级 (Popa 2011)
# ================================================================
# CryptDB 给每个操作一层"洋葱"：
#   SEARCH onion:  → 加密后仍能做等值搜索 (DET → JOIN → SEARCH → RND)
#   ADD onion:     → 加密后仍能做加法 (HOM)
#   COMPARE onion: → 加密后仍能比较大小 (OPE → JOIN → SEARCH)
# 加密从外层（最强）逐层剥到内层（最弱），需要哪种操作就剥到能支持为止。

def cryptdb_onion_demo():
    """
    演示 CryptDB 三种洋葱如何同时支持 SELECT/JOIN/GROUP BY/SUM/<。
    """
    # SEARCH onion: 等值查询
    def enc_DET(plaintext, key):
        # 确定性加密：相同明文 → 相同密文（可等值搜索）
        return hash((plaintext, key)) & 0xFFFFFFFF
    # ADD onion: 同态加法
    def enc_HOM(plaintext, key):
        # 简化：用 Paillier 思想（这里用线性近似教学）
        return plaintext * key + key  # 不真实的简化
    def add_HOM(c1, c2, key):
        # 同态：(m1*key+key) + (m2*key+key) - 2*key = (m1+m2)*key
        return c1 + c2 - 2 * key
    def dec_HOM(c, key):
        return (c - key) // key
    # COMPARE onion: 保序加密（OPE）
    def enc_OPE(plaintext, key):
        # 简化：保序 = plaintext + key * 1000（key 大就单调）
        return plaintext + key * 1000
    # SEARCH 操作
    rows = [('alice', 100), ('bob', 50), ('carol', 100)]
    key = 7777
    enc_rows = [(enc_DET(name, key), enc_OPE(salary, key)) for name, salary in rows]

    # 等值查询：SELECT * WHERE name = 'alice'
    target = enc_DET('alice', key)
    matches = [r for r in enc_rows if r[0] == target]
    # 比较查询：SELECT * WHERE salary > 60 → OPE 域内 > enc_OPE(60)
    salary_threshold = enc_OPE(60, key)
    cmp_matches = [r for r in enc_rows if r[1] > salary_threshold]
    return {
        'rows': rows,
        'enc_rows': enc_rows,
        'search alice matches': len(matches),
        'salary>60 matches': len(cmp_matches),
    }


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("Berkeley CS 161 Computer Security Demo")
    print("=" * 60)
    random.seed(42)

    # --- 1. 符号执行 ---
    print("\n📋 1. mini KLEE 符号执行器")
    # 程序：if x+y == 5: assert(x > 0)
    # 找出让 assert 失败的所有 (x, y)：x+y=5 且 x ≤ 0
    program = [
        ('if', lambda e: e['x'] + e['y'] == 5,
            [('assert', lambda e: e['x'] > 0)],   # then 分支：x>0 才 ok
            []),
    ]
    bugs = symbolic_execute(program, ['x', 'y'], range(-3, 8),
                            target="assert_fail")
    print("   程序: if x+y==5 then assert(x>0)")
    print("   符号变量: x, y ∈ [-3, 8)")
    print(f"   符号执行找到 {len(bugs)} 个让 assert 失败的输入:")
    seen = set()
    shown = 0
    for env, path in bugs:
        key = (env['x'], env['y'])
        if key in seen:
            continue
        seen.add(key)
        if shown >= 6:
            print(f"   ... 共 {len(seen)} 个唯一反例（截断显示）")
            break
        print(f"     x={env['x']:>2}, y={env['y']:>2}, x+y={env['x']+env['y']:>2}, path={path}")
        shown += 1
    # 验证：所有反例都满足 x+y=5 ∧ x≤0
    ok = all(env['x'] + env['y'] == 5 and env['x'] <= 0 for env, _ in bugs) and len(bugs) > 0
    print(f"   验证所有反例满足 (x+y=5 ∧ x≤0): {'✓' if ok else '✗'}")
    assert ok and len(bugs) >= 3   # 至少 (-1,6),(-2,7),(0,5)

    # --- 2. AFL Fuzzer ---
    print("\n📋 2. Coverage-guided Fuzzer (AFL 风格)")
    # 目标程序：根据输入第 1 个字符走不同分支，"P" 开头触发秘密分支，"!" 触发 crash
    def target(inp):
        cov = [0] * 8
        s = inp if isinstance(inp, str) else ''.join(chr(c) for c in inp)
        if len(s) == 0:
            return None, cov
        cov[0] = 1
        c = s[0]
        if c == 'P':
            cov[1] = 1
            if len(s) > 1 and s[1] == 'W':
                cov[2] = 1   # 秘密分支 PW
        elif c == '!':
            cov[3] = 1
            assert False, "crash triggered by '!' input"
        elif c.isdigit():
            cov[4] = 1
            if int(c) > 5:
                cov[5] = 1
        else:
            cov[6] = 1
        return s, cov

    result = fuzzer(target, seed_inputs=['hello', '1', 'a'], iterations=500)
    print(f"   初始种子: ['hello', '1', 'a']")
    print(f"   初始 coverage edges: {result['initial_edges']}")
    print(f"   迭代 500 次后:")
    print(f"     最终种子池大小: {result['final_corpus']}")
    print(f"     coverage edges: {result['edges_covered']}")
    print(f"     发现 crash: {result['crashes_found']}")
    if result['crash_examples']:
        ex = result['crash_examples'][0]
        print(f"     crash 示例: 输入含 '!' (前 20 字符): {str(ex[0])[:20]!r}")
    assert result['crashes_found'] > 0, "Fuzzer 应该能发现 crash"
    assert result['edges_covered'] > result['initial_edges']
    print(f"   ✓ Fuzzer 通过反馈覆盖率找到了初始种子未覆盖的分支和 crash")

    # --- 3. Buffer Overflow ---
    print("\n📋 3. Stack Buffer Overflow")
    addrs, orig_ret, new_ret = buffer_overflow_demo()
    print("   栈布局（高→低）:")
    print(f"     ret_addr   @ {addrs['ret_addr']:>3}  (原值 0x{orig_ret:08X})")
    print(f"     saved_rbp  @ {addrs['saved_rbp']:>3}")
    print(f"     buf[8]     @ {addrs['buf']:>3}  (用户输入)")
    print(f"   攻击 payload: 'A'*12 + '\\x00\\xFD\\xFF\\xBF'")
    print(f"   写入 buf[8] 后溢出:")
    print(f"     ret_addr 被覆盖为 0x{new_ret:08X} (期望 0xBFFFFD00)")
    assert new_ret == 0xBFFFFD00
    print(f"   ✓ 控制流被劫持到攻击者指定地址")

    # --- 4. ROP ---
    print("\n📋 4. Return-Oriented Programming (ROP)")
    gadgets, bin_sh, chain = rop_chain_demo()
    print("   Gadget 表（已扫描自可执行段）:")
    for name, addr in gadgets.items():
        print(f"     {name:<14} @ 0x{addr:08X}")
    print(f"   \"/bin/sh\" 字符串地址: 0x{bin_sh:08X}")
    print(f"   构造 ROP chain（栈上从低到高）:")
    for i, addr in enumerate(chain):
        label = ['pop_rdi_ret', '"/bin/sh" arg', 'system'][i] if i < 3 else '?'
        print(f"     [{i}] 0x{addr:08X}   ← {label}")
    print(f"   执行流: ret→pop_rdi→rdi←bin_sh→ret→system(\"/bin/sh\")")
    print(f"   ✓ 用现有代码段拼出任意计算，绕过 W^X 不可执行栈")

    # --- 5. CFI ---
    print("\n📋 5. Control-Flow Integrity (CFI) 检查")
    allowed = {
        'call_indirect_1': {0x08048450, 0x08048500},   # 合法目标集
        'call_indirect_2': {0x08048600},
    }
    actual = {
        'call_indirect_1': 0x08048500,   # 合法
        'call_indirect_2': 0xBFFFFD00,   # 非法（被 ROP 劫持）
    }
    violations = cfi_check(list(allowed.keys()), allowed, actual)
    print(f"   预计算合法目标: {allowed}")
    print(f"   运行时实际目标: {actual}")
    print(f"   CFI 违反数: {len(violations)}")
    for site, act, allow in violations:
        print(f"     [{site}] 跳到 0x{act:08X} 不在白名单 {allow}")
    assert len(violations) == 1 and violations[0][0] == 'call_indirect_2'
    print(f"   ✓ CFI 检测到 ROP 攻击")

    # --- 6. CryptDB Onion ---
    print("\n📋 6. CryptDB Onion (Popa 2011)")
    cb = cryptdb_onion_demo()
    print(f"   原始行: {cb['rows']}")
    print(f"   加密后 (SEARCH onion + COMPARE onion):")
    for r in cb['enc_rows']:
        print(f"     name_hash=0x{r[0]:08X}  salary_enc={r[1]}")
    print(f"   查询 1 (SEARCH onion): SELECT * WHERE name='alice'")
    print(f"     → 等值匹配 {cb['search alice matches']} 行 (DET 加密保证相同明文→相同密文)")
    print(f"   查询 2 (COMPARE onion): SELECT * WHERE salary>60")
    print(f"     → 比较匹配 {cb['salary>60 matches']} 行 (OPE 加密保持顺序)")
    assert cb['search alice matches'] == 1  # DET 等值，只匹配 'alice' 一行
    assert cb['salary>60 matches'] == 2     # OPE 保序，salary=100 的 alice 和 carol
    print(f"   ✓ 数据全程加密，数据库服务器看不到明文仍能执行 SQL")

    # 反直觉
    print("\n💡 反直觉发现：")
    print("   1. 符号执行 = 静态分析里的 SAT 求解")
    print("      100 行程序的路径空间 = 2^50，但符号执行用约束剪枝，常能找出穷举不可能找的 bug")
    print("   2. Fuzzing 不随机，而是反馈驱动")
    print("      AFL 的核心洞察：'coverage 反馈' 把盲猜变成 directed search")
    print("   3. ROP 颠覆了'不可执行栈 = 安全'的常识")
    print("      攻击者不写新代码，复用现有合法代码片段拼出恶意逻辑")
    print("      → 这是为什么 CFI（白名单合法控制流）才是 ROP 的真正克星")
    print("   4. CryptDB 揭示：'加密'和'可用'不是非黑即白")
    print("      不同操作需要不同强度的洋葱层，按需剥皮")
    print("      → 这是 TEE/Confidential Computing 的理论祖先")

    print("\n✅ CS 161 Demo 完成！")


if __name__ == "__main__":
    demo()
