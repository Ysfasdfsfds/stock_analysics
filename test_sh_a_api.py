#!/usr/bin/env python3
"""
上证A股API测试脚本
测试新创建的接口是否正常工作
"""

import requests
import json
import sys
from datetime import datetime

def test_api(endpoint, params=None):
    """测试API接口"""
    base_url = "http://localhost:5000"
    url = f"{base_url}{endpoint}"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"✅ {endpoint} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                if isinstance(data['data'], dict):
                    if 'stocks' in data['data']:
                        print(f"   返回股票数量: {len(data['data']['stocks'])}")
                    elif 'total' in data['data']:
                        print(f"   总数: {data['data']['total']}")
                else:
                    print(f"   数据类型: {type(data['data'])}")
        else:
            print(f"   错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint} - 连接失败，请确保服务已启动")
    except Exception as e:
        print(f"❌ {endpoint} - 错误: {str(e)}")

def main():
    """主测试函数"""
    print("🧪 测试上证A股API接口...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试接口
    test_cases = [
        ("/api/sh-a/market-summary", None),
        ("/api/sh-a/low-turnover-stocks", {"count": 5}),
        ("/api/sh-a/hot-stocks", {"count": 5}),
        ("/api/sh-a/stock/600000", None),
        ("/api/sh-a/filter", {
            "min_price": 10,
            "max_price": 60,
            "min_turnover_rate": 1,
            "max_turnover_rate": 5,
            "min_market_cap": 100,
            "count": 5
        }),
        ("/api/sh-a/realtime", {"limit": 3})
    ]
    
    print("测试步骤：")
    print("1. 确保服务已启动: python3 run.py")
    print("2. 等待所有接口测试完成...")
    print()
    
    for endpoint, params in test_cases:
        test_api(endpoint, params)
    
    print()
    print("📋 测试完成！")
    print("如果所有接口都返回200状态码，说明API正常工作")
    print("如果返回404，请确保服务已启动")
    print("如果返回500，请检查akshare库是否安装: pip install akshare")

if __name__ == '__main__':
    main()