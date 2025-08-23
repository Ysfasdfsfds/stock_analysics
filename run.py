#!/usr/bin/env python3
"""
启动脚本
提供多种启动方式
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app
from config import config

def main():
    """主函数"""
    # 获取环境配置
    env = os.environ.get('FLASK_ENV', 'development')
    
    # 初始化配置
    config[env].init_app(app)
    
    # 启动应用
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"启动Flask应用...")
    print(f"环境: {env}")
    print(f"端口: {port}")
    print(f"调试模式: {debug}")
    print(f"访问: http://localhost:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()