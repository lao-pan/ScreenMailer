#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具模块
设置应用的日志记录
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(log_dir, log_level=logging.INFO):
    """
    设置应用日志系统
    
    Args:
        log_dir (str): 日志文件保存目录
        log_level: 日志级别，默认为INFO
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建日志文件名
    log_file = os.path.join(log_dir, f"screenmailer_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 设置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 清空已有的handlers，避免重复
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # 创建文件处理器，使用RotatingFileHandler可以限制日志文件大小
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_format)
    
    # 添加处理器到根日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    logger.info("日志系统初始化完成")
    return logger

def get_logger(name):
    """
    获取指定名称的日志记录器
    
    Args:
        name (str): 日志记录器名称
        
    Returns:
        logging.Logger: 指定名称的日志记录器
    """
    return logging.getLogger(name)