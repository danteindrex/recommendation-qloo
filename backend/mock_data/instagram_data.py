"""
Mock Instagram data for testing cultural intelligence features
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock Instagram content categories with cultural significance
INSTAGRAM_CATEGORIES = {
    "food": {"cultural_weight": 0.9, "regions": ["global", "asia", "europe", "latin_america", "africa"]},
    "fashion": {"cultural_weight": 0.8, "regions": ["global", "europe", "asia", "north_america"]},
    "art": {"cultural_weight": 0.9, "regions": ["global", "europe", "asia", "africa"]},
    "travel": {"cultural_weight": 0.8, "regions": ["global", "europe", "asia", "oceania"]},
    "music": {"cultural_weight": 0.7, "regions": ["global", "north_america", "latin_america", "africa"]},
    "dance": {"cultural_weight": 0.9, "regions": ["global", "latin_america", "africa", "asia"]},
    "architecture": {"cultural_weight": 0.8, "regions": ["europe", "asia", "middle_east"]},
    "festivals": {"cultural_weight": 0.9, "regions": ["global", "asia", "europe", "latin_america"]},
    "language": {"cultural_weight": 0.9, "regions": ["global", "asia", "europe", "africa"]},
    "lifestyle": {"cultural_weight": 0.6, "regions": ["global", "north_america", "europe"]},
    "nature": {"cultural_weight": 0.5, "regions": ["global", "oceania", "africa", "asia"]},
    "sports": {"cultural_weight": 0.4, "regions": ["global", "north_america", "europe"]},
    "technology": {"cultural_weight": 0.3, "regions": ["global", "north_america", "asia"]},
    "wellness": {"cultural_weight": 0.6, "regions": ["global", "asia", "north_america"]},
    "crafts": {"cultural_weight": 0.8, "regions": ["global", "asia", "africa", "latin_america"]}
}

# Mock cultural hashtags
CULTURAL_HASHTAGS = {
    "food": ["#authenticcuisine", "#streetfood", "#traditionalrecipes", "#culturalcooking", "#localflavors"],
    "fashion": ["#traditionalwear", "#culturalstyle", "#ethnicfashion", "#heritageclothing", "#culturalbeauty"],
    "art": ["#culturalart", "#traditionalart", "#indigenousart", "#folkart", "#culturalheritage"],
    "travel": ["#culturaltravel", "#heritagetourism", "#localculture", "#culturalexperience", "#authentictravel"],
    "music": ["#worldmusic", "#traditionalmusic", "#culturalmusic", "#folkmusic", "#ethnicmusic"],
    "dance": ["#culturaldance", "#traditionaldance", "#folkdance", "#ethnicdance", "#culturalperformance"],
    "festivals": ["#culturalfestival", "#traditionalfestival", "#culturalcelebration", "#heritagefestival"],
    "language": ["#languagelearning", "#culturallanguage", "#nativelanguage", "#linguisticheritage"]
}

def generate_mock_instagram_profile(user_id: str) -> Dict[str, Any]:
    """Generate a comprehensive mock Instagram profile"""
    
    # Generate posts
    posts = []
    for i in range(50):  # 50 recent posts
        category = random.choice(list(INSTAGRAM_CATEGORIES.keys()))
        region = random.choice(INSTAGRAM_CATEGORIES[category]["regions"])
        
        post = {
            "post_id": f"ig_post_{user_id}_{i}",
            "type": random.choice(["photo", "video", "carousel", "reel", "story"]),
            "category": category,
            "region": region,
            "caption": generate_mock_caption(category),
            "hashtags": random.sample(CULTURAL_HASHTAGS.get(category, []), random.randint(2, 5)),
            "likes": random.randint(10, 1000),
            "comments": random.randint(0, 100),
            "shares": random.randint(0, 50),
            "saves": random.randint(0, 200),
            "posted_at": (datetime.now() - timedelta(days=random.randint(0, 90))).isoformat(),
            "cultural_weight": INSTAGRAM_CATEGORIES[category]["cultural_weight"],
            "engagement_rate": random.uniform(0.02, 0.15),
            "cultural_tags": generate_cultural_tags(category, region)
        }
        posts.append(post)
    
    # Generate following data
    following = generate_following_data(user_id)
    
    # Generate interaction data
    interactions = generate_interaction_data(user_id)
    
    # Calculate cultural metrics
    cultural_metrics = calculate_instagram_cultural_metrics(posts, following, interactions)
    
    return {
        "user_id": user_id,
        "platform": "instagram",
        "profile": {
            "username": f"user_{user_id}",
            "display_name": f"Cultural Explorer {user_id}",
            "bio": "Exploring cultures around the world 🌍",
            "followers": random.randint(100, 5000),
            "following": random.randint(200, 1000),
            "posts_count": len(posts),
            "verified": random.choice([True, False]),
            "private": random.choice([True, False])
        },
        "posts": posts,
        "following": following,
        "interactions": interactions,
        "cultural_metrics": cultural_metrics,
        "content_analysis": analyze_content_patterns(posts),
        "engagement_patterns": analyze_engagement_patterns(posts),
        "cultural_evolution": generate_instagram_cultural_evolution(posts),
        "last_updated": datetime.now().isoformat()
    }

def generate_mock_caption(category: str) -> str:
    """Generate mock captions based on category"""
    captions = {
        "food": [
            "Trying this amazing traditional dish! The flavors are incredible 🍜",
            "Homemade recipe passed down through generations ❤️",
            "Street food adventures continue! This is authentic culture 🌮",
            "Cooking class was amazing - learned so much about local cuisine 👨‍🍳"
        ],
        "fashion": [
            "Loving this traditional outfit! The craftsmanship is beautiful ✨",
            "Fashion week vibes with cultural inspiration 👗",
            "Vintage pieces tell such amazing stories 🧥",
            "Supporting local artisans and their incredible work 🎨"
        ],
        "art": [
            "This museum exhibition blew my mind! Such rich cultural history 🎨",
            "Local artist spotlight - the talent here is incredible 🖼️",
            "Traditional art techniques are so fascinating to learn about 🖌️",
            "Art has no boundaries - it speaks to the soul 💫"
        ],
        "travel": [
            "Every corner of this city tells a story 🏛️",
            "Cultural immersion at its finest! Learning so much 🗺️",
            "The architecture here is absolutely breathtaking 🏰",
            "Meeting locals and hearing their stories - priceless experiences 🤝"
        ]
    }
    
    return random.choice(captions.get(category, ["Amazing cultural experience! 🌟"]))

def generate_cultural_tags(category: str, region: str) -> List[str]:
    """Generate cultural tags based on category and region"""
    base_tags = {
        "food": ["cuisine", "recipe", "cooking", "flavors", "ingredients"],
        "fashion": ["style", "design", "clothing", "accessories", "trends"],
        "art": ["painting", "sculpture", "gallery", "exhibition", "artist"],
        "travel": ["destination", "culture", "history", "architecture", "local"]
    }
    
    region_tags = {
        "asia": ["asian", "eastern", "oriental", "traditional"],
        "europe": ["european", "western", "classical", "heritage"],
        "africa": ["african", "tribal", "indigenous", "ancestral"],
        "latin_america": ["latino", "hispanic", "colonial", "vibrant"],
        "north_america": ["american", "modern", "contemporary", "urban"],
        "middle_east": ["middle_eastern", "ancient", "historic", "cultural"],
        "oceania": ["pacific", "island", "coastal", "natural"]
    }
    
    tags = base_tags.get(category, ["cultural"])
    tags.extend(region_tags.get(region, ["global"]))
    
    return random.sample(tags, min(len(tags), 3))

def generate_following_data(user_id: str) -> List[Dict]:
    """Generate mock following data"""
    account_types = [
        {"type": "cultural_institution", "weight": 0.9},
        {"type": "artist", "weight": 0.8},
        {"type": "chef", "weight": 0.7},
        {"type": "travel_blogger", "weight": 0.6},
        {"type": "fashion_designer", "weight": 0.7},
        {"type": "musician", "weight": 0.6},
        {"type": "cultural_center", "weight": 0.9},
        {"type": "language_teacher", "weight": 0.8},
        {"type": "historian", "weight": 0.8},
        {"type": "lifestyle_influencer", "weight": 0.4}
    ]
    
    following = []
    for i in range(random.randint(50, 200)):
        account_type = random.choice(account_types)
        account = {
            "account_id": f"ig_account_{i}",
            "username": f"{account_type['type']}_{i}",
            "type": account_type["type"],
            "cultural_weight": account_type["weight"],
            "followers": random.randint(1000, 100000),
            "verified": random.choice([True, False]),
            "category": random.choice(list(INSTAGRAM_CATEGORIES.keys())),
            "region_focus": random.choice(["global", "asia", "europe", "africa", "latin_america"]),
            "followed_at": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
        }
        following.append(account)
    
    return following

def generate_interaction_data(user_id: str) -> List[Dict]:
    """Generate mock interaction data"""
    interactions = []
    interaction_types = ["like", "comment", "share", "save", "story_view", "story_reply"]
    
    for i in range(random.randint(100, 500)):
        interaction = {
            "interaction_id": f"ig_interaction_{user_id}_{i}",
            "type": random.choice(interaction_types),
            "target_account": f"account_{random.randint(1, 100)}",
            "content_category": random.choice(list(INSTAGRAM_CATEGORIES.keys())),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
            "cultural_relevance": random.uniform(0.1, 1.0),
            "engagement_depth": random.choice(["surface", "moderate", "deep"])
        }
        interactions.append(interaction)
    
    return interactions

def calculate_instagram_cultural_metrics(posts: List[Dict], following: List[Dict], interactions: List[Dict]) -> Dict[str, Any]:
    """Calculate cultural intelligence metrics from Instagram data"""
    
    # Content diversity
    categories = set(post["category"] for post in posts)
    regions = set(post["region"] for post in posts)
    content_diversity = len(categories) / len(INSTAGRAM_CATEGORIES)
    regional_diversity = len(regions) / 7  # 7 major regions
    
    # Cultural engagement
    cultural_posts = [p for p in posts if p["cultural_weight"] > 0.6]
    cultural_engagement = len(cultural_posts) / len(posts)
    
    # Following cultural relevance
    cultural_following = [f for f in following if f["cultural_weight"] > 0.6]
    following_cultural_ratio = len(cultural_following) / len(following)
    
    # Interaction cultural depth
    deep_interactions = [i for i in interactions if i["engagement_depth"] == "deep"]
    interaction_depth = len(deep_interactions) / len(interactions)
    
    return {
        "content_diversity": content_diversity,
        "regional_diversity": regional_diversity,
        "cultural_engagement": cultural_engagement,
        "following_cultural_ratio": following_cultural_ratio,
        "interaction_depth": interaction_depth,
        "overall_cultural_score": (content_diversity + regional_diversity + cultural_engagement + following_cultural_ratio + interaction_depth) / 5,
        "authenticity_score": random.uniform(0.6, 0.9),
        "exploration_tendency": random.uniform(0.4, 0.8),
        "cultural_influence": random.uniform(0.2, 0.7)
    }

def analyze_content_patterns(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze content posting patterns"""
    category_distribution = {}
    for post in posts:
        category = post["category"]
        category_distribution[category] = category_distribution.get(category, 0) + 1
    
    # Normalize
    total_posts = len(posts)
    category_distribution = {k: v/total_posts for k, v in category_distribution.items()}
    
    return {
        "category_distribution": category_distribution,
        "posting_frequency": calculate_posting_frequency(posts),
        "engagement_trends": calculate_engagement_trends(posts),
        "content_evolution": analyze_content_evolution(posts)
    }

