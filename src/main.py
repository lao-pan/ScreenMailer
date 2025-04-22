#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ScreenMailer - 自动屏幕截图和邮件发送监控工具
主程序入口文件
"""

import os
import sys
import time
import logging
from datetime import datetime

# 添加项目根目录到系统路径，确保可以正确导入模块
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# 导入项目模块 - 修正导入路径，避免与标准库冲突
from src.screenshot.capture import ScreenCapture
from src.email.sender import EmailSender  # 修改为完整导入路径
from src.scheduler.scheduler import Scheduler
from src.config.config_manager import ConfigManager
from src.utils.logger import setup_logger

def main():
    """主程序入口函数"""
    # 初始化日志系统
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    logger = setup_logger(log_path)
    logger.info("ScreenMailer 启动中... %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # 加载配置
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')
        config_manager = ConfigManager(config_path)
        config = config_manager.get_config()
        
        # 初始化截图模块
        screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'screenshots')
        screen_capture = ScreenCapture(screenshot_dir, config['screenshot'])
        
        # 初始化邮件发送模块
        email_sender = EmailSender(config['email'])
        
        # 初始化调度器
        scheduler = Scheduler(
            screen_capture=screen_capture,
            email_sender=email_sender,
            config=config['scheduler']
        )
        
        # 启动调度器
        logger.info("开始执行监控任务")
        scheduler.start()
        
    except Exception as e:
        logger.error(f"程序发生错误: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())