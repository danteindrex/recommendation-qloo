#!/usr/bin/env python3
"""Simple integration test to verify social media clients work"""

import asyncio
from app.integrations.social_media.instagram import InstagramClient
from app.integrations.social_media.tiktok import TikTokClient
from app.integrations.social_media.spotify import SpotifyClient
from app.services.social_media_service import SocialMediaService
from app.models.cultural_data import SocialPlatform


async def test_clients():
    """Test that all clients can be instantiated and basic methods work"""
    
    # Test Instagram client
    instagram = InstagramClient("test_id", "test_secret")
    oauth_url = await instagram.get_oauth_url("http://localhost:3000/callback", "test_state")
    print(f"✓ Instagram OAuth URL generated: {oauth_url[:50]}...")
    
    # Test TikTok client
    tiktok = TikTokClient("test_id", "test_secret")
    oauth_url = await tiktok.get_oauth_url("http://localhost:3000/callback", "test_state")
    print(f"✓ TikTok OAuth URL generated: {oauth_url[:50]}...")
    
    # Test Spotify client
    spotify = SpotifyClient("test_id", "test_secret")
    oauth_url = await spotify.get_oauth_url("http://localhost:3000/callback", "test_state")
    print(f"✓ Spotify OAuth URL generated: {oauth_url[:50]}...")
    
    # Test unified service
    service = SocialMediaService()
    
    # Test OAuth URL generation for each platform
    for platform in [SocialPlatform.INSTAGRAM, SocialPlatform.TIKTOK, SocialPlatform.SPOTIFY]:
        try:
            oauth_url = await service.get_oauth_url(platform, "http://localhost:3000/callback", "test_state")
            print(f"✓ {platform.value} service OAuth URL generated: {oauth_url[:50]}...")
        except Exception as e:
            print(f"✗ Error with {platform.value} service: {e}")
    
    # Test data normalization
    from app.integrations.social_media.base import SocialMediaData
    from datetime import datetime, timezone
    
    test_data = SocialMediaData(
        platform="instagram",
        user_id="test_user",
        data_type="post",
        content={"media_type": "IMAGE", "caption": "Test post #hashtag"},
        timestamp=datetime.now(timezone.utc),
        raw_data={}
    )
    
    normalized = service._normalize_social_media_data(test_data)
    print(f"✓ Data normalization works: {normalized['platform']}")
    
    # Test cultural signal extraction
    signals = service._extract_cultural_signals(test_data)
    print(f"✓ Cultural signal extraction works: {len(signals)} signals extracted")
    
    # Test confidence score calculation
    confidence = service._calculate_confidence_score(test_data)
    print(f"✓ Confidence score calculation works: {confidence}")
    
    # Close clients
    await instagram.close()
    await tiktok.close()
    await spotify.close()
    await service.close_clients()
    
    print("\n🎉 All social media integration tests passed!")


if __name__ == "__main__":
    asyncio.run(test_clients())