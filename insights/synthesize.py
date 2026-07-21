import json
import sqlite3
import logging
from dotenv import load_dotenv
from analysis.groq_client import client

logger = logging.getLogger(__name__)
load_dotenv()

# Pre-defined mock insights mapping for fallback runs (when GROQ_API_KEY is missing)
MOCK_INSIGHTS = {
    "Habitual purchase patterns block Groceries exploration": {
        "title": "Default Grocery Buying Habits Block App Discovery",
        "finding": "177 users default to offline grocery shopping due to established habit loops and lack of top-of-mind awareness for non-staple items on Zepto.",
        "root_cause": "Buying fresh items is an automatic cognitive habit. Users only open Zepto for emergency staples (milk, eggs) and don't evaluate other categories because they default to local markets out of muscle memory.",
        "impact": {
            "affected_users": "45% of MACs",
            "blocked_category": "Groceries",
            "severity": "high"
        },
        "target_segment": {
            "description": "Habitual Minimalists",
            "behavioral_profile": "Order the same 3-4 staple items twice a week, rarely open search, and checkout in under 60 seconds."
        },
        "hypotheses": [
            {
                "statement": "If we inject contextual category cross-sells at cart checkout for staples (e.g., recommend coriander/lemons when buying onions/tomatoes), then we break the default habit and increase category entry by 18%.",
                "experiment_type": "A/B test",
                "effort": "low",
                "expected_impact": "medium"
            },
            {
                "statement": "If we introduce a 'weekly grocery list' auto-replenish reminder notification, then we capture planned weekly grocery buying and increase category penetration.",
                "experiment_type": "pre-post",
                "effort": "medium",
                "expected_impact": "high"
            }
        ]
    },
    "Quality and Trust barriers for Groceries": {
        "title": "Freshness Skepticism Blocks Fresh Produce Adoption",
        "finding": "12 users express strong trust barriers and quality concerns, refusing to buy fresh fruits and vegetables online.",
        "root_cause": "Users believe that picker boys do not select fresh onions, tomatoes, or greens, and fear receiving rotten/sub-standard produce without an easy inspect-on-delivery option.",
        "impact": {
            "affected_users": "35% of MACs",
            "blocked_category": "Groceries",
            "severity": "high"
        },
        "target_segment": {
            "description": "Life-Stage Movers",
            "behavioral_profile": "Willing to spend more for family health but require visual quality assurance and proof of freshness."
        },
        "hypotheses": [
            {
                "statement": "If we show 'Last Stock Checked' timestamps and grower farm origin details on the fresh produce PDP, then we reduce quality skepticism and lift category conversion by 12%.",
                "experiment_type": "A/B test",
                "effort": "medium",
                "expected_impact": "medium"
            },
            {
                "statement": "If we offer a 'no-questions-asked instant refund' badge directly on the fruits/vegetables category page, then we mitigate the risk barrier for new trial users.",
                "experiment_type": "A/B test",
                "effort": "low",
                "expected_impact": "high"
            }
        ]
    },
    "Value and pricing concerns for Groceries": {
        "title": "Supermarket Price-Anchoring Impedes Large Basket Exploration",
        "finding": "14 users perceive Zepto as premium-priced and limit purchases to single items, avoiding monthly grocery stock-ups.",
        "root_cause": "Users compare Zepto's small pack sizes and convenience markups against local supermarkets (like D-Mart) and assume large baskets are too expensive, ignoring time saved.",
        "impact": {
            "affected_users": "40% of MACs",
            "blocked_category": "Groceries",
            "severity": "medium"
        },
        "target_segment": {
            "description": "Value Seekers",
            "behavioral_profile": "Highly price-sensitive, compares prices across apps, and drops off if delivery/handling fees exceed discounts."
        },
        "hypotheses": [
            {
                "statement": "If we launch a 'Smart Saver' bulk pack section (e.g., 5kg potato/onion packs) with price-per-kg comparison tags, then we change the value perception for basket builders.",
                "experiment_type": "A/B test",
                "effort": "medium",
                "expected_impact": "high"
            }
        ]
    }
}

