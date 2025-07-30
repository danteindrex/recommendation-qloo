"""
Mock Spotify data for testing cultural intelligence features
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Mock Spotify genres and their cultural associations
SPOTIFY_GENRES = {
    "pop": {"region": "global", "cultural_weight": 0.3, "diversity_score": 0.4},
    "hip-hop": {"region": "north_america", "cultural_weight": 0.8, "diversity_score": 0.7},
    "k-pop": {"region": "asia", "cultural_weight": 0.9, "diversity_score": 0.8},
    "reggaeton": {"region": "latin_america", "cultural_weight": 0.9, "diversity_score": 0.8},
    "afrobeats": {"region": "africa", "cultural_weight": 0.9, "diversity_score": 0.9},
    "electronic": {"region": "europe", "cultural_weight": 0.6, "diversity_score": 0.5},
    "indie": {"region": "global", "cultural_weight": 0.7, "diversity_score": 0.6},
    "jazz": {"region": "north_america", "cultural_weight": 0.8, "diversity_score": 0.7},
    "classical": {"region": "europe", "cultural_weight": 0.9, "diversity_score": 0.6},
    "folk": {"region": "global", "cultural_weight": 0.8, "diversity_score": 0.8},
    "reggae": {"region": "caribbean", "cultural_weight": 0.9, "diversity_score": 0.8},
    "flamenco": {"region": "europe", "cultural_weight": 0.9, "diversity_score": 0.7},
    "bollywood": {"region": "asia", "cultural_weight": 0.9, "diversity_score": 0.8},
    "bossa_nova": {"region": "latin_america", "cultural_weight": 0.8, "diversity_score": 0.7},
    "nordic_folk": {"region": "europe", "cultural_weight": 0.8, "diversity_score": 0.6}
}

# Mock artists with cultural significance
MOCK_ARTISTS = [
    {"name": "BTS", "genre": "k-pop", "popularity": 95, "cultural_impact": 0.9},
    {"name": "Bad Bunny", "genre": "reggaeton", "popularity": 92, "cultural_impact": 0.9},
    {"name": "Burna Boy", "genre": "afrobeats", "popularity": 85, "cultural_impact": 0.8},
    {"name": "Rosalía", "genre": "flamenco", "popularity": 80, "cultural_impact": 0.8},
    {"name": "Anitta", "genre": "pop", "popularity": 78, "cultural_impact": 0.7},
    {"name": "Stromae", "genre": "electronic", "popularity": 75, "cultural_impact": 0.7},
    {"name": "Tash Sultana", "genre": "indie", "popularity": 70, "cultural_impact": 0.6},
    {"name": "Kamasi Washington", "genre": "jazz", "popularity": 65, "cultural_impact": 0.8},
    {"name": "Ólafur Arnalds", "genre": "nordic_folk", "popularity": 60, "cultural_impact": 0.7},
    {"name": "A.R. Rahman", "genre": "bollywood", "popularity": 88, "cultural_impact": 0.9},
]

def generate_mock_spotify_profile(user_id: str) -> Dict[str, Any]:
    """Generate a comprehensive mock Spotify profile"""
    
    # Generate listening history
    listening_history = []
    for i in range(100):  # 100 recent tracks
        artist = random.choice(MOCK_ARTISTS)
        track = {
            "track_id": f"spotify:track:{random.randint(100000, 999999)}",
            "track_name": f"Song {random.randint(1, 1000)}",
            "artist_name": artist["name"],
            "genre": artist["genre"],
            "played_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "duration_ms": random.randint(120000, 300000),  # 2-5 minutes
            "popularity": artist["popularity"],
            "cultural_weight": SPOTIFY_GENRES[artist["genre"]]["cultural_weight"]
        }
        listening_history.append(track)
    
    # Calculate genre distribution
    genre_counts = {}
    for track in listening_history:
        genre = track["genre"]
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    total_tracks = len(listening_history)
    genre_distribution = {
        genre: count / total_tracks 
        for genre, count in genre_counts.items()
    }
    
    # Calculate cultural metrics
    cultural_diversity = calculate_cultural_diversity(listening_history)
    regional_exposure = calculate_regional_exposure(listening_history)
    
    return {
        "user_id": user_id,
        "platform": "spotify",
        "profile": {
            "display_name": f"User_{user_id}",
            "followers": random.randint(10, 1000),
            "following": random.randint(50, 500),
            "total_playlists": random.randint(5, 50)
        },
        "listening_history": listening_history,
        "genre_distribution": genre_distribution,
        "cultural_metrics": {
            "diversity_score": cultural_diversity,
            "regional_exposure": regional_exposure,
            "mainstream_ratio": calculate_mainstream_ratio(listening_history),
            "discovery_rate": random.uniform(0.1, 0.8),
            "cultural_openness": random.uniform(0.3, 0.9)
        },
        "top_artists": get_top_artists(listening_history),
        "top_genres": dict(sorted(genre_distribution.items(), key=lambda x: x[1], reverse=True)[:10]),
        "cultural_evolution": generate_cultural_evolution(listening_history),
        "last_updated": datetime.now().isoformat()
    }

def calculate_cultural_diversity(listening_history: List[Dict]) -> float:
    """Calculate cultural diversity score based on genre and regional variety"""
    genres = set(track["genre"] for track in listening_history)
    regions = set(SPOTIFY_GENRES[track["genre"]]["region"] for track in listening_history)
    
    # Normalize scores
    genre_diversity = min(len(genres) / 10, 1.0)  # Max 10 genres for full score
    regional_diversity = min(len(regions) / 6, 1.0)  # Max 6 regions for full score
    
    return (genre_diversity + regional_diversity) / 2

def calculate_regional_exposure(listening_history: List[Dict]) -> Dict[str, float]:
    """Calculate exposure to different cultural regions"""
    region_counts = {}
    for track in listening_history:
        region = SPOTIFY_GENRES[track["genre"]]["region"]
        region_counts[region] = region_counts.get(region, 0) + 1
    
    total = len(listening_history)
    return {region: count / total for region, count in region_counts.items()}

def calculate_mainstream_ratio(listening_history: List[Dict]) -> float:
    """Calculate ratio of mainstream vs niche music"""
    mainstream_threshold = 70
    mainstream_count = sum(1 for track in listening_history if track["popularity"] >= mainstream_threshold)
    return mainstream_count / len(listening_history)

def get_top_artists(listening_history: List[Dict]) -> List[Dict]:
    """Get top artists by play count"""
    artist_counts = {}
    for track in listening_history:
        artist = track["artist_name"]
        if artist not in artist_counts:
            artist_counts[artist] = {"count": 0, "genre": track["genre"]}
        artist_counts[artist]["count"] += 1
    
    return [
        {"name": artist, "play_count": data["count"], "genre": data["genre"]}
        for artist, data in sorted(artist_counts.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    ]

def generate_cultural_evolution(listening_history: List[Dict]) -> List[Dict]:
    """Generate cultural evolution timeline"""
    # Sort by date
    sorted_history = sorted(listening_history, key=lambda x: x["played_at"])
    
    # Group by weeks
    evolution = []
    current_week = None
    week_genres = {}
    
    for track in sorted_history:
        track_date = datetime.fromisoformat(track["played_at"])
        week_start = track_date - timedelta(days=track_date.weekday())
        week_key = week_start.strftime("%Y-%W")
        
        if current_week != week_key:
            if current_week and week_genres:
                evolution.append({
                    "week": current_week,
                    "dominant_genre": max(week_genres.items(), key=lambda x: x[1])[0],
                    "genre_distribution": week_genres,
                    "diversity_score": len(week_genres) / 10
                })
            current_week = week_key
            week_genres = {}
        
        genre = track["genre"]
        week_genres[genre] = week_genres.get(genre, 0) + 1
    
    return evolution[-12:]  # Last 12 weeks

def generate_playlist_data(user_id: str) -> List[Dict]:
    """Generate mock playlist data"""
    playlists = []
    playlist_themes = [
        "Workout Vibes", "Chill Evening", "Cultural Discovery", "Global Beats",
        "Study Focus", "Party Mix", "Indie Discoveries", "World Music Journey",
        "Electronic Exploration", "Jazz & Soul", "Latin Rhythms", "Asian Pop Hits"
    ]
    
    for i, theme in enumerate(playlist_themes[:random.randint(5, 10)]):
        playlist = {
            "playlist_id": f"playlist_{user_id}_{i}",
            "name": theme,
            "description": f"My {theme.lower()} collection",
            "track_count": random.randint(15, 100),
            "followers": random.randint(0, 50),
            "public": random.choice([True, False]),
            "collaborative": random.choice([True, False]),
            "created_at": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
            "cultural_theme": random.choice(list(SPOTIFY_GENRES.keys())),
            "diversity_score": random.uniform(0.2, 0.9)
        }
        playlists.append(playlist)
    
    return playlists

# Mock data for testing
MOCK_USERS = ["user_1", "user_2", "user_3", "user_4", "user_5"]

def get_all_mock_spotify_data() -> Dict[str, Any]:
    """Get all mock Spotify data for testing"""
    return {
        user_id: {
            "profile": generate_mock_spotify_profile(user_id),
            "playlists": generate_playlist_data(user_id)
        }
        for user_id in MOCK_USERS
    }

if __name__ == "__main__":
    # Test the mock data generation
    test_data = generate_mock_spotify_profile("test_user")
    print("Mock Spotify Profile Generated:")
    print(f"Genres: {len(test_data['genre_distribution'])}")
    print(f"Diversity Score: {test_data['cultural_metrics']['diversity_score']:.2f}")
    print(f"Top Genre: {list(test_data['top_genres'].keys())[0]}")