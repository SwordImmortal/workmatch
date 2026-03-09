"""API 端集成测试。"""

import pytest
from http import HTTPStatus
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """测试客户端。"""
    with TestClient(app) as client:
        yield client


class TestAuthAPI:
    """认证 API 测试。"""

    def test_login_endpoint_exists(self, client):
        """测试登录端点存在。"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpassword"},
        )
        # 可能返回 401（无用户）或 422（验证失败），但不应是 404
        assert response.status_code != HTTPStatus.NOT_FOUND

    def test_me_endpoint_requires_auth(self, client):
        """测试 /me 端点需要认证。"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_me_endpoint_with_invalid_token(self, client):
        """测试无效 token 访问 /me。"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_logout_endpoint(self, client):
        """测试登出端点。"""
        response = client.post("/api/v1/auth/logout")
        # logout 应该是无状态的，不需要认证
        assert response.status_code == HTTPStatus.OK


class TestRootEndpoint:
    """根端点测试。"""

    def test_root(self, client):
        """测试根端点。"""
        response = client.get("/")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "message" in data
        assert "docs" in data

    def test_health_endpoint(self, client):
        """测试健康检查端点。"""
        response = client.get("/health")
        # 可能存在也可能不存在
        if response.status_code == HTTPStatus.OK:
            assert response.json() is not None
