#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""perfagent.resident — Qwen2.5-0.5B 常驻 server（消除子进程反复加载 ~15s 的成本）。

协议（stdin/stdout 按行 JSON，零网络依赖）：
  请求 {"op": "setup", "threads": 4}            → {"ok": true, "load_s": 12.3}
  请求 {"op": "forward", "input_ids": [[...]], "attention_mask": [[...]]}
                                                → {"ok": true, "fp": [...], "median_ms": 8.2,
                                                   "det_ok": true}
  请求 {"op": "quit"}                           → {"ok": true}

关键设计：
  - torch.set_num_threads 必须在模型加载前设置（interop 也设）——线程 knob 对
    常驻进程只能 setup 时生效；search 换 threads = campaign 侧重启 server
  - 计时仍在 server 内做（warmup + 逐 rep），但输入由 campaign 生成：
    防作弊语义不变（server 是"诚实的被测对象"，扰动由调用方注入）
  - 掉线/超时 → campaign 侧自动降级为子进程模式（见 runner 接入）
"""
import json
import os
import statistics
import sys
import time

MODEL_PATH = os.environ.get(
    "PERFAGENT_QWEN_PATH", "~/ai/models/Qwen2.5-0.5B-Instruct")


def main():
    import torch
    from transformers import AutoModelForCausalLM

    model = None
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "error": "bad json"}), flush=True)
            continue
        op = req.get("op")
        if op == "quit":
            print(json.dumps({"ok": True}), flush=True)
            return
        if op == "setup":
            t0 = time.perf_counter()
            torch.set_num_threads(int(req.get("threads", 1)))
            try:
                torch.set_num_interop_threads(1)
            except RuntimeError:
                pass                   # 已初始化后不可改，忽略
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH, torch_dtype=torch.float32).eval()
            print(json.dumps({"ok": True,
                              "load_s": round(time.perf_counter() - t0, 1)}),
                  flush=True)
        elif op == "forward":
            if model is None:
                print(json.dumps({"ok": False, "error": "setup first"}),
                      flush=True)
                continue
            ids = torch.tensor(req["input_ids"], dtype=torch.long)
            mask = torch.tensor(req["attention_mask"], dtype=torch.long)
            reps = int(req.get("reps", 8))
            # warmup（首次 forward 含惰性初始化）
            with torch.no_grad():
                model(input_ids=ids, attention_mask=mask)
            times, first_fp = [], None
            with torch.no_grad():
                for _ in range(reps):
                    t0 = time.perf_counter()
                    out = model(input_ids=ids, attention_mask=mask)
                    times.append((time.perf_counter() - t0) * 1000.0)
                    logits = out.logits[:, -1, :]          # 末 token logits
                    fp = [float(logits.sum()), float(logits.mean()),
                          float(logits.max()),
                          float((logits * logits).sum() ** 0.5)]
                    first_fp = first_fp or fp
            det_ok = all(abs(x - y) <= 1e-9 * max(1.0, abs(x))
                         for x, y in zip(first_fp, fp))
            print(json.dumps({
                "ok": True, "median_ms": statistics.median(times),
                "fp": first_fp, "det_ok": det_ok,
                "all_ms": [round(t, 2) for t in times]}), flush=True)
        else:
            print(json.dumps({"ok": False, "error": f"unknown op {op!r}"}),
                  flush=True)


if __name__ == "__main__":
    main()
