import akshare as ak
from scipy import stats
import pandas as pd

# 获取上证A股实时行情数据
stock_sh_a_spot_em_df = ak.stock_sh_a_spot_em()

# 打印列名
print(stock_sh_a_spot_em_df.columns)

# 筛选换手率在1%到5%之间且最新价在10到60之间的股票
low_turnover_stocks = stock_sh_a_spot_em_df[
    (stock_sh_a_spot_em_df['换手率'] < 5) & 
    (stock_sh_a_spot_em_df['换手率'] > 1) &
    (stock_sh_a_spot_em_df['最新价'] > 10) &
    (stock_sh_a_spot_em_df['最新价'] < 60) &
    (stock_sh_a_spot_em_df['流通市值'] > 10000000000)  # 100亿元
].copy()

# 按换手率升序排序
low_turnover_stocks = low_turnover_stocks.sort_values('换手率')

# 显示结果，只展示关键信息
result = low_turnover_stocks[['代码', '名称', '最新价', '换手率', '涨跌幅', '振幅', '总市值', '流通市值', '市盈率-动态', '市净率']]

# 将市值从元转换为亿元
result['总市值'] = result['总市值'] / 100000000
result['流通市值'] = result['流通市值'] / 100000000

print('\n换手率在1%到5%之间的股票：')
print(f'共找到 {len(result)} 只股票\n')

# def get_pe_stats(symbol):
#     """获取指定股票的PE(TTM)值和分位数"""
#     try:
#         pe_data = ak.stock_value_em(symbol=symbol)
#         if pe_data is None or len(pe_data) == 0:
#             return None, None
#         current_pe = pe_data.iloc[-1]['PE(TTM)']
#         pe_percentile = stats.percentileofscore(pe_data['PE(TTM)'], current_pe)
#         return current_pe, pe_percentile
#     except Exception as e:
#         print(f"获取{symbol}的PE数据时出错: {str(e)}")
#         return None, None

# # 为每只股票获取PE信息
# results = []
# for stock in result.itertuples():
#     pe, percentile = get_pe_stats(stock.代码)
#     print(f'股票代码: {stock.代码}, 名称: {stock.名称}, PE(TTM): {pe:.2f}, 分位数: {percentile:.1f}%')
#     results.append({
#         '代码': stock.代码,
#         '名称': stock.名称,
#         'PE(TTM)': pe,
#         '分位数(%)': percentile
#     })

# # 保存为CSV文件
# df = pd.DataFrame(results)
# df.to_csv('/Users/huangchuang/Downloads/金融数据分析/上证筛选结果.csv', index=False, encoding='utf_8_sig')
# print('\n筛选结果已保存到: /Users/huangchuang/Downloads/金融数据分析/筛选结果.csv')
# # 格式化输出
# formatted = result.head(10).copy()
# formatted['最新价'] = formatted['最新价'].map('{:.2f}'.format)
# formatted['换手率'] = formatted['换手率'].map('{:.2f}%'.format)
# formatted['涨跌幅'] = formatted['涨跌幅'].map('{:.2f}%'.format)
# formatted['振幅'] = formatted['振幅'].map('{:.2f}%'.format)
# formatted['总市值'] = formatted['总市值'].map('{:.2f}亿'.format)
# formatted['流通市值'] = formatted['流通市值'].map('{:.2f}亿'.format)

# print(formatted.to_string(index=False, justify='center'))
stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
print(stock_individual_info_em_df)

# 筛选最近一个月的数据
# last_month = pe_data[pe_data['数据日期'].dt.date >= (pd.to_datetime('today') - pd.Timedelta(days=30)).date()]

# 计算当前PE在所有历史数据中的分位数
# current_pe = pe_data.iloc[-1]['PE(TTM)']
# pe_percentile = stats.percentileofscore(pe_data['PE(TTM)'], current_pe)

# print(f'\n当前PE(TTM): {current_pe:.2f}')
# print(f'在所有历史数据中的分位数: {pe_percentile:.1f}%')

# 计算最近一个月PE的分位数
# last_month_percentile = stats.percentileofscore(last_month['pe'], current_pe)
# print(f'在最近一个月数据中的分位数: {last_month_percentile:.1f}%')
# 保存恒瑞医药的历史市盈率数据为 CSV 文件
# pe_data.to_csv('/Users/huangchuang/Downloads/金融数据分析/恒瑞医药历史市盈率数据.csv', index=False, encoding='utf_8_sig')


