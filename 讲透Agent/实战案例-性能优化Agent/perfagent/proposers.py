"""perfagent.proposers — 决策层提议器（易变插槽：换提议器不动 guard/评估）。

四类：
  grid      零智能基线（对照组）
  fullgrid  双 knob 全扫描（E3：threads × affinity，空间平方化）
  heuristic 画像卡驱动的规则提议（带宽/同步开销先验）
  llm       OpenAI 兼容端点（上下文=画像卡+trap 库，SemaTune decision context）
  mockllm   LLM 插槽管路验证（确定性假 LLM，真实端点不可用时的降级）
"""
import json
import os
import urllib.request

from actions import NPROC, expand
from workloads import stable_seed


class Grid:
    def propose(self, card, traps, budget):
        return [{"threads": t} for t in range(1, NPROC + 1)][:budget]


class FullGrid:
    """E3：加 affinity 维度。SMT 机器上提供 '物理核半宽' 与 '偶数核(避开 SMT 兄弟)' 两种。"""
    def __init__(self, topo):
        self.topo = topo

    def propose(self, card, traps, budget):
        out, p = [], self.topo["physical_cores"]
        if self.topo["smt"] and p < NPROC:
            affs = [None, f"0-{p-1}", ",".join(str(i) for i in range(0, NPROC, 2))]
        else:
            # 无 SMT：半宽/四分宽（少核→少争用+缓存局部性，对 flat/memory 类可能有益）
            affs = [None, f"0-{max(1, p//2)-1}", f"0-{max(1, p//4)-1}"]
        for t in range(1, NPROC + 1):
            for a in affs:
                if a is None:
                    out.append({"threads": t})
                elif t <= len(expand(a)):
                    out.append({"threads": t, "affinity": a})
        return out[:budget]


class Heuristic:
    """画像卡 → 少量候选。v2：先验 + probe_best_threads 遥测双通道（E2-v2 验证
    '规则+遥测' 是否追平 'LLM+遥测'）。"""
    def __init__(self, topo):
        self.topo = topo

    def propose(self, card, traps, budget):
        p, cls, out = self.topo["physical_cores"], card["scaling_class"], []
        probe_t = card.get("probe_best_threads")
        if cls == "thread-adverse":
            out += [{"threads": 1}, {"threads": 2}]
        elif cls == "compute-scaling":
            out += [{"threads": p}, {"threads": self.topo["nproc"]}]
        elif cls == "partial-scaling":
            out += [{"threads": max(2, p // 2)}, {"threads": p}]
        else:
            out += [{"threads": 2}, {"threads": 1}]
        if probe_t:                                   # v2：遥测通道（有探针就用）
            out.insert(0, {"threads": int(probe_t)})
        if self.topo["smt"] and cls in ("thread-adverse", "flat"):
            out.append({"threads": 1, "affinity": "0"})   # 单物理核钉扎避 SMT 抖动
        # 去重保序
        seen, dedup = set(), []
        for c in out:
            k = json.dumps(c, sort_keys=True)
            if k not in seen:
                seen.add(k)
                dedup.append(c)
        return dedup[:budget]


class MockLLM(Heuristic):
    """LLM 管路验证：响应走相同解析路径，但内容确定性生成。"""
    tag = "mockllm"


class LLM:
    def __init__(self, topo):
        self.topo = topo
        self.base = (os.environ.get("PERFAGENT_LLM_BASE_URL")
                     or os.environ.get("PERFLOOP_LLM_BASE_URL")
                     or os.environ.get("ZHIPU_CODING_BASE_URL", "")).rstrip("/")
        self.key = (os.environ.get("PERFAGENT_LLM_API_KEY")
                    or os.environ.get("PERFLOOP_LLM_API_KEY")
                    or os.environ.get("ZHIPU_API_KEY", ""))
        self.model = (os.environ.get("PERFAGENT_LLM_MODEL")
                      or os.environ.get("PERFLOOP_LLM_MODEL", "glm-5.3"))
        if not (self.base and self.key):
            raise SystemExit("[perfagent] LLM 提议器需要 PERFAGENT_LLM_BASE_URL/_API_KEY "
                             "（或 PERFLOOP_* 同名）；无端点请用 mockllm/heuristic/grid")

    def propose(self, card, traps, budget):
        ctx = json.dumps({
            "workload": {k: card[k] for k in
                         ("name", "scaling_class", "probe_ms", "probe_best_threads",
                          "intensity_Mflop_per_rep", "baseline_ms")},
            "topology": self.topo,
            "recent_traps": traps[-5:],
            "budget": budget,
            "output_format": '{"proposals": [{"threads": int, "affinity": "0-3"|null}]}',
        }, ensure_ascii=False)
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content":
                 "你是 CPU 性能调优专家。根据负载画像与拓扑提出至多 budget 个线程/亲和配置。"
                 "只输出 JSON：{\"proposals\":[{\"threads\":int,\"affinity\":string|null}]}"},
                {"role": "user", "content": ctx}],
            "temperature": 0.2,
            "thinking": {"type": "disabled"},   # ZHIPU coding 端点铁律
        }).encode()
        # 提议器永不炸主循环：超时/解析失败 → 1 次重试 → 空列表降级（记入日志）
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(
                    self.base + "/chat/completions", data=body,
                    headers={"Content-Type": "application/json",
                             "Authorization": f"Bearer {self.key}"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    txt = json.loads(resp.read())["choices"][0]["message"]["content"]
                data = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
                out = []
                for c in data.get("proposals", []):
                    cfg = {"threads": int(c["threads"])}
                    if c.get("affinity"):
                        cfg["affinity"] = str(c["affinity"])
                    out.append(cfg)
                return out[:budget]
            except Exception as e:
                print(f"  [proposer:llm] 第{attempt}次调用失败: {type(e).__name__}: {e}")
        print("  [proposer:llm] 降级为空提议（本负载跳过）")
        return []


def make(name, topo):
    if name == "grid":
        return Grid()
    if name == "fullgrid":
        return FullGrid(topo)
    if name == "heuristic":
        return Heuristic(topo)
    if name == "mockllm":
        return MockLLM(topo)
    if name == "llm":
        return LLM(topo)
    raise ValueError(name)
