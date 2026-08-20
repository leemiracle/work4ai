#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""authorize.py — Scope 子系统 + L 组件：fail-closed 权限门（RL 版）

手册 03 章：authorize_tool_call 是 L 组件核心挂点；fail-closed：无规则 = 拒绝。
RL 场景特化：
  - 环境变更不可见性（pip install 动全局解释器 = 跑别人代码）
  - 结果数据是证据链（rm 结果目录/手编 jsonl = 毁证据）
  - 外发通道（wandb/hf upload）= 数据出域
CLI 自测: python3 hooks/authorize.py
"""
import os
import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

TOOLS = {'read_file', 'grep_tree', 'run_verify', 'write_file',
         'rl_lint', 'rl_test', 'rl_smoke', 'rl_repro',
         'graph_guard', 'graph_conflict', 'patch_queue', 'deep_plan'}

DENY_PATTERNS = [
    (r'\bpip\s+install\b(?![^&|;]*--user)', 'pip install 动全局环境：依赖变更须人工/走 venv（--user 也建议声明）'),
    (r'\bpip\s+uninstall\b', '卸包动共享环境'),
    (r'\bpip\s+install\s+--force', '强制重装覆盖版本'),
    (r'\bpython3?\s+-m\s+pip\b[^&|;]*(install|uninstall)', 'python -m pip 同 pip'),
    (r'\bconda\s+(install|remove|update)\b', 'conda 动全局环境'),
    (r'\bwandb\s+(login|sync|upload)\b', 'wandb 外发实验数据：出域操作须人工'),
    (r'\bhuggingface-cli\s+upload\b|\bhf\s+upload\b', 'HF 上传出域'),
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--)\s*[^ ]*(runs|results|outputs|checkpoints|wandb)',
     '删实验结果目录 = 毁证据链（账本即队列原则）'),
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*|--)', 'rm -f 系列被拦：删除请精确到文件名'),
    (r'\bgit\s+push\s+(-f|--force)', 'force-push 毁历史'),
    (r'\bgit\s+reset\s+--hard', '硬重置吞未提交实验'),
    (r'\bcurl[^|]*\|\s*(ba)?sh', '管道执行远程代码'),
    (r'\b(reboot|shutdown)\b', '宿主机不是你的测试机（尤其跑长训练前）'),
    (r'\bnvidia-smi\s+-r\b|\bcuda-uninstall\b', '动 GPU 驱动/运行时'),
    (r'\bkill(all)?\s+-9?\s*(python|train)', '批量杀训练进程：长跑实验是共享资源，须点名 kill'),
]

# Goodhart 通道（RL 形态）
DENY_PATTERNS += [
    (r'--no-seed\b|--seed\s+-1\b', '显式禁用 seed = 主动放弃可复现性（L4 红线）'),
    (r'TORCH_DETERMINISTIC\s*=\s*0', '关确定性 = 对比实验失效'),
    (r'env\.seed\(\s*None', '环境 seed=None：随机漂移'),
]


def _writable_roots():
    roots = [str(PLUGIN_ROOT / 'state')]
    ws = os.environ.get('RL_PROJECT')
    if ws:
        roots.append(ws)
    return roots


def authorize(tool, args):
    """返回 (ok, why)。fail-closed：未知工具/未知参数键 = 拒。"""
    if tool not in TOOLS:
        return False, f"未知工具 {tool}（fail-closed）"
    known_keys = {
        'path': str, 'offset': int, 'pattern': str, 'glob': str, 'cmd': str,
        'content': str, 'target': str, 'base': str, 'series': str,
        'files': list, 'patch': str, 'question': str, 'action': str,
    }
    for k, v in (args or {}).items():
        if k not in known_keys:
            return False, f"未知参数键 {k}"
        if not isinstance(v, known_keys[k]):
            return False, f"参数 {k} 类型不符（期望 {known_keys[k].__name__}）"
    if tool == 'run_verify' or tool in ('rl_repro',):
        cmd = str(args.get('cmd', ''))
        for pat, why in DENY_PATTERNS:
            if re.search(pat, cmd):
                return False, why
    if tool == 'write_file':
        p = Path(str(args.get('path', '')))
        if not p.is_absolute():
            rp = os.environ.get('RL_PROJECT')
            p = (Path(rp) / p) if rp else (PLUGIN_ROOT / p)
        if not any(str(p.resolve()).startswith(r) for r in _writable_roots()):
            return False, f"写路径越界：{p}（白名单：RL_PROJECT + 插件 state/）"
    return True, ''


def _self_test():
    ok = True
    cases = [
        ('run_verify', {'cmd': 'pip install gymnasium'}, False, 'pip install'),
        ('run_verify', {'cmd': 'python3 -m pip install torch'}, False, 'python -m pip'),
        ('run_verify', {'cmd': 'wandb login'}, False, 'wandb'),
        ('run_verify', {'cmd': 'rm -rf runs/'}, False, '删结果'),
        ('run_verify', {'cmd': 'python3 train.py --seed 42'}, True, '正常训练'),
        ('run_verify', {'cmd': 'python3 train.py --seed -1'}, False, '禁 seed'),
        ('rl_repro', {'cmd': 'python3 eval.py --seed 7'}, True, '复现检查'),
        ('qq', {}, False, '未知工具'),
        ('write_file', {'path': 'state/x.md', 'content': 'x'}, True, '写 state'),
        ('write_file', {'path': '/etc/passwd', 'content': 'x'}, False, '越界写'),
        ('run_verify', {'cmd': 'x', 'evil': 1}, False, '未知参数键'),
    ]
    for tool, args, want, name in cases:
        got = authorize(tool, args)[0]
        mark = '✓' if got == want else '✗'
        ok = ok and (got == want)
        print(f"  [{mark}] {name}: {tool} → {got}（期望 {want}）")
    print("authorize self-test:", "ALL PASS" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(_self_test())
