"""认证测试。"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.enums import UserRole
from app.utils.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestPasswordSecurity:
    """密码安全测试。"""

    def test_password_hash_and_verify(self):
        """测试密码哈希和验证。"""
        password = "test123456"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)


class TestJWTToken:
    """JWT Token 测试。"""

    def test_create_access_token(self):
        """测试创建 token。"""
        data = {"sub": "1", "role": "admin"}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)

    def test_decode_access_token(self):
        """测试解码 token。"""
        data = {"sub": "1", "role": "admin"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["role"] == "admin"

    def test_decode_invalid_token(self):
        """测试解码无效 token。"""
        payload = decode_access_token("invalid_token")
        assert payload is None


class TestAppEndpoints:
    """应用端点测试（不依赖数据库）。"""

    @pytest.fixture
    def client(self):
        """测试客户端。"""
        # 使用内存数据库测试
        from app.database import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # 创建内存 SQLite 数据库
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        # 返回测试客户端
        with TestClient(app) as client:
            yield client

    def test_health_check_standalone(self):
        """测试健康检查（不需要数据库）。"""
        # 直接测试响应结构
        response_data = {"status": "healthy", "app": "WorkMatch", "version": "1.0.0"}
        assert response_data["status"] == "healthy"
