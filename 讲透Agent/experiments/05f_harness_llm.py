"""
实验 05f — L5 去模拟器化: harness 自进化闭环的归因+提案交给真 LLM (glm-5.3)
对应: 自进化2.0-整体叠加.md §7.1 (05c 的续篇) · perfagent 同款 env 链

与 05c 的分工:
  05c: 归因+提案 = 确定性策略 (隔离"harness 闭环"变量)
  05f: 归因+提案 = 真 glm-5.3 读自然语言失败日志 (隔离"LLM 归因质量"变量);
       冻结模型/逐题骰子/验证门全部沿用 05c — 只换"读日志出提案"的那个脑袋

诚实声明: "答题模型"仍是模拟器 (与 05c 同, 骰子钉题 id); 真实的是 ②归因 ③提案 —
  05c 反直觉点的原话: "真实系统里 ③ 归因那步就是 LLM 的位置, 也是 L5 层自进化
  最值钱的一环"。本实验就是把那个位置交给真 LLM。

LLM 接口 (perfagent proposers.py:80-135 同款, 2026-08-24 实测可用):
  env: ZHIPU_CODING_BASE_URL / ZHIPU_API_KEY (缺省 PERFAGENT_LLM_*)
  POST {base}/chat/completions · model=glm-5.3 · temperature=0.2
  thinking: {"type":"disabled"} ← ZHIPU coding 端点铁律
  永不炸主循环: 超时/解析失败 → 重试 1 次 → 降级为确定性归因 (输出中标注)

旋钮菜单 (Scope 允许清单, LLM 只能从中选):
  R_neg          指令规则: 否定词处理 ("不正确/没有/从未" 需反转判断)
  E_conflict     few-shot 示例: 冲突消解范例 (后文更新覆盖前文旧事实)
  strict_parser  严格解析器 + 重试预算 1 (裸字母输出, 解析失败即重试)
  R_fmt_noise    装饰性规则 (诱饵: 看起来像改进, 实际不影响任何题型)

评估指标:
  ① 每轮 LLM 提案 vs 模拟器"最大失分桶"真值 → 归因命中率
  ② 验证门把关 (R_fmt_noise 若被选中必须被拒)
  ③ 终分 vs 05c 确定性版 (92.5%)

实测结论 (2026-08-24, 真端点 glm-5.3 @ open.bigmodel.cn/api/coding/paas/v4, 3 runs × 3 轮 = 9 次调用):
  LLM 归因命中率(首选=最大失分桶): 9/9 (否定题→R_neg / 冲突题→E_conflict / 格式陷阱→strict_parser)
  三 run 终分全部 0.925 = 05c 确定性版 — 真 LLM 归因无损替换手写归因
  降级次数 0; LLM 的 reason 自带正确诊断语言 ("肯定式复述"/"后文覆盖前文"/"挽回疑似
  正确答案") — 原始调用与解析留档 05f_llm_log.jsonl
  ★ 局限声明: 失败日志由模拟器渲染 (题型→失败模式一一对应, 信号较干净); 真实日志
    混杂多因、含简单题噪声, 命中率会降 — 但验证门保证坏提案进不了谱系

跑法: python3 -u 05f_harness_llm.py   (无 env 时自动降级为确定性归因演示)
"""
import json, os, random, urllib.request, zlib

def P(*a): print(*a, flush=True)

random.seed(42)

