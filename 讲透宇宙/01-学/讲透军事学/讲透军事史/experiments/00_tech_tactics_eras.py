# -*- coding: utf-8 -*-
"""军事技术-战术共同演化七纪元编年:结构化处理+纪元间隔与转型战例锚断言(00/04 章配套实验)。

00 章七纪元骨架 + 04 章 C1(编年结构化走廊)的成品:
七纪元(冷兵器→火药→线列→堑壕→装甲→核→无人)各六字段:
  主导技术 / 战术形态 / 纪元成立年(=转型战例锚)/ 成立战例锚 /
  技术首现年 / 攻防平衡态
四个史学直觉的结构化断言:
  ① 锚战例年表正确且严格递增(坎尼 前216 → 纳卡 2020,无 0 年跨代计算)
  ② 加速律:火药纪元以来成立锚间隔 251→173→40→28 严格递减
     ——战争形态转型的时钟从百年级拧到十年级
  ③ 核反例:核→无人间隔 75 年 > 装甲→核的 28 年
     ——威慑冻结大国直接战争,转型钟被战略稳定性人为拨慢
  ④ 技术先行律:每个纪元的技术首现都早于纪元成立(滞后列=组织吸收期):
     984/107/17/36/1/7/19 年——"军事革命"的完成时刻是组织与条令
     吸收新技术的时刻,不是发明时刻(军事革命论/RMA 史学批判的数据面)

⚠ 史学纪律(02 章):锚战例选样=军事史通说(西欧-大西洋战场为主);
换选样(如以中国战史锚重排)会改变曲线——04 章 §5 断代敏感性
是使用本脚本的正确姿势。

跑法: python experiments/00_tech_tactics_eras.py
"""

# 纪元记录:year 负数=公元前(无 0 年);balance 为序数判断(攻/防/威慑),
# 只做交替断言不做强度宣称;锚战例多为 T3/T4(通说档),升级须换一手研究
ERAS = [
    dict(name="冷兵器",
         tech="青铜/铁冷兵器+畜力(战车/骑兵)",
         tactic_form="方阵·车战·骑射:密集近战体系",
         anchor_year=-216, anchor="坎尼会战(双层包围母题)",
         tech_first=-1200, tech_first_note="铁器军事化扩散(约前 1200 起)",
         balance="攻"),
    dict(name="火药",
         tech="黑火药攻城炮+火绳枪(pike and shot 混编)",
         tactic_form="炮兵攻坚+长矛火绳枪方阵;城墙以棱堡回应",
         anchor_year=1453, anchor="君士坦丁堡陷落(乌尔班攻城炮)",
         tech_first=1346, tech_first_note="克雷西会战(火炮西欧野战早期运用记载)",
         balance="攻"),
    dict(name="线列",
         tech="燧发枪+套环刺刀(长矛兵退役)",
         tactic_form="线式战术+操典训练+常备军",
         anchor_year=1704, anchor="布伦海姆会战(线式战术成熟)",
         tech_first=1687, tech_first_note="套环刺刀普及(淘汰长矛的组织临界)",
         balance="攻"),
    dict(name="堑壕",
         tech="后装线膛枪炮(射速×精度跃升)",
         tactic_form="火力配系+野战工事:正面冲锋破产",
         anchor_year=1877, anchor="普列夫纳围攻(堑壕+后装枪挡停纵队冲锋)",
         tech_first=1841, tech_first_note="德赖泽针发后装线膛枪列装",
         balance="防"),
    dict(name="装甲",
         tech="内燃机+履带装甲+无线电",
         tactic_form="诸兵种合成突击(坦克集群+奇袭炮兵)",
         anchor_year=1917, anchor="康布雷战役(大规模坦克集群突破堑壕)",
         tech_first=1916, tech_first_note="索姆河战役(坦克首次实战)",
         balance="攻"),
    dict(name="核",
         tech="核武器+投送体系",
         tactic_form="威慑结构(非战场形态:战略均衡)",
         anchor_year=1945, anchor="广岛长崎(核武器实战使用)",
         tech_first=1938, tech_first_note="核裂变发现(哈恩-斯特拉斯曼)",
         balance="威慑"),
    dict(name="无人",
         tech="无人机+精确弹药+组网传感器",
         tactic_form="透明战场分布式杀伤(集中即暴露)",
         anchor_year=2020, anchor="纳卡战争(无人机主导的对装甲体系作战)",
         tech_first=2001, tech_first_note="武装无人机首次实战运用(阿富汗)",
         balance="防"),
]

# 锚战例年表校准值(转型战例锚七条;通说档 T3/T4)
ANCHOR_EXPECTED = {
    "坎尼会战(双层包围母题)": -216,
    "君士坦丁堡陷落(乌尔班攻城炮)": 1453,
    "布伦海姆会战(线式战术成熟)": 1704,
    "普列夫纳围攻(堑壕+后装枪挡停纵队冲锋)": 1877,
    "康布雷战役(大规模坦克集群突破堑壕)": 1917,
    "广岛长崎(核武器实战使用)": 1945,
    "纳卡战争(无人机主导的对装甲体系作战)": 2020,
}

ERA_ORDER = ["冷兵器", "火药", "线列", "堑壕", "装甲", "核", "无人"]


def years_between(a, b):
    """跨公元前后差值:无 0 年——一正一负时差值再减 1。"""
    return b - a - (1 if (a < 0 < b) else 0)


