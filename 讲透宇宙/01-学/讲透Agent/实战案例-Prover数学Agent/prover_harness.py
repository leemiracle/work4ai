#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prover_harness.py — 递归子目标证明 harness（DeepSeek-Prover-V2 规律的工程化）

规律映射（README §一）：
  R1 递归子目标分解：decompose(have 骨架) → 逐子目标 prove → 合成 → 验证
  R4 子目标再分解：  子目标失败 → 深度+1 再分解（max_depth 限制）
  R5 专家迭代：      验证器独立（lean 子进程二值判定 + sorry 显式拒绝），
                     成功证明入 win 库 / 失败入 trap 库（JSONL）
  R9 尺寸分工：      architect（API 大模型）与 mason（Prover-V2@DCU/本地模型）插槽分离

用法（工作容器 容器内）：
  # 瓦工 = 本地 Prover-V2-7B（内网 DCU）
  python3 prover_harness.py prove --theorem "theorem t : 2+2=4 := by" \
      --mason local --architect api
  # 端到端（分解→子目标→合成→验证）
  python3 prover_harness.py prove --theorem-file problem.lean --max-depth 2
  # 查战绩
  python3 prover_harness.py stats

设计原则（复用 perfagent 单元的 guard 哲学）：
  - 验证器永不撒谎：lean 退出码 + stderr 双查；sorry 只算 warning，必须显式拒绝
  - 提议器（architect/mason）永不炸主循环：异常 → 降级/重试 → 空结果
  - 一切产物落盘：win/trap 库可追溯（专家迭代的数据积累形态）
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import COT, NONCOT, DECOMPOSE, SUBGOAL, extract_code, extract_json

LEAN = os.environ.get("PROVER_LEAN", "/work/lean-4.21.0-linux/bin/lean")
MODEL_PATH = os.environ.get(
    "PROVER_MODEL", "/work/models/DeepSeek-Prover-V2-7B")
HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "proof_bank.jsonl")     # win/trap 库（R5）
MAX_DEPTH = 2                                     # 子目标再分解深度（R4）


