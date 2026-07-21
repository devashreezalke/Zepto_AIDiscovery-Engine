import logging

logger = logging.getLogger(__name__)

def get_user_segments():
    """Returns the 5 archetypal user segments for Zepto category discovery."""
    logger.info("Generating user segment profiles...")
    return [
        {
            "id": "segment_curious_browsers",
            "name": "Curious Browsers",
            "description": "Users who explore multiple categories and view product detail pages but rarely add non-grocery items to their carts.",
            "estimated_size": "25% of MACs",
            "cross_category_potential": "Very High",
            "behavioral_profile": "High search query variance, views categories via sidebar, long session times, but high cart drop-off for premium/electronics items.",
            "recommended_intervention": "Introduce category entry coupons, show real-time purchase triggers (e.g. '12 people in Bangalore bought this keyboard in the last hour')."
        },
        {
            "id": "segment_habitual_minimalists",
            "name": "Habitual Minimalists",
            "description": "Staple-only buyers who order a narrow list of items (e.g., milk, eggs, bread) and checkout instantly out of routine.",
            "estimated_size": "30% of MACs",
            "cross_category_potential": "Low",
            "behavioral_profile": "Very short session durations (< 2 mins), uses order history or search bar for exact item matches, ignores banners.",
            "recommended_intervention": "Inject cross-sell options directly at cart checkout based on staple matches (e.g., add lemons if onions and tomatoes are in cart)."
        },
        {
            "id": "segment_value_seekers",
            "name": "Value Seekers",
            "description": "Users who purchase heavily discounted or bundle deal items across categories, comparing prices against other quick commerce apps.",
            "estimated_size": "20% of MACs",
            "cross_category_potential": "Medium",
            "behavioral_profile": "Always clicks 'Offers' tab, builds large baskets to waive delivery fees, highly sensitive to handling charges.",
            "recommended_intervention": "Promote bulk-buy value packs and category cross-buy rewards (e.g. 'Buy Groceries, get 15% off Personal Care')."
        },
        {
            "id": "segment_life_stage_movers",
            "name": "Life-Stage Movers",
            "description": "Families and parents who purchase premium child care, pet care, or clean organic groceries.",
            "estimated_size": "15% of MACs",
            "cross_category_potential": "High",
            "behavioral_profile": "Purchases premium items, reads product labels and ingredient lists, shows lower price sensitivity if quality is assured.",
            "recommended_intervention": "Show third-party organic certificates, detail ingredient origins, and display customer ratings and diapers/formula sizing sheets."
        },
        {
            "id": "segment_loyalists",
            "name": "Platform Loyalists",
            "description": "Power users who already purchase from 3+ categories monthly and trust the brand for general deliveries.",
            "estimated_size": "10% of MACs",
            "cross_category_potential": "Medium",
            "behavioral_profile": "Highest purchase frequency (> 10 orders/month), uses Zepto Pass, low customer care issues, high average basket sizes.",
            "recommended_intervention": "Offer VIP early-access to new category launches (e.g., books, premium apparel, or electronics)."
        }
    ]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    segments = get_user_segments()
    print(f"Generated {len(segments)} segments.")
