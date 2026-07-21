import uuid
import hashlib
import logging
from google_play_scraper import reviews, Sort

logger = logging.getLogger(__name__)

def scrape_playstore(app_id, count=200):
    """Scrapes reviews for a given package ID from Google Play Store."""
    logger.info(f"Scraping {count} reviews for package: {app_id}")
    try:
        results, _ = reviews(
            app_id,
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=count
        )
        
        documents = []
        for r in results:
            content = r.get('content', '')
            if not content:
                continue
                
            # Create a unique ID based on a hash of the content and date to prevent dupes later
            author_name = r.get('userName', '')
            author_hash = hashlib.sha256(author_name.encode('utf-8', errors='ignore')).hexdigest() if author_name else None
            
            # Format timestamp to ISO format string
            timestamp = r.get('at')
            timestamp_str = timestamp.isoformat() if timestamp else None
            
            doc_id = str(uuid.uuid4())
            documents.append({
                'id': doc_id,
                'source': 'play_store',
                'content': content,
                'content_clean': None,
                'source_url': f"https://play.google.com/store/apps/details?id={app_id}",
                'author_hash': author_hash,
                'rating': float(r.get('score', 0)),
                'upvotes': int(r.get('thumbsUpCount', 0)),
                'source_timestamp': timestamp_str,
                'word_count': len(content.split()),
                'is_duplicate': 0
            })
            
        logger.info(f"Successfully scraped {len(documents)} reviews for {app_id}")
        return documents
    except Exception as e:
        logger.error(f"Error scraping Play Store app {app_id}: {e}")
        return []

if __name__ == '__main__':
    # Test script locally
    logging.basicConfig(level=logging.INFO)
    docs = scrape_playstore('com.zeptoconsumerapp', count=10)
    print(f"Scraped {len(docs)} sample reviews from Zepto app.")
    if docs:
        print("Sample review:", docs[0])
