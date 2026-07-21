import uuid
import hashlib
import logging
import datetime
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

def get_mock_twitter_data():
    """Returns realistic mock tweets about Zepto category selection and customer reactions."""
    logger.info("Generating mock Twitter/X discussions for testing.")
    mock_tweets = [
        {
            "content": "Zepto delivery is 8 mins but why is the personal care section so bad? Out of stock for basic Cetaphil wash. Had to order from Amazon. #zepto #quickcommerce",
            "url": "https://twitter.com/user1/status/112233",
            "author": "tech_guy_99",
            "likes": 12,
            "created": "2026-07-14T10:00:00Z"
        },
        {
            "content": "Tried ordering fresh fruits on Zepto today. Quality of apples was quite sub-par. I think I'll stick to buying veggies offline where I can check freshness. #grocery #quickcomm",
            "url": "https://twitter.com/user2/status/445566",
            "author": "organic_foodie",
            "likes": 34,
            "created": "2026-07-14T15:20:00Z"
        },
        {
            "content": "Why is there no product review section in Zepto? Wanted to try a new cold brew brand but too scared to buy without seeing customer feedback first. Going to order from Amazon. @ZeptoNow",
            "url": "https://twitter.com/user3/status/778899",
            "author": "coffee_caffeine",
            "likes": 56,
            "created": "2026-07-15T08:15:00Z"
        },
        {
            "content": "ordered a diaper pack for my nephew on Zepto, but they delivered the wrong size. Customer care refunded instantly but now I have to order again. Still no size selection on diaper brand category page. Frustrating UX.",
            "url": "https://twitter.com/user4/status/101112",
            "author": "angry_uncle",
            "likes": 5,
            "created": "2026-07-15T11:45:00Z"
        },
        {
            "content": "Zepto has electronics now? Who is buying keyboards and chargers in 10 mins? 🙄 What about return policy? If it breaks, do they send a delivery boy to pick it up? Trust issues.",
            "url": "https://twitter.com/user5/status/131415",
            "author": "skeptic_retailer",
            "likes": 198,
            "created": "2026-07-15T13:00:00Z"
        }
    ]

    documents = []
    for tweet in mock_tweets:
        content = tweet["content"]
        author_hash = hashlib.sha256(tweet["author"].encode()).hexdigest()
        documents.append({
            'id': str(uuid.uuid4()),
            'source': 'twitter',
            'content': content,
            'content_clean': None,
            'source_url': tweet["url"],
            'author_hash': author_hash,
            'rating': None,
            'upvotes': tweet["likes"],
            'source_timestamp': tweet["created"],
            'word_count': len(content.split()),
            'is_duplicate': 0
        })
    return documents

def scrape_twitter(query="zepto delivery", limit=50):
    """
    Scrapes tweets about quick commerce.
    Since Twitter search scrape is frequently blocked, we gracefully fall back to mock data.
    """
    logger.info(f"Attempting to scrape Twitter/X using snscrape for query: '{query}'...")
    documents = []
    
    try:
        # Import snscrape locally to prevent top-level import crashes
        import snscrape.modules.twitter as sntwitter
        
        scraper = sntwitter.TwitterSearchScraper(query)
        for i, tweet in enumerate(scraper.get_items()):
            if i >= limit:
                break
                
            content = tweet.rawContent
            if len(content.strip()) < 15:
                continue
                
            author = tweet.user.username if tweet.user else "anonymous"
            author_hash = hashlib.sha256(author.encode()).hexdigest()
            timestamp_str = tweet.date.isoformat()
            
            doc_id = str(uuid.uuid4())
            documents.append({
                'id': doc_id,
                'source': 'twitter',
                'content': content,
                'content_clean': None,
                'source_url': tweet.url,
                'author_hash': author_hash,
                'rating': None,
                'upvotes': int(tweet.likeCount),
                'source_timestamp': timestamp_str,
                'word_count': len(content.split()),
                'is_duplicate': 0
            })
            
        logger.info(f"Successfully scraped {len(documents)} tweets.")
        if not documents:
            logger.warning("No tweets found. Falling back to mock data.")
            return get_mock_twitter_data()
        return documents
    except Exception as e:
        logger.warning(f"snscrape Twitter search failed: {e}. Falling back to mock Twitter/X data.")
        return get_mock_twitter_data()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    docs = scrape_twitter(limit=10)
    print(f"Total Twitter documents parsed: {len(docs)}")
    if docs:
        print("Sample:", docs[0]["content"])
