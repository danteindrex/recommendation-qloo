"""
Mock TikTok data for testing cultural intelligence features
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock TikTok content categories with cultural significance
TIKTOK_CATEGORIES = {
    "dance": {"cultural_weight": 0.9, "viral_potential": 0.8, "regions": ["global", "latin_america", "africa", "asia"]},
    "comedy": {"cultural_weight": 0.6, "viral_potential": 0.9, "regions": ["global", "north_america", "europe"]},
    "food": {"cultural_weight": 0.9, "viral_potential": 0.7, "regions": ["global", "asia", "latin_america", "africa"]},
    "fashion": {"cultural_weight": 0.8, "viral_potential": 0.6, "regions": ["global", "europe", "asia", "north_america"]},
    "music": {"cultural_weight": 0.8, "viral_potential": 0.8, "regions": ["global", "north_america", "latin_america", "africa"]},
    "education": {"cultural_weight": 0.7, "viral_potential": 0.5, "regions": ["global", "asia", "europe", "north_america"]},
    "lifestyle": {"cultural_weight": 0.5, "viral_potential": 0.6, "regions": ["global", "north_america", "europe"]},
    "travel": {"cultural_weight": 0.8, "viral_potential": 0.7, "regions": ["global", "europe", "asia", "oceania"]},
    "art": {"cultural_weight": 0.9, "viral_potential": 0.6, "regions": ["global", "europe", "asia", "africa"]},
    "language": {"cultural_weight": 0.9, "viral_potential": 0.5, "regions": ["global", "asia", "europe", "africa"]},
    "sports": {"cultural_weight": 0.4, "viral_potential": 0.7, "regions": ["global", "north_america", "europe"]},
    "beauty": {"cultural_weight": 0.6, "viral_potential": 0.7, "regions": ["global", "asia", "north_america", "europe"]},
    "pets": {"cultural_weight": 0.3, "viral_potential": 0.8, "regions": ["global", "north_america", "europe"]},
    "diy": {"cultural_weight": 0.6, "viral_potential": 0.6, "regions": ["global", "north_america", "europe", "asia"]},
    "gaming": {"cultural_weight": 0.4, "viral_potential": 0.7, "regions": ["global", "north_america", "asia", "europe"]}
}

# Mock trending sounds and their cultural origins
TRENDING_SOUNDS = [
    {"sound_id": "sound_1", "name": "Afrobeats Remix", "origin": "africa", "cultural_weight": 0.9, "usage_count": 50000},
    {"sound_id": "sound_2", "name": "K-Pop Dance Beat", "origin": "asia", "cultural_weight": 0.9, "usage_count": 80000},
    {"sound_id": "sound_3", "name": "Latin Reggaeton", "origin": "latin_america", "cultural_weight": 0.9, "usage_count": 60000},
    {"sound_id": "sound_4", "name": "Bollywood Fusion", "origin": "asia", "cultural_weight": 0.9, "usage_count": 40000},
    {"sound_id": "sound_5", "name": "Electronic Pop", "origin": "europe", "cultural_weight": 0.6, "usage_count": 70000},
    {"sound_id": "sound_6", "name": "Hip Hop Beat", "origin": "north_america", "cultural_weight": 0.7, "usage_count": 90000},
    {"sound_id": "sound_7", "name": "Traditional Folk", "origin": "global", "cultural_weight": 0.8, "usage_count": 20000},
    {"sound_id": "sound_8", "name": "Jazz Instrumental", "origin": "north_america", "cultural_weight": 0.8, "usage_count": 15000},
    {"sound_id": "sound_9", "name": "Flamenco Guitar", "origin": "europe", "cultural_weight": 0.9, "usage_count": 25000},
    {"sound_id": "sound_10", "name": "Ambient World", "origin": "global", "cultural_weight": 0.7, "usage_count": 30000}
]

# Mock hashtag trends with cultural significance
CULTURAL_HASHTAGS = {
    "dance": ["#culturaldance", "#traditionaldance", "#dancechallenge", "#worlddance", "#ethnicdance"],
    "food": ["#culturalcooking", "#traditionalfood", "#worldcuisine", "#authenticrecipes", "#streetfood"],
    "fashion": ["#culturalstyle", "#traditionalwear", "#ethnicfashion", "#heritagestyle", "#worldfashion"],
    "music": ["#worldmusic", "#culturalmusic", "#traditionalmusic", "#ethnicbeats", "#globalrhythms"],
    "art": ["#culturalart", "#traditionalart", "#worldart", "#ethnicart", "#heritageart"],
    "language": ["#languagelearning", "#culturallanguage", "#worldlanguages", "#polyglot", "#linguistics"],
    "travel": ["#culturaltravel", "#worldtravel", "#culturalexperience", "#localculture", "#heritagetourism"]
}

def generate_mock_tiktok_profile(user_id: str) -> Dict[str, Any]:
    """Generate a comprehensive mock TikTok profile"""
    
    # Generate videos
    videos = []
    for i in range(30):  # 30 recent videos
        category = random.choice(list(TIKTOK_CATEGORIES.keys()))
        sound = random.choice(TRENDING_SOUNDS)
        region = random.choice(TIKTOK_CATEGORIES[category]["regions"])
        
        video = {
            "video_id": f"tiktok_video_{user_id}_{i}",
            "category": category,
            "region": region,
            "sound": sound,
            "duration": random.randint(15, 180),  # 15 seconds to 3 minutes
            "description": generate_mock_description(category),
            "hashtags": random.sample(CULTURAL_HASHTAGS.get(category, []), random.randint(2, 4)),
            "views": random.randint(100, 100000),
            "likes": random.randint(10, 10000),
            "comments": random.randint(0, 1000),
            "shares": random.randint(0, 500),
            "saves": random.randint(0, 200),
            "posted_at": (datetime.now() - timedelta(days=random.randint(0, 60))).isoformat(),
            "cultural_weight": TIKTOK_CATEGORIES[category]["cultural_weight"],
            "viral_score": calculate_viral_score(random.randint(100, 100000), random.randint(10, 10000), random.randint(0, 500)),
            "engagement_rate": random.uniform(0.05, 0.25),
            "cultural_authenticity": random.uniform(0.6, 1.0),
            "trend_participation": random.choice([True, False])
        }
        videos.append(video)
    
    # Generate following data
    following = generate_tiktok_following_data(user_id)
    
    # Generate interaction data
    interactions = generate_tiktok_interaction_data(user_id)
    
    # Calculate cultural metrics
    cultural_metrics = calculate_tiktok_cultural_metrics(videos, following, interactions)
    
    return {
        "user_id": user_id,
        "platform": "tiktok",
        "profile": {
            "username": f"@culturalexplorer{user_id}",
            "display_name": f"Cultural Explorer {user_id}",
            "bio": "Sharing cultures from around the world 🌍✨",
            "followers": random.randint(500, 50000),
            "following": random.randint(100, 2000),
            "likes_received": random.randint(1000, 100000),
            "videos_count": len(videos),
            "verified": random.choice([True, False]),
            "private": random.choice([True, False])
        },
        "videos": videos,
        "following": following,
        "interactions": interactions,
        "cultural_metrics": cultural_metrics,
        "trend_analysis": analyze_trend_participation(videos),
        "sound_preferences": analyze_sound_preferences(videos),
        "cultural_evolution": generate_tiktok_cultural_evolution(videos),
        "viral_content": identify_viral_content(videos),
        "last_updated": datetime.now().isoformat()
    }

def generate_mock_description(category: str) -> str:
    """Generate mock video descriptions based on category"""
    descriptions = {
        "dance": [
            "Learning this traditional dance from my grandmother! 💃 #culture",
            "Dance challenge with a cultural twist! Who's joining? 🕺",
            "This dance tells a beautiful story from our heritage ✨",
            "Fusion of traditional and modern moves! What do you think? 🔥"
        ],
        "food": [
            "Making my family's secret recipe! Passed down for generations 🍜",
            "Street food adventure! This is how we do it in my culture 🌮",
            "Cooking with love and tradition ❤️ Recipe in comments!",
            "Food is culture! Sharing my favorite childhood dish 🥘"
        ],
        "fashion": [
            "Traditional outfit for today's celebration! Feeling proud 👗",
            "Modern twist on cultural fashion! Love this fusion style ✨",
            "Handmade by local artisans! Supporting our community 🧵",
            "Fashion tells our story! What's your cultural style? 👘"
        ],
        "music": [
            "This song reminds me of home! Music connects us all 🎵",
            "Traditional instruments meet modern beats! 🎶",
            "Singing in my native language! Music has no borders 🎤",
            "Cultural fusion at its finest! What's your favorite world music? 🌍"
        ],
        "art": [
            "Traditional art technique passed down through generations 🎨",
            "Art is universal language! Creating cultural bridges 🖼️",
            "Local artist spotlight! Supporting cultural creativity ✨",
            "Every brushstroke tells our story 🖌️"
        ]
    }
    
    return random.choice(descriptions.get(category, ["Sharing culture with the world! 🌍"]))

def calculate_viral_score(views: int, likes: int, shares: int) -> float:
    """Calculate viral score based on engagement metrics"""
    if views == 0:
        return 0.0
    
    like_rate = likes / views
    share_rate = shares / views
    
    # Viral score combines like rate and share rate with share rate weighted higher
    viral_score = (like_rate * 0.3) + (share_rate * 0.7)
    
    return min(viral_score * 10, 1.0)  # Normalize to 0-1 scale

def generate_tiktok_following_data(user_id: str) -> List[Dict]:
    """Generate mock TikTok following data"""
    creator_types = [
        {"type": "cultural_educator", "weight": 0.9},
        {"type": "dance_creator", "weight": 0.8},
        {"type": "food_creator", "weight": 0.8},
        {"type": "travel_creator", "weight": 0.7},
        {"type": "language_teacher", "weight": 0.9},
        {"type": "fashion_creator", "weight": 0.6},
        {"type": "music_artist", "weight": 0.7},
        {"type": "comedy_creator", "weight": 0.4},
        {"type": "lifestyle_creator", "weight": 0.3},
        {"type": "art_creator", "weight": 0.8}
    ]
    
    following = []
    for i in range(random.randint(50, 200)):
        creator_type = random.choice(creator_types)
        creator = {
            "creator_id": f"tiktok_creator_{i}",
            "username": f"@{creator_type['type']}_{i}",
            "type": creator_type["type"],
            "cultural_weight": creator_type["weight"],
            "followers": random.randint(1000, 1000000),
            "verified": random.choice([True, False]),
            "primary_category": random.choice(list(TIKTOK_CATEGORIES.keys())),
            "region_focus": random.choice(["global", "asia", "europe", "africa", "latin_america", "north_america"]),
            "followed_at": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat(),
            "engagement_with_user": random.uniform(0.0, 0.8)
        }
        following.append(creator)
    
    return following

def generate_tiktok_interaction_data(user_id: str) -> List[Dict]:
    """Generate mock TikTok interaction data"""
    interactions = []
    interaction_types = ["like", "comment", "share", "save", "duet", "stitch", "follow"]
    
    for i in range(random.randint(200, 800)):
        interaction = {
            "interaction_id": f"tiktok_interaction_{user_id}_{i}",
            "type": random.choice(interaction_types),
            "target_creator": f"creator_{random.randint(1, 100)}",
            "video_category": random.choice(list(TIKTOK_CATEGORIES.keys())),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
            "cultural_relevance": random.uniform(0.1, 1.0),
            "engagement_depth": random.choice(["surface", "moderate", "deep"]),
            "trend_related": random.choice([True, False]),
            "sound_used": random.choice(TRENDING_SOUNDS)["sound_id"] if random.choice([True, False]) else None
        }
        interactions.append(interaction)
    
    return interactions

def calculate_tiktok_cultural_metrics(videos: List[Dict], following: List[Dict], interactions: List[Dict]) -> Dict[str, Any]:
    """Calculate cultural intelligence metrics from TikTok data"""
    
    # Content diversity
    categories = set(video["category"] for video in videos)
    regions = set(video["region"] for video in videos)
    content_diversity = len(categories) / len(TIKTOK_CATEGORIES)
    regional_diversity = len(regions) / 6  # 6 major regions
    
    # Cultural authenticity
    authentic_videos = [v for v in videos if v["cultural_authenticity"] > 0.7]
    authenticity_ratio = len(authentic_videos) / len(videos) if videos else 0
    
    # Trend participation vs cultural content
    trend_videos = [v for v in videos if v["trend_participation"]]
    cultural_videos = [v for v in videos if v["cultural_weight"] > 0.7]
    
    trend_ratio = len(trend_videos) / len(videos) if videos else 0
    cultural_ratio = len(cultural_videos) / len(videos) if videos else 0
    
    # Following cultural relevance
    cultural_following = [f for f in following if f["cultural_weight"] > 0.6]
    following_cultural_ratio = len(cultural_following) / len(following) if following else 0
    
    # Sound diversity (cultural origins)
    sound_origins = set(video["sound"]["origin"] for video in videos)
    sound_diversity = len(sound_origins) / 6  # 6 major regions
    
    # Viral cultural content
    viral_cultural_videos = [v for v in videos if v["viral_score"] > 0.6 and v["cultural_weight"] > 0.7]
    viral_cultural_ratio = len(viral_cultural_videos) / len(videos) if videos else 0
    
    return {
        "content_diversity": content_diversity,
        "regional_diversity": regional_diversity,
        "authenticity_ratio": authenticity_ratio,
        "trend_participation": trend_ratio,
        "cultural_content_ratio": cultural_ratio,
        "following_cultural_ratio": following_cultural_ratio,
        "sound_diversity": sound_diversity,
        "viral_cultural_ratio": viral_cultural_ratio,
        "overall_cultural_score": (content_diversity + regional_diversity + authenticity_ratio + cultural_ratio + following_cultural_ratio + sound_diversity) / 6,
        "cultural_influence": calculate_cultural_influence(videos, interactions),
        "trend_vs_culture_balance": abs(trend_ratio - cultural_ratio),  # Lower is better balance
        "global_perspective": regional_diversity,
        "cultural_innovation": calculate_cultural_innovation(videos)
    }

def calculate_cultural_influence(videos: List[Dict], interactions: List[Dict]) -> float:
    """Calculate how much cultural influence the user has"""
    if not videos:
        return 0.0
    
    # Cultural videos with high engagement
    cultural_videos = [v for v in videos if v["cultural_weight"] > 0.7]
    if not cultural_videos:
        return 0.0
    
    total_cultural_engagement = sum(v["likes"] + v["shares"] + v["comments"] for v in cultural_videos)
    avg_cultural_engagement = total_cultural_engagement / len(cultural_videos)
    
    # Normalize based on follower count (would be available in real implementation)
    # For mock data, use a reasonable baseline
    baseline_engagement = 1000
    influence_score = min(avg_cultural_engagement / baseline_engagement, 1.0)
    
    return influence_score

def calculate_cultural_innovation(videos: List[Dict]) -> float:
    """Calculate cultural innovation score"""
    if not videos:
        return 0.0
    
    # Look for fusion content (high cultural weight + trend participation)
    fusion_videos = [v for v in videos if v["cultural_weight"] > 0.7 and v["trend_participation"]]
    fusion_ratio = len(fusion_videos) / len(videos)
    
    # Look for unique sound usage
    sound_usage = {}
    for video in videos:
        sound_id = video["sound"]["sound_id"]
        sound_usage[sound_id] = sound_usage.get(sound_id, 0) + 1
    
    unique_sounds = len([s for s, count in sound_usage.items() if count == 1])
    sound_innovation = unique_sounds / len(videos) if videos else 0
    
    return (fusion_ratio + sound_innovation) / 2

def analyze_trend_participation(videos: List[Dict]) -> Dict[str, Any]:
    """Analyze trend participation patterns"""
    trend_videos = [v for v in videos if v["trend_participation"]]
    
    if not trend_videos:
        return {"participation_rate": 0.0, "trends": []}
    
    # Analyze which categories have most trend participation
    category_trends = {}
    for video in trend_videos:
        category = video["category"]
        category_trends[category] = category_trends.get(category, 0) + 1
    
    return {
        "participation_rate": len(trend_videos) / len(videos),
        "trending_categories": dict(sorted(category_trends.items(), key=lambda x: x[1], reverse=True)),
        "cultural_trend_fusion": len([v for v in trend_videos if v["cultural_weight"] > 0.7]) / len(trend_videos),
        "trend_success_rate": sum(v["viral_score"] for v in trend_videos) / len(trend_videos)
    }

def analyze_sound_preferences(videos: List[Dict]) -> Dict[str, Any]:
    """Analyze sound usage preferences"""
    sound_usage = {}
    origin_usage = {}
    
    for video in videos:
        sound = video["sound"]
        sound_id = sound["sound_id"]
        origin = sound["origin"]
        
        sound_usage[sound_id] = sound_usage.get(sound_id, 0) + 1
        origin_usage[origin] = origin_usage.get(origin, 0) + 1
    
    total_videos = len(videos)
    origin_distribution = {origin: count/total_videos for origin, count in origin_usage.items()}
    
    return {
        "most_used_sounds": dict(sorted(sound_usage.items(), key=lambda x: x[1], reverse=True)[:5]),
        "origin_distribution": origin_distribution,
        "cultural_sound_preference": sum(count for origin, count in origin_usage.items() if origin != "global") / total_videos,
        "sound_diversity": len(set(v["sound"]["sound_id"] for v in videos)) / total_videos
    }

def generate_tiktok_cultural_evolution(videos: List[Dict]) -> List[Dict]:
    """Generate cultural evolution timeline for TikTok"""
    # Sort videos by date
    sorted_videos = sorted(videos, key=lambda x: x["posted_at"])
    
    # Group by weeks
    weekly_data = {}
    for video in sorted_videos:
        video_date = datetime.fromisoformat(video["posted_at"])
        week_start = video_date - timedelta(days=video_date.weekday())
        week_key = week_start.strftime("%Y-W%U")
        
        if week_key not in weekly_data:
            weekly_data[week_key] = {"videos": [], "categories": {}, "sounds": {}, "regions": {}}
        
        weekly_data[week_key]["videos"].append(video)
        
        category = video["category"]
        sound_origin = video["sound"]["origin"]
        region = video["region"]
        
        weekly_data[week_key]["categories"][category] = weekly_data[week_key]["categories"].get(category, 0) + 1
        weekly_data[week_key]["sounds"][sound_origin] = weekly_data[week_key]["sounds"].get(sound_origin, 0) + 1
        weekly_data[week_key]["regions"][region] = weekly_data[week_key]["regions"].get(region, 0) + 1
    
    evolution = []
    for week, data in sorted(weekly_data.items())[-8:]:  # Last 8 weeks
        if data["videos"]:
            evolution.append({
                "week": week,
                "video_count": len(data["videos"]),
                "dominant_category": max(data["categories"].items(), key=lambda x: x[1])[0] if data["categories"] else None,
                "dominant_sound_origin": max(data["sounds"].items(), key=lambda x: x[1])[0] if data["sounds"] else None,
                "dominant_region": max(data["regions"].items(), key=lambda x: x[1])[0] if data["regions"] else None,
                "cultural_diversity": len(data["categories"]) / len(TIKTOK_CATEGORIES),
                "sound_diversity": len(data["sounds"]) / 6,  # 6 major origins
                "avg_viral_score": sum(v["viral_score"] for v in data["videos"]) / len(data["videos"]),
                "cultural_weight": sum(v["cultural_weight"] for v in data["videos"]) / len(data["videos"]),
                "trend_participation": sum(1 for v in data["videos"] if v["trend_participation"]) / len(data["videos"])
            })
    
    return evolution

def identify_viral_content(videos: List[Dict]) -> List[Dict]:
    """Identify viral content and analyze patterns"""
    # Sort by viral score
    viral_videos = sorted([v for v in videos if v["viral_score"] > 0.6], 
                         key=lambda x: x["viral_score"], reverse=True)[:5]
    
    viral_analysis = []
    for video in viral_videos:
        analysis = {
            "video_id": video["video_id"],
            "category": video["category"],
            "viral_score": video["viral_score"],
            "cultural_weight": video["cultural_weight"],
            "views": video["views"],
            "engagement_rate": video["engagement_rate"],
            "sound_origin": video["sound"]["origin"],
            "trend_participation": video["trend_participation"],
            "success_factors": identify_success_factors(video)
        }
        viral_analysis.append(analysis)
    
    return viral_analysis

def identify_success_factors(video: Dict) -> List[str]:
    """Identify factors that contributed to video success"""
    factors = []
    
    if video["cultural_weight"] > 0.8:
        factors.append("high_cultural_authenticity")
    
    if video["trend_participation"]:
        factors.append("trend_participation")
    
    if video["engagement_rate"] > 0.15:
        factors.append("high_engagement")
    
    if video["sound"]["usage_count"] > 50000:
        factors.append("popular_sound")
    
    if video["duration"] < 30:
        factors.append("short_format")
    
    if len(video["hashtags"]) >= 3:
        factors.append("good_hashtag_usage")
    
    return factors

# Mock data for testing
MOCK_USERS = ["user_1", "user_2", "user_3", "user_4", "user_5"]

def get_all_mock_tiktok_data() -> Dict[str, Any]:
    """Get all mock TikTok data for testing"""
    return {
        user_id: generate_mock_tiktok_profile(user_id)
        for user_id in MOCK_USERS
    }

if __name__ == "__main__":
    # Test the mock data generation
    test_data = generate_mock_tiktok_profile("test_user")
    print("Mock TikTok Profile Generated:")
    print(f"Videos: {len(test_data['videos'])}")
    print(f"Following: {len(test_data['following'])}")
    print(f"Cultural Score: {test_data['cultural_metrics']['overall_cultural_score']:.2f}")
    print(f"Viral Cultural Ratio: {test_data['cultural_metrics']['viral_cultural_ratio']:.2f}")
    print(f"Sound Diversity: {test_data['cultural_metrics']['sound_diversity']:.2f}")