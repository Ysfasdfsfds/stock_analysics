#!/usr/bin/env python3
"""
基本面分析API路由
提供股票基本面分析数据的RESTful API接口
"""

from datetime import datetime
import akshare as ak
import pandas as pd
import logging

from flask import Blueprint, jsonify, request
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

# 创建蓝图
bp = Blueprint('fundamental_analysis', __name__, url_prefix='/api/fundamental')

@bp.route('/company-info/<code>', methods=['GET'])
def get_company_info(code):
    """
    获取公司基本信息
    
    Args:
        code: 股票代码，例如：600000
    
    Returns:
        公司基本信息JSON
    """
    try:
        # 获取股票基本信息
        stock_info = ak.stock_individual_info_em(symbol=code)
        
        if stock_info is None or stock_info.empty:
            return error_response(f'未找到股票{code}的基本信息', 404)
        
        # 转换为字典格式
        info_dict = {}
        for _, row in stock_info.iterrows():
            key = row['item']
            value = row['value']
            info_dict[key] = value
        
        # 初始化公司数据（不依赖实时数据）
        company_data = {
            'code': code,
            'name': info_dict.get('股票简称', ''),
            'industry': info_dict.get('行业', ''),
            'establishment_date': info_dict.get('成立日期', ''),
            'listing_date': info_dict.get('上市日期', ''),
            'registered_capital': info_dict.get('注册资本', ''),
            'employees': info_dict.get('员工人数', ''),
            'main_business': info_dict.get('主营业务', ''),
            'business_scope': info_dict.get('经营范围', ''),
            # 实时数据默认值
            'total_market_cap': 0,
            'circulation_market_cap': 0,
            'pe_ratio': 0,
            'pb_ratio': 0,
            'latest_price': 0,
            'change_percent': 0,
            'turnover_rate': 0
        }
        
        # 尝试获取实时数据（使用单股票查询）
        try:
            # 使用历史数据获取最新价格信息
            hist_data = ak.stock_zh_a_hist(symbol=code, period='daily', start_date='2025-08-20', end_date='2025-08-27', adjust='')
            if not hist_data.empty:
                latest_record = hist_data.iloc[-1]
                company_data.update({
                    'latest_price': float(latest_record.get('收盘', 0)),
                    'change_percent': float(latest_record.get('涨跌幅', 0))
                })
        except Exception as realtime_error:
            logger.warning(f"获取股票{code}实时数据失败: {str(realtime_error)}")
            # 继续返回基本信息，即使没有实时数据
        
        return success_response(company_data)
        
    except Exception as e:
        logger.error(f"获取股票{code}基本信息失败: {str(e)}")
        return error_response(f'获取股票基本信息失败: {str(e)}', 500)

def get_stock_prefix(code):
    """
    根据股票代码判断市场前缀
    
    Args:
        code: 股票代码，如600000
    
    Returns:
        带前缀的股票代码，如sh600000
    """
    if code.startswith(('600', '601', '603', '605', '688')):
        return 'sh' + code  # 上海市场
    elif code.startswith(('000', '001', '002', '003', '300')):
        return 'sz' + code  # 深圳市场
    return 'sh' + code  # 默认上海市场

