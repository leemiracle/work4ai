# -*- coding: utf-8 -*-
"""fact_agent.py — 端侧事实记忆 Agent 的共享核心（校验器+评估框架）

单一来源原则（AGENTS.md）：parse_json/validate/collapse_count 在此定义，
后续所有实验 import 复用。01_l1_bare_loop.py 是历史快照，保留但不回改。

用法：
    from fact_agent import DATASET30, parse_json, validate, judge, run_eval
"""
import json

CATS = ["日程", "账单", "人际", "档案", "健康"]
GENERIC = {"日期", "时间", "地点", "事件", "人物", "事实", "金额", "内容",
           "事项", "信息", "行为", "动作", "数量", "名称", "编号"}


# ── 校验器三件套 ────────────────────────────────────────────────────
def parse_json(text):
    """从模型输出抠 JSON。返回 {'facts': [...]} 或 None。"""
    try:
        lo, hi = text.find("{"), text.rfind("}")
        obj = json.loads(text[lo:hi + 1])
        return obj if isinstance(obj.get("facts"), list) else None
    except Exception:
        return None


def _bigrams(s):
    import re
    s = re.sub(r"[，。、！？\s\d]", "", s)  # 标点/数字归一（数字形态多变）
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) > 1 else {s}


def validate(obj, sentence, grounded_mode="substr"):
    """校验工具：枚举 + 塌缩 + 证据接地。返回 (ok, problems, facts)。
    grounded_mode:
      "substr" 连续子串（严：拒绝一切重组，但误杀合理重组——L3 教训）
      "bag"    词袋覆盖 ≥80%（宽：容忍语序重组，仍拒绝编造词——L3-E 版）"""
    problems, facts = [], []
    sb = _bigrams(sentence)
    for f in obj["facts"]:
        fact = str(f.get("fact", "")).strip()
        cat = str(f.get("category", "")).strip()
        if cat not in CATS:
            problems.append(f"category '{cat}' 不在枚举内")
            continue
        if not fact or fact in GENERIC or len(fact) <= 2:
            problems.append(f"fact '{fact}' 是标签词/过短")
            continue
        if grounded_mode == "substr":
            ok_g = fact in sentence
        else:  # bag：fact 的 bigram 至少 80% 出现在原句
            fb = _bigrams(fact)
            ok_g = (len(fb & sb) / len(fb)) >= 0.8 if fb else False
        if not ok_g:
            problems.append(f"fact '{fact}' 未通过证据接地（{grounded_mode}）")
            continue
        facts.append({"fact": fact, "category": cat})
    return (not problems), problems, facts


def collapse_count(obj):
    return sum(1 for f in obj["facts"]
               if str(f.get("fact", "")).strip() in GENERIC
               or len(str(f.get("fact", "")).strip()) <= 2)


# ── L3 固定任务集：34 句（L1 的 10 句为子集，标注含 gold 类别多重集）──
# 难度分布：直陈 16 / 复合句 8 / 口语间接 2 / 无事实 4
# 金标准只锁 类别多重集+事实数，fact 内容由接地校验保证
DATASET30 = [
    # — 日程 (6) —
    ("我明天早上八点要去医院复查，记得提醒我带上医保卡。", ["日程", "健康"], 2),
    ("小张说他下周三要去杭州出差。", ["日程", "人际"], 2),
    ("周三下午三点和老王在星巴克谈合作。", ["日程", "人际"], 2),
    ("周五晚上要参加公司的年会，得提前半小时到。", ["日程"], 2),
    ("下周二上午十点约了牙医洗牙。", ["日程", "健康"], 2),
    ("明天下午的部门例会改到线上开了。", ["日程"], 1),
    # — 账单 (6) —
    ("这个月电费已经交过了，一共137块。", ["账单"], 2),
    ("房贷每月还3200块，15号自动扣。", ["账单"], 2),
    ("手机套餐下个月涨到99了，考虑换个便宜的。", ["账单"], 1),
    ("物业费还没交，月底前得去交一下。", ["账单"], 1),
    ("孩子的钢琴课学费一学期4800，周日续费。", ["账单", "日程"], 2),
    ("宽带年费到期了，续费是600一年。", ["账单"], 2),
    # — 人际 (6) —
    ("我女儿的生日是6月12号。", ["档案", "人际"], 2),
    ("小李升职当上部门经理了，下周请大家吃饭。", ["人际", "日程"], 2),
    ("老王家儿子考上北大了吧？", ["人际", "档案"], 1),
    ("隔壁新搬来的邻居姓陈，人挺热情。", ["人际"], 1),
    ("王姐说她周六从上海回来。", ["人际", "日程"], 2),
    ("我大学同学聚会定在下个月15号。", ["人际", "日程"], 2),
    # — 档案 (6) —
    ("我的身份证放在书房抽屉第二层了。", ["档案"], 1),
    ("家里户口本在妈妈那保管着。", ["档案"], 1),
    ("车钥匙我挂玄关钥匙架上了。", ["档案"], 1),
    ("我的工号是A0872，入职五年了。", ["档案"], 2),
    ("护照明年三月到期，得提前半年换新的。", ["档案"], 2),
    ("Wi-Fi密码改成了家里生日组合。", ["档案"], 1),
    # — 健康 (6) —
    ("降压药每天吃一次，早饭之后吃。", ["健康"], 2),
    ("爸的体检报告出来了，血压有点高。", ["健康"], 2),
    ("最近失眠严重，凌晨三点都睡不着。", ["健康"], 1),
    ("医生说我的血糖临界了，少吃甜的。", ["健康"], 2),
    ("过敏药得常备，春天花粉太厉害。", ["健康"], 2),
    ("体检预约在周四上午，需要空腹。", ["日程", "健康"], 2),
    # — 无事实 (4)（从 L1 的 2 句扩为 4 句）—
    ("今天天气真不错啊，适合出门散散步。", [], 0),
    ("哈哈，这个视频太好笑了。", [], 0),
    ("嗯，我知道了。", [], 0),
    ("谢谢，辛苦了。", [], 0),
]


def judge(facts, gold_cats, gold_n):
    """裁判（L1 教训修订版）：
    pass = 类别多重集匹配（大类不漏不错） + 事实全部接地（无编造，validate 已保证）
          + 无事实句必须抽 0 条。
    数量精确匹配被降级为过程指标——因为"电费已交+137块"抽 1 条合并或
    2 条拆分都合理，精确数量匹配是金标准粒度歧义，不是模型错误。
    返回 (passed, n_delta)  n_delta=len(facts)-gold_n 供过程统计。
    """
    from collections import Counter
    pred = Counter(f["category"] for f in facts)
    gold = Counter(gold_cats)
    if gold_n == 0:
        return (len(facts) == 0), 0
    return (pred == gold), len(facts) - gold_n


def metrics_header():
    return ("ver        json cat_ok grnd colps hallu pass   "
            "time_s  retries")


def metrics_row(name, R, n, dt):
    return (f"{name:<10} {R['json_ok']:>3} {R['cat_ok']:>5} "
            f"{R['grounded']:>4} {R['collapse']:>5} {R['hallu']:>4} "
            f"{R['passn']:>4} {dt:>6.0f} {R['retry_used']:>7}")
