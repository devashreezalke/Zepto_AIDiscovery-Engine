# Edge Cases & Corner Scenarios: Zepto AI Discovery Engine

> **Purpose:** Comprehensive catalog of every edge case, corner scenario, and failure mode across all 7 architecture layers and 6 implementation phases. Each entry includes the scenario, its impact, and the recommended handling strategy.

---

## Table of Contents

1. [Layer 1 — Data Ingestion Edge Cases](#1-layer-1--data-ingestion-edge-cases)
2. [Layer 2 — Processing & Normalization Edge Cases](#2-layer-2--processing--normalization-edge-cases)
3. [Layer 3 — AI Analysis Edge Cases](#3-layer-3--ai-analysis-edge-cases)
4. [Layer 4 — Clustering Edge Cases](#4-layer-4--clustering-edge-cases)
5. [Layer 5 — Insight Generation Edge Cases](#5-layer-5--insight-generation-edge-cases)
6. [Layer 6 — Validation Edge Cases](#6-layer-6--validation-edge-cases)
7. [Layer 7 — Dashboard & Presentation Edge Cases](#7-layer-7--dashboard--presentation-edge-cases)
8. [Infrastructure & Deployment Edge Cases](#8-infrastructure--deployment-edge-cases)
9. [Groq API-Specific Edge Cases](#9-groq-api-specific-edge-cases)
10. [Data Quality & Integrity Edge Cases](#10-data-quality--integrity-edge-cases)
11. [Business Logic Edge Cases](#11-business-logic-edge-cases)

---

## 1. Layer 1 — Data Ingestion Edge Cases

### 1.1 Source Availability

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 1.1.1 | **Play Store scraper gets rate-limited or blocked** (HTTP 429 / CAPTCHA) | No new Play Store data flows in | Implement exponential backoff (2s → 4s → 8s → 16s). Rotate user-agent strings. If blocked for >24h, switch to RSS feed fallback. Pipeline continues with other sources. |
| 1.1.2 | **Reddit API returns 403 Forbidden** (OAuth token expired or revoked) | Reddit data stops flowing | Auto-refresh OAuth token on 401/403. If refresh fails, log error and alert. Pipeline continues without Reddit. Retry authentication every 30 min. |
| 1.1.3 | **snscrape stops working** (Twitter/X changes HTML structure) | Twitter/X source goes dark | snscrape is community-maintained and may break. Fallback: skip Twitter source, log warning. Post-MVP: add Nitter as alternative scraper. |
| 1.1.4 | **Forum website goes offline or restructures HTML** | Forum data stops | BeautifulSoup selectors break. Detect via HTTP error or empty response. Log warning, skip source. Each source is independent — others continue. |
| 1.1.5 | **All 4 sources fail simultaneously** | Zero new data | Alert immediately. Pipeline exits gracefully with message "No sources available." Dashboard shows stale data with "Last updated: X hours ago" warning. |
| 1.1.6 | **Source returns valid HTML but zero reviews** (new app, empty subreddit) | Empty dataset for that source | Check `len(results) == 0` after scraping. Log as warning, not error. Don't insert empty rows. |

### 1.2 Data Volume Extremes

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 1.2.1 | **Source returns 10,000+ reviews in one fetch** (viral app update) | Memory spike, slow processing | Set max per-fetch limit: `count=500` per scraper call. If more available, paginate across multiple fetches with `time.sleep(1)` between pages. |
| 1.2.2 | **Total corpus < 50 documents after scraping all sources** | Insufficient data for meaningful clustering | Warn user: "Minimum 100 documents recommended for clustering." Expand search terms, add more subreddits/apps. Proceed with analysis but skip clustering (set all themes to "Insufficient Data"). |
| 1.2.3 | **Single source dominates** (e.g., 450 Play Store reviews, 10 from Reddit, 5 from Twitter) | Source bias in themes and insights | Calculate source distribution. If any source > 80% of total, add warning badge on dashboard: "⚠️ Results may be biased toward Play Store data." Normalize theme scores by source diversity. |
| 1.2.4 | **Duplicate deluge** — same review copy-pasted across platforms | Inflated counts, fake signal | Exact dedup (SHA-256) catches identical copies. Near-dedup (MinHash, Jaccard > 0.85) catches slight variations. If >50% flagged as duplicate, log warning. |

### 1.3 Content Anomalies

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 1.3.1 | **Review is just emojis** (e.g., "👍👍👍👍👍") | No textual content for LLM to analyze | Check `word_count < 3` after stripping emojis. Skip analysis. Optionally store emoji-only reviews as sentiment signal (5 thumbs-up → positive). |
| 1.3.2 | **Review is in a non-supported language** (Tamil, Marathi, Bengali) | LLM may produce garbage analysis | Language detection via `langdetect`. If not English/Hindi/Hinglish, skip document. Log language distribution for visibility. |
| 1.3.3 | **Review contains only a URL or promotional link** | Spam / no useful content | Regex detect: if >50% of content is URLs, flag as spam. Skip analysis. |
| 1.3.4 | **Review is extremely long** (>2000 words — blog-length Reddit post) | May exceed Groq token limit, slow processing | Truncate to first 1000 words for analysis. Store full text in DB. Add `truncated=True` flag. |
| 1.3.5 | **Review contains code snippets, HTML tags, or markdown** | Pollutes analysis text | Strip HTML tags, code blocks, and markdown formatting before analysis. Use `BeautifulSoup(text, 'html.parser').get_text()`. |

---

## 2. Layer 2 — Processing & Normalization Edge Cases

### 2.1 Deduplication

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 2.1.1 | **Near-duplicate with opposite sentiment** (e.g., "Zepto is great for groceries" vs "Zepto is terrible for groceries") | MinHash may flag as duplicate despite opposite meaning | After MinHash flags near-duplicate, compare sentiment scores. If sentiment differs by > 0.5, keep both documents. Mark as "semantically distinct near-duplicate." |
| 2.1.2 | **Same user posts same complaint across Reddit + Play Store** | Legitimate cross-platform signal, but inflates count | Keep both but link them via `cross_source_duplicate=True`. Count as 1 unique voice but note multi-platform presence (strengthens the signal). |
| 2.1.3 | **Template/bot reviews** (same structure, different product names) | Many near-duplicates from bots | Detect via template patterns (e.g., "I love [PRODUCT], 5 stars"). If >10 reviews match a template, flag entire batch as bot-generated. |

### 2.2 PII Redaction

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 2.2.1 | **PII embedded in natural text** ("my friend Rajesh told me...") | Named entity not caught by regex | Use spaCy NER (`en_core_web_sm`) to detect PERSON entities. Replace with `[NAME_REDACTED]`. Accept that some names will be missed — redaction is best-effort. |
| 2.2.2 | **Phone number in non-standard format** ("+91-98765 43210", "call me at nine eight...") | Regex misses non-standard formats | Extend regex to cover: `+91`, spaces, dashes, dots between digits. Written-out numbers are impractical to catch — accept this gap. |
| 2.2.3 | **PII is the critical context** (e.g., "I ordered for my baby Arjun") | Redacting removes context about "baby" → Baby Care category signal | Redact the name but preserve the noun context: "[NAME_REDACTED]" preserves surrounding words. Category detection still works on "ordered for my baby [NAME_REDACTED]." |
| 2.2.4 | **Email or phone appears in the middle of a product complaint** | Important feedback lost if entire review is discarded | Never discard the review — only replace the PII token. The rest of the text remains fully intact for analysis. |

### 2.3 Schema Normalization

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 2.3.1 | **Missing timestamp on scraped document** | Can't determine temporal trends | Set `source_timestamp = scraped_at` (current time). Flag as `timestamp_imputed=True`. Exclude from temporal trend analysis. |
| 2.3.2 | **Rating field has unexpected value** (e.g., 6/5, -1, null) | Corrupts sentiment baseline | Clamp to valid range: `rating = max(1, min(5, rating))`. If null, set to `None` and exclude from rating-based analysis. |
| 2.3.3 | **Content field is empty after cleaning** (was all URLs or emojis) | Empty string in DB | Check `len(content_clean.strip()) == 0` after cleaning. Mark as `is_empty=True`, skip all downstream processing. |
| 2.3.4 | **Unicode encoding issues** (mojibake, mixed encodings) | Garbled text fed to LLM | Force UTF-8 encoding: `content.encode('utf-8', errors='replace').decode('utf-8')`. Log any documents with encoding errors. |

---

## 3. Layer 3 — AI Analysis Edge Cases

### 3.1 Groq LLM Response Issues

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 3.1.1 | **Groq returns invalid JSON** (malformed, truncated, or wrapped in markdown) | JSON parse fails, document goes un-analyzed | Retry up to 3 times with stricter prompt ("Return ONLY valid JSON, no markdown, no explanation"). If still fails, strip markdown code fences and re-parse. If still fails, log error and skip document. |
| 3.1.2 | **Groq returns valid JSON but with wrong schema** (missing fields, extra fields) | Downstream code crashes on missing key | Validate response against expected schema. Fill missing fields with defaults: `sentiment="neutral"`, `sentiment_score=0.0`, `emotions=[]`, `drivers=[]`. Log as "partial analysis." |
| 3.1.3 | **Groq hallucinates a category not in the taxonomy** (e.g., "Automotive Parts") | Invalid category pollutes downstream analysis | Validate `categories_mentioned` against the hardcoded taxonomy list. Drop any category not in the list. Log hallucinated categories for prompt improvement. |
| 3.1.4 | **Groq returns the same analysis for every document** (stuck/degenerate response) | All documents get identical sentiment/drivers | Detect: if >20 consecutive documents have identical `sentiment_score` and `drivers`, flag as degenerate. Pause, wait 60s, retry batch with different prompt phrasing. |
| 3.1.5 | **Groq returns analysis in wrong language** (Hindi response for English prompt) | Cannot parse or use the response | Add `"RESPOND IN ENGLISH ONLY"` to system prompt. If response contains non-ASCII characters (excluding common symbols), retry with explicit language instruction. |
| 3.1.6 | **LLM refuses to analyze** ("I cannot analyze user reviews" / safety filter) | No analysis for that document | Detect refusal patterns in response text ("I cannot", "I'm sorry", "As an AI"). Skip document, log as "LLM_REFUSED". Rephrase prompt to avoid safety triggers. |

### 3.2 Sentiment Analysis Edge Cases

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 3.2.1 | **Sarcastic review** ("Wow, amazing delivery — 3 hours for instant delivery 🙄") | LLM may classify as positive (misses sarcasm) | Accept as a known limitation. Sarcasm detection is imperfect even for humans. The validation layer (Gate 5: self-consistency) may catch some cases. Flag reviews with positive text + low rating (1-2 stars) as "potential sarcasm." |
| 3.2.2 | **Mixed sentiment in one review** ("Love the groceries section but personal care is terrible") | Single sentiment label doesn't capture nuance | Use `"mixed"` sentiment label. The `behavioral_drivers` array captures both positive and negative signals separately. Category-level sentiment is derived from drivers, not the global sentiment. |
| 3.2.3 | **Neutral/factual review** ("Ordered 3 items, delivered in 12 minutes") | Classified as neutral but may contain implicit satisfaction | Accept neutral classification. If rating is 4-5 stars, the neutral text + high rating signals satisfaction. Don't force sentiment where there is none. |
| 3.2.4 | **Review about competitor, not Zepto** ("Blinkit is better than Zepto for baby products") | Sentiment about competitor, not Zepto | LLM should extract: `categories_desired=["Baby Care"]`, `driver="VALUE_PERCEPTION.price_higher_than_alternatives"`. The comparative mention is still useful — it reveals why users don't buy Baby Care on Zepto. |

### 3.3 Category Detection Edge Cases

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 3.3.1 | **Ambiguous category mention** ("I need some stuff for the house") | Could be Household Essentials, Home & Kitchen, or Groceries | LLM should return the most likely category with confidence < 0.5. If ambiguous, tag multiple categories: `categories_mentioned=["Household Essentials", "Home & Kitchen"]`. |
| 3.3.2 | **No category mentioned** ("The app is slow and crashes often") | This is a platform complaint, not category-specific | Set `categories_mentioned=[]`. Tag with driver `PLATFORM_LIMITATION.app_performance_issues`. This still answers Q6 (pain points) and Q8 (unmet needs). |
| 3.3.3 | **Category mentioned doesn't exist on Zepto** ("Can I order alcohol from Zepto?") | Invalid category but reveals unmet demand | Tag as `categories_desired=["Alcohol"]` even though it's not in the taxonomy. Create a special `"Unmet Category Demand"` bucket for these. Valuable for Q8 (unmet needs). |
| 3.3.4 | **Product mentioned but not the category** ("I want Dove shampoo") | Need to map product → category | LLM should infer: Dove shampoo → Personal Care → Hair Care. If LLM fails, add a product-to-category lookup table for common brands. |

### 3.4 Behavioral Driver Edge Cases

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 3.4.1 | **No behavioral driver detected** ("Good app, I like it") | Generic positive review, no actionable driver | Set `behavioral_drivers=[]`. This is valid — not every review contains a behavioral signal. Skip for theme clustering (noise). |
| 3.4.2 | **Multiple conflicting drivers** ("I trust Zepto for groceries but don't trust them for electronics") | Two opposite trust signals in one review | Both drivers are valid. Tag both: `TRUST_BARRIER` for electronics and implicit trust for groceries. Each will cluster into different themes. |
| 3.4.3 | **Driver doesn't fit any taxonomy category** ("The delivery person was rude") | Delivery experience complaint — not a category exploration barrier | Map to `PLATFORM_LIMITATION.delivery_experience`. While not directly about category exploration, it affects overall platform trust which indirectly impacts willingness to try new categories. |
| 3.4.4 | **Review mentions a driver but for a competitor** ("Blinkit has better recommendations") | Driver is about competitor's feature, not Zepto's lack | Still useful — implies `DISCOVERY_FRICTION.no_personalized_recommendations` for Zepto. Tag as discovery friction with evidence noting the comparison. |

---

## 4. Layer 4 — Clustering Edge Cases

### 4.1 Cluster Formation

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 4.1.1 | **HDBSCAN produces 0 clusters** (all points classified as noise) | No themes generated | `min_cluster_size` is too high. Reduce from 8 → 5 → 3. If still 0 clusters at `min_cluster_size=3`, the data may be too sparse or homogeneous. Fall back to keyword-based topic modeling (TF-IDF + manual grouping). |
| 4.1.2 | **HDBSCAN produces 100+ clusters** (too fragmented) | Themes are too granular to be useful | Increase `min_cluster_size` from 8 → 15 → 25. Alternatively, merge clusters with centroid cosine similarity > 0.8. |
| 4.1.3 | **One mega-cluster contains 80% of documents** | Most documents grouped into one vague theme | The embedding space may not differentiate well. Solutions: (1) embed `content + driver + category` instead of just `content + driver`, (2) increase UMAP `n_neighbors`, (3) manually split the mega-cluster using driver sub-types. |
| 4.1.4 | **>50% of documents are noise** (cluster_id = -1) | Half the data is unused for theming | Reduce `min_samples` from 3 → 2. Reduce `min_cluster_size`. Alternatively, assign noise points to the nearest cluster via cosine similarity (soft assignment). |
| 4.1.5 | **Two themes are nearly identical** (e.g., "Trust issues with Personal Care" and "Quality concerns for Personal Care") | Redundant themes confuse PM | Post-clustering merge: compute centroid similarity. If > 0.85, merge into one theme. LLM re-labels the merged cluster. |

### 4.2 Embedding Issues

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 4.2.1 | **Very short documents embed poorly** (<10 words → noisy embeddings) | Short reviews cluster randomly | Filter: only embed documents with `word_count >= 10`. Shorter docs contribute to aggregate stats but not to clustering. |
| 4.2.2 | **Multilingual text produces inconsistent embeddings** | Hindi/Hinglish reviews cluster away from English reviews on the same topic | `all-MiniLM-L6-v2` has limited multilingual support. For Hindi-heavy corpus, consider switching to `paraphrase-multilingual-MiniLM-L12-v2`. Or translate to English before embedding. |
| 4.2.3 | **Embedding model runs out of memory** (corpus too large for RAM) | Process crashes | Batch embedding: process 100 documents at a time, concatenate NumPy arrays. Peak memory = batch_size × 384 × 4 bytes = negligible. This should not occur at 500-doc scale. |

### 4.3 Theme Labeling

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 4.3.1 | **LLM generates a vague theme title** ("Users have concerns") | Theme is not actionable | Add constraint to prompt: "Title MUST mention a specific category or behavior. Bad: 'Users have concerns.' Good: 'Trust Deficit Blocks Personal Care Adoption.'" Retry if title has no specificity. |
| 4.3.2 | **LLM generates a theme label that contradicts the documents** | Hallucinated theme | Validation: check if LLM's `key_drivers` match the majority of drivers in the cluster documents. If <50% overlap, re-label with a different sample of documents. |
| 4.3.3 | **Sampled documents for labeling are all outliers** | Theme label reflects edge cases, not the cluster center | Sample documents by proximity to cluster centroid, not randomly. Pick the 15 documents closest to the centroid for labeling. |

---

## 5. Layer 5 — Insight Generation Edge Cases

### 5.1 Insight Synthesis

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 5.1.1 | **Theme has high doc count but all docs say the same thing** (e.g., 100 reviews all saying "app crashes") | Insight is valid but one-dimensional | Still generate insight, but note `evidence_diversity="low"`. The root cause and hypothesis should be straightforward. Flag as "single-issue insight." |
| 5.1.2 | **LLM generates a hypothesis that's already a Zepto feature** ("If we add 10-minute delivery...") | Irrelevant hypothesis — feature already exists | Add context to prompt: "Zepto already offers: 10-minute delivery, wide grocery selection, COD payment. Do NOT suggest features that already exist." |
| 5.1.3 | **No themes qualify for insight generation** (all themes have doc_count < 10) | Zero insights produced | Lower the threshold from 10 → 5 documents. If still no qualifying themes, generate "exploratory insights" with a disclaimer: "Low evidence — treat as hypothesis, not finding." |
| 5.1.4 | **Cross-theme synthesis finds no compound barriers** | Cross-theme analysis returns empty | Not every category will have compound barriers. Log as "no compound effects detected." This is a valid finding — some barriers are isolated. |
| 5.1.5 | **LLM generates identical insights for different themes** | Redundant insights in the output | Deduplicate insights by title similarity (Jaccard > 0.7 on title words). Merge duplicates, combine supporting themes. |

### 5.2 Segment Profiling

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 5.2.1 | **LLM can't distinguish 5 segments from the data** | Segments feel forced or overlapping | Accept 3-4 segments instead of forcing 5. Prompt: "Generate between 3 and 5 segments. Only create segments with clear behavioral distinctions." |
| 5.2.2 | **Segment estimated sizes don't add up to 100%** | PM questions the math | Segments can overlap (a user can be both a "Value Seeker" and a "Curious Browser"). Add footnote: "Segments may overlap; percentages indicate primary behavioral archetype." |
| 5.2.3 | **LLM hallucinates a segment not supported by data** ("Tech Enthusiasts") | Segment has no backing evidence | Validate: for each segment, check if at least 1 theme's representative quotes match the segment description. If no evidence, drop the segment. |

### 5.3 Hypothesis Quality

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 5.3.1 | **Hypothesis is too vague** ("If we improve the app, more users will try new categories") | Not testable, not actionable | Prompt constraint: "Each hypothesis MUST include: (1) a specific product change, (2) a specific metric to measure, (3) an expected % improvement range." Retry if hypothesis lacks specificity. |
| 5.3.2 | **Hypothesis requires data Zepto doesn't have** ("If we target users who shop at D-Mart offline...") | Infeasible experiment | Add prompt context: "Hypotheses must be testable using only Zepto's in-app data: purchase history, browse behavior, cart data, order frequency. No offline or third-party data." |
| 5.3.3 | **All hypotheses are the same type** (e.g., all suggest discounts) | Lack of creative solutions | Prompt: "Generate diverse hypotheses spanning: (a) UX/navigation changes, (b) social proof/reviews, (c) pricing/bundling, (d) personalization/recommendations. At least 2 of the 4 types must be represented." |

---

## 6. Layer 6 — Validation Edge Cases

### 6.1 Confidence Scoring

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 6.1.1 | **All insights score LOW confidence** | Nothing passes validation, dashboard is empty | Review the thresholds. If the dataset is small (< 200 docs), lower thresholds: HIGH ≥ 0.65, MEDIUM ≥ 0.45. Add a "Limited Data" disclaimer on dashboard. |
| 6.1.2 | **All insights score HIGH confidence** | No differentiation, PM can't prioritize | The scoring weights may be too lenient. Increase the weight on `source_diversity` (require ≥ 3 platforms for HIGH). Or tighten the HIGH threshold to ≥ 0.85. |
| 6.1.3 | **Confidence score is exactly 0.60 or 0.80** (boundary) | Ambiguous classification | Use strict boundaries: `>=0.80` is HIGH, `>=0.60` is MEDIUM, else LOW. Document this clearly. 0.60 is MEDIUM, 0.80 is HIGH. |
| 6.1.4 | **LLM self-consistency check can't run** (Groq quota exhausted) | Gate 5 returns no score | Skip Gate 5. Calculate confidence without the LLM agreement component. Redistribute its weight (0.20) equally across other 4 components. Flag as "partial validation." |

### 6.2 Validation Gate Failures

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 6.2.1 | **Insight passes 4/5 gates but fails source grounding** (all evidence from one platform) | Valid insight but single-source bias | Allow it as MEDIUM confidence with a warning badge: "⚠️ Single-source evidence. Validate with additional data." |
| 6.2.2 | **Theme has 50 documents but all from the same week** | Fails temporal stability (could be a viral event) | Check if there's a known event (app outage, viral tweet). If yes, tag as "Event-Driven Theme" — still valid but not persistent. If no event, flag as "potential anomaly." |
| 6.2.3 | **Sentiment consistency check fails** (high std. dev. within theme) | Theme may contain mixed sub-topics | The cluster might need splitting. Run sub-clustering on this theme with lower `min_cluster_size`. If sub-clusters emerge, split the theme. If not, accept the variability and note it. |

---

## 7. Layer 7 — Dashboard & Presentation Edge Cases

### 7.1 Data Display

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 7.1.1 | **Zero insights to display** (pipeline hasn't run or all failed) | Empty dashboard, PM sees nothing | Show a clear empty state: "No insights generated yet. Run the pipeline to get started." with a prominent "Run Pipeline" button. Never show a blank page. |
| 7.1.2 | **Insight title or finding is extremely long** (200+ characters) | Text overflows card boundaries | CSS: `text-overflow: ellipsis; overflow: hidden; max-height: 60px;`. Show full text on hover/click expand. |
| 7.1.3 | **Representative quote contains special characters** (`<script>`, `"`, `'`, `&`) | XSS vulnerability or broken rendering | Sanitize all user-generated content before rendering. Use React's built-in JSX escaping. Never use `dangerouslySetInnerHTML` on user content. |
| 7.1.4 | **Charts have only 1 data point** (e.g., only 1 source) | Pie chart / bar chart looks broken | Handle gracefully: if only 1 source, show a stat card instead of a pie chart. If only 1 theme, show a detail view instead of a grid. |
| 7.1.5 | **Sentiment score is exactly 0.0 for all documents** | Sentiment bar shows no variation | Check if analysis actually ran. If all scores are 0.0, this likely means the analysis pipeline failed silently. Show warning: "Sentiment analysis may not have run correctly." |

### 7.2 Interaction & Navigation

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 7.2.1 | **User navigates to a theme that no longer exists** (data refreshed, theme ID changed) | 404 or crash | Handle missing theme ID gracefully: redirect to Theme Explorer with message "This theme is no longer available. Themes are regenerated with each pipeline run." |
| 7.2.2 | **Dashboard loads before pipeline has finished** | Partial or stale data displayed | Check `data/insights_export.json` modification timestamp. If older than current pipeline run, show "Pipeline in progress..." loading state. |
| 7.2.3 | **Multiple users open dashboard simultaneously** | No issue (static JSON, no shared state) | Since the dashboard reads from a static JSON export, concurrent access is not a problem. Vercel handles this natively via CDN. |
| 7.2.4 | **Browser back button breaks navigation** | User gets stuck or lost | Use Next.js `useRouter` with proper URL-based routing. Each view has its own URL (`/themes`, `/research`, etc.). Back button works naturally. |

### 7.3 Responsive Design

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 7.3.1 | **Dashboard opened on mobile** (< 768px width) | Sidebar overlaps content, cards are unreadable | Responsive breakpoints: sidebar collapses to hamburger menu at 768px. Cards switch to single-column layout. Stat numbers resize to 24px. |
| 7.3.2 | **Very wide screen** (> 2560px, ultrawide monitor) | Content stretches, looks sparse | Set `max-width: 1440px; margin: 0 auto;` on main content container. Cards maintain their grid layout without stretching. |
| 7.3.3 | **Dark mode requested by user** | Dashboard only has light theme | MVP: light theme only (matches Zepto's white aesthetic). Post-MVP: add dark mode toggle with inverted color tokens. |

---

## 8. Infrastructure & Deployment Edge Cases

### 8.1 Railway

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 8.1.1 | **Railway free credit ($5) exhausted mid-month** | Backend goes offline | Monitor credit usage via Railway dashboard. Set up email alert at 80% usage. If exhausted: pipeline stops, dashboard shows last cached data. Upgrade to $5/month Hobby plan or switch to Render free tier. |
| 8.1.2 | **Railway deployment fails** (build error, missing dependency) | Backend not updated | Check Railway build logs. Common issues: missing dependency in `requirements.txt`, Python version mismatch. Fix locally, push again. Railway auto-retries on new push. |
| 8.1.3 | **SQLite database corrupted on Railway** (disk issue, concurrent writes) | Data loss | SQLite is not designed for concurrent writes. Ensure only one worker writes at a time (use file locking). Take periodic backups via Railway CLI: `railway run sqlite3 data/discovery.db ".backup backup.db"`. |
| 8.1.4 | **Railway persistent volume reaches disk limit** | No new data can be written | Monitor disk usage. Set up cleanup: delete raw documents older than 6 months. Compress old data. Or upgrade to larger volume. |

### 8.2 Vercel

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 8.2.1 | **Vercel build fails** (TypeScript errors, import issues) | Dashboard not updated | Check Vercel build logs. Fix locally with `npm run build`, then push. Vercel keeps the last working deployment live until the new one succeeds. |
| 8.2.2 | **API URL environment variable not set in Vercel** | Dashboard can't fetch data from Railway | Dashboard falls back to local JSON file if API is unreachable. Add `NEXT_PUBLIC_API_URL` in Vercel project settings → Environment Variables. |
| 8.2.3 | **Vercel function timeout** (if using API routes for data fetching) | API route returns 504 | Vercel free tier has 10-second function timeout. Avoid server-side API calls that proxy to Railway. Fetch directly from Railway API in the browser. |
| 8.2.4 | **CORS error when dashboard (Vercel) calls API (Railway)** | Browser blocks API requests | Add CORS middleware to FastAPI: `app.add_middleware(CORSMiddleware, allow_origins=["https://zepto-discovery.vercel.app"], ...)`. |

---

## 9. Groq API-Specific Edge Cases

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 9.1 | **Groq API is completely down** (503 Service Unavailable) | All LLM-dependent tasks halt | Retry 3 times with 30s interval. If still down, queue unprocessed documents for later. Use VADER sentiment as fallback for basic analysis. Alert user. |
| 9.2 | **Daily request quota exhausted** (free tier limit hit) | No more LLM calls for the day | Celery rate limiter should prevent this. If it happens: queue remaining documents for tomorrow. Log exactly how many documents remain. Dashboard shows "Analysis pending for X documents." |
| 9.3 | **Rate limit hit (429 Too Many Requests)** | Individual request fails | Exponential backoff: wait 2s → 4s → 8s → 16s. Max 4 retries per request. Reduce concurrent rate to 15 req/min if hitting limits frequently. |
| 9.4 | **Model becomes unavailable** (`llama-3.3-70b-versatile` removed from free tier) | Primary model no longer accessible | Fall back to `llama-3.1-8b-instant` or `mixtral-8x7b-32768`. Check Groq model list at startup: `client.models.list()`. Auto-select best available model. |
| 9.5 | **Groq response latency spikes** (>30s per request) | Pipeline takes hours instead of minutes | Set timeout at 30s per request. If >3 consecutive timeouts, pause for 5 minutes, then resume. Switch to smaller model (`llama-3.1-8b-instant`) for remaining documents. |
| 9.6 | **Groq changes free-tier limits** (reduces from 30 req/min to 10) | Pipeline is 3x slower | Update rate limiter dynamically. Fetch current limits from Groq response headers (`x-ratelimit-limit-requests`). Adapt `time.sleep()` accordingly. |
| 9.7 | **Groq returns empty response** (200 OK but no content) | No analysis for that document | Treat as a transient error. Retry up to 3 times. If still empty, skip document and log as "EMPTY_RESPONSE." |

---

## 10. Data Quality & Integrity Edge Cases

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 10.1 | **Pipeline crashes mid-run** (power failure, OOM, network drop) | Partially processed corpus | Implement checkpoint/resume: after each major step (scraping, analysis, clustering), save progress to a `pipeline_state.json` file. On restart, resume from last completed step. |
| 10.2 | **Pipeline run twice without clearing DB** | Duplicate documents, double-counted themes | Before scraping, check for existing documents by `source_url` or content hash. Skip already-ingested documents (upsert pattern). For themes/insights, clear and regenerate on each run. |
| 10.3 | **System clock is wrong** | Timestamps are off, temporal analysis is invalid | Use UTC for all internal timestamps. Validate system clock against an NTP server at pipeline start. Warn if clock skew > 5 minutes. |
| 10.4 | **JSON export file is corrupted** (incomplete write, disk full) | Dashboard shows broken/empty data | Write to a temp file first, then atomic rename: `os.replace('temp_export.json', 'insights_export.json')`. This ensures the file is always complete. |
| 10.5 | **Database file exceeds 1 GB** (after many pipeline runs) | Performance degradation, disk quota on Railway | Implement data rotation: keep only the last 3 pipeline runs. Archive older data. Run `VACUUM` on SQLite after deleting old rows. |

---

## 11. Business Logic Edge Cases

| # | Scenario | Impact | Handling |
|---|---|---|---|
| 11.1 | **All themes are about the same category** (e.g., every theme is about Groceries) | No cross-category discovery insights | This means users primarily discuss groceries. Valid finding: "Users view Zepto as a grocery-only platform." Generate insight about platform perception as a category expansion barrier. |
| 11.2 | **No category-switching signals detected in any document** | Core problem statement has no evidence in the data | Expand search terms to explicitly look for category-related content ("wish zepto had", "why doesn't zepto sell", "started buying X from zepto"). If still no signals, this is itself an insight: "Users don't think about category exploration at all." |
| 11.3 | **All insights point to price as the only barrier** | Monotonic finding, limited actionability | Add prompt diversity: "Beyond pricing, what behavioral, trust, or information barriers exist?" If pricing genuinely is the only barrier, generate sub-insights about price elasticity across different categories. |
| 11.4 | **Positive insights emerge** ("Users love trying new categories during festivals") | Unexpected positive signal — not a problem to solve | Don't filter out positive signals. These are equally valuable — they reveal when and why category expansion works. Tag as `CONTEXTUAL_TRIGGER.seasonal_or_event_based_need`. Use as positive case study for growth experiments. |
| 11.5 | **Insights contradict each other** ("Users want more choice" vs "Users feel overwhelmed by options") | PM is confused about which is true | Both can be true for different segments. Cross-reference with user segments. "Curious Browsers" want more choice; "Habitual Minimalists" feel overwhelmed. Present both insights with segment labels. |
| 11.6 | **Research question has zero supporting themes** | One of the 8 Qs is unanswered | Not all questions will have equal evidence. Show on dashboard: "Q7 (User Segments): ⚠️ Insufficient data — 0 supporting themes. Consider adding more targeted data sources." Don't fabricate evidence. |
| 11.7 | **New category launches on Zepto after pipeline runs** | Taxonomy is outdated | Make the category taxonomy a configuration file (`config/categories.json`), not hardcoded. Update the file when Zepto adds new categories. Re-run analysis pipeline with updated taxonomy. |

---

## Quick Reference: Edge Case Count by Layer

| Layer | Category | Edge Cases |
|---|---|---|
| Layer 1 — Ingestion | Source availability, volume, content | 15 |
| Layer 2 — Processing | Dedup, PII, normalization | 11 |
| Layer 3 — AI Analysis | LLM response, sentiment, category, drivers | 18 |
| Layer 4 — Clustering | Formation, embeddings, labeling | 10 |
| Layer 5 — Insights | Synthesis, segments, hypotheses | 11 |
| Layer 6 — Validation | Scoring, gate failures | 6 |
| Layer 7 — Dashboard | Display, navigation, responsive | 10 |
| Infrastructure | Railway, Vercel | 8 |
| Groq API | Rate limits, downtime, model changes | 7 |
| Data Quality | Pipeline crashes, corruption | 5 |
| Business Logic | Domain-specific scenarios | 7 |
| **Total** | | **108 edge cases** |
