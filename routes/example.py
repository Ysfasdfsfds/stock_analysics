#!/usr/bin/env python3
"""
示例路由文件
展示如何创建API路由
用户可以复制此文件并重命名为新的路由文件
"""

from flask import Blueprint, jsonify, request
from utils.response import success_response, error_response
from data_handlers.stock_data import get_stock_data

# 创建蓝图
bp = Blueprint('example', __name__, url_prefix='/api/example')

@bp.route('/hello', methods=['GET'])
def hello_world():
    """示例接口 - Hello World"""
    return success_response({
        'message': 'Hello, World!',
        'data': {
            'timestamp': '2024-01-01 12:00:00',
            'version': '1.0.0'
        }
    })

@bp.route('/stock/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """
    获取股票信息示例接口
    
    Args:
        symbol: 股票代码，例如：AAPL, MSFT
    
    Returns:
        股票信息JSON
    """
    try:
        # 获取查询参数
        period = request.args.get('period', '1d')
        
        # 调用数据处理器获取数据
        stock_data = get_stock_data(symbol, period)
        
        if not stock_data:
            return error_response('股票数据获取失败', 404)
        
        return success_response({
            'symbol': symbol,
            'period': period,
            'data': stock_data
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"获取股票信息失败: {str(e)}")
        return error_response(f'获取股票信息失败: {str(e)}', 500)

@bp.route('/stocks', methods=['POST'])
def batch_get_stocks():
    """
    批量获取股票信息
    
    Request Body:
        {
            "symbols": ["AAPL", "MSFT", "GOOGL"],
            "period": "1d"
        }
    
    Returns:
        批量股票信息
    """
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        period = data.get('period', '1d')
        
        if not symbols:
            return error_response('股票代码列表不能为空', 400)
        
        results = []
        for symbol in symbols:
            stock_data = get_stock_data(symbol, period)
            results.append({
                'symbol': symbol,
                'data': stock_data,
                'success': bool(stock_data)
            })
        
        return success_response({
            'total': len(results),
            'results': results
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"批量获取股票信息失败: {str(e)}")
        return error_response(f'批量获取股票信息失败: {str(e)}', 500)

# 其他示例接口
@bp.route('/market/status', methods=['GET'])
def get_market_status():
    """获取市场状态"""
    return success_response({
        'status': 'open',
        'timestamp': '2024-01-01 12:00:00',
        'timezone': 'UTC+8'
    })

@bp.route('/market/summary', methods=['GET'])
def get_market_summary():
    """获取市场概览"""
    try:
        # 这里可以调用实际的数据获取逻辑
        summary_data = {
            'total_stocks': 5000,
            'up_stocks': 2500,
            'down_stocks': 2000,
            'flat_stocks': 500,
            'total_volume': 1000000000
        }
        
        return success_response(summary_data)
        
    except Exception as e:
        return error_response(f'获取市场概览失败: {str(e)}', 500)