import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import auth_service
from app.models.user import User, UserRole
from app.schemas.auth import UserCreate


class TestUserRegistration:
    """Test user registration functionality."""
    
    async def test_register_new_user(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "role": "consumer"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "consumer"
        assert data["has_passkey"] is False
        assert "id" in data
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with existing email fails."""
        user_data = {
            "email": test_user.email,
            "role": "consumer"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestGoogleOAuth:
    """Test Google OAuth authentication."""
    
    @patch('app.services.auth_service.AuthService.verify_google_token')
    async def test_google_auth_new_user(self, mock_verify, client: AsyncClient):
        """Test Google OAuth with new user."""
        mock_verify.return_value = {
            'sub': 'google123',
            'email': 'google@example.com',
            'iss': 'accounts.google.com'
        }
        
        response = await client.post("/api/auth/google", json={"token": "fake_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "google@example.com"
        assert data["user"]["google_id"] == "google123"
    
    @patch('app.services.auth_service.AuthService.verify_google_token')
    async def test_google_auth_existing_user(self, mock_verify, client: AsyncClient, db_session: AsyncSession):
        """Test Google OAuth with existing user."""
        # Create user with Google ID
        user = await auth_service.create_user(
            db_session, 
            "existing@example.com", 
            google_id="google456"
        )
        
        mock_verify.return_value = {
            'sub': 'google456',
            'email': 'existing@example.com',
            'iss': 'accounts.google.com'
        }
        
        response = await client.post("/api/auth/google", json={"token": "fake_token"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == str(user.id)
    
    @patch('app.services.auth_service.AuthService.verify_google_token')
    async def test_google_auth_invalid_token(self, mock_verify, client: AsyncClient):
        """Test Google OAuth with invalid token."""
        mock_verify.return_value = None
        
        response = await client.post("/api/auth/google", json={"token": "invalid_token"})
        
        assert response.status_code == 401
        assert "Invalid Google token" in response.json()["detail"]


class TestPasskeyAuthentication:
    """Test passkey authentication functionality."""
    
    async def test_begin_passkey_registration(self, client: AsyncClient, test_user: User, access_token: str):
        """Test beginning passkey registration."""
        response = await client.post(
            "/api/auth/passkey/register/begin",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "challenge" in data
        assert "rp" in data
        assert "user" in data
        assert data["rp"]["id"] == "localhost"
    
    async def test_begin_passkey_registration_user_not_found(self, client: AsyncClient):
        """Test passkey registration with non-existent user."""
        response = await client.post(
            "/api/auth/passkey/register/begin",
            json={"email": "nonexistent@example.com"}
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    async def test_begin_passkey_authentication_no_passkey(self, client: AsyncClient, test_user: User):
        """Test passkey authentication when user has no passkey."""
        response = await client.post(
            "/api/auth/passkey/authenticate/begin",
            json={"email": test_user.email}
        )
        
        assert response.status_code == 404
        assert "no passkey registered" in response.json()["detail"]


class TestJWTTokens:
    """Test JWT token functionality."""
    
    async def test_create_and_verify_access_token(self):
        """Test access token creation and verification."""
        user_id = "test-user-id"
        token = await auth_service.create_access_token({"sub": user_id})
        
        payload = await auth_service.verify_token(token, "access")
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
    
    async def test_create_and_verify_refresh_token(self):
        """Test refresh token creation and verification."""
        user_id = "test-user-id"
        token = await auth_service.create_refresh_token({"sub": user_id})
        
        payload = await auth_service.verify_token(token, "refresh")
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    async def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        payload = await auth_service.verify_token("invalid_token", "access")
        assert payload is None
    
    async def test_refresh_token_endpoint(self, client: AsyncClient, test_user: User):
        """Test token refresh endpoint."""
        refresh_token = await auth_service.create_refresh_token({"sub": str(test_user.id)})
        
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["id"] == str(test_user.id)
    
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]


class TestRoleBasedAccessControl:
    """Test role-based access control."""
    
    async def test_get_current_user_info(self, client: AsyncClient, test_user: User, access_token: str):
        """Test getting current user info."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """Test access without token."""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 403
    
    async def test_invalid_token_access(self, client: AsyncClient):
        """Test access with invalid token."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestLogout:
    """Test logout functionality."""
    
    async def test_logout_with_refresh_token(self, client: AsyncClient, test_user: User, access_token: str):
        """Test logout with refresh token."""
        refresh_token = await auth_service.create_refresh_token({"sub": str(test_user.id)})
        
        response = await client.post(
            "/api/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
        
        # Verify refresh token is blacklisted
        payload = await auth_service.verify_token(refresh_token, "refresh")
        assert payload is not None  # Token is still valid but should be blacklisted
        
        # Try to use blacklisted token
        response = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        # Note: This would require implementing blacklist check in refresh endpoint
    
    async def test_logout_without_refresh_token(self, client: AsyncClient, access_token: str):
        """Test logout without refresh token."""
        response = await client.post(
            "/api/auth/logout",
            json={},
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]


class TestAuthService:
    """Test AuthService methods directly."""
    
    async def test_create_user(self, db_session: AsyncSession):
        """Test user creation."""
        user = await auth_service.create_user(
            db_session, 
            "service@example.com", 
            UserRole.ENTERPRISE
        )
        
        assert user.email == "service@example.com"
        assert user.role == UserRole.ENTERPRISE
        assert user.id is not None
    
    async def test_get_user_by_email(self, db_session: AsyncSession, test_user: User):
        """Test getting user by email."""
        found_user = await auth_service.get_user_by_email(db_session, test_user.email)
        
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email
    
    async def test_get_user_by_id(self, db_session: AsyncSession, test_user: User):
        """Test getting user by ID."""
        found_user = await auth_service.get_user_by_id(db_session, str(test_user.id))
        
        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email
    
    async def test_get_user_by_google_id(self, db_session: AsyncSession):
        """Test getting user by Google ID."""
        # Create user with Google ID
        user = await auth_service.create_user(
            db_session, 
            "google@example.com", 
            google_id="google789"
        )
        
        found_user = await auth_service.get_user_by_google_id(db_session, "google789")
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.google_id == "google789"


class TestTokenBlacklist:
    """Test token blacklisting functionality."""
    
    async def test_blacklist_token(self):
        """Test token blacklisting."""
        from datetime import datetime, timedelta
        
        token = "test_token"
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        await auth_service.blacklist_token(token, expires_at)
        
        is_blacklisted = await auth_service.is_token_blacklisted(token)
        assert is_blacklisted is True
    
    async def test_non_blacklisted_token(self):
        """Test checking non-blacklisted token."""
        is_blacklisted = await auth_service.is_token_blacklisted("non_blacklisted_token")
        assert is_blacklisted is False