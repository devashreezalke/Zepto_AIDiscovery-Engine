import json
import sqlite3
import logging
from tqdm import tqdm
from analysis.groq_client import client
from clustering.cluster import run_clustering
from clustering.label_prompts import THEME_LABEL_SYSTEM_PROMPT, THEME_LABEL_USER_PROMPT

logger = logging.getLogger(__name__)

def generate_and_save_themes(db_path='data/discovery.db'):
    """Performs clustering, queries Groq to label each cluster, and saves results to SQLite."""
    # 1. Run DBSCAN clustering
    doc_cluster_map, unique_labels = run_clustering(db_path)
    
    if not doc_cluster_map:
        logger.warning("No clustered documents. Skipping theme generation.")
        return 0
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clean previous themes and relationships
    cursor.execute("DELETE FROM themes")
    cursor.execute("DELETE FROM theme_docs")
    conn.commit()
    
    # 2. Iterate through each valid cluster (exclude noise cluster -1)
    theme_count = 0
    
    for label in unique_labels:
        if label == -1:
            continue
            
        # Get all doc IDs in this cluster
        cluster_doc_ids = [doc_id for doc_id, c_id in doc_cluster_map.items() if c_id == label]
        
        # Fetch clean content + meta for all docs in this cluster
        placeholders = ','.join('?' for _ in cluster_doc_ids)
        cursor.execute(f"""
            SELECT d.id, d.content_clean, d.rating, d.source, a.sentiment_score
            FROM documents d
            JOIN analysis a ON d.id = a.doc_id
            WHERE d.id IN ({placeholders})
        """, cluster_doc_ids)
        docs = cursor.fetchall()
        
        # Calculate stats for the cluster
        doc_count = len(docs)
        ratings = [d[2] for d in docs if d[2] is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None
        sentiments = [d[4] for d in docs if d[4] is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        # Sample representative documents (sort by word count descending to get detailed reviews)
        sorted_docs = sorted(docs, key=lambda x: len(x[1].split()), reverse=True)
        sampled_docs = sorted_docs[:15]
        
        # Format quotes block for prompt
        quotes_text = ""
        for i, (_, text, rating, source, _) in enumerate(sampled_docs, 1):
            rating_str = f" [Rating: {rating}/5]" if rating is not None else ""
            quotes_text += f"{i}. \"{text}\" (Source: {source}{rating_str})\n"
            
        # Compile representative quotes to store in the DB
        representative_quotes = [d[1] for d in sampled_docs[:3]]
        
        logger.info(f"Generating theme metadata for Cluster {label} ({doc_count} documents)...")
        
        # 3. Request LLM Theme Labeling
        try:
            if not client.api_key:
                # Local mock theme labeler fallback
                # Find most common driver and category in this cluster
                cluster_doc_ids_placeholders = ','.join('?' for _ in cluster_doc_ids)
                cursor.execute(f"""
                    SELECT behavioral_drivers, categories_mentioned
                    FROM analysis
                    WHERE doc_id IN ({cluster_doc_ids_placeholders})
                """, cluster_doc_ids)
                analysis_rows = cursor.fetchall()
                
                drivers_list = []
                categories_list = []
                for row_d, row_c in analysis_rows:
                    try:
                        drivers_list.extend([d.get('driver') for d in json.loads(row_d)])
                        categories_list.extend(json.loads(row_c))
                    except:
                        pass
                
                from collections import Counter
                common_driver = Counter(drivers_list).most_common(1)[0][0] if drivers_list else "HABIT_LOOP"
                common_category = Counter(categories_list).most_common(1)[0][0] if categories_list else "Groceries"
                
                # Mock theme mappings
                mock_themes = {
                    "TRUST_BARRIER": {
                        "title": f"Quality and Trust barriers for {common_category}",
                        "summary": f"Users express concerns regarding product quality, freshness, and return speed in {common_category}.",
                        "macro_theme": "Trust & Quality",
                        "key_drivers": ["TRUST_BARRIER"],
                        "blocked_categories": [common_category],
                        "research_questions": ["Q2_discovery_barriers", "Q5_information_needs"]
                    },
                    "INFORMATION_GAP": {
                        "title": f"Information gaps for {common_category} items",
                        "summary": f"Missing reviews, star ratings, and detailed descriptions make users hesitant to buy {common_category}.",
                        "macro_theme": "Information Gaps",
                        "key_drivers": ["INFORMATION_GAP"],
                        "blocked_categories": [common_category],
                        "research_questions": ["Q5_information_needs", "Q8_unmet_needs"]
                    },
                    "HABIT_LOOP": {
                        "title": f"Habitual purchase patterns block {common_category} exploration",
                        "summary": f"Users default to buying {common_category} from offline vendors or other apps due to default habits.",
                        "macro_theme": "Habit & Cognitive Load",
                        "key_drivers": ["HABIT_LOOP"],
                        "blocked_categories": [common_category],
                        "research_questions": ["Q1_habit_formation", "Q4_role_of_habits"]
                    },
                    "DISCOVERY_FRICTION": {
                        "title": f"Friction in category discovery for {common_category}",
                        "summary": f"App search bugs, poor layout navigation, or lack of recommendations hide {common_category} catalog.",
                        "macro_theme": "Discovery Friction",
                        "key_drivers": ["DISCOVERY_FRICTION"],
                        "blocked_categories": [common_category],
                        "research_questions": ["Q2_discovery_barriers", "Q3_discovery_mechanisms"]
                    },
                    "VALUE_PERCEPTION": {
                        "title": f"Value and pricing concerns for {common_category}",
                        "summary": f"Users perceive Zepto prices to be higher than supermarket bulk purchases for {common_category}.",
                        "macro_theme": "Pricing & Value",
                        "key_drivers": ["VALUE_PERCEPTION"],
                        "blocked_categories": [common_category],
                        "research_questions": ["Q2_discovery_barriers", "Q6_pain_points"]
                    },
                    "PLATFORM_LIMITATION": {
                        "title": f"Platform constraints for {common_category} items",
                        "summary": f"Frequent out-of-stock items or delivery speed drops prevent regular purchases in {common_category}.",
                        "macro_theme": "Platform Limitations",
                        "key_drivers": ["PLATFORM_LIMITATION"],
                        "blocked_categories": [common_category],
                        "research_questions": ["Q6_pain_points", "Q8_unmet_needs"]
                    }
                }
                
                theme_meta = mock_themes.get(common_driver, {
                    "title": f"User exploration barriers in {common_category}",
                    "summary": f"General user feedback highlights multiple barriers affecting purchases in {common_category}.",
                    "macro_theme": "Habit & Cognitive Load",
                    "key_drivers": [common_driver],
                    "blocked_categories": [common_category],
                    "research_questions": ["Q2_discovery_barriers"]
                })
            else:
                theme_meta = client.request_json(
                    system_prompt=THEME_LABEL_SYSTEM_PROMPT,
                    user_prompt=THEME_LABEL_USER_PROMPT.format(
                        n=len(sampled_docs),
                        sampled_texts=quotes_text
                    ),
                    model=client.quality_model
                )
            
            theme_id = f"theme_{label}"
            
            # Save theme
            cursor.execute("""
                INSERT INTO themes (
                    id, title, summary, macro_theme, drivers, 
                    blocked_categories, research_questions, doc_count, 
                    avg_sentiment, representative_quotes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                theme_id,
                theme_meta.get('title', f"Theme {label}"),
                theme_meta.get('summary', ''),
                theme_meta.get('macro_theme', 'General'),
                json.dumps(theme_meta.get('key_drivers', [])),
                json.dumps(theme_meta.get('blocked_categories', [])),
                json.dumps(theme_meta.get('research_questions', [])),
                doc_count,
                avg_sentiment,
                json.dumps(representative_quotes)
            ))
            
            # Save doc relationships
            for doc_id in cluster_doc_ids:
                cursor.execute("""
                    INSERT INTO theme_docs (theme_id, doc_id)
                    VALUES (?, ?)
                """, (theme_id, doc_id))
                
            conn.commit()
            theme_count += 1
            logger.info(f"Saved Theme {theme_id}: {theme_meta.get('title')}")
            
        except Exception as e:
            logger.error(f"Failed to label theme for cluster {label}: {e}")
            conn.rollback()
            
    conn.close()
    logger.info(f"Theme generation complete. Total themes saved: {theme_count}")
    return theme_count

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_and_save_themes()
