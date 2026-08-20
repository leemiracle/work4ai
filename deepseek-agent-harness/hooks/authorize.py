#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""authorize.py — Scope 子系统 + L 组件：fail-closed 权限门（Agent 版）

Agent 场景特化：
  - 轨迹是证据链（删轨迹 = 毁审计）
  - 对外 API 费用（滥发邮件/发帖/下单类动作）
  - 权限自我提权（改自己的 authorize 规则 = 自由）
"""
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

TOOLS = {'read_file', 'grep_tree', 'run_verify', 'write_file',
         'agent_lint', 'agent_test', 'agent_smoke', 'agent_eval',
         'graph_guard', 'graph_conflict', 'patch_queue', 'deep_plan'}

DENY_PATTERNS = [
    (r'\bpip\s+install\b', 'pip install 动全局环境：须人工/venv'),
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--)\s*[^ ]*(trace|traj|runs|logs)',
     '删轨迹/日志 = 毁审计证据链'),
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--)', 'rm -f 系列：删除精确到文件名'),
    (r'\bgit\s+push\s+(-f|--force)|git\s+reset\s+--hard', '毁历史/吞工作'),
    (r'\bcurl[^|]*\|\s*(ba)?sh', '管道执行远程代码'),
    (r'\b(reboot|shutdown)\b', '宿主机不是你的测试机'),
    (r'(smtp|sendmail|send_email|sendmail\s)', '对外发信须人工：费用+身份红线'),
    (r'\brequests\.(post|put)\b[^&|;]*(api|webhook)', '对外 API 写操作须声明预算'),
    # 自我提权通道
    (r'hooks/authorize\.py\b', '改 authorize 规则 = 自我提权：须人工 review（本插件自己拦自己）'),
    (r'hooks/authorize\.py', '同上'),
]

# Goodhart 通道（agent 评测形态）
DENY_PATTERNS += [
    (r'agent_eval\.py[^&|;]*--baseline\s*/dev/null', '假基线对比'),
    (r'\-\-skip-checks\b|--no-verify\b', '跳过校验 = Goodhart'),
]


def _writable_roots():
    roots = [str(PLUGIN_ROOT / 'state')]
    ws = os.environ.get('AGENT_PROJECT')
    if ws:
        roots.append(ws)
    return roots


def authorize(tool, args):
    if tool not in TOOLS:
        return False, f"未知工具 {tool}（fail-closed）"
    known_keys = {'path': str, 'offset': int, 'pattern': str, 'glob': str, 'cmd': str,
                  'content': str, 'target': str, 'base': str, 'series': str,
                  'files': list, 'patch': str, 'question': str, 'action': str}
    for k, v in (args or {}).items():
        if k not in known_keys:
            return False, f"未知参数键 {k}"
        if not isinstance(v, known_keys[k]):
            return False, f"参数 {k} 类型不符"
    if tool in ('run_verify', 'agent_eval'):
        cmd = str(args.get('cmd', ''))
        for pat, why in DENY_PATTERNS:
            if re.search(pat, cmd):
                return False, why
    if tool == 'write_file':
        p = Path(str(args.get('path', '')))
        if not p.is_absolute():
            rp = os.environ.get('AGENT_PROJECT')
            p = (Path(rp) / p) if rp else (PLUGIN_ROOT / p)
        # 写 authorize.py 自身 = 提权
        if p.name == 'authorize.py' and 'hooks' in p.parts:
            return False, '写 authorize.py = 自我提权，须人工'
        if not any(str(p.resolve()).startswith(r) for r in _writable_roots()):
            return False, f"写路径越界：{p}"
    return True, ''


def _self_test():
    ok = True
    cases = [
        ('run_verify', {'cmd': 'pip install langchain'}, False, 'pip install'),
        ('run_verify', {'cmd': 'rm -rf traces/'}, False, '删轨迹'),
        ('run_verify', {'cmd': 'python3 tools/agent_trace_check.py t.jsonl'}, True, '正常校验'),
        ('run_verify', {'cmd': 'git push --no-verify'}, False, '跳过校验'),
        ('write_file', {'path': 'hooks/authorize.py', 'content': 'x'}, False, '提权写'),
        ('qq', {}, False, '未知工具'),
    ]
    for tool, args, want, name in cases:
        got = authorize(tool, args)[0]
        mark = '✓' if got == want else '✗'
        ok = ok and (got == want)
        print(f"  [{mark}] {name}: → {got}（期望 {want}）")
    print("authorize self-test:", "ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(_self_test())
