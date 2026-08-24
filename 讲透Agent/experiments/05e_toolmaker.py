"""
实验 05e — L3 补缺: 造工具闭环 (缺 → 写 → 验 → 注 → warm 复用) + 真 MCP 回路
对应: 自进化2.0-整体叠加.md §7 自查表 L3 行 · harness 五子系统的 Verification + Scope 在工具层的落地

闭环五步 (每个任务):
  ① NEED    任务声明需要工具 multiply/sqrt/sort_list
  ② WRITE   工具生成器 ("冻结 LLM" 模板, 真系统=LLM 写代码): 首个生成物故意带边界 bug
  ③ VERIFY  内置测试集 (含边界用例) 实跑 — 不过即弃, 重生成 ("验证即证据"在工具层)
  ④ REGISTER 注册进 registry (进程内 = MCP 动态注册的最小形态)
  ⑤ WARM    同型任务再来说"已注册, 直接用" — 工具复用零成本

安全两闸:
  验证门 — 边界用例 (乘 0 / 负数) 抓住 a*b 之外的静默错 (a==0 时返回 1 的实现能骗过普通用例)
  Scope  — 请求 shell/exec 类工具: 不在允许清单 → 拒绝并优雅降级 (harness 的 Scope 子系统)

Part 2 (彩蛋, 需 mcp 包): 真 MCP 协议回路 — 拉起 [05e_mcp_server.py](./05e_mcp_server.py)
(FastMCP/stdio), 进程内 client initialize → list_tools → call_tool, 验证真协议往返。

实测结论 (2026-08-24, 秒级):
  Part 1 闭环: multiply 首生成物 (a*b if a!=0 else 1) 普通用例全过、边界用例 (0,9) 抓出 →
           验证门拒绝 → 正确版 3/3 通过注册; cold 创建 3 工具 / warm 复用 2 次;
           shell 请求在生成前被 Scope 拒绝 (入口闸先于质量闸)
  Part 2 真协议: fastmcp 3.4.7 server (stdio) 进程内拉起 → ping ✓ → 发现 3 工具 →
           multiply(6,7)=42.0 ✓ → '写好→挂总线→被发现→被调用'全链路走通
  ★ 开发实录: 官方 mcp SDK 新版已移除 mcp.server.fastmcp (ModuleNotFoundError 实证),
    FastMCP 拆为独立包 fastmcp — "最新 API 不凭记忆"铁律的当日活例子

跑法: python3 -u 05e_toolmaker.py
"""
import os

def P(*a): print(*a, flush=True)

# ============================================================
# Part 1: 离线核心 — 造工具闭环 + 验证门 + Scope
# ============================================================
ALLOWLIST = {"multiply", "sqrt", "sort_list"}      # Scope: 只许造这些

# 工具生成器 ("冻结 LLM"): 模板库; multiply 的首个候选故意带边界 bug
TEMPLATES_BUGGY = {
    "multiply": ("def multiply(a, b):\n    return a * b if a != 0 else 1\n", "v0_边界bug版"),
}
TEMPLATES = {
    "multiply": ("def multiply(a, b):\n    return a * b\n", "v1_正确版"),
    "sqrt":     ("def sqrt(x):\n    return x ** 0.5\n", "v1_正确版"),
    "sort_list": ("def sort_list(xs):\n    return sorted(xs)\n", "v1_正确版"),
}
TESTS = {   # 内置测试集: 普通用例 + 边界用例 (验证门的牙齿)
    "multiply": [((6, 7), 42), ((-2, 3), -6), ((0, 9), 0)],
    "sqrt":     [((16,), 4.0), ((0,), 0.0), ((2,), 1.4142135623730951)],
    "sort_list": [(([3, 1, 2],), [1, 2, 3]), (([],), []), (([5, -1],), [-1, 5])],
}

REGISTRY = {}          # name -> (func, 版本, 来源: cold创建 / warm复用)

def validate(code, cases):
    """验证门: 沙箱 exec + 全测试实跑 (含边界). 过=证据, 不过=弃"""
    ns = {}
    try:
        exec(code, {"__builtins__": __builtins__}, ns)   # 演示级隔离; 生产用真沙箱
        fn = ns[next(iter(k for k in ns if callable(ns[k]) and not k.startswith("__")))]
        for args, want in cases:
            got = fn(*args)
            if got != want:
                return None, f"用例 {args}: 期望 {want}, 实得 {got}"
        return fn, None
    except Exception as e:
        return None, f"执行异常: {e}"

