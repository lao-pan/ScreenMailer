#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ScreenMailer打包脚本
用于将ScreenMailer程序打包成Windows可执行文件
"""

import os
import sys
import shutil
import PyInstaller.__main__

def build_exe():
    """构建可执行文件"""
    print("开始构建ScreenMailer可执行文件...")
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 创建图标文件（如果不存在）
    icon_path = os.path.join(current_dir, "icon.ico")
    if not os.path.exists(icon_path):
        print("警告: 图标文件不存在，将使用默认图标")
        icon_path = None
    
    # 源代码目录路径
    src_dir = os.path.join(project_root, 'src')
    
    # 定义打包参数
    pyinstaller_args = [
        'screenmailer_gui.py',  # 主程序文件
        '--name=ScreenMailer',  # 生成的可执行文件名称
        '--onefile',            # 打包成单个可执行文件
        '--windowed',           # 使用Windows子系统，不显示控制台窗口
        '--clean',              # 在构建之前清除临时文件
        '--noconfirm',          # 不询问确认
        f'--add-data={src_dir};src',  # 使用绝对路径添加源代码目录
        '--hidden-import=PIL',  # 添加PIL模块作为隐式导入
        '--hidden-import=PIL._imagingtk',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=PIL.ImageGrab',
        '--hidden-import=PIL.Image',
        '--hidden-import=Pillow',
        # 添加标准库模块作为隐式导入
        '--hidden-import=smtplib',
        '--hidden-import=email',
        '--hidden-import=email.mime.multipart',
        '--hidden-import=email.mime.text',
        '--hidden-import=email.mime.image',
        '--hidden-import=logging',
        '--hidden-import=logging.handlers',
        '--hidden-import=datetime',
        '--hidden-import=yaml',
        '--hidden-import=platform',
        '--hidden-import=schedule',
        '--hidden-import=threading',
    ]
    
    # 如果有图标文件，添加图标
    if icon_path:
        pyinstaller_args.append(f'--icon={icon_path}')
    
    # 设置工作目录
    os.chdir(current_dir)
    
    print("检测所需库是否已安装...")
    try:
        import PIL
        print(f"Pillow已安装，版本: {PIL.__version__}")
    except ImportError:
        print("警告: 未检测到Pillow(PIL)库，请先运行 'pip install Pillow'")
        
    try:
        import yaml
        print(f"PyYAML已安装，版本: {yaml.__version__}")
    except ImportError:
        print("警告: 未检测到PyYAML库，请先运行 'pip install pyyaml'")
        
    try:
        import schedule
        print(f"schedule已安装，版本: {schedule.__version__}")
    except (ImportError, AttributeError):
        print("警告: 未检测到schedule库，请先运行 'pip install schedule'")
    
    # 创建一个临时的__init__.py文件，以帮助PyInstaller识别自定义包
    email_init_path = os.path.join(src_dir, 'email', '__init__.py')
    if not os.path.exists(email_init_path):
        try:
            open(email_init_path, 'w').close()
            print(f"创建了临时文件: {email_init_path}")
        except Exception as e:
            print(f"无法创建临时文件: {e}")
    
    # 调用PyInstaller
    print("正在调用PyInstaller打包程序...")
    PyInstaller.__main__.run(pyinstaller_args)
    
    # 如果创建了临时文件，尝试删除
    if os.path.exists(email_init_path) and os.path.getsize(email_init_path) == 0:
        try:
            os.remove(email_init_path)
            print(f"删除了临时文件: {email_init_path}")
        except:
            pass
    
    # 构建完成后检查
    dist_dir = os.path.join(current_dir, "dist")
    if not os.path.exists(dist_dir):
        dist_dir = os.path.join(project_root, "dist")  # 尝试项目根目录下的dist文件夹
        
    exe_path = os.path.join(dist_dir, "ScreenMailer.exe")
    
    if os.path.exists(exe_path):
        print(f"打包成功! 可执行文件路径: {exe_path}")
        
        # 创建发布目录
        release_dir = os.path.join(project_root, "release")
        os.makedirs(release_dir, exist_ok=True)
        
        # 将可执行文件复制到发布目录
        release_exe = os.path.join(release_dir, "ScreenMailer.exe")
        shutil.copy2(exe_path, release_exe)
        print(f"已将可执行文件复制到发布目录: {release_exe}")
        
        return True
    else:
        print("打包失败，请检查错误信息")
        return False

if __name__ == "__main__":
    try:
        success = build_exe()
        if success:
            print("ScreenMailer打包过程成功完成!")
        else:
            print("ScreenMailer打包过程失败!")
            sys.exit(1)
    except Exception as e:
        print(f"打包过程中发生错误: {str(e)}")
        sys.exit(1)