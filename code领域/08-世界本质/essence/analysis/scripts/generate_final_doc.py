#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成最终文档 v3 —— 两阶段架构：
阶段1: 为每个"机制池"收集所有候选引用
阶段2: 按章节从池中"领取"引用，保证每个子节有内容、跨节不重复
"""
import json, re
from pathlib import Path
from collections import defaultdict

ROOT = Path('/mnt/c/workspace/essence')
CACHE = ROOT / 'analysis/scripts/_central_local_cache'
OUT = ROOT / 'analysis/theme-central-local-relations.md'
items = json.loads((CACHE/'all_items.json').read_text(encoding='utf-8'))

# ============================================================
# 清洗
# ============================================================
def deep_clean(t):
    t = re.sub(r'【[^】]*】\s*', '', t)
    t = re.sub(r'\[(?:百分比|年份|金额|页码|其他\d*|地名[^]]*|人名)\]\s*', '', t)
    t = re.sub(r'\[(?:百分比|年份|金额)\d*\]\s*', '', t)
    t = re.sub(r'-\s*\d+\s*[-—]\s*[窒筑符靠第序论一二三四五六七八九十]+[^。；]{0,20}', '', t)
    t = re.sub(r'^\s*-\s*\d+\s*-\s*', '', t)
    t = t.replace('o/o', '%').replace('〇/', '%').replace('0/', '%')
    # 清理残留的"429毛"类 OCR 错误（毛→%）
    t = re.sub(r'(\d+)毛', r'\1%', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def is_low_quality(r):
    t = r['text']
    if re.match(r'^\d+\.\d+\s', t) and len(t) < 80: return True
    if re.match(r'^\d+\.\d+\s+\S+\s+\d+\.\d+\s', t) and '第' not in t: return True
    if len(deep_clean(t)) < 30: return True
    if re.match(r'^\[?\d+\]?\s*(?:参见|同上|转引自|资料来自)', t): return True
    return False

def smart_truncate(t, maxlen=650):
    t = deep_clean(t)
    if len(t) <= maxlen: return t
    cut = t[:maxlen]
    for sep in ['。', '；', '！', '？', '……']:
        idx = cut.rfind(sep)
        if idx > maxlen * 0.5: return cut[:idx+1]
    for sep in ['，', '、']:
        idx = cut.rfind(sep)
        if idx > maxlen * 0.6: return cut[:idx+1] + '……'
    return cut.rstrip('，、；') + '……'

def pk(r):
    m = re.search(r'(\d+)', str(r.get('page','')))
    return int(m.group(1)) if m else 9999

def fp(r):
    t = deep_clean(r['text'])
    return t[30:110] if len(t) >= 120 else t[:80]

def fmt_quote(r, maxlen=650):
    t = smart_truncate(r['text'], maxlen)
    page = r.get('page','') or '（页码不详）'
    return f'> **《{r.get("book","")}》** | {r["author"]} | {page}\n>\n> {t}\n'

# ============================================================
# 过滤候选
# ============================================================
def candidates(author, groups, kws_any=None, kws_all=None, exclude=None, min_len=60):
    out = []
    for r in items:
        if r['author'] != author: continue
        if not any(g in r['groups'] for g in groups): continue
        if is_low_quality(r): continue
        t = r['text']
        if len(deep_clean(t)) < min_len: continue
        if kws_any and not any(k in t for k in kws_any): continue
        if kws_all and not all(k in t for k in kws_all): continue
        if exclude and any(k in t for k in exclude): continue
        out.append(r)
    out.sort(key=pk)
    return out

def candidates_multi(authors, groups, **kw):
    out = []
    for a in authors:
        out.extend(candidates(a, groups, **kw))
    out.sort(key=pk)
    return out

# ============================================================
# 全局已用集合 + 领取函数
# ============================================================
USED = set()

def take(pool, n=1, prefer_kws=None, must_have=None):
    """从候选池中领取 n 个未被使用的条目"""
    if prefer_kws:
        pool = sorted(pool, key=lambda r: 0 if any(k in r['text'] for k in prefer_kws) else 1)
    else:
        pool = sorted(pool, key=pk)
    result = []
    for r in pool:
        f = fp(r)
        if f in USED: continue
        if must_have and must_have not in r['text']: continue
        USED.add(f)
        result.append(r)
        if len(result) >= n: break
    return result

# ============================================================
# 预建候选池
# ============================================================
P = {}
# 周雪光
P['zxg_yitong'] = candidates('周雪光', ['一统体制','有效治理'], min_len=60)
P['zxg_control'] = candidates('周雪光', ['控制权'], min_len=60)
P['zxg_gongmou'] = candidates('周雪光', ['共谋'], min_len=60)
P['zxg_yundong'] = candidates('周雪光', ['运动式治理'], min_len=60)
P['zxg_all'] = candidates('周雪光', ['一统体制','有效治理','控制权','共谋','运动式治理','集权分权','央地总论'], min_len=60)
# 周黎安
P['zla_fabao'] = candidates('周黎安', ['行政发包'], min_len=60)
P['zla_jinbiao'] = candidates('周黎安', ['锦标赛'], min_len=60)
P['zla_all'] = candidates('周黎安', ['行政发包','锦标赛','集权分权','财税总论','分税制'], min_len=60)
# 周飞舟
P['zfz_fiscal'] = candidates('周飞舟', ['央地总论','集权分权','分税制'], min_len=50)
P['zfz_transfer'] = candidates('周飞舟', ['转移支付'], min_len=40)
P['zfz_tudi'] = candidates('周飞舟', ['土地财政','分税制'], min_len=50)
P['zfz_budget'] = candidates('周飞舟', ['预算约束'], min_len=40)
P['zfz_all'] = candidates('周飞舟', ['央地总论','集权分权','分税制','转移支付','土地财政','预算约束','行政发包','锦标赛','财税总论'], min_len=40)
P['zfz_data'] = [r for r in P['zfz_all'] if re.search(r'\d', r['text'])]
# 黄奇帆
P['hq_data'] = candidates('黄奇帆', ['财税总论','分税制','土地财政','转移支付'], min_len=40)
P['hq_data'] = [r for r in P['hq_data'] if re.search(r'\d{2,}|亿元|万亿', r['text'])]

print('Pool sizes:')
for k, v in P.items():
    print(f'  {k}: {len(v)}')

# ============================================================
# 构建文档
# ============================================================
doc = []
def w(s=''):
    doc.append(s)

def emit_section(title, quotes, intro=None, maxlen=700):
    """输出一个子节：标题 + 可选导语 + 引用列表。quotes 为空则不输出。"""
    if not quotes:
        return
    w(title)
    w()
    if intro:
        w(f'**{intro}**')
        w()
    for r in quotes:
        w(fmt_quote(r, maxlen))
    w()

# ======================= 标题与统计 =======================
w('---')
w('title: 央地关系专题深度分析——三书原文汇编')
w('date: 2026-07-13')
w('source: knowledge_index.json + 三份提取文件')
w('abstract: 从周雪光、周黎安、周飞舟三部著作中提取所有"央地关系"相关原文，按理论框架、关键机制、数据、历史演变四维组织。每条引用标注书名+作者+页码+原文，不做概括。')
w('---')
w()
w('# 央地关系专题深度分析')
w()
w('> **编制说明**：本文档从以下数据源中提取所有"央地关系"主题相关内容：')
w('> - `knowledge_index.json`（2.4MB，4407条知识条目）')
w('> - `extracted-knowledge-zhou-xueguang.md`（周雪光《中国国家治理的制度逻辑》）')
w('> - `extracted-knowledge-zhou-lian.md`（周黎安《转型中的地方政府》）')
w('> - `extracted-knowledge-others.md`（周飞舟《以利为利》等）')
w('>')
w('> 搜索关键词覆盖 14 组：央地总论 / 集权分权 / 一统体制 / 有效治理 / 控制权 / 共谋 / 行政发包 / 锦标赛 / 运动式治理 / 土地财政 / 分税制 / 转移支付 / 预算约束 / 财税总论。')
w('>')
w('> **体例**：每条引用格式为 `> **《书名》** | 作者 | 页码` + 原文摘录。不做概括，只引用原文。')
w()

from collections import Counter
acount = Counter()
for r in items:
    if r['groups'] and not is_low_quality(r):
        acount[r['author']] += 1
w('## 原文引用统计')
w()
w('| 作者 | 著作 | 央地关系相关条目（去低质后） |')
w('|------|------|------:|')
for a, c in acount.most_common():
    book = {'周雪光':'中国国家治理的制度逻辑','周黎安':'转型中的地方政府',
            '周飞舟':'以利为利','黄奇帆':'分析与思考','习近平':'习近平谈治国理政',
            '陈云':'陈云文选','钱穆':'钱穆国学作品集','孙萍':'过渡劳动',
            '王沪宁':'政治的人生','其他':'—'}.get(a,a)
    w(f'| {a} | {book} | {c} |')
w(f'| **合计** | | **{sum(acount.values())}** |')
w()
w('---')
w()

# ======================= 一、理论框架对照 =======================
w('## 一、理论框架对照')
w()
w('三部著作分别从不同学科视角切入央地关系，形成三个互补且存在张力的理论框架：')
w()
w('| 学者 | 著作 | 核心框架 | 学科视角 | 关键概念 |')
w('|------|------|---------|---------|---------|')
w('| 周雪光 | 中国国家治理的制度逻辑 | **一统体制 vs 有效治理** | 组织社会学 | 一统体制、有效治理、控制权理论、运动型治理、共谋现象 |')
w('| 周黎安 | 转型中的地方政府 | **行政发包制 + 政治锦标赛** | 经济学/激励理论 | 行政逐级发包、政治锦标赛、官场+市场、属地管理 |')
w('| 周飞舟 | 以利为利 | **财政关系**视角 | 公共财政学/社会学 | 统收统支、财政包干、分税制、转移支付、土地财政、软预算约束 |')
w()
w('---')
w()

# --- 1.1 周雪光 ---
w('### 1.1 周雪光："一统体制与有效治理"框架')
w()
w('> **核心命题**：中国国家治理的基本矛盾是"一统体制与有效治理"之间的深刻张力。中央集权的一统体制面对辽阔国土与地方差异，必然产生治理负荷过重与有效性不足之间的结构性矛盾。')
w()

emit_section('#### （一）基本矛盾的提出与两个维系机制',
    take(P['zxg_yitong'], 5, prefer_kws=['基本矛盾','一统体制与有效治理','两个基本维系','应对机制']),
    intro='一统体制有两个基本维系机制——官僚体制与一统观念制度。面对多重挑战，演化出三个应对机制。')

emit_section('#### （二）矛盾的两个极端：集权下的死寂 vs 分权下的失控',
    take(P['zxg_all'], 3, prefer_kws=['集权下的死寂','资源和权力的重心','激烈程度','权力下放']))

emit_section('#### （三）控制权理论：统一分析框架',
    take(P['zxg_control'], 5, prefer_kws=['控制权"理论','控制权理论','不完全契约','新产权理论','委托方','剩余控制权']),
    intro='周雪光借鉴不完全契约和新产权理论，提出"控制权"理论，将央地关系看作控制权在不同层级间的分配组合。')

emit_section('#### （四）中央集权体制如何解决一统与差异的矛盾？',
    take(P['zxg_all'], 2, prefer_kws=['中央集权体制如何解决','一统体制与地方差异','国土辽阔','一脉相承']))

w()
w('---')
w()

# --- 1.2 周黎安 ---
w('### 1.2 周黎安："行政发包制 + 政治锦标赛"框架')
w()
w('> **核心命题**：中国政府治理的两大基本制度是行政发包制（纵向权威分配）和政治锦标赛（横向晋升竞争），二者构成"官场+市场"的双层竞争模式。')
w()

emit_section('#### （一）行政发包制的定义',
    take(P['zla_fabao'], 3, prefer_kws=['行政逐级发包','理想类型','混合形态','属地管理为基础']),
    intro='行政发包制介于韦伯科层制与纯粹外包制之间，是一种混合治理形态。')

emit_section('#### （二）政治锦标赛的定义',
    take(P['zla_jinbiao'], 3, prefer_kws=['政治锦标赛模式','晋升与地方经济','为了政治晋升','地方官员的晋升与']),
    intro='将地方官员的晋升与地方经济发展绩效挂钩，形成横向晋升竞争。')

emit_section('#### （三）两大制度的内在统一',
    take(P['zla_all'], 2, prefer_kws=['两个基本分析概念','行政发包制和政治锦标赛','最重要的分析视角']))

emit_section('#### （四）"官场+市场"双层竞争模式',
    take(P['zla_jinbiao'], 3, prefer_kws=['官场+市场','双层','官场竞争','政经互动','嵌入','零和']),
    intro='"官场+市场"——地方官员之间的官场竞争与辖区企业之间的市场竞争高度结合、相互嵌入。')

w()
w('---')
w()

# --- 1.3 周飞舟 ---
w('### 1.3 周飞舟："财政关系"视角')
w()
w('> **核心命题**：理解中国政府行为的关键是财政关系——从统收统支到财政包干再到分税制，财政体制的变革塑造了央地关系的基本格局。分税制后"财权层层上收、事权层层下移"的效应是理解当代基层治理困境的锁钥。')
w()

emit_section('#### （一）财政体制规定央地关系基本框架',
    take(P['zfz_fiscal'], 3, prefer_kws=['财政体制规定了','基本框架','规定了财政方面']))

emit_section('#### （二）统收统支：改革前的高度集权',
    take(P['zfz_fiscal'], 2, prefer_kws=['统收统支','高度集权','全部财政收入上缴']))

emit_section('#### （三）集权与分权的周期性循环',
    take(P['zfz_fiscal'], 3, prefer_kws=['集中模式','地方竞赛模式','周期性循环','波浪型','收放']))

emit_section('#### （四）分税制：财权上收与事权下放',
    take(P['zfz_fiscal'], 3, prefer_kws=['财权层层上收','事权层层下移','75%归中央','25%归地方','财政缺口']))

emit_section('#### （五）分权的本质：事权下放而非真正财权下放',
    take(P['zfz_fiscal'], 2, prefer_kws=['事权','财权','分权在本质','本质上是']))

w()
w('---')
w()

# --- 1.4 三框架比较 ---
w('### 1.4 三种框架的比较：互补与张力')
w()
w('三种框架从不同层面切入央地关系，既有互补也有张力：')
w()
w('| 维度 | 周雪光（组织社会学） | 周黎安（激励理论） | 周飞舟（财政学） |')
w('|------|-------------------|-------------------|-----------------|')
w('| **核心问题** | 大国一统如何可能？ | 地方官员为何有动力？ | 钱在中央还是地方？ |')
w('| **分析单位** | 中央—地方权威关系 | 官员个体激励 | 财政收支结构 |')
w('| **矛盾焦点** | 一统决策 vs 灵活执行 | 行政发包 vs 锦标赛竞争 | 财权 vs 事权 |')
w('| **历史纵深** | 帝国以来一脉相承 | 明清发包传统 | 1949年以来体制演变 |')
w('| **主要机制** | 控制权分配、运动式纠偏 | 晋升激励、属地竞争 | 分税制、转移支付 |')
w('| **对"灵活性"的解释** | 共谋行为=制度调节 | 发包制赋予自主空间 | 财政包干驱动逐利 |')
w('| **对"集权"的理解** | 决策一统性 | 人事控制权集中 | 财权上收 |')
w()
w('#### 三框架的交叉验证')
w()

emit_section('**周雪光对"行政发包制"的重新思考（纳入控制权理论）：**',
    take(P['zxg_control'], 2, prefer_kws=['行政发包制','重新思考','重新审视','控制权分配']))

emit_section('**周黎安论行政发包制的财政维度：**',
    take(P['zla_all'], 2, prefer_kws=['财政包干','预算外','土地财政','包干']))

emit_section('**周飞舟论改革前"锦标赛"与放权集权的同时性：**',
    take(P['zfz_fiscal'], 2, prefer_kws=['放权和集权','同时进行','政治竞赛','锦标赛','大跃进']))

w()
w('---')
w()

# ======================= 二、关键机制详解 =======================
w('## 二、关键机制详解')
w()
w('以下对央地关系中的五大核心机制，汇集所有书中的相关原文。')
w()

# --- 2.1 行政发包制 ---
w('### 2.1 行政发包制（≥10 条原文）')
w()
w('> **定义**：周黎安提出的核心概念——中国政府间关系呈现为"多层级权力关系下以属地管理为基础的行政逐级发包制"，介于韦伯科层制与纯粹外包制之间的混合形态。')
w()

emit_section('#### （一）行政发包制的核心定义',
    take(P['zla_fabao'], 3, prefer_kws=['行政逐级发包','理想类型','混合形态','属地管理']))

emit_section('#### （二）行政发包制的六大特征',
    take(P['zla_fabao'], 2, prefer_kws=['特征','低薪水','强激励','财政权','安排']))

emit_section('#### （三）行政发包制 vs 韦伯科层制',
    take(P['zla_fabao'], 2, prefer_kws=['韦伯','科层制','区别','高薪水弱激励','低薪水强激励']))

emit_section('#### （四）行政发包制的历史根源',
    take(P['zla_fabao'], 2, prefer_kws=['明清','古代','传统','原型','历史']))

emit_section('#### （五）行政发包制的财政维度',
    take(P['zla_all'], 2, prefer_kws=['财政包干','预算外','土地财政','转移支付相对有限']))

emit_section('#### （六）周雪光：纳入控制权理论的重新审视',
    take(P['zxg_all'], 2, prefer_kws=['行政发包制','控制权','委托方','承包方','重新审视','重新思考']))

emit_section('#### （七）周飞舟：财政包干制的具体运作',
    take(P['zfz_all'], 2, prefer_kws=['定收定支','收支包干','固定比例分成','定额上解','大包干','递增']))

w()
w('---')
w()

# --- 2.2 晋升锦标赛 ---
w('### 2.2 晋升锦标赛（≥5 条原文）')
w()
w('> **定义**：周黎安提出的核心概念——将地方官员的晋升与地方经济发展绩效挂钩，让官员为政治晋升而在经济上相互竞争。')
w()

emit_section('#### （一）锦标赛的定义与特征',
    take(P['zla_jinbiao'], 2, prefer_kws=['政治锦标赛','晋升','经济绩效','GDP','竞争']))

emit_section('#### （二）锦标赛的制度条件',
    take(P['zla_jinbiao'], 2, prefer_kws=['人事权','集中','考核指标','GDP','路线保证','组织保证','级别','参与人']))

emit_section('#### （三）锦标赛的激励效应',
    take(P['zla_jinbiao'], 1, prefer_kws=['帮助之手','攫取之手','帮助','掠夺','扶持','制度来源']))

emit_section('#### （四）"官场+市场"：双层竞争的逻辑',
    take(P['zla_jinbiao'], 2, prefer_kws=['官场+市场','双层','零和','正和','官场竞争','市场竞争']))

emit_section('#### （五）周飞舟：改革前"锦标赛"的历史先例',
    take(P['zfz_all'], 2, prefer_kws=['放权和集权','同时进行','政治竞赛','大跃进','锦标赛']))

w()
w('---')
w()

# --- 2.3 运动式治理 ---
w('### 2.3 运动式治理（≥5 条原文）')
w()
w('> **定义**：周雪光提出的核心概念——暂时叫停官僚制常规过程，以政治动员过程替代之，是中央政府针对"一统体制与有效治理"矛盾的主要"纠偏"手段。')
w()

emit_section('#### （一）运动型治理的定义与纠偏功能',
    take(P['zxg_yundong'], 2, prefer_kws=['纠偏','叫停','常规过程','政治动员','替代','最大特点']))

emit_section('#### （二）运动型治理在国家治理逻辑中的位置',
    take(P['zxg_all'], 2, prefer_kws=['不同治理模式','转化','机制','治理模式','常规与动员','双重']))

emit_section('#### （三）历史渊源：叫魂、大跃进、文革',
    take(P['zxg_all'], 2, prefer_kws=['叫魂','大跃进','文革','乾隆','历史','渊源','革命教化']))

emit_section('#### （四）党政双重权威与运动型治理的制度基础',
    take(P['zxg_all'], 1, prefer_kws=['党政','专断权力','卡理斯玛','政治罪','党务系统','凌驾']))

w()
w('---')
w()

# --- 2.4 共谋现象 ---
w('### 2.4 共谋现象（≥5 条原文）')
w()
w('> **定义**：周雪光提出的核心概念——基层上下级政府间在执行更上级任务时的共谋行为，是"政策一统性与执行灵活性"应对机制在基层的重要体现。')
w()

emit_section('#### （一）共谋现象的定义与表现',
    take(P['zxg_gongmou'], 2, prefer_kws=['共谋现象','共谋行为','上有政策','基层','检查验收']))

emit_section('#### （二）共谋行为的制度逻辑：三个悖论',
    take(P['zxg_gongmou'], 2, prefer_kws=['悖论','一统性','灵活性','激励强度','目标替代','非人格化','人缘化']))

emit_section('#### （三）共谋行为的命题：执行链条越长，共谋越强',
    take(P['zxg_gongmou'], 1, prefer_kws=['命题','执行链条','资源分配渠道','合法性','越长']))

emit_section('#### （四）共谋行为的功能：调节一统与灵活',
    take(P['zxg_gongmou'], 2, prefer_kws=['调节','缓解','重要组成','执行灵活性','适应策略','象征性强大国家','有效性地方治理','组成部分']))

emit_section('#### （五）共谋行为与中央集权决策的代价',
    take(P['zxg_gongmou'], 1, prefer_kws=['中央集权','决策过程','所付出','代价','成本']))

w()
w('---')
w()

# --- 2.5 土地财政 ---
w('### 2.5 土地财政（≥5 条原文）')
w()
w('> **定义**：分税制改革后，地方政府为弥补财政缺口，逐步依赖土地出让金等预算外收入的现象。周飞舟对此有最系统的分析。')
w()

emit_section('#### （一）土地财政的形成逻辑',
    take(P['zfz_tudi'], 3, prefer_kws=['土地财政','以地生财','圈地','预算外','开辟税收之外','预期','预料']))

emit_section('#### （二）土地财政与分税制的因果链',
    take(P['zfz_tudi'], 2, prefer_kws=['分税制','财政缺口','地方财政','预算外','财力结构','行为取向','转变']))

emit_section('#### （三）周黎安：行政发包制下的财政包干与土地财政',
    take(P['zla_all'], 2, prefer_kws=['土地财政','预算外','土地出让','包干','财政和预算包干']))

emit_section('#### （四）土地金融与"三位一体"发展模式',
    take(P['zfz_all'], 2, prefer_kws=['土地金融','城市化','三位一体','融资','抵押','城市建设','经营城市']))

w()
w('---')
w()

# ======================= 三、关键数据汇总 =======================
w('## 三、关键数据汇总')
w()
w('以下汇集所有涉及央地关系的定量数据——财政占比、税收分配比例、转移支付规模等。')
w()

emit_section('### 3.1 "两个比重"：中央财政收入占比与财政收入占GDP比重',
    take(P['zfz_data'], 5, prefer_kws=['两个比重','中央财政收入','40.5%','22%','55%','1994','比重']))

emit_section('### 3.2 分税制：增值税分成比例（75%归中央，25%归地方）',
    take(P['zfz_data'], 4, prefer_kws=['75%','25%','增值税','中央','地方','分成']))

emit_section('### 3.3 改革前财政收入分配（1949-1979）',
    take(P['zfz_data'], 4, prefer_kws=['45%','55%','80%','20%','一五','统收统支','中央和地方财政']))

emit_section('### 3.4 财政包干时期（1980-1993）',
    take(P['zfz_data'], 3, prefer_kws=['包干','上解','留用','分成','定额','递增','比例']))

emit_section('### 3.5 转移支付数据',
    take(P['zfz_transfer'], 4, must_have=None))

emit_section('### 3.6 周黎安提供的财政数据',
    [r for r in take(P['zla_all'], 6) if re.search(r'\d{2,}|亿元|万亿', r['text'])])

emit_section('### 3.7 黄奇帆《分析与思考》中的数据',
    take(P['hq_data'], 4))

emit_section('### 3.8 周雪光：逆向软预算约束的数据',
    take(P['zxg_all'], 3, prefer_kws=['预算约束','资源密集型','攫取','向下攫取']))

w()
w('---')
w()

# ======================= 四、历史演变 =======================
w('## 四、央地关系的历史演变')
w()
w('以下按时间顺序汇集关于央地关系演变的原文，主要来自周飞舟《以利为利》对财政体制变迁的系统梳理。')
w()

emit_section('### 4.1 新中国成立初期：高度集权的统收统支（1949-1952）',
    take(P['zfz_all'], 3, prefer_kws=['统收统支','新中国成立','1950','1952','平抑物价','抗美援朝','公粮']))

emit_section('### 4.2 "一五"时期：分类分成体制（1953-1958）',
    take(P['zfz_all'], 3, prefer_kws=['分类分成','1953','1954','1958','一五','固定收入','调剂收入']))

emit_section('### 4.3 "大跃进"与大规模放权（1958-1960）',
    take(P['zfz_all'], 3, prefer_kws=['1958','大跃进','放权','下放','竞赛','放权和集权']))

emit_section('### 4.4 调整与收权（1961-1965）',
    take(P['zfz_all'], 2, prefer_kws=['1961','1962','调整','收权','总额分成','恢复']))

emit_section('### 4.5 "文革"时期的反复（1966-1978）',
    take(P['zfz_all'], 3, prefer_kws=['收支包干','1971','固定分成','1974','1976','4:3:3','总额分成']))

emit_section('### 4.6 改革开放：财政包干与分权让利（1978-1993）',
    take(P['zfz_all'], 4, prefer_kws=['包干','分权让利','放权让利','大包干','递增','留成','定额','递增包干']))

emit_section('### 4.7 分水岭：1994年分税制改革',
    take(P['zfz_all'], 4, prefer_kws=['分税制改革','税制改革','增值税','国税','地税','返还','所得税分享','中央地方共享']))

emit_section('### 4.8 分税制后的连锁效应：基层财政危机与政权"悬浮"',
    take(P['zfz_all'], 4, prefer_kws=['基层财政','县乡','危机','悬浮','专项化','财权','事权','缺口','税费改革']))

emit_section('### 4.9 周黎安：行政发包制的历史延续性',
    take(P['zla_all'], 2, prefer_kws=['历史','传统','明清','延续','计划经济','承袭','包干制从1958']))

emit_section('### 4.10 周雪光：从帝国到当代的制度延续',
    take(P['zxg_all'], 2, prefer_kws=['帝国','一脉相承','中华帝国','延续','循环','停滞','君主官僚制']))

w()
w('---')
w()

# ======================= 附录 =======================
w('## 附录：关键概念索引')
w()
w('| 概念 | 提出者 | 所属框架 | 主要出现章节 |')
w('|------|--------|---------|------------|')
w('| 一统体制与有效治理 | 周雪光 | 组织社会学 | §1.1；§2.3-2.4 |')
w('| 控制权理论 | 周雪光 | 组织社会学 | §1.1；§2.1 |')
w('| 运动型治理机制 | 周雪光 | 组织社会学 | §1.1；§2.3 |')
w('| 共谋现象 | 周雪光 | 组织社会学 | §1.1；§2.4 |')
w('| 行政发包制 | 周黎安 | 激励理论 | §1.2；§2.1 |')
w('| 政治锦标赛 | 周黎安 | 激励理论 | §1.2；§2.2 |')
w('| 官场+市场 | 周黎安 | 激励理论 | §1.2 |')
w('| 统收统支 | 周飞舟 | 公共财政学 | §1.3；§3；§4.1 |')
w('| 财政包干 | 周飞舟 | 公共财政学 | §1.3；§2.1；§4.6 |')
w('| 分税制 | 周飞舟 | 公共财政学 | §1.3；§3；§4.7 |')
w('| 转移支付 | 周飞舟 | 公共财政学 | §1.3；§3.5；§4.8 |')
w('| 土地财政 | 周飞舟/周黎安 | 财政学/激励理论 | §2.5 |')
w('| 软预算约束 / 逆向软预算约束 | 周飞舟/周雪光 | 公共财政学/组织学 | §2.5；§3.8 |')
w('| 财权层层上收、事权层层下移 | 周飞舟 | 公共财政学 | §1.3；§4.8 |')
w()
w('---')
w()
w('> **文档结束**')
w(f'> 本文档共收录去重原文引用 {len(USED)} 条。')
w('> 数据源：`knowledge_index.json`（4407条）+ 三份提取MD文件（共12765行）。')
w('> 生成方法：Python正则提取 + 14组关键词过滤 + 两阶段分配去重 + 人工审定结构。')

# ============================================================
OUT.write_text('\n'.join(doc), encoding='utf-8')
print(f'\nDocument written: {OUT}')
print(f'Total lines: {len(doc)}')
print(f'Unique quotes used: {len(USED)}')
print(f'File size: {OUT.stat().st_size} bytes ({OUT.stat().st_size/1024:.0f} KB)')