def calculate_posting_frequency(posts: List[Dict]) -> Dict[str, float]:
    """Calculate posting frequency patterns"""
    # Group posts by day of week
    day_counts = {}
    for post in posts:
        post_date = datetime.fromisoformat(post["posted_at"])
        day = post_date.strftime("%A")
        day_counts[day] = day_counts.get(day, 0) + 1
    
    total_posts = len(posts)
    return {day: count/total_posts for day, count in day_counts.items()}

def calculate_engagement_trends(posts: List[Dict]) -> Dict[str, float]:
    """Calculate engagement trends"""
    if not posts:
        return {}
    
    avg_likes = sum(post["likes"] for post in posts) / len(posts)
    avg_comments = sum(post["comments"] for post in posts) / len(posts)
    avg_saves = sum(post["saves"] for post in posts) / len(posts)
    
    return {
        "average_likes": avg_likes,
        "average_comments": avg_comments,
        "average_saves": avg_saves,
        "engagement_rate": sum(post["engagement_rate"] for post in posts) / len(posts)
    }

def analyze_content_evolution(posts: List[Dict]) -> List[Dict]:
    """Analyze how content has evolved over time"""
    # Sort posts by date
    sorted_posts = sorted(posts, key=lambda x: x["posted_at"])
    
    # Group by month
    monthly_data = {}
    for post in sorted_posts:
        post_date = datetime.fromisoformat(post["posted_at"])
        month_key = post_date.strftime("%Y-%m")
        
        if month_key not in monthly_data:
            monthly_data[month_key] = {"posts": [], "categories": set()}
        
        monthly_data[month_key]["posts"].append(post)
        monthly_data[month_key]["categories"].add(post["category"])
    
    evolution = []
    for month, data in sorted(monthly_data.items()):
        evolution.append({
            "month": month,
            "post_count": len(data["posts"]),
            "category_diversity": len(data["categories"]),
            "avg_cultural_weight": sum(p["cultural_weight"] for p in data["posts"]) / len(data["posts"]),
            "dominant_category": max(set(p["category"] for p in data["posts"]), 
                                   key=lambda x: sum(1 for p in data["posts"] if p["category"] == x))
        })
    
    return evolution