def main():
    print("=" * 76)
    print(f"军事技术-战术共同演化七纪元编年:{len(ERAS)} 个纪元 · 六字段结构化")
    print("=" * 76)

    # ── C1 主表:纪元×技术×锚×滞后 ─────────────────────────
    print(f"\n{'纪元':<5} {'成立年':>6} {'成立战例锚':<24} {'技术首现':>5} "
          f"{'滞后':>4}  {'平衡态'}")
    for e in ERAS:
        lag = years_between(e["tech_first"], e["anchor_year"])
        print(f"{e['name']:<5} {e['anchor_year']:>6} {e['anchor']:<24} "
              f"{e['tech_first']:>5} {lag:>4}  {e['balance']}")
    print("\n主导技术首现:")
    for e in ERAS:
        print(f"  {e['name']:<5} ← {e['tech_first_note']}({e['tech_first']})")

    anchors = [e["anchor_year"] for e in ERAS]
    gaps = [years_between(a, b) for a, b in zip(anchors, anchors[1:])]

    # ── 断言 1:结构完整 + 锚战例年表正确 + 严格递增 ─────────
    assert len(ERAS) == 7, "七纪元缺一不可"
    assert [e["name"] for e in ERAS] == ERA_ORDER, "纪元顺序应与通说分期一致"
    for e in ERAS:
        assert ANCHOR_EXPECTED[e["anchor"]] == e["anchor_year"], \
            f"锚战例年份校准失败:{e['anchor']}"
        assert e["tech_first"] < e["anchor_year"], \
            f"技术先行律违反:{e['name']}"
        assert e["balance"] in ("攻", "防", "威慑"), "平衡态枚举外取值"
    assert anchors == sorted(anchors) and len(set(anchors)) == 7, \
        "成立锚应严格递增"
    assert years_between(-216, 1453) == 1668, "无 0 年纪律:前216→1453 应为 1668 年"
    assert years_between(-1, 1) == 1, "无 0 年纪律:前1→公元1 应为 1 年"
    print("\n" + "=" * 76)
    print("断言 1 通过:七纪元结构完整,锚战例年表正确,成立锚严格递增"
          "(前216→2020,跨代差值实测 1668 年)✓")

    # ── 断言 2:加速律(251→173→40→28 严格递减)──────────────
    print(f"\n纪元成立锚间隔序列:{gaps}")
    core = gaps[1:5]           # 火药→线列→堑壕→装甲→核(核反例除外)
    assert core == [251, 173, 40, 28], "加速律核心四跳应为此值"
    assert all(a > b for a, b in zip(core, core[1:])), \
        "加速律:火药纪元以来成立锚间隔应严格递减"
    print(f"加速律检验:{' > '.join(map(str, core))} 严格递减 ✓")
    print("          ——转型时钟从百年级(251)拧到十年级(28);"
          "操典/军校/参谋制度在系统性缩短组织吸收期")

    # ── 断言 3:核反例(75 年 > 28 年)──────────────────────
    nuclear_gap = gaps[-1]
    assert nuclear_gap == 75 and nuclear_gap > gaps[-2], \
        "核反例:核→无人间隔应大于装甲→核间隔"
    assert nuclear_gap > core[2], "核反例应同时大于堑壕→装甲的 40 年"
    print(f"核反例检验:核→无人间隔 {nuclear_gap} 年 > 装甲→核 28 年 ✓")
    print("            ——威慑冻结大国直接战争,转型钟被战略稳定性拨慢;"
          "核纪元的特殊性在编年数据上肉眼可见(1991 海湾是纪元内变奏)")

    # ── 断言 4:技术先行律(滞后列=组织吸收期)────────────────
    lags = [years_between(e["tech_first"], e["anchor_year"]) for e in ERAS]
    assert all(l >= 1 for l in lags), "技术首现必须早于纪元成立"
    assert lags == [984, 107, 17, 36, 1, 7, 19], "滞后列应为此值"
    assert max(lags[1:]) == 107, "火药吸收最久(107 年,克雷西→君士坦丁堡)"
    assert min(lags) == 1, "装甲吸收最急(1 年,索姆河→康布雷,战时危机压缩)"
    print(f"技术先行律:滞后列 {lags} ✓")
    print("            ——火药最久(107 年)、装甲最急(1 年);纪元成立年="
          "组织与条令吸收完成年,不是发明年(技术决定论读不出这一列)")

    # ── 断言 5:攻防钟摆交替(堑壕=防 → 装甲=攻 的再平衡)─────
    bal = {e["name"]: e["balance"] for e in ERAS}
    assert bal["堑壕"] == "防" and bal["装甲"] == "攻", \
        "攻防钟摆:1877 防御极盛 → 1917 攻势恢复"
    assert bal["核"] == "威慑", "核纪元是攻防之外的第三态"
    assert bal["堑壕"] != bal["装甲"], "钟摆必须交替"
    print("攻防钟摆检验:线列(攻)→堑壕(防)→装甲(攻)→核(威慑第三态)✓")
    print("              ——一战堑壕是攻防失衡下的理性均衡,装甲恢复机动;"
          "钟摆交替而非单向箭头")

    print("\n" + "=" * 76)
    print("五组断言全部通过:锚年表 / 加速律 / 核反例 / 技术先行律 / 攻防钟摆 ✓")
    print("\n⚠ 史学纪律提醒:锚战例选样=西欧-大西洋战场通说;换选样重跑"
          "(04 章 §5 断代敏感性)")
    print("  是使用本脚本的正确姿势——数据度量『通说关注度』,"
          "不直接等于『战争形态演化速率』。")


if __name__ == "__main__":
    main()
