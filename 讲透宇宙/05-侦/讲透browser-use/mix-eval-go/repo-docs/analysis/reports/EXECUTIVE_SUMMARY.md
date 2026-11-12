# Mix-Eval-Go Authentication Analysis - Executive Summary

## Plan & Objectives

This analysis examines authentication requirements and bypass strategies in the Mix-Eval-Go browser automation evaluation dataset. The goal was to understand how agents complete web scraping tasks when platforms require login credentials that agents don't possess.

**Analysis Pipeline:**
1. **Dataset Characterization*V◊ - Analyzed task distribution across 8 categories (333 total tasks)
2. **Website Extraction** - Identified 204 unique domains targeted for Direct Web Scraping tasks
3. **Authentication Detection** - Manual review of all 201 Direct Web Scraping tasks to identify genuine authentication requirements
4. **Success Rate Evaluation** - Matched auth-required tasks against evaluation results to measure completion rates
5. **Bypass Method Analysis** - Investigated how agents successfully completed tasks without credentials

**Key Questions Addressed:**
- How many tasks require authentication?
- What platforms are most commonly targeted?
- Can agents complete auth-required tasks without credentials?
- What bypass strategies do agents employ?
- Which strategies succeed and which fail?

**Outcome:** Authentication barriers are rare in browser automation evaluations. Only 9-11% of tasks genuinely require login credentials. Most data is legally public or accessible through third-party proxy services.

---

## Dataset Overview

### Task Distribution

The PostHog Cleaned Feb 2026 dataset contains **333 evaluation tasks** across 8 categories:

| Category | Count | Percentage |
|----------|-------|------------|
| **Direct Web Scraping** | 201 | 60.4% |
| Web Research | 59 | 17.7% |
| Search | 27 | 8.1% |
| Search Results Extracting | 21 | 6.3% |
| Price Scraping | 17 | 5.1% |
| UI Testing | 6 | 1.8% |
| Social Media Interactions | 1 | 0.3% |
| File Download | 1 | 0.3% |

Direct Web Scraping dominates the dataset at 60.4%, making it the primary focus of this analysis.

### Target Platforms

From 201 Direct Web Scraping tasks, we extracted **511 URLs** referencing **204 unique domains**.

**Top targets:** github.com (28), bhphotovideo.com (12), google.com (10), nvd.nist.gov (10), instagram.com (9), sec.gov (9), amazon.com (8). Platform diversity includes government sites, e-commerce, social media, real estate, job boards, and financial databases.

---

## Authentication Requirements Analysis

### Results

Manual review of all 201 Direct Web Scraping tasks identified **18-22 tasks requiring authentication** (9-11% of total).

| Category | Count | % of Total |
|----------|-------|------------|
| **Hard Authentication Walls** | 13 | 6.5% |
| **Subscription/Freemium Services** | 5-9 | 2.5-4.5% |
| **Public - No Authentication** | ~180 | 89.5% |

### Hard Authentication Walls (13 tasks)

**Social Media Platforms (2):** Instagram profile analysis tasks require login to view profiles

**Job/Freelance Platforms (3):** Upwork job listings, Apna.co require accounts for full access

**Professional Networks (2):** LinkedIn company pages and profiles require authentication

**Betting Platforms (2):** Stake.com, Breaking-bet.com require accounts to view odds/markets

**Government Procurement (2):** eProcure India, PhilGEPS require registration for certain data access

**Business Directories (2):** Mergr.com transactions and similar B2B platforms with restricted data

### Subscription/Freemium Services (5-9 tasks)

Business intelligence platforms (Beauhurst, SEMrush, SimilarWeb, Crunchbase) offer limited free access but full data requires paid subscriptions. Keyword research tools (Wordstream, WordTracker) may require accounts.

### Public Data - No Authentication (~180 tasks)

**Government/Regulatory (50+ tasks):** SEC filings, NVD vulnerability database, UK Contracts Finder, court records, patent databases - all legally required to be public

**E-Commerce (40+ tasks):** Amazon, Flipkart, Taobao, and other retail sites - product browsing is public

**Real Estate (20+ tasks):** Zillow, Redfin, Apartments.com - listing views are public (bot detection ≠ authentication)

