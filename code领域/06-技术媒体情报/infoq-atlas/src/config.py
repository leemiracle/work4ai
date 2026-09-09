"""项目全局路径与配置。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DATA = ROOT / "data"
RAW = DATA / "raw"
RAW_TOPICS = RAW / "topics"
RAW_LISTS = RAW / "lists"          # 每个 topic 的文章列表 JSON
RAW_ARTICLES = RAW / "articles"    # 每篇文章的详情+正文
PROCESSED = DATA / "processed"
REPORTS = ROOT / "reports"
REPORT_TOPICS = REPORTS / "topics"
REPORT_GLOBAL = REPORTS / "global"
DASHBOARD = ROOT / "dashboard"
ASSETS = ROOT / "assets"
NOTES = ROOT / "notes"
DB_PATH = PROCESSED / "infoq.db"

for p in [RAW_TOPICS, RAW_LISTS, RAW_ARTICLES, PROCESSED, REPORT_TOPICS,
          REPORT_GLOBAL, DASHBOARD, ASSETS, NOTES]:
    p.mkdir(parents=True, exist_ok=True)

# InfoQ API
API_BASE = "https://www.infoq.cn/public/v1/"
STATIC_BASE = "https://static001.infoq.cn"
SITE = "https://www.infoq.cn"

# 爬取节流（秒）。InfoQ 对 public API 较宽松，仍保持礼貌。
LIST_PAGE_SIZE = 30          # 列表每页
LIST_DELAY = 0.25
DETAIL_DELAY = 0.15
CONTENT_DELAY = 0.1
MAX_RETRIES = 4
HTTP_TIMEOUT = 25

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
