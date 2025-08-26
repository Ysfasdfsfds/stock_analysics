#!/usr/bin/env python3
"""
上证A股实时行情API路由
提供上证A股实时行情数据的RESTful API接口
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from utils.response import success_response, error_response
from utils.validators import validate_stock_symbol
from data_handlers.sh_a_stock_data import (
    get_sh_a_realtime_stocks,
    filter_sh_a_stocks,
    get_sh_a_stock_by_code,
    get_sh_a_market_summary,
    get_stock_type_info,
    get_stock_type_batch,
    get_all_industries
)

# 创建蓝图
bp = Blueprint('sh_a_stock', __name__, url_prefix='/api/sh-a')

@bp.route('/realtime', methods=['GET'])
def get_realtime_stocks():
    """
    获取上证A股实时行情数据
    
    Query Parameters:
        limit (int): 返回股票数量限制，默认返回全部
        offset (int): 偏移量，默认0
    
    Returns:
        {
            "code": 200,
            "message": "success",
            "timestamp": "2024-01-01T12:00:00",
            "data": {
                "total": 500,
                "stocks": [...],
                "query_time": "2024-01-01T12:00:00"
            }
        }
    """
    try:
        # 获取查询参数
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 获取实时数据
        stocks = get_sh_a_realtime_stocks()
        if stocks is None:
            return error_response('获取上证A股数据失败', 500)
        
        # 应用分页
        total = len(stocks)
        if limit:
            stocks = stocks[offset:offset + limit]
        else:
            stocks = stocks[offset:]
        
        return success_response({
            'total': total,
            'stocks': stocks,
            'query_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        return error_response(f'获取上证A股实时行情失败: {str(e)}', 500)

@bp.route('/filter', methods=['GET'])
def filter_stocks():
    """
    根据条件筛选上证A股股票
    
    Query Parameters:
        min_price (float): 最低价格，默认0
        max_price (float): 最高价格，默认1000
        min_turnover_rate (float): 最低换手率(%)
        max_turnover_rate (float): 最高换手率(%)
        min_market_cap (float): 最低流通市值(亿元)
        max_market_cap (float): 最高流通市值(亿元)
        sort_by (str): 排序字段，可选: latest_price, change_percent, turnover_rate, total_market_cap, circulation_market_cap
        ascending (bool): 是否升序，默认true
    
    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total": 50,
                "stocks": [...],
                "filters": {...}
            }
        }
    """
    try:
        # 获取筛选参数
        filters = {
            'min_price': request.args.get('min_price', 0, type=float),
            'max_price': request.args.get('max_price', 1000, type=float),
            'min_turnover_rate': request.args.get('min_turnover_rate', 0, type=float),
            'max_turnover_rate': request.args.get('max_turnover_rate', 100, type=float),
            'min_market_cap': request.args.get('min_market_cap', 0, type=float),
            'max_market_cap': request.args.get('max_market_cap', 100000, type=float),
            'sort_by': request.args.get('sort_by', 'turnover_rate'),
            'ascending': request.args.get('ascending', 'true').lower() != 'false'
        }
        
        # 筛选股票
        filtered_stocks = filter_sh_a_stocks(**filters)
        if filtered_stocks is None:
            return error_response('筛选股票数据失败', 500)
        
        return success_response({
            'total': len(filtered_stocks),
            'stocks': filtered_stocks,
            'filters': filters
        })
        
    except ValueError as e:
        return error_response(f'参数格式错误: {str(e)}', 400)
    except Exception as e:
        return error_response(f'筛选股票失败: {str(e)}', 500)

@bp.route('/stock/<code>', methods=['GET'])
def get_stock_detail(code):
    """
    获取单只股票详细信息
    
    Args:
        code (str): 股票代码
    
    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {...}
        }
    """
    try:
        # 验证股票代码
        if not validate_stock_symbol(code):
            return error_response('无效的股票代码格式', 400)
        
        # 获取股票详情
        stock = get_sh_a_stock_by_code(code)
        if stock is None:
            return error_response(f'未找到股票 {code}', 404)
        
        return success_response(stock)
        
    except Exception as e:
        return error_response(f'获取股票详情失败: {str(e)}', 500)

@bp.route('/market-summary', methods=['GET'])
def get_market_summary():
    """
    获取上证A股市场概览信息
    
    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total_stocks": 500,
                "up_stocks": 250,
                "down_stocks": 200,
                "flat_stocks": 50,
                "avg_turnover_rate": 2.35,
                "avg_change_percent": 1.25,
                "timestamp": "2024-01-01T12:00:00"
            }
        }
    """
    try:
        summary = get_sh_a_market_summary()
        if summary is None:
            return error_response('获取市场概览失败', 500)
        
        return success_response(summary)
        
    except Exception as e:
        return error_response(f'获取市场概览失败: {str(e)}', 500)

@bp.route('/hot-stocks', methods=['GET'])
def get_hot_stocks():
    """
    获取热门股票（基于换手率排序）
    
    Query Parameters:
        count (int): 返回股票数量，默认10
    
    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "count": 10,
                "stocks": [...]
            }
        }
    """
    try:
        count = min(request.args.get('count', 10, type=int), 100)
        
        # 获取高换手率股票
        hot_stocks = filter_sh_a_stocks(
            min_turnover_rate=5,  # 换手率大于5%
            sort_by='turnover_rate',
            ascending=False
        )
        
        if hot_stocks is None:
            return error_response('获取热门股票失败', 500)
        
        # 限制返回数量
        hot_stocks = hot_stocks[:count]
        
        return success_response({
            'count': len(hot_stocks),
            'stocks': hot_stocks
        })
        
    except Exception as e:
        return error_response(f'获取热门股票失败: {str(e)}', 500)

@bp.route('/low-turnover-stocks', methods=['GET'])
def get_low_turnover_stocks():
    """
    获取低换手率优质股票
    
    基于你原有代码逻辑：换手率在1%到5%之间，价格在10-60之间，流通市值大于100亿
    
    Query Parameters:
        count (int): 返回股票数量，默认20
    
    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "count": 20,
                "stocks": [...],
                "criteria": {...}
            }
        }
    """
    try:
        count = min(request.args.get('count', 20, type=int), 100)
        
        # 使用原有筛选逻辑
        low_turnover_stocks = filter_sh_a_stocks(
            min_price=10,
            max_price=60,
            min_turnover_rate=1,
            max_turnover_rate=5,
            min_market_cap=100,  # 100亿元
            sort_by='turnover_rate',
            ascending=True
        )
        
        if low_turnover_stocks is None:
            return error_response('获取低换手率股票失败', 500)
        
        # 限制返回数量
        low_turnover_stocks = low_turnover_stocks[:count]
        
        criteria = {
            'price_range': '10-60',
            'turnover_range': '1%-5%',
            'min_market_cap': '100亿元',
            'sort_by': 'turnover_rate_asc'
        }
        
        return success_response({
            'count': len(low_turnover_stocks),
            'stocks': low_turnover_stocks,
            'criteria': criteria
        })
        
    except Exception as e:
        return error_response(f'获取低换手率股票失败: {str(e)}', 500)

@bp.route('/stock/<code>/type', methods=['GET'])
def get_stock_type(code):
    """
    获取指定股票的类型信息

    Args:
        code (str): 股票代码

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {...}
        }
    """
    try:
        type_info = get_stock_type_info(code)
        print(type_info)
        if type_info is None:
            return error_response(f'无法获取股票{code}的类型信息', 404)
        
        return success_response(type_info)
        
    except Exception as e:
        return error_response(str(e), 500)

@bp.route('/stock/types/batch', methods=['POST'])
def get_stock_types_batch():
    """
    批量获取股票类型信息

    POST Body:
        {
            "codes": ["600000", "600001", ...]
        }

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total": 3,
                "types": [...]
            }
        }
    """
    try:
        data = request.get_json()
        if not data or 'codes' not in data:
            return error_response('请提供股票代码列表', 400)
        
        codes = data['codes']
        if not isinstance(codes, list):
            return error_response('codes必须是列表格式', 400)
        
        type_info_list = get_stock_type_batch(codes)
        if type_info_list is None:
            return error_response('获取股票类型信息失败', 500)
        
        return success_response({
            'total': len(type_info_list),
            'types': type_info_list
        })
        
    except Exception as e:
        return error_response(str(e), 500)

@bp.route('/industries', methods=['GET'])
def get_industries():
    """
    获取所有上证A股行业分类

    Returns:
        {
            "code": 200,
            "message": "success",
            "data": {
                "total": 50,
                "industries": [...]
            }
        }
    """
    try:
        industries = get_all_industries()
        if industries is None:
            return error_response('获取行业分类失败', 500)
        
        return success_response({
            'total': len(industries),
            'industries': industries
        })
        
    except Exception as e:
        return error_response(str(e), 500)