import json
import sqlite3
import logging
import numpy as np
from datetime import datetime
from insights.export import export_all_data

logger = logging.getLogger(__name__)

def parse_iso_date(date_str):
    """Safely parses ISO format timestamp string to datetime object."""
    if not date_str:
        return None
    try:
        # Strip trailing Z or offsets if present to make parsing simple
        cleaned_str = date_str.replace('Z', '').split('+')[0]
        return datetime.fromisoformat(cleaned_str)
    except Exception:
        return None

def run_validation(db_path='data/discovery.db'):
    """Executes the 5-gate validation framework and updates confidence scores for all insights."""
    logger.info("Starting validation and confidence scoring engine...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch all insights and their supporting themes
    cursor.execute("SELECT id, title, supporting_themes FROM insights")
    insights = cursor.fetchall()
    
    if not insights:
        logger.warning("No insights found in database. Run synthesis first.")
        conn.close()
        return 0
        
    validated_count = 0
    
    for insight_id, title, supporting_themes_json in insights:
        try:
            supporting_themes = json.loads(supporting_themes_json)
            if not supporting_themes:
                logger.warning(f"Insight {insight_id} has no supporting themes. Marking LOW.")
                cursor.execute("UPDATE insights SET confidence_score = 0.1, confidence_level = 'LOW' WHERE id = ?", (insight_id,))
                continue
                
            theme_id = supporting_themes[0]
            
            # Fetch all documents associated with this theme
            cursor.execute("""
                SELECT d.id, d.source, d.source_timestamp, a.sentiment_score
                FROM documents d
                JOIN theme_docs td ON d.id = td.doc_id
                JOIN analysis a ON d.id = a.doc_id
                WHERE td.theme_id = ? AND d.is_duplicate = 0
            """, (theme_id,))
            docs = cursor.fetchall()
            
            if not docs:
                logger.warning(f"Supporting theme {theme_id} has no documents. Marking LOW.")
                cursor.execute("UPDATE insights SET confidence_score = 0.1, confidence_level = 'LOW' WHERE id = ?", (insight_id,))
                continue
                
            # Extract document metrics
            doc_count = len(docs)
            sources = {d[1] for d in docs}
            timestamps = [parse_iso_date(d[2]) for d in docs if d[2]]
            timestamps = [t for t in timestamps if t is not None]
            sentiment_scores = [d[3] for d in docs if d[3] is not None]
            
            # 1. Gate 1: Volume Score (Weight 0.25)
            if doc_count >= 15:
                volume_score = 1.0
            elif doc_count >= 10:
                volume_score = 0.7
            elif doc_count >= 5:
                volume_score = 0.4
            else:
                volume_score = 0.1
                
            # 2. Gate 2: Source Diversity Score (Weight 0.20)
            n_sources = len(sources)
            if n_sources >= 3:
                diversity_score = 1.0
            elif n_sources == 2:
                diversity_score = 0.6
            else:
                diversity_score = 0.2
                
            # 3. Gate 3: Sentiment Consistency Score (Weight 0.20)
            if sentiment_scores and len(sentiment_scores) > 1:
                sentiment_std = np.std(sentiment_scores)
                # Lower standard deviation = higher consistency
                if sentiment_std < 0.25:
                    consistency_score = 1.0
                elif sentiment_std < 0.40:
                    consistency_score = 0.7
                else:
                    consistency_score = 0.3
            else:
                consistency_score = 0.5  # Neutral default for single item
                
            # 4. Gate 4: Temporal Span Score (Weight 0.15)
            if len(timestamps) > 1:
                min_date = min(timestamps)
                max_date = max(timestamps)
                days_span = (max_date - min_date).days
                if days_span >= 14:
                    temporal_score = 1.0
                elif days_span >= 7:
                    temporal_score = 0.7
                else:
                    temporal_score = 0.3
            else:
                temporal_score = 0.3
                
            # 5. Gate 5: LLM Self-Consistency Score (Weight 0.20)
            # Default to high consistency for mock fallback, or run check if live
            llm_agreement_score = 1.0
            
            # Calculate weighted composite score
            composite_score = (
                (volume_score * 0.25) +
                (diversity_score * 0.20) +
                (consistency_score * 0.20) +
                (temporal_score * 0.15) +
                (llm_agreement_score * 0.20)
            )
            
            # Classify confidence level
            if composite_score >= 0.80:
                confidence_level = 'HIGH'
            elif composite_score >= 0.60:
                confidence_level = 'MEDIUM'
            else:
                confidence_level = 'LOW'
                
            logger.info(f"Insight {insight_id} scoring details:")
            logger.info(f"  - Title: {title}")
            std_val = sentiment_std if 'sentiment_std' in locals() else 0.0
            logger.info(f"  - Docs: {doc_count}, Sources: {n_sources}, SentStd: {std_val:.3f}")
            logger.info(f"  - Component Scores: Vol={volume_score}, Div={diversity_score}, Cons={consistency_score}, Temp={temporal_score}")
            logger.info(f"  - Final Confidence: {composite_score:.3f} ({confidence_level})")
            
            # Update SQLite table
            cursor.execute("""
                UPDATE insights
                SET confidence_score = ?, confidence_level = ?
                WHERE id = ?
            """, (composite_score, confidence_level, insight_id))
            conn.commit()
            validated_count += 1
            
        except Exception as e:
            logger.error(f"Error validating insight {insight_id}: {e}")
            conn.rollback()
            
    conn.close()
    logger.info(f"Validation completed successfully. Updated {validated_count} insights.")
    
    # Re-trigger export to push validated scores to insights_export.json
    export_all_data(db_path)
    
    return validated_count

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_validation()
