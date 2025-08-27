#!/usr/bin/env python3
"""
股票分析系统启动器
专为Windows exe打包优化的启动脚本
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# 添加项目根目录到Python路径
if hasattr(sys, '_MEIPASS'):
    # PyInstaller环境
    BASE_DIR = Path(sys._MEIPASS)
    # 确保所有项目目录在路径中
    sys.path.insert(0, str(BASE_DIR))
    for subdir in ['routes', 'data_handlers', 'utils']:
        subdir_path = BASE_DIR / subdir
        if subdir_path.exists():
            sys.path.insert(0, str(subdir_path))
else:
    # 开发环境  
    BASE_DIR = Path(__file__).parent

sys.path.insert(0, str(BASE_DIR))

# 设置工作目录
os.chdir(str(BASE_DIR))

# 导入Flask应用
from app import create_app, register_base_routes, auto_register_routes, auto_import_data_handlers

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待Flask启动
    webbrowser.open('http://localhost:5001')

def main():
    """主函数"""
    print("正在启动股票分析系统...")
    print("=" * 50)
    
    try:
        # 创建Flask应用
        app = create_app()
        
        # 注册基础路由
        register_base_routes(app)
        
        # 自动导入数据处理器
        auto_import_data_handlers()
        
        # 自动注册路由
        auto_register_routes(app)
        
        print("✓ Flask应用初始化完成")
        print("✓ 路由注册完成")
        print("✓ 数据处理器导入完成")
        print("=" * 50)
        print("服务地址: http://localhost:5001")
        print("正在启动浏览器...")
        print("=" * 50)
        
        # 启动浏览器（在新线程中）
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,  # 生产环境关闭调试模式
            threaded=True,
            use_reloader=False  # 避免重启导致问题
        )
        
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
    except Exception as e:
        print(f"启动失败: {str(e)}")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()