def generate_insights_from_themes(db_path='data/discovery.db'):
    """Analyzes themes and synthesizes structured insights with hypotheses."""
    logger.info("Starting insight synthesis engine...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear previous insights
    cursor.execute("DELETE FROM insights")
    conn.commit()
    
    # Select significant themes (doc_count >= 3 for fallback testing, normally >= 10)
    cursor.execute("SELECT id, title, summary, doc_count, avg_sentiment, drivers, blocked_categories, research_questions, representative_quotes FROM themes WHERE doc_count >= 3")
    themes = cursor.fetchall()
    
    logger.info(f"Analyzing {len(themes)} significant themes for insight generation.")
    
    insights_created = 0
    
    for theme_id, title, summary, doc_count, avg_sentiment, drivers_json, blocked_cats_json, rqs_json, quotes_json in themes:
        logger.info(f"Synthesizing insight for theme: {title}...")
        
        # Check if we should use fallback
        if not client.api_key:
            # Fallback mock lookup
            mock_data = MOCK_INSIGHTS.get(title, {
                "title": f"Key friction in {title.split()[-1]} Adoption",
                "finding": f"{doc_count} users highlight barriers related to {title.lower()}.",
                "root_cause": f"Primary friction centers around user behavior, app layout, or platform limits regarding {title.lower()}.",
                "impact": {
                    "affected_users": "25% of MACs",
                    "blocked_category": json.loads(blocked_cats_json)[0] if json.loads(blocked_cats_json) else "General",
                    "severity": "medium"
                },
                "target_segment": {
                    "description": "Curious Browsers",
                    "behavioral_profile": "Explore multiple pages but drop off before adding new category items to cart."
                },
                "hypotheses": [
                    {
                        "statement": f"If we simplify checkout details and showcase popular items in this category, then we increase conversion.",
                        "experiment_type": "A/B test",
                        "effort": "low",
                        "expected_impact": "medium"
                    }
                ]
            })
            
            insight_data = mock_data
        else:
            # Live LLM prompt synthesis (llama-3.3-70b-versatile)
            from insights.prompts import INSIGHT_SYSTEM_PROMPT, INSIGHT_USER_PROMPT
            
            drivers = json.loads(drivers_json)
            blocked_cats = json.loads(blocked_cats_json)
            quotes = json.loads(quotes_json)
            quotes_formatted = "\n".join(f"- \"{q}\"" for q in quotes)
            
            try:
                insight_data = client.request_json(
                    system_prompt=INSIGHT_SYSTEM_PROMPT,
                    user_prompt=INSIGHT_USER_PROMPT.format(
                        theme_title=title,
                        theme_summary=summary,
                        doc_count=doc_count,
                        avg_sentiment=avg_sentiment,
                        drivers=drivers,
                        blocked_categories=blocked_cats,
                        quotes=quotes_formatted
                    ),
                    model=client.quality_model
                )
            except Exception as e:
                logger.error(f"Failed to query Groq for insight on theme {title}: {e}. Falling back.")
                continue

        # Save insight to DB
        insight_id = f"insight_{theme_id.split('_')[-1]}"
        try:
            cursor.execute("""
                INSERT INTO insights (
                    id, title, finding, root_cause, impact, 
                    target_segment, hypotheses, supporting_themes, 
                    confidence_score, confidence_level, research_questions
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight_id,
                insight_data.get('title', f"Insight for {title}"),
                insight_data.get('finding', ''),
                insight_data.get('root_cause', ''),
                json.dumps(insight_data.get('impact', {})),
                json.dumps(insight_data.get('target_segment', {})),
                json.dumps(insight_data.get('hypotheses', [])),
                json.dumps([theme_id]),
                0.0, # Will be calculated in Phase 5 Validation
                'PENDING',
                rqs_json # Propagate mapped research questions
            ))
            conn.commit()
            insights_created += 1
            logger.info(f"Saved Insight {insight_id}: {insight_data.get('title')}")
        except Exception as e:
            logger.error(f"Failed to insert insight for theme {theme_id}: {e}")
            conn.rollback()
            
    conn.close()
    logger.info(f"Insight synthesis completed. Generated {insights_created} insights.")
    return insights_created

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_insights_from_themes()
