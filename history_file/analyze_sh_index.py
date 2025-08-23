import pandas as pd
import os
from datetime import datetime
from tabulate import tabulate

def analyze_sh_index_unique_points():
    """
    分析上证指数历史数据，将收盘价转为整型后除以100得到两位数点数，
    输出不重复的点数序列
    """
    # 读取CSV文件
    file_path = "/Users/huangchuang/Downloads/金融数据分析/上证指数历史数据.csv"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        # 读取数据
        df = pd.read_csv(file_path)
        
        # 检查必要列是否存在
        if '收盘价' not in df.columns or '日期' not in df.columns:
            print("CSV文件缺少必要的'收盘价'或'日期'列")
            return
        
        # 处理收盘价：转为整型后除以100得到两位数点数
        df['点数'] = (df['收盘价'].astype(int) // 100)
        
        # 存储不重复的点数序列
        unique_points = []
        previous_point = None
        
        print("上证指数不重复点数序列:")
        print("=" * 40)
        
        # 遍历数据，输出不重复的点数
        for index, row in df.iterrows():
            current_point = row['点数']
            date = row['日期']
            
            # 如果与前面的点数不同，则输出
            if current_point != previous_point:
                unique_points.append({
                    '日期': date,
                    '收盘价': row['收盘价'],
                    '点数': current_point
                })
                print(f"日期: {date}, 收盘价: {row['收盘价']:.2f}, 点数: {current_point:02d}")
                previous_point = current_point
        
        print("=" * 40)
        print(f"总数据条数: {len(df)}")
        print(f"不重复点数序列长度: {len(unique_points)}")
        
        return unique_points
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        return None

def analyze_sh_index_with_details():
    """
    增强版分析函数，包含更多统计信息，计算交易天数并以表格形式输出
    """
    file_path = "/Users/huangchuang/Downloads/金融数据分析/上证指数历史数据.csv"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        df = pd.read_csv(file_path)
        
        # 计算点数
        df['点数'] = (df['收盘价'].astype(int) // 100)
        
        # 转换日期格式为datetime
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期')
        
        # 获取不重复的点数序列
        unique_points = []
        previous_point = None
        previous_date = None
        
        for _, row in df.iterrows():
            current_point = row['点数']
            current_date = row['日期']
            
            if current_point != previous_point:
                # 计算与上一个日期之间的天数（包括周末）
                days_between = 0
                if previous_date is not None:
                    days_between = (current_date - previous_date).days
                
                unique_points.append({
                    '序号': len(unique_points) + 1,
                    '日期': current_date.strftime('%Y-%m-%d'),
                    '收盘价': row['收盘价'],
                    '点数': current_point,
                    '距上次天数': days_between
                })
                previous_point = current_point
                previous_date = current_date
        
        # 创建表格数据
        table_data = []
        headers = ['序号', '日期', '收盘价', '点数', '距上次天数']
        
        for item in unique_points:
            table_data.append([
                item['序号'],
                item['日期'],
                f"{item['收盘价']:.2f}",
                f"{item['点数']:02d}",
                str(item['距上次天数'])
            ])
        
        # 输出统计信息
        print("上证指数点数变化分析:")
        print("=" * 80)
        print(f"数据时间范围: {df['日期'].min().strftime('%Y-%m-%d')} 到 {df['日期'].max().strftime('%Y-%m-%d')}")
        print(f"总交易日数: {len(df)}")
        print(f"不重复点数个数: {len(unique_points)}")
        print(f"最低点数: {min([p['点数'] for p in unique_points])}")
        print(f"最高点数: {max([p['点数'] for p in unique_points])}")
        print()
        
        # 输出表格
        print("上证指数不重复点数序列（含交易天数统计）:")
        print("=" * 80)
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # 保存结果到CSV文件
        output_df = pd.DataFrame(unique_points)
        output_file = "/Users/huangchuang/Downloads/金融数据分析/上证指数不重复点数序列.csv"
        output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到: {output_file}")
        
        return unique_points
        
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        return None

if __name__ == "__main__":
    # 运行分析
    print("开始分析上证指数数据...")
    print()
    
    # 详细分析（包含交易天数和表格输出）
    detailed_points = analyze_sh_index_with_details()