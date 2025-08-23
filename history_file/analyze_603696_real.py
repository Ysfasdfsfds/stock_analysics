import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_real_stock_data_603696():
    """
    使用akshare获取603696海南矿业在2024年8月22日的真实交易数据
    """
    try:
        import akshare as ak
        
        stock_code = "603696"
        target_date = "2024-08-22"
        
        print(f"🚀 正在获取{stock_code}海南矿业在{target_date}的真实交易数据...")
        
        # 获取股票历史数据
        # 603696是沪市股票，代码前加sh
        stock_code_full = "sh603696"
        
        # 获取指定日期附近的数据（前后各扩展几天以确保获取到目标日期）
        start_date = "20240820"  # 2024年8月20日
        end_date = "20240823"    # 2024年8月23日
        
        # 获取日线数据
        stock_data = ak.stock_zh_a_hist(symbol=stock_code_full, 
                                       period="daily", 
                                       start_date=start_date, 
                                       end_date=end_date, 
                                       adjust="")
        
        if stock_data.empty:
            print("❌ 未获取到数据，可能的原因：")
            print("   1. 8月22日是非交易日（周末或节假日）")
            print("   2. 网络连接问题")
            print("   3. akshare数据源暂时不可用")
            return None
        
        # 转换日期格式
        stock_data['日期'] = pd.to_datetime(stock_data['日期'])
        target_date_dt = datetime.strptime(target_date, "%Y-%m-%d")
        
        # 查找8月22日的数据
        target_data = stock_data[stock_data['日期'] == target_date_dt]
        
        if target_data.empty:
            print(f"⚠️  {target_date}没有{stock_code}的交易数据")
            print("   可能原因：该日是周末或节假日")
            
            # 显示该时间段内的所有数据
            print("\n📊 该时间段内的交易数据：")
            print(stock_data[['日期', '开盘', '收盘', '最高', '最低', '成交量', '涨跌幅']])
            return None
        
        # 提取8月22日的数据
        data = target_data.iloc[0]
        
        # 获取股票名称
        try:
            stock_info = ak.stock_zh_a_spot()
            stock_name = stock_info[stock_info['代码'] == stock_code]['名称'].iloc[0]
        except:
            stock_name = "海南矿业"
        
        # 构建结果字典
        result = {
            '股票代码': stock_code,
            '股票名称': stock_name,
            '交易日期': target_date,
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
        print("❌ 未安装akshare库")
        print("💡 请运行: pip install akshare")
        return None
    except Exception as e:
        print(f"❌ 获取数据失败: {str(e)}")
        return None

def analyze_603696_data(data):
    """
    详细分析603696的交易数据
    """
    if not data:
        return None
    
    print("\n" + "="*80)
    print(f"🔍 {data['股票名称']}({data['股票代码']}) - {data['交易日期']} 完整分析报告")
    print("="*80)
    
    # 1. 基本信息
    print(f"\n📋 【基本信息】")
    print(f"   股票代码: {data['股票代码']}")
    print(f"   股票名称: {data['股票名称']}")
    print(f"   交易日期: {data['交易日期']}")
    
    # 2. 价格分析
    print(f"\n📊 【价格分析】")
    print(f"   开盘价: ¥{data['开盘价']:.2f}")
    print(f"   收盘价: ¥{data['收盘价']:.2f}")
    print(f"   最高价: ¥{data['最高价']:.2f}")
    print(f"   最低价: ¥{data['最低价']:.2f}")
    
    price_range = data['最高价'] - data['最低价']
    price_range_pct = (price_range / data['开盘价']) * 100
    print(f"   日内波幅: ¥{price_range:.2f} ({price_range_pct:.2f}%)")
    
    # 3. 涨跌分析
    print(f"\n📈 【涨跌分析】")
    print(f"   涨跌额: ¥{data['涨跌额']:.2f}")
    print(f"   涨跌幅: {data['涨跌幅']:.2f}%")
    
    # 涨跌状态判断
    if data['涨跌幅'] >= 9.5:
        status = "🚀 涨停"
    elif data['涨跌幅'] >= 5:
        status = "📈 大幅上涨"
    elif data['涨跌幅'] >= 2:
        status = "✅ 温和上涨"
    elif data['涨跌幅'] >= 0:
        status = "📊 微幅上涨"
    elif data['涨跌幅'] >= -2:
        status = "📉 微幅下跌"
    elif data['涨跌幅'] >= -5:
        status = "❌ 温和下跌"
    elif data['涨跌幅'] >= -9.5:
        status = "💥 大幅下跌"
    else:
        status = "💣 跌停"
    
    print(f"   当日状态: {status}")
    
    # 4. 成交量分析
    print(f"\n📊 【成交分析】")
    print(f"   成交量: {data['成交量']:,} 手")
    print(f"   成交额: ¥{data['成交额']:,.0f}")
    
    if '换手率' in data and data['换手率'] > 0:
        print(f"   换手率: {data['换手率']:.2f}%")
    
    if '振幅' in data and data['振幅'] > 0:
        print(f"   振幅: {data['振幅']:.2f}%")
    
    # 成交量活跃度判断
    if '换手率' in data:
        if data['换手率'] > 15:
            activity = "🔥 极度活跃"
        elif data['换手率'] > 8:
            activity = "📊 较为活跃"
        elif data['换手率'] > 3:
            activity = "💤 正常交易"
        elif data['换手率'] > 1:
            activity = "😴 交易清淡"
        else:
            activity = "🪨 极度冷清"
        
        print(f"   成交活跃度: {activity}")
    
    # 5. K线形态分析
    print(f"\n📉 【K线形态分析】")
    
    close_price = data['收盘价']
    open_price = data['开盘价']
    high_price = data['最高价']
    low_price = data['最低价']
    
    # K线颜色
    if close_price > open_price:
        candle_color = "🟢 阳线"
        candle_type = "上涨"
    elif close_price < open_price:
        candle_color = "🔴 阴线"
        candle_type = "下跌"
    else:
        candle_color = "➖ 十字星"
        candle_type = "平盘"
    
    print(f"   K线形态: {candle_color} ({candle_type})")
    
    # 影线分析
    upper_shadow = high_price - max(open_price, close_price)
    lower_shadow = min(open_price, close_price) - low_price
    body_size = abs(close_price - open_price)
    
    print(f"   上影线: ¥{upper_shadow:.2f}")
    print(f"   下影线: ¥{lower_shadow:.2f}")
    print(f"   实体大小: ¥{body_size:.2f}")
    
    # 影线意义分析
    if upper_shadow > body_size * 2:
        print(f"   📈 长上影线: 上方抛压较重")
    elif upper_shadow > body_size:
        print(f"   📊 中上影线: 上方有一定压力")
    
    if lower_shadow > body_size * 2:
        print(f"   📉 长下影线: 下方有较强支撑")
    elif lower_shadow > body_size:
        print(f"   📊 中下影线: 下方有一定支撑")
    
    # 6. 市值和估值分析（如果有数据）
    print(f"\n💰 【市值分析】")
    
    # 计算市值（基于收盘价和流通股数估算）
    # 假设603696总股本约为20亿股（需要真实数据）
    estimated_shares = 2e9  # 20亿股
    market_cap = data['收盘价'] * estimated_shares / 1e8  # 转换为亿元
    
    print(f"   估算总市值: ¥{market_cap:.1f} 亿元")
    print(f"   当日成交额占比: {(data['成交额'] / (market_cap * 1e8) * 100):.3f}%")
    
    # 7. 投资建议
    print("\n" + "="*80)
    print("🎯 【投资建议与风险提示】")
    print("="*80)
    
    recommendations = []
    
    # 基于涨跌幅的建议
    if data['涨跌幅'] > 5:
        recommendations.append("⚠️  涨幅较大，注意短期回调风险")
        recommendations.append("📊 观察次日量能变化，谨防冲高回落")
    elif data['涨跌幅'] > 2:
        recommendations.append("✅ 温和上涨，走势相对健康")
        recommendations.append("📈 关注后续量能配合情况")
    elif data['涨跌幅'] > -2:
        recommendations.append("📊 小幅波动，走势平稳")
        recommendations.append("💡 可继续持有观察")
    elif data['涨跌幅'] > -5:
        recommendations.append("❌ 温和下跌，关注支撑位")
        recommendations.append("🔍 观察是否有止跌迹象")
    else:
        recommendations.append("💥 大幅下跌，谨慎观望")
        recommendations.append("⚠️  避免盲目抄底")
    
    # 基于成交量的建议
    if '换手率' in data:
        if data['换手率'] > 10:
            recommendations.append("🔥 高换手率，资金关注度高")
            recommendations.append("📊 适合短线交易者参与")
        elif data['换手率'] < 1:
            recommendations.append("💤 低换手率，流动性较差")
            recommendations.append("⏰ 不适合短线交易")
    
    # 基于K线形态的建议
    if upper_shadow > body_size * 1.5:
        recommendations.append("📈 长上影线显示上方压力较大")
    if lower_shadow > body_size * 1.5:
        recommendations.append("📉 长下影线显示下方支撑较强")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # 8. 风险提示
    print(f"\n⚠️  【风险提示】")
    print(f"   1. 以上分析基于当日数据，不构成投资建议")
    print(f"   2. 股市有风险，投资需谨慎")
    print(f"   3. 建议结合基本面和技术面综合分析")
    print(f"   4. 注意控制仓位，设置止损位")
    
    return data

def save_analysis_report(data):
    """
    保存分析报告到文件
    """
    if not data:
        return None
    
    # 保存详细数据
    filename = f"603696_{data['交易日期'].replace('-', '')}_detailed_analysis.csv"
    filepath = f"/Users/huangchuang/Downloads/金融数据分析/{filename}"
    
    # 创建详细的数据框
    df = pd.DataFrame([data])
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"\n📄 详细分析报告已保存至: {filepath}")
    return filepath

if __name__ == "__main__":
    print("🚀 开始获取603696海南矿业在2024年8月22日的真实交易数据...")
    
    # 获取真实数据
    stock_data = get_real_stock_data_603696()
    
    if stock_data:
        # 分析数据
        analyzed_data = analyze_603696_data(stock_data)
        
        # 保存报告
        save_analysis_report(analyzed_data)
        
        print("\n✅ 真实数据分析完成！")
    else:
        print("\n❌ 无法获取真实数据，请检查网络连接或安装akshare库")
        print("💡 解决方案：")
        print("   1. 安装akshare: pip install akshare")
        print("   2. 检查网络连接")
        print("   3. 确认8月22日是否为交易日")