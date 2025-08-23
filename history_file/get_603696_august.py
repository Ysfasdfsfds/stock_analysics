import akshare as ak
import pandas as pd
from datetime import datetime
import time

def check_akshare_version():
    """检查akshare版本"""
    try:
        version = ak.__version__
        print(f"当前akshare版本: {version}")
        return version
    except:
        print("无法获取akshare版本信息")
        return None

def get_available_tick_functions():
    """获取可用的逐笔交易相关函数"""
    tick_functions = []
    possible_functions = [
        'stock_zh_a_tick_tx',
        'stock_zh_a_tick_tx_js',
        'stock_individual_detail_em',
        'stock_zh_a_tick_163',
        'stock_zh_a_tick_tx_sina',
        'tool_individual_detail'
    ]
    
    for func_name in possible_functions:
        if hasattr(ak, func_name):
            tick_functions.append(func_name)
    
    return tick_functions

def get_stock_tick_data_v1(stock_code):
    """方法1：使用stock_zh_a_tick_tx"""
    try:
        if len(stock_code) == 6:
            if stock_code.startswith(('0', '3')):
                formatted_code = f"sz{stock_code}"
            elif stock_code.startswith('6'):
                formatted_code = f"sh{stock_code}"
            else:
                formatted_code = stock_code
        else:
            formatted_code = stock_code.lower()
        
        tick_data = ak.stock_zh_a_tick_tx(symbol=formatted_code)
        return tick_data, "stock_zh_a_tick_tx"
    except Exception as e:
        print(f"方法1失败: {e}")
        return None, None

def get_stock_tick_data_v2(stock_code):
    """方法2：使用stock_individual_detail_em"""
    try:
        tick_data = ak.stock_individual_detail_em(symbol=stock_code)
        return tick_data, "stock_individual_detail_em"
    except Exception as e:
        print(f"方法2失败: {e}")
        return None, None

def get_stock_tick_data_v3(stock_code):
    """方法3：使用分时数据作为替代"""
    try:
        # 获取1分钟级别的分时数据
        tick_data = ak.stock_zh_a_hist_min_em(symbol=stock_code, period="1", adjust="")
        return tick_data, "stock_zh_a_hist_min_em (1分钟)"
    except Exception as e:
        print(f"方法3失败: {e}")
        return None, None

def get_stock_tick_data_v4(stock_code):
    """方法4：使用实时行情数据"""
    try:
        # 获取实时行情
        spot_data = ak.stock_zh_a_spot_em()
        if stock_code in spot_data['代码'].values:
            stock_info = spot_data[spot_data['代码'] == stock_code]
            return stock_info, "stock_zh_a_spot_em (实时行情)"
        else:
            return None, None
    except Exception as e:
        print(f"方法4失败: {e}")
        return None, None

