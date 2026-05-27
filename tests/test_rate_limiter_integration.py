"""
Integration tests for rate limiting with authentication
"""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app, users_db


@pytest.fixture(autouse=True)
def cleanup_users():
    """Clean up test users before and after each test"""
    # Store original users
    original_users = users_db.copy()
    
    yield
    
    # Restore original users after test
    users_db.clear()
    users_db.update(original_users)


@pytest.mark.asyncio
class TestRateLimiter:
    """Test rate limiting with authenticated and anonymous users"""

    async def test_anonymous_user_rate_limit_2_requests(self):
        """Anonymous user should be limited to 2 requests per minute"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Request 1 - should succeed
            response1 = await client.get("/books/")
            assert response1.status_code == 200
            assert response1.headers.get("x-ratelimit-limit") == "2"
            assert response1.headers.get("x-ratelimit-remaining") == "1"
            
            # Request 2 - should succeed
            response2 = await client.get("/books/")
            assert response2.status_code == 200
            assert response2.headers.get("x-ratelimit-limit") == "2"
            assert response2.headers.get("x-ratelimit-remaining") == "0"
            
            # Request 3 - should be rate limited (429)
            response3 = await client.get("/books/")
            assert response3.status_code == 429
            assert "Rate limit exceeded" in response3.text
            assert response3.headers.get("x-ratelimit-remaining") == "0"

    async def test_authenticated_user_rate_limit_10_requests(self):
        """Authenticated user should be limited to 10 requests per minute"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Signup
            signup_response = await client.post(
                "/auth/signup",
                json={"username": "testuser_auth_10_v3", "password": "pass123"}
            )
            # Either 200 (new user) or 409 (already exists from previous run) is ok
            assert signup_response.status_code in [200, 409]

            # 2. Login and get token
            login_response = await client.post(
                "/auth/login",
                data={"username": "testuser_auth_10_v3", "password": "pass123"}
            )
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            token = login_response.json()["access_token"]

            # 3. Make 10 successful requests and check rate limit decreases
            prev_remaining = None
            for i in range(10):
                response = await client.get(
                    "/books/",
                    headers={"Authorization": f"Bearer {token}"}
                )
                remaining = int(response.headers.get("x-ratelimit-remaining", -1))
                print(f"Request {i+1}: status={response.status_code}, limit={response.headers.get('x-ratelimit-limit')}, remaining={remaining}")
                
                assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}: {response.text}"
                assert response.headers.get("x-ratelimit-limit") == "10"
                
                # Check that remaining decreases or stays same (for first request)
                if prev_remaining is not None:
                    assert remaining <= prev_remaining, f"Request {i+1}: remaining should decrease, got {remaining} after {prev_remaining}"
                prev_remaining = remaining

            # 4. 11th request should be rate limited
            response11 = await client.get(
                "/books/",
                headers={"Authorization": f"Bearer {token}"}
            )
            remaining11 = response11.headers.get("x-ratelimit-remaining", "?")
            print(f"Request 11: status={response11.status_code}, limit={response11.headers.get('x-ratelimit-limit')}, remaining={remaining11}")
            
            assert response11.status_code == 429, f"Expected 429, got {response11.status_code}"
            assert "Rate limit exceeded" in response11.text

    async def test_authenticated_vs_anonymous_different_limits(self):
        """Authenticated and anonymous users should have different limits"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. Signup and login
            signup_response = await client.post(
                "/auth/signup",
                json={"username": "testuser_diff_limits", "password": "pass123"}
            )
            assert signup_response.status_code in [200, 409]

            login_response = await client.post(
                "/auth/login",
                data={"username": "testuser_diff_limits", "password": "pass123"}
            )
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            token = login_response.json()["access_token"]

            # 2. Anonymous request
            anon_response = await client.get("/books/")
            assert anon_response.status_code == 200
            anon_limit = int(anon_response.headers.get("x-ratelimit-limit"))

            # 3. Authenticated request
            auth_response = await client.get(
                "/books/",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert auth_response.status_code == 200
            auth_limit = int(auth_response.headers.get("x-ratelimit-limit"))

            # Anonymous limit should be 2, authenticated should be 10
            assert anon_limit == 2, f"Expected anonymous limit 2, got {anon_limit}"
            assert auth_limit == 10, f"Expected auth limit 10, got {auth_limit}"
            assert auth_limit > anon_limit

    async def test_invalid_token_treated_as_anonymous(self):
        """Invalid token should be treated as anonymous user"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Make request with invalid token
            response = await client.get(
                "/books/",
                headers={"Authorization": "Bearer invalid_token_xyz"}
            )
            assert response.status_code == 200
            # Should have anonymous limit (2)
            assert response.headers.get("x-ratelimit-limit") == "2"

    async def test_auth_endpoints_not_rate_limited(self):
        """Auth endpoints should not be rate limited"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Login multiple times without hitting rate limit
            for i in range(5):
                response = await client.post(
                    "/auth/login",
                    data={"username": "admin", "password": "admin123"}
                )
                # Should get either 200 or 401, but NOT 429
                assert response.status_code in [200, 401]
                assert response.status_code != 429

    async def test_docs_not_rate_limited(self):
        """Documentation endpoints should not be rate limited"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Access docs multiple times
            for i in range(5):
                response = await client.get("/docs")
                # Should get 200, not 429
                assert response.status_code != 429

    async def test_get_endpoints_public_without_auth(self):
        """GET /books/ should be accessible without authentication"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/books/")
            # Should return 200, not 401
            assert response.status_code in [200, 429]  # 429 only if rate limited

    async def test_post_books_requires_auth(self):
        """POST /books/ should require authentication"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/books/",
                json={
                    "title": "Test Book",
                    "author": "Test Author",
                    "description": "Test",
                    "status": "available",
                    "year": 2024
                }
            )
            # Should return 401 (Unauthorized), not 200
            assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Test complete authentication flow"""

    async def test_signup_and_login(self):
        """Test user registration and login"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Signup
            signup_response = await client.post(
                "/auth/signup",
                json={"username": "newuser_signup_123", "password": "securepass"}
            )
            assert signup_response.status_code == 200, f"Signup failed: {signup_response.text}"
            assert signup_response.json()["username"] == "newuser_signup_123"

            # Login
            login_response = await client.post(
                "/auth/login",
                data={"username": "newuser_signup_123", "password": "securepass"}
            )
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            assert "access_token" in login_response.json()
            assert "refresh_token" in login_response.json()

    async def test_login_with_invalid_credentials(self):
        """Test login with wrong password"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                data={"username": "admin", "password": "wrongpassword"}
            )
            assert response.status_code == 401

    async def test_refresh_token(self):
        """Test refresh token functionality"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Login
            login_response = await client.post(
                "/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            assert login_response.status_code == 200
            refresh_token = login_response.json()["refresh_token"]

            # Refresh
            refresh_response = await client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert refresh_response.status_code == 200
            assert "access_token" in refresh_response.json()

    async def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Login
            login_response = await client.post(
                "/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            token = login_response.json()["access_token"]

            # Create book with token
            response = await client.post(
                "/books/",
                json={
                    "title": "Protected Book",
                    "author": "Admin",
                    "description": "Test book",
                    "status": "available",
                    "year": 2024
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200, f"Create book failed: {response.text}"
            assert response.json()["title"] == "Protected Book"
