# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# 获取项目根目录
project_root = Path(SPECPATH)

# 数据文件列表 - 包含所有静态资源和模板
datas = [
    # 静态文件
    (str(project_root / 'static'), 'static'),
    # 模板文件
    (str(project_root / 'templates'), 'templates'),
    # 路由模块
    (str(project_root / 'routes'), 'routes'),
    # 数据处理器
    (str(project_root / 'data_handlers'), 'data_handlers'),
    # 工具函数
    (str(project_root / 'utils'), 'utils'),
    # 配置文件
    (str(project_root / 'config.py'), '.'),
]

# 添加akshare数据文件（安全的跨平台方式）
try:
    import akshare
    akshare_path = Path(akshare.__file__).parent
    file_fold_dir = akshare_path / 'file_fold'
    if file_fold_dir.exists():
        # 使用相对路径，避免Windows路径问题
        datas.append((str(file_fold_dir), os.path.join('akshare', 'file_fold')))
        print(f"Added akshare data directory: {file_fold_dir}")
except ImportError:
    print("Warning: akshare not found, skipping data files")
except Exception as e:
    print(f"Warning: Could not locate akshare data files: {e}")

# 隐式导入 - 确保所有必要模块被包含
hiddenimports = [
    # Flask相关
    'flask',
    'flask_cors',
    'werkzeug',
    'jinja2',
    'markupsafe',
    
    # 数据处理
    'pandas',
    'numpy',
    'akshare',
    'requests',
    'urllib3',
    'json',
    'datetime',
    'sqlite3',
    
    # 项目模块
    'config',
    'app',
    'launcher',
    
    # 路由模块
    'routes.sh_a_stock_routes',
    'routes.fundamental_analysis_routes',
    
    # 数据处理器
    'data_handlers.sh_a_stock_data',
    'data_handlers.stock_data',
    
    # 工具函数
    'utils.response',
    'utils.validators',
    
    # 其他依赖
    'logging',
    'threading',
    'webbrowser',
    'pathlib',
    'importlib',
    'importlib.util',
    'ctypes',
    'platform',
]

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'tkinter',
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StockAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口，方便查看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 暂时移除图标以避免路径问题
    version_file=None,
)