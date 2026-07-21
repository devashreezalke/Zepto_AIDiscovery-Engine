# Architecture: Zepto AI-Powered Discovery Engine

> **Version:** 1.0  
> **Date:** July 2026  
> **Owner:** Growth Team, Zepto  
> **Objective:** Design a scalable AI system that ingests user-generated feedback from 7+ sources, extracts behavioral themes, and produces PM-grade insights to drive cross-category discovery.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture Diagram](#2-high-level-architecture-diagram)
3. [Layer 1 — Data Ingestion & Collection](#3-layer-1--data-ingestion--collection)
4. [Layer 2 — Data Processing & Normalization](#4-layer-2--data-processing--normalization)
5. [Layer 3 — AI Analysis Pipeline](#5-layer-3--ai-analysis-pipeline)
6. [Layer 4 — Theme Clustering & Pattern Recognition](#6-layer-4--theme-clustering--pattern-recognition)
7. [Layer 5 — Insight Generation & Recommendation Engine](#7-layer-5--insight-generation--recommendation-engine)
8. [Layer 6 — Validation & Quality Assurance](#8-layer-6--validation--quality-assurance)
9. [Layer 7 — Presentation & Delivery](#9-layer-7--presentation--delivery)
10. [Data Schema & Models](#10-data-schema--models)
11. [Technology Stack](#11-technology-stack)
12. [Infrastructure & Deployment](#12-infrastructure--deployment)
13. [Security & Compliance](#13-security--compliance)
14. [Scalability & Performance](#14-scalability--performance)
15. [Monitoring & Observability](#15-monitoring--observability)
16. [Cost Estimation Model](#16-cost-estimation-model)
17. [Phased Rollout Plan](#17-phased-rollout-plan)

---

## 1. System Overview

The Zepto AI Discovery Engine is a multi-layered data intelligence platform purpose-built to answer a single strategic question:

> **Why don't users explore new categories, and what can we do about it?**

The system operates as an **end-to-end pipeline** that moves user-generated feedback through seven discrete processing layers — from raw collection through AI-powered semantic analysis to validated, actionable insights delivered to the Growth PM dashboard.

### Design Principles

| Principle | Description |
|---|---|
| **Source-Agnostic Ingestion** | Every data source (Reddit, App Store, Play Store, etc.) is abstracted behind a unified connector interface. Adding a new source requires only a new adapter — zero changes to downstream processing. |
| **LLM-Augmented, Not LLM-Dependent** | The system uses LLMs for semantic enrichment and synthesis but falls back gracefully to statistical NLP (TF-IDF, keyword extraction) if the LLM layer is unavailable or rate-limited. |
| **Evidence-Grounded Insights** | Every insight must trace back to a minimum number of source documents. No hallucinated or unsupported conclusions. |
| **Incremental Processing** | The pipeline processes new data incrementally (not full re-runs), enabling near-real-time theme tracking without reprocessing the entire corpus. |
| **Human-in-the-Loop** | PMs can review, override, merge, or split themes — and those corrections feed back into the classification prompts, improving accuracy over time. |

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          ZEPTO AI DISCOVERY ENGINE                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 1: DATA INGESTION                              │   │
│  │                                                                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │   │
│  │  │App Store │ │Play Store│ │  Reddit  │ │  Forums  │ │  Social  │      │   │
│  │  │Connector │ │Connector │ │Connector │ │Connector │ │ Media    │      │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │   │
│  │       │             │            │             │            │             │   │
│  └───────┼─────────────┼────────────┼─────────────┼────────────┼────────────┘   │
│          │             │            │             │            │                 │
│          ▼             ▼            ▼             ▼            ▼                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 2: PROCESSING & NORMALIZATION                   │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ Deduplication │  │ Language     │  │ Schema       │                   │   │
│  │  │ & Filtering   │  │ Detection    │  │ Normalization│                   │   │
│  │  └──────┬────────┘  └──────┬───────┘  └──────┬───────┘                   │   │
│  └─────────┼──────────────────┼─────────────────┼───────────────────────────┘   │
│            │                  │                  │                               │
│            ▼                  ▼                  ▼                               │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 3: AI ANALYSIS PIPELINE                         │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ Sentiment    │  │ Category     │  │ Behavioral   │                   │   │
│  │  │ Analysis     │  │ Detection    │  │ Driver       │                   │   │
│  │  │              │  │              │  │ Extraction   │                   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │   │
│  └─────────┼─────────────────┼─────────────────┼────────────────────────────┘   │
│            │                 │                  │                                │
│            ▼                 ▼                  ▼                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 4: THEME CLUSTERING                             │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ Embedding    │  │ HDBSCAN      │  │ LLM Theme    │                   │   │
│  │  │ Generation   │  │ Clustering   │  │ Labeling     │                   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │   │
│  └─────────┼─────────────────┼─────────────────┼────────────────────────────┘   │
│            │                 │                  │                                │
│            ▼                 ▼                  ▼                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                    LAYER 5: INSIGHT GENERATION                           │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │   │
│  │  │ Cross-Theme  │  │ Hypothesis   │  │ Segment      │                   │   │
│  │  │ Synthesis    │  │ Formulation  │  │ Profiling    │                   │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                   │   │
│  └─────────┼─────────────────┼─────────────────┼────────────────────────────┘   │
│            │                 │                  │                                │
│            ▼                 ▼                  ▼                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │           LAYER 6: VALIDATION & QUALITY ASSURANCE                       │   │
│  └─────────────────────────────────┬────────────────────────────────────────┘   │
│                                    │                                            │
│                                    ▼                                            │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │           LAYER 7: PRESENTATION & DELIVERY (Dashboard / API)            │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1 — Data Ingestion & Collection

This layer is responsible for reliably collecting raw user-generated content from all target platforms.

### 3.1 Connector Architecture

Every data source is accessed through a **Source Connector** — a modular adapter that implements a common interface:

```python
class BaseConnector(ABC):
    """
    Abstract base class for all data source connectors.
    Each connector handles authentication, pagination, rate-limiting,
    and incremental fetching for its specific platform.
    """

    @abstractmethod
    def authenticate(self) -> None:
        """Establish authenticated session with the data source."""
        pass

    @abstractmethod
    def fetch_incremental(self, since: datetime) -> List[RawDocument]:
        """Fetch new documents since the last checkpoint."""
        pass

    @abstractmethod
    def get_source_metadata(self) -> SourceMetadata:
        """Return metadata about this source (name, type, rate limits)."""
        pass
```

### 3.2 Source-Specific Connectors

| Source | Connector Type | Method | Rate Limits | Data Fields |
|---|---|---|---|---|
| **App Store (iOS)** | `AppStoreConnector` | Apple RSS Feed / App Store Connect API | 20 req/min | Review text, rating, date, app version, country |
| **Play Store (Android)** | `PlayStoreConnector` | `google-play-scraper` library | 30 req/min (throttled) | Review text, rating, thumbs up, date, device |
| **Reddit** | `RedditConnector` | PRAW (Reddit API wrapper) | 60 req/min (OAuth) | Post title, body, comments, subreddit, score, date |
| **Community Forums** | `ForumConnector` | Scrapy spiders / RSS feeds | Varies per site | Thread title, post body, replies, author, date |
| **Social Media** | `SocialMediaConnector` | snscrape (Twitter/X), BeautifulSoup (public pages) | No API key needed | Post text, engagement metrics, hashtags, date |
| **Product Reviews** | `ProductReviewConnector` | E-commerce APIs / Scraping | Varies | Review text, rating, product name, category, date |
| **Quick-Commerce Discussions** | `QCommerceConnector` | Custom scrapers (blogs, comparison sites) | Throttled | Article/comment text, platform mentioned, date |

### 3.3 Ingestion Scheduler

```
┌───────────────────────────────────────────────────┐
│              INGESTION SCHEDULER                  │
│                                                   │
│  Schedule:                                        │
│  ├── App Store / Play Store  → Every 6 hours      │
│  ├── Reddit                  → Every 2 hours      │
│  ├── Social Media            → Every 4 hours      │
│  ├── Forums                  → Every 12 hours     │
│  └── Product Reviews         → Every 24 hours     │
│                                                   │
│  Features:                                        │
│  ├── Checkpoint tracking (last_fetched_at)        │
│  ├── Automatic retry with exponential backoff     │
│  ├── Dead-letter queue for persistent failures    │
│  └── Alerting on >3 consecutive failures          │
└───────────────────────────────────────────────────┘
```

### 3.4 Raw Data Store

All ingested data is immediately written to a **Raw Data Lake** (append-only) before any processing:

- **Storage:** Local filesystem or self-hosted MinIO (S3-compatible, open-source) partitioned by `source/year/month/day/`
- **Format:** JSON Lines (`.jsonl`) for streaming compatibility
- **Retention:** 24 months (configurable)
- **Purpose:** Immutable audit trail; enables full reprocessing if pipeline logic changes

---

## 4. Layer 2 — Data Processing & Normalization

Raw data from heterogeneous sources must be cleaned, deduplicated, and normalized into a uniform schema before AI analysis.

### 4.1 Processing Pipeline Steps

```
Raw Document
    │
    ▼
┌──────────────────┐
│  1. DEDUPLICATION │  ← Exact + near-duplicate detection (MinHash / SimHash)
│     & SPAM        │  ← Bot detection, promotional content filtering
│     FILTERING     │  ← Minimum length threshold (>15 chars)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. LANGUAGE      │  ← Detect language (fastText / langdetect)
│     DETECTION     │  ← Filter to supported languages (English, Hindi, Hinglish)
│     & TRANSLATION │  ← Optional: Translate non-English to English via Groq API (free tier)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. PII           │  ← Redact emails, phone numbers, names
│     REDACTION     │  ← Replace with [PII_REDACTED] tokens
│                   │  ← Uses regex patterns + NER model
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  4. SCHEMA        │  ← Map source-specific fields to unified schema
│     NORMALIZATION │  ← Assign unique document_id (UUID v4)
│                   │  ← Validate required fields
└────────┬─────────┘
         │
         ▼
   Normalized Document (stored in ProcessedDocuments table)
```

### 4.2 Unified Document Schema

```json
{
  "document_id": "uuid-v4",
  "source": "reddit | app_store | play_store | forum | social_media | product_review | qcommerce",
  "source_url": "https://...",
  "source_document_id": "platform-specific-id",
  "content": "The cleaned, normalized text content",
  "content_language": "en",
  "author_id_hash": "sha256-hashed-author-id",
  "timestamp": "2026-07-10T14:30:00Z",
  "metadata": {
    "rating": 4,
    "upvotes": 23,
    "subreddit": "r/quickcommerce",
    "app_version": "7.4.2",
    "device": "Android",
    "country": "IN",
    "engagement_score": 0.78
  },
  "processing": {
    "ingested_at": "2026-07-10T15:00:00Z",
    "processed_at": "2026-07-10T15:01:23Z",
    "pipeline_version": "1.2.0",
    "is_duplicate": false,
    "is_spam": false,
    "word_count": 87
  }
}
```

### 4.3 Deduplication Strategy

| Level | Method | Purpose |
|---|---|---|
| **Exact** | SHA-256 hash of `content` field | Catch identical cross-posts |
| **Near-Duplicate** | MinHash with Jaccard similarity > 0.85 | Catch rephrased/similar reviews |
| **Cross-Source** | Semantic embedding cosine similarity > 0.95 | Catch same user posting on Reddit + Play Store |

---

## 5. Layer 3 — AI Analysis Pipeline

The core intelligence layer. Each normalized document is enriched with structured attributes using a combination of **LLM-based extraction** and **classical NLP fallbacks**.

### 5.1 Enrichment Pipeline

Every document passes through three parallel enrichment modules:

#### Module A: Sentiment & Emotion Analysis

```python
# LLM Prompt Template (simplified)
SENTIMENT_PROMPT = """
Analyze the following user feedback about a quick-commerce platform.

Text: "{content}"

Return a JSON object with:
- "sentiment": "positive" | "negative" | "neutral" | "mixed"
- "sentiment_score": float between -1.0 (very negative) and 1.0 (very positive)
- "emotions": list of detected emotions from:
  ["frustration", "satisfaction", "confusion", "excitement",
   "disappointment", "trust", "anxiety", "delight"]
- "emotion_intensity": "low" | "medium" | "high"
"""
```

**Fallback:** VADER sentiment + TextBlob subjectivity if LLM is unavailable.

#### Module B: Category & Product Detection

Maps mentions in the text to Zepto's internal category taxonomy:

```
Zepto Category Taxonomy (L1 → L2):
├── Groceries
│   ├── Fruits & Vegetables
│   ├── Dairy & Bread
│   ├── Rice, Atta & Dals
│   └── Oils, Masalas & Condiments
├── Snacks & Beverages
│   ├── Chips & Namkeen
│   ├── Chocolates & Sweets
│   └── Cold Drinks & Juices
├── Household Essentials
│   ├── Cleaning Supplies
│   ├── Detergents
│   └── Kitchen Essentials
├── Personal Care
│   ├── Skin Care
│   ├── Hair Care
│   └── Oral Care
├── Baby Care
│   ├── Diapers & Wipes
│   ├── Baby Food
│   └── Baby Accessories
├── Pet Supplies
│   ├── Pet Food
│   └── Pet Accessories
├── Electronics & Accessories
├── Pharma & Wellness
└── Home & Kitchen
```

The LLM extracts:
- **Mentioned Categories:** Which L1/L2 categories the user talks about
- **Purchased Categories:** Categories the user has bought from (stated or implied)
- **Desired Categories:** Categories the user expresses interest in but hasn't purchased

#### Module C: Behavioral Driver Extraction

This is the most critical module — it classifies *why* users behave the way they do:

```
Behavioral Driver Taxonomy:
│
├── HABIT_LOOP
│   ├── comfort_with_known_products
│   ├── auto_reorder_dependency
│   └── cognitive_load_avoidance
│
├── DISCOVERY_FRICTION
│   ├── poor_search_navigation
│   ├── category_not_visible
│   ├── no_personalized_recommendations
│   └── overwhelming_product_options
│
├── TRUST_BARRIER
│   ├── quality_uncertainty_new_category
│   ├── freshness_concerns
│   ├── brand_unfamiliarity
│   └── return_policy_doubts
│
├── VALUE_PERCEPTION
│   ├── price_higher_than_alternatives
│   ├── no_bundle_or_trial_offers
│   ├── delivery_fee_for_small_orders
│   └── perceived_value_mismatch
│
├── INFORMATION_GAP
│   ├── missing_product_details
│   ├── no_reviews_for_new_products
│   ├── insufficient_images
│   └── unclear_sizing_or_specs
│
├── CONTEXTUAL_TRIGGER
│   ├── seasonal_or_event_based_need
│   ├── life_stage_change
│   ├── recommendation_from_peer
│   └── social_media_influence
│
└── PLATFORM_LIMITATION
    ├── limited_selection_in_category
    ├── delivery_time_too_long
    ├── stock_availability_issues
    └── app_performance_issues
```

### 5.2 Enrichment Output Schema

Each document is augmented with an `analysis` block:

```json
{
  "document_id": "uuid-v4",
  "analysis": {
    "sentiment": {
      "label": "negative",
      "score": -0.72,
      "emotions": ["frustration", "disappointment"],
      "intensity": "high"
    },
    "categories": {
      "mentioned": ["Groceries", "Personal Care"],
      "purchased": ["Groceries"],
      "desired": ["Personal Care"],
      "category_switching_signal": true
    },
    "behavioral_drivers": [
      {
        "driver": "TRUST_BARRIER.quality_uncertainty_new_category",
        "confidence": 0.89,
        "evidence_span": "I want to try skincare from Zepto but not sure about the quality"
      },
      {
        "driver": "INFORMATION_GAP.no_reviews_for_new_products",
        "confidence": 0.76,
        "evidence_span": "there are no reviews for most personal care items"
      }
    ],
    "research_question_mapping": ["Q2_discovery_barriers", "Q5_information_needs"],
    "llm_model": "llama-3.3-70b-versatile (via Groq)",
    "analysis_version": "1.2.0",
    "analyzed_at": "2026-07-10T15:02:45Z"
  }
}
```

### 5.3 Research Question Mapping

Every enriched document is tagged with the specific research questions (from the problem statement) it helps answer:

| Tag | Research Question |
|---|---|
| `Q1_habit_formation` | Why do users repeatedly buy from the same categories? |
| `Q2_discovery_barriers` | What prevents users from exploring new categories? |
| `Q3_discovery_mechanisms` | How do users discover products today? |
| `Q4_role_of_habits` | What role do habits play in shopping behavior? |
| `Q5_information_needs` | What information do users need before trying a new category? |
| `Q6_pain_points` | What frustrations emerge repeatedly? |
| `Q7_user_segments` | Which user segments are more likely to experiment? |
| `Q8_unmet_needs` | What unmet needs emerge consistently across discussions? |

---

## 6. Layer 4 — Theme Clustering & Pattern Recognition

Individual document-level analysis is aggregated into **Themes** — coherent, named clusters of feedback that represent a shared concern, behavior, or unmet need.

### 6.1 Clustering Pipeline

```
Enriched Documents
        │
        ▼
┌────────────────────────────┐
│  1. EMBEDDING GENERATION   │
│                            │
│  Model: all-MiniLM-L6-v2   │
│  (sentence-transformers)   │
│  Dimensions: 384           │
│  Input: content + driver   │
│  Output: dense vector      │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│  2. DIMENSIONALITY         │
│     REDUCTION              │
│                            │
│  Algorithm: UMAP           │
│  n_components: 50          │
│  n_neighbors: 15           │
│  min_dist: 0.1             │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│  3. DENSITY-BASED          │
│     CLUSTERING             │
│                            │
│  Algorithm: HDBSCAN        │
│  min_cluster_size: 10      │
│  min_samples: 5            │
│  metric: euclidean         │
│                            │
│  Output: cluster_id or -1  │
│  (noise/outlier)           │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│  4. LLM THEME LABELING    │
│                            │
│  For each cluster:         │
│  - Sample 20 documents     │
│  - LLM generates:          │
│    • Theme title            │
│    • 2-sentence summary    │
│    • Key behavioral driver │
│    • Affected categories   │
│    • Research questions     │
└───────────┬────────────────┘
            │
            ▼
      Theme Registry
```

### 6.2 Theme Schema

```json
{
  "theme_id": "TH-2026-0042",
  "title": "Quality Anxiety Blocks Personal Care Exploration",
  "summary": "Users who buy groceries from Zepto express interest in purchasing personal care products but hesitate due to uncertainty about product authenticity and quality. The absence of detailed product reviews and ingredient lists amplifies this trust deficit.",
  "macro_theme": "Trust & Quality Barriers",
  "behavioral_drivers": ["TRUST_BARRIER.quality_uncertainty_new_category", "INFORMATION_GAP.no_reviews_for_new_products"],
  "affected_categories": {
    "source_categories": ["Groceries", "Snacks & Beverages"],
    "blocked_categories": ["Personal Care", "Baby Care"]
  },
  "research_questions": ["Q2_discovery_barriers", "Q5_information_needs"],
  "statistics": {
    "document_count": 347,
    "source_distribution": {
      "reddit": 142,
      "play_store": 98,
      "app_store": 56,
      "social_media": 31,
      "forums": 20
    },
    "avg_sentiment_score": -0.58,
    "dominant_emotions": ["frustration", "anxiety"],
    "temporal_trend": "increasing",
    "first_seen": "2026-01-15",
    "last_updated": "2026-07-10"
  },
  "representative_quotes": [
    {
      "document_id": "uuid-1",
      "source": "reddit",
      "text": "I order groceries weekly from Zepto but would never buy skincare there. How do I know if it's genuine?",
      "sentiment_score": -0.65
    },
    {
      "document_id": "uuid-2",
      "source": "play_store",
      "text": "Great for daily essentials but the personal care section has zero reviews. Not risking it.",
      "sentiment_score": -0.48
    }
  ],
  "created_at": "2026-07-10T16:00:00Z",
  "status": "active",
  "pm_reviewed": false
}
```

### 6.3 Theme Hierarchy

Themes are organized in a two-level hierarchy:

```
Macro-Themes (5–8 top-level groups)
│
├── Trust & Quality Barriers
│   ├── TH-0042: Quality Anxiety Blocks Personal Care Exploration
│   ├── TH-0043: Freshness Concerns Limit Produce Category Expansion
│   └── TH-0044: Brand Authenticity Doubts in Electronics
│
├── Discovery & Navigation Friction
│   ├── TH-0051: Categories Hidden Behind Deep Navigation
│   ├── TH-0052: Search Does Not Surface Cross-Category Suggestions
│   └── TH-0053: Homepage Dominated by Grocery — Other Categories Invisible
│
├── Habitual Behavior & Cognitive Load
│   ├── TH-0061: Reorder Button Reinforces Repetitive Behavior
│   ├── TH-0062: Users Treat Zepto as Single-Category Utility
│   └── TH-0063: Decision Fatigue Prevents Category Browsing
│
├── Pricing & Value Perception
│   ├── TH-0071: Premium Pricing on Non-Grocery Categories
│   └── TH-0072: No Trial/Sample Offers for New Categories
│
├── Information & Content Gaps
│   ├── TH-0081: Insufficient Product Descriptions
│   └── TH-0082: Missing User Reviews in New Categories
│
└── Platform & Experience Limitations
    ├── TH-0091: Limited SKU Depth in Niche Categories
    └── TH-0092: Delivery Slot Availability for Combined Orders
```

### 6.4 Theme Drift Detection

The system monitors themes over time:
- **Emerging Themes:** New clusters that didn't exist in the prior analysis window
- **Growing Themes:** Clusters with >20% increase in document count week-over-week
- **Declining Themes:** Clusters losing volume (possibly due to a fix being shipped)
- **Seasonal Themes:** Clusters that spike around events (festivals, back-to-school)

---

## 7. Layer 5 — Insight Generation & Recommendation Engine

Themes are synthesized into **PM-grade insights** — structured findings that directly inform product decisions.

### 7.1 Insight Generation Process

```
Theme Clusters
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                  INSIGHT SYNTHESIS (LLM)                 │
│                                                          │
│  For each theme (or cross-theme pattern):                │
│                                                          │
│  1. FINDING: What is happening? (descriptive)            │
│  2. ROOT CAUSE: Why is it happening? (diagnostic)        │
│  3. IMPACT: How does it affect cross-category            │
│     discovery? (quantified where possible)               │
│  4. USER SEGMENT: Who is most affected?                  │
│  5. HYPOTHESIS: What product/marketing intervention      │
│     could address this? (prescriptive)                   │
│  6. EVIDENCE: Supporting quotes, volume, sentiment       │
│  7. CONFIDENCE: Statistical confidence rating            │
└──────────────────────────────────────────────────────────┘
```

### 7.2 Insight Schema

```json
{
  "insight_id": "INS-2026-0015",
  "title": "Trust Deficit Is the #1 Barrier to Personal Care Category Entry",
  "finding": "34% of users who discuss quick-commerce personal care express quality/authenticity concerns. This is 2.4x higher than the trust concern rate for grocery categories.",
  "root_cause": "Users associate quick-commerce platforms with convenience purchases (groceries, snacks) and do not have a mental model for quality assurance in personal care. The absence of reviews, ratings, and brand-verification badges in non-grocery categories reinforces this perception.",
  "impact": {
    "affected_mac_percentage_estimate": "12-18%",
    "blocked_category": "Personal Care",
    "annual_gmv_opportunity_estimate": "₹XX Cr (based on average Personal Care basket size × addressable MACs)"
  },
  "target_segment": {
    "description": "Regular grocery buyers (3+ orders/month) who have never purchased Personal Care on Zepto",
    "estimated_size": "~2.1M MACs",
    "behavioral_profile": "High platform trust for groceries, active review readers, price-conscious"
  },
  "hypotheses": [
    {
      "id": "H1",
      "statement": "If we display a 'Verified Authentic' badge on Personal Care products from known brands, then trust-related category-entry conversions will increase by 15-25%.",
      "experiment_type": "A/B test",
      "effort": "medium",
      "expected_impact": "high"
    },
    {
      "id": "H2",
      "statement": "If we seed the first 50 reviews on top Personal Care SKUs (via power-user program), then browse-to-purchase conversion will increase by 10-20%.",
      "experiment_type": "Pre/post analysis",
      "effort": "low",
      "expected_impact": "medium"
    }
  ],
  "supporting_themes": ["TH-0042", "TH-0082"],
  "evidence_strength": {
    "document_count": 347,
    "source_diversity": 5,
    "temporal_consistency": "6+ months",
    "cross_platform_agreement": true,
    "confidence_level": "high"
  },
  "research_questions_addressed": ["Q2_discovery_barriers", "Q5_information_needs", "Q7_user_segments"],
  "status": "pending_review",
  "generated_at": "2026-07-10T17:00:00Z"
}
```

### 7.3 Cross-Theme Synthesis

The engine also performs **cross-theme analysis** to identify compounding effects:

```
Example Cross-Theme Insight:

  Theme A: "Quality Anxiety Blocks Personal Care" (Trust)
  Theme B: "Missing User Reviews in New Categories" (Information)
  Theme C: "No Trial/Sample Offers" (Value)

  Cross-Theme Insight:
  "Trust, information, and value barriers compound for Personal Care.
   Users need TRUST (authenticity proof) + INFORMATION (reviews) + VALUE
   (low-risk trial) simultaneously before category entry. Addressing only
   one in isolation will not move the conversion needle significantly."
```

### 7.4 User Segment Profiling

Based on behavioral patterns detected across documents, the engine builds **archetypal user segments**:

| Segment | Description | Estimated Size | Cross-Category Potential |
|---|---|---|---|
| **Habitual Minimalists** | Buy 5-10 SKUs from 1-2 categories, reorder same list weekly | ~35% of MACs | Low — need strong nudges |
| **Curious Browsers** | Browse multiple categories, add to cart but abandon non-grocery items | ~15% of MACs | **Very High** — lowest barrier to conversion |
| **Value Seekers** | Compare prices across platforms, only buy deals/offers | ~20% of MACs | Medium — price-sensitive but open to new categories on discount |
| **Life-Stage Movers** | Users going through life changes (new parent, new pet, new home) | ~10% of MACs | **High** — active need for new categories |
| **Loyalists** | High trust, high frequency, often leave reviews | ~20% of MACs | Medium — respond to recommendations from trusted platform |

---

## 8. Layer 6 — Validation & Quality Assurance

Every insight produced must pass a multi-gate validation process to ensure reliability.

### 8.1 Validation Framework

```
┌─────────────────────────────────────────────────────────┐
│                VALIDATION GATES                         │
│                                                         │
│  Gate 1: SOURCE GROUNDING                               │
│  ├── Every claim must cite ≥ 5 source documents         │
│  ├── Sources must span ≥ 2 different platforms          │
│  └── Representative quotes must be real, unedited       │
│                                                         │
│  Gate 2: STATISTICAL SIGNIFICANCE                       │
│  ├── Theme must have ≥ 10 documents                     │
│  ├── Sentiment score std. dev. must be < 0.3            │
│  │   (i.e., documents within theme agree)               │
│  └── Theme must not be a single-day spike (≥ 7d span)   │
│                                                         │
│  Gate 3: CROSS-PLATFORM TRIANGULATION                   │
│  ├── Theme must appear in ≥ 2 source platforms          │
│  └── Sentiment direction must be consistent across      │
│       platforms (prevents platform-specific bias)        │
│                                                         │
│  Gate 4: TEMPORAL STABILITY                             │
│  ├── Theme must persist across ≥ 2 analysis windows     │
│  └── Not a one-off event or viral complaint             │
│                                                         │
│  Gate 5: LLM SELF-CONSISTENCY CHECK                     │
│  ├── Re-run analysis with different prompt framings      │
│  ├── Compare outputs: if <80% agreement, flag for       │
│  │   human review                                       │
│  └── Temperature=0 for deterministic outputs            │
│                                                         │
│  Gate 6: HUMAN-IN-THE-LOOP REVIEW                       │
│  ├── PM reviews flagged insights on dashboard           │
│  ├── Can approve, reject, merge, or refine              │
│  └── Corrections feed back into prompt tuning           │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Confidence Scoring

Each insight receives a composite confidence score:

```
Confidence Score = weighted average of:
  ├── Volume Weight (0.25)    → Based on document count (log-scaled)
  ├── Diversity Weight (0.20) → Based on source platform diversity
  ├── Consistency Weight (0.20) → Sentiment agreement within cluster
  ├── Temporal Weight (0.15)  → Duration of theme persistence
  └── LLM Agreement (0.20)   → Self-consistency check score

Rating Thresholds:
  ├── ≥ 0.80  →  HIGH confidence    (auto-publish to dashboard)
  ├── 0.60–0.79 → MEDIUM confidence (publish with flag)
  └── < 0.60  →  LOW confidence     (requires PM review before publishing)
```

---

## 9. Layer 7 — Presentation & Delivery

### 9.1 Growth PM Dashboard

The primary interface for consuming insights. Built as a web application with the following views:

#### View 1: Executive Summary
- Top 5 insights by impact potential
- Category expansion opportunity heatmap
- Week-over-week theme trend chart

#### View 2: Theme Explorer
- Interactive cluster visualization (2D UMAP projection)
- Click-to-drill into any theme → supporting documents
- Filter by: source, category, driver, sentiment, time range

#### View 3: Research Question Tracker
- For each of the 8 research questions:
  - Number of supporting themes
  - Top insights
  - Evidence strength indicator

#### View 4: Segment Profiles
- User segment cards with behavioral profiles
- Cross-category opportunity per segment
- Recommended intervention per segment

#### View 5: Source Monitor
- Ingestion health: documents per source per day
- Data freshness indicators
- Anomaly alerts (spike in negative sentiment, new topic emergence)

### 9.2 API Layer

RESTful API for programmatic access:

```
Base URL: /api/v1/discovery

Endpoints:
  GET   /insights                   → List all insights (paginated, filterable)
  GET   /insights/{insight_id}      → Get single insight with full evidence
  GET   /themes                     → List all active themes
  GET   /themes/{theme_id}          → Get theme detail with documents
  GET   /themes/{theme_id}/trend    → Get temporal trend for a theme
  GET   /segments                   → List all user segments
  GET   /research-questions         → Get status of all 8 research questions
  GET   /sources/health             → Ingestion pipeline health check
  POST  /insights/{id}/review       → Submit PM review (approve/reject/modify)
  POST  /query                      → Natural language query against the corpus
```

### 9.3 Notification & Alerting

| Alert Type | Trigger | Channel |
|---|---|---|
| **New High-Confidence Insight** | Confidence ≥ 0.80 | Slack + Email |
| **Emerging Theme Detected** | New cluster with >20 docs in first 48h | Slack |
| **Sentiment Spike** | >30% increase in negative sentiment in any category | Slack + PagerDuty |
| **Data Ingestion Failure** | Any source fails 3+ consecutive fetches | PagerDuty |
| **Weekly Digest** | Every Monday 9:00 AM IST | Email |

---

## 10. Data Schema & Models

### 10.1 Database Schema (PostgreSQL)

```sql
-- Core tables
CREATE TABLE raw_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source          VARCHAR(50) NOT NULL,
    source_url      TEXT,
    source_doc_id   VARCHAR(255),
    content         TEXT NOT NULL,
    content_language VARCHAR(10) DEFAULT 'en',
    author_hash     VARCHAR(64),
    source_timestamp TIMESTAMPTZ,
    metadata        JSONB,
    ingested_at     TIMESTAMPTZ DEFAULT NOW(),
    connector_version VARCHAR(20)
);

CREATE TABLE processed_documents (
    id              UUID PRIMARY KEY REFERENCES raw_documents(id),
    clean_content   TEXT NOT NULL,
    word_count      INTEGER,
    is_duplicate    BOOLEAN DEFAULT FALSE,
    is_spam         BOOLEAN DEFAULT FALSE,
    processed_at    TIMESTAMPTZ DEFAULT NOW(),
    pipeline_version VARCHAR(20)
);

CREATE TABLE document_analysis (
    id              UUID PRIMARY KEY REFERENCES raw_documents(id),
    sentiment_label VARCHAR(20),
    sentiment_score FLOAT,
    emotions        TEXT[],
    emotion_intensity VARCHAR(10),
    categories_mentioned TEXT[],
    categories_purchased TEXT[],
    categories_desired TEXT[],
    category_switch_signal BOOLEAN DEFAULT FALSE,
    behavioral_drivers JSONB,
    research_questions TEXT[],
    llm_model       VARCHAR(50),
    analysis_version VARCHAR(20),
    analyzed_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE embeddings (
    document_id     UUID PRIMARY KEY REFERENCES raw_documents(id),
    embedding       VECTOR(384),  -- pgvector extension (matches all-MiniLM-L6-v2)
    model           VARCHAR(50),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE themes (
    id              VARCHAR(20) PRIMARY KEY,  -- e.g., TH-2026-0042
    title           VARCHAR(255) NOT NULL,
    summary         TEXT,
    macro_theme     VARCHAR(100),
    behavioral_drivers TEXT[],
    affected_source_categories TEXT[],
    affected_blocked_categories TEXT[],
    research_questions TEXT[],
    document_count  INTEGER,
    avg_sentiment   FLOAT,
    dominant_emotions TEXT[],
    temporal_trend  VARCHAR(20),
    first_seen      DATE,
    status          VARCHAR(20) DEFAULT 'active',
    pm_reviewed     BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE theme_documents (
    theme_id        VARCHAR(20) REFERENCES themes(id),
    document_id     UUID REFERENCES raw_documents(id),
    PRIMARY KEY (theme_id, document_id)
);

CREATE TABLE insights (
    id              VARCHAR(20) PRIMARY KEY,  -- e.g., INS-2026-0015
    title           VARCHAR(255) NOT NULL,
    finding         TEXT,
    root_cause      TEXT,
    impact          JSONB,
    target_segment  JSONB,
    hypotheses      JSONB,
    supporting_themes TEXT[],
    evidence_strength JSONB,
    confidence_score FLOAT,
    confidence_level VARCHAR(10),
    research_questions TEXT[],
    status          VARCHAR(20) DEFAULT 'pending_review',
    pm_feedback     JSONB,
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_raw_docs_source ON raw_documents(source);
CREATE INDEX idx_raw_docs_timestamp ON raw_documents(source_timestamp);
CREATE INDEX idx_analysis_sentiment ON document_analysis(sentiment_label);
CREATE INDEX idx_analysis_drivers ON document_analysis USING GIN(behavioral_drivers);
CREATE INDEX idx_themes_macro ON themes(macro_theme);
CREATE INDEX idx_insights_confidence ON insights(confidence_score DESC);
```

### 10.2 Vector Store

- **Engine:** PostgreSQL with `pgvector` extension (free, self-hosted) or ChromaDB (open-source, embedded)
- **Index Type:** IVFFlat or HNSW for approximate nearest neighbor search
- **Dimension:** 384 (matching `all-MiniLM-L6-v2` from sentence-transformers)
- **Distance Metric:** Cosine similarity

---

## 11. Technology Stack

> **Zero-Cost Principle:** Every component in this stack is free. We use Groq's free-tier API for LLM inference (no credit card required) and open-source tools for everything else.

| Layer | Technology | Cost | Rationale |
|---|---|---|---|
| **Language** | Python 3.11+ | Free | Rich ML/NLP ecosystem, team familiarity |
| **Web Framework** | FastAPI | Free | Async-native, auto-generated OpenAPI docs |
| **Task Queue** | Celery + Redis | Free | Reliable async job processing for pipeline |
| **Database** | PostgreSQL 16 + pgvector | Free | ACID compliance, JSONB support, vector search |
| **Object Storage** | MinIO (self-hosted) or local filesystem | Free | S3-compatible API, open-source, self-hosted |
| **LLM Provider** | Groq API free tier (Llama 3.3 70B primary, Mixtral 8x7B fallback) | Free | Ultra-fast inference (~500 tokens/sec), free API key, no credit card required |
| **Embeddings** | `all-MiniLM-L6-v2` (sentence-transformers) | Free | 384d, runs locally on CPU, high quality |
| **ML Libraries** | scikit-learn, HDBSCAN, UMAP, sentence-transformers | Free | Clustering and dimensionality reduction |
| **Scraping** | Scrapy, PRAW (Reddit), `google-play-scraper`, snscrape | Free | Source-specific data collection, no paid APIs |
| **Dashboard** | Next.js + React + Recharts | Free | Modern, responsive PM-facing UI |
| **Monitoring** | Prometheus + Grafana OSS (self-hosted) | Free | Pipeline health and performance metrics |
| **Orchestration** | Apache Airflow (self-hosted) or APScheduler | Free | DAG-based pipeline scheduling |
| **Containerization** | Docker + Docker Compose | Free | Lightweight, reproducible deployments |
| **CI/CD** | GitHub Actions (free tier) | Free | Automated testing and deployment |

---

## 12. Infrastructure & Deployment

### 12.1 Deployment Architecture (Railway + Vercel + Groq)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRODUCTION DEPLOYMENT                       │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    RAILWAY (Backend)                          │  │
│  │                    railway.app — Free Tier                    │  │
│  │                                                               │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐        │  │
│  │  │ FastAPI     │  │ Pipeline     │  │ SQLite DB    │        │  │
│  │  │ API Server  │  │ Worker       │  │ (Persistent  │        │  │
│  │  │ (REST)      │  │ (Scrapers +  │  │  Volume)     │        │  │
│  │  │             │  │  Analysis)   │  │              │        │  │
│  │  └──────┬──────┘  └──────┬───────┘  └──────────────┘        │  │
│  │         │                │                                    │  │
│  │         └────────┬───────┘                                    │  │
│  │                  ▼                                            │  │
│  │         ┌────────────────┐                                    │  │
│  │         │  Groq API      │                                    │  │
│  │         │  (Free Tier)   │                                    │  │
│  │         │  LLM Inference │                                    │  │
│  │         └────────────────┘                                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│                              │ JSON API                             │
│                              ▼                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    VERCEL (Frontend)                          │  │
│  │                    vercel.app — Free Tier                     │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐    │  │
│  │  │  Next.js Dashboard                                    │    │  │
│  │  │  ├── Executive Summary                                │    │  │
│  │  │  ├── Theme Explorer                                   │    │  │
│  │  │  ├── Research Questions                               │    │  │
│  │  │  ├── User Segments                                    │    │  │
│  │  │  └── Source Monitor                                   │    │  │
│  │  └──────────────────────────────────────────────────────┘    │  │
│  │                                                               │  │
│  │  CDN: Global edge network, automatic HTTPS, preview deploys   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

  Backend: Railway free tier ($5 credit, ~500 hrs/month)
  Frontend: Vercel free tier (100 GB bandwidth, unlimited deploys)
  LLM: Groq free tier (no credit card required)
  Total cost: $0
```

### 12.2 Platform Details

| Platform | Role | Free Tier Includes | URL |
|---|---|---|---|
| **Railway** | Python backend (FastAPI + pipeline) | $5 free credit/month, 500 hrs execution, 1 GB RAM, persistent volumes | [railway.app](https://railway.app) |
| **Vercel** | Next.js dashboard (frontend) | Unlimited deploys, 100 GB bandwidth, global CDN, automatic HTTPS, preview deploys | [vercel.com](https://vercel.com) |
| **Groq** | LLM inference (analysis + synthesis) | ~14,400 req/day, Llama 3.3 70B, no credit card | [console.groq.com](https://console.groq.com) |

### 12.3 Environment Strategy

| Environment | Frontend (Vercel) | Backend (Railway) | Cost |
|---|---|---|---|
| **Development** | `localhost:3000` | `localhost:8000` | $0 |
| **Preview** | Auto-deployed on every PR (Vercel preview URL) | Railway preview environment | $0 |
| **Production** | `your-app.vercel.app` (custom domain free) | `your-api.railway.app` | $0 |

### 12.4 Deployment Workflow

```
Git Push to main
       │
       ├──► Vercel auto-deploys dashboard
       │    └── Build: npm run build
       │    └── Live at: https://zepto-discovery.vercel.app
       │
       └──► Railway auto-deploys backend
            └── Build: pip install -r requirements.txt
            └── Start: uvicorn api.main:app --host 0.0.0.0 --port $PORT
            └── Live at: https://zepto-api.railway.app
```

---

## 13. Security & Compliance

| Concern | Mitigation |
|---|---|
| **PII in User Feedback** | All PII is redacted at Layer 2 before storage. Original raw data on local disk / MinIO is encrypted at rest and access-logged. |
| **API Authentication** | JWT-based auth for dashboard; API keys for programmatic access |
| **Data Encryption** | TLS 1.3 in transit (self-signed certs or Let's Encrypt — free); AES-256 at rest (MinIO + PostgreSQL) |
| **LLM Data Privacy** | All PII is redacted at Layer 2 **before** any text is sent to Groq. Only anonymized, cleaned text reaches the API. Groq does not use API data for training. |
| **Access Control** | RBAC: `admin`, `pm_editor`, `pm_viewer`, `developer` roles |
| **Audit Logging** | All API calls, PM reviews, and data exports are logged with timestamp + actor |
| **Data Retention** | Raw data: 24 months. Processed/analyzed data: indefinite. Configurable per source. |
| **Scraping Compliance** | Respect `robots.txt`, honor rate limits, use official free APIs where available |

---

## 14. Scalability & Performance

### 14.1 Performance Targets

| Metric | Target |
|---|---|
| Ingestion throughput | 10,000 documents/hour |
| Analysis latency (per document) | < 2 seconds (Groq runs at ~500 tokens/sec — fastest LLM inference available) |
| Clustering re-run (full corpus) | < 30 minutes for 100K documents |
| Dashboard page load | < 2 seconds (P95) |
| API response time | < 500ms (P95) for read endpoints |
| Natural language query | < 10 seconds |

### 14.2 Scaling Strategy

| Component | Scaling Method |
|---|---|
| **Connectors** | Horizontal: add more worker pods per source |
| **LLM Analysis** | Batch processing + async queuing; use `llama-3.1-8b-instant` (faster, smaller) for bulk re-analysis; reserve `llama-3.3-70b-versatile` for insight synthesis |
| **Embeddings** | CPU batch generation via sentence-transformers; optional GPU acceleration; cache embeddings in pgvector |
| **Clustering** | Run as scheduled batch job (not real-time); incremental updates for new documents |
| **Database** | Read replicas for dashboard queries; partitioning by `source_timestamp` |
| **Dashboard** | Nginx (free) for static assets; server-side rendering for initial load |

---

## 15. Monitoring & Observability

### 15.1 Key Dashboards (Grafana)

1. **Pipeline Health:** Documents ingested/processed/analyzed per hour, error rates, queue depths
2. **LLM Performance:** Latency, token usage, Groq rate limit utilization, error rate by model (track daily free-tier quota usage)
3. **Data Quality:** Spam detection rate, duplicate rate, PII redaction count
4. **Theme Metrics:** Active theme count, new themes detected, theme drift alerts
5. **Insight Metrics:** Insights generated, confidence distribution, PM review backlog

### 15.2 Alerting Rules

```yaml
alerts:
  - name: ingestion_failure
    condition: "source_fetch_errors > 3 consecutive"
    severity: critical
    channel: pagerduty

  - name: llm_latency_high
    condition: "p95_analysis_latency > 15s for 10min"
    severity: warning
    channel: slack

  - name: embedding_storage_full
    condition: "pgvector_table_size > 80% quota"
    severity: warning
    channel: slack

  - name: negative_sentiment_spike
    condition: "category_sentiment_score drops > 30% in 24h"
    severity: info
    channel: slack_growth_team
```

---

## 16. Cost Estimation Model

> **🎯 Total Monthly Cost: $0** — All components are free. LLM inference uses Groq's free-tier API (no credit card required). Everything else is open-source and self-hosted.

### 16.1 Monthly Cost Breakdown

| Component | Cost | Technology | Notes |
|---|---|---|---|
| **LLM Inference** | **$0** | Groq API free tier (Llama 3.3 70B, Mixtral 8x7B) | Free API key, no credit card. ~14,400 requests/day free. |
| **Embedding Generation** | **$0** | sentence-transformers (`all-MiniLM-L6-v2`) | Runs locally on CPU. ~0.5s per document. |
| **Database** | **$0** | PostgreSQL + pgvector (Docker) | Self-hosted, open-source. |
| **Object Storage** | **$0** | MinIO (Docker) or local filesystem | S3-compatible, self-hosted, open-source. |
| **Task Queue** | **$0** | Redis (Docker) | Self-hosted, open-source. |
| **Scraping / Data Collection** | **$0** | Scrapy, PRAW (free tier), snscrape, google-play-scraper | All open-source libraries, no paid APIs. |
| **Monitoring** | **$0** | Prometheus + Grafana OSS (Docker) | Self-hosted, open-source. |
| **Orchestration** | **$0** | Apache Airflow (Docker) or APScheduler | Self-hosted, open-source. |
| **Dashboard** | **$0** | Next.js + React + Recharts | Open-source, self-hosted. |
| **CI/CD** | **$0** | GitHub Actions (free tier for public repos) | 2,000 mins/month free for private repos. |
| **Total** | **$0/month** | — | Groq free tier + FOSS stack. Only cost is your own hardware electricity. |

### 16.2 Groq Free Tier Limits & How We Stay Within Them

| Resource | Groq Free Tier Limit | Our Usage Pattern |
|---|---|---|
| **Requests/min** | 30 | Batch queue with rate limiter; Celery worker throttled to 25 req/min |
| **Requests/day** | ~14,400 | Sufficient for ~14K documents/day enrichment |
| **Tokens/min** | 15,000 | Each document prompt ~300 tokens → ~50 docs/min comfortably |
| **Models available** | Llama 3.3 70B, Llama 3.1 8B, Mixtral 8x7B, Gemma 2 9B | We use 70B for quality, 8B for bulk/fallback |

**Rate Limit Strategy:**
- Celery workers use a token bucket rate limiter to stay under Groq's free-tier limits
- Insight synthesis (Layer 5) uses `llama-3.3-70b-versatile` for maximum quality
- Bulk enrichment (Layer 3) uses `llama-3.1-8b-instant` for speed and quota efficiency
- If daily quota is exhausted, remaining documents are queued for the next day automatically

### 16.3 Hardware Requirements (Lightweight — No Local LLM)

Since LLM inference runs on Groq's servers, hardware requirements are **much lower** than a local-LLM setup:

| Resource | Minimum | Recommended | Notes |
|---|---|---|---|
| **RAM** | 4 GB | 8 GB | No local model loading needed. RAM is for PostgreSQL, Redis, and embeddings. |
| **CPU** | 2 cores | 4 cores | For embedding generation (sentence-transformers) and pipeline orchestration. |
| **GPU** | Not needed | Not needed | All LLM inference handled by Groq cloud. Embeddings run fine on CPU. |
| **Disk** | 10 GB | 50 GB | Data storage only. No large model files to download. |

### 16.4 Free-Tier Cloud Alternatives (Optional)

If you want to deploy without owning hardware, these free-tier options work:

| Provider | Free Tier | Suitable For |
|---|---|---|
| **Oracle Cloud** | Always-free ARM VM (4 CPU, 24 GB RAM) | Running the entire stack (lightweight without local LLM) |
| **Google Cloud** | e2-micro VM (free forever) | Lightweight services (API, scheduler) |
| **Hugging Face Spaces** | Free CPU Spaces | Hosting the dashboard |
| **Render** | Free tier web services | API hosting |
| **Supabase** | Free PostgreSQL (500 MB) | Database for smaller datasets |

### 16.5 Why Zero Cost Works

- **Groq free tier is genuinely free:** No credit card required. Provides access to Llama 3.3 70B — a model that rivals GPT-4 on many benchmarks — at industry-leading speed (~500 tokens/sec).
- **No cloud storage bills:** MinIO provides S3-compatible storage on your own disk.
- **No embedding fees:** `all-MiniLM-L6-v2` runs on CPU in milliseconds — no GPU required.
- **No monitoring SaaS:** Prometheus + Grafana OSS are industry-standard and fully self-hosted.
- **No scraping costs:** All data sources use free APIs (Reddit free tier, RSS feeds) or open-source scraping libraries.
- **Minimal hardware:** Without a local LLM, even a 4 GB RAM laptop can run the full pipeline.

---

## 17. Phased Rollout Plan

### Phase 1 — Foundation (Weeks 1–3)

| Task | Deliverable |
|---|---|
| Set up project repo, CI/CD, Docker | Deployable skeleton |
| Implement App Store + Play Store connectors | First 2 data sources live |
| Build normalization pipeline (Layer 2) | Clean, deduplicated documents |
| Design and deploy PostgreSQL schema | Database ready |
| Basic ingestion scheduler | Automated data collection |

### Phase 2 — AI Core (Weeks 4–6)

| Task | Deliverable |
|---|---|
| Implement Reddit + Social Media connectors | 4 data sources live |
| Build LLM analysis pipeline (Layer 3) | Sentiment, category, driver extraction |
| Generate embeddings + vector storage | Searchable corpus |
| Implement HDBSCAN clustering (Layer 4) | First theme clusters |
| LLM theme labeling | Named, summarized themes |

### Phase 3 — Intelligence (Weeks 7–9)

| Task | Deliverable |
|---|---|
| Add Forum + Product Review connectors | All 7 sources live |
| Build insight generation engine (Layer 5) | PM-grade insights with hypotheses |
| Implement validation framework (Layer 6) | Confidence scoring + quality gates |
| Cross-theme synthesis | Compounding barrier detection |
| User segment profiling | 5 archetypal segments defined |

### Phase 4 — Delivery & Polish (Weeks 10–12)

| Task | Deliverable |
|---|---|
| Build PM dashboard (Layer 7) | Interactive web UI |
| Implement REST API | Programmatic access |
| Set up alerting & notifications | Slack/email alerts |
| Deploy monitoring stack | Grafana dashboards |
| PM user acceptance testing | Validated with Growth Team |
| Documentation & runbooks | Operational readiness |

---

## Appendix A: Glossary

| Term | Definition |
|---|---|
| **MAC** | Monthly Active Customer — a user who places at least one order in a calendar month |
| **Category Expansion** | A user purchasing from a category they have not bought from in the prior 90 days |
| **Theme** | A cluster of semantically similar user feedback united by a common concern or behavior |
| **Insight** | A structured, evidence-backed finding derived from one or more themes |
| **Behavioral Driver** | The underlying motivation or barrier that explains a user's shopping behavior |
| **Cross-Category Signal** | Text indicating a user's interest in or resistance to trying a new product category |
| **HDBSCAN** | Hierarchical Density-Based Spatial Clustering of Applications with Noise |
| **UMAP** | Uniform Manifold Approximation and Projection (dimensionality reduction) |

## Appendix B: Research Question → Architecture Mapping

| Research Question | Primary Layers | Key Outputs |
|---|---|---|
| Q1: Why same categories? | Layer 3 (Driver: HABIT_LOOP) → Layer 4 | Habit-related themes |
| Q2: What prevents exploration? | Layer 3 (Driver: DISCOVERY_FRICTION, TRUST_BARRIER) → Layer 5 | Barrier insights |
| Q3: How do users discover today? | Layer 3 (Driver: CONTEXTUAL_TRIGGER) → Layer 5 | Discovery mechanism report |
| Q4: Role of habits? | Layer 3 (Driver: HABIT_LOOP) → Layer 4 → Layer 5 | Habit impact analysis |
| Q5: Information needs? | Layer 3 (Driver: INFORMATION_GAP) → Layer 5 | Content gap insights |
| Q6: Recurring frustrations? | Layer 3 (Sentiment: negative) → Layer 4 | Pain point themes |
| Q7: Experimental segments? | Layer 5 (Segment Profiling) | User segment profiles |
| Q8: Unmet needs? | Layer 4 (All themes) → Layer 5 (Cross-theme) | Opportunity insights |