def extract_financial_indicators(financial_data):
    """
    从新浪财经数据中提取财务指标
    
    Args:
        financial_data: 新浪财经返回的财务数据
    
    Returns:
        整理后的财务指标字典
    """
    indicators = {
        'report_date': '',
        'roe': 0.0,
        'roa': 0.0, 
        'gross_profit_margin': 0.0,
        'net_profit_margin': 0.0,
        'debt_ratio': 0.0,
        'current_ratio': 0.0,
        'quick_ratio': 0.0,
        'inventory_turnover': 0.0,
        'receivable_turnover': 0.0,
        'total_asset_turnover': 0.0,
        'eps': 0.0,
        'book_value_per_share': 0.0
    }
    
    if financial_data is None or financial_data.empty:
        return indicators
    
    # 获取最新报告期（第3列通常是最新的数据）
    latest_column = financial_data.columns[2] if len(financial_data.columns) > 2 else financial_data.columns[0]
    indicators['report_date'] = latest_column
    
    # 尝试提取各种财务指标
    try:
        # 遍历数据查找相关指标
        for idx, row in financial_data.iterrows():
            indicator_name = row['指标'] if '指标' in row else (row.iloc[1] if len(row) > 1 else '')
            value = row[latest_column] if latest_column in row else 0
            
            # 净资产收益率
            if '净资产收益率' in str(indicator_name) or 'ROE' in str(indicator_name):
                indicators['roe'] = float(value) if value and value != '-' else 0.0
            # 每股收益
            elif '每股收益' in str(indicator_name) or 'EPS' in str(indicator_name):
                indicators['eps'] = float(value) if value and value != '-' else 0.0
            # 每股净资产
            elif '每股净资产' in str(indicator_name):
                indicators['book_value_per_share'] = float(value) if value and value != '-' else 0.0
    except Exception as e:
        logger.error(f"提取财务指标失败: {str(e)}")
    
    return indicators

@bp.route('/financial-indicators/<code>', methods=['GET'])
def get_financial_indicators(code):
    """
    获取财务指标
    
    Args:
        code: 股票代码，例如：600000
    
    Returns:
        财务指标JSON
    """
    try:
        # 获取财务指标数据 - 使用新浪财经API
        financial_data = ak.stock_financial_abstract(symbol=code)
        
        if financial_data is None or financial_data.empty:
            return error_response(f'未找到股票{code}的财务数据', 404)
        
        # 提取财务指标
        indicators = extract_financial_indicators(financial_data)
        
        # 计算财务健康评分
        score = calculate_financial_score(indicators)
        indicators['financial_score'] = score
        
        return success_response(indicators)
        
    except Exception as e:
        logger.error(f"获取股票{code}财务指标失败: {str(e)}")
        return error_response(f'获取财务指标失败: {str(e)}', 500)

@bp.route('/balance-sheet/<code>', methods=['GET'])
def get_balance_sheet(code):
    """
    获取资产负债表
    
    Args:
        code: 股票代码
    
    Returns:
        资产负债表数据
    """
    try:
        # 获取资产负债表数据 - 使用新浪财经API
        stock_code = get_stock_prefix(code)
        balance_data = ak.stock_financial_report_sina(stock=stock_code, symbol='资产负债表')
        
        if balance_data is None or balance_data.empty:
            return error_response(f'未找到股票{code}的资产负债表数据', 404)
        
        balance_sheet_items = []
        
        # 主要资产负债表项目映射
        balance_items = [
            ('货币资金', ['货币资金', '现金及存放中央银行款项', '现金及现金等价物']),
            ('应收账款', ['应收账款', '应收账款及应收利息', '发放贷款及垫款']),
            ('存货', ['存货']),
            ('流动资产合计', ['流动资产合计', '流动资产总计']),
            ('固定资产', ['固定资产', '固定资产净额']),
            ('资产总计', ['资产总计', '资产合计', '资产总额']),
            ('短期借款', ['短期借款', '短期负债']),
            ('应付账款', ['应付账款']),
            ('流动负债合计', ['流动负债合计', '流动负债总计']),
            ('长期借款', ['长期借款', '长期负债']),
            ('负债合计', ['负债合计', '负债总计']),
            ('股东权益合计', ['所有者权益合计', '股东权益合计', '归属于母公司所有者权益合计'])
        ]
        
        # 获取最近两期数据（第1行和第2行数据）
        if len(balance_data) >= 2:
            current_row = balance_data.iloc[0]  # 最新期数据
            previous_row = balance_data.iloc[1]  # 上期数据
            
            for item_display, possible_names in balance_items:
                current_value = 0
                previous_value = 0
                
                # 在列名中查找匹配的项目名称
                for possible_name in possible_names:
                    for col in balance_data.columns:
                        if possible_name in str(col):
                            try:
                                current_val = current_row[col] 
                                previous_val = previous_row[col]
                                
                                current_value = float(current_val) if current_val and str(current_val) != 'nan' and current_val != '-' else 0
                                previous_value = float(previous_val) if previous_val and str(previous_val) != 'nan' and previous_val != '-' else 0
                                break
                            except (ValueError, TypeError):
                                continue
                    if current_value > 0 or previous_value > 0:  # 找到数据就跳出
                        break
                
                # 计算变动比例
                if previous_value != 0:
                    change_percent = ((current_value - previous_value) / previous_value) * 100
                else:
                    change_percent = 0
                
                balance_sheet_items.append({
                    'item': item_display,
                    'current': format_amount(current_value),
                    'previous': format_amount(previous_value),
                    'change': f"{'+' if change_percent > 0 else ''}{change_percent:.2f}%"
                })
        
        return success_response(balance_sheet_items)
        
    except Exception as e:
        logger.error(f"获取股票{code}资产负债表失败: {str(e)}")
        return error_response(f'获取资产负债表失败: {str(e)}', 500)

