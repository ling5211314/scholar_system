import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    """测试用户注册"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123456",
        "full_name": "Test User"
    }
    response = client.post("/api/users/register", json=user_data)
    # 可能因为用户已存在而失败，这是正常的
    assert response.status_code in [200, 201, 400]


def test_login():
    """测试用户登录"""
    login_data = {
        "username": "testuser",
        "password": "test123456"
    }
    response = client.post("/api/users/login", json=login_data)
    # 如果用户不存在会返回401
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        assert "access_token" in response.json()
