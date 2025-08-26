#!/usr/bin/env python3
"""
股票类型信息API测试脚本
测试新创建的股票类型信息接口
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_api(endpoint, method='GET', data=None, params=None):
    """测试API接口"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, timeout=30)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=30)
        else:
            print(f"❌ 不支持的方法: {method}")
            return
        
        print(f"✅ {endpoint} - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   响应数据示例: {json.dumps(result.get('data', {}), ensure_ascii=False, indent=2)[:200]}...")
        else:
            print(f"   错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint} - 连接失败，请确保服务已启动")
    except Exception as e:
        print(f"❌ {endpoint} - 错误: {str(e)}")

def test_get_all_industries():
    """测试获取行业分类"""
    try:
        response = requests.get(f"{BASE_URL}/api/sh-a/industries")
        
        if response.status_code == 200:
            data = response.json()
            industries = data.get('data', {}).get('industries', [])
            total = data.get('data', {}).get('total', 0)
            
            print(f"✅ 行业分类获取成功")
            print(f"   总行业数: {total}")
            print(f"   行业列表: {[ind['industry'] for ind in industries[:5]]}")
            
            # 验证行业数据格式
            if industries:
                sample = industries[0]
                print(f"   示例行业数据: {sample['industry']} ({sample['count']}只股票)")
            return True
        else:
            print(f"❌ 行业分类获取失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 行业分类测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🧪 测试股票类型信息API接口...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试接口
    test_cases = [
        ("/api/sh-a/stock/600000/type", "GET"),
        ("/api/sh-a/stock/688001/type", "GET"),
        ("/api/sh-a/stock/types/batch", "POST", {"codes": ["600000", "600001", "688001"]}),
        ("/api/sh-a/industries", "GET")
    ]
    
    print("测试步骤：")
    print("1. 确保服务已启动: python3 run.py")
    print("2. 等待所有接口测试完成...")
    print()
    
    for endpoint, method, *data in test_cases:
        test_data = data[0] if data else None
        if endpoint == "/api/sh-a/industries":
            test_get_all_industries()
        else:
            test_api(endpoint, method, test_data)
    
    print()
    print("📋 测试完成！")
    print("如果所有接口都返回200状态码，说明API正常工作")
    print("如果返回404，请确保服务已启动")
    print("如果返回500，请检查akshare库是否安装: pip install akshare")

if __name__ == '__main__':
    main()