@bp.route('/income-statement/<code>', methods=['GET'])
def get_income_statement(code):
    """
    获取利润表
    
    Args:
        code: 股票代码
    
    Returns:
        利润表数据
    """
    try:
        # 获取利润表数据 - 使用新浪财经API
        stock_code = get_stock_prefix(code)
        income_data = ak.stock_financial_report_sina(stock=stock_code, symbol='利润表')
        
        if income_data is None or income_data.empty:
            return error_response(f'未找到股票{code}的利润表数据', 404)
        
        income_statement_items = []
        
        # 主要利润表项目映射
        income_items = [
            ('营业收入', ['营业收入', '营业总收入']),
            ('营业成本', ['营业成本', '营业总成本']),
            ('营业利润', ['营业利润']),
            ('利润总额', ['利润总额', '税前利润']),
            ('净利润', ['净利润', '归属于母公司所有者的净利润'])
        ]
        
        # 获取最新期数据
        if len(income_data) >= 1:
            latest_row = income_data.iloc[0]  # 最新期数据
            revenue = 0
            
            # 先获取营业收入用于计算占比
            for possible_name in income_items[0][1]:  # 营业收入的可能名称
                for col in income_data.columns:
                    if possible_name in str(col):
                        try:
                            revenue_val = latest_row[col]
                            revenue = float(revenue_val) if revenue_val and str(revenue_val) != 'nan' and revenue_val != '-' else 0
                            if revenue > 0:
                                break
                        except (ValueError, TypeError):
                            continue
                if revenue > 0:
                    break
            
            # 提取各项利润表数据
            for item_display, possible_names in income_items:
                amount = 0
                
                # 在列名中查找匹配的项目名称
                for possible_name in possible_names:
                    for col in income_data.columns:
                        if possible_name in str(col):
                            try:
                                amount_val = latest_row[col]
                                amount = float(amount_val) if amount_val and str(amount_val) != 'nan' and amount_val != '-' else 0
                                break
                            except (ValueError, TypeError):
                                continue
                    if amount != 0:  # 找到数据就跳出
                        break
                
                # 计算占收入比例
                if revenue > 0 and amount != 0:
                    percentage = (amount / revenue) * 100
                else:
                    percentage = 100.0 if item_display == '营业收入' and amount > 0 else 0.0
                
                income_statement_items.append({
                    'item': item_display,
                    'amount': format_amount(amount),
                    'percentage': f"{percentage:.2f}%"
                })
        
        return success_response(income_statement_items)
        
    except Exception as e:
        logger.error(f"获取股票{code}利润表失败: {str(e)}")
        return error_response(f'获取利润表失败: {str(e)}', 500)

