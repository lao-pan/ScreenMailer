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

# 添加src目录到路径，以便导入ScreenMailer模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')

if src_dir not in sys.path:
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
        
        # 设置窗口图标
        self.setWindowIcon(QIcon("icon.png"))  # 您需要添加一个图标文件
        
    def create_dashboard_tab(self):
        """创建仪表盘选项卡"""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        
        # 状态组
        status_group = QGroupBox("系统状态")
        status_layout = QFormLayout()
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 状态标签
        self.status_label = QLabel("未运行")
        status_layout.addRow("监控状态:", self.status_label)
        
        self.last_screenshot_label = QLabel("无")
        status_layout.addRow("上次截图:", self.last_screenshot_label)
        
        self.last_email_label = QLabel("无")
        status_layout.addRow("上次邮件:", self.last_email_label)
        
        self.screenshot_count_label = QLabel("0")
        status_layout.addRow("未发送截图数量:", self.screenshot_count_label)
        
        # 统计信息组
        stats_group = QGroupBox("统计信息")
        stats_layout = QFormLayout()
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.total_screenshots_label = QLabel("0")
        stats_layout.addRow("总截图数:", self.total_screenshots_label)
        
        self.total_emails_label = QLabel("0")
        stats_layout.addRow("总邮件数:", self.total_emails_label)
        
        self.run_time_label = QLabel("00:00:00")
        stats_layout.addRow("运行时间:", self.run_time_label)
        
        # 添加仪表盘选项卡
        self.tabs.addTab(dashboard_tab, "仪表盘")
        
    def create_email_config_tab(self):
        """创建邮件配置选项卡"""
        email_tab = QWidget()
        layout = QVBoxLayout(email_tab)
        
        # SMTP服务器设置组
        smtp_group = QGroupBox("SMTP服务器设置")
        smtp_layout = QFormLayout()
        smtp_group.setLayout(smtp_layout)
        layout.addWidget(smtp_group)
        
        # SMTP服务器地址
        self.smtp_server_input = QLineEdit()
        smtp_layout.addRow("SMTP服务器:", self.smtp_server_input)
        
        # 端口号
        self.smtp_port_input = QSpinBox()
        self.smtp_port_input.setRange(1, 65535)
        self.smtp_port_input.setValue(587)
        smtp_layout.addRow("端口号:", self.smtp_port_input)
        
        # 使用SSL
        self.use_ssl_checkbox = QCheckBox()
        smtp_layout.addRow("使用SSL:", self.use_ssl_checkbox)
        
        # 邮箱凭证组
        credentials_group = QGroupBox("邮箱凭证")
        credentials_layout = QFormLayout()
        credentials_group.setLayout(credentials_layout)
        layout.addWidget(credentials_group)
        
        # 用户名
        self.username_input = QLineEdit()
        credentials_layout.addRow("用户名:", self.username_input)
        
        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        credentials_layout.addRow("密码:", self.password_input)
        
        # 发件人
        self.sender_email_input = QLineEdit()
        credentials_layout.addRow("发件人:", self.sender_email_input)
        
        # 收件人设置组
        recipients_group = QGroupBox("收件人设置")
        recipients_layout = QVBoxLayout()
        recipients_group.setLayout(recipients_layout)
        layout.addWidget(recipients_group)
        
        # 收件人列表
        self.recipients_list = QListWidget()
        recipients_layout.addWidget(self.recipients_list)
        
        # 收件人管理按钮
        recipients_buttons = QHBoxLayout()
        
        self.add_recipient_btn = QPushButton("添加")
        self.add_recipient_btn.clicked.connect(self.add_recipient)
        recipients_buttons.addWidget(self.add_recipient_btn)
        
        self.remove_recipient_btn = QPushButton("移除")
        self.remove_recipient_btn.clicked.connect(self.remove_recipient)
        recipients_buttons.addWidget(self.remove_recipient_btn)
        
        recipients_layout.addLayout(recipients_buttons)
        
        # 邮件主题前缀
        self.subject_prefix_input = QLineEdit()
        layout.addWidget(QLabel("邮件主题前缀:"))
        layout.addWidget(self.subject_prefix_input)
        
        # 添加测试按钮
        self.test_email_btn = QPushButton("发送测试邮件")
        self.test_email_btn.clicked.connect(self.send_test_email)
        layout.addWidget(self.test_email_btn)
        
        # 添加邮件配置选项卡
        self.tabs.addTab(email_tab, "邮件设置")
        
        # 初始化邮件配置
        self.init_email_config()
        
    def init_email_config(self):
        """从配置中初始化邮件设置"""
        if not self.config:
            return
            
        email_config = self.config.get('email', {})
        
        # 设置SMTP信息
        self.smtp_server_input.setText(email_config.get('smtp_server', ''))
        self.smtp_port_input.setValue(email_config.get('smtp_port', 587))
        self.use_ssl_checkbox.setChecked(email_config.get('use_ssl', False))
        
        # 设置凭证
        self.username_input.setText(email_config.get('username', ''))
        self.password_input.setText(email_config.get('password', ''))
        self.sender_email_input.setText(email_config.get('sender_email', ''))
        
        # 设置收件人
        self.recipients_list.clear()
        recipients = email_config.get('recipients', [])
        for recipient in recipients:
            self.recipients_list.addItem(recipient)
            
        # 设置主题前缀
        self.subject_prefix_input.setText(email_config.get('subject_prefix', '[ScreenMailer]'))
        
    def add_recipient(self):
        """添加收件人"""
        email, ok = QInputDialog.getText(self, "添加收件人", "请输入收件人邮箱:")
        if ok and email:
            self.recipients_list.addItem(email)
            
    def remove_recipient(self):
        """移除收件人"""
        selected_items = self.recipients_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            self.recipients_list.takeItem(self.recipients_list.row(item))
            
    def create_screenshot_config_tab(self):
        """创建截图配置选项卡"""
        screenshot_tab = QWidget()
        layout = QVBoxLayout(screenshot_tab)
        
        # 截图设置组
        screenshot_group = QGroupBox("截图设置")
        screenshot_layout = QFormLayout()
        screenshot_group.setLayout(screenshot_layout)
        layout.addWidget(screenshot_group)
        
        # 图片格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpg", "bmp"])
        screenshot_layout.addRow("图片格式:", self.format_combo)
        
        # 图片质量
        self.quality_spinbox = QSpinBox()
        self.quality_spinbox.setRange(1, 100)
        self.quality_spinbox.setValue(90)
        screenshot_layout.addRow("图片质量(1-100):", self.quality_spinbox)
        
        # 截图区域设置
        self.region_group = QGroupBox("截图区域")
        region_layout = QFormLayout()
        self.region_group.setLayout(region_layout)
        layout.addWidget(self.region_group)
        
        # 全屏选项
        self.fullscreen_checkbox = QCheckBox("全屏截图")
        self.fullscreen_checkbox.setChecked(True)
        self.fullscreen_checkbox.toggled.connect(self.toggle_region_inputs)
        region_layout.addRow("", self.fullscreen_checkbox)
        
        # 自定义区域
        region_inputs_layout = QHBoxLayout()
        
        self.left_input = QSpinBox()
        self.left_input.setRange(0, 9999)
        region_inputs_layout.addWidget(QLabel("左:"))
        region_inputs_layout.addWidget(self.left_input)
        
        self.top_input = QSpinBox()
        self.top_input.setRange(0, 9999)
        region_inputs_layout.addWidget(QLabel("上:"))
        region_inputs_layout.addWidget(self.top_input)
        
        self.right_input = QSpinBox()
        self.right_input.setRange(0, 9999)
        region_inputs_layout.addWidget(QLabel("右:"))
        region_inputs_layout.addWidget(self.right_input)
        
        self.bottom_input = QSpinBox()
        self.bottom_input.setRange(0, 9999)
        region_inputs_layout.addWidget(QLabel("下:"))
        region_inputs_layout.addWidget(self.bottom_input)
        
        region_layout.addRow("自定义区域:", region_inputs_layout)
        
        # 选择区域按钮
        self.select_region_btn = QPushButton("选择屏幕区域")
        self.select_region_btn.clicked.connect(self.select_screen_region)
        region_layout.addRow("", self.select_region_btn)
        
        # 测试截图按钮
        self.test_screenshot_btn = QPushButton("测试截图")
        self.test_screenshot_btn.clicked.connect(self.test_screenshot)
        layout.addWidget(self.test_screenshot_btn)
        
        # 添加截图配置选项卡
        self.tabs.addTab(screenshot_tab, "截图设置")
        
        # 初始化截图配置
        self.init_screenshot_config()
        
    def init_screenshot_config(self):
        """从配置中初始化截图设置"""
        if not self.config:
            return
            
        screenshot_config = self.config.get('screenshot', {})
        
        # 设置图片格式
        format_value = screenshot_config.get('format', 'png')
        index = self.format_combo.findText(format_value)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
            
        # 设置图片质量
        self.quality_spinbox.setValue(screenshot_config.get('quality', 90))
        
        # 设置截图区域
        bbox = screenshot_config.get('bbox', None)
        if bbox is None:
            self.fullscreen_checkbox.setChecked(True)
            self.toggle_region_inputs(True)
        else:
            self.fullscreen_checkbox.setChecked(False)
            self.toggle_region_inputs(False)
            
            # 设置区域值
            self.left_input.setValue(bbox[0])
            self.top_input.setValue(bbox[1])
            self.right_input.setValue(bbox[2])
            self.bottom_input.setValue(bbox[3])
            
    def toggle_region_inputs(self, fullscreen):
        """切换区域输入框的启用状态"""
        self.left_input.setDisabled(fullscreen)
        self.top_input.setDisabled(fullscreen)
        self.right_input.setDisabled(fullscreen)
        self.bottom_input.setDisabled(fullscreen)
        self.select_region_btn.setDisabled(fullscreen)
        
    def select_screen_region(self):
        """选择屏幕区域"""
        # 这里需要实现屏幕区域选择功能
        # 可以使用第三方库如PyQt5的QRubberBand
        QMessageBox.information(self, "选择区域", "区域选择功能待实现")
        
    def test_screenshot(self):
        """测试截图功能"""
        try:
            # 获取截图配置
            screenshot_config = {
                'format': self.format_combo.currentText(),
                'quality': self.quality_spinbox.value(),
                'bbox': None if self.fullscreen_checkbox.isChecked() else [
                    self.left_input.value(),
                    self.top_input.value(),
                    self.right_input.value(),
                    self.bottom_input.value()
                ]
            }
            
            # 创建临时截图对象
            screen_capture = ScreenCapture(self.screenshot_dir, screenshot_config)
            
            # 进行截图
            screenshot_path = screen_capture.capture()
            
            if screenshot_path:
                QMessageBox.information(self, "测试成功", f"截图已保存至: {screenshot_path}")
            else:
                QMessageBox.warning(self, "测试失败", "截图失败，请检查设置和日志")
                
        except Exception as e:
            logger.error(f"测试截图失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"测试截图时发生错误: {str(e)}")
            
    def create_scheduler_config_tab(self):
        """创建调度器配置选项卡"""
        scheduler_tab = QWidget()
        layout = QVBoxLayout(scheduler_tab)
        
        # 截图调度设置组
        screenshot_schedule_group = QGroupBox("截图调度设置")
        screenshot_schedule_layout = QFormLayout()
        screenshot_schedule_group.setLayout(screenshot_schedule_layout)
        layout.addWidget(screenshot_schedule_group)
        
        # 截图间隔
        self.screenshot_interval_spinbox = QSpinBox()
        self.screenshot_interval_spinbox.setRange(5, 86400)  # 5秒到24小时
        self.screenshot_interval_spinbox.setValue(300)  # 默认5分钟
        self.screenshot_interval_spinbox.setSuffix(" 秒")
        screenshot_schedule_layout.addRow("截图间隔:", self.screenshot_interval_spinbox)
        
        # 连续截图数量
        self.screenshot_count_spinbox = QSpinBox()
        self.screenshot_count_spinbox.setRange(1, 10)
        self.screenshot_count_spinbox.setValue(1)
        self.screenshot_count_spinbox.setSuffix(" 张")
        screenshot_schedule_layout.addRow("连续截图数量:", self.screenshot_count_spinbox)
        
        # 连续截图间隔
        self.screenshot_delay_spinbox = QSpinBox()
        self.screenshot_delay_spinbox.setRange(0, 60)
        self.screenshot_delay_spinbox.setValue(1)
        self.screenshot_delay_spinbox.setSuffix(" 秒")
        screenshot_schedule_layout.addRow("连续截图间隔:", self.screenshot_delay_spinbox)
        
        # 邮件调度设置组
        email_schedule_group = QGroupBox("邮件调度设置")
        email_schedule_layout = QFormLayout()
        email_schedule_group.setLayout(email_schedule_layout)
        layout.addWidget(email_schedule_group)
        
        # 邮件发送模式
        self.email_mode_combo = QComboBox()
        self.email_mode_combo.addItems(["按间隔发送", "整点发送", "每半小时发送", "自定义时间发送"])
        self.email_mode_combo.currentIndexChanged.connect(self.email_mode_changed)
        email_schedule_layout.addRow("发送模式:", self.email_mode_combo)
        
        # 邮件发送间隔
        self.email_interval_spinbox = QSpinBox()
        self.email_interval_spinbox.setRange(60, 86400)  # 1分钟到24小时
        self.email_interval_spinbox.setValue(3600)  # 默认1小时
        self.email_interval_spinbox.setSuffix(" 秒")
        email_schedule_layout.addRow("发送间隔:", self.email_interval_spinbox)
        
        # 自定义时间列表
        self.custom_times_list = QListWidget()
        email_schedule_layout.addRow("自定义时间:", self.custom_times_list)
        
        # 自定义时间管理按钮
        custom_time_buttons = QHBoxLayout()
        
        self.add_time_btn = QPushButton("添加时间")
        self.add_time_btn.clicked.connect(self.add_custom_time)
        custom_time_buttons.addWidget(self.add_time_btn)
        
        self.remove_time_btn = QPushButton("移除时间")
        self.remove_time_btn.clicked.connect(self.remove_custom_time)
        custom_time_buttons.addWidget(self.remove_time_btn)
        
        email_schedule_layout.addRow("", custom_time_buttons)
        
        # 启动时立即执行
        self.send_immediate_checkbox = QCheckBox()
        email_schedule_layout.addRow("启动时立即执行:", self.send_immediate_checkbox)
        
        # 截图后立即发送
        self.send_with_capture_checkbox = QCheckBox()
        email_schedule_layout.addRow("截图后立即发送:", self.send_with_capture_checkbox)
        
        # 添加调度器配置选项卡
        self.tabs.addTab(scheduler_tab, "调度设置")
        
        # 初始化调度器配置
        self.init_scheduler_config()
        
    def init_scheduler_config(self):
        """从配置中初始化调度器设置"""
        if not self.config:
            return
            
        scheduler_config = self.config.get('scheduler', {})
        
        # 设置截图调度 - 确保将浮点数转换为整数
        self.screenshot_interval_spinbox.setValue(int(scheduler_config.get('screenshot_interval', 300)))
        self.screenshot_count_spinbox.setValue(int(scheduler_config.get('screenshot_count', 1)))
        self.screenshot_delay_spinbox.setValue(int(scheduler_config.get('screenshot_delay', 1)))
        
        # 设置邮件调度
        email_mode = scheduler_config.get('email_mode', 'interval')
        if email_mode == 'interval':
            self.email_mode_combo.setCurrentIndex(0)
        elif email_mode == 'hourly':
            self.email_mode_combo.setCurrentIndex(1)
        elif email_mode == 'half_hourly':
            self.email_mode_combo.setCurrentIndex(2)
        elif email_mode == 'custom':
            self.email_mode_combo.setCurrentIndex(3)
            
        self.email_interval_spinbox.setValue(int(scheduler_config.get('email_interval', 3600)))
        
        # 设置自定义时间
        self.custom_times_list.clear()
        custom_times = scheduler_config.get('email_custom_times', [])
        for time_str in custom_times:
            self.custom_times_list.addItem(time_str)
            
        # 设置其他选项
        self.send_immediate_checkbox.setChecked(scheduler_config.get('send_immediate', True))
        self.send_with_capture_checkbox.setChecked(scheduler_config.get('send_with_capture', False))
        
        # 根据发送模式更新UI状态
        self.email_mode_changed(self.email_mode_combo.currentIndex())
        
    def email_mode_changed(self, index):
        """邮件发送模式改变时的UI更新"""
        # 启用/禁用邮件发送间隔
        self.email_interval_spinbox.setEnabled(index == 0)  # 只在"按间隔发送"模式启用
        
        # 启用/禁用自定义时间列表
        custom_times_enabled = index == 3  # 只在"自定义时间发送"模式启用
        self.custom_times_list.setEnabled(custom_times_enabled)
        self.add_time_btn.setEnabled(custom_times_enabled)
        self.remove_time_btn.setEnabled(custom_times_enabled)
        
    def add_custom_time(self):
        """添加自定义时间"""
        time_dialog = QTimeEdit()
        time_dialog.setTime(QTime.currentTime())
        time_dialog.setDisplayFormat("HH:mm")
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加自定义时间")
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("请选择时间:"))
        layout.addWidget(time_dialog)
        
        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        if dialog.exec_():
            time_str = time_dialog.time().toString("HH:mm")
            self.custom_times_list.addItem(time_str)
            
    def remove_custom_time(self):
        """移除自定义时间"""
        selected_items = self.custom_times_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            self.custom_times_list.takeItem(self.custom_times_list.row(item))
            
    def create_logs_tab(self):
        """创建日志选项卡"""
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 日志操作按钮
        log_buttons = QHBoxLayout()
        
        self.refresh_logs_btn = QPushButton("刷新日志")
        self.refresh_logs_btn.clicked.connect(self.refresh_logs)
        log_buttons.addWidget(self.refresh_logs_btn)
        
        self.clear_logs_btn = QPushButton("清空日志")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        log_buttons.addWidget(self.clear_logs_btn)
        
        self.open_log_dir_btn = QPushButton("打开日志目录")
        self.open_log_dir_btn.clicked.connect(lambda: os.startfile(self.log_dir))
        log_buttons.addWidget(self.open_log_dir_btn)
        
        layout.addLayout(log_buttons)
        
        # 添加日志选项卡
        self.tabs.addTab(logs_tab, "日志")
        
        # 初始化日志内容
        self.refresh_logs()
        
    def refresh_logs(self):
        """刷新日志内容"""
        try:
            # 获取最新日志文件
            log_files = [f for f in os.listdir(self.log_dir) if f.endswith('.log')]
            if not log_files:
                self.log_text.setPlainText("无日志文件")
                return
                
            # 按修改时间排序，取最新的日志文件
            log_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.log_dir, x)), reverse=True)
            latest_log = os.path.join(self.log_dir, log_files[0])
            
            # 读取日志内容
            with open(latest_log, 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            # 显示日志内容
            self.log_text.setPlainText(log_content)
            
            # 滚动到底部
            self.log_text.moveCursor(QTextCursor.End)
            
        except Exception as e:
            self.log_text.setPlainText(f"读取日志失败: {str(e)}")
            
    def clear_logs(self):
        """清空日志显示"""
        self.log_text.clear()
        
    def update_config_from_ui(self):
        """从UI更新配置"""
        # 邮件配置
        email_config = {}
        email_config['smtp_server'] = self.smtp_server_input.text()
        email_config['smtp_port'] = self.smtp_port_input.value()
        email_config['use_ssl'] = self.use_ssl_checkbox.isChecked()
        email_config['username'] = self.username_input.text()
        email_config['password'] = self.password_input.text()
        email_config['sender_email'] = self.sender_email_input.text()
        
        # 收件人列表
        recipients = []
        for i in range(self.recipients_list.count()):
            recipients.append(self.recipients_list.item(i).text())
        email_config['recipients'] = recipients
        
        email_config['subject_prefix'] = self.subject_prefix_input.text()
        
        # 更新邮件配置
        self.config['email'] = email_config
        
        # 截图配置
        screenshot_config = {}
        screenshot_config['format'] = self.format_combo.currentText()
        screenshot_config['quality'] = self.quality_spinbox.value()
        
        # 截图区域
        if self.fullscreen_checkbox.isChecked():
            screenshot_config['bbox'] = None
        else:
            screenshot_config['bbox'] = [
                self.left_input.value(),
                self.top_input.value(),
                self.right_input.value(),
                self.bottom_input.value()
            ]
            
        # 更新截图配置
        self.config['screenshot'] = screenshot_config
        
        # 调度器配置
        scheduler_config = {}
        scheduler_config['screenshot_interval'] = self.screenshot_interval_spinbox.value()
        scheduler_config['screenshot_count'] = self.screenshot_count_spinbox.value()
        scheduler_config['screenshot_delay'] = self.screenshot_delay_spinbox.value()
        
        # 邮件发送模式
        email_mode_index = self.email_mode_combo.currentIndex()
        if email_mode_index == 0:
            scheduler_config['email_mode'] = 'interval'
        elif email_mode_index == 1:
            scheduler_config['email_mode'] = 'hourly'
        elif email_mode_index == 2:
            scheduler_config['email_mode'] = 'half_hourly'
        elif email_mode_index == 3:
            scheduler_config['email_mode'] = 'custom'
            
        scheduler_config['email_interval'] = self.email_interval_spinbox.value()
        
        # 自定义时间
        custom_times = []
        for i in range(self.custom_times_list.count()):
            custom_times.append(self.custom_times_list.item(i).text())
        scheduler_config['email_custom_times'] = custom_times
        
        # 其他选项
        scheduler_config['send_immediate'] = self.send_immediate_checkbox.isChecked()
        scheduler_config['send_with_capture'] = self.send_with_capture_checkbox.isChecked()
        
        # 更新调度器配置
        self.config['scheduler'] = scheduler_config
        
    def toggle_monitoring(self):
        """切换监控状态"""
        if self.is_running:
            self.stop_monitoring()
        else:
            self.start_monitoring()
            
    def start_monitoring(self):
        """启动监控"""
        try:
            # 保存当前配置
            self.update_config_from_ui()
            
            # 创建截图模块
            screen_capture = ScreenCapture(
                self.screenshot_dir, 
                self.config['screenshot']
            )
            
            # 创建邮件发送模块
            email_sender = EmailSender(self.config['email'])
            
            # 创建调度器
            self.scheduler = Scheduler(
                screen_capture=screen_capture,
                email_sender=email_sender,
                config=self.config['scheduler']
            )
            
            # 启动调度器
            self.scheduler.start()
            
            # 更新状态
            self.is_running = True
            self.start_stop_button.setText("停止监控")
            self.status_label.setText("正在运行")
            
            # 记录启动时间
            self.start_time = datetime.now()
            
            logger.info("监控已启动")
            QMessageBox.information(self, "成功", "监控已启动")
            
        except Exception as e:
            logger.error(f"启动监控失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"启动监控失败: {str(e)}")
            
    def stop_monitoring(self):
        """停止监控"""
        if self.scheduler:
            self.scheduler.stop()
            self.scheduler = None
            
        # 更新状态
        self.is_running = False
        self.start_stop_button.setText("启动监控")
        self.status_label.setText("未运行")
        
        logger.info("监控已停止")
        QMessageBox.information(self, "成功", "监控已停止")
        
    def capture_and_send(self):
        """立即截图并发送"""
        try:
            # 保存当前配置
            self.update_config_from_ui()
            
            # 创建临时截图模块
            screen_capture = ScreenCapture(
                self.screenshot_dir,
                self.config['screenshot']
            )
            
            # 创建临时邮件发送模块
            email_sender = EmailSender(self.config['email'])
            
            # 截图
            logger.info("执行手动截图")
            screenshot_paths = screen_capture.capture_multi(
                count=self.screenshot_count_spinbox.value(),
                interval=self.screenshot_delay_spinbox.value()
            )
            
            if not screenshot_paths:
                logger.warning("截图失败")
                QMessageBox.warning(self, "失败", "截图失败，请检查设置")
                return
                
            # 发送邮件
            logger.info(f"发送手动截图邮件，共{len(screenshot_paths)}张")
            result = email_sender.send_monitor_email(screenshot_paths)
            
            if result:
                logger.info("手动发送邮件成功")
                QMessageBox.information(self, "成功", f"已成功发送{len(screenshot_paths)}张截图")
                
                # 清理截图
                screen_capture.cleanup_screenshots(screenshot_paths)
            else:
                logger.error("手动发送邮件失败")
                QMessageBox.warning(self, "失败", "发送邮件失败，请检查邮件设置")
                
        except Exception as e:
            logger.error(f"手动截图和发送失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
            
    def send_test_email(self):
        """发送测试邮件"""
        try:
            # 保存当前配置
            self.update_config_from_ui()
            
            # 创建临时邮件发送模块
            email_sender = EmailSender(self.config['email'])
            
            # 发送测试邮件
            logger.info("发送测试邮件")
            subject = "测试邮件"
            message = "这是一封来自ScreenMailer的测试邮件。\n\n如果您收到此邮件，说明邮件配置正确。"
            
            result = email_sender.send_email(subject, message)
            
            if result:
                logger.info("测试邮件发送成功")
                QMessageBox.information(self, "成功", "测试邮件已成功发送")
            else:
                logger.error("测试邮件发送失败")
                QMessageBox.warning(self, "失败", "测试邮件发送失败，请检查邮件设置")
                
        except Exception as e:
            logger.error(f"发送测试邮件失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"发送测试邮件失败: {str(e)}")
            
    def update_status(self):
        """更新状态信息"""
        if self.is_running:
            # 更新运行时间
            run_duration = datetime.now() - self.start_time
            hours, remainder = divmod(run_duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.run_time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # TODO: 更新其他状态信息，如果scheduler实现了相应的接口
            
def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = ScreenMailerGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()