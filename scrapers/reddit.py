import os
import uuid
import hashlib
import logging
from dotenv import load_dotenv
import praw

logger = logging.getLogger(__name__)
load_dotenv()

def get_reddit_client():
    """Initializes and returns a PRAW Reddit client if credentials are configured."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "ZeptoDiscoveryEngine/1.0")

    # If placeholders are present or keys are missing, return None
    if not client_id or not client_secret or "your_" in client_id or "your_" in client_secret:
        logger.warning("Reddit API credentials not configured in environment. Reddit scraping will be skipped or mocked.")
        return None

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        # Test read-only access
        reddit.read_only = True
        return reddit
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {e}")
        return None

def get_mock_reddit_data():
    """Returns realistic mock Reddit posts about Zepto/Blinkit for testing purposes."""
    logger.info("Generating mock Reddit discussions for testing.")
    mock_posts = [
        {
            "content": "Why does Zepto not sell high-end skincare or personal care items? I order groceries from here everyday, but I have to go to Nykaa or purple for my shampoo and moisturizer. It would be so convenient if they delivered in 10 mins.",
            "url": "https://reddit.com/r/zepto/comments/mock1",
            "author": "skincare_lover",
            "score": 45,
            "created": "2026-07-10T12:00:00Z"
        },
        {
            "content": "Switched from Zepto to Blinkit because Zepto does not show reviews for products. How can I buy a new brand of snacks or biscuits without seeing what others think? At least Blinkit shows star ratings on many items.",
            "url": "https://reddit.com/r/india/comments/mock2",
            "author": "curious_shopper",
            "score": 120,
            "created": "2026-07-11T14:30:00Z"
        },
        {
            "content": "Quick commerce has ruined my grocery shopping habits, but I refuse to buy fresh vegetables from Zepto. The quality is so hit-or-miss. For onions and potatoes I trust the local vendor or GoFresh where I can touch and pick them.",
            "url": "https://reddit.com/r/bangalore/comments/mock3",
            "author": "cook_from_scratch",
            "score": 88,
            "created": "2026-07-12T09:15:00Z"
        },
        {
            "content": "Zepto is super fast for milk and eggs, but their baby care section is empty. Trying to find diaper sizes or baby wipes is impossible. They should really expand this category.",
            "url": "https://reddit.com/r/zepto/comments/mock4",
            "author": "new_mom_2026",
            "score": 32,
            "created": "2026-07-13T18:40:00Z"
        },
        {
            "content": "Does anyone buy electronics from Zepto? I saw a mouse and keyboard on the app but I am too scared to order. What if it is defective? How does replacement work on Zepto? Better to order from Amazon even if it takes 1 day.",
            "url": "https://reddit.com/r/india/comments/mock5",
            "author": "tech_geek",
            "score": 150,
            "created": "2026-07-14T21:10:00Z"
        }
    ]
    
    documents = []
    for post in mock_posts:
        content = post["content"]
        author_hash = hashlib.sha256(post["author"].encode()).hexdigest()
        documents.append({
            'id': str(uuid.uuid4()),
            'source': 'reddit',
            'content': content,
            'content_clean': None,
            'source_url': post["url"],
            'author_hash': author_hash,
            'rating': None,
            'upvotes': post["score"],
            'source_timestamp': post["created"],
            'word_count': len(content.split()),
            'is_duplicate': 0
        })
    return documents

def scrape_reddit(limit=50):
    """Scrapes posts from Reddit about quick commerce or returns mock data if API credentials are not set."""
    reddit = get_reddit_client()
    if not reddit:
        return get_mock_reddit_data()

    logger.info(f"Searching Reddit for quick commerce discussions (limit: {limit})...")
    documents = []
    
    # Define subreddits and search terms
    subreddits = ['zepto', 'IndianFood', 'india', 'bangalore']
    search_queries = ['zepto', 'quick commerce', 'blinkit', 'instamart']
    
    try:
        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                # Search within subreddit
                for query in search_queries:
                    for submission in subreddit.search(query, limit=limit // len(subreddits)):
                        content = f"{submission.title}\n{submission.selftext}"
                        if len(content.strip()) < 15:
                            continue
                            
                        author = submission.author.name if submission.author else "deleted"
                        author_hash = hashlib.sha256(author.encode()).hexdigest()
                        
                        created_utc = submission.created_utc
                        import datetime
                        timestamp_str = datetime.datetime.fromtimestamp(created_utc, tz=datetime.timezone.utc).isoformat()
                        
                        doc_id = str(uuid.uuid4())
                        documents.append({
                            'id': doc_id,
                            'source': 'reddit',
                            'content': content,
                            'content_clean': None,
                            'source_url': f"https://reddit.com{submission.permalink}",
                            'author_hash': author_hash,
                            'rating': None,
                            'upvotes': int(submission.score),
                            'source_timestamp': timestamp_str,
                            'word_count': len(content.split()),
                            'is_duplicate': 0
                        })
            except Exception as e:
                logger.error(f"Error searching subreddit r/{sub_name}: {e}")
                continue
                
        logger.info(f"Successfully scraped {len(documents)} Reddit documents.")
        return documents
    except Exception as e:
        logger.error(f"Failed to scrape Reddit: {e}")
        return get_mock_reddit_data()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    docs = scrape_reddit(limit=10)
    print(f"Total documents parsed: {len(docs)}")
    if docs:
        print("Sample:", docs[0]["content"][:100] + "...")
