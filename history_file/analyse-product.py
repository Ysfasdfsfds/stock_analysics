import akshare as ak
from scipy import stats
import pandas as pd
import concurrent.futures

# 获取上证A股实时行情数据
stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()

# 打印列名
print(stock_sh_a_spot_em_df.columns)

# # 筛选换手率在1%到5%之间且最新价在10到60之间的股票
# low_turnover_stocks = stock_sh_a_spot_em_df[
#     (stock_sh_a_spot_em_df['换手率'] < 5) & 
#     (stock_sh_a_spot_em_df['换手率'] > 1) &
#     (stock_sh_a_spot_em_df['最新价'] > 10) &
#     (stock_sh_a_spot_em_df['最新价'] < 60) &
#     (stock_sh_a_spot_em_df['流通市值'] > 10000000000)  # 100亿元
# ].copy()

# # 按换手率升序排序
# low_turnover_stocks = low_turnover_stocks.sort_values('换手率')

# # 显示结果，只展示关键信息
# result = low_turnover_stocks[['代码', '名称', '最新价', '换手率', '涨跌幅', '振幅', '总市值', '流通市值', '市盈率-动态', '市净率']]

# # 将市值从元转换为亿元
# result['总市值'] = result['总市值'] / 100000000
# result['流通市值'] = result['流通市值'] / 100000000

# print('\n换手率在1%到5%之间的股票：')
# print(f'共找到 {len(result)} 只股票\n')

def get_pe_stats(symbol):
    """获取指定股票的PE(TTM)值和分位数"""
    try:
        pe_data = ak.stock_value_em(symbol=symbol)
        if pe_data is None or len(pe_data) == 0:
            return None, None
        current_pe = pe_data.iloc[-1]['PE(TTM)']
        pe_percentile = stats.percentileofscore(pe_data['PE(TTM)'], current_pe)
        print(f"成功获取{symbol}的PE数据，当前PE为: {current_pe}, 分位数为: {pe_percentile}")
        return current_pe, pe_percentile
    except Exception as e:
        print(f"获取{symbol}的PE数据时出错: {str(e)}")
        return None, None


def get_stock_industry(symbol):
    """通过股票代码获取行业信息"""
    try:
        info_df = ak.stock_individual_info_em(symbol=symbol)
        industry = info_df.iloc[7][1]  # 行业信息在第7行
        print(f"成功获取股票{symbol}的行业信息，行业为: {industry}")
        return industry
    except Exception as e:
        print(f"获取股票{symbol}行业信息时出错: {str(e)}")
        return None

# 获取所有股票数据
all_stocks = stock_sh_a_spot_em_df.copy()

# 为每只股票添加PE分位数和行业信息
results = []
def process_stock(stock):
    try:
        # print(stock)
        pe, percentile = get_pe_stats(stock.代码)
        industry = get_stock_industry(stock.代码)
        return {
            '代码': stock.代码,
            '名称': stock.名称,
            '最新价': stock.最新价,
            '涨跌幅': stock.涨跌幅,
            '涨跌额': stock.涨跌额,
            '成交量': stock.成交量,
            '成交额': stock.成交额,
            '振幅': stock.振幅,
            '最高': stock.最高,
            '最低': stock.最低,
            '今开': stock.今开,
            '昨收': stock.昨收,
            '量比': stock.量比,
            '换手率': stock.换手率,
            '市净率': stock.市净率,
            '总市值': stock.总市值 / 100000000,
            '流通市值': stock.流通市值 / 100000000,
            '涨速': stock.涨速,
            '5分钟涨跌': stock._21,
            '60日涨跌幅': stock._22,
            '年初至今涨跌幅': stock.年初至今涨跌幅,
            'PE(TTM)': pe,
            'PE分位数(%)': percentile,
            '行业': industry
        }
    except Exception as e:
        print(f"处理股票{stock.代码} {stock.名称}时出错: {str(e)}")
        return None

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    futures = []
    for i, stock in enumerate(all_stocks.itertuples()):
        print(f"正在处理股票代码: {stock.代码} ({i+1}/{len(all_stocks)})")
        futures.append(executor.submit(process_stock, stock))
    
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            results.append(result)

# 保存为CSV文件
df = pd.DataFrame(results)
df.to_csv('/Users/huangchuang/Downloads/金融数据分析/股票完整数据.csv', index=False, encoding='utf_8_sig')
print('\n所有股票数据已保存到: /Users/huangchuang/Downloads/金融数据分析/股票完整数据.csv')


