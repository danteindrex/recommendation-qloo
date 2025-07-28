#!/usr/bin/env python3
"""Test API routes for social media integration"""

import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from app.models.cultural_data import SocialPlatform


def test_oauth_url_generation():
    """Test OAuth URL generation endpoint"""
    client = TestClient(app)
    
    # Mock authentication
    with patch('app.api.dependencies.auth.get_current_user') as mock_auth:
        mock_user = MagicMock()
        mock_user.id = "test_user_id"
        mock_auth.return_value = mock_user
        
        # Test Instagram OAuth URL
        response = client.get(
            "/api/social-media/oauth/instagram/url",
            params={
                "redirect_uri": "http://localhost:3000/callback",
                "state": "test_state"
            }
        )
        
        print(f"OAuth URL response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ OAuth URL generated: {data['oauth_url'][:50]}...")
            print(f"✓ Platform: {data['platform']}")
        else:
            print(f"✗ Error: {response.text}")


def test_connections_endpoint():
    """Test user connections endpoint"""
    client = TestClient(app)
    
    # Mock authentication and database
    with patch('app.api.dependencies.auth.get_current_user') as mock_auth, \
         patch('app.core.database.get_db') as mock_db:
        
        mock_user = MagicMock()
        mock_user.id = "test_user_id"
        mock_auth.return_value = mock_user
        
        # Mock database session
        mock_session = MagicMock()
        mock_db.return_value = mock_session
        
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        response = client.get("/api/social-media/connections")
        
        print(f"Connections response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Connections retrieved: {data['total_connections']} connections")
        else:
            print(f"✗ Error: {response.text}")


if __name__ == "__main__":
    print("Testing social media API routes...")
    test_oauth_url_generation()
    test_connections_endpoint()
    print("✅ API route tests completed!")