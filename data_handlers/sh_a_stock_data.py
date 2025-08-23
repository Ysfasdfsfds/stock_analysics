#!/usr/bin/env python3
"""
上证A股实时行情数据处理器
基于akshare库获取上证A股实时行情数据
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import akshare as ak
import requests
from datetime import datetime
import time
import sqlite3
import os
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class SHAStockDataHandler:
    """上证A股数据处理类"""
    
    def __init__(self):
        import os
        
        self.cache_timeout = 60  # 缓存60秒
        self.last_update = None
        self.cached_data = None
        
        # 从环境变量读取超时配置
        self.request_timeout = int(os.environ.get('STOCK_DATA_TIMEOUT', 120))  # 请求超时时间(秒)
        self.max_retries = int(os.environ.get('STOCK_DATA_RETRIES', 3))  # 最大重试次数
        self.retry_delay = int(os.environ.get('STOCK_DATA_RETRY_DELAY', 2))  # 重试间隔(秒)
        
        # 缓存配置
        self.cache_max_age_minutes = int(os.environ.get('CACHE_MAX_AGE_MINUTES', 360))
        self.cache_cleanup_hours = int(os.environ.get('CACHE_CLEANUP_HOURS', 24))
        
        # 数据库配置
        self.db_path = self._get_db_path()
        self._init_database()
        
        logger.info(f"股票数据处理器配置: timeout={self.request_timeout}s, retries={self.max_retries}, retry_delay={self.retry_delay}s")
        logger.info(f"数据库路径: {self.db_path}")
        logger.info(f"SQLite缓存配置: 数据库路径={self.db_path}, 缓存有效期={self.cache_max_age_minutes}分钟, 清理周期={self.cache_cleanup_hours}小时")
        logger.info("股票数据字段已完整映射: 包含序号、代码、名称、最新价、涨跌幅、涨跌额、成交量、成交额、振幅、最高、最低、今开、昨收、量比、换手率、市盈率-动态、市净率、总市值、流通市值、涨速、5分钟涨跌、60日涨跌幅、年初至今涨跌幅等全部字段")
    
    def _get_db_path(self) -> str:
        """获取数据库文件路径"""
        project_root = Path(__file__).parent.parent
        db_dir = project_root / 'data'
        db_dir.mkdir(exist_ok=True)
        return str(db_dir / 'stock_cache.db')
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建股票数据缓存表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_data_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL,
                        name TEXT NOT NULL,
                        latest_price REAL,
                        change_percent REAL,
                        change_amount REAL,
                        volume INTEGER,
                        amount REAL,
                        amplitude REAL,
                        high REAL,
                        low REAL,
                        open_price REAL,
                        close_price REAL,
                        volume_ratio REAL,
                        turnover_rate REAL,
                        pe_ratio REAL,
                        pb_ratio REAL,
                        total_market_cap REAL,
                        circulation_market_cap REAL,
                        speed REAL,
                        change_5min REAL,
                        change_60day REAL,
                        change_ytd REAL,
                        timestamp TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(code, timestamp)
                    )
                ''')
                
                # 创建索引以提高查询性能
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_code_timestamp 
                    ON stock_data_cache(code, timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON stock_data_cache(timestamp)
                ''')
                
                conn.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise
    
    def get_realtime_sh_a_stocks(self) -> Optional[List[Dict]]:
        """
        获取上证A股实时行情数据，优先使用缓存
        
        Returns:
            上证A股实时行情数据列表
        """
        try:
            # 清理过期缓存
            self._clear_old_cache()
            
            # 首先尝试从缓存加载
            cached_stocks = self._load_from_cache(max_age_minutes=self.cache_max_age_minutes)
            if cached_stocks is not None and len(cached_stocks) > 0:
                logger.info(f"使用缓存的股票数据（{self.cache_max_age_minutes}分钟内）")
                return cached_stocks
                self.last_update = datetime.now()
                return cached_stocks
            
            # 缓存中没有，从原始接口获取
            logger.info("缓存中没有有效数据，从原始接口获取")
            stock_df = self._fetch_with_retry()
            
            if stock_df is None or stock_df.empty:
                logger.warning("获取到的股票数据为空")
                return None
            
            # 转换数据格式
            result = []
            for _, row in stock_df.iterrows():
                stock_data = {
                    'code': str(row['代码']),
                    'name': str(row['名称']),
                    'latest_price': float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                    'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                    'change_amount': float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0.0,
                    'volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                    'amount': float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                    'amplitude': float(row['振幅']) if pd.notna(row['振幅']) else 0.0,
                    'high': float(row['最高']) if pd.notna(row['最高']) else 0.0,
                    'low': float(row['最低']) if pd.notna(row['最低']) else 0.0,
                    'open': float(row['今开']) if pd.notna(row['今开']) else 0.0,
                    'close': float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                    'volume_ratio': float(row['量比']) if pd.notna(row['量比']) else 0.0,
                    'turnover_rate': float(row['换手率']) if pd.notna(row['换手率']) else 0.0,
                    'pe_ratio': float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else 0.0,
                    'pb_ratio': float(row['市净率']) if pd.notna(row['市净率']) else 0.0,
                    'total_market_cap': float(row['总市值']) / 100000000 if pd.notna(row['总市值']) else 0.0,  # 转换为亿元
                    'circulation_market_cap': float(row['流通市值']) / 100000000 if pd.notna(row['流通市值']) else 0.0,  # 转换为亿元
                    'speed': float(row['涨速']) if pd.notna(row['涨速']) else 0.0,
                    'change_5min': float(row['5分钟涨跌']) if pd.notna(row['5分钟涨跌']) else 0.0,
                    'change_60day': float(row['60日涨跌幅']) if pd.notna(row['60日涨跌幅']) else 0.0,
                    'change_ytd': float(row['年初至今涨跌幅']) if pd.notna(row['年初至今涨跌幅']) else 0.0,
                    'timestamp': datetime.now().isoformat()
                }
                result.append(stock_data)
            
            # 保存到缓存
            if result:
                self._save_to_cache(result)
            
            self.cached_data = result
            self.last_update = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"获取上证A股实时行情数据失败: {str(e)}")
            return None
    
    def _fetch_with_retry(self) -> Optional[pd.DataFrame]:
        """
        使用重试机制获取股票数据，增加超时时间
        
        Returns:
            股票数据DataFrame或None
        """
        import warnings
        warnings.filterwarnings('ignore')
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"尝试获取上证A股实时数据，第 {attempt + 1} 次尝试")
                
                # 设置全局超时时间
                import socket
                socket.setdefaulttimeout(self.request_timeout)
                
                # 获取数据
                stock_df = ak.stock_sh_a_spot_em()
                
                if stock_df is not None and not stock_df.empty:
                    logger.info(f"成功获取上证A股实时数据，共 {len(stock_df)} 条记录")
                    return stock_df
                else:
                    logger.warning(f"第 {attempt + 1} 次尝试：获取到的数据为空")
                    
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次尝试失败: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"所有 {self.max_retries} 次尝试均失败")
        
        return None
    
    def _save_to_cache(self, stocks: List[Dict]) -> bool:
        """
        将股票数据保存到数据库缓存
        
        Args:
            stocks: 股票数据列表
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 批量插入数据
                for stock in stocks:
                    cursor.execute('''
                    INSERT OR REPLACE INTO stock_data_cache (
                        code, name, latest_price, change_percent, change_amount,
                        volume, amount, amplitude, high, low,
                        open_price, close_price, volume_ratio, turnover_rate,
                        pe_ratio, pb_ratio, total_market_cap, circulation_market_cap,
                        speed, change_5min, change_60day, change_ytd, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock['code'], stock['name'], stock['latest_price'],
                    stock['change_percent'], stock['change_amount'],
                    stock['volume'], stock['amount'], stock['amplitude'],
                    stock['high'], stock['low'], stock['open'], stock['close'],
                    stock['volume_ratio'], stock['turnover_rate'],
                    stock['pe_ratio'], stock['pb_ratio'], stock['total_market_cap'],
                    stock['circulation_market_cap'], stock['speed'],
                    stock['change_5min'], stock['change_60day'],
                    stock['change_ytd'], stock['timestamp']
                ))
                
                conn.commit()
                logger.info(f"成功保存 {len(stocks)} 条股票数据到缓存")
                return True
                
        except Exception as e:
            logger.error(f"保存数据到缓存失败: {str(e)}")
            return False
    
    def _load_from_cache(self, max_age_minutes: int = 5) -> Optional[List[Dict]]:
        """
        从数据库缓存加载股票数据
        
        Args:
            max_age_minutes: 最大缓存时间（分钟）
            
        Returns:
            股票数据列表或None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 查询最近的数据
                cursor.execute('''
                    SELECT code, name, latest_price, change_percent, change_amount,
                           volume, amount, amplitude, high, low,
                           open_price, close_price, volume_ratio, turnover_rate,
                           pe_ratio, pb_ratio, total_market_cap, circulation_market_cap,
                           speed, change_5min, change_60day, change_ytd, timestamp
                    FROM stock_data_cache
                    WHERE timestamp >= datetime('now', '-{} minutes')
                    ORDER BY code
                '''.format(max_age_minutes))
                
                rows = cursor.fetchall()
                
                if not rows:
                    logger.info("缓存中没有有效的股票数据")
                    return None
                
                # 转换为字典列表
                stocks = []
                for row in rows:
                    stock = {
                        'code': row[0],
                        'name': row[1],
                        'latest_price': row[2],
                        'change_percent': row[3],
                        'change_amount': row[4],
                        'volume': row[5],
                        'amount': row[6],
                        'amplitude': row[7],
                        'high': row[8],
                        'low': row[9],
                        'open': row[10],
                        'close': row[11],
                        'volume_ratio': row[12],
                        'turnover_rate': row[13],
                        'pe_ratio': row[14],
                        'pb_ratio': row[15],
                        'total_market_cap': row[16],
                        'circulation_market_cap': row[17],
                        'speed': row[18],
                        'change_5min': row[19],
                        'change_60day': row[20],
                        'change_ytd': row[21],
                        'timestamp': row[22]
                    }
                    stocks.append(stock)
                
                logger.info(f"从缓存加载了 {len(stocks)} 条股票数据")
                return stocks
                
        except Exception as e:
            logger.error(f"从缓存加载数据失败: {str(e)}")
            return None
    
    def _clear_old_cache(self, max_age_hours: int = 24):
        """
        清理过期的缓存数据
        
        Args:
            max_age_hours: 最大缓存时间（小时）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM stock_data_cache
                    WHERE created_at < datetime('now', '-{} hours')
                '''.format(max_age_hours))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"清理了 {deleted_count} 条过期缓存数据")
                    
        except Exception as e:
            logger.error(f"清理缓存失败: {str(e)}")
    
    def refresh_cache(self) -> bool:
        """
        手动刷新缓存数据
        
        Returns:
            是否刷新成功
        """
        try:
            logger.info("开始手动刷新缓存...")
            
            # 从原始接口获取最新数据
            stock_df = self._fetch_with_retry()
            if stock_df is None or stock_df.empty:
                logger.warning("刷新缓存失败：无法获取最新数据")
                return False
            
            # 转换数据格式
            stocks = []
            for _, row in stock_df.iterrows():
                stock_data = {
                    'code': str(row['代码']),
                    'name': str(row['名称']),
                    'latest_price': float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                    'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                    'change_amount': float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0.0,
                    'volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                    'amount': float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                    'turnover_rate': float(row['换手率']) if pd.notna(row['换手率']) else 0.0,
                    'amplitude': float(row['振幅']) if pd.notna(row['振幅']) else 0.0,
                    'high': float(row['最高']) if pd.notna(row['最高']) else 0.0,
                    'low': float(row['最低']) if pd.notna(row['最低']) else 0.0,
                    'open': float(row['今开']) if pd.notna(row['今开']) else 0.0,
                    'close': float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                    'total_market_cap': float(row['总市值']) / 100000000 if pd.notna(row['总市值']) else 0.0,
                    'circulation_market_cap': float(row['流通市值']) / 100000000 if pd.notna(row['流通市值']) else 0.0,
                    'pe_ratio': float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else 0.0,
                    'pb_ratio': float(row['市净率']) if pd.notna(row['市净率']) else 0.0,
                    'timestamp': datetime.now().isoformat()
                }
                stocks.append(stock_data)
            
            # 保存到缓存
            if stocks:
                success = self._save_to_cache(stocks)
                if success:
                    self.cached_data = stocks
                    self.last_update = datetime.now()
                    logger.info(f"缓存刷新成功，共 {len(stocks)} 条记录")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"刷新缓存失败: {str(e)}")
            return False
    
    def filter_stocks(self, 
                     min_price: float = 0,
                     max_price: float = 1000,
                     min_turnover_rate: float = 0,
                     max_turnover_rate: float = 100,
                     min_market_cap: float = 0,  # 亿元
                     max_market_cap: float = 100000,  # 亿元
                     sort_by: str = 'turnover_rate',
                     ascending: bool = True) -> Optional[List[Dict]]:
        """
        根据条件筛选股票
        
        Args:
            min_price: 最低价格
            max_price: 最高价格
            min_turnover_rate: 最低换手率(%)
            max_turnover_rate: 最高换手率(%)
            min_market_cap: 最低流通市值(亿元)
            max_market_cap: 最高流通市值(亿元)
            sort_by: 排序字段
            ascending: 是否升序
            
        Returns:
            筛选后的股票数据列表
        """
        try:
            # 获取实时数据
            stocks = self.get_realtime_sh_a_stocks()
            if not stocks:
                return None
            
            # 筛选数据
            filtered_stocks = [
                stock for stock in stocks
                if min_price <= stock['latest_price'] <= max_price
                and min_turnover_rate <= stock['turnover_rate'] <= max_turnover_rate
                and min_market_cap <= stock['circulation_market_cap'] <= max_market_cap
            ]
            
            # 排序
            if sort_by in ['latest_price', 'change_percent', 'turnover_rate', 'total_market_cap', 'circulation_market_cap']:
                filtered_stocks.sort(key=lambda x: x[sort_by], reverse=not ascending)
            
            return filtered_stocks
            
        except Exception as e:
            logger.error(f"筛选股票数据失败: {str(e)}")
            return None
    
    def get_stock_by_code(self, code: str) -> Optional[Dict]:
        """
        根据股票代码获取单只股票信息
        
        Args:
            code: 股票代码
            
        Returns:
            股票详细信息
        """
        try:
            stocks = self.get_realtime_sh_a_stocks()
            if not stocks:
                return None
            
            for stock in stocks:
                if stock['code'] == code:
                    return stock
            
            return None
            
        except Exception as e:
            logger.error(f"获取股票 {code} 信息失败: {str(e)}")
            return None
    
    def get_market_summary(self) -> Optional[Dict]:
        """
        获取市场概览信息
        
        Returns:
            市场概览数据
        """
        try:
            stocks = self.get_realtime_sh_a_stocks()
            if not stocks:
                return None
            
            total_stocks = len(stocks)
            up_stocks = len([s for s in stocks if s['change_percent'] > 0])
            down_stocks = len([s for s in stocks if s['change_percent'] < 0])
            flat_stocks = len([s for s in stocks if s['change_percent'] == 0])
            
            avg_turnover_rate = sum(s['turnover_rate'] for s in stocks) / total_stocks
            avg_change_percent = sum(s['change_percent'] for s in stocks) / total_stocks
            
            return {
                'total_stocks': total_stocks,
                'up_stocks': up_stocks,
                'down_stocks': down_stocks,
                'flat_stocks': flat_stocks,
                'avg_turnover_rate': round(avg_turnover_rate, 2),
                'avg_change_percent': round(avg_change_percent, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取市场概览失败: {str(e)}")
            return None

# 创建全局实例
sh_a_stock_handler = SHAStockDataHandler()

# 便捷函数，供路由直接调用
def get_sh_a_realtime_stocks() -> Optional[List[Dict]]:
    """获取上证A股实时行情数据的便捷函数"""
    return sh_a_stock_handler.get_realtime_sh_a_stocks()

def filter_sh_a_stocks(**kwargs) -> Optional[List[Dict]]:
    """筛选上证A股股票的便捷函数"""
    return sh_a_stock_handler.filter_stocks(**kwargs)

def get_sh_a_stock_by_code(code: str) -> Optional[Dict]:
    """根据代码获取上证A股股票信息的便捷函数"""
    return sh_a_stock_handler.get_stock_by_code(code)

def get_sh_a_market_summary() -> Optional[Dict]:
    """获取上证A股市场概览的便捷函数"""
    return sh_a_stock_handler.get_market_summary()