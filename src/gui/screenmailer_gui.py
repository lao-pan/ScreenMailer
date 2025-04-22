#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ScreenMailer GUI应用程序
提供图形界面来配置和运行ScreenMailer
"""

import os
import sys
import yaml
import time
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QLineEdit, QGroupBox, 
                            QFormLayout, QSpinBox, QComboBox, QTextEdit, QFileDialog,
                            QCheckBox, QMessageBox, QListWidget, QTimeEdit, QDialog, QInputDialog)
from PyQt5.QtCore import Qt, QTimer, QTime, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QTextCursor

# 添加项目根目录到路径，以便导入ScreenMailer模块
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

# 导入ScreenMailer的核心模块
from src.screenshot.capture import ScreenCapture
from src.email.sender import EmailSender
from src.scheduler.scheduler import Scheduler
from src.config.config_manager import ConfigManager
from src.utils.logger import setup_logger, get_logger

# 设置日志
logger = get_logger(__name__)

class ScreenMailerGUI(QMainWindow):
    """ScreenMailer图形界面主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 应用程序状态
        self.scheduler = None
        self.is_running = False
        self.config_manager = None
        self.config = None
        
        # 设置应用程序数据目录
        self.setup_app_directories()
        
        # 初始化日志
        self.logger = setup_logger(self.log_dir)
        
        # 加载配置
        self.load_config()
        
        # 设置UI
        self.init_ui()
        
        self.logger.info("ScreenMailer GUI已启动")
        
    def setup_app_directories(self):
        """设置应用程序的数据目录"""
        # 使用用户的"文档"文件夹存储应用程序数据
        app_name = "ScreenMailer"
        if sys.platform == "win32":
            # 获取Windows系统中的"文档"文件夹路径
            import ctypes.wintypes
            CSIDL_PERSONAL = 5  # "我的文档"文件夹的ID
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(0, CSIDL_PERSONAL, 0, 0, buf)
            documents_path = buf.value
            self.app_data_dir = os.path.join(documents_path, app_name)
        else:
            # 在非Windows系统上使用用户的主目录下的Documents文件夹
            self.app_data_dir = os.path.join(os.path.expanduser("~"), "Documents", app_name)
            
        # 创建必要的子目录
        self.log_dir = os.path.join(self.app_data_dir, "logs")
        self.config_dir = os.path.join(self.app_data_dir, "config")
        self.screenshot_dir = os.path.join(self.app_data_dir, "screenshots")
        
        # 确保目录存在
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # 设置配置文件路径
        self.config_file = os.path.join(self.config_dir, "config.yaml")
        
        logger.info(f"应用程序数据目录: {self.app_data_dir}")
        
    # ...剩余代码保持不变...
    def load_config(self):
        """加载配置文件"""
        try:
            # 初始化配置管理器
            self.config_manager = ConfigManager(self.config_file)
            self.config = self.config_manager.get_config()
            logger.info("已加载配置文件")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            self.config = {}
            
    def save_config(self):
        """保存配置到文件"""
        if self.config_manager:
            # 从UI更新配置
            self.update_config_from_ui()
            
            # 保存配置
            result = self.config_manager.save_config(self.config)
            if result:
                logger.info("配置已保存")
                QMessageBox.information(self, "配置保存", "配置已成功保存")
            else:
                logger.error("保存配置失败")
                QMessageBox.warning(self, "保存失败", "配置保存失败，请检查日志")
                
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("ScreenMailer")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标 - 更新图标路径
        tools_dir = os.path.join(project_root, "tools")
        assets_dir = os.path.join(tools_dir, "assets")
        icon_path = os.path.join(assets_dir, "icon.ico")
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡部件
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 添加选项卡
        self.create_dashboard_tab()
        self.create_email_config_tab()
        self.create_screenshot_config_tab()
        self.create_scheduler_config_tab()
        self.create_logs_tab()
        
        # 底部按钮布局
        bottom_layout = QHBoxLayout()
        main_layout.addLayout(bottom_layout)
        
        # 保存按钮
        self.save_button = QPushButton("保存配置")
        self.save_button.clicked.connect(self.save_config)
        bottom_layout.addWidget(self.save_button)
        
        # 开始/停止按钮
        self.start_stop_button = QPushButton("启动监控")
        self.start_stop_button.clicked.connect(self.toggle_monitoring)
        bottom_layout.addWidget(self.start_stop_button)
        
        # 立即截图和发送按钮
        self.capture_send_button = QPushButton("立即截图并发送")
        self.capture_send_button.clicked.connect(self.capture_and_send)
        bottom_layout.addWidget(self.capture_send_button)
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # 每秒更新一次
        
    # ...其余GUI代码保持不变...