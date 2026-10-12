import re
from typing import Dict, Any, List

NICHE_TAXONOMY = {
    "AI & Emerging Technology": {
        "keywords": ["ai", "artificial intelligence", "machine learning", "neural network", "chatgpt", "deep learning", "llm", "automation", "python", "software", "code", "agent", "robotics", "algorithm", "developer", "cloud"],
        "target_audience": "Tech professionals, developers, founders, and innovators",
        "platforms": "YouTube Shorts, TikTok, LinkedIn Video",
        "themes": ["Automation", "Future of Work", "Developer Productivity", "AI Tools"]
    },
    "Business & Entrepreneurship": {
        "keywords": ["business", "revenue", "startup", "founder", "sales", "customer", "product", "growth", "marketing", "scale", "profit", "company", "clients", "pricing", "b2b", "saas", "hiring"],
        "target_audience": "Entrepreneurs, agency owners, business leaders, and operators",
        "platforms": "LinkedIn Video, YouTube Shorts, Instagram Reels",
        "themes": ["Business Strategy", "Customer Acquisition", "Operational Scaling", "Bootstrapping"]
    },
    "Finance & Wealth Building": {
        "keywords": ["money", "investing", "wealth", "stock", "crypto", "cash flow", "passive income", "assets", "debt", "portfolio", "real estate", "interest", "dividends", "tax", "inflation"],
        "target_audience": "Investors, financial planners, and individuals seeking wealth building",
        "platforms": "YouTube Shorts, TikTok, Instagram Reels",
        "themes": ["Asset Allocation", "Cash Flow Management", "Long-term Compounding", "Market Trends"]
    },
    "Personal Growth & High Performance": {
        "keywords": ["discipline", "mindset", "habit", "focus", "goals", "productivity", "routine", "failure", "struggle", "motivation", "consistency", "psychology", "mental toughness", "energy"],
        "target_audience": "Self-driven individuals, students, creators, and professionals",
        "platforms": "Instagram Reels, TikTok, YouTube Shorts",
        "themes": ["Daily Habits", "Mental Resilience", "Deep Work", "Overcoming Procrastination"]
    },
    "Health, Fitness & Longevity": {
        "keywords": ["workout", "diet", "sleep", "muscle", "health", "nutrition", "training", "exercise", "fasting", "recovery", "cardio", "protein", "bodybuilding", "wellness", "metabolism"],
        "target_audience": "Fitness enthusiasts, athletes, and health-conscious individuals",
        "platforms": "TikTok, Instagram Reels, YouTube Shorts",
        "themes": ["Strength Training", "Nutrition Optimization", "Sleep Hygiene", "Longevity Protocols"]
    },
    "Education & Practical Tutorials": {
        "keywords": ["how to", "tutorial", "step by step", "guide", "learn", "lesson", "teach", "skill", "technique", "framework", "breakdown", "example", "principle", "fundamental"],
        "target_audience": "Lifelong learners, students, and practitioners",
        "platforms": "YouTube Shorts, LinkedIn Video",
        "themes": ["Skill Acquisition", "Actionable Frameworks", "Step-by-step Guides"]
    },
    "Commentary & Cultural Insights": {
        "keywords": ["interview", "podcast", "story", "truth", "happened", "experience", "society", "culture", "conversation", "opinion", "debate", "history", "perspective"],
        "target_audience": "Curious listeners, podcast fans, and general audience",
        "platforms": "TikTok, Instagram Reels, YouTube Shorts",
        "themes": ["Cultural Commentary", "Behind-the-Scenes Stories", "Contrarian Perspectives"]
    }
}

def analyze_content_niche(text: str, video_title: str = "") -> Dict[str, Any]:
    """
    Analyzes transcript text and title to detect primary niche, target audience,
    suitable short-form platforms, and key themes with evidence.
    """
    combined = f"{video_title} {text}".lower()
    scores = {}
    evidence_matches = {}

    for niche_name, data in NICHE_TAXONOMY.items():
        matched_words = []
        score = 0
        for kw in data["keywords"]:
            count = len(re.findall(r"\b" + re.escape(kw) + r"\b", combined))
            if count > 0:
                score += count
                matched_words.append(kw)
        scores[niche_name] = score
        evidence_matches[niche_name] = matched_words[:6]

    best_niche = max(scores, key=scores.get) if scores else "General Insight"
    best_score = scores.get(best_niche, 0)

    if best_score == 0:
        best_niche = "Education & Practical Tutorials"

    niche_info = NICHE_TAXONOMY.get(best_niche, NICHE_TAXONOMY["Education & Practical Tutorials"])
    
    # Calculate confidence based on evidence count
    confidence = min(0.95, max(0.55, 0.5 + (best_score * 0.03)))

    return {
        "primary_niche": best_niche,
        "confidence_score": round(confidence, 2),
        "target_audience": niche_info["target_audience"],
        "suitable_platforms": niche_info["platforms"],
        "key_themes": ", ".join(niche_info["themes"]),
        "evidence_keywords": evidence_matches.get(best_niche, []),
        "word_count": len(text.split())
    }
