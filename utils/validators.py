#!/usr/bin/env python3
"""
数据验证工具
提供常用的数据验证函数
"""

import re
from typing import List, Optional

def validate_stock_symbol(symbol: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        symbol: 股票代码
    
    Returns:
        是否有效
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # 支持A股和美股格式
    pattern = r'^[A-Z]{1,6}$|^\d{6}$'
    return bool(re.match(pattern, symbol.upper()))

def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    验证日期范围
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        是否有效
    """
    try:
        from datetime import datetime
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        return start <= end
    except ValueError:
        return False

def validate_period(period: str) -> bool:
    """
    验证时间周期
    
    Args:
        period: 时间周期
    
    Returns:
        是否有效
    """
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    return period in valid_periods

def validate_interval(interval: str) -> bool:
    """
    验证时间间隔
    
    Args:
        interval: 时间间隔
    
    Returns:
        是否有效
    """
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    return interval in valid_intervals

def validate_symbols_list(symbols: List[str], max_count: int = 100) -> bool:
    """
    验证股票代码列表
    
    Args:
        symbols: 股票代码列表
        max_count: 最大数量限制
    
    Returns:
        是否有效
    """
    if not isinstance(symbols, list):
        return False
    
    if len(symbols) > max_count:
        return False
    
    return all(validate_stock_symbol(symbol) for symbol in symbols)

def sanitize_input(input_str: str) -> str:
    """
    清理输入字符串，防止注入攻击
    
    Args:
        input_str: 输入字符串
    
    Returns:
        清理后的字符串
    """
    if not isinstance(input_str, str):
        return ''
    
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '&', '"', "'", ";", "--", "/*", "*/"]
    result = input_str
    for char in dangerous_chars:
        result = result.replace(char, '')
    
    return result.strip()

class ValidationError(Exception):
    """验证错误异常类"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)