def analyze_engagement_patterns(posts: List[Dict]) -> Dict[str, Any]:
    """Analyze engagement patterns"""
    # Engagement by category
    category_engagement = {}
    for post in posts:
        category = post["category"]
        if category not in category_engagement:
            category_engagement[category] = {"total_engagement": 0, "post_count": 0}
        
        total_engagement = post["likes"] + post["comments"] + post["saves"]
        category_engagement[category]["total_engagement"] += total_engagement
        category_engagement[category]["post_count"] += 1
    
    # Calculate average engagement per category
    avg_engagement_by_category = {}
    for category, data in category_engagement.items():
        avg_engagement_by_category[category] = data["total_engagement"] / data["post_count"]
    
    return {
        "engagement_by_category": avg_engagement_by_category,
        "best_performing_category": max(avg_engagement_by_category.items(), key=lambda x: x[1])[0],
        "engagement_consistency": calculate_engagement_consistency(posts),
        "viral_potential": calculate_viral_potential(posts)
    }

def calculate_engagement_consistency(posts: List[Dict]) -> float:
    """Calculate how consistent engagement is across posts"""
    engagement_rates = [post["engagement_rate"] for post in posts]
    if not engagement_rates:
        return 0.0
    
    mean_rate = sum(engagement_rates) / len(engagement_rates)
    variance = sum((rate - mean_rate) ** 2 for rate in engagement_rates) / len(engagement_rates)
    
    # Lower variance = higher consistency
    return max(0, 1 - (variance / mean_rate if mean_rate > 0 else 1))

