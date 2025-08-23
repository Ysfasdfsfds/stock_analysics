import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')

def get_stock_data_real(stock_code, date_str):
    """
    使用akshare获取真实股票数据
    """
    try:
        import akshare as ak
        
        # 获取股票历史数据
        # 对于603345这样的沪市股票，代码前加sh
        stock_code_full = f"sh{stock_code}" if stock_code.startswith('6') else f"sz{stock_code}"
        
        # 获取指定日期附近的数据
        start_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=10)).strftime("%Y%m%d")
        end_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y%m%d")
        
        # 获取日线数据
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code_full, period="daily", start_date=start_date, end_date=end_date, adjust="")
        
        if stock_zh_a_hist_df.empty:
            print(f"未找到{stock_code}在{date_str}的数据")
            return None
            
        # 转换日期格式
        stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # 查找指定日期的数据
        target_data = stock_zh_a_hist_df[stock_zh_a_hist_df['日期'] == target_date]
        
        if target_data.empty:
            print(f"{stock_code}在{date_str}无交易数据")
            return None
            
        # 提取数据
        data = target_data.iloc[0]
        
        # 获取股票基本信息
        try:
            stock_info = ak.stock_zh_a_spot()
            stock_name = stock_info[stock_info['代码'] == stock_code]['名称'].iloc[0]
        except:
            stock_name = "未知"
        
        result = {
            '股票代码': stock_code,
            '股票名称': stock_name,
            '交易日期': date_str,
            '开盘价': float(data['开盘']),
            '收盘价': float(data['收盘']),
            '最高价': float(data['最高']),
            '最低价': float(data['最低']),
            '成交量': int(data['成交量']),
            '成交额': float(data['成交额']),
            '涨跌幅': float(data['涨跌幅']),
            '涨跌额': float(data['涨跌额']),
            '换手率': float(data['换手率']) if '换手率' in data else 0.0,
            '振幅': float(data['振幅']) if '振幅' in data else 0.0
        }
        
        return result
        
    except ImportError:
        print("未安装akshare，请运行: pip install akshare")
        return None
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        return None

def create_sample_data_603345(date_str):
    """
    创建603345的样本数据，用于演示
    """
    return {
        '股票代码': '603345',
        '股票名称': '安井食品',
        '交易日期': date_str,
        '开盘价': 78.50,
        '收盘价': 79.25,
        '最高价': 80.12,
        '最低价': 77.80,
        '成交量': 2456800,
        '成交额': 194500000,
        '涨跌幅': 1.28,
        '涨跌额': 1.00,
        '换手率': 2.45,
        '振幅': 2.96
    }