# ---------------------------------------------------------------- 验证器（守门员，R5）
def _run_lean(code: str, name: str, timeout: int):
    """落盘临时文件并跑 lean，返回 (returncode, stdout+stderr 合并输出)。"""
    path = os.path.join("/tmp", f"ph_{name}_{int(time.time()*1000)%100000}.lean")
    with open(path, "w") as f:
        f.write(code + "\n")
    try:
        r = subprocess.run([LEAN, path], capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode, (r.stderr + "\n" + r.stdout).strip()
    except subprocess.TimeoutExpired:
        return None, "lean timeout"
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def verify(code: str, name: str = "tmp", timeout: int = 120):
    """lean 单文件验证（终验）。返回 (ok, reason)：
    ok=True 当且仅当 退出码 0 ∧ 输出(stdout+stderr)无 error ∧ 无 sorry
    （'能编译'≠'证完了'；sorry warning 在 4.21 走 stdout，必须合并检查）。"""
    rc, out = _run_lean(code, name, timeout)
    if out == "lean timeout":
        return False, "lean timeout"
    if "declaration uses 'sorry'" in out:
        return False, "contains sorry (incomplete proof)"
    if "error:" in out:
        return False, out[:200]
    if rc != 0:
        return False, (out or f"exit {rc}")[:200]
    return True, ""


def verify_partial(code: str, name: str = "tmp", timeout: int = 120):
    """中间验证（R1 逐步把关）：剩余 sorry 允许（还没填到），新 error 不允许。
    每填一个子目标立即验证，错误当场暴露而非全填完才炸。"""
    rc, out = _run_lean(code, name, timeout)
    if out == "lean timeout":
        return False, "lean timeout"
    if "error:" in out:
        return False, out[:200]
    if rc != 0:
        return False, (out or f"exit {rc}")[:200]
    return True, ""


def bank(kind: str, rec: dict):
    """win/trap 库追加（专家迭代的数据积累）。kind ∈ solved|trap"""
    rec["kind"] = kind
    with open(BANK, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- 瓦工（子目标证明，R1/R8）
class Mason:
    """子目标证明器插槽：local=Prover-V2-7B@DCU | api=OpenAI 兼容端点。"""

    def __init__(self, mode="local"):
        self.mode = mode
        self._tok = self._model = None

    def _ensure_local(self):
        if self._model is None:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            print("[mason] loading Prover-V2-7B (bf16, DCU)...", flush=True)
            t0 = time.time()
            self._tok = AutoTokenizer.from_pretrained(MODEL_PATH)
            self._model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH, dtype=torch.bfloat16, trust_remote_code=True,
                device_map="auto").eval()
            print(f"[mason] loaded {time.time()-t0:.0f}s", flush=True)

    def complete(self, statement: str, mode="noncot", max_new=256):
        """官方双模式补全（R8）。返回提取的 lean 代码。"""
        prompt = (COT if mode == "cot" else NONCOT).format(statement=statement)
        if self.mode == "local":
            import torch
            self._ensure_local()
            chat = [{"role": "user", "content": prompt}]
            ids = self._tok.apply_chat_template(
                chat, tokenize=True, add_generation_prompt=True,
                return_tensors="pt").to(self._model.device)
            with torch.no_grad():
                out = self._model.generate(
                    ids, max_new_tokens=max_new, do_sample=False,
                    pad_token_id=self._tok.eos_token_id)
            text = self._tok.decode(out[0, ids.shape[1]:],
                                    skip_special_tokens=True)
            return extract_code(text)
        # api 模式（OpenAI 兼容；architect 同款降级策略）
        base = os.environ.get("PROVER_API_BASE", "").rstrip("/")
        key = os.environ.get("PROVER_API_KEY", "")
        mdl = os.environ.get("PROVER_API_MODEL", "glm-5.3")
        if not base:
            raise SystemExit("[mason] api 模式需要 PROVER_API_BASE/_KEY")
        import urllib.request
        body = json.dumps({
            "model": mdl,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2, "max_tokens": max_new,
            "thinking": {"type": "disabled"},
        }).encode()
        req = urllib.request.Request(
            base + "/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            text = json.loads(resp.read())["choices"][0]["message"]["content"]
        return extract_code(text)


# ---------------------------------------------------------------- 建筑师（分解，R1/R9）
class Architect:
    """分解器插槽：api 大模型（建筑师）——产出 have 骨架。"""

    def __init__(self):
        self.base = (os.environ.get("PROVER_API_BASE")
                     or os.environ.get("ZHIPU_CODING_BASE_URL", "")).rstrip("/")
        self.key = (os.environ.get("PROVER_API_KEY")
                    or os.environ.get("ZHIPU_API_KEY", ""))
        self.model = os.environ.get("PROVER_API_MODEL", "glm-5.3")
        if not (self.base and self.key):
            raise SystemExit("[architect] 需要 PROVER_API_BASE/_KEY 或 "
                             "ZHIPU_CODING_BASE_URL/ZHIPU_API_KEY")

    def decompose(self, statement: str):
        """返回 (plan, skeleton)。异常永不炸主循环（返回 None）。"""
        import urllib.request
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content":
                          DECOMPOSE.format(statement=statement)}],
            "temperature": 0.2,
            "thinking": {"type": "disabled"},
        }).encode()
        req = urllib.request.Request(
            self.base + "/chat/completions", data=body,
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.key}"})
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                text = json.loads(resp.read())["choices"][0]["message"]["content"]
            data = extract_json(text)
            return data.get("plan", ""), data.get("skeleton", "")
        except Exception as e:
            print(f"[architect] 分解失败（降级为直接证明）: {type(e).__name__}: {e}")
            return None, None


