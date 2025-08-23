#!/usr/bin/env python3
"""
应用测试文件
"""

import pytest
import json
from app import create_app

@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """测试健康检查接口"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index(client):
    """测试根路径接口"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data

def test_404(client):
    """测试404错误"""
    response = client.get('/nonexistent')
    assert response.status_code == 404