**Technical Resources (25+ tasks):** GitHub public repositories, documentation sites, package managers - freely accessible

**Business Directories (15+ tasks):** Google Maps, BBB, company websites - publicly browsable


### Coverage and Completion Rates

Out of **18-22 auth-required tasks**, only **7 were found** in the Evals Export dataset (~35% coverage).

**For the 7 evaluated tasks:**
- **100%** self-reported as completed by agents
- **100%** have judge evaluations

**Judge Verdicts:**
- ✅ **PASS: 4 tasks (57%)**
- ❌ **FAIL: 2 tasks (29%)**
- ❔ **UNCLEAR: 1 task (14%)**

### Breakdown by Authentication Type

**Hard Authentication Walls (13 tasks):**
- 3 evaluated / 10 not evaluated
- Results: 1 PASS (Instagram via Inflact proxy), 1 FAIL, 1 UNCLEAR
- **Pass rate: 33%** (via third-party workaround)

**Subscription Services (5-9 tasks):**
- 1 evaluated / 4-8 not evaluated
- Limited evaluation data

**Public Data Misclassified (4 tasks):**
- Originally flagged as auth-required, but data was actually public
- SEC.gov, NSE India, UK Contracts Finder, TenderNED
- All passed via direct access to legally public data
- **Pass rate: 100%**

### No-Auth Tasks Evaluation (181 tasks)

Out of **183 no-auth tasks** (public data), **181 were found** in the Evals Export dataset (98.9% coverage) and **176 have judge verdicts**.

**Judge Verdicts:**
- ✅ **PASS: 62 tasks (35.2%)**
- ❌ **FAIL: 20 tasks (11.4%)**
- ❔ **UNCLEAR: 94 tasks (53.4%)**

**Verdict Context:**

**PASS (62 tasks):** Successfully extracted public data - government filings, e-commerce products, documentation, tenders, business directories

**FAIL (20 tasks):** Blocked by bot detection/CAPTCHAs (Cloudflare, anti-scraping), incorrect selectors, or platform substitution (used wrong source)

**UNCLEAR (94 tasks):** Partial success, incomplete extraction, or nuanced judge verdicts without explicit pass/fail determination

Overall, agents successfully accessed public data in ~35% of evaluated cases, with technical barriers (not authentication) being the primary challenge.

---

## Authentication Bypass Strategies

### Strategy 1: Public Data Access ✅ (100% success rate)

**4 out of 7 evaluated auth-required tasks** accessed data that was **actually publicly available by law**.

**Successful Cases:**

1. **SEC.gov - Financial Statements** ✅
   - EDGAR filings are legally required to be public
   - Agent directly scraped HTML, extracted tables to CSV
   - No authentication ever needed

2. **NSE India - Stock Data** ✅
   - Corporate filings must be public per regulations
   - Used public autocomplete API, extracted 60 rows
   - Authentication only needed for advanced features

3. **UK Contracts Finder** ✅
   - Public procurement transparency law requires tender publication
   - Extracted 20 complete tender listings
   - Registration optional for submitting bids, not viewing

4. **TenderNED Netherlands** ✅ (partial)
   - EU procurement directives mandate public listings
   - Extracted 5 tenders (incomplete but valid data)

**Why No Authentication Was Needed:**
- Data is legally required to be public (SEC filings, procurement transparency laws)
- Platforms have optional login features for premium/submission functions
- Core data requested is freely accessible without credentials

### Strategy 2: Third-Party Proxy Service ✅ (100% success rate)

**Instagram via Inflact.com** ✅
- Instagram requires login to view profiles
- Agent used **inflact.com** (Instagram downloader service)
- Inflact scraped Instagram on their backend
- Agent received 36 posts (URLs, media, captions, hashtags)
- **No direct Instagram authentication needed**

**How Third-Party Services Work:**
- Maintain their own authenticated sessions to target platforms
- Use platform APIs or web scraping infrastructure
- Provide data through simple, public web interfaces
- No authentication required from end user

### Strategy 3: Platform Substitution ❌ (0% success rate)

**When agents couldn't access target platforms, they used alternatives. All were rejected by judges.**

