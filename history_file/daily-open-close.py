import akshare as ak
import pandas as pd
from datetime import datetime, timedelta



def get_index_daily_price(index_symbol, index_name, start_date, end_date):
    """获取大盘指数的每日开盘价和收盘价"""
    try:
        index_df = ak.index_zh_a_hist(
            symbol=index_symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date
        )
        
        if index_df.empty:
            return None
            
        daily_data = index_df[['日期', '开盘', '收盘']].copy()
        daily_data['指数代码'] = index_symbol
        daily_data['指数名称'] = index_name
        daily_data = daily_data[['指数代码', '指数名称', '日期', '开盘', '收盘']]
        daily_data.columns = ['指数代码', '指数名称', '日期', '开盘价', '收盘价']
        
        print(f"成功获取{index_name}({index_symbol})的开盘价和收盘价数据，共 {len(daily_data)} 条记录")
        return daily_data
        
    except Exception as e:
        print(f"获取{index_name}({index_symbol})数据时出错: {str(e)}")
        return None

def calculate_100_point_breakthroughs(shanghai_data):
    """计算上证指数每突破100点所用的时间"""
    if shanghai_data is None or shanghai_data.empty:
        return []
    
    # 按日期排序
    shanghai_data = shanghai_data.sort_values('日期').reset_index(drop=True)
    
    # 获取收盘价数据
    closing_prices = shanghai_data['收盘价'].values
    dates = pd.to_datetime(shanghai_data['日期'])
    
    breakthroughs = []
    current_level = 0
    
    # 从3000点开始计算（避免早期数据影响）
    start_index = 0
    for i, price in enumerate(closing_prices):
        if price >= 3000:
            start_index = i
            break
    
    if start_index == 0 and closing_prices[0] < 3000:
        print("数据中没有找到3000点以上的记录")
        return breakthroughs
    
    # 计算每次突破100点整数位所用时间
    for i in range(start_index, len(closing_prices)):
        price = closing_prices[i]
        target_level = (int(price) // 100) * 100
        
        if target_level > current_level and target_level % 100 == 0:
            # 找到上一次在这个100点以下的位置
            prev_below = None
            for j in range(i-1, -1, -1):
                if closing_prices[j] < target_level:
                    prev_below = j
                    break
            
            if prev_below is not None:
                days_taken = (dates[i] - dates[prev_below]).days
                breakthroughs.append({
                    '突破点位': target_level,
                    '突破日期': dates[i].strftime('%Y-%m-%d'),
                    '收盘价': price,
                    '用时天数': days_taken,
                    '起始点位': closing_prices[prev_below],
                    '起始日期': dates[prev_below].strftime('%Y-%m-%d')
                })
                current_level = target_level
    
    return breakthroughs

def main():
    # 设置较长的日期范围（获取历史数据）
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=7650)).strftime('%Y%m%d')  # 10年数据
    
    print(f"开始获取上证指数历史数据并计算100点突破时间")
    print(f"日期范围: {start_date} 到 {end_date}")
    
    # 获取上证指数数据
    shanghai_data = get_index_daily_price('000001', '上证指数', start_date, end_date)
    
    if shanghai_data is not None and not shanghai_data.empty:
        # 计算100点突破时间
        breakthroughs = calculate_100_point_breakthroughs(shanghai_data)
        
        if breakthroughs:
            # 创建DataFrame
            breakthrough_df = pd.DataFrame(breakthroughs)
            
            # 保存突破数据
            output_file = '/Users/huangchuang/Downloads/金融数据分析/上证指数100点突破时间统计.csv'
            breakthrough_df.to_csv(output_file, index=False, encoding='utf_8_sig')
            
            print(f"\n100点突破时间统计完成！")
            print(f"共找到 {len(breakthroughs)} 次100点突破")
            print(f"数据已保存到: {output_file}")
            
            # 显示统计结果
            print("\n100点突破时间统计:")
            print(breakthrough_df.to_string(index=False))
            
            # 计算平均用时
            avg_days = breakthrough_df['用时天数'].mean()
            print(f"\n平均每次突破100点用时: {avg_days:.1f} 天")
            
            # 保存完整的上证指数数据
            full_output_file = '/Users/huangchuang/Downloads/金融数据分析/上证指数历史数据.csv'
            shanghai_data.to_csv(full_output_file, index=False, encoding='utf_8_sig')
            print(f"完整历史数据已保存到: {full_output_file}")
            
        else:
            print("未找到100点突破记录")
    else:
        print("无法获取上证指数数据")

if __name__ == "__main__":
    main()