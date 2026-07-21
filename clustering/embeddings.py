import json
import sqlite3
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from analysis.groq_client import client

logger = logging.getLogger(__name__)

def get_primary_driver(behavioral_drivers_json):
    """Extracts the primary driver name from the JSON array string."""
    try:
        drivers = json.loads(behavioral_drivers_json)
        if drivers:
            # Sort by confidence descending
            drivers_sorted = sorted(drivers, key=lambda x: x.get('confidence', 0.0), reverse=True)
            return drivers_sorted[0].get('driver', '')
    except Exception:
        pass
    return ""

def generate_embeddings(db_path='data/discovery.db'):
    """Generates embeddings for analyzed documents using sentence-transformers."""
    logger.info("Fetching analyzed documents for embedding generation...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Select clean documents and their analysis results
    cursor.execute("""
        SELECT d.id, d.content_clean, a.behavioral_drivers 
        FROM documents d
        JOIN analysis a ON d.id = a.doc_id
        WHERE d.is_duplicate = 0
    """)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        logger.warning("No analyzed documents found. Run analysis first.")
        return [], np.array([])
        
    doc_ids = []
    texts_to_embed = []
    
    for doc_id, content, drivers_json in rows:
        primary_driver = get_primary_driver(drivers_json)
        
        # Concatenate text with primary driver to inject strong semantic signal
        if primary_driver:
            text_to_embed = f"[{primary_driver}] {content}"
        else:
            text_to_embed = content
            
        doc_ids.append(doc_id)
        texts_to_embed.append(text_to_embed)
        
    # Check if we should directly bypass to prevent Windows memory exhaustion in mock run
    if not client.api_key:
        logger.info("GROQ_API_KEY is not configured. Directly using category+driver-based semantic vectors fallback (saves CPU/Memory).")
        use_mock = True
    else:
        use_mock = False
        
    embeddings = None
    if not use_mock:
        logger.info(f"Loading sentence-transformers model 'all-MiniLM-L6-v2'...")
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info(f"Generating embeddings for {len(texts_to_embed)} documents...")
            embeddings = model.encode(texts_to_embed, show_progress_bar=True)
            embeddings = np.array(embeddings)
        except Exception as e:
            logger.warning(f"SentenceTransformer failed to load/run ({e}). Falling back to local category+driver-based semantic vectors.")
            use_mock = True

    if use_mock:
        # Rule-based semantic vector generator fallback (384 dimensions)
        # We assign distinct orthogonal coordinates based on category and driver, then normalize.
        categories_map = {
            "Groceries": 0, "Snacks & Beverages": 1, "Personal Care": 2, "Baby Care": 3,
            "Pet Supplies": 4, "Household Essentials": 5, "Electronics": 6, "Pharma": 7
        }
        drivers_map = {
            "HABIT_LOOP": 0, "DISCOVERY_FRICTION": 1, "TRUST_BARRIER": 2, "VALUE_PERCEPTION": 3,
            "INFORMATION_GAP": 4, "CONTEXTUAL_TRIGGER": 5, "PLATFORM_LIMITATION": 6
        }
        
        embeddings_list = []
        # Connect to DB to read categories/drivers for these document IDs
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for doc_id in doc_ids:
            cursor.execute("SELECT categories_mentioned, behavioral_drivers FROM analysis WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            
            # Base vector: all zeros
            vec = np.zeros(384)
            
            # Add small random noise for cluster dispersion
            np.random.seed(hash(doc_id) % 123456)
            vec += np.random.normal(0, 0.05, 384)
            
            if row:
                try:
                    cats = json.loads(row[0])
                    drivers = json.loads(row[1])
                    
                    # Highlight category coordinate block (indices 0 to 79)
                    for cat in cats:
                        if cat in categories_map:
                            cat_idx = categories_map[cat]
                            vec[cat_idx * 10 : (cat_idx + 1) * 10] += 1.5
                            
                    # Highlight driver coordinate block (indices 100 to 169)
                    for d in drivers:
                        driver_name = d.get('driver')
                        if driver_name in drivers_map:
                            d_idx = drivers_map[driver_name]
                            vec[100 + d_idx * 10 : 100 + (d_idx + 1) * 10] += 2.0
                except:
                    pass
            
            # Normalize vector
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
                
            embeddings_list.append(vec)
            
        conn.close()
        embeddings = np.array(embeddings_list)
    
    logger.info(f"Embeddings generated successfully. Shape: {embeddings.shape}")
    return doc_ids, embeddings

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    ids, embs = generate_embeddings()
    print(f"Generated {len(ids)} embeddings.")
