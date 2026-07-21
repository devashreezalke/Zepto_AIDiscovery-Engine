-- Schema for Zepto AI Discovery Engine SQLite Database

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,                  -- play_store, reddit, twitter, forum
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
    sentiment TEXT,                        -- positive, negative, neutral, mixed
    sentiment_score REAL,
    emotions TEXT,                         -- JSON array
    categories_mentioned TEXT,             -- JSON array
    categories_desired TEXT,               -- JSON array
    category_switch_signal BOOLEAN,
    behavioral_drivers TEXT,              -- JSON array [{driver, confidence, evidence}]
    research_questions TEXT,               -- JSON array of Q1-Q8 tags
    analyzed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS themes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    macro_theme TEXT,
    drivers TEXT,                          -- JSON array
    blocked_categories TEXT,               -- JSON array
    research_questions TEXT,               -- JSON array
    doc_count INTEGER,
    avg_sentiment REAL,
    representative_quotes TEXT,           -- JSON array
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
    impact TEXT,                           -- JSON
    target_segment TEXT,                  -- JSON
    hypotheses TEXT,                      -- JSON array
    supporting_themes TEXT,               -- JSON array of theme IDs
    confidence_score REAL,
    confidence_level TEXT,                -- HIGH, MEDIUM, LOW
    research_questions TEXT,              -- JSON array
    created_at TEXT DEFAULT (datetime('now'))
);
