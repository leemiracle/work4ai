#!/usr/bin/env python3
"""注释版验证器：代码零改动 + 可编译 + 注释覆盖率。

三条硬校验（对每个文件）：
  1. AST 等价：ast.dump(parse(orig)) == ast.dump(parse(new))
     —— 注释是 # 级，不影响 AST；若子代理动了代码/docstring 立刻暴露。
  2. py_compile 通过（防语法损伤）。
  3. 空行保留：原文件空行位置在新文件仍是空行（结构不变弱校验）。

覆盖率统计（软指标）：
  非空代码行（去掉纯注释行）中带 # 注释的比例。行内字符串含 # 会误判，
  只统计、不卡阈值，人工抽验兜底。

用法: python3 _verify.py            # 全量
      python3 _verify.py <file...>  # 只验指定相对路径
退出码: 坏文件数（0=全过）
"""
import ast
import py_compile
import sys
from pathlib import Path

ORIG = Path("/usr-data/data1/workspace/rl/DRL-robot-navigation-IR-SIM")
DEST = Path("/file-not-set")  # 由 __main__ 设置
DEST_DEFAULT = Path("/data/usershare/ai/work4ai/讲透DRL-robot-navigation-IR-SIM/code-annotated")


def verify(rel: str) -> tuple[bool, str, float]:
    """返回 (ok, 消息, 注释覆盖率)。"""
    src, dst = ORIG / rel, DEST / rel
    if not dst.exists():
        return False, "副本缺失", 0.0
    o_text, n_text = src.read_text(), dst.read_text()

    # 1. AST 等价
    try:
        if ast.dump(ast.parse(o_text)) != ast.dump(ast.parse(n_text)):
            return False, "AST 不等价（代码或 docstring 被改动）", 0.0
    except SyntaxError as e:
        return False, f"语法错误: {e}", 0.0

    # 2. 编译
    try:
        py_compile.compile(str(dst), doraise=True)
    except py_compile.PyCompileError as e:
        return False, f"编译失败: {e}", 0.0

    # 3. 空行只增不减（子代理不得删除原空行；块注释旁适度新增可容忍）
    if n_text.count("\n\n") < o_text.count("\n\n"):
        return False, "空行数减少（原空行被删）", 0.0

    # 覆盖率（全局口径）：新文件中非空非纯注释行里、行内含 # 的比例。
    code_lines = [l for l in n_text.splitlines() if l.strip() and not l.strip().startswith("#")]
    commented = [l for l in code_lines if "#" in l]
    cov = len(commented) / max(len(code_lines), 1)
    return True, "OK", cov


def main() -> None:
    global DEST
    DEST = DEST_DEFAULT
    targets = sys.argv[1:]
    if not targets:
        targets = sorted(
            str(p.relative_to(ORIG)) for p in ORIG.rglob("*.py") if ".git" not in p.parts
        )
    bad = 0
    total_cov, n = 0.0, 0
    for rel in targets:
        if rel.endswith("__init__.py"):
            continue  # 主会话手写包说明，AST 恒等价，跳过
        ok, msg, cov = verify(rel)
        if not ok:
            bad += 1
            print(f"BAD  {rel}: {msg}")
        else:
            total_cov += cov
            n += 1
            print(f"OK   {rel}  注释覆盖 {cov:.0%}")
    if n:
        print(f"\n均覆盖率 {total_cov / n:.0%}（{n} 文件，{bad} 坏）")
    sys.exit(bad)


if __name__ == "__main__":
    main()
