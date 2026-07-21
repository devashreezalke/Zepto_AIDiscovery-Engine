# Zepto AI-Powered Category Discovery Engine 🚀

An end-to-end data-enrichment, clustering, and growth-hypothesis synthesis pipeline for mapping, validating, and overcoming customer barriers to category exploration on Zepto.

Designed to run **100% free of charge** using the **Groq API** (free tier) for lightning-fast analysis and Next.js + Tailwind for an interactive category-styled Product Manager dashboard.

---

## 🏗️ Project Architecture

```
Zepto_AIDiscovery-Engine/
├── scrapers/            # Layer 1: Data Ingestion Scrapers & Cleaners
│   ├── playstore.py     # Pulls reviews from Zepto (com.zeptoconsumerapp) & competitors
│   ├── reddit.py        # Pulls discussions from r/zepto, r/india, etc. (with PRAW)
│   ├── twitter.py       # Pulls tweets matching discovery topics (via snscrape)
│   ├── forums.py        # Parses consumer comparison sites & blogs (BeautifulSoup)
│   └── ingest.py        # Cleans whitespace, redacts PII, flags exact duplicates, & inserts
│
├── analysis/            # Layer 2 & 3: LLM Sentiment & Behavioral Driver Analysis
│   ├── prompts.py       # Optimized JSON prompts for Groq LLMs
│   ├── groq_client.py   # Groq wrapper (25 rpm throttle, 429 backoff, schema validator)
│   └── analyzer.py      # Batch enricher: sentiment, emotions, drivers, categories, & Q1-Q8 RQs
│
├── clustering/          # Layer 4: Semantic Clustering & Theme Labeling
│   ├── embeddings.py    # Generates MiniLM embeddings (memory-resilient, offline-friendly)
│   ├── cluster.py       # DBSCAN semantic grouping + PCA dimensionality reduction
│   ├── label_prompts.py # Prompt to synthesize cluster quotes into actionable themes
│   └── label_themes.py  # Cluster centroid-quote selector & Groq theme writer
│
├── insights/            # Layer 5 & 6: Hypothesis Synthesis & 5-Gate Validation
│   ├── prompts.py       # Growth PM prompt to formulate testable growth hypotheses
│   ├── synthesize.py    # Formulates insights & "If-Then-Leading-To" hypotheses per theme
│   ├── validate.py      # 5-Gate Validation: Volume, Diversity, SentStd, Temporal, & Agreement
│   ├── segments.py      # Hardcoded definitions for the 5 archetypal user segments
│   └── export.py        # Aggregates everything into unified insights_export.json data feed
│
├── dashboard/           # Layer 7: PM Presentation Layer (Next.js Dashboard)
│   ├── app/page.js      # Interactive, 5-tab, search-enabled dashboard page (Recharts)
│   └── public/          # Stores insights_export.json dynamic API database mock
│
├── data/                # Database and Static Cache Storage
│   ├── schema.sql       # Table definitions (documents, analysis, themes, insights)
│   ├── db_init.py       # Creates SQLite discovery.db and runs schema script
│   └── clusters.png     # Scatter plot of DBSCAN semantic cluster coordinates
│
└── run_pipeline.py      # Single command to execute all pipeline stages sequentially
```

---

## 🛠️ Local Quick Start

### 1. Clone & Install Dependencies
Ensure you have Python 3.12+ (tested up to 3.14 on Windows) and Node.js LTS installed.

```bash
# Clone the repository
git clone https://github.com/your-username/Zepto_AIDiscovery-Engine.git
cd Zepto_AIDiscovery-Engine

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials.
```bash
cp .env.example .env
```
*Note: If `GROQ_API_KEY` is not present, the pipeline automatically operates in **Offline / Mock Fallback mode**, enabling complete testing of downstream clustering, insights, validation, and dashboard rendering without hitting API limits or requiring keys.*

### 3. Run the Database Initializer
Initialize the local SQLite database schema.
```bash
python data/db_init.py
```

### 4. Run the Full Ingestion & Synthesis Pipeline
Runs scrapers, cleans PII, runs sentiment/driver analysis, clusters semantic themes, generates testable growth hypotheses, validates confidence levels, and exports data.
```bash
python run_pipeline.py
```

### 5. Launch the Dashboard
```bash
cd dashboard
npm install
npm run dev
# Open http://localhost:3000 in your browser
```

---

## 📊 Dashboard Views (Zepto Brand Aesthetic)

The dashboard is built to match Zepto's visual guidelines (deep purple `#3E0075`, magenta `#E21A84` accents, and category sidebar active states):
*   **Executive Summary:** High-level metrics, category opportunity hotspots (bar charts), source distributions (donut charts), and top growth insights.
*   **Theme Explorer:** Semantic clusters with average sentiment bars, key driver tags, and actual representative customer quotes.
*   **Research Questions:** High-fidelity answers addressing the 8 core strategic research questions (Q1–Q8) with evidence ratings.
*   **User Segments:** Dynamic profiles of the 5 key Quick-Commerce archetypes (Curious Browsers, Value Seekers, Habitual Minimalists, Life-Stage Movers, Loyalists) with custom product recommendations.
*   **Source Monitor:** Connectivity tables detailing average ratings, documentation counts, and word-density per source.

---

## 🚀 Production Cloud Deployment ($0 Cost)

### 1. Deploy API & Pipeline Backend to [Railway](https://railway.app)
1. Install Railway CLI and login:
   ```bash
   npm install -g @railway/cli
   railway login
   ```
2. Initialize project and link your GitHub repository.
3. Configure the environment variables in the Railway dashboard (`GROQ_API_KEY`, etc.).
4. Add a persistent storage volume and mount it to `/data` so your SQLite database persists across deploys.
5. Deploy:
   ```bash
   railway up
   ```

### 2. Deploy Dashboard Frontend to [Vercel](https://vercel.com)
1. Connect your repository to Vercel.
2. Set the build output directory to the Next.js standard.
3. Set environment variable: `NEXT_PUBLIC_API_URL` to point to your Railway API endpoint.
4. Push to `main` — Vercel will auto-deploy your frontend.

---

## 📋 Definition of Done Validation Check
- [x] Ingests **500+ raw documents** across 4 platforms (Play Store, Reddit, Twitter, Forums).
- [x] Cleans text, redacts email/phone PII, and filters exact duplicates.
- [x] Maps customer sentiments, emotions, categories, and behavioral sub-drivers.
- [x] Density DBSCAN groups similar complaints and UMAP/PCA plots clusters.
- [x] Formulates PM growth hypotheses in `"If we X, then Y, leading to Z"` templates.
- [x] Validates findings using a **5-Gate validation framework** (High/Medium/Low confidence).
- [x] Exports structured data feed for real-time dashboard loading.
- [x] Dashboard UI matches Zepto's design language, colors, and layout structure.
- [x] Executable through a single orchestrator command (`python run_pipeline.py`).