def calculate_viral_potential(posts: List[Dict]) -> float:
    """Calculate viral potential based on share/save ratios"""
    if not posts:
        return 0.0
    
    viral_scores = []
    for post in posts:
        likes = post["likes"]
        shares = post["shares"]
        saves = post["saves"]
        
        if likes > 0:
            viral_score = (shares + saves) / likes
            viral_scores.append(min(viral_score, 1.0))  # Cap at 1.0
    
    return sum(viral_scores) / len(viral_scores) if viral_scores else 0.0

def generate_instagram_cultural_evolution(posts: List[Dict]) -> List[Dict]:
    """Generate cultural evolution timeline for Instagram"""
    # Sort posts by date
    sorted_posts = sorted(posts, key=lambda x: x["posted_at"])
    
    # Group by weeks
    weekly_data = {}
    for post in sorted_posts:
        post_date = datetime.fromisoformat(post["posted_at"])
        week_start = post_date - timedelta(days=post_date.weekday())
        week_key = week_start.strftime("%Y-W%U")
        
        if week_key not in weekly_data:
            weekly_data[week_key] = {"posts": [], "categories": {}, "regions": {}}
        
        weekly_data[week_key]["posts"].append(post)
        
        category = post["category"]
        region = post["region"]
        weekly_data[week_key]["categories"][category] = weekly_data[week_key]["categories"].get(category, 0) + 1
        weekly_data[week_key]["regions"][region] = weekly_data[week_key]["regions"].get(region, 0) + 1
    
    evolution = []
    for week, data in sorted(weekly_data.items())[-12:]:  # Last 12 weeks
        if data["posts"]:
            evolution.append({
                "week": week,
                "post_count": len(data["posts"]),
                "dominant_category": max(data["categories"].items(), key=lambda x: x[1])[0] if data["categories"] else None,
                "dominant_region": max(data["regions"].items(), key=lambda x: x[1])[0] if data["regions"] else None,
                "cultural_diversity": len(data["categories"]) / len(INSTAGRAM_CATEGORIES),
                "regional_diversity": len(data["regions"]) / 7,
                "avg_engagement": sum(p["likes"] + p["comments"] + p["saves"] for p in data["posts"]) / len(data["posts"]),
                "cultural_weight": sum(p["cultural_weight"] for p in data["posts"]) / len(data["posts"])
            })
    
    return evolution

# Mock data for testing
MOCK_USERS = ["user_1", "user_2", "user_3", "user_4", "user_5"]

def get_all_mock_instagram_data() -> Dict[str, Any]:
    """Get all mock Instagram data for testing"""
    return {
        user_id: generate_mock_instagram_profile(user_id)
        for user_id in MOCK_USERS
    }

if __name__ == "__main__":
    # Test the mock data generation
    test_data = generate_mock_instagram_profile("test_user")
    print("Mock Instagram Profile Generated:")
    print(f"Posts: {len(test_data['posts'])}")
    print(f"Following: {len(test_data['following'])}")
    print(f"Cultural Score: {test_data['cultural_metrics']['overall_cultural_score']:.2f}")
    print(f"Content Diversity: {test_data['cultural_metrics']['content_diversity']:.2f}")