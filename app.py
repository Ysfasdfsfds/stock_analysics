#!/usr/bin/env python3
"""
Flask股票数据服务主应用
用户只需要在指定目录添加数据获取逻辑、接口函数和路由即可
"""

import os
import sys
import importlib.util
from pathlib import Path
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    
    # 启用CORS
    CORS(app)
    
    # 配置应用
    app.config['JSON_AS_ASCII'] = False  # 支持中文
    app.config['JSON_SORT_KEYS'] = False  # 保持JSON字段顺序
    
    return app

def register_base_routes(app):
    """注册基础路由"""
    
    # 健康检查接口
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        return jsonify({
            'status': 'healthy',
            'message': '股票数据服务运行正常',
            'version': '1.0.0'
        })

    # 前端应用路由
    @app.route('/')
    def index():
        """提供前端应用主页"""
        return render_template('index.html')

    # 静态资源路由  
    @app.route('/assets/<path:filename>')
    def assets(filename):
        """提供静态资源文件"""
        return send_from_directory('static/assets', filename)

    @app.route('/favicon.ico')
    def favicon():
        """提供favicon"""
        return send_from_directory('static', 'favicon.ico')

    # 所有前端路由都返回index.html（SPA模式）
    @app.route('/<path:path>')
    def spa_routes(path):
        """处理Vue Router的路由，返回index.html"""
        # 如果请求的是API路径，不处理
        if path.startswith('api/') or path.startswith('health'):
            return jsonify({'error': 'API endpoint not found'}), 404
        return render_template('index.html')

def auto_register_routes(app):
    """
    自动发现并注册路由
    扫描routes目录下的所有Python文件并注册路由
    """
    routes_dir = Path(__file__).parent / 'routes'
    
    if not routes_dir.exists():
        logger.warning(f"路由目录不存在: {routes_dir}")
        return
    
    # 获取所有Python文件
    route_files = [f for f in routes_dir.glob('*.py') if not f.name.startswith('__')]
    
    for route_file in route_files:
        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(
                route_file.stem, route_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找并注册蓝图
            if hasattr(module, 'bp'):
                app.register_blueprint(module.bp)
                logger.info(f"已注册路由模块: {route_file.stem}")
            else:
                logger.warning(f"路由文件 {route_file.stem} 未定义蓝图(bp)")
                
        except Exception as e:
            logger.error(f"注册路由文件 {route_file.stem} 失败: {str(e)}")

def auto_import_data_handlers():
    """
    自动导入数据处理器
    扫描data_handlers目录下的所有Python文件
    """
    handlers_dir = Path(__file__).parent / 'data_handlers'
    
    if not handlers_dir.exists():
        logger.warning(f"数据处理器目录不存在: {handlers_dir}")
        return
    
    # 获取所有Python文件
    handler_files = [f for f in handlers_dir.glob('*.py') if not f.name.startswith('__')]
    
    for handler_file in handler_files:
        try:
            # 动态导入模块
            spec = importlib.util.spec_from_file_location(
                handler_file.stem, handler_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            logger.info(f"已导入数据处理器: {handler_file.stem}")
            
        except Exception as e:
            logger.error(f"导入数据处理器 {handler_file.stem} 失败: {str(e)}")

if __name__ == '__main__':
    # 创建Flask应用
    app = create_app()
    
    # 注册基础路由
    register_base_routes(app)
    
    # 自动导入数据处理器
    auto_import_data_handlers()
    
    # 自动注册路由
    auto_register_routes(app)
    print(app.url_map)
    # 启动应用
    port = int(os.environ.get('PORT', 5001))
    print(port)
    
    logger.info(f"启动Flask应用，端口: {port}, 调试模式: True")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True,
    )