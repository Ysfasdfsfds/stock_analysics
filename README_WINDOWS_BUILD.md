# Windows exe 打包指南

## 重要说明
当前在Linux环境中生成的`dist/StockAnalyzer`是Linux可执行文件，**无法在Windows上运行**。

要生成Windows exe文件，需要在Windows环境中执行以下步骤：

## Windows环境构建步骤

### 1. 准备Windows环境
- 安装Python 3.8-3.12（推荐3.12）
- 安装Git（从GitHub克隆项目）

### 2. 克隆项目
```cmd
git clone <项目地址>
cd stock_data_service
```

### 3. 创建虚拟环境
```cmd
python -m venv stock_env
stock_env\Scripts\activate
```

### 4. 安装依赖
```cmd
pip install -r requirements.txt
pip install pyinstaller
```

### 5. 复制配置文件
确保以下文件存在：
- `launcher.py`
- `stock_analyzer.spec`
- `build_exe.py`
- `static/` 目录（前端文件）
- `templates/` 目录

### 6. 执行打包
```cmd
pyinstaller --clean stock_analyzer.spec
```

### 7. 测试运行
```cmd
dist\StockAnalyzer.exe
```

## 预期结果
- 生成的exe文件大小约200-300MB
- 双击运行后自动启动浏览器
- 访问 http://localhost:5001

## 替代方案：GitHub Actions自动构建

如果您没有Windows环境，可以使用GitHub Actions：

1. 将项目推送到GitHub
2. 使用提供的`.github/workflows/build-windows.yml`
3. GitHub会自动构建Windows exe并提供下载

## 故障排除

### 问题1: 缺少依赖模块
解决方案：在spec文件的hiddenimports中添加缺少的模块

### 问题2: 静态文件找不到
解决方案：检查datas配置，确保static和templates目录被正确包含

### 问题3: akshare数据获取失败
解决方案：检查网络连接和防火墙设置

## 当前Linux版本测试
如果要在当前Linux环境测试功能：
```bash
./dist/StockAnalyzer
```
然后访问 http://localhost:5001 验证功能完整性。