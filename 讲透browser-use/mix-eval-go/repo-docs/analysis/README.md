# Mix-Eval-Go Analysis

Comprehensive analysis of authentication requirements and bypass strategies in browser automation evaluation tasks.

## Directory Structure

```
analysis/
├── scripts/              # Python analysis scripts
│   ├── extract_scraping_websites.py          # Extract target websites from tasks
│   ├── extract_auth_required_tasks.py        # Detect auth-required tasks
│   ├── analyze_auth_task_results.py          # Match tasks with evaluation results
│   └── extract_auth_bypass_methods.py        # Analyze bypass strategies
├── data/                 # Input datasets (read-only)
│   └── runs/
│       ├── PostHog Cleaned Feb 2026 (1).json # Task definitions (333 tasks)
│       └── Evals Export.json                  # Evaluation results (330 evals)
├── results/              # Generated analysis outputs
│   ├── websites/         # Website extraction results
│   ├── auth_detection/   # Authentication requirement detection
│   ├── completion_analysis/  # Success rate analysis
│   └── bypass_methods/   # Bypass strategy analysis
└── reports/              # Final documentation
    ├── EXECUTIVE_SUMMARY.md                   # 1,431-word comprehensive summary
    └── auth_bypass_comprehensive_report.md    # Detailed bypass method analysis
```

## Quick Start

All scripts should be run from the `analysis/` directory:

```bash
cd analysis

# 1. Extract target websites from tasks
uv run scripts/extract_scraping_websites.py

# 2. Detect authentication-required tasks
uv run scripts/extract_auth_required_tasks.py

# 3. Analyze completion rates
uv run scripts/analyze_auth_task_results.py

# 4. Analyze bypass methods
uv run scripts/extract_auth_bypass_methods.py
```

## Analysis Pipeline

### Step 1: Website Extraction
**Script:** `scripts/extract_scraping_websites.py`
**Input:** `data/runs/PostHog Cleaned Feb 2026 (1).json`
**Output:**
- `results/websites/direct_web_scraping_websites.txt` - Human-readable summary
- `results/websites/direct_web_scraping_websites_detailed.json` - Full data with task mappings

**Findings:** 204 unique domains across 201 Direct Web Scraping tasks

### Step 2: Authentication Detection
**Script:** `scripts/extract_auth_required_tasks.py`
**Input:** `data/runs/PostHog Cleaned Feb 2026 (1).json`
**Output:**
- `results/auth_detection/auth_required_tasks.txt` - Task breakdown by confidence
- `results/auth_detection/auth_required_tasks_detailed.json` - Full task details

**Method:**
- Platform knowledge base (30+ known auth-required platforms)
- Keyword analysis (login, credentials, authentication, etc.)

**Findings:** 45 auth-required tasks (28 HIGH, 5 MEDIUM, 12 LOW confidence)

### Step 3: Completion Analysis
**Script:** `scripts/analyze_auth_task_results.py`
**Input:**
- `results/auth_detection/auth_required_tasks_detailed.json`
- `data/runs/Evals Export.json`

**Output:**
- `results/completion_analysis/auth_task_completion_analysis.txt` - Success rates
- `results/completion_analysis/auth_task_completion_detailed.json` - Full match data

**Findings:** 13/45 tasks evaluated, 53.8% pass rate (7 PASS, 4 FAIL, 2 UNCLEAR)

### Step 4: Bypass Method Analysis
**Script:** `scripts/extract_auth_bypass_methods.py`
**Input:**
- `results/auth_detection/auth_required_tasks_detailed.json`
- `data/runs/Evals Export.json`

**Output:** `results/bypass_methods/auth_bypass_methods.txt`

**Findings:** 3 bypass strategies identified (Public Access, Third-Party Proxy, Platform Substitution)

## Key Findings

### Authentication Requirements
- **22.4%** of Direct Web Scraping tasks flagged as auth-required (45/201)
- **50% false positive rate** - data was actually publicly accessible
- Only **1 task** (Instagram) had genuine login wall in evaluated set

### Success Rates
- **53.8% overall pass rate** for auth-required tasks (7/13)
- **100% agent self-report** vs **54% judge confirmation**
- **Public data access:** 100% success (4/4 tasks)
- **Third-party proxies:** 100% success (1/1 task)
- **Platform substitution:** 0% success (0/3 tasks)

### Bypass Strategies

#### ✅ Strategy 1: Public Data Access (100% success)
Platforms flagged as auth-required but data was legally public:
- **SEC.gov** - EDGAR filings (public by law)
- **NSE India** - Stock exchange disclosures (regulatory requirement)
- **UK Contracts Finder** - Government procurement (transparency mandate)
- **TenderNED** - EU tender listings (procurement directive)

#### ✅ Strategy 2: Third-Party Proxy (100% success)
- **Instagram via Inflact.com** - Downloader service handles authentication
- Service maintains authenticated sessions, provides public interface
- Agent never directly accesses Instagram

#### ❌ Strategy 3: Platform Substitution (0% success)
- **Zillow → Craigslist** - Wrong platform, rejected
- **Redfin → Trulia/Google** - Wrong platform, rejected
- **eProcure India → data.gov.in** - Incomplete data, rejected

Judges require exact platform specified, no substitutions accepted.

## Common Misconceptions

### "Authentication Required" Often Means:
1. **Public regulatory data** - Legally must be accessible (SEC, stock exchanges)
2. **Freemium model** - Basic features public, premium needs login
3. **Bot detection** - Anti-scraping measures, not authentication
4. **CAPTCHA challenges** - Human verification, not login

### Bot Detection ≠ Authentication
Real estate sites (Zillow, Redfin) failed due to:
- Cloudflare protection
- Browser fingerprinting
- Rate limiting

**Not** due to authentication requirements.

## Recommendations

### For Task Design
- Separate public regulatory data from genuinely auth-required tasks
- Clearly distinguish authentication from bot detection challenges
- Test credential injection capabilities explicitly
- Use specific auth-required platforms (paywalls, SaaS, social media)

### For Evaluation
- Reduce keyword-based detection (50% false positive rate)
- Expand coverage beyond 28.9% of auth-required tasks
- Distinguish between bypass strategies in scoring
- Don't accept platform substitution as valid completion

### For Agent Development
**Can do without credentials:**
- Scrape public regulatory/government data
- Use third-party proxy/downloader services
- Access freemium platforms' public pages

**Cannot do without credentials:**
- Bypass sophisticated bot detection
- Solve CAPTCHAs reliably
- Access genuinely authenticated content
- Substitute platforms (judges reject)

## Reports

### Executive Summary
**File:** `reports/EXECUTIVE_SUMMARY.md`
**Length:** 1,431 words (Plan: 181 words)
**Content:** Complete self-contained analysis from dataset overview through findings and recommendations

### Detailed Bypass Analysis
**File:** `reports/auth_bypass_comprehensive_report.md`
**Content:** In-depth examination of each bypass strategy with case studies and technical details

## Dependencies

- Python 3.x
- `uv` for script execution
- Standard library only (no external packages)

## Notes

- All scripts use relative paths from `analysis/` directory
- Results can be regenerated by running scripts in order
- Input data in `data/runs/` is read-only, never modified
- All analysis outputs are deterministic (same inputs → same outputs)
