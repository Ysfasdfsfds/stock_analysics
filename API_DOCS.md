# 上证A股实时行情API文档

本文档描述了基于akshare库的上证A股实时行情API接口，提供完整的23个字段的股票数据，包括价格、成交量、技术指标、市值等全面信息。

## 基础信息

- **Base URL**: `http://localhost:5000/api/sh-a`
- **数据格式**: JSON
- **编码**: UTF-8
- **更新频率**: 实时数据（来自akshare）

## 接口列表

### 1. 获取上证A股实时行情数据

获取全部上证A股实时行情数据。

**Endpoint**: `GET /api/sh-a/realtime`

**Query Parameters**:
- `limit` (int, optional): 返回股票数量限制，默认返回全部
- `offset` (int, optional): 偏移量，默认0

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "total": 500,
    "stocks": [
      {
        "code": "600000",
        "name": "浦发银行",
        "latest_price": 7.25,
        "change_percent": 1.25,
        "change_amount": 0.09,
        "volume": 12345678,
        "amount": 123456789.0,
        "amplitude": 3.45,
        "high": 7.35,
        "low": 7.15,
        "open": 7.18,
        "close": 7.16,
        "volume_ratio": 1.25,
        "turnover_rate": 2.35,
        "pe_ratio": 5.67,
        "pb_ratio": 0.89,
        "total_market_cap": 1567.89,
        "circulation_market_cap": 1567.89,
        "speed": 0.14,
        "change_5min": 0.28,
        "change_60day": 12.34,
        "change_ytd": 8.91,
        "timestamp": "2024-01-01T12:00:00"
      }
    ],
    "query_time": "2024-01-01T12:00:00"
  }
}
```

### 2. 筛选上证A股股票

根据条件筛选上证A股股票。

**Endpoint**: `GET /api/sh-a/filter`

**Query Parameters**:
- `min_price` (float, optional): 最低价格，默认0
- `max_price` (float, optional): 最高价格，默认1000
- `min_turnover_rate` (float, optional): 最低换手率(%)，默认0
- `max_turnover_rate` (float, optional): 最高换手率(%)，默认100
- `min_market_cap` (float, optional): 最低流通市值(亿元)，默认0
- `max_market_cap` (float, optional): 最高流通市值(亿元)，默认100000
- `sort_by` (str, optional): 排序字段，可选: latest_price, change_percent, turnover_rate, total_market_cap, circulation_market_cap，默认turnover_rate
- `ascending` (bool, optional): 是否升序，默认true

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 50,
    "stocks": [...],
    "filters": {
      "min_price": 10,
      "max_price": 60,
      "min_turnover_rate": 1,
      "max_turnover_rate": 5,
      "min_market_cap": 100,
      "max_market_cap": 100000,
      "sort_by": "turnover_rate",
      "ascending": true
    }
  }
}
```

### 3. 获取单只股票详情

根据股票代码获取单只股票详细信息。

**Endpoint**: `GET /api/sh-a/stock/<code>`

**Path Parameters**:
- `code` (str): 股票代码，例如：600000

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "latest_price": 7.25,
    "change_percent": 1.25,
    "change_amount": 0.09,
    "volume": 12345678,
    "amount": 123456789.0,
    "amplitude": 3.45,
    "high": 7.35,
    "low": 7.15,
    "open": 7.18,
    "close": 7.16,
    "volume_ratio": 1.25,
    "turnover_rate": 2.35,
    "pe_ratio": 5.67,
    "pb_ratio": 0.89,
    "total_market_cap": 1567.89,
    "circulation_market_cap": 1567.89,
    "speed": 0.14,
    "change_5min": 0.28,
    "change_60day": 12.34,
    "change_ytd": 8.91,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

### 4. 获取市场概览

获取上证A股市场概览信息。

**Endpoint**: `GET /api/sh-a/market-summary`

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_stocks": 500,
    "up_stocks": 250,
    "down_stocks": 200,
    "flat_stocks": 50,
    "avg_turnover_rate": 2.35,
    "avg_change_percent": 1.25,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

### 5. 获取热门股票

获取换手率最高的热门股票。

**Endpoint**: `GET /api/sh-a/hot-stocks`

**Query Parameters**:
- `count` (int, optional): 返回股票数量，默认10，最大100

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 10,
    "stocks": [...]
  }
}
```

### 6. 获取低换手率优质股票

基于原有代码逻辑获取低换手率优质股票（换手率在1%到5%之间，价格在10-60之间，流通市值大于100亿）。

**Endpoint**: `GET /api/sh-a/low-turnover-stocks`

**Query Parameters**:
- `count` (int, optional): 返回股票数量，默认20，最大100

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "count": 20,
    "stocks": [...],
    "criteria": {
      "price_range": "10-60",
      "turnover_range": "1%-5%",
      "min_market_cap": "100亿元",
      "sort_by": "turnover_rate_asc"
    }
  }
}
```

### 7. 获取股票类型信息

获取指定上证股票的类型信息，包括行业、板块等详细信息。

**Endpoint**: `GET /api/sh-a/stock/<code>/type`

**Path Parameters**:
- `code` (str): 股票代码，例如：600000

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "code": "600000",
    "name": "浦发银行",
    "industry": "银行",
    "sector": "股份制银行",
    "board": "上证主板",
    "market": "上证A股",
    "list_date": "1999-11-10",
    "total_shares": 2935208.04,
    "circulating_shares": 2935208.04,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