@bp.route('/cash-flow/<code>', methods=['GET'])
def get_cash_flow(code):
    """
    获取现金流量表
    
    Args:
        code: 股票代码
    
    Returns:
        现金流量表数据
    """
    try:
        # 获取现金流量表数据 - 使用新浪财经API
        stock_code = get_stock_prefix(code)
        cashflow_data = ak.stock_financial_report_sina(stock=stock_code, symbol='现金流量表')
        
        if cashflow_data is None or cashflow_data.empty:
            return error_response(f'未找到股票{code}的现金流量表数据', 404)
        
        cashflow_items = []
        
        # 主要现金流量项目映射
        cash_flow_items = [
            ('经营活动现金流量净额', ['经营活动产生的现金流量净额', '经营活动现金流量净额']),
            ('投资活动现金流量净额', ['投资活动产生的现金流量净额', '投资活动现金流量净额']),
            ('筹资活动现金流量净额', ['筹资活动产生的现金流量净额', '筹资活动现金流量净额']),
            ('现金及现金等价物净增加额', ['现金及现金等价物净增加额', '现金净增加额'])
        ]
        
        # 获取最新期数据
        if len(cashflow_data) >= 1:
            latest_row = cashflow_data.iloc[0]  # 最新期数据
            
            for item_display, possible_names in cash_flow_items:
                amount = 0
                
                # 在列名中查找匹配的项目名称
                for possible_name in possible_names:
                    for col in cashflow_data.columns:
                        if possible_name in str(col):
                            try:
                                amount_val = latest_row[col]
                                amount = float(amount_val) if amount_val and str(amount_val) != 'nan' and amount_val != '-' else 0
                                break
                            except (ValueError, TypeError):
                                continue
                    if amount != 0:  # 找到数据就跳出
                        break
                
                # 判断现金流方向
                if amount > 0:
                    direction = '流入'
                elif amount < 0:
                    direction = '流出'
                else:
                    direction = '平衡'
                
                cashflow_items.append({
                    'item': item_display,
                    'amount': format_amount(abs(amount)),
                    'direction': direction
                })
        
        return success_response(cashflow_items)
        
    except Exception as e:
        logger.error(f"获取股票{code}现金流量表失败: {str(e)}")
        return error_response(f'获取现金流量表失败: {str(e)}', 500)

def calculate_financial_score(indicators):
    """
    计算财务健康评分
    
    Args:
        indicators: 财务指标字典
    
    Returns:
        评分(0-100)
    """
    score = 0
    
    # ROE评分 (0-25分)
    roe = indicators.get('roe', 0)
    if roe > 20:
        score += 25
    elif roe > 15:
        score += 20
    elif roe > 10:
        score += 15
    elif roe > 5:
        score += 10
    
    # 负债率评分 (0-25分)
    debt_ratio = indicators.get('debt_ratio', 0)
    if debt_ratio < 30:
        score += 25
    elif debt_ratio < 50:
        score += 20
    elif debt_ratio < 70:
        score += 15
    elif debt_ratio < 85:
        score += 10
    
    # 流动比率评分 (0-25分)
    current_ratio = indicators.get('current_ratio', 0)
    if current_ratio > 2:
        score += 25
    elif current_ratio > 1.5:
        score += 20
    elif current_ratio > 1:
        score += 15
    elif current_ratio > 0.8:
        score += 10
    
    # 净利润率评分 (0-25分)
    net_profit_margin = indicators.get('net_profit_margin', 0)
    if net_profit_margin > 20:
        score += 25
    elif net_profit_margin > 15:
        score += 20
    elif net_profit_margin > 10:
        score += 15
    elif net_profit_margin > 5:
        score += 10
    
    return min(score, 100)

def format_amount(amount):
    """
    格式化金额
    
    Args:
        amount: 金额
    
    Returns:
        格式化后的金额字符串
    """
    if amount >= 100000000:
        return f"{amount / 100000000:.2f}亿"
    elif amount >= 10000:
        return f"{amount / 10000:.2f}万"
    else:
        return f"{amount:.2f}"