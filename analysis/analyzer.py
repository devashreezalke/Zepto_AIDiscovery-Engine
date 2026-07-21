import json
import sqlite3
import logging
from tqdm import tqdm
from analysis.groq_client import client
from analysis.prompts import (
    SENTIMENT_SYSTEM_PROMPT, SENTIMENT_USER_PROMPT,
    ANALYSIS_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT
)

logger = logging.getLogger(__name__)

def map_research_questions(sentiment, drivers, desired_categories):
    """Maps analyzed drivers, sentiment, and desired categories to the 8 research questions."""
    rqs = set()
    driver_types = {d.get('driver') for d in drivers}
    
    # Q1: Why do users buy the same categories?
    if 'HABIT_LOOP' in driver_types:
        rqs.add('Q1_habit_formation')
        
    # Q2: What prevents users from exploring new categories?
    if any(d in driver_types for d in ['DISCOVERY_FRICTION', 'TRUST_BARRIER', 'VALUE_PERCEPTION']):
        rqs.add('Q2_discovery_barriers')
        
    # Q3: How do users discover new categories/products today?
    if 'CONTEXTUAL_TRIGGER' in driver_types or 'DISCOVERY_FRICTION' in driver_types:
        rqs.add('Q3_discovery_mechanisms')
        
    # Q4: What is the role of shopping habits in quick-commerce?
    if 'HABIT_LOOP' in driver_types:
        rqs.add('Q4_role_of_habits')
        
    # Q5: What information do users need before purchasing a new category?
    if 'INFORMATION_GAP' in driver_types or 'TRUST_BARRIER' in driver_types:
        rqs.add('Q5_information_needs')
        
    # Q6: What are recurring frustrations with category browsing/checkout?
    if 'PLATFORM_LIMITATION' in driver_types or sentiment == 'negative':
        rqs.add('Q6_pain_points')
        
    # Q7: Which user segments are more likely to explore categories?
    if any(d in driver_types for d in ['CONTEXTUAL_TRIGGER', 'VALUE_PERCEPTION', 'HABIT_LOOP']):
        rqs.add('Q7_user_segments')
        
    # Q8: What unmet needs/categories emerge consistently?
    if 'INFORMATION_GAP' in driver_types or 'PLATFORM_LIMITATION' in driver_types or desired_categories:
        rqs.add('Q8_unmet_needs')
        
    return list(rqs)

def get_local_mock_analysis(content):
    """Fallback rule-based analyzer when Groq API key is not configured."""
    text_lower = content.lower()
    
    # 1. Mock Sentiment
    pos_words = ['good', 'love', 'great', 'fast', 'convenient', 'best', 'cared', 'happy', 'instant']
    neg_words = ['bad', 'terrible', 'slow', 'missing', 'delay', 'scared', 'defect', 'ruined', 'worse', 'worry']
    
    pos_score = sum(1 for w in pos_words if w in text_lower)
    neg_score = sum(1 for w in neg_words if w in text_lower)
    
    if pos_score > neg_score:
        sentiment = 'positive'
        sentiment_score = 0.6
        emotions = ['satisfaction']
    elif neg_score > pos_score:
        sentiment = 'negative'
        sentiment_score = -0.6
        emotions = ['frustration' if 'delay' in text_lower or 'slow' in text_lower else 'anxiety']
    else:
        sentiment = 'neutral'
        sentiment_score = 0.0
        emotions = []
        
    # 2. Mock Categories
    categories = []
    desired = []
    if any(w in text_lower for w in ['diaper', 'baby', 'parent', 'mom']):
        categories.append('Baby Care')
    if any(w in text_lower for w in ['shampoo', 'soap', 'skincare', 'cream', 'moisturizer', 'dove', 'cetaphil']):
        categories.append('Personal Care')
    if any(w in text_lower for w in ['vegetable', 'fruit', 'grocery', 'groceries', 'milk', 'egg', 'onion', 'potato']):
        categories.append('Groceries')
    if any(w in text_lower for w in ['keyboard', 'mouse', 'charger', 'cable', 'electronics', 'device']):
        categories.append('Electronics')
    if any(w in text_lower for w in ['snack', 'drink', 'beverage', 'chips', 'biscuit', 'cold brew', 'coffee']):
        categories.append('Snacks & Beverages')
        
    # 3. Mock Drivers
    drivers = []
    if any(w in text_lower for w in ['habit', 'usual', 'offline', 'default']):
        drivers.append({
            "driver": "HABIT_LOOP",
            "sub_driver": "default_offline_shopping",
            "confidence": 0.85,
            "evidence": content[:50]
        })
    if any(w in text_lower for w in ['search', 'navigate', 'ui', 'find', 'catalog', 'recommend']):
        drivers.append({
            "driver": "DISCOVERY_FRICTION",
            "sub_driver": "poor_navigation",
            "confidence": 0.8,
            "evidence": content[:50]
        })
    if any(w in text_lower for w in ['trust', 'scared', 'authentic', 'quality', 'return', 'replace', 'defective']):
        drivers.append({
            "driver": "TRUST_BARRIER",
            "sub_driver": "quality_skepticism" if 'quality' in text_lower else "returns_friction",
            "confidence": 0.9,
            "evidence": content[:50]
        })
    if any(w in text_lower for w in ['price', 'expensive', 'discount', 'offer', 'cost']):
        drivers.append({
            "driver": "VALUE_PERCEPTION",
            "sub_driver": "higher_prices",
            "confidence": 0.75,
            "evidence": content[:50]
        })
    if any(w in text_lower for w in ['reviews', 'ratings', 'feedback', 'star']):
        drivers.append({
            "driver": "INFORMATION_GAP",
            "sub_driver": "missing_reviews",
            "confidence": 0.9,
            "evidence": content[:50]
        })
    if any(w in text_lower for w in ['emergency', 'recipe', 'need', 'immediate']):
        drivers.append({
            "driver": "CONTEXTUAL_TRIGGER",
            "sub_driver": "emergency_need",
            "confidence": 0.7,
            "evidence": content[:50]
        })
    if any(w in text_lower for w in ['crash', 'bug', 'stock', 'slow', 'delay']):
        drivers.append({
            "driver": "PLATFORM_LIMITATION",
            "sub_driver": "out_of_stock" if 'stock' in text_lower else "app_performance_issues",
            "confidence": 0.85,
            "evidence": content[:50]
        })
        
    # Default driver if none matched
    if not drivers:
        drivers.append({
            "driver": "HABIT_LOOP",
            "sub_driver": "lack_of_top_of_mind_awareness",
            "confidence": 0.5,
            "evidence": content[:30]
        })
        
    # Map research questions
    rqs = map_research_questions(sentiment, drivers, desired)
        
    return {
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'emotions': json.dumps(emotions),
        'categories_mentioned': json.dumps(categories),
        'categories_desired': json.dumps(desired),
        'category_switch_signal': 1 if 'switch' in text_lower or len(categories) > 1 else 0,
        'behavioral_drivers': json.dumps(drivers),
        'research_questions': json.dumps(rqs)
    }

