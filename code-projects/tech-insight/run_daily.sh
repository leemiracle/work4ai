#!/bin/bash
# TechInsight 每日运行脚本 - 采集 + 分析 + 报告
# 用法: ./run_daily.sh 或通过 cron 定时执行

set -e
cd "$(dirname "$0")"

echo "=========================================="
echo "TechInsight 每日运行 $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="

# 阶段1: 采集（不增强内容，快速入库）
echo "[1/3] 数据采集..."
python run.py collect 2>&1 | grep -E "(采集完成|篇)" || true

# 阶段2: 内容增强（仅对摘要过短的文章获取全文，限制50篇）
echo "[2/3] 内容增强..."
python -c "
import logging, sys
sys.path.insert(0, '.')
logging.basicConfig(level=logging.INFO, format='%(message)s')
from src.storage.database import get_all_articles, save_article, init_db
from src.collectors.enricher import ContentEnricher
from src.storage.models import Article
init_db()
enricher = ContentEnricher()
articles = get_all_articles(limit=300)
enriched = 0
for a in articles:
    if enriched >= 30:
        break
    if len(a.get('content','')) < 200 and a.get('url','').startswith('http'):
        full = enricher.enrich_webpage(a['url'])
        if full and len(full) > 200:
            a['content'] = full
            art = Article(
                id=a['id'], source=a['source'], source_name=a['source_name'],
                title=a['title'], url=a['url'], uuid=a.get('uuid',''),
                summary=full[:500], content=full,
                category=a.get('category',''), author=a.get('author',''),
                published_at=a.get('published_at',''),
            )
            save_article(art)
            enriched += 1
print(f'增强完成: {enriched}篇')
" 2>&1 || true

# 阶段3: 分析 + 报告
echo "[3/3] 深度分析 + 报告生成..."
python run.py analyze --max-articles 300 2>&1 | grep -E "(完成|报告)" || true

echo ""
echo "=========================================="
echo "运行完成 $(date '+%Y-%m-%d %H:%M')"
echo "=========================================="
python run.py stats 2>&1 || true
