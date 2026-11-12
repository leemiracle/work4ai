#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static vs Continuous Batching 离散事件模拟器（教学用）。

模型：GPU 每 iteration 处理当前 batch 内每个请求 1 步（prefil 1 步 + decode L 步）。
  - static batching：凑满 B 个请求（或超时）才开工，整批全部完成才接收下一批
  - continuous batching：每 iteration 粒度调度——完成的请求立即退出，等待的请求立即补位
请求长度异构（真实负载的宿命），观察吞吐/延迟/批占用率差异。
真实跑法：python3 batching_sim.py
"""
import random


def make_requests(n, seed=42, min_len=8, max_len=128, span=200):
    rng = random.Random(seed)
    reqs = []
    for i in range(n):
        reqs.append({
            'id': i,
            'arrive': rng.randint(0, span),        # 到达时间（iteration 单位）
            'decode': rng.randint(min_len, max_len),  # 需要的 decode 步数（异构！）
        })
    return reqs


def simulate(reqs, batch_size, mode, timeout=None):
    """返回 (总时长, 平均请求延迟, 完成吞吐, 平均批占用率)。

    时间轴按 iteration 离散推进；static 模式下新批需凑满 B 或等 timeout 个 iteration。
    """
    t = 0
    pending = sorted(reqs, key=lambda r: r['arrive'])  # 未到达队列
    idx = 0
    batch = {}          # id -> 剩余步数（含 prefill 1 步，计入 remaining 初始 decode+1）
    done_at = {}
    occupancies = []
    static_wait = 0
    while len(done_at) < len(reqs):
        # ---- 接收到达的请求 ----
        if mode == 'static':
            # 仅当 batch 为空时才凑批：凑到 B 或超时
            if not batch:
                while idx < len(pending) and len(batch) < batch_size:
                    r = pending[idx]
                    if r['arrive'] <= t:
                        batch[r['id']] = r['decode'] + 1
                        idx += 1
                    else:
                        break
                if len(batch) < batch_size:
                    # 等下一个请求到达或超时凑批
                    static_wait += 1
                    nxt = pending[idx]['arrive'] if idx < len(pending) else t + 1
                    if timeout is not None and static_wait >= timeout and batch:
                        static_wait = 0
                    elif nxt > t:
                        t = nxt - 1  # 跳到下一请求到达前一刻（下面 t+=1 对齐）
                        static_wait = 0
        else:
            # continuous：每步都补位
            while idx < len(pending) and len(batch) < batch_size and pending[idx]['arrive'] <= t:
                r = pending[idx]
                batch[r['id']] = r['decode'] + 1
                idx += 1
        # ---- 执行一个 iteration：批内每请求走 1 步 ----
        occupancies.append(len(batch))
        t += 1
        for rid in list(batch):
            batch[rid] -= 1
            if batch[rid] == 0:
                done_at[rid] = t
                del batch[rid]
    total = t
    lat = sum(done_at[r['id']] - r['arrive'] for r in reqs) / len(reqs)
    thru = len(reqs) / total
    occ = sum(occupancies) / len(occupancies)
    return total, lat, thru, occ


def main():
    N, B = 200, 16
    reqs = make_requests(N)
    st = simulate(reqs, B, 'static', timeout=None)          # 纯凑满才开批
    ct = simulate(reqs, B, 'continuous')
    print(f'负载: {N} 请求 / batch容量 {B} / decode 长度 8-128 异构')
    print(f'{"":12}{"总时长":>8}{"平均延迟":>10}{"吞吐(req/it)":>14}{"平均批占用":>12}')
    print(f'{"static":12}{st[0]:>8}{st[1]:>10.1f}{st[2]:>14.3f}{st[3]:>12.1f}/{B}')
    print(f'{"continuous":12}{ct[0]:>8}{ct[1]:>10.1f}{ct[2]:>14.3f}{ct[3]:>12.1f}/{B}')
    print(f'吞吐提升 {st[2] and ct[2]/st[2]:.2f}x, 批占用提升 {ct[3]/st[3]:.2f}x')


if __name__ == '__main__':
    main()
