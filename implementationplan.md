# Implementation Plan: Zepto AI-Powered Discovery Engine

> **Timeline:** 2 Days  
> **Builder:** Solo developer  
> **Budget:** $0 (Groq free tier + open-source)  
> **Objective:** Build a working AI Discovery Engine that scrapes user feedback, analyzes it via Groq, clusters themes, generates validated insights, and displays results on an interactive dashboard.

---

## Phase Overview

```
DAY 1                                       DAY 2
───────────────────────────────             ───────────────────────────────
Phase 1: Project Setup & Infra (~2 hrs)    Phase 4: Insight Engine (~2 hrs)
Phase 2: Data Collection      (~2 hrs)    Phase 5: Validation        (~2 hrs)
Phase 3: AI Analysis Pipeline  (~2 hrs)    Phase 6: Dashboard & Ship  (~4 hrs)
Phase 3B: Clustering           (~2 hrs)

End of Day 1:                               End of Day 2:
✓ 500+ docs from 4 sources                 ✓ 10-15 validated insights
✓ Every doc analyzed (sentiment + drivers)  ✓ Confidence scoring
✓ 10-25 theme clusters with labels          ✓ Interactive PM dashboard
                                            ✓ One-command pipeline
```

---

## Scope: MVP vs. Post-MVP

| Build Now (MVP) | Build Later (Post-MVP) |
|---|---|
| Python scripts run via CLI | Docker Compose, Airflow orchestration |
| SQLite (zero-config database) | PostgreSQL + pgvector |
| 4 sources: Play Store, Reddit, Twitter/X, forums | App Store (needs Apple ID), product reviews, QCommerce blogs |
| Groq API for all LLM tasks | Fallback NLP pipeline (VADER + keyword extraction) |
| `all-MiniLM-L6-v2` embeddings in-memory | pgvector persistent storage |
| HDBSCAN clustering | UMAP dimensionality reduction |
| Next.js dashboard (5 views) | REST API, Slack/email alerts, Grafana |
| JSON file export for dashboard | Live API connection |
| Manual pipeline run | Scheduled cron ingestion |

---