### 8. 批量获取股票类型信息

批量获取多个股票的类型信息。

**Endpoint**: `POST /api/sh-a/stock/types/batch`

**Request Body**:
```json
{
  "codes": ["600000", "600001", "688001"]
}
```

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 3,
    "types": [
      {
        "code": "600000",
        "name": "浦发银行",
        "industry": "银行",
        "board": "上证主板"
      },
      {
        "code": "600001",
        "name": "邯郸钢铁",
        "industry": "钢铁",
        "board": "上证主板"
      },
      {
        "code": "688001",
        "name": "华兴源创",
        "industry": "专用设备",
        "board": "科创板"
      }
    ]
  }
}
```

### 9. 获取行业分类

获取所有上证A股的行业分类信息，基于股票名称特征进行智能分类，避免重复API调用。

**Endpoint**: `GET /api/sh-a/industries`

**Response Example**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 25,
    "industries": [
      {
        "industry": "银行",
        "count": 32,
        "stocks": [
          {"code": "600000", "name": "浦发银行"},
          {"code": "600015", "name": "华夏银行"}
        ]
      },
      {
        "industry": "医药",
        "count": 45,
        "stocks": [
          {"code": "600276", "name": "恒瑞医药"},
          {"code": "600196", "name": "复星医药"}
        ]
      },
      {
        "industry": "其他",
        "count": 120,
        "stocks": [
          {"code": "600519", "name": "贵州茅台"}
        ]
      }
    ]
  }
}
```

**注意**: 行业分类基于股票名称特征进行智能识别，主要行业包括：银行、保险、证券、医药、房地产、汽车、钢铁、电力、石油、化工、机械、电子、通信、计算机、食品饮料、纺织服装、家电、建材、交通运输、农林牧渔、传媒、环保、有色金属、煤炭等。无法识别的股票将归类为"其他"。

## 字段说明

### 股票行情字段

| 字段名 | 类型 | 说明 | 单位 |
|--------|------|------|------|
| code | string | 股票代码 | - |
| name | string | 股票名称 | - |
| latest_price | float | 最新价 | 元 |
| change_percent | float | 涨跌幅 | % |
| change_amount | float | 涨跌额 | 元 |
| volume | integer | 成交量 | 手 |
| amount | float | 成交额 | 元 |
| amplitude | float | 振幅 | % |
| high | float | 最高价 | 元 |
| low | float | 最低价 | 元 |
| open | float | 今开价 | 元 |
| close | float | 昨收价 | 元 |
| volume_ratio | float | 量比 | - |
| turnover_rate | float | 换手率 | % |
| pe_ratio | float | 市盈率(动态) | - |
| pb_ratio | float | 市净率 | - |
| total_market_cap | float | 总市值 | 亿元 |
| circulation_market_cap | float | 流通市值 | 亿元 |
| speed | float | 涨速 | % |
| change_5min | float | 5分钟涨跌 | % |
| change_60day | float | 60日涨跌幅 | % |
| change_ytd | float | 年初至今涨跌幅 | % |
| timestamp | string | 数据时间 | ISO 8601 |

### 股票类型字段

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| industry | string | 行业分类 | "银行" |
| sector | string | 细分行业 | "股份制银行" |
| board | string | 所属板块 | "上证主板" / "科创板" |
| market | string | 所属市场 | "上证A股" |
| list_date | string | 上市日期 | "1999-11-10" |
| total_shares | float | 总股本 | 万股 |
| circulating_shares | float | 流通股本 | 万股 |

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

## 使用示例

### 获取全部上证A股数据
```bash
curl http://localhost:5000/api/sh-a/realtime
```

### 筛选低换手率股票
```bash
curl "http://localhost:5000/api/sh-a/filter?min_price=10&max_price=60&min_turnover_rate=1&max_turnover_rate=5&min_market_cap=100&sort_by=turnover_rate&ascending=true"
```

### 获取单只股票信息
```bash
curl http://localhost:5000/api/sh-a/stock/600000
```

### 获取市场概览
```bash
curl http://localhost:5000/api/sh-a/market-summary
```

### 获取热门股票
```bash
curl "http://localhost:5000/api/sh-a/hot-stocks?count=20"
```

### 获取低换手率优质股票
```bash
curl "http://localhost:5000/api/sh-a/low-turnover-stocks?count=50"
```

### 获取股票类型信息
```bash
curl http://localhost:5000/api/sh-a/stock/600000/type
```

### 批量获取股票类型信息
```bash
curl -X POST http://localhost:5000/api/sh-a/stock/types/batch \
  -H "Content-Type: application/json" \
  -d '{"codes": ["600000", "600001", "688001"]}'
```

### 获取行业分类
```bash
curl http://localhost:5000/api/sh-a/industries
```

## 注意事项

1. 数据来源于akshare，为实时数据
2. 所有市值单位已转换为亿元
3. 换手率单位为百分比
4. 价格单位为元
5. 数据更新频率取决于akshare数据源
6. 内置SQLite缓存机制，缓存有效期6小时，可配置
7. 支持环境变量配置缓存时间和重试参数
8. 提供完整的23个股票数据字段

## 快速测试

1. 安装依赖：
```bash
pip install akshare
```

2. 启动服务：
```bash
python3 run.py
```

3. 测试接口：
```bash
curl http://localhost:5000/api/sh-a/low-turnover-stocks
```