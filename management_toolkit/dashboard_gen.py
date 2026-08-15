"""
生成自包含 HTML Dashboard —— 零依赖, 浏览器直接打开
- 嵌入全部 PNG 图 (base64)
- 纯 JS 交互计算器: EOQ / NPV / EMV / 报童 / 牛鞭放大比
- 思想地图 + 算法速查
"""
import base64, os

DIR = "/tmp/opencode/management_toolkit"
IMGS = ["dupont.png", "ahp.png", "porter_radar.png", "bsc.png",
        "beer_game.png", "ona_karate.png", "systems_dynamics.png", "pert_risk.png"]


def b64(name):
    p = os.path.join(DIR, name)
    if os.path.exists(p):
        return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    return ""


imgs_html = "".join(
    f'<figure><figcaption>{n}</figcaption><img src="{b64(n)}"></figure>'
    for n in IMGS if b64(n))

HTML = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>管理学量化 Dashboard</title>
<style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#0f1419;color:#e6e6e6;}}
header{{background:linear-gradient(90deg,#1f6feb,#a371f7);padding:20px;text-align:center;}}
h1{{margin:0;font-size:1.5em}} h2{{color:#79c0ff;border-bottom:1px solid #30363d;padding-bottom:6px}}
nav{{display:flex;justify-content:center;background:#161b22;padding:10px;position:sticky;top:0;z-index:10}}
nav button{{background:#21262b;color:#e6e6e6;border:1px solid #30363d;padding:8px 16px;margin:0 4px;border-radius:6px;cursor:pointer}}
nav button.active{{background:#1f6feb;border-color:#1f6feb}}
.tab{{display:none;padding:20px;max-width:1200px;margin:0 auto}}
.tab.active{{display:block}}
figure{{display:inline-block;width:48%;vertical-align:top;margin:8px 1%;background:#161b22;padding:10px;border-radius:8px}}
figcaption{{color:#79c0ff;font-size:.85em;margin-bottom:6px;text-align:center}}
img{{width:100%;border-radius:4px}}
.calc{{background:#161b22;padding:16px;border-radius:8px;margin:12px 0}}
.calc label{{display:inline-block;width:180px}} 
input{{background:#0d1117;color:#e6e6e6;border:1px solid #30363d;padding:6px;border-radius:4px;width:120px}}
.result{{color:#7ee787;font-weight:bold;font-size:1.1em;margin-top:8px}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}
td,th{{border:1px solid #30363d;padding:8px;text-align:left}} th{{background:#21262b}}
code{{background:#21262b;padding:2px 6px;border-radius:3px;color:#f0883e}}
.map{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}}
.card{{background:#161b22;padding:14px;border-radius:8px;border-left:3px solid #1f6feb}}
</style></head><body>
<header><h1>管理学量化武器库 · 交互 Dashboard</h1>
<p style="opacity:.85">全·深·多视角 · 含全部算法 · 仿真验证 · 零依赖单文件</p></header>
<nav>
<button class="active" onclick="show('calc')">交互计算器</button>
<button onclick="show('viz')">可视化图集</button>
<button onclick="show('map')">思想地图</button>
<button onclick="show('algo')">算法速查</button>
</nav>

<div id="calc" class="tab active">
<h2>交互计算器 (纯浏览器, 实时)</h2>
<div class="calc"><h3>经济订货量 EOQ</h3>
<label>年需求 D:</label><input id="eoqD" value="10000" oninput="eoq()"><br>
<label>每次订货成本 S:</label><input id="eoqS" value="50" oninput="eoq()"><br>
<label>单位持有成本 H:</label><input id="eoqH" value="2" oninput="eoq()"><br>
<div class="result" id="eoqR"></div></div>

<div class="calc"><h3>净现值 NPV</h3>
<label>现金流(逗号分隔):</label><input id="npvCF" value="-1000,300,400,500,600" style="width:300px" oninput="npv()"><br>
<label>折现率 r (%):</label><input id="npvR" value="10" oninput="npv()"><br>
<div class="result" id="npvR2"></div></div>

<div class="calc"><h3>期望货币价值 EMV (两方案两状态)</h3>
<label>方案A 高需求收益:</label><input id="emvAh" value="200" oninput="emv()"><br>
<label>方案A 低需求收益:</label><input id="emvAl" value="-20" oninput="emv()"><br>
<label>方案B 高需求收益:</label><input id="emvBh" value="60" oninput="emv()"><br>
<label>方案B 低需求收益:</label><input id="emvBl" value="20" oninput="emv()"><br>
<label>P(高需求):</label><input id="emvP" value="0.6" oninput="emv()"><br>
<div class="result" id="emvR"></div></div>

<div class="calc"><h3>报童关键比率 (Newsvendor CR)</h3>
<label>售价 p:</label><input id="nvP" value="30" oninput="nv()"><br>
<label>进价 c:</label><input id="nvC" value="18" oninput="nv()"><br>
<label>残值 s:</label><input id="nvS" value="6" oninput="nv()"><br>
<div class="result" id="nvR"></div></div>

<div class="calc"><h3>牛鞭放大比 (方差逐级)</h3>
<label>级数:</label><input id="bwN" value="4" oninput="bw()"><br>
<label>每级平均放大 (倍):</label><input id="bwK" value="5" oninput="bw()"><br>
<div class="result" id="bwR"></div></div>
</div>

<div id="viz" class="tab"><h2>可视化图集</h2>{imgs_html}</div>

<div id="map" class="tab"><h2>管理学思想地图</h2>
<div class="map">
<div class="card"><b>科学管理 (泰勒 1911)</b><br>时间动作研究·计件工资·one best way</div>
<div class="card"><b>科层制 (韦伯)</b><br>法理权威·层级·规章 → 铁笼</div>
<div class="card"><b>人际关系 (梅奥 霍桑)</b><br>士气·非正式组织·社会人</div>
<div class="card"><b>决策学派 (西蒙 1947)</b><br>有限理性·满意原则·EMV/AHP/贝叶斯</div>
<div class="card"><b>系统/权变</b><br>开放系统·视情境而定</div>
<div class="card"><b>交易成本 (Coase/Williamson)</b><br>企业边界 = 内部成本 vs 市场成本</div>
<div class="card"><b>委托代理/机制设计</b><br>信息不对称·激励相容·拍卖</div>
<div class="card"><b>RBV + 动态能力</b><br>VRIO·sensing/seizing/reconfiguring</div>
<div class="card"><b>波特竞争战略</b><br>五力·价值链·三通用战略</div>
<div class="card"><b>学习/知识 (圣吉/野中)</b><br>系统思考·SECI·双元组织</div>
<div class="card"><b>质量/精益 (戴明/TPS)</b><br>PDCA·JIT·六西格玛·田口</div>
<div class="card"><b>AI/算法管理 (新)</b><br>六机制·HITL·augmentation</div>
</div></div>

<div id="algo" class="tab"><h2>算法速查表</h2>
<table><tr><th>类别</th><th>算法</th><th>用途</th><th>关键公式/结论</th></tr>
<tr><td rowspan=4>决策</td><td>EMV</td><td>风险决策</td><td>Σ pᵢ·收益ᵢ</td></tr>
<tr><td>EVPI</td><td>信息价值</td><td>确定期望 − EMV</td></tr>
<tr><td>贝叶斯</td><td>更新先验</td><td>P(H|E)=P(E|H)P(H)/P(E)</td></tr>
<tr><td>AHP</td><td>多准则权重</td><td>最大特征向量·CR&lt;0.1</td></tr>
<tr><td rowspan=5>运筹</td><td>LP</td><td>资源配置</td><td>单纯形法</td></tr>
<tr><td>CPM</td><td>项目工期</td><td>松弛=0 的路径</td></tr>
<tr><td>EOQ</td><td>库存</td><td>Q*=√(2DS/H)</td></tr>
<tr><td>M/M/1</td><td>排队</td><td>L=ρ/(1−ρ)</td></tr>
<tr><td>报童</td><td>易逝品</td><td>CR=cu/(cu+co)</td></tr>
<tr><td rowspan=3>财务</td><td>NPV/IRR</td><td>投资决策</td><td>Σ CFₜ/(1+r)ᵗ</td></tr>
<tr><td>CAPM</td><td>权益成本</td><td>rf+β(E(Rm)−rf)</td></tr>
<tr><td>杜邦</td><td>ROE分解</td><td>净利率×周转×权益乘数</td></tr>
<tr><td rowspan=2>质量</td><td>六西格玛</td><td>减变异</td><td>DPMO·3.4ppm</td></tr>
<tr><td>田口</td><td>损失</td><td>L=k(x−m)²</td></tr>
<tr><td rowspan=3>组织/系统</td><td>ONA</td><td>非正式网络</td><td>中心性+社区</td></tr>
<tr><td>系统动力学</td><td>反馈延迟</td><td>牛鞭=方差放大</td></tr>
<tr><td>博弈</td><td>策略互动</td><td>纳什均衡·DSIC·收益等价</td></tr>
</table></div>

<script>
function show(id){{document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));document.querySelectorAll('nav button').forEach(b=>b.classList.remove('active'));event.target.classList.add('active');document.getElementById(id).classList.add('active');}}
function v(id){{return parseFloat(document.getElementById(id).value);}}
function eoq(){{var D=v('eoqD'),S=v('eoqS'),H=v('eoqH');var Q=Math.sqrt(2*D*S/H);document.getElementById('eoqR').textContent='EOQ = '+Q.toFixed(1)+' 件, 年订货 '+(D/Q).toFixed(1)+' 次, 总库存成本='+(Q/2*H+D/Q*S).toFixed(1);}}
function npv(){{var cf=document.getElementById('npvCF').value.split(',').map(Number);var r=v('npvR')/100;var n=cf.reduce((a,c,t)=>a+c/Math.pow(1+r,t),0);document.getElementById('npvR2').textContent='NPV = '+n.toFixed(2)+(n>0?'  ✓ 接受':'  ✗ 拒绝');}}
function emv(){{var Ah=v('emvAh'),Al=v('emvAl'),Bh=v('emvBh'),Bl=v('emvBl'),p=v('emvP');var A=p*Ah+(1-p)*Al,B=p*Bh+(1-p)*Bl;document.getElementById('emvR').textContent='EMV(A)='+A.toFixed(1)+'  EMV(B)='+B.toFixed(1)+'  → 选'+(A>B?'A':'B');}}
function nv(){{var p=v('nvP'),c=v('nvC'),s=v('nvS');var cu=p-c,co=c-s,CR=cu/(cu+co);document.getElementById('nvR').textContent='CR='+CR.toFixed(3)+'  → 最优订货量=需求分布的'+(CR*100).toFixed(0)+'分位';}}
function bw(){{var n=v('bwN'),k=v('bwK');document.getElementById('bwR').textContent='终端需求方差 → 上游订单方差放大 '+Math.pow(k,n).toFixed(0)+' 倍 (牛鞭!)';}}
eoq();npv();emv();nv();bw();
</script>
</body></html>"""

out = os.path.join(DIR, "dashboard.html")
open(out, "w").write(HTML)
print(f"Dashboard 已生成: {out}  ({len(HTML)//1024} KB)")
print("打开方式: 浏览器直接打开该 HTML 文件 (自包含, 无需服务器)")
