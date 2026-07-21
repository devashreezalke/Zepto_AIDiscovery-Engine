import re
import sqlite3
import logging
from dotenv import load_dotenv
from scrapers.playstore import scrape_playstore
from scrapers.reddit import scrape_reddit
from scrapers.twitter import scrape_twitter
from scrapers.forums import scrape_forums

logger = logging.getLogger(__name__)
load_dotenv()

# Simple regexes for PII Redaction
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')

def clean_and_redact(text):
    """Cleans text of raw spacing issues and redacts emails and phone numbers."""
    if not text:
        return ""
    
    # 1. Basic cleaning: collapse whitespace
    cleaned = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Redact PII
    cleaned = EMAIL_REGEX.sub("[EMAIL_REDACTED]", cleaned)
    cleaned = PHONE_REGEX.sub("[PHONE_REDACTED]", cleaned)
    
    return cleaned

def is_valid_document(doc):
    """Filters out noise: empty, extremely short, or trash reviews."""
    content = doc.get('content', '')
    if not content:
        return False
    if len(content.strip()) < 15:
        return False
    return True

def run_ingestion(db_path='data/discovery.db'):
    """Runs all scrapers, processes, deduplicates and saves documents to the SQLite database."""
    logger.info("Starting data ingestion pipeline...")
    
    # 0. Ensure database tables exist
    from data.db_init import init_db
    init_db(db_path)
    
    # 1. Fetch data from all sources
    all_docs = []
    
    # Play Store (Zepto + Blinkit + Instamart)
    all_docs.extend(scrape_playstore('com.zeptoconsumerapp', count=200))
    all_docs.extend(scrape_playstore('com.grofers.customerapp', count=150))
    all_docs.extend(scrape_playstore('in.swiggy.android', count=150))
    
    # Reddit discussions
    all_docs.extend(scrape_reddit(limit=100))
    
    # Twitter discussions
    all_docs.extend(scrape_twitter(limit=100))
    
    # Forums
    all_docs.extend(scrape_forums())
    
    logger.info(f"Total raw documents fetched: {len(all_docs)}")
    
    # 2. Open DB connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get existing document hashes or contents to avoid inserting exact duplicates
    cursor.execute("SELECT content FROM documents")
    existing_contents = {row[0] for row in cursor.fetchall()}
    
    inserted_count = 0
    duplicate_count = 0
    skipped_count = 0
    
    for doc in all_docs:
        if not is_valid_document(doc):
            skipped_count += 1
            continue
            
        content = doc['content']
        cleaned_content = clean_and_redact(content)
        
        # Check duplicate
        is_duplicate = 0
        if content in existing_contents:
            is_duplicate = 1
            duplicate_count += 1
        else:
            existing_contents.add(content)
            
        doc['content_clean'] = cleaned_content
        doc['is_duplicate'] = is_duplicate
        
        # Insert to DB
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO documents (
                    id, source, content, content_clean, source_url, 
                    author_hash, rating, upvotes, source_timestamp, is_duplicate, word_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc['id'],
                doc['source'],
                doc['content'],
                doc['content_clean'],
                doc['source_url'],
                doc['author_hash'],
                doc['rating'],
                doc['upvotes'],
                doc['source_timestamp'],
                doc['is_duplicate'],
                doc['word_count']
            ))
            inserted_count += 1
        except Exception as e:
            logger.error(f"Error inserting document {doc['id']}: {e}")
            
    conn.commit()
    conn.close()
    
    logger.info("Ingestion summary:")
    logger.info(f"  - Clean documents inserted: {inserted_count} (including duplicates)")
    logger.info(f"  - Exact duplicates flagged: {duplicate_count}")
    logger.info(f"  - Skipped (too short/noisy): {skipped_count}")
    
    return inserted_count

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_ingestion()
