#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""perfagent.campaign — 全链路战役编排器（主入口）。

用法（按序）：
  python3 campaign.py profile                                  # 基线+探针+画像卡
  python3 campaign.py search --proposer grid --budget 8        # E2 对照组
  python3 campaign.py search --proposer heuristic --budget 4   # E2 实验组
  python3 campaign.py search --proposer fullgrid --budget 24   # E3 双 knob
  python3 campaign.py search --proposer llm --budget 4         # E2（需端点；否则 mockllm）
  python3 campaign.py redteam                                  # E1 作弊 vs guard
  python3 campaign.py report                                   # 汇总 campaign_report.md

阶段模型 = profile（感知+诊断）→ search（决策+执行+裁判+记忆）→ report（评估）。
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import memory
from actions import child_cmd, child_env, validate
from diagnose import build_card
from guard import judge, SUSPICIOUS
from proposers import make
from sensors import topology, perf_stat_cmd
from workloads import SPECS

RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runner.py")
TIMEOUT = 300


# ---------------------------------------------------------------- 测量原语
def measure(w, cfg, perturb=1):
    spec = SPECS[w]
    args = [w, str(spec["samples"]), str(spec["inner"]),
            cfg.get("impl", "ref"), str(perturb)]
    cmd = child_cmd(cfg, RUNNER, args)
    env = child_env(cfg)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           env=env, timeout=TIMEOUT)
        if r.returncode != 0:
            return {"error": (r.stderr or r.stdout or "unknown")[-300:]}
        return json.loads(r.stdout.strip().splitlines()[-1])
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {"error": str(e)}