def analyze_single_document(content):
    """Performs sentiment and category/driver analysis for a single text string."""
    # Fallback if Groq key is not configured
    if not client.api_key:
        return get_local_mock_analysis(content)
        
    try:
        # 1. Sentiment & Emotion Analysis
        sentiment_data = client.request_json(
            system_prompt=SENTIMENT_SYSTEM_PROMPT,
            user_prompt=SENTIMENT_USER_PROMPT.format(content=content),
            model=client.bulk_model
        )
        
        # 2. Category & Driver Analysis
        analysis_data = client.request_json(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=ANALYSIS_USER_PROMPT.format(content=content),
            model=client.bulk_model
        )
        
        # 3. Combine responses
        combined = {
            'sentiment': sentiment_data.get('sentiment', 'neutral'),
            'sentiment_score': sentiment_data.get('sentiment_score', 0.0),
            'emotions': json.dumps(sentiment_data.get('emotions', [])),
            'categories_mentioned': json.dumps(analysis_data.get('categories_mentioned', [])),
            'categories_desired': json.dumps(analysis_data.get('categories_desired', [])),
            'category_switch_signal': int(analysis_data.get('category_switch_signal', False)),
            'behavioral_drivers': json.dumps(analysis_data.get('behavioral_drivers', []))
        }
    except Exception as e:
        logger.warning(f"Groq API call failed: {e}. Falling back to local rule-based mock analysis.")
        return get_local_mock_analysis(content)
    
    # 4. Map to research questions
    drivers = json.loads(combined['behavioral_drivers'])
    desired = json.loads(combined['categories_desired'])
    rqs = map_research_questions(combined['sentiment'], drivers, desired)
    combined['research_questions'] = json.dumps(rqs)
    
    return combined

def run_analysis_pipeline(db_path='data/discovery.db', limit=None):
    """Fetches un-analyzed documents and runs them through the Groq analysis pipeline."""
    logger.info("Starting Groq AI analysis pipeline...")
    
    # Open DB connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find documents that haven't been analyzed yet
    cursor.execute("""
        SELECT d.id, d.content_clean FROM documents d
        LEFT JOIN analysis a ON d.id = a.doc_id
        WHERE a.doc_id IS NULL AND d.is_duplicate = 0
    """)
    rows = cursor.fetchall()
    
    # Apply limit if specified
    if limit:
        rows = rows[:limit]
        
    logger.info(f"Found {len(rows)} un-analyzed documents to process.")
    if not rows:
        logger.info("No new documents to analyze.")
        conn.close()
        return
        
    processed_count = 0
    failed_count = 0
    
    # Process with progress bar
    for doc_id, content in tqdm(rows, desc="Analyzing documents"):
        try:
            # Analyze using Groq client
            results = analyze_single_document(content)
            
            # Save results
            cursor.execute("""
                INSERT OR REPLACE INTO analysis (
                    doc_id, sentiment, sentiment_score, emotions, 
                    categories_mentioned, categories_desired, category_switch_signal, 
                    behavioral_drivers, research_questions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                doc_id,
                results['sentiment'],
                results['sentiment_score'],
                results['emotions'],
                results['categories_mentioned'],
                results['categories_desired'],
                results['category_switch_signal'],
                results['behavioral_drivers'],
                results['research_questions']
            ))
            conn.commit()
            processed_count += 1
        except Exception as e:
            logger.error(f"Failed to analyze document {doc_id}: {e}")
            failed_count += 1
            
    conn.close()
    logger.info(f"AI Analysis completed. Success: {processed_count}, Failed: {failed_count}")
    return processed_count

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # Test run on 3 documents to verify API prompts
    run_analysis_pipeline(limit=3)