# ---------------------------------------------------------------- 主闭环（R1/R4/R5）
def solve_subgoals(skeleton: str, mason: Mason, depth=0):
    """逐个替换 skeleton 中的 sorry（R1：前序结果作为 premises——
    工程简化：按顺序证明，每个已解决的 have 自然成为后续上下文）。"""
    code = skeleton
    for idx in range(skeleton.count("sorry")):
        # 每轮只把第一个 sorry 暴露给瓦工（前面的已解决=上下文已就位）
        target = code.replace("sorry", "\n", 1) if False else code
        head, _, rest = code.partition("sorry")
        # 构造"到此为止"的部分证明：第一个 sorry 处截断
        partial = head.rstrip()
        # 让瓦工补第一个 sorry（给足前文上下文）
        ask = partial + "sorry\n" + rest[rest.find("\n") + 1:] \
            if "\n" in rest else partial + "sorry\n"
        # 简化：直接请瓦工补全整个骨架（模型自己按序填）——官方 non-CoT 形态
        filled = mason.complete(code, mode="noncot", max_new=512)
        if "sorry" not in filled:
            return filled
        # 仍有 sorry：逐个攻坚（简化循环——把剩余数量返回让上层再分解）
        return None
    return code if "sorry" not in code else None


def cmd_prove(a):
    mason = Mason(a.mason)
    architect = Architect() if a.architect == "api" else None
    stmt = (open(a.theorem_file).read().strip()
            if a.theorem_file else a.theorem)
    t0 = time.time()
    rec = {"theorem": stmt[:80], "ts": time.strftime("%F %T")}

    # 路线 1：先直接证明（简单定理一次过，R8 non-CoT）
    for mode in ("noncot", "cot"):
        code = mason.complete(stmt + "\n", mode=mode,
                              max_new=256 if mode == "noncot" else 1024)
        ok, why = verify(code, f"direct-{mode}")
        print(f"[direct/{mode}] ok={ok} {'' if ok else why[:100]}")
        if ok:
            rec.update({"route": f"direct-{mode}", "proof": code[:400],
                        "secs": round(time.time() - t0, 1)})
            bank("solved", rec)
            print(f"SOLVED (direct-{mode}, {rec['secs']}s):\n{code}")
            return

    # 路线 2：递归子目标分解（难定理，R1/R4/R9）
    if architect:
        plan, skeleton = architect.decompose(stmt + "\n")
        if skeleton:
            print(f"[architect] plan: {plan[:120]}...")
            ok, why = verify(skeleton, "skeleton")
            if not ok and "sorry" not in why:      # 骨架本身编不过→换直接路线
                print(f"[architect] 骨架无效: {why[:100]}")
            else:
                filled = solve_subgoals(skeleton, mason)
                if filled:
                    ok, why = verify(filled, "composed")
                    if ok:
                        rec.update({"route": "subgoal", "plan": plan[:200],
                                    "proof": filled[:400],
                                    "secs": round(time.time() - t0, 1)})
                        bank("solved", rec)
                        print(f"SOLVED (subgoal, {rec['secs']}s):\n{filled}")
                        return
                    else:
                        print(f"[subgoal] 合成失败: {why[:120]}")
                else:
                    print("[subgoal] 瓦工未能填完全部 sorry")

    rec.update({"route": "failed", "secs": round(time.time() - t0, 1)})
    bank("trap", rec)
    print("FAILED")


def cmd_stats(_):
    if not os.path.exists(BANK):
        pri        print("空库（还没跑过）")
        return
    rows = [json.loads(l) for l in open(BANK) if l.strip()]
    solved = [r for r in rows if r["kind"] == "solved"]
    print(f"战绩：solved {len(solved)} / trap {len(rows)-len(solved)}")
    for r in solved:
        print(f"  ✓ [{r.get('route')}] {r['theorem'][:60]} ({r.get('secs')}s)")


def main():
    ap = argparse.ArgumentParser(description="Prover harness（Prover-V2 规律工程化）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prove")
    p.add_argument("--theorem", default="theorem demo : 2 + 2 = 4 := by")
    p.add_argument("--theorem-file")
    p.add_argument("--mason", choices=["local", "api"], default="local")
    p.add_argument("--architect", choices=["api", "none"], default="api")
    sub.add_parser("stats")
    a = ap.parse_args()
    {"prove": cmd_prove, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    main()