1. **Zillow → Craigslist** ❌
   - Encountered Zillow's anti-bot protection
   - Switched to Craigslist for rental data
   - **Failed:** Task explicitly required Zillow

2. **Redfin → Trulia/Google** ❌
   - Hit Cloudflare bot detection
   - Used Trulia and Google instead
   - **Failed:** No Redfin URLs, wrong data source

3. **eProcure India → data.gov.in** ❌
   - Encountered "robust CAPTCHA system"
   - Used Open Government Data portal
   - **Failed:** Incomplete data, missing required fields

Agents frame failures as external blockers ("aggressive bot detection", "robust CAPTCHA") rather than their limitations.

---

## Key Findings

### 1. Authentication Barriers Are Rare

Only **9-11% of Direct Web Scraping tasks** genuinely require authentication. The vast majority (89.5%) target public data:
- Government regulatory filings (SEC, court records, patent databases)
- E-commerce product browsing (Amazon, retail sites)
- Real estate listings (Zillow, Redfin)
- Technical documentation (GitHub public repos, API docs)

### 2. Legally Public Data Dominates

**Over 50 tasks** target government/regulatory data that is **legally required to be public**:
- SEC EDGAR filings (securities law)
- Public procurement tenders (transparency mandates)
- Court records and business registrations (FOIA)
- Stock exchange filings (regulatory requirements)

Agents successfully access this data directly without any authentication workarounds.

### 3. Bot Detection ≠ Authentication

Real estate platforms (Zillow, Redfin) fail due to anti-scraping measures:
- Cloudflare protection
- Browser fingerprinting
- CAPTCHA challenges

These are **technical barriers**, not authentication requirements. The data is publicly viewable but protected against automated access.

### 4. Third-Party Proxies Bypass Some Auth

Instagram task succeeded via **Inflact.com** - a third-party service that:
- Maintains authenticated sessions to target platforms
- Provides data through public interfaces
- Requires no credentials from end user

This is a legitimate workaround for platforms with hard authentication walls.

### 5. Platform Substitution Always Fails

Judges reject tasks where agents use alternative data sources, even when:
- Data is equivalent
- Target platform is inaccessible
- Agent provides valid justification

**Evaluation standard:** Must use specified platform, no substitutions accepted.

### 6. Agent Self-Reporting is Unreliable

- **100% of agents self-reported success**
- **Only 57% confirmed by judges** (4/7 tasks)

Agents claim completion even when they:
- Used wrong platforms
- Provided incomplete data
- Failed to meet task requirements

---

## Implications and Recommendations

### For Authentication Detection

**Manual review required** - Platform-specific knowledge necessary to identify genuine authentication barriers

**Critical distinctions:**
- **Authentication barriers** - Need user credentials (Instagram, LinkedIn, Upwork)
- **Bot detection** - Anti-scraping measures (Cloudflare, fingerprinting, CAPTCHAs)
- **Subscription walls** - Freemium models with limited free access
- **Legally public data** - No authentication needed despite platform having login features

**Prioritize checking legal requirements:**
- Government regulatory filings → Always public
- Public procurement portals → Transparency laws mandate public access
- Court records → FOIA requirements
- Stock exchange filings → Regulatory transparency

### Agent Capabilities Without Credentials

**CAN successfully access:**
- Public regulatory data (SEC, NVD, procurement tenders)
- E-commerce browsing (product listings, prices)
- Real estate listings (viewing public data)
- Technical documentation (GitHub, API docs)
- Third-party proxy services (Inflact for Instagram)

**CANNOT access:**
- Social media profiles (without proxy workarounds)
- Job platform full details (Upwork, LinkedIn)
- Subscription service full data (SEMrush, Beauhurst)
- Bot-protected sites (Cloudflare, CAPTCHAs)
- Alternative platforms (substitution rejected by judges)

---

**Analysis Artifacts:**
- `analysis/direct_web_scraping_websites.txt` - 204 unique domains
- `analysis/auth_required_tasks.txt` - 18-22 auth-required tasks breakdown
- `analysis/auth_task_completion_analysis.txt` - Evaluation results
- `analysis/auth_bypass_comprehensive_report.md` - Detailed bypass methods
- `analysis/auth_bypass_methods.txt` - Strategy summaries