def get_stock_tick_data(stock_code, max_retries=3, delay=1):
    """
    获取指定股票的交易数据（尝试多种方法）
    
    参数:
    stock_code (str): 股票代码，如 '000001'
    max_retries (int): 最大重试次数
    delay (int): 重试间隔时间（秒）
    
    返回:
    tuple: (pandas.DataFrame, method_used) 交易数据和使用的方法
    """
    
    print(f"正在获取股票 {stock_code} 的交易数据...")
    
    # 检查版本和可用函数
    check_akshare_version()
    available_functions = get_available_tick_functions()
    print(f"可用的相关函数: {available_functions}")
    
    # 尝试不同的方法
    methods = [
        get_stock_tick_data_v1,
        get_stock_tick_data_v2,
        get_stock_tick_data_v3,
        get_stock_tick_data_v4
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\n尝试方法 {i}...")
        for attempt in range(max_retries):
            try:
                tick_data, method_name = method(stock_code)
                
                if tick_data is not None and not tick_data.empty:
                    print(f"成功使用 {method_name} 获取 {len(tick_data)} 条记录")
                    return tick_data, method_name
                else:
                    print(f"方法 {i} 第 {attempt + 1} 次尝试：未获取到数据")
                    
            except Exception as e:
                print(f"方法 {i} 第 {attempt + 1} 次尝试失败：{e}")
                
            if attempt < max_retries - 1:
                print(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
    
    print("所有方法都失败了，请检查股票代码、akshare版本或网络连接")
    return None, None

def analyze_data(data, method_name):
    """
    分析交易数据
    
    参数:
    data (pandas.DataFrame): 交易数据
    method_name (str): 使用的方法名称
    """
    if data is None or data.empty:
        print("没有数据可以分析")
        return
    
    print(f"\n=== 交易数据分析 (使用方法: {method_name}) ===")
    print(f"数据条数: {len(data)}")
    print(f"数据列: {list(data.columns)}")
    print(f"数据形状: {data.shape}")
    
    # 显示前几行数据
    print(f"\n=== 数据预览 ===")
    print(data.head())
    
    # 根据不同的数据类型进行分析
    if "stock_zh_a_hist_min_em" in method_name:
        # 分时数据分析
        if '收盘' in data.columns:
            print(f"\n价格范围: {data['收盘'].min():.2f} - {data['收盘'].max():.2f}")
            print(f"平均价格: {data['收盘'].mean():.2f}")
        if '成交量' in data.columns:
            print(f"总成交量: {data['成交量'].sum():,}")
        if '成交额' in data.columns:
            print(f"总成交额: {data['成交额'].sum():,.2f}")
    
    elif "stock_zh_a_spot_em" in method_name:
        # 实时行情数据分析
        if '最新价' in data.columns:
            print(f"\n当前价格: {data['最新价'].iloc[0]}")
        if '涨跌幅' in data.columns:
            print(f"涨跌幅: {data['涨跌幅'].iloc[0]}%")
        if '成交量' in data.columns:
            print(f"成交量: {data['成交量'].iloc[0]:,}")

def save_data(data, stock_code, method_name, file_format='csv'):
    """
    保存交易数据到文件
    
    参数:
    data (pandas.DataFrame): 交易数据
    stock_code (str): 股票代码
    method_name (str): 使用的方法名称
    file_format (str): 文件格式 'csv' 或 'excel'
    """
    if data is None or data.empty:
        print("没有数据可以保存")
        return
    
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    method_short = method_name.split('(')[0].replace('_', '')
    
    if file_format.lower() == 'csv':
        filename = f"{stock_code}_{method_short}_{current_date}.csv"
        data.to_csv(filename, encoding='utf-8-sig', index=True)
        print(f"数据已保存到: {filename}")
    elif file_format.lower() == 'excel':
        filename = f"{stock_code}_{method_short}_{current_date}.xlsx"
        data.to_excel(filename, index=True)
        print(f"数据已保存到: {filename}")

# 主程序
if __name__ == "__main__":
    # 示例：获取平安银行(000001)的交易数据
    stock_code = "601288"  # 可以修改为其他股票代码
    
    print("=== 股票交易数据获取工具 ===")
    print("支持多种数据获取方式，自动尝试最适合的方法\n")
    
    # 获取数据
    tick_data, method_used = get_stock_tick_data(stock_code)
    
    if tick_data is not None:
        # 分析数据
        analyze_data(tick_data, method_used)
        
        # 询问是否保存数据
        save_choice = input("\n是否保存数据到文件? (y/n): ").lower()
        if save_choice == 'y':
            format_choice = input("选择文件格式 (csv/excel): ").lower()
            save_data(tick_data, stock_code, method_used, format_choice)
    
    print("\n程序执行完毕")
    
    # 提示如何更新akshare
    print("\n=== 提示 ===")
    print("如果遇到接口不可用的问题，可以尝试更新akshare:")
    print("pip install akshare --upgrade")
    print("或指定特定版本:")
    print("pip install akshare==1.12.0")