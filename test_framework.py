#!/usr/bin/env python3
"""
框架测试脚本
验证框架结构是否正确
"""

import os
import sys
from pathlib import Path

def test_framework():
    """测试框架结构"""
    print("🔍 检查框架结构...")
    
    # 检查必要的目录
    required_dirs = [
        'routes',
        'data_handlers',
        'utils',
        'models',
        'tests',
        'logs',
        'data'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {missing_dirs}")
    else:
        print("✅ 所有必要目录已存在")
    
    # 检查必要的文件
    required_files = [
        'app.py',
        'run.py',
        'config.py',
        'requirements.txt',
        'README.md',
        'routes/example.py',
        'data_handlers/stock_data.py',
        'utils/response.py',
        'utils/validators.py'
    ]
    
    missing_files = []
    for file_name in required_files:
        if not Path(file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
    else:
        print("✅ 所有必要文件已存在")
    
    # 检查Python语法
    print("\n🔍 检查Python语法...")
    
    python_files = [
        'app.py',
        'run.py',
        'config.py',
        'routes/example.py',
        'data_handlers/stock_data.py',
        'utils/response.py',
        'utils/validators.py'
    ]
    
    syntax_errors = []
    for file_name in python_files:
        try:
            with open(file_name, 'r') as f:
                code = f.read()
            compile(code, file_name, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_name}: {e}")
    
    if syntax_errors:
        print(f"❌ 语法错误: {syntax_errors}")
    else:
        print("✅ 所有Python文件语法正确")
    
    print("\n📋 框架验证完成！")
    print("\n下一步：")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 复制环境变量: cp .env.example .env")
    print("3. 启动服务: python3 run.py")
    print("4. 测试接口: curl http://localhost:5000/health")

if __name__ == '__main__':
    test_framework()