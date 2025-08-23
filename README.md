# 股票数据服务 Flask 框架

这是一个灵活的股票数据服务 Flask 框架，用户只需要在指定目录添加数据获取逻辑、接口函数和路由即可快速构建股票数据API服务。

## 项目结构

```
stock_data_service/
├── app.py                 # 主应用文件
├── run.py                 # 启动脚本
├── config.py              # 配置文件
├── requirements.txt       # 依赖文件
├── .env.example          # 环境变量模板
├── Dockerfile            # Docker配置文件
├── docker-compose.yml    # Docker Compose配置
├── routes/               # 路由目录
│   ├── example.py        # 示例路由文件
├── data_handlers/        # 数据处理器目录
│   └── stock_data.py     # 股票数据处理
├── utils/                # 工具函数目录
│   ├── response.py       # 响应工具
│   └── validators.py     # 验证工具
├── models/               # 数据模型目录（预留）
├── tests/                # 测试文件目录
├── logs/                 # 日志目录
└── data/                 # 数据存储目录
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置项
```

### 3. 启动服务

```bash
# 开发模式
python run.py

# 或使用Flask命令
flask run

# 生产模式
export FLASK_ENV=production
python run.py
```

### 4. 测试服务

访问以下地址测试服务是否正常运行：
- http://localhost:5000/ - 服务主页
- http://localhost:5000/health - 健康检查
- http://localhost:5000/api/example/hello - 示例接口

## 使用指南

### 添加新的数据获取逻辑

在 `data_handlers/` 目录下创建新的数据处理器文件：

```python
# data_handlers/my_data_handler.py
from typing import Dict, List

class MyDataHandler:
    def get_data(self, symbol: str) -> Dict:
        # 实现你的数据获取逻辑
        return {"data": "your data here"}

# 创建便捷函数供路由使用
my_handler = MyDataHandler()
def get_my_data(symbol: str) -> Dict:
    return my_handler.get_data(symbol)
```

### 添加新的接口函数

在 `routes/` 目录下创建新的路由文件：

```python
# routes/my_routes.py
from flask import Blueprint, request
from utils.response import success_response, error_response
from data_handlers.my_data_handler import get_my_data

# 创建蓝图
bp = Blueprint('my_routes', __name__, url_prefix='/api/my')

@bp.route('/data/<symbol>', methods=['GET'])
def get_custom_data(symbol):
    """获取自定义数据"""
    try:
        data = get_my_data(symbol)
        return success_response(data)
    except Exception as e:
        return error_response(str(e), 500)

@bp.route('/batch', methods=['POST'])
def batch_get_data():
    """批量获取数据"""
    try:
        symbols = request.json.get('symbols', [])
        results = [get_my_data(symbol) for symbol in symbols]
        return success_response(results)
    except Exception as e:
        return error_response(str(e), 500)
```

### 使用工具函数

#### 响应工具

```python
from utils.response import success_response, error_response

# 成功响应
return success_response(data, '操作成功')

# 错误响应
return error_response('错误信息', 400)
```

#### 验证工具

```python
from utils.validators import validate_stock_symbol, validate_symbols_list

# 验证单个股票代码
if not validate_stock_symbol(symbol):
    return error_response('无效的股票代码', 400)

# 验证股票代码列表
if not validate_symbols_list(symbols):
    return error_response('无效的股票代码列表', 400)
```

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| FLASK_ENV | 运行环境 | development |
| PORT | 服务端口 | 5000 |
| SECRET_KEY | 安全密钥 | dev-secret-key |
| STOCK_API_KEY | 股票API密钥 | - |
| STOCK_API_BASE_URL | 股票API基础URL | https://api.example.com |
| DATABASE_URL | 数据库连接 | sqlite:///stock_data.db |
| REDIS_URL | Redis连接 | redis://localhost:6379/0 |
| LOG_LEVEL | 日志级别 | INFO |

### 配置文件

编辑 `config.py` 文件可以添加更多配置项：

```python
class MyConfig(Config):
    MY_CUSTOM_SETTING = os.environ.get('MY_SETTING') or 'default_value'
```

## Docker部署

### 使用Docker

```bash
# 构建镜像
docker build -t stock-data-service .

# 运行容器
docker run -p 5000:5000 stock-data-service
```

### 使用Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down
```

## 开发最佳实践

### 1. 数据获取逻辑

- 将所有数据获取逻辑放在 `data_handlers/` 目录
- 使用类封装数据获取功能
- 提供错误处理和日志记录
- 使用缓存提高性能

### 2. 路由设计

- 每个功能模块创建独立的路由文件
- 使用蓝图（Blueprint）组织路由
- 提供清晰的API文档注释
- 统一响应格式

### 3. 错误处理

- 使用 try-except 处理异常
- 提供有意义的错误信息
- 记录错误日志
- 返回标准的错误响应

### 4. 测试

```bash
# 运行测试
pytest tests/

# 运行特定测试
pytest tests/test_app.py::test_health_check

# 生成测试报告
pytest --cov=. --cov-report=html
```

## 示例API

### 健康检查

```bash
curl http://localhost:5000/health
```

### 获取股票数据

```bash
curl http://localhost:5000/api/example/stock/AAPL?period=1d
```

### 批量获取股票数据

```bash
curl -X POST http://localhost:5000/api/example/stocks \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"], "period": "1d"}'
```

## 故障排除

### 常见问题

1. **端口占用**
   ```bash
   lsof -i :5000
   kill -9 <PID>
   ```

2. **依赖问题**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **权限问题**
   ```bash
   chmod +x run.py
   ```

### 日志查看

```bash
# 查看应用日志
tail -f logs/app.log

# 查看系统日志（Docker）
docker-compose logs -f web
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。