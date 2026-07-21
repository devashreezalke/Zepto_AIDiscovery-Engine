import sys
import logging
from scrapers.ingest import run_ingestion
from analysis.analyzer import run_analysis_pipeline
from clustering.label_themes import generate_and_save_themes
from insights.synthesize import generate_insights_from_themes
from insights.validate import run_validation

# Configure execution logging
handlers = [logging.StreamHandler(sys.stdout)]
try:
    handlers.append(logging.FileHandler('pipeline_run.log', encoding='utf-8'))
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

def run_full_pipeline():
    """Orchestrates and executes all 5 stages of the Zepto AI Discovery Engine pipeline."""
    logger.info("=================================================================")
    logger.info("    ZEPTO AI-POWERED DISCOVERY ENGINE PIPELINE EXECUTION START    ")
    logger.info("=================================================================")
    
    # Step 0: DB Schema Initialization
    logger.info("--- [STAGE 0] Initializing Database Schema ---")
    try:
        from data.db_init import init_db
        init_db()
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 0 (DB Init): {e}")
        raise RuntimeError(f"Stage 0 failed: {e}") from e

    # Step 1: Ingestion
    logger.info("--- [STAGE 1] Running Data Ingestion Scrapers ---")
    try:
        inserted = run_ingestion()
        logger.info(f"Stage 1 Complete. Ingested data corpus records.")
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 1 (Ingestion): {e}")
        raise RuntimeError(f"Stage 1 failed: {e}") from e
        
    # Step 2: AI Analysis
    logger.info("--- [STAGE 2] Running AI Sentiment & Driver Analysis ---")
    try:
        analyzed = run_analysis_pipeline()
        logger.info("Stage 2 Complete. Document enrichment stored.")
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 2 (Analysis): {e}")
        raise RuntimeError(f"Stage 2 failed: {e}") from e
        
    # Step 3: Semantic Clustering
    logger.info("--- [STAGE 3] Running DBSCAN Clustering & Theme Labeling ---")
    try:
        themes = generate_and_save_themes()
        logger.info(f"Stage 3 Complete. Generated {themes} semantic theme clusters.")
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 3 (Clustering): {e}")
        raise RuntimeError(f"Stage 3 failed: {e}") from e
        
    # Step 4: Growth Insight Synthesis
    logger.info("--- [STAGE 4] Running Insight & Hypothesis Synthesis ---")
    try:
        insights = generate_insights_from_themes()
        logger.info(f"Stage 4 Complete. Formulated {insights} growth insights.")
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 4 (Insights): {e}")
        raise RuntimeError(f"Stage 4 failed: {e}") from e
        
    # Step 5: Confidence Gate Validation & Scoring
    logger.info("--- [STAGE 5] Running Validation Gates & Exporting Data ---")
    try:
        validated = run_validation()
        logger.info(f"Stage 5 Complete. Validated {validated} insights and updated JSON export.")
    except Exception as e:
        logger.error(f"Pipeline failed at Stage 5 (Validation): {e}")
        raise RuntimeError(f"Stage 5 failed: {e}") from e
        
    logger.info("=================================================================")
    logger.info("      ZEPTO AI-POWERED DISCOVERY ENGINE PIPELINE COMPLETED      ")
    logger.info("=================================================================")
    logger.info("Run the Next.js app to browse findings: npm run dev (in /dashboard)")

if __name__ == '__main__':
    try:
        run_full_pipeline()
    except Exception as e:
        sys.exit(1)
