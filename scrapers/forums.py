import uuid
import hashlib
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def get_mock_forum_data():
    """Returns realistic mock forum posts concerning Zepto/Blinkit category expansion barriers."""
    logger.info("Generating mock forum discussions for testing.")
    mock_forum_posts = [
        {
            "content": "I buy my weekly groceries on Zepto, but for home decor and kitchen utensils, I prefer Amazon. The selection on Zepto is too small. In kitchen tools, they only have 2 brands of knives and 1 chopping board. How can I browse and find the best item when there are only two choices?",
            "url": "https://consumerforum.in/threads/mock-qcommerce-decor",
            "author": "kitchen_enthusiast",
            "upvotes": 15,
            "created": "2026-07-08T11:00:00Z"
        },
        {
            "content": "Zepto is expanding to electronics and books but their replacement policy is unclear. In Amazon, I can return a book or a charger in 7 days. If a book from Zepto comes torn, do I get an immediate refund or replacement? The delivery guy won't wait. Has anyone tried replacement for high-value goods on Zepto?",
            "url": "https://consumerforum.in/threads/mock-qcommerce-returns",
            "author": "consumer_rights_india",
            "upvotes": 42,
            "created": "2026-07-09T16:15:00Z"
        },
        {
            "content": "Why is Zepto's personal care section mostly filled with off-brand items? For baby diapers and baby soaps, I only buy Pampers and Sebamed. On Zepto, they only have local brands or private labels in stock. I don't trust private labels for baby skin. I'd rather buy from FirstCry or local medical shop.",
            "url": "https://consumerforum.in/threads/mock-qcommerce-babycare",
            "author": "parenting_guy",
            "upvotes": 28,
            "created": "2026-07-12T10:30:00Z"
        }
    ]

    documents = []
    for post in mock_forum_posts:
        content = post["content"]
        author_hash = hashlib.sha256(post["author"].encode()).hexdigest()
        documents.append({
            'id': str(uuid.uuid4()),
            'source': 'forum',
            'content': content,
            'content_clean': None,
            'source_url': post["url"],
            'author_hash': author_hash,
            'rating': None,
            'upvotes': post["upvotes"],
            'source_timestamp': post["created"],
            'word_count': len(content.split()),
            'is_duplicate': 0
        })
    return documents

def scrape_forums():
    """Scrapes public forums. Falls back to mock data if networking fails or link is blocked."""
    logger.info("Attempting to scrape public consumer forums for quick commerce content...")
    documents = []
    
    # Example consumer forum thread to check
    test_url = "https://example.com/consumer-discussions"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(test_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Example parsing logic (normally tailored to specific forum layouts)
            posts = soup.find_all('div', class_='forum-post')
            for post in posts:
                text = post.get_text().strip()
                if len(text) < 15:
                    continue
                doc_id = str(uuid.uuid4())
                author = post.find('span', class_='author').get_text() if post.find('span', class_='author') else "anonymous"
                author_hash = hashlib.sha256(author.encode()).hexdigest()
                
                documents.append({
                    'id': doc_id,
                    'source': 'forum',
                    'content': text,
                    'content_clean': None,
                    'source_url': test_url,
                    'author_hash': author_hash,
                    'rating': None,
                    'upvotes': 0,
                    'source_timestamp': None,
                    'word_count': len(text.split()),
                    'is_duplicate': 0
                })
        
        if not documents:
            logger.info("No active threads found or page structure mismatch. Falling back to mock forum data.")
            return get_mock_forum_data()
        return documents
    except Exception as e:
        logger.warning(f"Consumer forum scraping failed: {e}. Falling back to mock forum data.")
        return get_mock_forum_data()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    docs = scrape_forums()
    print(f"Total forum documents: {len(docs)}")
    if docs:
        print("Sample:", docs[0]["content"])
