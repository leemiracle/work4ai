# -*- coding: utf-8 -*-
"""04a_memory.py — L4a 记忆层：JSONL 存储 + 去重 + 检索（ClaudeCode 式文件记忆）

设计立场（端侧诚实约束）：
  - 不用向量库：端侧 CPU 没有 embedding 模型预算；ClaudeCode 源码深读的
    结论——"记忆无向量库"在生产编码 agent 中同样成立
  - 文件即记忆：memory.jsonl 人类可读可编辑（用户能直接删错条目=最朴素的
    记忆治理），去重/检索规则全在代码里可审计

三层功能：
  1. write(fact, category, src_sentence)   精确去重 + 子串软去重
  2. query(text, category=None, k=3)       词袋打分检索（BM25 简化版）
  3. stats()                               记忆库健康度

自测：灌入模拟抽取结果（含 3 组重复/子串冲突）→ 验证去重 → 8 个查询测检索。
运行（容器或本机，无模型依赖，秒级）：python3 04a_memory.py
"""
import json
import os
import re
import time
from collections import Counter

MEMORY_PATH = os.environ.get("MEMORY_PATH", "memory.jsonl")


def _norm(s):
    return re.sub(r"[，。、！？\s]", "", s)


class FactMemory:
    def __init__(self, path=MEMORY_PATH):
        self.path = path
        self.facts = []
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.facts.append(json.loads(line))

    def write(self, fact, category, src_sentence):
        """写入：精确去重 → 子串软去重（保留信息更全的一条）。返回动作。"""
        nf = _norm(fact)
        if not nf:
            return "skip-empty"
        for i, m in enumerate(self.facts):
            if m["category"] == category:
                om = _norm(m["fact"])
                if nf == om:
                    return "skip-dup"
                if nf in om:            # 新事实是已有事实的子串 → 已覆盖
                    return "skip-covered"
                if om in nf:            # 新事实超串 → 替换（信息更全）
                    m["fact"] = fact
                    m["src_sentence"] = src_sentence
                    m["ts"] = time.strftime("%Y-%m-%d")
                    self._flush()
                    return "replace-upgraded"
        self.facts.append({
            "fact": fact, "category": category,
            "src_sentence": src_sentence,
            "ts": time.strftime("%Y-%m-%d"), "src": "extract"})
        self._flush()
        return "append"

    def _flush(self):
        with open(self.path, "w", encoding="utf-8") as f:
            for m in self.facts:
                f.write(json.dumps(m, ensure_ascii=False) + "\n")

    def query(self, text, category=None, k=3):
        """词袋检索：查询词命中 fact 的字数（滑窗二元组）打分。
        兜底：过滤后全 0 分时返回该类别最近 k 条（ts 倒序）——
        词袋有语义鸿沟（"安排"↔"周三下午"无交集），端侧无向量模型时
        类别过滤是最后的安全网。"""
        def bigrams(s):
            s = _norm(s)
            return {s[i:i + 2] for i in range(len(s) - 1)}
        qb = bigrams(text)
        pool = ([m for m in self.facts
                 if m["category"] == category] if category
                else self.facts)
        scored = []
        for m in pool:
            fb = bigrams(m["fact"] + m["src_sentence"])
            score = len(qb & fb)
            if score > 0:
                scored.append((score, m))
        if scored:
            scored.sort(key=lambda x: -x[0])
            return [m for _, m in scored[:k]]
        # fallback：类别兜底（L4b 将用 LLM 查询改写进一步补语义）
        ranked = sorted(pool, key=lambda m: m.get("ts", ""), reverse=True)
        return ranked[:k]

    def stats(self):
        c = Counter(m["category"] for m in self.facts)
        return {"total": len(self.facts), "by_cat": dict(c)}


if __name__ == "__main__":
    # —— 自测：模拟抽取结果灌入（含冲突组）——
    os.environ["MEMORY_PATH"] = MEMORY_PATH
    if os.path.exists(MEMORY_PATH):
        os.remove(MEMORY_PATH)
    mem = FactMemory(MEMORY_PATH)
    IN = [  # (fact, category, src)
        ("周三下午三点和老王在星巴克谈合作", "日程", "周三下午三点和老王在星巴克谈合作。"),
        ("房贷每月15号自动扣款3200块", "账单", "房贷每月还3200块，15号自动扣。"),
        ("降压药每天吃一次", "健康", "降压药每天吃一次，早饭之后吃。"),
        ("降压药每天吃一次早饭之后吃", "健康", "降压药每天吃一次，早饭之后吃。"),  # 超串→replace
        ("周三下午三点和老王在星巴克谈合作", "日程", "重复句"),                      # 精确dup
        ("房贷每月还3200块", "账单", "房贷每月还3200块。"),                          # 子串→covered
        ("我女儿的生日是6月12号", "档案", "我女儿的生日是6月12号。"),
        ("体检预约在周四上午", "健康", "体检预约在周四上午，需要空腹。"),
    ]
    actions = [mem.write(f, c, s) for f, c, s in IN]
    print("[去重测试]")
    for (f, _, _), a in zip(IN, actions):
        print(f"  {a:<16} {f}")
    st = mem.stats()
    print(f"[库] total={st['total']}（期望 5：8条输入，1精确dup+1子串+1超串替换）")
    print("     by_cat:", st["by_cat"])

    print("\n[检索测试] 查询→top1（命中判定：返回的相关事实含查询关键信息）")
    QUERIES = [
        ("这周有什么安排？", "日程", "周三下午三点老王星巴克"),
        ("房贷什么时候扣？", "账单", "15号3200"),
        ("药怎么吃？", "健康", "降压药每天一次"),
        ("女儿生日？", "档案", "6月12"),
        ("体检是啥时候？", None, "周四上午"),
    ]
    hits = 0
    for q, cat, expect in QUERIES:
        got = mem.query(q, category=cat, k=2)
        top = got[0]["fact"] if got else "(空)"
        ok = expect.replace(" ", "") in top or any(
            expect[:3] in m["fact"] for m in got)
        hits += ok
        print(f"  {'OK ' if ok else 'MISS'} [{q}] → {top}")
    print(f"[结论] 检索命中 {hits}/{len(QUERIES)}（词袋无向量的能力上限样本）")