def solve_task(name, args):
    """①NEED ②WRITE ③VERIFY ④REGISTER ⑤WARM 的闭环入口"""
    if name not in ALLOWLIST:
        return f"REFUSED(超出允许清单 {sorted(ALLOWLIST)}), 优雅降级: 返回'无此能力'"
    if name in REGISTRY:                                   # ⑤ WARM
        fn, ver, _ = REGISTRY[name]
        REGISTRY[name] = (fn, ver, "warm")
        return f"WARM 命中 {name}({ver}) → {fn(*args)}"
    cands = ([TEMPLATES_BUGGY[name]] if name in TEMPLATES_BUGGY else []) + [TEMPLATES[name]]
    for code, ver in cands:                                # ② WRITE: 先试生成物, 验证不过换重生成
        fn, err = validate(code, TESTS[name])              # ③ VERIFY
        if fn:
            REGISTRY[name] = (fn, ver, "cold")             # ④ REGISTER
            return f"COLD 创建 {name}({ver}) 验证 {len(TESTS[name])}/{len(TESTS[name])} 用例通过 → {fn(*args)}"
        P(f"    [验证门拒绝 {name} {ver}] {err}")
    return "生成失败"

def main():
    P("=" * 74)
    P("Part 1  造工具闭环 (离线核心)")
    tasks = [("multiply", (6, 7)), ("multiply", (3, 9)), ("sqrt", (16,)),
             ("sort_list", ([5, 2, 9],)), ("multiply", (0, 9)), ("shell", ("rm -rf /",))]
    for name, args in tasks:
        P(f"  任务 {name}{str(args):<16} → {solve_task(name, args)}")
    cold = sum(1 for _, v in REGISTRY.items() if v[2] == "cold")
    warm = sum(1 for _, v in REGISTRY.items() if v[2] == "warm")
    P(f"\n  注册表终态: {len(REGISTRY)} 个工具 (工具级来源: cold {cold} / warm {warm}); "
      f"任务级: cold 创建 3 次, warm 复用 2 次, Scope 拒绝 1 次")

    # ========================================================
    # Part 2: 真 MCP 回路 (需 mcp 包; 不可用时优雅跳过)
    # ========================================================
    P("\n" + "=" * 74)
    P("Part 2  真 MCP 协议回路 (fastmcp server + 进程内 client)")
    try:
        import asyncio, warnings
        warnings.filterwarnings("ignore")
        from fastmcp import Client
    except ImportError:
        P("  fastmcp 包不可用 → 跳过 (离线核心已完整演示闭环; pip install fastmcp 后重跑启用)")
        P("  开发实录: 官方 mcp SDK 新版已移除 mcp.server.fastmcp → 必须装独立包 fastmcp (3.4.7 实测)")
        return

    async def mcp_roundtrip():
        here = os.path.dirname(os.path.abspath(__file__))
        async with Client(os.path.join(here, "05e_mcp_server.py")) as client:  # 自动 spawn stdio server
            await client.ping()                                   # 真握手
            tools = await client.list_tools()                     # 真发现
            names = sorted(t.name for t in tools)
            P(f"  ping ✓   list_tools → {names}")
            r1 = await client.call_tool("multiply", {"a": 6, "b": 7})
            v1 = str(getattr(r1, "data", None) or r1.content[0].text)
            P(f"  call_tool multiply(6,7) → {v1} {'✓' if float(v1) == 42 else '✗'}")
            r2 = await client.call_tool("sort_list", {"xs": "5,2,9"})
            v2 = str(getattr(r2, "data", None) or r2.content[0].text)
            P(f"  call_tool sort_list('5,2,9') → {v2}")
            return names, v1
    try:
        names, v1 = asyncio.run(mcp_roundtrip())
        P(f"\n  真 MCP 回路结论: 协议往返成功 — 工具'写好→挂上总线→被发现→被调用'全链路走通")
        P("  注册进常驻 agent (opencode) 的三行配置见 05e_mcp_server.py 文档字符串")
    except Exception as e:
        P(f"  MCP 回路失败: {type(e).__name__}: {str(e)[:200]}")
        P("  → 离线核心 (Part 1) 的闭环演示不受影响")

    P("=" * 74)
    P("反直觉点")
    P("""
- 验证门抓住的是'普通用例骗得过'的实现: a*b 在 (6,7)/(-2,3) 上全对, 只在
  乘 0 时返回 1 — 没有边界用例的验证门是装饰品. 工具自造系统的最小测试集
  必须 = 普通用例 + 该工具的典型失效边界 (与性能优化Agent guard 的'容差分层'
  同思路: 验证强度要按失效模式设计, 不是按行数).

- warm 复用是经济性所在: cold 创建含'生成+验证'两次全测试, warm 只查一次
  字典 — 工具库的价值不在第一次造出来, 在第二次不用再造 (Voyager 技能库/
  skills 市场同构). 反过来, 工具失效时要有退役机制 (动态图综述的 Delete
  重写), 本玩具未演示 — 留作扩展.

- Scope 拒绝的位置很关键: 在'生成之前'而不是'生成之后' — 等工具写好了再
  审, 恶意代码已经在沙箱里跑过验证测试了. 允许清单是入口闸, 验证门是质量
  闸, 两道闸缺一不可, 顺序也不能换.

- 真 MCP 回路的意义: 进程内 registry 是'自家工具自家用', MCP 是'工具挂上
  总线, 任何 agent 都能发现并调用' — 自造工具的价值被协议放大 N 倍,
  这正是 L3 与 MCP 生态 (64k 仓) 的接缝.
""")

if __name__ == "__main__":
    main()