# ============================================================
# Part 1: 冻结的答题模型 + 基准 (与 05c 完全同源)
# ============================================================
TYPES = ["simple", "negation", "conflict", "fmttrap"]
TYPE_CN = {"simple": "简单题", "negation": "否定题", "conflict": "冲突题", "fmttrap": "格式陷阱题"}
BENCH = [(i // 10, f"q{i:02d}") for i in range(40)]

def default_harness():
    return {"rules": [], "examples": [], "strict_parser": False, "retry": 0}

def p_correct(type_id, h):
    t = TYPES[type_id]
    if t == "simple":   return 0.95
    if t == "negation": return 0.30 + (0.60 if "R_neg" in h["rules"] else 0.0)
    if t == "conflict": return 0.25 + (0.55 if "E_conflict" in h["examples"] else 0.0)
    return 0.20 + (0.70 if (h["strict_parser"] and h["retry"] >= 1) else 0.0)

def evaluate(h):
    fp = json.dumps(h, sort_keys=True)
    score, per, failed = 0, {t: [0, 0] for t in TYPES}, []
    for type_id, qid in BENCH:
        rng = random.Random(zlib.crc32(qid.encode("utf-8")))
        ok = rng.random() < p_correct(type_id, h)
        per[TYPES[type_id]][0] += ok; per[TYPES[type_id]][1] += 1
        score += ok
        if not ok: failed.append((TYPES[type_id], qid))
    return score / len(BENCH), per, failed

def gap_truth(per):
    """模拟器内部的最大失分桶 (LLM 归因的地面真值)"""
    gaps = [((n - ok) * (0.3 if t == "simple" else 1.0), t) for t, (ok, n) in per.items()]
    gaps.sort(reverse=True)
    return gaps[0][1]

# ============================================================
# Part 2: 失败日志 → 自然语言 (LLM 读的原文, 含原始信号不含结论)
# ============================================================
def render_log(h, per, failed):
    lines = [f"## 基准失败日志 (当前得分 {evaluate(h)[0]:.1%}, 失败 {len(failed)}/40)",
             f"已应用的 harness 配置: rules={h['rules']} examples={h['examples']} "
             f"strict_parser={h['strict_parser']} retry={h['retry']}", ""]
    for t in TYPES:
        ok, n = per[t]
        if n - ok == 0: continue
        lines.append(f"### {TYPE_CN[t]} 失败 {n-ok}/{n}")
        for ft, qid in [x for x in failed if x[0] == t][:3]:   # 每桶最多 3 例
            if t == "negation":
                lines.append(f"- {qid}: 题干「以下哪项说法__不正确__? A.巴黎在法国 B.水往低处流 "
                             f"C.鲸是鱼 D.光速有限」模型答「A, 显然正确」正确答案 D — 输出肯定式复述, 未见否定语义处理")
            elif t == "conflict":
                lines.append(f"- {qid}: 对话前文「用户住上海」, 后文更新「我搬到杭州了」; 问「用户住哪」"
                             f"模型答「上海」正确答案 杭州 — 检索命中前文旧事实, 未消解时序冲突")
            elif t == "fmttrap":
                lines.append(f"- {qid}: 要求输出裸字母, 模型输出「答案是 C。因为……」"
                             f"解析器提取失败记 0 分 — 内容疑似正确但格式不可解析, 无重试")
            else:
                lines.append(f"- {qid}: 简单事实题错误 (个体噪声)")
        lines.append("")
    return "\n".join(lines)

KNOB_MENU = """可选 harness 旋钮 (只能从以下选择, 输出 knob 字段):
  R_neg          指令规则: 否定词处理 — 教模型识别"不正确/没有/从未"并反转判断
  E_conflict     few-shot 示例: 冲突消解范例 — 教模型"后文更新覆盖前文旧事实"
  strict_parser  严格解析器 + 重试预算 1 — 只接受裸字母, 解析失败自动重试一次
  R_fmt_noise    装饰性规则: 要求输出更"规范礼貌" (对正确率无已知作用)"""

# ============================================================
# Part 3: 真 LLM 归因+提案 (perfagent LLM 类的最小移植)
# ============================================================
class LLMAttributor:
    def __init__(self):
        self.base = (os.environ.get("PERFAGENT_LLM_BASE_URL")
                     or os.environ.get("ZHIPU_CODING_BASE_URL", "")).rstrip("/")
        self.key = (os.environ.get("PERFAGENT_LLM_API_KEY")
                    or os.environ.get("ZHIPU_API_KEY", ""))
        self.model = os.environ.get("PERFAGENT_LLM_MODEL", "glm-5.3")
        self.live = bool(self.base and self.key)
        self.log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "05f_llm_log.jsonl"), "a", encoding="utf-8")

    def propose(self, log_text, applied):
        """返回有序提案列表 [{"knob","reason"}]; 失败两次 → None (降级信号)"""
        if not self.live: return None
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content":
                 "你是 agent harness 工程专家。读基准失败日志, 归因最大失分模式, "
                 "从旋钮菜单中按预期收益排序选出至多 2 个提案。"
                 "只输出 JSON: {\"proposals\":[{\"knob\":\"...\",\"reason\":\"一句话\"}]}\n"
                 + KNOB_MENU},
                {"role": "user", "content": log_text + f"\n已应用过(勿重复): {applied}"}],
            "temperature": 0.2,
            "thinking": {"type": "disabled"},          # ZHIPU coding 端点铁律
        }).encode()
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(
                    self.base + "/chat/completions", data=body,
                    headers={"Content-Type": "application/json",
                             "Authorization": f"Bearer {self.key}"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    txt = json.loads(resp.read())["choices"][0]["message"]["content"]
                self.log.write(json.dumps({"t": "raw", "content": txt}, ensure_ascii=False) + "\n")
                data = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
                props = [{"knob": p["knob"], "reason": p.get("reason", "")}
                         for p in data.get("proposals", []) if p.get("knob") in
                         ("R_neg", "E_conflict", "strict_parser", "R_fmt_noise")]
                self.log.write(json.dumps({"t": "parsed", "proposals": props}, ensure_ascii=False) + "\n")
                self.log.flush()
                return props or None
            except Exception as e:
                self.log.write(json.dumps({"t": "error", "attempt": attempt,
                                           "err": f"{type(e).__name__}: {e}"}, ensure_ascii=False) + "\n")
                self.log.flush()
                P(f"    [llm] 第{attempt}次调用失败: {type(e).__name__}: {str(e)[:120]}")
        return None

APPLY = {"R_neg": lambda h: {**h, "rules": h["rules"] + ["R_neg"]},
         "E_conflict": lambda h: {**h, "examples": h["examples"] + ["E_conflict"]},
         "strict_parser": lambda h: {**h, "strict_parser": True, "retry": 1},
         "R_fmt_noise": lambda h: {**h, "rules": h["rules"] + ["R_fmt_noise"]}}

def deterministic_fallback(per, applied):
    """降级: 05c 的确定性归因 (桶失分排序 → 未应用的最大桶旋钮)"""
    order = {"negation": "R_neg", "conflict": "E_conflict", "fmttrap": "strict_parser", "simple": "R_fmt_noise"}
    gaps = sorted([((n-ok) * (0.3 if t == "simple" else 1.0), t) for t, (ok, n) in per.items()], reverse=True)
    for _, t in gaps:
        k = order[t]
        if k not in applied: return [{"knob": k, "reason": "[降级]确定性归因"}]
    return []

# ============================================================
# Part 4: 主循环 — 3 runs × 3 轮, LLM 归因 vs 真值
# ============================================================
def main():
    llm = LLMAttributor()
    P("=" * 74)
    P("Part 4  harness 自进化闭环 · 真 LLM 归因版 (模型冻结, 验证门确定性)")
    P(f"  LLM 端点: {'✓ ' + llm.model + ' @ ' + llm.base if llm.live else '✗ env 缺失 → 全程确定性降级'}")
    if not llm.live:
        P("  (设 ZHIPU_CODING_BASE_URL / ZHIPU_API_KEY 后重跑启用真端点)")

    RUNS = 3 if llm.live else 1
    hit_total, hit_cnt = 0, 0
    finals, degrades = [], 0
    for run in range(RUNS):
        P(f"\n—— run {run+1}/{RUNS} ——")
        h = default_harness()
        applied, score = [], evaluate(h)[0]
        P(f"  v1 种子 score={score:.3f}")
        for rnd in range(1, 4):
            s, per, failed = evaluate(h)
            log_text = render_log(h, per, failed)
            truth = gap_truth(per)
            props = llm.propose(log_text, applied)
            if props is None:
                props = deterministic_fallback(per, applied); degrades += 1
                P(f"  [run{run+1} r{rnd}] LLM 降级 → 确定性归因")
            top = props[0]["knob"]
            hit = (top == {"negation": "R_neg", "conflict": "E_conflict",
                           "fmttrap": "strict_parser", "simple": "R_fmt_noise"}[truth])
            hit_total += 1; hit_cnt += hit
            P(f"  [r{rnd}] 失分真值={TYPE_CN[truth]:5s} LLM首选={top:14s} "
              f"{'命中' if hit else '未中'} | reason: {props[0]['reason'][:46]}")
            committed = False
            for p in props:                               # 验证门: 提分才 commit
                cand = APPLY[p["knob"]](h)
                cs = evaluate(cand)[0]
                if cs > score:
                    P(f"        验证门: {p['knob']:14s} {score:.3f}→{cs:.3f} KEEP")
                    h, score, applied = cand, cs, applied + [p["knob"]]
                    committed = True; break
                P(f"        验证门: {p['knob']:14s} {score:.3f}→{cs:.3f} REJECT")
            if not committed:
                P("        ⚠ 本轮提案全被拒, harness 不变")
        finals.append(score)
        P(f"  终态 v: score={score:.3f}  applied={applied}")

    P("\n" + "=" * 74)
    P("汇总")
    P(f"  LLM 归因命中率(首选=最大失分桶): {hit_cnt}/{hit_total}")
    P(f"  终分: {['%.3f' % f for f in finals]}  (05c 确定性版 = 0.925)")
    P(f"  LLM 降级次数: {degrades}; 原始调用留档: 05f_llm_log.jsonl")

    P("=" * 74)
    P("反直觉点")
    P("""
- LLM 的位置只有两步, 但这两步正是'从日志到行动'的翻译: 模拟器答题产生的原始
  信号 (肯定式复述/时序冲突/格式不可解析) 不含任何结论, LLM 要把它们聚合成
  '这是否定语义缺陷'再映射到旋钮 — 05c 里这两步是手写的, 现在交给真 glm-5.3.

- 验证门依然确定性: LLM 选了诱饵 R_fmt_noise 也不怕 — 重跑基准分数不动即拒.
  'LLM 提案 + 确定性把关'的分工是 L5 层的安全形态: 允许 LLM 犯错, 不允许
  错误进谱系 (与 penguin RSI / Harness Evolver 的工程共识一致).

- 降级路径是设计的一部分: 端点超时/解析失败 → 确定性归因接管, 闭环永不中断
  (perfagent '提议器永不炸主循环'的同款纪律). 真实系统的可靠性来自最坏情况
  的地板, 不是最好情况的天花板.
""")

if __name__ == "__main__":
    main()
