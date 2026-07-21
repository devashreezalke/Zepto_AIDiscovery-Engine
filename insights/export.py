import os
import json
import sqlite3
import datetime
import logging
from insights.segments import get_user_segments
from insights.research_mapping import RESEARCH_QUESTION_ANSWERS

logger = logging.getLogger(__name__)

def export_all_data(db_path='data/discovery.db', output_path='data/insights_export.json'):
    """Aggregates all insights, themes, segments, research questions, and stats into a single JSON file."""
    logger.info("Starting data export for dashboard...")
    
    if not os.path.exists(db_path):
        logger.error(f"Database not found at {db_path}. Run pipeline stages first.")
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Fetch Source Statistics
    cursor.execute("""
        SELECT source, COUNT(*), AVG(rating), AVG(word_count)
        FROM documents
        WHERE is_duplicate = 0
        GROUP BY source
    """)
    source_rows = cursor.fetchall()
    
    # Combine with avg sentiment score from analysis
    source_stats = {}
    for src, count, avg_rating, avg_words in source_rows:
        cursor.execute("""
            SELECT AVG(a.sentiment_score)
            FROM documents d
            JOIN analysis a ON d.id = a.doc_id
            WHERE d.source = ? AND d.is_duplicate = 0
        """, (src,))
        avg_sentiment = cursor.fetchone()[0] or 0.0
        
        source_stats[src] = {
            "name": src.replace("_", " ").title(),
            "doc_count": count,
            "avg_rating": round(avg_rating, 2) if avg_rating is not None else None,
            "avg_words": round(avg_words, 1),
            "avg_sentiment": round(avg_sentiment, 3)
        }

    # 2. Fetch Themes
    cursor.execute("""
        SELECT id, title, summary, macro_theme, drivers, blocked_categories, 
               research_questions, doc_count, avg_sentiment, representative_quotes 
        FROM themes
    """)
    theme_rows = cursor.fetchall()
    themes = []
    for row in theme_rows:
        themes.append({
            "id": row[0],
            "title": row[1],
            "summary": row[2],
            "macro_theme": row[3],
            "drivers": json.loads(row[4]),
            "blocked_categories": json.loads(row[5]),
            "research_questions": json.loads(row[6]),
            "doc_count": row[7],
            "avg_sentiment": round(row[8], 3),
            "representative_quotes": json.loads(row[9])
        })

    # 3. Fetch Insights
    cursor.execute("""
        SELECT id, title, finding, root_cause, impact, target_segment, 
               hypotheses, supporting_themes, confidence_score, confidence_level, research_questions
        FROM insights
    """)
    insight_rows = cursor.fetchall()
    insights = []
    for row in insight_rows:
        insights.append({
            "id": row[0],
            "title": row[1],
            "finding": row[2],
            "root_cause": row[3],
            "impact": json.loads(row[4]),
            "target_segment": json.loads(row[5]),
            "hypotheses": json.loads(row[6]),
            "supporting_themes": json.loads(row[7]),
            "confidence_score": round(row[8], 3),
            "confidence_level": row[9],
            "research_questions": json.loads(row[10])
        })

    # 4. Fetch User Segments
    segments = get_user_segments()

    # 5. Compile Research Question Answers
    # The 8 research questions mapped in problemStatement.md
    rq_definitions = {
        "Q1_habit_formation": "Why do Monthly Active Customers (MACs) purchase from the same categories repeatedly?",
        "Q2_discovery_barriers": "What prevents users from exploring new categories?",
        "Q3_discovery_mechanisms": "How do users discover products outside their usual checklist today?",
        "Q4_role_of_habits": "What is the role of shopping habits and routine loops?",
        "Q5_information_needs": "What information do users need before purchasing a new category?",
        "Q6_pain_points": "What are recurring frustrations in category browsing or checkout?",
        "Q7_user_segments": "Which user segments are most open to exploring new categories?",
        "Q8_unmet_needs": "What unmet needs or missing categories emerge from search/mentions?"
    }
    
    research_questions = []
    for rq_id, question_text in rq_definitions.items():
        # Find themes supporting this RQ
        supporting_themes = [t["id"] for t in themes if rq_id in t["research_questions"]]
        supporting_insights = [i["id"] for i in insights if rq_id in i["research_questions"]]
        
        # Calculate evidence strength
        total_docs = sum(t["doc_count"] for t in themes if t["id"] in supporting_themes)
        
        if total_docs >= 50:
            evidence_strength = "HIGH"
        elif total_docs >= 15:
            evidence_strength = "MEDIUM"
        elif total_docs > 0:
            evidence_strength = "LOW"
        else:
            evidence_strength = "INSUFFICIENT_DATA"
            
        # Fetch detailed answers from static research mapping
        detailed_ans = RESEARCH_QUESTION_ANSWERS.get(rq_id, {})
            
        research_questions.append({
            "id": rq_id,
            "question": question_text,
            "evidence_strength": evidence_strength,
            "supporting_themes": supporting_themes,
            "supporting_insights": supporting_insights,
            "document_count": total_docs,
            "finding": detailed_ans.get("finding", ""),
            "root_cause": detailed_ans.get("root_cause", ""),
            "quotes": detailed_ans.get("quotes", []),
            "hypothesis": detailed_ans.get("hypothesis", {})
        })

    # 6. Build final export JSON
    cursor.execute("SELECT COUNT(*) FROM documents WHERE is_duplicate = 0")
    total_docs = cursor.fetchone()[0]
    
    export_data = {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": {
            "total_documents": total_docs,
            "total_themes": len(themes),
            "total_insights": len(insights)
        },
        "source_stats": source_stats,
        "insights": insights,
        "themes": themes,
        "segments": segments,
        "research_questions": research_questions
    }
    
    conn.close()
    
    # Save output to primary data folder
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
        
    # Save output copy to dashboard public folder for Next.js access
    dashboard_public_path = os.path.join('dashboard', 'public', 'insights_export.json')
    try:
        os.makedirs(os.path.dirname(dashboard_public_path), exist_ok=True)
        with open(dashboard_public_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully copied export copy to {dashboard_public_path}")
    except Exception as e:
        logger.warning(f"Failed to copy export copy to dashboard public: {e}")
        
    logger.info(f"Successfully exported all dashboard data to {output_path}")
    return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    export_all_data()
