# Detailed synthesized research mapping for dashboard export

RESEARCH_QUESTION_ANSWERS = {
    "Q1_habit_formation": {
        "finding": "Users purchase same categories repeatedly due to habitual checkout loops. Session times for routine grocery checkouts average under 120 seconds, with users directly bypassing catalog navigation pages.",
        "root_cause": "Buying fresh items is an automatic cognitive habit. Users open the app with a specific list in mind and do not treat quick-commerce as a browsing destination, rendering unsearched categories invisible.",
        "quotes": [
            "I order the exact same grocery list twice a week. I open the app, search for milk and eggs, click buy, and close it. I have never clicked on the electronics or home decor tabs because it's simply not what I think of when I think of Zepto."
        ],
        "hypothesis": {
            "statement": "If we inject contextual category cross-sells at cart checkout for staples (e.g. recommend limes/cilies when onion/tomatoes are added), then we break the default loop and increase category entry by 18%.",
            "type": "A/B test",
            "effort": "low",
            "impact": "medium"
        }
    },
    "Q2_discovery_barriers": {
        "finding": "Exploring new categories is blocked by picking quality skepticism, perceived pricing markups on bulk carts, and return anxiety on higher-value products.",
        "root_cause": "Users assume that pickers select sub-standard fresh produce or personal care items, and fear that returns/replacements for wrong sizes or broken electronics will be rejected by customer service bots.",
        "quotes": [
            "Company are frauds and delivery boy also fraud... missing items and they refuse to refund. The chatbot straight away rejects your queries. How can I buy a mouse or a charger here? If it arrives broken, I am stuck with no help!",
            "They charge convenience surge fees, handling fees even when opting for no bag, and rain fees when it is only cloudy. This is making grocery shopping too expensive. I will only buy single emergency items."
        ],
        "hypothesis": {
            "statement": "If we introduce a prominent, 'No-Questions-Asked Instant Refund' badge on category pages for baby care and electronics, then we lower the risk barrier and lift conversion by 22%.",
            "type": "A/B test",
            "effort": "low",
            "impact": "high"
        }
    },
    "Q3_discovery_mechanisms": {
        "finding": "Product discovery is almost entirely search-driven or contextual emergency-driven. Static banners and category carousels have click-through rates (CTR) below 1.5%.",
        "root_cause": "Users search directly for immediate needs. If the autocomplete indexing or search filters fail to display relevant products, the user leaves the app instead of browsing adjacent categories.",
        "quotes": [
            "I wanted to try a new cold brew brand. I searched for it but search just showed basic instant coffee. It was too hard to browse options so I closed the app and ordered from Amazon."
        ],
        "hypothesis": {
            "statement": "If we display category-switching suggestions on the search results page (e.g., if a user searches 'diapers', show wipes/lotions), then we redirect search intent and lift category entry by 10%.",
            "type": "A/B test",
            "effort": "medium",
            "impact": "medium"
        }
    },
    "Q4_role_of_habits": {
        "finding": "Shopping habits establish rigid cognitive lock-ins. Users have partitioned apps for routines: Zepto for emergency milk, Nykaa for cosmetics, D-Mart for monthly groceries.",
        "root_cause": "Routine habits require low cognitive load. Breaking these loops to try a new category on Zepto requires a strong incentive to counteract established routine convenience on competitor platforms.",
        "quotes": [
            "Zepto is super fast for milk and eggs, but for my monthly groceries, I go to D-Mart. For shampoo and moisturizer, I order on Nykaa out of habit. Changing this feels like too much work."
        ],
        "hypothesis": {
            "statement": "If we bundle non-grocery discount coupons directly inside the 'Zepto Pass' weekly checkout email, then we leverage the existing loyalty loop and lift trial category purchases by 14%.",
            "type": "pre-post",
            "effort": "medium",
            "impact": "high"
        }
    },
    "Q5_information_needs": {
        "finding": "Users require active social proof, star ratings, and detailed sizing grids before they are willing to try a new category or unknown brand.",
        "root_cause": "Without reviews or sizing grids, users cannot gauge quality, fit, or taste, and fallback to offline shopping or other apps that provide this context.",
        "quotes": [
            "Switched from Zepto to Blinkit because Zepto does not show reviews for products. How can I buy a new brand of snacks or biscuits without seeing what others think? At least Blinkit shows star ratings.",
            "Diaper sizing is missing on the product detail page. Ordered wrong size twice. Now I have to go through unhelpful support. Please add clear weight charts."
        ],
        "hypothesis": {
            "statement": "If we integrate crowdsourced customer star ratings and review snippets on all non-grocery PDPs, then we resolve the information gap and increase conversion by 25%.",
            "type": "A/B test",
            "effort": "medium",
            "impact": "high"
        }
    },
    "Q6_pain_points": {
        "finding": "Repeated customer support failures on rotten produce or missing items, combined with opaque billing fees (surge, rain fees), create severe platform friction.",
        "root_cause": "The support bot uses rigid scripts that reject refund/return requests, making customers feel cheated and highly hesitant to purchase anything beyond basic low-cost staples.",
        "quotes": [
            "The chatbot straight away rejects your queries... I have Zepto Pass and this is how they treat customers. Putting up a complaint in consumer forum, see u in court.",
            "They completely missed items from my order and charged me for it. Support team claimed it was 'delivered' without doing actual verification. Complete fraud."
        ],
        "hypothesis": {
            "statement": "If we automatically credit a validation voucher if picked produce is reported below quality score (bypassing CS bots), then we salvage trust and lift retention by 40% after poor delivery events.",
            "type": "A/B test",
            "effort": "low",
            "impact": "high"
        }
    },
    "Q7_user_segments": {
        "finding": "The 'Curious Browsers' (25% of MACs) and 'Life-Stage Movers' (15% of MACs) cohorts show the highest statistical willingness to explore new categories.",
        "root_cause": "Browsers are already exploring PDPs but drop off at checkout. Life-Stage Movers want clean baby/pet products and will convert immediately if quality and brand authenticity are verified.",
        "quotes": [
            "I saw a diaper pack for my nephew on Zepto, but they delivered the wrong size. Customer care refunded instantly but now I have to order again. Still no size selection on diaper brand category page."
        ],
        "hypothesis": {
            "statement": "If we target the 'Curious Browser' cohort with location-based real-time purchase banners (e.g. '12 people in your neighborhood bought this moisturizer today'), then we convert browser inertia and lift checkout by 30%.",
            "type": "A/B test",
            "effort": "medium",
            "impact": "medium"
        }
    },
    "Q8_unmet_needs": {
        "finding": "A lack of organic premium brands (e.g. baby wash, premium pet food) and missing spec details for electronics consistently drive users away to alternative platforms.",
        "root_cause": "Zepto stocks generic private labels which parents do not trust for their children/pets, and fails to list basic electronic specifications (watts, cable length) or return policies.",
        "quotes": [
            "For baby diapers and baby soaps, I only buy Pampers and Sebamed. On Zepto, they only have local brands or private labels in stock. I don't trust private labels for baby skin. I'd rather buy from FirstCry.",
            "I saw a keyboard and mouse but too scared to order. If it's defective, how do I return? I'll buy from Amazon instead even if it takes 1 day."
        ],
        "hypothesis": {
            "statement": "If we introduce a '100% Brand Certified' badge on premium categories with a 24h return assurance, then we neutralize trust barriers and increase sales by 15%.",
            "type": "A/B test",
            "effort": "low",
            "impact": "high"
        }
    }
}
