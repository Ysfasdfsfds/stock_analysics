#!/usr/bin/env python3
"""
股票分析系统Windows exe构建脚本
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)
    
    print("✓ 构建目录清理完成")

def build_exe():
    """构建exe文件"""
    print("开始构建Windows可执行文件...")
    print("=" * 60)
    
    # 清理之前的构建文件
    clean_build_dirs()
    
    # 构建命令
    build_cmd = [
        sys.executable.replace('python', 'pyinstaller'),  # 使用同环境的pyinstaller
        '--clean',  # 清理缓存
        'stock_analyzer.spec'  # 使用spec文件
    ]
    
    print(f"执行命令: {' '.join(build_cmd)}")
    print("=" * 60)
    
    try:
        # 执行构建
        result = subprocess.run(
            build_cmd,
            check=True,
            capture_output=False,  # 显示实时输出
            text=True
        )
        
        print("=" * 60)
        print("✓ exe文件构建成功！")
        
        # 检查输出文件
        exe_path = Path('dist/StockAnalyzer.exe')
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"✓ 输出文件: {exe_path}")
            print(f"✓ 文件大小: {file_size:.1f} MB")
        else:
            print("⚠ 警告: 未找到输出的exe文件")
        
        print("=" * 60)
        print("构建完成！请在 dist/ 目录下找到 StockAnalyzer.exe")
        print("双击运行即可启动股票分析系统")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 构建过程出错: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("股票分析系统 - Windows exe 构建工具")
    print("=" * 60)
    
    # 检查环境
    try:
        import pyinstaller
        print(f"✓ PyInstaller版本: {pyinstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller未安装，请先运行: pip install pyinstaller")
        return
    
    # 检查spec文件
    spec_file = Path('stock_analyzer.spec')
    if not spec_file.exists():
        print(f"✗ 配置文件不存在: {spec_file}")
        return
    
    print("✓ 环境检查通过")
    print("=" * 60)
    
    # 开始构建
    if build_exe():
        print("\n🎉 构建成功完成！")
    else:
        print("\n❌ 构建失败，请检查错误信息")

if __name__ == '__main__':
    main()