def analyze_stock_data(data):
    """
    详细分析股票数据
    """
    if not data:
        return None
        
    print("\n" + "="*70)
    print(f"🔍 {data['股票名称']}({data['股票代码']}) - {data['交易日期']} 详细分析报告")
    print("="*70)
    
    # 1. 价格分析
    print("\n📊 【价格分析】")
    print(f"   开盘价: ¥{data['开盘价']:.2f}")
    print(f"   收盘价: ¥{data['收盘价']:.2f}")
    print(f"   最高价: ¥{data['最高价']:.2f}")
    print(f"   最低价: ¥{data['最低价']:.2f}")
    
    price_range = data['最高价'] - data['最低价']
    price_range_pct = (price_range / data['开盘价']) * 100
    print(f"   日内波幅: ¥{price_range:.2f} ({price_range_pct:.2f}%)")
    
    # 2. 涨跌分析
    print("\n📈 【涨跌分析】")
    print(f"   涨跌额: ¥{data['涨跌额']:.2f}")
    print(f"   涨跌幅: {data['涨跌幅']:.2f}%")
    
    if data['涨跌幅'] > 5:
        status = "🚀 强势涨停"
    elif data['涨跌幅'] > 2:
        status = "📈 大幅上涨"
    elif data['涨跌幅'] > 0:
        status = "✅ 温和上涨"
    elif data['涨跌幅'] > -2:
        status = "📉 温和下跌"
    elif data['涨跌幅'] > -5:
        status = "❌ 大幅下跌"
    else:
        status = "💥 跌停"
    
    print(f"   当日状态: {status}")
    
    # 3. 成交量分析
    print("\n📊 【成交分析】")
    print(f"   成交量: {data['成交量']:,} 手")
    print(f"   成交额: ¥{data['成交额']:,.0f}")
    print(f"   换手率: {data['换手率']:.2f}%")
    print(f"   振幅: {data['振幅']:.2f}%")
    
    # 成交量活跃度判断
    if data['换手率'] > 10:
        activity = "🔥 极度活跃"
    elif data['换手率'] > 5:
        activity = "📊 较为活跃"
    elif data['换手率'] > 2:
        activity = "💤 正常交易"
    else:
        activity = "😴 交易清淡"
    
    print(f"   成交活跃度: {activity}")
    
    # 4. 技术指标计算
    print("\n📉 【技术指标】")
    
    # 计算一些基础技术指标
    close_price = data['收盘价']
    open_price = data['开盘价']
    high_price = data['最高价']
    low_price = data['最低价']
    
    # 计算K线形态
    if close_price > open_price:
        candle_color = "🟢 阳线"
    else:
        candle_color = "🔴 阴线"
    
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    body_size = abs(close_price - open_price)
    
    print(f"   K线形态: {candle_color}")
    print(f"   上影线: ¥{upper_shadow:.2f}")
    print(f"   下影线: ¥{lower_shadow:.2f}")
    print(f"   实体大小: ¥{body_size:.2f}")
    
    # 5. 投资建议
    print("\n" + "="*70)
    print("🎯 【投资建议】")
    print("="*70)
    
    # 基于数据的综合分析
    recommendations = []
    
    # 基于涨跌幅
    if data['涨跌幅'] > 3:
        recommendations.append("⚠️  涨幅较大，注意回调风险")
    elif data['涨跌幅'] < -3:
        recommendations.append("🔍 跌幅较大，关注反弹机会")
    
    # 基于换手率
    if data['换手率'] > 8:
        recommendations.append("🔥 高换手率，资金关注度高")
    elif data['换手率'] < 1:
        recommendations.append("💤 低换手率，流动性较差")
    
    # 基于振幅
    if data['振幅'] > 5:
        recommendations.append("⚡ 振幅较大，波动性强")
    
    # 基于K线形态
    if upper_shadow > body_size * 2:
        recommendations.append("📈 上影线较长，上方有压力")
    if lower_shadow > body_size * 2:
        recommendations.append("📉 下影线较长，下方有支撑")
    
    if not recommendations:
        recommendations.append("📊 走势平稳，正常波动")
    
    for rec in recommendations:
        print(f"   {rec}")
    
    return data

def save_analysis_result(data, filename=None):
    """
    保存分析结果到文件
    """
    if not filename:
        filename = f"{data['股票代码']}_{data['交易日期'].replace('-', '')}_analysis.csv"
    
    filepath = f"/Users/huangchuang/Downloads/金融数据分析/{filename}"
    
    # 转换为DataFrame并保存
    df = pd.DataFrame([data])
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"\n📄 分析结果已保存至: {filepath}")
    return filepath

if __name__ == "__main__":
    # 分析603345在2024年8月22日的数据
    stock_code = "603345"
    target_date = "2024-08-22"
    
    print("🚀 开始获取603345股票数据...")
    
    # 尝试获取真实数据
    data = get_stock_data_real(stock_code, target_date)
    
    if not data:
        print("使用样本数据进行演示...")
        data = create_sample_data_603345(target_date)
    
    # 分析数据
    analyzed_data = analyze_stock_data(data)
    
    # 保存结果
    save_analysis_result(analyzed_data)
    
    print("\n✅ 分析完成！")