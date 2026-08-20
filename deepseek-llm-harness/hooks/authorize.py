#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""authorize.py — Scope 子系统 + L 组件：fail-closed 权限门（LLM 版）

LLM 场景特化：
  - 模型/数据文件是重资产（rm 模型目录 = 丢数 GB）
  - 外发通道（hf upload / API 滥发）= 数据/费用出域
  - 评测作弊通道（改评测集/改 judge prompt 对答案）
"""
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

TOOLS = {'read_file', 'grep_tree', 'run_verify', 'write_file',
         'llm_lint', 'llm_test', 'llm_smoke', 'llm_eval',
         'graph_guard', 'graph_conflict', 'patch_queue', 'deep_plan'}

DENY_PATTERNS = [
    (r'\bpip\s+install\b', 'pip install 动全局环境：依赖变更须人工/走 venv'),
    (r'\bpip\s+uninstall\b|\bconda\s+(install|remove)', '动共享环境'),
    (r'\bhuggingface-cli\s+upload\b|\bhf\s+upload\b|\bhub\.upload', '模型/数据出域须人工'),
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--)\s*[^ ]*(models|checkpoints|adapter|data)',
     '删模型/数据/adapter 目录 = 毁重资产'),
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--)', 'rm -f 系列：删除精确到文件名'),
    (r'\bgit\s+push\s+(-f|--force)', 'force-push 毁历史'),
    (r'\bgit\s+reset\s+--hard', '硬重置吞未提交实验'),
    (r'\bcurl[^|]*\|\s*(ba)?sh', '管道执行远程代码'),
    (r'\b(reboot|shutdown)\b', '宿主机不是你的测试机'),
    (r'git\s+add\s+[^&|;]*\.(safetensors|bin|pt|gguf)\b', '模型权重绝不进 git（仓库爆炸+协议风险）'),
    (r'--max_tokens\s+0\b|--n\s+1000', '异常批量调用：费用红线'),
]

# Goodhart 通道（LLM 评测形态）
DENY_PATTERNS += [
    (r'eval\.jsonl?\b[^&|;]*(>>|>|sed|nano|vim)', '手编评测集 = 对答案（评测作弊通道）'),
    (r'judge[_-]prompt[^&|;]*(--set|=)', '改 judge prompt 须单独 review：评测即任务'),
    (r'--skip-eval\b', '跳过评测上线 = Goodhart'),
]


def _writable_roots():
    roots = [str(PLUGIN_ROOT / 'state')]
    ws = os.environ.get('LLM_PROJECT')
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
    if tool in ('run_verify', 'llm_eval'):
        cmd = str(args.get('cmd', ''))
        for pat, why in DENY_PATTERNS:
            if re.search(pat, cmd):
                return False, why
    if tool == 'write_file':
        p = Path(str(args.get('path', '')))
        if not p.is_absolute():
            rp = os.environ.get('LLM_PROJECT')
            p = (Path(rp) / p) if rp else (PLUGIN_ROOT / p)
        if not any(str(p.resolve()).startswith(r) for r in _writable_roots()):
            return False, f"写路径越界：{p}（白名单：LLM_PROJECT + 插件 state/）"
    return True, ''


def _self_test():
    ok = True
    cases = [
        ('run_verify', {'cmd': 'pip install peft'}, False, 'pip install'),
        ('run_verify', {'cmd': 'hf upload .'}, False, 'hf 上传'),
        ('run_verify', {'cmd': 'rm -rf checkpoints/'}, False, '删 ckpt'),
        ('run_verify', {'cmd': 'git add model.safetensors'}, False, '权重进 git'),
        ('run_verify', {'cmd': 'python3 tools/llm_smoke.py'}, True, '正常冒烟'),
        ('qq', {}, False, '未知工具'),
        ('write_file', {'path': 'state/x.md', 'content': 'x'}, True, '写 state'),
        ('write_file', {'path': '/root/x', 'content': 'x'}, False, '越界写'),
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
