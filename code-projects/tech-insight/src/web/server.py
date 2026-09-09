"""FastAPI Web 服务 - 数据仪表盘 + 知识图谱可视化 + RAG 问答"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..config import Config
from ..collectors.factory import collect_all, collect_from, get_all_source_keys
from ..storage.database import get_all_articles, get_stats, init_db
from ..storage.models import Article
from ..storage.database import save_article

logger = logging.getLogger(__name__)

app = FastAPI(title="TechInsight", description="技术媒体洞察平台")


class CollectRequest(BaseModel):
    source: Optional[str] = None
    priority: Optional[int] = None


class QARequest(BaseModel):
    question: str
    top_k: int = 5


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    stats = get_stats()
    return _render_dashboard(stats)


@app.get("/api/stats")
async def api_stats():
    return get_stats()


@app.get("/api/sources")
async def api_sources():
    sources = Config.sources()["sources"]
    return {
        key: {
            "name": cfg.get("name", key),
            "type": cfg.get("type", "web"),
            "priority": cfg.get("priority", 5),
            "url": cfg.get("url", ""),
            "tags": cfg.get("tags", []),
        }
        for key, cfg in sources.items()
    }


@app.get("/api/articles")
async def api_articles(
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    days: Optional[int] = None,
):
    articles = get_all_articles(limit=limit + offset, source=source, days=days)
    return articles[offset:offset + limit]


@app.post("/api/collect")
async def api_collect(req: CollectRequest):
    """触发采集"""
    try:
        if req.source:
            articles = collect_from(req.source)
            saved = _save_articles(articles)
            return {"source": req.source, "collected": len(articles), "saved": saved}
        else:
            results = collect_all(priority=req.priority)
            total_collected = sum(len(v) for v in results.values())
            total_saved = sum(_save_articles(v) for v in results.values())
            return {
                "sources": {k: len(v) for k, v in results.items()},
                "total_collected": total_collected,
                "total_saved": total_saved,
            }
    except Exception as e:
        logger.exception("采集失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/qa")
async def api_qa(req: QARequest):
    """RAG 问答"""
    try:
        from ..rag.qa import RAGEngine

        engine = RAGEngine()
        result = engine.answer(req.question, top_k=req.top_k)
        return result
    except Exception as e:
        logger.exception("问答失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def api_analyze():
    """运行完整分析管道并生成报告"""
    try:
        from ..pipeline import run_analysis_pipeline

        results = run_analysis_pipeline()
        return results
    except Exception as e:
        logger.exception("分析失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports")
async def api_list_reports():
    """列出已生成报告"""
    settings = Config.settings()
    report_dir = Config.base_dir() / settings["storage"]["reports_path"]
    if not report_dir.exists():
        return {"reports": []}
    reports = []
    for f in sorted(report_dir.glob("*.md"), reverse=True):
        reports.append({
            "name": f.name,
            "path": str(f),
            "size": f.stat().st_size,
        })
    return {"reports": reports[:50]}


@app.get("/api/reports/{name}")
async def api_get_report(name: str):
    """获取报告内容"""
    settings = Config.settings()
    report_dir = Config.base_dir() / settings["storage"]["reports_path"]
    filepath = report_dir / name
    if not filepath.exists() or not filepath.suffix == ".md":
        raise HTTPException(status_code=404, detail="报告不存在")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return JSONResponse(content={"name": name, "content": content})


def _save_articles(articles: list[Article]) -> int:
    saved = 0
    for article in articles:
        try:
            save_article(article)
            saved += 1
        except Exception as e:
            logger.warning(f"保存失败 {article.url}: {e}")
    return saved


def _render_dashboard(stats: dict) -> str:
    source_list = get_all_source_keys()
    by_source_html = "".join(
        f'<div class="source-bar"><span>{s}</span><span class="count">{stats["by_source"].get(s, 0)}</span></div>'
        for s in source_list
    )
    return _DASHBOARD_HTML.format(
        total=stats["total_articles"],
        analyzed=stats["analyzed_articles"],
        entities=stats["entities"],
        relations=stats["relations"],
        by_source_html=by_source_html,
        sources_json=json.dumps(source_list),
    )


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TechInsight - 技术媒体洞察平台</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: -apple-system, "Segoe UI", Roboto, sans-serif; background:#0f1117; color:#e0e0e0; }}
.header {{ background:linear-gradient(135deg,#1a1d29,#2a2d3a); padding:20px 30px; border-bottom:1px solid #333; }}
.header h1 {{ font-size:24px; }}
.header .subtitle {{ color:#888; font-size:14px; margin-top:5px; }}
.container {{ max-width:1400px; margin:0 auto; padding:20px; }}
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }}
.card {{ background:#1a1d29; border:1px solid #2a2d3a; border-radius:12px; padding:20px; }}
.card .label {{ color:#888; font-size:13px; margin-bottom:8px; }}
.card .value {{ font-size:32px; font-weight:700; color:#61dafb; }}
.card.green .value {{ color:#4ade80; }}
.card.yellow .value {{ color:#fbbf24; }}
.card.purple .value {{ color:#c084fc; }}
.section {{ background:#1a1d29; border:1px solid #2a2d3a; border-radius:12px; padding:20px; margin-bottom:24px; }}
.section h2 {{ font-size:18px; margin-bottom:16px; color:#61dafb; }}
.sources-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:10px; }}
.source-bar {{ display:flex; justify-content:space-between; padding:8px 12px; background:#0f1117; border-radius:8px; font-size:14px; }}
.source-bar .count {{ color:#61dafb; font-weight:600; }}
.controls {{ display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap; }}
button {{ background:#2563eb; color:#fff; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-size:14px; transition:background .2s; }}
button:hover {{ background:#1d4ed8; }}
button:disabled {{ background:#555; cursor:wait; }}
button.secondary {{ background:#374151; }}
button.secondary:hover {{ background:#4b5563; }}
.qa-box {{ margin-top:16px; }}
.qa-box textarea {{ width:100%; background:#0f1117; color:#e0e0e0; border:1px solid #333; border-radius:8px; padding:12px; font-size:14px; resize:vertical; }}
.answer {{ background:#0f1117; border-radius:8px; padding:16px; margin-top:12px; white-space:pre-wrap; line-height:1.6; display:none; }}
.answer.show {{ display:block; }}
.sources-list {{ margin-top:8px; font-size:12px; color:#888; }}
.status {{ padding:8px 16px; border-radius:8px; font-size:13px; display:none; }}
.status.show {{ display:inline-block; }}
.status.success {{ background:#064e3b; color:#4ade80; }}
.status.error {{ background:#7f1d1d; color:#f87171; }}
.status.loading {{ background:#1e3a5f; color:#61dafb; }}
</style>
</head>
<body>
<div class="header">
<h1>TechInsight 技术媒体洞察平台</h1>
<div class="subtitle">InfoQ + 12+ 技术媒体 | 知识图谱 | 趋势分析 | AI 机会识别 | RAG 问答</div>
</div>
<div class="container">
<div class="grid">
<div class="card"><div class="label">采集文章</div><div class="value">{total}</div></div>
<div class="card green"><div class="label">已分析</div><div class="value">{analyzed}</div></div>
<div class="card yellow"><div class="label">知识实体</div><div class="value">{entities}</div></div>
<div class="card purple"><div class="label">实体关系</div><div class="value">{relations}</div></div>
</div>

<div class="controls">
<button onclick="collectAll()">采集全部</button>
<button class="secondary" onclick="collectInfoQ()">仅采集 InfoQ</button>
<button class="secondary" onclick="runAnalysis()">运行深度分析</button>
<button class="secondary" onclick="loadReports()">查看报告</button>
<span id="status" class="status"></span>
</div>

<div class="section">
<h2>数据源采集量</h2>
<div class="sources-grid">{by_source_html}</div>
</div>

<div class="section">
<h2>RAG 智能问答</h2>
<div class="qa-box">
<textarea id="question" rows="3" placeholder="输入问题，如：大模型应用落地的关键技术有哪些？RAG 和微调各自的优缺点？">当前最值得关注的技术趋势是什么？</textarea>
<div style="margin-top:8px;">
<button onclick="askQuestion()">提问</button>
</div>
<div id="answer" class="answer"></div>
</div>
</div>

<div class="section" id="reports-section" style="display:none;">
<h2>已生成报告</h2>
<div id="reports-list"></div>
</div>
</div>

<script>
const API = '';
function setStatus(msg, type) {{
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = 'status show ' + (type || 'loading');
}}
function clearStatus() {{ document.getElementById('status').className = 'status'; }}

async function collectAll() {{
  setStatus('采集中...', 'loading');
  try {{
    const resp = await fetch(API + '/api/collect', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{}})}});
    const data = await resp.json();
    setStatus(`采集完成: ${{data.total_collected}}篇, 新增 ${{data.total_saved}}篇`, 'success');
    setTimeout(() => location.reload(), 2000);
  }} catch(e) {{ setStatus('采集失败: ' + e.message, 'error'); }}
}}

async function collectInfoQ() {{
  setStatus('采集 InfoQ...', 'loading');
  try {{
    const resp = await fetch(API + '/api/collect', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{source:'infoq'}})}});
    const data = await resp.json();
    setStatus(`InfoQ采集: ${{data.collected}}篇, 新增 ${{data.saved}}篇`, 'success');
    setTimeout(() => location.reload(), 2000);
  }} catch(e) {{ setStatus('采集失败: ' + e.message, 'error'); }}
}}

async function runAnalysis() {{
  setStatus('深度分析中（可能需要几分钟）...', 'loading');
  try {{
    const resp = await fetch(API + '/api/analyze', {{method:'POST'}});
    if (resp.ok) {{
      const data = await resp.json();
      setStatus(`分析完成，生成 ${{data.reports ? Object.keys(data.reports).length : 0}} 份报告`, 'success');
    }} else {{
      const text = await resp.text();
      setStatus('分析失败: ' + text, 'error');
    }}
  }} catch(e) {{ setStatus('分析失败: ' + e.message, 'error'); }}
}}

async function askQuestion() {{
  const q = document.getElementById('question').value.trim();
  if (!q) return;
  const answerEl = document.getElementById('answer');
  answerEl.className = 'answer show';
  answerEl.textContent = '思考中...';
  setStatus('问答中...', 'loading');
  try {{
    const resp = await fetch(API + '/api/qa', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{question:q}})}});
    const data = await resp.json();
    let html = data.answer || '无回答';
    if (data.sources && data.sources.length) {{
      html += '\\n\\n---\\n参考来源:\\n';
      data.sources.forEach((s,i) => {{
        html += `[${{i+1}}] (相关度:${{(s.score*100).toFixed(0)}}%) ${{s.text.substring(0,100)}}...\\n`;
      }});
    }}
    answerEl.textContent = html;
    clearStatus();
  }} catch(e) {{
    answerEl.textContent = '错误: ' + e.message;
    setStatus('问答失败', 'error');
  }}
}}

async function loadReports() {{
  const section = document.getElementById('reports-section');
  section.style.display = 'block';
  const list = document.getElementById('reports-list');
  list.innerHTML = '加载中...';
  try {{
    const resp = await fetch(API + '/api/reports');
    const data = await resp.json();
    if (!data.reports || data.reports.length === 0) {{
      list.innerHTML = '<p>暂无报告，请先运行分析</p>';
      return;
    }}
    list.innerHTML = data.reports.map(r => `
      <div style="padding:10px;border-bottom:1px solid #2a2d3a;">
        <a href="#" onclick="loadReport('${{r.name}}');return false;" style="color:#61dafb;text-decoration:none;">📄 ${{r.name}}</a>
        <span style="color:#888;font-size:12px;margin-left:10px;">(${{(r.size/1024).toFixed(1)}}KB)</span>
      </div>
    `).join('');
  }} catch(e) {{ list.innerHTML = '加载失败: ' + e.message; }}
}}

async function loadReport(name) {{
  try {{
    const resp = await fetch(API + '/api/reports/' + name);
    const data = await resp.json();
    const w = window.open('', '_blank');
    w.document.write(`<html><head><meta charset="UTF-8"><title>${{name}}</title>
      <style>body{{font-family:sans-serif;max-width:900px;margin:40px auto;padding:20px;line-height:1.8;}}table{{border-collapse:collapse;width:100%;}}th,td{{border:1px solid #ddd;padding:8px;text-align:left;}}</style>
      </head><body><div id="content"></div></body></html>`);
    const rendered = marked ? marked.parse(data.content) : '<pre>' + data.content + '</pre>';
    w.document.getElementById('content').innerHTML = rendered;
  }} catch(e) {{ alert('加载失败: ' + e.message); }}
}}
</script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</body>
</html>
"""