## Pre-Sprint Setup (30 min)

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Create free Groq account → API key from [console.groq.com](https://console.groq.com)
- [ ] Create Reddit app at [reddit.com/prefs/apps](https://reddit.com/prefs/apps) → get `client_id` + `client_secret`
- [ ] Create `.env` file:
  ```
  GROQ_API_KEY=gsk_...
  REDDIT_CLIENT_ID=...
  REDDIT_CLIENT_SECRET=...
  REDDIT_USER_AGENT=ZeptoDiscoveryEngine/1.0
  ```
- [ ] Install Python dependencies:
  ```bash
  pip install google-play-scraper praw snscrape sentence-transformers hdbscan scikit-learn groq tqdm python-dotenv
  ```

---

# PHASE 1: Project Setup & Infrastructure

> **Duration:** ~2 hours  
> **Goal:** Project structure, database, and Groq client ready.  
> **Architecture Layers:** Foundation for all layers

---

### 1.1 Create Project Structure

```
Zepto_AIDiscovery-Engine/
├── scrapers/
│   ├── __init__.py
│   ├── playstore.py
│   ├── reddit.py
│   ├── twitter.py
│   └── forums.py
├── analysis/
│   ├── __init__.py
│   ├── groq_client.py
│   ├── analyzer.py
│   └── prompts.py
├── clustering/
│   ├── __init__.py
│   ├── embeddings.py
│   ├── cluster.py
│   └── label_themes.py
├── insights/
│   ├── __init__.py
│   ├── synthesize.py
│   ├── segments.py
│   ├── validate.py
│   └── export.py
├── dashboard/                  # Next.js app (created in Phase 6)
├── data/
│   ├── discovery.db            # SQLite database
│   ├── schema.sql
│   └── insights_export.json    # Dashboard data feed
├── run_pipeline.py             # Single entry point
├── requirements.txt
├── .env
├── problemStatement.md
├── architecture.md
└── README.md
```

**Time:** 15 min

---

### 1.2 Initialize SQLite Database

Create `data/schema.sql` and initialize the database:

```sql
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,              -- play_store, reddit, twitter, forum
    content TEXT NOT NULL,
    content_clean TEXT,
    source_url TEXT,
    author_hash TEXT,
    rating REAL,
    upvotes INTEGER,
    source_timestamp TEXT,
    scraped_at TEXT DEFAULT (datetime('now')),
    word_count INTEGER,
    is_duplicate BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS analysis (
    doc_id TEXT PRIMARY KEY REFERENCES documents(id),
    sentiment TEXT,                    -- positive, negative, neutral, mixed
    sentiment_score REAL,
    emotions TEXT,                     -- JSON array
    categories_mentioned TEXT,         -- JSON array
    categories_desired TEXT,           -- JSON array
    category_switch_signal BOOLEAN,
    behavioral_drivers TEXT,          -- JSON array [{driver, confidence, evidence}]
    research_questions TEXT,           -- JSON array of Q1-Q8 tags
    analyzed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS themes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    macro_theme TEXT,
    drivers TEXT,                      -- JSON array
    blocked_categories TEXT,           -- JSON array
    research_questions TEXT,           -- JSON array
    doc_count INTEGER,
    avg_sentiment REAL,
    representative_quotes TEXT,       -- JSON array
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS theme_docs (
    theme_id TEXT REFERENCES themes(id),
    doc_id TEXT REFERENCES documents(id),
    PRIMARY KEY (theme_id, doc_id)
);

CREATE TABLE IF NOT EXISTS insights (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    finding TEXT,
    root_cause TEXT,
    impact TEXT,                       -- JSON
    target_segment TEXT,              -- JSON
    hypotheses TEXT,                  -- JSON array
    supporting_themes TEXT,           -- JSON array of theme IDs
    confidence_score REAL,
    confidence_level TEXT,            -- HIGH, MEDIUM, LOW
    research_questions TEXT,          -- JSON array
    created_at TEXT DEFAULT (datetime('now'))
);
```

**Time:** 20 min

---

### 1.3 Build Groq API Client

Build `analysis/groq_client.py` — a wrapper with rate limiting and retries:

```python
# Key features:
# - Rate limiting: 25 requests/min (under Groq's 30/min free limit)
# - Retry with exponential backoff on 429/500 errors
# - Model selection: 8b-instant for bulk, 70b-versatile for synthesis
# - JSON response parsing with fallback handling
```

| Config | Value |
|---|---|
| Primary model (bulk analysis) | `llama-3.1-8b-instant` |
| Quality model (themes, insights) | `llama-3.3-70b-versatile` |
| Rate limit | 25 req/min with `time.sleep(2.4)` |
| Max retries | 3 with exponential backoff |
| Temperature | 0 (deterministic) |

**Time:** 25 min

---

### 1.4 Verify Setup

- [ ] `python -c "import groq; print('Groq OK')"` passes
- [ ] `python -c "import sqlite3; print('SQLite OK')"` passes
- [ ] Groq test prompt returns valid JSON
- [ ] Database file `data/discovery.db` created with all tables

**Time:** 10 min

---

### Phase 1 — Definition of Done

- [x] Project folder structure created
- [x] SQLite database initialized with schema
- [x] Groq client wrapper built and tested
- [x] All Python dependencies installed and verified

---

# PHASE 2: Data Collection & Processing

> **Duration:** ~2 hours  
> **Goal:** Scrape 500+ documents from 4 platforms, clean and deduplicate.  
> **Architecture Layer:** Layer 1 (Ingestion) + Layer 2 (Normalization)

---

### 2.1 Play Store Scraper

**File:** `scrapers/playstore.py`

Scrape reviews from Zepto + competitor apps for broader quick-commerce context:

| App | Package ID | Reviews |
|---|---|---|
| Zepto | `com.zepto.app` | 200 |
| Blinkit | `com.grofers.customerapp` | 150 |
| Swiggy Instamart | `in.swiggy.android` | 150 |

```python
# Uses: google-play-scraper library
# Extracts: review text, rating (1-5), thumbs up count, date, device
# Outputs: List of document dicts ready for DB insertion
```

**Time:** 25 min

---

### 2.2 Reddit Scraper

**File:** `scrapers/reddit.py`

Scrape posts + top-level comments from relevant subreddits:

| Subreddit | Search Keywords |
|---|---|
| `r/zepto` | All posts |
| `r/IndianFood` | "zepto", "quick commerce", "delivery" |
| `r/india` | "zepto", "blinkit", "instamart" |
| `r/bangalore`, `r/mumbai`, `r/delhi` | "zepto", "grocery delivery" |

```python
# Uses: PRAW (Python Reddit API Wrapper) with free OAuth
# Extracts: post title + body, top comments, score, subreddit, date
# Each comment is stored as a separate document
```

**Time:** 25 min

---

### 2.3 Twitter/X Scraper

**File:** `scrapers/twitter.py`

Search tweets about quick-commerce platforms:

| Search Query | Timeframe |
|---|---|
| `"zepto" lang:en` | Last 6 months |
| `"quick commerce" category` | Last 6 months |
| `"blinkit" OR "instamart" shopping` | Last 6 months |

```python
# Uses: snscrape (no API key needed)
# Extracts: tweet text, date, likes, retweets, username hash
```

**Time:** 25 min

---

### 2.4 Forum/Blog Scraper

**File:** `scrapers/forums.py`

Scrape quick-commerce discussion threads and comparison articles:

```python
# Uses: BeautifulSoup + requests
# Targets: Quick-commerce comparison blogs, consumer forums
# Extracts: Article/comment text, author, date, URL
```

**Time:** 20 min

---

### 2.5 Cleaning & Deduplication

Apply to all scraped data before insertion:

| Step | Method |
|---|---|
| **Exact dedup** | SHA-256 hash of `content` → skip if hash exists |
| **Noise removal** | Drop entries < 15 characters |
| **PII redaction** | Regex: emails, phone numbers → `[REDACTED]` |
| **Language filter** | Keep English / Hindi / Hinglish (use simple heuristics) |
| **Word count** | Compute and store for each document |

**Time:** 15 min

---

### 2.6 Verify Data

```sql
-- Run these checks:
SELECT source, COUNT(*) as docs FROM documents GROUP BY source;
SELECT AVG(word_count) as avg_words, MIN(word_count), MAX(word_count) FROM documents;
SELECT COUNT(*) FROM documents WHERE is_duplicate = 1;
```

**Expected:** 500+ clean documents across 4 sources.

**Time:** 10 min

---

### Phase 2 — Definition of Done

- [x] 4 scrapers implemented and working
- [x] 500+ documents in `documents` table
- [x] Documents span 4 source platforms
- [x] Duplicates flagged, PII redacted
- [x] Manual review of 10 samples confirms data quality

---

# PHASE 3: AI Analysis & Theme Clustering

> **Duration:** ~4 hours (2 hrs analysis + 2 hrs clustering)  
> **Goal:** Enrich every document with AI analysis, then cluster into named themes.  
> **Architecture Layers:** Layer 3 (AI Analysis) + Layer 4 (Clustering)

---

### 3.1 Build Analysis Prompts

**File:** `analysis/prompts.py`

Two prompt templates optimized for structured JSON output:

#### Prompt A: Sentiment & Emotion

```
Analyze this quick-commerce user feedback.
Return JSON: {sentiment, sentiment_score, emotions[], emotion_intensity}
```

#### Prompt B: Category & Behavioral Driver

```
Analyze this feedback against Zepto's category taxonomy and behavioral driver framework.
Return JSON: {categories_mentioned[], categories_desired[], category_switch_signal,
              behavioral_drivers[{driver, sub_driver, confidence, evidence}]}
```

**Time:** 20 min

---

### 3.2 Implement Analysis Pipeline

**File:** `analysis/analyzer.py`

Process all documents through Groq in batches:

| Config | Value |
|---|---|
| Model | `llama-3.1-8b-instant` (fast, saves quota for later phases) |
| Batch size | 1 document per request (Groq processes fast) |
| Rate limit | 25 req/min → `time.sleep(2.4)` between calls |
| Progress | `tqdm` progress bar |
| Error handling | JSON parse retry (3x), 429 backoff, skip + log failures |

**Time:** 30 min

---

### 3.3 Research Question Tagging

Map detected behavioral drivers to the 8 research questions (rule-based, no LLM needed):

| Driver Family | Maps To |
|---|---|
| `HABIT_LOOP` | Q1 (habit formation), Q4 (role of habits) |
| `DISCOVERY_FRICTION` | Q2 (discovery barriers), Q3 (discovery mechanisms) |
| `TRUST_BARRIER` | Q2 (discovery barriers), Q5 (information needs) |
| `VALUE_PERCEPTION` | Q2 (discovery barriers), Q6 (pain points) |
| `INFORMATION_GAP` | Q5 (information needs), Q8 (unmet needs) |
| `CONTEXTUAL_TRIGGER` | Q3 (discovery mechanisms), Q7 (user segments) |
| `PLATFORM_LIMITATION` | Q6 (pain points), Q8 (unmet needs) |

**Time:** 10 min

---

### 3.4 Run Analysis on Full Corpus

```bash
python -m analysis.analyzer
# Expected: ~500 documents × 2.4s interval = ~20 min runtime
# Output: All rows populated in `analysis` table
```

**Time:** 25 min (mostly waiting for Groq processing)

---

### 3.5 Spot-Check Quality

Manually review 20 randomly sampled analysis results:

- [ ] Sentiment label matches the tone of the text
- [ ] Categories are correctly identified (not hallucinated)
- [ ] Behavioral drivers are relevant and have real evidence spans
- [ ] Research question tags make sense for the content

**Time:** 10 min

---

### 3.6 Generate Embeddings

**File:** `clustering/embeddings.py`

```python
# Model: all-MiniLM-L6-v2 (384 dimensions, runs on CPU)
# Input: content + primary behavioral driver (concatenated)
# Output: NumPy array of shape (N, 384) + document ID mapping
# Storage: In-memory (NumPy) — no need for pgvector at MVP scale
```

**Time:** 20 min (coding) + ~2 min (embedding 500 docs on CPU)

---

### 3.7 HDBSCAN Clustering

**File:** `clustering/cluster.py`

| Parameter | Value | Rationale |
|---|---|---|
| `min_cluster_size` | 8 | Minimum docs to form a theme |
| `min_samples` | 3 | Core point density |
| `metric` | `euclidean` | Standard for dense embeddings |

```python
# Output:
# - cluster_labels array (cluster_id per document, -1 = noise)
# - Print: number of clusters, noise percentage
# - If noise > 40%: reduce min_cluster_size and re-run
# - If clusters < 5: reduce min_cluster_size
# - If clusters > 40: increase min_cluster_size
```

**Time:** 15 min

---

### 3.8 LLM Theme Labeling

**File:** `clustering/label_themes.py`

For each cluster:
1. Sample 15 representative documents
2. Send to Groq `llama-3.3-70b-versatile`
3. Generate: title, 2-sentence summary, macro_theme, key drivers, blocked categories, research questions
4. Save to `themes` + `theme_docs` tables

**Time:** 30 min (coding) + ~5 min (Groq processing for 15-25 themes)

---

### 3.9 Cluster Visualization

Generate 2D scatter plot for visual review:

```python
# UMAP: reduce 384d → 2d for plotting
# matplotlib scatter: color by cluster_id
# Save as data/clusters.png
```

**Time:** 15 min

---

### Phase 3 — Definition of Done

- [x] Every document has sentiment, emotions, categories, behavioral drivers
- [x] Research questions Q1–Q8 tagged on all documents
- [x] 10–25 theme clusters generated via HDBSCAN
- [x] Each theme has an LLM-generated title and summary
- [x] Cluster visualization saved as PNG
- [x] Manual review confirms themes are coherent

---

# PHASE 4: Insight Generation

> **Duration:** ~2 hours  
> **Goal:** Synthesize themes into PM-grade insights with testable growth hypotheses.  
> **Architecture Layer:** Layer 5 (Insight Generation)

---

### 4.1 Insight Synthesis

**File:** `insights/synthesize.py`

For each significant theme (doc_count ≥ 10), send to Groq `llama-3.3-70b-versatile`:

**Input to LLM:**
- Theme title + summary
- Document count + average sentiment
- Key behavioral drivers
- Blocked categories
- 5 representative user quotes

**Output (structured JSON):**

| Field | Description |
|---|---|
| `title` | Concise insight headline |
| `finding` | What is happening (1–2 sentences with data) |
| `root_cause` | Why it's happening (2–3 sentences) |
| `impact` | Affected users %, blocked category, severity |
| `target_segment` | Who is most affected + behavioral profile |
| `hypotheses[]` | 2–3 testable experiments with effort/impact ratings |

**Time:** 30 min

---

### 4.2 Cross-Theme Synthesis

Identify themes that share `blocked_categories` (e.g., both Trust and Information themes block Personal Care). Send grouped themes to Groq to generate **compound barrier insights**:

```
"Trust + Information + Value barriers compound for Personal Care.
 Users need all three resolved simultaneously before category entry."
```

**Time:** 20 min

---

### 4.3 User Segment Profiling

**File:** `insights/segments.py`

Send all theme data to Groq. Generate 5 archetypal user segments:

| Segment | Cross-Category Potential |
|---|---|
| Habitual Minimalists | Low |
| Curious Browsers | Very High |
| Value Seekers | Medium |
| Life-Stage Movers | High |
| Loyalists | Medium |

Each segment includes: name, description, estimated size (% of MACs), behavioral profile, recommended intervention.

**Time:** 20 min

---

### 4.4 Research Question Mapping

For each of the 8 research questions, compile:
- Number of supporting themes
- Top 1–2 insights that address the question
- Evidence strength (based on document volume + source diversity)

**Time:** 15 min

---

### 4.5 Export Data

**File:** `insights/export.py`

Export everything to `data/insights_export.json`:

```json
{
  "generated_at": "2026-07-16T...",
  "summary": { "total_docs": 523, "total_themes": 18, "total_insights": 12 },
  "insights": [...],
  "themes": [...],
  "segments": [...],
  "research_questions": [...],
  "source_stats": {...}
}
```

**Time:** 15 min

---

### Phase 4 — Definition of Done

- [x] 10–15 insights generated with findings + root causes + hypotheses
- [x] Cross-theme compound barriers identified
- [x] 5 user segments profiled
- [x] All 8 research questions mapped to supporting evidence
- [x] `data/insights_export.json` exported for dashboard

---

# PHASE 5: Validation & Confidence Scoring

> **Duration:** ~2 hours  
> **Goal:** Score every insight for reliability. Ensure no hallucinated or unsupported conclusions.  
> **Architecture Layer:** Layer 6 (Validation)

---

### 5.1 Validation Gates

**File:** `insights/validate.py`

Run each insight through 5 automated quality gates:

| Gate | Check | Pass Criteria | Action on Fail |
|---|---|---|---|
| **Gate 1: Source Grounding** | Count supporting source documents | ≥ 5 documents from ≥ 2 platforms | Flag as `LOW` confidence |
| **Gate 2: Volume** | Check theme document count | ≥ 10 documents, spans ≥ 7 days | Flag as `LOW` confidence |
| **Gate 3: Sentiment Consistency** | Compute std. dev. of sentiment scores within theme | Std. dev. < 0.3 | Flag for manual review |
| **Gate 4: Cross-Platform Agreement** | Check sentiment direction across platforms | Consistent across ≥ 2 platforms | Flag potential platform bias |
| **Gate 5: LLM Self-Consistency** | Re-run 5 sample analyses with rephrased prompts | ≥ 80% agreement | Flag potential hallucination |

**Time:** 60 min

---

### 5.2 Composite Confidence Score

Calculate weighted score for every insight:

```
Confidence = Volume(0.25) + Diversity(0.20) + Consistency(0.20) + Temporal(0.15) + LLM_Agreement(0.20)

Classification:
  ≥ 0.80  →  HIGH    (reliable, ready for action)
  0.60–0.79 → MEDIUM  (likely valid, review recommended)
  < 0.60  →  LOW     (needs more data or manual verification)
```

**Time:** 20 min

---

### 5.3 Update & Re-Export

- Update `insights` table with `confidence_score` and `confidence_level`
- Re-export `data/insights_export.json` with confidence data included

**Time:** 10 min

---

### Phase 5 — Definition of Done

- [x] All insights scored with composite confidence
- [x] At least 50% of insights rated MEDIUM or HIGH
- [x] LOW-confidence insights flagged with specific failure reasons
- [x] Updated `insights_export.json` includes confidence data

---

# PHASE 6: Dashboard & Ship

> **Duration:** ~4 hours  
> **Goal:** Build interactive PM dashboard, create one-command pipeline runner, write docs, and ship.  
> **Architecture Layer:** Layer 7 (Presentation)

---

### 6.1 Initialize Dashboard

```bash
npx -y create-next-app@latest ./dashboard
cd dashboard && npm install recharts
```

**Time:** 15 min

---

### 6.2 Zepto Design System (Brand-Aligned UI)

The dashboard must visually match Zepto's signature aesthetic — **deep purple branding, magenta accents, clean white layouts, and modern sans-serif typography**.

#### Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--zepto-purple` | `#3E0075` | Primary brand color — header, sidebar active state, headings |
| `--zepto-purple-light` | `#5C0099` | Hover states, secondary brand elements |
| `--zepto-purple-bg` | `#F3EAFF` | Light purple tint for selected/active backgrounds |
| `--zepto-magenta` | `#E21A84` | Accent CTA — buttons, links, badges, interactive elements |
| `--zepto-magenta-light` | `#FF007F` | Hover state for magenta elements |
| `--zepto-green` | `#16A34A` | Positive indicators — HIGH confidence, positive sentiment |
| `--zepto-red` | `#DC2626` | Negative indicators — LOW confidence, negative sentiment |
| `--zepto-amber` | `#F59E0B` | Warning/medium — MEDIUM confidence |
| `--bg-primary` | `#FFFFFF` | Main content background |
| `--bg-secondary` | `#F8F9FA` | Section backgrounds, card hover states |
| `--bg-sidebar` | `#F3F4F6` | Sidebar navigation background |
| `--text-primary` | `#1F2937` | Headlines, card titles, bold text |
| `--text-secondary` | `#5A6477` | Metadata, labels, secondary information |
| `--text-muted` | `#9CA3AF` | Timestamps, placeholder text |
| `--border` | `#E5E7EB` | Card borders, dividers |

#### CSS Variables (in `globals.css`)

```css
:root {
  --zepto-purple: #3E0075;
  --zepto-purple-light: #5C0099;
  --zepto-purple-bg: #F3EAFF;
  --zepto-magenta: #E21A84;
  --zepto-magenta-light: #FF007F;
  --zepto-green: #16A34A;
  --zepto-red: #DC2626;
  --zepto-amber: #F59E0B;
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8F9FA;
  --bg-sidebar: #F3F4F6;
  --text-primary: #1F2937;
  --text-secondary: #5A6477;
  --text-muted: #9CA3AF;
  --border: #E5E7EB;
  --radius-card: 12px;
  --radius-button: 8px;
  --radius-badge: 6px;
  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-hover: 0 4px 12px rgba(62, 0, 117, 0.08);
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

#### Typography (Google Fonts — Inter)

| Element | Font Weight | Size | Color |
|---|---|---|---|
| Page title | 700 (Bold) | 28px | `--zepto-purple` |
| Section heading | 600 (Semi-bold) | 20px | `--text-primary` |
| Card title | 500 (Medium) | 16px | `--text-primary` |
| Body text | 400 (Regular) | 14px | `--text-secondary` |
| Stat number | 700 (Bold) | 32px | `--zepto-purple` |
| Badge text | 600 (Semi-bold) | 12px | White on colored bg |
| Caption / metadata | 400 (Regular) | 12px | `--text-muted` |

#### Component Patterns

**Cards (Insight, Theme, Segment):**
```css
.zepto-card {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
  padding: 20px;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.zepto-card:hover {
  box-shadow: var(--shadow-hover);
  transform: translateY(-2px);
}
```

**Buttons (Zepto "ADD" style — outline with magenta):**
```css
.zepto-btn-primary {
  background: var(--bg-primary);
  border: 1.5px solid var(--zepto-magenta);
  color: var(--zepto-magenta);
  font-weight: 600;
  border-radius: var(--radius-button);
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.zepto-btn-primary:hover {
  background: var(--zepto-magenta);
  color: white;
}
```

**Confidence Badges:**
```css
.badge-high   { background: #DCFCE7; color: #16A34A; }  /* Green */
.badge-medium { background: #FEF3C7; color: #D97706; }  /* Amber */
.badge-low    { background: #FEE2E2; color: #DC2626; }  /* Red */
```

**Sidebar Navigation (matches Zepto category sidebar):**
```css
.sidebar {
  background: var(--bg-sidebar);
  width: 240px;
  border-right: 1px solid var(--border);
}
.sidebar-item {
  padding: 12px 20px;
  color: var(--text-secondary);
  font-weight: 500;
  border-left: 3px solid transparent;
  transition: all 0.15s ease;
}
.sidebar-item.active {
  color: var(--zepto-purple);
  background: var(--zepto-purple-bg);
  border-left-color: var(--zepto-purple);
  font-weight: 600;
}
```

**Time:** 20 min (set up design system in `globals.css` + component classes)

---

### 6.3 Build 5 Dashboard Views (Zepto-Styled)

#### View 1: Executive Summary (`app/page.tsx`)

| Element | Zepto Style | Data Source |
|---|---|---|
| **Header bar** | Deep purple (`#3E0075`) full-width bar with white logo text "Zepto Discovery Engine" + search bar (rounded, grey border) | Static |
| **Stat cards (4x row)** | White cards, purple large stat number (32px bold), grey label text below. Icons in magenta circles | Total docs, themes, insights, sources |
| **Top 5 insights list** | White cards with magenta left border accent. Title in dark text, finding in grey. Confidence badge (green/amber/red pill) on right | `insights[]` sorted by impact × confidence |
| **Category opportunity heatmap** | Recharts heatmap using purple gradient (`#F3EAFF` → `#3E0075`). Grid of blocked categories | Blocked categories frequency |
| **Source breakdown** | Recharts donut chart with purple/magenta/teal palette. Clean legend below | `source_stats` |

**Time:** 35 min

---

#### View 2: Theme Explorer (`app/themes/page.tsx`)

| Element | Zepto Style | Data Source |
|---|---|---|
| **Filter bar** | Horizontal pills (Zepto outline button style — magenta border, white bg). Active filter = filled magenta | Client-side filter by macro_theme |
| **Theme cards (grid)** | 3-column grid. Each card: title (medium weight), doc count badge (purple bg), horizontal sentiment bar (green-to-red gradient), driver tags as small purple pills | `themes[]` |
| **Expanded detail** | Click card → slide-down panel with: summary text, representative quotes in grey italic quote blocks, affected categories as magenta outline badges | `themes[].representative_quotes` |

**Time:** 35 min

---

#### View 3: Research Questions (`app/research/page.tsx`)

| Element | Zepto Style | Data Source |
|---|---|---|
| **8 question cards (2×4 grid)** | Each card: Q number in purple circle badge, question text in semi-bold, supporting theme count, top insight preview, evidence strength bar (segmented, colored by confidence level) | `research_questions[]` |

**Time:** 20 min

---

#### View 4: User Segments (`app/segments/page.tsx`)

| Element | Zepto Style | Data Source |
|---|---|---|
| **5 segment cards (horizontal scroll or grid)** | Each card: segment name in bold, description text, "% of MACs" as large purple stat number, cross-category potential bar (horizontal bar in magenta gradient), recommended intervention in grey italics below | `segments[]` |

**Time:** 20 min

---

#### View 5: Source Monitor (`app/sources/page.tsx`)

| Element | Zepto Style | Data Source |
|---|---|---|
| **Bar chart** | Recharts vertical bars in purple gradient. Source labels below. Hover shows exact count | `source_stats` |
| **Source table** | Clean table with alternating row backgrounds (`#FFFFFF` / `#F8F9FA`). Purple header row. Columns: Source, Docs, Date Range, Avg Sentiment (color-coded) | Computed from documents |

**Time:** 15 min

---

### 6.4 Navigation & Layout

**Overall layout matches Zepto's category page pattern:**

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER (deep purple #3E0075, full width)                       │
│  [🟣 Zepto Discovery Engine]  [🔍 Search insights...]  [👤]    │
├────────────┬────────────────────────────────────────────────────┤
│  SIDEBAR   │  MAIN CONTENT                                     │
│  (240px)   │                                                    │
│  #F3F4F6   │  White background                                 │
│            │                                                    │
│  📊 Summary│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  🏷️ Themes │  │ Stat Card│ │ Stat Card│ │ Stat Card│          │
│  ❓ Research│  └──────────┘ └──────────┘ └──────────┘          │
│  👥 Segments│                                                   │
│  📡 Sources│  ┌─────────────────────────────────────┐          │
│            │  │     Charts / Content Area            │          │
│            │  │                                       │          │
│            │  └─────────────────────────────────────┘          │
├────────────┴────────────────────────────────────────────────────┤
│  FOOTER (light grey, subtle)                                    │
└─────────────────────────────────────────────────────────────────┘
```

- Sidebar: sticky, independent scroll (like Zepto's category sidebar)
- Active view highlighted with purple left border + purple background tint
- Smooth page transitions between views
- Responsive: sidebar collapses to hamburger menu on mobile

**Time:** 20 min

---

### 6.4 Create `run_pipeline.py`

Single entry point that runs everything sequentially:

```python
"""
Usage: python run_pipeline.py

Runs the full Zepto AI Discovery Engine pipeline:
  Step 1: Scrape data from 4 sources
  Step 2: Clean, dedup, and normalize
  Step 3: Analyze via Groq (sentiment, categories, drivers)
  Step 4: Generate embeddings
  Step 5: Cluster into themes (HDBSCAN)
  Step 6: Label themes via Groq
  Step 7: Synthesize insights + segments
  Step 8: Validate and score confidence
  Step 9: Export JSON for dashboard
"""
```

**Time:** 15 min

---

### 6.5 Write README.md

Cover:
- Project overview (what it does, why)
- Architecture diagram (simplified)
- Quick start instructions (3 commands)
- Screenshot of dashboard
- Groq API setup guide
- How to add new data sources

**Time:** 15 min

---

### 6.6 End-to-End Test

```bash
# Full pipeline test
python run_pipeline.py

# Dashboard test
cd dashboard && npm run dev
# Open http://localhost:3000 → verify all 5 views load with real data
```

**Time:** 15 min

---

### 6.7 Final Quality Review

Review the top 5 insights and ask:

| Quality Check | Expected |
|---|---|
| Is the finding specific (not generic)? | ✅ References specific categories and user behaviors |
| Is the root cause evidence-backed? | ✅ Cites user quotes and document counts |
| Are hypotheses testable? | ✅ Each has a clear if-then statement with expected metric |
| Does the confidence score feel right? | ✅ HIGH insights are clearly strong, LOW ones are clearly weak |
| Are all 8 research questions addressed? | ✅ Each has ≥1 supporting theme |

**Time:** 10 min

---

### 6.8 Deploy Backend to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project (from repo root)
railway init

# 4. Set environment variables
railway variables set GROQ_API_KEY=gsk_...
railway variables set REDDIT_CLIENT_ID=...
railway variables set REDDIT_CLIENT_SECRET=...
railway variables set REDDIT_USER_AGENT=ZeptoDiscoveryEngine/1.0

# 5. Add a Procfile for Railway
echo "web: uvicorn api.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 6. Deploy
railway up
```

**Railway free tier:** $5 credit/month, 500 hrs execution, 1 GB RAM, persistent volumes for SQLite.

**Live at:** `https://zepto-api.railway.app`

**Time:** 15 min

---

### 6.9 Deploy Dashboard to Vercel

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Navigate to dashboard
cd dashboard

# 3. Set the backend API URL as environment variable
# In dashboard/.env.production:
echo "NEXT_PUBLIC_API_URL=https://zepto-api.railway.app" > .env.production

# 4. Deploy
vercel --prod

# Or: Connect GitHub repo on vercel.com for auto-deploys on every push
```

**Vercel free tier:** Unlimited deploys, 100 GB bandwidth, global CDN, automatic HTTPS, preview deploys on every PR.

**Live at:** `https://zepto-discovery.vercel.app`

**Time:** 10 min

---

### 6.10 Verify Production Deployment

| Check | Command / Action | Expected |
|---|---|---|
| Backend health | `curl https://zepto-api.railway.app/health` | `{"status": "ok"}` |
| Dashboard loads | Open `https://zepto-discovery.vercel.app` | All 5 views render |
| API connection | Dashboard fetches insights from Railway API | Real data displayed |
| Pipeline trigger | `curl -X POST https://zepto-api.railway.app/run-pipeline` | Pipeline executes on Railway |

**Time:** 10 min

---

### 6.11 Git Commit & Tag

```bash
git add -A
git commit -m "feat: Zepto AI Discovery Engine MVP - Railway + Vercel deployment"
git tag v1.0-mvp
git push origin main --tags
```

**Time:** 5 min

---

### Phase 6 — Definition of Done

- [x] Dashboard loads all 5 views with real data
- [x] Can navigate: Executive Summary → Theme → Quotes in <5 clicks
- [x] `run_pipeline.py` runs the full pipeline with one command
- [x] Backend deployed on Railway (`zepto-api.railway.app`)
- [x] Dashboard deployed on Vercel (`zepto-discovery.vercel.app`)
- [x] Environment variables configured on both platforms
- [x] README.md with setup + deployment instructions
- [x] All code committed and tagged `v1.0-mvp`

---

## Groq Free-Tier Budget

| Phase | Model | Requests | Tokens (est.) |
|---|---|---|---|
| Phase 3: Document analysis (500 docs) | `llama-3.1-8b-instant` | ~500 | ~250K |
| Phase 3: Theme labeling (20 themes) | `llama-3.3-70b-versatile` | ~20 | ~30K |
| Phase 4: Insight synthesis (15 insights) | `llama-3.3-70b-versatile` | ~15 | ~25K |
| Phase 4: Cross-theme + segments | `llama-3.3-70b-versatile` | ~5 | ~10K |
| Phase 5: LLM consistency checks | `llama-3.1-8b-instant` | ~25 | ~12K |
| **Total** | — | **~565** | **~327K** |
| **Groq daily free limit** | — | **~14,400** | **~6M** |
| **Usage** | — | **~4%** | **~5%** |

> Plenty of headroom for retries, prompt iteration, and experimentation.

---

## Final Deliverables (End of Day 2)

| # | Deliverable | Status |
|---|---|---|
| 1 | 500+ documents scraped from 4 sources | ✅ |
| 2 | AI analysis: sentiment, emotions, categories, behavioral drivers | ✅ |
| 3 | 10–25 theme clusters with LLM-generated labels | ✅ |
| 4 | 10–15 PM-grade insights with testable hypotheses | ✅ |
| 5 | Cross-theme compound barrier analysis | ✅ |
| 6 | 5 user segments with behavioral profiles | ✅ |
| 7 | Confidence scoring on all insights (HIGH/MEDIUM/LOW) | ✅ |
| 8 | All 8 research questions addressed with evidence | ✅ |
| 9 | Interactive dashboard with 5 views | ✅ |
| 10 | `run_pipeline.py` — one command runs everything | ✅ |
| 11 | README.md with setup guide | ✅ |
| 12 | Backend deployed on **Railway** (`zepto-api.railway.app`) | ✅ |
| 13 | Dashboard deployed on **Vercel** (`zepto-discovery.vercel.app`) | ✅ |

---

## Research Questions → Phase Mapping

| Research Question | Answered In | Evidence Source |
|---|---|---|
| Q1: Why do users buy same categories? | Phase 3 (driver: `HABIT_LOOP`) → Phase 4 (themes) | Habit-related theme clusters |
| Q2: What prevents exploring new categories? | Phase 3 (drivers: `DISCOVERY_FRICTION`, `TRUST_BARRIER`) → Phase 4 | Barrier insights |
| Q3: How do users discover products today? | Phase 3 (driver: `CONTEXTUAL_TRIGGER`) → Phase 4 | Discovery mechanism themes |
| Q4: Role of habits in shopping behavior? | Phase 3 → Phase 4 → Phase 4 (cross-theme) | Habit impact analysis |
| Q5: What info needed before trying new category? | Phase 3 (driver: `INFORMATION_GAP`) → Phase 4 | Content gap insights |
| Q6: What frustrations emerge repeatedly? | Phase 3 (negative sentiment) → Phase 3 (themes) | Pain point themes |
| Q7: Which segments more likely to experiment? | Phase 4 (segment profiling) | User segment profiles |
| Q8: What unmet needs emerge consistently? | Phase 3 (all themes) → Phase 4 (cross-theme) | Opportunity insights |