# ---------------------------------------------------------------- qwen 常驻 server
class ResidentServer:
    """Qwen 常驻进程管理：spawn → setup(threads) → forward。换 threads 需重启
    （torch 线程池在模型加载后不可变）。掉线/超时自动降级：返回 error 行。"""

    def __init__(self):
        self.proc = None
        self.threads = None

    def _send(self, obj, timeout=120):
        try:
            self.proc.stdin.write(json.dumps(obj) + "\n")
            self.proc.stdin.flush()
            import selectors
            sel = selectors.DefaultSelector()
            sel.register(self.proc.stdout, selectors.EVENT_READ)
            if not sel.select(timeout):
                return {"ok": False, "error": "server timeout"}
            line = self.proc.stdout.readline()
            return json.loads(line) if line else {"ok": False, "error": "server died"}
        except (BrokenPipeError, json.JSONDecodeError) as e:
            return {"ok": False, "error": str(e)}

    def ensure(self, threads):
        if self.proc and self.proc.poll() is None and self.threads == threads:
            return {"ok": True}
        self.close()
        env = dict(os.environ)
        for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                  "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            env.pop(k, None)
        self.proc = subprocess.Popen(
            [os.environ.get("PERFAGENT_PY", "python3"),
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "resident.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env)
        r = self._send({"op": "setup", "threads": threads}, timeout=300)
        if r.get("ok"):
            self.threads = threads
        return r

    def forward(self, ids, mask, reps):
        return self._send({"op": "forward", "input_ids": ids,
                           "attention_mask": mask, "reps": reps})

    def close(self):
        if self.proc and self.proc.poll() is None:
            try:
                self._send({"op": "quit"}, timeout=10)
                self.proc.wait(timeout=10)
            except Exception:
                self.proc.kill()
        self.proc, self.threads = None, None


_QWEN = {}   # 输入缓存（确定性生成一次，跨配置复用——同 bert 的钉种子语义）


def qwen_inputs(seq, batch):
    import numpy as np
    if "ids" not in _QWEN:
        rng = np.random.default_rng(20260824)
        v = 151936            # Qwen2.5 vocab
        _QWEN["ids"] = rng.integers(0, v, (batch, seq)).tolist()
        _QWEN["mask"] = np.ones((batch, seq), dtype=int).tolist()
    return _QWEN["ids"], _QWEN["mask"]


def measure_qwen(cfg, spec, server, reps=8):
    """qwen 负载专用测量：server.ensure(threads) → forward。
    正确性语义：fp 与首个 baseline 的 fp 比对（campaign 内做，同 guard rel=1e-4）。"""
    t = cfg.get("threads", 1)
    r = server.ensure(t)
    if not r.get("ok"):
        return {"error": f"server setup: {r.get('error')}"}
    ids, mask = qwen_inputs(spec["seq"], spec["batch"])
    return server.forward(ids, mask, reps)


def rebaseline(w, n=3, perturb=1):
    """v2 re-baseline：n 次独立子进程测量取中位——消跨 run 漂移（05§四方差课的解法）。
    fps 取首次（指纹确定性，取哪次都一样）；median 取中位。"""
    meds = []
    first = None
    for _ in range(n):
        r = measure(w, {}, perturb)
        assert "median_ms" in r, f"re-baseline failed for {w}: {r}"
        meds.append(r["median_ms"])
        first = first or r
    out = dict(first)
    out["median_ms"] = statistics.median(meds)
    out["rebaseline_ms"] = [round(m, 3) for m in meds]
    return out


def measure_or_die(w, cfg, perturb=1):
    res = measure(w, cfg, perturb)
    assert "median_ms" in res, f"baseline measure failed for {w}: {res}"
    return res


# ---------------------------------------------------------------- 阶段 1：profile
def cmd_profile():
    topo = topology()
    data = {"env": {"date": time.strftime("%F %T"),
                    "arch": os.uname().machine,
                    "topology": topo},
            "workloads": {}}
    print(f"[profile] topo={topo}")
    for w, spec in SPECS.items():
        if spec["kind"] == "qwen":                 # qwen：常驻 server 画像
            server = ResidentServer()
            try:
                base_r = measure_qwen({"threads": topo["nproc"]}, spec, server)
                assert base_r.get("ok"), base_r
                probe = {}
                for t in (1, 2, 4):
                    r = measure_qwen({"threads": t}, spec, server)
                    if r.get("ok"):
                        probe[t] = r["median_ms"]
                card = build_card(w, spec, base_r["median_ms"], probe)
                data["workloads"][w] = {
                    "baseline": {"median_ms": base_r["median_ms"],
                                 "fps": {"101": base_r["fp"]}},
                    "card": card}
                memory.save_cards(data)
                print(f"[profile] {w}: base={base_r['median_ms']:.1f}ms "
                      f"class={card['scaling_class']} probe={card['probe_ms']}")
            finally:
                server.close()
            continue
        base = measure_or_die(w, {})
        threads_list = sorted({t for t in (1, 2, 4, topo["physical_cores"])
                               if t <= topo["nproc"]})
        probe = {}
        for t in threads_list:
            res = measure(w, {"threads": t})
            if "median_ms" in res:
                probe[t] = res["median_ms"]
        ipc = None
        if spec.get("flops", 0) > 1e9:      # 只对重负载做粗粒度 IPC 遥测
            env = child_env({"threads": threads_list[-1]})
            got = perf_stat_cmd(child_cmd({"threads": threads_list[-1]},
                                          RUNNER,
                                          [w, "3", str(spec["inner"]), "ref", "1"]), env)
            ipc = (got or {}).get("ipc")
        card = build_card(w, spec, base["median_ms"], probe, ipc)
        data["workloads"][w] = {"baseline": base, "card": card}
        memory.save_cards(data)
        print(f"[profile] {w}: base={base['median_ms']:.3f}ms "
              f"class={card['scaling_class']} probe={card['probe_ms']} ipc={ipc}")
    print(f"[profile] 画像卡 → {memory.CARDS}")


def _search_qwen(w, proposer_name, budget, fresh, server):
    """qwen 负载搜索：换 threads = 重启常驻 server（torch 线程池加载后不可变）。
    keep 需双测两次独立命中（同 v3 协议）；fp 对照 profile baseline（rel=1e-4）。"""
    data = memory.load_cards()
    wd = data["workloads"][w]
    base, card = wd["baseline"], wd["card"]
    spec = SPECS[w]
    seen = set() if fresh else memory.seen_keys(w)
    traps = memory.traps_for(w)
    proposer = make(proposer_name, data["env"]["topology"])
    cands, used = [], set()
    for cfg in proposer.propose(card, traps, budget):
        key = memory.cfg_key(cfg)
        if key not in seen and key not in used:
            cands.append(cfg)
            used.add(key)
    print(f"[search:{proposer_name}] {w}: baseline={base['median_ms']:.1f}ms "
          f"{len(cands)} 个候选 (class={card['scaling_class']})")
    from workloads import fp_close
    base_fp = base["fps"]["101"]

    def once(cfg):
        r = measure_qwen(cfg, spec, server)
        if not r.get("ok"):
            return {"verdict": "measure_error",
                    "error": r.get("error", "?")}
        if not r.get("det_ok"):
            return {"verdict": "invalid", "why": "non-deterministic output"}
        if not fp_close(r["fp"], base_fp, 1e-4):
            return {"verdict": "invalid",
                    "why": "fingerprint mismatch (wrong output/cheat)"}
        sp = base["median_ms"] / r["median_ms"]
        return {"verdict": "keep" if sp >= 1.05 else "revert",
                "median_ms": r["median_ms"], "speedup": round(sp, 3),
                "flag": "SUSPICIOUS" if sp > 5 else ""}

    for cfg in cands[:budget]:
        ts = time.strftime("%F %T")
        ok, why = validate(cfg)
        if not ok:
            print(f"  [REJECT] {cfg} — {why}")
            memory.append_row({"ts": ts, "workload": w, "proposer": proposer_name,
                               "cfg": cfg, "verdict": "REJECT", "why": why})
            continue
        j1, j2 = once(cfg), once(cfg)
        if j1["verdict"] == "keep" and j2["verdict"] == "keep":
            verdict = "keep"
            med = (j1["median_ms"] + j2["median_ms"]) / 2
            sp = round(base["median_ms"] / med, 3)
            pair = [round(j1["median_ms"], 1), round(j2["median_ms"], 1)]
            flag = j1.get("flag") or j2.get("flag")
        else:
            j = next((x for x in (j1, j2) if x["verdict"] != "keep"), j1)
            verdict = j["verdict"]
            med, sp, pair, flag = j.get("median_ms"), j.get("speedup"), None, ""
        memory.append_row({"ts": ts, "workload": w, "proposer": proposer_name,
                           "cfg": cfg, "verdict": verdict, "speedup": sp,
                           "median_ms": med, "median_ms_pair": pair,
                           "flag": flag, "why": j1.get("why", "") if verdict != "keep" else "",
                           "error": j1.get("error", "") if verdict == "measure_error" else ""})
        print(f"  [{verdict.upper():13s}] {cfg} {med if med else -1:.1f}ms "
              f"pair={pair} speedup={sp}" + (f" ⚠{flag}" if flag else "")
              + (f" ({j1.get('why') or j1.get('error', '')[:50]})"
                 if verdict != "keep" else ""))


# ---------------------------------------------------------------- 阶段 2：search
def cmd_search(proposer_name, budget, fresh=False, rebase=3):
    data = memory.load_cards()
    assert data, "先跑 campaign.py profile"
    topo = data["env"]["topology"]
    proposer = make(proposer_name, topo)
    server = ResidentServer()          # qwen 负载用（惰性启动，非 qwen 不 spawn）
    try:
        for w, wd in data["workloads"].items():
            if SPECS[w]["kind"] == "qwen":
                _search_qwen(w, proposer_name, budget, fresh, server)
                continue
            base = rebaseline(w, rebase) if rebase > 1 else measure_or_die(w, {})
            card = wd["card"]
            seen = set() if fresh else memory.seen_keys(w)   # fresh=A/B 隔离；默认全局去重(warm-start)
            print(f"[search:{proposer_name}] {w}: baseline={base['median_ms']:.3f}ms "
                  f"(rebase{rebase}: {base.get('rebaseline_ms', ['-'][-1])})")
            traps = memory.traps_for(w)
            cands, used = [], set()
            for cfg in proposer.propose(card, traps, budget):
                key = memory.cfg_key(cfg)
                if key not in seen and key not in used:
                    cands.append(cfg)
                    used.add(key)
            cands = cands[:budget]
            print(f"[search:{proposer_name}] {w}: {len(cands)} 个候选 "
                  f"(class={card['scaling_class']})")
            for cfg in cands:
                ts = time.strftime("%F %T")
                ok, why = validate(cfg)
                if not ok:
                    print(f"  [REJECT] {cfg} — {why}")
                    memory.append_row({"ts": ts, "workload": w, "proposer": proposer_name,
                                       "cfg": cfg, "verdict": "REJECT", "why": why})
                    continue
                # v3 双测协议：两次独立子进程测量各取中位再平均；
                # keep 需两次独立命中（任一次 revert/invalid → 记 revert*）
                res1 = measure(w, cfg)
                j1 = judge(res1, base)
                res2 = measure(w, cfg)
                j2 = judge(res2, base)
                if j1["verdict"] == "keep" and j2["verdict"] == "keep":
                    merged = dict(j1)
                    merged["median_ms"] = (j1["median_ms"] + j2["median_ms"]) / 2
                    merged["median_ms_pair"] = [round(j1["median_ms"], 3),
                                                round(j2["median_ms"], 3)]
                    merged["speedup"] = round(base["median_ms"] / merged["median_ms"], 3)
                    verdict = "keep"
                elif "invalid" in (j1["verdict"], j2["verdict"]):
                    merged = next(j for j in (j1, j2) if j["verdict"] == "invalid")
                    verdict = "invalid"
                elif "measure_error" in (j1["verdict"], j2["verdict"]):
                    merged = next(j for j in (j1, j2)
                                  if j["verdict"] == "measure_error")
                    verdict = "measure_error"
                else:
                    merged = dict(j1)
                    merged["median_ms"] = (j1.get("median_ms", 0)
                                           + j2.get("median_ms", 0)) / 2 or None
                    verdict = "revert"          # 至少一次没赢 → 不确认（保守）
                row = {"ts": ts, "workload": w, "proposer": proposer_name, "cfg": cfg,
                       "verdict": verdict,
                       "speedup": merged.get("speedup"),
                       "median_ms": merged.get("median_ms"),
                       "median_ms_pair": merged.get("median_ms_pair"),
                       "flag": merged.get("flag", ""), "why": merged.get("why", ""),
                       "error": merged.get("error", "")}
                memory.append_row(row)
                msg = (f"  [{verdict.upper():13s}] {cfg} "
                       f"{merged.get('median_ms') or -1:.3f}ms "
                       f"pair={merged.get('median_ms_pair')} "
                       f"speedup={merged.get('speedup', '')}"
                       + (f" ⚠{merged['flag']}" if merged.get("flag") else "")
                       + (f" ({merged.get('why') or merged.get('error', '')[:60]})"
                          if merged.get("why") or merged.get("error") else ""))
                print(msg)
    finally:
        server.close()          # qwen 常驻进程随战役结束退出


# ---------------------------------------------------------------- 阶段 2b：redteam（E1/E4）
def cmd_redteam():
    """E4 军备竞赛矩阵（v2 修正版）：{cheat_content, cheat_ptr} × {perturb 0,1,2}。
    v1 设计失误（元教训）：cheat 用 threads=4 而 baseline 用默认 8 线程——
    speedup 混淆了配置收益与作弊收益。v2 每格加同配置 ref 对照：
      纯作弊收益 = ref_ms / cheat_ms（同 threads、同 perturb）
    负载 matmul-512，threads=4（该负载实测最优区）。"""
    w = "matmul-512"
    lines = ["# E4 红队矩阵 v2：作弊实现 × 防御档位（含同配置 ref 对照）", "",
             "| 作弊 \\ 防御 | 0 无防御 | 1 内容扰动 | 2 对象轮换 |",
             "|---|---|---|---|"]
    for impl, label in (("cheat_content", "内容键"), ("cheat_ptr", "指针键")):
        cells = []
        for perturb in (0, 1, 2):
            base = rebaseline(w, 3, perturb)
            t = 4
            ok, why = validate({"threads": t, "impl": impl},
                               allowed_impls=("ref", "cheat_content", "cheat_ptr"))
            assert ok, why
            cheat_cfg = {"threads": t, "impl": impl}
            ref_cfg = {"threads": t}
            ref = measure(w, ref_cfg, perturb)
            res = measure(w, cheat_cfg, perturb)
            judged = judge(res, base)
            pure = (ref.get("median_ms") / res["median_ms"]
                    if "median_ms" in res and "median_ms" in ref else None)
            cells.append(f"vs-ref {round(pure, 1)}x ({judged['verdict']})" if pure
                         else f"? ({judged['verdict']})")
            memory.append_row({
                "ts": time.strftime("%F %T"), "workload": w,
                "proposer": f"redteam-{impl}", "cfg": cheat_cfg,
                "verdict": judged["verdict"],
                "speedup": judged.get("speedup"),
                "median_ms": judged.get("median_ms"),
                "flag": judged.get("flag", ""),
                "why": (judged.get("why", "") or "") +
                       f" [perturb={perturb} pure_vs_ref="
                       f"{round(pure, 2) if pure else '?'}]", "error": ""})
        lines.append(f"| {label} ({impl}) | " + " | ".join(cells) + " |")
    lines += ["",
              "读法：vs-ref≈1× = 作弊无效（被迫真算）；vs-ref>>1× = 作弊存活。",
              "- 预期：内容键被防御 1/2 双杀；指针键在防御 1 存活、被防御 2 击落",
              "- 混淆警示（v1 元教训）：对 baseline 的 speedup 含配置收益，",
              "  红队对照必须同配置——『裁判的对照组和实验组一样需要设计』"]
    out = os.path.join(memory.STATE, "redteam_report.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[redteam] → {out}")


# ---------------------------------------------------------------- 阶段 3：report
def _fmt_cfg(cfg):
    s = f"threads={cfg.get('threads')}"
    if cfg.get("affinity"):
        s += f",aff={cfg['affinity']}"
    if cfg.get("impl", "ref") != "ref":
        s += f",impl={cfg['impl']}"
    return s


def cmd_report():
    rows = [r for r in memory.load_rows() if r.get("verdict") != "REJECT"]
    # 红队行（impl≠ref）不进主榜单（DQ 语义），只留在效率表与反作弊统计
    rankable = [r for r in rows if r.get("cfg", {}).get("impl", "ref") == "ref"]
    data = memory.load_cards() or {}
    cards = {w: wd["card"] for w, wd in data.get("workloads", {}).items()}
    lines = ["# perfagent campaign 报告", "",
             f"生成：{time.strftime('%F %T')} · 环境：{data.get('env', {})}", ""]
    # 1) 每负载最优
    lines += ["## 每负载最优配置（keep 中最快；红队 impl 行已 DQ）", "",
              "| 负载 | 画像 | baseline ms | 最优 cfg | ms | speedup | 提议器 |",
              "|---|---|---|---|---|---|---|"]
    best_by_w = {}
    for w in SPECS:
        keeps = [r for r in rankable if r["workload"] == w and r["verdict"] == "keep"]
        if not keeps:
            continue
        best = min(keeps, key=lambda r: r["median_ms"])
        best_by_w[w] = best
        card = cards.get(w, {})
        lines.append(
            f"| {w} | {card.get('scaling_class', '?')} | "
            f"{round(card.get('baseline_ms', 0), 3)} | {_fmt_cfg(best['cfg'])} | "
            f"{round(best['median_ms'], 3)} | {round(best['speedup'], 2)}× | "
            f"{best['proposer']} |")
    # 2) 提议器样本效率（E2/E3）
    lines += ["", "## 提议器样本效率（E2/E3）", "",
              "| 提议器 | 负载 | 评估次数 | 最优 speedup | 达到最优所用次数 |",
              "|---|---|---|---|---|"]
    for prop in sorted({r["proposer"] for r in rows if r.get("proposer")}):
        for w in SPECS:
            sub = [r for r in rows if r["proposer"] == prop and r["workload"] == w]
            if not sub:
                continue
            best = max(sub, key=lambda r: r.get("speedup") or 0)
            idx = next(i for i, r in enumerate(sub, 1)
                       if (r.get("speedup") or 0) >= 0.95 * (best.get("speedup") or 0))
            lines.append(f"| {prop} | {w} | {len(sub)} | "
                         f"{round(best.get('speedup') or 0, 2)}× | {idx} |")
    # 3) 全局 compromise（maximin）
    lines += ["", "## 全局配置 vs 按负载分派", ""]
    by_cfg = {}
    for r in rows:
        if r["workload"] in SPECS and r.get("speedup") and r["verdict"] == "keep" \
           and not r["cfg"].get("affinity") and r["cfg"].get("impl", "ref") == "ref":
            by_cfg.setdefault(memory.cfg_key(r["cfg"]), {})[r["workload"]] = r
    full = {k: v for k, v in by_cfg.items() if len(v) == len(SPECS)}
    if full:
        best_key, best_min = None, -1
        for k, v in full.items():
            mn = min(x["speedup"] for x in v.values())
            if mn > best_min:
                best_key, best_min = k, mn
        cfg = json.loads(best_key)
        per = full[best_key]
        lines.append(f"- maximin 单一配置：{_fmt_cfg(cfg)}，最差负载 speedup="
                     f"{round(best_min, 2)}×（各负载："
                     + ", ".join(f"{w}={round(x['speedup'], 2)}×"
                                 for w, x in sorted(per.items())) + "）")
    lines.append("- 按负载分派（dispatch）："
                 + "; ".join(f"{w}→{_fmt_cfg(b['cfg'])}({round(b['speedup'], 2)}×)"
                             for w, b in sorted(best_by_w.items()))
                 + "  ← 各负载各自最优")
    lines += ["", "## 反作弊统计", ""]
    flags = [r for r in rows if r.get("flag") == "SUSPICIOUS"]
    inv = [r for r in rows if r["verdict"] == "invalid"]
    lines.append(f"- SUSPICIOUS flag：{len(flags)} 次；invalid：{len(inv)} 次；"
                 f"总评估：{len(rows)} 次")
    out = os.path.join(memory.STATE, "campaign_report.md")
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[report] → {out}")


def main():
    ap = argparse.ArgumentParser(description="perfagent 全链路战役")
    ap.add_argument("phase", choices=["profile", "search", "redteam", "report"])
    ap.add_argument("--proposer", default="heuristic")
    ap.add_argument("--budget", type=int, default=8)
    ap.add_argument("--fresh", action="store_true",
                    help="A/B 隔离：忽略历史去重（默认跨 session warm-start 去重）")
    ap.add_argument("--rebase", type=int, default=3,
                    help="search 前 re-baseline 次数（0/1=单次；>=2 取中位，默认 3）")
    a = ap.parse_args()
    if a.phase == "profile":
        cmd_profile()
    elif a.phase == "search":
        cmd_search(a.proposer, a.budget, a.fresh, a.rebase)
    elif a.phase == "redteam":
        cmd_redteam()
    else:
        cmd_report()


if __name__ == "__main__":
    main()
